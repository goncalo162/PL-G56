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


class Parser:
    """
    Analisador sintático para Fortran 77.
    
    Constrói a árvore sintática abstrata (AST) a partir de tokens.
    Utiliza ply.yacc para análise bottom-up (shift-reduce).
    """
    
    def __init__(self):
        """Inicializa o parser."""
        # Será configurado com ply.yacc
        pass
    
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
