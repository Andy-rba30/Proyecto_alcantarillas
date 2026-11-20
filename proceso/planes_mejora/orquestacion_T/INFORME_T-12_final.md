# INFORME T-12 · CIERRE (correcciones de la auditoría + integración en `main`) — último prompt de la cadena T

- **Commit en `origin/main`:** `07ef2960c3eef25a1b66cde0e8219c6123babf14` (`07ef296`) — UN commit `tesis(T-12): …` sobre `f77c5d4` (fast-forward).
- **Rama `tesis/T-12`:** dejada en ese mismo commit. `tesis/T-12-cierre-wip`: el mismo commit (respaldo).
- **Quién hizo qué.** Este cierre lo retomé yo tras el reinicio del contenedor que se llevó al agente anterior a
  media integración. Encontré en disco `6f121e0` (el aplastado del agente anterior, sin empujar a `main`) y en el
  remoto `f2b7880` (la serie `wip(T-12)` con las correcciones H1–H8). **Comprobé** cada punto del encargo contra el
  árbol (lectura del código y de los tests, y las corridas de abajo, todas mías); **completé** lo que faltaba (la
  bitácora de T-12 con el eje nuevo de `NORMAS_DIR` y el par de la exportación, el README §7 —que tenía un marcador
  `[[PARES_README]]` sin rellenar—, `docs/linea_base.md` §8, los sellos con el par final, el mensaje del commit),
  **medí** las cuatro suites sobre el commit que se empuja, y lo integré.
- **Sin cambios de cálculo.** `git diff f77c5d4 HEAD -- src/modulos/` sólo toca `M11_reporte.py` (plomería de reporte,
  sin aritmética: su test de AST pasa). **Diámetros / secciones / materiales / HW movidos: ninguno.**

## 1. Hallazgos de la auditoría (AJUSTADO: 1 ALTA, 4 MEDIA, 3 BAJA)

Todos los encontré ya implementados en `f2b7880` (agente anterior) y los **verifiqué yo**: leí el cambio, corrí sus
tests en las suites finales (verdes) y **medí su rojo** con los dos archivos finales (`tests/test_t12_entregable.py`,
`proceso/tests/test_t12_proceso.py`) contra la FASE A `78a7780`: **29 failed, 65 passed de 94** (los verdes son tests
de la FASE A que no cambian y guardias). Lo que hice yo, por hallazgo, va dicho.

| H | Sev. | Estado | Qué hay (símbolos) | Mío |
|---|---|---|---|---|
| H1 | ALTA | **cerrado** | `test_sin_literales.AUSENTES_EN_UNA_EXPORTACION` (la exención de `proceso` no caduca donde la exportación no lo lleva); `test_ext11_mutacion.MOTIVO_SIN_GIT` (el arnés se salta sin `.git`); `test_t12_entregable.REQUIEREN_GIT` + `test_solo_los_censados_invocan_git_y_sus_tests_se_saltan_sin_el` (censo estático, sin correr la suite) y `test_la_suite_del_entregable_pasa_sobre_una_exportacion` (`lento`, exportación emulada). | **El par MEDIDO sobre la exportación real** (`git archive 07ef296` → `SP/T-12/export_final`, suite entera, `NORMAS_DIR`): **6398 passed, 27 skipped, 0 failed**; escrito en la bitácora y en el README §7 (que tenía el marcador sin rellenar). |
| H2 | MEDIA | **cerrado** | `M11.MARCA_VACIO_VERIFICADO` en `_filas_verificaciones` cuando no hay remisión; test `test_la_resumida_marca_la_adopcion_sobre_vacio_verificado` (≥ 2 en el juego de T-11: G1 de B-01, V9 de C-01). | verificado |
| H3 | MEDIA | **cerrado** | `M11.datos_sitio_resumidos` y `_cabecera_de_corredor` (compartida con la completa); línea del corredor, advertencia y tabla de [S] con valor y origen; tests `..._lleva_el_corredor_su_advertencia_y_el_origen_de_cada_S`, `test_datos_sitio_resumidos_es_la_seccion_de_S_de_la_resumida`. | verificado |
| H4 | MEDIA | **cerrado** | `proceso/tests/test_t12_proceso.py`: las reglas de corrección, byte a byte contra `f77c5d4`; la bitácora, por SUBSECUENCIA de palabras con las cifras libres (se puede insertar y actualizar conteos; borrar o reescribir una palabra sin cifra la pone en rojo) + test de que la comprobación no es vacua; `proceso/verificar_sesion.py` paso 1-bis corre `proceso/tests`. | La primera actualización real de la bitácora (la mía) la puso en rojo al cambiar «Sin él,» por «Sin él —…»: lo corregí insertando sin reescribir. Prueba de que el test hace lo que dice. |
| H5 | MEDIA | **cerrado** (resolución del orquestador) | `docs/hoja_de_ruta_correcciones_v12.md` y `docs/auditoria_y_ruta_despliegue_v9.md` → `proceso/` con `git mv` (comprobado: ningún test ni módulo los abre; sólo prosa); `docs/ruta_familia_c.md` se queda (lo exige `vacio_verificado` al importar); `proceso/README.md` traduce las rutas; ficha T12-02 y fila `INF-5.2.2` «Cerrado» CON SALVEDAD que nombra `ruta_familia_c.md` y los otros cuatro documentos. | verificado (grep de lectores) |
| H6 | BAJA | **cerrado** | `M11._filas_h_o` dentro de `_filas_combinacion_adoptada` (las dos vistas; el orden de la completa no cambia: medido, las memorias completas de la línea base sólo cambian por el rótulo y T11-09); test `test_la_fila_h_o_del_punto_llega_a_las_dos_vistas`. | verificado |
| H7 | BAJA | **cerrado** | `M11.estado_del_expediente` (un formateador para las dos vistas); `test_cada_fila_de_la_resumida_es_una_fila_de_la_completa` (identidad de `<tr>`, salvo la marca de H2) y `test_el_estado_del_expediente_es_el_mismo_en_las_dos_vistas`. | verificado |
| H8 | BAJA | **cerrado** | `CLAUDE.md` «Fuente de verdad»; comentario de `fuentes.py` (sin `SOLO_EN_EL_REPO_NORMAS`); docstrings de `test_normativa_pdf`, `test_t0_gobernanza` (ítem 5), `test_decisiones_diferidas` (la regla 4 vive en `proceso/`); `rotulo_fixture.BLOQUE` sin nombrar `entradas_ampliadas.json`; README §7 con el intérprete POSIX y «byte a byte … más el rótulo del generador»; `proceso/README.md` nombrado sin enlace, diciendo que la exportación no lo lleva; `cli.main` nombra en la resumida la completa que DE VERDAD se escribió (`escritas`, el `.html` de la vía del navegador); test `test_la_resumida_nombra_la_completa_que_de_verdad_se_escribio`. | verificado |
| Subagentes | — | **hecho** | `.claude/agents/` → `proceso/.claude/agents/`; `proceso/README.md` dice cómo reactivarlos (copiarlos al `.claude/agents/` de la sesión que los necesite). | verificado |

## 2. IDs (canónicos) — tracker `proceso/auditorias/matriz_cruzada_auditorias.xlsx`

Filas escritas por el agente anterior en `6f121e0`; las leí con `openpyxl` y coinciden con el encargo (responsable
«Claude Code (cadena T, T-12)»; la columna Commit dice «commit que sigue a f77c5d4 en origin/main», como las
anteriores). Fila de T-12 en `LO_QUE_ESCRIBIO_CADA_PROMPT` (`proceso/tests/test_t0_gobernanza_proceso.py`): verde.

| ID | Estado | Nota |
|---|---|---|
| `INF-5.2.2` | **Cerrado con salvedad** (Estado «Cerrado», texto «CON SALVEDAD», precedente INF-0.5) | material de proceso en `proceso/`; salvedad: `ruta_familia_c.md` y otros cuatro documentos técnicos de origen de proceso en `docs/`; rutas en prosa sin reescribir. Ficha T12-02. |
| `INF-5.2.3` | **Cerrado con salvedad** | 18 PDF retirados (sha1 = Normas); siguen en la historia de git (decisión del dueño: no se reescribe; app privada hasta la sustentación). Ficha T12-01. |
| `INF-5.2.4` | **Cerrado** | rótulo de fixture (generador), `_advertencia`, cabeceras. Ficha T12-03. |
| `INF-5.2.6` | **Cerrado parcial** | manifiesto en su estado final; 12 fuentes ausentes = entradas del dueño. |
| `INF-5.2.7` | **Cerrado** | LICENSE, pyproject, README; carátula y versión, marcadores (ficha T12-05). |
| `INF-5.2.1` | Abierto + NOTA | sin acción en el prompt; 24 de 84 SHA en el clon superficial. |

## 3. Tests y pares (TODOS medidos por mí, «PyMuPDF sí · ventana Tk no», Python 3.13)

**Sobre el commit que se empuja, `07ef296`** (clon limpio y exportación):

| Suite / árbol | `NORMAS_DIR` | passed | skipped | collected | failed |
|---|---|---|---|---|---|
| entregable, checkout (`python -m pytest`) | sí | 6402 | 23 | 6425 | 0 |
| entregable, checkout | no | 6250 | 175 | 6425 | 0 |
| entregable, **exportación** (`git archive 07ef296`, sin `proceso/` ni `.git`) | sí | 6398 | 27 | 6425 | 0 |
| proceso (`python -m pytest proceso/tests`) | sí / no | 145 / 145 | 0 | 145 | 0 |
| entregable, **`origin/main` tras el push** | sí | 6402 | 23 | 6425 | 0 |

Pre-medida sobre `6f121e0` (el aplastado del agente anterior; base de los sellos): 6402 / 23 con `NORMAS_DIR`, 6250 / 175
sin él, exportación 6398 / 27, proceso 145 / 145 — idénticas.

- **Qué salta.** Con `NORMAS_DIR`: 13 de ventana real + 10 de diseño (`test_familias_del_csv`). Sin él, +152: los 150
  `pdf` (un solo motivo, `conftest.pytest_runtest_setup`), la mitad de PC-23 que mira el repositorio enlazado y el sha1
  de los dos PDF censados. Exportación, +4: `test_ext11_mutacion` (arnés, sin `.git`), `test_ext6_registro_normativo`
  (`git ls-files`), y en `test_t12_entregable` el de `git check-attr` y el de la exportación emulada.
- **Contabilidad.** Base `f77c5d4`: 6469. Salen 138 a `proceso/tests` (119 cruce de temarios, 16 de gobernanza T-0 +
  `verificar_sesion`, 1 de las 22 fichas, 2 anclajes). Entran 94 al entregable (88 de `test_t12_entregable.py`: 61 FASE A +
  27 cierre; 6 anclajes T12-01, -03..-07) y 7 a proceso (6 de `test_t12_proceso.py`, anclaje T12-02). 6469 − 138 + 94 =
  6425; 138 + 7 = 145; suma 6570 = 6469 + 101. Ninguno de los 101 lleva `pdf` (siguen 150) ni depende de Tk.
- **Derivadas, no medidas** (sin tkinter en el contenedor; quitar PyMuPDF apagaría la verificación), con `NORMAS_DIR`:
  sí·sí 6415 / 10; no·sí 6266 / 159; no·no 6253 / 172 (misma derivación que T-11: +13 de Tk, −149 sin PyMuPDF).
- **Censos sin mover:** 141 criterios, 20 sin valor, 507 citas, 150 `pdf`, ninguna marca `literal-ok` nueva en `src/`,
  techos de `test_ext8` sin tocar.
- **Sellos.** `docs/trazabilidad.csv` y `docs/indice_formulas.md` regenerados sobre el árbol LIMPIO de `6f121e0` con el
  par medido allí (6402 passed, 23 skipped …): el sello dice `6f121e0`, que no es el commit de `main` (no puede: el
  sello va dentro del commit) ni queda en una rama remota tras el `--force-with-lease` de la wip — el mismo caso que
  `64e9f28` en el sello de T-11. Los cuerpos generados son idénticos en el commit final (lo comprueban los tests de
  sincronía, verdes). Los dos manifiestos no cambiaron (0 referencias resincronizadas).

## 4. Línea base (medida por mí contra `f77c5d4`)

- `cli.py --comparar` de los cuatro JSON (`informe_expediente`, `informe_rama_error`, `informe_perfil_ancho`,
  `informe_familia_c`) de `f77c5d4` contra los del commit: **IGUALES los cuatro**.
- Byte a byte: idénticos los dos CSV, `cli_familia_c.txt`, `cli_perfil.txt`, `cli_perfil_ancho.txt`, `cli_rama_error.txt`
  y `punto_cajon.py`.
- Memorias completas, diff por línea quitado el rótulo: `memoria_expediente.html`, `memoria_perfil.html` y
  `memoria_punto_cajon.html` sólo el rótulo (título + bloque); `memoria_perfil_ancha.html` además UNA cadena, la de
  T11-09 en A-02: `(entrada 0.572 / salida 0.560)` → `(entrada 0.572 / salida no se forma: el perfil no alcanza la entrada)`.
- `cli_expediente.txt` +1 línea («Memoria resumida (HTML)»); `memoria_resumida_expediente.html` nueva;
  `entradas_ampliadas.json` + `_advertencia`; `regenerar.sh` y README de la carpeta.
- `test_linea_base` (regenera con `regenerar.sh` y compara) verde en las suites finales.
- **Diámetros / secciones / materiales / HW movidos: ninguno.**

## 5. Lo que escribí yo en este cierre

- `proceso/bitacora_conteos_y_entorno.md`: párrafo de T-12 (delante del de T-11), invariante «hoy 6425» (+ proceso 145),
  el eje de `NORMAS_DIR` (152), la cadena de totales (`T-12: 6425 …, 138 a la de proceso (145)`), la tabla de las cuatro
  configuraciones (sí·no MEDIDA, las otras tres DERIVADAS, dicho así), «Tras T-11 la tabla decía …», y una tabla nueva
  con los tres pares del entregable (checkout con/sin `NORMAS_DIR`, exportación) y los dos de proceso. Todo por
  inserción y cambio de cifras: el test H4 de proceso, verde.
- `README.md` §7: el marcador `[[PARES_README]]` (sin rellenar en `6f121e0`) sustituido por la tabla medida y qué salta.
- `docs/linea_base.md` §8 (T-12).
- Sellos de `docs/trazabilidad.csv` y `docs/indice_formulas.md`; mensaje del commit con cuerpo y pares.

## 6. Diferidos con símbolo (Parte LV de `docs/decisiones_diferidas.md`)

T12-01 `src/normativa/fuentes.py::RUTA_SIN_ENLACE` (historia de git con los PDF) · T12-02
`proceso/tests/conftest.py::pytest_collection_modifyitems` (cinco documentos de origen de proceso en `docs/`, rutas en
prosa) · T12-03 `tests/apoyo/rotulo_fixture.py::rotular` · T12-04 `src/modulos/M11_reporte.py::memoria_resumida_html`
(botón de la ventana → lote posterior) · T12-05 `tests/test_t12_entregable.py::test_pyproject_fija_las_mismas_versiones_que_requirements`
(carátula y versión) · T12-06 (rojo no primero) · T12-07 `tests/test_t12_entregable.py::test_la_suite_del_entregable_pasa_sobre_una_exportacion`.

## 7. Pendiente del dueño

1. **Nombre de la carátula y versión** (`LICENSE`, `pyproject.toml`: hoy `Andy-rba30` y `0.1.0`, marcadores; ficha T12-05).
2. **Dejar privado el repositorio de la app** hasta la sustentación (lo hace el dueño en GitHub; T12-01). Los PDF siguen
   en la historia.
3. **Ejemplares de normas ausentes** (12; entre ellos AASHTO M 294 original, un M 170M legible, Ley 29338, series
   SENAMHI/ANA, EMS): `docs/manifiesto_registro_normativo.md` §2.
4. **Corrida de HY-8** con `docs/validacion_hy8.md`, y los **datos reales del proyecto** (contrato de entradas §7).
5. Lanzar (o no) el **lote posterior** (§9): no se lanza sin avisarle.

## 8. Lo que NO hice

- No toqué cálculo, ni `gui/`, ni el botón de la resumida (T12-04, lote posterior).
- No reescribí la historia de git ni cambié la visibilidad de ningún repositorio.
- No medí sí·sí, no·sí ni no·no (derivadas).
- No corrí `python3 -m proceso.verificar_sesion` entero (corre las suites otra vez y pide limpiar ramas remotas, que
  no son de este prompt); corrí sus pasos 1 y 1-bis a mano (las suites de arriba).
- No reescribí el rojo de la FASE A (26 failed + 32 errores contra `f77c5d4`, medido por el agente de la FASE A): cito
  su número; el rojo de las correcciones sí lo medí yo.
- No abrí pull requests; ningún correo ni identificador de modelo nuevo en el repositorio (comprobado con grep sobre
  lo añadido).

## 9. Estado de la cadena T al cerrar

Con `tesis(T-12)` en `main`, **la cadena T queda cerrada**. De las 64 filas `INF-` del tracker, siguen sin «Cerrado»:

| ID | Estado | Qué falta | Quién lo destraba |
|---|---|---|---|
| `INF-5.2.1` | Abierto (NOTA) | SHA citados que no están en el clon superficial (24 de 84 presentes) | nadie en la cadena; medir con un clon completo (`git fetch --unshallow`) |
| `INF-3.2.9` | Abierto (diferido, ficha T2-06) | el segundo indicador de sedimentación de HDS-5 §5.3.3 (n del cauce natural) | el n del cauce por punto (estudio hidrológico / inspección) + una regla que adopte el proyectista |
| `INF-5.2.6` | Cerrado parcial | 12 fuentes citadas sin PDF | el dueño (ejemplares) |
| `INF-5.1.8` | Cerrado parcial | comprobar que `area_ha` de la Familia B es el área del tramo de cuneta (T9-07) | el estudio hidrológico |
| `INF-3.1.1` | Cerrado parcial | delimitación de la cuenca sobre plano | el estudio hidrológico |
| `INF-3.1.4` | Cerrado parcial | quién fija R y n del periodo de retorno | el Propietario (`riesgo_admisible_propietario`) |
| `INF-3.2.2` | Cerrado parcial | la corrida de HY-8 | el autor (`docs/validacion_hy8.md`) |
| `INF-3.2.6` | Cerrado parcial | adoptar «aviso» en `borde_libre_bajo_tw_ahogante` exige el nivel del receptor medido | levantamiento del receptor |
| `INF-3.2.8` | Cerrado parcial | sección y caudal medidos del dren | ANA / Junta de Usuarios |
| `INF-3.4.4` | Cerrado parcial | E4/E5 sin evaluar (T7B-07), Meyerhof en talud vacío, zapata sin iterar (T7B-09) | EMS y decisión del dueño |
| `INF-4.3` | Cerrado parcial | cabezal paralelo a la vía del marco (Carta 11, T7A-03) | alcance declarado por el dueño; trabajo posterior |
| `INF-3.2.3`, `INF-3.3.2`, `INF-3.3.6` | N/A (sin trabajo) | — | — |
| `INF-3.2.5` | Verificado (sin corrección) | — | — |

**Lote posterior a la cadena** (aprobado por el dueño; **no se lanza sin avisarle**): digitalizar las Figuras 3.3–3.4 de
HEC-14 (T8-08); `max(V_c, V_erosion)` en la banda de régimen de M4 (T8-09); juego de cuencas de prueba coherente
(prioridad baja); las dos correcciones de diagnóstico de MD de T11-03 (abiertos 3 y 4); abrir la forma de
`n_manning_cajon` al par de HDS-5 B.3 (T11-10); el botón «memoria resumida» en la ventana (T12-04). El README de usuario
(§8) los lista, con lo pendiente del autor.
