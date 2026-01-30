def equals(a, b):
    return a == b


def in_(a, b):
    if b is None:
        return False
    try:
        return a in b
    except TypeError:
        return False


def gt(a, b):
    if a is None or b is None:
        return False
    try:
        return a > b
    except TypeError:
        return False


def lt(a, b):
    if a is None or b is None:
        return False
    try:
        return a < b
    except TypeError:
        return False


OPERATORS = {
    "equals": equals,
    "in": in_,
    "gt": gt,
    "lt": lt,
}
