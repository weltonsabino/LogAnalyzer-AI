# Script de Registro de Prompts para LogAnalyzer AI
# Registra prompts em docs/prompts/ com metadados completos

param(
    [string]$prompt_text,
    [string]$author_name
)

# ============================================
# Configurações
# ============================================

$base_path = (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$prompts_dir = Join-Path $base_path "docs/prompts"
$min_char_count = 250

# ============================================
# Funções Auxiliares
# ============================================

function Test-PromptRelevance {
    param([string]$text)
    
    # Validar comprimento mínimo
    if ($text.Length -le $min_char_count) {
        return $false
    }
    
    # Validar que é pedido de implementação/documentação
    $implementation_keywords = @(
        "implementar", "criar", "adicionar", "modificar", "alterar",
        "corrigir", "fix", "documentar", "atualizar", "remover",
        "refatorar", "configure", "configure", "implement", "create",
        "add", "modify", "update", "remove", "document"
    )
    
    $text_lower = $text.ToLower()
    $has_implementation_intent = $implementation_keywords | Where-Object { $text_lower -contains $_ } | Measure-Object | Select-Object -ExpandProperty Count
    
    if ($has_implementation_intent -eq 0) {
        return $false
    }
    
    return $true
}

function Get-AuthorName {
    # Tentar extrair de prompt (por <nome>)
    if ($prompt_text -match "por <([^>]+)>") {
        return $matches[1]
    }
    
    # Tentar git config
    $git_name = & git config user.name 2>$null
    if ($LASTEXITCODE -eq 0 -and $git_name) {
        return $git_name
    }
    
    # Default
    return "nao-identificado"
}

function Sanitize-UserIdentifier {
    param([string]$name)
    
    $sanitized = $name.ToLower()
    $sanitized = $sanitized -replace " ", "-"
    $sanitized = $sanitized -replace "[/\\:*?`"<>|]", ""
    
    return $sanitized
}

function Get-CurrentTimestamp {
    # Timestamp format: yyyy-MM-dd_HH-mm-ss
    return (Get-Date -Format "yyyy-MM-dd_HH-mm-ss")
}

function Get-CurrentDateTime {
    # DateTime format para arquivo: YYYY-MM-DD HH:MM:SS
    return (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}

function Create-PromptSummary {
    param([string]$text)
    
    # Extrai primeiras palavras até 100 caracteres
    $words = $text -split "\s+"
    $summary = ""
    $char_count = 0
    
    foreach ($word in $words) {
        if (($char_count + $word.Length + 1) -gt 100) {
            break
        }
        $summary += $word + " "
        $char_count += $word.Length + 1
    }
    
    return $summary.Trim()
}

function Ensure-PromptDirectory {
    if (-not (Test-Path $prompts_dir)) {
        New-Item -ItemType Directory -Force -Path $prompts_dir | Out-Null
    }
}

function Register-Prompt {
    # ============================================
    # 1. Validar Filtro de Relevância
    # ============================================
    
    if (-not (Test-PromptRelevance $prompt_text)) {
        Write-Host "[HOOK] Prompt ignorado: não atende critérios de relevância"
        exit 0
    }
    
    # ============================================
    # 2. Extrair Metadados
    # ============================================
    
    $author = Get-AuthorName
    $user_id = Sanitize-UserIdentifier $author
    $timestamp = Get-CurrentTimestamp
    $datetime = Get-CurrentDateTime
    $summary = Create-PromptSummary $prompt_text
    
    # ============================================
    # 3. Criar Estrutura do Arquivo
    # ============================================
    
    Ensure-PromptDirectory
    
    $filename = "$timestamp`_$user_id.md"
    $filepath = Join-Path $prompts_dir $filename
    
    # Verificar se arquivo existe (garantir unicidade)
    if (Test-Path $filepath) {
        # Adicionar UUID curto se houver conflito
        $uuid_short = ([guid]::NewGuid().ToString().Substring(0, 8))
        $filename = "$timestamp`_$user_id`_$uuid_short.md"
        $filepath = Join-Path $prompts_dir $filename
    }
    
    # ============================================
    # 4. Construir Conteúdo
    # ============================================
    
    $content = @"
Prompt: $summary
Responsável: $author
Usuário: $user_id
Data/hora: $datetime

## Prompt original

$prompt_text
"@
    
    # ============================================
    # 5. Persistir Arquivo
    # ============================================
    
    try {
        Set-Content -Path $filepath -Value $content -Encoding UTF8
        
        if (Test-Path $filepath) {
            Write-Host "[HOOK] ✅ Prompt registrado: $filename"
            exit 0
        } else {
            Write-Host "[HOOK] ❌ Falha ao criar arquivo: $filename"
            exit 1
        }
    } catch {
        Write-Host "[HOOK] ❌ Erro ao persistir prompt: $_"
        exit 1
    }
}

# ============================================
# Executar Registro
# ============================================

Register-Prompt
