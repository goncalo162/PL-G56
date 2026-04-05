
# Projeto de Processamento de Linguagens — Compilador Fortran 77

Compilador para Fortran 77 (ANSI X3.9-1978) desenvolvido no âmbito da unidade curricular de Processamento de Linguagens.

## Visão Geral

Este projeto implementa um compilador completo para Fortran 77 com as seguintes fases:

1. **Análise Léxica** - Tokenização do código-fonte
2. **Análise Sintática** - Construção da Interface Sintática Abstrata (AST)
3. **Análise Semântica** - Validação de tipos e coerência
4. **Geração de Código** - Produção de código intermediário
5. **Otimização** (opcional) - Melhorias de eficiência


## Instalação e Setup

1. **Criar ambiente virtual e instalar dependências:**

```bash
make setup
# Ativar ambiente virtual (sempre que fores trabalhar):
source venv/bin/activate
```

2. **Executar testes:**

```bash
make test-all           # Executa todos os testes
make test-lexer         # Testa apenas o lexer
```

3. **Executar o compilador:**

```bash
python -m src.main caminho/para/ficheiro.f
```

## Documentação

Ver pasta `docs/` para:
- [Arquitetura](docs/arquitetura.md)
- [Gramática](docs/grammar.md)
- [Decisões de Design](docs/design_decisions.md)

## Grupo 56

- A106804 - Alice Soares
- A106914 - Gonçalo Martins
- A107367 - João Azevedo
