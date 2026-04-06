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
    
    # =====================================================================
    # Testes de Declarações e Procura de Variáveis
    # =====================================================================
    
    def test_simple_declaration(self):
        """Testa declaração simples de variável."""
        from src.ast.nodes import Program, VariableDeclaration
        
        program = Program(
            name="test",
            declarations=[VariableDeclaration(name="X", type_name="INTEGER")],
            statements=[],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
        self.assertEqual(len(self.analyzer.errors), 0)
    
    def test_multiple_declarations(self):
        """Testa múltiplas declarações."""
        from src.ast.nodes import Program, VariableDeclaration
        
        program = Program(
            name="test",
            declarations=[
                VariableDeclaration(name="X", type_name="INTEGER"),
                VariableDeclaration(name="Y", type_name="REAL"),
                VariableDeclaration(name="Z", type_name="LOGICAL"),
            ],
            statements=[],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
    
    # =====================================================================
    # Testes de Tipos e Expressões
    # =====================================================================
    
    def test_integer_literal_type(self):
        """Testa tipo de literal inteiro."""
        from src.ast.nodes import Literal
        
        lit = Literal(value=42, type_name="INTEGER")
        lit.accept(self.analyzer)
        
        inferred_type = self.analyzer._get_type(lit)
        self.assertEqual(inferred_type, "INTEGER")
    
    def test_real_literal_type(self):
        """Testa tipo de literal real."""
        from src.ast.nodes import Literal
        
        lit = Literal(value=3.14, type_name="REAL")
        lit.accept(self.analyzer)
        
        inferred_type = self.analyzer._get_type(lit)
        self.assertEqual(inferred_type, "REAL")
    
    def test_integer_binary_operation(self):
        """Testa operação binária entre inteiros."""
        from src.ast.nodes import BinaryOp, Literal
        
        op = BinaryOp(
            left=Literal(value=1, type_name="INTEGER"),
            operator="+",
            right=Literal(value=2, type_name="INTEGER")
        )
        
        op.accept(self.analyzer)
        result_type = self.analyzer._get_type(op)
        self.assertEqual(result_type, "INTEGER")
    
    def test_integer_plus_real(self):
        """Testa INTEGER + REAL resulta em REAL."""
        from src.ast.nodes import BinaryOp, Literal
        
        op = BinaryOp(
            left=Literal(value=1, type_name="INTEGER"),
            operator="+",
            right=Literal(value=2.0, type_name="REAL")
        )
        
        op.accept(self.analyzer)
        result_type = self.analyzer._get_type(op)
        self.assertEqual(result_type, "REAL")
    
    def test_comparison_result_logical(self):
        """Testa que comparação resulta em LOGICAL."""
        from src.ast.nodes import BinaryOp, Literal
        
        op = BinaryOp(
            left=Literal(value=1, type_name="INTEGER"),
            operator=".LT.",
            right=Literal(value=2, type_name="INTEGER")
        )
        
        op.accept(self.analyzer)
        result_type = self.analyzer._get_type(op)
        self.assertEqual(result_type, "LOGICAL")
    
    def test_unary_plus(self):
        """Testa operação unária +."""
        from src.ast.nodes import UnaryOp, Literal
        
        op = UnaryOp(
            operator="+",
            operand=Literal(value=42, type_name="INTEGER")
        )
        
        op.accept(self.analyzer)
        result_type = self.analyzer._get_type(op)
        self.assertEqual(result_type, "INTEGER")
    
    def test_unary_minus(self):
        """Testa operação unária -."""
        from src.ast.nodes import UnaryOp, Literal
        
        op = UnaryOp(
            operator="-",
            operand=Literal(value=3.14, type_name="REAL")
        )
        
        op.accept(self.analyzer)
        result_type = self.analyzer._get_type(op)
        self.assertEqual(result_type, "REAL")
    
    def test_logical_not(self):
        """Testa operação unária .NOT."""
        from src.ast.nodes import UnaryOp, Literal
        
        op = UnaryOp(
            operator=".NOT.",
            operand=Literal(value=True, type_name="LOGICAL")
        )
        
        op.accept(self.analyzer)
        result_type = self.analyzer._get_type(op)
        self.assertEqual(result_type, "LOGICAL")
    
    # =====================================================================
    # Testes de Atribuição
    # =====================================================================
    
    def test_valid_integer_assignment(self):
        """Testa atribuição válida INTEGER = INTEGER."""
        from src.ast.nodes import (Program, VariableDeclaration, Assignment, 
                                 Identifier, Literal)
        
        program = Program(
            name="test",
            declarations=[VariableDeclaration(name="X", type_name="INTEGER")],
            statements=[
                Assignment(
                    target=Identifier(name="X"),
                    value=Literal(value=42, type_name="INTEGER")
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
    
    def test_integer_to_real_coercion(self):
        """Testa coerção INTEGER → REAL em atribuição."""
        from src.ast.nodes import (Program, VariableDeclaration, Assignment, 
                                 Identifier, Literal)
        
        program = Program(
            name="test",
            declarations=[VariableDeclaration(name="X", type_name="REAL")],
            statements=[
                Assignment(
                    target=Identifier(name="X"),
                    value=Literal(value=42, type_name="INTEGER")
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
    
    def test_undeclared_variable_in_assignment(self):
        """Testa erro quando variável não é declarada."""
        from src.ast.nodes import (Program, Assignment, Identifier, Literal)
        
        program = Program(
            name="test",
            declarations=[],
            statements=[
                Assignment(
                    target=Identifier(name="X"),
                    value=Literal(value=42, type_name="INTEGER")
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertFalse(result)
        self.assertTrue(any("não declarada" in e for e in self.analyzer.errors))
    
    def test_undeclared_variable_in_expression(self):
        """Testa erro quando variável em expressão não é declarada."""
        from src.ast.nodes import (Program, Assignment, Identifier, Literal, BinaryOp)
        
        program = Program(
            name="test",
            declarations=[],
            statements=[
                Assignment(
                    target=Identifier(name="X"),
                    value=BinaryOp(
                        left=Identifier(name="Y"),
                        operator="+",
                        right=Literal(value=1, type_name="INTEGER")
                    )
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertFalse(result)
    
    # =====================================================================
    # Testes de Controlo de Fluxo
    # =====================================================================
    
    def test_if_with_logical_condition(self):
        """Testa IF com condição LOGICAL."""
        from src.ast.nodes import (Program, VariableDeclaration, IfStatement, 
                                 BinaryOp, Literal)
        
        program = Program(
            name="test",
            declarations=[],
            statements=[
                IfStatement(
                    condition=BinaryOp(
                        left=Literal(value=1, type_name="INTEGER"),
                        operator=".GT.",
                        right=Literal(value=0, type_name="INTEGER")
                    ),
                    then_body=[],
                    else_body=None
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
    
    def test_if_with_integer_condition_error(self):
        """Testa erro quando condição IF é INTEGER (não LOGICAL)."""
        from src.ast.nodes import (Program, IfStatement, Literal)
        
        program = Program(
            name="test",
            declarations=[],
            statements=[
                IfStatement(
                    condition=Literal(value=42, type_name="INTEGER"),
                    then_body=[],
                    else_body=None
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertFalse(result)
        self.assertTrue(any("LOGICAL" in e for e in self.analyzer.errors))
    
    def test_do_loop_valid(self):
        """Testa DO loop válido."""
        from src.ast.nodes import (Program, VariableDeclaration, DoLoop, Identifier, Literal)
        
        program = Program(
            name="test",
            declarations=[VariableDeclaration(name="I", type_name="INTEGER")],
            statements=[
                DoLoop(
                    variable=Identifier(name="I"),
                    start=Literal(value=1, type_name="INTEGER"),
                    end=Literal(value=10, type_name="INTEGER"),
                    body=[]
                )
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
    
    def test_continue_outside_loop_error(self):
        """Testa erro CONTINUE fora de DO loop."""
        from src.ast.nodes import (Program, ContinueStatement)
        
        program = Program(
            name="test",
            declarations=[],
            statements=[ContinueStatement()],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertFalse(result)
        self.assertTrue(any("CONTINUE fora de DO" in e for e in self.analyzer.errors))
    
    # =====================================================================
    # Testes de I/O
    # =====================================================================
    
    def test_read_declared_variables(self):
        """Testa READ com variáveis declaradas."""
        from src.ast.nodes import (Program, VariableDeclaration, ReadStatement, Identifier)
        
        program = Program(
            name="test",
            declarations=[
                VariableDeclaration(name="X", type_name="INTEGER"),
                VariableDeclaration(name="Y", type_name="REAL"),
            ],
            statements=[
                ReadStatement(unit=None, variables=[Identifier(name="X"), Identifier(name="Y")])
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)
    
    def test_read_undeclared_variable_error(self):
        """Testa erro quando READ usa variável não declarada."""
        from src.ast.nodes import (Program, ReadStatement, Identifier)
        
        program = Program(
            name="test",
            declarations=[],
            statements=[ReadStatement(unit=None, variables=[Identifier(name="X")])],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertFalse(result)
    
    def test_print_with_expressions(self):
        """Testa PRINT com expressões."""
        from src.ast.nodes import (Program, VariableDeclaration, PrintStatement, 
                                 Identifier, Literal, BinaryOp)
        
        program = Program(
            name="test",
            declarations=[VariableDeclaration(name="X", type_name="INTEGER")],
            statements=[
                PrintStatement(expressions=[
                    Identifier(name="X"),
                    Literal(value="Hello", type_name="CHARACTER"),
                    BinaryOp(
                        left=Identifier(name="X"),
                        operator="+",
                        right=Literal(value=1, type_name="INTEGER")
                    )
                ])
            ],
            subprograms=[]
        )
        
        result = self.analyzer.analyze(program)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
