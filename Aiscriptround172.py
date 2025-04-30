import chess
import math
import random

move_history = []

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

pawn_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10,-20,-20, 10, 10,  5,
    5, -5,-10,  0,  0,-10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10,25,25, 10,  5,  5,
    10, 10, 20,30,30, 20, 10, 10,
    50, 50, 50,50,50, 50, 50, 50,
    0,  0,  0,  0,  0,  0,  0,  0
]

knight_table = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -30,  5, 10,15,15, 10,  5,-30,
   -30,  0, 15,20,20, 15,  0,-30,
   -30,  5, 15,20,20, 15,  5,-30,
   -30,  0, 10,15,15, 10,  0,-30,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]

piece_square_tables = {
    chess.PAWN: pawn_table,
    chess.KNIGHT: knight_table,
}

def evaluate_board(board: chess.Board) -> int:
    """Evaluate board with material, positional heuristics, and king safety."""
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue

        value = piece_values[piece.piece_type]
        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value

        pst = piece_square_tables.get(piece.piece_type)
        if pst:
            index = square if piece.color == chess.WHITE else chess.square_mirror(square)
            bonus = pst[index]
            score += bonus if piece.color == chess.WHITE else -bonus

    king_position = board.king(chess.WHITE) if board.turn == chess.WHITE else board.king(chess.BLACK)
    score += center_control(king_position, board)

    return score

def center_control(king_square, board):
    """Give a bonus for king being closer to the center."""
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    return 10 if king_square in center_squares else 0


def quiescence(board, alpha, beta):
    """Extend search during unstable positions (e.g., captures)."""
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    return alpha

def order_moves(board):
    """Order moves by capture and checks."""
    captures = []
    non_captures = []
    for move in board.legal_moves:
        if board.is_capture(move):
            captures.append(move)
        else:
            non_captures.append(move)

    # Order captures first
    captures.sort(key=lambda move: board.piece_at(move.to_square).piece_type, reverse=True)
    return captures + non_captures


def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return evaluate_board(board), None

    best_move = None
    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

def findBestMove(fen: str):
    board = chess.Board(fen)
    _, best_move = minimax(board, depth=4, alpha=-math.inf, beta=math.inf, maximizing_player=board.turn)
    
    if best_move in move_history:
        legal_moves = list(board.legal_moves)
        best_move = random.choice(legal_moves) if legal_moves else None
    
    move_history.append(best_move)
    return best_move.uci() if best_move else None
