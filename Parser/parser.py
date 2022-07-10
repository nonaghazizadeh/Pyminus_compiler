from Parser.enums import FOLLOW, TERMINAL, NON_TERMINAL, GRAMMAR
from Parser.helper import get_first, extract_token

from Scanner.new_version_scanner import Scanner
from InterCodeGenerator.generator import InterCodeGen
from SemanticAnalyzer.analyzer import SemanticAnalyzer

from anytree import Node


class Parser:
    def __init__(self):
        self.table = {fi: {} for fi in NON_TERMINAL}
        self.root = Node('Program')
        self.stack = [Node('$', self.root), self.root]
        self.syntax_error = ''
        self.scanner = Scanner('input.txt')
        self.create_table()
        self.add_synch()

        # Added For ICG
        self.inter_code_gen = InterCodeGen(self.scanner)

        # Added for Semantic Analyzer
        self.semantic_analyzer = SemanticAnalyzer()

    def create_table(self):
        for A, v in GRAMMAR.items():
            for alpha in v:
                firsts = get_first(alpha)
                for t in firsts:
                    if t != 'EPSILON':
                        self.table[A][t] = alpha

                if 'EPSILON' in firsts:
                    for t in FOLLOW[A]:
                        self.table[A][t] = alpha

    def add_synch(self):
        for nt in FOLLOW:
            for fo in FOLLOW[nt]:
                if fo not in self.table[nt]:
                    self.table[nt][fo] = 'synch'

    def parse(self):
        scanner_res = self.scanner.get_next_token()
        current_token = extract_token(scanner_res)
        while True:
            # print(''.join(['-' for _ in range(50)]))
            # print(f'STACK: {[i.name for i in self.stack]}')
            # print(f'CURRENT_TOKEN: {current_token}')

            top_of_stack = self.stack.pop()

            # Added for Semantic Analyzer
            if top_of_stack.name[0] == '@':
                # turn $ to ($, $) -> analyzer doesn't even use it actually!
                normalize_token = lambda x: (x, x) if type(scanner_res) == str else x
                self.semantic_analyzer.analyze(top_of_stack.name, normalize_token(scanner_res)[1], self.scanner.lineno)
                continue

            # Added for ICG
            if top_of_stack.name[0] == '#':
                if self.semantic_analyzer.is_correct:
                    try:
                        self.inter_code_gen.generate(top_of_stack.name, scanner_res[1])
                    except Exception as e:
                        print(f'Error while generating IC: {e}')
                        self.semantic_analyzer.is_correct = False

                continue

            if current_token == top_of_stack.name == '$':
                # print('ACTION: SUCCESS')
                top_of_stack.parent = None
                top_of_stack.parent = self.root
                return

            if top_of_stack.name in NON_TERMINAL:
                if current_token in self.table[top_of_stack.name]:
                    temp = self.table[top_of_stack.name][current_token]
                    if temp == 'synch':
                        # print('SYNCH ERROR')
                        self.recover_error(err_type=2, lineno=self.scanner.lineno, top_of_stack=top_of_stack.name)
                        top_of_stack.parent = None
                        continue

                    elif temp == 'EPSILON':
                        # print(f'ACTION: EPSILON')
                        Node('epsilon', parent=top_of_stack)

                    else:
                        # print(f'ACTION: {temp}')
                        self.stack.extend([Node(name, parent=top_of_stack) for name in temp.split(' ')][::-1])

                else:
                    # print('EMPTY ERROR')
                    self.recover_error(err_type=1, lineno=self.scanner.lineno, current_token=current_token)
                    if current_token == '$':
                        top_of_stack.parent = None
                        for i in self.stack:
                            i.parent = None
                        return

                    scanner_res = self.scanner.get_next_token()
                    current_token = extract_token(scanner_res)
                    self.stack.append(top_of_stack)
                    continue

            if current_token == top_of_stack.name:
                # print('ACTION: TERMINAL')
                token_type = scanner_res[0] if scanner_res[0] != 'NUMBER' else 'NUM'
                token_id = scanner_res[1]
                top_of_stack.name = '(' + token_type + ', ' + token_id + ')'
                scanner_res = self.scanner.get_next_token()
                current_token = extract_token(scanner_res)

            elif top_of_stack.name in TERMINAL:
                # print('DID NOT MATCH!')

                self.recover_error(err_type=3, lineno=self.scanner.lineno, top_of_stack=top_of_stack.name)
                top_of_stack.parent = None
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
