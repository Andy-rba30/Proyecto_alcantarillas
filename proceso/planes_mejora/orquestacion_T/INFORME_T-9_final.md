# Informe final — T-9 (espaciamiento de alivios, Fase 10), correcciones + integración

## 1. Entrega

- **`origin/main` = `c654a16`** (fast-forward desde `6c25f1d`, `tesis(T-3)`; un solo commit
  `tesis(T-9): espaciamiento de alivios — … — INF-5.1.12, INF-3.3.8 (cerrados); INF-5.1.8 (en parte)`).
  Confirmado con `git fetch origin main`: `origin/main == HEAD == c654a16`. La rama `tesis/T-9`
  quedó empujada en el mismo commit (`--force-with-lease`, sólo sobre la rama; `main` nunca con `--force`).
- Ritual: la rama `tesis/T-9` (FASE A + correcciones H1–H11 y decisiones A–D, sobre `df1b23c`) se
  aplastó sobre `6c25f1d`. Conflictos resueltos conservando las dos partes: `modelos.py`, `citas.py`,
  `fundamentos.py` (paréntesis y llaves de cierre de las dos entradas), `constantes_normativas.py`,
  `variables_entrada.py`, `casos_patron.py`, `test_memoria_sustentada.py`, `test_ext8`,
  `test_t0_gobernanza.py` (filas de T-3 y de T-9), `guia_perfil.md`, `decisiones_diferidas.md`
  (Parte de T-9 renumerada a **XLVIII**, detrás de la XLVII de T-3). Los generados, la línea base, la
  guía y el tracker se tomaron de `main` y se regeneraron / reescribieron sobre el árbol fusionado.
- Pie del commit: el que la sesión indica como atribución vigente (mismo `Claude-Session`); ningún identificador de modelo en otro sitio.

## 2. Par de la suite (configuración «PyMuPDF sí · ventana Tk no»)

| Árbol | Con `NORMAS_DIR` | Sin `NORMAS_DIR` |
|---|---|---|
| final, antes del push | 5529 passed, 19 skipped | 5511 passed, 37 skipped |
| `origin/main` = `c654a16` (remedido tras el push) | **5529 passed, 19 skipped (collected 5548)** | — (mismo árbol) |

Base `6c25f1d`: 5336 / 16 / collected 5352. **+196 tests**, siete `pdf` (los `-m pdf` pasan de 105 a
112), ninguno de Tk ni del repositorio de normas; tres son saltos de DISEÑO nuevos en
`test_familias_del_csv` (la Familia B usa las tres claves nuevas). CLAUDE.md: «sí · no» MEDIDO;
las otras tres DERIVADAS: 5542/6, 5431/117, 5418/130.

## 3. IDs

| ID | Estado | Por qué |
|---|---|---|
| **INF-5.1.12** | **Cerrado (entero)** | La Fase 10 ya no cumple por construcción: 10.1 es un límite sin veredicto; VB1 juzga el tramo de cuneta de cada alivio contra min(200, L_hidráulica) y VB2 (H1) el caudal de aporte contra la capacidad de la cuneta (condición literal del Manual, pág. 177). Las dos pueden fallar y entran a la aceptación de la Familia B. |
| **INF-3.3.8** | **Cerrado (entero)** | La longitud por capacidad se calcula (Manning ec. 117, Tablas 32/33/34, sección de archivo [A]); la declarada gana. |
| **INF-5.1.8** | **En parte** | `area_ha` en B tiene consumidores reales (contraste Q/A de T-1; reparto q·b sin tramo, con aviso de la longitud implícita), pero con el tramo conocido ya no entra a L y nada comprueba que sea el área del tramo (ficha T9-07). |

Tracker (`matriz_cruzada_auditorias.xlsx`, Responsable «Claude Code (cadena T, T-9)»): INF-5.1.12 y
INF-3.3.8 «Cerrado», INF-5.1.8 «Cerrado parcial». `test_t0_gobernanza::LO_QUE_ESCRIBIO_CADA_PROMPT`
gana la fila de T-9.

## 4. Correcciones de la auditoría (PARTE 1, ya entregada en `INFORME_T-9_correcciones.md`)

H1 (ALTA, VB2) a H11 y las decisiones A–D del dueño: todas cerradas; detalle hallazgo por hallazgo en
`/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/INFORME_T-9_correcciones.md`.
Respuestas del orquestador aplicadas: (1) VB2 sin `S_cuneta` y con L declarado sigue como AVISO;
(2) la guía termina con la VB1 de B-01 NO CUMPLE y explica cómo se resuelve; (3) la región pluvial en
año FEN, la V.D. y el IMDA de la vía (y además el talud de corte y el inicio de cada tramo) están en
`docs/contrato_entradas.md` como entradas que el proyecto debe, con quién las debe.

## 5. Mutación (arnés de EXT-11, sobre una copia del árbol fusionado en el scratchpad)

- M10 (todas las funciones nuevas o tocadas): 240/288 → 261/288 → **262/288 (91.0 %)**.
- `servicio` (las seis funciones de la Fase 10): 66/78 → 77/78 → **78/78**.
- Cerrados con 21 tests `test_mut_*` en `tests/test_t9_correcciones.py`, entre ellos un defecto REAL:
  el extremo del tramo se resolvía también para obras A y C y enmascaraba un `solo` invertido; desde
  aquí sólo se resuelve para los alivios.
- Los 26 vivos de M10 censados en la ficha **T9-11** (10 banda de tolerancia/igualdad, 10 guardias
  `LimiteNumericoError` inalcanzables con datos válidos, 3 de presentación, 3 equivalentes).

## 6. Lo que se mueve (línea base medida con el comparador de E-B contra `6c25f1d`)

En los **cuatro** JSON (`expediente`, `familia_c`, `perfil_ancho`, `rama_error`): **8 diferencias, 0 no
comparables**, las mismas en los cuatro: `criterios_sha1`; en B-01 `tramo_alivio` (extremo A-02, 530 m),
`aporte_alivio` (VB2 sin evaluar: falta `S_cuneta`), VB1 evaluada y el texto del bloqueo de la Fase 10;
`long_max_cuneta` y `obras_familia_a_extremo_de_cuneta` entre los criterios usados;
`verificacion_pendiente` 28 → 29.

- **Diámetros / secciones / materiales movidos: ninguno.** El bloque `diseno` de los cuatro puntos es
  idéntico en los cuatro JSON (A-01 y A-02 Ø 0.90 m concreto donde dimensionan; C-01 marco
  1.20 × 0.90 m en la corrida 6; B-01 sin diseño, como antes).
- **Único veredicto que cambia: VB1 de B-01**, «no se evaluó» → **NO CUMPLE** (la obra A-02 cierra el
  tramo por la decisión C: 530 m > 200 m). «Verificaciones incumplidas» 0 → 1 en las cinco corridas de
  la CLI y en las dos de la guía, que salen con código 1 y explican cómo se resuelve (un alivio
  intermedio o el inicio del tramo declarado con su procedencia).
- Techos de EXT-8 remedidos: 109.7 → **113.96 KB** y 31.7 → **32.3 páginas** por punto (el bloque de
  B-01, que ahora evalúa la Fase 10); techos 114.5 / 33, pegados a la medida (los reconcilia T-10).

## 7. Censos

114 criterios (cuatro nuevos, todos con valor; siguen 27 sin valor), citas del registro 384 → 401,
`CLAVES_EXTERNAS` 21, `-m pdf` 112, dos marcas `literal-ok` nuevas (exponentes de Manning en M10).

## 8. Diferidos (fichas T9-01..T9-11, Parte XLVIII)

Sección trapezoidal para región > 3000 mm/año sin implementar (T9-01); `area_ha` no se comprueba
como área del tramo (T9-07); cuatro ecuaciones del ejemplo del Manual que no reproducen su geometría
(T9-04); pendiente de la cuneta como dato del trazo (T9-05); los 26 mutantes vivos (T9-11, para T-10).

## 9. Preguntas para el dueño

1. ¿Se mantiene `obras_familia_a_extremo_de_cuneta = si` (decisión C) como valor de archivo, sabiendo
   que deja la VB1 de B-01 en NO CUMPLE en todo el fixture hasta que el trazo dé el inicio del tramo?
2. ¿Quién entrega, y cuándo, las entradas que quedaron en el contrato (región pluvial FEN, V.D./IMDA,
   talud de corte, inicio de cada tramo)?
