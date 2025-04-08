def quiescence(board, alpha, beta, depth=0, max_depth=10):
    """ Quiescence search to handle captures and prevent horizon effect """
    if depth >= max_depth:
        return evaluate_board(board)  # Return static evaluation if max depth is reached
    
    stand_pat = evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence(board, -beta, -alpha, depth + 1, max_depth)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha