from enum import Enum


class Languages(Enum):
    KEYWORDS = ['break', 'continue', 'def', 'else', 'if', 'return', 'while', 'output', 'global']
    SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '+', '-', '*', '=', '<', '==', '**']
    WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
    EQUAL = '='
    STAR = '*'
    SLASH = '/'
    HASHTAG = '#'


class Regex(Enum):
    LETTER = '[a-zA-Z]'
    DIGIT = '[0-9]'


class TokenType(Enum):
    NUMBER = 1
    SYMBOL = 2
    KEYWORD = 3
    ID = 4


class ErrorType(Enum):
    INVALID_INPUT = 'Invalid input'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'
    INVALID_NUMBER = 'Invalid number'
    NO_ERROR = 'There is no lexical error.'
