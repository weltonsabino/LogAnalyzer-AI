Prompt: Implementar Task #28 - Corrigir LangGraph Error Handling com Arestas Condicionais
Responsável: Welton Sabino
Usuário: welton-sabino
Data/hora: 2026-08-20 14:00:00

## ⚠️ AVISO IMPORTANTE - OPERAÇÕES GIT

**NÃO FAÇA NENHUMA OPERAÇÃO GIT:**
- ❌ NÃO criar branches
- ❌ NÃO fazer commits
- ❌ NÃO fazer push
- ❌ NÃO fazer merge

**Todas as operações git serão feitas manualmente pelo desenvolvedor.**

Foco: Apenas implementação técnica (código + testes + documentação)

---

## Prompt original

Vamos implementar a Task #28: Corrigir LangGraph - Error Handling com Arestas Condicionais conforme especificado em `.kiro/specs/loganalyzer-ai/tasks_m2.2.md`

### Objetivo
Implementar arestas condicionais no StateGraph para redirecionar erros ao nó error_handling, resolvendo o feedback crítico do mini-projeto M2.1 (Feedback: LangGraph score 0.5 → esperado 1.0 após implementação)

### Contexto
- Mini-projeto M2.1: Score LangGraph 0.5/1.0 (error handling node existe mas não é acionado)
- Feedback do professor: "Adicionar arestas condicionais para redirecionar erros"
- Impacto: Bloqueador P0 (impossível prosseguir sem isso)
- Precedência: Vem após Task #27 (documentação estratégia)
- Próxima: Task #29 (Setup Kanban)

### Requisitos Funcionais

#### 1. Implementar 4 Funções de Roteamento em `src/loganalyzer/agent.py`

**Função 1: `route_after_validation()`**
```python
def route_after_validation(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se validação falhar.
    
    Retorno:
        "error_handling" se state.get("validation_error")
        "parse_events" caso contrário
    """
    # Verifica se há erro de validação
    if state.get("validation_error"):
        return "error_handling"
    return "parse_events"
```

**Função 2: `route_after_parsing()`**
```python
def route_after_parsing(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se parsing falhar.
    
    Retorno:
        "error_handling" se state.get("parsing_error")
        "detect_patterns" caso contrário
    """
    # Verifica se há erro de parsing
    if state.get("parsing_error"):
        return "error_handling"
    return "detect_patterns"
```

**Função 3: `route_after_detection()`**
```python
def route_after_detection(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se detecção falhar.
    
    Retorno:
        "error_handling" se state.get("detection_error")
        "analyze_ai" caso contrário
    """
    # Verifica se há erro de detecção
    if state.get("detection_error"):
        return "error_handling"
    return "analyze_ai"
```

**Função 4: `route_after_analysis()`**
```python
def route_after_analysis(state: LogAnalysisState) -> str:
    """
    Roteia para error_handling se análise IA falhar.
    
    Retorno:
        "error_handling" se state.get("analysis_error")
        "format_report" caso contrário
    """
    # Verifica se há erro de análise
    if state.get("analysis_error"):
        return "error_handling"
    return "format_report"
```

#### 2. Adicionar Arestas Condicionais ao Grafo em `src/loganalyzer/agent.py`

**No método `build_graph()`, após adicionar os nós:**

```python
# Arestas condicionais para redirecionar erros

# Aresta condicional após validação
graph.add_conditional_edges(
    "validate_input",
    route_after_validation,
    {
        "error_handling": "error_handling",
        "parse_events": "parse_events"
    }
)

# Aresta condicional após parsing
graph.add_conditional_edges(
    "parse_events",
    route_after_parsing,
    {
        "error_handling": "error_handling",
        "detect_patterns": "detect_patterns"
    }
)

# Aresta condicional após detecção
graph.add_conditional_edges(
    "detect_patterns",
    route_after_detection,
    {
        "error_handling": "error_handling",
        "analyze_ai": "analyze_ai"
    }
)

# Aresta condicional após análise
graph.add_conditional_edges(
    "analyze_ai",
    route_after_analysis,
    {
        "error_handling": "error_handling",
        "format_report": "format_report"
    }
)

# Aresta final do error_handling para END
graph.add_edge("error_handling", END)
```

#### 3. Atualizar Nodes para Setarem Flags de Erro em `src/loganalyzer/nodes.py`

**Modificar `validate_input_node()`:**
- Se ocorrer erro durante validação, setar `state["validation_error"] = str(error)`
- Continuação com estado inconsistente (não lançar exceção)
- Deixar error_handling processar

**Modificar `parse_events_node()`:**
- Se ocorrer erro durante parsing, setar `state["parsing_error"] = str(error)`
- Continuação com estado parcial

**Modificar `detect_patterns_node()`:**
- Se ocorrer erro durante detecção, setar `state["detection_error"] = str(error)`
- Continuação com detecção parcial

**Modificar `analyze_with_ai_node()`:**
- Se ocorrer erro durante chamada IA, setar `state["analysis_error"] = str(error)`
- Continuação sem análise IA (usar dados locais)

#### 4. Implementar 5+ Testes de Cenários de Erro em `tests/`

**Arquivo: `tests/test_error_handling.py`**

```python
import pytest
from src.loganalyzer.agent import build_agent
from src.loganalyzer.models import LogAnalysisState


class TestErrorHandling:
    """Testa error handling com arestas condicionais."""
    
    def test_validation_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando validação falha."""
        # Prepara estado com arquivo inválido
        state = LogAnalysisState(file_path="/arquivo/inexistente.log")
        
        # Executa agente
        agent = build_agent()
        result = agent.invoke(state)
        
        # Valida roteamento
        assert result.get("validation_error") is not None
        assert "error_summary" in result
    
    def test_parsing_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando parsing falha."""
        # Prepara arquivo com conteúdo inválido
        state = LogAnalysisState(
            file_path="tests/fixtures/invalid_format.log",
            file_content="Conteúdo inválido sem estrutura"
        )
        
        # Executa agente
        agent = build_agent()
        result = agent.invoke(state)
        
        # Valida roteamento
        assert result.get("parsing_error") is not None
    
    def test_detection_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando detecção falha."""
        # Prepara estado com parsed_events vazio
        state = LogAnalysisState(
            file_path="tests/fixtures/empty.log",
            file_content="",
            parsed_events=[]
        )
        
        # Executa agente
        agent = build_agent()
        result = agent.invoke(state)
        
        # Valida handling de vazio
        assert result.get("detection_error") or len(result.get("errors_found", [])) == 0
    
    def test_analysis_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando análise IA falha."""
        # Simula erro da IA (mock)
        state = LogAnalysisState(
            file_path="tests/fixtures/sample.log",
            file_content="LOG com erros",
            parsed_events=[{"level": "ERROR", "message": "Erro crítico"}],
            errors_found=[{"level": "ERROR", "count": 1}],
            warnings_found=[]
        )
        
        # Executa agente
        agent = build_agent()
        result = agent.invoke(state)
        
        # Valida se continua mesmo com erro IA
        assert "error_summary" in result or "report" in result
    
    def test_error_handler_generates_summary(self):
        """Testa se error_handler gera sumário de erro."""
        # Prepara estado com múltiplos erros
        state = LogAnalysisState(
            file_path="/inexistente",
            validation_error="Arquivo não encontrado"
        )
        
        # Executa agente
        agent = build_agent()
        result = agent.invoke(state)
        
        # Valida sumário
        assert "error_summary" in result
        assert result["error_summary"] is not None
        assert len(result["error_summary"]) > 0
```

#### 5. Atualizar Documentação

**A. Atualizar `ARCHITECTURE.md`:**
- Adicionar seção "Arestas Condicionais"
- Descrever 4 rotas condicionais
- Diagrama (ASCII art ou descrição) do fluxo de erro
- Exemplo de execução com erro

```markdown
## Arestas Condicionais (Roteamento Inteligente)

### Overview
O grafo utiliza arestas condicionais para redirecionar automaticamente para 
error_handling quando qualquer nó detecta uma falha.

### 4 Rotas Condicionais

1. **validate_input → error_handling|parse_events**
   - Condição: `state.get("validation_error")`
   - Acionado: Arquivo inválido, falta de permissão, encoding incorreto

2. **parse_events → error_handling|detect_patterns**
   - Condição: `state.get("parsing_error")`
   - Acionado: Formato de log não reconhecido, parsing falha

3. **detect_patterns → error_handling|analyze_ai**
   - Condição: `state.get("detection_error")`
   - Acionado: Sem padrões detectados, análise de padrão falha

4. **analyze_ai → error_handling|format_report**
   - Condição: `state.get("analysis_error")`
   - Acionado: Timeout IA, falha de API, resposta inválida

### Fluxo Normal vs Fluxo com Erro

```
Fluxo Normal:
validate_input → parse_events → detect_patterns → analyze_ai → format_report → END

Fluxo com Erro (exemplo: parsing falha):
validate_input → parse_events [ERROR] → error_handling → END
```
```

**B. Atualizar `README.md`:**
- Adicionar seção "Error Handling"
- Descrever comportamento com erros
- Exemplo de saída de erro

```markdown
## Error Handling

O agente implementa tratamento robusto de erros através de arestas condicionais.

### Cenários Cobertos

- **Validação:** Arquivo não existe, sem permissão, encoding inválido
- **Parsing:** Formato inválido, estrutura corrompida
- **Detecção:** Sem padrões, análise falha
- **IA:** Timeout, API indisponível, resposta inválida

### Resposta de Erro

```json
{
  "error_summary": "Descrição completa do erro",
  "error_type": "validation|parsing|detection|analysis",
  "recovery_suggestion": "Como resolver o problema"
}
```
```

### Pontos de Alteração

| Arquivo | Tipo | Mudança |
|---------|------|---------|
| `src/loganalyzer/agent.py` | Modificado | +4 funções de roteamento, +4 arestas condicionais |
| `src/loganalyzer/nodes.py` | Modificado | +5 modificações (setando flags de erro) |
| `tests/test_error_handling.py` | Novo | 5+ testes de cenários |
| `ARCHITECTURE.md` | Modificado | +Seção arestas condicionais |
| `README.md` | Modificado | +Seção error handling |

### Critérios de Aceição

- ✅ 4 funções de roteamento implementadas
- ✅ 4 arestas condicionais adicionadas ao grafo
- ✅ Todos os nós atualizam flags de erro
- ✅ 5+ testes passando (validação, parsing, detecção, análise, sumário)
- ✅ Código segue padrão (comentários PT, variáveis EN)
- ✅ ARCHITECTURE.md atualizado com arestas condicionais
- ✅ README.md atualizado com error handling
- ✅ Pylint ≥ 9.8/10 em agent.py + nodes.py
- ✅ Coverage ≥ 95% em error handling
- ✅ Nenhum erro de tipo (mypy)
- ✅ Score LangGraph sobe de 0.5 → 1.0 (esperado)

### Ordem de Execução

1. Implementar 4 funções de roteamento em `agent.py`
2. Adicionar 4 arestas condicionais ao grafo em `agent.py`
3. Modificar nós em `nodes.py` para setarem flags de erro
4. Criar `tests/test_error_handling.py` com 5+ testes
5. Atualizar `ARCHITECTURE.md` com seção arestas condicionais
6. Atualizar `README.md` com seção error handling
7. Executar testes: `pytest tests/test_error_handling.py -v`
8. Executar pylint: `pylint src/loganalyzer/agent.py src/loganalyzer/nodes.py`

### Importante

- Manter nomenclatura consistente (PT em comentários/docs, EN em código)
- Task crítica (P0 Bloqueador) — deve estar 100% completa antes de Task #29

### ⚠️ Atenção Final

Após implementar toda a Task #28 completa (incluindo testes, documentação e commits), você DEVERÁ atualizar o arquivo `.kiro/specs/loganalyzer-ai/tasks_m2.2.md` marcando:
- Task #28 como ✅ CONCLUÍDO
- Atualizando status, data de conclusão e referência de execução
- Adicionando subtarefas marcadas com [x]
- Verificando critérios de aceição

Isso garante rastreabilidade completa do projeto e conformidade com a regra "prompt-registration-mandatory".

