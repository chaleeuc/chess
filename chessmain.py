''' 
Driver file
responsible for handling user input and displaying game state
'''
import pygame as p
import engine
import ai

# WINDOW SIZE
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT

DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
load images one time
initialize Images dictionary
'''
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('img/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))

''' 
main 

'''
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = engine.GameState()

    valid_moves = gs.get_valid_moves()
    move_made = False   # flag for when a move is made, i.e., valid move generation is expensive
                        # so only turn this whenever a valid move is made, we create a new valid moves list

    animate = False     # flag variable for animating a move

    load_images()
    running = True
    sq_selected = ()    # (row, col) for user click
    player_clicks = []  # two tuples (row, col), (row, col)

    gameover = False    

    # AI TESTING PURPOSE
    player_one = True   # True if human is playing, else False
    player_two = True   # True if human is playing, else False

    # movelog font 
    move_log_font = p.font.SysFont('Arial', 12, False, False)
    while running:
        human_turn = (gs.whites_turn and player_one) or (not gs.whites_turn and player_two)       

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse Event Handler
            elif(e.type == p.MOUSEBUTTONDOWN):
                # if not gameover:                   
                if not gameover and human_turn:     # for AI testing Purpose
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE 
                    row = location[1] // SQ_SIZE 
                    # print(col)                    

                    # user clicked on same square twice
                    # OR user clicked on move log panel
                    if sq_selected == (row, col) or col >= 8:   
                        sq_selected = ()            # deselect
                        player_clicks = []

                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:                    
                        # make the move
                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        # check chess notation
                        print(move.get_chess_notation())

                        # move validation
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_a_move(valid_moves[i])
                                move_made = True
                                animate = True

                                sq_selected = ()    # deselect
                                player_clicks = []  
                        if not move_made:
                            player_clicks = [sq_selected]
                        
            # key handler
            elif(e.type == p.KEYDOWN):
                # undo move, when z is pressed
                if e.key == p.K_z:
                    gs.undo_a_move()
                    move_made = True
                    animate = False
                    gameover = False

                # reset board, when r is pressed
                if e.key == p.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()    # deselect
                    player_clicks = []  
                    move_made = False
                    animate = False
                    gameover = False

        # AI move Generation
        if not gameover and not human_turn:
            ai_move = ai.negamax_helper(gs, valid_moves)
            if ai_move == None:
                ai_move = ai.find_random_move(valid_moves)      # Implement this Asynchronously
            gs.make_a_move(ai_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_gamestate(screen, gs, valid_moves, sq_selected, move_log_font) 

        if gs.checkmate or gs.stalemate:
            gameover = True
            draw_text(screen, 'draw' if gs.stalemate else 'black wins by checkmate' if gs.whites_turn else 'white wins by checkmate')

        clock.tick(MAX_FPS)
        p.display.flip()

'''
draws squares and pieces
'''
def draw_gamestate(screen, gs, valid_moves, sq_selected, font):
    draw_board(screen)
    draw_highlight(screen, gs, valid_moves, sq_selected)
    highlight_last_move(screen, gs)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, font)

'''
draw the squares on the draw_board
note: top left is always light
'''
def draw_board(screen):
    global colors   
    colors = [p.Color('white'), p.Color('grey')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

''' 
Highlight square selected, and show possible moves
'''
def draw_highlight(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():   # square needs not be empty
        row, col = sq_selected
        if gs.board[row][col][0] == ('w' if gs.whites_turn else 'b'):   # check if piece can be moved
            # highlighting selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency: 0 = transparent, 255 = opaque
            s.fill(p.Color(40, 255, 40))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))

            s.fill(p.Color(80, 80, 255))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))

'''
Highlights last move made
'''
def highlight_last_move(screen, gs):
    # get the game log
    if len(gs.move_log) != 0:
        move = gs.move_log[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color(40, 255, 40))
        screen.blit(s, (move.start_col*SQ_SIZE, move.start_row*SQ_SIZE))
        screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))

'''
draw pieces using current gamestate.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

''' draws movelog '''
def draw_move_log(screen, gs, font):
    # side panel, start panel at where chess board ends
    movelog_panel = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color(0, 0, 0), movelog_panel)

    # string manipulation for proper move log notation
    move_log = gs.move_log
    move_text = []
    for i in range(0, len(move_log), 2):
        turn_string = str(i//2 + 1) + '.' + str(move_log[i]) + ' '
        # check if black piece has been moved
        if i + 1 < len(move_log):
            turn_string += str(move_log[i + 1])
        move_text.append(turn_string)


    padding = 5
    text_y = padding
    line_spacing = 2
    moves_per_row = 4

    for i in range(0, len(move_text), moves_per_row):
        text = ''
        for j in range(moves_per_row):
            if i + j < len(move_text):
                text += move_text[i+j] + '  '
 
        text_obj = font.render(text, True, p.Color(255, 255, 255))
        text_loc = movelog_panel.move(padding, text_y)
        text_y += text_obj.get_height() + line_spacing
        screen.blit(text_obj, text_loc)


''' 
Chess Piece Move Animation
'''
def animate_move(move, screen, board, clock):
    global colors
    drow = move.end_row - move.start_row
    dcol = move.end_col - move.start_col

    frames_per_square = 5  # frame to move one square
    frame_count = (abs(drow) + abs(dcol)) * frames_per_square
    for frame in range(frame_count + 1):    
        row, col = (move.start_row + drow*frame/frame_count, move.start_col + dcol*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)    
        # erase the piece moved from it's ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.enpassant:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col*SQ_SIZE, enpassant_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(IMAGES[move.piece_captured], end_square)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont('Sans', 32, True, False)
    text_obj = font.render(text, 0, p.Color('Gray'))
    text_loc = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - text_obj.get_width()/2, BOARD_HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj, text_loc)
    text_obj = font.render(text, 0, p.Color('Black'))
    screen.blit(text_obj, text_loc.move(2, 2))

if __name__ == '__main__':
    main()