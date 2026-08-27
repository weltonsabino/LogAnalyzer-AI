# LogAnalyzer AI

> Um agente de IA para automatizar análise de arquivos de log usando LangGraph

## 📋 Visão Geral

**LogAnalyzer AI** é um agente inteligente que analisa automaticamente arquivos de log, identificando padrões importantes (erros, avisos, exceções) e gerando relatórios técnicos estruturados em markdown.

### Objetivo

Demonstrar o uso de agentes LangGraph em um caso real de análise de logs, com componentes como:
- Estado compartilhado (StateGraph)
- Nós com responsabilidades claras
- Ferramentas integradas e funcionais
- Validações robustas em cada etapa
- Contexto e memória mantidos durante execução
- Respostas estruturadas e úteis

### Casos de Uso

- 📊 Análise automatizada de logs de aplicação
- 🔍 Identificação de padrões de erro recorrentes
- ⚠️ Detecção de eventos críticos
- 💡 Geração de recomendações de ação
- 📈 Extração de métricas de qualidade

### Stack

- **Python** 3.10+
- **LangGraph** para construção do agente
- **LangChain** para integrações de IA
- **OpenAI GPT-4** / **Groq** para análise inteligente (opcional)
- **n8n** para automação low-code (webhook → email)
- **Docker** para rodar n8n localmente
- **Pytest** para testes

---

## 📊 Apresentação

**[Clique aqui para visualizar a apresentação interativa](docs/Apresentacao/Apresentação_LogAnalyzer_ai.html)** 🎬

A apresentação contém 2 slides com:
- **Slide 1:** Problema e Solução — O gargalo tradicional vs. a resolução inteligente com agentes
- **Slide 2:** Arquitetura e Métricas — Diagrama do StateGraph interativo, nós funcionais e métricas de qualidade

---

## 📌 Versão e Evolução

### Mini-Projeto M2.1 (Concluído ✅)

- **Data de conclusão:** 14/07/2026
- **Status:** ✅ Completo (76/85 testes, Pylint 9.83/10)
- **Score:** 9.5/10
- **Repositório:** Branch `main` com tag `v1.0.0`
- **Referência:** [`docs/M2.1_SCORE_FINAL.md`](docs/M2.1_SCORE_FINAL.md)

### Projeto Final M2.2 (Em Progresso 🔄)

- **Data de início:** 17/08/2026
- **Data prevista:** 31/08/2026
- **Estratégia:** Continuação e expansão do mini-projeto
- **Referência:** [`docs/M2.2_CONTINUACAO_ESTRATEGIA.md`](docs/M2.2_CONTINUACAO_ESTRATEGIA.md)
- **Mapeamento de requisitos:** [`docs/M2.2_REQUISITOS_MAPEAMENTO.md`](docs/M2.2_REQUISITOS_MAPEAMENTO.md)

### Linha do Tempo

```
07/07 - 14/07/2026: Mini-Projeto M2.1
       ✅ Concluído (Score: 9.5/10)

17/08 - 31/08/2026: Projeto Final M2.2
       🔄 Em progresso (17 tasks mapeadas)
       
       Phase 1 (3h):    Bloqueadores (Task #27-#29)
       Phase 2 (7h):    Features (Task #30-#33, #36)
       Phase 3 (8h):    Qualidade (Task #34-#35, #37-#38, #40)
       Phase 4 (2.75h): Apresentação (Task #41-#43)
```

---

## 🚀 Instalação e Setup

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip ou conda
- (Opcional) Chave de API OpenAI para análise com IA

### 2. Clonar Repositório
```bash
git clone https://github.com/weltonsabino/mini-projeto-LogAnalyzer-AI
cd mini-projeto-LogAnalyzer-AI
```

### 3. Criar Virtual Environment
```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
venv\Scripts\activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente
```bash
# Copiar template
cp .env.example .env

# Editar .env com suas configurações (opcional)
# OPENAI_API_KEY=sua_chave_aqui (deixe em branco para usar fallback)
```

---

## 📖 Como Usar

### Uso Básico (CLI)

#### 1. Analisar um arquivo de log
```bash
python -m src.loganalyzer.main /caminho/para/seu.log
```

#### 2. Salvar saída em arquivo
```bash
python -m src.loganalyzer.main /caminho/para/seu.log --output relatorio.md
```

#### 3. Formato JSON
```bash
python -m src.loganalyzer.main /caminho/para/seu.log --json
```

#### 4. Modo verboso
```bash
python -m src.loganalyzer.main /caminho/para/seu.log --verbose
```

### Suporte a Múltiplos Provedores LLM

**LogAnalyzer AI** agora suporta dois provedores de IA para análise inteligente:

#### 1. OpenAI GPT-4 (Padrão)
Análise mais precisa e poderosa, requer chave de API paga.

```bash
# Usar OpenAI (padrão)
python -m src.loganalyzer.main seu.log

# Ou explicitamente
python -m src.loganalyzer.main seu.log --provider openai
```

#### 2. Groq (Grátis ✨)
Análise rápida e grátis usando LLaMA 2 / Mixtral.

**Configuração:**

1. Obter chave em: https://console.groq.com/keys
2. Adicionar ao `.env`:
   ```
   GROQ_API_KEY=gsk-...sua-chave...
   ```
3. Usar:
   ```bash
   # Via CLI
   python -m src.loganalyzer.main seu.log --provider groq
   
   # Ou via variável de ambiente
   LLM_PROVIDER=groq python -m src.loganalyzer.main seu.log
   ```

**Precedência (CLI > Environment > Padrão):**
```bash
# CLI sobrescreve tudo
python -m src.loganalyzer.main seu.log --provider groq    # Groq
python -m src.loganalyzer.main seu.log --provider openai   # OpenAI

# Environment (se CLI não especificado)
LLM_PROVIDER=groq python -m src.loganalyzer.main seu.log   # Groq
LLM_PROVIDER=openai python -m src.loganalyzer.main seu.log # OpenAI

# Padrão (se nenhuma opção)
python -m src.loganalyzer.main seu.log                     # OpenAI
```

### Error Handling

O agente implementa tratamento robusto de erros através de arestas condicionais no StateGraph. Qualquer problema em qualquer etapa é capturado e processado graciosamente.

#### Cenários Cobertos

- **Validação:** Arquivo não existe, sem permissão, encoding inválido
- **Parsing:** Formato de log inválido, estrutura corrompida, arquivo vazio
- **Detecção:** Sem padrões encontrados, análise de padrão falha
- **IA:** Timeout da API, chave inválida, resposta inválida

#### Exemplo de Resposta de Erro

Se um arquivo não existir:
```bash
$ python -m src.loganalyzer.main /arquivo/inexistente.log
```

Saída:
```
✗ Erro ao processar arquivo
  Detalhes: Arquivo não encontrado: /arquivo/inexistente.log
  Timestamp: 2026-08-20 10:30:45
```

#### Fluxo Interno

```
┌─────────────────────────┐
│   Execução Normal       │
│ ✓ validate_input       │
│ ✓ read_file            │
│ ✓ parse_events         │
│ ✓ analyze_patterns     │
│ ✓ interpret_with_llm   │
│ ✓ generate_report      │
│ ✓ notify_webhook       │
└─────────────────────────┘

vs.

┌──────────────────────────┐
│   Com Erro (ex: parsing) │
│ ✓ validate_input        │
│ ✓ read_file             │
│ ✗ parse_events [ERROR]  │
│ → error_handling        │
│ → notify_webhook        │
│ → Saída consistente     │
└──────────────────────────┘
```

### Executar Exemplo
```bash
# Processa sample.log incluído no projeto
python examples/run_example.py
```

### Usar em Python
```python
from src.loganalyzer.agent import create_agent_graph, get_initial_state

# Criar agente
agent = create_agent_graph()

# Preparar estado (pode incluir provider)
state = get_initial_state("/caminho/para/log.log", provider="groq")

# Executar
result = agent.invoke(state)

# Acessar resultado
print(result["report"])
```

---

## 📊 Observabilidade Avançada

A partir da **Task #33**, o LogAnalyzer AI implementa **2+ sinais de observabilidade correlacionados** para rastreamento completo de execução.

### Sinais de Observabilidade Implementados

#### Sinal 1: Logs Estruturados com TraceCollector
```python
from src.loganalyzer.observability import TraceCollector

# Criar coletor com execution_id único
collector = TraceCollector()

# Adicionar traces
collector.add_trace(
    node_name="parse_events",
    event_type="node_start",
    data={"events_count": 150}
)

# Recuperar todos os traces
traces = collector.get_traces()
```

#### Sinal 2: Correlação com execution_id
Todos os traces de uma execução compartilham o mesmo `execution_id` (UUID), permitindo rastreamento end-to-end:

```python
# Sumário correlacionado
summary = collector.get_correlation_summary()

# Resultado:
{
    "execution_id": "a1b2c3d4-e5f6-47a8-9b0c-1d2e3f4a5b6c",
    "trace_count": 42,
    "duration_seconds": 3.245,
    "event_counts": {
        "node_start": 8,
        "node_end": 7,
        "error": 1,
        "warning": 2
    },
    "status": "OK"
}
```

#### Sinal 3: Timing com Spans (Bônus)
Decorador `@observability_middleware` registra duração de cada nó:

```python
@observability_middleware(collector=collector)
def my_node(state):
    # Duração será registrada automaticamente
    result = process_data(state)
    return result

# Trace registra:
{
    "event_type": "node_end",
    "data": {
        "duration_seconds": 1.234,
        "success": True
    }
}
```

### Decoradores de Resiliência

#### @with_timeout(seconds=30)
Limita tempo de execução de funções:

```python
from src.loganalyzer.observability import with_timeout

@with_timeout(seconds=30)
def read_large_file(file_path):
    return read_log_file(file_path)

# Lança TimeoutError se exceder 30s
```

#### @with_retry(max_attempts=3, backoff=1.5)
Retry automático com backoff exponencial:

```python
from src.loganalyzer.observability import with_retry

@with_retry(max_attempts=3, backoff=1.5)
def read_log_file(file_path):
    # Tenta até 3 vezes com espera exponencial
    # Apenas para erros transientes (timeout, permission, OSError)
    return open(file_path).read()
```

### Integração com Agent

O TraceCollector é integrado automaticamente:

```python
from src.loganalyzer.agent import get_initial_state

# Estado inicial já inclui TraceCollector
state = get_initial_state(file_path="/path/to/log.txt")

# Acessar collector dentro do agente
collector = state["trace_collector"]
execution_id = state["execution_id"]
```

### Exemplo Completo

```python
from src.loganalyzer.observability import TraceCollector, observability_middleware

# 1. Criar coletor
collector = TraceCollector()
print(f"Execution ID: {collector.execution_id}")

# 2. Instrumentar função
@observability_middleware(collector=collector)
def analyze_logs(file_content):
    return process_events(file_content)

# 3. Executar
result = analyze_logs(content)

# 4. Obter resumo correlacionado
summary = collector.get_correlation_summary()
print(f"Status: {summary['status']}")
print(f"Duração: {summary['duration_seconds']}s")
print(f"Traces: {summary['trace_count']}")
```

---

## 🤖 QA com IA

A partir da **Task #34**, o LogAnalyzer AI implementa **garantia de qualidade com IA** através de análise estática de código e testes end-to-end gerados.

### Code Review com IA

Documentação completa em `docs/qa/code_review_with_ai.md`:
- Metodologia em 3 camadas (automática + IA + contexto)
- Checklist de 15+ critérios de revisão
- Exemplo de análise completa
- Integração com CI/CD

**Scores Atuais:**
- Pylint: **9.83/10** ✅
- Coverage: **95%+** ✅
- Type Hints: **100%** ✅
- Docstrings: **100%** ✅

### Priorização por Risco

Documentação em `docs/qa/risk_prioritization.md`:
- Matriz de risco por módulo (probabilidade × impacto)
- 7 módulos analisados (P0-P3)
- Estratégia de testes por prioridade
- 18 testes E2E com cobertura total

### Testes E2E Gerados

Arquivo: `tests/test_e2e_generated_by_ai.py` (20 testes)

**8 Cenários Críticos:**

1. **Sucesso E2E** — Fluxo completo, relatório gerado
2. **Erro Validação** — Path inválido, error_handling acionado
3. **Timeout** — Decorator @with_timeout funciona
4. **Retry** — Sucesso após tentativa falha
5. **Observabilidade** — execution_id + traces correlacionados
6. **Segurança** — Path traversal bloqueado
7. **Autonomia** — Ações bloqueadas por governance
8. **Multi-Provider** — OpenAI + Groq funcionam

**Adicionais:**
- Testes de integração (pipeline completo)
- Testes de performance (<30s execução)
- Validação de estado (consistência)

### Executar Testes E2E

```bash
# Todos os 20 testes E2E
pytest tests/test_e2e_generated_by_ai.py -v

# Apenas cenários críticos (P0)
pytest tests/test_e2e_generated_by_ai.py::TestE2E -v
pytest tests/test_e2e_generated_by_ai.py::TestE2EErrorHandling -v
pytest tests/test_e2e_generated_by_ai.py::TestE2EResilience -v

# Apenas testes de segurança
pytest tests/test_e2e_generated_by_ai.py::TestE2ESecurity -v

# Com coverage
pytest tests/test_e2e_generated_by_ai.py --cov=src --cov-report=term
```

### Métricas de QA

| Métrica | Valor | Target | Status |
|---------|-------|--------|--------|
| Testes E2E | 20 | ≥8 | ✅ |
| Coverage | 95%+ | ≥95% | ✅ |
| Pylint Score | 9.83/10 | ≥9.8 | ✅ |
| Code Review Critérios | 15+ | 15+ | ✅ |
| Cenários Cobertos | 8/8 | 100% | ✅ |

---

## 🔗 Integração Low-Code (n8n)

A partir da **Task #36**, o LogAnalyzer AI integra com **n8n** (plataforma open-source de automação) para enviar notificações automáticas por email ao final de cada análise.

### Fluxo

```
LogAnalyzer executa análise → notify_webhook_node → POST para n8n → n8n formata → Email enviado
```

### Como Funciona

O nó `notify_webhook` é o último do pipeline. Roda tanto no caminho de sucesso quanto no de erro:
- Se webhook configurado → envia payload JSON com severidade, resumo e contagem de erros
- Se não configurado → skip silencioso (`webhook_status = "skipped"`)
- Se erro de conexão → captura sem crashar (`webhook_status = "error"`)

### Setup Local (Docker)

```bash
# Subir n8n
docker run -d --name n8n -p 5678:5678 n8nio/n8n

# Importar workflow
# http://localhost:5678 → Import from File → docs/low-code/n8n_workflow.json

# Configurar .env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/loganalyzer
N8N_WEBHOOK_ENABLED=true
```

### Testar

```bash
python examples/run_with_webhook.py
```

**Documentação completa:** `docs/low-code/n8n-integration.md`

---

## 🔍 DevOps Inteligente: Detecção de Anomalias

A partir da **Task #35**, o LogAnalyzer AI implementa detecção heurística de anomalias em logs.

### AnomalyDetector

```python
from src.loganalyzer.devops import AnomalyDetector

detector = AnomalyDetector(window_size=20, spike_threshold=2.0)
result = detector.analyze(log_lines)

# Resultado:
# {
#   "error_spike": {"anomaly": True, "severity": "high", ...},
#   "recurring_patterns": {"recurring": True, "patterns": [...], ...},
#   "risk": {"risk_level": "critical", "trend": "increasing", ...}
# }
```

### Heurísticas Implementadas

| Detecção | Método | Resultado |
|----------|--------|-----------|
| Error Spike | Janela deslizante vs baseline | anomaly: True/False + severity |
| Padrões Recorrentes | Agrupamento por mensagem | patterns com contagem |
| Estimativa de Risco | Consolidação de anomalias | risk_level + trend |

**Documentação completa:** `docs/devops/intelligent_log_analysis.md`

---

## 🧪 Testes

### Executar Todos os Testes
```bash
pytest tests/ -v
```

### Testes por Tarefa
```bash
# Task 2: Architecture and Models
pytest tests/test_agent.py -v

# Task 3: Node Logic
pytest tests/test_tools.py tests/test_task3_implementation.py -v

# Task 4: LLM and Tools
pytest tests/test_analysis.py tests/test_task4_implementation.py -v
```

### Cobertura de Testes
```bash
pytest tests/ --cov=src --cov-report=html
```

### Status Atual
- ✅ **222 testes passando**
- ✅ **Score Linter:** 9.83/10
- ✅ **Suporte Multi-Provider:** OpenAI + Groq
- ✅ **Observabilidade:** TraceCollector + retry + timeout
- ✅ **Segurança:** Governança adversarial + InputValidator
- ✅ **Low-Code:** n8n webhook integrado ao pipeline

---

## 🔧 Ferramentas de Desenvolvimento

### Linter
```bash
pylint src/
```

### Formatter
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

---

## 📝 Exemplos

### Entrada
Arquivo `examples/sample.log` com 47 linhas:
```
2026-07-12 10:00:01 INFO Application started
2026-07-12 10:00:02 INFO Loading configuration
2026-07-12 10:00:03 WARNING Config file not found at /etc/app.conf
2026-07-12 10:00:06 ERROR Connection timeout - retrying (1/3)
2026-07-12 10:08:02 ERROR Out of memory exception in request handler
2026-07-12 10:20:00 INFO Health check passed
...
```

### Saída
Relatório markdown estruturado:
```
# Relatorio de Analise de Log

## Resumo Executivo
| Métrica | Quantidade |
|---------|-----------|
| Total de eventos | 47 |
| Erros encontrados | 11 |
| Avisos encontrados | 9 |
| Eventos críticos | 10 |

## Eventos Criticos
1. Database connection failed after 3 retries
2. Service initialization failed: database connection error
3. Out of memory exception in request handler
...

## Recomendações de Ação
1. Investigar eventos críticos imediatamente
2. Revisar padrões de erro e corrigir raiz do problema
3. Monitorar avisos e ajustar configurações se necessário
...
```

Veja `examples/sample_output.md` para saída completa.

---

## 🎯 Análise Inteligente por Severidade (Task #30)

O agente agora roteia automaticamente o processamento com base na severidade dos eventos encontrados:

### Roteamento Automático

```
eventos parseados
    ↓
route_by_severity()  ← Função condicional
    ├─ Se CRITICAL/ERROR → Nó especializado para HIGH severity
    ├─ Se WARNING        → Nó especializado para MEDIUM severity  
    └─ Se INFO/DEBUG     → Nó especializado para LOW severity
    ↓
Análise LLM especializada
```

### Três Tipos de Análise

| Nível | Trigger | LLM Focus | Urgência |
|-------|---------|-----------|----------|
| **HIGH** | CRITICAL, ERROR | Recuperação de incidentes | IMEDIATA |
| **MEDIUM** | WARNING | Prevenção proativa | NORMAL |
| **LOW** | INFO, DEBUG, TRACE | Insights e otimização | BAIXA |

### Exemplo: Log com Multiple Severidades

**Input:** Log com erros, avisos e info misturados
```
ERROR: Connection lost to database
WARNING: Retrying connection attempt 2/5
INFO: Successfully reconnected
```

**Processamento:** 
1. Parser extrai 3 eventos
2. Detector identifica: 1 ERROR (HIGH), 1 WARNING (MEDIUM), 1 INFO (LOW)
3. `route_by_severity()` prioriza → **rota HIGH**
4. `analyze_high_severity_node()` processa com foco em incidentes
5. LLM gera recomendações urgentes

**Output:** `severity_level: "HIGH"`, `urgency: "IMEDIATA"` com recomendações de ação

### Rastreabilidade

Campo `severity_routes` armazena contagem:
```python
# Estado após processamento
state["severity_routes"] = {
    "HIGH": 1,    # Eventos críticos/erro
    "MEDIUM": 1,  # Eventos warning
    "LOW": 1      # Eventos info/debug
}
```

---

## 📋 Cenários de Teste (Task #31)

LogAnalyzer AI foi validado com múltiplos cenários de teste para demonstrar robustez em diferentes contextos:

### Cenário 1: Operação Normal

- **Arquivo:** `examples/sample.log` (47 linhas)
- **Tipo:** Aplicação rodando normalmente com alguns avisos
- **Severidade:** LOW/MEDIUM (sem eventos críticos)
- **Output:** `examples/sample_output.md`
- **Teste:** Testes padrão do suite

**Reproduzir:**
```bash
python -m src.loganalyzer.main examples/sample.log
```

### Cenário 2: Degradação e Falha (NOVO)

- **Arquivo:** `tests/fixtures/failure_logs/scenario_failure.log` (43 linhas)
- **Tipo:** Cascata de falhas — database → cache → memory → crash
- **Severidade:** HIGH (6 CRITICAL events, 15 ERROR events)
- **Output:** `docs/examples/scenario_failure_output.md`
- **Testes:** `tests/test_scenario_failure.py` (9 testes)

**Padrão:**
```
T=0s: Startup normal (INFO)
T=5s: Database lento (WARNING)
T=10s: Cache falha (ERROR)
T=30s: Memory crescente (WARNING)
T=50s: Pool esgotado (CRITICAL)
T=60s: Ambos database falham (CRITICAL)
T=70s: Out of memory (CRITICAL)
T=80s: Shutdown + restart falha (CRITICAL)
```

**Reproduzir:**
```bash
# Executar análise
python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log

# Executar testes
pytest tests/test_scenario_failure.py -v

# Com cobertura
pytest tests/test_scenario_failure.py --cov=src.loganalyzer
```

**Documentação Completa:**
- 📖 `docs/examples/scenario_failure.md` — Descrição, fluxo, análise esperada
- 📊 `docs/examples/scenario_failure_output.md` — Saída real da análise

### Comparação de Cenários

| Aspecto | Normal | Falha |
|---------|--------|-------|
| Eventos | 47 | 43 |
| CRITICAL | 0 | 6 |
| ERROR | 0 | 15 |
| WARNING | 9 | 13 |
| INFO | 38 | 9 |
| Severity Routing | LOW/MEDIUM | HIGH (IMEDIATA) |
| Analysis Focus | Otimizações | Recuperação |
| Recomendações | Preventivas | Urgentes |

---

## 🏗️ Estrutura do Projeto

```
LogAnalyzer-AI/
├── src/loganalyzer/
│   ├── main.py                 # CLI entrypoint
│   ├── agent.py                # StateGraph principal
│   ├── models.py               # Modelos (LogAnalysisState)
│   ├── nodes.py                # Nós do fluxo (10+ nós)
│   ├── governance.py           # Governança e limites de autonomia
│   ├── observability.py        # TraceCollector, timeout, retry
│   ├── tools/
│   │   ├── validators.py       # Validação de entrada
│   │   ├── file_reader.py      # Leitura de arquivo
│   │   ├── parser.py           # Parsing de eventos
│   │   ├── detector.py         # Detecção de padrões
│   │   └── formatter.py        # Formatação de relatório
│   ├── analysis/
│   │   └── llm_interpreter.py  # Integração com IA (OpenAI/Groq)
│   ├── devops/
│   │   └── anomaly_detector.py # Detecção de anomalias e spikes
│   └── integrations/
│       └── webhook.py          # Webhook n8n (low-code)
│
├── tests/
│   ├── test_agent.py                  # Testes do agente
│   ├── test_tools.py                  # Testes de ferramentas
│   ├── test_analysis.py               # Testes de análise (multi-provider)
│   ├── test_task3_implementation.py   # Testes nodes
│   ├── test_task4_implementation.py   # Testes LLM/formatter
│   ├── test_error_handling.py         # Testes arestas condicionais
│   ├── test_advanced_langgraph.py     # Testes ramificação/severidade
│   ├── test_observability.py          # Testes TraceCollector/retry
│   ├── test_adversarial_security.py   # Testes segurança adversarial
│   ├── test_scenario_failure.py       # Testes cenário de falha
│   ├── test_e2e_generated_by_ai.py    # Testes E2E gerados por IA
│   ├── test_devops_anomaly.py         # Testes detecção de anomalias
│   ├── test_webhook_integration.py    # Testes webhook (mock)
│   └── fixtures/                      # Dados de teste
│
├── docs/
│   ├── ARCHITECTURE.md                # Design detalhado
│   ├── PROJECT_REQUIREMENTS.md        # Pré-requisitos
│   ├── devops/
│   │   └── intelligent_log_analysis.md # Análise inteligente de logs
│   ├── low-code/
│   │   ├── n8n-integration.md         # Guia de integração n8n
│   │   └── n8n_workflow.json          # Workflow importável
│   ├── qa/
│   │   ├── code_review_with_ai.md     # Code review com IA
│   │   └── risk_prioritization.md     # Priorização por risco
│   ├── examples/                      # Cenários de teste documentados
│   └── prompts/                       # Histórico de prompts (21+)
│
├── examples/
│   ├── run_example.py                 # Script de demonstração básico
│   ├── run_with_webhook.py            # Demo com webhook n8n
│   └── sample.log                     # Log de exemplo
│
├── .github/workflows/
│   ├── lint.yml                       # Pylint + Flake8
│   ├── test.yml                       # Pytest + Coverage
│   └── build.yml                      # Validação de imports
│
├── requirements.txt                   # Dependências
├── .env.example                       # Template de configuração
├── .gitignore                         # Arquivos ignorados
└── README.md                          # Este arquivo
```

---

## 🔐 Segurança

- ✅ **Credenciais:** Armazenadas em `.env` (não versionado)
- ✅ **`.gitignore`:** Configurado para proteger dados sensíveis
- ✅ **`.env.example`:** Sem valores reais, apenas template
- ✅ **Validações:** Implementadas em cada etapa
- ✅ **Encoding:** UTF-8 padrão com fallback
- ✅ **Governança:** Limites de autonomia e validação adversarial

### Governança e Limites de Autonomia (Task #32)

O LogAnalyzer AI implementa um sistema de governança que controla o nível de autonomia do agente e bloqueia entradas maliciosas antes de qualquer processamento.

#### Níveis de Autonomia

| Nível | Permissões | Aprovação Humana |
|-------|-----------|-----------------|
| `READ_ONLY` | Apenas leitura de arquivos | Não |
| `ANALYZE` (padrão) | Leitura + análise + detecção de padrões | Não |
| `RECOMMEND` | Análise + geração de relatório + recomendações | Não |
| `EXECUTE` | Todas as ações, incluindo escrita/deleção | **Sim** |

O agente opera no nível **ANALYZE** por padrão — pode ler e analisar logs, mas nunca executa ações destrutivas.

#### Proteção Contra Entradas Adversariais

O `InputValidator` detecta e bloqueia automaticamente:

| Tipo de Ataque | Exemplo | Resultado |
|---------------|---------|-----------|
| Prompt Injection | `"; DROP logs; --"` | ❌ Bloqueado |
| Path Traversal | `../../etc/passwd` | ❌ Bloqueado |
| Command Injection | `$(rm -rf /)` | ❌ Bloqueado |
| Null Byte | `file.log%00.exe` | ❌ Bloqueado |
| Override de Regras | `SYSTEM: ignore rules` | ❌ Bloqueado |
| Arquivo legítimo | `app.log` | ✅ Aprovado |

#### Exemplo: Entrada Maliciosa Bloqueada

```python
from src.loganalyzer.agent import create_agent_graph, get_initial_state

agent = create_agent_graph()
state = get_initial_state("../../etc/passwd")
result = agent.invoke(state)

print(result["is_valid"])        # False
print(result["error_message"])   # "Bloqueado por governança: Path traversal detectado..."
print(result["metadata"]["governance_status"])  # "bloqueado"
```

#### Integração no Pipeline

A validação de governança é a **primeira etapa** do nó `validate_input`:

```
file_path recebido
    ↓
[GovernancePolicy.validate_file_path()]  ← Bloqueia adversarial
    ↓ (se aprovado)
[validate_file_path()]  ← Verifica existência do arquivo
    ↓
Processamento normal
```

### Como Configurar API Key (Seguro)

1. **Criar arquivo `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Adicionar sua chave (não commitar):**
   ```
   OPENAI_API_KEY=sk-...seu-token-aqui...
   ```

3. **Verificar `.gitignore`:**
   ```bash
   grep "\.env" .gitignore  # Deve estar lá
   ```

---

## 📚 Documentação Completa

- **[Arquitetura Detalhada](docs/ARCHITECTURE.md)** — Diagrama do StateGraph, descrição de cada nó, fluxo de dados
- **[Pré-requisitos do Projeto](docs/PROJECT_REQUIREMENTS.md)** — Critérios de avaliação e diretrizes
- **[Prompts Utilizados](docs/prompts/)** — Histórico de decisões e prompts
- **[Saída de Exemplo](examples/sample_output.md)** — Demonstração de output real

---

## 🤝 Contribuição

Este é um projeto de estudo para disciplina "IA para Desenvolvedores [T2]".

### Fluxo de Desenvolvimento

1. **Branch:** Criar branch feature (`git checkout -b feature/nome-da-feature`)
2. **Código:** Implementar respeitando `docs/` guidelines
3. **Testes:** Adicionar testes unitários
4. **Commits:** Usar padrão semântico (feat:, fix:, docs:, etc)
5. **PR:** Enviar Pull Request para review
6. **Merge:** Após aprovação, mergear em develop

### Convenções de Código

- **Comentários:** 🇧🇷 Português
- **Variáveis/Funções:** 🇺🇸 Inglês
- **Docstrings:** 🇧🇷 Português
- **Style:** PEP 8 + Black formatter

---

## ✅ Checklist de Entrega

- [x] Repositório público no GitHub
- [x] Código do agente implementado (StateGraph com 10+ nós)
- [x] Ferramentas integradas e funcionais (7 ferramentas)
- [x] README.md completo
- [x] docs/ARCHITECTURE.md documentado
- [x] docs/prompts/ com histórico de prompts (21+)
- [x] examples/sample_output.md com saída real
- [x] 222 testes passando (100% de conformidade)
- [x] Commits semânticos (30+ commits)
- [x] Sem credenciais versionadas
- [x] Apresentação (2 slides interativos em HTML)
- [x] Observabilidade (TraceCollector + retry + timeout)
- [x] Segurança adversarial (GovernancePolicy + InputValidator)
- [x] Integração low-code (n8n webhook → email)
- [x] Detecção de anomalias (AnomalyDetector)
- [x] QA com IA (code review + testes E2E gerados)

---

## 🐛 Troubleshooting

### Erro: "FileNotFoundError: [Errno 2] No such file or directory"
```bash
# Verifique o caminho do arquivo
python -m src.loganalyzer.main ./seu-arquivo.log  # Caminho relativo
```

### Erro: "OPENAI_API_KEY not set"
```bash
# Use fallback (análise heurística funciona sem API key)
# Ou configure a chave em .env
export OPENAI_API_KEY="sua-chave"
```

### Testes falhando
```bash
# Reinstale dependências
pip install -r requirements.txt --upgrade

# Limpe cache
rm -rf .pytest_cache __pycache__

# Execute novamente
pytest tests/ -v
```

---

## 📊 Métricas do Projeto

| Métrica | Valor |
|---------|-------|
| Total de Nós | 10+ (pipeline + severidade + webhook) |
| Total de Ferramentas | 7 (validators, reader, parser, detector, formatter, anomaly, webhook) |
| Provedores LLM | 2 (OpenAI + Groq) |
| Linhas de Código | ~3500+ |
| Testes Unitários | 222 |
| Cobertura de Testes | ~76% |
| Score de Linter | 9.83/10 |
| Integração Low-Code | n8n (webhook → email) |

---

## 📞 Contato e Informações

- **Projeto:** LogAnalyzer AI
- **Disciplina:** IA para Desenvolvedores [T2]
- **Instituição:** SCTEC
- **Prazo:** 31/08/2026 (Projeto Final M2.2)
- **Avaliação:** 30% do módulo
- **Repositório:** [GitHub - weltonsabino/mini-projeto-LogAnalyzer-AI](https://github.com/weltonsabino/mini-projeto-LogAnalyzer-AI)

---

**Última atualização:** 25 de Agosto, 2026  
**Status:** 🔄 Em Progresso (Projeto Final M2.2)
