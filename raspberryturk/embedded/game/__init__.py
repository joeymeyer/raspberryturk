import os
import logging
from pathlib import Path

import chess
import time
from raspberryturk import games_path
from chess.pgn import read_game, Game, FileExporter

from raspberryturk.core import mkdir

TEMPORARY_GAME_PATH = Path(os.path.extsep.join(['tmp', 'pgn']))
mkdir(TEMPORARY_GAME_PATH.parent)
CURRENT_GAME_PATH = Path(games_path(os.path.extsep.join(['game', 'pgn'])))
mkdir(CURRENT_GAME_PATH.parent)

def _logger():
    return logging.getLogger(__name__)

def _game():
    with open(CURRENT_GAME_PATH) as pgn:
        return read_game(pgn)

def _save_game(game, path=CURRENT_GAME_PATH):
    _logger().info("Saving game '{}'...".format(path))
    pgn = open(path, 'w')
    exporter = FileExporter(pgn)
    game.accept(exporter)
    pgn.close()
    _logger().info("Done saving game '{}'.".format(path))
    # _sync()

def is_temporary():
    base = os.path.basename(os.path.realpath(CURRENT_GAME_PATH))
    return base == TEMPORARY_GAME_PATH

def start_new_game(temporary=False):
    base = 'tmp' if temporary else str(int(time.time()))
    fn = os.path.extsep.join([base, 'pgn'])
    path = games_path(fn)
    _logger().info("Starting new game '{}'...".format(path))
    game = Game()
    game.headers["Date"] = time.strftime("%Y.%m.%d")
    game.headers["White"] = "Human"
    game.headers["Black"] = "Raspberry Turk"
    _save_game(game, path)
    enter_game(fn)

def enter_game(fn):
    try:
        os.unlink(CURRENT_GAME_PATH)
    except OSError as e:
        if e.errno != 2:
            raise e
    os.symlink(fn, CURRENT_GAME_PATH)
    _logger().info("Entered game {} -> {}".format(CURRENT_GAME_PATH, fn))
    _sync()

def get_board() -> chess.Board:
    g = _game()
    return g.end().board()

def apply_move(move, comment=''):
    _logger().info("Applying move {}...".format(move.uci()))
    g = _game()
    b = g.end().board()
    assert move in b.legal_moves, "{0} is not a legal move for board {1}".format(move.uci(), b.fen())
    g.end().add_main_variation(move, comment=comment)
    b.push(move)
    g.headers["Result"] = b.result()
    _save_game(g)
    _logger().info("Applied move {}.".format(move.uci()))

def pgn():
    return str(_game())

def setup_games_repo():
    if not os.path.exists(os.path.join(games_path('.git'))):
        commands = [
            "cd {}".format(games_path()),
            "echo \"{}\" > .gitignore".format(TEMPORARY_GAME_PATH),
            "git init",
            "git add .gitignore",
            "git commit -m \"Initial commit\""
        ]
        os.system(";".join(commands))

def _sync():
    _logger().info("Syncing games...")
    b = get_board()
    commit_message = "new game"
    if len(b.move_stack) > 0:
        color = chess.COLOR_NAMES[not b.turn]
        move = b.move_stack[-1].uci()
        commit_message = "{} {}".format(color, move)
    commands = [
        "cd {}".format(games_path()),
        "git add --all",
        "git commit -m \"{}\"".format(commit_message)
    ]
    os.system(";".join(commands))
    _logger().info("Sync games successful.")
