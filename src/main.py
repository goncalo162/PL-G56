"""
Compilador Principal
====================

Orquestra as fases do compilador: lexer → parser → análise semântica →
geração de código → otimização.
"""

import logging
from typing import Optional

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.codegen.ir_generator import CodeGenerator
from src.codegen.vm_codegen import VMCodeGenerator
from src.optimizer.optimizer import IROptimizer
from src.exceptions import CompilerError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FortranCompiler:
    """
    Compilador Fortran 77.
    
    Orquestra todas as fases da compilação.
    """
    
    def __init__(self, enable_optimizations=True):
        self.lexer = Lexer()
        self.parser = Parser()
        self.semantic_analyzer = SemanticAnalyzer()
        self.ir_generator = CodeGenerator()
        self.optimizer = IROptimizer()
        self.vm_codegen = VMCodeGenerator()
        self.enable_optimizations = enable_optimizations
    
    def compile(self, source_code: str) -> Optional[str]:
        """
        Compila código-fonte Fortran.
        
        Args:
            source_code: String contendo o código Fortran
            
        Returns:
            String contendo código da máquina virtual ou None se erro
        """
        try:
            logger.info("Iniciando compilação...")
            
            # 1. Análise Léxica
            logger.info("Fase 1: Análise Léxica")
            tokens = self.lexer.tokenize(source_code)
            logger.info(f"Tokens gerados: {len(tokens)}")
            
            # 2. Análise Sintática
            logger.info("Fase 2: Análise Sintática")
            ast = self.parser.parse(tokens)
            logger.info("AST construída")
            
            # 3. Análise Semântica
            logger.info("Fase 3: Análise Semântica")
            if not self.semantic_analyzer.analyze(ast):
                raise CompilerError("Erros semânticos detectados")
            logger.info("Análise semântica OK")
            
            # 4. Geração de IR (Intermediate Representation)
            logger.info("Fase 4: Geração de Código Intermédio (IR)")
            ir_program = self.ir_generator.generate_code(ast)
            logger.info("IR gerado")
            
            # 5. Otimização (Valorização)
            if self.enable_optimizations:
                logger.info("Fase 5: Otimização de Código (!valorização!)")
                ir_program = self.optimizer.optimize(ir_program)
                logger.info(f"Otimizações aplicadas: {', '.join(self.optimizer.optimizations_applied)}")
            
            # 6. Geração de Código Máquina (VM)
            logger.info("Fase 6: Geração de Código VM")
            vm_code = self.vm_codegen.generate_vm_code(ir_program)
            logger.info("Código intermédio convertido para VM")
            
            logger.info("Compilação concluída com sucesso!")
            return vm_code
            
        except CompilerError as e:
            logger.error(f"Erro de compilação: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None


def main():
    """Ponto de entrada do compilador."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python -m src.main <arquivo.f>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
        
        compiler = FortranCompiler()
        output = compiler.compile(source_code)
        
        if output:
            print(output)
            sys.exit(0)
        else:
            sys.exit(1)
    
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado")
        sys.exit(1)


if __name__ == "__main__":
    main()
