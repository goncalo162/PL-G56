C     --------- EXEMPLO 6: OPERAÇÕES COM REAIS ---------
      PROGRAM OPERACOES
      REAL X, Y, Z, RESULTADO
      INTEGER N
      
      X = 3.14
      Y = 2.71
      Z = 1.5E2
      N = 10
      
      RESULTADO = X + Y
      RESULTADO = Z * 1.0E-1
      RESULTADO = X ** 2
      
      IF (X .GT. Y) THEN
         PRINT *, 'X maior que Y'
      ENDIF
      
      END