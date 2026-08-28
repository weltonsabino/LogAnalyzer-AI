#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$REPO = "weltonsabino/LogAnalyzer-AI"

# ── 1. Validacao: alteracoes nao commitadas ──────────────────────────────────
$null = git diff --exit-code 2>&1
$hasDiff = $LASTEXITCODE -ne 0
$null = git diff --cached --exit-code 2>&1
$hasCached = $LASTEXITCODE -ne 0

if ($hasDiff -or $hasCached) {
    Write-Host "OPERACAO BLOQUEADA: Existem alteracoes nao commitadas. Realize o commit antes de executar o push."
    exit 1
}

# ── 2. Identificar branch atual ──────────────────────────────────────────────
$branch = git branch --show-current

# ── 3. Validacao: branch protegida ───────────────────────────────────────────
if ($branch -eq "main" -or $branch -eq "develop") {
    Write-Host "OPERACAO BLOQUEADA: Push direto na branch '$branch' e proibido. Use uma branch de feature, bugfix ou docs."
    exit 1
}

# ── 4. Extracao do ISSUE_ID ──────────────────────────────────────────────────
if ($branch -match '_task(\d+)$') {
    $issueId = $Matches[1]
} elseif ($branch -match '^[a-zA-Z]+/task(\d+)') {
    $issueId = $Matches[1]
} else {
    Write-Host "Erro: nao foi possivel identificar o numero da Issue pela branch '$branch'."
    Write-Host "   Padroes aceitos: feature/<slug>_task<N> ou bugfix/<slug>_task<N>"
    exit 1
}

# ── 5. Buscar titulo da issue no GitHub ──────────────────────────────────────
$issueTitle = gh issue view $issueId --repo $REPO --json title --jq '.title'
if (-not $issueTitle) {
    Write-Host "Erro: nao foi possivel obter o titulo da Issue #$issueId no repositorio $REPO."
    exit 1
}

$prTitle = $issueTitle -replace '^\[(STORY|EPIC|DOCS|TECH|BUG)\]\s*', ''

# ── 6. Determinar tipo de commit pelo prefixo da branch ────────────────────
$commitType = switch -Wildcard ($branch) {
    "docs/*"   { "docs" }
    "bugfix/*" { "fix" }
    default    { "feat" }
}

# ── 7. Coletar commits da branch em relacao a develop ────────────────────────
$commitLog = $null
try { $commitLog = git log origin/develop..HEAD --pretty=format:"%s" 2>$null } catch { $commitLog = $null }
if (-not $commitLog) {
    try { $commitLog = git log develop..HEAD --pretty=format:"%s" 2>$null } catch { $commitLog = $null }
}
$commitLines = if ($commitLog) { $commitLog -split "`n" | Where-Object { $_.Trim() -ne "" } } else { @() }
$commitCount = $commitLines.Count

# ── 8. Coletar arquivos alterados em relacao a develop ─────────────────────
$changedFiles = $null
try { $changedFiles = git diff origin/develop..HEAD --name-only 2>$null } catch { $changedFiles = $null }
if (-not $changedFiles) {
    try { $changedFiles = git diff develop..HEAD --name-only 2>$null } catch { $changedFiles = $null }
}
$fileList = if ($changedFiles) { $changedFiles -split "`n" | Where-Object { $_.Trim() -ne "" } } else { @() }

# ── 9. Classificar arquivos por camada (adaptado para Python/LangGraph) ────────
function Get-FilesByLayer {
    param([string[]]$files)

    $layers = @{
        Agent    = @()
        Analysis = @()
        Tools    = @()
        Models   = @()
        Utils    = @()
        Nodes    = @()
        Tests    = @()
        Docs     = @()
        Config   = @()
        Other    = @()
    }

    foreach ($f in $files) {
        $fn = $f.ToLower()
        if     ($fn -match 'agent\.py')                          { $layers.Agent    += $f }
        elseif ($fn -match 'src/loganalyzer/analysis')           { $layers.Analysis += $f }
        elseif ($fn -match 'src/loganalyzer/tools')              { $layers.Tools    += $f }
        elseif ($fn -match 'models\.py')                         { $layers.Models   += $f }
        elseif ($fn -match 'src/loganalyzer/utils')              { $layers.Utils    += $f }
        elseif ($fn -match 'nodes\.py')                          { $layers.Nodes    += $f }
        elseif ($fn -match 'tests/')                             { $layers.Tests    += $f }
        elseif ($fn -match '^docs/')                             { $layers.Docs     += $f }
        elseif ($fn -match 'requirements\.txt|\.env|\.kiro|\.github') { $layers.Config += $f }
        else                                                     { $layers.Other    += $f }
    }

    return $layers
}

$layers = Get-FilesByLayer -files $fileList

# ── 10. Construir secoes do body ─────────────────────────────────────────────

# Objetivo
$objetivoBase = "Implementacao referente a Issue #${issueId}: **$prTitle**."

# Resumo do que foi feito com base nos commits e camadas alteradas
$resumoPartes = @()

if ($commitCount -eq 1) {
    $resumoPartes += $commitLines[0]
} elseif ($commitCount -gt 1) {
    $resumoPartes += "$commitCount commits realizados nesta branch."
}

$camadasAlteradas = @()
if ($layers.Agent.Count    -gt 0) { $camadasAlteradas += "agent (StateGraph)" }
if ($layers.Analysis.Count -gt 0) { $camadasAlteradas += "analise (parser, detector, formatter)" }
if ($layers.Tools.Count    -gt 0) { $camadasAlteradas += "ferramentas" }
if ($layers.Models.Count   -gt 0) { $camadasAlteradas += "modelos (TypedDict)" }
if ($layers.Utils.Count    -gt 0) { $camadasAlteradas += "utilitarios" }
if ($layers.Nodes.Count    -gt 0) { $camadasAlteradas += "nos" }
if ($layers.Tests.Count    -gt 0) { $camadasAlteradas += "testes" }
if ($layers.Docs.Count     -gt 0) { $camadasAlteradas += "documentacao" }
if ($layers.Config.Count   -gt 0) { $camadasAlteradas += "configuracao" }

if ($camadasAlteradas.Count -gt 0) {
    $resumoPartes += "Camadas impactadas: " + ($camadasAlteradas -join ", ") + "."
}

if ($fileList.Count -gt 0) {
    $resumoPartes += "$($fileList.Count) arquivo(s) alterado(s) no total."
}

$resumo = if ($resumoPartes.Count -gt 0) {
    $resumoLines = $resumoPartes | ForEach-Object { "> $_" }
    "`n`n" + ($resumoLines -join "`n")
} else { "" }

$objetivo = "$objetivoBase$resumo"

# Principais Alteracoes — resumo por camada
function Build-AlteracoesSection {
    param($layers)

    $lines = @()

    if ($layers.Agent.Count    -gt 0) { $lines += "- **Agent (StateGraph):** $($layers.Agent.Count) arquivo(s)" }
    if ($layers.Analysis.Count -gt 0) { $lines += "- **Analise (Parser/Detector/Formatter):** $($layers.Analysis.Count) arquivo(s)" }
    if ($layers.Tools.Count    -gt 0) { $lines += "- **Ferramentas:** $($layers.Tools.Count) arquivo(s)" }
    if ($layers.Models.Count   -gt 0) { $lines += "- **Modelos (TypedDict):** $($layers.Models.Count) arquivo(s)" }
    if ($layers.Utils.Count    -gt 0) { $lines += "- **Utilitarios:** $($layers.Utils.Count) arquivo(s)" }
    if ($layers.Nodes.Count    -gt 0) { $lines += "- **Nos:** $($layers.Nodes.Count) arquivo(s)" }
    if ($layers.Tests.Count    -gt 0) { $lines += "- **Testes:** $($layers.Tests.Count) arquivo(s)" }
    if ($layers.Docs.Count     -gt 0) { $lines += "- **Documentacao:** $($layers.Docs.Count) arquivo(s)" }
    if ($layers.Config.Count   -gt 0) { $lines += "- **Configuracao:** $($layers.Config.Count) arquivo(s)" }
    if ($layers.Other.Count    -gt 0) { $lines += "- **Outros:** $($layers.Other.Count) arquivo(s)" }

    if ($lines.Count -eq 0) { return "_Nenhum arquivo identificado nas camadas conhecidas._" }

    return ($lines -join "`n")
}

$alteracoesSection = Build-AlteracoesSection -layers $layers

# Impacto Tecnico
function Build-ImpactoSection {
    param($layers, [int]$totalFiles)

    $impactos = @()

    $agentCount   = $layers.Agent.Count + $layers.Models.Count + $layers.Nodes.Count
    $analysisCount = $layers.Analysis.Count + $layers.Tools.Count + $layers.Utils.Count
    $testCount    = $layers.Tests.Count

    if ($agentCount -gt 0) { $impactos += "- **Agent LangGraph:** $agentCount arquivo(s) alterado(s) em StateGraph, models e nodes." }
    if ($analysisCount -gt 0) { $impactos += "- **Analise:** $analysisCount arquivo(s) alterado(s) em parser, detector, formatter e ferramentas." }
    if ($testCount -gt 0) { $impactos += "- **Testes:** $testCount arquivo(s) de teste adicionado(s) ou modificado(s)." }
    if ($layers.Docs.Count -gt 0) { $impactos += "- **Documentacao:** documentacao e exemplos atualizados." }
    if ($layers.Config.Count -gt 0) { $impactos += "- **Configuracao:** arquivos de config, ambiente ou CI/CD modificados." }

    $impactos += "- **Total de arquivos alterados:** $totalFiles"

    return ($impactos -join "`n")
}

$impactoSection = Build-ImpactoSection -layers $layers -totalFiles $fileList.Count

# Testes
function Build-TestesSection {
    param([string[]]$testFiles)

    if (-not $testFiles -or $testFiles.Count -eq 0) { 
        return "_Nenhum arquivo de teste identificado neste PR._" 
    }

    $lines = @()
    $lines += "**Arquivos de teste modificados:**"
    $testFiles | ForEach-Object { $lines += "- ``$_``" }
    $lines += ""
    $lines += "_Certifique-se de executar: ``pytest tests/ -v``_"

    return ($lines -join "`n")
}

$testesSection = Build-TestesSection -testFiles ([string[]]$layers.Tests)

# Commits
$commitBullets = if ($commitLines.Count -gt 0) {
    ($commitLines | ForEach-Object { "- $_" }) -join "`n"
} else {
    "- _Nenhum commit identificado alem do base._"
}

# ── 11. Montar body do PR ────────────────────────────────────────────────────
$bodyFile = [System.IO.Path]::GetTempFileName() + ".md"

$bodyContent = "## Objetivo`n`n$objetivo`n`n"
$bodyContent += "## Principais Alteracoes`n`n$alteracoesSection`n`n"
$bodyContent += "## Impacto Tecnico`n`n$impactoSection`n`n"
$bodyContent += "## Testes`n`n$testesSection`n`n"
$bodyContent += "## Evidencias`n`n"
$bodyContent += "- Issue relacionada: Closes #$issueId`n"
$bodyContent += "- Implementacao guiada por IA (Kiro) - prompts registrados em ``docs/prompts/``""`n"
$bodyContent += "- Projeto LogAnalyzer AI: agente LangGraph para analise de arquivos de log`n`n"
$bodyContent += "## Checklist`n`n"
$bodyContent += "- [ ] Codigo revisado e limpo`n"
$bodyContent += "- [ ] Testes executados com sucesso`n"
$bodyContent += "- [ ] Documentacao atualizada`n"
$bodyContent += "- [ ] Sem erros de lint ou compilacao`n"
$bodyContent += "- [ ] Build funcionando`n`n"
$bodyContent += "## Commits neste PR`n`n$commitBullets`n`n"
$bodyContent += "## Observacoes`n`n"
$bodyContent += "> _Preencher manualmente se houver riscos, limitacoes tecnicas ou proximos passos relevantes._`n"

# Gravar como UTF-8 sem BOM para evitar corrupcao de caracteres no GitHub
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($bodyFile, $bodyContent, $utf8NoBom)

# ── 12. Push da branch ───────────────────────────────────────────────────────
Write-Host "Executando push da branch '$branch'..."
git push -u origin $branch

# ── 13. Criar ou atualizar Pull Request ──────────────────────────────────────
Write-Host "Verificando se ja existe PR para esta branch..."
try {
    $existingPr = gh pr view $branch --repo $REPO --json number,url --jq '.url' 2>$null
} catch {
    $existingPr = $null
}

if ($existingPr) {
    Write-Host "PR ja existe: $existingPr"
    Write-Host "Atualizando body do PR..."
    gh pr edit $existingPr --body-file $bodyFile
    $prUrl = $existingPr
    Write-Host "Body do PR atualizado: $prUrl"
} else {
    Write-Host "Abrindo Pull Request para develop..."
    $prUrl = gh pr create `
        --repo $REPO `
        --base develop `
        --head $branch `
        --title "${commitType}: $prTitle" `
        --body-file $bodyFile

    if (-not $prUrl) {
        Write-Host "Erro ao criar PR. Verifique em: https://github.com/$REPO/pulls"
        Remove-Item -Path $bodyFile -Force
        exit 1
    }

    Write-Host "Pull Request criado: $prUrl"
    
    # ── 14. Adicionar PR ao projeto Kanban ───────────────────────────────────
    Write-Host "Adicionando PR ao projeto Kanban..."
    gh project item-add 1 --owner weltonsabino --url $prUrl
    Write-Host "PR adicionado ao Kanban com sucesso."
}

Remove-Item -Path $bodyFile -Force
Write-Host "Script concluido com sucesso."
