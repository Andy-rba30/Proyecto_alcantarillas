# INFORME T-12 · FASE A — repositorio listo para la sustentación

- **Rama:** `tesis/T-12`, empujada; SHA final: `78a7780e5cacd01a73f11b4f32ad64c4d9261133`. Base `f77c5d4`. NO fusionado a `main`.
- **Sin cambios de cálculo.** `src/modulos/` sólo cambia en `M11_reporte.py` (plomería de
  reporte: la memoria resumida y la celda de T11-09, sin aritmética; el test de AST de M11
  sigue verde). Fuera de `src/modulos/`: `src/modelos.py` (dos propiedades booleanas,
  `salida_no_se_forma`, leídas de campos existentes), `src/servicio.py` (la clave documental
  `_advertencia` del JSON de datos externos), `src/normativa/fuentes.py` (dónde se buscan los
  PDF), `src/normativa/manifiesto.py` (texto del manifiesto), `cli.py` (dos banderas) y
  `conftest.py` (el salto sin `NORMAS_DIR`).
- **Diámetros, secciones, materiales y HW movidos: ninguno.**

## 1. IDs (canónicos, `INF-5.2.k`)

| ID | Resultado | Por qué |
|---|---|---|
| `INF-5.2.2` (material de proceso) | **entero** | `.claude/agents`, `docs/planes_mejora` (cadena T incluida), `docs/auditorias` (tracker sin editar), `verificar_sesion.py`, `tests/apoyo/tracker.py` y los tests de proceso movidos con `git mv` a `proceso/`; la bitácora de conteos/incidentes y las reglas de corrección de `CLAUDE.md` movidas ENTERAS (verificado byte a byte contra `f77c5d4`); `proceso/` fuera del entregable (`testpaths`, `.gitattributes export-ignore`, verificado con `git archive`). |
| `INF-5.2.3` (PDF con copyright) | **entero, con salvedad** | 18 PDF retirados tras comprobar sha1 = repositorio de normas; los PDF siguen en la historia de git (pregunta 1). |
| `INF-5.2.4` (fixtures que parecen datos) | **entero** | cabecera en los dos `datos_referenciales_prueba*.md`, `_advertencia` en `entradas_ampliadas.json`, rótulo visible (título + bloque al principio) en las 4+1 memorias HTML de la línea base puesto por el generador. |
| `INF-5.2.6` (fuentes citadas y ausentes) | **en parte** | el manifiesto dice el estado final (18 presentes + 2 censados, todos sólo en el repositorio de normas; 12 ausentes); siguen ausentes las 12 (M 294 original, ejemplar legible de M 170M, Ley 29338, SENAMHI/ANA, EMS…), que son entradas del dueño. |
| `INF-5.2.7` (LICENSE, pyproject) | **entero** | `LICENSE` todos los derechos reservados; `pyproject.toml` con las versiones de `requirements*.txt` (ninguna nueva); README de usuario. |
| `INF-5.2.1` (SHAs citados inexistentes) | **no** | el prompt no trae acción; medido: 24 de 84 SHAs que cita el tracker están en este clon (superficial, 55 commits). |
| `INF-5.2.5` | ya cerrado (T-1) | — |

## 2. Tests

**Pares MEDIDOS sobre `dac11f8`** (árbol final; `78a7780` sólo re-sella dos líneas de
sello), configuración «PyMuPDF sí · Tk no»:

| Suite | `NORMAS_DIR` | passed | skipped | collected |
|---|---|---|---|---|
| entregable (`python -m pytest`, = `tests/`) | **sí** | **6374** | **23** | **6397** |
| entregable | **no** | **6222** | **175** | 6397 |
| proceso (`python -m pytest proceso/tests`) | sí / no | 142 / 142 | 0 / 0 | 142 |

Base `f77c5d4`: 6446 / 23 / 6469 (sin `NORMAS_DIR` 6423 / 46). **El par con `NORMAS_DIR` no
baja en saltos (23 = 23)**; los `passed` bajan sólo por lo que SALE a la suite de proceso:
6446 − 138 + 66 = 6374. Sumadas las dos suites, 6374 + 142 = 6516 passed = 6446 + 70.

- **Salen de la suite del entregable: 138** de los 6469 de la base → `proceso/tests/`: 119
  (`test_ext11_cruce_temarios`), 16 (bloques 1 y 6 de `test_t0_gobernanza` + su test de
  `verificar_sesion`), 1 (`test_estan_las_veintidos_fichas_que_la_auditoria_clasifico`) y 2
  anclajes de fichas (EXT-11-03, T0-04) cuyo símbolo vive ahora en `proceso/tests/`.
- **Nuevos: 70.** `tests/test_t12_entregable.py` (61), 5 anclajes de las fichas T12 en
  `test_decisiones_diferidas` (entregable); `proceso/tests/test_t12_proceso.py` (3) y el
  anclaje de T12-02 (en proceso). Ninguno con la marca `pdf` (siguen 150) ni de Tk.
- **Sin `NORMAS_DIR` saltan 152 más que con él** (eran 23 en la base): los 150 `pdf` (por el
  hook `conftest.pytest_runtest_setup`, un solo motivo) + la mitad de PC-23 que mira el
  repositorio enlazado + el sha1 de los dos PDF censados. Es el número nuevo del eje
  `NORMAS_DIR` de la tabla.
- **Derivadas, no medidas** (el contenedor no tiene tkinter; quitar PyMuPDF apagaría la
  verificación): sí·sí 6387 / 10; no·sí 6238 / 159; no·no 6225 / 172 (con `NORMAS_DIR`; misma
  derivación que T-11: +13 de Tk, −149 sin PyMuPDF).
- **Reescritos, declarándolo en su docstring:** `test_t0_gobernanza` (tres del bloque 5 al
  contrato sin caída a `normas/`; separada su mitad de proceso), `test_ext6_registro_normativo`
  (PC-23: «la app no versiona ningún PDF» + el repositorio enlazado; el sha1 de los censados
  se salta sin enlace), `test_sin_literales` (`verificar_sesion.py` fuera de la lista y del
  censo de marcas, `proceso` declarado fuera del barrido), `test_decisiones_diferidas` (un test
  movido; los anclajes en `proceso/` se comprueban en la suite de proceso).
- **Rojo (no escrito primero, medido):** `tests/test_t12_entregable.py` final contra
  `f77c5d4` (exportado con `git archive`): 26 failed + 32 errors, 2 passed (guardias:
  `test_T11_09_no_mueve_ningun_numero_del_punto`, correo del README) y 1 skipped (el de
  `git check-attr`, fuera de un checkout). Ficha T12-06.
- Censos sin mover: 141 criterios, 20 sin valor, 507 citas, 150 tests `pdf`; ninguna marca
  `literal-ok` nueva en `src/`; techos de `test_ext8` sin tocar (la completa sólo cambia el
  texto de T11-09).

## 3. Censo: qué archivo de proceso leía cada test (base `f77c5d4`) y qué se hizo

| Test (base) | Archivo de proceso que lee | Qué hice |
|---|---|---|
| `test_t0_gobernanza.py`, bloque 1: 5 funciones, 15 casos (filas `INF-`, estados por prompt `LO_QUE_ESCRIBIO_CADA_PROMPT`, 10 alias, tabla de equivalencias) | `docs/auditorias/matriz_cruzada_auditorias.xlsx` (vía `tests/apoyo/tracker.py`) y `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md` | movidos, texto intacto, a `proceso/tests/test_t0_gobernanza_proceso.py` |
| `test_t0_gobernanza.py::test_verificar_sesion_busca_los_PDF_por_la_misma_puerta` | `verificar_sesion.py` + tracker | movido (ídem) |
| `test_t0_gobernanza.py::test_la_copia_de_la_cadena_no_se_edita_sin_que_se_note` | la cadena T | movido (ídem) |
| `test_ext11_cruce_temarios.py` (119) | `docs/auditorias/temario_refutar_*.json` + tracker | `git mv` a `proceso/tests/` (rutas e import corregidos) |
| `test_decisiones_diferidas.py::test_estan_las_veintidos_fichas_que_la_auditoria_clasifico` | `docs/auditorias/auditoria_sistema.md` | movido a `proceso/tests/test_decisiones_diferidas_auditoria.py` |
| `test_decisiones_diferidas.py` anclajes EXT-11-03 y T0-04 | símbolos en tests que se movieron | fichas re-ancladas en `proceso/tests/`; los anclajes bajo `proceso/` se comprueban en la suite de proceso (una exportación no lleva `proceso/`) |
| `test_sin_literales.py` (capa de presentación + censo de marcas, 2) | `verificar_sesion.py` | sale de la lista; `proceso` declarado fuera del barrido con su razón |
| `tests/apoyo/tracker.py` | el tracker | `git mv` a `proceso/apoyo/` |
| `test_criterios_adoptados.py::test_dato_faltante_admite_un_dato_que_no_es_columna_del_csv` | `CLAUDE.md` («Excepciones», regla técnica) | se queda: esa sección sigue en `CLAUDE.md` |
| Los que leen `docs/decisiones_diferidas.md`, `contrato_entradas.md`, la v8, manifiestos, `trazabilidad.csv`, índice, guía, validación, `ruta_familia_c.md` | documentos del ENTREGABLE | se quedan |

Guardia nueva: `tests/test_t12_entregable.py::test_ningun_test_del_entregable_lee_material_de_proceso`
(AST: ni imports de `proceso` ni rutas construidas a `proceso/`, `auditorias`, `planes_mejora`).

## 4. Qué se movió y adónde

| Antes | Ahora | Cómo |
|---|---|---|
| `normas/*.pdf` (18) | — (sólo en el repositorio de normas) | `git rm`, tras sha1 IGUAL uno a uno (`SP/T-12/sha1_normas_antes_del_git_rm.txt`) |
| `.claude/agents/` (3) | `proceso/.claude/agents/` | `git mv` |
| `docs/planes_mejora/` (14, con la cadena T) | `proceso/planes_mejora/` | `git mv` |
| `docs/auditorias/` (3 informes, 2 temarios, el tracker sin editar) | `proceso/auditorias/` | `git mv` |
| `verificar_sesion.py` | `proceso/verificar_sesion.py` (`python3 -m proceso.verificar_sesion`; paso 5 al contrato nuevo; ruta del tracker) | `git mv` + rutas |
| `tests/apoyo/tracker.py` | `proceso/apoyo/tracker.py` | `git mv` + ruta |
| `tests/test_ext11_cruce_temarios.py` | `proceso/tests/` | `git mv` + rutas/import |
| bloques 1 y 6 de `tests/test_t0_gobernanza.py` + su test de `verificar_sesion` | `proceso/tests/test_t0_gobernanza_proceso.py` | texto intacto, rutas nuevas |
| `test_estan_las_veintidos_fichas…` de `tests/test_decisiones_diferidas.py` | `proceso/tests/test_decisiones_diferidas_auditoria.py` | ídem |
| `CLAUDE.md` «Cierre de tarea» (bitácora + tabla de conteos) | `proceso/bitacora_conteos_y_entorno.md` | entera, verificada byte a byte contra `f77c5d4` (test) |
| `CLAUDE.md` «Reglas de corrección…» + «Git (fase de corrección)» | `proceso/reglas_de_correccion_de_auditorias.md` | ídem |

Nuevos: `proceso/README.md` (README de proceso), `proceso/tests/conftest.py`,
`.gitattributes` (`proceso export-ignore`; `git archive HEAD` no lleva `proceso/`: medido),
`pyproject.toml` (`testpaths = ["tests"]`), `LICENSE`, README de usuario. **No movidos, a
propósito** (el código y documentos del entregable los citan como procedencia):
`hoja_de_ruta_correcciones_v12.md`, `ruta_familia_c.md`, `diseno_registro_normativo.md`,
`resolucion_clase_sitio.md`, `manifiesto_datos_proyecto_vs_constantes.md`, `linea_base.md`,
`auditoria_y_ruta_despliegue_v9.md`. Las rutas viejas que citan los documentos/comentarios en
prosa no se reescribieron (la v8 entre ellos: su huella está en cada memoria); la tabla de
`proceso/README.md` las traduce. La carpeta de orquestación sigue en `tesis/orquestacion-estado`.

## 5. Línea base (contra `f77c5d4`)

- Las cuatro memorias HTML: rótulo de fixture en `<title>` y al principio del cuerpo (en la
  del cajón, al principio del archivo). Quitado el rótulo, `memoria_expediente.html`,
  `memoria_perfil.html` y `memoria_punto_cajon.html` son IDÉNTICAS byte a byte.
- `memoria_perfil_ancha.html`: además, UNA cadena (T11-09, A-02): `(entrada 0.572 / salida
  0.560)` → `(entrada 0.572 / salida no se forma: el perfil no alcanza la entrada)`. Medido:
  es la única otra diferencia.
- `cli_expediente.txt`: +1 línea («Memoria resumida (HTML)  : <SALIDA>/memoria_resumida_exp.html»).
- Nuevo: `memoria_resumida_expediente.html` (la corrida 4 escribe la resumida).
- `entradas_ampliadas.json` (entrada): + clave `_advertencia`.
- Idénticos byte a byte: los cuatro JSON (comparador de E-B: IGUALES), los dos CSV y los otros
  cuatro `cli_*.txt`.
- **Diámetros / secciones / materiales / HW movidos: ninguno.**

## 6. T11-09 (aprobado por el dueño): cómo se resolvió

La regla `cli.salida_no_se_forma` se llevó al dato: `PerfilLamina.salida_no_se_forma`
(`sustituye_aproximacion and HW_remanso_m is None`, la condición exacta en que `HW_efectivo_m`
es None) y `ResultadoHidraulico.salida_no_se_forma` (False sin perfil). `cli.salida_no_se_forma`
la delega (el JSON y la línea «Control» no cambian) y M11 la lee en
`M11._celda_control_gobernante`, compartida por las dos vistas, con el texto
`M11.SALIDA_NO_SE_FORMA` = «salida no se forma: el perfil no alcanza la entrada» (la redacción
de la CLI). La aproximación descartada sigue en la fila del perfil, rotulada HW<sub>aprox</sub>.
Sólo mueve esa cadena de A-02 en `memoria_perfil_ancha.html`. Ficha T11-09 actualizada
(cerrada). Rojo medido contra `f77c5d4`.

## 7. Memoria en dos vistas

`M11.memoria_resumida_html` / `exportar_html_resumida` / `exportar_pdf_resumida`, plantilla
`src/plantillas/memoria_resumida.html`; CLI `--html-resumida`, `--pdf-resumida` (misma
invocación que `--html`; la resumida nombra el archivo de la completa). Por punto: combinación
adoptada, tabla de verificaciones con veredicto, avisos (`InformePunto.avisos()`), etapas
bloqueadas, criterios [A] con valor y ventana; proyecto: trazabilidad, alcance, cuadro
resumen, pendientes. Mismos formateadores que la completa (`_filas_combinacion_adoptada`,
`_filas_verificaciones` se extrajeron de `_tabla_diseno` / `_tabla_verificaciones` sin cambiar
su salida: medido, las memorias completas de la línea base no se mueven salvo T11-09).
Tests: ningún número de la resumida falta en la completa (total y por punto; tres corridas de
referencia, el juego de T-11 y la línea base), mismo encabezado de trazabilidad, CLI con las dos
vistas. Tamaño medido: 63 KB frente a 828 KB de la completa (expediente, entradas ampliadas).
GUI: NO (no es plomería directa: quinto exportador con sus contratos y pruebas de ventana real
que este contenedor no corre) → ficha T12-04, símbolo `M11_reporte.py::memoria_resumida_html`;
desde la ventana, `cli.py --sesion sesion.json --html-resumida`.

## 8. Diferidos con símbolo (Parte LV provisional de `docs/decisiones_diferidas.md`)

T12-01 `fuentes.py::RUTA_SIN_ENLACE` (historia de git con los PDF) · T12-02
`proceso/tests/conftest.py::pytest_collection_modifyitems` (rutas históricas en prosa no
reescritas; siete documentos técnicos de origen de proceso se quedan en `docs/`) · T12-03
`tests/apoyo/rotulo_fixture.py::rotular` · T12-04 `M11_reporte.py::memoria_resumida_html`
(botón de la ventana) · T12-05 `test_t12_entregable.py::test_pyproject_fija_las_mismas_versiones_que_requirements`
(nombre de la carátula) · T12-06 (rojo no primero). Actualizadas: T11-09 (cerrada), T11-10
(decisión del dueño: lote posterior), T0-01 (remite a T12-01).

## 9. Filas del tracker para FASE B (responsable «Claude Code (cadena T, T-12)»)

| ID | Estado | Nota |
|---|---|---|
| `INF-5.2.2` | Cerrado | material de proceso en `proceso/` (git mv), bitácora y reglas de `CLAUDE.md` movidas enteras, 138 tests de proceso fuera de la suite del entregable; fichas T12-02. |
| `INF-5.2.3` | Cerrado (con salvedad) | 18 PDF retirados tras sha1 = repositorio de normas; los PDF siguen en la historia de git (decisión del dueño); NORMAS_DIR única vía; Normas privado recomendado. Ficha T12-01. |
| `INF-5.2.4` | Cerrado | advertencia en los dos .md, en `entradas_ampliadas.json` (`_advertencia`) y en las memorias de la línea base (por el generador). Ficha T12-03. |
| `INF-5.2.6` | Cerrado parcial | manifiesto con el estado final (18 + 2 + 12 ausentes); las ausentes siguen siendo entradas del dueño. |
| `INF-5.2.7` | Cerrado | LICENSE (todos los derechos reservados), pyproject.toml, README de usuario. Ficha T12-05. |
| `INF-5.2.1` | Abierto (NOTA) | T-12 no trae acción; 24 de 84 SHAs citados presentes en el clon superficial. |

`LO_QUE_ESCRIBIO_CADA_PROMPT` (hoy en `proceso/tests/test_t0_gobernanza_proceso.py`):
`"T-12": {Cerrado: {INF-5.2.2, INF-5.2.3, INF-5.2.4, INF-5.2.7}, Cerrado parcial: {INF-5.2.6}}`.
**Ojo FASE B:** el tracker está en `proceso/auditorias/`, la tabla de conteos en
`proceso/bitacora_conteos_y_entorno.md` (no en `CLAUDE.md`), y la suite de proceso se corre
aparte (`python -m pytest proceso/tests`).

## 10. Preguntas para el dueño

1. **Historia de git con los PDF (INF-5.2.3, T12-01).** El `git rm` no los quita de los
   commits anteriores. Opciones: (a) reescribir la historia (`git filter-repo` + empuje
   forzado de `main`: rompe los SHA que citan el tracker y los documentos); (b) dejar privado
   también el repositorio de la app. *Recomendación:* (b) hasta la sustentación; (a) sólo si
   se publica, y después.
2. **Botón «memoria resumida» en la ventana (T12-04).** *Recomendación:* al lote posterior;
   hoy sale con `cli.py --sesion … --html-resumida`.
3. **Nombre de la carátula** para `LICENSE` y `pyproject.toml` (hoy `Andy-rba30`), y la
   `version` de `pyproject.toml` (puse `0.1.0`, marcador). *Recomendación:* darlos antes de
   la sustentación.
4. **Los siete documentos técnicos de origen de proceso que quedan en `docs/`** (T12-02).
   *Recomendación:* dejarlos; a lo sumo `auditoria_y_ruta_despliegue_v9.md` (documento de
   trabajo) podría ir a `proceso/` reescribiendo sus dos citas.
5. **INF-5.2.1** (SHAs inverificables): sin acción en el prompt. *Recomendación:* dejarlo
   abierto con la nota; con un clon completo (`git fetch --unshallow`) volver a medir.

## 11. Lo que NO hice

- No fusioné ni empujé a `main`; no toqué el `.xlsx` (sólo lo moví) ni la tabla de conteos
  (movida entera, sin editar) ni escribí la fila de T-12 en `LO_QUE_ESCRIBIO_CADA_PROMPT`
  (FASE B).
- No corrí `python3 -m proceso.verificar_sesion` entero (corre la suite dos veces); compila,
  y su test de proceso (AST) pasa.
- No medí sí·sí, no·sí ni no·no (derivadas).
- No añadí el botón de la resumida a la GUI (ficha T12-04) ni toqué `gui/`.
- No reescribí las rutas históricas en prosa ni moví los siete documentos técnicos de §4.
- No reescribí la historia de git (pregunta 1).
- `INF-5.2.1` y lo ausente de `INF-5.2.6` (12 fuentes) siguen abiertos: dependen del dueño.
