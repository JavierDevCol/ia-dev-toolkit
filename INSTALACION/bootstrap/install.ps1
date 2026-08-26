# ============================================
# squad-skills — Instalador Bootstrap para Windows
# ============================================
#
# Uso:
#   irm https://github.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.ps1 | iex
#
# O descargando primero:
#   Invoke-WebRequest -Uri "https://github.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.ps1" -OutFile install.ps1
#   Get-Content install.ps1
#   .\install.ps1
#

# ============================================
# CONFIGURACIÓN
# ============================================
$SKILLS_HOME = "$env:LOCALAPPDATA\squad-skills"
$BIN_PATH = "$env:LOCALAPPDATA\squad-skills\bin"
$REPO_URL = "https://github.com/JavierDevCol/squad-skills.git"
$REPO_BRANCH = "main"

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================
function Print-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                               ║" -ForegroundColor Cyan
    Write-Host "║   🛠️  squad-skills — Instalador Bootstrap para Windows        ║" -ForegroundColor Cyan
    Write-Host "║   Skills y Agentes IA para tu proyecto                        ║" -ForegroundColor Cyan
    Write-Host "║                                                               ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
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

    # Verificar Git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Print-Error "Git no está instalado"
        Print-Info "Instala Git desde: https://git-scm.com/downloads"
        return $false
    }

    $gitVersion = git --version 2>&1
    Print-Success "Git encontrado: $gitVersion"

    Write-Host ""
    return $true
}

# ============================================
# INSTALACIÓN
# ============================================
function Install-Skills {
    Write-Host "📦 Instalando squad-skills..." -ForegroundColor White
    Write-Host ""

    $repoPath = "$SKILLS_HOME\repo"

    # Crear estructura
    Print-Info "Creando estructura de carpetas..."
    New-Item -ItemType Directory -Force -Path $SKILLS_HOME | Out-Null
    New-Item -ItemType Directory -Force -Path $BIN_PATH | Out-Null
    Print-Success "Carpeta creada: $SKILLS_HOME"

    # Clonar o actualizar repositorio
    if (Test-Path "$repoPath\.git") {
        Print-Info "Repositorio existente, actualizando..."
        Set-Location $repoPath
        git fetch origin 2>$null
        git checkout $REPO_BRANCH 2>$null
        git pull origin $REPO_BRANCH 2>$null
        Set-Location $PSScriptRoot
        Print-Success "Repositorio actualizado"
    } else {
        Print-Info "Clonando repositorio desde GitHub..."
        if (Test-Path $repoPath) {
            Remove-Item -Recurse -Force $repoPath
        }
        $result = git clone --branch $REPO_BRANCH $REPO_URL $repoPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            Print-Error "Error al clonar el repositorio"
            return $false
        }
        Print-Success "Repositorio clonado"
    }

    # Crear comando global 'skills.bat'
    Print-Info "Creando comando global 'skills'..."
    $skillsBat = "$BIN_PATH\skills.bat"

    @'
@echo off
set PYTHON_CMD=python3
where python3 >nul 2>&1 || set PYTHON_CMD=python

set INSTALLER_PATH=%LOCALAPPDATA%\squad-skills\repo\INSTALACION\instalar.py

if exist "%INSTALLER_PATH%" (
    %PYTHON_CMD% "%INSTALLER_PATH%" %*
) else (
    echo ❌ Error: No se encontró el instalador
    echo    Ejecuta el script de instalación nuevamente
    exit /b 1
)
'@ | Out-File -FilePath $skillsBat -Encoding ASCII

    Print-Success "Comando 'skills' creado en $BIN_PATH"

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
    Write-Host "║   ✅ SQUAD-SKILLS INSTALADO CORRECTAMENTE                     ║" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📍 Ubicación:  $SKILLS_HOME" -ForegroundColor White
    Write-Host ""
    Write-Host "   🚀 Comandos disponibles:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "      skills --help              Ver ayuda"
    Write-Host "      skills `"C:\mi-proyecto`"    Instalar en un proyecto"
    Write-Host ""
    Write-Host "   ⚠️  IMPORTANTE: Reinicia la terminal para usar el comando 'skills'" -ForegroundColor Yellow
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

if (-not (Install-Skills)) {
    Write-Host ""
    Print-Error "La instalación falló."
    exit 1
}

Print-Summary
