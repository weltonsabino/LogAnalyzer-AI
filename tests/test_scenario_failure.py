"""
Testes para Task #31: Segundo Cenário de Uso - Risco/Falha.

Valida processamento de logs com degradação progressiva, falhas críticas
e anomalias, demonstrando comportamento realista do LogAnalyzer AI.
"""

import os
import pytest
from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.agent import create_agent_graph, get_initial_state

# Raiz do projeto (resolve independente do cwd)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def failure_log_path():
    """Caminho absoluto do log de cenário de falha"""
    return os.path.join(PROJECT_ROOT, "tests", "fixtures", "failure_logs", "scenario_failure.log")


# ============================================
# TESTES DE CENÁRIO DE FALHA
# ============================================

def test_failure_log_processing(failure_log_path):
    """Processa log de falha e valida saída estruturada"""
    # Arranjo: Carrega log de falha
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    
    # Ato: Executa agente
    result = agent.invoke(initial_state)
    
    # Assert: Valida resultado
    assert result["is_valid"] is True, "Estado deve ser válido após processamento"
    assert result["file_path"] == failure_log_path
    assert len(result["file_content"]) > 0, "Conteúdo do arquivo deve ser carregado"
    assert len(result["parsed_events"]) > 0, "Eventos devem ser parseados"
    assert result["report"] != "", "Relatório deve ser gerado"


def test_severity_routing_in_failure_scenario(failure_log_path):
    """Valida que roteamento por severidade funciona no cenário de falha"""
    # Arranjo
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    
    # Ato
    result = agent.invoke(initial_state)
    
    # Assert: Deve rotear para analyze_high_severity (há CRITICAL)
    assert result["is_valid"] is True
    assert len(result["critical_events"]) > 0, "Deve ter eventos críticos"
    
    # Assert: severity_routes deve ter contagem HIGH > 0
    assert "severity_routes" in result
    assert result["severity_routes"]["HIGH"] > 0, "Deve ter roteamento HIGH"
    assert result["analysis_result"]["severity_level"] == "HIGH"
    assert result["analysis_result"]["urgency"] == "IMEDIATA"


def test_failure_scenario_report_generation(failure_log_path):
    """Valida geração de relatório para cenário de falha"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: Relatório deve ser markdown válido
    assert result["report"] is not None
    assert len(result["report"]) > 0, "Relatório deve ter conteúdo"
    assert "# " in result["report"], "Relatório deve ter header markdown"
    
    # Assert: Relatório deve mencionar eventos críticos
    report_lower = result["report"].lower()
    assert "crítico" in report_lower or "critical" in report_lower or "erro" in report_lower, \
        "Relatório deve mencionar eventos críticos"
    
    # Assert: Relatório deve conter recomendações
    assert "recomendação" in report_lower or "recommendation" in report_lower or "ação" in report_lower, \
        "Relatório deve conter recomendações"


def test_failure_log_events_detection(failure_log_path):
    """Valida detecção de eventos no log de falha"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: Deve ter quantidade esperada de eventos
    assert len(result["parsed_events"]) >= 40, "Deve ter mínimo 40 eventos parseados"
    assert len(result["errors_found"]) >= 8, "Deve ter 8+ erros encontrados"
    assert len(result["critical_events"]) >= 5, "Deve ter 5+ eventos críticos"
    assert len(result["warnings_found"]) >= 10, "Deve ter 10+ avisos"


def test_failure_scenario_analysis_result(failure_log_path):
    """Valida analysis_result estruturado para cenário de falha"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: analysis_result deve ter estrutura esperada
    assert "severity_level" in result["analysis_result"]
    assert result["analysis_result"]["severity_level"] == "HIGH"
    
    # Assert: Deve ter insights e recomendações
    assert "insights" in result["analysis_result"], "Deve ter insights"
    assert "recommendations" in result["analysis_result"], "Deve ter recomendações"
    
    # Assert: Deve ter conteúdo real
    assert isinstance(result["analysis_result"]["insights"], list)
    assert len(result["analysis_result"]["insights"]) > 0, "Deve ter pelo menos 1 insight"
    assert len(result["analysis_result"]["recommendations"]) >= 2, "Deve ter 2+ recomendações"


def test_parallel_analysis_in_failure_scenario(failure_log_path):
    """Valida análise paralela no cenário de falha"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: Deve ter análise paralela
    assert "parallel_patterns" in result["analysis_result"], \
        "Deve conter parallel_patterns da análise assíncrona"
    
    parallel = result["analysis_result"]["parallel_patterns"]
    
    # Assert: Deve ter frequência de níveis
    assert "frequency_by_level" in parallel, "Deve ter frequency_by_level"
    assert isinstance(parallel["frequency_by_level"], dict)
    assert len(parallel["frequency_by_level"]) > 0, "frequency_by_level deve ter dados"
    
    # Valida que tem múltiplos níveis
    levels_found = list(parallel["frequency_by_level"].keys())
    assert len(levels_found) >= 2, f"Deve ter múltiplos níveis de log. Encontrado: {levels_found}"


def test_failure_scenario_metadata(failure_log_path):
    """Valida metadados completos do cenário de falha"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: Metadados devem estar preenchidos
    metadata = result["metadata"]
    assert "parsed_events_count" in metadata
    assert metadata["parsed_events_count"] >= 40
    
    assert "errors_count" in metadata
    assert metadata["errors_count"] >= 8
    
    assert "critical_count" in metadata
    assert metadata["critical_count"] >= 5
    
    assert "severity_analysis" in metadata
    assert metadata["severity_analysis"] == "HIGH"


def test_failure_scenario_degradation_pattern(failure_log_path):
    """Valida que cenário captura padrão de degradação"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: Deve ter padrão esperado
    # - Começa com INFO (startup)
    # - Depois WARNING (degradação)
    # - Depois ERROR (falha)
    # - Depois CRITICAL (parada)
    
    events = result["parsed_events"]
    
    # Pega primeiros e últimos eventos
    first_event_level = events[0].get("level", "").upper()
    last_event_level = events[-1].get("level", "").upper()
    
    # Valida progressão esperada
    assert first_event_level in ["INFO", "WARNING"], "Deve começar com operação normal"
    assert last_event_level in ["CRITICAL", "ERROR"], "Deve terminar com evento de erro"
    
    # Valida que há progressão
    critical_count = result["metadata"]["critical_count"]
    error_count = result["metadata"]["errors_count"]
    warning_count = result["metadata"]["warnings_count"]
    
    # Degradação: mais warnings que info, mais erros que warnings, críticos presentes
    assert critical_count > 0, "Deve ter eventos críticos"
    assert error_count > warning_count / 2, "Deve ter erros significativos"


def test_failure_scenario_root_cause_analysis(failure_log_path):
    """Valida que análise identifica causa raiz"""
    # Arranjo e Ato
    initial_state = get_initial_state(failure_log_path)
    agent = create_agent_graph()
    result = agent.invoke(initial_state)
    
    # Assert: Análise deve mencionar componentes que falharam
    analysis_text = str(result["analysis_result"]).lower()
    
    # Deve identificar componentes afetados
    has_component_mention = (
        "database" in analysis_text or
        "cache" in analysis_text or
        "memory" in analysis_text or
        "connection" in analysis_text
    )
    
    assert has_component_mention, \
        "Análise deve identificar componentes que falharam"
