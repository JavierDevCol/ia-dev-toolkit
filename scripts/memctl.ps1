#!/usr/bin/env pwsh
#Requires -Version 5.1
# ============================================================
# memctl — consulta de configuración del ecosistema SAC (SOLO LECTURA)
# Implementación PowerShell 5.1+ (Windows 10/11/Server de fábrica),
# sin módulos externos. Misma superficie y contrato que memctl.sh:
#   memctl get <ruta> [fuente] | memctl list [fuente]
#   fuentes: memory (default) | user | system
#   salida: escalares en crudo; objetos/arrays JSON indent 2
#   códigos: 0 ok · 1 formato/motor · 2 clave o fuente inexistente
#
# NOTA: PowerShell no trae parser YAML, así que YAML usa el parser
# restringido incluido (mapas anidados, escalares y flow [] {} de
# escalares). Fuera de ese perfil FALLA RUIDOSAMENTE: nunca adivina.
# MEMCTL_ENGINE se acepta por compatibilidad: auto|restricted.
# ============================================================
[CmdletBinding()]
param(
  [Parameter(Position = 0)][string]$Comando = '',
  [Parameter(Position = 1)][string]$Arg1 = '',
  [Parameter(Position = 2)][string]$Arg2 = ''
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
  memctl get <ruta> [fuente]    valor o subárbol (JSON indent 2 si es objeto/array)
  memctl list [fuente]          claves de primer nivel, en orden de aparición

Fuentes:
  memory (default)   skills/memory_skill.json
  user               config/config/CONFIG_USER.yaml
  system             config/config/CONFIG_SYSTEM.yaml

Variables:
  MEMCTL_ROOT     raíz del proyecto (por defecto, la raíz de este script)
  MEMCTL_ENGINE   auto|restricted (compatibilidad con memctl.sh)

Códigos de salida: 0 ok · 1 formato/motor · 2 clave o fuente inexistente
'@)
}

# ---------- argumentos ----------
switch ($Comando) {
  'get' {
    if ($Arg1 -eq '') { Die 2 'falta <ruta> (prueba: memctl get ado.config)' }
    $ruta = $Arg1
    $fuente = if ($Arg2 -eq '') { 'memory' } else { $Arg2 }
    $modo = 'get'
  }
  'list' {
    $ruta = ''
    $fuente = if ($Arg1 -eq '') { 'memory' } else { $Arg1 }
    $modo = 'list'
  }
  'help' { Uso; exit 0 }
  '-h' { Uso; exit 0 }
  '--help' { Uso; exit 0 }
  '' { Uso; exit 2 }
  default { Uso; Die 2 "comando desconocido '$Comando'" }
}

# ---------- raíz y fuente ----------
$raiz = $env:MEMCTL_ROOT
if (-not $raiz) { $raiz = Split-Path -Parent $PSScriptRoot }
# Layout instalado (.SAC/memctl.ps1 + .SAC/config/): sin MEMCTL_ROOT, el YAML vive junto al script.
$cfg = Join-Path $raiz 'config/config'
if (-not $env:MEMCTL_ROOT -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'config') -PathType Container)) { $cfg = Join-Path $PSScriptRoot 'config' }
switch ($fuente) {
  'memory' { $archivo = if ($env:MEMCTL_MEMORY) { $env:MEMCTL_MEMORY } else { Join-Path $raiz 'skills/memory_skill.json' }; $fmt = 'json' }
  'user'   { $archivo = Join-Path $cfg 'CONFIG_USER.yaml'; $fmt = 'yaml' }
  'system' { $archivo = Join-Path $cfg 'CONFIG_SYSTEM.yaml'; $fmt = 'yaml' }
  default  { Die 2 "fuente desconocida '$fuente' (use: memory|user|system)" }
}
if (-not (Test-Path -LiteralPath $archivo -PathType Leaf)) { Die 2 "fuente inexistente: $archivo" }

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

# ---------- parser YAML restringido (sin módulos) ----------
function Quitar-Comentario([string]$linea) {
  $enComilla = $false
  $comilla = ''
  $esc = $false
  for ($i = 0; $i -lt $linea.Length; $i++) {
    $c = $linea[$i]
    if ($enComilla) {
      if ($esc) { $esc = $false; continue }
      if ($c -eq '\') { $esc = $true; continue }
      if ($c -eq $comilla) { $enComilla = $false }
      continue
    }
    if ($c -eq '"' -or $c -eq "'") { $enComilla = $true; $comilla = $c; continue }
    if ($c -eq '#') {
      if ($i -eq 0 -or [char]::IsWhiteSpace($linea[$i - 1])) { return $linea.Substring(0, $i) }
    }
  }
  return $linea
}

function Decodificar([string]$s) {
  $sb = New-Object System.Text.StringBuilder
  $esc = $false
  foreach ($c in $s.ToCharArray()) {
    if ($esc) {
      switch ($c) {
        'n' { [void]$sb.Append("`n") }
        't' { [void]$sb.Append("`t") }
        'r' { [void]$sb.Append("`r") }
        '\' { [void]$sb.Append('\') }
        '"' { [void]$sb.Append('"') }
        "'" { [void]$sb.Append("'") }
        default { Die 1 "YAML no soportado: escape \$c" }
      }
      $esc = $false
      continue
    }
    if ($c -eq '\') { $esc = $true; continue }
    [void]$sb.Append($c)
  }
  if ($esc) { Die 1 'YAML no soportado: escape sin terminar' }
  return $sb.ToString()
}

function Dividir-Flow([string]$cuerpo) {
  $salida = New-Object System.Collections.ArrayList
  $cur = New-Object System.Text.StringBuilder
  $enComilla = $false
  $comilla = ''
  $esc = $false
  foreach ($c in $cuerpo.ToCharArray()) {
    if ($enComilla) {
      [void]$cur.Append($c)
      if ($esc) { $esc = $false; continue }
      if ($c -eq '\') { $esc = $true; continue }
      if ($c -eq $comilla) { $enComilla = $false }
      continue
    }
    if ($c -eq '"' -or $c -eq "'") { $enComilla = $true; $comilla = $c; [void]$cur.Append($c); continue }
    if ($c -eq ',') { [void]$salida.Add($cur.ToString()); [void]$cur.Clear(); continue }
    [void]$cur.Append($c)
  }
  if ($cur.ToString().Trim() -ne '' -or $salida.Count -eq 0) { [void]$salida.Add($cur.ToString()) }
  return $salida
}

function Parse-Escalar([string]$v) {
  if ($v -eq 'true') { return $true }
  if ($v -eq 'false') { return $false }
  if ($v -eq 'null' -or $v -eq '~') { return $null }
  if ($v -match '^-?[0-9]+$') { return [int64]::Parse($v, [System.Globalization.CultureInfo]::InvariantCulture) }
  if ($v -match '^-?[0-9]+\.[0-9]+$') { return [double]::Parse($v, [System.Globalization.CultureInfo]::InvariantCulture) }
  $first = $v[0]
  $last = $v[$v.Length - 1]
  if ($first -eq '"' -or $last -eq '"') {
    if ($first -ne '"' -or $last -ne '"') { Die 1 'YAML no soportado: string sin cerrar' }
    return (Decodificar $v.Substring(1, $v.Length - 2))
  }
  if ($first -eq "'" -or $last -eq "'") {
    if ($first -ne "'" -or $last -ne "'") { Die 1 'YAML no soportado: string sin cerrar' }
    return $v.Substring(1, $v.Length - 2).Replace("''", "'")
  }
  if ($v -match '^[|>]') { Die 1 "YAML no soportado: escalares de bloque ($v)" }
  if ($v -match '^[&*!]') { Die 1 "YAML no soportado: anclas o alias ($v)" }
  return $v
}

function Parse-Valor([string]$v) {
  if ($v -eq '[]') { return , (New-Object System.Collections.ArrayList) }
  if ($v -eq '{}') { return , ([ordered]@{}) }
  $first = $v[0]
  $last = $v[$v.Length - 1]
  if ($first -eq '[') {
    if ($last -ne ']') { Die 1 "YAML no soportado: flow array ($v)" }
    $salida = New-Object System.Collections.ArrayList
    foreach ($parte in (Dividir-Flow $v.Substring(1, $v.Length - 2))) {
      $p = $parte.Trim()
      if ($p -eq '') { continue }
      [void]$salida.Add((Parse-Escalar $p))
    }
    return , $salida
  }
  if ($first -eq '{') {
    if ($last -ne '}') { Die 1 "YAML no soportado: flow map ($v)" }
    $salida = [ordered]@{}
    foreach ($parte in (Dividir-Flow $v.Substring(1, $v.Length - 2))) {
      $p = $parte.Trim()
      if ($p -eq '') { continue }
      $dos = $p.IndexOf(':')
      if ($dos -lt 0) { Die 1 "YAML no soportado: entrada flow map sin ':' ($p)" }
      $k = $p.Substring(0, $dos).Trim()
      $salida[$k] = Parse-Escalar $p.Substring($dos + 1).Trim()
    }
    return , $salida
  }
  return (Parse-Escalar $v)
}

function Construir([string]$prefijo, $nodos, $visto) {
  $salida = [ordered]@{}
  foreach ($n in $nodos) {
    $p = $n.ruta
    if ($prefijo -eq '') {
      $r = $p
    } else {
      if (-not $p.StartsWith("$prefijo.")) { continue }
      $r = $p.Substring($prefijo.Length + 1)
    }
    if ($r -eq '') { continue }
    $dot = $r.IndexOf('.')
    if ($dot -lt 0) { $f = $r } else { $f = $r.Substring(0, $dot) }
    $clave = "$prefijo|$f"
    if ($visto.ContainsKey($clave)) { continue }
    $visto[$clave] = $true
    if ($dot -lt 0 -and -not $n.cont) {
      $hijo = $n.valor
    } else {
      $sub = if ($prefijo -eq '') { $f } else { "$prefijo.$f" }
      $hijo = Construir $sub $nodos $visto
    }
    $salida[$f] = $hijo
  }
  return , $salida
}

function Cargar-Yaml([string]$f) {
  $nodos = New-Object System.Collections.ArrayList
  $pila = New-Object System.Collections.ArrayList
  foreach ($linea in (Get-Content -LiteralPath $f -Encoding UTF8)) {
    $l = (Quitar-Comentario $linea).TrimEnd()
    if ($l.Trim() -eq '') { continue }
    $ind = 0
    while ($ind -lt $l.Length -and $l[$ind] -eq ' ') { $ind++ }
    if ($ind -lt $l.Length -and $l[$ind] -eq "`t") { Die 1 'YAML no soportado: tabulaciones' }
    $contenido = $l.Substring($ind)
    if ($contenido -eq '---' -or $contenido -eq '...') { continue }
    if ($contenido.StartsWith('-')) { Die 1 'YAML no soportado: secuencias de bloque' }
    $m = [regex]::Match($contenido, '^([A-Za-z_][A-Za-z0-9_.\-]*):\s*(.*)$')
    if (-not $m.Success) { Die 1 "YAML no soportado: clave '$contenido'" }
    $clave = $m.Groups[1].Value
    $resto = $m.Groups[2].Value.Trim()
    while ($pila.Count -gt 0 -and $pila[$pila.Count - 1].ind -ge $ind) {
      $pila.RemoveAt($pila.Count - 1)
    }
    $padre = ''
    if ($pila.Count -gt 0) { $padre = $pila[$pila.Count - 1].ruta }
    $rutaClave = if ($padre -eq '') { $clave } else { "$padre.$clave" }
    [void]$pila.Add(@{ ind = $ind; ruta = $rutaClave })
    if ($resto -eq '') {
      [void]$nodos.Add(@{ ruta = $rutaClave; cont = $true; valor = $null })
    } else {
      $valor = Parse-Valor $resto
      [void]$nodos.Add(@{ ruta = $rutaClave; cont = $false; valor = $valor })
    }
  }
  $visto = @{}
  return , (Construir '' $nodos $visto)
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
if ($fmt -eq 'json') {
  $dato = Cargar-Json $archivo
} else {
  $dato = Cargar-Yaml $archivo
}

if ($modo -eq 'list') {
  if ($dato -is [System.Collections.IDictionary]) {
    foreach ($k in $dato.Keys) { [Console]::Out.WriteLine([string]$k) }
    exit 0
  }
  Die 1 "no se pudo listar '$fuente': la raiz no es un objeto"
}

$res = Obtener $dato $ruta
if (-not $res.ok) { Die 2 "clave inexistente: '$ruta' en '$fuente'" }
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
