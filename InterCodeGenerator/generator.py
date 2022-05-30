from InterCodeGenerator.memory_manager import MemoryManager
from InterCodeGenerator import enums


class InterCodeGen:

    def __init__(self, scanner):
        self.semantic_stack = []
        self.scanner = scanner
        self.mem_manager = MemoryManager(size=enums.MEMORY_SIZE)

    def generate(self, action_symbol, param):
        action_symbol = action_symbol[1:]  # delete first hashtag
        if action_symbol == 'update_method':
            self.update_method(param)
        elif action_symbol == 'push_id':
            self.push_id(param)
        elif action_symbol == 'push_num':
            self.push_num(param)
        elif action_symbol == 'assign':
            self.assign()
        elif action_symbol == 'print':
            self.print()
        elif action_symbol == 'add_param':
            self.add_param()
        elif action_symbol == 'call_func':
            self.call_func()
        elif action_symbol == 'return_value':
            self.return_value()
        elif action_symbol == 'push_returned_value':
            print(f'before: {self.semantic_stack}')
            self.push_returned_value()
            print(f'after: {self.semantic_stack}')
        else:
            print('ACTION SYMBOL NOT FOUND')

    # Action Routines

    def update_method(self, name: str):
        addr = self.mem_manager.convert_to_pc()
        if name == 'main':
            self.mem_manager.virtual_mem[8] = f'(JP, {addr}, , )'
            return
        print(f'{name}: {self.mem_manager.code_block_inx}')
        self.scanner.symbol_table[name] = {
            'type': 'method',
            'addr': addr
        }

    def push_id(self, name: str):
        symbol_table = self.scanner.symbol_table
        if name in symbol_table.keys():
            if type(symbol_table[name]) == dict:
                # function call
                self.semantic_stack.append(symbol_table[name]['addr'])
                self.semantic_stack.append(0)   # params number
                pass
            elif type(symbol_table[name]) == int:
                # simple assignment
                self.semantic_stack.append(self.mem_manager.find_addr(self.scanner.symbol_table[name]))
            else:
                print('ERROR WHILE PUSHING ID')

    def push_num(self, num: str):
        self.semantic_stack.append('#' + num)

    def assign(self):
        self.mem_manager.write('assign', self.semantic_stack.pop(), self.semantic_stack.pop())

    def print(self):
        self.mem_manager.write('print', self.semantic_stack.pop())

    def add_param(self):    # add param to semantic stack
        # print(f'before: {self.semantic_stack}')
        num = self.semantic_stack.pop(-2) + 1
        self.semantic_stack.append(num)

        # print(f'after: {self.semantic_stack}')

    def call_func(self):
        param_num = self.semantic_stack.pop()
        t = self.mem_manager.get_temp()

        # set TOP_SP
        self.mem_manager.write('add', self.mem_manager.top_addr, '#8', t)
        self.mem_manager.write('assign', self.mem_manager.top_sp_addr, f'@{t}')

        # set TOP
        self.mem_manager.write('add', t, '#4', t)
        self.mem_manager.write('assign', self.mem_manager.top_addr, f'@{t}')

        # update TOP_SP
        self.mem_manager.write('add', t, '#4', t)
        self.mem_manager.write('assign', t, self.mem_manager.top_sp_addr)

        # set params
        for i in range(-param_num, 0, 1):
            self.mem_manager.write('assign', self.semantic_stack.pop(i), f'@{t}')
            self.mem_manager.write('add', t, '#4', t)

        # update TOP
        self.mem_manager.write('assign', t, self.mem_manager.top_addr)

        # set PC
        self.mem_manager.write('sub', t, f'#{(param_num + 3) * 4}', t)
        self.mem_manager.write('assign', f'#{self.mem_manager.convert_to_pc() + 2}', f'@{t}')

        # write jump
        self.mem_manager.write('jp', self.semantic_stack.pop())

    def return_value(self):
        t = self.mem_manager.get_temp()
        self.mem_manager.write('assign', self.mem_manager.top_sp_addr, t)

        # restore TOP
        self.mem_manager.write('sub', t, '#4', t)
        self.mem_manager.write('assign', f'@{t}', self.mem_manager.top_addr)

        # restore TOP_SP
        self.mem_manager.write('sub', t, '#4', t)
        self.mem_manager.write('assign', f'@{t}', self.mem_manager.top_sp_addr)

        # save returned value
        self.mem_manager.write('assign', self.semantic_stack.pop(), f'@{self.mem_manager.top_addr}')

        # restore PC
        self.mem_manager.write('sub', t, '#4', t)
        self.mem_manager.write('assign', f'@{t}', t)
        self.mem_manager.write('jp', f'@{t}')

    def push_returned_value(self):
        t = self.mem_manager.get_temp()
        self.semantic_stack.append(f'@{t}')