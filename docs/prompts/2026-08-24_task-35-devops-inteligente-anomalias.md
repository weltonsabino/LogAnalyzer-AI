Prompt: Implementar Task #35 - DevOps Inteligente + Deteccao de Anomalias
Responsavel: Welton Sabino
Usuario: welton-sabino
Data/hora: 2026-08-24 21:22:00

## Prompt original

Implementar **Task #35: DevOps Inteligente + Deteccao de Anomalias**.

Objetivo: Implementar analise inteligente de logs e deteccao de anomalias com heuristicas, integrando ao pipeline existente do LogAnalyzer AI.

**IMPORTANTE: NAO fazer commit, NAO fazer push, NAO criar branches. Apenas implementar os arquivos e rodar testes localmente.**

---

## Descricao Detalhada

### O que fazer:

**1. Documentacao de Analise de Logs com IA**
- Criar arquivo `docs/devops/intelligent_log_analysis.md` (~150 linhas)
- Secoes obrigatorias:
  - Pipeline configurado (GitHub Actions: lint, tests, build)
  - Analise de logs com IA (exemplos reais de prompts e respostas)
  - Deteccao de anomalias (error spike, padroes recorrentes)
  - Estimativa de risco (tendencia, severidade)
  - Acoes recomendadas baseadas na analise
  - Integracao com o agente LogAnalyzer AI

**2. Implementar AnomalyDetector**
- Criar `src/loganalyzer/devops/__init__.py`
- Criar `src/loganalyzer/devops/anomaly_detector.py` (~120 linhas)
- Classe `AnomalyDetector` com metodos:
  - `detect_error_spike(log_lines: list) -> dict` — Detecta aumento anormal de erros. Baseline = media de erros por janela. Anomalia = >2x baseline.
  - `detect_recurring_pattern(log_lines: list, window_minutes: int = 5) -> dict` — Detecta padroes recorrentes (mesmo erro N vezes em janela de tempo)
  - `estimate_risk(anomalies: list) -> dict` — Estima risco com severidade (low/medium/high/critical) e tendencia
  - `analyze(log_lines: list) -> dict` — Metodo principal que orquestra deteccao + risco

Logica do `detect_error_spike`:
```python
# Janela deslizante de 20 eventos
# Conta erros por janela
# Baseline = media de todas as janelas
# Se janela atual > 2x baseline → anomalia medium
# Se janela atual > 3x baseline → anomalia high
```

Logica do `detect_recurring_pattern`:
```python
# Agrupa mensagens de erro identicas
# Se mesmo erro aparece 3+ vezes → padrao recorrente
# Retorna top patterns com contagem
```

Logica do `estimate_risk`:
```python
# Se tem anomalia high → risco critical
# Se tem anomalia medium → risco high
# Se tem padrao recorrente com 5+ ocorrencias → risco medium
# Senao → risco low
# Inclui tendencia (increasing/stable/decreasing)
```

**3. Testes**
- Criar `tests/test_devops_anomaly.py` (~100 linhas)
- Minimo 6 testes:
  - `test_detect_error_spike_normal_log` — log sem anomalia retorna `{"anomaly": False}`
  - `test_detect_error_spike_detected` — log com spike retorna anomalia
  - `test_detect_error_spike_severity_high` — spike >3x retorna severity high
  - `test_detect_recurring_pattern_found` — padrao recorrente detectado
  - `test_detect_recurring_pattern_none` — sem padrao recorrente
  - `test_estimate_risk_critical` — anomalia high → risco critical
  - `test_analyze_complete_pipeline` — metodo analyze retorna estrutura completa

**4. Integracao (opcional se tempo permitir)**
- Registrar AnomalyDetector como ferramenta disponivel no agente
- Adicionar no `__init__.py` do pacote devops

---

## Criterios de Aceite

- [ ] `docs/devops/intelligent_log_analysis.md` existe com ~150 linhas
- [ ] `src/loganalyzer/devops/anomaly_detector.py` existe com classe AnomalyDetector
- [ ] `src/loganalyzer/devops/__init__.py` existe com exports
- [ ] `tests/test_devops_anomaly.py` existe com 6+ testes
- [ ] Todos os testes passam localmente (`pytest tests/test_devops_anomaly.py -v`)
- [ ] Todos os 194+ testes existentes continuam passando
- [ ] Codigo segue convencoes: comentarios PT, variaveis EN, docstrings PT
- [ ] Nenhum commit ou push realizado

---

## Restricoes

- **NAO** fazer `git commit`
- **NAO** fazer `git push`
- **NAO** criar branches
- **NAO** alterar arquivos existentes que nao sejam necessarios
- **NAO** adicionar dependencias externas (usar apenas stdlib + libs ja no requirements.txt)
- Apenas criar os arquivos novos e validar que testes passam

---

## Referencia de Estrutura

```
src/loganalyzer/devops/
├── __init__.py
└── anomaly_detector.py

docs/devops/
└── intelligent_log_analysis.md

tests/
└── test_devops_anomaly.py
```

---

## Pontuacao Esperada

+0.50 pontos (Criterios 12 e 13 do M2.2: DevOps inteligente + Deteccao de anomalias)
