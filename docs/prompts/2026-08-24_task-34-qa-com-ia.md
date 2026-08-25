Prompt: Implementar Task #34 - QA com IA (Code Review + Testes E2E)
Responsável: Welton Sabino
Usuário: welton-sabino
Data/hora: 2026-08-24 19:09:00

## Prompt Original

Implementar **Task #34: QA com IA - Code Review + E2E Gerados**.

Objetivo: Usar modelos de IA para análise estática de código, sugestões de otimização e geração automática de testes E2E (end-to-end) baseados em cobertura de gaps.

---

## 📋 Descrição Detalhada

### O que fazer:

**1. Documentação de Code Review com IA**
- Criar arquivo `docs/qa/code_review_with_ai.md` (~200 linhas)
- Seções obrigatórias:
  - Metodologia de análise com IA (prompt engineering)
  - Checklist de 15+ critérios de revisão
  - Exemplo de análise completa de 1 arquivo
  - Artefatos analisados (src/, tests/, docs/)
  - Riscos identificados e soluções
  - Métricas de qualidade (Pylint, coverage, testes)
  - Integração com CI/CD

**2. Testes E2E Gerados por IA**
- Criar arquivo `tests/test_e2e_generated_by_ai.py` (~300 linhas)
- Mínimo 8 testes E2E que cobrem:
  - Cenário sucesso: arquivo normal, análise completa, relatório correto
  - Cenário erro validação: arquivo inválido, error_handling acionado
  - Cenário timeout: arquivo grande, timeout dispara corretamente
  - Cenário retry: falha transiente, retry tem sucesso
  - Cenário observabilidade: execution_id propagado, traces registrados
  - Cenário segurança: input injection bloqueado
  - Cenário autonomia: ação bloqueada por governo, mensagem clara
  - Cenário multi-provider: OpenAI e Groq funcionam

**3. Priorização por Risco**
- Criar arquivo `docs/qa/risk_prioritization.md` (~150 linhas)
- Seções:
  - Matriz de risco (probabilidade × impacto) para cada módulo
  - Testes críticos (P0) que cobrem 80% dos riscos
  - Testes auxiliares (P1) para edge cases
  - Testes exploratórios (P2) para descobrir novos cenários

**4. Integração com README**
- Adicionar seção "🤖 QA com IA" no README.md (~80 linhas)
- Conteúdo:
  - Explicação da estratégia de QA
  - Como usar code review com IA
  - Exemplo de rodar testes E2E
  - Comando para executar tudo: `pytest tests/test_e2e_generated_by_ai.py -v`
  - Link para documentação detalhada

---

## 🎯 Critérios de Aceição

- ✅ Arquivo `docs/qa/code_review_with_ai.md` criado (200+ linhas)
- ✅ Arquivo `docs/qa/risk_prioritization.md` criado (150+ linhas)
- ✅ Arquivo `tests/test_e2e_generated_by_ai.py` criado com 8+ testes
- ✅ Todos os 8 cenários E2E cobertos
- ✅ Testes passam sem erros
- ✅ Coverage não diminui (≥95%)
- ✅ README.md atualizado com seção QA
- ✅ Sem regressão (testes existentes continuam passando)
- ✅ Pylint score mantém ≥9.8/10

---

## 📁 Arquivos a Criar/Modificar

**CRIAR:**
- `docs/qa/code_review_with_ai.md` (200+ linhas)
- `docs/qa/risk_prioritization.md` (150+ linhas)
- `tests/test_e2e_generated_by_ai.py` (8+ testes)

**MODIFICAR:**
- `README.md` (adicionar seção "🤖 QA com IA")

---

## 🧪 Cenários E2E Obrigatórios

### Cenário 1: Sucesso End-to-End
- Input: Arquivo de log válido (`examples/sample.log`)
- Fluxo: Validação → Leitura → Parsing → Análise → Relatório
- Output: Relatório markdown correto com eventos, análise IA, recomendações
- Asserções:
  - `state["is_valid"] == True`
  - `len(state["parsed_events"]) > 0`
  - `len(state["report"]) > 500`
  - `state["severity_routes"] is not None`

### Cenário 2: Erro de Validação
- Input: Caminho inválido ou arquivo que não existe
- Fluxo: `validate_input` falha → `route_after_validation` redireciona → `error_handling`
- Output: Estado com `is_valid=False`, `validation_error` preenchido
- Asserções:
  - `state["is_valid"] == False`
  - `state["validation_error"] is not None`
  - `state["error_message"] is not None`

### Cenário 3: Timeout em Leitura
- Input: Arquivo simulado (ou grande)
- Fluxo: `read_log_file` com `@with_timeout(30)` simula timeout
- Output: Estado com erro de timeout
- Asserções:
  - `state["is_valid"] == False`
  - `"timeout" in state["parsing_error"].lower()` ou erro apropriado

### Cenário 4: Retry Bem-Sucedido
- Input: Arquivo com permissão temporária (simular)
- Fluxo: Primeira tentativa falha, retry sucede
- Output: Análise completa
- Asserções:
  - `state["is_valid"] == True`
  - Verificar logs que mostram retry ocorreu

### Cenário 5: Observabilidade
- Input: Arquivo normal
- Fluxo: Execução com TraceCollector ativo
- Output: execution_id propagado, traces registrados, summary disponível
- Asserções:
  - `state["execution_id"] is not None`
  - `len(state["trace_collector"].get_traces()) > 0`
  - `summary["trace_count"] > 0`
  - `summary["status"] in ["OK", "WARNING"]` (sem erro)

### Cenário 6: Segurança - Input Injection
- Input: Caminho com caracteres maliciosos (`../../../etc/passwd`)
- Fluxo: `InputValidator` bloqueia, `governance` nega acesso
- Output: Estado com `is_valid=False`, mensagem de segurança
- Asserções:
  - `state["is_valid"] == False`
  - `"unauthorized" in state["error_message"].lower() or "denied" in state["error_message"].lower()`

### Cenário 7: Autonomia - Ação Bloqueada
- Input: Arquivo normal, autonomy_level=READ_ONLY
- Fluxo: Governança permite READ mas nega ANALYZE
- Output: Estado interrompido com mensagem de aprovação necessária
- Asserções:
  - `state["is_valid"] == False` (ou bloqueado em algum nó)
  - Mensagem indica que ação requer aprovação

### Cenário 8: Multi-Provider (OpenAI + Groq)
- Input: Arquivo de log
- Fluxo: Executar com `--provider openai` e depois com `--provider groq`
- Output: Ambos produzem análise válida (podem variar em conteúdo)
- Asserções:
  - `state["is_valid"] == True` em ambos os casos
  - `len(state["report"]) > 0` em ambos os casos
  - `state["analysis_result"] is not None`

---

## 📊 Estrutura do Teste E2E

```python
class TestE2ESuccessScenarios:
    """Testa cenários de sucesso end-to-end."""
    
    def test_e2e_success_normal_log(self):
        """Teste cenário 1: Sucesso completo."""
        # Setup
        # Execute
        # Assert
    
    # ... mais testes ...

class TestE2EErrorHandling:
    """Testa tratamento de erros end-to-end."""
    
    def test_e2e_validation_error(self):
        """Teste cenário 2: Erro de validação."""
        # ...

class TestE2EResilience:
    """Testa resiliência (timeout, retry)."""
    
    def test_e2e_timeout_scenario(self):
        """Teste cenário 3: Timeout."""
        # ...
    
    def test_e2e_retry_scenario(self):
        """Teste cenário 4: Retry bem-sucedido."""
        # ...

class TestE2EObservability:
    """Testa observabilidade."""
    
    def test_e2e_observability(self):
        """Teste cenário 5: Observabilidade."""
        # ...

class TestE2ESecurity:
    """Testa segurança."""
    
    def test_e2e_input_injection_blocked(self):
        """Teste cenário 6: Input injection."""
        # ...

class TestE2EGovernance:
    """Testa governança e autonomia."""
    
    def test_e2e_autonomy_blocked(self):
        """Teste cenário 7: Autonomia bloqueada."""
        # ...

class TestE2EMultiProvider:
    """Testa suporte a múltiplos provedores."""
    
    def test_e2e_openai_and_groq(self):
        """Teste cenário 8: Multi-provider."""
        # ...
```

---

## 📝 Estrutura de `code_review_with_ai.md`

```markdown
# Code Review com IA — LogAnalyzer AI

## 1. Metodologia
- Análise automática com Pylint + Flake8
- Análise com IA para legibilidade + design
- Checklist de 15+ critérios
- Exemplo prático

## 2. Checklist de Revisão (15+ critérios)
1. Type hints completos?
2. Docstrings em português?
3. Testes >95% coverage?
4. Pylint ≥9.8/10?
5. Sem credenciais hardcoded?
6. Sem circular imports?
7. Nomes de variáveis descritivos?
... (mais 8)

## 3. Exemplo de Análise Completa
- Arquivo analisado: `observability.py`
- Scores: Type hints 10/10, Docstrings 10/10, ...
- Sugestões de melhoria (com justificativa)
- Decisões tomadas

## 4. Resultados da Análise
- Arquivos analisados: 35
- Problemas encontrados: 0 críticos, 2 menores
- Recomendações implementadas: 18

## 5. Integração CI/CD
- GitHub Actions: Rodar análise em cada PR
- Faixa de aprovação: Pylint ≥9.8/10
```

---

## 🧮 Checklist de Implementação

### Antes de Começar
- [ ] Ler Task #34 em `.kiro/specs/loganalyzer-ai/tasks_m2.2.md`
- [ ] Verificar arquivos E2E em outros projetos para padrão
- [ ] Listar todos os arquivos a criar/modificar

### Fase 1: Documentação QA
- [ ] Criar diretório `docs/qa/`
- [ ] Criar `code_review_with_ai.md` com 15+ critérios de revisão
- [ ] Criar `risk_prioritization.md` com matriz de riscos
- [ ] Validar links e formatação markdown

### Fase 2: Testes E2E
- [ ] Criar `tests/test_e2e_generated_by_ai.py`
- [ ] Implementar 8 testes (1 por cenário)
- [ ] Rodar testes localmente: `pytest tests/test_e2e_generated_by_ai.py -v`
- [ ] Verificar se todos passam

### Fase 3: Integração
- [ ] Atualizar README.md com seção "🤖 QA com IA"
- [ ] Validar links para documentação
- [ ] Verificar exemplo de execução

### Fase 4: Validação
- [ ] Rodar todos os testes: `pytest tests/ -q`
- [ ] Verificar Pylint: `pylint src/ --score=yes`
- [ ] Confirmar coverage: `pytest --cov=src`
- [ ] Sem regressão (112+ testes passando)

---

## ⏱️ Estimativa

- **Documentação QA:** 45min
- **Testes E2E:** 1h
- **Integração README:** 15min
- **Validação:** 30min
- **TOTAL:** ~2h

---

## ⚠️ Observações Importantes

### 1. NÃO fazer commits ou branches
- Apenas escrever código
- Operações git são manuais

### 2. Testes E2E devem ser reais
- Usar arquivos reais do projeto (examples/sample.log)
- Usar fixtures quando necessário
- Não fazer mocks de nó inteiro

### 3. Coverage deve aumentar
- Novos 8 testes = +~50 linhas de cobertura
- Coverage final deve ser ≥95%

### 4. Pylint score não pode cair
- Score atual: ~9.8/10
- Novos arquivos: target ≥9.8/10

---

## ✨ Próxima Task

**Task #35: DevOps Inteligente + Anomalias**
- Criar `src/loganalyzer/devops/anomaly_detector.py`
- Implementar detecção de anomalias em logs
- Criar testes adicionais
- Documentar em README

---

## 📚 Referências

- **Task #34 Spec:** `.kiro/specs/loganalyzer-ai/tasks_m2.2.md` (linhas ~430-460)
- **Tasks anteriores:** `docs/prompts/` (18 prompts)
- **Padrão de testes:** `tests/test_*.py` (observar estrutura)
- **README:** `README.md` (seções existentes para entender padrão)

---

**Importante:** Este prompt é estrutural. Nenhuma implementação foi realizada ainda. Aguardando execução.
