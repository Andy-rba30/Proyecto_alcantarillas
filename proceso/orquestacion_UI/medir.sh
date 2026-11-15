#!/bin/bash
# Uso: medir.sh <commit> <etiqueta>  -> mide entregable, proceso y exportacion sobre un worktree limpio fuera del repo
set -u
C=$1; L=$2
S=/tmp/claude-0/-home-user-Proyecto-alcantarillas/27447412-9039-5db5-97eb-d2ae1bcdc8b7/scratchpad
W=/home/user/medida_$L
export NORMAS_DIR=/home/user/andy-rba30/normas
cd /home/user/Proyecto_alcantarillas
git worktree remove --force $W 2>/dev/null; rm -rf $W
git worktree add --detach $W $C >/dev/null 2>&1
cd $W
xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header -rs > $S/suite_${L}_entregable.txt 2>&1
xvfb-run -a python -m pytest proceso/tests -q -p no:cacheprovider --no-header -rs > $S/suite_${L}_proceso.txt 2>&1
if [ "${3:-}" = "export" ]; then
  E=/home/user/medida_${L}_export; rm -rf $E; mkdir -p $E
  git archive HEAD | tar -x -C $E
  cd $E && xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header -rs > $S/suite_${L}_export.txt 2>&1
fi
for f in $S/suite_${L}_*.txt; do echo "== $f"; tail -1 $f; done
