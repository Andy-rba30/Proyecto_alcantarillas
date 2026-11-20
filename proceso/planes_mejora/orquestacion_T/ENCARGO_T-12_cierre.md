# Encargo: T-12 — correcciones de la auditoría corta + INTEGRACIÓN EN MAIN (cierre de la cadena T) — sexta sesión

Eres el agente que CIERRA T-12 (worktree `/home/user/wt/T-12`, rama `tesis/T-12`, HEAD `78a7780`, base `origin/main` = `f77c5d4`).
Sigue `ORQ/ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (PARTE 1 y PARTE 2) con la ENMIENDA DE LA SEXTA SESIÓN de
`ORQ/ORQUESTACION.md`. Lee `ORQ/AUDITORIA_T-12.md` ENTERO (también está en `SP/AUDITORIA_T-12.md`; sus exportaciones y scripts en
`SP/T-12-aud/`) y la última sección de `ORQ/DECISIONES_DUENO_2026-11-12.md` («Decisiones del dueño sobre las preguntas de la FASE A
de T-12»). SIN CAMBIOS DE CÁLCULO; PARADA (c) vigente.

## PARTE 1 — hallazgos (todos se corrigen; resoluciones del orquestador)
- **H1 (ALTA)** — el entregable tiene que pasar su suite sobre una EXPORTACIÓN (`git archive HEAD`, sin `proceso/` ni `.git`):
  (1) `test_sin_literales`: la exención de `proceso` no caduca cuando el árbol es una exportación (declarado en el test: «una
  exportación no lo lleva: `.gitattributes`»); (2) `test_ext11_mutacion::test_el_arnes_mata_de_verdad_un_mutante_conocido` (o
  `mutacion._archivos_del_arbol`): `pytest.skip` sin `.git`, con el motivo dicho, como `test_ext6` y `test_t12`; (3) un test nuevo
  que fije la propiedad sin correr la suite entera (p. ej. que ningún test de `tests/` exija `proceso/` ni `.git` salvo los
  censados con su salto) y **el par MEDIDO sobre la exportación** (suite entera una vez, con `NORMAS_DIR`), escrito en la
  bitácora y en el README §7 junto al del checkout: 0 failed, o no empujas.
- **H2 (MEDIA)** — en la resumida, toda fila cuyo criterio tenga `vacio_verificado` lleva una marca de TEXTO («adopción sobre
  vacío verificado — ver acotaciones en la memoria completa», o la redacción que ya use la casa), sin números; test que la exija.
- **H3 (MEDIA)** — la resumida lleva la línea del corredor, la advertencia de corredor (la misma de la completa, leída del
  `ContextoCorrida`) y una tabla compacta de los [S] usados con valor y origen; test: la advertencia de la completa está en la
  resumida.
- **H4 (MEDIA)** — `proceso/tests/test_t12_proceso.py`: que fije lo que NO debe cambiar (las reglas de corrección, enteras; de la
  bitácora, que el texto histórico de `f77c5d4` siga presente como bloque salvo lo que una actualización legítima cambia —decide
  la forma y dila—) y no impida actualizar la tabla; `proceso/verificar_sesion.py` (y el ritual escrito en la bitácora) corre
  también `python -m pytest proceso/tests`.
- **H5 (MEDIA) — RESOLUCIÓN**: la premisa con la que el dueño aceptó «dejar los siete» (que el entregable los cita) no se
  sostiene para dos de ellos (ni código ni tests los leen, y llevan prompts literales y asignación de modelos, que es lo que
  INF-5.2.2 nombra): **`docs/hoja_de_ruta_correcciones_v12.md` y `docs/auditoria_y_ruta_despliegue_v9.md` se MUEVEN a `proceso/`**
  con `git mv` (mismo criterio que T12-02: las rutas en prosa no se reescriben; `proceso/README.md` las traduce; comprueba antes
  con grep que ningún test ni módulo los abre, y el anclaje de fichas que los nombre). **`docs/ruta_familia_c.md` SE QUEDA** (el
  código lo exige al importar: `vacio_verificado`), y los otros cuatro también. `INF-5.2.2` → **Cerrado con salvedad** que nombra
  `ruta_familia_c.md` y el contenido de proceso que conserva. Ficha T12-02 al día.
- **H6 (BAJA)** — la fila «h_o fuera de rango» del punto llega a la resumida (por el formateador común o por los avisos), sin
  números que la completa no tenga; si no es plomería directa, ficha y repórtalo.
- **H7 (BAJA)** — test de identidad de filas (cada `<tr>` de verificaciones y de combinación de la resumida es subcadena del
  bloque del punto en la completa, salvo la marca de H2) y test de que el estado del expediente de la resumida es el de la
  completa (mejor: compartir el formateador).
- **H8 (BAJA)** — los textos falsos que lista el auditor, corregidos en su sitio (`CLAUDE.md` «Fuente de verdad», comentario de
  `fuentes.py`, docstrings de `test_normativa_pdf`, `test_t0_gobernanza`, `test_decisiones_diferidas`; el rótulo de fixture que
  nombra `entradas_ampliadas.json` donde la corrida no lo usa; README §7: intérprete POSIX, «byte a byte» con el rótulo del
  generador, enlace a `proceso/README.md` ausente en la exportación; `cli.main` con `--pdf` + `--html-resumida` y caída a la vía
  del navegador: la resumida nombra el archivo que DE VERDAD se escribió).
- Subagentes: `.claude/agents/` se queda en `proceso/.claude/agents/`; `proceso/README.md` dice cómo reactivarlos (copiarlos a
  `.claude/agents/` de la sesión que los necesite).

## PARTE 2 — integración (la del encargo común, con lo que T-12 cambió de sitio)
- UN commit `tesis(T-12): … — INF-5.2.2, INF-5.2.3, INF-5.2.4, INF-5.2.7 (cerrados); INF-5.2.6 (en parte)` sobre `origin/main`.
- **Tracker** (`proceso/auditorias/matriz_cruzada_auditorias.xlsx`; responsable «Claude Code (cadena T, T-12)»): `INF-5.2.2`
  Cerrado con salvedad (H5); `INF-5.2.3` Cerrado con salvedad (los PDF siguen en la historia de git; decisión del dueño: no se
  reescribe; recomendado dejar privado el repositorio de la app hasta la sustentación; ficha T12-01); `INF-5.2.4` Cerrado;
  `INF-5.2.6` Cerrado parcial (12 fuentes ausentes: entradas del dueño); `INF-5.2.7` Cerrado (nombre de la carátula y versión:
  marcadores, ficha T12-05); NOTA en `INF-5.2.1` (sigue abierto: sin acción en el prompt; 24 de 84 SHA en el clon superficial).
  Fila de T-12 en `LO_QUE_ESCRIBIO_CADA_PROMPT` (`proceso/tests/test_t0_gobernanza_proceso.py`).
- **Bitácora** (`proceso/bitacora_conteos_y_entorno.md`, donde vive ahora la tabla de `CLAUDE.md`): párrafo de T-12 en el estilo de
  los existentes; tabla de pares con el eje NUEVO (`NORMAS_DIR`: sin él saltan todos los que abren un PDF) y los tres números
  medidos: entregable con `NORMAS_DIR`, entregable sin él, y **exportación** con `NORMAS_DIR`; la suite de proceso aparte; las
  otras configuraciones DERIVADAS, dicho así; cadena de totales. `CLAUDE.md` conserva las reglas técnicas y apunta a `proceso/`.
- Fichas T12 renumeradas a la Parte siguiente libre; documentos generados con su sello; `docs/linea_base.md`; línea base regenerada
  y medida contra `f77c5d4` con el comparador de E-B (los cuatro JSON IGUALES; las memorias completas sólo por el rótulo y T11-09;
  la resumida nueva): **«diámetros / secciones / materiales / HW movidos: ninguno» o NO empujas**.
- README de usuario: el lote posterior aprobado (Figuras 3.3–3.4 de HEC-14; `max(V_c, V_erosion)` en M4; juego de cuencas
  coherente; las dos de MD de T11-03; la forma de `n_manning_cajon`, T11-10; el botón de la memoria resumida en la ventana,
  T12-04) y lo que queda pendiente del dueño (nombre de la carátula y versión; ejemplares de normas ausentes; HY-8).
- Suites: entregable ENTERA con `NORMAS_DIR` y sin él, `proceso/tests`, y la exportación; `git push origin HEAD:main`
  (fast-forward; nunca `--force`); `git fetch`, confirma `origin/main == HEAD`, deja `tesis/T-12` en ese commit y remide el par
  con `NORMAS_DIR` sobre ese árbol.

## Entrega
`SP/INFORME_T-12_final.md` (hallazgo por hallazgo; IDs; tests y los pares medidos; movidos; diferidos con símbolo; lo que queda
pendiente del dueño; lo que NO hiciste; y una sección final **«Estado de la cadena T al cerrar»**: qué `INF-` quedan sin cerrar y
quién los destraba, y el lote posterior) y, como respuesta, MENOS DE 350 PALABRAS con el SHA en `origin/main`, los pares, IDs,
tests, movidos, diferidos y pendientes del dueño.
