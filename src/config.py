"""
Configuração Global do Compilador
==================================

Define constantes, palavras-chave e configurações do compilador Fortran 77.
"""

# Versão da linguagem
LANGUAGE_VERSION = "Fortran 77 (ANSI X3.9-1978)"

# Formato suportado (Escolher um: 'fixed' ou 'free')
# O formato fixed usa colunas (labels em 1-5, código em 7+)
# O formato free permite espaços arbitrários
FORMAT = 'fixed'  # Alterado para 'fixed' para cumprir estritamente o standard F77

# Palavras-chave do Fortran 77
KEYWORDS = {
    'PROGRAM', 'SUBROUTINE', 'FUNCTION', 'END',
    'INTEGER', 'REAL', 'LOGICAL', 'CHARACTER', 'COMPLEX',
    'DIMENSION', 'PARAMETER', 'INTENT', 'IMPLICIT',
    'IF', 'THEN', 'ELSE', 'ELSEIF', 'ENDIF',
    'DO', 'CONTINUE', 'ENDDO', 'GOTO',
    'READ', 'WRITE', 'PRINT', 'FORMAT',
    'OPEN', 'CLOSE', 'REWIND',
    'CALL', 'RETURN',
    'TRUE', 'FALSE',
    'MOD', 'ABS', 'MAX', 'MIN',
    'SQRT', 'SIN', 'COS', 'EXP', 'LOG',
    'NINT', 'INT', 'REAL', 'DBLE', 'CMPLX',
    'LEN', 'INDEX', 'SUBSTRING'
}

# Operadores
OPERATORS = {
    '+', '-', '*', '/', '**',  # Aritméticos
    '.LT.', '.LE.', '.GT.', '.GE.', '.EQ.', '.NE.',  # Relacionais
    '.AND.', '.OR.', '.NOT.',  # Lógicos
    '=', '=='  # Atribuição
}

# Delimitadores
DELIMITERS = {'(', ')', '[', ']', '{', '}', ',', '.', ':', ';'}

# Tamanho máximo das linhas (formato fixed usa max 72)
MAX_LINE_LENGTH = 132
