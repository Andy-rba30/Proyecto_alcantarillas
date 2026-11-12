# Contrato de entradas de diseño — lo que el programa recibe y no rellena

**Para qué existe.** El programa calcula con datos que **no produce**: el caudal lo da un
estudio hidrológico, las cotas un levantamiento, el CBR una calicata, el nivel del dren la
Junta de Usuarios. Este documento lista **todas** esas entradas, dice **quién las aporta y
con qué procedimiento**, y deja escrita la regla que gobierna a la cadena T
(`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`) y a cualquier sesión posterior:

> **Las entradas de diseño no se corrigen ni se rellenan.** La cadena T no las rellena:
> valida su forma y su dominio, declara de dónde salen y, cuando una falta y hace falta,
> detiene la etapa con `DatoFaltanteError` (falta el dato) o `CriterioPendienteError`
> (falta una declaración), con un mensaje que dice qué la destraba. **Ninguna entrada de
> esta lista tiene ni tendrá un valor por defecto.** Un número plausible puesto para que
> la corrida avance es el peor error posible en este proyecto (`CLAUDE.md`, «Fuente de
> verdad»).

Lo abrió T-0 (2026-11-11) y lo vigila `tests/test_t0_gobernanza.py`: cada columna de
`M0_carga.COLUMNAS`, cada clave de `servicio.CLAVES_EXTERNAS`, cada dato de
`datos_sitio.DATOS_SITIO` y cada criterio con etiqueta `[S]` tiene que estar nombrado
aquí. Una entrada nueva que no tenga fila en este contrato pone ese test en rojo.

**Lo que este documento NO es.** No es la guía de uso (esa es `docs/guia_perfil.md`, que
dice cómo se llena cada archivo y se ejecuta sola en la suite), ni la ficha de cada
variable (`src/variables_entrada.py` y la ayuda de entrada de la GUI). Es el reparto de
**responsabilidades**: qué estudio debe cada número.

---

## 1. Los cinco orígenes

| Origen | Quién lo aporta | Qué entrega |
|---|---|---|
| **Estudio hidrológico** | El proyectista (hidrología de la tesis), con series de SENAMHI | Caudal de diseño por cuenca, área de cuenca, tratamiento de los años FEN |
| **ANA / Junta de Usuarios** | Autoridad Nacional del Agua y Junta de Usuarios del Bajo Piura (Tablero 3.1 de la hoja de ruta) | Caudal de diseño y geometría de los drenes y canales: el del receptor de toda alcantarilla y el del canal que cruza una obra de Familia C |
| **EMS** | Estudio de Mecánica de Suelos del expediente: calicatas, SPT, ensayos de laboratorio | CBR, clasificación SUCS, nivel freático por cruce, química de suelo y agua, clase de sitio, parámetros de resistencia |
| **Topografía / QGIS** | Levantamiento con dron (MDT) y el script `cotas_esviaje_alcantarillas.py` del repositorio `Cotas-esviaje-alcantarillas` | Cotas de terreno y de fondo, pendiente del cauce, esviaje, coronación de canales |
| **Trazo** | Diseño geométrico de la vía (DG-2018): eje, perfil longitudinal, sección típica | Progresiva, rasante, subrasante, ancho de plataforma, clase de vía, derecho de vía |

Un sexto origen no es un estudio sino una **decisión del Propietario** de la obra (riesgo
admisible, desplazamiento sísmico admisible del cabezal, tipo de cabezal): entra por
criterios declarables y está en la §6.

---

## 2. El CSV de puntos críticos — 19 columnas

El encabezado es el de `M0_carga.COLUMNAS` (los campos de `modelos.PuntoCritico`, en su
orden) y **todas las columnas tienen que estar en el encabezado** aunque la celda vaya
vacía. Qué celdas pueden ir vacías, y en qué familia, lo fija `M0_carga.VACIOS_ADMITIDOS`;
la tabla familia por familia está en `docs/guia_perfil.md` §1.1.

| Columna | Unidad | Origen | Cómo se obtiene | Si falta |
|---|---|---|---|---|
| `id` | — | Trazo | Identificador de la obra en el inventario del proyecto | La carga se detiene |
| `progresiva_km` | km (`0+380` o `0.380`) | Trazo | Cruce del eje con el cauce, la cuneta o el canal | La carga se detiene |
| `familia` | A / B / C | Trazo | A: paso de quebrada. B: alivio de cuneta. C: cruce de canal o dren (hoja de ruta §2.3) | La carga se detiene |
| `Q_m3s` | m³/s | **Estudio hidrológico** (A y B) · **ANA / Junta** (C) | A y B: caudal de la cuenca o de la cuneta con el TR de la Fase 2. C: el caudal de diseño **del canal**, no uno hidrológico | A y B: celda obligatoria, **salvo** que la corrida traiga la cuenca de la obra y la serie de su estación (`--cuencas` y `--estacion`, §2-bis): entonces puede ir vacía y lo calcula el programa. Si viene llena, **gana la celda**. C: puede ir vacía y entra por `--datos-externos`; sin él el punto no se dimensiona |
| `area_ha` | ha | Estudio hidrológico | Delimitación de la cuenca aportante. **Solo clasifica** la fila de la Tabla N° 02 en la Familia A; no entra en ninguna fórmula | A y B: obligatoria. Desde T-1 la lee además el contraste de caudal específico Q/A del caudal declarado, en A y en B (cuando la obra no tiene fila en el CSV de cuencas). C: puede ir vacía |
| `S_cauce` | m/m | Topografía / QGIS | Pendiente del cauce en el cruce (recta ajustada sobre el MDT, 75 m aguas arriba y abajo). En C, la del canal | A y B: obligatoria. C: puede ir vacía y entra por `--datos-externos` |
| `cota_terreno` | msnm | Topografía / QGIS | Cota del terreno natural en el eje, leída del MDT | La carga se detiene |
| `cota_rasante` | msnm | Trazo | Perfil longitudinal del diseño (Civil 3D), tras fijar la rasante en 7.A | La carga se detiene |
| `cota_subrasante` | msnm | Trazo | Rasante menos el espesor del paquete estructural | La carga se detiene |
| `cbr_subrasante` | % | **EMS** | CBR de diseño de la subrasante, de la calicata del tramo. Define el resguardo de V4 | La carga se detiene |
| `esviaje_grados` | ° | Topografía / QGIS | Ángulo entre el eje del conducto y la **perpendicular** al eje de la vía. Ver la §5 | La carga se detiene |
| `ancho_plataforma` | m | Trazo | Sección típica de la vía (DG-2018) | La carga se detiene |
| `cota_fondo_receptor` | msnm | Topografía / QGIS | Fondo del dren, quebrada o canal que recibe la descarga (el script la lee a 13 m del eje, aguas abajo) | La carga se detiene |
| `Q_receptor_m3s` | m³/s | **ANA / Junta** | Caudal de diseño del cuerpo receptor. Es la vía 3 del TW (Manning en el receptor). **0 es un receptor seco** y se admite desde T-2 (TW = 0, salida libre); negativo, no | Puede ir vacía en las tres familias; el TW sale por otra vía |
| `cota_TW` | msnm | **ANA / Junta** | Nivel de agua del receptor durante la avenida, ya calculado fuera. Es la vía 2 del TW | Puede ir vacía en las tres familias |
| `sucs_fundacion` | texto | **EMS** | Clasificación SUCS del suelo de fundación, de la calicata más cercana | La carga se detiene. Desde T-4 la lee la matriz de durabilidad para el aviso «suelo de fundación deficiente → marco» (`INF-5.1.9`): compara el grupo con el conjunto del criterio `sucs_fundacion_deficiente` `[A]`; no cambia material ni sección |
| `NF_profundidad_m` | m | **EMS** | Profundidad del nivel freático **en el cruce**, medida por punto. La lee V7 (flotación) | Puede ir vacía; V7 queda pendiente de ese dato |
| `cota_fondo_entrada` | msnm | Topografía / QGIS | Invert de entrada **medido** en el cauce, aguas arriba | Puede ir vacía: rige el criterio `origen_cota_fondo_entrada` (hoy «igual al terreno»), que es una adopción y no una medición (`INF-5.1.18`) |
| `cota_coronacion_canal` | msnm | Topografía / QGIS | La más baja de las dos coronaciones del canal en el cruce. La compara VC1 | Puede ir vacía; en la Familia C, VC1 queda pendiente de ese dato |

---

## 2-bis. Las dos entradas de la hidrología — `--cuencas` y `--estacion` (T-1)

Son **opcionales y van juntas**. Sin ellas el caudal entra declarado por `Q_m3s`, como
siempre. Con ellas, un punto de Familia A o B que tenga fila en el CSV de cuencas puede
traer `Q_m3s` vacío y el programa lo calcula por el método racional
(`src/modulos/MH_hidrologia.py`, Manual de Hidrología cap. III). **Ninguna columna tiene
valor por defecto**: las obligatorias detienen la carga si faltan, y las opcionales
vacías no se rellenan —lo que cada una habilita está en su fila—. Las líneas que
empiezan por `#` son comentarios.

**CSV de cuencas** — una fila por obra:

| Columna | Unidad | Origen | Qué es | Si falta |
|---|---|---|---|---|
| `id` | — | Trazo | El `id` de la obra en el CSV de puntos | La carga se detiene |
| `area_km2` | km² | **Estudio hidrológico** | Área de la cuenca aportante, delimitada sobre plano. En una alcantarilla de alivio, el área tributaria de la cuneta (plataforma y talud). Desde 10 km² el método racional no se evalúa. **Tiene que decir lo mismo que `area_ha` del CSV de puntos**, que es la que fija el periodo de retorno | La carga se detiene. Si las dos áreas difieren más de un 1 % (un redondeo), el punto se detiene nombrando el par |
| `L_cauce_m` | m | Estudio hidrológico | Longitud del cauce principal, o del recorrido del flujo sobre la superficie cuando el método es de flujo superficial | La carga se detiene |
| `S_cauce_cuenca` | m/m | Estudio hidrológico | Pendiente media del cauce principal, o de la superficie por la que corre el flujo: la que acompaña a `L_cauce_m`. Entra a la fórmula del tiempo de concentración (Kirpich, FAA, Témez) | La carga se detiene |
| `S_terreno` | m/m | Estudio hidrológico | Pendiente media del **terreno** de la cuenca. Con ella la Tabla Nº 08 elige columna, y es la «pendiente promedio de la cuenca» de la ecuación de retardo. **No es** la del cauce y no se rellena con ella | La carga se detiene |
| `cobertura` | clave | Estudio hidrológico | Fila de cobertura de la Tabla Nº 08 —`sin_vegetacion`, `cultivos`, `pastos_vegetacion_ligera`, `hierba_grama`, `bosques_densa_vegetacion`— **o** una superficie de la plataforma vial, que esa tabla no tiene: `pavimento`, `berma_de_tierra`, `talud_de_tierra`, `talud_con_cesped` (criterio [C] `coeficiente_escorrentia_superficie_vial`, WSDOT Table 2-2, con su incremento por periodo de retorno) | La carga se detiene |
| `suelo` | clave | Estudio hidrológico · EMS | Tipo de suelo de la Tabla Nº 08: `impermeable`, `semipermeable`, `permeable`. **Vacía** cuando `cobertura` es una superficie vial | La carga se detiene (con cobertura de cuenca vacía; con superficie vial, llena) |
| `estacion` | texto | Estudio hidrológico | Nombre de la estación cuya serie representa a la cuenca; tiene que estar en el CSV de la estación | La carga se detiene |
| `metodo_tc` | clave | Estudio hidrológico | Método del tiempo de concentración, **por cuenca**: `kirpich` y `california_culverts_practice` (cauce; salieron de cuencas con pendientes de 3 a 10 %), `federal_aviation_administration` (flujo superficial: plataforma, talud, cuenca plana), `retardo_scs` (pide `CN`; cuencas de menos de 800 ha) o `temez` (0.25 a 24 h; trae consigo el coeficiente K). Fuera de la población de una fórmula decide el criterio `tc_fuera_de_la_poblacion_del_metodo` | La carga se detiene |
| `H_desnivel_m` | m | Topografía / QGIS | **Opcional.** Desnivel entre la divisoria y la salida | Sólo lo exige el método de California: sin él, ese punto se detiene. No se deduce de S·L |
| `ajuste_kirpich` | clave | Estudio hidrológico | **Obligatoria con `metodo_tc = kirpich`**, vacía con cualquier otro: `ninguno`, `superficie_de_concreto_o_asfalto` (×0.4) o `canal_de_concreto` (×0.2), de la observación de la Tabla Nº 05. «`ninguno`» es una clave y se escribe | La carga se detiene: una celda vacía no elige la fila sin factor |
| `CN` | — | Estudio hidrológico | **Opcional.** Número de curva de la cuenca (mayor que 0, hasta 100). El programa no tiene tabla de la que leerlo | Sólo lo exige `retardo_scs`: sin él, ese punto se detiene |

**CSV de la estación** — una fila por año; un archivo puede traer varias estaciones:

| Columna | Unidad | Origen | Qué es | Si falta |
|---|---|---|---|---|
| `estacion` | texto | **SENAMHI** | Nombre de la estación | La carga se detiene |
| `anio` | año | SENAMHI | Año del registro; uno por año y estación | La carga se detiene |
| `p24_mm` | mm | SENAMHI | Precipitación máxima en 24 horas de ese año. Un **0** es un dato y se admite (excluye a la log normal, y la memoria lo dice) | La carga se detiene |
| `fen` | `si` / `no` | **Estudio hidrológico** | Si ese año fue del fenómeno El Niño. Es un **hecho** que declara quien entrega la serie; el programa no lo deduce del valor | La carga se detiene: la serie tiene que declarar sus años FEN, **año por año**. Una celda vacía no se lee como «no» |

Qué se hace con los años FEN **no** es una columna: es el criterio
`homogeneidad_serie_fen` (`serie_completa`, `serie_sin_fen` o `dos_poblaciones`), sin
valor de archivo, que se declara con `--declarar`. Rige sólo el caudal que el programa
**calcula**: a un `Q_m3s` declarado no se le atribuye ningún tratamiento. Declarar
`serie_sin_fen` cuando da **menos** lluvia que la serie completa incumple la regla de
la hoja de ruta (adoptar el más conservador) y **detiene** el cálculo hidrológico del
punto, con las dos lluvias en el mensaje: el remedio es declarar `serie_completa` o
traer el caudal del estudio en `Q_m3s` (ficha `T1-09`). Si da igual o más, pasa. Los años faltantes de la serie no se rellenan: la serie entra
como está, y la memoria imprime de qué periodo es, cuántos años tiene y cuáles le
faltan. Con menos de 5 años no hay ajuste; con menos de 25, un aviso.

Cuatro criterios más gobiernan el cálculo y tienen valor de archivo: la duración mínima
de la lluvia de diseño (`duracion_minima_lluvia_min`, [C], 5 min), el trato de una
cuenca fuera de la población de su fórmula (`tc_fuera_de_la_poblacion_del_metodo`, [A],
«no evaluar»), el coeficiente de uniformidad con la fórmula de Témez
(`coeficiente_uniformidad_temez`, [A], «aplicar») y el coeficiente de las superficies
viales (`coeficiente_escorrentia_superficie_vial`, [C]).

---

## 3. Datos externos — `--datos-externos` y sus banderas

Lo que no es columna del CSV entra por un JSON aparte (`servicio.CLAVES_EXTERNAS`), por
punto o global, o por su bandera de línea de comandos. Las diez claves (ocho hasta T-2,
que sumó las dos últimas):

| Clave | Unidad | Origen | Qué es | Si no se declara |
|---|---|---|---|---|
| `luz_m` | m | Topografía / QGIS | Abertura libre que el cruce exige de la estructura. Decide alcantarilla o puente (umbral 6.0 m) | El punto no se clasifica ni se dimensiona |
| `TW_m` | m | **ANA / Junta** (o escenario declarado) | Tirante del receptor sobre el fondo de la salida, declarado a mano. Es la vía 1 del TW y manda sobre las demás | Se intenta `cota_TW`, luego `Q_receptor_m3s`, luego los dos escenarios acotados con `seccion_receptor`; por último, el criterio `TW_receptor` |
| `longitud_m` | m | Trazo | Longitud del conducto, cuando se quiere declarar en vez de calcular | La calcula la Fase 7.B con las cotas, el ancho y el esviaje |
| `Q_m3s` | m³/s | Estudio hidrológico · ANA / Junta | El mismo dato de la columna, para los puntos que la dejan vacía (Familia C) | Vale la celda del CSV |
| `S_conducto` | m/m | Trazo | Pendiente del barril, cuando no es la del cauce. Admite **0** (barril horizontal, HDS-5 num. 3.3.4) desde T-2; negativa, no | Vale `S_cauce` |
| `S_cauce` | m/m | Topografía / QGIS · ANA / Junta | La misma de la columna, para la Familia C (pendiente del canal) | Vale la celda del CSV |
| `L_hidraulico_m` | m | Estudio hidrológico | Longitud de cuneta a la que se agota su capacidad (Familia B, Fase 10) | Se detiene la etapa de espaciamiento (Fase 10) del punto: el dato no se deduce |
| `categoria_tr` | texto | Estudio hidrológico | Fila de la Tabla N° 02 que corresponde al cauce (quebrada importante o menor) | Familia A: la decide `area_ha` contra el criterio `umbral_area_quebrada_importante_ha`. Familia B: fila fija |
| `seccion_receptor_medida` | objeto: `b_m` (m), `z_HV` (H:V), `S` (m/m), `n` (—), `altura_total_m` (m) | Topografía / QGIS · **ANA / Junta** | Sección **medida** del cuerpo receptor (levantamiento): ancho de solera, talud, pendiente longitudinal, n de Manning y profundidad total. Gana sobre el criterio `seccion_receptor` en las vías 3 y 4 del TW (T-2, `INF-3.2.8`) | Rige la sección **adoptada** del criterio `seccion_receptor`, y la memoria lo dice con un aviso: «seccion adoptada [A] por falta de levantamiento». Si se declara incompleta, la carga se detiene: no se completa con la del criterio |
| `acceso_mantenimiento_previsto` | booleano (`true` / `false`) | **Proyectista** (planos) | Si los planos del punto prevén el acceso de mantenimiento que declara el criterio `acceso_mantenimiento_v2b` (Manual, num. 4.1.1.3.7 d)) (T-2, `INF-0.5`) | No se afirma nada. Con `false`, la memoria y la CLI imprimen un aviso; no cambia ningún veredicto |

Un dato externo que **todavía no tiene clave**: el ancho del derecho de vía por punto,
`ancho_derecho_via_m` (origen: **Trazo**, la resolución que aprueba el derecho de vía del
tramo). La hoja de ruta lo declara dato externo desde T-0 (fila V5 de la Fase 5) y el
programa lo reclama con `DatoFaltanteError` cuando V5 llega a pedirlo; no hay todavía
puerta por la que declararlo.

### 3.1 Ensayos de durabilidad — opcionales, por el mismo JSON (T-4)

Seis claves más entran por `--datos-externos`, en la sección `globales` (valen para todo
el sitio) o en `puntos` (una calicata; pisa al del sitio). **Son opcionales y ninguna
tiene valor por defecto**: no están en `servicio.CLAVES_EXTERNAS` —esas son datos que
alguna etapa exige— sino en `servicio.CLAVES_DE_DURABILIDAD`, y su ausencia no detiene
nada. Las aplica la matriz de durabilidad de la Fase 3 (`M2.matriz_durabilidad`, hoja de
ruta §3.4). La cadena T no las rellena ni las deduce.

| Clave | Unidad | Origen | Qué es | Qué hace la matriz con ella |
|---|---|---|---|---|
| `sulfatos_suelo_ppm` | ppm (mg/kg) | **EMS** | Sulfato soluble en agua (SO₄) presente en el suelo. La Tabla 4.4 de E.060 lo lee en % en peso: 1 % = 10 000 ppm | Fija la exposición del concreto y le **exige** cemento, a/c y f'c. No excluye |
| `sulfatos_agua_ppm` | ppm | **EMS** | Sulfato (SO₄) en el agua, la otra escala de la misma tabla | Ídem; con las dos, rige la más exigente |
| `cloruros_ppm` | ppm | **EMS** | Cloruros en suelo o agua | Para el concreto **avisa** (E.060 4.4.2 no da umbral en ppm). Para la TMC, sobre 100 ppm el suelo cuenta como agresivo por analogía con AASHTO LRFD 11.10.6.4.2a: **aviso** y exigencia de protección (o exclusión, si se declara `suelo_agresivo_lrfd_sobre_tmc` = `excluye`) |
| `pH` | — | **EMS** | pH del suelo o del agua | Fuera de 5.0–8.5 **excluye la TMC**; menor de 5.8 le **exige** protección; fuera de 5–10, suelo agresivo por analogía |
| `resistividad_ohm_cm` | ohm·cm | **EMS** | Resistividad del suelo o del agua | Menor de 1000 **excluye la TMC**; menor de 3000, suelo agresivo por analogía (**aviso**) |
| `abrasion` | texto | **Estudio hidrológico · campo** | Nivel de abrasión del sitio, uno de los cuatro de la Tabla 8-4 del WSDOT Hydraulics Manual: `no_abrasivo`, `poco_abrasivo`, `moderadamente_abrasivo`, `severamente_abrasivo`. Depende de la carga de fondo y de la pendiente además de la velocidad: **no se deduce de la velocidad** | Severo **excluye el HDPE**; moderado o severo **avisa** al metal y al concreto |

**Si no se declara ninguna**, la matriz no actúa, los tres materiales siguen candidatos y
la memoria de cada punto imprime «durabilidad: sin ensayos, matriz no aplicada» (más el
aviso fijo del Manual para la TMC, que no depende de ensayos). Los sulfatos son **el
mismo ensayo** que el dato de sitio `exposicion_quimica_ems` (recubrimiento del cabezal):
si los dos están declarados y dan exposiciones distintas, la matriz lo avisa. Cada
concentración admite de 0 a 1 000 000 ppm.

---

## 4. Datos de sitio `[S]`

Un `[S]` es un hecho determinado por un procedimiento normativo aplicado a **este** sitio:
no es elección del proyectista ni se defiende con un rango, sino con la trazabilidad de la
lectura (`CLAUDE.md`, «Taxonomía de etiquetas»).

### 4.1 De corredor — `src/datos_sitio.py`, o `--datos-sitio` para otra obra

| Clave | Origen | Procedimiento |
|---|---|---|
| `corredor_del_proyecto` | Trazo | El tramo de vía al que se aplica el expediente; ámbito de los demás `[S]` |
| `PGA_roca_B` | Lectura de mapa (Manual de Puentes, Apéndice A3) | Aceleración pico en roca, TR 1000 años, leída de la isolínea en las coordenadas del corredor |
| `ZONA_SISMICA_LA_UNION` | Lectura de tabla (E.030, zonificación por distritos) | Zona sísmica del distrito |
| `Z_E030` | **Derivado** de la zona | No se declara: sale de `ZONA_SISMICA_LA_UNION` por la Tabla N° 1 de E.030 |
| `orientacion_muro_respecto_al_trafico` | Trazo | Si el trasdós del cabezal es perpendicular o paralelo al tráfico (elige tabla de h_eq en AASHTO 3.11.6.4) |
| `distancia_borde_calzada_al_trasdos_m` | Trazo | Distancia del trasdós al borde de la calzada (sección típica) |
| `carriles_por_sentido` | Trazo | De la sección típica; fija el número de calicatas (Manual de Suelos, Cuadro 4.1) |
| `clase_de_via` | Trazo (estudio de demanda, IMDA) | Clase de carretera; elige fila del Cuadro 4.1 y de la Tabla 304.09 del DG-2018 |
| `existe_informacion_secundaria_tramo` | EMS | Si hay estudios geotécnicos previos en el tramo (Manual de Suelos, num. 4.2) |

### 4.2 Pendientes de ensayo — en `src/criterios_adoptados.py`, con `trazabilidad`

| Clave | Origen | Qué ensayo lo cierra |
|---|---|---|
| `clase_sitio` | **EMS** | Caracterización de los 100 ft (30.48 m) superiores: Vs30 o N̄ (AASHTO LRFD 3.10.3.1). Sin valor: las fuentes prohíben suponerla |
| `PERFIL_SUELO_PRESUNTO` | **EMS** | Perfil de suelo de E.030 (S0–S5). Lleva un valor **presunto** declarado como tal, sin ensayo que lo cierre |
| `exposicion_quimica_ems` | **EMS** | Ensayo químico de suelo y de agua freática: sulfatos, cloruros, sales solubles, y la condición de exposición del elemento (E.060 Cap. 4) |

### 4.3 Por punto — son columnas del CSV

`NF_profundidad_m` y `cbr_subrasante` son `[S]` que varían de un cruce a otro y por eso
viajan en el CSV (§2).

---

## 5. La convención de esviaje

**En el programa, 0° = perpendicular.** `esviaje_grados` es el ángulo entre el eje del
conducto y la **perpendicular** al eje de la vía: un cruce a escuadra vale 0° y la longitud
del conducto se alarga con `1 / cos(esviaje)` (`M7_geometria.factor_esviaje`), que vale 1
en el cruce perpendicular. El dominio es `0 ≤ esviaje < 90` (`dominios.ESVIAJE_MAX`): a 90°
el conducto sería paralelo a la vía y no habría cruce. Es la convención de HDS-5, del
Manual de Hidrología del MTC y del script de QGIS, que mide «el ángulo entre la línea del
cauce y la perpendicular al eje».

**Muchos expedientes usan la contraria: 90° = perpendicular.** Miden el ángulo entre el
conducto y el **eje** de la vía, de modo que un cruce a escuadra se tabula como 90°. Es el
caso del expediente de referencia de la tesis («2.7 Estudio de Estructuras de Obras de
Arte y Drenaje», tablas 3 a 6), y de la mayoría de los inventarios viales. Antes de copiar
un esviaje de un expediente a la columna `esviaje_grados` hay que saber cuál de las dos
usa, y si es la segunda, convertir:

```
esviaje_app = 90° − esviaje_expediente
```

| En el expediente (90° = perpendicular) | En el programa (0° = perpendicular) |
|---|---|
| 90° (a escuadra) | 0° |
| 75° | 15° |
| 60° | 30° |
| 45° | 45° |

**El programa no puede detectar el error por sí solo**: 75° es un valor válido en las dos
convenciones. Copiado sin convertir, un cruce casi perpendicular entra como uno muy
esviado y el conducto sale 3.9 veces más largo de lo que es (`1 / cos 75°`). La única
defensa es este contrato y la revisión en planta: el script de QGIS avisa de todo esviaje
mayor de 45° justamente por eso.

---

## 6. Lo que la cadena T añade como entrada — y tampoco rellena

Los prompts T-1 a T-9 abren puertas nuevas para datos que hoy no tienen por dónde entrar.
Cada una nace **vacía**, opcional o con `DatoFaltanteError`, y ninguna trae valor de
archivo. Se listan aquí para que el reparto de responsabilidades quede escrito antes de
que existan; cuando cada prompt cierre, su entrada pasa a las tablas de arriba con su
nombre definitivo.

| Qué | Origen | Prompt | Mientras no exista |
|---|---|---|---|
| Cuencas por obra (área, longitud y pendiente del cauce, cobertura, suelo) y serie de precipitación máxima de la estación | Estudio hidrológico · SENAMHI | T-1 | **Hecho en T-1: ver la §2-bis.** Sin ellas el caudal entra ya calculado por `Q_m3s`, que sigue ganando cuando viene lleno |
| Tratamiento de los años FEN de la serie (`homogeneidad_serie_fen`) | Estudio hidrológico | T-1 | **Hecho en T-1.** El criterio sigue sin valor de archivo y ya tiene consumidor: detiene el cálculo hidrológico del punto cuando el caudal lo calcula el programa, y sólo avisa cuando el caudal entra declarado |
| Sección medida del receptor (ancho de fondo, talud, profundidad, n, pendiente) | Topografía / QGIS · ANA / Junta | T-2 — **hecho**: es `seccion_receptor_medida` de la sección 3 | Rige la sección **adoptada** del criterio `seccion_receptor`, con aviso en la memoria |
| Parámetros de resistencia del suelo: φ, c, γ, capacidad portante admisible | EMS | T-7b | Los criterios de la Fase 9 están vacíos y el cabezal no se verifica |
| Profundidad de socavación estimada a la salida; tipo de terreno del cauce receptor | Estudio hidrológico · EMS | T-8 | La protección de salida se calcula solo con el d₅₀ de Laushey |
| Sección de la cuneta, ancho tributario y pendiente longitudinal de la rasante | Trazo | T-9 | `L_hidraulico_m` entra declarado |
| Riesgo admisible y vida útil (`riesgo_admisible_propietario`), desplazamiento sísmico admisible del cabezal, tipo de cabezal | **Propietario** | T-7a, T-7b | Rigen los máximos recomendados de la Tabla N° 02; el resto está sin declarar |

*(La fila de T-4 —ensayos de durabilidad por sitio o por punto— pasó al §3.1 al cerrar T-4.)*

Al terminar la cadena, el programa deja de detenerse por criterios vacíos y se detiene
solo por entradas de esta lista que falten. Es lo que un jurado acepta: «este dato lo da
el estudio X».
