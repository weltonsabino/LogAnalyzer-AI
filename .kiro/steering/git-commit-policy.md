# Política de Commits e Git — LogAnalyzer AI

## 🚫 Regra Absoluta: PROIBIDO Commits Automáticos

**NUNCA fazer commit ou push por conta própria, sem autorização explícita do desenvolvedor.**

---

## ✅ O que Fazer

### Antes de Qualquer Operação Git

1. **Identificar mudanças** — Verificar o que foi modificado
2. **Informar ao usuário** — Descrever exatamente quais arquivos serão afetados
3. **Aguardar confirmação** — Obter aprovação explícita ANTES de prosseguir
4. **Executar com permissão** — Fazer commit/push APENAS após autorização

### Exemplo de Fluxo Correto

```
Usuário: Implemente a feature X

Kiro: Vou fazer as seguintes mudanças:
  • src/feature.py (novo arquivo)
  • tests/test_feature.py (novo arquivo)
  • requirements.txt (atualizado)

Autorizo fazer commit dessas mudanças?

Usuário: Sim, prossiga

Kiro: [faz commit e push com permissão]
```

---

## ❌ O que NÃO Fazer

| ❌ PROIBIDO | Motivo |
|-----------|--------|
| Fazer commit silenciosamente | Desenvolvedor perde controle |
| Fazer push automático | Pode conflitar com trabalho local |
| Criar branches sem avisar | Confunde histórico do repositório |
| Forçar push (force push) | Pode perder trabalho de outros |
| Fazer rebase sem permissão | Altera histórico de commits |
| Deletar branches sem avisar | Pode perder código importante |

---

## 📋 Checklist Obrigatório

Antes de QUALQUER operação git:

- [ ] Listar TODOS os arquivos que serão afetados
- [ ] Descrever o que cada mudança faz
- [ ] Informar branch alvo (develop, main, feature/*, etc)
- [ ] **AGUARDAR confirmação explícita do usuário**
- [ ] Só depois executar o comando

---

## 🔒 Exceções (Raríssimas)

Commits automáticos são permitidos APENAS se:

1. O usuário explicitamente pediu: "Faz tudo sozinho"
2. AND você resumiu exatamente quais mudanças serão feitas
3. AND o usuário confirmou
4. AND é uma tarefa bem definida e baixo risco

**Mesmo nesses casos, informar ao final:**
```
✅ Feito! Mudanças commitadas em: [hash do commit]
Branch: [branch name]
Arquivos: [lista]
```

---

## 📝 Mensagens de Commit

Padrão semântico obrigatório:

```
feat: adicionar nova funcionalidade
fix: corrigir bug
docs: atualizar documentação
refactor: reorganizar código
test: adicionar testes
chore: manutenção
```

Exemplo correto:
```
feat: implementar autenticação de usuários

- Adicionar rota /login
- Integrar JWT
- Criar tabela users
```

---

## 🎯 Resumo

**Em uma frase:** Nunca faça commit sem pedir permissão first.

---

**Última atualização:** 2026-07-09  
**Status:** ✅ OBRIGATÓRIO  
**Responsável:** Desenvolvedor (você autoriza o que acontece)
