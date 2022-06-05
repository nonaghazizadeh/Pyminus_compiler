import re

from Scanner import enums

from Scanner.file_handler import FileHandler


class Scanner:
    def __init__(self, file):
        self.file_handler = FileHandler(file)
        self.lines = self.file_handler.read_input_file()
        self.scanner_symbol_table = self.file_handler.symbol_table
        self.error_lines = []
        self.token_lines = []
        self.comment_mode = False
        self.comment_line = 0
        self.comment_buffer = [enums.Languages.SLASH.value, enums.Languages.STAR.value]
        self.tokens = []
        self.errors = ''
        self.lineno = 0
        self.idx = 0
        self.symbol_table = {'global': {}, 'local': {}}
        self.first_current_state = 0
        self.second_current_state = 0
        self.func_start = False
        self.in_second_scope = False
        self.reach_keyword = False
        self.memory = ''
        self.functions_name = []
        self.second_scope_globals = []

    def recognize_keyid(self, token):
        if token in enums.Languages.KEYWORDS.value:
            return 'KEYWORD', token
        else:
            self.scanner_symbol_table.add_element(token)
            return 'ID', token

    @staticmethod
    def recognize_symbol(token):
        return enums.TokenType.SYMBOL.name, token

    @staticmethod
    def recognize_number(token):
        return enums.TokenType.NUMBER.name, token

    @staticmethod
    def recognize_invalid_input_error(token):
        return token, enums.ErrorType.INVALID_INPUT.value

    @staticmethod
    def recognize_invalid_number_error(token):
        return token, enums.ErrorType.INVALID_NUMBER.value

    @staticmethod
    def recognize_unmatched_comment_error(token):
        return token, enums.ErrorType.UNMATCHED_COMMENT.value

    @staticmethod
    def recognize_unclosed_comment_error(token):
        return token, enums.ErrorType.UNCLOSED_COMMENT.value

    @staticmethod
    def whitespace_dfa(idx):
        return idx + 1

    def end_comment_dfa(self, chars, idx):
        return idx + 2, ' (' + str(', '.join(self.recognize_unmatched_comment_error(chars[idx] + chars[idx + 1]))) + ")"

    def symbol_dfa(self, chars, idx):
        line_tokens = ''
        errors = ''
        if ''.join(chars[idx: idx + 2]) in enums.Languages.SYMBOLS.value:
            line_tokens += ' (' + str(
                ', '.join((self.recognize_symbol(''.join(chars[idx: idx + 2]))))) + ")"
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
                line_tokens += ' (' + str(', '.join(self.recognize_symbol(current_token))) + ')'
            elif chars[idx] in enums.Languages.SYMBOLS.value:
                line_tokens += ' (' + str(', '.join(self.recognize_symbol(current_token))) + ')'
            else:
                errors += ' (' + str(
                    ', '.join(self.recognize_invalid_input_error(current_token + chars[idx]))) + ")"
                idx += 1
        else:
            line_tokens += ' (' + str(', '.join(self.recognize_symbol(''.join(chars[idx])))) + ')'
            idx += 1

        return idx, bool(errors), errors, line_tokens

    def keyid_dfa(self, chars, idx):
        lexeme = ''
        another_char_recognized = False
        line_tokens = ''
        errors = ''
        for i in range(idx, len(chars)):
            if re.search(enums.Regex.LETTER.value, chars[i]) or re.search(enums.Regex.DIGIT.value,
                                                                          chars[i]):
                lexeme = chars[idx:i + 1]
            elif chars[i] in enums.Languages.SYMBOLS.value or chars[i] in enums.Languages.WHITESPACES.value:
                idx = i
                line_tokens += ' (' + str(', '.join(self.recognize_keyid(''.join(lexeme)))) + ")"
                another_char_recognized = True
                break
            elif chars[i] == enums.Languages.HASHTAG.value or (
                    chars[i] == enums.Languages.SLASH.value and i + 1 < len(chars) and chars[
                i + 1] == enums.Languages.STAR.value):
                idx = i
                line_tokens += ' (' + str(', '.join(self.recognize_keyid(''.join(lexeme)))) + ")"
                another_char_recognized = True
                break
            elif chars[i] == enums.Languages.SLASH.value:
                idx = i
                line_tokens += ' (' + str(', '.join(self.recognize_keyid(''.join(lexeme)))) + ")"
                another_char_recognized = True
                break
            else:
                idx = i
                errors += ' (' + str(
                    ', '.join(self.recognize_invalid_input_error(''.join(lexeme) + chars[idx]))) + ")"
                idx = i + 1
                another_char_recognized = True
                break

        self.filling_symbol_table(chars, idx, lexeme)

        return idx, another_char_recognized, lexeme, bool(errors), errors, line_tokens

    def number_dfa(self, chars, idx):
        number_lexeme = ''
        another_char_recognized = False
        line_tokens = ''
        errors = ''
        for i in range(idx, len(chars)):
            if re.search(enums.Regex.DIGIT.value, chars[i]):
                number_lexeme = chars[idx:i + 1]
            elif chars[i] == '.' and re.search(enums.Regex.DIGIT.value,
                                               chars[i - 1]) and '.' not in chars[idx:i] and i + 1 < len(
                chars) and re.search(
                enums.Regex.DIGIT.value,
                chars[i + 1]):
                number_lexeme = chars[idx:i + 1]
            elif chars[i] == '.' and re.search(enums.Regex.DIGIT.value, chars[i - 1]) and '.' in chars[
                                                                                                 idx:i]:
                errors += ' ' + str(self.recognize_invalid_number_error(''.join(number_lexeme) + chars[i]))
                idx = i + 1
                another_char_recognized = True
                break
            elif chars[i] in enums.Languages.SYMBOLS.value or chars[i] in enums.Languages.WHITESPACES.value:
                idx = i
                line_tokens += ' (' + str(', '.join(self.recognize_number(''.join(number_lexeme)))) + ')'
                another_char_recognized = True
                break
            elif re.search(enums.Regex.LETTER.value, chars[i]):
                errors += ' (' + str(
                    ', '.join(self.recognize_invalid_number_error(''.join(number_lexeme) + chars[i]))) + ")"
                idx = i + 1
                another_char_recognized = True
                break
            elif chars[i] == enums.Languages.HASHTAG.value or chars[i] == enums.Languages.SLASH.value:
                idx = i
                line_tokens += ' (' + str(', '.join(self.recognize_number(''.join(number_lexeme)))) + ")"
                another_char_recognized = True
                break
            elif chars[i] == '.' and i + 1 < len(chars) and not re.search(enums.Regex.DIGIT.value,
                                                                          chars[i + 1]):
                errors += ' (' + str(', '.join(
                    self.recognize_invalid_number_error(
                        ''.join(number_lexeme) + chars[i] + chars[i + 1]))) + ")"
                idx = i + 2
                another_char_recognized = True
                break
            else:
                errors += ' (' + str(', '.join(
                    self.recognize_invalid_number_error(''.join(number_lexeme) + chars[i]))) + ")"
                idx = i + 1
                another_char_recognized = True
                break
        return idx, another_char_recognized, number_lexeme, bool(errors), errors, line_tokens

    def hashtag_comment_dfa(self, chars, idx):
        for i in range(idx, len(chars)):
            idx += 1
        self.lineno += 1
        return idx

    def slash_star_comment_dfa(self, lineno):
        self.comment_mode = True
        self.comment_line = lineno + 1

    def others_dfa(self, chars, idx):
        return idx + 1, ' (' + str(', '.join(self.recognize_invalid_input_error(chars[idx]))) + ")"

    def filling_symbol_table(self, chars, idx, lexeme):
        if lexeme == enums.Languages.KEYWORDS.value[8]:
            self.memory = lexeme

        if self.in_second_scope and lexeme in enums.Languages.STARTER_KEYWORDS.value:
            self.reach_keyword = True

        if self.func_start:
            temp_dict = self.symbol_table['global']
            temp_dict[lexeme] = None
            self.functions_name.append(lexeme)
            self.func_start = False
        elif not self.func_start and lexeme not in enums.Languages.KEYWORDS.value and not self.reach_keyword:
            if self.in_second_scope:
                if self.memory == enums.Languages.KEYWORDS.value[8]:
                    self.second_scope_globals.append(lexeme)
                    self.memory = ''
                elif self.memory == '' and lexeme not in self.second_scope_globals:
                    temp_dict = self.symbol_table['local']
                    for jdx in range(idx, len(chars)):
                        if chars[jdx] == enums.Languages.WHITESPACES.value[0]:
                            continue
                        elif chars[jdx] == enums.Languages.EQUAL.value or chars[jdx] == enums.Languages.SYMBOLS.value[
                            2] or chars[jdx] == enums.Languages.SYMBOLS.value[6]:
                            if lexeme not in temp_dict:
                                temp_dict[lexeme] = self.second_current_state
                                self.second_current_state += 1
                            break
                        else:
                            break
            elif not self.in_second_scope:
                temp_dict = self.symbol_table['global']
                if lexeme not in temp_dict:
                    temp_dict[lexeme] = self.first_current_state
                    self.first_current_state += 1
                self.second_scope_globals = []

        if lexeme == enums.Languages.KEYWORDS.value[2]:
            self.in_second_scope = True
            self.func_start = True
            self.reach_keyword = False
            self.symbol_table['local'] = {}
            self.second_current_state = 0

        print(self.symbol_table)

    def add_to_files(self):
        if len(self.tokens) != 0:
            if self.lineno + 1 not in self.token_lines:
                self.token_lines.append(self.lineno + 1)
                self.file_handler.tokenized += str(self.lineno + 1) + ".\t" + ''.join(self.tokens).lstrip() + "\n"
            else:
                self.file_handler.tokenized = self.file_handler.tokenized[:-1]
                self.file_handler.tokenized += ''.join(self.tokens) + "\n"
        if self.errors != '':
            self.error_lines.append(self.lineno + 1)
            self.file_handler.lexical_errors += str(self.lineno + 1) + ".\t" + self.errors.lstrip() + "\n"

    def clear_data(self):
        self.tokens = []
        self.errors = ''
        self.idx = 0

    def get_next_token(self):
        token = ''
        founded = False
        chars = self.lines[self.lineno]

        while not founded:
            if not self.comment_mode:
                if self.idx >= len(chars):
                    self.add_to_files()
                    self.clear_data()
                    self.lineno += 1
                    token = ''
                    founded = True
                elif chars[self.idx] == '\n':
                    self.add_to_files()
                    self.clear_data()
                    self.lineno += 1
                    token = ''
                    founded = False
                    if self.lineno < len(self.lines):
                        chars = self.lines[self.lineno]
                    else:
                        break
                elif chars[self.idx] in enums.Languages.WHITESPACES.value:
                    self.idx = self.whitespace_dfa(self.idx)
                    continue
                elif chars[self.idx] == enums.Languages.STAR.value and self.idx + 1 < len(chars) and chars[
                    self.idx + 1] == enums.Languages.SLASH.value:
                    res = self.end_comment_dfa(chars, self.idx)
                    self.idx = res[0]
                    self.errors += res[1]
                elif chars[self.idx] in enums.Languages.SYMBOLS.value:
                    res = self.symbol_dfa(chars, self.idx)
                    self.idx = res[0]
                    if res[1]:
                        self.errors += res[2]
                    else:
                        token = res[3]
                        self.tokens.append(token)
                        founded = True
                elif re.search(enums.Regex.LETTER.value, chars[self.idx]):
                    res = self.keyid_dfa(chars, self.idx)
                    self.idx = res[0]
                    if res[1] and res[3]:
                        self.errors += res[4]
                    elif res[1] and not res[3]:
                        token = res[5]
                        self.tokens.append(token)
                        founded = True
                    else:
                        token = ' (' + str(', '.join(self.recognize_keyid(''.join(res[2])))) + ")"
                        self.tokens.append(token)
                        self.idx += len(''.join(res[2]))
                        founded = True
                    continue
                elif re.search(enums.Regex.DIGIT.value, chars[self.idx]):
                    res = self.number_dfa(chars, self.idx)
                    self.idx = res[0]
                    if res[1] and res[3]:
                        self.errors += res[4]
                    elif res[1] and not res[3]:
                        token = res[5]
                        self.tokens.append(res[5])
                        founded = True
                    else:
                        token = ' (' + str(', '.join(self.recognize_number(''.join(res[2])))) + ")"
                        self.tokens.append(token)
                        self.idx += len(''.join(res[2]))
                        founded = True
                    continue
                elif chars[self.idx] == enums.Languages.HASHTAG.value:
                    self.add_to_files()
                    self.clear_data()
                    self.lineno += 1
                    break
                elif chars[self.idx] == enums.Languages.SLASH.value and self.idx + 1 < len(chars) and chars[
                    self.idx + 1] == enums.Languages.STAR.value:
                    self.idx += 2
                    self.slash_star_comment_dfa(self.lineno)
                else:
                    res = self.others_dfa(chars, self.idx)
                    self.idx = res[0]
                    self.errors += res[1]
            elif self.comment_mode:
                chars = self.lines[self.lineno]
                self.add_to_files()
                for i in range(self.idx, len(chars)):
                    self.comment_buffer.append(chars[i])
                    if chars[i] == enums.Languages.STAR.value and i + 1 < len(chars) and chars[
                        i + 1] == enums.Languages.SLASH.value:
                        self.clear_data()
                        self.idx = i + 2
                        self.comment_mode = False
                        break
                if self.comment_mode:
                    self.clear_data()
                    self.lineno += 1
                    break
                continue

        if token == '' and self.lineno == len(self.lines):
            self.lineno -= 1
            return "$"
        elif token != '':
            return tuple(map(str, token[2:-1].split(', ')))
        else:
            return self.get_next_token()

    def get_input(self):
        while self.lineno < len(self.lines):
            res = self.get_next_token()
            if res != "$":
                continue
            elif res == "$":
                break
        print(self.symbol_table)

    def get_all_tokens(self):
        self.get_input()
        if self.comment_mode:
            if self.comment_line in self.error_lines:
                self.file_handler.lexical_errors = self.file_handler.lexical_errors[:-1] + " (" + str(', '.join(
                    self.recognize_unclosed_comment_error(''.join(self.comment_buffer[0:10]) + '...'))) + ")\n"
            else:
                self.file_handler.lexical_errors += str(self.comment_line) + ".\t(" + str(', '.join(
                    self.recognize_unclosed_comment_error(''.join(self.comment_buffer[0:10]) + '...'))) + ")\n"
        self.file_handler.write_files()
