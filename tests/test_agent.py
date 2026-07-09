"""
Unit tests for the LogAnalyzer AI agent and StateGraph.

Tests focus on:
- StateGraph structure and node connectivity
- Initial state creation
- Node function signatures and return types
- Graph compilation and execution flow
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
    """Test LogAnalysisState TypedDict."""
    
    def test_state_creation(self):
        """Test that LogAnalysisState can be created with valid data."""
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
        """Test that LogAnalysisState has all required fields."""
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
    """Test individual node functions."""
    
    def test_validate_input_node_returns_state(self):
        """Test that validate_input_node returns a valid state."""
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
        """Test that read_file_node returns a valid state."""
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
        """Test that parse_events_node returns a valid state."""
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
        """Test that analyze_patterns_node returns a valid state."""
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
        """Test that interpret_with_llm_node returns a valid state."""
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
        """Test that generate_report_node returns a valid state."""
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
        """Test that error_handling_node returns a valid state."""
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
    """Test the StateGraph creation and structure."""
    
    def test_create_agent_graph_returns_graph(self):
        """Test that create_agent_graph returns a valid graph."""
        graph = create_agent_graph()
        assert graph is not None
        # Note: Compiled graphs don't have direct .nodes access
        # We validate by attempting to invoke
    
    def test_graph_can_be_compiled(self):
        """Test that the graph compiles without errors."""
        try:
            graph = create_agent_graph()
            assert graph is not None
        except Exception as e:
            pytest.fail(f"Graph compilation failed: {str(e)}")
    
    def test_get_initial_state_creates_valid_state(self):
        """Test that get_initial_state creates a valid initial state."""
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
        """Test that initial state includes metadata."""
        state = get_initial_state("/test.log")
        
        assert isinstance(state["metadata"], dict)
        assert "version" in state["metadata"]
        assert "agent_name" in state["metadata"]
        assert state["metadata"]["agent_name"] == "LogAnalyzer AI"


class TestGraphIntegration:
    """Integration tests for the complete graph."""
    
    def test_graph_can_execute_with_initial_state(self):
        """Test that the graph can be invoked with initial state."""
        try:
            graph = create_agent_graph()
            initial_state = get_initial_state("/test/log.txt")
            
            # Invoke the graph with a simple test
            # This will run through all nodes (placeholders)
            result = graph.invoke(initial_state)
            
            # Verify result is a dict with state
            assert isinstance(result, dict)
            assert "file_path" in result
        except Exception as e:
            pytest.fail(f"Graph invocation failed: {str(e)}")
    
    def test_graph_preserves_file_path(self):
        """Test that file_path is preserved through execution."""
        graph = create_agent_graph()
        initial_path = "/test/sample.log"
        initial_state = get_initial_state(initial_path)
        
        result = graph.invoke(initial_state)
        
        assert result["file_path"] == initial_path
