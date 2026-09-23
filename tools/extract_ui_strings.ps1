#Requires -Version 5.1
<#
.SYNOPSIS
  Extract printable UI-like UTF-16 strings from Gaea.dll into dict/ui.shell.zh.json skeleton.
  Phase 3 helper — does not patch the DLL.
#>
param(
    [string]$DllPath = "D:\Program Files\Gaea 2\Gaea.dll",
    [string]$OutPath = ""
)

$ErrorActionPreference = "Stop"
if (-not $OutPath) {
    $OutPath = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path "dict\ui.shell.zh.json"
}

if (-not (Test-Path $DllPath)) {
    throw "DLL not found: $DllPath"
}

$bytes = [IO.File]::ReadAllBytes($DllPath)
$set = New-Object 'System.Collections.Generic.HashSet[string]'
$list = New-Object System.Collections.Generic.List[string]

for ($i = 0; $i -lt $bytes.Length - 1 -and $list.Count -lt 2000; $i++) {
    if ($bytes[$i] -ge 0x20 -and $bytes[$i] -le 0x7E -and $bytes[$i + 1] -eq 0) {
        $j = $i
        $sb = New-Object System.Text.StringBuilder
        while ($j -lt $bytes.Length - 1 -and $bytes[$j] -ge 0x20 -and $bytes[$j] -le 0x7E -and $bytes[$j + 1] -eq 0) {
            [void]$sb.Append([char]$bytes[$j])
            $j += 2
        }
        if ($sb.Length -ge 8 -and $sb.Length -le 120) {
            $s = $sb.ToString()
            if (($s.Contains(" ") -or $s.Contains("&")) -and [char]::IsLetter($s[0])) {
                if ($set.Add($s)) { $list.Add($s) }
            }
        }
        $i = $j
    }
}

$entries = [ordered]@{}
foreach ($s in ($list | Sort-Object)) {
    $entries[$s] = ""
}

$obj = [ordered]@{
    version = 1
    policy  = "Display-only UI strings. zh empty until translated. Do not binary-patch DLL."
    source  = $DllPath
    count   = $entries.Count
    strings = $entries
}

$dir = Split-Path $OutPath -Parent
New-Item -ItemType Directory -Path $dir -Force | Out-Null
$json = $obj | ConvertTo-Json -Depth 5
# ConvertTo-Json escapes unicode; write UTF-8
[IO.File]::WriteAllText($OutPath, $json, [Text.UTF8Encoding]::new($false))
Write-Host "Wrote $OutPath ($($entries.Count) strings)"
