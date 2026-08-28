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
DIAMETRO_MIN = 0.90                 # m (4.1.1.3.4 a)
DIAMETRO_MIN_SELVA_ALTA = 1.22      # m = 48"; NO aplica en costa (4.1.1.3.7 a)
Y_SOBRE_D_MAX = 0.75                # borde libre >= 25% (4.1.1.3.7 b)
V_MIN = 0.25                        # m/s (4.1.1.3.6, pag. 76) -- ver abajo
# Texto que fija V_MIN, literal (MC-HHD, RD 20-2011-MTC/14, num. 4.1.1.3.6,
# pag. 76, parrafo inmediatamente posterior a la Tabla Nº 10):
#
#     "Se deberá verificar que la velocidad mínima del flujo dentro del
#     conducto no produzca sedimentación que pueda incidir en una reducción de
#     su capacidad hidráulica, recomendándose que la velocidad mínima sea igual
#     a 0.25 m/s."
#
# Se transcribe entero y no solo el numero porque el parrafo fija dos cosas
# que el 0.25 suelto pierde. Primera: el numeral RECOMIENDA, no prohibe --
# V2 lo aplica como umbral duro por decision conservadora del proyecto, y ese
# matiz viaja hasta la memoria dentro de M5.NUMERAL_V2. Segunda: la razon del
# minimo es la SEDIMENTACION que reduce capacidad, no el desgaste; por eso
# vale igual para todos los materiales, mientras que el techo de V_MAX cambia
# con la calidad del revestimiento. Es la misma pagina que la Tabla Nº 10 y
# el mismo numeral, de modo que sin el titulo de la tabla y sin este parrafo
# los dos limites se confunden -- que es exactamente el error que V3 tenia.
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

RIESGO_ADMISIBLE = {                # Tabla N 02, num. 3.6
    "quebrada_importante": {"R": 0.30, "n": 25},   # -> TR = 71 anios
    "quebrada_menor":      {"R": 0.35, "n": 15},   # -> TR = 35 anios
}
# TR = 1 / (1 - (1-R)**(1/n))       # sin piso normativo

MANNING = {                         # Tabla N 09: (n_min, n_max)
    "metal_corrugado": (0.021, 0.030),
    "concreto_recto":  (0.010, 0.013),
    "madera_duelas":   (0.010, 0.014),
    # HDPE no listado -> criterios_adoptados.valor("n_manning_hdpe")
}
# n_max -> capacidad y tirante ; n_min -> velocidad y socavacion

# Tabla N 10, "Velocidades maximas admisibles en conductos revestidos"
# (num. 4.1.1.3.6, pag. 76). Los DOS numeros de cada fila son velocidades
# MAXIMAS: el rango recorre la calidad del revestimiento y el extremo inferior
# es el maximo admisible del acabado mas pobre. NO es (piso, techo). V3
# verifica solo el superior; el piso de autolimpieza es V_MIN, aparte y para
# todos los materiales. La transcripcion no cambia: cambia como se lee.
V_MAX = {
    "concreto":            (3.0, 6.0),
    "ladrillo_c_concreto": (2.5, 3.5),
    "mamposteria_piedra":  (2.0, 2.0),
    # TMC y HDPE no listados -> criterios_adoptados
}

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
D_INICIO = 0.90                     # m; minimo normativo MTC
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
    "DIAMETRO_MIN_SELVA_ALTA",   # 'diametros_normalizados' (D_INICIO), y la
                                 # fila de selva alta no aplica en costa
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
