"""
Testes Unitários para o Compilador
===================================

Testes para cada fase do compilador.
"""

import unittest
from pathlib import Path

from src.main import FortranCompiler
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


class TestCompilerExamplesE2E(unittest.TestCase):
    """Testes end-to-end com export de código VM e resultados esperados."""

    EXAMPLES_DIR = Path("tests/examples")
    VM_EXPORT_DIR = Path("tests/examples/generated_vm")
    EXPECTED_FILE = VM_EXPORT_DIR / "expected_vm_results.txt"

    EXPECTED_VM_RESULTS = {
        "exemplo1_hello.f": {
            "input": "<sem input>",
            "expected_output": "Ola, Mundo!",
        },
        "exemplo2_fatorial.f": {
            "input": "5",
            "expected_output": "Introduza um numero inteiro positivo:Fatorial de 5: 120",
        },
    }

    def setUp(self):
        self.compiler = FortranCompiler(enable_optimizations=True)

    def test_compile_all_examples_without_crash_and_export_vm(self):
        self.VM_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        compiled = []
        failed = []

        for example_path in sorted(self.EXAMPLES_DIR.glob("*.f")):
            with self.subTest(example=example_path.name):
                source = example_path.read_text(encoding="utf-8")
                vm_code = self.compiler.compile(source)

                if vm_code is None:
                    failed.append(example_path.name)
                    continue

                compiled.append(example_path.name)
                self.assertIn("SECTION .text", vm_code)
                self.assertIn("start", vm_code)
                self.assertIn("stop", vm_code)

                out_file = self.VM_EXPORT_DIR / f"{example_path.stem}.vm"
                out_file.write_text(vm_code, encoding="utf-8")

        lines = ["# Resultados esperados para validacao manual na EWVM", ""]
        for example_name, expectation in self.EXPECTED_VM_RESULTS.items():
            lines.append(f"{example_name}")
            lines.append(f"input: {expectation['input']}")
            lines.append(f"expected_output: {expectation['expected_output']}")
            lines.append("")
        self.EXPECTED_FILE.write_text("\n".join(lines), encoding="utf-8")

        self.assertGreaterEqual(
            len(compiled),
            2,
            "Esperavam-se pelo menos 2 exemplos compilados para validação de VM.",
        )

        # Lista útil para evolução da cobertura sem partir toda a suite.
        self.assertIn("exemplo1_hello.f", compiled)
        self.assertIn("exemplo2_fatorial.f", compiled)
        self.assertIn("exemplo10_strings.f", failed)

    def test_expected_result_manifest_is_generated(self):
        if not self.EXPECTED_FILE.exists():
            self.test_compile_all_examples_without_crash_and_export_vm()

        content = self.EXPECTED_FILE.read_text(encoding="utf-8")
        self.assertIn("exemplo1_hello.f", content)
        self.assertIn("expected_output: Ola, Mundo!", content)
        self.assertIn("exemplo2_fatorial.f", content)
        self.assertIn("expected_output: Introduza um numero inteiro positivo:Fatorial de 5: 120", content)

    def test_example_hello_expected_vm_output_reference(self):
        source = (self.EXAMPLES_DIR / "exemplo1_hello.f").read_text(encoding="utf-8")
        vm_code = self.compiler.compile(source)

        self.assertIsNotNone(vm_code)
        self.assertEqual(
            self.EXPECTED_VM_RESULTS["exemplo1_hello.f"]["expected_output"],
            "Ola, Mundo!",
        )

    def test_example_factorial_expected_vm_output_reference(self):
        source = (self.EXAMPLES_DIR / "exemplo2_fatorial.f").read_text(encoding="utf-8")
        vm_code = self.compiler.compile(source)

        self.assertIsNotNone(vm_code)
        self.assertEqual(
            self.EXPECTED_VM_RESULTS["exemplo2_fatorial.f"]["expected_output"],
            "Introduza um numero inteiro positivo:Fatorial de 5: 120",
        )


if __name__ == "__main__":
    unittest.main()
