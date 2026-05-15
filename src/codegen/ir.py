"""
Representação Intermediária (IR) - Código de Três Endereços (TAC)
================================================================

Define a IR usada pelo gerador de código e pelos passos de optimização.
O objectivo é manter uma estrutura simples, linear e fácil de imprimir.
Utiliza o formato de Código de Três Endereços (Three-Address Code), onde cada instrução tem no máximo três operandos.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IROpcode(Enum):
    """Operações disponíveis na IR (TAC).

    Os valores são strings para tornar a impressão da IR mais legível.
    """

    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    POW = "pow"
    MOD = "mod"
    CONCAT = "concat"

    ABS = "abs"
    MAX = "max"
    MIN = "min"
    INT = "int"
    REAL = "real"
    SQRT = "sqrt"
    SIN = "sin"
    COS = "cos"
    EXP = "exp"
    LOG = "log"
    NINT = "nint"

    AND = "and"
    OR = "or"

    UMINUS = "uminus"
    NOT = "not"

    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"
    EQ = "eq"
    NE = "ne"

    ASSIGN = "assign"

    LABEL = "label"
    GOTO = "goto"
    IF_FALSE = "if_false"
    IF_GOTO = "if_goto"
    IF_FALSE_GOTO = "if_false_goto"

    LOAD_ARRAY = "load_array"
    STORE_ARRAY = "store_array"

    READ = "read"
    WRITE = "write"

    PARAM = "param"
    CALL = "call"
    RETURN = "return"

    ENTER_SCOPE = "enter_scope"
    LEAVE_SCOPE = "leave_scope"


@dataclass
class IRInstruction:
    """Representa uma instrução individual de TAC.

    O significado dos campos depende do opcode:
    - `result` guarda o destino do resultado quando existe.
    - `arg1` e `arg2` guardam operandos, nomes, índices ou valores.
    - `label` é usado em saltos, labels e blocos de escopo.
    """

    opcode: IROpcode
    result: Optional[str] = None
    arg1: Optional[Any] = None
    arg2: Optional[Any] = None
    label: Optional[Any] = None

    def __repr__(self) -> str:
        """Devolve uma versão textual compacta da instrução.

        Este método serve sobretudo para depuração e para imprimir o TAC
        gerado em forma legível.
        """
        if self.opcode in {
            IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV,
            IROpcode.POW, IROpcode.MOD, IROpcode.CONCAT, IROpcode.MAX, IROpcode.MIN,
            IROpcode.AND, IROpcode.OR,
            IROpcode.LT, IROpcode.LE, IROpcode.GT, IROpcode.GE,
            IROpcode.EQ, IROpcode.NE,
        }:
            return f"    {self.result} = {self.arg1} {self.opcode.value} {self.arg2}"

        if self.opcode in {
            IROpcode.UMINUS, IROpcode.NOT, IROpcode.ABS, IROpcode.INT,
            IROpcode.REAL, IROpcode.SQRT, IROpcode.SIN, IROpcode.COS,
            IROpcode.EXP, IROpcode.LOG, IROpcode.NINT,
        }:
            operator_map = {
                IROpcode.UMINUS: "-", IROpcode.NOT: "!",
                IROpcode.ABS: "abs", IROpcode.INT: "int", IROpcode.REAL: "real",
                IROpcode.SQRT: "sqrt", IROpcode.SIN: "sin", IROpcode.COS: "cos",
                IROpcode.EXP: "exp", IROpcode.LOG: "log", IROpcode.NINT: "nint",
            }
            operator = operator_map[self.opcode]
            return f"    {self.result} = {operator}{self.arg1}"

        if self.opcode == IROpcode.ASSIGN:
            return f"    {self.result} = {self.arg1}"

        if self.opcode == IROpcode.LABEL:
            return f"L{self.label}:"

        if self.opcode == IROpcode.GOTO:
            return f"    GOTO L{self.label}"

        if self.opcode in {IROpcode.IF_FALSE, IROpcode.IF_FALSE_GOTO}:
            return f"    IF_FALSE {self.arg1} GOTO L{self.label}"

        if self.opcode == IROpcode.IF_GOTO:
            return f"    IF {self.arg1} GOTO L{self.label}"

        if self.opcode == IROpcode.PARAM:
            return f"    PARAM {self.arg1}"

        if self.opcode == IROpcode.CALL:
            prefix = f"{self.result} = " if self.result else ""
            return f"    {prefix}CALL {self.arg1}, {self.arg2}"

        if self.opcode == IROpcode.RETURN:
            value = "" if self.arg1 is None else self.arg1
            return f"    RETURN {value}"

        if self.opcode == IROpcode.READ:
            return f"    READ {self.result}"

        if self.opcode == IROpcode.WRITE:
            return f"    WRITE {self.arg1}"

        if self.opcode == IROpcode.LOAD_ARRAY:
            return f"    {self.result} = {self.arg1}[{self.arg2}]"

        if self.opcode == IROpcode.STORE_ARRAY:
            return f"    {self.arg1}[{self.arg2}] = {self.result}"

        if self.opcode == IROpcode.ENTER_SCOPE:
            suffix = "" if self.label is None else f" {self.label}"
            return f"    ENTER_SCOPE{suffix}"

        if self.opcode == IROpcode.LEAVE_SCOPE:
            suffix = "" if self.label is None else f" {self.label}"
            return f"    LEAVE_SCOPE{suffix}"

        return f"    {self.opcode.value} {self.result or ''} {self.arg1 or ''} {self.arg2 or ''}".rstrip()


@dataclass
class IRProgram:
    """Programa completo em TAC.

    Guarda a sequência de instruções e uma tabela simples de variáveis.
    Também fornece helpers para criar temporários, labels e instruções.
    """

    name: str
    instructions: List[IRInstruction] = field(default_factory=list)
    variables: Dict[str, dict] = field(default_factory=dict)
    function_params: Dict[str, List[str]] = field(default_factory=dict)
    _temp_count: int = field(default=0, init=False, repr=False, compare=False)
    _label_count: int = field(default=0, init=False, repr=False, compare=False)

    def new_temp(self) -> str:
        """Cria um novo temporário no formato `t1`, `t2`, ..."""
        self._temp_count += 1
        return f"t{self._temp_count}"

    def new_label(self) -> int:
        """Cria um novo identificador numérico de label."""
        self._label_count += 1
        return self._label_count

    def emit(self, instruction: IRInstruction) -> IRInstruction:
        """Adiciona uma instrução já construída ao programa."""
        self.instructions.append(instruction)
        return instruction

    def emit_assign(self, result: str, src: Any) -> IRInstruction:
        """Emite uma atribuição simples: `result = src`."""
        return self.emit(IRInstruction(IROpcode.ASSIGN, result=result, arg1=src))

    def emit_binop(self, op: IROpcode, result: str, arg1: Any, arg2: Any) -> IRInstruction:
        """Emite uma operação binária: `result = arg1 op arg2`."""
        return self.emit(IRInstruction(op, result=result, arg1=arg1, arg2=arg2))

    def emit_unop(self, op: IROpcode, result: str, arg1: Any) -> IRInstruction:
        """Emite uma operação unária: `result = op arg1`."""
        return self.emit(IRInstruction(op, result=result, arg1=arg1))

    def emit_label(self, label: int) -> IRInstruction:
        """Emite uma marca de posição no fluxo de execução."""
        return self.emit(IRInstruction(IROpcode.LABEL, label=label))

    def emit_goto(self, label: int) -> IRInstruction:
        """Emite um salto incondicional para `label`."""
        return self.emit(IRInstruction(IROpcode.GOTO, label=label))

    def emit_if_false(self, cond: Any, label: int) -> IRInstruction:
        """Emite um salto para `label` quando `cond` for falso/zero."""
        return self.emit(IRInstruction(IROpcode.IF_FALSE, arg1=cond, label=label))

    def emit_if_goto(self, cond: Any, label: int) -> IRInstruction:
        """Emite um salto para `label` quando `cond` for verdadeiro."""
        return self.emit(IRInstruction(IROpcode.IF_GOTO, arg1=cond, label=label))

    def emit_param(self, arg: Any) -> IRInstruction:
        """Emite um argumento para uma chamada de função."""
        return self.emit(IRInstruction(IROpcode.PARAM, arg1=arg))

    def emit_call(self, func: str, n_params: int, result: Optional[str] = None) -> IRInstruction:
        """Emite uma chamada de função com `n_params` argumentos."""
        return self.emit(IRInstruction(IROpcode.CALL, result=result, arg1=func, arg2=n_params))

    def emit_return(self, value: Optional[Any] = None) -> IRInstruction:
        """Emite o retorno de uma função, opcionalmente com valor."""
        return self.emit(IRInstruction(IROpcode.RETURN, arg1=value))

    def emit_read(self, result: str) -> IRInstruction:
        """Emite uma leitura da entrada padrão para `result`."""
        return self.emit(IRInstruction(IROpcode.READ, result=result))

    def emit_write(self, value: Any) -> IRInstruction:
        """Emite a escrita de `value` para a saída padrão."""
        return self.emit(IRInstruction(IROpcode.WRITE, arg1=value))

    def emit_array_load(self, result: str, array: str, index: Any) -> IRInstruction:
        """Emite uma leitura de array: `result = array[index]`."""
        return self.emit(IRInstruction(IROpcode.LOAD_ARRAY, result=result, arg1=array, arg2=index))

    def emit_array_store(self, array: str, index: Any, value: Any) -> IRInstruction:
        """Emite uma escrita em array: `array[index] = value`."""
        return self.emit(IRInstruction(IROpcode.STORE_ARRAY, result=value, arg1=array, arg2=index))

    def emit_enter_scope(self, label: Optional[Any] = None) -> IRInstruction:
        """Marca o início de um escopo/função."""
        return self.emit(IRInstruction(IROpcode.ENTER_SCOPE, label=label))

    def emit_leave_scope(self, label: Optional[Any] = None) -> IRInstruction:
        """Marca o fim de um escopo/função."""
        return self.emit(IRInstruction(IROpcode.LEAVE_SCOPE, label=label))

    def dump(self) -> str:
        """Produz uma string com o programa TAC formatado para leitura."""
        lines = [f"=== TAC: {self.name} ==="]
        lines.extend(repr(instr) for instr in self.instructions)
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Mostra o TAC completo quando o programa é impresso."""
        return self.dump()
