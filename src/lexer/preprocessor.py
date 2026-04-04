import re

class Preprocessor:
    """
    Pré-processador Léxico para o Compilador Fortran 77.
    Resolve a limitação das bibliotecas baseadas em Regex (como o PLY) em lidarem
    com linguagens baseadas em posições de colunas estritas.
    """

    @staticmethod
    def process(source_code: str, format_type: str = 'fixed') -> str:
        """
        Recebe o código fonte bruto e devolve um código processado e limpo,
        agnóstico ao formato, para poder ser facilmente lido pelo PLY Regex Lexer.
        """
        if format_type == 'fixed':
            return Preprocessor._process_fixed(source_code)
        elif format_type == 'free':
            return Preprocessor._process_free(source_code)
        else:
            raise ValueError(f"Formato desconhecido no config: {format_type}")

    @staticmethod
    def _process_fixed(source_code: str) -> str:
        """
        Processa Fortran 77 ANSI Standard (Fixed Form).
        A regra das colunas é:
        C1    : 'C', 'c', '*' indica linha inteira como comentário.
        C1-C5 : Label numérico (separado do código).
        C6    : Se não for espaço ou '0', é uma linha de continuação.
        C7-C72: O código executável efetivamente real.
        """
        lines = source_code.splitlines()
        processed_lines = []
        previous_line_eligible_for_continuation = False

        for line in lines:

            # Ignora linhas totalmente vazias (mas mantém o número de linhas para relatórios de erro)
            if not line.strip():
                processed_lines.append("")
                previous_line_eligible_for_continuation = False
                continue

            # Comentários (coluna 1 com C ou *)
            # Remove comentários inteiros, mas mantém o número de linhas para relatórios de erro
            if line[0].upper() in ['C', '*']:
                processed_lines.append("")
                previous_line_eligible_for_continuation = False
                continue

            # Se a linha for mais curta que 72, fará padding.
            line_padded = line.ljust(72)
            
            # Para o resto das linhas, precisamos de separar as componentes lógicas (label, caracter de continuação, código executável).
            label_field = line_padded[0:5].strip()
            continuation_char = line_padded[5]
            code_field = line_padded[6:72]

            # Continuação de Linhas
            # TODO: Ver no futuro onde fazer a gestão de erros na linha original caso uma linha de continuação provoque erro de sintaxe.
        
            if continuation_char not in [' ', '0']: # É uma linha de continuação. 
                # Se a continuação vier imediatamente após uma linha de código ou outra continuação válida,
                # junta-se ao statement anterior.
                if previous_line_eligible_for_continuation:
                    last_index = len(processed_lines) - 1
                    while last_index >= 0 and not processed_lines[last_index].strip():
                        last_index -= 1

                    if last_index >= 0:
                        processed_lines[last_index] += " " + code_field.strip()
                    else:
                        processed_lines.append(line)

                    processed_lines.append("")  # Deixar vazio na linha atual para manter contador
                    previous_line_eligible_for_continuation = True
                    continue
                # Caso contrário, preservamos a linha original inteira (com o caractere de continuação) para depois tratar do erro de sintaxe.
                processed_lines.append(line)
                previous_line_eligible_for_continuation = False
                continue
            
            # Se chegamos aqui, estamos a lidar com uma nova linha / statement.
            # Convertê-la usando um formato intermédio para facilitar o Lexer.

            # DUVIDA: ESCOLHER UMA DAS ABORDAGENS:

            # 1. Usamos um token reservado para o label, porque um simples espaço poderia tornar
            # ambíguo distinguir entre um label numérico e um número que começa o statement.
            # Ex: em "10 DO I = 1" o 10 é um label; em "10 + 20" o 10 é um valor.
            # O token especial __LABEL__ não existe em Fortran normal, então o lexer/parser
            # pode identificar o rótulo sem confundir com a sintaxe da linguagem.
            
            # Ex: "10    DO I = 1, 5" -> "__LABEL__10 DO I = 1, 5"
            built_line = f"__LABEL__{label_field} {code_field.strip()}" if label_field else code_field.strip()

            # 2. Para manter o output uniforme entre fixed-form e free-form, apenas mantemos
            # o label e o resto do código separados por espaço. A desambiguação
            # entre label inicial e número de expressão fica a cargo do parser.
            
            # Ex: "10    DO I = 1, 5" -> "10 DO I = 1, 5"
            # built_line = f"{label_field} {code_field.strip()}" if label_field else code_field.strip()

            processed_lines.append(built_line)
            previous_line_eligible_for_continuation = True

        return '\n'.join(processed_lines)
    
    #TODO: Acho que dá para simplificar isto, ou pelo menos fazer uma lógica mais uniforme para as linhas de continuação nos dois formato
    #porque um esta a usar um buffer e o outro a manter um contador de linhas elegíveis para continuação e ir dar append á ultima linha se for elegivel
    # Talvez seja possível unificar a lógica de continuação e flush para ambos os formatos, ou pelo menos tornar mais consistente.

    @staticmethod
    def _process_free(source_code: str) -> str:
        """
        Processa Fortran Free Form.
        Neste formato, comentários são dados por '!', 
        e continuações de linha são indicadas por '&' no final da linha.
        """
        lines = source_code.splitlines()
        processed_lines = []
        
        buffer_line = ""
        statement_start_line = None

        def flush_buffer() -> None:
            nonlocal buffer_line, statement_start_line
            if statement_start_line is not None:
                processed_lines[statement_start_line] = buffer_line.strip()
                buffer_line = ""
                statement_start_line = None

        for line in lines:
            if not line.strip():
                flush_buffer()
                processed_lines.append("")
                continue

            # Remover comentários: encontra o primeiro '!' fora de strings, mas de forma simples só procuramos '!'
            code_part = line.split('!', 1)[0].strip() # divide a linha no primeiro '!' e usa a parte do código (index 0, antes do comentário)
            
            if not code_part:
                flush_buffer()
                processed_lines.append("")
                continue

            # Verificar continuação '&'
            if code_part.endswith('&'):
                if statement_start_line is None:
                    statement_start_line = len(processed_lines)
                    buffer_line = ""

                buffer_line += code_part[:-1] + " "
                processed_lines.append("") # Preservar layout de nº de linhas
                continue

            if statement_start_line is not None:
                buffer_line += code_part
                flush_buffer()
                processed_lines.append("")
            else:
                processed_lines.append(code_part)

        flush_buffer()
        return '\n'.join(processed_lines)

