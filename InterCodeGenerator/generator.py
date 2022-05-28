from InterCodeGenerator import enums


class InterCodeGen:

    def __init__(self, scanner):
        self.semantic_stack = []
        self.scanner = scanner

        # memory manager
        self.virtual_mem = {i: '' for i in range(0, 2000, 4)}
        self.code_block_inx = enums.CODE_BLOCK_START_INX
        self.static_data_inx = enums.STATIC_DATA_START_INX
        self.runtime_stack_inx = enums.RUNTIME_STACK_START_INX
        self.top_sp = 0
        self.top = 0

    def generate(self, action_symbol, method_name: str = ''):
        action_symbol = action_symbol[1:]   # delete first hashtag
        if action_symbol == 'update_method_addr':
            self.update_method_addr(method_name)
        else:
            print('ACTION SYMBOL NOT FOUND')

    def update_method_addr(self, name: str):
        self.scanner.symbol_table[name] = self.code_block_inx
