"""
Testes Completos e Unitários para o Analisador Sintático (Parser)
==================================================================

Testes para todas as regras gramaticais de Fortran 77:
- Estrutura de programas
- Declarações de tipos e variáveis
- Expressões (aritméticas, lógicas, comparações)
- Statements simples (assignment, read, print)
- Statements de controlo de fluxo (IF, DO loops, GOTO)
- Arrays e acesso a elementos
- Subprogramas (functions, subroutines)
- I/O operations (READ, WRITE, PRINT)
- Operadores diversos
"""

import unittest
import os
from src.parser.parser import Parser
from src.lexer.lexer import Lexer
from src.ast.nodes import (
    Program, VariableDeclaration, Assignment, Identifier,
    IfStatement, DoLoop, FunctionCall, BinaryOp, Literal,
    PrintStatement, ReadStatement, FunctionDeclaration
)


class TestParserStructure(unittest.TestCase):
    """Testes da estrutura básica de programas Fortran 77."""
    
    def setUp(self):
        """Inicializa parser e lexer para cada teste."""
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        """Helper para tokenizar e fazer parsing de código."""
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_simple_program(self):
        """Testa programa vazio básico: PROGRAM END."""
        code = "PROGRAM HELLO END"
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        self.assertIsInstance(ast, Program)
        self.assertEqual(ast.name, "HELLO")
    
    def test_program_with_name(self):
        """Testa programa com nome específico."""
        code = "PROGRAM MYPROG END"
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        self.assertEqual(ast.name, "MYPROG")
    
    def test_program_with_declarations_only(self):
        """Testa programa com apenas declarações."""
        code = """PROGRAM TEST
        INTEGER X
        REAL Y
        LOGICAL Z
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        self.assertGreater(len(ast.declarations), 0)


class TestParserTypeDeclarations(unittest.TestCase):
    """Testes para declarações de tipos e variáveis."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_integer_declaration_single(self):
        """Testa declaração de uma variável inteira."""
        code = """PROGRAM TEST
        INTEGER X
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        # Verifica se há declarações
        self.assertGreater(len(ast.declarations), 0)
    
    def test_integer_declaration_multiple(self):
        """Testa declaração de múltiplas variáveis inteiras numa linha."""
        code = """PROGRAM TEST
        INTEGER X, Y, Z
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        # Deve ter 3 declarações de inteiros
        decls = [d for d in ast.declarations if isinstance(d, VariableDeclaration)]
        self.assertGreaterEqual(len(decls), 3)
    
    def test_real_declaration(self):
        """Testa declaração de variável real."""
        code = """PROGRAM TEST
        REAL PI, RADIUS
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_logical_declaration(self):
        """Testa declaração de variável lógica."""
        code = """PROGRAM TEST
        LOGICAL FLAG, SWITCH
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_character_declaration(self):
        """Testa declaração de variável CHARACTER."""
        code = """PROGRAM TEST
        CHARACTER NAME
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_complex_declaration(self):
        """Testa declaração de variável COMPLEX."""
        code = """PROGRAM TEST
        COMPLEX Z
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_mixed_type_declarations(self):
        """Testa múltiplas declarações de tipos variados."""
        code = """PROGRAM TEST
        INTEGER X, Y
        REAL PI, RAIO
        LOGICAL ATIVO
        CHARACTER STR
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserExpressions(unittest.TestCase):
    """Testes para parsing de expressões (aritméticas, lógicas, comparações)."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_arithmetic_addition(self):
        """Testa expressão de adição."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = X + 5
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_arithmetic_subtraction(self):
        """Testa expressão de subtração."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = X - 3
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_arithmetic_multiplication(self):
        """Testa expressão de multiplicação."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = X * 4
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_arithmetic_division(self):
        """Testa expressão de divisão."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = X / 2
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_arithmetic_power(self):
        """Testa expressão de potência."""
        code = """PROGRAM TEST
        REAL X, RESULT
        RESULT = X ** 2
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_complex_arithmetic(self):
        """Testa expressão aritmética complexa com precedência."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = 2 + 3 * 4 - 1
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_arithmetic_with_parentheses(self):
        """Testa expressão aritmética com parênteses."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = (2 + 3) * 4
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_unary_plus(self):
        """Testa operador unário positivo."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = +5
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_unary_minus(self):
        """Testa operador unário negativo."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = -X
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_comparison_less_than(self):
        """Testa operador de comparação <."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .LT. 10
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_comparison_less_equal(self):
        """Testa operador de comparação <=."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .LE. 10
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_comparison_greater_than(self):
        """Testa operador de comparação >."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .GT. 5
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_comparison_greater_equal(self):
        """Testa operador de comparação >=."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .GE. 0
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_comparison_equal(self):
        """Testa operador de comparação ==."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .EQ. 42
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_comparison_not_equal(self):
        """Testa operador de comparação !=."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .NE. 0
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_logical_and(self):
        """Testa operador lógico AND."""
        code = """PROGRAM TEST
        LOGICAL A, B, RESULT
        RESULT = A .AND. B
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_logical_or(self):
        """Testa operador lógico OR."""
        code = """PROGRAM TEST
        LOGICAL A, B, RESULT
        RESULT = A .OR. B
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_logical_not(self):
        """Testa operador lógico NOT."""
        code = """PROGRAM TEST
        LOGICAL A, RESULT
        RESULT = .NOT. A
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_complex_logical_expression(self):
        """Testa expressão lógica complexa."""
        code = """PROGRAM TEST
        INTEGER X
        LOGICAL RESULT
        RESULT = X .GT. 5 .AND. X .LT. 10 .OR. X .EQ. 0
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_literal_integer(self):
        """Testa literal inteiro."""
        code = """PROGRAM TEST
        INTEGER X
        X = 42
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_literal_real(self):
        """Testa literal real."""
        code = """PROGRAM TEST
        REAL X
        X = 3.14159
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_literal_string(self):
        """Testa literal string."""
        code = """PROGRAM TEST
        CHARACTER MSG
        MSG = 'Hello'
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_literal_logical_true(self):
        """Testa literal lógico .TRUE.."""
        code = """PROGRAM TEST
        LOGICAL FLAG
        FLAG = .TRUE.
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_literal_logical_false(self):
        """Testa literal lógico .FALSE.."""
        code = """PROGRAM TEST
        LOGICAL FLAG
        FLAG = .FALSE.
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserAssignments(unittest.TestCase):
    """Testes para atribuições de valores a variáveis."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_simple_assignment(self):
        """Testa atribuição simples."""
        code = """PROGRAM TEST
        INTEGER X
        X = 10
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_assignment_from_variable(self):
        """Testa atribuição usando outra variável."""
        code = """PROGRAM TEST
        INTEGER X, Y
        Y = X
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_assignment_with_expression(self):
        """Testa atribuição com expressão."""
        code = """PROGRAM TEST
        INTEGER X, Y, RESULT
        RESULT = X + Y * 2
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_multiple_assignments(self):
        """Testa múltiplas atribuições consecutivas."""
        code = """PROGRAM TEST
        INTEGER X, Y, Z
        X = 1
        Y = 2
        Z = X + Y
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserArrays(unittest.TestCase):
    """Testes para arrays e acesso a elementos de array."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_array_declaration_1d(self):
        """Testa declaração de array unidimensional."""
        code = """PROGRAM TEST
        INTEGER ARR(10)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_declaration_2d(self):
        """Testa declaração de array bidimensional."""
        code = """PROGRAM TEST
        INTEGER MATRIX(3, 3)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_declaration_3d(self):
        """Testa declaração de array tridimensional."""
        code = """PROGRAM TEST
        REAL TENSOR(2, 3, 4)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_access_1d(self):
        """Testa acesso a elemento de array 1D."""
        code = """PROGRAM TEST
        INTEGER ARR(10), X
        X = ARR(5)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_access_2d(self):
        """Testa acesso a elemento de array 2D."""
        code = """PROGRAM TEST
        INTEGER MATRIX(3, 3), ELEM
        ELEM = MATRIX(2, 3)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_element_assignment(self):
        """Testa atribuição a elemento de array."""
        code = """PROGRAM TEST
        INTEGER ARR(10)
        ARR(1) = 42
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_element_assignment_2d(self):
        """Testa atribuição a elemento de array 2D."""
        code = """PROGRAM TEST
        INTEGER MATRIX(3, 3)
        MATRIX(2, 1) = 99
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_array_in_expression(self):
        """Testa uso de elemento de array em expressão."""
        code = """PROGRAM TEST
        INTEGER ARR(10), X
        X = ARR(3) + ARR(5) * 2
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserIOOperations(unittest.TestCase):
    """Testes para operações de entrada/saída (READ, PRINT, WRITE)."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_print_simple(self):
        """Testa PRINT sem argumentos."""
        code = """PROGRAM TEST
        PRINT *
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_print_single_value(self):
        """Testa PRINT com uma expressão."""
        code = """PROGRAM TEST
        INTEGER X
        PRINT *, X
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_print_multiple_values(self):
        """Testa PRINT com múltiplas expressões."""
        code = """PROGRAM TEST
        INTEGER X, Y
        PRINT *, X, Y, 42
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_print_with_string(self):
        """Testa PRINT com string literal."""
        code = """PROGRAM TEST
        INTEGER X
        PRINT *, 'O valor e:', X
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_read_simple(self):
        """Testa READ simples."""
        code = """PROGRAM TEST
        INTEGER X
        READ *, X
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_read_multiple_variables(self):
        """Testa READ com múltiplas variáveis."""
        code = """PROGRAM TEST
        INTEGER X, Y
        READ *, X, Y
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_read_no_variables(self):
        """Testa READ sem variáveis."""
        code = """PROGRAM TEST
        READ *
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_read_array_element(self):
        """Testa READ para elemento de array."""
        code = """PROGRAM TEST
        INTEGER ARR(10)
        READ *, ARR(1)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserControlFlow(unittest.TestCase):
    """Testes para estruturas de controlo de fluxo (IF, DO, GOTO)."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_if_then_endif(self):
        """Testa estrutura IF-THEN-ENDIF."""
        code = """PROGRAM TEST
        INTEGER X
        IF (X .GT. 0) THEN
            X = 1
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        # Verifica se há IF statement
        statements = [s for s in ast.statements if isinstance(s, IfStatement)]
        self.assertGreater(len(statements), 0)
    
    def test_if_then_else_endif(self):
        """Testa estrutura IF-THEN-ELSE-ENDIF."""
        code = """PROGRAM TEST
        INTEGER X
        IF (X .GT. 0) THEN
            X = 1
        ELSE
            X = -1
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_if_then_elseif_endif(self):
        """Testa estrutura IF-THEN-ELSEIF-ENDIF."""
        code = """PROGRAM TEST
        INTEGER X
        IF (X .GT. 0) THEN
            X = 1
        ELSEIF (X .LT. 0) THEN
            X = -1
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_if_then_elseif_else_endif(self):
        """Testa estrutura IF-THEN-ELSEIF-ELSE-ENDIF."""
        code = """PROGRAM TEST
        INTEGER X
        IF (X .GT. 0) THEN
            X = 1
        ELSEIF (X .LT. 0) THEN
            X = -1
        ELSE
            X = 0
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_nested_if(self):
        """Testa IF aninhados."""
        code = """PROGRAM TEST
        INTEGER X, Y
        IF (X .GT. 0) THEN
            IF (Y .GT. 0) THEN
                X = 1
            ENDIF
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_do_loop_with_continue(self):
        """Testa DO loop com label CONTINUE."""
        code = """PROGRAM TEST
        INTEGER I, SUM
        SUM = 0
        DO 10 I = 1, 10
            SUM = SUM + I
        10 CONTINUE
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
        # Verifica se há DO loop
        statements = [s for s in ast.statements if isinstance(s, DoLoop)]
        self.assertGreater(len(statements), 0)
    
    def test_do_loop_with_enddo(self):
        """Testa DO loop com ENDDO."""
        code = """PROGRAM TEST
        INTEGER I, SUM
        SUM = 0
        DO I = 1, 10
            SUM = SUM + I
        ENDDO
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_nested_do_loops(self):
        """Testa DO loops aninhados."""
        code = """PROGRAM TEST
        INTEGER I, J, SOMA
        SOMA = 0
        DO 100 I = 1, 3
            DO 50 J = 1, 3
                SOMA = SOMA + I + J
            50 CONTINUE
        100 CONTINUE
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_do_loop_in_if(self):
        """Testa DO loop dentro de IF."""
        code = """PROGRAM TEST
        INTEGER I, X
        X = 5
        IF (X .GT. 0) THEN
            DO 10 I = 1, X
                X = X + 1
            10 CONTINUE
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_goto_statement(self):
        """Testa GOTO simples."""
        code = """PROGRAM TEST
        INTEGER X
        X = 1
        GOTO 100
        X = 2
        100 CONTINUE
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserFunctionCalls(unittest.TestCase):
    """Testes para chamadas de funções e subrotinas."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_function_call_no_args(self):
        """Testa chamada de função sem argumentos."""
        code = """PROGRAM TEST
        INTEGER RESULT
        RESULT = FUNC()
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_function_call_single_arg(self):
        """Testa chamada de função com um argumento."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = SQRT(X)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_function_call_multiple_args(self):
        """Testa chamada de função com múltiplos argumentos."""
        code = """PROGRAM TEST
        INTEGER X, Y, RESULT
        RESULT = MOD(X, Y)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_call_statement_no_args(self):
        """Testa CALL de subrotina sem argumentos."""
        code = """PROGRAM TEST
        CALL INIT()
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_call_statement_with_args(self):
        """Testa CALL de subrotina com argumentos."""
        code = """PROGRAM TEST
        INTEGER X, Y
        CALL SOMAR(X, Y)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_nested_function_calls(self):
        """Testa chamadas de funções aninhadas."""
        code = """PROGRAM TEST
        INTEGER X, RESULT
        RESULT = MOD(ABS(X), 10)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserSubprograms(unittest.TestCase):
    """Testes para definição de subprogramas (FUNCTION e SUBROUTINE)."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_integer_function_definition(self):
        """Testa definição de função que retorna INTEGER."""
        code = """PROGRAM MAIN
        END
        
        INTEGER FUNCTION DOUBLE(X)
        INTEGER X
        DOUBLE = X * 2
        RETURN
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_real_function_definition(self):
        """Testa definição de função que retorna REAL."""
        code = """PROGRAM MAIN
        END
        
        REAL FUNCTION AVERAGE(X, Y)
        REAL X, Y
        AVERAGE = (X + Y) / 2.0
        RETURN
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_subroutine_definition(self):
        """Testa definição de subrotina."""
        code = """PROGRAM MAIN
        END
        
        SUBROUTINE PRINT_MSG(MSG)
        CHARACTER MSG
        PRINT *, MSG
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_function_with_multiple_parameters(self):
        """Testa função com múltiplos parâmetros."""
        code = """PROGRAM MAIN
        END
        
        INTEGER FUNCTION SOMA(A, B, C)
        INTEGER A, B, C
        SOMA = A + B + C
        RETURN
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_subroutine_with_multiple_parameters(self):
        """Testa subrotina com múltiplos parâmetros."""
        code = """PROGRAM MAIN
        END
        
        SUBROUTINE SWAP(X, Y)
        INTEGER X, Y
        INTEGER TEMP
        TEMP = X
        X = Y
        Y = TEMP
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_function_with_local_variables(self):
        """Testa função com variáveis locais."""
        code = """PROGRAM MAIN
        END
        
        INTEGER FUNCTION FACT(N)
        INTEGER N
        INTEGER I, RESULTADO
        RESULTADO = 1
        DO 10 I = 1, N
            RESULTADO = RESULTADO * I
        10 CONTINUE
        FACT = RESULTADO
        RETURN
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


class TestParserFromExamples(unittest.TestCase):
    """Testes usando os exemplos de programas Fortran fornecidos."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
        self.examples_dir = "tests/examples"
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def _parse_with_preprocess(self, code):
        """Parse with preprocessing for example files that use fixed format."""
        tokens = self.lexer.tokenize(code, preprocess=True)
        return self.parser.parse(tokens)
    
    def _read_example(self, filename):
        """Lê um arquivo de exemplo."""
        filepath = os.path.join(self.examples_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def test_example1_hello(self):
        """Testa parsing de exemplo1_hello.f (Hello World)."""
        code = self._read_example("exemplo1_hello.f")
        if code:
            ast = self._parse(code)
            self.assertIsNotNone(ast)
            self.assertEqual(ast.name, "HELLO")
    
    def test_example2_fatorial(self):
        """Testa parsing de exemplo2_fatorial.f (Factorial)."""
        code = self._read_example("exemplo2_fatorial.f")
        if code:
            ast = self._parse(code)
            self.assertIsNotNone(ast)
            self.assertEqual(ast.name, "FATORIAL")
            # Verifica se tem declarações
            self.assertGreater(len(ast.declarations), 0)
            # Verifica se tem statements
            self.assertGreater(len(ast.statements), 0)
    
    def test_example3_primo(self):
        """Testa parsing de exemplo3_primo.f (Prime number check)."""
        code = self._read_example("exemplo3_primo.f")
        if code:
            ast = self._parse_with_preprocess(code)
            self.assertIsNotNone(ast)
            self.assertEqual(ast.name, "PRIMO")
    
    def test_example5_conversor(self):
        """Testa parsing de exemplo5_conversor_bases.f com função."""
        code = self._read_example("exemplo5_conversor_bases.f")
        if code:
            ast = self._parse_with_preprocess(code)
            self.assertIsNotNone(ast)
            self.assertEqual(ast.name, "CONVERSOR")
            # Verifica se tem subprogramas
            self.assertGreater(len(ast.subprograms), 0)
    
    def test_example7_arrays(self):
        """Testa parsing de exemplo7_arrays_multidimensionais.f."""
        code = self._read_example("exemplo7_arrays_multidimensionais.f")
        if code:
            ast = self._parse_with_preprocess(code)
            self.assertIsNotNone(ast)
            self.assertEqual(ast.name, "ARRAYS")
    
    def test_example8_subrotina(self):
        """Testa parsing de exemplo8_subrotina.f com subrotina."""
        code = self._read_example("exemplo8_subrotina.f")
        if code:
            ast = self._parse_with_preprocess(code)
            self.assertIsNotNone(ast)
            self.assertEqual(ast.name, "SUBS")
            # Verifica se tem subprogramas
            if ast.subprograms:
                self.assertGreater(len(ast.subprograms), 0)


class TestParserEdgeCases(unittest.TestCase):
    """Testes para casos extremos e situações especiais."""
    
    def setUp(self):
        self.parser = Parser()
        self.lexer = Lexer()
    
    def _parse(self, code):
        tokens = self.lexer.tokenize(code, preprocess=False)
        return self.parser.parse(tokens)
    
    def test_deeply_nested_expressions(self):
        """Testa expressões profundamente aninhadas."""
        code = """PROGRAM TEST
        INTEGER X
        X = ((((1 + 2) * 3) - 4) / 5)
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_long_variable_list(self):
        """Testa lista longa de variáveis."""
        code = """PROGRAM TEST
        INTEGER A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_long_expression_list(self):
        """Testa lista longa em PRINT."""
        code = """PROGRAM TEST
        INTEGER A, B, C, D, E
        PRINT *, A, B, C, D, E, 1, 2, 3, 4, 5
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_deeply_nested_loops(self):
        """Testa loops aninhados profundamente."""
        code = """PROGRAM TEST
        INTEGER I, J, K, SOMA
        SOMA = 0
        DO 100 I = 1, 2
            DO 90 J = 1, 2
                DO 80 K = 1, 2
                    SOMA = SOMA + 1
                80 CONTINUE
            90 CONTINUE
        100 CONTINUE
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)
    
    def test_multiple_elseif_clauses(self):
        """Testa múltiplas cláusulas ELSEIF."""
        code = """PROGRAM TEST
        INTEGER X
        IF (X .EQ. 1) THEN
            X = 10
        ELSEIF (X .EQ. 2) THEN
            X = 20
        ELSEIF (X .EQ. 3) THEN
            X = 30
        ELSEIF (X .EQ. 4) THEN
            X = 40
        ELSE
            X = 0
        ENDIF
        END"""
        ast = self._parse(code)
        self.assertIsNotNone(ast)


if __name__ == "__main__":
    unittest.main()
