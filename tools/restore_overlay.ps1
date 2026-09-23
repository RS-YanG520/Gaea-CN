#Requires -Version 5.1
<#
.SYNOPSIS
  Restore Resources\Nodes.json from backups/Nodes.json.bak
#>
param(
    [string]$GaeaRoot = "D:\Program Files\Gaea 2",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$target = Join-Path $GaeaRoot "Resources\Nodes.json"
$backup = Join-Path $RepoRoot "backups\Nodes.json.bak"

if (-not (Test-Path $backup)) {
    throw "Backup missing: $backup"
}
if (-not (Test-Path (Split-Path $target -Parent))) {
    throw "Gaea Resources folder missing under $GaeaRoot"
}

Copy-Item -LiteralPath $backup -Destination $target -Force
Write-Host "Restored $backup -> $target"
Write-Host "Size: $((Get-Item -LiteralPath $target).Length) bytes"
