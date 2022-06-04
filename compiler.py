"""
Shayan Mohammadizadeh 98102273
Nona Ghazizadeh 98171007
"""

# from Parser.parser import Parser
#
# parser = Parser()
# parser.parse()
#
# with open('output.txt', 'w') as f:
#     output = parser.inter_code_gen.mem_manager.return_code_block()
#     f.write(output)


# from anytree import RenderTree

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

from Scanner.new_version_scanner import Scanner

scanner = Scanner('input.txt')
x = scanner.get_next_token()
while x != '$':
    print(x)
    print(scanner.symbol_table)
    print()
    x = scanner.get_next_token()

