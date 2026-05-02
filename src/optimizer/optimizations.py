"""
Passes de Otimização
====================

Implementações específicas de passes de otimização.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.codegen.ir import IRInstruction, IROpcode


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
        return [instr.arg1, instr.arg2, instr.result]
    if instr.opcode == IROpcode.CALL:
        return [instr.arg1]
    if instr.opcode in {IROpcode.IF_FALSE, IROpcode.IF_FALSE_GOTO, IROpcode.IF_GOTO,
                        IROpcode.WRITE, IROpcode.PARAM, IROpcode.RETURN,
                        IROpcode.UMINUS, IROpcode.NOT, IROpcode.ASSIGN}:
        return [instr.arg1]
    if instr.opcode == IROpcode.LOAD_ARRAY:
        return [instr.arg1, instr.arg2]
    return [instr.arg1, instr.arg2]


def _is_temp_name(name: Any) -> bool:
    """Deteta temporários gerados pelo IR (`_t1`, `_t2`, ...)."""
    return isinstance(name, str) and name.startswith("_t") and name[2:].isdigit()


class DeadCodeElimination:
    """Remove código que nunca é executado ou cujo resultado é descartado."""

    @staticmethod
    def apply(instructions):
        """Aplica eliminação de código morto por análise de liveness.

        A análise percorre as instruções de trás para a frente. Instruções sem
        efeito colateral cujo resultado não é usado são removidas.
        """
        referenced_labels = {
            instr.label
            for instr in instructions
            if instr.opcode in {IROpcode.GOTO, IROpcode.IF_FALSE, IROpcode.IF_GOTO, IROpcode.IF_FALSE_GOTO}
            and instr.label is not None
        }
        referenced_labels.update(
            instr.arg1
            for instr in instructions
            if instr.opcode == IROpcode.CALL and instr.arg1 is not None
        )

        side_effecting = {
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

            if instr.opcode == IROpcode.LABEL:
                if instr.label in referenced_labels:
                    kept_reversed.append(instr)
                continue

            must_keep = (
                instr.opcode in side_effecting
                or (defines is not None and not _is_temp_name(defines))
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
                        else:
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


class AlgebraicSimplification:
    """Aplica identidades algébricas locais sem alterar efeitos observáveis."""

    @staticmethod
    def apply(instructions):
        out: List[IRInstruction] = []

        for instr in instructions:
            if instr.result is None:
                out.append(instr)
                continue

            left = _to_number(instr.arg1)
            right = _to_number(instr.arg2)

            replacement = None
            if instr.opcode == IROpcode.ADD:
                if right == 0:
                    replacement = instr.arg1
                elif left == 0:
                    replacement = instr.arg2
            elif instr.opcode == IROpcode.SUB:
                if right == 0:
                    replacement = instr.arg1
            elif instr.opcode == IROpcode.MUL:
                if right == 1:
                    replacement = instr.arg1
                elif left == 1:
                    replacement = instr.arg2
                elif right == 0 or left == 0:
                    replacement = 0
            elif instr.opcode == IROpcode.DIV:
                if right == 1:
                    replacement = instr.arg1
            elif instr.opcode == IROpcode.AND:
                if right == 1:
                    replacement = instr.arg1
                elif left == 1:
                    replacement = instr.arg2
                elif right == 0 or left == 0:
                    replacement = 0
            elif instr.opcode == IROpcode.OR:
                if right == 0:
                    replacement = instr.arg1
                elif left == 0:
                    replacement = instr.arg2
                elif right == 1 or left == 1:
                    replacement = 1

            if replacement is not None:
                out.append(IRInstruction(IROpcode.ASSIGN, result=instr.result, arg1=replacement))
            else:
                out.append(instr)

        return out


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
            if instr.opcode == IROpcode.LABEL:
                constants.clear()

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
                expr_to_result.clear()

            out.append(instr)

        return out


class LocalTempForwarding:
    """Elimina temporários usados apenas na atribuição imediatamente seguinte."""

    @staticmethod
    def apply(instructions):
        out: List[IRInstruction] = []
        index = 0

        while index < len(instructions):
            instr = instructions[index]
            next_instr = instructions[index + 1] if index + 1 < len(instructions) else None

            if (
                next_instr is not None
                and _is_temp_name(instr.result)
                and next_instr.opcode == IROpcode.ASSIGN
                and next_instr.arg1 == instr.result
                and isinstance(next_instr.result, str)
            ):
                forwarded = IRInstruction(
                    opcode=instr.opcode,
                    result=next_instr.result,
                    arg1=instr.arg1,
                    arg2=instr.arg2,
                    label=instr.label,
                )
                out.append(forwarded)
                index += 2
                continue

            out.append(instr)
            index += 1

        return out


class ControlFlowSimplification:
    """Simplifica saltos e código inalcançável em sequências lineares de IR."""

    @staticmethod
    def apply(instructions):
        simplified = ControlFlowSimplification._simplify_constant_branches(instructions)
        simplified = ControlFlowSimplification._remove_redundant_gotos(simplified)
        return ControlFlowSimplification._remove_unreachable_after_jump(simplified)

    @staticmethod
    def _simplify_constant_branches(instructions):
        out: List[IRInstruction] = []
        for instr in instructions:
            if instr.opcode in {IROpcode.IF_FALSE, IROpcode.IF_FALSE_GOTO, IROpcode.IF_GOTO}:
                value = _to_number(instr.arg1)
                if value is not None:
                    should_jump = (
                        value == 0
                        if instr.opcode in {IROpcode.IF_FALSE, IROpcode.IF_FALSE_GOTO}
                        else value != 0
                    )
                    if should_jump:
                        out.append(IRInstruction(IROpcode.GOTO, label=instr.label))
                    continue
            out.append(instr)
        return out

    @staticmethod
    def _remove_redundant_gotos(instructions):
        out: List[IRInstruction] = []
        for index, instr in enumerate(instructions):
            next_instr = instructions[index + 1] if index + 1 < len(instructions) else None
            if (
                instr.opcode == IROpcode.GOTO
                and next_instr is not None
                and next_instr.opcode == IROpcode.LABEL
                and instr.label == next_instr.label
            ):
                continue
            out.append(instr)
        return out

    @staticmethod
    def _remove_unreachable_after_jump(instructions):
        out: List[IRInstruction] = []
        unreachable = False

        for instr in instructions:
            if unreachable and instr.opcode != IROpcode.LABEL:
                continue

            unreachable = False
            out.append(instr)

            if instr.opcode in {IROpcode.GOTO, IROpcode.RETURN}:
                unreachable = True

        return out
