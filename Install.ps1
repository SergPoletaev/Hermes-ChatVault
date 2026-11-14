# Public Hermes ChatVault installer - Windows; no fixed user paths.
[CmdletBinding()]
param([string]$HermesHome = '')
$ErrorActionPreference = 'Stop'
function Resolve-HermesHome([string]$Explicit) {
    if ($Explicit) { $choice = [Environment]::ExpandEnvironmentVariables($Explicit) }
    elseif ($env:HERMES_HOME) { $choice = [Environment]::ExpandEnvironmentVariables($env:HERMES_HOME) }
    else {
        $candidates = @()
        if ($env:LOCALAPPDATA) { $candidates += (Join-Path $env:LOCALAPPDATA 'hermes') }
        if ($env:USERPROFILE) { $candidates += (Join-Path $env:USERPROFILE '.hermes') }
        $existing = @($candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Container } | Select-Object -Unique)
        if ($existing.Count -eq 0) { throw 'Hermes home not found. Install Hermes first, use Install from Git, or pass -HermesHome <path>.' }
        if ($existing.Count -gt 1) { throw 'Multiple Hermes homes found. Pass -HermesHome <path> to choose the correct one.' }
        $choice = $existing[0]
    }
    if (-not (Test-Path -LiteralPath $choice -PathType Container)) { throw "Hermes home does not exist: $choice" }
    return (Resolve-Path -LiteralPath $choice).ProviderPath
}
try {
    $from = Join-Path $PSScriptRoot 'plugin.js'
    if (-not (Test-Path -LiteralPath $from -PathType Leaf)) { throw 'Missing root plugin.js. Extract the full release ZIP.' }
    $src = [System.IO.File]::ReadAllText($from, [System.Text.Encoding]::UTF8)
    if (-not ($src.Contains("const PLUGIN_VERSION = '0.2.2-vault'") -and
               $src.Contains("const PLUGIN_ID = 'hermes-chat-vault'") -and
               $src.Contains('HERMES_CHAT_SHARE_EMBED_MEDIA_V1') -and
               $src.Contains('function VaultBanner'))) { throw 'Plugin validation failed; refusing install.' }
    $resolvedHermesHome = Resolve-HermesHome $HermesHome
    $destDir = Join-Path (Join-Path $resolvedHermesHome 'desktop-plugins') 'hermes-chat-vault'
    if ((Test-Path -LiteralPath $destDir) -and ((Get-Item -LiteralPath $destDir -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Plugin directory is a link/junction; refusing write.' }
    if (-not (Test-Path -LiteralPath $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    if (Test-Path -LiteralPath (Join-Path $destDir '.hermes-package.json')) { throw 'This is a managed plugin; update it from Hermes Capabilities instead.' }
    if (Test-Path -LiteralPath (Join-Path $destDir '.git')) { throw 'This is a Git-managed directory; use Hermes plugin management.' }
    $dest = Join-Path $destDir 'plugin.js'
    if (Test-Path -LiteralPath $dest -PathType Leaf) {
        $old = [System.IO.File]::ReadAllText($dest,[System.Text.Encoding]::UTF8)
        if (-not $old.Contains("const PLUGIN_ID = 'hermes-chat-vault'")) { throw 'Different plugin at destination; nothing overwritten.' }
        $backup = Join-Path $destDir ('plugin.js.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.bak')
        Copy-Item -LiteralPath $dest -Destination $backup -ErrorAction Stop
        Write-Host "Backup: $backup"
    }
    $tmp = Join-Path $destDir 'plugin.js.new'
    try {
        Copy-Item -LiteralPath $from -Destination $tmp -Force
        if ((Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $from -Algorithm SHA256).Hash) { throw 'Staged file checksum differs.' }
        Move-Item -LiteralPath $tmp -Destination $dest -Force
    } finally { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
    Write-Host 'INSTALL SUCCESS: Hermes ChatVault 0.2.2' -ForegroundColor Green
    Write-Host "Installed: $dest"
    Write-Host 'Restart Hermes Desktop or use Reload desktop plugins.'
} catch {
    Write-Host ('INSTALL FAILED: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
