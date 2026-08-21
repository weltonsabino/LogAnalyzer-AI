"""
StateGraph para o agente LogAnalyzer AI.

Define a estrutura principal do grafo de agente usando LangGraph,
incluindo nós, arestas e fluxo de execução para automação de análise de logs.
"""

from typing import Optional
from langgraph.graph import StateGraph, END

from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.observability import TraceCollector
from src.loganalyzer.nodes import (
    validate_input_node,
    read_file_node,
    parse_events_node,
    analyze_patterns_node,
    analyze_patterns_node_parallel,
    analyze_patterns_parallel_sync,
    interpret_with_llm_node,
    generate_report_node,
    error_handling_node,
    analyze_high_severity_node,
    analyze_medium_severity_node,
    analyze_low_severity_node,
)


# ============================================
# FUNÇÕES DE ROTEAMENTO CONDICIONAL
# ============================================

def route_after_validation(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se validação falhar.

    Argumentos:
        state: Estado atual do grafo

    Retorno:
        "error_handling" se há erro de validação, "read_file" caso contrário
    """
    # Verifica se há erro de validação
    if state.get("validation_error"):
        return "error_handling"
    return "read_file"


def route_after_parsing(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se parsing falhar.

    Argumentos:
        state: Estado atual do grafo

    Retorno:
        "error_handling" se há erro de parsing, "analyze_patterns" caso contrário
    """
    # Verifica se há erro de parsing
    if state.get("parsing_error"):
        return "error_handling"
    return "analyze_patterns"


def route_after_detection(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se detecção de padrões falhar.

    Argumentos:
        state: Estado atual do grafo

    Retorno:
        "error_handling" se há erro de detecção, "interpret_with_llm" caso contrário
    """
    # Verifica se há erro de detecção
    if state.get("detection_error"):
        return "error_handling"
    return "interpret_with_llm"


def route_after_analysis(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se análise IA falhar.

    Argumentos:
        state: Estado atual do grafo

    Retorno:
        "error_handling" se há erro de análise, "generate_report" caso contrário
    """
    # Verifica se há erro de análise
    if state.get("analysis_error"):
        return "error_handling"
    return "generate_report"


def route_by_severity(state: LogAnalysisState) -> str:
    """
    Roteia análise com base na severidade dos eventos detectados.
    
    Implementação da Task #30: Ramificação inteligente por severidade.
    
    Determina o nó de análise apropriado baseado na severidade máxima
    dos eventos encontrados no estado.
    
    Argumentos:
        state: Estado atual contendo parsed_events
    
    Retorno:
        - "analyze_high_severity": Se há eventos críticos (CRITICAL, ERROR)
        - "analyze_medium_severity": Se há eventos médios (WARNING)
        - "analyze_low_severity": Se há eventos baixos (INFO, DEBUG)
    """
    # Extrai eventos já parseados do estado
    events = state.get("parsed_events", [])
    
    # Inicializa contadores de severidade
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    # Mapeia níveis de severidade para categorias
    high_severity_levels = ["CRITICAL", "ERROR"]
    medium_severity_levels = ["WARNING", "WARN"]
    low_severity_levels = ["INFO", "DEBUG", "TRACE"]
    
    # Conta eventos por severidade
    for event in events:
        # Extrai nível de severidade do evento
        level = event.get("level", "").upper()
        
        if level in high_severity_levels:
            severity_counts["HIGH"] += 1
        elif level in medium_severity_levels:
            severity_counts["MEDIUM"] += 1
        elif level in low_severity_levels:
            severity_counts["LOW"] += 1
    
    # Armazena contadores no estado para rastreabilidade
    state["severity_routes"] = severity_counts
    
    # Retorna rota baseada na severidade máxima encontrada
    if severity_counts["HIGH"] > 0:
        return "analyze_high_severity"
    elif severity_counts["MEDIUM"] > 0:
        return "analyze_medium_severity"
    else:
        return "analyze_low_severity"


def create_agent_graph() -> StateGraph:
    """
    Cria e retorna o StateGraph configurado para LogAnalyzer AI.

    Estrutura do grafo com arestas condicionais:
    ```
    INÍCIO
      ↓
    [validate_input]
      ├─(validation_error)──→ [error_handling] → FIM
      └─(sucesso)──→ [read_file]
      ↓ (sempre sucesso)
    [parse_events]
      ├─(parsing_error)──→ [error_handling] → FIM
      └─(sucesso)──→ [analyze_patterns]
      ↓
    [analyze_patterns]
      ├─(detection_error)──→ [error_handling] → FIM
      └─(sucesso)──→ [interpret_with_llm]
      ↓
    [interpret_with_llm]
      ├─(analysis_error)──→ [error_handling] → FIM
      └─(sucesso)──→ [generate_report]
      ↓
    [generate_report]
      ↓
    FIM
    ```

    Retorno:
        StateGraph: Grafo configurado com arestas condicionais para error handling

    Nota:
        As arestas condicionais roteiam para error_handling baseado em flags
        específicas (validation_error, parsing_error, detection_error, analysis_error)
        definidas pelos nós correspondentes no estado.
    """

    # Inicializa o grafo com LogAnalysisState
    graph = StateGraph(LogAnalysisState)

    # ============================================
    # 1. ADICIONA NÓS AO GRAFO
    # ============================================

    # Nós principais do pipeline de processamento
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("read_file", read_file_node)
    graph.add_node("parse_events", parse_events_node)
    graph.add_node("analyze_patterns", analyze_patterns_node)
    graph.add_node("interpret_with_llm", interpret_with_llm_node)
    graph.add_node("generate_report", generate_report_node)

    # Nó de tratamento de erro
    graph.add_node("error_handling", error_handling_node)

    # Nós de análise paralela (Task #30)
    graph.add_node("analyze_patterns_parallel", analyze_patterns_parallel_sync)

    # Nós de análise por severidade (Task #30)
    graph.add_node("analyze_high_severity", analyze_high_severity_node)
    graph.add_node("analyze_medium_severity", analyze_medium_severity_node)
    graph.add_node("analyze_low_severity", analyze_low_severity_node)

    # ============================================
    # 2. DEFINE PONTO DE ENTRADA
    # ============================================
    graph.set_entry_point("validate_input")

    # ============================================
    # 3. ADICIONA ARESTAS (Conexões entre nós)
    # ============================================

    # Aresta condicional após validação
    # Se há erro de validação → error_handling, senão → read_file
    graph.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "error_handling": "error_handling",
            "read_file": "read_file"
        }
    )

    # Aresta direta: read_file para parse_events (sem erro esperado)
    graph.add_edge("read_file", "parse_events")

    # Aresta condicional após parsing
    # Se há erro de parsing → error_handling, senão → analyze_patterns
    graph.add_conditional_edges(
        "parse_events",
        route_after_parsing,
        {
            "error_handling": "error_handling",
            "analyze_patterns": "analyze_patterns"
        }
    )

    # Aresta condicional após detecção de padrões
    # Se há erro de detecção → error_handling, senão → route_by_severity (rota condicional)
    graph.add_conditional_edges(
        "analyze_patterns",
        route_by_severity,
        {
            "error_handling": "error_handling",
            "analyze_high_severity": "analyze_high_severity",
            "analyze_medium_severity": "analyze_medium_severity",
            "analyze_low_severity": "analyze_low_severity",
        }
    )

    # Aresta condicional após análise IA
    # Se há erro de análise → error_handling, senão → generate_report
    graph.add_conditional_edges(
        "interpret_with_llm",
        route_after_analysis,
        {
            "error_handling": "error_handling",
            "generate_report": "generate_report"
        }
    )

    # Arestas dos nós de análise por severidade para análise paralela (Task #30)
    graph.add_edge("analyze_high_severity", "analyze_patterns_parallel")
    graph.add_edge("analyze_medium_severity", "analyze_patterns_parallel")
    graph.add_edge("analyze_low_severity", "analyze_patterns_parallel")

    # Aresta da análise paralela para interpretação LLM
    graph.add_edge("analyze_patterns_parallel", "interpret_with_llm")

    # Aresta final: generate_report para END
    graph.add_edge("generate_report", END)

    # Aresta final: error_handling para END
    graph.add_edge("error_handling", END)

    # ============================================
    # 4. COMPILA O GRAFO
    # ============================================

    agent = graph.compile()
    return agent


def get_initial_state(file_path: str, provider: Optional[str] = None) -> LogAnalysisState:
    """
    Cria estado inicial para execução do agente.

    Argumentos:
        file_path: Caminho do arquivo de log a analisar
        provider: Provedor LLM (openai ou groq). Sobrescreve LLM_PROVIDER env.

    Retorno:
        LogAnalysisState inicial pronto para execução do agente
    """
    # Cria coletor de observabilidade com execution_id único
    trace_collector = TraceCollector()
    
    return LogAnalysisState(
        file_path=file_path,
        file_content="",
        parsed_events=[],
        errors_found=[],
        warnings_found=[],
        critical_events=[],
        analysis_result={},
        report="",
        metadata={
            "start_time": None,  # Será definido em runtime
            "version": "0.0.1",
            "agent_name": "LogAnalyzer AI",
        },
        llm_provider=provider,
        is_valid=True,
        error_message=None,
        validation_error=None,
        parsing_error=None,
        detection_error=None,
        analysis_error=None,
        severity_routes={},
        trace_collector=trace_collector,
        execution_id=trace_collector.execution_id,
    )
