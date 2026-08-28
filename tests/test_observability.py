"""
Testes para o módulo de observabilidade avançada.

Valida TraceCollector, decorators de timeout/retry, e middleware
de instrumentação de nós.
"""

import pytest
import time
from datetime import datetime
from src.loganalyzer.observability import (
    TraceCollector,
    with_timeout,
    with_retry,
    observability_middleware,
    TRACE_EVENTS,
    TRACE_LEVELS
)


class TestTraceCollectorInitialization:
    """Testa inicialização do TraceCollector."""
    
    def test_trace_collector_creates_execution_id(self):
        """Verifica se TraceCollector gera execution_id único."""
        # Cria dois coletores
        collector1 = TraceCollector()
        collector2 = TraceCollector()
        
        # Valida que ambos têm execution_id
        assert collector1.execution_id is not None
        assert collector2.execution_id is not None
        # Valida que são diferentes
        assert collector1.execution_id != collector2.execution_id
    
    def test_trace_collector_accepts_custom_execution_id(self):
        """Verifica se TraceCollector aceita execution_id customizado."""
        # Usa execution_id customizado
        custom_id = "test-execution-12345"
        collector = TraceCollector(execution_id=custom_id)
        
        # Valida que usa o ID fornecido
        assert collector.execution_id == custom_id
    
    def test_trace_collector_initializes_empty_traces(self):
        """Verifica se TraceCollector começa com lista vazia de traces."""
        collector = TraceCollector()
        
        # Valida que lista de traces está vazia
        assert collector.traces == []
        assert len(collector.get_traces()) == 0


class TestTraceCollectorAddTrace:
    """Testa adição de traces ao TraceCollector."""
    
    def test_add_single_trace(self):
        """Adiciona um trace e valida estrutura."""
        collector = TraceCollector()
        
        # Adiciona trace
        collector.add_trace(
            node_name="test_node",
            event_type="node_start",
            data={"key": "value"}
        )
        
        # Valida que trace foi adicionado
        traces = collector.get_traces()
        assert len(traces) == 1
        assert traces[0]["node_name"] == "test_node"
        assert traces[0]["event_type"] == "node_start"
        assert traces[0]["data"]["key"] == "value"
        assert traces[0]["execution_id"] == collector.execution_id
    
    def test_add_multiple_traces_in_order(self):
        """Adiciona múltiplos traces e valida ordem cronológica."""
        collector = TraceCollector()
        
        # Adiciona 3 traces com pequeno delay
        for i in range(3):
            collector.add_trace(
                node_name=f"node_{i}",
                event_type="node_start",
                data={"index": i}
            )
            time.sleep(0.01)
        
        # Valida que traces estão em ordem
        traces = collector.get_traces()
        assert len(traces) == 3
        for i, trace in enumerate(traces):
            assert trace["data"]["index"] == i
    
    def test_trace_has_iso_timestamp(self):
        """Valida que trace tem timestamp ISO válido."""
        collector = TraceCollector()
        
        # Adiciona trace
        collector.add_trace(
            node_name="test",
            event_type="node_start",
            data={}
        )
        
        # Valida timestamp ISO
        trace = collector.get_traces()[0]
        assert "timestamp" in trace
        # Tenta fazer parse ISO
        dt = datetime.fromisoformat(trace["timestamp"])
        assert dt is not None


class TestTraceCollectorCorrelation:
    """Testa correlação de traces com execution_id."""
    
    def test_all_traces_have_same_execution_id(self):
        """Valida que todos os traces têm mesmo execution_id."""
        collector = TraceCollector()
        
        # Adiciona múltiplos traces
        for i in range(5):
            collector.add_trace(
                node_name=f"node_{i}",
                event_type="node_start",
                data={"index": i}
            )
        
        # Valida que todos têm mesmo execution_id
        traces = collector.get_traces()
        execution_ids = [t["execution_id"] for t in traces]
        assert len(set(execution_ids)) == 1
        assert execution_ids[0] == collector.execution_id
    
    def test_correlation_summary_includes_execution_id(self):
        """Valida que summary de correlação inclui execution_id."""
        collector = TraceCollector()
        
        # Adiciona alguns traces
        for i in range(3):
            collector.add_trace(
                node_name=f"node_{i}",
                event_type="node_start",
                data={"index": i}
            )
        
        # Pega summary
        summary = collector.get_correlation_summary()
        
        # Valida execution_id no summary
        assert summary["execution_id"] == collector.execution_id


class TestCorrelationSummary:
    """Testa geração de sumário de correlação."""
    
    def test_correlation_summary_structure(self):
        """Valida estrutura do sumário de correlação."""
        collector = TraceCollector()
        
        # Adiciona traces variados
        collector.add_trace("node1", "node_start", {"data": "test"})
        collector.add_trace("node2", "node_end", {"data": "test"})
        collector.add_trace("node3", "warning", {"data": "test"})
        
        # Pega summary
        summary = collector.get_correlation_summary()
        
        # Valida campos obrigatórios
        assert "execution_id" in summary
        assert "trace_count" in summary
        assert "duration_seconds" in summary
        assert "event_counts" in summary
        assert "status" in summary
        assert "start_time" in summary
        assert "end_time" in summary
    
    def test_correlation_summary_counts_events(self):
        """Valida contagem de eventos no sumário."""
        collector = TraceCollector()
        
        # Adiciona traces variados
        collector.add_trace("node1", "node_start", {})
        collector.add_trace("node2", "node_start", {})
        collector.add_trace("node3", "node_end", {})
        collector.add_trace("node4", "error", {})
        
        # Pega summary
        summary = collector.get_correlation_summary()
        
        # Valida contagem
        assert summary["trace_count"] == 4
        assert summary["event_counts"]["node_start"] == 2
        assert summary["event_counts"]["node_end"] == 1
        assert summary["event_counts"]["error"] == 1
    
    def test_correlation_summary_status_ok(self):
        """Valida status OK sem erros."""
        collector = TraceCollector()
        
        # Adiciona apenas traces bons
        collector.add_trace("node1", "node_start", {})
        collector.add_trace("node2", "node_end", {})
        
        summary = collector.get_correlation_summary()
        assert summary["status"] == "OK"
    
    def test_correlation_summary_status_warning(self):
        """Valida status WARNING com avisos."""
        collector = TraceCollector()
        
        # Adiciona trace com warning
        collector.add_trace("node1", "warning", {})
        
        summary = collector.get_correlation_summary()
        assert summary["status"] == "WARNING"
    
    def test_correlation_summary_status_error(self):
        """Valida status ERROR com erros."""
        collector = TraceCollector()
        
        # Adiciona trace com erro
        collector.add_trace("node1", "error", {})
        
        summary = collector.get_correlation_summary()
        assert summary["status"] == "ERROR"
    
    def test_correlation_summary_duration(self):
        """Valida duração calculada corretamente."""
        collector = TraceCollector()
        
        # Adiciona trace
        collector.add_trace("node1", "node_start", {})
        
        # Aguarda um pouco
        time.sleep(0.1)
        
        # Pega summary
        summary = collector.get_correlation_summary()
        
        # Valida duração
        assert summary["duration_seconds"] >= 0.1
        assert isinstance(summary["duration_seconds"], float)


class TestTimeoutDecorator:
    """Testa decorator @with_timeout."""
    
    def test_timeout_function_completes_in_time(self):
        """Função que completa em tempo não dispara timeout."""
        @with_timeout(seconds=5)
        def quick_function():
            """Função que executa rápido."""
            time.sleep(0.1)
            return "success"
        
        # Executa função rápida
        result = quick_function()
        assert result == "success"
    
    def test_timeout_preserves_function_metadata(self):
        """Verifica se decorator preserva metadados da função."""
        @with_timeout(seconds=5)
        def documented_function():
            """Função com documentação."""
            return "result"
        
        # Valida que preserva nome e docstring
        assert documented_function.__name__ == "documented_function"
        assert "Função com documentação" in documented_function.__doc__


class TestRetryDecorator:
    """Testa decorator @with_retry."""
    
    def test_retry_succeeds_on_first_attempt(self):
        """Função bem-sucedida na primeira tentativa."""
        call_count = {"count": 0}
        
        @with_retry(max_attempts=3, backoff=1.0)
        def success_function():
            """Função que sempre sucede."""
            call_count["count"] += 1
            return "success"
        
        result = success_function()
        
        # Valida que não houve retries
        assert result == "success"
        assert call_count["count"] == 1
    
    def test_retry_attempts_multiple_times_on_timeout(self):
        """Retry dispara múltiplas vezes em caso de timeout."""
        call_count = {"count": 0}
        
        @with_retry(max_attempts=3, backoff=0.1)
        def timeout_function():
            """Função que lança timeout."""
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise TimeoutError("Timeout simulated")
            return "success"
        
        result = timeout_function()
        
        # Valida que houve 3 tentativas
        assert result == "success"
        assert call_count["count"] == 3
    
    def test_retry_gives_up_after_max_attempts(self):
        """Retry desiste após número máximo de tentativas."""
        call_count = {"count": 0}
        
        @with_retry(max_attempts=2, backoff=0.1)
        def always_fails():
            """Função que sempre falha."""
            call_count["count"] += 1
            raise TimeoutError("Always fails")
        
        # Espera que lance exceção após 2 tentativas
        with pytest.raises(TimeoutError):
            always_fails()
        
        # Valida que tentou 2 vezes
        assert call_count["count"] == 2
    
    def test_retry_only_for_transient_errors(self):
        """Retry apenas para erros transientes."""
        call_count = {"count": 0}
        
        @with_retry(max_attempts=3, backoff=0.1)
        def raises_value_error():
            """Função que lança ValueError (não transiente)."""
            call_count["count"] += 1
            raise ValueError("Not transient")
        
        # Espera que lance ValueError
        with pytest.raises(ValueError):
            raises_value_error()
        
        # Valida que tentou apenas 1 vez (sem retry para ValueError)
        assert call_count["count"] == 1
    
    def test_retry_preserves_function_metadata(self):
        """Verifica se decorator preserva metadados."""
        @with_retry(max_attempts=3)
        def documented_function():
            """Função com documentação."""
            return "result"
        
        # Valida que preserva nome e docstring
        assert documented_function.__name__ == "documented_function"
        assert "Função com documentação" in documented_function.__doc__


class TestObservabilityMiddleware:
    """Testa decorator @observability_middleware."""
    
    def test_middleware_without_collector(self):
        """Middleware executa normalmente sem collector."""
        @observability_middleware(collector=None)
        def test_function():
            """Função de teste."""
            return "result"
        
        result = test_function()
        assert result == "result"
    
    def test_middleware_records_success(self):
        """Middleware registra execução bem-sucedida."""
        collector = TraceCollector()
        
        @observability_middleware(collector=collector)
        def test_function():
            """Função de teste."""
            return "result"
        
        result = test_function()
        
        # Valida resultado
        assert result == "result"
        
        # Valida que foram registrados node_start e node_end
        traces = collector.get_traces()
        assert len(traces) == 2
        assert traces[0]["event_type"] == "node_start"
        assert traces[1]["event_type"] == "node_end"
    
    def test_middleware_records_error(self):
        """Middleware registra exceção."""
        collector = TraceCollector()
        
        @observability_middleware(collector=collector)
        def failing_function():
            """Função que lança erro."""
            raise ValueError("Test error")
        
        # Executa e captura erro
        with pytest.raises(ValueError):
            failing_function()
        
        # Valida que foram registrados node_start e error
        traces = collector.get_traces()
        assert len(traces) == 2
        assert traces[0]["event_type"] == "node_start"
        assert traces[1]["event_type"] == "error"
        assert traces[1]["data"]["error_type"] == "ValueError"
    
    def test_middleware_records_duration(self):
        """Middleware registra duração de execução."""
        collector = TraceCollector()
        
        @observability_middleware(collector=collector)
        def slow_function():
            """Função que demora."""
            time.sleep(0.1)
            return "result"
        
        slow_function()
        
        # Valida que duration está registrada
        traces = collector.get_traces()
        end_trace = traces[1]
        assert "duration_seconds" in end_trace["data"]
        assert end_trace["data"]["duration_seconds"] >= 0.1


class TestTraceConstants:
    """Testa constantes de observabilidade."""
    
    def test_trace_events_defined(self):
        """Valida que TRACE_EVENTS está definido."""
        assert TRACE_EVENTS is not None
        assert len(TRACE_EVENTS) >= 4
        assert "node_start" in TRACE_EVENTS
        assert "node_end" in TRACE_EVENTS
        assert "error" in TRACE_EVENTS
    
    def test_trace_levels_defined(self):
        """Valida que TRACE_LEVELS está definido."""
        assert TRACE_LEVELS is not None
        assert "DEBUG" in TRACE_LEVELS
        assert "INFO" in TRACE_LEVELS
        assert "WARN" in TRACE_LEVELS
        assert "ERROR" in TRACE_LEVELS
        # Valida que estão em ordem crescente
        assert TRACE_LEVELS["DEBUG"] < TRACE_LEVELS["INFO"]
        assert TRACE_LEVELS["INFO"] < TRACE_LEVELS["WARN"]
        assert TRACE_LEVELS["WARN"] < TRACE_LEVELS["ERROR"]
