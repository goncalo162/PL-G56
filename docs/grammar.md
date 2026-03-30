# Gramática Fortran 77

## Formato EBNF Simplificado

```ebnf
program        ::= 'PROGRAM' IDENTIFIER decl_list stmt_list 'END'
                 | 'PROGRAM' IDENTIFIER decl_list stmt_list subprogram_list 'END'

decl_list      ::= decl_list declaration
                 | ε

declaration    ::= type_spec IDENTIFIER array_spec
                 | type_spec IDENTIFIER '=' expr

type_spec      ::= 'INTEGER'
                 | 'REAL'
                 | 'LOGICAL'
                 | 'CHARACTER'
                 | 'COMPLEX'

array_spec     ::= ε
                 | '(' dim_list ')'

stmt_list      ::= stmt_list statement
                 | ε

statement      ::= assignment
                 | if_statement
                 | do_loop
                 | goto_statement
                 | read_statement
                 | print_statement
                 | call_statement
                 | continue_statement
                 | label ':' statement

assignment     ::= IDENTIFIER '=' expr

if_statement   ::= 'IF' '(' expr ')' 'THEN' stmt_list 'ENDIF'
                 | 'IF' '(' expr ')' 'THEN' stmt_list elif_part else_part 'ENDIF'

elif_part      ::= 'ELSEIF' '(' expr ')' 'THEN' stmt_list elif_part
                 | ε

else_part      ::= 'ELSE' stmt_list
                 | ε

do_loop        ::= 'DO' label IDENTIFIER '=' expr ',' expr do_body label 'CONTINUE'
                 | 'DO' label IDENTIFIER '=' expr ',' expr ',' expr do_body 'ENDDO'

do_body        ::= stmt_list

goto_statement ::= 'GOTO' NUMBER

read_statement ::= 'READ' '*' id_list
                 | 'READ' '(' unit_spec ')' id_list

print_statement::= 'PRINT' '*' expr_list
                 | 'PRINT' format_spec expr_list

expr           ::= or_expr

or_expr        ::= or_expr '.OR.' and_expr
                 | and_expr

and_expr       ::= and_expr '.AND.' rel_expr
                 | rel_expr

rel_expr       ::= rel_expr rel_op add_expr
                 | add_expr

rel_op         ::= '.LT.' | '.LE.' | '.GT.' | '.GE.' | '.EQ.' | '.NE.'

add_expr       ::= add_expr '+' mul_expr
                 | add_expr '-' mul_expr
                 | mul_expr

mul_expr       ::= mul_expr '*' pow_expr
                 | mul_expr '/' pow_expr
                 | pow_expr

pow_expr       ::= pow_expr '**' unary_expr
                 | unary_expr

unary_expr     ::= '-' unary_expr
                 | '.NOT.' unary_expr
                 | primary

primary        ::= NUMBER
                 | STRING
                 | IDENTIFIER
                 | IDENTIFIER '[' expr_list ']'
                 | function_call
                 | '(' expr ')'

function_call  ::= IDENTIFIER '(' expr_list ')'

expr_list      ::= expr_list ',' expr
                 | expr
                 | ε
```

## Precedência de Operadores

(da menor para a maior precedência)

1. `.OR.`
2. `.AND.`
3. `.NOT.`
4. Operadores relacionais (`.LT.`, `.LE.`, etc)
5. `+`, `-` (aditivos)
6. `*`, `/` (multiplicativos)
7. `**` (potência)
8. Unário `-`

## Exemplos de Expressões Válidas

- `A + B * C` → `A + (B * C)`
- `X .LT. 10 .AND. Y .GT. 5`
- `.NOT. FLAG`
- `2 ** 10 - 1` → `(2 ** 10) - 1`
- `MOD(N, 2) .EQ. 0`

## Construções Especiais

### DO Loop com Label

```fortran
DO 10 I = 1, N
    ...
10 CONTINUE
```

Label permite `GOTO` para dentro e fora do loop.

### Arrays

```fortran
INTEGER MATRIZ(10, 5)
REAL VETOR(100)
```

Declaração: `IDENTIFIER(dimension_list)`
Acesso: `MATRIZ(I, J)`

### Atribuição com Labels

```fortran
20  IF (X .LT. 100) THEN
        X = X + 1
        GOTO 20
    ENDIF
```

## Palavras-Chave Reservadas

Ver `src/config.py` para lista completa.

Principais:
- Tipos: `INTEGER`, `REAL`, `LOGICAL`, `CHARACTER`, `COMPLEX`
- Estrutura: `PROGRAM`, `END`, `SUBROUTINE`, `FUNCTION`
- Controle: `IF`, `THEN`, `ELSE`, `ENDIF`, `DO`, `CONTINUE`, `GOTO`
- I/O: `READ`, `WRITE`, `PRINT`, `FORMAT`
