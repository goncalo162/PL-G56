"""
Otimizador de Representação Intermediária
==========================================

Implementa passes de otimização sobre a IR.
"""

from src.codegen.ir import IRProgram, IRInstruction, IROpcode


class IROptimizer:
    """
    Otimizador de IR.
    
    Implementa passes de otimização:
    - Eliminação de código morto
    - Propagação de constantes
    - Simplificação de expressões
    """
    
    def __init__(self):
        self.optimizations_applied = []
    
    def optimize(self, ir_program: IRProgram) -> IRProgram:
        """
        Aplica passes de otimização.
        
        Args:
            ir_program: Programa em IR
            
        Returns:
            IRProgram otimizado
        """
        # Pass 1: Eliminação de código morto
        ir_program = self._eliminate_dead_code(ir_program)
        self.optimizations_applied.append("dead_code_elimination")
        
        # Pass 2: Propagação de constantes (simplificado)
        ir_program = self._constant_propagation(ir_program)
        self.optimizations_applied.append("constant_propagation")
        
        return ir_program
    
    def _eliminate_dead_code(self, ir_program: IRProgram) -> IRProgram:
        """
        Remove instruções com resultados não utilizados.
        
        Simplificação: Remove instruções cujo resultado não é usado.
        """
        # Marcar instruções usadas
        used = set()
        
        for instr in ir_program.instructions:
            if instr.arg1:
                used.add(instr.arg1)
            if instr.arg2:
                used.add(instr.arg2)
        
        # Manter instruções com efeito colateral ou usadas
        filtered = []
        for instr in ir_program.instructions:
            # Sempre manter instruções de controle e I/O
            if instr.opcode in [IROpcode.LABEL, IROpcode.GOTO, IROpcode.COND_GOTO,
                               IROpcode.READ, IROpcode.WRITE, IROpcode.CALL,
                               IROpcode.RETURN]:
                filtered.append(instr)
            # Manter se resultado é usado
            elif instr.result in used or instr.result is None:
                filtered.append(instr)
        
        ir_program.instructions = filtered
        return ir_program
    
    def _constant_propagation(self, ir_program: IRProgram) -> IRProgram:
        """
        Substitui variáveis por constantes quando possível.
        
        Simplificação: Detecta atribuições de constantes e substitui.
        """
        constants = {}
        
        # Primeira passagem: encontrar constantes
        for instr in ir_program.instructions:
            if instr.opcode == IROpcode.ASSIGN:
                try:
                    # Se arg1 é constante
                    val = int(instr.arg1) if isinstance(instr.arg1, (int, str)) else None
                    if val is not None:
                        constants[instr.result] = val
                except (ValueError, TypeError):
                    pass
        
        # Segunda passagem: substituição
        for instr in ir_program.instructions:
            if instr.arg1 in constants:
                instr.arg1 = constants[instr.arg1]
            if instr.arg2 in constants:
                instr.arg2 = constants[instr.arg2]
        
        return ir_program
    
    def get_report(self) -> str:
        """Retorna relatório de otimizações aplicadas."""
        return f"Otimizações: {', '.join(self.optimizations_applied)}"
