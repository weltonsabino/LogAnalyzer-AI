# Saída Esperada do LogAnalyzer AI

Este documento demonstra a saída esperada quando o agente processa um arquivo de log com o exemplo fornecido (`sample_critical.log`).

## Entrada

**Arquivo:** `examples/sample_critical.log`  
**Tamanho:** 48 linhas  
**Tipo:** Log de aplicação com eventos INFO, WARNING, ERROR e CRITICAL

Amostra dos primeiros eventos:
```
2026-07-12 10:00:01 INFO Application started
2026-07-12 10:00:02 INFO Loading configuration
2026-07-12 10:00:03 WARNING Config file not found at /etc/app.conf
...
2026-07-12 10:08:02 ERROR Out of memory exception in request handler
...
```

## Saída

### Relatório em Markdown

```markdown
# Relatorio de Analise de Log
## LogAnalyzer AI
---
## Resumo Executivo
| Métrica | Quantidade |
|---------|-----------|
| Total de eventos | 47 |
| Erros encontrados | 11 |
| Avisos encontrados | 9 |
| Eventos críticos | 10 |

### Percentuais
- **Erros:** 23.4%
- **Avisos:** 19.1%
- **Críticos:** 21.3%

### Status Geral: CRITICA

## Eventos Criticos
Encontrados **10** evento(s) critico(s):

1. **Linha 8:** Database connection failed after 3 retries
   - Motivo: contém keyword crítica

2. **Linha 9:** Service initialization failed: database connection error
   - Motivo: contém keyword crítica

3. **Linha 37:** Out of memory exception in request handler
   - Motivo: contém keyword crítica

...

## Erros Identificados
Total: **11** erro(s)

- **(2x)** Connection timeout - retrying (1/3)
- **(2x)** Connection timeout - retrying (2/3)
- **(2x)** Database connection failed after 3 retries
- **(2x)** Service initialization failed: database connection error
- **(1x)** Connection timeout - retrying (3/3)
- ... e 2 padrão(ões) adicional(is) (2 erro(s))

## Avisos Encontrados
Total: **9** aviso(s)

- **(1x)** Config file not found at /etc/app.conf
- **(2x)** Attempting graceful shutdown
- **(1x)** Connection slow - latency 2500ms
- **(1x)** High memory usage: 87%
- **(1x)** High memory usage: 92%
- ... e 3 padrão(ões) adicional(is) (3 aviso(s))

## Insights e Recomendacoes

### Causas Raiz Identificadas
- Múltiplos erros podem indicar falha no componente central

### Insights da Análise
- Detectados 10 evento(s) crítico(s) que requerem atenção imediata
- Elevada quantidade de erros (11) sugere problema sistêmico

### Recomendações de Ação
1. Investigar eventos críticos imediatamente
2. Revisar padrões de erro e corrigir raiz do problema
3. Monitorar avisos e ajustar configurações se necessário
4. Implementar alertas para eventos críticos futuros

---

## Metadados de Execucao

**Agente:** LogAnalyzer AI  
**Versão:** 0.0.1  
**Data de Geração:** 2026-07-13T14:41:16.952194

### Timestamps de Processamento
- Arquivo lido: 2026-07-13T14:40:45.223944
- Parsing concluído: 2026-07-13T14:40:45.224949
- Análise concluída: 2026-07-13T14:40:45.225656

**Tamanho do arquivo:** 0.00 MB  
**Total de linhas:** 48
```

## Como Usar Este Exemplo

1. **Executar o script de exemplo:**
   ```bash
   python examples/run_example.py
   ```

2. **Ou usar via CLI:**
   ```bash
   python -m src.loganalyzer.main examples/sample_critical.log
   ```

3. **Salvar saída em arquivo:**
   ```bash
   python -m src.loganalyzer.main examples/sample_critical.log --output resultado.md
   ```

## Informações Adicionais

- **Tempo de Processamento:** ~2 segundos
- **Formato de Saída:** Markdown estruturado
- **Categorias de Severidade:** INFO, WARNING, ERROR, CRITICAL
- **Análise:** Automática com fallback quando LLM não está disponível
