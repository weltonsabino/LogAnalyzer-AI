---
inclusion: always
---

# Regra Obrigatória: Registro de Prompts — LogAnalyzer AI

## 🎯 Status

✅ **OBRIGATÓRIO** | ✅ **AUTOMÁTICO** | ✅ **SILENCIOSO**

## 📋 Fluxo de Execução Obrigatório

**ORDEM DE EXECUÇÃO — NÃO PODE SER ALTERADA:**

```
1. Usuário envia prompt
   ↓
2. Hook intercepta ("promptSubmit")
   ↓
3. Validação de Relevância (>250 chars + implementação)
   ↓
4. Extração de Metadados (author, timestamp, summary)
   ↓
5. Persistência em docs/prompts/
   ↓
6. Validação de Sucesso
   ↓
7. SOMENTE DEPOIS: Processar a solicitação principal
```

## ✅ Critérios de Registro (FILTRO OBRIGATÓRIO)

**Um prompt é registrado SE E SOMENTE SE:**

- ✅ Tem **> 250 caracteres**
- ✅ É pedido de **implementar**, **criar**, **modificar**, **corrigir**, **documentar**, **atualizar** ou **refatorar**
- ✅ Envolve **código**, **testes**, **documentação** ou **configuração**

**Um prompt é IGNORADO (silenciosamente) SE:**

- ❌ Tem ≤ 250 caracteres
- ❌ É pergunta simples (ex: "o que é?", "como funciona?")
- ❌ É confirmação (ex: "ok", "sim", "continue")
- ❌ É pedido de explicação sem ação

## 📝 Estrutura do Arquivo Registrado

```
Prompt: <resumo objetivo até 100 caracteres>
Responsável: <nome completo>
Usuário: <identificador-em-lowercase-com-hifens>
Data/hora: <YYYY-MM-DD HH:MM:SS>

## Prompt original

<conteúdo completo e literal do prompt, sem truncamento>
```

### Exemplo Real

```
Prompt: Implementar module análise com parser, detector, formatter
Responsável: Welton Sabino
Usuário: welton-sabino
Data/hora: 2026-07-07 23:35:21

## Prompt original

Preciso que você configure no meu projeto essa regra básica. Para que qualquer alteração que você faça, você segue essa regra. Todo comentário deverá estar em português, variáveis e funções em inglês...
```

## 🔄 Integração com Fluxo do Projeto

### Antes Desta Regra (❌ Problema)

```
Usuario envia prompt
↓
Kiro processa imediatamente
↓
(Prompt NÃO é registrado)
↓
Resultado: Perda de rastreabilidade
```

### Depois Desta Regra (✅ Correto)

```
Usuário envia prompt
↓
Hook valida relevância
↓
Se válido: Registra em docs/prompts/
↓
Se inválido: Ignora silenciosamente
↓
Kiro processa solicitação
↓
Resultado: 100% de rastreabilidade
```

## 🔧 Configuração Técnica

### Hook Ativo

- **Arquivo:** `.kiro/hooks/log-prompts-to-file.kiro.hook`
- **Evento:** `promptSubmit`
- **Ação:** `askAgent` (com instruções completas de registro)
- **Timeout:** 30 segundos
- **Status:** ✅ ATIVO E OBRIGATÓRIO

### Diretório de Armazenamento

- **Caminho:** `docs/prompts/`
- **Padrão de Nome:** `YYYY-MM-DD_HH-mm-ss_usuario.md`
- **Exemplo:** `2026-07-07_23-35-21_welton-sabino.md`
- **Encoding:** UTF-8

## 📊 Rastreabilidade Garantida

Cada prompt registrado permite:

✅ **Histórico completo** de alterações e decisões  
✅ **Rastreabilidade** de quem pediu o quê e quando  
✅ **Auditoria** de evolução do projeto  
✅ **Referência** para documentação futura  
✅ **Validação** de critérios de avaliação  

## ⚡ Regras de Ouro

1. **SEMPRE registrar ANTES de processar**
   - Não há exceções
   - Não há bypass
   - Não há "depois"

2. **Registro SILENCIOSO**
   - Não interrompe fluxo
   - Não mostra mensagens ao usuário
   - Apenas executa e confirma

3. **NUNCA perder um prompt**
   - Validação clara de sucesso
   - Arquivo sempre criado
   - Nomes únicos garantidos

4. **Validação de relevância é OBRIGATÓRIA**
   - Não pode ser ignorada
   - Filtra ruído automaticamente
   - Mantém histórico limpo

## 🔍 Como Verificar se Está Funcionando

### Verificar Diretório

```bash
# Ver prompts registrados
ls -la docs/prompts/

# Contar prompts
ls docs/prompts/ | wc -l
```

### Validar Arquivo

```bash
# Ver conteúdo de um prompt
cat docs/prompts/2026-07-07_23-35-21_welton-sabino.md

# Verificar estrutura
head -5 docs/prompts/2026-07-07_23-35-21_welton-sabino.md
```

### Monitorar Novos Registros

```bash
# Ver últimos prompts registrados
ls -lt docs/prompts/ | head -5

# Verificar timestamp mais recente
ls -lt docs/prompts/ | head -1
```

## ⚠️ Se o Registro Falhar

**Não há tolerância a falhas:**

1. Hook não consegue criar arquivo
   → ❌ **Tarefa bloqueada** até resolução
   → Informar motivo exato
   → Solicitar aprovação antes de prosseguir

2. Validação identifica problema
   → ❌ **Análise parada** até correção
   → Detalhar qual validação falhou
   → Aguardar input do usuário

3. Arquivo não pode ser persistido
   → ❌ **Tudo parado**
   → Verificar permissões de pasta
   → Verificar espaço em disco
   → Limpar `docs/prompts/` se necessário

## 📋 Checklist para Cada Sessão

Antes de iniciar qualquer trabalho:

- [ ] Hook está habilitado em `.kiro/hooks/`
- [ ] Diretório `docs/prompts/` existe e é acessível
- [ ] Últimos prompts foram registrados com sucesso
- [ ] Estrutura de arquivos segue o padrão
- [ ] Nenhum prompt foi perdido na sessão anterior

## 🚀 Impacto para o Projeto

### Conformidade de Avaliação

Critério: **Contribução Individual e Rastreabilidade**
- ✅ Todos os prompts que geraram código estão documentados
- ✅ Histórico completo de decisões
- ✅ Rastreabilidade de evolução
- ✅ Prova de autoria e cronologia

### Vantagens Operacionais

- 📊 Análise post-mortem de bugs
- 📈 Métricas de produtividade
- 🎯 Referência para futuras melhorias
- 🔐 Auditoria de segurança
- 📚 Base de conhecimento

---

**Última atualização:** Julho 2026  
**Versão:** 1.0  
**Status:** ✅ OBRIGATÓRIO E ATIVO

