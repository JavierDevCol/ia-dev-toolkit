# ============================================
# ia-dev-toolkit — Desinstalador para Windows
# ============================================
#
# Uso:
#   irm https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/uninstall.ps1 | iex
#
# O descargando primero:
#   Invoke-WebRequest -Uri "https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/uninstall.ps1" -OutFile uninstall.ps1
#   .\uninstall.ps1
#

# ============================================
# CONFIGURACIÓN
# ============================================
$DIAT_PATH = "$env:LOCALAPPDATA\ia-dev-toolkit\bin\diat"
$DIAT_BAT = "$env:LOCALAPPDATA\ia-dev-toolkit\bin\diat.bat"
$TOOLKIT_HOME = "$env:LOCALAPPDATA\ia-dev-toolkit"

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================
function Print-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                               ║" -ForegroundColor Cyan
    Write-Host "║   🗑️  ia-dev-toolkit — Desinstalador para Windows              ║" -ForegroundColor Cyan
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

# ============================================
# CONFIRMACIÓN
# ============================================
function Confirm-Uninstall {
    Write-Host "Se eliminarán los siguientes elementos:" -ForegroundColor White
    Write-Host ""

    if (Test-Path $DIAT_PATH) {
        Write-Host "  📄 $DIAT_PATH"
    }
    if (Test-Path $DIAT_BAT) {
        Write-Host "  📄 $DIAT_BAT"
    }
    if (Test-Path $TOOLKIT_HOME) {
        Write-Host "  📁 $TOOLKIT_HOME\"
    }

    Write-Host ""
    Write-Host "⚠️  Esta acción no se puede deshacer" -ForegroundColor Yellow
    Write-Host ""

    $response = Read-Host "  ¿Continuar con la desinstalación? (s/N)"
    if ($response -ne "s" -and $response -ne "S") {
        Write-Host ""
        Print-Info "Desinstalación cancelada"
        exit 0
    }

    Write-Host ""
}

# ============================================
# DESINSTALACIÓN
# ============================================
function Uninstall-Diat {
    Write-Host "🗑️  Desinstalando ia-dev-toolkit..." -ForegroundColor White
    Write-Host ""

    # Eliminar diat
    if (Test-Path $DIAT_PATH) {
        Remove-Item -Force $DIAT_PATH
        Print-Success "Eliminado: $DIAT_PATH"
    } else {
        Print-Info "No se encontró: $DIAT_PATH"
    }

    # Eliminar diat.bat
    if (Test-Path $DIAT_BAT) {
        Remove-Item -Force $DIAT_BAT
        Print-Success "Eliminado: $DIAT_BAT"
    } else {
        Print-Info "No se encontró: $DIAT_BAT"
    }

    # Eliminar directorio de toolkit
    if (Test-Path $TOOLKIT_HOME) {
        Remove-Item -Recurse -Force $TOOLKIT_HOME
        Print-Success "Eliminado: $TOOLKIT_HOME\"
    } else {
        Print-Info "No se encontró: $TOOLKIT_HOME\"
    }

    # Eliminar del PATH
    Print-Info "Limpiando PATH..."
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $binPath = "$env:LOCALAPPDATA\ia-dev-toolkit\bin"

    if ($currentPath -like "*$binPath*") {
        $newPath = $currentPath -replace [regex]::Escape("$binPath;"), ""
        $newPath = $newPath -replace [regex]::Escape(";$binPath"), ""
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = $newPath
        Print-Success "PATH actualizado"
    } else {
        Print-Info "PATH no contiene el directorio"
    }

    Write-Host ""
}

# ============================================
# RESUMEN FINAL
# ============================================
function Print-Summary {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "║   ✅ IA DEV TOOLKIT DESINSTALADO CORRECTAMENTE                ║" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📍 Para reinstalar:" -ForegroundColor White
    Write-Host "      irm https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex"
    Write-Host ""
    Write-Host "   ⚠️  Reinicia la terminal para aplicar los cambios" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
Print-Banner
Confirm-Uninstall
Uninstall-Diat
Print-Summary
