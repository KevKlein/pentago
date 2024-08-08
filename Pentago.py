# Author: Kevin Klein
# GitHub username: kevmklein
# Date: 2024.8.8
# Project: OSU cs162 portfolio project
# Description: Includes Pentago class.
#   * Maintains a representation of the board, number of pieces placed, and
#       game state, and has some access methods including get_game_state,
#       is_board_full, and whose_turn.
#   * Handles making a move with make_move, with various helper functions to
#       place a piece, rotate a quadrant, evaluate the game state, and do some
#       input validity checking.
#   * Can print_board for a visual representation of the board.

"""
DETAILED TEXT DESCRIPTIONS OF HOW TO HANDLE THE SCENARIOS
(sorry if this includes some redundancies, but some questions kind of overlap.)

1. Initializing the Pentago class
    Initialize _board to a list of 6 lists of 6 empty spaces, a 6x6 2-D list.
    initialize _pieces_placed to 0. Initialize _game_state to 'UNFINISHED'.

2. Keeping track of turn order
    If the number of pieces that have been placed is even, then it's black's
    turn, otherwise white. Keep track of the number of pieces placed
    in _pieces_placed and update after a valid move.

3. Keeping track of the current board position
    (I interpret this to mean keeping track of the board re: the pieces on it.)
    _board keeps track of the whole board. It is a 6x6 2-D list containing
    all the pieces of the board. The board is updated during make_move by
    calling set_piece with the color and position arguments to make_move,
    and if there is no winner it is updated again by calling rotate with
    the sub_board and rotation arguments.

4. Determining if a regular move is valid
    We need to check four things:
    * whether the game is finished: call get_game_state and see if it is
    'UNFINISHED'.
    * whether it is the correct player's turn: compare the given color
    argument to a call to whose_turn, which is based on the number of pieces
    placed.
    * whether the position is already occupied: call piece_at(pos) to see
    if it is empty or not. piece_at looks up a position in _board.
    * whether the position is outside the bounds of the board: compare the
    given position argument's x and y components to 0 and 5. The x and y
    coordinate representation of a position is gotten via a call to coords.

5. Rotating the sub-board
    Add the eight relative positions from the center of a sub_board
    (e.g. (-1,-1), (-1, 0), etc, (one spot away from (0, 0) in each direction))
    to the coordinates of the center of the given sub_board
    (e.g. (4, 1) for sub_board #3) to calculate the coordinates of each
    position to be rotated. Reverse the list of coordinates if direction
    argument is anti-clockwise. Iterate through the positions in a circle,
    setting each position's color in _board to the color of the previous
    position.

6. Updating the board to reflect the valid move
    (this seems almost the same as question 3...)
    The board is updated during make_move (if the move is valid) by calling
    set_piece with the color and position arguments to make_move. After
    checking for a winner, if there is none then the positions of the given
    sub_board are updated by calling rotate with the give sub_board and
    rotation arguments. rotate updates the eight pieces of the sub_board
    that need to be updated.

7. Determining whether there is any 5-in-row on the board for one color of the
piece
    (I interpret this question to mean "Determining whether there is any
    5-in-a-row on the board 'for either color after placing a piece'".)

    * after placing a piece, get the lines (lists of positions) going through
    the given position via get_row_line, get_col_line, and get_diag_lines.
    Call contains_5_in_a_row on each of the the lists, which iterates
    through the positions getting their pieces and checking for
    five consecutive pieces of either color.
    * after rotating, do the same thing on all the row and column lines
    of the rotated sub_board, as well as the diagonals going through the inner
    corner and the diagonals adjacent to those, 6 diagonals are passed to
    contains_5_in_a_row, though only 4 might return a winner.

8. Determining whether the current board is full
    Compare the value of _pieces_placed to 36.

9. Determining the current state of the game
    Call contains_5_in_a_row on the appropriate lines, as above, and iterate
    through the results. If red and black both have 5-in-a-row at the same
    time, it's a draw. If only one color has 5-in-a-row, they win. If there
    is no color with 5-in-a-row, check for a draw by calling is_board_full.
    If not, then the game is unfinished.

10. How to present the board using the print method
    * Make a copy of the board, iterating through each piece and replacing the
    string representations of the pieces with pretty symbol representations.
    * Add a header row with column numbers.
    * Iterate through the rows, adding row letters at the start of each row and
    quadrant dividing lines after the third piece, as well as a line after the
    third row, then printing the embellished rows.
    * Print a legend row.
"""

# constant definitions
WHITE_MARBLE = '○'
BLACK_MARBLE = '●'
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
    sub_board_centers = {1: (1, 1), 2: (1, 4), 3: (4, 1), 4: (4, 4)}

    def __init__(self):
        self._board = [[EMPTY] * 6 for _ in range(6)]  # [y][x]
        self._pieces_placed = 0
        self._game_state = 'UNFINISHED'

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
        the position they want to put it in, the sub_board they want to
        rotate, and the direction they want to rotate it.
        * Checks to see if move is valid, returning a status message if not.
        * If valid, places the marble, evaluates the game state, rotates the
        sub_board if there's still no winner, and evaluates the game state
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

        # Get the relevant lines passing through the given position
        y, x = self.coords(position)
        lines_to_check = [self.get_row_line(y), self.get_col_line(x)]
        lines_to_check += [self.get_diag_lines(position)]
        # Check for 5 in a row, update game state if current player won
        for winner in [self.contains_5_in_a_row(line) for line in
                       lines_to_check]:
            if winner:  # no need to check for draw, only current player can win
                self._game_state = winner
                return True  # don't rotate if the game is finished

        #  Rotate the given sub_board
        self.rotate(sub_board, rotation)

        # Find which lines we need to check for 5-in-a-row
        #   including all the rows and cols of the sub_board
        lines_to_check = []
        y, x = SUB_BOARD_CENTERS.get(sub_board)
        lines_to_check += [self.get_row_line(row) for row in [y - 1, y, y + 1]]
        lines_to_check += [self.get_col_line(col) for col in [x - 1, x, x + 1]]
        #   including the diagonals passing through the inner corner
        #   and the diagonals on either side of those
        y, x = SUB_BOARD_INNER_CORNERS.get(sub_board)
        lines_to_check += [self.get_diag_lines(pos) for pos in [(y, x - 1),
                                                                (y, x),
                                                                (y, x + 1)]]
        # Check the lines for 5-in-a-row
        black_wins = False
        white_wins = False
        for winner in [self.contains_5_in_a_row(line) for line in
                       lines_to_check]:
            if winner == 'black':
                black_wins = True
            if winner == 'white':
                white_wins = True

        #  Re-evaluate game-state
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
        are already taken, and whether the position is within the bounds of
        the board. All other aspects of the input are assumed to be
        valid. Returns an error message if invalid, else returns 'valid'.
        """
        if self._game_state != 'UNFINISHED':
            return "game is finished"
        if self.whose_turn != color:
            return "not this player's turn"
        if self.piece_at(position) != EMPTY:
            return "position is not empty"
        x, y = self.coords(position)
        if not (0 <= x <= 5 and 0 <= y <= 5):
            return "position out of bounds"
        else:
            return 'valid'

    def whose_turn(self):
        """Returns whose turn it is. Black goes first."""
        if self._pieces_placed % 2 == 0:
            return 'black'
        else:
            return 'white'

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
        direction (clockwise or anti-clockwise). Moves the pieces of the
        given sub-board in the given direction.
        """
        relative_positions = [(UP, LEFT), (UP, MID), (UP, RIGHT),
                              (MID, RIGHT), (DOWN, RIGHT), (DOWN, MID),
                              (DOWN, LEFT), (MID, LEFT), (UP, LEFT)]

        if direction == ANTI_CLOCKWISE:
            relative_positions.reverse()

        # move all the pieces of the sub_board to the next position going
        # around the sub_board center
        y, x = SUB_BOARD_CENTERS.get(sub_board)
        prev_color = None
        for dy, dx in relative_positions:
            pos = (y + dy, x + dx)
            if prev_color is None:
                prev_color = self.piece_at(pos)
            else:
                current_color = self.piece_at(pos)
                self.set_piece(pos, prev_color)
                prev_color = current_color

    def get_row_line(self, row):
        """Takes a row number and returns the positions along that row."""
        return [(row, col) for col in range(6)]

    def get_col_line(self, col):
        """Takes a column number and returns the positions along that column."""
        return [(row, col) for row in range(6)]

    def get_diag_lines(self, position):
        """Takes a tuple representing a position (y x).
        Returns a list of the diagonal line positions that go through the given 
        position, rightward then leftward.
        """
        y, x = self.coords(position)

        # rightward (e.g. (0,0) to (5,5))
        dist_from_edge = min(y, x)
        y -= dist_from_edge
        x -= dist_from_edge
        rightward = []
        while y <= 5 and x <= 5:
            rightward.append((y, x))
            y += 1
            x += 1

        # leftward (e.g. (0,5) to (5,0))
        dist_from_edge = min(y, 5 - x)
        y -= dist_from_edge
        x += dist_from_edge
        leftward = []
        while y <= 5 and x >= 0:
            leftward.append((y, x))
            y += 1
            x -= 1

        return [rightward, leftward]

    def contains_5_in_a_row(self, position_list):
        """Takes list of positions as a parameter. Checks to see if the given 
        row contains five-in-a-row of either color. Returns the color that got
        5-in-a-row ('black' or 'white') or False if neither got one.
        """
        if len(position_list) < 5:
            return False

        consecutive_count = 1
        previous_color = self.piece_at(position_list[0])
        for position in position_list:
            color = self.piece_at(position)
            if color == previous_color and color != EMPTY:
                consecutive_count += 1
            else:
                consecutive_count = 1
                previous_color = color
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
        print(" ○ = white   ● = black  - = empty")

    def to_print_symbol(self, marble_color):
        """Helper for print_board. Returns a unicode symbol representation of
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
    p = Pentago()
    p.set_piece('a0', 'white')
    p.set_piece('a2', 'black')
    p.set_piece('b0', 'black')
    p.set_piece('b1', 'black')
    p.set_piece('a3', 'white')
    p.set_piece('c2', 'white')

    p.print_board()
    p.rotate(1, CLOCKWISE)
    p.print_board()


if __name__ == "__main__":
    main()
