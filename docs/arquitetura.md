# Arquitetura do Compilador

## Visão Geral

O compilador segue a arquitetura clássica de um compilador com separação clara de responsabilidades.

```
Código Fortran
     ↓
  [LEXER] - Análise Léxica
     ↓ (Tokens)
  [PARSER] - Análise Sintática
     ↓ (AST)
  [SEMANTIC] - Análise Semântica
     ↓ (AST validada)
  [CODEGEN] - Geração de Código
     ↓ (IR)
  [OPTIMIZER] - Otimização (opcional)
     ↓
  Código VM
```

## Componentes

### 1. Lexer (Análise Léxica)

**Responsabilidade:** Converter código-fonte em tokens

**Entrada:** String (código Fortran)
**Saída:** Lista de tokens

**Uso de ply.lex:**
- Definir tokens em `tokens.py`
- Implementar regras em `lexer.py`
- Suportar comentários (começam com `!` ou `*` na coluna 1)

### 2. Parser (Análise Sintática)

**Responsabilidade:** Construir a Árvore Sintática Abstrata (AST)

**Entrada:** Lista de tokens
**Saída:** AST (Program node)

**Uso de ply.yacc:**
- Definir regras de gramática BNF
- Implementar ações semânticas
- Tratar erros sintáticos

### 3. Análise Semântica

**Responsabilidade:** Validar corretude semântica

**Verificações:**
- Variáveis declaradas antes do uso
- Compatibilidade de tipos
- Labels únicos e referenciados
- CONTINUE corresponde a DO
- Argumentos de função compatíveis

**Usar padrão Visitor:**
```python
ast.accept(semantic_analyzer)
```

### 4. Geração de Código

**Responsabilidade:** Produzir código intermediário e/ou código VM

**Fases:**
1. Converter AST para IR (Intermediate Representation)
2. Traduzir IR para código VM

**IR (Representação Intermediária):**
- Operações básicastí (add, sub, mul, div, etc)
- Instruções de controle (goto, label, cond_goto)
- Simplifica otimizações posteriores

### 5. Otimizador (Opcional)

**Responsabilidade:** Melhorar eficiência do código intermediário

**Otimizações possíveis:**
- Eliminação de código morto
- Propagação de constantes
- Desdobramento de loops
- Otimizações de memória

## Padrões de Design

### Padrão Visitor

Usado para desacoplar operações dos nós da AST:

```python
class MyAnalyzer(ASTVisitor):
    def visit_program(self, node):
        # Processar nó Program
        
    def visit_if_statement(self, node):
        # Processar nó IfStatement
        # ...

ast.accept(my_analyzer)
```

**Benefícios:**
- Fácil adicionar novas operações
- Não polui as classes de nó
- Simples com múltiplas análises

### Tabela de Símbolos

Mantém informações sobre variáveis:
- Nome, tipo, dimensões
- Suporta escopos (para subprogramas)

```python
symbol_table.declare('count', 'INTEGER')
info = symbol_table.lookup('count')
symbol_table.push_scope()  # Novo escopo
symbol_table.pop_scope()   # Finalizar escopo
```

## Fluxo de Compilação

```python
compiler = FortranCompiler()
output = compiler.compile(source_code)
```

## Tratamento de Erros

Erros estruturados com informação de localização:

```python
raise LexerError("Caractere inválido", line=10, column=5)
raise ParserError("Token inesperado", line=15, column=12)
raise SemanticError("Variável não declarada", line=20, column=8)
```

## Extensibilidade

### Adicionar Novo Recurso

1. Estender gramática em `parser.py`
2. Criar novo nó AST em `ast/nodes.py`
3. Implementar `accept()` no nó
4. Adicionar `visit_*` em `ASTVisitor`
5. Implementar lógica em analisadores
