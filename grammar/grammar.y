%token NUM
%token ID
%start program
%%
program: declaration_list
;
declaration_list: declaration_list declaration
| declaration
;
declaration: var_declaration 
| fun_declaration 
;
var_declaration: type_specifier ID ';' 
| type_specifier ID '[' p_num NUM ']' ';'
;
type_specifier: "int"
| "void"
;
fun_declaration: type_specifier ID '(' params ')' compound_stmt
;
params: param_list
| "void"
;
param_list: param_list ',' param
| param
;
param: type_specifier p_id ID
| type_specifier p_id ID '[' ']'
;
compound_stmt: '{' local_declarations statement_list '}'
;
local_declarations: local_declarations var_declaration
| /* epsilon */
;
statement_list: statement_list statement
| /* epsilon */
;
statement: expression_stmt
| compound_stmt
| selection_stmt
| iteration_stmt
| return_stmt
| switch_stmt
| output_stmt
;
expression_stmt: expression ';'
| "break" ';'
| ';'
;
selection_stmt: "if" '(' expression ')' save statement "endif"
| "if" '(' expression ')' save statement save_jpf "else" statement "endif" 
;
iteration_stmt: p_size "while" label '(' expression ')' save statement
;
return_stmt: "return" ';'
| "return" expression ';'
;
switch_stmt: p_size "switch" '(' expression ')' '{' case_stmts default_stmt '}'
;
case_stmts: case_stmts case_stmt
| /* epsilon */
;
case_stmt: "case" p_num NUM case_save ':' statement_list
;
default_stmt: "default" ':' statement_list
| /* epsilon */
;
output_stmt: "output" '(' expression ')' ';'
;
expression: var '=' expression
| simple_expression
;
var: p_id ID
| p_id ID '[' expression ']'
;
simple_expression: additive_expression relop additive_expression
| additive_expression
;
relop: '<'
| "=="
;
additive_expression: additive_expression addop term
| term
;
addop: '+'
| '-'
;
term: term mulop factor
| factor
;
mulop: '*'
| '/'
;
factor: '(' expression ')'
| var
| call
| p_num NUM
;
call: p_id ID '(' args ')'
;
args: arg_list
| /* epsilon */
;
arg_list: arg_list ',' expression
| expression
;
p_id: /* epsilon */
;
p_num: /* epsilon */
;
p_size: /* epsilon */
;
save: /* epsilon */
;
label: /* epsilon */
;
save_jpf: /* epsilon */
;
case_save: /* epsilon */
;
%%