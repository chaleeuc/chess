import random

piece_weight = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}    # material scoring
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)] 

''' returns global variable next_move i.e., make the first recursive call'''
def negamax_helper(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    negamax(gs, valid_moves, DEPTH, 1 if gs.whites_turn else -1)
    return next_move

''' minmax using negamax / alpha beta pruning
    alpha: maximum possible 
    beta:  minimum possible
    at any time alpha > beta, break
'''
def negamax(gs, valid_moves, depth, turn):
    global next_move
    if depth == 0:  # deepest depth, we will return and evaluate
        return turn * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_a_move(move)
        next_moves = gs.get_valid_moves()
        score = -negamax(gs, next_moves, depth-1, -turn)  # this line is crucial in negamax
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        gs.undo_a_move()    

    return max_score

''' take the gamestate of the engine 
    ## ideas to check board positions
    1) how many valid moves each piece can make (more options)
    2) how many threats are each pieces making
        2.1) forks
        2.2) double attacks
        2.3) pinning 
    3) how many pieces are being protected
    4) 

    NOTES: positive score is good for white, negative is good for black
'''
def score_board(gs):
    if gs.checkmate:            # check gamestate for checkmate
        if gs.whites_turn:
            return -CHECKMATE   # black wins
        else:
            return CHECKMATE    # white wins
    elif gs.stalemate:          # check gamestate for stalemate
        return STALEMATE
    else:
        score = 0
        for row in gs.board:
            for square in row:
                if square[0] == 'w':
                    score += piece_weight[square[1]]
                elif square[0] == 'b': 
                    score -= piece_weight[square[1]]

    return score

'''
score board purely based on material
'''
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_weight[square[1]]
            elif square[0] == 'b': 
                score -= piece_weight[square[1]]

    return score
