# Integracao Low-Code: n8n Webhook

> Automacao de notificacoes por email usando n8n (open-source, self-hosted).

**Modulo:** `src/loganalyzer/integrations/webhook.py`  
**Workflow:** `docs/low-code/n8n_workflow.json`  
**Task:** #36 — Low-Code Integration

---

## O que e n8n

n8n e uma plataforma de automacao open-source e self-hosted. Alternativa gratuita ao Make.com e Zapier. Permite criar workflows visuais (drag-and-drop) que conectam servicos via webhooks, APIs e acoes automatizadas.

- Open-source (licenca fair-code)
- Self-hosted via Docker (sem limites de execucao)
- 400+ integracoes nativas
- UI visual para criacao de fluxos

---

## Fluxo Implementado

```
LogAnalyzer AI          n8n (local)              Email
     |                      |                      |
     |--- POST payload ---->|                      |
     |                      |--- Formata dados --->|
     |                      |--- Envia email ----->|
     |                      |                      |
     |<-- 200 OK ----------|                      |
```

**3 nos no workflow:**
1. **Webhook LogAnalyzer** — Recebe POST com payload JSON
2. **Formatar Email** — Monta subject e body HTML com severidade
3. **Enviar Email** — Dispara email via SMTP configurado

---

## Setup Rapido

### 1. Rodar n8n com Docker

```bash
docker run -d --name n8n -p 5678:5678 n8nio/n8n
```

Acessar: http://localhost:5678

### 2. Importar Workflow

1. Abrir n8n UI → Menu lateral → "Workflows"
2. Clicar "Import from File"
3. Selecionar `docs/low-code/n8n_workflow.json`
4. Workflow aparece com 3 nos conectados

### 3. Configurar SMTP (Email)

1. Clicar no nó "Enviar Email"
2. Em "Credentials" → "Connect to SMTP"
3. Preencher dados SMTP:
   - User: seu email
   - Password: senha de app (Gmail: gerar em myaccount.google.com/apppasswords, colar a senha no campo sem espaços)
   - Host: `smtp.gmail.com` (ou seu provedor)
   - Port: `465`
   - SSL/TLS: Habilitado
4. Salvar

**NOTA:** Os campos To/From do email NAO precisam ser editados no n8n. Eles sao enviados automaticamente via payload pelas variaveis `N8N_EMAIL_TO` e `N8N_EMAIL_FROM` do `.env`.

**Para n8n.cloud (remoto):** Mesmo procedimento — configurar credenciais SMTP uma unica vez na UI do cloud.

### 4. Ativar Workflow

1. Toggle "Publish" no canto superior direito
2. Copiar URL do webhook (ex: `http://localhost:5678/webhook/loganalyzer`)

### 5. Configurar .env

```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/loganalyzer
N8N_WEBHOOK_ENABLED=true
N8N_EMAIL_TO=seuemail@gmail.com
N8N_EMAIL_FROM=seuemail@gmail.com
```

### 6. Testar

```bash
python examples/run_with_webhook.py
```

---

## Payload Enviado

```json
{
  "timestamp": "2026-08-24T21:51:00.000000",
  "source": "LogAnalyzer AI",
  "severity": "high",
  "error_count": 5,
  "warning_count": 2,
  "summary": "## Relatorio de Analise\n\nResumo dos primeiros 500 caracteres...",
  "full_report": "Relatorio completo em markdown...",
  "email_to": "seuemail@gmail.com",
  "email_from": "seuemail@gmail.com"
}
```

---

## Variaveis de Ambiente

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| `N8N_WEBHOOK_URL` | URL do webhook n8n | `http://localhost:5678/webhook/loganalyzer` |
| `N8N_WEBHOOK_ENABLED` | Habilita/desabilita envio | `true` ou `false` |
| `N8N_EMAIL_TO` | Destinatario do email | `seuemail@gmail.com` |
| `N8N_EMAIL_FROM` | Remetente do email | `seuemail@gmail.com` |

---

## Evidencia de Funcionamento

Ao executar com sucesso, o terminal mostra:

```
[INFO] Analise concluida. Enviando para webhook...
[INFO] Webhook enviado com sucesso (status: 200)
```

E o email chega com:
- Assunto: "🟠 LogAnalyzer AI - Severidade: HIGH"
- Body: HTML com resumo da analise, contagem de erros, timestamp

---

## Limitacoes

- Requer Docker para rodar n8n localmente (ou usar n8n.cloud)
- Credenciais SMTP precisam ser configuradas UMA VEZ na UI do n8n (unica etapa manual)
- Webhook so funciona com n8n ativo (Docker local ou cloud)
- Campos To/From sao enviados via payload — nao requerem edição no n8n

---

**Ultima atualizacao:** Agosto 2026
