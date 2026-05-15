"""
Definição de Tokens do Lexer
=============================

Define os tipos de tokens e as estruturas para representá-los.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TokenType(Enum):
    """Tipos de tokens do Fortran 77."""
    
    # Literais
    INTEGER_LITERAL = "INTEGER_LITERAL"
    REAL_LITERAL = "REAL_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    LOGICAL_LITERAL = "LOGICAL_LITERAL"
    
    # Identificadores e palavras-chave
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    
    # Operadores aritméticos
    PLUS = "PLUS"           # +
    MINUS = "MINUS"         # -
    MULTIPLY = "MULTIPLY"   # *
    DIVIDE = "DIVIDE"       # /
    CONCAT = "CONCAT"       # //
    POWER = "POWER"         # **
    
    # Operadores relacionais
    LT = "LT"  # .LT.
    LE = "LE"  # .LE.
    GT = "GT"  # .GT.
    GE = "GE"  # .GE.
    EQ = "EQ"  # .EQ.
    NE = "NE"  # .NE.
    
    # Operadores lógicos
    AND = "AND"  # .AND.
    OR = "OR"    # .OR.
    NOT = "NOT"  # .NOT.
    
    # Atribuição
    ASSIGN = "ASSIGN"
    
    # Delimitadores
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    COLON = "COLON"
    LABEL = "LABEL"
    
    # Fim de linha
    EOL = "EOL"
    EOF = "EOF"


@dataclass
class Token:
    """
    Representa um token do programa Fortran.
    
    Atributos:
        type: Tipo do token (TokenType)
        value: Valor do token (string, número, etc)
        line: Número da linha no código-fonte
        column: Número da coluna no código-fonte
    """
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}:{self.column})"
