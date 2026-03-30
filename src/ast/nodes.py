"""
Nós da Árvore Sintática Abstrata (AST)
=======================================

Define as classes para representar a estrutura de um programa Fortran.

Cada nó representa uma construção sintática do programa.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass, field


class ASTNode(ABC):
    """
    Classe base para todos os nós da AST.
    
    Todos os nós da árvore sintática devem herdar desta classe.
    """
    
    @abstractmethod
    def accept(self, visitor):
        """Implementa o padrão Visitor para traversal da AST."""
        pass


# === Nós de Declaração ===

@dataclass
class Program(ASTNode):
    """Representa um programa Fortran."""
    name: str
    declarations: List[ASTNode] = field(default_factory=list)
    statements: List[ASTNode] = field(default_factory=list)
    subprograms: List[ASTNode] = field(default_factory=list)
    
    def accept(self, visitor):
        return visitor.visit_program(self)


@dataclass
class VariableDeclaration(ASTNode):
    """Representa uma declaração de variável."""
    name: str
    type_name: str  # INTEGER, REAL, LOGICAL, CHARACTER
    dimensions: Optional[List[tuple]] = None  # Para arrays
    initial_value: Optional[ASTNode] = None
    
    def accept(self, visitor):
        return visitor.visit_variable_declaration(self)


@dataclass
class FunctionDeclaration(ASTNode):
    """Representa uma declaração de função."""
    name: str
    return_type: str
    parameters: List['VariableDeclaration'] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    
    def accept(self, visitor):
        return visitor.visit_function_declaration(self)


# === Nós de Expressão ===

@dataclass
class BinaryOp(ASTNode):
    """Representa uma operação binária."""
    left: ASTNode
    operator: str
    right: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)


@dataclass
class UnaryOp(ASTNode):
    """Representa uma operação unária."""
    operator: str
    operand: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)


@dataclass
class Identifier(ASTNode):
    """Representa um identificador/variável."""
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)


@dataclass
class Literal(ASTNode):
    """Representa um literal (número, string, etc)."""
    value: Any
    type_name: str  # INTEGER, REAL, STRING, LOGICAL
    
    def accept(self, visitor):
        return visitor.visit_literal(self)


# === Nós de Instrução ===

@dataclass
class Assignment(ASTNode):
    """Representa uma atribuição."""
    target: Identifier
    value: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)


@dataclass
class IfStatement(ASTNode):
    """Representa uma instrução IF-THEN-ELSE."""
    condition: ASTNode
    then_body: List[ASTNode]
    elif_parts: List[tuple] = field(default_factory=list)  # (condition, body)
    else_body: Optional[List[ASTNode]] = None
    
    def accept(self, visitor):
        return visitor.visit_if_statement(self)


@dataclass
class DoLoop(ASTNode):
    """Representa um ciclo DO."""
    variable: Identifier
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode] = None
    label: Optional[int] = None
    body: List[ASTNode] = field(default_factory=list)
    
    def accept(self, visitor):
        return visitor.visit_do_loop(self)


@dataclass
class GotoStatement(ASTNode):
    """Representa um GOTO."""
    label: int
    
    def accept(self, visitor):
        return visitor.visit_goto_statement(self)


@dataclass
class ReadStatement(ASTNode):
    """Representa um READ."""
    unit: Optional[ASTNode]
    variables: List[Identifier]
    
    def accept(self, visitor):
        return visitor.visit_read_statement(self)


@dataclass
class PrintStatement(ASTNode):
    """Representa um PRINT."""
    expressions: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_print_statement(self)
