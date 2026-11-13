"""
tests/fixtures/casos_patron.py
===============================
Casos de referencia calculados fuera del pipeline para contrastar cada módulo.

Uso previsto en los módulos de prueba:

    from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING

    def test_geometria_circular():
        c = CP2_GEOMETRIA_MANNING
        theta = resolver_theta(c["D"], c["y_sobre_D"])
        assert theta == pytest.approx(c["theta_esperado"], rel=1e-5)
        ...

Cómo se verifica cada caso (MAT-O20)
------------------------------------
Este encabezado decía «todos los valores numéricos fueron verificados con
scipy.optimize.brentq de forma independiente». Era falso por partida doble: el
bloque `__main__` solo autoverificaba CP-2 y CP-8, y brentq no interviene en
ningún caso que no resuelva una raíz. La afirmación tapó durante toda su vida
el defecto de CP-1 (MAT-D7 / SIS-F-03), cuyos dorados no salían de la fórmula
que el propio caso declara. Lo que hoy es cierto:

- **Autoverificados por el bloque `__main__` de este archivo** (recomputación
  independiente, sin importar módulos del repo): CP-1, CP-2, CP-7 y CP-8.
  Córrelo con `python3 tests/fixtures/casos_patron.py`. Solo CP-2 usa
  `scipy.optimize.brentq` -- es el único que resuelve una raíz; los otros tres
  son fórmula cerrada.
- **Recomputados a mano, sin autoverificación en este archivo**: CP-3, CP-4,
  CP-5 y CP-6. CP-6 no tiene valor cerrado por construcción (se contrasta por
  residuo en su propio test).

Si un test contra estos valores falla, el error está *probablemente* en el
módulo bajo prueba -- pero el fixture no es infalible y ya falló una vez:
recalcula antes de tocar el módulo.

Referencias de numeral: ver docs/hoja_de_ruta_alcantarillas_v8.md
"""

import math

G = 9.81  # m/s2, gravedad fisica generica (constantes_fisicas.G). CP-8 usa
          # esta, no G_LAUSHEY = 9.8 (esa es solo para Sec. 4.1.1.3.7 c) en M6).


# ---------------------------------------------------------------------------
# CP-1 · Periodo de retorno (Sec. 2.2, Tabla N 02)
# ---------------------------------------------------------------------------
# TR = 1 / (1 - (1-R)**(1/n))
#
# CORREGIDO (MAT-D7 / SIS-F-03). Los dorados anteriores -- 70.63 y 35.29 --
# NO salían de esta fórmula: la doble precisión da 70.59302021387457 y
# 35.322715552711315. Los errores (-0.037 y +0.033, uno alto y otro bajo)
# cabían justo debajo de la tolerancia de 0.05, de modo que la ventana quedaba
# centrada en un número falso y la implementación CORRECTA pasaba con margen
# de solo 0.013. Ningún documento de docs/ contiene 70.63 ni 35.29: no eran
# valores de fuente mal copiados, eran dorados mal calculados.
#
# Los dorados de abajo son el double exacto redondeado a 5 decimales, así que
# el residuo frente al cálculo real es <= 5e-6 por construcción; la tolerancia
# de 1e-5 lo cubre y es 3700 veces más estrecha que la que dejó pasar el error.
# Los redondeos publicados en la memoria (71 y 35 años) no cambian.

CP1_PERIODO_RETORNO = [
    {
        "descripcion": "Quebradas importantes / badenes",
        "R": 0.30,
        "n": 25,
        "TR_esperado": 70.59302,   # exacto 70.59302021387457; redondea a 71
        "tolerancia": 1e-5,
    },
    {
        "descripcion": "Quebradas menores / descarga de cunetas",
        "R": 0.35,
        "n": 15,
        "TR_esperado": 35.32272,   # exacto 35.322715552711315; redondea a 35
        "tolerancia": 1e-5,
    },
]


# ---------------------------------------------------------------------------
# CP-2 · Geometria circular y Manning (Sec. 4.1)
# ---------------------------------------------------------------------------
# Entradas: D=0.90 m, y/D=0.75, S=0.005, n_max=0.013 (capacidad), n_min=0.010
# (velocidad). CORREGIDO respecto de un calculo previo con error de formula:
# la velocidad se obtiene de V = (1/n) R^(2/3) S^(1/2); el caudal es Q = V*A.
# NO dividir Q entre A para obtener V (error cometido en una version anterior
# de esta guia).

CP2_GEOMETRIA_MANNING = {
    "D": 0.90,
    "y_sobre_D": 0.75,
    "S": 0.005,
    "n_max": 0.013,   # rama de capacidad / tirante
    "n_min": 0.010,   # rama de velocidad / socavacion

    "theta_esperado": 4.18879,     # rad
    "A_esperado": 0.51180,         # m2
    "P_esperado": 1.88496,         # m
    "R_esperado": 0.27152,         # m

    # Formula: V = (1/n) * R^(2/3) * S^(1/2)  (NO multiplicar por A -- V es
    # velocidad media de la seccion, no un caudal). Q = V * A se deriva aparte.
    "V_con_n_max_esperado": 2.2807,   # m/s  (n=0.013, rama de capacidad/tirante)
    "Q_con_n_max_esperado": 1.1673,   # m3/s = V_con_n_max * A

    "V_con_n_min_esperado": 2.9650,   # m/s  (n=0.010, rama de velocidad)

    "tolerancia_geometria": 1e-5,
    "tolerancia_hidraulica": 1e-3,
}

# Assert de diseno del test: V_con_n_min > V_con_n_max siempre que n_min <
# n_max (a igual S, R). Si un modulo devuelve el mismo numero para ambas
# ramas, esta ahorrando el calculo doble que exige la regla de Sec. 4.1.


# ---------------------------------------------------------------------------
# CP-3 · La velocidad minima nunca gobierna (Sec. 5.2)
# ---------------------------------------------------------------------------
# Pendiente que produce exactamente V=0.25 m/s con D=0.90, y/D=0.75, n=0.013.
# Cualquier pendiente constructiva razonable (>= 0.001) la supera con margen.

CP3_VELOCIDAD_MINIMA = {
    "D": 0.90,
    "y_sobre_D": 0.75,
    "n": 0.013,
    "V_objetivo": 0.25,          # m/s, V2 del Manual MTC
    "S_que_produce_V_objetivo": 6.008e-5,   # adimensional
    # La pendiente esta redondeada a cuatro cifras significativas, y esa es
    # toda la precision que el caso patron sostiene: la V que devuelve Manning
    # a partir de ella iguala la V objetivo hasta el milimetro por segundo, no
    # mas alla. Se declara aqui, con el caso, en vez de repetirse a mano en
    # cada test que lo consuma (regla de tests/apoyo/aproximacion.py).
    "tolerancia_V": 1e-3,        # m/s
    "S_constructiva_minima_referencia": 0.001,
    # La conclusion va condicionada a SUS entradas (MAT-O20): escrita sin
    # ellas era falsa. Con y/D < 0.056 (mismo D y n) V2 SI se viola a
    # S = 0.001; la hoja de ruta (Sec. 5.2) la condiciona correctamente.
    "conclusion": "Para D=0.90, y/D=0.75 y n=0.013, V2 se cumple para "
                  "cualquier S >= 0.001 y no gobierna el diseno. No es "
                  "universal: no vale para tirantes relativos muy bajos.",
}


# ---------------------------------------------------------------------------
# CP-4 · Laushey (Fase 6) -- d50 = V^2 / (3.1*g)
# ---------------------------------------------------------------------------

CP4_LAUSHEY = [
    {"V": 1.0, "d50_esperado": 0.03292, "tolerancia": 1e-4},
    {"V": 2.0, "d50_esperado": 0.13167, "tolerancia": 1e-4},
    {"V": 3.0, "d50_esperado": 0.29625, "tolerancia": 1e-4},
    {"V": 4.0, "d50_esperado": 0.52666, "tolerancia": 1e-4},
]


# ---------------------------------------------------------------------------
# CP-5 · Caudal adimensional en zona de transicion (Sec. 4.2)
# ---------------------------------------------------------------------------
# q* = Ku*Q / (A_llena * D^0.5),  Ku = 1.811 (SI)
# Dato curioso verificado: el propio Q de diseno de CP-2 (Q=1.1673 m3/s,
# el que sale de Manning con n_max) da q*=3.5027 -- practicamente sobre el
# limite inferior de la zona de transicion. Por eso CP-5 usa un Q distinto
# (1.2330 m3/s) elegido para caer CLARAMENTE dentro de la zona de
# transicion (3.5 < q* < 4.0), y no justo en el borde.

CP5_TRANSICION_HDS5 = {
    "D": 0.90,
    "Q": 1.2330,                     # m3/s -- elegido para caer en transicion
    "A_llena_esperada": 0.63617,      # m2, pi*D^2/4
    "Ku": 1.811,
    "q_estrella_esperado": 3.70,
    "tolerancia": 0.02,
    "zona": "transicion",            # 3.5 < q* < 4.0
    "nota": "El test debe fallar si el modulo devuelve el valor puro de la "
            "forma no sumergida o de la sumergida en vez de interpolar entre "
            "ambas.",
}

# ---------------------------------------------------------------------------
# CP-5T · El PUNTO MEDIO de la recta de transicion, Forma 1 (EXT-M-04, PC-19)
# ---------------------------------------------------------------------------
# CALCULADO A MANO desde las ecuaciones del num. A.2 de HDS-5 y de la Sec. 4.2
# de la hoja de ruta (enmendada en EXT-0), NUNCA desde la salida del codigo.
# Carta del concreto reforzado (Tabla A.1, Carta 1 escala 1, «Square edge
# w/headwall», Forma 1): K = 0.0098, M = 2.0, c = 0.0398, Y = 0.67, Ks = -0.5.
#
# El extremo inferior de la recta es «la rama no sumergida en q* = 3.5», y la
# rama no sumergida en q* = 3.5 es la del CAUDAL que corresponde a q* = 3.5:
#
#     A_llena = pi*0.90^2/4                        = 0.636172512 m2
#     Q_lo    = 3.5 * A_llena * sqrt(0.90) / 1.811 = 1.166395268 m3/s
#
# y su H_c es el de ESE caudal, no el del caudal real del punto. Con
# Q^2*T/(g*A^3) = 1 sobre la circular (el segundo Brent de M4) sale
#
#     theta_c = 4.012418 rad -> y_c = 0.639803 m, A_c = 0.483699 m2,
#     V_c = Q_lo/A_c = 2.411405 m/s,  H_c = y_c + V_c^2/(2g) = 0.936177851 m
#
# Con S = 0.005 (la pendiente del caso patron CP-2):
#
#     lo = H_c/D + K*3.5^M + Ks*S = 1.040197612 + 0.12005 - 0.0025
#        = 1.157747612            -> HW_lo = lo * D = 1.041972851 m
#     hi = c*4.0^2 + Y + Ks*S     = 0.6368 + 0.67 - 0.0025
#        = 1.3043                 -> HW_hi = hi * D = 1.17387 m
#
# En q* = 3.75, el punto medio de la ventana, la recta vale la MEDIA EXACTA de
# los dos extremos: HW = (1.041972851 + 1.17387)/2 = 1.107921425 m.
#
# LO QUE EL CODIGO DABA HASTA EXT-2 (y lo que la auditoria externa midio):
# 1.129037883 m, porque evaluaba el extremo inferior con el H_c del caudal REAL
# (Q = 1.249709 m3/s, el de q* = 3.75), de modo que el extremo se movia con q*
# y la «recta» era una curva. El error era conservador (+1.9 %) y solo de la
# Forma 1: la ec. (A.2) no lleva H_c.
CP5T_PUNTO_MEDIO_TRANSICION = {
    "D": 0.90,
    "S": 0.005,
    "q_estrella": 3.75,                       # el punto medio de (3.5, 4.0)
    "Q_lo_esperado": 1.166395268,             # 3.5*A_llena*sqrt(D)/Ku
    "H_c_lo_esperado": 0.936177851,           # H_c(Q_lo), no H_c(Q real)
    "HW_lo_esperado": 1.041972851,            # m, extremo inferior * D
    "HW_hi_esperado": 1.17387,                # m, extremo superior * D
    "HW_esperado": 1.107921425,               # m, media exacta de los extremos
    "HW_con_extremo_movil": 1.129037883,      # m, lo que daba el codigo
    "tolerancia": 1e-9,                       # los dorados llevan 9 decimales
    "tolerancia_linealidad": 1e-12,           # segundas diferencias en la ventana
    # La misma propiedad, en la ventana entera: paso de q* con que se barre.
    "paso_q_estrella": 0.05,
}

# Caso adicional para las ramas puras, con el mismo D:
CP5B_NO_SUMERGIDO = {"D": 0.90, "Q": 0.8998, "q_estrella_aprox": 2.70, "zona": "no_sumergido"}
CP5C_SUMERGIDO = {"D": 0.90, "Q": 1.3997, "q_estrella_aprox": 4.20, "zona": "sumergido"}


# ---------------------------------------------------------------------------
# CP-5D · HDS-5 FORMA 2 (ec. A.2) -- las cuatro ramas y el defecto que las mira
# ---------------------------------------------------------------------------
# Calculados A MANO desde las ecuaciones del num. A.2 de HDS-5, NUNCA desde la
# salida del codigo:
#
#     Forma 1   HW/D = H_c/D + K*(q*)^M + Ks*S      ec. (A.1)
#     Forma 2   HW/D = K*(q*)^M                     ec. (A.2)  <-- SIN Ks*S
#     sumergida HW/D = c*(q*)^2 + Y + Ks*S          ec. (A.3)  <-- comun a las dos
#
# LA CARTA ES LA 9 ESCALA 1 de la Tabla A.1 -- «45° wingwall flare d = .043D»,
# K = 0.510, M = 0.667, c = 0.0309, Y = 0.80, Equation Form 2 --, transcrita en
# C2 y verificada contra el PDF.
#
# ADVERTENCIA QUE HAY QUE LEER ANTES DE USAR ESTOS CASOS: la carta 9 es de
# CAJON RECTANGULAR y estos casos la evaluan sobre una seccion circular. Eso
# NO es un diseño y seria justamente lo que el num. A.3 prohibe -- «coefficients
# for rectangular (box) shapes should not be used for nonrectangular ... shapes
# and vice-versa» --. Es una SONDA DE LA ECUACION: aisla la bifurcacion por
# forma de la forma de la seccion, que es lo unico que se puede probar en C3
# porque `SeccionRectangular` la implementa C4. Cuando C4 llegue, estos casos
# se repiten sobre la seccion que les corresponde; el numero de la ecuacion no
# cambia, porque la ecuacion no mira la forma: mira q*, K y M.

CP5D_FORMA2 = {
    "carta": "Tabla A.1, Carta 9 escala 1 -- 45° wingwall flare d = .043D",
    "K": 0.510, "M": 0.667, "c": 0.0309, "Y": 0.80, "Ks": -0.5,
    "forma": 2,
    # Las tres tolerancias que los tests de esta familia necesitan, DECLARADAS
    # AQUI y no escritas a mano al lado del assert: es lo que manda
    # `tests/apoyo/aproximacion.py` y lo que la guardia de cupo de
    # `test_guardias_de_la_suite` persigue. Cada una dice de que igualdad
    # habla, que es lo que un `abs=1e-15` suelto no dice:
    "tolerancia_identidad": 1e-15,    # dos vias que deben dar el MISMO numero
    "tolerancia_distincion": 1e-9,    # dos numeros que deben DIFERIR
    "tolerancia_continuidad": 1e-12,  # relativa, en el empalme de la recta
    # -- rama NO SUMERGIDA, ec. (A.2). q*^M = 1.9396332961359162
    "no_sumergido": {
        "q_estrella": 2.70, "S": 0.030,
        "hw_sobre_D_esperado": 0.9892129810293173,
        "tolerancia": 1e-12,
        # El mismo caso resuelto con la Forma 1 SIN el H_c/D -- es decir,
        # dejandose el Ks*S por copiar la (A.1) -- daria esto. La diferencia
        # es exactamente -Ks*S = +0.015 y NO depende de q*.
        "hw_sobre_D_si_se_cuela_Ks_S": 0.9742129810293173,
    },
    # -- rama SUMERGIDA, ec. (A.3): comun a las dos formas y SI lleva Ks*S
    "sumergido": {
        "q_estrella": 4.20, "S": 0.030,
        "hw_sobre_D_esperado": 1.3300760000000003,
        "tolerancia": 1e-12,
    },
    # -- rama de TRANSICION con la Forma 2 en el extremo inferior.
    # La recta va del valor de la ec. (A.2) en q* = 3.5 al de la (A.3) en 4.0:
    #     Forma2(3.5)    = 1.176152298622456
    #     Sumergida(4.0) = 1.2794
    #     peso           = (3.70 - 3.5)/(4.0 - 3.5) = 0.4
    "transicion": {
        "q_estrella": 3.70, "S": 0.030,
        "extremo_inferior_esperado": 1.176152298622456,
        "extremo_superior_esperado": 1.2794,
        "hw_sobre_D_esperado": 1.2174513791734736,
        "tolerancia": 1e-12,
    },
}

# LA TRANSICION BAJO FORMA 2 PUEDE DECRECER CON EL CAUDAL, y hay que fijarlo
# porque no lo atrapa ninguna guardia: `_resolver_hw_fuera_de_rango` solo mira el
# signo y aqui el numero es positivo. Lo encontro la auditoria de C3.
#
# Con Forma 1 los DOS extremos de la recta llevan Ks*S y el termino se cancela
# en la diferencia: la pendiente de la recta no depende de S. Con Forma 2 el
# extremo inferior lo pierde, y por encima de un umbral de pendiente la recta
# BAJA al subir el caudal. Umbral exacto, para esta carta:
#
#     S* = (c*4^2 + Y - K*3.5^M) / |Ks| = 0.236495 m/m
#
# NO ES UN DEFECTO A CORREGIR: sale de combinar la (A.2), la (A.3) y la recta
# del criterio [C] `metodo_transicion_hds5`. Se DECLARA. Este caso existe para
# que si alguien cambia el metodo de transicion, el cambio de esta propiedad
# se vea en un test en vez de descubrirse en obra.
CP5D_FORMA2_TRANSICION_NO_MONOTONA = {
    "K": 0.510, "M": 0.667, "c": 0.0309, "Y": 0.80, "Ks": -0.5, "forma": 2,
    "altura_m": 0.90,
    "S_umbral": 0.23649540275508807,     # (c*16 + Y - K*3.5^M)/|Ks|
    "S_ensayada": 0.30,                  # por encima del umbral
    "HW_en_q_3_5_m": 1.0585370687602105,
    "HW_en_q_4_0_m": 1.0299600000000002,
    "delta_mm": -28.577068760210288,     # NEGATIVO: baja al subir el caudal
    "tolerancia": 1e-12,
    "nota": "Con S por DEBAJO del umbral la recta crece, que es lo esperable. "
            "El caso fija las dos mitades: que crece abajo y que decrece "
            "arriba, y donde esta la frontera.",
}


# EL CASO QUE FIJA EL DEFECTO DE C2, con la magnitud que el auditor midio.
# C2 escribio en el docstring de `ConstantesHDS5` que la Forma 2 era
# «HW/D = K*(q*)^M + Ks*S», y esa frase estaba a once lineas de otra que decia
# lo contrario. Nadie la habria visto sin auditar a mano: el resultado sigue
# siendo positivo y ninguna guardia de signo se dispara.
#
# Este caso existe para que un regreso ROMPA UN TEST en vez de esperar a otro
# auditor. La altura de 2.00 m y la S de 0.030 no son de proyecto: estan para
# que la diferencia salga en milimetros redondos y sea legible en el mensaje.
CP5D_FORMA2_KS_ESPUREO = {
    "K": 0.510, "M": 0.667, "Ks": -0.5, "forma": 2,
    # q* del caso que describen los docstrings -- cajon 2.00 x 2.00 m,
    # Q = 8 m3/s, Ku = 1.811 -> q* = 1.811*8/(4.0*sqrt(2)) --, escrito con
    # TODOS sus digitos. La primera version puso 2.5613 redondeado, y el
    # quinto digito no se reproducia desde los datos que el docstring da: son
    # 0.08 mm de diferencia, invisibles a tres decimales y suficientes para
    # que un revisor que rehaga la cuenta no llegue al mismo numero.
    "q_estrella": 2.5611407614576747,
    "S": 0.030,
    "altura_m": 2.00,
    "hw_sobre_D_correcto": 0.9549822202443748,     # K*q^M
    "hw_sobre_D_con_Ks_espureo": 0.9399822202443748,  # K*q^M + Ks*S
    "HW_correcto_m": 1.9099644404887497,
    "HW_con_Ks_espureo_m": 1.8799644404887497,
    "delta_mm_esperado": 30.0,          # y con S = 0.08 son 80 mm: crece lineal
    "tolerancia": 1e-12,
    "tolerancia_mm": 1e-6,              # la del delta, que va en milimetros
    "nota": "La diferencia va SIEMPRE en la direccion NO conservadora: con "
            "Ks = -0.5 el termino resta, de modo que el HW espureo es MENOR "
            "que el real y V4, V4b y el tamizado de 7.A pasan mas facil.",
}


# ---------------------------------------------------------------------------
# CP-6 · Tirante critico -- autoconsistencia (no hay valor cerrado)
# ---------------------------------------------------------------------------
# Q^2 * T / (g * A^3) = 1   en y = y_critico
# Froude = V / sqrt(g*A/T) debe valer 1.000 en y_critico.

CP6_TIRANTE_CRITICO = {
    "D": 0.90,
    "Q_casos": [0.30, 0.60, 1.00, 1.50],   # m3/s, varios caudales de prueba
    "residuo_maximo_admisible": 1e-6,       # |Q^2*T/(g*A^3) - 1|
    "froude_esperado": 1.0,
    "froude_tolerancia": 1e-4,
}


# ---------------------------------------------------------------------------
# CP-7 · Cadena sismica desagregada (Sec. 9.2)
# ---------------------------------------------------------------------------

CP7_CADENA_SISMICA = {
    "PGA": 0.50,
    "F_pga": 1.0,
    "factor_muro_rigido": 1.0,
    "factor_muro_desplazable": 0.5,

    "A_s_esperado": 0.50,
    "k_h0_esperado": 0.50,
    "k_h_con_muro_rigido_esperado": 0.50,
    "k_h_con_muro_desplazable_esperado": 0.25,   # 0.5 * k_h0 -- prueba que
                                                   # la cadena esta desagregada
                                                   # y no hardcodeada en 0.50
    "k_v_esperado": 0.0,

    # Rama de sensibilidad de la MISMA cadena: si el SPT cerrara la clase de
    # sitio en E, F_pga baja a 0.9 (F_PGA_TABLA["E"]) y TODA la cadena se
    # mueve. Es el detector de un k_h = 0.50 escrito a mano, y sus dorados
    # viven aqui y no como literales en tests/test_M9_cabezal.py (SIS-F-14).
    "F_pga_clase_E": 0.9,
    "A_s_con_F_pga_clase_E_esperado": 0.45,          # 0.9 * 0.50
    "k_h_con_F_pga_clase_E_esperado": 0.45,          # muro rigido: 1.0 * k_h0
}


# ---------------------------------------------------------------------------
# CP-8 · Constante del control de salida -- SI vs. imperial (Sec. 4.3)
# ---------------------------------------------------------------------------
# H = (1 + ke + K_friccion*n^2*L/R^(4/3)) * V^2/(2g)
# K_friccion = 19.63 en SI. Usar 29 (valor ingles) es el error clasico.
#
# El 19.63 es la conversion SI que HDS-5 declara para su K = 29 -- pero SOLO
# en una de las dos copias del manual que hay en normas/, y esta linea decia
# "el propio HDS-5 declara" sin esa salvedad (MAT-O12, MAT-X5):
#
#   hif12026.pdf (3a ed., 2012), num. 3.1.4, ec. (3.4b), pag. impresa 3.10:
#       "KU = 29 in English Units (19.63 in SI)"    <- de aqui sale el 19.63
#   fhwa_culvert_hydraulics_hds5si.pdf (ed. de 1985, la que lleva "si" en el
#       nombre del archivo): sus ecs. (4b) y (5), en la pag. 54 del PDF,
#       imprimen "29 n^2 L / R^1.33" con rotulos duales "ft (m)", y su
#       gravedad, en la pag. 53, es "32.2 ft/s/s (9.8 m/s/s)". No imprime
#       19.63 en ninguna de las dos. Leida literal "en SI" reproduce
#       exactamente el error del 29 (+9.6 %) que este caso patron atrapa.
#
# El 19.63 sustituye al 19.62 que este fixture uso hasta ahora, justificado
# entonces como "2*g". La correccion del VALOR se mantiene; la de la RAZON no:
# el parecido con 2*g no era una coincidencia, es exacto -- K = 2*g/phi^2 con
# phi = 1.486 en el sistema ingles y 1 en SI, de modo que 2*32.2/1.486^2 =
# 29.16 y 2*9.81456 = 19.629 --, y lo unico que separa 19.63 de 19.62 es cual
# g: la de HDS-5 son 32.2 ft/s^2 = 9.81456 m/s^2 y la del proyecto es 9.81.
# Los valores dorados de abajo estan recalculados con 19.63; el cambio mueve H
# en 5e-5 m, tres ordenes por debajo del salto que este caso patron existe
# para atrapar.

CP8_CONTROL_SALIDA = {
    "n": 0.013,
    "L": 20.0,       # m
    "R": 0.27152,    # m, de CP-2
    "ke": 0.5,
    "V": 2.2807,     # m/s, de CP-2 (rama n_max) -- velocidad, no caudal
    "K_friccion_SI_correcto": 19.63,
    "K_friccion_imperial_incorrecto": 29.0,

    "H_esperado_con_K_SI": 0.49772,    # m, verificado con calculo independiente
    "H_con_29_incorrecto": 0.54548,    # m, para comparacion en el test
    "nota": "test_constante_friccion_es_SI_no_imperial debe fallar si el "
            "modulo usa 29 en vez de 19.63. Con estos datos la diferencia "
            "entre ambas H es de ~9.6% (0.4977 m vs 0.5455 m) -- suficiente "
            "para que el test lo detecte con una tolerancia estrecha, pero "
            "no tan grande como para notarse 'a ojo' en una revision "
            "manual descuidada. Es exactamente el tipo de error silencioso "
            "que este caso patron existe para atrapar. La clave del valor "
            "dorado se llama 'H_esperado_con_K_SI' y no lleva el numero en "
            "el nombre a proposito: el nombre anterior "
            "('H_esperado_con_19_62') habria quedado mintiendo al corregir "
            "la constante. Los dos valores usan g = 9.81 "
            "(constantes_fisicas.G), no los 9.8 de G_LAUSHEY: recalculados "
            "tras separar la gravedad generica de la de Laushey.",
}


# ---------------------------------------------------------------------------
# CP-9 · Mononobe-Okabe con los CUATRO angulos no nulos (Sec. 9.2)
# ---------------------------------------------------------------------------
#                 cos^2(phi - psi - beta)
# K_AE = ----------------------------------------------------------
#        cos(psi) cos^2(beta) cos(delta + beta + psi) [1 + R]^2
#
#              /  sen(phi + delta) sen(phi - psi - i)
# con   R = _ /  --------------------------------------      psi = atan[k_h/(1-k_v)]
#          V    cos(delta + beta + psi) cos(i - beta)
#
# POR QUE EXISTE ESTE CASO (SIS-F-04). El unico contraste de valor que tenia
# Mononobe-Okabe era su caso limite de Rankine: i = beta = delta = 0 y
# k_h = k_v = 0. En ese punto la formula es CIEGA a los signos, porque los
# cuatro cosenos tienen argumento nulo y cos es par: cos(i-beta) y cos(i+beta)
# valen los dos 1, cos(delta+beta+psi) y cos(delta+beta-psi) valen los dos 1,
# y phi-psi-beta = phi+psi-beta = phi. Medido: de quince mutantes de signo de
# la formula, DOCE dejan el caso limite intacto hasta el ultimo bit. El
# docstring de la funcion decia "es la comprobacion que garantiza que los
# signos estan bien puestos" y el del test "si un signo esta cambiado, aqui se
# ve": las dos afirmaciones eran falsas.
#
# Los tres casos de abajo tienen phi, i, beta, delta, k_h y k_v distintos
# entre si y distintos de cero, que es la unica configuracion en la que cada
# suma y cada resta de la formula deja huella en el resultado. Con estos
# dorados, el mutante que menos se aparta lo hace en 3.7e-3 relativo
# (CP9-B, cos_dbp*cos_ib -> cos_dbp/cos_ib), nueve ordenes por encima de la
# tolerancia 1e-12 que se propone.
#
# AUTOVERIFICADOS por el bloque __main__ de este archivo: formula cerrada,
# recomputada ahi con math y sin importar ningun modulo del repo.
#
# 'K_AE_errata_1_menos_R_esperado' NO es un valor a producir: es el valor que
# saldria de escribir el denominador [1 - R] que el Manual de Puentes imprime
# por errata (Apendice A11, num. A.11.3.1, pag. impresa 586). El codigo sigue
# a AASHTO con [1 + R] (Art. A11.3.1, ec. A11.3.1-1) y esta declarado en
# constantes_normativas.K_AE_ERRATA_MANUAL. El dorado esta aqui para que un
# test pueda exigir que el modulo NO lo produzca.

CP9_MONONOBE_OKABE = (
    {
        "nombre": "CP9-A",
        "phi_grados": 40.0, "i_grados": 5.0,
        "beta_grados": 20.0, "delta_grados": 25.0,
        "k_h": 0.15, "k_v": 0.05,
        "psi_esperado": 8.972626614896393,
        "K_AE_esperado": 0.5567083864792189,
        "K_A_esperado": 0.40338013713689563,
        "K_AE_errata_1_menos_R_esperado": 70.38546372456175,
        "nota": "El mas discriminante de los tres: el mutante mas cercano "
                "(cos(i-beta) -> cos(i+beta)) se aparta 2.9e-2 relativo.",
    },
    {
        "nombre": "CP9-B",
        "phi_grados": 38.0, "i_grados": 12.0,
        "beta_grados": 6.0, "delta_grados": 20.0,
        "k_h": 0.20, "k_v": 0.10,
        "psi_esperado": 12.528807709151511,
        "K_AE_esperado": 0.5203195665286864,
        "K_A_esperado": 0.2990004513187056,
        "K_AE_errata_1_menos_R_esperado": 4.7818805476967166,
        "nota": "Invierte el orden relativo de i y beta respecto de CP9-A "
                "(aqui i > beta): cos(i-beta) cambia de lado.",
    },
    {
        "nombre": "CP9-C",
        "phi_grados": 40.0, "i_grados": 5.0,
        "beta_grados": 15.0, "delta_grados": 22.0,
        "k_h": 0.50, "k_v": 0.10,
        "psi_esperado": 29.054604099077146,
        "K_AE_esperado": 1.3753494480822512,
        "K_A_esperado": 0.3393072702172859,
        "K_AE_errata_1_menos_R_esperado": 11.045723439981058,
        "nota": "k_h = 0.50, el de la cadena sismica de CP-7. psi = 29.05 "
                "grados deja phi-psi-i = 5.95: cerca del borde del dominio, "
                "que es donde el proyecto va a operar de verdad.",
    },
)

# Caso limite de Rankine, con su dorado y con el valor que produce la errata
# del Manual: con [1 - R] y todos los angulos nulos, K_AE resulta ser el
# RECIPROCO EXACTO del Ka de Rankine ((1+sen phi)/(1-sen phi) en vez de
# (1-sen phi)/(1+sen phi)), no un valor parecido. Verificado en el bloque
# __main__: |K_AE(1-R) * Ka - 1| < 1e-15 para los cinco phi.
CP9_RANKINE_LIMITE = {
    "phi_casos": (25.0, 30.0, 34.0, 38.0, 42.0),
    "Ka_rankine_esperado": (0.4058585172053274, 0.3333333333333333,
                            0.28271491971777274, 0.23788307794915586,
                            0.19822858222156756),
    "K_AE_errata_1_menos_R_esperado": (2.4639128110106694, 3.0000000000000004,
                                       3.537132037454108, 4.203745842794819,
                                       5.04468118973006),
}

# La tolerancia de TODOS los casos CP-9. Vivio un tiempo tambien como clave
# `tolerancia_relativa` dentro de CP9_RANKINE_LIMITE, con el mismo valor y sin
# un solo lector: dos nombres para una cosa, y el que nadie leia podia
# cambiarse sin que ningun test lo notara. Se retiro la clave muerta.
CP9_TOLERANCIA_RELATIVA = 1e-12


# ---------------------------------------------------------------------------
# CP-9 · Empuje del trasdos: estatico, sismico total e incremento (Sec. 9.2)
# ---------------------------------------------------------------------------
# P_A   = gamma * H^2 * K_A / 2
# P_AE  = gamma * H^2 * (1 - k_v) * K_AE / 2
# dP_AE = P_AE - P_A
#
# POR QUE EXISTE (SIS-F-05). CP-7 cubre la cadena sismica y se detiene en el
# COEFICIENTE: ningun caso patron llegaba al EMPUJE. Sin dorado, cuatro
# mutantes de `empuje_activo_sismico_total` sobrevivian a la suite entera,
# porque el unico assert que la tocaba --
#     assert incremento == pytest.approx(P_AE - P_A)
# -- llama a las MISMAS dos funciones en los dos lados de la igualdad: el
# mutante se propaga identico a ambos y la igualdad se cumple igual. No era un
# assert debil, era una tautologia.
#
# EL BLOQUE A ES DELIBERADAMENTE INDEPENDIENTE DE MONONOBE-OKABE: prueba la
# formula cerrada del empuje con cuatro entradas dadas, todas distintas entre
# si y ninguna igual a 1 ni a 2, para que multiplicar frente a dividir y el
# signo de (1 - k_v) den numeros separados por un 35 % como minimo. k_v = 0.15
# NO es el k_v del proyecto (ese es 0.0, criterio 'k_v', CP-7): es el valor DE
# PRUEBA que hace visible el factor (1 - k_v). Con k_v = 0 el factor vale 1 y
# el mutante (1 + k_v) es indetectable por construccion -- y k_v = 0.0 era
# justamente lo que usaba el test viejo.
#
# El bloque B es la cadena coherente: los mismos angulos llevados desde phi
# hasta el empuje y el incremento, para que el contraste no dependa de un K_AE
# inventado. k_h = 0.25 (muro desplazable de CP-7) y no 0.50: con 0.50 y k_v
# distinto de cero, phi - psi - i queda a 3 grados del limite de existencia de
# la formula y el dorado seria de mala condicion.
#
# DORADOS: double exacto redondeado a 9 decimales; el residuo relativo maximo
# es 1.0e-9 (en B_K_A_esperado). La tolerancia declarada abajo, 1e-7, lo cubre
# con dos ordenes de margen y sigue siendo seis ordenes mas estrecha que la
# separacion del mutante mas cercano. Autoverificados por el bloque __main__
# de este archivo, recalculando sin importar ningun modulo del repo.

CP9_EMPUJE_TRASDOS = {
    # --- Bloque A: formula cerrada de P_AE, con K_AE DADO -----------------
    "A_gamma_relleno": 18.5,          # kN/m3
    "A_H": 2.4,                       # m
    "A_K_AE": 0.55,                   # adimensional, dado (no sale de M-O)
    "A_k_v": 0.15,                    # de prueba; el del proyecto es 0.0
    "A_P_AE_esperado": 24.908400000,  # kN/m

    # Los cuatro mutantes que sobrevivian, con el valor que devuelven. No son
    # dorados: son la MEDIDA DE LA SEPARACION -- el mas cercano queda a +35 %,
    # de modo que la tolerancia de 1e-7 no tiene nada que ver con si mueren.
    "A_mutante_1_mas_kv": 33.699600000,    # (1 - k_v)   -> (1 + k_v)
    "A_mutante_por_dos": 99.633600000,     # K_AE / 2    -> K_AE * 2
    "A_mutante_divide_kv": 34.475294118,   # * (1 - k_v) -> / (1 - k_v)
    "A_mutante_divide_KAE": 82.341818182,  # * K_AE      -> / K_AE

    # --- Bloque B: cadena coherente phi -> K_AE -> P_AE -> dP_AE ----------
    "B_phi_grados": 34.0,
    "B_i_grados": 0.0,
    "B_beta_grados": 0.0,
    "B_delta_grados": 0.0,
    "B_k_h": 0.25,
    "B_k_v": 0.15,
    "B_gamma_relleno": 18.5,               # kN/m3
    "B_H": 2.4,                            # m
    "B_psi_grados_esperado": 16.389540334,
    "B_K_AE_esperado": 0.489557368,
    "B_K_A_esperado": 0.282714920,         # Coulomb con k = 0; con i=beta=
                                           # delta=0 coincide con Rankine
    "B_incremento_K_esperado": 0.206842448,
    "B_P_AE_esperado": 22.171074072,       # kN/m
    "B_P_A_esperado": 15.063050923,        # kN/m
    "B_incremento_P_esperado": 7.108023149,   # kN/m
    "B_brazo_fraccion": 0.6,               # 'punto_aplicacion_incremento_sismico'
    "B_z_incremento_esperado": 1.440000000,   # m; el mutante `/ H` daria 0.25

    # --- Bloque C: Coulomb con angulos NO nulos, dentro de las ventanas ---
    # EXT-M-06. Los bloques A y B tienen i = beta = delta = 0, donde Coulomb y
    # Rankine coinciden hasta el ultimo bit: un empuje estatico calculado con
    # cualquiera de los dos pasaba. Este bloque pone los tres angulos distintos
    # de cero y DENTRO de las ventanas de sensibilidad de sus criterios (i y
    # beta en 0-10 grados, delta en 0-22.7; el i = 20 de la auditoria no es
    # declarable), con phi = 34 y delta = phi/2 -- concreto contra granular --.
    # k_h = 0.25 y k_v = 0.05 dejan phi - psi - i = 14.3 grados, lejos del
    # borde del dominio; con el k_h = 0.50 de la obra, psi = 26.6 y la ventana
    # de i no es alcanzable entera (i < phi - psi: 3.4 grados con phi = 30).
    #
    # DORADOS por recomputacion INDEPENDIENTE en el bloque __main__: el Ka se
    # recalcula con la escritura del Manual de Puentes (num. 2.4.4.1.5.3, ecs.
    # -1 y -2, con theta medido desde la HORIZONTAL: theta = 90 - beta), que
    # es algebraicamente distinta de la de Mononobe-Okabe con k = 0 que usa
    # M9; coinciden a 5.6e-17. Double exacto redondeado a 9 decimales.
    "C_phi_grados": 34.0,
    "C_i_grados": 5.0,
    "C_beta_grados": 5.0,
    "C_delta_grados": 17.0,
    "C_k_h": 0.25,
    "C_k_v": 0.05,
    "C_gamma_relleno": 18.5,               # kN/m3
    "C_H": 2.4,                            # m
    "C_K_A_coulomb_esperado": 0.310057323,     # MP 2.4.4.1.5.3, theta = 85
    "C_K_A_rankine_esperado": 0.282714920,     # tan^2(45 - phi/2): NO es el Ka
    "C_diferencia_relativa_coulomb_rankine": 0.096713691,   # +9.67 %
    "C_psi_grados_esperado": 14.743562836,
    "C_K_AE_esperado": 0.551134269,
    "C_P_A_esperado": 16.519854173,        # kN/m, con el Ka de COULOMB
    "C_P_AE_esperado": 27.896212172,       # kN/m
    "C_incremento_P_esperado": 11.376357999,   # kN/m

    # Tolerancia RELATIVA del contraste. Vive aqui y no como literal en
    # tests/test_M9_cabezal.py por la misma razon que los dorados (SIS-F-14).
    "tolerancia_relativa": 1e-7,
}

# ---------------------------------------------------------------------------
# CP-9 · Sec. 7.B -- longitud del conducto, proyeccion de taludes y cota de
#        salida (SIS-F-08 / SIS-F-13)
# ---------------------------------------------------------------------------
# Las tres son IDENTIDADES GEOMETRICAS, no valores normativos. Sec. 7.B fija
# COMO se obtienen -- "longitud = ancho de plataforma + proyeccion de taludes,
# afectada por esviaje", "cotas de entrada y salida amarradas al perfil del
# cauce y a la cota de fondo del receptor" -- y no da ningun ejemplo numerico:
# se busco en docs/hoja_de_ruta_alcantarillas_v8.md y la Sec. 7.B no tiene
# tabla ni cifra que copiar. Por eso este caso es un RECALCULO INDEPENDIENTE
# de las formulas que la propia Sec. 7.B escribe, no una cita:
#
#     altura      = cota_rasante - cota_terreno
#     proyeccion  = 2 * talud * altura
#     longitud    = (ancho_plataforma + proyeccion) / cos(esviaje)
#     caida       = S * longitud
#     cota_salida = cota_entrada - caida
#
# EL TALUD DE ESTE CASO NO ES UN VALOR DE PROYECTO Y NO CIERRA NINGUN VACIO.
# 'talud_terraplen' sigue en valor=None en criterios_adoptados.py, a proposito
# (Sec. 7.B pide la proyeccion y no da la inclinacion), y este fixture no lo
# toca: los tests lo declaran EN CALIENTE, solo para su duracion, con
# `establecer_valor_dinamico`, y lo retiran al salir. El 2.5 esta elegido para
# que los tres errores tipicos den resultados que un assert pueda separar --
#
#     2 * talud = 5.00      2 / talud = 0.80      talud^2 = 6.25
#
# -- cosa que no consiguen ni el 1.5 "de practica corriente" que el criterio
# prohibe adoptar en silencio (2*t = 3.00 contra t^2 = 2.25) ni el 2.0, con el
# que 2*t y t^2 colapsan en 4.00. El talud REAL sale de la seccion tipica del
# expediente vial (DG-2018) y lo declara el proyectista.
#
# Los 30 grados de esviaje separan multiplicar de dividir por el coseno: el
# factor vale 1.15470054 y el error da 20.8712122 m donde lo correcto son
# 27.828283 m, o sea un conducto MAS CORTO que el mismo cruce perpendicular
# (24.10 m), que es geometricamente imposible.
#
# Autoverificado por el bloque `__main__` de este archivo: formula cerrada,
# sin scipy.

CP9_GEOMETRIA_7B = {
    # --- entradas (las cinco columnas de Sec. 1.2 que 7.B necesita) --------
    "ancho_plataforma": 9.60,        # m
    "cota_terreno": 42.10,           # msnm
    "cota_rasante": 45.00,           # msnm
    "cota_subrasante": 44.85,        # msnm  (e_paq = 0.15 m)
    "cota_fondo_receptor": 41.30,    # msnm
    "S": 0.006,                      # pendiente del diseno (ResultadoHidraulico.S)

    # --- declaracion en caliente de la corrida de pruebas, NO del proyecto -
    "talud_de_prueba": 2.5,          # H:V

    # --- dorados -----------------------------------------------------------
    "altura_terraplen_esperada": 2.90,      # m   45.00 - 42.10
    "proyeccion_esperada": 14.50,           # m   2 * 2.5 * 2.90

    "esviaje_perpendicular_grados": 0.0,
    "factor_esviaje_perpendicular_esperado": 1.0,
    "longitud_perpendicular_esperada": 24.10,       # m   9.60 + 14.50

    "esviaje_oblicuo_grados": 30.0,
    "factor_esviaje_oblicuo_esperado": 1.15470054,
    "longitud_oblicua_esperada": 27.828283,         # m   24.10 / cos(30)
    # El error clasico, para que el test pueda decir de que se defiende:
    "longitud_oblicua_si_multiplica_por_el_coseno": 20.8712122,

    "cota_entrada_esperada": 42.10,   # msnm, con 'origen_cota_fondo_entrada'
                                      # = "cota_terreno" (la de la corrida)
    "caida_oblicua_esperada": 0.1669697,        # m     0.006 * 27.828283
    "cota_salida_oblicua_esperada": 41.9330303,  # msnm  42.10 - 0.1669697

    # Tolerancias nombradas: el proyecto prohibe comparar floats sueltos. Son
    # 0.1 mm en longitud y 0.01 mm en cota -- tres a cinco ordenes por encima
    # del error de doble precision del propio dorado (2.5e-8 y 2.2e-9) y seis
    # a nueve ordenes por debajo del salto que cualquiera de los mutantes
    # produce (el mas cercano se aparta 3.73 m en longitud y 0.33 m en cota).
    "tolerancia_longitud": 1e-4,     # m
    "tolerancia_cota": 1e-5,         # m
}


# ---------------------------------------------------------------------------
# Indice para iterar todos los casos desde un solo import
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CP-9 · Ensamble de empujes del trasdos CON AGUA (M9.empujes_trasdos)
# ---------------------------------------------------------------------------
#
# Por que existe, y por que CON AGUA. El unico test que ejercitaba
# `empujes_trasdos` de punta a punta usaba un tablero con `D_f = 1.00` y el NF
# a 1.40 m: `h_agua = max(1.00 - 1.40, 0) = 0`, de modo que TODA la rama del
# agua corria en cero y el propio test lo escribia
# (`assert E_hidrostatico == approx(0.0)`). El resto de los asserts eran de
# ORDEN (`sismico > estatico`) y de BRAZO (`z_activo == H/3`). Resultado
# medido en una revision adversarial: once mutantes del ENSAMBLADOR sobrevivian
# --- anular la hidrostatica y la subpresion, partir h_agua por dos, pasar
# `B=D_f` a la subpresion, y pasar `H=geometria.H` en vez de `altura_empuje` a
# los tres empujes y al incremento sismico. El peor, `k_v=mo.k_h`, bajaba el
# incremento sismico un 80.6 % y era NO CONSERVADOR.
#
# El tablero cambia `D_f` de 1.00 a 2.00 para que haya 0.60 m de agua sobre la
# base. Los dorados salen de la formula y NO del modulo, y el bloque
# `__main__` los recalcula.
CP9_ENSAMBLE_TRASDOS = {
    "nombre": "Ensamble de empujes con 0.60 m de agua sobre la base",
    # Geometria del cabezal de tanteo (no es propuesta de proyecto).
    "H": 2.00,
    "B": 1.60,
    "D_f": 2.00,
    "espesor_zapata": 0.40,
    "altura_empuje": 2.40,          # H + espesor_zapata
    "NF_profundidad_m": 1.40,
    "h_agua_esperada": 0.60,        # D_f - NF
    # Datos de prueba (los mismos que el test declara en caliente).
    "gamma_relleno": 19.0,
    "phi_grados": 34.0,
    "gamma_agua": 9.81,
    # h_eq de AASHTO 3.11.6.4 para muro paralelo al trafico, borde a 1.0 m y
    # altura de tabla 2.40 m. Es LECTURA DE TABLA, no formula: por eso se
    # escribe aqui como entrada del recalculo y no se deduce.
    "h_eq": 0.6096,
    # La misma lectura con la orientacion PERPENDICULAR, donde la tabla SI
    # depende de la altura: 1.204 / 1.124 / 1.044 m para 1.60 / 2.00 / 2.40 m.
    # Existe para poder ver `altura_para_h_eq`: con el tablero paralelo la
    # tabla devuelve 0.6096 para las tres alturas, de modo que un ensamblador
    # que pasara `geometria.H` o `H - espesor_zapata` en vez de
    # `H + espesor_zapata` daba el mismo numero y era invisible.
    "h_eq_perpendicular_a_2_40": 1.044,
    "h_eq_perpendicular_a_1_60": 1.204,
    # Dorados. Formula cerrada, recalculados en `__main__`:
    #   Ka       = tan^2(45 - phi/2)
    #   E_activo = 0.5 * gamma * Ka * He^2
    #   E_sobrec = gamma * Ka * h_eq * He
    #   E_hidro  = 0.5 * gamma_agua * h_agua^2
    #   U        = gamma_agua * h_agua * B
    "Ka_esperado": 0.28271491971777274,
    "E_activo_esperado": 15.470160406956524,
    "E_sobrecarga_esperado": 7.858841486733915,
    "E_hidrostatico_esperado": 1.7658,
    "U_subpresion_esperado": 9.4176,
}


TODOS_LOS_CASOS = {
    "CP1_PERIODO_RETORNO": CP1_PERIODO_RETORNO,
    "CP2_GEOMETRIA_MANNING": CP2_GEOMETRIA_MANNING,
    "CP3_VELOCIDAD_MINIMA": CP3_VELOCIDAD_MINIMA,
    "CP4_LAUSHEY": CP4_LAUSHEY,
    "CP5_TRANSICION_HDS5": CP5_TRANSICION_HDS5,
    "CP5T_PUNTO_MEDIO_TRANSICION": CP5T_PUNTO_MEDIO_TRANSICION,
    "CP5B_NO_SUMERGIDO": CP5B_NO_SUMERGIDO,
    "CP5C_SUMERGIDO": CP5C_SUMERGIDO,
    "CP6_TIRANTE_CRITICO": CP6_TIRANTE_CRITICO,
    "CP7_CADENA_SISMICA": CP7_CADENA_SISMICA,
    "CP8_CONTROL_SALIDA": CP8_CONTROL_SALIDA,
    "CP9_GEOMETRIA_7B": CP9_GEOMETRIA_7B,
    "CP9_MONONOBE_OKABE": CP9_MONONOBE_OKABE,
    "CP9_RANKINE_LIMITE": CP9_RANKINE_LIMITE,
    "CP9_EMPUJE_TRASDOS": CP9_EMPUJE_TRASDOS,
    "CP9_ENSAMBLE_TRASDOS": CP9_ENSAMBLE_TRASDOS,
}


# ---------------------------------------------------------------------------
# CP-*R · LA SECCION RECTANGULAR (C4) -- las cuatro piezas sobre el marco
# ---------------------------------------------------------------------------
# CALCULADOS A MANO DESDE LA ECUACION, nunca desde la salida del codigo. La
# seccion es el marco 2.00 x 1.50 m que la §4.1 del plan de la Familia C usa
# de ejemplo, y las formulas son las de esa misma seccion:
#
#     A = B*y      P = B + 2y      R = A/P      T = B
#     A_llena = B*H          R_lleno = B*H / (2(B+H))
#
# LAS DOS "R" NO SON LA MISMA, y estos casos lo fijan a proposito: la de
# lamina libre (P = B + 2y, sin la losa) y la de seccion llena a presion
# (P = 2(B+H), con ella). En la circular las dos convergen y la distincion no
# se ve; en un marco no convergen nunca, porque el ancho de la lamina vale B
# hasta el final.
#
# NO SON DATOS DE PROYECTO: son entradas de prueba elegidas para que cada
# numero se pueda rehacer a mano en una hoja.

CP2R_GEOMETRIA_MANNING_RECTANGULAR = {
    "B": 2.00,
    "H": 1.50,
    "y": 0.90,             # y/H = 0.60, dentro del 0.75 que admite V1
    "S": 0.005,
    "n_max": 0.014,        # rama de capacidad / tirante  (fila `concreto_afinado`)
    "n_min": 0.011,        # rama de velocidad / socavacion

    "A_esperado": 1.8,                       # B*y
    "P_esperado": 3.8,                       # B + 2y
    "R_esperado": 0.4736842105263158,        # A/P
    "T_esperado": 2.00,                      # = B, CONSTANTE con el tirante
    "A_llena_esperada": 3.0,                 # B*H
    "R_lleno_esperado": 0.42857142857142855,  # B*H/(2(B+H)) -- NO es A/P al tirante H

    # V = (1/n) * R^(2/3) * S^(1/2); Q = V*A. Igual que en CP-2: NO dividir Q
    # entre A para obtener V.
    "V_con_n_max_esperado": 3.0691367451089424,
    "V_con_n_min_esperado": 3.906174039229563,
    "Q_con_n_max_esperado": 5.524446141196097,

    # El radio hidraulico de LAMINA LIBRE en y = H, para poder contrastarlo
    # con `R_lleno_esperado` y ver que no coinciden: 3.0/5.0 = 0.60 m frente a
    # 0.4285... m, un 40 %.
    "R_lamina_libre_en_H": 0.6,

    "tolerancia_geometria": 1e-12,
    "tolerancia_hidraulica": 1e-12,
    # La circular NO llega exacta al borde: su bracket se separa de theta =
    # 2*pi por TOL_THETA_BORDE = 1e-9 rad, y a esa distancia el radio
    # hidraulico de lamina libre difiere del de seccion llena en ~3.6e-11 m.
    # Es convergencia del bracket, no una diferencia de formula, y por eso
    # tiene tolerancia propia: compararla con 1e-12 seria medir el margen del
    # bracket creyendo medir la geometria.
    "tolerancia_convergencia_circular": 1e-9,
    # La del tirante que devuelve Brent. `TOL_BRENT` vale 1e-10 sobre el
    # PARAMETRO PROPIO, y en el marco ese parametro es el tirante EN METROS
    # -- en la circular es theta en radianes, que sobre un tubo de 0.90 m
    # equivale a ~1e-11 m --. O sea que aqui la tolerancia del solver se lee
    # directamente en metros, y 1e-9 m es una millonesima de milimetro.
    "tolerancia_brent": 1e-9,
}

# El tirante critico rectangular tiene solucion CERRADA, y por eso este caso
# no se parece a CP-6: alli habia que comprobar autoconsistencia porque no hay
# valor cerrado, y aqui hay tres identidades que se rehacen en una linea:
#
#     y_c = (q^2/g)^(1/3)   con q = Q/B
#     V_c = q/y_c   y   V_c^2 = g*y_c   (porque y_c^3 = q^2/g)
#     H_c = y_c + V_c^2/(2g) = 1.5*y_c  <- EXACTA, y no depende de Q ni de B
#     Froude = V_c / sqrt(g*A/T) = 1
#
# La tercera es la mas util como oraculo: H_c/y_c = 3/2 es una propiedad de la
# seccion rectangular que se demuestra en dos renglones y que ningun error de
# transcripcion de constantes reproduce por casualidad.
CP6R_TIRANTE_CRITICO_RECTANGULAR = {
    "B": 2.00,
    "H": 1.50,
    "g": 9.81,             # constantes_fisicas.G, no los 9.8 de G_LAUSHEY
    "casos": (
        {"Q": 2.00,  "q": 1.0,
         "y_c_esperado": 0.4671363512679737,
         "V_c_esperado": 2.1407025963311255,
         "H_c_esperado": 0.7007045269019605},
        {"Q": 6.00,  "q": 3.0,
         "y_c_esperado": 0.9716827674320039,
         "V_c_esperado": 3.0874273997145196,
         "H_c_esperado": 1.457524151148006},
        # EL TERCERO ERA Q = 12.00 m3/s Y HUBO QUE CAMBIARLO, y conviene
        # saber por que: daba y_c = 1.5424 m sobre un barril de H = 1.50 m, o
        # sea un tirante critico IMPOSIBLE, y este mismo fixture lo dio por
        # bueno hasta que la auditoria adversarial de C4 encontro el techo que
        # faltaba (ver `CP6R_TECHO_DEL_CRITICO`). Se sustituye por Q = 10.00,
        # que sigue siendo un caudal grande --y_c = 1.366 m, el 91 % de la
        # altura-- y cae por debajo del techo, que es lo que este caso quiere
        # medir: la formula cerrada, no el tope.
        {"Q": 10.00, "q": 5.0,
         "y_c_esperado": 1.3659149772715913,
         "V_c_esperado": 3.66054994871458,
         "H_c_esperado": 2.048872465907387},
    ),
    "H_c_sobre_y_c": 1.5,
    "froude_esperado": 1.0,
    "tolerancia": 1e-12,
    "tolerancia_identidad": 1e-14,   # H_c/y_c = 3/2 y Froude = 1
}

# EL TECHO DEL TIRANTE CRITICO, que la solucion cerrada retiro sin querer.
# En la circular el limite lo pone la geometria del bracket: y = (D/2)(1 -
# cos(theta/2)) no puede pasar de D, y por eso un Q desmedido solo acerca y_c
# a D (medido: D = 0.90 da y_c = 0.8999649945 con Q = 15 y 0.8999999823 con
# Q = 100). El despeje y_c = (q^2/g)^(1/3) no tiene ese limite.
#
# El caso que lo destapo es un punto VIABLE, y eso es lo que lo hace grave: el
# tirante normal cae dentro del 0.75 que admite V1 y ninguna verificacion se
# queja, mientras el informe imprime un area critica MAYOR que la del barril
# entero. El numero era positivo y finito, de modo que ninguna guardia de
# signo ni de finitud lo veia.
#
# El techo NO es una decision del proyecto: HDS-5 3a ed., num. 3.3.3, pag.
# impresa 3.24 (PDF 106), establece que el tirante critico no puede exceder la
# altura interior del barril, y las cartas del Apendice C lo acotan igual.
CP6R_TECHO_DEL_CRITICO = {
    "B": 2.00,
    "H": 1.50,
    "Q": 15.00,             # m3/s
    "S": 0.05,              # m/m -- pendiente alta, punto supercritico
    "n_max": 0.014,

    # Lo que hace que el caso NO se descarte antes: el punto es viable.
    "y_normal_esperado": 0.8045885708471225,
    "y_sobre_H_esperado": 0.5363923805647484,   # dentro del 0.75 de V1

    # Lo que el despeje SIN techo daba, y por que es imposible.
    "y_c_sin_techo": 1.7898549609527818,        # (7.5^2/9.81)^(1/3)
    "A_c_sin_techo": 3.5797099219055637,        # B*y_c, MAYOR que A_llena
    "A_llena": 3.0,

    # Lo que da CON el techo: el critico se topa en H y el area critica pasa a
    # ser la del barril lleno.
    "y_c_esperado": 1.50,
    "A_c_esperado": 3.0,
    "V_c_esperado": 5.0,                        # Q/A_llena, exacta
    "H_c_esperado": 2.77420998980632,           # H + V_c^2/(2g)

    # La circular, en cambio, se acota sola: dos caudales desmedidos sobre el
    # mismo tubo, y los dos por debajo de D.
    "D_circular": 0.90,
    "y_c_circular_Q15": 0.8999649945473036,
    "y_c_circular_Q100": 0.8999999822791347,

    "tolerancia": 1e-12,
}

# Control de entrada sobre el MARCO, por las DOS formas de la Tabla A.1. Las
# dos cartas son de cajon --regla vinculante #5: no se cruzan geometrias-- y
# la eleccion entre ellas la fija la columna «Equation Form», no el
# proyectista:
#
#     Carta 8  esc. 1  «30 to 75 degree wingwall flares»  Forma 1
#     Carta 9  esc. 1  «45 degree wingwall flare d = .043D»  Forma 2
#
# El punto es el mismo para las dos: marco 2.00 x 1.50 m, Q = 6.00 m3/s,
# S = 0.004 m/m. Con q* = 2.957 < 3.5 la rama es la NO SUMERGIDA en las dos, o
# sea la (A.1) pura frente a la (A.2) pura, que es donde la diferencia entre
# formas se ve entera y sin interpolar.
CP5R_CONTROL_ENTRADA_RECTANGULAR = {
    "B": 2.00,
    "H": 1.50,
    "Q": 6.00,
    "S": 0.004,
    "Ku": 1.811,

    "A_llena_esperada": 3.0,
    "q_estrella_esperado": 2.9573506161202237,   # Ku*Q/(A_llena*H^0.5)
    "zona": "no_sumergido",                      # q* <= 3.5
    "y_c_esperado": 0.9716827674320039,
    "H_c_esperado": 1.457524151148006,
    # UN ULP DE DISTANCIA DE `y_c_esperado`, Y NO ES UN DESCUIDO. Con H = 1.5
    # el algebra dice que H_c/H = 1.5*y_c/1.5 = y_c, pero en doble precision
    # `(y_c + V_c^2/(2g))/H` y `y_c` NO son el mismo float: dan
    # 0.971682767432004 y 0.9716827674320039. El dorado es el PRIMERO, que es
    # el que la memoria imprime y el que el paso sustituye; rehacerlo por la
    # identidad da el segundo. Se dice aqui porque un revisor que rehaga la
    # cuenta a mano llegara al segundo y tiene que saber por que difieren.
    "H_c_sobre_D_esperado": 0.971682767432004,

    # -- Carta 9 escala 1, FORMA 2: HW/D = K*(q*)^M, ec. (A.2). Sin H_c/D y
    #    sin Ks*S.
    "forma_2": {
        "carta": "cajon_concreto_aleta_45_d043",
        "K": 0.510, "M": 0.667, "Ks": -0.5, "forma": 2,
        "hw_sobre_D_esperado": 1.0511443364335622,
        "HW_esperado": 1.5767165046503433,
    },
    # -- Carta 8 escala 1, FORMA 1: HW/D = H_c/D + K*(q*)^M + Ks*S, ec. (A.1).
    #    Con M = 1.0 el termino K*(q*)^M es K*q* y se rehace de cabeza:
    #    0.026 * 2.9573506161202237 = 0.07689111601912581.
    "forma_1": {
        "carta": "cajon_concreto_aletas_30_75",
        "K": 0.026, "M": 1.0, "Ks": -0.5, "forma": 1,
        "termino_directo": 0.07689111601912581,
        "hw_sobre_D_esperado": 1.0465738834511298,
        "HW_esperado": 1.5698608251766948,
    },
    "tolerancia": 1e-12,
}

# Control de salida sobre el marco LLENO. Misma ecuacion que CP-8 y misma
# constante SI; lo que cambia es de donde sale la R, y ese es justamente el
# punto: aqui es B*H/(2(B+H)) y no D/4.
CP8R_CONTROL_SALIDA_RECTANGULAR = {
    "B": 2.00,
    "H": 1.50,
    "Q": 6.00,
    "S": 0.004,
    "L": 20.0,
    "n": 0.014,
    "ke": 0.5,
    "TW": 0.30,

    "R_lleno_esperado": 0.42857142857142855,
    "V_esperada": 2.0,                  # Q/A_llena = 6.0/3.0, exacta
    "K_friccion_SI_correcto": 19.63,
    "K_friccion_imperial_incorrecto": 29.0,
    "H_esperado_con_K_SI": 0.3543619441312314,
    "H_con_29_incorrecto": 0.37753708378651335,

    # h_o = max(TW, (y_c + D)/2) con D = H: manda la aproximacion geometrica.
    "h_o_esperado": 1.2358413837160018,
    "HW_salida_esperado": 1.510203327847233,   # H + h_o - S*L
    "tolerancia": 1e-12,
}


# LA TRANSICION NO MONOTONA, AHORA SOBRE LAS CARTAS QUE DE VERDAD SON DE
# CAJON. `CP5D_FORMA2_TRANSICION_NO_MONOTONA` fijo la propiedad con la Carta 9
# escala 1 evaluada sobre una seccion CIRCULAR, porque en C3 no habia otra.
# C4 la repite donde corresponde -- seccion rectangular y carta de cajon -- y
# ademas barre las DOCE cartas de cajon con Forma 2 de la Tabla A.1 para
# quedarse con la peor:
#
#     S* = (c*4^2 + Y - K*3.5^M) / |Ks|
#
#     cajon_concreto_aleta_18_337_d083     0.215192   <- la MINIMA de las doce
#     cajon_concreto_aleta_45_d043         0.236495
#     cajon_concreto_chaflan_esviaje_15    0.238747
#     ...
#     cajon_concreto_chaflan_aletas_184    0.493306   <- la maxima
#
# Las TRES cartas de cajon con Forma 1 (Cartas 8, escalas 1 a 3) no tienen
# umbral: con Forma 1 los dos extremos de la recta llevan Ks*S y el termino se
# cancela en la diferencia.
#
# QUE SIGNIFICA PARA ESTE PROYECTO, con el numero delante: la pendiente mas
# alta del expediente de prueba es 0.010 m/m (`tests/ejemplo_puntos.csv`) y la
# que C-01 declara para su conducto es 0.004. La minima de las doce, 0.215192,
# esta 21.5 veces por encima de la primera. NO MUERDE. Pero tampoco esta
# excluida por ninguna guardia: `dominios.S_CAUCE_MAX` vale 1.0, de modo que
# un CSV valido puede traer una pendiente por encima del umbral y el calculo
# la aceptaria sin decir nada -- el numero sigue siendo positivo --. Por eso
# se fija aqui en vez de darse por descartada.
CP5DR_TRANSICION_CAJON = {
    "carta": "cajon_concreto_aleta_18_337_d083",
    "K": 0.486, "M": 0.667, "c": 0.0249, "Y": 0.83, "Ks": -0.5, "forma": 2,
    "B": 2.00,
    "H": 1.50,
    "S_umbral": 0.21519208968426007,      # (c*16 + Y - K*3.5^M)/|Ks|
    "S_umbral_minimo_de_las_doce": 0.21519208968426007,
    "S_umbral_maximo_de_las_doce": 0.4933055559965851,
    # Quince desde T-2 (INF-3.2.2), que transcribio las tres filas de la
    # Carta 13 (bisel superior con aletas desplazadas). Eran doce, y las dos
    # claves de arriba conservan «de_las_doce» en el nombre: el minimo y el
    # maximo NO se movieron, porque los umbrales de las tres nuevas (0.2265,
    # 0.2853 y 0.3441) caen dentro del intervalo.
    "cartas_cajon_forma_2": 15,
    "cartas_cajon_forma_1": 3,

    "S_ensayada": 0.30,                   # por encima del umbral
    "HW_en_q_3_5_m": 1.681205932736805,   # ec. (A.2) pura, sin Ks*S
    "HW_en_q_4_0_m": 1.6176,              # ec. (A.3), con Ks*S
    "delta_mm": -63.60593273680482,       # NEGATIVO: baja al subir el caudal

    "S_baja": 0.05,                       # por debajo del umbral
    "delta_mm_con_S_baja": 123.89406726319518,   # POSITIVO: crece, lo esperable

    "S_maxima_del_expediente": 0.010,     # tests/ejemplo_puntos.csv
    "S_maxima_admitida_por_dominios": 1.0,   # dominios.S_CAUCE_MAX
    "tolerancia": 1e-12,
    "tolerancia_mm": 1e-6,      # la del delta, que va en milimetros
}


if __name__ == "__main__":
    # Recalculo independiente de verificacion. CP-1, CP-7 y CP-9 son formula
    # cerrada y no necesitan scipy: se autoverifican siempre. CP-2 resuelve una
    # raiz (brentq) y CP-8 se recalcula junto a el.

    # --- CP-1: TR = 1 / (1 - (1-R)^(1/n)) -----------------------------------
    # Esta autoverificacion no existia (MAT-O20) y por eso los dorados de
    # CP-1 pudieron estar mal durante toda su vida (MAT-D7 / SIS-F-03).
    for _caso in CP1_PERIODO_RETORNO:
        _TR = 1 / (1 - (1 - _caso["R"]) ** (1 / _caso["n"]))
        print(f"Recalculo CP-1: R={_caso['R']} n={_caso['n']} "
              f"TR={_TR:.11f} (fixture {_caso['TR_esperado']}, "
              f"redondea a {round(_TR)})")
        assert abs(_TR - _caso["TR_esperado"]) < _caso["tolerancia"], (
            f"CP-1 R={_caso['R']} n={_caso['n']}: el dorado "
            f"{_caso['TR_esperado']} no sale de la formula ({_TR!r})")
    print("CP-1 verificado contra los valores del fixture.")

    # --- CP-7: cadena sismica desagregada -----------------------------------
    _cp7 = CP7_CADENA_SISMICA
    _A_s = _cp7["F_pga"] * _cp7["PGA"]
    _k_h0 = _A_s                                    # k_h0 = A_s (2.8.1.1.14.2)
    assert abs(_A_s - _cp7["A_s_esperado"]) < 1e-12
    assert abs(_k_h0 - _cp7["k_h0_esperado"]) < 1e-12
    assert abs(_cp7["factor_muro_rigido"] * _k_h0
               - _cp7["k_h_con_muro_rigido_esperado"]) < 1e-12
    assert abs(_cp7["factor_muro_desplazable"] * _k_h0
               - _cp7["k_h_con_muro_desplazable_esperado"]) < 1e-12
    _A_s_E = _cp7["F_pga_clase_E"] * _cp7["PGA"]
    assert abs(_A_s_E - _cp7["A_s_con_F_pga_clase_E_esperado"]) < 1e-12
    assert abs(_cp7["factor_muro_rigido"] * _A_s_E
               - _cp7["k_h_con_F_pga_clase_E_esperado"]) < 1e-12
    print(f"CP-7 verificado: A_s={_A_s:.2f} k_h(rigido)="
          f"{_cp7['factor_muro_rigido'] * _k_h0:.2f} k_h(desplazable)="
          f"{_cp7['factor_muro_desplazable'] * _k_h0:.2f} "
          f"k_h(F_pga clase E)={_cp7['factor_muro_rigido'] * _A_s_E:.2f}")

    # --- CP-9: geometria de 7.B (formula cerrada) ---------------------------
    _cp9 = CP9_GEOMETRIA_7B
    _h = _cp9["cota_rasante"] - _cp9["cota_terreno"]
    _proy = 2 * _cp9["talud_de_prueba"] * _h
    _f30 = 1.0 / math.cos(math.radians(_cp9["esviaje_oblicuo_grados"]))
    _L0 = (_cp9["ancho_plataforma"] + _proy)
    _L30 = _L0 * _f30
    _caida = _cp9["S"] * _L30
    _salida = _cp9["cota_entrada_esperada"] - _caida
    _tl, _tc = _cp9["tolerancia_longitud"], _cp9["tolerancia_cota"]
    assert abs(_h - _cp9["altura_terraplen_esperada"]) < _tc
    assert abs(_proy - _cp9["proyeccion_esperada"]) < _tl
    assert abs(_f30 - _cp9["factor_esviaje_oblicuo_esperado"]) < 1e-8
    assert abs(_L0 - _cp9["longitud_perpendicular_esperada"]) < _tl
    assert abs(_L30 - _cp9["longitud_oblicua_esperada"]) < _tl
    assert abs(_L0 / _f30
               - _cp9["longitud_oblicua_si_multiplica_por_el_coseno"]) < _tl
    assert abs(_caida - _cp9["caida_oblicua_esperada"]) < _tc
    assert abs(_salida - _cp9["cota_salida_oblicua_esperada"]) < _tc
    print(f"CP-9 geometria 7.B verificado: proyeccion={_proy:.2f} L(0)={_L0:.2f} "
          f"L(30)={_L30:.6f} cota_salida={_salida:.7f}")


    # --- CP-9: Mononobe-Okabe con los cuatro angulos no nulos ---------------
    # Recomputacion independiente de la formula del docstring de
    # M9_cabezal.k_ae_mononobe_okabe, escrita aqui otra vez y sin importar el
    # modulo: si el dorado y el modulo comparten implementacion, el caso
    # patron no verifica nada (la leccion de CP-1 / MAT-D7).
    def _kae_cp9(phi_g, i_g, beta_g, delta_g, k_h, k_v, signo=1.0):
        p = math.radians(phi_g); ii = math.radians(i_g)
        b = math.radians(beta_g); d = math.radians(delta_g)
        ps = math.atan2(k_h, 1.0 - k_v)
        R = math.sqrt(math.sin(p + d) * math.sin(p - ps - ii)
                      / (math.cos(d + b + ps) * math.cos(ii - b)))
        return (math.cos(p - ps - b) ** 2
                / (math.cos(ps) * math.cos(b) ** 2 * math.cos(d + b + ps)
                   * (1.0 + signo * R) ** 2))

    for _c in CP9_MONONOBE_OKABE:
        _psi = math.degrees(math.atan2(_c["k_h"], 1.0 - _c["k_v"]))
        _kae = _kae_cp9(_c["phi_grados"], _c["i_grados"], _c["beta_grados"],
                        _c["delta_grados"], _c["k_h"], _c["k_v"])
        _ka = _kae_cp9(_c["phi_grados"], _c["i_grados"], _c["beta_grados"],
                       _c["delta_grados"], 0.0, 0.0)
        _err = _kae_cp9(_c["phi_grados"], _c["i_grados"], _c["beta_grados"],
                        _c["delta_grados"], _c["k_h"], _c["k_v"], signo=-1.0)
        for _clave, _obtenido in (("psi_esperado", _psi),
                                  ("K_AE_esperado", _kae),
                                  ("K_A_esperado", _ka),
                                  ("K_AE_errata_1_menos_R_esperado", _err)):
            assert abs(_obtenido - _c[_clave]) <= CP9_TOLERANCIA_RELATIVA * abs(_c[_clave]), (
                f"{_c['nombre']}: el dorado {_clave} = {_c[_clave]} no sale "
                f"de la formula ({_obtenido!r})")
        print(f"Recalculo {_c['nombre']}: psi={_psi:.6f} K_AE={_kae:.10f} "
              f"K_A={_ka:.10f} K_AE(errata 1-R)={_err:.6f}")

    # El caso limite de Rankine, y la prueba de que la errata [1 - R] devuelve
    # el RECIPROCO exacto de Ka -- no un valor parecido.
    for _phi, _ka_d, _err_d in zip(CP9_RANKINE_LIMITE["phi_casos"],
                                   CP9_RANKINE_LIMITE["Ka_rankine_esperado"],
                                   CP9_RANKINE_LIMITE["K_AE_errata_1_menos_R_esperado"]):
        _ka_r = math.tan(math.radians(45.0 - _phi / 2.0)) ** 2
        _kae_r = _kae_cp9(_phi, 0.0, 0.0, 0.0, 0.0, 0.0)
        _err_r = _kae_cp9(_phi, 0.0, 0.0, 0.0, 0.0, 0.0, signo=-1.0)
        assert abs(_ka_r - _ka_d) <= 1e-12 * _ka_d
        assert abs(_kae_r - _ka_r) <= 1e-12 * _ka_r      # [1+R] SI reproduce Ka
        assert abs(_err_r - _err_d) <= 1e-12 * _err_d
        assert abs(_err_r * _ka_r - 1.0) < 1e-12          # la errata es 1/Ka
    print("CP-9 Mononobe-Okabe verificado: los tres casos de angulos no nulos y el caso "
          "limite de Rankine (donde [1-R] da exactamente 1/Ka).")

    # --- CP-9: empuje del trasdos (formula cerrada, sin scipy) --------------
    # Recalculo independiente: esta funcion NO importa M9_cabezal, se escribe
    # aqui a partir de la formula de Mononobe-Okabe. Si algun dia el modulo y
    # este bloque discrepan, uno de los dos esta mal y hay que mirarlos.
    _cp9 = CP9_EMPUJE_TRASDOS
    _tol9 = _cp9["tolerancia_relativa"]

    def _cerca(obtenido, dorado, quien):
        assert abs(obtenido - dorado) <= _tol9 * abs(dorado), (
            f"CP-9 {quien}: el dorado {dorado} no sale de la formula "
            f"({obtenido!r})")

    def _k_ae_independiente(phi_g, i_g, beta_g, delta_g, k_h, k_v):
        psi = math.atan2(k_h, 1 - k_v)
        phi, i, beta, delta = (math.radians(a)
                               for a in (phi_g, i_g, beta_g, delta_g))
        cos_dbp = math.cos(delta + beta + psi)
        cos_ib = math.cos(i - beta)
        radicando = (math.sin(phi + delta) * math.sin(phi - psi - i)
                     / (cos_dbp * cos_ib))
        R_mo = math.sqrt(max(radicando, 0.0))
        K = (math.cos(phi - psi - beta) ** 2
             / (math.cos(psi) * math.cos(beta) ** 2 * cos_dbp * (1 + R_mo) ** 2))
        return K, math.degrees(psi)

    # Bloque A: la formula cerrada del empuje, con K_AE dado
    _P_AE_A = (_cp9["A_gamma_relleno"] * _cp9["A_H"] ** 2
               * (1 - _cp9["A_k_v"]) * _cp9["A_K_AE"] / 2)
    _cerca(_P_AE_A, _cp9["A_P_AE_esperado"], "A_P_AE_esperado")
    # y los cuatro mutantes, para que su distancia quede verificada y no dicha
    _g, _H, _K, _kv = (_cp9["A_gamma_relleno"], _cp9["A_H"],
                       _cp9["A_K_AE"], _cp9["A_k_v"])
    _cerca(_g * _H**2 * (1 + _kv) * _K / 2,
           _cp9["A_mutante_1_mas_kv"], "A_mutante_1_mas_kv")
    _cerca(_g * _H**2 * (1 - _kv) * _K * 2,
           _cp9["A_mutante_por_dos"], "A_mutante_por_dos")
    _cerca(_g * _H**2 / (1 - _kv) * _K / 2,
           _cp9["A_mutante_divide_kv"], "A_mutante_divide_kv")
    _cerca(_g * _H**2 * (1 - _kv) / _K / 2,
           _cp9["A_mutante_divide_KAE"], "A_mutante_divide_KAE")
    assert min(_cp9["A_mutante_1_mas_kv"], _cp9["A_mutante_por_dos"],
               _cp9["A_mutante_divide_kv"], _cp9["A_mutante_divide_KAE"]) \
        > 1.3 * _cp9["A_P_AE_esperado"], \
        "CP-9: algun mutante quedo a menos del 30 % del dorado"

    # Bloque B: la cadena coherente
    _K_AE_B, _psi_B = _k_ae_independiente(
        _cp9["B_phi_grados"], _cp9["B_i_grados"], _cp9["B_beta_grados"],
        _cp9["B_delta_grados"], _cp9["B_k_h"], _cp9["B_k_v"])
    _K_A_B, _ = _k_ae_independiente(
        _cp9["B_phi_grados"], _cp9["B_i_grados"], _cp9["B_beta_grados"],
        _cp9["B_delta_grados"], 0.0, 0.0)
    _P_AE_B = (_cp9["B_gamma_relleno"] * _cp9["B_H"] ** 2
               * (1 - _cp9["B_k_v"]) * _K_AE_B / 2)
    _P_A_B = _cp9["B_gamma_relleno"] * _cp9["B_H"] ** 2 * _K_A_B / 2
    _cerca(_psi_B, _cp9["B_psi_grados_esperado"], "B_psi_grados_esperado")
    _cerca(_K_AE_B, _cp9["B_K_AE_esperado"], "B_K_AE_esperado")
    _cerca(_K_A_B, _cp9["B_K_A_esperado"], "B_K_A_esperado")
    _cerca(_K_AE_B - _K_A_B, _cp9["B_incremento_K_esperado"],
           "B_incremento_K_esperado")
    _cerca(_P_AE_B, _cp9["B_P_AE_esperado"], "B_P_AE_esperado")
    _cerca(_P_A_B, _cp9["B_P_A_esperado"], "B_P_A_esperado")
    _cerca(_P_AE_B - _P_A_B, _cp9["B_incremento_P_esperado"],
           "B_incremento_P_esperado")
    _cerca(_cp9["B_brazo_fraccion"] * _cp9["B_H"],
           _cp9["B_z_incremento_esperado"], "B_z_incremento_esperado")
    # Con i = beta = delta = 0 el K_A de Coulomb TIENE que ser el de Rankine
    _cerca(_K_A_B, math.tan(math.radians(45 - _cp9["B_phi_grados"] / 2)) ** 2,
           "B_K_A_esperado (contra Rankine)")

    # Bloque C: Coulomb con angulos no nulos, recalculado con la ESCRITURA
    # DEL MANUAL DE PUENTES (num. 2.4.4.1.5.3, ecs. -1 y -2), no con la de
    # Mononobe-Okabe: theta es el angulo de la cara posterior del muro con
    # la horizontal (theta = 90 - beta_M9) y beta_MP el del relleno (= i).
    def _ka_coulomb_manual(phi_g, i_g, beta_g, delta_g):
        theta = math.radians(90.0 - beta_g)
        phi, beta_mp, delta = (math.radians(a) for a in (phi_g, i_g, delta_g))
        r = (1 + math.sqrt(math.sin(phi + delta) * math.sin(phi - beta_mp)
                           / (math.sin(theta - delta)
                              * math.sin(theta + beta_mp)))) ** 2
        return (math.sin(theta + phi) ** 2
                / (r * math.sin(theta) ** 2 * math.sin(theta - delta)))

    _K_A_C = _ka_coulomb_manual(_cp9["C_phi_grados"], _cp9["C_i_grados"],
                                _cp9["C_beta_grados"], _cp9["C_delta_grados"])
    _cerca(_K_A_C, _cp9["C_K_A_coulomb_esperado"], "C_K_A_coulomb_esperado")
    # y la misma cifra por la formulacion de M-O con k = 0: las dos escrituras
    # son la misma formula (identidad exacta, no coincidencia numerica)
    _K_A_C_mo, _ = _k_ae_independiente(
        _cp9["C_phi_grados"], _cp9["C_i_grados"], _cp9["C_beta_grados"],
        _cp9["C_delta_grados"], 0.0, 0.0)
    assert abs(_K_A_C_mo - _K_A_C) <= 1e-15, "Coulomb (MP) != Mononobe-Okabe(k=0)"
    _K_A_rank_C = math.tan(math.radians(45 - _cp9["C_phi_grados"] / 2)) ** 2
    _cerca(_K_A_rank_C, _cp9["C_K_A_rankine_esperado"], "C_K_A_rankine_esperado")
    _cerca((_K_A_C - _K_A_rank_C) / _K_A_rank_C,
           _cp9["C_diferencia_relativa_coulomb_rankine"],
           "C_diferencia_relativa_coulomb_rankine")
    assert _K_A_C > _K_A_rank_C, "con i, beta, delta > 0 Coulomb tiene que superar a Rankine aqui"
    _K_AE_C, _psi_C = _k_ae_independiente(
        _cp9["C_phi_grados"], _cp9["C_i_grados"], _cp9["C_beta_grados"],
        _cp9["C_delta_grados"], _cp9["C_k_h"], _cp9["C_k_v"])
    _cerca(_psi_C, _cp9["C_psi_grados_esperado"], "C_psi_grados_esperado")
    _cerca(_K_AE_C, _cp9["C_K_AE_esperado"], "C_K_AE_esperado")
    _P_A_C = _cp9["C_gamma_relleno"] * _cp9["C_H"] ** 2 * _K_A_C / 2
    _P_AE_C = (_cp9["C_gamma_relleno"] * _cp9["C_H"] ** 2
               * (1 - _cp9["C_k_v"]) * _K_AE_C / 2)
    _cerca(_P_A_C, _cp9["C_P_A_esperado"], "C_P_A_esperado")
    _cerca(_P_AE_C, _cp9["C_P_AE_esperado"], "C_P_AE_esperado")
    _cerca(_P_AE_C - _P_A_C, _cp9["C_incremento_P_esperado"],
           "C_incremento_P_esperado")
    print(f"CP-9 bloque C verificado: Ka(Coulomb)={_K_A_C:.9f} "
          f"Ka(Rankine)={_K_A_rank_C:.9f} K_AE={_K_AE_C:.9f} P_A={_P_A_C:.6f}")
    print(f"CP-9 empujes verificado: P_AE(A)={_P_AE_A:.6f}  K_AE(B)={_K_AE_B:.6f}  "
          f"P_AE(B)={_P_AE_B:.6f}  dP_AE(B)={_P_AE_B - _P_A_B:.6f}")
    # --- CP-2 y CP-8 --------------------------------------------------------
    try:
        import numpy as np
        from scipy.optimize import brentq

        D, yD, n, S = 0.90, 0.75, 0.013, 0.005
        y_target = yD * D
        f = lambda th: (D / 2) * (1 - math.cos(th / 2)) - y_target
        theta = brentq(f, 1e-6, 2 * math.pi - 1e-6)
        A = (D**2 / 8) * (theta - math.sin(theta))
        P = D * theta / 2
        R = A / P
        V_max = (1 / n) * R ** (2 / 3) * S ** 0.5
        Q = V_max * A
        print(f"Recalculo CP-2: theta={theta:.5f} A={A:.5f} P={P:.5f} "
              f"R={R:.5f} V(n=0.013)={V_max:.4f} Q={Q:.4f}")
        assert abs(theta - CP2_GEOMETRIA_MANNING["theta_esperado"]) < 1e-4
        assert abs(V_max - CP2_GEOMETRIA_MANNING["V_con_n_max_esperado"]) < 1e-3
        assert abs(Q - CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"]) < 1e-3
        print("CP-2 verificado contra los valores del fixture.")

        # CP-8: verificacion cruzada de la constante SI vs imperial
        n8 = CP8_CONTROL_SALIDA["n"]
        L8 = CP8_CONTROL_SALIDA["L"]
        R8 = CP8_CONTROL_SALIDA["R"]
        ke8 = CP8_CONTROL_SALIDA["ke"]
        V8 = CP8_CONTROL_SALIDA["V"]
        H_si = (1 + ke8 + 19.63 * n8**2 * L8 / R8**(4/3)) * V8**2 / (2*G)
        H_imp = (1 + ke8 + 29.0 * n8**2 * L8 / R8**(4/3)) * V8**2 / (2*G)
        assert abs(H_si - CP8_CONTROL_SALIDA["H_esperado_con_K_SI"]) < 1e-3
        assert abs(H_imp - CP8_CONTROL_SALIDA["H_con_29_incorrecto"]) < 1e-3
        print(f"CP-8 verificado: H(19.63)={H_si:.5f}  H(29, incorrecto)={H_imp:.5f}")
    except ImportError:
        print("numpy/scipy no disponibles en este entorno; "
              "omite la autoverificacion.")

    # --- CP-9: ensamble de empujes del trasdos con agua ---------------------
    _c = CP9_ENSAMBLE_TRASDOS
    _Ka = math.tan(math.radians(45 - _c["phi_grados"] / 2)) ** 2
    _He, _g, _gw = _c["altura_empuje"], _c["gamma_relleno"], _c["gamma_agua"]
    _h = _c["D_f"] - _c["NF_profundidad_m"]
    _esperados = {
        "h_agua_esperada": _h,
        "Ka_esperado": _Ka,
        "E_activo_esperado": 0.5 * _g * _Ka * _He ** 2,
        "E_sobrecarga_esperado": _g * _Ka * _c["h_eq"] * _He,
        "E_hidrostatico_esperado": 0.5 * _gw * _h ** 2,
        "U_subpresion_esperado": _gw * _h * _c["B"],
    }
    for _clave, _valor in _esperados.items():
        assert abs(_valor - _c[_clave]) < CP9_TOLERANCIA_RELATIVA * max(1.0, abs(_valor)), (
            f"CP-9 ensamble: el dorado {_clave} = {_c[_clave]!r} no sale de la "
            f"formula ({_valor!r})")
    print(f"CP-9 ensamble verificado: h_agua={_h:.2f} "
          f"E_a={_esperados['E_activo_esperado']:.6f} "
          f"E_s={_esperados['E_sobrecarga_esperado']:.6f} "
          f"E_w={_esperados['E_hidrostatico_esperado']:.6f} "
          f"U={_esperados['U_subpresion_esperado']:.6f}")



# ===========================================================================
# CP10 - Flotacion de un MARCO frente a un cilindro (V7, C7)
# ===========================================================================
#
# EL CASO QUE MATA LA REGRESION QUE C5 DEJO ABIERTA. Hasta C7,
# `M8.empuje_flotacion_kn_m` recibia un `D_exterior` escalar y calculaba
# `pi/4 * D^2`: un CILINDRO cableado. Un marco al que se le pasara su altura
# exterior se evaluaba como el cilindro circunscrito a esa altura, y la
# subpresion salia MUY por debajo de la real -- que es la direccion insegura,
# porque U es la carga DESestabilizante de V7 --.
#
# Los dos numeros los midio la auditoria adversarial de C5 y este caso los
# fija: prisma 40.6 kN/m contra cilindro 25.0 kN/m sobre la misma altura.
#
# COMO SE LEE LA DIFERENCIA, que se puede enunciar de dos formas y conviene
# no confundirlas: el prisma es un 63 % MAYOR que el cilindro (40.61/24.96 =
# 1.627), o el cilindro un 39 % MENOR que el prisma (1 - 24.96/40.61). Las
# dos son la misma medicion sobre bases distintas; el docstring de
# `M2.espesor_pared` usa la primera.
#
# Y EL PESO DE RELLENO NO CAE IGUAL, que es lo que hace que el error no se
# cancele: EV usa el ANCHO exterior, que en el marco es 2.30 m y en el
# cilindro 1.80 m -- un 28 % menos, no un 39 % --. La subpresion cae mas que
# lo que la sujeta, y por eso V7 SOBREESTIMA la seguridad del marco alrededor
# de un 27 % cuando se lo evalua como cilindro.
_CP10_B = 2.00          # m - ancho interior de la celda
_CP10_H = 1.50          # m - altura interior
_CP10_T = 0.15          # m - espesor de pared adoptado
_CP10_H_RELLENO = 0.95  # m - relleno sobre la clave
_CP10_GAMMA_R = 18.0    # kN/m3 - peso especifico del relleno

CP10_FLOTACION_MARCO = {
    "descripcion": ("V7 sobre un marco de 2.00 x 1.50 m con t = 0.15 m: la "
                    "subpresion es la de un PRISMA, no la del cilindro "
                    "circunscrito a su altura"),
    "B": _CP10_B,
    "H": _CP10_H,
    "espesor": _CP10_T,
    "altura_relleno": _CP10_H_RELLENO,
    "gamma_relleno": _CP10_GAMMA_R,
    # Geometria exterior, con la nomenclatura del Art. 12.6.6.3 de AASHTO.
    "Bc_esperado": _CP10_B + 2 * _CP10_T,           # 2.30 m - ancho exterior
    "Bc_prima_esperado": _CP10_H + 2 * _CP10_T,     # 1.80 m - canto exterior
    "area_exterior_esperada": (_CP10_B + 2 * _CP10_T) * (_CP10_H + 2 * _CP10_T),
    # U = gamma_agua * area_exterior, con gamma_agua = 9.81 kN/m3.
    "U_prisma_esperado": 9.81 * (_CP10_B + 2 * _CP10_T) * (_CP10_H + 2 * _CP10_T),
    # Y el que saldria si se lo evaluara como cilindro de su misma altura
    # exterior: es el numero EQUIVOCADO, y esta aqui para que el test pueda
    # comprobar que NO es el que sale.
    "U_cilindro_equivocado": 9.81 * 3.141592653589793
    * (_CP10_H + 2 * _CP10_T) ** 2 / 4,
    # EV = gamma_relleno * ancho_exterior * altura_relleno.
    "EV_esperado": _CP10_GAMMA_R * (_CP10_B + 2 * _CP10_T) * _CP10_H_RELLENO,
}


# ===========================================================================
# CP11 - Series de diametros nominales de las normas de producto (M2, N2)
# ===========================================================================
#
# EL DORADO SALE DE LA TABLA, NO DE LA FORMULA (conflicto #7 del plan). M2
# recorre una progresion [C] -- 0.90 m + 0.15 m, 'diametros_normalizados' --
# que la hoja de ruta defiende diciendo que «reproduce las series» de las
# normas de producto. Hasta N2 nadie lo contrastaba: SIS-F-13 tenia a M2
# exento de caso patron porque las series no estaban transcritas, y
# fabricarle un dorado con la misma formula habria sido inventar el valor de
# referencia. Las series de abajo son las TRANSCRITAS en
# src/normativa/tablas.py y verificadas contra los PDF de normas/, copiadas
# aqui como literales a proposito -- un dorado es una copia INDEPENDIENTE --,
# y test_M2 cruza las tres cosas: la columna de la tabla del registro, este
# dorado y lo que M2 recorre.
#
# HDPE: AASHTO M 294-11, num. 7.2.1 (cita AASHTO_M294_TRAD.7.2.1, cuyo texto
#   T2 comprueba contra el PDF) y tabla de 7.2.2 (AASHTO_M294_TRAD.T7.2.2).
#   ES UNA TRADUCCION NO OFICIAL, sin firma -- el ejemplar no imprime folio y
#   el original en ingles sigue ausente --: este dorado acredita lo que la
#   traduccion imprime. La serie TERMINA en 1500 mm, sin «y superiores»: por
#   eso el tope de catalogo del HDPE coincide con su ultima fila.
# TMC: ASTM A760/A760M-10 Tabla 1 (ASTM_A760.T1, tambien una traduccion,
#   leida por imagen en I1) y AASHTO M 36 Table 6 (AASHTO_M36.T6), cruzadas
#   por CORR-TAMANOS-TMC. La serie sigue hasta 3600 mm y el tope de catalogo
#   (2.10 m) la corta: el 2100 es una fila mas.
# CONCRETO: SIN DORADO, y se dice aqui para que el caso no se lea como
#   completo. AASHTO M 170M-04 Tablas 1 a 5 no estan transcritas -- escaneo
#   con OCR inutilizable: se transcriben por imagen, tabla a tabla, en una
#   sesion propia --. La entrada es None a proposito y test_M2 lo comprueba.
#
# LO QUE EL CASO NO DECIDE: ni el piso (0.90 m, [N] del Manual, num.
# 4.1.1.3.4 a) ni los topes ([A] 'D_max_catalogo'). Los lee el test de sus
# simbolos; el caso solo fija que filas tiene cada serie.
CP11_SERIES_NOMINALES = {
    "descripcion": ("M2.siguiente_diametro recorre, para cada material, "
                    "EXACTAMENTE las filas de la serie de tamaños nominales "
                    "de su norma de producto que caen entre el piso peruano "
                    "y el tope de catalogo -- ni una fila de mas, ni una de "
                    "menos, ni un diametro que la serie no tabule"),
    "hdpe": {
        "tabla": "AASHTO_M294_TRAD.T7.2.2",
        "columna": "dn_mm",
        "cita_serie": "AASHTO_M294_TRAD.7.2.1",
        "fuente_derivada": ("AASHTO M 294-11, TRADUCCION NO OFICIAL al "
                            "español, sin firma (sin folio; el original en "
                            "ingles sigue en FUENTES_AUSENTES)"),
        # Leidos del num. 7.2.1 (PDF 5): doce diametros, paso 75 mm hasta
        # 750 y 150 mm de 900 a 1500.
        "serie_mm": (300, 375, 450, 525, 600, 675, 750,
                     900, 1050, 1200, 1350, 1500),
        "techo_de_la_serie_mm": 1500,        # ultima fila: no hay «y superiores»
    },
    "tmc": {
        "tabla": "ASTM_A760.T1",
        "columna": "dn_mm",
        "tabla_gemela": "AASHTO_M36.T6",
        "fuente_derivada": ("ASTM A760/A760M-10, traduccion al español "
                            "(declarada en la Fuente), leida por imagen"),
        # Leidos de la Tabla 1 (PDF 3): 31 diametros, paso 150 mm desde 900.
        "serie_mm": (100, 150, 200, 250, 300, 375, 450, 500, 600, 675, 750,
                     825, 900, 1050, 1200, 1350, 1500, 1650, 1800, 1950,
                     2100, 2250, 2400, 2550, 2700, 2850, 3000, 3150, 3300,
                     3450, 3600),
        "techo_de_la_serie_mm": 3600,
    },
    "concreto_reforzado": {
        "tabla": "AASHTO_M170M.T5",
        "columna": "dn_mm",
        "fuente_derivada": ("AASHTO M 170M-04, Tabla 5 (Clase V), leida por "
                            "imagen de la pag. PDF 10 --el unico escaneo "
                            "real del ejemplar; las Tablas 1 a 4 son "
                            "recomposiciones OCR con digitos equivocados-- "
                            "(cierre C09, SIS-F-13)"),
        # Leidos de la Tabla 5 (PDF 10, rotada): 27 diametros, paso 75 mm
        # hasta 900 y 150 mm de 900 a 3600. La serie designada es la misma
        # en las cinco clases; ver la interpretacion de la tabla.
        "serie_mm": (300, 375, 450, 525, 600, 675, 750, 825, 900, 1050,
                     1200, 1350, 1500, 1650, 1800, 1950, 2100, 2250, 2400,
                     2550, 2700, 2850, 3000, 3150, 3300, 3450, 3600),
        "techo_de_la_serie_mm": 3600,
    },
    # Desde el cierre de C09 los tres materiales tienen dorado de TABLA. El
    # censo de lo que sigue sin caso patron es el de test_guardias_de_la_suite
    # (M10, expediente vial).
    "sin_dorado": {},
}


# ---------------------------------------------------------------------------
# CP-12 · REGIMEN DEL BARRIL LLENO (EXT-3) -- el unico dorado cerrado del cluster
# ---------------------------------------------------------------------------
# CALCULADO A MANO, y es aritmetica de la fuente y no un dorado inventado: con
# el TW por encima de la clave (TW >= D) el barril fluye lleno (v8 §1.3
# enmendada en EXT-0; HDS-5 3.1.6, pag. impresa 3.18: «Total barrel area is
# used when the tailwater exceeds the top of the barrel»), el tirante del
# regimen es D entero -- y/D = 1, sin borde libre: MC-HHD pag. 79, «las
# alcantarillas no deben ser diseñadas para trabajar a seccion llena» -- y la
# velocidad es Q entre el area llena:
#
#     A_llena = pi * D^2 / 4 = pi * 0.81 / 4 = 0.6361725124 m2
#     V_llena = Q / A_llena  = 0.05 / 0.6361725124 = 0.07859503363 m/s  < 0.25
#
# Es el caso (a) del dictamen del 2026-09-19 (EXT-M-01): hasta EXT-3 la memoria
# imprimia «manda TW: la salida esta ahogada» y en la misma pagina V1 [OK] con
# y/D = 0.135 y V2 evaluada con la velocidad uniforme de Manning (0.974 m/s).
# El resto del caso (HW, control gobernante) NO lleva dorado: sale de Brent y
# de las ecuaciones del HDS-5, y fabricarle una cifra seria el conflicto #7.
CP12_REGIMEN_LLENO = {
    "D": 0.90,
    "Q": 0.05,
    "S": 0.005,
    "L": 20.0,
    "TW": 1.2,                        # >= D: salida sumergida, barril lleno
    "material": "concreto_reforzado",
    "A_llena_esperada": 0.6361725124, # m2, pi*D^2/4
    "V_llena_esperada": 0.07859503363, # m/s, Q/A_llena -- por debajo de V_MIN
    "y_sobre_D_esperado": 1,          # el tirante del regimen es D entero
    "tolerancia": 1e-9,               # los dorados llevan 9 decimales
}


# ---------------------------------------------------------------------------
# --- T-2 --- CP-HDS5-DG1 · EJEMPLOS PUBLICADOS DEL HDS-5 (validacion externa)
# ---------------------------------------------------------------------------
# EL PRIMER DORADO DEL REPOSITORIO QUE NO SALE DE UNA FORMULA RECOMPUTADA SINO
# DE UNA CORRIDA EXTERNA CITABLE (conflicto #7 de la matriz de auditorias;
# INF-3.2.2). Son los dos ejemplos de diseño que el Cap. III del HDS-5 remite a
# su «Design Guideline 1» (num. 3.3.6 «Example Problems», pag. impresa 3.26,
# PDF 108), con control de ENTRADA y de SALIDA calculados los dos:
#
#   DG 1.3  «Circular culvert»   enunciado y resultados: pags. impresas DG1.1
#           a DG1.3 (PDF 272-274); FORMULARIO con los intermedios («DG 1.3.3
#           Culvert Design Form», Example Problem No. 1): pag. impresa DG1.4,
#           PDF 275.
#   DG 1.4  «Box culvert»        enunciado y resultados: pags. impresas DG1.8
#           y DG1.9 (PDF 279-280); FORMULARIO («DG 1.4.3 Culvert Design
#           Form», Example Problem No. 2): pag. impresa DG1.10, PDF 281.
#
# Los dos formularios son IMAGEN, sin capa de texto: se leyeron sobre la
# pagina renderizada (T-2, 2026-11-11). Los enunciados si tienen texto.
#
# UNIDADES. La fuente resuelve los dos en unidades inglesas («The complete
# customary unit (CU) solution is detailed below») y da de la solucion SI solo
# un resumen, con la advertencia de que «direct conversion of the CU solution
# to SI may yield slightly different results» (pag. impresa DG1.2). El codigo
# opera en SI. LA CONVERSION SE HACE AQUI, en el fixture, y solo en un
# sentido: los DATOS se convierten de pies a metros con el factor exacto
# (1 ft = 0.3048 m; 1 ft3/s = 0.3048^3 m3/s), el motor corre en SI, y los
# RESULTADOS del motor se llevan a pies para compararlos con la cifra impresa.
# Los diametros nominales en pulgadas se convierten igual (54 in = 1.3716 m):
# NO se usan los «1500 mm» de la solucion SI, que es otro tubo.
#
# QUE FILA DE LA TABLA A.1 CORRESPONDE A CADA RENGLON DEL FORMULARIO, que es
# una lectura y se declara:
#   «Conc. Circ. - groove end»     Carta 1, escala 2, «Groove end w/headwall».
#        El formulario no dice si la campana va en cabezal o saliente. Se
#        toma la de cabezal porque el enunciado diseña en cabezal («in
#        headwall», pag. DG1.2) y porque es la que reproduce la lectura: con
#        la escala 3 («Groove end projecting») el 54 in da HW/D = 1.799, +1.6
#        % sobre el 1.77 publicado; con la escala 2, 1.761 (-0.5 %).
#   «C.M.P. - bevel 45° in headwall»  Carta 3, escala A, «Beveled ring, 45°
#        bevels».
#   «Box - Sq. edge» (90° headwall)   Carta 8, escala 2, «90° and 15° wingwall
#        flares»: el cabezal a 90° con borde a escuadra (el enunciado nombra
#        las cartas 8B, 10B, 14B y 15B).
#   «Box - 45° bevel»                 Carta 10, escala 2, «90° headwall w/45°
#        bevels».
#
# LA TOLERANCIA, DECLARADA ANTES DE COMPARAR Y CON SU RAZON. Las cifras
# publicadas son LECTURAS DE NOMOGRAMA redondeadas (HW/D a dos decimales, las
# alturas a 0.1 ft); el motor resuelve las ecuaciones de las que el nomograma
# sale. Dos tolerancias, y las dos se aplican:
#
#   tolerancia_de_la_fuente = 10 %   la que el propio HDS-5 declara para su
#        procedimiento: «it should be assumed that the results of the
#        procedure are accurate to within plus or minus ten percent, in terms
#        of headwater elevation» (num. 3.1.1, pag. impresa 3.1, PDF 83).
#   tolerancia_de_lectura   =  3 %   la del proyecto, mas estrecha: lo que
#        cabe esperar entre una ecuacion y la lectura de su propio nomograma
#        (dos decimales de HW/D sobre un valor del orden de 1.5 son ~1.3 %;
#        0.1 ft sobre 4 ft son 2.5 %).
#
# Toda magnitud comparada tiene que caer dentro del 3 %, SALVO las que el
# censo `fuera_de_tolerancia` nombra una a una con su causa. El censo se
# comprueba en las dos direcciones --lo que nombra tiene que estar de verdad
# fuera del 3 %-- para que no pueda esconder una magnitud que cumple, y NO se
# ajusta la tolerancia para vaciarlo: la causa de cada una esta en la ficha
# T2-05 de docs/decisiones_diferidas.md.
PIE_EN_METROS = 0.3048              # definicion exacta del pie internacional
PULGADA_EN_METROS = 0.0254          # definicion exacta de la pulgada

CP_HDS5_DG1 = {
    "fuente": "HDS-5 3a ed. (FHWA-HIF-12-026, abril 2012), Design Guideline 1 "
              "«Culvert Design Using Nomographs»: DG 1.3 (circular) y DG 1.4 "
              "(cajon); formularios en las pags. impresas DG1.4 (PDF 275) y "
              "DG1.10 (PDF 281)",
    "tolerancia_de_lectura": 0.03,
    "tolerancia_de_la_fuente": 0.10,
    "pagina_pdf_tolerancia_de_la_fuente": 83,
    "frase_tolerancia_de_la_fuente": (
        "accurate to within plus or minus ten percent, in terms of headwater "
        "elevation"),
    # --- DG 1.3: Q25 = 200 ft3/s, TW = 3.5 ft, So = 0.01, La = 200 ft,
    #     ELi = 100.0 ft, ELo = 98.0 ft (pag. impresa DG1.2 y formulario).
    "circular": {
        "pagina_pdf_enunciado": 273, "pagina_pdf_formulario": 275,
        "Q_ft3_s": 200.0, "TW_ft": 3.5, "S": 0.01, "L_ft": 200.0,
        "EL_i_ft": 100.0, "EL_o_ft": 98.0,
        "filas": (
            {"id": "rcp_54_groove",        # el diseño ADOPTADO por el ejemplo
             "D_in": 54.0, "carta": "circular_concreto_groove_end_headwall",
             "n": 0.012, "ke": 0.2,        # n impreso en el formulario
             "publicado": {"HW_sobre_D": 1.77, "HW_entrada_ft": 7.97,
                           "d_c_ft": 4.1, "h_o_ft": 4.3, "H_ft": 4.7,
                           "EL_ho_ft": 107.0, "V_salida_ft_s": 15.3,
                           "control": "entrada"}},
            {"id": "rcp_60_groove",
             "D_in": 60.0, "carta": "circular_concreto_groove_end_headwall",
             "n": 0.012, "ke": 0.2,
             "publicado": {"HW_sobre_D": 1.36, "HW_entrada_ft": 6.80,
                           "d_c_ft": 4.1, "h_o_ft": 4.6, "H_ft": 2.9,
                           "EL_ho_ft": 105.5, "V_salida_ft_s": 15.6,
                           "control": "entrada"}},
            # LOS DOS DE METAL CORRUGADO. El formulario imprime el n del tubo
            # ADOPTADO (concreto, 0.012) y no el del CMP. Lo que NO depende de
            # n se compara como en las demas filas (`publicado`: el control
            # de entrada, d_c y h_o). Lo que SI depende --H, la cota de
            # control de salida, cual control gobierna y la velocidad de la
            # fila de 72 in, que es la normal-- se compara con el n ACOTADO
            # por la propia fuente (`n_interpretado`, abajo): no se le pide al
            # motor una cifra, se le pide que la cifra publicada caiga DENTRO
            # del intervalo que da el rango de la Tabla B.1.
            {"id": "cmp_72_bisel_45",
             "D_in": 72.0, "carta": "circular_anillo_biselado_45",
             "n": None, "ke": 0.2,
             "publicado": {"HW_sobre_D": 0.96, "HW_entrada_ft": 5.76,
                           "d_c_ft": 3.8, "h_o_ft": 4.9},
             "publicado_con_n_interpretado": {
                 "H_ft": 2.6, "EL_ho_ft": 105.5, "V_salida_ft_s": 9.0,
                 "control": "entrada"}},
            # LA UNICA FILA DE LOS DOS FORMULARIOS QUE GOBIERNA LA SALIDA
            # (EL_ho 108.9 > EL_hi 107.0), y por eso se descarta («try
            # smoother pipe», pag. impresa DG1.3). Su velocidad de salida no
            # depende de n: es Q/A al tirante critico (TW < d_c).
            {"id": "cmp_60_bisel_45",
             "D_in": 60.0, "carta": "circular_anillo_biselado_45",
             "n": None, "ke": 0.2,
             "publicado": {"HW_sobre_D": 1.40, "HW_entrada_ft": 7.10,
                           "d_c_ft": 4.1, "h_o_ft": 4.6},
             "publicado_con_n_interpretado": {
                 "H_ft": 6.3, "EL_ho_ft": 108.9, "V_salida_ft_s": 11.9,
                 "control": "salida"}},
        ),
        # EL n DEL METAL CORRUGADO ES UNA INTERPRETACION, y se declara. El
        # enunciado dice «CMP with 2-2/3 by 1/2 in corrugations» (pag. impresa
        # DG1.2, PDF 273) y no da n. La fuente lo acota en dos sitios:
        #   * `rango`: Tabla B.1 «Manning's n Values for Culverts», pag.
        #     impresa B.6 (PDF 208), fila «Corrugated Metal Pipe, Pipe-Arch
        #     and Box (Annular Corrugations), 2-2/3 by 1/2 in»: 0.022-0.027.
        #     (La fila helicoidal de la misma corrugacion da 0.011-0.023 y
        #     remite a la Figura B.3; el enunciado no dice cual es, y el
        #     nomograma de salida del CMP esta trazado con el n anular.)
        #   * `tipico`: «Typical Manning's n values used for designing
        #     culverts are n = 0.012 for smooth walled culverts and n = 0.024
        #     for rough culverts (corrugated)», pag. impresa 3.8 (PDF 90); es
        #     el n del nomograma de control de salida del CMP, «Head for
        #     Standard C.M. Pipe Culverts Flowing Full, n = 0.024» (indice de
        #     cartas, PDF 211).
        # Medido: con el tipico el motor da H = 2.45 y 5.96 ft contra 2.6 y
        # 6.3 publicados (-5.6 % y -5.5 %, dentro del 10 % de la fuente y
        # fuera del 3 % de lectura); los dos publicados caen dentro del
        # intervalo del rango ([2.21, 2.86] y [5.31, 7.03] ft), cerca de
        # n = 0.025.
        "n_interpretado": {
            "tipico": 0.024, "pagina_pdf_tipico": 90,
            "frase_tipico": "n = 0.024 for rough culverts (corrugated)",
            "rango": (0.022, 0.027), "pagina_pdf_rango": 208,
            "frase_rango": "0.022-0.027",
        },
    },
    # --- DG 1.4: Q50 = 300 ft3/s, TW = 4.0 ft, So = 0.02, La = 250 ft,
    #     ELi = 100.0 ft, ELo = 95.0 ft; concreto, n = 0.012 (formulario).
    "cajon": {
        "pagina_pdf_enunciado": 279, "pagina_pdf_formulario": 281,
        "Q_ft3_s": 300.0, "TW_ft": 4.0, "S": 0.02, "L_ft": 250.0,
        "EL_i_ft": 100.0, "EL_o_ft": 95.0,
        "filas": (
            {"id": "cajon_6x5_escuadra",
             "B_ft": 6.0, "H_ft": 5.0, "carta": "cajon_concreto_aletas_90_15",
             "n": 0.012, "ke": 0.5,
             "publicado": {"HW_sobre_D": 1.57, "HW_entrada_ft": 7.9,
                           "d_c_ft": 4.2, "h_o_ft": 4.6, "H_ft": 3.55,
                           "EL_ho_ft": 103.2, "V_salida_ft_s": 21.1,
                           "control": "entrada"}},
            {"id": "cajon_5x5_escuadra",
             "B_ft": 5.0, "H_ft": 5.0, "carta": "cajon_concreto_aletas_90_15",
             "n": 0.012, "ke": 0.5,
             "publicado": {"HW_sobre_D": 1.91, "HW_entrada_ft": 9.6,
                           "d_c_ft": 4.8, "h_o_ft": 4.9, "H_ft": 5.2,
                           "EL_ho_ft": 105.1, "V_salida_ft_s": 20.8,
                           "control": "entrada"}},
            {"id": "cajon_5x5_bisel_45",   # el diseño ADOPTADO por el ejemplo
             "B_ft": 5.0, "H_ft": 5.0,
             "carta": "cajon_concreto_cabezal_90_bisel_45",
             "n": 0.012, "ke": 0.2,
             "publicado": {"HW_sobre_D": 1.71, "HW_entrada_ft": 8.55,
                           "d_c_ft": 4.8, "h_o_ft": 4.9, "H_ft": 5.0,
                           "EL_ho_ft": 104.9, "V_salida_ft_s": 20.8,
                           "control": "entrada"}},
        ),
    },
    # LO QUE EL FORMULARIO PUBLICA Y NO SE COMPARA, con su razon.
    # Desde la revision adversarial de T-2 las dos filas SI se comparan, por
    # intervalo y con el n interpretado (`n_interpretado`); lo que sigue sin
    # compararse CONTRA UNA CIFRA es lo de abajo.
    "no_comparado": {
        "cmp_72_bisel_45": "H, EL_ho y V_salida no se comparan contra una "
                           "cifra al 3 %: el formulario no imprime el n del "
                           "metal corrugado. Se comprueba que lo publicado "
                           "cae en el intervalo del rango de n de la Tabla "
                           "B.1",
        "cmp_60_bisel_45": "H y EL_ho no se comparan contra una cifra al 3 %, "
                           "por lo mismo; se comprueban por intervalo. La "
                           "velocidad de salida si (no depende de n)",
    },
    # NINGUNA FILA CAE EN LA TRANSICION 3.5 < q* < 4.0 del control de entrada
    # (q* = Ku·Q/(A·D^0.5), SI): los valores son 5.93, 4.56, 2.89 y 4.56 en el
    # circular y 4.47, 5.37 y 5.37 en el cajon. El ejemplo publicado valida
    # las dos ramas --una fila no sumergida, seis sumergidas-- y NO la recta
    # de transicion, que sigue sostenida solo por los casos patron internos.
    "q_estrella_transicion": (3.5, 4.0),
    # EL CENSO DE LO QUE QUEDA FUERA DEL 3 %, magnitud a magnitud, con la
    # diferencia MEDIDA (motor frente a publicado) y la causa. No se ajusta
    # la tolerancia ni el motor para vaciarlo (ficha T2-05).
    "fuera_de_tolerancia": {
        ("cmp_60_bisel_45", "HW_sobre_D"): (
            "-3.1 %: lectura de la Carta 3B. La ec. (A.3) con c = 0.0300 e "
            "Y = 0.74 da 1.357 para q* = 4.555; el formulario lee 1.40"),
        ("cmp_60_bisel_45", "HW_entrada_ft"): (
            "-4.4 %: ademas de la lectura anterior, la cifra impresa (7.10 "
            "ft) no es el producto de las dos que tiene al lado (1.40 x 5.0 "
            "ft = 7.00 ft)"),
        ("cajon_6x5_escuadra", "H_ft"): (
            "-3.9 %: lectura del nomograma de control de salida (Carta 15B). "
            "La formula (7) que el propio formulario imprime al pie da 3.41 "
            "ft con sus datos (A = 30 ft2, R = 30/22 ft, n = 0.012, L = 250 "
            "ft, ke = 0.5); el formulario anota 3.55"),
        ("cajon_5x5_bisel_45", "H_ft"): (
            "-11.4 %: la cifra impresa (5.0 ft) NO se reproduce con la "
            "formula (7) del pie del formulario y el ke = 0.2 que la misma "
            "fila declara, que da 4.43 ft; con ke = 0.5 daria 5.10 ft, que es "
            "la fila de encima (5.2). Es una inconsistencia interna de la "
            "fuente: pasar de ke 0.5 a 0.2 tiene que bajar H en 0.3 x V^2/2g "
            "= 0.67 ft, y el formulario la baja 0.2 ft"),
        ("cajon_5x5_bisel_45", "EL_ho_ft"): (
            "-5.6 % sobre H + h_o (la altura sobre el fondo de la salida): "
            "arrastra el H de la linea anterior"),
    },
}


# ---------------------------------------------------------------------------
# CP-13 · Hidrologia (Fase 1-bis, T-1): tiempo de concentracion, ajuste de
# frecuencia, intensidad y metodo racional -- Manual de Hidrologia, cap. III
# ---------------------------------------------------------------------------
# DORADOS CALCULADOS A MANO, Y SE DICE: el Manual no trae ejemplo numerico de
# ninguna de estas formulas (leidos enteros el num. 3.9 con su Tabla N 05, el
# 3.8.1, el 3.7 y el 3.12.2; pags. impresas 25 a 51). Cada valor esperado
# sale de la formula que la pagina imprime, con la cuenta escrita al lado, y
# lleva cinco o seis cifras: la `tolerancia` relativa del caso es esa
# precision de escritura, no la del programa. NO son la salida del modulo.
# Las entradas son numeros redondos inventados para la cuenta; no son de
# ninguna cuenca ni de ninguna estacion.
CP13_HIDROLOGIA = {
    "tolerancia": 5e-5,               # relativa: dorados escritos con 5-6 cifras

    # Kirpich, Tabla N 05: tc = 0.01947 · L^0.77 · S^-0.385 [min; m, m/m]
    #   1000^0.77 = 10^2.31 = 204.174 ; 0.05^-0.385 = e^(0.385·2.99573) = 3.16883
    #   tc = 0.01947 · 204.174 · 3.16883 = 12.5969 min
    "kirpich": {"L_m": 1000.0, "S": 0.05, "tc_min_esperado": 12.5969,
                "rango_S": (0.03, 0.10),
                "ajustes": {"superficie_de_concreto_o_asfalto": 0.4,
                            "canal_de_concreto": 0.2}},

    # California Culverts Practice, Tabla N 05: tc = 0.0195 · (L^3/H)^0.385
    #   L^3/H = 1e9/50 = 2e7 ; (2e7)^0.385 = e^(0.385·16.8112) = 646.989
    #   tc = 0.0195 · 646.989 = 12.6163 min
    # Es la misma cuenca que la de Kirpich (H = S·L = 50 m), y la tabla dice
    # que «esencialmente es la ecuación de Kirpich»: 12.62 frente a 12.60.
    "california": {"L_m": 1000.0, "H_m": 50.0, "tc_min_esperado": 12.6163,
                   "coincide_con_kirpich_dentro_de": 0.01},

    # Temez, ecuacion (30) del num. 3.12.2.1: Tc = 0.3 · (L/S^0.25)^0.76 [h; km]
    #   0.01^0.25 = 0.316228 ; 5/0.316228 = 15.8114 ; 15.8114^0.76 = 8.15112
    #   Tc = 0.3 · 8.15112 = 2.44534 h
    # Y una cuneta de 200 m al 0.5 %: 0.005^0.25 = 0.265915 ; 0.2/0.265915 =
    # 0.752120 ; ^0.76 = 0.805339 ; Tc = 0.241602 h, por debajo de 0.25 h.
    # Federal Aviation Administration, Tabla N 05:
    # tc = 0.7035 · (1.1 − C) · L^0.50 / S^0.333 [min; m, m/m]
    #   100^0.5 = 10 ; 0.02^0.333 = e^(0.333 · −3.912023) = e^−1.302704 = 0.271796
    #   tc = 0.7035 · 0.5 · 10 / 0.271796 = 12.9417 min
    # El exponente es 0.333 como lo imprime la tabla, no 1/3.
    "faa": {"C": 0.6, "L_m": 100.0, "S": 0.02, "tc_min_esperado": 12.9417},

    # Ecuacion de retardo SCS, Tabla N 05:
    # tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 / S^0.5 [min; m, m/m]
    #   1000^0.8 = 10^2.4 = 251.189 ; 1000/80 − 9 = 3.5 ; 3.5^0.7 =
    #   e^(0.7 · 1.252763) = 2.40352 ; 0.04^0.5 = 0.2
    #   tc = 0.0136 · 251.189 · 2.40352 / 0.2 = 41.0541 min
    "retardo_scs": {"L_m": 1000.0, "CN": 80.0, "S": 0.04, "area_km2": 2.0,
                    "tc_min_esperado": 41.0541, "area_max_km2": 8.0},

    # Coeficiente de uniformidad, ecuacion (31) del num. 3.12.2.1:
    # K = 1 + Tc^1.25 / (Tc^1.25 + 14), Tc en horas
    #   Tc = 1: K = 1 + 1/15 = 1.066667
    #   Tc = 2: 2^1.25 = 2.378414 ; K = 1 + 2.378414/16.378414 = 1.145216
    "uniformidad": {"casos": ((1.0, 1.066667), (2.0, 1.145216))},

    # Superficies de la plataforma vial (WSDOT Hydraulics Manual, Table 2-2 y
    # num. 2-6.2): C de 10 años, +10 % a 25, +20 % a 50, +25 % a 100, tope
    # 0.95; entre frecuencias, el incremento de la inmediatamente mayor.
    #   talud de tierra: 0.60 ; 0.60·1.10 = 0.66 ; 35 años -> el de 50:
    #   0.60·1.20 = 0.72 ; 0.60·1.25 = 0.75
    #   pavimento: 0.90 ; 0.90·1.10 = 0.99 -> tope 0.95
    "superficie_vial": {"casos": (("talud_de_tierra", 10.0, 0.60, False),
                                  ("talud_de_tierra", 25.0, 0.66, False),
                                  ("talud_de_tierra", 35.0, 0.72, False),
                                  ("talud_de_tierra", 100.0, 0.75, False),
                                  ("berma_de_tierra", 5.0, 0.50, False),
                                  ("talud_con_cesped", 50.0, 0.36, False),
                                  ("pavimento", 10.0, 0.90, False),
                                  ("pavimento", 25.0, 0.95, True)),
                        "sin_incremento_por_encima_de": 100.0},

    "temez": {"L_km": 5.0, "S": 0.01, "area_km2": 8.0, "Tc_h_esperado": 2.44534,
              "rango_h": (0.25, 24.0), "area_max_km2": 770.0,
              "fuera_de_rango": {"L_km": 0.2, "S": 0.005, "area_km2": 0.05,
                                 "Tc_h": 0.241602}},

    # Dick y Peschke, ecuacion (16): Pd = P24 · (d/1440)^0.25 ; I = Pd/(d/60)
    #   d = 60: (1/24)^0.25 = 0.451801 -> Pd = 45.1801 mm, I = 45.1801 mm/h
    #   d = 30: (1/48)^0.25 = 0.379918 -> Pd = 37.9918 mm, I = 75.9836 mm/h
    "dick_peschke": {"P24_mm": 100.0,
                     "casos": ({"d_min": 60.0, "Pd_mm": 45.1801, "I_mm_h": 45.1801},
                               {"d_min": 30.0, "Pd_mm": 37.9918, "I_mm_h": 75.9836},
                               {"d_min": 1440.0, "Pd_mm": 100.0, "I_mm_h": 4.16667})},

    # Tabla N 04, 1.5 h: interpolacion lineal entre 1 h (0.25) y 2 h (0.31):
    #   k = 0.28 -> Pd = 28 mm ; I = 28/1.5 = 18.6667 mm/h
    "tabla_04": {"P24_mm": 100.0, "d_min": 90.0, "k": 0.28, "Pd_mm": 28.0,
                 "I_mm_h": 18.6667, "fila_exacta": (6.0, 0.56)},

    # Gumbel por momentos (num. 3.7.1.7): alfa = 1.2825/sigma ; beta = mu −
    # 0.45·sigma ; x_T = beta − ln(−ln(1 − 1/T))/alfa
    #   mu = 100, sigma = 20: alfa = 0.064125 ; beta = 91
    #   T = 50: −ln(−ln 0.98) = 3.90194 -> x = 91 + 3.90194/0.064125 = 151.849
    #   T = 71: −ln(−ln(70/71)) = 4.25560 -> x = 91 + 4.25560/0.064125 = 157.364
    "gumbel": {"media": 100.0, "desviacion": 20.0,
               "cuantiles": ((50.0, 151.849), (71.0, 157.364))},

    # Normal y log normal de 2 parametros sobre la serie 10..50 (num. 3.7.1.1
    # y 3.7.1.2), y su Kolmogorov-Smirnov (num. 3.7.2 b):
    #   media 30 ; S = raiz(1000/4) = 15.8114 ; z(1 − 1/50) = 2.05375
    #   normal:     30 + 2.05375 · 15.8114 = 62.4726
    #   log normal: Y = 3.26008, Sy = 0.635509 (ln, n − 1) -> exp(Y + z·Sy) = 96.0876
    #   K-S normal: Fo = 5/6, 4/6, 3/6, 2/6, 1/6 (de mayor a menor) ;
    #     F(50) = 0.897048, F(40) = 0.736455, F(30) = 0.5 -> diferencias
    #     0.06371, 0.06979, 0, 0.06979, 0.06371 ; D = 0.06979 < d(5; 0.05) = 0.56
    "serie": {"valores": (10.0, 20.0, 30.0, 40.0, 50.0), "TR": 50.0,
              "alfa": 0.05, "media": 30.0, "S": 15.8114,
              "normal_P_TR": 62.4726, "lognormal_P_TR": 96.0876,
              "D_normal": 0.06979, "tolerancia_D": 1e-3, "d_critico": 0.56},

    # Metodo racional, ecuacion (28): Q = 0.278 · C · I · A [m3/s; mm/h; km2]
    #   0.278 · 0.5 · 50 · 2 = 13.9 m3/s
    # Con el coeficiente de uniformidad de Tc = 2 h (ecuacion 29):
    #   13.9 · 1.145216 = 15.9185 m3/s
    # El caudal de aporte de una cuneta (num. 4.1.2.1 b, que escribe
    # C·I·A/3.6) se calcula con ESTE mismo 0.278: no hay segundo coeficiente.
    "racional": {"C": 0.5, "I_mm_h": 50.0, "area_km2": 2.0, "Q_m3s": 13.9,
                 "area_limite_km2": 10.0, "K": 1.145216, "Q_con_K_m3s": 15.9185},

    # Caudal especifico del punto A-01 del INFORME (§3.1): 1.167 m3/s sobre
    # 850 ha. q = 1.167/8.5 = 0.137294 m3/s por km2 ; C·I = q/0.278 = 0.49386
    "caudal_especifico": {"Q_m3s": 1.167, "area_km2": 8.5,
                          "q_m3s_km2": 0.137294, "lamina_mm_h": 0.49386},
}


# ---------------------------------------------------------------------------
# CP-T6 · LONGITUD DEL CONDUCTO POR EXTREMO (T-6 de la cadena T) -- a mano
# ---------------------------------------------------------------------------
# El dorado del metodo `por_extremo` de `M7.longitud_del_conducto`, con la
# ARITMETICA ESCRITA y sin la formula cerrada del codigo. (CP-9 sigue siendo
# el dorado del terraplen simetrico, la formula anterior.) No lleva numero de
# serie a proposito: T-6 corrio en paralelo con otros prompts de la cadena
# que tambien añadieron casos (CP-13 es el de hidrologia de T-1).
#
# El punto es A-01 del fixture: ancho de plataforma 9.60 m, rasante 44.20,
# terreno 42.10 (el fondo de entrada ADOPTADO), esviaje 15 grados, S = 0.006,
# talud 2.0 H:V. La geometria, sobre la seccion transversal del cruce:
#
#   el talud de la entrada baja 44.20 - 42.10 = 2.10 m   -> 2.0 * 2.10 = 4.20 m
#   el de la salida baja 2.10 m MAS la caida S*L          -> 2.0 * (2.10 + 0.006 L)
#   medido normal a la via, el conducto ocupa             L * cos(15)
#
#       L * 0.9659258 = 9.60 + 4.20 + 4.20 + 0.012 L
#       L * (0.9659258 - 0.012) = 18.00
#       L = 18.00 / 0.9539258 = 18.869392 m
#
# Y SIN DESPEJAR, que es la comprobacion independiente: empezando en
# L0 = 18.00 / 0.9659258 = 18.634971 (la formula anterior) e iterando
# L <- (9.60 + 4.20 + 2.0*(2.10 + 0.006 L)) / 0.9659258 se obtiene
# 18.866479, 18.869355, 18.869391, 18.869392, ... El test rehace esa
# iteracion: no usa el cociente de arriba.
#
#   caida          = 0.006 * 18.869392           = 0.113216 m
#   cota de salida = 42.10 - 0.113216            = 41.986784 msnm
#   proyeccion de la salida = 2.0 * (2.10 + 0.113216) = 4.426433 m
#   comprobacion: 9.60 + 4.20 + 4.426433 = 18.226433 = 18.869392 * 0.9659258
#
# CON PERALTE de +4 % (sube el borde de la ENTRADA): medio ancho 4.80 m,
# 0.04 * 4.80 = 0.192 m. Bordes a 44.392 y 44.008; el talud de la entrada baja
# 2.292 m y el de la salida 1.908 m mas la caida. La suma 2.292 + 1.908 = 4.20
# es la misma, y por eso L NO CAMBIA: 18.869392 m. Lo que cambia es el reparto:
#
#   semilongitud de la entrada = (4.80 + 2.0 * 2.292) / 0.9659258 = 9.715032 m
#   semilongitud de la salida  = 18.869392 - 9.715032            = 9.154360 m
#
# CON EL FONDO MEDIDO en el cauce a 41.50 msnm (0.60 m bajo el terreno): cada
# talud baja 44.20 - 41.50 = 2.70 m.
#
#       L = (9.60 + 2.0 * (2.70 + 2.70)) / 0.9539258 = 20.40 / 0.9539258
#         = 21.385311 m
#   caida = 0.128312 m ; cota de salida = 41.50 - 0.128312 = 41.371688 msnm
#
# CON BOMBEO de 2 % (y sin peralte): los dos bordes bajan 0.02 * 4.80 = 0.096
# m, cada talud baja 2.004 m:  L = (9.60 + 2.0 * 4.008) / 0.9539258
#   = 17.616 / 0.9539258 = 18.466845 m. Bombeo y peralte son EXCLUYENTES: con
# los dos a la vez no hay dorado, hay `DatoInvalidoError`.
CP_T6_LONGITUD_POR_EXTREMO = {
    "ancho_plataforma": 9.60, "cota_rasante": 44.20, "cota_terreno": 42.10,
    "esviaje_grados": 15.0, "S": 0.006, "talud": 2.0,
    "cos_esviaje": 0.9659258,
    # --- fondo adoptado igual al terreno, plataforma horizontal -------------
    "longitud_esperada": 18.869392,              # m
    "longitud_formula_anterior": 18.634971,      # m   18.00 / cos(15)
    "caida_esperada": 0.113216,                  # m
    "cota_salida_esperada": 41.986784,           # msnm
    "proyeccion_entrada_esperada": 4.20,         # m
    "proyeccion_salida_esperada": 4.426433,      # m
    # --- peralte +4 % --------------------------------------------------------
    "peralte": 0.04,
    "cota_borde_entrada_con_peralte": 44.392,    # msnm
    "cota_borde_salida_con_peralte": 44.008,     # msnm
    "longitud_con_peralte_esperada": 18.869392,  # m   la misma
    "semilongitud_entrada_con_peralte": 9.715032,    # m
    "semilongitud_salida_con_peralte": 9.154360,     # m
    # --- fondo medido 0.60 m bajo el terreno ---------------------------------
    "cota_fondo_entrada_medida": 41.50,          # msnm
    "longitud_con_fondo_medido_esperada": 21.385311,     # m
    "cota_salida_con_fondo_medido_esperada": 41.371688,  # msnm
    # --- bombeo 2 % ----------------------------------------------------------
    "bombeo": 0.02,
    "longitud_con_bombeo_esperada": 18.466845,   # m
    # Los dorados llevan seis decimales; el salto del error mas cercano (la
    # formula anterior) es 0.234 m.
    "tolerancia": 1e-5,                          # m
}


# ===========================================================================
# --- T-5 --- CP_FASE_8_ESTRUCTURAL: la Fase 8 real del conducto (INF-3.3.5)
# ===========================================================================
#
# LOS DORADOS SE CALCULARON A MANO, EN UNIDADES INGLESAS, ecuacion por
# ecuacion de AASHTO LRFD 9a ed. (kip, ft, in, psf, ksi), y no con M8: es la
# unidad en que la fuente escribe las ecuaciones, de modo que la conversion a
# SI que M8 hace UNA vez (constantes_normativas, bloque T-5) queda probada por
# el contraste. Pesos: 120 pcf el relleno compactado y 140 pcf el paquete
# (Manual de Puentes Tabla 2.4.2.1-1, PDF 103), 62.4 pcf el agua (AASHTO
# 12.10.2.2, PDF 1692). La unica diferencia de constante con M8 es la del
# agua (9.81 kN/m3 = 62.45 pcf, +0.08 %), y por eso la tolerancia es
# relativa 1e-3.
#
# EL PUNTO ES A-01 DEL FIXTURE (tests/ejemplo_puntos.csv): subrasante 44.05,
# rasante 44.20 (paquete 0.15 m), con el concreto de 0.90 m que la corrida de
# perfil dimensiona. Las alturas de relleno sobre la clave fisica son las de
# `M5.altura_relleno_sobre_clave` con cada envolvente de pared: 0.950 m el
# concreto (t = 0.100), 1.035 m el TMC (68 x 13 + 2.01 = 0.015), 0.960 m el
# HDPE (t = 0.08975, OD maximo de la Tabla A12-11).
#
# LA CARGA VIVA (3.6.1.2.6b, PDF 81-82; HL-93 del Manual 2.4.3.2.2.2/.3,
# PDF 105; m = 1.20, PDF 106; IM 2.4.3.3.2, PDF 110), concreto, H = 1.10 m
# = 3.6089 ft, D_i = 2.9528 ft:
#   LLDF = 1.15 + 0.60 (2.9528 - 2)/6 = 1.24528           (Tabla 3.6.1.2.6a-1)
#   H_int-t = (6 - 20/12 - 0.06*2.9528)/1.24528 = 3.3375 ft < H: interactuan
#     w_w = 20/12 + 6 + 1.24528*3.6089 + 0.17717 = 12.338 ft; P = 32 kip
#   H_int-p (camion) = (14 - 10/12)/1.24528 = 10.573 ft > H:
#     l_w = 10/12 + 1.24528*3.6089 = 5.3274 ft
#   IM con D_E = 0.95 m = 3.1168 ft, la cubierta de TIERRA (sin el paquete,
#   el IM mayor): 33 (1 - 0.125*3.1168) = 20.143 %
#   P_L = 32 (1.20143)(1.20)/(12.338*5.3274) = 0.70189 ksf = 33.607 kPa
#   (el tandem, con los ejes interactuando, da 0.6264 ksf: gobierna el camion)
#
# EL CONCRETO (metodo indirecto, 12.10.4.3.1, PDF 1702; VAF Tipo 3 = 1.40,
# Tabla 12.10.2.1-3, PDF 1691; B_FE Tabla 12.10.4.3.2a-1, PDF 1703; B_FLL
# Tabla 12.10.4.3.2c-1, PDF 1704):
#   W_E = 1.40 (3.6089 ft)(120*3.1168 + 140*0.4921) = 2237.8 lb/ft
#   W_F = 62.4 pi/4 (2.9528)^2 = 427.3 lb/ft
#   W_L = 701.89 psf * min(l_w, B_c = 3.6089 ft) = 2533.1 lb/ft
#   B_FE = 2.4 - 0.1 (35.433 - 24)/12 = 2.3047 (Tipo 3); B_FLL = 2.2
#   D = (12/35.433)[(2237.8 + 427.3)/2.3047 + 2533.1/2.2] = 781.56 lb/ft/ft
#     = 37.421 N/m/mm  <  50.0 de la Clase II: Clase II
#
# EL TMC (12.7.2, PDF 1663-1665; eta 1.05, gamma_EV 1.95, gamma_LL 1.75):
#   H = 1.185 m = 3.888 ft, LLDF 1.15, D_E = 1.035 m: IM = 18.993 %,
#   P_L = 0.69951 ksf (camion)
#   P_sp = 120*3.3957 + 140*0.4921 = 476.38 psf; P_w = 62.4*1.5256 = 95.20 psf
#   P_FD = 1.05 (1.95*476.38 + 95.20) = 1075.37 psf
#   T_L = 1075.37*2.9528/2 + 1.05*1.75*699.51*2.9528*1/2 = 3485.3 lb/ft
#       = 50.864 kN/m
#   f_cr (12.7.2.4, r = 4.371 mm) = 42.015 ksi > F_y = 33 ksi
#   A_req = (3485.3/12 lb/in)/(33 000 psi) = 0.0088012 in2/in = 0.22355 mm2/mm
#
# EL HDPE (12.12, perfil minimo de 36 in de la Tabla A12-11, PDF 1746;
# Cl-95, 75 años; suma por duracion):
#   P_sp = 120 (3.1496 + 0.11*3.5417) + 140*0.4921 = 493.60 psf = 3.4278 psi
#   M_s = 0.530 + 0.095 (2.4278/4) = 0.58766 ksi              (Tabla 12.12.3.5-1)
#   R = (35.433 + 42.5)/4 = 19.483 in; A_g = 0.375 in2/in
#   S_H,75 = 0.9*0.58766*19.483/(21*0.375) = 1.3085 -> VAF = 0.73674
#   S_H,ini = 0.24982 -> F_2 = 0.82617
#   T_d = 1.05 (1.95*0.73674*493.60 + 110.5)(1.77083) = 1524.0 lb/ft
#   A_eff,75 = 0.5*0.375*3.0*0.25/0.9 = 0.15625 in2/in -> eps_d = 0.038705
#   P_L (D_E = 0.96 m: IM = 20.008 %) = 0.76277 ksf
#   T_l = 1.05*1.75*762.77*1*1*0.82617*1.77083 = 2050.5 lb/ft
#   A_eff,ini = 0.16875 in2/in -> eps_l = 0.0092055
#   eps_uc = 0.047910 > phi_T eps_yc = 0.041: NO CUMPLE
#   Pandeo (12.12.3.10.1e, C_n 0.55, nu 0.40): R_h = 11.4/(11 + 3.2472/3.1496)
#     = 0.94755; [0.9*0.58766*0.2/0.36]^(2/3) = 0.4420
#     eps_bck,75 = 1.2*0.55*(21*0.222)^(1/3)*0.4420*0.94755/(0.15625*21)
#                = 0.14072; eps_bck,ini (110 ksi, A 0.16875) = 0.043200
#     u = 0.038705/0.14072 + 0.0092055/0.043200 = 0.48814 <= 0.70: cumple
#     (suma por duracion). Y POR LA LETRA DE 12.12.3.3 (cierre de T-5), todo
#     con el modulo de 75 años: F_2,75 = 0.95/(1 + 0.6*1.3085) = 0.53218;
#     T_l,75 = 1.05*1.75*762.77*0.53218*1.77083 = 1320.9 lb/ft;
#     eps_l,75 = (1320.9/12)/(0.15625*21000) = 0.033545;
#     u = (0.038705 + 0.033545)/0.14072 = 0.51342. Rige la mayor: 0.51342.
#   Deflexion (12.12.2.2, K_B 0.10, D_L 1.5): E I/R^3 = 21000*0.222/19.483^3
#     = 0.63037 psi; 0.061 M_s = 35.847 psi
#     Spangler = 0.1 (1.5*3.42778 + 5.2970) 42.5 / 36.478 = 1.2162 in
#     eps_sc = 69.97/3281.25 + 92.99/18562.5 = 0.026335 -> 1.0262 in
#     Delta = 2.2424 in = 0.056957 m > 0.05*0.90 = 0.045 m: NO CUMPLE
#
# EL CONTRASTE ASD (ASTM A796 num. 8; el expediente de referencia «VARIOS»):
# D = 0.90 m, DL = 4.5 kPa y LL = 86 kPa (la H20 de 6.2.2.1 a 1 ft):
#   C = 90.5 * 0.90/2 = 40.725 kN/m
#   A = 40.725 * 2 / 230 = 0.35413 mm2/mm (el 0.354 del expediente, que
#       redondea F_y a 230 MPa); con el 225 MPa de A796-13 num. 4: 0.36200
_CP_F8_H_REL = {"concreto_reforzado": 0.950, "tmc": 1.035, "hdpe": 0.960}


def _cp_f8_punto_A01():
    """A-01 de tests/ejemplo_puntos.csv, cargado por M0 (sin copiar valores)."""
    from pathlib import Path
    from src.modulos.M0_carga import cargar_puntos
    ruta = Path(__file__).resolve().parent.parent / "ejemplo_puntos.csv"
    return next(p for p in cargar_puntos(ruta) if p.id == "A-01")


CP_FASE_8_ESTRUCTURAL = {
    "punto_A01": _cp_f8_punto_A01,
    "D": 0.90,
    "H_relleno": _CP_F8_H_REL,
    "e_paquete": 0.15,
    "tolerancia_rel": 1e-3,
    # Carga viva sobre el concreto, H = 1.10 m.
    "LL_concreto": {"LLDF": 1.24528, "IM_pct": 20.143, "l_w_m": 1.62380,
                    "P_L_kPa": 33.607, "vehiculo": "camion", "D_E_m": 0.95},
    "concreto": {"W_E_kN_m": 32.658, "W_F_kN_m": 6.2359, "W_L_kN_m": 36.968,
                 "B_FE": 2.3047, "B_FLL": 2.2, "D_req_N_m_mm": 37.421,
                 "clase": "II", "D_clase": 50.0},
    "tmc": {"P_L_kPa": 33.493, "T_L_kN_m": 50.864, "f_cr_MPa": 289.68,
            "A_req_mm2_mm": 0.22355, "plancha": "68x13/2.01"},
    "hdpe": {"eps_d": 0.038705, "eps_l": 0.0092055, "eps_uc": 0.047910,
             "eps_bck_lp": 0.14072, "eps_bck_ini": 0.043200, "u_bck": 0.48814,
             "u_letra": 0.51342,
             "Delta_m": 0.056957, "eps_sc": 0.026335,
             "eps_lim": 0.041, "cumple_empuje": False},
    # Segun el INFORME §1.1 (repositorio Cotas-esviaje-alcantarillas): las
    # paginas del PDF «VARIOS» no se verificaron en esta sesion.
    "varios_asd": {"S_m": 0.90, "P_kPa": 90.5, "T_kN_m": 40.725,
                   "A_fy230": 0.35413, "A_fy225": 0.36200,
                   "A_publicado": 0.354, "r_mm": 4.348,
                   "FF_publicado": 0.109},
}


# ===========================================================================
# --- T-5 (cierre) --- CP_FASE_8_CIERRE: los dorados de las correcciones de
# las dos auditorias adversariales (2026-11-12)
# ===========================================================================
#
# CALCULADOS A MANO EN UNIDADES INGLESAS, igual que CP_FASE_8_ESTRUCTURAL y
# con las mismas constantes (120 y 140 pcf, 62.4 pcf el agua, HL-93 de 32 y
# 25 kip, m = 1.20), SIN M8. Cada uno fija algo que la FASE A no fijaba.
#
# (1) GOBIERNA EL VEHICULO DE MAYOR EFECTO. Tubo de concreto de 2.10 m (pared
# de 0.200 m: B_c = 2.50 m = 8.2021 ft), 0.47 m de relleno sobre la clave y
# 0.15 m de paquete, Tipo 3:
#   H = 0.62 m = 2.0341 ft; D_i = 6.8898 ft; D_E = 1.5420 ft
#   LLDF = 1.15 + 0.60 (6.8898 - 2)/6 = 1.63898; IM = 33 (1 - 0.125*1.5420)
#        = 26.639 %
#   H_int-t = (6 - 1.6667 - 0.06*6.8898)/1.63898 = 2.3917 ft > H: una rueda
#     w_w = 1.6667 + 1.63898*2.0341 + 0.4134 = 5.4139 ft
#   CAMION: H_int-p = (14 - 0.8333)/1.63898 = 8.03 ft > H: P = 16 kip,
#     l_w = 0.8333 + 3.3338 = 4.1672 ft
#     P_L = 16 (1.26639)(1.2)/(4.1672*5.4139) = 1.0777 ksf = 51.602 kPa
#     W_L = 1077.7 psf * min(4.1672, 8.2021) = 4491.1 lb/ft = 65.543 kN/m
#   TANDEM: H_int-p = (4 - 0.8333)/1.63898 = 1.932 ft < H: P = 25 kip,
#     l_w = 0.8333 + 4 + 3.3338 = 8.1672 ft
#     P_L = 25 (1.26639)(1.2)/(8.1672*5.4139) = 0.8592 ksf = 41.140 kPa
#     W_L = 859.2 psf * min(8.1672, 8.2021) = 7017.4 lb/ft = 102.41 kN/m
#   El camion da MAS PRESION (51.6 contra 41.1 kPa) y el tandem MAS CARGA
#   (102.4 contra 65.5 kN/m): gobierna el tandem.
#   W_E = 1.40 (8.2021)(120*1.5420 + 140*0.4921) = 2915.9 lb/ft
#   W_F = 62.4 pi/4 (6.8898)^2 = 2326.4 lb/ft; B_FE(82.68 in, Tipo 3) = 2.2;
#   B_FLL = 2.2
#   D = (12/82.677)[(2915.9 + 2326.4)/2.2 + 7017.4/2.2] = 808.83 lb/ft/ft
#     = 38.727 N/m/mm  (con el camion: 642.16 lb/ft/ft = 30.747 N/m/mm)
#
# (2) LA CARGA VIVA SE CONSERVA PASADOS LOS 8 FT. Tubo de concreto de 0.90 m
# de A-01 con 2.90 m de relleno (H = 3.05 m = 10.0066 ft > 8 ft y > la luz),
# Tipo 3; IM = 0:
#   W_E = 1.40 (3.6089)(120*9.5144 + 140*0.4921) = 6116.7 lb/ft; W_F = 427.3
#   TANDEM (ruedas y ejes interactuando): l_w = 0.8333 + 4 + 12.4610 =
#     17.2943 ft; w_w = 1.6667 + 6 + 12.4610 + 0.1772 = 20.3048 ft;
#     P_L = 50 (1.2)/(17.2943*20.3048) = 0.17086 ksf = 8.181 kPa
#     W_L = 170.86 * 3.6089 = 616.6 lb/ft (camion: 513.4 lb/ft)
#   D conservando = (12/35.433)[(6116.7 + 427.3)/2.3047 + 616.6/2.2]
#     = 1056.5 lb/ft/ft = 50.587 N/m/mm > 50.0: la Clase II NO alcanza
#   D despreciando = (12/35.433)(6544.0/2.3047) = 961.6 lb/ft/ft
#     = 46.043 N/m/mm < 50.0: «cumplia»
#
# (3) EL TIPO 4 AL LADO. A-01, tubo de 0.90 m, 0.95 m de relleno:
#   W_E = 1.45 (3.6089)(120*3.1168 + 140*0.4921) = 2317.7 lb/ft; B_FE = 1.7
#   D_T4 = (12/35.433)[(2317.7 + 427.3)/1.7 + 2533.1/2.2] = 936.79 lb/ft/ft
#     = 44.854 N/m/mm  (Tipo 3: 37.421)
#
# (4) EL HDPE QUE CUMPLE, con el relleno de archivo (Si-95) y el perfil
# minimo de 36 in declarado como del fabricante, en A-01 (0.960 m):
#   P_sp = 493.60 psf = 3.4278 psi; M_s = 1.415 + 0.255 (2.4278/4) = 1.56977
#   S_H,75 = 0.9*1.56977*19.483/(21*0.375) = 3.4953 -> VAF = 0.50265,
#     F_2,75 = 0.95/(1 + 0.6*3.4953) = 0.30673
#   S_H,ini = 0.66729 -> F_2,ini = 0.67839
#   T_d = 1.05 (1.95*0.50265*493.60 + 110.5)(1.77083) = 1105.0 lb/ft
#     -> eps_d = (1105.0/12)/(0.15625*21000) = 0.028065
#   T_l = 1.05*1.75*762.77*0.67839*1.77083 = 1683.7 lb/ft
#     -> eps_l = (1683.7/12)/(0.16875*110000) = 0.007559
#   eps_uc = 0.035624 <= 0.041: CUMPLE
#   Pandeo: R_h = 0.94755; [0.9*1.56977*0.2/0.36]^(2/3) = 0.85094
#     eps_bck,75 = 1.2*0.55*(21*0.222)^(1/3)*0.85094*0.94755/(0.15625*21)
#                = 0.27092; eps_bck,ini = 0.083169
#     suma por duracion: 0.028065/0.27092 + 0.007559/0.083169 = 0.19448
#     letra de 12.12.3.3: eps_l,75 = (1.05*1.75*762.77*0.30673*1.77083/12)
#       /(0.15625*21000) = 0.019334; (0.028065 + 0.019334)/0.27092 = 0.17496
#     rige la mayor: 0.19448 <= 0.70: CUMPLE (aqui gobierna la suma por
#     duracion; con Cl-95 gobierna la letra: CP_FASE_8_ESTRUCTURAL)
#   Deflexion: 1.2490 in = 0.031725 m <= 0.05*0.90 = 0.045 m: CUMPLE
#   FF (12.12.3.6, con el diametro EXTERIOR y el modulo INICIAL):
#     42.5^2/(110*0.222) = 73.97 in/kip = 0.42236 mm/N <= 95.0 in/kip
#     = 0.54246 mm/N: CUMPLE
#   El relleno maximo cae entre 1.40 m (eps_uc = 0.040041) y 1.60 m
#   (eps_uc = 0.042580, ya con el tandem gobernando P_L C_L F_1).
#
# (5) LA RAMA ELASTICA DEL PANDEO DEL TMC (Eq. 12.7.2.4-2), que ningun test
# tocaba: r = 4.371 mm (0.17209 in), k = 0.22, E_m = 29 000 ksi, F_u = 45 ksi
#   umbral S = (r/k) sqrt(24 E_m/F_u) = 0.78221*124.365 = 97.280 in = 2470.9 mm
#   S = 3000 mm = 118.110 in > umbral:
#     f_cr = 12 E_m/(k S/r)^2 = 348 000/(150.995)^2 = 15.2635 ksi = 105.238 MPa
#
# (6) EL NIVEL FREATICO SOBRE LA CLAVE. TMC de 0.90 m de A-01 (H_rel 1.035 m,
# envolvente 0.015 m): la clave exterior queda en 44.05 - 1.035 = 43.015, el
# centro en 43.015 - 0.015 - 0.45 = 42.550 msnm. Con el terreno en 44.00 y el
# NF a 0.30 m: agua en 43.70, H_w = 1.150 m en vez de D/2 + t = 0.465 m.
#   Delta T_L = eta gamma_WA gamma_w (1.150 - 0.465) S/2
#             = 1.05*1.0*9.81*0.685*0.45 = 3.1751 kN/m
# HDPE de 0.90 m (H_rel 0.960, D_o = 1.0795 m): centro en 44.05 - 0.960 -
# 0.53975 = 42.55025; H_w = 1.14975 m en vez de D_o/2 = 0.53975 m.
#   Delta T_d = 1.05*1.0*9.81*0.61000*1.0795/2 = 3.3914 kN/m
#   Delta eps_d = 3.3914/(A_eff,75 E_75) = 3.3914/(0.00396875*144 790)
#               = 0.0059019
#
# (7) F_1 > 1 Y EL CAMBIO DE VEHICULO EN UN FLEXIBLE. TMC de 2.10 m (6.8898
# ft), LLDF 1.15, paquete 0.15 m (el dorado que el test de la FASE A no
# tenia: reconstruia T_L con la formula de M8 y las magnitudes del paso):
#   H_rel = 0.40 m: H = 1.8045 ft; IM = 33 (1 - 0.125*1.3123) = 27.587 %
#     una rueda: w_w = 1.6667 + 2.0751 + 0.4134 = 4.1552 ft;
#     l_w = 0.8333 + 2.0751 = 2.9085 ft = 0.8865 m (los dos vehiculos)
#     camion: P_L = 16 (1.27587)(1.2)/(2.9085*4.1552) = 2.0270 ksf = 97.053 kPa
#     tandem: 12.5 kip -> 1.5836 ksf = 75.823 kPa
#     C_L = l_w = 0.8865 m; F_1 = 0.75*6.8898/2.9085 = 1.77665 (> F_min = 1)
#     P_L C_L F_1 = 152.86 (camion) contra 119.42 kN/m: gobierna el CAMION
#   H_rel = 0.99 m: H = 3.7402 ft; IM = 19.602 %; ruedas interactuando,
#     w_w = 12.3812 ft
#     camion: l_w = 5.1345 ft = 1.5650 m; P_L = 0.72245 ksf = 34.591 kPa;
#       F_1 = max(0.75*6.8898/5.1345, 1) = 1.00639; efecto 54.48 kN/m
#     tandem: l_w = 9.1345 ft = 2.7842 m > S -> C_L = S = 2.10 m;
#       P_L = 0.63451 ksf = 30.381 kPa; F_1 = 1; efecto 63.80 kN/m
#     gobierna el TANDEM, que presiona menos.
CP_FASE_8_CIERRE = {
    "tmc_f1": {"D": 2.10,
               0.40: {"vehiculo": "camion", "P_L_kPa": 97.053, "C_L_m": 0.8865,
                      "F_1": 1.77665, "efecto_kN_m": 152.86},
               0.99: {"vehiculo": "tandem", "P_L_kPa": 30.381, "C_L_m": 2.10,
                      "F_1": 1.0, "efecto_kN_m": 63.80}},
    "tolerancia_rel": 1e-3,
    "efecto": {"D": 2.10, "t": 0.200, "H_rel": 0.47, "e_paq": 0.15,
               "camion": {"P_L_kPa": 51.602, "l_w_m": 1.27016,
                          "W_L_kN_m": 65.543, "D_N_m_mm": 30.747},
               "tandem": {"P_L_kPa": 41.140, "l_w_m": 2.48936,
                          "W_L_kN_m": 102.41, "D_N_m_mm": 38.727},
               "gobierna": "tandem"},
    "conservar": {"D": 0.90, "H_rel": 2.90, "P_L_kPa": 8.181,
                  "vehiculo": "tandem", "D_conservando": 50.587,
                  "D_despreciando": 46.043, "D_clase": 50.0},
    "tipo_4": {"D": 0.90, "D_T4": 44.854, "D_T3": 37.421},
    "hdpe_si95": {"eps_d": 0.028065, "eps_l": 0.007559, "eps_uc": 0.035624,
                  "u_duracion": 0.19448, "u_letra": 0.17496,
                  "Delta_m": 0.031725, "FF_mm_N": 0.42236,
                  "FF_lim_mm_N": 0.54246, "H_max_entre": (1.40, 1.60)},
    "pandeo_elastico": {"r_mm": 4.371, "S_umbral_mm": 2470.9,
                        "S_mm": 3000.0, "f_cr_MPa": 105.238},
    "nf": {"cota_terreno": 44.00, "NF": 0.30, "delta_T_tmc_kN_m": 3.1751,
           "delta_eps_d_hdpe": 0.0059019},
}


# ===========================================================================
# --- T-9 (correcciones de la auditoria) --- CP_T9_CUNETA: la capacidad de la
# cuneta triangular, VB2 y la longitud por capacidad (M10, Fase 10)
# ===========================================================================
# CALCULADO A MANO, con la aritmetica escrita, independiente de la formula
# cerrada de M10. El Manual de Hidrologia no trae un ejemplo numerico que
# sirva: sus ecuaciones de ejemplo (4.1), (4.3), (4.4) y (4.6) no reproducen
# la geometria que nombran (ficha T9-04). Geometria del triangulo de taludes
# 1:Z1 y 1:Z2 (V:H) y tirante y: A = (Z1 + Z2)·y²/2 ; P = y·(√(1+Z1²) +
# √(1+Z2²)) ; Rh = A/P ; Manning (117) con n = 1/K de la Tabla Nº 32.
#
# «auditor» -- el caso de H1 de la auditoria adversarial de T-9: seccion
# 0.20 x 0.50 m (minimo de la region SECA, que la ventana de archivo ya no
# admite: se sustituye el valor efectivo), Z2 = 0.5, concreto (K = 67),
# S = 0.005, Q de aporte 0.095 m3/s (el de B-01).
#   Z1 = 0.50 / 0.20 = 2.5
#   A  = (2.5 + 0.5) · 0.04 / 2 = 0.060 m2
#   P  = 0.20 · (√7.25 + √1.25) = 0.20 · (2.692582 + 1.118034) = 0.762123 m
#   Rh = 0.060 / 0.762123 = 0.078727 m ; Rh^(2/3) = 0.183689
#   Q  = 67 · 0.060 · 0.183689 · √0.005 = 4.02 · 0.183689 · 0.0707107
#      = 0.052215 m3/s   (V = 0.870 m/s < 4.50: gobierna la cuneta llena)
#   VB2: 0.095 > 0.052215 -> NO CUMPLE, margen 0.052215 − 0.095 = −0.042785
#   L con el tramo de 200 m: 0.052215 · 200 / 0.095 = 109.93 m
#   L con el tramo de 530 m: 0.052215 · 530 / 0.095 = 291.30 m
#
# «archivo» -- la seccion de archivo (decision A): 0.40 x 1.20 m, Z2 = 1,
# concreto, S = 0.01.
#   Z1 = 3 ; A = 4 · 0.16 / 2 = 0.32 m2
#   P  = 0.40 · (√10 + √2) = 0.40 · (3.162278 + 1.414214) = 1.830596 m
#   Rh = 0.174806 m ; Rh^(2/3) = 0.312635
#   Q  = 67 · 0.32 · 0.312635 · 0.1 = 0.670290 m3/s (V = 2.095 m/s)
#
# «arena_fina» -- la seccion de archivo con «Arena fina o limo» (Tabla Nº 33:
# 0.20 – 0.60 m/s, extremo inferior; Tabla Nº 32: cuneta excavada, K = 33) y
# S = 0.005: gobierna la velocidad limite.
#   Rh_v = (n·v/√S)^(3/2) = (0.030303 · 0.20 / 0.0707107)^(3/2)
#        = (0.0857099)^(3/2) = 0.0250927 m
#   c    = Rh / y = (3 + 1) / (2 · (√10 + √2)) = 4 / 9.152982 = 0.437016
#   y_v  = 0.0250927 / 0.437016 = 0.0574182 m
#   A_v  = 4 · 0.0574182² / 2 = 0.00659369 m2 ; Q_v = A_v · 0.20 = 0.0013188
#
# «velocidad_Z2» -- `caudal_a_velocidad` con talud exterior distinto de 1
# (H7: con Z2 = 1 en todos los tests, el mutante Z2**2 -> Z2**3 vivia):
# v = 0.20 m/s, n = 1/33, S = 0.01, Z1 = 3, Z2 = 2.
#   Rh_v = (0.030303 · 0.20 / 0.1)^(3/2) = (0.0606061)^(3/2) = 0.0149202 m
#   c    = 5 / (2 · (√10 + √5)) = 5 / (2 · 5.398346) = 0.463105
#   y_v  = 0.0149202 / 0.463105 = 0.0322177 m
#   A_v  = 5 · 0.0322177² / 2 = 0.00259495 m2 ; Q_v = 0.000518991 m3/s
#   (con Z2**3 seria y_v = 0.036777 y Q_v = 0.000676: el mutante muere)
CP_T9_CUNETA = {
    "auditor": {
        "seccion": {"profundidad_m": 0.20, "ancho_m": 0.50,
                    "talud_exterior_HV": 0.5, "borde_libre_m": 0.0},
        "S": 0.005, "Q": 0.095,
        "A": 0.060, "Rh": 0.078727, "Q_adm": 0.052215,
        "margen_VB2": -0.042785,
        "L_200": 109.93, "L_530": 291.30,
    },
    "archivo": {"S": 0.01, "A": 0.32, "Rh": 0.174806, "Q_adm": 0.670290},
    "arena_fina": {"S": 0.005, "Rh_v": 0.0250927, "y_v": 0.0574182,
                   "Q_v": 0.0013188},
    "velocidad_Z2": {"v": 0.20, "n": 1 / 33, "S": 0.01, "Z1": 3.0, "Z2": 2.0,
                     "y_v": 0.0322177, "Q_v": 0.000518991},
}


# ===========================================================================
# --- T-7b --- ESTABILIDAD DEL CABEZAL: dorados A MANO, con la aritmetica
# ===========================================================================
# Ninguna fuente de normas/ trae un ejemplo resuelto del cabezal (el «PDF de
# VARIOS» que el encargo nombra no esta en la sesion: sus cifras van aparte,
# en CP_T7B_ENCARGO, como contraste rotulado). Estos numeros se calcularon a
# mano desde las ecuaciones de AASHTO, con la forma de la ECUACION 3.11.5.3-1
# para K_A y la de A11.3.1-1 para K_AE -- que no son la funcion del modulo,
# que deduce Coulomb de Mononobe-Okabe --, y la suma de momentos escrita.
#
# EL MURO DE TANTEO (por metro), sin agua y con relleno horizontal:
#   pantalla 0.30 x 2.00 m, trasdos vertical; zapata B = 2.00 x 0.40 m;
#   punta 0.60 m, talon 1.10 m; relleno retenido hasta la corona (h = 2.40 m
#   sobre la base) y horizontal; D_f = 0.80 m; freatico a 5.00 m.
#   gamma = 18 kN/m3 (relleno), gamma_c = 23.56 kN/m3; phi = 30 grados;
#   delta = 0.67·30 = 20.1 grados; suelo de fundacion friccionante, phi_f =
#   32 grados, gamma = 18 kN/m3.
#
# K_A (AASHTO ec. 3.11.5.3-1 y -2, theta = 90, beta = 0):
#   Gamma = [1 + sqrt( sen(50.1)·sen(30) / (sen(69.9)·sen(90)) )]^2
#         = [1 + sqrt( 0.767165·0.5 / 0.939094 )]^2
#         = [1 + sqrt(0.408460)]^2 = (1.639109)^2 = 2.686679
#   K_A   = sen^2(120) / (Gamma·sen^2(90)·sen(69.9))
#         = 0.75 / (2.686679·0.939094) = 0.75 / 2.523044 = 0.297260
#
# CARGAS SIN FACTORAR (kN/m) y brazo (x desde la punta, z desde la base):
#   DC pantalla  23.56·0.30·2.00          = 14.136    x = 0.60 + 0.15 = 0.75
#   DC zapata    23.56·2.00·0.40          = 18.848    x = 1.00
#   EV talon     18·1.10·2.00             = 39.600    x = 0.90 + 0.55 = 1.45
#   P_A          0.5·0.297260·18·2.40^2   = 15.4100
#   EH.h         15.4100·cos(20.1) = 15.4100·0.939094 = 14.4714   z = 0.80
#   EH.v         15.4100·sen(20.1) = 15.4100·0.343660 =  5.2958   x = 2.00
#   h_eq         muro paralelo, borde a mas de 1 ft: 2.0 ft = 0.6096 m (> 0.60)
#   LS.h         0.297260·18·0.6096·2.40  =  7.8283   z = 1.20
#   LS.v         18·0.6096·1.10           = 12.0701   x = 1.45
#
# RESISTENCIA I, MINIMOS (0.90 DC, 1.00 EV, 1.50 EH, 1.75 LS solo empuje):
#   N   = 0.90·32.984 + 39.600 + 1.50·5.2958 = 29.6856 + 39.6 + 7.9437
#       = 77.2293
#   H   = 1.50·14.4714 + 1.75·7.8283 = 21.7071 + 13.6995 = 35.4066
#   M_e = 0.90·(14.136·0.75 + 18.848·1.00) + 39.6·1.45 + 1.50·5.2958·2.00
#       = 0.90·29.450 + 57.420 + 15.8874 = 26.505 + 57.42 + 15.8874 = 99.8124
#   M_v = 1.50·14.4714·0.80 + 1.75·7.8283·1.20 = 17.3657 + 16.4394 = 33.8051
#   e   = 2.00/2 - (99.8124 - 33.8051)/77.2293 = 1.00 - 0.85470 = 0.14530
#   E2  : 0.14530 <= B/3 = 0.66667                                  CUMPLE
#   E3  : R_tau = 77.2293·tan(32) = 77.2293·0.624869 = 48.2582;
#         0.80·48.2582 = 38.6066 >= 35.4066                         CUMPLE
#
# RESISTENCIA I, MAXIMOS (1.25 DC, 1.35 EV, 1.50 EH, 1.75 LS con su peso):
#   N   = 1.25·32.984 + 1.35·39.6 + 1.50·5.2958 + 1.75·12.0701
#       = 41.230 + 53.460 + 7.9437 + 21.1227 = 123.7564
#   M_e = 1.25·29.450 + 1.35·57.42 + 15.8874 + 1.75·12.0701·1.45
#       = 36.8125 + 77.517 + 15.8874 + 30.6279 = 160.8448
#   e   = 1.00 - (160.8448 - 33.8051)/123.7564 = 1.00 - 1.02653 = -0.02653
#         (hacia el talon); B' = 2.00 - 2·0.02653 = 1.94694
#   sigma_v = 123.7564 / 1.94694 = 63.5646 kPa
#   Inclinacion, con las cargas SIN factorar de servicio (con el peso de LS):
#     V = 32.984 + 39.6 + 5.2958 + 12.0701 = 89.9499; H = 14.4714 + 7.8283
#       = 22.2997; 1 - H/V = 0.752088; i_q = 0.752088^2 = 0.565636;
#     i_gamma = 0.752088^3 = 0.425408
#   q_n = 18·0.80·23.2·0.565636 + 0.5·18·1.94694·30.2·0.425408
#       = 188.9661 + 225.1182 = 414.0843 (C_wq = C_wgamma = 1: freatico a
#         5.00 m > D_f + 1.5·B' = 3.72 m)
#   E1  : 63.5646 <= 0.45·414.0843 = 186.3379                       CUMPLE
#
# SERVICIO (ASD, todos los factores 1; sin el peso de LS en volteo y desl.):
#   N = 77.8798; H = 22.2997; M_e = 29.450 + 57.42 + 10.5916 = 97.4616;
#   M_v = 14.4714·0.80 + 7.8283·1.20 = 11.5771 + 9.3940 = 20.9711
#   FS volteo        = 97.4616 / 20.9711            = 4.6474  >= 1.5
#   FS deslizamiento = 77.8798·0.624869 / 22.2997   = 2.1823  >= 1.5
#   portante (con el peso de LS): N = 89.9499, e = -0.04494, B' = 1.91012,
#     q = 47.0912 kPa; q_n = 188.9661 + 0.5·18·1.91012·30.2·0.425408
#     = 188.9661 + 220.8612 = 409.8273; q_adm = 409.8273/3.0 = 136.6091
#
# SISMICA con k_h = 0.25, k_v = 0 (theta_MO = arctan 0.25 = 14.0362 grados):
#   K_AE (AASHTO A11.3.1-1, i = beta = 0, delta = 20.1) = 0.508300
#   P_AE = 0.5·18·2.40^2·0.508300 = 26.3503; dP = 26.3503 - 15.4100 = 10.9403
#   dP.h = 10.9403·0.939094 = 10.2740 a z = 0.6·2.40 = 1.44
#   dP.v = 10.9403·0.343660 =  3.7597 a x = 2.00
#   P_IR muro  = 0.25·32.984 = 8.2460 a z = (14.136·1.40 + 18.848·0.20)/32.984
#              = 23.5600/32.984 = 0.71429
#   P_IR suelo = 0.25·39.6 = 9.9000 a z = 0.40 + 1.00 = 1.40
#   Caso 1 (100 % P_AE + 50 % P_IR), sin el peso de LS, gamma_EQ = 0.5:
#     N = 32.984 + 39.6 + 5.2958 + 3.7597 = 81.6395
#     H = 14.4714 + 10.2740 + 0.5·18.146 + 0.5·7.8283 = 37.7325
#     e = 0.21561 <= 0.36667·2.00 = 0.73333 ; R_tau = 51.0140 >= 37.7325
#   Caso 2 (50 % P_AE + 100 % P_IR): 0.5·26.3503 = 13.1751 < P_A = 15.4100,
#     de modo que RIGE EL PISO ESTATICO: EH entero, sin incremento.
#     H = 14.4714 + 18.146 + 0.5·7.8283 = 36.5315
CP_T7B_ESTABILIDAD = {
    # Tolerancias de la ESCRITURA del dorado, no de la maquina.
    "tolerancia": 2e-4, "tolerancia_rel": 2e-4, "tolerancia_K": 1e-6,
    "tolerancia_fina": 1e-5, "tolerancia_mm": 2e-3, "tolerancia_cm": 1e-2,
    "geometria": {"H": 2.0, "B": 2.0, "D_f": 0.80, "espesor_corona": 0.30,
                  "espesor_base_muro": 0.30, "espesor_zapata": 0.40,
                  "ancho_talon": 1.10, "ancho_punta": 0.60},
    "gamma_relleno": 18.0, "phi_relleno": 30.0, "delta": 20.1,
    "suelo": {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0,
              "gamma_kn_m3": 18.0},
    "NF": 5.0, "h": 2.40, "h_eq": 0.6096,
    "K_A": 0.297260, "K_AE_kh_025": 0.508300,
    "cargas": {   # codigo: (V, H, x, z)
        "DC.pantalla": (14.136, 0.0, 0.75, None),
        "DC.zapata": (18.848, 0.0, 1.00, None),
        "EV.talon": (39.600, 0.0, 1.45, None),
        "EH.h": (0.0, 14.4714, None, 0.80),
        "EH.v": (5.2958, 0.0, 2.00, None),
        "LS.h": (0.0, 7.8283, None, 1.20),
        "LS.v": (12.0701, 0.0, 1.45, None),
    },
    "resistencia_min": {"N": 77.2293, "H": 35.4066, "M_e": 99.8124,
                        "M_v": 33.8051, "e": 0.14530},
    "resistencia_max": {"N": 123.7564, "M_e": 160.8448, "e": -0.02653},
    "E1_LRFD": {"sigma_v": 63.5646, "q_n": 414.0843, "q_R": 186.3379},
    "E2_LRFD": {"e": 0.14530, "e_max": 2.0 / 3.0},
    "E3_LRFD": {"H": 35.4066, "R_tau": 48.2582, "R_R": 38.6066},
    "ASD": {"FS_volteo": 4.6474, "FS_deslizamiento": 2.1823,
            "q_servicio": 47.0912, "q_adm": 136.6091},
    "sismico": {
        "k_h": 0.25, "P_AE": 26.3503, "dP_h": 10.2740, "dP_v": 3.7597,
        "z_dP": 1.44, "PIR_muro": 8.2460, "z_muro": 0.71429,
        "PIR_suelo": 9.9000, "z_suelo": 1.40,
        "caso_1": {"N": 81.6395, "H": 37.7325, "e": 0.21561,
                   "R_tau": 51.0140},
        "caso_2": {"H": 36.5315},
        "e_max": 0.73333,
    },
}

# El ejemplo numerico que el encargo de T-7b cita del «PDF de VARIOS» (pp.
# 112-122). LA FUENTE NO ESTA EN LA SESION: estas son CIFRAS DEL ENCARGO, no
# un dorado. Se usan como CONTRASTE rotulado, con tolerancia declarada. Lo
# que se pudo reconstruir de ellas, hacia atras:
#   Kp = 2.578 = tan^2(45 + phi/2)  ->  phi = 26.17 grados
#   Ka = tan^2(45 - phi/2) = 0.3879 (0.388): es RANKINE, con delta = 0
#   P_A = 2793 kg/m = 0.5·0.388·gamma·H^2 con gamma = 1600 kg/m3 y H = 3.00 m
#   dP_AE = 0.5·1600·9·(0.498 - 0.388) = 792 kg/m (791)
#   M sismico = 2793.6·(3.00/3) + 792·(0.6·3.00) = 4219 kg·m/m (4217.9): el
#     incremento va a 0.6·H, que es lo que 'punto_aplicacion_incremento_
#     sismico' adopta
#   EQ = 1.58 t = k_h·(DC + EV) = k_h·(7.47 + 3.07)  ->  k_h = 0.150
#   K_AE con phi = 26.17, delta = i = beta = 0 y k_h = 0.15: 0.4965 (0.498)
#   h_eq = 0.90 m: la fila de 10 ft (3.05 m) de la Tabla 3.11.6.4-1, 3.0 ft
# Lo que NO se pudo reconstruir: DC = 7.47 t y EV = 3.07 t, que dependen de
# la seccion del muro del ejemplo (B = 1.50 m, h = 0.38 m), que el encargo
# no da completa.
CP_T7B_ENCARGO = {
    "rotulo": "cifras del encargo; fuente no disponible en la sesion",
    "Ka": 0.388, "Kp": 2.578, "K_AE": 0.498, "h_eq_m": 0.90,
    "P_A_kg_m": 2793.0, "dP_AE_kg_m": 791.0, "M_sismico_kgm_m": 4217.9,
    "DC_t": 7.47, "EV_t": 3.07, "EQ_t": 1.58,
    "reconstruido": {"phi_grados": 26.17, "gamma_kg_m3": 1600.0, "H_m": 3.00,
                     "k_h": 0.15, "fraccion_brazo": 0.6},
    # Tolerancias del CONTRASTE: las cifras del encargo vienen redondeadas a
    # tres o cuatro cifras y phi se reconstruyo de Kp.
    "tolerancia_Ka": 0.002, "tolerancia_K_AE": 0.005, "tolerancia_Kp": 0.01,
    "tolerancia_P_A": 0.002, "tolerancia_dP_AE": 0.02,
    "tolerancia_M_sismico": 0.005, "tolerancia_EQ": 0.002,
}

# V5 por el metodo del embalse a nivel, A-01 del fixture (HW de la linea
# base, 1.042 m con el tubo de 0.90 m): a mano.
#   x_embalse = HW / S_cauce = 1.0420 / 0.006 = 173.667 m
#   L_boca    = semilongitud de entrada de 7.B (9.317 m en la linea base)
#   d = (9.317 + 173.667)·cos(15) = 182.984·0.965926 = 176.75 m
#   con ancho_derecho_via = 400 m: 176.75 <= 200.0, margen 23.25 m
#   con ancho_derecho_via = 300 m: 176.75 >  150.0  -> NO CUMPLE
CP_T7B_V5 = {"S_cauce": 0.006, "esviaje": 15.0, "cos_15": 0.965926,
             "ancho_que_cumple": 400.0, "ancho_que_no": 300.0}


# EL SEGUNDO MURO DE TANTEO, con todo lo que el primero deja en cero: pantalla
# TRAPECIAL, relleno que SUBE detras (cuña sobre el talon, parte triangulo y
# parte rectangulo), pendiente equivalente no nula y AGUA PARCIAL en el plano
# de empuje. Lo pidio la mutacion (arnes de EXT-11): con el primer muro solo,
# 77 mutantes de `cargas_del_cabezal` quedaban vivos. A mano, como el primero.
#
#   pantalla 0.25 (corona) a 0.45 (base) x 2.00 m, trasdos vertical;
#   zapata B = 2.40 x 0.40 m; punta 0.75, talon 1.20; D_f = 1.00 m.
#   relleno retenido hasta z = 2.40 m sobre la base; detras sube 0.30 m con
#   talud 2.0 H:V hasta el borde de la plataforma, y sigue horizontal.
#   gamma = 18, gamma_sat = 20 (gamma' = 10.19), gamma_c = 23.56 kN/m3;
#   phi = 30, delta = 20.1; freatico a 0.40 m bajo el pie, trasdos DRENADO:
#   el agua queda 1.00 - 0.40 = 0.60 m sobre la base, delante y detras.
#
# Geometria del relleno:
#   el talud alcanza el borde a 0.30·2.0 = 0.60 m del trasdos (< talon):
#     cuña = triangulo 0.60·0.30/2 = 0.09 m2 + rectangulo 0.60·0.30 = 0.18 m2
#   sobre el extremo del talon el terreno esta 0.30 m mas alto: h = 2.70 m
#   pendiente equivalente (talud quebrado, 2·z_rel = 4.80 m): a 4.80 m el
#     talud habria subido 2.40 m, pero se quiebra a 0.30:
#     i = arctan(0.30 / 4.80) = 3.5763 grados
#
# K_A (AASHTO 3.11.5.3-1 y -2, theta = 90, beta = i):
#   Gamma = [1 + sqrt( sen(50.1)·sen(30 - 3.5763) / (sen(69.9)·sen(93.5763)) )]^2
#         = [1 + sqrt( 0.767165·0.445005 / (0.939094·0.998053) )]^2
#         = [1 + sqrt(0.341393 / 0.937266)]^2 = (1.603526)^2 = 2.571294
#   K_A   = 0.75 / (2.571294·0.939094) = 0.310599
#
# Cargas sin factorar:
#   DC pantalla: rectangulo 23.56·0.25·2.00 = 11.780 en x = 1.20 - 0.125
#                = 1.075, z = 1.40; triangulo 23.56·0.20·2.00/2 = 4.712 en
#                x = 0.75 + 2·0.20/3 = 0.88333, z = 0.40 + 2.00/3 = 1.06667
#                total 16.492; x = (12.6635 + 4.1623)/16.492 = 1.02024;
#                z = (16.492 + 5.0261)/16.492 = 1.30476
#   DC zapata:   23.56·2.40·0.40 = 22.6176 en x = 1.20, z = 0.20
#   EV talon:    seco 18·1.20·1.80 = 38.88; mojado (0.60 - 0.40 = 0.20 m)
#                20·1.20·0.20 = 4.80; cuña 18·0.27 = 4.86; total 48.54
#                x = [43.68·1.80 + 18·(0.09·1.60 + 0.18·2.10)] / 48.54
#                  = (78.624 + 9.396)/48.54 = 1.81335
#   Empuje del suelo (diagrama en tres partes, h_seco = 2.10, h_w = 0.60):
#                K·18·2.10^2/2 = K·39.69 a z = 0.60 + 0.70 = 1.30
#                K·18·2.10·0.60 = K·22.68 a z = 0.30
#                K·10.19·0.60^2/2 = K·1.8342 a z = 0.20
#                P_A = 0.310599·64.2042 = 19.9418; z_A = 58.76784/64.2042
#                = 0.91533
#   EH.h = 19.9418·0.939094 = 18.7272 ; EH.v = 19.9418·0.343660 = 6.8532
#   LS.h = 0.310599·18·0.6096·2.70 = 9.2020 a z = 1.35
#   LS.v = 18·0.6096·1.20 = 13.1674 en x = 1.80
#   WA.h = 9.81·0.60^2/2 = 1.7658 a z = 0.20
#   WA.u = 9.81·0.60·2.40 = 14.1264 (uniforme) en x = 1.20
#
# Resistencia I, minimos (0.90 DC, 1.00 EV, 1.50 EH, 1.75 LS empuje, 1.00 WA):
#   N   = 0.90·39.1096 + 48.54 + 1.50·6.8532 - 14.1264 = 79.8920
#   H   = 1.50·18.7272 + 1.75·9.2020 + 1.7658 = 45.9601
#   M_e = 0.90·(16.8258 + 27.1411) + 88.020 + 1.50·6.8532·2.40 = 152.2617
#   M_v = 1.50·18.7272·0.91533 + 1.75·9.2020·1.35 + 1.7658·0.20
#         + 14.1264·1.20 = 25.7123 + 21.7397 + 0.3532 + 16.9517 = 64.7569
#   e   = 1.20 - (152.2617 - 64.7569)/79.8920 = 0.10471
CP_T7B_MURO_2 = {
    # Sumas de productos redondeados a cuatro decimales: tolerancia mayor.
    "tolerancia": 3e-3, "tolerancia_K": 1e-6, "tolerancia_fina": 1e-5,
    "tolerancia_e": 1e-4,           # cociente de sumas a cuatro decimales
    "geometria": {"H": 2.0, "B": 2.4, "D_f": 1.0, "espesor_corona": 0.25,
                  "espesor_base_muro": 0.45, "espesor_zapata": 0.40,
                  "ancho_talon": 1.20, "ancho_punta": 0.75},
    "z_rel": 2.40, "subida": 0.30, "talud": 2.0, "NF": 0.40,
    "gamma_saturado": 20.0, "h": 2.70, "i_grados": 3.57633,
    "area_tri": 0.09, "area_rec": 0.18, "K_A": 0.310599,
    "P_A": 19.9418, "z_A": 0.91533,
    "cargas": {   # codigo: (V, H, x, z)
        "DC.pantalla": (16.492, 0.0, 1.02024, 1.30476),
        "DC.zapata": (22.6176, 0.0, 1.20, 0.20),
        "EV.talon": (48.54, 0.0, 1.81335, 1.40),
        "EH.h": (0.0, 18.7272, None, 0.91533),
        "EH.v": (6.8532, 0.0, 2.40, None),
        "LS.h": (0.0, 9.2020, None, 1.35),
        "LS.v": (13.1674, 0.0, 1.80, None),
        "WA.h": (0.0, 1.7658, None, 0.20),
        "WA.u": (-14.1264, 0.0, 1.20, None),
    },
    "resistencia_min": {"N": 79.8920, "H": 45.9601, "M_e": 152.2617,
                        "M_v": 64.7569, "e": 0.10471},
}

# Suelo de fundacion COHESIVO sobre el primer muro (E.050 Art. 20: phi = 0).
# Tabla 10.6.3.1.2a-1 en phi = 0: N_c = 5.14, N_q = 1.0, N_gamma = 0.
#   Deslizamiento LRFD (AASHTO 10.6.3.4, sobre material granular compactado),
#   combinacion de minimos: N = 77.2293, e = 0.14531, B' = 1.70938,
#   sigma_v = 45.1795 kPa, sigma_v/2 = 22.5898 kPa.
#     c = 60 kPa: q_s = min(60, 22.5898) = 22.5898; R_tau = 22.5898·1.70938
#                 = 38.6146; phi_tau = 0.85 -> 32.8224 < 35.4066  NO CUMPLE
#     c = 15 kPa: q_s = 15; R_tau = 15·1.70938 = 25.6407; -> 21.7946
#   Deslizamiento ASD: FS = c·B / H = 15·2.00/22.2997 = 1.3453 (c = 15);
#                      60·2.00/22.2997 = 5.3812 (c = 60)
#   Portante LRFD, c = 60, combinacion de maximos (B' = 1.94694, H de
#   servicio 22.2997): i_c = 1 - 2·22.2997/(60·1.94694·5.14)
#                          = 1 - 44.5994/600.436 = 0.925722
#     q_n = 60·5.14·0.925722 + 18·0.80·1.0 = 285.4927 + 14.4 = 299.8927
#     phi_b = 0.50 -> q_R = 149.9463 kPa (sigma_v = 63.5646)
CP_T7B_COHESIVO = {
    "tolerancia": 3e-3,
    "c_60": {"R_tau": 38.6146, "R_R": 32.8224, "FS_desliz_ASD": 5.3812,
             "i_c": 0.925722, "q_n": 299.8927, "q_R": 149.9463},
    "c_15": {"R_tau": 25.6407, "R_R": 21.7946, "FS_desliz_ASD": 1.3453},
}

# Las solicitaciones de la zapata del primer muro, Resistencia I (maximos):
# N = 123.7564, B' = 1.94694, sigma = 63.5646 kPa; peso propio factorado de
# la zapata 1.25·23.56·0.40 = 11.78 kPa.
#   punta (0.60 m):  V_u = (63.5646 - 11.78)·0.60 = 31.0708
#                    M_u = 63.5646·0.60·0.30 - 11.78·0.60^2/2 = 9.3212
#   talon (1.10 m):  cargas hacia abajo 1.35·39.6 + 1.75·12.0701 + 1.50·5.2958
#                    = 53.460 + 21.1227 + 7.9437 = 82.5264, mas el peso propio
#                    11.78·1.10 = 12.958; la presion alcanza 1.94694 - 0.90
#                    = 1.04694 m del talon: 63.5646·1.04694 = 66.5484
#                    V_u = 82.5264 + 12.958 - 66.5484 = 28.9360
#                    M_u = (53.460 + 21.1227)·0.55 + 7.9437·1.10
#                          + 11.78·1.10^2/2 - 63.5646·1.04694^2/2
#                        = 41.0205 + 8.7381 + 7.1269 - 34.8360 = 22.0495
CP_T7B_SOLICITACIONES = {
    "tolerancia": 3e-3,
    "punta": {"V_u": 31.0708, "M_u": 9.3212},
    "talon": {"V_u": 28.9360, "M_u": 22.0495},
    # Correcciones de T-7c (H1): el diagrama de cada empuje integrado por
    # encima del arranque (dorado a mano en CP_T7C_ARMADO, punto 2, activo).
    # Hasta ahi 35.4066 / 19.6425, con la resultante entera de cada empuje.
    "pantalla": {"V_u": 26.4906, "M_u": 21.4658},
}

# Las filas SISMICAS del primer muro que dependen de CUAL combinacion es la
# peor (k_h = 0.25), a mano:
#   E3-LRFD: caso 1  H = 37.7325, R_tau = 81.6395·0.624869 = 51.0140
#                    (holgura 13.2815)
#            caso 2  H = 36.5315, R_tau = 77.8798·0.624869 = 48.6647
#                    (holgura 12.1332)  <- la peor: es la que se imprime
#   E1-LRFD: la de mayor aprovechamiento es el caso 1 SIN el peso de la
#            sobrecarga: N = 81.6395, e = 0.21561, B' = 2.00 - 0.43122
#            = 1.56878; sigma_v = 81.6395/1.56878 = 52.0401 kPa.
#            Inclinacion con su hermana de servicio (N = 93.7096,
#            H = 41.6467): 1 - H/V = 0.555577; i_q = 0.308666;
#            i_gamma = 0.171488
#            q_n = 18·0.80·23.2·0.308666 + 0.5·18·1.56878·30.2·0.171488
#                = 103.1191 + 73.1220 = 176.2411; phi_b = 0.8 -> 140.9929
#   E2-ASD:  caso 1  M_e/M_v = 104.9811/45.6406 = 2.3002   <- el menor
#            caso 2  97.4616/40.7210 = 2.3934
#   E3-ASD:  caso 1  51.0140/41.6467 = 1.2249
#            caso 2  48.6647/40.4457 = 1.2032              <- el menor
#
# Y el talon del SEGUNDO muro, Resistencia I (maximos), con subpresion:
#   N   = 1.25·39.1096 + 1.35·48.54 + 1.50·6.8532 + 1.75·13.1674 - 14.1264
#       = 48.8870 + 65.5290 + 10.2798 + 23.0430 - 14.1264 = 133.6124
#   M_e = 1.25·43.9669 + 1.35·88.020 + 24.6715 + 1.75·13.1674·1.80
#       = 54.9586 + 118.8270 + 24.6715 + 41.4773 = 239.9344
#   M_v = 64.7569 (los mismos factores que en minimos)
#   e   = 1.20 - 175.1775/133.6124 = -0.11109 (hacia el talon)
#   B'  = 2.40 - 0.22218 = 2.17782; sigma = 133.6124/2.17782 = 61.3514
#   talon: abajo = 65.5290 + 23.0430 + 10.2798 = 98.8518; peso propio
#          11.78·1.20 = 14.136; presion sobre 2.17782 - 1.20 = 0.97782 m:
#          61.3514·0.97782 = 59.9906; subpresion 14.1264·1.20/2.40 = 7.0632
#          V_u = 98.8518 + 14.136 - 59.9906 - 7.0632 = 45.9340
#          M_u = 65.5290·0.61335 + 23.0430·0.60 + 10.2798·1.20
#                + 11.78·1.20^2/2 - 61.3514·0.97782^2/2 - 7.0632·0.60
#              = 40.1922 + 13.8258 + 12.3358 + 8.4816 - 29.3300 - 4.2379
#              = 41.2675
CP_T7B_PEOR_COMBINACION = {
    "tolerancia": 3e-3,
    "E3_LRFD_sis": {"H": 36.5315, "R_R": 48.6647},
    "E1_LRFD_sis": {"sigma_v": 52.0401, "q_R": 140.9929},
    "E2_ASD_sis": 2.3002, "E3_ASD_sis": 1.2032,
    "muro_2_talon_max": {"V_u": 45.9340, "M_u": 41.2675, "tolerancia": 6e-3},
}


# ---------------------------------------------------------------------------
# --- correcciones de T-7b (H4) --- LA CUÑA DE TANTEO (Culmann), A MANO
# ---------------------------------------------------------------------------
# Plano vertical del talon de altura h; la superficie del relleno sube desde
# su tope con 1 V : talud H y se quiebra, `subida` m mas arriba, en una
# plataforma horizontal. La cuña de prueba con el plano de falla a rho sobre
# la horizontal pesa W = gamma·A, y su empuje (k_h = k_v = 0) es
#     P = W·sen(rho - phi) / cos(rho - phi - delta)
# y con k_h (k_v = 0), psi = arctan(k_h):
#     P = W·sen(rho - phi + psi) / [cos(psi)·cos(rho - phi - delta)]
#
# CASO QUEBRADO: h = 2.00, subida = 0.50, talud = 2 (quiebre a x = 1.00 m),
# phi = 30, delta = 20, gamma = 18.
#   rho = 50: tan = 1.191754; sobre el talud x = 2/(1.191754 - 0.5) = 2.891
#             > 1.00 -> corta la plataforma, z = 2.50: x = 2.5/1.191754 =
#             2.097749. A = 0.5·2.5·2.097749 - 0.5·0.5·1.00 = 2.622186 -
#             0.25 = 2.372186 m2; W = 18·2.372186 = 42.69935 kN/m;
#             P = 42.69935·sen 20 / cos 0 = 42.69935·0.342020 = 14.60404
#   rho = 55: tan = 1.428148; x = 2.5/1.428148 = 1.750519; A = 2.188149 -
#             0.25 = 1.938149; W = 34.88667; P = 34.88667·sen 25 / cos 5 =
#             34.88667·0.422618/0.996195 = 14.80006
#   rho = 60: tan = 1.732051; x = 1.443376; A = 1.804220 - 0.25 = 1.554220;
#             W = 27.97595; P = 27.97595·0.5/cos 10 = 13.98798/0.984808 =
#             14.20376
#   rho = 80: tan = 5.671282; sobre el talud x = 2/(5.671282 - 0.5) =
#             0.386751 <= 1.00 -> triangulo, A = 0.5·2·0.386751 = 0.386751;
#             W = 6.96152; P = 6.96152·sen 50 / cos 30 = 6.96152·0.766044/
#             0.866025 = 6.15783
#   Sismo k_h = 0.20 (psi = 11.309932), rho = 50: W = 42.69935;
#             P = 42.69935·sen 31.309932/(cos 11.309932·cos 0) =
#             42.69935·0.519778/0.980581 = 22.62889
#   La cuña critica queda entre 50 y 60 grados y su empuje no baja del de
#   ninguna de las escritas.
#
# LIMITE DE COULOMB (talud sin quiebre, la ec. 3.11.5.3-1 con theta = 90):
# h = 2.00, talud 2 (i = arctan 0.5 = 26.565051), phi = 34, delta = 22.78,
# gamma = 17:
#   sen(phi + delta) = sen 56.78 = 0.836573; sen(phi - i) = sen 7.434949 =
#   0.129400; cos delta = 0.921998; cos i = 0.894427
#   Gamma = [1 + raiz(0.836573·0.129400/(0.921998·0.894427))]² =
#           [1 + raiz(0.131270)]² = 1.362314² = 1.855893
#   K_A = cos² 34 / (Gamma·cos delta) = 0.687303/(1.855893·0.921998) =
#         0.401666;  P_A = 0.5·0.401666·17·2² = 13.65665 kN/m
#
# LIMITE DE MONONOBE-OKABE (relleno horizontal, A11.3.1-1, beta = i = 0):
# h = 2.00, phi = 34, delta = 22.78, gamma = 17, k_h = 0.25, k_v = 0
# (psi = 14.036243):
#   cos²(phi - psi) = cos² 19.963757 = 0.883429; sen(phi + delta) =
#   0.836573; sen(phi - psi) = 0.341426; cos(delta + psi) = cos 36.816243 =
#   0.800562
#   Gamma = [1 + raiz(0.836573·0.341426/0.800562)]² = 2.551412
#   K_AE = 0.883429 / (cos psi·cos(delta + psi)·Gamma) = 0.883429/
#          (0.970143·0.800562·2.551412) = 0.445821
#   P_AE = 0.5·0.445821·17·2² = 15.15792 kN/m
CP_T7B_CUNA = {
    "tolerancia": 1e-4,             # cifras escritas a cinco decimales
    "quebrado": {"h": 2.0, "subida": 0.5, "talud": 2.0, "phi": 30.0,
                 "delta": 20.0, "gamma": 18.0,
                 "P_por_rho": {50.0: 14.60404, 55.0: 14.80006,
                               60.0: 14.20376, 80.0: 6.15783},
                 "k_h": 0.20, "P_sismico_rho_50": 22.62889},
    "coulomb": {"h": 2.0, "talud": 2.0, "phi": 34.0, "delta": 22.78,
                "gamma": 17.0, "K_A": 0.401666, "P_A": 13.65665},
    "mononobe_okabe": {"h": 2.0, "phi": 34.0, "delta": 22.78, "gamma": 17.0,
                       "k_h": 0.25, "K_AE": 0.445821, "P_AE": 15.15792},
    # CONTRASTE: los oraculos del auditor adversarial (su cuña independiente,
    # `aud_T-7b_scripts/cuna.py`) sobre la geometria de A-01 de la FASE A,
    # phi 34, delta 22.78, gamma 17, talud 2. Dos decimales.
    "auditor": {
        "entrada": {"h": 2.477625, "subida": 0.80 - 0.75525 / 2,
                    "P": {0.0: 16.95, 0.25: 30.58, 0.50: 59.73}},
        "salida": {"h": 3.325459, "subida": 0.913216 - 1.077352 / 2,
                   "P": {0.0: 28.61, 0.25: 50.85, 0.50: 98.19}},
    },
}


# ===========================================================================
# --- T-7c --- El armado del cabezal: dorados A MANO, con la aritmetica
# ===========================================================================
# EL MURO es el de tanteo de T-7b (`CP_T7B_ESTABILIDAD`): H = 2.00 m sobre
# una zapata de 0.40 m (h = 2.40 m), pantalla de 0.30 m, punta 0.60 m, talon
# 1.10 m, B = 2.00 m; relleno gamma = 18 kN/m3, phi = 30 grados, delta = 20.1
# grados, horizontal y seco; h_eq = 0.6096 m (2.0 ft). Sus cargas SIN
# FACTORAR son las de aquel dorado: EH.h = 14.4714 kN/m a z = 0.80 m (P_A =
# 0.5·0.297260·18·2.40² = 15.40996, por cos 20.1° = 0.9390943), EH.v = 5.2958
# a x = 2.00, LS.h = 7.8283 a z = 1.20, LS.v = 12.0701 a x = 1.45, EV.talon =
# 39.600 a x = 1.45, DC.pantalla = 14.136 a x = 0.75, DC.zapata = 18.848 a x
# = 1.00 (gamma_c = 23.56 kN/m3).
#
# MATERIALES Y DETALLE (los de archivo): f'c = 21 MPa, fy = 420 MPa (A615
# Grado 60, gamma_3 = 0.67), barra minima principal 1/2" (12.7 mm, 129 mm2).
# Recubrimiento SIN el analisis quimico ni la categoria del acero: la cota
# mas exigente, max(E.060, 3.0 in x 1.2) = 76.2·1.2 = 91.44 mm.
#
# 1. EL EMPUJE EN REPOSO (lo que se escala y lo que no)
#    K0 = 1 - sen 30° = 0.5
#    P_0  = (K0/K_A)·P_A = 0.5·0.5·18·2.40² = 25.92 kN/m, HORIZONTAL, z = 0.80
#    EH.v = 0 (sin friccion muro-relleno)
#    LS_0 = K0·gamma·h_eq·h = 0.5·18·0.6096·2.40 = 13.16736 kN/m, z = 1.20
#    lo demas (DC, EV, LS.v) igual
#
# 2. LA PANTALLA EN SU ARRANQUE, con el diagrama de cada empuje INTEGRADO
#    POR ENCIMA DEL ARRANQUE (correcciones de T-7c, H1): de h = 2.40 m de
#    plano quedan h - e_z = 2.00 m sobre la zapata.
#    suelo, activo: 14.4714·(2.00/2.40)² = 14.4714·0.694444 = 10.04958, a
#      2.00/3 = 0.666667 del arranque -> M 6.69972
#    sobrecarga, activo: 7.8283·(2.00/2.40) = 6.52355, a 1.00 -> M 6.52355
#    activo, Resistencia I (gamma_EH 1.50, gamma_LS 1.75):
#      V_u = 1.50·10.04958 + 1.75·6.52355 = 15.07437 + 11.41621 = 26.49059
#      M_u = 1.50·6.69972 + 1.75·6.52355 = 10.04958 + 11.41621 = 21.46580
#    reposo (K0 = 0.5): 25.92·0.694444 = 18.0 a 0.666667 -> M 12.0;
#      13.16736·(2.00/2.40) = 10.9728 a 1.00 -> M 10.9728
#    reposo, Resistencia I (gamma_EH de la fila «En reposo» 1.35):
#      V_u = 1.35·18.0 + 1.75·10.9728 = 24.3 + 19.2024 = 43.5024
#      M_u = 1.35·12.0 + 1.75·10.9728 = 16.2 + 19.2024 = 35.4024
#    rige (regimen no_cedente_k0): la mayor -> M_u = 35.4024, V_u = 43.5024
#    ANTES de las correcciones (resultante entera de cada empuje con su
#    brazo desde el arranque): activo 35.4066 / 19.6424, reposo 58.03488 /
#    32.431104; el momento quedaba un 8.4 % por debajo (H1).
#
# 3. FLEXION DE LA PANTALLA (AASHTO 5.6.3.2, b = 1000 mm)
#    d = 300 - 91.44 - 12.7/2 = 202.21 mm
#    phi·0.85·f'c·b·d² = 0.9·0.85·21·1000·202.21² = 16065·40888.8841
#                      = 656 879 923 N·mm
#    R = 2·35.4024e6 / 656 879 923 = 0.1077896
#    A_s = (0.85·21/420)·[1 - sqrt(1 - R)]·b·d
#        = 0.0425·(1 - 0.9445689)·202 210 = 0.0425·0.0554311·202 210
#        = 476.4 mm2/m
#    minimo de flexion (5.6.3.3): M_cr = gamma_3·gamma_1·f_r·S
#      f_r = 0.24·sqrt(21/6.894757) ksi = 0.6301889·sqrt(21) = 2.887888 MPa
#      S = 1000·300²/6 = 15.0e6 mm3
#      M_cr = 0.67·1.6·2.887888·15.0e6 = 46.4372e6 N·mm = 46.437 kN·m/m
#      1.33·M_u = 1.33·35.4024 = 47.0852 kN·m/m: ahora M_cr es el menor
#      R = 2·46.4372e6 / 656 879 923 = 0.1413873; sqrt(1 - R) = 0.9266136
#      A_s = 0.0425·0.0733864·202 210 = 630.7 mm2/m
#    retraccion y temperatura (5.10.6), b = 2000 mm (la altura de la
#      pantalla, menor que la longitud de 3.00 m), h = 300 mm:
#      A_s = 0.7469320·2000·300 / [2·(2000 + 300)·420] = 0.7469320·0.3105590
#          = 0.23197 mm2/mm = 232.0 mm2/m, por debajo del piso de 0.11
#          in2/ft = 232.83 mm2/m -> rige el piso: 232.8 mm2/m
#    E.060 14.3.1 vertical: 0.0015·300·1000 / 2 capas = 225 mm2/m
#    adoptado = max(476.4, 630.7, 232.8) = 630.7 mm2/m (minimo de flexion)
#    s maximo = min(1.5·0.30, 0.4572, max(3·0.30, 0.4572), 3·0.30, 0.40)
#             = 0.40 m (E.060 14.3.3)
#    barra: 1/2" a 0.30 -> 430; a 0.25 -> 516; a 0.20 -> 645 >= 630.7
#      -> Ø 1/2" @ 0.20 m, 645 mm2/m (la misma barra que antes de H1)
#    a = 645·420 / (0.85·21·1000) = 270 900 / 17 850 = 15.1765 mm
#    c = a / 0.85 = 17.8547 mm
#    M_n = 645·420·(202.21 - 15.1765/2) = 270 900·194.62176
#        = 52 723 035 N·mm = 52.7230 kN·m/m;  M_r = 0.9·M_n = 47.4507
#    epsilon_t = 0.003·(202.21 - 17.8547)/17.8547 = 0.030976 (>= 0.005)
#
# 4. CORTANTE DE LA PANTALLA (AASHTO 5.7.3.3, simplificado: beta = 2.0;
#    permitido porque h = 0.30 m < 16.0 in = 0.4064 m)
#    letra de 5.7.2.8: max(202.21 - 7.588, 0.9·202.21, 0.72·300) =
#      max(194.62, 181.99, 216.00) = 216.00 mm; ACOTADO al peralte efectivo
#      (correcciones de T-7c, H8): d_v = min(216.00, 202.21) = 202.21 mm
#    en unidades de la fuente: f'c = 21/6.894757 = 3.045793 ksi, sqrt =
#      1.745220; b_v = 39.37008 in, d_v = 202.21/25.4 = 7.961024 in
#      V_c = 0.0316·2.0·1.745220·39.37008·7.961024 = 0.1102979·313.4262
#          = 34.5702 kip = 34.5702·4.4482216 = 153.776 kN/m
#    tope 0.25·f'c·b·d_v = 0.25·21·202 210 = 1061.6 kN/m (no gobierna)
#    V_r = 0.9·153.776 = 138.40 kN/m  >= V_u = 43.50; 0.5·phi·V_c = 69.20
#      > 43.50: A2 CUMPLE sin indicador
#    ANTES (d_v de la letra): V_c 164.264, V_r 147.84
#
# 5. CONTRASTE E.060 DE LA PANTALLA (sus cargas, sus factores; los empujes
#    integrados sobre el arranque, como en el punto 2)
#    (9-6) U = 1,4 CM + 1,7 CV + 1,7 CE, con el empuje en reposo:
#      M_u = 1.7·12.0 + 1.7·10.9728 = 20.4 + 18.65376 = 39.05376 kN·m/m;
#      V_u = 1.7·(18.0 + 10.9728) = 49.25376 kN/m
#    flexion (phi = 0,90, bloque 0,85 f'c): R = 2·39.05376e6 / 656 879 923
#      = 0.1189073; sqrt(1 - R) = 0.9386654
#      A_s = 0.0425·0.0613346·202 210 = 527.1 mm2/m; / 645 = 0.8172
#    cortante: phi·V_c = 0,85·0,17·sqrt(21)·1000·202.21
#      = 0.1445·4.5825757·202 210 = 133.90 kN/m; 49.25376/133.90 = 0.3678
#    aprovechamiento = max(0.8172, 0.3678) = 0.8172
#
# 5b. SERVICIO I DE LA PANTALLA (AASHTO 5.6.7; correcciones de T-7c, H3),
#    todas las cargas con 1.00 y el mismo regimen: activo 6.69972 + 6.52355
#    = 13.22327; reposo 12.0 + 10.9728 = 22.9728 -> M_s = 22.9728 kN·m/m
#    traccion bruta = 22.9728 / (0.30²/6) = 1531.5 kPa = 1.5315 MPa
#    0.8·f_r = 0.8·2.887888 = 2.3103 MPa > 1.5315: 5.6.7 NO aplica
#
# 6. LA ZAPATA (presion de contacto LINEAL, AASHTO 10.6.5)
#    punta, Resistencia I (minimos) con el empuje en reposo (DC 0.90, EV
#    1.00, EH 1.35, LS 1.75 sin su peso):
#      N   = 0.90·(14.136 + 18.848) + 39.600 = 29.6856 + 39.6 = 69.2856
#      M_e = 0.90·(14.136·0.75 + 18.848·1.00) + 39.600·1.45
#          = 26.505 + 57.42 = 83.925
#      M_v = 1.35·25.92·0.80 + 1.75·13.16736·1.20 = 27.9936 + 27.651456
#          = 55.645056
#      x   = (83.925 - 55.645056)/69.2856 = 0.408165 m; e = 0.591835 > B/6
#      triangulo desde la punta: largo 3·0.408165 = 1.224496 m,
#        sigma = 2·69.2856/1.224496 = 113.1659 kPa en la punta y
#        113.1659·(1 - 0.60/1.224496) = 57.7149 kPa en la cara
#      F = (113.1659 + 57.7149)/2·0.60 = 51.26424; su centro a
#        0.60·(113.1659 + 2·57.7149)/(3·170.8808) = 0.267549 m de la punta,
#        a 0.332451 m de la cara: M = 17.04285
#      peso propio: 0.90·23.56·0.40 = 8.4816 kN/m2 -> V 5.08896, M 1.526688
#      V_u = 51.26424 - 5.08896 = 46.1753;  M_u = 17.04285 - 1.52669 = 15.5162
#    talon con el PESO ENTERO (AASHTO 11.6.1.2), Resistencia I (maximos),
#    activo (brazos desde la cara de la pantalla, x = 0.90 m):
#      V_u = 1.35·39.600 + 1.75·12.0701 + 1.50·5.2958 + 1.25·23.56·0.40·1.10
#          = 53.46 + 21.122675 + 7.9437 + 12.958 = 95.4844
#      M_u = 53.46·0.55 + 21.122675·0.55 + 7.9437·1.10 + 11.78·1.10²/2
#          = 29.403 + 11.617471 + 8.73807 + 7.1269 = 56.8854
#
# 7. EVENTO EXTREMO I, caso 100 % P_AE + 50 % P_IR (k_h = k_h0 = 0.25):
#    cargas del dorado sismico de T-7b (incremento 10.2740 a z = 1.44 =
#    0.6·h), gamma_EQ = 0.5, phi = 1.0, integradas sobre el arranque (H1):
#      suelo 10.04958 a 0.666667 -> 6.69972 (punto 2)
#      incremento: el diagrama LINEAL con la resultante a 0.6·h tiene en la
#        base 2·10.2740/2.40·(2 - 1.8) = 1.712333 kPa y en la corona
#        2·10.2740/2.40·(1.8 - 1) = 6.849333 kPa; en el arranque (z = 0.40)
#        1.712333 + 5.137·0.40/2.40 = 2.568500; sobre el arranque:
#        F = (2.568500 + 6.849333)/2·2.00 = 9.417833, a
#        2.00·(2.568500 + 2·6.849333)/[3·(2.568500 + 6.849333)] = 1.151515
#        -> M 10.844778
#      sobrecarga 0.5·6.52355 = 3.26177 a 1.00
#      inercia de la PANTALLA sola: 0.5·0.25·14.136 = 1.767 a 1.00
#      en su posicion: V = 10.04958 + 9.417833 + 3.26177 + 1.767 = 24.49619
#                      M = 6.69972 + 10.844778 + 3.26177 + 1.767 = 22.57327
#      con la resultante total a h/2 (C11.6.5.4: diagrama uniforme):
#        (14.4714 + 10.2740)·2.00/2.40 = 20.62117 a 1.00
#        V = M = 20.62117 + 3.26177 + 1.767 = 25.64994  <- rige
#    caso 50 % P_AE + 100 % P_IR (rige el piso estatico: EH 1, incremento
#    0, inercia 1): en su posicion V = 10.04958 + 3.26177 + 3.534 = 16.84536,
#    M = 6.69972 + 3.26177 + 3.534 = 13.49550; a h/2: 14.4714·2.00/2.40 =
#    12.05950 -> V = M = 12.05950 + 3.26177 + 3.534 = 18.85528
#    ANTES (resultante entera, inercia del muro y de la zapata): 20.9007 en
#    su posicion y 24.2235 a h/2
CP_T7C_ARMADO = {
    # Tolerancias de la ESCRITURA del dorado, no de la maquina.
    "tolerancia": 2e-3,             # cifras escritas a tres o cuatro decimales
    "tolerancia_As": 0.2,           # mm2/m: areas escritas a un decimal
    "tolerancia_rel": 2e-4,
    "tolerancia_cm": 1e-2,          # cifras escritas a dos decimales
    "tolerancia_mm": 1e-3,          # cifras escritas a tres decimales
    "tolerancia_fina": 1e-5,        # deformaciones y cocientes a cinco
    "tolerancia_K": 1e-6,           # coeficientes y constantes a seis
    # Lo que sale de una o dos operaciones sobre datos exactos (un espesor
    # menos un recubrimiento, un area entre un espaciamiento): absoluta para
    # longitudes y areas, relativa para lo que se reproduce con otra formula.
    "tolerancia_exacta": 1e-9,
    "tolerancia_calculo_rel": 1e-9,
    "tolerancia_unidades_rel": 1e-5,    # ida y vuelta por unidades inglesas
    "K0": 0.5,
    "reposo": {"EH_h": 25.92, "EH_v": 0.0, "LS_h": 13.16736},
    "pantalla": {
        "activo": {"V_u": 26.49059, "M_u": 21.46580},
        "reposo": {"V_u": 43.5024, "M_u": 35.4024},
        "recubrimiento_mm": 91.44, "d_m": 0.20221,
        "As_resistencia": 476.4, "M_cr": 46.437, "As_minimo_flexion": 630.7,
        "As_temperatura": 232.8, "As_e060": 225.0, "s_max": 0.40,
        "barra": ("1/2", 0.20, 645.0),
        "a_mm": 15.1765, "M_n": 52.7230, "M_r": 47.4507,
        "epsilon_t": 0.030976,
        "d_v_m": 0.20221, "d_v_letra_m": 0.216, "V_c": 153.776,
        "V_r": 138.40, "media_phi_Vc": 69.20,
        "sismico": {"en_su_posicion": 22.57327, "a_media_altura": 25.64994,
                    "V_en_su_posicion": 24.49619,
                    "incremento_sobre_el_arranque": 9.417833,
                    "brazo_del_incremento": 1.151515,
                    "caso_2": {"en_su_posicion": 13.49550,
                               "a_media_altura": 18.85528}},
        "servicio": {"activo": 13.22327, "reposo": 22.9728,
                     "f_t_MPa": 1.5315, "umbral_MPa": 2.3103},
    },
    "e060_pantalla": {"M_u": 39.05376, "V_u": 49.25376, "As": 527.1,
                      "phi_Vc": 133.90, "aprovechamiento": 0.8172,
                      "tolerancia_uso": 5e-4, "tolerancia_V": 0.02},
    "punta": {"N": 69.2856, "e": 0.591835, "sigma": 113.1659,
              "V_u": 46.1753, "M_u": 15.5162},
    "talon": {"V_u": 95.4844, "M_u": 56.8854},
}

# LA ECUACION (11-32) DE E.060 11.10.10.3, a mano, con sus dos topes:
#   rho_v = 0,0025 + 0,5·(2,5 - hm/lm)·(rho_h - 0,0025), >= 0,0025 y <= rho_h
#   hm/lm = 2.4/3.0 = 0.8, rho_h = 0.0040: 0.0025 + 0.5·1.7·0.0015 = 0.003775
#   hm/lm = 1.0/5.0 = 0.2, rho_h = 0.0040: 0.0025 + 0.5·2.3·0.0015 = 0.004225
#       -> no necesita superar rho_h: 0.0040
#   hm/lm = 6.0/2.0 = 3.0, rho_h = 0.0040: 0.0025 - 0.5·0.5·0.0015 = 0.002125
#       -> piso: 0.0025
#   con rho_h = 0.0025 (el piso horizontal) da 0.0025 para cualquier hm/lm
CP_T7C_EC_11_32 = (
    # (hm, lm, rho_h, rho_v)
    (2.4, 3.0, 0.0040, 0.003775),
    (1.0, 5.0, 0.0040, 0.0040),
    (6.0, 2.0, 0.0040, 0.0025),
    (2.4, 3.0, 0.0025, 0.0025),
    (6.0, 2.0, 0.0025, 0.0025),
)

# EL ACERO DE RETRACCION Y TEMPERATURA DE AASHTO 5.10.6, contra los tres
# ejemplos que su comentario C5.10.6 PUBLICA (pag. impresa 5-174, PDF 533),
# con fy = 60 ksi = 413.685 MPa: «a 30.0 ft high × 1.0 ft thick wall section
# requires 0.126 in.2/ft ...; a 4.0 ft × 4.0 ft component requires 0.260
# in.2/ft ...; and a 5.0 ft × 20.0 ft footing requires 0.520 in.2/ft».
# 1 in2/ft = 645.16 mm2 / 0.3048 m = 2116.667 mm2/m.
CP_T7C_TEMPERATURA_PUBLICADA = {
    "fy_mpa": 413.685438,
    "tolerancia_in2_ft": 5e-4,      # el ejemplo se publica a tres decimales
    "casos": (   # (ancho m, espesor m, in2/ft publicado)
        (9.144, 0.3048, 0.126),
        (1.2192, 1.2192, 0.260),
        (6.096, 1.524, 0.520),
    ),
}

# EL CABEZAL DE GRAVEDAD EN CICLOPEO, a mano. Cuerpo H = 1.30 m, de 0.30 m
# en la corona a 0.50 m en el arranque (trasdos vertical), sobre una zapata
# de 0.30 m; relleno horizontal y seco hasta la corona (h = 1.60 m: sobre el
# 1.524 m de la primera fila de la tabla de h_eq), gamma = 18, phi = 30
# grados (K0 = 0.5; K_A = 0.297260 con delta = 20.1 grados), h_eq = 0.6096
# m, gamma_c = 23.56 kN/m3.
#   ARRANQUE DEL CUERPO (z = 0.30 m; 1.30 m de muro y de diagrama encima)
#     t = 0.50; W = 23.56·(0.50 + 0.30)/2·1.30 = 12.2512 kN/m
#     x_W = (0.50² + 0.50·0.30 + 0.30²)/(3·0.80) = 0.49/2.40 = 0.2041667 m
#     reposo: suelo 0.5·18·1.30²/2 = 7.605 a 0.433333 -> 3.2955; sobrecarga
#       0.5·18·0.6096·1.30 = 7.13232 a 0.65 -> 4.636008; M_H = 7.931508
#       e = [7.931508 - 12.2512·(0.25 - 0.2041667)]/12.2512
#         = (7.931508 - 0.561513)/12.2512 = 0.601573 m   (t/6 = 0.08333)
#     activo: suelo 0.297260·18·1.69/2·cos 20.1° = 4.521325·0.9390943 =
#       4.245950 a 0.433333 -> 1.839912; sobrecarga 0.297260·18·0.6096·1.30
#       = 4.240307 a 0.65 -> 2.756200; M_H = 4.596112
#       e = (4.596112 - 0.561513)/12.2512 = 0.329323 m
#     rige el reposo: e = 0.601573 > t/6 -> hay traccion
#   MEDIA ALTURA (z = 0.95 m; 0.65 m encima): t = 0.40; W = 23.56·0.35·0.65
#     = 5.3599; x_W = (0.16 + 0.12 + 0.09)/(3·0.70) = 0.1761905
#     reposo: 0.5·18·0.65²/2 = 1.90125 a 0.216667 -> 0.411938;
#       0.5·18·0.6096·0.65 = 3.56616 a 0.325 -> 1.159002; M_H = 1.570940
#       e = [1.570940 - 5.3599·(0.20 - 0.1761905)]/5.3599 = 0.269282 m
#   CONTRASTE E.060 (22.5.3 y 22.5.4; phi = 0,5; f'c = 10 MPa; h - 50 mm;
#     cargas 0,9 CM + 1,7 CE), arranque en reposo: t = 0.45 m
#     P_u = 0.9·12.2512 = 11.02608; M_u = 1.7·3.2955 + 1.7·4.636008
#       - 11.02608·0.0458333 = 5.60235 + 7.881214 - 0.505362 = 12.978202
#     traccion = 12.978202/(0.45²/6) - 11.02608/0.45 = 384.5393 - 24.5024
#       = 360.0369 kPa; admisible 0.5·0.42·sqrt(10)·1000 = 664.078 kPa
#       -> 0.54216
#     cortante: 1.7·(7.605 + 7.13232) = 25.053444 kN/m; resistencia
#       0.5·0.11·sqrt(10)·1000·0.45 = 78.2664 kN/m -> 0.32011
#     media altura (t = 0.35): 0.16775 y 0.15269: rige el arranque, 0.54216
#   22.6.3 (correcciones de T-7c, H5): el momento no baja de P_u·0,10·t =
#     11.02608·0.10·0.50 = 0.5513 kN·m/m, muy por debajo de 12.978: no rige.
#   C2 EN LA JUNTA DE CONSTRUCCION (E.060 22.4.7; correcciones de T-7c, H5):
#     ademas de la de servicio, la excentricidad con las cargas amplificadas
#     de E.060 respecto del centro de la seccion, e_u = M_u / P_u:
#     reposo  e_u = 12.978202 / 11.02608 = 1.177046 m
#     activo  M_u = 1.7·1.839912 + 1.7·2.756200 - 0.505362 = 7.308028;
#             e_u = 7.308028 / 11.02608 = 0.662795 m
#     C2 = max(0.601573, 1.177046) = 1.177046 m frente a t/6 = 0.08333
CP_T7C_CICLOPEO = {
    "geometria": {"H": 1.30, "B": 1.00, "D_f": 0.80, "espesor_corona": 0.30,
                  "espesor_base_muro": 0.50, "espesor_zapata": 0.30,
                  "ancho_talon": 0.20, "ancho_punta": 0.30},
    "h": 1.60, "tolerancia": 2e-4,
    "arranque": {"z": 0.30, "t": 0.50, "W": 12.2512, "x_W": 0.2041667,
                 "M_H_reposo": 7.931508, "e_reposo": 0.601573,
                 "M_H_activo": 4.596112, "e_activo": 0.329323},
    "media": {"z": 0.95, "t": 0.40, "W": 5.3599, "x_W": 0.1761905,
              "M_H_reposo": 1.570940, "e_reposo": 0.269282},
    "e060": {"aprovechamiento": 0.54216, "tolerancia": 5e-4},
    "junta": {"e_u_reposo": 1.177046, "e_u_activo": 0.662795},
}

# LA BASE del muro de tanteo de T-7b con cargas de SERVICIO (factor 1), para
# la fila C1 (e <= B/6 = 0.33333 m), a mano:
#   activo, sin el peso de la sobrecarga: N = 14.136 + 18.848 + 39.6 + 5.2958
#     = 77.8798; M_e = 10.602 + 18.848 + 57.42 + 10.5916 = 97.4616; M_v =
#     14.4714·0.80 + 7.8283·1.20 = 20.97108; e = 1 - 76.49052/77.8798 = 0.01784
#   reposo, sin el peso de la sobrecarga: N = 72.584; M_e = 86.87; M_v =
#     25.92·0.80 + 13.16736·1.20 = 36.536832; e = 1 - 50.333168/72.584
#     = 0.306553   <- la mayor
#   reposo, con el peso de la sobrecarga: N = 84.6541; M_e = 104.371645;
#     e = 1 - 67.834813/84.6541 = 0.198682
CP_T7C_BASE_SERVICIO = {"e": 0.306553, "limite": 2.0 / 6.0,
                        "e_activo": 0.044939, "tolerancia": 2e-5}
