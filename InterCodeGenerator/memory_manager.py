from InterCodeGenerator import enums


class MemoryManager:

    def __init__(self, size):
        """"
        AR architecture:
        - returned value
        - PC
        - top_sp
        - params
        - local data
        - temp
        """
        self.virtual_mem = {i: '' for i in range(0, size)}
        self.code_block_inx = enums.CODE_BLOCK_START_INX  # PC
        self.__static_data_inx = enums.STATIC_DATA_START_INX
        self.__runtime_stack_inx = enums.RUNTIME_STACK_START_INX
        self.__free_inx = enums.FREE_START_INX
        self.array_inx = enums.ARRAY_START_INX
        self.dis = 0
        self.ids = []
        self.main_addr = None
        self.break_f = []
        self.continue_addr = []

        # save top and top_sp in static data
        self.top_sp_addr = self.__static_data_inx
        self.__static_data_inx += 4
        self.write('assign', f'#{self.__runtime_stack_inx}', f'{self.top_sp_addr}')

    def return_code_block(self):
        cb = dict(filter(lambda x: x[1] != '' and x[0] < enums.STATIC_DATA_START_INX, self.virtual_mem.items()))
        return '\n'.join([f'{int(i / 4)}\t{cb[i]}' for i in sorted(cb)])

    def write(self, inst, addr1='', addr2='', addr3=''):
        self.virtual_mem[self.code_block_inx] = f'({inst.upper()}, {addr1}, {addr2}, {addr3})'
        self.code_block_inx += 4

    def get_pc(self):
        return int(self.code_block_inx / 4)

    def get_free(self):  # get next free address -> 3000, 3008, 3096, ...
        f = self.__free_inx
        self.__free_inx += 4
        return f

    def get_temp(self):
        dis = self.dis
        self.dis += 1
        f = self.get_free()
        self.write('add', self.top_sp_addr, f'#{dis * 4}', f)
        return f'@{f}', f'%{dis}'

    def get_absolute(self, base: str, dis: int):  # dis: displacement
        dis *= 4
        if base == 'top_sp':
            f = self.get_free()
            self.write('add', self.top_sp_addr, f'#{dis}', f)
            return f'@{f}'
        elif base == 'static':
            return f'{self.__static_data_inx + dis}'
