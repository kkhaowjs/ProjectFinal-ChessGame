import chess
import time
import random
import AiMoveScript

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000
}

pawn_position_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]

knight_position_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishop_position_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 10, 15, 15, 10, 5, -10,
    -10, 10, 15, 20, 20, 15, 10, -10,
    -10, 5, 10, 15, 15, 10, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
    -20, -10, -10, -10, -10, -10, -10, -20
]

rook_position_table = [
    0, 0, 0, 5, 5, 0, 0, 0,
    0, 0, 5, 10, 10, 5, 0, 0,
    0, 5, 10, 15, 15, 10, 5, 0,
    5, 10, 15, 20, 20, 15, 10, 5,
    5, 10, 15, 20, 20, 15, 10, 5,
    0, 5, 10, 15, 15, 10, 5, 0,
    0, 0, 5, 10, 10, 5, 0, 0,
    0, 0, 0, 5, 5, 0, 0, 0
]

queen_position_table = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 5, 0, 0, 5, 0, -10,
    -10, 5, 10, 10, 10, 10, 5, -10,
    -5, 0, 10, 15, 15, 10, 0, -5,
    -5, 0, 10, 15, 15, 10, 0, -5,
    -10, 5, 10, 10, 10, 10, 5, -10,
    -10, 0, 5, 0, 0, 5, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

king_position_table = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -40, -60, -60, -70, -70, -60, -60, -40,
    -40, -60, -60, -70, -70, -60, -60, -40,
    -50, -70, -70, -80, -80, -70, -70, -50,
    -50, -70, -70, -80, -80, -70, -70, -50,
    -40, -60, -60, -70, -70, -60, -60, -40,
    -40, -60, -60, -70, -70, -60, -60, -40,
    -30, -40, -40, -50, -50, -40, -40, -30
]

def evaluate_board(board):
    evaluation = 0
    for square in range(64):
        piece = board.piece_at(square)
        if piece:
            piece_value = piece_values.get(piece.piece_type, 0)
            
            if piece.piece_type == chess.PAWN:
                position_value = pawn_position_table[square]
            elif piece.piece_type == chess.KNIGHT:
                position_value = knight_position_table[square]
            elif piece.piece_type == chess.BISHOP:
                position_value = bishop_position_table[square]
            elif piece.piece_type == chess.ROOK:
                position_value = rook_position_table[square]
            elif piece.piece_type == chess.QUEEN:
                position_value = queen_position_table[square]
            elif piece.piece_type == chess.KING:
                position_value = king_position_table[square]
            else:
                position_value = 0

            if piece.color == chess.WHITE:
                evaluation += piece_value + position_value
            else:
                evaluation -= piece_value + position_value

    return evaluation

def minimax(board, depth, maximizing_player, alpha, beta):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)
    
    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            board.pop()
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            board.pop()
            if beta <= alpha:
                break
        return min_eval

def MiNimaxfindBestMove(fen: str, time_limit=1.0, skill_level=5):
    # Get move from Stockfish (or any other AI source you have for comparison)
    aimove = AiMoveScript.findBestMoveStockfish(fen, time_limit=time_limit, skill_level=skill_level)
    
    # Initialize the board with the given FEN position
    board = chess.Board(fen)
    
    # Define skill level and depth
    skill_level = min(max(skill_level, 0), 20)
    depth = max(1, skill_level // 2)

    best_move = None
    best_value = -float('inf')

    legal_moves = list(board.legal_moves)
    
    start_time = time.time()

    # Minimax evaluation for best move
    for move in legal_moves:
        if time.time() - start_time > time_limit:
            break
        
        board.push(move)
        move_value = minimax(board, depth - 1, False, -float('inf'), float('inf'))
        if move_value > best_value:
            best_value = move_value
            best_move = move
        board.pop()

    # If no best move was found, fall back to a random move
    if best_move is None:
        best_move = random.choice(legal_moves)

    # Randomly decide whether to switch to Stockfish's move or use the best move
    use_stockfish_move = random.choice([True, False])  # Randomly choose to use Stockfish or Minimax move
    
    if use_stockfish_move and aimove:
        best_move = chess.Move.from_uci(aimove)

    # Return the best move (either from Minimax or Stockfish)
    return best_move.uci()