"""
Otimizador de Representação Intermediária
==========================================

Implementa passes de otimização sobre a IR.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

from src.codegen.ir import IRInstruction, IRProgram
from src.optimizer.optimizations import (
    AlgebraicSimplification,
    CommonSubexpressionElimination,
    ConstantFolding,
    ConstantPropagation,
    ControlFlowSimplification,
    DeadCodeElimination,
    LocalTempForwarding,
    LoopUnrolling,
)


class IROptimizer:
    """
    Otimizador de IR.

    Implementa uma pipeline simples de passes:
    - Constant Folding
    - Constant Propagation
    - Algebraic Simplification
    - Common Subexpression Elimination
    - Local Temporary Forwarding
    - Control Flow Simplification
    - Dead Code Elimination
    - Loop Unrolling (placeholder seguro)
    """

    def __init__(self):
        self.optimizations_applied = []
        self._pipeline: List[Tuple[str, Callable[[list], list]]] = [
            ("constant_folding", ConstantFolding.apply),
            ("constant_propagation", ConstantPropagation.apply),
            ("algebraic_simplification", AlgebraicSimplification.apply),
            ("constant_folding_after_algebraic", ConstantFolding.apply),
            ("common_subexpression_elimination", CommonSubexpressionElimination.apply),
            ("local_temp_forwarding", LocalTempForwarding.apply),
            ("control_flow_simplification", ControlFlowSimplification.apply),
            ("dead_code_elimination", DeadCodeElimination.apply),
            ("loop_unrolling", LoopUnrolling.apply),
        ]

    def optimize(self, ir_program: IRProgram) -> IRProgram:
        """
        Aplica passes de otimização.

        Args:
            ir_program: Programa em IR

        Returns:
            IRProgram otimizado
        """
        self.optimizations_applied = []
        instructions = list(ir_program.instructions)
        for pass_name, pass_fn in self._pipeline:
            before = self._instruction_signature(instructions)
            instructions = pass_fn(instructions)
            after = self._instruction_signature(instructions)

            if before != after:
                self.optimizations_applied.append(pass_name)

        ir_program.instructions = instructions
        return ir_program

    @staticmethod
    def _instruction_signature(instructions: List[IRInstruction]) -> List[Tuple]:
        """Cria uma assinatura simples das instruções para comparação de mudanças."""
        return [
            (instr.opcode, instr.result, instr.arg1, instr.arg2, instr.label)
            for instr in instructions
        ]

    def get_report(self) -> str:
        """Retorna relatório de otimizações aplicadas."""
        total = len(self.optimizations_applied)
        if total == 0:
            return "Otimizações aplicadas: 0 (nenhuma alteração)"
        return (
            f"Otimizações aplicadas: {total} "
            f"({', '.join(self.optimizations_applied)})"
        )
