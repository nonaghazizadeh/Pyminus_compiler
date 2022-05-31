"""
Shayan Mohammadizadeh 98102273
Nona Ghazizadeh 98171007
"""


from Parser.parser import Parser
from anytree import RenderTree
from Scanner.new_version_scanner import Scanner
from InterCodeGenerator.memory_manager import MemoryManager
from InterCodeGenerator.generator import InterCodeGen

parser = Parser()
parser.parse()

with open('output.txt', 'w') as f:
    output = parser.inter_code_gen.mem_manager.return_code_block()
    f.write(output)
    # f.write('(PRINT, 500, , )\n(PRINT, 504, , )'.join(output))


# mem_manager = MemoryManager(5000)
# scanner = Scanner('input.txt')
# scanner.symbol_table = {'i': 0, 'j': 1}
# icg = InterCodeGen(scanner)
# icg.push_id('i')
# icg.push_id('j')
# icg.mem_manager.write('print', '@3000')
# icg.mem_manager.write('print', '@3004')
# print(icg.mem_manager.return_code_block())


# output = ''
# for pre, fill, node in RenderTree(parser.root):
#     output += "%s%s" % (pre, node.name) + '\n'
# with open('parse_tree.txt', 'w') as f:
#     f.write(output)
#
#
# with open('syntax_errors.txt', 'w') as f:
#     if parser.syntax_error == '':
#         f.write('There is no syntax error.')
#     else:
#         f.write(parser.syntax_error)

# print('*************************')
