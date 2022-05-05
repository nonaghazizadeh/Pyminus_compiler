from Parser.enums import FIRST, FOLLOW, TERMINAL, NON_TERMINAL, GRAMMAR
from Parser.helper import get_first


class Parser:
    def __init__(self):
        self.table = {fi: {} for fi in NON_TERMINAL}
        self.stack = ['$', 'Program']

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

    def add_synch(self):
        for nt in FOLLOW:
            for fo in FOLLOW[nt]:
                if self.table[nt].get(fo) is None:
                    self.table[nt][fo] = 'synch'

    def parse(self):
        top_of_stack = self.stack.pop()
        current_token = ''
        if current_token == top_of_stack == '$':
            print('SUCCESS')
            return

        if top_of_stack in NON_TERMINAL:
            temp = self.table[top_of_stack].get(current_token)
            if temp is None or temp == 'synch':
                pass
            else:
                temp = temp.split('')
                temp.reverse()
                self.stack.extend(temp)

        if current_token == top_of_stack:
            pass
