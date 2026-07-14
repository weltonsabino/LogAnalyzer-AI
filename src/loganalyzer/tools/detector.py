"""
Ferramenta de detecção de padrões para o LogAnalyzer AI.

Fornece função para analisar eventos de log e identificar padrões, erros e críticos.
"""

import re
from typing import List, Dict, Any
from collections import defaultdict


def detect_patterns(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analisa eventos de log para detectar padrões, erros e eventos críticos.

    Esta ferramenta:
    - Classifica eventos por level (ERROR, WARNING, INFO, DEBUG)
    - Identifica padrões recorrentes
    - Detecta eventos críticos/severos
    - Agrupa eventos similares

    Argumentos:
        events: Lista de eventos parseados

    Retorno:
        Dicionário contendo:
        {
            "errors": List[Dict] - eventos com level ERROR,
            "warnings": List[Dict] - eventos com level WARNING,
            "critical": List[Dict] - eventos críticos detectados
        }
    """
    errors = []
    warnings = []
    critical = []

    # Agrupa eventos por nível
    errors_by_message = defaultdict(list)
    warnings_by_message = defaultdict(list)

    for event in events:
        level = event.get("level", "UNKNOWN")

        if level == "ERROR":
            errors.append(event)
            # Agrupa erros similares por message
            msg_key = _get_message_pattern(event.get("message", ""))
            errors_by_message[msg_key].append(event)

        elif level == "WARNING":
            warnings.append(event)
            # Agrupa avisos similares
            msg_key = _get_message_pattern(event.get("message", ""))
            warnings_by_message[msg_key].append(event)

    # Detecta eventos críticos
    critical = _detect_critical_events(errors, warnings, errors_by_message)

    return {
        "errors": errors,
        "warnings": warnings,
        "critical": critical,
    }


def _get_message_pattern(message: str) -> str:
    """
    Extrai padrão da mensagem para agrupamento.

    Remove números e valores específicos para detectar padrões similares.

    Argumentos:
        message: Mensagem de log

    Retorno:
        Padrão simplificado da mensagem
    """
    # Remove números (IDs, portas, etc)
    pattern = re.sub(r'\d+', 'NUM', message)

    # Remove paths/URLs
    pattern = re.sub(r'[/\\][^\s]+', 'PATH', pattern)

    # Remove IPs
    pattern = re.sub(r'\d+\.\d+\.\d+\.\d+', 'IP', pattern)

    return pattern.strip()


def _detect_critical_events(
    errors: List[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
    errors_by_message: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Detecta eventos críticos baseado em heurísticas.

    Critérios de criticidade:
    - Erros com keywords críticas (crash, fatal, critical)
    - Erros recorrentes (>2 ocorrências)
    - Padrões de cascata (múltiplos erros em sequência)

    Argumentos:
        errors: Lista de erros
        warnings: Lista de avisos (não usado atualmente)
        errors_by_message: Erros agrupados por padrão de mensagem

    Retorno:
        Lista de eventos críticos detectados
    """
    critical = []
    critical_keywords = ["crash", "fatal", "critical", "panic", "exception", "failed"]

    for error in errors:
        message = error.get("message", "").lower()

        # Detecta keywords críticas
        if any(keyword in message for keyword in critical_keywords):
            error["critical_reason"] = "contém keyword crítica"
            critical.append(error)

    # Detecta padrões recorrentes (múltiplas ocorrências)
    for pattern, events in errors_by_message.items():
        if len(events) > 2:
            # Marca eventos de padrão recorrente como críticos
            for event in events[:len(events) - 1]:  # Marca exceto o último
                if event not in critical:
                    event["critical_reason"] = f"padrão recorrente ({len(events)} ocorrências)"
                    critical.append(event)

    # Remove duplicatas mantendo ordem
    seen = set()
    unique_critical = []
    for event in critical:
        event_id = event.get("line_number")
        if event_id not in seen:
            seen.add(event_id)
            unique_critical.append(event)

    return unique_critical
