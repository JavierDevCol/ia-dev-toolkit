# Bootstrap de DIAT (ia-dev-toolkit) para Windows.
# Descarga el CLI y lo deja invocable como `diat`.
#
#   irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALADOR-DOS/bootstrap/install.ps1 | iex
#
$ErrorActionPreference = "Stop"

$Owner  = "JavierDevCol"
$Repo   = "ia-dev-toolkit"
$Ref    = "main"
$CliDir = "INSTALADOR-DOS"          # cutover -> INSTALACION

$Bin   = Join-Path $env:LOCALAPPDATA "ia-dev-toolkit\bin"
$Cache = Join-Path $env:LOCALAPPDATA "ia-dev-toolkit"

function Write-Ok($m)   { Write-Host "OK  $m" -ForegroundColor Green }
function Write-Err($m)  { Write-Host "ERR $m" -ForegroundColor Red }

Write-Host ""
Write-Host "                     AI DEVELOPER TOOLKIT" -ForegroundColor Cyan
Write-Host "        Skills - Agents - Workflows - Tools - Commands" -ForegroundColor Cyan
Write-Host ""

# 1. Requisitos
Write-Host "Verificando requisitos previos..."
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { Write-Err "Python no encontrado. Instalalo y reintenta."; exit 1 }
Write-Ok ("Python encontrado: " + (& $py.Source --version))

# 2. Descargar CLI (tarball, 1 request)
Write-Host "Instalando diat..."
$tmp = Join-Path $env:TEMP ("diat-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
try {
    $url = "https://codeload.github.com/$Owner/$Repo/tar.gz/$Ref"
    $tgz = Join-Path $tmp "repo.tar.gz"
    Invoke-WebRequest -Uri $url -OutFile $tgz -UseBasicParsing
    tar -xzf $tgz -C $tmp

    # La carpeta raiz extraida se descubre (robusto ante refs con '/')
    $root = Get-ChildItem -Path $tmp -Directory | Select-Object -First 1
    $src = Join-Path $root.FullName $CliDir
    if (-not (Test-Path (Join-Path $src "diat"))) {
        Write-Err "No se encontro el CLI en el repo ($CliDir)."; exit 1
    }

    New-Item -ItemType Directory -Path $Bin -Force | Out-Null
    Copy-Item (Join-Path $src "diat")     (Join-Path $Bin "diat")     -Force
    Copy-Item (Join-Path $src "diat.bat") (Join-Path $Bin "diat.bat") -Force
    $pkgDst = Join-Path $Bin "diatlib"
    if (Test-Path $pkgDst) { Remove-Item $pkgDst -Recurse -Force }
    Copy-Item (Join-Path $src "diatlib") $pkgDst -Recurse -Force
    Write-Ok "diat instalado"
}
finally {
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

# 3. Garantizar PATH (usuario; idempotente)
Write-Host "Verificando PATH..."
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($null -eq $userPath) { $userPath = "" }
$parts = $userPath.Split(';') | Where-Object { $_ -ne "" }
if ($parts -notcontains $Bin) {
    $new = ($parts + $Bin) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $new, "User")
    Write-Ok "PATH configurado"
} else {
    Write-Ok "PATH ya configurado"
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  DIAT - IA DEV TOOLKIT INSTALADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos: diat | diat --install | diat --help"
Write-Host ""
Write-Host "IMPORTANTE: abre una terminal nueva para que tome efecto." -ForegroundColor Yellow
Write-Host ""
