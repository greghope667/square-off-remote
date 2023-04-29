from squareoff import SquareOff
import player

import chess

white = player.random_player()
black = player.stockfish_player()

try:
    so = SquareOff()
    so.start_game()

    board = chess.Board()

    active, non_active = white, black
    while not board.is_game_over(claim_draw = True):
        move = active(board)
        print(move.uci())
        board.push(move)
        so.make_move(move)
        active, non_active = non_active, active

    so.end_game()
finally:
    so.disconnect()
