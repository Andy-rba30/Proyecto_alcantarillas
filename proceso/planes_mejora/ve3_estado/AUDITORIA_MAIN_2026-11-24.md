# Auditoría independiente de `main` tras el plan de mantenibilidad y las rondas de Windows (2026-11-24)

Material de proceso (`proceso/`), no del entregable. Auditoría adversarial e
independiente del commit `1f56d99` (`origin/main`), que cierra el plan
`proceso/planes_mejora/11_PLAN_MANTENIBILIDAD_Y_USO.md` (bloques A a D), los
hallazgos H1 a H5 de la auditoría del 21-11
(`AUDITORIA_CIERRE_VE7_2026-11-21.md`, `main` en `362beb4`) y las rondas 1 y 2
de compatibilidad Windows (fichas WIN-01 a WIN-03). Son 59 commits
(`git log --oneline 362beb4..1f56d99 | wc -l` = 59). No se modificó ningún
archivo aparte de este informe y no se hizo commit.

## Dictamen

**APROBADO CON CAMBIOS.**

- El plan cumplió su principio 1: **ningún número calculado cambió**. Está
  comprobado por tres vías independientes (§3.3), no por la declaración.
- El sello **sí corresponde a una corrida medida**, con su registro en disco,
  y H1 a H5 están cerrados (H2 con una reserva de margen, hallazgo N6).
- Las particiones D0 a D3 son correctas: mismos nombres, mismos objetos,
  mismo AST, y las guardias por AST siguen viendo el código movido (tres
  mutantes sembrados, tres muertos).
- Lo que falta antes de dar la entrega por cerrada **no es de cálculo**:
  la confirmación en Windows (N1), el trabajo `completa` de la CI de `main`
  sobre `1f56d99`, que seguía en curso al cerrar este informe (el `rapida`
  ya está en verde, §3.1), y el `README.md`, que es la puerta del entregable
  y no se enteró del plan (N3).

| Nota | 21-11 (`362beb4`) | 24-11 (`1f56d99`) |
|---|---|---|
| **Global** | 8.5 / 10 | **8.8 / 10** |
| **Eje «mantenibilidad y uso»** | 6.5 / 10 | **7.8 / 10** |

El plan estimaba «~8 en el eje y ~9 global» con los bloques A, B y **C1**
(§6 del plan). C1 (el piloto real) no se hizo, la receta del ejecutable no se
ha construido nunca y Windows está sin confirmar: por eso el eje queda en 7.8
y no en 8.

## 1. Entorno y método

- Contenedor Linux, 4 núcleos (`nproc` = 4), **ocupados durante toda la
  auditoría por otra corrida completa** (`uptime`: carga 4.1 a 4.8). Por eso
  no se corrió la suite entera ni `-n` > 1: sólo tests puntuales y medidas
  livianas.
- `/usr/bin/python3.12` (3.12.3), pytest 9.1.1, pytest-xdist 3.8.0, numpy
  2.2.3, scipy 1.15.2, PyMuPDF; Tk con `xvfb-run -a`;
  `NORMAS_DIR=/home/user/andy-rba30/normas`.
- Árbol limpio desacoplado: `git worktree add --detach
  <scratchpad>/auditoria 1f56d99` (`git status --short | wc -l` = 0 antes y
  después; los tres mutantes de §4.3 se revirtieron con `git checkout -- src`).
  Árbol de comparación: `git archive 362beb4` extraído en
  `<scratchpad>/arbol_362`.
- Leído: `CLAUDE.md` (78 líneas), `docs/guia_del_desarrollador.md` (145),
  `docs/manual_usuario.md` (162), `README.md` (359), la auditoría del 21-11,
  el plan 11 (§0, §1, §6, §8), la bitácora (sección del cierre, líneas 2822 a
  2860), `ve3_estado/LEEME.md`, `.github/workflows/pruebas.yml`,
  `pyproject.toml`, `requirements*.txt`, `.gitattributes`,
  `empaquetado/proyecto_alcantarillas.spec`, los `__init__.py` de los cuatro
  subpaquetes, las fichas WIN-01 a WIN-03, y los diffs de `404d06c`,
  `cd45995`, `fbbde5b`, `3d8a8ea`, `5248a36`, `1961b4a` y de `src/` entre
  `362beb4` y `1f56d99`.
- Registros de la sesión de cierre que quedaron en el scratchpad y se leyeron
  como evidencia: `suite.sh`, `suite_completa.log`, `suite_export.sh` y
  `suite_export.log` (este último, en curso).

Lo que se corrió, con su salida:

| Comprobación | Resultado |
|---|---|
| `tests/test_linea_base.py` (worktree `1f56d99`, `python3` → 3.12 al frente del PATH) | **`5 passed in 5.97s`** |
| 14 archivos de guardias y sincronía, `-m "not lento"`: `test_d0_subpaquetes_ast`, `test_d2_catalogo_de_fichas`, `test_ext9_paquete_servicio`, `test_guardias_de_la_suite`, `test_sin_literales`, `test_indice_formulas`, `test_trazabilidad_csv`, `test_manifiesto_citas`, `test_decisiones_diferidas`, `test_plantillas`, `test_c4_bloqueos_gui`, `test_t12_entregable`, `test_nivel_medido`, `test_cierre_perfil` | **`647 passed, 137 deselected in 115.13s`** |
| `pytest -m aislado` (sin `-n`), tres veces, **con la máquina cargada** | `1 failed` (primera), `1 passed`, `1 passed` (hallazgo N6) |
| Tres mutantes sembrados en los subpaquetes (§4.3) | 3 de 3 detectados |
| `gh run list` / `gh run view` sobre el repositorio | §3.1 |

Lo que **no** se corrió: la suite completa, la suite rápida entera, la
exportación (`git archive`) y nada en Windows. Las cifras de esas corridas que
aparecen abajo se **leen** de los registros y de GitHub Actions, y se dice de
dónde.

## 2. Notas

### 2.1 Eje «mantenibilidad y uso»: 6.5 → 7.8

| Concepto | Medida (de dónde sale) | Efecto |
|---|---|---|
| **A. Suite en dos velocidades** | CI serie de `362beb4`: 2 h 27 min (run `44859160957`). Hoy: suite rápida en la CI `8734 passed, 173 skipped` en 15 min 25 s (run `45228860806`) y `8743 passed` en 17 min 00 s (run `45305926473`); completa local `-n 4 --dist loadfile` en 1 h 39 min 51 s (`suite_completa.log`). 23 archivos con `pytest.mark.lento`, con guardia bidireccional por AST (`tests/test_guardias_de_la_suite.py:1401`) | **+0.50** |
| **B1–B2. `CLAUDE.md` corto y guía** | `CLAUDE.md` 965 → 78 líneas; la historia íntegra en `proceso/historia_de_las_reglas.md` (974 líneas; `git diff --stat 362beb4:CLAUDE.md 1f56d99:proceso/historia_de_las_reglas.md`: sólo 9 inserciones, la cabecera). Guía de 145 líneas; contrastados contra el código sus cinco ejemplos de etiqueta, `modelos.paso`, `M5.v1_borde_libre`, `F5.V1` y `tests/test_estilo_criterios.py`: todos ciertos. Resta: tres reglas vigentes que sólo quedaron en la historia (N8) y el `README.md` sin tocar (N3) | **+0.35** |
| **B3–B4. Manual e índice de fichas** | `docs/manual_usuario.md`, 162 líneas, sin una sola captura (`grep -c "png\|capturas_interfaz"` = 0, y `docs/capturas_interfaz/` tiene cinco); índice de 404 fichas en `docs/decisiones_diferidas.md` (10 384 líneas) con guardia de sincronía, en verde | **+0.15** |
| **C2. Plantillas** | `plantillas/` con seis archivos y su `README.md`; `tests/test_plantillas.py` en verde | **+0.15** |
| **C3–C4. Ejecutable y pestaña 4** | C4 hecho y probado (`tests/test_c4_bloqueos_gui.py` en verde). C3 es una receta **nunca construida** (el propio plan §8: «sin verificar el ejecutable en Windows ni WeasyPrint empaquetado») y con un defecto legible en el código (N2) | **+0.10** |
| **D. Partición de archivos** | `M9_cabezal.py` 16 793 → 13 archivos, máx. 2 543; `criterios_adoptados.py` 14 732 → 2 145 de mecanismo + 12 archivos en `src/criterios/`, máx. 2 546; `modelos.py` 8 714 → 14 archivos, máx. 1 619; `M11_reporte.py` 5 992 → 19 archivos, máx. 695 (`wc -l`). Resta: el criterio de aceptación «ningún archivo de `src/` sobre ~3 000 líneas» no se cumple (N10), y los paquetes M9 y M11 propagan `monkeypatch` cambiando la clase del módulo en producción (N4) | **+0.25** |
| **Lo que resta al conjunto** | Windows sin confirmar y sin trabajo en la CI (N1); toda la rama con la CI en rojo por el sello PROVISIONAL (N7); el piloto real C1 sin hacer | **−0.20** |
| **Total** | 6.5 + 1.50 − 0.20 | **7.8** |

**Para un desarrollador nuevo.** Mejora real y medible: la constitución se
lee en minutos, la guía tiene recetas que funcionan y la suite de trabajo
baja de 2 h 27 min a un cuarto de hora. Sigue costando: quien entra por el
`README.md` (lo natural) lee `python -m pytest -q` y conteos del 13 y 14 de
noviembre (6 402 y 6 609 frente a los 9 226 recolectados hoy), y no encuentra
ni la guía ni el manual; quedan 12 archivos de `src/` sobre 3 000 líneas
(`normativa/citas.py` 17 536, `constantes_normativas.py` 6 678,
`normativa/tablas.py` 6 018, `servicio.py` 5 509, `M5_verificaciones.py`
5 056, `M8_estructural.py` 5 046…), más `gui/app.py` (4 376) y `cli.py`
(3 492).

**Para el usuario final.** Mejora: manual, plantillas comentadas con test de
pre-vuelo y la pestaña 4 que dice dónde se declara cada bloqueo. Sigue
costando: su máquina es Windows y allí la suite dio 16 fallos de plataforma
cuya corrección está sin confirmar; el ejecutable sin Python no existe más
que como receta; y no hay todavía una obra real pasada de punta a punta (C1).

### 2.2 Nota global: 8.5 → 8.8

| Concepto | Efecto |
|---|---|
| Cálculo: sin cambios. AST de `M9`, `modelos` y `M11` idéntico salvo lo declarado; 169 criterios idénticos campo a campo; línea base con sólo `criterios_sha1` distinto (§3.3). La nota de corrección técnica del 21-11 se conserva íntegra | 0 |
| Eje «mantenibilidad y uso» +1.3, con su peso en el conjunto | +0.30 |
| Integridad del cierre: primer sello con registro de corrida en disco; H1 a H5 cerrados | +0.10 |
| Riesgo de plataforma nuevo y sin cerrar: Windows sin confirmar, ejecutable sin construir, CI de `main` sin terminar al auditar | −0.10 |
| **Total** | **8.8** |

## 3. Verificación del cierre

### 3.1 El sello: corresponde a una corrida medida

- `docs/indice_formulas.md:10` y `docs/trazabilidad.csv:1` dicen
  `ca234cf` · `9213 passed, 13 skipped` · «paralelo -n 4 más el paso aislado».
- `suite.sh` (el guion) corre en `<scratchpad>/limpio` — un worktree en
  `ca234cf` según `git worktree list` — con `NORMAS_DIR`, `xvfb-run`,
  `-n 4 --dist loadfile` y después `-m aislado`.
- `suite_completa.log`, últimas líneas, literal:
  `2 failed, 9210 passed, 13 skipped, 1 warning in 5991.45s (1:39:51)` ·
  `EXIT_PARALELO 1` · `1 passed, 9225 deselected in 9.27s` · `EXIT_AISLADO 0`.
  Los dos fallos son `test_trazabilidad_csv.py::test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes`
  y `test_indice_formulas.py::test_el_sello_lleva_fecha_commit_y_par_de_la_suite`,
  los dos con `'PROVISIONAL: suite por medir'`.
- 9210 + 2 + 1 = 9213; 9213 + 13 = 9226 recolectados. La bitácora
  (líneas 2842 a 2844) lo declara fila a fila, sin esconder la suma.
- `git diff --stat ca234cf 1f56d99`: 5 archivos; del entregable sólo
  `docs/indice_formulas.md` y `docs/trazabilidad.csv`, **una línea cada uno**
  (el sello). El código sellado es el código medido.
- Los dos tests de sello y los de sincronía pasan sobre `1f56d99` (incluidos
  en los 647 de §1).

Reserva (hallazgo N7): «9213 passed» **no lo imprimió ninguna corrida**. Es
la suma de tres observaciones, dos de ellas tests que fallaron en la corrida
medida y pasaron después de sellar. Es una consecuencia del diseño del sello
PROVISIONAL y está declarada con honradez; no es el defecto de H1 (aquél era
una deducción desde otra máquina y no se reproducía), pero el principio 3 del
plan pedía «el par medido en una sola corrida completa» y eso, al pie de la
letra, es inalcanzable con este diseño.

**La CI de `main` sobre `1f56d99`** (run `45318925991`, creada 03:21 UTC):
el trabajo **`rapida` terminó en `success`** (03:21:24 a 03:38:17 UTC,
16 min 53 s con la instalación incluida, suite rápida y paso `aislado`); el
trabajo **`completa` seguía `in_progress`** a las 03:38 UTC, cuando se cerró
este informe. **`main` se adelantó antes de tener esa CI en verde.** El
último verde completo de `main` es el de `362beb4` (run `44859160957`). Todas las corridas de la rama entre `7efb15d` y `ca234cf`
terminaron en `failure`, y en las dos que se abrieron (`45228860806` y
`45305926473`) el único fallo era el test del sello PROVISIONAL.

**La exportación** (`git archive 90b8f74`): su corrida estaba al 96 % sin
resumen final; no se usa aquí. La bitácora no tiene todavía esa fila y el
LEEME lo dice («En curso»).

### 3.2 H1 a H5

| Hallazgo | Estado comprobado |
|---|---|
| H1 sello deducido | **Cerrado.** §3.1. La fila deducida de `5eccfe2` queda rotulada como tal en la bitácora, sin reescribirla |
| H2 test de `import cli` intermitente | **Cerrado con reserva.** Mide tiempo de CPU (`time.process_time`), mínimo de 7 subprocesos, marca `aislado` con paso propio en la CI y deselección declarada bajo xdist (`conftest.py:95-107`). El límite sigue en 0.30 s por decisión del dueño, y el margen es estrecho: N6 |
| H3 cifras a mano en el anexo de sensibilidad | **Cerrado.** `tests/apoyo/sensibilidad.py::cifras_de_la_prosa_del_cabezal` las lee del `informe_json` de la corrida y detiene la generación si falta una; `grep "40.94\|41.46\|33.17\|1.715" tests/apoyo/sensibilidad.py` no devuelve nada |
| H4 LEEME desactualizado | **Cerrado.** `ve3_estado/LEEME.md` describe el estado real (sello, exportación en curso, pendiente de Windows) y la rama que nombra existe en el remoto |
| H5 | Informativo; resuelto con H1 (los sellos de `90b8f74` son las dos líneas esperadas) |

### 3.3 Principio 1: «ninguna tarea cambia un número calculado» — CUMPLIDO

Tres comprobaciones independientes entre `362beb4` y `1f56d99`:

1. **AST de lo partido.** Comparado con `ast.dump` cada definición de nivel
   superior del archivo viejo contra los submódulos nuevos:
   - `src/modelos.py` → `src/modelos/`: 299 de 299, **0 distintas**.
   - `src/modulos/M9_cabezal.py` → subpaquete: 539 de 539, **1 distinta**:
     `_sesgo` (la de WIN-02, abajo).
   - `src/modulos/M11_reporte.py` → subpaquete: 259 → 261; 4 distintas
     (`RAIZ`, por la profundidad de la ruta; `trazabilidad`, por la fecha del
     catálogo de D2; `CriterioBloqueante` y `criterios_bloqueantes`, de C4) y
     2 nuevas (`DatoBloqueante`, `datos_bloqueantes`, de C4). Ninguna es de
     cálculo.
2. **Catálogo de criterios.** Importado el `criterios_adoptados.py` de
   `362beb4` junto al de hoy: 169 claves en los dos, **mismo orden, 0 campos
   distintos** (`repr` campo a campo de las 169 fichas).
3. **Salidas.** `git diff 362beb4 1f56d99 -- tests/linea_base_familia_c`:
   8 archivos, una línea cada uno, y la única cadena que cambia es
   `criterios_sha1` (`0c6986d8…` → `30cff47a…`, cuatro veces cada una).
   `tests/test_linea_base.py`: `5 passed`. `docs/validacion_*.md`: sin
   diferencias. `docs/indice_formulas.md`: 3 líneas — el sello y dos filas
   (`9.2.1.est.e.alero.100` y `9.2.1.est.s.alero.100`) donde «da un …% MENOS
   que» pasa a «coincide con».

Los cambios que **sí** hay, todos declarados y ninguno numérico:

- `criterios_sha1` cambia de valor (ficha D2-01): ahora cubre el mecanismo y
  las fichas. Efecto real: el comparador marcará como distintas dos corridas
  de antes y de después de D2 con los mismos criterios. Declarado en
  `criterios_adoptados.sha1_criterios` y en `servicio.capturar_contexto`.
- La palabra del contraste fórmula–cuña (WIN-02, `fbbde5b`): con tolerancia
  **con nombre**, `TOL_REL_SESGO_CONTRASTE = 1e-9` en `src/tolerancias.py`,
  justificada con la medida (2.8e-16 a 5.5e-16 en 7 de 1 273 contrastes).
  Cumple la regla de tolerancias de `CLAUDE.md`.
- `"csv"` del JSON con `/` (`cli.py:1476`, WIN-01) y los textos que dicen
  dónde vive una ficha (`src/criterios/`).

Y uno **no declarado**, menor (N11): D0 corrigió de paso un falso negativo de
`variables_entrada`.

## 4. Revisión adversarial

### 4.1 Reexportaciones e identidad (D1, D2, D3)

Guion propio: importa cada paquete y sus submódulos, lee por AST las
definiciones de nivel superior y comprueba nombre a nombre.

| Paquete | Submódulos | Definiciones | Sin reexportar | No idénticas (`is`) | Mismo nombre en dos submódulos |
|---|---|---|---|---|---|
| `src.modelos` | 13 | 299 | 0 | 0 | 0 |
| `src.modulos.M9_cabezal` | 12 | 539 | 0 | 0 | 0 |
| `src.modulos.M11_reporte` | 18 | 261 | 0 | 0 | 0 |
| `src.criterios` | 11 | 34 | — (los reexporta `criterios_adoptados`) | 0 | sólo `CRITERIOS`, por diseño |

- De los 157 nombres de nivel superior del `criterios_adoptados.py` viejo,
  hoy faltan 26: 22 constantes que el archivo importaba de otros módulos, el
  símbolo `dataclass` y tres privados (`_NIVELES`, `_NIVEL_PERFIL`,
  `_NIVEL_EXPEDIENTE`). `grep` de `ca.<nombre>` y
  `criterios_adoptados.<nombre>` para los 26 en todo el repositorio: **cero
  usos**. Ningún importador se rompe.
- `sha1_criterios` lee bytes; con `* text=auto eol=lf` en `.gitattributes` la
  huella es la misma en Windows y en Linux.
- El estado mutable de M11 (la sonda de WeasyPrint, único `global` de los
  cuatro paquetes: `exportadores.py:88`) se resolvió bien: el paquete no
  guarda copia y lee y escribe en el submódulo.
- `tests/test_ext9_paquete_servicio.py` (identidad de módulos, estilo único,
  cero `sys.path`) pasa.

Tres defectos, ninguno de cálculo: **N4** (el propagador de `monkeypatch`),
**N5** (`__module__` normalizado rompe la introspección) y **N9** (una
guardia que se estrechó).

### 4.2 Guardias por AST que ya no ven código

Se buscaron en `tests/` las lecturas de los cuatro archivos desaparecidos y
los `glob("*.py")` no recursivos.

- Las que copiaban `criterios_adoptados.py` para probar la escritura
  permanente (`test_ui5_decisiones.py:1174`, `test_ve1_validacion.py:653`,
  `test_ve2_revision_m3_m4.py:285` y `:391`) copian ahora
  `ca.archivo_de_criterio(clave)`: correcto.
- `test_sin_literales.py:1549` pregunta a todos los archivos del catálogo y
  falla si una clave aparece en dos: correcto, y más fuerte que antes.
- `tests/apoyo/fuente_m11.py` concatena el subpaquete entero para las
  guardias de M11: correcto.
- **Una sí se estrechó**: `tests/test_M1_clasificacion.py:769` (N9).

### 4.3 Mutantes sembrados (worktree, revertidos)

| Mutante | Guardia | Resultado |
|---|---|---|
| `AUD_MUTANTE_M9 = 3.7` al final de `M9_cabezal/empujes.py` | `test_ningun_modulo_declara_literales_numericos` | **detectado** (`modulos/M9_cabezal/empujes.py: linea 1533 -> 3.7`) |
| `AUD_MUTANTE_MOD = 0.45` al final de `modelos/cabezal.py` | la misma | **detectado** (`modelos/cabezal.py: linea 1621 -> 0.45`) |
| `informe.y_m / informe.D_m` en `M11_reporte/cabezal.py` | `test_M11_no_calcula_y_sobre_D` | **detectado** |

Un cuarto, `a == 0.75` en `M9_cabezal/alero.py`, lo vio la guardia de
literales por el 0.75 y no por el `==`: la regla «prohibido comparar
flotantes con `==`» sólo tiene guardia para los `assert` de los tests, no
para `src/`. No es nuevo de este tramo.

### 4.4 Rondas de Windows (`404d06c`, `cd45995`, `fbbde5b`, `3d8a8ea`, `5248a36`)

- **Ronda 1 (`404d06c`, del dueño, medida en Windows).** `as_posix()` en las
  rutas de los documentos generados y `newline="\n"` al escribirlos; `-z` y
  bytes en `git ls-files` / `check-attr` del test de la exportación; un
  archivo nuevo por intento donde el antivirus bloqueaba la reescritura.
  Correcto y bien explicado en cada sitio.
- **`cd45995`** revierte el único trozo de la ronda 1 que rompía un contrato
  (las rutas de la hidrología en `gui/app.py`). Correcto, y deja una
  asimetría declarada en WIN-01 y en `cli.py:1469-1475`: el `csv` del JSON va
  con `/` y las dos rutas de la hidrología con el separador del sistema. El
  comparador omite las tres.
- **`fbbde5b`** (WIN-02): revisado en §3.3. Correcto.
- **`3d8a8ea` y `5248a36`** (WIN-03): `geometria_inicial`, `area_de_trabajo`
  y `tomar_foco_al_abrir` en `gui/componentes.py`. Fuera de Windows no cambia
  nada (`sys.platform != "win32"` devuelve antes). **Todo el camino de
  `ctypes.windll` se escribió y se probó en Linux con dobles**: no se ha
  ejecutado nunca contra la API real después de la ronda 2 (N1). Dos
  observaciones menores de lectura: `_rect_de_trabajo_del_monitor` fija
  `argtypes` y `restype` sobre `ctypes.windll.user32`, que es un objeto
  compartido por todo el proceso (`gui/componentes.py:252-255`); y el límite
  declarado al 150 % (N12).

## 5. Hallazgos

Ninguno es de cálculo. **Bloquean la entrega**: N1 y el trabajo `completa` de
la CI de `main` (parte de N7). **Conviene antes de la sustentación**: N3. El resto no bloquea.

| Id | Severidad | Hallazgo | Evidencia | Acción recomendada |
|---|---|---|---|---|
| N1 | **MEDIA** — bloquea la entrega si se usa o se demuestra en Windows | **Windows está sin confirmar y la CI no lo cubre.** La suite en la máquina del dueño dio `18 failed` sobre `7efb15d` (2 de sello y 16 de plataforma). La ronda 2 corrige 8 de ellos **desde Linux**, con dobles de la API de Windows, y no se ha vuelto a correr allí. Los dos trabajos de la CI son `ubuntu-24.04`. La guía del desarrollador y el empaquetado están escritos para Windows | `proceso/bitacora_conteos_y_entorno.md:2854-2859`; `.github/workflows/pruebas.yml:34` y `:63`; `gui/componentes.py:233-330`; ficha WIN-03, «Qué haría falta» | (1) El dueño corre en Windows los 8 tests y después la suite completa, y la fila va a la bitácora. (2) Añadir un trabajo `windows-latest` con la suite rápida, al menos por `workflow_dispatch`. Hasta entonces, las fichas WIN no deberían leerse como verificadas en su plataforma |
| N2 | **MEDIA** — no bloquea si el entregable se usa desde el clon, que es lo que dice el `README.md` | **El ejecutable de C3 no se ha construido nunca y tiene un defecto legible.** En el paquete congelado `sys.executable` es `alcantarillas_gui.exe`, y las dos funciones de la ventana que lanzan un proceso hijo lo usan como intérprete de `cli.py`: la exportación a PDF y **«Barrido…»**. La guía (§5) sólo avisa del PDF | `gui/exportacion_pdf.py:325`; `gui/proceso_barrido.py:190`; `grep "frozen\|_MEIPASS"` en `gui/`, `src/` y `cli.py`: ninguna detección; plan 11 §8, fila C3 | Detectar `getattr(sys, "frozen", False)` y lanzar `alcantarillas_cli.exe` del mismo directorio; construir y probar en Windows (abrir, correr la plantilla, PDF y barrido); mientras tanto, rotular C3 como «receta sin verificar» en la guía y no ofrecerlo al usuario |
| N3 | **MEDIA** — no bloquea; es lo primero que lee el tribunal y quien llega | **El `README.md` no se enteró del plan.** Su último commit es del 2026-11-20. §7 manda `python -m pytest -q` (la vía de 2 h 27 min), no nombra `-m "not lento"`, xdist ni el paso `aislado`, y da conteos del 13 y 14 de noviembre (6 402, 6 609) frente a los 9 226 de hoy. No enlaza `docs/manual_usuario.md`, `docs/guia_del_desarrollador.md`, `plantillas/` ni `empaquetado/` | `README.md:280-323`; `grep -c -i "manual_usuario\|guia_del_desarrollador\|plantillas/\|empaquetado\|xdist\|lento\|aislado" README.md` = 0 | Actualizar §1 (dependencias de test), §3 (plantillas), §7 (dos velocidades, par de hoy con su fecha) y enlazar los tres documentos nuevos |
| N4 | **MEDIA** (mantenibilidad) — no bloquea | **Los paquetes M9 y M11 cambian su clase de módulo en producción para servir a los tests.** `_PaqueteM9` y `_PaqueteM11` propagan cada `setattr` sobre el paquete a todos los submódulos que tengan ese nombre; lo usan 80 `monkeypatch.setattr` de la suite. (a) El camino de `delattr` no se restaura: **medido**, tras `monkeypatch.delattr(M9, "TOL_ANGULO_CUNA")` y `undo()`, el paquete recupera el nombre y `estabilidad_cargas` no. (b) Ningún test prueba el mecanismo ni el invariante «el paquete reexporta todo nombre de sus submódulos»; el primer cambio posterior a la partición ya lo rompe: `TOL_REL_SESGO_CONTRASTE` está en `estabilidad_cargas` y no en el paquete. (c) El `__init__.py` de M9 tiene 1 162 líneas, 387 de ellas de `import` mantenidas a mano | `src/modulos/M9_cabezal/__init__.py:1144-1162`; `src/modulos/M11_reporte/__init__.py:560-587`; `grep -c "monkeypatch.setattr(M9\|…M11"` = 80; `grep -rl "_SUBMODULOS_M9\|_PaqueteM9" tests`: vacío | Un test que fije el mecanismo (propaga, restaura, también con `delattr`) y otro que exija que todo nombre de nivel superior de un submódulo esté en el paquete; arreglar `__delattr__` o retirarlo. A medio plazo, que los tests parcheen el submódulo dueño del nombre |
| N5 | BAJA | **`__module__` normalizado a `src.modelos` rompe la introspección.** Medido sobre las 164 clases del paquete: `inspect.getsource` falla en las 164 y `typing.get_type_hints` en 114 (`NameError: name 'Tuple' is not defined`). Antes de D3 las dos funcionaban. Hoy no tiene consumidor (`grep` de `get_type_hints`: ninguno; los `getsource` de la suite son sobre funciones) | `src/modelos/__init__.py:182-188` | Declararlo en la ficha de D3 como límite conocido, o normalizar sólo en `serializacion_informe._nombre_de` (que es quien lo necesita) y dejar el `__module__` real |
| N6 | BAJA | **El presupuesto de `import cli` quedó sin holgura.** Con la máquina cargada, 12 muestras de tiempo de CPU dieron 0.290 a 0.316 s contra 0.30 s; alternando con el árbol de `362beb4` en las mismas condiciones, 10 pares: 0.284 a 0.292 s el viejo y 0.291 a 0.311 s el nuevo. **Las particiones añadieron unos 7 ms** (más archivos que abrir). El test `aislado` falló aquí 1 de 3 veces; no es un fallo en sus condiciones (pide la máquina libre), pero la auditoría del 21-11 medía 0.216 a 0.263 s en reposo y el margen sólo ha ido a menos | `tests/test_ext8_rendimiento_gui.py:97-98` y `:312-341` | Volver a medir en reposo en la CI y en la máquina del dueño y anotar la cifra en la ficha EXT-8-06; fijar el presupuesto relativo a esa medida, o recuperar los 7 ms con imports perezosos en los `__init__` |
| N7 | BAJA — salvo la CI de `main`, que hay que ver en verde | **El sello PROVISIONAL tiñe de rojo toda la rama y el par del sello es una suma.** Entre `7efb15d` y `ca234cf` todas las corridas de la CI terminaron en `failure` por un único test de sello, de modo que un fallo real no se habría distinguido a simple vista; el paso `aislado` ni siquiera corre cuando el anterior falla. «9213 passed» es 9210 + 2 + 1. Y `main` se adelantó a `1f56d99` con su CI todavía en curso | `gh run list` (runs `45228860806` a `45305926473`); `suite_completa.log`; `bitacora_conteos_y_entorno.md:2842-2844` | Confirmar en verde el trabajo `completa` de la run `45318925991` (el `rapida` ya lo está) y anotarla en la bitácora. Que los tests de sello acepten `PROVISIONAL` fuera de `main` y de las etiquetas (o lo marquen `xfail` con motivo), para que la rama esté en verde y la corrida que mide imprima el par entero |
| N8 | BAJA | **`CLAUDE.md` corto perdió tres reglas vigentes**, que sólo quedan en la historia: toda verificación devuelve `Verificacion(...)` y nunca un `bool` (está en la guía, no en la constitución); `G_LAUSHEY = 9.8` separado de la gravedad genérica; y los dos `inf` deliberados de M9 que ninguna guardia de finitud puede atrapar. Además sus 16 referencias a `proceso/` (11 enlaces a la historia) quedan rotas en la exportación, porque `proceso/` es `export-ignore` | `grep -n -i "desnudo\|laushey\|\binf\b" CLAUDE.md`: sin resultados; `grep -c "proceso/" CLAUDE.md` = 16; `.gitattributes` | Devolver las tres reglas en una línea cada una; decidir si la historia viaja con el entregable o si los enlaces se rotulan «sólo en el repositorio» |
| N9 | BAJA | **Una guardia se estrechó con la partición.** El contrapeso de los bloques `Uso` recorre `src/modulos` con `glob("*.py")`: ya no ve los docstrings de `M9_cabezal/__init__.py` ni de `M11_reporte/__init__.py`, que conservan su bloque `Uso` | `tests/test_M1_clasificacion.py:768-769` | Añadir los `__init__.py` de los subpaquetes al recorrido (el iterador de D0 ya existe) |
| N10 | BAJA | **El criterio de aceptación del bloque D no se cumple** tal como está escrito («ningún archivo de `src/` por encima de ~3 000 líneas»): quedan 12 en `src/` (18 → 14 contando `gui/app.py` y `cli.py`). D3 de `constantes_normativas.py` está diferida con ficha (D3-03) | `wc -l`; plan 11, §5 y §8 | Corregir el criterio en el plan a lo que de verdad se hizo (los cuatro archivos objetivo) y dejar el resto como deuda censada |
| N11 | INFORMATIVA | **D0 cambió una atribución derivada sin declararlo**: `F_pga_lectura_columna_extrema` pasa de «Fase 9» a «Fase 9 · Fase 0-bis» en `variables_entrada.reporte_variables()` (única línea distinta de 1 297 entre los dos árboles). Es una **corrección**: `ML_licuefaccion.py:461` lo lee con `ca.valor(M9.CRITERIO_F_PGA_LECTURA)` | `diff` de `reporte_variables()` entre `362beb4` y `1f56d99` | Una línea en la ficha de D0 |
| N12 | INFORMATIVA | **Límite declarado de WIN-03**: en 1920×1080 al 150 % «Barrido…» vuelve a quedar bajo la pestaña 2. Es una configuración corriente en portátiles | `gui/componentes.py:198-206` | Remedio de layout (fila de botones fija o con desplazamiento) antes de demostrar en un equipo que no sea el del dueño |
| N13 | INFORMATIVA | **C1 (piloto real) sigue sin hacerse**, bloqueado por el expediente del dueño. Es la tarea con más efecto pendiente sobre «uso» (+0.5 en la estimación del plan) y la que el manual y las plantillas necesitan para probarse con un dato que no sea de prueba | plan 11, §8, fila C1 | Es del dueño |
| N14 | INFORMATIVA | Detalles de la CI: `rapida` corre dos veces por commit en una rama con PR (`push` y `pull_request`); `requirements-dev.txt` instala `pyinstaller` en cada corrida sin usarlo | `.github/workflows/pruebas.yml:24-27`; `requirements-dev.txt` | `concurrency` o limitar `push` a `main`; mover `pyinstaller` al extra `empaquetado`, que ya existe en `pyproject.toml` |

## 6. ¿Listo para entrega y sustentación?

- **Cálculo (`src/`)**: sí. Este tramo no movió ningún número, y está
  comprobado por AST, por catálogo y por salidas. La valoración técnica del
  21-11 sigue en pie.
- **Sello y trazabilidad**: sí. El par es el de una corrida con registro.
- **Antes de dar la entrega por cerrada**:
  1. ver en verde el trabajo `completa` de la run `45318925991` de `main`
     (N7; el `rapida` ya terminó en `success`);
  2. la confirmación en Windows del dueño (N1), con su fila en la bitácora;
  3. cerrar la fila de la exportación, que estaba en curso.
- **Antes de la sustentación, sin bloquear**: `README.md` al día (N3) y no
  presentar el ejecutable como producto mientras N2 siga abierto.
- **Después**: N4 a N10, que son deuda de mantenimiento y no de resultado.
