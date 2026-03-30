"""
Analisador Léxico (Lexer)
==========================

Implementa o lexer usando ply.lex para converter código Fortran em tokens.
Usa o Preprocessor internamente para suportar as formatações 'fixed' e 'free'.

Uso:
    from src.lexer.lexer import Lexer
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
"""

import ply.lex as lex
from src.exceptions import LexerError
from src.config import KEYWORDS, FORMAT
from .tokens import Token, TokenType
from .preprocessor import Preprocessor


class Lexer:
    """
    Analisador léxico para Fortran 77.
    
    Converte código-fonte Fortran em uma série de tokens.
    Utiliza o preprocessor em conjunto com expressões regulares (ply.lex) para 
    identificar, de forma agnóstica ao formato (Fixed ou Free):
    - Palavras-chave
    - Identificadores
    - Números (inteiros e reais)
    - Operadores
    - Strings
    - Comentários
    """

    # --- PLY Regex Rules ---
    # TODO: PLY exige uma variável ou propriedade 'tokens' (lista de strings).
    # Deves incluir os listados no documento `tokens.py` + as KEYWORDS do `config.py`.
    # Exemplo: tokens = ['IDENTIFIER', 'INTEGER_LITERAL', 'PLUS'] + list(KEYWORDS.values())
    tokens = []

    # TODO: Definir caracteres a serem ignorados (e.g. t_ignore = ' \t')

    # TODO: Definir regras Regex simples para operadores. 
    # O PLY identifica métodos ou strings a começar com 't_'
    # Exemplo: t_PLUS = r'\+'
    
    # TODO: Criar regras mais complexas através de funções para:
    # 1. Identificadores (e verificar se dão match com alguma keyword de config.KEYWORDS)
    # 2. Números (Inteiros e Reais)
    # 3. Operadores Lógicos/Relacionais (.EQ., .TRUE.)
    # 4. Strings ('texto')
    
    # TODO: Regra para contabilizar quebras de linha (`t_newline`)
    
    # TODO: Regra para tratamento de erro (`t_error`)
    
    def __init__(self):
        """Inicializa o lexer do PLY e o estado base."""
        self.line = 1
        self.column = 1
        self.tokens_list = []
        # TODO: Descomentar e criar a instância verdadeira do PLY assim que os tokens estiverem definidos
        # self.lexer = lex.lex(module=self)
    
    def tokenize(self, source_code: str) -> list:
        """
        Tokeniza código-fonte Fortran aplicando o Pré-Processamento primeiro.
        
        Args:
            source_code: String contendo o código Fortran cru
            
        Returns:
            Lista de objetos Token
            
        Raises:
            LexerError: Se encontrar um caractere inválido
        """
        # 1. PROCESSAMENTO INICIAL (Fixed ou Free form resolvido aqui)
        # Limpa comentários e concatena linhas de continuação antes de chegar ao Regex
        processed_code = Preprocessor.process(source_code, FORMAT)
        
        # 2. ALIMENTAR O LEXER COM CÓDIGO NORMALIZADO
        # TODO: Passar o 'processed_code' para o ply.lex (ex: self.lexer.input(processed_code))
        
        # 3. EXTRAIR TOKENS
        # TODO: Iterar sobre self.lexer.token() e guardar numa lista até ser vazio.
        # Retornar essa lista.
            
        return []
