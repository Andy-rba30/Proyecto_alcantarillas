PREÁMBULO COMÚN (VE-2, ejecución en paralelo)

Eres una de cuatro sesiones que ejecutan EN PARALELO partes del prompt VE-2 del repositorio
Proyecto_alcantarillas. Trabajas en tu propio git worktree (ya estás en él: tu directorio de
trabajo). El dueño aprobó VE-2 el 2026-11-17 y pidió ejecutarlo todo; la orquestadora repartió
los bloques por archivos para que no choquen. Haz SOLO tu parte.

Lee antes, enteros: CLAUDE.md; proceso/reglas_de_correccion_de_auditorias.md; el bloque
«### VE-2» de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md (hallazgos de la revisión
normativa + el prompt en ```text```: tus pasos están ahí con su número); §1 «Reglas comunes»
del mismo archivo; las fichas VE1-01, VE1-02 (y las que tu parte nombra) de
docs/decisiones_diferidas.md. Los hallazgos de la revisión son punto de partida, NO
verificación: toda cita que uses la verificas tú contra el PDF (numeral, página impresa, texto
literal) y la registras en el registro normativo (src/normativa/) como el resto del proyecto.

ENTORNO (cada comando de shell que corra Python o la suite empieza con esto; el python por
defecto, 3.13, no tiene tkinter):
  export PATH=/tmp/claude-0/-home-user-Proyecto-alcantarillas/5662f60b-e18a-5f3b-9b04-634e8aedadde/scratchpad/bin:$PATH NORMAS_DIR=/home/user/andy-rba30/normas
  (python = 3.12 con tkinter, ttkbootstrap, weasyprint, PyMuPDF, numpy, scipy, pytest; xvfb-run disponible)
  Leer un PDF: python -m src.normativa.extraccion buscar|texto|png <fragmento> ...
  Suite completa: xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header
  La máquina tiene 4 núcleos y otras tres sesiones corren a la vez: durante el desarrollo corre
  SÓLO los tests que tocan lo tuyo (-k, archivos concretos); la suite completa UNA vez al final
  (o dos si tuviste que corregir). Usa timeouts largos.

REGLAS DE ESTA EJECUCIÓN EN PARALELO (para que la integración sea mecánica):
- Tests primero, en rojo (xfail(strict=True) con la expectativa, nunca la salida actual como
  oráculo), y luego verdes. Pon tus tests nuevos en un archivo PROPIO: tests/test_ve2_<tu_parte>.py.
  Cada decisión y corrección comprobada por mutación (anota los mutantes y que murieron).
- Criterios nuevos en src/criterios_adoptados.py: con nivel, forma, sensibilidad, resolución,
  Fundamento; ningún valor de criterio existente cambia. Si un test fija el recuento total de
  criterios (hoy 141: tests/test_ui5_decisiones.py:1305, tests/test_ve1_validacion.py:605),
  súmale los tuyos; la orquestadora resolverá la suma al integrar.
- NO edites: CLAUDE.md, proceso/bitacora_conteos_y_entorno.md, docs/hoja_de_ruta_*.md,
  src/datos_sitio.py. La orquestadora actualiza CLAUDE.md y la bitácora al integrar.
- Documentos generados y línea base: si tu cambio los desfasa, regenéralos con su comando
  (CLAUDE.md, «Tests»; la línea base con su script, ver docs/linea_base.md y
  tests/linea_base_familia_c/README) para que TU suite quede verde, y commitea. Al integrar se
  volverán a regenerar sobre el conjunto; lo que importa de ti es el informe de QUÉ NÚMEROS se
  movieron y por qué.
- Fichas: escribe las tuyas en docs/decisiones_diferidas.md AL FINAL del archivo, bajo un
  encabezado de ficha propio (los nombres que tu parte indica), y en VE1-02 / T1-08 marca
  «Cerrado (VE-2)» sólo el inciso que es tuyo, con una línea.
- Commits en tu rama del worktree, uno por decisión, mensaje en español con el formato de la
  serie: «validacion(VE-2.<bloque>): <qué> — VE1-02 (<letra>)», terminado con:
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_015HTdHiPZWiKxgDKs43cQ4D
  NO empujes nada a origin: la orquestadora integra tu rama.
- Si algo del prompt no se puede hacer sin inventar un valor, o choca con la norma verificada,
  NO lo rellenes: detente en ese punto, déjalo en la ficha y repórtalo.

INFORME FINAL (≤ 500 palabras, en español): nombre de tu rama y lista de commits; qué hiciste
por paso; citas verificadas (numeral, página, PDF); tests nuevos (cuántos, en rojo antes,
mutantes muertos); números de la línea base o de documentos generados que se movieron (con su
causa); resultado de la suite completa (passed / skipped / collected, y los fallos si los hay);
lo que quedó diferido y por qué; archivos tocados fuera de los que tu parte nombra.
