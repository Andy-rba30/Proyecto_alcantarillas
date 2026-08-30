"""
tests/apoyo/aproximacion.py
===========================
Las dos tolerancias con que la suite compara numeros de punto flotante.

Por que existe (SIS-F-16)
-------------------------
Quince asserts de la suite comparaban floats con ``==``. CLAUDE.md lo prohibe
sin excepcion para tests: "No comparar floats con ==. Tolerancias explicitas y
nombradas". Los quince eran, ademas, EXACTOS POR CONSTRUCCION -- un numero que
el CSV entrega y el pipeline transporta sin operar sobre el, o una constante
normativa leida tal cual --, y por eso pasaban: el defecto no era que fallaran,
era que la suite congelaba una practica prohibida y la extendia a cada test
nuevo que copiara el patron.

QUINCE ES EL RECUENTO DEL GREP DE LA FICHA, NO EL DEL REPOSITORIO, y conviene
decirlo en vez de que se deduzca. Al ampliar el detector a las formas que el
grep no ve -- el literal dentro de una tupla, de una lista o de un dict; la
pertenencia ``in (a, b)``; el literal negativo, que en el arbol no es un
``Constant`` sino un ``UnaryOp`` -- aparecieron dieciseis mas, en test_M2,
test_M4, test_M5, test_M8, test_M9 y test_MD, y todos se convirtieron tambien.
La propia ficha añadia ademas ``(+ test_M2:129-130)``, que son dos asserts de
NOMBRE contra NOMBRE (``tmc.v_max_adoptado == ca.valor("v_max_tmc")``): esos no
los ve ningun detector sintactico y hubo que encontrarlos leyendo.

Cambiarlos a ``pytest.approx`` con la tolerancia por defecto habria cumplido la
letra y no el fondo: la regla pide tolerancias **nombradas**, para que quien
lea el assert sepa QUE clase de igualdad se esta afirmando. Aqui hay dos, y no
son intercambiables.

``REL_TRANSPORTE``
    Igualdad de un valor que el pipeline TRANSPORTA: entra por el CSV o por
    una tabla normativa y sale por el otro extremo sin que ninguna formula
    opere sobre el. La unica diferencia admisible es el ruido de convertir el
    texto a double y volver a leerlo, muy por debajo de 1e-12 relativo. Si un
    assert con esta tolerancia falla, el valor NO se transporto: alguien lo
    calculo por el camino.

``ABS_CERO``
    Igualdad contra CERO. La tolerancia relativa no existe en el cero (todo
    numero dista de el un 100 %), de modo que la comparacion tiene que ser
    absoluta. Las tres cifras, medidas y no estimadas: la magnitud POSITIVA
    mas pequeña que el proyecto declara es ``CUANTIA_MIN_MURO['vertical'] =
    0.0015`` (E.060, cuantia minima del muro), de modo que 1e-12 queda 9.2
    ordenes por debajo de lo mas pequeño que hay que distinguir de cero; y
    esta 3.65 ordenes por encima del epsilon del double (2.22e-16), que es la
    holgura que absorbe el ruido de tres o cuatro operaciones encadenadas.
    Una version anterior de este parrafo decia "doce ordenes", "el n de
    Manning, 0.010" y "ocho por encima del epsilon": las tres eran falsas, y
    la primera por un factor de mil.

Uso::

    from tests.apoyo.aproximacion import REL_TRANSPORTE, ABS_CERO

    assert punto.D == pytest.approx(0.60, rel=REL_TRANSPORTE)
    assert n_s == pytest.approx(0.0, abs=ABS_CERO)

Estas NO son las tolerancias del calculo: esas viven en ``src/tolerancias.py``
y responden a otra pregunta (cuanto vale el ultimo bit del float en una
comparacion contra un umbral normativo). Un test que contrasta un valor
CALCULADO contra un caso patron usa la tolerancia que el propio caso patron
declara, no estas dos.
"""

# Ruido admisible en un valor que solo se transporta. Un round-trip
# texto -> double -> texto no lo mueve ni de lejos: 0.60 leido del CSV y
# devuelto por el informe es el mismo double, bit a bit.
REL_TRANSPORTE = 1e-12

# Igualdad contra cero: absoluta, porque la relativa no existe en el cero.
ABS_CERO = 1e-12
