#!/usr/bin/env python

'''
Minimax demo for tic-tac-toe with alpha-beta pruning
LPL, 13-Jan-2018
'''

import sys
import copy
import random

class gameBoard:
    board = None
    prev_move = None

    def __init__(self,board=None):
        if board is not None:
            self.board = copy.copy(board.board)
            self.last_move = copy.copy(board.prev_move)

    def print_board(self):
        for i, j in enumerate(self.board):
            if i % 3 == 0 and i != 0:
                sys.stdout.write("\n")
            sys.stdout.write(" "+j)
        sys.stdout.write("\n")
        sys.stdout.flush()

class gameRules:
    empty = None
    player = None
    player_inv = None
    win_score = None
    winconf = None

    def __init__(self):
        self.empty = '.'
        self.player = {0:'x', 1:'o'}
        self.player_inv = {v:k for k,v in self.player.items()}
        self.win_score = {0:1000000, 1:-1000000}
        self.win_score_inv = {v:k for k,v in self.win_score.items()}
        self.winconf = ( \
            (0,1,2), \
            (3,4,5), \
            (6,7,8), \
            (0,3,6), \
            (1,4,7), \
            (2,5,8), \
            (0,4,8),
            (2,4,6) \
        )

    def possible_moves(self,board):
        return [i for i,k in enumerate(board.board) if k == self.empty]

    def check_move(self,board,pos):
        try:
            return board.board[pos] == self.empty
        except:
            return False

    def move(self,board,pos,player):
        board.board[pos] = self.player[player]
        board.last_move = (pos,player)

    def undo_move(self,board,move=None):
        if move is not None:
            board.board[move] = self.empty
        else:
            if board.last_move is None:
                print "No moves to undo"
            else:
                board.board[board.last_move[0]] = self.empty

    def generate_board(self):
        board = gameBoard()
        board.board = [self.empty for _ in xrange(9)]
        board.prev_move = None

        return board

    def instruction_board(self):
        board = gameBoard()
        board.board = [str(k) for k in xrange(9)]
        board.prev_move = None

        return board

    def win(self,board):
        for iwin in self.winconf:
            ref = board.board[iwin[0]]
            if ref != self.empty:
                for iiwin in iwin[1:]:
                    if (board.board[iiwin] != ref):
                        ref = self.empty
                        break
                if ref != self.empty:
                    break
        if ref == self.empty:
            if len(self.possible_moves(board)) == 0:
                return 0
            else:
                return None
        else:
            return self.win_score[self.player_inv[ref]]

    def get_other_player(self,player):
        assert player == 0 or player == 1, "Error: Invalid player"
        if player == 0:
            return 1
        else:
            return 0

    def is_maximizing_player(self,player):
        assert player == 0 or player == 1, "Error: Invalid player"
        return player == 0

    def is_mimimizing_player(self,player):
        assert player == 0 or player == 1, "Error: Invalid player"
        return player == 1

    def min_score(self):
        return self.win_score[1]

    def max_score(self):
        return self.win_score[0]

    def announce_win(self,win_state):
        if win_state is None:
            return "N/A"
        else:
            if win_state in self.win_score_inv:
                win_player = self.win_score_inv[win_state]
                return ("Player %d wins" % win_player)
            else:
                return "Draw"

    def winning_player(self,win_state):
        if win_state in self.win_score_inv:
            return self.win_score_inv[win_state]
        else:
            return None

def alphabeta(game_rules,game_board,player,alpha,beta,depth,depth_max=None):
    # Check win condition
    win_cond = game_rules.win(game_board)
    # Check wining state - if not, this isn't yet a leaf node
    is_maximizing_player = game_rules.is_maximizing_player(player)
    if (win_cond is not None):
        # Adjust win/lose decisions - speedy win, dragged-out loss
        if is_maximizing_player:
            if win_cond > 0:
                win_cond -= depth
            else:
                win_cond += depth
        else:
            if win_cond < 0:
                win_cond += depth
            else:
                win_cond -= depth
        return win_cond
    else:
        next_player = game_rules.get_other_player(player)
        # Iterate over all possible moves
        if ((depth_max is not None) and (depth == depth_max)):
            return depth_max

        for imove in game_rules.possible_moves(game_board):
            # Try current move
            game_rules.move(game_board,imove,player)
            # Compute score for this move
            score = alphabeta(game_rules,game_board,next_player, \
                alpha,beta,depth=depth+1,depth_max=depth_max)

            '''
            # Play max number of moves
            if is_maximizing_player:
                score += 1
            else:
                score -= 1
            '''

            # Reset current board
            game_rules.undo_move(game_board,imove)

            # alpha-beta pruning
            if is_maximizing_player:
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    return beta
            else:
                if score < beta:
                    beta = score
                if beta <= alpha:
                    return alpha

        if is_maximizing_player:
            return alpha
        else:
            return beta

def minimax(game_rules,game_board,player):
    # Check win condition
    win_cond = game_rules.win(game_board)
    # Check wining state - if not, this isn't yet a leaf node
    if (win_cond is not None):
        return win_cond
    else:
        # Iterate over all possible moves
        is_maximizing_player = game_rules.is_maximizing_player(player)
        next_player = game_rules.get_other_player(player)
        best_score = None
        for imove in game_rules.possible_moves(game_board):
            # Try current move
            game_rules.move(game_board,imove,player)
            # Compute score for this move
            score = minimax(game_rules,game_board,next_player)
            # Reset current board
            game_rules.undo_move(game_board,imove)

            # minimax
            if best_score is None:
                best_score = score
            if is_maximizing_player:
                best_score = max(score,best_score)
            else:
                best_score = min(score,best_score)

        return best_score

def play(game_rules,game_board,player):
    best_moves = []
    prev_score = None
    best_score = None

    possible_moves = game_rules.possible_moves(game_board)
    for imove in possible_moves:
        game_rules.move(game_board,imove,player)
        score = alphabeta( \
            game_rules, \
            game_board, \
            game_rules.get_other_player(player), \
            game_rules.min_score(), \
            game_rules.max_score(), \
            depth=0, \
            depth_max=None)
        '''
        score = minimax( \
            game_rules, \
            game_board, \
            game_rules.get_other_player(player), \
            )
        '''
        game_rules.undo_move(game_board,imove)

        #print "MOVE: %d, SCORE: %7d" % (imove, score)

        if best_score is None:
            best_score = score
        prev_score = best_score

        if game_rules.is_maximizing_player(player):
            best_score = max(best_score,score)
        else:
            best_score = min(best_score,score)

        # If new best score found, clear list
        if best_score != prev_score:
            best_moves[:] = []
            best_moves.append(imove)
        elif score == best_score:
            best_moves.append(imove)

    # Select from list of possible best scores
    random.shuffle(best_moves)
    return best_moves[-1]

if __name__ == '__main__':
    # Initialize game_rules object
    game_rules = gameRules()
    # Generate empty game_board
    game_board = game_rules.generate_board()

    '''
    # Rigged board
    game_rules.move(game_board,6,0)
    game_rules.move(game_board,7,0)
    game_rules.move(game_board,1,1)
    game_rules.move(game_board,5,1)
    game_rules.move(game_board,8,1)
    '''
    print "Tile coordinates:"
    game_rules.instruction_board().print_board()
    print ""
    print "Initial board:"
    game_board.print_board()
    print ""
    print "Player 0: AI    (" + game_rules.player[0]+ ")"
    print "Player 1: Human (" + game_rules.player[1]+ ")"
    print ""
    while (True):
        starting_player = raw_input("Select starting player (0 or 1):")
        try:
            starting_player = int(starting_player)
            assert starting_player == 0 or starting_player == 1
            break
        except:
            print "Invalid input"
            continue

    input_player = 1
    current_player = starting_player
    win_state = game_rules.win(game_board)
    while (win_state is None):
        if current_player == input_player:
            while (True):
                input_move = raw_input("Move: ")
                try:
                    input_move = int(input_move)
                    proceed = game_rules.check_move(game_board,input_move)
                except:
                    proceed = False

                if proceed:
                    break
                else:
                    print "Invalid move. Please select a valid move."
            #input_move = play(game_rules,game_board,current_player)
            game_rules.move(game_board,input_move,current_player)
        else:
            ai_move = play(game_rules,game_board,current_player)
            game_rules.move(game_board,ai_move,current_player)

        print "Player " + str(current_player) + " move:"
        game_board.print_board()
        win_state = game_rules.win(game_board)
        print "Win state: ", game_rules.announce_win(win_state)
        print ""

        current_player = game_rules.get_other_player(current_player)
