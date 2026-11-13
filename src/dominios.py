"""
dominios.py
===========
Limites de dominio del dato de entrada. NO son valores de proyecto.

Cuarta categoria exenta de la regla "todo literal numerico fuera de
constantes_normativas.py y criterios_adoptados.py es un defecto", junto con
0/1/2 e indices, las constantes matematicas puras (pi) y las tolerancias
numericas de `tolerancias.py`.

Por que no son constantes normativas ni criterios adoptados
-----------------------------------------------------------
Una constante normativa responde a "que exige la norma" y llega con numeral.
Un criterio adoptado responde a "que decidio el proyectista donde la norma
calla", y por eso lleva etiqueta, justificacion, fuente y sensibilidad.

Un limite de dominio no responde a ninguna de las dos: responde a "que valores
puede tomar este dato antes de dejar de ser ese dato". Un CBR negativo no es
una subrasante mala, es una celda mal llenada; un esviaje de 120 grados no es
un cruce forzado, es un numero imposible. Ninguno entra en formula ni en
verificacion alguna: solo deciden si el CSV se puede leer. Declararlos como
criterios llenaria el bloque de M11 de parametros que no defienden ninguna
decision de diseno, y ponerlos en el Anexo B les inventaria un numeral que no
tienen.

Regla practica para saber si un numero va aqui: si cambiarlo puede alterar un
resultado del calculo, NO es un limite de dominio.

El archivo hospeda ademas las DEFINICIONES DE UNIDAD que el calculo necesita
para leer o escribir un dato (METROS_POR_KM, CENTIMETROS_POR_METRO). No son
limites de dominio en sentido estricto, pero responden a la misma pregunta --
que significa el numero que entra o sale, no cuanto vale una magnitud del
proyecto -- y cambiarlas seria redefinir la unidad, no ajustar un criterio.
Ninguna entra en formula de calculo: METROS_POR_KM traduce la notacion vial de
progresivas al leer el CSV y CENTIMETROS_POR_METRO escribe en centimetros el
delta de rasante que Sec. 7.B redacta en esa unidad.

Las marcas `# literal-ok` viajaron con los valores desde M0_carga.py. En este
archivo son redundantes -- el archivo entero esta exento del barrido -- pero se
conservan porque son la justificacion de cada numero, no un permiso.
"""

# Piso de la escala del CBR: es una proporcion en porcentaje y no puede ser
# nula ni negativa. NO TIENE TECHO AQUI, y hasta PF-6 lo tenia (R48-007):
# `CBR_MAX_FISICO = 100.0`, con el comentario «por encima de 100 el dato esta
# en otra escala o mal transcrito». Se retiro contra la fuente primaria,
# verificada pagina a pagina: el Manual de Suelos, Geologia, Geotecnia y
# Pavimentos (MTC) deja la categoria S5 de subrasante ABIERTA por arriba
# (Cuadro 4.11 «Categorias de Sub rasante», pag. impresa 37 / PDF 38: «S5 :
# Sub rasante Excelente | CBR >= 30%»), exige «Minimo 100%» a la base
# granular de carreteras de primera clase o trafico > 10 x 10^6 EE (Cuadro
# N 10.2 «Valor Relativo de Soporte, CBR en Base Granular», pag. impresa 108
# / PDF 109) y tabula «Base Granular CBR 100%» (Cuadro 12.13, pag. impresa
# 129 / PDF 130); en sus 281 paginas no hay techo alguno del CBR ni la
# expresion «piedra patron». Un techo que la fuente no fija es un valor de
# proyecto inventado, y este archivo solo acota lo que un dato PUEDE SER.
# Que el CBR sea alto o bajo no lo juzga este archivo; lo juzga la tabla de
# resguardo de Sec. 5.1, cuya fila mas alta es ilimitada.
CBR_MIN_FISICO = 0.0      # literal-ok: piso de la escala del CBR (proporcion en %, exclusivo)

# A 0 grados el cruce es perpendicular a la via. A 90 el eje del conducto seria
# paralelo al eje de la via y no habria cruce que resolver.
ESVIAJE_MAX = 90.0        # literal-ok: a 90 grados el conducto seria paralelo a la via

# Pendiente del cauce en m/m. Un valor >= 1 (100 %) delata una celda cargada en
# porcentaje: es el error de transcripcion mas frecuente de esta columna.
S_CAUCE_MAX = 1.0

# --- T-2 --- LA SECCION MEDIDA DEL RECEPTOR (`seccion_receptor_medida` de
# --datos-externos) es entrada de usuario y dos de sus campos no tenian techo:
# aceptaba n = 5.0. Los dos de abajo acotan lo que el dato PUEDE SER, no lo
# que conviene que sea.
#
# n de Manning, s/m^(1/3). Ninguna tabla de las fuentes llega a la decima
# parte de 1: la B.1 del HDS-5 (conductos) termina en 0.037 y la C.1 (cauces
# naturales pequeños) no pasa de las decimas. Un valor >= 1 delata OTRA
# magnitud en la celda --el coeficiente de Strickler, K = 1/n, que vale
# decenas-- y no una rugosidad grande.
N_MANNING_MAX_FISICO = 1.0
# Profundidad total del dren o canal receptor, m. Un valor de 100 m o mas no
# es un cauce hondo: es una celda en CENTIMETROS (110 por 1.10).
ALTURA_RECEPTOR_MAX_FISICA_M = 100.0   # literal-ok: techo de dominio del dato, delata centimetros

# Conversion de la notacion vial de progresivas ('0+380') a kilometros.
METROS_POR_KM = 1000      # literal-ok: definicion de la unidad, no valor de proyecto

# Conversion a la unidad de presentacion del delta de rasante de Sec. 7.B, que
# la hoja de ruta redacta en centimetros ("no factible -> subir rasante X cm").
# Mismo caso que METROS_POR_KM: es la definicion de la unidad, no un valor de
# proyecto. El calculo entero sigue en metros; esto solo lo escribe.
CENTIMETROS_POR_METRO = 100   # literal-ok: definicion de la unidad, no valor de proyecto

# Conversion al DIAMETRO DESIGNADO de las normas de producto, que tabulan en
# milimetros enteros (AASHTO M 170M-04, ASTM A760, AASHTO M294) mientras el
# calculo trabaja en metros. Mismo caso que los dos anteriores: es la
# definicion de la unidad, no un valor de proyecto -- no dice que diametros
# existen, solo como se escribe el mismo diametro en la otra unidad.
MILIMETROS_POR_METRO = 1000   # literal-ok: definicion de la unidad, no valor de proyecto


# --- T-4 --- Los dos limites de los ensayos de durabilidad (matriz de la
# Sec. 3.3). Mismo caso que los de arriba: acotan lo que el dato PUEDE SER o
# definen una unidad; ninguno es un umbral de proyecto -- esos viven en
# 'durabilidad_tmc_umbrales' [C] y en `constantes_normativas`.
#
# El pH es una escala de 0 a 14: un 70 delata un ensayo cargado en otra
# magnitud, y un valor negativo no existe.
PH_MAX_FISICO = 14.0      # literal-ok: extremo de la escala de pH, no un umbral de proyecto

# Conversion de ppm en peso (mg/kg) a porcentaje en peso: la Tabla 4.4 de
# E.060 tabula el sulfato del suelo en porcentaje y el laboratorio lo
# informa en ppm.
PPM_POR_PORCIENTO = 10000     # literal-ok: definicion de la unidad, no valor de proyecto

# Techo de una concentracion en partes por millon: un millon de ppm es el
# 100 % de la muestra. No acota una magnitud de proyecto: es la definicion de
# la unidad, y existe para que la puerta rechace un ensayo mal tecleado.
PPM_MAX_FISICO = 1000000    # literal-ok: definicion de la unidad (1e6 ppm = 100 %)

# --- T-1 --- Conversiones de las unidades en que el Manual de Hidrologia
# escribe su capitulo III (minutos y horas, hectareas y km2). Mismo caso que
# METROS_POR_KM: definen la unidad, no un valor de proyecto. Las usa
# `modulos/MH_hidrologia.py` para pasar de la columna `area_ha` del CSV de
# puntos a los km2 de la ecuacion (28), y de las horas de la formula de Temez
# a los minutos de la Tabla N 05.
MINUTOS_POR_HORA = 60         # literal-ok: definicion de la unidad, no valor de proyecto
HECTAREAS_POR_KM2 = 100       # literal-ok: definicion de la unidad, no valor de proyecto
# --- T-8 --- El porcentaje: techo del dominio de un pasante (EG-2013, Tabla
# 511-06 entra por el % que pasa el tamiz N.º 200) y la conversion de una
# pendiente en m/m al % con que entra la Tabla 5.3 de HEC-14. Mismo caso que
# los tres anteriores: definicion de la unidad, no valor de proyecto (el
# auditor de T-8 lo saco de `constantes_normativas`, donde no era [N]).
PORCENTAJE_POR_UNIDAD = 100.0   # literal-ok: definicion del porcentaje, no valor de proyecto
# --- T-7a --- Techo FISICO de una dimension declarada del cabezal
# (`cabezal_declarado` de `--datos-externos`): rechaza un dato mal tecleado
# -- una cota en msnm puesta donde va una altura, un milimetro por un metro --
# y no acota ninguna magnitud de proyecto. Un muro de cabecera de alcantarilla
# (luz < 6 m) de mas de 30 m en cualquiera de sus dimensiones no es un
# cabezal: es otra estructura. No entra en ninguna formula.
DIMENSION_CABEZAL_MAX_M = 30.0   # literal-ok: rango fisico de un dato de entrada, no un umbral de proyecto
