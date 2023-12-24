import time
import chess

import communicator

class SquareOff:

    def __init__(self):
        self._board = communicator.Communicator()
        self._start_comms()
        self._active_player = None

        print("Connected, battery = ", self.battery())

    def _start_comms(self):
        self._board.run()
        self._board.transmit("CONNECTED")

    def _play(self, board: chess.Board) -> chess.Move:
        def parse(b: chess.Board, s: str) -> chess.Move|None:
            try:
                if (m:=chess.Move.from_uci(s)) in board.legal_moves:
                    return m
            except chess.InvalidMoveError:
                pass
            return None

        while True:
            pressed = self._board.receive()
            if move:=parse(board, pressed):
                self._board.transmit("OK")
                return move
            elif move:=parse(board, pressed+"q"):
                self._board.transmit("OK")
                return move
            else:
                self._board.transmit("ERR")
                print("Illegal move", pressed)

    def make_move(self, move: chess.Move):
        if self._active_player == True:
            self._active_player = False
            return

        self._board.transmit(move.uci()[:4])

        if self._active_player == False:
            self._active_player = True
        else:
            # Wait for OK response
            self._board.receive()

    def start_game(self, player=None):
        self.end_game()
        if player is None:
            self._active_player = None
            self._board.transmit("LIVE")
            return
        elif player == chess.WHITE:
            self._active_player = True
            self._board.transmit("GAMEWHITE")
        else:
            self._active_player = False
            self._board.transmit("GAMEBLACK")
        return self._play

    def end_game(self):
        self._board.transmit("RSTVAR")

    def battery(self) -> str:
        self._board.transmit("BATTERY")
        return self._board.receive()

    def disconnect(self):
        self._board.stop()


def _main(move_count = 4):
    """
    Do some random moves for testing
    """
    import random
    import time

    so = SquareOff()
    so.start_game()

    board = chess.Board()
    for i in range(move_count):
        move = random.choice(list(board.generate_legal_moves()))
        print(f"Moving {i+1}/{move_count} :", move.uci())
        so.make_move(move)
        board.push(move)

    so.end_game()
    print("Done with random moves, exiting")

    so.disconnect()

if __name__ == "__main__":
    _main()
