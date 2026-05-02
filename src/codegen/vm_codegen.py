"""
Geração de Código para a Máquina Virtual EWVM.
===============================================

Converte TAC para assembly da EWVM seguindo a documentação da máquina.
A implementação evita uma longa cadeia de `if/elif` usando despacho por
opcode e pequenos handlers por família de instruções.
"""

from __future__ import annotations

from math import prod
from typing import Any, Dict, List, Optional

from src.codegen.ir import IRInstruction, IRProgram, IROpcode


class VMCodeGenerator:
    """Traduz um programa TAC para instruções da EWVM.

    O gerador mantém duas estruturas internas:
    - `vm_code`: instruções do programa
    - `symbol_map`: mapeamento de nomes para endereços estáticos
    """

    def __init__(self):
        self._function_end_label = "ENDFUNCTIONS"
        self._reset()

    def _reset(self):
        """Limpa o estado interno antes de cada geração."""
        self.vm_code: List[str] = []
        self.symbol_map: Dict[str, int] = {}
        self.next_address: int = 0
        self._function_names: set[str] = set()
        self._emitted_function_jump = False

    def generate_vm_code(self, ir_program: IRProgram) -> str:
        """Gera assembly EWVM a partir de um programa TAC."""
        self._reset()
        self._function_names = set(getattr(ir_program, "function_params", {}))
        self._allocate_static_data(ir_program)

        self.vm_code.append("start")

        for instr in ir_program.instructions:
            self._translate_instruction(instr, ir_program)

        if self._emitted_function_jump:
            self.vm_code.append(f"{self._function_end_label}:")

        if not any(line.strip() == "stop" for line in self.vm_code):
            self.vm_code.append("stop")

        return self._format_output()

    def _infer_allocation_size(self, dimensions: Optional[List[Any]]) -> int:
        """Calcula o tamanho a reservar para uma variável ou array."""
        if not dimensions:
            return 1

        def _dimension_bound(value: Any) -> Optional[int]:
            if isinstance(value, int) and not isinstance(value, bool):
                return value
            if hasattr(value, "value") and isinstance(getattr(value, "value"), int):
                return getattr(value, "value")
            return None

        sizes: List[int] = []
        for dimension in dimensions:
            if isinstance(dimension, tuple) and len(dimension) == 2:
                start, end = dimension
                start_value = _dimension_bound(start)
                end_value = _dimension_bound(end)
                if start_value is not None and end_value is not None:
                    sizes.append(max(1, end_value - start_value + 1))
                else:
                    sizes.append(1)
            else:
                bound = _dimension_bound(dimension)
                if bound is not None:
                    sizes.append(max(1, bound))
                else:
                    sizes.append(1)

        return max(1, prod(sizes))

    def _allocate_symbol(self, name: str, size: int = 1):
        """Reserva um bloco estático e associa-o a um nome simbólico."""
        if name in self.symbol_map:
            return

        self.symbol_map[name] = self.next_address
        self.next_address += size

    def _allocate_static_data(self, ir_program: IRProgram):
        """Aloca variáveis globais e temporários."""
        for name, info in ir_program.variables.items():
            dims = info.get("dims") if isinstance(info, dict) else None
            self._allocate_symbol(name, self._infer_allocation_size(dims))

        for instr in ir_program.instructions:
            if isinstance(instr.result, str) and instr.result not in self.symbol_map:
                self._allocate_symbol(instr.result)

    def _emit(self, line: str):
        """Adiciona uma linha de código."""
        self.vm_code.append(line)

    def _emit_comment(self, text: str):
        self._emit(f"// {text}")

    def _is_integer(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    def _is_float(self, value: Any) -> bool:
        return isinstance(value, float)

    def _operand_symbol_type(self, operand: Any, ir_program: IRProgram) -> Optional[str]:
        if isinstance(operand, str) and operand in ir_program.variables:
            info = ir_program.variables[operand]
            if isinstance(info, dict):
                return info.get("type")
        return None

    def _array_lower_bound(self, array_name: str, ir_program: IRProgram) -> int:
        info = ir_program.variables.get(array_name)
        if not isinstance(info, dict):
            return 1

        dims = info.get("dims")
        if not dims:
            return 1

        first_dim = dims[0]
        if isinstance(first_dim, tuple) and len(first_dim) == 2:
            start, _end = first_dim
            if isinstance(start, int):
                return start
            if hasattr(start, "value") and isinstance(getattr(start, "value"), int):
                return getattr(start, "value")
        return 1

    def _push_operand(self, operand: Any, ir_program: IRProgram):
        """Empilha um operando literal ou o valor de uma variável."""
        if isinstance(operand, bool):
            self._emit(f"pushi {1 if operand else 0}")
            return

        if self._is_integer(operand):
            self._emit(f"pushi {operand}")
            return

        if self._is_float(operand):
            self._emit(f"pushf {operand}")
            return

        if isinstance(operand, str):
            if operand in self.symbol_map:
                self._emit(f"pushg {self.symbol_map[operand]}")
                return
            self._emit(f'pushs "{operand}"')
            return

        self._emit(f"pushs {operand}")

    def _store_result(self, name: str):
        """Guarda o topo da pilha numa variável ou temporário."""
        if name not in self.symbol_map:
            self._allocate_symbol(name)
        self._emit(f"storeg {self.symbol_map[name]}")

    def _should_use_float_ops(self, ir_program: IRProgram, arg1: Any, arg2: Any) -> bool:
        """Detecta se uma operação deve usar opcodes de ponto flutuante."""
        if self._is_float(arg1) or self._is_float(arg2):
            return True
        if isinstance(arg1, str) and self._operand_symbol_type(arg1, ir_program) == "REAL":
            return True
        if isinstance(arg2, str) and self._operand_symbol_type(arg2, ir_program) == "REAL":
            return True
        return False

    def _emit_binary_opcode(self, opcode: IROpcode, ir_program: IRProgram, arg1: Any, arg2: Any):
        """Emite uma operação binária com o mnemonic EWVM correcto."""
        self._push_operand(arg1, ir_program)
        self._push_operand(arg2, ir_program)

        use_float = self._should_use_float_ops(ir_program, arg1, arg2)

        if opcode == IROpcode.NE:
            self._emit("equal")
            self._emit("not")
            return

        int_map = {
            IROpcode.ADD: "add",
            IROpcode.SUB: "sub",
            IROpcode.MUL: "mul",
            IROpcode.DIV: "div",
            IROpcode.MOD: "mod",
            IROpcode.POW: "pow",
            IROpcode.LT:  "inf",
            IROpcode.LE:  "infeq",
            IROpcode.GT:  "sup",
            IROpcode.GE:  "supeq",
            IROpcode.EQ:  "equal",
            IROpcode.AND: "and",
            IROpcode.OR:  "or",
        }

        float_map = {
            IROpcode.ADD: "fadd",
            IROpcode.SUB: "fsub",
            IROpcode.MUL: "fmul",
            IROpcode.DIV: "fdiv",
            IROpcode.LT:  "finf",
            IROpcode.LE:  "finfeq",
            IROpcode.GT:  "fsup",
            IROpcode.GE:  "fsupeq",
            IROpcode.EQ:  "equal",
            IROpcode.AND: "and",
            IROpcode.OR:  "or",
        }

        mnemonic = float_map.get(opcode) if use_float else int_map.get(opcode)
        if mnemonic is None:
            self._emit_comment(f"unsupported binary opcode {opcode.value}")
            return

        self._emit(mnemonic)

    def _emit_write(self, operand: Any, ir_program: IRProgram):
        """Emite WRITEI/WRITEF/WRITES conforme o tipo do operando."""
        operand_type = self._operand_symbol_type(operand, ir_program)
        if self._is_float(operand) or operand_type == "REAL":
            self._push_operand(operand, ir_program)
            self._emit("writef")
        elif operand_type in {"CHARACTER", "STRING"}:
            self._push_operand(operand, ir_program)
            self._emit("writes")
        elif isinstance(operand, str) and operand in self.symbol_map:
            self._push_operand(operand, ir_program)
            self._emit("writei")
        elif isinstance(operand, str):
            self._push_operand(operand, ir_program)
            self._emit("writes")
        else:
            self._push_operand(operand, ir_program)
            self._emit("writei")

    def _emit_read(self, result: Optional[str], ir_program: IRProgram):
        """Lê da entrada e converte para o tipo esperado."""
        self._emit("read")
        if result is None:
            return

        result_type = ir_program.variables.get(result, {}).get("type")
        if result_type in {"INTEGER", "LOGICAL"}:
            self._emit("atoi")
        elif result_type == "REAL":
            self._emit("atof")
        self._store_result(result)

    def _emit_array_access(self, opcode: IROpcode, instr: IRInstruction, ir_program: IRProgram):
        """Traduz acesso a arrays com base em PADD + LOAD/STORE."""
        if instr.arg1 not in self.symbol_map:
            raise KeyError(f"Array desconhecido: {instr.arg1}")

        self._emit("pushgp")
        self._emit(f"pushi {self.symbol_map[instr.arg1]}")
        self._emit("padd")
        self._push_operand(instr.arg2, ir_program)
        lower_bound = self._array_lower_bound(instr.arg1, ir_program)
        if lower_bound != 0:
            self._emit(f"pushi {lower_bound}")
            self._emit("sub")
        self._emit("padd")

        if opcode == IROpcode.LOAD_ARRAY:
            self._emit("load 0")
            if instr.result:
                self._store_result(instr.result)
            return

        self._push_operand(instr.result, ir_program)
        self._emit("store 0")

    def _emit_call(self, instr: IRInstruction):
        """Emite chamada de procedimento/função."""
        self._emit(f"pusha {instr.arg1}")
        self._emit("call")
        if instr.arg2:
            self._emit(f"pop {instr.arg2}")
        if instr.result:
            self._push_operand(instr.arg1, None)
            self._store_result(instr.result)

    def _emit_return(self, instr: IRInstruction, ir_program: IRProgram):
        """Emite RETURN com valor opcional."""
        if instr.arg1 is not None:
            self._push_operand(instr.arg1, ir_program)
        self._emit("return")

    def _format_output(self) -> str:
        """Junta todas as linhas num único texto."""
        return "\n".join(self.vm_code)

    def _translate_instruction(self, instr: IRInstruction, ir_program: IRProgram):
        """Traduz uma única instrução TAC para EWVM."""
        match instr.opcode:
            case (IROpcode.ADD | IROpcode.SUB | IROpcode.MUL | IROpcode.DIV |
                  IROpcode.MOD | IROpcode.POW | IROpcode.EQ | IROpcode.NE |
                  IROpcode.LT | IROpcode.LE | IROpcode.GT | IROpcode.GE |
                  IROpcode.AND | IROpcode.OR):
                self._emit_binary_opcode(instr.opcode, ir_program, instr.arg1, instr.arg2)
                if instr.result:
                    self._store_result(instr.result)

            case IROpcode.ASSIGN:
                self._push_operand(instr.arg1, ir_program)
                if instr.result:
                    self._store_result(instr.result)

            case IROpcode.UMINUS:
                self._push_operand(instr.arg1, ir_program)
                self._emit("neg")
                if instr.result:
                    self._store_result(instr.result)

            case IROpcode.NOT:
                self._push_operand(instr.arg1, ir_program)
                self._emit("not")
                if instr.result:
                    self._store_result(instr.result)

            case IROpcode.LOAD_ARRAY:
                self._emit_array_access(IROpcode.LOAD_ARRAY, instr, ir_program)

            case IROpcode.STORE_ARRAY:
                self._emit_array_access(IROpcode.STORE_ARRAY, instr, ir_program)

            case IROpcode.READ:
                self._emit_read(instr.result, ir_program)

            case IROpcode.WRITE:
                self._emit_write(instr.arg1, ir_program)

            case IROpcode.LABEL:
                if (
                    instr.label in self._function_names
                    and not self._emitted_function_jump
                ):
                    self._emit(f"jump {self._function_end_label}")
                    self._emitted_function_jump = True
                self._emit(f"{instr.label}:")

            case IROpcode.GOTO:
                self._emit(f"jump {instr.label}")

            case IROpcode.IF_FALSE | IROpcode.IF_FALSE_GOTO:
                self._push_operand(instr.arg1, ir_program)
                self._emit(f"jz {instr.label}")

            case IROpcode.IF_GOTO:
                self._push_operand(instr.arg1, ir_program)
                self._emit("not")
                self._emit(f"jz {instr.label}")

            case IROpcode.PARAM:
                self._push_operand(instr.arg1, ir_program)

            case IROpcode.CALL:
                self._emit_call(instr)

            case IROpcode.RETURN:
                self._emit_return(instr, ir_program)

            case IROpcode.ENTER_SCOPE:
                params = getattr(ir_program, "function_params", {}).get(instr.label, [])
                for offset, param in enumerate(params, start=1):
                    self._emit("pushfp")
                    self._emit(f"load -{offset}")
                    self._store_result(param)
                self._emit_comment(f"enter scope {instr.arg1 or ''}".rstrip())

            case IROpcode.LEAVE_SCOPE:
                self._emit_comment(f"leave scope {instr.arg1 or ''}".rstrip())

            case _:
                self._emit_comment(f"unsupported opcode {instr.opcode.name}")
