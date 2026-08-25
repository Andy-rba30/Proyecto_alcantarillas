# Manifiesto de citas normativas

Inventario de **toda afirmación normativa que el software hace hoy**, extraída
de `src/constantes_normativas.py`, `src/criterios_adoptados.py`,
`src/datos_sitio.py` y los docstrings de `src/modulos/*.py`.

> **Regenerado** tras la incorporación de la quinta etiqueta `[S]` (dato de
> sitio) y las cuatro correcciones de clasificación de
> [manifiesto_datos_proyecto_vs_constantes.md](manifiesto_datos_proyecto_vs_constantes.md).
> Cambia **dónde vive y con qué etiqueta se declara** cada afirmación; no
> cambia ninguna afirmación normativa ni ningún valor, y no verifica ninguna
> cita nueva. Las filas afectadas llevan la marca **↻**.
>
> **Segunda regeneración** (esta revisión), tras: (1) actualizar la fuente
> normativa a `docs/hoja_de_ruta_alcantarillas_v8.md` (la v7 ya no existe en
> el repo); (2) cerrar el numeral de `COMPACTACION_CORONA`/`COMPACTACION_CUERPO`
> (Manual de Suelos num. 3.2.1, 3.2.2, 3.3 y 9.1(1)) y de
> `CALICATAS_POR_KM`/`ESPACIAMIENTO_PERFIL_KM` (Manual de Suelos num. 4.2,
> Cuadro 4.1); (3) separar la gravedad genérica de la de Laushey —
> `G_LAUSHEY = 9.8` (num. 4.1.1.3.7 c), uso exclusivo de M6) queda en
> `constantes_normativas.py`, y la gravedad física universal se movió a
> `src/constantes_fisicas.py` (`G = 9.81`), resolviendo la inconsistencia
> silenciosa entre `G = 9.8` y el `g = 9.81` implícito en `GAMMA_AGUA_KN_M3`.
> Esta última **sí cambia un valor calculado**: la constante de gravedad que
> usan el control de salida y el tirante crítico de M4 pasa de 9.8 a 9.81
> (los tres casos patrón CP-8 se recalcularon; CP-4/Laushey no cambia, sigue
> en 9.8). Las filas afectadas por esta segunda pasada llevan la marca **⟳**.

## Qué es y qué no es este documento

- **Es** un volcado literal de lo que el código YA afirma. Cada fila dice: qué
  valor usa el programa, qué numeral invoca para justificarlo, a qué documento
  atribuye ese numeral, y dónde está escrito en el repositorio.
- **No es** una verificación. Ningún PDF fue abierto para producirlo. Que una
  fila exista aquí no significa que el numeral sea correcto, ni que exista, ni
  que diga lo que el código dice que dice. Eso es exactamente lo que queda por
  comprobar.
- **Orden**: por documento fuente, para que cada bloque se pueda contrastar
  contra su PDF en una sola sesión de NotebookLM.
- **Etiquetas** (cinco desde esta revisión): `[N]` normativo verificado ·
  `[N→]` normativo por analogía · `[S]` **dato de sitio**: procedimiento
  normativo real (mapa, ensayo, medición) aplicado a las coordenadas o
  condiciones de ESTE proyecto, con trazabilidad obligatoria en vez de
  sensibilidad · `[C]` vacío cubierto con fuente técnica reconocida ·
  `[A]` adopción declarada sin norma.
- **Qué le cambia `[S]` a esta verificación.** Una fila `[S]` sigue teniendo
  numeral que comprobar —el mapa y la tabla son normativos—, pero comprobar el
  numeral **no basta**: hay que comprobar además que la lectura se hizo sobre
  la ubicación de este proyecto y que la memoria dice **dónde**. Un `[N]` se
  verifica una vez y vale para cualquier obra; un `[S]` hay que volver a
  leerlo en la siguiente.

## Cómo usar cada bloque

Para cada fila con numeral: abrir el PDF del documento, ir al numeral, y
responder tres cosas — (1) ¿el numeral existe?, (2) ¿dice lo que la fila dice?,
(3) ¿el valor transcrito coincide? Las filas marcadas **⚠ sin numeral** no se
pueden verificar por esta vía: se anotan aquí porque el código las declara en un
archivo de constantes `[N]` sin numeral que las sustente, y esa es una
observación de auditoría en sí misma.

Abreviaturas de archivo: `CN` = `src/constantes_normativas.py`,
`CA` = `src/criterios_adoptados.py`, `DS` = `src/datos_sitio.py`.

---

## 1. Manual de Hidrología, Hidráulica y Drenaje (MTC, RD 20-2011-MTC/14)

Es el documento con más citas del proyecto y el que gobierna las Fases 2 a 6.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `LUZ_MAX_ALCANTARILLA = 6.0` m (≥ 6.0 → puente) | 4.1.1.3.1 / 4.1.1.5.1 | Manual de Hidrología | [CN:28](src/constantes_normativas.py:28) | [N] |
| `DIAMETRO_MIN = 0.90` m | 4.1.1.3.4 a) | Manual de Hidrología | [CN:29](src/constantes_normativas.py:29) | [N] |
| `DIAMETRO_MIN_SELVA_ALTA = 1.22` m (48"; no aplica en costa) | 4.1.1.3.7 a) | Manual de Hidrología | [CN:30](src/constantes_normativas.py:30) | [N] |
| `Y_SOBRE_D_MAX = 0.75` (borde libre ≥ 25 %) | 4.1.1.3.7 b) | Manual de Hidrología | [CN:31](src/constantes_normativas.py:31) | [N] |
| `V_MIN = 0.25` m/s | 4.1.1.3.6 | Manual de Hidrología | [CN:32](src/constantes_normativas.py:32) | [N] |
| `LAUSHEY_K = 3.1` (d50 = V²/(3.1·g), métrico) | 4.1.1.3.7 c) | Manual de Hidrología | [CN:33](src/constantes_normativas.py:33) | [N] |
| ⟳ `G_LAUSHEY = 9.8` m/s² — uso exclusivo de M6 (Laushey) | 4.1.1.3.7 c) (la hoja de ruta escribe "g = 9.8 m/s²" junto a la fórmula de d50) | Manual de Hidrología | [CN:33-38](src/constantes_normativas.py:33) | [N] |
| ⟳ **Ya no vive aquí**: la gravedad genérica de M4 (tirante crítico, control de salida) es `constantes_fisicas.G = 9.81`, constante física universal, no una cita del Manual de Hidrología | — | (constante física, sin numeral que citar — igual que π) | [constantes_fisicas.py:29](src/constantes_fisicas.py:29) | — |
| `RIESGO_ADMISIBLE`: quebrada importante R=0.30, n=25 → TR 71 | Tabla N° 02, num. 3.6 | Manual de Hidrología | [CN:37-38](src/constantes_normativas.py:37) | [N] |
| `RIESGO_ADMISIBLE`: quebrada menor R=0.35, n=15 → TR 35 | Tabla N° 02, num. 3.6 | Manual de Hidrología | [CN:37,39](src/constantes_normativas.py:39) | [N] |
| `TR = 1/(1-(1-R)^(1/n))`, sin piso normativo | num. 3.6 (fórmula, no lista de TR) | Manual de Hidrología | [CN:41](src/constantes_normativas.py:41), [M1:183](src/modulos/M1_clasificacion.py:183) | [N] |
| `MANNING["metal_corrugado"] = (0.021, 0.030)` | Tabla N° 09 | Manual de Hidrología | [CN:44](src/constantes_normativas.py:44) | [N] |
| `MANNING["concreto_recto"] = (0.010, 0.013)` | Tabla N° 09 | Manual de Hidrología | [CN:45](src/constantes_normativas.py:45) | [N] |
| `MANNING["madera_duelas"] = (0.010, 0.014)` | Tabla N° 09 | Manual de Hidrología | [CN:46](src/constantes_normativas.py:46) | [N] |
| **Afirmación negativa**: HDPE NO está listado en la Tabla N° 09 | Tabla N° 09 | Manual de Hidrología | [CN:47](src/constantes_normativas.py:47) | [N] |
| `V_MAX["concreto"] = (3.0, 6.0)` m/s | Tabla N° 10 | Manual de Hidrología | [CN:52](src/constantes_normativas.py:52) | [N] |
| `V_MAX["ladrillo_c_concreto"] = (2.5, 3.5)` m/s | Tabla N° 10 | Manual de Hidrología | [CN:53](src/constantes_normativas.py:53) | [N] |
| `V_MAX["mamposteria_piedra"] = (2.0, 2.0)` m/s | Tabla N° 10 | Manual de Hidrología | [CN:54](src/constantes_normativas.py:54) | [N] |
| **Afirmación negativa**: TMC y HDPE NO están listados en la Tabla N° 10 | Tabla N° 10 | Manual de Hidrología | [CN:55](src/constantes_normativas.py:55) | [N] |
| `LONG_MAX_CUNETA = {seca: 250.0, muy_lluviosa: 200.0}` m | 4.1.2.1 d) | Manual de Hidrología | [CN:58](src/constantes_normativas.py:58) | [N] |
| `NUMERAL_LUZ = "4.1.1.3.1 / 4.1.1.5.1"` (págs. 70 y 88) | 4.1.1.3.1 / 4.1.1.5.1 | Manual de Hidrología | [M1:78](src/modulos/M1_clasificacion.py:78) | [N] |
| `NUMERAL_TR = "3.6, Tabla N 02"` (pág. 25) | 3.6, Tabla N° 02 | Manual de Hidrología | [M1:79](src/modulos/M1_clasificacion.py:79) | [N] |
| Catálogo de diámetros arranca en 0.90 m "mínimo normativo MTC" | num. 4.1.1.3.4 a) | Manual de Hidrología | [M2:58](src/modulos/M2_material.py:58) | [N] |
| `NUMERAL_V1 = "4.1.1.3.7 b)"` (V1, borde libre y/D ≤ 0.75) | 4.1.1.3.7 b) | Manual de Hidrología | [M5:106](src/modulos/M5_verificaciones.py:106) | [N] |
| `NUMERAL_V2 = "4.1.1.3.6"` (V2, V ≥ 0.25 m/s) | 4.1.1.3.6 | Manual de Hidrología | [M5:107](src/modulos/M5_verificaciones.py:107) | [N] |
| `NUMERAL_V3 = "Tabla Nº 10 (num. 4.1.1.3.6)"` (V3, velocidad máxima) — **solo se verifica el extremo SUPERIOR**, ver la nota al pie de esta sección | Tabla N° 10, num. 4.1.1.3.6, pág. 76 | Manual de Hidrología | [M5:108](src/modulos/M5_verificaciones.py:108) | [N] |
| ⟳ `NUMERAL_LAUSHEY = "4.1.1.3.7 c)"`; d50 = V²/(K·G_LAUSHEY), pág. 80 | 4.1.1.3.7 c) | Manual de Hidrología | [M6:6](src/modulos/M6_proteccion.py:6), [M6:42](src/modulos/M6_proteccion.py:42) | [N] |
| `NUMERAL_FASE_10 = "Fase 10 (num. 4.1.2.1 d), pag. 178)"` | 4.1.2.1 d), pág. 178 | Manual de Hidrología | [M10:9](src/modulos/M10_espaciamiento.py:9), [M10:61](src/modulos/M10_espaciamiento.py:61) | [N] |
| `n_manning_hdpe = (0.010, 0.013)` — rango del concreto por analogía | "Analogía a Tabla N° 09 (concreto, tubo recto)" | Manual de Hidrología (analogía) | [CA:485](src/criterios_adoptados.py:485) | [A] |
| `v_max_concreto_eleccion = None` — techo **opcional** más conservador que el máximo normativo de 6.0 m/s | Tabla N° 10 (num. 4.1.1.3.6, pág. 76): los máximos son [N]; adoptar uno más bajo que el techo de la tabla no está normado | Manual de Hidrología | [CA:523](src/criterios_adoptados.py:523) | [A] |
| `long_max_cuneta = 200.0` m (se adopta la fila "muy lluviosa" por FEN) | num. 4.1.2.1 d), pág. 178 | Manual de Hidrología | [CA:639](src/criterios_adoptados.py:639) | [A] |
| `umbral_area_quebrada_importante_ha = None` — **afirmación negativa formalizada [A]**: la Tabla N° 02 da R y n por categoría y el Manual **no fija ninguna regla de asignación física** (área, caudal, longitud ni orden de cauce) para clasificar una quebrada. No es [C] porque no hay fuente técnica que cubra el vacío: el vacío está en la norma | Tabla N° 02 (num. 3.6) | Manual de Hidrología | [CA:452](src/criterios_adoptados.py:452) | [A] |

> **Nota sobre `NUMERAL_V3` y la Tabla N° 10 — qué extremo se verifica.**
> La tabla se titula **"Velocidades máximas admisibles en conductos
> revestidos"** (num. 4.1.1.3.6, **pág. 76**). Los **dos** números de cada
> fila —concreto (3.0, 6.0), ladrillo con concreto (2.5, 3.5), mampostería de
> piedra (2.0, 2.0)— son velocidades **máximas**: el rango recorre la calidad
> del revestimiento, y el extremo inferior es el máximo admisible del acabado
> más pobre. **No es un piso.** Por eso `M5.v3_velocidad_maxima` verifica
> únicamente `V ≤ v_max` y publica como `valor_admisible` un escalar, no el
> par.
>
> El piso de velocidad existe y está fijado **aparte**, en el párrafo
> siguiente a la tabla de esa misma página: **0.25 m/s** de autolimpieza,
> aplicable por igual a todos los materiales. Eso es **V2**
> (`NUMERAL_V2 = "4.1.1.3.6"`), y no una regla adicional de V3.
>
> **Qué estaba mal antes.** V3 exigía `v_min ≤ V ≤ v_max`, es decir un segundo
> piso —por material y muy por encima del normativo— sin numeral que lo
> sostuviera: un conducto de concreto a 1.5 m/s se rechazaba por V3 aunque
> cumpliera V2 seis veces. La **transcripción** de `V_MAX` en la §1 nunca
> estuvo mal y no se ha tocado; el defecto estaba en cómo M5 la consumía.

> **Nota sobre `NUMERAL_MANNING = "4.1"`** ([M3:100](src/modulos/M3_hidraulica.py:100)):
> es la **Sec. 4.1 de la hoja de ruta**, no un numeral del Manual MTC. Lo mismo
> vale para `NUMERAL_CRITICO/ENTRADA/SALIDA = "4.2.1"/"4.2"/"4.3"`
> ([M4:153-155](src/modulos/M4_control.py:153)) y `NUMERAL_V6 = "3.1"`
> ([M5:111](src/modulos/M5_verificaciones.py:111)). Ver §11.

---

## 2. Manual de Suelos, Geología, Geotecnia y Pavimentos (MTC, RD 10-2014-MTC/14)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `RESGUARDO_NAPA_SUBRASANTE`: CBR ≥ 20 % → 0.60 m | num. 4.5.4 | Manual de Suelos | [CN:96-97](src/constantes_normativas.py:96) | [N] |
| `RESGUARDO_NAPA_SUBRASANTE`: 6 ≤ CBR < 20 → 0.80 m | num. 4.5.4 | Manual de Suelos | [CN:96](src/constantes_normativas.py:96) | [N] |
| `RESGUARDO_NAPA_SUBRASANTE`: 3 ≤ CBR < 6 → 1.00 m | num. 4.5.4 | Manual de Suelos | [CN:97](src/constantes_normativas.py:97) | [N] |
| `RESGUARDO_NAPA_SUBRASANTE`: CBR < 3 → 1.20 m | num. 4.5.4 | Manual de Suelos | [CN:97](src/constantes_normativas.py:97) | [N] |
| `CBR_MIN_SUBRASANTE = 6.0` % | num. 3.3 | Manual de Suelos | [CN:100](src/constantes_normativas.py:100) | [N] |
| ⟳ `COMPACTACION_CORONA = 0.95` (0.30 m superiores, capas de 0.15 m) | num. 3.2.1, 3.2.2, 3.3 y 9.1(1) | Manual de Suelos | [CN:107-108](src/constantes_normativas.py:107) | [N] |
| ⟳ `COMPACTACION_CUERPO = 0.90` (capas de hasta 0.30 m) | num. 3.2.1, 3.2.2, 3.3 y 9.1(1) | Manual de Suelos | [CN:109-110](src/constantes_normativas.py:109) | [N] |
| ⟳ `CALICATAS_POR_KM` (autopista/dual/1ª clase 4; 2ª clase 3; 3ª clase 2; bajo volumen 1) + `CALICATAS_POR_SENTIDO` (autopista y dual: **× sentido**, el total se duplica) | num. 4.2, Cuadro 4.1 | Manual de Suelos | [CN:125](src/constantes_normativas.py:125), [CN:134](src/constantes_normativas.py:134) | [N] |
| ⟳ `ESPACIAMIENTO_PERFIL_KM = 4.0` (nivel perfil) | num. 4.2, Cuadro 4.1 | Manual de Suelos | [CN:115](src/constantes_normativas.py:115) | [N] |
| `resguardo_HW_subrasante = "segun_CBR"` — la tabla 4.5.4 aplicada al HW de avenida, **por analogía** (el numeral regula el nivel freático, no un nivel transitorio) | num. 4.5.4 y 9.1(3) | Manual de Suelos | [CA:616](src/criterios_adoptados.py:616) | [N→] |
| `NUMERAL_V4` — `ReferenciaNormativa`: `seccion_hoja_ruta="Sec. 5.1"` / `numeral_norma="Manual de Suelos…, num. 4.5.4 y 9.1(3)"` | 4.5.4 y 9.1(3) | Manual de Suelos | [M5:109](src/modulos/M5_verificaciones.py:109) | [N→] |
| `resguardo_por_cbr()` — tabla de CBR aplicada en V4 | num. 4.5.4 | Manual de Suelos | [M5:225-226](src/modulos/M5_verificaciones.py:225) | [N] |
| Tamizado 7.A: CBR → resguardo, misma tabla de Sec. 5.1 | num. 4.5.4 | Manual de Suelos | [M7:82](src/modulos/M7_geometria.py:82) | [N] |
| ↻ `NF_profundidad_m` — **ya no es un valor declarado**: es columna del CSV, medida en cada cruce, y hoy viene vacía en las cuatro filas | El 1.4 m que se declaraba no tenía numeral del Manual: citaba la *hoja de ruta* (Sec. 0.5 num. 105; Fase 8 num. 545; Fase 9 num. 582). Siendo dato por punto, **no hay nada que verificar contra un PDF**: se verifica contra el estudio geotécnico del expediente, cruce por cruce | Estudio geotécnico del expediente (antes: "Manual de Suelos MTC / caracterización geotécnica del sitio") | [modelos.py:323](src/modelos.py:323), [M0:86](src/modulos/M0_carga.py:86) | [S] |

---

## 3. Manual de Puentes (MTC, RD 041-2016-MTC/14)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `GAMMA_AGUA_KN_M3 = 9.81` kN/m³ (subpresión) | num. 2.4.3.8.2 | Manual de Puentes | [CN:35](src/constantes_normativas.py:35) | [N] |
| `SOBRECARGA_TRASDOS_H_EQ = 0.60` m de relleno equivalente | 2.1.4.3.9, pág. 91 | Manual de Puentes | [CN:154](src/constantes_normativas.py:154), [CN:190](src/constantes_normativas.py:190) | [N] |
| `CARGA_VIVA = "HL-93"` | 2.4.3.2.2.1 | Manual de Puentes | [CN:155](src/constantes_normativas.py:155) | [N] |
| `NQ_ZAPATA_EN_TALUD = 0.0` (zapata próxima a talud) | 2.8.1.3.1.2c, págs. 272-273 | Manual de Puentes | [CN:156](src/constantes_normativas.py:156), [CN:191](src/constantes_normativas.py:191) | [N] |
| `F_PGA_TABLA = {C: 1.0, D: 1.0, E: 0.9}` para PGA ≥ 0.50 | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CN:157-159](src/constantes_normativas.py:157) | [N] |
| `NUMERAL_K_H0 = "2.8.1.1.14.2"` (k_h0 = A_s) | 2.8.1.1.14.2 | Manual de Puentes | [CN:192](src/constantes_normativas.py:192), [M9:28](src/modulos/M9_cabezal.py:28), [M9:255](src/modulos/M9_cabezal.py:255) | [N] |
| `COMBINACIONES_AASHTO = ("Resistencia I", "Servicio I", "Evento Extremo I")` — solo los **nombres** | 2.4.5.3 (AASHTO LRFD Sec. 3.4.1), págs. 140-143 | Manual de Puentes (vía AASHTO) | [CN:188-189](src/constantes_normativas.py:188) | [N] |
| ↻ `PGA_roca_B = 0.50` g, Tr = 1000 años, roca Clase B — **el mapa es normativo, la lectura es de este sitio** | Apéndice A3, mapa "Isoaceleraciones Espectrales Suelo Tipo B, AASHTO 2014 (Roca). Periodo estructural 0.0 seg (PGA)". Verificar además **sobre qué punto del mapa se leyó**: el expediente no lo registra (pendiente 1.4 de la hoja de ruta) | Manual de Puentes | [DS:128](src/datos_sitio.py:128), [M9:220](src/modulos/M9_cabezal.py:220) | [S] |
| ↻ `FACTOR_MURO_TABLA = {rígido: 1.0, desplazable: 0.5}` — los **dos** valores de tabla del numeral | numeral 2.8.1.1.14.2 | Manual de Puentes | [CN:175](src/constantes_normativas.py:175), [CN:179](src/constantes_normativas.py:179) | [N] |
| ↻ `factor_muro_eleccion = 1.0` — la **elección** de la fila rígida para este cabezal (empotrado, sin desplazamiento admisible garantizado); sensibilidad (0.5, 1.0) | El numeral fija las dos filas, **no** cuál aplica a este cabezal: eso no se verifica contra el PDF | Manual de Puentes (tabla) + decisión de proyecto (elección) | [CA:284](src/criterios_adoptados.py:284), [M9:264](src/modulos/M9_cabezal.py:264) | [A] |
| `F_pga = 1.0` — la **tabla** es [N], la **elección** dentro de ella es [A] | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CA:271](src/criterios_adoptados.py:271), [M9:168](src/modulos/M9_cabezal.py:168) | [A] |
| **Afirmación negativa**: el Manual de Puentes NO tipifica excepciones para Clase F en su Tabla 2.4.3.11.2.1.2-1 | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CA:262-263](src/criterios_adoptados.py:262) | [C] |
| `empuje_flotacion()` — U por metro lineal, conducto sumergido | num. 2.4.3.8.2 | Manual de Puentes | [M8:138-139](src/modulos/M8_estructural.py:138), [M8:148](src/modulos/M8_estructural.py:148) | [N] |
| `NUMERAL_V7 = "Fase 5, V7 (Manual de Puentes num. 2.4.3.8.2 + Fase 8, item 3)"` | 2.4.3.8.2 | Manual de Puentes | [M5:112](src/modulos/M5_verificaciones.py:112), [M8:100](src/modulos/M8_estructural.py:100) | [N] |
| `NUMERAL_SUBPRESION = "Manual de Puentes num. 2.4.3.8.2"` (subpresión del cabezal) | 2.4.3.8.2 | Manual de Puentes | [M9:169](src/modulos/M9_cabezal.py:169), [M9:663](src/modulos/M9_cabezal.py:663) | [N] |
| `presion_sobrecarga_trasdos()`: p = γ·0.60·k_a; aplica con tráfico a ≤ H/2 | num. 2.1.4.3.9 | Manual de Puentes | [M9:537](src/modulos/M9_cabezal.py:537), [M9:566](src/modulos/M9_cabezal.py:566) | [N] |
| `n_q_zapata_en_talud()` = 0.0; N_c y N_γ **reemplazados** por N_cq y N_γq | num. 2.8.1.3.1.2c, págs. 272-273 | Manual de Puentes | [M9:1024](src/modulos/M9_cabezal.py:1024), [M9:1039-1041](src/modulos/M9_cabezal.py:1039) | [N] |
| `N_cq_N_gammaq_meyerhof = None` — salen de **figuras**, no de tabla ni fórmula | figuras 2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), págs. 272-273 | Manual de Puentes | [CA:1047](src/criterios_adoptados.py:1047) | [A] |
| `factores_carga_aashto = None` — el Manual nombra las combinaciones y no transcribe las Tablas 3.4.1-1/-2 | 2.4.5.3, págs. 140-143 | Manual de Puentes (vía AASHTO) | [CA:969](src/criterios_adoptados.py:969) | [A] |
| `procedimiento_flexion_corte_aashto_sec5 = None` — remisión a AASHTO Sec. 5 | Manual de Puentes Sección 2.9, pág. 337 | Manual de Puentes (vía AASHTO) | [CA:1125](src/criterios_adoptados.py:1125), [M9:170](src/modulos/M9_cabezal.py:170), [M9:1333-1334](src/modulos/M9_cabezal.py:1333) | [A] |
| **Afirmación negativa**: AASHTO LRFD Sec. 12 NO está incorporada por el Manual de Puentes (difiere rigidez de anillo, pandeo y costura) | Sec. 12 de AASHTO, no incorporada | Manual de Puentes | [M8:35-36](src/modulos/M8_estructural.py:35), [M8:199-200](src/modulos/M8_estructural.py:199), [M8:209-210](src/modulos/M8_estructural.py:209) | [C] |
| ↻ **Afirmación negativa, ahora con la evidencia de índice**: el Manual **nunca incorporó** la Sección 12 de AASHTO LRFD (*Buried Structures and Tunnel Liners*) — su índice **salta de 2.11** (Muros de Contención y Estribos) **a 2.12** (Disposiciones Constructivas). Vacío absoluto sobre conductos enterrados; ver §14 | índice: 2.11 → 2.12 (no existe el equivalente de la Sec. 12) | Manual de Puentes | [CA:1068-1073](src/criterios_adoptados.py:1068) | [C] |
| ⚠ **TRAMPA DE VOCABULARIO — no usar este valor como altura de relleno**: el Manual sí usa la palabra "recubrimiento" para alcantarillas y da 2.0 in / 50 mm, pero ahí significa el **recubrimiento de concreto sobre el acero de refuerzo**, no la altura de relleno de tierra. Dos conceptos que comparten palabra en español y no tienen relación | Tabla 2.9.1.5.5.3-1, pág. 378 | Manual de Puentes | [CA:1073-1080](src/criterios_adoptados.py:1073) | — |

---

## 4. E.050 Suelos y Cimentaciones (RM 406-2018-VIVIENDA)

Toda la tabla de factores de seguridad de la Fase 9 sale de este documento.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `FS["capacidad_portante"] = {estático: 3.00, sísmico: 2.50}` | Art. 21 (21.1/21.2), pág. 34 | E.050 | [CN:196](src/constantes_normativas.py:196), [CN:203](src/constantes_normativas.py:203) | [N] |
| `FS["volteo"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 a), pág. 72 | E.050 | [CN:197](src/constantes_normativas.py:197), [CN:204](src/constantes_normativas.py:204) | [N] |
| `FS["deslizamiento"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 a), pág. 72 | E.050 | [CN:198](src/constantes_normativas.py:198), [CN:205](src/constantes_normativas.py:205) | [N] |
| `FS["estabilidad_global"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 b), pág. 72 | E.050 | [CN:199](src/constantes_normativas.py:199), [CN:206](src/constantes_normativas.py:206) | [N] |
| `FS["talud"] = {estático: 1.50, sísmico: 1.25}` | Art. 30.3, pág. 39 | E.050 | [CN:200](src/constantes_normativas.py:200), [CN:207](src/constantes_normativas.py:207) | [N] |
| `NUMERAL_C_PHI`: en cohesivos φ=0, en friccionantes c=0 (prohibido sumar) | Art. 20, pág. 33 | E.050 | [CN:209](src/constantes_normativas.py:209), [M9:926-927](src/modulos/M9_cabezal.py:926), [M9:979](src/modulos/M9_cabezal.py:979) | [N] |
| `NUMERAL_ZAPATA_TALUD_E050`: doble verificación (inclinación de superficie y de base + estabilidad global del talud) | Art. 30.1-30.2 | E.050 | [CN:210](src/constantes_normativas.py:210), [M9:1056](src/modulos/M9_cabezal.py:1056) | [N] |
| `SPT_PROF_MIN = 15.0` m | Art. 38 | E.050 | [CN:212](src/constantes_normativas.py:212) | [N] |
| `SPT_ESPACIAMIENTO = 1.0` m entre ensayos | **⚠ sin numeral propio** (hereda el Art. 38 de la línea anterior; `clase_sitio` sí lo cita como Art. 38) | E.050 | [CN:213](src/constantes_normativas.py:213), [CA:264-265](src/criterios_adoptados.py:264) | [N] |
| `e1_capacidad_portante()` ≥ 3.00 / 2.50 | Art. 21.1/21.2 | E.050 | [M9:882](src/modulos/M9_cabezal.py:882) | [N] |
| `e2_volteo()` ≥ 1.50 / 1.25 | num. 39.13.6 a) | E.050 | [M9:903](src/modulos/M9_cabezal.py:903) | [N] |
| `e3_deslizamiento()` ≥ 1.50 / 1.25 | num. 39.13.6 a) | E.050 | [M9:903](src/modulos/M9_cabezal.py:903) | [N] |
| `e4_estabilidad_global()` ≥ 1.50 / 1.25 | num. 39.13.6 b) | E.050 | [M9:944](src/modulos/M9_cabezal.py:944) | [N] |
| `e5_estabilidad_talud()` ≥ 1.50 / 1.25 | Art. 30.3 | E.050 | [M9:962-963](src/modulos/M9_cabezal.py:962) | [N] |
| `c_phi_fundacion = None` — la obligación de usar solo uno (φ=0 o c=0) | Art. 20 | E.050 | [CA:719](src/criterios_adoptados.py:719) | [A] |
| `PERFIL_SUELO_PRESUNTO` — lo reemplaza el **SPT de licuefacción: ≥ 15 m, ensayos cada 1 m** | Art. 38 | E.050 | [CA:229](src/criterios_adoptados.py:229) | [S] |
| `clase_sitio` — lo reemplazan el **estudio de respuesta de sitio específico** que AASHTO exige para la Clase F y la **caracterización sobre los 30 m superiores** (Vs30 o N̄). El SPT de 15 m **no lo cierra**: otra profundidad, otra pregunta | Art. 3.10.3.1 (AASHTO) / perfil de E.030 | AASHTO LRFD / E.030 | [CA:256](src/criterios_adoptados.py:256) | **[A]** (era [C]) |
| `metodo_estabilidad_global = None` — **afirmación negativa**: E.050 fija el umbral, no el método | Art. 30.3 y num. 39.13.6 b) | E.050 | [CA:1078](src/criterios_adoptados.py:1078) | [A] |

---

## 5. E.060 Concreto Armado

Entra al proyecto solo por la **excepción declarada de durabilidad y
recubrimientos** (Vía 1 de Sec. 0.2); el diseño estructural es de AASHTO.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `SULFATOS`: SO₄ 0.00–0.10 % → sin exigencia | Tabla 4.4 | E.060 | [CN:217](src/constantes_normativas.py:217) | [N] |
| `SULFATOS`: 0.10–0.20 % → cemento II/IP(MS)/IS(MS), a/c 0.50, f'c 28 MPa | Tabla 4.4 | E.060 | [CN:218](src/constantes_normativas.py:218) | [N] |
| `SULFATOS`: 0.20–2.00 % → cemento V, a/c 0.45, f'c 31 MPa | Tabla 4.4 | E.060 | [CN:219](src/constantes_normativas.py:219) | [N] |
| `SULFATOS`: > 2.00 % → cemento V + puzolana, a/c 0.45, f'c 31 MPa | Tabla 4.4 | E.060 | [CN:220](src/constantes_normativas.py:220) | [N] |
| `CLORUROS_EXTERNOS = {a/c máx 0.40, f'c mín 35 MPa}` | Art. 4.2 / 4.4 | E.060 | [CN:222](src/constantes_normativas.py:222) | [N] |
| `RECUBRIMIENTO`: contra suelo 70 mm; suelo/intemperie ≥ 3/4" 50 mm; ≤ 5/8" 40 mm | Art. 7.7.1, pág. 54 | E.060 | [CN:223-225](src/constantes_normativas.py:223), [M9:1129](src/modulos/M9_cabezal.py:1129) | [N] |
| `AMBIENTE_CORROSIVO_AUMENTAR` — el artículo dice "aumentar adecuadamente" y **no fija cuánto** | Art. 7.7.5.1 | E.060 | [CN:226-229](src/constantes_normativas.py:226), [M9:1196](src/modulos/M9_cabezal.py:1196) | [N] |
| `CUANTIA_MIN_MURO = {horizontal 0.0020, vertical 0.0015}` — **piso obligatorio**, aplicado como ρ_diseño = max(ρ_calculado, ρ_mínimo) en `M9.cuantia_de_diseno`. Que AASHTO gobierne el *dimensionamiento* (Vía 1, Sec. 0.2) no convierte el mínimo en informativo | Art. 14.3.1, pág. 133 | E.060 | [CN:291](src/constantes_normativas.py:291), [M9:1281](src/modulos/M9_cabezal.py:1281) | [N] |
| `cortante_alto_muro_e060_art_11_10_10_2 = None` — **segundo mínimo de E.060**: escalón de la cuantía horizontal a 0.0025 bajo cortante alto. **Vacío declarado**, no omitido: M9 no calcula cortante (bloqueado en `procedimiento_flexion_corte_aashto_sec5`) y el artículo no está en la hoja de ruta | Art. 11.10.10.2 — **⚠ pendiente de recoger en la hoja de ruta** | E.060 | [CA:1214](src/criterios_adoptados.py:1214) | [A] |
| `ESPESOR_TEMPERATURA_DOS_CARAS = 0.250` m (refuerzo en dos caras) | Art. 14.8.3 | E.060 | [CN:238-239](src/constantes_normativas.py:238), [M9:1250](src/modulos/M9_cabezal.py:1250) | [N] |
| `ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0` (≤ 3h) | Art. 14.3.3 | E.060 | [CN:240](src/constantes_normativas.py:240), [M9:1276-1277](src/modulos/M9_cabezal.py:1276) | [N] |
| `ESPACIAMIENTO_MAX_ABSOLUTO = 0.400` m (400 mm) | Art. 14.3.3 | E.060 | [CN:241-242](src/constantes_normativas.py:241) | [N] |
| `CICLOPEO_FC_MATRIZ_MIN = 10.0` MPa | Art. 22.10, págs. 194-195 | E.060 | [CN:245](src/constantes_normativas.py:245), [M9:1303](src/modulos/M9_cabezal.py:1303) | [N] |
| `CICLOPEO_FRACCION_PIEDRA_MAX = 0.30` del volumen | Art. 22.10, págs. 194-195 | E.060 | [CN:246-247](src/constantes_normativas.py:246) | [N] |

---

## 6. EG-2013 — Especificaciones Técnicas Generales para Construcción, Capítulo V (Secciones 502-508)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `H_RELLENO_MIN["hdpe"] = 0.30` m (clave a subrasante) | 508.07 / 508.08 | EG-2013 | [CN:110](src/constantes_normativas.py:110), [M7:20](src/modulos/M7_geometria.py:20), [M7:259-260](src/modulos/M7_geometria.py:259) | [N] |
| `H_RELLENO_MIN["concreto"] = None` — **afirmación negativa**: EG-2013 no lo fija, remite a AASHTO M-170M | AASHTO M-170M (clases I a V) | EG-2013 → norma de producto | [CN:111](src/constantes_normativas.py:111) | [N]/[C] |
| `H_RELLENO_MIN["tmc"] = None` — **afirmación negativa**: EG-2013 no lo fija, remite a la norma de producto | ASTM A-807 / AASHTO M36 | EG-2013 → norma de producto | [CN:112](src/constantes_normativas.py:112) | [N]/[C] |
| `SECCION_EG2013`: concreto simple 505, concreto reforzado 506, TMC 507, HDPE 508. **Renombrada desde `SUBSECCION`**: son Secciones completas del Capítulo V, no subsecciones de ninguna "Sección 500" | Secciones 505 / 506 / 507 / 508 | EG-2013 | [CN:158](src/constantes_normativas.py:158), [M11:697](src/modulos/M11_reporte.py:697) | [N] |
| `SECCION_CABEZALES = "503"` (concreto estructural; + 504 acero) | 503 (+504) | EG-2013 | [CN:116](src/constantes_normativas.py:116) | [N] |
| `CAMA_RELLENO_LATERAL["concreto_simple"]`: cama Clase F (f'c = 14 MPa) ≥ 15 cm; Clase F hasta ≥ 1/4 del D exterior; relleno Sec. 502 ≥ 95 % MDS | 505.03/.07/.10/.11, págs. 950-951 | EG-2013 | [CN:124-129](src/constantes_normativas.py:124) | [N] |
| `CAMA_RELLENO_LATERAL["concreto_reforzado"]`: subbase granular (Sec. 402) ≥ 15 cm, ≥ 95 % MDS; subbase hasta ≥ 1/6 del D exterior; relleno Sec. 502 | 506.03/.07/.10/.11, págs. 959-960 | EG-2013 | [CN:130-135](src/constantes_normativas.py:130) | [N] |
| `CAMA_RELLENO_LATERAL["tmc"]`: subbase ≥ 15 cm, ≥ 95 % MDS con arena suelta de 12 mm; capas de 15-20 cm ≥ 90 % base/cuerpo y ≥ 95 % corona | 507.06/.07/.08, pág. 970 | EG-2013 | [CN:136-142](src/constantes_normativas.py:136) | [N] |
| `CAMA_RELLENO_LATERAL["hdpe"]`: arena gruesa, capas de 15 cm, espesor 15-30 cm (30 cm en roca o suelo blando); capas alternadas simétricas de 15 cm a > 95 %, los 30 cm superiores a ≥ 100 %; prohibida la anegación | 508.05/.07, págs. 981-982 | EG-2013 | [CN:143-150](src/constantes_normativas.py:143) | [N] |
| `NUMERAL_8_1` — `ReferenciaNormativa`: `seccion_hoja_ruta="Sec. 8.1"` / `numeral_norma="EG-2013, Capítulo V, Sección de cada material (505/506/507/508); rellenos generales en la Sección 502"`. **Corrige una cita doblemente falsa**: ni "Sec. 8.1" es del EG-2013, ni existe una "Sección 500" | Capítulo V, Secciones 502 y 505-508 | EG-2013 | [M8:106](src/modulos/M8_estructural.py:106) | [N] |
| `NUMERAL_9_1` — `ReferenciaNormativa`: `seccion_hoja_ruta="Sec. 9.1"` / `numeral_norma="EG-2013, Capítulo V, Sección 503 (concreto estructural), num. 503.01, pág. 905"` | 503.01, pág. 905 | EG-2013 | [M9:173](src/modulos/M9_cabezal.py:173) | [N] |
| ↻ `h_relleno_min_concreto_tmc = None` — **cita cerrada como VACÍO VERIFICADO**, ver §14. EG-2013 fija 0.30 m para HDPE y **no** fija nada para concreto ni TMC | 508.07 (lo que sí fija, literal); 505 / 506 / 507 → 502 (lo que no fija) | EG-2013 | [CA:1054-1088](src/criterios_adoptados.py:1054) | [C] |
| ↻ **Cita literal de lo que sí fija** — «La altura de relleno mínimo desde la clave de la tubería hasta el nivel de la subrasante será de 0,30 m.» Es exactamente la magnitud que calcula V7 (subrasante − clave) | Subsección 508.07, pág. 982 | EG-2013 | [CN:160](src/constantes_normativas.py:160) | [N] |
| **Afirmación negativa**: las Secciones 505, 506 y 507 solo regulan colocación y compactación y remiten a la Sección 502, que tampoco fija altura mínima de diseño | 505 / 506 / 507 → 502 | EG-2013 | [CA:1076-1082](src/criterios_adoptados.py:1076) | [C] |
| **Remisiones formales** que cierran el circuito hacia §9: 506.02 → AASHTO M-170M (concreto reforzado); 507.05 / 507.06 / 507.08 → ASTM A-807 (TMC) | 506.02, pág. 959; 507.05/.06/.08, págs. 969-970 | EG-2013 → norma de producto | [CA:1082-1088](src/criterios_adoptados.py:1082) | [C] |
| Nota constructiva: el equipo pesado no circula sobre el conducto antes de que el relleno alcance 0.30 m | Sec. 7.A de la hoja de ruta, apoyada en EG-2013 | EG-2013 | [CA:1103-1105](src/criterios_adoptados.py:1103) | [N] |

---

## 7. HDS-5 (FHWA), 3ª edición, abril 2012

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `KU_METRICO = 1.811` (q* = KU·Q/(A·D^0.5)) | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:61-62](src/constantes_normativas.py:61) | [N] |
| `Q_LIM_NO_SUMERGIDO = 3.5` | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:63](src/constantes_normativas.py:63) | [N] |
| `Q_LIM_SUMERGIDO = 4.0` (entre ambos: interpolación lineal) | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:64](src/constantes_normativas.py:64) | [N] |
| `HDS5_INLET["circular_concreto_square_edge_headwall"]`: K=0.0098, M=2.00, c=0.0398, Y=0.67 | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:67-68](src/constantes_normativas.py:67) | [N] |
| `HDS5_INLET["circular_cmp_headwall"]`: K=0.0078, M=2.00, c=0.0379, Y=0.69 | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:69-70](src/constantes_normativas.py:69) | [N] |
| `HDS5_INLET["circular_cmp_mitered"]`: K=0.0210, M=1.33, c=0.0463, Y=0.75 | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:71-72](src/constantes_normativas.py:71) | [N] |
| `Ks = -0.5` (sin inglete) / `+0.7` (con inglete) | **⚠ el código declara expresamente que NO figura en la Tabla A.1**: "proviene de la formulación" | HDS-5 (formulación, sin tabla) | [CN:74](src/constantes_normativas.py:74), [M4:67-76](src/modulos/M4_control.py:67), [M4:308-310](src/modulos/M4_control.py:308) | [N] |
| Ecuaciones de control de entrada: q* ≤ 3.5 → HWi/D = Hc/D + K·(q*)^M + Ks·S; q* ≥ 4.0 → HWi/D = c·(q*)² + Y + Ks·S | Apéndice A (Formas 1 y 2) | HDS-5 | [M4:55-57](src/modulos/M4_control.py:55) | [N] |
| `metodo_transicion_hds5 = "interpolacion_lineal_entre_extremos"` — la transición 3.5 < q* < 4.0. **La recta NO es el método del HDS-5**: HDS-5 empalma las dos ramas con una curva **tangente empírica sin ecuación publicada**. La interpolación lineal la prescribe Sec. 4.2 de la hoja de ruta y aquí queda declarada como simplificación adoptada | Cap. IV y Apéndice A (curva de transición, sin ecuación) | HDS-5 3ª ed. (2012) | [CA:523](src/criterios_adoptados.py:523), [M4:335-355](src/modulos/M4_control.py:335) | [C] |
| `K_FRICCION_SI = 19.63` — H = (1 + ke + 19.63·n²·L/R^(4/3))·V²/(2g); "29 es el valor inglés". **Corregido desde 19.62**: 19.63 es la conversión SI que el propio HDS-5 declara para su K = 29. Se retiró la justificación "= 2·g", coincidencia numérica sin respaldo en la fuente. **⚠ La hoja de ruta sigue diciendo 19.62 y debe corregirse** | **⚠ sin numeral**: se cita la ecuación de control de salida, no un apartado | HDS-5 / literatura FHWA | [CN:84](src/constantes_normativas.py:84), [M4:79-110](src/modulos/M4_control.py:79) | [N] |
| `h_o = max(TW, (y_c + D)/2)` | **⚠ sin numeral** | HDS-5 (control de salida) | [CN:81](src/constantes_normativas.py:81), [M4:80-82](src/modulos/M4_control.py:80) | [N] |
| `hds5_embocadura_hdpe = {K:0.0098, M:2.00, c:0.0398, Y:0.67, Ks:-0.5}` — fila del **concreto** aplicada a HDPE de interior liso a ras del muro | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CA:467](src/criterios_adoptados.py:467) | [C] |
| `ke_entrada = 0.5` (square edge with headwall) — **cita cerrada** | Apéndice C, **Tabla C.2, pág. C.2** | HDS-5 3ª ed. (2012) | [CA:617](src/criterios_adoptados.py:617) | [C] |
| `geometria_control_salida = "seccion_llena"` (A = πD²/4, R = D/4, V = Q/A) | Cap. III — control de salida a sección llena | HDS-5 | [CA:568](src/criterios_adoptados.py:568) | [C] |
| `HW_D_max = 1.5` — **cita cerrada**. La sensibilidad declarada (1.2, 1.5) es un **subrango** del 1.0–1.5 de la fuente | **Sec. 2.2.5, pág. 2.14** (rango 1.0–1.5) | HDS-5 3ª ed. (2012) | [CA:683](src/criterios_adoptados.py:683) | [C] |
| Alternativa citada si el barril no llena: procedimiento de barril parcialmente lleno | Cap. III | HDS-5 | [CA:595-597](src/criterios_adoptados.py:595), [M4:400](src/modulos/M4_control.py:400) | [C] |

---

## 8. AASHTO LRFD Bridge Design Specifications

Ninguna cita a AASHTO LRFD lleva hoy un valor numérico transcrito: **todas las
tablas quedaron sin extraer**. Este bloque es, casi entero, el inventario de lo
que falta traer del PDF.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `COMBINACIONES_AASHTO` — los tres **nombres** (Resistencia I, Servicio I, Evento Extremo I) | Sec. 3.4.1 (vía Manual de Puentes num. 2.4.5.3) | AASHTO LRFD | [CN:188-189](src/constantes_normativas.py:188), [M9:798-799](src/modulos/M9_cabezal.py:798) | [N] |
| ~~`clase_sitio = "F_con_excepcion_periodo_corto"` — excepción para estructuras de periodo fundamental corto (≤ 0.5 s)~~ **CITA FALSA — RETIRADA.** Verificado contra AASHTO LRFD 9.ª ed. (2020): la dispensa no está en el Art. 3.10.3.1, ni en C3.10.3.1, ni en tabla o nota alguna. AASHTO exige estudio de respuesta de sitio específico para la Clase F, de forma incondicional. Hoy: `clase_sitio = "F_con_factores_tabulados_por_adopcion"`, adopción declarada del proyectista **sin respaldo normativo** — §0.5 | ninguna | — | [CA:256](src/criterios_adoptados.py:256) | ~~[C]~~ → **[A]** |
| ↳ esa verificación **ya se hizo**: no está en el articulado ni en el comentario, porque no existe. Lo que queda pendiente es otra cosa — declarar en la memoria que la adopción va contra una exigencia expresa de AASHTO, y programar el estudio de respuesta de sitio | Art. 3.10.3.1 y C3.10.3.1, 9.ª ed. (2020) | AASHTO LRFD | [CA:317](src/criterios_adoptados.py:317) | **[A]** |
| `factores_carga_aashto = None` — factores γ (DC, EV, EH, LS, WA, EQ) con máximos y mínimos | Tablas 3.4.1-1 y 3.4.1-2 | AASHTO LRFD | [CA:969](src/criterios_adoptados.py:969), [M9:52](src/modulos/M9_cabezal.py:52), [M9:805](src/modulos/M9_cabezal.py:805) | [A] |
| `FS_flotacion = None` — FS de V7, ΣW ≥ FS·U | Sec. 12 (no incorporada por el Manual de Puentes) | AASHTO LRFD | [CA:842](src/criterios_adoptados.py:842) | [C] |
| Rigidez de anillo, pandeo y resistencia de costura: **diferidos al expediente** | Sec. 12 | AASHTO LRFD | [M8:35-36](src/modulos/M8_estructural.py:35), [M8:209-214](src/modulos/M8_estructural.py:209) | [C] |
| `recubrimiento_aashto_mm = None` — lado AASHTO de la regla "rige el recubrimiento MAYOR" | tabla de recubrimientos mínimos, Sec. 5 | AASHTO LRFD | [CA:1100](src/criterios_adoptados.py:1100), [M9:1147-1150](src/modulos/M9_cabezal.py:1147) | [A] |
| `procedimiento_flexion_corte_aashto_sec5 = None` — factores φ, límites de refuerzo, modelo de corte (MCFT / β-θ) | Sección 5 (vía Manual de Puentes Sec. 2.9, pág. 337) | AASHTO LRFD | [CA:1125](src/criterios_adoptados.py:1125), [M9:1333-1345](src/modulos/M9_cabezal.py:1333) | [A] |
| `peso_especifico_concreto_kn_m3 = None` — peso unitario del concreto armado | Tabla 3.5.1-1 (o Manual de Puentes) | AASHTO LRFD | [CA:998](src/criterios_adoptados.py:998), [CA:1012-1013](src/criterios_adoptados.py:1012) | [A] |
| `punto_aplicacion_incremento_sismico = None` — altura de aplicación de (P_AE − P_A) | Sec. 11 (alternativa: Seed-Whitman, 0.6H) | AASHTO LRFD | [CA:390](src/criterios_adoptados.py:390), [CA:406-408](src/criterios_adoptados.py:406) | [A] |
| Advertencia transversal: **declarar la EDICIÓN de AASHTO LRFD** — los factores y la numeración de la Sec. 11 cambiaron entre ediciones | — | AASHTO LRFD | [CA:992-995](src/criterios_adoptados.py:992) | [A] |

---

## 9. Normas de producto ASTM / AASHTO (M-170M, M36, A760, A-807, M294, C76)

No están en la lista de PDF de la sesión, pero el código las cita con nombre y
usa valores atribuidos a ellas. Se separan para que quede claro que su
verificación necesita otras fuentes.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `D_MAX["concreto_reforzado"] = 2.70` m | (nombre de norma, sin numeral) — marcado "VERIFICAR" en el propio código | ASTM C76 / AASHTO M170 | [CN:87-88](src/constantes_normativas.py:87) | [N] |
| `D_MAX["tmc"] = 2.10` m | (nombre de norma, sin numeral) | AASHTO M36 / ASTM A760 | [CN:88](src/constantes_normativas.py:88) | [N] |
| `D_MAX["hdpe"] = 1.50` m (el más restrictivo) | (nombre de norma, sin numeral) | AASHTO M294 | [CN:89](src/constantes_normativas.py:89) | [N] |
| `D_PASO = 0.15` m — "reproduce las series de 6″ y 150 mm" | (nombre de norma, sin numeral) | ASTM / AASHTO | [CN:84](src/constantes_normativas.py:84) | [N] |
| `D_INICIO = 0.90` m | mínimo normativo MTC (ver §1) | Manual de Hidrología | [CN:85](src/constantes_normativas.py:85) | [N] |
| `diametros_normalizados` = inicio 0.90, paso 0.15, topes {concreto 2.70, TMC 2.10, HDPE 1.50} | ASTM C76/AASHTO M170; AASHTO M36/ASTM A760; AASHTO M294 | ASTM / AASHTO | [CA:764](src/criterios_adoptados.py:764) | [C] |
| ↳ verificación pendiente declarada: confirmar los topes contra el texto de cada norma de producto | — | ASTM / AASHTO | [CA:775-777](src/criterios_adoptados.py:775) | [C] |
| `NORMA_PRODUCTO` por material (reporte) | ASTM C76/AASHTO M170; AASHTO M36/ASTM A760; AASHTO M294 | ASTM / AASHTO | [M2:148-150](src/modulos/M2_material.py:148) | [N] |
| `clases_producto_por_relleno = None` — tabla clase/calibre × diámetro × rango de altura de relleno, **sin extraer** | AASHTO M-170M (clases I-V); ASTM A-807 / AASHTO M36 (calibre por altura) | ASTM / AASHTO | [CA:814](src/criterios_adoptados.py:814), [M8:113](src/modulos/M8_estructural.py:113) | [C] |
| **Afirmación negativa**: AASHTO M294 (HDPE) no tiene tabla de clase por altura; depende de un cálculo de rigidez de anillo diferido al expediente | AASHTO M294 | ASTM / AASHTO | [CA:829-832](src/criterios_adoptados.py:829) | [C] |
| ↻ `h_relleno_min_concreto_tmc = None` (lado norma de producto) — **cita cerrada en negativo**, ver §14. Ya no es "falta extraer": no hay nada que extraer | AASHTO M 170M; AASHTO M 36; ASTM A760 | ASTM / AASHTO | [CA:1054-1088](src/criterios_adoptados.py:1054) | [C] |
| **Afirmación negativa**: AASHTO M 170M, M 36 y ASTM A760 **no contienen alturas de relleno admisibles**. Su **Nota 1** las excluye de forma expresa: son especificaciones de **fabricación y compra**, y no cubren encamado, relleno ni la relación entre carga de cobertura y clase o espesor | Nota 1 de cada norma | ASTM / AASHTO | [CA:1057-1063](src/criterios_adoptados.py:1057) | [C] |
| **Afirmación negativa**: **M 170M clasifica por D-load (resistencia), no por altura** — no existe la tabla clase-a-altura que el criterio decía que iba a extraer de ella | AASHTO M 170M | ASTM / AASHTO | [CA:1063-1065](src/criterios_adoptados.py:1063) | [C] |

---

## 10. E.030 Diseño Sismorresistente (RM 183-2026-VIVIENDA) — solo referencia

El código declara expresamente que estos valores **no gobiernan** el cabezal.
Los tres salieron de `constantes_normativas.py` en esta revisión: ninguno era
una constante `[N]` —los tres son la lectura de un mapa o de una clasificación
**sobre las coordenadas de este proyecto**— y los tres siguen siendo
referencia que no entra en ningún cálculo. El cambio es de clasificación, no
de uso.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| ↻ `ZONA_SISMICA_LA_UNION = 4` | Antes **⚠ sin numeral**; ahora declara Anexo II (zonificación sísmica por distritos). El numeral es de E.030 y **no está en la hoja de ruta**, que solo cita el `Z` resultante | E.030 | [DS:167](src/datos_sitio.py:167) | [S] |
| ↻ `Z_E030 = 0.45` (Tr = 475 años) — "NO se usa para el cabezal" | Antes **⚠ sin numeral**; ahora declara Art. 11.1 leído con la zona del Anexo II. Lo que sí está en la hoja de ruta (num. 87) es el **descarte** | E.030 | [DS:194](src/datos_sitio.py:194) | [S] |
| ↻ `PERFIL_SUELO_PRESUNTO = "S5"` (suelos potencialmente licuables) — **referencia muerta**: no lo invoca ningún módulo | Art. 14.6. El artículo define el **esquema** S0–S5; qué letra le toca a este sitio es la aplicación de ese esquema a las condiciones de la llanura del Bajo Piura | E.030 | [CA:217](src/criterios_adoptados.py:217) | [S] |
| `demanda_sismica_licuefaccion = 1000` años — **descarta** el sismo de 475 años de E.030 por coherencia con el Manual de Puentes | (referencia al Tr 475 de E.030) | E.030 (descartado) | [CA:751](src/criterios_adoptados.py:751) | [A] |

---

## 10-bis. WSDOT Hydraulics Manual (M 23-03.12, abril 2026)

Cubre el vacío que la Tabla N° 10 del Manual MTC deja abierto: esa tabla solo
lista conductos **revestidos** (concreto, ladrillo, mampostería) y no alcanza a
los materiales flexibles. Los dos valores salen de la **misma** tabla de la
misma página, pero **no significan lo mismo** en cada material, y la columna de
numeral lo dice: para el termoplástico la fuente prohíbe el uso por encima del
límite, y para el metal solo exige mayor calibre o revestimiento. El 4.6 m/s
del TMC es, por eso, adopción conservadora del proyecto y no un techo de la
fuente.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `v_max_hdpe = 4.6` m/s (= 15 ft/s) — **techo duro de la fuente**: por encima del límite el termoplástico no puede reforzarse estructuralmente y la propia tabla prohíbe su uso | Cap. 8, S8-6, Tabla 8-4 "Pipe Abrasion Levels", pp. 8-27/8-28 | WSDOT Hydraulics Manual M 23-03.12 (abril 2026) | [CA:660](src/criterios_adoptados.py:660) | [C] |
| `v_max_tmc = 4.6` m/s — **la fuente NO fija techo absoluto para metal**: por encima de este valor exige mayor calibre o revestimiento, no prohíbe el material. Se adopta como límite de diseño conservador porque el catálogo de M2 no modela protección adicional por calibre | Cap. 8, S8-6, Tabla 8-4 "Pipe Abrasion Levels", pp. 8-27/8-28 | WSDOT Hydraulics Manual M 23-03.12 (abril 2026) | [CA:672](src/criterios_adoptados.py:672) | [C] |

---

## 11. Citas que NO apuntan a ninguno de los PDF

Se listan aparte para que nadie las busque en un documento normativo.

### 11.a. Referencias a la propia hoja de ruta (`docs/hoja_de_ruta_alcantarillas_v8.md`)

Varios `NUMERAL_*` de módulo parecen numerales normativos y son secciones de la
hoja de ruta. **No se verifican contra un PDF externo; se verifican contra la
hoja de ruta**, que es la fuente de verdad del proyecto.

| Constante | Valor de la cita | Archivo:línea |
|---|---|---|
| `NUMERAL_FAMILIA` | `"Sec. 2.3"` — "la hoja de ruta, sin numeral MTC propio" | [M1:80](src/modulos/M1_clasificacion.py:80) |
| `NUMERAL_CATALOGO` | `"Sec. 3.2"` — "nuevo en v7, sin numeral MTC propio" | [M2:125](src/modulos/M2_material.py:125) |
| `NUMERAL_MATERIAL` | `"Sec. 3.4"` | [M2:126](src/modulos/M2_material.py:126) |
| `NUMERAL_MANNING` | `"4.1"` (Sec. 4.1 de la hoja de ruta) | [M3:100](src/modulos/M3_hidraulica.py:100) |
| `NUMERAL_CRITICO` / `NUMERAL_ENTRADA` / `NUMERAL_SALIDA` | `"4.2.1"` / `"4.2"` / `"4.3"` | [M4:153-155](src/modulos/M4_control.py:153) |
| `NUMERAL_V6` | `"3.1"` | [M5:111](src/modulos/M5_verificaciones.py:111) |
| `NUMERAL_V8` | `"Fase 5, V8"` — "[N] verificación, no diseño, sin numeral que fije el TR ni el umbral" | [M5:113](src/modulos/M5_verificaciones.py:113), [CA:699-700](src/criterios_adoptados.py:699) |
| `NUMERAL_V9` | `"Sec. 3.2 (V9, nuevo en v7)"` | [M5:114](src/modulos/M5_verificaciones.py:114) |
| `NUMERAL_7A` / `NUMERAL_7B` | `"Sec. 7.A"` / `"Sec. 7.B"` | [M7:206-207](src/modulos/M7_geometria.py:206) |
| `NUMERAL_G1` / `NUMERAL_G2` | `"Sec. 7.A (recubrimiento EG-2013 / resguardo Sec. 5.1)"` / `"Sec. 7.B (cotas amarradas al fondo del receptor)"` | [M7:208-209](src/modulos/M7_geometria.py:208) |
| `NUMERAL_8_1_2` / `NUMERAL_8_5` | `"Fase 8, items 1-2"` / `"Fase 8, item 5"` | [M8:97](src/modulos/M8_estructural.py:97), [M8:99](src/modulos/M8_estructural.py:99) |
| `NUMERAL_9_2` / `NUMERAL_9_3` / `NUMERAL_MO` | `"Sec. 9.2"` / `"Sec. 9.3 (E.050)"` / `"Sec. 9.2 (Mononobe-Okabe)"` | [M9:164-166](src/modulos/M9_cabezal.py:164) |
| `NUMERAL_REGLA_RECUBRIMIENTO` | `"Sec. 0.2 (rige el recubrimiento mayor)"` | [M9:171](src/modulos/M9_cabezal.py:171) |
| `NUMERAL_BUCLE` | `"Sec. 2 de la guia de sesiones (Fases 4 y 5)"` | [MD:116](src/modulos/MD.py:116) |

### 11.b. Otras fuentes citadas por nombre

| Valor | Fuente citada | Archivo:línea | Etiqueta |
|---|---|---|---|
| `remanso_derecho_via = None` | Manual de Diseño Geométrico **DG-2018** + **Ley 29338**; requiere perfil de remanso (paso a paso o HEC-RAS) | [CA:677-679](src/criterios_adoptados.py:677), [M5:110](src/modulos/M5_verificaciones.py:110) | [A] |
| `talud_terraplen = None` | **DG-2018** y sección tipo del proyecto | [CA:909-911](src/criterios_adoptados.py:909) | [A] |
| `pendiente_relleno_trasdos_i = None` | Sección típica del expediente vial (**DG-2018**) o detalle de coronación del terraplén | [CA:335-337](src/criterios_adoptados.py:335) | [A] |
| `v_max_hdpe = 4.6` m/s | ↻ **cita cerrada** — WSDOT Hydraulics Manual, ver §10-bis. Antes: PPI/FHWA, fuente identificada y valores sin extraer | [CA:660](src/criterios_adoptados.py:660) | [C] |
| `v_max_tmc = 4.6` m/s | ↻ **cita cerrada** — WSDOT Hydraulics Manual, ver §10-bis. Antes: PPI/FHWA, ídem | [CA:672](src/criterios_adoptados.py:672) | [C] |
| `longitud_proteccion_salida = None` | Práctica corriente de enrocado o **HEC-14** | [CA:947-948](src/criterios_adoptados.py:947) | [A] |
| `homogeneidad_serie_fen = None` | Serie **SENAMHI** con longitud de registro, estación y años faltantes | [CA:427-429](src/criterios_adoptados.py:427) | [A] |
| `TW_receptor = None` | **ANA** / Junta de Usuarios del Bajo Piura | [CA:635](src/criterios_adoptados.py:635) | [A] |
| `Mw_licuefaccion = None` | Desagregación del peligro sísmico / sismo de subducción del norte peruano | [CA:746-747](src/criterios_adoptados.py:746) | [A] |
| `k_v = 0.0` | "Práctica corriente; no fijado por el Manual de Puentes" | [CA:306](src/criterios_adoptados.py:306) | [A] |
| `espesor_proteccion_salida = 1.75`·d50 | "Práctica corriente de diseño de enrocado" (rango 1.5–2.0 d50) | [CA:933](src/criterios_adoptados.py:933) | [A] |
| `angulo_aletas = None` | "Práctica corriente; no fijado por el Manual" | [CA:960](src/criterios_adoptados.py:960) | [A] |
| `N_cq_N_gammaq_meyerhof = None` | **Meyerhof (1957)**, vía las figuras del Manual de Puentes (ver §3) | [CA:1066-1067](src/criterios_adoptados.py:1066) | [A] |
| `punto_aplicacion_incremento_sismico = None` | **Seed-Whitman** (≈0.6H), vía AASHTO (ver §8) | [CA:406-408](src/criterios_adoptados.py:406) | [A] |

### 11.c. Módulos sin citas normativas externas

`M0_carga.py`, `MD.py` y `M11_reporte.py` no formulan afirmaciones normativas
propias: M0 y MD citan solo secciones de la hoja de ruta, y M11 reimprime los
numerales que le llegan dentro de los objetos `Verificacion` y demás modelos, sin
declarar ninguno por su cuenta.

---

## 12. Criterios `[A]` — quedan FUERA de la verificación de citas

**Los `[A]` no entran a este chequeo.** Un criterio `[A]` es, por definición, un
parámetro que **ninguna norma fija**: no hay numeral que confrontar contra un
PDF, y buscarle uno es perder el tiempo o, peor, inventarlo.

Estos criterios se auditan con **otra pregunta**, en una revisión distinta:

> ¿La adopción sigue siendo razonable, sigue estando justificada, y sigue siendo
> el valor que se va a defender en la memoria de cálculo?

Esa revisión mira la `justificacion`, la `sensibilidad` declarada y el
`reemplazado_por` — no un numeral.

**Matiz importante, para que nadie lo confunda:** varios `[A]` **sí mencionan un
numeral**, y por eso aparecen también en los bloques de arriba. En esos casos lo
que está citado es la **tabla o el artículo subyacente** (que es `[N]` y sí se
verifica), mientras que lo `[A]` es la **elección o el relleno del vacío**. El
caso canónico es `F_pga`: la Tabla 2.4.3.11.2.1.2-1 del Manual de Puentes es
`[N]` y se verifica; adoptar 1.0 dentro de ella es `[A]` y no se verifica, se
justifica. Algo parecido ocurre con `v_max_concreto_eleccion`, aunque **no es el
mismo caso** y conviene no confundirlos: ahí la norma **sí** resuelve sola —el
techo `[N]` es 6.0 m/s— y el criterio solo permite adoptar uno **más
conservador**, de modo que no hay vacío ni elección obligatoria. Por eso es el
único que se lee con `valor_si_declarado()`: sin declarar no detiene nada. Con
`long_max_cuneta` (las dos filas son `[N]`, elegir la de 200 m es
`[A]`) y —desde esta revisión— con `factor_muro_eleccion`, que hasta ahora
mezclaba las dos mitades en un solo valor `[N]`.

**Y no confundir un `[A]` con un `[S]`.** Los dos son valores que no son
portables a otra obra, y ahí termina el parecido: un `[A]` es una decisión que
pudo ser otra, y por eso se defiende con el rango de sensibilidad; un `[S]` es
un hecho que se leyó o se midió, no admite rango, y se defiende con la
trazabilidad de la lectura. Antes de la quinta etiqueta, forzar el PGA o el
nivel freático dentro de `[A]` habría dicho que alguien los "adoptó".

### Los 33 criterios `[A]` del proyecto

| Criterio | Valor | Estado | Sensibilidad declarada | Archivo:línea |
|---|---|---|---|---|
| `F_pga` | 1.0 | declarado | (0.9, 1.0) | [CA:289](src/criterios_adoptados.py:289) |
| ↻ `factor_muro_eleccion` | 1.0 (fila rígida) | declarado | (0.5, 1.0) | [CA:284](src/criterios_adoptados.py:284) |
| `k_v` | 0.0 | declarado | (0.0, 0.5) | [CA:318](src/criterios_adoptados.py:318) |
| `pendiente_relleno_trasdos_i` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 10.0) ° | [CA:335](src/criterios_adoptados.py:335) |
| `inclinacion_muro_beta` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 10.0) ° | [CA:364](src/criterios_adoptados.py:364) |
| `friccion_muro_suelo_delta` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 22.7) ° | [CA:384](src/criterios_adoptados.py:384) |
| `punto_aplicacion_incremento_sismico` | `None` | **vacío — bloquea el momento de volteo sísmico** | (0.333, 0.6)·H | [CA:408](src/criterios_adoptados.py:408) |
| `homogeneidad_serie_fen` | `None` | **vacío — bloquea el Q de diseño de todos los puntos** | — | [CA:433](src/criterios_adoptados.py:433) |
| `umbral_area_quebrada_importante_ha` | `None` | **vacío — bloquea el TR de toda la Familia A** | — | [CA:452](src/criterios_adoptados.py:452) |
| `n_manning_hdpe` | (0.010, 0.013) | declarado | (0.010, 0.013) | [CA:561](src/criterios_adoptados.py:561) |
| `v_max_concreto_eleccion` | `None` | **OPCIONAL — no bloquea nada.** Sin declarar, V3 aplica el techo `[N]` de 6.0 m/s de la Tabla N° 10 y el criterio no se registra como usado. Declarándolo se baja ese techo y la `Verificacion` lo atribuye a esta clave. Único criterio del archivo que se lee con `valor_si_declarado()` en vez de `valor()` | (3.0, 6.0) m/s | [CA:599](src/criterios_adoptados.py:599) |
| `TW_receptor` | `None` | **vacío** | — | [CA:717](src/criterios_adoptados.py:717) |
| `long_max_cuneta` | 200.0 m | declarado | (200.0, 250.0) | [CA:728](src/criterios_adoptados.py:728) |
| `remanso_derecho_via` | `None` | **vacío — bloquea V5 para todo punto** | — | [CA:752](src/criterios_adoptados.py:752) |
| `TR_evento_extremo` | `None` | **vacío — bloquea V8 para todo punto** | — | [CA:776](src/criterios_adoptados.py:776) |
| `phi_relleno_trasdos` | `None` | **vacío** | (30.0, 38.0) ° | [CA:797](src/criterios_adoptados.py:797) |
| `c_phi_fundacion` | `None` | **vacío** | — | [CA:808](src/criterios_adoptados.py:808) |
| `capacidad_portante_adm` | `None` | **vacío** | — | [CA:819](src/criterios_adoptados.py:819) |
| `Mw_licuefaccion` | `None` | **vacío — bloquea la evaluación de licuefacción** | — | [CA:828](src/criterios_adoptados.py:828) |
| `demanda_sismica_licuefaccion` | 1000 años | declarado | (475, 1000) | [CA:840](src/criterios_adoptados.py:840) |
| `peso_especifico_relleno_kn_m3` | `None` | **vacío — bloquea el término ΣW de V7** | (17.0, 20.0) kN/m³ | [CA:949](src/criterios_adoptados.py:949) |
| `talud_terraplen` | `None` | **vacío — bloquea la longitud del conducto en 7.B** | — | [CA:977](src/criterios_adoptados.py:977) |
| `espesor_proteccion_salida` | 1.75·d50 | declarado | (1.5, 2.0) | [CA:1015](src/criterios_adoptados.py:1015) |
| `longitud_proteccion_salida` | `None` | **vacío — completa el diseño de la Fase 6** | — | [CA:1026](src/criterios_adoptados.py:1026) |
| `angulo_aletas` | `None` | **vacío** | — | [CA:1044](src/criterios_adoptados.py:1044) |
| `factores_carga_aashto` | `None` | **vacío — bloquea toda combinación de carga** | — | [CA:1058](src/criterios_adoptados.py:1058) |
| `peso_especifico_concreto_kn_m3` | `None` | **vacío — bloquea el peso propio del cabezal** | (23.5, 24.5) kN/m³ | [CA:1087](src/criterios_adoptados.py:1087) |
| `predimensionamiento_cabezal` | `None` | **vacío — bloquea la estabilidad automática** | — | [CA:1108](src/criterios_adoptados.py:1108) |
| `N_cq_N_gammaq_meyerhof` | `None` | **vacío — bloquea la capacidad portante en talud** | — | [CA:1136](src/criterios_adoptados.py:1136) |
| `metodo_estabilidad_global` | `None` | **vacío — bloquea E4 y E5 de Sec. 9.3** | — | [CA:1167](src/criterios_adoptados.py:1167) |
| `recubrimiento_aashto_mm` | `None` | **vacío — bloquea la regla del mayor (Sec. 0.2)** | — | [CA:1189](src/criterios_adoptados.py:1189) |
| `cortante_alto_muro_e060_art_11_10_10_2` | `None` | **vacío — bloquea el escalón de ρ a 0.0025 (E.060 Art. 11.10.10.2)** | — | [CA:1214](src/criterios_adoptados.py:1214) |
| `procedimiento_flexion_corte_aashto_sec5` | `None` | **vacío — bloquea el dimensionado del refuerzo** | — | [CA:1266](src/criterios_adoptados.py:1266) |

De los 33, **26 están sin valor**: invocarlos lanza `CriterioPendienteError` y
detiene el cálculo. Solo 7 tienen valor declarado (`F_pga`,
`factor_muro_eleccion`, `k_v`, `n_manning_hdpe`, `long_max_cuneta`,
`demanda_sismica_licuefaccion`, `espesor_proteccion_salida`).

---

## 13. Recuento

| Bloque | Filas con cita |
|---|---|
| §1 Manual de Hidrología | 30 |
| §2 Manual de Suelos | 13 |
| §3 Manual de Puentes | 21 |
| §4 E.050 | 16 |
| §5 E.060 | 13 |
| §6 EG-2013 | 13 |
| §7 HDS-5 | 15 |
| §8 AASHTO LRFD | 11 |
| §9 Normas de producto ASTM/AASHTO | 11 |
| §10 E.030 (solo referencia) | 4 |
| §10-bis WSDOT Hydraulics Manual | 2 |
| §11 Sin PDF externo (hoja de ruta + otras fuentes) | 14 + 14 |

Distribución de los 46 criterios de `criterios_adoptados.py`:
**0 `[N]`** ·
**1 `[N→]`** (`resguardo_HW_subrasante`) ·
**1 `[S]`** (`PERFIL_SUELO_PRESUNTO`) ·
**14 `[C]`** ·
**30 `[A]`** (§12).

> **La distribución anterior decía 45 criterios, 11 `[C]` y 32 `[A]`, y estaba
> desactualizada respecto al código** — no por esta revisión, que no cambia
> ninguna etiqueta: `v_max_hdpe` y `v_max_tmc` ya eran `[C]` y siguen siéndolo.
> Lo único que cambió en ellos es que pasaron de `[C]` **sin valor** a `[C]`
> **con cita cerrada** (§10-bis). Los números de arriba son ahora los que
> devuelve el propio archivo.

Más **3 `[S]` de corredor** en `src/datos_sitio.py` (`PGA_roca_B`,
`ZONA_SISMICA_LA_UNION`, `Z_E030`) y **1 `[S]` por punto** convertido en
columna del CSV (`NF_profundidad_m`).

> **Que no quede ningún `[N]` en `criterios_adoptados.py` es el resultado
> buscado, no una casualidad.** Ese archivo es, por definición, el de lo que
> NO es exigencia normativa verificada. Los tres `[N]` que tenía eran
> exactamente las tres entradas mal clasificadas: dos datos de sitio y una
> tabla normativa mezclada con la elección de su fila.

### Puntos que la verificación debería mirar primero

1. **Las filas marcadas ⚠ sin numeral que viven en `constantes_normativas.py`.**
   Ese archivo admite solo `[N]` "con numeral verificado" (su propio docstring,
   [CN:6-8](src/constantes_normativas.py:6)). Esta revisión cerró cuatro:
   `COMPACTACION_CORONA`, `COMPACTACION_CUERPO` (num. 3.2.1, 3.2.2, 3.3 y
   9.1(1)) y `CALICATAS_POR_KM`, `ESPACIAMIENTO_PERFIL_KM` (num. 4.2, Cuadro
   4.1) — ver la marca ⟳ en §2. `G` se resolvió por otra vía: dejó de ser una
   constante sin numeral porque se separó en dos — `G_LAUSHEY = 9.8` con su
   numeral propio (4.1.1.3.7 c), uso exclusivo de M6) y la gravedad genérica
   de M4, que salió del archivo por completo hacia `constantes_fisicas.py`
   (constante física universal, no una cita normativa — no necesita numeral,
   igual que π). Siguen sin numeral: `SPT_ESPACIAMIENTO`, `K_FRICCION_SI`,
   `h_o`, `Ks`, `D_MAX`/`D_PASO`. Eran 11 en la revisión anterior:
   `ZONA_SISMICA_LA_UNION`/`Z_E030` habían salido del archivo por no ser
   constantes normativas, no por conseguir el numeral que les faltaba.
2. **`D_MAX` lleva la palabra "VERIFICAR" escrita en el propio código**
   ([CN:86](src/constantes_normativas.py:86)) y el criterio homólogo repite la
   advertencia ([CA:775-777](src/criterios_adoptados.py:775)). Los tres topes
   son los que descartan materiales enteros.
3. **`Ks` es una cita que se declara a sí misma como no-tabla**
   ([CN:74](src/constantes_normativas.py:74)): el código dice que NO figura en
   la Tabla A.1 y que "proviene de la formulación". Hay que encontrar de dónde,
   exactamente, dentro de HDS-5.
4. **La doble definición declarada** ([CN:12-24](src/constantes_normativas.py:12)):
   `D_INICIO`/`D_PASO`/`D_MAX`, `HDS5_INLET` y `H_RELLENO_MIN` existen a la vez en
   los dos archivos. Verificar los dos lados y confirmar que dicen lo mismo.
5. ~~**La excepción de Clase F**~~ **RESUELTA, y en contra: la regla no existe.**
   Verificado contra AASHTO LRFD 9.ª ed. (2020) — Art. 3.10.3.1, comentario
   C3.10.3.1 y tablas de clase de sitio. No era la diferencia entre articulado
   y comentario: no estaba en ninguno de los dos. El uso de factores de sitio
   tabulados pasó a **adopción declarada `[A]`** del proyectista, sin respaldo
   normativo, y la memoria debe decirlo con esas palabras
   ([CA:256](src/criterios_adoptados.py:256), §0.5).

---

## 14. Vacíos normativos VERIFICADOS

Un vacío verificado no es lo mismo que una cita pendiente, y mezclarlos es
justamente lo que este manifiesto existe para impedir. Una cita pendiente dice
«el valor está en tal norma y falta ir a buscarlo»; un vacío verificado dice
«se fue a buscar a todas las fuentes donde podía estar, y **no está en
ninguna**». Lo segundo es un hallazgo con la misma fuerza que un número, y se
registra con su cita textual, porque es lo que un revisor necesita para no
repetir la búsqueda ni para pedir que se «complete» algo que no existe.

Las filas de los bloques anteriores marcadas **Afirmación negativa** son piezas
de estos vacíos; aquí quedan consolidadas por criterio.

### 14.a. `h_relleno_min_concreto_tmc` — altura mínima de relleno sobre la clave (concreto y TMC)

**Estado: vacío verificado. Búsqueda cerrada en las tres fuentes donde podía
estar.** El criterio sigue en `valor=None` y sigue `[C]`; lo que cambió es que
su `fuente` ya no promete un valor que nadie puede extraer
([CA:1054-1088](src/criterios_adoptados.py:1054)).

| # | Dónde se buscó | Qué se encontró | Cita |
|---|---|---|---|
| 1 | **Normas de producto** — AASHTO M 170M, AASHTO M 36, ASTM A760 | **No contienen alturas de relleno admisibles.** Su **Nota 1** lo excluye de forma expresa: son especificaciones de **fabricación y compra**, y no cubren encamado, relleno ni la relación entre carga de cobertura y clase o espesor. **M 170M clasifica por D-load (resistencia), no por altura** | Nota 1 de cada norma; ver §9 |
| 2 | **Manual de Puentes** (MTC, RD 041-2016-MTC/14) | **Nunca incorporó la Sección 12 de AASHTO LRFD** (*Buried Structures and Tunnel Liners*): el índice **salta de 2.11** (Muros de Contención y Estribos) **a 2.12** (Disposiciones Constructivas). Vacío absoluto sobre conductos enterrados | índice 2.11 → 2.12; ver §3 |
| 3 | **EG-2013, Capítulo V** | **HDPE sí**, concreto y TMC **no**. Las Secciones 505, 506 y 507 solo regulan colocación y compactación y remiten a la Sección 502, que tampoco fija altura mínima de diseño. Las remisiones cierran el circuito hacia (1) | 508.07, pág. 982; 506.02, pág. 959; 507.05/.06/.08, págs. 969-970; ver §6 |

**Lo único que el EG-2013 sí fija, literal** (Subsección 508.07, pág. 982):

> «La altura de relleno mínimo desde la clave de la tubería hasta el nivel de
> la subrasante será de 0,30 m.»

Vale para HDPE, y su magnitud es **exactamente la que calcula V7**: cota de
subrasante menos cota de clave. Por eso `H_RELLENO_MIN["hdpe"] = 0.30`
([CN:160](src/constantes_normativas.py:160)) es `[N]` puro y entra al catálogo
sin criterio adoptado de por medio, mientras concreto y TMC comparten el vacío.

#### ⚠ Trampa de vocabulario, anotada para que nadie la vuelva a pisar

El Manual de Puentes **sí** usa la palabra «recubrimiento» para alcantarillas,
en la **Tabla 2.9.1.5.5.3-1 (pág. 378)**, y da **2.0 in / 50 mm**. Ese número
**no sirve aquí**: es el recubrimiento de **concreto sobre el acero de
refuerzo**, no la altura de relleno de tierra sobre la clave. Son dos conceptos
que comparten palabra en español y no tienen ninguna relación. Quien busque
«recubrimiento» en el Manual va a encontrar esa tabla primero, y usarla sería
fijar la rasante de todos los puntos de concreto con un dato de otra cosa.

#### Qué puede cerrar el vacío

Ninguna lectura: las dos salidas son **decisiones de proyecto**, y cualquiera
de las dos convierte el criterio de `[C]` en `[A]`, porque deja de haber fuente
que lo cubra.

- **(a) Analogía declarada** con el 0.30 m que EG-2013 508.07 fija para HDPE,
  escrita como adopción del proyectista y no como cita.
- **(b) Cálculo estructural** de cobertura mínima: AASHTO LRFD Sec. 12 — que el
  Manual de Puentes no incorpora, punto (2) — o clase D-load con factor de
  cama. Es la misma salida que ya declara `clases_producto_por_relleno`
  ([CA:1123](src/criterios_adoptados.py:1123)) y la que M8 difiere al
  expediente ([M8:326](src/modulos/M8_estructural.py:326)).

**Lo que NO se hace:** declarar un número para concreto o TMC mientras no se
tome una de esas dos decisiones. Hoy el vacío detiene el tamizado 7.A en esos
dos materiales, y esa detención es el comportamiento correcto.
