from InterCodeGenerator.memory_manager import MemoryManager
from InterCodeGenerator import enums


class InterCodeGen:

    def __init__(self, scanner):
        self.semantic_stack = []
        self.scanner = scanner
        self.mem_manager = MemoryManager(size=enums.MEMORY_SIZE)

    def generate(self, action_symbol, param):
        # print('*******************************')
        # print(action_symbol.upper())
        # print(f'before: {self.semantic_stack}')

        action_symbol = action_symbol[1:]  # delete first hashtag
        if action_symbol == 'update_method':
            self.update_method(param)
        elif action_symbol == 'push_id':
            self.push_id(param)
        elif action_symbol == 'push_num':
            self.push_num(param)
        elif action_symbol == 'assign_value':
            self.assign_value()
        elif action_symbol == 'print':
            self.print()
        elif action_symbol == 'add_param':
            self.add_param()
        elif action_symbol == 'call_func':
            self.call_func()
        elif action_symbol == 'return_value':
            self.return_value(True)
        elif action_symbol == 'return':
            self.return_value(False)
        elif action_symbol == 'power':
            self.power()
        elif action_symbol in ['add', 'sub', 'mult']:
            self.add_mul_sub(action_symbol)
        elif action_symbol == 'push_relop':
            self.push_relop(param)
        elif action_symbol == 'compare':
            self.compare()
        elif action_symbol == 'save':
            self.save_pc(True)
        elif action_symbol == 'save_while':
            self.fill_save_while()
        elif action_symbol == 'if':
            self.fill_if()
        elif action_symbol == 'if_save':
            self.fill_if_and_save()
        elif action_symbol == 'else':
            self.fill_else()
        elif action_symbol == 'label':
            self.label()
        elif action_symbol == 'while':
            self.fill_while_jp()
        elif action_symbol == 'break':
            self.fill_break()
        elif action_symbol == 'continue':
            self.fill_continue()
        elif action_symbol == 'saw_id':
            self.add_id(param)
        elif action_symbol == 'push_returned_value':
            self.push_returned_value()
        elif action_symbol == 'assign_array':
            self.assign_array()
        elif action_symbol == 'add_element':
            self.add_element()
        elif action_symbol == 'push_element':
            self.push_element()
        else:
            print('ACTION SYMBOL NOT FOUND')

        # print(f'after: {self.semantic_stack}')

    def pop_semantic_stack(self, inx: int = -1):
        x = self.semantic_stack.pop(inx)
        if type(x) == str:
            if x[0] == '%':     # top_addr relative
                return self.mem_manager.get_absolute(base='top_sp', dis=int(x[1:]))
            elif x[0] == '^':       # static data relative
                return self.mem_manager.get_absolute(base='static', dis=int(x[1:]))
            elif x[0] == '*':       # array
                self.semantic_stack.extend(x[1:].split('|'))
                t, _ = self.mem_manager.get_temp()
                self.mem_manager.write('mult', self.pop_semantic_stack(), '#4', t)
                f = self.mem_manager.get_free()
                self.mem_manager.write('add', t, self.pop_semantic_stack(), f)
                return f'@{f}'
            else:
                return x    # num
        else:   # params, ...
            return x

    # Action Routines
    def update_method(self, name: str):
        self.mem_manager.dis = 0  # reset temp displacement
        self.mem_manager.ids = []  # empty saw ids list

        if self.mem_manager.main_addr is None:
            self.mem_manager.main_addr = self.mem_manager.code_block_inx
            self.mem_manager.code_block_inx += 4

        addr = self.mem_manager.get_pc()
        if name == 'main':
            self.mem_manager.virtual_mem[self.mem_manager.main_addr] = f'(JP, {addr}, , )'

        self.scanner.symbol_table['global'][name] = f'{addr}'

    def push_id(self, name: str):
        local_data = self.scanner.symbol_table['local']
        global_data = self.scanner.symbol_table['global']

        # simple assignment
        if local_data.get(name) is not None:
            # name is local var
            self.semantic_stack.append(f'%{local_data[name]}')
            if name not in self.mem_manager.ids:
                self.add_id(name)
        else:
            if type(global_data[name]) == str:
                # name is function -> function call
                self.semantic_stack.append(int(global_data[name]))
                self.semantic_stack.append(0)  # params number
            else:
                # name is global var
                self.semantic_stack.append(f'^{global_data[name]}')

    def push_num(self, num: str):
        self.semantic_stack.append('#' + num)

    def assign_value(self):
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

    def return_value(self, has_value: bool):
        # if func is main
        if 'main' in self.scanner.symbol_table['global'].keys():
            return

        t = self.mem_manager.get_free()
        self.mem_manager.write('assign', self.mem_manager.top_sp_addr, t)

        # save returned value
        self.mem_manager.write('sub', t, '#12', t)
        if has_value:
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
        self.semantic_stack.append(self.mem_manager.code_block_inx)
        self.mem_manager.write('')
        self.mem_manager.continue_addr.append(self.mem_manager.get_pc())

    def fill_while_jp(self):
        self.mem_manager.write('jp', self.mem_manager.continue_addr.pop())

        code_inx = self.mem_manager.code_block_inx  # store
        self.mem_manager.code_block_inx = self.pop_semantic_stack()
        self.mem_manager.write('assign', f'#{int(code_inx / 4)}', self.mem_manager.break_f.pop())
        self.mem_manager.code_block_inx = code_inx  # restore

    def fill_continue(self):
        self.mem_manager.write('jp', self.mem_manager.continue_addr[-1])

    def fill_save_while(self):
        f = self.mem_manager.get_free()
        self.mem_manager.write('jpf', self.pop_semantic_stack(), f'@{f}')
        self.mem_manager.break_f.append(f)

    def fill_break(self):
        self.mem_manager.write('jp', f'@{self.mem_manager.break_f[-1]}')

    def add_id(self, name: str):
        self.mem_manager.ids.append(name)
        self.mem_manager.dis += 1

    def assign_array(self):
        self.mem_manager.write('assign', f'#{self.mem_manager.array_inx}', self.pop_semantic_stack())

    def add_element(self):
        self.mem_manager.write('assign', self.pop_semantic_stack(), self.mem_manager.array_inx)
        self.mem_manager.array_inx += 4

    def push_element(self):
        self.semantic_stack.append(f'*{self.semantic_stack.pop(-2)}|{self.semantic_stack.pop()}')

