"""
StateGraph para o agente LogAnalyzer AI.

Define a estrutura principal do grafo de agente usando LangGraph,
incluindo nós, arestas e fluxo de execução para automação de análise de logs.
"""

from typing import Optional
from langgraph.graph import StateGraph, END

from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.nodes import (
    validate_input_node,
    read_file_node,
    parse_events_node,
    analyze_patterns_node,
    interpret_with_llm_node,
    generate_report_node,
    error_handling_node,
)


def create_agent_graph() -> StateGraph:
    """
    Cria e retorna o StateGraph configurado para LogAnalyzer AI.

    Estrutura do grafo:
    ```
    INÍCIO
      ↓
    [validate_input] ──(inválido)──→ [error_handling] → FIM
      ↓ (válido)
    [read_file] ──(erro)──→ [error_handling] → FIM
      ↓ (sucesso)
    [parse_events] ──(erro)──→ [error_handling] → FIM
      ↓ (sucesso)
    [analyze_patterns] ──(erro)──→ [error_handling] → FIM
      ↓ (sucesso)
    [interpret_with_llm] ──(erro)──→ [error_handling] → FIM
      ↓ (sucesso)
    [generate_report]
      ↓
    FIM
    ```

    Retorno:
        StateGraph: Grafo configurado pronto para execução

    Nota:
        Arestas condicionais (transições if-else) serão adicionadas em Issue #3
        quando a lógica dos nós estiver completamente implementada.
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

    # ============================================
    # 2. DEFINE PONTO DE ENTRADA
    # ============================================
    graph.set_entry_point("validate_input")

    # ============================================
    # 3. ADICIONA ARESTAS (Conexões entre nós)
    # ============================================

    # Caminho feliz: Progressão linear pelo pipeline
    graph.add_edge("validate_input", "read_file")
    graph.add_edge("read_file", "parse_events")
    graph.add_edge("parse_events", "analyze_patterns")
    graph.add_edge("analyze_patterns", "interpret_with_llm")
    graph.add_edge("interpret_with_llm", "generate_report")
    graph.add_edge("generate_report", END)

    # Caminhos de erro: Qualquer etapa pode transicionar para error_handling
    # Nota: Arestas condicionais baseadas em state.is_valid ou flags de erro
    # serão implementadas em Issue #3 quando lógica dos nós estiver pronta
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
    )
