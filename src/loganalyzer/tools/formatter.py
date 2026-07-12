"""
Ferramenta de formatação de relatório para o LogAnalyzer AI.

Fornece função para formatar resultados de análise em markdown estruturado.
"""

from typing import Dict, Any, List
from datetime import datetime


def format_report(
    analysis_result: Dict[str, Any],
    errors_found: List[Dict[str, Any]],
    warnings_found: List[Dict[str, Any]],
    critical_events: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> str:
    """
    Formata resultados de análise em relatório markdown estruturado.

    Esta ferramenta:
    - Estrutura saída em formato markdown
    - Inclui resumo, métricas, eventos críticos
    - Adiciona recomendações baseadas em análise
    - Retorna relatório pronto para visualização

    Argumentos:
        analysis_result: Resultados da análise do LLM (insights, recomendações)
        errors_found: Lista de erros identificados
        warnings_found: Lista de avisos identificados
        critical_events: Lista de eventos críticos
        metadata: Metadados da execução (timestamps, contadores, etc)

    Retorno:
        Relatório completo em markdown
    """
    report_lines = [
        "# Relatorio de Analise de Log",
        "## LogAnalyzer AI",
        "",
        "---",
        "",
    ]

    # ============================================
    # Secao: Resumo Executivo
    # ============================================
    report_lines.extend(_format_summary_section(metadata, errors_found, warnings_found, critical_events))

    # ============================================
    # Secao: Eventos Criticos
    # ============================================
    if critical_events:
        report_lines.extend(_format_critical_section(critical_events))

    # ============================================
    # Secao: Erros Identificados
    # ============================================
    if errors_found:
        report_lines.extend(_format_errors_section(errors_found))

    # ============================================
    # Secao: Avisos Identificados
    # ============================================
    if warnings_found:
        report_lines.extend(_format_warnings_section(warnings_found))

    # ============================================
    # Secao: Insights e Recomendacoes do LLM
    # ============================================
    if analysis_result:
        report_lines.extend(_format_insights_section(analysis_result))

    # ============================================
    # Secao: Metadados de Execucao
    # ============================================
    report_lines.extend(_format_metadata_section(metadata))

    # Retorna relatório como string única
    return "\n".join(report_lines)


def _format_summary_section(
    metadata: Dict[str, Any],
    errors_found: List[Dict[str, Any]],
    warnings_found: List[Dict[str, Any]],
    critical_events: List[Dict[str, Any]],
) -> List[str]:
    """
    Formata secao de resumo executivo com metricas principais.

    Retorno:
        Lista de linhas markdown para resumo
    """
    lines = [
        "## Resumo Executivo",
        "",
    ]

    # Calcula métricas
    total_events = metadata.get("parsed_events_count", 0)
    error_count = len(errors_found)
    warning_count = len(warnings_found)
    critical_count = len(critical_events)

    # Tabela de métricas
    lines.extend([
        "| Métrica | Quantidade |",
        "|---------|-----------|",
        f"| Total de eventos | {total_events} |",
        f"| Erros encontrados | {error_count} |",
        f"| Avisos encontrados | {warning_count} |",
        f"| Eventos críticos | {critical_count} |",
        "",
    ])

    # Percentuais
    if total_events > 0:
        error_pct = (error_count / total_events) * 100
        warning_pct = (warning_count / total_events) * 100
        critical_pct = (critical_count / total_events) * 100

        lines.extend([
            "### Percentuais",
            f"- **Erros:** {error_pct:.1f}%",
            f"- **Avisos:** {warning_pct:.1f}%",
            f"- **Críticos:** {critical_pct:.1f}%",
            "",
        ])

    # Avaliação de saúde
    if critical_count > 0:
        health = "CRITICA"
    elif error_count > 10:
        health = "ALERTA"
    elif warning_count > 20:
        health = "ATENCAO"
    else:
        health = "SAUDAVEL"

    lines.extend([
        f"### Status Geral: {health}",
        "",
    ])

    return lines


def _format_critical_section(critical_events: List[Dict[str, Any]]) -> List[str]:
    """
    Formata secao de eventos criticos.

    Retorno:
        Lista de linhas markdown para eventos criticos
    """
    lines = [
        "## Eventos Criticos",
        "",
        f"Encontrados **{len(critical_events)}** evento(s) critico(s):",
        "",
    ]

    for idx, event in enumerate(critical_events[:10], 1):  # Limita a 10 para não poluir
        line_num = event.get("line_number", "?")
        message = event.get("message", "")[:100]  # Limita mensagem a 100 caracteres
        reason = event.get("critical_reason", "detectado como crítico")

        lines.append(f"{idx}. **Linha {line_num}:** {message}")
        lines.append(f"   - Motivo: {reason}")
        lines.append("")

    if len(critical_events) > 10:
        lines.append(f"... e mais {len(critical_events) - 10} evento(s) crítico(s)")
        lines.append("")

    return lines


def _format_errors_section(errors_found: List[Dict[str, Any]]) -> List[str]:
    """
    Formata secao de erros encontrados.

    Retorno:
        Lista de linhas markdown para erros
    """
    lines = [
        "## Erros Identificados",
        "",
        f"Total: **{len(errors_found)}** erro(s)",
        "",
    ]

    # Agrupa erros por padrão de mensagem para detecção de padrões
    error_patterns = {}
    for error in errors_found:
        msg = error.get("message", "")[:80]  # Primeiros 80 caracteres
        if msg not in error_patterns:
            error_patterns[msg] = []
        error_patterns[msg].append(error)

    # Exibe padrões únicos
    for pattern, events in list(error_patterns.items())[:5]:  # Limita a 5 padrões
        count = len(events)
        lines.append(f"- **({count}x)** {pattern}")

    if len(error_patterns) > 5:
        remaining = len(error_patterns) - 5
        total_remaining_errors = sum(len(e) for e in list(error_patterns.values())[5:])
        lines.append(f"- ... e {remaining} padrão(ões) adicional(is) ({total_remaining_errors} erro(s))")

    lines.append("")
    return lines


def _format_warnings_section(warnings_found: List[Dict[str, Any]]) -> List[str]:
    """
    Formata secao de avisos encontrados.

    Retorno:
        Lista de linhas markdown para avisos
    """
    lines = [
        "## Avisos Encontrados",
        "",
        f"Total: **{len(warnings_found)}** aviso(s)",
        "",
    ]

    # Agrupa avisos por padrão de mensagem
    warning_patterns = {}
    for warning in warnings_found:
        msg = warning.get("message", "")[:80]
        if msg not in warning_patterns:
            warning_patterns[msg] = []
        warning_patterns[msg].append(warning)

    # Exibe padrões únicos
    for pattern, events in list(warning_patterns.items())[:5]:
        count = len(events)
        lines.append(f"- **({count}x)** {pattern}")

    if len(warning_patterns) > 5:
        remaining = len(warning_patterns) - 5
        total_remaining_warnings = sum(len(e) for e in list(warning_patterns.values())[5:])
        lines.append(f"- ... e {remaining} padrão(ões) adicional(is) ({total_remaining_warnings} aviso(s))")

    lines.append("")
    return lines


def _format_insights_section(analysis_result: Dict[str, Any]) -> List[str]:
    """
    Formata secao de insights e recomendacoes do LLM.

    Retorno:
        Lista de linhas markdown para insights
    """
    lines = [
        "## Insights e Recomendacoes",
        "",
    ]

    # Extrai insights e recomendações do resultado da análise
    insights = analysis_result.get("insights", [])
    recommendations = analysis_result.get("recommendations", [])
    root_causes = analysis_result.get("root_causes", [])

    # Causas raiz
    if root_causes:
        lines.extend([
            "### Causas Raiz Identificadas",
            "",
        ])
        for cause in root_causes:
            lines.append(f"- {cause}")
        lines.append("")

    # Insights
    if insights:
        lines.extend([
            "### Insights da Análise",
            "",
        ])
        for insight in insights:
            lines.append(f"- {insight}")
        lines.append("")

    # Recomendações
    if recommendations:
        lines.extend([
            "### Recomendações de Ação",
            "",
        ])
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    # Se não houver nenhuma informação de análise
    if not insights and not recommendations and not root_causes:
        lines.append("*Análise com LLM pendente ou sem resultados adicionais*")
        lines.append("")

    return lines


def _format_metadata_section(metadata: Dict[str, Any]) -> List[str]:
    """
    Formata secao de metadados de execucao.

    Retorno:
        Lista de linhas markdown para metadados
    """
    lines = [
        "---",
        "",
        "## Metadados de Execucao",
        "",
    ]

    # Extrai metadados relevantes
    agent_name = metadata.get("agent_name", "LogAnalyzer AI")
    version = metadata.get("version", "desconhecida")
    file_read_ts = metadata.get("file_read_timestamp", "N/A")
    parse_ts = metadata.get("parse_timestamp", "N/A")
    analysis_ts = metadata.get("analysis_timestamp", "N/A")

    lines.extend([
        f"**Agente:** {agent_name}",
        f"**Versão:** {version}",
        f"**Data de Geração:** {datetime.now().isoformat()}",
        "",
        "### Timestamps de Processamento",
        f"- Arquivo lido: {file_read_ts}",
        f"- Parsing concluído: {parse_ts}",
        f"- Análise concluída: {analysis_ts}",
        "",
    ])

    # Tamanho do arquivo
    file_size = metadata.get("file_size_bytes", 0)
    if file_size > 0:
        size_mb = file_size / (1024 * 1024)
        lines.append(f"**Tamanho do arquivo:** {size_mb:.2f} MB")

    # Linhas do arquivo
    file_lines = metadata.get("file_lines", 0)
    if file_lines > 0:
        lines.append(f"**Total de linhas:** {file_lines}")

    lines.extend([
        "",
        "---",
    ])

    return lines

