import sys
import pygame as p
import ChessEngine, AiMoveScript, MiniMax

# Constants
BOARD_WIDTH = BOARD_HEIGHT = 512
# MOVE_LOG_PANEL_WIDTH = 250
# MOVE_LOG_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 30
IMAGES = {}

# customize colors
green1 = (235, 237, 209)
green2 = (100, 164, 96)


def loadImages():
    """Load images for chess pieces."""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    """Main driver for the game, handling user input and updating the display."""
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH , BOARD_HEIGHT))  # + MOVE_LOG_PANEL_WIDTH
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = False  # Human playing white
    playerTwo = True  # Human playing black
    

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col, row = location[0] // SQ_SIZE, location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    if not gs.checkmate and not gs.stalemate:
                        gs.undoMove() 
                        moveMade = True
                        animate = False
                        gameOver = False 
                        if playerOne or playerTwo:
                            gs.undoMove()
                    else:
                        print("Cannot undo after checkmate or stalemate!")
            
                if e.key == p.K_r:  # Reset when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False 
                    print(f"Restart the game")
                if e.key == p.K_t:  # Press 't' to Resign
                    gameOver = True
                    winner = "Black" if gs.whiteToMove else "White"
                    print(f"{winner} wins by resignation!")
                
                if e.key == p.K_q:  # Press 'q' to Quit
                    running = False
                    print(f"Quit game")
                    p.quit()
                    sys.exit()
                    
        # AI Move
        if not gameOver and not humanTurn:
            fen = gs.getFen()
            we = 800
            be = 2800
            # aiEloRating = 100
            # Dynamically set AI Elo rating based on game state
            # if gs.turnCount < 20:
            #     aiEloRating = 1200  # Easy for first 20 moves
            # elif gs.turnCount < 40:
            #     aiEloRating = 1600  # Medium difficulty after 20 moves
            # else:
            #     aiEloRating = 2000  # Hard for endgame
            aiMove = AiMoveScript.adjustableBotElo(fen, time_limit=1.0, white_elo=we, black_elo=be)
            # aiMove = MiniMax.MiNimaxfindBestMove(fen, time_limit=1.0, skill_level=7)
            if aiMove:
                move = ChessEngine.Move.fromUci(aiMove, gs.board)

                # Correctly set isCastleMove if necessary
                if abs(move.startCol - move.endCol) == 2 and move.pieceMoved[1].upper() == 'K': # Check if the move is a king move of two squares (castling), case-insensitive
                    move.isCastleMove = True
                    if move.pieceMoved[0] == 'w': #white castle
                        if move.endCol > move.startCol: # Kingside castling (right)
                            move.rookStartCol = 7
                            move.rookEndCol = 5
                        else: # Queenside castling (left)
                            move.rookStartCol = 0
                            move.rookEndCol = 3
                    else: #black castle
                        if move.endCol > move.startCol: # Kingside castling (right)
                            move.rookStartCol = 7
                            move.rookEndCol = 5
                        else: # Queenside castling (left)
                            move.rookStartCol = 0
                            move.rookEndCol = 3
                gs.makeMove(move)
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


def drawGameState(screen, gs, validMoves, sqSelected, _):  # moveLogFont
    drawBoard(screen)
    highLightSquares(screen, gs, validMoves, sqSelected)
    drawPiece(screen, gs.board)
    # drawMoveLog(screen, gs, moveLogFont)
    highlightLastMove(screen, gs)
    

def highlightLastMove(screen, gs):
    moveLog = gs.moveLog
    if moveLog:
        lastMove = moveLog[-1]
        highlightColor = (255, 255, 100, 128)

        highlightSurface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        highlightSurface.fill(highlightColor)

        startSquare = p.Rect(lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        screen.blit(highlightSurface, startSquare)

        endSquare = p.Rect(lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        screen.blit(highlightSurface, endSquare)
    drawPiece(screen, gs.board)

        
def drawBoard(screen):
    colors = [p.Color(green1), p.Color(green2)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, color, rect)


def highLightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)

            s.fill(p.Color(255, 255, 100, 128))
            
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    validMoveSurface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                    
                    if move.isCapture:
                        p.draw.circle(validMoveSurface, (100, 100, 100, 200), (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 2.5, 5)
                    else:
                        p.draw.circle(validMoveSurface, (100, 100, 100, 200), (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 6)
                    
                    screen.blit(validMoveSurface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

    if gs.checkmate or gs.stalemate:
        return


def drawPiece(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# def drawMoveLog(screen, gs, font):
#     moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_HEIGHT)
#     p.draw.rect(screen, p.Color('black'), moveLogRect)
    
#     moveLog = gs.moveLog
#     moveTexts = []

#     for i in range(0, len(moveLog), 2):
#         moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
#         if i + 1 < len(moveLog):
#             moveString += str(moveLog[i + 1]) + "  "
#         moveTexts.append(moveString)
#     movesPerRow = 3
#     padding = 5
#     lineSpacing = 2
#     textY = padding
#     for i in range(0, len(moveTexts), movesPerRow):
#         text = ""
#         for j in range(movesPerRow):
#             if i + j < len(moveTexts):
#                 text += moveTexts[i + j]
#         textObject = font.render(text, True, p.Color('White'))
#         textLocation = moveLogRect.move(padding, textY)
#         screen.blit(textObject, textLocation)
#         textY += textObject.get_height() + lineSpacing


def animateMove(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    baseFramePerSquare = 20
    maxFrames = 40
    framePerSquare = min(baseFramePerSquare, maxFrames // (abs(dR) + abs(dC) + 1))
    
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR * frame / frameCount), (move.startCol + dC * frame / frameCount))
        
        drawBoard(screen)
        drawPiece(screen, board)
        
        # color = colors[(move.endRow + move.endCol) % 2]
        # startSquare = p.Rect(move.startCol * SQ_SIZE, move.startRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        # p.draw.rect(screen, color, startSquare)
        # p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        drawBoard(screen)
        drawPiece(screen, board)
        p.display.flip()
        clock.tick(120)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 48, True, False)
    textObject = font.render(text, 0, p.Color('White'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
