"""
Testes para Geração de Código
=============================
"""

import unittest
from src.codegen.ir_generator import CodeGenerator
from src.codegen.ir import IRProgram, IRInstruction, IROpcode
from src.codegen.vm_codegen import VMCodeGenerator
from src.optimizer.optimizer import IROptimizer


class TestIRGenerator(unittest.TestCase):
    """Testes do gerador de IR."""
    
    def setUp(self):
        self.codegen = CodeGenerator()
    
    def test_generate_ir_simple(self):
        """Testa geração de IR simples."""
        # Será testado quando AST estiver pronto
        pass


class TestVMCodeGenerator(unittest.TestCase):
    """Testes do gerador de código VM."""
    
    def setUp(self):
        self.vmgen = VMCodeGenerator()
    
    def test_generate_vm_code(self):
        """Testa geração de código VM."""
        # Criar programa IR simples
        ir_program = IRProgram(name="TEST")
        ir_program.variables = {'X': {'type': 'INTEGER'}, 'Y': {'type': 'REAL'}}
        ir_program.add_instruction(
            IRInstruction(opcode=IROpcode.ASSIGN, result='X', arg1='5')
        )
        ir_program.add_instruction(
            IRInstruction(opcode=IROpcode.ADD, result='Y', arg1='X', arg2='3')
        )
        
        # Gerar código VM
        vm_code = self.vmgen.generate_vm_code(ir_program)
        self.assertIsNotNone(vm_code)
        self.assertIn("MOV", vm_code)  # MOV é o equivalente de ASSIGN


class TestIROptimizer(unittest.TestCase):
    """Testes do otimizador de IR."""
    
    def setUp(self):
        self.optimizer = IROptimizer()
    
    def test_constant_propagation(self):
        """Testa propagação de constantes."""
        ir_program = IRProgram(name="TEST")
        ir_program.variables = {'X': {'type': 'INTEGER'}}
        ir_program.add_instruction(
            IRInstruction(opcode=IROpcode.ASSIGN, result='X', arg1='5')
        )
        ir_program.add_instruction(
            IRInstruction(opcode=IROpcode.ADD, result='Y', arg1='X', arg2='3')
        )
        
        # Aplicar otimização
        optimized = self.optimizer.optimize(ir_program)
        self.assertIsNotNone(optimized)
    
    def test_dead_code_elimination(self):
        """Testa eliminação de código morto."""
        ir_program = IRProgram(name="TEST")
        ir_program.variables = {'X': {'type': 'INTEGER'}}
        ir_program.add_instruction(
            IRInstruction(opcode=IROpcode.ASSIGN, result='X', arg1='5')
        )
        ir_program.add_instruction(
            IRInstruction(opcode=IROpcode.ASSIGN, result='UNUSED', arg1='10')
        )
        
        # Aplicar otimização
        optimized = self.optimizer.optimize(ir_program)
        self.assertIsNotNone(optimized)


if __name__ == "__main__":
    unittest.main()
