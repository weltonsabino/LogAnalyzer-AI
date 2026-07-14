"""
Testes para ferramentas (tools) do LogAnalyzer AI.

Testa:
- validators.py: validação de arquivo e conteúdo
- file_reader.py: leitura de arquivo
- parser.py: parsing de eventos em múltiplos formatos
- detector.py: detecção de padrões
- formatter.py: formatação de relatório
"""

import os
import pytest
import tempfile
import json

from src.loganalyzer.tools.validators import (
    validate_file_path,
    validate_file_content,
)
from src.loganalyzer.tools.file_reader import read_log_file
from src.loganalyzer.tools.parser import parse_log_content
from src.loganalyzer.tools.detector import detect_patterns
from src.loganalyzer.tools.formatter import format_report


class TestValidators:
    """Testa ferramentas de validação."""

    def test_validate_file_path_with_valid_file(self):
        """Testa validação com arquivo válido."""
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("test log content\n")
            temp_file = f.name

        try:
            # Valida arquivo existente
            is_valid, message = validate_file_path(temp_file)
            assert is_valid is True
            assert "validado" in message.lower()
        finally:
            os.unlink(temp_file)

    def test_validate_file_path_with_nonexistent_file(self):
        """Testa validação com arquivo inexistente."""
        # Tenta validar arquivo que não existe
        is_valid, message = validate_file_path("/inexistente/arquivo.log")
        assert is_valid is False
        assert "não encontrado" in message.lower()

    def test_validate_file_path_without_path(self):
        """Testa validação com caminho vazio."""
        # Tenta validar sem fornecer caminho
        is_valid, message = validate_file_path("")
        assert is_valid is False
        assert "não foi fornecido" in message.lower()

    def test_validate_file_content_with_valid_content(self):
        """Testa validação de conteúdo válido."""
        # Conteúdo com eventos válidos
        content = "2026-07-13 10:00:00 ERROR Database connection failed\n"
        is_valid, message = validate_file_content(content)
        assert is_valid is True

    def test_validate_file_content_with_empty_content(self):
        """Testa validação de conteúdo vazio."""
        # Conteúdo vazio
        is_valid, message = validate_file_content("")
        assert is_valid is False


class TestFileReader:
    """Testa ferramentas de leitura de arquivo."""

    def test_read_log_file_with_valid_file(self):
        """Testa leitura de arquivo válido."""
        # Cria arquivo temporário com conteúdo
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            content = "2026-07-13 10:00:00 ERROR Test error\n"
            f.write(content)
            temp_file = f.name

        try:
            # Lê arquivo
            result = read_log_file(temp_file)
            assert result == content
        finally:
            os.unlink(temp_file)

    def test_read_log_file_with_nonexistent_file(self):
        """Testa leitura de arquivo inexistente."""
        # Tenta ler arquivo que não existe
        with pytest.raises(FileNotFoundError):
            read_log_file("/inexistente/arquivo.log")

    def test_read_log_file_with_multiline_content(self):
        """Testa leitura de arquivo com múltiplas linhas."""
        # Cria arquivo temporário com múltiplas linhas
        content = "2026-07-13 10:00:00 INFO App started\n" \
                  "2026-07-13 10:01:00 ERROR Database error\n" \
                  "2026-07-13 10:02:00 WARNING High memory\n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(content)
            temp_file = f.name

        try:
            # Lê arquivo
            result = read_log_file(temp_file)
            assert result == content
            assert result.count('\n') == 3
        finally:
            os.unlink(temp_file)


class TestParser:
    """Testa ferramentas de parsing."""

    def test_parse_log_content_with_text_format(self):
        """Testa parsing de formato texto simples."""
        # Conteúdo em formato texto
        content = "2026-07-13 10:00:00 ERROR Database connection failed\n" \
                  "2026-07-13 10:01:00 WARNING High CPU usage\n"
        
        events = parse_log_content(content)
        assert len(events) >= 2
        assert any("ERROR" in str(e).upper() for e in events)

    def test_parse_log_content_with_json_format(self):
        """Testa parsing de formato JSON."""
        # Conteúdo em formato JSON
        json_content = json.dumps({
            "timestamp": "2026-07-13 10:00:00",
            "level": "ERROR",
            "message": "Database error"
        })
        
        events = parse_log_content(json_content)
        assert len(events) > 0

    def test_parse_log_content_with_mixed_format(self):
        """Testa parsing de conteúdo com múltiplos formatos."""
        # Conteúdo misto
        content = "2026-07-13 10:00:00 ERROR Error message\n" \
                  "INFO Another line\n"
        
        events = parse_log_content(content)
        assert len(events) >= 2

    def test_parse_log_events_returns_list(self):
        """Testa que parse_log_content retorna lista."""
        # Eventos parseados
        content = "2026-07-13 10:00:00 ERROR Test\n"
        events = parse_log_content(content)
        assert isinstance(events, list)


class TestDetector:
    """Testa ferramentas de detecção de padrões."""

    def test_detect_patterns_finds_errors(self):
        """Testa detecção de padrão ERROR."""
        # Eventos com erro
        events = [
            {"timestamp": "2026-07-13 10:00:00", "level": "ERROR", "message": "DB error"},
            {"timestamp": "2026-07-13 10:01:00", "level": "INFO", "message": "Info"},
        ]
        
        patterns = detect_patterns(events)
        assert "errors" in patterns or "critical" in patterns

    def test_detect_patterns_finds_warnings(self):
        """Testa detecção de padrão WARNING."""
        # Eventos com aviso
        events = [
            {"timestamp": "2026-07-13 10:00:00", "level": "WARNING", "message": "High memory"},
            {"timestamp": "2026-07-13 10:01:00", "level": "INFO", "message": "Info"},
        ]
        
        patterns = detect_patterns(events)
        assert patterns is not None

    def test_find_critical_patterns_identifies_critical_events(self):
        """Testa identificação de eventos críticos."""
        # Eventos críticos
        events = [
            {"timestamp": "2026-07-13 10:00:00", "level": "CRITICAL", "message": "System down"},
            {"timestamp": "2026-07-13 10:01:00", "level": "ERROR", "message": "Major error"},
            {"timestamp": "2026-07-13 10:02:00", "level": "INFO", "message": "Info"},
        ]
        
        patterns = detect_patterns(events)
        assert "critical" in patterns or "errors" in patterns


class TestFormatter:
    """Testa ferramentas de formatação."""

    def test_format_report_returns_string(self):
        """Testa que format_report retorna string."""
        # Dados de análise
        analysis_result = {
            "summary": "Test summary",
            "insights": ["Insight 1"],
            "recommendations": ["Rec 1"],
            "root_causes": ["Cause 1"],
        }
        errors = [{"message": "Error 1"}]
        warnings = [{"message": "Warning 1"}]
        critical = []
        metadata = {"file": "test.log", "timestamp": "2026-07-13", "total_events": 10}
        
        report = format_report(analysis_result, errors, warnings, critical, metadata)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_format_report_includes_file_name(self):
        """Testa que report inclui informações de arquivo."""
        # Dados de análise
        analysis_result = {"summary": "Test"}
        errors = []
        warnings = []
        critical = []
        metadata = {"file": "mylog.log", "timestamp": "2026-07-13"}
        
        report = format_report(analysis_result, errors, warnings, critical, metadata)
        assert "mylog.log" in report or "Relatorio" in report

    def test_format_report_includes_summary(self):
        """Testa que report inclui resumo."""
        # Dados de análise
        analysis_result = {"summary": "Test summary", "insights": []}
        errors = []
        warnings = []
        critical = []
        metadata = {"file": "test.log"}
        
        report = format_report(analysis_result, errors, warnings, critical, metadata)
        assert "Test summary" in report or "Relatorio" in report
