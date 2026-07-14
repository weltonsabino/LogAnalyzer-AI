"""
Funções de nós para o StateGraph do LogAnalyzer AI.

Cada nó representa uma etapa no pipeline de execução do agente,
responsável por uma parte específica do workflow de análise de logs.

Implementação:
- Issue #3: Implementar lógica real dos nós (validate, read, parse, analyze)
- Issue #4: Integrar ferramentas LLM e formatação
"""

from datetime import datetime
from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.tools.validators import validate_file_path, validate_file_content
from src.loganalyzer.tools.file_reader import read_log_file
from src.loganalyzer.tools.parser import parse_log_content
from src.loganalyzer.tools.detector import detect_patterns
from src.loganalyzer.analysis.llm_interpreter import analyze_with_llm
from src.loganalyzer.tools.formatter import format_report


def validate_input_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Valida o caminho do arquivo de log e prepara para leitura.

    Este nó:
    - Verifica se file_path foi fornecido
    - Valida se arquivo existe e é legível (verificações básicas)
    - Define flag is_valid
    - Popula metadata com timestamp de validação

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com resultados de validação
    """
    # Valida arquivo usando ferramenta
    is_valid, message = validate_file_path(state.get("file_path", ""))

    # Atualiza estado com resultado de validação
    state["is_valid"] = is_valid

    if not is_valid:
        state["error_message"] = message
    else:
        state["error_message"] = None

    # Popula metadata com timestamp de validação
    state["metadata"]["validation_timestamp"] = datetime.now().isoformat()
    state["metadata"]["validation_message"] = message

    return state


def read_file_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Lê o conteúdo do arquivo de log usando a ferramenta file_reader.

    Este nó:
    - Usa a ferramenta file_reader
    - Popula file_content no estado
    - Trata erros de leitura graciosamente

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com file_content preenchido
    """
    # Verifica se validação anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando leitura - validação anterior falhou"
        return state

    try:
        # Lê arquivo usando ferramenta
        content = read_log_file(state.get("file_path", ""))
        state["file_content"] = content

        # Valida conteúdo do arquivo
        is_valid, message = validate_file_content(content)
        state["is_valid"] = is_valid

        if not is_valid:
            state["error_message"] = message
        else:
            state["metadata"]["file_read_timestamp"] = datetime.now().isoformat()
            state["metadata"]["file_size_bytes"] = len(content)
            state["metadata"]["file_lines"] = len(content.split('\n'))

    except FileNotFoundError as e:
        state["is_valid"] = False
        state["error_message"] = f"Arquivo não encontrado: {str(e)}"
    except PermissionError as e:
        state["is_valid"] = False
        state["error_message"] = f"Sem permissão de leitura: {str(e)}"
    except UnicodeDecodeError as e:
        state["is_valid"] = False
        state["error_message"] = f"Erro de encoding: {str(e)}"
    except Exception as e:
        state["is_valid"] = False
        state["error_message"] = f"Erro ao ler arquivo: {str(e)}"

    return state


def parse_events_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Faz parsing do conteúdo do log e identifica eventos individuais.

    Este nó:
    - Chama a ferramenta parser
    - Extrai eventos do conteúdo bruto do log
    - Popula lista parsed_events
    - Trata vários formatos de log (JSON, texto plano, customizado)

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com parsed_events preenchido
    """
    # Verifica se leitura anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando parsing - leitura anterior falhou"
        return state

    try:
        # Faz parsing do conteúdo
        content = state.get("file_content", "")
        events = parse_log_content(content)

        # Valida que eventos foram extraídos
        if not events:
            state["is_valid"] = False
            state["error_message"] = "Nenhum evento foi parseado do arquivo"
            return state

        # Popula eventos no estado
        state["parsed_events"] = events
        state["metadata"]["parsed_events_count"] = len(events)
        state["metadata"]["parse_timestamp"] = datetime.now().isoformat()

    except Exception as e:
        state["is_valid"] = False
        state["error_message"] = f"Erro ao parsear log: {str(e)}"

    return state


def analyze_patterns_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa eventos analisados para identificar padrões, erros, avisos.

    Este nó:
    - Chama a ferramenta detector
    - Identifica erros, avisos, eventos críticos
    - Agrupa eventos similares
    - Usa regex e heurísticas para detecção de padrões
    - Popula listas errors_found, warnings_found, critical_events

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com resultados de análise
    """
    # Verifica se parsing anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando análise - parsing anterior falhou"
        return state

    try:
        # Detecta padrões nos eventos
        events = state.get("parsed_events", [])
        analysis = detect_patterns(events)

        # Popula resultados no estado
        state["errors_found"] = analysis.get("errors", [])
        state["warnings_found"] = analysis.get("warnings", [])
        state["critical_events"] = analysis.get("critical", [])

        # Atualiza metadados
        state["metadata"]["errors_count"] = len(state["errors_found"])
        state["metadata"]["warnings_count"] = len(state["warnings_found"])
        state["metadata"]["critical_count"] = len(state["critical_events"])
        state["metadata"]["analysis_timestamp"] = datetime.now().isoformat()

    except Exception as e:
        state["is_valid"] = False
        state["error_message"] = f"Erro ao analisar padrões: {str(e)}"

    return state


def interpret_with_llm_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Usa LLM para interpretar a análise e gerar insights.

    Este nó:
    - Chama LangChain/LLM com contexto de análise
    - Gera analysis_result estruturado
    - Adiciona recomendações e insights
    - Pode chamar LLM múltiplas vezes para diferentes aspectos

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com analysis_result preenchido

    Integração com LLM: Issue #4
    """
    # Verifica se análise anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando interpretação LLM - análise anterior falhou"
        return state

    try:
        # Chama LLM com contexto de análise
        analysis_result = analyze_with_llm(
            errors_found=state.get("errors_found", []),
            warnings_found=state.get("warnings_found", []),
            critical_events=state.get("critical_events", []),
            parsed_events=state.get("parsed_events", []),
        )

        # Popula resultado no estado
        state["analysis_result"] = analysis_result

        # Atualiza metadados
        state["metadata"]["llm_analysis_timestamp"] = datetime.now().isoformat()
        state["metadata"]["llm_analysis_status"] = "concluída com sucesso"

    except Exception as e:
        state["is_valid"] = False
        state["error_message"] = f"Erro ao interpretar com LLM: {str(e)}"

    return state


def generate_report_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Gera o relatório markdown final a partir dos resultados de análise.

    Este nó:
    - Chama a ferramenta formatador (Issue #4)
    - Estrutura saída em formato markdown
    - Inclui resumo, eventos críticos, recomendações, métricas
    - Popula o campo report

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com report preenchido

    Implementação e ferramenta: Issue #3 & #4
    """
    try:
        # Formata relatório usando ferramenta
        report = format_report(
            analysis_result=state.get("analysis_result", {}),
            errors_found=state.get("errors_found", []),
            warnings_found=state.get("warnings_found", []),
            critical_events=state.get("critical_events", []),
            metadata=state.get("metadata", {}),
        )

        # Popula relatório no estado
        state["report"] = report

        # Atualiza metadados
        state["metadata"]["report_generation_timestamp"] = datetime.now().isoformat()
        state["metadata"]["report_status"] = "gerado com sucesso"

    except Exception as e:
        state["is_valid"] = False
        state["error_message"] = f"Erro ao gerar relatório: {str(e)}"

    return state


def error_handling_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Trata erros encontrados durante a execução.

    Este nó:
    - É chamado em transições de erro
    - Registra detalhes do erro
    - Define is_valid como False
    - Popula error_message
    - Pode também ser chamado como nó fallback

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com detalhes do erro
    """
    # Registra se não estava registrado
    if not state.get("error_message"):
        state["error_message"] = "Erro desconhecido durante execução"

    # Garante que is_valid está False
    state["is_valid"] = False

    # Popula metadados de erro
    state["metadata"]["error_timestamp"] = datetime.now().isoformat()
    state["metadata"]["error_message"] = state.get("error_message")

    return state
