"""
constantes_normativas.py
========================
Anexo B de docs/hoja_de_ruta_alcantarillas_v8.md, copiado literalmente.

Solo constantes [N] con numeral verificado. Todo [N->], [C] y [A] vive en
`criterios_adoptados.py`. No agregar aqui ningun valor que no venga con su
numeral: si falta, se declara alla como criterio adoptado, no aqui.

Unidades: SI (m, m3/s, m/s, MPa donde se indica, mm en recubrimientos).

ADVERTENCIA DE DOBLE DEFINICION
-------------------------------
Dos bloques de este anexo tienen un homologo en `criterios_adoptados.py`,
porque la hoja de ruta los incluyo aqui aun siendo [C] (eran tres: el tercero,
H_RELLENO_MIN, dejo de tener homologo al retirarse
'h_relleno_min_concreto_tmc' -- ver abajo):

    D_INICIO / D_PASO           <->  criterio "diametros_normalizados"
    HDS5_INLET                  <->  criterio "hds5_embocadura_hdpe" (HDPE)

La inconsistencia Clase D/F que motivo la v5 fue exactamente esto: el mismo
parametro definido en dos lugares (Sec. 0.7). Para el CALCULO, la fuente unica
es `criterios_adoptados.py`; lo de aqui queda como referencia trazable del
Anexo B.

La prohibicion es POR CLAVE, no por bloque entero. Un modulo no debe leer de
aqui la clave que tiene homologo declarado; las demas filas de esos mismos
diccionarios no tienen homologo y se leen de aqui, que es su unica fuente:

    HDS5_INLET      las filas de concreto y de TMC no tienen criterio
                    homologo (son lectura directa de la Tabla A.1 de HDS-5) y
                    M2 las lee de aqui. La fila de HDPE, no: esa sale del
                    criterio 'hds5_embocadura_hdpe'.
    H_RELLENO_MIN   YA NO TIENE HOMOLOGO. Su criterio gemelo,
                    'h_relleno_min_concreto_tmc', se retiro: el recubrimiento
                    minimo ya no es un escalar por material sino un calculo
                    (M7.altura_recubrimiento) sobre la Tabla 12.6.6.3-1 de
                    AASHTO LRFD, que vive en el criterio
                    'cobertura_minima_aashto'. De este archivo sale hoy solo
                    el minimo de EG-2013, que es [N] y solo existe para HDPE.
    D_INICIO / D_PASO   la progresion sale siempre del criterio
                    'diametros_normalizados'. Los topes ya no estan aqui:
                    ver el bloque de diametros normalizados, mas abajo.

La frase anterior era categorica ("Ningun modulo debe leer los bloques
citados desde este archivo") y describia mal lo que el propio bloque de arriba
acota clave por clave; M2 documenta la reparticion en su docstring y la marca
con comentarios de linea. Queda escrita aqui para que no haya que deducirla.
"""

# ================= Manual de Hidrologia (RD 20-2011-MTC/14) =================
LUZ_MAX_ALCANTARILLA = 6.0          # m; >= 6.0 -> puente (4.1.1.3.1 / 4.1.1.5.1)

# --- Diametro minimo de seccion circular: num. 4.1.1.3.4 a), pag. impresa 72 -
# El numero suelto se lee como un piso incondicional y NO lo es. El numeral
# trae dos condicionantes y la transcripcion literal los conserva porque el
# proyecto no puede evaluar el primero y SI cae dentro del segundo (NOR-HID-03,
# MAT-O19):
DIAMETRO_MIN = 0.90                 # m (4.1.1.3.4 a), pag. impresa 72
DIAMETRO_MIN_TEXTO = (
    "En carreteras de alto volumen de transito y por necesidad de limpieza y "
    "mantenimiento de las alcantarillas, se adoptara una seccion minima "
    "circular de 0.90 m (36\") de diametro o su equivalente de otra seccion, "
    "salvo en cruces de canales de riego donde se adoptaran secciones de "
    "acuerdo a cada diseno particular.")
DIAMETRO_MIN_AMBITO = (
    "CONDICION 1 -- 'carreteras de alto volumen de transito': la clase de via "
    "del corredor NO esta cerrada (depende del IMDA del estudio de demanda), "
    "de modo que el proyecto no puede afirmar que se cumple. El piso se aplica "
    "igual a las Familias A y B, y esa es una ADOPCION declarada, no una "
    "lectura automatica del numeral. "
    "SU DIRECCION NO ES UNIFORMEMENTE CONSERVADORA, y decirlo importa porque "
    "lo contrario -- 'mas seccion nunca puede ser peor' -- es intuitivo y es "
    "falso. Mas diametro da mas capacidad y mas borde libre, o sea es "
    "conservador para V1; y da MENOS velocidad para el mismo caudal, o sea "
    "va CONTRA el piso de autolimpieza de V2. Ejemplo real, concreto con "
    "n_max = 0.013, S = 0.001 y Q = 0.0035 m3/s: D = 0.75 m da 0.2554 m/s y "
    "cumple V2; D = 0.90 m da 0.2488 m/s y NO cumple. En ese caudal, aplicar "
    "el piso sin que la condicion del numeral este establecida puede declarar "
    "no factible un punto que un conducto mas chico resolveria. Es una "
    "consecuencia de la adopcion, no un defecto del calculo, y se declara "
    "aqui para que quien cierre el IMDA sepa que hay algo que revisar. "
    "CONDICION 2 -- 'salvo en cruces de canales de riego': la Familia C de "
    "este expediente ES un conjunto de cruces de canal, y el numeral la "
    "EXCEPTUA expresamente: alli la seccion se adopta 'de acuerdo a cada "
    "diseno particular' y este piso no rige. El catalogo de conductos "
    "circulares no entrega candidatos para esa familia, de modo que ningun "
    "punto suyo recibe el piso -- pero hasta ahora la razon escrita era solo "
    "la forma de la seccion (Sec. 2.3 de la hoja de ruta) y no esta excepcion "
    "normativa, que es la que gobierna.")

# --- Diametro minimo recomendado en selva alta: num. 4.1.1.3.7 a), pag. 79 ---
# El nombre anterior (DIAMETRO_MIN_SELVA_ALTA) omitia las tres restricciones
# que el numeral pone y que el valor solo no lleva (NOR-HID-12): es una
# RECOMENDACION, es solo para TMC, y esta condicionada a cuatro caracteristicas
# fisicas y geomorfologicas. El nombre nuevo lleva dos de las tres y el texto
# literal la tercera.
DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO = 1.22   # m = 48" (4.1.1.3.7 a), pag. 79
DIAMETRO_MIN_TMC_SELVA_ALTA_TEXTO = (
    "Se recomienda utilizar, en zonas de selva alta, con las caracteristicas "
    "fisicas y geomorfologicos indicadas en el parrafo anterior, como diametro "
    "minimo alcantarillas TMC Ø 48\".")
DIAMETRO_MIN_TMC_SELVA_ALTA_CONDICIONES = (
    "Las cuatro caracteristicas del parrafo anterior, que el numeral exige "
    "para que la recomendacion aplique: cauces encajonados, en V, inactivos o "
    "con flujo permanente de agua; pendientes entre 5% y 60%; suelo de taludes "
    "y lecho de material granular (aluvial, coluvial, con matriz fina de arena "
    "y limos, gravas y gravillas), vulnerable a erosion pluvial; vegetacion "
    "arbustiva en taludes. NO APLICA EN COSTA, que es donde esta este "
    "corredor (La Union, Piura).")

Y_SOBRE_D_MAX = 0.75                # borde libre >= 25% (4.1.1.3.7 b), pag. 79
# Texto que fija Y_SOBRE_D_MAX, literal (MC-HHD, RD 20-2011-MTC/14,
# num. 4.1.1.3.7 b) "Borde libre", pag. impresa 79):
#
#     "Se recomienda que el diseño hidráulico considere como mínimo el 25 % de
#     la altura, diámetro o flecha de la estructura."
#
# SE TRANSCRIBE POR LO MISMO QUE V_MIN, Y ESO ES EL DEFECTO QUE CIERRA
# (MAT-O13, NOR-HID-10): el 0.75 y el 0.25 salen del MISMO tipo de frase --
# "se recomienda" -- del mismo apartado 4.1.1.3, y hasta ahora solo V_MIN
# llevaba el matiz. Un revisor que viera "recomienda, no prohibe" en V2 y un
# numeral pelado en V1 leeria que el borde libre es una exigencia y el piso de
# velocidad no, cuando la fuente los escribe igual. Los dos se aplican como
# umbral duro por decision conservadora del proyecto, y las dos veces eso es
# una ADOPCION que la memoria tiene que declarar.
V_MIN = 0.25                        # m/s (4.1.1.3.6, pags. 76-77) -- ver abajo
# Texto que fija V_MIN, literal (MC-HHD, RD 20-2011-MTC/14, num. 4.1.1.3.6,
# parrafo inmediatamente posterior a la Tabla Nº 10; ARRANCA en la pag.
# impresa 76 y el numero se imprime en la 77):
#
#     "Se deberá verificar que la velocidad mínima del flujo dentro del
#     conducto no produzca sedimentación que pueda incidir en una reducción de
#     su capacidad hidráulica, recomendándose que la velocidad mínima sea igual
#     a 0.25 m/s."
#
# Se transcribe entero y no solo el numero porque el parrafo fija dos cosas
# que el 0.25 suelto pierde. Primera: el numeral RECOMIENDA, no prohibe --
# V2 lo aplica como umbral duro por decision conservadora del proyecto, y ese
# matiz viaja hasta la memoria por DOS vias, no una: dentro de M5.NUMERAL_V2
# (que solo se imprime si el punto llego a evaluarse) y dentro de
# UMBRALES_DE_VERIFICACION, que M11 imprime SIEMPRE (NOR-MEM-01: la memoria
# generada no llevaba el matiz ni una sola vez, porque el pipeline se detiene
# antes de V2 y la unica via era la tabla de verificaciones del punto).
# Segunda: la razon del minimo es la SEDIMENTACION que reduce capacidad, no el
# desgaste; por eso vale igual para todos los materiales, mientras que el techo
# de la Tabla Nº 10 cambia con el material. Es el mismo numeral que la Tabla
# Nº 10, de modo que sin el titulo de la tabla y sin este parrafo los dos
# limites se confunden -- que es exactamente el error que V3 tenia.
LAUSHEY_K = 3.1                     # d50 = V^2/(3.1*g), metrico (4.1.1.3.7 c)
G_LAUSHEY = 9.8                      # m/s2; g tal como lo escribe la Sec.
                                     # 4.1.1.3.7 c) junto a su formula de d50.
                                     # Uso exclusivo de M6 (Laushey). La
                                     # gravedad generica del resto del script
                                     # (M4: tirante critico, control de
                                     # salida) es constantes_fisicas.G = 9.81,
                                     # no esta -- ver constantes_fisicas.py.
# GAMMA_AGUA_KN_M3 ya no vive aqui: es una constante FISICA, no una exigencia
# normativa. El num. 2.4.3.8.2 del Manual de Puentes dice como se calcula la
# subpresion, no cuanto pesa el agua -- ningun numeral peruano fija eso. Vive
# en constantes_fisicas.py, y ademas DERIVADA (RHO_AGUA * G), para que el
# proyecto tenga una sola gravedad. Mismo criterio ya aplicado a G.

# ---------------------------------------------------------------------------
# Tabla N 02 -- riesgo admisible (num. 3.6, pag. impresa 25)
# ---------------------------------------------------------------------------
# TRANSCRITA COMPLETA: seis filas, aunque el calculo use dos (NOR-HID-07,
# NOR-HID-08). Las cuatro filas que el script no consume no sobran -- son las
# que dejan ver que la fila de la alcantarilla de cuneta es la MISMA que la de
# quebrada menor, y que el drenaje de plataforma tiene otra.
TABLA_02_TITULO = ("TABLA Nº 02: VALORES MAXIMOS RECOMENDADOS DE RIESGO "
                   "ADMISIBLE DE OBRAS DE DRENAJE")
TABLA_02_COLUMNAS = ("TIPO DE OBRA", "RIESGO ADMISIBLE (**) ( %)")
TABLA_02_TEXTO_PREVIO = (
    "De acuerdo a los valores presentados en la Tabla Nº 01 se recomienda "
    "utilizar como maximo, los siguientes valores de riesgo admisible de obras "
    "de drenaje:")
# Nota al pie (**), literal. Es normativa y es la que cambia el CARACTER de
# toda la tabla: el titulo dice "valores maximos RECOMENDADOS" y el pie asigna
# la decision al Propietario. El proyecto adopta los maximos recomendados, que
# es el extremo MENOS conservador del margen que la tabla concede (mas riesgo
# admisible -> menos TR -> menos caudal de diseno), y esa adopcion se declara
# en la memoria porque no es una lectura automatica del numeral.
TABLA_02_NOTA_VIDA_UTIL = (
    "(**) Vida Util considerado (n): Puentes y Defensas Ribereñas n = 40 anios; "
    "Alcantarillas de quebradas importantes n = 25 anios; Alcantarillas de "
    "quebradas menores n = 15 anios; Drenaje de plataforma y Sub-drenes "
    "n = 15 anios.")
TABLA_02_NOTA_PUENTES = (
    "(*) - Para obtencion de la luz y nivel de aguas maximas extraordinarias. "
    "- Se recomienda un periodo de retorno T de 500 anios para el calculo de "
    "socavacion.")
TABLA_02_NOTA_IMPORTANCIA = (
    "Se tendra en cuenta, la importancia y la vida util de la obra a "
    "disenarse.")
TABLA_02_NOTA_PROPIETARIO = (
    "El Propietario de una Obra es el que define el riesgo admisible de falla "
    "y la vida util de las obras.")
# Las cuatro notas de la tabla, en el orden en que la pagina las imprime. La
# fila "Puentes (*)" llevaba su marcador y la nota no estaba transcrita: un
# (*) colgando en una transcripcion que se anuncia completa.
TABLA_02_NOTAS = (TABLA_02_NOTA_PUENTES, TABLA_02_NOTA_VIDA_UTIL,
                  TABLA_02_NOTA_IMPORTANCIA, TABLA_02_NOTA_PROPIETARIO)
# clave de calculo -> (nombre literal de la fila, R en tanto por uno, n anios)
TABLA_02_FILAS = {
    "puentes": {
        "fila": "Puentes (*)", "R": 0.25, "n": 40},
    "quebrada_importante": {
        "fila": "Alcantarillas de paso de quebradas importantes y badenes",
        "R": 0.30, "n": 25},
    "quebrada_menor": {
        "fila": ("Alcantarillas de paso quebradas menores y descarga de agua "
                 "de cunetas"),
        "R": 0.35, "n": 15},
    "drenaje_plataforma": {
        "fila": "Drenaje de la plataforma (a nivel longitudinal)",
        "R": 0.40, "n": 15},
    "subdrenes": {
        "fila": "Subdrenes", "R": 0.40, "n": 15},
    "defensas_riberenas": {
        "fila": "Defensas Ribereñas", "R": 0.25, "n": 40},
}
# Las DOS filas que el calculo de la Fase 2 consume. Se derivan de la
# transcripcion completa en vez de repetir los numeros: si la transcripcion se
# corrige, esta vista se corrige con ella y no quedan dos copias que puedan
# divergir (el mismo motivo por el que 'n_manning_hdpe' LEE de MANNING).
RIESGO_ADMISIBLE = {
    clave: {"R": TABLA_02_FILAS[clave]["R"], "n": TABLA_02_FILAS[clave]["n"]}
    for clave in ("quebrada_importante", "quebrada_menor")
}   # -> TR = 71 y 35 anios
# TR = 1 / (1 - (1-R)**(1/n))       # sin piso normativo

# ---------------------------------------------------------------------------
# Tabla N 09 -- coeficiente de rugosidad de Manning (num. 4.1.1.3.6, pag. 75)
# ---------------------------------------------------------------------------
# TRANSCRITA COMPLETA EN LO QUE AL PROYECTO LE TOCA, con las TRES columnas y
# con las SUBFILAS separadas (NOR-HID-11). Los dos defectos que cierra:
#
#   1. La tabla tiene MINIMO / NORMAL / MAXIMO y el codigo llevaba dos
#      columnas. La columna NORMAL es la de uso corriente y no aparecia por
#      ningun lado; ahora esta transcrita, y por que el calculo no la usa esta
#      dicho abajo en vez de deducirse de su ausencia.
#   2. "Metal corrugado" tiene DOS subfilas -- sub-dren (0.017/0.019/0.021) y
#      dren para aguas lluvias (0.021/0.024/0.030) -- y el codigo tomaba la
#      segunda bajo la clave generica 'metal_corrugado', sin declarar la
#      eleccion. El par (0.021, 0.030) coincide ademas con el MAXIMO de la
#      primera subfila, de modo que la confusion no se detectaba leyendo los
#      numeros. Las claves llevan ahora la subfila en el nombre y M2 declara
#      cual aplica a cada material y por que.
#
# POR QUE EL CALCULO USA MINIMO Y MAXIMO Y NO NORMAL: por la regla de doble n
# (Sec. 4.1 de la hoja de ruta), que no pide el valor corriente sino los dos
# EXTREMOS -- n maximo para capacidad y tirante, n minimo para velocidad
# maxima y socavacion --, de modo que cada verificacion se resuelva con el
# extremo que la deja del lado seguro. El valor NORMAL no entra en ninguna de
# las dos ramas: entraria en un calculo de un solo n, que es justo lo que la
# regla prohibe.
TABLA_09_TITULO = ("TABLA Nº 09: Valores del Coeficiente de Rugosidad de "
                   "Manning (n)")
TABLA_09_COLUMNAS = ("TIPO DE CANAL", "MINIMO", "NORMAL", "MAXIMO")
TABLA_09_FUENTE_TABLA = "Hidraulica de Canales Abiertos, Ven Te Chow, 1983"
TABLA_09_GRUPO = ("A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO "
                  "-- el unico grupo de la tabla que describe una alcantarilla; "
                  "los grupos B (canales revestidos), C (excavado) y D "
                  "(corrientes naturales) describen el cauce, no el conducto, y "
                  "no se transcriben aqui porque ningun modulo dimensiona un "
                  "cauce")
TABLA_09_FILAS = {
    "metal_corrugado_subdren": {
        "fila": "A.1 METALICOS - c. Metal corrugado - sub - dren",
        "min": 0.017, "normal": 0.019, "max": 0.021},
    "metal_corrugado_dren_aguas_lluvias": {
        "fila": "A.1 METALICOS - c. Metal corrugado - dren para aguas lluvias",
        "min": 0.021, "normal": 0.024, "max": 0.030},
    "concreto_tubo_recto": {
        "fila": ("A.2 NO METALICOS - a. Concreto - tubo recto y libre de "
                 "basuras"),
        "min": 0.010, "normal": 0.011, "max": 0.013},
    "madera_duelas": {
        "fila": "A.2 NO METALICOS - b. Madera - duelas",
        "min": 0.010, "normal": 0.012, "max": 0.014},
    # HDPE no listado -> criterios_adoptados.valor("n_manning_hdpe")
}
# Vista de calculo: (n_min, n_max) por fila. Derivada de la transcripcion, no
# copiada de ella. n_max -> capacidad y tirante ; n_min -> velocidad MAXIMA y
# socavacion. El piso de velocidad (V2) NO sale de n_min: sale de n_max, que
# es la estimacion BAJA de velocidad -- ver `M3_hidraulica.resolver_manning`.
MANNING = {clave: (fila["min"], fila["max"])
           for clave, fila in TABLA_09_FILAS.items()}

# ---------------------------------------------------------------------------
# Tabla N 10 -- velocidades maximas admisibles (num. 4.1.1.3.6, pag. 76)
# ---------------------------------------------------------------------------
# TITULO LITERAL, CON LA UNIDAD. El repo lo entrecomillaba sin "(m/s)"
# (NOR-HID-06) en los tres sitios donde lo cita, y la unidad omitida es lo
# primero que un revisor comprueba en una cita entre comillas.
TABLA_10_TITULO = ("TABLA Nº 10: Velocidades maximas admisibles (m/s) en "
                   "conductos revestidos")
TABLA_10_COLUMNAS = ("TIPO DE REVESTIMIENTO", "VELOCIDAD (M/S)")
TABLA_10_FUENTE_TABLA = "HCANALES, Maximo Villon B."
TABLA_10_TEXTO_PREVIO = (
    "Se debe tener en cuenta la velocidad, parametro que es necesario "
    "verificar de tal manera que se encuentre dentro de un rango, cuyos "
    "limites se describen a continuacion.")
# Cada fila con su nombre LITERAL y sus valores tal como la tabla los imprime:
# la mamposteria trae UN solo valor, no un par (NOR-HID-07). Escribirla como
# (2.0, 2.0) inventaba un par que la fuente no escribe.
TABLA_10_FILAS = {
    "concreto":            {"fila": "Concreto", "valores": (3.0, 6.0)},
    "ladrillo_c_concreto": {"fila": "Ladrillo con concreto",
                            "valores": (2.5, 3.5)},
    "mamposteria_piedra":  {"fila": "Mamposteria de piedra y concreto",
                            "valores": (2.0,)},
    # TMC y HDPE no listados -> criterios_adoptados
}
# QUE SIGNIFICAN LOS DOS NUMEROS, Y QUE PARTE DE ESO ES DEL MANUAL Y QUE PARTE
# ES DEL PROYECTO (NOR-HID-04). Del Manual, verificado:
#   - el titulo dice "Velocidades maximas admisibles (m/s)" y la unica columna
#     de valores se rotula "VELOCIDAD (M/S)": los dos numeros son MAXIMOS, y
#     ninguno es un piso. Esa lectura se sostiene y es la que V3 aplica.
#   - el piso de velocidad esta APARTE, en el parrafo siguiente (V_MIN), y vale
#     para todos los materiales por igual.
#   - la fila de mamposteria trae un solo valor.
#   - la fuente de la tabla no es el MTC: es HCANALES, Maximo Villon B.
# Del proyecto, NO del Manual -- y hasta ahora se imprimia pegado a la cita
# como si fuera de la fuente: la explicacion de POR QUE hay dos numeros ("el
# rango recorre la calidad del revestimiento; el inferior es el maximo del
# acabado mas pobre"). El Manual no lo dice en ninguna parte, y ademas la
# frase con que introduce la tabla apunta en otra direccion ("se encuentre
# dentro de un rango, cuyos limites se describen a continuacion") y la fila de
# mamposteria, con un solo numero, no encaja con una lectura de acabados. Es
# INTERPRETACION DEL PROYECTISTA, razonable y declarada como tal; lo que la
# fuente sostiene es solo que los dos numeros son maximos.
TABLA_10_INTERPRETACION_PROYECTO = (
    "INTERPRETACION DEL PROYECTISTA, NO DEL MANUAL: que los dos numeros de una "
    "fila recorran la calidad del revestimiento -- el superior para el acabado "
    "de mejor calidad y el inferior para el mas pobre -- es una lectura que "
    "este proyecto adopta para poder elegir un techo mas conservador dentro de "
    "la fila ('v_max_concreto_eleccion'). El Manual NO la escribe: solo dice "
    "que la tabla da velocidades maximas admisibles. En contra de esta lectura "
    "juegan dos hechos de la propia fuente: la frase que introduce la tabla "
    "habla de un 'rango' con 'limites', y la fila de mamposteria trae un solo "
    "valor. A favor juega el titulo, que es lo unico que decide que ninguno de "
    "los dos numeros sea un piso. Se imprime SIEMPRE separada de la cita.")
# Vista de calculo: los valores de la fila, tal cual. V3 aplica el MAYOR (el
# techo del acabado de mejor calidad) y no verifica el menor: el piso de
# velocidad es V_MIN, no el extremo inferior de esta fila.
V_MAX = {clave: fila["valores"] for clave, fila in TABLA_10_FILAS.items()}

# ---------------------------------------------------------------------------
# El CARACTER de cada umbral que el proyecto verifica
# ---------------------------------------------------------------------------
# Existe por NOR-MEM-01, que es un defecto del PRODUCTO y no del codigo: el
# matiz "el numeral recomienda, no prohibe" viajaba solo dentro de
# M5.NUMERAL_V2, o sea dentro de la tabla de verificaciones de cada punto. Esa
# tabla no se imprime si el punto no llego a evaluarse -- y hoy no llega,
# porque 'homogeneidad_serie_fen' bloquea el Q de toda la Familia A --, de modo
# que la palabra "recomend" aparecia CERO veces en la memoria generada mientras
# el repositorio afirmaba que era "lo unico que la memoria imprime de V2".
#
# Un umbral aplicado como exigencia cuando la fuente lo escribe como
# recomendacion es una decision del proyecto, no una lectura de la norma, y se
# declara. Al reves -- imprimir "exigencia" donde la fuente recomienda -- es
# una cita falsa, que es la clase de defecto que la Sec. 0.5 de la hoja de ruta
# llama la mas grave: "un vacio se ve; una cita falsa se cree".
#
# `caracter` es lo que la FUENTE hace (recomendacion / exigencia) y
# `aplicacion` lo que el PROYECTO hace con ello. Los dos se imprimen juntos y
# separados: sin el segundo no se ve la decision, sin el primero se inventa una
# exigencia.
#
# `texto` es una TUPLA de citas VERBATIM, y esa forma es deliberada. En la
# primera version era una sola cadena y en dos entradas -- TR y V3 -- llevaba
# prosa del proyecto y una tabla reformateada bajo el rotulo "Texto literal".
# Rotular como literal lo que no lo es es exactamente el defecto NOR-HID-06,
# reintroducido por el bloque construido para cerrarlo. Lo que no es cita
# verbatim va en `transcripcion`, con su propio rotulo.
UMBRALES_DE_VERIFICACION = (
    {"codigo": "V1",
     "que": "Borde libre: y/D <= 0.75 (minimo 25 % de borde libre)",
     "numeral": "MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.7 b) 'Borde libre', "
                "pag. impresa 79",
     "caracter": "RECOMENDACION",
     "texto": ("Se recomienda que el diseño hidraulico considere como minimo "
               "el 25 % de la altura, diametro o flecha de la estructura.",),
     "aplicacion": "Se aplica como umbral DURO (un punto con y/D > 0.75 se "
                   "marca 'NO cumple'). Es la lectura conservadora y es "
                   "decision del proyecto, no exigencia del numeral."},
    {"codigo": "V2",
     "que": "Velocidad minima de autolimpieza: V >= 0.25 m/s",
     "numeral": "MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.6, parrafo posterior "
                "a la Tabla Nº 10; arranca en la pag. impresa 76 y el valor se "
                "imprime en la 77",
     "caracter": "RECOMENDACION",
     "texto": ("Se debera verificar que la velocidad minima del flujo dentro "
               "del conducto no produzca sedimentacion que pueda incidir en "
               "una reduccion de su capacidad hidraulica, recomendandose que "
               "la velocidad minima sea igual a 0.25 m/s.",),
     "aplicacion": "Se aplica como umbral DURO, y se evalua con la velocidad "
                   "de la rama de n MAXIMO -- la estimacion BAJA de velocidad "
                   "--, que es el extremo conservador para un piso. La razon "
                   "del minimo es la sedimentacion que reduce capacidad, no el "
                   "desgaste: por eso vale igual para todos los materiales."},
    {"codigo": "V3",
     "que": "Velocidad maxima admisible del revestimiento",
     "numeral": "MC-HHD (RD 20-2011-MTC/14), Tabla Nº 10 'Velocidades maximas "
                "admisibles (m/s) en conductos revestidos', num. 4.1.1.3.6, "
                "pag. impresa 76. Fuente de la tabla: HCANALES, Maximo Villon B.",
     "caracter": "EXIGENCIA (tabla de valores admisibles)",
     "texto": (TABLA_10_TITULO,
               TABLA_10_TEXTO_PREVIO),
     "transcripcion": ("Filas de la Tabla Nº 10, con su nombre literal y los "
                       "valores tal como la tabla los imprime: "
                       + " ; ".join(
                           f"{fila['fila']} = "
                           + " - ".join(f"{v}" for v in fila["valores"])
                           for fila in TABLA_10_FILAS.values())
                       + " (m/s). No es una cita: es la tabla reordenada en "
                         "una linea. La fila de mamposteria trae UN solo "
                         "valor, no un par."),
     "aplicacion": "Los DOS numeros de la fila son MAXIMOS: se verifica solo el "
                   "superior, y el inferior NO es un piso. Se evalua con la "
                   "velocidad de la rama de n MINIMO -- la estimacion ALTA --, "
                   "que es el extremo conservador para un techo. TMC y HDPE no "
                   "tienen fila en esta tabla: su techo sale de un criterio [C] "
                   "con fuente WSDOT."},
    {"codigo": "TR",
     "que": "Riesgo admisible y vida util con que se calcula el periodo de "
            "retorno (Tabla Nº 02)",
     "numeral": "MC-HHD (RD 20-2011-MTC/14), Tabla Nº 02, num. 3.6, "
                "pag. impresa 25",
     "caracter": "RECOMENDACION -- MAXIMOS, y la decision es del Propietario",
     # Las tres citas van SEPARADAS y verbatim, incluida la mayuscula del
     # titulo impreso: unidas en un parrafo explicativo dejaban de ser citas.
     "texto": (TABLA_02_TITULO,
               TABLA_02_TEXTO_PREVIO,
               TABLA_02_NOTA_PROPIETARIO),
     "aplicacion": "El proyecto adopta los valores maximos recomendados de la "
                   "tabla (R = 30 % / n = 25 anios para quebrada importante; "
                   "R = 35 % / n = 15 anios para quebrada menor y descarga de "
                   "cunetas). ADVERTENCIA QUE HAY QUE LEER: adoptar el MAXIMO "
                   "recomendado es el extremo MENOS conservador del margen que "
                   "la tabla concede -- mas riesgo admisible da menos TR y "
                   "menos caudal de diseno --, y a diferencia de V1 y V2 aqui "
                   "la lectura conservadora seria adoptar MENOS. El "
                   "Propietario tiene una via declarada para ejercer la "
                   "decision que la nota al pie le asigna: el criterio "
                   "adoptado 'riesgo_admisible_propietario', que aparece en "
                   "el bloque de criterios de esta memoria y que solo admite "
                   "endurecer el techo, nunca aflojarlo. Mientras no la use, "
                   "esta adopcion gobierna el TR de todos los puntos."},
    {"codigo": "D_min",
     "que": "Seccion minima circular de 0.90 m",
     "numeral": "MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.4 a), pag. impresa 72",
     "caracter": "EXIGENCIA CONDICIONADA ('se adoptara', con dos condiciones)",
     "texto": (DIAMETRO_MIN_TEXTO,),
     "aplicacion": DIAMETRO_MIN_AMBITO},
)

LONG_MAX_CUNETA = {"seca": 250.0, "muy_lluviosa": 200.0}   # m (4.1.2.1 d)

# ================= HDS-5 (FHWA) 3a ed., abril 2012 =========================
# Apendice A, Tabla A.1, pag. A.8
KU_METRICO = 1.811                  # q* = KU*Q/(A*D**0.5)
Q_LIM_NO_SUMERGIDO = 3.5
Q_LIM_SUMERGIDO    = 4.0            # entre ambos: interpolacion lineal

HDS5_INLET = {   # cartas por forma/material; dentro de cada una, por borde
    "circular_concreto_square_edge_headwall": {"K": 0.0098, "M": 2.00,
                                               "c": 0.0398, "Y": 0.67, "Ks": -0.5},
    "circular_cmp_headwall":                  {"K": 0.0078, "M": 2.00,
                                               "c": 0.0379, "Y": 0.69, "Ks": -0.5},
    "circular_cmp_mitered":                   {"K": 0.0210, "M": 1.33,
                                               "c": 0.0463, "Y": 0.75, "Ks":  0.7},
}
# Ks NO figura en la Tabla A.1: proviene de la formulacion (-0.5 / +0.7). No omitir.
# HDPE -> criterios_adoptados.valor("hds5_embocadura_hdpe")

# ================= Control de salida (SI) ==================================
K_FRICCION_SI = 19.63               # H = (1 + ke + 19.63*n^2*L/R^(4/3)) * V^2/(2g)
                                    # OJO: 29 es el valor ingles.
                                    # TEST UNITARIO OBLIGATORIO.
# De donde sale el 19.63: es el valor que el propio HDS-5 escribe como
# conversion SI de su constante K = 29 del sistema ingles. Es una cifra de la
# FUENTE PRIMARIA, transcrita, no una derivacion propia.
# Lo que este comentario dijo antes y era falso: que 19.62 saliera de 2*g
# (2 x 9.81). Es una coincidencia numerica -- los dos numeros se parecen
# porque ambos rondan 2*g -- y no el origen de la constante. HDS-5 no deriva
# K de la gravedad: K absorbe la conversion de unidades del termino de
# friccion de Manning, donde g no interviene sola. Se retira esa
# justificacion en vez de conservarla "por si acaso": una razon inventada
# para un numero correcto es el mismo defecto que un numero inventado.
# DISCREPANCIA ABIERTA CON LA HOJA DE RUTA: docs/hoja_de_ruta_alcantarillas_v8.md
# (lineas 432, 436, 790 y 901) sigue escribiendo 19.62. Aqui gana la fuente
# primaria HDS-5 por verificacion externa; la hoja de ruta debe corregirse.
# ho = max(TW, (yc + D)/2)

# ================= Diametros normalizados (ASTM / AASHTO) ==================
D_PASO = 0.15                       # m; reproduce las series de 6" y 150 mm
D_INICIO = 0.90                     # m; el piso del num. 4.1.1.3.4 a), que
                                    # NO es incondicional: ver DIAMETRO_MIN,
                                    # DIAMETRO_MIN_TEXTO y DIAMETRO_MIN_AMBITO.
                                    # Decia "minimo normativo MTC" a secas, que
                                    # es la formula exacta que NOR-HID-03 cita
                                    # como defecto -- el numeral lo condiciona
                                    # a "carreteras de alto volumen de
                                    # transito" y exceptua los cruces de canal
                                    # de riego.
# D_MAX SALIO DE ESTE ARCHIVO. Declaraba los topes por material -- 2.70 /
# 2.10 / 1.50 m -- atribuidos a "ASTM C76 / AASHTO M170", "AASHTO M36 / ASTM
# A760" y "AASHTO M294", bajo el rotulo "topes por norma de producto -
# VERIFICAR". La atribucion es FALSA y esta verificada en contra sobre los
# PDF de normas/ (NOR-PRO-01, NOR-PRO-02, MAT-O8):
#
#   ASTM A760/A760M-10, Tabla 1 "Tamaños de tuberia", pag. 3: diametros
#   nominales de 100 mm (4 in) a 3600 mm (144 in). Los 2100 mm son una fila
#   mas de la serie, no un maximo.
#   AASHTO M 170M-04, Tablas 1 a 5 (Clases I a V): de 300 a 3600 mm, y la
#   Seccion 7.2 preve ademas diseños especiales por encima de lo tabulado.
#   AASHTO M294 no esta en normas/: el tope del HDPE no se pudo contrastar.
#
# No son topes normativos: son topes de CATALOGO, y como tales descartaban
# material en silencio con una cita que ninguna norma sostiene. Viven ahora
# en criterios_adoptados.py, criterio 'D_max_catalogo' [A], con el campo
# `de_catalogo` que obliga a imprimirlos rotulados como lo que son. La marca
# "VERIFICAR" que llevaban era la senal de que nunca debieron entrar aqui:
# una constante [N] sin numeral no es una constante [N] pendiente de
# confirmar, es un valor de otra clase.
#
# Sin tope, el solver puede converger a un diametro que nadie fabrica ni
# transporta a la obra. Superado el tope: "material descartado por diametro
# requerido" -- y ese descarte es ADOPTADO, no normativo.
#
# DISCREPANCIA ABIERTA CON LA HOJA DE RUTA: su Anexo B (linea 806 de
# docs/hoja_de_ruta_alcantarillas_v8.md) declara estos mismos topes bajo el
# rotulo "topes por norma de producto - VERIFICAR" y con las mismas
# atribuciones. Gana la fuente primaria -- las tablas de A760 y M 170M,
# leidas de los PDF -- y la hoja de ruta SIGUE MAL mientras no se corrija.

# ================= Manual de Suelos (RD 10-2014-MTC/14) ====================
RESGUARDO_NAPA_SUBRASANTE = [       # (CBR_min, CBR_max, resguardo_m)  num. 4.5.4
    (20.0, None, 0.60), (6.0, 20.0, 0.80),
    (3.0, 6.0, 1.00),   (None, 3.0, 1.20),
]
# Su aplicacion al HW es POR ANALOGIA [N->] -> ver criterios_adoptados
CBR_MIN_SUBRASANTE = 6.0            # % (num. 3.3)
COMPACTACION_CORONA = 0.95          # 0.30 m superiores, capas de 0.15 m
                                     # (num. 3.2.1, 3.2.2, 3.3 y 9.1(1))
COMPACTACION_CUERPO = 0.90          # capas de hasta 0.30 m
                                     # (num. 3.2.1, 3.2.2, 3.3 y 9.1(1))

CALICATAS_POR_KM = {"autopista": 4, "dual": 4, "primera_clase": 4,
                    "segunda_clase": 3, "tercera_clase": 2, "bajo_volumen": 1}
                    # num. 4.2, Cuadro 4.1
# El Cuadro 4.1 no es "calicatas x km" para todas las clases: en autopistas y
# duales/multicarril la exigencia es "x km x SENTIDO", y el total se duplica.
# Sin este multiplicador, una autopista de 5 km salia con 20 calicatas cuando
# el Cuadro pide 40. Se declara aparte y no metido en el numero de arriba
# porque son dos cosas distintas del mismo Cuadro: cuantas por kilometro, y
# sobre cuantos sentidos se cuenta el kilometro.
CALICATAS_POR_SENTIDO = {"autopista": True, "dual": True, "primera_clase": False,
                         "segunda_clase": False, "tercera_clase": False,
                         "bajo_volumen": False}
                    # num. 4.2, Cuadro 4.1
# El Cuadro admite ademas 6 en vez de 4 para autopistas con 4 carriles por
# sentido, y "4 (o 6)" para duales. Ese 6 NO se transcribe aqui: el Cuadro lo
# da como alternativa sin decir cuando aplica cada una, de modo que la
# eleccion entre 4 y 6 no es [N]. Si el proyecto llega a necesitarla, es un
# criterio [A] declarado en criterios_adoptados.py, no un numero mas en esta
# tabla. Con el corredor de 5 km de este expediente la clase de via ni
# siquiera esta cerrada (depende del IMDA del estudio de demanda), asi que la
# alternativa no se ha alcanzado todavia.
ESPACIAMIENTO_PERFIL_KM = 4.0       # nivel perfil (num. 4.2, Cuadro 4.1)

# ================= EG-2013, Capitulo V (Secciones 502-508) =================
H_RELLENO_MIN = {
    "hdpe":     0.30,               # m, clave a subrasante (508.07, pag. 984)
    "concreto": None,               # EG-2013 no lo fija -- ver comentario
    "tmc":      None,               # EG-2013 no lo fija -- idem
}
# Texto que fija la fila del HDPE, literal (EG-2013, Capitulo V, Subseccion
# 508.07 "Colocacion del relleno alrededor de la estructura", pagina impresa
# 984, ultimo parrafo):
#
#     "La altura de relleno minimo desde la clave de la tuberia hasta el
#     nivel de la subrasante sera de 0,30 m."
#
# Dos cosas que el 0.30 suelto pierde. Primera: la magnitud es CLAVE a
# SUBRASANTE, exactamente la que calcula 7.A. Segunda: "la clave de la
# tuberia" es la superficie EXTERIOR del tubo, no el punto que queda a D
# sobre el invert interior -- de ahi que M7 calcule la clave con el espesor
# de pared (MAT-D4).
# LA PAGINA: 984, verificada leyendo el PDF. Este comentario decia 982, y esa
# cita viaja a mas sitios del expediente (NOR-EG-01, cluster C11); aqui se
# corrige la ocurrencia que este archivo declara, no las demas.
#
# NOTA CONSTRUCTIVA [N] que acompaña a este mismo 0.30 m (Sec. 7.A de la hoja
# de ruta): el equipo pesado no circula sobre el conducto antes de que el
# relleno alcance 0.30 m. Vivia en el criterio 'h_relleno_min_concreto_tmc' y
# se traslada aqui al retirarse aquel: es una exigencia de EJECUCION sobre el
# relleno del EG-2013, no la altura minima de diseño, y no la sustituye la
# cobertura minima de AASHTO -- que es de diseño en servicio, no de obra.
#
# QUE SIGNIFICAN LOS DOS None, que NO es lo que decia este comentario. Antes
# decian "VACIO VERIFICADO -- no es 'falta extraer'", y sostenian que la
# busqueda estaba cerrada en todas las fuentes posibles. Era falso por dos
# lados:
#
#   (a) LA FUENTE QUE FALTABA (NOR-VAC-01). AASHTO LRFD 9a ed., Art.
#       12.6.6.3 y Tabla 12.6.6.3-1 (pag. 12-22), tabulan la cobertura minima
#       para los tres tipos de conducto de este catalogo. Esta en normas/ y
#       es el cuerpo normativo que Sec. 0.2 adopta de extremo a extremo. El
#       valor de concreto y TMC sale de ahi, via el criterio
#       'cobertura_minima_aashto'; estos None significan hoy "EG-2013 no lo
#       fija para este material", que es cierto, y nada mas.
#   (b) LA ATRIBUCION DE LA EXCLUSION ERA FALSA EN DOS DE TRES (NOR-PRO-03).
#       Las tres normas de producto efectivamente NO dan alturas de relleno
#       -- ese fondo se confirma -- pero la formula "su Nota 1 las excluye
#       por ser especificaciones de fabricacion y compra" es de UNA sola:
#       AASHTO M 170M-04, Nota 1 ("This specification is a manufacturing and
#       purchase specification only, and does not include requirements for
#       bedding, backfill, or the relationship between field load condition
#       and the strength classification of pipe"). En AASHTO M 36 la
#       exclusion esta en §1.3 y en ASTM A760/A760M-10 en §1.4, con otra
#       redaccion; la Nota 1 de esas dos habla de laminas con fibra de
#       aramida y post-recubrimiento asfaltico. Sigue siendo cierto que
#       M 170M clasifica por D-load y no por altura.
#
# DISCREPANCIA ABIERTA CON LA HOJA DE RUTA. La v8 sigue escribiendo lo que
# aqui se corrige, y quien la lea sin leer el codigo diseñara con el valor
# equivocado:
#
#   linea 523 (tabla de Sec. 7.A): "Concreto y TMC | No fijado. Remite al
#     Proyecto, AASHTO M-170M (clases I-V) o ASTM A-807 | [C] norma de
#     producto". Las dos remisiones son falsas: M 170M no da alturas de
#     relleno y A-807 no es la norma que se le atribuye (ver NOR-PRO-04). Y
#     "no fijado" ya no es cierto: lo fija AASHTO LRFD Art. 12.6.6.3, que el
#     propio Sec. 0.2 adopta.
#   linea 546 (tabla de Fase 8): "TMC | ASTM A-807 / AASHTO M36 -- calibre
#     segun altura". El calibre por altura de cobertura es de ASTM A796/A796M.
#   linea 832 (Anexo B): repite la remision a A-807 en el comentario de
#     H_RELLENO_MIN["tmc"].
#
# Aqui gana la fuente primaria por verificacion externa contra los PDF de
# normas/, como en K_FRICCION_SI. La hoja de ruta SIGUE MAL mientras no se
# corrija: el defecto esta reportado contra ella, no contra este archivo.
# 505, 506, 507 y 508 son SECCIONES completas del EG-2013, dentro del
# Capitulo V. No son subsecciones de ninguna "Seccion 500": esa denominacion
# no existe en el EG-2013 y la constante se llamaba SUBSECCION por arrastre de
# ese error. Las SUBsecciones son las de dentro de cada una (505.03, 508.07).
SECCION_EG2013 = {"concreto_simple": "505", "concreto_reforzado": "506",
                  "tmc": "507", "hdpe": "508"}
SECCION_CABEZALES = "503"           # concreto estructural (+504 acero)

# ========== EG-2013, Capitulo V - 8.1 Cama y relleno lateral ===============
# Tabla literal de Sec. 8.1 de la hoja de ruta, con los numerales del EG-2013
# por SECCION de material (505/506/507/508). Solo texto (cama, sujecion,
# numeral): no es una verificacion con umbral, es la ficha por material para memoria y
# planos (Sec. 11, entregable 7). Los porcentajes y fracciones de diametro
# viajan como parte del texto normativo citado, no como numeros a comparar.
CAMA_RELLENO_LATERAL = {
    "concreto_simple": {
        "cama_apoyo": "Concreto Clase F (f'c = 14 MPa), >= 15 cm",
        "sujecion_relleno_lateral": "Clase F hasta >= 1/4 del diametro "
                                    "exterior. Relleno Sec. 502 >= 95% MDS",
        "numeral": "505.03/.07/.10/.11, pags. 950-951",
    },
    "concreto_reforzado": {
        "cama_apoyo": "Subbase granular (Sec. 402) >= 15 cm, >= 95% MDS",
        "sujecion_relleno_lateral": "Subbase hasta >= 1/6 del diametro "
                                    "exterior. Relleno Sec. 502",
        "numeral": "506.03/.07/.10/.11, pags. 959-960",
    },
    "tmc": {
        "cama_apoyo": "Subbase granular >= 15 cm, >= 95% MDS, con arena "
                      "suelta de 12 mm",
        "sujecion_relleno_lateral": "Capas de 15-20 cm: >= 90% en base y "
                                    "cuerpo, >= 95% en corona",
        "numeral": "507.06/.07/.08, pag. 970",
    },
    "hdpe": {
        "cama_apoyo": "Arena gruesa, capas de 15 cm, espesor 15-30 cm "
                      "(30 cm en roca o suelo blando)",
        "sujecion_relleno_lateral": "Capas alternadas y simetricas de "
                                    "15 cm a > 95%; los 30 cm superiores a "
                                    ">= 100%. Prohibida la anegacion",
        "numeral": "508.05/.07, pags. 981-982",
    },
}

# ================= Manual de Puentes (RD 041-2016-MTC/14) ==================
SOBRECARGA_TRASDOS_H_EQ = 0.60      # m de relleno equivalente (2.1.4.3.9)
CARGA_VIVA = "HL-93"                # (2.4.3.2.2.1)
NQ_ZAPATA_EN_TALUD = 0.0            # (2.8.1.3.1.2c)
F_PGA_TABLA = {                     # Tabla 2.4.3.11.2.1.2-1, PGA >= 0.50
    "C": 1.0, "D": 1.0, "E": 0.9,
}
# Factor de reduccion del coeficiente sismico por desplazamiento admisible del
# muro (num. 2.8.1.1.14.2). Las DOS filas son [N]: el numeral las fija. Cual de
# las dos aplica a ESTE cabezal no lo dice el numeral -- lo decide como se
# disena el cabezal -- y por eso la eleccion es el criterio [A]
# 'factor_muro_eleccion', el mismo reparto que ya tenian F_PGA_TABLA y 'F_pga'.
FACTOR_MURO_TABLA = {
    "rigido": 1.0,        # sin reduccion: el muro no admite desplazamiento
    "desplazable": 0.5,   # k_h = 0.5*k_h0, muros que admiten 25-50 mm
}
NUMERAL_FACTOR_MURO = "2.8.1.1.14.2"
# PGA -> datos_sitio (dato de sitio [S]); F_pga elegido, factor de muro elegido
# y k_v -> criterios_adoptados

# Combinaciones de carga: AASHTO LRFD Sec. 3.4.1 via Manual de Puentes
# (num. 2.4.5.3, pags. 140-143). La hoja de ruta NOMBRA las tres y no
# transcribe la Tabla 3.4.1-1: los factores gamma son un vacio declarado en
# criterios_adoptados ("factores_carga_aashto"). Aqui solo viven los nombres,
# que si estan en el texto normativo citado.
COMBINACIONES_AASHTO = ("Resistencia I", "Servicio I", "Evento Extremo I")
NUMERAL_COMBINACIONES = "2.4.5.3 (AASHTO LRFD Sec. 3.4.1), pags. 140-143"
NUMERAL_SOBRECARGA_TRASDOS = "2.1.4.3.9, pag. 91"
NUMERAL_ZAPATA_EN_TALUD = "2.8.1.3.1.2c, pags. 272-273"
NUMERAL_K_H0 = "2.8.1.1.14.2"

# ================= E.050 (RM 406-2018-VIVIENDA) ============================
FS = {
    "capacidad_portante": {"estatico": 3.00, "sismico": 2.50},   # Art. 21
    "volteo":             {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 a
    "deslizamiento":      {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 a
    "estabilidad_global": {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 b
    "talud":              {"estatico": 1.50, "sismico": 1.25},   # Art. 30.3
}
FS_NUMERAL = {                      # el numeral de cada fila de la tabla de 9.3
    "capacidad_portante": "E.050 Art. 21.1/21.2, pag. 34",
    "volteo":             "E.050 num. 39.13.6 a), pag. 72",
    "deslizamiento":      "E.050 num. 39.13.6 a), pag. 72",
    "estabilidad_global": "E.050 num. 39.13.6 b), pag. 72",
    "talud":              "E.050 Art. 30.3, pag. 39",
}
NUMERAL_C_PHI = "E.050 Art. 20, pag. 33"   # cohesivos phi=0; friccionantes c=0
NUMERAL_ZAPATA_TALUD_E050 = "E.050 Art. 30.1-30.2"

SPT_PROF_MIN = 15.0                 # m (Art. 38)
SPT_ESPACIAMIENTO = 1.0             # m entre ensayos

# ================= E.060 (durabilidad, excepcion declarada) ================
SULFATOS = [                        # Tabla 4.4: (SO4_min%, SO4_max%, cemento, a/c, f'c_MPa)
    (0.00, 0.10, None,               None, None),
    (0.10, 0.20, "II/IP(MS)/IS(MS)", 0.50, 28),
    (0.20, 2.00, "V",                0.45, 31),
    (2.00, None, "V + puzolana",     0.45, 31),
]
CLORUROS_EXTERNOS = {"a_c_max": 0.40, "fc_min_MPa": 35}   # Art. 4.2 / 4.4
RECUBRIMIENTO = {"contra_suelo": 70, "suelo_intemperie_ge_3_4": 50,
                 "suelo_intemperie_le_5_8": 40}           # Art. 7.7.1, mm
NUMERAL_RECUBRIMIENTO = "E.060 Art. 7.7.1, pag. 54"
AMBIENTE_CORROSIVO_AUMENTAR = "E.060 Art. 7.7.5.1"        # "aumentar adecuadamente"
# Sin numero: el articulo dice "aumentar adecuadamente" y no fija cuanto. Con
# NF a 1.4 m y suelos salinos es directamente invocable (Sec. 3.3), asi que el
# aumento se declara en criterios_adoptados, no aqui.

# ---- E.060, refuerzo de muros - MINIMO OBLIGATORIO ------------------------
# Que "no gobierna el diseno" y que "es informativo" no son lo mismo, y este
# bloque decia lo segundo cuando lo cierto es lo primero. La Via 1 de Sec. 0.2
# pone el DIMENSIONAMIENTO bajo AASHTO LRFD Sec. 5 y deja a E.060 la
# durabilidad y los recubrimientos: de ahi que Sec. 9.4 hable de "referencia
# de cuantias minimas". Pero el Art. 14.3.1 fija un PISO por debajo del cual
# ningun muro se arma, y un piso se aplica -- rho_diseno =
# max(rho_calculado, rho_minimo), en `M9.cuantia_de_diseno` -- no se imprime.
# Falta aqui el segundo minimo de E.060: el Art. 11.10.10.2 escalona la
# cuantia HORIZONTAL a 0.0025 bajo demanda de cortante alta. No se transcribe
# como constante [N] porque la hoja de ruta no lo recoge (solo cita el
# 14.3.1); queda declarado como vacio en el criterio
# 'cortante_alto_muro_e060_art_11_10_10_2'. Mientras siga asi, el 0.0020 de
# abajo es el minimo MENOR de los dos que tiene E.060, y M9 obliga a contestar
# expresamente cual aplica.
CUANTIA_MIN_MURO = {"horizontal": 0.0020, "vertical": 0.0015}   # Art. 14.3.1, pag. 133
NUMERAL_CUANTIA_MIN = "E.060 Art. 14.3.1, pag. 133"
ESPESOR_TEMPERATURA_DOS_CARAS = 0.250       # m (250 mm); Art. 14.8.3
NUMERAL_TEMPERATURA_DOS_CARAS = "E.060 Art. 14.8.3"
ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0       # <= 3h        Art. 14.3.3
ESPACIAMIENTO_MAX_ABSOLUTO = 0.400          # m (400 mm)   Art. 14.3.3
NUMERAL_ESPACIAMIENTO = "E.060 Art. 14.3.3"

# ---- E.060, concreto ciclopeo (alternativa de muro de gravedad) ----------
CICLOPEO_FC_MATRIZ_MIN = 10.0               # MPa            Art. 22.10
CICLOPEO_FRACCION_PIEDRA_MAX = 0.30         # del volumen    Art. 22.10
NUMERAL_CICLOPEO = "E.060 Art. 22.10, pags. 194-195"

# ================= E.030 (RM 183-2026-VIVIENDA) - donde quedo ==============
# Este bloque tenia tres valores y ninguno era [N]: los tres son la lectura de
# un mapa o de una clasificacion SOBRE LAS COORDENADAS DE ESTE PROYECTO. Citan
# E.030 correctamente y aun asi cambiarian de valor en otra provincia, que es
# justo lo que una constante normativa no hace. Se reclasificaron como datos de
# sitio [S] y salieron de aqui:
#
#     ZONA_SISMICA_LA_UNION  ->  datos_sitio.DATOS_SITIO["ZONA_SISMICA_LA_UNION"]
#     Z_E030                 ->  datos_sitio.DATOS_SITIO["Z_E030"]
#     PERFIL_SUELO_PRESUNTO  ->  criterios_adoptados.CRITERIOS["PERFIL_SUELO_PRESUNTO"]
#                                ([S] pendiente de SPT, junto a 'clase_sitio')
#
# El cambio es de clasificacion, no de uso: los tres seguian siendo referencia
# que no gobierna el cabezal (Sec. 0.4 descarta el sismo de 475 anios de E.030
# frente al PGA de Tr = 1000 anios del Manual de Puentes) y lo siguen siendo.


# ===========================================================================
# Constantes de REFERENCIA: transcritas del Anexo B, sin consumidor de calculo
# ===========================================================================
# Este archivo es la transcripcion literal del Anexo B, y el Anexo B trae mas
# de lo que el script calcula. Trece de sus constantes no las lee ningun
# modulo de produccion: son requisitos que el expediente tiene que cumplir
# (densidad de calicatas, compactacion, limites de agresividad quimica) o
# pisos normativos que el pipeline aplica por otra via.
#
# La lista existe porque sin ella las dos clases de constante se ven iguales
# leyendo el archivo, y un revisor no puede saber si "sin consumidor"
# significa "todavia no cableada" o "no le corresponde cablearse". Aqui
# significa lo segundo, en las trece.
#
# Es documentacion, no configuracion: nadie la importa para calcular. Si
# alguna se cablea, sale de esta lista en el mismo commit.
CONSTANTES_DE_REFERENCIA = (
    "DIAMETRO_MIN",              # el piso de 0.90 m entra por
                                 # 'diametros_normalizados' (D_INICIO). Ver
                                 # DIAMETRO_MIN_AMBITO: su numeral lo
                                 # condiciona y exceptua a los cruces de canal
    "DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO",   # recomendacion, solo TMC y
                                 # solo selva alta: no aplica en costa
    "LONG_MAX_CUNETA",           # Fase 10 recibe L_hidraulico declarado
    "CBR_MIN_SUBRASANTE",        # requisito del paquete estructural vial
    "COMPACTACION_CORONA",       # requisitos de ejecucion (EG-2013), sin
    "COMPACTACION_CUERPO",       # columna en el CSV contra la que comparar
    "CALICATAS_POR_KM",          # densidad de investigacion geotecnica:
    "CALICATAS_POR_SENTIDO",     # gobierna la campana de campo, no el
    "ESPACIAMIENTO_PERFIL_KM",   # dimensionamiento de la alcantarilla
    "SPT_PROF_MIN",              # profundidad y paso del SPT que cerraria
    "SPT_ESPACIAMIENTO",         # 'clase_sitio' y 'PERFIL_SUELO_PRESUNTO'
    "SULFATOS",                  # agresividad quimica: la decide el EMS del
    "CLORUROS_EXTERNOS",         # expediente, no este calculo
)
