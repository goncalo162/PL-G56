C     --------- EXEMPLO 7: ARRAYS MULTIDIMENSIONAIS ---------
      PROGRAM ARRAYS
      INTEGER MATRIX(3,3)
      INTEGER I, J, SOMA
      REAL VECTOR(10)
      
      SOMA = 0
      DO 100 I = 1, 3
         DO 150 J = 1, 3
            MATRIX(I, J) = I + J
            SOMA = SOMA + MATRIX(I, J)
   150    CONTINUE
   100 CONTINUE