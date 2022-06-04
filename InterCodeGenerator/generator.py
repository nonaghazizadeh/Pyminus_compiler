from InterCodeGenerator.memory_manager import MemoryManager
from InterCodeGenerator import enums


class InterCodeGen:

    def __init__(self, scanner):
        self.semantic_stack = []
        self.scanner = scanner
        self.mem_manager = MemoryManager(size=enums.MEMORY_SIZE)

    def generate(self, action_symbol, param):
        print('*******************************')
        print(action_symbol.upper())
        print(f'before: {self.semantic_stack}')

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
        elif action_symbol == 'power':
            self.power()
        elif action_symbol in ['add', 'sub', 'mult']:
            self.add_mul_sub(action_symbol)
        elif action_symbol == 'push_relop':
            self.push_relop(param)
        elif action_symbol == 'compare':
            self.compare()
        elif action_symbol == 'save_cond':
            self.save_pc(True)
        elif action_symbol == 'save_uncond':
            self.save_pc(False)
        elif action_symbol == 'if':
            self.fill_if()
        elif action_symbol == 'if_save':
            self.fill_if_and_save()
        elif action_symbol == 'else':
            self.fill_else()
        elif action_symbol == 'label':
            self.label()
        elif action_symbol == 'while':
            self.fill_while()
        elif action_symbol == 'saw_id':
            self.add_id(param)
        elif action_symbol == 'push_returned_value':
            self.push_returned_value()
        else:
            print('ACTION SYMBOL NOT FOUND')

        print(f'after: {self.semantic_stack}')

    def pop_semantic_stack(self, inx: int = -1):
        x = self.semantic_stack.pop(inx)
        if type(x) == str:
            if x[0] == '%':
                return self.mem_manager.get_absolute(int(x[1:]))
            else:
                return x
        else:
            return x

    # Action Routines
    def update_method(self, name: str):
        addr = self.mem_manager.get_pc()
        self.mem_manager.dis = 0  # reset temp displacement
        self.mem_manager.ids = []  # empty saw ids list
        if name == 'main':
            self.mem_manager.virtual_mem[4] = f'(JP, {addr}, , )'
            return
        self.scanner.symbol_table[name] = {
            'type': 'method',
            'addr': addr
        }

    def push_id(self, name: str):
        symbol_table = self.scanner.symbol_table
        if type(symbol_table[name]) == dict:
            # function call
            self.semantic_stack.append(symbol_table[name]['addr'])
            self.semantic_stack.append(0)  # params number
        elif type(symbol_table[name]) == int:
            # simple assignment
            self.semantic_stack.append(f'%{symbol_table[name]}')
            if name not in self.mem_manager.ids:
                self.add_id(name)
        else:
            print('ERROR WHILE PUSHING ID')

    def push_num(self, num: str):
        self.semantic_stack.append('#' + num)

    def assign(self):
        self.mem_manager.write('assign', self.pop_semantic_stack(), self.pop_semantic_stack())

    def print(self):
        self.mem_manager.write('print', self.pop_semantic_stack())

    def add_param(self):  # add param to semantic stack
        num = self.pop_semantic_stack(-2) + 1
        self.semantic_stack.append(num)

    def call_func(self):
        param_num = self.pop_semantic_stack()
        t = self.mem_manager.get_free()

        # update top_addr
        self.mem_manager.write('add', self.mem_manager.top_sp_addr, f'#{self.mem_manager.dis * 4}', t)

        # set params
        self.mem_manager.write('add', t, '#12', t)
        for i in range(-param_num, 0, 1):
            self.mem_manager.write('assign', self.pop_semantic_stack(i), f'@{t}')
            self.mem_manager.write('add', t, '#4', t)

        # set TOP_SP
        self.mem_manager.write('sub', t, f'#{(param_num + 1) * 4}', t)
        self.mem_manager.write('assign', self.mem_manager.top_sp_addr, f'@{t}')

        # update TOP_SP
        self.mem_manager.write('add', t, '#4', t)
        self.mem_manager.write('assign', t, self.mem_manager.top_sp_addr)

        # set PC
        self.mem_manager.write('sub', t, '#8', t)
        self.mem_manager.write('assign', f'#{self.mem_manager.get_pc() + 2}', f'@{t}')

        # write jump
        self.mem_manager.write('jp', self.pop_semantic_stack())

    def push_returned_value(self):
        self.semantic_stack.append(f'%{self.mem_manager.dis}')
        self.mem_manager.dis += 1

    def return_value(self):
        t = self.mem_manager.get_free()
        self.mem_manager.write('assign', self.mem_manager.top_sp_addr, t)

        # save returned value
        self.mem_manager.write('sub', t, '#12', t)
        self.mem_manager.write('assign', self.pop_semantic_stack(), f'@{t}')

        # restore TOP_SP
        self.mem_manager.write('add', t, '#8', t)
        self.mem_manager.write('assign', f'@{t}', self.mem_manager.top_sp_addr)

        # restore PC
        self.mem_manager.write('sub', t, '#4', t)
        self.mem_manager.write('assign', f'@{t}', t)
        self.mem_manager.write('jp', f'@{t}')

    def power(self):
        t1, dis1 = self.mem_manager.get_temp()
        t2, _ = self.mem_manager.get_temp()
        self.mem_manager.write('assign', '#1', t1)
        self.mem_manager.write('assign', self.pop_semantic_stack(), t2)
        pc = self.mem_manager.get_pc()

        self.mem_manager.write('jpf', t2, self.mem_manager.get_pc() + 5)
        self.mem_manager.write('mult', t1, self.pop_semantic_stack(), t1)
        self.mem_manager.write('sub', t2, '#1', t2)
        self.mem_manager.write('jp', pc)

        self.semantic_stack.append(dis1)

    def add_mul_sub(self, op: str):
        t, dis = self.mem_manager.get_temp()
        self.mem_manager.write(op, self.pop_semantic_stack(-2), self.pop_semantic_stack(), t)
        self.semantic_stack.append(dis)

    def push_relop(self, param):
        self.semantic_stack.append(param)

    def compare(self):
        t, dis = self.mem_manager.get_temp()
        relop = self.pop_semantic_stack(-2)
        inst = 'lt' if relop == '<' else 'eq'
        self.mem_manager.write(inst, self.pop_semantic_stack(-2), self.pop_semantic_stack(), t)
        self.semantic_stack.append(dis)

    def save_pc(self, cond):
        self.semantic_stack.append(self.mem_manager.code_block_inx)
        self.mem_manager.write('')

        if cond:
            self.mem_manager.write('')

    def fill_if(self):
        code_inx = self.mem_manager.code_block_inx  # store
        self.mem_manager.code_block_inx = self.pop_semantic_stack()
        self.mem_manager.write('jpf', self.pop_semantic_stack(), int(code_inx / 4))
        self.mem_manager.code_block_inx = code_inx  # restore

    def fill_if_and_save(self):
        self.save_pc(False)
        code_inx = self.mem_manager.code_block_inx
        self.mem_manager.code_block_inx = self.pop_semantic_stack(-2)
        self.mem_manager.write('jpf', self.pop_semantic_stack(-2), int(code_inx / 4))
        self.mem_manager.code_block_inx = code_inx

    def fill_else(self):
        code_inx = self.mem_manager.code_block_inx
        self.mem_manager.code_block_inx = self.pop_semantic_stack()
        self.mem_manager.write('jp', int(code_inx / 4))
        self.mem_manager.code_block_inx = code_inx

    def label(self):
        self.semantic_stack.append(self.mem_manager.get_pc())

    def fill_while(self):
        self.mem_manager.write('jp', self.pop_semantic_stack(-3))
        code_inx = self.mem_manager.code_block_inx
        self.mem_manager.code_block_inx = self.pop_semantic_stack()
        self.mem_manager.write('jpf', self.pop_semantic_stack(), int(code_inx / 4))
        self.mem_manager.code_block_inx = code_inx

    def add_id(self, name: str):
        self.mem_manager.ids.append(name)
        self.mem_manager.dis += 1
