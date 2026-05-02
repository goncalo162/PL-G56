"""
Geração de Código Intermediário (TAC)
=======================================

Converte a AST em Código de Três Endereços (Three-Address Code).
"""

from src.ast.visitor import ASTVisitor
from src.ast import nodes
from .ir import IRProgram, IROpcode

class CodeGenerator(ASTVisitor):
    """
    Gerador de Código de Três Endereços (TAC).
    
    Percorre a AST e gera uma sequência de instruções lineares de baixo nível.
    Mantém também uma pequena pilha de ciclos para traduzir `CONTINUE`.
    """
    
    def __init__(self):
        self.ir_program = None
        self.temp_counter = 0
        self.label_counter = 0
        self.loop_stack = []
    
    def generate_code(self, ast: nodes.Program):
        """Gera o IR para o AST fornecido.

        Cada chamada reinicia o estado interno do gerador.
        """
        self.ir_program = IRProgram(name=ast.name)
        self.temp_counter = 0
        self.label_counter = 0
        self.loop_stack = []
        ast.accept(self)
        return self.ir_program
    
    def new_temp(self):
        """Cria uma nova variável temporária para resultados intermédios."""
        self.temp_counter += 1
        return f"_t{self.temp_counter}"
    
    def new_label(self, prefix="L"):
        """Cria um novo label string único para a EWVM."""
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def _emit_statement_with_optional_label(self, stmt):
        """Emite label explícito para statements rotulados antes do conteúdo."""
        label = getattr(stmt, 'statement_label', None)
        if label is not None:
            self.ir_program.emit_label(label)
        stmt.accept(self)

    def visit_program(self, node: nodes.Program):
        # O bloco principal é tratado como um escopo próprio.
        self.ir_program.emit_enter_scope("main")
        for decl in node.declarations:
            decl.accept(self)
        for stmt in node.statements:
            self._emit_statement_with_optional_label(stmt)
        for subprogram in node.subprograms:
            subprogram.accept(self)
        self.ir_program.emit_leave_scope("main")

    def visit_variable_declaration(self, node: nodes.VariableDeclaration):
        # A declaração é gerida pela tabela de símbolos na análise semântica.
        # Aqui apenas registamos metadados e, se existir, a inicialização.
        self.ir_program.variables[node.name] = {'type': node.type_name, 'dims': node.dimensions}
        if node.initial_value:
            val = node.initial_value.accept(self)
            self.ir_program.emit_assign(node.name, val)

    def visit_assignment(self, node: nodes.Assignment):
        # Primeiro avaliamos o lado direito para obter um valor já materializado.
        value_reg = node.value.accept(self)
        
        if isinstance(node.target, nodes.ArrayAccess):
            # A implementação actual trata apenas arrays 1D.
            index_reg = node.target.indices[0].accept(self)
            self.ir_program.emit_array_store(node.target.name, index_reg, value_reg)
        else:
            self.ir_program.emit_assign(node.target.name, value_reg)

    def visit_binary_op(self, node: nodes.BinaryOp):
        # Calculamos os operandos antes de emitir a operação binária.
        left_reg = node.left.accept(self)
        right_reg = node.right.accept(self)
        
        temp_reg = self.new_temp()
        
        op_map = {
            '+': IROpcode.ADD, '-': IROpcode.SUB, '*': IROpcode.MUL, '/': IROpcode.DIV,
            '**': IROpcode.POW, '.EQ.': IROpcode.EQ, '.NE.': IROpcode.NE,
            '.LT.': IROpcode.LT, '.LE.': IROpcode.LE, '.GT.': IROpcode.GT,
            '.GE.': IROpcode.GE, '.AND.': IROpcode.AND, '.OR.': IROpcode.OR
        }
        
        ir_opcode = op_map.get(node.operator.upper())
        if not ir_opcode:
            raise ValueError(f"Operador binário desconhecido: {node.operator}")
            
        self.ir_program.emit_binop(ir_opcode, temp_reg, left_reg, right_reg)
        return temp_reg

    def visit_unary_op(self, node: nodes.UnaryOp):
        # Operações unárias seguem o mesmo padrão: avaliar e depois emitir.
        operand_reg = node.operand.accept(self)
        temp_reg = self.new_temp()
        
        op_map = {'-': IROpcode.UMINUS, '.NOT.': IROpcode.NOT}
        ir_opcode = op_map.get(node.operator.upper())
        if not ir_opcode:
            raise ValueError(f"Operador unário desconhecido: {node.operator}")

        self.ir_program.emit_unop(ir_opcode, temp_reg, operand_reg)
        return temp_reg

    def visit_identifier(self, node: nodes.Identifier):
        return node.name

    def visit_literal(self, node: nodes.Literal):
        return node.value

    def visit_if_statement(self, node: nodes.IfStatement):
        else_label = self.new_label("IFELSE")
        end_label = self.new_label("IFEND")

        # Se a condição for falsa, saltamos diretamente para o ELSE.
        cond_reg = node.condition.accept(self)
        self.ir_program.emit_if_false(cond_reg, else_label)
        for stmt in node.then_body:
            self._emit_statement_with_optional_label(stmt)
        self.ir_program.emit_goto(end_label)

        # O bloco ELSE é opcional.
        self.ir_program.emit_label(else_label)
        if node.else_body:
            for stmt in node.else_body:
                self._emit_statement_with_optional_label(stmt)
        
        # Marca o ponto de saída comum do IF.
        self.ir_program.emit_label(end_label)



    def visit_do_loop(self, node: nodes.DoLoop):
        start_label    = self.new_label("DOSTART")
        continue_label = self.new_label("DOCONT")
        end_label      = self.new_label("DOEND")

        # Inicialização: variavel = start
        start_val = node.start.accept(self)
        self.ir_program.emit_assign(node.variable.name, start_val)

        self.ir_program.emit_label(start_label)
        end_val  = node.end.accept(self)
        perm_reg = self.new_temp()
        self.ir_program.emit_binop(IROpcode.LE, perm_reg, node.variable.name, end_val)
        self.ir_program.emit_if_false(perm_reg, end_label)  # jz end_label se variavel > fim

        # Corpo
        self.loop_stack.append(continue_label)
        for stmt in node.body:
            self._emit_statement_with_optional_label(stmt)
        self.loop_stack.pop()

        # Label do passo para `CONTINUE`; o DCE remove-a quando não for usada.
        self.ir_program.emit_label(continue_label)

        # Incremento
        step_val  = node.step.accept(self) if node.step else 1
        step_temp = self.new_temp()
        self.ir_program.emit_binop(IROpcode.ADD, step_temp, node.variable.name, step_val)
        self.ir_program.emit_assign(node.variable.name, step_temp)

        self.ir_program.emit_goto(start_label)
        self.ir_program.emit_label(end_label)

    def visit_print_statement(self, node: nodes.PrintStatement):
        for expr in node.expressions:
            val = expr.accept(self)
            self.ir_program.emit_write(val)

    def visit_read_statement(self, node: nodes.ReadStatement):
        for var in node.variables:
            if isinstance(var, nodes.ArrayAccess):
                # READ numa posição de array precisa ler para um temporário
                # e depois armazenar no elemento correspondente.
                temp_reg = self.new_temp()
                element_type = self.ir_program.variables.get(var.name, {}).get("type", "UNKNOWN")
                self.ir_program.variables[temp_reg] = {"type": element_type}

                self.ir_program.emit_read(temp_reg)
                index_reg = var.indices[0].accept(self)
                self.ir_program.emit_array_store(var.name, index_reg, temp_reg)
            else:
                self.ir_program.emit_read(var.name)

    def visit_function_declaration(self, node: nodes.FunctionDeclaration):
        # Funções e subrotinas partilham a mesma estrutura de geração no TAC.
        self.ir_program.function_params[node.name] = [param.name for param in (node.parameters or [])]
        self.ir_program.variables.setdefault(node.name, {'type': node.return_type, 'dims': None})
        for param in node.parameters or []:
            self.ir_program.variables.setdefault(param.name, {'type': param.type_name, 'dims': param.dimensions})

        self.ir_program.emit_label(node.name)
        self.ir_program.emit_enter_scope(node.name)
        # Os parâmetros são resolvidos no CALL; aqui emitimos apenas o corpo.
        for stmt in node.body:
            self._emit_statement_with_optional_label(stmt)
        self.ir_program.emit_leave_scope(node.name)
        # O RETURN é gerado por nós próprios no corpo da função.

    def visit_subroutine_declaration(self, node):
        # A AST actual normaliza subrotinas para FunctionDeclaration,
        # mas este método fica para compatibilidade com visitantes antigos.
        return self.visit_function_declaration(node)
        
    def visit_return_statement(self, node: nodes.ReturnStatement):
        val = node.value.accept(self) if hasattr(node, 'value') and node.value else None
        self.ir_program.emit_return(val)

    def visit_function_call(self, node: nodes.FunctionCall):
        # O parser pode representar argumentos como lista ou nó único.
        args = node.arguments if isinstance(node.arguments, list) else [node.arguments]

        if node.function_name == "MOD" and len(args) == 2:
            left = args[0].accept(self)
            right = args[1].accept(self)
            temp_reg = self.new_temp()
            self.ir_program.emit_binop(IROpcode.MOD, temp_reg, left, right)
            return temp_reg

        # Os argumentos são empilhados na ordem inversa para preservar a ordem.
        for arg in reversed(args):
            arg_val = arg.accept(self)
            self.ir_program.emit_param(arg_val)
        
        temp_reg = self.new_temp()
        self.ir_program.emit_call(node.function_name, len(args), temp_reg)
        return temp_reg

    def visit_call_statement(self, node: nodes.CallStatement):
        # O parser pode representar argumentos como lista ou nó único.
        args = node.arguments if isinstance(node.arguments, list) else [node.arguments]
        # Chamada de subrotina: os efeitos laterais interessam, não o retorno.
        for arg in reversed(args):
            arg_val = arg.accept(self)
            self.ir_program.emit_param(arg_val)

        self.ir_program.emit_call(node.subroutine, len(args))

    def visit_array_access(self, node: nodes.ArrayAccess):
        # A versão actual ainda trata acessos unidimensionais.
        index_reg = node.indices[0].accept(self)
        temp_reg = self.new_temp()
        self.ir_program.emit_array_load(temp_reg, node.name, index_reg)
        return temp_reg
        
    def visit_goto_statement(self, node: nodes.GotoStatement):
        self.ir_program.emit_goto(node.label)

    def visit_continue_statement(self, node):
        # CONTINUE só faz sentido dentro de um DO; saltamos para o passo.
        if not self.loop_stack:
            raise ValueError("CONTINUE fora de um ciclo DO")
        self.ir_program.emit_goto(self.loop_stack[-1])
