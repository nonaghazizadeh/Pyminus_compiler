from InterCodeGenerator import enums


class MemoryManager:

    def __init__(self, size, step):
        """"
        AR architecture:
        - returned value
        - SMS -> pc, top_sp, top
        - params + local data
        - temp
        """
        self.virtual_mem = {i: '' for i in range(0, size, step)}
        self.code_block_inx = enums.CODE_BLOCK_START_INX
        self.static_data_inx = enums.STATIC_DATA_START_INX
        self.runtime_stack_inx = enums.RUNTIME_STACK_START_INX
        self.top_sp = enums.RUNTIME_STACK_START_INX
        self.top = enums.RUNTIME_STACK_START_INX
        self.step = step

    def take_pic(self):
        non_empty_cells = dict(filter(lambda x: x[1] != '', self.virtual_mem.items()))

        code_block, static_data, runtime_stack = [], [], []
        for k in sorted(non_empty_cells):
            to_show = f'{k}\t{non_empty_cells[k]}'
            if k < enums.STATIC_DATA_START_INX:
                code_block.append(to_show)
            elif k < enums.RUNTIME_STACK_START_INX:
                static_data.append(to_show)
            else:
                runtime_stack.append(to_show)

        for v1, v2 in zip(['CODE BLOCK', 'STATIC DATA', 'RUNTIME STACK'], [code_block, static_data, runtime_stack]):
            print(f'*********** {v1} ***********')
            print('\n'.join(v2))
            print()

    def write(self, inst: str, addr1: str = '', addr2: str = '', addr3: str = ''):
        self.virtual_mem[self.code_block_inx] = f'({inst.upper()}, {addr1}, {addr2}, {addr3})'
        self.code_block_inx += self.step

    def find_addr(self, dis):   # dis: displacement
        dis *= self.step
        if self.virtual_mem[self.top_sp + dis] == '':
            self.virtual_mem[self.top_sp + dis] = '0'
            self.top += self.step

        return self.top_sp + dis
