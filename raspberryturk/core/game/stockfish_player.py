import chess.engine


class StockfishPlayer(object):
    def __init__(self):
        self._engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
        # self._engine.uci()

    def select_move(self, board) -> chess.Move:
        # self._engine.position(board)
        result = self._engine.play(board, chess.engine.Limit(time=0.1))
        return result.move
