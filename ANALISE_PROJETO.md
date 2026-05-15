# Análise Completa do Projeto Compilador Fortran 77 - PL-G56

**Data**: 12 de Maio de 2026  
**Status**: Etapa de Finalização e Valorização  
**Classificação Atual**: 7.8/10

---

## 1. O Que Falta Implementar

### 1.1 Funcionalidades Críticas (Especificação Principal)

#### 🔴 **Prioridade Crítica - Impacto Alto**

| Funcionalidade | Estado Atual | Razão | Esforço | Nota |
|---|---|---|---|---|
| **Funções Intrínsecas Completas** | Parcial | MOD funciona, mas faltam: ABS, MAX, MIN, INT, REAL, SQRT, SIN, COS, EXP, LOG, etc. | Médio | Essencial para os exemplos |
| **DIMENSION em Declarações** | ⚠️ Limitado | `INTEGER A(10)` declarado mas sem suporte completo a multi-dimensionais | Alto | Exemplo 7 falha totalmente |
| **PARAMETER (Constantes)** | ❌ Não | `PARAMETER PI = 3.14159` não reconhecido | Baixo | Necessário para compatibilidade |
| **FORMAT Statements** | ❌ Não | `WRITE(*, 100) X` com labels de formato | Alto | Apenas PRINT simples funciona |
| **Character String Operations** | ⚠️ Limitado | Concatenação com `//` não suportada | Médio | Exemplo 10 incompleto |

#### 🟡 **Prioridade Média - Impacto Médio**

| Funcionalidade | Estado Atual | Esforço | Nota |
|---|---|---|---|
| **COMMON Blocks** | ❌ | Alto | Comparticipação de memória entre subprogramas |
| **EQUIVALENCE** | ❌ | Médio | Sobreposição de variáveis |
| **IMPLICIT RULES** | ❌ | Médio | Variáveis I-N → INTEGER por padrão |
| **Double Precision / INTEGER*8** | ❌ | Baixo | Suporte a tipos estendidos |
| **SUBROUTINE com RETURN** | ⚠️ Parcial | Baixo | SUBROUTINE sem return value |

#### 🟢 **Nice-to-Have - Impacto Baixo**

- Recursão em funções (actualmente não testado)
- File I/O (OPEN, CLOSE, REWIND)
- GOTO forward jumps (apenas backward loops estão confirmados)
- Variáveis inicializadas em declaração (`INTEGER X / 5 /`)

---

### 1.2 Testes de Validação contra EWVM

O projeto gera código EWVM mas **sem validação contra a VM real**:

- ✅ Exemplos `.f` existem
- ✅ Ficheiros `.vm` de referência existem em `results/`
- ❌ **Sem comparação automática**: saída gerada vs. saída esperada
- ❌ **Sem execução da VM**: não se verifica se `.vm` gerado executa correctamente

**Impacto**: Impossível garantir que o compilador está funcional de verdade.

---

## 2. Melhorias e Extras a Fazer

### 2.1 Melhorias Funcionais

#### 🎯 **Mensagens de Erro com Localização**

**Estado Actual**:
```
SemanticError: Variable 'X' not declared
```

**Proposto**:
```
SemanticError: Variable 'X' not declared (linha 15, coluna 7)
  DO 10 X = 1, 10
         ^
```

**Implementação**: Rastrear `(line, col)` desde o lexer até ao parser e semântica.

#### 🎯 **Modo de Recolha de Múltiplos Erros**

**Actual**: Parser para no primeiro erro sintáctico.

**Proposto**: Modo `--lenient` que coleciona até N erros antes de abortar.

```python
# Em main.py
parser.error_recovery = args.lenient
errors = parser.parse(tokens, error_handler=collector)
```

#### 🎯 **Visualização da IR**

**Actual**: `ir_program.dump()` retorna lista linear de instruções.

**Proposto**: Visualização estruturada com blocos e edges de controlo:
```
[BLOCK_0: linha 5-10]
  ASSIGN temp1 = 5
  ASSIGN temp2 = 10
  IF_GOTO temp1 < temp2 → BLOCK_2
  GOTO BLOCK_1
[BLOCK_1: linha 20]
  WRITE temp1
  RETURN
[BLOCK_2: linha 15]
  ...
```

#### 🎯 **Diagnósticos de Optimização**

**Actual**: Apenas conta passes aplicados.

**Proposto**: Detalhe de transformações:
```
Optimization Report
==================
Pass 1: Constant Folding
  - Folded: 3 expressions → constants
  - Removed: 2 assignments to temp variables
Pass 2: Dead Code Elimination
  - Removed: 1 unreachable block
  ...
Reduction: 28 instruções → 22 instruções (21% ganho)
```

### 2.2 Melhorias de Suporte

#### 🎯 **Análise de Cobertura de Testes**

Criar relatório visual:
```
Lexer:        ████████████████████ 100%
Parser:       ████████████████████ 100%
Semantic:     ████████████████░░░░  80%
IR Codegen:   ████████░░░░░░░░░░░░  40%
VM Codegen:   ████████░░░░░░░░░░░░  35%
Optimizer:    ██████░░░░░░░░░░░░░░  30%
Integration:  ████░░░░░░░░░░░░░░░░  20%
```

#### 🎯 **Documentação de Limitações Conhecidas**

Ficheiro `docs/LIMITACOES.md` com:
- ❌ Não suportado
- ⚠️ Parcialmente suportado
- ✅ Suportado
- 📌 Comportamento não padrão

#### 🎯 **CI/CD Pipeline**

Ficheiro `.github/workflows/test.yml`:
```yaml
- Run lexer tests
- Run parser tests
- Run semantic tests
- Generate coverage report
- Test against examples (generate VM and compare)
- Check code quality (pylint, black)
```

---

## 3. Limpeza de Código Necessária

### 3.1 Problemas Identificados

#### ⚠️ **Cache Stale do Parser**

**Ficheiro**: `src/parser/parsetab.py`

**Problema**: Gerado automaticamente pelo PLY. Durante desenvolvimento, pode causar comportamentos inconsistentes se a gramática mudar.

**Solução**:
```makefile
clean-parser:
	rm -f src/parser/parsetab.py
	rm -f src/parser/parser.out
```

Executar antes de cada teste durante desenvolvimento.

#### ⚠️ **Logging Ausente**

**Estado**: Apenas em `main.py`, nenhum em módulos.

**Impacto**: Difícil debugar fases intermediárias.

**Solução**: Adicionar em cada módulo:
```python
import logging
logger = logging.getLogger(__name__)

# Em operações chave:
logger.debug(f"Processing statement: {node}")
logger.info(f"Generated {len(instructions)} IR instructions")
```

#### ⚠️ **Validação de Entrada Mínima**

**Problema**: `main.py` não verifica se ficheiro existe.

**Solução**:
```python
if not os.path.isfile(args.input):
    raise FileNotFoundError(f"Input file not found: {args.input}")
if os.path.getsize(args.input) == 0:
    raise ValueError("Input file is empty")
```

#### ⚠️ **Variáveis Globais em Módulos**

**Localização**: `src/config.py`

**Estado**: Bom uso de constantes, mas sem documentação de valores default.

**Solução**: Adicionar comments explicando cada constant.

#### ⚠️ **Exceções Não Específicas**

**Problema**: Alguns `except Exception` genéricos que deviam ser específicos.

**Proposto**: Usar `SemanticError`, `CodegenError`, etc.

---

### 3.2 Refactoring Recomendado

#### 📦 **Extrair Factory de Nós AST**

Centralizar criação de nós em `ast/factory.py`:
```python
class ASTFactory:
    @staticmethod
    def create_assignment(target, value):
        return AssignmentNode(target, value)
    
    @staticmethod
    def create_do_loop(label, var, start, end, body):
        # Validações centralizadas
        return DoLoopNode(...)
```

#### 📦 **Separar Validação de Construção**

Converter validações semânticas em duas fases:
1. **Construction**: Criar nós válidos sintaticamente
2. **Validation**: Aplicar regras semânticas

#### 📦 **Constants em Tipo Enum**

```python
from enum import Enum

class IROpcode(Enum):
    ADD = "ADD"
    SUB = "SUB"
    ...
```

---

## 4. Incoerências para Rever

### 4.1 Inconsistências Semânticas

#### 🔍 **Coerção de Tipos Ambígua**

**Problema**: INTEGER + REAL → REAL (esperado), mas REAL + LOGICAL não definido claramente.

**Verificação Necessária**:
```fortran
PROGRAM TEST
  REAL X
  LOGICAL L
  X = X + L  ! Erro ou conversão?
END
```

**Solução**: Documentar matriz de coerção explicitamente.

#### 🔍 **CONTINUE fora de DO Loop**

**Problema**: Validação não é robusta para ciclos aninhados.

**Teste**:
```fortran
DO 10 I = 1, 10
  DO 20 J = 1, 10
20 CONTINUE  ! Qual loop fecha?
10 CONTINUE
```

**Verificação**: Executar contra EWVM para confirmar comportamento.

#### 🔍 **GOTO para Labels em Diferentes Escopos**

**Problema**: Um GOTO pode saltar de/para função diferente?

```fortran
SUBROUTINE SUB1()
  GOTO 999  ! Salta para SUB2?
END

SUBROUTINE SUB2()
999 CONTINUE
END
```

**Status Actual**: Provavelmente não suportado, mas sem testes.

### 4.2 Inconsistências de Representação

#### 🔍 **Array vs. Escalar na AST**

**Problema**: Distinção entre `X` (escalar) e `X(10)` (array) pode não ser clara em todas as fases.

**Verificação Necessária**: Rastrear atributo `is_array` da declaração até ao uso.

#### 🔍 **Tipo de Função vs. SUBROUTINE**

**Problema**: Funções devem retornar valor, subroutines não. Validação incompleta?

**Teste**:
```fortran
SUBROUTINE SUB()
  RETURN 5  ! Erro?
END
```

---

## 5. Documentação em Falta

### 5.1 Documentação Técnica Ausente

#### 📝 **API Reference - Formato da IR**

**Ficheiro a Criar**: `docs/IR_FORMAT.md`

**Conteúdo**:
```markdown
# IR Format Specification

## IROpcode Reference

### Aritméticas
- ADD(dst, src1, src2): dst = src1 + src2
- SUB(dst, src1, src2): dst = src1 - src2
...

## IRInstruction Structure

```python
IRInstruction(
    opcode: IROpcode,
    operands: List[Operand],  # 0-3 operands
    result: Optional[Operand],
    line: int,  # Localização no source
    metadata: Dict  # Informação auxiliar
)
```

## Example Traces

Input Fortran:
```fortran
X = 5 + Y * 2
```

Generated IR:
```
ASSIGN temp1 = 2
MUL temp2 = Y, temp1
ADD temp3 = 5, temp2
ASSIGN X = temp3
```
```

#### 📝 **Guia de Debugging**

**Ficheiro a Criar**: `docs/DEBUG_GUIDE.md`

**Conteúdo**:
- Flags de logging por nível (`--debug`, `--verbose`)
- Exemplo: Analisar porque um programa falha na semântica
- Comando: `python -m src.main --input test.f --dump-ast --dump-ir`

#### 📝 **Lista de Limitações Conhecidas**

**Ficheiro a Criar**: `docs/LIMITACOES.md`

```markdown
# Limitações Conhecidas

## ✅ Totalmente Suportado
- Declarações INTEGER, REAL, LOGICAL
- IF/THEN/ELSE/ENDIF
- DO loops com labels
- Arrays uni e bidimensionais
- FUNCTION e SUBROUTINE simples
- Operadores aritméticos e lógicos

## ⚠️ Parcialmente Suportado
- DIMENSION: declarado mas validação incompleta
- Funções intrínsecas: MOD funciona, faltam ABS, SQRT, etc.
- Character strings: sem concatenação com //
- Format statements: parcialmente suportado

## ❌ Não Suportado
- COMMON blocks
- EQUIVALENCE
- File I/O (OPEN, CLOSE)
- PARAMETER constants
- Implicit type rules (I-N auto-integer)
- GOTO forward jumps (apenas backward loops)

## 📌 Comportamento Não-Padrão
- [Lista de desvios de Fortran 77 standard]
```

#### 📝 **Troubleshooting Guide**

**Ficheiro a Criar**: `docs/TROUBLESHOOTING.md`

```markdown
# Troubleshooting Guide

## Erro: "Variable X not declared"

Causas comuns:
1. Tipo de dados não declarado (falta INTEGER X)
2. Nome com typo (Xmj vs Xnij)
3. Declaração em escopo diferente

Solução:
```python
python -m src.main --input test.f --dump-symbols
```

Verá todas as variáveis em cada escopo.

## Erro: "Type mismatch in assignment"

...
```

---

### 5.2 Documentação de Código em Falta

#### 📝 **Docstrings Ausentes/Incompletas**

**Ficheiros a Verificar e Completar**:

| Ficheiro | Módulo | Prioridade |
|----------|--------|-----------|
| `src/codegen/ir_generator.py` | IRGenerator class | Alta |
| `src/codegen/vm_codegen.py` | VMCodegen class | Alta |
| `src/optimizer/optimizer.py` | Optimizer class | Média |
| `src/semantic/type_checker.py` | TypeChecker class | Média |

**Formato Esperado**:
```python
class IRGenerator(Visitor):
    """Converts AST to Three-Address Code (TAC).
    
    This visitor transforms an Abstract Syntax Tree into an intermediate
    representation consisting of linear three-address instructions, enabling
    independent optimization and code generation.
    
    Attributes:
        ir_program (IRProgram): Container for generated instructions
        symbol_table (SymbolTable): Context for variable resolution
        temp_counter (int): Counter for temporary variable generation
        
    Example:
        >>> ast = parser.parse(tokens)
        >>> gen = IRGenerator(symbol_table)
        >>> ir_program = gen.visit(ast)
        >>> print(ir_program.dump())
    """
```

---

## 6. Testes em Falta

### 6.1 Cobertura de Testes Incompleta

#### ❌ **Testes de IR Codegen (Quantificação)**

**Estado Atual**: Ficheiro `tests/test_ir_codegen.py` existe mas intensidade desconhecida.

**Testes a Adicionar**:
```python
def test_ir_constant_folding():
    """Verifica se 5 + 3 é reduzido a 8"""
    
def test_ir_array_indexing():
    """Gera IR correcto para A(3, 5)"""
    
def test_ir_function_call():
    """Gera CALL, PARAM, RETURN correctamente"""
```

#### ❌ **Testes de VM Codegen (Quantificação)**

**Estado Atual**: Ficheiro `tests/test_vm_codegen.py` existe mas sem verificação de completude.

**Testes a Adicionar**:
```python
def test_vm_memory_allocation():
    """Aloca endereços correctos para variáveis"""
    
def test_vm_arrays_multidimensional():
    """Calcula índices correctamente para arrays 2D"""
```

#### ❌ **Testes de Edge Cases (Semântica)**

**Casos Não Cobertos**:

| Caso | Teste | Esperado |
|------|-------|----------|
| Variável nunca usada | `INTEGER X` sem assignment | Aviso? |
| Division by zero | `X = 5 / 0` | Detecção estática? |
| Array out of bounds | `A(100)` mas declarado A(10) | Erro? |
| Recursive function | `FUNCTION F() CALL F()` | Erro? |
| Implicit declaration | Variável usada sem declarar | Erro padrão |

#### ❌ **Testes de Recuperação de Erros**

**Situações a Testar**:
```python
def test_parse_error_recovery():
    """Parser colecciona múltiplos erros com --lenient"""
    
def test_missing_variable_declaration():
    """Semântica detecta 2 variáveis não declaradas, não 1"""
```

#### ❌ **Testes de Integração Contra Exemplos**

**Estado Atual**: 9 exemplos existem, mas sem validação automática.

**Proposto**: Target make novo:
```makefile
test-examples: compile-examples compare-vm
	@for f in tests/examples/*.f; do \
		echo "Testing $$f..."; \
		python -m src.main $$f -o /tmp/$$(basename $$f .f).vm; \
		diff /tmp/$$(basename $$f .f).vm results/$$(basename $$f .f).vm; \
	done
```

#### ❌ **Testes de Performance**

**Proposto**:
```python
def test_optimizer_performance():
    """1000 de instruções → < 100ms"""
    big_ir = generate_large_program(1000)
    start = time.time()
    optimized = optimizer.optimize(big_ir)
    assert time.time() - start < 0.1
```

### 6.2 Testes de Validação Contra EWVM

#### 🔴 **Crítico: Sem Execução da VM**

**Problema**: Gera `.vm` mas não executa.

**Solução Proposta**: Integração com executável EWVM (se disponível):

```python
def test_hello_world_execution():
    """Gera e executa exemplo1_hello.f"""
    vm_code = compile_fortran("tests/examples/exemplo1_hello.f")
    output = run_ewvm(vm_code)
    assert output.strip() == "Ola, Mundo!"

def test_fatorial_execution():
    """Gera e executa exemplo2_fatorial.f com input 5"""
    vm_code = compile_fortran("tests/examples/exemplo2_fatorial.f")
    output = run_ewvm(vm_code, input="5\n")
    assert "120" in output
```

**Dependência**: Executável `ewvm` disponível ou simulador.

---

## 7. Próximos Passos para Finalização

### 7.1 Plano de Ação Ordenado (Semanas antes de 17/05)

#### **Fase 1: Validação Funcional (2-3 dias)**

1. ✅ Verificar cobertura real de `test_ir_codegen.py` e `test_vm_codegen.py`
   ```bash
   python -m pytest tests/test_ir_codegen.py -v --cov --cov-report=html
   python -m pytest tests/test_vm_codegen.py -v --cov --cov-report=html
   ```

2. ✅ Testar manualmente cada exemplo contra EWVM
   - Se `.vm` gerados executam correctamente
   - Se saída corresponde ao esperado

3. ✅ Criar issue tracker com bugs encontrados

#### **Fase 2: Correcções Críticas (3-5 dias)**

1. 🔴 **Funções Intrínsecas** (ABS, MAX, MIN, SQRT, SIN, COS)
   - Análise: 2h
   - Implementação: 4h
   - Testes: 2h

2. 🔴 **DIMENSION Multidimensional** (se falhar Exemplo 7)
   - Análise: 1h
   - Implementação: 3h
   - Testes: 1h

3. 🔴 **CHARACTER String Operations**
   - Concatenação com `//`: 2h
   - Substrings `A(1:5)`: 3h

4. 🟡 **Mensagens de Erro com Linha/Coluna**
   - Refactor lexer para rastrear `(line, col)`: 3h

#### **Fase 3: Melhorias de Suporte (2-3 dias)**

1. 📝 Criar `docs/IR_FORMAT.md` com exemplos
2. 📝 Criar `docs/DEBUG_GUIDE.md`
3. 📝 Criar `docs/LIMITACOES.md` com matriz completa
4. 📝 Completar docstrings em módulos principais
5. ⚙️ Adicionar CI/CD `.github/workflows/test.yml`

#### **Fase 4: Testes Finais (2 dias)**

1. ✅ Executar `make test-coverage` e garantir 80%+ em fases principais
2. ✅ Executar `make test-examples` contra todos os 9 exemplos
3. ✅ Testar cada um dos exemplos manualmente contra EWVM
4. ✅ Verificar mensagens de erro são informativos

#### **Fase 5: Relatório (2-3 dias)**

1. 📋 Ver Secção 8 abaixo

---

### 7.2 Checkpoint Críticos Antes de Entregar

- [ ] Todos os 9 exemplos compilam sem erro
- [ ] Testes passam: `make test-coverage` com >80%
- [ ] VM code gerado é válido (pode executar em EWVM)
- [ ] Sem warnings de pylint (ou documentados)
- [ ] Relatório completo em LaTeX com > 5 páginas

---

## 8. Tópicos de Relatório Necessários Desenvolver

### 8.1 Estrutura Sugerida do Relatório (10 páginas máx)

#### **Página 1-2: Introdução e Objectivos**

**Tópicos**:
- Contexto: compilador Fortran 77 standard
- Objectivos do projeto (4 fases + otimização)
- Escolha de formato: Fixed vs. Free
- Ferramentas: PLY, Python 3.x

**Texto Sugerido** (excerpt):
> O presente projeto implementa um compilador para a linguagem Fortran 77 (ANSI X3.9-1978), seguindo a especificação fornecida em [referência]. O compilador processa código Fortran através de cinco etapas: análise léxica, análise sintática, análise semântica, geração de código intermediário e otimização. O grupo optou pelo formato **[fixed/free]** de forma a [justificação]. A implementação utiliza a biblioteca PLY (Python Lex-Yacc) para construção de lexer e parser, garantindo compatibilidade com ferramentas standards de processamento de linguagens.

---

#### **Página 2-3: Arquitectura e Desenho**

**Tópicos**:
- Diagrama de fases (Lexer → Parser → AST → Semantic → IR → Optimizer → VMCodegen)
- Padrão Visitor para travessia de AST
- Estrutura de dados principais (AST nodes, IR instructions, Symbol Table)
- Fluxo de controlo geral

**Visualizações**:
```
Input (.f)
    ↓
[LEXER] → Tokens
    ↓
[PARSER] → AST
    ↓
[SEMANTIC] → AST validada + Symbol Table
    ↓
[IR GENERATOR] → TAC (Three-Address Code)
    ↓
[OPTIMIZER] → IR otimizado (8 passes)
    ↓
[VM CODEGEN] → EWVM Assembly
    ↓
Output (.vm)
```

**Documentar a escolha**:
- Padrão Visitor justificado
- IR em TAC (vs. bytecode, vs. DAG)
- 8 passes de optimização e sua ordem

---

#### **Página 3-4: Gramática e Linguagem Suportada**

**Tópicos**:
- Gramática BNF da linguagem aceita (subset de Fortran 77)
- Tipos de dados suportados (INTEGER, REAL, LOGICAL, CHARACTER)
- Construções de controlo (IF/THEN/ELSE, DO loops, GOTO)
- Subprogramas (FUNCTION, SUBROUTINE)
- I/O (READ, PRINT, WRITE básico)

**Exemplo BNF** (simplificado):
```
<program> ::= PROGRAM <ident> <declarations> <statements> END
<declarations> ::= <declaration> | <declarations> <declaration> | ε
<declaration> ::= <type> <var_list>
<type> ::= INTEGER | REAL | LOGICAL | CHARACTER
...
```

**Mencionar**:
- O que é suportado completamente
- O que é suportado parcialmente (DIMENSION, FORMAT)
- O que não é suportado (COMMON, EQUIVALENCE)

---

#### **Página 4-5: Decisões de Implementação**

**Tópicos**:
- Por que PLY? (vs. ANTLR, vs. hand-written)
- Por que Python? (rapidez de desenvolvimento, prototipagem)
- Escolha de formato fixed vs. free
- Representação da IR (TAC vs. alternativas)
- Estratégia de otimização (8 passes independentes)

**Secção de Reflexão** (Importante para defesa):
> Durante o desenvolvimento, considerámos duas abordagens para a IR: uma baseada em Three-Address Code linear, e outra em Control-Flow Graphs (CFG). Optámos por TAC porque [razão]. Posteriormente, durante a implementação do optimizador, verificámos que [aprendizado]. Para futuros trabalhos, uma abordagem baseada em CFG seria mais apropriada para otimizações globais.

---

#### **Página 5-6: Análise Semântica e Otimização**

**Tópicos**:
- Verificação de tipos (compatibilidade, coerção automática)
- Validação de escopos (variáveis globais vs. locais)
- Validação de labels (DO/GOTO)
- 8 passes de optimização (com exemplos de cada)

**Exemplo de Optimização**:
```fortran
Input:
  X = 5 * 3
  Y = X + 1

IR Initial:
  ASSIGN temp1 = 5
  ASSIGN temp2 = 3
  MUL temp3 = temp1, temp2
  ASSIGN X = temp3
  ASSIGN temp4 = X
  ASSIGN temp5 = 1
  ADD temp6 = temp4, temp5
  ASSIGN Y = temp6

IR After Constant Folding:
  ASSIGN X = 15
  ASSIGN temp4 = X
  ASSIGN temp5 = 1
  ADD temp6 = temp4, temp5
  ASSIGN Y = temp6

IR After Constant Propagation:
  ASSIGN X = 15
  ASSIGN temp5 = 1
  ADD temp6 = 15, temp5
  ASSIGN Y = temp6

IR After Algebraic Simplification + Final:
  ASSIGN X = 15
  ASSIGN Y = 16
```

---

#### **Página 6-7: Dificuldades Encontradas e Soluções**

**Tópicos** (Adaptar conforme experiência do grupo):
- Problema 1: [Descrever]
  - Impacto: [Crítico/Médio/Baixo]
  - Solução: [Como foi resolvido]
  - Lição: [O que aprendemos]

**Exemplos típicos**:
- "Problema: Parser não diferenciava entre `DO 10 I = 1, 10` e `DO I = 1, 10`"
  - Solução: Refactor gramática para tornar label obrigatório
  
- "Problema: Recursão infinita em optimizador quando variáveis circulares"
  - Solução: Adicionar limite de passes (max 10) + fix-point detection

- "Problema: Verificação de tipos muito permissiva (LOGICAL + INTEGER)"
  - Solução: Matriz de coerção explícita + erros em combinações inválidas

---

#### **Página 7-8: Resultados e Validação**

**Tópicos**:
- Exemplos de programa compilados com sucesso
- Estatísticas de teste (% cobertura, # de testes)
- Comparação IR before/after optimização
- Qualidade do código EWVM gerado

**Tabelas/Gráficos**:
```
| Exemplo | Linhas Fortran | IR Instructions | IR After Opt | Reduction |
|---------|---|---|---|---|
| hello.f | 3 | 5 | 4 | 20% |
| fatorial.f | 8 | 18 | 12 | 33% |
| primo.f | 12 | 35 | 28 | 20% |
```

---

#### **Página 8-9: Limitações e Trabalho Futuro**

**Tópicos**:
- Funcionalidades não suportadas (COMMON, EQUIVALENCE, etc.)
- Comportamentos não-padrão
- Potenciais melhorias (control-flow graphs, better type system)
- Escalabilidade

**Exemplo**:
> **Limitações Conhecidas**:
> 1. Não suportamos COMMON blocks para compartilhação de memória entre subprogramas
> 2. DIMENSION com inicialização em declaração (ex: `INTEGER A(10) / 0 /`) não é reconhecido
> 3. FORMAT statements aceitam apenas identidade (formato literal)
> 
> **Potenciais Melhorias**:
> 1. Implementação de CFG para otimizações mais agressivas
> 2. Suporte a tipos DOUBLE PRECISION e INTEGER*8
> 3. Análise de liveness mais sofisticada para register allocation (se VM tivesse registadores)

---

#### **Página 9-10: Conclusão e Instruções de Utilização**

**Tópicos**:
- Resumo do que foi alcançado
- Instruções de instalação e utilização
- Como estender/modificar o compilador
- Referências

**Instruções de Utilização**:
```
Instalação:
$ python -m pip install -r requirements.txt

Compilação:
$ python -m src.main input.f -o output.vm
$ python -m src.main input.f -o output.vm --dump-ir  # Ver IR
$ python -m src.main input.f -o output.vm --dump-ast # Ver AST

Testes:
$ make test              # Todos
$ make test-lexer        # Específico
$ make test-coverage     # Com cobertura

Extensão:
1. Adicionar nó à AST em src/ast/nodes.py
2. Adicionar regra de parsing em src/parser/grammar.py
3. Adicionar método visit_* em visitantes (semantic, codegen, etc.)
```

---

### 8.2 Sugestões de Conteúdo por Tópico

#### **Análise Léxica**

**O que documentar**:
- Formato fixed vs. free (decisão tomada)
- Tratamento de continuações de linha
- Tabela de keywords reconhecidas
- Exemplos de tokenização

#### **Análise Sintática**

**O que documentar**:
- Gramática BNF (ou simplificada)
- Resolução de precedência de operadores
- Tratamento de ambiguidades
- Exemplos de parse trees

#### **Análise Semântica**

**O que documentar**:
- Algoritmo de construção da tabela de símbolos
- Regras de coerção de tipos (tabela)
- Validações específicas (labels, escopos)
- Exemplos de erros semânticos detectados

#### **Geração de IR**

**O que documentar**:
- Justificação da escolha de TAC vs. alternativas
- Algoritmo de tradução AST → TAC
- Exemplo completo de programa Fortran → IR
- Tratamento de controlo de fluxo

#### **Optimização**

**O que documentar**:
- Descrição de cada um dos 8 passes
- Ordem das passes e justificação
- Exemplos antes/depois de cada passa
- Complexidade aproximada de cada passa

#### **Geração de Código VM**

**O que documentar**:
- Esquema de alocação de memória (static vs. dynamic)
- Mapeamento de IR → EWVM
- Exemplo de programa otimizado → VM code
- Estratégia de gestão de pilha (se aplicável)

---

### 8.3 Estrutura de Ficheiros do Relatório

```
relatorio.tex
├── \section{Introdução}
│   ├── Motivação
│   └── Objectivos
├── \section{Especificação da Linguagem}
│   ├── Gramática BNF
│   └── Construções Suportadas
├── \section{Arquitectura e Desenho}
│   ├── Diagrama de Fases
│   ├── Padrões de Desenho
│   └── Estruturas de Dados Principais
├── \section{Implementação Detalhada}
│   ├── Análise Léxica
│   ├── Análise Sintática
│   ├── Análise Semântica
│   ├── Geração de IR
│   ├── Optimização
│   └── Geração de Código VM
├── \section{Dificuldades e Soluções}
├── \section{Resultados e Validação}
├── \section{Limitações e Trabalho Futuro}
└── \section{Conclusão}
```

---

## 9. Resumo Executivo

### 9.1 Estado Atual do Projeto

| Aspecto | Status | Nota |
|---------|--------|------|
| **Etapa 1: Análise Léxica** | ✅ Completa | 2.0/2.0 |
| **Etapa 2: Análise Sintática** | ✅ Completa | 2.0/2.0 |
| **Etapa 3: Análise Semântica** | ✅ Completa | 2.0/2.0 |
| **Etapa 4: Tradução de Código** | ✅ Completa | 2.0/2.0 |
| **Valorização: Otimização** | ✅ Completa | 2.0/2.0 |
| **Testes** | ⚠️ 70% | 1.4/2.0 |
| **Documentação** | ⚠️ 80% | 1.6/2.0 |
| **Defesa** | ⏳ A preparar | ? |
| **TOTAL (Estimado)** | | **13.0-15.0/20** |

### 9.2 Tarefas Críticas até 17/05

**Prioritário (Semanal)**:
1. ✅ Validar todos os 9 exemplos compilam sem erro
2. ✅ Garantir 80%+ cobertura de testes
3. 📝 Completar relatório com secções 8.1-8.3
4. 🐛 Corrigir bugs encontrados em validação

**Secundário (Se houver tempo)**:
1. 🟡 Adicionar funções intrínsecas (ABS, SQRT, etc.)
2. 🟡 Melhorar mensagens de erro com linha/coluna
3. 📝 Criar documentação de debugging e limitações

### 9.3 Checklist Pré-Entrega

- [ ] Código compila sem warnings (excepto deprecações PLY)
- [ ] `make test` passa 100%
- [ ] `make test-coverage` mostra ≥80% nas fases críticas
- [ ] Todos os 9 exemplos testados e funcionais
- [ ] Relatório tem 5-10 páginas, cobre tópicos 8.1-8.3
- [ ] README actualizado com instruções claras
- [ ] Sem ficheiros temporários ou caches (`parsetab.py`, `__pycache__`)
- [ ] Commit final com mensagem descritiva antes de 23:59 de 17/05

---

## 10. Documentação Adicional Recomendada

### Ficheiros a Criar

```
docs/
├── IR_FORMAT.md          ← Especificação completa da IR
├── DEBUG_GUIDE.md        ← Como debugar o compilador
├── LIMITACOES.md         ← Matriz de funcionalidades
├── TROUBLESHOOTING.md    ← Problemas e soluções comuns
└── EXEMPLOS.md           ← Exemplos comentados de cada construção
```

### Actualizar

```
README.md
├── Expandir secção de "Exemplos de Uso" com mais flags
└── Adicionar secção de "Troubleshooting"

relatorio.tex
├── Aplicar secções de 8.1-8.3 acima
└── Adicionar imagens/diagramas de fases
```

---

**Documento Preparado**: 12 de Maio de 2026  
**Próxima Revisão**: 15 de Maio de 2026 (pré-defesa)  
**Data de Entrega**: 17 de Maio de 2026 (23:59)
