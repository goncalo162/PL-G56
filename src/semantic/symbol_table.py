"""
Tabela de Símbolos
==================

Gerencia informações sobre variáveis, funções e escopos.
Suporta múltiplos níveis de escopo para subprogramas.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from src.exceptions import SemanticError


@dataclass
class SymbolInfo:
    """
    Informação armazenada sobre um símbolo na tabela de símbolos.
    
    Atributos:
        name: Nome do símbolo
        type_name: Tipo Fortran (INTEGER, REAL, LOGICAL, CHARACTER, COMPLEX)
        dimensions: Para arrays: lista de tuplas [(lower, upper), ...] por dimensão
                   Ex: [(1, 10), (1, 5)] para array 10x5
        initial_value: Valor inicial atribuído em declaração
        is_parameter: TRUE se é um PARÂMETRO FORMAL de função/subrotina (argumento)
                     Ex: SUBROUTINE FOO(X, Y) — X e Y têm is_parameter=True
        is_constant: TRUE se é uma CONSTANTE PARAMETER Fortran 77 (imutável em compilação)
                    Ex: PARAMETER (PI=3.14159) — PI tem is_constant=True
                    Nota: Uma constante PARAMETER pode ser argumento, tendo ambos flags=True
        is_function: TRUE se é uma função (vs variável comum)
        return_type: Tipo de retorno se is_function=True
        parameters: Lista de parâmetros se is_function=True
        scope_level: Nível de escopo onde foi declarado (0=global)
    """
    name: str
    type_name: str  # INTEGER, REAL, LOGICAL, CHARACTER, COMPLEX
    dimensions: Optional[list] = None  # Para arrays: [(1, 10), (1, 5)]
    initial_value: Optional[Any] = None # Valor inicial para variáveis
    is_parameter: bool = False # Se é um parâmetro de função/subrotina
    is_constant: bool = False # Se é uma constante PARAMETER de Fortran
    is_function: bool = False # Se é uma função (para diferenciar de variáveis comuns)
    return_type: Optional[str] = None # Tipo de retorno para funções
    parameters: Optional[list] = None  # Para funções
    scope_level: int = 0 # Nível de escopo onde o símbolo foi declarado
    
    def __repr__(self):
        if self.is_function:
            return f"{self.name}({self.return_type}) @ scope {self.scope_level}"
        return f"{self.type_name} {self.name}" + (f"[{self.dimensions}]" if self.dimensions else "")


class SymbolTable:
    """
    Tabela de Símbolos com suporte a múltiplos escopos.
    
    Atributos:
        scopes: Lista de dicionários representando escopos
        current_level: Nível de escopo atual
    """
    
    def __init__(self):
        """Inicializa com escopo global."""
        self.scopes = [{}]  # Escopo global
        self.current_level = 0 # Nível do escopo atual (0 = global)
    
    def declare(self, name: str, type_name: str, **kwargs) -> SymbolInfo:
        """
        Declara um novo símbolo no escopo atual.
        
        Args:
            name: Nome do símbolo
            type_name: Tipo (INTEGER, REAL, LOGICAL, etc)
            **kwargs: Argumentos adicionais (dimensions, initial_value, etc)
            
        Returns:
            SymbolInfo: Informação do símbolo criado
            
        Raises:
            SemanticError: Se símbolo já existe no escopo atual
        """
        if name in self.scopes[self.current_level]:
            raise SemanticError(f"Símbolo '{name}' já declarado neste escopo")
        
        symbol = SymbolInfo(
            name=name,
            type_name=type_name,
            scope_level=self.current_level,
            **kwargs
        )
        self.scopes[self.current_level][name] = symbol
        return symbol
    
    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """
        Procura um símbolo começando do escopo atual até ao global.
        
        Args:
            name: Nome do símbolo
            
        Returns:
            SymbolInfo se encontrado, None caso contrário
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_in_current(self, name: str) -> Optional[SymbolInfo]:
        """Procura apenas no escopo atual."""
        return self.scopes[self.current_level].get(name)
    
    def push_scope(self):
        """Abre um novo escopo (para subprogramas, blocos IF, etc)."""
        self.scopes.append({})
        self.current_level += 1
    
    def pop_scope(self):
        """Fecha o escopo atual."""
        if self.current_level > 0:
            self.scopes.pop()
            self.current_level -= 1
        else:
            raise SemanticError("Tentativa de fechar escopo global")
    
    def get_all_in_scope(self, level: int = None) -> Dict[str, SymbolInfo]:
        """
        Retorna todos os símbolos num nível de escopo.
        
        Args:
            level: Nível de escopo (default: atual)
            
        Returns:
            Dicionário de símbolos
        """
        if level is None:
            level = self.current_level
        if 0 <= level < len(self.scopes):
            return self.scopes[level].copy()
        return {}
    
    def get_current_scope_symbols(self) -> Dict[str, SymbolInfo]:
        """Retorna todos os símbolos do escopo atual."""
        return self.scopes[self.current_level].copy()
    
    def __repr__(self):
        return f"SymbolTable(level={self.current_level}, scopes={len(self.scopes)})"
