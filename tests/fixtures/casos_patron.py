"""
tests/fixtures/casos_patron.py
===============================
Casos de referencia con valores calculados a mano (fuera del pipeline, con
scipy.optimize.brentq de forma independiente) para contrastar cada módulo.

Uso previsto en los módulos de prueba:

    from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING

    def test_geometria_circular():
        c = CP2_GEOMETRIA_MANNING
        theta = resolver_theta(c["D"], c["y_sobre_D"])
        assert theta == pytest.approx(c["theta_esperado"], rel=1e-5)
        ...

Todos los valores numéricos fueron verificados con scipy.optimize.brentq de
forma independiente al pipeline (no se copiaron de la hoja de ruta sin
recalcular). Si un test contra estos valores falla, el error está en el
modulo bajo prueba, no en el fixture -- pero si tienes dudas, recalcula.

Referencias de numeral: ver docs/hoja_de_ruta_alcantarillas_v8.md
"""

import math

G = 9.81  # m/s2, gravedad fisica generica (constantes_fisicas.G). CP-8 usa
          # esta, no G_LAUSHEY = 9.8 (esa es solo para Sec. 4.1.1.3.7 c) en M6).


# ---------------------------------------------------------------------------
# CP-1 · Periodo de retorno (Sec. 2.2, Tabla N 02)
# ---------------------------------------------------------------------------
# TR = 1 / (1 - (1-R)**(1/n))

CP1_PERIODO_RETORNO = [
    {
        "descripcion": "Quebradas importantes / badenes",
        "R": 0.30,
        "n": 25,
        "TR_esperado": 70.63,   # redondea a 71 en la memoria
        "tolerancia": 0.05,
    },
    {
        "descripcion": "Quebradas menores / descarga de cunetas",
        "R": 0.35,
        "n": 15,
        "TR_esperado": 35.29,   # redondea a 35 en la memoria
        "tolerancia": 0.05,
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
    "conclusion": "V2 se cumple para cualquier S >= 0.001; nunca gobierna el diseno",
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
}


# ---------------------------------------------------------------------------
# CP-8 · Constante del control de salida -- SI vs. imperial (Sec. 4.3)
# ---------------------------------------------------------------------------
# H = (1 + ke + K_friccion*n^2*L/R^(4/3)) * V^2/(2g)
# K_friccion = 19.63 en SI. Usar 29 (valor ingles) es el error clasico.
#
# El 19.63 es la conversion SI que el propio HDS-5 declara para su K = 29.
# Sustituye al 19.62 que este fixture uso hasta ahora, justificado entonces
# como "2*g": esa derivacion era una coincidencia numerica sin respaldo en la
# fuente primaria y se retiro. Los valores dorados de abajo estan recalculados
# con 19.63; el cambio mueve H en 5e-5 m, tres ordenes por debajo del salto
# que este caso patron existe para atrapar.

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
# Indice para iterar todos los casos desde un solo import
# ---------------------------------------------------------------------------

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
}


if __name__ == "__main__":
    # Recalculo independiente de verificacion, usa scipy si esta disponible.
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
