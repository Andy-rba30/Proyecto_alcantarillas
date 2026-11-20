# AUDITORÍA ADVERSARIAL DE T-12 (FASE A) — repositorio listo para la sustentación

- Auditado: `/home/user/wt/T-12`, rama `tesis/T-12`, HEAD `78a7780`; base `f77c5d4`.
- Auditor: solo lectura. Temporales en `SP/T-12-aud/` (exportaciones `export/` = HEAD y `base/` = f77c5d4 por `git archive`; `clon/` = clon independiente para la mutación; `out/{base,head}/` = corridas de la CLI; `scripts/`). Nada escrito en `/home/user/wt/T-12` (`git status` limpio al cerrar).

## Veredicto: **AJUSTADO**

El cálculo NO se movió (refutación intentada en cuatro corridas y fallida), los PDF están byte a byte en el repositorio de normas, nada se borró salvo los 18 PDF y las secciones de `CLAUDE.md` salieron enteras. Pero la **propiedad central —el entregable se sostiene solo— está REFUTADA**: la suite sobre `git archive HEAD` con `NORMAS_DIR` da **2 failed, 6370 passed, 25 skipped (collected 6397)**, uno de los fallos introducido por T-12. Y la memoria resumida pierde tres cosas que la completa dice a propósito (la remisión de acotación, la advertencia de corredor / el origen de los [S] y la fila de h_o del punto). Nada de esto toca cálculo; todo se corrige en una pasada corta.

**Diámetros / secciones / materiales / HW movidos: ninguno.**

---

## Refutado con evidencia

### H1 · ALTA — La suite del entregable NO pasa sobre una exportación (`git archive` / «Download ZIP» de GitHub)

Evidencia (la corrida entera, una vez, sobre la exportación):
```
git -C /home/user/wt/T-12 archive HEAD | tar -x -C SP/T-12-aud/export
cd SP/T-12-aud/export && NORMAS_DIR=/home/user/andy-rba30/normas python3 -m pytest -q -p no:cacheprovider --no-header -rs
→ 2 failed, 6370 passed, 25 skipped in 419.13s   (collected 6397)
FAILED tests/test_sin_literales.py::test_ningun_py_fuera_de_src_se_queda_sin_declarar
   AssertionError: 'proceso' ya no existe: su exencion caduco
FAILED tests/test_ext11_mutacion.py::test_el_arnes_mata_de_verdad_un_mutante_conocido
   CalledProcessError: ['git','ls-files','--cached','--others','--exclude-standard'] returned 128
SKIPPED tests/test_ext6_registro_normativo.py:202: sin git o fuera de un checkout
SKIPPED tests/test_t12_entregable.py:527: sin git o fuera de un checkout
```
- El primero lo **introduce T-12**: añadió `"proceso"` a `test_sin_literales.DIRECTORIOS_FUERA_DEL_BARRIDO`, y la guardia de caducidad exige que cada directorio exento exista (`assert (RAIZ / directorio).is_dir()`). Sobre la base exportada ese test pasa (medido: `base/` → 1 passed). La guardia de T-12 `test_ningun_test_del_entregable_lee_material_de_proceso` no lo vio porque el nombre llega por clave de diccionario y no como `RAIZ / "proceso"` literal.
- El segundo es **anterior a T-12** (falla igual sobre `base/` exportada) pero cae dentro del encargo «el entregable se sostiene solo»: `tests/apoyo/mutacion.py::_archivos_del_arbol` exige `.git`.
- Los dos saltos por falta de `.git` son legítimos y están dichos; el par del implementador (6374/23) es el de un checkout, no el de la exportación.
- Consecuencia: quien siga el §7 del README sobre el ZIP de GitHub (que respeta `export-ignore`) obtiene una suite roja.

Corrección:
1. `tests/test_sin_literales.py::test_ningun_py_fuera_de_src_se_queda_sin_declarar`: la caducidad de `"proceso"` no se exige cuando el árbol es una exportación (p. ej. `if directorio == "proceso" and not (RAIZ / directorio).exists(): continue`, con el comentario «una exportación no lo lleva: `.gitattributes`»), o sacar `proceso` del dict y declararlo como exención condicionada.
2. `tests/test_ext11_mutacion.py::test_el_arnes_mata_de_verdad_un_mutante_conocido` (o `mutacion._archivos_del_arbol`): `pytest.skip` sin `.git`, como ya hacen `test_ext6` y `test_t12`.
3. Declarar en el informe y en la bitácora el par MEDIDO sobre la exportación (tras corregir, esperable 6371–6372 passed / 25–26 skipped) además del de checkout.

### H2 · MEDIA — La resumida imprime una adopción sobre vacío verificado como si fuera una cita corriente

`_filas_verificaciones(..., remision_acotacion=False)` quita el enlace «☛ acotación» y la resumida no tiene bloque de acotaciones; no lo sustituye nada. Es justo lo que el propio código prohíbe: «La fila sola engaña: dice la etiqueta y la clave, y de ahí se lee una cita normativa corriente. No lo es» (comentario en `M11._filas_verificaciones`; docstring de `M11.bloque_acotaciones`, linaje NOR-VAC-01).

Evidencia (juego de T-11 por la CLI, filas de la resumida que no son subcadena del bloque del punto en la completa, excluida la tabla de criterios):
```
juego  punto-B-01 FILA: <tr><td>G1</td>... <span class="etiqueta et-C">C</span> <code>cobertura_minima_aashto</code></td><td>cumple...
juego  punto-C-01 FILA: <tr><td>V9</td>... <span class="etiqueta et-A">A</span> <code>secciones_cajon_normalizadas</code></td><td>cumple...
(completa: la misma fila + <a href="#acotaciones" class="remision" ...>&#9755; acotacion</a>)
```
Corrección: con `remision_acotacion=False`, sustituir el enlace por una marca de texto (p. ej. `<span class="remision">adopción sobre vacío verificado — ver acotaciones en la memoria completa</span>`), sin números, y un test que exija la marca en toda fila de la resumida cuyo `ca.CRITERIOS[v.criterio_aplicado].vacio_verificado` no esté vacío.

### H3 · MEDIA — La resumida no lleva la advertencia de corredor ni el origen de los [S]

La resumida no tiene `bloque_datos_sitio`: ni la línea «Corredor de los datos de sitio … (origen …)», ni `datos_sitio.advertencia_de_corredor`, ni de qué archivo salió cada [S] (regla (3) de EXT-10 en `CLAUDE.md`; EXT-V-01). El encabezado de la resumida afirma ser «el MISMO encabezado que el de la memoria completa», y lo es en las huellas, pero la advertencia de que los [S] son los de la obra del repositorio desaparece justo en la vista que se imprime.
```
fix_per  completa: 'Advertencia de corredor' = 1 | resumida = 0
juego    completa: 'Advertencia de corredor' = 1, 'declarado (sesion)' = 3 | resumida = 0, 0
```
Corrección: llevar a la resumida la línea del corredor y la advertencia (`ds.advertencia_de_corredor` con el corredor del `ContextoCorrida`, lo mismo que hace `bloque_datos_sitio`) y una tabla compacta de los [S] usados con valor y origen; test: el texto de la advertencia de la completa está en la resumida.

### H4 · MEDIA — La suite de proceso congela la bitácora que `CLAUDE.md` manda actualizar, y nadie corre esa suite

- `proceso/tests/test_t12_proceso.py::test_la_bitacora_y_las_reglas_se_movieron_enteras_sin_reescribir` exige que `proceso/bitacora_conteos_y_entorno.md`, desde «## Cierre de tarea» hasta el final, sea BYTE A BYTE la sección de `git show f77c5d4:CLAUDE.md`.
- `CLAUDE.md` («Material de proceso») y `proceso/README.md` dicen «**La tabla de conteos se actualiza allí/aquí**», y el propio informe de T-12 encarga a la FASE B actualizarla. La primera actualización (la de T-12) pone ese test en rojo.
- Y no lo verá nadie: `proceso/verificar_sesion.py` paso 1 corre `python -m pytest -q`, que por `testpaths` es solo `tests/`; la suite de proceso no la invoca ningún ritual.

Corrección: que el test compare sólo lo que no debe cambiar (las reglas, y de la bitácora el texto anterior a la tabla, o un prefijo anclado), o que se retire después de la FASE B dejándolo dicho; y añadir `python -m pytest proceso/tests` al paso 1 de `verificar_sesion` (o al ritual escrito en la bitácora).

### H5 · MEDIA — INF-5.2.2 no está cerrado «entero»: el entregable sigue llevando prompts y asignación de modelos de IA

INF-5.2.2 nombra «13 prompts literales» y material de desarrollo con IA. Quedan en `docs/` (y en la exportación):
```
docs/hoja_de_ruta_correcciones_v12.md : «**Prompt (Sonnet 5, esfuerzo `medium`):**», tabla «Modelo | Fable 5 (el especialista) · Opus 5 … · Sonnet 5 …», «Sobre Fable 5 … planes Max»; 25 × «Opus 5»
docs/ruta_familia_c.md                : 17 × «Opus 5», 5 × «Fable», 4 × «Sonnet 5»
docs/auditoria_y_ruta_despliegue_v9.md: 15 menciones de «prompt»
```
Lo declara la ficha T12-02, pero la fila del tracker propuesta dice «Cerrado» y el informe «entero». Medido: `hoja_de_ruta_correcciones_v12.md` y `auditoria_y_ruta_despliegue_v9.md` no los lee ningún test ni ningún módulo en ejecución (sólo docstrings/comentarios como procedencia); `ruta_familia_c.md` SÍ es dependencia de ejecución (`vacio_verificado="ruta_familia_c.md Sec. …"`, que `_verificar_criterio` comprueba al importar) y debe quedarse.
Corrección: o mover los dos sin dependencia a `proceso/` con el mismo criterio de T12-02 (rutas en prosa no reescritas, traducidas por `proceso/README.md`), o escribir la fila como «Cerrado con salvedad» nombrando los tres documentos y el contenido de IA que conservan.

## Sospechas (sin caso vivo en las cuatro corridas) y defectos menores

### H6 · BAJA (sospecha) — La resumida pierde la fila «h_o fuera de rango» del punto (NOR-HDS-05: «dicha EN EL PUNTO»)
`_tabla_diseno_con_perfil` añade, sólo en la completa, la fila que dice «PIDE CAUTELA» / «NO DEBE USARSE» y qué HW se usó; no está en `InformePunto.avisos()`. Juego, C-01: completa 1 fila, resumida 0 (aquí el HW impreso es el del remanso y es correcto). El caso que importa —banda 0.75–1.2 con la aproximación rigiendo y «PIDE CAUTELA»— no se da en las corridas medidas. Corrección: pasar esa fila a `_filas_combinacion_adoptada` (sus números ya están en la completa) o su texto a los avisos de la resumida.

### H7 · BAJA — Los tests de la resumida son de conjunto de números, insensibles a la posición
Mutación acotada (`tests/apoyo/mutacion.py` sobre `resumen_de_punto`, `_criterios_A_del_punto`, `pendientes_resumidos`, `memoria_resumida_html`, `_celda_control_gobernante`, `_filas_combinacion_adoptada`, `_remision_a_la_completa`; objetivo `tests/test_t12_entregable.py`): **39/47 muertos**. Sobreviven: el intercambio `V_erosion`↔`V_sedimentacion` y `n_min`↔`n_max` en el formateador común (las dos vistas cambian a la vez y el test de conjunto no lo ve), `numero_celdas != 1` → `== 1`, y **`if informe.cerrado:` → `if not informe.cerrado:` en `memoria_resumida_html`** (la resumida diría «cerrado» de un expediente que no cierra). Este último lo mata `test_linea_base` (medido: 1 failed) por el diff de bytes, no un test semántico. La resumida además REPITE el formateador del estado del expediente en vez de compartirlo con la completa. Corrección: test de identidad de filas (cada `<tr>` de verificaciones y combinación de la resumida es subcadena del bloque del punto en la completa, salvo la marca de H2) y test de que el estado de la resumida coincide con el de la completa (o compartir el formateador).

### H8 · BAJA — Textos que dicen algo que ya no es cierto
- `CLAUDE.md` «Fuente de verdad»: «el PDF en `normas/`, o en el repositorio de normas…» (la app ya no tiene PDF).
- `src/normativa/fuentes.py`, comentario de las fuentes de T-0: «Por eso estan en `SOLO_EN_EL_REPO_NORMAS`» (símbolo retirado).
- `tests/test_normativa_pdf.py` docstring: «DESDE T-0 «normas/» SON DOS CARPETAS … `normas/` de este repositorio mientras exista»; `tests/test_t0_gobernanza.py` cabecera ítem 5: «con caida a `normas/`»; `tests/test_decisiones_diferidas.py`: «Regla 4 de CLAUDE.md» (vive ahora en `proceso/reglas_de_correccion_de_auditorias.md`).
- `tests/apoyo/rotulo_fixture.BLOQUE` dice «sobre el CSV del ejemplo y entradas de prueba (`entradas_ampliadas.json`)» también en `memoria_perfil.html` (corrida 1, SIN `--datos-externos`) y en `memoria_punto_cajon.html` (driver, sin CLI).
- README §7 omite el eje del intérprete POSIX (`test_linea_base` salta sin `sh`, que el README anterior sí decía) y afirma que la línea base fija «byte a byte lo que el programa escribe» cuando las memorias llevan el rótulo del generador; README enlaza `proceso/README.md`, ausente en la exportación.
- `cli.main`: con `--pdf x.pdf --html-resumida` y caída a la vía del navegador, la resumida nombra `x.pdf` como «escrita en la MISMA invocación», pero lo escrito es `x.html` (`_escribir_pdf` usa `destino.with_suffix(".html")`).

## Lo que intenté refutar y NO pude (confirmado)

1. **Sin cambios de cálculo.** Fixture a perfil y a expediente con `entradas_ampliadas.json`, juego completo y juego titular de T-11, por la CLI sobre `base/` y sobre `export/`: `cli.py --comparar` → **IGUALES** las cuatro; diff crudo normalizado de JSON y CSV: 0 líneas; texto de la CLI: sólo la línea «Memoria resumida (HTML)»; memorias completas: única diferencia la cadena de T11-09 (fix_per A-02; juego y titular A-02 y B-01), y JSON `HW_salida_m = null` exactamente en esos puntos. `ResultadoHidraulico.salida_no_se_forma` ≡ la condición de `cli.salida_no_se_forma` de la base (`sustituye_aproximacion and HW_remanso_m is None`, con perfil). `_escribir_pdf` reproduce el `exportar_pdf` de la base línea a línea. `_advertencia` es una puerta estrecha: sólo esa clave, sólo `str`; cualquier otra clave de nivel superior sigue siendo `DatoInvalidoError` (lo prueba el test y lo leí en `servicio.cargar_datos_externos`). Ningún literal numérico nuevo en `src/`; M11 sin aritmética (su test de AST pasa).
2. **Línea base.** Cambian sólo las 4 memorias (rótulo; `memoria_perfil_ancha` además la cadena de A-02), `cli_expediente.txt` (+1 línea), `entradas_ampliadas.json` (+`_advertencia`), `regenerar.sh`, README y la memoria resumida nueva. Los cuatro JSON, los dos CSV y los otros cuatro `cli_*.txt`: idénticos. El rótulo lo pone `regenerar.sh` vía `tests/apoyo/rotulo_fixture.py`; el programa no lo conoce.
3. **Nada se borró.** `git diff -M --name-status`: 18 D (los PDF), 23 R100, R095/R090/R084 (rutas), 31 M, 14 A. `test_t0_gobernanza` repartido por AST: todo lo de la base está en `tests/` o en `proceso/tests/`, sólo con rutas cambiadas. Las dos secciones de `CLAUDE.md` están enteras en `proceso/` (comprobado como subcadena y por el test de proceso); las líneas 1–760 de `CLAUDE.md` son idénticas a la base. Ningún test que salió comprobaba algo del entregable que ahora nadie compruebe (el de las 22 fichas sigue, en la suite de proceso — con la salvedad de H4).
4. **PDF.** sha1 de los 18 de `/home/user/wt/main/normas/` = los de `/home/user/andy-rba30/normas/normas/` (18 IGUAL), y los 18 blobs de `git ls-tree f77c5d4 normas/` están en Normas (0 faltan; Normas tiene 20). `ruta_pdf`, `python3 -m src.normativa.extraccion sha1 hec14 / E.060` y `verificar_sesion` paso 5 funcionan con `NORMAS_DIR`; sin él, `directorios_de_normas() == ()`, `ruta_pdf → $NORMAS_DIR/normas/hec14.pdf`, la extracción sale con mensaje; con `NORMAS_DIR=/no/existe`, `FileNotFoundError`. Con `NORMAS_DIR`, ningún test `pdf` salta (exportación); sin él, los 150 `pdf` saltan con un solo motivo.
5. **README** seguido sobre la exportación: corrida de perfil con `--html --html-resumida --csv-resumen` (rc 1, cuatro archivos, JSON por defecto `<csv>.informe.json`), CSV inexistente → rc 2, `--sesion … --html … --html-resumida …` y `--pdf … --pdf-resumida …` (weasyprint 69.0: los dos PDF), ejemplo de `sitio.json` aceptado. `pyproject.toml`: mismas dependencias y versiones que `requirements*.txt`, ninguna nueva.
6. **Memoria en dos vistas.** Ninguna fila de verificación, combinación, cuadro, alcance o resumen de la resumida contradice a la completa (identidad de subcadena por punto, salvo H2); los 23 «no cumple» del juego (cabezal E/A incluidos) están en la resumida; todos los avisos de `InformePunto.avisos()` y todos los bloqueos del punto están, y los avisos son subcadena del bloque completo; no imprime como «salida» una aproximación descartada; mismas huellas y hora. El test «ningún número…» no es vacuo (por punto, >20 números), pero es débil (H7).
7. **Licencia y privacidad.** `LICENSE`: todos los derechos reservados, nota de las normas, MIT posterior, autor `Andy-rba30` con la línea de dónde cambiarlo. `grep -rIE` de correos: ninguno en HEAD ni en base; identificadores de modelo: el mismo conjunto que en la base, sólo movido (ver H5 para lo que queda en `docs/`).

## Pares medidos

| Árbol | `NORMAS_DIR` | Resultado |
|---|---|---|
| `git archive HEAD` (sin `proceso/`, sin `.git`), suite entera | sí | **2 failed, 6370 passed, 25 skipped** (collected 6397) |
| `git archive HEAD`, `-m pdf` | no | 150 skipped (un motivo) |
| clon de `78a7780`, `proceso/tests` | sí | 142 passed |

## Preguntas para el dueño (con recomendación)

1. **Documentos con prompts y modelos de IA que quedan en `docs/` (H5).** Recomiendo mover a `proceso/` `hoja_de_ruta_correcciones_v12.md` y `auditoria_y_ruta_despliegue_v9.md` (ni código ni tests los leen) y dejar `ruta_familia_c.md` (el código lo exige al importar) declarando la salvedad; INF-5.2.2 «Cerrado con salvedad».
2. **Subagentes.** `.claude/agents/` pasó a `proceso/.claude/agents/`, donde Claude Code ya no los registra. Para el lote posterior aprobado, ¿deben seguir disponibles? Recomiendo dejarlos en `proceso/` y que el lote posterior los copie a su sesión si los necesita.
3. **Historia de git con los PDF** (pregunta 1 del implementador): coincido — repositorio de la app privado hasta la sustentación; reescribir la historia sólo si se publica.
