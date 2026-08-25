"""
Testes para o modulo de deteccao de anomalias (DevOps Inteligente).

Valida heuristicas de spike detection, padroes recorrentes e
estimativa de risco do AnomalyDetector.
"""

import pytest

from src.loganalyzer.devops.anomaly_detector import AnomalyDetector


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def detector():
    """Cria instancia do AnomalyDetector com parametros padrao."""
    return AnomalyDetector(window_size=20, spike_threshold=2.0)


@pytest.fixture
def normal_log():
    """Log normal sem anomalias (2 erros em 40 linhas)."""
    lines = ["INFO Request processed successfully"] * 18
    lines += ["ERROR Connection timeout"] * 2
    lines += ["INFO Request processed successfully"] * 18
    lines += ["ERROR Connection timeout"] * 2
    return lines


@pytest.fixture
def spike_log():
    """Log com spike de erros (muitos erros no final apos periodo limpo)."""
    # Baseline: poucas erros no inicio (40 linhas normais com 1 erro)
    lines = ["INFO Normal operation"] * 39
    lines += ["ERROR Minor issue"] * 1
    # Spike: muitos erros concentrados no final (15 erros em 20 linhas)
    lines += ["ERROR Critical failure"] * 15
    lines += ["INFO Recovery attempt"] * 5
    return lines


@pytest.fixture
def recurring_log():
    """Log com padrao recorrente (mesma mensagem 5+ vezes)."""
    lines = [
        "INFO Starting service",
        "ERROR Connection timeout - retrying (1/3)",
        "ERROR Connection timeout - retrying (1/3)",
        "ERROR Connection timeout - retrying (1/3)",
        "ERROR Connection timeout - retrying (1/3)",
        "ERROR Connection timeout - retrying (1/3)",
        "INFO Service started",
        "WARNING Slow response",
        "ERROR Database unavailable",
        "ERROR Database unavailable",
    ]
    return lines


# ============================================
# Testes: detect_error_spike
# ============================================

class TestDetectErrorSpike:
    """Testa deteccao de spikes de erro."""

    def test_detect_error_spike_normal_log(self, detector, normal_log):
        """Log normal sem anomalia retorna anomaly=False."""
        result = detector.detect_error_spike(normal_log)

        assert result["anomaly"] is False

    def test_detect_error_spike_detected(self, detector, spike_log):
        """Log com spike retorna anomalia detectada."""
        result = detector.detect_error_spike(spike_log)

        assert result["anomaly"] is True
        assert result["type"] == "error_spike"
        assert result["current"] > result["baseline"] * 2

    def test_detect_error_spike_severity_high(self, detector):
        """Spike >3x baseline retorna severity high."""
        # Baseline: 0-1 erro por janela (40 linhas limpas)
        lines = ["INFO ok"] * 40
        # Spike: 16 erros nos ultimos 20 eventos (>>3x baseline de ~0)
        lines += ["ERROR critical"] * 16 + ["INFO ok"] * 4
        
        result = detector.detect_error_spike(lines)

        assert result["anomaly"] is True
        assert result["severity"] == "high"

    def test_detect_error_spike_insufficient_data(self, detector):
        """Poucas linhas retorna insufficient_data."""
        lines = ["INFO short"] * 5

        result = detector.detect_error_spike(lines)

        assert result["anomaly"] is False
        assert result.get("reason") == "insufficient_data"


# ============================================
# Testes: detect_recurring_pattern
# ============================================

class TestDetectRecurringPattern:
    """Testa deteccao de padroes recorrentes."""

    def test_detect_recurring_pattern_found(self, detector, recurring_log):
        """Padrao recorrente (5x mesma msg) e detectado."""
        result = detector.detect_recurring_pattern(recurring_log)

        assert result["recurring"] is True
        assert result["total_recurring"] >= 1
        # Verifica que o padrao mais frequente tem 5 ocorrencias
        assert result["patterns"][0]["count"] >= 5

    def test_detect_recurring_pattern_none(self, detector):
        """Log sem padroes recorrentes retorna recurring=False."""
        lines = [
            "INFO Starting",
            "ERROR Unique error 1",
            "ERROR Unique error 2",
            "ERROR Unique error 3",
            "INFO Done",
        ]

        result = detector.detect_recurring_pattern(lines)

        assert result["recurring"] is False
        assert result["total_recurring"] == 0

    def test_detect_recurring_pattern_no_errors(self, detector):
        """Log sem erros retorna recurring=False."""
        lines = ["INFO All good"] * 20

        result = detector.detect_recurring_pattern(lines)

        assert result["recurring"] is False
        assert result["patterns"] == []


# ============================================
# Testes: estimate_risk
# ============================================

class TestEstimateRisk:
    """Testa estimativa de risco."""

    def test_estimate_risk_critical(self, detector):
        """Anomalia high spike resulta em risco critical."""
        anomalies = [
            {"type": "error_spike", "severity": "high", "anomaly": True}
        ]

        result = detector.estimate_risk(anomalies)

        assert result["risk_level"] == "critical"
        assert result["trend"] == "increasing"

    def test_estimate_risk_high(self, detector):
        """Anomalia medium spike resulta em risco high."""
        anomalies = [
            {"type": "error_spike", "severity": "medium", "anomaly": True}
        ]

        result = detector.estimate_risk(anomalies)

        assert result["risk_level"] == "high"
        assert result["trend"] == "increasing"

    def test_estimate_risk_low_no_anomalies(self, detector):
        """Sem anomalias resulta em risco low."""
        result = detector.estimate_risk([])

        assert result["risk_level"] == "low"
        assert result["trend"] == "stable"
        assert result["anomaly_count"] == 0


# ============================================
# Testes: analyze (pipeline completo)
# ============================================

class TestAnalyzeComplete:
    """Testa metodo analyze (orquestracao completa)."""

    def test_analyze_complete_pipeline(self, detector, spike_log):
        """Metodo analyze retorna estrutura completa."""
        result = detector.analyze(spike_log)

        # Verifica estrutura do resultado
        assert "error_spike" in result
        assert "recurring_patterns" in result
        assert "risk" in result
        assert "total_lines" in result
        assert "error_count" in result

        # Verifica tipos
        assert isinstance(result["error_spike"], dict)
        assert isinstance(result["recurring_patterns"], dict)
        assert isinstance(result["risk"], dict)
        assert isinstance(result["total_lines"], int)
        assert isinstance(result["error_count"], int)

        # Verifica valores coerentes
        assert result["total_lines"] == len(spike_log)
        assert result["error_count"] > 0

    def test_analyze_normal_log_low_risk(self, detector, normal_log):
        """Log normal resulta em risco baixo."""
        result = detector.analyze(normal_log)

        assert result["risk"]["risk_level"] == "low"

    def test_analyze_spike_log_high_risk(self, detector, spike_log):
        """Log com spike resulta em risco alto."""
        result = detector.analyze(spike_log)

        assert result["risk"]["risk_level"] in ("critical", "high")
        assert result["error_spike"]["anomaly"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
