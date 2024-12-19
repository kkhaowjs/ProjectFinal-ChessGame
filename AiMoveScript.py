import chess  # noqa: F401
import chess.engine

# Define the correct path to your Stockfish executable
STOCKFISH_PATH = "C:\\Users\\jetsa\\OneDrive\\Desktop\\stockfish\\stockfish-windows-x86-64-avx2.exe"


def findBestMoveStockfish(fen: str, time_limit=1.0, skill_level=10):
    """
    Uses Stockfish to find the best move for a given FEN position with an adjustable Elo rating.
    
    Args:
        fen (str): The FEN string representing the chessboard position.
        time_limit (float): Time limit for Stockfish's analysis in seconds.
        skill_level (int): The skill level of the bot (0-20).
    
    Returns:
        str: The best move in UCI format (e.g., 'e2e4').
    """
    try:
        # Start the Stockfish engine
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # Set the skill level based on the Elo
            # Map Elo rating to Stockfish's skill level (e.g., 0-20 range)
            engine.configure({"Skill Level": skill_level})
            board = chess.Board(fen)
            result = engine.play(board, chess.engine.Limit(time=time_limit))
            return result.move.uci()
    except Exception as e:
        print(f"Error using Stockfish: {e}")
        return None



def adjustableBotElo(fen: str, elo_rating: int, time_limit=2.0):
    """
    Adjusts the bot's difficulty based on the Elo rating.
    
    Args:
        fen (str): The FEN string representing the chessboard position.
        elo_rating (int): The Elo rating for the bot (e.g., 1200, 1500, 2000).
        time_limit (float): Time limit for Stockfish's analysis in seconds.
    
    Returns:
        str: The best move in UCI format.
    """
    # Adjust skill level based on Elo rating
    skill_level = (elo_rating - 1000) // 100  # Map Elo to Stockfish skill level (0-20)
    skill_level = max(0, min(20, skill_level))  # Ensure skill level is between 0 and 20

    return findBestMoveStockfish(fen, time_limit, skill_level)
