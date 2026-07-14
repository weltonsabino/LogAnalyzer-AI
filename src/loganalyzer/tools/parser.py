"""
Ferramenta de parsing de logs para o LogAnalyzer AI.

Fornece função para fazer parsing de linhas de log em múltiplos formatos.
"""

import json
import re
from typing import List, Dict, Any


def parse_log_content(content: str) -> List[Dict[str, Any]]:
    """
    Faz parsing do conteúdo de log e extrai eventos individuais.

    Esta ferramenta:
    - Separa conteúdo em linhas
    - Detecta e parsea múltiplos formatos (JSON, texto, padrão)
    - Extrai timestamp, level, message de cada linha
    - Retorna lista de eventos estruturados

    Argumentos:
        content: Conteúdo completo do arquivo de log

    Retorno:
        Lista de eventos parseados com estrutura:
        {
            "line_number": int,
            "timestamp": str (ou None se não detectado),
            "level": str (ERROR, WARNING, INFO, DEBUG, UNKNOWN),
            "message": str,
            "raw_line": str
        }
    """
    events = []
    lines = content.split('\n')

    for line_number, line in enumerate(lines, start=1):
        # Ignora linhas vazias
        if not line.strip():
            continue

        # Tenta parsear como JSON
        json_event = _parse_json_line(line, line_number)
        if json_event:
            events.append(json_event)
            continue

        # Tenta parsear com padrão regex comum
        regex_event = _parse_regex_line(line, line_number)
        if regex_event:
            events.append(regex_event)
            continue

        # Fallback: linha de texto puro
        fallback_event = _parse_text_line(line, line_number)
        events.append(fallback_event)

    return events


def _parse_json_line(line: str, line_number: int) -> Dict[str, Any] | None:
    """
    Tenta parsear linha como JSON estruturado.

    Retorno:
        Evento parseado ou None se não for JSON válido
    """
    try:
        data = json.loads(line)

        # Extrai campos relevantes de JSON
        return {
            "line_number": line_number,
            "timestamp": data.get("timestamp") or data.get("time") or data.get("ts"),
            "level": _normalize_level(data.get("level") or data.get("severity") or "UNKNOWN"),
            "message": data.get("message") or data.get("msg") or str(data),
            "raw_line": line,
        }
    except (json.JSONDecodeError, ValueError):
        return None


def _parse_regex_line(line: str, line_number: int) -> Dict[str, Any] | None:
    """
    Tenta parsear linha com padrão regex comum.

    Suporta formatos como:
    - [2026-07-09 10:30:45] [ERROR] Connection timeout
    - 2026-07-09 10:30:45 ERROR: Connection timeout
    - ERROR - Connection timeout at module.py:45

    Retorno:
        Evento parseado ou None se não corresponder
    """
    # Padrão 1: [TIMESTAMP] [LEVEL] MESSAGE
    pattern1 = r'\[?([\d\-\s:\.]+)\]?\s*\[?([A-Z]+)\]?\s+(.+)$'
    match = re.match(pattern1, line)

    if match:
        timestamp, level, message = match.groups()
        return {
            "line_number": line_number,
            "timestamp": timestamp.strip() if timestamp else None,
            "level": _normalize_level(level.strip() if level else "UNKNOWN"),
            "message": message.strip() if message else "",
            "raw_line": line,
        }

    # Padrão 2: LEVEL - MESSAGE
    pattern2 = r'^([A-Z]+)\s*-\s+(.+)$'
    match = re.match(pattern2, line)

    if match:
        level, message = match.groups()
        return {
            "line_number": line_number,
            "timestamp": None,
            "level": _normalize_level(level.strip()),
            "message": message.strip(),
            "raw_line": line,
        }

    return None


def _parse_text_line(line: str, line_number: int) -> Dict[str, Any]:
    """
    Parseia linha como texto puro, detectando keywords.

    Retorno:
        Evento parseado com detecção heurística de level
    """
    # Detecta level por keywords na mensagem
    level = "UNKNOWN"
    line_upper = line.upper()

    if any(keyword in line_upper for keyword in ["ERROR", "CRITICAL", "FAIL", "EXCEPTION"]):
        level = "ERROR"
    elif any(keyword in line_upper for keyword in ["WARN", "WARNING"]):
        level = "WARNING"
    elif any(keyword in line_upper for keyword in ["INFO", "INFORMATION"]):
        level = "INFO"
    elif any(keyword in line_upper for keyword in ["DEBUG", "TRACE"]):
        level = "DEBUG"

    return {
        "line_number": line_number,
        "timestamp": None,
        "level": level,
        "message": line.strip(),
        "raw_line": line,
    }


def _normalize_level(level: str) -> str:
    """
    Normaliza nomes de level para padrão uniforme.

    Argumentos:
        level: Nome do nível do log (pode variar)

    Retorno:
        Level normalizado (ERROR, WARNING, INFO, DEBUG, UNKNOWN)
    """
    level = level.upper().strip()

    # Mapeamento de variações
    if level in ["ERROR", "ERR", "E", "EXCEPTION", "FAIL", "FAILURE", "CRITICAL", "CRIT"]:
        return "ERROR"
    if level in ["WARN", "WARNING", "W"]:
        return "WARNING"
    if level in ["INFO", "I", "INFORMATION"]:
        return "INFO"
    if level in ["DEBUG", "D", "TRACE", "VERBOSE"]:
        return "DEBUG"
    return "UNKNOWN"
