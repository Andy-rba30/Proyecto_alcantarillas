# Prompt para retomar VE-3 desde otra sesión

Se mantiene al día con cada integración. Copia el bloque `text` en una sesión nueva de Claude
Code sobre `Andy-rba30/Proyecto_alcantarillas`.

```text
Retoma VE-3 del repositorio Andy-rba30/Proyecto_alcantarillas. Lee enteros CLAUDE.md, proceso/reglas_de_correccion_de_auditorias.md y proceso/planes_mejora/ve3_estado/LEEME.md (estado, decisiones del dueño, decisiones pendientes con su recomendación, ramas de respaldo). Trabaja en la rama claude/cool-euler-tpoj7o (git fetch origin claude/cool-euler-tpoj7o), que continua claude/festive-bell-wrmps1; lee primero el bloque «ESTADO (2026-11-18 ...)» del LEEME, que dice el orden de trabajo vigente. Las ramas claude/youthful-shannon-rjzmuc* y claude/festive-bell-wrmps1* ya no se tocan. main NO se toca sin autorización del dueño. El dueño no lee el chat: las preguntas van al LEEME («Decisiones pendientes del dueño») con tu recomendación, y todo informe se copia al repo.

Entorno: python 3.12 con tkinter (si el del sistema no lo trae, `uv python install 3.12` y un venv), `pip install -r requirements.txt PyMuPDF "pillow<13"` (openpyxl sólo para leer las hojas de CDOT), xvfb; clona Andy-rba30/Normas y export NORMAS_DIR=<clon> (trae normas/ y ejemplos_resueltos/). Suite: `xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header` en un clon LIMPIO fuera del repositorio (los worktrees bajo .claude/ hacen fallar test_sin_literales) y en una exportación (git archive HEAD). Para regenerar la línea base pon el python del venv primero en el PATH (sh tests/linea_base_familia_c/regenerar.sh).

Qué falta, en orden (al día 2026-11-20; VE-3.1 a VE-3.16 hechos y la hoja de ruta corregida por el dueño en VE3-20 y VE3-21, ver el bloque «ESTADO (2026-11-20 ...)» del LEEME):
1. Si la bitácora no tiene la fila de 2026-11-20: medir la suite completa en un clon limpio y en la exportación (`git archive HEAD`) sobre la punta de la rama; si algo falla, corregirlo declarando la causa.
2. Sellar con el par medido: `python -m src.normativa.manifiesto --escribir --suite "<N> passed, <M> skipped (PyMuPDF sí · ventana Tk sí · repositorio de normas enlazado)"` y `python -m src.indice_formulas --escribir --suite "<lo mismo>"` (si llevan el sello PROVISIONAL «0 passed, 0 skipped»); fila en proceso/bitacora_conteos_y_entorno.md con los dos pares.
3. Integrar en main SOLO con autorización expresa del dueño (fast-forward; la rama no está por detrás de main).
4. Abierto por obra, no del programa: el sismo del cabezal se cierra declarando reduccion_por_desplazamiento + cedente con detalle de juntas, aceptación del Propietario y el EMS real.
```
