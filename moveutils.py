from typing import Iterator
import chess as c

def encode_precise(board: c.Board, move: c.Move) -> str:

    s = c.piece_symbol(board.piece_type_at(move.from_square))
    s += c.square_name(move.from_square)

    if board.is_en_passant(move):
        s += "x" + c.piece_name(c.PAWN)
    elif board.is_capture(move):
        s += "x" + c.piece_name(board.piece_type_at(move.to_square))

    s += c.square_name(move.to_square)

    if move.promotion is not None:
        s += "=" + c.piece_symbol(move.promotion)

    return s

def matches(precise_move: str, candidate: str) -> bool:
    p, c = 0, 0
    while True:
        if c == len(candidate):
            return True
        elif p == len(precise_move):
            return False
        elif precise_move[p] == candidate[c]:
            p += 1
            c += 1
        else:
            p += 1

def candidates(board: c.Board, candidate: str) -> Iterator[c.Move]:
    for move in board.generate_legal_moves():
        if matches(encode_precise(board, move), candidate):
            yield move
