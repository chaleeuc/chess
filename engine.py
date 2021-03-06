'''
Responsible for storing all game state
Responsible for move validation
Stack for move logs
'''
from turtle import color


class GameState():
    def __init__(self):
        # perhaps consider numpy, for efficiency
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],            
            ['--', '--', '--', '--', '--', '--', '--', '--'],            
            ['--', '--', '--', '--', '--', '--', '--', '--'],            
            ['--', '--', '--', '--', '--', '--', '--', '--'],            
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

        self.move_functions = { 'P': self.get_pawn_moves, 
                                'R': self.get_rook_moves,
                                'N': self.get_knight_moves,
                                'B': self.get_bishop_moves,
                                'Q': self.get_queen_moves,
                                'K': self.get_king_moves,
        } 

        self.whites_turn = True
        self.move_log = []

        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4) 
        self.in_check = False
        self.pins = []
        self.checks = []

        self.enpassant_possible = ()  # coordinations of the square where en passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]

        self.castling_rights = CastlingRights(True, True, True, True)
        self.castling_rights_log = [CastlingRights(self.castling_rights.white_king_side, self.castling_rights.white_queen_side, 
                                                   self.castling_rights.black_king_side, self.castling_rights.black_queen_side)]

        self.checkmate = False
        self.stalemate = False

    ''' make_a_move 
    does not work for pawn promotion, castling, en passant
    '''
    def make_a_move(self, move):
        self.board[move.end_row][move.end_col] = move.piece_moved   # if valid, piece moves to new board[row][col]
        self.board[move.start_row][move.start_col] = '--'           # if valid, piece at board[row][col] becomes '--'
        self.move_log.append(move)              # logging for backtracks
        self.whites_turn = not self.whites_turn   # switch side

        # update king's position
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)  

        # when pawn moves twice, next move maybe en passant
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.end_col)
        else:
            self.enpassant_possible = ()

        # if en passant, update board accordingly
        if move.enpassant:
            self.board[move.start_row][move.end_col] = '--' # capturing the pawn in the same row

        # check for pawn promotion
        if move.pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q' # make it a queen for now

        # Castling
        if move.castle:
            if move.end_col - move.start_col == 2:  # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1] 
                self.board[move.end_row][move.end_col + 1] = '--'                              
            else:   # queen side castling
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2] 
                self.board[move.end_row][move.end_col - 2] = '--'                              

        # update enpassant log
        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castling rights
        self.update_castling_rights(move)
        self.castling_rights_log.append(CastlingRights(self.castling_rights.white_king_side, self.castling_rights.white_queen_side, 
                                                   self.castling_rights.black_king_side, self.castling_rights.black_queen_side))

    '''
    undo moves
    '''
    def undo_a_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whites_turn = not self.whites_turn

            # update king's position
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # undo enpassant
            if move.enpassant:
                self.board[move.end_row][move.end_col] = '--'   # leave where pawn ends up blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            # reset enpassant rights
            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # reset castling rights
            self.castling_rights_log.pop()
            self.castling_rights = self.castling_rights_log[-1]

            # undo castle
            if move.castle:
                if move.end_col - move.start_col == 2:  # kingside castle
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1] 
                    self.board[move.end_row][move.end_col - 1] = '--'                              
                else:   # queen side castling
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1] 
                    self.board[move.end_row][move.end_col + 1] = '--'                              


            self.checkmate = False
            self.stalemate = False

    def update_castling_rights(self, move):
        if move.piece_moved == 'wK':
            self.castling_rights.white_king_side = False
            self.castling_rights.white_queen_side = False

        elif move.piece_moved == 'bK':
            self.castling_rights.black_king_side = False
            self.castling_rights.black_queen_side = False
        
        elif move.piece_moved == 'wR':
            if move.start_col == 0: # left rook
                self.castling_rights.white_queen_side = False
            elif move.start_col == 7: # right rook
                self.castling_rights.white_king_side = False

        elif move.piece_moved == 'bR':
            if move.start_col == 0: # left rook
                self.castling_rights.black_queen_side = False
            elif move.start_col == 7: # right rook
                self.castling_rights.black_king_side = False

        # if look is captured, update
        if move.piece_captured == 'wR':
            if move.end_row == 7: 
                if move.end_col == 0: # left rook
                    self.castling_rights.white_king_side = False
                elif move.end_col == 7: # right rook 
                    self.castling_rights.white_queen_side = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0: 
                    self.castling_rights.black_king_side = False
                elif move.end_col == 7: 
                    self.castling_rights.black_queen_side = False

    '''
    Check for validity of player move
    '''
    def get_valid_moves(self):
        # castling right check
#        for log in self.castling_rights_log:
#            print(log.white_king_side, log.white_queen_side, log.black_king_side, log.black_queen_side, end=', ')
#        print()
        temp_castle_rights = CastlingRights(self.castling_rights.white_king_side, self.castling_rights.white_queen_side, 
                                            self.castling_rights.black_king_side, self.castling_rights.black_queen_side)        
        moves = []
        self.in_check, self.pins, self.checks = self.check_pins_and_checks()
        if self.whites_turn:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                # to block,
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_check = self.board[check_row][check_col]
                valid_sqaures = []  # squares which pieces other than king can move to block the check

                if piece_check[1] == 'N':  # if the opposing check is given by knight, you must capture it
                    valid_sqaures = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_sqaures.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_col) in valid_sqaures:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)

        else:
            moves = self.get_all_possible_moves()
            if self.whites_turn:
                self.get_castling_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castling_moves(self.black_king_location[0], self.black_king_location[1], moves)

        # check for checkmate/stalemates
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.castling_rights = temp_castle_rights

        return moves

    '''maybe use greedy algorithm'''
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]    # either b or w for black or white OR --
                if (turn == 'w' and self.whites_turn) or (turn == 'b' and not self.whites_turn):
                    piece = self.board[row][col][1]
                    # generate proper moves for the piece.
                    self.move_functions[piece](row, col, moves) # calls for appropriate move function based on piece type
        return moves

    def check_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False

        if self.whites_turn:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]

        # check outwards from king's perspective
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        if  (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or (i == 1 and type == 'P' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break

        # check knight_moves
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))            
        for m in knight_moves:
            end_row = start_row +m[0]
            end_col = start_col +m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks  

    '''
    get all possible pawn moves for the pawn located at row and col, add to moves list
        if pawns in starting row, can move 1 or 2
        cant move backwards
        black and white behave differently
        captures in diagonal move              
        # PROMOTION  
    '''
    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pawn_promotion = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        # grab black and white with one code
        if self.whites_turn:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = 'b'
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = 'w' 
            king_row, king_col = self.black_king_location

        if self.board[row + move_amount][col] == '--':    # 1 square move
            if not piece_pinned or pin_direction == (move_amount, 0):
                if row + move_amount == back_row: #check promotion
                    pawn_promotion = True
                moves.append(Move((row, col), (row+move_amount, col), self.board, pawn_promotion=pawn_promotion))
                if row == start_row and self.board[row+2*move_amount][col] == '--':
                    moves.append(Move((row, col), (row+2*move_amount, col), self.board))

        if col - 1 >= 0: # emulate capture to left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col-1][0] == enemy_color:
                    if row + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col - 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:   # check if king is left of the pawn
                            inside_range = range(king_col + 1, col - 1) # go upto enemy pawn's column
                            outside_range = range(col + 1, 8)
                        else:
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != '--':  # something is blocking
                                blocking_piece = True
                        for i in outside_range:
                            sq = self.board[row][i]
                            if sq[0] == 'enemy_color' and (sq[1] =='R' or sq[1] == 'Q'):
                                attacking_piece = True
                            elif sq != '--':
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, enpassant = True))

        if col + 1 <= 7: # emulate capture to right
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[row + move_amount][col+1][0] == enemy_color:
                    if row + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col + 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:   # check if king is left of the pawn
                            inside_range = range(king_col + 1, col) # go upto enemy pawn's column
                            outside_range = range(col + 2, 8)
                        else:
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != '--':  # something is blocking
                                blocking_piece = True
                        for i in outside_range:
                            sq = self.board[row][i]
                            if sq[0] == 'enemy_color' and (sq[1] =='R' or sq[1] == 'Q'):
                                attacking_piece = True
                            elif sq != '--':
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, enpassant = True))

    '''
    get all possible pawn moves for the pawn located at row and col, add to moves list
    '''
    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': 
                    self.pins.remove(self.pins[i])
                break

        dir = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemy = 'b' if self.whites_turn else 'w'

        for d in dir:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:   # range check
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    get all possible pawn moves for the pawn located at row and col, add to moves list
    '''    
    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally = 'w' if self.whites_turn else 'b'

        for m in knight_moves:
            end_row = row + m[0]
            end_col = col + m[1] 
            if 0 <= end_row < 8 and 0 <= end_col < 8:   # range check
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    '''
    get all possible pawn moves for the pawn located at row and col, add to moves list
    '''
    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': 
                    self.pins.remove(self.pins[i])
                break

        dir = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # upleft, upright, downleft, downright
        enemy = 'b' if self.whites_turn else 'w'

        for d in dir:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:   # range check
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    get all possible pawn moves for the pawn located at row and col, add to moves list
    '''
    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row ,col, moves)

    '''
    get all possible pawn moves for the pawn located at row and col, add to moves list
    '''
    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.whites_turn else 'b'

        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]

                if end_piece[0] != ally_color:
                    # place king on end square, and check for checks
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)

                    in_check, pins, checks = self.check_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

                    if ally_color == 'w':
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    def square_under_attack(self, row, col):
        self.whites_turn = not self.whites_turn
        moves = self.get_all_possible_moves()   # get all opponents moves
        self.whites_turn = not self.whites_turn
        for move in moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_castling_moves(self, row, col, moves):
        if self.square_under_attack(row, col):
            return

        if (self.whites_turn and self.castling_rights.white_king_side) or (not self.whites_turn and self.castling_rights.black_king_side):
            self.king_side_castle(row, col, moves)

        if (self.whites_turn and self.castling_rights.white_queen_side) or (not self.whites_turn and self.castling_rights.black_queen_side):
            self.queen_side_castle(row, col, moves)

    def king_side_castle(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, castle = True))
        
    def queen_side_castle(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, castle = True))


class CastlingRights():
    def __init__(self, white_king_side, white_queen_side, black_king_side, black_queen_side):
        self.white_king_side = white_king_side
        self.white_queen_side = white_queen_side
        self.black_king_side = black_king_side
        self.black_queen_side = black_queen_side

class Move():
    # for each k, v in ranks to row, make a keypair {v1: k1, ..., vn:kn}
    ranks_to_rows = { '1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0 } 
    rows_to_ranks = { v: k for k, v in ranks_to_rows.items() } 
    files_to_cols = { 'a': 7, 'b': 6, 'c': 5, 'd': 4, 'e': 3, 'f': 2, 'g': 1, 'h': 0 }
    cols_to_files = { v: k for k, v in files_to_cols.items() }

    def __init__(self, start, end, board, pawn_promotion = False, enpassant=False, castle = False):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]    # what is being moved 
        self.piece_captured = board[self.end_row][self.end_col]     # what is being captured            
        self.enpassant = enpassant                                  # is the move enpassant
        self.pawn_promotion = pawn_promotion                        # is the move pawn promotion
        self.castle = castle
        if self.enpassant:
            self.piece_captured = 'bP' if self.piece_moved == 'wP' else 'wP'

        self.is_capture = self.piece_captured != '--' 
        # unique id generation from 0 - 7000
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        # old pawn promotion
        # self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7)

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]


    ''' OVERRIDE for equals '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    ''' OVERRIDE str 
        mock chess notation
    '''
    def __str__(self):
        if self.castle: # castle
            return 'O-O' if self.end_col == 6 else 'O-O-O'
        
        end_sq = self.get_rank_file(self.end_row, self.end_col)
        if self.piece_moved[1] == 'P':
            if self.is_capture:
                return self.cols_to_files[self.start_row] + 'x' + end_sq
            else:
                return end_sq
        
        # piece moves
        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += 'x'
        return move_string + end_sq

        # pawn promotion
        # two or more different pieces moving to same square, i.e., Nbd2, if both knights can move to d2
        # adding + for a check move, # for a checkmate