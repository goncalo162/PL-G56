"""
Definição da Gramática Fortran 77
=================================

Define a gramática BNF efetivamente aceite pelo parser (ply.yacc).
O parser importa deste módulo a tabela PRECEDENCE; a string GRAMMAR serve
como referência sincronizada com as regras `p_*` de `parser.py`.

CONCEITOS IMPORTANTES
=====================

1. ARRAYS e DIMENSION:
   - DIMENSION é uma declaração separada (artefato histórico) para especificar dimensões
   - Exemplo Fortran:
       INTEGER A
       DIMENSION A(10, 5)          ! Declara array bidimensional separadamente
   - Forma moderna (equivalente):
       INTEGER A(10, 5)            ! Inline na declaração de tipo
   - No parser: ambas são tratadas equivalentemente
   - dimensions: lista de tuplas [(lower, upper)] em symbol_table

2. PARAMETERS vs CONSTANTS:
   - is_parameter: True se é um parâmetro formal de função/subrotina (argumento)
     Ex: SUBROUTINE FOO(X, Y) — X e Y têm is_parameter=True
   - is_constant: True se é uma CONSTANTE PARAMETER Fortran 77 (imutável em compilação)
     Ex: PARAMETER (PI=3.14159) — PI tem is_constant=True
   - Ambos podem coexistir: uma constante PARAMETER pode ser passada como argumento
     Ex: CALL BAR(PI) — PI tem ambos is_constant=True e is_parameter=True (no contexto da chamada)
"""

# GRAMÁTICA FORTRAN 77 - FORMATO EBNF

GRAMMAR = """

# Programa e Unidades

program         : 'PROGRAM' IDENTIFIER declarations statements 'END' subprograms_opt

subprograms_opt : subprograms
                | /* empty */

subprograms     : subprogram
                | subprograms subprogram

subprogram      : function_def
                | subroutine_def

function_def    : type_spec 'FUNCTION' IDENTIFIER '(' param_list ')'
                  declarations statements 'END'

subroutine_def  : 'SUBROUTINE' IDENTIFIER '(' param_list ')'
                  declarations statements 'END'
                | 'SUBROUTINE' IDENTIFIER
                  declarations statements 'END'

param_list      : IDENTIFIER
                | param_list ',' IDENTIFIER
                | /* empty */

# Declarações

declarations    : declaration
                | declarations declaration
                | /* empty */

# declaration: apenas tipo_base + lista_variáveis
# Arrays podem ser declarados inline: INTEGER A(10, 5)
# ou separadamente com DIMENSION (não suportado nesta versão do compilador)
declaration     : type_spec var_list

type_spec       : 'INTEGER'
                | 'REAL'
                | 'LOGICAL'
                | 'CHARACTER'
                | 'COMPLEX'

var_list        : var_decl
                | var_list ',' var_decl

# var_decl: variável simples, array ou inicialização
# IDENTIFIER               : simples variável (ex: X)
# IDENTIFIER(dimension_list): array (ex: A(10, 5) ou B(1:100, 1:50))
# IDENTIFIER=expression    : inicialização (ex: X=3.14)
var_decl        : IDENTIFIER
                | IDENTIFIER '(' dimension_list ')'
                | IDENTIFIER '=' expression

# dimension_list: especifica limites de cada dimensão
# Formato 1: expression ':' expression  — limites explícitos (ex: 1:10, 0:99)
# Formato 2: expression                 — apenas tamanho, começa em 1 (ex: 10 equivale a 1:10)
# Múltiplas dimensões separadas por vírgula
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

label_opt       : INTEGER_LITERAL
                | LABEL
                | /* empty */

simple_statement : assignment
                | read_stmt
                | print_stmt
                | write_stmt
                | call_stmt
                | continue_stmt
                | goto_stmt
                | return_stmt
                | stop_stmt

control_statement : if_stmt
                 | do_stmt

continue_stmt   : 'CONTINUE'

goto_stmt       : 'GOTO' INTEGER_LITERAL
                | 'GOTO' LABEL

return_stmt     : 'RETURN'

stop_stmt       : 'STOP'

assignment      : IDENTIFIER '=' expression
                | IDENTIFIER '(' subscript_list ')' '=' expression

read_stmt       : 'READ' '(' io_spec ')' io_list
                | 'READ' '(' io_spec ')' 
                | 'READ' '*' io_list
                | 'READ' '*'

print_stmt      : 'PRINT' '*' expr_list
                | 'PRINT' '*' ',' expr_list
                | 'PRINT' '*'

write_stmt      : 'WRITE' '(' io_spec ')' expr_list
                | 'WRITE' '(' io_spec ')'

call_stmt       : 'CALL' IDENTIFIER
                | 'CALL' IDENTIFIER '(' expr_list ')'

io_spec         : '*'
                | IDENTIFIER
                | io_spec ','
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

if_stmt         : 'IF' '(' expression ')' 'THEN' statements 'ENDIF'
                | 'IF' '(' expression ')' 'THEN' statements 'ELSE' statements 'ENDIF'
                | 'IF' '(' expression ')' 'THEN' statements elseif_list else_opt 'ENDIF'

elseif_list     : elseif_clause
                | elseif_list elseif_clause
                | /* empty */

elseif_clause   : 'ELSEIF' '(' expression ')' 'THEN' statements

else_opt        : 'ELSE' statements
                | /* empty */

do_stmt         : 'DO' IDENTIFIER '=' expression ',' expression
                  statements
                  'ENDDO'
                | 'DO' LABEL IDENTIFIER '=' expression ',' expression
                  statements
                  'ENDDO'
                | 'DO' INTEGER_LITERAL IDENTIFIER '=' expression ',' expression
                  statements
                  'ENDDO'
                | 'DO' IDENTIFIER '=' expression ',' expression
                  statements
                  label_opt 'CONTINUE'
                | 'DO' IDENTIFIER '=' expression ',' expression
                  statements
                  INTEGER_LITERAL 'CONTINUE'
                | 'DO' LABEL IDENTIFIER '=' expression ',' expression
                  statements
                  LABEL 'CONTINUE'
                | 'DO' LABEL IDENTIFIER '=' expression ',' expression
                  statements
                  INTEGER_LITERAL 'CONTINUE'
                | 'DO' INTEGER_LITERAL IDENTIFIER '=' expression ',' expression
                  statements
                  LABEL 'CONTINUE'
                | 'DO' INTEGER_LITERAL IDENTIFIER '=' expression ',' expression
                  statements
                  INTEGER_LITERAL 'CONTINUE'

# Expressões (sem precedência explícita aqui — veja tabela PRECEDENCE abaixo)

expression      : expression '+' expression
                | expression '-' expression
                | expression '*' expression
                | expression '/' expression
                | expression '**' expression
                | expression '.LT.' expression
                | expression '.LE.' expression
                | expression '.GT.' expression
                | expression '.GE.' expression
                | expression '.EQ.' expression
                | expression '.NE.' expression
                | expression '.AND.' expression
                | expression '.OR.' expression
                | '+' expression
                | '-' expression
                | '.NOT.' expression
                | '(' expression ')'
                | function_call
                | INTEGER_LITERAL
                | REAL_LITERAL
                | STRING_LITERAL
                | LOGICAL_LITERAL
                | IDENTIFIER
                | IDENTIFIER '(' subscript_list ')'

# function_call: chamadas de funções definidas pelo utilizador e funções intrínsecas Fortran
# MOD/MAX/MIN/ABS/SQRT/SIN/COS/EXP/LOG/INT/REAL/NINT são funções built-in
function_call   : IDENTIFIER '(' expr_list ')'
                | 'MOD' '(' expression ',' expression ')'
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

# Terminais (tokens)

IDENTIFIER      : letra (letra | digito | '_')*
INTEGER_LITERAL : digito+
REAL_LITERAL    : digito+ '.' digito*
                | digito* '.' digito+
                | (digito+ | digito+ '.' digito* | digito* '.' digito+) 'E' ('+' | '-')? digito+
STRING_LITERAL  : '\'' (.)*? '\''
LOGICAL_LITERAL : '.TRUE.' | '.FALSE.'

LABEL           : INTEGER_LITERAL (com contexto apropriado)

"""

# Precedência dos Operadores (da menor para maior), usada por parser.py
# Lista ordenada: primeira = menor precedência, última = maior precedência
PRECEDENCE = (
    ('left', 'OR'),                            # .OR. tem menor precedência que .AND.
    ('left', 'AND'),                           # .AND. tem menor precedência que .NOT.
    ('left', 'NOT'),                           # .NOT. tem menor precedência que os relacionais
    ('left', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),  # Operadores relacionais têm menor precedência que +/-
    ('left', 'PLUS', 'MINUS'),                 # +/- têm menor precedência que *,/
    ('left', 'CONCAT'),                        # Concatenação de strings
    ('left', 'MULTIPLY', 'DIVIDE'),            # *,/ têm menor precedência que ** (potência)
    ('right', 'UMINUS', 'UNOT'),               # Operadores unários (-x, .NOT. x) — right associative
    ('right', 'POWER'),                        # ** tem maior precedência que unários — right associative
)
