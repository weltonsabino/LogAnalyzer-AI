# Arquitetura do LogAnalyzer AI

## Visão Geral

LogAnalyzer AI é um agente inteligente baseado em LangGraph que automatiza a análise de arquivos de log, identificando padrões, erros críticos e gerando relatórios estruturados em markdown.

### Características Principais

- **Análise Automatizada:** Processa logs em múltiplos formatos
- **IA Integrada:** Utiliza GPT-4 com fallback automático
- **Relatórios Estruturados:** Saída em markdown com métricas e recomendações
- **Tratamento Robusto de Erros:** Validações em cada etapa
- **Contexto Compartilhado:** State gerenciado pelo LangGraph

---

## Arquitetura em Camadas

```
┌─────────────────────────────────────────┐
│         CLI / Interface do Usuário       │
│         (main.py)                       │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│         StateGraph (agent.py)            │
│     ┌──────────────────────────────┐    │
│     │   Orquestração de Nós        │    │
│     │   Gerenciamento de Estado    │    │
│     └──────────────────────────────┘    │
└────────────────────┬────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼──────┐  ┌────▼─────┐  ┌──────▼──┐
│   Nós    │  │ Ferramentas│  │ Análise │
│(nodes.py)│  │(tools/)   │  │(analysis/)│
└──────────┘  └───────────┘  └──────────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
┌────────────────────▼────────────────────┐
│       Modelos de Dados (models.py)      │
│       LogAnalysisState com 19 campos    │
└─────────────────────────────────────────┘
```

---

## Estado Compartilhado (LogAnalysisState)

O `LogAnalysisState` é um TypedDict que mantém todas as informações durante execução:

```python
class LogAnalysisState(TypedDict):
    # Entrada
    file_path: str                           # Caminho do arquivo
    file_content: str                        # Conteúdo completo
    
    # Resultados da análise
    parsed_events: List[Dict[str, Any]]     # Eventos parseados
    errors_found: List[Dict[str, Any]]      # Erros identificados
    warnings_found: List[Dict[str, Any]]    # Avisos encontrados
    critical_events: List[Dict[str, Any]]   # Eventos críticos
    
    # Saída do agente
    analysis_result: Dict[str, Any]         # Análise estruturada
    report: str                             # Relatório markdown
    
    # Metadados
    metadata: Dict[str, Any]                # Info de processamento
    is_valid: bool                          # Status de validação
    error_message: Optional[str]            # Mensagem de erro
```

---

## Fluxo de Execução (StateGraph)

### Diagrama do Grafo

```
                    ┌─────────────────┐
                    │     INÍCIO      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ validate_input  │
                    │ Valida caminho  │
                    └────────┬────────┘
                             │ (válido)
                    ┌────────▼────────┐
                    │   read_file     │
                    │ Lê conteúdo     │
                    └────────┬────────┘
                             │ (sucesso)
                    ┌────────▼────────┐
                    │  parse_events   │
                    │ Extrai eventos  │
                    └────────┬────────┘
                             │ (sucesso)
                    ┌────────▼────────────────┐
                    │ analyze_patterns       │
                    │ Detecta erros/avisos   │
                    └────────┬────────────────┘
                             │ (sucesso)
                    ┌────────▼────────────────┐
                    │ interpret_with_llm     │
                    │ Análise inteligente     │
                    └────────┬────────────────┘
                             │ (sucesso)
                    ┌────────▼────────────────┐
                    │  generate_report       │
                    │ Formata saída markdown │
                    └────────┬────────────────┘
                             │
                    ┌────────▼────────┐
                    │       FIM       │
                    └─────────────────┘
                    
    (Em caso de erro em qualquer etapa)
                    └──→ error_handling → FIM
```

---

## Arestas Condicionais (Roteamento Inteligente)

### Overview
O grafo utiliza arestas condicionais para redirecionar automaticamente para error_handling quando qualquer nó detecta uma falha. Isso melhora a robustez do sistema e garante que erros não causem travamentos.

### 4 Rotas Condicionais Implementadas

#### 1. **validate_input → error_handling | read_file**
- **Condição:** `state.get("validation_error")`
- **Acionado em:** Arquivo inválido, sem permissão, encoding incorreto
- **Flag:** `validation_error: Optional[str]`
- **Comportamento:** Se erro, vai direto para error_handling; senão, vai para read_file

#### 2. **parse_events → error_handling | analyze_patterns**
- **Condição:** `state.get("parsing_error")`
- **Acionado em:** Formato de log não reconhecido, parsing falha
- **Flag:** `parsing_error: Optional[str]`
- **Comportamento:** Se erro, redireciona; senão, continua normalmente

#### 3. **analyze_patterns → error_handling | interpret_with_llm**
- **Condição:** `state.get("detection_error")`
- **Acionado em:** Sem padrões detectados, análise de padrão falha
- **Flag:** `detection_error: Optional[str]`
- **Comportamento:** Se erro, redireciona; senão, continua

#### 4. **interpret_with_llm → error_handling | generate_report**
- **Condição:** `state.get("analysis_error")`
- **Acionado em:** Timeout IA, falha de API, resposta inválida
- **Flag:** `analysis_error: Optional[str]`
- **Comportamento:** Se erro, redireciona; senão, gera relatório

### Implementação das Funções de Roteamento

**Em `src/loganalyzer/agent.py`:**

```python
def route_after_validation(state: LogAnalysisState) -> str:
    """Roteia para error_handling se validação falhar."""
    if state.get("validation_error"):
        return "error_handling"
    return "read_file"

def route_after_parsing(state: LogAnalysisState) -> str:
    """Roteia para error_handling se parsing falhar."""
    if state.get("parsing_error"):
        return "error_handling"
    return "analyze_patterns"

def route_after_detection(state: LogAnalysisState) -> str:
    """Roteia para error_handling se detecção falhar."""
    if state.get("detection_error"):
        return "error_handling"
    return "interpret_with_llm"

def route_after_analysis(state: LogAnalysisState) -> str:
    """Roteia para error_handling se análise IA falhar."""
    if state.get("analysis_error"):
        return "error_handling"
    return "generate_report"
```

### Adição das Arestas Condicionais

**No método `create_agent_graph()`, seção "ADICIONA ARESTAS":**

```python
# Aresta condicional após validação
graph.add_conditional_edges(
    "validate_input",
    route_after_validation,
    {
        "error_handling": "error_handling",
        "read_file": "read_file"
    }
)

# Aresta condicional após parsing
graph.add_conditional_edges(
    "parse_events",
    route_after_parsing,
    {
        "error_handling": "error_handling",
        "analyze_patterns": "analyze_patterns"
    }
)

# Aresta condicional após detecção
graph.add_conditional_edges(
    "analyze_patterns",
    route_after_detection,
    {
        "error_handling": "error_handling",
        "interpret_with_llm": "interpret_with_llm"
    }
)

# Aresta condicional após análise
graph.add_conditional_edges(
    "interpret_with_llm",
    route_after_analysis,
    {
        "error_handling": "error_handling",
        "generate_report": "generate_report"
    }
)
```

### Fluxo Normal vs Fluxo com Erro

**Caminho de Sucesso:**
```
validate_input [✓] → read_file [✓] → parse_events [✓] → 
analyze_patterns [✓] → interpret_with_llm [✓] → generate_report [✓] → END
```

**Caminho com Erro (exemplo: parsing falha):**
```
validate_input [✓] → read_file [✓] → parse_events [ERROR] → 
[route_after_parsing retorna "error_handling"] → error_handling → END
```

**Caminho com Erro Inicial:**
```
validate_input [ERROR] → 
[route_after_validation retorna "error_handling"] → error_handling → END
```

### Campos de Erro no Estado

Os 4 novos campos no `LogAnalysisState` permitem roteamento granular:

```python
class LogAnalysisState(TypedDict):
    # ... campos anteriores ...
    
    # Flags de erro específicas por etapa (para roteamento condicional)
    validation_error: Optional[str]  # Erro na validação
    parsing_error: Optional[str]     # Erro no parsing
    detection_error: Optional[str]   # Erro na detecção de padrões
    analysis_error: Optional[str]    # Erro na análise IA
```

Cada nó seta o campo correspondente quando ocorre erro:
- `validate_input_node` seta `validation_error`
- `parse_events_node` seta `parsing_error`
- `analyze_patterns_node` seta `detection_error`
- `interpret_with_llm_node` seta `analysis_error`

### Benefícios da Implementação

1. **Robustez:** Erros não causam travamento
2. **Rastreabilidade:** Fácil identificar em qual etapa ocorreu erro
3. **Granularidade:** Cada etapa tem seu próprio tipo de erro
4. **Extensibilidade:** Fácil adicionar novas condições
5. **Manutenibilidade:** Lógica de roteamento é explícita

---

## Detalhamento dos Nós

### 1. **validate_input_node** (Validação)
- **Função:** Valida se o arquivo existe e é acessível
- **Entrada:** `file_path` do estado
- **Saída:** Atualiza `is_valid` e `error_message`
- **Arquivo:** `nodes.py` (linhas 21-54)
- **Ferramentas:** `validators.py`

### 2. **read_file_node** (Leitura)
- **Função:** Lê conteúdo completo do arquivo
- **Entrada:** `file_path` validado
- **Saída:** Popula `file_content`
- **Arquivo:** `nodes.py` (linhas 55-106)
- **Ferramentas:** `file_reader.py`
- **Tratamento:** Suporta encoding UTF-8, com fallback

### 3. **parse_events_node** (Parsing)
- **Função:** Extrai eventos estruturados do log
- **Entrada:** `file_content` bruto
- **Saída:** Popula `parsed_events` (lista de dicts)
- **Arquivo:** `nodes.py` (linhas 107-150)
- **Ferramentas:** `parser.py`
- **Formatos:** JSON, regex, texto puro

### 4. **analyze_patterns_node** (Detecção)
- **Função:** Identifica padrões, erros e avisos
- **Entrada:** `parsed_events`
- **Saída:** Popula `errors_found`, `warnings_found`, `critical_events`
- **Arquivo:** `nodes.py` (linhas 151-195)
- **Ferramentas:** `detector.py`
- **Keywords:** Identifica severidade por palavras-chave

### 5. **interpret_with_llm_node** (IA)
- **Função:** Analisa eventos com modelo de linguagem
- **Entrada:** `parsed_events`, `critical_events`
- **Saída:** Popula `analysis_result`
- **Arquivo:** `nodes.py` (linhas 196-244)
- **Ferramentas:** `llm_interpreter.py`
- **Modelo:** GPT-4 Turbo (com fallback heurístico)
- **Features:** Identifica causas raiz e recomendações

### 6. **generate_report_node** (Formatação)
- **Função:** Converte análise em relatório markdown
- **Entrada:** `analysis_result`, `errors_found`, `critical_events`
- **Saída:** Popula `report`
- **Arquivo:** `nodes.py` (linhas 245-289)
- **Ferramentas:** `formatter.py`
- **Estrutura:** Seções de resumo, eventos críticos, recomendações

### 7. **error_handling_node** (Tratamento)
- **Função:** Trata erros e encerra execução graciosamente
- **Entrada:** `error_message` do estado
- **Saída:** Garante saída consistente mesmo em erro
- **Arquivo:** `nodes.py` (linhas 290-305)

---

## Ferramentas Integradas

### `validators.py`
- `validate_file_path()` → Valida arquivo
- `validate_events()` → Valida estrutura de eventos

### `file_reader.py`
- `read_log_file()` → Lê arquivo com tratamento de encoding

### `parser.py`
- `parse_log_events()` → Extrai eventos de múltiplos formatos

### `detector.py`
- `detect_patterns()` → Identifica erros/avisos/críticos
- `find_critical_patterns()` → Localiza eventos severidade alta

### `formatter.py`
- `format_report()` → Gera markdown com métricas e insights

### `llm_interpreter.py`
- `analyze_with_llm()` → Chamada ao GPT-4 Turbo
- `generate_fallback_analysis()` → Análise heurística sem LLM

---

## Fluxo de Dados

```
╔════════════════════════╗
║  Arquivo de Log        ║
║  (sample.log)          ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Validação            ║
║  ✓ Existe?            ║
║  ✓ Legível?           ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Conteúdo Bruto       ║
║  (strings)            ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Parsing              ║
║  Estrutura: evento    ║
║  timestamp, level     ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Detecção de Padrões ║
║  errors, warnings     ║
║  critical_events      ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Análise com IA       ║
║  (LLM ou fallback)    ║
║  causas_raiz          ║
║  recomendações        ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Formatação          ║
║  Markdown Report      ║
║  + Métricas          ║
╚────────────┬───────────╝
             │
             ▼
╔════════════════════════╗
║  Relatório Final      ║
║  (output.md)          ║
╚════════════════════════╝
```

---

## Integração com LLM

### Configuração
- **Provider:** OpenAI (GPT-4 Turbo)
- **Variável:** `OPENAI_API_KEY` em `.env`
- **Temperature:** 0.7 (criativo mas consistente)

### Fluxo
```
Eventos Críticos
     │
     ▼
Prompt Estruturado (veja docs/prompts/)
     │
     ▼
GPT-4 Turbo
     │
     ├─→ Sucesso: JSON estruturado
     │        │
     │        ▼
     │    analysis_result
     │
     └─→ Erro/Sem API Key
              │
              ▼
          Fallback Heurístico
               │
               ▼
          analysis_result (simples)
```

### Fallback Automático
Quando `OPENAI_API_KEY` não está configurada ou chamada falha:
- Análise baseada em regras heurísticas
- Identificação de padrões por keywords
- Recomendações genéricas mas úteis

---

## Decisões Arquiteturais

### 1. **Uso de LangGraph (StateGraph)**
- ✅ Gerenciamento automático de estado
- ✅ Fácil visualização e debug do fluxo
- ✅ Escalabilidade para novos nós

### 2. **Separação em Ferramentas**
- ✅ Responsabilidade única por ferramenta
- ✅ Fácil testes unitários
- ✅ Reutilização em múltiplos nós

### 3. **Fallback para Análise Heurística**
- ✅ Funciona sem OpenAI API
- ✅ Reduz custos em produção
- ✅ Nunca falha (degradação graciosa)

### 4. **Estado Tipado (TypedDict)**
- ✅ Type hints para IDE support
- ✅ Documentação automática de campos
- ✅ Validação em tempo de execução

---

## Ramificação Condicional por Severidade (Task #30)

### Contexto

Após análise de padrões, o agente agora roteia para processamento especializado baseado na severidade máxima dos eventos detectados.

### Função de Roteamento

```python
def route_by_severity(state: LogAnalysisState) -> str:
    """
    Roteia análise com base na severidade dos eventos.
    
    Retorna:
        - "analyze_high_severity": Se há CRITICAL ou ERROR
        - "analyze_medium_severity": Se há WARNING
        - "analyze_low_severity": Se há INFO, DEBUG, TRACE
    """
```

### Três Caminhos de Análise Especializados

#### 1. **Alta Severidade** (CRITICAL, ERROR)
- **Processamento:** Foco em incidentes críticos
- **LLM Context:** Instruções para recuperação de falhas
- **Saída:** `severity_level = "HIGH"`, `urgency = "IMEDIATA"`
- **Nó:** `analyze_high_severity_node()`

#### 2. **Severidade Média** (WARNING)
- **Processamento:** Análise balanceada preventiva
- **LLM Context:** Instruções padrão
- **Saída:** `severity_level = "MEDIUM"`, `urgency = "NORMAL"`
- **Nó:** `analyze_medium_severity_node()`

#### 3. **Baixa Severidade** (INFO, DEBUG, TRACE)
- **Processamento:** Análise simplificada com insights
- **LLM Context:** Foco em otimização
- **Saída:** `severity_level = "LOW"`, `urgency = "BAIXA"`
- **Nó:** `analyze_low_severity_node()`

### Diagrama de Roteamento

```
parse_events
      │
      ▼
analyze_patterns
      │
      ▼
route_by_severity (função condicional)
      │
    ┌─┼─┐
    │ │ │
┌───▼─┴─┴─────────────────────────────────────┐
│   Ramificação Condicional (3 caminhos)      │
│  ┌──────────────────────────────────────┐   │
│  │ Se há CRITICAL/ERROR:                │   │
│  │   → analyze_high_severity            │   │
│  ├──────────────────────────────────────┤   │
│  │ Elif há WARNING:                     │   │
│  │   → analyze_medium_severity          │   │
│  ├──────────────────────────────────────┤   │
│  │ Else (INFO/DEBUG/TRACE):             │   │
│  │   → analyze_low_severity             │   │
│  └──────────────────────────────────────┘   │
└────────────────────────────────────────────┘
      │
      │ (3 nós convergem)
      │
      ▼
interpret_with_llm
      │
      ▼
generate_report
      │
      ▼
notify_webhook
      │
      ▼
FIM
```

### Campo de Rastreabilidade

Um novo campo foi adicionado ao `LogAnalysisState`:

```python
severity_routes: Dict[str, int]
# Exemplo: {"HIGH": 2, "MEDIUM": 1, "LOW": 5}
# Armazena contagem de eventos por nível de severidade
```

### Análise Paralela (Task #30)

Adicionalmente, foi implementado um nó de análise paralela que pode processar múltiplos aspectos simultaneamente:

```python
async def analyze_patterns_node_parallel(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa padrões em paralelo usando asyncio.gather()
    
    Processa em paralelo:
        - Padrões recorrentes
        - Frequência por severidade
        - Anomalias em timestamps
    """
```

**Resultado:** Campo `analysis_result["parallel_patterns"]` com:
- `recurrent_patterns`: Mensagens que aparecem múltiplas vezes
- `frequency_by_level`: Contagem de eventos por nível
- `anomalies`: Detecta timestamps fora de ordem

---

## Limitações Conhecidas

1. **Parsing:** Suporta principalmente formatos baseados em texto
2. **LLM:** Suporta OpenAI GPT-4 e Groq (LLaMA/Mixtral)
3. **Performance:** Logs > 10MB podem ter latência
4. **Formatos:** JSON logs requerem format específico
5. **Anomalias:** Detecção heurística (não ML)
6. **Webhook:** Requer n8n rodando (Docker local ou cloud)

---

## Extensões Futuras

1. Processamento de logs em stream
2. Integração com OpenTelemetry
3. Dashboard real-time com métricas
4. Modelo ML para predição de anomalias
5. Histórico de análises persistidas

---

## Observabilidade e Rastreabilidade (Task #33)

### Visão Geral

A partir da Task #33, LogAnalyzer AI implementa **observabilidade avançada** com 2+ sinais correlacionados para rastreamento completo de execução, permitindo auditoria, debug e monitoramento de agentes em produção.

### Sinais de Observabilidade

#### 1️⃣ Sinal 1: Traces Estruturados com TraceCollector

**O que é:** Um coletor centralizado que registra eventos de execução com timestamps ISO.

**Implementação:**
```python
class TraceCollector:
    - execution_id: str (UUID único)
    - traces: List[Dict] (eventos em ordem cronológica)
    - add_trace(node_name, event_type, data) → registra evento
    - get_traces() → retorna lista ordenada
    - get_correlation_summary() → sumário agregado
```

**Exemplos de eventos:**
- `node_start`: Nó iniciou execução
- `node_end`: Nó terminou com sucesso
- `error`: Nó lançou exceção
- `warning`: Evento de aviso sem falha
- `timeout`: Exceção de timeout
- `retry`: Tentativa de retry automático

#### 2️⃣ Sinal 2: Correlação com execution_id

**O que é:** Todos os traces de uma execução compartilham o mesmo UUID (`execution_id`), permitindo rastreamento end-to-end em sistemas distribuídos.

**Estrutura de Trace:**
```python
trace = {
    "execution_id": "a1b2c3d4-...",  # UUID único por execução
    "node_name": "read_file",        # Nó que gerou o trace
    "event_type": "node_end",        # Tipo de evento
    "timestamp": "2026-08-21T10:11:00.123456",  # ISO 8601
    "data": {                        # Metadados específicos
        "duration_seconds": 1.234,
        "success": True
    }
}
```

**Benefício:** Possibilita correlacionar todos os logs de uma execução mesmo em sistemas com múltiplos serviços.

#### 3️⃣ Sinal 3 (Bônus): Duração com Spans de Tempo

**O que é:** Cada trace registra `duration_seconds` permitindo análise de performance.

**Implementação:**
```python
@observability_middleware(collector=collector)
def process_node(state):
    # Início: node_start registrado
    result = do_work(state)
    # Fim: node_end com duration_seconds registrado
    return result
```

**Métricas extraídas:**
- Duração por nó
- Nó mais lento
- Gargalos no pipeline
- Tempo total de execução

### Decoradores de Resiliência

#### @with_timeout(seconds=30)
Limita tempo máximo de execução:

```python
@with_timeout(seconds=30)
def read_log_file(file_path: str) -> str:
    # Lançará TimeoutError se > 30s
    with open(file_path) as f:
        return f.read()
```

**Implementação:**
- Windows: Simples try/except (sem signal.SIGALRM)
- Unix/Linux: Usa signal.SIGALRM
- Aplicado a: `read_log_file()`, LLM.invoke()

#### @with_retry(max_attempts=3, backoff=1.5)
Retry automático com backoff exponencial:

```python
@with_retry(max_attempts=3, backoff=1.5)
def read_log_file(file_path: str) -> str:
    # Retry apenas para: TimeoutError, PermissionError, OSError
    # Backoff: 1s, 1.5s, 2.25s
    with open(file_path) as f:
        return f.read()
```

**Estratégia:**
- Tenta até `max_attempts` vezes
- Aguarda `backoff^attempt` segundos entre tentativas
- Apenas para erros transientes
- Falhas permanentes (FileNotFoundError) levantam imediatamente

### Integração com Agent

#### No estado inicial:
```python
state = get_initial_state(file_path="/logs/app.log")

# State agora inclui:
state["trace_collector"]  # TraceCollector ativo
state["execution_id"]     # UUID para correlação
```

#### Em cada nó:
```python
@observability_middleware(collector=state["trace_collector"])
def my_node(state: LogAnalysisState) -> LogAnalysisState:
    # Traces registrados automaticamente
    result = process(state)
    state["trace_collector"].add_trace(
        node_name="my_node",
        event_type="custom_event",
        data={"items_processed": 42}
    )
    return state
```

### Exemplo de Saída de Observabilidade

```python
# Obter sumário correlacionado
summary = state["trace_collector"].get_correlation_summary()

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
    "status": "OK",
    "start_time": "2026-08-21T10:11:00.000000",
    "end_time": "2026-08-21T10:11:03.245000"
}
```

**Interpretação:**
- **execution_id:** Identifique esta execução em logs
- **trace_count:** 42 eventos registrados (boa cobertura)
- **duration_seconds:** Levou 3.2 segundos
- **event_counts:** 1 erro, 2 avisos (investigar)
- **status:** ERROR (porque há 1 erro no event_counts)

### Casos de Uso

#### 🔍 Debug e Troubleshooting
```python
# Encontrar exatamente onde falhou
summary = collector.get_correlation_summary()
if summary["status"] == "ERROR":
    traces = collector.get_traces()
    for trace in traces:
        if trace["event_type"] == "error":
            print(f"Erro em {trace['node_name']}: {trace['data']}")
```

#### 📊 Análise de Performance
```python
# Identificar gargalos
traces = collector.get_traces()
durations = {
    t["node_name"]: t["data"]["duration_seconds"]
    for t in traces if t["event_type"] == "node_end"
}
slowest = max(durations, key=durations.get)
print(f"Nó mais lento: {slowest} ({durations[slowest]}s)")
```

#### 🔗 Correlação em Sistemas Distribuídos
```python
# Rastreie uma execução através de múltiplos serviços
log_entry = {
    "execution_id": execution_id,  # Mesmo UUID em todo lugar
    "service": "log-analyzer",
    "timestamp": datetime.now(),
    "message": "Análise concluída"
}
# Enviar para ELK Stack, Datadog, etc
```

### Testes de Observabilidade

Arquivo: `tests/test_observability.py` (27 testes)

**Categorias:**
- ✅ Inicialização (3 testes)
- ✅ Adição de traces (3 testes)
- ✅ Correlação (2 testes)
- ✅ Sumário (5 testes)
- ✅ Timeout (2 testes)
- ✅ Retry (5 testes)
- ✅ Middleware (3 testes)
- ✅ Constantes (2 testes)

**Executar:**
```bash
pytest tests/test_observability.py -v
# 27 passed in 2.50s
```

### Métricas de Qualidade

- ✅ **27 testes** para observabilidade (+195 testes existentes = 222 total)
- ✅ **Type hints** em todos os parâmetros
- ✅ **Docstrings** em português para todas as funções
- ✅ **Pylint score** ≥ 9.8/10
- ✅ **Coverage** ≥ 95% para `observability.py`

### Limitações e Considerações

1. **Windows:** @with_timeout funciona mas sem signal.SIGALRM
2. **Memory:** TraceCollector armazena todos os eventos em memória
3. **Escalabilidade:** Para logs > 10MB, considere streaming
4. **Privacy:** Não registre dados sensíveis em traces (aplique sanitização)

### Extensões Futuras

1. Persistência de traces em banco de dados
2. Streaming de traces em tempo real
3. Integração com OpenTelemetry
4. Dashboard de visualização
5. Alertas baseados em padrões de traces

---

**Status:** ✅ Implementado e Funcional (Task #33)  
**Última atualização:** 25 de Agosto, 2026  

---

## Integração Low-Code: Webhook n8n (Task #36)

### Visão Geral

O nó `notify_webhook` é o último do pipeline. Envia resultado da análise para n8n via POST HTTP, que dispara envio de email com resumo.

### Fluxo no StateGraph

```
[Sucesso]  generate_report → notify_webhook → END
[Erro]     error_handling  → notify_webhook → END
```

Toda execução (sucesso ou erro) passa pelo webhook antes de terminar.

### Comportamento

| Situação | webhook_status | Ação |
|----------|---------------|------|
| Variáveis não configuradas | `skipped` | Retorna sem fazer nada |
| Webhook configurado, POST 200 | `sent` | Payload enviado com sucesso |
| Erro de conexão/timeout | `error` | Captura, não crashar pipeline |

### Campo no Estado

```python
webhook_status: Optional[str]  # "sent", "skipped", "error"
```

### Segurança

- Zero credenciais em arquivos versionados
- URL do webhook via variável de ambiente (`N8N_WEBHOOK_URL`)
- `.env` protegido pelo `.gitignore`
- Testes usam mock (sem requests reais)

### Workflow n8n

Arquivo: `docs/low-code/n8n_workflow.json` (importável)

```
[Webhook trigger] → [Function: formata HTML] → [Send Email]
```

---

## DevOps Inteligente: Detecção de Anomalias (Task #35)

### Visão Geral

Módulo `src/loganalyzer/devops/anomaly_detector.py` implementa detecção heurística de anomalias via janela deslizante e agrupamento de padrões.

### Classe AnomalyDetector

```python
class AnomalyDetector:
    def detect_error_spike(log_lines) → dict     # Janela deslizante vs baseline
    def detect_recurring_pattern(log_lines) → dict  # Agrupa mensagens repetidas
    def estimate_risk(anomalies) → dict           # Severidade + tendência
    def analyze(log_lines) → dict                 # Orquestra tudo
```

### Matriz de Risco

| Anomalia Detectada | Risk Level | Trend |
|-------------------|------------|-------|
| Spike HIGH (>3x baseline) | critical | increasing |
| Spike MEDIUM (>2x baseline) | high | increasing |
| Padrão recorrente (5+ vezes) | medium | stable |
| Nenhuma | low | stable |

### Testes

Arquivo: `tests/test_devops_anomaly.py` (13 testes)

---

**Última atualização:** 25 de Agosto, 2026
**Versão:** 3.0

---

## Referências

- **LangGraph:** https://python.langchain.com/docs/langgraph/
- **OpenAI API:** https://platform.openai.com/docs/
- **Exemplo de Saída:** `examples/sample_output.md`
- **Prompts Utilizados:** `docs/prompts/`

---

**Status:** ✅ Implementado e Funcional (Inclui Task #30: Ramificação + Paralelização)  
**Última atualização:** 20 de Agosto, 2026  
**Versão:** 2.0
