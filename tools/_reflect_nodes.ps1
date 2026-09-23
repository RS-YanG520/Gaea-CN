$ErrorActionPreference = 'Stop'
$asm = [Reflection.Assembly]::LoadFrom('D:\Program Files\Gaea 2\Gaea.Nodes.dll')
Write-Host $asm.FullName
function Find-Type([string]$name) {
  foreach ($t in $asm.GetTypes()) {
    if ($t.Name -eq $name) { return $t }
  }
  return $null
}
foreach ($n in @('Mountain','Erosion2','Combine')) {
  $t = Find-Type $n
  Write-Host ""
  Write-Host "=== $n : $($t.FullName) ==="
  if ($null -eq $t) { continue }
  Write-Host "Base:" $t.BaseType.FullName
  foreach ($a in $t.GetCustomAttributes($true)) {
    Write-Host "Attr:" $a.GetType().FullName "|" $a
  }
}
