Prompt: Integrar webhook no LangGraph + seguranca de secrets (Task #36 parte 2)
Responsavel: Welton Sabino
Usuario: welton-sabino
Data/hora: 2026-08-25 20:20:00

## Prompt original

Implementar **Task #36 (parte 2): Integracao do webhook como no final do LangGraph + seguranca de credenciais**.

Objetivo: Adicionar no `notify_webhook_node` ao StateGraph para que o webhook n8n seja chamado automaticamente ao final de cada execucao do agente. Garantir que ZERO credenciais, URLs ou tokens sensiveis existam em arquivos versionados. Toda configuracao sensivel vem de variaveis de ambiente (local via `.env`, CI via GitHub Secrets).

**IMPORTANTE: NAO fazer commit, NAO fazer push, NAO criar branches. Apenas implementar os arquivos e rodar testes localmente.**

---

## Descricao Detalhada

### O que fazer:

**1. Criar no `notify_webhook_node` no pipeline LangGraph**

- Adicionar funcao `notify_webhook_node(state)` em `src/loganalyzer/nodes.py`
- Logica:
  ```python
  # 1. Ler N8N_WEBHOOK_URL e N8N_WEBHOOK_ENABLED de os.getenv()
  # 2. Se nao configurado ou desabilitado → retornar state sem alterar (skip silencioso)
  # 3. Se configurado → instanciar WebhookIntegration e chamar send_report()
  # 4. Registrar resultado no state["metadata"]["webhook_status"]
  # 5. Emitir trace via _emit_trace()
  # 6. NUNCA crashar o pipeline — erros de webhook sao capturados e logados
  ```
- O no NAO deve alterar `is_valid` nem qualquer campo de analise
- Apenas adiciona metadata sobre o envio

**2. Registrar no no StateGraph (agent.py)**

- Adicionar no `notify_webhook` ao grafo
- Posicao: APOS `generate_report` (caminho de sucesso) e APOS `error_handling` (caminho de erro)
- Aresta: `notify_webhook` → `END`
- Ou seja: toda execucao (sucesso ou erro) termina passando pelo webhook

Fluxo atualizado:
```
[Sucesso]  generate_report → notify_webhook → END
[Erro]     error_handling  → notify_webhook → END
```

**3. Adicionar campo `webhook_status` ao modelo**

- Em `src/loganalyzer/models.py`, adicionar ao `LogAnalysisState`:
  ```python
  webhook_status: Optional[str]  # "sent", "skipped", "error"
  ```

**4. Garantir seguranca — Auditoria de fontes**

- Verificar que NENHUM arquivo versionado contem:
  - URLs reais de webhook (ex: `hook.make.com/xxx`, `xxx.app.n8n.cloud/webhook/xxx`)
  - API keys (ex: `sk-xxx`, `gsk_xxx`)
  - Senhas SMTP
  - Tokens de acesso
- `.env` ja esta no `.gitignore` (confirmar)
- `.env.example` tem APENAS placeholders
- `n8n_workflow.json` usa APENAS placeholders (`CONFIGURE_SEU_SMTP`, `seu-email@exemplo.com`)

**5. (Opcional) Adicionar step de scan de secrets no CI**

- Em `.github/workflows/lint.yml` ou novo workflow, adicionar step:
  ```yaml
  - name: Verificar vazamento de secrets
    run: |
      ! grep -rn "sk-[a-zA-Z0-9]" src/ tests/ examples/ || exit 1
      ! grep -rn "gsk_[a-zA-Z0-9]" src/ tests/ docs/ examples/ || exit 1
      ! grep -rn "hook\.make\.com" src/ tests/ docs/ examples/ || exit 1
      ! grep -rn "\.app\.n8n\.cloud" src/ tests/ docs/ examples/ || exit 1
  ```

**6. Testes**

- Adicionar testes em `tests/test_webhook_integration.py` (ou novo arquivo):
  - `test_notify_webhook_node_skips_when_disabled` — Sem env vars, no retorna state inalterado
  - `test_notify_webhook_node_sends_when_configured` — Com mock, webhook e chamado
  - `test_notify_webhook_node_error_does_not_crash` — Erro de conexao nao afeta pipeline
  - `test_notify_webhook_node_populates_metadata` — metadata["webhook_status"] preenchido

**IMPORTANTE:** Usar mock para `requests.post` e `os.getenv`. NAO fazer requests reais.

---

## Criterios de Aceite

- [ ] `notify_webhook_node` existe em `nodes.py`
- [ ] No registrado no StateGraph (agent.py) apos generate_report e error_handling
- [ ] Campo `webhook_status` adicionado ao modelo
- [ ] Webhook so dispara se N8N_WEBHOOK_URL e N8N_WEBHOOK_ENABLED configurados
- [ ] Se nao configurado → skip silencioso, sem erro
- [ ] Se erro de conexao → captura, nao crashar, loga em metadata
- [ ] Zero credenciais/URLs reais em arquivos versionados
- [ ] `.env` no `.gitignore`
- [ ] `.env.example` so com placeholders
- [ ] `n8n_workflow.json` sem dados sensiveis
- [ ] Testes novos passam com mock
- [ ] Todos os 218+ testes existentes continuam passando
- [ ] Codigo segue convencoes: comentarios PT, variaveis EN, docstrings PT
- [ ] Nenhum commit ou push realizado

---

## Restricoes

- **NAO** fazer `git commit`
- **NAO** fazer `git push`
- **NAO** criar branches
- **NAO** incluir URLs, tokens ou senhas reais em nenhum arquivo
- **NAO** fazer requests HTTP reais nos testes
- **NAO** quebrar testes existentes (o no deve ser transparente quando desabilitado)
- Apenas criar/modificar arquivos e validar que testes passam

---

## Arquivos modificados

```
src/loganalyzer/nodes.py          → +notify_webhook_node()
src/loganalyzer/agent.py          → +no e arestas para notify_webhook
src/loganalyzer/models.py         → +campo webhook_status
tests/test_webhook_integration.py → +4 testes do no
.github/workflows/lint.yml        → (opcional) step de scan de secrets
```

---

## Seguranca — Checklist Final

- [ ] `grep -rn "sk-" src/ tests/ examples/` → nenhum resultado
- [ ] `grep -rn "gsk_" src/ tests/ examples/` → nenhum resultado
- [ ] `grep -rn "hook.make.com" src/ tests/ docs/ examples/` → nenhum resultado
- [ ] `grep -rn ".app.n8n.cloud" src/ tests/ docs/ examples/` → nenhum resultado
- [ ] `grep -rn "smtp.gmail.com" src/ tests/ examples/` → nenhum resultado (so em docs como exemplo)
- [ ] `.env` esta no `.gitignore`
- [ ] Nenhum valor real de variavel sensivel hardcoded

---

## Pontuacao Esperada

+0.25 pontos (Criterio 7 do M2.2: Seguranca — sem credenciais no repositorio)
+0.25 pontos (Criterio 13: Low-code integration completa e integrada ao agente)
