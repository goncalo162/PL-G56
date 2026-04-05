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
    # PLY exige uma variável ou propriedade 'tokens' (lista de strings).
    # Inclui todos os tipos de token do TokenType e as keywords do config.KEYWORDS.
    tokens = [token.name for token in TokenType] + list(KEYWORDS)

    # Ignora espaços e tabulações entre tokens
    t_ignore = ' \t'

    # Regras Regex simples para operadores aritméticos e delimitadores
    t_POWER    = r'\*\*'
    t_PLUS     = r'\+'
    t_MINUS    = r'-'
    t_MULTIPLY = r'\*'
    t_DIVIDE   = r'/'
    t_ASSIGN   = r'='
    t_LPAREN   = r'\('
    t_RPAREN   = r'\)'
    t_COMMA    = r','
    t_COLON    = r':'

    # Operadores relacionais e lógicos
    t_LT  = r'\.LT\.'
    t_LE  = r'\.LE\.'
    t_GT  = r'\.GT\.'
    t_GE  = r'\.GE\.'
    t_EQ  = r'\.EQ\.'
    t_NE  = r'\.NE\.'
    t_AND = r'\.AND\.'
    t_OR  = r'\.OR\.'
    t_NOT = r'\.NOT\.'
    
    # Regras complexas (Números Reais, Inteiros, Identificadores/Keywords, Strings, Lógicos)

    def t_REAL_LITERAL(self, t):
        r'\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+'
        t.value = float(t.value)
        return t

    def t_INTEGER_LITERAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_LOGICAL_LITERAL(self, t):
        r'\.(TRUE|FALSE|true|false)\.'
        t.value = (t.value.upper() == '.TRUE.')
        return t

    def t_STRING_LITERAL(self, t):
        r"'(?:[^']|'')*'"
        # Fortran usa '' dentro da string para representar uma aspa escape
        t.value = t.value[1:-1].replace("''", "'")
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        upper_val = t.value.upper()
        # Verificar se identificador é uma Keyword e re-atribuir o tipo
        if upper_val in KEYWORDS:
            t.type = upper_val
        return t
    
    # Regra para contabilizar quebras de linha mantendo formato do PLY
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Regra para tratamento de erro
    def t_error(self, t):
        raise LexerError(f"Caractere inválido '{t.value[0]}' na linha {t.lexer.lineno}")
    
    def __init__(self):
        """Inicializa o lexer do PLY e o estado base."""
        self.line = 1
        self.column = 1
        self.tokens_list = []
        # Cria a instância verdadeira do PLY assim que os tokens estiverem definidos
        self.lexer = lex.lex(module=self)
    
    def tokenize(self, source_code: str, preprocess: bool = True):
        """
        Atualiza o estado do lexer com o código pré-processado e devolve a 
        instância do lexer do PLY (necessária para ser consumida pelo YACC).
        
        Args:
            source_code: String contendo o código Fortran cru
            preprocess: Se True, aplica o pré-processador (default True)
        Returns:
            Instância do PLY lexer pronta a gerar tokens.
        """
        # Se preprocess=True, aplica o pré-processador normalmente
        if preprocess:
            processed_code = Preprocessor.process(source_code, FORMAT)
        else:
            processed_code = source_code
        # Alimenta o lexer com o código (pré-processado ou não)
        self.lexer.input(processed_code)
        return self.lexer

    def get_tokens(self, source_code: str, preprocess: bool = False) -> list:
        """
        Gera uma lista com todos os objetos Token (custom class) extraídos do código.
        Ideal para utilizar em testes isolados do lexer.
        Se preprocess=False, não aplica o pré-processador (útil para testes unitários do lexer puro).
        """
        self.tokenize(source_code, preprocess=preprocess)
        tokens = []
        while True:
            t = self.lexer.token()
            if not t:
                break
            # Cria um objeto Token personalizado 
            token_obj = Token(
                type=TokenType[t.type] if t.type in TokenType.__members__ else t.type,
                value=t.value,
                line=t.lineno if hasattr(t, 'lineno') else self.line,
                column=t.lexpos if hasattr(t, 'lexpos') else self.column
            )
            tokens.append(token_obj)
        return tokens

#DUVIDA Opção 2: Pré-processador fora do Lexer (mais modular)
# Nesta abordagem, o pré-processador seria chamado explicitamente antes do lexer, fora da classe Lexer.
# Exemplo de uso:
#   processed_code = Preprocessor.process(source_code, FORMAT)
#   tokens = lexer.get_tokens(processed_code, preprocess=False)
# Prós:
#   - Separação clara de responsabilidades (SRP): cada componente faz só uma coisa.
#   - Facilita testes unitários e manutenção.
#   - O lexer pode ser reutilizado em outros contextos sem depender do pré-processador.
# Contras:
#   - O utilizador do Lexer precisa lembrar de sempre pré-processar o código antes.
#   - Pode aumentar a complexidade do pipeline principal.
