# Gramática Fortran 77

## Conceitos Importantes

### ARRAYS e DIMENSION

**DIMENSION** é uma declaração separada em Fortran 77 para especificar dimensões de arrays. É principalmente um artefato histórico do Fortran fixo-formato.

**Duas formas equivalentes:**

```fortran
! Forma 1: DIMENSION inline (moderna, recomendada)
INTEGER A(10, 5)              ! Array bidimensional 10×5
REAL B(100)                   ! Array unidimensional com 100 elementos

! Forma 2: DIMENSION separada (compatibilidade com código antigo)
INTEGER A
REAL B
DIMENSION A(10, 5), B(100)    ! Declaração separada
```

**No compilador:** Ambas são tratadas equivalentemente. A representação interna usa:
- `dimensions = [(1, 10), (1, 5)]` para array 10×5 (tuplas lower:upper por dimensão)

### PARAMETERS vs CONSTANTS

Dois conceitos **distintos** em Fortran 77:

| Atributo | Significado | Exemplo |
|----------|------------|---------|
| **`is_parameter`** | Parâmetro formal de função/subrotina (argumento) | `SUBROUTINE FOO(X, Y)` — X e Y são parâmetros |
| **`is_constant`** | Constante PARAMETER (imutável em compilação) | `PARAMETER (PI=3.14159)` — PI é constante |

**Exemplo mostrando ambos:**

```fortran
PROGRAM TEST
    REAL, PARAMETER :: PI = 3.14159    ! PI: is_constant=True
    CALL CALCULAR(PI)                  ! PI: is_parameter=True (argumento)
END

SUBROUTINE CALCULAR(VALOR)
    REAL VALOR                         ! VALOR: is_parameter=True (param. formal)
    PRINT *, VALOR * 2.0
END
```

Portanto, **ambos os flags podem coexistir** num símbolo.

## Formato EBNF 

### Programa e Unidades de Programa

```ebnf
program        ::= 'PROGRAM' IDENTIFIER declarations statements 'END' subprograms_opt

subprograms_opt ::= subprograms
                  | ε

subprograms    ::= subprogram
                 | subprograms subprogram

subprogram     ::= function_def
                 | subroutine_def

function_def   ::= type_spec 'FUNCTION' IDENTIFIER '(' param_list ')' 
                   declarations statements 'END'

subroutine_def ::= 'SUBROUTINE' IDENTIFIER '(' param_list ')' 
                   declarations statements 'END'
                 | 'SUBROUTINE' IDENTIFIER 
                   declarations statements 'END'

param_list     ::= IDENTIFIER
                 | param_list ',' IDENTIFIER
                 | ε
```

### Declarações

```ebnf
declarations   ::= declaration
                 | declarations declaration
                 | ε

declaration    ::= type_spec var_list

type_spec      ::= 'INTEGER'
                 | 'REAL'
                 | 'LOGICAL'
                 | 'CHARACTER'
                 | 'COMPLEX'

var_list       ::= var_decl
                 | var_list ',' var_decl

# var_decl: variável simples, array ou inicialização
# IDENTIFIER               : simples variável (ex: X)
# IDENTIFIER(dimension_list): array (ex: A(10, 5) ou B(1:100, 1:50))
# IDENTIFIER=expression    : inicialização (ex: X=3.14)
var_decl       ::= IDENTIFIER
                 | IDENTIFIER '(' dimension_list ')'
                 | IDENTIFIER '=' expression

# dimension_list: especifica limites de cada dimensão
# Formato 1: expr           — apenas tamanho, começa em 1 (ex: 10 = 1:10)
# Formato 2: expr ':' expr  — limites explícitos (ex: 1:10, 0:99)
# Múltiplas dimensões separadas por vírgula (ex: 10, 5 ou 1:10, 1:5)
dimension_list ::= expression
                 | dimension_list ',' expression
                 | expression ':' expression
                 | dimension_list ',' expression ':' expression
```

### Instruções

```ebnf
statements     ::= statement
                 | statements statement
                 | ε

statement      ::= label_opt simple_statement
                 | label_opt control_statement

label_opt      ::= INTEGER_LITERAL
                 | LABEL
                 | ε

simple_statement ::= assignment
                   | read_stmt
                   | print_stmt
                   | write_stmt
                   | call_stmt
                   | continue_stmt
                   | goto_stmt
                   | return_stmt
                   | stop_stmt

control_statement ::= if_stmt
                    | do_stmt

assignment     ::= IDENTIFIER '=' expression
                 | IDENTIFIER '(' subscript_list ')' '=' expression

read_stmt      ::= 'READ' '*' io_list
                 | 'READ' '*'
                 | 'READ' '(' io_spec ')' io_list
                 | 'READ' '(' io_spec ')'

print_stmt     ::= 'PRINT' '*' expr_list
                 | 'PRINT' '*' ',' expr_list
                 | 'PRINT' '*'

write_stmt     ::= 'WRITE' '(' io_spec ')' expr_list
                 | 'WRITE' '(' io_spec ')'

call_stmt      ::= 'CALL' IDENTIFIER
                 | 'CALL' IDENTIFIER '(' expr_list ')'

continue_stmt  ::= 'CONTINUE'

goto_stmt      ::= 'GOTO' INTEGER_LITERAL
                 | 'GOTO' LABEL

return_stmt    ::= 'RETURN'

stop_stmt      ::= 'STOP'

io_spec        ::= '*'
                 | IDENTIFIER
                 | io_spec ','
                 | io_spec ',' IDENTIFIER

io_list        ::= io_item
                 | io_list ',' io_item
                 | ε

io_item        ::= IDENTIFIER
                 | IDENTIFIER '(' subscript_list ')'

subscript_list ::= expression
                 | subscript_list ',' expression
```

### Instruções de Controlo de Fluxo

```ebnf
if_stmt        ::= 'IF' '(' expression ')' 'THEN' statements 'ENDIF'
                 | 'IF' '(' expression ')' 'THEN' statements 'ELSE' statements 'ENDIF'
                 | 'IF' '(' expression ')' 'THEN' statements elseif_list else_opt 'ENDIF'

elseif_list    ::= elseif_clause
                 | elseif_list elseif_clause
                 | ε

elseif_clause  ::= 'ELSEIF' '(' expression ')' 'THEN' statements

else_opt       ::= 'ELSE' statements
                 | ε

do_stmt        ::= 'DO' IDENTIFIER '=' expression ',' expression statements 'ENDDO'
                 | 'DO' LABEL IDENTIFIER '=' expression ',' expression statements 'ENDDO'
                 | 'DO' INTEGER_LITERAL IDENTIFIER '=' expression ',' expression statements 'ENDDO'
                 | 'DO' IDENTIFIER '=' expression ',' expression statements label_opt 'CONTINUE'
                 | 'DO' IDENTIFIER '=' expression ',' expression statements INTEGER_LITERAL 'CONTINUE'
                 | 'DO' LABEL IDENTIFIER '=' expression ',' expression statements LABEL 'CONTINUE'
                 | 'DO' LABEL IDENTIFIER '=' expression ',' expression statements INTEGER_LITERAL 'CONTINUE'
                 | 'DO' INTEGER_LITERAL IDENTIFIER '=' expression ',' expression statements LABEL 'CONTINUE'
                 | 'DO' INTEGER_LITERAL IDENTIFIER '=' expression ',' expression statements INTEGER_LITERAL 'CONTINUE'
```

### Expressões

```ebnf
expr_list      ::= expression
                 | expr_list ',' expression
                 | ε

expression     ::= expression '+' expression
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
                 | '+' expression %prec UMINUS
                 | '-' expression %prec UMINUS
                 | '.NOT.' expression %prec UNOT
                 | '(' expression ')'
                 | function_call
                 | INTEGER_LITERAL
                 | REAL_LITERAL
                 | STRING_LITERAL
                 | LOGICAL_LITERAL
                 | IDENTIFIER
                 | IDENTIFIER '(' subscript_list ')'

function_call  ::= IDENTIFIER '(' expr_list ')'
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
```

## Precedência de Operadores

(da menor para a maior precedência)

1. `.OR.` (Lógico OU)
2. `.AND.` (Lógico E)
3. `.NOT.` (Lógico NÃO)
4. Operadores relacionais: `.LT.` (menor), `.LE.` (menor ou igual), `.GT.` (maior), `.GE.` (maior ou igual), `.EQ.` (igual), `.NE.` (diferente)
5. `+`, `-` (adição e subtração)
6. `*`, `/` (multiplicação e divisão)
7. Operadores unários: `-` (negação), `+` (positivo), `.NOT.` (lógico)
8. `**` (potência, associatividade à direita)

**Nota**: A tabela acima reflete `PRECEDENCE` em `src/parser/grammar.py`. No parser atual, `**` tem precedência superior aos operadores unários.

## Exemplos de Expressões Válidas

```fortran
! Expressões aritméticas
A + B * C                ! → A + (B * C), multiplicação tem maior precedência
2 ** 10 - 1             ! → (2 ** 10) - 1, potência tem maior precedência
X / Y * Z               ! → (X / Y) * Z, mesma precedência, associatividade à esquerda

! Expressões lógicas
X .LT. 10 .AND. Y .GT. 5     ! Comparações são mais fracas que lógicos
.NOT. FLAG .OR. CONDITION    ! NOT tem maior precedência que OR

! Expressões mistas
A + B .LT. C * D        ! → (A + B) .LT. (C * D)
2 ** 3 + 4 * 5          ! → (2 ** 3) + (4 * 5) = 8 + 20 = 28

! Chamadas de função
MOD(N, 2) .EQ. 0        ! Função MOD retorna resto
SQRT(A ** 2 + B ** 2)   ! Raiz quadrada de expressão
MAX(X, Y, Z)            ! Máximo de lista de valores
```

## Construções Especiais

### DO Loop com Label e CONTINUE

O compilador suporta várias formas de ciclos DO:

```fortran
! Formato 1: Sem label, com ENDDO
DO I = 1, N
    X(I) = I * I
ENDDO

! Formato 2: Sem label de início, com label de fim e CONTINUE
DO I = 1, N
    X(I) = I * I
10 CONTINUE

! Formato 3: Com label de início numérico e ENDDO
DO 20 J = 1, M
    PRINT *, J
ENDDO

! Formato 4: Com labels de início e fim com CONTINUE
DO 30 K = 1, 10
    SUM = SUM + K
30 CONTINUE
```

**Nota importante**: O compilador **não suporta o passo (terceiro argumento) em DO**. Todos os ciclos têm incremento implícito de 1.

Labels permitem `GOTO` para dentro e fora do loop, facilitando transferência de controlo complexa (embora não recomendado em código moderno).

### Arrays Unidimensionais e Multidimensionais

```fortran
! Declaração unidimensional
INTEGER VETOR(100)
REAL MATRIZ(10, 5)          ! Bidimensional
CHARACTER STRINGS(20)       ! Array de strings

! Acesso
VALOR = VETOR(5)
ELEMENTO = MATRIZ(I, J)
```

Declaração: `type IDENTIFIER(dimension_list)`  
Acesso: `IDENTIFIER(subscript_list)`  
Dimensões podem ser escalares ou ranges (`:` for specification).

### Instruções Condicionais

```fortran
! IF simples
IF (X .LT. 100) THEN
    X = X + 1
ENDIF

! IF com ELSE
IF (A .EQ. 0) THEN
    B = 0
ELSE
    B = C / A
ENDIF

! IF com múltiplos ELSEIF
IF (GRADE .GE. 90) THEN
    PRINT *, 'A'
ELSEIF (GRADE .GE. 80) THEN
    PRINT *, 'B'
ELSEIF (GRADE .GE. 70) THEN
    PRINT *, 'C'
ELSE
    PRINT *, 'F'
ENDIF
```

### Subprogramas

Os subprogramas são reconhecidos depois do `END` do programa principal.

```fortran
PROGRAM MAIN
    INTEGER RESULTADO
    RESULTADO = QUADRADO(5)
    CALL IMPRIMIR('Ola')
END

! Função (retorna valor)
INTEGER FUNCTION QUADRADO(N)
    INTEGER N
    QUADRADO = N * N
    RETURN
END

! Subrotina (não retorna valor)
SUBROUTINE IMPRIMIR(MSG)
    CHARACTER MSG
    PRINT *, MSG
    RETURN
END
```

### Atribuição com Labels

```fortran
20  IF (X .LT. 100) THEN
        X = X + 1
        GOTO 20           ! Volta para label 20
    ENDIF
```

## Funções Integradas (Built-in Functions)

O compilador suporta as seguintes funções intrínsecas Fortran:

| Função | Argumento(s) | Retorna | Descrição |
|--------|--------------|---------|-----------|
| `MOD(a, b)` | 2 inteiros | inteiro | Resto da divisão |
| `ABS(x)` | número | mesmo tipo | Valor absoluto |
| `SQRT(x)` | real | real | Raiz quadrada |
| `SIN(x)` | real (radianos) | real | Seno |
| `COS(x)` | real (radianos) | real | Cosseno |
| `EXP(x)` | real | real | Exponencial (e^x) |
| `LOG(x)` | real positivo | real | Logaritmo natural |
| `INT(x)` | real | inteiro | Converte para inteiro (trunca) |
| `REAL(x)` | inteiro | real | Converte para real |
| `NINT(x)` | real | inteiro | Arredonda para inteiro mais próximo |
| `MAX(a, b, ...)` | 2 ou mais números | mesmo tipo | Máximo |
| `MIN(a, b, ...)` | 2 ou mais números | mesmo tipo | Mínimo |

## Palavras-Chave Reservadas

A gramática suportada pelo parser usa as seguintes palavras-chave (maiúsculas ou minúsculas):

### Estrutura de Programa
- `PROGRAM` – início de programa principal
- `END` – fim de programa/subprograma
- `SUBROUTINE` – definição de subrotina
- `FUNCTION` – definição de função
- `CALL` – chamada de subrotina
- `RETURN` – retorno de subprograma
- `STOP` – término de execução

### Declaração de Tipos
- `INTEGER` – tipo inteiro
- `REAL` – tipo real (ponto flutuante)
- `LOGICAL` – tipo booleano (verdadeiro/falso)
- `CHARACTER` – tipo caractere/string
- `COMPLEX` – tipo complexo

### Estruturas de Controlo de Fluxo
- `IF`, `THEN`, `ELSE`, `ELSEIF`, `ENDIF` – condicional
- `DO`, `ENDDO` – ciclo (loop)
- `CONTINUE` – marca de continuação (usado com labels)
- `GOTO` – salto incondicional para label
- `TRUE`, `FALSE` – literais booleanos

### I/O (Entrada/Saída)
- `READ` – leitura de dados
- `WRITE` – escrita de dados
- `PRINT` – impressão

### Funções Intrínsecas
- `MOD` – resto da divisão
- `ABS` – valor absoluto
- `MAX`, `MIN` – máximo e mínimo
- `SQRT` – raiz quadrada
- `SIN`, `COS` – trigonométricas
- `EXP`, `LOG` – exponencial e logaritmo
- `INT`, `REAL`, `NINT` – conversão de tipo

## Terminais (Tokens)

### Literais

```ebnf
INTEGER_LITERAL  ::= [0-9]+

REAL_LITERAL     ::= [0-9]+'.'[0-9]*
                   | [0-9]*'.'[0-9]+
                   | ([0-9]+'.'[0-9]* | [0-9]*'.'[0-9]+) 'E' [+-]? [0-9]+

STRING_LITERAL   ::= '\'' [^']*? '\''

LOGICAL_LITERAL  ::= '.TRUE.' | '.FALSE.'

IDENTIFIER       ::= [a-zA-Z][a-zA-Z0-9_]*
```

### Operadores e Símbolos

| Token | Significado |
|-------|-------------|
| `+` | Adição / Unário positivo |
| `-` | Subtração / Unário negativo |
| `*` | Multiplicação |
| `/` | Divisão |
| `**` | Potência |
| `=` | Atribuição |
| `.LT.` | Menor que (<) |
| `.LE.` | Menor ou igual (≤) |
| `.GT.` | Maior que (>) |
| `.GE.` | Maior ou igual (≥) |
| `.EQ.` | Igual (==) |
| `.NE.` | Diferente (!=) |
| `.AND.` | Lógico E |
| `.OR.` | Lógico OU |
| `.NOT.` | Lógico NÃO |
| `(` `)` | Parêntesis |
| `,` | Vírgula (separador) |
| `:` | Dois-pontos (intervalo ou especificador) |

## Restrições e Limitações

1. **DO Loop Step**: O compilador **não suporta o passo (step) em ciclos DO** (ex: `DO I = 1, 100, 2`). Apenas suporta incremento unitário (passo implícito de 1).

2. **Arrays Multidimensionais**: Arrays com 2 ou mais dimensões são reconhecidos pela gramática, mas a geração de código está otimizada principalmente para unidimensionais.

3. **Format Statements e File I/O**: `FORMAT`, `OPEN`, `CLOSE` e `REWIND` podem existir como palavras-chave do lexer, mas não têm regras sintáticas parseáveis nesta gramática.

4. **Rótulos Numéricos**: Labels são apenas números inteiros (ex: `10`, `20`, `100`), não strings.

5. **Colunas de Posição Fixa**: No formato `fixed`, as colunas têm significado especial:
   - Colunas 1-5: Labels
   - Coluna 6: Indicador de continuação
   - Colunas 7-72: Código
   - Coluna 73+: Ignorado (cartão ID Fortran histórico)

6. **Funções Intrínsecas**: Apenas as listadas na Secção de Funções Integradas são suportadas como intrínsecas. Chamadas com outro identificador podem ser parseadas como chamadas de função definida pelo utilizador.
