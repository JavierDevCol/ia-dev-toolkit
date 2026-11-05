#!/usr/bin/env bash
# Uso: bash estado-ambientes.sh [-c candidatas a eliminar: en PRO + tag PRO + contenido en develop]  [-e última entrega por ambiente: fecha, PR, quién, release, tag]  [-d desvíos: cambios en des/pru/prepro/main que develop no tiene]  [-r release/vX.Y.Z  tabla de esa release en des/pru/prepro/main] [-t TARGET] repo1 repo2 ...   (default develop -> des)
# Señal principal = diff de ÁRBOL (DES recibe releases por squash: ancestría y git cherry dan falsos pendientes).
BASE=develop; TARGET=des; REL=; DESV=; ENTR=; CAND=
repos=()   # opciones válidas antes o después de los repos
while [ $# -gt 0 ]; do
  case $1 in -t|-r) [ $# -ge 2 ] || { echo "$1 requiere un valor (ej: -r release/v1.0.5)"; exit 1; };; esac
  case $1 in
  -b) echo "-b ya no existe: la comparación es release más nueva -> destino (-t). CREAR_RELEASE usa siempre develop"; exit 1;; -t) TARGET=$2; shift 2;; -r) REL=$2; shift 2;; -l) echo "-l ya no existe: usa -r all (matriz release x ambiente, con aviso SALTO), -e (versión de cada ambiente) o la tabla por defecto con -t"; exit 1;; -d) DESV=1; shift;; -e) ENTR=1; shift;; -c) CAND=1; shift;;
  -*) echo "opción desconocida: $1"; exit 1;; *) repos+=("$1"); shift;; esac; done
set -- "${repos[@]}"
# -e, -d y -r son vistas exclusivas (cada una termina el script): avisar qué opciones se ignoran
modo=; [ -n "$ENTR" ] && modo=-e; [ -z "$modo" ] && [ -n "$DESV" ] && modo=-d; [ -z "$modo" ] && [ -n "$REL" ] && modo=-r; [ -z "$modo" ] && [ -n "$CAND" ] && modo=-c
if [ -n "$modo" ]; then
  ign=; [ -n "$ENTR" ] && [ "$modo" != -e ] && ign="$ign -e"; [ -n "$DESV" ] && [ "$modo" != -d ] && ign="$ign -d"
  [ -n "$REL" ] && [ "$modo" != -r ] && ign="$ign -r"; [ -n "$CAND" ] && [ "$modo" != -c ] && ign="$ign -c"
  [ -n "$ign" ] && echo "AVISO: se muestra solo $modo; se ignora:$ign (ejecútalos por separado)" >&2
fi
# -t acepta alias: pre -> prepro, pro -> main. SUF = sufijo del tag del ambiente (prepro -> PRE, main -> PRO)
TARGET=$(echo "$TARGET" | tr A-Z a-z)
case $TARGET in pre) TARGET=prepro;; pro) TARGET=main;; esac

case $TARGET in prepro) SUF=PRE;; main) SUF=PRO;; *) SUF=$(echo $TARGET | tr a-z A-Z);; esac
LBL=$(echo $SUF | tr A-Z a-z)   # nombre en estados: des, pru, pre, pro
# Color solo en terminal (apagar con NO_COLOR=1). Los códigos van fuera del printf %-Ns para no romper la alineación.
if [ -t 1 ] && [ -z "$NO_COLOR" ]; then R=$'\033[31m'; RB=$'\033[1;31m'; C=$'\033[36m'; G=$'\033[32m'; Y=$'\033[33m'; D=$'\033[2m'; N=$'\033[1m'; Z=$'\033[0m'; else R=; RB=; C=; G=; Y=; D=; N=; Z=; fi
# Color por gravedad: verde = ok · cian = trabajo normal (PR pendiente) · amarillo = atención (falta tag) · rojo = revisar (conflicto) · rojo negrita = bloquea · gris = sin dato
cest() { case $1 in TAG_SIN_CONTENIDO*) printf %s "$RB";; *CONFLICTO*) printf %s "$R";; *PENDIENTE*) printf %s "$C";; *SIN_TAG*|*DESACTUALIZADO*|*ADELANTADO*) printf %s "$Y";; *APLICADA*) printf %s "$G";; SIN_RAMA*|-) printf %s "$D";; esac; }
# intro TÍTULO DESCRIPCIÓN: una línea al inicio de cada vista para saber qué se va a ver
intro() { printf '%s%s%s — %s%s%s\n\n' "$N" "$1" "$Z" "$D" "$2" "$Z"; }
linea() { local l= i; for ((i=0;i<$1;i++)); do l="${l}─"; done; printf '%s%s%s\n' "$D" "$l" "$Z"; }   # separador de N columnas
# Sin repos: si estás dentro de un repo git, usa '.'; si no, todos los subdirectorios con .git
if [ $# = 0 ]; then
  if git rev-parse --git-dir >/dev/null 2>&1; then set -- .; else for d in */; do [ -e "${d}.git" ] && set -- "$@" "${d%/}"; done; fi
  [ $# = 0 ] && { echo "No hay repos git aquí. Pasa las rutas: estado-ambientes.sh ms-banca-*"; exit 1; }
fi
# tagcheck TAG SUFIJO RELEASE -> vacío si coinciden; DESACTUALIZADO si el tag es de una versión anterior a la release; ADELANTADO si es posterior
tagcheck() {
  [ "$1" = - ] && return; [ "$3" = - ] && return
  local tv rv hi; tv=$(echo "${1%-$2}" | tr A-Z a-z | sed 's/^v//'); rv=$(echo "${3#release/}" | tr A-Z a-z | sed 's/^v//')
  [ "$tv" = "$rv" ] && return
  hi=$(printf '%s\n%s\n' "$tv" "$rv" | sort -V | tail -1)
  [ "$hi" = "$rv" ] && echo DESACTUALIZADO || echo ADELANTADO
}
tagmsg() { # repo ambiente tag release estado
  case $5 in
    DESACTUALIZADO) printf '  - %s en %s: el tag %s es anterior a la release contenida %s (falta el tag de esa versión)\n' "$1" "$2" "$3" "$4";;
    ADELANTADO) printf '  - %s en %s: el tag %s es posterior a la release contenida %s (tag sin contenido o release incompleta)\n' "$1" "$2" "$3" "$4";;
  esac
}
# via REPO RELEASE TARGET -> imprime la release más cercana que contiene a RELEASE y ya está aplicada en TARGET
# (una release vieja choca al simular el merge si la nueva reescribió sus archivos, pero igual llegó vía la nueva)
via() {
  local tt y out; tt=$(git -C "$1" rev-parse origin/$3^{tree})
  for y in $(git -C "$1" branch -r --list 'origin/release/*' | sed 's# *origin/##' | sort -V); do
    [ "$y" = "$2" ] && continue
    git -C "$1" merge-base --is-ancestor origin/$2 origin/$y || continue
    out=$(git -C "$1" merge-tree --write-tree origin/$3 origin/$y 2>/dev/null) && [ "$(echo "$out" | head -1)" = "$tt" ] && { echo "$y"; return; }
  done
}
# blobhist REPO RAMA RELEASE -> ALL | NONE | MIX: de los archivos en que la release y la rama difieren, ¿la versión de la RELEASE existió alguna vez en el historial de la RAMA?
blobhist() {
  local f rb tot=0 found=0
  for f in $(git -C "$1" diff --name-only origin/$2 origin/$3); do
    rb=$(git -C "$1" rev-parse -q --verify "origin/$3:$f" 2>/dev/null) || continue
    tot=$((tot+1)); git -C "$1" log -m --raw --no-abbrev --format= origin/$2 -- "$f" | grep -qF "$rb" && found=$((found+1))
  done
  if [ $tot -gt 0 ] && [ $found -eq $tot ]; then echo ALL; elif [ $found -eq 0 ]; then echo NONE; else echo MIX; fi
}
# enpr REPO RAMA RELEASE -> 0 si el título de algún PR mergeado en RAMA nombra esa release (ej. "Merged PR 6262: Release/v1.0.4 - DES")
enpr() { local v; v=$(echo "${3#release/}" | tr A-Z a-z | sed 's/^v//; s/\./\\./g'); git -C "$1" log --first-parent -500 --format=%s origin/$2 2>/dev/null | tr A-Z a-z | grep -qE "release/v?${v}([^0-9.]|$)"; }
# prmax REPO RAMA -> versión (sin v) más alta que nombran los títulos de PR de la RAMA; vacío si ninguna. Sirve aunque la rama de la release ya no exista.
prmax() { git -C "$1" log --first-parent -500 --format=%s origin/$2 2>/dev/null | sed -nE 's#.*[Rr]elease/([vV]?[0-9][0-9.]*[0-9]).*#\1#p' | tr A-Z a-z | sed 's/^v//' | sort -V | tail -1; }
# est REPO RAMA RELEASE -> APLICADA | APLICADA_VIA_vX | APLICADA_POR_PR | APLICADA_CON_CAMBIOS | PR_PENDIENTE | PR_PENDIENTE_CHOCA | PR_CONFLICTO
# Si el merge simulado choca: el título de un PR mergeado nombra la release -> APLICADA_POR_PR; si no, el historial de blobs: todas las versiones de la release ya
# pasaron por la rama -> APLICADA_CON_CAMBIOS (la rama las cambió después); ninguna -> PR_PENDIENTE_CHOCA (pendiente y el PR chocará); mezcla -> PR_CONFLICTO (revisar).
est() {
  local out rc v h
  out=$(git -C "$1" merge-tree --write-tree origin/$2 origin/$3 2>/dev/null); rc=$?
  [ $rc = 0 ] && [ "$(echo "$out" | head -1)" = "$(git -C "$1" rev-parse origin/$2^{tree})" ] && { echo APLICADA; return; }
  v=$(via "$1" "$3" "$2"); [ -n "$v" ] && { echo "APLICADA_VIA_${v#release/}"; return; }
  if [ $rc = 1 ]; then
    enpr "$1" "$2" "$3" && { echo APLICADA_POR_PR; return; }
    h=$(blobhist "$1" "$2" "$3")
    case $h in ALL) echo APLICADA_CON_CAMBIOS;; NONE) echo PR_PENDIENTE_CHOCA;; *) echo PR_CONFLICTO;; esac
  else echo PR_PENDIENTE; fi
}
# desv_ambiente REPO RAMA -> líneas "archivo<TAB>blob" de archivos cuya versión en RAMA nunca existió en el historial de develop (no depende de las release/*)
desv_ambiente() {
  local f eb
  for f in $(git -C "$1" diff --name-only origin/develop origin/$2); do
    eb=$(git -C "$1" rev-parse -q --verify "origin/$2:$f" 2>/dev/null) || continue   # borrado en el ambiente: no se detecta
    git -C "$1" log -m --raw --no-abbrev --format= origin/develop -- "$f" | grep -qF "$eb" && continue
    printf '%s\t%s\n' "$f" "$eb"
  done
}
# ley PATRÓN ESTADO EXPLICACIÓN ACCIÓN -> imprime la entrada solo si el estado apareció en la tabla (en el color de la celda)
ley() { case "$vistos" in $1) printf '\n  %s%s%s\n      %s\n      Acción: %s\n' "$(cest "$2")" "$2" "$Z" "$3" "$4";; esac; }
leyr() { # $1 = release (o "la release"), $2 = versión
  printf '\n%sESTADOS%s\n' "$N" "$Z"
  ley '* APLICADA(tag) *' 'APLICADA(tag)' "El contenido de $1 ya está en la rama del ambiente y existe su tag." 'ninguna.'
  ley '*APLICADA_SIN_TAG*' APLICADA_SIN_TAG "El contenido está en la rama, pero falta el tag $2-<AMBIENTE> (hotfix subido sin etiquetar o etiqueta olvidada)." 'crear el tag.'
  ley '*APLICADA_VIA_*' 'APLICADA_VIA_vX' 'No está tal cual, pero llegó dentro de la release vX, que la contiene.' 'ninguna (no se le exige tag propio).'
  ley '*APLICADA_CON_CAMBIOS*' APLICADA_CON_CAMBIOS 'El contenido no coincide hoy, pero todas las versiones de la release ya pasaron por la rama: el ambiente las cambió después.' 'ninguna (revisar con -d si hay cambios sin devolver a develop).'
  ley '*APLICADA_POR_PR*' APLICADA_POR_PR 'El merge choca, pero el título de un PR mergeado en el ambiente nombra la release (ej. "Release/vX - DES"): se entregó.' 'ninguna.'
  ley '* PR_PENDIENTE *' PR_PENDIENTE 'Falta contenido de la release en el ambiente y el PR release -> ambiente entraría limpio.' 'abrir el PR.'
  ley '*PR_PENDIENTE_CHOCA*' PR_PENDIENTE_CHOCA 'Ninguna versión de la release pasó por el ambiente y el merge choca (archivos listados arriba): está pendiente y el PR va a chocar.' 'abrir el PR resolviendo los conflictos en la release.'
  ley '*PR_CONFLICTO*' PR_CONFLICTO 'El merge choca y la prueba de historial no es concluyente (unas versiones de la release pasaron por el ambiente y otras no).' 'revisar el diff antes de decidir.'
  ley '*TAG_SIN_CONTENIDO*' TAG_SIN_CONTENIDO 'Existe el tag, pero la rama no contiene la release (tag mal puesto, rama reescrita o release cambiada después).' 'revisar el tag o la rama; bloquea la entrega.'
  ley '*SIN_RAMA*' SIN_RAMA 'El ambiente no tiene esa rama.' 'ninguna.'
  printf '\nRamas: des=DES, pru=PRU, prepro=PRE, main=PRO. Tags comparados sin distinguir mayúsculas.\n'
}
if [ -n "$ENTR" ]; then
  # Última entrega por ambiente = último commit (primer padre) de la rama del ambiente; la release = la más nueva contenida en él
  intro "ÚLTIMA ENTREGA POR AMBIENTE" "último commit/PR de cada rama (DES, PRU, PRE, PRO), la release que contiene y su tag"
  printf '%s%-32s %-4s %-11s %-6s %-26s %-24s %-14s %s%s\n' "$N" REPO AMB FECHA PR MERGEADO_POR RELEASE TAG ASUNTO "$Z"; linea 194
  prim=1
  for r in "$@"; do
    git -C "$r" fetch -q --tags origin 2>/dev/null || { echo "$r: fetch falló"; continue; }
    [ -n "$prim" ] || linea 194; prim=
    rels=$(git -C "$r" branch -r --list 'origin/release/*' | sed 's# *origin/##' | sort -V -r)
    v_DES=-; v_PRU=-; v_PRE=-; v_PRO=-; nm=${r#ms-banca-}
    for e in des:DES pru:PRU prepro:PRE main:PRO; do
      br=${e%%:*}; suf=${e##*:}
      git -C "$r" rev-parse -q --verify origin/$br >/dev/null || continue
      info=$(git -C "$r" log -1 --first-parent --format='%ad|%an|%s' --date=short origin/$br)
      fecha=${info%%|*}; rest=${info#*|}; autor=${rest%%|*}; asunto=${rest#*|}
      pr=$(echo "$asunto" | sed -n 's/^Merged PR \([0-9]*\).*/\1/p'); [ -n "$pr" ] || pr=-
      tt=$(git -C "$r" rev-parse origin/$br^{tree}); rl=-
      for y in $rels; do
        o=$(git -C "$r" merge-tree --write-tree origin/$br origin/$y 2>/dev/null) && [ "$(echo "$o" | head -1)" = "$tt" ] && { rl=$y; break; }
      done
      # si el título de un PR mergeado nombra una release más nueva que la del contenido (choca o su rama se borró), RELEASE la muestra marcada (por PR)
      rlpr=; prx=$(prmax "$r" $br); rln=$(echo "${rl#release/}" | tr A-Z a-z | sed 's/^v//')
      if [ -n "$prx" ] && [ "$prx" != "$rln" ]; then
        [ "$rl" = - ] && hi=$prx || hi=$(printf '%s\n%s\n' "$prx" "$rln" | sort -V | tail -1)
        [ "$hi" = "$prx" ] && { rl="release/v$prx"; rlpr=1; }
      fi
      tag=$(git -C "$r" describe --tags --match "*-$suf" --abbrev=0 origin/$br 2>/dev/null || echo -)
      tc=$(tagcheck "$tag" $suf "$rl"); [ -n "$tc" ] && { tagw="$tagw$(tagmsg "$r" $suf "$tag" "$rl" $tc)\n"; tag="$tag*"; }
      # release nombrada en el título del último PR (ej. "Merged PR 6284: release/v1.0.3.1 - DES"): si difiere de RELEASE (por contenido), avisar al pie
      pv=$(echo "$asunto" | sed -nE 's#.*[Rr]elease/([vV]?[0-9][0-9.]*[0-9]).*#\1#p' | head -1)
      if [ -n "$pv" ]; then
        pvn=$(echo "$pv" | tr A-Z a-z | sed 's/^v//'); rln=$(echo "$rl" | tr A-Z a-z | sed 's#^release/##;s/^v//')
        if [ "$pvn" != "$rln" ]; then
          echo "$rels" | tr A-Z a-z | sed 's#^release/##;s/^v//' | grep -qxF "$pvn" && ex="" || ex=" (esa rama de release ya no existe)"
          [ "$rl" = - ] && cn="ninguna release existente coincide con el contenido" || cn="el contenido incluye hasta $(echo "$rl" | tr A-Z a-z)"
          difpr="$difpr  - $r en $suf: el último PR ($pr) fue release/$(echo "$pv" | tr A-Z a-z), pero $cn$ex\n"
        fi
      fi
      rld=$(echo "$rl" | tr A-Z a-z)   # nombres de release siempre en minúscula (existen release/V1.x y release/v1.x)
      [ -n "$rlpr" ] && rld="$rld (por PR)"
      printf -v "v_$suf" %s "${rld#release/}"   # para la tabla resumen
      cr=; [ "$rl" = - ] && cr=$D; ct=; case $tag in *'*') ct=$Y;; -) ct=$D;; esac
      printf '%-32s %-4s %-11s %-6s %-26s %s%-24s%s %s%-14s%s %s\n' "$r" "$suf" "$fecha" "$pr" "${autor:0:25}" "$cr" "$rld" "$Z" "$ct" "$tag" "$Z" "${asunto:0:70}"
    done
    resumen="$resumen$(printf '%-22s' "$nm")$(for c in "$v_DES" "$v_PRU" "$v_PRE" "$v_PRO"; do [ "$c" = - ] && k=$D || k=; printf ' %s%-18s%s' "$k" "$c" "$Z"; done)\n"
  done
  # tabla resumen: versión actual de cada ambiente (release más nueva cuyo contenido ya tiene; (por PR) = sale del título de un PR)
  printf '\n%sVERSIÓN ACTUAL POR AMBIENTE%s\n%s%-22s %-18s %-18s %-18s %-18s%s\n' "$N" "$Z" "$N" REPO DES PRU PRE PRO "$Z"; linea 100; printf '%b' "$resumen"
  [ -n "$tagw" ] && printf '\nREVISAR TAGS (marcados con *):\n%b' "$tagw"
  [ -n "$difpr" ] && printf '\nRELEASE DEL ÚLTIMO PR ≠ RELEASE POR CONTENIDO (ambas pueden ser ciertas: hotfix entregado después, o rama de release borrada):\n%b' "$difpr"
  printf '\n%sLEYENDA%s\n' "$N" "$Z"; linea 84
  printf '\n  %sCOLUMNAS%s\n    FECHA · PR · MERGEADO_POR · ASUNTO   último commit de la rama del ambiente (la entrega más reciente); PR sale del título "Merged PR N"\n    RELEASE                               release más nueva cuyo contenido ya está en el ambiente (- = ninguna); (por PR) = sale del título de un PR\n    TAG                                   tag -<AMBIENTE> más cercano a la rama; * si su versión difiere de RELEASE\n' "$N" "$Z"
  printf '\n  %sAVISOS AL PIE%s\n    REVISAR TAGS                          cada tag marcado con *: falta el tag de la release contenida, o hay un tag sin contenido\n    RELEASE DEL ÚLTIMO PR ≠ RELEASE       el título del último PR nombra otra release que la del contenido (hotfix posterior o rama borrada)\n' "$N" "$Z"
  printf '\n  %sSI ALGO NO CUADRA%s\n    una release que crees entregada no aparece en RELEASE (entrega parcial, conflicto con cambios posteriores del ambiente o rama borrada)  →  estado-ambientes.sh <repo> -r release/vX.Y.Z\n    sospechas de cambios encima de la release (hotfix, commit directo)                                                              →  estado-ambientes.sh <repo> -d\n' "$N" "$Z"
  exit
fi
if [ -n "$DESV" ]; then
  # Desvío = archivo del ambiente cuya versión NUNCA existió en el historial de develop (fix/hotfix/commit directo no devuelto).
  # No depende de las release/*. Si develop solo avanzó, la versión del ambiente sí está en su historial y no cuenta.
  intro "DESVÍOS" "archivos de cada ambiente cuya versión nunca existió en develop (cambios que no volvieron)"
  envs="des:DES pru:PRU prepro:PRE main:PRO"; hoy=$(date +%s)
  res=; det=; cmds=; limpios=; nrep=0; ndes=0; npro=0
  for r in "$@"; do
    echo "analizando $r..." >&2
    git -C "$r" fetch -q --tags origin 2>/dev/null || { echo "$r: fetch falló" >&2; continue; }
    git -C "$r" rev-parse -q --verify origin/develop >/dev/null || continue
    dr=; cel=
    for e in $envs; do
      br=${e%%:*}; n=0
      if ! git -C "$r" rev-parse -q --verify origin/$br >/dev/null; then cel="$cel$(printf ' %s%-18s%s' "$D" SIN_RAMA "$Z")"; continue; fi
      d1=$(desv_ambiente "$r" $br); [ -n "$d1" ] && { n=$(printf '%s\n' "$d1" | grep -c .); dr="$dr$d1"$'\n'; }
      if [ $n -gt 0 ]; then cel="$cel$(printf ' %s%-18s%s' "$R" "CON DESVIOS ($n)" "$Z")"; else cel="$cel$(printf ' %s%-18s%s' "$G" CONTENIDO "$Z")"; fi
    done
    res="$res$(printf '%-24s' "${r#ms-banca-}")$cel\n"
    keys=$(printf '%s' "$dr" | sort -u)
    [ -z "$keys" ] && { limpios="$limpios${limpios:+, }${r#ms-banca-}"; continue; }
    nrep=$((nrep+1))
    while IFS=$'\t' read -r f eb; do
      dvb=$(git -C "$r" rev-parse -q --verify "origin/develop:$f" 2>/dev/null); [ -n "$dvb" ] && ed="otra versión" || ed="no existe"
      fila=; first=; enpro=
      for e in $envs; do
        br=${e%%:*}; xb=$(git -C "$r" rev-parse -q --verify "origin/$br:$f" 2>/dev/null)
        if [ -z "$xb" ]; then m=-; c=$D
        elif [ "$xb" = "$eb" ]; then m=X; c=$R; [ $br = main ] && { c=$RB; enpro=1; }; [ -n "$first" ] || first=$br
        elif [ "$xb" = "$dvb" ]; then m='='; c=$G
        else m='~'; c=$Y; fi
        fila="$fila$(printf ' %s%-3s%s' "$c" "$m" "$Z")"
      done
      ci=$(git -C "$r" log -1 --format='%h %an|%ad|%ct' --date=short origin/$first -- "$f"); ct=${ci##*|}; ci=${ci%|*}; ct=${ct:-$hoy}
      p=$f; [ ${#p} -gt 34 ] && p="...${f: -31}"
      det="$det$(printf '%-18s %-34s%s  %-12s %5sd  %s' "${r#ms-banca-}" "$p" "$fila" "$ed" $(( (hoy-ct)/86400 )) "${ci%|*} ${ci#*|}")\n"
      cmds="$cmds  git -C $r diff origin/develop origin/$first -- $f\n"
      ndes=$((ndes+1)); [ -n "$enpro" ] && npro=$((npro+1))
    done <<< "$keys"
  done
  printf '%s%-24s' "$N" "RESUMEN POR AMBIENTE"; for e in $envs; do printf ' %-18s' "${e##*:}"; done; printf '%s\n' "$Z"; linea 100; printf '%b' "$res"
  if [ $ndes -gt 0 ]; then
    printf '\n%s%-18s %-34s %-3s %-3s %-3s %-3s  %-12s %6s  %s%s\n' "$N" REPO ARCHIVO DES PRU PRE PRO EN_DEVELOP EDAD ULTIMO_COMMIT "$Z"; linea 130; printf '%b' "$det"
    printf '\nRESUMEN: %s repo(s) con desvíos · %s desvío(s) · %s ya en PRO.\n' "$nrep" "$ndes" "$npro"
  else echo; echo "Sin desvíos: todo lo que tienen los ambientes ya existe en el historial de develop."; fi
  [ -n "$limpios" ] && printf 'Sin desvíos: %s\n' "$limpios"
  [ -n "$cmds" ] && printf '\nPara ver cada diff (no se ejecuta nada):\n%b' "$cmds"
  printf '\n%sLEYENDA%s\n' "$N" "$Z"; linea 84
  printf '\n  %sESTADO POR AMBIENTE%s\n    %s%-18s%s todo lo que tiene el ambiente ya existe en develop (develop puede tener más: las funcionalidades nuevas no cuentan)\n    %s%-18s%s n archivo(s) con una versión que develop nunca tuvo (fix, hotfix o commit directo no devuelto)\n' "$N" "$Z" "$G" CONTENIDO "$Z" "$R" "CON DESVIOS (n)" "$Z"
  printf '\n  %sMARCAS EN DES · PRU · PRE · PRO%s  (¿qué versión del archivo tiene el ambiente?)\n    %sX%s    tiene esta versión, la que falta en develop (en negrita si es PRO)\n    %s=%s    igual a develop\n    %s~%s    otra versión, distinta de esta fila y de develop (mirar la otra fila del archivo)\n    %s-%s    el ambiente no tiene el archivo\n' "$N" "$Z" "$R" "$Z" "$G" "$Z" "$Y" "$Z" "$D" "$Z"
  printf '\n  %sCOLUMNAS%s\n    EN_DEVELOP    no existe = develop no tiene el archivo (la próxima release lo quitaría)\n                  otra versión = develop lo tiene distinto (la próxima release pisaría el cambio del ambiente)\n    EDAD          días desde el último commit que tocó el archivo\n    ULTIMO_COMMIT último commit que tocó el archivo en el ambiente\n' "$N" "$Z"
  printf '\n  %sLÍMITE%s  no detecta archivos borrados solo en el ambiente\n' "$N" "$Z"
  exit
fi
# tieneTag VER SUF -> 0 si existe el tag VER-SUF en $tags (minúsculas; sin distinguir mayúsculas: el banco mezcla v/V)
tieneTag() { echo "$tags" | grep -qxF "$(echo "$1-$2" | tr A-Z a-z)"; }
if [ "$REL" = all ] || [ "$REL" = missing ]; then
  # -r all: todas las release/* de cada repo en los 4 ambientes; -r missing: solo las filas con tag faltante o tag sin contenido
  envs="des:DES pru:PRU prepro:PRE main:PRO"
  if [ "$REL" = all ]; then intro "TODAS LAS RELEASES EN LOS 4 AMBIENTES" "una fila por release, con tags faltantes y entregas fuera de orden (SALTO)"; else intro "RELEASES CON TAG FALTANTE O SIN CONTENIDO" "solo las filas con algún problema de tag, más los avisos de SALTO"; fi
  printf '%s%-32s' "$N" RELEASE; for e in $envs; do printf ' %-26s' "${e##*:}"; done; printf '%s\n' "$Z"; linea 140
  for r in "$@"; do
    git -C "$r" fetch -q --tags origin 2>/dev/null || { echo "$r: fetch falló"; continue; }
    tags=$(git -C "$r" tag -l | tr A-Z a-z); buf=; faltan=; nm=${r#ms-banca-}
    for x in $(git -C "$r" branch -r --list 'origin/release/*' | sed 's# *origin/##' | sort -V -r); do
      ver=${x#release/}; fila=; prob=; hueco=; salto=
      for e in $envs; do
        br=${e%%:*}; suf=${e##*:}
        if ! git -C "$r" rev-parse -q --verify origin/$br >/dev/null; then st=SIN_RAMA
        else
          st=$(est "$r" $br "$x")
          case $st in PR_CONFLICTO|PR_PENDIENTE_CHOCA) true;; *) false;; esac && confl="$confl  - $r $x en $br: $(git -C "$r" merge-tree --write-tree --name-only origin/$br origin/$x 2>/dev/null | sed '1d;/^$/,$d' | head -3 | tr '\n' ' ')\n"
        fi
        # SALTO: un ambiente anterior no tiene la release (PR_PENDIENTE*) y uno posterior sí (APLICADA*); PR_CONFLICTO y SIN_RAMA no cuentan (no se sabe)
        case $st in APLICADA*) [ -n "$hueco" ] && [ -z "$salto" ] && salto="está en ${suf} pero falta en $hueco";; PR_PENDIENTE*) [ -z "$hueco" ] && hueco=$suf;; esac
        if tieneTag "$ver" $suf; then
          [[ "$st" == PR_PENDIENTE* ]] && { st=TAG_SIN_CONTENIDO; prob=1; incons="$incons  - $r en $br: existe $ver-$suf pero la rama no contiene la release\n"; } || st="$st(tag)"
        elif [[ "$st" == APLICADA || "$st" == APLICADA_CON_CAMBIOS || "$st" == APLICADA_POR_PR ]]; then st=APLICADA_SIN_TAG; prob=1; faltan="$faltan${faltan:+, }$ver-$suf"; fi
        vistos="$vistos $st "
        fila="$fila$(printf ' %s%-26s%s' "$(cest "$st")" "$st" "$Z")"
      done
      [ -n "$salto" ] && saltos="$saltos  - $nm $x: $salto\n"
      [ "$REL" = missing ] && [ -z "$prob" ] && continue
      buf="$buf$(printf '  %-30s' "$x")$fila${salto:+  ${RB}SALTO${Z}}\n"
    done
    [ -n "$buf" ] && { printf '%s%s%s\n' "$N" "$r" "$Z"; printf '%b' "$buf"; }
    [ -n "$faltan" ] && sintag="$sintag  - $r: $faltan\n"
  done
  [ -n "$sintag" ] && printf '\nFALTAN TAGS (contenido integrado sin tag):\n%b' "$sintag" || printf '\nNo faltan tags: toda release integrada directamente tiene su tag.\n'
  [ -n "$confl" ] && printf '\nPR_CONFLICTO (el merge simulado con el ambiente choca en estos archivos: o la release ya se entregó y el ambiente cambió esas líneas después, o está pendiente y el PR va a chocar; hay que mirar el contenido):\n%b' "$confl"
  [ -n "$incons" ] && printf '\nINCONSISTENTE: hay tag pero falta el contenido (tag mal puesto, rama reescrita o release cambiada después):\n%b' "$incons"
  [ -n "$saltos" ] && printf '\n%sSALTO%s (entrega fuera de orden: la release está en un ambiente posterior pero falta en uno anterior; puede ser intencional, p. ej. un hotfix urgente):\n%b' "$RB" "$Z" "$saltos"
  leyr 'la release' 'vX.Y.Z'
  exit
fi
if [ -n "$REL" ]; then
  ver=${REL#release/}; envs="des:DES pru:PRU prepro:PRE main:PRO"   # rama:sufijo de tag
  intro "ESTADO DE $REL EN LOS 4 AMBIENTES" "si su contenido ya está en DES, PRU, PRE y PRO, y si tiene su tag"
  printf '%s%-32s' "$N" REPO; for e in $envs; do printf ' %-26s' "${e##*:}"; done; printf '%s\n' "$Z"; linea 140
  for r in "$@"; do
    git -C "$r" fetch -q --tags origin 2>/dev/null || { echo "$r: fetch falló"; continue; }
    printf '%-32s' "$r"; tags=$(git -C "$r" tag -l | tr A-Z a-z); stdes=
    if ! git -C "$r" rev-parse -q --verify origin/$REL >/dev/null; then printf ' %s\n' "(sin $REL)"; continue; fi
    for e in $envs; do
      br=${e%%:*}; suf=${e##*:}
      if ! git -C "$r" rev-parse -q --verify origin/$br >/dev/null; then st=SIN_RAMA
      else
        st=$(est "$r" $br "$REL"); [ $br = des ] && stdes=$st
        case $st in PR_CONFLICTO|PR_PENDIENTE_CHOCA) true;; *) false;; esac && confl="$confl  - $r en $br: $(git -C "$r" merge-tree --write-tree --name-only origin/$br origin/$REL 2>/dev/null | sed '1d;/^$/,$d' | head -3 | tr '\n' ' ')\n"
      fi
      if tieneTag "$ver" $suf; then
        [[ "$st" == PR_PENDIENTE* ]] && { st=TAG_SIN_CONTENIDO; incons="$incons  - $r en $br: existe $ver-$suf pero la rama no contiene la release\n"; } || st="$st(tag)"
      elif [[ "$st" == APLICADA || "$st" == APLICADA_CON_CAMBIOS || "$st" == APLICADA_POR_PR ]]; then st=APLICADA_SIN_TAG; sintag="$sintag  - $r en $br: falta el tag $ver-$suf\n"; fi
      vistos="$vistos $st "; printf ' %s%-26s%s' "$(cest "$st")" "$st" "$Z"
    done; echo
    # ¿DES tiene archivos cuya versión nunca existió en develop? (mismo método que -d; no depende de qué release/* sigan existiendo)
    case $stdes in APLICADA*) git -C "$r" rev-parse -q --verify origin/develop >/dev/null && {
      fl=$(desv_ambiente "$r" des | cut -f1); n=$(printf '%s' "$fl" | grep -c .)
      [ "$n" -gt 0 ] && propio="$propio  - $r: $n archivo(s) de des cuya versión nunca existió en develop: $(echo "$fl" | head -3 | tr '\n' ' ')\n"; };; esac
  done
  [ -n "$propio" ] && printf '\nDES CON CONTENIDO PROPIO (cambios en DES que nunca estuvieron en develop: fix o commit directo no devuelto; ver todo con -d; revisar antes de promover a PRU):\n%b' "$propio"
  [ -n "$confl" ] && printf '\nPR_CONFLICTO (el merge simulado con el ambiente choca en estos archivos: o la release ya se entregó y el ambiente cambió esas líneas después, o está pendiente y el PR va a chocar; hay que mirar el contenido):\n%b' "$confl"
  [ -n "$incons" ] && printf '\nINCONSISTENTE: hay tag pero falta el contenido (tag mal puesto, rama reescrita o release cambiada después):\n%b' "$incons"
  [ -n "$sintag" ] && printf '\nREVISAR: el contenido está pero no hay tag (hotfix subido sin etiquetar o etiqueta olvidada):\n%b' "$sintag"
  leyr "$REL" "$ver"
  exit
fi
if [ -n "$CAND" ]; then
  # -c: candidatas a eliminar. Las release/* se cortan de develop sin squash, así que la MÁS NUEVA de todas contiene (por ancestría) a las anteriores:
  #  · contenida en la más nueva  -> candidata (su contenido viaja con la más nueva), salvo que tenga ramas de trabajo sin integrar basadas en ella;
  #  · NO contenida (hotfix, líneas viejas) -> reglas completas: en DES/PRU/PRE/PRO, tag vX-PRO en main, cambios ya en develop, sin ramas basadas;
  #  · se conservan siempre: la más nueva y la base de PRO (por contenido y por el último tag -PRO).
  # Solo informa; nunca borra.
  # mk MARCA COLOR ANCHO: la marca puede ser UTF-8 (✓): se rellena con espacios contando caracteres, no bytes
  mk() { local p=$(( $3 - ${#1} )); [ $p -lt 0 ] && p=0; printf '%s%s%s%*s' "$2" "$1" "$Z" $p ''; }
  cell() { case $1 in SI) mk '✓' "$G" 4;; VIA) mk '≈' "$G" 4;; NO) mk '✗' "$C" 4;; CONF) mk '!' "$R" 4;; FUERA) mk '✗' "$R" 4;; N/A) mk '–' "$D" 4;; D:*) mk "✗${1#D:}" "$R" 4;; B:*) mk "✗${1#B:}" "$C" 4;; *) mk '·' "$D" 4;; esac; }
  mapst() { case $1 in APLICADA|APLICADA_CON_CAMBIOS|APLICADA_POR_PR) echo SI;; APLICADA_VIA_*) echo VIA;; PR_CONFLICTO) echo CONF;; *) echo NO;; esac; }
  # marcas por ambiente (DES, PRU, PRE) -> v_DES v_PRU v_PRE y la lista falta; PRO llega en $sp
  emarks() { falta=; for e in des:DES pru:PRU prepro:PRE; do
      s1=$(mapst "$(est "$r" ${e%%:*} "$x")"); eval "v_${e##*:}=$s1"
      case $s1 in SI|VIA) :;; CONF) falta="$falta${falta:+, }${e##*:} (choca)";; *) falta="$falta${falta:+, }${e##*:}";; esac
    done; }
  # tag vX-PRO (existe y está en la historia de main) -> tg
  tagchk() { if [ "$sp" = VIA ]; then tg=N/A
    else tn=$(echo "$tags" | grep -ixF "$ver-PRO" | head -1)
      if [ -z "$tn" ]; then tg=NO; bloq=1; tf="$tf${tf:+ · }$ver-PRO"
      elif git -C "$r" merge-base --is-ancestor "refs/tags/$tn" origin/main 2>/dev/null; then tg=SI
      else tg=FUERA; bloq=1; acRev="$acRev      $(printf '%-22s %-18s' "$nm" "$x")el tag $tn existe pero no está en la historia de main\n"; fi
    fi; }
  # cambios hechos en la release (desde que se cortó de develop) cuya versión nunca existió en develop -> dv, y lista en acDev si bloquea
  devchk() { mb=$(git -C "$r" merge-base origin/develop origin/$x 2>/dev/null); lost=; nl=0
    if [ -z "$mb" ]; then dv=CONF; bloq=1; acRev="$acRev      $(printf '%-22s %-18s' "$nm" "$x")sin ancestro común con develop\n"
    else
      for f in $(git -C "$r" diff --name-only $mb origin/$x); do
        rb=$(git -C "$r" rev-parse -q --verify "origin/$x:$f" 2>/dev/null) || continue
        git -C "$r" log -m --raw --no-abbrev --format= origin/develop -- "$f" | grep -qF "$rb" && continue
        nl=$((nl+1)); lost="$lost $f"
      done
      if [ $nl -eq 0 ]; then dv=SI; else dv="D:$nl"
        [ -z "$nodev" ] && { bloq=1; acDev="$acDev      $(printf '%-22s %s' "$nm" "$x")\n"
          for f in $(echo $lost | tr ' ' '\n' | head -3); do [ ${#f} -gt 80 ] && f="…${f: -79}"; acDev="$acDev          · $f\n"; done
          [ $nl -gt 3 ] && acDev="$acDev          · (+$((nl-3)) más)\n"; }
      fi
    fi; }
  # ramas de trabajo sin integrar que nacieron de esta release (solo detectable si la release no se fusionó a develop) -> rm_
  ramchk() { rm_=SI
    if ! git -C "$r" merge-base --is-ancestor origin/$x origin/develop 2>/dev/null; then
      bas=; nbs=0; for b in $otras; do git -C "$r" merge-base --is-ancestor origin/$x origin/$b 2>/dev/null && ! git -C "$r" merge-base --is-ancestor origin/$b origin/develop 2>/dev/null && { bas="$bas $b"; nbs=$((nbs+1)); }; done
      [ $nbs -gt 0 ] && { rm_="B:$nbs"; bloq=1; acBas="$acBas      $(printf '%-22s %-18s' "$nm" "$x")${bas# }\n"; }
    fi; }
  intro "CANDIDATAS A ELIMINAR" "qué releases se pueden borrar y qué falta para poder hacerlo"
  sum=; det=; acTag=; acDev=; acBas=; acRev=; acAvi=; cands=; ncand=0; nbloq=0
  for r in "$@"; do
    echo "analizando $r..." >&2
    git -C "$r" fetch -q --tags origin 2>/dev/null || { echo "$r: fetch falló" >&2; continue; }
    nm=${r#ms-banca-}
    for ref in origin/develop origin/main; do git -C "$r" rev-parse -q --verify $ref >/dev/null || { sum="$sum$(printf '%-24s' "$nm")(sin $ref: se omite)\n"; continue 2; }; done
    rels=$(git -C "$r" branch -r --list 'origin/release/*' | sed 's# *origin/##' | tr -d ' ' | sort -V -r)
    [ -z "$rels" ] && { sum="$sum$(printf '%-24s' "$nm")(sin release/*)\n"; continue; }
    newest=$(echo "$rels" | head -1); nv=${newest#release/}
    tags=$(git -C "$r" tag -l); rows=; curso=; nc=0; nb=0; ne=0; tf=
    otras=$(git -C "$r" branch -r | sed 's# *origin/##' | grep -vE '^(HEAD|develop|des|pru|prepro|main|release/)')   # ramas de trabajo
    # estado de cada release en PRO (una vez) y base de PRO: por contenido (la más nueva contenida en main) y por el último tag -PRO
    spmap=; baseC=; for x in $rels; do s0=$(mapst "$(est "$r" main "$x")"); spmap="$spmap$x $s0\n"; [ -z "$baseC" ] && { [ "$s0" = SI ] || [ "$s0" = VIA ]; } && baseC=$x; done
    baseT=; tp=$(git -C "$r" describe --tags --match "*-PRO" --abbrev=0 origin/main 2>/dev/null)
    [ -n "$tp" ] && for x in $rels; do [ "$(echo "${x#release/}" | tr A-Z a-z | sed 's/^v//')" = "$(echo "${tp%-PRO}" | tr A-Z a-z | sed 's/^v//')" ] && { baseT=$x; break; }; done
    for x in $rels; do
      ver=${x#release/}; bloq=; cd_=-; cu=-; ce=-; tg=-; dv=-; rm_=-; anc=-; est_=; ec=; nodev=
      sp=$(printf '%b' "$spmap" | awk -v k="$x" '$1==k{print $2}')
      lbl=; [ "$x" = "$newest" ] && lbl="más nueva"; [ "$x" = "$baseC" ] && lbl="$lbl${lbl:+ y }base de PRO"; [ "$x" = "$baseT" ] && [ "$x" != "$baseC" ] && lbl="$lbl${lbl:+ y }tag PRO"
      if [ -n "$lbl" ]; then
        # se conserva: se muestra dónde está y si hay cambios sin devolver (aviso: las eliminadas por estar contenidas en la más nueva dependen de ella)
        emarks; cd_=$v_DES; cu=$v_PRU; ce=$v_PRE
        if [ "$sp" = SI ] || [ "$sp" = VIA ]; then tagchk; bloq=; fi
        nodev=1; devchk; bloq=; rm_=-; est_="CONSERVAR ($lbl)"; ec=$C
        case $dv in D:*) [ "$x" = "$newest" ] && acAvi="$acAvi      $(printf '%-22s %-18s' "$nm" "$x")tiene ${dv#D:} archivo(s) con versión que develop nunca tuvo; lo que se elimine por estar contenido en ella depende de que eso llegue a develop\n";; esac
        [ "$x" = "$newest" ] && anc=N/A || { git -C "$r" merge-base --is-ancestor origin/$x origin/$newest 2>/dev/null && anc=SI || anc=NO; }
      elif git -C "$r" merge-base --is-ancestor origin/$x origin/$newest 2>/dev/null; then
        # contenida en la más nueva: su contenido viaja con ella
        anc=SI; emarks; cd_=$v_DES; cu=$v_PRU; ce=$v_PRE; ramchk
        if [ -n "$bloq" ]; then est_="BLOQUEADA"; ec=$Y; else est_="ELIMINAR (contenida en $nv)"; ec=$G; fi
      else
        # no contenida en la más nueva (hotfix o línea antigua): reglas completas
        anc=NO
        if [ "$sp" = NO ]; then curso="$curso${curso:+, }${ver}"; ne=$((ne+1)); continue; fi   # aún no llega a PRO: se resume en una línea
        if [ "$sp" = CONF ]; then bloq=1; acRev="$acRev      $(printf '%-22s %-18s' "$nm" "$x")choca al compararla con PRO  →  estado-ambientes.sh $r -r $x\n"
        else
          emarks; cd_=$v_DES; cu=$v_PRU; ce=$v_PRE
          [ -n "$falta" ] && { bloq=1; acRev="$acRev      $(printf '%-22s %-18s' "$nm" "$x")falta en $falta  →  estado-ambientes.sh $r -r $x\n"; }
          tagchk; devchk; ramchk
        fi
        if [ -n "$bloq" ]; then est_="BLOQUEADA"; ec=$Y; else est_="ELIMINAR"; ec=$G; fi
      fi
      case $est_ in BLOQUEADA) nb=$((nb+1));; ELIMINAR*) nc=$((nc+1)); cands="$cands$r $x\n";; esac
      rows="$rows$(printf '  %-24s' "$x")$(cell $cd_)$(cell $cu)$(cell $ce)$(cell $sp)$(cell $tg)$(cell $dv)$(cell $rm_)$(cell $anc)$ec$est_$Z\n"
    done
    [ -n "$tf" ] && acTag="$acTag      $(printf '%-22s' "$nm")$tf\n"
    ncand=$((ncand+nc)); nbloq=$((nbloq+nb))
    sc=; [ $nc -gt 0 ] && sc=$G; sb=; [ $nb -gt 0 ] && sb=$Y
    bp=${baseC#release/}; sum="$sum$(printf '%-24s%-12s%-12s' "$nm" "$nv" "${bp:--}")$sc$(printf '%-12s' "$nc")$Z$sb$(printf '%-12s' "$nb")$Z$ne\n"
    det="$det\n${N}${r}${Z}  (más nueva: $nv · base de PRO: ${bp:--})\n"
    [ -n "$curso" ] && det="$det  ${D}En curso, no contenidas en la más nueva y aún no en PRO: $curso${Z}\n"
    [ -n "$rows" ] && det="$det\n  $(printf '%s%-24s%-4s%-4s%-4s%-4s%-4s%-4s%-4s%-4s%s' "$N" RELEASE DES PRU PRE PRO TAG DEV RAM ANC ESTADO)$Z\n$rows"
  done
  # 1) resumen
  printf '%s%-24s%-12s%-12s%-12s%-12s%s%s\n' "$N" REPO MAS_NUEVA BASE_PRO CANDIDATAS BLOQUEADAS EN_CURSO "$Z"; linea 84; printf '%b' "$sum"
  # 2) detalle por repo
  printf '\n%sDETALLE%s\n' "$N" "$Z"; linea 84; printf '%b' "$det"
  # leyenda (antes de las acciones)
  printf '\n%sLEYENDA%s\n' "$N" "$Z"; linea 84
  printf '\n  %sMARCAS EN DES · PRU · PRE · PRO%s  (¿el contenido de la release ya está en la rama de ese ambiente?)\n' "$N" "$Z"
  printf '    %s✓%s    sí: el contenido ya está en la rama\n    %s≈%s    sí, pero llegó dentro de otra release posterior que ya está en la rama\n    %s✗%s    todavía no: falta entregarla (el merge entraría limpio)\n         si la release está contenida en la más nueva, llegará con ella: NO bloquea la eliminación\n    %s!%s    el merge simulado choca: revisar con estado-ambientes.sh <repo> -r release/vX\n    %s·%s    no evaluado\n' "$G" "$Z" "$G" "$Z" "$C" "$Z" "$R" "$Z" "$D" "$Z"
  printf '\n  %sMARCAS EN TAG · DEV · RAM · ANC%s\n    %s✓%s    cumple\n    %s✗%s    no cumple (✗n = n archivos o ramas)\n    %s–%s    no aplica\n    %s·%s    no evaluado\n' "$N" "$Z" "$G" "$Z" "$C" "$Z" "$D" "$Z" "$D" "$Z"
  printf '\n  %sCOLUMNAS%s\n    DES PRU PRE PRO   dónde está ya el contenido de la release (informativo si está contenida en la más nueva)\n    TAG               existe el tag vX-PRO y está en la historia de main\n    DEV               lo cambiado en la release ya existió en develop\n    RAM               no hay ramas de trabajo sin integrar basadas en ella\n    ANC               está contenida (es ancestra) en la release más nueva\n' "$N" "$Z"
  printf '\n  %sESTADOS%s\n    %s%-27s%s contenida en la más nueva: su contenido viaja con ella\n    %s%-27s%s no contenida, pero cumple las reglas completas\n    %s%-27s%s falta algo: ver "PARA PODER ELIMINAR"\n    %s%-27s%s más nueva, base de PRO o tag PRO: no se elimina\n' "$N" "$Z" "$G" "ELIMINAR (contenida en vX)" "$Z" "$G" "ELIMINAR" "$Z" "$Y" "BLOQUEADA" "$Z" "$C" "CONSERVAR (...)" "$Z"
  printf '\n  %sREGLAS%s\n    1. Contenida en la más nueva → candidata, salvo que tenga ramas sin integrar basadas en ella.\n    2. No contenida (hotfix, líneas antiguas) → en los 4 ambientes, tag vX-PRO en main, sus cambios en develop y sin ramas basadas.\n    3. Siempre se conservan la más nueva y la base de PRO (por contenido y por el último tag -PRO).\n' "$N" "$Z"
  # 3) acciones pendientes, por tipo de tarea
  printf '\n%sPARA PODER ELIMINAR%s\n' "$N" "$Z"; linea 84; k=0
  [ -n "$acAvi" ] && { k=$((k+1)); printf '\n %s. %sAVISO: LA RELEASE MÁS NUEVA TIENE CAMBIOS SIN DEVOLVER %s(las contenidas en ella dependen de que lleguen a develop)%s\n%b' "$k" "$N" "$D" "$Z" "$acAvi"; }
  [ -n "$acTag" ] && { k=$((k+1)); printf '\n %s. %sCREAR TAG %s(entregadas sin etiqueta)%s\n%b' "$k" "$N" "$D" "$Z" "$acTag"; }
  [ -n "$acDev" ] && { k=$((k+1)); printf '\n %s. %sLLEVAR A DEVELOP %s(cambios de la release que develop nunca tuvo)%s\n%b' "$k" "$N" "$D" "$Z" "$acDev"; }
  [ -n "$acBas" ] && { k=$((k+1)); printf '\n %s. %sRESOLVER RAMAS BASADAS EN LA RELEASE %s(sin integrar a develop)%s\n%b' "$k" "$N" "$D" "$Z" "$acBas"; }
  [ -n "$acRev" ] && { k=$((k+1)); printf '\n %s. %sREVISAR %s(conflicto, falta en un ambiente, tag fuera de main)%s\n%b' "$k" "$N" "$D" "$Z" "$acRev"; }
  [ $k -eq 0 ] && printf '\n Nada pendiente.\n'
  # 4) candidatas
  printf '\n%sCANDIDATAS A ELIMINAR (%s)%s\n' "$N" "$ncand" "$Z"; linea 84
  if [ $ncand -gt 0 ]; then printf '%b' "$cands" | while read -r cr cx; do printf '  git -C %s push origin --delete %s\n' "$cr" "$cx"; done
    printf '\n  Comandos sugeridos, NO ejecutados. Antes, verifica en Azure DevOps que no haya PRs abiertos desde o hacia la rama (se abandonarían): el script no los ve.\n'
  else printf '  Ninguna todavía: se liberan al completar las acciones de arriba.\n'; fi
  exit
fi
LU0=$(echo $LBL | tr a-z A-Z)
if [ "$TARGET" = des ]; then intro "ESTADO DE PASO A $LU0" "qué falta para pasar a $TARGET con la release más nueva, y si hay que cortar otra"; else intro "ESTADO DE PASO A $LU0" "qué falta para pasar a $TARGET con la release más nueva"; fi
printf '%s%-26s %-18s %-20s %-24s %-24s %-16s %s%s\n' "$N" REPO RELEASE_MAS_NUEVA "$(echo $LBL | tr a-z A-Z)_TIENE" VEREDICTO QUE_TRAE CREAR_RELEASE ULTIMO_TAG "$Z"; linea 150
acPR=; acCf=; acCut=; evaluados=0
prim=1
for r in "$@"; do
  git -C "$r" fetch -q --tags origin 2>/dev/null || { echo "$r: fetch falló"; continue; }
  B=origin/$BASE; T=origin/$TARGET
  for ref in $B $T; do git -C "$r" rev-parse -q --verify $ref >/dev/null || { printf '%-26s %s\n' "${r#ms-banca-}" "(sin $ref: no aplica paso de ambiente, se omite)"; continue 2; }; done
  evaluados=$((evaluados+1))
  Ttree=$(git -C "$r" rev-parse $T^{tree}); rel=""; ult="-"; est="-"
  for x in $(git -C "$r" branch -r --list 'origin/release/*' | sed 's# *origin/##' | sort -V -r); do
    [ -z "$rel" ] && rel=$x
    ok=; out=$(git -C "$r" merge-tree --write-tree $T origin/$x 2>/dev/null) && [ "$(echo "$out" | head -1)" = "$Ttree" ] && ok=1
    [ -n "$ok" ] && [ "$ult" = "-" ] && ult=$x
    [ -n "$ok" ] && break
  done
  # el contenido (ult) subestima si la release choca o su rama se borró: los títulos de PR mergeados en el destino son otra evidencia
  ultpr=; prx=$(prmax "$r" $TARGET); ultn=$(echo "${ult#release/}" | tr A-Z a-z | sed 's/^v//')
  if [ -n "$prx" ] && [ "$prx" != "$ultn" ]; then
    [ "$ult" = - ] && hi=$prx || hi=$(printf '%s\n%s\n' "$prx" "$ultn" | sort -V | tail -1)
    [ "$hi" = "$prx" ] && { ult="release/v$prx"; ultpr=1; }
  fi
  tiene=${ult#release/}; [ -n "$ultpr" ] && tiene="$tiene (por PR)"
  tag=$(git -C "$r" describe --tags --match "*-$SUF" --abbrev=0 $T 2>/dev/null || echo -)
  tc=$(tagcheck "$tag" $SUF "$ult"); [ -n "$tc" ] && { tagw="$tagw$(tagmsg "$r" $LBL "$tag" "$ult" $tc)\n"; tag="$tag*"; }
  sinrel=-; [ "$TARGET" = des ] && [ "$BASE" = develop ] && [ -n "$rel" ] && sinrel=$(git -C "$r" rev-list --no-merges --count origin/$rel..$B)
  nm=${r#ms-banca-}; ver=; trae=-; crear=-
  # CREAR_RELEASE: ¿hay commits de la base (develop) fuera de la release más nueva? (solo con base develop)
  [ "$sinrel" != - ] && { [ "$sinrel" -gt 0 ] && crear="SI ($sinrel)" || crear=NO; }
  if [ -z "$rel" ]; then ver=SIN_RELEASE
    [ "$TARGET" = des ] && [ "$BASE" = develop ] && [ "$(git -C "$r" diff --numstat $T $B | wc -l | tr -d ' ')" != 0 ] && { crear=SI; acCut="$acCut      $(printf '%-22s' "$nm")el repo no tiene releases y $BASE difiere de $TARGET\n"; }
  else
    case $(est "$r" $TARGET "$rel") in
      PR_PENDIENTE) ver="PR_PENDIENTE"
        trae=$(git -C "$r" diff --shortstat $T origin/$rel | sed -E 's/ files? changed/f/;s/ insertions?\(\+\)/+/;s/ deletions?\(-\)/-/;s/,//g;s/^ //')
        acPR="$acPR      $(printf '%-22s' "$nm")$rel -> $TARGET   ($trae)\n";;
      PR_PENDIENTE_CHOCA|PR_CONFLICTO)
        case $(est "$r" $TARGET "$rel") in PR_CONFLICTO) ver="PR_CONFLICTO";; *) ver="PR_PENDIENTE (choca)";; esac
        cf=$(git -C "$r" merge-tree --write-tree --name-only $T origin/$rel 2>/dev/null | sed '1d;/^$/,$d' | sort -u); trae="choca en $(echo "$cf" | grep -c .) archivo(s)"
        acCf="$acCf      $(printf '%-22s' "$nm")$rel  →  estado-ambientes.sh $r -r $rel\n          · $(echo "$cf" | head -2 | tr '\n' ' ')\n";;
      APLICADA_CON_CAMBIOS) ver="APLICADA (con cambios)";;
      APLICADA_POR_PR) ver="APLICADA (por PR)";;
      *) ver=APLICADA;;
    esac
    [ "$sinrel" != - ] && [ "$sinrel" -gt 0 ] && acCut="$acCut      $(printf '%-22s' "$nm")$sinrel commit(s) de $BASE fuera de $rel\n"
  fi
  case $ver in APLICADA*) vc=$G;; PR_PENDIENTE*choca*) vc=$R;; PR_PENDIENTE*) vc=$C;; PR_CONFLICTO*) vc=$R;; *) vc=$D;; esac
  rn=${rel#release/}; [ -n "$rn" ] || rn=-
  case $crear in SI*) cs=$Y;; *) cs=$D;; esac; ct=; case $tag in *'*') ct=$Y;; -) ct=$D;; esac
  printf '%-26s %-18s %-20s %s%-24s%s %-24s %s%-16s%s %s%s%s\n' "$nm" "$rn" "$tiene" "$vc" "$ver" "$Z" "$trae" "$cs" "$crear" "$Z" "$ct" "$tag" "$Z"
done
BU=$(echo $BASE | tr a-z A-Z); LU=$(echo $LBL | tr a-z A-Z)
# LEYENDA
printf '\n%sLEYENDA%s\n' "$N" "$Z"; linea 84
printf '\n  %sCOLUMNAS%s\n' "$N" "$Z"
printf '    %-20s %s\n' RELEASE_MAS_NUEVA "release contra la que se compara: la de mayor versión entre las release/* que existen (no usa la fecha)" "${LU}_TIENE" "release más nueva cuyo contenido ya está en $TARGET" VEREDICTO "estado de RELEASE_MAS_NUEVA respecto a $TARGET" QUE_TRAE "diferencia de archivos entre RELEASE_MAS_NUEVA y $TARGET (f = archivos, + / - = líneas)" CREAR_RELEASE "SI (n) = $BASE tiene n commits (sin merges) que la release más nueva no incluye: hay que cortar una release nueva; NO = nada fuera de ella; - = no aplica: solo se calcula con -t des (cortar una release es el paso previo a DES)" ULTIMO_TAG "tag -$SUF más cercano a la rama; * si su versión difiere de la release que $TARGET ya tiene"
printf '\n  %sVEREDICTOS%s  (solo hablan de la release ya cortada; si falta cortar otra, lo dice CREAR_RELEASE)\n' "$N" "$Z"
printf '    %s%-26s%s %s ya contiene RELEASE_MAS_NUEVA\n    %s%-26s%s la release pasó por %s y este la cambió después (revisar con -d)\n    %s%-26s%s el merge choca, pero el título de un PR mergeado nombra la release: se entregó\n    %s%-26s%s hay que abrir el PR release/vX -> %s (entraría limpio)\n    %s%-26s%s pendiente y el PR va a chocar: resolver los conflictos en la release\n    %s%-26s%s el PR release/vX -> %s chocaría: revisar con estado-ambientes.sh <repo> -r release/vX\n    %s%-26s%s el repo no tiene ramas release/*\n' "$G" APLICADA "$Z" "$TARGET" "$G" "APLICADA (con cambios)" "$Z" "$TARGET" "$G" "APLICADA (por PR)" "$Z" "$C" "PR_PENDIENTE" "$Z" "$TARGET" "$R" "PR_PENDIENTE (choca)" "$Z" "$R" "PR_CONFLICTO" "$Z" "$TARGET" "$D" SIN_RELEASE "$Z"
printf '    (por PR) en %s_TIENE: sale de los títulos de PR (ej. "Release/vX - DES") cuando el contenido choca o la rama de la release se borró\n' "$LU"
printf '\n  %sFLUJO%s  develop no se promueve directo a %s: se corta una release/vX.Y.Z y esa release se promueve (release -> %s).\n' "$N" "$Z" "$TARGET" "$TARGET"
# ACCIONES
printf '\n%sPARA PASAR A %s%s\n' "$N" "$LU" "$Z"; linea 84; k=0
[ -n "$acPR" ] && { k=$((k+1)); printf '\n %s. %sABRIR PR %s(release -> %s)%s\n%b' "$k" "$N" "$D" "$TARGET" "$Z" "$acPR"; }
[ -n "$acCf" ] && { k=$((k+1)); printf '\n %s. %sREVISAR CONFLICTO %s(el PR release -> %s chocaría)%s\n%b' "$k" "$N" "$D" "$TARGET" "$Z" "$acCf"; }
[ -n "$acCut" ] && { k=$((k+1)); printf '\n %s. %sCORTAR RELEASE NUEVA %s(%s tiene commits fuera de la release más nueva)%s\n%b' "$k" "$N" "$D" "$BASE" "$Z" "$acCut"; }
[ $k -eq 0 ] && { [ "$evaluados" -eq 0 ] && printf '\n Ningún repo evaluado: faltan las ramas indicadas arriba.\n' || printf '\n Nada pendiente: todo al día.\n'; }
[ -n "$tagw" ] && printf '\n%sREVISAR TAGS%s (marcados con * en ULTIMO_TAG):\n%b' "$N" "$Z" "$tagw"
