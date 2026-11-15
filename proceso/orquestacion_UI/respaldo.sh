#!/bin/bash
# Respaldo del trabajo en curso en la rama de respaldo, con el estado de la orquestacion.
# Uso: respaldo.sh <ruta del worktree (o del checkout principal)> <etiqueta>
# No toca el indice ni los archivos del worktree: usa un indice temporal.
# Ademas de lo del worktree, mete en proceso/orquestacion_UI/ el ESTADO.md y los
# scripts medir.sh y respaldo.sh, para retomar desde otra sesion.
set -eu
W=$1; L=$2
S=/tmp/claude-0/-home-user-Proyecto-alcantarillas/27447412-9039-5db5-97eb-d2ae1bcdc8b7/scratchpad
RAMA=claude/awesome-mendel-dyj4p4-respaldo
cd "$W"
TMPIDX=$(mktemp)
export GIT_INDEX_FILE=$TMPIDX
git read-tree HEAD
git add -A .
for f in ESTADO.md PROMPT_CONTINUACION.md medir.sh respaldo.sh; do
  if [ -f "$S/$f" ]; then
    B=$(git hash-object -w "$S/$f")
    git update-index --add --cacheinfo "100644,$B,proceso/orquestacion_UI/$f"
  fi
done
# Los ejemplos de la web y los resultados de la validacion (solo texto: json, md, csv, txt; nunca los PDF).
for d in /tmp/ejemplos_web:ejemplos_web /tmp/validacion_web:validacion_web /tmp/revision_validacion:revision_validacion /tmp/revisor_ve1:revisor_ve1; do
  ORIG=${d%%:*}; DEST=${d##*:}
  [ -d "$ORIG" ] || continue
  find "$ORIG" -maxdepth 3 -type f -not -path '*/pdf/*' \( -name '*.json' -o -name '*.md' -o -name '*.csv' -o -name '*.txt' -o -name '*.py' \) -size -5M | while read -r f; do
    B=$(git hash-object -w "$f")
    git update-index --add --cacheinfo "100644,$B,proceso/orquestacion_UI/$DEST/${f#$ORIG/}"
  done
done
ARBOL=$(git write-tree)
unset GIT_INDEX_FILE
rm -f "$TMPIDX"
COMMIT=$(git commit-tree "$ARBOL" -p HEAD -m "respaldo WIP $L ($(date -u +%Y-%m-%dT%H:%MZ)), sobre $(git rev-parse --short HEAD)")
cd /home/user/Proyecto_alcantarillas
for i in 1 2 3 4; do
  if git push -f origin "$COMMIT:refs/heads/$RAMA" 2>&1 | tail -1; then break; fi
  sleep $((i * 2))
done
echo "respaldo $L -> $RAMA = $(git rev-parse --short "$COMMIT")"
