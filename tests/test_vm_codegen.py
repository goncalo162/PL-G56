"""Testes para a geração de código da EWVM a partir da IR."""

import unittest

from src.codegen.ir import IRInstruction, IRProgram, IROpcode
from src.codegen.vm_codegen import VMCodeGenerator


class TestVMCodeGenerator(unittest.TestCase):
    """Testes unitários e de integração para o VMCodeGenerator."""

    def setUp(self):
        self.codegen = VMCodeGenerator()

    def _generate(self, ir_program: IRProgram) -> str:
        return self.codegen.generate_vm_code(ir_program)

    def test_generate_vm_code_resets_state_between_calls(self):
        first = IRProgram(name="FIRST")
        first.variables = {"X": {"type": "INTEGER"}}
        first.emit_assign("X", 1)

        second = IRProgram(name="SECOND")
        second.variables = {"Y": {"type": "INTEGER"}}
        second.emit_assign("Y", 2)

        output1 = self._generate(first)
        output2 = self._generate(second)

        self.assertIn("X: DS 1", output1)
        self.assertNotIn("Y: DS 1", output1)
        self.assertIn("Y: DS 1", output2)
        self.assertNotIn("X: DS 1", output2)

    def test_output_contains_sections_and_entrypoint(self):
        ir_program = IRProgram(name="MAIN")
        output = self._generate(ir_program)

        self.assertIn("SECTION .data", output)
        self.assertIn("SECTION .text", output)
        self.assertIn("start", output)
        self.assertIn("jump main", output)
        self.assertIn("stop", output)

    def test_allocates_scalar_variables_and_temporaries(self):
        ir_program = IRProgram(name="ALLOC")
        ir_program.variables = {"X": {"type": "INTEGER"}, "Y": {"type": "REAL"}}
        ir_program.emit_assign("X", 10)
        ir_program.emit_binop(IROpcode.ADD, "_t1", "X", 2)

        output = self._generate(ir_program)

        self.assertIn("X: DS 1", output)
        self.assertIn("Y: DS 1", output)
        self.assertIn("_t1: DS 1", output)

    def test_allocates_array_by_dimension_size(self):
        ir_program = IRProgram(name="ARRAYS")
        ir_program.variables = {"ARR": {"type": "INTEGER", "dims": [(1, 4)]}}

        output = self._generate(ir_program)

        self.assertIn("ARR: DS 4", output)

    def test_integer_assignment_emits_pushi_storeg(self):
        ir_program = IRProgram(name="ASSIGN")
        ir_program.variables = {"X": {"type": "INTEGER"}}
        ir_program.emit_assign("X", 42)

        output = self._generate(ir_program)

        self.assertIn("pushi 42", output)
        self.assertIn("storeg 0", output)

    def test_float_assignment_emits_pushf_storeg(self):
        ir_program = IRProgram(name="ASSIGNF")
        ir_program.variables = {"R": {"type": "REAL"}}
        ir_program.emit_assign("R", 3.5)

        output = self._generate(ir_program)

        self.assertIn("pushf 3.5", output)
        self.assertIn("storeg 0", output)

    def test_binary_integer_operations_emit_expected_vm_opcodes(self):
        ir_program = IRProgram(name="BIN")
        ir_program.variables = {"A": {"type": "INTEGER"}, "B": {"type": "INTEGER"}, "C": {"type": "INTEGER"}}
        ir_program.emit_binop(IROpcode.ADD, "C", "A", "B")
        ir_program.emit_binop(IROpcode.SUB, "C", "A", "B")
        ir_program.emit_binop(IROpcode.MUL, "C", "A", "B")
        ir_program.emit_binop(IROpcode.DIV, "C", "A", "B")
        ir_program.emit_binop(IROpcode.MOD, "C", "A", "B")
        ir_program.emit_binop(IROpcode.POW, "C", "A", "B")
        ir_program.emit_binop(IROpcode.EQ, "C", "A", "B")
        ir_program.emit_binop(IROpcode.NE, "C", "A", "B")
        ir_program.emit_binop(IROpcode.LT, "C", "A", "B")
        ir_program.emit_binop(IROpcode.LE, "C", "A", "B")
        ir_program.emit_binop(IROpcode.GT, "C", "A", "B")
        ir_program.emit_binop(IROpcode.GE, "C", "A", "B")
        ir_program.emit_binop(IROpcode.AND, "C", "A", "B")
        ir_program.emit_binop(IROpcode.OR, "C", "A", "B")

        output = self._generate(ir_program)

        self.assertIn("add", output)
        self.assertIn("sub", output)
        self.assertIn("mul", output)
        self.assertIn("div", output)
        self.assertIn("mod", output)
        self.assertIn("pow", output)
        self.assertIn("equal", output)
        self.assertIn("not", output)
        self.assertIn("inf", output)
        self.assertIn("infeq", output)
        self.assertIn("sup", output)
        self.assertIn("supeq", output)
        self.assertIn("and", output)
        self.assertIn("or", output)

    def test_float_binary_operation_uses_float_opcode(self):
        ir_program = IRProgram(name="FLOATBIN")
        ir_program.variables = {"A": {"type": "REAL"}, "B": {"type": "REAL"}, "C": {"type": "REAL"}}
        ir_program.emit_binop(IROpcode.ADD, "C", "A", "B")

        output = self._generate(ir_program)

        self.assertIn("fadd", output)
        self.assertNotIn("\nadd\n", output)

    def test_unary_operations_emit_neg_and_not(self):
        ir_program = IRProgram(name="UNARY")
        ir_program.variables = {"X": {"type": "INTEGER"}, "Y": {"type": "INTEGER"}}
        ir_program.emit_unop(IROpcode.UMINUS, "X", 7)
        ir_program.emit_unop(IROpcode.NOT, "Y", 0)

        output = self._generate(ir_program)

        self.assertIn("neg", output)
        self.assertIn("not", output)

    def test_labels_and_goto_translate_directly(self):
        ir_program = IRProgram(name="FLOW")
        ir_program.emit_label("main")
        ir_program.emit_goto("END")

        output = self._generate(ir_program)

        self.assertIn("main:", output)
        self.assertIn("jump END", output)

    def test_if_false_and_if_goto_translate_to_jz(self):
        ir_program = IRProgram(name="IFS")
        ir_program.variables = {"COND": {"type": "INTEGER"}}
        ir_program.emit_if_false("COND", "ELSE")
        ir_program.emit_if_goto("COND", "THEN")

        output = self._generate(ir_program)

        self.assertIn("jz ELSE", output)
        self.assertIn("jz THEN", output)
        self.assertIn("not", output)

    def test_read_statement_applies_type_conversion(self):
        ir_program = IRProgram(name="READS")
        ir_program.variables = {"I": {"type": "INTEGER"}, "R": {"type": "REAL"}, "S": {"type": "CHARACTER"}}
        ir_program.emit_read("I")
        ir_program.emit_read("R")
        ir_program.emit_read("S")

        output = self._generate(ir_program)

        self.assertIn("read", output)
        self.assertIn("atoi", output)
        self.assertIn("atof", output)
        self.assertIn("storeg 0", output)
        self.assertIn("storeg 1", output)
        self.assertIn("storeg 2", output)

    def test_write_statement_chooses_write_variant(self):
        ir_program = IRProgram(name="WRITES")
        ir_program.variables = {"I": {"type": "INTEGER"}, "R": {"type": "REAL"}, "S": {"type": "CHARACTER"}}
        ir_program.emit_write(10)
        ir_program.emit_write(3.14)
        ir_program.emit_write("hello")
        ir_program.emit_assign("I", 1)
        ir_program.emit_write("I")
        ir_program.emit_assign("R", 2.5)
        ir_program.emit_write("R")
        ir_program.emit_assign("S", "world")
        ir_program.emit_write("S")

        output = self._generate(ir_program)

        self.assertIn("writei", output)
        self.assertIn("writef", output)
        self.assertIn("writes", output)

    def test_call_translation_pushes_address_and_stores_result(self):
        ir_program = IRProgram(name="CALLS")
        ir_program.variables = {"X": {"type": "INTEGER"}, "Y": {"type": "INTEGER"}}
        ir_program.emit_label("F")
        ir_program.emit_enter_scope("F")
        ir_program.emit_return(1)
        ir_program.emit_leave_scope("F")
        ir_program.emit_call("F", 0, "X")

        output = self._generate(ir_program)

        self.assertIn("pusha F", output)
        self.assertIn("call", output)
        self.assertIn("storeg 0", output)

    def test_return_with_and_without_value(self):
        ir_program = IRProgram(name="RET")
        ir_program.variables = {"X": {"type": "INTEGER"}}
        ir_program.emit_return(10)
        ir_program.emit_return()

        output = self._generate(ir_program)

        self.assertIn("pushi 10", output)
        self.assertIn("return", output)

    def test_array_load_and_store_translate_using_padd_and_load_store(self):
        ir_program = IRProgram(name="ARRAYOPS")
        ir_program.variables = {"ARR": {"type": "INTEGER", "dims": [(1, 4)]}, "I": {"type": "INTEGER"}, "X": {"type": "INTEGER"}}
        ir_program.emit_array_load("X", "ARR", "I")
        ir_program.emit_array_store("ARR", "I", "X")

        output = self._generate(ir_program)

        self.assertIn("padd", output)
        self.assertIn("load 0", output)
        self.assertIn("store 0", output)

    def test_scope_markers_are_documented_as_comments(self):
        ir_program = IRProgram(name="SCOPES")
        ir_program.emit(IRInstruction(IROpcode.ENTER_SCOPE, label="main"))
        ir_program.emit(IRInstruction(IROpcode.LEAVE_SCOPE, label="main"))

        output = self._generate(ir_program)

        self.assertIn("enter main scope", output)
        self.assertIn("leave scope main", output)

    def test_example_simple_program(self):
        ir_program = IRProgram(name="EXAMPLE")
        ir_program.variables = {"A": {"type": "INTEGER"}, "B": {"type": "INTEGER"}, "C": {"type": "INTEGER"}}
        ir_program.emit_assign("A", 5)
        ir_program.emit_assign("B", 7)
        ir_program.emit_binop(IROpcode.ADD, "C", "A", "B")
        ir_program.emit_write("C")

        output = self._generate(ir_program)

        self.assertIn("pushi 5", output)
        self.assertIn("pushi 7", output)
        self.assertIn("add", output)
        self.assertIn("writei", output)

    def test_empty_program_still_produces_valid_output(self):
        ir_program = IRProgram(name="EMPTY")
        output = self._generate(ir_program)

        self.assertIn("SECTION .data", output)
        self.assertIn("SECTION .text", output)
        self.assertIn("start", output)
        self.assertIn("stop", output)


if __name__ == "__main__":
    unittest.main()
