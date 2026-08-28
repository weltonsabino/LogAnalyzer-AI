"""
Testes para Task #30: LangGraph Avançado - Ramificação + Paralelização.

Valida:
- Roteamento por severidade
- Nós especializados (HIGH, MEDIUM, LOW)
- Análise paralela
- Integração completa
"""

import pytest
import inspect
from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.agent import (
    route_by_severity,
    create_agent_graph,
)
from src.loganalyzer.nodes import (
    analyze_high_severity_node,
    analyze_medium_severity_node,
    analyze_low_severity_node,
    analyze_patterns_node_parallel,
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def state_high_severity():
    """Cria estado com eventos de alta severidade"""
    return LogAnalysisState(
        file_path="test.log",
        file_content="ERROR: conexão perdida\nCRITICAL: banco de dados offline",
        parsed_events=[
            {"level": "ERROR", "message": "conexão perdida", "timestamp": "2026-08-20T10:00:00"},
            {"level": "CRITICAL", "message": "banco de dados offline", "timestamp": "2026-08-20T10:01:00"},
            {"level": "INFO", "message": "iniciando", "timestamp": "2026-08-20T09:59:00"},
        ],
        errors_found=[
            {"message": "conexão perdida", "line": 1},
        ],
        warnings_found=[],
        critical_events=[
            {"message": "banco de dados offline", "line": 2},
        ],
        analysis_result={},
        report="",
        metadata={"start_time": None, "version": "0.0.1", "agent_name": "LogAnalyzer AI"},
        llm_provider=None,
        is_valid=True,
        error_message=None,
        validation_error=None,
        parsing_error=None,
        detection_error=None,
        analysis_error=None,
        severity_routes={},
    )


@pytest.fixture
def state_medium_severity():
    """Cria estado com eventos de severidade média"""
    return LogAnalysisState(
        file_path="test.log",
        file_content="WARNING: timeout detectado\nWARN: retry necessário",
        parsed_events=[
            {"level": "WARNING", "message": "timeout detectado", "timestamp": "2026-08-20T10:00:00"},
            {"level": "WARN", "message": "retry necessário", "timestamp": "2026-08-20T10:01:00"},
            {"level": "INFO", "message": "operação iniciada", "timestamp": "2026-08-20T09:59:00"},
        ],
        errors_found=[],
        warnings_found=[
            {"message": "timeout detectado", "line": 1},
            {"message": "retry necessário", "line": 2},
        ],
        critical_events=[],
        analysis_result={},
        report="",
        metadata={"start_time": None, "version": "0.0.1", "agent_name": "LogAnalyzer AI"},
        llm_provider=None,
        is_valid=True,
        error_message=None,
        validation_error=None,
        parsing_error=None,
        detection_error=None,
        analysis_error=None,
        severity_routes={},
    )


@pytest.fixture
def state_low_severity():
    """Cria estado com eventos de baixa severidade"""
    return LogAnalysisState(
        file_path="test.log",
        file_content="INFO: sistema iniciado\nDEBUG: thread 1 executando",
        parsed_events=[
            {"level": "INFO", "message": "sistema iniciado", "timestamp": "2026-08-20T10:00:00"},
            {"level": "DEBUG", "message": "thread 1 executando", "timestamp": "2026-08-20T10:01:00"},
            {"level": "TRACE", "message": "função X chamada", "timestamp": "2026-08-20T10:02:00"},
        ],
        errors_found=[],
        warnings_found=[],
        critical_events=[],
        analysis_result={},
        report="",
        metadata={"start_time": None, "version": "0.0.1", "agent_name": "LogAnalyzer AI"},
        llm_provider=None,
        is_valid=True,
        error_message=None,
        validation_error=None,
        parsing_error=None,
        detection_error=None,
        analysis_error=None,
        severity_routes={},
    )


# ============================================
# TESTES DE ROTEAMENTO
# ============================================

def test_route_high_severity_events(state_high_severity):
    """Valida roteamento para eventos de alta severidade"""
    # Executa roteamento
    route = route_by_severity(state_high_severity)
    
    # Valida resultado
    assert route == "analyze_high_severity"
    assert state_high_severity["severity_routes"]["HIGH"] > 0
    assert state_high_severity["severity_routes"]["MEDIUM"] == 0


def test_route_medium_severity_events(state_medium_severity):
    """Valida roteamento para eventos de severidade média"""
    # Executa roteamento
    route = route_by_severity(state_medium_severity)
    
    # Valida resultado
    assert route == "analyze_medium_severity"
    assert state_medium_severity["severity_routes"]["MEDIUM"] > 0
    assert state_medium_severity["severity_routes"]["HIGH"] == 0


def test_route_low_severity_events(state_low_severity):
    """Valida roteamento para eventos de baixa severidade"""
    # Executa roteamento
    route = route_by_severity(state_low_severity)
    
    # Valida resultado
    assert route == "analyze_low_severity"
    assert state_low_severity["severity_routes"]["LOW"] > 0
    assert state_low_severity["severity_routes"]["HIGH"] == 0


# ============================================
# TESTES DE NÓS ESPECIALIZADOS
# ============================================

def test_analyze_high_severity_node(state_high_severity):
    """Valida nó de análise de alta severidade"""
    # Executa nó
    result_state = analyze_high_severity_node(state_high_severity)
    
    # Valida resultado
    assert result_state["is_valid"] is True
    assert result_state["analysis_result"]["severity_level"] == "HIGH"
    assert result_state["analysis_result"]["urgency"] == "IMEDIATA"
    assert "severity_analysis" in result_state["metadata"]


def test_analyze_medium_severity_node(state_medium_severity):
    """Valida nó de análise de severidade média"""
    # Executa nó
    result_state = analyze_medium_severity_node(state_medium_severity)
    
    # Valida resultado
    assert result_state["is_valid"] is True
    assert result_state["analysis_result"]["severity_level"] == "MEDIUM"
    assert result_state["analysis_result"]["urgency"] == "NORMAL"
    assert "severity_analysis" in result_state["metadata"]


def test_analyze_low_severity_node(state_low_severity):
    """Valida nó de análise de baixa severidade"""
    # Executa nó
    result_state = analyze_low_severity_node(state_low_severity)
    
    # Valida resultado
    assert result_state["is_valid"] is True
    assert result_state["analysis_result"]["severity_level"] == "LOW"
    assert result_state["analysis_result"]["urgency"] == "BAIXA"
    assert "severity_analysis" in result_state["metadata"]


# ============================================
# TESTES DE PARALELIZAÇÃO
# ============================================

def test_analyze_patterns_parallel_structure(state_high_severity):
    """Valida estrutura de nó paralelo (wrapper síncrono)"""
    # Valida que nó existe e é callable
    assert callable(analyze_patterns_node_parallel)
    
    # Nota: Testes de execução async requerem pytest-asyncio
    # Testamos a estrutura do nó aqui


def test_parallel_analyzer_imports():
    """Valida que nó paralelo foi importado corretamente"""
    # Valida que função é corrotina
    assert inspect.iscoroutinefunction(analyze_patterns_node_parallel)


# ============================================
# TESTES DE INTEGRAÇÃO
# ============================================

def test_langgraph_routing_integration():
    """Valida fluxo completo com roteamento"""
    # Cria agente
    agent = create_agent_graph()
    
    # Valida que agente foi compilado
    assert agent is not None
    
    # Valida que nós existem
    # Nota: Esta é uma validação básica, execução completa é teste de E2E


def test_multiple_severity_levels_mixed():
    """Valida processamento de múltiplos níveis em um log"""
    # Cria estado com mix de severidades
    state = LogAnalysisState(
        file_path="test.log",
        file_content="mix de eventos",
        parsed_events=[
            {"level": "CRITICAL", "message": "falha crítica", "timestamp": "2026-08-20T10:00:00"},
            {"level": "WARNING", "message": "aviso", "timestamp": "2026-08-20T10:01:00"},
            {"level": "INFO", "message": "info", "timestamp": "2026-08-20T10:02:00"},
        ],
        errors_found=[],
        warnings_found=[],
        critical_events=[],
        analysis_result={},
        report="",
        metadata={"start_time": None, "version": "0.0.1", "agent_name": "LogAnalyzer AI"},
        llm_provider=None,
        is_valid=True,
        error_message=None,
        validation_error=None,
        parsing_error=None,
        detection_error=None,
        analysis_error=None,
        severity_routes={},
    )
    
    # Roteia - deve priorizar o mais alto
    route = route_by_severity(state)
    
    # Valida que roteou para HIGH (mais crítico)
    assert route == "analyze_high_severity"
    assert state["severity_routes"]["HIGH"] > 0


def test_severity_routes_tracking():
    """Valida rastreamento de contadores de severidade"""
    # Cria estado
    state = LogAnalysisState(
        file_path="test.log",
        file_content="tracking",
        parsed_events=[
            {"level": "ERROR", "message": "erro 1", "timestamp": "2026-08-20T10:00:00"},
            {"level": "ERROR", "message": "erro 2", "timestamp": "2026-08-20T10:01:00"},
            {"level": "WARNING", "message": "aviso", "timestamp": "2026-08-20T10:02:00"},
        ],
        errors_found=[],
        warnings_found=[],
        critical_events=[],
        analysis_result={},
        report="",
        metadata={"start_time": None, "version": "0.0.1", "agent_name": "LogAnalyzer AI"},
        llm_provider=None,
        is_valid=True,
        error_message=None,
        validation_error=None,
        parsing_error=None,
        detection_error=None,
        analysis_error=None,
        severity_routes={},
    )
    
    # Roteia
    route_by_severity(state)
    
    # Valida contadores
    assert state["severity_routes"]["HIGH"] == 2
    assert state["severity_routes"]["MEDIUM"] == 1
    assert state["severity_routes"]["LOW"] == 0
