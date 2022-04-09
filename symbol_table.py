import enums


class SymbolTable:
    def __init__(self):
        self.elements = enums.Languages.KEYWORDS.value.copy()

    def add_element(self, element):
        if not self.element_exist(element):
            self.elements.append(element)

    def element_exist(self, element):
        return element in self.elements

    def get_elements(self):
        output = ''
        for idx, element in enumerate(self.elements):
            output += str(idx + 1) + ".\t" + element + "\n"
        return output
