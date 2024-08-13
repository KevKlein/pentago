# Author: Kevin Klein
# GitHub username: kevmklein
# Date: 2024.8.13
# Project: OSU cs162 portfolio project
# Description: Includes Pentago class.
#   * Maintains a representation of the board, number of pieces placed,
#       game state, and current player, and has some access methods including
#       get_game_state and is_board_full.
#   * Handles making a move with make_move, with helper functions to
#       place a piece, rotate a quadrant, check for 5-in-a-row, and do some
#       input validity checking.
#   * Can print_board for a visual representation of the board.


# constant definitions
WHITE_MARBLE = '●'
BLACK_MARBLE = '○'
EMPTY = '-'

CLOCKWISE = 'C'
ANTI_CLOCKWISE = 'A'

UP = -1
DOWN = 1
LEFT = -1
RIGHT = 1
MID = 0

SUB_BOARD_CENTERS = {1: (1, 1), 2: (1, 4), 3: (4, 1), 4: (4, 4)}
SUB_BOARD_INNER_CORNERS = {1: (2, 2), 2: (2, 3), 3: (3, 2), 4: (3, 3)}


class Pentago:
    """Pentago is a two-player abstract strategy game played on a 6×6 board,
    which is divided into four 3×3 sub-boards (or quadrants). Players take turns
    placing a marble of their color (either black or white) onto an unoccupied
    space on the board and then rotating one of the sub-boards by 90 degrees,
    either clockwise or anti-clockwise. The rotation step is mandatory, and the
    player can choose to rotate any of the four sub-boards, not necessarily the
    one where they placed the marble.

    A player wins by getting five of their marbles in a vertical, horizontal,
    or diagonal row, either before or after the sub-board rotation. If a
    player achieves five-in-a-row before the rotation step, the game ends
    immediately, and the player doesn't need to rotate a sub-board. If both
    players achieve five-in-a-row after the rotation, the game is a draw. If
    only the opponent gets a five-in-a-row after the rotation, the opponent
    wins. If all 36 spaces on the entire board are occupied without forming a
    row of five after the rotation, the game ends in a draw.

    * Handles all the logic for the game. Initializes and keeps track of the
    board and the game state, including if a player has won, how many pieces
    have been placed, and whose turn it is.
    * Handles making a player's move, including updating the board
    to reflect the placed piece and sub_board rotation, and re-evaluating the
    game state. Also handles some input validation.
    * Can display a visual representation of the board.
    * Has various helper methods to accomplish the above.
    """

    def __init__(self):
        self._board = [[EMPTY] * 6 for _ in range(6)]  # 2-D list, [y][x]
        self._pieces_placed = 0
        self._game_state = 'UNFINISHED'
        self._current_player = 'black'

    def get_game_state(self):
        """Returns the state of the game, which is evaluated after each move.
        Can be 'UNFINISHED', 'WHITE_WON', 'BLACK_WON', or 'DRAW'.
        """
        return self._game_state

    def is_board_full(self):
        """Return whether all 36 positions on the board are occupied."""
        return self._pieces_placed == 36

    def set_piece(self, position, color):
        """Sets the piece at the given position to the given color.
        Color may be 'white', 'black', or '-' (empty).
        """
        if type(position) is str:
            position = self.coords(position)
        y, x = position
        self._board[y][x] = color

    def make_move(self, color, position, sub_board, rotation):
        """Takes as parameters the color of marble a player wishes to place,
        the position they want to put it in (in alphanumeric form, e.g.'b3'),
        the sub_board they want to rotate (1-4), and the direction they want to
        rotate it ('C' for clockwise or 'A' for anit-clockwise).
        * Checks to see if move is valid, returning a status message if not.
        * If valid, places the marble, updates the game state, rotates the
        sub_board if there's still no winner, and updates the game state
        again.
        * Returns True if the move was carried out.
        """
        # check if input is valid
        status = self.is_valid_move(color, position, sub_board, rotation)
        if status != 'valid':
            return status

        # place piece
        self.set_piece(position, color)
        self._pieces_placed += 1
        self._current_player = ('black' if self._pieces_placed % 2 == 0
                                else 'white')

        # Re-evaluate game state by checking for win at position
        #   Get the lines passing through the given position
        y, x = self.coords(position)
        lines_to_check = ([self.get_row_line(y), self.get_col_line(x)] +
                          self.get_diag_lines((y, x)))
        #   Check lines for 5 in a row, update game state if current player won
        for result in [self.contains_5_in_a_row(line) for line in
                       lines_to_check]:
            if result == 'black':
                self._game_state = 'BLACK_WON'
                return True
            if result == 'white':
                self._game_state = 'WHITE_WON'
                return True

        #  Rotate the given sub_board
        self.rotate(sub_board, rotation)

        # Re-evaluate game state by checking for a win through rotated board
        #   Find which lines we need to check for 5-in-a-row
        #   including all the rows and cols of the sub_board
        lines_to_check = []
        y, x = SUB_BOARD_CENTERS.get(sub_board)
        lines_to_check += [self.get_row_line(row) for row in [y - 1, y, y + 1]]
        lines_to_check += [self.get_col_line(col) for col in [x - 1, x, x + 1]]
        #   plus the diagonals passing through the quadrant's inner corner
        #   plus the diagonals on either side of those diagonals
        y, x = SUB_BOARD_INNER_CORNERS.get(sub_board)
        diag_line_pairs = [self.get_diag_lines(pos) for pos in [(y, x - 1),
                                                                (y, x),
                                                                (y, x + 1)]]
        for diag_line in diag_line_pairs:
            lines_to_check += diag_line
        #   Check the lines for 5-in-a-row
        black_wins = False
        white_wins = False
        for result in [self.contains_5_in_a_row(line) for line in
                       lines_to_check]:
            if result == 'black':
                black_wins = True
            if result == 'white':
                white_wins = True
        #   Did black, white, both (or neither) get 5-in-a-row?
        if black_wins and white_wins:
            self._game_state = 'DRAW'
        elif black_wins:
            self._game_state = 'BLACK_WON'
        elif white_wins:
            self._game_state = 'WHITE_WON'

        elif self.is_board_full():
            self._game_state = 'DRAW'

        return True

    def is_valid_move(self, color, position, sub_board, rotation):
        """Helper for make_move. Checks if move is valid with respect to
        whether the game is already finished, turn order, and which positions
        are already taken, whether the position is within the bounds of
        the board, whether the sub_board is actually a quadrant of the
        board, and whether the rotation direction is clockwise or
        anti-clockwise. All other aspects of the input are assumed to be valid.
        Returns an error message if invalid, else returns 'valid'.
        """
        x, y = self.coords(position)

        if self._game_state != 'UNFINISHED':
            return "game is finished"
        if color != self._current_player:
            return "not this player's turn"
        if not (0 <= x <= 5 and 0 <= y <= 5):
            return "position out of bounds"
        if self.piece_at(position) != EMPTY:
            return "position is not empty"
        if not (1 <= sub_board <= 4):
            return "sub_board out of bounds"
        if not (rotation == 'C' or rotation == 'A'):
            return "rotation direction invalid"
        else:
            return 'valid'

    def piece_at(self, position):
        """Takes a position, either in alphanumeric form (b3) or in
        coordinate form (1, 3). Returns the piece at the given position
        (black, white, or empty)."""
        if type(position) is not tuple:
            position = self.coords(position)
        y, x = position
        return self._board[y][x]

    def coords(self, alpha_num_position):
        """Converts a given board position like `b3` to a tuple like (1, 3).
        Returns the coordinates as a tuple (y, x).
        Letters are zero-indexed (a = 0).
        """
        y = "abcdef".index(alpha_num_position[0])
        x = int(alpha_num_position[1])
        return y, x

    def rotate(self, sub_board, direction):
        """Takes as parameters a sub_board (1, 2, 3, or 4) and a rotation
        direction ('C' for clockwise or 'A' for anti-clockwise). Moves the
        pieces of the given sub_board 90 degrees around the center of the
        sub_board in the given direction.
        """
        # get list of positions to be rotated, in order going in a circle
        y, x = SUB_BOARD_CENTERS.get(sub_board)
        relative_positions = [(UP, LEFT), (UP, MID), (UP, RIGHT),
                              (MID, RIGHT), (DOWN, RIGHT), (DOWN, MID),
                              (DOWN, LEFT), (MID, LEFT)]
        sub_board_positions = [(y + dy, x + dx) for dy, dx in
                               relative_positions]

        if direction == ANTI_CLOCKWISE:
            sub_board_positions.reverse()

        # get list of piece colors currently at those positions and move
        # them on the board two spaces in the given direction
        current_colors = [self.piece_at(pos) for pos in sub_board_positions]
        for i, pos in enumerate(sub_board_positions):
            new_color = current_colors[(i - 2) % len(current_colors)]
            self.set_piece(pos, new_color)

    def get_row_line(self, row):
        """Takes a row number and returns the positions along that row."""
        return [(row, col) for col in range(6)]

    def get_col_line(self, col):
        """Takes a column number and returns the positions along that column."""
        return [(row, col) for row in range(6)]

    def get_diag_lines(self, position):
        """Takes a tuple representing a position (y, x).
        Returns a list of two lists: the diagonal line positions that go
        through the given position rightward, then leftward.
        """
        y, x = position
        if not (0 <= x <= 5 and 0 <= y <= 5):
            return []

        # rightward (e.g. (0,0) to (5,5))
        dist_from_starting_edge = min(y, x)
        y -= dist_from_starting_edge
        x -= dist_from_starting_edge
        rightward = []
        while y <= 5 and x <= 5:
            rightward.append((y, x))
            y += 1
            x += 1

        # leftward (e.g. (0,5) to (5,0))
        y, x = position
        dist_from_starting_edge = min(y, 5 - x)
        y -= dist_from_starting_edge
        x += dist_from_starting_edge
        leftward = []
        while y <= 5 and x >= 0:
            leftward.append((y, x))
            y += 1
            x -= 1

        return [rightward, leftward]

    def contains_5_in_a_row(self, position_list):
        """Takes list of positions as a parameter. Checks to see if the given 
        row contains five-in-a-row of either color. Positions are
        assumed to actually be in a straight line. Returns the color
        that got 5-in-a-row ('black' or 'white') or False if neither got one.
        """
        if len(position_list) < 5:
            return False

        previous_color = self.piece_at(position_list[0])
        consecutive_count = 1
        for position in position_list[1:]:
            color = self.piece_at(position)
            if color == previous_color and color != EMPTY:
                consecutive_count += 1
            else:
                previous_color = color
                consecutive_count = 1
            if consecutive_count == 5:
                return color
        return False

    def print_board(self):
        """Display the board on standard output. Adds row and column headers,
        as well as lines between quadrants.
        """
        # replace 'white' and 'black' with appropriate symbols
        board_to_print = []
        for row in self._board:
            row = [self.to_print_symbol(marble) for marble in row]
            board_to_print.append(row)

        # add col headers
        header_nums = [str(i) for i in range(6)]
        board_to_print = [header_nums] + board_to_print

        # print rows, with vertical and horizontal sub_board dividing lines
        for index, row in enumerate(board_to_print):
            row.insert(3, ' | ')
            line = " abcdef"[index] + '  ' + '  '.join(row)
            print(line)
            if index == 3:
                print('   ————————  |  ————————')

        # print legend
        print(" ", WHITE_MARBLE, " = white   ", BLACK_MARBLE, " = black  ",
              EMPTY, " = empty")

    def to_print_symbol(self, marble_color):
        """Helper for print_board. Returns a symbol representation of
        a marble for display purpose.
        """
        if marble_color == 'white':
            return WHITE_MARBLE
        if marble_color == 'black':
            return BLACK_MARBLE
        else:
            return EMPTY


def main():
    """Place for quick testing"""


if __name__ == "__main__":
    main()
