"""
Models and data structures for LogAnalyzer AI agent.

Defines the shared state (LogAnalysisState) used by the StateGraph
to maintain information throughout the agent's execution.
"""

from typing import TypedDict, Optional, List, Dict, Any


class LogAnalysisState(TypedDict):
    """
    Shared state for the LogAnalyzer AI StateGraph.

    This state maintains all relevant information throughout the agent's
    execution, from input validation through final report generation.

    Attributes:
        file_path (str): Path to the log file to analyze
        file_content (str): Full content of the log file (populated after reading)
        parsed_events (list): List of parsed log events/lines
        errors_found (list): List of errors identified in the log
        warnings_found (list): List of warnings identified in the log
        critical_events (list): List of critical/severe events
        analysis_result (dict): Structured analysis results from the agent
        report (str): Final formatted markdown report
        metadata (dict): Additional metadata (timestamps, processing info)
        is_valid (bool): Whether the input and processing are valid
        error_message (Optional[str]): Error description if something went wrong
    """

    file_path: str
    file_content: str
    parsed_events: List[Dict[str, Any]]
    errors_found: List[Dict[str, Any]]
    warnings_found: List[Dict[str, Any]]
    critical_events: List[Dict[str, Any]]
    analysis_result: Dict[str, Any]
    report: str
    metadata: Dict[str, Any]
    is_valid: bool
    error_message: Optional[str]
