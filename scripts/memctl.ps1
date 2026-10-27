#!/usr/bin/env pwsh
#Requires -Version 5.1
# ============================================================
# memctl — consulta de configuración del ecosistema SAC (SOLO LECTURA)
# Implementación PowerShell 5.1+ (Windows 10/11/Server de fábrica),
# sin módulos externos. Misma superficie y contrato que memctl.sh:
#   memctl get <ruta> | memctl list
#   fuente única: sac.json (JSON nativo con ConvertFrom-Json)
#   salida: escalares en crudo; objetos/arrays JSON indent 2
#   códigos: 0 ok · 1 formato/motor · 2 clave o archivo inexistente
#
# MEMCTL_ENGINE se acepta por compatibilidad: auto|restricted.
# ============================================================
[CmdletBinding()]
param(
  [Parameter(Position = 0)][string]$Comando = '',
  [Parameter(Position = 1)][string]$Arg1 = ''
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Die([int]$codigo, [string]$mensaje) {
  [Console]::Error.WriteLine("memctl: $mensaje")
  exit $codigo
}

function Uso {
  [Console]::Out.WriteLine(@'
memctl — consulta de configuración del ecosistema SAC (solo lectura)

Uso:
  memctl get <ruta>    valor o subárbol (JSON indent 2 si es objeto/array)
  memctl list          claves de primer nivel, en orden de aparición

Fuente: sac.json (.SAC/config/sac.json; repo fuente: config/config/sac.json)
Ruta:   segmentos separados por '.' (ej: ado.config.perfil_activo)

Variables:
  MEMCTL_ROOT     raíz del proyecto (repo fuente; por defecto, la raíz de este script)
  MEMCTL_FILE     ruta explícita a sac.json (pisa todo lo demás)
  MEMCTL_ENGINE   auto|restricted (compatibilidad con memctl.sh)

Códigos de salida: 0 ok · 1 formato/motor · 2 clave o archivo inexistente
'@)
}

# ---------- argumentos ----------
switch ($Comando) {
  'get' {
    if ($Arg1 -eq '') { Die 2 'falta <ruta> (prueba: memctl get ado.config)' }
    $ruta = $Arg1
    $modo = 'get'
  }
  'list' {
    $ruta = ''
    $modo = 'list'
  }
  'help' { Uso; exit 0 }
  '-h' { Uso; exit 0 }
  '--help' { Uso; exit 0 }
  '' { Uso; exit 2 }
  default { Uso; Die 2 "comando desconocido '$Comando'" }
}

# ---------- archivo ----------
if ($env:MEMCTL_FILE) {
  $archivo = $env:MEMCTL_FILE
} elseif (-not $env:MEMCTL_ROOT -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'config/sac.json') -PathType Leaf)) {
  $archivo = Join-Path $PSScriptRoot 'config/sac.json'          # layout instalado (.SAC/)
} else {
  $raiz = $env:MEMCTL_ROOT
  if (-not $raiz) { $raiz = Split-Path -Parent $PSScriptRoot }
  $archivo = Join-Path $raiz 'config/config/sac.json'           # repo fuente
}
if (-not (Test-Path -LiteralPath $archivo -PathType Leaf)) { Die 2 "sac.json inexistente: $archivo" }

$engine = $env:MEMCTL_ENGINE
if (-not $engine) { $engine = 'auto' }
if ($engine -ne 'auto' -and $engine -ne 'restricted') {
  Die 1 "motor '$engine' no disponible en la implementación PowerShell (use: auto|restricted)"
}

# ---------- serializador común (paridad con memctl.sh) ----------
function Escapar-Json([string]$s) {
  $sb = New-Object System.Text.StringBuilder
  foreach ($c in $s.ToCharArray()) {
    switch ($c) {
      '\' { [void]$sb.Append('\\') }
      '"' { [void]$sb.Append('\"') }
      "`n" { [void]$sb.Append('\n') }
      "`t" { [void]$sb.Append('\t') }
      "`r" { [void]$sb.Append('\r') }
      default { [void]$sb.Append($c) }
    }
  }
  return $sb.ToString()
}

function Es-Contenedor($v) {
  return ($v -is [System.Collections.IDictionary] -or $v -is [System.Collections.IList])
}

function Serializar($v, [int]$nivel) {
  $sangria = '  ' * ($nivel + 1)
  $cierre = '  ' * $nivel
  if ($null -eq $v) { return 'null' }
  if ($v -is [bool]) { if ($v) { return 'true' } else { return 'false' } }
  if ($v -is [string]) { return '"' + (Escapar-Json $v) + '"' }
  if ($v -is [System.Collections.IDictionary]) {
    if ($v.Count -eq 0) { return '{}' }
    $partes = New-Object System.Collections.ArrayList
    foreach ($k in $v.Keys) {
      [void]$partes.Add($sangria + '"' + (Escapar-Json ([string]$k)) + '": ' + (Serializar $v[$k] ($nivel + 1)))
    }
    return "{`n" + ($partes -join ",`n") + "`n" + $cierre + '}'
  }
  if ($v -is [System.Collections.IList]) {
    if ($v.Count -eq 0) { return '[]' }
    $partes = New-Object System.Collections.ArrayList
    foreach ($item in $v) {
      [void]$partes.Add($sangria + (Serializar $item ($nivel + 1)))
    }
    return "[`n" + ($partes -join ",`n") + "`n" + $cierre + ']'
  }
  return [Convert]::ToString($v, [System.Globalization.CultureInfo]::InvariantCulture)
}

# ---------- carga JSON (nativo) ----------
function Cargar-Json([string]$f) {
  try {
    $crudo = Get-Content -LiteralPath $f -Raw -Encoding UTF8
    return (Normalizar ($crudo | ConvertFrom-Json))
  } catch {
    Die 1 "JSON mal formado o motor insuficiente ($f)"
  }
}

function Normalizar($v) {
  if ($null -eq $v) { return $null }
  if ($v -is [string] -or $v -is [bool]) { return $v }
  if ($v -is [System.Management.Automation.PSCustomObject]) {
    $h = [ordered]@{}
    foreach ($p in $v.PSObject.Properties) { $h[$p.Name] = Normalizar $p.Value }
    return $h
  }
  if ($v -is [System.Collections.IEnumerable]) {
    $lista = New-Object System.Collections.ArrayList
    foreach ($x in $v) { [void]$lista.Add((Normalizar $x)) }
    return , $lista
  }
  return $v
}

# ---------- acceso por ruta ----------
function Obtener($dato, [string]$r) {
  $v = $dato
  if ($r -ne '') {
    foreach ($seg in $r.Split('.')) {
      if ($v -is [System.Collections.IDictionary]) {
        if (-not $v.Contains($seg)) { return [pscustomobject]@{ ok = $false; valor = $null } }
        $v = $v[$seg]
      } elseif ($v -is [System.Collections.IList]) {
        $idx = 0
        if (-not [int]::TryParse($seg, [ref]$idx)) { return [pscustomobject]@{ ok = $false; valor = $null } }
        if ($idx -lt 0 -or $idx -ge $v.Count) { return [pscustomobject]@{ ok = $false; valor = $null } }
        $v = $v[$idx]
      } else {
        return [pscustomobject]@{ ok = $false; valor = $null }
      }
    }
  }
  return [pscustomobject]@{ ok = $true; valor = $v }
}

# ---------- orquestación ----------
$dato = Cargar-Json $archivo

if ($modo -eq 'list') {
  if ($dato -is [System.Collections.IDictionary]) {
    foreach ($k in $dato.Keys) { [Console]::Out.WriteLine([string]$k) }
    exit 0
  }
  Die 1 "no se pudo listar: la raiz no es un objeto"
}

$res = Obtener $dato $ruta
if (-not $res.ok) { Die 2 "clave inexistente: '$ruta'" }
$valor = $res.valor
if ($valor -is [string]) {
  [Console]::Out.WriteLine($valor)
} elseif (Es-Contenedor $valor) {
  [Console]::Out.WriteLine((Serializar $valor 0))
} elseif ($null -eq $valor) {
  [Console]::Out.WriteLine('null')
} elseif ($valor -is [bool]) {
  if ($valor) { [Console]::Out.WriteLine('true') } else { [Console]::Out.WriteLine('false') }
} else {
  [Console]::Out.WriteLine([Convert]::ToString($valor, [System.Globalization.CultureInfo]::InvariantCulture))
}
exit 0
