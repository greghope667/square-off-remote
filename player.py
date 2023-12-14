import typing
import random

import chess
import chess.engine

import moveutils

Player: typing.TypeAlias = typing.Callable[[chess.Board], chess.Move]

def player_random() -> Player:
    return lambda b: random.choice(list(b.generate_legal_moves()))

def player_stockfish(skill=None) -> Player:
    engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    if skill is not None:
        engine.configure({"Skill Level": skill})
    return lambda b: engine.play(b, chess.engine.Limit(time=0.1)).move

def player_voice() -> Player:
    import voice
    vc = voice.VoiceControl()

    def play(board: chess.Board) -> chess.Move:
        for phrase in vc.listen():
            candidate = vc.translate_phrase(phrase)
            print("Searching", candidate)
            candidates = list(moveutils.candidates(board, candidate))
            print("Potential moves:", candidates)
            if len(candidates) == 1:
                move = candidates[0]
                print("Playing", move.uci())
                return move
            else:
                print("Move ambiguous, please try again")

    return play

def player_cli() -> Player:
    def play(board: chess.Board) -> chess.Move:
        while True:
            text = input("Enter move: ").lower()
            candidates = list(moveutils.candidates(board, text))
            if len(candidates) == 1:
                move = candidates[0]
                print("Playing", move.uci())
                return move
            elif len(candidates) == 0:
                print("Unknown/invalid move")
            else:
                print("Move ambiguous, candidates", [moveutils.encode_precise(board, m) for m in candidates])

    return play
