import sys

from Scanner.symbol_table import SymbolTable
import os
from Scanner import enums


class FileHandler:
    def __init__(self, file_name):
        self.input_file = open(os.path.join(sys.path[0], file_name), "r")
        self.tokenized = ''
        self.lexical_errors = ''
        self.symbol_table = SymbolTable()

    def read_input_file(self):
        return self.input_file.readlines()

    def write_token_file(self):
        f = open(os.path.join(sys.path[0], 'tokens.txt'), "w")
        f.write(self.tokenized)
        f.close()

    def write_symbol_table_file(self):
        f = open(os.path.join(sys.path[0], 'symbol_table.txt'), "w")
        f.write(self.symbol_table.get_elements())
        f.close()

    def write_lexical_errors(self):
        f = open(os.path.join(sys.path[0], 'lexical_errors.txt'), "w")
        if self.lexical_errors == '':
            self.lexical_errors = enums.ErrorType.NO_ERROR.value
        f.write(self.lexical_errors)
        f.close()

    def write_files(self):
        self.write_token_file()
        self.write_symbol_table_file()
        self.write_lexical_errors()
