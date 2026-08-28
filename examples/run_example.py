"""
Script de exemplo para executar LogAnalyzer AI.

Demonstra como usar o agente para analisar um arquivo de log.
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loganalyzer.agent import create_agent_graph, get_initial_state


def main():
    """
    Executa exemplo de análise de log.
    """
    print("=" * 60)
    print("LogAnalyzer AI - Exemplo de Uso")
    print("=" * 60)
    print()

    # Define caminho do log de exemplo
    log_file = Path(__file__).parent / "sample_critical.log"

    if not log_file.exists():
        print(f"[ERRO] Arquivo de exemplo nao encontrado: {log_file}")
        return 1

    print(f"[LOG] Analisando arquivo: {log_file}")
    print()

    try:
        # Cria agente
        print("[INFO] Inicializando agente...")
        agent = create_agent_graph()

        # Cria estado inicial
        initial_state = get_initial_state(str(log_file))

        # Executa agente
        print("[INFO] Processando log...")
        print()

        final_state = agent.invoke(initial_state)

        # Verifica sucesso
        if not final_state.get("is_valid", False):
            error_msg = final_state.get("error_message", "Erro desconhecido")
            print(f"[ERRO] Erro: {error_msg}")
            return 1

        print("[OK] Analise concluida com sucesso!")
        print()

        # ============================================
        # Exibe Relatório
        # ============================================
        report = final_state.get("report", "")
        if report:
            print("=" * 60)
            print("RELATORIO GERADO:")
            print("=" * 60)
            print()
            print(report)
        else:
            print("[AVISO] Nenhum relatorio foi gerado")

        print()
        print("=" * 60)
        print("[OK] Exemplo concluido")
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n[AVISO] Interrompido pelo usuario")
        return 130

    except Exception as e:
        print(f"[ERRO] Erro nao esperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
