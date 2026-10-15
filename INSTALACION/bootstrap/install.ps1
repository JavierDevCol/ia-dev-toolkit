# Bootstrap de DIAT (ia-dev-toolkit) para Windows.
# Descarga el CLI y lo deja invocable como `diat`.
#
# DIAT_REF solo como argumento del bootstrap y SOLO tags de release o de
# prueba (R8/R9):
#
#   irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
#       -> instala la última release publicada (vX.Y.Z)
#
#   $env:DIAT_REF="v2.2.0-TEST"; irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
#       -> instala un tag explícito (release vX.Y.Z o de prueba vX.Y.Z-TEST)
#
$ErrorActionPreference = "Stop"

$Owner = "JavierDevCol"
$Repo  = "ia-dev-toolkit"
$CliDir = "INSTALACION"

$Bin   = Join-Path $env:LOCALAPPDATA "ia-dev-toolkit\bin"
$Cache = Join-Path $env:LOCALAPPDATA "ia-dev-toolkit"

function Write-Ok($m)   { Write-Host "OK  $m" -ForegroundColor Green }
function Write-Err($m)  { Write-Host "ERR $m" -ForegroundColor Red }
function Write-Warn($m) { Write-Host "WARN $m" -ForegroundColor Yellow }

# StatusCode HTTP de un fallo de Invoke-RestMethod (PS 5.x y 7+); $null si es fallo de red.
function Get-HttpStatusCode($err) {
    $resp = $err.Exception.Response
    if ($resp -and $resp.StatusCode) {
        try { return [int]$resp.StatusCode } catch { }
    }
    return $null
}

# B1/R9: $fromEnv=$true (vino de DIAT_REF) -> canal vX.Y.Z[-TEST];
#        $fromEnv=$false (resuelto de la API) -> estable estricto, jamás -TEST.
function Validate-RefFormat([string]$ref, [bool]$fromEnv) {
    $pattern = if ($fromEnv) { '^v\d+\.\d+\.\d+(-TEST)?$' } else { '^v\d+\.\d+\.\d+$' }
    return $ref -cmatch $pattern   # -cmatch: case-sensitive como [[ =~ ]] en install.sh (rechaza -test / V1.2.3)
}

# B3/R8: última release publicada (GET /releases/latest -> tag_name).
function Resolve-LatestRelease {
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases/latest" `
        -Headers @{ Accept = "application/vnd.github+json" } -UserAgent "diat-bootstrap" -TimeoutSec 30
    return [string]$release.tag_name
}

# G3/B6: existencia del tag ANTES de descargar (solo tags explícitos).
function Test-TagExists {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/git/ref/tags/$Ref" `
        -Headers @{ Accept = "application/vnd.github+json" } -UserAgent "diat-bootstrap" -TimeoutSec 30 | Out-Null
}

Write-Host ""
Write-Host "                     AI DEVELOPER TOOLKIT" -ForegroundColor Cyan
Write-Host "        Skills - Agents - Workflows - Tools - Commands" -ForegroundColor Cyan
Write-Host ""

# 1) Leer DIAT_REF; resolver canal; validar formato (B1/B3/B14/R8/R9)
$RefFromEnv = [bool] "$($env:DIAT_REF)".Trim()
$Ref = "$($env:DIAT_REF)".Trim()
$env:DIAT_REF = $null                       # B2: nunca invocar diat con la env puesta
if (-not $RefFromEnv) {
    try {
        $Ref = Resolve-LatestRelease
    } catch {
        if ((Get-HttpStatusCode $_) -eq 404) {
            Write-Err "No hay releases publicadas en $Owner/$Repo. Publica una release (vX.Y.Z) o instala con DIAT_REF=vX.Y.Z-TEST."
        } else {
            Write-Err "No se pudo resolver la última release (red/permisos). Reintenta."
        }
        exit 1
    }
}
if (-not (Validate-RefFormat $Ref $RefFromEnv)) {
    Write-Err "DIAT_REF solo acepta tags vX.Y.Z o vX.Y.Z-TEST. Recibido: '$Ref'. Para la última release, ejecuta sin DIAT_REF."
    exit 1
}

# 2. Requisitos
Write-Host "Verificando requisitos previos..."
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { Write-Err "Python no encontrado. Instalalo y reintenta."; exit 1 }
Write-Ok ("Python encontrado: " + (& $py.Source --version))

# 3) Existencia del tag explícito (G3/B6); si es la última release ya vino de la API
if ($RefFromEnv) {
    try {
        Test-TagExists
    } catch {
        $code = Get-HttpStatusCode $_
        if ($code -eq 404) {
            Write-Err "El tag '$Ref' no existe en $Owner/$Repo. Publícalo (git tag $Ref && git push --tags) o corrige el nombre. No se descargó nada."
            exit 1
        } elseif ($null -ne $code) {
            Write-Warn "No se pudo verificar el tag (rate-limit/permisos); continúo..."
        } else {
            Write-Warn "Sin conexión a la API; continúo (la descarga decidirá)..."
        }
    }
}

# 4) [P] cambio de canal sobre instalación existente (G7/B10)
$oldRef = (Get-Content (Join-Path $Cache ".ref") -ErrorAction SilentlyContinue)
if ((Test-Path (Join-Path $Bin "diat")) -and ($oldRef -ne $Ref)) {
    $oldDisplay = if ($oldRef) { $oldRef } else { "canal desconocido" }
    try { $ans = Read-Host " Canal actual: '$oldDisplay' → nuevo: '$Ref'. ¿Continuar? [s/N]" }
    catch { Write-Err "Sin terminal interactiva no puedo confirmar el cambio de canal. Ejecuta desde una terminal."; exit 1 }
    if ($ans -notmatch '^(s|y)') { Write-Host "Cancelado. El canal sigue en '$oldDisplay'."; exit 0 }
}

# 5. Descargar CLI (tarball, 1 request)
Write-Host "Instalando diat..."
$tmp = Join-Path $env:TEMP ("diat-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
try {
    $url = "https://codeload.github.com/$Owner/$Repo/tar.gz/$Ref"
    if ($RefFromEnv -and $Ref -clike "*-TEST") { Write-Host "Canal de prueba: instalando desde ref '$Ref'" -ForegroundColor Yellow }
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

# 6) Estado del canal antes del mensaje de éxito (G4/B15): .ref siempre;
#    .version = espejo del tag; .sha NUNCA (lo escribe quien descarga).
New-Item -ItemType Directory -Path $Cache -Force | Out-Null
Set-Content (Join-Path $Cache ".ref") $Ref
Set-Content (Join-Path $Cache ".version") $Ref.Substring(1)

# 7. Garantizar PATH (usuario; idempotente)
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
