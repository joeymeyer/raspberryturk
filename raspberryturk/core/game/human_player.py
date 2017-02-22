import socket
import sys
import os
import logging
import argparse
from raspberryturk import lib_path, setup_console_logging

SERVER_ADDRESS = lib_path('human_player_uds_socket')

class HumanPlayer(object):
    def __init__(self):
        try:
            os.unlink(SERVER_ADDRESS)
        except OSError:
            if os.path.exists(SERVER_ADDRESS):
                raise
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(SERVER_ADDRESS)
        self._sock.listen(1)

    def select_move(self, board):
        moves_dict = { str(move) : move for move in board.legal_moves }
        move = None
        while move is None:
            connection, client_address = self._sock.accept()
            try:
                data = connection.recv(4)
                move = moves_dict.get(data, None)
                connection.sendall("selected move: {}".format(move))
            finally:
                connection.close()
        return move

def _get_args():
    prog = os.path.relpath(__file__)
    desc = "Send moves to the raspberryturk HumanPlayer"
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('move', type=str, help="UCI string of a valid move (ex. e2e4).")
    return parser.parse_args()

def main():
    setup_console_logging()
    args = _get_args()
    logger = logging.getLogger(__name__)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    logger.info("connecting to {}".format(SERVER_ADDRESS))
    try:
        sock.connect(SERVER_ADDRESS)
    except socket.error, msg:
        logger.error(msg)
        raise RaspberryTurkError("There was a problem connecting to {}".format(SERVER_ADDRESS))
    try:
        message = args.move
        logger.info("sending {}".format(message))
        sock.sendall(message)
        data = sock.recv(19)
        logger.info(data)
    finally:
        logger.info("closing socket")
        sock.close()

if __name__ == '__main__':
    main()
