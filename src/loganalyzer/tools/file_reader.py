"""
Ferramenta de leitura de arquivo para o LogAnalyzer AI.

Fornece função para ler arquivos de log com tratamento de erros.
"""


def read_log_file(file_path: str) -> str:
    """
    Lê o conteúdo completo de um arquivo de log.

    Esta ferramenta:
    - Abre arquivo de log
    - Lê conteúdo com encoding UTF-8
    - Trata erros de leitura
    - Retorna conteúdo ou mensagem de erro

    Argumentos:
        file_path: Caminho do arquivo de log a ler

    Retorno:
        Conteúdo do arquivo em string

    Levanta:
        FileNotFoundError: Se arquivo não existe
        PermissionError: Se sem permissão de leitura
        UnicodeDecodeError: Se encoding incompatível
    """
    # Tenta abrir e ler arquivo com encoding UTF-8
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    except PermissionError:
        raise PermissionError(f"Sem permissão de leitura: {file_path}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"Erro de encoding ao ler {file_path}: {e.reason}"
        )
