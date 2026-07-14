"""
Integração com LLM para interpretação inteligente de análise de logs.

Fornece funções para chamar LLM e gerar insights baseado em análise.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


def initialize_llm() -> Optional[ChatOpenAI]:
    """
    Inicializa cliente OpenAI para LLM.

    Esta função:
    - Verifica se OPENAI_API_KEY está configurada
    - Cria instância ChatOpenAI com modelo GPT-4 ou GPT-3.5
    - Retorna None se API não estiver configurada

    Retorno:
        Instância ChatOpenAI ou None se não configurado
    """
    # Tenta ler chave de API do ambiente
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # API não configurada, retorna None
        return None

    # Cria instância do LLM
    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4-turbo-preview",  # Usa GPT-4 se disponível
        temperature=0.3,  # Baixa temperatura para respostas consistentes
        max_tokens=1000,  # Limita tokens para respostas concisas
    )

    return llm


def analyze_with_llm(
    errors_found: List[Dict[str, Any]],
    warnings_found: List[Dict[str, Any]],
    critical_events: List[Dict[str, Any]],
    parsed_events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Usa LLM para gerar insights e recomendações baseado na análise.

    Esta função:
    - Inicializa LLM (se disponível)
    - Formata contexto com eventos identificados
    - Chama LLM com prompt estruturado
    - Extrai insights, recomendações e causas raiz
    - Retorna resultados estruturados

    Argumentos:
        errors_found: Lista de erros identificados
        warnings_found: Lista de avisos identificados
        critical_events: Lista de eventos críticos
        parsed_events: Lista completa de eventos parseados

    Retorno:
        Dicionário contendo:
        {
            "insights": [lista de insights],
            "recommendations": [lista de recomendações],
            "root_causes": [lista de causas raiz],
            "summary": resumo geral da análise
        }
    """
    # Tenta inicializar LLM
    llm = initialize_llm()

    # Se LLM não estiver disponível, retorna análise padrão
    if not llm:
        return _generate_fallback_analysis(errors_found, warnings_found, critical_events)

    try:
        # Formata contexto com análise
        ctx = _format_analysis_context(
            errors_found, warnings_found, critical_events, parsed_events
        )

        # Cria prompt estruturado
        prompt_template = ChatPromptTemplate.from_template(
            "Analise os seguintes eventos de log e problemas identificados:\n\n"
            "{analysis_context}\n\n"
            "Forneça uma análise estruturada em JSON com os seguintes campos:\n"
            "- insights: lista de insights principais (máximo 5)\n"
            "- recommendations: lista de recomendações de ação (máximo 5)\n"
            "- root_causes: lista de causas raiz identificadas (máximo 3)\n"
            "- summary: resumo geral da análise em uma frase\n\n"
            "Responda APENAS com JSON válido, sem markdown ou explicações."
        )

        # Formata e invoca LLM
        formatted_prompt = prompt_template.format(analysis_context=ctx)
        response = llm.invoke(formatted_prompt)

        # Extrai conteúdo da resposta
        response_text = response.content.strip()

        # Tenta parsear JSON da resposta
        analysis_result = _parse_llm_response(response_text)
        return analysis_result

    except Exception as e:
        # Se erro ao chamar LLM, retorna análise padrão
        print(f"Aviso: Erro ao chamar LLM: {str(e)}")
        return _generate_fallback_analysis(
            errors_found, warnings_found, critical_events
        )


def _format_analysis_context(
    errors_found: List[Dict[str, Any]],
    warnings_found: List[Dict[str, Any]],
    critical_events: List[Dict[str, Any]],
    parsed_events: List[Dict[str, Any]],
) -> str:
    """
    Formata contexto de análise para enviar ao LLM.

    Retorno:
        String com contexto formatado para análise
    """
    lines = []

    # Resumo geral
    lines.append("## Resumo de Eventos")
    lines.append(f"- Total de eventos: {len(parsed_events)}")
    lines.append(f"- Erros: {len(errors_found)}")
    lines.append(f"- Avisos: {len(warnings_found)}")
    lines.append(f"- Críticos: {len(critical_events)}")
    lines.append("")

    # Eventos críticos
    if critical_events:
        lines.append("## Eventos Críticos Detectados")
        for event in critical_events[:5]:  # Primeiros 5
            msg = event.get("message", "")[:100]
            lines.append(f"- {msg}")
        if len(critical_events) > 5:
            lines.append(f"- ... e mais {len(critical_events) - 5}")
        lines.append("")

    # Padrões de erro
    if errors_found:
        lines.append("## Padrões de Erro")
        error_messages = {}
        for error in errors_found:
            msg = error.get("message", "")[:80]
            error_messages[msg] = error_messages.get(msg, 0) + 1

        for msg, count in list(error_messages.items())[:5]:
            lines.append(f"- ({count}x) {msg}")
        if len(error_messages) > 5:
            lines.append(f"- ... e mais {len(error_messages) - 5} padrões")
        lines.append("")

    # Padrões de aviso
    if warnings_found:
        lines.append("## Padrões de Aviso")
        warning_messages = {}
        for warning in warnings_found:
            msg = warning.get("message", "")[:80]
            warning_messages[msg] = warning_messages.get(msg, 0) + 1

        for msg, count in list(warning_messages.items())[:5]:
            lines.append(f"- ({count}x) {msg}")
        if len(warning_messages) > 5:
            lines.append(f"- ... e mais {len(warning_messages) - 5} padrões")
        lines.append("")

    return "\n".join(lines)


def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parseia resposta do LLM e extrai JSON.

    Retorno:
        Dicionário com análise parseada
    """
    # Tenta extrair JSON da resposta
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

    if not json_match:
        # Se não encontrar JSON, retorna estrutura padrão
        return {
            "insights": ["Análise com LLM não extraiu insights"],
            "recommendations": ["Revisar eventos críticos manualmente"],
            "root_causes": ["Análise automática limitada sem JSON"],
            "summary": "Análise concluída com limitações",
        }

    try:
        # Parseia JSON extraído
        json_str = json_match.group(0)
        analysis = json.loads(json_str)

        # Garante que possui campos obrigatórios
        analysis.setdefault("insights", [])
        analysis.setdefault("recommendations", [])
        analysis.setdefault("root_causes", [])
        analysis.setdefault("summary", "Análise concluída")

        return analysis

    except json.JSONDecodeError:
        # Se erro ao parsear JSON, retorna estrutura padrão
        return {
            "insights": ["Erro ao parsear resposta do LLM"],
            "recommendations": ["Revisar eventos críticos manualmente"],
            "root_causes": ["JSON inválido na resposta"],
            "summary": "Análise incompleta",
        }


def _generate_fallback_analysis(
    errors_found: List[Dict[str, Any]],
    warnings_found: List[Dict[str, Any]],
    critical_events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Gera análise padrão quando LLM não está disponível.

    Retorno:
        Dicionário com análise heurística
    """
    # Constrói análise heurística
    insights = []
    recommendations = []
    root_causes = []

    # Insights baseado em contadores
    if len(critical_events) > 0:
        msg = (
            f"Detectados {len(critical_events)} evento(s) crítico(s) "
            "que requerem atenção imediata"
        )
        insights.append(msg)

    if len(errors_found) > 10:
        msg = (
            f"Elevada quantidade de erros ({len(errors_found)}) "
            "sugere problema sistêmico"
        )
        insights.append(msg)
        msg = "Múltiplos erros podem indicar falha no componente central"
        root_causes.append(msg)

    if len(warnings_found) > 20:
        msg = (
            f"Muitos avisos ({len(warnings_found)}) "
            "indicam situações anormais"
        )
        insights.append(msg)

    # Recomendações padrão
    if len(critical_events) > 0:
        recommendations.append("Investigar eventos críticos imediatamente")

    if len(errors_found) > 0:
        recommendations.append("Revisar padrões de erro e corrigir raiz do problema")

    if len(warnings_found) > 0:
        recommendations.append("Monitorar avisos e ajustar configurações se necessário")

    recommendations.append("Implementar alertas para eventos críticos futuros")

    return {
        "insights": insights if insights else [
            "Análise heurística: sem problemas graves detectados"
        ],
        "recommendations": recommendations,
        "root_causes": root_causes if root_causes else [
            "Análise heurística ativada (LLM não disponível)"
        ],
        "summary": "Análise com modo fallback (sem LLM)",
    }

