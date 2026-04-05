# Estrutura do Projeto - Guia Rápido

## 📁 Estrutura de Diretórios

```
PL-G56/
│
├── src/                           # Código-fonte do compilador
│   ├── __init__.py               # Inicialização do pacote
│   ├── config.py                 # Configuração global (F77, FORMAT, KEYWORDS)
│   ├── exceptions.py             # Classes de exceção (LexerError, ParserError, etc)
│   ├── main.py                   # Ponto de entrada do compilador
│   │
│   ├── lexer/                    # Fase 1: Análise Léxica
│   │   ├── __init__.py
│   │   ├── tokens.py             # Definição e classe Token
│   │   └── lexer.py              # Implementação do Lexer (ply.lex)
│   │
│   ├── parser/                   # Fase 2: Análise Sintática
│   │   ├── __init__.py
│   │   ├── grammar.py            # (opcional) Definição formal da gramática
│   │   └── parser.py             # Implementação do Parser (ply.yacc)
│   │
│   ├── ast/                      # Fase 2-3: Estruturas de Sintaxe Abstrata
│   │   ├── __init__.py
│   │   ├── nodes.py              # Classes de nós (Program, IfStatement, etc)
│   │   └── visitor.py            # Padrão Visitor + PrintVisitor
│   │
│   ├── semantic/                 # Fase 3: Análise Semântica
│   │   ├── __init__.py
│   │   ├── analyzer.py           # SemanticAnalyzer (SymbolTable, validações)
│   │   └── symbol_table.py       # (opcional se em analyzer.py)
│   │
│   ├── codegen/                  # Fase 4: Geração de Código
│   │   ├── __init__.py
│   │   ├── ir.py                 # Representação Intermediária (IR)
│   │   ├── ir_generator.py       # Gerador de IR via Visitor
│   │   └── vm_codegen.py         # (futura) Gerador de código VM
│   │
│   └── optimizer/                # Fase 5: Otimização (opcional)
│       ├── __init__.py
│       └── optimizer.py          # Passes de otimização
│
├── tests/                        # Testes e exemplos
│   ├── __init__.py
│   ├── test_compiler.py          # Testes unitários (unittest/pytest)
│   ├── test_lexer.py             # (separado) Testes lexer
│   ├── test_parser.py            # (separado) Testes parser
│   ├── test_semantic.py          # (separado) Testes semântica
│   └── examples/                 # Programas Fortran para teste
│       ├── hello.f               # Exemplo: Olá Mundo
│       ├── factorial.f           # Exemplo: Fatorial
│       └── prime.f               # Exemplo: Verificar primo
│
├── docs/                         # Documentação técnica
│   ├── arquitetura.md           # Visão da arquitetura + padrões
│   ├── grammar.md               # Gramática em EBNF + exemplos
│   └── design_decisions.md      # Decisões arquiteturais
│
├── README.md                    # Instruções gerais do projeto
├── requirements.txt             # Dependências (ply, pytest, etc)
└── .gitignore                  # Ficheiros ignorados por git
```

## 🔄 Fluxo de Compilação

```
programa.f
    ↓
[LEXER] → tokens
    ↓
[PARSER] → AST
    ↓
[SEMANTIC] → AST validada
    ↓
[CODEGEN] → IR
    ↓
[OPTIMIZER] → IR otimizada (opcional)
    ↓
código VM
```

## 📝 Diagrama de Responsabilidades

| Módulo | Entrada | Saída | Usa |
|--------|---------|-------|-----|
| **lexer** | String (código) | List[Token] | config.py, exceptions.py, tokens.py |
| **parser** | List[Token] | Program (AST) | ast/nodes.py, exceptions.py |
| **semantic** | Program (AST) | Program validada | ast/visitor.py, exceptions.py |
| **codegen** | Program (AST) | IRProgram | ast/visitor.py, ir.py, exceptions.py |
| **optimizer** | IRProgram | IRProgram otimizada | ir.py, exceptions.py |

## ✅ Checklist de Modularidade

- [x] Separação clara de fases
- [x] Cada módulo tem responsabilidade única
- [x] Interfaces bem definidas (entrada/saída claras)
- [x] Sem dependências circulares
- [x] Documentação em docstrings
- [x] Estrutura de exceções consistente
- [x] Testes por módulo
- [x] Configuração centralizada (config.py)

## 🎯 Como Estender

1. **Novo tipo de nó AST**
   - Adicionar classe em `ast/nodes.py`
   - Implementar `accept(visitor)`
   - Adicionar `visit_*` em `ASTVisitor`
   - Implementar em cada visitante

2. **Nova análise/otimização**
   - Criar classe que herda `ASTVisitor`
   - Implementar métodos `visit_*`
   - Usar `ast.accept(meu_visitante)`

3. **Novo preprocessor**
   - Adicionar em `src/preprocessor/`
   - Usar no `main.py` antes do lexer

## 🧪 Executar Testes

```bash
# Todos os testes
python -m pytest tests/

# Com cobertura
python -m pytest --cov=src tests/

# Um teste específico
python -m pytest tests/test_lexer.py::TestLexer::test_simple_program
```

## 🔨 Compilar um Programa

```bash
python -m src.main tests/examples/hello.f
```

## 📚 Referências

- **Padrão Visitor**: Design Patterns - Gang of Four
- **Compiladores**: "Compilers: Principles, Techniques, and Tools" (Dragon Book)
- **ply documentation**: https://www.dabeaz.com/ply/
- **Fortran 77 Standard**: ANSI X3.9-1978
