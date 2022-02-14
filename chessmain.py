''' 
Driver file
responsible for handling user input and displaying game state
'''
import pygame as p
import engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
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
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = engine.GameState()

    valid_moves = gs.get_valid_moves()
    move_made = False   # flag for when a move is made, i.e., valid move generation is expensive
                        # so only turn this whenever a valid move is made, we create a new valid moves list

    load_images()
    running = True
    sq_selected = () # (row, col) for user click
    player_clicks = [] # two tuples (row, col), (row, col)

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse Event Handler
            elif(e.type == p.MOUSEBUTTONDOWN):
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                if sq_selected == (row, col):   # user clicked on same square twice
                    sq_selected = ()            # deselect
                    player_clicks = []

                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)

                if len(player_clicks) == 2:                    
                    # make the move
                    move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())

                    # move validation
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_a_move(valid_moves[i])
                            move_made = True
                            sq_selected = ()    # deselect
                            player_clicks = []  
                    if not move_made:
                        player_clicks = [sq_selected]

            # key handler
            elif(e.type == p.KEYDOWN):
                # undo move, if z is press
                if e.key == p.K_z:
                    gs.undo_a_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_gamestate(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
draws squares and pieces
'''
def draw_gamestate(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)

'''
draw the squares on the draw_board
note: top left is always light
'''
def draw_board(screen):
    colors = [p.Color('white'), p.Color('grey')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
draw pieces using current gamestate.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



if __name__ == '__main__':
    main()