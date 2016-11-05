import os
from time import time
from raspberryturk import games_path
from chess.pgn import read_game, Game, FileExporter

TEMPORARY_GAME_PATH = os.path.extsep.join(['tmp', 'pgn'])
CURRENT_GAME_PATH = games_path(os.path.extsep.join(['game', 'pgn']))

def _game():
    with open(CURRENT_GAME_PATH) as pgn:
        return read_game(pgn)

def _save_game(game, path=CURRENT_GAME_PATH):
    pgn = open(path, 'w')
    exporter = FileExporter(pgn)
    game.accept(exporter)
    pgn.close()

def is_temporary():
    base = os.path.basename(os.path.realpath(CURRENT_GAME_PATH))
    return base == TEMPORARY_GAME_PATH

def start_new_game(temporary=False):
    base = 'tmp' if temporary else str(int(time()))
    fn = os.path.extsep.join([base, 'pgn'])
    path = games_path(fn)
    _save_game(Game(), path)
    enter_game(fn)

def enter_game(fn):
    try:
        os.unlink(CURRENT_GAME_PATH)
    except OSError as e:
        if e.errno != 2:
            raise e
    os.symlink(fn, CURRENT_GAME_PATH)

def get_board():
    g = _game()
    return g.end().board()

def apply_move(move, comment=''):
    g = _game()
    b = g.end().board()
    assert move in b.legal_moves, "{0} is not a legal move for board {1}".format(move.uci(), b.fen())
    g.end().add_main_variation(move, comment=comment)
    _save_game(g)
