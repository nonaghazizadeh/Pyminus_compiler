from Parser.enums import FIRST, FOLLOW, TERMINAL, NON_TERMINAL, GRAMMAR
from Parser.helper import get_first


class Parser:
    def __init__(self):
        self.table = {fi: {} for fi in NON_TERMINAL}
        self.stack = []

    def create_table(self):
        for A, v in GRAMMAR.items():
            for alpha in v:
                firsts = get_first(alpha)
                for t in firsts:
                    if t is not None:
                        self.table[A][t] = alpha

                if None in firsts:
                    for t in FOLLOW[A]:
                        self.table[A][t] = alpha
