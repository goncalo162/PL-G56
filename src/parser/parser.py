"""
Analisador Sintático (Parser)
==============================

Implementa o parser usando ply.yacc para construir a AST.

Uso:
    from src.parser.parser import Parser
    parser = Parser()
    ast = parser.parse(tokens)
"""

from src.exceptions import ParserError
from src.ast.nodes import Program
from .grammar import PRECEDENCE 


class Parser:
    """
    Analisador sintático para Fortran 77.
    
    Constrói a árvore sintática abstrata (AST) a partir de tokens.
    Utiliza ply.yacc para análise bottom-up (shift-reduce).
    """
    
    def __init__(self):
        """Inicializa o parser."""
        # TODO: Instanciar a classe do parser
        # self.parser = yacc.yacc(module=self)
        pass
    
    # Definição explícita da precedência dos operadores matemáticos e lógicos (importada de grammar.py)
    precedence = PRECEDENCE

    # TODO 2: Criar as funções de produção (Gramática)
    # tens de migrar de "parser que só reconhece" para "parser que constrói uma AST estruturada baseada em Classes".
    # Exemplo para a raiz (Program):
    # def p_program(self, p):
    #     '''program : statement_list'''
    #     p[0] = Program(statements=p[1]) # Objecto da AST
    
    # TODO 3: Criar regras de expressões e associar nós da AST (AST Node Classes)
    # As funções do yacc devem extrair os valores consumidos e ligá-los às tuas classes AST.
    # Exemplo:
    # def p_expression_binop(self, p):
    #     '''expression : expression PLUS expression
    #                   | expression MINUS expression'''
    #     p[0] = BinaryOpNode(left=p[1], op=p[2], right=p[3])
    
    # TODO 4: Função para lidar com erros sintáticos na gramática (Recuperação ou lançamento de exceções)
    # def p_error(self, p):
    #     raise ParserError("Syntax error at ...")

    def parse(self, tokens: list) -> Program:
        """
        Analisa tokens e constrói a AST.
        
        Args:
            tokens: Lista de objetos Token
            
        Returns:
            ASTNode: Raiz da árvore sintática (usually Program)
            
        Raises:
            ParserError: Se encontrar erro sintático
        """
        # TODO: Implementar parser com ply.yacc
        pass
