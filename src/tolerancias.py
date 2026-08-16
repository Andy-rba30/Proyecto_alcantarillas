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
    from tolerancias import TOL_BRENT, TOL_UMBRAL_NORMATIVO

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
