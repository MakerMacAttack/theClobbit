# Specification for the Clobber board
from __future__ import print_function

from Move import *
from random import *
from Piece import *
from collections import defaultdict
import time
import math


class Board:
    def __init__(self, rows, columns):

        # Fields for MaxStrand
        self.my_pieces = []
        self.your_pieces = []

        # Fields for MCTS
        self.total_simulation_reward = 0
        self.total_number_visits = 1
        self.parent_board = None
        self.children = []
        self.visited = False

        self.current_player = 1
        self.rows = rows
        self.v = None
        self.columns = columns
        self.moveset = []
        self.opp_moveset = []
        self.move_group = defaultdict(list)
        self.move_type_list = defaultdict(list)
        self.opp_move_group = defaultdict(list)
        self.opp_move_type_list = defaultdict(list)
        self.history = []
        self.flex_value = 0  # should these three default to None? The numbers shown are correct.
        self.my_moving_pieces = 15
        self.your_moving_pieces = 15
        current_color = 0
        self.latest_move = Move(None, None, None, None, None)
        self.matrix = [[0 for j in range(columns)] for i in range(rows)]
        for i in range(rows):
            for j in range(columns):
                if i % 2 == 0:
                    if j % 2 == 0:
                        self.matrix[i][j] = 1
                    else:
                        self.matrix[i][j] = 0
                else:
                    if j % 2 == 0:
                        self.matrix[i][j] = 0
                    else:
                        self.matrix[i][j] = 1

    def display(self):
        for i in range(self.rows):
            print()
            for j in range(self.columns):
                print(self.matrix[i][j], end="")
        print()

    def get_moves_black(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.matrix[i][j] == 1:
                    # adds down move if legal
                    if i < self.rows - 1 and self.matrix[i + 1][j] == 0:
                        self.moveset.append(Move(i, j, i + 1, j))
                    # adds up move if legal
                    if i > 0 and self.matrix[i - 1][j] == 0:
                        self.moveset.append(Move(i, j, i - 1, j))
                    # adds left move if legal
                    if j > 0 and self.matrix[i][j - 1] == 0:
                        self.moveset.append(Move(i, j, i, j - 1))
                    # adds right move if legal
                    if j < self.columns - 1 and self.matrix[i][j + 1] == 0:
                        self.moveset.append(Move(i, j, i, j + 1))
                        # print(self.moveset)

    def get_moves_white(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.matrix[i][j] == 0:
                    # adds down move if legal
                    if i < self.rows - 1 and self.matrix[i + 1][j] == 1:
                        self.moveset.append(Move(i, j, i + 1, j))
                    # adds up move if legal
                    if i > 0 and self.matrix[i - 1][j] == 1:
                        self.moveset.append(Move(i, j, i - 1, j))
                    # adds left move if legal
                    if j > 0 and self.matrix[i][j - 1] == 1:
                        self.moveset.append(Move(i, j, i, j - 1))
                    # adds right move if legal
                    if j < self.columns - 1 and self.matrix[i][j + 1] == 1:
                        self.moveset.append(Move(i, j, i, j + 1))
                        # print(self.moveset)

    def get_moves(self):
        # Clears the current moveset for previous player
        self.moveset = []
        if self.current_player == 1:
            self.get_moves_black()

        elif self.current_player == 0:
            self.get_moves_white()

    def get_opp_moves(self):
        self.moveset = []
        if self.current_player == 1:
            self.get_moves_white()
        else:
            self.get_moves_black()

    # Loop over moveset to look at each piece to determine how many moves each piece can make, so we can "type"
    # each piece based on whether it can make 4, 3, 2, 1, or 0 moves. Stores list of pieces by "type" in move_type_list
    def group_moves(self):
        self.move_group = defaultdict(list)
        for m in self.moveset:
            key = str(m.player_row) + ", " + str(m.player_col)
            self.move_group[key].append(m)
        self.move_type_list = defaultdict(list)
        for key, value in self.move_group.items():
            num_moves = len(value)
            self.move_type_list[num_moves] += value

    # Separate function to repeat group_moves and get the values for the opponent.
    def opp_group_moves(self):
        self.opp_move_group = defaultdict(list)
        for m in self.opp_moveset:
            key = str(m.player_row) + ", " + str(m.player_col)
            self.opp_move_group[key].append(m)
        self.opp_move_type_list = defaultdict(list)
        for key, value in self.opp_move_group.items():
            num_moves = len(value)
            self.move_type_list[num_moves] += value

    # Picks and executes a random move for a player
    @staticmethod
    def random_walk(board):
        board.get_moves()
        return board.moveset[randint(0, len(board.moveset) - 1)]

    # Function to execute strategy one: pick a piece of own color based on # of available moves, (0 thorugh 4),
    # 4 is best, 0 is worst.
    @staticmethod
    def pick_max_moves(board):
        board.get_moves()
        board.group_moves()
        for i in range(4, 0, -1):  # loops over piece "types", starting with 4-types, until a move can be selected
            if len(board.move_type_list[i]):
                # print("Piece type: " + str(i)) #prints type
                result = choice(board.move_type_list[i])  # picks a move available for that player's available "types"
                # result.display_move()
                return result
        return None

    # Function that selects a move that maximizes the curent player's moveable pieces, and minimizes this
    # value for their opponent
    @staticmethod
    def min_opp_moves(board):
        elapsed_time = 0.0
        start_time = time.time()
        max_ratio = -9999
        max_ratio_move = []
        board.get_moves()
        for m in board.moveset:
            b = board.make_move(m)
            b.get_moves()
            b.group_moves()
            opp_moves = len(
                b.move_group.keys())  # number of moveable pieces for 'opponent' (player who is currently NOT taking turn)
            if b.current_player == 0:
                b.current_player = 1
            elif b.current_player == 1:
                b.current_player = 0
            b.get_moves()
            b.group_moves()
            my_moves = len(b.move_group.keys())  # number of moveable pieces of player currently taking turn
            if opp_moves == 0:
                current_ratio = my_moves
            else:
                current_ratio = my_moves / float(opp_moves)
            if current_ratio == max_ratio:
                max_ratio_move.append(m)
            elif current_ratio > max_ratio:
                max_ratio = current_ratio
                max_ratio_move = []
                max_ratio_move.append(m)

            elapsed_time = time.time() - start_time
            if elapsed_time >= .1:
                break

        return max_ratio_move[randint(0, len(max_ratio_move) - 1)]

    # This method makes a move on the current board, updates latest move, and sets moving player in move object
    def make_move(self, move):
        board = self.clone_board()
        move.moving_player = board.current_player
        move.parent = board.latest_move
        board.latest_move = move

        # Executes move for white and switches to opposing player (black).
        if board.current_player == 0:
            board.matrix[move.opponent_row][move.opponent_col] = 0
            board.current_player = 1

        # Executes move for black and then switches to opposing player (white).
        elif board.current_player == 1:
            board.matrix[move.opponent_row][move.opponent_col] = 1
            board.current_player = 0

        # Changes square that's just been vacated to an 'x'
        board.matrix[move.player_row][move.player_col] = 'x'
        board.get_moves()
        return board

    # Checks if the current board is in a winning state, and returns true or false.
    def win_check(self):
        self.get_moves()
        return len(self.moveset) == 0

    # Returns a list of moves that have the most pieces remaining.
    def get_max_move_pieces(self):
        piece_list = []
        current_max = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if self.current_player != self.matrix[i][j]:
                    pass
                # Determines the number of moves available for the piece on square (i,j)
                piece_move_numb = 0
                if i < self.rows - 1 and self.matrix[i + 1][j] == 0:
                    piece_move_numb = piece_move_numb + 1
                if i > 0 and self.matrix[i - 1][j] == 0:
                    piece_move_numb = piece_move_numb + 1
                if j > 0 and self.matrix[i][j - 1] == 0:
                    piece_move_numb = piece_move_numb + 1
                if j < self.columns - 1 and self.matrix[i][j + 1] == 0:
                    piece_move_numb = piece_move_numb + 1
                # Adds piece to current move list if it has the same number of moves available as current max
                if piece_move_numb == current_max:
                    piece_list.append(Piece(i, j))
                # If a piece with more moves than the current max is found, the current_max is updated and a new move list created
                if piece_move_numb > current_max:
                    current_max = piece_move_numb
                    piece_list = []
                    piece_list.append(Piece(i, j))

        return piece_list

    # This method returns one of the pieces with the most moves.
    @staticmethod
    def most_moves(board):
        move_list = board.get_max_move_pieces()
        return move_list(randint(0, len(move_list)))

    # This move returns the number of valid moves remaining for the current player.
    def get_numb_moves_remaining(self):
        self.get_moves()
        return len(self.moveset)

    # Clones board
    def clone_board(self):
        clone_board = Board(self.rows, self.columns)
        clone_board.current_player = self.current_player
        clone_board.moveset = []
        (clone_board.moveset).extend(self.moveset)
        (clone_board.moveset).extend(self.history)
        clone_board.latest_move = self.latest_move
        clone_board.matrix = [row[:] for row in self.matrix]

        return clone_board

    @staticmethod
    # Min_value method for alpha-beta search
    def min_value(self, alpha, beta):
        # global numb_visited
        # global numb_skipped
        # numb_visited = numb_visited + 1

        # self.get_moves()
        if self.get_numb_moves_remaining() == 0:
            if self.current_player == 1:
                self.latest_move.v = -1
                return -1
            elif self.current_player == 0:
                self.latest_move.v = 1
                return 1
        v = 2
        for move in self.moveset:
            v = min(v, Board.max_value(self.make_move(move), alpha, beta))
            self.latest_move.v = v
            if v <= alpha:
                # numb_skipped = numb_skipped + 1
                return v
            beta = min(beta, v)
        return v

    @staticmethod
    # Max_value method for alpha-beta search
    def max_value(self, alpha, beta):
        # global numb_visited
        # global numb_skipped
        # self.display()
        # numb_visited = numb_visited + 1

        # self.get_moves()
        if self.get_numb_moves_remaining() == 0:
            if self.current_player == 1:
                self.latest_move.v = -1
                return -1
            elif self.current_player == 0:
                self.latest_move.v = 1
                return 1
        v = -2
        for move in self.moveset:
            v = max(v, Board.min_value(self.make_move(move), alpha, beta))
            self.latest_move.v = v
            if v >= beta:
                # numb_skipped = numb_skipped + 1
                return v
            alpha = max(alpha, v)
        return v

    # Implementation of pg 172 AI textbook algorithm
    # For this algorithm for positions that give black a win have a value of 1 and positions that give
    # white a win have a value of -1
    # Currently assumes can reach end of board and not using a heuristic function

    # global numb_visited
    # global numb_skipped
    @staticmethod
    def alpha_beta_search(board):
        # global numb_visited
        # global numb_skipped
        numb_visited = 0
        numb_skipped = 0

        v = board.max_value(board, -2, 2)
        # print(numb_visited)
        # print(numb_skipped)
        for move in board.moveset:
            if move.v == v:
                return move
        return board.moveset[0]

    # MCTS strategy
    # Pseudocode from https://int8.io/monte-carlo-tree-search-beginners-guide/--template for general MCTS strategy
    # Updates the reward and visited stats that the MCTS makes use of
    @staticmethod
    def update_stats(node, result):
        node.total_simulation_reward = node.total_simulation_reward + result
        node.total_number_visits = node.total_number_visits + 1

    # Passes a result value up to the previous node on the propogation path
    @staticmethod
    def backpropogate(node, result):
        if node.parent_board == None:
            return
        Board.update_stats(node, result)
        Board.backpropogate(node.parent_board, result)

    # Returns the most promising child of a node based on the number of times it
    # appeared on a backpropogaton path
    @staticmethod
    def best_child(node):
        max_numb_visits = 0
        best_node = None
        for child in node.children:
            if best_node == None:
                best_node = child
                max_numb_visits = node.total_number_visits
            if child.total_number_visits > max_numb_visits:
                max_numb_visits = child.total_number_visits
                best_node = node
        return best_node

    # Returns score corresponding to which player won
    # Note a win for white is counted as -1 and a win for black is counted as 1
    @staticmethod
    def get_result(node):
        if node.current_player == 1:
            return -1
        return 1

    # Implements rollout policy for MCTS
    @staticmethod
    def rollout_policy(node):
        return Board.random_walk(node)

    # Returns result of a rollout for MCTS strategy
    @staticmethod
    def rollout(node):
        while not node.win_check():
            policy_move = Board.rollout_policy(node)
            node = node.make_move(policy_move)
        return Board.get_result(node)

    # Intitializes list of child nodes.
    # Note that this is not a static method
    def get_children(self):
        self.get_moves()
        for move in self.moveset:
            (self.children).append(self.make_move(move))

    # Checks to see if all of a node's children have been visited
    @staticmethod
    def is_fully_expanded(node):
        if len(node.children) == 0:
            return False
        for child in node.children:
            if not child.visited:
                return False
        return True

    # Retuns the child of a node that hasnt been visited yet in a MCTS exploration
    @staticmethod
    def pick_unvisited_child(node):
        if len(node.children) == 0:
            node.get_children()
        for child in node.children:
            if child.visited == False:
                return child

    # Computes upper confidence bound for the black pieces
    @staticmethod
    def best_uct_white(node):
        best_uct = float("inf")
        best_child = None
        # total_sim_visits = Board.get_total_sim_visits(node)
        for child in node.children:
            component_1 = float(child.total_simulation_reward) / float(
                child.total_number_visits)  # float div by zero error?
            component_2 = 1.41 * math.sqrt(
                math.log1p(Board.get_total_sim_visits(child)) / float(child.total_number_visits))
            current_uct = -(component_1 + component_2)
            if current_uct < best_uct:
                best_uct = current_uct
                best_child = child
        return best_child

    # Calculates total number of times a node has appeared on a backpropogation path
    @staticmethod
    def get_total_sim_visits(node):
        total_sim_visits = 0
        for child in node.children:
            total_sim_visits = total_sim_visits + child.total_number_visits
        return total_sim_visits

    # Computes upper confidence bound for the black pieces
    @staticmethod
    def best_uct_black(node):
        best_uct = float("-inf")
        best_child = None
        total_sim_visits = Board.get_total_sim_visits(node)
        for child in node.children:
            component_1 = float(child.total_simulation_reward) / float(
                child.total_number_visits)  # float div by zero error?
            component_2 = 1.41 * math.sqrt(
                math.log1p(Board.get_total_sim_visits(child)) / float(child.total_number_visits))
            current_uct = component_1 + component_2
            if current_uct > best_uct:
                best_uct = current_uct
                best_child = child
        return best_child

    # Computes upper condfidence bound for a node
    @staticmethod
    def best_uct(node):
        if node.current_player == 1:
            return Board.best_uct_black(node)
        return Board.best_uct_white(node)

    # Traverses tree until an unexplored node has been found
    @staticmethod
    def traverse(node):
        while Board.is_fully_expanded(node):
            node = Board.best_uct(node)
        if node.win_check():
            return node
        return Board.pick_unvisited_child(node)

    # Monte Carlo Tree search strategy
    @staticmethod
    def monte_carlo_tree_search(root):
        elapsed_time = 0.0
        start_time = time.time()
        while elapsed_time <= 0.1:
            leaf = Board.traverse(root)
            leaf.visited = True
            simulation_result = Board.rollout(leaf)
            Board.backpropogate(leaf, simulation_result)
            elapsed_time = time.time() - start_time
        return Board.best_child(root)

    """
    #This method takes the number of the current turn. It then calls the strategy for the black 
    #or white pieces based on the number of the turn. Because black plays first, all odd number turns
    #black moves. Because white plays second, all even number turns are white moves. 
    def get_move( self, turn, strategies):
        if strategy % 2 == 1 :
            return strategies.get_strategic_move(1)
        else:
            return strategies

    #Runs two strategies against each other and returns the win loss ration
    def run_simulation(strategies, simulation_numb):
        board = Board(5, 6)
        for i in range(1, simulation_numb + 1):
            while not board.win_check():
                move = board.get_move(strategies, i)
                board.make_move(move)
                  

    """

    # The following two functions are for the Max Flex strategy.

    def get_moving_pieces(self):
        self.my_moving_pieces = 0
        self.your_moving_pieces = 0
        self.get_moves()
        self.group_moves()

        for key, value in self.move_group.items():
            if len(value) > 0:
                self.my_moving_pieces += 1

        self.get_opp_moves()
        self.group_moves()
        for key, value in self.move_group.items():
            if len(value) > 0:
                self.your_moving_pieces += 1
        return self.my_moving_pieces, self.your_moving_pieces

    def get_flex_value(self):
        mine, yours = self.get_moving_pieces()
        flex = self.flex_value - mine - yours
        return flex

    @staticmethod
    def strat_maxflex(board):  # moveset is a list of move objects
        check_flex_value = -30  # starting point to begin ranking options
        check_move = []

        board.get_moves()
        for move in board.moveset:
            test = board.clone_board()
            t = test.get_flex_value()

            # Gets all equal moves
            if t == check_flex_value:
                check_move.append(move)
            # if better move is found, clears all previous ones and starts over
            elif t > check_flex_value:
                check_move = []
                check_move.append(move)
                check_flex_value = t
        return check_move[randint(0, len(check_move) - 1)]
    
    @staticmethod
    def theClobbit(board, num_moves):
        if num_moves < 6:
            return Board.min_opp_moves(board)
        elif num_moves < 11:
            return Board.strat_maxflex(board)
        else:
            return Board.alpha_beta_search(board)

    # # Following is for Max_Strand
    # # This function populates the lists of one's own pieces as well as the opponents, then sees which are stranded.
    # def get_pieces(self, board):
    #     # Note that this resets all previous pieces and inits them as un-stranded
    #     self.my_pieces = []
    #     self.your_pieces = []
    #     for i in range(self.rows):
    #         for j in range(self.columns):
    #             if (self.matrix[i][j] == self.current_player):
    #                 piece = Piece(i, j)
    #                 self.my_pieces.append(piece)
    #             if (self.current_player == 0):
    #                 if (self.matrix[i][j] == 1):
    #                     self.your_pieces.append(Piece(i, j))
    #             if (self.current_player == 1):
    #                 if (self.matrix[i][j] == 0):
    #                     self.your_pieces.append(Piece(i, j))
    #     self.check_stranded()
    #
    # # This function checks which pieces are stranded. Note this is the one I'm not quite done with.
    # def check_stranded(self, board):
    #     # This should only get called from get_pieces()
    #     unsorted = []
    #     visited = []
    #     frontier = []
    #     alone = True
    #     unsorted = self.my_pieces
    #     # Remove any currently stranded pieces
    #     for token in unsorted:
    #         if token.stranded:
    #             unsorted.remove(token)
    #     while (len(unsorted) > 0):  # If all pieces are stranded, the game should be over.
    #         frontier.append(unsorted.pop())
    #         alone = True
    #         while (frontier.len() > 0):
    #             test = frontier.pop()
    #
    #             # checking the space below the piece
    #             if (test.column + 1 <= self.columns):  # make sure it's on the board
    #                 # Do I need to write it for both sides?
    #                 if (self.matrix[test.row][test.column + 1] == 0):
    #                     # This is the bit where I'm running into a wall.
    #                     # if that piece is not already in frontier or visited
    #                     frontier.append(  # piece at that location)
    #                         unsorted.remove(
    #                     # piece at that location)
    #                     if (self.matrix[test.row][test.column + 1] == 1):
    #                         alone = False
    #                         # This will measure only black "blocks", not mixed.
    #
    #                         # checking right
    #                         if test.row + 1 <= self.rows
    #                     # repeat as above
    #
    #                     # checking above
    #                     if test.column > 0
    #                     # repeat as above
    #
    #                     # checking left
    #                     if test.row > 0
    #                     # repeat as above
    #
    #                     # if alone:
    #                     #     for
    #                     # piece in visited:
    #                     # self.stranded = True
    #                     # visited = []
    #
    #                     # Copy all of the above but this time check white for black
    #
    #                     # This is the core of the maxStrand strategy, picking any move that strands many opponent pieces.
    #
    # def strat_maxStrand(self, board):
    #     optimum = -31
    #     choice = []
    #     for move in self.moveset:
    #         #make_move()  # Is this a way to test each move or will this just keep making moves?
    #         if (self.stranded_value() == optimum):
    #             choice.append(move)
    #         if (self.stranded_value() > optimum):
    #             choice = []
    #             choice.append(move)
    #             optimum = self.stranded_value()
    #     action = self.max_flex(choice)
    #     # this should go through the max_strand options and return the one with the greatest flexibility
    #     return action
    #
    # # This function checks cloned boards to see how many opponent pieces will be stranded as compared to one's own
    # def stranded_value(self, board):
    #     self.get_pieces()
    #     white_stranded = 0
    #     black_stranded = 0
    #     for piece in self.my_pieces:
    #         if piece.stranded:
    #             black_stranded += 1
    #     for piece in self.your_pieces:
    #         if piece.stranded:
    #             white_stranded += 1
    #     return white_stranded - black_stranded
