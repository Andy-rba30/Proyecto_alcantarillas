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
| `G = 9.8` m/s² | **⚠ sin numeral** en CN; M4 lo atribuye al "Manual de Hidrología MTC" | Manual de Hidrología | [CN:34](src/constantes_normativas.py:34), [M4:92-94](src/modulos/M4_control.py:92) | [N] |
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
| `NUMERAL_V3 = "Tabla Nº 10 (num. 4.1.1.3.6)"` (V3, velocidad máxima) | Tabla N° 10, num. 4.1.1.3.6 | Manual de Hidrología | [M5:108](src/modulos/M5_verificaciones.py:108) | [N] |
| `NUMERAL_LAUSHEY = "4.1.1.3.7 c)"`; d50 = V²/(K·G), pág. 80 | 4.1.1.3.7 c) | Manual de Hidrología | [M6:6](src/modulos/M6_proteccion.py:6), [M6:42](src/modulos/M6_proteccion.py:42) | [N] |
| `NUMERAL_FASE_10 = "Fase 10 (num. 4.1.2.1 d), pag. 178)"` | 4.1.2.1 d), pág. 178 | Manual de Hidrología | [M10:9](src/modulos/M10_espaciamiento.py:9), [M10:61](src/modulos/M10_espaciamiento.py:61) | [N] |
| `n_manning_hdpe = (0.010, 0.013)` — rango del concreto por analogía | "Analogía a Tabla N° 09 (concreto, tubo recto)" | Manual de Hidrología (analogía) | [CA:485](src/criterios_adoptados.py:485) | [A] |
| `v_max_concreto_eleccion = None` — elección dentro del rango 3.0–6.0 | Tabla N° 10 (num. 4.1.1.3.6): el rango es [N], la elección no está normada | Manual de Hidrología | [CA:523](src/criterios_adoptados.py:523) | [A] |
| `long_max_cuneta = 200.0` m (se adopta la fila "muy lluviosa" por FEN) | num. 4.1.2.1 d), pág. 178 | Manual de Hidrología | [CA:639](src/criterios_adoptados.py:639) | [A] |
| `umbral_area_quebrada_importante_ha = None` — **afirmación negativa**: el Manual no define "quebrada importante"/"menor" por umbral de área, longitud ni caudal | Tabla N° 02 (num. 3.6) entrega R y n pero no la regla de asignación | Manual de Hidrología | [CA:434](src/criterios_adoptados.py:434) | [A] |

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
| `COMPACTACION_CORONA = 0.95` (0.30 m superiores, capas de 0.15 m) | **⚠ sin numeral** | Manual de Suelos | [CN:101](src/constantes_normativas.py:101) | [N] |
| `COMPACTACION_CUERPO = 0.90` (capas de hasta 0.30 m) | **⚠ sin numeral** | Manual de Suelos | [CN:102](src/constantes_normativas.py:102) | [N] |
| `CALICATAS_POR_KM` (autopista/dual/1ª clase 4; 2ª clase 3; 3ª clase 2; bajo volumen 1) | **⚠ sin numeral** | Manual de Suelos | [CN:104-105](src/constantes_normativas.py:104) | [N] |
| `ESPACIAMIENTO_PERFIL_KM = 4.0` (nivel perfil) | **⚠ sin numeral** | Manual de Suelos | [CN:106](src/constantes_normativas.py:106) | [N] |
| `resguardo_HW_subrasante = "segun_CBR"` — la tabla 4.5.4 aplicada al HW de avenida, **por analogía** (el numeral regula el nivel freático, no un nivel transitorio) | num. 4.5.4 y 9.1(3) | Manual de Suelos | [CA:616](src/criterios_adoptados.py:616) | [N→] |
| `NUMERAL_V4 = "5.1 (Manual de Suelos, num. 4.5.4 y 9.1(3))"` | 4.5.4 y 9.1(3) | Manual de Suelos | [M5:109](src/modulos/M5_verificaciones.py:109) | [N→] |
| `resguardo_por_cbr()` — tabla de CBR aplicada en V4 | num. 4.5.4 | Manual de Suelos | [M5:225-226](src/modulos/M5_verificaciones.py:225) | [N] |
| Tamizado 7.A: CBR → resguardo, misma tabla de Sec. 5.1 | num. 4.5.4 | Manual de Suelos | [M7:82](src/modulos/M7_geometria.py:82) | [N] |
| ↻ `NF_profundidad_m` — **ya no es un valor declarado**: es columna del CSV, medida en cada cruce, y hoy viene vacía en las cuatro filas | El 1.4 m que se declaraba no tenía numeral del Manual: citaba la *hoja de ruta* (Sec. 0.5 num. 105; Fase 8 num. 545; Fase 9 num. 582). Siendo dato por punto, **no hay nada que verificar contra un PDF**: se verifica contra el estudio geotécnico del expediente, cruce por cruce | Estudio geotécnico del expediente (antes: "Manual de Suelos MTC / caracterización geotécnica del sitio") | [modelos.py:323](src/modelos.py:323), [M0:86](src/modulos/M0_carga.py:86) | [S] |

---

## 3. Manual de Puentes (MTC, RD 041-2016-MTC/14)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `GAMMA_AGUA_KN_M3 = 9.81` kN/m³ (subpresión) | num. 2.4.3.8.2 | Manual de Puentes | [CN:35](src/constantes_normativas.py:35) | [N] |
| `SOBRECARGA_TRASDOS_H_EQ = 0.60` m de relleno equivalente | 2.1.4.3.9, pág. 91 | Manual de Puentes | [CN:154](src/constantes_normativas.py:154), [CN:180](src/constantes_normativas.py:180) | [N] |
| `CARGA_VIVA = "HL-93"` | 2.4.3.2.2.1 | Manual de Puentes | [CN:155](src/constantes_normativas.py:155) | [N] |
| `NQ_ZAPATA_EN_TALUD = 0.0` (zapata próxima a talud) | 2.8.1.3.1.2c, págs. 272-273 | Manual de Puentes | [CN:156](src/constantes_normativas.py:156), [CN:181](src/constantes_normativas.py:181) | [N] |
| `F_PGA_TABLA = {C: 1.0, D: 1.0, E: 0.9}` para PGA ≥ 0.50 | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CN:157-159](src/constantes_normativas.py:157) | [N] |
| `NUMERAL_K_H0 = "2.8.1.1.14.2"` (k_h0 = A_s) | 2.8.1.1.14.2 | Manual de Puentes | [CN:182](src/constantes_normativas.py:182), [M9:28](src/modulos/M9_cabezal.py:28), [M9:255](src/modulos/M9_cabezal.py:255) | [N] |
| `COMBINACIONES_AASHTO = ("Resistencia I", "Servicio I", "Evento Extremo I")` — solo los **nombres** | 2.4.5.3 (AASHTO LRFD Sec. 3.4.1), págs. 140-143 | Manual de Puentes (vía AASHTO) | [CN:178-179](src/constantes_normativas.py:178) | [N] |
| ↻ `PGA_roca_B = 0.50` g, Tr = 1000 años, roca Clase B — **el mapa es normativo, la lectura es de este sitio** | Apéndice A3, mapa "Isoaceleraciones Espectrales Suelo Tipo B, AASHTO 2014 (Roca). Periodo estructural 0.0 seg (PGA)". Verificar además **sobre qué punto del mapa se leyó**: el expediente no lo registra (pendiente 1.4 de la hoja de ruta) | Manual de Puentes | [DS:128](src/datos_sitio.py:128), [M9:220](src/modulos/M9_cabezal.py:220) | [S] |
| ↻ `FACTOR_MURO_TABLA = {rígido: 1.0, desplazable: 0.5}` — los **dos** valores de tabla del numeral | numeral 2.8.1.1.14.2 | Manual de Puentes | [CN:165](src/constantes_normativas.py:165), [CN:169](src/constantes_normativas.py:169) | [N] |
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

---

## 4. E.050 Suelos y Cimentaciones (RM 406-2018-VIVIENDA)

Toda la tabla de factores de seguridad de la Fase 9 sale de este documento.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `FS["capacidad_portante"] = {estático: 3.00, sísmico: 2.50}` | Art. 21 (21.1/21.2), pág. 34 | E.050 | [CN:186](src/constantes_normativas.py:186), [CN:193](src/constantes_normativas.py:193) | [N] |
| `FS["volteo"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 a), pág. 72 | E.050 | [CN:187](src/constantes_normativas.py:187), [CN:194](src/constantes_normativas.py:194) | [N] |
| `FS["deslizamiento"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 a), pág. 72 | E.050 | [CN:188](src/constantes_normativas.py:188), [CN:195](src/constantes_normativas.py:195) | [N] |
| `FS["estabilidad_global"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 b), pág. 72 | E.050 | [CN:189](src/constantes_normativas.py:189), [CN:196](src/constantes_normativas.py:196) | [N] |
| `FS["talud"] = {estático: 1.50, sísmico: 1.25}` | Art. 30.3, pág. 39 | E.050 | [CN:190](src/constantes_normativas.py:190), [CN:197](src/constantes_normativas.py:197) | [N] |
| `NUMERAL_C_PHI`: en cohesivos φ=0, en friccionantes c=0 (prohibido sumar) | Art. 20, pág. 33 | E.050 | [CN:199](src/constantes_normativas.py:199), [M9:926-927](src/modulos/M9_cabezal.py:926), [M9:979](src/modulos/M9_cabezal.py:979) | [N] |
| `NUMERAL_ZAPATA_TALUD_E050`: doble verificación (inclinación de superficie y de base + estabilidad global del talud) | Art. 30.1-30.2 | E.050 | [CN:200](src/constantes_normativas.py:200), [M9:1056](src/modulos/M9_cabezal.py:1056) | [N] |
| `SPT_PROF_MIN = 15.0` m | Art. 38 | E.050 | [CN:202](src/constantes_normativas.py:202) | [N] |
| `SPT_ESPACIAMIENTO = 1.0` m entre ensayos | **⚠ sin numeral propio** (hereda el Art. 38 de la línea anterior; `clase_sitio` sí lo cita como Art. 38) | E.050 | [CN:203](src/constantes_normativas.py:203), [CA:264-265](src/criterios_adoptados.py:264) | [N] |
| `e1_capacidad_portante()` ≥ 3.00 / 2.50 | Art. 21.1/21.2 | E.050 | [M9:882](src/modulos/M9_cabezal.py:882) | [N] |
| `e2_volteo()` ≥ 1.50 / 1.25 | num. 39.13.6 a) | E.050 | [M9:903](src/modulos/M9_cabezal.py:903) | [N] |
| `e3_deslizamiento()` ≥ 1.50 / 1.25 | num. 39.13.6 a) | E.050 | [M9:903](src/modulos/M9_cabezal.py:903) | [N] |
| `e4_estabilidad_global()` ≥ 1.50 / 1.25 | num. 39.13.6 b) | E.050 | [M9:944](src/modulos/M9_cabezal.py:944) | [N] |
| `e5_estabilidad_talud()` ≥ 1.50 / 1.25 | Art. 30.3 | E.050 | [M9:962-963](src/modulos/M9_cabezal.py:962) | [N] |
| `c_phi_fundacion = None` — la obligación de usar solo uno (φ=0 o c=0) | Art. 20 | E.050 | [CA:719](src/criterios_adoptados.py:719) | [A] |
| `clase_sitio` — el SPT que lo reemplazaría: perforaciones ≥ 15 m, ensayos cada 1 m | Art. 38 | E.050 | [CA:264-265](src/criterios_adoptados.py:264) | [C] |
| `metodo_estabilidad_global = None` — **afirmación negativa**: E.050 fija el umbral, no el método | Art. 30.3 y num. 39.13.6 b) | E.050 | [CA:1078](src/criterios_adoptados.py:1078) | [A] |

---

## 5. E.060 Concreto Armado

Entra al proyecto solo por la **excepción declarada de durabilidad y
recubrimientos** (Vía 1 de Sec. 0.2); el diseño estructural es de AASHTO.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `SULFATOS`: SO₄ 0.00–0.10 % → sin exigencia | Tabla 4.4 | E.060 | [CN:207](src/constantes_normativas.py:207) | [N] |
| `SULFATOS`: 0.10–0.20 % → cemento II/IP(MS)/IS(MS), a/c 0.50, f'c 28 MPa | Tabla 4.4 | E.060 | [CN:208](src/constantes_normativas.py:208) | [N] |
| `SULFATOS`: 0.20–2.00 % → cemento V, a/c 0.45, f'c 31 MPa | Tabla 4.4 | E.060 | [CN:209](src/constantes_normativas.py:209) | [N] |
| `SULFATOS`: > 2.00 % → cemento V + puzolana, a/c 0.45, f'c 31 MPa | Tabla 4.4 | E.060 | [CN:210](src/constantes_normativas.py:210) | [N] |
| `CLORUROS_EXTERNOS = {a/c máx 0.40, f'c mín 35 MPa}` | Art. 4.2 / 4.4 | E.060 | [CN:212](src/constantes_normativas.py:212) | [N] |
| `RECUBRIMIENTO`: contra suelo 70 mm; suelo/intemperie ≥ 3/4" 50 mm; ≤ 5/8" 40 mm | Art. 7.7.1, pág. 54 | E.060 | [CN:213-215](src/constantes_normativas.py:213), [M9:1129](src/modulos/M9_cabezal.py:1129) | [N] |
| `AMBIENTE_CORROSIVO_AUMENTAR` — el artículo dice "aumentar adecuadamente" y **no fija cuánto** | Art. 7.7.5.1 | E.060 | [CN:216-219](src/constantes_normativas.py:216), [M9:1196](src/modulos/M9_cabezal.py:1196) | [N] |
| `CUANTIA_MIN_MURO = {horizontal 0.0020, vertical 0.0015}` — **referencia declarada, no gobierna** | Art. 14.3.1, pág. 133 | E.060 | [CN:226-227](src/constantes_normativas.py:226), [M9:1211](src/modulos/M9_cabezal.py:1211) | [N] |
| `ESPESOR_TEMPERATURA_DOS_CARAS = 0.250` m (refuerzo en dos caras) | Art. 14.8.3 | E.060 | [CN:228-229](src/constantes_normativas.py:228), [M9:1250](src/modulos/M9_cabezal.py:1250) | [N] |
| `ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0` (≤ 3h) | Art. 14.3.3 | E.060 | [CN:230](src/constantes_normativas.py:230), [M9:1276-1277](src/modulos/M9_cabezal.py:1276) | [N] |
| `ESPACIAMIENTO_MAX_ABSOLUTO = 0.400` m (400 mm) | Art. 14.3.3 | E.060 | [CN:231-232](src/constantes_normativas.py:231) | [N] |
| `CICLOPEO_FC_MATRIZ_MIN = 10.0` MPa | Art. 22.10, págs. 194-195 | E.060 | [CN:235](src/constantes_normativas.py:235), [M9:1303](src/modulos/M9_cabezal.py:1303) | [N] |
| `CICLOPEO_FRACCION_PIEDRA_MAX = 0.30` del volumen | Art. 22.10, págs. 194-195 | E.060 | [CN:236-237](src/constantes_normativas.py:236) | [N] |

---

## 6. EG-2013 — Especificaciones Técnicas Generales para Construcción, Sección 500

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `H_RELLENO_MIN["hdpe"] = 0.30` m (clave a subrasante) | 508.07 / 508.08 | EG-2013 | [CN:110](src/constantes_normativas.py:110), [M7:20](src/modulos/M7_geometria.py:20), [M7:259-260](src/modulos/M7_geometria.py:259) | [N] |
| `H_RELLENO_MIN["concreto"] = None` — **afirmación negativa**: EG-2013 no lo fija, remite a AASHTO M-170M | AASHTO M-170M (clases I a V) | EG-2013 → norma de producto | [CN:111](src/constantes_normativas.py:111) | [N]/[C] |
| `H_RELLENO_MIN["tmc"] = None` — **afirmación negativa**: EG-2013 no lo fija, remite a la norma de producto | ASTM A-807 / AASHTO M36 | EG-2013 → norma de producto | [CN:112](src/constantes_normativas.py:112) | [N]/[C] |
| `SUBSECCION`: concreto simple 505, concreto reforzado 506, TMC 507, HDPE 508 | 505 / 506 / 507 / 508 | EG-2013 | [CN:114-115](src/constantes_normativas.py:114), [M11:697](src/modulos/M11_reporte.py:697) | [N] |
| `SECCION_CABEZALES = "503"` (concreto estructural; + 504 acero) | 503 (+504) | EG-2013 | [CN:116](src/constantes_normativas.py:116) | [N] |
| `CAMA_RELLENO_LATERAL["concreto_simple"]`: cama Clase F (f'c = 14 MPa) ≥ 15 cm; Clase F hasta ≥ 1/4 del D exterior; relleno Sec. 502 ≥ 95 % MDS | 505.03/.07/.10/.11, págs. 950-951 | EG-2013 | [CN:124-129](src/constantes_normativas.py:124) | [N] |
| `CAMA_RELLENO_LATERAL["concreto_reforzado"]`: subbase granular (Sec. 402) ≥ 15 cm, ≥ 95 % MDS; subbase hasta ≥ 1/6 del D exterior; relleno Sec. 502 | 506.03/.07/.10/.11, págs. 959-960 | EG-2013 | [CN:130-135](src/constantes_normativas.py:130) | [N] |
| `CAMA_RELLENO_LATERAL["tmc"]`: subbase ≥ 15 cm, ≥ 95 % MDS con arena suelta de 12 mm; capas de 15-20 cm ≥ 90 % base/cuerpo y ≥ 95 % corona | 507.06/.07/.08, pág. 970 | EG-2013 | [CN:136-142](src/constantes_normativas.py:136) | [N] |
| `CAMA_RELLENO_LATERAL["hdpe"]`: arena gruesa, capas de 15 cm, espesor 15-30 cm (30 cm en roca o suelo blando); capas alternadas simétricas de 15 cm a > 95 %, los 30 cm superiores a ≥ 100 %; prohibida la anegación | 508.05/.07, págs. 981-982 | EG-2013 | [CN:143-150](src/constantes_normativas.py:143) | [N] |
| `NUMERAL_8_1 = "Sec. 8.1 (EG-2013 Seccion 500)"` (cama y relleno lateral) | Sección 500 | EG-2013 | [M8:98](src/modulos/M8_estructural.py:98), [M8:172](src/modulos/M8_estructural.py:172) | [N] |
| `NUMERAL_9_1 = "Sec. 9.1 (EG-2013 num. 503.01, pag. 905)"` — cabezales y aletas, concreto estructural, partida específica | 503.01, pág. 905 | EG-2013 | [M9:163](src/modulos/M9_cabezal.py:163), [M9:1364](src/modulos/M9_cabezal.py:1364) | [N] |
| `h_relleno_min_concreto_tmc = None` — EG-2013 fija 0.30 m para HDPE pero **no** para concreto ni TMC | 508.07 / 508.08 (lo que sí fija) | EG-2013 | [CA:780](src/criterios_adoptados.py:780) | [C] |
| Nota constructiva: el equipo pesado no circula sobre el conducto antes de que el relleno alcance 0.30 m | Sec. 7.A de la hoja de ruta, apoyada en EG-2013 | EG-2013 | [CA:794-796](src/criterios_adoptados.py:794) | [N] |

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
| `K_FRICCION_SI = 19.62` — H = (1 + ke + 19.62·n²·L/R^(4/3))·V²/(2g); "29 es el valor inglés" | **⚠ sin numeral**: se cita la ecuación de control de salida, no un apartado | HDS-5 / literatura FHWA | [CN:78-80](src/constantes_normativas.py:78), [M4:79-96](src/modulos/M4_control.py:79) | [N] |
| `h_o = max(TW, (y_c + D)/2)` | **⚠ sin numeral** | HDS-5 (control de salida) | [CN:81](src/constantes_normativas.py:81), [M4:80-82](src/modulos/M4_control.py:80) | [N] |
| `hds5_embocadura_hdpe = {K:0.0098, M:2.00, c:0.0398, Y:0.67, Ks:-0.5}` — fila del **concreto** aplicada a HDPE de interior liso a ras del muro | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CA:467](src/criterios_adoptados.py:467) | [C] |
| `ke_entrada = 0.5` (square edge with headwall) | **⚠ sin numeral de tabla**: "tablas de coeficiente de pérdida de entrada" | HDS-5 | [CA:541](src/criterios_adoptados.py:541) | [C] |
| `geometria_control_salida = "seccion_llena"` (A = πD²/4, R = D/4, V = Q/A) | Cap. III — control de salida a sección llena | HDS-5 | [CA:568](src/criterios_adoptados.py:568) | [C] |
| `HW_D_max = 1.5` | **⚠ sin numeral**: "HDS-5 (FHWA), práctica corriente" | HDS-5 | [CA:605](src/criterios_adoptados.py:605) | [C] |
| Alternativa citada si el barril no llena: procedimiento de barril parcialmente lleno | Cap. III | HDS-5 | [CA:595-597](src/criterios_adoptados.py:595), [M4:400](src/modulos/M4_control.py:400) | [C] |

---

## 8. AASHTO LRFD Bridge Design Specifications

Ninguna cita a AASHTO LRFD lleva hoy un valor numérico transcrito: **todas las
tablas quedaron sin extraer**. Este bloque es, casi entero, el inventario de lo
que falta traer del PDF.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `COMBINACIONES_AASHTO` — los tres **nombres** (Resistencia I, Servicio I, Evento Extremo I) | Sec. 3.4.1 (vía Manual de Puentes num. 2.4.5.3) | AASHTO LRFD | [CN:178-179](src/constantes_normativas.py:178), [M9:798-799](src/modulos/M9_cabezal.py:798) | [N] |
| `clase_sitio = "F_con_excepcion_periodo_corto"` — excepción para estructuras de periodo fundamental corto (≤ 0.5 s) | Art. 3.10.3.1 | AASHTO LRFD | [CA:262](src/criterios_adoptados.py:262) | [C] |
| ↳ verificación pendiente sobre esa misma cita: precisar si la excepción está en el **articulado** 3.10.3.1 o en el **comentario** C3.10.3.1 / nota a la tabla | Art. 3.10.3.1 vs. C3.10.3.1 | AASHTO LRFD | [CA:266-268](src/criterios_adoptados.py:266) | [C] |
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
| `h_relleno_min_concreto_tmc = None` (lado norma de producto) | AASHTO M-170M; ASTM A-807 / AASHTO M36 | ASTM / AASHTO | [CA:789-791](src/criterios_adoptados.py:789) | [C] |

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

## 11. Citas que NO apuntan a ninguno de los PDF

Se listan aparte para que nadie las busque en un documento normativo.

### 11.a. Referencias a la propia hoja de ruta (`docs/hoja_de_ruta_alcantarillas_v7.md`)

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
| `v_max_hdpe = None` | **Plastics Pipe Institute (PPI)** y **FHWA** — fuente identificada, valores sin extraer | [CA:502](src/criterios_adoptados.py:502) | [C] |
| `v_max_tmc = None` | **PPI** y **FHWA** — ídem | [CA:513](src/criterios_adoptados.py:513) | [C] |
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
justifica. Lo mismo ocurre con `v_max_concreto_eleccion` (rango `[N]`, elección
`[A]`), con `long_max_cuneta` (las dos filas son `[N]`, elegir la de 200 m es
`[A]`) y —desde esta revisión— con `factor_muro_eleccion`, que hasta ahora
mezclaba las dos mitades en un solo valor `[N]`.

**Y no confundir un `[A]` con un `[S]`.** Los dos son valores que no son
portables a otra obra, y ahí termina el parecido: un `[A]` es una decisión que
pudo ser otra, y por eso se defiende con el rango de sensibilidad; un `[S]` es
un hecho que se leyó o se midió, no admite rango, y se defiende con la
trazabilidad de la lectura. Antes de la quinta etiqueta, forzar el PGA o el
nivel freático dentro de `[A]` habría dicho que alguien los "adoptó".

### Los 32 criterios `[A]` del proyecto

| Criterio | Valor | Estado | Sensibilidad declarada | Archivo:línea |
|---|---|---|---|---|
| `F_pga` | 1.0 | declarado | (0.9, 1.0) | [CA:271](src/criterios_adoptados.py:271) |
| ↻ `factor_muro_eleccion` | 1.0 (fila rígida) | declarado | (0.5, 1.0) | [CA:284](src/criterios_adoptados.py:284) |
| `k_v` | 0.0 | declarado | (0.0, 0.5) | [CA:300](src/criterios_adoptados.py:300) |
| `pendiente_relleno_trasdos_i` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 10.0) ° | [CA:317](src/criterios_adoptados.py:317) |
| `inclinacion_muro_beta` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 10.0) ° | [CA:346](src/criterios_adoptados.py:346) |
| `friccion_muro_suelo_delta` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 22.7) ° | [CA:366](src/criterios_adoptados.py:366) |
| `punto_aplicacion_incremento_sismico` | `None` | **vacío — bloquea el momento de volteo sísmico** | (0.333, 0.6)·H | [CA:390](src/criterios_adoptados.py:390) |
| `homogeneidad_serie_fen` | `None` | **vacío — bloquea el Q de diseño de todos los puntos** | — | [CA:415](src/criterios_adoptados.py:415) |
| `umbral_area_quebrada_importante_ha` | `None` | **vacío — bloquea el TR de toda la Familia A** | — | [CA:434](src/criterios_adoptados.py:434) |
| `n_manning_hdpe` | (0.010, 0.013) | declarado | (0.010, 0.013) | [CA:485](src/criterios_adoptados.py:485) |
| `v_max_concreto_eleccion` | `None` | **vacío — bloquea V3 en concreto** | (3.0, 6.0) m/s | [CA:523](src/criterios_adoptados.py:523) |
| `TW_receptor` | `None` | **vacío** | — | [CA:628](src/criterios_adoptados.py:628) |
| `long_max_cuneta` | 200.0 m | declarado | (200.0, 250.0) | [CA:639](src/criterios_adoptados.py:639) |
| `remanso_derecho_via` | `None` | **vacío — bloquea V5 para todo punto** | — | [CA:663](src/criterios_adoptados.py:663) |
| `TR_evento_extremo` | `None` | **vacío — bloquea V8 para todo punto** | — | [CA:687](src/criterios_adoptados.py:687) |
| `phi_relleno_trasdos` | `None` | **vacío** | (30.0, 38.0) ° | [CA:708](src/criterios_adoptados.py:708) |
| `c_phi_fundacion` | `None` | **vacío** | — | [CA:719](src/criterios_adoptados.py:719) |
| `capacidad_portante_adm` | `None` | **vacío** | — | [CA:730](src/criterios_adoptados.py:730) |
| `Mw_licuefaccion` | `None` | **vacío — bloquea la evaluación de licuefacción** | — | [CA:739](src/criterios_adoptados.py:739) |
| `demanda_sismica_licuefaccion` | 1000 años | declarado | (475, 1000) | [CA:751](src/criterios_adoptados.py:751) |
| `peso_especifico_relleno_kn_m3` | `None` | **vacío — bloquea el término ΣW de V7** | (17.0, 20.0) kN/m³ | [CA:860](src/criterios_adoptados.py:860) |
| `talud_terraplen` | `None` | **vacío — bloquea la longitud del conducto en 7.B** | — | [CA:888](src/criterios_adoptados.py:888) |
| `espesor_proteccion_salida` | 1.75·d50 | declarado | (1.5, 2.0) | [CA:926](src/criterios_adoptados.py:926) |
| `longitud_proteccion_salida` | `None` | **vacío — completa el diseño de la Fase 6** | — | [CA:937](src/criterios_adoptados.py:937) |
| `angulo_aletas` | `None` | **vacío** | — | [CA:955](src/criterios_adoptados.py:955) |
| `factores_carga_aashto` | `None` | **vacío — bloquea toda combinación de carga** | — | [CA:969](src/criterios_adoptados.py:969) |
| `peso_especifico_concreto_kn_m3` | `None` | **vacío — bloquea el peso propio del cabezal** | (23.5, 24.5) kN/m³ | [CA:998](src/criterios_adoptados.py:998) |
| `predimensionamiento_cabezal` | `None` | **vacío — bloquea la estabilidad automática** | — | [CA:1019](src/criterios_adoptados.py:1019) |
| `N_cq_N_gammaq_meyerhof` | `None` | **vacío — bloquea la capacidad portante en talud** | — | [CA:1047](src/criterios_adoptados.py:1047) |
| `metodo_estabilidad_global` | `None` | **vacío — bloquea E4 y E5 de Sec. 9.3** | — | [CA:1078](src/criterios_adoptados.py:1078) |
| `recubrimiento_aashto_mm` | `None` | **vacío — bloquea la regla del mayor (Sec. 0.2)** | — | [CA:1100](src/criterios_adoptados.py:1100) |
| `procedimiento_flexion_corte_aashto_sec5` | `None` | **vacío — bloquea el dimensionado del refuerzo** | — | [CA:1125](src/criterios_adoptados.py:1125) |

De los 32, **25 están sin valor**: invocarlos lanza `CriterioPendienteError` y
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
| §11 Sin PDF externo (hoja de ruta + otras fuentes) | 14 + 14 |

Distribución de los 45 criterios de `criterios_adoptados.py`:
**0 `[N]`** ·
**1 `[N→]`** (`resguardo_HW_subrasante`) ·
**1 `[S]`** (`PERFIL_SUELO_PRESUNTO`) ·
**11 `[C]`** ·
**32 `[A]`** (§12).

Más **3 `[S]` de corredor** en `src/datos_sitio.py` (`PGA_roca_B`,
`ZONA_SISMICA_LA_UNION`, `Z_E030`) y **1 `[S]` por punto** convertido en
columna del CSV (`NF_profundidad_m`).

> **Que no quede ningún `[N]` en `criterios_adoptados.py` es el resultado
> buscado, no una casualidad.** Ese archivo es, por definición, el de lo que
> NO es exigencia normativa verificada. Los tres `[N]` que tenía eran
> exactamente las tres entradas mal clasificadas: dos datos de sitio y una
> tabla normativa mezclada con la elección de su fila.

### Puntos que la verificación debería mirar primero

1. **Las 10 filas marcadas ⚠ sin numeral que viven en `constantes_normativas.py`.**
   Ese archivo admite solo `[N]` "con numeral verificado" (su propio docstring,
   [CN:6-8](src/constantes_normativas.py:6)), y estas entraron sin él:
   `G`, `COMPACTACION_CORONA`, `COMPACTACION_CUERPO`, `CALICATAS_POR_KM`,
   `ESPACIAMIENTO_PERFIL_KM`, `SPT_ESPACIAMIENTO`, `K_FRICCION_SI`, `h_o`,
   `Ks`, `D_MAX`/`D_PASO`. Eran 11: `ZONA_SISMICA_LA_UNION`/`Z_E030` salieron
   del archivo en esta revisión, no por conseguir el numeral que les faltaba,
   sino porque nunca fueron constantes normativas.
   **Las restantes merecen la misma pregunta antes de buscarles numeral:**
   ¿falta el numeral, o falta la etiqueta? `CALICATAS_POR_KM` y
   `ESPACIAMIENTO_PERFIL_KM` son regla de campaña de ensayos, no valor de
   sitio; pero conviene mirarlas con las cinco etiquetas en la mano y no con
   cuatro.
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
5. **La excepción de Clase F** ([CA:266-268](src/criterios_adoptados.py:266)):
   el propio criterio pide precisar si AASHTO Art. 3.10.3.1 la trae en el
   articulado o solo en el comentario. Es la diferencia entre una cita normativa
   y una cita a un comentario no vinculante.
