# Convenciones de la sesión orquestadora de la cadena T (leer entero)

Eres un agente ejecutor de UN prompt de la cadena T. La sesión orquestadora te dio el número de prompt.
Trabajas en español (código, docstrings, commits), como el repositorio.

## Dónde está cada cosa

| Qué | Ruta |
|---|---|
| Repo de trabajo (app) | `/home/user/proyecto_alcantarillas` (o el worktree que te indique el orquestador) |
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
- No dejes archivos temporales en el repo: usa `/tmp/claude-0/-home-user/8c9a9d01-15e4-5a10-91d4-d894b414664c/scratchpad/`.
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
  Claude-Session: https://claude.ai/code/session_011fq2pFDnSitdx4Vq8wp8Zz
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
