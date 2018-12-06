from __future__ import print_function
from Board import *
import csv


# Currently assumes black plays first; "Player 1": Black
# Static board size, usually default to 5x6

def main():
    rows = 6
    cols = 5
    game_iterations = 100  # number of games to be played
    stats = []
    w_wins = 0
    b_wins = 0
    for i in range(game_iterations):
        winner, num_moves = run_sim(rows, cols)
        stats.append([winner, num_moves])
        if winner == "White":
            w_wins += 1
        else:
            b_wins += 1
        # print("next game")
    with open('stats.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Black wins: {}% ".format((b_wins / float(game_iterations)) * 100)])
        writer.writerow(["White wins: {}% ".format((w_wins / float(game_iterations)) * 100)])
        writer.writerow([])
        for s in stats:
            writer.writerow(s)


#the Clobbit function
def run_sim(rows, cols):
    board = Board(rows, cols)
    move_counter = 0


    while not board.win_check():
        #board.display()
        if board.current_player == 1:
            #move = Board.theClobbit(board, move_counter)
            move = Board.min_opp_moves(board)
            #move = Board.strat_maxflex(board)
            #move = Board.alpha_beta_search(board)
            #move = Board.random_walk(board)
            #board = Board.monte_carlo_tree_search(board)
            board = board.make_move(move)
        else:
            move = Board.theClobbit(board, move_counter)
            #move = Board.min_opp_moves(board)
            #move = Board.strat_maxflex(board)
            #move = Board.alpha_beta_search(board)
            #move = Board.random_walk(board)
            #board = Board.monte_carlo_tree_search(board)
            board = board.make_move(move)
        move_counter = move_counter + 1
        # move.display_move()
    if board.current_player == 1:
        # print("White wins.")
        return "White", move_counter
    else:
        # print("Black wins.")
        return "Black", move_counter


if __name__ == "__main__":
    main()