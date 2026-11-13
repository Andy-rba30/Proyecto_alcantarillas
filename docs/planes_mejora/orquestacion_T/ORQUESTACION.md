# Convenciones de la sesión orquestadora de la cadena T (leer entero)

Eres un agente ejecutor de UN prompt de la cadena T. La sesión orquestadora te dio el número de prompt.
Trabajas en español (código, docstrings, commits), como el repositorio.

## Dónde está cada cosa

| Qué | Ruta |
|---|---|
| Repo de trabajo (app) | el worktree que te indique el orquestador (`/home/user/wt/T-n`); `/home/user/wt/main` es un checkout de `origin/main` SÓLO de consulta y `/home/user/Proyecto_alcantarillas` es del orquestador: no los toques |
| Cadena T (especificación de los prompts y sus REGLAS COMUNES §2) | `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md` del repo (copia fiel + NOTA DEL ORQUESTADOR al principio: **léela**, trae la tabla de equivalencias de IDs `INF-` —el ID canónico es el del INFORME, no el que escribe el prompt— y tres hechos que corrigen prompts posteriores) |
| Contrato de entradas que la cadena NO rellena | `docs/contrato_entradas.md` |
| INFORME (especificación) | `/home/user/andy-rba30/cotas-esviaje-alcantarillas/INFORME_evaluacion_app_alcantarillas_vs_PDF.md` |
| PDF de normas (repo Normas, 20 PDF, solo lectura) | `/home/user/andy-rba30/normas/normas/` (incluye `hec14.pdf` y `HydraulicsManual.pdf`, que NO están en `normas/` de la app) |
| Script QGIS | `/home/user/andy-rba30/cotas-esviaje-alcantarillas/cotas_esviaje_alcantarillas.py` |

## Antes de tocar nada

1. Lee `CLAUDE.md` del repo ENTERO (es largo; es la constitución del proyecto) y la §2 «Reglas comunes» de la cadena T.
2. Lee el INFORME en las secciones que tu prompt cita.
3. Antes de tocar un objeto consulta la hoja `Conflictos` del tracker y `docs/decisiones_diferidas.md` (regla 2 de «Reglas de corrección» de CLAUDE.md).

## Entorno

- `python3` es 3.13 con numpy, scipy, pytest, openpyxl y PyMuPDF instalados. NO hay tkinter ni se puede instalar
  (`apt` devuelve 503): la suite corre en la configuración **«PyMuPDF sí · Ventana Tk no»** de la tabla de CLAUDE.md.
- **Enlace a Normas (T-0): `export NORMAS_DIR=/home/user/andy-rba30/normas` en TODA orden que corra la suite, el
  manifiesto o el índice** (sin él, 7 tests de las dos fuentes nuevas se saltan y el par no es el de referencia).
- Par de referencia sobre `origin/main`: mídelo tú sobre tu base al empezar (tras T-2, `ad5cb97`, con `NORMAS_DIR`:
  **4390 passed / 16 skipped / 4406 collected**; sin `NORMAS_DIR`: 4383 / 23). El invariante es `passed + skipped = collected`.
- La suite entera tarda ~4–5 min sola (más si corren otros agentes a la vez: hay 4 CPU compartidas). Córrela con
  `NORMAS_DIR=/home/user/andy-rba30/normas python3 -m pytest -q -p no:cacheprovider --no-header > <archivo> 2>&1`
  y mientras iteras corre sólo los tests afectados. La suite completa verde es obligatoria antes de reportar FASE A y antes
  del commit de cierre. Si un test de TIEMPO (presupuesto de import, subprocesos) falla con la máquina cargada, repítelo
  solo antes de concluir nada; no lo relajes.
- Leer un PDF: `import fitz; d = fitz.open(ruta); d[i].get_text()` (i = página PDF − 1). Declara siempre página impresa Y página del PDF.
  Si una página es escaneo sin texto, renderízala (`page.get_pixmap(dpi=150).save(png)`) y léela como imagen con tu herramienta Read.
- No dejes archivos temporales en el repo: usa `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/`.
- NUNCA escribas sobre `/dev/null` con `cli.py --json /dev/null` (CLAUDE.md cuenta el incidente).

## Reglas que el dueño del proyecto declaró NO NEGOCIABLES

1. Las entradas de diseño (Q, cotas, CBR, datos de ANA/Junta, EMS) no se corrigen ni se rellenan con valores por defecto.
2. Ningún valor inventado: criterio [A] con ventana (`sensibilidad`) y justificación, o `valor=None` + `CriterioPendienteError`
   con mensaje que diga qué dato lo destraba.
3. Nada se rompe: los cuatro puntos de `tests/ejemplo_puntos.csv` siguen cargando; cada número de la línea base
   (`docs/linea_base.md`, `tests/linea_base_familia_c/`, `tests/ejemplo_puntos.referencia.json`) que se mueva se declara con su causa.
4. Si el prompt no puede cerrarse sin inventar un valor o sin una entrada del proyecto, NO lo fuerces: deja el criterio pendiente
   con el mensaje que diga qué lo destraba, y sigue con el resto del prompt.

## PARADAS OBLIGATORIAS (decide el dueño, no tú)

Detente y devuélvele la pregunta al orquestador (en tu informe final, con las opciones, tu recomendación y la evidencia),
SIN aplicar el cambio, en cualquiera de estos tres casos:

- (a) la elección del marco de estabilidad del cabezal (T-7b punto 1);
- (b) la elección entre las dos opciones de velocidad máxima de TMC (T-4 punto 3);
- (c) **cualquier cambio que mueva un diámetro (o sección B×H) ya dimensionado en el fixture** — es decir, que cambie el D adoptado
  de algún punto en `tests/linea_base_familia_c/`, `tests/ejemplo_puntos.referencia.json`, `docs/linea_base.md`, `docs/guia_perfil.md`
  o en cualquier test que fije un diámetro. Antes de cerrar, compara los diámetros de la corrida del fixture antes/después
  (por ejemplo con `cli.py --comparar` o el comparador de E-B) y dilo explícitamente en tu informe: «diámetros movidos: ninguno» o la lista.
  Si una parte de tu prompt lo movería, implementa todo lo demás, deja esa parte SIN aplicar (o aplicada sólo como alternativa
  barrible que no cambia el valor por defecto) y repórtalo.

### Decisiones que el dueño YA tomó (2026-11-11) — aplícalas, no vuelvas a preguntar

- **(b) T-4 punto 3 → OPCIÓN A**: `v_max_tmc` pasa a [A] con ventana y justificación (abrasión; manual MTC 4.1.1.3.7 e);
  Tabla 8-4 de WSDOT como referencia de nivel de abrasión); NO se sustituye por la regla de nivel de abrasión + calibre.
  El valor y la ventana exactos y la redacción de la ficha: los que la verificación contra el PDF sostenga (el orquestador
  te pasa el dictamen del verificador normativo en el encargo de T-4).
- **(a) T-7b punto 1 → OPCIÓN (b)**: rige LRFD AASHTO 11.6; la verificación ASD de E.050 se calcula e imprime en paralelo;
  cuál rige se declara [A] con justificación (dictamen del verificador en el encargo de T-7b).
- La parada (c) —mover un diámetro del fixture— sigue vigente.
- `borde_libre_bajo_tw_ahogante` = `no_cumple` (T-2); `aviso` sólo como alternativa barrible.
- FEN: se adopta el más conservador; `serie_sin_fen` con menos lluvia que la completa bloquea el cálculo hidrológico (T-1).
- Umbrales electroquímicos de AASHTO LRFD sobre TMC: por analogía, `aviso` por defecto, `excluye` barrible (T-4).
- Familia B: aceptación «V1 + V2 + V4 + V5 + espaciamiento de la Fase 10» (se cablea en T-9).
- Cuando una fuente no da cifra, el valor es [A] con ventana y la ficha lo dice; la exclusión de un material o el bloqueo de un
  punto se apoyan en la fuente específica, y las analogías avisan (criterio general que el dueño aprobó para T-4).

### Lecciones de las auditorías del lote 1 (evítalas de entrada)
- No atribuyas a una cita lo que es elección del proyecto: fuente / interpretación / lo que el proyecto hace van separados.
- Ninguna columna u entrada «opcional» puede rellenarse en silencio, y menos del lado no conservador: o es obligatoria, o su
  ausencia sale como AVISO en CLI/JSON/memoria (no sólo en una nota del paso HTML).
- Todo aviso/indicador debe llegar a `InformePunto.avisos()` (CLI, JSON y memoria), no sólo a un paso.
- Guardias de segunda línea en las funciones públicas (signo, finitud, NaN) con la forma MAT-D13, aunque M0 ya valide el CSV.
- Los dorados se calculan a mano con la aritmética escrita, independientes de la fórmula cerrada del código.
- Escribe los tests PRIMERO en rojo (`xfail(strict=True)`); si no lo haces, mide el rojo contra el árbol base y decláralo.
- Comprueba cada consumidor de un valor que ahora puede ser `None` (CSV de resumen incluido).
- `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT` lleva la tabla de lo que cada prompt escribe en el tracker: añade tus filas al integrar.

El dueño añadió: **«igual verifica: todo tiene que ser ingenierilmente coherente y también con la norma, porque será para una
tesis»**. Consecuencia para ti: (1) toda cita y todo valor [N]/[N→]/[C] que escribas lo verificas TÚ contra el PDF (numeral,
título literal, página impresa y página PDF, texto); si el título del numeral no corresponde a lo que le atribuyes, no lo
cites; (2) comprueba la coherencia ingenieril con un caso numérico a mano (unidades SI, órdenes de magnitud, dirección del
conservadurismo) antes de dar por buena una fórmula; (3) si la cadena T te pide algo que la fuente contradice, gana la fuente:
impleméntalo como la fuente dice, declara la discrepancia y repórtala; (4) antes de tu commit de cierre el orquestador
pasará un auditor adversarial sobre tu diff: deja el trabajo auditable.

## Git

- Serie de commits: `tesis(T-n): <resumen> — <IDs del INFORME cerrados>`. UN commit por prompt en `main`
  (puedes hacer commits intermedios en tu rama; al integrar se aplastan en uno).
- Pie de TODOS los commits (obligatorio, tal cual):

  ```
  Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_015HTdHjggReUnNNncetQU39
  ```

- No escribas el identificador del modelo en ningún otro sitio del repo (ni en docs, ni en el tracker: como «Responsable» usa
  «Claude Code (cadena T, T-n)»).
- No abras pull requests. Push: `git push -u origin main`; si falla por red, reintenta hasta 4 veces (2 s, 4 s, 8 s, 16 s).
  Antes de empujar: `git fetch origin main` y rebase si hace falta.
- El clon es superficial (depth 1): no hace falta más historia.

## Dos modos de trabajo (el orquestador te dice cuál)

**MODO SECUENCIAL** (trabajas directamente en `main`, nadie más escribe): haces el ritual de cierre entero tú mismo,
incluido push a `origin/main` y medición del par sobre ese árbol.

**MODO PARALELO** (trabajas en un worktree, rama `tesis/T-n`; otros agentes trabajan a la vez en otras ramas):
- FASE A (ahora): implementa el prompt entero con sus tests, suite verde EN TU RAMA, commits en tu rama.
  NO toques todavía: `docs/auditorias/matriz_cruzada_auditorias.xlsx` (binario: no se puede fusionar),
  la tabla de entornos/conteos de `CLAUDE.md`, ni `verificar_sesion.py`. Los documentos generados
  (`manifiesto_citas.md`, `manifiesto_registro_normativo.md`, `trazabilidad.csv`, `indice_formulas.md`) regenéralos si tu
  suite los necesita verdes, sabiendo que se volverán a regenerar al integrar. En tu informe de FASE A entrega las filas
  del tracker que habrá que escribir (ID, estado, nota). Añade criterios al FINAL de su sección de `criterios_adoptados.py`
  (nunca reordenes) y constantes nuevas en bloque propio con cabecera `# --- T-n ---`.
  NO fusiones a main ni empujes. Termina y reporta.
- FASE B (cuando el orquestador te escriba «integra»): `git fetch origin main`, rebase de tu rama sobre `origin/main`
  aplastada en UN commit `tesis(T-n): …`, resuelve conflictos (los censos numéricos de los tests —conteo de criterios,
  marcas `literal-ok`, filas del tracker— se recalculan sobre el árbol fusionado), regenera los cuatro documentos generados,
  escribe el tracker y `decisiones_diferidas.md`, actualiza la tabla de CLAUDE.md, suite entera verde, fast-forward de `main`,
  push, y devuelve el informe final con el SHA.

## Informe final que debes devolver (corto y veraz)

1. IDs cerrados: entero / en parte / no (con una línea de por qué).
2. Tests nuevos (archivo y cuántos) y el par de la suite `passed / skipped / collected` medido, diciendo sobre qué árbol.
3. Números de la línea base movidos y por qué; **«diámetros movidos: ninguno»** o la lista.
4. Qué quedó diferido (con símbolo) y qué criterios quedaron pendientes con el dato que los destraba.
5. SHA del commit (y si quedó en `origin/main` o sólo en la rama).
6. Paradas obligatorias que encontraste (pregunta + opciones + recomendación), si hubo.
7. Cualquier cosa del prompt que NO hiciste, dicho sin adornos. No reportes como hecho lo que no verificaste.

## ENMIENDA DE LA SESIÓN DE REANUDACIÓN (2026-11-12, tercera sesión) — gana sobre lo de arriba donde discrepe

- **Base**: `origin/main` = `df1b23c` (T-0, T-2, T-4, T-1, T-6 y T-8 integrados). Par de referencia con `NORMAS_DIR`:
  **4960 passed / 16 skipped / 4976 collected** (sin `NORMAS_DIR`: 4942 / 34). 102 criterios, 35 sin valor.
  `docs/decisiones_diferidas.md` tiene ocupadas las Partes hasta la XLV (T-8): usa rótulo provisional y se renumera al integrar.
- **Rutas**: INFORME y script QGIS en `/home/user/andy-rba30/cotas-esviaje-alcantarillas/`; PDF en
  `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`). Temporales SÓLO en
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-n/` (créala).
- **Guardado de progreso (obligatorio, puede haber cortes por límite de uso en cualquier momento)**: commit intermedio en tu rama
  cada vez que tengas un bloque coherente y `git push -u origin tesis/T-n` (o `--force-with-lease` tras un rebase) después de CADA
  commit. Nunca `git stash`. Si te cortan, otro agente retoma desde la rama del remoto: deja el mensaje del commit diciendo qué falta.
- **FASE B (integrar)** en esta sesión: `git fetch origin main`; rebase de tu rama sobre `origin/main` aplastada en UN commit
  `tesis(T-n): …`; ritual entero; suite verde; `git push origin HEAD:main` (fast-forward del remoto; si lo rechaza porque `main`
  avanzó, vuelve a rebasar, re-mide y reintenta; nunca `--force` sobre `main`); después `git fetch origin main`, confirma
  `git rev-parse origin/main == HEAD` y remide el par sobre ese árbol. Deja también la rama `tesis/T-n` empujada en ese commit.
- **4 CPU compartidas entre varios agentes**: no lances la suite entera más de lo necesario (itera con los tests afectados);
  la suite entera puede tardar 8–15 min con la máquina cargada. Los tests de TIEMPO que fallen bajo carga se repiten solos.
- **Lecciones añadidas por T-6 y T-8** (además de las de arriba): un bloqueo leído FUERA de `servicio._etapa` tumba la corrida
  (toda excepción de `ErrorProyecto` nueva se captura como `Bloqueo` del punto); un `MetodoNoEvaluableError` lleva el rótulo de
  SU fuente (`rotulo=`), no el de HDS-5; un verbo de obligación exige una cita con ese carácter (si la fuente dice «is typically»,
  es `Interpretacion`); los techos de tamaño de la memoria (`tests/test_ext8_*`: KB y páginas por punto) se REMIDEN y se dicen, no
  se relajan a ojo; la tabla `LO_QUE_ESCRIBIO_CADA_PROMPT` y los censos (criterios 102, `CLAVES_EXTERNAS` 18, marcas `literal-ok`
  de `dominios.py` 11) se recalculan sobre el árbol fusionado.
- **Informe final**: además de devolverlo, ESCRÍBELO en
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-n_<fase>.md`
  y devuelve al orquestador un resumen de MENOS DE 400 PALABRAS con: IDs (entero / en parte / no), tests nuevos y par medido,
  números movidos («diámetros movidos: ninguno» o la lista), diferidos, SHA y rama, paradas para el dueño.

## ENMIENDA DE LA CUARTA SESIÓN (2026-11-13) — gana sobre TODO lo de arriba donde discrepe

- **Base**: `origin/main` = `e78a4e7` (T-0, T-2, T-4, T-1, T-6, T-8, T-5 y las correcciones de T-8 integrados). Par de referencia
  con `NORMAS_DIR`: **5230 passed / 16 skipped / 5246 collected** (sin `NORMAS_DIR`: 5212 / 34). 109 criterios, 34 sin valor,
  `CLAVES_EXTERNAS` 18. `docs/decisiones_diferidas.md` tiene ocupadas las Partes hasta la XLVI (T-5; la XLV es T-8 con T8-01..12).
- **Rutas de ESTA sesión** (las de arriba, con `003c3043-…`, ya no existen):
  - carpeta de orquestación (este archivo, PRECISIONES, INFORMES de FASE A, DECISIONES, auditorías): `ORQ` =
    `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/` (SÓLO LECTURA para los agentes: la escribe el orquestador);
  - scratchpad: `SP` = `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/`
    (temporales en `SP/T-n/` o `SP/T-n-aud/`; informes en `SP/INFORME_T-n_<fase>.md` / `SP/AUDITORIA_T-n.md`);
  - INFORME y script QGIS: `/home/user/andy-rba30/cotas-esviaje-alcantarillas/`; PDF: `/home/user/andy-rba30/normas/normas/`
    (`export NORMAS_DIR=/home/user/andy-rba30/normas`);
  - worktrees: `/home/user/wt/T-3`, `/home/user/wt/T-9`, `/home/user/wt/T-7a` (ramas `tesis/T-n`, base `df1b23c`, FASE A hecha);
    `/home/user/wt/main` = `origin/main` de consulta; `/home/user/Proyecto_alcantarillas` es del orquestador.
- **Pie de TODOS los commits de esta sesión** (sustituye al de arriba):

  ```
  Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01Jteyqg5CzW7hzPFvqiat9M
  ```

- **Decisiones del dueño del 2026-11-12** (`ORQ/DECISIONES_DUENO_2026-11-12.md`): son decisiones tomadas para T-3, T-9 y T-7a;
  se aplican, no se vuelven a preguntar. Sigue ganando la fuente primaria y **ningún diámetro, sección ni material adoptado del
  fixture se mueve** (A-01 y A-02 concreto Ø 0.90; B-01; C-01 marco 1.20 × 0.90 donde dimensiona).
- **4 CPU compartidas**: la suite entera (~5 min sola) se corre lo imprescindible; los auditores NO la corren entera (el
  implementador ya la midió y la integración la remide): tests afectados y mutación acotada.
- **Lecciones de T-5 y de las correcciones de T-8** (además de las de arriba): un punto al que sólo le falta un DATO no es «no
  factible» (se relanza el `DatoFaltanteError`); una decisión del dueño cuya premisa contradice el PDF NO se aplica tal cual: se
  deja lo que la fuente sostiene y se reporta; los tests que cambian de verdad se reescriben DECLARÁNDOLO (qué pasaba, qué pasa,
  por qué), nunca en silencio; el rojo se mide con el archivo final contra la base; `/dev/null` nunca como destino de `--json`.

## ENMIENDA DE LA QUINTA SESIÓN (2026-11-13 17:16 UTC) — gana sobre TODO lo de arriba donde discrepe

- **Base**: `origin/main` = `14f6138` (T-0 a T-10 integrados, cabezal completo). Par con `NORMAS_DIR`: **6337 passed /
  23 skipped / 6360 collected** (sin `NORMAS_DIR`: 6319 / 41). 141 criterios, 20 sin valor.
- **Rutas de ESTA sesión**:
  - `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/` (enlace simbólico a `/home/user/orq`, worktree de
    `tesis/orquestacion-estado`; SÓLO LECTURA para los agentes);
  - `SP` = `/tmp/claude-0/-home-user-Proyecto-alcantarillas/7cb96d40-c574-5ae4-841a-e8d6d2b9b04b/scratchpad/`
    (temporales en `SP/T-n/`, informes en `SP/INFORME_T-n_<fase>.md`, auditorías en `SP/AUDITORIA_T-n.md`). Toda mención de
    `1cd08434-…` o `003c3043-…` en los encargos se lee con ESTA ruta;
  - INFORME y script QGIS: `/home/user/andy-rba30/cotas-esviaje-alcantarillas/`; PDF: `/home/user/andy-rba30/normas/normas/`
    (`export NORMAS_DIR=/home/user/andy-rba30/normas`);
  - worktrees: `/home/user/wt/main` (consulta, `origin/main`), `/home/user/wt/T-11` (rama `tesis/T-11`).
- **Pie de los commits de esta sesión**: el del aviso de atribución que reciba cada agente; si no lo recibe:

  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01UcoTV8c2xW71eEw7p9oHgo
  ```

- Reparto: Opus 5.5 (esfuerzo extra) para implementación, correcciones medias/bajas e integraciones; Fable SÓLO para la
  auditoría adversarial de T-11 y para corregir lo que una auditoría encuentre fuera de lugar en fórmulas o citas.
