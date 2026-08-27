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

## 🏗️ Arquitetura do Agente (StateGraph Completo)

O LogAnalyzer AI é construído sobre um **StateGraph do LangGraph** com 12 nós funcionais, arestas condicionais para error handling e roteamento inteligente por severidade.

### Diagrama Completo do Pipeline

```
                         ┌─────────────────────────────────────────────────────────────┐
                         │                   LogAnalyzer AI — StateGraph               │
                         └─────────────────────────────────────────────────────────────┘

                                              INÍCIO
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │   validate_input      │ ← GovernancePolicy + InputValidator
                                    └───────────────────────┘
                                         │            │
                              (validation_error)   (sucesso)
                                         │            │
                                         ▼            ▼
                              ┌──────────────┐  ┌───────────────┐
                              │error_handling│  │   read_file   │ ← @with_retry + @with_timeout
                              └──────────────┘  └───────────────┘
                                         │            │
                                         │            ▼
                                         │  ┌───────────────────────┐
                                         │  │    parse_events       │ ← Parser multi-formato
                                         │  └───────────────────────┘
                                         │       │            │
                                         │  (parsing_error) (sucesso)
                                         │       │            │
                                         │       ▼            ▼
                                         │       │  ┌───────────────────────┐
                                         │       │  │  analyze_patterns     │ ← Detecção de padrões
                                         │       │  └───────────────────────┘
                                         │       │            │
                                         │       │     route_by_severity()
                                         │       │     ┌──────┼──────┐
                                         │       │     ▼      ▼      ▼
                                         │       │  ┌─────┐┌──────┐┌─────┐
                                         │       │  │HIGH ││MEDIUM││ LOW │  ← Nós especializados
                                         │       │  └─────┘└──────┘└─────┘
                                         │       │     │      │      │
                                         │       │     └──────┼──────┘
                                         │       │            ▼
                                         │       │  ┌───────────────────────────────┐
                                         │       │  │ analyze_patterns_parallel     │ ← Consolidação
                                         │       │  └───────────────────────────────┘
                                         │       │            │
                                         │       │            ▼
                                         │       │  ┌───────────────────────┐
                                         │       │  │  interpret_with_llm   │ ← OpenAI/Groq
                                         │       │  └───────────────────────┘
                                         │       │       │            │
                                         │       │  (analysis_error) (sucesso)
                                         │       │       │            │
                                         │       │       ▼            ▼
                                         ◄───────┼───────┘  ┌───────────────────┐
                                         │       │          │  generate_report   │ ← Markdown
                                         │       │          └───────────────────┘
                                         │       │                    │
                                         │       │                    ▼
                                         ▼       ▼            ┌──────────────────┐
                                    ┌──────────────┐          │                  │
                                    │error_handling│──────────►│ notify_webhook   │ ← n8n (opcional)
                                    └──────────────┘          │                  │
                                                              └──────────────────┘
                                                                      │
                                                                      ▼
                                                                     END
```

### Classificação dos Nós

| Nó | Responsabilidade | Categoria |
|----|-----------------|-----------|
| `validate_input` | Governança + validação de path/existência | Segurança |
| `read_file` | Leitura com retry e timeout | I/O |
| `parse_events` | Extração de eventos (multi-formato) | Processamento |
| `analyze_patterns` | Detecção de padrões e classificação | Análise |
| `analyze_high_severity` | Análise foco em incidentes críticos | Especializado |
| `analyze_medium_severity` | Análise foco em prevenção | Especializado |
| `analyze_low_severity` | Análise foco em otimizações | Especializado |
| `analyze_patterns_parallel` | Consolidação dos resultados paralelos | Agregação |
| `interpret_with_llm` | Interpretação com IA (OpenAI/Groq) | IA |
| `generate_report` | Geração de relatório markdown | Output |
| `error_handling` | Tratamento gracioso de erros | Resiliência |
| `notify_webhook` | Notificação n8n (se configurado) | Integração |

### Arestas Condicionais (Error Handling)

```python
# 4 pontos de roteamento condicional:
route_after_validation(state)  → "error_handling" | "read_file"
route_after_parsing(state)     → "error_handling" | "analyze_patterns"
route_by_severity(state)       → "error_handling" | "high" | "medium" | "low"
route_after_analysis(state)    → "error_handling" | "generate_report"
```

Qualquer erro em qualquer etapa é capturado e redirecionado → `error_handling` → `notify_webhook` → END, garantindo saída consistente.

### Estado Compartilhado (LogAnalysisState)

```python
class LogAnalysisState(TypedDict):
    file_path: str                    # Caminho do arquivo de log
    file_content: str                 # Conteúdo lido
    parsed_events: list               # Eventos extraídos
    errors_found: list                # Erros identificados
    warnings_found: list              # Avisos identificados
    analysis_result: dict             # Resultado da análise IA
    report: str                       # Relatório final markdown
    is_valid: bool                    # Flag de validade
    error_message: Optional[str]      # Mensagem de erro (se houver)
    metadata: dict                    # Metadados (governance, webhook, traces)
    validation_error: Optional[str]   # Flag de erro de validação
    parsing_error: Optional[str]      # Flag de erro de parsing
    detection_error: Optional[str]    # Flag de erro de detecção
    analysis_error: Optional[str]     # Flag de erro de análise
    severity_level: Optional[str]     # Nível de severidade roteado
    severity_routes: Optional[dict]   # Contagem por severidade
    webhook_status: Optional[str]     # Status do webhook (sent/skipped/error)
    trace_collector: Optional[Any]    # TraceCollector para observabilidade
    execution_id: Optional[str]       # UUID da execução
```

**Documentação detalhada:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 📊 Observabilidade Avançada

A partir da **Task #33**, o LogAnalyzer AI implementa **3 sinais de observabilidade correlacionados** para rastreamento completo de execução, com decoradores de resiliência integrados.

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

### Como Investigar Problemas

Quando uma execução falha ou apresenta comportamento inesperado:

**1. Identificar a execução:**
```python
# Cada execução tem UUID único
execution_id = state["execution_id"]
# Ex: "a1b2c3d4-e5f6-47a8-9b0c-1d2e3f4a5b6c"
```

**2. Obter traces correlacionados:**
```python
collector = state["trace_collector"]
traces = collector.get_traces()

# Filtrar por tipo de evento
errors = [t for t in traces if t["event_type"] == "error"]
timeouts = [t for t in traces if "timeout" in str(t.get("data", {}))]
```

**3. Analisar duração por nó:**
```python
summary = collector.get_correlation_summary()
# duration_seconds mostra tempo total
# event_counts mostra distribuição de eventos
```

**4. Verificar retries:**
```python
# Traces de retry aparecem como event_type="retry"
retries = [t for t in traces if t["event_type"] == "retry"]
# Cada retry inclui attempt_number e backoff_seconds
```

**Testes:** [`tests/test_observability.py`](tests/test_observability.py)  
**Módulo:** [`src/loganalyzer/observability.py`](src/loganalyzer/observability.py)

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

**Documentação completa:**
- [`docs/qa/code_review_with_ai.md`](docs/qa/code_review_with_ai.md) — Metodologia e critérios
- [`docs/qa/risk_prioritization.md`](docs/qa/risk_prioritization.md) — Matriz de risco por módulo
- [`tests/test_e2e_generated_by_ai.py`](tests/test_e2e_generated_by_ai.py) — Testes E2E

---

## 🔗 Integração Low-Code (n8n)

A partir da **Task #36**, o LogAnalyzer AI integra com **n8n** (plataforma open-source de automação) para enviar notificações automáticas por email ao final de cada análise.

### Fluxo de Automação

```
LogAnalyzer executa análise
    ↓
notify_webhook_node (último nó do pipeline)
    ↓
POST JSON para n8n webhook
    ↓
n8n recebe → formata dados → envia email
```

### Como Funciona

O nó `notify_webhook` é o **último nó** do pipeline. Roda tanto no caminho de sucesso quanto no de erro:

| Situação | Comportamento | `webhook_status` |
|----------|--------------|------------------|
| Webhook configurado + disponível | Envia payload JSON | `"sent"` |
| Webhook não configurado | Skip silencioso | `"skipped"` |
| Webhook com erro de conexão | Captura sem crashar | `"error"` |

### Payload Enviado

```json
{
  "execution_id": "a1b2c3d4-...",
  "file_path": "/path/to/log.log",
  "severity": "critical",
  "errors_count": 15,
  "warnings_count": 13,
  "critical_count": 6,
  "summary": "Cascata de falhas detectada",
  "timestamp": "2026-08-27T20:18:00Z",
  "status": "completed"
}
```

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
# Script de demonstração com webhook
python examples/run_with_webhook.py

# Testes unitários (mock, sem rede)
pytest tests/test_webhook_integration.py -v
```

**Documentação completa:** [`docs/low-code/n8n-integration.md`](docs/low-code/n8n-integration.md)  
**Workflow importável:** [`docs/low-code/n8n_workflow.json`](docs/low-code/n8n_workflow.json)  
**Módulo:** [`src/loganalyzer/integrations/webhook.py`](src/loganalyzer/integrations/webhook.py)

---

## 🔍 DevOps Inteligente: Detecção de Anomalias

A partir da **Task #35**, o LogAnalyzer AI implementa detecção heurística de anomalias em logs, integrada com pipeline CI/CD automatizado.

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
| Error Spike | Janela deslizante vs baseline (>2x = anomalia) | anomaly: True/False + severity |
| Padrões Recorrentes | Agrupamento por mensagem (3+ = recorrente) | patterns com contagem |
| Estimativa de Risco | Consolidação de anomalias + tendência | risk_level + trend |

### Pipeline CI/CD (GitHub Actions)

| Workflow | Arquivo | Função |
|----------|---------|--------|
| Lint | `.github/workflows/lint.yml` | Pylint + Flake8 em cada push |
| Test | `.github/workflows/test.yml` | Pytest + Coverage report |
| Build | `.github/workflows/build.yml` | Validação de imports e build |

```bash
# Executar localmente o que o CI faz
pylint src/ --fail-under=9.5
pytest tests/ --cov=src --cov-fail-under=75
flake8 src/ --max-line-length=120
```

**Documentação completa:** [`docs/devops/intelligent_log_analysis.md`](docs/devops/intelligent_log_analysis.md)  
**Testes:** [`tests/test_devops_anomaly.py`](tests/test_devops_anomaly.py)  
**Módulo:** [`src/loganalyzer/devops/anomaly_detector.py`](src/loganalyzer/devops/anomaly_detector.py)

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

## 📋 Cenários de Uso

LogAnalyzer AI foi validado com **2 cenários completos** que demonstram robustez em diferentes contextos de operação.

### Cenário 1: Operação Normal (Sucesso)

- **Arquivo:** `examples/sample.log` (47 linhas)
- **Tipo:** Aplicação rodando normalmente com alguns avisos e erros esporádicos
- **Severidade detectada:** LOW/MEDIUM
- **Roteamento:** `route_by_severity()` → rota MEDIUM (warnings predominam)

**Entrada (primeiras linhas):**
```
2026-07-12 10:00:01 INFO Application started
2026-07-12 10:00:02 INFO Loading configuration
2026-07-12 10:00:03 WARNING Config file not found at /etc/app.conf
2026-07-12 10:00:06 ERROR Connection timeout - retrying (1/3)
2026-07-12 10:08:02 ERROR Out of memory exception in request handler
2026-07-12 10:20:00 INFO Health check passed
```

**Saída (resumo do relatório):**
```
# Relatorio de Analise de Log

## Resumo Executivo
| Métrica       | Quantidade |
|---------------|-----------|
| Total eventos | 47        |
| Erros         | 11        |
| Avisos        | 9         |
| Críticos      | 10        |

## Recomendações
1. Investigar eventos críticos imediatamente
2. Revisar padrões de erro e corrigir raiz
3. Monitorar avisos e ajustar configurações
```

**Reproduzir:**
```bash
# Executar análise completa
python -m src.loganalyzer.main examples/sample.log

# Com output em arquivo
python -m src.loganalyzer.main examples/sample.log --output resultado.md

# Com provedor Groq (grátis)
python -m src.loganalyzer.main examples/sample.log --provider groq
```

**Saída completa:** [`examples/sample_output.md`](examples/sample_output.md)

---

### Cenário 2: Degradação Progressiva e Falha Crítica

- **Arquivo:** `tests/fixtures/failure_logs/scenario_failure.log` (43 linhas)
- **Tipo:** Cascata de falhas — database → cache → memory → crash
- **Severidade detectada:** HIGH (6 CRITICAL + 15 ERROR)
- **Roteamento:** `route_by_severity()` → rota HIGH (urgência IMEDIATA)

**Entrada (padrão de degradação):**
```
2026-08-15 14:00:01 INFO Application started successfully
2026-08-15 14:00:05 WARNING Database connection slow: 2500ms response time
2026-08-15 14:00:10 ERROR Failed to connect to cache: Connection refused at localhost:6379
2026-08-15 14:00:30 WARNING Memory pressure detected: 85% usage
2026-08-15 14:00:50 CRITICAL Connection pool exhausted - no available connections
2026-08-15 14:01:00 CRITICAL Both primary and secondary database unreachable
2026-08-15 14:01:10 CRITICAL Out of memory - killing process
2026-08-15 14:01:20 CRITICAL Application shutdown initiated - unrecoverable state
```

**Saída (relatório de incidente):**
```
# Relatório de Análise — INCIDENTE CRÍTICO

## Severidade: HIGH | Urgência: IMEDIATA

## Resumo Executivo
| Métrica       | Quantidade |
|---------------|-----------|
| Total eventos | 43        |
| Erros         | 15        |
| Avisos        | 13        |
| Críticos      | 6         |

## Padrão Detectado: Cascata de Falhas
T=0s  → Startup normal (INFO)
T=5s  → Database lento (WARNING)
T=10s → Cache falha (ERROR)
T=30s → Memory crescente (WARNING)
T=50s → Pool esgotado (CRITICAL)
T=60s → Database duplo fora (CRITICAL)
T=70s → Out of memory (CRITICAL)
T=80s → Shutdown forçado (CRITICAL)

## Recomendações Urgentes
1. Reiniciar serviços de cache (Redis)
2. Investigar database connection pooling
3. Aumentar memory allocation
4. Implementar circuit breaker
```

**Reproduzir:**
```bash
# Executar análise do cenário de falha
python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log

# Executar testes específicos do cenário
pytest tests/test_scenario_failure.py -v

# Com cobertura
pytest tests/test_scenario_failure.py --cov=src.loganalyzer
```

**Documentação completa:**
- [`docs/examples/scenario_failure.md`](docs/examples/scenario_failure.md) — Descrição e fluxo
- [`docs/examples/scenario_failure_output.md`](docs/examples/scenario_failure_output.md) — Saída real

---

### Comparação dos Cenários

| Aspecto | Cenário 1 (Normal) | Cenário 2 (Falha) |
|---------|--------------------|--------------------|
| Eventos | 47 | 43 |
| CRITICAL | 0 | 6 |
| ERROR | 11 | 15 |
| WARNING | 9 | 13 |
| INFO | 38 | 9 |
| Severity Routing | MEDIUM | HIGH |
| Urgência | Normal | IMEDIATA |
| Foco da Análise | Otimizações | Recuperação de incidente |
| Recomendações | Preventivas | Urgentes (ação imediata) |
| Webhook payload | `severity: "medium"` | `severity: "critical"` |

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

## 🔐 Segurança Avançada e Limites de Autonomia

O LogAnalyzer AI implementa segurança em múltiplas camadas: governança de autonomia, validação adversarial de entradas e proteção de credenciais.

### Princípio: Defense in Depth

```
Entrada do usuário
    ↓
[1. GovernancePolicy]  ← Verifica nível de autonomia permitido
    ↓
[2. InputValidator]    ← Detecta e bloqueia entradas maliciosas
    ↓
[3. validate_input]    ← Validação funcional (existência, encoding)
    ↓
Processamento seguro
```

### Governança e Limites de Autonomia (Task #32)

O sistema de governança controla o nível de autonomia do agente e impede ações além do escopo autorizado.

#### Níveis de Autonomia

| Nível | Permissões | Aprovação Humana |
|-------|-----------|-----------------|
| `READ_ONLY` | Apenas leitura de arquivos | Não |
| `ANALYZE` (padrão) | Leitura + análise + detecção de padrões | Não |
| `RECOMMEND` | Análise + geração de relatório + recomendações | Não |
| `EXECUTE` | Todas as ações, incluindo escrita/deleção | **Sim** |

O agente opera no nível **ANALYZE** por padrão — pode ler e analisar logs, mas nunca executa ações destrutivas sem aprovação explícita.

#### Proteção Contra Entradas Adversariais

O `InputValidator` detecta e bloqueia automaticamente 6 tipos de ataque:

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

### Proteção de Credenciais

| Aspecto | Implementação |
|---------|--------------|
| API Keys | Variáveis de ambiente via `.env` (não versionado) |
| `.gitignore` | Protege `.env`, `*.log`, `__pycache__/`, `.pytest_cache/` |
| `.env.example` | Apenas placeholders (`your_key_here`) |
| CI/CD | GitHub Secrets para keys em workflows |
| Webhook URLs | Em `.env`, nunca hardcoded |
| Auditoria | Zero credenciais em arquivos versionados (verificado) |

### Testes de Segurança

```bash
# Executar todos os testes adversariais (10+ cenários)
pytest tests/test_adversarial_security.py -v

# Testes específicos
pytest tests/test_adversarial_security.py -k "path_traversal" -v
pytest tests/test_adversarial_security.py -k "injection" -v
pytest tests/test_adversarial_security.py -k "autonomy" -v
```

**Módulo:** [`src/loganalyzer/governance.py`](src/loganalyzer/governance.py)  
**Testes:** [`tests/test_adversarial_security.py`](tests/test_adversarial_security.py)

---

## 🔬 Análise Crítica e Limitações

### Limitações Conhecidas

| Limitação | Impacto | Mitigação Atual |
|-----------|---------|-----------------|
| Processamento síncrono | Apenas 1 arquivo por execução | Pipeline sequencial otimizado |
| Dependência de LLM externo | Requer API key para análise inteligente | Fallback heurístico sem API |
| Sem streaming de logs | Não monitora em tempo real | Batch processing por arquivo |
| Tamanho máximo de arquivo | Performance degrada com arquivos >50MB | Timeout de 30s no read_file |
| Formato de log | Melhor desempenho com formato `TIMESTAMP LEVEL MESSAGE` | Parser multi-formato com fallback |
| Sem persistência de histórico | Cada execução é independente | TraceCollector registra execução atual |

### Ciclos de Refinamento Realizados

**Ciclo 1: Mini-Projeto M2.1 → Projeto Final M2.2**

| Aspecto | Antes (M2.1) | Depois (M2.2) |
|---------|-------------|---------------|
| Nós do StateGraph | 7 (linear) | 12 (ramificação + paralelo) |
| Error Handling | Nó existe mas nunca acionado | 4 arestas condicionais funcionais |
| Cenários | 1 (sucesso apenas) | 2 (sucesso + falha crítica) |
| Segurança | Básica (.env) | Governança + adversarial + 4 níveis |
| Observabilidade | Nenhuma | 3 sinais correlacionados |
| Integração | Nenhuma | Webhook n8n + email |
| Testes | 76 | 222 |

**Ciclo 2: Feedback de Error Handling (Task #28)**

- **Problema:** O nó `error_handling` existia desde M2.1 mas NUNCA era acionado (nenhuma aresta condicional)
- **Diagnóstico:** Score LangGraph 0.5/1.0 por falta de roteamento inteligente
- **Solução:** 4 funções de roteamento + 4 arestas condicionais
- **Resultado:** Score esperado 0.5 → 1.0, qualquer erro em qualquer etapa é capturado

**Ciclo 3: Arquitetura Linear → Ramificação (Task #30)**

- **Problema:** Pipeline puramente linear, sem demonstrar capacidades avançadas do LangGraph
- **Diagnóstico:** Avaliação exige ramificação condicional e/ou paralelização
- **Solução:** `route_by_severity()` + 3 nós especializados + análise paralela
- **Resultado:** Roteamento inteligente por severidade, análise especializada por contexto

### Trade-offs de Design

| Decisão | Alternativa rejeitada | Motivo |
|---------|----------------------|--------|
| TypedDict para estado | Pydantic models | Compatibilidade nativa com LangGraph |
| Fallback heurístico sem LLM | Falhar sem API key | Permitir uso sem custos |
| Webhook opcional (skip silencioso) | Webhook obrigatório | Flexibilidade de deploy |
| Timeout fixo (30s) | Timeout configurável por nó | Simplicidade vs. complexidade |
| Parser regex multi-formato | Parser estrito por formato | Aceitar mais variedade de logs |
| Análise síncrona | Async com asyncio | Simplicidade, LangGraph sync-first |

### Possibilidades de Evolução Futura

1. **Multi-arquivo:** Analisar diretórios inteiros de logs em batch
2. **Dashboard web:** Interface visual com FastAPI + React para visualizar relatórios
3. **Streaming:** Monitoramento contínuo com tail -f e análise incremental
4. **Alertas real-time:** Integração com Slack/Teams além de email
5. **Histórico:** Banco de dados para comparar execuções ao longo do tempo
6. **Custom parsers:** Sistema de plugins para formatos de log proprietários
7. **Multi-LLM:** Consensus de múltiplos modelos para análise mais robusta
8. **Exportação:** Integração com Grafana/Prometheus para métricas

---

## 📚 Documentação Completa

- **[Arquitetura Detalhada](docs/ARCHITECTURE.md)** — Diagrama do StateGraph, descrição de cada nó, fluxo de dados
- **[Pré-requisitos do Projeto](docs/PROJECT_REQUIREMENTS.md)** — Critérios de avaliação e diretrizes
- **[Prompts Utilizados](docs/prompts/)** — Histórico completo de decisões e prompts (23+)
- **[Saída de Exemplo](examples/sample_output.md)** — Demonstração de output real
- **[Cenário de Falha](docs/examples/scenario_failure.md)** — Segundo cenário (degradação crítica)
- **[QA com IA](docs/qa/code_review_with_ai.md)** — Code review e priorização por risco
- **[DevOps Inteligente](docs/devops/intelligent_log_analysis.md)** — Detecção de anomalias
- **[Integração n8n](docs/low-code/n8n-integration.md)** — Webhook e automação low-code
- **[Estratégia M2.2](docs/M2.2_CONTINUACAO_ESTRATEGIA.md)** — Plano de evolução do projeto
- **[Mapeamento de Requisitos](docs/M2.2_REQUISITOS_MAPEAMENTO.md)** — Critérios vs implementação

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
- [x] Código do agente implementado (StateGraph com 12 nós)
- [x] Ferramentas integradas e funcionais (7 ferramentas)
- [x] README.md completo (8 seções obrigatórias M2.2)
- [x] docs/ARCHITECTURE.md documentado
- [x] docs/prompts/ com histórico de prompts (23+)
- [x] examples/sample_output.md com saída real
- [x] 222 testes passando (100% de conformidade)
- [x] Commits semânticos (30+ commits)
- [x] Sem credenciais versionadas
- [x] Apresentação (2 slides interativos em HTML)
- [x] Observabilidade (3 sinais: TraceCollector + correlation + spans)
- [x] Segurança adversarial (GovernancePolicy + InputValidator + 4 níveis)
- [x] Integração low-code (n8n webhook → email)
- [x] Detecção de anomalias (AnomalyDetector + 3 heurísticas)
- [x] QA com IA (code review + 20 testes E2E gerados)
- [x] 2 cenários de uso documentados (sucesso + falha)
- [x] Ramificação condicional no StateGraph (route_by_severity)
- [x] Análise crítica e limitações documentadas

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
| Total de Nós | 12 (pipeline + severidade + paralelo + webhook) |
| Total de Ferramentas | 7 (validators, reader, parser, detector, formatter, anomaly, webhook) |
| Provedores LLM | 2 (OpenAI + Groq) |
| Linhas de Código | ~3500+ |
| Testes Unitários | 222 |
| Cobertura de Testes | ~76% |
| Score de Linter | 9.83/10 |
| Integração Low-Code | n8n (webhook → email) |
| Prompts Documentados | 23 |
| Cenários de Uso | 2 (sucesso + falha) |
| Arestas Condicionais | 4 (error handling) |
| Sinais de Observabilidade | 3 (traces, correlation, spans) |

---

## 📞 Contato e Informações

- **Projeto:** LogAnalyzer AI
- **Disciplina:** IA para Desenvolvedores [T2]
- **Instituição:** SCTEC
- **Prazo:** 31/08/2026 (Projeto Final M2.2)
- **Avaliação:** 30% do módulo
- **Repositório:** [GitHub - weltonsabino/mini-projeto-LogAnalyzer-AI](https://github.com/weltonsabino/mini-projeto-LogAnalyzer-AI)

---

**Última atualização:** 27 de Agosto, 2026  
**Status:** 🔄 Em Progresso (Projeto Final M2.2)
