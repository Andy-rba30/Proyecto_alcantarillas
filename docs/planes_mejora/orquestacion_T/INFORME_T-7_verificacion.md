# INFORME — correcciones de la verificación de fórmulas de los cierres de T-7b y T-7c

Rama `tesis/T-7-verificacion` (worktree `/home/user/wt/T-7v`), base `origin/main` = `2b13dc1`.
Un commit en `origin/main`: `tesis(T-7): verificacion de formulas de los cierres de T-7b y T-7c — …`
SHA en `origin/main`: `2265d9098d74a45bb857dc25c9984bf438c73b15` (`origin/main == HEAD`, fast-forward desde `2b13dc1`; la rama `tesis/T-7-verificacion` apunta al mismo commit). El par se midió sobre ese mismo árbol antes de aplastar los commits `wip`.

## Pares

| | passed | skipped | collected |
|---|---|---|---|
| con `NORMAS_DIR` (medido, «sí · no») | 6287 | 23 | 6310 |
| sin `NORMAS_DIR` (medido, mismo árbol) | 6269 | 41 | 6310 |

+34 tests: 28 de `tests/test_t7_verificacion.py`, 4 anclajes de fichas (T7V-01..04) y 2 de
`test_ext5_forma_gui` (dos criterios nuevos). Rojo medido con el archivo final contra `2b13dc1`:
26 rojos y 2 guardias. No se corrió mutación.

## Punto 3 — V8 con el barril «a presión» (MEDIA, lado inseguro): CERRADO

- `M4.hidraulica_a_presion` calcula el perfil de la lámina (`perfil_lamina` no necesita tirante
  normal) y gobierna con él, igual que `resolver_control` desde E-A: bajo 1.2 D la carga de
  salida es la mayor de la aproximación y del remanso, con aviso; bajo 0.75 D la aproximación no
  se usa y rige el remanso, con aviso.
- **Decisión bajo 0.75 D: aviso expreso, no `MetodoNoEvaluableError`.** HDS-5 pág. 3.24 dice
  «the approximate method should not be used»; la misma fuente dice qué hacer (pág. 3.12, cálculo
  de remanso desde la salida) y M4 lo tiene. Es la misma decisión de E-A en lámina libre.
- `M5.v8_evento_extremo`: guardia HW_ext ≥ HW de diseño; si no, juzga con la de diseño y avisa.
  El aviso viaja por un campo nuevo, `Verificacion.avisos`, que `InformePunto.avisos()` recoge.
- Control (tubo de A-01, S 0.003, L 60 m, TW 0): HW_ext(1.0213) 0.9570 → **0.9890 m** ≥ 0.9654 m.
  A-01 del fixture no cambia: 1.5880 m, 43.69 msnm (gobierna la entrada).
- **Hallazgo nuevo, medido y NO corregido (ficha T7V-01):** la regla de E-A tiene un escalón
  propio donde la aproximación cruza HW/D = 1.2. Tubo de A-01, S 0.006, L 18.869 m, TW 0.5 m,
  los dos caudales en lámina libre: 1.1507 m con 1.276 m³/s y 1.1394 m con 1.290 m³/s (11 mm
  menos con más caudal). Es de `M4.resolver_control` (punto conforme): no se tocó. Para V8 lo
  cubre la guardia; para el caudal de diseño queda como está.

## Punto 9 — η de AASHTO 1.3.2.1 en el cabezal (MEDIA): CERRADO; cierra la ficha T7C-11

- `M9.modificador_de_carga` + `M9._resistencia_i_con_eta`, usados por
  `M9.combinaciones_de_estabilidad` y `M9._combinaciones_en_reposo`: η en las cargas de γ
  máximo (≥ 0.95), 1/η en DC y EV de la combinación de mínimos (≤ 1.0), 1.00 en Evento Extremo I
  y en Servicio. Rige en estabilidad LRFD y en armado; ASD (E.050) y contraste E.060, sin η.
- **η_I: el mismo criterio del conducto** (`eta_importancia_operativa_conducto` [A] = 1.05); no
  se duplicó el número; el concepto y la justificación dicen ahora que rige el cruce (la clave
  conserva el nombre). **η_D y η_R: dos criterios [A] nuevos** (`eta_ductilidad_cabezal`,
  `eta_redundancia_cabezal`, 1.00, ventana 0.95–1.05). Se separan del conducto porque la fuente
  obliga: el 1.00 del conducto sale de 12.5.4 (estructuras enterradas).
- Literales verificados en el PDF: 1.3.2.1 (PDF 18), 1.3.3 (PDF 20, no 21: «1.00 for
  conventional designs and details complying with these Specifications»), 1.3.4 (PDF 21, cierra
  en la 22), 1.3.5 (PDF 22). Tres citas nuevas (503 → 506).
- Lectura del proyecto, declarada como `Interpretacion`: WA y LS (factor único) van con η de γ
  máximo en las dos combinaciones.
- Paso de memoria: `F9.COMBINACIONES` y `F9.ARM_REGIMEN` imprimen η_D, η_R, η_I y los dos η_i con
  sus citas; en la condición sísmica, la nota dice 1.00.
- Control: con η solo (zapata de 0.37 m) se reprodujeron exactas las cifras de la ficha T7C-11 y
  el talón de salida 71.72 → 75.31 kN·m/m → Ø 1/2" @ 0.15, antes de tocar la zapata.
- En el muro de tanteo η **cambia el veredicto** de E3-LRFD estática: 37.177 > 37.156 kN/m (con
  1.00, 35.407 ≤ 38.607). A mano en `CP_T7V_ETA`.

## Punto 7 — piso de la zapata armada (BAJA): CERRADO

- `M9.peralte_minimo_zapata` (voladizo): 0.30 + recubrimiento de `recubrimiento_para_armar` +
  medio diámetro de la MAYOR barra del catálogo (Ø 1" → 12.7 mm), sin redondeo: **0.40414 m** con
  la cota de 91.44 mm; 0.3827 m con 70 mm (categoría y análisis químico declarados).
- A8 cumple por construcción con cualquier barra del catálogo en un cabezal de regla; sigue
  fallando con una zapata declarada más delgada (probado con 0.37 m: 0.2722 m).
- A8 imprime las tres lecturas (eje —la que usa—, cara inferior, cara superior) y la nota ya no
  dice que baste bajar el recubrimiento. La lectura a la cara superior NO queda garantizada
  (0.3000 m exactos con Ø 1/2"; 0.2968 m con Ø 5/8"): se imprime y no decide.

## Matiz del punto 2

La nota de V5 por cota de afectación dice «el nivel del agua EN LA BOCA» y que es el más alto
solo con el embalse a nivel.

## A-01 con los datos de prueba (sin categoría del acero ni análisis químico)

Zapata de los dos cabezales: 0.37 → 0.40414 m. Sección Ø 0.90 m, concreto, HW 1.042002 m: idénticos.

| Fila | antes | después | veredicto |
|---|---|---|---|
| E1-LRFD.est.e | 67.52 ≤ 87.41 | 73.41 ≤ 86.72 | cumple |
| E2-LRFD.est.e | 0.352 ≤ 0.525 | 0.396 ≤ 0.525 | cumple |
| E3-LRFD.est.e | 38.05 > 29.39 | 39.95 > 28.70 | NO cumple |
| E1-LRFD.sis.e | 80.26 > 52.94 | 80.86 > 54.11 | NO cumple |
| E2-LRFD.sis.e | 0.392 ≤ 0.578 | 0.391 ≤ 0.578 | cumple |
| E3-LRFD.sis.e | 38.82 ≤ 39.68 | 38.89 ≤ 40.04 | cumple |
| E1-LRFD.est.s | 81.85 ≤ 100.81 | 78.17 ≤ 91.57 | cumple |
| E2-LRFD.est.s | 0.362 ≤ 0.685 | 0.415 ≤ 0.685 | cumple |
| E3-LRFD.est.s | 57.93 > 49.13 | 60.83 > 47.90 | NO cumple |
| E1-LRFD.sis.s | 97.13 > 56.22 | 97.73 > 57.16 | NO cumple |
| E2-LRFD.sis.s | 0.488 ≤ 0.754 | 0.487 ≤ 0.754 | cumple |
| E3-LRFD.sis.s | 62.79 ≤ 65.58 | 62.89 ≤ 66.07 | cumple |

Ningún veredicto cambia. A8: 0.2722 m (no cumple) → 0.3064 m (cumple), los dos cabezales.

| Armado | antes (M_u kN·m/m, barra) | después |
|---|---|---|
| entrada pantalla | 59.34 · Ø 1/2" @ 0.175 | 57.49 · Ø 1/2" @ 0.175 |
| entrada punta | 38.39 · Ø 1/2" @ 0.25 | 38.35 · Ø 1/2" @ 0.25 |
| entrada talón | 28.69 · Ø 1/2" @ 0.25 | 30.19 · Ø 1/2" @ 0.25 |
| salida pantalla | 138.08 · Ø 5/8" @ 0.10 | 134.99 · Ø 5/8" @ 0.10 |
| salida punta | 83.51 · Ø 1/2" @ 0.15 | 83.41 · Ø 1/2" @ 0.175 |
| salida talón | 71.72 · Ø 1/2" @ 0.175 | 75.45 · Ø 1/2" @ 0.15 |

Con la zapata declarada de 3.00 m de ancho (test de T-7b): las 24 filas cumplen (el
deslizamiento ASD sísmico de salida pasa de FS 1.2489, indicador, a 1.2517).

## Línea base

Regenerada y medida contra `2b13dc1` con el comparador de E-B: 1 diferencia en cada uno de los
cuatro JSON (`criterios_sha1`), 0 no comparables; en las tres memorias, las dos huellas y
«139 … 20» → «141 … 20». Ninguna corrida de la línea base alcanza V8 ni la Fase 9.
**Diámetros, secciones, materiales y HW movidos: ninguno.**

## Ritual

Fichas Parte LII (T7V-01..04); T7C-11 cerrada; T7B-02, T7A-08 y T7C-13 al día. Hoja de ruta v8:
dos notas «Corregido» (fila V8 y §9.4). `docs/contrato_entradas.md`: A8 y los tres η. Tracker:
NOTA en `INF-4.2`, `INF-4.5`, `INF-4.6` (responsable añadido; ningún estado cambia; sin fila nueva
en `LO_QUE_ESCRIBIO_CADA_PROMPT`, el test no la exige). Manifiesto, registro y `trazabilidad.csv`
resellados con el par; `indice_formulas.md` ya estaba sincronizado. `CLAUDE.md`: párrafo, censos
(141 criterios, 20 sin valor; 506 citas), tabla de pares, cadena de totales.

## Lo que NO hice

1. **No rehíce uno a uno los ~22 dorados del muro de tanteo de T-7b y T-7c.** Se calcularon con
   los factores de la tabla (η = 1.00); el fixture `tanteo` de los dos archivos declara ahora
   η_I = 1.00 (dentro de la ventana), dicho en su docstring, y el efecto de η con el 1.05 de
   archivo lo fija a mano un dorado nuevo (`CP_T7V_ETA`: las dos combinaciones, E1–E3 y la
   pantalla en reposo). Los tests de A-01 sí se reescribieron con las cifras nuevas.
2. Los dorados de A-01 son lectura de la corrida con la aritmética a mano de E3 estática (dos
   cabezales) y del talón de salida sobre las cargas sin factorar; las otras filas no se
   recalcularon a mano.
3. No corregí el escalón de la regla de E-A en HW/D = 1.2 (arriba).
4. No corrí mutación. No barrí otras secciones ni el marco para el punto 3.
5. No medí las tres configuraciones con Tk o sin PyMuPDF: derivadas.
6. No toqué `M4.resolver_control`, la cuña de tanteo ni ningún punto conforme.
7. Durante las medidas ejecuté dos scripts de lectura contra `/home/user/wt/main` (sólo importan
   y corren; pueden haber dejado `__pycache__` ignorados por git). No edité nada ahí.
