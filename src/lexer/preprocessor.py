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
        
        current_statement = ""
        current_label = ""

        for line_number, line in enumerate(lines):
            # Se a linha for mais curta que 72, fará padding mentalmente. Mas lidamos string a string.
            if not line.strip():
                # Ignora linhas totalmente vazias
                processed_lines.append("") 
                continue

            # 1. Comentários (coluna 1 com C ou *)
            # Retornamos uma string vazia para manter o número de linhas igual e não quebrar
            # os relatórios de erros ("Erro na linha X").
            if line[0:1].upper() in ['C', '*']:
                processed_lines.append("")
                continue

            # Para linhas normais, precisamos separar as componentes lógicas.
            # Lidar com o caso de linhas que não chegam sequer à coluna 6
            line_padded = line.ljust(72)
            
            label_field = line_padded[0:5].strip()
            continuation_char = line_padded[5:6]
            code_field = line_padded[6:72]

            # 2. Continuação de Linhas
            # TODO: Melhorar no futuro a gestão de erros na linha original caso 
            # uma linha de continuação provoque erro de sintaxe.
            if continuation_char not in [' ', '0']:
                # É uma linha de continuação. Removemos a pontuação newline anterior
                # e apendamos ao statement atual.
                # (Nota: o PLY vai precisar de adaptar-se aqui se as sub-linhas derem erro de linha, mas 
                # a nível léxico, o Fortran encara tudo como um só statement)
                
                # Pop out a última linha processada para concatenar
                if processed_lines:
                    last_index = len(processed_lines) - 1
                    # Apenas concatenamos na última linha válida
                    while last_index >= 0 and not processed_lines[last_index].strip():
                        last_index -= 1
                    
                    if last_index >= 0:
                        processed_lines[last_index] += " " + code_field.strip()
                        processed_lines.append("") # Deixar vazio na linha atual para manter contador
                continue
            
            # Se chegamos aqui, é uma nova linha / statement.
            # Convertê-la usando um formato intermédio para facilitar o Lexer
            # Podemos simplesmente inserir o label seguido de dois pontos (ou outro token), 
            # ou deixá-los explicitos.
            
            # Ex: "10    DO I = 1, 5" -> "10 DO I = 1, 5"
            built_line = f"{label_field} {code_field.strip()}" if label_field else code_field.strip()
            processed_lines.append(built_line)

        return '\n'.join(processed_lines)

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

        for line in lines:
            if not line.strip():
                processed_lines.append("")
                continue

            # Remover comentários: encontra o primeiro '!' fora de strings, mas 
            # de forma simples só procuramos '!'
            code_part = line.split('!', 1)[0].strip()
            
            if not code_part:
                processed_lines.append("")
                continue

            # Verificar continuação '&'
            if code_part.endswith('&'):
                buffer_line += code_part[:-1] + " "
                processed_lines.append("") # Preservar layout de nº de linhas
            else:
                buffer_line += code_part
                processed_lines.append(buffer_line.strip())
                buffer_line = ""

        return '\n'.join(processed_lines)

