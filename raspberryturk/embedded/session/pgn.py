from path import session_path
from chess.pgn import read_game
from chess.pgn import Game
from chess.pgn import FileExporter

def _pgn_path():
    return session_path('game.pgn')

def _game():
    pgn = open(_pgn_path())
    return read_game(pgn)

def _save_game(game):
    pgn = open(_pgn_path(), 'w')
    exporter = FileExporter(pgn)
    game.accept(exporter)

def start_new_game():
    _save_game(Game())

def get_board():
    g = _game()
    return g.end().board()

def apply_move(move, comment=''):
    g = _game()
    b = g.end().board()
    assert move in b.legal_moves, "{0} is not a legal move for board {1}".format(move.uci(), b.fen())
    g.end().add_main_variation(move, comment=comment)
    _save_game(g)
