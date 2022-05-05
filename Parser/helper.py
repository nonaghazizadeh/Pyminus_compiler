from Parser.enums import FIRST, TERMINAL


def get_first(alpha: str):
    res = set()
    if alpha is None:
        res.add(None)
        return res

    for beta in alpha.split(" "):
        if beta in TERMINAL:
            res.add(beta)
            return res

        res.update(FIRST[beta])
        if None in FIRST[beta]:
            res.remove(None)
            continue

        return res

    res.add(None)
    return res


def extract_token(t):
    if t == '$':
        return '$'
    elif t[0] == 'ID':
        return 'ID'
    elif t[0] == 'NUMBER':
        return 'NUM'
    else:
        return t[1]
