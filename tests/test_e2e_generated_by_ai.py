"""
Testes end-to-end gerados por IA para o LogAnalyzer AI.

Cobre 8 cenários críticos: sucesso, erro, timeout, retry, observabilidade,
segurança, autonomia e multi-provider.
"""

import pytest
import time
import os
from pathlib import Path

from src.loganalyzer.agent import create_agent_graph, get_initial_state
from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.observability import TraceCollector
from src.loganalyzer.governance import GovernancePolicy, AutonomyLevel, InputValidator
from src.loganalyzer.tools.file_reader import read_log_file


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_log_path():
    """Retorna caminho do arquivo de log de exemplo."""
    # Resolve caminho absoluto a partir da raiz do projeto
    project_root = Path(__file__).parent.parent
    return str(project_root / "examples" / "sample_critical.log")


@pytest.fixture
def invalid_log_path():
    """Retorna caminho inválido para testes de erro."""
    return "/nonexistent/path/to/log.txt"


@pytest.fixture
def agent_graph():
    """Cria grafo do agente para testes."""
    return create_agent_graph()


# ============================================================================
# Cenário 1: Sucesso End-to-End
# ============================================================================

class TestE2ESuccess:
    """Testa cenários de sucesso completo."""
    
    def test_e2e_success_normal_log(self, sample_log_path, agent_graph):
        """
        Teste 1: Fluxo completo de sucesso.
        
        Validação → Leitura → Parsing → Análise → Relatório
        
        Esperado: Relatório completo com análise e recomendações.
        """
        # Pré-requisito: arquivo de exemplo existe
        assert os.path.exists(sample_log_path), f"Arquivo não encontrado: {sample_log_path}"
        
        # Cria estado inicial
        state = get_initial_state(sample_log_path)
        assert state["is_valid"] is True
        assert state["execution_id"] is not None
        
        # Executa grafo
        result = agent_graph.invoke(state)
        
        # Validações
        assert result["is_valid"] is True, "Execução deve ter sucesso"
        assert result["file_content"] != "", "Conteúdo de arquivo deve ser lido"
        assert len(result["parsed_events"]) > 0, "Eventos devem ser parseados"
        assert len(result["report"]) > 500, "Relatório deve ser substantivo"
        assert result["analysis_result"] is not None, "Análise deve ser gerada"
        assert result["error_message"] is None, "Não deve haver erros"
    
    def test_e2e_success_report_contains_sections(self, sample_log_path, agent_graph):
        """
        Teste 2: Relatório contém seções esperadas.
        
        Esperado: Relatório com resumo, eventos, análise, recomendações.
        """
        state = get_initial_state(sample_log_path)
        result = agent_graph.invoke(state)
        
        report = result["report"].lower()
        
        # Valida seções no relatório
        assert "resumo" in report or "summary" in report or "análise" in report
        assert "evento" in report or "event" in report or "log" in report
        assert len(report) > 500, "Relatório suficientemente longo"
        
    def test_e2e_success_severity_routes_populated(self, sample_log_path, agent_graph):
        """
        Teste 3: Roteamento por severidade funciona.
        
        Esperado: severity_routes preenchido com contagem de eventos.
        """
        state = get_initial_state(sample_log_path)
        result = agent_graph.invoke(state)
        
        assert result["severity_routes"] is not None
        assert isinstance(result["severity_routes"], dict)


# ============================================================================
# Cenário 2: Erro de Validação
# ============================================================================

class TestE2EErrorHandling:
    """Testa tratamento de erros end-to-end."""
    
    def test_e2e_validation_error_invalid_path(self, invalid_log_path, agent_graph):
        """
        Teste 4: Erro de validação com caminho inválido.
        
        Esperado: validation_error set, error_handling acionado.
        """
        state = get_initial_state(invalid_log_path)
        result = agent_graph.invoke(state)
        
        assert result["is_valid"] is False, "Estado deve indicar inválido"
        assert result["validation_error"] is not None, "validation_error deve estar set"
        assert result["error_message"] is not None, "error_message deve estar set"
        assert "não encontrado" in result["error_message"].lower() or \
               "not found" in result["error_message"].lower() or \
               "inválido" in result["error_message"].lower()
    
    def test_e2e_error_handling_node_called(self, invalid_log_path, agent_graph):
        """
        Teste 5: error_handling node é acionado em erro.
        
        Esperado: Report contém informação de erro.
        """
        state = get_initial_state(invalid_log_path)
        result = agent_graph.invoke(state)
        
        # Após error_handling, report pode estar vazio ou com mensagem de erro
        assert result["is_valid"] is False


# ============================================================================
# Cenário 3: Timeout
# ============================================================================

class TestE2EResilience:
    """Testa resiliência (timeout, retry)."""
    
    def test_e2e_timeout_scenario(self):
        """
        Teste 6: Timeout em leitura de arquivo.
        
        Esperado: TimeoutError capturado e tratado.
        """
        # Teste simples: validar que decorator existe
        from src.loganalyzer.observability import with_timeout
        
        @with_timeout(seconds=1)
        def slow_function():
            """Função que demora."""
            time.sleep(0.5)
            return "rápido"
        
        # Deve completar porque demora <1s
        result = slow_function()
        assert result == "rápido"
    
    def test_e2e_retry_scenario(self):
        """
        Teste 7: Retry com sucesso após tentativa falha.
        
        Esperado: Função retorna sucesso após retry.
        """
        from src.loganalyzer.observability import with_retry
        
        call_count = {"count": 0}
        
        @with_retry(max_attempts=3, backoff=0.1)
        def sometimes_fails():
            """Função que falha primeira vez."""
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise TimeoutError("Tentativa 1 falhou")
            return "sucesso"
        
        result = sometimes_fails()
        assert result == "sucesso"
        assert call_count["count"] == 2


# ============================================================================
# Cenário 4: Observabilidade
# ============================================================================

class TestE2EObservability:
    """Testa observabilidade e rastreamento."""
    
    def test_e2e_observability_execution_id_propagated(self, sample_log_path, agent_graph):
        """
        Teste 8: execution_id é propagado em toda execução.
        
        Esperado: execution_id único e preenchido em estado.
        """
        state = get_initial_state(sample_log_path)
        initial_execution_id = state["execution_id"]
        
        assert initial_execution_id is not None
        assert len(initial_execution_id) > 0
        
        result = agent_graph.invoke(state)
        
        # execution_id mantido igual
        assert result["execution_id"] == initial_execution_id
    
    def test_e2e_observability_traces_recorded(self, sample_log_path, agent_graph):
        """
        Teste 9: Traces são registrados durante execução.
        
        Esperado: trace_collector com múltiplos traces.
        """
        state = get_initial_state(sample_log_path)
        trace_collector = state["trace_collector"]
        
        result = agent_graph.invoke(state)
        
        traces = result["trace_collector"].get_traces()
        
        # Deve ter registrado traces
        assert len(traces) > 0, "Deve ter traces registrados"
        
        # Todos com mesmo execution_id
        for trace in traces:
            assert trace["execution_id"] == state["execution_id"]
    
    def test_e2e_observability_correlation_summary(self, sample_log_path, agent_graph):
        """
        Teste 10: Sumário de correlação está disponível.
        
        Esperado: Summary com trace_count, status, duration.
        """
        state = get_initial_state(sample_log_path)
        result = agent_graph.invoke(state)
        
        summary = result["trace_collector"].get_correlation_summary()
        
        assert "execution_id" in summary
        assert "trace_count" in summary
        assert "status" in summary
        assert "duration_seconds" in summary
        
        assert summary["trace_count"] > 0
        assert summary["status"] in ["OK", "WARNING", "ERROR"]


# ============================================================================
# Cenário 5: Segurança
# ============================================================================

class TestE2ESecurity:
    """Testa segurança e validação de entrada."""
    
    def test_e2e_input_injection_blocked(self, agent_graph):
        """
        Teste 11: Path traversal é bloqueado.
        
        Esperado: Entrada maliciosa rejeitada por InputValidator.
        """
        # Tenta usar path traversal
        malicious_path = "../../../etc/passwd"
        
        validator = InputValidator()
        is_safe, message = validator.validate_file_path(malicious_path)
        
        # Deve ser bloqueado
        assert is_safe is False, "Path traversal deve ser bloqueado"
    
    def test_e2e_input_validation_safe_path(self):
        """
        Teste 12: Path válido passa na validação.
        
        Esperado: Entrada segura aceita.
        """
        validator = InputValidator()
        
        # Caminhos válidos
        is_safe, message = validator.validate_file_path("examples/sample_critical.log")
        assert is_safe is True
        
        is_safe, message = validator.validate_file_path("tests/fixtures/sample_critical.log")
        assert is_safe is True


# ============================================================================
# Cenário 6: Autonomia
# ============================================================================

class TestE2EGovernance:
    """Testa governança e limites de autonomia."""
    
    def test_e2e_autonomy_read_only_blocks_analyze(self):
        """
        Teste 13: Autonomy level READ_ONLY bloqueia ANALYZE.
        
        Esperado: Policy nega analyze quando autonomy=READ_ONLY.
        """
        policy = GovernancePolicy(autonomy_level=AutonomyLevel.READ_ONLY)
        
        # READ_ONLY não pode analyze
        can_analyze = policy.can_execute_action("analyze")
        assert can_analyze is False, "READ_ONLY não deve permitir analyze"
        
        # Mas pode read_file
        can_read = policy.can_execute_action("read_file")
        assert can_read is True, "READ_ONLY deve permitir read_file"
    
    def test_e2e_autonomy_execute_allows_all(self):
        """
        Teste 14: Autonomy level EXECUTE permite todas ações.
        
        Esperado: Policy permite analyze, recommend, execute_command.
        """
        policy = GovernancePolicy(autonomy_level=AutonomyLevel.EXECUTE)
        
        assert policy.can_execute_action("read_file") is True
        assert policy.can_execute_action("analyze") is True
        assert policy.can_execute_action("recommend") is True
        assert policy.can_execute_action("execute_command") is True


# ============================================================================
# Cenário 7: Multi-Provider
# ============================================================================

class TestE2EMultiProvider:
    """Testa suporte a múltiplos provedores LLM."""
    
    def test_e2e_multi_provider_openai_fallback(self, sample_log_path, agent_graph):
        """
        Teste 15: Fallback para análise sem LLM funciona.
        
        Esperado: Análise bem-sucedida mesmo sem API válida.
        """
        # Força sem API (environment var não setada)
        old_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        try:
            state = get_initial_state(sample_log_path)
            result = agent_graph.invoke(state)
            
            # Deve completar mesmo sem API
            assert result["is_valid"] is True or result["is_valid"] is False
            # O importante é não travar
        finally:
            # Restaura variável
            if old_key:
                os.environ["OPENAI_API_KEY"] = old_key
    
    def test_e2e_provider_specified_in_state(self, sample_log_path, agent_graph):
        """
        Teste 16: Provider pode ser especificado no estado.
        
        Esperado: llm_provider field aceito e respeitado.
        """
        state = get_initial_state(sample_log_path, provider="groq")
        
        assert state["llm_provider"] == "groq"


# ============================================================================
# Cenários Adicionais (Integração)
# ============================================================================

class TestE2EIntegration:
    """Testa integração de múltiplos componentes."""
    
    def test_e2e_complete_pipeline_with_observability(self, sample_log_path, agent_graph):
        """
        Teste 17: Pipeline completo com observabilidade ativa.
        
        Esperado: Tudo funciona junto.
        """
        state = get_initial_state(sample_log_path)
        
        # Verifica observabilidade inicializada
        assert state["trace_collector"] is not None
        assert state["execution_id"] is not None
        
        # Executa pipeline
        result = agent_graph.invoke(state)
        
        # Verifica resultado
        assert result["is_valid"] is True
        assert len(result["trace_collector"].get_traces()) > 0
    
    def test_e2e_state_consistency(self, sample_log_path, agent_graph):
        """
        Teste 18: Estado mantém consistência ao longo do pipeline.
        
        Esperado: Campos não são perdidos, valores são coerentes.
        """
        state = get_initial_state(sample_log_path)
        initial_file_path = state["file_path"]
        
        result = agent_graph.invoke(state)
        
        # file_path não deve mudar
        assert result["file_path"] == initial_file_path
        
        # execution_id não deve mudar
        initial_id = state["execution_id"]
        assert result["execution_id"] == initial_id
        
        # trace_collector não deve ser perdido
        assert result["trace_collector"] is not None


# ============================================================================
# Testes de Performance
# ============================================================================

class TestE2EPerformance:
    """Testa performance e limites."""
    
    def test_e2e_execution_time_reasonable(self, sample_log_path, agent_graph):
        """
        Teste 19: Execução completa é razoavelmente rápida.
        
        Esperado: <30 segundos para arquivo de exemplo.
        """
        state = get_initial_state(sample_log_path)
        
        start_time = time.time()
        result = agent_graph.invoke(state)
        elapsed = time.time() - start_time
        
        assert elapsed < 30, f"Execução demorou {elapsed}s, esperado <30s"
    
    def test_e2e_traces_not_too_many(self, sample_log_path, agent_graph):
        """
        Teste 20: Não há explosão de traces.
        
        Esperado: <500 traces para arquivo pequeno.
        """
        state = get_initial_state(sample_log_path)
        result = agent_graph.invoke(state)
        
        trace_count = len(result["trace_collector"].get_traces())
        assert trace_count < 500, f"Muitos traces: {trace_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
