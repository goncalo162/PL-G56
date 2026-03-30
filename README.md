# Compilador Fortran 77

Um compilador para Fortran 77 (ANSI X3.9-1978) implementado em Python.

## Visão Geral

Este projeto implementa um compilador completo para Fortran 77 com as seguintes fases:

1. **Análise Léxica** - Tokenização do código-fonte
2. **Análise Sintática** - Construção da Interface Sintática Abstrata (AST)
3. **Análise Semântica** - Validação de tipos e coerência
4. **Geração de Código** - Produção de código intermediário
5. **Otimização** (opcional) - Melhorias de eficiência

## Estrutura do Projeto

```
src/
├── config.py           # Configuração global
├── exceptions.py       # Definições de exceções
├── main.py            # Ponto de entrada
├── lexer/
│   ├── tokens.py      # Definição de tokens
│   └── lexer.py       # Analisador léxico (ply.lex)
├── parser/
│   └── parser.py      # Analisador sintático (ply.yacc)
├── ast/
│   ├── nodes.py       # Nós da AST
│   └── visitor.py     # Padrão Visitor
├── semantic/
│   ├── analyzer.py    # Análise semântica
│   └── symbol_table.py # Tabela de símbolos (se necessário)
├── codegen/
│   ├── ir.py          # Representação intermediária
│   └── ir_generator.py # Gerador de IR
└── optimizer/
    └── optimizer.py   # Otimizações

tests/
├── test_compiler.py   # Testes unitários
└── examples/          # Exemplos Fortran
```

## Instalação

### Requisitos

- Python 3.8+
- ply

### Setup

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar testes
python -m pytest tests/
```

## Uso

### Compilar um Arquivo

```bash
python -m src.main programa.f
```

### Exemplo

```bash
python -m src.main tests/examples/hello.f
```

## Recursos Suportados

### Obrigatórios (Nota 10)

- [x] Declaração de tipos e variáveis
- [x] Expressões aritméticas
- [x] Operadores relacionais e lógicos
- [x] IF-THEN-ELSE
- [x] Ciclos DO com labels
- [x] GOTO
- [x] READ/PRINT

### Opcionais - Valorização

- [ ] SUBROUTINE e FUNCTION
- [ ] Otimização de código

## Documentação

Ver pasta `docs/` para:
- [Arquitetura](docs/arquitetura.md)
- [Gramática](docs/grammar.md)
- [Decisões de Design](docs/design_decisions.md)

## Notas Importantes

### Formato de Código

O compilador suporta **formato de colunas fixas** (fixed-form), que é o comportamento estrito do Standard Fortran 77 (ANSI X3.9-1978).
As regras principais são:
- Colunas 1-5: Reservadas para numeração de labels (ex: destinos de `GOTO` ou encerramento de `DO`).
- Coluna 6: Continuação de linha (se tiver um caractere diferente de espaço ou zero).
- Colunas 7-72: Código executável (as instruções).
- Coluna 1: Se começar por `C`, `c`, `*` ou `!`, a linha é ignorada (comentário).

Para alterar para formato livre (free-form), alterar em `src/config.py`:

```python
FORMAT = 'free'
```

### Padrões de Código

- Cada módulo é independente e testável
- Usar padrão **Visitor** para traversal da AST
- Documentação inline para funcionalidades complexas
- **Logger** para mensagens de depuração

## Equipa

Projeto de Processamento de Linguagens 2026 - PL-G56

## Prazos

- Entrega: 17/05/2026 às 23:59
- Defesa: 01/06/2026 a 05/06/2026
