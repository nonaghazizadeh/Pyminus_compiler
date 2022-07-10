class SemanticAnalyzer:
    def __init__(self):
        self.is_correct = True
        self.semantic_errors = []
        self.methods = []
        self.global_vars = []
        self.local_vars = []
        self.is_local = False
        self.is_method_valid = False
        self.in_while = 0
        self.saved_id = ''
        self.lineno = 0
        self.param_num = 0
        self.passed_num = 0
        self.called_func = ''
        self.defined_func = ''

    def analyze(self, semantic_routine: str, param: str, lineno: int):
        print(semantic_routine.upper())

        semantic_routine = semantic_routine[1:]  # delete two first hashtags
        self.lineno = lineno

        if semantic_routine == 'add_method':
            if self.find_method(self.defined_func, self.param_num) is not None:
                self.add_error('overloading', self.defined_func)
            else:
                self.is_method_valid = True
                self.methods.append({
                    'name': self.defined_func,
                    'is_void': True,
                    'arg_num': self.param_num
                })

        elif semantic_routine == 'save_func':
            self.local_vars = []
            self.is_local = True
            self.param_num = 0
            self.defined_func = param
            self.is_method_valid = False

        elif semantic_routine == 'check_main':
            if 'main' not in self.get_method_names():
                self.add_error('func_main')

        elif semantic_routine == 'save_id':
            self.saved_id = param

        elif semantic_routine == 'add_id':
            if self.is_local:
                self.local_vars.append(self.saved_id)
            else:
                self.global_vars.append(self.saved_id)

        elif semantic_routine == 'check_id':
            ids = self.get_method_names() + self.local_vars + self.global_vars
            if self.saved_id not in ids:
                self.add_error('scoping', self.saved_id)

        elif semantic_routine == 'call_func':
            self.passed_num = 0
            self.called_func = self.saved_id

        elif semantic_routine == 'inc_param_num':
            self.param_num += 1

        elif semantic_routine == 'inc_passed':
            self.passed_num += 1

        elif semantic_routine == 'match_param':
            if self.called_func in self.get_method_names():
                if self.find_method(self.called_func, self.passed_num) is None:
                    self.add_error('match_param', self.called_func)

        elif semantic_routine == 'is_not_void':
            if self.is_method_valid:
                self.methods[-1]['is_void'] = False

        elif semantic_routine == 'check_type':
            if self.called_func in self.get_method_names():
                inx = self.find_method(self.called_func, self.passed_num)
                if inx is None:
                    for i, m in enumerate(self.methods):
                        if m['name'] == self.called_func:
                            inx = i
                            break

                if self.methods[inx]['is_void']:
                    self.add_error('type_mismatch')

        elif semantic_routine == 'enter_while':
            self.in_while += 1

        elif semantic_routine == 'exit_while':
            self.in_while -= 1

        elif semantic_routine == 'continue':
            if self.in_while == 0:
                self.add_error('continue')

        elif semantic_routine == 'break':
            if self.in_while == 0:
                self.add_error('break')

        else:
            print('SEMANTIC ROUTINE NOT FOUND!')

    def add_error(self, err: str, id: str = ''):
        msg = {
            'func_main': 'main function not found',
            'scoping': f'\'{id}\' is not defined appropriately',
            'match_param': f'Mismatch in numbers of arguments of \'{id}\'',
            'break': 'No \'while\' found for \'break\'',
            'continue': 'No \'while\' found for \'continue\'',
            'type_mismatch': 'Void type in operands',
            'overloading': f'Function \'{id}\' has already been defined with this number of arguments'
        }.get(err)
        self.semantic_errors.append(f'#{self.lineno} : Semantic Error! {msg}.')

    def find_method(self, name, num):
        for inx, method in enumerate(self.methods):
            if method['name'] == name and method['arg_num'] == num:
                return inx

        return None

    def get_method_names(self):
        return [m['name'] for m in self.methods]
