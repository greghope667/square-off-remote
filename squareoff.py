import time
import chess

import communicator

class SquareOff:

    def __init__(self):
        self._board = communicator.Communicator()
        self._start_comms()

        print("Connected, battery = ", self.battery())

    def _start_comms(self):
        self._board.run()
        self._board.transmit("CONNECTED")

    def make_move(self, move: chess.Move):
        self._board.transmit(move.uci()[:4])
        self._board.receive()

    def start_game(self):
        self._board.transmit("LIVE")

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
