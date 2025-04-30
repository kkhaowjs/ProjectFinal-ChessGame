import chess  # noqa: F401
import chess.engine
STOCKFISH_PATH = "C:\\Users\\jetsa\\OneDrive\\Desktop\\stockfish\\stockfish-windows-x86-64-avx2.exe"


def findBestMoveStockfish(fen: str, time_limit=1.0, white_elo=1500, black_elo=1500):
    """
    Uses Stockfish to find the best move for a given FEN position with adjustable Elo ratings for white and black.
    
    Args:
        fen (str): The FEN string representing the chessboard position.
        time_limit (float): Time limit for Stockfish's analysis in seconds.
        white_elo (int): The Elo rating for the white pieces.
        black_elo (int): The Elo rating for the black pieces.
    
    Returns:
        str: The best move in UCI format (e.g., 'e2e4').
    """
    try:
        board = chess.Board(fen)
        is_white_turn = board.turn == chess.WHITE
        elo_rating = white_elo if is_white_turn else black_elo
        # Adjust skill level based on Elo rating
        if elo_rating < 800:
            skill_level = 0
        elif elo_rating < 1500:
            skill_level = 5
        elif elo_rating < 2000:
            skill_level = 10
        elif elo_rating < 2500:
            skill_level = 15
        else:
            skill_level = 20

        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            engine.configure({"Skill Level": skill_level})
            result = engine.play(board, chess.engine.Limit(time=time_limit))
            return result.move.uci()
    except Exception as e:
        print(f"Error using Stockfish: {e}")
        return None


def adjustableBotElo(fen: str, white_elo: int, black_elo: int, time_limit=2.0):
    """
    Adjusts the bot's difficulty based on the Elo ratings for white and black.
    
    Args:
        fen (str): The FEN string representing the chessboard position.
        white_elo (int): The Elo rating for the white pieces.
        black_elo (int): The Elo rating for the black pieces.
        time_limit (float): Time limit for Stockfish's analysis in seconds.
    
    Returns:
        str: The best move in UCI format.
    """
    return findBestMoveStockfish(fen, time_limit, white_elo, black_elo)