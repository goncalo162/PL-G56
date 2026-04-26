"""Testes para os passes de otimização da IR."""

import unittest

from src.codegen.ir import IRInstruction, IRProgram, IROpcode
from src.optimizer.optimizations import (
    CommonSubexpressionElimination,
    ConstantFolding,
    ConstantPropagation,
    DeadCodeElimination,
    LoopUnrolling,
)
from src.optimizer.optimizer import IROptimizer


class TestOptimizationPasses(unittest.TestCase):
    """Testes unitários de cada pass isolado."""

    def test_constant_folding_add_and_mul(self):
        instructions = [
            IRInstruction(IROpcode.ADD, result="t1", arg1=2, arg2=3),
            IRInstruction(IROpcode.MUL, result="t2", arg1="4", arg2="5"),
        ]

        optimized = ConstantFolding.apply(instructions)

        self.assertEqual(optimized[0].opcode, IROpcode.ASSIGN)
        self.assertEqual(optimized[0].arg1, 5)
        self.assertEqual(optimized[1].opcode, IROpcode.ASSIGN)
        self.assertEqual(optimized[1].arg1, 20)

    def test_constant_folding_comparison(self):
        instructions = [IRInstruction(IROpcode.GT, result="t1", arg1=10, arg2=3)]

        optimized = ConstantFolding.apply(instructions)

        self.assertEqual(optimized[0].opcode, IROpcode.ASSIGN)
        self.assertEqual(optimized[0].arg1, 1)

    def test_constant_folding_skips_division_by_zero(self):
        instructions = [IRInstruction(IROpcode.DIV, result="t1", arg1=10, arg2=0)]

        optimized = ConstantFolding.apply(instructions)

        self.assertEqual(optimized[0].opcode, IROpcode.DIV)

    def test_constant_propagation_replaces_arguments(self):
        instructions = [
            IRInstruction(IROpcode.ASSIGN, result="x", arg1=5),
            IRInstruction(IROpcode.ADD, result="t1", arg1="x", arg2=2),
        ]

        optimized = ConstantPropagation.apply(instructions)

        self.assertEqual(optimized[1].arg1, 5)

    def test_dead_code_elimination_removes_unused_assign(self):
        instructions = [
            IRInstruction(IROpcode.ASSIGN, result="unused", arg1=10),
            IRInstruction(IROpcode.ASSIGN, result="x", arg1=2),
            IRInstruction(IROpcode.WRITE, arg1="x"),
        ]

        optimized = DeadCodeElimination.apply(instructions)

        self.assertEqual(len(optimized), 2)
        self.assertEqual(optimized[0].result, "x")
        self.assertEqual(optimized[1].opcode, IROpcode.WRITE)

    def test_dead_code_elimination_keeps_side_effects(self):
        instructions = [
            IRInstruction(IROpcode.CALL, result="tmp", arg1="f", arg2=0),
            IRInstruction(IROpcode.RETURN),
        ]

        optimized = DeadCodeElimination.apply(instructions)

        self.assertEqual(len(optimized), 2)
        self.assertEqual(optimized[0].opcode, IROpcode.CALL)

    def test_common_subexpression_elimination_reuses_previous_result(self):
        instructions = [
            IRInstruction(IROpcode.ADD, result="t1", arg1="a", arg2="b"),
            IRInstruction(IROpcode.ADD, result="t2", arg1="a", arg2="b"),
        ]

        optimized = CommonSubexpressionElimination.apply(instructions)

        self.assertEqual(optimized[0].opcode, IROpcode.ADD)
        self.assertEqual(optimized[1].opcode, IROpcode.ASSIGN)
        self.assertEqual(optimized[1].arg1, "t1")

    def test_loop_unrolling_is_safe_noop(self):
        instructions = [IRInstruction(IROpcode.LABEL, label="L1")]

        optimized = LoopUnrolling.apply(instructions)

        self.assertEqual(len(optimized), 1)
        self.assertEqual(optimized[0].opcode, IROpcode.LABEL)


class TestIROptimizer(unittest.TestCase):
    """Testes de integração da pipeline de otimização."""

    def setUp(self):
        self.optimizer = IROptimizer()

    def test_pipeline_applies_and_tracks_changes(self):
        ir_program = IRProgram(name="P")
        ir_program.instructions = [
            IRInstruction(IROpcode.ASSIGN, result="x", arg1=5),
            IRInstruction(IROpcode.ADD, result="t1", arg1="x", arg2=3),
            IRInstruction(IROpcode.ASSIGN, result="dead", arg1=10),
            IRInstruction(IROpcode.WRITE, arg1="t1"),
        ]

        optimized = self.optimizer.optimize(ir_program)

        self.assertIs(optimized, ir_program)
        self.assertTrue(len(self.optimizer.optimizations_applied) >= 1)
        opcodes = [instr.opcode for instr in optimized.instructions]
        self.assertIn(IROpcode.WRITE, opcodes)

    def test_get_report_when_no_optimization_changes(self):
        ir_program = IRProgram(name="P")
        ir_program.instructions = [IRInstruction(IROpcode.WRITE, arg1=1)]

        self.optimizer.optimize(ir_program)
        report = self.optimizer.get_report()

        self.assertEqual(report, "Otimizações aplicadas: 0 (nenhuma alteração)")

    def test_get_report_includes_total_optimizations(self):
        ir_program = IRProgram(name="P")
        ir_program.instructions = [
            IRInstruction(IROpcode.ASSIGN, result="x", arg1=1),
            IRInstruction(IROpcode.ADD, result="t1", arg1="x", arg2=2),
            IRInstruction(IROpcode.ASSIGN, result="dead", arg1=0),
            IRInstruction(IROpcode.WRITE, arg1="t1"),
        ]

        self.optimizer.optimize(ir_program)
        report = self.optimizer.get_report()

        self.assertIn("Otimizações aplicadas:", report)
        self.assertNotIn("aplicadas: 0", report)


if __name__ == "__main__":
    unittest.main()
