"""
Definição de Exceções do Compilador
====================================

Define classes de exceção para diferentes fases do compilador.
"""


class CompilerError(Exception):
    """Classe base para todos os erros do compilador."""
    
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())
    
    def _format_message(self):
        if self.line and self.column:
            return f"Linha {self.line}, Coluna {self.column}: {self.message}"
        elif self.line:
            return f"Linha {self.line}: {self.message}"
        return self.message


class LexerError(CompilerError):
    """Erro durante análise léxica."""
    pass


class ParserError(CompilerError):
    """Erro durante análise sintática."""
    pass


class SemanticError(CompilerError):
    """Erro durante análise semântica."""
    pass


class CodeGenerationError(CompilerError):
    """Erro durante geração de código."""
    pass


class CompilationError(CompilerError):
    """Erro geral de compilação."""
    pass
