from InterCodeGenerator.memory_manager import MemoryManager
from InterCodeGenerator import enums


class InterCodeGen:

    def __init__(self, scanner):
        self.semantic_stack = []
        self.scanner = scanner
        self.mem_manager = MemoryManager(size=enums.MEMORY_SIZE, step=enums.STEP)

    def generate(self, action_symbol, param):
        action_symbol = action_symbol[1:]  # delete first hashtag
        if action_symbol == 'update_method_addr':
            self.update_method_addr(param)
        elif action_symbol == 'push_id':
            self.push_id(param)
        elif action_symbol == 'push_num':
            self.push_num(param)
        elif action_symbol == 'assign':
            self.assign()
        else:
            print('ACTION SYMBOL NOT FOUND')

    # Action Routines
    def update_method_addr(self, name: str):
        self.scanner.symbol_table[name] = self.mem_manager.code_block_inx

    def push_id(self, name: str):
        self.semantic_stack.append(self.mem_manager.find_addr(self.scanner.symbol_table[name]))

    def push_num(self, num: str):
        self.semantic_stack.append('#' + num)

    def assign(self):
        self.mem_manager.write('assign', self.semantic_stack.pop(), self.semantic_stack.pop())

