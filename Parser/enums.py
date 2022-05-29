FIRST = {
    "Program": ["break", "continue", "ID", "return", "global", "def", "if", "while", "output", None],
    "Statements": ["break", "continue", "ID", "return", "global", "def", "if", "while", "output", None],
    "Statement": ["break", "continue", "ID", "return", "global", "def", "if", "while", "output"],
    "Simple_stmt": ["break", "continue", "ID", "return", "global", "output"],
    "Compound_stmt": ["def", "if", "while"],
    "Assignment_Call": ["ID"],
    "B": ["=", "[", "("],
    "C": ["ID", "[", "NUM"],
    "List_Rest": [",", None],
    "Return_stmt": ["return"],
    "Return_Value": ["ID", "NUM", None],
    "Global_stmt": ["global"],
    "Function_def": ["def"],
    "Params": ["ID", None],
    "Params_Prime": [",", None],
    "If_stmt": ["if"],
    "Else_block": ["else", None],
    "Iteration_stmt": ["while"],
    "Relational_Expression": ["ID", "NUM"],
    "Relop": ["==", "<"],
    "Expression": ["ID", "NUM"],
    "Expression_Prime": ["+", "-", None],
    "Term": ["ID", "NUM"],
    "Term_Prime": ["*", None],
    "Factor": ["ID", "NUM"],
    "Power": ["(", "[", "**", None],
    "Primary": ["(", "[", None],
    "Arguments": ["ID", "NUM", None],
    "Arguments_Prime": [",", None],
    "Atom": ["ID", "NUM"]
}

FOLLOW = {
    "Program": ["$"],
    "Statements": [";", "else", "$"],
    "Statement": [";"],
    "Simple_stmt": [";"],
    "Compound_stmt": [";"],
    "Assignment_Call": [";"],
    "B": [";"],
    "C": [";"],
    "List_Rest": ["]"],
    "Return_stmt": [";"],
    "Return_Value": [";"],
    "Global_stmt": [";"],
    "Function_def": [";"],
    "Params": [")"],
    "Params_Prime": [")"],
    "If_stmt": [";"],
    "Else_block": [";"],
    "Iteration_stmt": [";"],
    "Relational_Expression": [")", ":"],
    "Relop": ["ID", "NUM"],
    "Expression": [";", "]", ")", ",", ":", "==", "<"],
    "Expression_Prime": [";", "]", ")", ",", ":", "==", "<"],
    "Term": [";", "]", ")", ",", ":", "==", "<", "+", "-"],
    "Term_Prime": [";", "]", ")", ",", ":", "==", "<", "+", "-"],
    "Factor": [";", "]", ")", ",", ":", "==", "<", "+", "-", "*"],
    "Power": [";", "]", ")", ",", ":", "==", "<", "+", "-", "*"],
    "Primary": [";", "]", ")", ",", ":", "==", "<", "+", "-", "*"],
    "Arguments": [")"],
    "Arguments_Prime": [")"],
    "Atom": [";", "[", "]", "(", ")", ",", ":", "==", "<", "+", "-", "*", "**"]
}

NON_TERMINAL = set(FIRST)
TERMINAL = {";", "break", "continue", "ID", "=", "[", "]", "(", ")", ",", "return", "global", "def", ":", "if",
            "else", "while", "==", "<", "+", "-", "*", "**", "NUM", "output"}

GRAMMAR = {
    "Program": ["Statements"],
    "Statements": ["Statement ; Statements", None],
    "Statement": ["Compound_stmt", "Simple_stmt"],
    "Simple_stmt": ["Assignment_Call", "Return_stmt", "Global_stmt", "break", "continue", "output ( ID )"],
    "Compound_stmt": ["Function_def", "If_stmt", "Iteration_stmt"],
    "Assignment_Call": ["#push_id ID B"],
    "B": ["= C #assign", "[ Expression ] = C #assign", "( Arguments )"],
    "C": ["Expression", "[ Expression List_Rest ]"],
    "List_Rest": [", Expression List_Rest", None],
    "Return_stmt": ["return Return_Value"],
    "Return_Value": ["Expression", None],
    "Global_stmt": ["global ID"],
    "Function_def": ["def #update_method_addr ID ( Params ) : Statements"],
    "Params": ["ID Params_Prime", None],
    "Params_Prime": [", ID Params_Prime", None],
    "If_stmt": ["if Relational_Expression : Statements Else_block"],
    "Else_block": ["else : Statements", None],
    "Iteration_stmt": ["while ( Relational_Expression ) Statements"],
    "Relational_Expression": ["Expression Relop Expression"],
    "Relop": ["==", "<"],
    "Expression": ["Term Expression_Prime"],
    "Expression_Prime": ["+ Term Expression_Prime", "- Term Expression_Prime", None],
    "Term": ["Factor Term_Prime"],
    "Term_Prime": ["* Factor Term_Prime", None],
    "Factor": ["Atom Power"],
    "Power": ["** Factor", "Primary"],
    "Primary": ["[ Expression ] Primary", "( Arguments ) Primary", None],
    "Arguments": ["Expression Arguments_Prime", None],
    "Arguments_Prime": [", Expression Arguments_Prime", None],
    "Atom": ["ID", "#push_num NUM"]
}
