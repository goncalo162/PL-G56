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
    """Informação armazenada sobre um símbolo."""
    name: str
    type_name: str  # INTEGER, REAL, LOGICAL, CHARACTER, COMPLEX
    dimensions: Optional[list] = None  # Para arrays: [(1, 10), (1, 5)]
    initial_value: Optional[Any] = None
    is_parameter: bool = False
    is_function: bool = False
    return_type: Optional[str] = None
    parameters: Optional[list] = None  # Para funções
    scope_level: int = 0
    
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
        self.current_level = 0
    
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
