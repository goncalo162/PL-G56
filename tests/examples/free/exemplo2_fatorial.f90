PROGRAM FATORIAL
INTEGER N, I, FAT

PRINT *, 'Introduza um numero inteiro positivo:'
READ *, N

FAT = 1
DO I = 1, N
  FAT = FAT * I
ENDDO

PRINT *, 'Fatorial de ', N, ': ', FAT
END
