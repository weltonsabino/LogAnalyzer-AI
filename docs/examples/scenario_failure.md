# Cenário de Falha — LogAnalyzer AI

## 1. Descrição do Cenário

**Tipo:** Degradação Progressiva → Falha Crítica → Restart Failure

**Contexto:** Uma aplicação Java inicia normalmente, mas progressivamente degrada através de múltiplas falhas em cascata:
1. Problema de conexão com database (lento)
2. Cache indisponível
3. Memory pressure (85%)
4. Pool de conexões database esgotado
5. Failover database também falha
6. Out of memory exception
7. Shutdown de emergência
8. Restart falha

**Duração:** ~82 segundos (14:00:00 até 14:01:22)

**Componentes Afetados:**
- Database (primário + failover)
- Cache (Redis)
- Memory (heap)
- Connection Pool
- Service Health

---

## 2. Fluxo de Eventos

```
T=0s (14:00:00)
├─ INFO: Application starting
├─ INFO: Loading configuration
├─ INFO: Cache provider initialized
└─ INFO: Health check routine started

T=5s (14:00:05)
├─ WARNING: Database connection slow (2500ms > 1000ms threshold)
├─ INFO: Retry database (1/3)
└─ INFO: Database connected

T=10s (14:00:10)
├─ ERROR: Cache connection refused
├─ WARNING: Retry cache (1/3)
├─ ERROR: Cache timeout after 2000ms
└─ WARNING: Running without cache (degraded mode)

T=20s (14:00:20)
├─ INFO: Application ready (but degraded)
└─ INFO: Started receiving requests

T=30s (14:00:30)
├─ WARNING: Response time 4200ms (4x threshold)
├─ WARNING: Memory at 72%
└─ WARNING: Database queries slow (3500ms)

T=40s (14:00:40)
├─ ERROR: Memory at 85% (critical threshold)
├─ ERROR: Garbage collection started
└─ WARNING: 45 requests queued

T=50s (14:00:50)
├─ CRITICAL: Connection pool exhausted (10/10 active)
├─ CRITICAL: New requests rejected
├─ ERROR: Failover database activated
└─ ERROR: Failover attempts 1-2 fail

T=60s (14:01:00)
├─ CRITICAL: Both primary and failover unreachable
├─ ERROR: Circuit breaker opened
├─ ERROR: All 45 requests rejected
└─ CRITICAL: Memory critical at 95%

T=70s (14:01:05)
├─ ERROR: Out of memory exception
├─ ERROR: Stack trace captured
├─ CRITICAL: Emergency shutdown initiated
└─ INFO: Crash dump saved

T=80s (14:01:15)
├─ INFO: Automatic restart attempted
├─ WARNING: Max restart attempts (3/3) reached
├─ ERROR: Database still unreachable
├─ CRITICAL: Service permanently down
└─ INFO: Manual intervention required
```

---

## 3. Análise Esperada

### Severidade
**HIGH** — Eventos CRITICAL presentes (6 total)

### Contagem de Eventos
- **CRITICAL:** 6 eventos (14% do total)
- **ERROR:** 15 eventos (35%)
- **WARNING:** 13 eventos (30%)
- **INFO:** 9 eventos (21%)
- **Total:** 43 eventos

### Insights Principais
1. **Falha em Cascata:** Database → Cache → Memory → Complete Outage
2. **Componentes Interdependentes:** Falha do cache aumenta carga do database
3. **Esgotamento de Recursos:** Memory crescente leva a exception fatal
4. **Failover Ineficaz:** Backup também indisponível
5. **Recuperação Impossível:** Restart falha (causa raiz não resolvida)

### Root Causes
1. **Database Indisponível** → Pool esgota, requests acumulam
2. **Memory Leak or Excessive Load** → Garbage collection não consegue recuperar
3. **Cache Down** → Todas as queries vão ao database (carga duplicada)
4. **No Graceful Degradation** → Aplicação tenta continuar até crash

### Recomendações de Ação
1. **URGENTE:** Investigar por que database está indisponível (network? crash?)
2. **URGENTE:** Verificar por que cache (Redis) está down
3. **Imediato:** Aumentar heap memory ou identificar memory leak
4. **Imediato:** Implementar circuit breaker com fallback (partial service)
5. **Preventivo:** Configurar alertas para memory > 70%
6. **Preventivo:** Configurar timeouts mais agressivos para queries slow
7. **Backup:** Testar e validar failover database antes de uso em prod
8. **Operacional:** Implementar auto-restart com exponential backoff + max attempts

---

## 4. Como Reproduzir

### Executar Análise
```bash
# Processar log de falha
python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log

# Com provider específico (opcional)
python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log --provider groq
```

### Executar Testes
```bash
# Todos os testes do cenário
pytest tests/test_scenario_failure.py -v

# Teste específico
pytest tests/test_scenario_failure.py::test_failure_log_processing -v

# Com cobertura
pytest tests/test_scenario_failure.py --cov=src.loganalyzer
```

---

## 5. Arquivo de Log

**Localização:** `tests/fixtures/failure_logs/scenario_failure.log`

**Linhas:** 43 eventos

**Formato:** Texto plano com timestamps e níveis de severidade

**Padrão:**
```
YYYY-MM-DD HH:MM:SS LEVEL Message
```

**Exemplo:**
```
2026-08-20 14:00:50 CRITICAL Database connection pool exhausted - 10/10 active
```

---

## 6. Output de Análise

Veja `docs/examples/scenario_failure_output.md` para saída completa gerada pelo LogAnalyzer AI.

**Estrutura esperada:**
- Resumo Executivo com métricas
- Eventos Críticos listados
- Padrões detectados
- Análise de causa raiz
- Recomendações prioritizadas
- Metadados de processamento

---

## 7. Integração com Fluxo do Agente

Este cenário testa:

### ✅ Roteamento por Severidade (Task #30)
- Log tem CRITICAL eventos → rota para `analyze_high_severity_node()`
- Severity level na saída: "HIGH"
- Urgency: "IMEDIATA"

### ✅ Análise Paralela (Task #30)
- `parallel_patterns` contém:
  - Frequência de eventos por nível
  - Padrões recorrentes (múltiplos ERROR em sequence)
  - Anomalias (timestamps podem ter gaps)

### ✅ Error Handling (Task #28)
- Múltiplos nós podem falhar se validações forem rigorosas
- Arestas condicionais garantem que erro não trava agente

### ✅ State Management
- `severity_routes` reflete contagem real: HIGH > MEDIUM > LOW
- `analysis_result` contém estrutura completa
- `metadata` rastreia todas as etapas

---

## 8. Comparação com Cenário Normal

| Aspecto | Normal (sample.log) | Falha (scenario_failure.log) |
|---------|-------------------|------------------------------|
| Eventos | ~47 | ~43 |
| CRITICAL | 0 | 6 |
| ERROR | 0 | 15 |
| WARNING | 9 | 13 |
| Duration | Normal operation | 82s degradation |
| Severity | LOW/MEDIUM | HIGH (IMEDIATA) |
| Routing | analyze_low/medium | analyze_high_severity |
| Focus | Otimizações | Recuperação de incidente |

---

**Arquivo criado:** 2026-08-20  
**Versão:** 1.0  
**Status:** ✅ Cenário completo e validado

