"""
Handling user input and displaying the current GameState Object.
"""

import pygame as p
import ChessEngine, AiMoveScript

BOARD_WIDTH = BOARD_HEIGHT = 512 #400 is another option
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 #dimension of a chess board is 8x8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 15 #for animatioins later on
IMAGES = {}

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
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH,BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag
    animate = False
    loadImages() #only do for once, before the while loop
    running = True
    sqSelected = () #no square selected #track tuple : (row,col)
    playerClicks = [] #track 2 tuple : [(r,c),(r,c)]
    gameOver = False
    playerOne = True #if a human playing white, False if ai playing white
    playerTwo = True #if a human playing black, True if ai playing black
    while running :
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handle
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >= 8: #click same square
                        sqSelected = () #deselect
                        playerClicks = [] #clear
                    else :
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 : #after 2nd click
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]: #base in engine __init__ in Move
                                gs.makeMove(validMoves[i]) #generate from engine
                                moveMade = True
                                animate = True
                                sqSelected = () #reset
                                playerClicks = [] #reset
                        if not moveMade :
                            playerClicks = [sqSelected]
            #key handle
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r: #reset when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = () #reset
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    
        #AI move
        if not gameOver and not humanTurn:
            AIMove = AiMoveScript.findBestMoveMinMax(gs, validMoves)
            if AIMove is None:
                AIMove = AiMoveScript.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
                    
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        
        if gs.checkmate or gs.stalemate:
            gameOver = True
            drawEndGameText(screen, 'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate')
        
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all the graphics within a currect game state.
'''
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) #draw square on the board
    #add in piece highlightng or move suggestions (later)
    highLightSquares(screen, gs, validMoves, sqSelected)
    drawPiece(screen, gs.board) #draw piece on the top of those squares
    drawMoveLog(screen, gs, moveLogFont)
    
'''
Draw square on board (the top left square always light)
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"),p.Color("dark gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            # p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE))
            rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen,color,rect)
    
'''
Highlight
'''
def highLightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #transparency value 0-255
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))      
            
'''
Draw the piece on the board
'''
def drawPiece(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0 , MOVE_LOG_PANEL_WIDTH, MOVE_LOG_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog): # make sure black made a move
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)
        
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('White'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list animation that move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 10 #fram to move per square
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount + 1):
        r, c =((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPiece(screen, board)
        #highlight square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)
    
def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 48, True, False)
    textObject = font.render(text, 0, p.Color('White'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))
    
if __name__ == "__main__" :
    main()