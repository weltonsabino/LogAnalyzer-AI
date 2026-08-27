"""
Modulo de integracoes externas do LogAnalyzer AI.

Fornece integracao com plataformas low-code via webhook HTTP
para envio automatico de resultados de analise.
"""

from src.loganalyzer.integrations.webhook import WebhookIntegration

__all__ = ["WebhookIntegration"]
