"""
Geração de Código da Máquina Virtual
=====================================

Converte a AST em código da máquina virtual.
"""

from src.ast.visitor import ASTVisitor
from .ir import IRProgram, IRInstruction, IROpcode


class CodeGenerator(ASTVisitor):
    """
    Gerador de código para máquina virtual.
    
    Implementa operações que convertem a AST em:
    1. Representação Intermediária (IR)
    2. Código da máquina virtual
    """
    
    def __init__(self):
        self.ir_program = None
        self.var_counter = 0
    
    def generate_code(self, ast):
        """Gera código para o AST fornecido."""
        self.ir_program = IRProgram(name="program")
        ast.accept(self)
        return self.ir_program
    
    def new_temp(self):
        """Cria uma nova variável temporária."""
        self.var_counter += 1
        return f"_t{self.var_counter}"
    
    # Implementar métodos visit_* para gerar código
    def visit_program(self, node):
        pass
    
    def visit_variable_declaration(self, node):
        pass
    
    def visit_assignment(self, node):
        pass
    
    def visit_binary_op(self, node):
        pass
    
    def visit_unary_op(self, node):
        pass
    
    def visit_identifier(self, node):
        pass
    
    def visit_literal(self, node):
        pass
    
    def visit_if_statement(self, node):
        pass
    
    def visit_do_loop(self, node):
        pass
    
    def visit_goto_statement(self, node):
        pass
    
    def visit_read_statement(self, node):
        pass
    
    def visit_print_statement(self, node):
        pass
    
    def visit_function_declaration(self, node):
        pass
