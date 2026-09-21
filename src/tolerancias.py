"""
tolerancias.py
==============
Precision numerica del calculo. NO son literales de proyecto.

La regla de arquitectura dice que todo literal numerico fuera de
`constantes_normativas.py` y `criterios_adoptados.py` es un defecto, y exime
dos categorias: 0, 1, 2 e indices, y las constantes matematicas puras (pi).
Este archivo es la TERCERA categoria exenta, y esta separada de las otras dos
a proposito. La cuarta es `dominios.py`, con los limites de dominio del dato
de entrada: tampoco son valores de proyecto, pero responden a otra pregunta
(que valores puede tomar un dato, no cuanto vale el ultimo bit del float).

Por que no son criterios adoptados
----------------------------------
Una constante normativa responde a "que exige la norma". Un criterio adoptado
responde a "que decidio el proyectista donde la norma calla" y por eso lleva
etiqueta [N->], [C] o [A], justificacion, fuente y analisis de sensibilidad.

Una tolerancia no responde a ninguna de las dos preguntas: responde a "cuanto
vale el ultimo bit del float". No lleva etiqueta porque no hay nada que
declarar en la memoria de calculo; cambiarla no mueve ninguna magnitud fisica,
solo el ruido de la aritmetica de punto flotante. Meterlas en
`criterios_adoptados.py` ensuciaria el bloque de declaracion de criterios de
M11 con parametros que a un revisor no le dicen nada.

Corolario que si hay que vigilar: si alguna vez cambiar una de estas
tolerancias convierte un "cumple" en un "no cumple", el problema NO es la
tolerancia. Es que el diseno cae exactamente sobre el limite normativo, y eso
se declara en la memoria en vez de esconderlo detras del redondeo.

Uso
---
    from src.tolerancias import TOL_BRENT, TOL_UMBRAL_NORMATIVO

    theta = brentq(f, a, b, xtol=TOL_BRENT)
    cumple = y_sobre_D <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO

Nunca comparar floats con ==: las tolerancias son explicitas y con nombre.
"""

# Convergencia de los dos solvers de Brent (tirante normal y tirante critico,
# Sec. 4.1 y 4.2). La variable que se itera es theta en radianes, sobre
# (0, 2*pi): 1e-10 rad equivale a ~1e-11 m de tirante en un tubo de 0.90 m,
# once ordenes por debajo de cualquier magnitud con sentido constructivo, y
# muy por encima del epsilon del double (~2.2e-16).
TOL_BRENT = 1e-10

# Margen del extremo del intervalo (0, 2*pi) sobre el que M3 busca theta con
# Brent (Sec. 4.1). En theta=0 el conducto esta vacio: A=0, P=0 y R=0/0 es
# indeterminado; en theta=2*pi esta lleno a presion, fuera del regimen de
# flujo libre que modela Manning. Ningun theta real del diseno cae tan cerca
# de cualquiera de los dos bordes (V1 tapa y/D en 0.75, muy lejos de ambos),
# de modo que recortar el intervalo por este margen no descarta ninguna
# solucion fisica: solo evita evaluar la geometria justo en la singularidad.
TOL_THETA_BORDE = 1e-9

# Comparacion contra un umbral normativo (y/D <= 0.75, V >= 0.25, HW/D <= 1.5).
# Absorbe el ruido de punto flotante -- 0.675/0.90 puede dar 0.7500000000000001
# y eso NO es un incumplimiento del borde libre -- sin llegar a tapar ninguna
# holgura real: 1e-9 sobre magnitudes de orden 1 es una millonesima de
# milimetro. Se suma al lado admisible de la comparacion, nunca al obtenido.
TOL_UMBRAL_NORMATIVO = 1e-9

# ---------------------------------------------------------------------------
# COS_ESVIAJE_MIN: donde 1/cos(esviaje) deja de estar determinado (PC-32)
# ---------------------------------------------------------------------------
# `M7.factor_esviaje` divide por cos(theta) y el dominio del esviaje es abierto
# en 90 grados: M0 admite todo theta < 90, y a medida que theta se acerca a 90
# el coseno se acerca a cero. La pregunta que este umbral contesta es
# NUMERICA, no de proyecto: a partir de que coseno el FACTOR ya no esta
# determinado al ultimo bit. El argumento de radians(theta) lleva un redondeo
# absoluto del orden de (pi/2)*epsilon, cos tiene pendiente ~1 cerca de 90
# grados, de modo que el error RELATIVO del factor es ~ (pi/2)*epsilon/cos.
# Se exige que ese error quede por debajo de TOL_UMBRAL_NORMATIVO -- la misma
# tolerancia con que el proyecto compara cualquier umbral --, y despejando:
#
#     cos(theta) > (pi/2) * epsilon / TOL_UMBRAL_NORMATIVO  ~= 3.5e-7
#
# o sea theta < 89.99998 grados. Dos precisiones que el auditor adversarial de
# EXT-1 pidio dejar escritas: (a) TOL_UMBRAL_NORMATIVO se usa aqui como
# tolerancia RELATIVA sobre el factor, no absoluta -- el factor es
# adimensional y de orden 1 en el cruce normal, y lo que se acota es cuanto lo
# mueve el ultimo bit del angulo --; (b) la derivacion usa epsilon donde el
# redondeo real de radians(theta) es ulp(theta)*pi/180 ~ 2.5e-16 rad, de modo
# que SOBREESTIMA el error ~1.6 veces y el umbral detiene un poco ANTES de lo
# estrictamente necesario: medido a 1 ulp del angulo, el cambio relativo del
# factor en el umbral es 6.4e-10. Es el lado conservador. Lo que NO es: una cota de cordura sobre el
# esviaje. El esviaje de 89.9 grados -- factor 573, longitud de 10 313 m en
# A-01 -- pasa este umbral, y pasa A PROPOSITO: cortarlo exigiria un valor
# que ninguna norma de normas/ fija, y `factor_esviaje` (MAT-O18) deja
# escrito que ese valor, si el proyecto lo quiere, es un criterio [A] con su
# sensibilidad, no un literal escondido aqui. Es la frontera exacta entre una
# tolerancia (esta) y un valor de proyecto (aquel).
import math as _math      # noqa: E402  -- solo para derivar el umbral
import sys as _sys        # noqa: E402

COS_ESVIAJE_MIN = (_math.pi / 2) * _sys.float_info.epsilon / TOL_UMBRAL_NORMATIVO
