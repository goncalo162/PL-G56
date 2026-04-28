"""
Passes de Otimização
====================

Implementações específicas de passes de otimização.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.codegen.ir import IRInstruction, IROpcode

#TODO: rever isto tudo, está tudo mal, o codigo gerado sem otimizaçoes funciona mas com não funciona


def _to_number(value: Any) -> Optional[float | int]:
    """Converte literais numéricos para tipos Python.

    Aceita inteiros, floats e strings com números. Devolve `None` quando o
    valor não pode ser interpretado como número.
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    try:
        if any(ch in text for ch in ".eE"):
            return float(text)
        return int(text)
    except ValueError:
        return None


def _instruction_uses(instr: IRInstruction) -> List[Any]:
    """Extrai operandos usados por uma instrução (para análise de liveness)."""
    if instr.opcode == IROpcode.STORE_ARRAY:
        # array[index] = value  -> usa array, index e value (guardado em result)
        return [instr.arg1, instr.arg2, instr.result]
    if instr.opcode in {IROpcode.IF_FALSE, IROpcode.IF_FALSE_GOTO, IROpcode.IF_GOTO,
                        IROpcode.WRITE, IROpcode.PARAM, IROpcode.RETURN,
                        IROpcode.UMINUS, IROpcode.NOT, IROpcode.ASSIGN}:
        return [instr.arg1]
    if instr.opcode == IROpcode.LOAD_ARRAY:
        return [instr.arg1, instr.arg2]
    return [instr.arg1, instr.arg2]


class DeadCodeElimination:
    """Remove código que nunca é executado ou cujo resultado é descartado."""
    
    @staticmethod
    def apply(instructions):
        """Aplica eliminação de código morto por análise de liveness.

        A análise percorre as instruções de trás para a frente. Instruções sem
        efeito colateral cujo resultado não é usado são removidas.
        """
        side_effecting = {
            IROpcode.LABEL,
            IROpcode.GOTO,
            IROpcode.IF_FALSE,
            IROpcode.IF_GOTO,
            IROpcode.IF_FALSE_GOTO,
            IROpcode.READ,
            IROpcode.WRITE,
            IROpcode.PARAM,
            IROpcode.CALL,
            IROpcode.RETURN,
            IROpcode.STORE_ARRAY,
            IROpcode.ENTER_SCOPE,
            IROpcode.LEAVE_SCOPE,
        }

        live = set()
        kept_reversed: List[IRInstruction] = []

        for instr in reversed(instructions):
            uses = [u for u in _instruction_uses(instr) if isinstance(u, str)]
            defines = instr.result if isinstance(instr.result, str) else None

            must_keep = (
                instr.opcode in side_effecting
                or defines is None
                or defines in live
            )

            if must_keep:
                kept_reversed.append(instr)
                if defines is not None:
                    live.discard(defines)
                live.update(uses)

        return list(reversed(kept_reversed))


class ConstantFolding:
    """Avalia expressões com constantes em tempo de compilação."""
    
    @staticmethod
    def apply(instructions):
        """Aplica constant folding em operações puramente literais."""
        new_instructions = []
        binary_ops = {
            IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV,
            IROpcode.MOD, IROpcode.POW, IROpcode.LT, IROpcode.LE,
            IROpcode.GT, IROpcode.GE, IROpcode.EQ, IROpcode.NE,
            IROpcode.AND, IROpcode.OR,
        }
        unary_ops = {IROpcode.UMINUS, IROpcode.NOT}
        
        for instr in instructions:
            if instr.result is None:
                new_instructions.append(instr)
                continue

            if instr.opcode in binary_ops:
                left = _to_number(instr.arg1)
                right = _to_number(instr.arg2)
                if left is not None and right is not None:
                    try:
                        if instr.opcode == IROpcode.ADD:
                            folded = left + right
                        elif instr.opcode == IROpcode.SUB:
                            folded = left - right
                        elif instr.opcode == IROpcode.MUL:
                            folded = left * right
                        elif instr.opcode == IROpcode.DIV:
                            if right == 0:
                                raise ZeroDivisionError()
                            folded = left / right
                        elif instr.opcode == IROpcode.MOD:
                            if right == 0:
                                raise ZeroDivisionError()
                            folded = left % right
                        elif instr.opcode == IROpcode.POW:
                            folded = left ** right
                        elif instr.opcode == IROpcode.LT:
                            folded = int(left < right)
                        elif instr.opcode == IROpcode.LE:
                            folded = int(left <= right)
                        elif instr.opcode == IROpcode.GT:
                            folded = int(left > right)
                        elif instr.opcode == IROpcode.GE:
                            folded = int(left >= right)
                        elif instr.opcode == IROpcode.EQ:
                            folded = int(left == right)
                        elif instr.opcode == IROpcode.NE:
                            folded = int(left != right)
                        elif instr.opcode == IROpcode.AND:
                            folded = int(bool(left) and bool(right))
                        else:  # IROpcode.OR
                            folded = int(bool(left) or bool(right))

                        new_instructions.append(
                            IRInstruction(opcode=IROpcode.ASSIGN, result=instr.result, arg1=folded)
                        )
                        continue
                    except (ZeroDivisionError, OverflowError):
                        pass

            if instr.opcode in unary_ops:
                operand = _to_number(instr.arg1)
                if operand is not None:
                    if instr.opcode == IROpcode.UMINUS:
                        folded = -operand
                    else:
                        folded = int(not bool(operand))
                    new_instructions.append(
                        IRInstruction(opcode=IROpcode.ASSIGN, result=instr.result, arg1=folded)
                    )
                    continue

            new_instructions.append(instr)
        
        return new_instructions


class ConstantPropagation:
    """Propaga constantes simples ao longo da lista de instruções."""

    @staticmethod
    def apply(instructions):
        constants: Dict[str, Any] = {}
        out: List[IRInstruction] = []

        def replace(value: Any) -> Any:
            if isinstance(value, str) and value in constants:
                return constants[value]
            return value

        for instr in instructions:
            # LABEL = possível alvo de salto para trás (loop).
            # Qualquer constante propagada pode estar desatualizada a partir daqui.
            if instr.opcode == IROpcode.LABEL:
                constants.clear()  # <- ESTA É A CORREÇÃO

            updated = IRInstruction(
                opcode=instr.opcode,
                result=instr.result,
                arg1=replace(instr.arg1),
                arg2=replace(instr.arg2),
                label=instr.label,
            )

            if instr.opcode == IROpcode.STORE_ARRAY:
                updated.result = replace(instr.result)

            if updated.opcode == IROpcode.ASSIGN and isinstance(updated.result, str):
                literal = _to_number(updated.arg1)
                if literal is not None:
                    constants[updated.result] = literal
                else:
                    constants.pop(updated.result, None)
            elif isinstance(updated.result, str):
                constants.pop(updated.result, None)

            out.append(updated)

        return out

class LoopUnrolling:
    """Desdobra loops pequenos para melhorar performance."""
    
    @staticmethod
    def apply(instructions):
        """Aplica loop unrolling (placeholder seguro).

        O IR actual não preserva metadados suficientes para unrolling seguro
        sem análise de CFG. Mantemos a transformação como no-op explícito.
        """
        return list(instructions)


class CommonSubexpressionElimination:
    """Remove computações de sub-expressões comuns."""
    
    @staticmethod
    def apply(instructions):
        """Aplica CSE local e conservadora.

        Reutiliza resultados de expressões puras idênticas enquanto nenhum dos
        operandos é redefinido.
        """
        pure_binary = {
            IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV, IROpcode.MOD,
            IROpcode.POW, IROpcode.LT, IROpcode.LE, IROpcode.GT, IROpcode.GE,
            IROpcode.EQ, IROpcode.NE, IROpcode.AND, IROpcode.OR,
        }

        expr_to_result: Dict[Tuple[IROpcode, Any, Any], str] = {}
        out: List[IRInstruction] = []

        def invalidate(var_name: str):
            keys_to_remove = []
            for key, result_name in expr_to_result.items():
                _, a1, a2 = key
                if a1 == var_name or a2 == var_name or result_name == var_name:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                expr_to_result.pop(key, None)

        for instr in instructions:
            if isinstance(instr.result, str):
                invalidate(instr.result)

            if instr.opcode in pure_binary and isinstance(instr.result, str):
                key = (instr.opcode, instr.arg1, instr.arg2)
                previous = expr_to_result.get(key)
                if previous is not None:
                    out.append(
                        IRInstruction(
                            opcode=IROpcode.ASSIGN,
                            result=instr.result,
                            arg1=previous,
                            label=instr.label,
                        )
                    )
                else:
                    expr_to_result[key] = instr.result
                    out.append(instr)
                continue

            if instr.opcode in {
                IROpcode.GOTO,
                IROpcode.IF_FALSE,
                IROpcode.IF_GOTO,
                IROpcode.IF_FALSE_GOTO,
                IROpcode.LABEL,
                IROpcode.CALL,
                IROpcode.READ,
                IROpcode.STORE_ARRAY,
            }:
                # Conservadoramente, fronteiras de controlo limpam o estado de CSE.
                expr_to_result.clear()

            out.append(instr)

        return out
