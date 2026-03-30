"""
Testes para Análise Semântica
========================
"""

import unittest
from src.semantic.analyzer import SemanticAnalyzer
from src.semantic.symbol_table import SymbolTable
from src.semantic.type_checker import TypeChecker
from src.exceptions import SemanticError


class TestSymbolTable(unittest.TestCase):
    """Testes da tabela de símbolos."""
    
    def setUp(self):
        self.symbol_table = SymbolTable()
    
    def test_declare_and_lookup(self):
        """Testa declaração e procura de símbolo."""
        self.symbol_table.declare('X', 'INTEGER')
        symbol = self.symbol_table.lookup('X')
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.name, 'X')
        self.assertEqual(symbol.type_name, 'INTEGER')
    
    def test_duplicate_declaration(self):
        """Testa que não é permitida declaração duplicada."""
        self.symbol_table.declare('X', 'INTEGER')
        with self.assertRaises(SemanticError):
            self.symbol_table.declare('X', 'REAL')
    
    def test_scope_management(self):
        """Testa gerenciamento de escopos."""
        # Escopo global
        self.symbol_table.declare('X', 'INTEGER')
        
        # Novo escopo
        self.symbol_table.push_scope()
        self.symbol_table.declare('Y', 'REAL')
        
        # X deve estar visível
        self.assertIsNotNone(self.symbol_table.lookup('X'))
        self.assertIsNotNone(self.symbol_table.lookup('Y'))
        
        # Fechar escopo
        self.symbol_table.pop_scope()
        
        # Y não deve estar mais visível
        self.assertIsNotNone(self.symbol_table.lookup('X'))
        self.assertIsNone(self.symbol_table.lookup('Y'))


class TestTypeChecker(unittest.TestCase):
    """Testes do verificador de tipos."""
    
    def test_numeric_types(self):
        """Testa funções de verificação de tipos."""
        self.assertTrue(TypeChecker.is_numeric('INTEGER'))
        self.assertTrue(TypeChecker.is_numeric('REAL'))
        self.assertTrue(TypeChecker.is_numeric('COMPLEX'))
        self.assertFalse(TypeChecker.is_numeric('LOGICAL'))
    
    def test_coercion(self):
        """Testa coerção de tipos."""
        # INTEGER para REAL é válido
        self.assertTrue(TypeChecker.can_coerce('INTEGER', 'REAL'))
        # REAL para COMPLEX é válido
        self.assertTrue(TypeChecker.can_coerce('REAL', 'COMPLEX'))
        # REAL para INTEGER não é válido
        self.assertFalse(TypeChecker.can_coerce('REAL', 'INTEGER'))
    
    def test_result_type(self):
        """Testa determinação de tipo resultado."""
        # INTEGER + INTEGER = INTEGER
        result = TypeChecker.get_result_type('INTEGER', 'INTEGER', '+')
        self.assertEqual(result, 'INTEGER')
        
        # INTEGER + REAL = REAL
        result = TypeChecker.get_result_type('INTEGER', 'REAL', '+')
        self.assertEqual(result, 'REAL')
        
        # REAL .LT. REAL = LOGICAL
        result = TypeChecker.get_result_type('REAL', 'REAL', '.LT.')
        self.assertEqual(result, 'LOGICAL')


class TestSemanticAnalyzer(unittest.TestCase):
    """Testes do analisador semântico."""
    
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
    
    def test_undeclared_variable(self):
        """Testa detecção de variável não declarada."""
        # TODO: Implementar quando AST estiver pronto
        pass


if __name__ == "__main__":
    unittest.main()
