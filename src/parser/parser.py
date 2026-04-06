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
    PrintStatement,
    CallStatement,
    ReturnStatement,
    ContinueStatement,
    FunctionCall,
    ArrayAccess
)
from .grammar import PRECEDENCE
from src.lexer.tokens import TokenType
from src.config import KEYWORDS


class Parser:
    """
    Analisador sintático para Fortran 77.
    
    Constrói a árvore sintática abstrata (AST) a partir de tokens (recebidos do lexer).
    Utiliza análise bottom-up (shift-reduce) com base na especificação.
    """
    
    # Lista de tokens necessária para o PLY yacc
    tokens = [token.name for token in TokenType] + list(KEYWORDS)
    
    # Definição da precedência importada para resolver os Shift/Reduce conflicts
    precedence = PRECEDENCE
    
    # Símbolo inicial da gramática
    start = 'program'
    
    def __init__(self):
        """Inicializa o parser associando o contexto (classe actual)."""
        # Cria o parser PLY apenas uma vez, mantendo-o no estado do objeto.
        if not hasattr(self, 'parser') or self.parser is None:
            self.parser = yacc.yacc(module=self)

    # ====================================================
    # Regras de Estrutura Inicial
    # ====================================================

    def p_empty(self, p):
        '''empty :'''
        # Regra vazia (epsilon), frequentemente utilizada quando declarações são opcionais.
        pass

    def p_program(self, p):
        '''program : PROGRAM IDENTIFIER declarations statements END
                   | PROGRAM IDENTIFIER declarations statements subprograms END'''
        # Nó raiz da árvore. Apanha o nome (p[2]), as declarações e instruções e envolve-os.
        subs = p[5] if len(p) == 6 and type(p[5]) == list else []
        p[0] = Program(name=p[2], declarations=p[3], statements=p[4], subprograms=subs)

    # ====================================================
    # Subprogramas
    # ====================================================

    def p_subprograms(self, p):
        '''subprograms : subprogram
                       | subprograms subprogram'''
        if len(p) == 2:
            p[0] = [p[1]]
        elif p[2]:
            p[0] = p[1] + [p[2]]

    def p_subprogram(self, p):
        '''subprogram : function_def
                      | subroutine_def'''
        p[0] = p[1]

    def p_function_def(self, p):
        '''function_def : type_spec FUNCTION IDENTIFIER LPAREN param_list RPAREN declarations statements END'''
        p[0] = FunctionDeclaration(
            name=p[3],
            return_type=p[1],
            parameters=[VariableDeclaration(name=arg, type_name="UNKNOWN") for arg in p[5]],
            body=(p[7] or []) + (p[8] or [])
        )

    def p_subroutine_def(self, p):
        '''subroutine_def : SUBROUTINE IDENTIFIER LPAREN param_list RPAREN declarations statements END
                          | SUBROUTINE IDENTIFIER declarations statements END'''
        if len(p) == 9:
            params = [VariableDeclaration(name=arg, type_name="UNKNOWN") for arg in p[4]]
            decls = p[6]
            stmts = p[7]
        else:
            params = []
            decls = p[3]
            stmts = p[4]
            
        p[0] = FunctionDeclaration(
            name=p[2],
            return_type="VOID",
            parameters=params,
            body=(decls or []) + (stmts or [])
        )

    def p_param_list(self, p):
        '''param_list : IDENTIFIER
                      | param_list COMMA IDENTIFIER
                      | empty'''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        else:
            p[0] = p[1] + [p[3]]

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
        '''statement : label_opt simple_statement
                     | label_opt control_statement'''
        # Delega os statements concretos numa estrutura da AST correspondente.
        # Por enquanto não guardamos a label no objeto da AST, exceto DoLoop / Goto.
        if p[1] is not None and isinstance(p[2], ContinueStatement):
            # Continue guardariamos a label para resolução de ciclos? 
            # O DO loop consume statements até encontrar NUMBER CONTINUE
            pass
        p[0] = p[2]

    def p_label_opt(self, p):
        '''label_opt : 
                     | empty'''
        # Captura instruções rotuladas no estilo Fortran de labels numéricos opcionais.
        p[0] = p[1]

    def p_simple_statement(self, p):
        '''simple_statement : assignment
                            | read_stmt
                            | print_stmt
                            | write_stmt
                            | call_stmt
                            | continue_stmt
                            | goto_stmt
                            | return_stmt
                            | stop_stmt'''        # Reconhece um statement simples sem controlo de fluxo.
        p[0] = p[1]

    def p_control_statement(self, p):
        '''control_statement : if_stmt
                             | do_stmt'''
        # Agrupa instruções de controlo de fluxo para serem processadas igualmente.
        p[0] = p[1]

    def p_write_stmt(self, p):
        '''write_stmt : WRITE LPAREN io_spec RPAREN expr_list
                      | WRITE LPAREN io_spec RPAREN'''
        # Trata WRITE como impressão de expressões em output, com ou sem lista.
        if len(p) == 6:
            p[0] = PrintStatement(expressions=p[5])
        else:
            p[0] = PrintStatement(expressions=[])

    def p_call_stmt(self, p):
        '''call_stmt : CALL IDENTIFIER
                     | CALL IDENTIFIER LPAREN expr_list RPAREN'''
        # Constrói um nó de chamada de subrotina com argumentos opcionais.
        if len(p) == 3:
            p[0] = CallStatement(subroutine=p[2], arguments=[])
        else:
            p[0] = CallStatement(subroutine=p[2], arguments=p[4])

    def p_continue_stmt(self, p):
        '''continue_stmt : CONTINUE'''
        # Representa um marcador CONTINUE de loop Fortran.
        p[0] = ContinueStatement()

    def p_goto_stmt(self, p):
        '''goto_stmt : GOTO INTEGER_LITERAL'''
        # Cria um GOTO apontando para um label numérico.
        p[0] = GotoStatement(label=p[2])

    def p_return_stmt(self, p):
        '''return_stmt : RETURN'''
        # Normaliza RETURN como um statement de término de função/subprograma.
        p[0] = ReturnStatement()

    def p_stop_stmt(self, p):
        '''stop_stmt : STOP'''
        # STOP é um comando de término de execução em Fortran.
        p[0] = ReturnStatement()

    def p_assignment(self, p):
        '''assignment : IDENTIFIER ASSIGN expression
                      | IDENTIFIER LPAREN subscript_list RPAREN ASSIGN expression'''
        if len(p) == 4:
            p[0] = Assignment(target=Identifier(name=p[1]), value=p[3])
        else:
            # Array assignment
            target = ArrayAccess(name=p[1], indices=p[3])
            p[0] = Assignment(target=target, value=p[6])

    def p_subscript_list(self, p):
        '''subscript_list : expression
                          | subscript_list COMMA expression'''
        # Agrupamento de índices para acesso a arrays.
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_if_stmt_basic(self, p):
        '''if_stmt : IF LPAREN expression RPAREN THEN statements ENDIF'''
        # Formato básico IF-THEN sem ELSE.
        p[0] = IfStatement(condition=p[3], then_body=p[6], else_body=[])

    def p_if_stmt_else(self, p):
        '''if_stmt : IF LPAREN expression RPAREN THEN statements ELSE statements ENDIF'''
        # IF-THEN com bloco ELSE explícito.
        p[0] = IfStatement(condition=p[3], then_body=p[6], else_body=p[8])

    def p_if_stmt_elseif(self, p):
        '''if_stmt : IF LPAREN expression RPAREN THEN statements elseif_list else_opt ENDIF'''
        # IF-THEN com múltiplos ELSEIF e eventual ELSE.
        p[0] = IfStatement(condition=p[3], then_body=p[6], else_body=p[8], elif_parts=p[7])

    def p_elseif_list(self, p):
        '''elseif_list : elseif_clause
                       | elseif_list elseif_clause
                       | empty'''
        # Lista de cláusulas ELSEIF opcional, acumulada recursivamente.
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        else:
            p[0] = p[1] + [p[2]]

    def p_elseif_clause(self, p):
        '''elseif_clause : ELSEIF LPAREN expression RPAREN THEN statements'''
        # Regra de cada ELSEIF individual com condição e corpo de statements.
        p[0] = (p[3], p[6])

    def p_else_opt(self, p):
        '''else_opt : ELSE statements
                    | empty'''
        # Bloco ELSE opcional associado ao IF.
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = []

    def p_do_stmt(self, p):
        '''do_stmt : DO IDENTIFIER ASSIGN expression COMMA expression statements ENDDO
                   | DO  IDENTIFIER ASSIGN expression COMMA expression statements  CONTINUE'''
        # Reconhece ciclos DO sem e com label de continuação.
        if len(p) == 9:
            # No DO label
            p[0] = DoLoop(variable=Identifier(name=p[2]), start=p[4], end=p[6], body=p[7])
        else:
            # DO label
            # do_stmt : DO NUMBER ID = exp , exp do_body NUMBER CONTINUE
            p[0] = DoLoop(variable=Identifier(name=p[3]), start=p[5], end=p[7], label=p[2], body=p[8])

    def p_print_stmt(self, p):
        '''print_stmt : PRINT MULTIPLY COMMA expr_list
                      | PRINT MULTIPLY expr_list
                      | PRINT MULTIPLY'''
        # Constrói instruções PRINT com lista de expressões opcional.
        if len(p) == 5:
            p[0] = PrintStatement(expressions=p[4])
        elif len(p) == 4:
            p[0] = PrintStatement(expressions=p[3])
        else:
            p[0] = PrintStatement(expressions=[])

    def p_read_stmt(self, p):
        '''read_stmt : READ MULTIPLY COMMA io_list
                     | READ MULTIPLY io_list
                     | READ LPAREN io_spec RPAREN io_list'''
        # Constrói instruções READ com unidade e lista de variáveis.
        if len(p) >= 5:
            io_list = p[4] if p[2] == '*' else p[5]
            p[0] = ReadStatement(unit=Literal(value='*', type_name='CHARACTER'), variables=io_list)
        else:
            p[0] = ReadStatement(unit=Literal(value='*', type_name='CHARACTER'), variables=p[3])

    def p_io_spec(self, p):
        '''io_spec : MULTIPLY
                   | IDENTIFIER
                   | io_spec COMMA 
                   | io_spec COMMA IDENTIFIER'''
        # Permite especificar arquivo/unidade de I/O com opções de múltiplos campos.
        p[0] = p[1]

    def p_io_list(self, p):
        '''io_list : io_item
                   | io_list COMMA io_item'''
        # Lista de itens I/O para READ/WRITE.
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_io_item(self, p):
        '''io_item : IDENTIFIER
                   | IDENTIFIER LPAREN subscript_list RPAREN'''
        if len(p) == 2:
            p[0] = Identifier(name=p[1])
        else:
            p[0] = ArrayAccess(name=p[1], indices=p[3])

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
        
    def p_expression_function_call(self, p):
        '''expression : IDENTIFIER LPAREN expr_list RPAREN'''
        # Chamada de função como expressão
        p[0] = FunctionCall(function_name=p[1], arguments=p[3])
        
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

    # ===== Regras adicionais da gramática =====

    def p_var_decl(self, p):
        '''var_decl : IDENTIFIER
                    | IDENTIFIER LPAREN dimension_list RPAREN
                    | IDENTIFIER ASSIGN expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 5:
            # Array declaration
            p[0] = {'name': p[1], 'dims': p[3]}
        else:
            # Assignment in declaration
            p[0] = {'name': p[1], 'value': p[3]}

    def p_array_list(self, p):
        '''array_list : IDENTIFIER LPAREN dimension_list RPAREN
                      | array_list COMMA IDENTIFIER LPAREN dimension_list RPAREN'''
        if len(p) == 5:
            p[0] = [{'name': p[1], 'dims': p[3]}]
        else:
            p[0] = p[1] + [{'name': p[3], 'dims': p[5]}]

    def p_dimension_list(self, p):
        '''dimension_list : expression COLON expression
                          | dimension_list COMMA expression COLON expression
                          | expression
                          | dimension_list COMMA expression'''
        # Retorna lista de tuplas (start, end) ou valores únicos
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 4:
            p[0] = p[1] + [p[3]]
        elif len(p) == 6:
            # (start:end)
            p[0] = p[1] + [(p[3], p[5])]
        else:
            p[0] = [(p[1], p[3])]

    def p_param_assign_list(self, p):
        '''param_assign_list : IDENTIFIER ASSIGN expression
                             | param_assign_list COMMA IDENTIFIER ASSIGN expression'''
        if len(p) == 4:
            p[0] = [{p[1]: p[3]}]
        else:
            p[0] = p[1] + [{p[3]: p[5]}]

    def p_format_spec(self, p):
        '''format_spec : MULTIPLY
                       | STRING_LITERAL'''
        p[0] = p[1]

    def p_step_opt(self, p):
        '''step_opt : COMMA expression
                    | empty'''
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None

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
