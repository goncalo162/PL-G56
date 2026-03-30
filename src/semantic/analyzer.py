"""
Analisador Semântico
====================

Valida a corretude semântica da AST e constrói a tabela de símbolos.

Verificações:
- Declaração de variáveis antes do uso
- Compatibilidade de tipos
- Validação de labels e CONTINUE
- Escopo de variáveis
"""

from src.exceptions import SemanticError
from src.ast.visitor import ASTVisitor


class SymbolTable:
    """
    Tabela de Símbolos para armazenar variáveis e suas propriedades.
    
    Attributes:
        symbols: Dict[str, SymbolInfo] - informações sobre símbolos
        scopes: List[Dict] - pilha de escopos para suportar subprogramas
    """
    
    def __init__(self):
        self.symbols = {}
        self.scopes = [{}]  # Escopo global
    
    def declare(self, name: str, type_name: str, **attrs):
        """Declara uma nova variável."""
        if name in self.scopes[-1]:
            raise SemanticError(f"Variável '{name}' já declarada")
        self.scopes[-1][name] = {
            'type': type_name,
            **attrs
        }
    
    def lookup(self, name: str):
        """Procura uma variável na tabela."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variável '{name}' não declarada")
    
    def push_scope(self):
        """Cria um novo escopo (para subprogramas)."""
        self.scopes.append({})
    
    def pop_scope(self):
        """Finaliza o escopo atual."""
        self.scopes.pop()


class SemanticAnalyzer(ASTVisitor):
    """
    Analisador semântico que valida a corretude do programa.
    
    Implementa operações sobre a AST usando o padrão Visitor.
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self, ast):
        """Inicia análise semântica."""
        ast.accept(self)
        return len(self.errors) == 0
    
    # Implementar métodos visit_* para validar cada tipo de nó
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
