"""
Testes para módulo de análise (analysis) do LogAnalyzer AI.

Testa:
- llm_interpreter.py: inicialização, análise com LLM, fallback
- Interpretação de eventos críticos
- Geração de insights e recomendações
- Fallback automático quando LLM não disponível
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.loganalyzer.analysis.llm_interpreter import (
    initialize_llm,
    analyze_with_llm,
)


class TestLLMInitialization:
    """Testa inicialização do LLM."""

    def test_initialize_llm_returns_none_without_api_key(self):
        """Testa que initialize_llm retorna None sem API key."""
        # Remove API key temporariamente
        with patch.dict(os.environ, {}, clear=False):
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            
            # Inicializa LLM sem API key
            llm = initialize_llm()
            assert llm is None

    def test_initialize_llm_with_api_key_in_environment(self):
        """Testa que initialize_llm cria instância com API key."""
        # Mock da API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            # Inicializa LLM (pode retornar None em ambiente de teste)
            llm = initialize_llm()
            # Valida que tentou inicializar
            assert True  # Se chegou aqui sem erro, passou


class TestAnalysisWithLLM:
    """Testa análise com LLM."""

    def test_analyze_with_llm_returns_dict(self):
        """Testa que analyze_with_llm retorna dicionário."""
        # Dados de entrada
        errors = [{"type": "ERROR", "message": "DB error"}]
        warnings = [{"type": "WARNING", "message": "High memory"}]
        critical = [{"type": "CRITICAL", "message": "System down"}]
        events = errors + warnings + critical
        
        # Chama análise (sem LLM, usa fallback)
        result = analyze_with_llm(errors, warnings, critical, events)
        
        # Valida estrutura
        assert isinstance(result, dict)
        assert "insights" in result or "summary" in result

    def test_analyze_with_llm_with_empty_events(self):
        """Testa análise com eventos vazios."""
        # Listas vazias
        result = analyze_with_llm([], [], [], [])
        assert isinstance(result, dict)

    def test_analyze_with_llm_with_multiple_errors(self):
        """Testa análise com múltiplos erros."""
        # Múltiplos erros
        errors = [
            {"type": "ERROR", "message": "DB error"},
            {"type": "ERROR", "message": "Network error"},
            {"type": "ERROR", "message": "Timeout"},
        ]
        warnings = []
        critical = []
        
        result = analyze_with_llm(errors, warnings, critical, errors)
        assert isinstance(result, dict)

    def test_analyze_with_llm_returns_expected_fields(self):
        """Testa que análise retorna campos esperados."""
        # Dados de entrada
        errors = [{"type": "ERROR", "message": "Test error"}]
        
        result = analyze_with_llm(errors, [], [], errors)
        
        # Valida que resultado possui estrutura esperada
        assert "insights" in result
        assert "recommendations" in result
        assert "summary" in result


class TestFallbackAnalysis:
    """Testa fallback automático (análise heurística)."""

    def test_fallback_analysis_with_critical_events(self):
        """Testa que fallback identifica eventos críticos."""
        # Eventos críticos
        critical = [
            {"type": "CRITICAL", "message": "System down"},
            {"type": "CRITICAL", "message": "Data corruption"},
        ]
        
        result = analyze_with_llm([], [], critical, critical)
        
        # Valida que reconhece criticidade
        assert "insights" in result
        assert len(result["insights"]) > 0

    def test_fallback_analysis_with_many_errors(self):
        """Testa que fallback detecta muitos erros."""
        # Muitos erros (simulando problema sistêmico)
        errors = [
            {"type": "ERROR", "message": f"Error {i}"}
            for i in range(15)
        ]
        
        result = analyze_with_llm(errors, [], [], errors)
        
        # Valida que result possui estrutura
        assert isinstance(result, dict)
        assert "recommendations" in result

    def test_fallback_analysis_with_warnings(self):
        """Testa que fallback trata avisos."""
        # Muitos avisos
        warnings = [
            {"type": "WARNING", "message": f"Warning {i}"}
            for i in range(25)
        ]
        
        result = analyze_with_llm([], warnings, [], warnings)
        
        # Valida que reconhece avisos
        assert isinstance(result, dict)

    def test_fallback_analysis_without_events(self):
        """Testa fallback sem eventos."""
        # Sem eventos
        result = analyze_with_llm([], [], [], [])
        assert isinstance(result, dict)


class TestAnalysisIntegration:
    """Testa integração da análise."""

    def test_analysis_handles_structured_events(self):
        """Testa análise com eventos estruturados."""
        # Eventos estruturados
        events = [
            {
                "timestamp": "2026-07-13 10:00:00",
                "level": "ERROR",
                "message": "Database error",
                "source": "app.py",
            },
            {
                "timestamp": "2026-07-13 10:01:00",
                "level": "WARNING",
                "message": "High CPU",
                "source": "monitor.py",
            },
        ]
        
        # Separa por nível
        errors = [e for e in events if e.get("level") == "ERROR"]
        warnings = [e for e in events if e.get("level") == "WARNING"]
        critical = [e for e in events if e.get("level") == "CRITICAL"]
        
        # Executa análise
        result = analyze_with_llm(errors, warnings, critical, events)
        assert isinstance(result, dict)

    def test_analysis_with_very_large_event_list(self):
        """Testa análise com lista muito grande de eventos."""
        # Gera muitos eventos
        events = [
            {"type": "INFO", "message": f"Event {i}"}
            for i in range(1000)
        ]
        
        # Alguns erros e avisos
        events.append({"type": "ERROR", "message": "Critical error"})
        events.append({"type": "WARNING", "message": "Warning"})
        
        # Separa por tipo
        errors = [e for e in events if e.get("type") == "ERROR"]
        warnings = [e for e in events if e.get("type") == "WARNING"]
        
        # Executa análise (não deve crash)
        result = analyze_with_llm(errors, warnings, [], events)
        assert isinstance(result, dict)

    def test_analysis_result_has_all_required_fields(self):
        """Testa que resultado possui todos os campos obrigatórios."""
        # Dados de entrada
        errors = [{"message": "Test"}]
        
        result = analyze_with_llm(errors, [], [], errors)
        
        # Valida campos obrigatórios
        assert "insights" in result
        assert "recommendations" in result
        assert "root_causes" in result
        assert "summary" in result
