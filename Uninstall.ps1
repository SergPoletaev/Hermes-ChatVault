# Public Hermes ChatVault uninstall - Windows; removes only the manual copy.
[CmdletBinding()]
param([string]$HermesHome = '')
$ErrorActionPreference = 'Stop'
try {
    if ($HermesHome) { $resolvedHermesHome = [Environment]::ExpandEnvironmentVariables($HermesHome) }
    elseif ($env:HERMES_HOME) { $resolvedHermesHome = $env:HERMES_HOME }
    else {
        $choices = @()
        if ($env:LOCALAPPDATA) { $choices += (Join-Path $env:LOCALAPPDATA 'hermes') }
        if ($env:USERPROFILE) { $choices += (Join-Path $env:USERPROFILE '.hermes') }
        $existing = @($choices | Where-Object { Test-Path -LiteralPath $_ -PathType Container } | Select-Object -Unique)
        if ($existing.Count -ne 1) { throw 'Hermes home not unique or missing. Pass -HermesHome <path>.' }
        $resolvedHermesHome = $existing[0]
    }
    $folder = Join-Path (Join-Path $resolvedHermesHome 'desktop-plugins') 'hermes-chat-vault'
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) { Write-Host 'ChatVault not installed'; exit 0 }
    if ((Get-Item -LiteralPath $folder -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Plugin directory is a link/junction; refusing delete.' }
    if (Test-Path -LiteralPath (Join-Path $folder '.hermes-package.json')) { throw 'Managed install: uninstall via Hermes Capabilities.' }
    if (Test-Path -LiteralPath (Join-Path $folder '.git')) { throw 'Git-managed install: uninstall via Hermes Capabilities.' }
    $dest = Join-Path $folder 'plugin.js'
    if (-not (Test-Path -LiteralPath $dest -PathType Leaf)) { Write-Host 'ChatVault plugin.js not present'; exit 0 }
    $code = [System.IO.File]::ReadAllText($dest, [System.Text.Encoding]::UTF8)
    if (-not ($code.Contains("const PLUGIN_ID = 'hermes-chat-vault'") -and $code.Contains('HERMES_CHATVAULT_FORK_V1'))) { throw 'Unknown plugin: no file deleted.' }
    Remove-Item -LiteralPath $dest -Force
    Write-Host 'UNINSTALL SUCCESS: manual ChatVault plugin removed.' -ForegroundColor Green
    Write-Host 'Backups and other files retained. Restart or reload Desktop plugins.'
} catch { Write-Host ('UNINSTALL FAILED: ' + $_.Exception.Message) -ForegroundColor Red; exit 1 }
