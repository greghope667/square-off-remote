from squareoff import SquareOff
import player

import time

import chess
import chess.pgn

so = SquareOff()

## Some games - change comments to set mode

# Player (board input) versus stockfish
white = so.start_game(player=chess.WHITE)
black = player.player_stockfish(skill=0)

## Stockfish versus random
#so.start_game()
#white = player.player_stockfish(skill=0)
#black = player.player_random()

## Stockfish vs player (text input)
#so.start_game()
#white = player.player_stockfish(skill=0)
#black = player.player_cli()

## Player (voice) vs random
#so.start_game()
#white = player.player_voice()
#black = player.player_random()

try:
    game = chess.pgn.Game()
    node = game

    board = chess.Board()

    active, non_active = white, black
    while not board.is_game_over(claim_draw = True):
        move = active(board)
        print(move.uci())
        board.push(move)
        node = node.add_variation(move)
        so.make_move(move)
        active, non_active = non_active, active
        time.sleep(1)

    so.end_game()
    print(game)
finally:
    so.disconnect()
