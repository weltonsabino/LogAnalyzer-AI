Prompt: Implementar Task #31 - Segundo Cenário de Uso (Risco/Falha)
Responsável: Welton Sabino
Usuário: welton-sabino
Data/hora: 2026-08-20 21:30:00

## Prompt original

# Task #31: Segundo Cenário de Uso — Risco/Falha

## ⚠️ GIT AVISO

**PROIBIDO - Operações Git Manuais:**
- ❌ NÃO fazer commits (será registrado no final)
- ❌ NÃO criar branches (operação local)
- ❌ NÃO fazer push (desenvolvedor autoriza depois)
- ❌ NÃO fazer pull requests (processo manual)

Todas as operações git serão feitas manualmente pelo desenvolvedor após conclusão da task.

---

## 📌 Objetivo

Criar e documentar um segundo cenário de uso completo do LogAnalyzer AI, demonstrando o comportamento do agente ao processar logs com padrões de risco, falhas e anomalias. Este cenário complementa o cenário básico existente em `examples/sample.log`.

**Resultado esperado:** Agente processa logs complexos com falhas, risco e anomalias, gerando análise estruturada com recomendações de ação.

---

## ✅ Requisitos Obrigatórios

### 1. Criação de Log de Teste (Cenário de Falha)
Criar arquivo `tests/fixtures/failure_logs/scenario_failure.log` com:

**Características:**
- 50-100 linhas de eventos
- Mix de severidades: CRITICAL (5+), ERROR (8+), WARNING (10+), INFO (5+)
- Padrão de degradação: serviço inicia, avisos aumentam, falha crítica ocorre
- Timestamps realistas (sequência cronológica)
- Múltiplos componentes falhando: Database, API, Cache, Memory

**Conteúdo Esperado:**
```
2026-08-20 14:00:00 INFO Application starting on port 8080
2026-08-20 14:00:01 INFO Loading database configuration
2026-08-20 14:00:02 WARNING Database connection slow: 2500ms (threshold: 1000ms)
2026-08-20 14:00:05 ERROR Failed to connect to cache: Connection refused
2026-08-20 14:00:06 WARNING Retrying cache connection (1/3)
2026-08-20 14:00:10 ERROR Memory usage at 85% (threshold: 80%)
2026-08-20 14:00:15 CRITICAL Database connection lost - failover triggered
2026-08-20 14:00:16 ERROR Failover database also unreachable
2026-08-20 14:00:20 CRITICAL Service shutdown initiated - recovery failed
...
```

**Validação:**
- ✅ Arquivo é válido UTF-8
- ✅ Contém mínimo 50 linhas
- ✅ Timestamps em ordem crescente
- ✅ Múltiplos níveis de severidade

### 2. Fixtures de Teste
Criar arquivo `tests/fixtures/failure_logs/__init__.py` (vazio) para tornar dir um pacote

### 3. Teste de Cenário: test_scenario_failure.py
Criar arquivo `tests/test_scenario_failure.py` com testes:

#### 3.1 - `test_failure_log_processing()`
```python
def test_failure_log_processing():
    """Processa log de falha e valida saída estruturada"""
    # Arranjo: Carrega log de falha
    log_path = "tests/fixtures/failure_logs/scenario_failure.log"
    
    # Ato: Executa agente
    state = get_initial_state(log_path)
    agent = create_agent_graph()
    result = agent.invoke(state)
    
    # Assert: Valida resultado
    assert result["is_valid"] is True
    assert len(result["parsed_events"]) > 0
    assert len(result["errors_found"]) > 0
    assert len(result["critical_events"]) > 0
```

#### 3.2 - `test_severity_routing_in_failure_scenario()`
```python
def test_severity_routing_in_failure_scenario():
    """Valida que roteamento por severidade funciona no cenário de falha"""
    # Load log e executa
    # Assert: Deve rotear para analyze_high_severity (há CRITICAL)
    # Assert: severity_routes["HIGH"] > 0
```

#### 3.3 - `test_failure_scenario_report_generation()`
```python
def test_failure_scenario_report_generation():
    """Valida geração de relatório para cenário de falha"""
    # Executa agente
    # Assert: result["report"] contém markdown válido
    # Assert: Relatório menciona eventos críticos
    # Assert: Relatório contém recomendações
```

#### 3.4 - `test_failure_log_events_detection()`
```python
def test_failure_log_events_detection():
    """Valida detecção de eventos no log de falha"""
    # Carrega e processa
    # Assert: errors_found tem 8+ itens
    # Assert: critical_events tem 5+ itens
    # Assert: warnings_found tem 10+ itens
```

#### 3.5 - `test_failure_scenario_analysis_result()`
```python
def test_failure_scenario_analysis_result():
    """Valida analysis_result estruturado"""
    # Executa agente
    # Assert: analysis_result["severity_level"] == "HIGH"
    # Assert: "insights" em analysis_result
    # Assert: "recommendations" em analysis_result
    # Assert: len(recommendations) >= 2
```

#### 3.6 - `test_parallel_analysis_in_failure_scenario()`
```python
def test_parallel_analysis_in_failure_scenario():
    """Valida análise paralela no cenário de falha"""
    # Executa agente
    # Assert: analysis_result contém "parallel_patterns"
    # Assert: frequency_by_level tem múltiplos níveis
    # Assert: anomalies detected (timestamps fora de ordem ou gaps)
```

**Cada teste deve:**
- ✅ Usar arquivo `scenario_failure.log` real
- ✅ Validar saída estruturada
- ✅ Ter assertions claras
- ✅ Não deixar dependências de estado global

### 4. Documentação do Cenário
Criar arquivo `docs/examples/scenario_failure.md` com:

**Seções:**
1. **Descrição do Cenário**
   - Contexto: "Aplicação iniciando, degradação progressiva, falha total"
   - Duração: ~20 segundos de logs
   - Componentes afetados: Database, Cache, Memory, Service

2. **Fluxo de Eventos**
   ```
   T=0s: Startup normal
   T=2s: Warning database lento
   T=5s: Error cache falha
   T=10s: Error memory alto
   T=15s: Critical database down
   T=16s: Error failover falha
   T=20s: Critical shutdown
   ```

3. **Análise Esperada**
   - Severity: HIGH (CRITICAL events presentes)
   - Insights principais (3-5)
   - Recomendações de ação (3-5)
   - Root causes (2-3)

4. **Exemplo de Relatório**
   - Salvar output real em `docs/examples/scenario_failure_output.md`
   - Mostrar estrutura markdown
   - Destacar recomendações

5. **Como Reproduzir**
   ```bash
   python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log
   ```

### 5. Integração com README.md
Adicionar seção em README.md:

```markdown
### Cenários de Teste

#### Cenário 1: Log Normal (Já Existente)
- Arquivo: `examples/sample.log`
- Tipo: Operação normal com alguns avisos
- Output: `examples/sample_output.md`

#### Cenário 2: Log com Falha (NOVO)
- Arquivo: `tests/fixtures/failure_logs/scenario_failure.log`
- Tipo: Degradação progressiva → falha crítica
- Output: `docs/examples/scenario_failure_output.md`
- Teste: `tests/test_scenario_failure.py`

**Para reproduzir Cenário 2:**
\`\`\`bash
python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log
\`\`\`
```

### 6. Testes Obrigatórios (6+ testes)
Criar arquivo `tests/test_scenario_failure.py` com mínimo 6 testes:
- ✅ test_failure_log_processing
- ✅ test_severity_routing_in_failure_scenario
- ✅ test_failure_scenario_report_generation
- ✅ test_failure_log_events_detection
- ✅ test_failure_scenario_analysis_result
- ✅ test_parallel_analysis_in_failure_scenario

---

## 📊 Critérios de Aceição

| Critério | Status |
|----------|--------|
| ✅ Log de falha criado (50+ linhas, múltiplas severidades) | OBRIGATÓRIO |
| ✅ Arquivo é válido UTF-8 e processável | OBRIGATÓRIO |
| ✅ Testes de cenário implementados (6+) | OBRIGATÓRIO |
| ✅ Documentação em `docs/examples/scenario_failure.md` | OBRIGATÓRIO |
| ✅ Output exemplo salvo em `scenario_failure_output.md` | OBRIGATÓRIO |
| ✅ README.md atualizado com Cenário 2 | OBRIGATÓRIO |
| ✅ 6+ testes passando | OBRIGATÓRIO |
| ✅ Sem quebra de testes anteriores | OBRIGATÓRIO |
| ✅ Demonstra roteamento por severidade | OBRIGATÓRIO |
| ✅ Demonstra análise paralela | OBRIGATÓRIO |

---

## 🔄 Ordem de Execução

### Passo 1: Criar Log de Falha (10min)
1. Criar diretório `tests/fixtures/failure_logs/`
2. Criar arquivo `scenario_failure.log` com 50-100 linhas
3. Incluir padrão de degradação real
4. Validar timestamps em ordem

### Passo 2: Criar Fixtures (5min)
1. Criar `tests/fixtures/__init__.py` (se não existir)
2. Criar `tests/fixtures/failure_logs/__init__.py`

### Passo 3: Implementar Testes (20min)
1. Criar `tests/test_scenario_failure.py`
2. Implementar 6+ testes
3. Validar com: `pytest tests/test_scenario_failure.py -v`

### Passo 4: Executar Agente e Gerar Output (10min)
1. Rodar agente com `scenario_failure.log`
2. Capturar output completo
3. Salvar em `docs/examples/scenario_failure_output.md`

### Passo 5: Documentar Cenário (15min)
1. Criar `docs/examples/scenario_failure.md`
2. Descrever fluxo de eventos
3. Documentar análise esperada
4. Incluir instruções de reprodução

### Passo 6: Atualizar README.md (5min)
1. Adicionar seção "Cenários de Teste"
2. Descrever Cenário 1 (existente)
3. Descrever Cenário 2 (novo)
4. Incluir comando de reprodução

### Passo 7: Validação Final (10min)
1. Rodar todos os testes: `pytest` (120+ testes)
2. Validar que nenhum teste anterior quebrou
3. Verificar documentação completa

**Tempo total estimado:** 1 hora 15 min

---

## ⚠️ NÃO FAÇA

1. ❌ **Commits automáticos** — Tudo local até confirmação
2. ❌ **Criar branches** — Trabalhe na branch atual (develop)
3. ❌ **Push para origin** — Desenvolvedor faz depois
4. ❌ **Quebrar testes anteriores** — Validar com `pytest`
5. ❌ **Alterar fixtures existentes** — Criar novas apenas
6. ❌ **Logs muito pequenos** — Mínimo 50 linhas com variação

---

## 📝 Atenção Final

Após implementar TODA a Task #31 completamente:

**Você deve atualizar o arquivo `.kiro/specs/loganalyzer-ai/tasks_m2.2.md`:**

1. Localizar seção de Task #31
2. Mudar `**Status:** A Fazer` → `**Status:** ✅ CONCLUÍDO`
3. Adicionar `**Data de Conclusão:** 2026-08-20` (data atual)
4. Adicionar `**Referência de Execução:** docs/prompts/2026-08-20_task-31-EXECUTION_SUMMARY.md`
5. Marcar todas as subtarefas com `[x]` (checkboxes)
6. Atualizar a tabela resumida (linha 31: status = ✅ CONCLUÍDO)

**Não fazer commit disso** — desenvolvedor fará após revisar.

---

**Instruções de Registro:**

Este prompt será automaticamente registrado em `docs/prompts/` conforme a regra **"prompt-registration-mandatory"** do projeto. Nenhuma ação adicional necessária — o registro ocorre antes da execução.

