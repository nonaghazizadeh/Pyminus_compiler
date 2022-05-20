import re

from Scanner import enums

from Scanner.file_handler import FileHandler


class Scanner:
    def __init__(self, file):
        self.file_handler = FileHandler(file)
        self.lines = self.file_handler.read_input_file()
        self.symbol_table = self.file_handler.symbol_table
        self.error_lines = []
        self.comment_mode = False
        self.comment_line = 0
        self.comment_buffer = [enums.Languages.SLASH.value, enums.Languages.STAR.value]
        self.tokens = []
        self.lineno = 0

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

    @staticmethod
    def hashtag_comment_dfa(chars, idx):
        for i in range(idx, len(chars)):
            idx += 1
        return idx

    def slash_star_comment_dfa(self, lineno):
        self.comment_mode = True
        self.comment_line = lineno + 1

    def others_dfa(self, chars, idx):
        return idx + 1, ' (' + str(', '.join(self.recognize_invalid_input_error(chars[idx]))) + ")"

    def go_trough_line(self, chars, lineno):
        idx = 0
        line_tokens = ''
        errors = ''
        while idx < len(chars):
            if not self.comment_mode:
                if chars[idx] in enums.Languages.WHITESPACES.value:
                    idx = self.whitespace_dfa(idx)
                    continue
                elif chars[idx] == enums.Languages.STAR.value and idx + 1 < len(chars) and chars[
                    idx + 1] == enums.Languages.SLASH.value:
                    res = self.end_comment_dfa(chars, idx)
                    idx = res[0]
                    errors += res[1]
                elif chars[idx] in enums.Languages.SYMBOLS.value:
                    res = self.symbol_dfa(chars, idx)
                    idx = res[0]
                    if res[1]:
                        errors += res[2]
                    else:
                        line_tokens += res[3]
                        self.tokens.append(res[3])
                elif re.search(enums.Regex.LETTER.value, chars[idx]):
                    res = self.keyid_dfa(chars, idx)
                    idx = res[0]
                    if res[1] and res[3]:
                        errors += res[4]
                    elif res[1] and not res[3]:
                        line_tokens += res[5]
                        self.tokens.append(res[5])
                    else:
                        line_tokens += ' (' + str(', '.join(self.recognize_keyid(''.join(res[2])))) + ")"
                        self.tokens.append(' (' + str(', '.join(self.recognize_keyid(''.join(res[2])))) + ")")
                        break
                    continue
                elif re.search(enums.Regex.DIGIT.value, chars[idx]):
                    res = self.number_dfa(chars, idx)
                    idx = res[0]
                    if res[1] and res[3]:
                        errors += res[4]
                    elif res[1] and not res[3]:
                        line_tokens += res[5]
                        self.tokens.append(res[5])
                    else:
                        line_tokens += ' (' + str(', '.join(self.recognize_number(''.join(res[2])))) + ")"
                        self.tokens.append(line_tokens)
                        break
                    continue
                elif chars[idx] == enums.Languages.HASHTAG.value:
                    idx = self.hashtag_comment_dfa(chars, idx)
                elif chars[idx] == enums.Languages.SLASH.value and idx + 1 < len(chars) and chars[
                    idx + 1] == enums.Languages.STAR.value:
                    idx += 2
                    self.slash_star_comment_dfa(lineno)
                else:
                    res = self.others_dfa(chars, idx)
                    idx = res[0]
                    errors += res[1]
            elif self.comment_mode:
                for i in range(idx, len(chars)):
                    self.comment_buffer.append(chars[i])
                    if chars[i] == enums.Languages.STAR.value and i + 1 < len(chars) and chars[
                        i + 1] == enums.Languages.SLASH.value:
                        idx = i + 2
                        self.comment_mode = False
                        break
                if self.comment_mode:
                    break
                continue
        return line_tokens, errors

    def get_next_line_tokens(self, lineno, line):
        res = self.go_trough_line(list(line), lineno)
        tokenized_line = res[0]
        errors = res[1]
        if tokenized_line != '':
            self.file_handler.tokenized += str(lineno + 1) + ".\t" + tokenized_line.lstrip() + "\n"
        if errors != '':
            self.error_lines.append(lineno + 1)
            self.file_handler.lexical_errors += str(lineno + 1) + ".\t" + errors.lstrip() + "\n"

    def get_all_tokens(self):
        print(self.lines)
        for line in self.lines:
            self.get_next_line_tokens(self.lineno, line)
            self.lineno += 1
        if self.comment_mode:
            if self.comment_line in self.error_lines:
                self.file_handler.lexical_errors = self.file_handler.lexical_errors[:-1] + " (" + str(', '.join(
                    self.recognize_unclosed_comment_error(''.join(self.comment_buffer[0:10]) + '...'))) + ")\n"
            else:
                self.file_handler.lexical_errors += str(self.comment_line) + ".\t(" + str(', '.join(
                    self.recognize_unclosed_comment_error(''.join(self.comment_buffer[0:10]) + '...'))) + ")\n"
        self.file_handler.write_files()


