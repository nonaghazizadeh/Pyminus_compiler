import re

from Scanner import enums

from Scanner.file_handler import FileHandler


class Scanner:
    def __init__(self, file):
        self.file_handler = FileHandler(file)
        self.lines = self.file_handler.read_input_file()
        self.symbol_table = self.file_handler.symbol_table
        self.tokenized = ''

    def recognize_keyid(self, token):
        if token in enums.Languages.KEYWORDS.value:
            return 'KEYWORD', token
        else:
            self.symbol_table.add_element(token)
            return 'ID', token

    @staticmethod
    def recognize_symbol(token):
        return enums.TokenType.SYMBOL.name, token

    @staticmethod
    def recognize_number(token):
        return enums.TokenType.NUMBER.name, token

    def get_next_token(self, chars):
        comment_is_continued = False
        idx = 0
        line_tokens = ''
        while idx < len(chars):
            if not comment_is_continued:
                if chars[idx] in enums.Languages.WHITESPACES.value:
                    idx += 1
                    continue
                elif chars[idx] in enums.Languages.SYMBOLS.value:
                    if ''.join(chars[idx: idx + 2]) in enums.Languages.SYMBOLS.value:
                        line_tokens += ' ' + str(self.recognize_symbol(''.join(chars[idx: idx + 2])))
                        idx += 2
                    elif (chars[idx] == enums.Languages.EQUAL.value or chars[
                        idx] == enums.Languages.STAR.value) and idx + 1 < len(chars) and chars[
                        idx + 1] not in enums.Languages.WHITESPACES.value and not re.search(enums.Regex.LETTER.value,
                                                                                            chars[
                                                                                                idx + 1]) and not re.search(
                        enums.Regex.DIGIT.value, chars[idx + 1]) and chars[
                        idx + 1] != enums.Languages.HASHTAG.value:
                        current_token = chars[idx]
                        idx += 1
                        if chars[idx] == enums.Languages.SLASH.value and idx + 1 < len(chars) and chars[
                            idx + 1] == enums.Languages.STAR.value:
                            line_tokens += ' ' + str(self.recognize_symbol(current_token))
                        else:
                            continue
                    else:
                        line_tokens += ' ' + str(self.recognize_symbol(''.join(chars[idx])))
                        idx += 1
                elif re.search(enums.Regex.LETTER.value, chars[idx]):
                    lexeme = ''
                    another_char_recognized = False
                    for i in range(idx, len(chars)):
                        if re.search(enums.Regex.LETTER.value, chars[i]) or re.search(enums.Regex.DIGIT.value,
                                                                                      chars[i]):
                            lexeme = chars[idx:i + 1]
                        elif chars[i] in enums.Languages.SYMBOLS.value or chars[i] in enums.Languages.WHITESPACES.value:
                            idx = i
                            line_tokens += ' ' + str(self.recognize_keyid(''.join(lexeme)))
                            another_char_recognized = True
                            break
                        elif chars[i] == '#' or chars[i] == '/':
                            idx = i
                            line_tokens += ' ' + str(self.recognize_keyid(''.join(lexeme)))
                            another_char_recognized = True
                            break
                        else:
                            idx = i
                            another_char_recognized = True
                            break
                    if not another_char_recognized:
                        line_tokens += ' ' + str(self.recognize_keyid(''.join(lexeme)))
                        break
                    continue
                elif re.search(enums.Regex.DIGIT.value, chars[idx]):
                    number_lexeme = ''
                    another_char_recognized = False
                    for i in range(idx, len(chars)):
                        if re.search(enums.Regex.DIGIT.value, chars[i]):
                            number_lexeme = chars[idx:i + 1]
                        elif chars[i] == '.' and re.search(enums.Regex.DIGIT.value,
                                                           chars[i - 1]) and '.' not in chars[idx:i] and re.search(
                            enums.Regex.DIGIT.value,
                            chars[i + 1]):
                            number_lexeme = chars[idx:i + 1]
                        elif chars[i] == '.' and re.search(enums.Regex.DIGIT.value, chars[i - 1]) and '.' in chars[
                                                                                                             idx:i]:
                            idx = i
                            another_char_recognized = True
                            break
                        elif chars[i] in enums.Languages.SYMBOLS.value or chars[i] in enums.Languages.WHITESPACES.value:
                            idx = i
                            line_tokens += ' ' + str(self.recognize_number(''.join(number_lexeme)))
                            another_char_recognized = True
                            break
                        elif re.search(enums.Regex.LETTER.value, chars[i]):
                            idx = i + 1
                            another_char_recognized = True
                            break
                        elif chars[i] == '#' or chars[i] == '/':
                            idx = i
                            line_tokens += ' ' + str(self.recognize_number(''.join(number_lexeme)))
                            another_char_recognized = True
                            break
                        else:
                            idx = i + 1
                            another_char_recognized = True
                            break
                    if not another_char_recognized:
                        line_tokens += ' ' + str(self.recognize_number(''.join(number_lexeme)))
                        break
                    continue
                elif chars[idx] == '#':
                    for i in range(idx, len(chars)):
                        idx += 1
                elif chars[idx] == '/' and idx + 1 < len(chars) and chars[idx + 1] == '*':
                    comment_is_continued = True
                else:
                    idx += 1
            elif comment_is_continued:
                for i in range(len(chars)):
                    if chars[i] == '*' and i + 1 < len(chars) and chars[i + 1] == '/':
                        idx = i + 2
                        comment_is_continued = False
                        break
                if comment_is_continued:
                    break
                continue
        return line_tokens

    def get_next_line_tokens(self, lineno, line):
        tokenized_line = self.get_next_token(list(line))
        if tokenized_line != '':
            self.file_handler.tokenized += str(lineno + 1) + ".\t" + tokenized_line + "\n"

    def get_all_tokens(self):
        for no, line in enumerate(self.lines):
            self.get_next_line_tokens(no, line)
        self.file_handler.write_files()
