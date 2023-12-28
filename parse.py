import json
from typing import Tuple, List
import anytree

from lexer import Lexer
from code_generator import CodeGenerator


class Parser:
    # initialize the parser
    def __init__(self, input_file_name: str) -> None:
        table_file = open('grammar/table.json')
        table = json.load(table_file)
        self.valid_tokens = {'NUM', 'ID', 'KEYWORD', 'SYMBOL', '$$'}    # valid tokens
        self.non_terminals = set(table['non_terminals'])                # grammar non-terminals
        self.follow = table['follow']                                   # follow sets
        self.grammar = table['grammar']                                 # the grammar itself
        self.parse_table = table['parse_table']                         # parse table
        self.lexer = Lexer(input_file_name)                             # connection between parser and lexer
        self.current_token = '', '', -1                                 # current token
        self.stack = []                                                 # stack for LR(1) parsing
        self.syntax_errors = []                                         # list of syntax errors
        self.has_parse_tree = True                                      # parse will be successful or not
        self.code_generator = CodeGenerator(self.lexer)

    # this function calls get_next_token in lexer until we reach a valid token (not a lexical error or COMMENT)
    def update_token(self) -> None:
        self.current_token = self.lexer.get_next_token()
        while not self.current_token[0] in self.valid_tokens:
            self.current_token = self.lexer.get_next_token()

    # some tokens are called with their lexeme (like int) but some aren't (like NUM)...
    def get_value_of_token(self) -> str:
        if self.current_token[0] == 'KEYWORD' or self.current_token[0] == 'SYMBOL':
            return self.current_token[1]
        if self.current_token[0] == '$$':
            return '$'
        return self.current_token[0]

    # which action should we make? we will find out after looking up the parse table
    def get_current_action(self) -> str:
        token = self.get_value_of_token()
        if self.parse_table[str(self.stack[-1][1])].get(token) is None:
            return ''       # if the cell is empty, return an empty string
        return self.parse_table[str(self.stack[-1][1])][token]

    # this function handles the shift action
    def shift(self, state: int) -> None:
        if self.current_token[0] == '$$':
            self.stack.append((anytree.Node('$'), state))
        else:
            self.stack.append((anytree.Node(f'({self.current_token[0]}, {self.current_token[1]})'), state))
        self.update_token()

    # this function handles the reduce action
    def reduce(self, state: str) -> None:
        children = []
        if self.grammar[state][2] == 'epsilon':
            children.append(anytree.Node('epsilon'))
        else:
            for _ in range(len(self.grammar[state]) - 2):
                children.append(self.stack.pop()[0])
        terminal = anytree.Node(self.grammar[state][0], children=children[::-1])
        new_state = int(self.parse_table[str(self.stack[-1][1])][self.grammar[state][0]].split('_')[1])
        self.stack.append((terminal, new_state))
        self.code_generator.code_gen(int(state), self.current_token[1])

    # this function accepts the current parsing
    def accept(self) -> None:
        last = self.stack.pop()         # join the ($) token to program node
        anytree.Node(last[0].name, parent=self.stack[-1][0])

    # this function does the action we should make in each step
    def take_action(self, current_action: str) -> bool:
        if current_action == '':        # if current action is empty, we should enter the panic mode
            return self.panic_recovery()
        if current_action == 'accept':  # if current action is accept, accept the parsing
            self.accept()
            return False            # return False so the parsing won't get further more
        current_action = current_action.split('_')
        if current_action[0] == 'shift':
            self.shift(int(current_action[1]))
        else:
            self.reduce(current_action[1])
        return True                 # return True so we can continue parsing

    # checks if a state has a goto to a non-terminal or not
    def has_goto(self, state: int) -> bool:
        for k, v in self.parse_table[str(state)].items():
            if k in self.non_terminals:
                return True
        return False

    # checks if with current token, state can follow any non-terminal
    def can_follow(self, state: int) -> Tuple[str, bool]:
        token = self.get_value_of_token()
        for k, v in sorted(self.parse_table[str(state)].items()):
            if k in self.non_terminals and token in self.follow[k]:
                return k, True
        return '', False

    # pop the stack until we find a state which has goto (Step 1 of Panic Mode)
    def find_goto(self) -> None:
        while not self.has_goto(self.stack[-1][1]):
            popped = self.stack.pop()
            self.syntax_errors.append(f'syntax error , discarded {popped[0].name} from stack')

    # discard the tokens until we find a token which can follow a non-terminal (Step 2 and 3 of Panic Mode)
    def find_follower(self) -> bool:
        can_follow = self.can_follow(self.stack[-1][1])
        while not can_follow[1]:                    # STEP 2
            if self.current_token[0] == '$$':       # when we discard $ token, we halt the parsing
                self.syntax_errors.append(f'#{self.current_token[2] + 1} : syntax error , Unexpected EOF')
                self.has_parse_tree = False         # we don't have a PARSE TREE
                return False
            self.syntax_errors.append(f'#{self.current_token[2] + 1} : syntax error , discarded {self.current_token[1]} from input')
            self.update_token()
            can_follow = self.can_follow(self.stack[-1][1])
        # STEP 3: stack the new non-terminal
        self.syntax_errors.append(f'#{self.current_token[2] + 1} : syntax error , missing {can_follow[0]}')
        new_state = int(self.parse_table[str(self.stack[-1][1])][can_follow[0]].split('_')[1])
        self.stack.append((anytree.Node(can_follow[0]), new_state))
        return True             # parsing should be continued

    # panic mode recovery
    def panic_recovery(self) -> bool:
        self.syntax_errors.append(f'#{self.current_token[2]+1} : syntax error , illegal {self.current_token[1]}')
        self.update_token()
        self.find_goto()
        return self.find_follower()

    # parse the program and get the parse tree
    def get_parse_tree(self) -> anytree.Node:
        self.stack = [(anytree.Node(''), 0)]
        self.update_token()
        res = self.take_action(self.get_current_action())
        while res:      # while parsing is continued, we take an action
            res = self.take_action(self.get_current_action())
        return self.stack[-1][0] if self.has_parse_tree else anytree.Node('')

    # get all the syntax errors of the written program
    def get_syntax_errors(self) -> List[str]:
        return self.syntax_errors
