from enums import *


class MemoryManager:

    def __init__(self):
        self.virtual_mem = {i: '' for i in range(0, 2000, 4)}
        self.code_block_inx = CODE_BLOCK_START_INX
        self.static_data_inx = STATIC_DATA_START_INX
        self.runtime_stack_inx = RUNTIME_STACK_START_INX
        self.top_sp = 0
        self.top = 0
        