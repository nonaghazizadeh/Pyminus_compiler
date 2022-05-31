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
        self.temp_inx = enums.REGISTER_START_INX

        # save top and top_sp in static data
        self.top_sp_addr = self.static_data_inx
        self.top_addr = self.static_data_inx + 4
        self.static_data_inx += 8
        self.virtual_mem[0] = f'(ASSIGN, #{self.runtime_stack_inx}, {self.top_sp_addr}, )'
        self.virtual_mem[4] = f'(ASSIGN, #{self.runtime_stack_inx}, {self.top_addr}, )'

    def return_code_block(self):
        cb = dict(filter(lambda x: x[1] != '' and x[0] < enums.STATIC_DATA_START_INX, self.virtual_mem.items()))
        return '\n'.join([f'{int(i / 4)}\t{cb[i]}' for i in sorted(cb)])

    def write(self, inst, addr1='', addr2='', addr3='', on_pc=None):
        if on_pc is None:
            self.virtual_mem[self.code_block_inx] = f'({inst.upper()}, {addr1}, {addr2}, {addr3})'
            self.inc_code_block_inx()
        else:
            self.virtual_mem[on_pc] = f'({inst.upper()}, {addr1}, {addr2}, {addr3})'

    def inc_code_block_inx(self):
        self.code_block_inx += 4

    def find_addr(self, dis):  # dis: displacement
        dis *= 4
        t = self.get_temp()
        self.write('add', self.top_sp_addr, f'#{dis}', t)
        return f'@{t}'

    def get_temp(self):     # get addr of new temp
        t = self.temp_inx
        self.write('assign', self.top_addr, t)
        self.write('add', self.top_addr, '#4', self.top_addr)
        self.temp_inx += 4
        return t

    def get_pc(self):
        return int(self.code_block_inx / 4)
