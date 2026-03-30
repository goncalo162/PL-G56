# Decisões de Design

## Escolhas Arquiteturais

### 1. Formato de Código e Análise Léxica (O Padrão Pré-Processador)

**Decisão:** Suportar ambos os formatos (**Fixed e Free**) para maximizar a flexibilidade e garantir a nota de valorização, mas resolvendo a complexidade através de um **Pré-Processador Léxico** que corre antes do `ply.lex`.

**Justificação:**
- O projeto exige o "standard ANSI X3.9-1978" (que dita o *Fixed Form* obrigatório com colunas estritas), mas suportar o *Free Form* moderno demonstra uma modularidade superior.
- Ferramentas como o PLY funcionam via Expressões Regulares (Regex), que são extremamente ineficientes/frágeis a lidar com posições estritas de colunas (*fixed-form*).
- **A Solução (Pré-processador):** Ao introduzir um `src/lexer/preprocessor.py`, o texto de entrada é normalizado *antes* de chegar às Regex. No formato fixo, o pré-processador trata as colunas de labels (C1-C5), junta linhas de continuação (C6) de forma programática, e descarta comentários (C1 com 'C' ou '*').
- Isto permite que o `lexer.py` fique agnóstico ao formato original do ficheiro. As Regex do `ply.lex` apenas têm de se preocupar em capturar tokens de Fortran purificados, preservando a coerência e organização do código.

**Configuração:**
```python
# src/config.py
FORMAT = 'fixed' # ou 'free', o pré-processador encarrega-se do resto
```

### 2. Padrão Visitor para Análises

**Decisão:** Usar padrão Visitor para desacoplar operações de estruturas

**Estrutura:**
- `ASTNode.accept(visitor)` - Cada nó implementa
- `ASTVisitor` - Interface de visitantes
- Subclasses: `SemanticAnalyzer`, `CodeGenerator`, `PrintVisitor`

**Benefícios:**
- Fácil adicionar novas análises
- Sem poluição de responsabilidades
- Suporta múltiplas passes

### 3. Representação Intermediária (IR) - Código de Três Endereços (TAC)

**Decisão:** Gerar uma Representação Intermediária (IR) antes do código alvo VM, adotando especificamente o formato de **Código de Três Endereços (TAC - Three-Address Code)**.

**Justificação:**
- O enunciado não impõe um modelo de IR específico, e para a nota mínima (10), a AST poderia ser traduzida diretamente para VM. 
- Contudo, a geração de IR é crucial para a vertente de **Valorização** (Otimização). O TAC "desmonta" as expressões da AST em instruções atómicas e lineares (ex: no máximo 2 operandos e 1 resultado), eliminando a complexidade das árvores.
- Isto simplifica substancialmente a criação de algoritmos de Otimização no `src/optimizer`, como o dobramento de constantes ou eliminação de código morto, uma vez que é iterado como uma linha de montagem linear.
- **Ressalva de Flexibilidade:** Embora o TAC seja o eleito por ser o padrão canónico e mais limpo em compiladores, a arquitetura modular permite que, no futuro (ou dependendo da especificação final detalhada da VM), a classe `IRProgram` seja adaptada ou substituída sem quebrar as fases do "Frontend" (Lexer+Parser) ou do "Backend" (VM Codegen). Outros formatos como o *Static Single Assignment (SSA)* ou baseados em *Pilhas Puras* poderiam ser implementados substituindo apenas o módulo do `ir_generator.py`.

**Estrutura da IR:**
- `IRInstruction` - Instrução (dataclass com `opcode`, `result`, `arg1`, `arg2`, `label`)
- `IRProgram` - Coleção de instruções estruturadas

**Exemplo de TAC gerado:**
```text
t1 = a + b
t2 = t1 * c
result = t2 - d
```

### 4. Tratamento de Erros

**Decisão:** Exceções estruturadas com localização

```python
class CompilerError(Exception):
    def __init__(self, message, line=None, column=None):
        # Formato: "Linha X, Coluna Y: mensagem"
```

**Exemplo:**
```
Linha 15, Coluna 8: Variável 'count' não declarada
```

## Desenvolvimento Iterativo

### Fase 1: Foundation (Semanas 1-2)
- [ ] Estrutura de projeto
- [ ] Lexer básico (formato livre)
- [ ] Testes para lexer

### Fase 2: Parsing (Semanas 3-4)
- [ ] Parser com ply.yacc
- [ ] Construção de AST
- [ ] Tratamento de erros sintáticos

### Fase 3: Semântica (Semanas 5-6)
- [ ] Análise semântica
- [ ] Tabela de símbolos
- [ ] Verificação de tipos

### Fase 4: Geração (Semanas 7-8)
- [ ] Geração de IR
- [ ] Código VM
- [ ] Testes end-to-end

### Fase 5: Otimização (Semanas 9-10, opcional)
- [ ] Passes de otimização
- [ ] Eliminação de código morto

## Diferenciais (Valorização)

Para aumentar a nota além de 10:

1. **SUBROUTINE e FUNCTION** (obrigatório para 15+)
   - Implementar escopo de variáveis
   - Passar parâmetros por valor/referência
   - Retorno de valores

2. **Otimização de Código**
   - Eliminação de sub-expressões comuns
   - Propagação de constantes
   - Desdobramento de loops simples

3. **Recursos Extras**
   - Suporte a FORMAT (formatação de I/O)
   - Arrays multidimensionais completos
   - Strings e CHARACTER melhorados
   - Relatório de análise estática

## Abordagem Modular

Cada módulo é:

1. **Independente** - Pode ser testado sozinho
2. **Testável** - Entradas e saídas claras
3. **Reutilizável** - Interfaces bem definidas
4. **Documentado** - Docstrings Python completas

Exemplo de teste modular:

```python
def test_lexer_integers():
    lexer = Lexer()
    tokens = lexer.tokenize("INTEGER X, Y, Z")
    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[1].type == TokenType.IDENTIFIER
```

## Logging e Debugging

Usar `logging` padrão Python:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Iniciando compilação...")
logger.debug(f"Token: {token}")
logger.warning("Código suspeito detectado")
logger.error(f"Erro semântico: {error}")
```

Ativar em modo verbose:
```bash
python -m src.main --debug programa.f
```
