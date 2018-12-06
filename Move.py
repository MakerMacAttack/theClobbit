# Class represents moves for our clobber board
class Move:

    def __init__(self, player_row=None, player_col=None, opponent_row=None, opponent_col=None, parent=None):
        # Moving player defaults to black because of assumption that black plays first
        self.moving_player = None
        self.player_row = player_row
        self.player_col = player_col
        self.opponent_row = opponent_row
        self.opponent_col = opponent_col
        # The move object contains a pointer to a parent move(previous move)
        # that way we can simply return the most recent move to get a list of the string of moves which allowed for a win.
        self.parent = parent
        #v-field is a counter that alpha-beta search makes use of
        self.v = None

    # Tests if two moves are equal
    @staticmethod
    def are_equal(move1, move2):
        if move1.player_row != move2.player_row:
            return False
        if move1.player_col != move2.player_col:
            return False
        if move1.opponent_row != move2.opponent_row:
            return False
        if move1.opponent_col != move2.opponent_col:
            return False
        return True

    # Displays the move
    def display_move(self):
        print("Move: (" + str(self.player_row) + "," + str(self.player_col) + ") -> (" + str(self.opponent_row) + "," + str(
            self.opponent_col) + ")")
