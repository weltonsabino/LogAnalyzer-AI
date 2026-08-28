"""
Entrypoint do LogAnalyzer AI.

Fornece interface CLI para executar análise de logs usando o agente.
"""

import sys
import json
import argparse
import os
import traceback
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.loganalyzer.agent import create_agent_graph, get_initial_state
from src.loganalyzer.models import LogAnalysisState

# Configure UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Carrega variaveis de ambiente do .env
load_dotenv()

# Adiciona diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def main():
    """
    Entrypoint principal do LogAnalyzer AI.

    Processa argumentos CLI e executa análise de log.
    """
    # Configura argumentos CLI
    parser = argparse.ArgumentParser(
        description="LogAnalyzer AI - Análise Automatizada de Arquivos de Log",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m loganalyzer.main /path/to/log.txt
  python -m loganalyzer.main /path/to/log.txt --output report.md
  python -m loganalyzer.main /path/to/log.txt --json
        """
    )

    parser.add_argument(
        "file_path",
        help="Caminho do arquivo de log a analisar"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Caminho de arquivo para salvar relatório (padrão: stdout)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Retorna resultado em JSON em vez de markdown"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostra informações detalhadas de execução"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "groq"],
        default=None,
        help="Provedor LLM a usar (padrão: openai). Sobrescreve variável LLM_PROVIDER"
    )

    # Parseia argumentos
    args = parser.parse_args()

    # Executa análise
    exit_code = analyze_log_file(
        file_path=args.file_path,
        output_path=args.output,
        output_json=args.json,
        verbose=args.verbose,
        provider=args.provider,
    )

    sys.exit(exit_code)


def analyze_log_file(
    file_path: str,
    output_path: Optional[str] = None,
    output_json: bool = False,
    verbose: bool = False,
    provider: Optional[str] = None,
) -> int:
    """
    Analisa arquivo de log usando o agente LogAnalyzer.

    Argumentos:
        file_path: Caminho do arquivo de log
        output_path: Caminho para salvar relatório (opcional)
        output_json: Se True, retorna JSON em vez de markdown
        verbose: Se True, mostra informações detalhadas
        provider: Provedor LLM (openai ou groq). Sobrescreve LLM_PROVIDER env.

    Retorno:
        Código de saída (0 = sucesso, 1 = erro)
    """
    try:
        if verbose:
            print("ℹ️  Inicializando LogAnalyzer AI...")
            print(f"📄 Arquivo de log: {file_path}")

        if verbose:
            print("🚀 Criando agente e iniciando análise...")

        # Cria agente
        agent = create_agent_graph()

        # Cria estado inicial com provider
        initial_state = get_initial_state(file_path, provider=provider)

        # Executa agente
        if verbose:
            print("⏳ Processando log...")

        final_state = agent.invoke(initial_state)

        # Verifica se execução foi bem-sucedida
        if not final_state.get("is_valid", False):
            error_msg = final_state.get("error_message", "Erro desconhecido")
            governance_status = final_state.get("metadata", {}).get("governance_status", "")
            governance_reason = final_state.get("metadata", {}).get("governance_reason", "")
            
            # Se foi bloqueado por governança, mostra mensagem específica
            if governance_status == "bloqueado":
                print(f"🛡️  BLOQUEADO POR SEGURANÇA", file=sys.stderr)
                print(f"   Motivo: {governance_reason}", file=sys.stderr)
                if verbose:
                    print(f"   Detalhes: {error_msg}", file=sys.stderr)
            else:
                print(f"❌ Erro durante análise: {error_msg}", file=sys.stderr)
            return 1

        if verbose:
            print("✅ Análise concluída com sucesso")

        # Formata saída
        if output_json:
            output_content = _format_json_output(final_state)
        else:
            output_content = final_state.get("report", "")

        # Salva ou mostra resultado
        if output_path:
            if verbose:
                print(f"💾 Salvando relatório em: {output_path}")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)

            print(f"✅ Relatório salvo em: {output_path}")
        else:
            print(output_content)

        if verbose:
            print("✅ Concluído!")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Análise cancelada pelo usuário", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"❌ Erro não esperado: {str(e)}", file=sys.stderr)
        if verbose:
            traceback.print_exc()
        return 1


def _format_json_output(state: LogAnalysisState) -> str:
    """
    Formata estado do agente como JSON estruturado.

    Argumentos:
        state: Estado final da execução

    Retorno:
        String JSON formatada
    """
    output = {
        "status": "sucesso" if state.get("is_valid") else "erro",
        "error_message": state.get("error_message"),
        "summary": {
            "total_events": state.get("metadata", {}).get("parsed_events_count", 0),
            "errors": len(state.get("errors_found", [])),
            "warnings": len(state.get("warnings_found", [])),
            "critical": len(state.get("critical_events", [])),
        },
        "analysis": state.get("analysis_result", {}),
        "metadata": state.get("metadata", {}),
    }

    return json.dumps(output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
