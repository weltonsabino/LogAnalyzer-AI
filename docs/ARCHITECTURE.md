# Arquitetura do LogAnalyzer AI

## Visão Geral

LogAnalyzer AI é um agente baseado em LangGraph que automatiza a análise de arquivos de log.

## Componentes

### StateGraph
- Define o fluxo do agente
- Gerencia estado compartilhado

### Nós
- Validação de entrada
- Leitura de arquivo
- Análise de eventos
- Geração de relatório

### Ferramentas
- Leitura de arquivo de log
- Processamento de texto
- Formatação de saída

## Estado Compartilhado

```python
class LogAnalysisState(TypedDict):
    file_path: str
    file_content: str
    parsed_events: list
    analysis_result: dict
    report: str
```

## Fluxo de Execução

1. Entrada: caminho do arquivo
2. Validação do caminho
3. Leitura do arquivo (ferramenta)
4. Análise de eventos
5. Processamento com IA
6. Geração de relatório

---

**Status:** Em Desenvolvimento  
**Última atualização:** Junho 2026
