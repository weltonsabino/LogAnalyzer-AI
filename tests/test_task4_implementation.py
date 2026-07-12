"""
Testes para Task #4 - Integração de Ferramentas e LLM do LogAnalyzer AI.

Testes focam em:
- Formatação de relatório
- Inicialização e uso de LLM
- Análise com fallback quando LLM não disponível
- Nós interpret_with_llm e generate_report
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.tools.formatter import format_report
from src.loganalyzer.analysis.llm_interpreter import (
    initialize_llm,
    analyze_with_llm,
    _generate_fallback_analysis,
)
from src.loganalyzer.nodes import interpret_with_llm_node, generate_report_node


class TestFormatterTool:
    """Testa ferramenta de formatação de relatório."""

    def test_format_report_returns_string(self):
        """Testa que format_report retorna string markdown."""
        # Prepara dados
        analysis_result = {
            "insights": ["Teste insight"],
            "recommendations": ["Teste recomendação"],
            "root_causes": ["Causa raiz de teste"],
        }
        errors = [{"message": "Erro 1", "line_number": 5}]
        warnings = [{"message": "Aviso 1", "line_number": 10}]
        critical = [{"message": "Crítico 1", "line_number": 15}]
        metadata = {
            "parsed_events_count": 100,
            "agent_name": "LogAnalyzer AI",
            "version": "0.0.1",
        }

        # Executa formatação
        report = format_report(analysis_result, errors, warnings, critical, metadata)

        # Valida resultado
        assert isinstance(report, str)
        assert len(report) > 0
        assert "# Relatorio de Analise de Log" in report
        assert "LogAnalyzer AI" in report

    def test_format_report_includes_metrics(self):
        """Testa que relatório inclui métricas resumidas."""
        analysis_result = {}
        errors = [{"message": f"Erro {i}", "line_number": i} for i in range(5)]
        warnings = [{"message": f"Aviso {i}", "line_number": 100 + i} for i in range(3)]
        critical = [{"message": "Crítico", "line_number": 200}]
        metadata = {
            "parsed_events_count": 200,
            "agent_name": "LogAnalyzer AI",
            "version": "0.0.1",
        }

        # Executa formatação
        report = format_report(analysis_result, errors, warnings, critical, metadata)

        # Valida métricas
        assert "5" in report  # 5 erros
        assert "3" in report  # 3 avisos
        assert "1" in report  # 1 crítico

    def test_format_report_includes_critical_events(self):
        """Testa que relatório inclui seção de eventos críticos."""
        analysis_result = {}
        critical = [
            {"message": "Crítico 1", "line_number": 10, "critical_reason": "teste"},
            {"message": "Crítico 2", "line_number": 20, "critical_reason": "teste"},
        ]
        errors = []
        warnings = []
        metadata = {"parsed_events_count": 100, "agent_name": "LogAnalyzer AI", "version": "0.0.1"}

        # Executa formatação
        report = format_report(analysis_result, errors, warnings, critical, metadata)

        # Valida seção crítica
        assert "Eventos Criticos" in report
        assert "Crítico 1" in report
        assert "Crítico 2" in report


class TestLLMIntegration:
    """Testa inicialização e uso de LLM."""

    def test_initialize_llm_returns_none_without_api_key(self):
        """Testa que initialize_llm retorna None sem OPENAI_API_KEY."""
        # Limpa API key temporariamente
        original_key = os.getenv("OPENAI_API_KEY")
        os.environ.pop("OPENAI_API_KEY", None)

        try:
            # Executa inicialização
            llm = initialize_llm()

            # Valida resultado
            assert llm is None

        finally:
            # Restaura API key se existia
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"})
    def test_initialize_llm_returns_chat_openai_with_api_key(self):
        """Testa que initialize_llm retorna ChatOpenAI com API key."""
        # Executa inicialização
        llm = initialize_llm()

        # Valida resultado
        assert llm is not None
        assert llm.model_name == "gpt-4-turbo-preview"

    def test_analyze_with_llm_returns_fallback_without_api_key(self):
        """Testa que analyze_with_llm retorna fallback sem LLM disponível."""
        # Limpa API key
        original_key = os.getenv("OPENAI_API_KEY")
        os.environ.pop("OPENAI_API_KEY", None)

        try:
            # Executa análise
            result = analyze_with_llm(
                errors_found=[{"message": "erro"}],
                warnings_found=[],
                critical_events=[],
                parsed_events=[],
            )

            # Valida resultado
            assert isinstance(result, dict)
            assert "insights" in result
            assert "recommendations" in result
            assert "root_causes" in result
            assert isinstance(result["insights"], list)
            assert isinstance(result["recommendations"], list)

        finally:
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

    def test_generate_fallback_analysis_with_critical_events(self):
        """Testa fallback analysis detecta eventos críticos."""
        # Prepara dados
        critical = [{"message": "Crítico 1"}, {"message": "Crítico 2"}]
        errors = []
        warnings = []

        # Executa fallback
        result = _generate_fallback_analysis(errors, warnings, critical)

        # Valida resultado
        assert len(result["insights"]) > 0
        assert any("crítico" in i.lower() for i in result["insights"])
        assert len(result["recommendations"]) > 0

    def test_generate_fallback_analysis_with_many_errors(self):
        """Testa fallback analysis detecta muitos erros."""
        # Prepara dados
        errors = [{"message": f"Error {i}"} for i in range(15)]
        critical = []
        warnings = []

        # Executa fallback
        result = _generate_fallback_analysis(errors, warnings, critical)

        # Valida resultado
        assert len(result["root_causes"]) > 0
        assert any("sistêmico" in r.lower() or "central" in r.lower() for r in result["root_causes"])


class TestLLMNode:
    """Testa nó interpret_with_llm."""

    def test_interpret_with_llm_node_updates_analysis_result(self):
        """Testa que nó atualiza analysis_result no estado."""
        # Prepara estado
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[{"message": "evento"}],
            errors_found=[{"message": "erro"}],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={"agent_name": "Test"},
            is_valid=True,
            error_message=None,
        )

        # Executa nó
        result_state = interpret_with_llm_node(state)

        # Valida resultado
        assert isinstance(result_state["analysis_result"], dict)
        assert "insights" in result_state["analysis_result"]
        assert "recommendations" in result_state["analysis_result"]

    def test_interpret_with_llm_node_skips_if_invalid(self):
        """Testa que nó pula se estado não é válido."""
        # Prepara estado inválido
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=False,
            error_message="Erro anterior",
        )

        # Executa nó
        result_state = interpret_with_llm_node(state)

        # Valida que pulou
        assert not result_state["is_valid"]
        assert result_state["error_message"] == "Pulando interpretação LLM - análise anterior falhou"


class TestReportGenerationNode:
    """Testa nó generate_report."""

    def test_generate_report_node_creates_report(self):
        """Testa que nó cria relatório markdown."""
        # Prepara estado
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[{"message": "evento"}],
            errors_found=[{"message": "erro"}],
            warnings_found=[],
            critical_events=[],
            analysis_result={"insights": ["Insight"], "recommendations": []},
            report="",
            metadata={"agent_name": "Test", "parsed_events_count": 1, "version": "0.0.1"},
            is_valid=True,
            error_message=None,
        )

        # Executa nó
        result_state = generate_report_node(state)

        # Valida resultado
        assert result_state["report"] != ""
        assert "Relatorio" in result_state["report"]
        assert "LogAnalyzer AI" in result_state["report"]

    def test_generate_report_node_includes_metrics(self):
        """Testa que relatório inclui métricas."""
        # Prepara estado
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[{"message": "evento"} for _ in range(10)],
            errors_found=[{"message": "erro"} for _ in range(3)],
            warnings_found=[{"message": "aviso"} for _ in range(2)],
            critical_events=[{"message": "crítico"}],
            analysis_result={},
            report="",
            metadata={
                "parsed_events_count": 10,
                "agent_name": "Test",
                "version": "0.0.1",
                "file_size_bytes": 1024,
            },
            is_valid=True,
            error_message=None,
        )

        # Executa nó
        result_state = generate_report_node(state)

        # Valida métricas no relatório
        report = result_state["report"]
        assert "10" in report  # Total eventos
        assert "3" in report   # Erros
        assert "2" in report   # Avisos


class TestEndToEndTask4:
    """Testes end-to-end da Task #4."""

    def test_full_pipeline_with_sample_data(self):
        """Testa pipeline completo com dados de amostra."""
        from src.loganalyzer.agent import create_agent_graph, get_initial_state

        # Prepara arquivo de teste temporário
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("2026-07-12 10:00:00 ERROR Connection timeout\n")
            f.write("2026-07-12 10:00:01 WARNING Memory high\n")
            f.write("2026-07-12 10:00:02 CRITICAL Database failed\n")
            temp_file = f.name

        try:
            # Cria agente
            agent = create_agent_graph()

            # Executa análise
            initial_state = get_initial_state(temp_file)
            final_state = agent.invoke(initial_state)

            # Valida resultado
            assert final_state["is_valid"] is True
            assert final_state["report"] != ""
            assert "Relatorio" in final_state["report"]
            assert len(final_state["parsed_events"]) > 0
            assert len(final_state["errors_found"]) > 0

        finally:
            # Limpa arquivo temporário
            import os
            os.unlink(temp_file)

