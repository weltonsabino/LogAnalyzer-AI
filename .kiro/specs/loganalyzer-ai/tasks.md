# Tasks - LogAnalyzer AI

## Visão Geral

Este documento lista todas as tarefas (tasks) para implementação do projeto LogAnalyzer AI, um agente LangGraph para análise automatizada de logs.

---

## Task #1: Configuração Inicial do Projeto ✅ CONCLUÍDO

**Status:** Completed  
**Descrição:** Setup e estrutura base do projeto

### Subtarefas

- [x] Criar repositório GitHub (weltonsabino/mini-projeto-LogAnalyzer-AI)
- [x] Estruturar diretórios (src/, tests/, docs/)
- [x] Configurar requirements.txt com dependências
- [x] Criar .gitignore e .env.example
- [x] Escrever README.md inicial

### Artefatos Criados

- `requirements.txt` — Dependências do projeto
- `README.md` — Documentação inicial
- `.gitignore` — Arquivos ignorados
- `.env.example` — Template de variáveis de ambiente

### Critérios de Aceição

- ✅ Repositório acessível publicamente no GitHub
- ✅ Estrutura de pastas conforme docs/PROJECT_REQUIREMENTS.md
- ✅ Dependências instaláveis sem erros
- ✅ Variáveis de ambiente protegidas (.env ignorado)

---

## Task #2: Definir Arquitetura e Models do StateGraph ✅ CONCLUÍDO

**Status:** Completed  
**Descrição:** Criar estrutura base de modelos e graph architecture

### Subtarefas

- [x] Definir LogAnalysisState (TypedDict)
  - Campos de entrada (file_path, file_content)
  - Campos de saída (errors_found, warnings_found, critical_events, report)
  - Metadados e status (is_valid, error_message, metadata)

- [x] Implementar nós placeholders do StateGraph
  - validate_input_node
  - read_file_node
  - parse_events_node
  - analyze_patterns_node
  - interpret_with_llm_node
  - generate_report_node
  - error_handling_node

- [x] Criar StateGraph e conectar nós (agent.py)
  - Inicializar grafo com LogAnalysisState
  - Adicionar todos os nós
  - Definir ponto de entrada (validate_input)
  - Conectar nós em sequência linear
  - Compilar grafo

- [x] Implementar função get_initial_state()
  - Criar estado inicial com todos os campos
  - Validar tipos de dados

- [x] Escrever testes básicos (test_agent.py)
  - Testes de criação do Estado
  - Testes de retorno dos nós
  - Teste de compilação do grafo
  - Teste de execução end-to-end

### Artefatos Criados

- `src/loganalyzer/models.py` — TypedDict LogAnalysisState (11 campos)
- `src/loganalyzer/nodes.py` — 7 funções de nó (placeholders)
- `src/loganalyzer/agent.py` — StateGraph com 7 nós + END node
- `tests/test_agent.py` — 17 testes unitários de integração

### Implementação

**LogAnalysisState (models.py):**
```
Campos de entrada:
  - file_path: str
  - file_content: str

Campos de análise:
  - parsed_events: List[Dict]
  - errors_found: List[Dict]
  - warnings_found: List[Dict]
  - critical_events: List[Dict]

Saída:
  - analysis_result: Dict
  - report: str

Metadados:
  - metadata: Dict (version, agent_name, timestamps)
  - is_valid: bool
  - error_message: Optional[str]
```

**StateGraph (agent.py):**
```
Fluxo: validate_input → read_file → parse_events → analyze_patterns 
       → interpret_with_llm → generate_report → END

Tratamento de erro: error_handling → END (todas as etapas podem transicionar)
```

**Testes (test_agent.py):**
- TestStateModel: 2 testes
- TestNodeFunctions: 7 testes (1 por nó)
- TestAgentGraph: 4 testes (compilação, estado inicial)
- TestGraphIntegration: 2 testes (invocação end-to-end)

### Critérios de Aceição

- ✅ LogAnalysisState possui 11 campos com tipos corretos
- ✅ Todos os 7 nós retornam LogAnalysisState
- ✅ StateGraph compila sem erros
- ✅ Grafo pode ser invocado com invoke()
- ✅ Todos os testes passam (17/17)
- ✅ Code style: comentários PT, variáveis EN
- ✅ Docstrings descrevem propósito de cada nó

---

## Task #3: Implementar Lógica Real dos Nós

**Status:** Ready  
**Descrição:** Implementar lógica de validação, parsing e análise

### Subtarefas

- [ ] Implementar validate_input_node
  - Verificar se file_path existe
  - Validar permissões de leitura
  - Verificar se arquivo é legível
  - Definir is_valid = True/False

- [ ] Implementar read_file_node
  - Ler arquivo de log
  - Tratar exceções (FileNotFoundError, PermissionError)
  - Validar encoding (UTF-8)
  - Popularfile_content no estado

- [ ] Implementar parse_events_node
  - Fazer parsing de linhas do log
  - Suportar múltiplos formatos (JSON, texto, custom)
  - Extrair timestamp, severity, message
  - Popularparsed_events com estrutura: {timestamp, level, message, ...}

- [ ] Implementar analyze_patterns_node
  - Classificar eventos (ERROR, WARNING, INFO, DEBUG)
  - Identificar padrões recorrentes
  - Detectar eventos críticos
  - Popularparsed_events, errors_found, warnings_found, critical_events

- [ ] Criar ferramentas em tools/
  - validators.py: validações de arquivo
  - file_reader.py: leitura de arquivo (ferramenta obrigatória)

### Critérios de Aceição

- [ ] Nós implementam lógica real (não placeholders)
- [ ] Validações funcionam corretamente
- [ ] Ferramentas integradas aos nós
- [ ] Testes atualizado para lógica real
- [ ] Sem hardcodes ou simulações

---

## Task #4: Integrar Ferramentas e LLM

**Status:** Ready  
**Descrição:** Integrar ferramentas e LLM para análise inteligente

### Subtarefas

- [ ] Criar tools/
  - file_reader.py: ler arquivo (real tool)
  - parser.py: ferramenta de parsing de logs
  - detector.py: ferramenta de detecção de padrões
  - formatter.py: ferramenta de formatação de relatório

- [ ] Integrar ferramentas ao LangChain
  - Criar tool definitions com @tool decorator
  - Registrar no agent como tool set

- [ ] Implementar interpret_with_llm_node
  - Chamar LLM com contexto de análise
  - Gerar analysis_result estruturado
  - Adicionar recomendações baseadas em LLM

- [ ] Implementar generate_report_node
  - Usar formatter para estruturar saída
  - Criar markdown com resultados
  - Incluir resumo, métricas, recomendações

- [ ] Configurar LangChain + LLM
  - Integrar com modelo (ex: GPT-4, Claude)
  - Definir prompts em docs/prompts/
  - Testar chamadas ao LLM

### Critérios de Aceição

- [ ] Ferramentas reais (não simuladas)
- [ ] LLM integrado e funcionando
- [ ] Relatório estruturado e útil
- [ ] Sem chamadas forçadas ao LLM (apenas quando necessário)

---

## Task #5: Implementar Entrada/Saída e CLI

**Status:** Ready  
**Descrição:** Criar interface de entrada e saída para o agente

### Subtarefas

- [ ] Criar main.py
  - Receber argumento file_path via CLI
  - Chamar create_agent_graph()
  - Executar grafo com invoke()
  - Retornar resultado estruturado

- [ ] Implementar tratamento de erros
  - Capturar exceções durante execução
  - Retornar mensagens de erro úteis
  - Validar entrada antes de executar

- [ ] Criar exemplo de uso
  - examples/run_example.py
  - Demonstrar invocação do agente
  - Mostrar saída esperada

### Critérios de Aceição

- [ ] CLI funciona: `python -m loganalyzer /path/to/log.txt`
- [ ] Saída estruturada (markdown ou JSON)
- [ ] Tratamento de erros robusto

---

## Task #6: Documentação Completa

**Status:** Ready  
**Descrição:** Finalizar documentação do projeto

### Subtarefas

- [ ] Atualizar README.md
  - Instruções de instalação
  - Exemplos de uso
  - Estrutura do projeto

- [ ] Escrever ARCHITECTURE.md
  - Diagrama do StateGraph
  - Descrição de cada nó
  - Fluxo de dados

- [ ] Documentar prompts em docs/prompts.md
  - Prompts utilizados para LLM
  - Histórico de mudanças

- [ ] Criar exemplos em examples/
  - sample.log: arquivo de log de exemplo
  - sample_output.md: saída esperada

### Critérios de Aceição

- [ ] README completo com exemplos
- [ ] ARCHITECTURE.md descreve todos os componentes
- [ ] Exemplos funcionam conforme documentado

---

## Task #7: Testes Completos

**Status:** Ready  
**Descrição:** Completar cobertura de testes

### Subtarefas

- [ ] Testes de tools (test_tools.py)
  - Testar file_reader com arquivos válidos/inválidos
  - Testar parser com diferentes formatos de log
  - Testar detector de padrões
  - Testar formatter de relatório

- [ ] Testes de análise (test_analysis.py)
  - Testes de parse_events_node com logs reais
  - Testes de analyze_patterns_node
  - Validar outputs estruturados

- [ ] Testes end-to-end (test_agent.py)
  - Invocar grafo completo com log real
  - Validar report gerado
  - Testar tratamento de erros

- [ ] CI/CD (GitHub Actions)
  - Linter (pylint/flake8)
  - Testes (pytest)
  - Coverage report

### Critérios de Aceição

- [ ] Cobertura de testes > 80%
- [ ] Todos os tests passam
- [ ] CI/CD verde em cada commit

---

## Task #8: Finalização e Release

**Status:** Ready  
**Descrição:** Validação final e preparação para entrega

### Subtarefas

- [ ] Code review
  - Validar code style (PT comments, EN variables)
  - Verificar segurança (.env protegido)
  - Revisar arquitetura

- [ ] Testes em produção
  - Testar com logs reais
  - Validar performance
  - Testar edge cases

- [ ] Commits semânticos
  - Validar histórico de commits
  - Mensagens descritivas
  - Pequenos commits frequentes

- [ ] Entrega final
  - Garantir acesso público ao repo
  - Criar apresentação (2 slides)
  - Registrar link no AVA

### Critérios de Aceição

- [ ] Repositório público e acessível
- [ ] Todos os critérios de PROJECT_REQUIREMENTS.md atendidos
- [ ] Apresentação concluída
- [ ] Submissão no AVA

---

## Resumo do Progresso

| # | Tarefa | Status | Progresso |
|---|--------|--------|-----------|
| 1 | Configuração Inicial | ✅ Concluído | 100% |
| 2 | Arquitetura e Models | ✅ Concluído | 100% |
| 3 | Lógica dos Nós | 🔵 Ready | 0% |
| 4 | Ferramentas e LLM | 🔵 Ready | 0% |
| 5 | CLI e Entrada/Saída | 🔵 Ready | 0% |
| 6 | Documentação | 🔵 Ready | 0% |
| 7 | Testes Completos | 🔵 Ready | 0% |
| 8 | Finalização | 🔵 Ready | 0% |

**Total:** 2/8 tasks concluídas (25%)

---

## Dependências entre Tasks

```
Task 1 (Setup)
  ↓
Task 2 (Architecture) ← Requisito para todas as próximas
  ├→ Task 3 (Node Logic)
  │   ├→ Task 4 (Tools & LLM)
  │   │   ├→ Task 5 (CLI)
  │   │   ├→ Task 6 (Docs)
  │   │   └→ Task 7 (Tests)
  │   └→ Task 8 (Release)
```

---

## Próximos Passos

1. **Agora:** Task #2 (CONCLUÍDO)
2. **Próximo:** Task #3 - Implementar lógica real dos nós
3. **Depois:** Task #4 - Integrar ferramentas e LLM
4. **Sequência:** Tasks 5-8 seguem em paralelo quando possível
