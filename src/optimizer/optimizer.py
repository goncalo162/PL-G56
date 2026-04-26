"""
Otimizador de Representação Intermediária
==========================================

Implementa passes de otimização sobre a IR.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

from src.codegen.ir import IRInstruction, IRProgram
from src.optimizer.optimizations import (
    CommonSubexpressionElimination,
    ConstantFolding,
    ConstantPropagation,
    DeadCodeElimination,
    LoopUnrolling,
)


class IROptimizer:
    """
    Otimizador de IR.
    
    Implementa uma pipeline simples de passes:
    - Constant Folding
    - Constant Propagation
    - Common Subexpression Elimination
    - Dead Code Elimination
    - Loop Unrolling (placeholder seguro)
    """
    
    def __init__(self):
        # Guarda os nomes dos passes que de facto alteraram o programa.
        self.optimizations_applied = []

        # A pipeline é explícita e fácil de reordenar/estender.
        self._pipeline: List[Tuple[str, Callable[[list], list]]] = [
            ("constant_folding", ConstantFolding.apply),
            ("constant_propagation", ConstantPropagation.apply),
            ("common_subexpression_elimination", CommonSubexpressionElimination.apply),
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
        # Limpamos o histórico para cada nova execução do otimizador.
        self.optimizations_applied = []

        # Trabalhamos sobre uma cópia da lista para evitar efeitos intermédios
        # durante a iteração dos passes.
        instructions = list(ir_program.instructions)
        for pass_name, pass_fn in self._pipeline:
            # Guardamos um snapshot estrutural antes do pass.
            before = self._instruction_signature(instructions)

            # Aplicamos o pass corrente.
            instructions = pass_fn(instructions)

            # Guardamos snapshot depois do pass para perceber se houve alteração.
            after = self._instruction_signature(instructions)

            # Só registamos passes que efetivamente mudaram o programa.
            if before != after:
                self.optimizations_applied.append(pass_name)

        # No fim, substituímos a lista de instruções do programa original.
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
