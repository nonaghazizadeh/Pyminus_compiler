from Parser.enums import FIRST, FOLLOW, TERMINAL, NON_TERMINAL, GRAMMAR
from Parser.helper import get_first, extract_token

from Scanner.new_version_scanner import Scanner


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
                if fo not in self.table[nt]:
                    self.table[nt][fo] = 'synch'

    def parse(self):
        scanner = Scanner('input.txt')
        self.create_table()
        self.add_synch()
        tabs_controller = [1, 0]
        output = ''
        scanner_res = scanner.get_next_token()
        current_token = extract_token(scanner_res)
        while True:
            # print(f'STACK: {self.stack}')
            # print(f'CURRENT_TOKEN: {current_token}')
            # print(tabs_controller)

            top_of_stack = self.stack.pop()
            depth = tabs_controller.pop()
            if current_token == top_of_stack == '$':
                # print('ACTION: SUCCESS')
                return output

            if top_of_stack in NON_TERMINAL:
                if current_token in self.table[top_of_stack]:
                    temp = self.table[top_of_stack][current_token]
                    if temp == 'synch':
                        # print('SYNCH ERROR')
                        raise RuntimeError
                    elif temp is None:
                        # print(f'ACTION: EPSILON')
                        output += '\t' * depth + top_of_stack + '\n'
                        output += '\t' * (depth + 1) + 'epsilon' + '\n'

                    else:
                        # print(f'ACTION: {temp}')
                        temp = temp.split(' ')
                        temp.reverse()
                        self.stack.extend(temp)

                        output += '\t' * depth + top_of_stack + '\n'
                        tabs_controller.extend([depth + 1 for _ in range(len(temp))])
                else:
                    # print('EMPTY ERROR')
                    raise RuntimeError

            if current_token == top_of_stack:
                # print('ACTION: TERMINAL')
                token_type = scanner_res[0] if scanner_res[0] != 'NUMBER' else 'NUM'
                token_id = scanner_res[1]

                output += '\t' * depth + '(' + token_type + ', ' + token_id + ')' + '\n'
                scanner_res = scanner.get_next_token()
                current_token = extract_token(scanner_res)

            # print(''.join(['-' for _ in range(50)]))
