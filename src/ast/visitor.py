"""
Padrão Visitor para Traversal da AST
====================================

Define a interface para visitar nós da AST.
Implementa o padrão Visitor para desacoplar operações dos nós.
"""

from abc import ABC, abstractmethod


class ASTVisitor(ABC):
    """
    Interface para o padrão Visitor.
    
    Cada método visit_* corresponde a um tipo de nó específico.
    Subclasses implementam operações específicas (análise semântica,
    geração de código, etc).
    """
    
    # Declarações
    @abstractmethod
    def visit_program(self, node):
        pass
    
    @abstractmethod
    def visit_variable_declaration(self, node):
        pass
    
    @abstractmethod
    def visit_function_declaration(self, node):
        pass
    
    # Expressões
    @abstractmethod
    def visit_binary_op(self, node):
        pass
    
    @abstractmethod
    def visit_unary_op(self, node):
        pass
    
    @abstractmethod
    def visit_identifier(self, node):
        pass
    
    @abstractmethod
    def visit_literal(self, node):
        pass
    
    # Instruções
    @abstractmethod
    def visit_assignment(self, node):
        pass
    
    @abstractmethod
    def visit_if_statement(self, node):
        pass
    
    @abstractmethod
    def visit_do_loop(self, node):
        pass
    
    @abstractmethod
    def visit_goto_statement(self, node):
        pass
    
    @abstractmethod
    def visit_read_statement(self, node):
        pass
    
    @abstractmethod
    def visit_print_statement(self, node):
        pass


class PrintVisitor(ASTVisitor):
    """
    Exemplo de Visitor: Imprime a AST em formato legível.
    Útil para visualização e debugging.
    """
    
    def __init__(self, indent=0):
        self.indent = indent
    
    def _print(self, text):
        print("  " * self.indent + text)
    
    def visit_program(self, node):
        self._print(f"PROGRAM {node.name}")
        for decl in node.declarations:
            decl.accept(self)
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_variable_declaration(self, node):
        self._print(f"VAR {node.type_name} {node.name}")
    
    def visit_binary_op(self, node):
        self._print(f"BINOP {node.operator}")
        self.indent += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent -= 1
    
    def visit_literal(self, node):
        self._print(f"LIT {node.type_name}({node.value})")
    
    def visit_identifier(self, node):
        self._print(f"ID {node.name}")
    
    def visit_assignment(self, node):
        self._print(f"ASSIGN")
        self.indent += 1
        self._print(f"to {node.target.name}")
        node.value.accept(self)
        self.indent -= 1
    
    def visit_if_statement(self, node):
        self._print(f"IF")
        self.indent += 1
        node.condition.accept(self)
        self.indent -= 1
    
    def visit_do_loop(self, node):
        self._print(f"DO {node.variable.name}")
    
    def visit_goto_statement(self, node):
        self._print(f"GOTO {node.label}")
    
    def visit_read_statement(self, node):
        self._print(f"READ")
    
    def visit_print_statement(self, node):
        self._print(f"PRINT")
    
    def visit_function_declaration(self, node):
        self._print(f"FUNCTION {node.name}")
    
    def visit_unary_op(self, node):
        self._print(f"UNOP {node.operator}")
