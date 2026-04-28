"""Testes para a geração de código intermédio (TAC)."""

import unittest

from src.ast import nodes
from src.codegen.ir import IRInstruction, IRProgram, IROpcode
from src.codegen.ir_generator import CodeGenerator


class TestIRGenerator(unittest.TestCase):
    """Testes focados no visitor de geração de IR."""

    def setUp(self):
        self.codegen = CodeGenerator()
        self.codegen.ir_program = IRProgram(name="TEST")

    def test_generate_code_resets_internal_state(self):
        program = nodes.Program(name="P1")

        ir_program = self.codegen.generate_code(program)

        self.assertEqual(ir_program.name, "P1")
        self.assertEqual(self.codegen.temp_counter, 0)
        self.assertEqual(self.codegen.label_counter, 0)
        self.assertEqual(self.codegen.loop_stack, [])

    def test_new_temp_and_new_label(self):
        self.assertEqual(self.codegen.new_temp(), "_t1")
        self.assertEqual(self.codegen.new_temp(), "_t2")
        self.assertEqual(self.codegen.new_label(), "_L1")
        self.assertEqual(self.codegen.new_label("IF"), "_IF2")

    def test_visit_literal_returns_value(self):
        node = nodes.Literal(value=5, type_name="INTEGER")
        self.assertEqual(self.codegen.visit_literal(node), 5)

    def test_visit_identifier_returns_name(self):
        node = nodes.Identifier(name="X")
        self.assertEqual(self.codegen.visit_identifier(node), "X")

    def test_visit_unary_op_minus(self):
        node = nodes.UnaryOp(operator="-", operand=nodes.Identifier(name="X"))

        result = self.codegen.visit_unary_op(node)

        self.assertEqual(result, "_t1")
        self.assertEqual(len(self.codegen.ir_program.instructions), 1)
        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.UMINUS)
        self.assertEqual(instr.result, "_t1")
        self.assertEqual(instr.arg1, "X")

    def test_visit_unary_op_not(self):
        node = nodes.UnaryOp(operator=".NOT.", operand=nodes.Identifier(name="FLAG"))

        result = self.codegen.visit_unary_op(node)

        self.assertEqual(result, "_t1")
        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.NOT)
        self.assertEqual(instr.result, "_t1")
        self.assertEqual(instr.arg1, "FLAG")

    def test_visit_unary_op_unknown_operator_raises(self):
        node = nodes.UnaryOp(operator="?", operand=nodes.Identifier(name="X"))

        with self.assertRaises(ValueError):
            self.codegen.visit_unary_op(node)

    def test_visit_binary_op_add(self):
        node = nodes.BinaryOp(
            left=nodes.Identifier(name="A"),
            operator="+",
            right=nodes.Literal(value=3, type_name="INTEGER"),
        )

        result = self.codegen.visit_binary_op(node)

        self.assertEqual(result, "_t1")
        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.ADD)
        self.assertEqual(instr.result, "_t1")
        self.assertEqual(instr.arg1, "A")
        self.assertEqual(instr.arg2, 3)

    def test_visit_binary_op_comparison(self):
        node = nodes.BinaryOp(
            left=nodes.Identifier(name="A"),
            operator=".LT.",
            right=nodes.Identifier(name="B"),
        )

        result = self.codegen.visit_binary_op(node)

        self.assertEqual(result, "_t1")
        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.LT)

    def test_visit_binary_op_unknown_operator_raises(self):
        node = nodes.BinaryOp(
            left=nodes.Identifier(name="A"),
            operator="@@",
            right=nodes.Identifier(name="B"),
        )

        with self.assertRaises(ValueError):
            self.codegen.visit_binary_op(node)

    def test_visit_assignment_simple(self):
        node = nodes.Assignment(
            target=nodes.Identifier(name="X"),
            value=nodes.Literal(value=10, type_name="INTEGER"),
        )

        self.codegen.visit_assignment(node)

        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.ASSIGN)
        self.assertEqual(instr.result, "X")
        self.assertEqual(instr.arg1, 10)

    def test_visit_assignment_array_store(self):
        node = nodes.Assignment(
            target=nodes.ArrayAccess(name="ARR", indices=[nodes.Identifier(name="I")]),
            value=nodes.Literal(value=42, type_name="INTEGER"),
        )

        self.codegen.visit_assignment(node)

        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.STORE_ARRAY)
        self.assertEqual(instr.arg1, "ARR")
        self.assertEqual(instr.arg2, "I")
        self.assertEqual(instr.result, 42)

    def test_visit_variable_declaration_registers_metadata_and_init(self):
        node = nodes.VariableDeclaration(
            name="X",
            type_name="INTEGER",
            dimensions=None,
            initial_value=nodes.Literal(value=7, type_name="INTEGER"),
        )

        self.codegen.visit_variable_declaration(node)

        self.assertIn("X", self.codegen.ir_program.variables)
        self.assertEqual(self.codegen.ir_program.variables["X"]["type"], "INTEGER")
        self.assertEqual(len(self.codegen.ir_program.instructions), 1)
        self.assertEqual(self.codegen.ir_program.instructions[0].opcode, IROpcode.ASSIGN)

    def test_visit_if_statement_emits_expected_control_flow(self):
        node = nodes.IfStatement(
            condition=nodes.Identifier(name="COND"),
            then_body=[
                nodes.Assignment(
                    target=nodes.Identifier(name="X"),
                    value=nodes.Literal(value=1, type_name="INTEGER"),
                )
            ],
            else_body=[
                nodes.Assignment(
                    target=nodes.Identifier(name="X"),
                    value=nodes.Literal(value=0, type_name="INTEGER"),
                )
            ],
        )

        self.codegen.visit_if_statement(node)

        opcodes = [instr.opcode for instr in self.codegen.ir_program.instructions]
        self.assertEqual(
            opcodes,
            [IROpcode.IF_FALSE, IROpcode.ASSIGN, IROpcode.GOTO, IROpcode.LABEL, IROpcode.ASSIGN, IROpcode.LABEL],
        )

    def test_visit_do_loop_emits_expected_structure(self):
        node = nodes.DoLoop(
            variable=nodes.Identifier(name="I"),
            start=nodes.Literal(value=1, type_name="INTEGER"),
            end=nodes.Literal(value=3, type_name="INTEGER"),
            step=nodes.Literal(value=1, type_name="INTEGER"),
            body=[nodes.PrintStatement(expressions=[nodes.Identifier(name="I")])],
        )

        self.codegen.visit_do_loop(node)

        opcodes = [instr.opcode for instr in self.codegen.ir_program.instructions]
        self.assertEqual(
            opcodes,
            [IROpcode.ASSIGN, IROpcode.LABEL, IROpcode.GT, IROpcode.IF_GOTO, IROpcode.WRITE, IROpcode.LABEL, IROpcode.ADD, IROpcode.GOTO, IROpcode.LABEL],
        )

    def test_visit_do_loop_pushes_continue_target(self):
        node = nodes.DoLoop(
            variable=nodes.Identifier(name="I"),
            start=nodes.Literal(value=1, type_name="INTEGER"),
            end=nodes.Literal(value=2, type_name="INTEGER"),
            body=[nodes.ContinueStatement()],
        )

        self.codegen.visit_do_loop(node)

        gotos = [instr for instr in self.codegen.ir_program.instructions if instr.opcode == IROpcode.GOTO]
        self.assertTrue(any(instr.label == "_DO_CONT2" for instr in gotos))

    def test_visit_continue_statement_outside_loop_raises(self):
        with self.assertRaises(ValueError):
            self.codegen.visit_continue_statement(nodes.ContinueStatement())

    def test_visit_continue_statement_inside_loop_emits_goto(self):
        self.codegen.loop_stack.append("_DO_CONT1")

        self.codegen.visit_continue_statement(nodes.ContinueStatement())

        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.GOTO)
        self.assertEqual(instr.label, "_DO_CONT1")

    def test_visit_function_call_returns_temp_and_emits_call(self):
        node = nodes.FunctionCall(
            function_name="F",
            arguments=[
                nodes.Literal(value=2, type_name="INTEGER"),
                nodes.Identifier(name="X"),
            ],
        )

        result = self.codegen.visit_function_call(node)

        self.assertEqual(result, "_t1")
        opcodes = [instr.opcode for instr in self.codegen.ir_program.instructions]
        self.assertEqual(opcodes, [IROpcode.PARAM, IROpcode.PARAM, IROpcode.CALL])
        self.assertEqual(self.codegen.ir_program.instructions[-1].result, "_t1")

    def test_visit_function_call_mod_emits_mod_binop(self):
        node = nodes.FunctionCall(
            function_name="MOD",
            arguments=[
                nodes.Identifier(name="NUM"),
                nodes.Identifier(name="I"),
            ],
        )

        result = self.codegen.visit_function_call(node)

        self.assertEqual(result, "_t1")
        self.assertEqual(len(self.codegen.ir_program.instructions), 1)
        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.MOD)
        self.assertEqual(instr.arg1, "NUM")
        self.assertEqual(instr.arg2, "I")
        self.assertEqual(instr.result, "_t1")

    def test_visit_call_statement_emits_call_without_result(self):
        node = nodes.CallStatement(
            subroutine="SUBR",
            arguments=[nodes.Identifier(name="A")],
        )

        result = self.codegen.visit_call_statement(node)

        self.assertIsNone(result)
        opcodes = [instr.opcode for instr in self.codegen.ir_program.instructions]
        self.assertEqual(opcodes, [IROpcode.PARAM, IROpcode.CALL])
        self.assertIsNone(self.codegen.ir_program.instructions[-1].result)

    def test_visit_array_access_returns_temp(self):
        node = nodes.ArrayAccess(name="ARR", indices=[nodes.Identifier(name="I")])

        result = self.codegen.visit_array_access(node)

        self.assertEqual(result, "_t1")
        instr = self.codegen.ir_program.instructions[0]
        self.assertEqual(instr.opcode, IROpcode.LOAD_ARRAY)
        self.assertEqual(instr.result, "_t1")

    def test_visit_program_wraps_main_scope(self):
        program = nodes.Program(
            name="MAIN",
            declarations=[nodes.VariableDeclaration(name="X", type_name="INTEGER")],
            statements=[
                nodes.Assignment(
                    target=nodes.Identifier(name="X"),
                    value=nodes.Literal(value=1, type_name="INTEGER"),
                )
            ],
            subprograms=[],
        )

        ir_program = self.codegen.generate_code(program)

        self.assertEqual(ir_program.name, "MAIN")
        self.assertEqual(ir_program.instructions[0].opcode, IROpcode.ENTER_SCOPE)
        self.assertEqual(ir_program.instructions[-1].opcode, IROpcode.LEAVE_SCOPE)

    def test_visit_function_declaration_emits_label_and_scope(self):
        node = nodes.FunctionDeclaration(
            name="F",
            return_type="INTEGER",
            parameters=[],
            body=[nodes.ReturnStatement()],
        )

        self.codegen.visit_function_declaration(node)

        opcodes = [instr.opcode for instr in self.codegen.ir_program.instructions]
        self.assertEqual(opcodes[0], IROpcode.LABEL)
        self.assertEqual(opcodes[1], IROpcode.ENTER_SCOPE)
        self.assertEqual(opcodes[-1], IROpcode.LEAVE_SCOPE)

    def test_visit_subroutine_declaration_delegates_to_function(self):
        node = nodes.FunctionDeclaration(
            name="SUB",
            return_type="VOID",
            parameters=[],
            body=[],
        )

        self.codegen.visit_subroutine_declaration(node)

        self.assertGreaterEqual(len(self.codegen.ir_program.instructions), 2)

    def test_function_call_inside_expression_can_feed_assignment(self):
        call = nodes.FunctionCall(function_name="F", arguments=[])
        assign = nodes.Assignment(target=nodes.Identifier(name="X"), value=call)

        self.codegen.visit_assignment(assign)

        self.assertEqual(self.codegen.ir_program.instructions[-1].opcode, IROpcode.ASSIGN)
        self.assertEqual(self.codegen.ir_program.instructions[0].opcode, IROpcode.CALL)


if __name__ == "__main__":
    unittest.main()
