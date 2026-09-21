# Guía de corrida de perfil: de un CSV nuevo a las tres familias dimensionadas

Esta guía es para quien tiene los puntos críticos de una vía en un CSV y
quiere el diseño a **nivel de perfil** de sus alcantarillas sin leer el
código. Va en el orden en que la corrida se detiene, que es el orden en que
uno descubre lo que falta: el programa se para en la **primera** falta de cada
punto y no en todas a la vez, y esta guía las recorre todas de una vez.

Todo lo que aquí se nombra existe como objeto del programa, y la suite lo
comprueba: `tests/test_guia_perfil.py` **ejecuta cada bloque de comandos de
esta guía** en un subproceso, con los archivos que la propia guía muestra, y
afirma lo que la guía promete (cuatro puntos dimensionados al final). Las
tablas marcadas como generadas salen de los símbolos que las gobiernan
(`python -m tests.apoyo.guia_perfil` las imprime) y el mismo test las compara:
si un criterio cambia de forma, el test lo dice antes de que esta página
mienta.

Lo que se necesita: Python 3.11 o superior, `pip install -r requirements.txt`,
y ejecutar los comandos **desde la raíz del repositorio**. Los archivos de
trabajo de la guía se ponen en una carpeta `guia/` y las salidas en
`guia/salida/`; el nombre no importa, la ruta relativa sí.

La fuente normativa es `docs/hoja_de_ruta_alcantarillas_v8.md`; los números de
sección que aparecen aquí («Sec. 1.2») son los de ese documento.

---

## 1. El CSV de puntos críticos

### 1.1 Las columnas, familia por familia

El encabezado del CSV es fijo: las columnas de `M0_carga.COLUMNAS`, en este
orden, y **todas tienen que estar en el encabezado** aunque la celda vaya
vacía (una fila sin una columna es una fila truncada y la carga la rechaza).
La familia de cada punto (Sec. 2.3) decide qué celdas pueden ir vacías:

- **A** — alcantarilla de paso de una quebrada.
- **B** — alcantarilla de alivio de cunetas.
- **C** — cruce de un canal o dren de riego.

<!-- generado: columnas -->
| Columna | Numérica | Familia A | Familia B | Familia C |
|---|---|---|---|---|
| `id` | no | obligatoria | obligatoria | obligatoria |
| `progresiva_km` | no | obligatoria | obligatoria | obligatoria |
| `familia` | no | obligatoria | obligatoria | obligatoria |
| `Q_m3s` | sí | obligatoria | obligatoria | puede ir vacía |
| `area_ha` | sí | obligatoria | obligatoria | puede ir vacía |
| `S_cauce` | sí | obligatoria | obligatoria | puede ir vacía |
| `cota_terreno` | sí | obligatoria | obligatoria | obligatoria |
| `cota_rasante` | sí | obligatoria | obligatoria | obligatoria |
| `cota_subrasante` | sí | obligatoria | obligatoria | obligatoria |
| `cbr_subrasante` | sí | obligatoria | obligatoria | obligatoria |
| `esviaje_grados` | sí | obligatoria | obligatoria | obligatoria |
| `ancho_plataforma` | sí | obligatoria | obligatoria | obligatoria |
| `cota_fondo_receptor` | sí | obligatoria | obligatoria | obligatoria |
| `Q_receptor_m3s` | sí | puede ir vacía | puede ir vacía | puede ir vacía |
| `cota_TW` | sí | puede ir vacía | puede ir vacía | puede ir vacía |
| `sucs_fundacion` | no | obligatoria | obligatoria | obligatoria |
| `NF_profundidad_m` | sí | puede ir vacía | puede ir vacía | puede ir vacía |
| `cota_fondo_entrada` | sí | puede ir vacía | puede ir vacía | puede ir vacía |
| `cota_coronacion_canal` | sí | puede ir vacía | puede ir vacía | puede ir vacía |
<!-- fin: columnas -->

«Puede ir vacía» no significa «no hace falta». Significa que el dato lo debe
otro tablero y no quien llena el CSV, y que la carga no se detiene sin él:
quien se detiene es la etapa que lo necesite, cuando lo necesite. Quién debe
cada vacío está declarado en `M0_carga.VACIOS_ADMITIDOS`:

<!-- generado: vacios -->
- `Q_receptor_m3s`, `cota_TW` — en las tres familias. Lo debe: Tablero 3.1 -- ANA / Junta de Usuarios del Bajo Piura. Si va vacía, la corrida marca la fila como pendiente de ese tablero.
- `Q_m3s`, `area_ha`, `S_cauce` — sólo en Familia C. Lo debe: Tablero 3.1 -- ANA / Junta de Usuarios del Bajo Piura: en un cruce de canal el caudal y la pendiente son los del CANAL, y no los levanta el proyectista vial. Si va vacía, la corrida marca la fila como pendiente de ese tablero.
- `NF_profundidad_m` — en las tres familias. Lo debe: el estudio geotecnico: el NF de cada cruce lo da ese estudio, y se mide por punto. Si va vacía, la corrida marca la fila como pendiente de ese tablero.
- `cota_coronacion_canal` — en las tres familias. Lo debe: el levantamiento topografico del cruce: la seccion transversal del canal con sus dos coronaciones. Si va vacía, la corrida marca la fila como pendiente de ese tablero.
- `cota_fondo_entrada` — en las tres familias. Lo debe: nadie: el proyecto TIENE regla declarada para su ausencia, en el criterio 'origen_cota_fondo_entrada'. Cuando la celda viene, el dato medido manda sobre la regla. Si va vacía, no espera a nadie.
<!-- fin: vacios -->

Dos reglas más de la carga, que no dependen de la familia: una celda
**numérica** con algo que no es un número detiene la carga entera
(`DatoInvalidoError`), y un valor fuera del rango físico posible de
`dominios.py` también. Y `S_cauce` es la pendiente del **cauce** en el cruce,
no la del conducto: son dos datos distintos y se confunden (Sec. 1.5); la del
conducto se declara aparte, en la sección 2.

### 1.2 Antes de correr: el pre-vuelo

No hace falta correr para saber qué falta. `--prevuelo` imprime, sin ejecutar
el cálculo, los criterios vacíos que el alcance puede invocar, el contraste
del CSV, lo que el alcance difiere y **los datos que faltan punto a punto**,
diciendo de cada uno si DETIENE una etapa o si ESPERA a un tablero. Termina
con código 0 si nada detiene una etapa y con 1 si algo lo hace. Sobre el CSV
de ejemplo del repositorio, tal como viene:

```sh id=prevuelo_vacio
python cli.py tests/ejemplo_puntos.csv --alcance perfil --prevuelo
```

Sale con 1 y nombra, entre otras, dos faltas que esta guía va a cubrir: la
**luz** de cada cruce (`luz_m`, que no es columna del CSV) y la **coronación
del canal** de C-01 (`cota_coronacion_canal`, que sí lo es). Es una
estimación por diseño —estima de más, porque la corrida se detiene en la
primera falta y el pre-vuelo las dice todas—; la lista definitiva la da la
corrida.

### 1.3 El CSV de trabajo de esta guía

La guía trabaja sobre una copia del CSV de ejemplo, `guia/puntos.csv`, con
una sola celda rellenada: la coronación del canal en C-01, que el pre-vuelo
acaba de pedir y que en el ejemplo del repositorio está vacía porque la debe
el levantamiento topográfico del cruce. La fila queda así (la cota es
geometría del ejemplo, no un valor de proyecto):

```csv id=fila_c01
C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,38.30
```

Los otros tres puntos (A-01, A-02, B-01) se copian tal cual. Lo que en C-01
sigue vacío —`Q_m3s`, `area_ha`, `S_cauce`— entra por la sección 2.

---

## 2. Lo que no es columna del CSV: `--datos-externos`

Ocho datos entran por un JSON aparte (`servicio.CLAVES_EXTERNAS`). Seis no
son columna del CSV; dos (`Q_m3s`, `S_cauce`) sí lo son y entran también por
aquí porque la Familia C las deja vacías por tablero. La tabla dice de cada
clave si tiene bandera de línea de comandos, qué familias la usan y qué pasa
si no se declara:

<!-- generado: externos -->
| Clave | ¿Columna del CSV? | Tipo | Bandera | Familias que la usan | Si no se declara |
|---|---|---|---|---|---|
| `luz_m` | no | número | `--luz` | las tres | el pre-vuelo la lista como falta |
| `TW_m` | no | número | `--tw` | las tres | el pre-vuelo la lista como falta |
| `longitud_m` | no | número | `--longitud` | las tres | el programa la resuelve por otra vía |
| `Q_m3s` | sí | número | — | las tres | vale la celda del CSV |
| `S_conducto` | no | número | — | las tres | el programa la resuelve por otra vía |
| `S_cauce` | sí | número | — | las tres | vale la celda del CSV |
| `L_hidraulico_m` | no | número | `--l-hidraulico` | B | el pre-vuelo la lista como falta |
| `categoria_tr` | no | texto | `--categoria-tr` | A, B | el programa la resuelve por otra vía |
<!-- fin: externos -->

«Por otra vía» quiere decir: `longitud_m` la calcula la Fase 7.B con las
cotas del CSV; `categoria_tr` cae en el criterio de la Tabla N° 02 (Familia A)
o en la fila fija de la Sec. 2.3 (Familia B); y `S_conducto` cae en
`S_cauce`. `TW_m` tiene además su propia cadena (Sec. 1.3: `cota_TW`, Manning
en el receptor con `Q_receptor_m3s`, y por último el criterio `TW_receptor`).

El archivo tiene dos secciones, las dos opcionales: `globales`, que vale para
todos los puntos, y `puntos`, por `id`. **Un valor por punto pisa al global; una
bandera de la línea de comandos pisa al global del archivo**, de modo que la
precedencia es: por punto > bandera > global. No hay valores por defecto: lo
que no está declarado, no está. Una clave que no sea de la tabla rechaza el
archivo entero (`DatoInvalidoError`), para que una errata no deje un punto
sin luz en silencio.

El JSON de esta guía, `guia/externos.json`:

```json archivo=guia/externos.json
{
  "globales": {"TW_m": 0.3, "L_hidraulico_m": 120.0},
  "puntos": {
    "C-01": {"Q_m3s": 0.85, "S_cauce": 0.006, "S_conducto": 0.006}
  }
}
```

Tres cosas que este archivo decide y conviene leer antes de copiarlo: el TW
global de 0.3 m es un escenario del ejemplo, no un dato de la vía; el caudal y
la pendiente de C-01 son los del **canal** (Sec. 2.3), no los de una cuenca; y
`S_conducto` se declara **igual** que `S_cauce`. La verificación V2b compara la
pendiente del conducto con la del cauce (HDS-5 §5.3.3, indicador de
sedimentación) y, con el valor de archivo del criterio `regimen_v2b`, un
conducto **menos** empinado que el cauce descarta la sección. Esa es la regla
`S_conducto ≥ S_cauce` que el punto C-01 necesita para dimensionar.

La luz va por bandera (`--luz`), porque vale para los cuatro puntos y es lo
primero que la corrida mira: un cruce de 6 m o más es puente y queda fuera del
alcance (Sec. 2.1). Con el CSV de trabajo y este JSON, el pre-vuelo ya no
encuentra nada que detenga una etapa y sale con 0:

```sh id=prevuelo_completo
python cli.py guia/puntos.csv --alcance perfil --prevuelo --luz 2.75 --datos-externos guia/externos.json
```

Lo que sigue apareciendo como «espera» (el nivel freático de cada cruce, la
coronación del canal en los puntos que no son de canal) no es una falta:
espera a un tablero y no detiene el perfil.

---

## 3. Otra obra que no es La Unión: `--datos-sitio`

Los datos de sitio **[S]** —los hechos de ESTE corredor, medidos o leídos de
un mapa, que no elige el proyectista— viven en `src/datos_sitio.py` con los
valores de la obra del repositorio (La Unión). Ese archivo **no se edita** para
calcular otra vía. Otra obra declara los suyos en un `sitio.json`, sólo para
la corrida, por la misma guardia que el archivo (`datos_sitio.establecer_dato_dinamico`):
cada dato lleva `valor`, `trazabilidad` (de dónde salió la lectura: el mapa, el
ensayo, el plano) y `fecha`, y los tres son obligatorios. Lo que se puede
declarar es lo que `datos_sitio.DATOS_SITIO` tiene ficha; una clave nueva se
rechaza (un [S] no se inventa por sesión), y un dato **derivado** tampoco se
declara:

<!-- generado: sitio -->
| Clave | Forma | Nivel | ¿Se declara en sitio.json? | Opciones cerradas |
|---|---|---|---|---|
| `PGA_roca_B` | float | expediente | sí | — |
| `ZONA_SISMICA_LA_UNION` | int | expediente | sí | — |
| `Z_E030` | float | expediente | no: se deriva de `ZONA_SISMICA_LA_UNION` | — |
| `corredor_del_proyecto` | str | perfil | sí | — |
| `orientacion_muro_respecto_al_trafico` | categoria | expediente | sí | `perpendicular_al_trafico`, `paralelo_al_trafico` |
| `distancia_borde_calzada_al_trasdos_m` | float | expediente | sí | — |
| `carriles_por_sentido` | int | perfil | sí | — |
| `clase_de_via` | str | perfil | sí | — |
| `existe_informacion_secundaria_tramo` | categoria | perfil | sí | `si`, `no` |
<!-- fin: sitio -->

La forma se exige en la puerta: `"0.30"` (texto) no es un `float`, `true` no es
un número, y un valor con signo equivocado no entra. Si un dato del archivo
falla, **no se aplica ninguno**: una obra con la mitad de sus [S] sería la obra
equivocada con más silencio.

El `sitio.json` de esta guía declara el corredor y el PGA de una vía que no es
la del repositorio (valores del ejemplo, con la lectura que los sostiene):

```json archivo=guia/sitio.json
{
  "corredor_del_proyecto": {
    "valor": "Via de evitamiento, km 10+000 a 12+000",
    "trazabilidad": "expediente vial del tramo, plano de planta P-01",
    "fecha": "2026-09-21"
  },
  "PGA_roca_B": {
    "valor": 0.30,
    "trazabilidad": "lectura del mapa de isoaceleraciones sobre el punto medio del tramo",
    "fecha": "2026-09-21"
  }
}
```

**Qué pasa si no se declara.** La corrida no se detiene: gobiernan los [S] de
`src/datos_sitio.py`, es decir, los de La Unión, y la consola y la memoria lo
dicen con la **advertencia de corredor** (`datos_sitio.advertencia_de_corredor`):
«Advertencia de corredor: el proyecto se llama «…» y los [S] de esta corrida
gobiernan desde src/datos_sitio.py, que es la obra del repositorio …». La regla
es por **origen** y no por texto: se avisa siempre que el corredor efectivo
salga del archivo, lleve el nombre que lleve el proyecto. La corrida
siguiente, que todavía no declara sitio ni criterios, la muestra:

```sh id=sin_cajon
python cli.py guia/puntos.csv --alcance perfil --luz 2.75 \
  --datos-externos guia/externos.json \
  --proyecto "Via de evitamiento" \
  --json guia/salida/sin_cajon.informe.json
```

Además de la advertencia, su RESUMEN dice esto:

```text id=resumen_sin_cajon
Alcance de la corrida   : perfil
Puntos del expediente   : 4
Puntos dimensionados    : 3
Verificaciones incumplidas: 0
Etapas bloqueadas       : 1
Diferidas por alcance   : 11 (ver ALCANCE DE LA CORRIDA; no cuentan para el cierre)
Expediente cerrado      : no
```

Tres puntos y no cuatro: C-01 es un cruce de canal, su sección es un marco
de concreto, y el marco tiene criterios sin valor que el programa **no rellena
por su cuenta**. El bloque «CRITERIOS PENDIENTES QUE BLOQUEARON UNA ETAPA»
nombra el primero que la corrida encontró (`embocadura_cajon`), y el
pre-vuelo de la sección 1.2 ya había listado los diez. Es la sección 4.

---

## 4. Los criterios [A] de perfil sin valor: cómo se declaran

Un criterio **[A]** es una adopción del proyectista: ni la norma ni una fuente
técnica lo fijan, y el programa no lo sustituye por un valor por defecto
(Sec. 0.7). Los que son de **nivel de perfil** y siguen sin valor en
`criterios_adoptados.py` los devuelve `ca.criterios_de_perfil_sin_valor()`;
cada uno declara la **forma** de su valor (`Criterio.forma`) y la **ventana**
dentro de la que se elige. La tabla sale de esas fichas:

<!-- generado: criterios -->
| Criterio | Etiqueta | Forma | Ventana |
|---|---|---|---|
| `TW_receptor` | [A] | `float` | m >= 0 sobre el fondo de la salida; 0 es salida libre |
| `cobertura_minima_cajon` | [A] | `float` | real >= 0, en metros |
| `embocadura_cajon` | [A] | `str` | la clave de una fila de `HDS5_3ED.TA1`, `HDS5_3ED.TC2` |
| `espesor_pared_cajon` | [A] | `float` | metros, > 0 |
| `homogeneidad_serie_fen` | [A] | `str` | declaracion del tratamiento estadistico |
| `hw_entrada_fuera_de_rango` | [A] | `categoria` | una de: `energia_critica`, `descartar` |
| `ke_entrada_cajon` | [C] | `str` | la clave de una fila de `HDS5_3ED.TC2` |
| `n_celdas_cajon` | [A] | `int` | entero >= 1 |
| `n_manning_cajon` | [N->] | `str` | la clave de una fila de `MC_HHD.T09` |
| `secciones_cajon_normalizadas` | [A] | `serie_de_pares` | serie de pares (B, H) en metros, de menor a mayor, con B y H interiores de UNA celda |
<!-- fin: criterios -->

Siete son **del cajón** (la sección rectangular de la Familia C) y los invoca
cualquier cruce de canal: `embocadura_cajon`, `ke_entrada_cajon`,
`n_manning_cajon`, `n_celdas_cajon`, `secciones_cajon_normalizadas`,
`espesor_pared_cajon` y `cobertura_minima_cajon`. Los otros tres sólo se
invocan en condiciones que este ejemplo no alcanza: `TW_receptor` es la última
puerta del TW (Sec. 1.3) cuando no hay ni `TW_m`, ni `cota_TW`, ni caudal del
receptor; `hw_entrada_fuera_de_rango` sólo cuando la carta de control de
entrada no tiene dominio para el par (Q, S) de un punto (v8 §4.2); y
`homogeneidad_serie_fen` es un hecho sobre la serie de precipitación de la
Fase 1-bis, que este software no procesa.

**Cómo se declara, no qué.** `--declarar CLAVE=VALOR` declara un criterio
**sólo para esa corrida**: el archivo no se toca y la memoria imprime el valor
marcado como declarado. El texto se lee con `ast.literal_eval` —un número, una
lista, un texto entre comillas— y lo que no sea un literal de Python se toma
como texto, que es lo que declara la clave de una fila o una categoría. La
puerta (`_verificar_criterio`) exige la forma y la ventana antes de correr:
un texto no es un `int`, `0,5` con coma decimal no es un número, y una fila
que la tabla no tiene no entra. Un ejemplo sintácticamente válido por criterio; los
valores son los del fixture de la suite y **no son una recomendación** (la
ficha de cada criterio, en `criterios_adoptados.py`, dice qué hay que mirar
para elegir):

```text id=ejemplos_declarar
--declarar TW_receptor=0.0
--declarar cobertura_minima_cajon=0.3048
--declarar embocadura_cajon=cajon_concreto_aletas_30_75
--declarar espesor_pared_cajon=0.20
--declarar "homogeneidad_serie_fen=serie con 1983, 1998 y 2017: ajuste con y sin ellos, adoptado el conservador"
--declarar hw_entrada_fuera_de_rango=energia_critica
--declarar ke_entrada_cajon=cajon_aletas_30_75_escuadra
--declarar n_celdas_cajon=1
--declarar n_manning_cajon=concreto_afinado
--declarar "secciones_cajon_normalizadas=[[1.20,0.90],[1.50,1.20],[2.00,1.50]]"
```

Por forma: un `float` se escribe con punto decimal; un `int` sin decimales;
una `serie_de_pares` como lista de pares `[[B,H],...]` de menor a mayor, entre
comillas porque lleva corchetes; una **fila de tabla** por su clave, tal como
la pestaña 2 de la ventana la lista (la fila trae consigo los números de la
tabla, y por eso lo que se declara es la clave y no el coeficiente); una
`categoria` por una de sus opciones cerradas; y un `str` libre entre comillas
si lleva espacios. El signo de `espesor_pared_cajon` es contraintuitivo y su
ficha lo dice primero: engrosar la pared **empeora** la flotación.

Con los siete del cajón declarados, el `sitio.json` de la sección 3 y las
salidas de la sección 6, la corrida completa de la guía es:

```sh id=perfil
python cli.py guia/puntos.csv --alcance perfil --luz 2.75 \
  --datos-externos guia/externos.json \
  --datos-sitio guia/sitio.json \
  --proyecto "Via de evitamiento" \
  --declarar embocadura_cajon=cajon_concreto_aletas_30_75 \
  --declarar ke_entrada_cajon=cajon_aletas_30_75_escuadra \
  --declarar n_manning_cajon=concreto_afinado \
  --declarar n_celdas_cajon=1 \
  --declarar "secciones_cajon_normalizadas=[[1.20,0.90],[1.50,1.20],[2.00,1.50]]" \
  --declarar espesor_pared_cajon=0.20 \
  --declarar cobertura_minima_cajon=0.3048 \
  --json guia/salida/perfil.informe.json \
  --html guia/salida/memoria.html \
  --csv-resumen guia/salida/resumen.csv
```

La consola dice primero que los datos de sitio se declararon **sólo para esta
corrida** desde `guia/sitio.json` («datos_sitio.py no se modifico»), ya no
imprime la advertencia de corredor, y el RESUMEN dice:

```text id=resumen_perfil
Alcance de la corrida   : perfil
Puntos del expediente   : 4
Puntos dimensionados    : 4
Verificaciones incumplidas: 0
Etapas bloqueadas       : 0
Diferidas por alcance   : 13 (ver ALCANCE DE LA CORRIDA; no cuentan para el cierre)
Expediente cerrado      : si
```

---

## 5. Cómo se lee el RESUMEN

Las seis cifras las calcula una sola vez `Informe.resumen()` (un
`ResumenDeCorrida`) y las leen las tres capas que las imprimen: la consola, la
pestaña 4 de la ventana y el encabezado de la memoria. Significan esto:

- **Puntos del expediente / Puntos dimensionados.** Cuántas filas cargó el CSV
  y cuántas llegaron a una sección aceptada (material, diámetro o marco, con
  sus verificaciones). Un punto **no dimensionado** tiene, en su bloque, la
  razón: un criterio pendiente, un dato que falta o «no factible» con el
  delta de rasante que haría falta.
- **Verificaciones incumplidas.** Las V1…V9, VC1, G1, G2 que se evaluaron y no
  cumplen en la sección aceptada. Un **[AVISO]** (veredicto indicador, como
  V2b bajo `regimen_v2b = indicador_con_aviso`) no cuenta aquí.
- **Etapas bloqueadas.** Las etapas que se detuvieron y **cuentan para el
  cierre**: un `CriterioPendienteError` (falta declarar un criterio), un
  `DatoFaltanteError` (falta un dato), un `DatoInvalidoError`, un
  `DisenoNoFactibleError`. El bloque «CRITERIOS PENDIENTES QUE BLOQUEARON UNA
  ETAPA» dice de cada criterio su concepto, su fuente, qué lo resuelve y en
  qué puntos. La corrida de la sección 3 tenía 1: el cajón de C-01.
- **Diferidas por alcance.** Lo que **esta corrida declaró fuera de su
  alcance** y por eso no cuenta como bloqueo: con `--alcance perfil`, las
  verificaciones V5 (remanso en el derecho de vía) y V8 (evento extremo) se
  intentan y su fallo se difiere; la Fase 8 (estructural del conducto) y la
  Fase 9 (cabezal) no se ejecutan; y en la Familia C la mitad del requisito de
  la Sec. 2.3 que VC1 no mide (la rasante hidráulica del canal) queda
  declarada. Cada una está en el bloque «ALCANCE DE LA CORRIDA» con su
  fundamento, y todas se ejecutan sin cambios con `--alcance expediente`.
- **Expediente cerrado.** `si` sólo si no falta nada **al alcance declarado**:
  todos los puntos dimensionados, ninguna etapa bloqueada y ninguna
  verificación incumplida. Mientras una etapa siga bloqueada dice `no`, y la
  consola añade por qué («Mientras un criterio siga sin valor, la etapa que lo
  invoca se detiene: no se sustituye por un defecto (Sec. 0.7)»); el código
  de salida de la CLI es 1 en ese caso y 0 cuando cierra. **Un `si` a perfil no
  es un expediente completo**: es el perfil cerrado, con las trece etapas
  diferidas impresas y esperando al expediente. Ése es el estado final de esta
  guía, y por eso la corrida de la sección 3 —que todavía tiene el cajón sin
  declarar— dice `no` y la de la sección 4 dice `si`.

---

## 6. Las salidas

Todas salen de la **misma corrida**: el informe se congela al terminar
(`Informe.contexto`), y lo que la memoria y el JSON imprimen es lo que la
corrida usó, no el estado del proceso al exportar.

- **JSON del expediente** (`--json`; por defecto `<csv>.informe.json` junto al
  CSV). Es el volcado completo: por punto, la clasificación, el diseño, las
  verificaciones con su veredicto, los bloqueos y las iteraciones; y aparte
  los datos de sitio con su **origen** (de qué archivo salió cada [S]) y los
  criterios usados, los declarados en caliente y los que bloquearon. Es lo
  que la ventana embebe en la sesión y lo que `--comparar` compara.
- **Memoria de cálculo en HTML** (`--html`). Con `--alcance perfil` usa la
  plantilla de perfil (`memoria_perfil.html`); cada paso lleva su fórmula con
  la cita, la sustitución con la procedencia de cada valor, el umbral con su
  carácter en la fuente y el veredicto, y separa lo que la fuente **dice**, lo
  que el proyecto **lee** y lo que el proyecto **hace**.
- **Memoria en PDF** (`--pdf`). La escribe WeasyPrint; si no está instalado o
  no carga, deja el HTML en su lugar, lo abre en el navegador para `Ctrl+P` y
  lo dice con esas palabras (el README explica la instalación en Windows).
- **CSV resumen** (`--csv-resumen`): el cuadro resumen de la Fase 11, una fila
  por punto, con estas columnas (`M11.COLUMNAS_RESUMEN_CSV`):

  <!-- generado: csv_resumen -->
  `id`, `progresiva`, `familia`, `TR_anios`, `tipo_hidraulico`, `material`, `norma_producto`, `seccion`, `V_erosion_ms`, `V_sedimentacion_ms`, `y_sobre_D`, `HW_m`, `control_gobernante`, `proteccion_d50_m`, `proteccion_espesor_m`, `proteccion_longitud_m`, `tipo_cabezal`
  <!-- fin: csv_resumen -->

- **Sesión.** La escribe la ventana (`python -m gui.app`, botón «Guardar
  sesion»): un JSON con el proyecto, las rutas del CSV, del JSON externo y del
  `sitio.json`, las banderas, el alcance, los criterios declarados con su
  procedencia, los [S] declarados y las corridas con su JSON embebido. Sus
  claves (`sesion.sesion_vacia`):

  <!-- generado: sesion -->
  Formato 3: `formato_version`, `app_version`, `id`, `proyecto`, `csv`, `datos_externos`, `datos_sitio`, `externos`, `alcance`, `criterios`, `sitio`, `csv_sha1`, `corridas`.
  <!-- fin: sesion -->

  La CLI la **lee** con `--sesion` y repone todo por el mismo camino con
  guardia que «Cargar sesion»; una bandera escrita gana a lo que la sesión
  trae, y `--declarar` compone encima. Es la vía por la que la ventana exporta
  el PDF en un proceso aparte. Una sesión mínima que reproduce la corrida de
  la sección 4 (las procedencias van vacías porque `--declarar` no las
  registra; la ventana sí):

  ```json archivo=guia/sesion.json
  {
    "formato_version": 3,
    "app_version": "guia_perfil",
    "id": "guia-perfil",
    "proyecto": "Via de evitamiento",
    "csv": "guia/puntos.csv",
    "datos_externos": "guia/externos.json",
    "datos_sitio": "guia/sitio.json",
    "externos": {"luz_m": "2.75"},
    "alcance": "perfil",
    "criterios": {
      "valores": {
        "embocadura_cajon": "cajon_concreto_aletas_30_75",
        "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
        "n_manning_cajon": "concreto_afinado",
        "n_celdas_cajon": 1,
        "secciones_cajon_normalizadas": [[1.20, 0.90], [1.50, 1.20], [2.00, 1.50]],
        "espesor_pared_cajon": 0.20,
        "cobertura_minima_cajon": 0.3048
      },
      "procedencias": {}
    },
    "sitio": {"valores": {}},
    "csv_sha1": "",
    "corridas": []
  }
  ```

  Con ella, la corrida de la sección 4 se repite sin volver a teclear nada, y
  la CLI dice qué criterios restauró de la sesión **sólo para esta corrida**:

  ```sh id=sesion
  python cli.py --sesion guia/sesion.json --json guia/salida/desde_sesion.informe.json
  ```

  Y el PDF, por la misma vía (si la sesión trae una corrida embebida, la CLI
  dice además si esta corrida la **reproduce** o **difiere**):

  ```sh id=pdf
  python cli.py --sesion guia/sesion.json --json guia/salida/pdf.informe.json --pdf guia/salida/memoria.pdf
  ```

- **Comparar dos corridas** (`--comparar A.json B.json`). Compara dos JSON del
  expediente por identidad de punto (`src/comparador.py`), sin recalcular
  nada, y termina: 0 si son iguales, 1 si difieren, 2 si no se pudo leer. Es
  la misma comparación que hace la pestaña 4 de la ventana y la que la CLI
  hace con la corrida embebida en una sesión. Entre la corrida sin el cajón y
  la completa:

  ```sh id=comparar
  python cli.py --comparar guia/salida/sin_cajon.informe.json guia/salida/perfil.informe.json
  ```

- **Barrido de sensibilidad** (`--barrido CLAVE=v1,v2,...`). Corre el
  pipeline una vez por valor con el criterio declarado a ese valor, compara
  cada corrida con la del primer valor y escribe la tabla; **una clave por
  bandera**, nunca el producto cartesiano, y cada valor pasa la **misma
  puerta** que una declaración (fuera de la ventana no corre nada; un
  criterio de tabla exige `--barrido-fila` o `--barrido-nota`). No arma
  memoria: el barrido es un anexo, no parte del expediente, y `--json` recibe
  el barrido. Sobre el número de celdas del marco, con los otros seis del
  cajón declarados:

  ```sh id=barrido
  python cli.py guia/puntos.csv --alcance perfil --luz 2.75 \
    --datos-externos guia/externos.json \
    --datos-sitio guia/sitio.json \
    --declarar embocadura_cajon=cajon_concreto_aletas_30_75 \
    --declarar ke_entrada_cajon=cajon_aletas_30_75_escuadra \
    --declarar n_manning_cajon=concreto_afinado \
    --declarar "secciones_cajon_normalizadas=[[1.20,0.90],[1.50,1.20],[2.00,1.50]]" \
    --declarar espesor_pared_cajon=0.20 \
    --declarar cobertura_minima_cajon=0.3048 \
    --barrido n_celdas_cajon=1,2 \
    --json guia/salida/barrido.json
  ```

  La tabla dice, por valor y por punto, si el punto dimensiona, qué
  verificaciones cambian de veredicto y qué incumplió en su progresión
  cuando deja de dimensionar.

---

## Lo que esta guía no cubre, para que nadie lo lea como pendiente

La hidrología (el caudal entra por el CSV), el nivel de **expediente** (Fases
8 y 9, V5, V8: `--alcance expediente`), y la ventana (`python -m gui.app`),
que hace lo mismo que estos comandos con la pestaña 1 para las entradas, la 2
para declarar criterios por editores tipados, la 3 para los puntos y la 4
para el resumen, la comparación y la exportación.
