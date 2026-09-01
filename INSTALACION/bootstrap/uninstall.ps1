# Desinstalador de DIAT (ia-dev-toolkit) para Windows.
# Elimina el CLI del bin, el cache y la entrada de PATH.
$ErrorActionPreference = "Stop"

$Bin   = Join-Path $env:LOCALAPPDATA "ia-dev-toolkit\bin"
$Cache = Join-Path $env:LOCALAPPDATA "ia-dev-toolkit"

function Write-Ok($m) { Write-Host "OK  $m" -ForegroundColor Green }

Write-Host "Desinstalando DIAT..."

# 1. CLI + cache (bin está dentro de cache en Windows, se borra todo)
if (Test-Path $Cache) { Remove-Item $Cache -Recurse -Force }
Write-Ok "CLI y cache eliminados ($Cache)"

# 2. Quitar el bin del PATH de usuario
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath) {
    $parts = $userPath.Split(';') | Where-Object { $_ -ne "" -and $_ -ne $Bin }
    [Environment]::SetEnvironmentVariable("Path", ($parts -join ';'), "User")
    Write-Ok "PATH limpiado"
}

Write-Host ""
Write-Host "Abre una terminal nueva para completar la desinstalacion." -ForegroundColor Yellow
Write-Host ""
