# Encargo: AUDITORÍA CORTA de T-12 (repositorio listo para sustentación) — FASE A, antes de integrar (sexta sesión)

Eres el auditor adversarial. SOLO LECTURA sobre el repositorio: no edites archivos del repo ni hagas commits. Intenta REFUTAR el
trabajo de otro agente antes de que entre en `main`. T-12 NO toca cálculo: tu foco es que eso sea verdad, que nada se haya
perdido al mover, y que el entregable se sostenga solo.

- Worktree a auditar: `/home/user/wt/T-12` (rama `tesis/T-12`, HEAD `78a7780`). Base = `origin/main` = `f77c5d4`, desplegada (sólo
  consulta) en `/home/user/wt/main`. Diff: `git -C /home/user/wt/T-12 diff -M f77c5d4 HEAD`.
- `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/` (sólo lectura); `SP` =
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/0d09ea9c-a87f-5311-8eec-38e45d8c2a3d/scratchpad/` (temporales SÓLO en
  `SP/T-12-aud/`). Informe del implementador: `SP/INFORME_T-12_faseA.md` (NO lo des por bueno).
- Lee primero: el bloque «T-12» de `proceso/planes_mejora/09_CADENA_PROMPTS_TESIS.md` (en el worktree), `ORQ/PRECISIONES_T-12.md`,
  `ORQ/ENCARGO_T-12.md`, y de `ORQ/DECISIONES_DUENO_2026-11-12.md` las secciones «Decisiones del dueño para T-12» y las dos últimas
  (T11-09 se aplica en T-12; lote posterior).
- PDF: `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`). python3 3.13, PyMuPDF sí, Tk no.
  Par que el implementador midió: entregable 6374 passed / 23 skipped (collected 6397) con `NORMAS_DIR`, 6222 / 175 sin él;
  `proceso/tests` 142 passed. Nunca `/dev/null` como destino de `cli.py --json`.

## Qué comprobar (como mínimo)
1. **Sin cambios de cálculo.** `git diff f77c5d4 HEAD -- src/ cli.py conftest.py`: cada cambio ¿es plomería de reporte / de
   búsqueda de PDF / documental, o cambia un resultado? En particular: la refactorización de M11 (`_filas_combinacion_adoptada`,
   `_filas_verificaciones`, `_celda_control_gobernante`) no cambia la memoria completa salvo T11-09; M11 sigue sin aritmética (su
   test de AST); la clave `_advertencia` de `--datos-externos` en `servicio` ¿es una puerta estrecha (sólo esa clave, documentada)
   o deja pasar en silencio cualquier clave mal escrita?; `ResultadoHidraulico.salida_no_se_forma` ¿es exactamente la condición
   de `cli.salida_no_se_forma` de la base? Corre el fixture y el juego de T-11 por la CLI sobre la base y sobre HEAD y compáralos
   (`cli.py --comparar`): «IGUALES» o la lista.
2. **Línea base.** `git diff f77c5d4 HEAD -- tests/linea_base_familia_c/`: ¿sólo el rótulo de fixture, la cadena de T11-09 (A-02),
   la línea nueva de `cli_expediente.txt` y la memoria resumida nueva? Los cuatro JSON y los dos CSV, ¿idénticos? ¿El rótulo lo
   pone el GENERADOR de la línea base y no el programa (una memoria real no debe llevarlo)? **Diámetros / secciones / materiales
   / HW movidos: ninguno**, o la lista.
3. **Nada se borró: se movió.** Con `git diff -M --summary f77c5d4 HEAD`: ¿los únicos borrados son los 18 PDF de `normas/`? Cada
   archivo de `docs/planes_mejora/`, `docs/auditorias/`, `.claude/agents/`, `verificar_sesion.py`, `tests/apoyo/tracker.py` y los
   tests de proceso, ¿está en `proceso/` con su contenido (salvo rutas)? Las secciones que salieron de `CLAUDE.md`, ¿están ENTERAS
   en `proceso/` (compara contra `git show f77c5d4:CLAUDE.md`)? ¿`CLAUDE.md` conserva TODAS las reglas técnicas y no dice ya nada
   falso (p. ej. «caída a `normas/`», rutas a `docs/auditorias/…`, «verificar_sesion.py»)? ¿Algún test que SALIÓ de la suite del
   entregable comprobaba algo del ENTREGABLE (y no del proceso) que ahora nadie comprueba?
4. **PDF.** Recalcula tú el sha1 de los 18 PDF de `git show f77c5d4:normas/…` (o de `/home/user/wt/main/normas/`) contra
   `/home/user/andy-rba30/normas/normas/`: ¿los 18 están y son iguales? `fuentes.ruta_pdf`, `python3 -m src.normativa.extraccion`,
   `proceso/verificar_sesion.py` y la guardia de PC-23: ¿encuentran los PDF con `NORMAS_DIR`, saltan/avisan sin él, y un
   `NORMAS_DIR` que apunta a una carpeta inexistente sigue siendo `FileNotFoundError`? Con `NORMAS_DIR`, ¿ningún test `pdf` salta?
5. **El entregable se sostiene solo.** `git -C /home/user/wt/T-12 archive HEAD | tar -x -C SP/T-12-aud/export`: ¿no lleva
   `proceso/`? Corre ahí la suite ENTERA UNA vez con `NORMAS_DIR` (es la propiedad central; ~7 min) y di el par; ¿algún test falla
   o se salta por faltar `proceso/` o `.git`? Sigue el README de usuario al pie de la letra sobre esa exportación (instalación,
   corrida de ejemplo, salidas): ¿cada comando funciona y hace lo que dice? `pyproject.toml`: mismas dependencias y versiones que
   `requirements*.txt`, ninguna nueva.
6. **Memoria en dos vistas.** Genera las dos de la misma corrida (fixture a expediente con `tests/fixtures/entradas_ampliadas.json`,
   y el juego de T-11): ¿la resumida publica algún número, veredicto o aviso que la completa no tenga o que la contradiga? ¿Le
   falta algún aviso de `InformePunto.avisos()`, algún bloqueo o algún criterio pendiente del punto? ¿Imprime como «salida» una
   aproximación descartada? ¿Lleva la misma trazabilidad (huellas, alcance declarado)? El test «ningún número de la resumida falta
   en la completa», ¿es vacuo (p. ej. busca cada número en TODO el HTML en vez de en el bloque del punto)?
7. **Licencia, autor, privacidad.** `LICENSE`: todos los derechos reservados (NO MIT), con la nota de los PDF de normas y de que
   abrirlo es decisión posterior a la sustentación; autor `Andy-rba30` con la línea que dice dónde cambiarlo. `grep -rI` de un
   correo electrónico del autor y de identificadores de modelo en todo el árbol (fuera de `proceso/` y dentro): ninguno nuevo.
8. **Tests nuevos**: vacuos, tautológicos o que pasarían con el defecto. Mutación acotada (≤ 10 min, `tests/apoyo/mutacion.py`)
   sólo sobre la lógica nueva de M11 que decide QUÉ entra en la resumida, si la hay.

## Entrega
Informe en `SP/AUDITORIA_T-12.md`: veredicto (APROBADO / AJUSTADO / RECHAZADO), hallazgos H1… con severidad (BLOQUEANTE / ALTA /
MEDIA / BAJA), evidencia reproducible (comando y salida) y la corrección concreta anclada por símbolo; «refutado con evidencia»
separado de «sospecha»; preguntas para el dueño con recomendación. Respuesta: menos de 300 palabras con veredicto, hallazgos por
severidad, los tres más graves, el par de la suite sobre la exportación, «diámetros movidos» y preguntas para el dueño.
