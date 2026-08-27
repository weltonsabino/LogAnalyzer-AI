Prompt: Implementar Task #36 - Low-Code Integration (n8n Webhook)
Responsavel: Welton Sabino
Usuario: welton-sabino
Data/hora: 2026-08-24 21:51:00

## Prompt original

Implementar **Task #36: Low-Code Integration (n8n Webhook)**.

Objetivo: Criar integracao com n8n (open-source, self-hosted) via webhook HTTP para enviar resultados de analise do LogAnalyzer AI. Inclui workflow JSON importavel no n8n.

**IMPORTANTE: NAO fazer commit, NAO fazer push, NAO criar branches. Apenas implementar os arquivos e rodar testes localmente.**

---

## Descricao Detalhada

### O que fazer:

**1. Implementar WebhookIntegration**
- Criar `src/loganalyzer/integrations/__init__.py`
- Criar `src/loganalyzer/integrations/webhook.py` (~90 linhas)
- Classe `WebhookIntegration` com metodos:
  - `__init__(self, webhook_url: str, enabled: bool = True)` — Inicializa com URL do webhook
  - `send_report(self, report: str, analysis: dict) -> dict` — Envia relatorio via POST
  - `build_payload(self, report: str, analysis: dict) -> dict` — Monta payload JSON
  - `is_configured(self) -> bool` — Verifica se webhook esta configurado

Logica do `send_report`:
```python
# 1. Verificar se esta habilitado e configurado (is_configured)
# 2. Montar payload com build_payload()
# 3. Fazer POST para webhook_url com payload JSON
# 4. Retornar {"success": True/False, "status_code": N, "message": "..."}
# 5. Em caso de erro (timeout, connection), retornar success=False sem crashar
```

Logica do `build_payload`:
```python
# Retorna dict com:
# - timestamp: ISO format (datetime.now().isoformat())
# - source: "LogAnalyzer AI"
# - severity: extrair de analysis (critical/high/medium/low)
# - error_count: contar erros no analysis
# - warning_count: contar warnings no analysis
# - summary: primeiros 500 chars do report
# - full_report: report completo
```

**IMPORTANTE sobre requests:**
- Usar `requests` (ja esta no requirements.txt)
- Timeout de 10 segundos
- Tratar ConnectionError e Timeout graciosamente
- NAO crashar se webhook estiver indisponivel

**2. Workflow n8n (JSON importavel)**
- Criar `docs/low-code/n8n_workflow.json`
- Workflow com 3 nos:
  - **Webhook trigger** — Recebe POST com payload do LogAnalyzer
  - **Function** — Formata mensagem com severity + summary para email
  - **Send Email** — Envia email com o resumo da analise (assunto inclui severidade)
- Este JSON pode ser importado no n8n via UI (Import from file)
- NAO incluir credenciais ou URLs reais no JSON
- O no de Email deve usar campos parametrizaveis (to, subject, body)
- Fluxo completo: LogAnalyzer → n8n webhook → email recebido

**3. Documentacao**
- Criar `docs/low-code/n8n-integration.md` (~100 linhas)
- Secoes:
  - O que e n8n (open-source, self-hosted, alternativa a Make/Zapier)
  - Como rodar n8n local (`docker run -p 5678:5678 n8nio/n8n`)
  - Como importar o workflow (passo a passo)
  - Como copiar a URL do webhook
  - Variaveis de ambiente necessarias
  - Exemplo de payload enviado
  - Como testar (executar script de exemplo)
  - Evidencia: print do email recebido como prova de funcionamento

**4. Script de demonstracao**
- Criar `examples/run_with_webhook.py` (~40 linhas)
- Script que:
  - Le .env com dotenv
  - Executa analise em examples/sample.log
  - Envia resultado via WebhookIntegration
  - Printa resultado do envio (success/failure)

**5. Atualizar .env.example**
- Adicionar:
```env
# n8n Webhook Integration (Low-Code)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/loganalyzer
N8N_WEBHOOK_ENABLED=true
```

**6. Testes**
- Criar `tests/test_webhook_integration.py` (~90 linhas)
- Minimo 5 testes (usar mock para requests.post):
  - `test_build_payload_structure` — payload tem campos obrigatorios (timestamp, source, severity, error_count, summary)
  - `test_send_report_success` — mock retorna 200, success=True
  - `test_send_report_timeout` — mock levanta Timeout, success=False sem crash
  - `test_send_report_connection_error` — mock levanta ConnectionError, success=False
  - `test_send_report_disabled` — enabled=False, nao faz request, retorna success=False
  - `test_is_configured_without_url` — URL vazia ou None retorna False
  - `test_is_configured_with_url` — URL valida retorna True

**IMPORTANTE:** Usar `unittest.mock.patch` para mockar `requests.post`. NAO fazer requests reais nos testes.

---

## Criterios de Aceite

- [ ] `src/loganalyzer/integrations/__init__.py` existe
- [ ] `src/loganalyzer/integrations/webhook.py` existe com classe WebhookIntegration
- [ ] `docs/low-code/n8n-integration.md` existe com guia completo
- [ ] `docs/low-code/n8n_workflow.json` existe e e importavel no n8n
- [ ] `examples/run_with_webhook.py` existe como script de demonstracao
- [ ] `.env.example` atualizado com N8N_WEBHOOK_URL e N8N_WEBHOOK_ENABLED
- [ ] `tests/test_webhook_integration.py` existe com 5+ testes
- [ ] Todos os testes novos passam (com mock, sem requests reais)
- [ ] Todos os 207+ testes existentes continuam passando
- [ ] Codigo segue convencoes: comentarios PT, variaveis EN, docstrings PT
- [ ] Nenhum commit ou push realizado

---

## Restricoes

- **NAO** fazer `git commit`
- **NAO** fazer `git push`
- **NAO** criar branches
- **NAO** fazer requests HTTP reais nos testes (usar mock)
- **NAO** incluir URLs ou credenciais reais nos arquivos
- **NAO** adicionar dependencias que nao estejam no requirements.txt
- Apenas criar os arquivos novos e validar que testes passam

---

## Referencia de Estrutura

```
src/loganalyzer/integrations/
├── __init__.py
└── webhook.py

docs/low-code/
├── n8n-integration.md
└── n8n_workflow.json

examples/
└── run_with_webhook.py

tests/
└── test_webhook_integration.py
```

---

## Setup n8n (manual do desenvolvedor)

```bash
# Rodar n8n local com Docker
docker run -d --name n8n -p 5678:5678 n8nio/n8n

# Acessar UI
# http://localhost:5678

# Importar workflow
# Settings → Import from file → selecionar docs/low-code/n8n_workflow.json

# Ativar workflow e copiar URL do webhook
# Colar URL no .env: N8N_WEBHOOK_URL=http://localhost:5678/webhook/xxxx

# Testar
python examples/run_with_webhook.py
```

---

## Pontuacao Esperada

+0.50 pontos (Criterio 13 do M2.2: Low-code integration)
