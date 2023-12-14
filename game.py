from squareoff import SquareOff
import player

import time

import chess

white = player.player_stockfish(skill=0)
black = player.player_random()

so = SquareOff()
try:
    so.start_game()

    board = chess.Board()

    active, non_active = white, black
    while not board.is_game_over(claim_draw = True):
        move = active(board)
        print(move.uci())
        board.push(move)
        so.make_move(move)
        active, non_active = non_active, active
        time.sleep(1)

    so.end_game()
finally:
    so.disconnect()
