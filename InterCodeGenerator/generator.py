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
            self.push_returned_value()
        elif action_symbol == 'power':
            self.power()
        elif action_symbol in ['add', 'sub', 'mult']:
            self.add_mul_sub(action_symbol)
        elif action_symbol == 'push_relop':
            self.push_relop(param)
        elif action_symbol == 'compare':
            self.compare()
        elif action_symbol == 'save_pc':
            self.save_pc()
        elif action_symbol == 'if':
            self.fill_if()
        elif action_symbol == 'if_save':
            self.fill_if_and_save()
        elif action_symbol == 'else':
            self.fill_else()
        else:
            print('ACTION SYMBOL NOT FOUND')

    # Action Routines

    def update_method(self, name: str):
        addr = self.mem_manager.get_pc()
        if name == 'main':
            self.mem_manager.virtual_mem[8] = f'(JP, {addr}, , )'
            return
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
        num = self.semantic_stack.pop(-2) + 1
        self.semantic_stack.append(num)

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
        self.mem_manager.write('assign', f'#{self.mem_manager.get_pc() + 2}', f'@{t}')

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

    def power(self):
        t1, t2 = [f'@{self.mem_manager.get_temp()}' for _ in range(2)]
        self.mem_manager.write('assign', '#1', t1)
        self.mem_manager.write('assign', self.semantic_stack.pop(), t2)
        pc = self.mem_manager.get_pc()

        self.mem_manager.write('jpf', t2, self.mem_manager.get_pc() + 4)
        self.mem_manager.write('mult', t1, self.semantic_stack.pop(), t1)
        self.mem_manager.write('sub', t2, '#1', t2)
        self.mem_manager.write('jp', pc)

        self.semantic_stack.append(t1)

    def add_mul_sub(self, op: str):
        t = f'@{self.mem_manager.get_temp()}'
        self.mem_manager.write(op, self.semantic_stack.pop(-2), self.semantic_stack.pop(), t)
        self.semantic_stack.append(t)

    def push_relop(self, param):
        self.semantic_stack.append(param)

    def compare(self):
        t = f'@{self.mem_manager.get_temp()}'
        relop = self.semantic_stack.pop(-2)
        inst = 'lt' if relop == '<' else 'eq'
        self.mem_manager.write(inst, self.semantic_stack.pop(-2), self.semantic_stack.pop(), t)
        self.semantic_stack.append(t)

    def save_pc(self):
        self.semantic_stack.append(self.mem_manager.code_block_inx)
        self.mem_manager.inc_code_block_inx()

    def fill_if(self):
        saved_pc = self.semantic_stack.pop()
        self.mem_manager.write('jpf', self.semantic_stack.pop(), self.mem_manager.get_pc(), on_pc=saved_pc)

    def fill_if_and_save(self):
        self.save_pc()
        saved_pc = self.semantic_stack.pop(-2)
        self.mem_manager.write('jpf', self.semantic_stack.pop(-2), self.mem_manager.get_pc(), on_pc=saved_pc)

    def fill_else(self):
        saved_pc = self.semantic_stack.pop()
        self.mem_manager.write('jp', self.mem_manager.get_pc(), on_pc=saved_pc)
