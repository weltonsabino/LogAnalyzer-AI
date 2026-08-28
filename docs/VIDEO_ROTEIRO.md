# 🎥 ROTEIRO DO VÍDEO — LogAnalyzer AI (≤12 minutos)

**Projeto:** LogAnalyzer AI — Projeto Final M2.2  
**Duração:** Recomendado ≤10 min, máximo 12 min  
**Formato:** YouTube não listado  
**Data de gravação:** [PREENCHER]

---

## ⏱️ Timeline Completa

### **0:00–1:00 — PROBLEMA, OBJETIVO E CLASSIFICAÇÃO** (1 min)

#### O que mostrar na tela:
- Slide ou texto: "Análise de logs é manual, tedioso e propenso a erros"
- Slide: "Solução: Agente LangGraph automatiza análise e gera relatórios"
- Slide: "Classificação: **Sistema Híbrido** (LLM + regras determinísticas)"

#### O que você fala:
> "LogAnalyzer AI é um agente inteligente que automatiza análise de logs. O problema: logs crescem exponencialmente e análise manual é lenta. A solução: um agente com inteligência artificial que identifica padrões críticos em segundos e gera relatórios estruturados. A arquitetura é híbrida: o LLM faz análise semântica, enquanto o sistema usa regras determinísticas para roteamento e validação."

---

### **1:00–2:00 — ARQUITETURA RESUMIDA** (1 min)

#### O que mostrar na tela:
- Diagrama do StateGraph (copie do README.md ou tire screenshot)
- Destacar: 12 nós, 4 rotas condicionais, webhook n8n
- Mostrar fluxo: `validate_input → read_file → parse_events → analyze_patterns → [roteamento] → LLM → generate_report → webhook`

#### O que você fala:
> "A arquitetura tem 12 nós organizados em um StateGraph. Começa com validação (segurança), leitura do arquivo, parsing multi-formato, detecção de padrões. Depois, roteamento inteligente por severidade: se encontra eventos críticos, vai para análise HIGH; se avisos, análise MEDIUM; se info, LOW. Depois consolida, passa para LLM para análise inteligente e gera um relatório markdown estruturado. Final: webhook notifica n8n para enviar email."

---

### **2:00–4:00 — DOIS CENÁRIOS** (2 min)

#### Cenário 1: Operação Normal (Sucesso) (~1 min)

**O que mostrar na tela:**

Terminal com execução:
```bash
$ python -m src.loganalyzer.main examples/sample_critical.log
```

Resultado: Abrir `examples/sample_output.md` mostrando:
- Título: "Relatório de Análise de Log"
- Tabela de resumo (total eventos, erros, avisos, críticos)
- Seção de eventos críticos
- Recomendações de ação

**O que você fala:**
> "Primeiro cenário: log normal de aplicação com alguns avisos e erros esporádicos. Executo o agente passando o arquivo. Em segundos, gera um relatório estruturado em markdown com resumo executivo, eventos críticos identificados, análise e recomendações. A severidade detectada foi MEDIUM, então a análise foca em prevenção."

---

#### Cenário 2: Cascata de Falha Crítica (~1 min)

**O que mostrar na tela:**

Terminal com execução:
```bash
$ python -m src.loganalyzer.main tests/fixtures/failure_logs/scenario_failure.log
```

Resultado: Abrir `docs/examples/scenario_failure_output.md` mostrando:
- "## Severidade: HIGH | Urgência: IMEDIATA"
- Padrão detectado: "Cascata de Falhas" (timeline de degradação)
- Recomendações urgentes (reiniciar serviços, investigar pool, etc.)

**O que você fala:**
> "Segundo cenário: degradação progressiva. Database lento → Cache falha → Memory crescente → Pool esgotado → Crash. O agente detecta severidade HIGH, roteando para análise especializada de incidentes. Gera relatório urgente com recomendações imediatas. Note que a mesma aplicação, inputs diferentes, análises completamente distintas."

---

### **4:00–5:00 — SEGURANÇA E APROVAÇÃO HUMANA** (1 min)

#### O que mostrar na tela:

**1. Terminal: Tentar input malicioso bloqueado**
```bash
$ python -m src.loganalyzer.main "../../etc/passwd"
# Resultado: Erro ao processar arquivo
# Detalhes: Bloqueado por governança: Path traversal detectado
```

**2. Código snippet (breve):**
```python
# src/loganalyzer/governance.py
if "../" in file_path or "/etc/" in file_path:
    raise ValueError("Path traversal detectado")
```

#### O que você fala:
> "Segurança é crítica. O sistema implementa validação adversarial: detecta e bloqueia path traversal, prompt injection, command injection — tudo ANTES de processar. Se alguém tenta `../../etc/passwd`, é bloqueado imediatamente. O nível de autonomia é ANALYZE por padrão: pode ler e analisar, mas nunca executa ações destrutivas sem aprovação explícita."

---

### **5:00–6:00 — QA E TESTES** (1 min)

#### O que mostrar na tela:

**1. Terminal: Rodar testes**
```bash
$ pytest tests/test_e2e_generated_by_ai.py -v

# Output mostrando (últimas linhas):
# test_e2e_success_normal_log PASSED
# test_e2e_error_handling_node_called PASSED
# test_e2e_timeout_scenario PASSED
# test_e2e_security_input_injection_blocked PASSED
# ... 20 passed in 15.23s
```

**2. Screenshot de `docs/qa/code_review_with_ai.md` mostrando:**
- "Pylint Score: 9.83/10"
- "Coverage: 95%+"
- "20 testes E2E"
- "15+ critérios de code review"

#### O que você fala:
> "Qualidade é garantida por 222 testes, cobertura 95%, code review com IA. Pylint score 9.83/10. A priorização é por risco: testes E2E cobrem fluxo principal, error handling, timeout, retry, segurança. Cada alteração de código passa por IA revisando 15+ critérios antes de integração."

---

### **6:00–8:00 — DEVOPS: PIPELINE, LOGS, ANOMALIA, RISCO** (2 min)

#### Parte 1: Pipeline CI/CD (~45 seg)

**O que mostrar na tela:**
- Screenshot do `.github/workflows/`:
  - `lint.yml` - Pylint
  - `test.yml` - Pytest + Coverage
  - `build.yml` - Validação

**O que você fala:**
> "Pipeline CI/CD executa 3 etapas: lint (Pylint 9.83/10), testes (222 testes, 95% coverage), e validação de build. A cada push em main/develop, workflow roda automaticamente."

---

#### Parte 2: Análise de Logs + Anomalia (~45 seg)

**O que mostrar na tela:**
- Abrir `docs/devops/intelligent_log_analysis.md`
- Mostrar seção "AnomalyDetector":
  - Error Spike Detection (2x baseline = anomalia)
  - Padrões Recorrentes (3+ mesma mensagem)
  - Estimativa de Risco (low/medium/high/critical)

```python
# Exemplo do detector
result = detector.analyze(log_lines)
# Resultado:
# error_spike: True, ratio: 2.5x
# recurring_patterns: ["Connection timeout", "DB error"]
# risk_level: CRITICAL, trend: increasing
```

**O que você fala:**
> "Detecção de anomalias usa 3 heurísticas: error spike (se erros aumentam >2x em janela deslizante), padrões recorrentes (mesma mensagem 3+ vezes), e estimativa de risco consolidando ambas. Resultado: probabilidade estimada de falha. Isso permite SRE antecipar problemas antes de usuários notarem."

---

### **8:00–9:00 — AUTOMAÇÃO LOW-CODE (N8N)** (1 min)

#### O que mostrar na tela:

**1. Diagrama ou screenshot:**
```
LogAnalyzer (fim análise)
    ↓
POST webhook JSON
    ↓
n8n recebe
    ↓
Formata dados
    ↓
Envia email
```

**2. Terminal mostrando webhook sendo chamado:**
```bash
$ python -m src.loganalyzer.main examples/sample_critical.log
# ... análise ...
# Webhook enviado: https://weltonsabino.app.n8n.cloud/webhook/loganalyzer
# Email notificado: weltonsabino17@gmail.com
```

**3. (Bônus) Screenshot do workflow n8n ou email recebido**

#### O que você fala:
> "Automação low-code: último nó do pipeline chama webhook do n8n. O payload contém execution_id, severidade, contadores, resumo. n8n recebe, formata, envia email automaticamente. Lógica principal continua em Python (análise), enquanto n8n atua como orquestração e notificação. Isso permite que SRE receba alertas sem código customizado."

---

### **9:00–10:00 — LIMITAÇÕES E EVOLUÇÃO FUTURA** (1 min)

#### O que mostrar na tela:

**1. Slide com tabela:**

| Limitação | Mitigação |
|-----------|-----------|
| Síncrono (1 arquivo/exec) | Pipeline otimizado |
| Sem persistência | TraceCollector registra execução atual |
| Sem streaming | Batch processing por arquivo |
| Arquivo >50MB | Timeout 30s |

**2. Slide com "Futuro":**
- Dashboard web
- Análise de diretórios inteiros
- Monitoramento em tempo real
- Histórico em banco de dados
- Integração Prometheus/Grafana

#### O que você fala:
> "Limitações atuais: processamento é síncrono (1 arquivo por vez), sem persistência de histórico entre execuções. Mitigações: pipeline é otimizado, timeout 30s para arquivos grandes, TraceCollector registra cada execução. Futuro: dashboard web, análise de diretórios, streaming de logs, histórico em banco."

---

## 📹 DICAS PRÁTICAS DE GRAVAÇÃO

### Setup Recomendado:

#### Ferramentas:
- **Windows:** OBS Studio (grátis) ou Camtasia
- **Mac:** ScreenFlow ou QuickTime
- **Resolução:** 1080p (1920x1080)
- **Framerate:** 30fps
- **Codec:** H.264

#### Áudio:
- Fale claro, pausas naturais entre seções
- Microfone: builtin do notebook OK, idealmente headset
- Evite barulhos de fundo (rua, ventilador)
- Nível de áudio: -6dB a -3dB pico (não muito alto)

#### Edição (Recomendado):
- **Software:** DaVinci Resolve (grátis), Shotcut, iMovie
- Cortes entre seções (abrir URLs, rodar comandos)
- Transições simples (fade, cut) — sem excessos
- Título inicial: "LogAnalyzer AI — Projeto Final M2.2"
- Título final: "Obrigado! Links no README"

---

## ✅ CHECKLIST ANTES DE PUBLICAR

- [ ] Duração ≤12 minutos (confirmar com cronômetro ou editor)
- [ ] Áudio claro, sem ruído excessivo
- [ ] Todas 8 seções cobertas (confira timeline)
- [ ] Nenhuma credencial visível na tela (API keys, emails)
- [ ] YouTube publicado como "**não listado**" (não público, não privado)
- [ ] Link copiado com sucesso
- [ ] Link inserido no README.md (seção "Análise Crítica")
- [ ] Link inserido no `.kiro/specs/tasks_m2.2.md` (Task #41)
- [ ] Vídeo está acessível (teste abrir em navegador anônimo)

---

## 🎬 FLUXO DE PUBLICAÇÃO NO YOUTUBE

1. **Fazer upload:**
   - YouTube.com → Create → Upload video
   - Selecionar arquivo `.mp4` ou `.mov`
   - Preencher título, descrição, tags

2. **Configurar visibilidade:**
   - **Importante:** Não listado (Not listed), NÃO privado, NÃO público
   - Motivo: Avaliador precisa acessar via link, mas não deve aparecer em buscas

3. **Copiar link:**
   - Botão "Share" → Copiar URL
   - Formato: `https://youtu.be/[VIDEO_ID]` ou `https://www.youtube.com/watch?v=[VIDEO_ID]`

4. **Inserir em documentação:**
   ```markdown
   # Vídeo de Demonstração
   
   [Clique aqui para assistir](https://youtu.be/[VIDEO_ID])
   
   Duração: X minutos  
   Publicado em: [DATA]
   ```

---

## 📊 ESTIMATIVA DE TEMPO

| Etapa | Tempo |
|-------|-------|
| Preparar slides | 30 min |
| Gravar primeira vez | 20-40 min (com possíveis retakes) |
| Editar (cortes, transições) | 45 min - 1h |
| Upload YouTube | 10 min |
| **TOTAL** | **2-3 horas** |

**Dica:** Grave seção por seção (não tudo de uma vez). Mais fácil fazer retakes.

---

## 🎯 OBJETIVO FINAL

✅ Vídeo ≤12 min  
✅ Cobrindo 8 pontos do roteiro  
✅ Demonstrando funcionalidade real  
✅ Mostrando segurança, QA, DevOps, low-code  
✅ YouTube não listado  
✅ Link no README  

**Resultado:** 10.00 / 10 🎉

---

**Última atualização:** 27 de Agosto, 2026  
**Projeto:** LogAnalyzer AI — M2.2  
**Responsável:** Welton Sabino
