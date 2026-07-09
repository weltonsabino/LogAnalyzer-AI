"""
Testes unitários para o agente LogAnalyzer AI e StateGraph.

Testes focam em:
- Estrutura do StateGraph e conectividade dos nós
- Criação de estado inicial
- Assinaturas de funções de nó e tipos de retorno
- Compilação do grafo e fluxo de execução
"""

import pytest
from langgraph.graph import StateGraph

from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.agent import create_agent_graph, get_initial_state
from src.loganalyzer.nodes import (
    validate_input_node,
    read_file_node,
    parse_events_node,
    analyze_patterns_node,
    interpret_with_llm_node,
    generate_report_node,
    error_handling_node,
)


class TestStateModel:
    """Testa LogAnalysisState TypedDict."""

    def test_state_creation(self):
        """Testa que LogAnalysisState pode ser criado com dados válidos."""
        state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )
        assert state["file_path"] == "/path/to/log.txt"
        assert state["is_valid"] is True
        assert state["error_message"] is None

    def test_state_has_required_fields(self):
        """Testa que LogAnalysisState possui todos os campos obrigatórios."""
        state = LogAnalysisState(
            file_path="test.log",
            file_content="content",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={"test": "data"},
            is_valid=True,
            error_message=None,
        )

        required_fields = [
            "file_path",
            "file_content",
            "parsed_events",
            "errors_found",
            "warnings_found",
            "critical_events",
            "analysis_result",
            "report",
            "metadata",
            "is_valid",
            "error_message",
        ]

        for field in required_fields:
            assert field in state


class TestNodeFunctions:
    """Testa funções de nó individuais."""

    def test_validate_input_node_returns_state(self):
        """Testa que validate_input_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )

        result = validate_input_node(initial_state)
        assert isinstance(result, dict)
        assert "file_path" in result

    def test_read_file_node_returns_state(self):
        """Testa que read_file_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )

        result = read_file_node(initial_state)
        assert isinstance(result, dict)

    def test_parse_events_node_returns_state(self):
        """Testa que parse_events_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="sample log content",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )

        result = parse_events_node(initial_state)
        assert isinstance(result, dict)

    def test_analyze_patterns_node_returns_state(self):
        """Testa que analyze_patterns_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[{"type": "info", "message": "test"}],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )

        result = analyze_patterns_node(initial_state)
        assert isinstance(result, dict)

    def test_interpret_with_llm_node_returns_state(self):
        """Testa que interpret_with_llm_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )

        result = interpret_with_llm_node(initial_state)
        assert isinstance(result, dict)

    def test_generate_report_node_returns_state(self):
        """Testa que generate_report_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={"summary": "test analysis"},
            report="",
            metadata={},
            is_valid=True,
            error_message=None,
        )

        result = generate_report_node(initial_state)
        assert isinstance(result, dict)

    def test_error_handling_node_returns_state(self):
        """Testa que error_handling_node retorna um estado válido."""
        initial_state = LogAnalysisState(
            file_path="/path/to/log.txt",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            is_valid=False,
            error_message="Test error",
        )

        result = error_handling_node(initial_state)
        assert isinstance(result, dict)


class TestAgentGraph:
    """Testa a criação e estrutura do StateGraph."""

    def test_create_agent_graph_returns_graph(self):
        """Testa que create_agent_graph retorna um grafo válido."""
        graph = create_agent_graph()
        assert graph is not None
        # Nota: Grafos compilados não possuem acesso direto a .nodes
        # Validamos ao tentar invocar

    def test_graph_can_be_compiled(self):
        """Testa que o grafo compila sem erros."""
        try:
            graph = create_agent_graph()
            assert graph is not None
        except Exception as e:
            pytest.fail(f"Falha na compilação do grafo: {str(e)}")

    def test_get_initial_state_creates_valid_state(self):
        """Testa que get_initial_state cria um estado inicial válido."""
        file_path = "/test/log.txt"
        state = get_initial_state(file_path)

        assert state["file_path"] == file_path
        assert state["file_content"] == ""
        assert state["parsed_events"] == []
        assert state["errors_found"] == []
        assert state["warnings_found"] == []
        assert state["critical_events"] == []
        assert state["analysis_result"] == {}
        assert state["report"] == ""
        assert state["is_valid"] is True
        assert state["error_message"] is None
        assert "metadata" in state
        assert state["metadata"]["version"] == "0.0.1"

    def test_initial_state_has_metadata(self):
        """Testa que estado inicial inclui metadados."""
        state = get_initial_state("/test.log")

        assert isinstance(state["metadata"], dict)
        assert "version" in state["metadata"]
        assert "agent_name" in state["metadata"]
        assert state["metadata"]["agent_name"] == "LogAnalyzer AI"


class TestGraphIntegration:
    """Testes de integração para o grafo completo."""

    def test_graph_can_execute_with_initial_state(self):
        """Testa que o grafo pode ser invocado com estado inicial."""
        try:
            graph = create_agent_graph()
            initial_state = get_initial_state("/test/log.txt")

            # Invoca o grafo com um teste simples
            # Isso executará todos os nós (placeholders)
            result = graph.invoke(initial_state)

            # Verifica se resultado é um dict com estado
            assert isinstance(result, dict)
            assert "file_path" in result
        except Exception as e:
            pytest.fail(f"Falha na invocação do grafo: {str(e)}")

    def test_graph_preserves_file_path(self):
        """Testa que file_path é preservado durante execução."""
        graph = create_agent_graph()
        initial_path = "/test/sample.log"
        initial_state = get_initial_state(initial_path)

        result = graph.invoke(initial_state)

        assert result["file_path"] == initial_path
