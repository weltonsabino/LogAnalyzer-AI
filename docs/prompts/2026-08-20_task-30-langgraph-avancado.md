Prompt: Implementar Task #30 - LangGraph Avançado com Ramificação + Paralelização
Responsável: Welton Sabino
Usuário: welton-sabino
Data/hora: 2026-08-20 20:08:00

## Prompt original

# Task #30: LangGraph Avançado — Ramificação Condicional + Paralelização

## ⚠️ GIT AVISO

**PROIBIDO - Operações Git Manuais:**
- ❌ NÃO fazer commits (será registrado no final)
- ❌ NÃO criar branches (operação local)
- ❌ NÃO fazer push (desenvolvedor autoriza depois)
- ❌ NÃO fazer pull requests (processo manual)

Todas as operações git serão feitas manualmente pelo desenvolvedor após conclusão da task.

---

## 📌 Objetivo

Implementar ramificação condicional e paralelização no StateGraph do LogAnalyzer AI, permitindo:
1. Roteamento inteligente baseado em severidade dos eventos
2. Análise paralela de padrões para melhor performance
3. Validação com 8+ testes

**Resultado esperado:** Agente capaz de processar logs em paralelo e tomar decisões inteligentes de roteamento.

---

## ✅ Requisitos Obrigatórios

### 1. Função de Roteamento por Severidade
Implementar em `src/loganalyzer/agent.py`:

```python
def route_by_severity(state: LogAnalysisState) -> str:
    """
    Roteia análise com base na severidade dos eventos detectados.
    
    Retorna:
        - "analyze_high_severity": Se há eventos críticos (CRITICAL, ERROR)
        - "analyze_medium_severity": Se há eventos médios (WARNING)
        - "analyze_low_severity": Se há eventos baixos (INFO, DEBUG)
    """
    # Lógica: Verificar severity dos parsed_events
    # Retornar rota baseada na severidade máxima encontrada
    pass
```

**Validação:**
- ✅ Função recebe estado como parâmetro
- ✅ Retorna string válida (nome do nó de destino)
- ✅ Lógica baseada em `state["parsed_events"]`

### 2. Três Nós de Análise Especializados
Implementar em `src/loganalyzer/nodes.py`:

#### 2.1 - `analyze_high_severity_node()`
- Processa CRITICAL e ERROR com prioridade máxima
- Usa modelo de IA com instruções específicas para eventos críticos
- Seta `state["analysis_result"]["severity_level"] = "HIGH"`

#### 2.2 - `analyze_medium_severity_node()`
- Processa WARNING com análise balanceada
- Usa modelo padrão do LLM
- Seta `state["analysis_result"]["severity_level"] = "MEDIUM"`

#### 2.3 - `analyze_low_severity_node()`
- Processa INFO e DEBUG com análise simplificada
- Usa heurística local (sem chamar LLM necessariamente)
- Seta `state["analysis_result"]["severity_level"] = "LOW"`

**Cada nó deve:**
- ✅ Validar estado de entrada
- ✅ Processar eventos com lógica apropriada
- ✅ Retornar estado atualizado
- ✅ Settar `severity_level` em `analysis_result`

### 3. Nó de Análise Paralela
Implementar em `src/loganalyzer/nodes.py`:

```python
async def analyze_patterns_node_parallel(state: LogAnalysisState) -> LogAnalysisState:
    """
    Analisa padrões em paralelo usando asyncio.
    
    Processa:
        - Detecção de padrões recorrentes
        - Análise de frequência de erros
        - Identificação de anomalias
    
    Retorna:
        Estado com `analysis_result["patterns"]` populado
    """
    # Usar asyncio.gather() para paralelizar tarefas
    # Combinar resultados de forma thread-safe
    pass
```

**Validação:**
- ✅ Função é async
- ✅ Usa `asyncio.gather()` para paralelização
- ✅ Retorna resultados combinados
- ✅ Mantém thread-safety

### 4. Arestas Condicionais no StateGraph
Adicionar em `src/loganalyzer/agent.py` no método `build()`:

```python
# Aresta condicional após analyze_patterns
graph.add_conditional_edges(
    "analyze_patterns",
    route_by_severity,
    {
        "analyze_high_severity": "analyze_high_severity",
        "analyze_medium_severity": "analyze_medium_severity",
        "analyze_low_severity": "analyze_low_severity",
    }
)

# Arestas dos nós especializados para o próximo nó
graph.add_edge("analyze_high_severity", "interpret_with_llm")
graph.add_edge("analyze_medium_severity", "interpret_with_llm")
graph.add_edge("analyze_low_severity", "interpret_with_llm")
```

**Validação:**
- ✅ Rota condicional implementada
- ✅ 3 destinos possíveis
- ✅ Arestas de saída para nó comum

### 5. Campo de Severidade no Estado
Adicionar em `src/loganalyzer/models.py`:

```python
class LogAnalysisState(TypedDict):
    # ... campos existentes ...
    severity_routes: dict  # Ex: {"HIGH": 3, "MEDIUM": 2, "LOW": 5}
```

### 6. Testes Obrigatórios (8+ testes)
Implementar em `tests/test_advanced_langgraph.py` (novo arquivo):

#### Testes de Roteamento
- `test_route_high_severity_events()` — Valida rota para eventos críticos
- `test_route_medium_severity_events()` — Valida rota para warnings
- `test_route_low_severity_events()` — Valida rota para info/debug

#### Testes de Nós Especializados
- `test_analyze_high_severity_node()` — Valida processamento crítico
- `test_analyze_medium_severity_node()` — Valida processamento médio
- `test_analyze_low_severity_node()` — Valida processamento baixo

#### Testes de Paralelização
- `test_analyze_patterns_parallel()` — Valida execução paralela
- `test_parallel_performance()` — Valida que paralelo é mais rápido que sequencial

#### Testes de Integração
- `test_langgraph_routing_integration()` — Fluxo completo com roteamento
- `test_multiple_severity_levels()` — Processa múltiplos níveis em um log

**Cada teste deve:**
- ✅ Usar fixtures com dados reais
- ✅ Validar saída estruturada
- ✅ Não deixar dependências de arquivo
- ✅ Ter assertions claras

### 7. Documentação
Atualizar em `docs/ARCHITECTURE.md`:
- ✅ Seção "Ramificação Condicional por Severidade" (~150 linhas)
- ✅ Diagrama do fluxo com roteamento
- ✅ Exemplos de cada caminho (HIGH, MEDIUM, LOW)

Atualizar em `README.md`:
- ✅ Seção "Análise Inteligente por Severidade"
- ✅ Exemplo: log com múltiplas severidades → resultado roteado

---

## 📊 Critérios de Aceição

| Critério | Status |
|----------|--------|
| ✅ Função `route_by_severity()` implementada | OBRIGATÓRIO |
| ✅ 3 nós especializados (HIGH, MEDIUM, LOW) | OBRIGATÓRIO |
| ✅ Nó `analyze_patterns_node_parallel()` com async | OBRIGATÓRIO |
| ✅ 4 arestas condicionais adicionadas ao grafo | OBRIGATÓRIO |
| ✅ Campo `severity_routes` no estado | OBRIGATÓRIO |
| ✅ 8+ testes passando (HIGH, MEDIUM, LOW, paralelo, integração) | OBRIGATÓRIO |
| ✅ ARCHITECTURE.md atualizado | OBRIGATÓRIO |
| ✅ README.md com exemplos | OBRIGATÓRIO |
| ✅ Sem quebra de testes anteriores | OBRIGATÓRIO |
| ✅ Pylint ≥ 9.8/10 | ESPERADO |

---

## 🔄 Ordem de Execução

### Passo 1: Implementar Função de Roteamento (10min)
1. Adicionar `route_by_severity()` em `src/loganalyzer/agent.py`
2. Lógica: Verificar severidade máxima em `parsed_events`
3. Retornar nome do nó apropriado

### Passo 2: Implementar 3 Nós Especializados (20min)
1. Criar `analyze_high_severity_node()` em `src/loganalyzer/nodes.py`
2. Criar `analyze_medium_severity_node()`
3. Criar `analyze_low_severity_node()`
4. Cada um com lógica apropriada e seta `severity_level`

### Passo 3: Implementar Análise Paralela (15min)
1. Criar `analyze_patterns_node_parallel()` em `src/loganalyzer/nodes.py`
2. Usar `asyncio.gather()` para paralelizar
3. Combinar resultados

### Passo 4: Adicionar Arestas ao StateGraph (10min)
1. Adicionar rota condicional após `analyze_patterns`
2. Adicionar 3 arestas de saída dos nós especializados
3. Atualizar `build()` method em `src/loganalyzer/agent.py`

### Passo 5: Atualizar Estado (5min)
1. Adicionar `severity_routes` em `src/loganalyzer/models.py`

### Passo 6: Implementar Testes (30min)
1. Criar `tests/test_advanced_langgraph.py`
2. Implementar 10+ testes
3. Validar roteamento, nós especializados, paralelização
4. Rodar: `pytest tests/test_advanced_langgraph.py -v`

### Passo 7: Atualizar Documentação (15min)
1. Atualizar `docs/ARCHITECTURE.md` com seção de ramificação
2. Atualizar `README.md` com exemplos
3. Validar links

### Passo 8: Validação Final (10min)
1. Rodar: `pytest` (todos os testes)
2. Rodar: `pylint src/` (validar score)
3. Rodar: `pytest --cov` (cobertura)

**Tempo total estimado:** 1 hora 15 min

---

## ⚠️ NÃO FAÇA

1. ❌ **Commits automáticos** — Tudo local até confirmação
2. ❌ **Criar branches** — Trabalhe na branch atual (develop)
3. ❌ **Push para origin** — Desenvolvedor faz depois
4. ❌ **Quebrar testes anteriores** — Validar com `pytest`
5. ❌ **Alterar código legado** — Apenas adicionar novos nós
6. ❌ **Deixar tipo hints incompletos** — Validar com pylint

---

## 📝 Atenção Final

Após implementar TODA a Task #30 completamente:

**Você deve atualizar o arquivo `.kiro/specs/loganalyzer-ai/tasks_m2.2.md`:**

1. Localizar seção de Task #30
2. Mudar `**Status:** A Fazer` → `**Status:** ✅ CONCLUÍDO`
3. Adicionar `**Data de Conclusão:** 2026-08-20` (data atual)
4. Adicionar `**Referência de Execução:** docs/prompts/2026-08-20_task-30-EXECUTION_SUMMARY.md`
5. Marcar todas as subtarefas com `[x]` (checkboxes)
6. Atualizar a tabela resumida (linha 30: status = ✅ CONCLUÍDO)

**Não fazer commit disso** — desenvolvedor fará após revisar.

---

**Instruções de Registro:**

Este prompt será automaticamente registrado em `docs/prompts/` conforme a regra **"prompt-registration-mandatory"** do projeto. Nenhuma ação adicional necessária — o registro ocorre antes da execução.

