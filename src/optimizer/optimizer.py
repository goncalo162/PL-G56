"""
Otimizador de Representação Intermediária
==========================================

Implementa passes de otimização sobre a IR.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class OptimizationDiagnostic:
    """Resumo de uma transformação de otimização."""
    pass_name: str
    before_count: int
    after_count: int
    changed: bool

    @property
    def removed_count(self) -> int:
        return max(0, self.before_count - self.after_count)


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
        self.diagnostics: List[OptimizationDiagnostic] = []
        self.initial_instruction_count = 0
        self.final_instruction_count = 0
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
        self.diagnostics = []
        instructions = list(ir_program.instructions)
        self.initial_instruction_count = len(instructions)
        for pass_name, pass_fn in self._pipeline:
            before = self._instruction_signature(instructions)
            before_count = len(instructions)
            instructions = pass_fn(instructions)
            after = self._instruction_signature(instructions)
            after_count = len(instructions)
            changed = before != after

            self.diagnostics.append(
                OptimizationDiagnostic(pass_name, before_count, after_count, changed)
            )

            if changed:
                self.optimizations_applied.append(pass_name)

        ir_program.instructions = instructions
        self.final_instruction_count = len(instructions)
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
        if not self.optimizations_applied:
            return "Otimizações aplicadas: 0 (nenhuma alteração)"

        lines = [
            f"Otimizações aplicadas: {len(self.optimizations_applied)} "
            f"({', '.join(self.optimizations_applied)})",
            "",
            "Optimization Report",
            "===================",
        ]
        for index, diagnostic in enumerate(self.diagnostics, start=1):
            status = "alterado" if diagnostic.changed else "sem alterações"
            lines.append(f"Pass {index}: {diagnostic.pass_name} - {status}")
            if diagnostic.changed:
                lines.append(
                    f"  - Instruções: {diagnostic.before_count} -> {diagnostic.after_count}"
                )
                if diagnostic.removed_count:
                    lines.append(f"  - Removidas: {diagnostic.removed_count}")

        reduction = self.initial_instruction_count - self.final_instruction_count
        percent = 0
        if self.initial_instruction_count:
            percent = round((reduction / self.initial_instruction_count) * 100)
        lines.append(
            f"Reduction: {self.initial_instruction_count} instruções -> "
            f"{self.final_instruction_count} instruções ({percent}% ganho)"
        )
        return "\n".join(lines)
