"""
constantes_fisicas.py
======================
Constantes fisicas universales, no de proyecto. Comparten categoria de
exencion con tolerancias.py y dominios.py (ver CLAUDE.md, Arquitectura):
ninguna de las tres responde a "que exige la norma peruana"
(constantes_normativas.py) ni a "que decidio el proyectista donde la norma
calla" (criterios_adoptados.py). Responden a un valor fisico universal, el
mismo en cualquier obra del planeta -- cambiarlo no es un criterio de
proyecto ni la lectura de un dato de sitio, es cambiar de planeta.

Por que esto NO es simplemente math.pi
---------------------------------------
pi no necesita archivo porque es un nombre (`math.pi`) y no un literal: el
barrido de tests/test_sin_literales.py ya lo deja pasar. La gravedad no tiene
un equivalente en la libreria estandar de Python, así que necesita un nombre
declarado en algun lado; este archivo es ese lado.

Por que NO es lo mismo que G_LAUSHEY (constantes_normativas.py)
-----------------------------------------------------------------
`G_LAUSHEY = 9.8` vive en constantes_normativas.py porque la Sec. 4.1.1.3.7 c)
de la hoja de ruta escribe ese numero explicitamente junto a su formula de
d50 (num. 4.1.1.3.7 c): es la cita, no la fisica. En el resto del script
(control de salida, tirante critico) la hoja de ruta escribe la formula con
el simbolo "g" sin fijarle un decimal propio -- ahi entra la constante fisica
de este archivo. Antes de esta separacion convivian dos valores del mismo
concepto sin que nadie lo declarara: G = 9.8 (heredado sin querer del
Laushey) frente a un GAMMA_AGUA_KN_M3 = 9.81 escrito como literal
independiente en constantes_normativas.py (que implica g = 9.81 kN/m3 /
1000 kg/m3), una inconsistencia silenciosa entre dos constantes que decian
representar la misma gravedad.

Por que el peso especifico del agua vive AQUI y no en constantes_normativas
-----------------------------------------------------------------------------
`GAMMA_AGUA_KN_M3 = 9.81` estuvo declarado como constante [N] con el numeral
2.4.3.8.2 del Manual de Puentes. La cita era correcta en cuanto a DONDE se usa
el valor -- la subpresion -- pero equivocada en cuanto a QUE es el valor: el
peso especifico del agua no es una exigencia de la norma peruana. Ningun
numeral peruano lo "fija"; el agua pesa lo que pesa en cualquier obra del
planeta, y quien cambie de norma no cambia ese numero. Es exactamente el
criterio que ya se le aplico a G.

Ademas dejo de ser un literal independiente: se DERIVA de la densidad del agua
y de la gravedad de este mismo archivo. Escribir 9.81 dos veces (una como
gravedad, otra como peso especifico) era pedir que algun dia alguien tocara
una y no la otra. Ahora solo hay una gravedad en el proyecto, y el peso
especifico del agua es una consecuencia aritmetica suya.
"""

G = 9.81   # m/s2; aceleracion estandar de la gravedad (CGPM, 1901)

RHO_AGUA = 1000.0   # kg/m3; densidad del agua dulce a temperatura ordinaria

# Factor de la unidad SI derivada, no un valor de proyecto: 1 kN = 1000 N. El
# calculo opera en kN (ver CLAUDE.md, Unidades), la fisica en N.
N_POR_KN = 1000.0

# 1 ft = 0.3048 m, EXACTO por definicion internacional del pie desde 1959 (y
# 1 in = 25.4 mm, que es de donde sale). Es un factor de unidad, de la misma
# clase que N_POR_KN, y por eso vive aqui y no en constantes_normativas.py:
# no lo "fija" ningun numeral peruano y no cambia al cambiar de norma.
#
# HACE FALTA PORQUE HAY TABLAS EN PIES. Las dos de altura de suelo
# equivalente de AASHTO (3.11.6.4-1 y -2) y la de recubrimiento (5.10.1-1)
# imprimen sus valores en pies y en pulgadas, y el calculo opera en SI: la
# conversion tiene que ocurrir en UN sitio y con el factor exacto. Redondearla
# no es inocuo -- el umbral "1.0 ft or Further" de la Tabla 3.11.6.4-2 son
# 0.3048 m y escribirlo 0.30 relaja el criterio --, y ese redondeo es
# justamente uno de los defectos que el cluster C02 cerro.
PIE_EN_METROS = 0.3048
PULGADA_EN_MM = 25.4

GAMMA_AGUA = RHO_AGUA * G                   # N/m3  = 9810.0
GAMMA_AGUA_KN_M3 = GAMMA_AGUA / N_POR_KN    # kN/m3 = 9.81, unidad del calculo
