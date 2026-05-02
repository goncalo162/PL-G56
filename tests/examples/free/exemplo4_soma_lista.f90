! EXEMPLO 4: SOMA DE LISTA
PROGRAM SOMAARR
INTEGER NUMS(5)
INTEGER I, SOMA

SOMA = 0
PRINT *, 'Introduza 5 numeros inteiros:'

DO I = 1, 5
  READ *, NUMS(I)
  SOMA = SOMA + NUMS(I)
ENDDO

PRINT *, 'A soma dos numeros e: ', SOMA
END
