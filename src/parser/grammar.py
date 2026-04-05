"""
Definição da Gramática Fortran 77
=================================

Define a gramática BNF do Fortran 77 para referência.
Utilizada como especificação pelo parser (ply.yacc).
"""

# GRAMÁTICA FORTRAN 77 - FORMATO EBNF

GRAMMAR = """

# Programa e Unidades

program         : 'PROGRAM' IDENTIFIER
                  declarations statements 'END'
                | 'PROGRAM' IDENTIFIER  
                  declarations statements subprograms 'END'

subprograms     : subprogram
                | subprograms subprogram

subprogram      : function_def
                | subroutine_def

function_def    : type_spec 'FUNCTION' IDENTIFIER '(' param_list ')'
                  declarations statements 'END'

subroutine_def  : 'SUBROUTINE' IDENTIFIER '(' param_list ')'
                  declarations statements 'END'

param_list      : IDENTIFIER
                | param_list ',' IDENTIFIER
                | /* empty */

# Declarações

declarations    : declaration
                | declarations declaration
                | /* empty */

declaration     : type_spec var_list
                | 'DIMENSION' array_list
                | 'PARAMETER' '(' param_assign_list ')'

type_spec       : 'INTEGER'
                | 'REAL'
                | 'LOGICAL'
                | 'CHARACTER' dimension_opt
                | 'COMPLEX'

var_list        : var_decl
                | var_list ',' var_decl

var_decl        : IDENTIFIER
                | IDENTIFIER '(' dimension_list ')'
                | IDENTIFIER '=' expression

array_list      : IDENTIFIER '(' dimension_list ')'
                | array_list ',' IDENTIFIER '(' dimension_list ')'

dimension_list  : expression ':' expression
                | dimension_list ',' expression ':' expression
                | expression
                | dimension_list ',' expression

# Instruções

statements      : statement
                | statements statement
                | /* empty */

statement       : label_opt simple_statement
                | label_opt control_statement

label_opt       : INTEGER ':'
                | /* empty */

simple_statement: assignment
                | read_stmt
                | print_stmt
                | write_stmt
                | call_stmt
                | 'CONTINUE'
                | 'RETURN'
                | 'GOTO' INTEGER
                | 'STOP'

control_statement: if_stmt
                 | do_stmt

assignment      : IDENTIFIER '=' expression
                | IDENTIFIER '(' subscript_list ')' '=' expression

read_stmt       : 'READ' '(' io_spec ')' io_list
                | 'READ' '(' io_spec ')' 
                | 'READ' '*' io_list
                | 'READ' '*'

print_stmt      : 'PRINT' '*' expr_list
                | 'PRINT' '*'
                | 'PRINT' format_spec expr_list

write_stmt      : 'WRITE' '(' io_spec ')' expr_list
                | 'WRITE' '(' io_spec ')'

call_stmt       : 'CALL' IDENTIFIER
                | 'CALL' IDENTIFIER '(' expr_list ')'

io_spec         : '*'
                | IDENTIFIER
                | io_spec ',' INTEGER
                | io_spec ',' IDENTIFIER

io_list         : io_item
                | io_list ',' io_item
                | /* empty */

io_item         : IDENTIFIER
                | IDENTIFIER '(' subscript_list ')'

subscript_list  : expression
                | subscript_list ',' expression

expr_list       : expression
                | expr_list ',' expression
                | /* empty */

if_stmt         : 'IF' '(' expression ')' 'THEN'
                  statements
                  elseif_list
                  else_opt
                  'ENDIF'

elseif_list     : elseif_clause
                | elseif_list elseif_clause
                | /* empty */

elseif_clause   : 'ELSEIF' '(' expression ')' 'THEN' statements

else_opt        : 'ELSE' statements
                | /* empty */

do_stmt         : 'DO' label_opt IDENTIFIER '=' expression ',' expression step_opt
                  statements
                  label_opt 'CONTINUE'
                | 'DO' label_opt IDENTIFIER '=' expression ',' expression step_opt
                  statements
                  'ENDDO'

step_opt        : ',' expression
                | /* empty */

# Expressões

expression      : or_expr

or_expr         : and_expr
                | or_expr '.OR.' and_expr

and_expr        : not_expr
                | and_expr '.AND.' not_expr

not_expr        : rel_expr
                | '.NOT.' rel_expr

rel_expr        : add_expr
                | rel_expr rel_op add_expr

rel_op          : '.LT.'
                | '.LE.'
                | '.GT.'
                | '.GE.'
                | '.EQ.'
                | '.NE.'

add_expr        : mul_expr
                | add_expr '+' mul_expr
                | add_expr '-' mul_expr

mul_expr        : pow_expr
                | mul_expr '*' pow_expr
                | mul_expr '/' pow_expr

pow_expr        : unary_expr
                | pow_expr '**' unary_expr

unary_expr      : primary
                | '+' unary_expr
                | '-' unary_expr

primary         : INTEGER_LIT
                | REAL_LIT
                | STRING_LIT
                | LOGICAL_LIT
                | IDENTIFIER
                | IDENTIFIER '(' expr_list ')'
                | IDENTIFIER '(' subscript_list ')'
                | '(' expression ')'
                | binary_function

binary_function : 'MOD' '(' expression ',' expression ')'
                | 'MAX' '(' expr_list ')'
                | 'MIN' '(' expr_list ')'
                | 'ABS' '(' expression ')'
                | 'SQRT' '(' expression ')'
                | 'SIN' '(' expression ')'
                | 'COS' '(' expression ')'
                | 'EXP' '(' expression ')'
                | 'LOG' '(' expression ')'
                | 'INT' '(' expression ')'
                | 'REAL' '(' expression ')'
                | 'NINT' '(' expression ')'

# Terminais

IDENTIFIER      : letra (letra | digito | '_')*
INTEGER_LIT     : digito+
REAL_LIT        : digito+ '.' digito*
                | digito* '.' digito+
                | (digito+ | digito+ '.' digito* | digito* '.' digito+) 'E' ('+' | '-')? digito+
STRING_LIT      : '\'' (.)*? '\''
LOGICAL_LIT     : '.TRUE.' | '.FALSE.'

"""

# Precedência dos Operadores (da menor para maior)
PRECEDENCE = (
    ('left', 'OR'), # .OR. tem menor precedência que .AND.
    ('left', 'AND'), # .AND. tem menor precedência que .NOT.
    ('left', 'NOT'), # .NOT. tem menor precedência que os relacionais
    ('left', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'), # .LT., .LE., .GT., .GE., .EQ., .NE. têm menor precedência que adição/subtração
    ('left', 'PLUS', 'MINUS'), # + e - têm menor precedência que multiplicação/divisão
    ('left', 'MULTIPLY', 'DIVIDE'), # * e / têm menor precedência que potência
    ('right', 'UMINUS', 'UNOT'), # Operadores unários (negativo e .NOT.) têm maior precedência que os binários, mas menor que ** (potência)
    ('right', 'POWER'), # ** tem maior precedência que unários
)
