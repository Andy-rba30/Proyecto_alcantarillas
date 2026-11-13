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
| `area_ha` | ha | Estudio hidrológico | Delimitación de la cuenca aportante. En la Familia A clasifica la fila de la Tabla N° 02. En la Familia B es el **área tributaria de la cuneta** que descarga en el alivio | A y B: obligatoria. Desde T-1 la lee además el contraste de caudal específico Q/A del caudal declarado, en A y en B (cuando la obra no tiene fila en el CSV de cuencas). **Desde T-9 entra en una fórmula en la Familia B** (`INF-5.1.8`), y desde sus correcciones sólo donde es coherente: cuando el tramo de cuneta del alivio **no** se conoce, la Fase 10 reparte el caudal con la escorrentía específica q = Q/A por el ancho tributario y **avisa** si el área y el ancho implican un tramo (A·10⁶/b) mayor que el recorrido máximo de la cuneta —el área no es la faja del tramo—; con el tramo conocido el aporte se reparte como Q / s y el área no entra. C: puede ir vacía |
| `S_cauce` | m/m | Topografía / QGIS | Pendiente del cauce en el cruce (recta ajustada sobre el MDT, 75 m aguas arriba y abajo). En C, la del canal | A y B: obligatoria. C: puede ir vacía y entra por `--datos-externos` |
| `cota_terreno` | msnm | Topografía / QGIS | Cota del terreno natural en el eje, leída del MDT | La carga se detiene |
| `cota_rasante` | msnm | Trazo | Perfil longitudinal del diseño (Civil 3D), tras fijar la rasante en 7.A | La carga se detiene |
| `cota_subrasante` | msnm | Trazo | Rasante menos el espesor del paquete estructural | La carga se detiene |
| `cbr_subrasante` | % | **EMS** | CBR de diseño de la subrasante, de la calicata del tramo. Define el resguardo de V4 | La carga se detiene |
| `esviaje_grados` | ° | Topografía / QGIS | Ángulo entre el eje del conducto y la **perpendicular** al eje de la vía. Ver la §5 | La carga se detiene |
| `ancho_plataforma` | m | Trazo | Sección típica de la vía (DG-2018) | La carga se detiene |
| `cota_fondo_receptor` | msnm | Topografía / QGIS | Fondo del dren, quebrada o canal que recibe la descarga (el script la lee a 13 m del eje, aguas abajo). En un paso de canal (Familia C) es el fondo del **mismo canal** aguas abajo, y desde T-3 VC2 le contrasta la cota de salida en los dos sentidos (aviso, tolerancia `desajuste_empalme_canal_m`) | La carga se detiene |
| `Q_receptor_m3s` | m³/s | **ANA / Junta** | Caudal de diseño del cuerpo receptor. Es la vía 3 del TW (Manning en el receptor). **0 es un receptor seco** y se admite desde T-2 (TW = 0, salida libre); negativo, no | Puede ir vacía en las tres familias; el TW sale por otra vía |
| `cota_TW` | msnm | **ANA / Junta** | Nivel de agua del receptor durante la avenida, ya calculado fuera. Es la vía 2 del TW | Puede ir vacía en las tres familias |
| `sucs_fundacion` | texto | **EMS** | Clasificación SUCS del suelo de fundación, de la calicata más cercana | La carga se detiene. Desde T-4 la lee la matriz de durabilidad para el aviso «suelo de fundación deficiente → marco» (`INF-5.1.9`): compara el grupo con el conjunto del criterio `sucs_fundacion_deficiente` `[A]`; no cambia material ni sección |
| `NF_profundidad_m` | m | **EMS** | Profundidad del nivel freático **en el cruce**, medida por punto. La lee V7 (flotación) | Puede ir vacía; V7 queda pendiente de ese dato |
| `cota_fondo_entrada` | msnm | Topografía / QGIS | Invert de entrada **medido** en el cauce, aguas arriba | Puede ir vacía: rige el criterio `origen_cota_fondo_entrada` (hoy «igual al terreno»), que es una adopción y no una medición (`INF-5.1.18`). Desde T-6 la memoria lo **avisa** («fondo de entrada adoptado igual al terreno de plataforma: medir en el cauce») y marca como provisional el delta de rasante de 7.A; con la celda llena, el dato medido gana y el aviso desaparece |
| `cota_coronacion_canal` | msnm | Topografía / QGIS | La más baja de las dos coronaciones del canal en el cruce. La compara VC1 | Puede ir vacía; en la Familia C, VC1 queda pendiente de ese dato (y con ella el punto: desde T-3 el marco ya no se detiene en sus criterios, sino aquí) |

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
punto o global, o por su bandera de línea de comandos. Las veintiuna claves (ocho hasta
T-2, que sumó `seccion_receptor_medida` y `acceso_mantenimiento_previsto`; doce hasta
T-6, que sumó `bombeo` y `peralte`; dieciocho desde T-8, que sumó las seis de la Fase 6;
veintiuna desde T-9, que sumó las tres de la cuneta de la Fase 10, las tres últimas de
la tabla):

| Clave | Unidad | Origen | Qué es | Si no se declara |
|---|---|---|---|---|
| `luz_m` | m | Topografía / QGIS | Abertura libre que el cruce exige de la estructura. Decide alcantarilla o puente (umbral 6.0 m) | El punto no se clasifica ni se dimensiona |
| `TW_m` | m | **ANA / Junta** (o escenario declarado) | Tirante del receptor sobre el fondo de la salida, declarado a mano. Es la vía 1 del TW y manda sobre las demás | Se intenta `cota_TW`, luego `Q_receptor_m3s`, luego los dos escenarios acotados con `seccion_receptor`; por último, el criterio `TW_receptor` |
| `longitud_m` | m | Trazo | Longitud del conducto, cuando se quiere declarar en vez de calcular (medida sobre la sección transversal del cruce) | La calcula la Fase 7.B con el método del criterio `metodo_longitud_conducto` (por extremo: cotas, ancho, talud, esviaje y pendiente) |
| `Q_m3s` | m³/s | Estudio hidrológico · ANA / Junta | El mismo dato de la columna, para los puntos que la dejan vacía (Familia C) | Vale la celda del CSV |
| `S_conducto` | m/m | Trazo | Pendiente del barril, cuando no es la del cauce. Admite **0** (barril horizontal, HDS-5 num. 3.3.4) desde T-2; negativa, no | Vale `S_cauce`, o el límite de pendiente adoptado (`pendiente_minima_conducto` / `pendiente_maxima_conducto`) cuando la del cauce lo traspasa; la memoria imprime cuál de los orígenes fue (T-6) |
| `S_cauce` | m/m | Topografía / QGIS · ANA / Junta | La misma de la columna, para la Familia C (pendiente del canal) | Vale la celda del CSV |
| `L_hidraulico_m` | m | Estudio hidrológico | Longitud de cuneta a la que se agota su capacidad (Familia B, Fase 10). Declarada **gana** | Desde T-9 la calcula la Fase 10 (M10) con la sección y el revestimiento de la cuneta (criterios `seccion_cuneta` [A], con el mínimo de la Tabla Nº 34 para región muy lluviosa como valor de archivo, y `revestimiento_cuneta` [A]), `S_cuneta` y el aporte del punto: con el tramo del alivio conocido y el caudal declarado, Q / s; si no, la escorrentía específica por `ancho_tributario_m`. Si falta un dato que haga falta, la etapa de espaciamiento del punto se detiene nombrándolo |
| `bombeo` | m/m | Trazo | Bombeo de la plataforma en el cruce, como pendiente transversal media de la semiplataforma (sección típica; DG-2018 núm. 304.05). `0.02` = 2 %. Solo por el JSON. **Excluyente con `peralte`** en un mismo punto | La plataforma se toma horizontal a la cota de rasante, y la memoria lo **avisa** con lo que cada 1 % acortaría la longitud |
| `peralte` | m/m | Trazo | Peralte de la plataforma en el cruce, con signo (DG-2018 núm. 304.06): positivo sube el borde del lado de la **entrada** del conducto y baja el de la salida. Solo por el JSON. **Excluyente con `bombeo`**: una sección tiene uno u otro, y el punto en curva anula un bombeo global declarando `bombeo` = 0 | Vale cero: los dos bordes a la misma cota |
| `categoria_tr` | texto | Estudio hidrológico | Fila de la Tabla N° 02 que corresponde al cauce (quebrada importante o menor) | Familia A: la decide `area_ha` contra el criterio `umbral_area_quebrada_importante_ha`. Familia B: fila fija |
| `seccion_receptor_medida` | objeto: `b_m` (m), `z_HV` (H:V), `S` (m/m), `n` (—), `altura_total_m` (m) | Topografía / QGIS · **ANA / Junta** | Sección **medida** del cuerpo receptor (levantamiento): ancho de solera, talud, pendiente longitudinal, n de Manning y profundidad total. Gana sobre el criterio `seccion_receptor` en las vías 3 y 4 del TW (T-2, `INF-3.2.8`). **En un paso de canal (Familia C) es la sección del MISMO canal**, y desde T-3 la lee además 7.B para la sobreelevación de la lámina del canal y la longitud mínima del remanso aguas arriba (`M7.remanso_canal`, aviso; desde la auditoría de T-3 calcula además el tirante crítico del canal y **no concluye**, sin cifra, si el canal es de pendiente fuerte o si VC2 está fuera de tolerancia) | Rige la sección **adoptada** del criterio `seccion_receptor`, y la memoria lo dice con un aviso: «seccion adoptada [A] por falta de levantamiento». Si se declara incompleta, la carga se detiene: no se completa con la del criterio. En la Familia C, sin ella el remanso del canal sale «no se evaluo», con aviso: la sección adoptada de un dren no sustituye a la del canal |
| `acceso_mantenimiento_previsto` | booleano (`true` / `false`) | **Proyectista** (planos) | Si los planos del punto prevén el acceso de mantenimiento que declara el criterio `acceso_mantenimiento_v2b` (Manual, num. 4.1.1.3.7 d)) (T-2, `INF-0.5`) | No se afirma nada. Con `false`, la memoria y la CLI imprimen un aviso; no cambia ningún veredicto |
| `tipo_terreno_receptor` | texto: una fila de la Tabla N° 11 (`arena_fina_no_coloidal` … `graduado_grava_a_piedras_mayor_20cm`) | **EMS** · reconocimiento del cauce | Material del cauce **receptor**, sobre el que descarga la salida: la fila de la Tabla N° 11 del Manual (velocidades máximas admisibles en canales no revestidos, num. 4.1.1.3.6, pág. 77) (T-8, `INF-3.3.7`) | La Fase 6 dimensiona la protección igual y **avisa** que no comparó la velocidad de salida con la admisible del terreno. Con el dato, el contraste **informa**: si la velocidad la supera, el terreno necesita la protección; si no la supera, el terreno la resistiría según la tabla, y la protección **se mantiene** —suprimirla queda sujeto a inspección de campo (HDS-5 núm. 5.3.2)—. Si la velocidad se tomó al tirante crítico (control de salida con el TW bajo el crítico) es una cota inferior y el contraste no concluye |
| `tipo_terreno_entrada` | texto: una fila de la Tabla N° 11 | **EMS** · reconocimiento del cauce | Material del cauce de **aproximación**, aguas arriba de la entrada: la misma fila (T-8, `INF-5.1.13`) | La protección de entrada declara su revestimiento y **avisa** que no se comparó la velocidad en la boca con la admisible |
| `regimen_flujo_descarga` | texto: `intermitente` / `permanente` | **Estudio hidrológico** | La columna de la Tabla N° 11: si el cauce lleva agua sólo en avenidas o todo el año. Vale para la entrada y para la salida (T-8) | Sin él no se compara con la Tabla N° 11 (el aviso lo nombra) |
| `material_lecho_salida` | objeto: `tipo` (`no_cohesivo` con `D84_m` y `D16_m` en m, o `cohesivo` con `IP` y `Sv_Pa` en N/m²) y `pasa_200_pct` (%) | **EMS** (granulometría, límites de Atterberg, compresión no confinada saturada) | Suelo del lecho a la salida: con él se estima la hoya de socavación local por HEC-14 Cap. 5 (Ec. 5.1 no cohesivo; 5.2–5.4 cohesivo, IP de 5 a 16) y se elige la columna del geotextil de filtro de EG-2013 (Tabla 511-06) (T-8) | La hoya **no se estima** —no se supone un suelo— y la corrida lo avisa; el filtro se declara como requisito sin elegir columna. Un `tipo` sin sus dos campos, o un campo del otro tipo, detiene la carga |
| `duracion_caudal_pico_min` | min | **Estudio hidrológico** | Duración del caudal pico del hidrograma de diseño: el tiempo t de la hoya de socavación de HEC-14 (T-8) | Rige el criterio [A] `duracion_caudal_pico_socavacion_min` (**360 min**, elección del proyecto en la ventana 30–360: HEC-14 num. 5.1.2 recomienda 30 min «lacking this knowledge» y dice que con ellos se alcanza de 2/3 a 3/4 de la hoya máxima): la corrida lo avisa con la profundidad a 30 min al lado. Por debajo de 30 min la fuente dice que sus exponentes no aplican: la hoya se estima con 30 min como cota superior, con aviso |
| `profundidad_socavacion_estimada_m` | m (admite 0: lecho de roca), **medida desde la cota que fija el criterio `referencia_profundidad_socavacion`** (por defecto, el fondo del cauce receptor al pie de la salida) | **Estudio de socavación** del cauce receptor | Profundidad de socavación a la salida de un estudio del cauce. **Gana** sobre la hoya que estima el programa y es la que se entrega al desplante del cabezal de salida (HEC-14 num. 5.1.3), con la cota del fondo de la hoya (T-8) | Se entrega la estimada (si el lecho está declarado) o ninguna, con aviso; si la declarada es menor que la estimada, la corrida lo avisa |
| `ancho_tributario_m` | m | **Trazo** | Ancho de la faja que drena a la cuneta por metro de cuneta: semiplataforma, berma y talud de corte que vierten a ella (sección típica, DG-2018). Familia B (T-9) | Hace falta sólo cuando el tramo del alivio no se conoce o el caudal se calcula: entonces, sin él (ni `L_hidraulico_m`), la Fase 10 no calcula la longitud por capacidad y se detiene nombrándolo. No se deduce del `ancho_plataforma` |
| `S_cuneta` | m/m | **Trazo** | Pendiente longitudinal de la cuneta que descarga en el alivio, la de la rasante en el tramo (perfil longitudinal). Entra a Manning. **No se deriva del CSV**: `cota_rasante` es la rasante en cada cruce, y la pendiente de la cuneta es la local del tramo, con sus curvas verticales. Familia B (T-9) | Sin ella no hay capacidad de la cuneta: **VB2** (el caudal de aporte contra la capacidad, la condición literal del Manual) no se evalúa —con `L_hidraulico_m` declarado, sólo se avisa— y, sin la longitud declarada, la Fase 10 se detiene nombrándola. Fuera de 0.5 % < i < 2 % (Manual de Hidrología núm. 4.1.2 c)) la corrida **avisa**, con el mínimo del DG-2018 (núm. 304.11) al lado |
| `inicio_tramo_cuneta_km` | km (admite 0) | **Trazo** | Progresiva donde empieza, del lado de progresivas **menores**, el tramo de cuneta que descarga en el alivio (punto alto de la rasante, inicio del corte, otra obra de drenaje transversal). **Gana** sobre la obra anterior del CSV; no puede ser posterior a la obra (la etapa se detiene con `DatoInvalidoError`). Familia B (T-9) | El tramo empieza en la obra anterior en progresiva —de Familia B, o de Familia A por el criterio `obras_familia_a_extremo_de_cuneta` (`si` por defecto)—; si no hay ninguna, **VB1 no se evalúa** y es un **bloqueo** del punto que espera este dato: la longitud del tramo no se supone. La cuneta que VB1 no mira (entre la obra anterior y el inicio declarado, y la del lado de progresivas mayores cuando la obra siguiente no es otro alivio) se avisa |

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
| Especificaciones del conducto para la Fase 8: tipo de instalación del tubo de concreto, fabricación del TMC (y, si es empernada, la resistencia de su costura), suelo y compactación del relleno del HDPE, qué hacer con la carga viva bajo relleno alto; importancia operativa de la vía | Especificaciones técnicas del expediente · **Propietario** (la importancia) | T-5 — **hecho**: criterios `[A]` de perfil con ventana (`instalacion_estandar_concreto`, `fabricacion_tmc`, `relleno_estructural_hdpe`, `parametros_diseno_hdpe`, `carga_viva_bajo_relleno_alto`, `eta_importancia_operativa_conducto`) | Rige el valor de archivo, que **no** es en todos «el más desfavorable» (ficha T5-09): Tipo 3 con el Tipo 4 impreso al lado; costura remachada simple —la más débil tabulada—, con aviso de que el EG-2013 507.02 a) describe tubería empernada; relleno granular `Si-95` (EG-2013 508.02 d)); carga viva conservada; η_I = 1.05. Una costura empernada detiene la Fase 8 pidiendo su resistencia |
| **Perfil del tubo de HDPE** que el expediente especifique: área de pared, momento de inercia y diámetro exterior por diámetro nominal (`perfil_hdpe_fabricante`) | **Fabricante** del tubo: catálogo o certificación (EG-2013 508.02 b)) | T-5 — criterio `[A]` **opcional, sin valor por defecto** | El HDPE queda **«no verificado con un producto real»** y **no se adopta**: el punto que solo pueda resolverse con HDPE se detiene con `DatoFaltanteError` sobre `perfil_hdpe_fabricante`, con la cota inferior del perfil mínimo de la Tabla A12-11 de AASHTO LRFD en el mensaje (AASHTO C12.12.3.2: esos mínimos «are not meaningful for design») |
| **D-load de 0.3 mm de las Clases I, III, IV y V de AASHTO M 170M** | **El dueño del proyecto tiene que conseguir un ejemplar LEGIBLE** de la norma de producto (AASHTO M 170M vigente, o ASTM C76M): el de `normas/` solo deja leer la Clase II | T-5 | Solo la Clase II está transcrita (50.0 N/m/mm); un tubo de concreto que pida más **bloquea el punto** con `DatoFaltanteError` sobre `clases_producto_por_relleno`, nombrando las clases que faltan (decisión del dueño, 2026-11-12: no se sube de diámetro para esquivar una clase). Con el Tipo 3 eso son ~2.85 m de relleno sobre un tubo de 0.90 m |
| Parámetros de resistencia del suelo: φ, c, γ, capacidad portante admisible | EMS | T-7b | Los criterios de la Fase 9 están vacíos y el cabezal no se verifica |
| Profundidad de socavación estimada a la salida; tipo de terreno del cauce receptor | Estudio hidrológico · EMS | T-8 — **hecho**: son `tipo_terreno_receptor`, `tipo_terreno_entrada`, `regimen_flujo_descarga`, `material_lecho_salida`, `duracion_caudal_pico_min` y `profundidad_socavacion_estimada_m` de la sección 3 | Sin el terreno, la protección se dimensiona igual (envolvente de Laushey y de HEC-14) y se avisa que no se comparó con la Tabla N° 11; sin el lecho, la hoya no se estima |
| Sección de la cuneta, ancho tributario y pendiente longitudinal de la rasante | Trazo | T-9 — **hecho**: el ancho tributario y la pendiente son `ancho_tributario_m` y `S_cuneta` de la sección 3; la sección es el criterio `seccion_cuneta` [A], con el mínimo de la Tabla Nº 34 para región muy lluviosa (0.40 × 1.20 m) y talud exterior 1:1 adoptados hasta que la sección típica y el EMS digan otra cosa | `L_hidraulico_m` entra declarado, y sigue ganando |
| **Región pluvial del corredor en año FEN**: la precipitación anual que decide la fila de la Tabla Nº 34 del Manual de Hidrología (mínimos de la cuneta) | **Estudio hidrológico** (lo debe el proyecto; no hay dato con trazabilidad en el repositorio) | Correcciones de T-9 — **pendiente** | La sección de archivo de `seccion_cuneta` supone región muy lluviosa (1600 a <3000 mm/año), coherente con los 200 m de `long_max_cuneta`; por encima de 3000 mm/año el mínimo es una sección **trapezoidal** que la Fase 10 no implementa |
| **Velocidad de diseño (V.D.) e IMDA de la vía**, para la fila de la Tabla 304.12 (talud interior de la cuneta) | **Trazo** (clasificación de la vía, DG-2018) · **estudio de tráfico** (lo debe el proyecto) | Correcciones de T-9 — **pendiente** | El talud interior 1:3 de la sección de archivo vale con V.D. < 70 km/h o IMDA < 750; con las dos mayores la tabla pide 1:4. La Fase 10 lo **avisa** en cada capacidad calculada |
| Talud de corte del tramo de cuneta (talud exterior Z2) | **EMS** | Correcciones de T-9 — **pendiente** | Rige Z2 = 1 adoptado (el más empinado de las filas de suelo fino o arenoso de la Tabla 304.10 del DG-2018, lado seguro para la capacidad) |
| Dónde empieza cada tramo de cuneta que descarga en un alivio (`inicio_tramo_cuneta_km`) | **Trazo** (perfil longitudinal y proyecto de drenaje longitudinal) | Correcciones de T-9 — **pendiente** | La obra anterior en progresiva cierra el tramo (B, o A por `obras_familia_a_extremo_de_cuneta`): en el fixture A-02 deja a B-01 con 530 m de cuneta y VB1 no cumple; sin ninguna obra, VB1 es un bloqueo que espera el dato |
| Riesgo admisible y vida útil (`riesgo_admisible_propietario`), desplazamiento sísmico admisible del cabezal, tipo de cabezal | **Propietario** | T-7a, T-7b | Rigen los máximos recomendados de la Tabla N° 02; el resto está sin declarar |

*(La fila de T-4 —ensayos de durabilidad por sitio o por punto— pasó al §3.1 al cerrar T-4.)*

Al terminar la cadena, el programa deja de detenerse por criterios vacíos y se detiene
solo por entradas de esta lista que falten. Es lo que un jurado acepta: «este dato lo da
el estudio X».

**Documentos que el repositorio de normas no tiene y que cerrarían una lectura de la
Fase 6** (segunda auditoría de T-8, 2026-11-12). No son datos del sitio: son fuentes que
hoy se leen de segunda mano, y cada una tiene declarada la lectura que rige mientras falte.

| Documento | Qué cerraría | Mientras falte |
|---|---|---|
| **AASHTO M 288** (Geotextile Specification for Highway Applications) | A qué columnas se aplica la nota de los suelos cohesivos (abertura de 0.30 mm) de la Tabla 511-06 de EG-2013, que es su traducción | Rige la lectura que no relaja: sólo en la columna «>50» (`Interpretacion` de la cita `EG2013.511.08#T511_06`) |
| **Manual de Carreteras de California** (la fuente que la Tabla N° 11 del Manual declara al pie) | Si las filas «Arcilla arenosa / limosa (no coloidal)» son suelos cohesivos o francos («loam») mal traducidos | Se clasifican por el nombre impreso; sólo alimentan el aviso de incoherencia entre el terreno y el lecho declarados |
| **HEC 11** (Design of Riprap Revetment), al que HEC-14 remite el filtro | El diseño del filtro granular bajo el enrocado | El filtro es un requisito declarado, no un dimensionado (ficha T8-02) |
