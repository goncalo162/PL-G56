# Projeto de Processamento de Linguagens - Grupo 56

Compilador para um subconjunto de **Fortran 77** desenvolvido no âmbito da unidade curricular de Processamento de Linguagens. O projeto implementa as fases principais de compilação, desde a análise léxica até à geração de código para a máquina virtual **EWVM**.

O compilador cobre as seguintes fases:

1. **Pre-processamento** de linhas em formato fixo, labels e continuação de linhas.
2. **Análise léxica** com PLY, incluindo keywords, identificadores, literais, operadores, arrays e labels.
3. **Análise sintática** com construção de AST.
4. **Análise semântica** com tabela de símbolos, validação de tipos, scopes e labels.
5. **Geração de código intermédio** em IR/TAC.
6. **Otimização opcional** da IR.
7. **Geração de código VM** compatível com a EWVM.


## Instalação

Criar o ambiente virtual e instalar as dependências:

```bash
make setup
source venv/bin/activate
```

Também é possível instalar manualmente:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilização

Compilar um programa Fortran:

```bash
python -m src.main tests/examples/exemplo1_hello.f
```

Ou através do `Makefile`:

```bash
make compile tests/examples/exemplo1_hello.f
```

O compilador imprime a IR e o código VM gerado. Quando executado por `src.main`, o resultado VM é também guardado em:

```text
results/<nome_do_ficheiro>.vm
```

## Exemplos

Os exemplos de entrada estão em `tests/examples/`, incluindo:

- `exemplo1_hello.f`
- `exemplo2_fatorial.f`
- `exemplo3_primo.f`
- `exemplo4_soma_lista.f`
- `exemplo5_conversor_bases.f`


Os testes end-to-end exportam código VM para `tests/examples/generated_vm/` e mantêm um manifesto de resultados esperados em `expected_vm_results.txt` para validação manual na EWVM.

## Testes

Executar a suite completa:

```bash
make test-all
```

Executar uma fase específica:

```bash
make test-lexer
make test-parser
make test-semantic
make test-ir_codegen
make test-vm_codegen
make test-optimizer
make test-compiler
```

Outras variantes úteis:

```bash
make test-verbose-parser
make test-summary-semantic
make test-quick-vm_codegen
make test-coverage
```

## Qualidade e Documentação

Verificar estilo:

```bash
make lint
```

Gerar documentação HTML:

```bash
make docs
```

Limpar ficheiros temporários:

```bash
make clean
make clean-all
```

Documentação adicional:

- [Arquitetura](docs/arquitetura.md)
- [Estrutura](docs/ESTRUTURA.md)
- [Gramática](docs/grammar.md)
- [Decisões de Design](docs/design_decisions.md)
- [EWVM](docs/VM.md)

## Dependências

- `ply`
- `pytest`
- `pytest-cov`
- `coverage`
- `flake8`
- `pdoc`

## Referências

- Standard Fortran 77: ANSI X3.9-1978
- EWVM: https://ewvm.epl.di.uminho.pt/

## Alunos

- A106804 - Alice Soares
- A106914 - Gonçalo Martins
- A107367 - João Azevedo