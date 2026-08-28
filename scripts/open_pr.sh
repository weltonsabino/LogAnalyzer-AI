#!/bin/bash

set -e

REPO="weltonsabino/LogAnalyzer-AI"

# ── 1. Validação: alterações não commitadas ──────────────────────────────────
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "OPERAÇÃO BLOQUEADA: Existem alterações não commitadas. Realize o commit antes de executar o push."
  exit 1
fi

# ── 2. Identificar branch atual ──────────────────────────────────────────────
BRANCH=$(git branch --show-current)

# ── 3. Validação: branch protegida ───────────────────────────────────────────
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "develop" ]; then
  echo "OPERAÇÃO BLOQUEADA: Push direto na branch '$BRANCH' é proibido. Use uma branch de feature, bugfix ou docs."
  exit 1
fi

# ── 4. Extração do ISSUE_ID ───────────────────────────────────────────────────
ISSUE_ID=$(echo "$BRANCH" | sed -E 's/.*_task([0-9]+)$/\1/')
if [ "$ISSUE_ID" = "$BRANCH" ]; then
  ISSUE_ID=$(echo "$BRANCH" | sed -E 's#^[a-zA-Z]+/task([0-9]+).*$#\1#')
fi
if [ -z "$ISSUE_ID" ] || [ "$ISSUE_ID" = "$BRANCH" ]; then
  echo "Erro: não foi possível identificar o número da Issue pela branch '$BRANCH'."
  echo "   Padrões aceitos: feature/<slug>_task<N> ou bugfix/<slug>_task<N>"
  exit 1
fi

# ── 5. Buscar título da issue no GitHub ──────────────────────────────────────
ISSUE_TITLE=$(gh issue view "$ISSUE_ID" --repo "$REPO" --json title --jq '.title')
if [ -z "$ISSUE_TITLE" ]; then
  echo "Erro: não foi possível obter o título da Issue #$ISSUE_ID no repositório $REPO."
  exit 1
fi

PR_TITLE=$(echo "$ISSUE_TITLE" | sed -E 's/^\[(STORY|EPIC|DOCS|TECH|BUG)\] *//')

# ── 6. Determinar tipo de commit pelo prefixo da branch ──────────────────────
COMMIT_TYPE="feat"
case "$BRANCH" in
  docs/*)   COMMIT_TYPE="docs" ;;
  bugfix/*) COMMIT_TYPE="fix" ;;
esac

# ── 7. Coletar commits da branch em relação a develop ────────────────────────
COMMIT_LOG=$(git log origin/develop..HEAD --pretty=format:"%s" 2>/dev/null || true)
if [ -z "$COMMIT_LOG" ]; then
  COMMIT_LOG=$(git log develop..HEAD --pretty=format:"%s" 2>/dev/null || true)
fi
COMMIT_COUNT=$(echo "$COMMIT_LOG" | grep -c . 2>/dev/null || echo "0")

# ── 8. Coletar arquivos alterados em relação a develop ───────────────────────
CHANGED_FILES=$(git diff origin/develop..HEAD --name-only 2>/dev/null || true)
if [ -z "$CHANGED_FILES" ]; then
  CHANGED_FILES=$(git diff develop..HEAD --name-only 2>/dev/null || true)
fi
TOTAL_FILES=$(echo "$CHANGED_FILES" | grep -c . 2>/dev/null || echo "0")

# ── 9. Classificar arquivos por camada ───────────────────────────────────────
FILES_CONTROLLERS=$(echo "$CHANGED_FILES" | grep -i 'controller' || true)
FILES_USECASES=$(echo "$CHANGED_FILES" | grep -iE 'usecase|use.case' || true)
FILES_SERVICES=$(echo "$CHANGED_FILES" | grep -i 'service' | grep -iv 'test' || true)
FILES_DOMAIN=$(echo "$CHANGED_FILES" | grep -iE 'domain/model|domain\\model' || true)
FILES_DTOS=$(echo "$CHANGED_FILES" | grep -iE 'dto|request|response' || true)
FILES_MAPPERS=$(echo "$CHANGED_FILES" | grep -i 'mapper' || true)
FILES_EXCEPTIONS=$(echo "$CHANGED_FILES" | grep -iE 'exception|handler' || true)
FILES_PERSISTENCE=$(echo "$CHANGED_FILES" | grep -iE 'persistence|repository|entity' || true)
FILES_CONFIG=$(echo "$CHANGED_FILES" | grep -iE 'config|configuration' || true)
FILES_TESTS=$(echo "$CHANGED_FILES" | grep -iE 'src/test|src\\test' || true)
FILES_FRONTEND=$(echo "$CHANGED_FILES" | grep -E '^frontend/' || true)
FILES_CICD=$(echo "$CHANGED_FILES" | grep -iE '\.github|\.yml|\.yaml' || true)
FILES_DOCS=$(echo "$CHANGED_FILES" | grep -E '^docs/' || true)

# ── 10. Contar arquivos por camada ───────────────────────────────────────────
count_lines() { echo "$1" | grep -c . 2>/dev/null || echo "0"; }

COUNT_CONTROLLERS=$(count_lines "$FILES_CONTROLLERS")
COUNT_USECASES=$(count_lines "$FILES_USECASES")
COUNT_SERVICES=$(count_lines "$FILES_SERVICES")
COUNT_DOMAIN=$(count_lines "$FILES_DOMAIN")
COUNT_DTOS=$(count_lines "$FILES_DTOS")
COUNT_MAPPERS=$(count_lines "$FILES_MAPPERS")
COUNT_EXCEPTIONS=$(count_lines "$FILES_EXCEPTIONS")
COUNT_PERSISTENCE=$(count_lines "$FILES_PERSISTENCE")
COUNT_CONFIG=$(count_lines "$FILES_CONFIG")
COUNT_TESTS=$(count_lines "$FILES_TESTS")
COUNT_FRONTEND=$(count_lines "$FILES_FRONTEND")
COUNT_CICD=$(count_lines "$FILES_CICD")
COUNT_DOCS=$(count_lines "$FILES_DOCS")

# ── 11. Detectar métodos de teste ────────────────────────────────────────────
TEST_METHODS=""
if [ -n "$FILES_TESTS" ]; then
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    methods=$(git show "HEAD:$f" 2>/dev/null | grep -oE 'void [a-zA-Z_][a-zA-Z0-9_]*\s*\(' | sed 's/void //;s/\s*($//' | head -10 || true)
    if [ -n "$methods" ]; then
      TEST_METHODS="$TEST_METHODS
$methods"
    fi
  done <<< "$FILES_TESTS"
fi

# ── 12. Detectar endpoints nos controllers ───────────────────────────────────
ENDPOINTS_TABLE=""
if [ -n "$FILES_CONTROLLERS" ]; then
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    content=$(git show "HEAD:$f" 2>/dev/null || true)
    if [ -n "$content" ]; then
      # Extrair mapeamentos simples
      get_eps=$(echo "$content" | grep -oE '@GetMapping\("[^"]*"\)' | sed 's/@GetMapping("\(.*\)")/GET \1/' || true)
      post_eps=$(echo "$content" | grep -oE '@PostMapping\("[^"]*"\)' | sed 's/@PostMapping("\(.*\)")/POST \1/' || true)
      put_eps=$(echo "$content" | grep -oE '@PutMapping\("[^"]*"\)' | sed 's/@PutMapping("\(.*\)")/PUT \1/' || true)
      patch_eps=$(echo "$content" | grep -oE '@PatchMapping\("[^"]*"\)' | sed 's/@PatchMapping("\(.*\)")/PATCH \1/' || true)
      del_eps=$(echo "$content" | grep -oE '@DeleteMapping\("[^"]*"\)' | sed 's/@DeleteMapping("\(.*\)")/DELETE \1/' || true)
      all_eps=$(printf '%s\n%s\n%s\n%s\n%s' "$get_eps" "$post_eps" "$put_eps" "$patch_eps" "$del_eps" | grep -v '^$' || true)
      if [ -n "$all_eps" ]; then
        ENDPOINTS_TABLE="$ENDPOINTS_TABLE
$all_eps"
      fi
    fi
  done <<< "$FILES_CONTROLLERS"
fi

# ── 13. Construir seção Objetivo ─────────────────────────────────────────────
if [ "$COMMIT_COUNT" -eq 1 ]; then
  OBJETIVO="$COMMIT_LOG — Issue #${ISSUE_ID}."
else
  OBJETIVO="Implementação referente à Issue #${ISSUE_ID}: **$PR_TITLE**."
fi

# ── 14. Construir seção Principais Alterações ────────────────────────────────
build_layer_section() {
  local label="$1"
  local files="$2"
  if [ -n "$files" ]; then
    echo "**$label:**"
    echo "$files" | while IFS= read -r f; do
      [ -n "$f" ] && echo "  - \`$f\`"
    done
    echo ""
  fi
}

ALTERACOES_SECTION=$(
  build_layer_section "Backend — Controllers" "$FILES_CONTROLLERS"
  build_layer_section "Backend — Use Cases" "$FILES_USECASES"
  build_layer_section "Backend — Services" "$FILES_SERVICES"
  build_layer_section "Domínio" "$FILES_DOMAIN"
  build_layer_section "DTOs (Request / Response)" "$FILES_DTOS"
  build_layer_section "Mappers" "$FILES_MAPPERS"
  build_layer_section "Exceptions / Error Handling" "$FILES_EXCEPTIONS"
  build_layer_section "Persistência (JPA / Repository)" "$FILES_PERSISTENCE"
  build_layer_section "Configuração" "$FILES_CONFIG"
  build_layer_section "Testes" "$FILES_TESTS"
  build_layer_section "Frontend" "$FILES_FRONTEND"
  build_layer_section "CI/CD" "$FILES_CICD"
  build_layer_section "Documentação" "$FILES_DOCS"
)

if [ -z "$ALTERACOES_SECTION" ]; then
  ALTERACOES_SECTION="_Nenhum arquivo identificado nas camadas conhecidas._"
fi

# ── 15. Construir seção Impacto Técnico ──────────────────────────────────────
IMPACTO_SECTION=""
BACKEND_COUNT=$((COUNT_CONTROLLERS + COUNT_USECASES + COUNT_SERVICES + COUNT_DOMAIN))
INFRA_COUNT=$((COUNT_PERSISTENCE + COUNT_CONFIG))

[ "$BACKEND_COUNT" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **Backend:** $BACKEND_COUNT arquivo(s) alterado(s) nas camadas de API, aplicação e domínio."
[ "$INFRA_COUNT" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **Infraestrutura:** $INFRA_COUNT arquivo(s) alterado(s) em persistência e configuração."
[ "$COUNT_EXCEPTIONS" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **Tratamento de erros:** handler(s) de exceção adicionado(s) ou modificado(s)."
[ "$COUNT_MAPPERS" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **Mapeamento:** conversão entre camadas (DTO ↔ Domínio ↔ Entidade JPA) atualizada."
[ "$COUNT_TESTS" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **Testes:** $COUNT_TESTS arquivo(s) de teste adicionado(s) ou modificado(s)."
[ "$COUNT_FRONTEND" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **Frontend:** $COUNT_FRONTEND arquivo(s) React/TypeScript alterado(s)."
[ "$COUNT_CICD" -gt 0 ] && IMPACTO_SECTION="$IMPACTO_SECTION
- **CI/CD:** pipeline ou workflow GitHub Actions modificado."
IMPACTO_SECTION="$IMPACTO_SECTION
- **Total de arquivos alterados:** $TOTAL_FILES"

# ── 16. Construir seção Endpoints ────────────────────────────────────────────
ENDPOINTS_SECTION=""
if [ -n "$FILES_CONTROLLERS" ]; then
  if [ -n "$ENDPOINTS_TABLE" ]; then
    ENDPOINTS_SECTION="## Endpoints Alterados

| Método | Endpoint |
|--------|----------|"
    echo "$ENDPOINTS_TABLE" | grep -v '^$' | while IFS= read -r ep; do
      parts=($ep)
      verb="${parts[0]}"
      path="${parts[1]:-/}"
      ENDPOINTS_SECTION="$ENDPOINTS_SECTION
| \`$verb\` | \`$path\` |"
    done
  else
    ENDPOINTS_SECTION="## Endpoints Alterados

Controllers modificados (inspecionar manualmente para detalhes dos endpoints):
$(echo "$FILES_CONTROLLERS" | while IFS= read -r f; do [ -n "$f" ] && echo "- \`$f\`"; done)"
  fi
fi

# ── 17. Construir seção Testes ───────────────────────────────────────────────
if [ -n "$FILES_TESTS" ]; then
  TESTES_SECTION="**Arquivos de teste:**
$(echo "$FILES_TESTS" | while IFS= read -r f; do [ -n "$f" ] && echo "- \`$f\`"; done)"

  if [ -n "$TEST_METHODS" ]; then
    TESTES_SECTION="$TESTES_SECTION

**Cenários validados:**
$(echo "$TEST_METHODS" | grep -v '^$' | head -10 | while IFS= read -r m; do echo "- \`$m\`"; done)"
  fi
else
  TESTES_SECTION="_Nenhum arquivo de teste identificado neste PR._"
fi

# ── 18. Construir bullets de commits ─────────────────────────────────────────
if [ -n "$COMMIT_LOG" ]; then
  COMMIT_BULLETS=$(echo "$COMMIT_LOG" | sed 's/^/- /')
else
  COMMIT_BULLETS="- _Nenhum commit identificado além do base._"
fi

# ── 19. Montar body do PR em arquivo temporário ──────────────────────────────
BODY_FILE=$(mktemp --suffix=.md)

cat > "$BODY_FILE" <<PREOF
## Objetivo

$OBJETIVO

## Principais Alterações

$ALTERACOES_SECTION

## Impacto Técnico

$IMPACTO_SECTION

$ENDPOINTS_SECTION

## Testes

$TESTES_SECTION

## Evidências

- Issue relacionada: Closes #$ISSUE_ID
- Implementação guiada por IA (Kiro) — prompts registrados em \`docs/prompts/\`
- Projeto avaliativo: demonstração de Clean Architecture + Hexagonal + SOLID com suporte de IA generativa

## Checklist

- [ ] Código revisado e limpo
- [ ] Testes executados com sucesso
- [ ] Documentação atualizada
- [ ] Swagger atualizado (quando aplicável)
- [ ] Sem erros de lint ou compilação
- [ ] Build funcionando no CI

## Commits neste PR

$COMMIT_BULLETS

## Observações

> _Preencher manualmente se houver riscos, limitações técnicas ou próximos passos relevantes._
PREOF

# ── 20. Push da branch ───────────────────────────────────────────────────────
echo "Executando push da branch '$BRANCH'..."
git push -u origin "$BRANCH"

# ── 21. Criar ou atualizar Pull Request ──────────────────────────────────────
echo "Verificando se já existe PR para esta branch..."
EXISTING_PR=$(gh pr view "$BRANCH" --repo "$REPO" --json url --jq '.url' 2>/dev/null || true)

if [ -n "$EXISTING_PR" ]; then
  echo "PR já existe: $EXISTING_PR"
  echo "Atualizando body do PR..."
  gh pr edit "$EXISTING_PR" --repo "$REPO" --body-file "$BODY_FILE"
  PR_URL="$EXISTING_PR"
  echo "Body do PR atualizado: $PR_URL"
else
  echo "Abrindo Pull Request para develop..."
  PR_URL=$(gh pr create \
    --repo "$REPO" \
    --base develop \
    --head "$BRANCH" \
    --title "$COMMIT_TYPE: $PR_TITLE" \
    --body-file "$BODY_FILE")

  if [ -z "$PR_URL" ]; then
    echo "Erro ao criar PR. Verifique em: https://github.com/$REPO/pulls"
    rm "$BODY_FILE"
    exit 1
  fi

  echo "Pull Request criado: $PR_URL"

  # ── 22. Adicionar PR ao projeto Kanban ─────────────────────────────────────
  echo "Adicionando PR ao projeto Kanban..."
  gh project item-add 19 --owner IA-para-DEVs-SCTEC-T2 --url "$PR_URL"
  echo "PR adicionado ao Kanban com sucesso."
fi

rm "$BODY_FILE"
