# Informe FINAL de T-7a (cabezal: geometría por punto y aleros) — correcciones e integración

## 1. Resultado

- **`origin/main`: `250c972`** (fast-forward desde `c654a16`; `origin/main == HEAD` confirmado) — commit único `tesis(T-7a): cabezal — geometria por punto y aleros …
  — INF-5.1.15, INF-3.4.1, INF-3.4.2 (cerrados); INF-4.2, INF-4.3, INF-4.1 (en parte)`, rebasado
  sobre `c654a16` (T-3 y T-9). `tesis/T-7a` empujada en el mismo commit.
- **Par** (PyMuPDF sí · Tk no), suite entera sobre el árbol final:
  - con `NORMAS_DIR`: **5690 passed / 19 skipped / 5709 collected**;
  - sin `NORMAS_DIR`: **5672 passed / 37 skipped**.
  (Medidas sobre `3584cf0`; el commit aplastado `250c972` solo difiere en el sello de dos
  documentos generados, re-sellados con ese par y con sus tests de sincronía en verde.)
  Base `c654a16`: 5529 / 19 / 5548 (sin: 5511 / 37). Las otras tres configuraciones de la tabla de
  `CLAUDE.md` son DERIVADAS (+161 a las de T-9; ninguno de los 161 tiene marca `pdf`, depende de Tk ni
  abre el repositorio de normas).

## 2. IDs

| ID | Estado | Por qué |
|---|---|---|
| `INF-5.1.15` | **Cerrado** | Fase 9 por punto (`servicio._fase_9`, `M9.cabezal_del_punto`, `InformePunto.cabezal`); el proyecto guarda solo la suma; `geometria_adoptada` retirada. |
| `INF-3.4.1` | **Cerrado** | `predimensionamiento_cabezal` con trece reglas [A] y ventana; mínimos con número aparte; `GeometriaCabezal` completa con el origen de cada dimensión. |
| `INF-3.4.2` | **Cerrado** | `Aleros` y `predimensionar_aleros` (convención ΘW del HDS-5; dos longitudes con esviaje; alero largo declarable). |
| `INF-4.2` | **En parte** | Predimensionamiento, CB1–CB7, memoria, JSON y CLI. Residual: ninguna corrida de expediente alcanza la Fase 9 (V5: `remanso_derecho_via` + sin método; V8: TR y Q del evento extremo) — ficha T7A-01, lo cierra **T-7b** (decisión del dueño). |
| `INF-4.3` | **En parte** | Aleros, embocadura del punto y coherencia embocadura ↔ ke ↔ carta. Residual: el mismo de T7A-01 y el cabezal paralelo a la vía para el marco (Carta 11), diferido (T7A-03). |
| `INF-4.1` | **En parte** | Entran por punto sección, HW, tirante, cotas de 7.B, talud, esviaje y socavación. Residual: geotécnicos y sísmicos, T-7b. |

Tracker escrito (openpyxl, responsable «Claude Code (cadena T, T-7a)») y fila de T-7a en
`tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`.

## 3. Hallazgos de la auditoría (PARTE 1, detalle en `INFORME_T-7a_correcciones.md`)

H1 a H10 cerrados; dudosos 3, 4 y 5 cerrados (el 4 con el literal de E.060 15.7, pág. 138);
decisión 3 aplicada (aviso de caja receptora en la Familia B); decisión 4 NO aplicada (premisa
refutada, medida). Al integrar, las decisiones del dueño del 2026-11-13:
(1) cabezal **normal al eje** por defecto en las tres familias; el paralelo a la vía diferido solo
para el marco (ficha T7A-03, «a un paso posterior a T-7c»), y el alero largo se acorta declarando
`cabezal_declarado.angulo_alero_largo_grados` (nuevo: validado en [0, 90), guardia
`LimiteNumericoError` propia, dimensión «declarada», longitudes «derivadas», y en un marco un aviso
de que el ke y la carta siguen con el α de la regla; 8 tests); (2) T7A-01 nombra a T-7b; (3) E.060
22.7.4 queda [N] y la ficha T7A-04 dice que lo resuelve T-7c.

## 4. Tests nuevos (+161 netos sobre `c654a16`)

- `tests/test_t7a_cabezal_geometria.py`: 67 (FASE A; 12 reescritos declarándolo — 11 en las
  correcciones y 1 al integrar: la coherencia del marco con los valores de archivo de T-3).
- `tests/test_t7a_correcciones.py`: 84 (61 primera tanda, 15 contra los mutantes vivos, 8 de la
  integración).
- `test_decisiones_diferidas` +8 (T7A-01..08), `test_ext5_forma_gui` +5 (criterios nuevos);
  `test_M9_cabezal` −1, `test_criterios_adoptados` −2 (los dos vacíos que dejan de serlo).
- Rojo medido (no `xfail`): FASE A 63 F + 3 E de 66 contra `df1b23c`; correcciones 47 rojos / 14
  verdes (guardias) de 61 contra `1b83d39`. Mutación (arnés de EXT-11, 17 funciones): 185/226 →
  309/326, +1 a mano.

## 5. Movido y por qué

- **Diámetros, secciones, materiales y HW movidos: ninguno.** Bloque `diseno` idéntico al de
  `c654a16` en los cuatro JSON de la línea base (comparado entero); C-01 sigue en marco 1.20 × 0.90
  con el HW de T-3 en la corrida de la Familia C.
- Línea base (comparador de E-B contra `c654a16`, README): huellas; criterios usados y recuentos
  (114/27 → 119/25; verificación pendiente 29 → 30; sin consumidor 9 → 8); bloque `cabezal` del
  proyecto (`geometria` → `por_punto`; sale el bloqueo de `predimensionamiento_cabezal`, «Etapas
  bloqueadas» 11 → 10 en `cli_expediente.txt`); embocadura por punto; `proteccion_entrada` de los
  puntos dimensionados `cabezal_recto` → `cabezal_con_aleros` (incluido C-01 en la corrida de la
  Familia C); aviso de la caja receptora en B-01.
- Techos de `test_ext8` remedidos sobre el árbol fusionado: 113.96 KB y 32.3 páginas por punto,
  sin cambio.
- Censos: 119 criterios / 25 sin valor; citas 401 → 412; `CLAVES_EXTERNAS` 21; `dominios.py` 12
  marcas `literal-ok`.

## 6. Diferidos (con símbolo)

T7A-01 (`servicio._fase_9`: Fase 9 inalcanzable a expediente → T-7b); T7A-02 (caja receptora no
modelada); T7A-03 (`M9.predimensionar_aleros`: cabezal paralelo a la vía para el marco, Carta 11);
T7A-04 (`predimensionamiento_cabezal`: «más material» no es el lado seguro, umbral del ciclópeo
inalcanzable, VARIOS no verificado, E.060 22.7.4 → T-7c); T7A-05 (lectura de AASHTO 12.6.5);
T7A-06 (longitud entre cabezales no sustituye a la del diseño); T7A-07 (aceptación escrita
después del código; mutación); T7A-08 (E.050 y E.060 15.7 [N→]; defecto de la §0.1 y §9.3 de la
hoja, que corrige T-7b). Parte XLIX de `docs/decisiones_diferidas.md`.

## 7. Preguntas para el dueño

Ninguna nueva. Para T-7b quedan escritas: verificar HDS-5 núm. 5.4.2 (embocaduras esviadas) antes
de la ficha del paralelo; el acoplamiento con `orientacion_muro_respecto_al_trafico`; corregir el
rótulo E.050 [N] de la §0.1 y §9.3 de la v8.

## 8. Lo que NO hice

- No medí las configuraciones con Tk ni sin PyMuPDF (derivadas, como en T-0).
- No cambié el umbral de 2.0 m del ciclópeo ni subí a 0.3048 m el relleno sobre la clave.
- No implementé la caja receptora ni el cabezal paralelo a la vía (diferidos).
