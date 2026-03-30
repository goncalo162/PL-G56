"""
Testes para Analisador Sintático
=================================
"""

import unittest
from src.parser.parser import Parser
from src.lexer.lexer import Lexer


class TestParserBasic(unittest.TestCase):
    """Testes básicos do parser."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def test_parse_simple_program(self):
        """Testa parsing de programa simples."""
        code = "PROGRAM TEST END"
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        self.assertIsNotNone(ast)
    
    def test_parse_declarations(self):
        """Testa parsing de declarações."""
        code = """PROGRAM TEST
        INTEGER X, Y
        END"""
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        self.assertIsNotNone(ast)


class TestParserExpressions(unittest.TestCase):
    """Testes de parsing de expressões."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def test_arithmetic_expression(self):
        """Testa parsing de expressões aritméticas."""
        code = """PROGRAM TEST
        INTEGER X
        X = 2 + 3 * 4
        END"""
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        self.assertIsNotNone(ast)
    
    def test_logical_expression(self):
        """Testa parsing de expressões lógicas."""
        code = """PROGRAM TEST
        LOGICAL X
        X = .TRUE. .AND. .FALSE.
        END"""
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        self.assertIsNotNone(ast)


class TestParserStatements(unittest.TestCase):
    """Testes de parsing de instruções."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def test_if_statement(self):
        """Testa parsing de IF-THEN-ELSE."""
        code = """PROGRAM TEST
        INTEGER X
        X = 5
        IF (X .GT. 0) THEN
            X = 1
        ENDIF
        END"""
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        self.assertIsNotNone(ast)
    
    def test_do_loop(self):
        """Testa parsing de DO loop."""
        code = """PROGRAM TEST
        INTEGER I, SUM
        SUM = 0
        DO 10 I = 1, 10
            SUM = SUM + I
        10 CONTINUE
        END"""
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        self.assertIsNotNone(ast)


if __name__ == "__main__":
    unittest.main()
