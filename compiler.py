"""
Shayan Mohammadizadh 98102273
Nona Ghazizadeh 98171007
"""


from Parser.parser import Parser
# from Scanner.new_version_scanner import Scanner


parser = Parser()
res = parser.parse()
print(res)
# scanner = Scanner('input.txt')
# while True:
#     print(scanner.get_next_token())

# print(parser.table['Relop'])

with open('parse_tree.txt', 'w') as f:
    f.write(res)
