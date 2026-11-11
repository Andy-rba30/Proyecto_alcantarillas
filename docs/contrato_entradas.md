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
| `Q_m3s` | m³/s | **Estudio hidrológico** (A y B) · **ANA / Junta** (C) | A y B: caudal de la cuenca o de la cuneta con el TR de la Fase 2. C: el caudal de diseño **del canal**, no uno hidrológico | A y B: celda obligatoria. C: puede ir vacía y entra por `--datos-externos`; sin él el punto no se dimensiona |
| `area_ha` | ha | Estudio hidrológico | Delimitación de la cuenca aportante. **Solo clasifica** la fila de la Tabla N° 02 en la Familia A; no entra en ninguna fórmula | A y B: obligatoria (en B hoy no la lee nadie: `INF-5.1.8`). C: puede ir vacía |
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
| `sucs_fundacion` | texto | **EMS** | Clasificación SUCS del suelo de fundación, de la calicata más cercana | La carga se detiene (hoy ningún módulo la lee: `INF-5.1.9`) |
| `NF_profundidad_m` | m | **EMS** | Profundidad del nivel freático **en el cruce**, medida por punto. La lee V7 (flotación) | Puede ir vacía; V7 queda pendiente de ese dato |
| `cota_fondo_entrada` | msnm | Topografía / QGIS | Invert de entrada **medido** en el cauce, aguas arriba | Puede ir vacía: rige el criterio `origen_cota_fondo_entrada` (hoy «igual al terreno»), que es una adopción y no una medición (`INF-5.1.18`) |
| `cota_coronacion_canal` | msnm | Topografía / QGIS | La más baja de las dos coronaciones del canal en el cruce. La compara VC1 | Puede ir vacía; en la Familia C, VC1 queda pendiente de ese dato |

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
| Cuencas por obra (área, longitud y pendiente del cauce, cobertura, suelo) y serie de precipitación máxima de la estación | Estudio hidrológico · SENAMHI | T-1 | El caudal entra ya calculado por `Q_m3s`, que seguirá ganando cuando venga lleno |
| Tratamiento de los años FEN de la serie (`homogeneidad_serie_fen`) | Estudio hidrológico | T-1 | El criterio está vacío y **no detiene nada**: ningún módulo lo lee (`INF-5.1.1`) |
| Sección medida del receptor (ancho de fondo, talud, profundidad, n, pendiente) | Topografía / QGIS · ANA / Junta | T-2 — **hecho**: es `seccion_receptor_medida` de la sección 3 | Rige la sección **adoptada** del criterio `seccion_receptor`, con aviso en la memoria |
| Ensayos de durabilidad por sitio o por punto: sulfatos, cloruros, pH, resistividad, abrasión | EMS | T-4 | La matriz de materiales no filtra por durabilidad |
| Parámetros de resistencia del suelo: φ, c, γ, capacidad portante admisible | EMS | T-7b | Los criterios de la Fase 9 están vacíos y el cabezal no se verifica |
| Profundidad de socavación estimada a la salida; tipo de terreno del cauce receptor | Estudio hidrológico · EMS | T-8 | La protección de salida se calcula solo con el d₅₀ de Laushey |
| Sección de la cuneta, ancho tributario y pendiente longitudinal de la rasante | Trazo | T-9 | `L_hidraulico_m` entra declarado |
| Riesgo admisible y vida útil (`riesgo_admisible_propietario`), desplazamiento sísmico admisible del cabezal, tipo de cabezal | **Propietario** | T-7a, T-7b | Rigen los máximos recomendados de la Tabla N° 02; el resto está sin declarar |

Al terminar la cadena, el programa deja de detenerse por criterios vacíos y se detiene
solo por entradas de esta lista que falten. Es lo que un jurado acepta: «este dato lo da
el estudio X».
