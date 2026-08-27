#!/usr/bin/env bash
# workflow-discover.sh — Lista workflows desde .SAC/workflows
# Uso: ./workflow-discover.sh [directorio]

WORKFLOWS_DIR="${1:-.SAC/workflows}"

if [[ ! -d "$WORKFLOWS_DIR" ]]; then
  echo "No tenemos workflows configurados en ${WORKFLOWS_DIR}"
  exit 0
fi

count=0
for subdir in "$WORKFLOWS_DIR"/*/; do
  [[ -d "$subdir" ]] || continue

  workflow_file="${subdir}workflow.md"
  [[ -f "$workflow_file" ]] || continue

  name=$(awk '/^---$/{n++; next} n==1 && /^name:/{sub(/^name: */, ""); print; exit}' "$workflow_file")
  desc=$(awk '/^---$/{n++; next} n==1 && /^description:/{sub(/^description: */, ""); print; exit}' "$workflow_file")

  phases_dir="${subdir}fases"
  phase_count=0
  if [[ -d "$phases_dir" ]]; then
    phase_count=$(find "$phases_dir" -name "*.md" -type f 2>/dev/null | wc -l)
  fi

  name="${name:-$(basename "$subdir")}"
  desc="${desc:-Sin descripción}"
  count=$((count + 1))

  if [[ $phase_count -gt 0 ]]; then
    echo "${count}. ${name} [${phase_count} fases] — ${desc}"
  else
    echo "${count}. ${name} — ${desc}"
  fi
done

if [[ $count -eq 0 ]]; then
  echo "No encontramos workflows con archivo workflow.md en ${WORKFLOWS_DIR}"
fi
