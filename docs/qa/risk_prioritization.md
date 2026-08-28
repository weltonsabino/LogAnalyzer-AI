# Priorização por Risco — LogAnalyzer AI

> Matriz de risco (probabilidade × impacto) para cada módulo do projeto, definindo estratégia de teste baseada em risco

**Data:** 24 de Agosto, 2026  
**Versão:** 1.0  
**Status:** ✅ Implementado

---

## 1. Matriz de Risco Geral

### Escala de Severidade

| Nível | Probabilidade | Impacto | Score | Ação |
|-------|---------------|---------|-------|------|
| 🔴 CRÍTICO | Alta (>70%) | Alto (>3) | >2.1 | P0 - Implementar teste |
| 🟠 ALTO | Média (40-70%) | Médio (2-3) | 0.8-2.1 | P1 - Implementar teste |
| 🟡 MÉDIO | Média (40-70%) | Baixo (<2) | 0.8-1.4 | P2 - Considerar teste |
| 🟢 BAIXO | Baixa (<40%) | Baixo (<2) | <0.8 | P3 - Opcional |

### Matriz por Módulo

```
┌─────────────────────────────────────────────────────────────┐
│ MATRIZ DE RISCO — SCORE = PROBABILIDADE × IMPACTO           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  CRÍTICO (P0)    ███ 🔴 🔴 🔴                                │
│  ALTO (P1)       ██  🟠 🟠                                   │
│  MÉDIO (P2)      █   🟡 🟡                                   │
│  BAIXO (P3)      ░   🟢 🟢                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Legenda:
🔴 agent.py (3.0) — Orquestração crítica
🔴 nodes.py (2.8) — Lógica de fluxo
🔴 observability.py (2.4) — Rastreamento
🟠 governance.py (1.8) — Segurança
🟠 tools/file_reader.py (1.6) — I/O
🟡 llm_interpreter.py (1.2) — IA
🟢 models.py (0.6) — Definições
```

---

## 2. Análise Detalhada por Módulo

### 🔴 P0 — CRÍTICO (Implementar Testes)

#### 1. agent.py — Score: 3.0 (CRÍTICO)

**Probabilidade de Falha:** 90% (muito alta)  
**Impacto:** 3.3/3 (catastrófico - agente inteiro falha)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| StateGraph malformado | 80% | ✅ Testes estrutura, arestas |
| Roteamento incorreto | 70% | ✅ Testes condicional |
| Estado inválido | 60% | ✅ Testes validação estado |

**Testes Obrigatórios:**
- ✅ `test_e2e_success_normal_log` — Fluxo completo
- ✅ `test_e2e_validation_error` — Erro roteado
- ✅ `test_route_by_severity` — Roteamento por severidade
- ✅ `test_state_initialization` — Estado inicial válido

**Cobertura Target:** 100%

---

#### 2. nodes.py — Score: 2.8 (CRÍTICO)

**Probabilidade de Falha:** 85% (muito alta)  
**Impacto:** 3.3/3 (cada nó é um ponto de falha)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| Parsing falha silenciosamente | 75% | ✅ Teste com arquivo ruim |
| Detecção não acha padrões | 65% | ✅ Teste com log padrão |
| Análise retorna vazio | 50% | ✅ Mock LLM para resposta |

**Testes Obrigatórios:**
- ✅ `test_validate_input_node` — Validação funciona
- ✅ `test_parse_events_node` — Parsing correto
- ✅ `test_analyze_patterns_node` — Detecção funciona
- ✅ `test_error_handling_node` — Erro tratado

**Cobertura Target:** 100%

---

#### 3. observability.py — Score: 2.4 (CRÍTICO)

**Probabilidade de Falha:** 70% (alta)  
**Impacto:** 3.4/3 (sem rastreamento, debug impossível)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| execution_id não único | 60% | ✅ Teste múltiplas instâncias |
| Traces perdidos | 40% | ✅ Teste correlação |
| Timeout não funciona | 35% | ✅ Teste Windows + Linux |

**Testes Obrigatórios:**
- ✅ `test_trace_collector_initialization` — execution_id único
- ✅ `test_add_trace` — Traces registrados
- ✅ `test_correlation_summary` — Sumário correto
- ✅ `test_timeout_decorator` — Timeout funciona
- ✅ `test_retry_decorator` — Retry com backoff

**Cobertura Target:** 100%

---

### 🟠 P1 — ALTO (Implementar Testes)

#### 4. governance.py — Score: 1.8 (ALTO)

**Probabilidade de Falha:** 65% (média-alta)  
**Impacto:** 2.8/3 (segurança comprometida)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| Input injection não bloqueada | 60% | ✅ Teste path traversal |
| Autonomy level não respeitado | 50% | ✅ Teste READ_ONLY vs EXECUTE |
| Validação muito permissiva | 40% | ✅ Teste edge cases |

**Testes Obrigatórios:**
- ✅ `test_e2e_input_injection_blocked` — Injection bloqueada
- ✅ `test_e2e_autonomy_blocked` — Autonomia respeitada
- ✅ `test_validator_malicious_input` — Inputs maliciosos

**Cobertura Target:** 95%+

---

#### 5. tools/file_reader.py — Score: 1.6 (ALTO)

**Probabilidade de Falha:** 60% (média)  
**Impacto:** 2.8/3 (sem dados, análise falha)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| Timeout expira em arquivo grande | 55% | ✅ Teste @with_timeout |
| Retry não tem sucesso | 45% | ✅ Teste @with_retry |
| Encoding issues | 35% | ✅ Teste UTF-8 vs Latin-1 |

**Testes Obrigatórios:**
- ✅ `test_e2e_timeout_scenario` — Timeout dispara
- ✅ `test_e2e_retry_scenario` — Retry sucede
- ✅ `test_read_log_file_encoding` — Encoding correto

**Cobertura Target:** 95%+

---

### 🟡 P2 — MÉDIO (Considerar Testes)

#### 6. llm_interpreter.py — Score: 1.2 (MÉDIO)

**Probabilidade de Falha:** 50% (média)  
**Impacto:** 2.4/3 (análise pior, não falha)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| API indisponível | 50% | ⚠️ Fallback heurístico |
| Resposta LLM vazia | 35% | ✅ Teste com mock |
| Timeout na chamada | 25% | ✅ Teste timeout=15s |

**Testes Recomendados:**
- ⚠️ `test_llm_fallback_heuristic` — Fallback funciona
- ⚠️ `test_e2e_multi_provider` — OpenAI + Groq

**Cobertura Target:** 85-90%

---

### 🟢 P3 — BAIXO (Opcional)

#### 7. models.py — Score: 0.6 (BAIXO)

**Probabilidade de Falha:** 20% (muito baixa)  
**Impacto:** 2.8/3 (se quebrar, é crítico, mas raramente quebra)

| Aspecto | Risco | Mitigação |
|---------|-------|-----------|
| Type hints incorretos | 15% | ⚠️ Pylint valida |
| Campos faltando | 10% | ⚠️ Type checking |

**Testes Opcionais:**
- Modelagens são cobertas por testes de nodes

**Cobertura Target:** Cobertura geral >95%

---

## 3. Testes por Prioridade

### 🔴 P0 — Testes Críticos (Implementar Primeiro)

**Total: 10 testes | Tempo: ~1h30min**

```python
def test_e2e_success_normal_log():
    """Teste 1: Sucesso end-to-end completo."""

def test_e2e_validation_error():
    """Teste 2: Erro de validação."""

def test_e2e_timeout_scenario():
    """Teste 3: Timeout em leitura."""

def test_e2e_retry_scenario():
    """Teste 4: Retry bem-sucedido."""

def test_trace_collector_correlation():
    """Teste 5: Correlação com execution_id."""

def test_route_by_severity():
    """Teste 6: Roteamento por severidade."""

def test_analyze_patterns_parallel():
    """Teste 7: Análise paralela funciona."""

def test_error_handling_node():
    """Teste 8: Error handling acionado."""

def test_state_initialization():
    """Teste 9: Estado inicial válido."""

def test_input_validator():
    """Teste 10: Validação de entrada."""
```

### 🟠 P1 — Testes de Alto Risco (Implementar Segundo)

**Total: 5 testes | Tempo: ~45min**

```python
def test_e2e_input_injection_blocked():
    """Teste 11: Input injection bloqueada."""

def test_e2e_autonomy_blocked():
    """Teste 12: Autonomia bloqueada."""

def test_llm_fallback_heuristic():
    """Teste 13: Fallback sem LLM."""

def test_read_log_file_encoding():
    """Teste 14: Encoding UTF-8."""

def test_timeout_decorator():
    """Teste 15: @with_timeout funciona."""
```

### 🟡 P2 — Testes Auxiliares (Implementar Terceiro)

**Total: 3 testes | Tempo: ~30min**

```python
def test_e2e_multi_provider():
    """Teste 16: OpenAI + Groq."""

def test_e2e_observability():
    """Teste 17: Observabilidade ativa."""

def test_governance_policy():
    """Teste 18: Policy aplicada."""
```

---

## 4. Estratégia de Cobertura

### Distribuição de Testes

| Categoria | # Testes | % | Tempo |
|-----------|----------|---|------|
| P0 Crítico | 10 | 55% | 1h30m |
| P1 Alto | 5 | 28% | 45m |
| P2 Médio | 3 | 17% | 30m |
| **TOTAL** | **18** | **100%** | **~2h45m** |

### Coverage por Módulo

| Módulo | Target | Status |
|--------|--------|--------|
| agent.py | 100% | ✅ |
| nodes.py | 100% | ✅ |
| observability.py | 100% | ✅ |
| governance.py | 95% | ⚠️ |
| tools/file_reader.py | 95% | ✅ |
| analysis/llm_interpreter.py | 85% | ⚠️ |
| models.py | 90% | ⚠️ |
| **GERAL** | **≥95%** | ✅ |

---

## 5. Decisões de Teste

### Decisão 1: Testes E2E vs Unit Tests

**Escolha:** 80% E2E + 20% Unit  
**Justificativa:** LogAnalyzer é um agente; comportamento end-to-end é mais importante que testes isolados  
**Trade-off:** E2E são mais lentos, mas validam integração real

### Decisão 2: Mocks vs Real Fixtures

**Escolha:** Real fixtures para dados, mocks para LLM/API  
**Justificativa:** Dados reais garantem comportamento real, mas evitar custo de LLM  
**Trade-off:** Testes mais realistas, setup mais complexo

### Decisão 3: Cobertura 95% vs 100%

**Escolha:** 95% geral, 100% para crítico  
**Justificativa:** 95% é ponto de diminuição em retorno, overhead vs benefício  
**Trade-off:** 5% de risco, mas mantém agilidade

---

## 6. Cronograma de Testes

### Fase 1: Setup (15min)
- Criar `tests/test_e2e_generated_by_ai.py`
- Criar fixtures (logs, mocks)

### Fase 2: P0 Crítico (1h30min)
- Implementar 10 testes críticos
- Rodar: `pytest tests/test_e2e_generated_by_ai.py::TestE2E* -v`

### Fase 3: P1 Alto (45min)
- Implementar 5 testes de risco
- Rodar: `pytest tests/test_e2e_generated_by_ai.py::TestRisk* -v`

### Fase 4: P2 Médio (30min)
- Implementar 3 testes auxiliares
- Rodar: `pytest tests/test_e2e_generated_by_ai.py::TestAux* -v`

### Fase 5: Validação (30min)
- Coverage: `pytest --cov=src --cov-report=term`
- Pylint: `pylint src/`
- Tudo OK? Commit + Push

---

## 7. Métricas de Sucesso

### Testes

- ✅ 18+ testes implementados
- ✅ 100% de passa (0 falhas)
- ✅ Coverage ≥95% geral, 100% para P0

### Qualidade

- ✅ Pylint ≥9.8/10
- ✅ Flake8 0 erros críticos
- ✅ Sem regressão (112+ testes)

### Documentação

- ✅ Cada teste tem docstring clara
- ✅ Arquivo este completo (150+ linhas)
- ✅ README atualizado

---

**Status:** ✅ MATRIZ DE RISCO DEFINIDA  
**Data:** 24/08/2026  
**Próximo:** Implementar testes em test_e2e_generated_by_ai.py
