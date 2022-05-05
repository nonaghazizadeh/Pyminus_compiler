"""
Shayan Mohammadizadeh 98102273
Nona Ghazizadeh 98171007
"""


from Parser.parser import Parser
# from Scanner.new_version_scanner import Scanner

parser = Parser()
parser.parse()
with open('parse_tree.txt', 'w') as f:
    f.write(parser.parse_tree)

with open('syntax_errors.txt', 'w') as f:
    if parser.syntax_error == '':
        f.write('There is no syntax error.')
    else:
        f.write(parser.syntax_error)

# scanner = Scanner('input.txt')
# while True:
#     print(f'{scanner.get_next_token()} {scanner.lineno}')
