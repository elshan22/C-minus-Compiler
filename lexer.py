from typing import List, Tuple, Dict
from dfa import DFA


# get initial keywords as the symbol table
def get_initial_symbols() -> Dict[str, Tuple[str, int, int]]:
    keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif', 'output']
    return {x: ('KEYWORD', 0, 1) for x in keywords}


# this function takes a file_name, and returns all its characters with its line number
def get_chars(file_name: str) -> List[Tuple[int, str]]:
    result = []
    with open(file_name) as code:
        for i, line in enumerate(code):
            for c in line:
                result.append((i, c))
        result.append((i+1, '$$'))
    return result


class Lexer:

    def __init__(self, file_name: str) -> None:
        self.chars = get_chars(file_name)   # get input characters
        self.pointer = 0    # indicates the index we are reading in the characters array
        self.lineno = 0     # indicates the line number that our token is started
        self.lexeme = ''    # the current lexeme we have read
        self.DFA = DFA()    # we use a DFA to get the tokens
        self.symbols = get_initial_symbols()    # symbol table
        self.spaces = {' ', '\n', '\t', '\f', '\r', '\v'}   # all whitespace characters

    # returns the symbol table
    def get_symbols(self) -> Dict[str, Tuple[str, int, int]]:
        return self.symbols

    # read the next character and change the DFA state according to the character
    def get_dfa_state(self):
        c = self.chars[self.pointer][1]
        self.lexeme += '' if c == '$$' else c
        self.pointer += 1   # move pointer forward
        return self.DFA.change_state(self.chars[self.pointer - 1][1], self.lexeme, self.symbols)

    # this function returns the next token recognized by the lexer
    def get_next_token(self) -> Tuple[str, str, int]:
        if self.pointer >= len(self.chars):     # if pointer has exceeded the number of characters, return EOF
            return '$$', '', self.chars[-1][0]
        result = self.get_dfa_state()   # read next character
        is_changed = False      # a bool value to correctly determine the line number
        while result[0] == '':  # while we haven't reached a token, read the next character
            if not is_changed and self.chars[self.pointer][1] not in self.spaces:
                # we use the first non-space character line number as the token line number
                is_changed = True
                self.lineno = self.chars[self.pointer][0]
            self.pointer -= result[1]   # some states will change our pointer position
            self.lexeme = '' if result[2] else self.lexeme[:len(self.lexeme)-result[1]]     # update the lexeme
            result = self.get_dfa_state()
        self.pointer -= result[1]
        returned_lexeme = self.lexeme[:len(self.lexeme) - (result[1] - 1)]  # final lexeme
        self.lexeme = '' if result[2] else self.lexeme[:len(self.lexeme) - result[1]]
        if result[0] == 'Unclosed comment':
            # if we have got an Unclosed comment token, we should check whether its length is below 7 or not
            return result[0], returned_lexeme if len(returned_lexeme) < 7 else (returned_lexeme[:7] + '...'), self.lineno
        return result[0], returned_lexeme, self.lineno  # we return the token, its lexeme and its line number
