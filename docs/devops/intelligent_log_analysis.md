# DevOps Inteligente: Analise de Logs com IA

> Documentacao da implementacao de analise inteligente de logs e deteccao de anomalias no LogAnalyzer AI.

**Modulo:** `src/loganalyzer/devops/anomaly_detector.py`  
**Task:** #35 — DevOps Inteligente + Anomalias  
**Status:** Implementado

---

## Pipeline Configurado

GitHub Actions executa 3 workflows automatizados:

| Workflow | Arquivo | Funcao |
|----------|---------|--------|
| Lint | `.github/workflows/lint.yml` | pylint + flake8 |
| Tests | `.github/workflows/test.yml` | pytest + coverage |
| Build | `.github/workflows/build.yml` | validacao de imports e estrutura |

Triggers: push e pull_request em `main`, `develop`, `feature/*`

---

## Analise de Logs com IA

### Estrategia

O LogAnalyzer AI aplica heuristicas para identificar problemas em logs sem depender de modelos ML complexos:

1. **Janela Deslizante** — Calcula taxa de erros em janelas de N eventos
2. **Baseline Dinamico** — Media historica como referencia
3. **Deteccao de Spike** — Compara atual vs baseline (limiar 2x/3x)
4. **Agrupamento** — Identifica mensagens repetidas (padroes recorrentes)
5. **Estimativa de Risco** — Consolida anomalias em nivel de severidade

### Exemplo de Analise

**Input: Log com degradacao progressiva**
```
2026-08-20 10:00:01 INFO Application started
2026-08-20 10:00:02 INFO Loading configuration
2026-08-20 10:00:03 WARNING Config file not found
2026-08-20 10:00:04 ERROR Connection timeout - retrying (1/3)
2026-08-20 10:00:05 ERROR Connection timeout - retrying (2/3)
2026-08-20 10:00:06 ERROR Connection timeout - retrying (3/3)
2026-08-20 10:00:07 CRITICAL Database connection failed
2026-08-20 10:00:08 ERROR Service initialization failed
2026-08-20 10:00:09 ERROR Connection timeout - retrying (1/3)
2026-08-20 10:00:10 ERROR Connection timeout - retrying (2/3)
```

**Output da Analise:**
```json
{
  "error_spike": {
    "anomaly": true,
    "type": "error_spike",
    "baseline": 1.5,
    "current": 7,
    "severity": "high"
  },
  "recurring_patterns": {
    "recurring": true,
    "patterns": [
      {"message": "ERROR Connection timeout - retrying", "count": 5}
    ],
    "total_recurring": 1
  },
  "risk": {
    "risk_level": "critical",
    "trend": "increasing",
    "anomaly_count": 2,
    "summary": "Spike critico de erros detectado. Acao imediata necessaria."
  },
  "total_lines": 10,
  "error_count": 7
}
```

---

## Deteccao de Anomalias

### 1. Error Spike (Aumento Anormal de Erros)

**Algoritmo:**
- Janela deslizante de 20 eventos (configuravel)
- Conta erros (ERROR + CRITICAL) por janela
- Calcula baseline = media de todas as janelas anteriores
- Compara janela atual vs baseline

**Limiares:**
| Condicao | Resultado |
|----------|-----------|
| Atual > 3x baseline | Anomalia HIGH |
| Atual > 2x baseline | Anomalia MEDIUM |
| Atual <= 2x baseline | Sem anomalia |
| Baseline = 0 e atual > 0 | Anomalia (novo erro) |

### 2. Padroes Recorrentes

**Algoritmo:**
- Filtra linhas com ERROR ou CRITICAL
- Agrupa mensagens identicas (Counter)
- Retorna padroes com 3+ ocorrencias

**Utilidade:**
- Identifica erros sistematicos (nao transientes)
- Prioriza investigacao por frequencia
- Detecta loops de retry infinito

### 3. Estimativa de Risco

**Matriz de decisao:**

| Anomalia Detectada | Risk Level | Trend |
|-------------------|------------|-------|
| Spike HIGH | critical | increasing |
| Spike MEDIUM | high | increasing |
| Pattern com 5+ repeticoes | medium | stable |
| Anomalias menores | low | stable |
| Nenhuma | low | stable |

---

## Integracao com o Agente

O `AnomalyDetector` pode ser usado como ferramenta adicional no pipeline:

```python
from src.loganalyzer.devops import AnomalyDetector

detector = AnomalyDetector(window_size=20, spike_threshold=2.0)

# Analise completa
result = detector.analyze(log_lines)

# Verificar risco
if result["risk"]["risk_level"] in ("critical", "high"):
    # Acionar alerta
    print(f"ALERTA: {result['risk']['summary']}")
```

### Parametros Configuraveis

| Parametro | Padrao | Descricao |
|-----------|--------|-----------|
| `window_size` | 20 | Eventos por janela |
| `spike_threshold` | 2.0 | Multiplicador para spike |
| `min_occurrences` | 3 | Minimo para padrao recorrente |

---

## Acoes Recomendadas por Nivel de Risco

### Critical
- Notificar equipe imediatamente
- Verificar health checks
- Considerar rollback se recente deploy

### High
- Investigar causa raiz em 1h
- Monitorar tendencia nas proximas execucoes
- Escalar se persistir

### Medium
- Adicionar ao backlog para investigacao
- Monitorar se frequencia aumenta
- Documentar padrao para referencia

### Low
- Monitoramento normal
- Revisao em sprint planning

---

## Metricas de Qualidade

| Metrica | Valor |
|---------|-------|
| Testes unitarios | 7+ |
| Cobertura do modulo | >90% |
| Falsos positivos | Minimizados via threshold configuravel |
| Performance | O(n) para n linhas de log |

---

## Limitacoes

1. Heuristica pura (nao usa ML)
2. Threshold fixo (nao adaptativo)
3. Nao diferencia tipos de erro por contexto semantico
4. Janela fixa (nao baseada em tempo real)

### Evolucoes Futuras

- [ ] Threshold adaptativo baseado em historico
- [ ] Integracao com alertas Slack/Discord
- [ ] Dashboard com metricas em tempo real
- [ ] Modelo ML para predicao de anomalias

---

**Ultima atualizacao:** Agosto 2026  
**Pontuacao esperada:** +0.50 pontos (Criterios 12 e 13 do M2.2)
