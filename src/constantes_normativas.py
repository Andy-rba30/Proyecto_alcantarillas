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

# ---------------------------------------------------------------------------
# EL REGISTRO NORMATIVO, y por que este archivo lo importa
# ---------------------------------------------------------------------------
# `src/normativa/` guarda la TRANSCRIPCION -- la tabla entera, con sus notas,
# su cita y su pagina PDF verificada -- y este archivo guarda la VISTA DE
# CALCULO que los modulos consumen. No es una capa nueva: es el patron que
# este archivo ya usaba (MANNING derivado de TABLA_09_FILAS, V_MAX de
# TABLA_10_FILAS, RIESGO_ADMISIBLE de TABLA_02_FILAS) llevado a su sitio, con
# el comentario que lo acompañaba de razon: "si la transcripcion se corrige,
# esta vista se corrige con ella y no quedan dos copias que puedan divergir".
#
# LA DIRECCION DE LA DEPENDENCIA IMPORTA y es de una sola via:
#
#     normativa/  <-  constantes_normativas.py  <-  criterios_adoptados.py
#                                                <-  modulos M0..M11
#
# El registro NO importa nada de la derecha. De ahi que conozca la CLAVE del
# criterio o del dato de sitio que resuelve una condicion y nunca el objeto:
# la resolucion es tardia y la hace el consumidor.
#
# Los nombres publicos de este archivo NO CAMBIAN. Un consumidor sigue
# leyendo `MANNING`, `V_MAX` o `SOBRECARGA_TRASDOS_H_EQ` con la misma forma y
# el mismo valor; lo unico que cambia es de donde salen.
# El motivo del bloqueo «metodo no evaluable», escrito UNA vez (EXT-3).
from src.modelos import MOTIVO_METODO_NO_EVALUABLE
from typing import Tuple

from src.normativa import registro as _registro_normativo

_reg = _registro_normativo.construir()

# ================= Manual de Hidrologia (RD 20-2011-MTC/14) =================
# El umbral que separa alcantarilla de puente. Los DOS numerales lo escriben,
# cada uno desde su lado, y por eso se citan los dos:
#   4.1.1.3.1 "Aspectos generales" (pag. impresa 70): "alcantarilla ... cuya
#       luz sea menor a 6.0 m";
#   4.1.1.5.1 "Aspectos generales" (pag. impresa 87): "puente ... cuya luz sea
#       mayor o igual a 6.0 m".
# LA SEGUNDA PAGINA ESTABA CORRIDA (NOR-HID-05): la cita decia 88, y la pag.
# impresa 88 trae "a.1) Topografia - Batimetria del cauce y zonas adyacentes",
# del num. 4.1.1.5.2. El numeral 4.1.1.5.1 ocupa las impresas 86-87 y la frase
# que fija el valor se imprime en la 87.
LUZ_MAX_ALCANTARILLA = 6.0          # m; >= 6.0 -> puente
NUMERAL_LUZ_ALCANTARILLA = _reg.cita("MC_HHD.4.1.1.3.1").como_texto()
NUMERAL_LUZ_PUENTE = _reg.cita("MC_HHD.4.1.1.5.1").como_texto()

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

# ---------------------------------------------------------------------------
# EL OTRO BORDE LIBRE DEL MISMO MANUAL -- el par de valores del BADEN
# ---------------------------------------------------------------------------
# ESTA AQUI PORQUE ES [N] Y NO PORQUE LO USE UN CANAL. Es lo que el num.
# 4.1.1.4.1 e) imprime, y lo que imprime vale igual en cualquier obra del pais:
# el mismo reparto que CLAUDE.md fija para F_PGA_TABLA frente a 'F_pga'. La
# TABLA es normativa; cual valor aplica a esta obra es del proyectista.
#
# Y AQUI LA DISTANCIA ENTRE LAS DOS COSAS ES MAYOR QUE DE COSTUMBRE, porque
# entre la fuente y el uso hay DOS saltos y no uno:
#
#   1. El objeto.   El apartado cuelga de «4.1.1.4  BADENES» y mide contra la
#                   SUPERFICIE DE RODADURA. VC1 mide contra la CORONACION DE UN
#                   CANAL. Llevar el par de un datum al otro es analogia.
#   2. La eleccion. Aun concedida la analogia, la fuente da una banda y NINGUNA
#                   regla para elegir dentro de ella. El 0.50 lo pone quien
#                   firma.
#
# Los dos saltos viven en 'borde_libre_canal_m' [A], con esta banda por
# `sensibilidad`. Aqui solo esta la banda, que es el hecho sobre la norma.
#
# EL MANUAL NO FIJA BORDE LIBRE PARA UN CANAL, y esta verificado por ausencia
# sobre las 225 paginas: ver `citas.SIN_BORDE_LIBRE_DE_CANAL`. Sin ese barrido
# esta constante seria una fuente ajena tapando un vacio que quiza no existia,
# que es la forma exacta de NOR-VAC-01.
BORDE_LIBRE_BADEN_RANGO_M = (0.30, 0.50)   # m, texto corrido, sin tabla
NUMERAL_BORDE_LIBRE_BADEN = _reg.cita("MC_HHD.4.1.1.4.1e").como_texto()
NUMERAL_BORDE_LIBRE_BADEN_RANGO = _reg.cita(
    "MC_HHD.4.1.1.4.1e#RANGO").como_texto()

Y_SOBRE_D_MAX = 0.75                # borde libre >= 25%
NUMERAL_BORDE_LIBRE = _reg.cita("MC_HHD.4.1.1.3.7b").como_texto()
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
# una ADOPCION que la memoria tiene que declarar. DESDE C05 (PC-24) LA
# ADOPCION TIENE SITIO PROPIO: los criterios [A] de perfil
# 'borde_libre_y_sobre_d_max' y 'velocidad_minima_autolimpieza_m_s' de
# criterios_adoptados.py, con estas dos cifras como valor por defecto y que
# solo se pueden endurecer. Aqui quedan las CIFRAS que la fuente escribe
# ([N], tabla); alli la ELECCION de aplicarlas como rechazo ([A]).
V_MIN = 0.25                        # m/s -- ver abajo
NUMERAL_V_MIN = _reg.cita("MC_HHD.4.1.1.3.6#VMIN").como_texto()
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
LAUSHEY_K = 3.1                     # d50 = V^2/(3.1*g), ec. (49) del
                                    # num. 4.1.1.3.7 c), pag. impresa 80.
                                    # El 3.1 SI esta impreso en la formula.
# ---------------------------------------------------------------------------
# G_LAUSHEY -- el numero es defendible y la cita no lo era (NOR-HID-01, MAT-O7)
# ---------------------------------------------------------------------------
# ESTA CONSTANTE LLEVABA ESCRITO: "g tal como lo escribe la Sec. 4.1.1.3.7 c)
# junto a su formula de d50". ES FALSO, y verificado en contra sobre el PDF: el
# num. 4.1.1.3.7 c) "Socavacion local a la salida de la alcantarilla" (pag.
# impresa 80, PDF 83) define g SIN NUMERO. Su lista de variables dice, literal:
#
#     g       : Aceleración de la gravedad (m/s2)
#
# y en toda esa pagina no hay otro numero que el 3.1 del denominador y el (49)
# del rotulo de la ecuacion.
#
# ES EL MISMO GENERO DE DEFECTO QUE EL PROYECTO YA PURGO CON EL "19.62 = 2g":
# una atribucion que suena razonable, que nadie comprueba porque el numero es
# correcto, y que manda al revisor a una pagina donde no esta lo que la cita
# promete. Una cita que no se puede comprobar es indistinguible de una
# inventada.
#
# DONDE SI ESCRIBE EL MANUAL g = 9.8, barrido sobre sus 225 paginas ("9.8"
# como gravedad aparece en dos y solo dos; "9.81" no aparece ni una vez):
#
#   num. 3.12.5 "Otras Metodologias", pag. impresa 63 (PDF 66):
#       "la velocidad critica (Vc) se define como la raiz cuadrada del calado
#        critico (yc) multiplicado por la aceleracion de la gravedad
#        (g= 9.8 m/s2)"
#   num. 4.1.1.5.4 b.2.4) "Metodo de Laursen", pag. impresa 111 (PDF 114):
#       "g       : Aceleración de la gravedad (9.8 m/s2)"
#
# El segundo es socavacion general por contraccion en PUENTES, no la de salida
# de alcantarilla. O sea: el 9.8 es la gravedad que ESTE Manual usa, leido
# entero, y por eso el valor se conserva; lo que se corrige es DE DONDE se
# dice que sale. Se citan los dos sitios y no uno, porque los dos lo escriben
# y ninguno es el numeral de Laushey.
#
# LA HOJA DE RUTA YA ESTA CORREGIDA: su Fase 6 escribia "g = 9.8 m/s2" bajo
# el encabezado "Laushey — num. 4.1.1.3.7 c), pag. 80", presentando el numero
# como si el numeral lo imprimiera, y hoy lleva la atribucion buena con su
# nota «Corregido (NOR-HID-01, MAT-O7)». La Discrepancia DIS-HR-G-LAUSHEY
# quedo RESUELTA en I2 (el registro estaba atras de la v8) y vive en el
# manifiesto.
#
# Uso exclusivo de M6 (Laushey). La gravedad generica del resto del script
# (M4: tirante critico, control de salida) es constantes_fisicas.G = 9.81.
G_LAUSHEY = 9.8                      # m/s2
NUMERAL_LAUSHEY = _reg.cita("MC_HHD.4.1.1.3.7c").como_texto()
NUMERAL_G_LAUSHEY = _reg.cita("MC_HHD.3.12.5#G").como_texto()
NUMERAL_G_LAUSHEY_SEGUNDA_FUENTE = _reg.cita(
    "MC_HHD.4.1.1.5.4b24#G").como_texto()
# El numeral que NO lo escribe, declarado para que la correccion tenga donde
# estar dicha y para que un test tenga contra que fallar si alguien la
# revierte.
NUMERAL_LAUSHEY_SIN_VALOR_DE_G = _reg.cita("MC_HHD.4.1.1.3.7c#G").como_texto()
G_LAUSHEY_ATRIBUCION = (
    "El num. 4.1.1.3.7 c), que es el de la formula de d50, NO escribe ningun "
    "valor de g: define el simbolo y su unidad. El 9.8 es la gravedad que el "
    "Manual usa, y la escribe en otros dos numerales -- el 3.12.5 (pag. "
    "impresa 63) y el 4.1.1.5.4 b.2.4) (pag. impresa 111) --. El 9.81 no "
    "aparece ni una vez en sus 225 paginas. Se conserva el numero y se "
    "corrige la atribucion")
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
NUMERAL_DISENO_HIDRAULICO = _reg.cita("MC_HHD.4.1.1.3.6").como_texto()
# El numeral con el que ESTE se confundio antes de S5, declarado para que la
# confusion no pueda repetirse en silencio: el 4.1.1.3.5 es "Recomendaciones y
# factores a tomar en cuenta para el diseño de una alcantarilla" y NO contiene
# ninguna tabla de rugosidad.
NUMERAL_RECOMENDACIONES_ALCANTARILLA = _reg.cita("MC_HHD.4.1.1.3.5").como_texto()
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
# R-4: LOS VALORES DEL BLOQUE A.2 SON LA LECTURA CORREGIDA, NO LA IMPRESA.
# La pagina imprime las tres columnas del bloque «A.2 NO METALICOS» UN RENGLON
# POR ENCIMA de sus rotulos, de modo que quien lea `concreto_tubo_recto` al
# pie de la letra en la pag. impresa 75 encuentra 0.011/0.013/0.014 y no los
# 0.010/0.011/0.013 que estan aqui. La errata esta demostrada y declarada en
# `normativa/discrepancias.py::DIS-MCHHD-T09-A2-DESPLAZADA` -- por coordenadas
# de linea base y por contraprueba con el bloque A.1 de la misma pagina, que NO
# esta desplazado --. La correspondencia con Ven Te Chow 1983, que la tabla
# declara como su fuente, se invocaba tambien aqui y NO es verificable en
# normas/: desde la auditoria de T-3 (H10) la errata se sostiene en la
# evidencia interna de la pagina, y el corrimiento alcanza tambien a los
# bloques B.1, B.2 y C, que este archivo no transcribe. Leida al pie de la
# letra, la tabla seria MAS conservadora para capacidad (n_max mayor).
#
# LA REMISION LA AÑADE C2 y no es adorno: hasta ahora la errata vivia en
# `normativa/` y este archivo transcribia la lectura corregida SIN DECIR QUE
# LO ERA. Quien leyera solo `constantes_normativas` y fuera a la pagina
# encontraba otros tres numeros y no tenia con que explicarse la diferencia.
# Afecta a las tres filas de A.2 que hay aqui: `concreto_tubo_recto`,
# `concreto_afinado` y `madera_duelas`. El bloque A.1 -- las dos de metal
# corrugado -- no esta afectado.
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
    # C2: la fila que sostiene la analogia del cajon. Se transcribe con sus
    # valores de la LECTURA CORREGIDA (errata DIS-MCHHD-T09-A2-DESPLAZADA),
    # igual que sus hermanas. Ningun material la consume todavia: el criterio
    # que la declara lo abre C5.
    "concreto_afinado": {
        "fila": "A.2 NO METALICOS - a. Concreto - afinado",
        "min": 0.011, "normal": 0.012, "max": 0.014},
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

# EL COEFICIENTE DE UNIDADES DE MANNING, que hasta PD estaba implicito. La
# formula de Manning NO es dimensionalmente homogenea: con n adimensional,
# A*R^(2/3)*S^(1/2) tiene dimension L^(8/3) y Q tiene L^3/T, y la diferencia,
# L^(1/3)/T, la absorbe un coeficiente que depende del sistema de unidades:
#
#     Q = (K_MANNING_SI / n) * A * R^(2/3) * S^(1/2)
#
#     SI:      k_n = 1.0   m^(1/3)/s     -- el que este codigo usa
#     ingles:  k_n = 1.486 ft^(1/3)/s    -- se nombra y NO se usa
#
# LO QUE SOSTIENE EL 1.0 ES LA FORMA EN QUE EL MANUAL ESCRIBE LA FORMULA,
# verificado contra el PDF en PD (num. 4.1.1.3.6 "Diseño hidraulico", pag.
# impresa 74, PDF 77): la ec. (47) se imprime
#
#     V = R^(2/3) * S^(1/2) / n      R = A/P      Q = V*A
#
# sin 1.486, sin 1.49 y sin ningun k_n, y su lista de variables declara
# unidades integramente SI -- "Q : Caudal (m3/s)", "V : Velocidad media de
# flujo (m/s)", "A : Area de la seccion hidraulica (m2)", "R : Radio
# hidraulico (m)", "S : Pendiente de fondo (m/m)" -- y ninguna para n. El 1.0
# es el coeficiente que esa ecuacion, con esas unidades, exige, y es lo mismo
# que la Sec. 4.1 de la hoja de ruta transcribe como «1/n». `M3._caudal_manning`
# lo aplicaba como (1/n) sin declararlo, y eso es exactamente lo que la regla
# de Unidades de CLAUDE.md prohibe: una constante empirica dependiente de
# unidades sin nombre `_SI` ni comentario imperial. Lo midio el piloto
# dimensional de I4 (tests/test_dimensional_piloto.py) y PD lo declaro aqui
# SIN mover un solo numero: multiplicar por 1.0 es la identidad.
#
# DE DONDE SALE EL 1.486, y no es de la practica: lo imprime HDS-5 3a ed.
# (hif12026.pdf), Apendice B, pag. impresa B.1 (PDF 203), ec. (B.3), en
# unidades inglesas y sin dar su equivalente SI:
#     "The usual form of the Manning equation is as follows:
#      V = (1.486/n) R^(2/3) S^(1/2)   (B.3)"
# con "V is the mean velocity of flow, ft/s (m/s)" y "R is the hydraulic
# radius, ft (m)". Verificado contra el PDF en PD. La copia de 1985
# (fhwa_culvert_hydraulics_hds5si.pdf) imprime la misma ecuacion como su
# ec. (35), Appendix B, PDF 363, en una imagen y sin pagina impresa. Ninguna
# fuente peruana de normas/ lo imprime: el Manual solo escribe la forma SI.
# Numericamente, 1.486 es 1/0.3048^(1/3) = 1.4859 redondeado --la conversion
# de m^(1/3)/s a ft^(1/3)/s--, y es el mismo phi de la relacion K = 2g/phi^2
# con que K_FRICCION_SI explica el 29 y el 19.63.
#
# POR QUE EL 1.486 SE NOMBRA Y NO SE USA: todo el codigo opera en SI (regla
# de Unidades), y usar el 1.486 con R en metros seria el error silencioso
# SIMETRICO al del 29 de K_FRICCION_SI y al del Ku = 1.0 de KU_SI: no falla
# ruidosamente, devuelve un caudal un 48.6 % mayor para el mismo tirante y un
# tirante normal mas chico del real. Por eso el imperial esta escrito al lado
# del valor y no entra en ninguna formula.
#
# ETIQUETA: [N], por la misma regla que KU_SI (que tambien es un coeficiente
# de unidades y tambien vive aqui como [N]): el valor lo fija la ecuacion de
# una norma peruana vigente con numeral verificado, es el mismo numero en
# cualquier obra del pais y ningun proyectista lo elige. No es [C] porque no
# cubre un vacio --el Manual escribe la formula--, y no va a
# constantes_fisicas.py porque no es una constante universal: es una
# convencion de sistema de unidades, como KU_SI, y cambia de valor al cambiar
# de sistema.
K_MANNING_SI = 1.0                  # Q = (K_MANNING_SI/n)*A*R^(2/3)*S^(1/2). Imperial: 1.486
NUMERAL_K_MANNING_SI = _reg.cita("MC_HHD.4.1.1.3.6").como_texto()

# LAS FILAS ENTRE LAS QUE 'n_manning_cajon' PUEDE ELEGIR SU ANALOGIA. Un marco
# de concreto no puede tomar prestada la n de un metal corrugado ni la de unas
# duelas de madera: la analogia que el criterio declara es DENTRO del subgrupo
# «a. Concreto» del grupo A, que es el unico que describe el material del
# conducto. Se deriva del rotulo literal de la fila, no de una lista escrita a
# mano, para que traer una fila nueva del subgrupo la incluya sola.
_SUBGRUPO_CONCRETO_T09 = "A.2 NO METALICOS - a. Concreto"
FILAS_MANNING_CONCRETO = frozenset(
    clave for clave, fila in TABLA_09_FILAS.items()
    if fila["fila"].startswith(_SUBGRUPO_CONCRETO_T09))

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
# SE LEE DEL REGISTRO, no se reescribe aqui. La interpretacion vive como
# `Interpretacion` en `TablaNormativa.interpretacion` de `MC_HHD.T10`, que es
# el unico tipo del proyecto que OBLIGA a declarar lo que juega en contra: una
# lectura que no encuentra nada en contra no se ha buscado a si misma. Tenerla
# ademas escrita aqui era una segunda redaccion de la misma cosa -- justo lo
# que NOR-HID-04 pide separar de la cita, duplicado.
_INTERPRETACION_T10 = _reg.tabla("MC_HHD.T10").interpretacion
TABLA_10_INTERPRETACION_PROYECTO = (
    "INTERPRETACION DEL PROYECTISTA, NO DEL MANUAL: "
    + _INTERPRETACION_T10.texto
    + " En contra de esta lectura juegan hechos de la propia fuente: "
    + "; ".join(_INTERPRETACION_T10.en_contra)
    + ". A favor: " + "; ".join(_INTERPRETACION_T10.a_favor)
    + ". Se imprime SIEMPRE separada de la cita.")
# Vista de calculo: los valores de la fila, tal cual. V3 aplica el MAYOR (el
# techo del acabado de mejor calidad) y no verifica el menor: el piso de
# velocidad es V_MIN, no el extremo inferior de esta fila.
V_MAX = {clave: fila["valores"] for clave, fila in TABLA_10_FILAS.items()}

# ---------------------------------------------------------------------------
# Longitud maxima de cuneta -- dos cifras que NO tienen la misma fuerza
# ---------------------------------------------------------------------------
# NOR-HID-02, cerrado en sus dos extremos.
#
# LA PAGINA. La cita decia "pag. 178". La pagina impresa 178 (PDF 181) trae la
# TABLA Nº 34 "Dimensiones minimas", que es el apartado c) del mismo numeral;
# el apartado d) "Desague de las cunetas", con las dos longitudes, esta en la
# 179 (PDF 182).
#
# EL CARACTER, que es lo que el dict pelado borraba. La fuente escribe las dos
# cifras con verbos DISTINTOS, y tratarlas como dos topes duros equivalentes
# hace pasar por exigencia lo que es recomendacion:
#
#   250 m (region seca o poca lluviosa)  "sera de 250m como maximo", futuro
#       imperativo, PERO con valvula de escape expresa en la misma frase:
#       "las longitudes de recorridos mayores deberan justificarse
#       tecnicamente". Es un maximo rebatible por justificacion tecnica, no un
#       tope absoluto.
#   200 m (region muy lluviosa)  "se recomienda reducir esta longitud maxima a
#       200m". Recomendacion pura, sin verbo imperativo.
#
# Y UN HUECO DE LA FUENTE que conviene ver: el apartado nombra solo DOS
# regimenes -- "seca o poca lluviosa" y "muy lluviosa" -- y deja sin longitud
# el regimen intermedio "lluviosa" que su propia Tabla Nº 34 tabula.
LONG_MAX_CUNETA = {"seca": 250.0, "muy_lluviosa": 200.0}   # m
NUMERAL_LONG_MAX_CUNETA = _reg.cita("MC_HHD.4.1.2.1d").como_texto()
LONG_MAX_CUNETA_CARACTER = {
    "seca": ("EXIGENCIA CON JUSTIFICACION ADMITIDA: «la longitud de las "
             "cunetas sera de 250m como maximo, las longitudes de recorridos "
             "mayores deberan justificarse tecnicamente»"),
    "muy_lluviosa": ("RECOMENDACION: «en region muy lluviosa se recomienda "
                     "reducir esta longitud maxima a 200m»"),
}
LONG_MAX_CUNETA_LAGUNA = (
    "El apartado 4.1.2.1 d) nombra dos regimenes -- «seca o poca lluviosa» y "
    "«muy lluviosa» -- y no asigna longitud al regimen intermedio "
    "«lluviosa» que su propia Tabla Nº 34 tabula. Es un hueco del texto "
    "impreso, no de esta transcripcion")

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
# EL NOMBRE LLEVA EL SUFIJO _SI, como manda la regla de CLAUDE.md para toda
# constante empirica dependiente de unidades (MAT-O19). Se llamaba
# `KU_METRICO`, y ese nombre no dice cual es el otro valor: en el sistema
# INGLES Ku vale 1.0, y la fuente los imprime juntos en una linea -- "Ku Unit
# conversion 1.0 (1.811 SI)". Usar el 1.0 en metrico es el error silencioso
# SIMETRICO al del 29 de K_FRICCION_SI: no falla ruidosamente, devuelve un q*
# 1.811 veces mas chico, que cae en la rama no sumergida cuando le tocaba la
# sumergida y sale un HW plausible y equivocado. Por eso el imperial se
# nombra aqui y NO se usa en ninguna parte. Las otras dos constantes con la
# misma forma son K_FRICCION_SI (mas abajo) y K_MANNING_SI (bloque de la
# Tabla Nº 09), que PD declaro con este mismo molde.
KU_SI = 1.811                       # q* = KU*Q/(A*D**0.5). Imperial: 1.0
NUMERAL_KU_SI = _reg.cita("HDS5_3ED.A.2").como_texto()
NUMERAL_KS_PENDIENTE = _reg.cita("HDS5_3ED.A.2.1#KS").como_texto()
NUMERAL_TABLA_A1 = _reg.cita("HDS5_3ED.TA.1").como_texto()
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
# `caudal_adimensional` multiplica por KU_SI = 1.811, el q* que compara
# M4 esta ya en la escala inglesa y los umbrales que le corresponden son 3.5 y
# 4.0. Cambiarlos por los del parentesis seria aplicar dos veces la conversion.
Q_LIM_NO_SUMERGIDO = 3.5
Q_LIM_SUMERGIDO    = 4.0            # entre ambos: interpolacion lineal
NUMERAL_Q_LIM_NO_SUMERGIDO = _reg.cita("HDS5_3ED.A.2.1#QLIM").como_texto()
NUMERAL_Q_LIM_SUMERGIDO = _reg.cita("HDS5_3ED.A.2.2#QLIM").como_texto()
# La ZONA DE TRANSICION entre las dos ramas: su numeral, corregido
# (NOR-HDS-06). No es el "Cap. IV" que el criterio citaba -- ese es "CULVERT
# DESIGN FOR AQUATIC ORGANISM PASSAGE" en la 3a ed. --, es el num. 3.1.3.
NUMERAL_ZONA_TRANSICION = _reg.cita("HDS5_3ED.3.1.3#TRANSICION").como_texto()
# Y la Tabla C.2, de donde sale ke: pag. impresa C.6, no C.2 (NOR-HDS-01).
NUMERAL_TABLA_KE = _reg.cita("HDS5_3ED.TC.2").como_texto()

# LA VISTA DE CALCULO DE LA TABLA C.2, y por que el cajon la necesita y el
# tubo no. Mismo patron que `HDS5_INLET`: se DERIVA de la transcripcion, no se
# copia, de modo que no puede divergir de ella.
#
# EL PROBLEMA QUE RESUELVE ES QUE EL NUMERO NO IDENTIFICA LA FILA. En el
# bloque «Box, Reinforced Concrete» el ke 0.2 aparece en TRES filas, el 0.5 en
# DOS y el 0.7 en UNA, y tres de las siete se rotulan con el mismo texto
# --«Square-edged at crown»-- bajo rotulos de agrupacion distintos. Un
# criterio que declarase «ke = 0.2» seria por tanto INDECIDIBLE: la memoria no
# podria decir de que fila salio, que es justo la condicion que el propio
# criterio 'ke_entrada_cajon' advierte que se pierde. Por eso lo que se
# declara en el marco es la CLAVE DE LA FILA, y el numero se lee de aqui --
# igual que 'embocadura_cajon' declara una carta y no un juego de K, M, c, Y.
#
# 'ke_entrada' (el circular) SIGUE SIENDO UN NUMERO y no se toca en C5: su
# valor esta declarado, tiene consumidor y funciona, y cambiar la forma de un
# criterio con valor por simetria es mover un dato de proyecto sin que nadie
# lo haya pedido. La asimetria queda escrita aqui para que se lea como lo que
# es -- una diferencia deliberada, no un descuido -- y su cierre es la
# migracion de 'ke_entrada' al mismo patron, que no es de esta sesion.
_TC2 = _reg.tabla("HDS5_3ED.TC2")
KE_HDS5_C2 = {
    _TC2.clave_corta(f): {
        "ke": f.valores["ke"],
        # Los dos textos que la memoria tiene que imprimir JUNTOS: la fila
        # suelta no identifica nada.
        "fila": f.etiqueta_literal,
        "agrupacion": f.jerarquia[-1] if f.jerarquia else "",
        "bloque": f.jerarquia[0] if f.jerarquia else "",
    }
    for f in _TC2.filas if "ke" in f.valores
}
# LAS CLAVES QUE 'ke_entrada_cajon' PUEDE TOMAR, y no son las 22 de arriba.
# La auditoria adversarial de C5 lo midio: `KE_HDS5_C2` trae la tabla entera y
# una guardia que valide contra ella ACEPTA UNA FILA DE TUBO para el marco --
# «concreto_headwall_square_edge», ke = 0.5, numero plausible y cita falsa --,
# que es NOR-HID-01 cometido por la guardia escrita para cerrarlo. El
# subconjunto se deriva del BLOQUE de la propia transcripcion, no de un
# prefijo de la clave.
KE_CAJON_C2 = frozenset(
    k for k, v in KE_HDS5_C2.items() if v["bloque"].startswith("Box"))

# LA VISTA DE CALCULO, DERIVADA DE LA TRANSCRIPCION Y NO COPIADA DE ELLA.
# Hasta C2 este diccionario estaba ESCRITO A MANO con los mismos numeros que
# `normativa/tablas.py::T_HDS5_A1` ya transcribia: dos copias que podian
# divergir sin que nada avisara, que es exactamente lo que D2 del diseño del
# registro prohibe y lo que MANNING, V_MAX y RIESGO_ADMISIBLE ya evitaban.
# C2 lo pasa al patron. Los tres valores circulares NO SE MUEVEN: la
# transcripcion ya decia lo mismo, y T14 ahora lo comprueba en vez de
# confiarlo.
#
# DOS CAMPOS NO SALEN DE LA TABLA, Y CADA UNO POR UNA RAZON DISTINTA:
#
#   `forma`  SI es columna de la Tabla A.1 -- «Equation Form» --, y C2 la
#            transcribio. Sale de la tabla como los demas.
#   `Ks`     NO es columna de ninguna tabla: vive en la lista de variables
#            del num. A.2.1, pag. impresa A.2 (PDF 191), que lo escribe en
#            una linea -- «Ks Slope correction, -0.5 (mitered inlets +0.7)» --.
#            Es decir: la fuente lo da como REGLA sobre la configuracion de
#            borde, no como dato por carta. Se aplica esa regla, y se aplica
#            SOBRE EL ROTULO LITERAL de la fila, que es donde la fuente
#            escribe «mitered». Ninguna de las dieciocho filas del cajon lo
#            es (quince hasta T-2, que sumo las tres de la Carta 13).
_TA1 = _reg.tabla("HDS5_3ED.TA1")
# LOS DOS VALORES QUE TOMA LA COLUMNA «Equation Form» DE LA TABLA A.1, con
# nombre porque el 1 y el 2 sueltos en una comparacion no dicen nada. No son
# una eleccion del proyecto: el num. A.2.1 escribe DOS ecuaciones no
# sumergidas y la tabla dice, carta por carta, cual le toca a cada una.
#
#   FORMA_1   HWi/D = H_c/D + K*(q*)^M + Ks*S      ec. (A.1)
#   FORMA_2   HWi/D = K*(q*)^M                     ec. (A.2), SIN Ks*S
#
# QUE SEPARA LAS DOS FORMAS: LA COLUMNA, Y NADA MAS. Esta linea decia que «la
# regla que las separa la escribe el num. A.3», y es FALSO -- lo escribi yo en
# C3 y lo refuto la auditoria --. El num. A.3 prohibe cruzar coeficientes
# entre FORMAS GEOMETRICAS: «coefficients for rectangular (box) shapes should
# not be used for nonrectangular (circular, arch, pipe-arch, etc.) shapes and
# vice-versa». Eso no habla de formas de ECUACION.
#
# Y la propia Tabla A.1 lo demuestra: FORMA Y GEOMETRIA SON ORTOGONALES.
# Medido sobre sus 36 filas -- «Rect. Box Concrete» aparece con Forma 1 (Carta
# 8) Y con Forma 2 (Cartas 9 a 11); «Circular» aparece con Forma 1 (Carta 3) Y
# con Forma 2 (Carta 55) --. Una prohibicion sobre geometrias no puede ser la
# regla que separa las formas, porque la misma geometria vive en las dos.
#
# Lo que HDS-5 dice de las formas esta en el num. A.2.1 y es descriptivo, no
# prohibitivo: que hay dos, que la (1) parte del tirante critico y la (2) es
# exponencial tipo vertedero, y que la (2) «is the only documented form of
# equation for some of the inlet control equations». Que constante va con que
# ecuacion lo dice la COLUMNA «Equation Form», fila por fila.
FORMA_1 = 1
FORMA_2 = 2
KS_INGLETE = 0.7                    # num. A.2.1, pag. impresa A.2 (PDF 191)
KS_SIN_INGLETE = -0.5


def _ks_de(configuracion: str) -> float:
    """
    El Ks que el num. A.2.1 asigna a una configuracion de borde.

    Se decide sobre el rotulo LITERAL de la carta -- «Mitered to slope» --
    porque es ahi donde la fuente pone la condicion. No hay tercera rama: si
    manana una carta trajera otra palabra para el inglete, este predicado
    daria -0.5 en silencio, y por eso `test_ks_esta_en_todas_las_cartas_de_la_tabla_a1`
    comprueba que todo Ks del diccionario sea uno de los dos valores.
    """
    return KS_INGLETE if "mitered" in configuracion.casefold() else KS_SIN_INGLETE


HDS5_INLET = {   # cartas por forma/material; dentro de cada una, por borde
    _TA1.clave_corta(f): {
        "K": f.valores["K"], "M": f.valores["M"],
        "c": f.valores["c"], "Y": f.valores["Y"],
        "Ks": _ks_de(f.valores["inlet_configuration"]),
        "forma": f.valores["equation_form"],
    }
    for f in _TA1.filas
}
# LAS CARTAS DE CAJON, para validar 'embocadura_cajon'. Misma leccion que
# `KE_CAJON_C2` y el mismo hallazgo de la auditoria de C5: sin este
# subconjunto, `M2.catalogo` acepta una carta CIRCULAR para un marco -- se
# midio con «circular_concreto_square_edge_headwall», que le da a un cajon las
# constantes de la Carta 1 y ademas la Forma 1 con su Ks*S --, y el paso de
# memoria imprime que la carta es «del bloque de CAJON» invocando el num. A.3,
# que es justo la regla que se estaria violando. Se deriva del rotulo
# «Shape and Material» de la transcripcion, no de un prefijo de la clave.
CARTAS_CAJON_TA1 = frozenset(
    _TA1.clave_corta(f) for f in _TA1.filas
    if "box" in str(f.valores["shape_and_material"]).casefold())

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
                                    # OJO: 29 es el valor ingles, impreso
                                    # redondeado. Exacto: 2*32.2/1.486^2 = 29.164
                                    # TEST UNITARIO OBLIGATORIO.
# De donde sale el 19.63: es el valor que el propio HDS-5 imprime, junto al 29
# del sistema ingles, como su constante K en SI. Los dos son cifras de la
# FUENTE PRIMARIA, transcritas, no una derivacion propia. Verificado en la 3a
# ed. (hif12026.pdf) en dos sitios: num. 3.1.4 "Outlet Control", ec. (3.4b),
# pag. impresa 3.10 (PDF 92) -- "KU = 29 in English Units (19.63 in SI)" --, y
# la ec. (DG 3.1), pag. impresa DG3.3 (PDF 296) -- "KU is 29 (19.63 in SI
# Units)".
#
# CUAL ES LA DERIVACION QUE CIERRA, porque hasta PD este comentario decia que
# el 19.63 era la «conversion SI de su constante K = 29», y ESA derivacion no
# cierra: 29 ft^(1/3) * 0.3048^(1/3) = 19.51 m^(1/3), un 0.6 % por debajo del
# 19.63 transcrito (lo midio el piloto dimensional de I4). El 29 es 29.164
# redondeado a dos cifras, y lo que HDS-5 convirtio fue el valor exacto de la
# relacion de abajo, K = 2g/phi^2:
#
#     ingles:  2 * 32.2 / 1.486^2 = 29.164 ft^(1/3)     -> el 29 impreso
#     al SI:   29.164 * 0.3048^(1/3) = 19.627 m^(1/3)   -> el 19.63 impreso
#     directo: 2 * 9.81456 / 1^2 = 19.629 m^(1/3)       -> el 19.63 impreso
#
# La dimension de K es L^(1/3) --es lo que hace adimensional a K*n^2*L/R^(4/3)
# con n adimensional--, y por eso la conversion de longitud entra con exponente
# 1/3. Lo mide tests/test_dimensional_piloto.py
# (`test_K_FRICCION_SI_cierra_desde_2g_sobre_phi_cuadrado_y_no_desde_el_29`).
#
# LA COPIA DE 1985 QUE ESTA EN normas/ NO SIRVE PARA ESTO, y hay que decirlo
# porque lleva "si" en el nombre del archivo (MAT-O12, MAT-X5): sus ecs. (4b)
# y (5), en la pag. 54 del PDF, imprimen "29 n^2 L / R^1.33" con rotulos de
# unidades duales "ft (m)", y su gravedad, en la pag. 53, es
# "32.2 ft/s/s (9.8 m/s/s)". Leida literal "en SI" reproduce exactamente el
# error del 29: x1.477 sobre el TERMINO de friccion (+47.7 %), que en CP-8
# sube H de 0.4977 a 0.5455 m (+9.6 % sobre H). El 19.63 solo lo imprime la
# 3a ed.
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
# el TERMINO DE FRICCION -- unas 950 veces menos que el +47.7 % que el 29
# imperial produce sobre ese mismo termino (+9.6 % sobre H en CP-8), que es el
# error que esta constante existe para atrapar.
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
H_O_NUMERAL = _reg.cita("HDS5_3ED.3.3.3#HO").como_texto()
# Texto literal de la condicion de uso. Las DOS citas estan en la misma pagina
# impresa 3.24 y en dos sitios distintos de ella, y decir cual es cual importa
# (era una sola atribucion para las dos, y una de ellas era falsa):
#
#   la primera es una vineta de la lista "The manual method has the
#   assumptions:";
#   la segunda esta en el parrafo de prosa que sigue a esa lista, el mismo que
#   trae la condicion de 1.2D.
#
# CORREGIDO EN EXT-0 (EXT-M-02, PC-25): la segunda cita estaba ELIDIDA SIN
# MARCAR. Entre «...(dc + D)/2.» y «If the headwater depth falls below 0.75D»
# la fuente escribe la oracion sobre las backwater calculations (Section 3.5),
# que es la que dice QUE HACER en la banda de cautela; el registro
# (`HDS5_3ED.3.3.3#HO_1_2D`, citas.py) ya la traia entera y verificada contra
# la PDF 106, y esta transcripcion a mano la habia perdido. Es exactamente la
# clase de divergencia que la regla «ningun texto literal se transcribe dos
# veces» de CLAUDE.md persigue; la v8 §4.3 se corrigio en la misma sesion.
H_O_CONDICION_TEXTO = (
    "Approximate hydraulic gradeline ho = (dc + D)/2 can only be used if the "
    "barrel flows full for most of its length. It should not be used if the "
    "inlet is not submerged.",
    "If outlet control governs and the headwater depth (referenced to the "
    "inlet invert) is less than 1.2D, it is possible that the barrel flows "
    "partly full though its entire length. In this case, caution should be "
    "used in applying the approximate method of setting the downstream "
    "elevation based on the greater of tailwater or (dc + D)/2. If a more "
    "accurate headwater is necessary, backwater calculations (Section 3.5) "
    "should be used to check the result from the approximate method. If the "
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
# LA PRIMERA CONDICION, MEDIDA (E-A): «can only be used if the barrel flows
# full for MOST of its length». Desde E-A el perfil de la lamina
# (`M4.perfil_lamina`, paso 4.3c) mide la longitud a seccion llena, y cuanto
# es «la mayor parte» NO vive aqui: es una lectura del proyectista con
# alternativas admitidas («casi toda»), o sea un [A] con su ventana,
# `criterios_adoptados 'fraccion_llena_mayor_parte'` (0.5, sensibilidad
# 0.5-0.9), declarada ademas como `Interpretacion` de la cita
# HDS5_3ED.3.3.3#HO. Aqui solo viven los dos numeros que la fuente escribe.
# La forma con el MAXIMO -- que es la que implementa `M4.control_salida` -- la
# 3a ed. no la numera: la escribe en prosa ("the greater of tailwater or
# (dc + D)/2", misma pag. 3.24; "or (dc + D)/2 if larger", num. 3.4.5, pag.
# 3.32). Impresa como igualdad esta en la edicion de 1985 que tambien vive en
# normas/, dentro de su procedimiento paso a paso (PDF 67):
H_O_FORMA_MAXIMO_TEXTO = "ho = TW or (dc + D)/2 whichever is larger."
# EL PAQUETE DE IMPLEMENTACION DEL PROCEDIMIENTO DE BARRIL PARCIALMENTE
# LLENO, evaluado y escrito en I1 (2026-09-12) para la sesion que lo
# implemente (NOR-HDS-05; la ficha de docs/decisiones_diferidas.md cita este
# bloque). Se abrio el Cap. III de la 3.a edicion (fuente HDS5_3ED,
# normas/hif12026.pdf) y el procedimiento SI es transcribible; el ensamble es
# sesion propia con plan mode porque toca M4.control_salida, que es motor
# validado. Las piezas, con numeral y pagina leidos del PDF:
#   1. EL PROCEDIMIENTO EN PROSA esta en «Hydraulics of Outlet Control
#      (Unsubmerged Outlet)», pag. impresa 3.12 (PDF 94): el calculo de
#      remanso empieza en la lamina de agua del extremo aguas abajo y avanza
#      hacia la entrada; la frontera aguas abajo es «critical depth at the
#      culvert outlet or ... the tailwater depth, whichever is higher»; y si
#      el perfil corta la clave del barril se empalma una linea de energia de
#      seccion llena con la pendiente de friccion de la Ec. 3.7 (misma pag.).
#   2. LOS DOS UMBRALES SUSTITUTOS YA IMPLEMENTADOS (H_O_HW_SOBRE_D_CAUTELA y
#      H_O_HW_SOBRE_D_MIN) salen de la pag. impresa 3.24 (PDF 106), que
#      ademas remite el calculo fino a la Seccion 3.5.
#   3. LA SECCION 3.5 (pag. impresa 3.34, PDF 116; el computo de perfil en
#      3.5.1, PDF 118-120) es en la 3.a edicion el capitulo de software:
#      HY-8 adopto el perfil de lamina para refinar «flow depth, flow
#      velocity, and length of barrel flowing full». La fraccion de longitud
#      a seccion llena -- exactamente lo que la primera condicion de este
#      bloque necesita -- es un RESULTADO del perfil, no una lectura.
#   4. QUE HABRIA QUE IMPLEMENTAR, Y DONDE: en M4, un perfil de lamina por
#      paso directo (flujo gradualmente variado con el n de Manning y la
#      geometria de theta que M3/M4 ya tienen), desde la frontera
#      max(y_c, TW) <= D en la salida hacia la entrada; con el, (a) la
#      primera condicion pasa de declarada a MEDIDA y (b) bajo
#      HW/D < H_O_HW_SOBRE_D_MIN el HW se calcula por remanso en vez de por
#      la aproximacion que la fuente prohibe ahi. M5 no cambia: consume el
#      mismo Verificacion/PasoDeMemoria que M4 emita.
#      ANOTADO EN EXT-0: «M5 no cambia» ERA FALSO, y lo refuto EXT-M-01 (el
#      hallazgo M-01 de la auditoria externa del 2026-09-19, dictamen en
#      docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md).
#      Bajo TW ahogante (TW >= D, o HW >= D con salida sumergida) el barril
#      fluye lleno y el tirante y la velocidad que V1 y V2 comparan son los
#      del REGIMEN DEL BARRIL, no los del flujo uniforme que M3 entrega:
#      medido, con TW = 1.2 m sobre D = 0.90 m la memoria decia «manda TW:
#      la salida esta ahogada» y en la misma pagina V1 [OK] con y/D = 0.135,
#      cuando a seccion llena Q/A_llena = 0.0786 m/s < 0.25 m/s. Y en
#      pendiente suave con salida libre la velocidad de salida a y_c (HDS-5
#      3.1.6, pag. 3.18) supera a V_erosion (1.508 vs 1.184 m/s), asi que M6
#      recibia una velocidad MENOR que la real. M5 SI cambia -- V2 compara la
#      velocidad de la seccion efectiva y V1 a seccion llena no cumple (MC
#      pag. 79) -- y M6 recibe la velocidad de salida: v8 §1.3, §4.1 y filas
#      V1/V2 enmendadas en EXT-0, codigo en EXT-3. El paquete de arriba sigue
#      valiendo para el PERFIL (E-A); lo que cambia es que M5 no espera a el.
#      HECHO EN EXT-3 (2026-09-20): `M4.regimen_del_barril`,
#      `M4.velocidad_de_salida` y el paso F4.REGIMEN; V1/V2 por regimen en M5
#      (`_exigir_regimen_evaluable`); M6 recibe `ResultadoHidraulico.V_salida`;
#      y bajo control de salida con HW/D < H_O_HW_SOBRE_D_MIN el punto viaja
#      con el bloqueo «metodo no evaluable» (`modelos.MetodoNoEvaluableError`,
#      compuerta en `servicio._compuerta_metodo_h_o`). Lo que sigue pendiente es
#      SOLO el perfil por paso directo (EXT-3b), con los puntos 1 a 5.
#      HECHO EN E-A (2026-09-21): `M4.perfil_lamina` integra por paso directo
#      sobre el PARAMETRO PROPIO de la seccion (regla vinculante #12: la via
#      por tirante no gana consumidores; el llenado del TW se resuelve con
#      Brent sobre `bracket_llenado()`), desde max(y_c, TW) acotado a D hacia
#      la entrada, con la Ec. 3.7 como pendiente de friccion y el empalme con
#      la linea de energia llena en los dos sentidos (un TW sobre la clave que
#      baja de ella aguas arriba; una M2 que la corta). Sale un
#      `modelos.PerfilLamina` en `ResultadoHidraulico.perfil`, con las dos
#      salidas: (a) la fraccion de longitud a seccion llena, juzgada en el
#      paso F4.PERFIL (4.3c) contra 'fraccion_llena_mayor_parte' [A], y (b) el
#      HW por remanso, que bajo HW/D < 0.75 SUSTITUYE a la aproximacion en
#      `ResultadoHidraulico.HW_salida` y, si el remanso no alcanza la entrada
#      (S1 que corta y_c, incluida la de longitud cero de un barril
#      supercritico con TW <= y_c), devuelve el control a la ENTRADA: es la
#      circularidad deshecha. V1 y V2 comparan `perfil.y_max_m` y
#      `perfil.V_min_m_s`, y el bloqueo «metodo no evaluable» queda como el
#      fallback de un resultado sin perfil, que M4 no produce.
#   5. LOS DORADOS NO SE FABRICAN: un caso patron de perfil necesita una
#      corrida de referencia externa citable (HY-8 u otra), que es la misma
#      regla del conflicto #7. E-A lo respeta: sus dos dorados son LIMITES de
#      la propia formula --flujo lleno de punta a punta (el perfil reproduce
#      HW = H + h_o - S*L) y flujo uniforme (TW = y_n)-- y el balance de
#      energia estacion a estacion; ningun numero de perfil se fija como
#      dorado (`tests/test_ea_perfil_lamina.py`).
# Lo que el proyecto hace con la condicion, y que NO puede hacer:
H_O_CONDICION_APLICACION = (
    "h_o se calcula SIEMPRE, y de las tres condiciones que la fuente le pone "
    "el proyecto EVALUA LAS TRES desde E-A (2026-09-21); hasta entonces "
    "evaluaba dos y declaraba la tercera. "
    "SE EVALUAN, punto por punto, los dos limites sobre HW/D: por debajo de "
    "1.2 la fuente pide cautela y por debajo de 0.75 dice que la aproximacion "
    "no debe usarse. Cuando el control de salida GOBIERNA un punto y su HW/D "
    "cae bajo 1.2, la memoria de ese punto lo dice con esas palabras, junto "
    "al HW, y el remanso del paso 4.3d es la comprobacion que la fuente pide "
    "(«backwater calculations (Section 3.5) should be used to check the "
    "result from the approximate method»): si la comprobacion pide MAS carga, "
    "manda ella --medido en E-A, en 165 de 228 combinaciones de la banda el "
    "remanso supera a la aproximacion, hasta +5 %--; un aviso general que no "
    "senala el punto afectado no le sirve al revisor. Y cuando cae bajo 0.75 "
    "la aproximacion NO SE USA (E-A; EXT-M-02, v8 §4.3): el metodo aproximado "
    "no esta definido para ese punto y el HW del punto es el del REMANSO "
    "(pag. impresa 3.12: «For lower headwaters, backwater calculations are "
    "required»), calculado por paso directo desde la salida hacia la entrada. "
    "Si ese remanso no alcanza la entrada --la lamina que sube desde la "
    "salida corta el tirante critico antes de llegar, que es lo que pasa en "
    "un barril supercritico con TW <= y_c--, el control de salida no impone "
    "carga alguna y gobierna la ENTRADA: es la circularidad de la "
    "aproximacion, deshecha. Hasta E-A ese punto viajaba con el bloqueo «"
    + MOTIVO_METODO_NO_EVALUABLE
    + "», diferible a nivel de perfil y no de expediente; el bloqueo queda "
    "como guardia de un resultado sin perfil, que M4 ya no produce. No es "
    "un incumplimiento: subir de diametro solo baja HW/D. "
    "SE MIDE la primera condicion --que el barril fluya lleno en la mayor "
    "parte de su longitud--, que hasta E-A no se podia evaluar: exige un "
    "perfil de la lamina de agua a lo largo del conducto, y el paso 4.3c lo "
    "calcula y publica la longitud a seccion llena. «La mayor parte» se lee "
    "como MAS DE LA MITAD ('fraccion_llena_mayor_parte' [A], lectura declarada "
    "en el registro con su ventana). El criterio adoptado 'geometria_control_salida' = "
    "'seccion_llena' sigue decidiendo de que seccion salen V y R de la "
    "formula de H, y la premisa que compartia con h_o --que el barril vaya "
    "lleno-- ya no entra por dos puertas sin comprobarse: se comprueba en el "
    "paso 4.3c. "
    "DISCREPANCIA DENTRO DE LA FUENTE, declarada aqui porque es donde se "
    "aplica: la vineta de la pag. 3.24 dice que la aproximacion «can only be "
    "used if the barrel flows full for most of its length», y la prosa de la "
    "pag. 3.12 dice que da «adequate results» hasta HW = 0.75D aun con el "
    "barril «partly full over its entire length». El proyecto aplica la "
    "regla CUANTIFICADA de la 3.12 --la aproximacion gobierna mientras HW/D "
    ">= 0.75-- y MIDE la de la 3.24: cuando el barril no va lleno en la mayor "
    "parte y la aproximacion se usa, el paso 4.3c lo dice con NO CUMPLE sobre "
    "esa condicion, con la cita de la 3.12 que ampara el HW y el remanso al "
    "lado; el punto no se rechaza por ello, porque lo que no se cumple es la "
    "condicion ideal de un metodo cuya validez la propia fuente extiende, no "
    "una exigencia sobre el diseño. Es la decision de la v8 §4.3.")

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
# tabla no se imprime si el punto no llego a evaluarse -- y en la corrida de
# referencia de entonces no llegaba: se detenia antes, en un criterio sin
# declarar --, de modo
# que la palabra "recomend" aparecia CERO veces en la memoria generada mientras
# el repositorio afirmaba que era "lo unico que la memoria imprime de V2".
# (Este comentario atribuia la detencion a que «'homogeneidad_serie_fen'
# bloquea el Q de toda la Familia A» hasta T-0, INF-5.1.1: entonces ningun
# modulo leia ese criterio, y un Q vacio es `DatoFaltanteError`. Desde T-1 lo
# lee `MH_hidrologia`, y solo cuando el caudal se calcula. La razon del bloque no
# cambia: una tabla que depende de un resultado no puede ser el unico sitio
# donde viaje el caracter de un umbral.)
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
def _literal_de_cita(cita_id: str) -> str:
    """El texto VERBATIM de una cita del registro. Una sola transcripcion."""
    return _reg.cita(cita_id).texto_literal.texto


def _literal_de_tabla(tabla_id: str, campo: str) -> str:
    """
    El titulo o el texto previo de una tabla del registro, verbatim.

    Estan en `TablaNormativa` y no en `Cita` porque son de la tabla; pero son
    igual de literales y la memoria los imprime igual de entrecomillados, de
    modo que tienen que salir de la misma fuente unica.
    """
    t = _reg.tabla(tabla_id)
    if campo == "titulo":
        return t.titulo_literal
    if campo == "previo":
        return t.texto_previo.texto
    raise KeyError(f"campo de tabla no soportado: {campo}")


def _nota_de_tabla(tabla_id: str, empieza_con: str) -> str:
    """
    Una nota al pie de una tabla del registro, localizada POR SU TEXTO y no
    por su posicion: la Tabla Nº 02 tiene cuatro y dos de ellas no llevan
    marca, de modo que un indice numerico las ataria al orden en que alguien
    las tecleo.
    """
    t = _reg.tabla(tabla_id)
    for nota in t.notas_al_pie:
        if nota.texto.texto.startswith(empieza_con):
            return nota.texto.texto
    raise KeyError(f"{tabla_id}: ninguna nota empieza por «{empieza_con}»")


UMBRALES_DE_VERIFICACION = (
    {"codigo": "V1",
     "fundamento": "F5.V1",
     "que": "Borde libre: y/D no mayor que la relacion de llenado adoptada "
            "(por defecto 0.75: minimo 25 % de borde libre)",
     "citas": ("MC_HHD.4.1.1.3.7b",),
     "literales_de_tabla": (),
     "aplicacion": "Se aplica como umbral DURO (un punto con y/D por encima "
                   "del maximo adoptado se marca 'NO cumple'). Es la lectura "
                   "conservadora y es decision del proyecto, no exigencia del "
                   "numeral: la adopcion vive en el criterio [A] "
                   "'borde_libre_y_sobre_d_max', con el 0.75 recomendado por "
                   "defecto y que solo se puede endurecer. El 0.75 es ademas "
                   "una DERIVACION aritmetica del 25 % que la fuente escribe "
                   "(1 - 0.25): el numeral no imprime ni el 0.75 ni la razon "
                   "y/D. A SECCION LLENA V1 separa dos casos (T-2): llena por "
                   "el CAUDAL DE DISEÑO, que no cumple siempre por la "
                   "exigencia del mismo parrafo; y llena por el NIVEL DEL "
                   "RECEPTOR (TW sobre la clave), donde lo que se hace lo "
                   "declara el criterio [A] 'borde_libre_bajo_tw_ahogante' "
                   "-- no cumple (valor del archivo), o aviso si con su "
                   "propio caudal el barril conserva el borde libre --."},
    {"codigo": "V2",
     "fundamento": "F5.V2",
     "que": "Velocidad minima de autolimpieza: V no menor que el piso "
            "adoptado (por defecto 0.25 m/s)",
     # DOS citas para una sola oracion del Manual, y no es redundancia: la
     # primera mitad («se debera verificar») es EXIGENCIA y la segunda
     # («recomendandose que... 0.25 m/s») es RECOMENDACION. Verificar el piso
     # es obligatorio; el valor del piso es lo recomendado. Con una sola cita,
     # cualquiera de las dos lecturas queda falseada.
     "citas": ("MC_HHD.4.1.1.3.6#VMIN_INICIO", "MC_HHD.4.1.1.3.6#VMIN"),
     "literales_de_tabla": (),
     "matiz": "La oracion contiene las dos cosas: la OBLIGACION de verificar "
              "el minimo y la RECOMENDACION sobre su valor. El proyecto "
              "cumple la primera y endurece la segunda.",
     "aplicacion": "Se aplica como umbral DURO, y la adopcion vive en el "
                   "criterio [A] 'velocidad_minima_autolimpieza_m_s' (por "
                   "defecto los 0.25 m/s recomendados; solo se puede "
                   "endurecer). Se evalua con la velocidad "
                   "de la rama de n MAXIMO -- la estimacion BAJA de velocidad "
                   "--, que es el extremo conservador para un piso. La razon "
                   "del minimo es la sedimentacion que reduce capacidad, no el "
                   "desgaste: por eso vale igual para todos los materiales."},
    {"codigo": "V2b",
     "fundamento": "F5.V2b",
     "que": "Sedimentacion / colmatacion: pendiente del conducto no menor "
            "que la del cauce natural (indicador del HDS-5 num. 5.3.3), "
            "mas el acceso de mantenimiento declarado",
     "citas": ("HDS5_3ED.5.3.3#INDICADORES", "HDS5_3ED.5.3.3#ALINEADO"),
     "literales_de_tabla": (),
     "matiz": "La fuente escribe «are key indicators of potential problems», "
              "no un umbral: es un INDICADOR y no una prohibicion. Como se "
              "aplica lo declara el criterio 'regimen_v2b' [A] (PF-4), que "
              "desde T-2 lo aplica en el archivo como la fuente lo escribe "
              "-- indicador con aviso --; el umbral duro, que lo endurece "
              "como el proyecto endurece las recomendaciones de V1 y de V2, "
              "queda en la ventana.",
     "aplicacion": "De los DOS indicadores que el numeral nombra se evalua "
                   "UNO -- pendiente del barril frente a la del cauce --, "
                   "porque el otro exige el n de Manning del CAUCE NATURAL, "
                   "que no es columna de Sec. 1.2. Con que regimen se aplica "
                   "el indicador evaluable lo fija el criterio 'regimen_v2b' "
                   "[A]: como indicador con aviso (valor del archivo desde "
                   "T-2), que se imprime con veredicto INDICADOR y no "
                   "descarta el diametro, o como umbral DURO que detiene el "
                   "punto; la comparacion es la misma en los dos. La otra "
                   "mitad de la "
                   "fila V2b de la hoja de ruta -- el acceso de "
                   "mantenimiento, contenido de planos -- no es un numero: "
                   "su EXIGENCIA es el num. 4.1.1.3.7 d) del Manual, y el "
                   "dispositivo entra por el criterio "
                   "'acceso_mantenimiento_v2b', que se "
                   "declara y se imprime, y sin el la verificacion se "
                   "detiene."},
    {"codigo": "V3",
     "fundamento": "F5.V3",
     "que": "Velocidad maxima admisible del revestimiento",
     "citas": ("MC_HHD.4.1.1.3.6#T10",),
     "literales_de_tabla": (("MC_HHD.T10", "previo"),),
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
    {"codigo": "V4",
     "fundamento": "F5.V4",
     "que": "Carga a la entrada bajo la subrasante: cota_entrada + HW <= "
            "cota_subrasante - resguardo(CBR)",
     "citas": ("MS.4.5.4", "MS.9.1.3"),
     "literales_de_tabla": (),
     "matiz": "El numeral regula el nivel de la NAPA FREATICA bajo la "
              "subrasante, no el de una avenida. Aplicarlo al HW es una "
              "ANALOGIA declarada del proyecto -- por eso el criterio "
              "'resguardo_HW_subrasante' es [N->] y no [N] --: la exigencia "
              "sobre el numero es de la fuente, la extension del numero a "
              "otro fenomeno es del proyectista.",
     "aplicacion": "Se aplica el resguardo por CBR de la tabla del num. 4.5.4 "
                   "a un nivel transitorio (la carga de la avenida de "
                   "diseño), que es mas exigente que aplicarlo solo a la napa "
                   "permanente. La regla con que se obtiene la cota de fondo "
                   "de entrada NO la elige el codigo: sale del criterio "
                   "'origen_cota_fondo_entrada', que aparece en el bloque de "
                   "criterios de esta memoria."},
    {"codigo": "VC1",
     "fundamento": "F5.VC1",
     "que": "Cruce de canal -- borde libre del canal: cota_entrada + HW <= "
            "cota_coronacion_canal - borde_libre_canal",
     "citas": ("MC_HHD.4.1.1.4.1e", "MC_HHD.4.1.1.4.1e#RANGO"),
     "literales_de_tabla": (),
     "matiz": "LOS DOS SALTOS QUE HAY QUE VER ANTES DE LEER EL NUMERO. "
              "(1) El requisito -- «no puede alterar la rasante hidraulica ni "
              "el borde libre del canal» -- lo fija la Sec. 2.3 de la hoja de "
              "ruta, NO un numeral del MTC: el Manual no fija borde libre "
              "para un canal, y eso esta verificado por ausencia sobre sus "
              "225 paginas (`citas.SIN_BORDE_LIBRE_DE_CANAL`). (2) El par "
              "0.30-0.50 m sale del num. 4.1.1.4.1 e), cuyo objeto es un "
              "BADEN y cuyo datum superior es la superficie de rodadura; "
              "traerlo a la coronacion de un canal es una ANALOGIA del "
              "proyectista, y elegir el 0.50 dentro de la banda es una "
              "SEGUNDA decision suya, porque la fuente no da regla para "
              "elegir. Por eso 'borde_libre_canal_m' es [A] y no [N->]: un "
              "[N->] seria un valor que la fuente determina una vez concedida "
              "la analogia, y aqui no lo determina.",
     "aplicacion": "Se aplica como umbral DURO. El borde libre se RESTA de la "
                   "coronacion, de modo que adoptar el extremo SUPERIOR de la "
                   "banda (0.50 m) baja la cota admisible y endurece la "
                   "verificacion: es el lado conservador, al reves que en la "
                   "adopcion del riesgo de la Tabla Nº 02. VC1 cierra la "
                   "mitad de la Sec. 2.3 que habla del BORDE LIBRE; la mitad "
                   "que habla de la RASANTE HIDRAULICA no la cierra -- acota "
                   "el nivel alcanzado, no mide en cuanto la obra levanta el "
                   "pelo de agua del canal --, y esa distincion la imprime la "
                   "memoria en el bloque de alcance."},
    {"codigo": "V7",
     "fundamento": "F5.V7",
     "que": "Flotacion del conducto vacio: gamma_DC_min*DC + gamma_EV_min*EV "
            ">= gamma_WA*U",
     "citas": ("MP.T2.4.5.3.1-1", "MP.T2.4.5.3.1-2"),
     "literales_de_tabla": (),
     "matiz": "La fila V7 de la hoja de ruta lo enuncia como SUMA_W >= FS*U, "
              "que es lenguaje de tension admisible. El proyecto no lo aplica "
              "asi: la Sec. 0.2 adopta LRFD de extremo a extremo y en LRFD el "
              "margen lo hacen los propios gamma. Conservar ademas un FS "
              "global seria contar dos veces el mismo margen.",
     "aplicacion": "Se minoran las acciones que estabilizan (DC y EV, con sus "
                   "gamma MINIMOS) y se mayora la que desestabiliza (WA). La "
                   "FILA de gamma_p se elige por tipo de estructura y esa "
                   "eleccion es del proyectista ('factores_carga_aashto'): la "
                   "tabla es normativa, la fila que describe a esta obra no "
                   "lo es. El peso propio del conducto se omite (DC = 0), que "
                   "reduce el lado estabilizante y es del lado conservador."},
    {"codigo": "TR",
     "fundamento": "F2.TR",
     "que": "Riesgo admisible y vida util con que se calcula el periodo de "
            "retorno (Tabla Nº 02)",
     "citas": ("MC_HHD.3.6",),
     "literales_de_tabla": (("MC_HHD.T02", "titulo"),),
     "notas_de_tabla": (("MC_HHD.T02", "El Propietario de una Obra"),),
     "matiz": "El titulo dice «MAXIMOS RECOMENDADOS» y la nota al pie asigna "
              "la decision al Propietario: la tabla no impone el riesgo, "
              "acota lo que recomienda como techo.",
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
     "fundamento": "F3.D_MIN",
     "que": "Seccion minima circular de 0.90 m",
     "citas": ("MC_HHD.4.1.1.3.4a",),
     "literales_de_tabla": (),
     "matiz": "«Se adoptara» es exigencia, pero la oracion la CONDICIONA dos "
              "veces: solo en carreteras de alto volumen de transito, y "
              "exceptuando los cruces de canales de riego.",
     "aplicacion": DIAMETRO_MIN_AMBITO},
    {"codigo": "h_o",
     "fundamento": "F4.HO",
     "que": "Linea de energia a la salida del conducto: "
            "h_o = max(TW, (y_c + D)/2), Sec. 4.3",
     # TRES citas, que son las tres condiciones de uso. La segunda -- «It
     # should not be used if the inlet is not submerged» -- vivia dentro de la
     # `nota` de la primera y por eso no se podia imprimir aparte; la tercera
     # se transcribia a mano CON UNA ELISION SIN MARCAR (se saltaba la oracion
     # sobre las backwater calculations) bajo el rotulo "texto literal".
     "citas": ("HDS5_3ED.3.3.3#HO", "HDS5_3ED.3.3.3#HO_SUMERGIDA",
               "HDS5_3ED.3.3.3#HO_1_2D"),
     "literales_de_tabla": (),
     "matiz": "Las tres son «can only» / «should», no «shall»: la fuente "
              "acota su propia aproximacion, no prohibe un diseño.",
     "transcripcion": ("La forma con el MAXIMO, que es la que el proyecto "
                       "implementa, la 3a ed. no la numera: la escribe en "
                       "prosa ('the greater of tailwater or (dc + D)/2', "
                       "misma pag. 3.24). Impresa como igualdad esta en la "
                       "edicion de 1985 que tambien vive en normas/, dentro "
                       "de su procedimiento paso a paso (PDF 67): <<"
                       + H_O_FORMA_MAXIMO_TEXTO + ">> Esta linea no es cita "
                       "de la 3a ed., y NO PUEDE INTERNARSE COMO CITA de la "
                       "de 1985: la paginacion de esa copia electronica es "
                       "`SinDeterminar` y el invariante T6 del registro "
                       "prohibe que una cita suya declare pagina PDF "
                       "firmada. Por eso va aqui, rotulada como "
                       "transcripcion, y no arriba."),
     "aplicacion": H_O_CONDICION_APLICACION},
    # --- T-2 --- (cadena T, 2026-11-11; INF-3.2.7) --------------------------
    {"codigo": "V10",
     "fundamento": "F5.V10",
     "que": "Pendiente del conducto dentro de la banda adoptada: "
            "S_min <= S_conducto <= S_max",
     "citas": ("MC_HHD.4.1.1.3.3", "HDS5_3ED.3.3.4#HORIZONTAL",
               "HDS5_3ED.5.4.4#PENDIENTE_10"),
     "literales_de_tabla": (),
     "matiz": "NINGUNA de las tres fija la banda. El Manual EXIGE que la "
              "pendiente no altere desmesuradamente la erosion y la "
              "sedimentacion, sin cifra; el HDS-5 PERMITE el barril "
              "horizontal y DESCRIBE que bajo el 10 % no se usan medidas "
              "estructurales especiales. Los dos numeros son adopcion del "
              "proyectista.",
     "aplicacion": "Se aplica como umbral DURO sobre la pendiente con que "
                   "corrio el diseño. Los extremos viven en los criterios "
                   "[A] 'pendiente_minima_conducto' (0.0: el barril "
                   "horizontal que la fuente admite; ventana hasta 0.005) y "
                   "'pendiente_maxima_conducto' (0.10; ventana desde 0.02, "
                   "la pendiente de las curvas del HDS-5). No depende del "
                   "diametro: incumplirla se resuelve con otra pendiente, no "
                   "con otro tubo. La pendiente del cauce que traspasa la "
                   "banda la sustituye el extremo antes del diseño (paso "
                   "7.B.1), de modo que solo la incumple una pendiente "
                   "declarada. No sustituye a V2, V2b ni V3, que juzgan "
                   "el efecto de la pendiente."},
)


def fundamento_del_umbral(umbral: dict):
    """
    El `Fundamento` de un umbral: POR QUE se hace ese paso.

    Es el mismo objeto que consume `PasoDeMemoria.por_que`, y por eso el
    bloque fijo de umbrales y el desarrollo de un punto no pueden decir cosas
    distintas del mismo umbral. Hace falta ademas porque hay umbrales que
    NINGUN paso emite: el minimo de 0.90 m no se verifica sobre un resultado,
    es el PISO de la serie de diametros candidatos, y su «por que» --- que por
    debajo de 0.90 m no entra una persona a limpiar el conducto --- solo tiene
    este sitio donde llegar al revisor.
    """
    return _reg.fundamento(umbral["fundamento"])


def literales_del_umbral(umbral: dict) -> Tuple[Tuple[str, str], ...]:
    """
    Las transcripciones LITERALES que sostienen un umbral, leidas del
    registro, como pares (de donde sale, texto).

    POR QUE ESTO ES UNA FUNCION Y NO UN CAMPO. Hasta S18 cada entrada llevaba
    su `texto` escrito a mano aqui: una SEGUNDA transcripcion del mismo
    parrafo, de-acentuada -- o sea imposible de encontrar en el PDF con el
    buscador de un lector-- y libre de divergir de la del registro sin que
    nada avisara. Dos de las seis divergian ya: la del titulo de la Tabla Nº
    10 (espaciado distinto) y la de la tercera condicion de h_o, que se
    saltaba una oracion entera SIN MARCAR LA ELISION bajo un rotulo que decia
    "texto literal". Ahora hay un solo original y esta verificado contra su
    pagina.
    """
    salida = []
    for cita_id in umbral.get("citas", ()):
        c = _reg.cita(cita_id)
        salida.append((c.como_texto(), _literal_de_cita(cita_id)))
    for tabla_id, campo in umbral.get("literales_de_tabla", ()):
        t = _reg.tabla(tabla_id)
        rotulo = ("titulo de la tabla" if campo == "titulo"
                  else "parrafo que introduce la tabla")
        salida.append((f"{tabla_id} ({rotulo})",
                       _literal_de_tabla(tabla_id, campo)))
    for tabla_id, prefijo in umbral.get("notas_de_tabla", ()):
        salida.append((f"{tabla_id} (nota al pie)",
                       _nota_de_tabla(tabla_id, prefijo)))
    return tuple(salida)


def caracter_del_umbral(umbral: dict) -> str:
    """
    El CARACTER que la fuente le da, leido de sus citas y no escrito a mano.

    Se compone de los `Caracter` de las citas que lo sostienen -- que es donde
    el registro los tiene verificados -- en vez de una cadena redactada aqui.
    Una cadena redactada es como se escribio "EXIGENCIA" encima de un parrafo
    que recomienda, que es NOR-MEM-01 leido al reves.

    El `matiz` NO entra aqui: se imprime aparte, porque es lectura del
    proyecto sobre la fuente y no el dato del registro.
    """
    vistos = []
    for cita_id in umbral.get("citas", ()):
        v = _reg.cita(cita_id).caracter.value.upper()
        if v not in vistos:
            vistos.append(v)
    for tabla_id, _campo in umbral.get("literales_de_tabla", ()):
        v = _reg.cita(_reg.tabla(tabla_id).cita_id).caracter.value.upper()
        if v not in vistos:
            vistos.append(v)
    return " + ".join(vistos) if vistos else "SIN CITA"


def numeral_del_umbral(umbral: dict) -> str:
    """El numeral y la pagina, compuestos por la `Cita`, no reescritos aqui."""
    partes = [_reg.cita(c).como_texto() for c in umbral.get("citas", ())]
    for tabla_id, _campo in umbral.get("literales_de_tabla", ()):
        cita = _reg.cita(_reg.tabla(tabla_id).cita_id).como_texto()
        if cita not in partes:
            partes.append(cita)
    return " | ".join(partes)


UMBRALES_POR_CODIGO = {u["codigo"]: u for u in UMBRALES_DE_VERIFICACION}


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
#   ASTM A760/A760M-10, Tabla 1 "Tamaños de tuberia", pag. impresa 3: la serie
#   va de 100 mm (4 in) a 3600 mm (144 in), fila a fila. Los 2100 mm son la
#   fila de 84 in, una mas de la serie, no un maximo. VERIFICADO POR IMAGEN:
#   el PDF de esta norma no entrega texto utilizable.
#   AASHTO M 170M-04, Tablas 1 a 5 (Clases I a V). LA REDACCION ANTERIOR
#   -- "Tablas 1 a 5 (Clases I a V): de 300 a 3600 mm" -- era falsa leida
#   distributivamente, y al verificarla por imagen se vio por que: la Tabla 1
#   (Clase I) va de 1500 a 3450 mm y la Tabla 2 (Clase II) tampoco llega a
#   3600. Lo cierto es la ENVOLVENTE: el conjunto de las cinco cubre de
#   300 mm (Tablas 2 a 5) a 3600 mm (Tablas 3 y 5). La Seccion 7.2
#   "Modified and Special Designs" preve ademas diseños por encima de lo
#   tabulado, con permiso del propietario. El fondo -- que 2.70 m no es un
#   tope de M 170M -- se sostiene igual; lo que se corrige es la forma de la
#   cita, que atribuia a cada tabla un rango que dos de ellas no tienen.
#   AASHTO M 294-11 esta en normas/ desde N2 como TRADUCCION NO OFICIAL: su
#   serie de tamaños nominales (num. 1.1.1 y 7.2.1) TERMINA en 1500 mm, de
#   modo que el tope del HDPE es el unico de los tres que coincide con el
#   techo de su norma de producto -- segun la traduccion, sin firma; el
#   original en ingles sigue ausente --. No devuelve el tope a este archivo:
#   la eleccion sigue siendo de catalogo para los tres materiales.
#
#   Y UNA COSA MAS QUE LA VERIFICACION POR IMAGEN DESTAPO: el PDF de ASTM
#   A760 que hay en normas/ NO es el original en ingles, es una TRADUCCION AL
#   ESPAÑOL, y ademas de doble designacion -- su portada rotula "AASHTO No.
#   M 36 / M 36M" --, de modo que ese PDF y el de AASHTO M 36 son la MISMA
#   norma en dos ediciones distintas y no dos normas independientes. Citar
#   una traduccion como si fuera el original es una cita imprecisa aunque el
#   dato sea correcto; queda declarado en `normativa/fuentes.py`.
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
# LA DISCREPANCIA CON LA HOJA DE RUTA QUEDO RESUELTA EN I2: su Anexo B
# declaraba estos mismos topes bajo el rotulo "topes por norma de producto -
# VERIFICAR" -- era el comentario de la asignacion `D_MAX = {` -- y con las
# mismas atribuciones. Gano la fuente primaria -- las tablas de A760 y
# M 170M, leidas de los PDF -- y la v8 escribe hoy la verdad verificada en
# §3.2, §3.4, Tablero 1.2 y Anexos A/B/C (DIS-HR-D-MAX, en el manifiesto).
#
# LA REFERENCIA SE DA POR SIMBOLO Y TEXTO, NO POR LINEA (NOR-COH-03). Este
# comentario decia "linea 806 de docs/hoja_de_ruta_alcantarillas_v8.md" y esa
# linea es hoy la de la longitud maxima de cuneta: el documento se movio y la
# cita quedo apuntando a otra cosa. Es la regla 4 de CLAUDE.md -- anclar por
# nombre de simbolo, nunca por numero de linea -- aplicada a una cita interna.

# ================= Manual de Suelos (RD 10-2014-MTC/14) ====================
# ---------------------------------------------------------------------------
# Distancia minima de la subrasante a la napa freatica
# ---------------------------------------------------------------------------
# EL NOMBRE DE ESTA CONSTANTE ES VOCABULARIO DEL PROYECTO, NO DEL MANUAL
# (NOR-SUE-05). "Resguardo" aparece UNA vez en las 281 paginas del Manual de
# Suelos -- pag. impresa 56, "deben mantenerse al resguardo de la luz" --, y
# es sobre conservacion de muestras. El Manual llama a esta magnitud
# "el nivel superior de la sub rasante debe quedar encima del nivel de la napa
# freatica como minimo a X m". El nombre se conserva porque esta cableado en
# M5 y en la memoria, y la equivalencia se declara aqui en vez de dejar que
# alguien busque "resguardo" en el PDF y no lo encuentre.
#
# Y NO ES UNA TABLA: el num. 4.5.4 lo escribe en PROSA CORRIDA, en una sola
# oracion con sus cuatro escalones. El numeral arranca en la pag. impresa 41 y
# el parrafo esta en la 42.
#
# LA FUENTE OFRECE REMEDIO, y tratarlo como umbral duro de rechazo la
# endurece: la ultima oracion del mismo parrafo dice "En caso necesario, se
# colocaran subdrenes o capas anticontaminantes y/o drenantes o se elevara la
# rasante hasta el nivel necesario". No es un rechazo binario.
RESGUARDO_NAPA_SUBRASANTE = [       # (CBR_min, CBR_max, resguardo_m)
    (20.0, None, 0.60), (6.0, 20.0, 0.80),
    (3.0, 6.0, 1.00),   (None, 3.0, 1.20),
]
NUMERAL_RESGUARDO_NAPA = _reg.cita("MS.4.5.4").como_texto()
NUMERAL_RESGUARDO_NAPA_SEGUNDA = _reg.cita("MS.9.1.3").como_texto()
NUMERAL_CATEGORIAS_SUBRASANTE = _reg.cita("MS.4.4#C411").como_texto()
RESGUARDO_PALABRA_DEL_PROYECTO = (
    "«Resguardo» es vocabulario de este proyecto. El Manual de Suelos no usa "
    "esa palabra para esta magnitud -- aparece una sola vez en sus 281 "
    "paginas, en la impresa 56 y sobre conservacion de muestras --: la llama "
    "«el nivel superior de la sub rasante debe quedar encima del nivel de la "
    "napa freatica como minimo a X m»")
RESGUARDO_REMEDIOS_ALTERNATIVOS = (
    "En caso necesario, se colocarán subdrenes o capas anticontaminantes y/o "
    "drenantes o se elevará la rasante hasta el nivel necesario")
# ERRATA DE LA PROPIA FUENTE, hallada al verificar: el num. 4.5.4 remite «al
# cuadro 4.10» para la categoria de sub rasante, y el Cuadro 4.10 (pag.
# impresa 36) es «Clasificacion de los suelos basada en AASHTO M 145 y/o ASTM
# D 3282». La tabla de categorias es el Cuadro 4.11 (pag. impresa 37).
CATEGORIAS_SUBRASANTE_ERRATA_REMISION = (
    "El num. 4.5.4 remite al «cuadro 4.10» y la tabla de categorias de sub "
    "rasante es el Cuadro 4.11; el 4.10 es la clasificacion de suelos "
    "AASHTO M 145 / ASTM D 3282. Errata de remision del propio Manual")
# Su aplicacion al HW es POR ANALOGIA [N->] -> ver criterios_adoptados
CBR_MIN_SUBRASANTE = 6.0            # %
# ---------------------------------------------------------------------------
# Compactacion -- UN numeral la sostiene, no cuatro (NOR-SUE-03)
# ---------------------------------------------------------------------------
# Los dos valores se citaban a "num. 3.2.1, 3.2.2, 3.3 y 9.1(1)", los cuatro a
# la vez. Verificado contra el PDF, uno por uno:
#
#   3.2.1 "Terraplen" (pag. impresa 24)  SOSTIENE LOS DOS. Es el unico:
#       "La base y cuerpo del terraplen o relleno sera conformado en capas de
#        hasta 0.30m y compactadas al 90% ... La corona ... tendra un espesor
#        minimo de 0.30m y sera conformada en capas de 0.15m, compactadas al
#        95%".
#   3.2.2 "Corte" (pag. impresa 24)  trae UN 95 %, pero es el del FONDO DE
#       EXCAVACION escarificado 0.15 m, otro elemento. No contiene el 90 %.
#   3.3 "Sub rasante del camino" (pag. impresa 24)  trae otro 95 %, el de los
#       ultimos 0.30 m bajo la subrasante. Tampoco contiene el 90 %.
#   9.1 apartado 1) (pag. impresa 89)  NO CONTIENE NINGUN PORCENTAJE DE
#       COMPACTACION. Va de CBR >= 6 % y de alternativas de estabilizacion:
#       es el numeral que sostiene CBR_MIN_SUBRASANTE, no estos dos.
#
# Citar los cuatro para los dos valores hacia pasar por respaldo lo que no lo
# era, y ademas repartia la responsabilidad de modo que ningun numeral quedaba
# como EL que hay que abrir. Se cita el que los sostiene y se dice que
# sostienen los otros.
COMPACTACION_CORONA = 0.95          # 0.30 m superiores, capas de 0.15 m
COMPACTACION_CUERPO = 0.90          # capas de hasta 0.30 m
NUMERAL_COMPACTACION = _reg.cita("MS.3.2.1").como_texto()
NUMERAL_COMPACTACION_CORTE = _reg.cita("MS.3.2.2").como_texto()
NUMERAL_COMPACTACION_SUBRASANTE = _reg.cita("MS.3.3").como_texto()
NUMERAL_ESTABILIZACION_CBR = _reg.cita("MS.9.1.1").como_texto()
COMPACTACION_ALCANCE_DE_CADA_NUMERAL = (
    "3.2.1 «Terraplen» sostiene LOS DOS valores (90 % base y cuerpo, 95 % "
    "corona). 3.2.2 «Corte» y 3.3 «Sub rasante del camino» traen cada uno un "
    "95 % de OTRO elemento -- el fondo de excavacion escarificado y los "
    "ultimos 0.30 m bajo la subrasante -- y ninguno contiene el 90 %. "
    "9.1(1) no contiene ningun porcentaje de compactacion: va de CBR >= 6 %")

# ---------------------------------------------------------------------------
# Cuadro 4.1 -- numero de calicatas (num. 4.2, pag. impresa 28, PDF 29)
# ---------------------------------------------------------------------------
# EL COMENTARIO QUE VIVIA AQUI AFIRMABA DOS COSAS, Y LAS DOS ERAN FALSAS
# (NOR-SUE-01, MAT-D11). Decia:
#
#     "El Cuadro admite ademas 6 en vez de 4 para autopistas con 4 carriles
#      por sentido, y '4 (o 6)' para duales. Ese 6 NO se transcribe aqui: el
#      Cuadro lo da como alternativa SIN DECIR CUANDO APLICA CADA UNA, de modo
#      que la eleccion entre 4 y 6 no es [N]."
#
# Verificado contra el PDF: (a) el Cuadro SI dice cuando aplica cada una --
# lo condiciona por CARRILES POR SENTIDO, con tres viñetas explicitas en cada
# una de las dos filas multicarril: 2 carriles/sentido -> 4, 3 -> 4, 4 -> 6 --;
# y (b) la cadena "4 (o 6)" NO EXISTE en ninguna celda del Cuadro ni en el
# texto del numeral: la fila de Duales dice exactamente lo mismo que la de
# Autopistas.
#
# POR QUE ESTE DEFECTO ES DE LA MISMA FAMILIA QUE UNA CITA FALSA, aunque
# parezca lo contrario. Afirmar que la fuente CALLA donde HABLA es la forma
# inversa del defecto que este cluster persigue: en vez de citar lo que la
# norma no dice, se niega lo que si dice. El resultado es igual de invisible
# -- un vacio inventado que convierte en [A] lo que es [N] -- y ademas mueve
# un numero: una autopista de 4 carriles por sentido salia con la mitad de las
# calicatas que el Cuadro exige.
#
# COMO QUEDA. La celda de las dos filas multicarril no es un escalar: es una
# tabla de tres entradas por carriles por sentido, y asi esta transcrita en el
# registro. La vista de calculo de abajo conserva la forma antigua para las
# cuatro clases de una calzada -- donde el Cuadro SI da un escalar -- y para
# las dos multicarril devuelve el centinela que obliga a pasar por
# `calicatas_por_km`, que exige el dato.
_C41 = _reg.tabla("MS.C41")
CALICATAS_POR_KM = {
    _C41.clave_corta(f): f.valores["calicatas_por_km"] for f in _C41.filas}
CALICATAS_POR_SENTIDO = {
    _C41.clave_corta(f): f.valores["por_sentido"] for f in _C41.filas}
# El Cuadro fija tambien la PROFUNDIDAD, en columna propia y con su datum
# ("1.50 m respecto al nivel de sub rasante del proyecto", no respecto al
# terreno natural). El repositorio no la recogia (NOR-SUE-04).
CALICATAS_PROFUNDIDAD_M = {
    _C41.clave_corta(f): f.valores["profundidad_m"] for f in _C41.filas}
# La celda de las multicarril, abierta por carriles por sentido. Es [N]: lo
# escribe el Cuadro. Lo que NO es [N] es cuantos carriles tiene esta via, y
# por eso el dato de sitio bloquea.
CALICATAS_POR_CARRILES_POR_SENTIDO = {
    _C41.clave_corta(f): {
        2: f.valores["calicatas_2_carriles_por_sentido"],
        3: f.valores["calicatas_3_carriles_por_sentido"],
        4: f.valores["calicatas_4_carriles_por_sentido"],
    }
    for f in _C41.filas
    if "calicatas_2_carriles_por_sentido" in f.valores
}
# El centinela que la vista devuelve para las filas multicarril: la fuente NO
# da un escalar ahi, y devolver 4 seria escribir un numero que el Cuadro no
# pone en esa celda.
CALICATAS_REMITE_A_CARRILES = _C41.fila("autopista").valores["calicatas_por_km"]

# El 4.0 km NO ESTA EN EL CUADRO 4.1 y NO ES INCONDICIONAL (NOR-SUE-02). Las
# dos cosas las decia el comentario anterior y las dos son falsas:
#
#   (a) UBICACION. El Cuadro no contiene ninguna celda con 4.0 km ni con
#       2.0 km: solo dice "x km". El 4.0 vive en un parrafo del num. 4.2, en
#       la pag. impresa 29 (PDF 30).
#   (b) CONDICION. La fuente lo condiciona DOS veces: solo para estudios a
#       nivel de PERFIL, y solo "de no existir informacion secundaria" -- el
#       orden de prelacion impreso es usar PRIMERO la informacion secundaria
#       existente en el tramo. Presentarlo como un espaciamiento fijo de nivel
#       perfil borra el primer termino de esa prelacion.
#
# Y el mismo parrafo trae un tercer escalon que el repositorio no recogia:
# 2.0 km para factibilidad y prefactibilidad, ese si incondicional.
ESPACIAMIENTO_PERFIL_KM = 4.0       # num. 4.2, parrafo posterior al Cuadro 4.1
ESPACIAMIENTO_FACTIBILIDAD_KM = 2.0  # mismo parrafo, sin condicion adicional

# ================= DG-2018, Seccion 304.07: derecho de via (EXT-6) =========
# EL PISO [N] DEL REQUISITO JURIDICO DE V5, y nada mas que el piso. La v8
# (fila V5, enmendada en EXT-0) parte V5 en tres: el requisito juridico es
# [N] --- el derecho de via es bien de dominio publico y su ancho minimo lo
# fija la Tabla 304.09 por clase de carretera, incrementado en 5.00 m en el
# caso «del borde mas alejado de las obras de drenaje» (como se compone ese
# incremento con el ancho de la fila es interpretacion registrada en la cita
# DG2018.304.07.02#INCREMENTO, no texto de la norma) ---, el metodo hidraulico con que se
# decide si el embalse cabe en esa faja es [A] ('remanso_derecho_via') y el
# ancho de ESTE corredor es un dato de sitio [S] ('ancho_derecho_via_m') que
# hoy no llega por ninguna via. Aqui vive la parte [N], derivada de la tabla
# transcrita (D2: la vista se deriva, no se copia). SIN CONSUMIDOR HOY, y
# esta en CONSTANTES_DE_REFERENCIA por eso: V5 se detiene antes, en el dato
# de sitio, y elegir fila exige 'clase_de_via', que el estudio de demanda
# no ha cerrado. El 304.07 NO enuncia condicion hidraulica alguna: lo que
# esta aqui acota el ANCHO, no el agua (EXT-N-04).
_T304_09 = _reg.tabla("DG2018.T304.09")
ANCHO_MIN_DERECHO_VIA_M = {
    _T304_09.clave_corta(f): f.valores["ancho_min"].minimo for f in _T304_09.filas
}
INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M = 5.0    # m, 304.07.02, pag. impresa 199 (PDF 200)
NUMERAL_DERECHO_VIA_DG2018 = {
    "definicion": _reg.cita("DG2018.304.07.01").como_texto(),
    "ancho_minimo": _reg.cita("DG2018.304.07.02").como_texto(),
    "incremento_obras_drenaje": _reg.cita("DG2018.304.07.02#INCREMENTO").como_texto(),
    "caso_obras_drenaje": _reg.cita("DG2018.304.07.02#INCREMENTO_DRENAJE").como_texto(),
}

# ================= EG-2013, Capitulo V (Secciones 502-508) =================
# EL ALCANCE DE CADA NORMA DE PRODUCTO, leido de su propia clausula 1.1 (EXT-6,
# EXT-N-03). Hasta EXT-6 las tres normas de producto tenian UNA sola cita cada
# una, y de tablas: el registro no podia decir que cubre cada norma, y por
# eso `M2._NORMA_PRODUCTO` pudo rotular un marco rectangular con la norma de
# un tubo sin que nada lo acusara. Los cuatro textos salen del registro
# (`como_texto`), no se escriben aqui; la clave «marco» no es una norma de
# producto sino la constancia de que no la hay: AASHTO LRFD 12.4.2.4 nombra
# M 259 y M 273 para el cajon PREFABRICADO, ausentes, y el proyecto decidio el
# marco vaciado in situ (docs/ruta_familia_c.md §14.1), que se diseña por
# 12.11 y la Seccion 5 y se construye por EG-2013 503 y 504. M2 lo imprime y
# `cli._diseno_json` lo exporta como `alcance_norma_producto`.
def _alcance(cita_id: str) -> str:
    """«<edicion de la fuente>: <cita en una linea>», para que el lector sepa
    de que norma es cada clausula sin abrir el registro."""
    c = _reg.cita(cita_id)
    return f"{_reg.fuente(c.fuente_id).edicion}: {c.como_texto()}"


ALCANCE_NORMA_PRODUCTO = {           # claves: TipoMaterial.value, y «marco»
    "concreto_reforzado": (_alcance("AASHTO_M170M.1.1") + " · "
                           + _alcance("AASHTO_M170M.1.1#NOTA1")),
    "tmc": _alcance("AASHTO_M36.1.1") + " · " + _alcance("ASTM_A760.1.1"),
    "hdpe": _alcance("AASHTO_M294_TRAD.1.1.1")
            + " (traduccion no oficial, sin folio)",
    "marco": ("sin norma de producto: " + _alcance("AASHTO_LRFD_9.12.4.2.4")
              + " nombra M 259 y M 273 para el cajon prefabricado, ausentes; "
              + _alcance("AASHTO_LRFD_9.12.11.1")
              + " rige el diseño del marco vaciado in situ"),
}
H_RELLENO_MIN = {
    "hdpe":     0.30,               # m, clave a subrasante (508.07, pag. 984)
    "concreto": None,               # EG-2013 no lo fija -- ver comentario
    "tmc":      None,               # EG-2013 no lo fija -- idem; ver abajo
}
# CABO PARA LA SESION QUE RELLENE LA FILA DEL TMC (anotado en N1): ASTM
# A796/A796M-13, en el registro desde N1, fija en su num. 11.1 dos pisos que
# dependen del ESPESOR y no de la altura -- Hmin nunca menor de 300 mm, y no
# menor de 600 mm si el espesor especificado es menor de 1.32 mm (cita
# ASTM_A796.11.1#PISOS) --, y las Tablas 3 y 5 transcritas incluyen la fila
# de 1.02 mm. El escalon de 600 mm NO esta en la Tabla 12.6.6.3-1 de AASHTO
# LRFD, que es la que hoy gobierna la cobertura minima (12.6.6.3). Quien
# rellene esta fila tiene que decidir como conviven los dos pisos, y no
# rellenarla en silencio con uno solo.
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
# LA PAGINA: impresa 984 (PDF 992), verificada leyendo el PDF en S12 sobre la
# cabecera de la propia pagina. Este comentario llego a decir 982, y la
# impresa 982 (PDF 990) trae 508.02 b), c) y d) -- calidad del tubo, muestreo
# y material para cama de asiento --, nada de altura de relleno. El desfase de
# este documento es +8, el mayor del corpus, y confundir pagina impresa con
# pagina PDF produce exactamente un error de 8: la distancia entre las dos
# cifras que el repositorio manejaba (NOR-EG-01, NOR-EG-02).
#
# Y NO CONFUNDIRLA CON SU VECINA: la subseccion 508.08 "Proteccion de la
# estructura durante la construccion" (pag. impresa 985) tambien dice 0,30 m,
# pero con otro sentido -- "el equipo y vehiculos pesados no deberan circular
# sobre la estructura antes que la altura de relleno minima sobre la misma sea
# de 0,30 m" --, que es la NOTA CONSTRUCTIVA de mas abajo y no la altura
# minima de diseño. Dos frases con el mismo numero en paginas contiguas: si se
# citan como una sola, el expediente pierde una de las dos exigencias.
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
# LAS DISCREPANCIAS CON LA HOJA DE RUTA: dos, y desde N1 las dos RESUELTAS
# (hasta N1 solo una tenia fuente contra la que verificarse):
#
#   TABLA DE SEC. 7.A, fila "Concreto y TMC" -- decia "No fijado. Remite al
#     Proyecto, AASHTO M-170M (clases I-V) o ASTM A-807 | [C] norma de
#     producto". Las dos remisiones eran falsas: M 170M no da alturas de
#     relleno y A-807 no es la norma que se le atribuye (ver NOR-PRO-04). Y
#     "no fijado" no era cierto: lo fija AASHTO LRFD Art. 12.6.6.3, que el
#     propio Sec. 0.2 adopta. CORREGIDA EN I2, junto con el comentario de
#     `H_RELLENO_MIN["tmc"]` del Anexo B que repetia la remision:
#     DIS-HR-H-RELLENO-MIN quedo RESUELTA y vive en el manifiesto.
#   TABLA DE FASE 8, fila "TMC" -- decia "ASTM A-807 / AASHTO M36 -- calibre
#     segun altura". CORREGIDA EN N1, con ASTM A796/A796M-13 en normas/ y
#     leida por imagen: A807/A807M es practica de INSTALACION (A796 num.
#     22.1), el calibre lo determina A796 por PROCEDIMIENTO (num. 7 a 10,
#     con sus Tablas 2 a 35) y no por una tabla de calibre por altura, que
#     la norma no tiene, y la mitad "AASHTO M36" de la fila era correcta
#     como norma de producto (A796 num. 17.1 remite a A760/A760M = M 36).
#     DIS-HR-A807 quedo RESUELTA y vive en el manifiesto; el criterio
#     'clases_producto_por_relleno' ya no la declara (una resuelta no viaja a
#     la memoria) y su justificacion cuenta lo que la fuente SI trae.
#
# SE CITAN POR TABLA Y FILA, NO POR LINEA (NOR-COH-03). Este bloque decia
# "linea 523", "linea 546" y "linea 832", y las tres estaban corridas y
# caian en separadores "---". Una cita interna que no se puede comprobar es
# indistinguible de una inventada, igual que una externa; la regla 4 de
# CLAUDE.md -- anclar por simbolo, nunca por linea -- vale tambien aqui.
#
# Aqui gano la fuente primaria por verificacion externa contra los PDF de
# normas/, como en K_FRICCION_SI. El defecto quedo reportado contra la hoja
# de ruta, no contra este archivo, y la parte verificable ya esta corregida.
# 505, 506, 507 y 508 son SECCIONES completas del EG-2013, dentro del
# Capitulo V. No son subsecciones de ninguna "Seccion 500": esa denominacion
# no existe en el EG-2013 y la constante se llamaba SUBSECCION por arrastre de
# ese error. Las SUBsecciones son las de dentro de cada una (505.03, 508.07).
# LA REMISION DE SEGUNDO NIVEL de tres de las cuatro fichas de cama y relleno.
# El "95 % MDS" que el expediente les atribuia NO es literal de las Secciones
# 505, 506 ni 507: llega desde el num. 205.12 c) 1., por remision. El valor es
# correcto; lo que faltaba era decir por que via llega, que es la diferencia
# entre una cita y una deduccion (NOR-EG-03).
NUMERAL_COMPACTACION_REMITIDA = _reg.cita("EG2013.205.12c1").como_texto()
NUMERAL_COMPACTACION_EG2013_506 = (
    "506.07 remite a " + NUMERAL_COMPACTACION_REMITIDA)
NUMERAL_COMPACTACION_EG2013_507 = (
    "507.08 remite a " + NUMERAL_COMPACTACION_REMITIDA)

SECCION_EG2013 = {"concreto_simple": "505", "concreto_reforzado": "506",
                  "tmc": "507", "hdpe": "508"}
SECCION_CONCRETO_ESTRUCTURAL = "503"
SECCION_ACERO_REFUERZO = "504"
SECCION_CABEZALES = SECCION_CONCRETO_ESTRUCTURAL

# ---- La Seccion de un MARCO, que no es ninguna de las cuatro de arriba ----
# LAS CUATRO ENTRADAS DE `SECCION_EG2013` SON DE TUBERIA, verificado leyendo
# los cuatro titulos impresos: «Tuberia de concreto simple» (505, impresa
# 949), «Tuberia de concreto reforzado» (506, impresa 959), «Tuberia metalica
# corrugada» (507, impresa 969) y «Tuberia de polietileno de alta densidad»
# (508, impresa 981). El dict indexa por MATERIAL, de modo que hasta C7 un
# marco de concreto reforzado heredaba la 506 -- una Seccion cuyo 506.01
# alcanza «la instalacion de TUBOS», cuyo 506.02 pide el «diametro interno» y
# cuya partida 506.A se mide en METRO LINEAL --. Ninguna de las tres cosas le
# corresponde a un marco vaciado in situ. Era la forma exacta de NOR-PUE-01:
# numeral que existe, titulo que suena a lo buscado, contenido que es otro.
#
# DONDE SI CAE, y es hallazgo positivo y no un vacio: bajo la Seccion 503
# «Concreto estructural». Lo prueba el num. 503.10 h) (impresa 926), que le
# fija plazo de desencofrado a la «Placa superior en alcantarillas de cajon»;
# una norma que regula el desencofrado de la placa superior de un cajon esta
# regulando su vaciado in situ. Y el 503.01 declara su alcance sobre
# «estructuras de drenaje», con lista enunciativa.
#
# EL «+ 504» ES ENSAMBLAJE DEL PROYECTO Y SE DICE. La 503 se mide en m3 de
# concreto y la 504 en kg de acero; que un marco se pague por las dos no lo
# escribe ningun numeral. Lo autoriza la AUSENCIA verificada de partida propia
# (`SIN_PARTIDA_DE_CAJON_EG2013`: la Tabla Anexo 2-1 no lista ninguna partida
# de cajon, marco ni box) mas el mismo argumento que
# `M9.condicion_normativa_cabezal` ya hacia para los cabezales. Por eso el
# texto de abajo dice que el cajon «se construye bajo» la 503 -- que es lo que
# la fuente sostiene -- y separa el pago como lectura del proyecto.
SECCION_EG2013_CAJON = (SECCION_CONCRETO_ESTRUCTURAL + " + "
                        + SECCION_ACERO_REFUERZO)
NUMERAL_SECCION_CAJON_EG2013 = (
    "EG-2013 Seccion 503 'Concreto estructural' (num. 503.01, pag. impresa "
    "905) y Seccion 504 'Acero de refuerzo' (pag. impresa 939). Que el cajon "
    "de concreto se construye bajo la 503 lo dice el num. 503.10 h), pag. "
    "impresa 926: 'Placa superior en alcantarillas de cajon: 14 dias'. Que se "
    "PAGUE por 503 + 504 es lectura del proyecto y no literal de la norma: "
    "ningun numeral lo escribe, y lo que la sostiene es que no hay partida "
    "propia de cajon en la Tabla Anexo 2-1. La Seccion 506 NO aplica: su num. "
    "506.01 alcanza 'la instalacion de tubos de concreto reforzado'")

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
        # PAGINAS CORREGIDAS (NOR-EG-03): el rango declarado era 950-951 y
        # dejaba fuera las dos subsecciones que sostienen lo que la ficha
        # afirma. Reales, leidas del PDF: 505.03 "Material para solado y
        # sujecion" pag. impresa 950; 505.07 "Solado" 951; 505.10 "Sujecion"
        # 952-953 -- la que trae el "un cuarto del diametro exterior" --;
        # 505.11 "Relleno" 953.
        "numeral": "505.03/.07/.10/.11, pags. impresas 950-953",
        # EL 95 % NO ES LITERAL DE 505.11, y decirlo importa: esa subseccion
        # solo remite a la Seccion 502, sin porcentaje. El 95 % de la pagina
        # vecina es de 505.06 "Preparacion del terreno base" y se refiere al
        # TERRENO BASE, no al relleno lateral.
        "procedencia_de_los_porcentajes": ("por remision a la Sec. 502; el 95 % impreso "
                               "cerca es de 505.06 y es del terreno base"),
    },
    "concreto_reforzado": {
        "cama_apoyo": "Subbase granular (Sec. 402) >= 15 cm, >= 95% MDS",
        "sujecion_relleno_lateral": "Subbase hasta >= 1/6 del diametro "
                                    "exterior. Relleno Sec. 502",
        # PAGINAS CORREGIDAS (NOR-EG-03): declarado 959-960, real 959-961.
        # 506.10 "Sujecion" y 506.11 "Relleno" estan en la impresa 961.
        "numeral": "506.03/.07/.10/.11, pags. impresas 959-961",
        # El 95 % llega por REMISION DE SEGUNDO NIVEL: 506.07 exige "la que se
        # especifica para la corona en la Subseccion 205.12(c)(1)", y esa
        # subseccion (pag. impresa 193) es la que imprime Di > 0.95 De para la
        # corona y Di > 0.90 De para base y cuerpo.
        "procedencia_de_los_porcentajes": NUMERAL_COMPACTACION_EG2013_506,
    },
    "tmc": {
        "cama_apoyo": "Subbase granular >= 15 cm, >= 95% MDS, con arena "
                      "suelta de 12 mm",
        "sujecion_relleno_lateral": "Capas de 15-20 cm: >= 90% en base y "
                                    "cuerpo, >= 95% en corona",
        # PAGINA CORRIDA TRES (NOR-EG-03): declarada 970, real 973-974. La
        # impresa 970 trae la Tabla 507-01 "Espesores Minimos de Alcantarillas
        # Circulares y Abovedadas", que es otra cosa. Reales: 507.05
        # "Preparacion del terreno base" y 507.06 "Solado" en la 973; 507.07
        # "Ensamblado e Instalacion de la tuberia" 973-974; 507.08 "Relleno"
        # 974.
        "numeral": "507.05/.06/.07/.08, pags. impresas 973-974",
        # De la Seccion 507 son literales las capas de 15-20 cm y la arena
        # suelta de 12 mm. El par 90/95 llega por remision a 205.12(c)(1), y
        # los 15 cm de cama por doble remision 507.06 -> 506.07.
        "procedencia_de_los_porcentajes": NUMERAL_COMPACTACION_EG2013_507,
    },
    "hdpe": {
        "cama_apoyo": "Arena gruesa, capas de 15 cm, espesor 15-30 cm "
                      "(30 cm en roca o suelo blando)",
        "sujecion_relleno_lateral": "Capas alternadas y simetricas de "
                                    "15 cm a > 95%; los 30 cm superiores a "
                                    ">= 100%. Prohibida la anegacion",
        # PAGINAS CORREGIDAS (NOR-EG-03): declaradas 981-982, reales 982-985.
        # En la impresa 981 solo esta 508.01 "Descripcion". Reales: 508.02 d)
        # "Material para cama de asiento" en la 982; 508.05 "Preparacion de la
        # cama de asiento del tubo" en la 983; 508.07 "Colocacion del relleno
        # alrededor de la estructura" en la 984-985.
        "numeral": "508.02 d)/.05/.07, pags. impresas 982-985",
    },
}

# ================= Manual de Puentes (RD 041-2016-MTC/14) ==================
# ---------------------------------------------------------------------------
# SOBRECARGA DE TRAFICO EN EL TRASDOS -- h_eq
# ---------------------------------------------------------------------------
# ESTE BLOQUE ERA UNA SOLA LINEA:
#
#     SOBRECARGA_TRASDOS_H_EQ = 0.60   # m de relleno equivalente (2.1.4.3.9)
#
# y esa linea tenia DOS defectos, uno de cita y otro de valor (NOR-PUE-01,
# NOR-PUE-02, MAT-D5, MAT-O1, MAT-X1; conflicto vinculante #4 del plan).
#
# EL DEFECTO DE CITA. El num. 2.1.4.3.9 del Manual de Puentes se titula
# "Aparatos de Apoyo" (pag. impresa 91, PDF 92) y va de la conexion entre
# superestructura y subestructura: no contiene la palabra "sobrecarga", ni
# "trasdós", ni "relleno equivalente", ni el valor 0.60. El texto que SI
# sostiene la sobrecarga esta en el num. 2.4.2.2 "Cargas de Suelo: EH, ES, y
# DD" (pag. impresa 102, PDF 103). El numeral falso estaba propagado a seis
# puntos del repositorio, y esa propagacion es la mitad del daño: eran seis
# cadenas independientes y nada garantizaba que se corrigieran las seis. Hoy
# es UNA cita del registro, `MP.2.4.2.2#SOBRECARGA`, referenciada desde donde
# haga falta.
#
# EL DEFECTO DE VALOR, que es el que mueve un numero. El Manual escribe
# "una sobrecarga vertical NO MENOR QUE la equivalente a 0.60 m de altura de
# relleno": es un PISO, no un valor de diseño, y ademas condicionado a que
# haya trafico dentro de H/2. AASHTO LRFD -- que la Sec. 0.2 adopta de extremo
# a extremo -- TABULA el valor en su Art. 3.11.6.4, y para un cabezal de 2.0 m
# con trafico perpendicular la interpolacion obligatoria da 1.12 m, o sea
# 1.87 veces el 0.60 adoptado. Con gamma_LS = 1.75 eso llega al empuje de
# diseño. El 0.60 plano no es defendible.
#
# LO QUE LA VERIFICACION DE S12 AÑADIO AL CONFLICTO #4, y matiza su
# resolucion sin contradecirla:
#
#   1. EL MANUAL DE PUENTES NO TRANSCRIBE LAS TABLAS DE AASHTO. Su traduccion
#      de la Sec. 3.11 (num. 2.4.4.1 "Empuje del Suelo: EH, ES, LS y DD") SE
#      CORTA en el empuje pasivo k_p: no hay 2.4.4.1.6 ni ningun subnumeral
#      LS. Barrido de las 673 paginas: "3.11.6.4" -> 0 apariciones. De modo
#      que h_eq variable con la altura NO sale del corpus peruano y hay que
#      citarlo a AASHTO, declarandolo.
#   2. AASHTO NO OFRECE UN EJE LIBRE "ORIENTACION": ofrece dos BINOMIOS
#      ACOPLADOS -- estribo + perpendicular (Tabla 3.11.6.4-1, cuya variable
#      se llama literalmente "Abutment Height") y muro de contencion +
#      paralelo (Tabla 3.11.6.4-2) --. No hay tabla para "muro perpendicular"
#      ni para "estribo paralelo". Aplicar la Tabla -1 a un cabezal es
#      ANALOGIA declarada, no lectura directa, y por eso el criterio que la
#      habilita es [N->] y no [N].
#   3. NO EXISTE FRASE NORMATIVA QUE REPARTA LAS DOS TABLAS. El articulado las
#      cita juntas y sin condicionante ("may be taken from Tables 3.11.6.4-1
#      and 3.11.6.4-2"); quien las reparte son los TITULOS de las tablas y el
#      comentario C3.11.6.4, que no es articulado. Atribuir el reparto al
#      articulo seria una cita falsa mas.
#   4. EL UMBRAL DE DISTANCIA ES 1.0 ft = 0.3048 m, NO 0.30 m. El plan escribe
#      "borde >= 0.3 m" y ese redondeo RELAJA el criterio: un trasdos con el
#      borde de calzada a 0.30 m exactos no alcanza el umbral de la fuente.
#   5. LA ALTURA QUE ENTRA EN LA TABLA INCLUYE LA ZAPATA: "The wall height
#      shall be taken as the distance between the surface of the backfill and
#      the bottom of the footing". Medirla sin la zapata subestima la altura
#      y, como h_eq DECRECE con ella, sobrestima h_eq.
#
# COMO QUEDA. Los dos numerales rigen a la vez y gobierna el mayor, que es la
# misma regla del mayor de la Sec. 0.2 que el proyecto ya aplica al
# recubrimiento:
#
#     h_eq = max( PISO_MP_M , h_eq_AASHTO(altura_total, orientacion, borde) )
#
# y `orientacion` es un DATO DE SITIO que BLOQUEA mientras no se declare
# (datos_sitio 'orientacion_muro_respecto_al_trafico'). No se sube h_eq a
# 1.12 m ni se deja en 0.60: se declara lo que falta, que es lo que el
# conflicto #4 ordena.
SOBRECARGA_TRASDOS_PISO_MP_M = 0.60   # m; PISO del num. 2.4.2.2, pag. 102
# El nombre viejo se conserva COMO ALIAS DEL PISO y no como "el h_eq", que es
# lo que era. Sigue existiendo porque el manifiesto, la hoja de ruta y los
# tests lo nombran, y porque su valor no cambia: lo que cambia es lo que
# significa. Quien quiera el h_eq de diseño llama a
# `M9.h_eq_sobrecarga_trasdos`, que exige la orientacion.
SOBRECARGA_TRASDOS_H_EQ = SOBRECARGA_TRASDOS_PISO_MP_M

# Las dos tablas de AASHTO, en PIES, que es lo que la fuente imprime. Vistas
# DERIVADAS de la transcripcion del registro: si la transcripcion se corrige,
# estas se corrigen con ella y no quedan dos copias que puedan divergir.
H_EQ_ESTRIBO_PERPENDICULAR_FT = _reg.tabla(
    "AASHTO_LRFD_9.T3.11.6.4-1").pares("altura_ft", "h_eq_ft")
H_EQ_MURO_PARALELO_FT = {
    _t.clave_corta(_f): (_f.valores["altura_ft"],
                         _f.valores["borde_0_0_ft"],
                         _f.valores["borde_1_0_ft_o_mas"])
    for _t in (_reg.tabla("AASHTO_LRFD_9.T3.11.6.4-2"),) for _f in _t.filas
}
# El umbral de distancia del borde de calzada al trasdos, EXACTO. La fuente
# rotula la columna "1.0 ft or Further"; 1.0 in = 25.4 mm exactos, luego
# 1.0 ft = 0.3048 m. Redondearlo a 0.30 va del lado inseguro.
H_EQ_BORDE_UMBRAL_M = 0.3048
H_EQ_BORDE_COLUMNA_CERO = "borde_0_0_ft"
H_EQ_BORDE_COLUMNA_LEJOS = "borde_1_0_ft_o_mas"
# Las dos orientaciones que la fuente tabula. Son NOMBRES de fila, no
# factores: cual aplica a esta obra lo dice el dato de sitio.
ORIENTACION_PERPENDICULAR_AL_TRAFICO = "perpendicular_al_trafico"
ORIENTACION_PARALELO_AL_TRAFICO = "paralelo_al_trafico"
ORIENTACIONES_TABULADAS = (ORIENTACION_PERPENDICULAR_AL_TRAFICO,
                           ORIENTACION_PARALELO_AL_TRAFICO)

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
NUMERAL_FALLA_CERCANA_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.3.10.2.2").como_texto()
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
NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.11.6.5.1#EXC").como_texto()
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
NUMERAL_K_AE_AASHTO = _reg.cita("AASHTO_LRFD_9.A11.3.1#KAE").como_texto()
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
NUMERAL_AGUA_TRASDOS_AASHTO = _reg.cita("AASHTO_LRFD_9.3.11.3").como_texto()
AGUA_TRASDOS_TEXTO_AASHTO = (
    "Submerged unit weights of the soil shall be used to determine the "
    "lateral earth pressure below the groundwater table.")
HIPOTESIS_EMPUJE_BAJO_NF = (
    # --- T-7b --- REESCRITA: hasta T-7b este texto declaraba una DESVIACION
    # (peso total en toda la altura mas la hidrostatica completa: el agua
    # contada dos veces, del lado conservador), que era lo que
    # `M9.empujes_trasdos` hacia. El ensamble de estabilidad
    # (`M9.cargas_del_cabezal`) ya no la comete, y la memoria no puede seguir
    # declarandola.
    "Bajo el nivel del agua el empuje del suelo se calcula con su peso "
    "especifico SUMERGIDO (el saturado menos el del agua), y el agua empuja "
    "aparte con su presion hidrostatica entera, como exige AASHTO 3.11.3: el "
    "agua de poros no se cuenta dos veces. Hasta donde sube el agua del "
    "relleno lo declara 'drenaje_trasdos': sin drenaje declarado, hasta la "
    "superficie del relleno RETENIDO contra el trasdos (coronacion menos "
    "bordillo), nunca por encima del muro (AASHTO 11.6.6); con el, el nivel "
    "freatico natural del punto, medido bajo el terreno del cruce, que no "
    "contempla el desembalse rapido tras la avenida. El peso saturado del relleno es un dato de "
    "ensayo ('peso_especifico_saturado_relleno_kn_m3') que solo hace falta "
    "cuando el agua alcanza el plano de empuje. La funcion suelta "
    "`M9.empujes_trasdos`, anterior al ensamble y sin llamador, conserva la "
    "forma antigua (peso total mas hidrostatica), que cuenta el agua dos "
    "veces del lado conservador. La hoja de ruta decia solo que 'empuje "
    "hidrostatico y subpresion, con NF a 1.4 m, no son opcionales'")

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
    # Las SIETE subfilas de "EV: Presion vertical de la tierra" (sic, sin
    # tilde en "Presion"). Decia "seis" y son siete -- contadas aqui abajo:
    # estabilidad global, muros y estribos, estructura rigida enterrada,
    # porticos rigidos y las tres flexibles --; lo encontro la auditoria
    # adversarial de C7, que ademas midio la contradiccion: este rotulo decia
    # SEIS mientras `M8.filas_ev_de_la_tabla` --que las DERIVA de este mismo
    # dict-- dice SIETE. Las tres ultimas cuelgan ademas del subtitulo
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
NUMERAL_GAMMA_EQ_COMENTARIO = _reg.cita(
    "AASHTO_LRFD_9.C3.4.1#GAMMA_EQ").como_texto()
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
# CORRESPONDENCIA DE FILAS ENTRE LAS DOS TRANSCRIPCIONES DE LA MISMA TABLA.
# No es una eleccion de proyecto: es la reconciliacion de dos traducciones del
# mismo original. AASHTO LRFD Tabla 5.10.1-1 y la Tabla 2.9.1.5.5.3-1 del
# Manual son la misma tabla, y aun asi sus filas NO se pueden cruzar por
# nombre de clave: el Manual traduce "shafts" por "Pilares" donde la
# transcripcion de AASHTO dice "pilote", y ademas PARTE EN DOS la fila de
# pilares in situ en ambiente corrosivo ("En general" / "Armadura
# protegida"), que del lado de AASHTO es una sola.
#
# POR QUE HACE FALTA ESCRIBIRLA. `M9._recubrimiento_aashto_detallado` cruza
# las dos transcripciones con la regla del mayor de Sec. 0.2, y ese cruce
# se hacia con `situacion in RECUBRIMIENTO_MP_MM`. Para las 14 filas de
# nombre coincidente funcionaba; para las 8 de la familia de pilotes la
# condicion daba False y el cruce SE SALTABA SIN AVISAR -- es decir, la red
# de seguridad estaba escrita para 14 filas de 21 y el comentario afirmaba
# que estaba escrita para todas. Con el mapa completo el cruce cubre las 21,
# y una fila sin correspondencia declarada es un error, no un salto callado.
RECUBRIMIENTO_MP_EQUIVALENCIA = {
    "agua_salada":                       ("agua_salada",),
    "vaciado_contra_suelo":              ("vaciado_contra_suelo",),
    "costera":                           ("costera",),
    "sales_anticongelantes":             ("sales_anticongelantes",),
    "tableros_neumaticos_clavos":        ("tableros_neumaticos_clavos",),
    "exterior_no_superior":              ("exterior_no_superior",),
    "interior_hasta_n11":                ("interior_hasta_n11",),
    "interior_n14_n18":                  ("interior_n14_n18",),
    "losa_in_situ_inferior_hasta_n11":   ("losa_in_situ_inferior_hasta_n11",),
    "losa_in_situ_inferior_n14_n18":     ("losa_in_situ_inferior_n14_n18",),
    "paneles_prefabricados_encofrados":  ("paneles_prefabricados_encofrados",),
    "pilote_prefab_armado_no_corrosivo": ("pilar_prefabricado_no_corrosivo",),
    "pilote_prefab_armado_corrosivo":    ("pilar_prefabricado_corrosivo",),
    "pilote_prefab_pretensado":          ("pilote_prefabricado_pretensado",),
    "pilote_in_situ_no_corrosivo":       ("pilar_in_situ_no_corrosivo",),
    # La fila que el Manual parte en dos. Se declaran las DOS subfilas y el
    # cruce toma el mayor de ellas, que es lo que hace la regla de Sec. 0.2
    # cuando una fuente detalla mas que la otra.
    "pilote_in_situ_corrosivo":          ("pilar_in_situ_corrosivo_general",
                                          "pilar_in_situ_corrosivo_protegida"),
    "pilote_in_situ_cascaras":           ("pilar_in_situ_cascaras",),
    "pilote_in_situ_tremie_o_lechada":   ("pilar_in_situ_tremie_o_lechada",),
    "alcantarilla_cajon_prefab_losa_de_rodadura":
        ("alcantarilla_cajon_prefab_losa_de_rodadura",),
    "alcantarilla_cajon_prefab_losa_menos_2_pies":
        ("alcantarilla_cajon_prefab_losa_menos_2_pies",),
    "alcantarilla_cajon_prefab_otros_miembros":
        ("alcantarilla_cajon_prefab_otros_miembros",),
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
NUMERAL_FACTOR_AC_AASHTO = _reg.cita("AASHTO_LRFD_9.5.10.1").como_texto()
NUMERAL_RECUBRIMIENTO_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.T5.10.1-1").como_texto()
# LOS OTROS DOS TEXTOS QUE CONDICIONAN LA TABLA 5.10.1-1, y son los ultimos:
# la cadena "Table 5.10.1-1" aparece en TRES paginas de toda la especificacion
# -- 5-167, 5-168 y 5-169 -- y en ninguna mas, de modo que la lista esta
# CERRADA, no muestreada. Uno lo aplica el calculo (el piso de 1.0 in sobre
# las barras principales) y el otro NO, y por eso se declaran los dos: quien
# lea la transcripcion tiene que poder ver que la regla de estribos existe y
# que este proyecto no la usa porque dimensiona barras principales.
NUMERAL_RECUBRIMIENTO_PISO_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.5.10.1#PISO").como_texto()
NUMERAL_RECUBRIMIENTO_ESTRIBOS_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.5.10.1#ESTRIBOS").como_texto()
RECUBRIMIENTO_ESTRIBOS_TEXTO = (
    "Cover to ties and stirrups may be 0.5 in. less than the values "
    "specified in Table 5.10.1-1 for main bars but shall not be less than "
    "1.0 in. except for precast soffit form panels noted in the table below.")
# POR QUE NO ES UN `Modificador` DEL REGISTRO. Un modificador es
# MULTIPLICATIVO -- factor y piso --, y esta regla RESTA 0.5 in con piso de
# 1.0 in. Meterla ahi obligaria a inventarle un factor y seria una lectura
# falsa del tipo, que es justo lo que el esquema existe para impedir.
RECUBRIMIENTO_AC_UMBRAL_BAJO = 0.40    # "Para W/C <= 0.40 ... 0.8"
RECUBRIMIENTO_AC_UMBRAL_ALTO = 0.50    # "Para W/C >= 0.50 ... 1.2"
RECUBRIMIENTO_MP_FACTOR_AC_LAGUNA = (
    "El Manual de Puentes imprime solo dos factores (W/C <= 0.40 -> 0.8 y "
    "W/C >= 0.50 -> 1.2) y deja sin factor la banda intermedia 0.40 < W/C < "
    "0.50, que AASHTO LRFD 9a ed. Art. 5.10.1 (pag. impresa 5-167) si cubre "
    "con 1.0. LA BANDA ES ALCANZABLE EN ESTE PROYECTO: una version anterior "
    "de esta nota decia que no lo era 'porque su a/c maxima la fija la Tabla "
    "4.2 de E.060 en 0.40 por cloruros', y eso daba por sabido justamente el "
    "dato que este cluster declaro VACIO ('exposicion_quimica_ems'). Con "
    "sulfatos severos y sin cloruros la a/c maxima resulta 0.45 y la banda "
    "intermedia se activa, de modo que la laguna del corpus peruano hay que "
    "cubrirla de verdad: lo hace el criterio [C] "
    "'factor_recubrimiento_banda_intermedia_ac', no un literal del modulo")
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

# LA CITA CORREGIDA, y sale del registro en vez de escribirse aqui: es UNA
# cita referenciada, no una cadena que casualmente coincide con otras cinco
# (NOR-PUE-01). El numeral viejo -- 2.1.4.3.9 "Aparatos de Apoyo" -- sigue en
# el registro como `MP.2.1.4.3.9`, declarado como lo que es, para que quien
# venga con la cita vieja en la mano encuentre por que no vale.
NUMERAL_SOBRECARGA_TRASDOS = _reg.cita("MP.2.4.2.2#SOBRECARGA").como_texto()
# EL Ka ESTATICO ES EL DE COULOMB DEL MANUAL (EXT-M-06). La v8 §9.2 escribia
# «Ka = tan²(45 − φ/2)» -- Rankine -- sin decir de donde salia, y M9 la
# seguia en el empuje estatico y la sobrecarga mientras el incremento sismico
# iba con Mononobe-Okabe, que es Coulomb con aceleracion. La fuente primaria
# del marco de §9.1 escribe Coulomb (num. 2.4.4.1.5.3, ecs. -1 y -2, pag.
# impresa 135), que con trasdos vertical, δ = 0 y relleno horizontal se
# reduce exactamente a la forma de la hoja. EXT-0 enmendo la hoja
# (DIS-HR-KA-COULOMB, resuelta); M9 lo declara en el punto de uso y la
# memoria lo imprime por `condicion_normativa_cabezal`.
NUMERAL_KA_COULOMB = _reg.cita("MP.2.4.4.1.5.3").como_texto()
KA_COULOMB_DECLARACION = (
    "Coeficiente de empuje activo estatico: el de Coulomb del "
    f"{NUMERAL_KA_COULOMB} (3.11.5.3 AASHTO), calculado con la misma "
    "formulacion que Mononobe-Okabe haciendo k_h = k_v = 0, de modo que el "
    "incremento sismico K_AE - K_A resta dos coeficientes homogeneos. Con "
    "trasdos vertical, friccion muro-relleno nula y relleno horizontal se "
    "reduce a tan^2(45 - phi/2), la forma que la hoja de ruta escribia en su "
    "Sec. 9.2 y que EXT-0 corrigio (discrepancia DIS-HR-KA-COULOMB, "
    "resuelta); con i, beta o delta distintos de cero los dos coeficientes "
    "difieren y rige el de Coulomb. La resultante de Coulomb actua a delta "
    "de la normal al plano de empuje (delta + beta respecto de la "
    "horizontal), y desde T-7b el ensamble de estabilidad la DESCOMPONE: la "
    "componente horizontal entra en el deslizamiento y en el momento "
    "volcante, y la vertical carga la base en el plano de empuje, que en un "
    "muro con talon es el vertical de su extremo (AASHTO C3.11.5.3). La "
    "ficha EXT-7-04, que la dejaba entera como horizontal, queda cerrada")
NUMERAL_SOBRECARGA_TRASDOS_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.3.11.6.4").como_texto()
NUMERAL_SOBRECARGA_TRASDOS_ALTURA = _reg.cita(
    "AASHTO_LRFD_9.3.11.6.4#ALTURA").como_texto()
NUMERAL_SOBRECARGA_TRASDOS_APLICA = _reg.cita(
    "AASHTO_LRFD_9.3.11.6.4#APLICA").como_texto()
# El COMENTARIO, que no es articulado y aun asi es lo unico que reparte las
# dos tablas junto con sus titulos. Se cita como comentario, no como articulo.
NUMERAL_SOBRECARGA_TRASDOS_COMENTARIO = _reg.cita(
    "AASHTO_LRFD_9.C3.11.6.4").como_texto()
H_EQ_REPARTO_DE_TABLAS = (
    "NO EXISTE en el articulado de AASHTO ninguna frase que reparta las dos "
    "tablas de h_eq: el cuerpo normativo las cita juntas y sin condicionante "
    "(«may be taken from Tables 3.11.6.4-1 and 3.11.6.4-2»). Quien las "
    "reparte son los TITULOS de las tablas -- «on Abutments Perpendicular to "
    "Traffic» y «on Retaining Walls Parallel to Traffic» -- y el comentario "
    "C3.11.6.4, que no es articulado. Atribuir el reparto al articulo seria "
    "una cita falsa; se cita a los titulos y al comentario, que es de donde "
    "sale")
# El numeral FALSO, declarado. No se borra: se nombra, para que el error tenga
# un sitio donde estar dicho y para que un test tenga contra que fallar si
# alguien lo reactiva.
NUMERAL_SOBRECARGA_TRASDOS_RETIRADO = _reg.cita("MP.2.1.4.3.9").como_texto()
# El rango de paginas DEJABA FUERA LA SEGUNDA FIGURA (NOR-PUE-13). Decia
# "pags. 272-273", y verificado contra el PDF: el texto del numeral esta en la
# pag. impresa 272 (PDF 273), la Figura 2.8.1.3.1.2c-1 -- suelos COHESIVOS --
# en la 273 (PDF 274) y la Figura 2.8.1.3.1.2c-2 -- suelos NO COHESIVOS -- en
# la 274 (PDF 275). Un revisor que abriera el rango declarado encontraria una
# de las dos figuras y no la otra, y son las dos las que hay que leer: cual
# aplica lo decide el tipo de suelo de fundacion.
NUMERAL_ZAPATA_EN_TALUD = ("2.8.1.3.1.2c, pags. impresas 272-274 (PDF "
                           "273-275): texto en la 272, Figura -1 (cohesivos) "
                           "en la 273, Figura -2 (no cohesivos) en la 274")
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
# EL CODIGO E1..E5 DE CADA FILA, derivado de la misma tabla y no escrito en
# los llamadores (EXT-M-07): `EstabilidadCabezal.exigidas` sale de aqui, de
# modo que «estable» significa las CINCO filas presentes y cumplidas, no las
# tres que el cabezal resuelve con sus propias fuerzas. Es una etiqueta de
# navegacion, como FS_NUMERAL, no un valor.
FS_CODIGO = {
    "capacidad_portante": "E1",
    "volteo":             "E2",
    "deslizamiento":      "E3",
    "estabilidad_global": "E4",
    "talud":              "E5",
}
FS_NUMERAL = {                      # el numeral de cada fila de la tabla de 9.3
    "capacidad_portante": _reg.cita("E050.21").como_texto(),
    "volteo":             _reg.cita("E050.39.13.6").como_texto(),
    "deslizamiento":      _reg.cita("E050.39.13.6").como_texto(),
    "estabilidad_global": _reg.cita("E050.39.13.6").como_texto(),
    "talud":              _reg.cita("E050.30.3").como_texto(),
}
# COMO NOMBRA E.050 LA SEGUNDA CONDICION, que NO es «sismico» en tres de las
# cinco filas (NOR-E050-01). La clave del dict se conserva porque esta
# cableada en M9 y en la memoria; lo que se añade es la palabra de la fuente,
# que es la que la memoria tiene que imprimir junto al numero:
#
#   Art. 21.2   «Para solicitacion maxima de SISMO O VIENTO (la que sea mas
#               desfavorable)». El viento esta DENTRO de la misma casilla, y
#               «sismico» lo excluye.
#   Art. 30.3   «en condiciones SISMICAS». Es el unico de los tres donde la
#               palabra es literal.
#   39.13.6     «Condicion Pseudo - dinamico» en a-2 y «condicion
#               pseudo-dinamica» en b). NO es un sinonimo decorativo: designa
#               el METODO de analisis -- coeficiente sismico horizontal
#               aplicado como fuerza estatica equivalente --, y el FS de 1.25
#               esta atado a ese metodo.
#   Anexo I     un CUARTO termino, «dinamico» a secas (pag. impresa 74).
#
# Aplanar los cuatro en «sismico» borra dos cosas distintas: que en capacidad
# portante el gobernante puede ser el VIENTO, y que en muros el 1.25 es de un
# metodo pseudoestatico concreto.
FS_NOMBRE_DE_LA_CONDICION = {
    "capacidad_portante": {
        "estatico": "Para cargas estáticas",
        "sismico": ("Para solicitación máxima de sismo o viento (la que sea "
                    "más desfavorable)")},
    "volteo": {"estatico": "Condición Estático",
               "sismico": "Condición Pseudo - dinámico"},
    "deslizamiento": {"estatico": "Condición Estático",
                      "sismico": "Condición Pseudo - dinámico"},
    "estabilidad_global": {"estatico": "condición estática",
                           "sismico": "condición pseudo-dinámica"},
    "talud": {"estatico": "en consideraciones estáticas",
              "sismico": "en condiciones sísmicas"},
}
# La coletilla que cierra el 39.13.6 y condiciona sus dos incisos por igual.
# El repositorio no la recogia.
FS_MUROS_ESTADO_LIMITE = "En todos los casos respecto al estado límite del suelo"
NUMERAL_C_PHI = _reg.cita("E050.20").como_texto()
NUMERAL_ZAPATA_TALUD_E050 = "E.050 Art. 30.1-30.2"

# ---------------------------------------------------------------------------
# El programa de SPT -- y PARA QUE es (NOR-E050-02)
# ---------------------------------------------------------------------------
# DOS COSAS QUE EL REPOSITORIO DECIA MAL. La primera es que el espaciamiento
# figuraba "sin numeral": SI LO TIENE, es el 38.4.3 (pag. impresa 51), y va
# reforzado con el adverbio «obligatoriamente». La segunda es mas grave y es
# de ALCANCE: los dos valores viven bajo el «Articulo 38.- Licuacion de
# suelos», y el 38.4.1 los dispara SOLO «Cuando la historia sismica del lugar
# haga sospechar la posibilidad de ocurrencia de Licuacion». NO son el
# programa de SPT general de E.050 -- ese esta en el 14.2.3 y la Tabla 3,
# pags. impresas 18-19 --: son el programa de exploracion PARA ANALISIS DE
# LICUEFACCION. Citarlos como minimos universales del SPT extiende la norma
# mas alla de lo que dice.
#
# Para este expediente el disparador SI se cumple -- el sitio se atribuye
# suelos potencialmente licuables --, de modo que los valores aplican; lo que
# faltaba era decir POR QUE aplican.
SPT_PROF_MIN = 15.0                 # m
SPT_ESPACIAMIENTO = 1.0             # m entre ensayos
NUMERAL_SPT = _reg.cita("E050.38.4.3").como_texto()
SPT_AMBITO = (
    "El num. 38.4.3 vive bajo el «Articulo 38.- Licuacion de suelos», "
    "sub-numeral «38.4 Exploracion de campo», y el 38.4.1 lo dispara solo "
    "«Cuando la historia sismica del lugar haga sospechar la posibilidad de "
    "ocurrencia de Licuacion». No es el programa de SPT general de E.050 -- "
    "ese esta en el num. 14.2.3 y la Tabla 3 --: es el de exploracion para "
    "analisis de licuefaccion. En este expediente el disparador se cumple")

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
# TABLA 4.2. La version anterior de este cluster llego a escribir aqui que
# citarla como "Art. 4.2 / 4.4" eran "dos numerales distintos citados como si
# fueran uno", y ESO ERA FALSO: verificado contra el PDF, el Art. 4.4.2
# (pag. impresa 39) es precisamente el articulo que MANDA aplicar la Tabla 4.2
# a los cloruros externos, y ademas remite al recubrimiento -- "deben
# cumplirse los requisitos de la Tabla 4.2 para la maxima relacion
# agua-material cementante y valor minimo de f'c, y los requisitos de
# recubrimiento minimo del concreto de 7.7". Es el eslabon normativo que ata
# este cluster de punta a punta, y la cadena de numerales lo habia perdido.
# Lo que si es cierto del 4.4 es que su primer inciso, el 4.4.1, va de otra
# cosa (contenido de ion cloruro en el concreto endurecido, Tabla 4.5): por
# eso se cita el 4.4.2 y no "el 4.4".
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
NUMERAL_EXPOSICION_ESPECIAL = ("E.060 Tabla 4.2, pag. impresa 37, aplicada "
                               "por el Art. 4.4.2, pag. impresa 39")
PROTECCION_CORROSION_TEXTO = (
    "Cuando el concreto con refuerzo vaya a estar expuesto a cloruros de "
    "químicos descongelantes, sal, agua salobre, agua de mar o salpicaduras "
    "de las mismas, deben cumplirse los requisitos de la Tabla 4.2 para la "
    "máxima relación agua-material cementante y valor mínimo de f'c, y los "
    "requisitos de recubrimiento mínimo del concreto de 7.7")
NUMERAL_PROTECCION_CORROSION = "E.060 Art. 4.4.2, pag. impresa 39"

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
NUMERAL_RECUBRIMIENTO = _reg.cita("E060.7.7.1").como_texto()
# El encabezado del 7.7.1 remite EL MISMO al 7.7.5.1: el aumento por ambiente
# corrosivo no es una nota externa que alguien decidio traer, es la excepcion
# que el propio articulo de los 70/50/40 mm declara.
RECUBRIMIENTO_SALVEDAD_TEXTO = (
    "Debe proporcionarse el siguiente recubrimiento mínimo de concreto al "
    "refuerzo, excepto cuando se requieran recubrimientos mayores según "
    "7.7.5.1 ó se requiera protección especial contra el fuego")
AMBIENTE_CORROSIVO_AUMENTAR = _reg.cita("E060.7.7.5.1").como_texto()
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
# alto, y el de la ec. (11-32) del 11.10.10.3 para la cuantia VERTICAL --
# sigue sin transcribirse como constante [N] en este archivo: la hoja de
# ruta lo recoge desde EXT-0 (v8 §9.4) y el registro tiene las cuatro citas
# desde EXT-6 (NUMERAL_CORTANTE_MUROS_E060, abajo), pero cablearlo con su
# caso patron es la sesion EXT-7 (EXT-M-05, R95-031). Mientras siga asi, el
# 0.0020 de abajo es el minimo MENOR de los dos que tiene E.060, y M9 obliga
# a contestar expresamente cual aplica ('cortante_alto_muro_e060_art_11_10_10_2').
CUANTIA_MIN_MURO = {"horizontal": 0.0020, "vertical": 0.0015}   # Art. 14.3.1, pag. 133
# Las cuatro citas de E.060 11.10 que EXT-7 consume, como texto de numeral y
# no como valor: la pregunta de aplicabilidad (11.10.1 remite el cortante
# perpendicular al plano a las losas de 11.12; 11.10.2 rige el cortante EN el
# plano) y los dos pisos bajo el regimen de 11.10.10. Salen del registro.
NUMERAL_CORTANTE_MUROS_E060 = {
    "perpendicular_al_plano": _reg.cita("E060.11.10.1").como_texto(),
    "en_el_plano": _reg.cita("E060.11.10.2").como_texto(),
    "cuantia_horizontal_min": _reg.cita("E060.11.10.10.2").como_texto(),
    "cuantia_vertical_min": _reg.cita("E060.11.10.10.3").como_texto(),
}
NUMERAL_CUANTIA_MIN = _reg.cita("E060.14.3.1").como_texto()
# Las DOS lecturas del plano del cortante, como NOMBRES de la categoria que
# el criterio 'regimen_cortante_muro_e060_art_11_10_2' declara (EXT-M-05).
# Son texto de navegacion, no valores: cual aplica a esta obra lo decide el
# proyectista con el diseno estructural delante. Con cortante EN EL PLANO
# rigen 11.10.3 a 11.10.10 (11.10.2); PERPENDICULAR al plano, el diseno es
# el de losas de 11.12 (11.10.1) y ni el 11.10.10.2 ni el .3 escalonan nada.
REGIMEN_CORTANTE_EN_EL_PLANO = "en_el_plano"
REGIMEN_CORTANTE_PERPENDICULAR = "perpendicular_al_plano"
REGIMENES_CORTANTE_MURO = (REGIMEN_CORTANTE_EN_EL_PLANO,
                           REGIMEN_CORTANTE_PERPENDICULAR)
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
NUMERAL_DOS_CAPAS_REFUERZO = _reg.cita("E060.14.3.2").como_texto()
EXCEPCION_DOS_CAPAS_REFUERZO = "excepto los muros de sótanos"
ESPESOR_TEMPERATURA_DOS_CARAS = 0.250       # m (250 mm); Art. 14.8.3, inclusivo
NUMERAL_TEMPERATURA_DOS_CARAS = "E.060 Art. 14.8.3, pag. 134"
ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0       # <= 3h        Art. 14.3.3
ESPACIAMIENTO_MAX_ABSOLUTO = 0.400          # m (400 mm)   Art. 14.3.3
# DOS NUMERALES CON EL MISMO CONTENIDO Y OTRAS PALABRAS, hallado al verificar:
# el 14.3.3 (muros en general) y el 14.8.4 (muros de CONTENCION, pag. impresa
# 134). Para un cabezal -- que es un muro de contencion -- el aplicable
# directo es el segundo, y el expediente citaba solo el primero.
NUMERAL_ESPACIAMIENTO = _reg.cita("E060.14.3.3").como_texto()
NUMERAL_ESPACIAMIENTO_MURO_CONTENCION = _reg.cita("E060.14.8.4").como_texto()

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
# LA DISCREPANCIA CON LA HOJA DE RUTA QUEDO RESUELTA EN I2. Estuvo declarada
# en este punto de uso porque la regla de CLAUDE.md pide las tres cosas y no
# una: (1) la Sec. 9.4 de la hoja de ruta escribia "f'c de matriz >= 10 MPa"
# y este modulo verifica contra 14 MPa; (2) el defecto era de la hoja de
# ruta, que miraba solo a E.060 y no veia que sobre el mismo material rige
# tambien la Tabla 503-07 del EG-2013, que es norma vial del MTC y pide mas;
# (3) la v8 escribe hoy los dos minimos y el mayor, con su nota «Corregido
# (DIS-HR-CICLOPEO, I2)». La fuente primaria decidio (EG-2013 Tabla 503-07,
# pag. impresa 912) y por eso gano. La historia entera esta en la
# Discrepancia DIS-HR-CICLOPEO del registro (manifiesto §7).
CICLOPEO_DOS_MINIMOS = (
    "Sobre la matriz del concreto ciclopeo rigen dos minimos: el Art. 22.10 "
    "de E.060 pide f'c >= 10 MPa y la Clase G de la Tabla 503-07 del EG-2013 "
    "-- norma vial del MTC que este proyecto aplica -- pide 14 MPa; por la "
    "regla del mayor gobierna esta ultima")
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
# el criterio 'clase_sitio' invoca (NOR-AAS-02).
#
# LA PREMISA YA NO ESTA ABIERTA -- este comentario decia que si, y desde S13
# es falso. Se resolvio contra las fuentes primarias, y no por el silencio
# sino por algo mas fuerte: las dos PROHIBEN suponer la clase E o F sin dato
# geotecnico ni determinacion de la autoridad. El expediente dejo de
# atribuirse la Clase F y 'clase_sitio' es hoy un [S] SIN VALOR. Fundamento
# en docs/resolucion_clase_sitio.md; discrepancia DIS-HR-CLASE-DE-SITIO-F
# (resuelta en I2: la Sec. 0.5 de la v8 quedo corregida).
# Esta constante sigue siendo util y no cambia: describe la discrepancia
# entre los DOS ESQUEMAS, que es un hecho de las normas y no una premisa del
# expediente.
E030_S5_VS_CLASE_F = (
    "E.030 clasifica los suelos potencialmente licuables en su perfil S5 "
    "'Suelos excepcionales' (Art. 14.6, Tabla N 2). AASHTO LRFD 9a ed. y el "
    "Manual de Puentes NO los nombran en su Clase de Sitio F y tratan la "
    "licuefaccion por via distinta de la clase de sitio (AASHTO Art. "
    "10.5.4.2). Los dos esquemas discrepan justamente en el rasgo que motiva "
    "la clasificacion de este sitio, y el salto de uno al otro no lo escribe "
    "ninguno de los dos: es premisa abierta del expediente, no cita")


# ---------------------------------------------------------------------------
# La clase de sitio, y por que este expediente no se atribuye ninguna
# ---------------------------------------------------------------------------
# Lo que la memoria tiene que imprimir sobre la clase de sitio, segun la
# seccion 4 de docs/resolucion_clase_sitio.md (S13, conflicto #8). Vive aqui
# y no en M9 por la razon de siempre: los textos entrecomillados son
# transcripciones normativas y salen del REGISTRO, no de una segunda copia a
# mano. M9.condicion_normativa_cabezal los lleva a las dos plantillas.
#
# Cierra NOR-AAS-02 (la premisa), SIS-B-01 (la memoria nunca lo declaraba),
# SIS-D-01 (F_pga y clase_sitio se defendian con premisas contradictorias) y
# NOR-MEM-03 (la convergencia C/D/E omitia la fila que el expediente
# reclamaba).
NUMERAL_CLASE_SITIO_AASHTO = _reg.cita("AASHTO_LRFD_9.3.10.3.1").como_texto()
NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA = _reg.cita(
    "AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES").como_texto()
NUMERAL_CLASE_SITIO_INVESTIGACION = _reg.cita(
    "AASHTO_LRFD_9.3.10.3.1#INVESTIGACION").como_texto()
NUMERAL_CLASE_SITIO_MP = _reg.cita("MP.2.4.3.11.2.1.1").como_texto()
NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA_MP = _reg.cita(
    "MP.2.4.3.11.2.1.1#EXCEPCIONES").como_texto()
NUMERAL_CLASE_SITIO_F_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.T3.10.3.1-1#F").como_texto()
NUMERAL_RESPUESTA_DE_SITIO_AASHTO = _reg.cita(
    "AASHTO_LRFD_9.3.10.2#CLASE_F").como_texto()
NUMERAL_RESPUESTA_DE_SITIO_MP = _reg.cita("MP.2.4.3.11.2#CLASE_F").como_texto()
NUMERAL_LICUEFACCION_AASHTO = _reg.cita("AASHTO_LRFD_9.10.5.4.2").como_texto()
NUMERAL_LICUEFACCION_ESPECTRO = _reg.cita(
    "AASHTO_LRFD_9.10.5.4.2#ESPECTRO").como_texto()

# Los textos literales, del registro y no copiados: conservan sus tildes
# (invariante T21) aunque el resto de este bloque se escriba sin ellas.
CLASE_SITIO_EF_NO_SUPUESTA_TEXTO = _reg.cita(
    "AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES").texto_literal.texto
CLASE_SITIO_EF_NO_SUPUESTA_MP_TEXTO = _reg.cita(
    "MP.2.4.3.11.2.1.1#EXCEPCIONES").texto_literal.texto
CLASE_SITIO_INVESTIGACION_TEXTO = _reg.cita(
    "AASHTO_LRFD_9.3.10.3.1#INVESTIGACION").texto_literal.texto
CLASE_SITIO_F_TEXTO = _reg.cita(
    "AASHTO_LRFD_9.T3.10.3.1-1#F").texto_literal.texto

CLASE_DE_SITIO_INDETERMINADA = (
    "Clase de sitio sismica: INDETERMINADA. Este expediente NO se atribuye la "
    "Clase de Sitio F, y no puede: el articulado que la define prohibe "
    "suponerla. Este expediente no tiene determinacion de la Entidad ni datos "
    "geotecnicos: el SPT esta pendiente. La misma clausula fija el deber "
    "positivo que queda abierto -- investigar hasta poder determinar la "
    "clase --, y por eso la clase de sitio es un dato de sitio [S] SIN VALOR "
    "y no una adopcion del proyectista")

CLASE_DE_SITIO_POR_QUE_DEJA_DE_DECIRSE = (
    "Por que el expediente decia Clase F, y por que deja de decirlo: el salto "
    "de 'suelo potencialmente licuable' a 'Clase de Sitio F' NO lo escribe "
    "ninguno de los dos documentos que la cadena sismica invoca. La fila F de "
    "la Tabla 3.10.3.1-1 enumera turbas o arcillas altamente organicas, "
    "arcillas de muy alta plasticidad y estratos potentes de arcilla blanda, "
    "y ninguna es licuefaccion; en las 1905 paginas de AASHTO no hay una sola "
    "donde coincidan 'liquefaction' y 'Site Class F'. La licuefaccion la "
    "trata el Art. 10.5.4.2 'Liquefaction Design Requirements', por via de "
    "cimentaciones y disparada por zona sismica, napa freatica y "
    "caracteristicas de suelo, nunca por la clase de sitio. Quien SI "
    "clasifica los suelos licuables en su categoria excepcional es E.030, en "
    "el perfil S5, que es de donde el expediente sacaba la letra: son dos "
    "esquemas distintos y discrepan justo en el rasgo que motivaba la "
    "clasificacion de este sitio")

CLASE_DE_SITIO_COHERENCIA_INTERNA = (
    "Y no es solo que la norma calle: el Art. 10.5.4.2 manda analizar el "
    "sitio licuable en configuracion no licuada y licuada con el mismo "
    "espectro de diseno, y acota el espectro especifico de sitio a no menos "
    "de dos tercios del general 'modified by the site factors in Article "
    "3.10.3.2'. AASHTO ESPERA que a un sitio licuable le aplique un factor de "
    "sitio tabulado, cosa imposible si la licuefaccion lo hiciera Clase F, "
    "porque la fila F no tiene factor. El reparto coherente es el que este "
    "expediente ya hace: clasificar por rigidez medida y evaluar la "
    "licuefaccion aparte, con el SPT de 15 m del Art. 38 de E.050")

CLASE_DE_SITIO_QUE_LA_CIERRA = (
    "Lo que cierra este vacio, y son DOS ensayos de profundidades distintas "
    "que conviene pedir juntos: (1) la caracterizacion de los 100 ft "
    "(30.48 m) superiores -- Vs30 o N_barra --, que es la profundidad que el "
    "Art. 3.10.3.1 escribe y con la que se lee la clase; y (2) si esa "
    "caracterizacion diera Clase F, el analisis de respuesta dinamica de "
    "sitio, que el Art. 3.10.2 exige con 'shall' y el num. 2.4.3.11.2 del "
    "Manual con 'sera usado'. NO lo cierra el SPT de licuefaccion de 15 m de "
    "E.050 Art. 38: ese ensayo responde a otra pregunta y se detiene a mitad "
    "de la columna que esta clase necesita")


# ---------------------------------------------------------------------------
# HOMONIMIAS: las palabras que significan dos o tres cosas en este expediente
# ---------------------------------------------------------------------------
# Cuatro terminos del corpus designan cosas distintas y sin relacion, y los
# dos sentidos de cada uno llegan a la MISMA memoria. Un revisor que lea el
# segundo con la definicion del primero no comete un error de calculo: comete
# un error de lectura, que es peor, porque no deja rastro.
#
# Se declaran AQUI, en un solo sitio, y M11 los imprime como glosario
# (`bloque_homonimias`). Antes cada uno vivia -- cuando vivia -- pegado a la
# constante que lo sufria, de modo que el lector lo encontraba solo si ya
# estaba mirando esa constante, que es justo cuando no le hace falta.
#
# Cierra NOR-VOC-01, NOR-VOC-02, NOR-VOC-03 y NOR-VOC-04.
#
# El formato es (TERMINO, SENTIDOS, LECTURA): los sentidos numerados, cada uno
# con su fuente, y la lectura que resuelve cual aplica.

HOMONIMIA_RECUBRIMIENTO = (
    "«Recubrimiento»",
    (
        "(a) ALTURA DE RELLENO DE TIERRA sobre la clave del conducto. Es "
        "vocabulario de este proyecto y de la Sec. 12 de AASHTO LRFD "
        "('cover', Art. 12.6.6.3): la que fija la rasante minima y la que "
        "gobierna 'cobertura_minima_aashto'. En metros.",
        "(b) RECUBRIMIENTO DE CONCRETO sobre el acero de refuerzo. Manual de "
        "Puentes, Tabla 2.9.1.5.5.3-1, pag. impresa 378; AASHTO LRFD Tabla "
        "5.10.1-1. En milimetros o pulgadas.",
        "(c) REVESTIMIENTO METALICO O BITUMINOSO de la plancha de acero. "
        "EG-2013 Seccion 507, Tabla 507-02 «Recubrimiento en peso de zinc, "
        "de acuerdo al espesor del acero base», pag. impresa 971 (610 a "
        "915 g/m2 por las dos caras), y el recubrimiento bituminoso del "
        "mismo numeral, que remite a AASHTO M-190. En gramos por metro "
        "cuadrado. Es el sentido que gobierna la proteccion del TMC en el "
        "ambiente agresivo de este proyecto, y el que faltaba declarar "
        "(NOR-VOC-02).",
    ),
    "Y NO SON TRES SENTIDOS INDEPENDIENTES, que es la otra mitad de la "
    "correccion: el repositorio afirmaba que (a) y (b) «no tienen ninguna "
    "relacion», y la fila que se citaba para decirlo los ACOPLA en su propio "
    "renglon -- «forjados con inferior a 2 pies de relleno que no se "
    "utilicen como una superficie de conduccion: 2.0 in» --, donde el "
    "recubrimiento del acero depende de la altura de relleno. Lo que se "
    "sostiene es lo mas debil y lo suficiente: son magnitudes distintas, con "
    "unidades distintas, y ninguna se puede usar en lugar de la otra.",
)

HOMONIMIA_TW = (
    "«TW» y «cota_TW»",
    (
        "TW es un TIRANTE: la altura de agua en el cuerpo receptor medida "
        "SOBRE EL FONDO DE LA SALIDA del conducto, en metros. Es lo que "
        "consume el control de salida (Sec. 4.3) y lo que declara el "
        "criterio 'TW_receptor'; la opcion de linea de comandos es `--tw`.",
        "cota_TW es una COTA ABSOLUTA, en msnm. Es columna del CSV de "
        "Sec. 1.2 y viene del tablero del ANA.",
    ),
    "Las separa exactamente la cota de fondo de la salida: "
    "cota_TW = cota_fondo_salida + TW. Confundirlas desplaza el control de "
    "salida en la magnitud ENTERA de esa cota -- centenares de metros en "
    "este corredor --, y el error no se ve porque los dos numeros son "
    "plausibles. Hoy no se puede ejercitar la confusion: las cuatro filas "
    "del CSV traen `cota_TW` vacia y el TW entra declarado. Se anota como "
    "riesgo de nomenclatura, no como error demostrado (NOR-VOC-01).",
)

HOMONIMIA_LUZ = (
    "«Luz» y «diametro»",
    (
        "LUZ es un dato de ENTRADA del cruce -- el ancho del canal o de la "
        "quebrada que hay que salvar -- y lo unico que decide con ella este "
        "software es si el cruce es alcantarilla o puente: «alcantarilla... "
        "cuya luz sea menor a 6.0 m» (num. 4.1.1.3.1, pag. impresa 70) y "
        "«puente... cuya luz sea mayor o igual a 6.0 m» (num. 4.1.1.5.1, "
        "pag. impresa 87). Entra por `--luz`, no es columna de Sec. 1.2.",
        "DIAMETRO es un RESULTADO: el del conducto que M2 y MD seleccionan "
        "del catalogo circular de Sec. 3.2, que arranca en 0.90 m.",
    ),
    "EL MANUAL NO DEFINE LA «LUZ» DE UN CONDUCTO CIRCULAR, y este proyecto "
    "NO LA NECESITA: ningun modulo convierte una en otra. La luz clasifica "
    "el cruce en la Fase 2 y el diametro se dimensiona despues, con el "
    "caudal, sin que la luz vuelva a entrar. Se declara porque el riesgo es "
    "de lectura: un revisor puede suponer que el 6.0 m del umbral y el "
    "0.90 m del catalogo estan en la misma escala. El num. 4.1.1.3.4 a) "
    "(pag. impresa 72) admite ademas «seccion minima circular de 0.90 m de "
    "diametro o su equivalente de otra seccion», y esa equivalencia no esta "
    "declarada en ninguna parte -- ni hace falta mientras el catalogo de "
    "Sec. 3.2 sea solo circular. El dia que se ofrezca una seccion no "
    "circular, hay que declararla antes (NOR-VOC-03).",
)

HOMONIMIA_CLASE_F = (
    "«Clase F»",
    (
        "CLASE DE SITIO SISMICA: AASHTO LRFD Tabla 3.10.3.1-1 / Manual de "
        "Puentes Tabla 2.4.3.11.2.1.1-1, «suelos que requieren evaluaciones "
        "especificas de sitio». Es la del eje de la Sec. 0.5, y este "
        "expediente NO se la atribuye: ver 'clase_sitio'.",
        "CONCRETO CLASE F: resistencia, EG-2013 Tabla 503-07, pag. impresa "
        "912 -- concreto simple, f'c = 14 MPa. Es la del relleno lateral y "
        "la cama de apoyo.",
        "ACERO ASTM A668 CLASE F: el propio Manual de Puentes lo tabula en "
        "su pag. impresa 289. No llega a esta memoria; se anota para que "
        "nadie lo cruce con los otros dos.",
    ),
    "Las dos primeras llegan a esta memoria, y por eso toda aparicion de "
    "«Clase F» lleva su calificador -- «Clase de Sitio F» o «Concreto "
    "Clase F» --, siempre, sin excepcion de contexto (NOR-VOC-04).",
)

HOMONIMIAS = (HOMONIMIA_CLASE_F, HOMONIMIA_RECUBRIMIENTO,
              HOMONIMIA_TW, HOMONIMIA_LUZ)


def homonimia_como_texto(homonimia) -> str:
    """
    Una homonimia en un parrafo, como la imprime una memoria en texto plano.

    La compone esta funcion y no un campo, por lo mismo que `Cita.como_texto`:
    los separadores son del proyecto y no de ninguna fuente. Existe para que
    M9 -- que imprime la de «Clase F» pegada a la cadena sismica, donde el
    lector se encuentra el termino -- y M11 -- que las imprime todas como
    glosario -- lean la MISMA declaracion en vez de dos copias que pueden
    desviarse.
    """
    termino, sentidos, lectura = homonimia
    return f"{termino} en este expediente: " + " ".join(sentidos) + f" {lectura}"

# ===========================================================================
# --- T-1 --- Hidrologia (Manual de Hidrologia, cap. III): lo que consume
# `modulos/MH_hidrologia.py`. Cadena T, 2026-11-11
# ===========================================================================
# Todo lo de este bloque lo leyo la sesion en el PDF (texto e imagen) y cada
# valor lleva su cita en el registro. Las cuatro TABLAS no se transcriben
# aqui: se DERIVAN de `normativa/tablas.py`, que es donde estan escritas una
# sola vez (regla D2). Los coeficientes de las FORMULAS si se escriben aqui,
# porque el registro guarda una formula como texto y no como numeros.
#
# UNIDADES. La hidrologia del Manual se escribe en mm, mm/h, km2, minutos y
# horas, y este bloque las conserva porque los coeficientes empiricos SON de
# esas unidades (0.278 solo vale con I en mm/h y A en km2). No son unidades
# imperiales ni de presentacion: `MH_hidrologia` nombra cada argumento con su
# unidad (`area_km2`, `tc_min`, `I_mm_h`) y entrega el caudal en m3/s.
#
# LAS CONSTANTES EMPIRICAS LLEVAN EL SUFIJO `_SI` (CLAUDE.md, «Unidades»): su
# valor depende del sistema de unidades y el que se transcribe es el METRICO
# que el Manual imprime. Cada una dice al lado su equivalente en unidades
# inglesas, que es como aparece en la bibliografia de origen, y por que NO se
# usa: el Manual ya las entrega convertidas, y mezclar una forma inglesa con
# longitudes en metros es el error clasico de estas formulas.

# --- num. 3.12.2, ecuacion (28): Q = 0,278 C I A -----------------------------
# 0.278 = 1/3.6: de (mm/h)·km2 a m3/s. El num. 4.1.2.1 b) escribe la misma
# expresion para la cuneta como C·I·A/3.6; el Manual redondea a tres cifras
# en la (28) y el programa usa el numero que la (28) imprime.
# Imperial equivalente, que NO se usa: Q[cfs] = C · I[in/h] · A[acres], con
# coeficiente 1 (1.008 exacto): es la forma del WSDOT Hydraulics Manual, ec.
# 2-3 (Kc = 1 «for English units»).
RACIONAL_COEFICIENTE_SI = 0.278             # m3/s por (mm/h · km2)
# Imperial: 1.008 en Q[cfs] = 1.008 · C · I[in/h] · A[acres], que la practica
# redondea a 1. NO se convierte de uno a otro con el pie: ninguno de los dos
# es una constante dimensional, los dos son un cambio de unidades DENTRO de su
# sistema (mm/h y km2 a m3/s; in/h y acres a cfs), y por eso el censo de
# `tests/test_dimensional_piloto.py` la lleva como «no cierra desde el
# comentario, y dice por que».
NUMERAL_RACIONAL = _reg.cita("MC_HHD.3.12.2").como_texto()
# «Muy usado para cuencas, A<10 Km2.» Desigualdad ESTRICTA: 10 km2 queda
# fuera. Caracter APROXIMACION (limite de validez), no prohibicion.
RACIONAL_AREA_MAX_KM2 = 10.0                # km2, EXCLUSIVO
NUMERAL_RACIONAL_AREA = _reg.cita("MC_HHD.3.12.2#AREA").como_texto()
# El num. 4.1.2.1 b) escribe el caudal de aporte de una cuneta como
# C·I·A/3.6. NO se transcribe ese 3.6 como constante: 1/3.6 = 0.2778 y la
# (28) imprime 0.278, y con los dos en el codigo la misma area daria dos
# caudales segun la puerta por la que entrase. La familia entera usa el de la
# (28); la cita de la cuneta se imprime en el paso.
NUMERAL_CUNETA_APORTE = _reg.cita("MC_HHD.4.1.2.1b").como_texto()
# Metodo racional modificado (num. 3.12.2.1), coeficiente de uniformidad,
# ecuacion (31): K = 1 + Tc^1.25 / (Tc^1.25 + 14), Tc en HORAS. Depende de la
# unidad de Tc y por eso es `_SI`; la formula es española (Temez) y no tiene
# forma inglesa en uso.
UNIFORMIDAD_TEMEZ_SI = {"exponente": 1.25, "sumando": 14}
NUMERAL_UNIFORMIDAD_TEMEZ = _reg.cita("MC_HHD.3.12.2.1#K").como_texto()

# --- Tabla Nº 08: coeficiente de escorrentia C -------------------------------
_T08 = _reg.tabla("MC_HHD.T08")
# (cobertura, suelo) -> {clase de pendiente: C}. Las claves salen del id de
# la fila («cobertura__suelo»); el numero, de su celda.
TABLA_08_COEFICIENTE_DE_ESCORRENTIA = {
    tuple(_T08.clave_corta(f).split("__")): dict(f.valores)
    for f in _T08.filas
}
# Las cinco columnas, de mayor a menor pendiente, con el UMBRAL que su rotulo
# imprime en tanto por uno y si la desigualdad impresa es «>» (True) o «<».
# Los umbrales son los de los rotulos de la pagina («> 50%», «> 20%»,
# «> 5%», «> 1%», «< 1%»): cuatro numeros para cinco columnas, porque la
# ultima se define por debajo del mismo 1 % que cierra la penultima.
TABLA_08_PENDIENTES = (
    ("pronunciada", 0.50), ("alta", 0.20), ("media", 0.05), ("suave", 0.01),
)
TABLA_08_PENDIENTE_MENOR = "despreciable"   # «< 1%»
NUMERAL_TABLA_08 = _reg.cita("MC_HHD.3.12.2#T08").como_texto()

# --- Tabla Nº 05: tiempo de concentracion (tc en MINUTOS) --------------------
# Kirpich (1940): tc = 0.01947 · L^0.77 · S^-0.385, L en m, S en m/m.
# Imperial equivalente, que NO se usa: tc[min] = 0.0078 · L[ft]^0.77 · S^-0.385.
TC_KIRPICH_SI = {"coeficiente": 0.01947, "exp_L": 0.77, "exp_S": -0.385}
# «pendientes empinadas (3 a 10%)»: la POBLACION de la que salio la formula
# (los dos extremos incluidos). La tabla la describe, no la impone: que se
# hace fuera de ella lo decide el criterio
# 'tc_fuera_de_la_poblacion_del_metodo'.
TC_KIRPICH_RANGO_S = (0.03, 0.10)           # m/m
# Los ajustes que la misma observacion manda: por 0.4 en flujo superficial
# sobre concreto o asfalto, por 0.2 en canales de concreto, ninguno en suelo
# descubierto ni en cunetas.
TC_KIRPICH_AJUSTES = {
    "ninguno": 1,
    "superficie_de_concreto_o_asfalto": 0.4,
    "canal_de_concreto": 0.2,
}
NUMERAL_TC_KIRPICH = _reg.cita("MC_HHD.3.9#T05_KIRPICH").como_texto()
# California Culverts Practice (1942): tc = 0.0195 · (L^3 / H)^0.385, L y H
# en m. La fila no escribe rango propio; se le aplica el de Kirpich (ver la
# `Interpretacion` de su cita). Imperial equivalente, que NO se usa:
# tc[min] = 60 · (11.9 · L[mi]^3 / H[ft])^0.385.
TC_CALIFORNIA_SI = {"coeficiente": 0.0195, "exp_L": 3, "exp": 0.385}
NUMERAL_TC_CALIFORNIA = _reg.cita("MC_HHD.3.9#T05_CALIFORNIA").como_texto()
# Federal Aviation Administration (1970): tc = 0.7035 · (1.1 − C) · L^0.50 /
# S^0.333, L en m, S en m/m, C el coeficiente del metodo racional. Imperial
# equivalente, que NO se usa: tc[min] = 1.8 · (1.1 − C) · L[ft]^0.5 / S[%]^0.333.
TC_FAA_SI = {"coeficiente": 0.7035, "resta_C": 1.1, "exp_L": 0.50,
             "exp_S": 0.333}
NUMERAL_TC_FAA = _reg.cita("MC_HHD.3.9#T05_FAA").como_texto()
# Ecuacion de retardo SCS (1973): tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 /
# S^0.5, L en m, S en m/m. Imperial equivalente, que NO se usa:
# tc[min] = 100 · L[ft]^0.8 · ((1000/CN) − 9)^0.7 / (1900 · S[%]^0.5).
TC_RETARDO_SCS_SI = {"coeficiente": 0.0136, "exp_L": 0.8, "mil": 1000,
                     "resta": 9, "exp_CN": 0.7, "exp_S": 0.5}
# «pequeñas cuencas urbanas con áreas inferiores a 800 Ha»: poblacion a la
# que se adapto, en km2 y EXCLUSIVA. Mismo trato que los 3 a 10 % de Kirpich.
TC_RETARDO_SCS_AREA_MAX_KM2 = 8.0
# El numero de curva es un indice entre 0 y 100; con CN = 100 el parentesis
# vale 1 y por debajo crece. Dominio de la formula, no umbral.
TC_RETARDO_SCS_CN_MAX = 100
NUMERAL_TC_RETARDO_SCS = _reg.cita("MC_HHD.3.9#T05_SCS").como_texto()
# Temez, ecuacion (30) del num. 3.12.2.1: Tc = 0.3 · (L / S^0.25)^0.76, con L
# en KM y Tc en HORAS. NO esta en la Tabla Nº 05. Sin forma inglesa en uso.
TC_TEMEZ_SI = {"coeficiente": 0.3, "exp_S": 0.25, "exp": 0.76}
# El rango del metodo del que la formula es pieza: «áreas menores de 770 km2
# y con tiempos de concentración (Tc) de entre 0.25 y 24 horas». Aqui la
# fuente SI escribe un rango de aplicacion del metodo, y fuera no se evalua.
TC_TEMEZ_RANGO_H = (0.25, 24.0)             # horas, los dos incluidos
TC_TEMEZ_AREA_MAX_KM2 = 770.0               # km2, EXCLUSIVO («menores de»)
NUMERAL_TC_TEMEZ = _reg.cita("MC_HHD.3.12.2.1#TC").como_texto()
NUMERAL_TABLA_05 = _reg.cita("MC_HHD.3.9#T05").como_texto()

# --- num. 3.8.1: de la precipitacion de 24 horas a la intensidad -------------
# Dick y Peschke, ecuacion (16): Pd = P24h · (d / 1440)^0.25, d en minutos.
DICK_PESCHKE = {"minutos_en_24_h": 1440, "exponente": 0.25}
NUMERAL_DICK_PESCHKE = _reg.cita("MC_HHD.3.8.1#DICK_PESCHKE").como_texto()
# Tabla Nº 04: horas -> coeficiente por el que se multiplica P24h.
_T04 = _reg.tabla("MC_HHD.T04")
TABLA_04_COEFICIENTES_DE_DURACION = {
    f.valores["duracion_h"]: f.valores["coeficiente"] for f in _T04.filas
}
NUMERAL_TABLA_04 = _reg.cita("MC_HHD.3.8.1#T04").como_texto()

# --- num. 3.7: ajuste de frecuencia y bondad de ajuste -----------------------
# Gumbel por momentos, las dos relaciones que la pag. impresa 29 imprime:
# alfa = 1.2825 / sigma ; beta = mu − 0.45 · sigma.
GUMBEL_MOMENTOS = {"alfa_por_sigma": 1.2825, "beta_resta_sigmas": 0.45}
NUMERAL_GUMBEL = _reg.cita("MC_HHD.3.7.1.7").como_texto()
NUMERAL_DISTRIBUCIONES = _reg.cita("MC_HHD.3.7.1").como_texto()
# Las ocho distribuciones que el num. 3.7.1 recomienda, con su rotulo
# impreso, y cuales trae el Manual con el estimador de sus parametros.
DISTRIBUCIONES_3_7_1 = {
    "normal": "Distribución Normal",
    "lognormal_2p": "Distribución Log Normal 2 parámetros",
    "lognormal_3p": "Distribución Log Normal 3 parámetros",
    "gamma_2p": "Distribución Gamma 2 parámetros",
    "gamma_3p": "Distribución Gamma 3 parámetros",
    "log_pearson_3": "Distribución Log Pearson tipo III",
    "gumbel": "Distribución Gumbel",
    "log_gumbel": "Distribución Log Gumbel",
}
DISTRIBUCIONES_CON_ESTIMADOR_IMPRESO = ("normal", "lognormal_2p", "gumbel")
# Tabla Nº 03: n -> {alfa: d critico}.
_T03 = _reg.tabla("MC_HHD.T03")
TABLA_03_KS = {
    f.valores["n"]: {0.10: f.valores["alfa_0_10"],
                     0.05: f.valores["alfa_0_05"],
                     0.01: f.valores["alfa_0_01"]}
    for f in _T03.filas
}
NUMERAL_KS = _reg.cita("MC_HHD.3.7.2b").como_texto()
# num. 3.4: «se recomienda contar con un mínimo de 25 años de registro».
REGISTRO_MINIMO_RECOMENDADO_ANIOS = 25
# El menor tamaño de muestra que la Tabla Nº 03 tabula. Por debajo no hay
# valor critico impreso con que juzgar el ajuste, y el calculo no se evalua.
KS_N_MINIMO_TABULADO = min(TABLA_03_KS)
NUMERAL_SERIE_HIDROLOGICA = _reg.cita("MC_HHD.3.4#FEN").como_texto()
NUMERAL_AVENIDA_DE_DISENO = _reg.cita("MC_HHD.3.13").como_texto()


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
    "ANCHO_MIN_DERECHO_VIA_M",   # piso [N] del derecho de via (DG-2018 Tabla
    "INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M",  # 304.09 y 304.07.02): V5 se
                                 # detiene antes, en 'ancho_derecho_via_m', y
                                 # elegir fila exige 'clase_de_via' (EXT-6)
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
# SULFATOS y EXPOSICION_ESPECIAL (la Tabla 4.2, que antes se referenciaba
# ademas desde un `CLORUROS_EXTERNOS` hoy retirado por no tener un solo
# consumidor) SALIERON de esta lista al entrar en el calculo (C07). Se
# declaraban aqui como "agresividad quimica: la decide el EMS del expediente,
# no este calculo", y era verdad a medias: el EMS decide el DATO, y con el
# dato las dos tablas si producen un numero que el calculo usa. Hoy
# `M9.requisitos_durabilidad_concreto` las combina por la nota al pie comun,
# de ahi sale la relacion a/c maxima, y de la a/c sale el factor que modifica
# el recubrimiento del refuerzo. El insumo -- 'exposicion_quimica_ems' -- es
# un [S] pendiente de ensayo, y mientras no llegue el calculo se detiene.


# ===========================================================================
# --- T-4 --- (cadena T, 2026-11-11) Materiales, espesores y durabilidad
# ===========================================================================
# CINCO VISTAS DE CALCULO Y UN [N]. Las cinco se DERIVAN del registro --no se
# copian-- y son de fuentes tecnicas [C] (AASHTO M 36, ASTM A796, WSDOT) o de
# una figura referencial de norma peruana (E.050): viven aqui por lo mismo
# que `HDS5_INLET`, que tampoco es [N]: son TABLAS, y lo que el proyecto
# ELIGE sobre ellas esta en `criterios_adoptados.py`
# ('corrugacion_y_espesor_tmc', 'D_max_norma_producto',
# 'sucs_fundacion_deficiente'). T13/T14 de `test_normativa` y
# `tests/test_t4_materiales_durabilidad.py` las contrastan con su tabla.

# ---- [N] EG-2013 Subseccion 507.10 «Aguas y Suelos agresivos», pag. 974 ---
# El unico umbral numerico de durabilidad de TUBERIA que la norma peruana
# escribe: con agua de pH menor de 5.8 «será necesario proteger la tubería»
# metalica corrugada (cita EG2013.507.10). EXIGE PROTEGER, no prohibe: la
# matriz de durabilidad (`M2.matriz_durabilidad`) lo aplica como REQUISITO
# sobre el TMC, que sigue candidato. El umbral a partir del cual el acero
# deja de ser alternativa aunque se proteja NO es peruano: es [C]
# ('durabilidad_tmc_umbrales', WSDOT §8-5).
PH_MIN_AGUA_TMC_SIN_PROTECCION = 5.8
NUMERAL_PH_MIN_TMC = ("EG-2013, Subseccion 507.10 'Aguas y Suelos agresivos', "
                      "pag. impresa 974")

# ---- Las corrugaciones de PLANCHA del catalogo de TMC, con su geometria ---
# Una entrada por (corrugacion, espesor especificado) de las Tablas 5, 7 y 9
# de ASTM A796/A796M-13 --68x13, 75x25 y 125x25 mm, las tres que AASHTO M 36
# Table 6 marca como estandar de 900 mm en adelante--, con la profundidad
# NOMINAL de la corrugacion tomada del rotulo de AASHTO M 36 Table 1.
#
#   clave               «68x13/2.01»: corrugacion / espesor en mm, como se
#                       imprime. Es lo que 'corrugacion_y_espesor_tmc' elige.
#   profundidad_m       profundidad nominal de la corrugacion, en METROS.
#   espesor_m           espesor especificado de la plancha, en METROS.
#   A_mm2_mm, I_mm4_mm, r_mm   area, inercia y radio de giro de la seccion
#                       por unidad de longitud, en las unidades de la tabla.
#                       Desde T-5 los consume la Fase 8 del TMC
#                       (`M8.verificar_tmc`, AASHTO LRFD 12.7.2), y viajan
#                       aqui para que no los vuelva a leer.
#   tabla               de que tabla del registro sale la fila.
#
# EL ESPESOR DE 1.02 mm NO ENTRA: la nota A de las Tablas 3 y 5 lo reserva al
# forro interior de la tuberia de doble pared o a tuberia temporal.
from src.dominios import MILIMETROS_POR_METRO  # noqa: E402  (bloque T-4)

_TABLAS_DE_PLANCHA_TMC = (("68x13", "ASTM_A796.T5"),
                          ("75x25", "ASTM_A796.T7"),
                          ("125x25", "ASTM_A796.T9"))


def _plancha_corrugada_tmc() -> dict:
    corrugaciones = _reg.tabla("AASHTO_M36.T1")
    vista = {}
    for corrugacion, tabla_id in _TABLAS_DE_PLANCHA_TMC:
        profundidad_mm = corrugaciones.fila(
            f"c{corrugacion}").valores["profundidad_nominal_mm"]
        for fila in _reg.tabla(tabla_id).filas:
            if fila.llamadas_a_nota:        # nota A: forro o tuberia temporal
                continue
            v = fila.valores
            vista[f"{corrugacion}/{fila.etiqueta_literal}"] = {
                "corrugacion": corrugacion,
                "profundidad_m": profundidad_mm / MILIMETROS_POR_METRO,
                "espesor_m": v["t_mm"] / MILIMETROS_POR_METRO,
                "A_mm2_mm": v["A"], "I_mm4_mm": v["I"], "r_mm": v["r"],
                "tabla": tabla_id,
            }
    return vista


TMC_PLANCHA_CORRUGADA = _plancha_corrugada_tmc()

# ---- En que diametros es ESTANDAR cada corrugacion: AASHTO M 36 Table 6 ---
# {corrugacion: (diametros nominales en mm con «X»)}. La nota a de la tabla
# dice que la X marca los tamaños de corrugacion estandar de cada diametro.
# De aqui sale el tope del TMC para la corrugacion adoptada: 2100 mm con
# 68x13 y 3600 mm con las dos de 25 mm de profundidad.
DIAMETROS_ESTANDAR_TMC = {
    corrugacion: tuple(
        fila.valores["dn_mm"] for fila in _reg.tabla("AASHTO_M36.T6").filas
        if fila.valores[f"c{corrugacion}"] == "X")
    for corrugacion, _tabla_id in _TABLAS_DE_PLANCHA_TMC
}
NUMERAL_DIAMETROS_ESTANDAR_TMC = ("AASHTO M 36-03 (2007), Table 6 'Pipe "
                                  "Sizes', pag. impresa M 36-11")

# ---- Los cuatro niveles de abrasion: WSDOT M 23-03.12, Table 8-4 [C] ------
# Las CLAVES con que el dato de entrada `abrasion` nombra el nivel del sitio
# (docs/contrato_entradas.md), en el orden de la tabla, de menor a mayor.
# El nivel es un dato de CAMPO; el programa no lo deduce de la velocidad.
NIVELES_DE_ABRASION = tuple(
    _reg.tabla("WSDOT_HM.T8-4").clave_corta(fila)
    for fila in _reg.tabla("WSDOT_HM.T8-4").filas)
NIVEL_DE_ABRASION_SEVERO = NIVELES_DE_ABRASION[-1]
NUMERAL_NIVELES_DE_ABRASION = ("WSDOT Hydraulics Manual M 23-03.12 (abril "
                               "2026), Table 8-4 'Pipe Abrasion Levels', "
                               "pags. impresas 8-27 y 8-28")

# ---- Los quince simbolos SUCS: E.050, Figura 3 (Referencial), pag. 31 -----
# En MAYUSCULAS, que es como se comparan: la figura imprime «Pt» y los
# ensayos lo escriben de las dos formas.
SIMBOLOS_SUCS = tuple(fila.valores["simbolo"].upper()
                      for fila in _reg.tabla("E050.FIG3").filas)
NUMERAL_SIMBOLOS_SUCS = ("NTE E.050, Figura 3 'Simbologia de Suelos "
                         "(Referencial)', pag. impresa 31")

# --- T-4 (auditoria adversarial, H2) --- EL MAYOR DIAMETRO DE TUBERIA DE
# CONCRETO CON DISEÑO ESTANDAR TABULADO en AASHTO M 170M-04. La serie de
# diametros designados de las Tablas 1 a 5 llega a 3600 mm, pero las filas
# por encima de 2700 mm llevan llamada a nota y rayas en lugar de pared y
# acero: son los «special designs» de la Seccion 7.2, que el fabricante
# propone con su espesor de pared y el propietario aprueba (citas
# AASHTO_M170M.7.2.1 y AASHTO_M170M.7.2.2, leidas por imagen; la lectura
# tabla a tabla esta en la nota de la primera). Es el tope del catalogo de
# concreto: por encima no hay pared que leer de la norma.
DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM = 2700
NUMERAL_DIAMETRO_MAX_ESTANDAR_M170M = (
    "AASHTO M 170M-04, Tablas 1 y 3 (pags. PDF 3 y 7): ultima fila con pared "
    "y acero tabulados; por encima, diseño especial de la Seccion 7.2, num. "
    "7.2.1 y 7.2.2 (pag. impresa M 170M-13)")


# ===========================================================================
# --- T-8 --- (cadena T) · proteccion de entrada y salida (M6)
# ===========================================================================
# Lo que M6 lee desde T-8, ademas de LAUSHEY_K y G_LAUSHEY: la Tabla Nº 11 del
# Manual (velocidades maximas admisibles en canales no revestidos), el apron
# de enrocado de HEC-14 Sec. 10.2, la hoya de socavacion de HEC-14 Cap. 5 y
# el geotextil de filtro de EG-2013 511.08. Cada bloque dice su pagina; las
# transcripciones estan en el registro (`normativa/citas.py`, bloque T-8, y
# `normativa/tablas.py`, MC_HHD.T11).
#
# NINGUN COEFICIENTE DE ESTE BLOQUE LLEVA SUFIJO `_SI` SALVO UNO, y no es un
# olvido de la regla «Unidades» de CLAUDE.md: las Ec. (10.4), (5.1) y (5.2) de
# HEC-14 son ADIMENSIONALES --sus grupos Q/(g^0.5·D^2.5), Q/(g^0.5·Rc^2.5) y
# ρV²/τc no tienen unidades-- y la fuente las escribe con los MISMOS
# coeficientes en SI y en unidades inglesas (sus ejemplos resueltos en los dos
# sistemas usan 0.2, 2.27, 316…). El unico que depende de unidades es αu de la
# Ec. (5.4), que la fuente tabula dos veces.

# --- Tabla Nº 11 (num. 4.1.1.3.6, pag. impresa 77, PDF 80) ------------------
# DERIVADA del registro, no copiada: una sola transcripcion (D2).
_T11 = _reg.tabla("MC_HHD.T11")
REGIMENES_DE_FLUJO_T11: Tuple[str, ...] = ("intermitente", "permanente")
V_MAX_NO_REVESTIDOS = {
    _T11.clave_corta(_f): {_r: _f.valores[_r] for _r in REGIMENES_DE_FLUJO_T11}
    for _f in _T11.filas}                                   # m/s
TERRENO_T11_ROTULO = {_T11.clave_corta(_f): _f.legible() for _f in _T11.filas}

# --- HEC-14 Sec. 10.2, apron de enrocado (pags. impresas 10-17 a 10-19) -----
# Ec. (10.4):  D50 = 0.2·D·[Q/(g^0.5·D^2.5)]^(4/3)·(D/TW)   (Fletcher y Grace)
HEC14_APRON_COEFICIENTE = 0.2
HEC14_APRON_EXPONENTE = 4.0 / 3.0
# «Tailwater depth for Equation 10.4 should be limited to between 0.4D and
# 1.0D. If tailwater is unknown, use 0.4D.»
HEC14_APRON_TW_SOBRE_D_MIN = 0.4
HEC14_APRON_TW_SOBRE_D_MAX = 1.0
# «Equation 10.4 assumes that the rock specific gravity is 2.65.»
HEC14_APRON_GRAVEDAD_ESPECIFICA_PIEDRA = 2.65
# Table 10.1 «Example Riprap Classes and Apron Dimensions»: clase, D50 (m),
# longitud del apron en multiplos de D («D is the culvert rise») y
# profundidad en multiplos de D50. La fuente la imprime en mm y en pulgadas;
# aqui va en metros.
HEC14_TABLA_10_1: Tuple[Tuple[int, float, float, float], ...] = (
    (1, 0.125, 4.0, 3.5),
    (2, 0.150, 4.0, 3.3),
    (3, 0.250, 5.0, 2.4),
    (4, 0.350, 6.0, 2.2),
    (5, 0.500, 7.0, 2.0),
    (6, 0.550, 8.0, 2.0),
)
# «Width (at apron end) = 3D + (2/3)L» (ejemplo resuelto, pag. impresa 10-19):
# el apron arranca con 3D de ancho en la boca y abre 1:3 por cada lado.
HEC14_APRON_ANCHO_EN_LA_BOCA_EN_D = 3.0
HEC14_APRON_ABOCINADO_POR_LONGITUD = 2.0 / 3.0

# --- HEC-14 Cap. 5, hoya de socavacion a la salida (pags. 5-1 a 5-7) --------
# Ec. (5.1), suelos NO cohesivos:
#   [hs, Ws, Ls]/Rc = Cs·Ch·(α/σ^(1/3))·[Q/(g^0.5·Rc^2.5)]^β·(t/316)^θ
# Table 5.1: (α, β, θ) por dimension de la hoya.
HEC14_SOCAVACION_NO_COHESIVO = {
    "profundidad": (2.27, 0.39, 0.06),
    "ancho":       (6.94, 0.53, 0.08),
    "longitud":    (17.10, 0.47, 0.10),
    "volumen":     (127.08, 1.24, 0.18),
}
HEC14_SOCAVACION_EXPONENTE_SIGMA = 1.0 / 3.0
# El tiempo de la ecuacion va en MINUTOS y se divide entre 316 (minutos).
HEC14_SOCAVACION_T_REFERENCIA_MIN = 316.0
# «…are not applicable for the first 30 minutes of the scour process» (5.1.2).
HEC14_SOCAVACION_T_MINIMO_MIN = 30.0
# «…occurs at a location approximately 0.4 Ls downstream of the culvert
# outlet» (5.1.1).
HEC14_SOCAVACION_FRACCION_LS_DEL_MAXIMO = 0.4
# Table 5.2, Ch por altura del fondo de la salida sobre el lecho, en
# diametros (Hd): filas 0, 1, 2 y 4.
HEC14_SOCAVACION_CH: Tuple[Tuple[float, dict], ...] = (
    (0.0, {"profundidad": 1.00, "ancho": 1.00, "longitud": 1.00, "volumen": 1.00}),
    (1.0, {"profundidad": 1.22, "ancho": 1.51, "longitud": 0.73, "volumen": 1.28}),
    (2.0, {"profundidad": 1.26, "ancho": 1.54, "longitud": 0.73, "volumen": 1.47}),
    (4.0, {"profundidad": 1.34, "ancho": 1.66, "longitud": 0.73, "volumen": 1.55}),
)
# Table 5.3, Cs por pendiente del conducto EN PORCENTAJE: filas 0, 2, 5 y
# «>7». La ultima fila se guarda con su borde, 7.0: vale para toda pendiente
# MAYOR que el 7 %.
HEC14_SOCAVACION_CS: Tuple[Tuple[float, dict], ...] = (
    (0.0, {"profundidad": 1.00, "ancho": 1.00, "longitud": 1.00, "volumen": 1.00}),
    (2.0, {"profundidad": 1.03, "ancho": 1.28, "longitud": 1.17, "volumen": 1.30}),
    (5.0, {"profundidad": 1.08, "ancho": 1.28, "longitud": 1.17, "volumen": 1.30}),
    (7.0, {"profundidad": 1.12, "ancho": 1.28, "longitud": 1.17, "volumen": 1.30}),
)
# Ec. (5.2) y (5.3), suelos COHESIVOS:
#   [hs, Ws, Ls]/D  = Cs·Ch·α ·(ρV²/τc)^β·(t/316)^θ     (circular)
#   [hs, Ws, Ls]/ye = Cs·Ch·αe·(ρV²/τc)^β·(t/316)^θ     (otras formas)
# Table 5.4: (α, β, θ, αe) por dimension de la hoya.
HEC14_SOCAVACION_COHESIVO = {
    "profundidad": (0.86, 0.18, 0.10, 1.37),
    "ancho":       (3.55, 0.17, 0.07, 5.63),
    "longitud":    (2.82, 0.33, 0.09, 4.48),
    "volumen":     (0.62, 0.93, 0.23, 2.48),
}
# «Equations 5.2 and 5.3 should be limited to sandy clay soils with a
# plasticity index of 5 to 16.»
HEC14_SOCAVACION_IP_MIN = 5.0
HEC14_SOCAVACION_IP_MAX = 16.0
# Ec. (5.4):  τc = 0.001·(Sv + αu)·tan(30 + 1.73·PI), angulo en GRADOS.
HEC14_TAU_C_COEFICIENTE = 0.001
HEC14_TAU_C_ANGULO_BASE_GRADOS = 30.0
HEC14_TAU_C_GRADOS_POR_IP = 1.73
# EL UNICO COEFICIENTE DEPENDIENTE DE UNIDADES DEL BLOQUE: «αu = unit
# conversion constant, 8630 N/m2 (SI), 180 lb/ft2 (CU)». Se usa el de SI, con
# Sv en N/m2 (Pa); el ingles NO se usa: el codigo opera en SI.
HEC14_TAU_C_ALFA_U_SI = 8630.0      # N/m2
# Imperial: 180 lb/ft2 (CU), el que la fuente escribe al lado y NO se usa.
# Es la misma presion: 180 lbf/ft2 · 4.44822 N/lbf / 0.3048^2 m2/ft2 = 8618.4
# N/m2, un 0.14 % bajo el 8630 impreso (la fuente redondea uno de los dos).
# El ejemplo resuelto de la pag. impresa 5-8 usa 8630 y da tau_c = 39.9 N/m2.

# --- EG-2013, Tabla 511-06 (num. 511.08, pag. impresa 1015, PDF 1023) -------
# Geotextil para control permanente de erosion, por el porcentaje de suelo in
# situ que pasa el tamiz N.º 200: (rotulo de la columna, techo del intervalo
# en %, permitividad minima en s-1, tamaño de abertura aparente maximo en mm).
# La ultima columna («> 50») no tiene techo: va con `None`.
GEOTEXTIL_EROSION_T511_06: Tuple[tuple, ...] = (
    ("< 15", 15.0, 0.7, 0.43),
    ("15-50", 50.0, 0.2, 0.25),
    ("> 50", None, 0.1, 0.22),
)
GEOTEXTIL_EROSION_CLASE = ("Clase 1 de la Tabla 511-01 (Clase 2 para "
                           "geotextiles tejidos de monofilamento)")
# Nota (5) b de la misma tabla: «Para los suelos cohesivos con un índice de
# plasticidad mayor a 7, el valor máximo promedio por rollo (VMPR) es de 0.30
# mm». El proyecto la aplica SOLO en la columna «>50», cuya celda «0,22(5)»
# lleva la llamada, y no en las otras dos, donde relajaria (15-50: 0.25 ->
# 0.30) lo que la celda fija. Es una LECTURA, declarada como `Interpretacion`
# de la cita EG2013.511.08#T511_06, porque el rotulo de la fila tambien lleva
# un «(5)»: la sostiene la Tabla 511-02 de la misma Seccion, que trae las dos
# notas con numeros distintos y pone la de los suelos cohesivos solo en la
# celda (cita EG2013.511.05#T511_02_NOTA_5). Decision del dueño del
# 2026-11-12, hasta conseguir AASHTO M 288, que no esta en normas/.
GEOTEXTIL_EROSION_IP_COHESIVO = 7.0
GEOTEXTIL_EROSION_TAA_COHESIVO_MM = 0.30
# El exponente del diametro (o del radio hidraulico) en el grupo de caudal
# adimensional de las Ec. (10.4) y (5.1): Q / (g^0.5 · D^2.5).
HEC14_EXPONENTE_LONGITUD_DEL_CAUDAL_ADIMENSIONAL = 2.5
# Table 1.1 «Energy Dissipators and Limitations», nota 8 de la fila «Riprap
# apron» (pag. impresa 1-2, PDF 15): «Culvert rise less than or equal to 1500
# mm (60 in)». La Sec. 10.2 lo repite como poblacion: «primarily for culverts
# 1500 mm (60 in) or smaller» (pag. impresa 10-16, PDF 217).
#
# LA FUENTE DA LAS DOS CIFRAS Y NO SON LA MISMA: 60 in = 1.524 m, 24 mm mas
# que los 1500 mm. Rige 1.524 m, y es una LECTURA DECLARADA (decision del
# dueño del 2026-11-12): es la que deja evaluar el ejemplo resuelto de la
# propia fuente, que en unidades inglesas usa D = 5.0 ft = 60 in (pag.
# impresa 10-19, PDF 220). Con 1.500 m ese ejemplo salia «no evaluable», y un
# limite que deja fuera el ejemplo de quien lo escribe esta mal transcrito.
# Ningun diametro de la progresion cae entre los dos (va de 0.15 en 0.15 m:
# 1.50 entra con las dos cifras y 1.65 no entra con ninguna).
# Imperial: 60 in, el que la fuente escribe al lado. 60·0.0254 = 1.524 m.
HEC14_APRON_ALTURA_MAX_M = 1.524
# El PISO del espesor de la capa de enrocado en HEC-14, en veces el D50:
# «at least 2D50 thick» (poza, Sec. 10.1, pag. impresa 10-1) y «to a limit
# of 2.0D50» (apron, Sec. 10.2, pag. impresa 10-18).
HEC14_ESPESOR_MIN_EN_D50 = 2.0


# ===========================================================================
# --- T-5 --- (cadena T, 2026-11-12) Fase 8: estructural del conducto
# ===========================================================================
# DOS CLASES DE NUMERO EN ESTE BLOQUE, y no se mezclan:
#
#   [N]  los del Manual de Puentes (HL-93, presencia multiple, IM de
#        componentes enterrados, pesos especificos) y del EG-2013 (espesor
#        minimo de la tuberia metalica corrugada): norma peruana vigente.
#   [C]  VISTAS DE TABLA de AASHTO LRFD 9a ed., Seccion 12, y de ASTM
#        A796/A796M-13, con el mismo regimen que las vistas de T-4: son
#        TABLAS de una fuente tecnica reconocida; lo que el proyecto ELIGE
#        sobre ellas (el tipo de instalacion, la fabricacion del TMC, el
#        relleno del HDPE, la importancia operativa) esta en
#        `criterios_adoptados.py`, bloque «--- T-5 ---».
#
# Las cifras se escriben EN LA UNIDAD QUE LA FUENTE IMPRIME (kip, ft, in,
# ksi, psi, pcf, in/kip) y se convierten a SI una sola vez, aqui debajo, con
# los factores exactos de `constantes_fisicas`. Cada pagina se leyo en la
# sesion de T-5 (por texto las de AASHTO, el Manual de Puentes y EG-2013;
# por imagen las de ASTM A796) y la cita del registro que la sostiene esta
# nombrada en el comentario de cada bloque.
# ===========================================================================
from src.constantes_fisicas import (KCF_EN_KN_M3, KIP_EN_KN,  # noqa: E402
                                    KSI_EN_MPA, PCF_EN_KN_M3,  # (bloque T-5)
                                    PIE_EN_METROS, PSI_EN_KPA,
                                    PULGADA_EN_MM)

_M_POR_PULG = PULGADA_EN_MM / MILIMETROS_POR_METRO

# ---- [N] HL-93: camion y tandem de diseño (Manual de Puentes) -------------
# 2.4.3.2.2.2 «Camión de Diseño» y 2.4.3.2.2.3 «Tándem de Diseño», pag.
# impresa 104 (PDF 105); citas MP.2.4.3.2.2.2 y MP.2.4.3.2.2.3. El Manual
# escribe kip y ft y pone entre parentesis una equivalencia REDONDEADA
# (14.55 t, 4.27 m, 1.20 m, 1.80 m); se convierte el valor primario con el
# factor exacto: 32.0 kip = 142.34 kN (las «14.55 t» darian 142.69 kN).
# Para alcantarillas solo cuentan los EJES (AASHTO 3.6.1.2.6a, cita
# AASHTO_LRFD_9.3.6.1.2.6a#EJES): no hay carga de carril.
EJE_CAMION_HL93_KIP = 32.0
EJE_TANDEM_HL93_KIP = 25.0
SEPARACION_EJES_CAMION_MIN_PIE = 14.0     # el minimo de 14 a 30 ft: el que
                                          # acerca los ejes y gobierna
SEPARACION_EJES_TANDEM_PIE = 4.0
SEPARACION_RUEDAS_PIE = 6.0               # transversal, los dos vehiculos
EJE_CAMION_HL93_KN = EJE_CAMION_HL93_KIP * KIP_EN_KN
EJE_TANDEM_HL93_KN = EJE_TANDEM_HL93_KIP * KIP_EN_KN
SEPARACION_EJES_CAMION_MIN_M = SEPARACION_EJES_CAMION_MIN_PIE * PIE_EN_METROS
SEPARACION_EJES_TANDEM_M = SEPARACION_EJES_TANDEM_PIE * PIE_EN_METROS
SEPARACION_RUEDAS_M = SEPARACION_RUEDAS_PIE * PIE_EN_METROS
NUMERAL_HL93_EJES = ("Manual de Puentes, num. 2.4.3.2.2.2 «Camión de Diseño» "
                     "y 2.4.3.2.2.3 «Tándem de Diseño», pag. impresa 104")

# ---- [N] Area de contacto del neumatico: 2.4.3.2.2.5, pag. impresa 104 ----
# 20.0 in de ancho (transversal) por 10.0 in de largo (longitudinal); son
# los w_t y l_t de AASHTO 3.6.1.2.6b. Cita MP.2.4.3.2.2.5.
ANCHO_NEUMATICO_PULG = 20.0
LARGO_NEUMATICO_PULG = 10.0
ANCHO_NEUMATICO_M = ANCHO_NEUMATICO_PULG * _M_POR_PULG
LARGO_NEUMATICO_M = LARGO_NEUMATICO_PULG * _M_POR_PULG

# ---- [N] Presencia multiple: Tabla 2.4.3.2.2.6-1, pag. impresa 105 --------
# Un carril cargado: m = 1.20. Para alcantarillas con trafico paralelo al
# vano AASHTO 3.6.1.2.6a manda UN carril con su factor (cita
# AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL). Cita MP.2.4.3.2.2.6.
PRESENCIA_MULTIPLE_UN_CARRIL = 1.20

# ---- [N] IM de componentes enterrados: 2.4.3.3.2, pag. impresa 109 --------
# IM = 33 (1.0 - 0.125 D_E) >= 0 %, con D_E en PIES (el Manual conserva la
# unidad de AASHTO 3.6.2.2). La pendiente en SI es 0.125/0.3048 = 0.4101 por
# metro; NO se usa 0.125 sobre metros, que daria un IM casi tres veces mas
# alto a la misma profundidad. Cita MP.2.4.3.3.2.
IM_ENTERRADO_MAXIMO_PCT = 33.0
IM_ENTERRADO_PENDIENTE_POR_PIE = 0.125
IM_ENTERRADO_PENDIENTE_SI = IM_ENTERRADO_PENDIENTE_POR_PIE / PIE_EN_METROS

# ---- [N] Pesos especificos: Tabla 2.4.2.1-1, pag. impresa 102 -------------
# «A falta de una información precisa, podrán usarse...» (PERMISO; cita
# MP.2.4.2.1#PESOS). Dos filas: «Arena, limo o arcilla compactado» 0.120 kcf
# para el relleno sobre el conducto y «Superficies de desgaste bituminosos»
# 0.140 kcf (la misma cifra que «Laminados grava, macadam, o de lastre»)
# para el paquete estructural. Que fila describe cada capa es lectura del
# proyecto, y la dice el paso de la carga de tierra.
PESO_SUELO_COMPACTADO_KCF = 0.120
PESO_PAQUETE_ESTRUCTURAL_KCF = 0.140
PESO_SUELO_COMPACTADO_KN_M3 = PESO_SUELO_COMPACTADO_KCF * KCF_EN_KN_M3
PESO_PAQUETE_ESTRUCTURAL_KN_M3 = PESO_PAQUETE_ESTRUCTURAL_KCF * KCF_EN_KN_M3

# ---- [N] EG-2013 Tabla 507-01 «Espesores Mínimos de Alcantarillas ---------
# Circulares y Abovedadas», pag. impresa 970 (PDF 978): {diametro mm:
# espesor minimo mm}. Es la UNICA cifra peruana sobre el calibre del TMC, y
# hasta T-5 no la leia nadie (la ficha de cama de 507 la mencionaba de paso).
# Cinco filas, de 0.60 a 1.80 m; para los diametros intermedios del catalogo
# rige la fila del diametro tabulado inmediato SUPERIOR (lectura del
# proyecto, del lado del mayor espesor), y por encima de 1.80 m la tabla no
# dice nada: ahi gobierna solo el procedimiento. Cita EG2013.T507-01.
ESPESOR_MIN_TMC_EG2013_MM = {600: 1.80, 900: 2.00, 1200: 2.50, 1500: 3.00,
                             1800: 3.30}

# ---- [C] Tabla 3.6.1.2.6a-1 de AASHTO LRFD (pag. 3-27): LLDF -------------
# «Concrete Pipe with fill depth 2.0 ft or greater»: 1.15 para diametro de
# 2.0 ft o menos, 1.75 para 8.0 ft o mas, interpolacion lineal entre medias;
# «All other culverts and buried structures»: 1.15. Cita
# AASHTO_LRFD_9.T3.6.1.2.6a-1.
LLDF_TUBO_CONCRETO_D_MIN_M = 2.0 * PIE_EN_METROS
LLDF_TUBO_CONCRETO_D_MAX_M = 8.0 * PIE_EN_METROS
LLDF_TUBO_CONCRETO_MIN = 1.15
LLDF_TUBO_CONCRETO_MAX = 1.75
LLDF_OTRAS_ALCANTARILLAS = 1.15
# 3.6.1.2.6a (pag. 3-26): el metodo de la rueda distribuida vale con relleno
# de MAS de 1.0 ft (no-concreto) o de 2.0 ft O MAS (tubo de concreto), y la
# carga viva se desprecia con relleno de mas de 8.0 ft que ademas supera la
# luz (alcantarilla de un solo vano). Citas AASHTO_LRFD_9.3.6.1.2.6a#RELLENO
# y #DESPRECIABLE.
RELLENO_MIN_METODO_NO_CONCRETO_M = 1.0 * PIE_EN_METROS
RELLENO_MIN_METODO_TUBO_CONCRETO_M = 2.0 * PIE_EN_METROS
RELLENO_DESPRECIA_CARGA_VIVA_M = 8.0 * PIE_EN_METROS

# ---- [C] Tubo de concreto: AASHTO LRFD 12.10 (pags. 12-50 a 12-66) --------
# VAF = Fe de las instalaciones estandar (Tabla 12.10.2.1-3, pag. 12-53;
# cita AASHTO_LRFD_9.12.10.2.1#VAF); peso del suelo nunca menor de
# 110 lb/ft3 (12.10.2.1, pag. 12-52; cita #PESO_MIN); factor de instalacion
# 1.10 para el Tipo 1 (12.10.4.3.1, pag. 12-64; cita #TIPO1).
VAF_INSTALACION_ESTANDAR = {"tipo_1": 1.35, "tipo_2": 1.40, "tipo_3": 1.40,
                            "tipo_4": 1.45}
PESO_SUELO_MIN_TUBO_CONCRETO_PCF = 110.0
PESO_SUELO_MIN_TUBO_CONCRETO_KN_M3 = (PESO_SUELO_MIN_TUBO_CONCRETO_PCF
                                      * PCF_EN_KN_M3)
FACTOR_INSTALACION_TIPO_1 = 1.10
# Tabla 12.10.4.3.2a-1 «Bedding Factors for Circular Pipe» (pag. 12-65):
# B_FE por diametro (in) y tipo; entre filas se interpola (12.10.4.3.2a).
BFE_DIAMETROS_PULG = (12.0, 24.0, 36.0, 72.0, 144.0)
BFE_POR_TIPO = {"tipo_1": (4.4, 4.2, 4.0, 3.8, 3.6),
                "tipo_2": (3.2, 3.0, 2.9, 2.8, 2.8),
                "tipo_3": (2.5, 2.4, 2.3, 2.2, 2.2),
                "tipo_4": (1.7, 1.7, 1.7, 1.7, 1.7)}
# Tabla 12.10.4.3.2c-1 «Bedding Factors, BFLL» (pag. 12-66): por diametro
# (in) y por relleno menor de 2.0 ft o desde 2.0 ft; «30 and larger» = 2.2.
BFLL_DIAMETROS_PULG = (12.0, 18.0, 24.0, 30.0)
BFLL_RELLENO_MENOR_2_PIES = (3.2, 3.2, 3.2, 2.2)
BFLL_RELLENO_DESDE_2_PIES = (2.4, 2.4, 2.4, 2.2)

# ---- [C] Tubo de acero corrugado: AASHTO LRFD 12.5, 12.7 y A12 ------------
# Propiedades del acero, Tabla A12-9 (pag. 12-107): F_u 45.0 ksi, F_y 33.0
# ksi, E_m 29 000 ksi. Factores de resistencia, Tabla 12.5.5-1 (pag. 12-12):
# area de pared y pandeo 1.00, costura longitudinal 0.67. Rigidez del suelo
# k = 0.22 (12.7.2.4, pag. 12-26). Limite del factor de flexibilidad, Tabla
# 12.5.6.1-1 (pag. 12-13), en in/kip por PROFUNDIDAD de corrugacion: 0.25 y
# 0.5 in -> 43; 1.0 in -> 33. Citas AASHTO_LRFD_9.TA12-9, .12.5.5,
# .12.7.2.4, .12.5.6.1#FF.
ACERO_TMC_FU_MPA = 45.0 * KSI_EN_MPA
ACERO_TMC_FY_MPA = 33.0 * KSI_EN_MPA
ACERO_TMC_EM_MPA = 29000.0 * KSI_EN_MPA
PHI_AREA_Y_PANDEO_TMC = 1.00
PHI_COSTURA_LONGITUDINAL_TMC = 0.67
K_RIGIDEZ_SUELO_TMC = 0.22
FF_LIMITE_ACERO_IN_KIP = {"68x13": 43.0, "75x25": 33.0, "125x25": 33.0}
FF_LIMITE_ACERO_MM_N = {c: v * PULGADA_EN_MM / (KIP_EN_KN * 1000.0)
                        for c, v in FF_LIMITE_ACERO_IN_KIP.items()}
# F_min = 15/(12 S) >= 1 (Eq. 12.7.2.2-4, S en ft): el 15 son PULGADAS.
F_MIN_NUMERADOR_M = 15.0 * _M_POR_PULG
# ASTM A796/A796M-13 num. 4 y 8 (por imagen, PDF 2 a 4): las cifras SI de
# la practica, para el CONTRASTE ASD (no rige): f_y 225 MPa, f_u 310 MPa,
# E 200 000 MPa ("all other corrugations"), SF 2 sobre el area de pared.
A796_FY_MPA = 225.0
A796_FU_MPA = 310.0
A796_E_MPA = 200000.0
A796_SF_AREA = 2.0
A796_K_SUELO = 0.22

# ---- [C] Polietileno corrugado: AASHTO LRFD 12.12 -------------------------
# Tabla 12.12.3.3-1 (pag. 12-77), fila «Corrugated PE Pipe - AASHTO M 294»:
# deformacion limite de traccion de servicio 5.0 %, de compresion mayorada
# 4.1 %; F_u y E inicial 3.0 / 110.0 ksi, a 50 anos 0.90 / 22, a 75 anos
# 0.90 / 21. Cita AASHTO_LRFD_9.T12.12.3.3-1.
PE_M294_EPS_YT = 0.050
PE_M294_EPS_YC = 0.041
PE_M294_PROPIEDADES_KSI = {"inicial": (3.0, 110.0), "50": (0.90, 22.0),
                           "75": (0.90, 21.0)}
# Tabla 12.12.3.10.1b-1 «Time Factor» (pag. 12-85), columna PE.
KT_PE = {"inicial": 0.9, "50": 0.3, "75": 0.25}
# Tabla 12.5.5-1, «PE and PVC pipe»: empuje 1.00, rigidez del suelo 0.90,
# pandeo global 0.70.
PHI_EMPUJE_PE = 1.00
PHI_SUELO_PE = 0.90
PHI_PANDEO_PE = 0.70
# 12.12.3.10.1e (pag. 12-87): C_n = 0.55; K_2 = 1.0 para el empuje en el
# arranque (12.12.3.5, pag. 12-79).
CN_PANDEO_PE = 0.55
K2_EMPUJE_ARRANQUE = 1.0
# Tabla 12.12.3.5-1 «Ms Based on Soil Type and Compaction Condition» (pag.
# 12-81), en ksi, por nivel de P_sp en psi. Las columnas son las cuatro que
# la compactacion del EG-2013 admite (ver 'relleno_estructural_hdpe').
MS_NIVELES_PSP_PSI = (1.0, 5.0, 10.0, 20.0, 40.0, 60.0)
MS_TABLA_KSI = {"Sn-100": (2.350, 3.450, 4.200, 5.500, 7.500, 9.300),
                "Sn-95": (2.000, 2.600, 3.000, 3.450, 4.250, 5.000),
                "Si-95": (1.415, 1.670, 1.770, 1.880, 2.090, None),
                "Cl-95": (0.530, 0.625, 0.690, 0.740, 0.815, 0.895)}
# AASHTO M 294-11 num. 7.7 (traduccion no oficial, hoja 8): la capacidad de
# compresion del perfil no puede ser inferior al 50 % del area bruta por el
# limite elastico minimo especificado. Cita AASHTO_M294_TRAD.7.7.
M294_FRACCION_CAPACIDAD_COMPRESION = 0.5

# ---- [C] Marco de concreto: AASHTO LRFD 12.11.2.2.1 (pag. 12-69) ----------
# F_e = 1 + 0.20 H/B_c, que no puede pasar de 1.15 con relleno compactado a
# los lados ni de 1.40 sin compactar. Cita AASHTO_LRFD_9.12.11.2.2.1.
FE_CAJON_MAX_COMPACTADO = 1.15
FE_CAJON_MAX_SIN_COMPACTAR = 1.40

# ---- [C] El perfil MINIMO del PE corrugado por diametro designado ---------
# DERIVADO de la Table A12-11 de AASHTO LRFD (pag. 12-108, tabla
# AASHTO_LRFD_9.TA12-11) y de la serie de M 294 (AASHTO_M294_TRAD.T7.2.2,
# que dice que «900 (36)» es el designado de 36 in): {mm: {...}} en SI. Son
# los MINIMOS de producto (Min. A, Min. c, Min. I) y el exterior MAXIMO: la
# Fase 8 verifica el perfil mas debil que la norma admite. Se derivan las
# ocho filas; el catalogo recorre solo las de 900 mm en adelante (su piso), y
# 1350 y 1500 mm no estan en la tabla: la Fase 8 no las alcanza porque el
# espesor de pared del HDPE ('espesor_pared_conducto', T-4) tampoco las trae
# y la geometria se detiene antes. `nota_largo_plazo` marca las filas con la
# llamada «*» de la tabla (42 y 48 in): «the wall thickness should be
# designed using the long-term tensile strength provision».
_MM2_POR_MM_POR_PULG2_PIE = PULGADA_EN_MM ** 2 / (PIE_EN_METROS
                                                 * MILIMETROS_POR_METRO)
_MM4_POR_MM_POR_PULG4_PULG = PULGADA_EN_MM ** 3


def _perfil_minimo_pe_m294() -> dict:
    designado_mm = {f.valores["dn_in"]: f.valores["dn_mm"]
                    for f in _reg.tabla("AASHTO_M294_TRAD.T7.2.2").filas}
    vista = {}
    for fila in _reg.tabla("AASHTO_LRFD_9.TA12-11").filas:
        v = fila.valores
        dn_mm = designado_mm[v["nominal_in"]]
        vista[dn_mm] = {
            "nominal_in": v["nominal_in"],
            "id_min_m": v["id_min_in"] * _M_POR_PULG,
            "od_max_m": v["od_max_in"] * _M_POR_PULG,
            "A_mm2_mm": v["A_min"] * _MM2_POR_MM_POR_PULG2_PIE,
            "c_mm": v["c_min"] * PULGADA_EN_MM,
            "I_mm4_mm": v["I_min"] * _MM4_POR_MM_POR_PULG4_PULG,
            "nota_largo_plazo": bool(fila.llamadas_a_nota),
        }
    return vista


PE_M294_PERFIL_MINIMO = _perfil_minimo_pe_m294()

# ---- [C] Resistencia ultima de la costura longitudinal REMACHADA del TMC --
# DERIVADA de las columnas de costura de las Tablas 5 y 7 de ASTM A796/A796M-13
# (PDF 8 y 9, por imagen; «Ultimate Longitudinal Seam Strength of Riveted or
# Spot Welded Corrugated Steel Pipe in kN per m of Seam»), por plancha de
# `TMC_PLANCHA_CORRUGADA`: {clave: {"simple": kN/m o None, "doble": ...}}.
# Cada espesor trae un solo diametro de remache con valor (8 mm hasta 2.01 mm
# y 10 mm desde 2.77 en la de 68 x 13; 10 u 11 mm dobles en la de 75 x 25);
# la celda «. . .» es una combinacion que no se fabrica y queda None. La de
# 125 x 25 es solo helicoidal (titulo de la Tabla 9): no tiene costura.
_COLUMNAS_COSTURA_TMC = {
    "ASTM_A796.T5": {"simple": ("s8_single", "s10_single"),
                     "doble": ("s8_double", "s10_double")},
    "ASTM_A796.T7": {"simple": (), "doble": ("s10_double", "s11_double")},
    "ASTM_A796.T9": {"simple": (), "doble": ()},
}


def _costura_remachada_tmc() -> dict:
    vista = {}
    for clave, plancha in TMC_PLANCHA_CORRUGADA.items():
        etiqueta = clave.split("/")[1]
        fila = next(f for f in _reg.tabla(plancha["tabla"]).filas
                    if f.etiqueta_literal == etiqueta)
        vista[clave] = {}
        for remache, columnas in _COLUMNAS_COSTURA_TMC[plancha["tabla"]].items():
            con_valor = [float(fila.valores[c]) for c in columnas
                         if isinstance(fila.valores[c], (int, float))]
            if len(con_valor) > 1:
                raise ValueError(
                    f"{clave}: la tabla da costura {remache} con dos remaches; "
                    "cual se fabrica es una eleccion que esta vista no hace")
            vista[clave][remache] = con_valor[0] if con_valor else None
    return vista


COSTURA_REMACHADA_TMC_KN_M = _costura_remachada_tmc()


# ===========================================================================
# --- T-5 (cierre) --- Lo que sumaron las dos auditorias adversariales
# ===========================================================================
# [C] El limite del factor de flexibilidad del tubo TERMOPLASTICO: AASHTO
# LRFD 9a ed., Art. 12.5.6.3, pag. impresa 12-14 (PDF 1652): «Flexibility
# factor, FF, of thermoplastic and fiberglass pipe shall not exceed 95.0
# in./kip» (cita AASHTO_LRFD_9.12.5.6.3). El de la FASE A solo traia los del
# acero (Tabla 12.5.6.1-1) y el HDPE no verificaba su FF.
FF_LIMITE_TERMOPLASTICO_IN_KIP = 95.0
FF_LIMITE_TERMOPLASTICO_MM_N = (FF_LIMITE_TERMOPLASTICO_IN_KIP * PULGADA_EN_MM
                                / (KIP_EN_KN * 1000.0))

# [C] El PRIMER diametro interior que AASHTO M 170M-04 tabula para cada clase,
# mm (Tablas 1 a 5, primera fila de cada una; PDF 3, 4, 6, 8 y 10, leidas por
# imagen; cita AASHTO_M170M.T1#DIAMETROS). La Clase I empieza en 1500 mm: por
# debajo la norma no la ofrece, y `M8.verificar_concreto` tampoco. Sin esto,
# completar 'clases_producto_por_relleno' con la D-load de la Clase I hacia
# que un tubo de 0.90 m saliera «Clase I» (auditoria de T-5).
DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM = {"I": 1500, "II": 300, "III": 300,
                                            "IV": 300, "V": 300}


# ===========================================================================
# --- T-3 --- (cadena T, auditoria adversarial, H1) La fila del MARCO de la
# Tabla B.1 del HDS-5
# ===========================================================================
# «Concrete Boxes | Smooth | 0.012-0.015 | FHWA 1961», HDS-5 3a ed., Table B.1,
# pag. impresa B.6 (PDF 208). Es el par (n_min, n_max) del valor de archivo de
# 'n_manning_cajon' [C], y NO se escribe a mano: se LEE de la fila transcrita
# del registro (`HDS5_3ED.TB.1#concrete_boxes`), por lo mismo que `MANNING` se
# deriva de `TABLA_09_FILAS` y 'n_manning_hdpe' de su propia fila. Vive aqui,
# junto a `KE_HDS5_C2` y `HDS5_INLET` -- las otras dos tablas del HDS-5 que el
# marco consume --, porque los valores de una tabla son de la tabla; cual fila
# aplica a esta obra es el criterio. La Tabla N 09 no tiene fila de seccion
# rectangular, de modo que esta fila no compite con una [N]: cubre su vacio.
_TB1 = _reg.tabla("HDS5_3ED.TB.1")
MANNING_CAJON_HDS5 = {
    _TB1.clave_corta(fila): (float(fila.valores["n_min"]),
                             float(fila.valores["n_max"]))
    for fila in _TB1.filas
    if _TB1.clave_corta(fila) == "concrete_boxes"
}


# ===========================================================================
# --- T-9 --- (cadena T) · espaciamiento de alivios: la cuneta (M10)
# ===========================================================================
# Lo que M10 lee desde T-9 para calcular la capacidad de la cuneta y avisar de
# su pendiente. Las tres tablas son DERIVADAS del registro, no copiadas
# (`normativa/tablas.py`, bloque T-9): una sola transcripcion (D2).

# --- Tabla Nº 32 (num. 4.1.2.1 a), pag. impresa 175, PDF 178) --------------
# Coeficiente de Strickler K = 1/n de la cuneta, por tipo de cuneta. En SI:
# Q = K·A·Rh^(2/3)·S^(1/2) con Q en m3/s, A en m2 y Rh en m. No lleva sufijo
# `_SI` porque no es un coeficiente empirico que cambie con el sistema: es
# la tabla de rugosidad, y la Tabla Nº 32 la escribe para la ecuacion (117)
# en metros.
_T32 = _reg.tabla("MC_HHD.T32")
CUNETA_STRICKLER_T32 = {_T32.clave_corta(_f): _f.valores["K"]
                        for _f in _T32.filas}                 # m^(1/3)/s
CUNETA_T32_ROTULO = {_T32.clave_corta(_f): _f.etiqueta_literal
                     for _f in _T32.filas}

# --- Tabla Nº 33 (num. 4.1.2.1 a), pag. impresa 175, PDF 178) --------------
# Velocidad limite admisible por tipo de superficie: el INTERVALO que la
# fuente imprime (minimo, maximo). Cual de los dos rige es el criterio
# 'lectura_velocidad_limite_cuneta' [A]; la fila, 'revestimiento_cuneta' [A].
_T33 = _reg.tabla("MC_HHD.T33")
CUNETA_VELOCIDAD_LIMITE_T33 = {
    _T33.clave_corta(_f): tuple(_f.valores["velocidad"].valores)
    for _f in _T33.filas}                                     # m/s
CUNETA_T33_ROTULO = {_T33.clave_corta(_f): _f.etiqueta_literal
                     for _f in _T33.filas}
CUNETA_T33_MUY_CORTA_DURACION = tuple(
    _T33.clave_corta(_f) for _f in _T33.filas if "*" in _f.llamadas_a_nota)

# --- Tabla Nº 34 (num. 4.1.2.1 c), pag. impresa 178, PDF 181) --------------
# Dimensiones MINIMAS de la cuneta triangular por region pluvial:
# (profundidad d, ancho a), en m. Es la ventana del criterio
# 'seccion_cuneta'; ninguna fila se adopta.
_T34 = _reg.tabla("MC_HHD.T34")
CUNETA_DIMENSIONES_MINIMAS_T34 = {
    _T34.clave_corta(_f): (_f.valores["profundidad_m"], _f.valores["ancho_m"])
    for _f in _T34.filas}                                     # m

# --- num. 4.1.2 c), pag. impresa 172, PDF 175 ------------------------------
# «La pendiente longitudinal (i) debe estar comprendida entre la condición de
# autolimpieza y la que produciría velocidades erosivas, es decir:
# 0.5 % < i < 2 %». Desigualdades estrictas; m/m.
PENDIENTE_DRENAJE_LONGITUDINAL = (0.005, 0.02)
NUMERAL_PENDIENTE_DRENAJE_LONGITUDINAL = _reg.cita("MC_HHD.4.1.2c").como_texto()
# DG-2018 num. 304.11 (pag. impresa 208, PDF 209): «Las pendientes
# longitudinales mínimas absolutas serán 0.2%, para cunetas revestidas y 0.5%
# para cunetas sin revestir». Discrepa del minimo del Manual para la cuneta
# revestida; el programa no elige entre las dos: solo las imprime en el aviso.
PENDIENTE_MIN_CUNETA_DG2018 = {"revestida": 0.002, "sin_revestir": 0.005}

# --- T-9 (correcciones de la auditoria, H5) ---------------------------------
# Tabla 304.12 del DG-2001 que el num. 4.1.2.1 del Manual de Hidrologia
# reproduce (pag. impresa 173, PDF 176; cita MC_HHD.4.1.2.1#T304_12):
# «INCLINACIONES MÁXIMAS DEL TALUD (V:H) INTERIOR DE LA CUNETA». Son TOPES de
# inclinacion: el talud interior 1:Z1 cumple una fila si Z1 >= el de la fila.
# La fila depende de la velocidad de diseño (V.D.) y del IMDA, que el programa
# no conoce; por eso se guardan las tres cotas que la tabla imprime:
#   1:2  V.D. < 70 km/h e IMDA < 750, «(*) Sólo en casos muy especiales»
#   1:3  V.D. < 70 km/h (o IMDA < 750 con V.D. > 70 km/h)
#   1:4  V.D. > 70 km/h e IMDA > 750
# Un talud interior mas empinado que 1:2 no lo admite ninguna fila.
CUNETA_Z1_MIN_T304_12 = {"casos_muy_especiales": 2.0,      # H por 1 de V
                         "general": 3.0,
                         "vd_mas_70_imda_mas_750": 4.0}

# ===========================================================================
# --- T-7a --- (cadena T) · el cabezal por punto: desplante y aleros
# ===========================================================================
# Solo [N] aqui, y solo los que la fuente escribe con su numero. Las reglas
# del predimensionamiento (alturas, espesores, anchos, longitudes) son [A] y
# viven en el criterio 'predimensionamiento_cabezal'; el margen bajo la
# socavacion es [C] (AASHTO Sec. 12) y vive en 'margen_zapata_bajo_socavacion_m';
# el dentellon de la Lamina Nº 04 es [N→] y vive en 'dentellon_losa_entrega'.
#
# LA PROFUNDIDAD MINIMA DE CIMENTACION DE E.050 Art. 26.2 (0,80 m) YA NO ESTA
# AQUI (correcciones de T-7a, H8): el ambito de E.050 son las edificaciones
# del RNE (Art. 1 y 3, pag. 7), y aplicada a un cabezal vial es [N→] por
# analogia, no [N]. Vive en el criterio 'profundidad_cimentacion_min_cabezal_m'
# con la analogia declarada (cita E050.26.2#PROFUNDIDAD y su `Interpretacion`).
# Y el peralte minimo de la zapata ARMADA de E.060 15.7, por lo mismo, en
# 'peralte_min_zapata_armada_m'.

# E.060 Art. 22.7.4, pag. 193: «El espesor de las zapatas de concreto simple
# estructural no debe ser menor que 300 mm». Rige la zapata del cabezal de
# GRAVEDAD en ciclopeo (Cap. 22, el mismo de `M9.verificar_ciclopeo`); no la
# del voladizo armado, que la Via 1 (§0.2) deja a AASHTO. Se mantiene [N] por
# la lectura de la §9.4 de la hoja de ruta, que hace regir E.060 22.10 sobre
# el ciclopeo junto con el EG-2013 (ficha T7A-04: la objecion de ambito que
# hace [N→] a E.050 26.2 alcanzaria tambien a E.060, y queda para el dueño).
ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M = 0.30
NUMERAL_ZAPATA_CONCRETO_SIMPLE = _reg.cita("E060.22.7.4#ZAPATA").como_texto()

# LAS BANDAS DE ANGULO DE ALETAS QUE IMPRIMEN LAS FILAS DE CAJON de las Tablas
# A.1 y C.2 del HDS-5, leidas de su ROTULO literal (no de una prosa propia):
# para cada clave de fila, los intervalos de angulo de aleros CON EL EJE DEL
# CONDUCTO en que la fila vale, y si vale tambien SIN aleros (cabezal recto).
# Es la vista que `M9.filas_hds5_del_cajon` lee para decir si la embocadura
# declarada del marco ('embocadura_cajon', 'ke_entrada_cajon') es la del
# cabezal del punto. Cuatro lecturas que conviene tener a la vista:
#
#   * «90° and 15° wingwall flares» (Carta 8, escala 2): 90° es el ala EN EL
#     PLANO DEL MURO, o sea un cabezal recto; la fila vale sin aleros y con
#     aleros a 15° exactos.
#   * Las Cartas 10 («90° headwall») y 11 («skewed headwall») son CABEZAL
#     SIN ALETAS. Las de la 11 son ademas de cabezal ESVIADO respecto del
#     barril, y el cabezal que este programa propone es NORMAL al eje del
#     conducto: no casan con ninguno de los dos tipos y quedan sin banda.
#     Por la MISMA razon queda sin banda la escala 3 de la Carta 12 («18.4°
#     non-offset wingwall flares 30° skewed barrel»): el barril esviado 30°
#     respecto del cabezal tampoco es el cabezal normal al eje (correcciones
#     de T-7a, H9; hasta entonces se le daba la banda de 18.4°).
#   * Las Cartas 9, 12 y 13 nombran un angulo (o un intervalo) EXACTO.
#   * La Tabla C.2 agrupa por «Wingwalls at 30⁰ to 75⁰ to barrel», «Wingwall
#     at 10⁰ to 25⁰ to barrel», «Wingwalls parallel (extension of sides)» y
#     «Headwall parallel to embankment (no wingwalls)». Entre 25° y 30°, y
#     entre 75° y 90°, la tabla NO TIENE FILA.
#
# EL TUBO NO ESTA AQUI, y a proposito: la Tabla C.2 pone el ke del tubo bajo
# «Headwall or headwall and wingwalls» (concreto y metal corrugado) y las
# Cartas 1 a 3 no separan aleros (ficha T2-04). Con tubo el angulo de los
# aleros NO mueve ke ni la carta; la fuente no distingue.
SIN_ALETAS = "sin_aletas"
BANDAS_ALETAS_CAJON_A1: "dict[str, Tuple[Tuple[float, float], ...]]" = {
    "cajon_concreto_aletas_30_75": ((30.0, 75.0),),
    "cajon_concreto_aletas_90_15": ((15.0, 15.0),),
    "cajon_concreto_aletas_0": ((0.0, 0.0),),
    "cajon_concreto_aleta_45_d043": ((45.0, 45.0),),
    "cajon_concreto_aleta_18_337_d083": ((18.0, 33.7),),
    "cajon_concreto_cabezal_90_chaflan": (),
    "cajon_concreto_cabezal_90_bisel_45": (),
    "cajon_concreto_cabezal_90_bisel_337": (),
    "cajon_concreto_chaflan_esviaje_45": (),
    "cajon_concreto_chaflan_esviaje_30": (),
    "cajon_concreto_chaflan_esviaje_15": (),
    "cajon_concreto_bisel_45_esviaje_10_45": (),
    "cajon_concreto_chaflan_aletas_45": ((45.0, 45.0),),
    "cajon_concreto_chaflan_aletas_184": ((18.4, 18.4),),
    "cajon_concreto_chaflan_aletas_184_esviaje_30": (),
    "cajon_concreto_bisel_superior_aletas_45_desplazadas": ((45.0, 45.0),),
    "cajon_concreto_bisel_superior_aletas_337_desplazadas": ((33.7, 33.7),),
    "cajon_concreto_bisel_superior_aletas_184_desplazadas": ((18.4, 18.4),),
}
# Las filas de la Tabla A.1 de cajon que valen SIN aleros (cabezal recto,
# normal al barril): la escala 2 de la Carta 8 («90°») y la Carta 10.
CAJON_A1_SIN_ALETAS = frozenset({
    "cajon_concreto_aletas_90_15",
    "cajon_concreto_cabezal_90_chaflan",
    "cajon_concreto_cabezal_90_bisel_45",
    "cajon_concreto_cabezal_90_bisel_337",
})
BANDAS_ALETAS_CAJON_C2: "dict[str, Tuple[Tuple[float, float], ...]]" = {
    "cajon_sin_aletas_escuadra_3": (),
    "cajon_sin_aletas_redondeado_3": (),
    "cajon_aletas_30_75_escuadra": ((30.0, 75.0),),
    "cajon_aletas_30_75_redondeado": ((30.0, 75.0),),
    "cajon_aletas_10_25_escuadra": ((10.0, 25.0),),
    "cajon_aletas_paralelas_escuadra": ((0.0, 0.0),),
    "cajon_aletas_paralelas_tapered": ((0.0, 0.0),),
}
CAJON_C2_SIN_ALETAS = frozenset({"cajon_sin_aletas_escuadra_3",
                                 "cajon_sin_aletas_redondeado_3"})


# ===========================================================================
# --- T-7b --- (cadena T) · estabilidad del cabezal en un solo marco
# ===========================================================================
# Las tablas y los numeros de AASHTO LRFD 9.a ed. (2020) con que el ensamble
# de estabilidad del cabezal (`M9.ensamble_estabilidad`) verifica en el marco
# LRFD de su Art. 11.6, transcritos celda a celda de su pagina (PDF de
# normas/, capa de texto) y fijados por `tests/test_t7b_cabezal_estabilidad.py`.
# AASHTO es fuente [C] en este expediente (hoja de ruta §0.1): viven aqui, con
# las demas tablas transcritas de AASHTO (h_eq, recubrimientos), porque son
# NUMEROS DE LA FUENTE y no elecciones; CUAL fila aplica al cabezal es [A] y
# vive en criterios_adoptados ('fila_phi_estabilidad_cabezal',
# 'marco_estabilidad_cabezal'). El cabezal no tiene en AASHTO un articulo
# que mande verificarlo por 11.6: se MODELA como muro de semigravedad en
# voladizo, y esa hipotesis de modelacion la declara el criterio del marco.

# Tabla 10.5.5.2.2-1 «Resistance Factors for Geotechnical Resistance of
# Shallow Foundations at the Strength Limit State», pag. impresa 10-42 (PDF
# 1331). Once filas, todas transcritas; el Manual de Puentes (2.8.1.1.12.6)
# transcribe esta misma tabla.
PHI_ZAPATAS_T10_5_5_2_2_1 = {
    "portante": {
        "teorico_arcilla": 0.50,            # Theoretical method (Munfakh et al., 2001), in clay
        "teorico_arena_cpt": 0.50,          # ..., in sand, using CPT
        "teorico_arena_spt": 0.45,          # ..., in sand, using SPT
        "semiempirico": 0.45,               # Semi-empirical methods (Meyerhof, 1957), all soils
        "roca": 0.45,                       # Footings on rock
        "ensayo_de_placa": 0.55,            # Plate Load Test
    },
    "deslizamiento": {
        "prefabricado_sobre_arena": 0.90,   # Precast concrete placed on sand
        "vaciado_in_situ_sobre_arena": 0.80,    # Cast-in-Place Concrete on sand
        "concreto_sobre_arcilla": 0.85,     # Cast-in-Place or precast Concrete on Clay
        "suelo_sobre_suelo": 0.90,          # Soil on soil
    },
    "pasivo": 0.50,                         # Passive earth pressure component of sliding resistance
}
NUMERAL_PHI_ZAPATAS = ("AASHTO LRFD 9a ed., Tabla 10.5.5.2.2-1, pag. impresa "
                       "10-42 (PDF 1331)")

# Tabla 11.5.7-1 «Strength Limit State Resistance Factors for Permanent
# Retaining Walls», pag. impresa 11-17 (PDF 1486), bloque «Mechanically
# Stabilized Earth Walls, Gravity Walls, and Semigravity Walls»: solo las
# tres filas geotecnicas que un muro de semigravedad usa. El 11.5.7 remite a
# la Seccion 10 «unless specifically identified in Table 11.5.7-1», y esta
# tabla SI identifica el portante y el deslizamiento de estos muros.
PHI_MUROS_T11_5_7_1 = {
    "portante_gravedad_y_semigravedad": 0.55,
    "portante_mse": 0.65,
    "deslizamiento": 1.0,
}
NUMERAL_PHI_MUROS = ("AASHTO LRFD 9a ed., 11.5.7 y Tabla 11.5.7-1, pags. "
                     "impresas 11-15 y 11-17 (PDF 1484 y 1486)")

# 11.5.8 «Resistance Factors—Extreme Event Limit State», pag. impresa 11-18
# (PDF 1487). NO es «phi = 1.0» a secas: el articulo fija 1.0 «unless
# otherwise specified» y especifica en la misma pagina 0.9 para la
# estabilidad global y 0.8 para el portante de los muros de gravedad y
# semigravedad.
PHI_EVENTO_EXTREMO_11_5_8 = {
    "general": 1.0,
    "estabilidad_global": 0.9,
    "portante_gravedad_y_semigravedad": 0.8,
    "portante_mse": 0.9,
}
NUMERAL_PHI_EVENTO_EXTREMO = ("AASHTO LRFD 9a ed., 11.5.8, pag. impresa "
                              "11-18 (PDF 1487)")

# 11.6.3.3 «Eccentricity Limits» (pag. impresa 11-24, PDF 1493) y 10.6.3.3
# (pags. 10-83 y 10-84, PDF 1372 y 1373): la resultante dentro de los dos
# tercios centrales en suelo (e <= B/3) y de los nueve decimos en roca
# (e <= 0.45·B), SOBRE CARGAS FACTORADAS. Es el limite ESTATICO; el sismico
# (`EXCENTRICIDAD_ADMISIBLE_FRACCION_B`, 11.6.5.1) depende de gamma_EQ. Las
# dos fracciones ya estaban transcritas del Manual de Puentes, que traduce
# este articulo (`EXCENTRICIDAD_ESTATICA_FRACCION_B`, mas arriba): aqui solo
# se añade el numeral de la fuente original, que es el que el marco LRFD cita.
NUMERAL_EXCENTRICIDAD_ESTATICA_AASHTO = (
    "AASHTO LRFD 9a ed., 11.6.3.3 «Eccentricity Limits», pag. impresa 11-24 "
    "(PDF 1493); 10.6.3.3, pags. impresas 10-83 y 10-84")

# 10.6.3.4 «Failure by Sliding», pag. impresa 10-84 (PDF 1373), ec.
# 10.6.3.4-2: R_tau = C·V·tan(phi_f), con C = 1.0 «for concrete cast against
# soil» y 0.8 «for precast concrete footing».
C_DESLIZAMIENTO_10_6_3_4 = {"vaciado_contra_el_suelo": 1.0,
                            "zapata_prefabricada": 0.8}
NUMERAL_DESLIZAMIENTO_AASHTO = (
    "AASHTO LRFD 9a ed., 11.6.3.6 -> 10.6.3.4 «Failure by Sliding», pags. "
    "impresas 11-24 y 10-84 (PDF 1493 y 1373)")

# Tabla 10.6.3.1.2a-1 «Bearing Capacity Factors Nc (Prandtl, 1921), Nq
# (Reissner, 1924), and N_gamma (Vesic, 1975)», pag. impresa 10-72 (PDF
# 1361): phi_f en grados enteros de 0 a 45 -> (Nc, Nq, N_gamma). Las 46
# filas, tal como la tabla las imprime (un decimal; Nc de la fila 0, dos).
FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1 = {
    0: (5.14, 1.0, 0.0), 1: (5.4, 1.1, 0.1), 2: (5.6, 1.2, 0.2),
    3: (5.9, 1.3, 0.2), 4: (6.2, 1.4, 0.3), 5: (6.5, 1.6, 0.5),
    6: (6.8, 1.7, 0.6), 7: (7.2, 1.9, 0.7), 8: (7.5, 2.1, 0.9),
    9: (7.9, 2.3, 1.0), 10: (8.4, 2.5, 1.2), 11: (8.8, 2.7, 1.4),
    12: (9.3, 3.0, 1.7), 13: (9.8, 3.3, 2.0), 14: (10.4, 3.6, 2.3),
    15: (11.0, 3.9, 2.7), 16: (11.6, 4.3, 3.1), 17: (12.3, 4.8, 3.5),
    18: (13.1, 5.3, 4.1), 19: (13.9, 5.8, 4.7), 20: (14.8, 6.4, 5.4),
    21: (15.8, 7.1, 6.2), 22: (16.9, 7.8, 7.1), 23: (18.1, 8.7, 8.2),
    24: (19.3, 9.6, 9.4), 25: (20.7, 10.7, 10.9), 26: (22.3, 11.9, 12.5),
    27: (23.9, 13.2, 14.5), 28: (25.8, 14.7, 16.7), 29: (27.9, 16.4, 19.3),
    30: (30.1, 18.4, 22.4), 31: (32.7, 20.6, 26.0), 32: (35.5, 23.2, 30.2),
    33: (38.6, 26.1, 35.2), 34: (42.2, 29.4, 41.1), 35: (46.1, 33.3, 48.0),
    36: (50.6, 37.8, 56.3), 37: (55.6, 42.9, 66.2), 38: (61.4, 48.9, 78.0),
    39: (67.9, 56.0, 92.3), 40: (75.3, 64.2, 109.4), 41: (83.9, 73.9, 130.2),
    42: (93.7, 85.4, 155.6), 43: (105.1, 99.0, 186.5),
    44: (118.4, 115.3, 224.6), 45: (133.9, 134.9, 271.8),
}
NUMERAL_CAPACIDAD_PORTANTE_AASHTO = (
    "AASHTO LRFD 9a ed., 10.6.3.1.2a «Basic Formulation», ec. 10.6.3.1.2a-1 "
    "a -4 y Tablas 10.6.3.1.2a-1 y -2, pags. impresas 10-70 a 10-73 (PDF "
    "1359 a 1362)")

# Tabla 10.6.3.1.2a-2 «Coefficients Cwq and Cw_gamma for Various Groundwater
# Depths», pag. impresa 10-72 (PDF 1361). Tres filas por la profundidad D_w
# del nivel freatico bajo la superficie del terreno: 0.0 -> (0.5, 0.5);
# D_f -> (1.0, 0.5); > 1.5·B + D_f -> (1.0, 1.0). La tabla NO dice que hacer
# entre filas: la interpolacion lineal es lectura del proyecto y el paso
# del calculo lo declara.
CW_NIVEL_FREATICO_T10_6_3_1_2A_2 = {
    "en_la_superficie": (0.5, 0.5),         # D_w = 0.0: (C_wq, C_wgamma)
    "en_el_desplante": (1.0, 0.5),          # D_w = D_f
    "bajo_la_zona_de_falla": (1.0, 1.0),    # D_w > 1.5·B + D_f
}
CW_PROFUNDIDAD_SIN_EFECTO_VECES_B = 1.5     # el «1.5B» de la tercera fila

# Figura C3.11.5.8.1-1 «Earth Pressure Distribution for MSE Wall with Broken
# Back Earth Surcharge», pag. impresa 3-138 (PDF 192), leida por imagen: la
# pendiente equivalente del relleno quebrado es la de la recta que va de la
# coronacion del muro al terreno a una distancia horizontal de 2·H.
TALUD_QUEBRADO_DISTANCIA_VECES_H = 2.0
