C     --------- EXEMPLO 9: LÓGICA COMPLEXA ---------
      PROGRAM LOGICA
      INTEGER N
      LOGICAL RESULTADO
      
      N = 15
      RESULTADO = (N .GT. 10) .AND. (N .LT. 20)
      RESULTADO = (N .EQ. 15) .OR. (N .EQ. 20)
      RESULTADO = .NOT. (N .LE. 0)
      
      END