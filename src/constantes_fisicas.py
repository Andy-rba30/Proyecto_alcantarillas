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
Laushey) frente a GAMMA_AGUA_KN_M3 = 9.81 (que implica g = 9.81 kN/m3 /
1000 kg/m3), una inconsistencia silenciosa entre dos constantes que decian
representar la misma gravedad.
"""

G = 9.81   # m/s2; aceleracion estandar de la gravedad (CGPM, 1901)
