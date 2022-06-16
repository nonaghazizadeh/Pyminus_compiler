"""
Shayan Mohammadizadeh 98102273
Nona Ghazizadeh 98171007
"""

from Parser.parser import Parser

parser = Parser()
parser.parse()

with open('semantic_errors.txt', 'w') as f:
    if parser.semantic_analyzer.is_correct:
        f.write('The input program is semantically correct.')
    else:
        errors = '\n'.join(parser.semantic_analyzer.semantic_errors)
        f.write(errors)

with open('output.txt', 'w') as f:
    if parser.semantic_analyzer.is_correct:
        output = parser.inter_code_gen.mem_manager.return_code_block()
        f.write(output)
    else:
        f.write('The output code has not been generated.')

print('\n\n///////////////////////////////')
print(parser.semantic_analyzer.methods)

# from Parser.parser import Parser
# from anytree import RenderTree
#
# parser = Parser()
# parser.parse()
# output = ''
# for pre, fill, node in RenderTree(parser.root):
#     output += "%s%s" % (pre, node.name) + '\n'
# with open('parse_tree.txt', 'w') as f:
#     f.write(output)


# with open('syntax_errors.txt', 'w') as f:
#     if parser.syntax_error == '':
#         f.write('There is no syntax error.')
#     else:
#         f.write(parser.syntax_error)

# print('*************************')

# from Scanner.new_version_scanner import Scanner
#
# scanner = Scanner('input.txt')
# x = scanner.get_next_token()
# while x != '$':
#     print(x)
#     print(scanner.symbol_table)
#     print()
#     x = scanner.get_next_token()

