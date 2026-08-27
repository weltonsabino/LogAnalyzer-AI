"""
Testes para o modulo de integracao webhook (n8n).

Valida envio de payload, tratamento de erros e configuracao
da classe WebhookIntegration usando mocks (sem requests reais).
"""

import pytest
from unittest.mock import patch, MagicMock

from src.loganalyzer.integrations.webhook import WebhookIntegration


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def webhook():
    """Cria instancia configurada do WebhookIntegration."""
    return WebhookIntegration(
        webhook_url="http://localhost:5678/webhook/loganalyzer",
        enabled=True,
    )


@pytest.fixture
def sample_analysis():
    """Retorna analise de exemplo para testes."""
    return {
        "errors_found": [
            {"level": "ERROR", "message": "Connection timeout"},
            {"level": "ERROR", "message": "Database unavailable"},
        ],
        "warnings_found": [
            {"level": "WARNING", "message": "Slow response"},
        ],
        "critical_events": [],
    }


@pytest.fixture
def sample_report():
    """Retorna relatorio de exemplo para testes."""
    return "## Relatorio de Analise\n\nErros: 2\nWarnings: 1\nStatus: Atencao necessaria"


# ============================================
# Testes: build_payload
# ============================================

class TestBuildPayload:
    """Testa montagem do payload JSON."""

    def test_build_payload_structure(self, webhook, sample_report, sample_analysis):
        """Payload contem todos os campos obrigatorios."""
        with patch.dict("os.environ", {"N8N_EMAIL_TO": "test@test.com", "N8N_EMAIL_FROM": "from@test.com"}):
            payload = webhook.build_payload(sample_report, sample_analysis)

        # Verifica campos obrigatorios
        assert "timestamp" in payload
        assert "source" in payload
        assert "severity" in payload
        assert "error_count" in payload
        assert "warning_count" in payload
        assert "summary" in payload
        assert "full_report" in payload
        assert "email_to" in payload
        assert "email_from" in payload

        # Verifica valores
        assert payload["source"] == "LogAnalyzer AI"
        assert payload["error_count"] == 2
        assert payload["warning_count"] == 1
        assert payload["severity"] == "medium"
        assert payload["email_to"] == "test@test.com"
        assert payload["email_from"] == "from@test.com"

    def test_build_payload_severity_critical(self, webhook, sample_report):
        """Analise com eventos criticos retorna severity critical."""
        analysis = {
            "errors_found": [],
            "warnings_found": [],
            "critical_events": [{"level": "CRITICAL", "message": "System down"}],
        }

        payload = webhook.build_payload(sample_report, analysis)

        assert payload["severity"] == "critical"

    def test_build_payload_summary_truncated(self, webhook, sample_analysis):
        """Summary e truncado em 2000 caracteres."""
        long_report = "x" * 3000

        payload = webhook.build_payload(long_report, sample_analysis)

        assert len(payload["summary"]) == 2000
        assert payload["full_report"] == long_report


# ============================================
# Testes: send_report
# ============================================

class TestSendReport:
    """Testa envio de relatorio via webhook."""

    @patch("src.loganalyzer.integrations.webhook.requests.post")
    def test_send_report_success(self, mock_post, webhook, sample_report, sample_analysis):
        """Mock retorna 200, resultado e success=True."""
        # Configura mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Executa envio
        result = webhook.send_report(sample_report, sample_analysis)

        # Valida resultado
        assert result["success"] is True
        assert result["status_code"] == 200
        assert "sucesso" in result["message"]

        # Valida que request foi feito
        mock_post.assert_called_once()

    @patch("src.loganalyzer.integrations.webhook.requests.post")
    def test_send_report_timeout(self, mock_post, webhook, sample_report, sample_analysis):
        """Mock levanta Timeout, resultado e success=False."""
        import requests

        # Configura mock para levantar timeout
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")

        # Executa envio
        result = webhook.send_report(sample_report, sample_analysis)

        # Nao deve crashar
        assert result["success"] is False
        assert result["status_code"] is None
        assert "Timeout" in result["message"]

    @patch("src.loganalyzer.integrations.webhook.requests.post")
    def test_send_report_connection_error(self, mock_post, webhook, sample_report, sample_analysis):
        """Mock levanta ConnectionError, resultado e success=False."""
        import requests

        # Configura mock para erro de conexao
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        # Executa envio
        result = webhook.send_report(sample_report, sample_analysis)

        # Nao deve crashar
        assert result["success"] is False
        assert result["status_code"] is None
        assert "conexao" in result["message"]

    def test_send_report_disabled(self, sample_report, sample_analysis):
        """Webhook desabilitado nao faz request."""
        webhook = WebhookIntegration(
            webhook_url="http://localhost:5678/webhook/test",
            enabled=False,
        )

        result = webhook.send_report(sample_report, sample_analysis)

        assert result["success"] is False
        assert "desabilitado" in result["message"] or "nao configurado" in result["message"]


# ============================================
# Testes: is_configured
# ============================================

class TestIsConfigured:
    """Testa verificacao de configuracao."""

    def test_is_configured_without_url(self):
        """URL vazia retorna False."""
        webhook = WebhookIntegration(webhook_url="", enabled=True)
        assert webhook.is_configured() is False

    def test_is_configured_with_none_url(self):
        """URL None retorna False."""
        webhook = WebhookIntegration(webhook_url=None, enabled=True)
        assert webhook.is_configured() is False

    def test_is_configured_with_url(self):
        """URL valida e enabled=True retorna True."""
        webhook = WebhookIntegration(
            webhook_url="http://localhost:5678/webhook/loganalyzer",
            enabled=True,
        )
        assert webhook.is_configured() is True

    def test_is_configured_disabled(self):
        """URL valida mas enabled=False retorna False."""
        webhook = WebhookIntegration(
            webhook_url="http://localhost:5678/webhook/loganalyzer",
            enabled=False,
        )
        assert webhook.is_configured() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



# ============================================
# Testes: notify_webhook_node (integrado no LangGraph)
# ============================================

from src.loganalyzer.nodes import notify_webhook_node
from src.loganalyzer.agent import get_initial_state


class TestNotifyWebhookNode:
    """Testa o no notify_webhook_node integrado ao pipeline."""

    def test_notify_webhook_node_skips_when_disabled(self):
        """Sem env vars configuradas, no retorna state com webhook_status=skipped."""
        state = get_initial_state("examples/sample.log")

        # Garante que env vars nao estao setadas
        with patch.dict("os.environ", {}, clear=True):
            result = notify_webhook_node(state)

        assert result["webhook_status"] == "skipped"
        assert result["metadata"]["webhook_status"] == "skipped"

    @patch("src.loganalyzer.integrations.webhook.requests.post")
    def test_notify_webhook_node_sends_when_configured(self, mock_post):
        """Com env vars configuradas e mock 200, webhook_status=sent."""
        # Configura mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        state = get_initial_state("examples/sample.log")
        state["report"] = "Relatorio de teste"
        state["errors_found"] = [{"level": "ERROR", "message": "test"}]

        env_vars = {
            "N8N_WEBHOOK_URL": "http://localhost:5678/webhook/test",
            "N8N_WEBHOOK_ENABLED": "true",
        }

        with patch.dict("os.environ", env_vars):
            result = notify_webhook_node(state)

        assert result["webhook_status"] == "sent"
        assert result["metadata"]["webhook_status"] == "sent"
        mock_post.assert_called_once()

    @patch("src.loganalyzer.integrations.webhook.requests.post")
    def test_notify_webhook_node_error_does_not_crash(self, mock_post):
        """Erro de conexao nao crashar o pipeline, webhook_status=error."""
        import requests

        # Configura mock para erro
        mock_post.side_effect = requests.exceptions.ConnectionError("refused")

        state = get_initial_state("examples/sample.log")
        state["report"] = "Relatorio"

        env_vars = {
            "N8N_WEBHOOK_URL": "http://localhost:5678/webhook/test",
            "N8N_WEBHOOK_ENABLED": "true",
        }

        with patch.dict("os.environ", env_vars):
            result = notify_webhook_node(state)

        # Nao deve crashar
        assert result["webhook_status"] == "error"
        assert result["metadata"]["webhook_status"] == "error"
        # is_valid nao deve ser alterado pelo webhook
        assert result["is_valid"] is True

    def test_notify_webhook_node_populates_metadata(self):
        """metadata["webhook_status"] e preenchido independente do resultado."""
        state = get_initial_state("examples/sample.log")

        with patch.dict("os.environ", {}, clear=True):
            result = notify_webhook_node(state)

        assert "webhook_status" in result["metadata"]
        assert result["metadata"]["webhook_status"] in ("skipped", "sent", "error")
