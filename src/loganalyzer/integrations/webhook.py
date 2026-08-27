"""
Integracao via webhook HTTP para plataformas low-code (n8n).

Envia resultados de analise do LogAnalyzer AI para um endpoint
webhook configuravel, permitindo automacao de notificacoes por email.

Implementacao: Task #36 (Low-Code Integration)
"""

from datetime import datetime
from typing import Any, Dict, Optional
import os

import requests


class WebhookIntegration:
    """
    Envia resultados de analise para webhook HTTP (n8n, Make, Zapier).

    Responsavel por:
    - Montar payload estruturado com severidade e resumo
    - Enviar via POST com timeout configuravel
    - Tratar erros de conexao sem crashar a aplicacao
    """

    def __init__(self, webhook_url: Optional[str] = None, enabled: bool = True):
        """
        Inicializa integracao com URL do webhook.

        Argumentos:
            webhook_url: URL do endpoint webhook (ex: http://localhost:5678/webhook/loganalyzer)
            enabled: Se True, envia requests. Se False, desabilita envio.
        """
        # URL do endpoint webhook
        self.webhook_url = webhook_url
        # Flag para habilitar/desabilitar envio
        self.enabled = enabled
        # Timeout padrao para requests (segundos)
        self.timeout = 10

    def is_configured(self) -> bool:
        """
        Verifica se o webhook esta configurado corretamente.

        Retorno:
            True se URL valida e integracao habilitada, False caso contrario.
        """
        # Verifica se URL esta preenchida e habilitado
        if not self.enabled:
            return False
        if not self.webhook_url or not self.webhook_url.strip():
            return False
        return True

    def build_payload(self, report: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monta payload JSON para envio ao webhook.

        Argumentos:
            report: Relatorio completo em markdown
            analysis: Dicionario com resultados da analise

        Retorno:
            Dicionario estruturado com campos para o webhook
        """
        # Extrai severidade da analise
        severity = self._extract_severity(analysis)

        # Conta erros e warnings
        error_count = len(analysis.get("errors_found", []))
        warning_count = len(analysis.get("warnings_found", []))

        # Monta payload estruturado
        payload = {
            "timestamp": datetime.now().isoformat(),
            "source": "LogAnalyzer AI",
            "severity": severity,
            "error_count": error_count,
            "warning_count": warning_count,
            "summary": report[:2000] if report else "",
            "full_report": report,
            "email_to": os.getenv("N8N_EMAIL_TO", ""),
            "email_from": os.getenv("N8N_EMAIL_FROM", ""),
        }

        return payload

    def send_report(self, report: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia relatorio para o webhook configurado.

        Argumentos:
            report: Relatorio completo em markdown
            analysis: Dicionario com resultados da analise

        Retorno:
            Dicionario com resultado do envio:
            - success: True/False
            - status_code: codigo HTTP (ou None se erro)
            - message: descricao do resultado
        """
        # Verifica se esta configurado
        if not self.is_configured():
            return {
                "success": False,
                "status_code": None,
                "message": "Webhook nao configurado ou desabilitado",
            }

        # Monta payload
        payload = self.build_payload(report, analysis)

        # Envia request POST
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
            )

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "message": "Webhook enviado com sucesso"
                if response.status_code == 200
                else f"Webhook retornou status {response.status_code}",
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status_code": None,
                "message": "Timeout ao enviar para webhook",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status_code": None,
                "message": "Erro de conexao com webhook",
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "message": f"Erro inesperado: {str(e)}",
            }

    def _extract_severity(self, analysis: Dict[str, Any]) -> str:
        """
        Extrai nivel de severidade da analise.

        Argumentos:
            analysis: Dicionario com resultados da analise

        Retorno:
            String com nivel: "critical", "high", "medium" ou "low"
        """
        # Tenta extrair de campos conhecidos
        critical_events = analysis.get("critical_events", [])
        errors_found = analysis.get("errors_found", [])
        warnings_found = analysis.get("warnings_found", [])

        if critical_events:
            return "critical"
        if len(errors_found) >= 5:
            return "high"
        if len(errors_found) >= 1:
            return "medium"
        if len(warnings_found) >= 3:
            return "medium"
        if len(warnings_found) >= 1:
            return "low"
        return "low"
