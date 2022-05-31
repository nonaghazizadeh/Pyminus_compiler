from Parser.enums import FIRST, TERMINAL


def get_first(alpha: str):
    res = set()
    if alpha == 'EPSILON':
        res.add('EPSILON')
        return res

    for beta in alpha.split(" "):
        if beta[0] == '#':
            continue

        if beta in TERMINAL:
            res.add(beta)
            return res

        res.update(FIRST[beta])
        if 'EPSILON' in FIRST[beta]:
            res.remove('EPSILON')
            continue

        return res

    res.add('EPSILON')
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
