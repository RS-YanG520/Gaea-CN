#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Install Gaea-CN like 星空汉化: wrap Gaea.exe, keep real binary as Gaea.real.exe.

.DESCRIPTION
  - Builds StartupHook + Launcher
  - Imports dict/xingkong into ui.display.zh.json
  - Copies hook + zh-dict to %LOCALAPPDATA%\Gaea-CN and <Gaea>\GaeaCn\
  - Backs up Gaea.exe -> Gaea.real.exe (once)
  - Replaces Gaea.exe with GaeaCn.Launcher.exe

.PARAMETER GaeaRoot
  Gaea 2 install folder (contains Gaea.exe). Default: from config/launcher.json or
  "D:\Program Files\Gaea 2"

.PARAMETER Uninstall
  Restore Gaea.real.exe -> Gaea.exe and remove GaeaCn folder / LocalAppData payload.
#>
param(
    [string]$GaeaRoot = "",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not (Test-Path (Join-Path $Repo "hooks\GaeaCn.StartupHook"))) {
    throw "Cannot locate repo root from $PSScriptRoot"
}
Write-Host "Repo: $Repo"

function Get-DefaultGaeaRoot {
    $cfg = Join-Path $Repo "config\launcher.json"
    if (Test-Path $cfg) {
        try {
            $j = Get-Content $cfg -Raw | ConvertFrom-Json
            if ($j.gaea_root -and (Test-Path $j.gaea_root)) { return [string]$j.gaea_root }
        } catch {}
    }
    foreach ($c in @("D:\Program Files\Gaea 2", "C:\Program Files\Gaea 2")) {
        if (Test-Path (Join-Path $c "Gaea.exe")) { return $c }
    }
    return ""
}

if (-not $GaeaRoot) { $GaeaRoot = Get-DefaultGaeaRoot }
if (-not $GaeaRoot -or -not (Test-Path (Join-Path $GaeaRoot "Gaea.exe"))) {
    throw "GaeaRoot invalid. Pass -GaeaRoot 'D:\Program Files\Gaea 2'"
}

$Local = Join-Path $env:LOCALAPPDATA "Gaea-CN"
$GaeaCnDir = Join-Path $GaeaRoot "GaeaCn"
$Real = Join-Path $GaeaRoot "Gaea.real.exe"
$GaeaExe = Join-Path $GaeaRoot "Gaea.exe"

if ($Uninstall) {
    Write-Host "Uninstalling Gaea-CN wrapper from $GaeaRoot"
    Get-Process Gaea, GaeaCn.Launcher -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    if (Test-Path $Real) {
        Copy-Item $Real $GaeaExe -Force
        Write-Host "Restored Gaea.exe from Gaea.real.exe"
    } else {
        Write-Warning "Gaea.real.exe missing — Gaea.exe left as-is"
    }
    if (Test-Path $GaeaCnDir) { Remove-Item $GaeaCnDir -Recurse -Force }
    Write-Host "Left %LOCALAPPDATA%\Gaea-CN in place (dictionaries/logs). Delete manually if desired."
    Write-Host "Done."
    exit 0
}

Write-Host "Importing 星空 dictionaries..."
python (Join-Path $Repo "tools\import_xingkong_dict.py")

Write-Host "Building StartupHook..."
$pub = Join-Path $Repo "hooks\publish2"
New-Item -ItemType Directory -Force -Path $pub | Out-Null
dotnet build (Join-Path $Repo "hooks\GaeaCn.StartupHook\GaeaCn.StartupHook.csproj") -c Release -o $pub --nologo
if ($LASTEXITCODE -ne 0) { throw "StartupHook build failed" }

Write-Host "Building Launcher..."
$pubL = Join-Path $Repo "hooks\publish-launcher"
New-Item -ItemType Directory -Force -Path $pubL | Out-Null
dotnet build (Join-Path $Repo "hooks\GaeaCn.Launcher\GaeaCn.Launcher.csproj") -c Release -o $pubL --nologo
if ($LASTEXITCODE -ne 0) { throw "Launcher build failed" }

Write-Host "Staging payload -> $Local and $GaeaCnDir"
foreach ($dest in @($Local, $GaeaCnDir)) {
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $pub "GaeaCn.StartupHook.dll") $dest -Force
    Copy-Item (Join-Path $Repo "dict\ui.display.zh.json") $dest -Force
    if (Test-Path (Join-Path $Repo "dict\ui.protected.json")) {
        Copy-Item (Join-Path $Repo "dict\ui.protected.json") $dest -Force
    }
    $zh = Join-Path $dest "zh-dict"
    New-Item -ItemType Directory -Force -Path $zh | Out-Null
    Copy-Item (Join-Path $Repo "dict\xingkong\*.txt") $zh -Force
}

# Ensure Gaea is not running
Get-Process Gaea -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

if (-not (Test-Path $Real)) {
    Write-Host "Backing up Gaea.exe -> Gaea.real.exe"
    Copy-Item $GaeaExe $Real -Force
} else {
    Write-Host "Gaea.real.exe already exists — keeping it"
}

Write-Host "Installing launcher as Gaea.exe"
Copy-Item (Join-Path $pubL "GaeaCn.Launcher.exe") $GaeaExe -Force
Copy-Item (Join-Path $pubL "GaeaCn.Launcher.exe") (Join-Path $GaeaCnDir "GaeaCn.Launcher.exe") -Force

Write-Host ""
Write-Host "OK. Double-click the normal Gaea shortcut — Chinese hook will load."
Write-Host "Uninstall: powershell -ExecutionPolicy Bypass -File tools\install_gaea_cn.ps1 -Uninstall"
