def _symbols_dict(symbols):
    return dict(zip(symbols, range(len(symbols))))

_COLOR_PIECE_SYMBOLS = _symbols_dict(['p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', 'B', 'R', 'Q', 'K', None])
_COLOR_PIECE_SYMBOLS_NOEMPTY = _symbols_dict(['p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', 'B', 'R', 'Q', 'K'])
_PIECE_SYMBOLS = _symbols_dict(['p', 'n', 'b', 'r', 'q', 'k', None])
_PIECE_SYMBOLS_NOEMPTY = _symbols_dict(['p', 'n', 'b', 'r', 'q', 'k'])
_PROMOTABLE_PIECE_SYMBOLS = _symbols_dict(['n', 'b', 'r', 'q'])

def _is_empty(piece_symbol):
    return piece_symbol == 'e' or piece_symbol is None

def _num_classes(n):
    def _num_classes_decorator(func):
        func.num_classes = n
        return func
    return _num_classes_decorator

def _dict_lookup(symbols_dict, piece_symbol):
    return symbols_dict.get(piece_symbol, -1)

@_num_classes(2)
def empty_or_not(piece_symbol):
    return int(_is_empty(piece_symbol))

@_num_classes(3)
def white_or_black(piece_symbol):
    if piece_symbol == 'e':
        piece_symbol = None
    if piece_symbol not in _COLOR_PIECE_SYMBOLS.keys():
        return -1
    else:
        if piece_symbol is None:
            return 0
        else:
            return int(not piece_symbol.islower()) + 1

@_num_classes(2)
def white_or_black_noempty(piece_symbol):
    if piece_symbol not in _COLOR_PIECE_SYMBOLS_NOEMPTY.keys():
        return -1
    else:
        return int(not piece_symbol.islower())

@_num_classes(len(_COLOR_PIECE_SYMBOLS.keys()))
def color_piece(piece_symbol):
    return _dict_lookup(_COLOR_PIECE_SYMBOLS, piece_symbol)

@_num_classes(len(_COLOR_PIECE_SYMBOLS_NOEMPTY.keys()))
def color_piece_noempty(piece_symbol):
    return _dict_lookup(_COLOR_PIECE_SYMBOLS_NOEMPTY, piece_symbol)

@_num_classes(len(_PIECE_SYMBOLS.keys()))
def piece(piece_symbol):
    return _dict_lookup(_PIECE_SYMBOLS, piece_symbol)

@_num_classes(len(_PIECE_SYMBOLS_NOEMPTY.keys()))
def piece_noempty(piece_symbol):
    return _dict_lookup(_PIECE_SYMBOLS_NOEMPTY, piece_symbol)

@_num_classes(len(_PROMOTABLE_PIECE_SYMBOLS.keys()))
def promotable_piece(piece_symbol):
    return _dict_lookup(_PROMOTABLE_PIECE_SYMBOLS, piece_symbol)

ENCODING_FUNCTIONS = [empty_or_not, white_or_black, color_piece, color_piece_noempty, piece, piece_noempty, promotable_piece]
