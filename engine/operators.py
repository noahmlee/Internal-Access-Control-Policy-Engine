def equals(a, b):
    return a == b

def in_(a, b):
    return a in b

OPERATORS = {
    "equals": equals,
    "in": in_,
}
