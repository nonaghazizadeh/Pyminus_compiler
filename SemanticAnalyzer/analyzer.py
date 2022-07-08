class SemanticAnalyzer:
    def __init__(self):
        self.is_correct = True
        self.semantic_errors = []
        self.methods = []
        self.variables = []

    def analyze(self, semantic_routine: str, param: str, lineno: int):
        print(semantic_routine.upper())

        semantic_routine = semantic_routine[1:]  # delete two first hashtags
        if semantic_routine == 'add_method':
            self.methods.append(param)
        elif semantic_routine == 'check_main':
            if 'main' not in self.methods:
                self.add_error('func_main', lineno)
        else:
            print('SEMANTIC ROUTINE NOT FOUND!')

    def add_error(self, err: str, lineno: int, id: str = ''):
        msg = {
            'func_main': 'main function not found'
        }.get(err)
        self.semantic_errors.append(f'#{lineno} : Semantic Error! {msg}.')
