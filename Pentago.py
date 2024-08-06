# Author: Kevin Klein
# GitHub username: kevmklein
# Date: 2024.8.5
# Project: OSU cs162 portfolio project
# Description: Includes
#   *


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


class Pentago:
    """ """

    def __init__(self):
        self._board = [[EMPTY]*6 for _ in range(6)]  # [y][x]
        self._pieces_placed = 0
        self._game_state = 'UNFINISHED'


    @staticmethod
    def to_print_symbol(marble_color):
        """Returns the symbol representation of a marble color."""
        if marble_color == 'white':
            return WHITE_MARBLE
        if marble_color == 'black':
            return BLACK_MARBLE
        else:
            return EMPTY

    def print_board(self):
        """Display the board on standard output. Adds row and column headers,
        as well as lines between quadrants.
        """
        # replace 'white' and 'black' with appropriate symbols
        board_to_print = []
        for row in self._board:
            row = [Pentago.to_print_symbol(marble) for marble in row]
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

    def get_game_state(self):
        """Returns the state of the game.
        (Can be 'UNFINISHED', 'WHITE_WON', 'BLACK_WON', or 'DRAW')
        """
        return self._game_state

    def is_board_full(self):
        """ """
        pass

    def make_move(self, color, position, sub_board, rotation):
        """Takes the color of marble a player wishes to place, the position
        they want to put it in, the sub_board they want to rotate and the
        direction they want to rotate it.
        Checks to see if move is valid, returning a status message if not.
        If valid, places the marble, rotates the sub_board and records the
        game state.
        """
        with self.is_valid_move(color, position, sub_board, rotation) as status:
            if status != 'valid':
                return status

        return True

    def is_valid_move(self, color, position, sub_board, rotation):
        """Checks if move is valid with respect whether the game is
        already finished, turn order, and which positions are already taken.
        All other aspects of the input are assumed to be valid.
        Returns error message if invalid, else returns 'valid'.
        """

        if self._game_state != 'UNFINISHED':
            return "game is finished"
        if self.whose_turn != color:
            return "not this player's turn"
        if self.piece_at(position) != EMPTY:
            return "position is not empty"
        else:
            return 'valid'


    def whose_turn(self):
        """Returns whose turn it is. Black goes first."""
        if self._pieces_placed % 2 == 0:
            return 'black'
        else:
            return 'white'

    def piece_at(self, position):
        """Return the piece at the given position (black, white, or empty)."""
        if type(position) is str:
            position = Pentago.coords(position)
        y, x = position
        return self._board[y][x]

    def rotate(self, sub_board, rotation):
        """Takes as parameters a sub_board (1, 2, 3, or 4) and a rotation
        direction (clockwise or anti-clockwise). Moves the pieces of the
        given sub-board in the given direction.
        """
        sub_board_centers = [(1, 1), (1, 4), (4, 1), (4, 4)]
        relative_positions = [(UP, LEFT), (UP, MID), (UP, RIGHT),
                              (MID, RIGHT), (DOWN, RIGHT), (DOWN, MID),
                              (DOWN, LEFT), (MID, LEFT), (UP, LEFT)]

        if rotation == ANTI_CLOCKWISE:
            relative_positions.reverse()

        # move all the pieces of the sub_board around the center
        y, x = sub_board_centers[sub_board - 1]
        prev = None
        for dy, dx in relative_positions:
            pos = (y + dy, x + dx)
            if prev is None:
                prev = self.piece_at(pos)
            else:
                current = self.piece_at(pos)
                self.set_piece(pos, prev)
                prev = current

    def set_piece(self, position, color):
        """Sets the piece at the given position to the given color.
        Color may be 'white', 'black', or '-' (empty).
        """
        if type(position) is str:
            position = Pentago.coords(position)
        y, x = position
        self._board[y][x] = color

    @staticmethod
    def coords(alpha_num_position):
        """Converts a given board position like `b3` to a tuple like (1, 3)
        with the y coordinate first, then x.
        Letters are zero-indexed (a = 0, b = 1, ...).
        """
        y = "abcdef".index(alpha_num_position[0])
        x = int(alpha_num_position[1])
        return y, x


def main():
    """Place for quick testing"""
    p = Pentago()
    p.set_piece('a0', 'white')
    p.set_piece('a2', 'black')
    p.set_piece('b0', 'black')
    p.set_piece('b1', 'black')
    p.set_piece('a3', 'white')
    p.set_piece('c2', 'white')

   #  p.print_board()
    p.rotate(1, CLOCKWISE)
    # p.print_board()


if __name__ == "__main__":
    main()
