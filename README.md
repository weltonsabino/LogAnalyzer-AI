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
- **OpenAI GPT-4** para análise inteligente (opcional)
- **Pytest** para testes

---

## 📊 Apresentação

**[Clique aqui para visualizar a apresentação interativa](docs/Apresentacao/Apresentação_LogAnalyzer_ai.html)** 🎬

A apresentação contém 2 slides com:
- **Slide 1:** Problema e Solução — O gargalo tradicional vs. a resolução inteligente com agentes
- **Slide 2:** Arquitetura e Métricas — Diagrama do StateGraph interativo, nós funcionais e métricas de qualidade

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
- ✅ **85 testes passando** (+9 para multi-provider)
- ✅ **2 testes skipped** (placeholders)
- ✅ **Score Linter:** 9.75/10
- ✅ **Suporte Multi-Provider:** OpenAI + Groq

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

## 🏗️ Estrutura do Projeto

```
LogAnalyzer-AI/
├── src/loganalyzer/
│   ├── main.py              # CLI entrypoint
│   ├── agent.py             # StateGraph principal
│   ├── models.py            # Modelos (LogAnalysisState)
│   ├── nodes.py             # 7 nós do fluxo
│   ├── tools/
│   │   ├── validators.py    # Validação de entrada
│   │   ├── file_reader.py   # Leitura de arquivo
│   │   ├── parser.py        # Parsing de eventos
│   │   ├── detector.py      # Detecção de padrões
│   │   └── formatter.py     # Formatação de relatório
│   └── analysis/
│       ├── llm_interpreter.py  # Integração com IA
│       └── __init__.py
│
├── tests/
│   ├── test_agent.py                # Testes do agente
│   ├── test_tools.py                # Testes de ferramentas
│   ├── test_analysis.py             # Testes de análise
│   ├── test_task3_implementation.py # 17 testes (nodes)
│   └── test_task4_implementation.py # 13 testes (LLM/formatter)
│
├── docs/
│   ├── PROJECT_REQUIREMENTS.md      # Pré-requisitos
│   ├── ARCHITECTURE.md              # Design detalhado
│   ├── prompts.md                   # Prompts utilizados
│   └── prompts/                     # Histórico de prompts
│
├── examples/
│   ├── run_example.py               # Script de demonstração
│   ├── sample.log                   # Log de exemplo
│   └── sample_output.md             # Saída esperada
│
├── requirements.txt                 # Dependências
├── .env.example                     # Template de configuração
├── .gitignore                       # Arquivos ignorados
└── README.md                        # Este arquivo
```

---

## 🔐 Segurança

- ✅ **Credenciais:** Armazenadas em `.env` (não versionado)
- ✅ **`.gitignore`:** Configurado para proteger dados sensíveis
- ✅ **`.env.example`:** Sem valores reais, apenas template
- ✅ **Validações:** Implementadas em cada etapa
- ✅ **Encoding:** UTF-8 padrão com fallback

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
- **[Prompts Utilizados](docs/prompts.md)** — Histórico de decisões e prompts
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
- [x] Código do agente implementado (StateGraph com 7 nós)
- [x] Ferramenta integrada e funcional (read_file)
- [x] README.md completo
- [x] docs/ARCHITECTURE.md documentado
- [x] docs/prompts.md preenchido
- [x] examples/sample_output.md com saída real
- [x] 85 testes passando (100% de conformidade)
- [x] Commits semânticos (30+ commits)
- [x] Sem credenciais versionadas
- [x] Apresentação (2 slides interativos em HTML)

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
| Total de Nós | 7 |
| Total de Ferramentas | 5 |
| Provedores LLM | 2 (OpenAI + Groq) |
| Linhas de Código | ~2200 |
| Testes Unitários | 85 |
| Cobertura de Testes | ~95% |
| Score de Linter | 9.75/10 |

---

## 📞 Contato e Informações

- **Projeto:** LogAnalyzer AI
- **Disciplina:** IA para Desenvolvedores [T2]
- **Instituição:** SCTEC
- **Prazo:** 20/07/2026 às 22h
- **Avaliação:** 30% do módulo
- **Repositório:** [GitHub - weltonsabino/mini-projeto-LogAnalyzer-AI](https://github.com/weltonsabino/mini-projeto-LogAnalyzer-AI)

---

**Versão:** 1.0  
**Última atualização:** 14 de Julho, 2026  
**Status:** ✅ Completo e Funcional (Apresentação Incluída)
