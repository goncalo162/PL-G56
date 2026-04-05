"""
Analisador Sintático (Parser)
==============================

Implementa o parser usando ply.yacc para construir a Árvore Sintática Abstrata (AST).

Sintaxe das Regras de Gramática (BNF em PLY):
----------------------------------------------
O parser utiliza a documentação das funções (`docstrings`) para definir
as regras de produção da gramática. As regras seguem a forma:

    '''nome_da_regra : TOKEN1 TOKEN2 ...
                     | TOKEN3 ...'''

- O argumento `p` representa os elementos da produção reconhecida no momento (redução/shift).
- `p[0]` guarda o valor ou o nó a passar para o nível de cima (que consumiu esta regra).
- `p[1]`, `p[2]`, etc. correspondem ao valor (ou cadeia resolvida) no lado direito, da esquerda para a direita.

Uso:
    from src.parser.parser import Parser
    parser = Parser()
    ast = parser.parse(tokens)
"""

import ply.yacc as yacc

from src.exceptions import ParserError
from src.ast.nodes import (
    Program,
    VariableDeclaration,
    FunctionDeclaration,
    BinaryOp,
    UnaryOp,
    Identifier,
    Literal,
    Assignment,
    IfStatement,
    DoLoop,
    GotoStatement,
    ReadStatement,
    PrintStatement
)
from .grammar import PRECEDENCE 


class Parser:
    """
    Analisador sintático para Fortran 77.
    
    Constrói a árvore sintática abstrata (AST) a partir de tokens (recebidos do lexer).
    Utiliza análise bottom-up (shift-reduce) com base na especificação.
    """
    
    def __init__(self):
        """Inicializa o parser associando o contexto (classe actual)."""
        if not hasattr(self, 'parser') or self.parser is None:
            self.parser = yacc.yacc(module=self)
            
    # Definição da precedência importada para resolver os Shift/Reduce conflicts
    precedence = PRECEDENCE

    # ====================================================
    # Regras de Estrutura Inicial
    # ====================================================

    def p_empty(self, p):
        '''empty :'''
        # Regra vazia (epsilon), frequentemente utilizada quando declarações são opcionais.
        pass

    def p_program(self, p):
        '''program : PROGRAM IDENTIFIER declarations statements END'''
        # Nó raiz da árvore. Apanha o nome (p[2]), as declarações e instruções e envolve-os.
        p[0] = Program(name=p[2], declarations=p[3], statements=p[4])

    # ====================================================
    # Declarações
    # ====================================================

    def p_declarations(self, p):
        '''declarations : declarations declaration
                        | empty'''
        # Constroi listas de declarações recursivamente.
        if len(p) == 3:
            p[0] = (p[1] or []) + p[2]
        else:
            p[0] = []

    def p_declaration(self, p):
        '''declaration : type_spec var_list'''
        # Mapeia multiplas variáveis definidas numa mesma linha para nós independentes (ex: INTEGER A,B).
        type_name = p[1]
        p[0] = [VariableDeclaration(name=var_name, type_name=type_name) for var_name in p[2]]

    def p_type_spec(self, p):
        '''type_spec : INTEGER
                     | REAL
                     | LOGICAL
                     | CHARACTER
                     | COMPLEX'''
        # Regressa imediatamente o nome literal do tipo de variável.
        p[0] = p[1]

    def p_var_list(self, p):
        '''var_list : var_list COMMA IDENTIFIER
                    | IDENTIFIER'''
        # Constroi a lista de nomes puros de identificadores (string) separados por vírgula.
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    # ====================================================
    # Instruções (Statements)
    # ====================================================

    def p_statements(self, p):
        '''statements : statements statement
                      | empty'''
        # Acumulador recursivo das instruções (statements) dentro do corpo da execução.
        if len(p) == 3 and p[2] is not None:
            p[0] = (p[1] or []) + [p[2]]
        else:
            p[0] = []

    def p_statement(self, p):
        '''statement : assignment
                     | if_stmt
                     | do_stmt
                     | print_stmt
                     | read_stmt'''
        # Delega os statements concretos numa estrutura da AST correspondente.
        p[0] = p[1]

    def p_assignment(self, p):
        '''assignment : IDENTIFIER ASSIGN expression'''
        # Constrói o nó de atribuição recebendo do lado esquerdo um identificador e à direita uma operação/expressão.
        p[0] = Assignment(target=Identifier(name=p[1]), value=p[3])

    def p_if_stmt_basic(self, p):
        '''if_stmt : IF LPAREN expression RPAREN THEN statements ENDIF'''
        # Bloco de condição IF THEN com o body correspondente.
        p[0] = IfStatement(condition=p[3], then_body=p[6], else_body=[])

    def p_if_stmt_else(self, p):
        '''if_stmt : IF LPAREN expression RPAREN THEN statements ELSE statements ENDIF'''
        # Bloco condicional cobrindo tanto o cenário IF THEn e a cláusula ELSE.
        p[0] = IfStatement(condition=p[3], then_body=p[6], else_body=p[8])

    def p_do_stmt(self, p):
        '''do_stmt : DO IDENTIFIER ASSIGN expression COMMA expression statements ENDDO'''
        # Exemplo simples de construção DO sem step explícito (usa valor de passo default no lexer ou checker semântico)
        p[0] = DoLoop(variable=Identifier(name=p[2]), start=p[4], end=p[6], body=p[7])

    def p_print_stmt(self, p):
        '''print_stmt : PRINT MULTIPLY COMMA expr_list
                      | PRINT MULTIPLY expr_list'''
        # Declara a presença do output standard de forma explícita com as expressões agregadas.
        if len(p) == 5:
            p[0] = PrintStatement(expressions=p[4])
        else:
            p[0] = PrintStatement(expressions=p[3])

    def p_read_stmt(self, p):
        '''read_stmt : READ MULTIPLY COMMA var_list_id'''
        # Operador read para ler sequencialmente identificadores (Input padrão em Fortran `READ *, a, b`).
        p[0] = ReadStatement(unit=Literal(value='*', type_name='CHARACTER'), variables=p[4])
        
    def p_var_list_id(self, p):
        '''var_list_id : var_list_id COMMA IDENTIFIER
                       | IDENTIFIER'''
        # Subregra para ler var_list de identificadores mas gerar nós AST do tipo Identifier de caras (para READ).
        if len(p) == 4:
            p[0] = p[1] + [Identifier(name=p[3])]
        else:
            p[0] = [Identifier(name=p[1])]

    # ====================================================
    # Expressões e Coleções (Aritmética e Lógica)
    # ====================================================

    def p_expr_list(self, p):
        '''expr_list : expr_list COMMA expression
                     | expression'''
        # Lista agregadora de expressões usada tipicamente para invocar Print ou functions parameters.
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_expression_binop(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression MULTIPLY expression
                      | expression DIVIDE expression
                      | expression POWER expression
                      | expression LT expression
                      | expression LE expression
                      | expression GT expression
                      | expression GE expression
                      | expression EQ expression
                      | expression NE expression
                      | expression AND expression
                      | expression OR expression'''
        # Engloba todos os operadores Lógicos (E), Relacionais e Matemáticos transformando nos nós de operação Binária
        p[0] = BinaryOp(left=p[1], operator=p[2], right=p[3])

    def p_expression_unary(self, p):
        '''expression : PLUS expression %prec UMINUS
                      | MINUS expression %prec UMINUS
                      | NOT expression %prec UNOT'''
        # Operações unárias prioritárias contornando os operadores de soma, dif e disjunções
        p[0] = UnaryOp(operator=p[1], operand=p[2])
        
    def p_expression_group(self, p):
        '''expression : LPAREN expression RPAREN'''
        # Trata o invólucro de precedência usando parêntesis repassando de imediato a expressão interpretada.
        p[0] = p[2]
        
    def p_expression_literal(self, p):
        '''expression : INTEGER_LITERAL
                      | REAL_LITERAL
                      | STRING_LITERAL
                      | LOGICAL_LITERAL'''
        # Transforma o valor primitivo na classe AST Literal. Adicionalmente tentamos associar se foi do Lexer.
        type_map = {
            'INTEGER_LITERAL': 'INTEGER',
            'REAL_LITERAL': 'REAL',
            'STRING_LITERAL': 'CHARACTER',
            'LOGICAL_LITERAL': 'LOGICAL'
        }
        token_type = p.slice[1].type
        p[0] = Literal(value=p[1], type_name=type_map.get(token_type, 'UNKNOWN'))
        
    def p_expression_identifier(self, p):
        '''expression : IDENTIFIER'''
        # Folha que resolve qualquer referência a variável ou acesso numa estrutura.
        p[0] = Identifier(name=p[1])
    
    # ====================================================
    # Gestão de Erros / Entrada de Parsing
    # ====================================================

    def p_error(self, p):
        """Função chamada implicitamente para capturar parsing mal sucedido."""
        if p:
            raise ParserError(f"Erro sintático perto do token '{p.value}' (tipo: {p.type}) na linha {getattr(p, 'lineno', '?')}")
        else:
            raise ParserError("Erro sintático: fim inesperado do input (EOF)")

    def parse(self, tokens: list) -> Program:
        """
        Ponto inicial de Parsing que delega o lexer e inicia o shift/reduce.
        
        Args:
            tokens: A lista objectos lexer ou um wrapper.
            
        Returns:
            Program: Um pointer correspondente ao topo / raiz da sintaxe lida.
            
        Raises:
            ParserError: Quando e caso o yacc devolva falha na associação ou consumimento do código.
        """
        return self.parser.parse(lexer=tokens)
