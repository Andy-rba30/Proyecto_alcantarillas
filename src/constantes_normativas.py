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

LONG_MAX_CUNETA = {"seca": 250.0, "muy_lluviosa": 200.0}   # m (4.1.2.1 d)

# ================= HDS-5 (FHWA) 3a ed., abril 2012 =========================
# Apendice A. NO todo sale de la Tabla A.1, y este encabezado decia que si
# (NOR-HDS-03): de la Tabla A.1 (pag. impresa A.8) salen SOLO las constantes
# K, M, c e Y de cada carta; KU, Ks, los dos limites de rama y las propias
# ecuaciones estan en el texto del num. A.2, pags. impresas A.1-A.2. Cada
# constante lleva abajo su sitio exacto.
#
# LAS DOS COPIAS DE HDS-5 QUE HAY EN normas/ NO DICEN LO MISMO, y todo este
# bloque se apoya en UNA de las dos (MAT-X5, MAT-O12):
#
#   hif12026.pdf                     3a ed., abril 2012 (FHWA-HIF-12-026).
#                                    Trae las conversiones SI explicitas.
#   fhwa_culvert_hydraulics_hds5si.pdf   edicion de septiembre de 1985
#                                    (FHWA-IP-85-15), rotulada "SI" por sus
#                                    cartas en version metrica. NO imprime
#                                    numero de pagina y NO imprime ni 1.811
#                                    ni 19.63: opera en unidades inglesas con
#                                    rotulos duales "ft (m)".
#
# Todo valor de este bloque sale de la 3a ed. Leer la copia de 1985 "en SI"
# reproduce exactamente el error del 29 (ver K_FRICCION_SI).
KU_METRICO = 1.811                  # q* = KU*Q/(A*D**0.5)
# El 1.811 no esta en la Tabla A.1 (pag. A.8) sino en la lista de variables de
# las ecuaciones de control de entrada, num. A.2.1 "Unsubmerged Inlet Control
# Equations", pag. impresa A.2 (PDF 191) de la 3a ed., que lo imprime asi:
#     "Ku Unit conversion 1.0 (1.811 SI)"
# Verificado contra el PDF en esta sesion. Lo que sigue citado a la Tabla A.1
# de la pag. A.8 son las constantes K, M, c e Y de HDS5_INLET.
# Los dos limites de rama tampoco salen de la Tabla A.1 (NOR-HDS-03): estan en
# el texto del num. A.2, pags. impresas A.1-A.2, que introduce las ecuaciones.
# La Tabla A.1 de la pag. A.8 contiene SOLO las constantes K, M, c e Y por
# carta. Y son los limites del sistema INGLES a proposito: HDS-5 los escribe
# sobre Q/(A*D^0.5) y da entre parentesis su equivalente SI, mas chico; como
# `caudal_adimensional` multiplica por KU_METRICO = 1.811, el q* que compara
# M4 esta ya en la escala inglesa y los umbrales que le corresponden son 3.5 y
# 4.0. Cambiarlos por los del parentesis seria aplicar dos veces la conversion.
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
# Ks NO figura en la Tabla A.1: proviene de la formulacion (-0.5 / +0.7). No
# omitir. Su sitio exacto en la 3a ed., verificado contra el PDF, es la lista
# de variables del num. A.2.1 "Unsubmerged Inlet Control Equations",
# pag. impresa A.2 (PDF 191), que lo imprime en una linea:
#     "Ks Slope correction, -0.5 (mitered inlets +0.7)"
# y lo explica en la pag. impresa 3.25 (PDF 107):
#     "For mitered culverts, a correction term of +0.7S is used to account for
#      the control section being outside the culvert barrel and slightly
#      higher."
#
# EL +0.7 DE INGLETE Y EL ke = 0.7 DE INGLETE SON DOS COEFICIENTES DISTINTOS
# CON EL MISMO NUMERO (NOR-HDS-04). Con embocadura ingleteada el 0.7 aparece
# dos veces en la misma cadena de calculo, por dos motivos sin relacion:
#
#   Ks = +0.7   correccion por PENDIENTE del control de ENTRADA. Multiplica a
#               S en HWi/D, es adimensional y vive en el num. A.2.1 (pag. A.2).
#   ke = 0.7    coeficiente de PERDIDA de entrada del control de SALIDA, fila
#               "Mitered to conform to fill slope" de la Tabla C.2, pag.
#               impresa C.6 (PDF 216). Entra en H, no en HWi/D, y llega por el
#               criterio 'ke_entrada'.
#
# Coinciden en valor y en condicion (inglete) y en nada mas. Se anota aqui, en
# el sitio donde vive el primero, para que nadie los cruce ni deduzca uno del
# otro: este proyecto adopta hoy la embocadura a ras del muro (square edge with
# headwall), donde los dos numeros son distintos -- Ks = -0.5 y ke = 0.5 --, y
# el cruce solo seria posible si alguien cambiara la embocadura a inglete.
#
# HDPE -> criterios_adoptados.valor("hds5_embocadura_hdpe")

# ================= Control de salida (SI) ==================================
K_FRICCION_SI = 19.63               # H = (1 + ke + 19.63*n^2*L/R^(4/3)) * V^2/(2g)
                                    # OJO: 29 es el valor ingles.
                                    # TEST UNITARIO OBLIGATORIO.
# De donde sale el 19.63: es el valor que el propio HDS-5 escribe como
# conversion SI de su constante K = 29 del sistema ingles. Es una cifra de la
# FUENTE PRIMARIA, transcrita, no una derivacion propia. Verificado en la 3a
# ed. (hif12026.pdf) en dos sitios: num. 3.1.4 "Outlet Control", ec. (3.4b),
# pag. impresa 3.10 (PDF 92) -- "KU = 29 in English Units (19.63 in SI)" --, y
# la ec. (DG 3.1), pag. impresa DG3.3 (PDF 296) -- "KU is 29 (19.63 in SI
# Units)".
#
# LA COPIA DE 1985 QUE ESTA EN normas/ NO SIRVE PARA ESTO, y hay que decirlo
# porque lleva "si" en el nombre del archivo (MAT-O12, MAT-X5): sus ecs. (4b)
# y (5), en la pag. 54 del PDF, imprimen "29 n^2 L / R^1.33" con rotulos de
# unidades duales "ft (m)", y su gravedad, en la pag. 53, es
# "32.2 ft/s/s (9.8 m/s/s)". Leida literal "en SI" reproduce exactamente el
# error del 29 (+9.6 %). El 19.63 solo lo imprime la 3a ed.
#
# POR QUE SE PARECE TANTO A 2*g, que es la pregunta que este comentario
# contestaba mal. Decia que el parecido era "una coincidencia numerica" y que
# "HDS-5 no deriva K de la gravedad". Es falso, y la relacion es exacta
# (MAT-D12, MAT-X5):
#
#     K = 2*g / phi^2      phi = factor de unidades de Manning
#                          (1.486 en el sistema ingles, 1 en SI)
#
#     ingles:  2 * 32.2 / 1.486^2 = 29.164   -> el 29 impreso
#     SI:      2 * 9.81456        = 19.629   -> el 19.63 impreso
#
# o sea que en SI la constante ES 2*g, y lo unico que separa 19.63 de 19.62 es
# CUAL g: HDS-5 trabaja con 32.2 ft/s^2 = 9.81456 m/s^2 y este proyecto usa
# constantes_fisicas.G = 9.81. Se conserva el 19.63 transcrito y no el 2*G
# derivado -- el valor es de la fuente primaria --, y el efecto de la
# diferencia se dice en vez de callarse: 19.63/19.62 = 1.0005, un +0.05 % sobre
# el TERMINO DE FRICCION -- unas 190 veces menos que el 9.6 % que produce el 29
# imperial, que es el error que esta constante existe para atrapar.
#
# La hoja de ruta escribia 19.62 en sus cuatro menciones y quedo corregida a
# 19.63 en el mismo commit que este comentario (Sec. 4.3, su nota de unidades,
# el Anexo C y las notas criticas de programacion). Ya no hay discrepancia
# abierta, y por eso este comentario ya no cita renglones de la hoja de ruta:
# citarlos fue lo que produjo SIS-A-20, cuatro numeros de linea que el propio
# documento fue corriendo.

# --------------------------------------------------------------------------
# h_o, la linea de energia a la salida -- y la CONDICION que la habilita
# --------------------------------------------------------------------------
# Este bloque existe porque la formula se aplicaba sin su condicion de uso, y
# la condicion esta impresa junto a la formula (NOR-HDS-05). El repositorio
# tenia aqui una sola linea de comentario -- "ho = max(TW, (yc + D)/2)" -- y el
# manifiesto marcaba la fila "sin numeral". Las dos cosas quedan cerradas: la
# formula SI tiene numeral, y viene con un limite de validez expreso.
H_O_NUMERAL = ("HDS-5 (FHWA) 3a ed., abril 2012, num. 3.3.3 'Outlet Control', "
               "pag. impresa 3.24 (PDF 106)")
# Texto literal de la condicion de uso. Las DOS citas estan en la misma pagina
# impresa 3.24 y en dos sitios distintos de ella, y decir cual es cual importa
# (era una sola atribucion para las dos, y una de ellas era falsa):
#
#   la primera es una vineta de la lista "The manual method has the
#   assumptions:";
#   la segunda esta en el parrafo de prosa que sigue a esa lista, el mismo que
#   trae la condicion de 1.2D.
H_O_CONDICION_TEXTO = (
    "Approximate hydraulic gradeline ho = (dc + D)/2 can only be used if the "
    "barrel flows full for most of its length. It should not be used if the "
    "inlet is not submerged.",
    "If outlet control governs and the headwater depth (referenced to the "
    "inlet invert) is less than 1.2D, it is possible that the barrel flows "
    "partly full though its entire length. In this case, caution should be "
    "used in applying the approximate method of setting the downstream "
    "elevation based on the greater of tailwater or (dc + D)/2. If the "
    "headwater depth falls below 0.75D, the approximate method should not be "
    "used.",
)
# Los dos numeros de esa segunda cita, extraidos para poder EVALUARLOS. Son
# [N]: los escribe la fuente, no los elige el proyectista.
#
# POR QUE SE EVALUAN Y LA PRIMERA CONDICION NO. "Que el barril fluya lleno en
# la mayor parte de su longitud" exige un perfil de la lamina de agua que este
# script no calcula. Estos dos, en cambio, son una comparacion entre dos
# numeros que el modulo ya tiene: HW y D. Declararlos sin evaluarlos, pudiendo,
# era extender a la segunda condicion una imposibilidad que solo vale para la
# primera -- y dejaba la memoria diciendo "esto podria estar fuera de rango"
# sin decir en que punto lo esta, que es literalmente el "nadie se entera" de
# NOR-HDS-05.
#
# El 0.75 NO es el 0.75 de Y_SOBRE_D_MAX, y por eso son dos constantes y no
# una: aquel es el borde libre del num. 4.1.1.3.7 b) del Manual MTC sobre el
# TIRANTE, este es un limite de validez del HDS-5 sobre la CARGA A LA ENTRADA.
# Misma cifra, dos magnitudes y dos fuentes. Es el mismo reparto que G y
# G_LAUSHEY.
H_O_HW_SOBRE_D_MIN = 0.75           # HW/D por debajo del cual la aproximacion
                                    # NO debe usarse (num. 3.3.3, pag. 3.24)
H_O_HW_SOBRE_D_CAUTELA = 1.2        # HW/D por debajo del cual la fuente pide
                                    # cautela: el barril puede fluir
                                    # parcialmente lleno (mismo numeral)
# La forma con el MAXIMO -- que es la que implementa `M4.control_salida` -- la
# 3a ed. no la numera: la escribe en prosa ("the greater of tailwater or
# (dc + D)/2", misma pag. 3.24; "or (dc + D)/2 if larger", num. 3.4.5, pag.
# 3.32). Impresa como igualdad esta en la edicion de 1985 que tambien vive en
# normas/, dentro de su procedimiento paso a paso (PDF 67):
H_O_FORMA_MAXIMO_TEXTO = "ho = TW or (dc + D)/2 whichever is larger."
# Lo que el proyecto hace con la condicion, y que NO puede hacer:
H_O_CONDICION_APLICACION = (
    "h_o se calcula SIEMPRE, y de las tres condiciones que la fuente le pone "
    "el proyecto EVALUA dos y declara la tercera. "
    "SE EVALUAN, punto por punto, los dos limites sobre HW/D: por debajo de "
    "1.2 la fuente pide cautela y por debajo de 0.75 dice que la aproximacion "
    "no debe usarse. Cuando el control de salida GOBIERNA un punto y su HW/D "
    "cae bajo alguno de los dos, la memoria de ese punto lo dice con esas "
    "palabras, junto al HW: un aviso general que no senala el punto afectado "
    "no le sirve al revisor, que es lo que este bloque venia haciendo. "
    "NO SE EVALUA la primera condicion -- que el barril fluya lleno en la "
    "mayor parte de su longitud --, y no por descuido: exige un perfil de la "
    "lamina de agua a lo largo del conducto, que este script no calcula. El "
    "criterio adoptado 'geometria_control_salida' = 'seccion_llena' "
    "PRESUPONE ademas lo mismo que ahi habria que verificar, de modo que esa "
    "premisa entra dos veces por dos puertas y no se comprueba por ninguna. "
    "No se sustituye por otra formula ni se inventa un criterio de llenado: "
    "se declara, y quien revise el expediente decide si el punto necesita el "
    "procedimiento de barril parcialmente lleno del Cap. III, que es la "
    "alternativa que el propio criterio ya cita. "
    "HAY UNA CIRCULARIDAD QUE CONVIENE VER: el HW con que se evaluan los dos "
    "limites es el que produce la propia aproximacion, de modo que un h_o "
    "sobreestimado puede hacer que el control de salida gobierne un punto "
    "donde no gobernaria. El aviso se emite igual; deshacer la circularidad "
    "exige el procedimiento completo, no otra lectura de esta pagina.")

# ---------------------------------------------------------------------------
# El CARACTER de cada umbral, y de cada CONDICION DE USO, que el proyecto aplica
# ---------------------------------------------------------------------------
# ESTE BLOQUE VIVE AQUI, DESPUES DE LAS TABLAS Y DE LAS CONSTANTES DE HDS-5,
# porque referencia constantes de las dos zonas del archivo -- las del Manual
# MTC (Tabla Nº 02, Tabla Nº 10, D_min) y las de HDS-5 (h_o) -- y en Python un
# nombre tiene que estar definido antes de usarse. Estaba mas arriba, cuando
# solo miraba a las primeras.
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
    {"codigo": "h_o",
     "que": "Linea de energia a la salida del conducto: "
            "h_o = max(TW, (y_c + D)/2), Sec. 4.3",
     "numeral": H_O_NUMERAL,
     "caracter": "APROXIMACION CON CONDICION DE USO EXPRESA",
     "texto": H_O_CONDICION_TEXTO,
     "transcripcion": ("La forma con el MAXIMO, que es la que el proyecto "
                       "implementa, la 3a ed. no la numera: la escribe en "
                       "prosa ('the greater of tailwater or (dc + D)/2', "
                       "misma pag. 3.24). Impresa como igualdad esta en la "
                       "edicion de 1985 que tambien vive en normas/, dentro "
                       "de su procedimiento paso a paso: <<"
                       + H_O_FORMA_MAXIMO_TEXTO + ">> Esta linea no es cita "
                       "de la 3a ed.: es la union de las dos ediciones, y por "
                       "eso va aqui y no arriba."),
     "aplicacion": H_O_CONDICION_APLICACION},
)

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

# ---- Tabla 503-07, "Clases de concreto estructural" -----------------------
# La Seccion 503 es la que este proyecto cita para los cabezales, y trae su
# propia escala de clases con la resistencia minima de cada una. Interesa
# aqui la Clase G, el concreto ciclopeo, porque convive con el Art. 22.10 de
# E.060 sobre el MISMO material y pide mas (NOR-E060-07): el expediente
# declaraba solo el minimo de E.060, que es el menor de los dos.
CLASES_CONCRETO_EG2013_MPA = {
    "A": 35.0,      # concreto pre y post tensado
    "B": 32.0,
    "C": 28.0,      # concreto reforzado
    "D": 21.0,
    "E": 17.5,
    "F": 14.0,      # concreto simple
    "G": 14.0,      # concreto ciclopeo (Clase F + agregado ciclopeo)
}
CICLOPEO_CLASE_G_TEXTO = (
    "Se compone de concreto simple Clase F y agregado ciclópeo, en "
    "proporción de 30% del volumen total, como máximo")
CICLOPEO_FC_MATRIZ_MIN_EG2013 = CLASES_CONCRETO_EG2013_MPA["G"]
NUMERAL_CICLOPEO_EG2013 = ("EG-2013 Seccion 503, num. 503.04 'Clases de "
                           "concreto', Tabla 503-07 'Clases de concreto "
                           "estructural', pag. impresa 912 (PDF 920)")

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

# --------------------------------------------------------------------------
# CADENA SISMICA (1/4) - Tabla de factores de sitio F_pga
# --------------------------------------------------------------------------
# La tabla ENTERA -- sus seis filas y sus cinco columnas -- y no las tres
# filas que el calculo consume. Es la regla del proyecto ("la tabla se
# transcribe COMPLETA, aunque el calculo use una parte") aplicada a la pieza
# donde su ausencia costaba mas caro:
#
#   * Faltaban las filas A y B (roca dura y roca blanda). Sin ellas la
#     clausula de roca del num. 2.8.1.1.14.2.1 -- k_h0 basado en 1.2 veces el
#     pico del suelo para muros cimentados en Clase A o B -- NO ERA
#     REPRESENTABLE: el codigo no tenia con que preguntar si la cimentacion
#     cae en esas dos filas, de modo que la regla no se implementaba NI se
#     descartaba (MAT-O4, NOR-PUE-12).
#   * Faltaba la fila F. El repositorio afirmaba que "el Manual NO tipifica
#     excepciones para Clase F en su Tabla 2.4.3.11.2.1.2-1". La tabla SI se
#     pronuncia sobre la Clase F: le pone asterisco en las cinco columnas y
#     una Nota 2 al pie que exige estudio. Eso no es un vacio que una fuente
#     tecnica deba cubrir: es una exigencia expresa (NOR-PUE-09, NOR-MEM-03).
#   * El rotulo de la ultima columna decia aqui "PGA >= 0.50" y la tabla dice
#     "PGA > 0.50", ESTRICTAMENTE MAYOR. El PGA de este proyecto es
#     exactamente 0.50: no cae en ninguna columna tabulada, y el signo mal
#     transcrito hacia invisible el problema (NOR-PUE-11).
#
# El signo de la ultima columna y el asterisco de la fila F deciden dos
# hallazgos y no se leen fiablemente por extraccion de texto: se verificaron
# renderizando la pag. impresa 123 (PDF 124) como imagen.
NUMERAL_F_PGA_TABLA = ("Manual de Puentes (MTC) num. 2.4.3.11.2.1.2, "
                       "Tabla 2.4.3.11.2.1.2-1 (Tabla 3.10.3.2-1 AASHTO), "
                       "pag. impresa 123 (PDF 124)")
F_PGA_TABLA_TITULO = ("Tabla 2.4.3.11.2.1.2-1 Valores de Factor de Sitio, "
                      "F_pga En Periodo-Cero en el Espectro de Aceleracion")
# El encabezado es de DOS niveles y el superior abarca las cinco columnas de
# la derecha. El "1" final es la llamada a la Nota 1, no un exponente.
F_PGA_TABLA_ENCABEZADO_SUPERIOR = ("Coeficiente Aceleracion Pico del Terreno "
                                   "(PGA)1")
F_PGA_TABLA_COLUMNAS = ("Clase de Sitio", "PGA < 0.10", "PGA = 0.20",
                        "PGA = 0.30", "PGA = 0.40", "PGA > 0.50")
# El PGA de referencia de cada columna, en g, para poder interpolar como
# manda la Nota 1. La ultima se rotula "> 0.50" y su punto de referencia es
# 0.50: es el valor a partir del cual la fuente deja de variar el factor. QUE
# HACER CON UN PGA DE EXACTAMENTE 0.50 -- leer esa columna o interpolar
# contra la anterior -- la tabla no lo resuelve, y por eso la lectura se
# declara en el criterio [A] 'F_pga' y no se decide aqui.
F_PGA_TABLA_PGA_COLUMNAS = (0.10, 0.20, 0.30, 0.40, 0.50)
# Marca de la celda que la fuente deja sin factor. No es un cero ni un
# olvido: es el asterisco impreso, que remite a la Nota 2. Mismo papel que
# GAMMA_P_NO_APLICA en la Tabla 2.4.5.3.1-2.
F_PGA_EXIGE_ESTUDIO_DE_SITIO = "*"
F_PGA_TABLA = {
    #          PGA<0.10  PGA=0.20  PGA=0.30  PGA=0.40  PGA>0.50
    "A": (0.8, 0.8, 0.8, 0.8, 0.8),
    "B": (1.0, 1.0, 1.0, 1.0, 1.0),
    "C": (1.2, 1.2, 1.1, 1.0, 1.0),
    "D": (1.6, 1.4, 1.2, 1.1, 1.0),
    "E": (2.5, 1.7, 1.2, 0.9, 0.9),
    "F": (F_PGA_EXIGE_ESTUDIO_DE_SITIO,) * 5,
}
F_PGA_TABLA_NOTAS = (
    "1. Usar linea recta de interpolacion para valores intermedios de PGA.",
    "2. Llevar a cabo investigaciones geotecnicas especificas del sitio y "
    "analisis de respuesta dinamica de sitio, para todos los sitios en sitio "
    "clase F",
)
# La fila que la Nota 2 marca. El Manual la imprime como "F2" -- el 2 es la
# llamada a la nota -- con asterisco en las cinco celdas.
F_PGA_CLASE_SIN_FACTOR = "F"
# Las dos filas que la clausula de roca del num. 2.8.1.1.14.2.1 nombra:
# "Clase A o B (roca dura o blanda)". Se declaran junto a la tabla que las
# define, y no dentro de M9, para que la clausula sea representable.
F_PGA_CLASES_EN_ROCA = ("A", "B")
# Como se leen los DOS rotulos extremos, que son desigualdades estrictas
# ("PGA < 0.10" y "PGA > 0.50"). Son NOMBRES de lectura, no valores: cual de
# los dos aplica lo declara el criterio [A] 'F_pga_lectura_columna_extrema',
# porque la tabla no lo resuelve y el PGA de este proyecto cae justo sobre
# uno de ellos (NOR-PUE-11).
LECTURA_COLUMNA_EXTREMA_INCLUSIVE = "limite_inclusive"
LECTURA_COLUMNA_EXTREMA_ESTRICTA = "limite_estricto"
LECTURAS_COLUMNA_EXTREMA = (LECTURA_COLUMNA_EXTREMA_INCLUSIVE,
                            LECTURA_COLUMNA_EXTREMA_ESTRICTA)

# --------------------------------------------------------------------------
# CADENA SISMICA (2/4) - k_h0, k_v y la reduccion por desplazamiento del muro
# --------------------------------------------------------------------------
# TRES NUMERALES DISTINTOS, y el repositorio los citaba todos como
# "2.8.1.1.14.2". Ese numeral existe y su titulo corresponde al tema, pero es
# un ENCABEZADO SIN CUERPO: entre el y el encabezado siguiente no hay una
# sola linea de texto (verificado como imagen, pag. impresa 254 / PDF 255).
# Citarlo manda al revisor a un renglon que no dice nada.
NUMERAL_CADENA_SISMICA = ("Manual de Puentes (MTC) num. 2.8.1.1.14 'Diseno "
                          "Sismico de Estribos y Muros de Contencion "
                          "Convencionales' (11.6.5 AASHTO), pag. impresa 252 "
                          "(PDF 253)")
NUMERAL_K_H0 = ("2.8.1.1.14.2.1 'Caracterizacion de la Aceleracion en la Base "
                "del Muro de Contencion' (11.6.5.2.1 AASHTO), pag. impresa "
                "254 (PDF 255)")
NUMERAL_FACTOR_MURO = ("2.8.1.1.14.2.2 'Estimacion de la Aceleracion que "
                       "Actua Sobre la Masa del Muro' (11.6.5.2.2 AASHTO), "
                       "pag. impresa 255 (PDF 256)")
NUMERAL_P_IR = ("2.8.1.1.14.1 'Generalidades' (11.6.5.1 AASHTO, titulado "
                "'General'), ec. 2.8.1.1.14.1-1, pag. impresa 253 (PDF 254)")

K_H0_TEXTO = ("kh0=FpgaPGA = As donde kh0 es el coeficiente de aceleracion "
              "sismico horizontal asumiendo que el desplazamiento del muro "
              "sea cero")

# Clausula de roca del mismo numeral. El 1.2 es [N] y sale de la PROSA; el
# parentesis que la acompana esta mal impreso y se transcribe entero para que
# nadie lo aplique (ver K_H0_ROCA_ERRATA).
K_H0_FACTOR_ROCA_A_B = 1.2
K_H0_ROCA_TEXTO = ("Para muros cimentados sobre Sitio con suelos Clase A o B "
                   "(roca dura o blanda), k h0 estara basado en 1.2 veces el "
                   "coeficiente de aceleracion pico del suelo (es decir, "
                   "1.2 kh0=FpgaPGA).")
K_H0_ROCA_ERRATA = (
    "ERRATA DE IMPRENTA DEL MANUAL, verificada como imagen en la pag. "
    "impresa 254 (PDF 255): el parentesis imprime '1.2 kh0=FpgaPGA', con el "
    "1.2 del lado izquierdo. Leido al pie de la letra daria "
    "k_h0 = F_pga*PGA/1.2, una REDUCCION del 17 %, justo lo contrario de lo "
    "que la prosa de la misma frase acaba de decir. AASHTO LRFD 9a ed., "
    "Art. 11.6.5.2.1 'Characterization of Acceleration at Wall Base', pag. "
    "impresa 11-27 (PDF 1496), lo escribe sin ambiguedad: "
    "'k_h0 shall be based on 1.2 times the site-adjusted peak ground "
    "acceleration coefficient (i.e., k_h0 = 1.2 F_pga PGA)'. GANA LA PROSA "
    "DEL MANUAL, coincidente con AASHTO. Es la segunda de las TRES erratas de "
    "imprenta de esta misma cadena sismica; las otras son "
    "K_AE_ERRATA_MANUAL y EXCENTRICIDAD_ERRATA_MANUAL")

# k_v: el Manual lo FIJA, no lo deja a eleccion. La afirmacion contraria
# ('practica corriente; no fijado por el Manual de Puentes') vivia en el
# criterio 'k_v' y era falsa (NOR-PUE-08, MAT-O11, MAT-X4).
K_V_PRESCRITO = 0.0
# La declaracion con la que el proyecto dice que rige el cero prescrito, es
# decir, que ninguno de los dos casos que el numeral reserva se da en este
# cabezal. Es un NOMBRE, no un valor: el valor es K_V_PRESCRITO y es [N].
K_V_DECLARACION_PRESCRITO = "prescrito_sin_caso_reservado"
K_V_TEXTO = ("El coeficiente de aceleracion sismica vertical, kv, se asumira "
             "cero con el proposito de calcular las presiones laterales del "
             "terreno, a no ser que el muro este significativamente afectado "
             "por efectos de alguna falla cercana, o si son relativamente "
             "altas las aceleraciones verticales que probablemente esten "
             "actuando simultaneamente con la aceleracion horizontal.")
# El "a no ser que" NO trae umbral en el corpus peruano: el Manual no da
# distancia a la falla, no define "cercana" y no cuantifica "relativamente
# altas"; y para ese caso tampoco escribe un k_v alternativo. Lo que el
# proyecto declara, entonces, no es un numero sino si el caso reservado se da
# (criterio 'k_v'). Si se diera, ahi hay un vacio real y el calculo se
# detiene en vez de inventar un valor.
K_V_CASO_RESERVADO = (
    "El num. 2.8.1.1.14.2.1 reserva dos casos -- muro significativamente "
    "afectado por efectos de alguna falla cercana, y aceleraciones "
    "verticales relativamente altas simultaneas con la horizontal -- y no "
    "cuantifica ninguno: no hay distancia a la falla, no hay definicion de "
    "'cercana' y no hay umbral de aceleracion vertical. El num. "
    "2.8.1.1.14.3 (pag. impresa 255) reitera el cero remitiendo a este "
    "numeral. AASHTO SI cuantifica el primer caso, pero en otro articulo y "
    "sobre un mapa que no cubre el Peru: Art. 3.10.2.2, pag. impresa 3-100 "
    "(PDF 154), 'For sites located within 6 miles of an active surface or a "
    "shallow fault, as depicted in the USGS Active Fault Map, studies shall "
    "be considered to quantify near-fault effects'. El Manual, que es la "
    "norma aplicable, no traslada ni el umbral ni el mapa")

# Reduccion por desplazamiento admisible del muro. UN SOLO VALOR NORMATIVO,
# 0.5, y ademas PERMISIVO ('puede ser reducido'). Aqui vivia
# FACTOR_MURO_TABLA = {rigido: 1.0, desplazable: 0.5} con el argumento de que
# "las DOS filas son [N]: el numeral las fija". El numeral no fija dos filas
# ni presenta tabla alguna: en las pags. impresas 252-257 del Manual no hay
# una sola tabla (NOR-PUE-07). El 1.0 no es una fila tabulada, es la
# AUSENCIA de reduccion -- que es la definicion misma de k_h0 en K_H0_TEXTO,
# 'asumiendo que el desplazamiento del muro sea cero'.
REDUCCION_KH_POR_DESPLAZAMIENTO = 0.5
REDUCCION_KH_TEXTO = ("Donde el muro es capaz de desplazamientos de 1.0 a "
                      "2.0 in o mas durante el evento sismico de diseno, kh "
                      "puede ser reducido a 0.5kh0 sin llevar a cabo un "
                      "analisis de la deformacion mediante el metodo Newmark "
                      "o una version simplificada de el.")
# Desplazamiento que HABILITA la reduccion, en m (SI, como todo el codigo).
# El Manual lo escribe en pulgadas: "de 1.0 a 2.0 in O MAS". El habilitante
# es el extremo INFERIOR, 1.0 in; el 2.0 in y el "o mas" dicen que el rango
# sigue abierto por arriba. El comentario que vivia aqui decia "muros que
# admiten 25-50 mm", que redondea la conversion y ademas PIERDE el "o mas":
# un muro con 60 mm de desplazamiento admisible quedaba fuera del rango
# escrito y si califica segun el Manual (NOR-PUE-07).
DESPLAZAMIENTO_HABILITA_REDUCCION_M = 0.0254     # 1.0 in exacta
DESPLAZAMIENTO_REFERENCIA_SUPERIOR_M = 0.0508    # 2.0 in exacta; no es tope
# La reduccion no depende solo de la geometria. AASHTO, del que el numeral es
# traduccion, acumula TRES condiciones y una de ellas no es tecnica.
REDUCCION_KH_CONDICIONES = (
    "el muro es libre de moverse lateralmente bajo la carga sismica",
    "el movimiento lateral durante el evento de diseno es aceptable para el "
    "propietario ('acceptable to the Owner', AASHTO 11.6.5.2.2)",
    "el muro es capaz de desplazamientos de 1.0 a 2.0 in o mas",
)
# Las dos declaraciones admisibles del criterio 'factor_muro_eleccion'. Son
# NOMBRES, no factores: el unico factor normativo de este numeral es
# REDUCCION_KH_POR_DESPLAZAMIENTO.
FACTOR_MURO_SIN_REDUCCION = "sin_reduccion"
FACTOR_MURO_CON_REDUCCION = "reduccion_por_desplazamiento"
FACTOR_MURO_DECLARACIONES = (FACTOR_MURO_SIN_REDUCCION,
                             FACTOR_MURO_CON_REDUCCION)

# --------------------------------------------------------------------------
# CADENA SISMICA (3/4) - inercia del muro y combinacion 100/50 - 50/100
# --------------------------------------------------------------------------
# El termino que faltaba ENTERO en el repositorio (MAT-D6, MAT-X7): la cadena
# de la hoja de ruta termina en k_h y K_AE, y el ensamble de empujes sumaba
# EH + LS + WA + el incremento de Mononobe-Okabe sin ninguna linea de inercia
# del muro. La MISMA seccion de la que la hoja toma k_h0 y la reduccion por
# desplazamiento exige combinar las dos.
P_IR_TEXTO = ("La fuerza lateral total debido al sismo sera aplicada al muro "
              "y la carga de presion del terreno, Pseis sera determinado "
              "teniendo en cuenta el efecto combinado de PAE y PIR, en el "
              "cual: PIR = kh (Ww + Ws)")
# Las definiciones son mas ESTRECHAS de lo que "peso del muro" sugiere, y en
# eso se juega el numero: W_s no es el relleno del trasdos entero.
P_IR_DEFINICIONES = (
    "Ww = peso de la pared.",
    "Ws = peso del suelo que esta inmediatamente encima del muro, incluyendo "
    "el talon del muro.",
)
P_SEIS_TEXTO = ("Para investigar la estabilidad de los muros de contencion, "
                "considerando que los efectos de la combinacion de PAE y "
                "PIR, no son simultaneos, la estabilidad se estudiara de la "
                "siguiente manera: Combinar el 100% de la presion sismica "
                "del terreno PAE con 50% de la fuerza de inercia del muro "
                "PIR, y Combinar el 50% de PAE, pero que no sea menor que la "
                "presion estatica activa del terreno (F = 1/2 gf h2 k), con "
                "el 100% de la fuerza de inercia del muro PIR. El resultado "
                "mas conservador de estos dos analisis se usara para el "
                "diseno del muro de contencion.")
# Las dos combinaciones, como dato: (nombre, fraccion de P_AE, fraccion de
# P_IR). El piso "no menor que la presion estatica activa" viaja aparte, en
# P_SEIS_PISO_ESTATICO, porque es una CONDICION y no un factor.
P_SEIS_COMBINACIONES = (
    ("100% P_AE + 50% P_IR", 1.00, 0.50),
    ("50% P_AE + 100% P_IR", 0.50, 1.00),
)
P_SEIS_PISO_ESTATICO = "50% P_AE + 100% P_IR"
P_SEIS_REGLA = "El resultado mas conservador de estos dos analisis"
# Que NO entra en P_AE, segun el Comentario del mismo articulo. Importa para
# no contar dos veces la sobrecarga de trasdos: su empuje y su propia inercia
# k_h*W_sobrecarga son terminos aparte.
P_AE_EXCLUYE_SOBRECARGA = (
    "La P_AE no incluye ninguna fuerza adicional lateral causada por cargas "
    "de sobrecarga permanente localizadas encima del muro (ejemplo. La "
    "fuerza estatica F_p y la fuerza dinamica k_h*W_surcharge ...)")
# Y que SI incluye, que es la otra mitad de la misma advertencia: AASHTO
# C11.6.5.1, pag. impresa 11-26 (PDF 1495).
P_AE_INCLUYE_ESTATICO = (
    "Since P_AE is the combined lateral earth pressure force resulting from "
    "static earth pressure plus dynamic effects, the static earth pressure "
    "... K_a, should not be added to the seismic earth pressure")

# --------------------------------------------------------------------------
# CADENA SISMICA (4/4) - excentricidad de la resultante en la base
# --------------------------------------------------------------------------
# El unico eslabon de la cadena de estabilidad que no tenia ni procedimiento
# ni vacio declarado (MAT-O16). El limite NO es "el tercio central" a secas:
# depende de gamma_EQ, el factor de carga viva de Evento Extremo I, que este
# expediente todavia no declara -- y por eso el criterio 'gamma_EQ' existe.
NUMERAL_EXCENTRICIDAD_SISMICA = NUMERAL_P_IR
EXCENTRICIDAD_SISMICA_TEXTO = (
    "Para la evaluacion de la excentricidad sismica de los muros que "
    "cimentan en suelo y roca, la ubicacion de la resultante de las fuerzas "
    "de reaccion estara dentro del tercio central de la base para gEQ = 0.0 "
    "y dentro de ocho decimas centrales para gEQ = 1.0. Para valores de gEQ "
    "entre 0.0 y 1.0 la ubicacion de la resultante se obtendra por "
    "interpolacion lineal entre los valores dados en este articulo.")
# Los dos extremos que el numeral tabula, como excentricidad admisible en
# FRACCION de B, SIGUIENDO A AASHTO Y NO AL LITERAL DEL MANUAL (ver
# EXCENTRICIDAD_ERRATA_MANUAL): dos tercios centrales -> e <= B/3; ocho
# decimas centrales -> e <= 0.4*B. Entre ellos, interpolacion lineal sobre
# gamma_EQ.
EXCENTRICIDAD_ADMISIBLE_FRACCION_B = {0.0: 1.0 / 3.0, 1.0: 0.4}
EXCENTRICIDAD_SISMICA_TEXTO_AASHTO = (
    "For seismic eccentricity evaluation of walls with foundations on soil "
    "and rock, the location of the resultant of the reaction forces shall be "
    "within the middle two-thirds of the base for gamma_EQ = 0.0 and within "
    "the middle eight-tenths of the base for gamma_EQ = 1.0. For values of "
    "gamma_EQ between 0.0 and 1.0, the resultant location restriction shall "
    "be obtained by linear interpolation of the values given in this Article.")
NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO = (
    "AASHTO LRFD 9a ed. (2020), Art. 11.6.5.1 'General', pag. impresa 11-25 "
    "(PDF 1494)")
EXCENTRICIDAD_ERRATA_MANUAL = (
    "TERCERA ERRATA DE IMPRENTA DEL MANUAL en esta misma cadena sismica, y la "
    "unica que mueve un numero. El num. 2.8.1.1.14.1 traduce el 'middle "
    "two-thirds' de AASHTO como 'tercio central', que no es lo mismo: dos "
    "tercios centrales es e <= B/3 y el tercio central es e <= B/6, la mitad. "
    "Que es descuido de traduccion y no decision del MTC lo prueba el propio "
    "Manual, tres paginas antes: en su numeral ESTATICO traduce el MISMO giro "
    "correctamente -- 'dentro los dos tercios centrales del ancho de la base' "
    "-- y en el mismo parrafo sismico traduce bien 'eight-tenths' como 'ocho "
    "decimas centrales'. Solo degrada 'two-thirds', y solo ahi. "
    "Y LA LECTURA LITERAL ES NORMATIVAMENTE IMPOSIBLE: dejaria el limite bajo "
    "SISMO (e <= B/6) al doble de estricto que el mismo Manual exige bajo "
    "carga estatica permanente (e <= B/3, fundacion en suelo), lo que invierte "
    "la filosofia de estados limite -- Evento Extremo I es raro y mas "
    "tolerante que Resistencia I, no al reves. Con el texto de AASHTO el "
    "articulo es coherente: ANCLA en gamma_EQ = 0.0 sobre el mismo B/3 del "
    "limite estatico y desde ahi RELAJA a 0.4*B cuando gamma_EQ = 1.0. "
    "GANA AASHTO. Seguir la letra del Manual seria conservador -- por eso "
    "esto no cambia ningun resultado ya emitido -- pero rechazaria disenos "
    "que la norma acepta, y sobre todo dejaria la cita sin sostener")

# --------------------------------------------------------------------------
# ESTABILIDAD - presion de contacto en la base (ESTATICO, y no sismico)
# --------------------------------------------------------------------------
# Las formulas de presion de contacto NO estan en el numeral sismico: estan
# aqui, y la fuente las reparte en DOS RAMAS segun el terreno de fundacion.
# Aplicar la de roca a una cimentacion en suelo -- que es lo que hacia este
# proyecto sin decirlo -- sobrestima la presion de pico, o sea es
# conservador, pero es la rama equivocada del numeral y se elegia en
# silencio.
NUMERAL_PRESION_CONTACTO = (
    "Manual de Puentes (MTC) num. 2.8.1.1.12.2 'Capacidad de Carga' "
    "(11.6.3.2 AASHTO), pag. impresa 248 (PDF 249)")
PRESION_CONTACTO_TEXTO = (
    "Si el muro es soportado por una fundacion en suelo: La tension vertical "
    "se debera calcular suponiendo una presion uniformemente distribuida "
    "sobre el area de una base efectiva. La presion vertical se debera "
    "calcular de la siguiente manera: sigma_v = SumaV / (B - 2e) "
    "(2.8.1.1.12.2-1). "
    "Si el muro es soportado por una fundacion en roca: La presion vertical "
    "se debera calcular suponiendo una presion distribuida linealmente sobre "
    "el area de una base efectiva. Si la resultante cae dentro del tercio "
    "central de la base, sigma_vmax = (SumaV/B)(1 + 6 e/B) (2.8.1.1.12.2-2), "
    "sigma_vmin = (SumaV/B)(1 - 6 e/B) (2.8.1.1.12.2-3). Si la resultante cae "
    "fuera del tercio central de la base, sigma_vmax = 2 SumaV / "
    "{3[(B/2) - e)]} (2.8.1.1.12.2-4), sigma_vmin = 0 (2.8.1.1.12.2-5)")
# El limite ESTATICO de excentricidad, que no es el sismico y tambien se
# desglosa por terreno. Se transcribe porque es lo que ancla el extremo
# gamma_EQ = 0.0 del limite sismico y por tanto lo que prueba que el "tercio
# central" de aquel es errata.
#
# EL NUMERAL SE IMPRIME MAL EN EL PROPIO MANUAL: dice "2.3.1.1.12.3", con un
# 3 donde toca un 8, rompiendo la serie 2.8.1.1.12.2 -> ... -> 2.8.1.1.12.5;
# y el indice del Manual repite la errata. La remision a AASHTO (11.6.3.3) si
# es correcta. Se cita como lo imprime, con la advertencia, para que quien lo
# busque lo encuentre.
NUMERAL_EXCENTRICIDAD_ESTATICA = (
    "Manual de Puentes (MTC) num. 2.3.1.1.12.3 'Limites de Excentricidad' "
    "(11.6.3.3 AASHTO) -- el numeral se imprime asi, con 2.3 en vez de 2.8, "
    "errata del Manual que su propio indice repite --, pag. impresa 250 "
    "(PDF 251)")
EXCENTRICIDAD_ESTATICA_FRACCION_B = {"suelo": 1.0 / 3.0, "roca": 0.45}
EXCENTRICIDAD_ESTATICA_TEXTO = (
    "En las fundaciones en suelo la ubicacion de la resultante de las fuerzas "
    "de reaccion debera estar dentro los dos tercios centrales del ancho de "
    "la base. En las fundaciones sobre roca la ubicacion de la resultante de "
    "las fuerzas de reaccion debera estar dentro de los nueve decimos "
    "centrales del ancho de la base. Los criterios especificados para la "
    "ubicacion de la resultante, junto con la investigacion de la presion de "
    "contacto, reemplaza la investigacion de la relacion entre el momento "
    "estabilizador y el momento de vuelco.")

# --------------------------------------------------------------------------
# CADENA SISMICA - las TRES erratas de imprenta del Manual
# --------------------------------------------------------------------------
# El proyecto sigue a AASHTO en los tres puntos y NO al literal del Manual.
# Esta declarado aqui, y no solo en un docstring de M9, porque es lo que
# impide que un revisor "corrija" el codigo contra la letra impresa y rompa
# la formula (MAT-O2, MAT-X2). Las otras dos son K_H0_ROCA_ERRATA y
# EXCENTRICIDAD_ERRATA_MANUAL; ninguna de las tres estaba declarada, y la
# tercera la destapo la auditoria adversarial de esta misma sesion.
NUMERAL_K_AE_MANUAL = ("Manual de Puentes (MTC), Apendice A11 'Diseno "
                       "Sismico de Estructuras de Contencion', num. A.11.3.1 "
                       "'Metodo de Mononobe -Okabe', ec. A.11.3.1-2, pag. "
                       "impresa 586 (PDF 587)")
NUMERAL_K_AE_AASHTO = ("AASHTO LRFD 9a ed. (2020), Appendix A11, Art. "
                       "A11.3.1 'Mononobe-Okabe Method', ec. A11.3.1-1, pag. "
                       "impresa 11-145 (PDF 1614)")
K_AE_ERRATA_MANUAL = (
    "ERRATA DE IMPRENTA DEL MANUAL. El Apendice A11 imprime el denominador "
    "de K_AE con '[1 - raiz(...)]', signo MENOS, verificado renderizando la "
    "pag. impresa 586 (PDF 587) a 6x: el trazo es horizontal unico, sin "
    "trazo vertical. AASHTO, del que el propio Manual declara transcribirlo, "
    "imprime '[1 + raiz(...)]' (pag. impresa 11-145). GANA AASHTO, y no por "
    "preferencia de fuente: con el signo menos K_AE DIVERGE cuando el "
    "radicando tiende a 1, y el caso limite k_h = k_v = 0 deja de devolver "
    "el Ka de Coulomb -- la formula se rompe donde el propio Manual la "
    "manda coincidir. EL CODIGO SIGUE A AASHTO. Quien 'corrija' M9 contra la "
    "letra impresa del Manual rompe la formula")
K_AE_ERRATA_ANOMALIA_ADICIONAL = (
    "En la misma pagina el texto llama a la fuerza 'E_AE' y la formula "
    "imprime 'E_EA', con los subindices transpuestos: otro descuido de "
    "composicion del mismo apendice")

# El agua bajo el nivel freatico: hipotesis del proyecto y la exigencia de la
# que se aparta. Se declara como dato y no como comentario porque la memoria
# tiene que imprimirla (MAT-O3, MAT-X3).
NUMERAL_AGUA_TRASDOS_AASHTO = ("AASHTO LRFD 9a ed. (2020), Art. 3.11.3 "
                               "'Presence of Water', pag. impresa 3-118 "
                               "(PDF 172)")
AGUA_TRASDOS_TEXTO_AASHTO = (
    "Submerged unit weights of the soil shall be used to determine the "
    "lateral earth pressure below the groundwater table.")
HIPOTESIS_EMPUJE_BAJO_NF = (
    "El empuje activo de este proyecto se calcula con el peso especifico "
    "TOTAL del relleno en toda la altura y se le suma la hidrostatica "
    "completa bajo el NF. AASHTO 3.11.3 exige peso especifico SUMERGIDO bajo "
    "el nivel freatico, de modo que el agua de poros se cuenta dos veces en "
    "la zona sumergida. "
    "CUANTO ES, exactamente: el exceso de presion horizontal es "
    "Ka*(gamma - gamma')*h = Ka*gamma_agua*h, o sea CONSTANTE en toda la zona "
    "sumergida y proporcional solo a la profundidad bajo el NF. Con "
    "gamma_sat = 20 kN/m3 (gamma' = 10.19), Ka = 1/3 y h = 0.60 m son "
    "1.96 kPa de mas, siempre. En porcentaje NO hay un solo numero, porque "
    "depende de la altura del muro: sobre un muro de 0.60 m -- todo el sumergido, "
    "que es el caso con que la ficha MAT-O3 lo calculo -- la presion en la "
    "base es 9.9 kPa contra 7.9 kPa, +25 %; sobre uno de 2.00 m con el "
    "freatico a 1.40 m es 19.2 contra 17.3 kPa, +11 %; y sigue bajando con la "
    "altura, porque el exceso no crece y el empuje si. La desviacion es "
    "CONSERVADORA en todos los casos (gamma > gamma' siempre). "
    "Se mantiene, y se declara, porque corregirla exige un peso especifico "
    "sumergido del relleno que este expediente todavia no tiene: aplicar "
    "AASHTO con el unico gamma declarado seria ALIVIAR el empuje sin dato "
    "que lo sostenga. La hoja de ruta no dice nada del NF en el empuje: solo "
    "que 'empuje hidrostatico y subpresion, con NF a 1.4 m, no son "
    "opcionales'")

# QUE DE ESTE BLOQUE TIENE CONSUMIDOR Y QUE NO, declarado en vez de deducirse,
# como ya se hacia con el bloque de gamma_p. Lo consume el calculo (M9):
# F_PGA_TABLA, F_PGA_TABLA_PGA_COLUMNAS, F_PGA_EXIGE_ESTUDIO_DE_SITIO,
# F_PGA_CLASES_EN_ROCA, LECTURAS_COLUMNA_EXTREMA,
# LECTURA_COLUMNA_EXTREMA_ESTRICTA, K_H0_FACTOR_ROCA_A_B, K_V_PRESCRITO,
# K_V_DECLARACION_PRESCRITO, REDUCCION_KH_POR_DESPLAZAMIENTO,
# FACTOR_MURO_DECLARACIONES, FACTOR_MURO_CON_REDUCCION,
# P_SEIS_COMBINACIONES, P_SEIS_PISO_ESTATICO,
# EXCENTRICIDAD_ADMISIBLE_FRACCION_B y los NUMERAL_*. Los textos literales
# K_V_CASO_RESERVADO, K_AE_ERRATA_MANUAL, K_H0_ROCA_ERRATA,
# HIPOTESIS_EMPUJE_BAJO_NF, E030_AMBITO_LECTURA, E030_S5_TEXTO y
# E030_S5_LECTURA no entran en ninguna formula pero SI los invoca M9: viajan
# a la memoria por `condicion_normativa_cabezal`. Lo demas -- los titulos, los
# encabezados, las notas al pie y el resto de los literales -- no lo invoca
# nadie: es la parte de la transcripcion que existe para que la cita sea
# verificable contra el PDF. No es codigo muerto, es la cita.
#
# PGA -> datos_sitio (dato de sitio [S]); la eleccion de filas de F_pga, la
# declaracion de reduccion del muro, el caso reservado de k_v y gamma_EQ ->
# criterios_adoptados

# Combinaciones de carga: Manual de Puentes num. 2.4.5.3 "Factores de Carga y
# Combinaciones" (= 3.4 AASHTO), subnumeral 2.4.5.3.1 (= 3.4.1 AASHTO),
# pag. impresa 140 (PDF 141). Aqui viven los NOMBRES de las tres combinaciones
# que usa el proyecto y, desde la correccion de NOR-PUE-04, tambien los
# FACTORES: las dos tablas del numeral estan transcritas mas abajo.
#
# POR QUE ESTABAN FUERA Y AHORA ESTAN AQUI (NOR-PUE-04). Este comentario decia
# que el Manual "no transcribe la Tabla 3.4.1-1" y que los gamma eran "un
# vacio declarado en criterios_adoptados". Las dos afirmaciones son falsas, y
# la segunda ademas describia un estado del repositorio que ya no existia (el
# criterio tenia valor desde hacia tiempo). El Manual SI transcribe las dos
# tablas, completas y con sus valores, DENTRO del rango de paginas que este
# mismo archivo citaba: Tabla 2.4.5.3.1-1 y Tabla 2.4.5.3.1-2, las dos en la
# pag. impresa 143 (PDF 144). Verificado leyendo el PDF de
# normas/"Puentes (Version Libro).pdf" (encabezado impreso de cada pagina, no
# aritmetica de desfase; el desfase es PDF = impresa + 1).
#
# Declarar un vacio sobre la pagina que trae la tabla es el defecto que
# Sec. 0.5 de la hoja de ruta llama el mas grave: un vacio se ve, una cita
# falsa se cree. Aqui ademas invertia la taxonomia entera -- los gamma son
# exigencia normativa peruana con numeral verificado, o sea [N], y lo unico
# elegido es QUE FILA de la tabla describe a cada estructura de esta obra,
# que es [A] y vive en 'factores_carga_aashto'. Es el mismo reparto de
# F_PGA_TABLA / 'F_pga'. El del factor de muro se le parece pero no es
# igual: alli la parte [N] no es una tabla sino un unico valor
# autorizado (REDUCCION_KH_POR_DESPLAZAMIENTO), y llamarla tabla era el
# defecto NOR-PUE-07.
COMBINACIONES_AASHTO = ("Resistencia I", "Servicio I", "Evento Extremo I")
NUMERAL_COMBINACIONES = "2.4.5.3 (AASHTO LRFD Sec. 3.4.1), pags. 140-143"

# El numeral con que hay que CITAR las dos tablas. El propio Manual las nombra
# de dos formas incompatibles: el rotulo impreso sobre cada tabla dice
# "Tabla 2.4.5.3.1-1" y "Tabla 2.4.5.3.1-2", pero el cuerpo del texto en la
# pag. impresa 142 (PDF 143) las llama "Tabla 2.4.5.3-1" y "Tabla 2.4.5.3-2",
# sin el ".1". Se cita la forma del ROTULO, que es la que un revisor lee sobre
# la tabla que tiene delante.
NUMERAL_TABLA_COMBINACIONES = (
    "Manual de Puentes (MTC) num. 2.4.5.3.1, Tabla 2.4.5.3.1-1 "
    "'Combinaciones de Carga y Factores de Carga' (3.4.1-1 AASHTO), "
    "pag. impresa 143 (PDF 144)")
NUMERAL_TABLA_GAMMA_P = (
    "Manual de Puentes (MTC) num. 2.4.5.3.1, Tabla 2.4.5.3.1-2 "
    "'Factores de carga para cargas permanentes, gamma_p' (3.4.1-2 AASHTO), "
    "pag. impresa 143 (PDF 144)")

# La correspondencia con AASHTO LRFD 9a ed., y en que difieren. Se declara
# porque el proyecto adopta la Via 1 (Sec. 0.2: AASHTO LRFD de extremo a
# extremo) y podria dar por identicas dos tablas que NO lo son: el Manual
# traduce una edicion anterior.
TABLAS_GAMMA_CORRESPONDENCIA_AASHTO = (
    "Tabla 2.4.5.3.1-1 = Table 3.4.1-1 'Load Combinations and Load Factors', "
    "AASHTO LRFD 9a ed. (2020), pag. impresa 3-17 (PDF 71). "
    "Tabla 2.4.5.3.1-2 = Table 3.4.1-2 'Load Factors for Permanent Loads, "
    "gamma_p', pag. impresa 3-18 (PDF 72). "
    "EN LAS COLUMNAS Y FILAS QUE ESTE PROYECTO USA las dos fuentes coinciden "
    "digito a digito, y por eso la peruana basta y se cita ella. DIFERENCIAS "
    "verificadas, ninguna en lo que se usa aqui: (a) la 9a ed. agrega a la "
    "tabla de gamma_p cuatro filas que el Manual no trae -- las tres de "
    "estabilidad interna de muros MSE y la de muros de suelo claveteado; "
    "(b) la 9a ed. dice 'O'Neill and Reese (2010)' donde el Manual dice "
    "'(1999)'; (c) en la fila flexible de 1.50 la 9a ed. exige 'Structural "
    "Plate Culverts with DEEP Corrugations' y el Manual traduce 'planchas "
    "estructurales con corrugaciones', sin 'profundas' -- omision sustantiva, "
    "ver la eleccion del TMC en 'factores_carga_aashto'; (d) en la Tabla -1 "
    "difieren factores de WS (Resistencia III, Resistencia V, Servicio I y "
    "Servicio IV), el LL de Servicio III y los de Fatiga I y II: ninguna de "
    "esas columnas ni de esas combinaciones entra en Sec. 9.2")

# La celda "N/A" de la Tabla 2.4.5.3.1-2. NO es "no declarado" ni "falta el
# dato": la fuente dice expresamente que esa fila no tiene ese extremo. Se le
# da nombre para que ningun consumidor la lea como un cero, un uno o una
# omision, y para que pedirla sea un error del expediente y no un KeyError.
#
# Existe por MAT-D15 / NOR-AAS-04: el criterio afirmaba que la fuente no
# declara minimo para EH en reposo. Lo declara -- 0.90 --; el N/A pertenece a
# la fila SIGUIENTE, "AEP Para paredes ancladas". Un corrimiento de una fila
# entre dos filas que comparten el maximo 1.35.
GAMMA_P_NO_APLICA = None

# El marcador "gamma_p" que la propia Tabla 2.4.5.3.1-1 imprime en la columna
# de cargas permanentes: no es un numero, es una remision a la Tabla -2.
GAMMA_P_MARCA = "gamma_p"

# QUE DE ESTE BLOQUE TIENE CONSUMIDOR Y QUE NO, declarado en vez de deducirse.
# Lo consume el calculo: TABLA_GAMMA_P_FILAS y fila_gamma_p_legible (M8 y M9),
# TABLA_COMBINACIONES_FILAS (M8 y M9), GAMMA_P_NO_APLICA (la guarda de M8) y
# GAMMA_P_MARCA (M9). Lo demas -- los titulos, las columnas, las notas al pie,
# la de erratas, la de completitud, la de correspondencia con AASHTO y
# GAMMA_EQ_TEXTO -- NO lo invoca ningun modulo: es la parte de la
# transcripcion que existe para que la cita sea verificable contra el PDF y
# para que la memoria pueda imprimirla el dia que la Fase 9 se desbloquee. Es
# el mismo caso de TABLA_09_TITULO y TABLA_09_COLUMNAS, que tampoco tienen
# consumidor y estan por la misma razon; no es codigo muerto, es la cita.

TABLA_GAMMA_P_TITULO = ("Tabla 2.4.5.3.1-2 Factores de carga para cargas "
                        "permanentes, γp")
TABLA_GAMMA_P_COLUMNAS = (
    "Tipo de Carga, Tipo de Fundaciones, y Métodos Usados para Fuerza de "
    "Arrastre Hacia Abajo (Downdrag)", "Maximo", "Mínimo")

# LAS DOS COLUMNAS SE ESCRIBEN COMO LAS IMPRIME EL MANUAL, y no son iguales:
# "Maximo" va SIN tilde en el original y "Mínimo" CON ella. Es una errata de
# la fuente, no de esta transcripcion, y por eso la primera no se "arregla".
# La distincion importa: si aqui se quitaran las dos tildes, la nota de erratas
# estaria atribuyendo al Manual una falta que seria del codigo.

# La tabla COMPLETA, las dieciocho filas con valor, aunque el calculo use
# cinco. Es la regla dura del proyecto (NOR-HID-11, NOR-VAC-01): la tabla se
# transcribe entera y la eleccion se declara aparte, porque una tabla podada
# no deja ver de que se eligio una fila.
#
# COMO SE LEEN LOS TRES CAMPOS DE TEXTO, que son transcripcion y no
# nomenclatura de este proyecto: `fila` es el texto LITERAL de la celda,
# `grupo` el encabezado literal del bloque del que cuelga -- EH, EV y DD traen
# sus subfilas colgadas de una fila de titulo -- y `subgrupo` el segundo nivel,
# que solo tienen las tres subfilas flexibles de EV. Estan SEPARADOS a
# proposito: la celda del reposo dice "En reposo.", no "EH: Presión Horizontal
# de la tierra -- En reposo.", y juntarlos en un solo campo haria pasar por
# transcripcion una frase compuesta aqui. Quien necesite una linea sola llama a
# `fila_gamma_p_legible`, y entonces la composicion es visible y esta en un
# solo sitio.
#
# LOS TRES VAN CON SUS TILDES Y CON SUS LETRAS GRIEGAS, al reves que la
# mayoria de este archivo: son texto citado, y un revisor tiene que poder
# buscarlo en el PDF y encontrarlo. Las erratas de imprenta del Manual se
# copian tal cual y se declaran en TABLA_GAMMA_P_ERRATAS.
TABLA_GAMMA_P_FILAS = {
    "DC_componentes_y_auxiliares": {
        "grupo": "", "subgrupo": "",
        "fila": "DC: Componentes y Auxiliares.", "max": 1.25, "min": 0.90},
    "DC_resistencia_IV_solamente": {
        "grupo": "", "subgrupo": "",
        "fila": "DC: Resistencia IV Solamente.", "max": 1.50, "min": 0.90},
    "DD_pilotes_metodo_tomlinson": {
        "grupo": "DD: Downdrag", "subgrupo": "",
        "fila": "Pilotes, α Método de Tomlinson.", "max": 1.40, "min": 0.25},
    "DD_pilotes_metodo_lambda": {
        "grupo": "DD: Downdrag", "subgrupo": "",
        "fila": "Pilotes, λ Método.", "max": 1.05, "min": 0.30},
    "DD_pilotes_perforados_oneill_reese": {
        "grupo": "DD: Downdrag", "subgrupo": "",
        "fila": "Pilotes Perforados, (Drilled Shaft) Método de O’Neill and "
                "Reese (1999).", "max": 1.25, "min": 0.35},
    "DW_superficie_de_rodadura_y_accesorios": {
        "grupo": "", "subgrupo": "",
        "fila": "DW: Superficie de rodadura y accesorios.",
        "max": 1.50, "min": 0.65},
    # Las tres subfilas de "EH: Presion Horizontal de la tierra".
    "EH_activa": {
        "grupo": "EH: Presión Horizontal de la tierra.", "subgrupo": "",
        "fila": "Activa.", "max": 1.50, "min": 0.90},
    "EH_en_reposo": {
        "grupo": "EH: Presión Horizontal de la tierra.", "subgrupo": "",
        "fila": "En reposo.", "max": 1.35, "min": 0.90},
    "EH_AEP_paredes_ancladas": {
        "grupo": "EH: Presión Horizontal de la tierra.", "subgrupo": "",
        "fila": "AEP Para paredes ancladas.",
        "max": 1.35, "min": GAMMA_P_NO_APLICA},
    "EL_esfuerzos_residuales": {
        "grupo": "", "subgrupo": "",
        "fila": "EL: Esfuerzos residuales acumulados resultantes del proceso "
                "constructivo, (Locked-in construction Stresses.)",
        "max": 1.00, "min": 1.00},
    # Las seis subfilas de "EV: Presion vertical de la tierra" (sic, sin
    # tilde en "Presion"). Las tres ultimas cuelgan ademas del subtitulo
    # "Estructuras flexible enterradas" (sic, sin la "s" de flexibles), que la
    # tabla imprime en su propia linea con sus tres opciones marcadas "o ...".
    "EV_estabilidad_global": {
        "grupo": "EV: Presion vertical de la tierra", "subgrupo": "",
        "fila": "Estabilidad global.",
        "max": 1.00, "min": GAMMA_P_NO_APLICA},
    "EV_muros_y_estribos_de_retencion": {
        "grupo": "EV: Presion vertical de la tierra", "subgrupo": "",
        "fila": "Muros y estribos de retención.", "max": 1.35, "min": 1.00},
    "EV_estructura_rigida_enterrada": {
        "grupo": "EV: Presion vertical de la tierra", "subgrupo": "",
        "fila": "Estructura rígida enterrada.", "max": 1.30, "min": 0.90},
    "EV_porticos_rigidos": {
        "grupo": "EV: Presion vertical de la tierra", "subgrupo": "",
        "fila": "Pórticos rígidos.", "max": 1.35, "min": 0.90},
    "EV_flexibles_cajon_metalico_plancha_fibra_vidrio": {
        "grupo": "EV: Presion vertical de la tierra",
        "subgrupo": "Estructuras flexible enterradas",
        "fila": "o Alcantarillas cajón metálicas, plancas estructurales con "
                "corrugaciones y alcantarillas de fibra de vidrio.",
        "max": 1.50, "min": 0.90},
    "EV_flexibles_alcantarillas_termoplasticas": {
        "grupo": "EV: Presion vertical de la tierra",
        "subgrupo": "Estructuras flexible enterradas",
        "fila": "o Alcantarillas termoplásticas.", "max": 1.30, "min": 0.90},
    "EV_flexibles_entre_otros": {
        "grupo": "EV: Presion vertical de la tierra",
        "subgrupo": "Estructuras flexible enterradas",
        "fila": "o Entre otros.", "max": 1.95, "min": 0.90},
    "ES_carga_superficial_en_el_terreno": {
        "grupo": "", "subgrupo": "",
        "fila": "ES: Carga superficial(Sobrecarga) en el terreno",
        "max": 1.50, "min": 0.75},
}


def fila_gamma_p_legible(clave: str) -> str:
    """
    Grupo, subgrupo y celda de una fila de gamma_p en una sola linea, para
    imprimirla. Los tres trozos son literales del PDF; el " -- " que los une
    es de aqui, y por eso la composicion vive en esta funcion y no dentro del
    dato: buscar la frase compuesta en el PDF no la encontraria, buscar
    cualquiera de sus tres trozos si.
    """
    r = TABLA_GAMMA_P_FILAS[clave]
    return " -- ".join(t for t in (r["grupo"], r["subgrupo"], r["fila"]) if t)


# TRES TRAMPAS DE LA EXTRACCION DE TEXTO, comprobadas sobre la celda
# RENDERIZADA y no sobre el volcado plano -- la leccion de NOR-VAC-01, donde
# una prima de SymbolMT se leyo como una raiz cuadrada:
#
#   1. El titulo imprime "gamma_p" con un glifo de fuente Symbol (la
#      extraccion devuelve un caracter de uso privado) y una "p" en negrita
#      matematica. Aqui se escribe el simbolo tal como se LEE en la pagina.
#   2. El encabezado de la primera columna aparece partido por la columna
#      vecina: la extraccion lo devuelve como "Tipo de Carga, Tipo de
#      Fundaciones, y / Factor de Carga / Metodos Usados...". Las dos mitades
#      son de la misma celda, y aqui van unidas como se leen.
#   3. LAS TRES SUBFILAS FLEXIBLES SALEN CON SUS PARES INTERCALADOS: la
#      extraccion da "...alcantarillas de fibra de | 1.50 0.90 | vidrio. |
#      1.30 0.90 | o Alcantarillas termoplasticas. | 1.95 0.90 | o Entre
#      otros.", que leido de corrido asignaria 1.30/0.90 a la fila de la fibra
#      de vidrio y 1.95/0.90 a la termoplastica. La asignacion correcta -- la
#      de la pagina renderizada -- es 1.50 a las metalicas y de plancha, 1.30 a
#      las termoplasticas y 1.95 a "Entre otros", y coincide digito a digito
#      con la Table 3.4.1-2 de AASHTO 9a ed. Esa coincidencia es lo que cierra
#      la lectura.
#
# Las erratas de imprenta del Manual en esta tabla, transcritas donde estan
# para que nadie las "corrija" creyendo que arregla una transcripcion.
TABLA_GAMMA_P_ERRATAS = (
    "Transcripcion literal, con las erratas de imprenta del Manual: 'Maximo' "
    "SIN tilde en el encabezado de columna (mientras 'Mínimo', a su lado, la "
    "lleva); 'EV: Presion vertical de la tierra' sin tilde en 'Presion' "
    "(mientras la fila hermana 'EH: Presión Horizontal de la tierra' si la "
    "lleva); 'Estructuras flexible enterradas', sin la 's' de flexibles; "
    "'plancas' por 'planchas'; y 'Entre otros' donde AASHTO dice 'All "
    "others'. Se copian tal cual: la fila que la memoria imprime tiene que "
    "poder buscarse en el PDF")

TABLA_COMBINACIONES_TITULO = ("Tabla 2.4.5.3.1-1 Combinaciones de Carga y "
                              "Factores de Carga")

# Las TRES combinaciones de Sec. 9.2, tal como las imprime la Tabla
# 2.4.5.3.1-1, por tipo de carga. Las demas filas de la tabla (Resistencia
# II a V, Evento Extremo II, Servicio II a IV, Fatiga I y II) no se
# transcriben porque Sec. 9.2 no las nombra: no es una tabla podada, es que
# la hoja de ruta elige tres combinaciones y estas son esas tres.
#
# La columna de cargas permanentes de la tabla es UNA sola -- "DC DD DW EH EV
# ES EL PS CR SH" -- y por eso DC, EV y EH comparten celda: donde dice
# GAMMA_P_MARCA hay que ir a la Tabla -2, y donde dice un numero ese numero
# vale para las tres.
#
# EVENTO EXTREMO I LLEVA 1.00 EN LAS PERMANENTES, NO gamma_p, y no es un
# error de transcripcion: lo dicen las dos fuentes y el comentario C3.4.1 de
# AASHTO explica por que ("Prior to 2015, these Specifications used a value
# for gamma_p greater than 1.0. This practice went against the intended
# philosophy behind the Extreme Event Limit State", pag. impresa 3-10).
# La celda "--" de la Tabla 2.4.5.3.1-1: la carga NO PARTICIPA en esa
# combinacion. Como el N/A de la Tabla -2, no es un cero: es la fuente
# diciendo que ahi no hay factor.
COMBINACION_NO_PARTICIPA = "--"

# Las CATORCE columnas de la tabla, en su orden impreso. La primera agrupa
# todas las cargas permanentes bajo un solo factor.
TABLA_COMBINACIONES_COLUMNAS = (
    "DC DD DW EH EV ES EL PS CR SH", "LL IM CE BR PL LS", "WA", "WS", "WL",
    "FR", "TU", "TG", "SE", "EQ", "BL", "IC", "CT", "CV")

# Nota literal al pie de la Tabla 2.4.5.3.1-1. NO es la que explica los pares
# del tipo 0.50/1.20 de la columna TU -- este comentario lo afirmaba y era una
# cita falsa dentro de un bloque [N]. Lo que gobierna son las ULTIMAS
# columnas, las de los eventos extremos: donde el Manual pone esta nota al
# pie, AASHTO imprime el encabezado "Use One of These at a Time" sobre EQ,
# BL, IC, CT y CV. Ninguna de esas cinco entra en Sec. 9.2 salvo EQ, y en
# Evento Extremo I es la unica de las cinco con valor.
TABLA_COMBINACIONES_NOTA_AL_PIE = (
    "Usar solamente uno de los indicados en estas columnas en cada "
    "combinación")

TABLA_COMBINACIONES_FILAS = {
    "Resistencia I": {
        "permanentes": GAMMA_P_MARCA,   # DC DD DW EH EV ES EL PS CR SH
        "LS": 1.75,                     # columna LL IM CE BR PL LS
        "WA": {"max": 1.00, "min": 1.00},
        "WS": COMBINACION_NO_PARTICIPA,
        "WL": COMBINACION_NO_PARTICIPA,
        "FR": 1.00,
        "TU": (0.50, 1.20),             # uno de los dos, ver la nota al pie
        "TG": "gamma_TG",
        "SE": "gamma_SE",
        "EQ": COMBINACION_NO_PARTICIPA,
        "BL": COMBINACION_NO_PARTICIPA,
        "IC": COMBINACION_NO_PARTICIPA,
        "CT": COMBINACION_NO_PARTICIPA,
        "CV": COMBINACION_NO_PARTICIPA,
    },
    "Servicio I": {
        "permanentes": {"max": 1.00, "min": 1.00},
        "LS": 1.00,
        "WA": {"max": 1.00, "min": 1.00},
        "WS": 0.30,                     # el Manual; AASHTO 9a ed. da 1.00
        "WL": 1.00,
        "FR": 1.00,
        "TU": (1.00, 1.20),
        "TG": "gamma_TG",
        "SE": "gamma_SE",
        "EQ": COMBINACION_NO_PARTICIPA,
        "BL": COMBINACION_NO_PARTICIPA,
        "IC": COMBINACION_NO_PARTICIPA,
        "CT": COMBINACION_NO_PARTICIPA,
        "CV": COMBINACION_NO_PARTICIPA,
    },
    "Evento Extremo I": {
        "permanentes": {"max": 1.00, "min": 1.00},
        "LS": "gamma_EQ",               # la tabla imprime gamma_EQ, no un numero
        "WA": {"max": 1.00, "min": 1.00},
        "WS": COMBINACION_NO_PARTICIPA,
        "WL": COMBINACION_NO_PARTICIPA,
        "FR": 1.00,
        "TU": COMBINACION_NO_PARTICIPA,
        "TG": COMBINACION_NO_PARTICIPA,
        "SE": COMBINACION_NO_PARTICIPA,
        "EQ": {"max": 1.00, "min": 1.00},
        "BL": COMBINACION_NO_PARTICIPA,
        "IC": COMBINACION_NO_PARTICIPA,
        "CT": COMBINACION_NO_PARTICIPA,
        "CV": COMBINACION_NO_PARTICIPA,
    },
}

# QUE SE TRANSCRIBE Y QUE NO, dicho aqui en vez de deducirse de la ausencia:
# de la Tabla 2.4.5.3.1-1 estan las TRES filas que Sec. 9.2 nombra, con sus
# CATORCE columnas completas. Las otras diez filas -- Resistencia II a V,
# Evento Extremo II, Servicio II a IV, Fatiga I y II -- no estan porque la
# hoja de ruta no las usa: no es una tabla podada, es que Sec. 9.2 elige tres
# combinaciones y estas son esas tres. De la Tabla 2.4.5.3.1-2, en cambio,
# estan las dieciocho filas, tambien las que el calculo no usa.
TABLA_COMBINACIONES_COMPLETITUD = (
    "PARCIAL POR FILAS, COMPLETA POR COLUMNAS: las tres combinaciones que "
    "Sec. 9.2 nombra (Resistencia I, Servicio I, Evento Extremo I), con las "
    "catorce columnas de la tabla. Las otras diez filas de la Tabla "
    "2.4.5.3.1-1 no se transcriben porque ninguna fase del proyecto las "
    "evalua")

# Los pares {1.00, 1.00} no son una invencion: la tabla imprime UN 1.00 para
# toda la columna de cargas permanentes (y para WA, y para EQ), o sea el mismo
# factor sea cual sea el extremo. Se escribe en la forma de dos extremos que
# usan los consumidores para que una fila de la Tabla -1 y una de la Tabla -2
# se lean igual; el numero es el de la fuente y no hay eleccion detras.
TABLA_COMBINACIONES_NOTA_EXTREMOS = (
    "Donde la Tabla 2.4.5.3.1-1 imprime un solo 1.00 para la columna de "
    "cargas permanentes, aqui figura {max 1.00, min 1.00}: es el MISMO "
    "numero escrito en la forma de dos extremos con que se leen las filas de "
    "la Tabla -2, no un par elegido")

# gamma_EQ, el factor de la carga viva en Evento Extremo I: la tabla no trae
# numero y la fuente NO ofrece un par a elegir. Cita literal, verificada:
GAMMA_EQ_TEXTO = (
    "AASHTO LRFD 9a ed., Art. 3.4.1, pag. impresa 3-19: 'The load factor for "
    "live load in Extreme Event Load Combination I, gamma_EQ, shall be "
    "determined on a project-specific basis.' El comentario C3.4.1 (pag. "
    "impresa 3-10) agrega: 'Past editions of the Standard Specifications used "
    "gamma_EQ = 0.0. This issue is not resolved. The possibility of partial "
    "live load, i.e., gamma_EQ < 1.0, with earthquakes should be considered. "
    "Application of Turkstra's rule for combining uncorrelated loads "
    "indicates that gamma_EQ = 0.50 is reasonable for a wide range of values "
    "of average daily truck traffic (ADTT).' O sea: el 0.0 es practica "
    "HISTORICA de ediciones pasadas y el 0.50 una indicacion de "
    "razonabilidad, no dos opciones tabuladas; y quien lo determina es el "
    "PROYECTO ('project-specific basis'), no 'el propietario'")
# ---- Recubrimiento de concreto: el corpus peruano SI lo da ----------------
# NOR-PUE-10. El lado "AASHTO" de la regla del mayor de Sec. 0.2 se venia
# sosteniendo solo contra AASHTO LRFD, con etiqueta [C], mientras el Manual de
# Puentes -- norma peruana vigente, de la que este mismo expediente saca los
# factores de carga y toda la cadena sismica -- transcribe la MISMA tabla y
# los MISMOS factores de modificacion por relacion agua-cemento. Estando en el
# corpus peruano, el numero es [N] y vive aqui.
#
# LO QUE EL TITULO DE LA TABLA DICE Y NADIE HABIA LEIDO -- es la clave de todo
# el cluster C07: "Recubrimiento para las armaduras principales de aceros NO
# PROTEGIDAS". La tabla peruana tiene UNA sola columna porque cubre UNA sola
# categoria de acero: la no protegida, que la 9a ed. de AASHTO llama
# Categoria A. El acero epoxico o galvanizado el Manual lo trata en un
# numeral aparte (2.9.1.5.5.4 "Recubrimiento Protector"). De modo que los
# 3.0 in de "ubicaciones costeras" NO son "el recubrimiento de AASHTO": son el
# del acero SIN recubrir, y con acero protegido la tabla de la 9a ed. baja a
# 2.0 in. Esa condicion de aplicacion es la que faltaba declarar (NOR-AAS-01),
# y por eso el criterio 'categoria_refuerzo_aashto' esta VACIO y bloquea.
#
# Los valores se transcriben en mm, la unidad en que este proyecto especifica
# recubrimientos (E.060 Art. 7.7.1 esta escrito en mm), con la pulgada de la
# fuente al lado. 1 in = 25.4 mm exacto: 3.0 in son 76.2 mm y no 75 (MAT-D16).
RECUBRIMIENTO_MP_TITULO = ("Recubrimiento para las armaduras principales de "
                           "aceros no protegidas")
RECUBRIMIENTO_MP_MM = {
    "agua_salada":                        101.6,   # 4.0 in
    "vaciado_contra_suelo":                76.2,   # 3.0 in
    "costera":                             76.2,   # 3.0 in
    "sales_anticongelantes":               63.5,   # 2.5 in
    "tableros_neumaticos_clavos":          63.5,   # 2.5 in
    "exterior_no_superior":                50.8,   # 2.0 in
    "interior_hasta_n11":                  38.1,   # 1.5 in
    "interior_n14_n18":                    50.8,   # 2.0 in
    "losa_in_situ_inferior_hasta_n11":     25.4,   # 1.0 in
    "losa_in_situ_inferior_n14_n18":       50.8,   # 2.0 in
    "paneles_prefabricados_encofrados":    20.32,  # 0.8 in
    "pilar_prefabricado_no_corrosivo":     50.8,   # 2.0 in
    "pilar_prefabricado_corrosivo":        76.2,   # 3.0 in
    "pilote_prefabricado_pretensado":      50.8,   # 2.0 in
    "pilar_in_situ_no_corrosivo":          50.8,   # 2.0 in
    "pilar_in_situ_corrosivo_general":     76.2,   # 3.0 in
    "pilar_in_situ_corrosivo_protegida":   76.2,   # 3.0 in
    "pilar_in_situ_cascaras":              50.8,   # 2.0 in
    "pilar_in_situ_tremie_o_lechada":      76.2,   # 3.0 in
    # Alcantarillas de cajon de concreto PREFABRICADAS. Las tres filas llevan
    # su condicion en el nombre a proposito (NOR-PUE-14): los "2.0 in / 50 mm
    # para alcantarillas" que el expediente citaba de pasada no son de
    # alcantarillas en general, son de la losa superior de una alcantarilla
    # cajon prefabricada con menos de 2 pies de relleno que ademas no se use
    # como superficie de rodadura. Y 2.0 in son 50.8 mm, no 50.
    "alcantarilla_cajon_prefab_losa_de_rodadura":       63.5,   # 2.5 in
    "alcantarilla_cajon_prefab_losa_menos_2_pies":      50.8,   # 2.0 in
    "alcantarilla_cajon_prefab_otros_miembros":         25.4,   # 1.0 in
}
RECUBRIMIENTO_MP_FILA_TEXTO = {
    "vaciado_contra_suelo": "Vaciado del concreto contra el suelo",
    "costera": "Ubicaciones costeras",
    "agua_salada": "Exposición directa al agua salada",
    "alcantarilla_cajon_prefab_losa_menos_2_pies":
        "Alcantarillas de cajón de concreto prefabricados: forjados con "
        "inferior a 2 pies de relleno que no se utilicen como una superficie "
        "de conducción",
}
# El modificador por relacion agua-cemento, que el criterio ignoraba entero
# (NOR-AAS-05). El Manual lo escribe con DOS vinetas y AASHTO con tres: el
# tramo intermedio (0.40 < W/C < 0.50 -> 1.0) esta en AASHTO Art. 5.10.1 y el
# Manual no lo imprime. Se transcribe lo que el Manual dice, y la ausencia se
# declara en RECUBRIMIENTO_MP_FACTOR_AC_LAGUNA en vez de rellenarse con el
# valor de la otra fuente.
RECUBRIMIENTO_MP_FACTOR_AC = {
    "a_c_menor_igual_0_40": 0.8,
    "a_c_mayor_igual_0_50": 1.2,
}
RECUBRIMIENTO_AC_UMBRAL_BAJO = 0.40    # "Para W/C <= 0.40 ... 0.8"
RECUBRIMIENTO_AC_UMBRAL_ALTO = 0.50    # "Para W/C >= 0.50 ... 1.2"
RECUBRIMIENTO_MP_FACTOR_AC_LAGUNA = (
    "El Manual de Puentes imprime solo dos factores (W/C <= 0.40 -> 0.8 y "
    "W/C >= 0.50 -> 1.2) y deja sin factor la banda intermedia 0.40 < W/C < "
    "0.50, que AASHTO LRFD 9a ed. Art. 5.10.1 (pag. impresa 5-167) si cubre "
    "con 1.0. Este proyecto no cae en esa banda -- su a/c maxima la fija la "
    "Tabla 4.2 de E.060 en 0.40 por cloruros --, asi que la laguna no lo "
    "afecta; se deja escrita para que nadie la resuelva de memoria el dia que "
    "una obra sin cloruros caiga dentro")
# Piso absoluto sobre las barras principales. Es lo que impide que el factor
# de 0.8 pueda llevar el recubrimiento a cualquier cosa.
RECUBRIMIENTO_MP_PISO_MM = 25.4                  # 1.0 in; el Manual escribe
                                                 # "1.0 in (25 mm)" y se aplica
                                                 # la pulgada exacta, que es la
                                                 # mayor de las dos cifras
RECUBRIMIENTO_MP_PISO_TEXTO = (
    "El recubrimiento mínimo sobre las barras principales, incluyendo las "
    "barras protegidas con un recubrimiento de resina epóxico, deberá ser de "
    "1.0 in (25 mm)")
NUMERAL_RECUBRIMIENTO_MP = (
    "Manual de Puentes num. 2.9.1.5.5.3 'Recubrimiento de Concreto' "
    "(5.12.3 AASHTO) y Tabla 2.9.1.5.5.3-1, pags. impresas 377-378 "
    "(PDF 378-379)")

NUMERAL_SOBRECARGA_TRASDOS = "2.1.4.3.9, pag. 91"
NUMERAL_ZAPATA_EN_TALUD = "2.8.1.3.1.2c, pags. 272-273"
# NUMERAL_K_H0 se declaraba aqui por segunda vez, como "2.8.1.1.14.2" a secas,
# y esta segunda asignacion pisaba a la primera. Vive ahora una sola vez, en
# el bloque de la cadena sismica, con el subnumeral que de verdad escribe la
# igualdad (2.8.1.1.14.2.1) y su pagina.

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
# LAS DOS TABLAS DE DURABILIDAD SE LEEN JUNTAS, y esa es la primera cosa que
# faltaba. La Tabla 4.2 y la Tabla 4.4 llevan las dos, al pie, la MISMA nota
# marcada con asterisco desde sus columnas de a/c y de f'c. No es un adorno de
# imprenta: es la regla que decide que se especifica cuando el sitio tiene
# sulfatos Y cloruros a la vez, que es precisamente el caso de un corredor
# costero con freatico somero. Transcribir una tabla sin la otra, o cualquiera
# de las dos sin la nota, deja el requisito de durabilidad a medias --
# NOR-E060-05 y NOR-E060-06 son ese mismo defecto visto desde dos lados.
NOTA_COMBINACION_4_2_4_4 = (
    "Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se debe "
    "utilizar la menor relación máxima agua-material cementante aplicable y "
    "el mayor f'c mínimo")
NUMERAL_COMBINACION_4_2_4_4 = ("E.060, nota al pie de las Tablas 4.2 y 4.4, "
                               "pags. impresas 37 y 38")

# ---- Tabla 4.2, "Requisitos para condiciones especiales de exposicion" -----
# Las TRES filas, con el texto literal de su condicion. El proyecto consumia
# solo la tercera y la atribuia a "Art. 4.2 / 4.4": el par (0.40, 35) es de la
# TABLA 4.2, y el 4.4 es otra exigencia -- "Proteccion del refuerzo contra la
# corrosion", que remite a la Tabla 4.5 sobre contenido de ion cloruro en el
# concreto endurecido. Dos numerales distintos citados como si fueran uno.
#
# EL ALCANCE DEL DISPARADOR, que la fila escribe y conviene no perder: los
# cloruros que activan esta fila son los "provenientes de productos
# descongelantes, sal, agua salobre, agua de mar o a salpicaduras del mismo
# origen". No es "cloruros en el suelo" en general.
EXPOSICION_ESPECIAL = {
    "baja_permeabilidad": {
        "texto": "Concreto que se pretende tenga baja permeabilidad en "
                 "exposición al agua",
        "a_c_max": 0.50, "fc_min_MPa": 28},
    "congelamiento_deshielo": {
        "texto": "Concreto expuesto a ciclos de congelamiento y deshielo en "
                 "condición húmeda o a productos químicos descongelantes",
        "a_c_max": 0.45, "fc_min_MPa": 31},
    "cloruros": {
        "texto": "Para proteger de la corrosión el refuerzo de acero cuando "
                 "el concreto está expuesto a cloruros provenientes de "
                 "productos descongelantes, sal, agua salobre, agua de mar o "
                 "a salpicaduras del mismo origen",
        "a_c_max": 0.40, "fc_min_MPa": 35},
}
NUMERAL_EXPOSICION_ESPECIAL = "E.060 Tabla 4.2, pag. impresa 37"

# `CLORUROS_EXTERNOS` NO vuelve a escribir el par: lo referencia. Dos
# transcripciones del mismo numero se desincronizan en cuanto una cambie, y
# este archivo ya tiene la fila entera con su texto literal encima.
CLORUROS_EXTERNOS = {
    "a_c_max": EXPOSICION_ESPECIAL["cloruros"]["a_c_max"],
    "fc_min_MPa": EXPOSICION_ESPECIAL["cloruros"]["fc_min_MPa"],
}

# ---- Tabla 4.4, "Requisitos para concreto expuesto a soluciones de sulfatos"
# DOS escalas paralelas, no una. La tabla clasifica la exposicion por el
# sulfato soluble en agua presente en el SUELO (porcentaje en peso) o por el
# sulfato en el AGUA (ppm). La transcripcion anterior llevaba solo la del
# suelo, de modo que un expediente con analisis de agua -- lo esperable con
# ANA de por medio -- no podia clasificarse (NOR-E060-05). Y los cementos de
# la exposicion moderada son SEIS: se transcribian tres.
#
# EL BORDE DE 2,0 % QUE LA TABLA IMPRESA DEJA ABIERTO. La fila severa termina
# en "< 2,0" y la muy severa empieza en "2,0 <", de modo que SO4 = 2,0 % exacto
# -- y 10 000 ppm exacto en la escala del agua -- no cae en ninguna de las dos.
# Es un hueco del texto impreso, no una omision de esta transcripcion, y la
# fuente primaria NO lo resuelve. Quien si lo resuelve es la hoja de ruta:
# su Sec. 3.3 escribe la fila severa como "0.20 - 2.00" y la muy severa como
# "> 2.00", de modo que el punto exacto cae en SEVERA. Se sigue a la hoja de
# ruta, que es la fuente de verdad del proyecto mientras el documento
# normativo no la contradiga -- y aqui no la contradice: calla. Por eso cada
# fila declara si su limite inferior es estricto, en vez de dejar la respuesta
# escondida en un ">=" del codigo. Ver SULFATOS_BORDE_ABIERTO_TEXTO.
SULFATOS = [
    {"exposicion": "insignificante",
     "so4_suelo_pct": (0.00, 0.10), "so4_agua_ppm": (0, 150),
     "limite_inferior_estricto": False,
     "cementos": (), "a_c_max": None, "fc_min_MPa": None},
    {"exposicion": "moderada",
     "so4_suelo_pct": (0.10, 0.20), "so4_agua_ppm": (150, 1500),
     "limite_inferior_estricto": False,
     "cementos": ("II", "IP(MS)", "IS(MS)", "P(MS)", "I(PM)(MS)", "I(SM)(MS)"),
     "a_c_max": 0.50, "fc_min_MPa": 28},
    {"exposicion": "severa",
     "so4_suelo_pct": (0.20, 2.00), "so4_agua_ppm": (1500, 10000),
     "limite_inferior_estricto": False,
     "cementos": ("V",), "a_c_max": 0.45, "fc_min_MPa": 31},
    {"exposicion": "muy_severa",
     "so4_suelo_pct": (2.00, None), "so4_agua_ppm": (10000, None),
     # ESTRICTO: la tabla imprime "2,0 <" y la hoja de ruta "> 2.00". El
     # valor 2,0 % exacto se queda en la fila severa.
     "limite_inferior_estricto": True,
     "cementos": ("V más puzolana",), "a_c_max": 0.45, "fc_min_MPa": 31},
]
NUMERAL_SULFATOS = "E.060 Tabla 4.4, pag. impresa 38"
SULFATOS_NOTA_AGUA_DE_MAR = ("Se considera el caso del agua de mar como "
                             "exposición moderada")
SULFATOS_NOTA_PUZOLANA = (
    "Puzolana que se ha comprobado por medio de ensayos, o por experiencia, "
    "que mejora la resistencia a sulfatos cuando se usa en concretos que "
    "contienen cemento tipo V")
SULFATOS_BORDE_ABIERTO_TEXTO = (
    "La Tabla 4.4 imprime la fila severa como '< 2,0 %' y la muy severa como "
    "'2,0 % <': el valor 2,0 % exacto -- y 10 000 ppm exacto en la escala del "
    "agua -- no cae en ninguna de las dos. El hueco lo cierra la hoja de ruta, "
    "que en su Sec. 3.3 escribe 'Severa 0.20 - 2.00' y 'Muy severa > 2.00': el "
    "punto exacto queda en SEVERA (cemento V, a/c 0.45, f'c 31 MPa). Se sigue "
    "esa lectura y no la mas exigente porque la fuente primaria no contradice "
    "a la hoja de ruta en este punto: calla. Se declara porque es una lectura, "
    "no un dato -- la tabla impresa no la escribe -- y porque la unica "
    "diferencia practica entre las dos filas es el cemento (V frente a V mas "
    "puzolana): la relacion a/c y el f'c minimo son los mismos, de modo que el "
    "recubrimiento no cambia por este borde")

# ---- E.060 Art. 7.7.1: el lado peruano de la regla del recubrimiento mayor -
RECUBRIMIENTO = {"contra_suelo": 70, "suelo_intemperie_ge_3_4": 50,
                 "suelo_intemperie_le_5_8": 40}           # Art. 7.7.1, mm
# El texto LITERAL de cada inciso. Importa porque el rotulo corto que el
# proyecto usa para el primero -- "vaciado contra el suelo" -- recoge solo la
# mitad de la condicion: el articulo exige las dos cosas a la vez, colocado
# contra el suelo Y expuesto permanentemente a el.
RECUBRIMIENTO_TEXTO = {
    "contra_suelo": "Concreto colocado contra el suelo y expuesto "
                    "permanentemente a él",
    "suelo_intemperie_ge_3_4": "Concreto en contacto permanente con el suelo "
                               "o la intemperie: barras de 3/4\" y mayores",
    "suelo_intemperie_le_5_8": "Concreto en contacto permanente con el suelo "
                               "o la intemperie: barras de 5/8\" y menores, "
                               "mallas electrosoldadas",
}
NUMERAL_RECUBRIMIENTO = "E.060 Art. 7.7.1, pag. 54"
# El encabezado del 7.7.1 remite EL MISMO al 7.7.5.1: el aumento por ambiente
# corrosivo no es una nota externa que alguien decidio traer, es la excepcion
# que el propio articulo de los 70/50/40 mm declara.
RECUBRIMIENTO_SALVEDAD_TEXTO = (
    "Debe proporcionarse el siguiente recubrimiento mínimo de concreto al "
    "refuerzo, excepto cuando se requieran recubrimientos mayores según "
    "7.7.5.1 ó se requiera protección especial contra el fuego")
AMBIENTE_CORROSIVO_AUMENTAR = "E.060 Art. 7.7.5.1, pag. 55"
# TEXTO LITERAL, corregido (NOR-E060-04). El repo entrecomillaba "aumentar
# adecuadamente" -- forma verbal que el articulo no imprime -- y ademas
# omitia la alternativa expresa del final, que es un camino de cumplimiento
# distinto del que el proyecto contempla: se puede aumentar el recubrimiento
# O disponer otro tipo de proteccion. Sin numero: el articulo no fija cuanto,
# asi que el aumento se declara en criterios_adoptados, no aqui.
AMBIENTE_CORROSIVO_TEXTO = (
    "En ambientes corrosivos u otras condiciones severas de exposición, debe "
    "aumentarse adecuadamente el espesor del recubrimiento de concreto y debe "
    "tomarse en consideración su densidad y porosidad o debe disponerse de "
    "otro tipo de protección")

# ---- E.060, refuerzo de muros - MINIMO OBLIGATORIO ------------------------
# Que "no gobierna el diseno" y que "es informativo" no son lo mismo, y este
# bloque decia lo segundo cuando lo cierto es lo primero. La Via 1 de Sec. 0.2
# pone el DIMENSIONAMIENTO bajo AASHTO LRFD Sec. 5 y deja a E.060 la
# durabilidad y los recubrimientos: de ahi que Sec. 9.4 hable de "referencia
# de cuantias minimas". Pero el Art. 14.3.1 fija un piso, y un piso se aplica
# -- rho_diseno = max(rho_calculado, rho_minimo), en `M9.cuantia_de_diseno` --
# no se imprime.
#
# LO QUE ESTE BLOQUE AFIRMABA DE MAS (NOR-E060-01). Decia que el 14.3.1 fija
# "un PISO por debajo del cual NINGUN muro se arma". Para un muro cualquiera
# pasa; para un muro de CONTENCION, que es lo que el cabezal es, el propio
# Capitulo 14 tiene un articulo especifico que lo exceptua:
#
#     14.8.2  "El refuerzo mínimo será el indicado en 14.3. Este requisito
#     podrá exceptuarse cuando el Ingeniero Proyectista disponga juntas de
#     contracción y señale procedimientos constructivos que controlen los
#     efectos de contracción y temperatura."
#
# La excepcion existe, es potestativa, y exige DOS actos del proyectista a la
# vez -- disponer las juntas Y señalar los procedimientos --, no uno. Este
# proyecto NO la invoca: no hay juntas de contraccion ni procedimientos
# constructivos declarados en el expediente, de modo que el minimo se aplica
# entero. Lo que cambia es el argumento: se aplica porque nadie ejercio la
# excepcion, no porque la norma no la ofrezca. Ver
# EXCEPCION_REFUERZO_MIN_MURO_TEXTO, que M9 imprime junto al minimo.
#
# El segundo minimo de E.060 -- el 0.0025 del Art. 11.10.10.2 bajo cortante
# alto -- sigue sin transcribirse como constante [N] porque la hoja de ruta no
# lo recoge (solo cita el 14.3.1); queda declarado como vacio en el criterio
# 'cortante_alto_muro_e060_art_11_10_10_2'. Mientras siga asi, el 0.0020 de
# abajo es el minimo MENOR de los dos que tiene E.060, y M9 obliga a contestar
# expresamente cual aplica.
CUANTIA_MIN_MURO = {"horizontal": 0.0020, "vertical": 0.0015}   # Art. 14.3.1, pag. 133
NUMERAL_CUANTIA_MIN = "E.060 Art. 14.3.1, pag. 133"
EXCEPCION_REFUERZO_MIN_MURO_TEXTO = (
    "El refuerzo mínimo será el indicado en 14.3. Este requisito podrá "
    "exceptuarse cuando el Ingeniero Proyectista disponga juntas de "
    "contracción y señale procedimientos constructivos que controlen los "
    "efectos de contracción y temperatura")
NUMERAL_EXCEPCION_REFUERZO_MIN_MURO = "E.060 Art. 14.8.2, pag. 134"

# DOS UMBRALES DE ESPESOR, no uno (NOR-E060-02). Se parecen y no son lo
# mismo, y el expediente aplicaba solo el segundo:
#
#   14.3.2 (pag. 133), 200 mm, ESTRICTO -- "Los muros con un espesor mayor
#     que 200 mm, excepto los muros de sótanos, deben tener el refuerzo en
#     cada dirección colocado en dos capas paralelas a las caras del muro."
#     Alcanza a TODO el refuerzo, en las dos direcciones. El 14.8.2 remite
#     expresamente a 14.3 entero, asi que un muro de contencion lo hereda.
#   14.8.3 (pag. 134), 250 mm, INCLUSIVO -- "El acero por temperatura y
#     contracción deberá colocarse en ambas caras para muros de espesor mayor
#     o igual a 250 mm." Alcanza SOLO al acero por temperatura y contraccion.
#
# Entre 200 y 250 mm el muro lleva refuerzo en dos capas por 14.3.2 aunque el
# acero por temperatura no lo exija por 14.8.3, y la memoria imprimia lo
# contrario ("Acero por temperatura en UNA cara") para todo espesor < 250 mm.
ESPESOR_DOS_CAPAS_REFUERZO = 0.200          # m (200 mm); Art. 14.3.2, estricto
NUMERAL_DOS_CAPAS_REFUERZO = "E.060 Art. 14.3.2, pag. 133"
EXCEPCION_DOS_CAPAS_REFUERZO = "excepto los muros de sótanos"
ESPESOR_TEMPERATURA_DOS_CARAS = 0.250       # m (250 mm); Art. 14.8.3, inclusivo
NUMERAL_TEMPERATURA_DOS_CARAS = "E.060 Art. 14.8.3, pag. 134"
ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0       # <= 3h        Art. 14.3.3
ESPACIAMIENTO_MAX_ABSOLUTO = 0.400          # m (400 mm)   Art. 14.3.3
NUMERAL_ESPACIAMIENTO = "E.060 Art. 14.3.3"

# ---- E.060, concreto ciclopeo (alternativa de muro de gravedad) ----------
# DOS MINIMOS SOBRE EL MISMO MATERIAL, y el expediente declaraba el menor
# (NOR-E060-07). E.060 Art. 22.10 pide f'c = 10 MPa para la matriz; la Tabla
# 503-07 del EG-2013 -- cuya Seccion 503 es la que este proyecto cita para
# cabezales -- clasifica el concreto ciclopeo como Clase G y le pide 14 MPa.
# Para una obra vial del MTC rigen los dos, y por tanto el mayor: la misma
# regla del mayor que Sec. 0.2 aplica al recubrimiento. `M9.verificar_ciclopeo`
# contrasta contra `CICLOPEO_FC_MATRIZ_MIN_APLICABLE` y declara de cual de las
# dos normas sale.
CICLOPEO_FC_MATRIZ_MIN = 10.0               # MPa            Art. 22.10
CICLOPEO_FRACCION_PIEDRA_MAX = 0.30         # del volumen    Art. 22.10
NUMERAL_CICLOPEO = "E.060 Art. 22.10, pags. 194-195"
CICLOPEO_FC_MATRIZ_MIN_APLICABLE = max(CICLOPEO_FC_MATRIZ_MIN,
                                       CICLOPEO_FC_MATRIZ_MIN_EG2013)
NUMERAL_CICLOPEO_APLICABLE = f"{NUMERAL_CICLOPEO} / {NUMERAL_CICLOPEO_EG2013}"
# DEUDA DECLARADA, fuera del alcance de este cluster y anotada para que no se
# pierda: el Art. 22.10.2.3 añade al mismo material un TECHO de calculo --
# "en el cálculo de las resistencias segun 22.5 se utilizará un factor
# phi = 0,5 y se utilizará, para el diseño, un valor de f'c no mayor a
# 10 MPa" --, de modo que el material se especifica con el mayor de los dos
# minimos y se DISEÑA con f'c <= 10 MPa y phi = 0.5. `verificar_ciclopeo`
# comprueba hoy la especificacion del material, no el dimensionamiento, y
# ningun modulo dimensiona un muro de gravedad ciclopeo todavia.

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
# que no gobierna el cabezal y lo siguen siendo. LO QUE CAMBIA ES POR QUE.
# El descarte se justificaba SOLO por periodo de retorno -- Sec. 0.4 prefiere
# el PGA de Tr = 1000 anios del Manual de Puentes al sismo de 475 anios de
# E.030 --, que es la via discutible: invita a preguntar por que no usar las
# dos. El argumento de AMBITO es anterior y cierra la pregunta, y el
# expediente no lo invocaba en ningun sitio (NOR-E030-03). Ver
# E030_AMBITO_TEXTO.
#
# Lo que sigue NO es un valor de calculo: son textos literales de E.030 que el
# expediente tiene que poder citar. Dos de ellos existen porque el
# repositorio los estaba diciendo mal.

NUMERAL_E030_AMBITO = ("E.030 (RM 183-2026-VIVIENDA), Art. 4 'Ambito de "
                       "aplicacion', pag. impresa 7 (PDF 7)")
E030_AMBITO_TEXTO = (
    "La presente Norma Tecnica es de cumplimiento obligatorio a nivel "
    "nacional y se aplica a: a) El diseno de edificaciones nuevas. b) El "
    "reforzamiento de edificaciones existentes y la reparacion de "
    "estructuras que resulten danadas por la accion de los sismos "
    "(Capitulo VIII).")
# COMO SE CITA ESTE ARTICULO SIN ESTIRARLO. El Art. 4 acota el ambito POR LO
# AFIRMATIVO: se aplica a edificaciones. No nombra puentes, obras de arte
# vial ni muros de contencion -- ni para incluirlos ni para excluirlos --, de
# modo que decir que "E.030 excluye expresamente los puentes" seria hacerle
# decir lo que no dice. Lo defendible es lo que el articulo si escribe: el
# ambito son las edificaciones, y un cabezal de alcantarilla de una carretera
# no lo es. Concuerdan el Art. 1 ('condiciones minimas para el diseno
# sismorresistente de las edificaciones', pag. impresa 6) y el Art. 61 'Otras
# estructuras' (pag. impresa 26), que alcanza a letreros, chimeneas, torres y
# antenas "instaladas en cualquier nivel del edificio" y por tanto tampoco
# abre el ambito a obras viales.
E030_AMBITO_LECTURA = (
    "El Art. 4 acota el ambito de E.030 a las edificaciones nuevas y al "
    "reforzamiento o reparacion de edificaciones existentes, y un cabezal de "
    "alcantarilla de una carretera no es una edificacion. PERO ESO SOLO NO "
    "BASTA, y creer que basta es el error que este campo cometia: E.030 NO "
    "guarda silencio sobre las obras que no son edificaciones. Su Art. 7.3 "
    "las nombra -- puentes y estructuras hidraulicas entre ellas -- y se las "
    "ATRAE, con una condicion suspensiva: 'mientras no se cuente con normas "
    "nacionales especificas'. De modo que 'no es una edificacion' no es lo "
    "que saca al cabezal de E.030: es el disparador del articulo que lo "
    "mete. LO QUE LO SACA es que la condicion NO SE CUMPLE: el MTC si tiene "
    "norma nacional especifica -- el Manual de Puentes --, y por eso el "
    "mandato de usar Z y S de E.030 no llega a activarse. Es un fundamento "
    "POSITIVO, y mas fuerte que el silencio que este campo invocaba: la "
    "propia E.030 cede el paso ante la norma sectorial. Ver "
    "E030_ART_7_3_TEXTO")

NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION = (
    "E.030 (RM 183-2026-VIVIENDA), Art. 7.3, dentro del Art. 7 "
    "'Consideraciones para el diseno y comportamiento estructural', pag. "
    "impresa 8 (PDF 8)")
E030_ART_7_3_TEXTO = (
    "Mientras no se cuente con normas nacionales especificas para estructuras "
    "tales como reservorios, tanques, silos, puentes, torres de transmision, "
    "muelles, estructuras hidraulicas, tuneles y todas aquellas cuyo "
    "comportamiento sismico difiera del de las edificaciones se deben "
    "utilizar los valores Z y S del Capitulo II de la presente Norma Tecnica "
    "amplificados de acuerdo a la importancia de la estructura, debiendo ser "
    "sustentado por el proyectista tomando en cuenta estandares "
    "internacionales.")
# Es el UNICO numeral de E.030 que nombra puentes u obras hidraulicas: se
# barrio la norma entera y los otros aciertos son otra cosa (los reservorios
# de la tabla de categoria A son EDIFICACIONES esenciales, las 'instalaciones
# hidraulicas y sanitarias' del Art. 55.2 d) son elementos no estructurales
# adosados a una edificacion, y "PUENTE PIEDRA" es un distrito de Lima en el
# Anexo II). Ningun numeral menciona alcantarillas ni obras de arte vial.

NUMERAL_E030_Z = ("E.030 (RM 183-2026-VIVIENDA), Art. 11.1 y Tabla N 1, "
                  "pag. impresa 9 (PDF 9)")
E030_Z_TEXTO = (
    "A cada zona se asigna un factor Z segun se indica en la Tabla N 1 de la "
    "presente Norma Tecnica. Este factor representa la aceleracion maxima "
    "horizontal en suelo rigido con una probabilidad de 10% de ser excedida "
    "en 50 anios.")
# El Art. 11 NO escribe "475 anios": escribe la probabilidad. El Tr = 475 es
# una derivacion aritmetica del proyectista, Tr = -50/ln(0.90) = 474.6, y
# atribuirsela al articulo es ponerle en la boca una cifra que no imprime
# (NOR-E030-01). La cifra SI aparece literal en E.030, pero en otro sitio y
# con otro proposito: el Anexo III, pag. impresa 67, sobre el contenido
# minimo de los estudios de microzonificacion sismica, que pide mapas "a
# nivel de roca o suelo firme (Vs30 >= 800 m/s) y periodo de retorno de 475
# anios". Es la unica pagina de la norma donde "475" aparece.
E030_TR_DERIVACION = (
    "Tr = 475 anios NO lo escribe el Art. 11: es la derivacion de la "
    "probabilidad que si escribe, Tr = -50/ln(0.90) = 474.6 ~ 475. La cifra "
    "aparece literal en el Anexo III de E.030 (pag. impresa 67), en el "
    "contenido minimo de los estudios de microzonificacion sismica, no en la "
    "definicion de Z")

NUMERAL_E030_S5 = ("E.030 (RM 183-2026-VIVIENDA), Art. 14.6, Tabla N 2, fila "
                   "S5, pag. impresa 11 (PDF 11)")
# La ultima vineta de la celda S5, que el repositorio no recogia. Es la
# afirmacion normativa mas fuerte que el expediente hace sobre este sitio, y
# se declaraba como "referencia muerta" (NOR-E030-02).
E030_S5_TEXTO = (
    "Estos casos no estan cubiertos en la clasificacion establecida en la "
    "Tabla N 2 de la presente Norma Tecnica. Se prohibe las construcciones "
    "apoyadas sobre estos perfiles, salvo que, se efectue un estudio "
    "especifico para el sitio, en el cual se debe considerar los "
    "mejoramientos en el estrato del perfil.")
E030_S5_LECTURA = (
    "Es una prohibicion CONDICIONADA, no absoluta: la misma oracion la "
    "levanta con estudio especifico de sitio y mejoramiento del estrato. "
    "Leerla como bloqueo duro va mas alla de la fuente; leerla como "
    "referencia muerta se queda muy por debajo. La fila S5 se llama 'Suelos "
    "excepcionales' y su primera vineta es 'Suelos potencialmente licuables', "
    "que es la razon por la que este expediente se atribuye esa letra. La "
    "Tabla N 3 del num. 14.7 -- la que el num. 14.8 obliga a usar para "
    "clasificar -- NO tiene fila S5, solo S0 a S4, coherente con que 'estos "
    "casos no estan cubiertos'")
# DONDE DISCREPAN LOS DOS ESQUEMAS, que es lo que el expediente cruzaba sin
# declararlo: E.030 SI mete los suelos potencialmente licuables en su
# categoria excepcional (S5); AASHTO y el Manual de Puentes NO los nombran en
# su Clase de Sitio F, y tratan la licuefaccion por otra via (AASHTO LRFD 9a
# ed., Art. 10.5.4.2 'Liquefaction Design Requirements'). El salto
# "licuable -> Clase F" no esta escrito en ninguno de los dos documentos que
# el criterio 'clase_sitio' invoca (NOR-AAS-02). Resolverlo no es materia de
# este archivo: es la premisa que el expediente tiene abierta.
E030_S5_VS_CLASE_F = (
    "E.030 clasifica los suelos potencialmente licuables en su perfil S5 "
    "'Suelos excepcionales' (Art. 14.6, Tabla N 2). AASHTO LRFD 9a ed. y el "
    "Manual de Puentes NO los nombran en su Clase de Sitio F y tratan la "
    "licuefaccion por via distinta de la clase de sitio (AASHTO Art. "
    "10.5.4.2). Los dos esquemas discrepan justamente en el rasgo que motiva "
    "la clasificacion de este sitio, y el salto de uno al otro no lo escribe "
    "ninguno de los dos: es premisa abierta del expediente, no cita")


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
)
# SULFATOS y CLORUROS_EXTERNOS SALIERON de esta lista al cablearse (C07). Se
# declaraban aqui como "agresividad quimica: la decide el EMS del expediente,
# no este calculo", y era verdad a medias: el EMS decide el DATO, y con el
# dato las dos tablas si producen un numero que el calculo usa. Hoy
# `M9.requisitos_durabilidad_concreto` las combina por la nota al pie comun,
# de ahi sale la relacion a/c maxima, y de la a/c sale el factor que modifica
# el recubrimiento del refuerzo. El insumo -- 'exposicion_quimica_ems' -- es
# un [S] pendiente de ensayo, y mientras no llegue el calculo se detiene.
