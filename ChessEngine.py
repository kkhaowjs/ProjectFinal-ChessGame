"""
Responsible for starting all the information about state of a chess game.
"""
class GameState():
    def __init__(self):
        #Board is an 8x8 2d list, each element of the list has 2 character.
        #The first character represents the color of a piece, 'b' or 'w'
        #The second character repersents the type of the piece, 'K', 'Q', 'R', 'B', 'N','P'.
        #"--" - represents an empty space with no piece.
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--",],
            ["--","--","--","--","--","--","--","--",],
            ["--","--","--","--","--","--","--","--",],
            ["--","--","--","--","--","--","--","--",],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.whiteToMove = True
        self.moveLog = []
        
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #to make undo later
        self.whiteToMove = not self.whiteToMove #swap player
        
class Move():
    #maps key values
    #key : value
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5, "g":6,"h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    
    def __init__(self, startSq , endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
    def getChessNotation(self):
        return self.getRanksFiles(self.startRow, self.startCol) + self.getRanksFiles(self.endRow, self.endCol)
        
    def getRanksFiles(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]