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
│       LogAnalysisState com 11 campos    │
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

## Limitações Conhecidas

1. **Parsing:** Suporta principalmente formatos baseados em texto
2. **LLM:** Limitado ao GPT-4 Turbo da OpenAI
3. **Performance:** Logs > 10MB podem ter latência
4. **Formatos:** JSON logs requerem format específico

---

## Extensões Futuras

1. Suporte a múltiplos provedores LLM
2. Processamento de logs em stream
3. Integração com sistemas de alertas
4. Visualizações gráficas de dados
5. Histórico de análises persistidas

---

## Referências

- **LangGraph:** https://python.langchain.com/docs/langgraph/
- **OpenAI API:** https://platform.openai.com/docs/
- **Exemplo de Saída:** `examples/sample_output.md`
- **Prompts Utilizados:** `docs/prompts/`

---

**Status:** ✅ Implementado e Funcional  
**Última atualização:** 13 de Julho, 2026  
**Versão:** 1.0
