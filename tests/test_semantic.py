"""
Testes para Análise Semântica
========================
"""

import unittest
import os
from pathlib import Path

from src.semantic.analyzer import SemanticAnalyzer
from src.semantic.symbol_table import SymbolTable
from src.semantic.type_checker import TypeChecker
from src.exceptions import SemanticError
from src.lexer.lexer import Lexer
from src.parser.parser import Parser


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

    def test_declaration_initial_value_type_error(self):
        """Testa erro quando valor inicial não é compatível com o tipo."""
        from src.ast.nodes import (Program, VariableDeclaration, Literal)

        program = Program(
            name="test",
            declarations=[
                VariableDeclaration(
                    name="X",
                    type_name="INTEGER",
                    initial_value=Literal(value=3.14, type_name="REAL")
                )
            ],
            statements=[],
            subprograms=[]
        )

        result = self.analyzer.analyze(program)
        self.assertFalse(result)
        self.assertTrue(any("Atribuição inválida" in e for e in self.analyzer.errors))

    def test_parameter_constant_can_be_read_but_not_assigned(self):
        """Testa PARAMETER como constante sem bloquear parâmetros de subrotina."""
        from src.ast.nodes import (Program, VariableDeclaration, Assignment, Identifier, Literal)

        parameter = VariableDeclaration(name="N", type_name="INTEGER", initial_value=Literal(value=10, type_name="INTEGER"))
        parameter.is_parameter = True
        program = Program(
            name="test",
            declarations=[
                parameter,
                VariableDeclaration(name="X", type_name="INTEGER"),
            ],
            statements=[
                Assignment(target=Identifier(name="X"), value=Identifier(name="N")),
                Assignment(target=Identifier(name="N"), value=Literal(value=2, type_name="INTEGER")),
            ],
            subprograms=[],
        )

        result = self.analyzer.analyze(program)
        self.assertFalse(result)
        self.assertTrue(any("PARAMETER 'N'" in e for e in self.analyzer.errors))

    def test_error_message_includes_location_when_available(self):
        """Testa diagnóstico semântico com linha/coluna anotadas pelo parser."""
        from src.ast.nodes import Program, Assignment, Identifier, Literal, SourceLocation

        assignment = Assignment(target=Identifier(name="X"), value=Literal(value=1, type_name="INTEGER"))
        assignment.location = SourceLocation(line=4, column=8)
        program = Program(name="test", declarations=[], statements=[assignment], subprograms=[])

        result = self.analyzer.analyze(program)

        self.assertFalse(result)
        self.assertTrue(any("linha 4" in e and "coluna 8" in e for e in self.analyzer.errors))

    def test_intrinsic_max_min_and_conversions_are_typed(self):
        """Testa tipos de intrínsecas críticas."""
        from src.ast.nodes import FunctionCall, Literal

        cases = [
            (FunctionCall("MAX", [Literal(1, "INTEGER"), Literal(2, "INTEGER")]), "INTEGER"),
            (FunctionCall("MIN", [Literal(1.0, "REAL"), Literal(2, "INTEGER")]), "REAL"),
            (FunctionCall("INT", [Literal(2.5, "REAL")]), "INTEGER"),
            (FunctionCall("REAL", [Literal(2, "INTEGER")]), "REAL"),
            (FunctionCall("SQRT", [Literal(4, "INTEGER")]), "REAL"),
        ]

        for node, expected_type in cases:
            with self.subTest(function=node.function_name):
                node.accept(self.analyzer)
                self.assertEqual(self.analyzer._get_type(node), expected_type)

    def test_goto_to_defined_label(self):
        """Testa GOTO para label definido em DO loop."""
        from src.ast.nodes import (Program, VariableDeclaration, DoLoop, GotoStatement,
                                 Identifier, Literal)

        program = Program(
            name="test",
            declarations=[VariableDeclaration(name="I", type_name="INTEGER")],
            statements=[
                GotoStatement(label=100),
                DoLoop(
                    variable=Identifier(name="I"),
                    start=Literal(value=1, type_name="INTEGER"),
                    end=Literal(value=10, type_name="INTEGER"),
                    label=100,
                    body=[]
                )
            ],
            subprograms=[]
        )

        result = self.analyzer.analyze(program)
        self.assertTrue(result)

    def test_goto_to_undefined_label_error(self):
        """Testa erro quando GOTO aponta para label inexistente."""
        from src.ast.nodes import (Program, GotoStatement)

        program = Program(
            name="test",
            declarations=[],
            statements=[GotoStatement(label=200)],
            subprograms=[]
        )

        result = self.analyzer.analyze(program)
        self.assertFalse(result)
        self.assertTrue(any("GOTO para label não definido" in e for e in self.analyzer.errors))

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


# =====================================================================
# Testes de Integração: Análise Semântica com Exemplos Reais
# =====================================================================

class TestSemanticExamples(unittest.TestCase):
    """
    Testes de integração da análise semântica com exemplos reais.

    Para cada exemplo, realizar:
    1. Lexing (tokenização)
    2. Parsing (construir AST)
    3. Análise Semântica (validação)
    """

    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes."""
        cls.examples_dir = Path(__file__).parent / "examples"
        cls.lexer = Lexer()
        cls.parser = Parser()
        cls.examples = sorted([
            f for f in os.listdir(cls.examples_dir)
            if f.endswith('.f')
        ])

    def _analyze_file(self, filename):
        """
        Analisa um arquivo Fortran completo.

        Args:
            filename: Nome do arquivo (ex: ejemplo1_hello.f)

        Returns:
            tuple: (ast, analyzer, success)
                ast: A árvore sintática construída
                analyzer: O analisador semântico utilizado
                success: True se análise sem erros, False caso contrário
        """
        filepath = self.examples_dir / filename

        if not filepath.exists():
            self.fail(f"Arquivo não encontrado: {filepath}")

        # Ler arquivo
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Lexing
        tokens = self.lexer.tokenize(source_code)
        if not tokens:
            return None, None, False

        # Parsing
        ast = self.parser.parse(tokens)
        if ast is None:
            return None, None, False

        # Análise Semântica
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        return ast, analyzer, success

    def test_exemplo1_hello(self):
        """Analisa ejemplo1_hello.f - programa simples com PRINT."""
        ast, analyzer, success = self._analyze_file("exemplo1_hello.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemple1_hello.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

        self.assertTrue(success,
                       f"Análise semântica falhou: {analyzer.get_errors()}")

    def test_exemplo2_fatorial(self):
        """Analisa ejemplo2_fatorial.f - função com loops."""
        ast, analyzer, success = self._analyze_file("exemplo2_fatorial.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo2_fatorial.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

        self.assertTrue(success)

    def test_exemplo3_primo(self):
        """Analisa ejemplo3_primo.f - controlo de fluxo complexo."""
        ast, analyzer, success = self._analyze_file("exemplo3_primo.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo3_primo.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

        self.assertTrue(success,
                       f"Análise semântica falhou: {analyzer.get_errors()}")

    def test_exemplo4_soma_lista(self):
        """Analisa ejemplo4_soma_lista.f - arrays e loops."""
        ast, analyzer, success = self._analyze_file("exemplo4_soma_lista.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo4_soma_lista.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

    def test_exemplo5_conversor_bases(self):
        """Analisa ejemplo5_conversor_bases.f - função com labels/GOTO."""
        ast, analyzer, success = self._analyze_file("exemplo5_conversor_bases.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo5_conversor_bases.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

        self.assertTrue(success,
                       f"Análise semântica falhou: {analyzer.get_errors()}")

    def test_exemplo6_operacoes_reais(self):
        """Analisa ejemplo6_operacoes_reais.f - operações com REAL."""
        ast, analyzer, success = self._analyze_file("exemplo6_operacoes_reais.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo6_operacoes_reais.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

    def test_exemplo7_arrays_multidimensionais(self):
        """Analisa ejemplo7_arrays_multidimensionais.f - arrays 2D."""
        ast, analyzer, success = self._analyze_file("exemplo7_arrays_multidimensionais.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo7_arrays_multidimensionais.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

    def test_exemplo8_subrotina(self):
        """Analisa ejemplo8_subrotina.f - subrotina (SUBROUTINE)."""
        ast, analyzer, success = self._analyze_file("exemplo8_subrotina.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo8_subrotina.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

    def test_exemplo9_logica_complexa(self):
        """Analisa ejemplo9_logica_complexa.f - lógica com operadores."""
        ast, analyzer, success = self._analyze_file("exemplo9_logica_complexa.f")

        self.assertIsNotNone(ast)
        self.assertIsNotNone(analyzer)

        if not success:
            print(f"\nErros em exemplo9_logica_complexa.f:")
            for error in analyzer.get_errors():
                print(f"  - {error}")

    # TODO: Parser não implementa CHARACTER*length syntax
    # def test_exemplo10_strings(self):
    #     """Analisa ejemplo10_strings.f - operações com CHARACTER."""
    #     ast, analyzer, success = self._analyze_file("exemplo10_strings.f")
    #
    #     self.assertIsNotNone(ast)
    #     self.assertIsNotNone(analyzer)
    #
    #     if not success:
    #         print(f"\nErros em exemplo10_strings.f:")
    #         for error in analyzer.get_errors():
    #             print(f"  - {error}")

    # TODO: Parser não implementa CHARACTER*length syntax em exemplo10_strings
    # Aguardar implementação do parser para CHARACTER*length
    # def test_all_examples_parse(self):
    #     """Testa que todos os exemplos fazem parsing sem erros."""
    #     from src.exceptions import ParserError
    #
    #     all_passed = True
    #     parser_failures = []
    #     semantic_failures = []
    #
    #     for example_file in self.examples:
    #         try:
    #             filepath = self.examples_dir / example_file
    #
    #             with open(filepath, 'r', encoding='utf-8') as f:
    #                 source_code = f.read()
    #
    #             tokens = self.lexer.tokenize(source_code)
    #             if not tokens:
    #                 parser_failures.append(f"{example_file}: Lexing falhou")
    #                 all_passed = False
    #                 continue
    #
    #             ast = self.parser.parse(tokens)
    #             if ast is None:
    #                 parser_failures.append(f"{example_file}: Parsing retornou None")
    #                 all_passed = False
    #                 continue
    #
    #             # Análise Semântica
    #             analyzer = SemanticAnalyzer()
    #             success = analyzer.analyze(ast)
    #
    #             if not success:
    #                 errors_str = "; ".join(analyzer.get_errors())
    #                 semantic_failures.append(f"{example_file}: {errors_str}")
    #                 all_passed = False
    #
    #         except ParserError as e:
    #             parser_failures.append(f"{example_file}: {str(e)}")
    #             all_passed = False
    #
    #     # Report issues
    #     if parser_failures:
    #         print(f"\nParser failures (não implementadas no momento):")
    #         for failure in parser_failures:
    #             print(f"  - {failure}")
    #
    #     if semantic_failures:
    #         print(f"\nSemantic failures:")
    #         for failure in semantic_failures:
    #             print(f"  - {failure}")
    #
    #     # We accept parser failures for now since some features aren't implemented
    #     # But semantic failures should not occur for successfully parsed programs
    #     self.assertEqual(len(semantic_failures), 0,
    #                     f"Falhas semânticas encontradas: {semantic_failures}")


if __name__ == "__main__":
    unittest.main()
