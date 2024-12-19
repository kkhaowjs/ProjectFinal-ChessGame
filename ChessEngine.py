"""
Responsible for starting all the information about state of a chess game.
"""


class GameState():

    def __init__(self):
        # Board is an 8x8 2d list, each element of the list has 2 character.
        # The first character represents the color of a piece, 'b' or 'w'
        # The second character repersents the type of the piece, 'K', 'Q', 'R', 'B', 'N','P'.
        # "--" - represents an empty space with no piece.
        self.board = [
            # Initialize the board with pieces
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        # King Track
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        # pawn promo idea indicate the pawn go to the back rank when pawn reach row 0 to promo
        # did make it to the back rank ?
        self.pawnPromotion = False
        # self.pawnPromoRow = 0
        # en passant
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        
        self.currentCastlingRights = CastleRights(True, True, True, True)  # Initialize castling rights
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]
        
    def transformBoard(self):
        """Transform the board to FEN-compatible format."""
        transformedBoard = []
        for row in self.board:
            transformedRow = []
            for square in row:
                if square == '--':
                    transformedRow.append('--')
                else:
                    pieceType = square[1]
                    if square[0] == 'b':
                        transformedRow.append(pieceType.lower())
                    elif square[0] == 'w':
                        transformedRow.append(pieceType.upper())
            transformedBoard.append(transformedRow)
        return transformedBoard

    def getFen(self):
        """Return the FEN string representing the current board state."""
        fen = ''
        transformedBoard = self.transformBoard()
        for row in transformedBoard:
            emptyCount = 0
            for square in row:
                if square == '--':
                    emptyCount += 1
                else:
                    if emptyCount > 0:
                        fen += str(emptyCount)
                        emptyCount = 0
                    fen += square
            if emptyCount > 0:
                fen += str(emptyCount)
            fen += '/'
        fen = fen.strip('/')
        fen += ' ' + ('w' if self.whiteToMove else 'b')
        castlingRights = ''
        if self.currentCastlingRights.wks: castlingRights += 'K'
        if self.currentCastlingRights.wqs: castlingRights += 'Q'
        if self.currentCastlingRights.bks: castlingRights += 'k'
        if self.currentCastlingRights.bqs: castlingRights += 'q'
        if castlingRights == '': castlingRights = '-'
        fen += ' ' + castlingRights
        if self.enpassantPossible == ():
            fen += ' -'
        else:
            fen += ' ' + self.getChessNotation(self.enpassantPossible)
        fen += ' 0 1'
        return fen

    # Helper function to convert coordinates like (x, y) to chess notation ('a1', 'b3', etc.)
    def getChessNotation(self, coords):
        """Convert a tuple of coordinates (x, y) to chess notation (e.g., (0, 0) -> 'a8')."""
        col = chr(coords[1] + ord('a'))
        row = str(8 - coords[0])
        return col + row

    '''
    Take a Move as a parametter and excutes it
    '''

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove  # swap player
        # update the king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # pawn promo
        if move.pawnPromotion:
            promotionPiece = 'Q'
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotionPiece
        # enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing
        self.enpassantPossibleLog.append(self.enpassantPossible)
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = () 
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'
                
        self.moveLog.append(move)
        
    '''
    undo
    '''

    def undoMove(self):
        if len(self.moveLog) == 0:
            print("No moves to undo!")
            return  # No move to undo
        
        if self.checkmate or self.stalemate:
            print("Cannot undo after checkmate or stalemate!")
            return  # Prevent undo after game over states
        
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # swap players
            # update the king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = 'bp' if self.whiteToMove else 'wp'
                self.enpassantPossibleLog.append(self.enpassantPossible)
                
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
                
            # Undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRights = CastleRights(self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks,
                                                      self.castleRightsLog[-1].wqs, self.castleRightsLog[-1].bqs)

            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # Undo pawn promotion
            if move.pawnPromotion:
                self.board[move.startRow][move.startCol] = 'wp' if move.pieceMoved[0] == 'w' else 'bp'
                if move.pieceCaptured != '--':
                    self.board[move.endRow][move.endCol] = move.pieceCaptured
                else:
                    self.board[move.endRow][move.endCol] = '--'
                
            # Undo castling move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
    
        self.checkmate = False;
        self.stalemate = False;
    
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    '''
    All move considering checks
    '''

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i , kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
        
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) 
        return moves
    
    '''
    Get all the pawn moves
    '''

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        pawnPromotion = False

        if self.board[r + moveAmount][c] == "--":  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r + moveAmount == backRow:  # get to back rank
                    pawnPromotion = True
                else:
                    pawnPromotion = False
                moves.append(Move((r, c), (r + moveAmount, c), self.board, pawnPromotion=pawnPromotion))  # 2 square pawn advance
                if  r == startRow and self.board[r + 2 * moveAmount][c] == "--":
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        if c - 1 >= 0:  # captures to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    else:
                        pawnPromotion = False
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))
        if c + 1 <= 7:  # captures to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    else:
                        pawnPromotion = False
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isEnpassantMove=True))
        
    '''
    Get all the rook moves
    '''

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:  # off board
                    break

    '''
    Get all the knight moves
    '''

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Get all the bishop moves
    '''

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    Get all the queen moves
    '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
                
    '''
    Get all King moves
    '''

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, _, _ = self.checkForPinsAndChecks()  # pins and checks
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, allyColor)
    
    def getCastleMoves(self, r, c, moves, allyColor):
        self.inCheck = self.squareUnderAttack(r, c, allyColor)
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    def getKingsideCastleMoves(self, r, c, moves, allyColor):
            if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and \
            not self.squareUnderAttack(r, c + 1, allyColor) and not self.squareUnderAttack(r, c + 2, allyColor):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
            not self.squareUnderAttack(r, c - 1, allyColor) and not self.squareUnderAttack(r, c - 2, allyColor):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def squareUnderAttack(self, r, c, allyColor):
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = (
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        )
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        piecetype = endPiece[1]
                        if (0 <= j <= 3 and piecetype == 'R') or \
                                (4 <= j <= 7 and piecetype == 'B') or \
                                (i == 1 and piecetype == 'p' and (
                                    (enemyColor == 'w' and (4 <= j <= 5)) or
                                    (enemyColor == 'b' and (6 <= j <= 7)))) \
                                or piecetype == 'Q' or (i == 1 and piecetype == 'K'):
                            return True
                        else:
                            break
                else:
                    break

        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    return True

        return False
    
    '''
    return if the player in check, a list of pins, and list of check
    '''

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow, startCol = self.whiteKingLocation
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow, startCol = self.blackKingLocation

        directions = [
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for j in range(len(directions)):
            d = directions[j]
            possiblePin = None
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin is None:
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        piecetype = endPiece[1]
                        if (0 <= j <= 3 and piecetype == 'R') or \
                                (4 <= j <= 7 and piecetype == 'B') or \
                                (i == 1 and piecetype == 'p' and (
                                    (enemyColor == 'w' and 6 <= j <= 7) or
                                    (enemyColor == 'b' and 4 <= j <= 5))) \
                                or piecetype == 'Q' or (i == 1 and piecetype == 'K'):
                            if possiblePin is None:
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks


class CastleRights():

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k, v in filesToCols.items()}
    
    def __init__(self, startSq , endSq, board, pawnPromotion=False, isEnpassantMove=False, isCastleMove=False, inCheck_instance=None):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.pawnPromotion = pawnPromotion
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.isCapture = self.pieceCaptured != '--'
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.inCheck_instance = inCheck_instance
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getRanksFiles(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self):
        return self.getRanksFiles(self.startRow, self.startCol) + self.getRanksFiles(self.endRow, self.endCol)
        
    def __str__(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRanksFiles(self.endRow, self.endCol)
        if self.pawnPromotion:
            return endSquare + "=" + self.pieceMoved[0].upper()
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        moveString = self.pieceMoved[1]

        if self.isCapture:
            moveString += "x"

        moveString += endSquare
        # if self.inCheck_instance and self.inCheck_instance.inCheck:
        #     moveString += "+"

        return moveString
    
    @staticmethod
    def fromUci(uci, board):
        """Create a Move object from a UCI string (e.g., 'e2e4')."""
        # UCI format is: <startFile><startRank><endFile><endRank> (e.g., 'e2e4')
        startFile = uci[0]
        startRank = uci[1]
        endFile = uci[2]
        endRank = uci[3]
        
        # Convert files (letters) to column indices
        startCol = Move.filesToCols[startFile]
        endCol = Move.filesToCols[endFile]
        
        # Convert ranks (numbers) to row indices
        startRow = Move.ranksToRows[startRank]
        endRow = Move.ranksToRows[endRank]
        
        pieceMoved = board[startRow][startCol]
        pawnPromotion = False

        if pieceMoved[1] == 'p' and (endRow == 0 or endRow == 7):
            pawnPromotion = True
        
        return Move((startRow, startCol), (endRow, endCol), board, pawnPromotion)
