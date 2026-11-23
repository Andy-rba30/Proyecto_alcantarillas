# Prompt genérico para retomar tras un corte

Copia el bloque y pégalo en una sesión nueva de Claude Code sobre `Andy-rba30/Proyecto_alcantarillas`.

```text
Retoma el cierre del proyecto Proyecto_alcantarillas donde se cortó la sesión anterior y SIGUE HASTA TERMINAR, sin pedirme confirmación. Objetivo: todo el código cerrado, integrado, verificado, sellado y en `main`.

1. ESTADO PRIMERO
   - `git fetch origin --tags` y `git ls-remote --heads origin`.
   - Lee `proceso/planes_mejora/ve3_estado/LEEME.md` de la rama más avanzada (`git ls-remote --heads origin`: desde el 2026-11-23 por la tarde es `claude/nifty-brahmagupta-rfj9o6`, que contiene a `claude/serene-keller-2p7pcs` y a sus ramas, o la que la contenga; compara con `git log A..B` y usa la que contenga a las demás). El bloque más reciente («CIERRE ... EN CURSO» / «ESTADO») dice qué está hecho, qué falta y desde dónde seguir.
   - Revisa TODAS las ramas: para cada una, `git rev-list --count <rama_más_avanzada>..<rama>`; lo que no esté contenido, lee sus commits y fichas en `docs/decisiones_diferidas.md` y decide si falta integrarlo o está superado (dilo).
   - Dime en pocas líneas qué falta antes de seguir, y sigue.

2. ENTORNO
   - Entorno de la nube «proyecto_alcantarillas» (PyPI habilitado).
   - Normas: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/Andy-rba30/normas /home/user/andy-rba30/normas` y `export NORMAS_DIR=/home/user/andy-rba30/normas`. Una sesión que verifica NO cierra con los tests `-m pdf` saltados.
   - Tk: fuentes apt a `https://` en `/etc/apt/sources.list.d/ubuntu.sources`, `apt-get install -y python3-tk python3-pil.imagetk`.
   - Dependencias: `NO_PROXY=localhost no_proxy=localhost /usr/bin/python3.12 -m pip install --break-system-packages -r requirements.txt -r requirements-dev.txt pytest-xdist`.
   - `python3` puede ser 3.13 sin dependencias: para scripts que llaman `python3` (p. ej. `regenerar.sh`) antepón al PATH una carpeta con `python3 -> /usr/bin/python3.12`.
   - Suite completa: SIEMPRE en un worktree limpio fuera del repo (`git worktree add <scratchpad>/limpio HEAD`), con la máquina libre: `NORMAS_DIR=... xvfb-run -a /usr/bin/python3.12 -m pytest -q -n 4 -p no:cacheprovider -rfE`. Corrige fallos corriendo sólo los archivos afectados y deja UNA corrida completa final para el sello.

3. REGLAS
   - Respeta `CLAUDE.md`: nunca inventar valores; si la norma no lo dice, criterio [A] sin valor y el cálculo se detiene.
   - Toda duda, ambigüedad técnica o recomendación la verifica y aprueba un agente Fable (`model: "fable"`), experto en programación e ingeniería, con apego estricto a la normativa (MTC, EG-2013, E.060, E.030, E.050, Manual de Hidrología, HDS-5, HEC-14, AASHTO LRFD). Aplica su dictamen y regístralo en el commit y en la ficha.
   - Trabaja en paralelo con agentes cuando ayude, cada uno en su rama/worktree, sin choque de archivos.
   - Commits atómicos; añade sólo tus archivos (nunca `git add -A` con worktrees dentro del repo).
   - GUARDA EL PROGRESO: actualiza el bloque de estado del LEEME y haz `git push` en cada hito y como mínimo cada ~20 minutos. Nunca force-push ni reescribir historia.
   - Avísame de lo que vayas encontrando que falte.

4. ORDEN PARA TERMINAR (salta lo que el LEEME diga que ya está hecho)
   a) Integrar en la rama de trabajo lo que falte de las ramas de VE.
   b) Regenerar documentos: `sh tests/linea_base_familia_c/regenerar.sh`; `python -m tests.apoyo.validacion_hidrologica --escribir`, `validacion_externa`, `validacion_conducto`, `validacion_cabezal` (todos con `--escribir`) y `validacion_integral --escribir` (~30 min); bloques de `docs/guia_perfil.md` desde `python -m tests.apoyo.guia_perfil` (imprime los bloques; empalmarlos entre sus marcas); `python -m tests.apoyo.sensibilidad --escribir` (~35 min).
   c) Suite completa en worktree limpio con NORMAS_DIR; corregir todo fallo (dudas → Fable).
   d) Sellar con el par medido: `python -m src.indice_formulas --escribir --suite "N passed, M skipped (PyMuPDF si, Tk si)"` y `python -m src.normativa.manifiesto --escribir --suite "<mismo par>"`; comprobar aparte los tests de sello.
   e) Fila en `proceso/bitacora_conteos_y_entorno.md`; actualizar el LEEME.
   f) Fast-forward de `main` (y de `v2/mantenibilidad-y-uso` si sigue viva) a la rama final, sólo con la autorización del dueño en esa sesión (main está enlazado para avanzar por fast-forward); etiqueta `respaldo-AAAA-MM-DD`.
   g) Limpieza: antes de borrar una rama superada, etiqueta `respaldo/<rama>` en su punta; si el borrado se deniega, déjalas y repórtalo.

5. ENTREGA: resumen conciso — tareas cerradas, estado final de las ramas, decisiones de Fable con su justificación, y lo que queda como bloqueo declarado (dato o documento externo).
```
