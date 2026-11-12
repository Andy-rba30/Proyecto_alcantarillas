# Informe de FASE A — T-3 · Familia C: el marco de concreto se dimensiona

Rama `tesis/T-3` (worktree `/home/user/wt/T-3`), base `origin/main` = `df1b23c`.
Commits en la rama (todos empujados a `origin/tesis/T-3`): `aa3e20f` (aceptación en rojo),
`e94ae8f`, `0ab0ea5`, `8fe4b74`, `f2ee7cd`, `255c97a` (último). **No se fusionó a `main`.**
No se tocó el `.xlsx` del tracker, la tabla de conteos de `CLAUDE.md` ni `verificar_sesion.py`.

## 1. IDs

| ID | Estado propuesto | Por qué |
|---|---|---|
| **INF-0.4** (§0 punto 4, «Familia C no se dimensiona»; alias de la cadena «INF-3.x») | **Cerrado**, con la PARADA (c) de la progresión abierta | Los siete criterios del marco tienen valor de archivo con fila nombrada, cita y ventana; con los datos del canal C-01 sale **marco 1.20 × 0.90 m** sin declarar nada (guía: control de entrada, HW 0.589 m; corrida 6 de la línea base: control de salida, HW 0.623 m). VC2 y el remanso del canal implementados como aviso; geometría del marco en `modelos.GeometriaMarco`/M7. El valor de `secciones_cajon_normalizadas` es provisional (ver §6) |
| **INF-3.2.1** (Manning; mitad del cajón) | **Cerrado** (T-4 cerró la del HDPE) | `n_manning_cajon` = `concreto_afinado` (0.011, 0.014), Tabla N° 09 leída con el corrimiento corregido (`DIS-MCHHD-T09-A2-DESPLAZADA`), [N→], `vacio_verificado` |
| **INF-0.5** (criterios vacíos, cluster C19) | **En parte** (la parte de T-3) | Los siete del cajón salen de los vacíos: `criterios_sin_valor()` pasa de 35 a 28; de perfil sin valor quedan dos (`TW_receptor`, `homogeneidad_serie_fen`) |

Filas del tracker a escribir en FASE B (hoja `Hallazgos`, columnas Estado / Responsable / Commit):
- `INF-0.4` → «Cerrado (T-3; progresión de secciones pendiente del dueño, ficha T3-01)» · «Claude Code (cadena T, T-3)» · SHA del commit de integración.
- `INF-3.2.1` → «Cerrado» (la mitad del cajón por T-3; la del HDPE la cerró T-4) · ídem.
- `INF-0.5` → sigue «Abierto», nota: «T-3: los siete del cajón con valor de archivo (35 → 28 sin valor)».
- `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`: añadir la fila de T-3 (INF-0.4 cerrado, INF-3.2.1 cerrado, INF-0.5 en parte) al integrar.

## 2. Lo que se hizo, por punto del prompt

**Punto 1 · los siete del cajón con valor de archivo** (`src/criterios_adoptados.py`, en su sitio):

| Criterio | Valor | Etiqueta | Fuente verificada contra el PDF |
|---|---|---|---|
| `n_manning_cajon` | `concreto_afinado` → (0.011, 0.014) | [N→] | MTC Tabla N° 09, impresas 75-76 (PDF 78): la fila «afinado» leída por coordenadas; los valores impresos en su línea (0.013/0.015/0.017) son los de la fila siguiente; corregidos, 0.011/0.012/0.014 |
| `embocadura_cajon` | `cajon_concreto_aletas_30_75` | [A] | HDS-5 Tabla A.1, PDF 197: Carta 8, escala 1, «30° to 75° wingwall flares», Forma 1, K 0.026, M 1.0, c 0.0347, Y 0.81 |
| `ke_entrada_cajon` | `cajon_aletas_30_75_escuadra` → 0.4 | [C] | HDS-5 Tabla C.2, pág. impresa C.6 (PDF 216): «Square-edged at crown» bajo «Wingwalls at 30° to 75° to barrel» |
| `n_celdas_cajon` | 1 | [A] | MTC 4.1.1.3.4 a), impresa 72 (PDF 75): recomienda sección libre sin subdivisiones ante arrastre |
| `secciones_cajon_normalizadas` | ((1.20, 0.90), (1.50, 1.20), (2.00, 1.50)) | [A] | provisional: ver §6 (PARADA (c)) |
| `espesor_pared_cajon` | 0.20 m | [A] | E.060 num. 14.5.3.2, pág. 134 (PDF 134): «El espesor de los muros exteriores de sótanos y cimentaciones no debe ser menor que 200 mm.» — POR ANALOGÍA (rige el método empírico de 14.5) |
| `cobertura_minima_cajon` | 0.3048 m | [A] | AASHTO LRFD 9.ª Tabla 12.6.6.3-1, impresa 12-22 (PDF 1660), fila «Reinforced Concrete Pipe … > 12.0 in.» POR ANALOGÍA rotulada (12.0 × 0.0254 = 0.3048) |

Cuatro llevan `vacio_verificado` (secciones → ruta §15.3.1, n_manning → §15.3.2, espesor → §14.1,
cobertura → §16.12): con valor de archivo el campo se puede poner y salen por
`bloque_acotaciones` (cierra el R-23 de la ruta de la Familia C).

Cuatro citas nuevas, verificadas por `test_normativa_pdf` contra su página
(`src/normativa/citas.py`, bloque «--- T-3 ---», firma `tesis/T-3 · lectura directa`):
`MC_HHD.4.1.1.3.4a#SEPARACION` (impresa 72 / PDF 75, RECOMENDACION), `E060.14.5.3.2`
(134/134), `EG2013.503.11g#COTAS` («Cotas superiores de placas y veredas: -10 mm a +10 mm.»,
impresa 934 / PDF 942) y `EG2013.501.07` («… más de 2 cm en cota …», impresa 889 / PDF 897).

**Punto 2 · VC1, VC2 y el remanso.** VC1 sin cambio. **VC2** (`M7.vc2_empalme_canal`, sólo
Familia C, detrás de G2): |cota_salida − cota_fondo_receptor| ≤ `desajuste_empalme_canal_m`
[A] = 0.010 m (ventana 0.010–0.020, analogía con EG-2013 503.11 g) y 501.07); veredicto
INDICADOR (cuenta en «Verificaciones con aviso», sale en `InformePunto.avisos()`, CLI, JSON y
memoria); segunda línea MAT-D13 sobre la tolerancia. **Remanso** (`M7.remanso_canal`, aviso
y paso 7.B.R): con `seccion_receptor_medida` → y_n del canal por Manning, dh = HW − y_n,
L_min = dh/S (cota inferior: el M1 real llega más lejos); sin ella → «no se evaluó» con aviso
(no cae a la sección adoptada del dren). Fundamentos nuevos `F7.MARCO`, `F7.EMPALME_CANAL`,
`F7.REMANSO_CANAL` (verbo DEFINE).

**Punto 3 · la geometría del marco.** `modelos.GeometriaMarco` + `M7.geometria_marco` (paso
7.B.M): B, H, N, t (uno para paredes, losas y tabique), tabique, ancho N·B + (N−1)·t + 2t
(`SeccionRectangular.ancho_exterior_de_celdas`, una sola cuenta para M7 y V6), canto H + 2t,
cotas de fondo, clave interior, clave exterior (= `M5.cota_clave`) y base, relleno sobre la
losa. Viaja en `CompatibilidadGeometrica.geometria_marco` y en el JSON
(`geometria.geometria_marco`, `geometria.remanso_canal`) y una línea en la CLI. **M8 no se
tocó** (T-5 lee `Seccion` y `espesor_pared`, que no cambian). 7.A, G1 y G2 corren para C-01
del fixture con los datos del canal: test `test_C01_dimensiona_con_los_valores_de_archivo` y
corrida 6 de la línea base (CSV del fixture + coronación 38.30 en una copia; Q, S por
`--datos-externos`). La coronación es columna del CSV y NO se añadió como clave externa.

**V6 con N > 1:** publica Q/N, el tabique y el ancho total y **sigue sin aceptar** la multicelda
(ficha EXT-2-01); la separación del MTC 4.1.1.3.4 a) es de tuberías (relleno compactado entre
tubos) y la fila dice por qué no la aplica a un marco monolítico.

**Punto 4 · línea base** regenerada (ver §4).

**Otros:** `M2._pasos_del_marco` guarda la progresión como TUPLA: con lista, la
`EleccionDeProyecto` congelada no se podía hashear y `M11.pasos_del_informe` tumbaba la
memoria en cuanto un marco dimensionaba sin declarar nada (defecto latente medido por un test
de T-4). Nota «Ampliado (T-3)» en la Sec. 2.3 de la v8. `docs/guia_perfil.md` reescrita al
contrato nuevo (los siete del cajón ya no se declaran; la corrida sin declarar dimensiona los
cuatro; tabla generada regenerada). `docs/contrato_entradas.md`, `docs/ruta_familia_c.md`
§16.21, `docs/decisiones_diferidas.md` Parte XLVI provisional (T3-01..T3-07). Techos de
`tests/test_ext8_*` remedidos (70.3 → 108.7 KB y 20.7 → 31.7 páginas por punto: C-01 pasa de
21 a 96 KB de bloque al llegar a VC1; los otros tres no cambian), pegados a la medida.

## 3. Tests y par de la suite

- **Nuevo:** `tests/test_t3_familia_c.py`, **45 tests**. Los 41 primeros se escribieron en
  ROJO con `xfail(strict=True)` y se midieron contra `df1b23c`: **38 xfailed, 3 passed**
  (las tres invariantes, nombradas `..._invariante`), commit `aa3e20f`; liberados al
  implementar. Los 4 últimos (guardia de la pendiente del canal, ancho de N celdas,
  tabique con N = 2, sin geometría de marco para un tubo) se escribieron DESPUÉS del código,
  en la auditoría propia: no pasaron por rojo.
- **Crecen solos:** 7 anclajes de `test_decisiones_diferidas` (T3-01..07) y los
  parametrizados por criterio con el criterio nuevo `desajuste_empalme_canal_m`.
- **Reescritos al contrato nuevo (premisa «criterio del cajón sin valor» recreada con
  `sin_valor(...)` durante el test, sin perder lo que medían):** `test_cli` (3),
  `test_cierre_perfil` (2), `test_M2_material` (2), `test_MD`, `test_M4_control`,
  `test_cierre_c10`, `test_eb_editores_comparador`, `test_pf3_barrido`,
  `test_criterios_adoptados`, `test_t2_hidraulica`, `test_pf2_prevuelo` (SOBRA_CON_TODO = {}),
  `test_memoria_sustentada` (tres F7 nuevos en el censo de inalcanzables de la corrida por
  defecto), `test_linea_base` (eje (f) nuevo), `test_guia_perfil`, `test_ext8_rendimiento_gui`
  (techos). Ningún test se borró.
- **Par medido** sobre el commit `255c97a` de la rama, configuración «PyMuPDF sí · ventana Tk
  no», con `NORMAS_DIR`: **4999 passed / 16 skipped / 5015 collected** (+39 sobre la base: 45 de `test_t3_familia_c`, 7 anclajes T3-01..07, los parametrizados del criterio nuevo, menos los casos de los siete criterios del cajón que salen de los parametrizados de «sin valor»). Base `df1b23c`: 4960 / 16 / 4976.

## 4. Línea base: qué se movió (medido con el comparador de E-B contra `df1b23c`)

**Diámetros movidos: ninguno.** A-01 y A-02 siguen en Ø 0.90 m de concreto; B-01 no
dimensiona como antes; el bloque `diseno` de los tres es idéntico en los cuatro JSON. En la
guía de perfil C-01 sigue en **marco 1.20 × 0.90 m, HW 0.589 m** (la corrida que lo declaraba
todo en caliente da el mismo diseño con los valores de archivo: test
`test_los_valores_de_archivo_reproducen_la_corrida_declarada_en_caliente`).

Movimientos declarados (README de la línea base, entrada T-3):
- **Corrida 6 nueva** (`cli_familia_c.txt`, `informe_familia_c.json`): C-01 pasa de bloqueado
  en `embocadura_cajon` (medido con el código de `df1b23c` sobre el mismo CSV) a
  **dimensionado: marco 1.20 × 0.90 m, control de salida, HW = 0.623 m**, V2b aviso
  (S_conducto 0.004 < S_cauce 0.006), VC2 aviso +0.614 m, geometría exterior 1.60 × 1.30 m,
  clave exterior 38.000 msnm, relleno sobre la losa 0.950 m.
- **Corridas ancha y de expediente:** el bloqueo de C-01 pasa de `CriterioPendienteError`
  (`embocadura_cajon`) a `DatoFaltanteError` (`cota_coronacion_canal`, que VC1 exige y la
  fila deja vacía); claves `geometria_marco`/`remanso_canal` en el JSON (null para tubos);
  criterios usados; 35 → 28 sin valor.
- **Memorias:** `criterios_sha1`, `hoja_ruta_sha1` (nota de la Sec. 2.3), «102/35» → «103/28»,
  fichas del cajón y bloque de acotaciones. `memoria_punto_cajon.html`: una línea (la
  progresión impresa como tupla). Sin cambio: `cli_perfil.txt`, `cli_rama_error.txt`, los dos
  CSV de resumen.
- **Guía de perfil:** la corrida sin declarar pasa de 3 a 4 puntos dimensionados, «Etapas
  bloqueadas» 1 → 0, «Diferidas por alcance» 11 → 13, «Expediente cerrado» no → sí; las dos
  corridas suman «Verificaciones con aviso: 1» (VC2 de C-01, +0.571 m: la cota de entrada es
  la del terreno, 36.90, y el fondo del canal aguas abajo está a 36.20).

## 5. Diferido, con símbolo (fichas provisionales T3-01..T3-07)

- T3-01 `criterios_adoptados.py::secciones_cajon_normalizadas` — la progresión de la cadena T (PARADA).
- T3-02 `::embocadura_cajon` — aletas 30–75 (la de hoy) frente a cabezal recto (HW 0.589 vs 0.629); T-7a cierra la coherencia carta↔ke↔aleros.
- T3-03 `M7_geometria.py::vc2_empalme_canal` — tolerancia por analogía; aviso y no bloqueo.
- T3-04 `M7_geometria.py::remanso_canal` — cota inferior dh/S; perfil paso a paso pendiente.
- T3-05 `M5_verificaciones.py::v6_material_solido_arrastre` — multicelda sigue rechazada; falta dato de arrastre; V7 por celda.
- T3-06 `modelos.py::GeometriaMarco` — un solo espesor; M8 es de T-5.
- T3-07 `M4_control.py::ke_declarado` — con la embocadura del cajón declarada, R4 ya no frena una fila de cajón para el ke del TUBO al declarar; la frena el consumidor al correr.

Criterios que siguen sin valor y bloquean en la Familia C: ninguno del cajón. El punto se
detiene ahora por DATOS: `Q_m3s`, `S_cauce` (o `S_conducto`) y `cota_coronacion_canal`.

## 6. PARADAS para el dueño

**PARADA (c) — la progresión de secciones del marco.**
- La cadena T pide anchos 1.00–4.00 m (paso 0.50) × alturas 1.00–3.00 m (paso 0.25). Medido
  sobre C-01 de la guía (por área creciente, 63 pares): **C-01 deja de dimensionar** —siete
  escalones incumplen V7 (flotación: con H ≥ 1.00 m el relleno sobre la losa no basta bajo la
  rasante 38.95) y el octavo (1.00 × 2.00) deja la clave 0.15 m sobre la subrasante y detiene
  el material—. Hoy C-01 es marco 1.20 × 0.90 (HW 0.589).
- Opciones: (a) **la de C7/la guía**, ((1.20, 0.90), (1.50, 1.20), (2.00, 1.50)), hoy en el
  archivo como [A] provisional: no mueve nada, arranca en H = 0.90 m (la sección mínima de
  mantenimiento del 4.1.1.3.4 a), por analogía) y se agota en 2.00 × 1.50; (b) la de la cadena
  T (C-01 no factible con estas cotas); (c) una tercera (por ejemplo la de la cadena T con
  alturas desde 0.90 m).
- Recomendación: (a) mientras no haya sección del canal; con el ancho de solera del canal
  (ANA/Junta) declarar una progresión que lo siga.

**Pregunta (no parada) — la embocadura del marco.** Se dejó la de aletas 30–75 (la de hoy);
la de cabezal recto sube HW 0.040 m en C-01. Lo decide T-7a con el cabezal por punto.

**Pregunta — VC2 como aviso.** La tolerancia (0.010 m) es analogía con EG-2013 503.11 g); si el
dueño quiere que VC2 detenga el punto, necesita una tolerancia del proyecto del canal y
aceptar que C-01 del fixture deje de dimensionar hasta medir su cota de entrada.

## 7. Lo que NO se hizo, dicho sin adornos

- No se adoptó la progresión de la cadena T (PARADA (c)).
- No se adoptó «square edge headwall 90°» como embocadura del marco (precisión del orquestador).
- La separación entre celdas del MTC 4.1.1.3.4 a) no se aplica: es de tuberías; V6 la nombra.
- La multicelda no se acepta (V6 sigue en no cumple con N > 1; EXT-2-01).
- El remanso es una cota inferior, no un perfil paso a paso.
- `cota_coronacion_canal` no se añadió como clave de `--datos-externos`: la corrida 6 de la
  línea base y el test usan una copia del CSV con la celda rellena, como la guía.
- No se tocó M8 (T-5), el tracker, la tabla de CLAUDE.md ni `verificar_sesion.py`.
- Los documentos generados se regeneraron con el par de la base en el sello («4960 passed,
  16 skipped»): hay que resellarlos al integrar.
