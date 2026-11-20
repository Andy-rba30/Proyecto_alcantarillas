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

# --- VE-3.11 (H2) --- Puntos de la integral del PRIMER MOMENTO del area mojada
# respecto de la lamina, int_0^y A(z) dz, con que `M3.tirante_conjugado_barril`
# forma la funcion momentum de una seccion de barril cualquiera (la circular
# no tiene forma cerrada a mano en el proyecto). Es precision de una
# cuadratura trapecial sobre el llenado propio de la seccion: con 4001 puntos
# el error relativo del momento es del orden de 1e-7 (medido contra la forma
# cerrada del rectangulo, B*y^2/2), muy por debajo de lo que distingue un TW
# de su conjugado. Cambiarlo no mueve ninguna magnitud fisica.
PUNTOS_MOMENTO_SECCION = 4001

# Comparacion contra un umbral normativo (y/D <= 0.75, V >= 0.25, HW/D <= 1.5).
# Absorbe el ruido de punto flotante -- 0.675/0.90 puede dar 0.7500000000000001
# y eso NO es un incumplimiento del borde libre -- sin llegar a tapar ninguna
# holgura real: 1e-9 sobre magnitudes de orden 1 es una millonesima de
# milimetro. Se suma al lado admisible de la comparacion, nunca al obtenido.
TOL_UMBRAL_NORMATIVO = 1e-9

# --- VE-2 (decision (b) de VE1-02) --- Continuidad de una rama de Manning:
# cuanto puede diferir, en RELATIVO, el producto V*A del caudal Q con que se
# resolvio el tirante normal de esa rama. Las dos ramas resuelven su propio
# tirante con Brent (`M3.resolver_manning`), y el llenado resuelto reproduce
# Q hasta `TOL_BRENT` en el parametro de llenado, amplificado por dQ/dllenado.
# MEDIDO al cerrar VE-2 sobre la malla de `tests/test_ve2_velocidad_erosion.py`
# (seis secciones circulares x tres materiales y cuatro marcos x cuatro
# pendientes x seis fracciones de Q_lleno, las dos ramas): la peor desviacion
# entre la velocidad de Manning sobre la geometria resuelta y Q/A es 8.1e-11
# en la rama de n_min y 3.6e-11 en la de n_max (la misma que midio EXT-11).
# Se fijo en 1e-9, «doce veces por encima de lo medido». CORRECCIONES DE
# VE-2 (B3 de la revision Fable): esa malla empieza en el 5 % del lleno, y
# fuera de ella la cifra no vale. Un barrido aleatorio fuera de la malla
# (Random(7), 40 000 marcos de `MARCOS_B_H` con S log-uniforme de 1e-4 a 0.3
# y Q uniforme del 0.1 % al 99.99 % del lleno; las secciones circulares de
# `DIAMETROS_M` con Random(20261117) y 20 000 muestras dan 1.25e-10) midio
# 1.81e-9 entre Manning sobre la geometria de n_min y Q/A, y 1.10e-9 en
# V_erosion*A/Q - 1, en el marco 1.0 x 1.0 con S = 0.0505 y Q al 0.53 % del
# lleno: el `xtol` de Brent es absoluto y con un tirante de milimetros pesa
# mas en relativo. Ninguna magnitud del calculo se mueve por eso (1.8e-9
# relativo es una millonesima de milimetro por segundo en la velocidad). Se
# fija en 1e-8, cinco veces y media lo medido y todavia seis ordenes de
# magnitud por debajo de cualquier diferencia de rama: la velocidad de n_min
# sobre el tirante de n_max --la formula anterior a VE-2-- se aparta de la
# continuidad un 4.8 % como minimo. Cambiarla no mueve ninguna magnitud:
# solo la lee la comprobacion de continuidad de la suite. VALE PARA EL
# DOMINIO MEDIDO (Q desde el 0.1 % del lleno): como el `xtol` es absoluto,
# la desviacion relativa crece aproximadamente como 1/Q, y la verificacion
# de las correcciones midio 1.81e-8 con Q desde el 0.01 % del lleno. Una
# comprobacion de continuidad por debajo del 0.1 % del lleno tiene que medir
# su propia tolerancia.
TOL_REL_CONTINUIDAD_MANNING = 1e-8

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

# ---------------------------------------------------------------------------
# El paso directo del perfil de la lamina de agua (E-A, HDS-5 pag. 3.12 y
# Section 3.5): dos parametros NUMERICOS, ninguno de proyecto
# ---------------------------------------------------------------------------
# `M4.perfil_lamina` integra la ecuacion del flujo gradualmente variado por
# paso directo: recorre el PARAMETRO PROPIO de la seccion (theta en la
# circular, el tirante en el marco) en una escalera uniforme entre la
# frontera de la salida y el objetivo del perfil (y_n, y_c o la clave), y en
# cada escalon resuelve dx = (E_abajo - E_arriba)/(S - Sf_medio). Cuantos
# escalones tiene la escalera es precision numerica: medido sobre los casos
# del dictamen (D = 0.90, L = 20), 500, 2000 y 8000 escalones mueven el HW
# del remanso menos de 1e-8 m; cambiarlo no mueve ninguna magnitud fisica,
# solo el ruido de la discretizacion, y por eso vive aqui y no en un archivo
# de valores. El cruce con x = L se resuelve dentro del escalon con Brent
# (`TOL_BRENT`), no por interpolacion lineal, para que la escalera no
# imponga su paso al tirante de la entrada.
PASOS_PERFIL_LAMINA = 2000

# --- VE-3.7 --- La escalera del paso directo del REMANSO EN EL CANAL
# (`M3.perfil_remanso_trapecial`, Familia C). Los escalones van en progresion
# GEOMETRICA de (y - y_n) -- no equiespaciados en y --, porque el perfil M1 es
# asintotico al normal y una escalera uniforme converge mal cerca de la
# asintota (medido en el canal de C-01, b 1.0, z 1.5, n 0.025, S 0.006,
# Q 0.85, de y = 0.80 m a y = 1.001 y_n: -0.16 % con 4000 escalones
# uniformes). Cuantos escalones es precision numerica, como en
# PASOS_PERFIL_LAMINA: el test de VE-3.7 contrasta la longitud con una
# integracion independiente de la ecuacion del flujo gradualmente variado
# (scipy, `solve_ivp` con rtol 1e-11) y la diferencia medida con 2000
# escalones esta en `TOL_REL_PASO_DIRECTO_REMANSO`.
PASOS_PERFIL_REMANSO = 2000
# Lo que el paso directo del remanso puede diferir, en RELATIVO, de la
# integracion independiente de la ecuacion del flujo gradualmente variado.
# MEDIDO con 2000 escalones geometricos sobre seis casos (M1 del canal de
# C-01 hasta 1.05, 1.01 y 1.001 y_n; S1 hasta el conjugado en tres canales
# fuertes, rectangular y trapeciales): peor 6.5e-8. Se fija quince veces por
# encima. Solo la lee el test de VE-3.7: no mueve ninguna magnitud.
TOL_REL_PASO_DIRECTO_REMANSO = 1e-6

# Donde la escalera se detiene porque llego a la ASINTOTA: en un perfil M1 o
# M2 la lamina tiende a y_n sin alcanzarlo, y ahi S - Sf tiende a cero por
# los dos lados. Cuando |S - Sf_medio| queda por debajo de esta fraccion de
# S, el cociente dx = dE/(S - Sf) ya no esta determinado en double --se
# dividen dos residuos de redondeo-- y el perfil se toma como plano desde ese
# escalon: la lamina esta, a todos los efectos, en y_n. Es una tolerancia
# RELATIVA sobre la pendiente, del orden del ruido de la aritmetica de Sf
# (una potencia 4/3 y dos cuadrados: unas decenas de ulp), y no un umbral de
# proyecto.
TOL_ASINTOTA_PERFIL = 1e-12

# ---------------------------------------------------------------------------
# El comparador de dos `informe_json` (E-B, E14): cuando dos numeros de dos
# volcados son "el mismo numero"
# ---------------------------------------------------------------------------
# `src/comparador.py` empareja dos volcados por identidad de punto y compara
# campo a campo. Dos corridas del mismo arbol sobre el mismo CSV producen los
# MISMOS bytes (la linea base de la Familia C lo demuestra byte a byte), de
# modo que la unica diferencia numerica legitima entre dos volcados iguales
# es el ruido de la aritmetica en punto flotante --- la asociacion de una
# suma, el orden de un producto --- y estas dos tolerancias lo absorben: un
# umbral absoluto para las magnitudes pequenas (un tirante de 0.30 m, una
# pendiente de 0.0008) y uno relativo para las grandes (una cota de 3800 m).
# Son del mismo orden que `TOL_UMBRAL_NORMATIVO`, y por la misma razon: un
# nanometro no es una diferencia de diseno. Una diferencia REAL de calculo
# --- 0.3 mm de HW por una constante cambiada (EXT-2 midio -0.306 mm) --- esta
# seis ordenes de magnitud por encima y se reporta.
#
# NO son valores de proyecto: cambiarlas no mueve ningun numero de ninguna
# memoria; solo cuantas cifras tienen que coincidir para que el comparador
# calle. Y no son un criterio: no hay nada que declarar en la memoria sobre
# ellas.
TOL_COMPARADOR_ABS = 1e-9
TOL_COMPARADOR_REL = 1e-9

# ---------------------------------------------------------------------------
# El area de una obra escrita DOS VECES (T-1, auditoria adversarial)
# ---------------------------------------------------------------------------
# Con --cuencas el area de la cuenca de una obra esta en dos archivos y en dos
# unidades: `area_ha` en el CSV de puntos (la que clasifica la obra y fija su
# periodo de retorno) y `area_km2` en el CSV de cuencas (la que entra al metodo
# racional). Son el mismo dato y tienen que decir lo mismo; cuando no, el
# programa no elige una: se detiene con `DatoInvalidoError` nombrando el par.
#
# La tolerancia existe porque las dos se teclean REDONDEADAS, cada una en su
# unidad. Dos escrituras del mismo numero a tres cifras significativas
# difieren a lo sumo un 1 % (medio por ciento cada una), y eso no es una
# contradiccion sino un redondeo. Por encima, son dos areas.
#
# NO es un valor de proyecto: no entra en ninguna formula ni mueve ningun
# resultado. Solo decide cuando dos celdas dejan de ser la misma medida.
TOL_REL_AREA_ESCRITA_DOS_VECES = 1e-2

# ---------------------------------------------------------------------------
# --- VE3-19 --- Dos maximos anuales «iguales» de la serie de una estacion
# ---------------------------------------------------------------------------
# El aviso de consistencia de la Fase 1-bis (`MH._paso_consistencia`) lista
# los maximos anuales que aparecen en mas de un año (`MH.
# maximos_anuales_repetidos`): en la serie de Cañaveral de UNTumbes dos años
# son copia de otros dos, y con un maximo por año eso solo se ve como un
# valor repetido. Dos valores son el MISMO cuando difieren menos que esto,
# en mm: absorbe la representacion binaria de dos escrituras del mismo
# numero («129» y «129.00») y nada mas. NO es un umbral de cercania --dos
# maximos a 0.1 mm son dos valores distintos y no se listan-- y no es un
# numero de corte del aviso, que no tiene ninguno.
#
# NO es un valor de proyecto: no entra en ninguna formula ni mueve ningun
# resultado. Solo decide que dos celdas dicen el mismo numero.
TOL_ABS_MISMO_MAXIMO_ANUAL_MM = 1e-9


# ---------------------------------------------------------------------------
# --- T-5 --- La busqueda del relleno maximo de la Fase 8
# ---------------------------------------------------------------------------
# `M8._relleno_maximo` busca el PRIMER relleno sobre la clave en que la
# clase, la plancha o el perfil elegidos dejan de cumplir. El margen no es
# monotono en todo el intervalo --la carga viva decrece con la profundidad
# mientras la de tierra crece, y se desprecia de golpe pasados los 8.0 ft--,
# de modo que un Brent sobre el intervalo entero podria devolver un cruce
# POSTERIOR al primero, que es el lado inseguro. Se muestrea el intervalo en
# este numero de tramos y se aplica Brent (con TOL_BRENT) en el primero que
# cambia de signo. Es una resolucion numerica: solo un hundimiento del margen
# mas estrecho que un tramo --del orden de un centimetro en los rellenos de
# esta obra-- podria escaparsele.
TRAMOS_BUSQUEDA_RELLENO_MAXIMO = 400

# --- VE-5 (m8) --- La discretizacion del portico del marco
# (`M8._ModeloPortico`): en cuantos elementos se parte cada losa y cada pared
# (ademas de las estaciones de las caras, el centro y las cartelas) y cuantas
# posiciones de la carga viva se prueban por celda. Es resolucion numerica:
# los esfuerzos en los nodos son exactos (vector de carga consistente con las
# funciones de Hermite) y solo el MAXIMO entre dos posiciones de la carga
# viva puede escaparse, del orden de (luz/posiciones)^2 en el momento.
DIVISIONES_MIEMBRO_PORTICO = 24
POSICIONES_CARGA_VIVA_POR_CELDA = 24


# ---------------------------------------------------------------------------
# --- T-7b --- La busqueda de la cuña critica (Coulomb / Culmann)
# ---------------------------------------------------------------------------
# `M9.cuna_de_tanteo` busca el angulo del plano de falla que da el MAYOR
# empuje sobre el plano vertical del talon, con la superficie real del
# relleno (talud que sube y se quiebra en la plataforma). La funcion del
# angulo es suave salvo en el quiebre, donde tiene un pico anguloso; un
# metodo de una sola llamada podria quedarse en un maximo local. Se muestrea
# el intervalo admisible en este numero de tramos y se afina el mejor con
# una busqueda acotada a los dos tramos vecinos, hasta `TOL_ANGULO_CUNA`
# radianes. Es resolucion numerica: medido sobre los dos cabezales de A-01,
# 450, 1800 y 7200 tramos dan el mismo empuje a 1e-9 kN/m.
TRAMOS_CUNA_DE_TANTEO = 1800
TOL_ANGULO_CUNA = 1e-10


# ---------------------------------------------------------------------------
# --- T8-08 --- La lectura por imagen de las Figuras 3.3 y 3.4 de HEC-14
# ---------------------------------------------------------------------------
# Cuanto puede diferir una celda de las tablas `HEC14.F3_3` y `HEC14.F3_4`
# (yo/D, adimensional) de la curva que la figura dibuja. Las figuras son
# imagenes de 403 x 659 y 454 x 668 px incrustadas en el PDF: una division de
# 0.05 en yo/D mide unos 30 px, y el trazo, 2 o 3. Las celdas se leyeron
# sobre la imagen NATIVA (sin reescalar) promediando las dos columnas de
# pixeles a cada lado de cada linea vertical de la reticula, y se
# contrastaron con los tres anclajes de descarga libre de la ficha T8-08
# (diferencias de 0.001 y 0.002) y con el ejemplo resuelto de la pag.
# impresa 3-4 (diferencias de 0.003 a 0.006 sobre un impreso de dos cifras).
# NO ENTRA EN NINGUNA FORMULA: la usan los tests que contrastan la lectura y
# la nota de las dos citas, que la declaran. Cambiarla no mueve ningun
# resultado; si una celda queda fuera de ella, lo que esta mal es la celda.
TOL_LECTURA_FIGURA_HEC14 = 0.01


# ---------------------------------------------------------------------------
# --- VE-5 (mh, ficha T1-07) --- El punto fijo tiempo de concentracion <-> I
# ---------------------------------------------------------------------------
# Izzard y la onda cinematica (Tabla N 05 del Manual de Hidrologia) llevan la
# intensidad DENTRO de la formula, y la intensidad depende de la duracion,
# que es el tiempo de concentracion que se busca: «la solución requiere de
# procesos iterativos». `MH._punto_fijo_tc` itera tc_{k+1} = f(I(tc_k)) desde
# una lluvia de 24 horas y se detiene cuando dos iterados consecutivos
# difieren menos que esta fraccion del ultimo. La aplicacion es CONTRACTIVA
# (tc crece con la duracion a la potencia 0.3 en la onda cinematica y ~0.5
# en Izzard con la relacion de Dick y Peschke, porque I cae con la duracion a
# la potencia 0.75): converge en una a tres decenas de iteraciones. Si no converge
# en `ITERACIONES_MAX_PUNTO_FIJO_TC`, el calculo se detiene con
# `LimiteNumericoError` en vez de devolver el ultimo iterado.
#
# NO son valores de proyecto: deciden cuando dos iterados son el mismo
# numero. Medido sobre una cuenca de 2.1 km2 con la onda cinematica y la
# serie de prueba (tests/test_ve5_mh.py): 19, 21 y 25 iteraciones con 1e-9,
# 1e-10 y 1e-12, y el mismo caudal a 3e-11 relativo.
TOL_REL_PUNTO_FIJO_TC = 1e-10
ITERACIONES_MAX_PUNTO_FIJO_TC = 200

# --- VE-5 fixve4 --- Si una raiz del reparto del desborde es una raiz
# ---------------------------------------------------------------------------
# `M4.repartir_caudal_con_desborde` busca con `brentq` el caudal del conducto
# Q_c con Q_c + Q_o = Q_total (HDS-5 num. 3.1.5), y antes los dos extremos
# del intervalo, los Q_c con que el agua llega a un tirante dado sobre la
# cresta. `brentq` supone la funcion CONTINUA, y la carga de M4 no lo es:
# salta donde cambia el control que gobierna o el regimen del barril
# (medido: O 1.50 m, S = 0.004, L = 30 m, TW = 0.5 m, HW salta de 1.061 a
# 1.126 m entre Q = 2.04 y 2.05 m3/s). Sobre un salto `brentq` converge al
# salto y devuelve un Q_c que NO cumple la ecuacion; estas dos tolerancias
# dicen cuando el residuo es el del solver (TOL_BRENT sobre Q_c por la
# pendiente de la funcion) y cuando es un salto. NO MUEVEN NINGUNA MAGNITUD:
# una raiz verdadera las cumple con ordenes de margen (medido sobre el
# ejemplo DG 1.5 del HDS-5 con la carga de M4: residuo relativo del balance
# ~1e-11, del tirante ~1e-11 m) y un salto las incumple por decenas de
# centimetros o de m3/s; solo deciden si el tanteo se detiene con «metodo no
# evaluable» en vez de devolver un reparto que no reparte.
TOL_REL_BALANCE_REPARTO_DESBORDE = 1e-6
TOL_ABS_TIRANTE_TANTEO_DESBORDE_M = 1e-6


# ---------------------------------------------------------------------------
# --- VE-7 (dictamen Fable sobre VE7-01, abierto (a)) --- Las franjas del
# alero que se verifican como muro
# ---------------------------------------------------------------------------
# El alero baja con el talud de h0 a H_f y, con el borde de la plataforma
# fijo, el relleno SUBE mas detras de cada franja hacia la punta (la
# pendiente equivalente y K_A crecen): la franja del arranque no rige
# siempre. Se verifica en estas fracciones de la longitud del alero (0 el
# arranque, 1 la punta). Es una DISCRETIZACION de la verificacion, como
# `TRAMOS_CUNA_DE_TANTEO`: no es un valor normativo ni una eleccion del
# proyecto entre opciones de una fuente, y no entra en ninguna formula.
FRACCIONES_DE_ESTABILIDAD_DEL_ALERO = (0, 1 / 4, 1 / 2, 3 / 4, 1)
