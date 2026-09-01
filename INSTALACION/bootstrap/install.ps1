# ============================================
# ia-dev-toolkit — Instalador Bootstrap para Windows
# ============================================
#
# Uso:
#   irm https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
#
# O descargando primero:
#   Invoke-WebRequest -Uri "https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1" -OutFile install.ps1
#   Get-Content install.ps1
#   .\install.ps1
#

# ============================================
# CONFIGURACIÓN
# ============================================
$DIAT_URL = "https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
$BIN_PATH = "$env:LOCALAPPDATA\ia-dev-toolkit\bin"

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================
function Print-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "║   ⢠⢤⡀⠀⠀⠀⠀⢀⠏⠀⠹⣄⠀⠀⠀⠀⠀⢀⡴⠋⢳⠀⠀⠀⠀      ██████╗ ██╗ █████╗ ████████╗   ║" -ForegroundColor Cyan
    Write-Host "║   ⡼⠀⢠⠀⠈⢣⡀⡼⠀⢠⠀⠈⢣⡀⠀⠀⡴⠋⠀⡀⠘⡆⠀⠀⠀      ██╔══██╗██║██╔══██╗╚══██╔══╝   ║" -ForegroundColor Cyan
    Write-Host "║   ⢠⠃⠀⣼⣷⠀⠀⠙⠒⠚⠛⠛⠛⠓⠒⠦⠚⠀⢀⣴⡇⠀⡇⠀⠀      ██║  ██║██║███████║   ██║       ║" -ForegroundColor Cyan
    Write-Host "║   ⡼⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠃⠀⣧⠀      ██║  ██║██║██╔══██║   ██║       ║" -ForegroundColor Cyan
    Write-Host "║  ⣀⡠⠤⢴⡷⠤⢤⡤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠀      ██████╔╝██║██║  ██║   ██║       ║" -ForegroundColor Cyan
    Write-Host "║   ⢸⡄⠙⢷⡀⠙⢦⡘⢧⣷⠚⠉⠉⠛⠒⣾⠉⠳⡄⠙⢦⡀⠈⠳⣄⠙⢾⡄  ╚═════╝ ╚═╝╚═╝  ╚═╝   ╚═╝   ║" -ForegroundColor Cyan
    Write-Host "║   ⠸⡝⢧⡀⠙⢦⡝⠀⣠⣤⣤⠀⢹⠳⣄⠙⢦⡀⠉⠳⣄⠈⠑⢄⠈⠳⣼⠁                                ║" -ForegroundColor Cyan
    Write-Host "║   ⠽⣄⠙⢦⡀⠙⣦⠞⠁⠀⠈⢻⠋⠀⠀⢣⡈⠳⣄⠙⢦⡀⠈⠳⣄⠀⠙⣶⣃⣀⣀⣀⣄                  ║" -ForegroundColor Cyan
    Write-Host "║   ⣀⣀⣀⣀⣀⣀⣻⡶⣿⣦⣤⣿⣦⣤⠿⠟⠃⠀⠀⠀⠀⢸⠀⠀⠀⠀⠻⢦⣜⣷⣄⣻⣦⣀⣸⣷⠟⠃     ║" -ForegroundColor Cyan
    Write-Host "║   ⠉⠉⠉⠉⠉⠉⢹⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣘⠀⠀⠀⠀⠀⠀⠈⠉⠙⠛⠛⠉⠩⢼⠒⠒⠲⠤⠤⠤║" -ForegroundColor Cyan
    Write-Host "║   ⠀⠀⠀⠀⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠇⠀⠀⠀⠀⠀⠀⠀║" -ForegroundColor Cyan
    Write-Host "║   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠢⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀║" -ForegroundColor Cyan
    Write-Host "║   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠢⠤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡤⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀║" -ForegroundColor Cyan
    Write-Host "║   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀║" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "║                         AI DEVELOPER TOOLKIT                              ║" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "║        ┌─────────────────────────────────────────────────────────┐        ║" -ForegroundColor Cyan
    Write-Host "║        │  Skills · Agents · Workflows · Tools · Commands         │        ║" -ForegroundColor Cyan
    Write-Host "║        └─────────────────────────────────────────────────────────┘        ║" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Print-Success {
    param([string]$Message)
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Print-Info {
    param([string]$Message)
    Write-Host "  ℹ️  $Message" -ForegroundColor Yellow
}

function Print-Warning {
    param([string]$Message)
    Write-Host "  ⚠️  $Message" -ForegroundColor Yellow
}

# ============================================
# VALIDACIONES
# ============================================
function Check-Prerequisites {
    Write-Host "🔍 Verificando requisitos previos..." -ForegroundColor White
    Write-Host ""

    # Verificar Python
    $pythonCmd = $null
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } else {
        Print-Error "Python no está instalado"
        Print-Info "Instala Python 3.8+ desde: https://www.python.org/downloads/"
        return $false
    }

    $pythonVersion = & $pythonCmd --version 2>&1
    Print-Success "Python encontrado: $pythonVersion"

    Write-Host ""
    return $true
}

# ============================================
# INSTALACIÓN
# ============================================
function Install-Diat {
    Write-Host "📦 Instalando diat..." -ForegroundColor White
    Write-Host ""

    # Crear directorio
    Print-Info "Creando directorio $BIN_PATH..."
    New-Item -ItemType Directory -Force -Path $BIN_PATH | Out-Null
    Print-Success "Directorio creado: $BIN_PATH"

    # Descargar diat
    Print-Info "Descargando diat desde GitHub..."
    try {
        Invoke-WebRequest -Uri $DIAT_URL -OutFile "$BIN_PATH\diat" -ErrorAction Stop
        Print-Success "diat descargado en $BIN_PATH\diat"
    } catch {
        Print-Error "Error al descargar diat"
        Print-Info "Verifica tu conexión a internet"
        return $false
    }

    # Crear wrapper .bat
    Print-Info "Creando comando diat.bat..."
    $diatBat = "$BIN_PATH\diat.bat"

    @'
@echo off
set PYTHON_CMD=python3
where python3 >nul 2>&1 || set PYTHON_CMD=python

set DIAT_PATH=%LOCALAPPDATA%\ia-dev-toolkit\bin\diat

if exist "%DIAT_PATH%" (
    %PYTHON_CMD% "%DIAT_PATH%" %*
) else (
    echo ❌ Error: No se encontró diat
    echo    Ejecuta el script de instalación nuevamente
    exit /b 1
)
'@ | Out-File -FilePath $diatBat -Encoding ASCII

    Print-Success "Comando diat.bat creado en $BIN_PATH"

    # Agregar al PATH si no está
    Print-Info "Verificando PATH..."
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($currentPath -notlike "*$BIN_PATH*") {
        [Environment]::SetEnvironmentVariable("Path", "$BIN_PATH;$currentPath", "User")
        $env:Path = "$BIN_PATH;$env:Path"
        Print-Success "PATH actualizado"
    } else {
        Print-Info "PATH ya contiene el directorio"
    }

    Write-Host ""
    return $true
}

# ============================================
# RESUMEN FINAL
# ============================================
function Print-Summary {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "║   ✅ IA DEV TOOLKIT INSTALADO CORRECTAMENTE                   ║" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📍 Ubicación:  $BIN_PATH\diat" -ForegroundColor White
    Write-Host ""
    Write-Host "   🚀 Comandos disponibles:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "      diat                     Ver comandos disponibles"
    Write-Host "      diat --install            Instalar componentes"
    Write-Host "      diat --help               Ver ayuda"
    Write-Host ""
    Write-Host "   ⚠️  IMPORTANTE: Reinicia la terminal para usar el comando 'diat'" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
Print-Banner

if (-not (Check-Prerequisites)) {
    Write-Host ""
    Print-Error "No se cumplen los requisitos previos. Instalación cancelada."
    exit 1
}

if (-not (Install-Diat)) {
    Write-Host ""
    Print-Error "La instalación falló."
    exit 1
}

Print-Summary
