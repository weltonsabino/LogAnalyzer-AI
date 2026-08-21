"""
Modelos e estruturas de dados para o agente LogAnalyzer AI.

Define o estado compartilhado (LogAnalysisState) usado pelo StateGraph
para manter informações durante a execução do agente.
"""

from typing import TypedDict, Optional, List, Dict, Any


class LogAnalysisState(TypedDict):
    """
    Estado compartilhado do StateGraph do LogAnalyzer AI.

    Mantém todas as informações relevantes durante a execução do agente,
    desde a validação de entrada até a geração do relatório final.

    Atributos:
        file_path (str): Caminho do arquivo de log a analisar
        file_content (str): Conteúdo completo do arquivo de log (preenchido após leitura)
        parsed_events (list): Lista de eventos de log analisados
        errors_found (list): Lista de erros identificados no log
        warnings_found (list): Lista de avisos identificados no log
        critical_events (list): Lista de eventos críticos/severos
        analysis_result (dict): Resultados da análise estruturada do agente
        report (str): Relatório final formatado em markdown
        metadata (dict): Metadados adicionais (timestamps, info de processamento)
        llm_provider (str): Provedor LLM a usar (openai ou groq). Padrão: openai
        is_valid (bool): Se a entrada e processamento são válidos
        error_message (Optional[str]): Descrição do erro se algo deu errado
        validation_error (Optional[str]): Erro específico de validação
        parsing_error (Optional[str]): Erro específico de parsing
        detection_error (Optional[str]): Erro específico de detecção de padrões
        analysis_error (Optional[str]): Erro específico de análise IA
        severity_routes (dict): Contagem de eventos por severidade {HIGH: N, MEDIUM: N, LOW: N}
    """

    # Entrada e conteúdo do arquivo
    file_path: str
    file_content: str

    # Resultados da análise
    parsed_events: List[Dict[str, Any]]
    errors_found: List[Dict[str, Any]]
    warnings_found: List[Dict[str, Any]]
    critical_events: List[Dict[str, Any]]

    # Saída do agente
    analysis_result: Dict[str, Any]
    report: str

    # Metadados e status
    metadata: Dict[str, Any]
    llm_provider: Optional[str]
    is_valid: bool
    error_message: Optional[str]

    # Flags de erro específicas por etapa (para roteamento condicional)
    validation_error: Optional[str]
    parsing_error: Optional[str]
    detection_error: Optional[str]
    analysis_error: Optional[str]

    # Roteamento por severidade
    severity_routes: Dict[str, int]
