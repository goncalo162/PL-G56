.PHONY: help test-all test-coverage clean clean-all install lint setup venv test-% test-%-verbose test-%-summary test-%-quick

help:
	@echo "Targets disponíveis:"
	@echo ""
	@echo "  make setup            - Cria venv e instala dependências"
	@echo "  make test-all         - Executa todos os testes da pasta tests"
	@echo "  make test-x           - Executa tests/test_x.py (ex: test-parser, test-lexer, ...)"
	@echo "  make test-x-verbose   - Executa tests/test_x.py com saída detalhada"
	@echo "  make test-x-summary   - Executa tests/test_x.py com resumo"
	@echo "  make test-x-quick     - Executa tests/test_x.py em modo rápido"
	@echo "  make test-coverage    - Gera relatório de cobertura"
	@echo "  make install          - Instala dependências (venv ativo)"
	@echo "  make venv             - Cria ambiente virtual"
	@echo "  make lint             - Verifica código com linter"
	@echo "  make clean            - Remove ficheiros de cache"
	@echo "  make clean-all        - Limpeza completa"


test-all:
	@echo "Executando suite completa de testes..."
	python3 -m pytest tests/ -v --tb=short

# Targets dinâmicos para ficheiros de teste individuais
test-verbose-%:
	python3 -m pytest tests/test_$*.py -vv --tb=long -s

test-summary-%:
	python3 -m pytest tests/test_$*.py -v --tb=line

test-quick-%:
	python3 -m pytest tests/test_$*.py -q

test-%:
	python3 -m pytest tests/test_$*.py -v --tb=short

test-coverage:
	coverage run -m pytest tests/test_lexer.py || true
	coverage report -m || true
	coverage html || true
	@echo "Relatório HTML gerado em htmlcov/index.html"

venv:
	python3 -m venv venv
	@echo "Ambiente virtual criado! Ative com: source venv/bin/activate"


install:
	. venv/bin/activate && pip install -r requirements.txt

setup: venv install
	@echo "Ambiente pronto! Ative o ambiente virtual com: source venv/bin/activate"

lint:
	flake8 src/ tests/ --max-line-length=120

clean:
	rm -rf **/__pycache__ **/*.pyc **/.pytest_cache **/.egg-info tests/lextab.py tests/parser.out

clean-all: clean
	rm -rf htmlcov/ .coverage coverage*.xml dist/ build/ docs/html/


