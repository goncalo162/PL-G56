"""
Analisador Semântico (Semantic Analyzer)
=========================================

Valida a corretude semântica da AST após o parsing.

Responsabilidades:
- Construir tabela de símbolos (declarações de variáveis e funções)
- Verificar se variáveis são usadas após declaração
- Validar compatibilidade de tipos em expressões e atribuições
- Validar labels e estruturas de controlo (DO loops, GOTO)
- Rastrear scopes (global vs subprogramas)

Padrão de Implementação:
- Usa o padrão Visitor para percorrer a AST
- Cada método visit_* corresponde a um tipo de nó AST
- Retorna tipo do nó (para propagação em expressões)
- Recolhe erros em lista self.errors
"""

from typing import Optional, Dict, List
from src.exceptions import SemanticError
from src.ast.nodes import VariableDeclaration
from src.ast.visitor import ASTVisitor
from src.semantic.symbol_table import SymbolTable
from src.semantic.type_checker import TypeChecker


class SemanticAnalyzer(ASTVisitor):
    """
    Analisador semântico que valida a corretude do programa Fortran 77.
    
    O analisador percorre a AST e valida:
    - declaração de símbolos antes do uso
    - compatibilidade de tipos em expressões e atribuições
    - uso correto de instruções de controlo de fluxo
    - definições de labels em DO/GOTO
    - scopes de funções e subprogramas
    
    A nota importante sobre type_stack é que os nós AST não são
    hasháveis, por isso usamos `id(node)` como chave interna.
    """
    
    def __init__(self):
        """Inicializa o analisador semântico."""
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()
        self.errors: List[str] = [] # Lista de erros semânticos encontrados
        # Usamos id(node) porque os nós AST não implementam __hash__.
        self.type_stack: Dict[int, str] = {} # Mapeia cada nó AST para seu tipo (INTEGER, REAL, etc)
        self.labels_defined: Dict[int, str] = {} # Mapeia cada label numérico para seu contexto
        self.goto_labels: List[int] = [] # Labels referenciados por GOTO, para validar depois
        self.active_loops: List[int] = [] # Pilha de IDs de loops ativos (para validar CONTINUE/EXIT)
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

    def _register_statement_label(self, stmt: object):
        """Regista labels de statements para validação de GOTO."""
        label = getattr(stmt, 'statement_label', None)
        if label is not None:
            self.labels_defined[label] = "statement"
    
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
        """Processa o nó raiz do programa.
        
        A ordem importa: primeiro declarações globais, depois assinaturas de
        subprogramas, depois statements, e por fim os corpos dos subprogramas.
        Isto permite chamadas a funções definidas após o END do programa
        principal, como é comum em Fortran 77.
        """
        if node.declarations:
            for decl in node.declarations:
                decl.accept(self)

        if node.subprograms:
            for subprog in node.subprograms:
                self._declare_function_symbol(subprog)
        
        if node.statements:
            for stmt in node.statements:
                self._register_statement_label(stmt)
                stmt.accept(self)
        
        if node.subprograms:
            for subprog in node.subprograms:
                subprog.accept(self)
        
        self._validate_goto_labels()

    def _declare_function_symbol(self, node):
        """Regista a assinatura de uma função sem visitar ainda o corpo."""
        existing = self.symbol_table.lookup_in_current(node.name)
        parameters = [p.name for p in (node.parameters or [])]

        if existing is None:
            try:
                self.symbol_table.declare(
                    node.name,
                    node.return_type,
                    is_function=True,
                    return_type=node.return_type,
                    parameters=parameters
                )
            except SemanticError as e:
                self._add_error(str(e))
            return

        # Fortran 77 permite declarar o tipo da função no programa principal,
        # por exemplo `INTEGER CONVRT`, antes de definir `INTEGER FUNCTION CONVRT`.
        if not existing.is_function and not existing.dimensions and existing.type_name == node.return_type:
            existing.is_function = True
            existing.return_type = node.return_type
            existing.parameters = parameters
            return

        if existing.is_function:
            return

        self._add_error(f"Símbolo '{node.name}' já declarado neste escopo")
    
    # ====================================================================
    # Declarações
    # ====================================================================
    
    def visit_variable_declaration(self, node):
        """Regista uma variável no scope atual.
        
        Se existir um valor inicial, valida se ele é compatível com o tipo
        declarado usando o TypeChecker.
        """
        valid_types = ["INTEGER", "REAL", "LOGICAL", "CHARACTER", "COMPLEX"]
        if node.type_name not in valid_types:
            self._add_error(f"Tipo desconhecido '{node.type_name}'")
            return
        
        initial_value = getattr(node, 'initial_value', None)
        try:
            self.symbol_table.declare(
                node.name,
                node.type_name,
                dimensions=getattr(node, 'dimensions', None),
                initial_value=initial_value
            )
        except SemanticError as e:
            self._add_error(str(e))
            return
        
        if initial_value is not None:
            # Valida o tipo do valor inicial antes de usar a variável.
            initial_value.accept(self)
            value_type = self._get_type(initial_value)
            if value_type:
                try:
                    self.type_checker.verify_assignment(value_type, node.type_name)
                except SemanticError as e:
                    self._add_error(str(e))
    
    # ====================================================================
    # Expressões
    # ====================================================================
    
    def visit_identifier(self, node):
        """Valida o uso de um identificador.
        
        Se o identificador não foi declarado, regista erro e marca como
        tipo desconhecido para evitar que a análise pare completamente.
        """
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self._add_error(f"Variável '{node.name}' não declarada")
            self._set_type(node, "UNKNOWN")
        else:
            self._set_type(node, symbol.type_name)
    
    def visit_literal(self, node):
        """Determina o tipo do literal diretamente do valor."""
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
        """Valida e infere tipo de uma operação binária."""
        # Primeiro valida os operandos recursivamente.
        node.left.accept(self)
        node.right.accept(self)
        
        left_type = self._get_type(node.left)
        right_type = self._get_type(node.right)
        
        if not left_type or not right_type:
            # Se algum operando estiver inválido, o resultado também fica desconhecido.
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
        """Valida e infere tipo de uma operação unária."""
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
        """Valida chamada de função e os seus argumentos."""
        args = node.arguments if isinstance(node.arguments, list) else [node.arguments]

        arg_types = []
        for arg in args:
            arg.accept(self)
            arg_types.append(self._get_type(arg) or "UNKNOWN")

        builtin_returns = {
            "MOD": arg_types[0] if arg_types else "UNKNOWN",
            "ABS": arg_types[0] if arg_types else "UNKNOWN",
            "SQRT": "REAL",
            "SIN": "REAL",
            "COS": "REAL",
            "EXP": "REAL",
            "LOG": "REAL",
            "INT": "INTEGER",
            "REAL": "REAL",
            "NINT": "INTEGER",
        }
        function_name = node.function_name.upper()
        if function_name in builtin_returns:
            self._set_type(node, builtin_returns[function_name])
            return

        symbol = self.symbol_table.lookup(node.function_name)
        if symbol is None:
            self._add_error(f"Função '{node.function_name}' não declarada")
            self._set_type(node, "UNKNOWN")
            return

        if not symbol.is_function:
            self._add_error(f"'{node.function_name}' não é uma função")
            self._set_type(node, "UNKNOWN")
            return

        self._set_type(node, symbol.return_type or symbol.type_name)
    
    def visit_array_access(self, node):
        """Valida acesso a um array e suas dimensões."""
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
        """Valida uma atribuição simples."""
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
        """Valida uma instrução IF simples."""
        node.condition.accept(self)
        cond_type = self._get_type(node.condition)
        
        if cond_type and not self.type_checker.is_logical(cond_type):
            self._add_error(f"Condição IF deve ser LOGICAL")
        
        if node.then_body:
            for stmt in node.then_body:
                self._register_statement_label(stmt)
                stmt.accept(self)
        
        if hasattr(node, 'else_body') and node.else_body:
            for stmt in node.else_body:
                self._register_statement_label(stmt)
                stmt.accept(self)
    
    def visit_do_loop(self, node):
        """Valida um ciclo DO e marca o loop como ativo."""
        # Armazenamos um identificador de loop para permitir CONTINUE dentro dele.
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
                self._register_statement_label(stmt)
                stmt.accept(self)
        
        if hasattr(node, 'label') and node.label:
            # Regista label para eventualmente validar GOTO.
            self.labels_defined[node.label] = "do_loop"
        
        self.active_loops.pop()
    
    def visit_goto_statement(self, node):
        """Regista um GOTO para validação posterior de label."""
        if node.label is not None:
            self.goto_labels.append(node.label)
    
    def visit_continue_statement(self, node):
        """Valida CONTINUE: só deve existir dentro de um DO."""
        if not self.active_loops:
            self._add_error("CONTINUE fora de DO loop")

    def _validate_goto_labels(self):
        """Verifica se todos os labels referenciados por GOTO existem."""
        for label in self.goto_labels:
            if label not in self.labels_defined:
                self._add_error(f"GOTO para label não definido: {label}")
    
    def visit_read_statement(self, node):
        """Valida um READ, garantindo que todas as variáveis existam."""
        if node.variables:
            for var in node.variables:
                symbol = self.symbol_table.lookup(var.name)
                if symbol is None:
                    self._add_error(f"Variável '{var.name}' em READ não declarada")
                var.accept(self)
    
    def visit_print_statement(self, node):
        """Valida um PRINT avaliando todas as expressões de saída."""
        if node.expressions:
            for expr in node.expressions:
                expr.accept(self)
    
    def visit_function_declaration(self, node):
        """Valida declaração de função e abre novo scope de parâmetros."""
        if self.symbol_table.lookup_in_current(node.name) is None:
            self._declare_function_symbol(node)
        
        # Função tem scope próprio para parâmetros e variáveis locais.
        self.symbol_table.push_scope()
        
        param_names = {param.name for param in (node.parameters or [])}
        local_param_types = {
            stmt.name: stmt.type_name
            for stmt in (node.body or [])
            if isinstance(stmt, VariableDeclaration) and stmt.name in param_names
        }

        if node.parameters:
            for param in node.parameters:
                try:
                    self.symbol_table.declare(
                        param.name,
                        local_param_types.get(param.name, param.type_name),
                        is_parameter=True
                    )
                except SemanticError as e:
                    self._add_error(str(e))
        
        if node.body:
            for stmt in node.body:
                if isinstance(stmt, VariableDeclaration) and stmt.name in param_names:
                    continue
                self._register_statement_label(stmt)
                stmt.accept(self)
        
        self.symbol_table.pop_scope()
