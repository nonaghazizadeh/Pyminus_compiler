from InterCodeGenerator import enums


class MemoryManager:

    def __init__(self, size):
        """"
        AR architecture:
        - returned value
        - PC
        - top_sp
        - top
        - params
        - local data
        - temp
        """
        self.virtual_mem = {i: '' for i in range(0, size)}
        self.code_block_inx = enums.CODE_BLOCK_START_INX + 12  # PC
        self.static_data_inx = enums.STATIC_DATA_START_INX
        self.runtime_stack_inx = enums.RUNTIME_STACK_START_INX
        self.free_inx = enums.FREE_START_INX
        self.temp_dis = 0
        self.ids = []

        # save top and top_sp in static data
        self.top_sp_addr = self.static_data_inx
        self.top_addr = self.static_data_inx + 4
        self.static_data_inx += 8
        self.virtual_mem[0] = f'(ASSIGN, #{self.runtime_stack_inx}, {self.top_sp_addr}, )'
        self.virtual_mem[4] = f'(ASSIGN, #{self.runtime_stack_inx}, {self.top_addr}, )'

    def return_code_block(self):
        cb = dict(filter(lambda x: x[1] != '' and x[0] < enums.STATIC_DATA_START_INX, self.virtual_mem.items()))
        return '\n'.join([f'{int(i / 4)}\t{cb[i]}' for i in sorted(cb)])

    def write(self, inst, addr1='', addr2='', addr3=''):
        self.virtual_mem[self.code_block_inx] = f'({inst.upper()}, {addr1}, {addr2}, {addr3})'
        self.code_block_inx += 4

    def get_pc(self):
        return int(self.code_block_inx / 4)

    def get_free(self):     # get next free address -> 3000, 3008, 3096, ...
        f = self.free_inx
        self.free_inx += 4
        return f

    def get_absolute(self, dis):        # dis: displacement
        dis *= 4
        f = self.get_free()
        self.write('add', self.top_sp_addr, f'#{dis}', f)
        return f'@{f}'

    def get_temp(self):
        dis = self.temp_dis
        self.temp_dis += 1
        f = self.get_free()
        self.write('add', self.top_sp_addr, f'#{dis * 4}', f)
        self.inc_top()
        return f'@{f}', f'%{dis}'

    def inc_top(self):
        self.write('add', self.top_addr, '#4', self.top_addr)
