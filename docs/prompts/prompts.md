# Prompts Utilizados no LogAnalyzer AI

Este documento registra os principais prompts utilizados para planejar, implementar, corrigir e melhorar o agente LogAnalyzer AI, bem como os prompts utilizados pelo LLM para análise de logs.

---

## Prompts de Planejamento

### Prompt 1: Definição da Arquitetura (Início do Projeto)
**Data:** Julho 2026  
**Objetivo:** Definir estrutura e componentes principais do agente

```
Preciso de um agente baseado em LangGraph para análise automatizada de logs.
O agente deve:

1. Receber caminho de um arquivo de log como entrada
2. Validar a entrada (arquivo existe? É legível?)
3. Ler conteúdo do arquivo
4. Identificar eventos relevantes (erros, avisos, exceções)
5. Interpretar com modelo de IA (GPT-4)
6. Gerar relatório técnico estruturado em markdown

Implementação esperada:
- StateGraph com 7 nós principais
- Estado compartilhado com 11 campos
- Ferramentas integradas (leitura, parsing, formatação)
- Validações em cada etapa
- Contexto mantido durante execução
```

**Decisões Tomadas:**
- ✅ Uso de StateGraph com 7 nós (validação, leitura, parsing, análise, LLM, relatório, erro)
- ✅ LogAnalysisState com 11 campos tipados
- ✅ Separação em módulos: tools/, analysis/, nodes.py
- ✅ TypedDict para state com type hints

---

## Prompts de Implementação

### Prompt 2: Implementar Modelos e Arquitetura (Task #2)
**Data:** Julho 2026  
**Objetivo:** Criar modelos base e StateGraph

```
Implemente:
1. LogAnalysisState (TypedDict) com 11 campos
2. StateGraph com 7 nós (placeholders)
3. Conexões entre nós (caminho feliz)
4. Função get_initial_state()
5. Testes básicos (15 testes)

Campos do State:
- file_path, file_content
- parsed_events, errors_found, warnings_found, critical_events
- analysis_result, report
- metadata, is_valid, error_message
```

**Resultado:** ✅ Task #2 completa com 15 testes passando

### Prompt 3: Implementar Lógica Real dos Nós (Task #3)
**Data:** Julho 2026  
**Objetivo:** Implementar validação, leitura, parsing, detecção de padrões

```
Implemente a lógica real dos nós:

1. validate_input_node: validar arquivo (usar validators.py)
2. read_file_node: ler conteúdo (usar file_reader.py)
3. parse_events_node: extrair eventos (usar parser.py)
4. analyze_patterns_node: detectar padrões (usar detector.py)

Crie ferramentas em tools/:
- validators.py: validate_file_path(), validate_events()
- file_reader.py: read_log_file()
- parser.py: parse_log_events()
- detector.py: detect_patterns(), find_critical_patterns()

Padrões esperados: INFO, WARNING, ERROR, CRITICAL
```

**Resultado:** ✅ Task #3 completa com 17 testes passando

### Prompt 4: Integrar LLM e Ferramentas (Task #4)
**Data:** Julho 2026  
**Objetivo:** Integrar GPT-4 com fallback automático

```
Implemente:
1. formatter.py: função format_report() que gera markdown estruturado
2. llm_interpreter.py: integração com OpenAI GPT-4 Turbo
3. interpret_with_llm_node: analisa eventos com LLM
4. generate_report_node: formata relatório final

Features:
- Fallback automático quando LLM não disponível
- Análise heurística como alternativa
- Parsing robusto de JSON do LLM
- Relatório com: resumo, eventos críticos, erros, avisos, recomendações

Prompt para LLM:
"Analise os seguintes eventos de log críticos e forneça insights..."
```

**Resultado:** ✅ Task #4 completa com 13 testes passando

### Prompt 5: CLI e Interface (Task #5)
**Data:** Julho 2026  
**Objetivo:** Criar interface CLI para uso do agente

```
Implemente:
1. main.py: CLI com argumentos (--output, --json, --verbose)
2. run_example.py: script de demonstração
3. sample.log: arquivo com 47 linhas de eventos reais

CLI esperada:
python -m src.loganalyzer.main arquivo.log --output relatorio.md
python -m src.loganalyzer.main arquivo.log --json
python -m src.loganalyzer.main arquivo.log --verbose
```

**Resultado:** ✅ Task #5 completa com 3 artefatos

---

## Prompts do LLM para Análise de Logs

### Template: Análise de Eventos Críticos
**Localização:** `src/loganalyzer/analysis/llm_interpreter.py`

```
Você é um especialista em análise de logs de aplicações.

Analise os seguintes eventos críticos extraídos de um arquivo de log e forneça:

1. **Resumo dos Problemas Principais:**
   - Quais são os principais problemas identificados?
   - Qual é a severidade de cada um?

2. **Análise de Padrões:**
   - Quais padrões de erro se repetem?
   - Há correlações entre os eventos?

3. **Causas Raiz Prováveis:**
   - Quais são as causas raiz mais prováveis?
   - Como cada causa afeta o sistema?

4. **Recomendações de Ação:**
   - Quais ações devem ser tomadas imediatamente?
   - Quais ajustes podem prevenir estes problemas?

5. **Priorização:**
   - Como você priorizaria os problemas para correção?

Eventos Críticos:
{críticos}

Forneça resposta em JSON estruturado com campos:
- summary (resumo)
- root_causes (lista de causas)
- patterns (padrões identificados)
- recommendations (recomendações)
- priority_order (priorização)
```

### Ajustes de Temperature e Parâmetros
- **Temperature:** 0.7 (criativo mas determinístico)
- **Max Tokens:** 1000
- **Model:** GPT-4 Turbo
- **Timeout:** 30 segundos

---

## Prompts de Correção

### Prompt 6: Ajuste de Parsing (Correção)
**Data:** Julho 2026  
**Issue:** Parsing não reconhecia formatos variados

```
O parser atual falha em logs que não seguem TIMESTAMP LEVEL MESSAGE.
Implemente suporte para:
1. Logs sem timestamp
2. Logs JSON
3. Logs com espaçamento variável
4. Logs com campos customizados

Mantenha retrocompatibilidade com formato atual.
```

**Resultado:** ✅ Parser suporta múltiplos formatos

### Prompt 7: Integração de Ferramentas (Correção)
**Data:** Julho 2026  
**Issue:** Ferramentas não eram chamadas pelos nós

```
Integre as ferramentas aos nós:
- read_file_node deve chamar read_log_file()
- parse_events_node deve chamar parse_log_events()
- analyze_patterns_node deve chamar detect_patterns()
- generate_report_node deve chamar format_report()

Mantenha estado atualizado em cada etapa.
```

**Resultado:** ✅ Todas as ferramentas integradas

---

## Prompts de Melhoria

### Prompt 8: Fallback Automático (Melhoria)
**Data:** Julho 2026  
**Objetivo:** Funcionar sem OpenAI API

```
Implemente fallback automático para análise heurística quando:
1. OPENAI_API_KEY não está definida
2. Chamada à API falha
3. Timeout na conexão

Análise heurística deve:
- Identificar erros/avisos por keywords
- Detectar padrões recorrentes
- Gerar recomendações genéricas mas úteis
- Nunca falhar (degradação graciosa)
```

**Resultado:** ✅ Fallback implementado e testado

### Prompt 9: Validações Robustas (Melhoria)
**Data:** Julho 2026  
**Objetivo:** Melhorar tratamento de erros

```
Implemente validações robustas:
1. Arquivo existe e é legível?
2. Conteúdo é válido?
3. Parsing extrai eventos?
4. Estado é consistente?

Cada erro deve ser capturado e registrado.
```

**Resultado:** ✅ Validações em todos os nós

---

## Documentação dos Prompts

### Registro de Prompts Utilizados
Todos os prompts que resultaram em implementação de código são registrados em:
- `docs/prompts/` → Histórico por data e responsável
- `docs/prompts.md` → Este arquivo

### Exemplo de Arquivo de Prompt Registrado
```
docs/prompts/2026-07-12_03-04-34_welton-sabino.md

Prompt: [resumo até 100 chars]
Responsável: [nome completo]
Usuário: [identificador]
Data/hora: [YYYY-MM-DD HH:MM:SS]

## Prompt original
[Conteúdo completo]
```

---

## Sumário de Prompts por Fase

| Fase | Prompts | Resultado |
|------|---------|-----------|
| **Planejamento** | 1 | ✅ Arquitetura definida |
| **Implementação** | 5 | ✅ 5 tasks implementadas |
| **Correção** | 2 | ✅ Issues resolvidas |
| **Melhoria** | 2 | ✅ Features adicionadas |
| **Total** | 10+ | ✅ Projeto completo |

---

## Referências

- **LLM Interpreter:** `src/loganalyzer/analysis/llm_interpreter.py`
- **Nodes:** `src/loganalyzer/nodes.py`
- **Formatter:** `src/loganalyzer/tools/formatter.py`
- **Histórico:** `docs/prompts/` (arquivos datados)

---

**Status:** ✅ Documentação Completa  
**Última atualização:** 13 de Julho, 2026  
**Versão:** 1.0
