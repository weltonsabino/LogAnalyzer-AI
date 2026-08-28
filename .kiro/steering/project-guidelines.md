---
inclusion: always
---

# Diretrizes do Projeto LogAnalyzer AI

Este documento estabelece as diretrizes de implementação e referência para o desenvolvimento do **LogAnalyzer AI** — um agente de IA baseado em LangGraph para análise automatizada de arquivos de log.

**Leia primeiro:** `docs/PROJECT_REQUIREMENTS.md` para compreender pré-requisitos e critérios de avaliação.

---

## 1. Visão Geral do Projeto

**LogAnalyzer AI** é um agente que automatiza a análise de arquivos de log, identificando padrões importantes (erros, avisos, exceções) e gerando relatórios técnicos estruturados.

- **Objetivo:** Demonstrar uso de agentes LangGraph em caso real
- **Entrada:** Caminho de um arquivo de log
- **Saída:** Relatório técnico estruturado com análise e recomendações
- **Stack:** Python 3.10+, LangGraph, LangChain
- **Avaliação:** 30% do módulo IA para DEVs

---

## 2. Fluxo Esperado do Agente

```
1. Receber caminho do arquivo de log
   ↓
2. Validar a entrada
   ↓
3. Ler conteúdo do arquivo (ferramenta)
   ↓
4. Identificar eventos relevantes
   ↓
5. Interpretar com modelo de IA
   ↓
6. Gerar relatório estruturado
```

---

## 3. Componentes Obrigatórios

### 3.1 StateGraph (LangGraph)
- Estado compartilhado para armazenar informações da execução
- Nós responsáveis pelas etapas principais
- Conexões entre nós definindo fluxo

### 3.2 Ferramentas Integradas
**Mínimo:** 1 ferramenta real
- Leitura de arquivo (obrigatória para LogAnalyzer)
- Processamento/análise de texto
- Geração de relatório estruturado

### 3.3 Contexto e Memória
- Estado deve manter histórico de análise
- Contexto disponível durante execução
- Informações relevantes não descartadas

### 3.4 Validações
- Entrada: arquivo existe? É legível?
- Processamento: dados válidos?
- Saída: relatório estruturado e correto?

### 3.5 Resposta Final
- Estruturada e não simulada
- Contém análise real do agente
- Útil para usuário final

---

## 4. Estrutura de Pacotes Recomendada

```
src/loganalyzer/
├── __init__.py
├── main.py                    # Entrypoint
├── agent.py                   # StateGraph principal
├── models.py                  # Modelos (State, etc)
├── nodes.py                   # Funções dos nós
├── tools/
│   ├── __init__.py
│   └── file_reader.py         # Tool: ler arquivo
├── analysis/
│   ├── __init__.py
│   ├── parser.py              # Parser de logs
│   ├── detector.py            # Detector de padrões
│   └── formatter.py           # Formatador de relatório
└── utils/
    ├── __init__.py
    └── validators.py          # Validações

tests/
├── __init__.py
├── test_agent.py
├── test_tools.py
└── test_analysis.py

docs/
├── PROJECT_REQUIREMENTS.md    # Pré-requisitos (este)
├── ARCHITECTURE.md            # Design do agente
├── prompts.md                 # Prompts utilizados
└── examples/
    ├── sample_critical.log     # Log de exemplo (severidade alta)
    └── sample_output.md       # Saída esperada

examples/
└── run_example.py             # Script de demonstração

.github/workflows/
├── lint.yml
├── tests.yml
└── build.yml
```

---

## 5. Padrões de Código Python

### Imports
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
```

### State Definition (TypedDict)
```python
class LogAnalysisState(TypedDict):
    file_path: str
    file_content: str
    parsed_events: list
    errors_found: list
    warnings_found: list
    analysis_result: dict
    report: str
```

### Node Function Pattern
```python
def process_node(state: LogAnalysisState) -> LogAnalysisState:
    # 1. Validar entrada
    if not state.get("required_field"):
        raise ValueError("Missing required field")
    
    # 2. Processar
    result = do_something(state)
    
    # 3. Atualizar estado
    state["output_field"] = result
    return state
```

### Tool Definition
```python
def read_log_file(file_path: str) -> str:
    """Read log file and return content."""
    # Validações
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Implementação
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

## 6. Critérios de Sucesso

### 1. Versionamento (1 ponto)
- ✅ Commits claros e incrementais
- ✅ Padrão semântico (feat:, fix:, docs:, etc)
- ✅ Branches nomeadas significativamente
- ✅ Histórico rastreável

### 2. Contribuição Individual (1 ponto)
- ✅ Commits frequentes com sua autoria
- ✅ Implementação clara de funcionalidades
- ✅ Documentação ou melhorias
- ✅ Revisão de código (em grupos)

### 3. Organização e Documentação (2 pontos)
- ✅ README.md completo
- ✅ Arquivo prompts.md
- ✅ Exemplos de entrada/saída
- ✅ Código bem estruturado

### 4. Ideia e Apresentação (1 ponto)
- ✅ Até 2 slides
- ✅ Problema + Solução + Fluxo
- ✅ Claro e objetivo

### 5. Implementação LangGraph (1 ponto)
- ✅ StateGraph definido
- ✅ Nós com responsabilidades claras
- ✅ Conexões entre etapas

### 6. Ferramenta Integrada (1 ponto)
- ✅ Ferramenta real (não simulada)
- ✅ Integrada ao fluxo
- ✅ Ação concreta (ler, escrever, processar)

### 7. Segurança (1 ponto)
- ✅ Sem credenciais no repositório
- ✅ .gitignore configurado
- ✅ .env.example sem valores reais

### 8. Contexto e Memória (2 pontos)
- ✅ Estado compartilhado funcional
- ✅ Validações básicas implementadas
- ✅ Saída estruturada

---

## 7. Checklist de Implementação

### Fase 1: Configuração (Semana 1)
- [ ] Repositório GitHub criado e acessível
- [ ] Estrutura de pastas criada
- [ ] requirements.txt com dependências
- [ ] .gitignore adequado
- [ ] README.md com estrutura básica

### Fase 2: Arquitetura (Semana 2)
- [ ] StateGraph definido
- [ ] Modelos (TypedDict) criados
- [ ] Nós principais planejados
- [ ] Ferramentas definidas
- [ ] ARCHITECTURE.md documentado

### Fase 3: Implementação (Semana 3-4)
- [ ] Nós implementados
- [ ] Ferramenta integrada
- [ ] Validações funcionando
- [ ] Testes básicos passando
- [ ] Exemplos funcionais

### Fase 4: Documentação (Semana 4)
- [ ] README.md completo
- [ ] prompts.md preenchido
- [ ] Exemplos de entrada/saída
- [ ] Apresentação (2 slides)
- [ ] Commits semânticos finalizados

---

## 8. Boas Práticas

✅ **Faça:**
- Commits pequenos e frequentes
- Mensagens descritivas em commits
- Testes básicos para funcionalidades
- Documentação simultânea ao código
- Use type hints em Python
- Validação sempre antes de processar

❌ **Não Faça:**
- Commits únicos "mega commits"
- Mensagens vagas ("fix", "update")
- Código sem testes
- Documentação faltante
- Credenciais no repositório
- Ignorar erros

---

## 9. Segurança Obrigatória

### API Keys e Credenciais
```bash
# ✅ Correto: variável de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ Errado: hardcoded
OPENAI_API_KEY = "sk-abc123..."
```

### .env.example
```env
# ✅ Correto: sem valores reais
OPENAI_API_KEY=your_key_here
LOG_FILE_PATH=/path/to/logs

# ❌ Errado: valores reais
OPENAI_API_KEY=sk-abc123xyz789
LOG_FILE_PATH=/home/user/project/logs
```

### .gitignore
```
__pycache__/
*.pyc
.env
*.log
venv/
.pytest_cache/
```

---

## 10. Exemplos de Prompts a Documentar

Em `docs/prompts.md`, registre:

1. **Prompt de Planejamento**
   - Como planejou a arquitetura
   - Decisões tomadas

2. **Prompt de Implementação**
   - Exemplos de geradores de código
   - Ajustes realizados

3. **Prompt de Correção**
   - Bugs encontrados
   - Como foram resolvidos

4. **Prompt de Melhoria**
   - Sugestões de otimização
   - Refatorações aplicadas

---

## 11. Referência Rápida

| Aspecto | Detalhe |
|---------|---------|
| **Framework** | LangGraph (StateGraph) |
| **Linguagem** | Python 3.10+ |
| **Dependências** | langgraph, langchain, python-dotenv |
| **Testes** | pytest |
| **Linter** | pylint ou flake8 |
| **Formatter** | black |
| **Versionamento** | git com commits semânticos |
| **Acesso** | GitHub público |
| **Prazo** | 20/07/2026 às 22h |
| **Entrega** | Link no AVA |

---

## 12. Links Importantes

- **Requisitos Completos:** `docs/PROJECT_REQUIREMENTS.md`
- **Critérios de Avaliação:** Seção 12 de PROJECT_REQUIREMENTS.md
- **Checklist Final:** Seção 14 de PROJECT_REQUIREMENTS.md

---

**Última atualização:** Junho 2026  
**Propósito:** Guia de implementação do LogAnalyzer AI  
**Próximo:** Consultar PROJECT_REQUIREMENTS.md para detalhes específicos
