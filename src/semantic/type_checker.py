"""
Verificação de Tipos
====================

Implementa regras de compatibilidade de tipos e coerção automática.
"""

from src.exceptions import SemanticError


class TypeChecker:
    """
    Verifica compatibilidade de tipos em expressões e atribuições.
    
    Regras de compatibilidade Fortran 77:
    - INTEGER pode ser usado onde REAL é esperado (coerção automática)
    - REAL pode ser usado onde COMPLEX é esperado
    - Operações entre tipos diferentes resultam no tipo "maior"
    """
    
    TYPE_HIERARCHY = {
        'LOGICAL': 0,
        'INTEGER': 1,
        'REAL': 2,
        'COMPLEX': 3,
        'CHARACTER': 4,
    }
    
    @staticmethod
    def is_numeric(type_name: str) -> bool:
        """Verifica se tipo é numérico."""
        return type_name in ['INTEGER', 'REAL', 'COMPLEX']
    
    @staticmethod
    def is_logical(type_name: str) -> bool:
        """Verifica se tipo é lógico."""
        return type_name == 'LOGICAL'
    
    @staticmethod
    def is_character(type_name: str) -> bool:
        """Verifica se tipo é caractere."""
        return type_name == 'CHARACTER'
    
    @staticmethod
    def can_coerce(from_type: str, to_type: str) -> bool:
        """
        Verifica se as possível coerção de tipo.
        
        Args:
            from_type: Tipo de origem
            to_type: Tipo de destino
            
        Returns:
            True se coerção é possível
        """
        if from_type == to_type:
            return True
        
        # INTEGER pode ser coagido para REAL ou COMPLEX
        if from_type == 'INTEGER' and to_type in ['REAL', 'COMPLEX']:
            return True
        
        # REAL pode ser coagido para COMPLEX
        if from_type == 'REAL' and to_type == 'COMPLEX':
            return True
        
        return False
    
    @staticmethod
    def get_result_type(left_type: str, right_type: str, operator: str) -> str:
        """
        Determinao tipo resultado de uma operação binária.
        
        Args:
            left_type: Tipo do operando esquerdo
            right_type: Tipo do operando direito
            operator: Operador (+, -, *, /, etc)
            
        Returns:
            Tipo resultado
            
        Raises:
            SemanticError: Se operação é inválida para tipos
        """
        # Operadores lógicos retornam LOGICAL
        if operator in ['.AND.', '.OR.', '.NOT.']:
            if TypeChecker.is_logical(left_type) and TypeChecker.is_logical(right_type):
                return 'LOGICAL'
            raise SemanticError(f"Operador {operator} requer tipos LOGICAL")
        
        # Operadores relacionais retornam LOGICAL
        if operator in ['.LT.', '.LE.', '.GT.', '.GE.', '.EQ.', '.NE.']:
            if TypeChecker.is_numeric(left_type) and TypeChecker.is_numeric(right_type):
                return 'LOGICAL'
            raise SemanticError(f"Operador {operator} requer tipos numéricos")
        
        # Operadores aritméticos
        if operator in ['+', '-', '*', '/', '**']:
            if not (TypeChecker.is_numeric(left_type) and TypeChecker.is_numeric(right_type)):
                raise SemanticError(f"Operador {operator} requer tipos numéricos")
            
            # Tipo resultado é o "maior" dos dois
            left_rank = TypeChecker.TYPE_HIERARCHY.get(left_type, 0)
            right_rank = TypeChecker.TYPE_HIERARCHY.get(right_type, 0)
            
            if left_rank >= right_rank:
                return left_type
            else:
                return right_type
        
        raise SemanticError(f"Operador desconhecido: {operator}")
    
    @staticmethod
    def verify_assignment(source_type: str, target_type: str) -> bool:
        """
        Verifica se atribuição é válida.
        
        Args:
            source_type: Tipo do valor a atribuir
            target_type: Tipo da variável destino
            
        Returns:
            True se atribuição é válida
            
        Raises:
            SemanticError: Se atribuição é inválida
        """
        if source_type == target_type:
            return True
        
        if not TypeChecker.can_coerce(source_type, target_type):
            raise SemanticError(
                f"Atribuição inválida: não pode atribuir {source_type} a {target_type}"
            )
        
        return True
