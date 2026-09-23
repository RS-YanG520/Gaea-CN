#Requires -Version 5.1
<#
.SYNOPSIS
  Backup install Nodes.json (once) and copy overlays/Nodes.json over it.
#>
param(
    [string]$GaeaRoot = "D:\Program Files\Gaea 2",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$target = Join-Path $GaeaRoot "Resources\Nodes.json"
$overlay = Join-Path $RepoRoot "overlays\Nodes.json"
$backupDir = Join-Path $RepoRoot "backups"
$backup = Join-Path $backupDir "Nodes.json.bak"

if (-not (Test-Path $overlay)) {
    throw "Overlay missing: $overlay — run python tools/build_overlay.py first"
}
if (-not (Test-Path $target)) {
    throw "Install Nodes.json missing: $target"
}

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

if (-not (Test-Path $backup)) {
    Copy-Item -LiteralPath $target -Destination $backup -Force
    Write-Host "Created backup: $backup"
} else {
    Write-Host "Backup already exists: $backup"
}

Copy-Item -LiteralPath $overlay -Destination $target -Force
Write-Host "Applied overlay -> $target"
Write-Host "Size: $((Get-Item -LiteralPath $target).Length) bytes"
