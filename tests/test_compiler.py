"""
Testes Unitários para o Compilador
===================================

Testes para cada fase do compilador.
"""

import unittest
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer


class TestLexer(unittest.TestCase):
    """Testes para o analisador léxico."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_simple_program(self):
        """Testa tokenização de programa simples."""
        code = """
        PROGRAM HELLO
        PRINT *, 'Ola, Mundo!'
        END
        """
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)


class TestParser(unittest.TestCase):
    """Testes para o analisador sintático."""
    
    def setUp(self):
        self.parser = Parser()


class TestSemanticAnalyzer(unittest.TestCase):
    """Testes para análise semântica."""
    
    def setUp(self):
        self.analyzer = SemanticAnalyzer()


if __name__ == "__main__":
    unittest.main()
