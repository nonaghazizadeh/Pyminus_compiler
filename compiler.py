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

print(parser.table['Simple_stmt'])

# print('*************************')

# parser.inter_code_gen.mem_manager.take_pic()
# print('tpp_sp: ' + str(parser.inter_code_gen.mem_manager.top))
