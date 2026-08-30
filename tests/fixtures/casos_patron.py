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

# Caso adicional para las ramas puras, con el mismo D:
CP5B_NO_SUMERGIDO = {"D": 0.90, "Q": 0.8998, "q_estrella_aprox": 2.70, "zona": "no_sumergido"}
CP5C_SUMERGIDO = {"D": 0.90, "Q": 1.3997, "q_estrella_aprox": 4.20, "zona": "sumergido"}


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

