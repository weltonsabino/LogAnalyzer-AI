"""
Script de demonstracao: executa analise e envia resultado via webhook.

O webhook e enviado automaticamente pelo no notify_webhook_node
dentro do pipeline LangGraph. Este script apenas executa o pipeline
e mostra o resultado.

Uso:
    python examples/run_with_webhook.py

Requer:
    - .env configurado com N8N_WEBHOOK_URL, N8N_WEBHOOK_ENABLED, N8N_EMAIL_TO, N8N_EMAIL_FROM
    - n8n rodando (local via Docker ou cloud)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Adiciona raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.loganalyzer.agent import create_agent_graph, get_initial_state


def main():
    """Executa analise — webhook e disparado automaticamente pelo pipeline."""
    # Carrega variaveis de ambiente
    load_dotenv()

    # Verifica configuracao do webhook
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
    webhook_enabled = os.getenv("N8N_WEBHOOK_ENABLED", "false").lower() == "true"

    if not webhook_url or not webhook_enabled:
        print("[AVISO] Webhook nao configurado. Verifique .env")
        print(f"  N8N_WEBHOOK_URL={webhook_url}")
        print(f"  N8N_WEBHOOK_ENABLED={webhook_enabled}")

    # Executa analise
    sample_log = str(project_root / "examples" / "sample_critical.log")
    print(f"[INFO] Analisando: {sample_log}")

    graph = create_agent_graph()
    state = get_initial_state(sample_log)
    result = graph.invoke(state)

    print(f"[INFO] Analise concluida. Valid={result['is_valid']}")
    print(f"[INFO] Erros: {len(result.get('errors_found', []))}")
    print(f"[INFO] Warnings: {len(result.get('warnings_found', []))}")

    # Webhook e enviado automaticamente pelo no notify_webhook no pipeline
    webhook_status = result.get("webhook_status", "unknown")
    if webhook_status == "sent":
        print(f"[INFO] Webhook enviado com sucesso (status: 200)")
    elif webhook_status == "skipped":
        print(f"[AVISO] Webhook ignorado (nao configurado ou desabilitado)")
    elif webhook_status == "error":
        webhook_error = result.get("metadata", {}).get("webhook_error", "erro desconhecido")
        print(f"[ERRO] Webhook falhou: {webhook_error}")
    else:
        print(f"[INFO] Webhook status: {webhook_status}")


if __name__ == "__main__":
    main()
