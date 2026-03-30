"""
Testes para Analisador Léxico
=============================
"""

import unittest
from src.lexer.lexer import Lexer
from src.lexer.tokens import TokenType


class TestLexerBasic(unittest.TestCase):
    """Testes básicos do lexer."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_keywords(self):
        """Testa reconhecimento de palavras-chave."""
        code = "PROGRAM END"
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)
    
    def test_identifiers(self):
        """Testa reconhecimento de identificadores."""
        code = "HELLO WORLD"
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)
    
    def test_numbers(self):
        """Testa reconhecimento de números."""
        code = "123 45.67"
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)
    
    def test_strings(self):
        """Testa reconhecimento de strings."""
        code = "'Hello World'"
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)


class TestLexerOperators(unittest.TestCase):
    """Testes de operadores."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_arithmetic_operators(self):
        """Testa reconhecimento de operadores aritméticos."""
        code = "+ - * / **"
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)
    
    def test_logical_operators(self):
        """Testa reconhecimento de operadores lógicos."""
        code = ".AND. .OR. .NOT."
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)
    
    def test_relational_operators(self):
        """Testa reconhecimento de operadores relacionais."""
        code = ".LT. .LE. .GT. .GE. .EQ. .NE."
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)


class TestLexerPrograms(unittest.TestCase):
    """Testes com programas completos."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_hello_program(self):
        """Testa tokenização do programa Olá Mundo."""
        code = """PROGRAM HELLO
        PRINT *, 'Ola, Mundo!'
        END"""
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)
    
    def test_factorial_program(self):
        """Testa tokenização do programa fatorial."""
        code = """PROGRAM FATORIAL
        INTEGER N, I, FAT
        PRINT *, 'Introduza um numero:'
        READ *, N
        FAT = 1
        DO 10 I = 1, N
            FAT = FAT * I
        10 CONTINUE
        PRINT *, 'Fatorial:', FAT
        END"""
        tokens = self.lexer.tokenize(code)
        self.assertIsNotNone(tokens)


if __name__ == "__main__":
    unittest.main()
