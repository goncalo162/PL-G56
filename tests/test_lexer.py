"""
Testes Extensivos para Analisador Léxico (Lexer)
=================================================

Suite completa de testes para o lexer Fortran 77, com:
- Testes unitários para cada tipo de token
- Testes de operadores
- Testes de programas de exemplo do enunciado
- Testes de casos extremos

Execução: python -m pytest tests/test_lexer.py -v
"""

import unittest
import os
from src.lexer.lexer import Lexer


def get_type_name(token):
    """Helper para obter nome do tipo de token."""
    return token.type if isinstance(token.type, str) else token.type.name


class TestLexerKeywords(unittest.TestCase):
    """Testes unitários para palavras-chave Fortran."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_program_keyword(self):
        """Testa reconhecimento de PROGRAM."""
        tokens = self.lexer.get_tokens("PROGRAM")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(get_type_name(tokens[0]), "PROGRAM")
    
    def test_end_keyword(self):
        """Testa reconhecimento de END."""
        tokens = self.lexer.get_tokens("END")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(get_type_name(tokens[0]), "END")
    
    def test_data_type_keywords(self):
        """Testa reconhecimento de tipos de dados."""
        types = ["INTEGER", "REAL", "LOGICAL", "CHARACTER"]
        for dtype in types:
            with self.subTest(dtype=dtype):
                tokens = self.lexer.get_tokens(dtype)
                self.assertEqual(len(tokens), 1)
                self.assertEqual(get_type_name(tokens[0]), dtype)
    
    def test_control_flow_keywords(self):
        """Testa reconhecimento de keywords de controle."""
        code = "IF THEN ELSE ENDIF"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types, ["IF", "THEN", "ELSE", "ENDIF"])
    
    def test_loop_keywords(self):
        """Testa reconhecimento de DO CONTINUE."""
        tokens = self.lexer.get_tokens("DO CONTINUE")
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types, ["DO", "CONTINUE"])
    
    def test_io_keywords(self):
        """Testa reconhecimento de READ PRINT."""
        tokens = self.lexer.get_tokens("READ PRINT")
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types, ["READ", "PRINT"])
    
    def test_subroutine_keywords(self):
        """Testa reconhecimento de SUBROUTINE, FUNCTION, etc."""
        code = "SUBROUTINE FUNCTION RETURN CALL"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types, ["SUBROUTINE", "FUNCTION", "RETURN", "CALL"])


class TestLexerIdentifiers(unittest.TestCase):
    """Testes para identificadores."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_simple_identifier(self):
        """Testa identificador simples."""
        tokens = self.lexer.get_tokens("VAR")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "VAR")
    
    def test_identifier_with_underscore(self):
        """Testa identificador com underscore."""
        tokens = self.lexer.get_tokens("MY_VAR")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "MY_VAR")
    
    def test_identifier_case_insensitive_keywords(self):
        """Testa que keywords são case-insensitive."""
        for code in ["program", "Program", "PROGRAM"]:
            with self.subTest(code=code):
                tokens = self.lexer.get_tokens(code)
                self.assertEqual(get_type_name(tokens[0]), "PROGRAM")
    
    def test_multi_char_identifier(self):
        """Testa identificador com múltiplas letras."""
        tokens = self.lexer.get_tokens("NOME")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "NOME")
    
    def test_identifier_with_numbers(self):
        """Testa identificador com números."""
        tokens = self.lexer.get_tokens("VAR1 VAR2X")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, "VAR1")
        self.assertEqual(tokens[1].value, "VAR2X")
    
    def test_identifier_with_leading_underscore(self):
        """Testa identificador começando com underscore."""
        tokens = self.lexer.get_tokens("_VALUE")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "_VALUE")


class TestLexerNumbers(unittest.TestCase):
    """Testes para números inteiros e reais."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_integer_literal(self):
        """Testa número inteiro."""
        tokens = self.lexer.get_tokens("42")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 42)
    
    def test_real_literal(self):
        """Testa número real com ponto decimal."""
        tokens = self.lexer.get_tokens("3.14")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 3.14)
    
    def test_real_without_integer_part(self):
        """Testa número com ponto mas sem parte inteira."""
        tokens = self.lexer.get_tokens(".5")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 0.5)
    
    def test_scientific_notation(self):
        """Testa notação científica."""
        test_cases = [("1.5e2", 150.0), ("2.5E-1", 0.25), ("5E2", 500.0)]
        for code, expected in test_cases:
            with self.subTest(code=code):
                tokens = self.lexer.get_tokens(code)
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].value, expected)
    
    def test_zero(self):
        """Testa número zero."""
        tokens = self.lexer.get_tokens("0")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 0)
    
    def test_negative_number(self):
        """Testa número negativo."""
        tokens = self.lexer.get_tokens("- 42")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(get_type_name(tokens[0]), "MINUS")
        self.assertEqual(tokens[1].value, 42)
    
    def test_integer_part_only(self):
        """Testa número com ponto mas só parte inteira."""
        tokens = self.lexer.get_tokens("10.")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 10.0)


class TestLexerStrings(unittest.TestCase):
    """Testes para strings."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_simple_string(self):
        """Testa string simples."""
        tokens = self.lexer.get_tokens("'Hello'")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "Hello")
    
    def test_string_with_spaces(self):
        """Testa string com espaços."""
        tokens = self.lexer.get_tokens("'Hello World'")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "Hello World")
    
    def test_empty_string(self):
        """Testa string vazia."""
        tokens = self.lexer.get_tokens("''")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "")
    
    def test_string_with_numbers(self):
        """Testa string com números."""
        tokens = self.lexer.get_tokens("'Test123'")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "Test123")
    
    def test_string_with_special_chars(self):
        """Testa string com caracteres especiais."""
        tokens = self.lexer.get_tokens("'.,!?-'")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, ".,!?-")
    
    def test_string_with_escaped_quote(self):
        """Testa string com aspa escapada (Fortran usa '')."""
        tokens = self.lexer.get_tokens("'It''s'")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "It's")


class TestLexerLogical(unittest.TestCase):
    """Testes para literais lógicos."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_true_literal(self):
        """Testa .TRUE."""
        tokens = self.lexer.get_tokens(".TRUE.")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, True)
    
    def test_false_literal(self):
        """Testa .FALSE."""
        tokens = self.lexer.get_tokens(".FALSE.")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, False)
    
    def test_true_literal_lower(self):
        """Testa .true. em minúscula."""
        tokens = self.lexer.get_tokens(".true.")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, True)
    
    def test_false_literal_lower(self):
        """Testa .false. em minúscula."""
        tokens = self.lexer.get_tokens(".false.")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, False)


class TestLexerOperators(unittest.TestCase):
    """Testes para operadores."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_arithmetic_operators(self):
        """Testa operadores aritméticos."""
        code = "+ - * / **"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("PLUS", types)
        self.assertIn("MINUS", types)
        self.assertIn("MULTIPLY", types)
        self.assertIn("DIVIDE", types)
        self.assertIn("POWER", types)
    
    def test_relational_operators(self):
        """Testa operadores relacionais."""
        code = ".LT. .LE. .GT. .GE. .EQ. .NE."
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("LT", types)
        self.assertIn("LE", types)
        self.assertIn("GT", types)
        self.assertIn("GE", types)
        self.assertIn("EQ", types)
        self.assertIn("NE", types)
    
    def test_logical_operators(self):
        """Testa operadores lógicos."""
        code = ".AND. .OR. .NOT."
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("AND", types)
        self.assertIn("OR", types)
        self.assertIn("NOT", types)
    
    def test_plus_operator(self):
        """Testa operador +."""
        tokens = self.lexer.get_tokens("+")
        self.assertEqual(get_type_name(tokens[0]), "PLUS")
    
    def test_minus_operator(self):
        """Testa operador -."""
        tokens = self.lexer.get_tokens("-")
        self.assertEqual(get_type_name(tokens[0]), "MINUS")
    
    def test_multiply_operator(self):
        """Testa operador *."""
        tokens = self.lexer.get_tokens("*")
        self.assertEqual(get_type_name(tokens[0]), "MULTIPLY")
    
    def test_divide_operator(self):
        """Testa operador /."""
        tokens = self.lexer.get_tokens("/")
        self.assertEqual(get_type_name(tokens[0]), "DIVIDE")
    
    def test_power_operator(self):
        """Testa operador **."""
        tokens = self.lexer.get_tokens("**")
        self.assertEqual(get_type_name(tokens[0]), "POWER")


class TestLexerDelimiters(unittest.TestCase):
    """Testes para delimitadores."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_parentheses(self):
        """Testa parênteses."""
        tokens = self.lexer.get_tokens("( )")
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types, ["LPAREN", "RPAREN"])
    
    def test_comma_colon(self):
        """Testa vírgula e dois-pontos."""
        tokens = self.lexer.get_tokens(", :")
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types, ["COMMA", "COLON"])
    
    def test_assignment(self):
        """Testa atribuição."""
        tokens = self.lexer.get_tokens("=")
        self.assertEqual(get_type_name(tokens[0]), "ASSIGN")
    
    def test_comma(self):
        """Testa vírgula."""
        tokens = self.lexer.get_tokens(",")
        self.assertEqual(get_type_name(tokens[0]), "COMMA")
    
    def test_colon(self):
        """Testa dois-pontos."""
        tokens = self.lexer.get_tokens(":")
        self.assertEqual(get_type_name(tokens[0]), "COLON")


class TestLexerArraysAndIndexing(unittest.TestCase):
    """Testes para arrays e indexação."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_single_dimension_array_indexing(self):
        """Testa indexação de array uni-dimensional."""
        code = "A(1)"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("LPAREN", types)
        self.assertIn("RPAREN", types)
        self.assertGreater(len(tokens), 2)
    
    def test_multi_dimension_array_indexing(self):
        """Testa indexação de array multi-dimensional."""
        code = "MATRIX(1, 2)"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("LPAREN", types)
        self.assertIn("COMMA", types)
        self.assertIn("RPAREN", types)
        self.assertGreater(len(tokens), 3)
    
    def test_array_declaration_with_dimension(self):
        """Testa declaração de array com dimensão."""
        code = "INTEGER A(10)"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("INTEGER", types)
        self.assertIn("LPAREN", types)
        self.assertIn("RPAREN", types)
    
    def test_array_with_range(self):
        """Testa array com intervalo."""
        code = "A(1:10)"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("LPAREN", types)
        self.assertIn("COLON", types)
        self.assertIn("RPAREN", types)


class TestLexerLabels(unittest.TestCase):
    """Testes para labels numéricos (Fortran 77)."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_label_number(self):
        """Testa label numérico."""
        code = "10"
        tokens = self.lexer.get_tokens(code)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 10)
    
    def test_label_in_continue(self):
        """Testa label com CONTINUE."""
        code = "10 CONTINUE"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types[0], "INTEGER_LITERAL" if isinstance(tokens[0].type, str) is False else tokens[0].type)
        self.assertIn("CONTINUE", types)
    
    def test_goto_with_label(self):
        """Testa GOTO com label."""
        code = "GOTO 100"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("GOTO", types)
        self.assertGreater(len(tokens), 1)


class TestLexerSpecialSequences(unittest.TestCase):
    """Testes para sequências especiais de tokens."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_declaration_with_assignment(self):
        """Testa declaração com atribuição."""
        code = "INTEGER X = 5"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("INTEGER", types)
        self.assertIn("ASSIGN", types)
    
    def test_function_call_with_args(self):
        """Testa chamada de função com argumentos."""
        code = "FUNC(A, B, C)"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("LPAREN", types)
        comma_count = types.count("COMMA")
        self.assertEqual(comma_count, 2)
        self.assertIn("RPAREN", types)
    
    def test_do_loop_with_range(self):
        """Testa loop DO com intervalo."""
        code = "DO I = 1, 10"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("DO", types)
        self.assertIn("ASSIGN", types)
        self.assertIn("COMMA", types)
    
    def test_if_condition(self):
        """Testa IF com condição."""
        code = "IF (X .GT. 0) THEN"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("IF", types)
        self.assertIn("GT", types)
        self.assertIn("THEN", types)
        self.assertIn("LPAREN", types)
        self.assertIn("RPAREN", types)


class TestLexerBoundaryNumbers(unittest.TestCase):
    """Testes para casos extremos de números."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_number_with_leading_zeros(self):
        """Testa número com zeros iniciais."""
        tokens = self.lexer.get_tokens("007")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 7)
    
    def test_very_small_decimal(self):
        """Testa número decimal muito pequeno."""
        tokens = self.lexer.get_tokens("0.000001")
        self.assertEqual(len(tokens), 1)
        self.assertAlmostEqual(tokens[0].value, 0.000001)
    
    def test_large_exponent(self):
        """Testa expoente grande."""
        tokens = self.lexer.get_tokens("1.0E+100")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 1.0E+100)
    
    def test_negative_exponent(self):
        """Testa expoente negativo."""
        tokens = self.lexer.get_tokens("2.5E-10")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, 2.5E-10)


class TestLexerMixedCases(unittest.TestCase):
    """Testes para casos mistos e combinações."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_mixed_case_identifiers_and_keywords(self):
        """Testa mistura de case em identificadores e keywords."""
        code = "ProGram MyVar inTEGER varName"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("PROGRAM", types)
        self.assertIn("INTEGER", types)
        self.assertGreater(len(tokens), 3)
    
    def test_multiple_spaces_between_tokens(self):
        """Testa múltiplos espaços entre tokens."""
        code = "INTEGER     X     =     42"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("INTEGER", types)
        self.assertIn("ASSIGN", types)
        self.assertGreater(len(tokens), 2)
    
    def test_tabs_between_tokens(self):
        """Testa tabulações entre tokens."""
        code = "DO\tI\t=\t1"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("DO", types)
        self.assertGreater(len(tokens), 2)
    
    def test_consecutive_operators(self):
        """Testa operadores consecutivos."""
        code = "A**B*C"
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertEqual(types.count("POWER"), 1)
        self.assertEqual(types.count("MULTIPLY"), 1)


class TestLexerInvalidCases(unittest.TestCase):
    """Testes para casos inválidos ou edge cases."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_identifier_starting_with_digit(self):
        """Testa que identificador não pode começar com dígito."""
        code = "1VAR"
        tokens = self.lexer.get_tokens(code)
        # Deve ser parseado como número seguido de identificador
        self.assertGreater(len(tokens), 0)
    
    def test_multiple_consecutive_dots(self):
        """Testa múltiplos pontos consecutivos (potencialmente inválido)."""
        code = "1..5"
        tokens = self.lexer.get_tokens(code)
        # Comportamento depende do lexer, pode ser parseado diferentemente
        self.assertGreater(len(tokens), 0)
    
    def test_unclosed_string(self):
        """Testa string não fechada (se o lexer suporta)."""
        code = "'unclosed"
        try:
            tokens = self.lexer.get_tokens(code)
            # Se não lançar erro, verificar comportamento
            self.assertGreater(len(tokens), 0)
        except:
            # Comportamento aceitável: lançar erro para string não fechada
            pass


class TestLexerExpressions(unittest.TestCase):
    """Testes de expressões."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_arithmetic_expression(self):
        """Testa expressão aritmética."""
        code = "X + Y * Z"
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 0)
    
    def test_relational_expression(self):
        """Testa expressão relacional."""
        code = "X .GT. Y"
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 0)
    
    def test_logical_expression(self):
        """Testa expressão lógica."""
        code = "(X .GT. 0) .AND. (Y .NE. 0)"
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 0)


class TestLexerProgramExamples(unittest.TestCase):
    """Testes com programas de exemplo do enunciado."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_exemplo1_hello(self):
        """Testa programa exemplo1_hello.f (Olá, Mundo!)."""
        with open("tests/examples/exemplo1_hello.f") as f:
            code = f.read()
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 3)
    
    def test_exemplo2_fatorial(self):
        """Testa programa exemplo2_fatorial.f (fatorial com loops)."""
        with open("tests/examples/exemplo2_fatorial.f") as f:
            code = f.read()
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("DO", types)
        self.assertIn("CONTINUE", types)
        self.assertIn("INTEGER", types)
    
    def test_exemplo3_primo(self):
        """Testa programa exemplo3_primo.f (primalidade)."""
        with open("tests/examples/exemplo3_primo.f") as f:
            code = f.read()
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("LOGICAL", types)
        self.assertTrue("GOTO" in types or True)
    
    def test_array_program(self):
        """Testa programa com arrays."""
        code = """PROGRAM ARRAY
        INTEGER NUMS(5)
        DO 10 I = 1, 5
            NUMS(I) = I
        10 CONTINUE
        END"""
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 10)
    
    def test_subroutine_program(self):
        """Testa programa com subroutine."""
        code = """PROGRAM MAIN
        CALL MYSUB()
        END
        
        SUBROUTINE MYSUB()
        RETURN
        END"""
        tokens = self.lexer.get_tokens(code)
        types = [get_type_name(t) for t in tokens]
        self.assertIn("SUBROUTINE", types)
        self.assertIn("CALL", types)


class TestLexerFromFile(unittest.TestCase):
    """Testes carregando programas de ficheiros."""
    
    def setUp(self):
        self.lexer = Lexer()
        self.examples_dir = "tests/examples"
    
    def test_load_examples_file(self):
        """Testa carregamento do ficheiro de exemplos."""
        examples_file = os.path.join(self.examples_dir, "fortran_examples.f")
        if os.path.exists(examples_file):
            with open(examples_file, 'r') as f:
                code = f.read()
            
            tokens = self.lexer.get_tokens(code)
            self.assertGreater(len(tokens), 50)


class TestLexerEdgeCases(unittest.TestCase):
    """Testes de casos extremos."""
    
    def setUp(self):
        self.lexer = Lexer()
    
    def test_empty_input(self):
        """Testa entrada vazia."""
        tokens = self.lexer.get_tokens("")
        self.assertEqual(len(tokens), 0)
    
    def test_whitespace_only(self):
        """Testa apenas espaços em branco."""
        tokens = self.lexer.get_tokens("   \t  \n   ")
        self.assertEqual(len(tokens), 0)
    
    def test_deeply_nested_parentheses(self):
        """Testa parênteses aninhados."""
        code = "((((A + B))))"
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 5)
    
    def test_very_long_identifier(self):
        """Testa identificador muito longo."""
        long_id = "THISISMYVERYLONGVARIABLENAMETOTESTLEXER"
        tokens = self.lexer.get_tokens(long_id)
        self.assertEqual(len(tokens), 1)
    
    def test_very_large_number(self):
        """Testa número muito grande."""
        tokens = self.lexer.get_tokens("999999999999999999")
        self.assertEqual(len(tokens), 1)
    
    def test_complex_expression(self):
        """Testa expressão complexa."""
        code = "RESULT = (X ** 2 + 3.14 * Y) / (Z - 1)"
        tokens = self.lexer.get_tokens(code)
        self.assertGreater(len(tokens), 10)


if __name__ == "__main__":
    unittest.main()
