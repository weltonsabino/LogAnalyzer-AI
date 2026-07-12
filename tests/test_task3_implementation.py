"""
Testes para a implementação real da Task #3 - Lógica dos Nós.

Testa:
- Validação de arquivo (validate_input_node)
- Leitura de arquivo (read_file_node)
- Parsing de eventos (parse_events_node)
- Análise de padrões (analyze_patterns_node)
- Tratamento de erros (error_handling_node)
- Ferramentas: validators, file_reader, parser, detector
"""

import os
import pytest
import tempfile

from src.loganalyzer.models import LogAnalysisState
from src.loganalyzer.agent import get_initial_state
from src.loganalyzer.nodes import (
    validate_input_node,
    read_file_node,
    parse_events_node,
    analyze_patterns_node,
    error_handling_node,
)
from src.loganalyzer.tools import (
    validate_file_path,
    read_log_file,
    parse_log_content,
    detect_patterns,
)


class TestValidateInputNode:
    """Testa validate_input_node com arquivo válido e inválido."""

    def test_validate_input_with_valid_file(self):
        """Testa validação com arquivo existente."""
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("test log content\n")
            temp_file = f.name

        try:
            state = get_initial_state(temp_file)
            result = validate_input_node(state)

            # Valida resultado
            assert result["is_valid"] is True
            assert result["error_message"] is None
            assert "validation_timestamp" in result["metadata"]
        finally:
            os.unlink(temp_file)

    def test_validate_input_with_invalid_file(self):
        """Testa validação com arquivo inexistente."""
        state = get_initial_state("/arquivo/inexistente.log")
        result = validate_input_node(state)

        # Valida resultado
        assert result["is_valid"] is False
        assert result["error_message"] is not None
        assert "não encontrado" in result["error_message"].lower()


class TestReadFileNode:
    """Testa read_file_node com arquivo válido."""

    def test_read_file_with_valid_file(self):
        """Testa leitura com arquivo válido."""
        content = "ERROR: Connection timeout\nWARNING: Retry attempt\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            state = get_initial_state(temp_file)
            # Primeiro valida
            state = validate_input_node(state)
            # Depois lê
            result = read_file_node(state)

            # Valida resultado
            assert result["is_valid"] is True
            assert result["file_content"] == content
            assert len(result["file_content"]) > 0
        finally:
            os.unlink(temp_file)

    def test_read_file_skips_if_validation_failed(self):
        """Testa que read_file pula se validação falhou."""
        state = get_initial_state("/arquivo/inexistente.log")
        state = validate_input_node(state)
        result = read_file_node(state)

        # Deve ter mantido is_valid = False
        assert result["is_valid"] is False


class TestParseEventsNode:
    """Testa parse_events_node com diferentes formatos de log."""

    def test_parse_simple_text_log(self):
        """Testa parsing de log em formato texto simples."""
        content = "ERROR: Connection timeout\nWARNING: Retry attempt\nINFO: Request received\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            state = get_initial_state(temp_file)
            state = validate_input_node(state)
            state = read_file_node(state)
            result = parse_events_node(state)

            # Valida resultado
            assert result["is_valid"] is True
            assert len(result["parsed_events"]) == 3
            assert result["metadata"]["parsed_events_count"] == 3
        finally:
            os.unlink(temp_file)

    def test_parse_log_with_timestamps(self):
        """Testa parsing de log com timestamps."""
        content = "[2026-07-09 10:30:45] ERROR Connection timeout\n[2026-07-09 10:31:00] INFO Request complete\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            state = get_initial_state(temp_file)
            state = validate_input_node(state)
            state = read_file_node(state)
            result = parse_events_node(state)

            # Valida resultado
            assert result["is_valid"] is True
            assert len(result["parsed_events"]) == 2
            # Verifica se timestamps foram detectados
            assert result["parsed_events"][0]["timestamp"] is not None
        finally:
            os.unlink(temp_file)


class TestAnalyzePatternsNode:
    """Testa analyze_patterns_node com detecção de erros e avisos."""

    def test_analyze_patterns_detects_errors(self):
        """Testa detecção de erros."""
        content = "ERROR: Connection failed\nERROR: Connection failed\nWARNING: Retrying\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            state = get_initial_state(temp_file)
            state = validate_input_node(state)
            state = read_file_node(state)
            state = parse_events_node(state)
            result = analyze_patterns_node(state)

            # Valida resultado
            assert result["is_valid"] is True
            assert len(result["errors_found"]) > 0
            assert len(result["warnings_found"]) > 0
            assert result["metadata"]["errors_count"] > 0
        finally:
            os.unlink(temp_file)

    def test_analyze_patterns_detects_critical(self):
        """Testa detecção de eventos críticos."""
        content = "ERROR: CRITICAL system failure\nERROR: Database crash\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            state = get_initial_state(temp_file)
            state = validate_input_node(state)
            state = read_file_node(state)
            state = parse_events_node(state)
            result = analyze_patterns_node(state)

            # Valida resultado
            assert result["is_valid"] is True
            assert len(result["critical_events"]) > 0
            assert result["metadata"]["critical_count"] > 0
        finally:
            os.unlink(temp_file)


class TestErrorHandlingNode:
    """Testa error_handling_node."""

    def test_error_handling_sets_flags(self):
        """Testa que error_handling_node define flags corretamente."""
        state = get_initial_state("/arquivo/inexistente.log")
        state["error_message"] = "Teste de erro"
        state["is_valid"] = True  # Força is_valid para True

        result = error_handling_node(state)

        # Valida que flags foram corrigidos
        assert result["is_valid"] is False
        assert result["error_message"] == "Teste de erro"
        assert "error_timestamp" in result["metadata"]


class TestToolValidators:
    """Testa ferramentas de validação."""

    def test_validate_file_path_with_existing_file(self):
        """Testa validação com arquivo existente."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name

        try:
            is_valid, message = validate_file_path(temp_file)
            assert is_valid is True
            assert "validado" in message.lower()
        finally:
            os.unlink(temp_file)

    def test_validate_file_path_with_nonexistent_file(self):
        """Testa validação com arquivo inexistente."""
        is_valid, message = validate_file_path("/arquivo/inexistente.log")
        assert is_valid is False
        assert "não encontrado" in message.lower()


class TestToolFileReader:
    """Testa ferramenta de leitura de arquivo."""

    def test_read_log_file_success(self):
        """Testa leitura bem-sucedida."""
        content = "test log content"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            result = read_log_file(temp_file)
            assert result == content
        finally:
            os.unlink(temp_file)

    def test_read_log_file_not_found(self):
        """Testa erro quando arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            read_log_file("/arquivo/inexistente.log")


class TestToolParser:
    """Testa ferramenta de parsing."""

    def test_parse_log_content_simple(self):
        """Testa parsing simples."""
        content = "ERROR: Message 1\nWARNING: Message 2\n"
        events = parse_log_content(content)

        assert len(events) == 2
        assert events[0]["level"] == "ERROR"
        assert events[1]["level"] == "WARNING"

    def test_parse_log_content_empty_lines(self):
        """Testa que linhas vazias são ignoradas."""
        content = "ERROR: Message 1\n\n\nWARNING: Message 2\n"
        events = parse_log_content(content)

        assert len(events) == 2


class TestToolDetector:
    """Testa ferramenta de detecção de padrões."""

    def test_detect_patterns_basic(self):
        """Testa detecção básica de padrões."""
        events = [
            {"level": "ERROR", "message": "Connection failed", "line_number": 1},
            {"level": "WARNING", "message": "Retry attempt", "line_number": 2},
        ]
        result = detect_patterns(events)

        assert len(result["errors"]) == 1
        assert len(result["warnings"]) == 1

    def test_detect_patterns_critical(self):
        """Testa detecção de críticos."""
        events = [
            {"level": "ERROR", "message": "CRITICAL failure", "line_number": 1},
            {"level": "ERROR", "message": "Connection failed", "line_number": 2},
            {"level": "ERROR", "message": "Connection failed", "line_number": 3},
        ]
        result = detect_patterns(events)

        # Deve ter detectado pelo menos um como crítico
        assert len(result["critical"]) > 0
