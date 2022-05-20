"""
Shayan Mohammadizadeh 98102273
Nona Ghazizadeh 98171007
"""


from Parser.parser import Parser
from anytree import RenderTree
# from Scanner.new_version_scanner import Scanner

parser = Parser()
parser.parse()

output = ''
for pre, fill, node in RenderTree(parser.root):
    output += "%s%s" % (pre, node.name) + '\n'
with open('parse_tree.txt', 'w') as f:
    f.write(output)


with open('syntax_errors.txt', 'w') as f:
    if parser.syntax_error == '':
        f.write('There is no syntax error.')
    else:
        f.write(parser.syntax_error)

print('*************************')

# for pre, fill, node in RenderTree(parser.root):
#     print("%s%s" % (pre, node.name))
#
# scanner = Scanner('input.txt')
# while True:
#     print(f'{scanner.get_next_token()} {scanner.lineno}')

# from Scanner.pre_version_scanner import Scanner
#
# scanner = Scanner('input.txt')
# scanner.get_all_tokens()
