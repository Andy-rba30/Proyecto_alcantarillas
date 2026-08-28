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
| `LUZ_MAX_ALCANTARILLA = 6.0` m (≥ 6.0 → puente) | 4.1.1.3.1 / 4.1.1.5.1 | Manual de Hidrología | [CN:53](src/constantes_normativas.py:53) | [N] |
| `DIAMETRO_MIN = 0.90` m | 4.1.1.3.4 a) | Manual de Hidrología | [CN:54](src/constantes_normativas.py:54) | [N] |
| `DIAMETRO_MIN_SELVA_ALTA = 1.22` m (48"; no aplica en costa) | 4.1.1.3.7 a) | Manual de Hidrología | [CN:55](src/constantes_normativas.py:55) | [N] |
| `Y_SOBRE_D_MAX = 0.75` (borde libre ≥ 25 %) | 4.1.1.3.7 b) | Manual de Hidrología | [CN:56](src/constantes_normativas.py:56) | [N] |
| ↻ `V_MIN = 0.25` m/s — **cita completada**: antes solo el numeral pelado. El párrafo **recomienda**, no prohíbe; V2 lo aplica como umbral duro por decisión conservadora del proyecto, y `NUMERAL_V2` lleva ese matiz hasta la memoria | num. 4.1.1.3.6, **pág. 76**, párrafo inmediatamente posterior a la Tabla N° 10 | Manual de Hidrología (MTC, RD 20-2011-MTC/14) | [CN:57-49](src/constantes_normativas.py:57), [M5:199](src/modulos/M5_verificaciones.py:199) | [N] |
| ↻ **Cita textual de lo que fija `V_MIN`** — «Se deberá verificar que la velocidad mínima del flujo dentro del conducto no produzca sedimentación que pueda incidir en una reducción de su capacidad hidráulica, **recomendándose** que la velocidad mínima sea igual a 0.25 m/s.» La razón es la **sedimentación**, no el desgaste: por eso el piso vale igual para todos los materiales, mientras el techo de `V_MAX` cambia con el revestimiento | num. 4.1.1.3.6, pág. 76 | Manual de Hidrología (MTC, RD 20-2011-MTC/14) | [CN:58-39](src/constantes_normativas.py:58), [M5:332-197](src/modulos/M5_verificaciones.py:332) | [N] |
| `LAUSHEY_K = 3.1` (d50 = V²/(3.1·g), métrico) | 4.1.1.3.7 c) | Manual de Hidrología | [CN:75](src/constantes_normativas.py:75) | [N] |
| ⟳ `G_LAUSHEY = 9.8` m/s² — uso exclusivo de M6 (Laushey) | 4.1.1.3.7 c) (la hoja de ruta escribe "g = 9.8 m/s²" junto a la fórmula de d50) | Manual de Hidrología | [CN:76-56](src/constantes_normativas.py:76) | [N] |
| ⟳ **Ya no vive aquí**: la gravedad genérica de M4 (tirante crítico, control de salida) es `constantes_fisicas.G = 9.81`, constante física universal, no una cita del Manual de Hidrología | — | (constante física, sin numeral que citar — igual que π) | [constantes_fisicas.py:29](src/constantes_fisicas.py:29) | — |
| `RIESGO_ADMISIBLE`: quebrada importante R=0.30, n=25 → TR 71 | Tabla N° 02, num. 3.6 | Manual de Hidrología | [CN:89-65](src/constantes_normativas.py:89) | [N] |
| `RIESGO_ADMISIBLE`: quebrada menor R=0.35, n=15 → TR 35 | Tabla N° 02, num. 3.6 | Manual de Hidrología | [CN:62,64](src/constantes_normativas.py:89) | [N] |
| `TR = 1/(1-(1-R)^(1/n))`, sin piso normativo | num. 3.6 (fórmula, no lista de TR) | Manual de Hidrología | [CN:66](src/constantes_normativas.py:66), [M1:62](src/modulos/M1_clasificacion.py:62) | [N] |
| `MANNING["metal_corrugado"] = (0.021, 0.030)` | Tabla N° 09 | Manual de Hidrología | [CN:95](src/constantes_normativas.py:95) | [N] |
| `MANNING["concreto_recto"] = (0.010, 0.013)` | Tabla N° 09 | Manual de Hidrología | [CN:95](src/constantes_normativas.py:95) | [N] |
| `MANNING["madera_duelas"] = (0.010, 0.014)` | Tabla N° 09 | Manual de Hidrología | [CN:95](src/constantes_normativas.py:95) | [N] |
| **Afirmación negativa**: HDPE NO está listado en la Tabla N° 09 | Tabla N° 09 | Manual de Hidrología | [CN:72](src/constantes_normativas.py:72) | [N] |
| `V_MAX["concreto"] = (3.0, 6.0)` m/s | Tabla N° 10 | Manual de Hidrología | [CN:109](src/constantes_normativas.py:109) | [N] |
| `V_MAX["ladrillo_c_concreto"] = (2.5, 3.5)` m/s | Tabla N° 10 | Manual de Hidrología | [CN:109](src/constantes_normativas.py:109) | [N] |
| `V_MAX["mamposteria_piedra"] = (2.0, 2.0)` m/s | Tabla N° 10 | Manual de Hidrología | [CN:109](src/constantes_normativas.py:109) | [N] |
| **Afirmación negativa**: TMC y HDPE NO están listados en la Tabla N° 10 | Tabla N° 10 | Manual de Hidrología | [CN:80](src/constantes_normativas.py:80) | [N] |
| `LONG_MAX_CUNETA = {seca: 250.0, muy_lluviosa: 200.0}` m | 4.1.2.1 d) | Manual de Hidrología | [CN:116](src/constantes_normativas.py:116) | [N] |
| `NUMERAL_LUZ = "4.1.1.3.1 / 4.1.1.5.1"` (págs. 70 y 88) | 4.1.1.3.1 / 4.1.1.5.1 | Manual de Hidrología | [M1:78](src/modulos/M1_clasificacion.py:78) | [N] |
| `NUMERAL_TR = "3.6, Tabla N 02"` (pág. 25) | 3.6, Tabla N° 02 | Manual de Hidrología | [M1:79](src/modulos/M1_clasificacion.py:79) | [N] |
| Catálogo de diámetros arranca en 0.90 m "mínimo normativo MTC" | num. 4.1.1.3.4 a) | Manual de Hidrología | [M2:109](src/modulos/M2_material.py:109) | [N] |
| `NUMERAL_V1 = "4.1.1.3.7 b)"` (V1, borde libre y/D ≤ 0.75) | 4.1.1.3.7 b) | Manual de Hidrología | [M5:188](src/modulos/M5_verificaciones.py:188) | [N] |
| ↻ `NUMERAL_V2` (V2, V ≥ 0.25 m/s) — **enriquecido**: era `"4.1.1.3.6"` pelado. Ahora lleva RD, página, de qué párrafo sale y el matiz **"el numeral RECOMIENDA, no prohíbe"**. Es lo único que la memoria imprime de V2 | num. 4.1.1.3.6, pág. 76, párrafo posterior a la Tabla N° 10 | Manual de Hidrología (MTC, RD 20-2011-MTC/14) | [M5:198-130](src/modulos/M5_verificaciones.py:198) | [N] |
| ↻ `NUMERAL_V3` (V3, velocidad máxima) — **enriquecido**: era `"Tabla Nº 10 (num. 4.1.1.3.6)"`, sin título ni página. El **título** de la tabla ES el sustento de que se verifique un solo extremo, y vivía solo en el código y en este manifiesto, que no van al expediente | Tabla N° 10 "Velocidades máximas admisibles en conductos revestidos", num. 4.1.1.3.6, pág. 76 | Manual de Hidrología (MTC, RD 20-2011-MTC/14) | [M5:204-134](src/modulos/M5_verificaciones.py:204) | [N] |
| ⟳ `NUMERAL_LAUSHEY = "4.1.1.3.7 c)"`; d50 = V²/(K·G_LAUSHEY), pág. 80 | 4.1.1.3.7 c) | Manual de Hidrología | [M6:76](src/modulos/M6_proteccion.py:76), [M6:76](src/modulos/M6_proteccion.py:76) | [N] |
| `NUMERAL_FASE_10 = "Fase 10 (num. 4.1.2.1 d), pag. 178)"` | 4.1.2.1 d), pág. 178 | Manual de Hidrología | [M10:62](src/modulos/M10_espaciamiento.py:62), [M10:62](src/modulos/M10_espaciamiento.py:62) | [N] |
| ↻ `n_manning_hdpe` — rango del concreto **aplicado por analogía** al HDPE de interior liso. Dos cambios (SIS-D-11): la etiqueta pasa de `[A]` a **`[N→]`** —lo exige la regla de coherencia de §0.1 de la hoja de ruta: un valor justificado invocando una fila de una tabla normativa no puede ser `[A]`, y los otros dos `[N→]` del proyecto son el mismo caso— y el valor **se lee de** `constantes_normativas.MANNING["concreto_recto"]` en vez de copiarse: escrito a mano era el mismo par duplicado sin nada que ligara las dos copias | Tabla N° 09, num. 4.1.1.3.5 (analogía declarada) | Manual de Hidrología (analogía) | [CA:915](src/criterios_adoptados.py:915) | **[N→]** |
| ↻ `v_max_concreto_eleccion = None` — techo **opcional** más conservador que el máximo normativo de 6.0 m/s. **`fuente` completada**: ahora explica que 6.0 es el máximo del mejor acabado (el defecto [N] que V3 aplica) y 3.0 el del acabado más pobre (el otro extremo de la sensibilidad). Iba ahí y no en `justificacion` porque el bloque "refinamiento opcional no adoptado" de la memoria imprime `fuente` | Tabla N° 10 "Velocidades máximas admisibles en conductos revestidos", num. 4.1.1.3.6, pág. 76 | Manual de Hidrología (MTC, RD 20-2011-MTC/14) | [CA:1001-791](src/criterios_adoptados.py:1001) | [A] |
| `long_max_cuneta = 200.0` m (se adopta la fila "muy lluviosa" por FEN) | num. 4.1.2.1 d), pág. 178 | Manual de Hidrología | [CA:1192](src/criterios_adoptados.py:1192) | [A] |
| `umbral_area_quebrada_importante_ha = None` — **afirmación negativa formalizada [A]**: la Tabla N° 02 da R y n por categoría y el Manual **no fija ninguna regla de asignación física** (área, caudal, longitud ni orden de cauce) para clasificar una quebrada. No es [C] porque no hay fuente técnica que cubra el vacío: el vacío está en la norma | Tabla N° 02 (num. 3.6) | Manual de Hidrología | [CA:778](src/criterios_adoptados.py:778) | [A] |

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
> ([M5:200](src/modulos/M5_verificaciones.py:200)). Ver §11.

---

## 2. Manual de Suelos, Geología, Geotecnia y Pavimentos (MTC, RD 10-2014-MTC/14)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `RESGUARDO_NAPA_SUBRASANTE`: CBR ≥ 20 % → 0.60 m | num. 4.5.4 | Manual de Suelos | [CN:189-142](src/constantes_normativas.py:189) | [N] |
| `RESGUARDO_NAPA_SUBRASANTE`: 6 ≤ CBR < 20 → 0.80 m | num. 4.5.4 | Manual de Suelos | [CN:189](src/constantes_normativas.py:189) | [N] |
| `RESGUARDO_NAPA_SUBRASANTE`: 3 ≤ CBR < 6 → 1.00 m | num. 4.5.4 | Manual de Suelos | [CN:189](src/constantes_normativas.py:189) | [N] |
| `RESGUARDO_NAPA_SUBRASANTE`: CBR < 3 → 1.20 m | num. 4.5.4 | Manual de Suelos | [CN:189](src/constantes_normativas.py:189) | [N] |
| `CBR_MIN_SUBRASANTE = 6.0` % | num. 3.3 | Manual de Suelos | [CN:194](src/constantes_normativas.py:194) | [N] |
| ⟳ `COMPACTACION_CORONA = 0.95` (0.30 m superiores, capas de 0.15 m) | num. 3.2.1, 3.2.2, 3.3 y 9.1(1) | Manual de Suelos | [CN:195-148](src/constantes_normativas.py:195) | [N] |
| ⟳ `COMPACTACION_CUERPO = 0.90` (capas de hasta 0.30 m) | num. 3.2.1, 3.2.2, 3.3 y 9.1(1) | Manual de Suelos | [CN:197-150](src/constantes_normativas.py:197) | [N] |
| ⟳ `CALICATAS_POR_KM` (autopista/dual/1ª clase 4; 2ª clase 3; 3ª clase 2; bajo volumen 1) + `CALICATAS_POR_SENTIDO` (autopista y dual: **× sentido**, el total se duplica) | num. 4.2, Cuadro 4.1 | Manual de Suelos | [CN:200](src/constantes_normativas.py:200), [CN:200](src/constantes_normativas.py:200) | [N] |
| ⟳ `ESPACIAMIENTO_PERFIL_KM = 4.0` (nivel perfil) | num. 4.2, Cuadro 4.1 | Manual de Suelos | [CN:221](src/constantes_normativas.py:221) | [N] |
| `resguardo_HW_subrasante = "segun_CBR"` — la tabla 4.5.4 aplicada al HW de avenida, **por analogía** (el numeral regula el nivel freático, no un nivel transitorio) | num. 4.5.4 y 9.1(3) | Manual de Suelos | [CA:1145](src/criterios_adoptados.py:1145) | [N→] |
| `NUMERAL_V4` — `ReferenciaNormativa`: `seccion_hoja_ruta="Sec. 5.1"` / `numeral_norma="Manual de Suelos…, num. 4.5.4 y 9.1(3)"` | 4.5.4 y 9.1(3) | Manual de Suelos | [M5:207](src/modulos/M5_verificaciones.py:207) | [N→] |
| `resguardo_por_cbr()` — tabla de CBR aplicada en V4 | num. 4.5.4 | Manual de Suelos | [M5:489-322](src/modulos/M5_verificaciones.py:489) | [N] |
| Tamizado 7.A: CBR → resguardo, misma tabla de Sec. 5.1 | num. 4.5.4 | Manual de Suelos | [M7:103](src/modulos/M7_geometria.py:103) | [N] |
| ↻ `NF_profundidad_m` — **ya no es un valor declarado**: es columna del CSV, medida en cada cruce, y hoy viene vacía en las cuatro filas | El 1.4 m que se declaraba no tenía numeral del Manual: citaba la *hoja de ruta* (Sec. 0.5 num. 105; Fase 8 num. 545; Fase 9 num. 582). Siendo dato por punto, **no hay nada que verificar contra un PDF**: se verifica contra el estudio geotécnico del expediente, cruce por cruce | Estudio geotécnico del expediente (antes: "Manual de Suelos MTC / caracterización geotécnica del sitio") | [modelos.py:359](src/modelos.py:359), [M0:86](src/modulos/M0_carga.py:86) | [S] |

---

## 3. Manual de Puentes (MTC, RD 041-2016-MTC/14)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `GAMMA_AGUA_KN_M3 = 9.81` kN/m³ (subpresión) | num. 2.4.3.8.2 | Manual de Puentes | [CN:60](src/constantes_normativas.py:60) | [N] |
| `SOBRECARGA_TRASDOS_H_EQ = 0.60` m de relleno equivalente | 2.1.4.3.9, pág. 91 | Manual de Puentes | [CN:340](src/constantes_normativas.py:340), [CN:340](src/constantes_normativas.py:340) | [N] |
| `CARGA_VIVA = "HL-93"` | 2.4.3.2.2.1 | Manual de Puentes | [CN:341](src/constantes_normativas.py:341) | [N] |
| `NQ_ZAPATA_EN_TALUD = 0.0` (zapata próxima a talud) | 2.8.1.3.1.2c, págs. 272-273 | Manual de Puentes | [CN:342](src/constantes_normativas.py:342), [CN:342](src/constantes_normativas.py:342) | [N] |
| `F_PGA_TABLA = {C: 1.0, D: 1.0, E: 0.9}` para PGA ≥ 0.50 | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CN:343-240](src/constantes_normativas.py:343) | [N] |
| `NUMERAL_K_H0 = "2.8.1.1.14.2"` (k_h0 = A_s) | 2.8.1.1.14.2 | Manual de Puentes | [CN:368](src/constantes_normativas.py:368), [M9:28](src/modulos/M9_cabezal.py:28), [M9:281](src/modulos/M9_cabezal.py:281) | [N] |
| `COMBINACIONES_AASHTO = ("Resistencia I", "Servicio I", "Evento Extremo I")` — solo los **nombres** | 2.4.5.3 (AASHTO LRFD Sec. 3.4.1), págs. 140-143 | Manual de Puentes (vía AASHTO) | [CN:364-260](src/constantes_normativas.py:364) | [N] |
| ↻ `PGA_roca_B = 0.50` g, Tr = 1000 años, roca Clase B — **el mapa es normativo, la lectura es de este sitio** | Apéndice A3, mapa "Isoaceleraciones Espectrales Suelo Tipo B, AASHTO 2014 (Roca). Periodo estructural 0.0 seg (PGA)". Verificar además **sobre qué punto del mapa se leyó**: el expediente no lo registra (pendiente 1.4 de la hoja de ruta) | Manual de Puentes | [DS:142](src/datos_sitio.py:142), [M9:220](src/modulos/M9_cabezal.py:220) | [S] |
| ↻ `FACTOR_MURO_TABLA = {rígido: 1.0, desplazable: 0.5}` — los **dos** valores de tabla del numeral | numeral 2.8.1.1.14.2 | Manual de Puentes | [CN:351](src/constantes_normativas.py:351), [CN:351](src/constantes_normativas.py:351) | [N] |
| ↻ `factor_muro_eleccion = 1.0` — la **elección** de la fila rígida para este cabezal (empotrado, sin desplazamiento admisible garantizado); sensibilidad (0.5, 1.0) | El numeral fija las dos filas, **no** cuál aplica a este cabezal: eso no se verifica contra el PDF | Manual de Puentes (tabla) + decisión de proyecto (elección) | [CA:613](src/criterios_adoptados.py:613), [M9:290](src/modulos/M9_cabezal.py:290) | [A] |
| `F_pga = 1.0` — la **tabla** es [N], la **elección** dentro de ella es [A] | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CA:600](src/criterios_adoptados.py:600), [M9:168](src/modulos/M9_cabezal.py:168) | [A] |
| **Afirmación negativa**: el Manual de Puentes NO tipifica excepciones para Clase F en su Tabla 2.4.3.11.2.1.2-1 | Tabla 2.4.3.11.2.1.2-1 | Manual de Puentes | [CA:522-403](src/criterios_adoptados.py:522) | [C] |
| `empuje_flotacion()` — U por metro lineal, conducto sumergido | num. 2.4.3.8.2 | Manual de Puentes | [M8:155-139](src/modulos/M8_estructural.py:155), [M8:165](src/modulos/M8_estructural.py:165) | [N] |
| `NUMERAL_V7 = "Fase 5, V7 (Manual de Puentes num. 2.4.3.8.2 + Fase 8, item 3)"` | 2.4.3.8.2 | Manual de Puentes | [M5:214](src/modulos/M5_verificaciones.py:214), [M8:167](src/modulos/M8_estructural.py:167) | [N] |
| `NUMERAL_SUBPRESION = "Manual de Puentes num. 2.4.3.8.2"` (subpresión del cabezal) | 2.4.3.8.2 | Manual de Puentes | [M9:189](src/modulos/M9_cabezal.py:189), [M9:189](src/modulos/M9_cabezal.py:189) | [N] |
| `presion_sobrecarga_trasdos()`: p = γ·0.60·k_a; aplica con tráfico a ≤ H/2 | num. 2.1.4.3.9 | Manual de Puentes | [M9:588](src/modulos/M9_cabezal.py:588), [M9:588](src/modulos/M9_cabezal.py:588) | [N] |
| `n_q_zapata_en_talud()` = 0.0; N_c y N_γ **reemplazados** por N_cq y N_γq | num. 2.8.1.3.1.2c, págs. 272-273 | Manual de Puentes | [M9:1047](src/modulos/M9_cabezal.py:1047), [M9:1047-1049](src/modulos/M9_cabezal.py:1047) | [N] |
| `N_cq_N_gammaq_meyerhof = None` — salen de **figuras**, no de tabla ni fórmula | figuras 2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), págs. 272-273 | Manual de Puentes | [CA:2213](src/criterios_adoptados.py:2213) | [A] |
| `factores_carga_aashto = None` — el Manual nombra las combinaciones y no transcribe las Tablas 3.4.1-1/-2 | 2.4.5.3, págs. 140-143 | Manual de Puentes (vía AASHTO) | [CA:2104](src/criterios_adoptados.py:2104) | [A] |
| `procedimiento_flexion_corte_aashto_sec5 = None` — remisión a AASHTO Sec. 5 | Manual de Puentes Sección 2.9, pág. 337 | Manual de Puentes (vía AASHTO) | [CA:2351](src/criterios_adoptados.py:2351), [M9:170](src/modulos/M9_cabezal.py:170), [M9:1333-1334](src/modulos/M9_cabezal.py:1333) | [A] |
| **Afirmación negativa**: AASHTO LRFD Sec. 12 NO está incorporada por el Manual de Puentes (difiere rigidez de anillo, pandeo y costura) | Sec. 12 de AASHTO, no incorporada | Manual de Puentes | [M8:46-36](src/modulos/M8_estructural.py:46), [M8:216-200](src/modulos/M8_estructural.py:216), [M8:278](src/modulos/M8_estructural.py:278) | [C] |
| ↻ **Afirmación negativa ACOTADA a lo que se sostiene** (NOR-PUE-05, NOR-PUE-06): el Manual **no incorporó un capítulo equivalente** a la Sección 12 de AASHTO LRFD (*Buried Structures and Tunnel Liners*) y **no fija altura mínima de relleno** para ningún material. Decía «vacío absoluto sobre conductos enterrados», y eso es falso: el Manual trata estructuras enterradas al menos en cinco lugares —2.4.3.3.2 «Componentes Enterrados» (pág. 109, IM = 33(1.0 − 0.125·DE)); Tabla 2.4.5.3.1-**2** «Factores de carga para cargas permanentes, γp» (pág. 143), con filas propias de «Estructura rígida enterrada» (1.30/0.90) y «Estructuras flexible enterradas» —es la **‑2** y no la **‑1**, que en esa misma página es la de combinaciones de carga—; 2.8.1.3A.6.2 (pág. 280), cortante en losas de alcantarilla cajón con menos/más de 600 mm de relleno; 2.9.1.4.6.4.6 (pág. 362), armadura de distribución según la altura de relleno; 2.4.3.11.1 (pág. 121), exención sísmica de alcantarillas cajón enterradas—. **Ninguno fija una cobertura mínima**: todos la suponen conocida y la usan como entrada, que es justo el dato que falta | verificado contra el PDF, págs. impresas 109, 121, 143, 280, 362 | Manual de Puentes | [CA:1762](src/criterios_adoptados.py:1762) | [C] |
| ↻ **La «evidencia de índice» se RETIRA por falsa** (NOR-PUE-06): se afirmaba que el índice «salta de 2.11 (Muros de Contención y Estribos) a 2.12 (Disposiciones Constructivas)». **2.11 es «DISEÑO DE BARRERAS DE SONIDO»** (15 AASHTO), pág. 505, y 2.12 «Disposiciones Constructivas», pág. 513; los muros y estribos viven dentro de **2.8 Cimentaciones**, de donde este mismo expediente saca 2.8.1.1.14.2. La numeración del Manual tampoco sigue la de AASHTO (2.8↔10, 2.10↔14.6, 2.11↔15), así que «entre 2.11 y 2.12 debería estar la Sec. 12» no era una inferencia válida. La conclusión no cambia; el argumento sí | verificado contra el PDF, págs. impresas 505 y 513 | Manual de Puentes | [CA:1762](src/criterios_adoptados.py:1762) | — |
| ⚠ **TRAMPA DE VOCABULARIO — no usar este valor como altura de relleno**: el Manual sí usa la palabra "recubrimiento" para alcantarillas y da 2.0 in / 50 mm, pero ahí significa el **recubrimiento de concreto sobre el acero de refuerzo**, no la altura de relleno de tierra. Dos conceptos que comparten palabra en español y no tienen relación | Tabla 2.9.1.5.5.3-1, pág. 378 | Manual de Puentes | [CA:2094](src/criterios_adoptados.py:2094) | — |

---

## 4. E.050 Suelos y Cimentaciones (RM 406-2018-VIVIENDA)

Toda la tabla de factores de seguridad de la Fase 9 sale de este documento.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `FS["capacidad_portante"] = {estático: 3.00, sísmico: 2.50}` | Art. 21 (21.1/21.2), pág. 34 | E.050 | [CN:371](src/constantes_normativas.py:371), [CN:371](src/constantes_normativas.py:371) | [N] |
| `FS["volteo"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 a), pág. 72 | E.050 | [CN:371](src/constantes_normativas.py:371), [CN:371](src/constantes_normativas.py:371) | [N] |
| `FS["deslizamiento"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 a), pág. 72 | E.050 | [CN:371](src/constantes_normativas.py:371), [CN:371](src/constantes_normativas.py:371) | [N] |
| `FS["estabilidad_global"] = {estático: 1.50, sísmico: 1.25}` | num. 39.13.6 b), pág. 72 | E.050 | [CN:371](src/constantes_normativas.py:371), [CN:371](src/constantes_normativas.py:371) | [N] |
| `FS["talud"] = {estático: 1.50, sísmico: 1.25}` | Art. 30.3, pág. 39 | E.050 | [CN:371](src/constantes_normativas.py:371), [CN:371](src/constantes_normativas.py:371) | [N] |
| `NUMERAL_C_PHI`: en cohesivos φ=0, en friccionantes c=0 (prohibido sumar) | Art. 20, pág. 33 | E.050 | [CN:385](src/constantes_normativas.py:385), [M9:1040](src/modulos/M9_cabezal.py:1040), [M9:1040](src/modulos/M9_cabezal.py:1040) | [N] |
| `NUMERAL_ZAPATA_TALUD_E050`: doble verificación (inclinación de superficie y de base + estabilidad global del talud) | Art. 30.1-30.2 | E.050 | [CN:386](src/constantes_normativas.py:386), [M9:1489](src/modulos/M9_cabezal.py:1489) | [N] |
| `SPT_PROF_MIN = 15.0` m | Art. 38 | E.050 | [CN:388](src/constantes_normativas.py:388) | [N] |
| `SPT_ESPACIAMIENTO = 1.0` m entre ensayos | **⚠ sin numeral propio** (hereda el Art. 38 de la línea anterior; `clase_sitio` sí lo cita como Art. 38) | E.050 | [CN:389](src/constantes_normativas.py:389), [CA:508-387](src/criterios_adoptados.py:508) | [N] |
| `e1_capacidad_portante()` ≥ 3.00 / 2.50 | Art. 21.1/21.2 | E.050 | [M9:882](src/modulos/M9_cabezal.py:882) | [N] |
| `e2_volteo()` ≥ 1.50 / 1.25 | num. 39.13.6 a) | E.050 | [M9:903](src/modulos/M9_cabezal.py:903) | [N] |
| `e3_deslizamiento()` ≥ 1.50 / 1.25 | num. 39.13.6 a) | E.050 | [M9:903](src/modulos/M9_cabezal.py:903) | [N] |
| `e4_estabilidad_global()` ≥ 1.50 / 1.25 | num. 39.13.6 b) | E.050 | [M9:944](src/modulos/M9_cabezal.py:944) | [N] |
| `e5_estabilidad_talud()` ≥ 1.50 / 1.25 | Art. 30.3 | E.050 | [M9:962-963](src/modulos/M9_cabezal.py:962) | [N] |
| `c_phi_fundacion = None` — la obligación de usar solo uno (φ=0 o c=0) | Art. 20 | E.050 | [CA:1330](src/criterios_adoptados.py:1330) | [A] |
| `PERFIL_SUELO_PRESUNTO` — lo reemplaza el **SPT de licuefacción: ≥ 15 m, ensayos cada 1 m** | Art. 38 | E.050 | [CA:460](src/criterios_adoptados.py:460) | [S] |
| `clase_sitio` — lo reemplazan el **estudio de respuesta de sitio específico** que AASHTO exige para la Clase F y la **caracterización sobre los 30 m superiores** (Vs30 o N̄). El SPT de 15 m **no lo cierra**: otra profundidad, otra pregunta | Art. 3.10.3.1 (AASHTO) / perfil de E.030 | AASHTO LRFD / E.030 | [CA:508](src/criterios_adoptados.py:508) | **[A]** (era [C]) |
| `metodo_estabilidad_global = None` — **afirmación negativa**: E.050 fija el umbral, no el método | Art. 30.3 y num. 39.13.6 b) | E.050 | [CA:2244](src/criterios_adoptados.py:2244) | [A] |

---

## 5. E.060 Concreto Armado

Entra al proyecto solo por la **excepción declarada de durabilidad y
recubrimientos** (Vía 1 de Sec. 0.2); el diseño estructural es de AASHTO.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `SULFATOS`: SO₄ 0.00–0.10 % → sin exigencia | Tabla 4.4 | E.060 | [CN:392](src/constantes_normativas.py:392) | [N] |
| `SULFATOS`: 0.10–0.20 % → cemento II/IP(MS)/IS(MS), a/c 0.50, f'c 28 MPa | Tabla 4.4 | E.060 | [CN:392](src/constantes_normativas.py:392) | [N] |
| `SULFATOS`: 0.20–2.00 % → cemento V, a/c 0.45, f'c 31 MPa | Tabla 4.4 | E.060 | [CN:392](src/constantes_normativas.py:392) | [N] |
| `SULFATOS`: > 2.00 % → cemento V + puzolana, a/c 0.45, f'c 31 MPa | Tabla 4.4 | E.060 | [CN:392](src/constantes_normativas.py:392) | [N] |
| `CLORUROS_EXTERNOS = {a/c máx 0.40, f'c mín 35 MPa}` | Art. 4.2 / 4.4 | E.060 | [CN:398](src/constantes_normativas.py:398) | [N] |
| `RECUBRIMIENTO`: contra suelo 70 mm; suelo/intemperie ≥ 3/4" 50 mm; ≤ 5/8" 40 mm | Art. 7.7.1, pág. 54 | E.060 | [CN:399-296](src/constantes_normativas.py:399), [M9:1162](src/modulos/M9_cabezal.py:1162) | [N] |
| `AMBIENTE_CORROSIVO_AUMENTAR` — el artículo dice "aumentar adecuadamente" y **no fija cuánto** | Art. 7.7.5.1 | E.060 | [CN:402-300](src/constantes_normativas.py:402), [M9:1229](src/modulos/M9_cabezal.py:1229) | [N] |
| `CUANTIA_MIN_MURO = {horizontal 0.0020, vertical 0.0015}` — **piso obligatorio**, aplicado como ρ_diseño = max(ρ_calculado, ρ_mínimo) en `M9.cuantia_de_diseno`. Que AASHTO gobierne el *dimensionamiento* (Vía 1, Sec. 0.2) no convierte el mínimo en informativo | Art. 14.3.1, pág. 133 | E.060 | [CN:422](src/constantes_normativas.py:422), [M9:1281](src/modulos/M9_cabezal.py:1281) | [N] |
| `cortante_alto_muro_e060_art_11_10_10_2 = None` — **segundo mínimo de E.060**: escalón de la cuantía horizontal a 0.0025 bajo cortante alto. **Vacío declarado**, no omitido: M9 no calcula cortante (bloqueado en `procedimiento_flexion_corte_aashto_sec5`) y el artículo no está en la hoja de ruta | Art. 11.10.10.2 — **⚠ pendiente de recoger en la hoja de ruta** | E.060 | [CA:2299](src/criterios_adoptados.py:2299) | [A] |
| `ESPESOR_TEMPERATURA_DOS_CARAS = 0.250` m (refuerzo en dos caras) | Art. 14.8.3 | E.060 | [CN:424-320](src/constantes_normativas.py:424), [M9:1358](src/modulos/M9_cabezal.py:1358) | [N] |
| `ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0` (≤ 3h) | Art. 14.3.3 | E.060 | [CN:426](src/constantes_normativas.py:426), [M9:1276-1277](src/modulos/M9_cabezal.py:1276) | [N] |
| `ESPACIAMIENTO_MAX_ABSOLUTO = 0.400` m (400 mm) | Art. 14.3.3 | E.060 | [CN:427-323](src/constantes_normativas.py:427) | [N] |
| `CICLOPEO_FC_MATRIZ_MIN = 10.0` MPa | Art. 22.10, págs. 194-195 | E.060 | [CN:431](src/constantes_normativas.py:431), [M9:1303](src/modulos/M9_cabezal.py:1303) | [N] |
| `CICLOPEO_FRACCION_PIEDRA_MAX = 0.30` del volumen | Art. 22.10, págs. 194-195 | E.060 | [CN:432-328](src/constantes_normativas.py:432) | [N] |

---

## 6. EG-2013 — Especificaciones Técnicas Generales para Construcción, Capítulo V (Secciones 502-508)

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| ↻ `H_RELLENO_MIN["hdpe"] = 0.30` m (clave a subrasante). **Pág. corregida: 984, no 982** (verificada leyendo el PDF; ver `NOR-EG-01`). Ya **no** es el h_rec del tamizado: es uno de los dos mínimos que `M7.altura_recubrimiento` compara, y el otro —la cobertura mínima de AASHTO— lo supera en HDPE bajo pavimento | 508.07, pág. impresa 984 | EG-2013 | [CN:224](src/constantes_normativas.py:224), [M7:24](src/modulos/M7_geometria.py:24) | [N] |
| ↻ `H_RELLENO_MIN["concreto"] = None` — **afirmación negativa**: EG-2013 no lo fija para concreto. **Qué significa ese `None`, corregido**: significa eso y solo eso. No significa «lo fija la norma de producto», que es lo que esta fila decía: M 170M no da alturas de relleno y clasifica por D-load. El valor sale hoy de `cobertura_minima_aashto` | Secciones 505/506 → 502 (lo que no fijan) | EG-2013 | [CN:224](src/constantes_normativas.py:224) | [N] |
| ↻ `H_RELLENO_MIN["tmc"] = None` — ídem para TMC. La remisión del EG-2013 a A-807 (507.05/.06/.08) es de **materiales y fabricación**, no de altura de relleno | Sección 507 → 502 (lo que no fija) | EG-2013 | [CN:224](src/constantes_normativas.py:224) | [N] |
| `SECCION_EG2013`: concreto simple 505, concreto reforzado 506, TMC 507, HDPE 508. **Renombrada desde `SUBSECCION`**: son Secciones completas del Capítulo V, no subsecciones de ninguna "Sección 500" | Secciones 505 / 506 / 507 / 508 | EG-2013 | [CN:299](src/constantes_normativas.py:299), [M11:717](src/modulos/M11_reporte.py:717) | [N] |
| `SECCION_CABEZALES = "503"` (concreto estructural; + 504 acero) | 503 (+504) | EG-2013 | [CN:301](src/constantes_normativas.py:301) | [N] |
| `CAMA_RELLENO_LATERAL["concreto_simple"]`: cama Clase F (f'c = 14 MPa) ≥ 15 cm; Clase F hasta ≥ 1/4 del D exterior; relleno Sec. 502 ≥ 95 % MDS | 505.03/.07/.10/.11, págs. 950-951 | EG-2013 | [CN:309-209](src/constantes_normativas.py:309) | [N] |
| `CAMA_RELLENO_LATERAL["concreto_reforzado"]`: subbase granular (Sec. 402) ≥ 15 cm, ≥ 95 % MDS; subbase hasta ≥ 1/6 del D exterior; relleno Sec. 502 | 506.03/.07/.10/.11, págs. 959-960 | EG-2013 | [CN:309-209](src/constantes_normativas.py:309) | [N] |
| `CAMA_RELLENO_LATERAL["tmc"]`: subbase ≥ 15 cm, ≥ 95 % MDS con arena suelta de 12 mm; capas de 15-20 cm ≥ 90 % base/cuerpo y ≥ 95 % corona | 507.06/.07/.08, pág. 970 | EG-2013 | [CN:309-210](src/constantes_normativas.py:309) | [N] |
| `CAMA_RELLENO_LATERAL["hdpe"]`: arena gruesa, capas de 15 cm, espesor 15-30 cm (30 cm en roca o suelo blando); capas alternadas simétricas de 15 cm a > 95 %, los 30 cm superiores a ≥ 100 %; prohibida la anegación | 508.05/.07, págs. 981-982 | EG-2013 | [CN:309-211](src/constantes_normativas.py:309) | [N] |
| `NUMERAL_8_1` — `ReferenciaNormativa`: `seccion_hoja_ruta="Sec. 8.1"` / `numeral_norma="EG-2013, Capítulo V, Sección de cada material (505/506/507/508); rellenos generales en la Sección 502"`. **Corrige una cita doblemente falsa**: ni "Sec. 8.1" es del EG-2013, ni existe una "Sección 500" | Capítulo V, Secciones 502 y 505-508 | EG-2013 | [M8:160](src/modulos/M8_estructural.py:160) | [N] |
| `NUMERAL_9_1` — `ReferenciaNormativa`: `seccion_hoja_ruta="Sec. 9.1"` / `numeral_norma="EG-2013, Capítulo V, Sección 503 (concreto estructural), num. 503.01, pág. 905"` | 503.01, pág. 905 | EG-2013 | [M9:179](src/modulos/M9_cabezal.py:179) | [N] |
| ↻ `h_relleno_min_concreto_tmc` — **RETIRADO** (`NOR-VAC-01`, ver §14.a). Su vacío no era un vacío: AASHTO LRFD Art. 12.6.6.3 lo tabula. Sigue siendo cierto lo que la fila decía del EG-2013 —fija 0.30 m para HDPE y nada para concreto ni TMC— y ese hecho vive ahora en el comentario de `H_RELLENO_MIN` y en la búsqueda de `cobertura_minima_aashto` | 508.07, pág. 984 (lo que sí fija, literal); 505 / 506 / 507 → 502 (lo que no fija) | EG-2013 | [CN:224](src/constantes_normativas.py:224), [CA:1538](src/criterios_adoptados.py:1538) | — |
| ↻ **Cita literal de lo que sí fija** — «La altura de relleno mínimo desde la clave de la tubería hasta el nivel de la subrasante será de 0,30 m.» Es exactamente la magnitud que calcula V7 (subrasante − clave) | Subsección 508.07, **pág. 984** | EG-2013 | [CN:208](src/constantes_normativas.py:208) | [N] |
| **Afirmación negativa**: las Secciones 505, 506 y 507 solo regulan colocación y compactación y remiten a la Sección 502, que tampoco fija altura mínima de diseño | 505 / 506 / 507 → 502 | EG-2013 | [CA:1147-1082](src/criterios_adoptados.py:1147) | [C] |
| **Remisiones formales** que cierran el circuito hacia §9: 506.02 → AASHTO M-170M (concreto reforzado); 507.05 / 507.06 / 507.08 → ASTM A-807 (TMC). ⚠ Esta remisión del EG-2013 a **A-807 es correcta y es de materiales y fabricación**; lo que era falso es atribuirle a A-807 la tabla de **calibre por altura de cobertura**, que es de ASTM A796/A796M (`NOR-PRO-04`) | 506.02, pág. 959; 507.05/.06 **pág. 973** y 507.08 **pág. 974** (verificadas leyendo el PDF; decían 969-970) | EG-2013 → norma de producto | [CA:1909](src/criterios_adoptados.py:1909) | [C] |
| Nota constructiva: el equipo pesado no circula sobre el conducto antes de que el relleno alcance 0.30 m. **Se trasladó** al comentario de `H_RELLENO_MIN` al retirarse el criterio que la alojaba: es exigencia de **ejecución**, no altura mínima de diseño, y la cobertura de AASHTO no la sustituye | Sec. 7.A de la hoja de ruta, apoyada en EG-2013 | EG-2013 | [CN:224](src/constantes_normativas.py:224) | [N] |

---

## 7. HDS-5 (FHWA), 3ª edición, abril 2012

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `KU_METRICO = 1.811` (q* = KU·Q/(A·D^0.5)) | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:120-96](src/constantes_normativas.py:120) | [N] |
| `Q_LIM_NO_SUMERGIDO = 3.5` | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:121](src/constantes_normativas.py:121) | [N] |
| `Q_LIM_SUMERGIDO = 4.0` (entre ambos: interpolación lineal) | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:122](src/constantes_normativas.py:122) | [N] |
| `HDS5_INLET["circular_concreto_square_edge_headwall"]`: K=0.0098, M=2.00, c=0.0398, Y=0.67 | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:124-100](src/constantes_normativas.py:124) | [N] |
| `HDS5_INLET["circular_cmp_headwall"]`: K=0.0078, M=2.00, c=0.0379, Y=0.69 | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:124-100](src/constantes_normativas.py:124) | [N] |
| `HDS5_INLET["circular_cmp_mitered"]`: K=0.0210, M=1.33, c=0.0463, Y=0.75 | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CN:124-100](src/constantes_normativas.py:124) | [N] |
| `Ks = -0.5` (sin inglete) / `+0.7` (con inglete) | **⚠ el código declara expresamente que NO figura en la Tabla A.1**: "proviene de la formulación" | HDS-5 (formulación, sin tabla) | [CN:132](src/constantes_normativas.py:132), [M4:343-346](src/modulos/M4_control.py:343), [M4:306-313](src/modulos/M4_control.py:306) | [N] |
| Ecuaciones de control de entrada: q* ≤ 3.5 → HWi/D = Hc/D + K·(q*)^M + Ks·S; q* ≥ 4.0 → HWi/D = c·(q*)² + Y + Ks·S | Apéndice A (Formas 1 y 2) | HDS-5 | [M4:56-57](src/modulos/M4_control.py:56) | [N] |
| `metodo_transicion_hds5 = "interpolacion_lineal_entre_extremos"` — la transición 3.5 < q* < 4.0. **La recta NO es el método del HDS-5**: HDS-5 empalma las dos ramas con una curva **tangente empírica sin ecuación publicada**. La interpolación lineal la prescribe Sec. 4.2 de la hoja de ruta y aquí queda declarada como simplificación adoptada | Cap. IV y Apéndice A (curva de transición, sin ecuación) | HDS-5 3ª ed. (2012) | [CA:877](src/criterios_adoptados.py:877), [M4:376](src/modulos/M4_control.py:376) | [C] |
| `K_FRICCION_SI = 19.63` — H = (1 + ke + 19.63·n²·L/R^(4/3))·V²/(2g); "29 es el valor inglés". **Corregido desde 19.62**: 19.63 es la conversión SI que el propio HDS-5 declara para su K = 29. Se retiró la justificación "= 2·g", coincidencia numérica sin respaldo en la fuente. **⚠ La hoja de ruta sigue diciendo 19.62 y debe corregirse** | **⚠ sin numeral**: se cita la ecuación de control de salida, no un apartado | HDS-5 / literatura FHWA | [CN:136](src/constantes_normativas.py:136), [M4:79-110](src/modulos/M4_control.py:79) | [N] |
| `h_o = max(TW, (y_c + D)/2)` | **⚠ sin numeral** | HDS-5 (control de salida) | [CN:135](src/constantes_normativas.py:135), [M4:98-100](src/modulos/M4_control.py:98) | [N] |
| `hds5_embocadura_hdpe = {K:0.0098, M:2.00, c:0.0398, Y:0.67, Ks:-0.5}` — fila del **concreto** aplicada a HDPE de interior liso a ras del muro | Apéndice A, Tabla A.1, pág. A.8 | HDS-5 | [CA:831](src/criterios_adoptados.py:831) | [C] |
| `ke_entrada = 0.5` (square edge with headwall) — **cita cerrada** | Apéndice C, **Tabla C.2, pág. C.2** | HDS-5 3ª ed. (2012) | [CA:1057](src/criterios_adoptados.py:1057) | [C] |
| `geometria_control_salida = "seccion_llena"` (A = πD²/4, R = D/4, V = Q/A) | Cap. III — control de salida a sección llena | HDS-5 | [CA:1085](src/criterios_adoptados.py:1085) | [C] |
| `HW_D_max = 1.5` — **cita cerrada**. La sensibilidad declarada (1.2, 1.5) es un **subrango** del 1.0–1.5 de la fuente | **Sec. 2.2.5, pág. 2.14** (rango 1.0–1.5) | HDS-5 3ª ed. (2012) | [CA:1123](src/criterios_adoptados.py:1123) | [C] |
| Alternativa citada si el barril no llena: procedimiento de barril parcialmente lleno | Cap. III | HDS-5 | [CA:735-597](src/criterios_adoptados.py:735), [M4:400](src/modulos/M4_control.py:400) | [C] |

---

## 8. AASHTO LRFD Bridge Design Specifications

**Corregido contra el archivo** (NOR-MAN-01). Este preámbulo decía «ninguna cita
a AASHTO LRFD lleva hoy un valor numérico transcrito: todas las tablas quedaron
sin extraer», y era falso: cuatro de las filas de abajo **tienen valor y etiqueta
`[C]`** desde hace tiempo —`factores_carga_aashto`, `recubrimiento_aashto_mm`,
`peso_especifico_concreto_kn_m3` y `procedimiento_flexion_corte_aashto_sec5`—,
mientras el texto las inventariaba como `None` `[A]`, o sea como vacíos que
bloquean lo que el programa ya calcula. **Un manifiesto que describe como
bloqueado lo que ya corre invierte el sentido de la revisión**: el revisor se
salta justo las filas donde vive el defecto.

Lo que sí sigue siendo cierto: varias tablas de AASHTO **siguen sin extraer**, y
este bloque es en buena parte el inventario de lo que falta traer del PDF. Cada
fila dice hoy cuál de las dos cosas es.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| `COMBINACIONES_AASHTO` — los tres **nombres** (Resistencia I, Servicio I, Evento Extremo I) | Sec. 3.4.1 (vía Manual de Puentes num. 2.4.5.3) | AASHTO LRFD | [CN:364-260](src/constantes_normativas.py:364), [M9:837](src/modulos/M9_cabezal.py:837) | [N] |
| ~~`clase_sitio = "F_con_excepcion_periodo_corto"` — excepción para estructuras de periodo fundamental corto (≤ 0.5 s)~~ **CITA FALSA — RETIRADA.** Verificado contra AASHTO LRFD 9.ª ed. (2020): la dispensa no está en el Art. 3.10.3.1, ni en C3.10.3.1, ni en tabla o nota alguna. AASHTO exige estudio de respuesta de sitio específico para la Clase F, de forma incondicional. Hoy: `clase_sitio = "F_con_factores_tabulados_por_adopcion"`, adopción declarada del proyectista **sin respaldo normativo** — §0.5 | ninguna | — | [CA:508](src/criterios_adoptados.py:508) | ~~[C]~~ → **[A]** |
| ↳ esa verificación **ya se hizo**: no está en el articulado ni en el comentario, porque no existe. Lo que queda pendiente es otra cosa — declarar en la memoria que la adopción va contra una exigencia expresa de AASHTO, y programar el estudio de respuesta de sitio | Art. 3.10.3.1 y C3.10.3.1, 9.ª ed. (2020) | AASHTO LRFD | [CA:557](src/criterios_adoptados.py:557) | **[A]** |
| ↻ `factores_carga_aashto` — factores γ (DC, EV, EH, LS, WA, EQ) con máximos y mínimos. **TIENE VALOR**: diccionario completo por combinación. Decía `= None` `[A]` | Tablas 3.4.1-1 y 3.4.1-2 | AASHTO LRFD | [CA:2104](src/criterios_adoptados.py:2104), [M9:52](src/modulos/M9_cabezal.py:52), [M9:805](src/modulos/M9_cabezal.py:805) | **[C]** |
| ~~`FS_flotacion = None` — FS de V7, ΣW ≥ FS·U~~ **CRITERIO RETIRADO**, y esta fila lo inventariaba como vivo con un ancla que caía en otro criterio (NOR-MAN-03). V7 se reescribió como equilibrio de factores de carga LRFD (§0.2, Fase 5 V7): un FS global es lenguaje de tensión admisible y conservarlo además de los γ contaría dos veces el mismo margen. El código lo declara retirado y un test lo vigila | — | — | [CA:1903](src/criterios_adoptados.py:1903), [M8:63](src/modulos/M8_estructural.py:63), [test_M8:130](tests/test_M8_estructural.py:130) | ~~[C]~~ → **retirado** |
| Rigidez de anillo, pandeo y resistencia de costura: **diferidos al expediente** | Sec. 12 | AASHTO LRFD | [M8:46-36](src/modulos/M8_estructural.py:46), [M8:278](src/modulos/M8_estructural.py:278) | [C] |
| ↻ `recubrimiento_aashto_mm` — lado AASHTO de la regla "rige el recubrimiento MAYOR". **TIENE VALOR**: 75 mm en las tres condiciones. Decía `= None` `[A]`. Su número está en revisión por otra vía (categoría de refuerzo y modificador por a/c), que es un asunto distinto de esta fila | tabla de recubrimientos mínimos, Sec. 5 | AASHTO LRFD | [CA:2266](src/criterios_adoptados.py:2266), [M9:1170-1173](src/modulos/M9_cabezal.py:1170) | **[C]** |
| ↻ `procedimiento_flexion_corte_aashto_sec5` — factores φ, límites de refuerzo, modelo de corte (MCFT / β-θ). **TIENE VALOR**: φ, modelo de corte y β-θ declarados. Decía `= None` `[A]` | Sección 5 (vía Manual de Puentes Sec. 2.9, pág. 337) | AASHTO LRFD | [CA:2351](src/criterios_adoptados.py:2351), [M9:1333-1345](src/modulos/M9_cabezal.py:1333) | **[C]** |
| ↻ `peso_especifico_concreto_kn_m3` — peso unitario del concreto armado. **TIENE VALOR**: 23.56 kN/m³. Decía `= None` `[A]` | Tabla 3.5.1-1 (o Manual de Puentes) | AASHTO LRFD | [CA:2166](src/criterios_adoptados.py:2166) | **[C]** |
| `punto_aplicacion_incremento_sismico = None` — altura de aplicación de (P_AE − P_A) | Sec. 11 (alternativa: Seed-Whitman, 0.6H) | AASHTO LRFD | [CA:719](src/criterios_adoptados.py:719), [CA:719-581](src/criterios_adoptados.py:719) | [A] |
| ↻ **La EDICIÓN de AASHTO LRFD sí está declarada, y esta fila decía lo contrario** (NOR-MAN-03). Inventariaba una «advertencia transversal» atribuida a `[CA:992-995]`, líneas que pertenecen a otro criterio y no contienen ese texto: la advertencia no existía en el archivo ni en ningún otro. Lo que sí existe es la declaración de edición, **9.ª ed. (2020)**, escrita en cada criterio que cita AASHTO (`clase_sitio`, `factores_carga_aashto`, `recubrimiento_aashto_mm`, `procedimiento_flexion_corte_aashto_sec5`). Sigue siendo verdad el fondo —los factores y la numeración de la Sec. 11 cambian entre ediciones—, y por eso la edición se cita en la fuente de cada criterio y no en una nota suelta | 9.ª ed. (2020) | AASHTO LRFD | [CA:546](src/criterios_adoptados.py:546) | — |

---

## 9. Normas de producto ASTM / AASHTO (M-170M, M36, A760, A-807, M294, C76)

No están en la lista de PDF de la sesión, pero el código las cita con nombre y
usa valores atribuidos a ellas. Se separan para que quede claro que su
verificación necesita otras fuentes.

| Valor | Numeral citado | Documento fuente (según la cita) | Archivo:línea | Etiqueta |
|---|---|---|---|---|
| ↻ `D_MAX` — **RETIRADA de `constantes_normativas.py`** (`NOR-PRO-01`, `NOR-PRO-02`, `MAT-O8`). Los tres topes (2.70 / 2.10 / 1.50 m) se atribuían a normas de producto que **no los sostienen**: la Tabla 1 de A760/A760M-10 tabula diámetros nominales de 100 a **3600 mm** —los 2100 mm son una fila más de la serie— y las Tablas 1 a 5 de M 170M-04 van de 300 a 3600 mm, con §7.2 previendo diseños especiales por encima. La marca "VERIFICAR" que llevaba era la señal de que nunca debieron entrar ahí. Viven ahora en el criterio `D_max_catalogo` `[A]`, rotulados como topes de **catálogo** | **ninguno**: verificado en contra sobre los PDF | ASTM A760/A760M-10 Tabla 1, pág. 3; AASHTO M 170M-04 Tablas 1-5 y §7.2 | [CN:157](src/constantes_normativas.py:157), [CA:1429](src/criterios_adoptados.py:1429) | — |
| `D_max_catalogo` = {concreto 2.70, TMC 2.10, HDPE 1.50} m — **tope de catálogo adoptado, no normativo**. V9 y `siguiente_diametro` descartan material contra él, y ese descarte es del proyecto, no de la norma | — (adopción declarada sobre disponibilidad de mercado) | ninguno | [CA:1429](src/criterios_adoptados.py:1429) | [A] |
| `D_PASO = 0.15` m — "reproduce las series de 6″ y 150 mm" | (nombre de norma, sin numeral) | ASTM / AASHTO | [CN:155](src/constantes_normativas.py:155) | [N] |
| `D_INICIO = 0.90` m | mínimo normativo MTC (ver §1) | Manual de Hidrología | [CN:156](src/constantes_normativas.py:156) | [N] |
| ↻ `diametros_normalizados` = inicio 0.90, paso 0.15. **Los topes salieron de aquí** y viven en `D_max_catalogo`: el paso sí se verifica contra la serie de diámetros nominales de las normas de producto, y los topes no salen de ninguna | series de diámetro nominal: A760 Tabla 1 (150→3600 mm en escalones de 150 desde 900); M 170M Tablas 1-5 (300→3600 mm); M294 (serie de 150 mm) | ASTM / AASHTO | [CA:1403](src/criterios_adoptados.py:1403) | [C] |
| ↳ verificación pendiente declarada, **ahora en `D_max_catalogo`**: los tres topes siguen sin respaldo documental, y el de HDPE es el único cuya norma (AASHTO M294) ni siquiera está en `normas/` para contrastarlo | — | ninguno | [CA:1429](src/criterios_adoptados.py:1429) | [A] |
| `NORMA_PRODUCTO` por material (reporte) | ASTM C76/AASHTO M170; AASHTO M36/ASTM A760; AASHTO M294 | ASTM / AASHTO | [M2:211-150](src/modulos/M2_material.py:211) | [N] |
| ↻ `clases_producto_por_relleno = None` — tabla clase/calibre × diámetro × rango de altura de relleno, **sin extraer**. **Norma corregida** (`NOR-PRO-04`): el calibre por altura de cobertura es de **ASTM A796/A796M**, no de A-807, que no aparece ni una vez en M 170M, M 36 ni A760. La relación luz/corrugación sí se puede cerrar hoy: está en la Tabla 1 de A760 y la Tabla 6 de M 36, ambas en `normas/` | AASHTO M 170M-04 Tablas 1-5 (clases I-V); ASTM A796/A796M (calibre por altura), **no en `normas/`** | ASTM / AASHTO | [CA:1901](src/criterios_adoptados.py:1901), [M8:170](src/modulos/M8_estructural.py:170) | [C] |
| **Afirmación negativa**: AASHTO M294 (HDPE) no tiene tabla de clase por altura; depende de un cálculo de rigidez de anillo diferido al expediente | AASHTO M294 | ASTM / AASHTO | [CA:1066-832](src/criterios_adoptados.py:1066) | [C] |
| ↻ **Afirmación negativa, ATRIBUCIÓN CORREGIDA** (`NOR-PRO-03`): AASHTO M 170M, M 36 y ASTM A760 **no contienen alturas de relleno admisibles** —el fondo se confirma en las tres—, pero la fórmula «*manufacturing and purchase specification only*» es la **Nota 1 de M 170M** y solo de ella. En **M 36** la exclusión está en **§1.3** y en **A760** en **§1.4**, con otra redacción; la Nota 1 de esas dos habla de láminas con fibra de aramida y post-recubrimiento asfáltico | M 170M-04 **Nota 1**; M 36-03(2007) **§1.3**; A760/A760M-10 **§1.4** | ASTM / AASHTO | [CA:1694](src/criterios_adoptados.py:1694) | [C] |
| `espesor_pared_conducto = None` — el `t` que separa el diámetro interior del exterior, **por declarar**. Sin él no hay clave física (`MAT-D4`) ni volumen desplazado (`MAT-D3`). No es transcripción sino elección: M 170M tabula **tres** paredes por diámetro (A, B y C) y hay que elegir una; en TMC depende del calibre, que `clases_producto_por_relleno` deja abierto; M294 no está en `normas/` | AASHTO M 170M-04 Tablas 1-5, columna *Wall Thickness*; A760 Tabla 1 (corrugación por diámetro) | ASTM / AASHTO | [CA:1808](src/criterios_adoptados.py:1808) | [A] |
| **Afirmación negativa**: **M 170M clasifica por D-load (resistencia), no por altura** — no existe la tabla clase-a-altura que el criterio decía que iba a extraer de ella | AASHTO M 170M | ASTM / AASHTO | [CA:1407-1065](src/criterios_adoptados.py:1407) | [C] |

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
| ↻ `ZONA_SISMICA_LA_UNION = 4` | Antes **⚠ sin numeral**; ahora declara Anexo II (zonificación sísmica por distritos). El numeral es de E.030 y **no está en la hoja de ruta**, que solo cita el `Z` resultante | E.030 | [DS:181](src/datos_sitio.py:181) | [S] |
| ↻ `Z_E030 = 0.45` (Tr = 475 años) — "NO se usa para el cabezal" | Antes **⚠ sin numeral**; ahora declara Art. 11.1 leído con la zona del Anexo II. Lo que sí está en la hoja de ruta (num. 87) es el **descarte** | E.030 | [DS:208](src/datos_sitio.py:208) | [S] |
| ↻ `PERFIL_SUELO_PRESUNTO = "S5"` (suelos potencialmente licuables) — **referencia muerta**: no lo invoca ningún módulo | Art. 14.6. El artículo define el **esquema** S0–S5; qué letra le toca a este sitio es la aplicación de ese esquema a las condiciones de la llanura del Bajo Piura | E.030 | [CA:460](src/criterios_adoptados.py:460) | [S] |
| `demanda_sismica_licuefaccion = 1000` años — **descarta** el sismo de 475 años de E.030 por coherencia con el Manual de Puentes | (referencia al Tr 475 de E.030) | E.030 (descartado) | [CA:1377](src/criterios_adoptados.py:1377) | [A] |

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
| `v_max_hdpe = 4.6` m/s (= 15 ft/s) — **techo duro de la fuente**: por encima del límite el termoplástico no puede reforzarse estructuralmente y la propia tabla prohíbe su uso | Cap. 8, S8-6, Tabla 8-4 "Pipe Abrasion Levels", pp. 8-27/8-28 | WSDOT Hydraulics Manual M 23-03.12 (abril 2026) | [CA:949](src/criterios_adoptados.py:949) | [C] |
| `v_max_tmc = 4.6` m/s — **la fuente NO fija techo absoluto para metal**: por encima de este valor exige mayor calibre o revestimiento, no prohíbe el material. Se adopta como límite de diseño conservador porque el catálogo de M2 no modela protección adicional por calibre | Cap. 8, S8-6, Tabla 8-4 "Pipe Abrasion Levels", pp. 8-27/8-28 | WSDOT Hydraulics Manual M 23-03.12 (abril 2026) | [CA:979](src/criterios_adoptados.py:979) | [C] |

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
| `NUMERAL_CATALOGO` | `"Sec. 3.2"` — "nuevo en v7, sin numeral MTC propio" | [M2:184](src/modulos/M2_material.py:184) |
| `NUMERAL_MATERIAL` | `"Sec. 3.4"` | [M2:185](src/modulos/M2_material.py:185) |
| `NUMERAL_MANNING` | `"4.1"` (Sec. 4.1 de la hoja de ruta) | [M3:100](src/modulos/M3_hidraulica.py:100) |
| `NUMERAL_CRITICO` / `NUMERAL_ENTRADA` / `NUMERAL_SALIDA` | `"4.2.1"` / `"4.2"` / `"4.3"` | [M4:181-183](src/modulos/M4_control.py:181) |
| `NUMERAL_V6` | `"3.1"` | [M5:213](src/modulos/M5_verificaciones.py:213) |
| `NUMERAL_V8` | `"Fase 5, V8"` — "[N] verificación, no diseño, sin numeral que fije el TR ni el umbral" | [M5:218](src/modulos/M5_verificaciones.py:218), [CA:1281](src/criterios_adoptados.py:1281) |
| `NUMERAL_V9` | `"Sec. 3.2 (V9, nuevo en v7)"` | [M5:219](src/modulos/M5_verificaciones.py:219) |
| `NUMERAL_7A` / `NUMERAL_7B` | `"Sec. 7.A"` / `"Sec. 7.B"` | [M7:241-207](src/modulos/M7_geometria.py:241) |
| ↻ `NUMERAL_G1` / `NUMERAL_G2` | `"Sec. 7.A (recubrimiento: el mayor entre EG-2013 508.07 —solo HDPE— y AASHTO LRFD Art. 12.6.6.3, Tabla 12.6.6.3-1 / resguardo Sec. 5.1)"` / `"Sec. 7.B (cotas amarradas al fondo del receptor)"`. **Corregido**: decía «recubrimiento EG-2013» a secas, y ese string es lo único que la memoria imprime de la fila G1 — en un punto de **concreto** atribuía a EG-2013 un mínimo que EG-2013 no fija, que es la tesis misma de `NOR-VAC-01` | [M7:249](src/modulos/M7_geometria.py:249) |
| `NUMERAL_8_1_2` / `NUMERAL_8_5` | `"Fase 8, items 1-2"` / `"Fase 8, item 5"` | [M8:151](src/modulos/M8_estructural.py:151), [M8:151](src/modulos/M8_estructural.py:151) |
| `NUMERAL_9_2` / `NUMERAL_9_3` / `NUMERAL_MO` | `"Sec. 9.2"` / `"Sec. 9.3 (E.050)"` / `"Sec. 9.2 (Mononobe-Okabe)"` | [M9:184-186](src/modulos/M9_cabezal.py:184) |
| `NUMERAL_REGLA_RECUBRIMIENTO` | `"Sec. 0.2 (rige el recubrimiento mayor)"` | [M9:191](src/modulos/M9_cabezal.py:191) |
| `NUMERAL_BUCLE` | `"Sec. 2 de la guia de sesiones (Fases 4 y 5)"` | [MD:120](src/modulos/MD.py:120) |

### 11.b. Otras fuentes citadas por nombre

| Valor | Fuente citada | Archivo:línea | Etiqueta |
|---|---|---|---|
| `remanso_derecho_via = None` | Manual de Diseño Geométrico **DG-2018** + **Ley 29338**; requiere perfil de remanso (paso a paso o HEC-RAS) | [CA:1274-959](src/criterios_adoptados.py:1274), [M5:199](src/modulos/M5_verificaciones.py:199) | [A] |
| `talud_terraplen = None` | **DG-2018** y sección tipo del proyecto | [CA:2011-1260](src/criterios_adoptados.py:2011) | [A] |
| `pendiente_relleno_trasdos_i = None` | Sección típica del expediente vial (**DG-2018**) o detalle de coronación del terraplén | [CA:646-508](src/criterios_adoptados.py:646) | [A] |
| `v_max_hdpe = 4.6` m/s | ↻ **cita cerrada** — WSDOT Hydraulics Manual, ver §10-bis. Antes: PPI/FHWA, fuente identificada y valores sin extraer | [CA:949](src/criterios_adoptados.py:949) | [C] |
| `v_max_tmc = 4.6` m/s | ↻ **cita cerrada** — WSDOT Hydraulics Manual, ver §10-bis. Antes: PPI/FHWA, ídem | [CA:979](src/criterios_adoptados.py:979) | [C] |
| `longitud_proteccion_salida = None` | Práctica corriente de enrocado o **HEC-14** | [CA:2060-1308](src/criterios_adoptados.py:2060) | [A] |
| `homogeneidad_serie_fen = None` | Serie **SENAMHI** con longitud de registro, estación y años faltantes | [CA:744-606](src/criterios_adoptados.py:744) | [A] |
| `TW_receptor = None` | **ANA** / Junta de Usuarios del Bajo Piura | [CA:1181](src/criterios_adoptados.py:1181) | [A] |
| `Mw_licuefaccion = None` | Desagregación del peligro sísmico / sismo de subducción del norte peruano | [CA:1359-1034](src/criterios_adoptados.py:1359) | [A] |
| `k_v = 0.0` | "Práctica corriente; no fijado por el Manual de Puentes" | [CA:629](src/criterios_adoptados.py:629) | [A] |
| `espesor_proteccion_salida = 1.75`·d50 | "Práctica corriente de diseño de enrocado" (rango 1.5–2.0 d50) | [CA:2049](src/criterios_adoptados.py:2049) | [A] |
| `angulo_aletas = None` | "Práctica corriente; no fijado por el Manual" | [CA:2078](src/criterios_adoptados.py:2078) | [A] |
| `N_cq_N_gammaq_meyerhof = None` | **Meyerhof (1957)**, vía las figuras del Manual de Puentes (ver §3) | [CA:2213-1449](src/criterios_adoptados.py:2213) | [A] |
| `punto_aplicacion_incremento_sismico = None` | **Seed-Whitman** (≈0.6H), vía AASHTO (ver §8) | [CA:719-581](src/criterios_adoptados.py:719) | [A] |

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

> **Precisión sobre `valor_si_declarado()`** (SIS-D-03). El párrafo anterior
> decía que `v_max_concreto_eleccion` es «el único que se lee con
> `valor_si_declarado()`», y no lo es: M2 lee así otras cuatro claves
> (`n_manning_hdpe`, `espesor_pared_conducto`, `v_max_tmc`, `v_max_hdpe`)
> para poder construir el catálogo con campos vacíos. Lo que **sí** es único es
> que sea `opcional=True`: aquéllas detienen el cálculo más tarde, en su punto
> de uso, y ésta no detiene nada nunca porque la norma resuelve sola. La
> diferencia no es la función que se llama, es qué significa el `None`.

**Y no confundir un `[A]` con un `[S]`.** Los dos son valores que no son
portables a otra obra, y ahí termina el parecido: un `[A]` es una decisión que
pudo ser otra, y por eso se defiende con el rango de sensibilidad; un `[S]` es
un hecho que se leyó o se midió, no admite rango, y se defiende con la
trazabilidad de la lectura. Antes de la quinta etiqueta, forzar el PGA o el
nivel freático dentro de `[A]` habría dicho que alguien los "adoptó".

### Los 30 criterios `[A]` del proyecto

> **Esta tabla se recontó contra el archivo** (SIS-D-02, NOR-MAN-01, NOR-MAN-02).
> Tenía 33 filas y **cuatro no eran `[A]`**: `factores_carga_aashto`,
> `peso_especifico_concreto_kn_m3`, `recubrimiento_aashto_mm` y
> `procedimiento_flexion_corte_aashto_sec5` son `[C]` en el código —y tienen
> valor—, de modo que se declaraban aquí como vacíos `[A]` que bloquean lo que
> el programa ya calcula. Están abajo, marcadas, en vez de borradas: quien venga
> del texto viejo tiene que encontrar qué pasó con ellas. `n_manning_hdpe` sale
> por otro motivo (pasó a `[N→]`, ver §0.3 de la hoja de ruta y SIS-D-11), y
> entran los dos `[A]` que faltaban: `clase_sitio` —que §8 reetiquetó y ninguna
> lista recogió— y `origen_cota_fondo_entrada`, nuevo en esta revisión.

| Criterio | Valor | Estado | Sensibilidad declarada | Archivo:línea |
|---|---|---|---|---|
| `clase_sitio` | `"F_con_factores_tabulados_por_adopcion"` | declarado — **adopción sin respaldo normativo**, ver §8 | — (no la declara: la premisa «Clase F» está bajo revisión y un rango fijaría la respuesta antes que la pregunta; ver el criterio) | [CA:508](src/criterios_adoptados.py:508) |
| `F_pga` | 1.0 | declarado | (0.9, 1.0) | [CA:600](src/criterios_adoptados.py:600) |
| ↻ `factor_muro_eleccion` | 1.0 (fila rígida) | declarado | (0.5, 1.0) | [CA:613](src/criterios_adoptados.py:613) |
| `k_v` | 0.0 | declarado | (0.0, 0.5) | [CA:629](src/criterios_adoptados.py:629) |
| `pendiente_relleno_trasdos_i` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 10.0) ° | [CA:646](src/criterios_adoptados.py:646) |
| `inclinacion_muro_beta` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 10.0) ° | [CA:675](src/criterios_adoptados.py:675) |
| `friccion_muro_suelo_delta` | `None` | **vacío — bloquea K_AE y Ka de Coulomb** | (0.0, 22.7) ° | [CA:695](src/criterios_adoptados.py:695) |
| `punto_aplicacion_incremento_sismico` | `None` | **vacío — bloquea el momento de volteo sísmico** | (0.333, 0.6)·H | [CA:719](src/criterios_adoptados.py:719) |
| `homogeneidad_serie_fen` | `None` | **vacío — bloquea el Q de diseño de todos los puntos** | — | [CA:744](src/criterios_adoptados.py:744) |
| `umbral_area_quebrada_importante_ha` | `None` | **vacío — bloquea el TR de toda la Familia A** | — | [CA:778](src/criterios_adoptados.py:778) |
| `v_max_concreto_eleccion` | `None` | **OPCIONAL — no bloquea nada.** Sin declarar, V3 aplica el techo `[N]` de 6.0 m/s de la Tabla N° 10 y el criterio no se registra como usado. Declarándolo se baja ese techo y la `Verificacion` lo atribuye a esta clave. Único criterio `opcional=True` del archivo — que **no** es lo mismo que «el único que se lee con `valor_si_declarado()`», como decía antes esta fila: M2 lee así otras cuatro, no opcionales (SIS-D-03) | (3.0, 6.0) m/s | [CA:1001](src/criterios_adoptados.py:1001) |
| `TW_receptor` | `None` | **vacío** | — | [CA:1181](src/criterios_adoptados.py:1181) |
| `long_max_cuneta` | 200.0 m | declarado | (200.0, 250.0) | [CA:1192](src/criterios_adoptados.py:1192) |
| `remanso_derecho_via` | `None` | **vacío — bloquea V5 para todo punto** | — | [CA:1274](src/criterios_adoptados.py:1274) |
| `TR_evento_extremo` | `None` | **vacío — bloquea V8 para todo punto** | — | [CA:1298](src/criterios_adoptados.py:1298) |
| `phi_relleno_trasdos` | `None` | **vacío** | (30.0, 38.0) ° | [CA:1319](src/criterios_adoptados.py:1319) |
| `c_phi_fundacion` | `None` | **vacío** | — | [CA:1330](src/criterios_adoptados.py:1330) |
| `capacidad_portante_adm` | `None` | **vacío** | — | [CA:1347](src/criterios_adoptados.py:1347) |
| `Mw_licuefaccion` | `None` | **vacío — bloquea la evaluación de licuefacción** | — | [CA:1359](src/criterios_adoptados.py:1359) |
| `demanda_sismica_licuefaccion` | 1000 años | declarado | (475, 1000) | [CA:1377](src/criterios_adoptados.py:1377) |
| `peso_especifico_relleno_kn_m3` | `None` | **vacío — bloquea el término ΣW de V7** | (17.0, 20.0) kN/m³ | [CA:1980](src/criterios_adoptados.py:1980) |
| `talud_terraplen` | `None` | **vacío — bloquea la longitud del conducto en 7.B** | — | [CA:2011](src/criterios_adoptados.py:2011) |
| `espesor_proteccion_salida` | 1.75·d50 | declarado | (1.5, 2.0) | [CA:2049](src/criterios_adoptados.py:2049) |
| `longitud_proteccion_salida` | `None` | **vacío — completa el diseño de la Fase 6** | — | [CA:2060](src/criterios_adoptados.py:2060) |
| `angulo_aletas` | `None` | **vacío** | — | [CA:2078](src/criterios_adoptados.py:2078) |
| `origen_cota_fondo_entrada` | `None` | **vacío — bloquea V4, V7 y el tamizado 7.A**: la cota de fondo de entrada no es columna de §1.2 y hasta esta revisión M5 adoptaba `cota_terreno` dentro del código, sin criterio ni declaración (SIS-A-04) | — | [CA:1218](src/criterios_adoptados.py:1218) |
| ⚠ `factores_carga_aashto` | **γ por combinación (dict completo)** | **NO es `[A]`: es `[C]` y TIENE valor.** Fila conservada, corregida, para quien la buscara aquí. Se verifica como cita en §8 | — | [CA:2104](src/criterios_adoptados.py:2104) |
| ⚠ `peso_especifico_concreto_kn_m3` | **23.56 kN/m³** | **NO es `[A]`: es `[C]` y TIENE valor.** Ídem | (23.5, 24.5) kN/m³ | [CA:2166](src/criterios_adoptados.py:2166) |
| `predimensionamiento_cabezal` | `None` | **vacío — bloquea la estabilidad automática** | — | [CA:2185](src/criterios_adoptados.py:2185) |
| `N_cq_N_gammaq_meyerhof` | `None` | **vacío — bloquea la capacidad portante en talud** | — | [CA:2213](src/criterios_adoptados.py:2213) |
| `metodo_estabilidad_global` | `None` | **vacío — bloquea E4 y E5 de Sec. 9.3** | — | [CA:2244](src/criterios_adoptados.py:2244) |
| ⚠ `recubrimiento_aashto_mm` | **75 mm en las tres condiciones** | **NO es `[A]`: es `[C]` y TIENE valor.** Ídem. Su número está en revisión por otra vía (AASHTO da 3.0 in = 76.2 mm para acero sin recubrir, y con galvanizado o epóxico daría 50.8; falta además el modificador por a/c). Eso NO es este hallazgo | — | [CA:2266](src/criterios_adoptados.py:2266) |
| `cortante_alto_muro_e060_art_11_10_10_2` | `None` | **vacío — bloquea el escalón de ρ a 0.0025 (E.060 Art. 11.10.10.2)** | — | [CA:2299](src/criterios_adoptados.py:2299) |
| ⚠ `procedimiento_flexion_corte_aashto_sec5` | **φ, modelo de corte y β-θ declarados** | **NO es `[A]`: es `[C]` y TIENE valor.** Ídem | — | [CA:2351](src/criterios_adoptados.py:2351) |

De los **30 `[A]`**, **23 están sin valor**: invocarlos lanza
`CriterioPendienteError` y detiene el cálculo. Los **7 con valor declarado** son
`F_pga`, `factor_muro_eleccion`, `k_v`, `long_max_cuneta`,
`demanda_sismica_licuefaccion`, `espesor_proteccion_salida` y `clase_sitio`.
Las cuatro filas ⚠ de arriba **no cuentan** en esos 30: son `[C]`.

Contado sobre el archivo (`Counter(c.etiqueta for c in CRITERIOS.values())`):
**47 criterios · 0 `[N]` · 3 `[N→]` · 1 `[S]` · 13 `[C]` · 30 `[A]`**, y **24
sin valor en total** (los 23 `[A]` más `clases_producto_por_relleno`, el único
`[C]` vacío).

---

## 13. Recuento

**Cómo se cuenta, para que se pueda recontar:** filas de tabla del bloque que
llevan al menos un enlace `archivo:línea` al código. Los números anteriores no
salían de contar así (§1 decía 30 donde hay 33, §3 decía 21 donde hay 24) y
llevaban tiempo desfasados, igual que la distribución de abajo (NOR-MAN-02).

| Bloque | Filas con cita |
|---|---|
| §1 Manual de Hidrología | 33 |
| §2 Manual de Suelos | 14 |
| §3 Manual de Puentes | 24 |
| §4 E.050 | 18 |
| §5 E.060 | 14 |
| §6 EG-2013 | 16 |
| §7 HDS-5 | 16 |
| §8 AASHTO LRFD | 11 |
| §9 Normas de producto ASTM/AASHTO | 13 |
| §10 E.030 (solo referencia) | 4 |
| §10-bis WSDOT Hydraulics Manual | 2 |
| §11 Sin PDF externo (hoja de ruta + otras fuentes) | 14 + 14 |

Distribución de los **50** criterios de `criterios_adoptados.py`, recontada
ejecutando el archivo tras C01:
**0 `[N]`** ·
**2 `[N→]`** (`resguardo_HW_subrasante`, `n_manning_hdpe`) ·
**1 `[S]`** (`PERFIL_SUELO_PRESUNTO`) ·
**14 `[C]`** ·
**33 `[A]`** (§12) ·
**25 sin valor** en total.

> **Qué movió C01** sobre los 47 anteriores: retiró `h_relleno_min_concreto_tmc`
> (`[N→]`, con valor) y añadió cuatro — `cobertura_minima_aashto` (`[C]`, con
> valor), `D_max_catalogo` (`[A]`, con valor), `condicion_pavimento` (`[A]`, sin
> valor) y `espesor_pared_conducto` (`[A]`, sin valor) —, además de partir
> `diametros_normalizados` en dos al sacarle los topes. Los vacíos suben de 24 a
> 25: entran dos y sale ninguno, porque el que se retiró tenía valor.

> **Los números de arriba se recontaron ejecutando el archivo**, y los
> anteriores no lo estaban a pesar de que este mismo párrafo lo afirmaba
> (NOR-MAN-02, SIS-D-02). Decían «46 criterios · 1 `[N→]` · 14 `[C]`», y el
> archivo devolvía 46 · 2 · 13: faltaba `h_relleno_min_concreto_tmc` entre los
> `[N→]` —que el §14.a de este mismo documento describe como analogía— y
> sobraba un `[C]`. Además §12 y §13 se contradecían entre sí (§12 hablaba de
> «33 criterios `[A]`» y de «26 sin valor»).
>
> **Qué cambió desde entonces, y por qué el total es 47 y no 46:** entró
> `origen_cota_fondo_entrada` (SIS-A-04) y `n_manning_hdpe` pasó de `[A]` a
> `[N→]` por la regla de coherencia de §0.1 de la hoja de ruta (SIS-D-11). Las
> etiquetas de `v_max_hdpe` y `v_max_tmc` no se han tocado nunca: eran `[C]` y
> siguen siéndolo; lo que cambió en ellos fue pasar de `[C]` **sin valor** a
> `[C]` **con cita cerrada** (§10-bis).
>
> Contra qué contrastar: `len(CRITERIOS)` y
> `Counter(c.etiqueta for c in CRITERIOS.values())`.

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
   ([CN:111](src/constantes_normativas.py:111)) y el criterio homólogo repite la
   advertencia ([CA:1002-777](src/criterios_adoptados.py:1002)). Los tres topes
   son los que descartan materiales enteros.
3. **`Ks` es una cita que se declara a sí misma como no-tabla**
   ([CN:99](src/constantes_normativas.py:99)): el código dice que NO figura en
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
   ([CA:291](src/criterios_adoptados.py:291), §0.5).

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
de estos vacíos.

**Qué se consolida aquí y qué no** (SIS-D-12). Esta sección anunciaba consolidar
«las filas marcadas Afirmación negativa» —nueve— y entrega **una**, la de §14.a.
No es un trabajo a medias: es que **una afirmación negativa no basta para abrir
un dossier de vacío**. El dossier existe cuando la búsqueda que terminó en nada
**sostiene un valor que entra al cálculo**, y entonces la memoria tiene que
poder mostrarle al revisor la búsqueda entera (el criterio lo ancla con
`vacio_verificado` y M11 la imprime en el bloque de acotaciones). Hoy ese caso
es uno solo: `cobertura_minima_aashto` — y no siempre lo fue el mismo. Hasta
C01 el dossier lo abría `h_relleno_min_concreto_tmc`, y resultó que su búsqueda
no había terminado en nada: había terminado antes de mirar AASHTO LRFD Sec. 12
(`NOR-VAC-01`). El criterio se retiró y el dossier de §14.a pasó a registrar la
búsqueda corregida, que sí está agotada en el corpus **peruano** y por eso
sostiene la adopción de una fuente extranjera que el propio §0.2 ya declara.

Las otras ocho no son ese caso, y conviene no confundirlas:

- **`v_max_hdpe` y `v_max_tmc`** no son vacío agotado sino **cita cerrada**: la
  búsqueda encontró fuente técnica (WSDOT M 23-03.12, Tabla 8-4) y el valor sale
  de ella. Se registran en §10-bis, no aquí, y **no llevan** `vacio_verificado`:
  marcarlos así los imprimiría en la memoria como «lo que el proyectista adoptó
  donde la norma no dice nada», que es lo contrario de lo que pasó. Lo que sí
  queda abierto en ellos es de otro orden —la tabla WSDOT no está en `normas/`,
  luego no es auditable en el repositorio— y está anotado en cada criterio.
- **Las demás** (Sec. 12 de AASHTO no incorporada, las tablas de norma de
  producto, el resto) son afirmaciones negativas que **no sostienen ningún valor
  adoptado**: bloquean o difieren, y su sitio es la fila del bloque de origen y
  el criterio vacío correspondiente, no un dossier.

### 14.a. Cobertura mínima sobre la clave — el vacío que no era un vacío

**Estado: registro CORREGIDO.** Esta sección declaraba un vacío verificado y una
adopción por analogía (`h_relleno_min_concreto_tmc` = 0.30 m `[N→]`). Las dos
cosas cayeron a la vez con `NOR-VAC-01`, y el criterio **se retiró**:

1. **El vacío no estaba agotado.** La búsqueda cerró tres fuentes —normas de
   producto, Manual de Puentes, EG-2013— y **faltó la cuarta**, que además está
   en el propio repositorio y es el cuerpo normativo que §0.2 de la hoja de ruta
   adopta *de extremo a extremo*: **AASHTO LRFD 9.ª ed. (2020), Art. 12.6.6.3
   «Minimum Cover» y Tabla 12.6.6.3-1, pág. impresa 12-22**.
2. **El número era corto.** Esa tabla pone un piso de **12.0 in = 0.3048 m** para
   concreto y para metal, de modo que los 0.30 m adoptados quedaban **5 mm por
   debajo**; y en diámetros grandes no gobierna el piso sino **Bc/8**, que para
   un tubo de concreto de 2.40 m (Bc ≈ 2.9 m) da **≈ 0.36 m**, un 20 % más.
3. **Y se medía desde el punto equivocado** (`MAT-D4`): la cota de clave se
   calculaba con el diámetro **interior**, sin espesor de pared, mientras
   EG-2013 508.07 mide el relleno «desde la clave de la tubería» — la superficie
   **exterior**. Corregir solo uno de los dos defectos dejaba el número corto
   igual: por eso el conflicto #5 del plan de correcciones los trata como un
   único paquete.

Lo que hay hoy en su lugar: `cobertura_minima_aashto` `[C]`
([CA:1538](src/criterios_adoptados.py:1538)), la transcripción de la
Tabla 12.6.6.3-1; `condicion_pavimento` `[A]`, **sin valor**, que decide qué fila
aplica; y `espesor_pared_conducto` `[A]`, **sin valor**, que sitúa la clave
física. El recubrimiento mínimo se **calcula** en
`M7_geometria.altura_recubrimiento` como el mayor entre el mínimo de EG-2013 —que
solo existe para HDPE— y la cobertura mínima de AASHTO.

#### La búsqueda, corregida fuente por fuente

| # | Dónde se buscó | Qué se encontró | Cita |
|---|---|---|---|
| 1 | **AASHTO LRFD 9.ª ed. (2020), Sec. 12** — *la que faltaba* | **Sí lo fija, para los tres tipos de conducto del catálogo.** `Corrugated Metal Pipe: S/8 ≥ 12.0 in.` · `Thermoplastic Pipe: ID/8 ≥ 12.0 in.` sin pavimentar y `ID/2 ≥ 24.0 in.` bajo pavimento · `Reinforced Concrete Pipe: Bc/8 or B′c/8, whichever is greater, ≥ 12.0 in.` bajo zona no pavimentada o techo de pavimento flexible, y `9.0 in.` bajo el fondo de pavimento rígido. Nomenclatura del propio artículo, las **cuatro**: `S` = diámetro de la tubería, `Bc` = diámetro **exterior**, `B′c` = *out-to-out vertical rise of pipe*, `ID` = diámetro interior. Nota al pie: la cobertura se mide desde el techo del pavimento rígido o el fondo del flexible.<br>⚠ **La ficha `NOR-VAC-01` transcribe ese segundo término como «√Bc/8» y no hay ningún radical en la tabla**: la prima de `B′c` es un glifo de SymbolMT (`\uf0a2`) que la extracción de texto convierte en basura. Verificado renderizando la celda. En un conducto **circular** `B′c = Bc`, de modo que el «whichever is greater» se reduce a `Bc/8` | Art. 12.6.6.3 y Tabla 12.6.6.3-1, pág. impresa 12-22 (índice de página 1659 del PDF, 0-based) |
| 2 | **Normas de producto** — AASHTO M 170M, AASHTO M 36, ASTM A760 | **No contienen alturas de relleno admisibles**, y eso se confirma. Lo que se **corrige** (`NOR-PRO-03`) es la atribución: la fórmula «*manufacturing and purchase specification only*» es la **Nota 1 de M 170M** y solo de ella; en **M 36** la exclusión está en **§1.3** y en **A760** en **§1.4**, con otra redacción — la Nota 1 de esas dos habla de láminas con fibra de aramida y post-recubrimiento asfáltico. Sigue siendo cierto que **M 170M clasifica por D-load, no por altura** | M 170M-04 Nota 1; M 36-03(2007) §1.3; A760/A760M-10 §1.4; ver §9 |
| 3 | **Manual de Puentes** (MTC, RD 041-2016-MTC/14) | **No incorporó un capítulo equivalente a la Sección 12 de AASHTO LRFD** y **no fija altura mínima de relleno**. Sí trata estructuras enterradas —IM de componentes enterrados (2.4.3.3.2, pág. 109); filas propias en la Tabla 2.4.5.3.1-**2** de factores γp (pág. 143), no en la ‑1 de combinaciones; cortante en losas de cajón según relleno (2.8.1.3A.6.2, pág. 280); armadura de distribución según relleno (2.9.1.4.6.4.6, pág. 362); exención sísmica de cajones enterrados (pág. 121)—, y **ninguno fija la cobertura mínima**: la usan como entrada. Es el corpus **peruano** el que calla, no el que el proyecto adopta | verificado contra el PDF: págs. impresas 109, 121, 143, 280, 362, 505, 513; ver §3 |
| 4 | **EG-2013, Capítulo V** | **HDPE sí**, concreto y TMC **no**. Las Secciones 505, 506 y 507 solo regulan colocación y compactación y remiten a la Sección 502, que tampoco fija altura mínima de diseño | 508.07, **pág. 984**; 506.02, pág. 959; 507.05/.06 **pág. 973** y 507.08 **pág. 974** (verificadas leyendo el PDF; decían 969-970); ver §6 |

**Lo único que el EG-2013 sí fija, literal** (Subsección 508.07, **pág. impresa
984**, verificada leyendo el PDF — decía 982, ver `NOR-EG-01`):

> «La altura de relleno mínimo desde la clave de la tubería hasta el nivel de
> la subrasante será de 0,30 m.»

Vale para HDPE, y su magnitud es **exactamente la que 7.A calcula**: cota de
subrasante menos cota de clave. Por eso `H_RELLENO_MIN["hdpe"] = 0.30`
([CN:225](src/constantes_normativas.py:225)) sigue siendo `[N]` puro. Lo que ya
**no** se sostiene es que ese 0.30 m sea el recubrimiento mínimo aplicable: para
un HDPE de 1.50 m bajo pavimento, la Tabla 12.6.6.3-1 pide **ID/2 ≥ 24 in =
0.75 m**, dos veces y media más.

#### ⚠ Trampa de vocabulario, anotada para que nadie la vuelva a pisar

El Manual de Puentes **sí** usa la palabra «recubrimiento» para alcantarillas,
en la **Tabla 2.9.1.5.5.3-1 (pág. 378)**, y da **2.0 in / 50 mm**. Ese número
**no sirve aquí**: es el recubrimiento de **concreto sobre el acero de
refuerzo**, no la altura de relleno de tierra sobre la clave. Son dos conceptos
que comparten palabra en español y no tienen ninguna relación. Quien busque
«recubrimiento» en el Manual va a encontrar esa tabla primero, y usarla sería
fijar la rasante de todos los puntos de concreto con un dato de otra cosa.

#### Lo que se retira con el criterio

- **El argumento de conservadurismo apoyado en WSDOT** (`NOR-ANA-01`). Decía que
  el HDPE es el material con menor tolerancia a cobertura reducida y que exigir
  su recubrimiento a los otros dos «no puede quedar del lado inseguro», citando
  WSDOT M 23-03.12 Tabla 8-6 — que **no está en `normas/`** y por tanto no era
  auditable. La Tabla 12.6.6.3-1 **confirma la dirección** (bajo pavimento el
  termoplástico pide ID/2 ≥ 24 in, el valor más alto de la tabla) y **desmiente
  la magnitud**: la analogía era conservadora *en el orden de los materiales* y
  no *en el número*. Con la tabla cableada, ni una cosa ni otra dependen ya de
  una fuente ausente.
- **La verificación de expediente «que la adopción no sustituye»**, en la parte
  que la tabla ya resuelve. Lo que queda abierto es de otro orden y está
  declarado en el propio criterio: el **datum** de la cobertura —la tabla la mide
  desde el fondo del pavimento flexible o el techo del rígido, y 7.A la exige
  sobre la subrasante, lo que es conservador pero es una elección de encuadre— y
  las filas de la tabla que este catálogo no usa.
- **La atribución del calibre por altura a ASTM A-807** (`NOR-PRO-04`): esa
  designación **no aparece ni una vez** en M 170M, M 36 ni A760. La norma de
  diseño estructural del TMC es **ASTM A796/A796M** y la de instalación
  **A798/A798M**; A-807 sí es a la que remiten las Subsecciones 507.05/.06/.08
  del EG-2013, pero para materiales y fabricación. Ver §9.

**Nota constructiva `[N]` que sobrevive al criterio retirado** y se traslada al
comentario de `H_RELLENO_MIN`: el equipo pesado no circula sobre el conducto
antes de que el relleno alcance 0.30 m (Sec. 7.A de la hoja de ruta). Es una
exigencia de **ejecución**, no la altura mínima de diseño, y la cobertura de
AASHTO no la sustituye.
