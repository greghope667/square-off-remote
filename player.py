import typing
import random

import chess
import chess.engine

Player: typing.TypeAlias = typing.Callable[[chess.Board], chess.Move]

def random_player() -> Player:
    return lambda b: random.choice(list(b.generate_legal_moves()))

def stockfish_player() -> Player:
    engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    return lambda b: engine.play(b, chess.engine.Limit(time=0.1)).move

