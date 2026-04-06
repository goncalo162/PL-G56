"""
Analisador Semântico (Semantic Analyzer)
=========================================

Valida a corretude semântica da AST após o parsing.

Responsabilidades:
- Construir tabela de símbolos (declarações de variáveis e funções)
- Verificar se variáveis são usadas após declaração
- Validar compatibilidade de tipos em expressões e atribuições
- Validar labels e estruturas de controlo (DO loops, GOTO)
- Rastrear escopos (global vs subprogramas)

Padrão de Implementação:
- Usa o padrão Visitor para percorrer a AST
- Cada método visit_* corresponde a um tipo de nó AST
- Retorna tipo do nó (para propagação em expressões)
- Recolhe erros em lista self.errors
"""

from typing import Optional, Dict, List
from src.exceptions import SemanticError
from src.ast.visitor import ASTVisitor
from src.semantic.symbol_table import SymbolTable
from src.semantic.type_checker import TypeChecker


class SemanticAnalyzer(ASTVisitor):
    """
    Analisador semântico que valida a corretude do programa Fortran 77.
    
    Atributos:
        symbol_table: SymbolTable
            Tabela de símbolos com gestão de escopos (usa symbol_table.py)
            
        type_checker: TypeChecker
            Verificador de compatibilidade de tipos (usa type_checker.py)
            
        errors: List[str]
            Lista de erros semânticos encontrados
            
        type_stack: Dict[object, str]
            Pilha auxiliar para rastrear tipos de expressões
            Mapeia cada nó AST para seu tipo (INTEGER, REAL, etc)
            
        labels_defined: Dict[int, str]
            Mapeia cada label numérico para seu contexto
            
        active_loops: List[int]
            Pilha de IDs de loops ativos (para validar CONTINUE/EXIT)
    """
    
    def __init__(self):
        """Inicializa o analisador semântico."""
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()
        self.errors: List[str] = []
        self.type_stack: Dict[object, str] = {}
        self.labels_defined: Dict[int, str] = {}
        self.active_loops: List[int] = []
        self._node_counter = 0
    
    def analyze(self, ast) -> bool:
        """
        Inicia análise semântica da AST.
        
        Args:
            ast: Nó raiz da AST (Program)
            
        Returns:
            True se análise é bem-sucedida (sem erros)
            False se há erros semânticos
        """
        try:
            ast.accept(self)
        except SemanticError as e:
            self.errors.append(str(e))
            return False
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Retorna lista de erros encontrados."""
        return self.errors.copy()
    
    def _add_error(self, message: str):
        """Adiciona erro à lista."""
        self.errors.append(message)
    
    def _get_type(self, node: object) -> Optional[str]:
        """Retorna tipo anotado de um nó."""
        return self.type_stack.get(id(node))
    
    def _set_type(self, node: object, type_name: str):
        """Anota tipo de um nó."""
        self.type_stack[id(node)] = type_name
    
    # ====================================================================
    # Estrutura de Programa
    # ====================================================================
    
    def visit_program(self, node):
        """Processa programa e seus componentes."""
        if node.declarations:
            for decl in node.declarations:
                decl.accept(self)
        
        if node.statements:
            for stmt in node.statements:
                stmt.accept(self)
        
        if node.subprograms:
            for subprog in node.subprograms:
                subprog.accept(self)
    
    # ====================================================================
    # Declarações
    # ====================================================================
    
    def visit_variable_declaration(self, node):
        """Registar variável na tabela de símbolos."""
        valid_types = ["INTEGER", "REAL", "LOGICAL", "CHARACTER", "COMPLEX"]
        if node.type_name not in valid_types:
            self._add_error(f"Tipo desconhecido '{node.type_name}'")
            return
        
        try:
            self.symbol_table.declare(
                node.name,
                node.type_name,
                dimensions=getattr(node, 'dimensions', None),
                initial_value=getattr(node, 'initial_value', None)
            )
        except SemanticError as e:
            self._add_error(str(e))
    
    # ====================================================================
    # Expressões
    # ====================================================================
    
    def visit_identifier(self, node):
        """Valida uso de identificador (variável)."""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self._add_error(f"Variável '{node.name}' não declarada")
            self._set_type(node, "UNKNOWN")
        else:
            self._set_type(node, symbol.type_name)
    
    def visit_literal(self, node):
        """Determina tipo de literal."""
        if isinstance(node.value, bool):
            type_name = "LOGICAL"
        elif isinstance(node.value, int):
            type_name = "INTEGER"
        elif isinstance(node.value, float):
            type_name = "REAL"
        elif isinstance(node.value, str):
            type_name = "CHARACTER"
        else:
            type_name = "UNKNOWN"
        
        self._set_type(node, type_name)
    
    def visit_binary_op(self, node):
        """Valida operação binária."""
        node.left.accept(self)
        node.right.accept(self)
        
        left_type = self._get_type(node.left)
        right_type = self._get_type(node.right)
        
        if not left_type or not right_type:
            self._set_type(node, "UNKNOWN")
            return
        
        try:
            result_type = self.type_checker.get_result_type(
                left_type, right_type, node.operator
            )
            self._set_type(node, result_type)
        except SemanticError as e:
            self._add_error(str(e))
            self._set_type(node, "UNKNOWN")
    
    def visit_unary_op(self, node):
        """Valida operação unária."""
        node.operand.accept(self)
        operand_type = self._get_type(node.operand)
        
        if not operand_type:
            self._set_type(node, "UNKNOWN")
            return
        
        if node.operator in ['+', '-']:
            if not self.type_checker.is_numeric(operand_type):
                self._add_error(
                    f"Operador '{node.operator}' requer tipo numérico"
                )
            self._set_type(node, operand_type)
        elif node.operator == '.NOT.':
            if not self.type_checker.is_logical(operand_type):
                self._add_error(f"'.NOT.' requer tipo LOGICAL")
            self._set_type(node, "LOGICAL")
    
    def visit_function_call(self, node):
        """Valida chamada de função."""
        if node.arguments:
            # Handle both list and single argument cases
            args = node.arguments if isinstance(node.arguments, list) else [node.arguments]
            for arg in args:
                arg.accept(self)
                arg_type = self._get_type(arg)
                self._set_type(node, arg_type or "UNKNOWN")
    
    def visit_array_access(self, node):
        """Valida acesso a array."""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self._add_error(f"Array '{node.name}' não declarado")
            self._set_type(node, "UNKNOWN")
            return
        
        if not symbol.dimensions:
            self._add_error(f"'{node.name}' não é um array")
            self._set_type(node, "UNKNOWN")
            return
        
        if len(node.indices) != len(symbol.dimensions):
            self._add_error(
                f"Número de índices incorreto para '{node.name}'"
            )
        
        for idx in node.indices:
            idx.accept(self)
        
        self._set_type(node, symbol.type_name)
    
    # ====================================================================
    # Statements
    # ====================================================================
    
    def visit_assignment(self, node):
        """Valida atribuição."""
        node.value.accept(self)
        rvalue_type = self._get_type(node.value)
        
        if not rvalue_type:
            return
        
        symbol = self.symbol_table.lookup(node.target.name)
        if symbol is None:
            self._add_error(f"Variável alvo '{node.target.name}' não declarada")
            return
        
        lvalue_type = symbol.type_name
        
        try:
            self.type_checker.verify_assignment(rvalue_type, lvalue_type)
        except SemanticError as e:
            self._add_error(str(e))
    
    def visit_if_statement(self, node):
        """Valida IF statement."""
        node.condition.accept(self)
        cond_type = self._get_type(node.condition)
        
        if cond_type and not self.type_checker.is_logical(cond_type):
            self._add_error(f"Condição IF deve ser LOGICAL")
        
        if node.then_body:
            for stmt in node.then_body:
                stmt.accept(self)
        
        if hasattr(node, 'else_body') and node.else_body:
            for stmt in node.else_body:
                stmt.accept(self)
    
    def visit_do_loop(self, node):
        """Valida DO loop."""
        self.active_loops.append(len(self.active_loops))
        
        node.start.accept(self)
        node.end.accept(self)
        
        start_type = self._get_type(node.start)
        end_type = self._get_type(node.end)
        
        if start_type and not self.type_checker.is_numeric(start_type):
            self._add_error("Valor inicial DO deve ser numérico")
        
        if end_type and not self.type_checker.is_numeric(end_type):
            self._add_error("Valor final DO deve ser numérico")
        
        if node.body:
            for stmt in node.body:
                stmt.accept(self)
        
        if hasattr(node, 'label') and node.label:
            self.labels_defined[node.label] = "do_loop"
        
        self.active_loops.pop()
    
    def visit_goto_statement(self, node):
        """Valida GOTO statement."""
        if node.label not in self.labels_defined:
            pass
    
    def visit_continue_statement(self, node):
        """Valida CONTINUE statement."""
        if not self.active_loops:
            self._add_error("CONTINUE fora de DO loop")
    
    def visit_read_statement(self, node):
        """Valida READ statement."""
        if node.variables:
            for var in node.variables:
                symbol = self.symbol_table.lookup(var.name)
                if symbol is None:
                    self._add_error(f"Variável '{var.name}' em READ não declarada")
                var.accept(self)
    
    def visit_print_statement(self, node):
        """Valida PRINT statement."""
        if node.expressions:
            for expr in node.expressions:
                expr.accept(self)
    
    def visit_function_declaration(self, node):
        """Valida FUNCTION declaration."""
        try:
            self.symbol_table.declare(
                node.name,
                node.return_type,
                is_function=True,
                return_type=node.return_type,
                parameters=[p.name for p in (node.parameters or [])]
            )
        except SemanticError as e:
            self._add_error(str(e))
            return
        
        self.symbol_table.push_scope()
        
        if node.parameters:
            for param in node.parameters:
                param.accept(self)
        
        if node.body:
            for stmt in node.body:
                stmt.accept(self)
        
        self.symbol_table.pop_scope()
