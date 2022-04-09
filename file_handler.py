from symbol_table import SymbolTable


class FileHandler:
    def __init__(self, file_name):
        self.input_file = open(file_name, "r")
        self.tokenized = ''
        self.symbol_table = SymbolTable()

    def read_input_file(self):
        return self.input_file.readlines()

    def write_token_file(self):
        f = open("tokens.txt", "w")
        f.write(self.tokenized)
        f.close()

    def write_symbol_table_file(self):
        f = open("symbol_table.txt", "w")
        f.write(self.symbol_table.get_elements())
        f.close()

    def write_files(self):
        self.write_token_file()
        self.write_symbol_table_file()
