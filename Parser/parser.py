from Parser.enums import FIRST, FOLLOW, TERMINAL, NON_TERMINAL, GRAMMAR
from Parser.helper import get_first, extract_token

from Scanner.new_version_scanner import Scanner


class Parser:
    def __init__(self):
        self.table = {fi: {} for fi in NON_TERMINAL}
        self.stack = ['$', 'Program']
        self.parse_tree = ''
        self.syntax_error = ''
        self.scanner = Scanner('input.txt')
        self.create_table()
        self.add_synch()

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
        tabs_controller = [1, 0]
        scanner_res = self.scanner.get_next_token()
        current_token = extract_token(scanner_res)
        while True:
            print(''.join(['-' for _ in range(50)]))
            print(f'STACK: {self.stack}')
            print(f'CURRENT_TOKEN: {current_token}')

            top_of_stack = self.stack.pop()
            depth = tabs_controller.pop()
            if current_token == top_of_stack == '$':
                print('ACTION: SUCCESS')
                self.parse_tree += '\t' * depth + '$'
                return

            if top_of_stack in NON_TERMINAL:
                if current_token in self.table[top_of_stack]:
                    temp = self.table[top_of_stack][current_token]
                    if temp == 'synch':
                        print('SYNCH ERROR')
                        self.recover_error(err_type=2, lineno=self.scanner.lineno, top_of_stack=top_of_stack)
                        continue

                    elif temp is None:
                        print(f'ACTION: EPSILON')
                        self.parse_tree += '\t' * depth + top_of_stack + '\n'
                        self.parse_tree += '\t' * (depth + 1) + 'epsilon' + '\n'

                    else:
                        print(f'ACTION: {temp}')
                        temp = temp.split(' ')
                        temp.reverse()
                        self.stack.extend(temp)

                        self.parse_tree += '\t' * depth + top_of_stack + '\n'
                        tabs_controller.extend([depth + 1 for _ in range(len(temp))])
                else:
                    print('EMPTY ERROR')
                    self.recover_error(err_type=1, lineno=self.scanner.lineno, current_token=current_token)
                    if current_token == '$':
                        return
                    scanner_res = self.scanner.get_next_token()
                    current_token = extract_token(scanner_res)
                    self.stack.append(top_of_stack)
                    tabs_controller.append(depth)
                    continue

            if current_token == top_of_stack:
                print('ACTION: TERMINAL')
                token_type = scanner_res[0] if scanner_res[0] != 'NUMBER' else 'NUM'
                token_id = scanner_res[1]

                self.parse_tree += '\t' * depth + '(' + token_type + ', ' + token_id + ')' + '\n'
                scanner_res = self.scanner.get_next_token()
                current_token = extract_token(scanner_res)

            elif top_of_stack in TERMINAL:
                print('DID NOT MATCH!')

                self.recover_error(err_type=3, lineno=self.scanner.lineno, top_of_stack=top_of_stack)
                continue

    def recover_error(self, err_type: int, lineno, current_token=None, top_of_stack=None):
        if err_type == 1:
            if current_token == '$':
                self.syntax_error += '#' + str(lineno + 1) + ' : syntax error, Unexpected EOF' + '\n'
            else:
                self.syntax_error += '#' + str(lineno + 1) + ' : syntax error, illegal ' + current_token + '\n'
        if err_type == 2:
            self.syntax_error += '#' + str(lineno + 1) + ' : syntax error, missing ' + top_of_stack + '\n'
        if err_type == 3:
            self.syntax_error += '#' + str(lineno + 1) + ' : syntax error, missing ' + top_of_stack + '\n'
