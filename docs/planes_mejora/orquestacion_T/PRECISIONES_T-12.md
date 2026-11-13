# Precisiones del orquestador para T-12 (repositorio listo para sustentación) — cuarta sesión (BORRADOR: falta la respuesta del dueño a tres preguntas)

Base: `origin/main` con T-11 integrado. SIN CAMBIOS DE CÁLCULO. Lee `ORQ/ORQUESTACION.md` (ENMIENDA DE LA CUARTA SESIÓN),
`ORQ/INFORME_T-10_final.md` y `ORQ/INFORME_T-11_final.md` («lo que T-12 debe saber»), y la sección «Cuarta sesión» de
`ORQ/DECISIONES_DUENO_2026-11-12.md`.

- **IDs canónicos**: lo que el prompt llama «INF-5.2» son las filas `INF-5.2.k` del tracker que sigan abiertas (míralas con
  `tests/apoyo/tracker.py`; `INF-5.2.5` lo cerró T-1): di cuáles cierras.
- **Punto 1 (normas)**: la decisión de T-0 es `NORMAS_DIR` (no submódulo). Al retirar `normas/` de la app: `fuentes.ruta_pdf`,
  `python3 -m src.normativa.extraccion`, `verificar_sesion.py`, la guardia de PC-23 (`tests/test_ext6_registro_normativo.py`),
  `fuentes.SOLO_EN_EL_REPO_NORMAS` y los tests `-m pdf` cambian de contrato: sin `NORMAS_DIR` ahora se saltan TODOS los que abren
  un PDF (mide y escribe el número: es el nuevo eje de la tabla de `CLAUDE.md`); con `NORMAS_DIR`, el par no puede bajar.
  **Comprueba ANTES que los 18 PDF que hoy están en `normas/` de la app están, byte a byte (sha1), en el repositorio Normas**
  (`/home/user/andy-rba30/normas/normas/`): si alguno falta o difiere, NO lo retires y repórtalo (el dueño tiene que subirlo).
  El `git rm` no reescribe historia. README: recomendar que Normas sea privado (copyright de AASHTO/ASTM).
- **Punto 2 (material de proceso)**: mover, no borrar, y SIN romper tests: muchos tests leen `CLAUDE.md`, el tracker `.xlsx`
  (`tests/apoyo/tracker.py`, `test_t0_gobernanza`, `test_ext11_cruce_temarios`), `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`
  (su huella), `docs/decisiones_diferidas.md` y `verificar_sesion.py`. Antes de mover nada haz el CENSO de qué archivo de proceso
  lee cada test (grep por ruta) y decide con él: lo que un test del entregable necesita se queda donde está o el test se va con
  el material (los tests de PROCESO —gobernanza de la cadena, cruce de temarios, sincronía del tracker— son también material de
  proceso y pueden vivir en `proceso/tests/` con su propio `conftest`, fuera de la suite del entregable; di cuántos tests salen de
  la suite y cuál es el par nuevo). `docs/decisiones_diferidas.md`, `docs/contrato_entradas.md`, la hoja de ruta v8, los
  manifiestos, `trazabilidad.csv`, `indice_formulas.md`, la guía y los documentos de validación de T-11 SON del entregable: no se
  mueven. `CLAUDE.md` conserva las reglas técnicas; la bitácora de conteos e incidentes de entorno se mueve entera (sin
  resumirla ni reescribirla) a `proceso/`. La carpeta de orquestación de esta cadena vive en la rama `tesis/orquestacion-estado`:
  no la traigas a `main`; déjala referenciada.
- **Punto 3 (fixtures)**: la cabecera de advertencia en las memorias HTML de la línea base NO puede romper `test_linea_base`
  (se regeneran por su script): la advertencia la pone el generador cuando el CSV/los datos son de fixture, o un envoltorio
  declarado; decide la vía que no falsee una memoria real y dila.
- **Punto 4 (LICENSE, pyproject, README)**: [PENDIENTE DEL DUEÑO: licencia y nombre del autor]. `pyproject.toml` con las
  dependencias que `requirements*.txt` ya fijan (no añadas ninguna; weasyprint y ttkbootstrap opcionales como hoy). README de
  usuario: instalación, entradas (remite a `docs/contrato_entradas.md` y a la guía), corrida, salidas, alcance declarado (lo que
  el programa NO hace: armado de la sección del marco de la Familia C, cabezal paralelo a la vía, iteración de zapata, planos,
  hidrología más allá del racional…), y lo que queda para después de la cadena (Figuras 3.3–3.4 de HEC-14, `max(V_c, V_erosion)`).
- **Memoria en dos vistas** [PENDIENTE DE CONFIRMAR CON EL DUEÑO]: memoria RESUMIDA para imprimir (por punto: resultados,
  veredictos, avisos, criterios adoptados y pendientes) y memoria COMPLETA como hoy (anexo digital), las dos de la MISMA corrida
  (`ContextoCorrida`), sin aritmética en M11, con test de que la resumida no publica ningún número que la completa no tenga.
- **Punto 5**: `docs/manifiesto_registro_normativo.md` es GENERADO: el estado final de las fuentes sale del registro
  (`fuentes.py`), no de una edición a mano.
- Ritual de cierre completo; par medido con y sin `NORMAS_DIR`; `CLAUDE.md` con la tabla al día.
