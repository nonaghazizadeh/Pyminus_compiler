"""
Shayan Mohammadizadh 98102273
Nona Ghazizadeh 98171007
"""


from Parser.parser import Parser
from Scanner.new_version_scanner import Scanner

scanner = Scanner('input.txt')
print(scanner.get_next_token())
print(scanner.tokens)
parser = Parser()
parser.create_table()
parser.add_synch()
# print(parser.table['Relop'])