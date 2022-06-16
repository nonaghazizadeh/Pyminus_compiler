class SemanticAnalyzer:
    def __init__(self):
        self.is_correct = True
        self.semantic_errors = []
        self.methods = []
        self.variables = []

    def analyze(self, semantic_routine: str, param: str, lineno: int):
        print(semantic_routine.upper())

        semantic_routine = semantic_routine[2:]     # delete two first hashtags
        if semantic_routine == 'add_method':
            self.methods.append(param)
        elif semantic_routine == 'check_main':
            print(lineno)
        else:
            print('SEMANTIC ROUTINE NOT FOUND!')
