"""
Representação Intermediária (IR)
=================================

Define a representação intermediária do programa para otimização e
geração de código.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum


class IROpcode(Enum):
    """Operações disponíveis na IR."""
    
    # Aritmética
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    POW = "pow"
    MOD = "mod"
    
    # Lógica
    AND = "and"
    OR = "or"
    NOT = "not"
    
    # Comparação
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"
    EQ = "eq"
    NE = "ne"
    
    # Controle de fluxo
    GOTO = "goto"
    COND_GOTO = "cond_goto"
    LABEL = "label"
    
    # Atribuição e entrada/saída
    ASSIGN = "assign"
    READ = "read"
    WRITE = "write"
    
    # Chamadas de função
    CALL = "call"
    RETURN = "return"


@dataclass
class IRInstruction:
    """
    Instrução da Representação Intermediária.
    
    Attributes:
        opcode: Tipo de operação
        result: Variável que recebe o resultado
        arg1, arg2: Argumentos da operação
        label: Label para instruções de salto
    """
    opcode: IROpcode
    result: Optional[str] = None
    arg1: Optional[Any] = None
    arg2: Optional[Any] = None
    label: Optional[int] = None
    
    def __repr__(self):
        if self.result:
            return f"{self.result} = {self.opcode.value} {self.arg1} {self.arg2}"
        return f"{self.opcode.value} {self.arg1} {self.arg2}"


@dataclass
class IRProgram:
    """
    Programa em representação intermediária.
    
    TODO: No futuro, pode decidir substituir esta representação 
    por outro formato (ex: SSA, Stack-based) caso a VM obrigue.
    Como a arquitetura é modular, basta criar uma nova dataclass aqui e atualizar `codegen/vm_codegen.py`.
    """
    name: str
    instructions: List[IRInstruction] = field(default_factory=list)
    variables: Dict[str, dict] = field(default_factory=dict)
    
    def add_instruction(self, instruction: IRInstruction):
        """Adiciona uma instrução ao programa."""
        self.instructions.append(instruction)
