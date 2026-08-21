"""
Funções de nós para o StateGraph do LogAnalyzer AI.

Cada nó representa uma etapa no pipeline de execução do agente,
responsável por uma parte específica do workflow de análise de logs.

Implementação:
- Issue #3: Implementar lógica real dos nós (validate, read, parse, analyze)
- Issue #4: Integrar ferramentas LLM e formatação
"""

from datetime import datetime
import asyncio
from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.tools.validators import validate_file_path, validate_file_content
from src.loganalyzer.tools.file_reader import read_log_file
from src.loganalyzer.tools.parser import parse_log_content
from src.loganalyzer.tools.detector import detect_patterns
from src.loganalyzer.analysis.llm_interpreter import analyze_with_llm
from src.loganalyzer.tools.formatter import format_report
from src.loganalyzer.governance import GovernancePolicy, AutonomyLevel


def validate_input_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Valida o caminho do arquivo de log e prepara para leitura.

    Este nó:
    - Aplica validação de governança (segurança adversarial)
    - Verifica se file_path foi fornecido
    - Valida se arquivo existe e é legível (verificações básicas)
    - Define flag is_valid e validation_error
    - Popula metadata com timestamp de validação e status de governança

    Argumentos:
        state: Estado atual de execução

    Retorno:
        Estado atualizado com resultados de validação
    """
    # Inicializa política de governança (nível ANALYZE = padrão)
    policy = GovernancePolicy(autonomy_level=AutonomyLevel.ANALYZE)
    file_path = state.get("file_path", "")

    # Validação de governança (adversarial) — executa ANTES de tudo
    governance_safe, governance_msg = policy.validate_file_path(file_path)
    state["metadata"]["governance_check_timestamp"] = datetime.now().isoformat()

    if not governance_safe:
        # Entrada adversarial detectada — bloqueia imediatamente
        state["is_valid"] = False
        state["error_message"] = f"Bloqueado por governança: {governance_msg}"
        state["validation_error"] = f"Bloqueado por governança: {governance_msg}"
        state["metadata"]["governance_status"] = "bloqueado"
        state["metadata"]["governance_reason"] = governance_msg
        state["metadata"]["validation_timestamp"] = datetime.now().isoformat()
        state["metadata"]["validation_message"] = governance_msg
        return state

    # Governança aprovada — prossegue com validação padrão
    state["metadata"]["governance_status"] = "aprovado"

    # Valida arquivo usando ferramenta
    is_valid, message = validate_file_path(file_path)

    # Atualiza estado com resultado de validação
    state["is_valid"] = is_valid

    if not is_valid:
        state["error_message"] = message
        state["validation_error"] = message
    else:
        state["error_message"] = None
        state["validation_error"] = None

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
    - Popula lista parsed_events e flag parsing_error
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
            error_msg = "Nenhum evento foi parseado do arquivo"
            state["error_message"] = error_msg
            state["parsing_error"] = error_msg
            return state

        # Popula eventos no estado
        state["parsed_events"] = events
        state["parsing_error"] = None
        state["metadata"]["parsed_events_count"] = len(events)
        state["metadata"]["parse_timestamp"] = datetime.now().isoformat()

    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao parsear log: {str(e)}"
        state["error_message"] = error_msg
        state["parsing_error"] = error_msg

    return state


def analyze_patterns_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa eventos analisados para identificar padrões, erros, avisos.

    Este nó:
    - Chama a ferramenta detector
    - Identifica erros, avisos, eventos críticos
    - Agrupa eventos similares e seta flag detection_error se falhar
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
        state["detection_error"] = None

        # Atualiza metadados
        state["metadata"]["errors_count"] = len(state["errors_found"])
        state["metadata"]["warnings_count"] = len(state["warnings_found"])
        state["metadata"]["critical_count"] = len(state["critical_events"])
        state["metadata"]["analysis_timestamp"] = datetime.now().isoformat()

        # Calcula rotas de severidade para rastreabilidade
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        high_levels = ["CRITICAL", "ERROR"]
        medium_levels = ["WARNING", "WARN"]
        for event in events:
            level = event.get("level", "").upper()
            if level in high_levels:
                severity_counts["HIGH"] += 1
            elif level in medium_levels:
                severity_counts["MEDIUM"] += 1
            else:
                severity_counts["LOW"] += 1
        state["severity_routes"] = severity_counts

    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao analisar padrões: {str(e)}"
        state["error_message"] = error_msg
        state["detection_error"] = error_msg

    return state


async def analyze_patterns_node_parallel(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa padrões em paralelo usando asyncio.
    
    Implementação da Task #30: Análise paralela de padrões.
    
    Este nó:
    - Processa eventos em paralelo com asyncio.gather()
    - Detecta padrões recorrentes
    - Analisa frequência de erros
    - Identifica anomalias
    - Combina resultados de forma thread-safe
    
    Argumentos:
        state: Estado atual contendo parsed_events
    
    Retorno:
        Estado atualizado com patterns analisados em paralelo
    """
    # Verifica se parsing anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando análise paralela - parsing anterior falhou"
        return state
    
    try:
        # Extrai eventos
        events = state.get("parsed_events", [])
        
        # Define tarefas paralelas (3 análises diferentes)
        async def analyze_recurrence():
            """Detecta padrões recorrentes nos eventos"""
            pattern_map = {}
            for event in events:
                message = event.get("message", "")
                pattern_map[message] = pattern_map.get(message, 0) + 1
            return {k: v for k, v in pattern_map.items() if v > 1}  # Apenas recorrentes
        
        async def analyze_frequency():
            """Analisa frequência de erros por tipo"""
            level_counts = {}
            for event in events:
                level = event.get("level", "UNKNOWN")
                level_counts[level] = level_counts.get(level, 0) + 1
            return level_counts
        
        async def analyze_anomalies():
            """Identifica anomalias (timestamps fora do padrão, etc)"""
            # Extrai timestamps e detecta gaps
            timestamps = []
            for event in events:
                if "timestamp" in event:
                    timestamps.append(event["timestamp"])
            
            anomalies = []
            if len(timestamps) > 1:
                # Detecta timestamps fora de sequência
                for i in range(1, len(timestamps)):
                    if timestamps[i] < timestamps[i-1]:
                        anomalies.append({
                            "type": "out_of_order_timestamp",
                            "index": i
                        })
            
            return anomalies
        
        # Executa tarefas em paralelo
        recurrence, frequency, anomalies = await asyncio.gather(
            analyze_recurrence(),
            analyze_frequency(),
            analyze_anomalies()
        )
        
        # Combina resultados em analysis_result
        parallel_analysis = {
            "recurrent_patterns": recurrence,
            "frequency_by_level": frequency,
            "anomalies": anomalies,
        }
        
        # Popula no estado (merges com análise anterior se existir)
        current_analysis = state.get("analysis_result", {})
        current_analysis["parallel_patterns"] = parallel_analysis
        state["analysis_result"] = current_analysis
        state["detection_error"] = None
        
        # Metadados
        state["metadata"]["parallel_analysis_timestamp"] = datetime.now().isoformat()
        state["metadata"]["parallel_analysis_status"] = "concluída com sucesso"
        
    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao analisar padrões em paralelo: {str(e)}"
        state["error_message"] = error_msg
        state["detection_error"] = error_msg
    
    return state


def analyze_patterns_parallel_sync(state: LogAnalysisState) -> LogAnalysisState:
    """
    Wrapper síncrono para análise paralela de padrões.
    
    Executa a corrotina analyze_patterns_node_parallel usando asyncio.run(),
    permitindo integração no grafo síncrono.
    
    Argumentos:
        state: Estado atual contendo parsed_events
    
    Retorno:
        Estado atualizado com patterns analisados em paralelo
    """
    return asyncio.run(analyze_patterns_node_parallel(state))


def interpret_with_llm_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Usa LLM para interpretar a análise e gerar insights.

    Este nó:
    - Chama LangChain/LLM com contexto de análise
    - Gera analysis_result estruturado com flag analysis_error se falhar
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
        # Obtém provider do estado (padrão: None, lê de ambiente)
        provider = state.get("llm_provider")

        # Chama LLM com contexto de análise
        analysis_result = analyze_with_llm(
            errors_found=state.get("errors_found", []),
            warnings_found=state.get("warnings_found", []),
            critical_events=state.get("critical_events", []),
            parsed_events=state.get("parsed_events", []),
            provider=provider,
        )

        # Merge com análise existente (preserva dados de severity/parallel)
        existing_analysis = state.get("analysis_result", {})
        # LLM result como base, preservando campos existentes que não vêm do LLM
        for key, value in existing_analysis.items():
            if key not in analysis_result:
                analysis_result[key] = value
        state["analysis_result"] = analysis_result
        state["analysis_error"] = None

        # Atualiza metadados
        state["metadata"]["llm_analysis_timestamp"] = datetime.now().isoformat()
        state["metadata"]["llm_analysis_status"] = "concluída com sucesso"
        state["metadata"]["llm_provider"] = provider or "openai (padrão)"

    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao interpretar com LLM: {str(e)}"
        state["error_message"] = error_msg
        state["analysis_error"] = error_msg

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


def analyze_high_severity_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa eventos de alta severidade com prioridade máxima.
    
    Implementação da Task #30: Nó especializado para eventos críticos/erro.
    
    Este nó:
    - Processa CRITICAL e ERROR com modelo focado em incidentes
    - Chama LLM com contexto crítico
    - Popula analysis_result com severity_level = "HIGH"
    - Adiciona recomendações urgentes
    
    Argumentos:
        state: Estado atual contendo events parseados
    
    Retorno:
        Estado atualizado com analysis_result populado
    """
    # Verifica se análise anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando análise alta severidade - etapas anteriores falharam"
        return state
    
    try:
        # Obtém provider
        provider = state.get("llm_provider")
        
        # Chama LLM com foco em eventos críticos
        analysis_result = analyze_with_llm(
            errors_found=state.get("errors_found", []),
            warnings_found=state.get("warnings_found", []),
            critical_events=state.get("critical_events", []),
            parsed_events=state.get("parsed_events", []),
            provider=provider,
        )
        
        # Seta severidade no resultado
        analysis_result["severity_level"] = "HIGH"
        analysis_result["urgency"] = "IMEDIATA"
        
        # Popula no estado
        state["analysis_result"] = analysis_result
        state["analysis_error"] = None
        
        # Metadados
        state["metadata"]["severity_analysis"] = "HIGH"
        state["metadata"]["severity_analysis_timestamp"] = datetime.now().isoformat()
        
    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao analisar alta severidade: {str(e)}"
        state["error_message"] = error_msg
        state["analysis_error"] = error_msg
    
    return state


def analyze_medium_severity_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa eventos de severidade média com análise balanceada.
    
    Implementação da Task #30: Nó especializado para avisos.
    
    Este nó:
    - Processa WARNING com modelo balanceado
    - Chama LLM com contexto padrão
    - Popula analysis_result com severity_level = "MEDIUM"
    - Adiciona recomendações preventivas
    
    Argumentos:
        state: Estado atual contendo events parseados
    
    Retorno:
        Estado atualizado com analysis_result populado
    """
    # Verifica se análise anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando análise média severidade - etapas anteriores falharam"
        return state
    
    try:
        # Obtém provider
        provider = state.get("llm_provider")
        
        # Chama LLM com análise padrão
        analysis_result = analyze_with_llm(
            errors_found=state.get("errors_found", []),
            warnings_found=state.get("warnings_found", []),
            critical_events=state.get("critical_events", []),
            parsed_events=state.get("parsed_events", []),
            provider=provider,
        )
        
        # Seta severidade no resultado
        analysis_result["severity_level"] = "MEDIUM"
        analysis_result["urgency"] = "NORMAL"
        
        # Popula no estado
        state["analysis_result"] = analysis_result
        state["analysis_error"] = None
        
        # Metadados
        state["metadata"]["severity_analysis"] = "MEDIUM"
        state["metadata"]["severity_analysis_timestamp"] = datetime.now().isoformat()
        
    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao analisar média severidade: {str(e)}"
        state["error_message"] = error_msg
        state["analysis_error"] = error_msg
    
    return state


def analyze_low_severity_node(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa eventos de baixa severidade com análise simplificada.
    
    Implementação da Task #30: Nó especializado para info/debug.
    
    Este nó:
    - Processa INFO e DEBUG com análise simplificada
    - Chama LLM para análise complementar
    - Popula analysis_result com severity_level = "LOW"
    - Adiciona insights informativos
    
    Argumentos:
        state: Estado atual contendo events parseados
    
    Retorno:
        Estado atualizado com analysis_result populado
    """
    # Verifica se análise anterior passou
    if not state.get("is_valid", False):
        state["error_message"] = "Pulando análise baixa severidade - etapas anteriores falharam"
        return state
    
    try:
        # Obtém provider
        provider = state.get("llm_provider")
        
        # Chama LLM para consistência
        analysis_result = analyze_with_llm(
            errors_found=state.get("errors_found", []),
            warnings_found=state.get("warnings_found", []),
            critical_events=state.get("critical_events", []),
            parsed_events=state.get("parsed_events", []),
            provider=provider,
        )
        
        # Seta severidade no resultado
        analysis_result["severity_level"] = "LOW"
        analysis_result["urgency"] = "BAIXA"
        
        # Popula no estado
        state["analysis_result"] = analysis_result
        state["analysis_error"] = None
        
        # Metadados
        state["metadata"]["severity_analysis"] = "LOW"
        state["metadata"]["severity_analysis_timestamp"] = datetime.now().isoformat()
        
    except Exception as e:
        state["is_valid"] = False
        error_msg = f"Erro ao analisar baixa severidade: {str(e)}"
        state["error_message"] = error_msg
        state["analysis_error"] = error_msg
    
    return state
