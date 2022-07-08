from Parser.enums import FIRST, TERMINAL


def get_first(alpha: str):
    res = set()
    alpha = remove_action_symbols(alpha)
    if 'EPSILON' == alpha:
        res.add('EPSILON')
        return res

    for beta in alpha.split(" "):

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


def remove_action_symbols(alpha: str, action_symbols=['#', '@']):
    res = []
    for s in alpha.split(' '):
        if s[0] not in action_symbols:
            res.append(s)

    return ' '.join(res)

