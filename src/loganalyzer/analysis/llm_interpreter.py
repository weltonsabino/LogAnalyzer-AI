"""
Integração com LLM para interpretação inteligente de análise de logs.

Fornece funções para chamar LLM e gerar insights baseado em análise.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional, Union
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


def initialize_llm(provider: Optional[str] = None) -> Optional[Union[ChatOpenAI, ChatGroq]]:
    """
    Inicializa cliente LLM com suporte a múltiplos provedores.

    Esta função:
    - Lê provider da variável de ambiente LLM_PROVIDER (padrão: openai)
    - Valida chaves de API apropriadas (OPENAI_API_KEY ou GROQ_API_KEY)
    - Cria instância do provider selecionado
    - Retorna None se nenhuma chave estiver configurada

    Argumentos:
        provider: Provedor LLM (openai ou groq). Se None, lê de LLM_PROVIDER env.

    Retorno:
        Instância ChatOpenAI, ChatGroq ou None se não configurado
    """
    # Determina provedor a usar
    if provider is None:
        # Lê do ambiente, padrão: openai
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # Factory pattern: cria instância baseado no provedor
    if provider == "groq":
        # Inicializa com Groq (grátis)
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            # Chave Groq não configurada, retorna None
            return None

        # Cria instância do Groq
        llm = ChatGroq(
            api_key=api_key,
            model="openai/gpt-oss-120b",  # Modelo Groq gratuito (120B parametros)
            temperature=0.3,  # Mesma temperatura para consistência
            max_tokens=1000,  # Mesmo limite de tokens
        )

        return llm

    elif provider == "openai":
        # Inicializa com OpenAI (GPT-4)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            # API não configurada, retorna None
            return None

        # Cria instância do OpenAI
        llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o-mini",  # Modelo OpenAI rapido e acessivel
            temperature=0.3,  # Baixa temperatura para respostas consistentes
            max_tokens=1000,  # Limita tokens para respostas concisas
        )

        return llm

    else:
        # Provedor desconhecido, retorna None
        return None


def analyze_with_llm(
    errors_found: List[Dict[str, Any]],
    warnings_found: List[Dict[str, Any]],
    critical_events: List[Dict[str, Any]],
    parsed_events: List[Dict[str, Any]],
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Usa LLM para gerar insights e recomendações baseado na análise.

    Esta função:
    - Inicializa LLM (se disponível) com provider selecionado
    - Formata contexto com eventos identificados
    - Chama LLM com prompt estruturado
    - Extrai insights, recomendações e causas raiz
    - Retorna resultados estruturados

    Argumentos:
        errors_found: Lista de erros identificados
        warnings_found: Lista de avisos identificados
        critical_events: Lista de eventos críticos
        parsed_events: Lista completa de eventos parseados
        provider: Provedor LLM (openai ou groq). Padrão: None (lê de env)

    Retorno:
        Dicionário contendo:
        {
            "insights": [lista de insights],
            "recommendations": [lista de recomendações],
            "root_causes": [lista de causas raiz],
            "summary": resumo geral da análise
        }
    """
    # Tenta inicializar LLM com provider especificado
    llm = initialize_llm(provider=provider)

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
        # Se erro ao chamar LLM, retorna análise fallback
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

    # Identifica componentes afetados nas mensagens dos eventos
    all_events = errors_found + warnings_found + critical_events
    all_messages = " ".join(
        event.get("message", "") for event in all_events
    ).lower()

    # Detecta componentes mencionados
    affected_components = []
    component_keywords = {
        "database": ["database", "db", "sql", "connection pool"],
        "cache": ["cache", "redis", "memcached"],
        "memory": ["memory", "heap", "out of memory", "oom"],
        "connection": ["connection", "timeout", "refused"],
        "network": ["network", "dns", "socket"],
    }

    for component, keywords in component_keywords.items():
        if any(kw in all_messages for kw in keywords):
            affected_components.append(component)

    # Insights baseado em contadores
    if len(critical_events) > 0:
        msg = (
            f"Detectados {len(critical_events)} evento(s) crítico(s) "
            "que requerem atenção imediata"
        )
        insights.append(msg)

    if len(errors_found) > 5:
        msg = (
            f"Elevada quantidade de erros ({len(errors_found)}) "
            "sugere problema sistêmico"
        )
        insights.append(msg)

    if affected_components:
        msg = (
            f"Componentes afetados identificados: "
            f"{', '.join(affected_components)}"
        )
        insights.append(msg)
        root_causes.append(
            f"Falha nos componentes: {', '.join(affected_components)}"
        )

    if len(errors_found) > 10:
        root_causes.append("Múltiplos erros indicam falha no componente central")

    if len(warnings_found) > 5:
        msg = (
            f"Muitos avisos ({len(warnings_found)}) "
            "indicam degradação progressiva"
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
