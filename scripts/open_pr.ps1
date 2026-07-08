#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$REPO = "weltonsabino/mini-projeto-LogAnalyzer-AI"

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

# ── 6. Determinar tipo de commit pelo prefixo da branch ──────────────────────
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

# ── 8. Coletar arquivos alterados em relacao a develop ───────────────────────
$changedFiles = $null
try { $changedFiles = git diff origin/develop..HEAD --name-only 2>$null } catch { $changedFiles = $null }
if (-not $changedFiles) {
    try { $changedFiles = git diff develop..HEAD --name-only 2>$null } catch { $changedFiles = $null }
}
$fileList = if ($changedFiles) { $changedFiles -split "`n" | Where-Object { $_.Trim() -ne "" } } else { @() }

# ── 9. Classificar arquivos por camada ───────────────────────────────────────
function Get-FilesByLayer {
    param([string[]]$files)

    $layers = @{
        Controllers = @()
        UseCases    = @()
        Services    = @()
        Domain      = @()
        DTOs        = @()
        Mappers     = @()
        Exceptions  = @()
        Persistence = @()
        Config      = @()
        Tests       = @()
        Frontend    = @()
        CiCd        = @()
        Docs        = @()
        Other       = @()
    }

    foreach ($f in $files) {
        $fn = $f.ToLower()
        if     ($fn -match 'controller')                  { $layers.Controllers += $f }
        elseif ($fn -match 'usecase|use.case')            { $layers.UseCases    += $f }
        elseif ($fn -match 'service')                     { $layers.Services    += $f }
        elseif ($fn -match 'domain/model|domain\\model')  { $layers.Domain      += $f }
        elseif ($fn -match 'dto|request|response')        { $layers.DTOs        += $f }
        elseif ($fn -match 'mapper')                      { $layers.Mappers     += $f }
        elseif ($fn -match 'exception|handler')           { $layers.Exceptions  += $f }
        elseif ($fn -match 'persistence|repository|entity') { $layers.Persistence += $f }
        elseif ($fn -match 'config|configuration')        { $layers.Config      += $f }
        elseif ($fn -match 'src/test|src\\test')          { $layers.Tests       += $f }
        elseif ($fn -match '^frontend/')                  { $layers.Frontend    += $f }
        elseif ($fn -match '\.github|\.yml|\.yaml')       { $layers.CiCd        += $f }
        elseif ($fn -match '^docs/')                      { $layers.Docs        += $f }
        else                                              { $layers.Other       += $f }
    }

    return $layers
}

$layers = Get-FilesByLayer -files $fileList

# ── 10. Detectar endpoints via diff ──────────────────────────────────────────
function Get-DetectedEndpoints {
    param([string[]]$controllerFiles)

    $endpoints = @()
    foreach ($f in $controllerFiles) {
        $currentContent = $null
        try { $currentContent = git show "HEAD:$f" 2>$null } catch { $currentContent = $null }
        if (-not $currentContent) { continue }

        $lines = $currentContent -split "`n"
        $method = ""
        foreach ($line in $lines) {
            if ($line -match '@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping)\s*\(?"?([^")\s]*)"?\)?') {
                $httpVerb = switch ($Matches[1]) {
                    "GetMapping"    { "GET" }
                    "PostMapping"   { "POST" }
                    "PutMapping"    { "PUT" }
                    "PatchMapping"  { "PATCH" }
                    "DeleteMapping" { "DELETE" }
                }
                $path = if ($Matches[2]) { $Matches[2] } else { "/" }
                $method = "$httpVerb $path"
            }
            if ($method -ne "" -and $line -match '@Operation\s*\(\s*summary\s*=\s*"([^"]+)"') {
                $endpoints += [PSCustomObject]@{ Method = $method; Summary = $Matches[1] }
                $method = ""
            }
        }
    }
    return $endpoints
}

$detectedEndpoints = Get-DetectedEndpoints -controllerFiles ([string[]]$layers.Controllers)

# ── 11. Detectar testes adicionados ──────────────────────────────────────────
function Get-TestSummary {
    param([string[]]$testFiles)

    if ($testFiles.Count -eq 0) { return $null }

    $testMethods = @()
    foreach ($f in $testFiles) {
        $content = $null
        try { $content = git show "HEAD:$f" 2>$null } catch { $content = $null }
        if (-not $content) { continue }
        $found = [regex]::Matches($content, '@Test[\s\S]*?void\s+(\w+)\s*\(')
        foreach ($m in $found) {
            $testMethods += $m.Groups[1].Value
        }
    }
    return $testMethods
}

$testMethods = Get-TestSummary -testFiles ([string[]]$layers.Tests)

# ── 12. Construir secoes do body ─────────────────────────────────────────────

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
if ($layers.Controllers.Count -gt 0) { $camadasAlteradas += "controllers" }
if ($layers.UseCases.Count    -gt 0) { $camadasAlteradas += "use cases" }
if ($layers.Services.Count    -gt 0) { $camadasAlteradas += "services" }
if ($layers.Domain.Count      -gt 0) { $camadasAlteradas += "dominio" }
if ($layers.DTOs.Count        -gt 0) { $camadasAlteradas += "DTOs" }
if ($layers.Mappers.Count     -gt 0) { $camadasAlteradas += "mappers" }
if ($layers.Exceptions.Count  -gt 0) { $camadasAlteradas += "tratamento de excecoes" }
if ($layers.Persistence.Count -gt 0) { $camadasAlteradas += "persistencia" }
if ($layers.Config.Count      -gt 0) { $camadasAlteradas += "configuracao" }
if ($layers.Tests.Count       -gt 0) { $camadasAlteradas += "testes" }
if ($layers.Frontend.Count    -gt 0) { $camadasAlteradas += "frontend" }
if ($layers.CiCd.Count        -gt 0) { $camadasAlteradas += "CI/CD" }
if ($layers.Docs.Count        -gt 0) { $camadasAlteradas += "documentacao" }

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

# Principais Alteracoes — resumo por camada (sem listar arquivos individuais)
function Build-AlteracoesSection {
    param($layers)

    $lines = @()

    if ($layers.Controllers.Count -gt 0) { $lines += "- **Backend - Controllers:** $($layers.Controllers.Count) arquivo(s)" }
    if ($layers.UseCases.Count    -gt 0) { $lines += "- **Backend - Use Cases:** $($layers.UseCases.Count) arquivo(s)" }
    if ($layers.Services.Count    -gt 0) { $lines += "- **Backend - Services:** $($layers.Services.Count) arquivo(s)" }
    if ($layers.Domain.Count      -gt 0) { $lines += "- **Dominio:** $($layers.Domain.Count) arquivo(s)" }
    if ($layers.DTOs.Count        -gt 0) { $lines += "- **DTOs (Request / Response):** $($layers.DTOs.Count) arquivo(s)" }
    if ($layers.Mappers.Count     -gt 0) { $lines += "- **Mappers:** $($layers.Mappers.Count) arquivo(s)" }
    if ($layers.Exceptions.Count  -gt 0) { $lines += "- **Exceptions / Error Handling:** $($layers.Exceptions.Count) arquivo(s)" }
    if ($layers.Persistence.Count -gt 0) { $lines += "- **Persistencia (JPA / Repository):** $($layers.Persistence.Count) arquivo(s)" }
    if ($layers.Config.Count      -gt 0) { $lines += "- **Configuracao:** $($layers.Config.Count) arquivo(s)" }
    if ($layers.Tests.Count       -gt 0) { $lines += "- **Testes:** $($layers.Tests.Count) arquivo(s)" }
    if ($layers.Frontend.Count    -gt 0) { $lines += "- **Frontend:** $($layers.Frontend.Count) arquivo(s)" }
    if ($layers.CiCd.Count        -gt 0) { $lines += "- **CI/CD:** $($layers.CiCd.Count) arquivo(s)" }
    if ($layers.Docs.Count        -gt 0) { $lines += "- **Documentacao:** $($layers.Docs.Count) arquivo(s)" }
    if ($layers.Other.Count       -gt 0) { $lines += "- **Outros:** $($layers.Other.Count) arquivo(s)" }

    if ($lines.Count -eq 0) { return "_Nenhum arquivo identificado nas camadas conhecidas._" }

    return ($lines -join "`n")
}

$alteracoesSection = Build-AlteracoesSection -layers $layers

# Impacto Tecnico
function Build-ImpactoSection {
    param($layers, [int]$totalFiles)

    $impactos = @()

    $backendCount = $layers.Controllers.Count + $layers.UseCases.Count + $layers.Services.Count + $layers.Domain.Count
    $infraCount   = $layers.Persistence.Count + $layers.Config.Count
    $testCount    = $layers.Tests.Count
    $frontCount   = $layers.Frontend.Count

    if ($backendCount -gt 0) { $impactos += "- **Backend:** $backendCount arquivo(s) alterado(s) nas camadas de API, aplicacao e dominio." }
    if ($infraCount   -gt 0) { $impactos += "- **Infraestrutura:** $infraCount arquivo(s) alterado(s) em persistencia e configuracao." }
    if ($layers.Exceptions.Count -gt 0) { $impactos += "- **Tratamento de erros:** handler(s) de excecao adicionado(s) ou modificado(s)." }
    if ($layers.Mappers.Count    -gt 0) { $impactos += "- **Mapeamento:** conversao entre camadas (DTO <-> Dominio <-> Entidade JPA) atualizada." }
    if ($testCount  -gt 0) { $impactos += "- **Testes:** $testCount arquivo(s) de teste adicionado(s) ou modificado(s)." }
    if ($frontCount -gt 0) { $impactos += "- **Frontend:** $frontCount arquivo(s) React/TypeScript alterado(s)." }
    if ($layers.CiCd.Count -gt 0) { $impactos += "- **CI/CD:** pipeline ou workflow GitHub Actions modificado." }

    $impactos += "- **Total de arquivos alterados:** $totalFiles"

    return ($impactos -join "`n")
}

$impactoSection = Build-ImpactoSection -layers $layers -totalFiles $fileList.Count

# Endpoints
function Build-EndpointsSection {
    param($endpoints, [string[]]$controllerFiles)

    if ($controllerFiles.Count -eq 0) { return $null }

    if ($endpoints.Count -gt 0) {
        $table  = "| Metodo | Endpoint | Descricao |`n"
        $table += '|--------|----------|-----------|' + "`n"
        foreach ($ep in $endpoints) {
            $parts = $ep.Method -split ' ', 2
            $verb  = $parts[0]
            $path  = if ($parts.Count -gt 1) { $parts[1] } else { "/" }
            $table += "| ``$verb`` | ``$path`` | $($ep.Summary) |`n"
        }
        return $table
    }

    $lines = $controllerFiles | ForEach-Object { "- ``$_``" }
    return ("Controllers modificados (endpoints nao detectados automaticamente):`n" + ($lines -join "`n"))
}

$endpointsSection = Build-EndpointsSection -endpoints $detectedEndpoints -controllerFiles ([string[]]$layers.Controllers)

# Testes
function Build-TestesSection {
    param([string[]]$testFiles, [string[]]$methods)

    if ($testFiles.Count -eq 0) { return "_Nenhum arquivo de teste identificado neste PR._" }

    $lines = @()
    $lines += "**Arquivos de teste:**"
    $testFiles | ForEach-Object { $lines += "- ``$_``" }

    if ($methods -and $methods.Count -gt 0) {
        $lines += ""
        $lines += "**Cenarios validados:**"
        $methods | Select-Object -First 10 | ForEach-Object { $lines += "- ``$_``" }
        if ($methods.Count -gt 10) {
            $lines += "- _... e mais $($methods.Count - 10) cenario(s)_"
        }
    }

    return ($lines -join "`n")
}

$testesSection = Build-TestesSection -testFiles ([string[]]$layers.Tests) -methods $testMethods

# Commits
$commitBullets = if ($commitLines.Count -gt 0) {
    ($commitLines | ForEach-Object { "- $_" }) -join "`n"
} else {
    "- _Nenhum commit identificado alem do base._"
}

# ── 13. Montar body do PR ────────────────────────────────────────────────────
$bodyFile = [System.IO.Path]::GetTempFileName() + ".md"

$endpointsBlock = if ($endpointsSection) {
    "## Endpoints Alterados`n`n$endpointsSection"
} else { "" }

$bodyContent = "## Objetivo`n`n$objetivo`n`n"
$bodyContent += "## Principais Alteracoes`n`n$alteracoesSection`n`n"
$bodyContent += "## Impacto Tecnico`n`n$impactoSection`n`n"
if ($endpointsBlock) { $bodyContent += "$endpointsBlock`n`n" }
$bodyContent += "## Testes`n`n$testesSection`n`n"
$bodyContent += "## Evidencias`n`n"
$bodyContent += "- Issue relacionada: Closes #$issueId`n"
$bodyContent += "- Implementacao guiada por IA (Kiro) - prompts registrados em ``docs/prompts/```n"
$bodyContent += "- Projeto avaliativo: demonstracao de Clean Architecture + Hexagonal + SOLID com suporte de IA generativa`n`n"
$bodyContent += "## Checklist`n`n"
$bodyContent += "- [ ] Codigo revisado e limpo`n"
$bodyContent += "- [ ] Testes executados com sucesso`n"
$bodyContent += "- [ ] Documentacao atualizada`n"
$bodyContent += "- [ ] Swagger atualizado (quando aplicavel)`n"
$bodyContent += "- [ ] Sem erros de lint ou compilacao`n"
$bodyContent += "- [ ] Build funcionando no CI`n`n"
$bodyContent += "## Commits neste PR`n`n$commitBullets`n`n"
$bodyContent += "## Observacoes`n`n"
$bodyContent += "> _Preencher manualmente se houver riscos, limitacoes tecnicas ou proximos passos relevantes._`n"

# Gravar como UTF-8 sem BOM para evitar corrupcao de caracteres no GitHub
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($bodyFile, $bodyContent, $utf8NoBom)

# ── 14. Push da branch ───────────────────────────────────────────────────────
Write-Host "Executando push da branch '$branch'..."
git push -u origin $branch

# ── 15. Criar ou atualizar Pull Request ──────────────────────────────────────
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

    # ── 16. Adicionar PR ao projeto Kanban ───────────────────────────────────
    Write-Host "Adicionando PR ao projeto Kanban..."
    gh project item-add 19 --owner IA-para-DEVs-SCTEC-T2 --url $prUrl
    Write-Host "PR adicionado ao Kanban com sucesso."
}

Remove-Item -Path $bodyFile -Force
