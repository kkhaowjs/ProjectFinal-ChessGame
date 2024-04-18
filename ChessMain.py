"""
Handling user input and displaying the current GameState Object.
"""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 #400 is another option
DIMENSION = 8 #dimension of a chess board is 8x8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15 #for animatioins later on
IMAGES ={}

'''
Initialize a global directory of images.
'''

def loadImages():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces :
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))
    #NOTE: can access an image by saying 'IMAGES['wp']'
    
'''
The main driver for code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag
    loadImages() #only do for once, before the while loop
    running = True
    sqSelected = () #no square selected #track tuple : (row,col)
    playerClicks = [] #track 2 tuple : [(r,c),(r,c)]
    while running :
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handle
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) location of mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row,col): #click same square
                    sqSelected = () #deselect
                    playerClicks = [] #clear
                else :
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2 : #after 2nd click
                    move = ChessEngine.Move(playerClicks[0],playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = () #reset
                        playerClicks = [] #reset
                    else :
                        playerClicks = [sqSelected]
            #key handle
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
                    
        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()
    
'''
Responsible for all the graphics within a currect game state.
'''
def drawGameState(screen,gs):
    drawBoard(screen) #draw square on the board
    #add in piece highlightng or move suggestions (later)
    drawPiece(screen, gs.board) #draw piece on the top of those squares

'''
Draw square on board (the top left square always light)
'''
def drawBoard(screen):
    colors = [p.Color("white"),p.Color("dark gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            # p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE))
            rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen,color,rect)
            
            
'''
Draw the piece on the board
'''
def drawPiece(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

if __name__ == "__main__" :
    main()