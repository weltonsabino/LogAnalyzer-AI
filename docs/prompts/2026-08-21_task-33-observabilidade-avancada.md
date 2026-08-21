Prompt: Implementar Task #33 - Observabilidade Avançada (2+ Sinais)
Responsável: Welton Sabino
Usuário: welton-sabino
Data/hora: 2026-08-21 10:11:00

## Prompt original

Implemente a Task #33: Observabilidade Avançada do projeto LogAnalyzer AI.

**IMPORTANTE: NÃO faça commit nem crie branches. Apenas implemente o código e os testes.**

---

## Escopo da Task #33

Implementar 2+ sinais de observabilidade correlacionados conforme requisitos do Projeto Final M2.2 (seção 4.7 do documento de avaliação).

---

## Subtarefas

### 1. Criar `src/loganalyzer/observability.py`

Implementar o módulo de observabilidade com:

- **TraceCollector (classe):** Centraliza coleta de traces e correlação
  - `__init__(execution_id: str)` — Inicializa com ID único de execução
  - `add_trace(node_name: str, event_type: str, data: Dict[str, Any]) -> None` — Adiciona trace com timestamp
  - `get_traces() -> List[Dict]` — Retorna lista de traces ordenada por timestamp
  - `get_correlation_summary() -> Dict` — Retorna sumário com execution_id, trace_count, duration, status
  - `_generate_execution_id() -> str` — Gera UUID único para execução

- **ObservabilityMiddleware (função):** Decorator para instrumentar nós
  - Captura entrada/saída de cada nó
  - Registra tempo de execução
  - Captura exceções sem interromper execução
  - Incrementa contadores por nó

- **Constantes de Observabilidade:**
  - `TRACE_EVENTS` — Lista de tipos de eventos (node_start, node_end, error, warning)
  - `TRACE_LEVELS` — Níveis de rastreamento (DEBUG, INFO, WARN, ERROR)

### 2. Integrar TraceCollector no Agent

- Modificar `src/loganalyzer/agent.py`:
  - Criar instância de TraceCollector em create_agent_graph()
  - Passar collector no estado inicial (get_initial_state)
  - Usar decorator @ObservabilityMiddleware em cada nó

- Modificar `src/loganalyzer/models.py`:
  - Adicionar campo `trace_collector: Optional[TraceCollector]` em LogAnalysisState
  - Adicionar campo `execution_id: str` em LogAnalysisState

### 3. Adicionar Retry + Timeout em `file_reader.py`

- Implementar decorator @with_timeout(seconds=30):
  - Lança TimeoutError se arquivo não lido em 30s
  - Aplicável a read_log_file()

- Implementar @with_retry(max_attempts=3, backoff=1.5):
  - Retry automático com backoff exponencial
  - Apenas para erros transientes (timeout, permission denied)
  - Aplicável a read_log_file()

- Atualizar initialize_llm() com timeout:
  - LLM.invoke(prompt, timeout=15)
  - Fallback automático se timeout

### 4. Implementar Testes de Observabilidade

Criar `tests/test_observability.py` com 5+ testes:

- **test_trace_collector_initialization:** Cria collector e verifica execution_id
- **test_trace_collector_add_trace:** Adiciona traces e verifica ordem cronológica
- **test_trace_collector_correlation:** Correlaciona traces com execution_id
- **test_timeout_decorator:** Arquivo grande dispara timeout após 30s
- **test_retry_decorator:** Falha na primeira vez, sucesso na segunda
- **test_observability_middleware:** Node decorado captura entrada/saída
- **test_trace_summary:** get_correlation_summary() retorna dados corretos

### 5. Documentar em README.md

- Adicionar seção "📊 Observabilidade Avançada" com:
  - 2+ sinais de observabilidade explicados
  - Exemplo de trace correlation
  - Como usar TraceCollector
  - Timeout e retry automáticos

### 6. Atualizar ARCHITECTURE.md

- Adicionar diagrama de fluxo de traces
- Documentar correlation ID (execution_id)
- Seção "Observabilidade e Rastreabilidade" (~150 linhas)

---

## Padrões de Código (OBRIGATÓRIO)

- Comentários em português
- Variáveis e funções em inglês
- Docstrings em português
- Seguir PEP 8
- Type hints em todos os parâmetros e retornos
- Usar UUID para execution_id

---

## Referências

- Seção 4.7 do documento de avaliação: `docs/IA PARA DESENVOLVEDORES [T2] - M2S08 - Projeto Avaliativo.md`
- Mapeamento de requisitos: `docs/M2.2_REQUISITOS_MAPEAMENTO.md` (Critério 5)
- Planejamento: `docs/PROJETO_FINAL_M2.2_PLANEJAMENTO.md` (Fase 2)
- Estrutura existente: `src/loganalyzer/models.py` (LogAnalysisState)

---

## Critérios de Aceição

- [ ] Módulo `src/loganalyzer/observability.py` criado com TraceCollector e decorators
- [ ] TraceCollector integrado em create_agent_graph()
- [ ] Timeout em read_log_file() (30s máximo)
- [ ] Retry automático em read_log_file() (máx 3 tentativas)
- [ ] `tests/test_observability.py` com 7+ testes passando
- [ ] ARCHITECTURE.md atualizado com seção de observabilidade
- [ ] README.md com seção "Observabilidade Avançada"
- [ ] Todos os 85+ testes existentes continuam passando (sem regressão)
- [ ] 2+ sinais de observabilidade correlacionados funcionando
- [ ] execution_id único por execução do agente

---

## Notas Importantes

**O que é um "sinal de observabilidade":**
- Sinal 1: Logs estruturados (timestamps, contadores, metadados)
- Sinal 2: Traces correlacionados (execution_id atravessando todos os nós)
- Sinal 3 (bônus): Spans com duração (timing de cada operação)

**Dois sinais são obrigatórios. Implementar TODOS os 3 se tempo permitir.**

**Timeout e Retry:**
- Não são estritamente observabilidade, mas aumentam resiliência
- Importante para evitar travamentos em arquivos problemáticos
- Usa mesmos padrões de timeout/retry da tarefa #6

