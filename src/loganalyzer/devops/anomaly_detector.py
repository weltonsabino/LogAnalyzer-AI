"""
Detector de anomalias para analise inteligente de logs.

Implementa heuristicas para identificar:
- Spikes de erro (aumento anormal acima do baseline)
- Padroes recorrentes (mesma mensagem repetida N vezes)
- Estimativa de risco (severidade + tendencia)

Implementacao: Task #35 (DevOps Inteligente + Anomalias)
"""

from typing import Dict, List, Any
from collections import Counter


class AnomalyDetector:
    """
    Detecta anomalias em logs e metricas usando heuristicas.

    Responsavel por:
    - Identificar spikes de erro via janela deslizante
    - Detectar padroes recorrentes por agrupamento
    - Estimar risco com severidade e tendencia
    - Orquestrar analise completa
    """

    def __init__(self, window_size: int = 20, spike_threshold: float = 2.0):
        """
        Inicializa detector com parametros de configuracao.

        Argumentos:
            window_size: Tamanho da janela deslizante para calculo de baseline
            spike_threshold: Multiplicador para considerar spike (padrao 2x)
        """
        # Tamanho da janela para calculo de media
        self.window_size = window_size
        # Limiar para deteccao de spike
        self.spike_threshold = spike_threshold

    def detect_error_spike(self, log_lines: List[str]) -> Dict[str, Any]:
        """
        Detecta aumento anormal de erros usando janela deslizante.

        Calcula baseline (media de erros por janela) e compara com
        a janela mais recente. Se atual > threshold * baseline, e anomalia.

        Argumentos:
            log_lines: Lista de linhas de log (cada linha e uma string)

        Retorno:
            Dicionario com resultado da deteccao:
            - anomaly: True/False
            - type: "error_spike" (se anomalia)
            - baseline: media de erros por janela
            - current: erros na janela atual
            - severity: "high" (>3x) ou "medium" (>2x)
        """
        # Precisa de linhas suficientes para calcular baseline
        if len(log_lines) < self.window_size:
            return {"anomaly": False, "reason": "insufficient_data"}

        # Calcula taxa de erros por janela deslizante
        error_rates = []
        for i in range(len(log_lines) - self.window_size + 1):
            window = log_lines[i:i + self.window_size]
            error_count = sum(
                1 for line in window
                if "ERROR" in line.upper() or "CRITICAL" in line.upper()
            )
            error_rates.append(error_count)

        # Se nao ha janelas suficientes
        if not error_rates:
            return {"anomaly": False, "reason": "no_windows"}

        # Calcula baseline (media de todas as janelas exceto a ultima)
        if len(error_rates) > 1:
            baseline = sum(error_rates[:-1]) / len(error_rates[:-1])
        else:
            baseline = error_rates[0]

        # Valor atual (ultima janela)
        current = error_rates[-1]

        # Verifica spike: atual > threshold * baseline
        if baseline > 0 and current > self.spike_threshold * baseline:
            severity = "high" if current > baseline * 3 else "medium"
            return {
                "anomaly": True,
                "type": "error_spike",
                "baseline": round(baseline, 2),
                "current": current,
                "severity": severity,
            }

        # Caso especial: baseline 0 mas ha erros agora
        if baseline == 0 and current > 0:
            return {
                "anomaly": True,
                "type": "error_spike",
                "baseline": 0,
                "current": current,
                "severity": "high" if current >= 5 else "medium",
            }

        return {"anomaly": False, "baseline": round(baseline, 2), "current": current}

    def detect_recurring_pattern(
        self, log_lines: List[str], min_occurrences: int = 3
    ) -> Dict[str, Any]:
        """
        Detecta padroes recorrentes em logs (mesma mensagem repetida).

        Agrupa mensagens de erro identicas e retorna aquelas que
        aparecem min_occurrences ou mais vezes.

        Argumentos:
            log_lines: Lista de linhas de log
            min_occurrences: Minimo de repeticoes para considerar padrao

        Retorno:
            Dicionario com resultado:
            - recurring: True/False
            - patterns: Lista de padroes com contagem
            - total_recurring: Numero total de padroes recorrentes
        """
        # Filtra apenas linhas de erro
        error_lines = [
            line for line in log_lines
            if "ERROR" in line.upper() or "CRITICAL" in line.upper()
        ]

        # Se nao ha erros, nao ha padrao
        if not error_lines:
            return {"recurring": False, "patterns": [], "total_recurring": 0}

        # Conta ocorrencias de cada mensagem
        message_counts = Counter(error_lines)

        # Filtra apenas padroes recorrentes (>= min_occurrences)
        recurring_patterns = [
            {"message": msg, "count": count}
            for msg, count in message_counts.most_common()
            if count >= min_occurrences
        ]

        return {
            "recurring": len(recurring_patterns) > 0,
            "patterns": recurring_patterns,
            "total_recurring": len(recurring_patterns),
        }

    def estimate_risk(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estima risco com base nas anomalias detectadas.

        Calcula severidade geral e tendencia baseado nos tipos
        e quantidades de anomalias encontradas.

        Argumentos:
            anomalies: Lista de anomalias detectadas (spike + patterns)

        Retorno:
            Dicionario com estimativa de risco:
            - risk_level: "critical" | "high" | "medium" | "low"
            - trend: "increasing" | "stable" | "decreasing"
            - anomaly_count: Numero de anomalias
            - summary: Resumo textual do risco
        """
        # Sem anomalias = risco baixo
        if not anomalies:
            return {
                "risk_level": "low",
                "trend": "stable",
                "anomaly_count": 0,
                "summary": "Nenhuma anomalia detectada. Sistema estavel.",
            }

        # Classifica severidade das anomalias
        has_high_spike = any(
            a.get("type") == "error_spike" and a.get("severity") == "high"
            for a in anomalies
        )
        has_medium_spike = any(
            a.get("type") == "error_spike" and a.get("severity") == "medium"
            for a in anomalies
        )
        has_heavy_recurring = any(
            a.get("recurring") and any(
                p.get("count", 0) >= 5 for p in a.get("patterns", [])
            )
            for a in anomalies
        )

        # Determina nivel de risco
        if has_high_spike:
            risk_level = "critical"
            trend = "increasing"
            summary = "Spike critico de erros detectado. Acao imediata necessaria."
        elif has_medium_spike:
            risk_level = "high"
            trend = "increasing"
            summary = "Aumento significativo de erros. Monitoramento urgente."
        elif has_heavy_recurring:
            risk_level = "medium"
            trend = "stable"
            summary = "Padroes recorrentes detectados. Investigacao recomendada."
        else:
            risk_level = "low"
            trend = "stable"
            summary = "Anomalias menores detectadas. Monitoramento normal."

        return {
            "risk_level": risk_level,
            "trend": trend,
            "anomaly_count": len(anomalies),
            "summary": summary,
        }

    def analyze(self, log_lines: List[str]) -> Dict[str, Any]:
        """
        Executa analise completa: deteccao de anomalias + estimativa de risco.

        Orquestra todas as heuristicas e retorna resultado consolidado
        com spike detection, padroes recorrentes e risco estimado.

        Argumentos:
            log_lines: Lista de linhas de log para analisar

        Retorno:
            Dicionario consolidado com:
            - error_spike: Resultado de detect_error_spike
            - recurring_patterns: Resultado de detect_recurring_pattern
            - risk: Resultado de estimate_risk
            - total_lines: Numero de linhas analisadas
            - error_count: Total de linhas com erro
        """
        # Executa deteccoes individuais
        spike_result = self.detect_error_spike(log_lines)
        pattern_result = self.detect_recurring_pattern(log_lines)

        # Coleta anomalias para estimativa de risco
        anomalies = []
        if spike_result.get("anomaly"):
            anomalies.append(spike_result)
        if pattern_result.get("recurring"):
            anomalies.append(pattern_result)

        # Estima risco consolidado
        risk_result = self.estimate_risk(anomalies)

        # Conta total de erros
        error_count = sum(
            1 for line in log_lines
            if "ERROR" in line.upper() or "CRITICAL" in line.upper()
        )

        return {
            "error_spike": spike_result,
            "recurring_patterns": pattern_result,
            "risk": risk_result,
            "total_lines": len(log_lines),
            "error_count": error_count,
        }
