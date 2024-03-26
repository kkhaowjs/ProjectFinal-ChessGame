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