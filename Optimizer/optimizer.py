class Optimizer:

    def __init__(self):
        self.code = []
        self.optimized_code = []
        self.const = dict()

        self.__read_file()

    def __read_file(self):
        with open('output.txt', 'r') as f:
            lines = f.read().replace(' ', '').split('\n')

        for line in lines:
            self.code.append(line[line.find('(') + 1: line.find(')')].split(','))

    def get_value(self, x: str):
        if x[0] == '#':
            return int(x[1:])
        elif x.isdigit():
            return self.const[x]
        elif x[0] == '@':
            return self.const[f'{self.const[x[1:]]}']

    def get_key(self, x: str):
        if x[0] == '@':
            return f'{self.const[x[1:]]}'
        elif x.isdigit():
            return x

    def optimize(self):
        i = 0
        while i != len(self.code):
            print(i)
            code = self.code[i]

            if code[0] == 'ASSIGN':
                self.const[self.get_key(code[2])] = self.get_value(code[1])

            if code[0] == 'PRINT':
                self.optimized_code.append(f'{len(self.optimized_code)}\t(PRINT, #{self.get_value(code[1])}, , )')

            if code[0] in ('ADD', 'MULT', 'SUB', 'EQ', 'LT'):
                a = self.get_value(code[1])
                b = self.get_value(code[2])

                self.const[self.get_key(code[3])] = {
                    'ADD': a + b,
                    'MULT': a * b,
                    'SUB': a - b,
                    'EQ': 1 if a == b else 0,
                    'LT': 1 if a < b else 0
                }.get(code[0])

            if code[0] == 'JP':
                if code[1].isdigit():  # direct jump
                    i = int(code[1])
                else:  # indirect jump
                    i = self.const[code[1][1:]]
            elif code[0] == 'JPF':
                if self.get_value(code[1]) == 0:
                    if code[2].isdigit():  # direct jump
                        i = int(code[2])
                    else:  # indirect jump
                        i = self.const[code[2][1:]]
                else:
                    i += 1
            else:
                i += 1

    def save_optimized_code(self):
        with open('optimized_output.txt', 'w') as f:
            f.write('\n'.join(self.optimized_code))
