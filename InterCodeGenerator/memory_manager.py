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

    # def take_pic(self):
    #     non_empty_cells = dict(filter(lambda x: x[1] != '', self.virtual_mem.items()))
    #
    #     code_block, static_data, runtime_stack = [], [], []
    #     for k in sorted(non_empty_cells):
    #         to_show = f'{k}\t{non_empty_cells[k]}'
    #         if k < enums.STATIC_DATA_START_INX:
    #             code_block.append(to_show)
    #         elif k < enums.RUNTIME_STACK_START_INX:
    #             static_data.append(to_show)
    #         else:
    #             runtime_stack.append(to_show)
    #
    #     for v1, v2 in zip(['CODE BLOCK', 'STATIC DATA', 'RUNTIME STACK'], [code_block, static_data, runtime_stack]):
    #         print(f'*********** {v1} ***********')
    #         print('\n'.join(v2))
    #         print()
    #
    #

    def write(self, inst, addr1='', addr2='', addr3=''):
        self.virtual_mem[self.code_block_inx] = f'({inst.upper()}, {addr1}, {addr2}, {addr3})'
        self.code_block_inx += 4

    def find_addr(self, dis):  # dis: displacement
        dis *= 4
        t = self.get_temp()
        self.write('add', self.top_sp_addr, f'#{dis}', t)
        return f'@{t}'

    def get_temp(self):
        t = self.temp_inx
        self.write('assign', self.top_addr, t)
        self.write('add', self.top_addr, '#4', self.top_addr)
        self.temp_inx += 4
        return t

    def convert_to_pc(self):
        return int(self.code_block_inx / 4)
