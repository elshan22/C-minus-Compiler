from collections import defaultdict
from typing import List, Dict, Tuple, Callable


# a helper function to add all digits through 0-9 to a DFA state
def add_nums(state: Dict[str, int], dst: int) -> None:
    for i in range(10):
        state[chr(ord('0')+i)] = dst


# a helper function to add all letters through a-zA-Z to a DFA state
def add_letters(state: Dict[str, int], dst: int) -> None:
    for i in range(26):
        state[chr(ord('a')+i)] = dst
        state[chr(ord('A')+i)] = dst


# a helper function to add all normal symbols to a DFA state
def add_normal_symbols(state: Dict[str, int], dst: int) -> None:
    for c in [';', ':', ',', '+', '-', '<', '[', ']', '(', ')', '{', '}']:
        state[c] = dst


# a helper function to add all special symbols like = and / to a DFA state
def add_special_symbols(state: Dict[str, int], dst: int) -> None:
    for c in ['/', '*', '=']:
        state[c] = dst


# a helper function to add all whitespace characters to a DFA state
def add_spaces(state: Dict[str, int], dst: int) -> None:
    for c in [' ', '\n', '\r', '\t', '\v', '\f']:
        state[c] = dst


# this function initialize the designed DFA
# the designed DFA is attached to the project as DFA.png
def initial_dfa() -> List[Dict[str, int]]:
    dfa_states = [defaultdict() for _ in range(22)]
    # STATE 0
    dfa_states[0] = defaultdict(lambda: None)
    add_nums(dfa_states[0], 1)
    add_letters(dfa_states[0], 3)
    add_normal_symbols(dfa_states[0], 5)
    add_spaces(dfa_states[0], 0)
    dfa_states[0]['='] = 6
    dfa_states[0]['/'] = 9
    dfa_states[0]['*'] = 18
    dfa_states[0]['$$'] = 21
    # STATE 1
    dfa_states[1] = defaultdict(lambda: None)
    add_nums(dfa_states[1], 1)
    add_normal_symbols(dfa_states[1], 2)
    add_special_symbols(dfa_states[1], 2)
    add_spaces(dfa_states[1], 2)
    # STATE 2 =
    dfa_states[2] = defaultdict(lambda: None)
    add_nums(dfa_states[2], 0)
    # STATE 3
    dfa_states[3] = defaultdict(lambda: None)
    add_nums(dfa_states[3], 3)
    add_letters(dfa_states[3], 3)
    add_normal_symbols(dfa_states[3], 4)
    add_special_symbols(dfa_states[3], 4)
    add_spaces(dfa_states[3], 4)
    # STATE 4
    dfa_states[4] = defaultdict(lambda: None)
    add_nums(dfa_states[4], 0)
    add_letters(dfa_states[4], 0)
    # STATE 5
    dfa_states[5] = defaultdict(lambda: None)
    add_normal_symbols(dfa_states[5], 0)
    # STATE 6
    dfa_states[6] = defaultdict(lambda: None)
    add_nums(dfa_states[6], 8)
    add_letters(dfa_states[6], 8)
    add_spaces(dfa_states[6], 8)
    add_normal_symbols(dfa_states[6], 8)
    dfa_states[6]['$$'] = 8
    dfa_states[6]['='] = 7
    # STATE 7
    dfa_states[7] = defaultdict(lambda: None)
    dfa_states[7]['='] = 0
    # STATE 8
    dfa_states[8] = defaultdict(lambda: None)
    dfa_states[8]['='] = 0
    # STATE 9
    dfa_states[9] = defaultdict(lambda: None)
    add_nums(dfa_states[9], 17)
    add_letters(dfa_states[9], 17)
    add_spaces(dfa_states[9], 17)
    add_normal_symbols(dfa_states[9], 17)
    dfa_states[9]['$$'] = 17
    dfa_states[9]['/'] = 14
    dfa_states[9]['*'] = 10
    # STATE 10
    dfa_states[10] = defaultdict(lambda: 10)
    dfa_states[10]['*'] = 11
    # STATE 11
    dfa_states[11] = defaultdict(lambda: 12)
    dfa_states[11]['/'] = 13
    # STATE 12
    dfa_states[12] = defaultdict(lambda: None)
    dfa_states[12]['*'] = 10
    # STATE 13
    dfa_states[13] = defaultdict(lambda: None)
    dfa_states[13]['/'] = 0
    # STATE 14
    dfa_states[14] = defaultdict(lambda: 14)
    dfa_states[14]['$$'] = 15
    dfa_states[14]['\n'] = 16
    # STATE 15
    dfa_states[15] = defaultdict(lambda: None)
    dfa_states[15]['$$'] = 0
    # STATE 16
    dfa_states[16] = defaultdict(lambda: None)
    dfa_states[16]['\n'] = 0
    # STATE 17
    dfa_states[17] = defaultdict(lambda: None)
    dfa_states[17]['/'] = 0
    # STATE 18
    dfa_states[18] = defaultdict(lambda: 20)
    dfa_states[18]['/'] = 19
    # STATE 19
    dfa_states[19] = defaultdict(lambda: None)
    dfa_states[19]['/'] = 0
    # STATE 20
    dfa_states[20] = defaultdict(lambda: None)
    dfa_states[20]['*'] = 0

    return dfa_states


# the next 5 functions are implemented just for more flexibility


def number_token(lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> str:
    return 'NUM'


def symbol_token(lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> str:
    return 'SYMBOL'


def comment_token(lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> str:
    return 'COMMENT'


def unmatched_token(lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> str:
    return 'Unmatched comment'


def eof_token(lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> str:
    return '$$'


# this function determines how each state affects the lexer pointer (how much should we backtrack)
def get_back_points() -> List[int]:
    return [0, 0, 2, 0, 2, 1, 0, 1, 2, 0, 0, 0, 2, 1, 0, 1, 1, 2, 0, 1, 2, 0]


class DFA:

    def __init__(self) -> None:
        self.goals = self.get_dfa_goals()    # DFA goals
        self.states = initial_dfa()     # DFA states
        self.current_state = 0          # DFA current state which is zero
        self.back_point = get_back_points()     # DFA backtrack amounts for each state
        self.variable_counter = 96

    # this function determines the DFA goal states
    # each goal maps to a function which returns its token type like KEYWORD, NUM or Unmatched comment
    def get_dfa_goals(self) -> Dict[int, Callable[[str, Dict[str, Tuple[str, int, int]]], str]]:
        goals = dict()
        goals[2] = number_token
        goals[4] = self.keyword_id_token
        goals[5] = symbol_token
        goals[7] = symbol_token
        goals[8] = symbol_token
        goals[13] = comment_token
        goals[15] = comment_token
        goals[16] = comment_token
        goals[17] = symbol_token
        goals[19] = unmatched_token
        goals[20] = symbol_token
        goals[21] = eof_token
        return goals

    def find_addr(self, lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> int:
        if lexeme not in symbols:
            self.variable_counter += 4
            symbols[lexeme] = ('ID', self.variable_counter, 1)
        return symbols[lexeme][1]

    def keyword_id_token(self, lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> str:
        if lexeme not in symbols:
            self.variable_counter += 4
            symbols[lexeme] = ('ID', self.variable_counter, 1)
        return symbols[lexeme][0]

    def set_size(self, lexeme: str, size: int, symbols: Dict[str, Tuple[str, int, int]]) -> None:
        symbols[lexeme] = (symbols[lexeme][0], symbols[lexeme][1], size)
        self.variable_counter += (size-1)*4

    # this function gets a character and move towards states in the DFA
    def change_state(self, c: str, lexeme: str, symbols: Dict[str, Tuple[str, int, int]]) -> Tuple[str, int, bool]:
        if c == '$$':
            if self.current_state == 1:     # we have a number as the last token
                return 'NUM', 0, True
            elif self.current_state == 3:   # we have a keyword or id as the last token
                return self.keyword_id_token(lexeme, symbols), 0, True
            elif 10 <= self.current_state <= 12:    # we have an unclosed comment
                return 'Unclosed comment', 0, True
        if self.states[self.current_state][c] is None:  # if we reached an unexpected character
            if self.current_state == 1:
                self.current_state = 0
                return 'Invalid number', 0, True    # if we were reading a NUM, return Invalid number error
            self.current_state = 0
            return 'Invalid input', 0, True         # else, return an Invalid input error
        self.current_state = self.states[self.current_state][c]     # update the current state
        if self.current_state in self.goals:        # if we have reached a goal, return its token
            return self.goals[self.current_state](lexeme[:len(lexeme)-self.back_point[self.current_state]+1], symbols), self.back_point[self.current_state], self.current_state == 0
        return '', self.back_point[self.current_state], self.current_state == 0     # else, return an empty string as token
