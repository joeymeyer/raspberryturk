import os
import chess
from raspberryturk.embedded.chess import game
from raspberryturk import games_path

def setup():
    if not os.path.exists(os.path.join(games_path('.git'))):
        commands = [
            "cd {}".format(games_path()),
            "echo \"{}\" > .gitignore".format(game.TEMPORARY_GAME_PATH),
            "git init",
            "git add .gitignore",
            "git commit -m \"Initial commit\""
        ]
        os.system(";".join(commands))

def sync():
    b = game.get_board()
    commit_message = "new game"
    if len(b.move_stack) > 0:
        commit_message = str(b.move_stack[-1])
    commands = [
        "cd {}".format(games_path()),
        "git add --all",
        "git commit -m \"{}\"".format(commit_message)
    ]
    os.system(";".join(commands))
