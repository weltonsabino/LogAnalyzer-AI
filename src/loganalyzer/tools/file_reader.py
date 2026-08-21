"""
Ferramenta de leitura de arquivo para o LogAnalyzer AI.

Fornece função para ler arquivos de log com tratamento de erros.
"""

from src.loganalyzer.observability import with_retry, with_timeout


@with_timeout(seconds=30)
@with_retry(max_attempts=3, backoff=1.5)
def read_log_file(file_path: str) -> str:
    """
    Lê o conteúdo completo de um arquivo de log.

    Esta ferramenta:
    - Abre arquivo de log
    - Lê conteúdo com encoding UTF-8
    - Trata erros de leitura
    - Retorna conteúdo ou mensagem de erro
    - Implementa retry automático em caso de erros transientes
    - Timeout máximo de 30 segundos

    Argumentos:
        file_path: Caminho do arquivo de log a ler

    Retorno:
        Conteúdo do arquivo em string

    Levanta:
        FileNotFoundError: Se arquivo não existe
        PermissionError: Se sem permissão de leitura
        UnicodeDecodeError: Se encoding incompatível
        TimeoutError: Se leitura exceder 30 segundos
    """
    # Tenta abrir e ler arquivo com encoding UTF-8
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}") from e
    except PermissionError as e:
        raise PermissionError(f"Sem permissão de leitura: {file_path}") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"Erro de encoding ao ler {file_path}: {e.reason}"
        ) from e
