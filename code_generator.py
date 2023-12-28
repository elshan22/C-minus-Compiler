from lexer import Lexer


# determines the address type (implicit, explicit or immediate)
def get_str_val(item: list) -> str:
    return ('' if not item[1] else '#' if item[1] == 1 else '@') + str(item[0])


class CodeGenerator:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer          # lexer instance of the compiler
        self.program_block = [[None, None, None, None] for _ in range(100)]     # program block
        self.stack = []             # semantic stack
        self.breaks_link = []       # linked list used for implementation of breaks
        self.current_scope = 0      # scope counter
        self.program_counter = 0    # index of the current line of program block
        self.temp_id = 996          # temp ID
        self.funcs = {}             # code generator functions
        self.fill_funcs()
        self.token = ''             # next input called as current token

    # returns a temp register
    def get_temp(self) -> int:
        self.temp_id += 4
        return self.temp_id

    # determines which function should be called in each reduction
    def fill_funcs(self) -> None:
        self.funcs[7] = self.arr_declare
        self.funcs[29] = self.pop
        self.funcs[30] = self.save_break
        self.funcs[32] = self.jpf
        self.funcs[33] = self.endif
        self.funcs[34] = self.handle_while
        self.funcs[36] = self.pop
        self.funcs[37] = self.switch_jump
        self.funcs[40] = self.jpf
        self.funcs[43] = self.print_out
        self.funcs[44] = self.assign
        self.funcs[47] = self.arr_access
        self.funcs[48] = self.calc
        self.funcs[50] = self.less_than
        self.funcs[51] = self.equal
        self.funcs[52] = self.calc
        self.funcs[54] = self.plus
        self.funcs[55] = self.minus
        self.funcs[56] = self.calc
        self.funcs[58] = self.mul
        self.funcs[59] = self.div
        self.funcs[69] = self.push_id
        self.funcs[70] = self.push_num
        self.funcs[71] = self.push_size
        self.funcs[72] = self.save
        self.funcs[73] = self.label
        self.funcs[74] = self.save_jpf
        self.funcs[75] = self.case_save

    # code_gen just calls the given reduction function
    def code_gen(self, reduce_number: int, current_token: str) -> None:
        if reduce_number in self.funcs:
            self.token = current_token
            self.funcs[reduce_number]()

    # pops an element from stack (used for balancing the statements)
    def pop(self) -> None:
        self.stack.pop()

    # add a break address to the linked list
    def save_break(self) -> None:
        self.breaks_link.append((self.program_counter, self.current_scope))
        self.program_counter += 1

    # jump if false implementation
    def jpf(self) -> None:
        x = get_str_val(self.stack[-2])
        self.program_block[self.stack.pop()[0]] = ['JPF', x, self.program_counter, None]
        self.stack.pop()

    # used for jumping before entering the else
    def endif(self) -> None:
        self.program_block[self.stack.pop()[0]] = ['JP', self.program_counter, None, None]

    # handles the while jumps
    def handle_while(self) -> None:
        while self.breaks_link and self.breaks_link[-1][1] == self.current_scope:
            self.program_block[self.breaks_link.pop()[0]] = ['JP', self.program_counter+1, None, None]
        x = get_str_val(self.stack[-2])
        self.program_block[self.stack.pop()[0]] = ['JPF', x, self.program_counter+1, None]
        self.stack.pop()
        x = get_str_val(self.stack.pop())
        self.program_block[self.program_counter] = ['JP', x, None, None]
        self.program_counter += 1
        self.current_scope -= 1

    # print the value of top of the stack
    def print_out(self):
        x = get_str_val(self.stack.pop())
        self.program_block[self.program_counter] = ['PRINT', x, None, None]
        self.program_counter += 1

    # assign implementation
    def assign(self):
        x = get_str_val(self.stack.pop())
        y = get_str_val(self.stack[-1])
        self.program_block[self.program_counter] = ['ASSIGN', x, y, None]
        self.program_counter += 1

    # calculates an operational command (+, -, *, /, <, ==)
    def calc(self):
        op = self.stack[-2][0]
        t = self.get_temp()
        x = get_str_val(self.stack[-3])
        y = get_str_val(self.stack[-1])
        self.program_block[self.program_counter] = [op, x, y, t]
        self.program_counter += 1
        for i in range(3):
            self.stack.pop()
        self.stack.append((t, 0))

    # the next 6 functions push the used operand to the stack
    def less_than(self):
        self.stack.append(('LT', 0))

    def equal(self):
        self.stack.append(('EQ', 0))

    def plus(self):
        self.stack.append(('ADD', 0))

    def minus(self):
        self.stack.append(('SUB', 0))

    def mul(self):
        self.stack.append(('MULT', 0))

    def div(self):
        self.stack.append(('DIV', 0))

    # pushes the ID of the next input (token) to the stack
    def push_id(self):
        self.stack.append((self.lexer.DFA.find_addr(self.token, self.lexer.symbols), 0))

    # push a number to the stack
    def push_num(self):
        self.stack.append((int(self.token), 1))

    # indicates that we have entered a new scope
    def push_size(self):
        self.current_scope += 1

    # push the index and go to the next index
    def save(self):
        self.stack.append((self.program_counter, 0))
        self.program_counter += 1

    # just push the index
    def label(self):
        self.stack.append((self.program_counter, 0))

    # push the index and than jpf (used for if-else)
    def save_jpf(self):
        x = get_str_val(self.stack[-2])
        self.program_block[self.stack.pop()[0]] = ['JPF', x, self.program_counter+1, None]
        self.stack.pop()
        self.stack.append((self.program_counter, 0))
        self.program_counter += 1

    # push a comparing value of switch expression and case value to the stack
    def case_save(self):
        x = get_str_val(self.stack.pop())
        y = get_str_val(self.stack[-1])
        self.program_block[self.program_counter] = ['EQ', x, y, self.get_temp()]
        self.stack.append((self.program_block[self.program_counter][-1], 0))
        self.program_counter += 1
        self.save()

    # set size of the array
    def arr_declare(self):
        self.lexer.DFA.set_size(self.token, self.stack.pop()[0], self.lexer.symbols)

    # we should play with addresses, and we did that in this function
    def arr_access(self):
        t = self.get_temp()
        x = self.stack.pop()
        x = ('' if not x[1] else '#' if x[1] == 1 else '@') + str(x[0])
        self.program_block[self.program_counter] = ['MULT', x, '#4', t]
        x = self.stack.pop()
        x = ('' if not x[1] else '#' if x[1] == 1 else '@') + str(x[0])
        self.program_block[self.program_counter+1] = ['ADD', f'#{x}', t, t]
        self.stack.append((t, 2))
        self.program_counter += 2

    # filling out breaks which has occurred in the switch statements
    def switch_jump(self):
        while self.breaks_link and self.breaks_link[-1][1] == self.current_scope:
            self.program_block[self.breaks_link.pop()[0]] = ['JP', self.program_counter, None, None]
