"""
Geração de Código para Máquina Virtual
======================================

Converte IR para código executável da máquina virtual.
"""

from src.codegen.ir import IRProgram, IRInstruction, IROpcode


class VMCodeGenerator:
    """
    Gerador de código para máquina virtual.
    
    Converte programa em IR para instruções da VM.
    """
    
    def __init__(self):
        self.instructions = []
        self.memory_map = {}
        self.next_address = 0
    
    def generate_vm_code(self, ir_program: IRProgram) -> str:
        """
        Gera código VM a partir de IR.
        
        Args:
            ir_program: Programa em representação intermediária
            
        Returns:
            String contendo código VM
        """
        # TODO: Iterar sobre ir_program.instructions
        # TODO: Fazer match a cada type de IROpcode
        # TODO: Construir a string final baseada nas instruções exigidas pela VM do Projeto
        
        self._allocate_memory(ir_program)
        self._emit_header(ir_program)
        self._emit_instructions(ir_program.instructions)
        
        return self._format_output()
    
    def _allocate_memory(self, ir_program: IRProgram):
        """Aloca endereços de memória para variáveis."""
        for var_name, var_info in ir_program.variables.items():
            self.memory_map[var_name] = self.next_address
            # Cada variável ocupa 1 word (simplificado)
            self.next_address += 1
    
    def _emit_header(self, ir_program: IRProgram):
        """Emite cabeçalho do código VM."""
        self.instructions.append(f"; Programa: {ir_program.name}")
        self.instructions.append(f"; Variáveis: {len(ir_program.variables)}")
        self.instructions.append("")
    
    def _emit_instructions(self, ir_instructions):
        """Emite instruções VM."""
        for instr in ir_instructions:
            self._emit_instruction(instr)
    
    def _emit_instruction(self, instr: IRInstruction):
        """Emite uma instrução VM individual."""
        # Mapear operações IR para instruções VM
        opcode_map = {
            IROpcode.ADD: "ADD",
            IROpcode.SUB: "SUB",
            IROpcode.MUL: "MUL",
            IROpcode.DIV: "DIV",
            IROpcode.MOD: "MOD",
            IROpcode.AND: "AND",
            IROpcode.OR: "OR",
            IROpcode.NOT: "NOT",
            IROpcode.LT: "LT",
            IROpcode.LE: "LE",
            IROpcode.GT: "GT",
            IROpcode.GE: "GE",
            IROpcode.EQ: "EQ",
            IROpcode.NE: "NE",
            IROpcode.ASSIGN: "MOV",
            IROpcode.LABEL: "LABEL",
            IROpcode.GOTO: "JMP",
            IROpcode.COND_GOTO: "JZ",  # Jump if zero
            IROpcode.READ: "READ",
            IROpcode.WRITE: "WRITE",
            IROpcode.CALL: "CALL",
            IROpcode.RETURN: "RET",
        }
        
        vm_opcode = opcode_map.get(instr.opcode, "???")
        
        if instr.result:
            self.instructions.append(
                f"{vm_opcode} {instr.result} {instr.arg1} {instr.arg2}"
            )
        else:
            args = []
            if instr.arg1:
                args.append(str(instr.arg1))
            if instr.arg2:
                args.append(str(instr.arg2))
            if instr.label:
                args.append(str(instr.label))
            self.instructions.append(f"{vm_opcode} {' '.join(args)}")
    
    def _format_output(self) -> str:
        """Formata saída final."""
        return "\n".join(self.instructions)
