"""
StateGraph for the LogAnalyzer AI agent.

This module defines the main agent graph structure using LangGraph,
including nodes, edges, and execution flow for log analysis automation.
"""

from langgraph.graph import StateGraph, END

from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.nodes import (
    validate_input_node,
    read_file_node,
    parse_events_node,
    analyze_patterns_node,
    interpret_with_llm_node,
    generate_report_node,
    error_handling_node,
)


def create_agent_graph() -> StateGraph:
    """
    Create and return the configured StateGraph for LogAnalyzer AI.

    Graph Structure:
    ```
    START
      ↓
    [validate_input] ──(invalid)──→ [error_handling] → END
      ↓ (valid)
    [read_file] ──(error)──→ [error_handling] → END
      ↓ (success)
    [parse_events] ──(error)──→ [error_handling] → END
      ↓ (success)
    [analyze_patterns] ──(error)──→ [error_handling] → END
      ↓ (success)
    [interpret_with_llm] ──(error)──→ [error_handling] → END
      ↓ (success)
    [generate_report]
      ↓
    END
    ```

    Returns:
        StateGraph: Configured graph ready for execution

    Note:
        Conditional edges (if-else transitions) will be added in Issue #3
        when node logic is fully implemented.
    """

    # Initialize the graph with LogAnalysisState
    graph = StateGraph(LogAnalysisState)

    # ============================================
    # 1. ADD NODES TO GRAPH
    # ============================================

    # Main processing pipeline nodes
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("read_file", read_file_node)
    graph.add_node("parse_events", parse_events_node)
    graph.add_node("analyze_patterns", analyze_patterns_node)
    graph.add_node("interpret_with_llm", interpret_with_llm_node)
    graph.add_node("generate_report", generate_report_node)

    # Error handling node
    graph.add_node("error_handling", error_handling_node)

    # ============================================
    # 2. SET ENTRY POINT
    # ============================================
    graph.set_entry_point("validate_input")

    # ============================================
    # 3. ADD EDGES (Connections between nodes)
    # ============================================

    # Happy path: Linear progression through pipeline
    graph.add_edge("validate_input", "read_file")
    graph.add_edge("read_file", "parse_events")
    graph.add_edge("parse_events", "analyze_patterns")
    graph.add_edge("analyze_patterns", "interpret_with_llm")
    graph.add_edge("interpret_with_llm", "generate_report")
    graph.add_edge("generate_report", END)

    # Error paths: Any step can transition to error_handling
    # Note: Conditional edges based on state.is_valid or error flags
    # will be implemented in Issue #3 when node logic is ready
    graph.add_edge("error_handling", END)

    # ============================================
    # 4. COMPILE GRAPH
    # ============================================

    agent = graph.compile()
    return agent


def get_initial_state(file_path: str) -> LogAnalysisState:
    """
    Create initial state for the agent execution.
    
    Args:
        file_path: Path to the log file to analyze
        
    Returns:
        Initial LogAnalysisState ready for agent execution
    """
    return LogAnalysisState(
        file_path=file_path,
        file_content="",
        parsed_events=[],
        errors_found=[],
        warnings_found=[],
        critical_events=[],
        analysis_result={},
        report="",
        metadata={
            "start_time": None,  # Will be set at runtime
            "version": "0.0.1",
            "agent_name": "LogAnalyzer AI",
        },
        is_valid=True,
        error_message=None,
    )
