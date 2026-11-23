# -*- coding: utf-8 -*-
"""
M9_cabezal.armado_secciones
===========================
Submodulo de Fase 9 (`M9_cabezal`): bloque `armado_secciones` (D1).
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from dataclasses import replace as _reemplazar
from src import criterios_adoptados as ca
from src.constantes_fisicas import (
    GAMMA_AGUA_KN_M3,
    KPA_POR_MPA,
    N_POR_KN,
    PULGADA_EN_MM,
)
from src.constantes_normativas import (
    ALFA_1_BLOQUE_AASHTO,
    ALFA_BLOQUE_E060,
    ALTURA_VOLADIZO_ACTIVO_M,
    BETA_1_BLOQUE_AASHTO,
    BETA_1_E060,
    BETA_1_E060_MINIMO,
    BETA_1_MINIMO,
    BETA_1_REDUCCION_AASHTO_SI,
    CUANTIA_MIN_CARA_TRACCION_E060,
    CUANTIA_MIN_LOSA_E060,
    DV_PISO_SOBRE_DE,
    DV_PISO_SOBRE_H,
    E060_FACTOR_CE,
    E060_FACTOR_CM,
    E060_FACTOR_CM_MINIMO,
    E060_FACTOR_CV,
    EC_11_32_ESBELTEZ,
    EC_11_32_FACTOR,
    EC_COEFICIENTE_AASHTO_SI,
    EC_EXPONENTE_AASHTO,
    EPSILON_CU_CONCRETO,
    EPSILON_TL_AASHTO,
    EPSILON_T_MIN_E060,
    ESPACIAMIENTO_MAX_ABSOLUTO_AASHTO_M,
    ESPACIAMIENTO_MAX_VECES_ESPESOR_AASHTO,
    ES_REFUERZO_AASHTO_MPA,
    FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO,
    FC_BETA_1_E060_MPA,
    FC_MAX_ALFA_1_MPA,
    FC_MAX_BETA_1_MPA,
    FISURACION_BETA_S_FACTOR,
    FISURACION_COEFICIENTE_AASHTO_SI,
    FISURACION_FRACCION_FR,
    FISURACION_FSS_MAX_SOBRE_FY,
    FISURACION_GAMMA_E,
    FY_ACERO_MPA,
    FY_MAX_EPSILON_TL_MPA,
    GAMMA_1_AGRIETAMIENTO_AASHTO,
    GAMMA_3_AASHTO,
    GENERAL_BETA_COEF_DEFORMACION,
    GENERAL_BETA_NUMERADOR,
    GENERAL_BETA_NUMERADOR_SXE_IN,
    GENERAL_BETA_SUMANDO_SXE_IN,
    MODULO_ROTURA_AASHTO_SI,
    NUCLEO_CENTRAL_DIVISOR,
    PERALTE_MAX_SIMPLIFICADO_AASHTO_SI,
    PHI_CORTE_E060,
    PHI_FLEXION_E060,
    REGIMEN_CORTANTE_EN_EL_PLANO,
    SXE_FACTOR_AGREGADO,
    SXE_MAX_IN,
    SXE_MIN_IN,
    SXE_SUMANDO_AGREGADO_IN,
    TABLA_GAMMA_P_FILAS,
    TEMPERATURA_AS_MAX_AASHTO_SI,
    TEMPERATURA_AS_MIN_AASHTO_SI,
    TEMPERATURA_COEFICIENTE_AASHTO_SI,
    TEMPERATURA_ESPESOR_GRUESO_M,
    TEMPERATURA_S_MAX_GRUESO_M,
    TEMPERATURA_S_PISO_M,
    TEMPERATURA_S_VECES_ESPESOR,
    VC_COEFICIENTE_AASHTO_SI,
    VC_COEFICIENTE_E060,
    VN_TOPE_SOBRE_FC_AASHTO,
    ZAPATA_SIMPLIFICADO_VECES_DV,
)
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (
    ArmadoDeSeccion,
    BarraPropuesta,
    CIFRAS_FACTOR,
    CIFRAS_FINA,
    CIFRAS_MAGNITUD,
    CLASES_DE_EXPOSICION,
    CLASE_EXPOSICION_1,
    CLASE_EXPOSICION_2,
    CombinacionDeEstabilidad,
    CondicionAnalisis,
    CriterioPendienteError,
    DatoFaltanteError,
    DatoInvalidoError,
    ELEMENTO_ALEROS,
    ELEMENTO_PANTALLA,
    ELEMENTO_ZAPATA,
    EntornoDelCabezal,
    ErrorProyecto,
    GeometriaCabezal,
    LimiteNumericoError,
    MARCO_ASD,
    MARCO_E060,
    MARCO_LRFD,
    MINIMOS_MAS_EXIGENTE,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL,
    Magnitud,
    MetodoNoEvaluableError,
    REGIMENES_DE_RESISTENCIA,
    REGIMEN_RESISTENCIA_CEDENTE,
    REGIMEN_RESISTENCIA_K0,
    REGLAS_DE_MINIMOS,
    SECCION_ALERO,
    SECCION_PANTALLA,
    SECCION_PUNTA,
    SECCION_TALON,
    SolicitacionDeArmado,
    SolicitacionDeElemento,
    TipoDeVeredicto,
    Umbral,
    Veredicto,
    Verificacion,
    paso,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CONDICION_RECUBRIMIENTO_ZAPATA,
    CRITERIO_CATALOGO_BARRAS,
    CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO,
    CRITERIO_FACTOR_MURO,
    CRITERIO_FLEXION_CORTE,
    CRITERIO_REGIMEN_CORTANTE,
    CRITERIO_REGIMEN_RESISTENCIA,
    FILA_EH_EN_REPOSO,
    LADOS_DEL_TRIANGULO,
    _caracter_de,
    _finito,
    catalogo_de_barras,
)
from src.modulos.M9_cabezal.durabilidad import (
    _minimo_de_cuantia_aplicable,
    espaciamiento_maximo,
    recubrimiento_para_armar,
    requiere_refuerzo_dos_capas,
)
from src.modulos.M9_cabezal.empujes import cadena_sismica
from src.modulos.M9_cabezal.estabilidad import (
    _carga_lineal_sobre_un_tramo,
    empujes_sobre_el_arranque,
    solicitaciones_por_elemento,
)
from src.modulos.M9_cabezal.estabilidad_base import factores_de_carga
from src.modulos.M9_cabezal.estabilidad_cargas import (
    CITAS_ARMADO_CON_EMPUJE_DECLARADO,
    CRITERIO_MOMENTO_TALON,
    CRITERIO_REGIMEN,
    C_DC_ZAPATA,
    C_EH_H,
    C_EH_V,
    C_EQ_H,
    C_EQ_KV,
    C_EQ_V,
    C_EV_TALON,
    C_LS_H,
    C_LS_V,
    C_WA_U,
    NOTA_ARMADO_CON_EMPUJE_DECLARADO,
    REGIMEN_NO_CEDENTE,
    TALON_EXACTO,
    TALON_PESO_ENTERO,
    _combinar,
    _eleccion,
    _resistencia_i_con_eta,
    cargas_del_cabezal,
    combinaciones_de_estabilidad,
)

CRITERIO_FC_CABEZAL = "fc_cabezal_mpa"


CRITERIO_ACERO_CABEZAL = "acero_refuerzo_cabezal"


CRITERIO_REGLA_MINIMOS = "regla_minimos_constructivos_cabezal"


CRITERIO_TRACCION_CICLOPEO = "criterio_traccion_cabezal_ciclopeo"


CRITERIO_CONCRETO_CICLOPEO = "concreto_ciclopeo_cabezal"


CRITERIO_CLASE_EXPOSICION = "clase_exposicion_fisuracion_cabezal"


CRITERIO_JUNTA_CICLOPEO = "junta_arranque_cabezal_ciclopeo"


JUNTA_DE_CONSTRUCCION = "junta_de_construccion"


JUNTA_MONOLITICA = "vaciado_monolitico"


JUNTAS_DEL_ARRANQUE = (JUNTA_DE_CONSTRUCCION, JUNTA_MONOLITICA)


NUMERAL_9_4_ARMADO = ("Sec. 9.4, armado (AASHTO LRFD Seccion 5; E.060 de "
                      "contraste, por analogia)")


NUMERAL_9_4_CICLOPEO = ("Sec. 9.4, alternativa ciclopea (E.060 Cap. 22 por "
                        "analogia; EG-2013 Tabla 503-07)")


MM2_POR_M2 = MILIMETROS_POR_METRO ** 2


# Condiciones del Art. 7.7.1 de E.060 que el armado empareja con cada cara.
CONDICION_RECUBRIMIENTO_BARRA_GRUESA = "suelo_intemperie_ge_3_4"


CONDICION_RECUBRIMIENTO_BARRA_FINA = "suelo_intemperie_le_5_8"


def _aviso_cabezal(entorno: EntornoDelCabezal) -> str:
    return f"Cabezal de {entorno.extremo} de {entorno.id_punto}"


# ---------------------------------------------------------------------------
# Materiales, regimen y regla de minimos
# ---------------------------------------------------------------------------

def materiales_del_armado() -> dict:
    """
    El concreto y el acero con que se arma el cabezal: f'c ('fc_cabezal_mpa'
    [A]) y la designacion del acero ('acero_refuerzo_cabezal' [A]), de la
    que salen fy y el gamma_3 de AASHTO 5.6.3.3 (`FY_ACERO_MPA`,
    `GAMMA_3_AASHTO`). Guardias de segunda linea con la forma MAT-D13: el
    bloque rectangular de 5.6.2.2 con alfa_1 = 0.85 vale hasta 10.0 ksi y el
    limite de traccion de 5.6.2.1 hasta 75.0 ksi.
    """
    fc = ca.valor(CRITERIO_FC_CABEZAL)
    if not (_finito(fc) and 0 < fc <= FC_MAX_ALFA_1_MPA):
        raise DatoInvalidoError(
            CRITERIO_FC_CABEZAL, valor=fc,
            motivo=f"f'c positivo y no mayor que {FC_MAX_ALFA_1_MPA:.1f} MPa "
                   "(10.0 ksi): por encima el factor alfa_1 del bloque de "
                   "AASHTO 5.6.2.2 deja de ser 0.85")
    acero = ca.valor(CRITERIO_ACERO_CABEZAL)
    if acero not in FY_ACERO_MPA or acero not in GAMMA_3_AASHTO:
        raise DatoInvalidoError(
            CRITERIO_ACERO_CABEZAL, valor=acero,
            motivo="se espera una de: " + ", ".join(sorted(FY_ACERO_MPA)))
    fy = FY_ACERO_MPA[acero]
    if not 0 < fy <= FY_MAX_EPSILON_TL_MPA:
        raise DatoInvalidoError(
            CRITERIO_ACERO_CABEZAL, valor=fy,
            motivo="fluencia fuera del dominio del limite de traccion de "
                   "AASHTO 5.6.2.1 (hasta 75.0 ksi)")
    return {"fc": float(fc), "fy": float(fy), "acero": acero,
            "gamma_3": GAMMA_3_AASHTO[acero]}


def regimen_de_resistencia() -> str:
    regimen = ca.valor(CRITERIO_REGIMEN_RESISTENCIA)
    if regimen not in REGIMENES_DE_RESISTENCIA:
        raise DatoInvalidoError(
            CRITERIO_REGIMEN_RESISTENCIA, valor=regimen,
            motivo="se espera una de: " + ", ".join(REGIMENES_DE_RESISTENCIA))
    return regimen


def _regla_de_minimos() -> str:
    regla = ca.valor(CRITERIO_REGLA_MINIMOS)
    if regla not in REGLAS_DE_MINIMOS:
        raise DatoInvalidoError(
            CRITERIO_REGLA_MINIMOS, valor=regla,
            motivo="se espera una de: " + ", ".join(REGLAS_DE_MINIMOS))
    return regla


def _procedimiento() -> dict:
    """Los factores de resistencia y el beta del simplificado, del criterio."""
    p = ca.valor(CRITERIO_FLEXION_CORTE)
    for clave in ("phi_flexion", "phi_corte", "phi_evento_extremo",
                  "beta_simplificado"):
        x = p.get(clave) if hasattr(p, "get") else None
        if not (_finito(x) and x > 0):
            raise DatoInvalidoError(
                CRITERIO_FLEXION_CORTE, valor=x,
                motivo=f"falta el campo '{clave}', positivo, del "
                       "procedimiento de flexion y corte")
    return p


# ---------------------------------------------------------------------------
# Las formulas de seccion: AASHTO LRFD 5.6 y 5.7, por metro de ancho
# ---------------------------------------------------------------------------

def beta_1_aashto(fc: float) -> float:
    """beta_1 del bloque rectangular, AASHTO 5.6.2.2 (f'c en MPa)."""
    exceso = max(fc - FC_MAX_BETA_1_MPA, 0.0)
    return max(BETA_1_BLOQUE_AASHTO - BETA_1_REDUCCION_AASHTO_SI * exceso,
               BETA_1_MINIMO)


def beta_1_e060(fc: float) -> float:
    """beta_1 de E.060 10.2.7.3 (f'c en MPa)."""
    bajo, alto = FC_BETA_1_E060_MPA
    if fc <= bajo:
        return BETA_1_E060
    if fc >= alto:
        return BETA_1_E060_MINIMO
    return BETA_1_E060 - (BETA_1_E060 - BETA_1_E060_MINIMO) * (
        (fc - bajo) / (alto - bajo))


def _exigir_seccion(d: float, fc: float, fy: float) -> None:
    for nombre, x in (("d", d), ("f'c", fc), ("fy", fy)):
        if not (_finito(x) and x > 0):
            raise DatoInvalidoError(
                nombre, valor=x,
                motivo="la seccion de concreto armado necesita peralte "
                       "efectivo, f'c y fy positivos y finitos")


def acero_por_flexion(*, M_u: float, d: float, fc: float, fy: float,
                      phi: float, alfa: float = ALFA_1_BLOQUE_AASHTO
                      ) -> Optional[float]:
    """
    Area de acero en traccion, mm2 por metro de ancho, con que una seccion
    rectangular de peralte efectivo `d` (m) desarrolla phi·M_n = M_u (kN·m/m)
    con el bloque rectangular de compresiones (AASHTO 5.6.3.2 con 5.6.2.2;
    con `alfa` = 0,85 y phi de 9.3.2.1 es la de E.060 10.2.7):

        M_u = phi·A_s·f_y·(d - a/2),   a = A_s·f_y / (alfa·f'c·b)

    de donde, con R = 2·M_u / (phi·alfa·f'c·b·d²):

        A_s = (alfa·f'c / f_y)·[1 - sqrt(1 - R)]·b·d

    Devuelve None cuando R >= 1: el momento supera lo que el bloque puede dar
    con cualquier cantidad de acero, y la seccion no alcanza. Con M_u <= 0
    no hay traccion que armar y devuelve 0.
    """
    _exigir_seccion(d, fc, fy)
    if not _finito(M_u):
        raise LimiteNumericoError("M_u", valor=M_u,
                                  motivo="el momento factorado no es finito")
    if not (_finito(phi) and phi > 0):
        raise DatoInvalidoError("phi", valor=phi,
                                motivo="factor de resistencia positivo")
    if M_u <= 0:
        return 0.0
    R = 2 * M_u / (phi * alfa * fc * KPA_POR_MPA * d ** 2)
    if not R < 1:
        return None
    return alfa * fc / fy * (1 - math.sqrt(1 - R)) * d * MM2_POR_M2


def resistencia_a_flexion(*, As: float, d: float, fc: float, fy: float,
                          alfa: float = ALFA_1_BLOQUE_AASHTO,
                          beta_1: Optional[float] = None) -> dict:
    """
    La resistencia NOMINAL a flexion de la seccion rectangular con `As`
    (mm2/m) a un peralte efectivo `d` (m), y la deformacion neta del acero
    (AASHTO 5.6.3.2.2-1 sin presfuerzo ni acero de compresion; 5.6.2.1):

        a = A_s·f_y / (alfa·f'c·b)      c = a / beta_1
        M_n = A_s·f_y·(d - a/2)         epsilon_t = 0.003·(d - c) / c

    Devuelve a y c en m, M_n en kN·m/m y epsilon_t (None sin acero).
    """
    _exigir_seccion(d, fc, fy)
    if not (_finito(As) and As >= 0):
        raise DatoInvalidoError("As", valor=As,
                                motivo="area de acero no negativa y finita")
    if beta_1 is None:
        beta_1 = beta_1_aashto(fc)
    a = As / MM2_POR_M2 * fy / (alfa * fc)
    c = a / beta_1
    M_n = As / MM2_POR_M2 * fy * KPA_POR_MPA * (d - a / 2)
    epsilon_t = EPSILON_CU_CONCRETO * (d - c) / c if c > 0 else None
    return {"a": a, "c": c, "M_n": M_n, "epsilon_t": epsilon_t,
            "beta_1": beta_1}


def momento_de_agrietamiento(*, espesor: float, fc: float,
                             gamma_3: float) -> float:
    """
    M_cr de AASHTO 5.6.3.3, kN·m por metro, para la seccion rectangular
    monolitica sin presfuerzo: la ec. 5.6.3.3-1 se reduce a

        M_cr = gamma_3·gamma_1·f_r·S,   f_r = 0.24·sqrt(f'c [ksi]),
        S = b·h²/6

    con gamma_1 = 1.6 y f_r en MPa por `MODULO_ROTURA_AASHTO_SI`.
    """
    if not (_finito(espesor) and espesor > 0 and _finito(fc) and fc > 0):
        raise DatoInvalidoError("espesor", valor=espesor,
                                motivo="espesor y f'c positivos y finitos")
    f_r = MODULO_ROTURA_AASHTO_SI * math.sqrt(fc)
    S = espesor ** 2 / NUCLEO_CENTRAL_DIVISOR
    return gamma_3 * GAMMA_1_AGRIETAMIENTO_AASHTO * f_r * KPA_POR_MPA * S


def cortante_del_concreto(*, d: float, a: float, espesor: float, fc: float,
                          beta: float) -> dict:
    """
    La resistencia NOMINAL a cortante del concreto sin refuerzo transversal,
    kN por metro (AASHTO 5.7.3.3 y 5.7.2.8):

        d_v = min[ max(d - a/2, 0.9·d, 0.72·h), d ]
        V_c = 0.0316·beta·sqrt(f'c)·b_v·d_v        (ksi, in; en SI,
              `VC_COEFICIENTE_AASHTO_SI`·beta·sqrt(f'c [MPa]), en MPa)
        V_n = min(V_c, 0.25·f'c·b_v·d_v)

    EL TOPE d_v <= d (correcciones de T-7c, H8) es una lectura del
    proyecto, declarada como `Interpretacion` de la cita
    AASHTO_LRFD_9.5.7.2.8#DV: la fuente define d_v como la distancia entre
    las resultantes de traccion y compresion (d - a/2) y dice que «need not
    be taken to be less than» el mayor de 0.9·d y 0.72·h. Con el
    recubrimiento de cota de una seccion delgada, 0.72·h supera al propio
    peralte efectivo (0.216 m frente a 0.202 m en una pantalla de 0.30 m) y
    el piso daria un brazo de cortante mayor que la distancia del acero a
    la cara comprimida; el proyecto no lo toma. `d_v_letra` es el de la
    letra, que se imprime al lado.
    """
    _exigir_seccion(d, fc, fc)
    d_v_letra = max(d - a / 2, DV_PISO_SOBRE_DE * d,
                    DV_PISO_SOBRE_H * espesor)
    d_v = min(d_v_letra, d)
    V_c = (VC_COEFICIENTE_AASHTO_SI * beta * math.sqrt(fc) * KPA_POR_MPA
           * d_v)
    V_tope = VN_TOPE_SOBRE_FC_AASHTO * fc * KPA_POR_MPA * d_v
    return {"d_v": d_v, "d_v_letra": d_v_letra, "V_c": V_c,
            "V_n": min(V_c, V_tope)}


def fisuracion_aashto(*, M_s: float, As: float, d: float, espesor: float,
                      d_c: float, fc: float, fy: float) -> dict:
    """
    --- correcciones de T-7c (H3) --- El control de fisuracion por
    distribucion del refuerzo de AASHTO 5.6.7 en UNA seccion rectangular de
    1 m de ancho, con el momento de SERVICIO I `M_s` (kN·m/m), el acero
    `As` (mm2/m) a un peralte efectivo `d` (m), el espesor y la distancia
    `d_c` (m) de la fibra extrema traccionada al eje de la barra mas
    proxima:

      aplica    la traccion de la seccion BRUTA, M_s/S con S = b·h²/6,
                supera 0.8·f_r (5.6.7; f_r de 5.4.2.6).
      f_ss      tension del acero en servicio con la seccion FISURADA
                elastica: n = E_s/E_c (5.4.3.2; C5.4.2.4-1), k =
                sqrt(2·rho·n + (rho·n)²) - rho·n, j = 1 - k/3, f_ss =
                M_s/(A_s·j·d). La fuente la limita a 0.60·f_y.
      beta_s    1 + d_c/[0.7·(h - d_c)] (ec. 5.6.7-2).
      s_max     700·gamma_e/(beta_s·f_ss) - 2·d_c (ec. 5.6.7-1), en SI por
                `FISURACION_COEFICIENTE_AASHTO_SI`, para cada clase de
                exposicion de `FISURACION_GAMMA_E`.

    Devuelve todo en MPa y m. Sin traccion (M_s <= 0) no aplica.
    """
    for nombre, x in (("As", As), ("d", d), ("espesor", espesor),
                      ("d_c", d_c), ("f'c", fc), ("fy", fy)):
        if not (_finito(x) and x > 0):
            raise DatoInvalidoError(
                nombre, valor=x,
                motivo="la fisuracion de AASHTO 5.6.7 necesita acero, "
                       "peraltes, recubrimiento y materiales positivos y "
                       "finitos")
    if not _finito(M_s):
        raise LimiteNumericoError("M_s", valor=M_s,
                                  motivo="el momento de servicio no es finito")
    if not d_c < espesor:
        raise DatoInvalidoError("d_c", valor=d_c,
                                motivo="el eje de la barra tiene que caer "
                                       "dentro del espesor de la seccion")
    f_r = MODULO_ROTURA_AASHTO_SI * math.sqrt(fc)
    S = espesor ** 2 / NUCLEO_CENTRAL_DIVISOR
    f_t = M_s / S / KPA_POR_MPA
    umbral = FISURACION_FRACCION_FR * f_r
    E_c = EC_COEFICIENTE_AASHTO_SI * fc ** EC_EXPONENTE_AASHTO
    n = ES_REFUERZO_AASHTO_MPA / E_c
    rho_n = As / MM2_POR_M2 / d * n
    k = math.sqrt(rho_n ** 2 + 2 * rho_n) - rho_n
    j = 1 - k / LADOS_DEL_TRIANGULO
    f_ss = max(M_s, 0.0) / (As / MM2_POR_M2 * j * d) / KPA_POR_MPA
    beta_s = 1 + d_c / (FISURACION_BETA_S_FACTOR * (espesor - d_c))
    s_max = ({clase: FISURACION_COEFICIENTE_AASHTO_SI * g / (beta_s * f_ss)
              - 2 * d_c for clase, g in FISURACION_GAMMA_E.items()}
             if f_ss > 0 else {})
    return {"aplica": f_t > umbral + TOL_UMBRAL_NORMATIVO, "f_t": f_t,
            "umbral": umbral, "f_r": f_r, "E_c": E_c, "n": n, "k": k,
            "j": j, "f_ss": f_ss,
            "f_ss_max": FISURACION_FSS_MAX_SOBRE_FY * fy, "beta_s": beta_s,
            "d_c": d_c, "s_max": s_max}


def clase_de_exposicion() -> Optional[str]:
    """
    La clase de exposicion de AASHTO 5.6.7 que el Propietario declaro
    ('clase_exposicion_fisuracion_cabezal' [A], SIN valor de archivo), o
    None si no la declaro: la fila de fisuracion lo dice como «no
    decidida». Un valor fuera de las dos clases se rechaza.
    """
    try:
        clase = ca.valor(CRITERIO_CLASE_EXPOSICION)
    except CriterioPendienteError:
        return None
    if clase not in CLASES_DE_EXPOSICION:
        raise DatoInvalidoError(
            CRITERIO_CLASE_EXPOSICION, valor=clase,
            motivo="se espera una de: " + ", ".join(CLASES_DE_EXPOSICION))
    return clase


def _fila_de_fisuracion(*, fis: dict, s_prop: float, clase: Optional[str],
                        codigo: str, donde: str, M_s: float, As: float,
                        rec: float, barra) -> Verificacion:
    """
    --- correcciones de T-7c (H3) --- La fila A6: el control de fisuracion
    de AASHTO 5.6.7 con el espaciamiento propuesto.

      no aplica   la traccion bruta de servicio no pasa de 0.8·f_r: CUMPLE,
                  diciendolo.
      declarada   la clase del Propietario DECIDE: s <= s_max(clase) y
                  f_ss <= 0.60·f_y.
      sin clase   CUMPLE si cumple tambien la Clase 2 (la mas exigente);
                  INDICADOR «no decidida» si solo cumple la Clase 1; NO
                  CUMPLE si no cumple ni la 1, que es la que cualquier
                  clase pide.
    """
    mag = lambda s, v, u, p, c=CIFRAS_MAGNITUD: Magnitud(s, v, u, p, cifras=c)  # noqa: E731
    s1 = fis["s_max"].get(CLASE_EXPOSICION_1)
    s2 = fis["s_max"].get(CLASE_EXPOSICION_2)
    fss_ok = fis["f_ss"] <= fis["f_ss_max"] + TOL_UMBRAL_NORMATIVO
    sustitucion = (
        mag("M_s", M_s, "kN·m/m", "Servicio I (AASHTO Tabla 3.4.1-1, todas "
            "las cargas con 1.00), con el mismo empuje con que se arma"),
        mag("f_t bruta", fis["f_t"], "MPa", "M_s / (b·h²/6)", CIFRAS_FACTOR),
        mag("0.8·f_r", fis["umbral"], "MPa", "f_r = 0.24·sqrt(f'c [ksi]) "
            "(5.4.2.6)", CIFRAS_FACTOR),
        mag("A_s", As, "mm2/m", barra.texto if barra is not None else
            "acero adoptado (sin barra del catalogo)", 0),
        mag("n", fis["n"], "", "E_s / E_c (5.4.3.2; C5.4.2.4-1)",
            CIFRAS_FACTOR),
        mag("f_ss", fis["f_ss"], "MPa", "M_s / (A_s·j·d), seccion fisurada "
            f"elastica, j = {fis['j']:.4f}; tope 0.60·f_y = "
            f"{fis['f_ss_max']:.1f} MPa", 1),
        mag("d_c", fis["d_c"], "m", f"recubrimiento con que se arma "
            f"({rec:.1f} mm) mas el radio de la barra"),
        mag("beta_s", fis["beta_s"], "", "1 + d_c/[0.7·(h - d_c)] "
            "(ec. 5.6.7-2)", CIFRAS_FACTOR),
        mag("s_max Clase 1", s1 if s1 is not None else 0.0, "m",
            "gamma_e = 1.00 (ec. 5.6.7-1)"),
        mag("s_max Clase 2", s2 if s2 is not None else 0.0, "m",
            "gamma_e = 0.75 (ec. 5.6.7-1)"),
    )
    comunes = dict(
        fundamento="F9.ARM_FISURACION", codigo=codigo,
        que=f"A6, control de fisuracion en servicio (AASHTO 5.6.7): {donde}",
        formula="si M_s/S > 0.8·f_r: s <= 700·gamma_e/(beta_s·f_ss) - 2·d_c "
                "(ksi, in; en SI 122.59·gamma_e/(beta_s·f_ss [MPa]) - 2·d_c "
                "[m]) y f_ss <= 0.60·f_y",
        sustitucion=sustitucion, criterio=CRITERIO_CLASE_EXPOSICION,
        cita="AASHTO_LRFD_9.5.6.7#FISURACION",
        citas=("AASHTO_LRFD_9.5.6.7#ESPACIAMIENTO",
               "AASHTO_LRFD_9.5.6.7#GAMMA_E", "AASHTO_LRFD_9.5.6.7#FSS",
               "AASHTO_LRFD_9.C5.6.7#CLASE_1", "AASHTO_LRFD_9.5.4.3.2#ES",
               "AASHTO_LRFD_9.C5.4.2.4#EC", "AASHTO_LRFD_9.T3.4.1-1"))
    if not fis["aplica"]:
        return _verificacion_de_armado(
            resultado=mag("f_t bruta", fis["f_t"], "MPa", "Servicio I",
                          CIFRAS_FACTOR),
            descripcion_umbral="traccion bruta en servicio <= 0.8·f_r: la "
                               "seccion no queda sujeta a 5.6.7",
            admisible=fis["umbral"], unidad="MPa",
            aplicacion="condicion de aplicacion de la fuente",
            cumple=True, margen=fis["umbral"] - fis["f_t"], decide=True,
            obtenido=fis["f_t"],
            nota=("La traccion de la seccion bruta no alcanza el 80 % del "
                  "modulo de rotura: AASHTO 5.6.7 no aplica y el "
                  "espaciamiento lo fijan los topes de A4."),
            explicacion_falla="", explicacion_cumple=(
                "5.6.7 no aplica: la traccion bruta de servicio no pasa de "
                "0.8·f_r"), **comunes)
    if clase is not None:
        s_lim = fis["s_max"][clase]
        cumple = fss_ok and s_prop <= s_lim + TOL_UMBRAL_NORMATIVO
        return _verificacion_de_armado(
            resultado=mag("s", s_prop, "m", "espaciamiento propuesto"),
            descripcion_umbral=f"s <= s_max de la {clase.replace('_', ' ')} "
                               "y f_ss <= 0.60·f_y",
            admisible=s_lim, unidad="m",
            aplicacion=(f"exigencia de la fuente con la clase de exposicion "
                        f"que declaro el Propietario "
                        f"('{CRITERIO_CLASE_EXPOSICION}' = '{clase}')"),
            cumple=cumple, margen=s_lim - s_prop, decide=True,
            obtenido=s_prop,
            nota="La barra propuesta respeta este espaciamiento si alguna "
                 "del catalogo lo consigue.",
            explicacion_falla=(
                "la tension del acero en servicio supera 0.60·f_y: aumentar "
                "el acero" if not fss_ok else
                "el espaciamiento propuesto supera el de 5.6.7: ninguna "
                "barra del catalogo lo cumple; reducir el espaciamiento o "
                "el recubrimiento"), **comunes)
    cumple_2 = fss_ok and s2 is not None and s_prop <= s2 + TOL_UMBRAL_NORMATIVO
    cumple_1 = fss_ok and s1 is not None and s_prop <= s1 + TOL_UMBRAL_NORMATIVO
    return _verificacion_de_armado(
        resultado=mag("s", s_prop, "m", "espaciamiento propuesto (respeta "
                      "la Clase 1, la menos exigente)"),
        descripcion_umbral="s <= s_max de la clase que declare el "
                           "Propietario (se imprime la de la Clase 2, la "
                           "mas exigente)",
        admisible=s2 if s2 is not None else 0.0, unidad="m",
        aplicacion=(f"clase de exposicion NO DECIDIDA "
                    f"('{CRITERIO_CLASE_EXPOSICION}' sin valor: la declara "
                    "el Propietario)"),
        cumple=cumple_2, margen=(s2 if s2 is not None else 0.0) - s_prop,
        decide=not cumple_1, obtenido=s_prop,
        nota=(f"Clase 1: s <= {s1 if s1 is not None else 0.0:.3f} m "
              f"({'cumple' if cumple_1 else 'NO cumple'}); Clase 2: s <= "
              f"{s2 if s2 is not None else 0.0:.3f} m "
              f"({'cumple' if cumple_2 else 'NO cumple'})."),
        explicacion_falla=(
            "no decidida: con la Clase 1 cumple y con la Clase 2 no; "
            "declarar la clase de exposicion" if cumple_1 else
            "no cumple ni con la Clase 1, que cualquier clase pide: "
            + ("la tension del acero en servicio supera 0.60·f_y"
               if not fss_ok else "reducir el espaciamiento o el "
               "recubrimiento")), **comunes)


def simplificado_permitido(*, es_zapata: bool, espesor: float,
                           vuelo: Optional[float], d_v: float
                           ) -> Tuple[bool, str]:
    """
    Si AASHTO 5.7.3.4.1 PERMITE el procedimiento simplificado (beta = 2.0,
    theta = 45 grados) en una seccion sin refuerzo transversal, y por cual
    de sus condiciones:

      * zapata cuya distancia del punto de cortante nulo a la cara del muro
        (el vuelo de la punta o del talon) es menor que 3·d_v; o
      * seccion de peralte total menor que 16.0 in (0.4064 m).

    La tercera condicion de la fuente -- llevar el refuerzo transversal
    minimo de 5.7.2.5 -- no se da: el cabezal no lleva estribos.
    """
    if es_zapata and vuelo is not None and \
            vuelo < ZAPATA_SIMPLIFICADO_VECES_DV * d_v - TOL_UMBRAL_NORMATIVO:
        return True, (f"zapata con vuelo {vuelo:.3f} m < 3·d_v = "
                      f"{ZAPATA_SIMPLIFICADO_VECES_DV * d_v:.3f} m")
    if espesor < PERALTE_MAX_SIMPLIFICADO_AASHTO_SI - TOL_UMBRAL_NORMATIVO:
        return True, (f"peralte total {espesor:.3f} m < 16.0 in = "
                      f"{PERALTE_MAX_SIMPLIFICADO_AASHTO_SI:.4f} m")
    return False, (f"peralte total {espesor:.3f} m >= 16.0 in = "
                   f"{PERALTE_MAX_SIMPLIFICADO_AASHTO_SI:.4f} m"
                   + ("" if not es_zapata else
                      f" y vuelo {vuelo:.3f} m >= 3·d_v = "
                      f"{ZAPATA_SIMPLIFICADO_VECES_DV * d_v:.3f} m"))


def beta_procedimiento_general(*, M_u: float, V_u: float, d_v: float,
                               A_s: float) -> dict:
    """
    β y εs del procedimiento GENERAL de cortante de AASHTO 5.7.3.4.2 (pags.
    impresas 5-70 a 5-72) para una seccion SIN el refuerzo transversal
    minimo, por metro de ancho (VE-3.14, H-2 de los ensayos de diseño del
    cabezal: hasta aqui el programa se detenia con «metodo no evaluable»
    cuando el simplificado de 5.7.3.4.1 no aplicaba):

        |M_u| >= |V_u|·d_v                                  (definicion de M_u)
        εs  = (|M_u|/d_v + |V_u|) / (E_s·A_s) >= 0            (ec. 5.7.3.4.2-4)
        s_x = d_v                       (una sola capa de acero en traccion)
        s_xe = s_x·1.38 / (a_g + 0.63), 12.0 in <= s_xe <= 80.0 in  (5.7.3.4.2-7)
        β   = [4.8 / (1 + 750·εs)]·[51 / (39 + s_xe)]         (ec. 5.7.3.4.2-2)

    con N_u = A_ps = V_p = 0 (el cabezal no lleva traccion axial ni
    presfuerzo) y a_g = 0, la cota inferior que vale para cualquier agregado
    (interpretacion de la cita AASHTO_LRFD_9.5.7.3.4.2#SXE). `M_u` en kN·m/m,
    `V_u` en kN/m, `d_v` en m y `A_s` en mm2/m.
    """
    for nombre, x in (("M_u", M_u), ("V_u", V_u)):
        if not (_finito(x) and x >= 0):
            raise LimiteNumericoError(nombre, valor=x,
                                      motivo="solicitacion no negativa y finita")
    for nombre, x in (("d_v", d_v), ("A_s", A_s)):
        if not (_finito(x) and x > 0):
            raise DatoInvalidoError(nombre, valor=x,
                                    motivo="positivo y finito para el "
                                           "procedimiento general de cortante")
    M = max(M_u, V_u * d_v)
    rigidez = ES_REFUERZO_AASHTO_MPA * A_s / N_POR_KN          # kN/m
    eps_s = max((M / d_v + V_u) / rigidez, 0.0)
    s_x_in = d_v * MILIMETROS_POR_METRO / PULGADA_EN_MM
    s_xe_in = s_x_in * SXE_FACTOR_AGREGADO / SXE_SUMANDO_AGREGADO_IN
    s_xe_in = min(max(s_xe_in, SXE_MIN_IN), SXE_MAX_IN)
    beta = (GENERAL_BETA_NUMERADOR
            / (1 + GENERAL_BETA_COEF_DEFORMACION * eps_s)
            * GENERAL_BETA_NUMERADOR_SXE_IN
            / (GENERAL_BETA_SUMANDO_SXE_IN + s_xe_in))
    return {"beta": beta, "eps_s": eps_s, "M_u_efectivo": M,
            "s_x_in": s_x_in, "s_xe_in": s_xe_in}


def acero_para_cortante_general(*, M_u: float, V_u: float, d_v: float,
                                 phi: float, V_c_por_beta: float,
                                 V_tope: float) -> Optional[float]:
    """
    --- VE-3.14 --- El acero longitudinal en traccion (mm2/m) con el que la
    seccion SIN refuerzo transversal cumple phi·V_n >= V_u por el
    procedimiento GENERAL de AASHTO 5.7.3.4.2: la ec. 5.7.3.4.2-2 despejada
    en εs y la 5.7.3.4.2-4 despejada en A_s,

        β_n  = V_u / (phi·V_c_por_beta)
        εs_n = [4.8·51 / ((39 + s_xe)·β_n) - 1] / 750
        A_s  = (max(M_u, V_u·d_v)/d_v + V_u) / (E_s·εs_n)

    con s_x = d_v y a_g = 0 (`beta_procedimiento_general`). `V_c_por_beta`
    es la resistencia del concreto por unidad de β con ESTE d_v (kN/m) y
    `V_tope` el tope 0.25·f'c·b_v·d_v. Es lo que el procedimiento general
    pone en manos del proyectista sin cambiar el espesor: mas acero
    longitudinal, menor εs, mayor β. None si ningun acero alcanza (el tope
    de 0.25·f'c·b_v·d_v, o un β mayor que el de εs = 0): entonces lo que
    falta es espesor.
    """
    if not (_finito(V_u) and V_u > 0):
        return 0.0
    if phi * V_tope < V_u - TOL_UMBRAL_NORMATIVO:
        return None
    s_xe_in = d_v * MILIMETROS_POR_METRO / PULGADA_EN_MM \
        * SXE_FACTOR_AGREGADO / SXE_SUMANDO_AGREGADO_IN
    s_xe_in = min(max(s_xe_in, SXE_MIN_IN), SXE_MAX_IN)
    beta_n = V_u / (phi * V_c_por_beta)
    tope_beta = (GENERAL_BETA_NUMERADOR * GENERAL_BETA_NUMERADOR_SXE_IN
                 / (GENERAL_BETA_SUMANDO_SXE_IN + s_xe_in))
    eps_n = (tope_beta / beta_n - 1) / GENERAL_BETA_COEF_DEFORMACION
    if not eps_n > 0:
        return None
    M = max(M_u, V_u * d_v)
    return (M / d_v + V_u) * N_POR_KN / (ES_REFUERZO_AASHTO_MPA * eps_n)


def acero_de_temperatura_aashto(*, ancho: float, espesor: float,
                                fy: float) -> float:
    """
    Acero de retraccion y temperatura de AASHTO 5.10.6, mm2 por metro, POR
    CARA Y POR DIRECCION: A_s >= 1.30·b·h / [2·(b + h)·f_y], acotado a 0.11
    <= A_s <= 0.60 in2/ft. `ancho` (b, el menor ancho de la seccion) y
    `espesor` (h) en m; la conversion a SI esta en la constante.

    EL ANCHO ES EL REAL DEL ELEMENTO, no una franja de calculo (cierre de O-2,
    decision 3 del dueño, 2026-11-17): 5.10.6 define b como el «least width
    of component section», y una franja de 12 in (CDOT Ex. 11) es una
    convencion de calculo, no la letra. Con el ancho real el minimo es mayor
    en un muro largo, que es el lado seguro; en los casos de CDOT manda el
    piso de 0.11 in2/ft y el ancho no cambia el acero (docs/
    validacion_cabezal.md).
    """
    for nombre, x in (("ancho", ancho), ("espesor", espesor), ("fy", fy)):
        if not (_finito(x) and x > 0):
            raise DatoInvalidoError(nombre, valor=x,
                                    motivo="positivo y finito")
    b, h = ancho * MILIMETROS_POR_METRO, espesor * MILIMETROS_POR_METRO
    As = (TEMPERATURA_COEFICIENTE_AASHTO_SI * b * h / (2 * (b + h) * fy)
          * MILIMETROS_POR_METRO)
    return min(max(As, TEMPERATURA_AS_MIN_AASHTO_SI), TEMPERATURA_AS_MAX_AASHTO_SI)


def espaciamiento_maximo_del_armado(*, espesor: float,
                                    regla: Optional[str] = None
                                    ) -> Tuple[float, str]:
    """
    El espaciamiento maximo del refuerzo de una cara, m, y de donde sale: el
    menor de los topes de AASHTO 5.10.3.2 (1.5 veces el espesor y 18.0 in) y
    de 5.10.6 (12.0 in en muros y zapatas de mas de 18.0 in; en lo demas,
    tres veces el espesor «but not less than 18.0 in.») y, con la regla del
    mas exigente, de E.060 14.3.3 (tres veces el espesor y 400 mm).
    """
    if not (_finito(espesor) and espesor > 0):
        raise DatoInvalidoError("espesor", valor=espesor,
                                motivo="espesor positivo y finito")
    regla = _regla_de_minimos() if regla is None else regla
    if espesor > TEMPERATURA_ESPESOR_GRUESO_M + TOL_UMBRAL_NORMATIVO:
        temperatura = TEMPERATURA_S_MAX_GRUESO_M
    else:
        temperatura = max(TEMPERATURA_S_VECES_ESPESOR * espesor,
                          TEMPERATURA_S_PISO_M)
    candidatos = [
        (ESPACIAMIENTO_MAX_VECES_ESPESOR_AASHTO * espesor,
         "1.5 veces el espesor (AASHTO 5.10.3.2)"),
        (ESPACIAMIENTO_MAX_ABSOLUTO_AASHTO_M, "18.0 in (AASHTO 5.10.3.2)"),
        (temperatura, "acero de temperatura (AASHTO 5.10.6)"),
    ]
    if regla == MINIMOS_MAS_EXIGENTE:
        candidatos.append((espaciamiento_maximo(espesor=espesor),
                           "min(3h, 400 mm) (E.060 14.3.3, por analogia)"))
    return min(candidatos)


def cuantia_vertical_ec_11_32(*, hm: float, lm: float,
                              rho_h: float) -> float:
    """
    La cuantia vertical minima de un muro bajo el regimen de cortante EN SU
    PLANO, E.060 11.10.10.3, ec. (11-32), completa y con sus dos topes:

        rho_v >= 0,0025 + 0,5·(2,5 - hm/lm)·(rho_h - 0,0025) >= 0,0025

    «pero no necesita ser mayor que el valor de rho_h requerido por
    11.10.10.1». `hm` es la altura total del muro y `lm` su longitud total
    (m); `rho_h`, la cuantia horizontal requerida. El piso sale del criterio
    [N→] 'cuantia_vertical_cortante_alto_e060_art_11_10_10_3'.
    """
    for nombre, x in (("hm", hm), ("lm", lm), ("rho_h", rho_h)):
        if not (_finito(x) and x > 0):
            raise DatoInvalidoError(
                nombre, valor=x,
                motivo="la ec. (11-32) de E.060 necesita altura, longitud y "
                       "cuantia horizontal positivas y finitas")
    piso = float(ca.valor(CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO))
    rho_v = piso + EC_11_32_FACTOR * (EC_11_32_ESBELTEZ - hm / lm) * (
        rho_h - piso)
    return min(max(rho_v, piso), max(rho_h, piso))


def proponer_barra(*, As: float, s_max: float, catalogo: dict,
                   desde: str, admite=None) -> Optional[BarraPropuesta]:
    """
    La barra y el espaciamiento PROPUESTOS para dar `As` (mm2/m) con un
    espaciamiento no mayor que `s_max` (m): empezando por la barra `desde`
    y subiendo de diametro, la primera que con el MAYOR espaciamiento de la
    serie del catalogo lo consigue. None si ninguna barra del catalogo
    alcanza. Es una regla de propuesta [A], no una exigencia.

    `admite(diametro_mm, s, As_provisto)` (correcciones de T-7c, H3) es una
    condicion mas que la propuesta tiene que cumplir -- la del control de
    fisuracion de AASHTO 5.6.7 --: el espaciamiento que no la cumple se
    salta.
    """
    if not (_finito(As) and As >= 0 and _finito(s_max) and s_max > 0):
        raise DatoInvalidoError("As", valor=As,
                                motivo="acero no negativo y espaciamiento "
                                       "maximo positivo, finitos")
    activo = False
    for diametro, area, nombre in catalogo["barras"]:
        activo = activo or nombre == desde
        if not activo:
            continue
        for s in catalogo["espaciamientos"]:
            if s <= s_max + TOL_UMBRAL_NORMATIVO and \
                    area / s >= As - TOL_UMBRAL_NORMATIVO and \
                    (admite is None or admite(diametro, s, area / s)):
                return BarraPropuesta(designacion=nombre,
                                      diametro_mm=diametro, area_mm2=area,
                                      espaciamiento=s, As_provisto=area / s)
    return None


# ---------------------------------------------------------------------------
# Las solicitaciones con que se arma: reposo y activo, y el contraste E.060
# ---------------------------------------------------------------------------

def _factores_por_tipo(cargas: tuple, **por_tipo) -> dict:
    """Factor de cada carga: el de su codigo (con «_» por «.») o el de su tipo."""
    return {c.codigo: por_tipo.get(c.codigo.replace(".", "_"),
                                   por_tipo.get(c.tipo, 0.0))
            for c in cargas}


def cargas_en_reposo(cargas: tuple, datos: dict) -> tuple:
    """
    Las cargas del ensamble de T-7b pasadas al empuje en REPOSO, para la
    resistencia de los elementos (regimen 'no_cedente_k0'). SOLO cambian
    las que son empuje de tierras:

        EH.h   P_A·cos(delta + beta)  ->  (K0 / K_A)·P_A, todo horizontal
        EH.v   P_A·sen(delta + beta)  ->  0 (sin friccion muro-relleno)
        LS.h   K_A·gamma·h_eq·h       ->  K0·gamma·h_eq·h

    con los mismos brazos (el diagrama conserva su forma). El peso de la
    pantalla y de la zapata, el del relleno sobre el talon, el de la
    sobrecarga, el agua y la subpresion NO se tocan. K0 es el de AASHTO
    3.11.5.2-1 (1 - sen phi), de terreno horizontal.
    """
    K_A, K0, P_A = datos["K_A"], datos["K0"], datos["P_A"]
    if not (_finito(K_A) and K_A > 0 and _finito(K0) and K0 > 0):
        raise LimiteNumericoError(
            "K0/K_A", valor=(K0, K_A),
            motivo="el coeficiente de empuje activo o el de reposo no es "
                   "positivo y finito: no hay cociente con que escalar")
    escala = K0 / K_A
    nuevas = []
    for c in cargas:
        if c.codigo == C_EH_H:
            c = _reemplazar(c, H=P_A * escala,
                            descripcion="empuje en reposo, horizontal",
                            procedencia="(K0 / K_A)·P_A, sin friccion "
                                        "muro-relleno")
        elif c.codigo == C_EH_V:
            c = _reemplazar(c, V=0.0,
                            descripcion="empuje en reposo, sin componente "
                                        "vertical",
                            procedencia="en reposo no se moviliza friccion "
                                        "muro-relleno")
        elif c.codigo == C_LS_H:
            # (VE-5) de los datos y no de la carga, para que sea idempotente
            # sobre el ensamble del muro que no cede, que ya va en reposo.
            c = _reemplazar(c, H=K0 * datos["gamma"] * datos["h_eq"]
                            * datos["h"],
                            descripcion="sobrecarga viva, empuje en reposo",
                            procedencia="K0·gamma·h_eq·h")
        nuevas.append(c)
    return tuple(nuevas)


def _combinaciones_en_reposo(cargas0: tuple, B: float) -> tuple:
    """
    Resistencia I con el factor de carga de la fila «En reposo» de la Tabla
    2.4.5.3.1-2 (1.35 / 0.90) en vez del de la activa, en las dos variantes
    del ensamble: maximos (con el peso de la sobrecarga) y minimos; y con el
    modificador de carga de AASHTO 1.3.2.1 (`_resistencia_i_con_eta`).
    """
    g = factores_de_carga("Resistencia I")
    reposo = TABLA_GAMMA_P_FILAS[FILA_EH_EN_REPOSO]
    # (verificacion de T-7, punto 9) con el modificador de carga de AASHTO
    # 1.3.2.1 dentro de cada factor, como en la estabilidad.
    maximos, minimos = _resistencia_i_con_eta(g, reposo["max"])
    return (
        _combinar("Resistencia I (maximos), empuje en reposo", MARCO_LRFD,
                  CondicionAnalisis.ESTATICO, cargas0,
                  _factores_por_tipo(cargas0, **maximos), B, "portante"),
        _combinar("Resistencia I (minimos), empuje en reposo", MARCO_LRFD,
                  CondicionAnalisis.ESTATICO, cargas0,
                  _factores_por_tipo(cargas0, **minimos), B,
                  "excentricidad y deslizamiento"),
    )


def _combinaciones_e060(cargas: tuple, B: float) -> tuple:
    """
    Las dos combinaciones de E.060 9.2.5 para el CONTRASTE: (9-6) U = 1,4 CM
    + 1,7 CV + 1,7 CE y (9-7) U = 0,9 CM + 1,7 CE. CM es el peso del
    concreto; CE, el peso y el empuje del suelo y la presion del agua
    contenida en el; CV, la sobrecarga viva.
    """
    est = CondicionAnalisis.ESTATICO
    return (
        _combinar("E.060 (9-6)", MARCO_E060, est, cargas,
                  _factores_por_tipo(cargas, DC=E060_FACTOR_CM,
                                     EV=E060_FACTOR_CE, EH=E060_FACTOR_CE,
                                     WA=E060_FACTOR_CE, LS=E060_FACTOR_CV),
                  B, "contraste"),
        _combinar("E.060 (9-7)", MARCO_E060, est, cargas,
                  _factores_por_tipo(cargas, DC=E060_FACTOR_CM_MINIMO,
                                     EV=E060_FACTOR_CE, EH=E060_FACTOR_CE,
                                     WA=E060_FACTOR_CE, LS=0.0),
                  B, "contraste"),
    )


def _clave_de(s: SolicitacionDeElemento) -> str:
    if s.elemento == ELEMENTO_PANTALLA:
        return SECCION_PANTALLA
    if s.elemento == ELEMENTO_ALEROS:
        return SECCION_ALERO
    return SECCION_PUNTA if s.seccion.startswith("punta") else SECCION_TALON


def presion_de_contacto_lineal(combo: CombinacionDeEstabilidad
                                ) -> Optional[dict]:
    """
    La presion de contacto del terreno bajo la zapata para el DISEÑO
    ESTRUCTURAL, lineal: AASHTO 10.6.5 («a triangular or trapezoidal contact
    stress distribution based on factored loads shall be used»). No es la
    uniforme sobre B - 2e de la capacidad portante (10.6.1.4), que es la que
    el ensamble de T-7b usa en E1 y en sus solicitaciones de la zapata.

        |e| <= B/6   trapecio: sigma = (N/B)·(1 +- 6·e/B) en punta y talon
        |e| >  B/6   triangulo desde el borde cargado, de largo 3·(B/2 - |e|)
                     y maxima 2·N / largo

    con e positiva hacia la punta. Devuelve el tramo cargado [x0, x1] (m
    desde la punta) y la presion en sus extremos (kPa); None si la
    resultante no comprime la base o cae fuera de ella.
    """
    N, B = combo.N, combo.B
    if not (_finito(N) and N > 0 and _finito(B) and B > 0):
        return None
    e = combo.excentricidad
    if not _finito(e):
        return None
    if abs(e) <= B / NUCLEO_CENTRAL_DIVISOR:
        return {"x0": 0.0, "x1": B,
                "s0": N / B * (1 + NUCLEO_CENTRAL_DIVISOR * e / B),
                "s1": N / B * (1 - NUCLEO_CENTRAL_DIVISOR * e / B),
                "forma": "trapecio"}
    largo = LADOS_DEL_TRIANGULO * (B / 2 - abs(e))
    if not largo > 0:
        return None
    if e > 0:
        return {"x0": 0.0, "x1": largo, "s0": 2 * N / largo, "s1": 0.0,
                "forma": "triangulo desde la punta"}
    return {"x0": B - largo, "x1": B, "s0": 0.0, "s1": 2 * N / largo,
            "forma": "triangulo desde el talon"}


def solicitaciones_de_la_zapata(g: GeometriaCabezal, cargas: tuple,
                                combo: CombinacionDeEstabilidad,
                                datos: dict) -> Optional[dict]:
    """
    El cortante y el momento de la PUNTA y del TALON en la cara de la
    pantalla para UNA combinacion, con la presion de contacto LINEAL del
    diseño estructural (`presion_de_contacto_lineal`, AASHTO 10.6.5) y con
    la subpresion del agua, que tambien empuja la zapata hacia arriba:

      punta   presion del terreno + subpresion - peso propio; positivo =
              tracciona la cara inferior.
      talon   («metodo mas exacto» de 11.6.1.2) relleno, sobrecarga,
              componente vertical del empuje y peso propio, menos la presion
              del terreno y la subpresion que alcanzan al talon; positivo =
              tracciona la cara superior.

    None si la combinacion no deja presion de contacto evaluable.
    """
    presion = presion_de_contacto_lineal(combo)
    if presion is None:
        return None
    f = dict(combo.factores)
    por = {c.codigo: c for c in cargas}
    punta, talon, x_t = datos["punta"], datos["talon"], datos["x_trasdos"]
    B = g.B
    w = f.get(C_DC_ZAPATA, 0.0) * datos["gamma_c"] * g.espesor_zapata
    f_u = f.get(C_WA_U, 0.0) if C_WA_U in por else 0.0
    u_p = GAMMA_AGUA_KN_M3 * datos["h_w_natural"]
    u_t = GAMMA_AGUA_KN_M3 * datos["h_w"]
    lineal = (presion["x0"], presion["x1"], presion["s0"], presion["s1"])
    agua = (0.0, B, u_p, u_t)
    F_p, M_p = _carga_lineal_sobre_un_tramo(*lineal, 0.0, punta, punta)
    U_p, MU_p = _carga_lineal_sobre_un_tramo(*agua, 0.0, punta, punta)
    F_t, M_t = _carga_lineal_sobre_un_tramo(*lineal, x_t, B, x_t)
    U_t, MU_t = _carga_lineal_sobre_un_tramo(*agua, x_t, B, x_t)
    V_peso, M_peso = _talon_con_el_peso_entero(g, cargas, combo, datos)
    return {
        "punta": (F_p + f_u * U_p - w * punta,
                  M_p + f_u * MU_p - w * punta ** 2 / 2),
        "talon": (V_peso - F_t - f_u * U_t, M_peso - M_t - f_u * MU_t),
        "forma": presion["forma"], "sigma_punta": presion["s0"]
        if presion["x0"] <= 0 else 0.0,
    }


def _talon_con_el_peso_entero(g: GeometriaCabezal, cargas: tuple,
                              combo: CombinacionDeEstabilidad,
                              datos: dict) -> Tuple[float, float]:
    """
    El cortante y el momento del talon en la cara de la pantalla cargado con
    el PESO ENTERO de lo que tiene encima -- relleno, sobrecarga, componente
    vertical del empuje y peso propio --, SIN descontar la reaccion del
    terreno ni la subpresion: AASHTO 11.6.1.2 («loaded with the full weight
    of the superimposed material, unless a more exact method is used»).
    """
    f = dict(combo.factores)
    por = {c.codigo: c for c in cargas}
    x_t, talon = datos["x_trasdos"], datos["talon"]
    w = f.get(C_DC_ZAPATA, 0.0) * datos["gamma_c"] * g.espesor_zapata
    encima = [por[k] for k in (C_EV_TALON, C_LS_V, C_EH_V, C_EQ_V)
              if k in por]
    V = sum(f.get(c.codigo, 0.0) * c.V for c in encima) + w * talon
    M = (sum(f.get(c.codigo, 0.0) * c.V * (c.x - x_t) for c in encima)
         + w * talon ** 2 / 2)
    return V, M


def _pantalla_con_resultante_a_media_altura(g: GeometriaCabezal,
                                            cargas: tuple,
                                            combo: CombinacionDeEstabilidad,
                                            datos: dict, V_u: float,
                                            M_u: float
                                            ) -> Tuple[float, float]:
    """
    El cortante y el momento de la pantalla en su arranque con la resultante
    del empuje TOTAL del suelo (estatico mas incremento sismico) a h/2, en
    vez de donde el ensamble la pone: AASHTO C11.6.5.4, para el muro que no
    cede. Una resultante a h/2 es un diagrama UNIFORME sobre h; integrado
    sobre el arranque (correcciones de T-7c, H1) da H_total·(h - e_z)/h a
    (h - e_z)/2, y sustituye a la parte que los dos empujes del suelo
    ponian sobre el arranque con su propio diagrama.
    """
    f = dict(combo.factores)
    e_z = g.espesor_zapata
    h = datos["h"]
    arranque = empujes_sobre_el_arranque(cargas, datos, e_z,
                                         id_punto=g.id_punto)
    tierra = [c for c in cargas if c.codigo in (C_EH_H, C_EQ_H)]
    H_total = sum(f.get(c.codigo, 0.0) * c.H for c in tierra)
    V_su_sitio = sum(f.get(c.codigo, 0.0) * arranque[c.codigo][0]
                     for c in tierra)
    M_su_sitio = sum(f.get(c.codigo, 0.0) * arranque[c.codigo][1]
                     for c in tierra)
    alto = max(h - e_z, 0.0)
    H_uniforme = H_total * alto / h
    return (V_u - V_su_sitio + H_uniforme,
            M_u - M_su_sitio + H_uniforme * alto / 2)


def _combinaciones_de_servicio(cargas: tuple, B: float) -> tuple:
    """
    --- correcciones de T-7c (H3) --- Servicio I de la Tabla 3.4.1-1 de
    AASHTO (pag. impresa 3-17, PDF 71; cita AASHTO_LRFD_9.T3.4.1-1): todas
    las cargas del cabezal con factor 1.00, en las dos variantes del ensamble
    (con y sin el peso de la sobrecarga sobre el talon). Es el estado limite
    en que AASHTO 5.6.7 controla la fisuracion. Se rotulan con el marco ASD
    porque sus factores son los de servicio; no son las de la estabilidad.
    """
    est = CondicionAnalisis.ESTATICO
    servicio = dict(DC=1.0, EV=1.0, EH=1.0, LS=1.0, WA=1.0)
    return (
        _combinar("Servicio I", MARCO_ASD, est, cargas,
                  _factores_por_tipo(cargas, **servicio), B, "fisuracion"),
        _combinar("Servicio I (sin el peso de la sobrecarga)", MARCO_ASD,
                  est, cargas,
                  _factores_por_tipo(cargas, LS_v=0.0, **servicio), B,
                  "fisuracion"),
    )


def _momentos_de_servicio(entorno: EntornoDelCabezal, juego: tuple,
                          datos: dict) -> dict:
    """
    --- correcciones de T-7c (H3) --- El MOMENTO de Servicio I de cada
    seccion critica con un juego de cargas (el activo o el de reposo): la
    pantalla y el alero con el diagrama integrado sobre el arranque, la punta
    con la presion de contacto lineal y el talon con el peso entero, como en
    Resistencia I. {clave: M} con el mayor de las dos variantes; la punta
    falta si ninguna deja presion de contacto evaluable.
    """
    g = entorno.geometria
    salida = {}
    for combo in _combinaciones_de_servicio(juego, g.B):
        f = dict(combo.factores)
        arranque = empujes_sobre_el_arranque(juego, datos, g.espesor_zapata,
                                             id_punto=entorno.id_punto)
        M_p = sum(f[k] * M for k, (_, M) in arranque.items())
        for clave in (SECCION_PANTALLA, SECCION_ALERO):
            salida[clave] = max(salida.get(clave, M_p), M_p)
        z = solicitaciones_de_la_zapata(g, juego, combo, datos)
        if z is not None:
            salida[SECCION_PUNTA] = max(salida.get(SECCION_PUNTA,
                                                   z["punta"][1]),
                                        z["punta"][1])
        _, M_t = _talon_con_el_peso_entero(g, juego, combo, datos)
        if (z is not None and _eleccion(CRITERIO_MOMENTO_TALON,
                                        (TALON_PESO_ENTERO, TALON_EXACTO))
                == TALON_EXACTO):
            M_t = z["talon"][1]
        salida[SECCION_TALON] = max(salida.get(SECCION_TALON, M_t), M_t)
    return salida


def solicitaciones_de_resistencia(entorno: EntornoDelCabezal) -> dict:
    """
    Las solicitaciones factoradas con que se arma UN cabezal, seccion por
    seccion (pantalla, punta, talon y alero) y combinacion por combinacion
    del marco que rige, con los dos empujes lado a lado:

      Resistencia I    `M_u_cedente` / `V_u_cedente` son los del ensamble de
                       T-7b (empuje activo, factor 1.50); `M_u_reposo` /
                       `V_u_reposo`, los de `cargas_en_reposo` con el factor
                       de la fila «En reposo» (1.35). Con el regimen
                       'no_cedente_k0' rige la MAYOR de las dos; con
                       'cedente', la primera, y la otra se imprime.
      Evento Extremo I el empuje sismico con el factor de resistencia 1.0
                       (AASHTO 1.3.2.1). Con 'no_cedente_k0' las cargas
                       sismicas DEL ARMADO se calculan con k_h = 1.0·k_h0
                       (AASHTO 11.6.5.4: «the value of kh used to calculate
                       seismic earth pressure shall be increased to 1.0kh0»;
                       correcciones de T-7c, H2), por la puerta `k_h` de
                       `cargas_del_cabezal`, que la estabilidad externa no
                       usa: si 'factor_muro_eleccion' reduce k_h para el
                       ensamble, el armado del muro que no cede no lo
                       hereda. Con 'cedente', el k_h de la cadena. Y con
                       'no_cedente_k0' el cortante y el momento de la
                       pantalla y del alero son los mayores de los de esa
                       posicion y los de la resultante total a h/2
                       (C11.6.5.4). La fuente no da un coeficiente sismico
                       de reposo: no se inventa.
      talon            lo que diga 'momento_talon_cabezal' (AASHTO
                       11.6.1.2): con «peso_entero», el peso entero; con
                       «exacto» (valor de archivo desde VE-3.15), el que
                       descuenta la reaccion lineal de 10.6.5 de cada
                       combinacion, y el peso entero SOLO si la resultante
                       cae fuera de la base; el otro se imprime como
                       contraste. NO rige el mayor de los dos (este
                       renglon lo decia hasta VE-7 y era anterior a la
                       opcion 9; ficha VE7C-06: con «exacto» el talon de la
                       salida de A-01 del juego pide 3.1 veces menos
                       momento, en la envolvente, y su peralte no crece).

    Y el CONTRASTE con E.060 (solo estatica: 9.2 no combina sismo con
    empuje de suelos): el mayor momento y el mayor cortante de cada seccion
    con las combinaciones (9-6) y (9-7), sobre las mismas cargas. Y el
    MOMENTO DE SERVICIO I de cada seccion (`_momentos_de_servicio`), con el
    mismo regimen, para la fisuracion de AASHTO 5.6.7.

    SI LA CONDICION SISMICA NO ES EVALUABLE (agua en el plano de empuje,
    cuña sin maximo...) el armado sale solo de Resistencia I y lo AVISA,
    diciendo si la etapa de estabilidad sismica lleva el mismo bloqueo o si
    es solo el k_h0 del armado el que no se puede evaluar.
    """
    g = entorno.geometria
    regimen = regimen_de_resistencia()
    proc = _procedimiento()
    metodo_talon = _eleccion(CRITERIO_MOMENTO_TALON,
                             (TALON_PESO_ENTERO, TALON_EXACTO))
    est, sis = CondicionAnalisis.ESTATICO, CondicionAnalisis.SISMICO
    quien = _aviso_cabezal(entorno)
    avisos: List[str] = []
    alto_pantalla = g.H - g.espesor_zapata
    if (regimen == REGIMEN_RESISTENCIA_CEDENTE
            and alto_pantalla < ALTURA_VOLADIZO_ACTIVO_M):
        # --- VE-3.15 (H6 de su revision) --- «cede» se declara con
        # justificacion; por debajo de la altura de C3.11.5.2 la fuente no
        # da por movilizado el activo, y la corrida lo dice.
        avisos.append(
            f"{quien}: el armado se declara del muro que CEDE "
            f"('{CRITERIO_REGIMEN_RESISTENCIA}' = '{regimen}') y la pantalla "
            f"mide {alto_pantalla:.2f} m: AASHTO C3.11.5.2 da por movilizado "
            "el empuje activo de un muro en voladizo de mas de "
            f"{ALTURA_VOLADIZO_ACTIVO_M:.3f} m (5.0 ft). Por debajo, la "
            "declaracion necesita la justificacion que pide la ficha del "
            "criterio")

    cargas, datos = cargas_del_cabezal(entorno, est)
    if (regimen == REGIMEN_RESISTENCIA_CEDENTE
            and datos["regimen"] == REGIMEN_NO_CEDENTE):
        # --- VE-5 (ficha T7B-14) --- las dos declaraciones se contradicen
        # y la corrida lo dice: el ensamble ya va con el muro que no cede.
        avisos.append(
            f"{quien}: el armado se declara del muro que CEDE "
            f"('{CRITERIO_REGIMEN_RESISTENCIA}' = '{regimen}') y la "
            f"estabilidad del que NO cede ('{CRITERIO_REGIMEN}' = "
            f"'{REGIMEN_NO_CEDENTE}'): las solicitaciones «del muro que "
            "cede» salen del ensamble, que ya va con el empuje en reposo y "
            "k_h = 1.0·k_h0. Un cabezal que no cede en conjunto no tiene "
            "elementos que cedan: la declaracion coherente es "
            f"'{CRITERIO_REGIMEN_RESISTENCIA}' = 'no_cedente_k0'")
    combos = combinaciones_de_estabilidad(cargas, datos, est, g.B)
    lrfd = [c for c in combos if c.marco == MARCO_LRFD]
    cargas0 = cargas_en_reposo(cargas, datos)
    combos0 = _combinaciones_en_reposo(cargas0, g.B)
    ced = solicitaciones_por_elemento(entorno, cargas, combos, datos)
    rep = solicitaciones_por_elemento(entorno, cargas0, combos0, datos)
    usa_reposo = regimen == REGIMEN_RESISTENCIA_K0

    def de(lista, clave, nombre):
        return next((s for s in lista if _clave_de(s) == clave
                     and s.combinacion == nombre), None)

    secciones = {clave: [] for clave in (SECCION_PANTALLA, SECCION_PUNTA,
                                         SECCION_TALON, SECCION_ALERO)}
    sin_presion = []
    reposo_sin_presion = []

    def zapata(clave, juego, combinacion, datos_x):
        """(M, V, nota) de la punta o del talon, o (None, None, '')."""
        z = solicitaciones_de_la_zapata(g, juego, combinacion, datos_x)
        if clave == SECCION_TALON:
            Vp, Mp = _talon_con_el_peso_entero(g, juego, combinacion,
                                               datos_x)
            exacto = ("no evaluable (resultante fuera de la base)"
                      if z is None else
                      f"M = {z['talon'][1]:.2f}, V = {z['talon'][0]:.2f} "
                      f"({z['forma']})")
            if metodo_talon == TALON_EXACTO and z is not None:
                # --- VE-3.14, opcion 9 --- el «more exact method» de
                # 11.6.1.2: la reaccion lineal de 10.6.5 con las cargas
                # factoradas de ESTA combinacion, sin traccion.
                return z["talon"][1], z["talon"][0], (
                    "metodo mas exacto (AASHTO 11.6.1.2, "
                    f"'{CRITERIO_MOMENTO_TALON}' = '{TALON_EXACTO}'): "
                    "descontando la reaccion lineal del terreno (10.6.5, "
                    f"cargas de esta combinacion, sin traccion) y la "
                    f"subpresion: {exacto}; peso entero (contraste): M = "
                    f"{Mp:.2f} kN·m/m, V = {Vp:.2f} kN/m")
            return Mp, Vp, (
                f"peso entero (AASHTO 11.6.1.2): M = {Mp:.2f} kN·m/m, V = "
                f"{Vp:.2f} kN/m; descontando la reaccion lineal del terreno "
                f"y la subpresion: {exacto}")
        if z is None:
            return None, None, ""
        V, M = z["punta"]
        return M, V, (f"presion de contacto lineal (AASHTO 10.6.5): "
                      f"{z['forma']}, {z['sigma_punta']:.1f} kPa en la punta")

    # `strict`: las dos Resistencia I del ensamble (maximos y minimos) y las
    # dos de reposo se corresponden una a una; si dejaran de hacerlo es un
    # fallo de programa, y `zip` lo dice.
    for combo, combo0 in zip(lrfd, combos0, strict=True):
        for clave in secciones:
            nota = ""
            if clave in (SECCION_PUNTA, SECCION_TALON):
                M_c, V_c, nota = zapata(clave, cargas, combo, datos)
                M_r, V_r, _ = zapata(clave, cargas0, combo0, datos)
                if usa_reposo and M_r is None and M_c is not None:
                    reposo_sin_presion.append(combo0.nombre)
            else:
                a = de(ced, clave, combo.nombre)
                b = de(rep, clave, combo0.nombre)
                M_c = None if a is None else a.M_u
                V_c = None if a is None else a.V_u
                M_r = None if b is None else b.M_u
                V_r = None if b is None else b.V_u
            if M_c is None:
                sin_presion.append(combo.nombre)
                continue        # punta sin presion de contacto evaluable
            candidatos_M = [M_c] + ([M_r] if usa_reposo and M_r is not None
                                    else [])
            candidatos_V = [abs(V_c)] + ([abs(V_r)] if usa_reposo
                                         and V_r is not None else [])
            secciones[clave].append(SolicitacionDeArmado(
                combinacion=combo.nombre, condicion=est,
                M_u=max(max(candidatos_M), 0.0), V_u=max(candidatos_V),
                phi_flexion=proc["phi_flexion"], phi_corte=proc["phi_corte"],
                M_u_cedente=M_c, V_u_cedente=abs(V_c),
                M_u_reposo=M_r, V_u_reposo=None if V_r is None else abs(V_r),
                nota=nota))

    # --- contraste E.060 (estatica) ----------------------------------------
    e060 = {}

    def suma_e060(clave, M, V):
        M0, V0 = e060.get(clave, (0.0, 0.0))
        e060[clave] = (max(M0, M), max(V0, abs(V)))

    for juego in ((cargas, cargas0) if usa_reposo else (cargas,)):
        combos_e = _combinaciones_e060(juego, g.B)
        for s in solicitaciones_por_elemento(entorno, juego, combos_e, datos,
                                             marco=MARCO_E060):
            if s.elemento != ELEMENTO_ZAPATA:
                suma_e060(_clave_de(s), s.M_u, s.V_u)
        for combo_e in combos_e:
            # E.060 15.4.1: el momento de las fuerzas a un lado del plano,
            # con la reaccion del terreno (aqui, la misma presion lineal).
            z = solicitaciones_de_la_zapata(g, juego, combo_e, datos)
            if z is not None:
                suma_e060(SECCION_PUNTA, z["punta"][1], z["punta"][0])
                suma_e060(SECCION_TALON, z["talon"][1], z["talon"][0])

    # --- Servicio I, para la fisuracion de 5.6.7 (H3) ----------------------
    servicio = _momentos_de_servicio(entorno, cargas, datos)
    if usa_reposo:
        for clave, M in _momentos_de_servicio(entorno, cargas0,
                                              datos).items():
            servicio[clave] = max(servicio.get(clave, M), M)

    # --- Evento Extremo I ---------------------------------------------------
    sismico, datos_s = False, None
    cadena = cadena_sismica()
    k_h_armado = cadena.k_h0 if usa_reposo else None
    try:
        cargas_s, datos_s = cargas_del_cabezal(entorno, sis, k_h=k_h_armado)
        # --- dictamen Fable (VE-7 lote A, (i)) --- el armado lleva los
        # pesos ENTEROS: la reduccion por k_v es de la estabilidad.
        if any(c.codigo == C_EQ_KV for c in cargas_s):
            cargas_s = tuple(c for c in cargas_s if c.codigo != C_EQ_KV)
            avisos.append(
                f"{quien}: el Evento Extremo I del armado lleva los pesos "
                "enteros; la reduccion (1 - k_v) de los pesos solo entra en "
                "la estabilidad (E1 a E3)")
        combos_s = combinaciones_de_estabilidad(cargas_s, datos_s, sis, g.B)
        if datos_s.get("empuje_sismico_declarado"):
            d = datos_s["empuje_sismico_declarado"]
            avisos.append(
                f"{quien}: el Evento Extremo I del armado usa el empuje "
                f"sismico DECLARADO ({d['documento']}, k_h = {d['k_h']:g})"
                + NOTA_ARMADO_CON_EMPUJE_DECLARADO + " ("
                + ", ".join(CITAS_ARMADO_CON_EMPUJE_DECLARADO) + ")")
        ced_s = solicitaciones_por_elemento(entorno, cargas_s, combos_s,
                                            datos_s)
        sismico = True
    except ErrorProyecto as motivo:
        solo_el_armado = False
        if (usa_reposo and cadena.k_h < cadena.k_h0 - TOL_UMBRAL_NORMATIVO):
            try:
                cargas_del_cabezal(entorno, sis)
                solo_el_armado = True
            except ErrorProyecto:
                pass
        avisos.append(
            f"{quien}: el armado sale SOLO de Resistencia I. El Evento "
            "Extremo I no entro al armado porque sus cargas no son "
            f"evaluables ({motivo}); "
            + ("es el k_h = 1.0·k_h0 que AASHTO 11.6.5.4 exige al muro que "
               f"no cede (k_h0 = {cadena.k_h0:.3f}) el que no se puede "
               "evaluar: la estabilidad externa, con el k_h reducido "
               f"({cadena.k_h:.3f}), si lo esta, y el armado de este "
               "cabezal NO cubre el sismo. Reducir k_h no es remedio para "
               "el muro que no cede"
               if solo_el_armado else
               "la etapa de estabilidad sismica de ese cabezal lleva el "
               "bloqueo con la misma causa"))
    if sismico:
        phi_x = proc["phi_evento_extremo"]
        for combo in (c for c in combos_s if c.marco == MARCO_LRFD):
            for clave in secciones:
                M_r, V_r, nota = None, None, ""
                if clave in (SECCION_PUNTA, SECCION_TALON):
                    M_c, V_c, nota = zapata(clave, cargas_s, combo, datos_s)
                else:
                    a = de(ced_s, clave, combo.nombre)
                    M_c = None if a is None else a.M_u
                    V_c = None if a is None else a.V_u
                if M_c is None:
                    sin_presion.append(combo.nombre)
                    continue
                if clave in (SECCION_PANTALLA, SECCION_ALERO):
                    V_r, M_r = _pantalla_con_resultante_a_media_altura(
                        g, cargas_s, combo, datos_s, V_c, M_c)
                    nota = (f"resultante del empuje total a h/2 (AASHTO "
                            f"C11.6.5.4): M = {M_r:.2f} kN·m/m, V = "
                            f"{V_r:.2f} kN/m; en su posicion: M = "
                            f"{M_c:.2f}, V = {V_c:.2f}")
                if usa_reposo and M_r is not None:
                    M_u, V_u = max(M_c, M_r), max(abs(V_c), abs(V_r))
                else:
                    M_u, V_u = M_c, abs(V_c)
                secciones[clave].append(SolicitacionDeArmado(
                    combinacion=combo.nombre, condicion=sis,
                    M_u=max(M_u, 0.0), V_u=V_u, phi_flexion=phi_x,
                    phi_corte=phi_x, M_u_cedente=M_c, V_u_cedente=abs(V_c),
                    M_u_reposo=M_r,
                    V_u_reposo=None if V_r is None else abs(V_r),
                    nota=nota))
        if usa_reposo and cadena.k_h < cadena.k_h0 - TOL_UMBRAL_NORMATIVO:
            avisos.append(
                f"{quien}: el regimen de resistencia es el del muro que NO "
                f"cede ('{CRITERIO_REGIMEN_RESISTENCIA}' = '{regimen}'): el "
                f"Evento Extremo I del ARMADO va con k_h = 1.0·k_h0 = "
                f"{cadena.k_h0:.3f}, como manda AASHTO 11.6.5.4, aunque la "
                f"cadena sismica reduzca el de la estabilidad externa (k_h = "
                f"{cadena.k_h:.3f}, '{CRITERIO_FACTOR_MURO}'). La "
                "estabilidad puede admitir la reduccion; la resistencia de "
                "los elementos del muro que no cede, no")

    # --- lo que falta o no rige, dicho -------------------------------------
    if sin_presion and secciones[SECCION_PUNTA]:
        avisos.append(
            f"{quien}: en {len(sin_presion)} combinacion(es) la resultante "
            "cae fuera de la base y no hay presion de contacto con que "
            "armar la punta (" + "; ".join(sin_presion) + "): la punta se "
            "arma con las demas, y esa geometria no pasa su estabilidad")
    if reposo_sin_presion and secciones[SECCION_PUNTA]:
        avisos.append(
            f"{quien}: con el empuje en REPOSO factorado la resultante cae "
            "fuera de la base en «" + "»; «".join(reposo_sin_presion)
            + "»: esa combinacion no deja presion de contacto con que armar "
            "la punta y se DESCARTA (la punta se arma con la del empuje "
            "activo). Con K0 factorado ese cabezal vuelca: la geometria no "
            "es estable con el empuje con que se arma")
    for clave, nombre in ((SECCION_PUNTA, "la punta"),):
        if datos["punta"] > TOL_UMBRAL_NORMATIVO and not secciones[clave]:
            raise MetodoNoEvaluableError(
                f"solicitaciones de {nombre} de la zapata del cabezal de "
                f"{entorno.extremo}",
                "una zapata mas ancha (la resultante tiene que caer dentro "
                "de la base para que haya presion de contacto que integrar)",
                "en todas las combinaciones del marco que rige la resultante "
                "cae fuera de la base (B - 2e <= 0): el cabezal no pasa su "
                "estabilidad y no hay presion de contacto con que armar la "
                "punta",
                entorno.id_punto, rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)
    return {"regimen": regimen, "datos": datos, "datos_sismicos": datos_s,
            "sismico": sismico, "secciones": {k: tuple(v)
                                               for k, v in secciones.items()},
            "e060": e060, "servicio": servicio, "avisos": avisos,
            "K0": datos["K0"], "K_A": datos["K_A"],
            "k_h_armado": None if datos_s is None else datos_s["k_h"],
            "k_h_estabilidad": cadena.k_h}


# ---------------------------------------------------------------------------
# El diseño de UNA seccion: flexion, minimos, barra propuesta y cortante
# ---------------------------------------------------------------------------

def _condicion_de_recubrimiento(clave: str, diametro_mm: float,
                                catalogo: dict) -> str:
    """
    La fila del Art. 7.7.1 de E.060 de cada cara: la inferior de la zapata
    se vacia contra el suelo; las demas (trasdos de la pantalla y del alero,
    cara superior del talon) quedan en contacto permanente con el relleno,
    y su fila depende del diametro de la barra (3/4" y mayores, o 5/8" y
    menores).
    """
    if clave == SECCION_PUNTA:
        return CONDICION_RECUBRIMIENTO_ZAPATA
    grueso = catalogo["diametro_grueso"]
    if grueso is not None and diametro_mm >= grueso - TOL_UMBRAL_NORMATIVO:
        return CONDICION_RECUBRIMIENTO_BARRA_GRUESA
    return CONDICION_RECUBRIMIENTO_BARRA_FINA


def minimo_e060_por_cara(*, es_zapata: bool, direccion: str,
                         espesor: float, hm: Optional[float] = None,
                         lm: Optional[float] = None) -> Tuple[float, str]:
    """
    El acero minimo de E.060 para UNA cara, mm2 por metro, y su origen. Por
    analogia ([N→]): es el lado peruano de 'regla_minimos_constructivos_
    cabezal'.

      muro    la cuantia de 14.3.1 (0,0020 horizontal, 0,0015 vertical; con
              el regimen de cortante «en el plano» declarado, los pisos de
              11.10.10.2 y de la ec. 11-32) sobre el area bruta, repartida
              en las dos capas que 14.3.2 pide a partir de 200 mm.
      zapata  10.5.4: 0,0012 en la cara en traccion (`direccion` =
              'principal') y la mitad del 0,0018 de 9.7.2 en cada cara de la
              otra direccion ('reparto').
    """
    if not (_finito(espesor) and espesor > 0):
        raise DatoInvalidoError("espesor", valor=espesor,
                                motivo="espesor positivo y finito")
    bruta = espesor * MM2_POR_M2            # mm2 por metro de ancho
    if es_zapata:
        if direccion == "principal":
            return (CUANTIA_MIN_CARA_TRACCION_E060 * bruta,
                    "0,0012·b·h en la cara en traccion (E.060 10.5.4)")
        return (CUANTIA_MIN_LOSA_E060 * bruta / 2,
                "0,0018·b·h repartido en dos caras (E.060 9.7.2 y 10.5.4)")
    en_el_plano = (ca.valor(CRITERIO_REGIMEN_CORTANTE)
                   == REGIMEN_CORTANTE_EN_EL_PLANO)
    rho, numeral, _, _ = _minimo_de_cuantia_aplicable(
        direccion=direccion, cortante_alto=en_el_plano)
    if en_el_plano and direccion == "vertical" and hm and lm:
        rho_h, _, _, _ = _minimo_de_cuantia_aplicable(
            direccion="horizontal", cortante_alto=True)
        rho = cuantia_vertical_ec_11_32(hm=hm, lm=lm, rho_h=rho_h)
        numeral += " (ec. 11-32 evaluada)"
    capas = 2 if requiere_refuerzo_dos_capas(espesor=espesor) else 1
    return (rho * bruta / capas,
            f"{rho:g}·b·h en {capas} capa(s) ({numeral})")


def _verificacion_de_armado(*, fundamento: str, codigo: str, que: str,
                            formula: str, sustitucion: tuple,
                            resultado: Magnitud, descripcion_umbral: str,
                            admisible, unidad: str, cita: str,
                            aplicacion: str, criterio: str, cumple: bool,
                            margen: Optional[float], decide: bool,
                            obtenido, nota: str, explicacion_falla: str,
                            citas: Tuple[str, ...] = (),
                            numeral: str = NUMERAL_9_4_ARMADO,
                            indicador: str = "",
                            explicacion_cumple: str = "cumple",
                            caracter: Optional[str] = None
                            ) -> Verificacion:
    """
    Arma la `Verificacion` de una fila del armado y su paso. Si la fila NO
    decide (el contraste con E.060, o la que el criterio del ciclopeo deja
    de informe), un incumplimiento sale como INDICADOR. Una fila que cumple
    con un `indicador` disparado (correcciones de T-7c: el cortante de la
    pantalla sobre 0.5·phi·V_c) sale tambien como INDICADOR, con ese texto.
    """
    if cumple and indicador:
        tipo, texto = TipoDeVeredicto.INDICADOR, indicador
    elif cumple:
        tipo, texto = TipoDeVeredicto.CUMPLE, explicacion_cumple
    elif decide:
        tipo, texto = TipoDeVeredicto.NO_CUMPLE, explicacion_falla
    else:
        tipo, texto = TipoDeVeredicto.INDICADOR, (
            explicacion_falla + ". Esta fila NO decide: informa y no "
            "detiene el punto")
    kw = dict(codigo=codigo, que=que, formula=formula,
              sustitucion=sustitucion, resultado=resultado,
              citas_textuales=(cita,) + tuple(citas),
              umbral=Umbral(descripcion=descripcion_umbral, valor=admisible,
                            unidad=unidad, cita_id=cita,
                            caracter=caracter or _caracter_de(cita),
                            aplicacion=aplicacion,
                            criterio_aplicado=criterio),
              veredicto=Veredicto(tipo=tipo, margen=margen, unidad=unidad,
                                  explicacion=texto),
              nota_del_proyecto=nota)
    # El fundamento va LITERAL en cada rama (el indice de formulas localiza
    # al emisor por el literal).
    if fundamento == "F9.ARM_FLEXION":
        p = paso("F9.ARM_FLEXION", **kw)
    elif fundamento == "F9.ARM_CORTANTE":
        p = paso("F9.ARM_CORTANTE", **kw)
    elif fundamento == "F9.ARM_MINIMO":
        p = paso("F9.ARM_MINIMO", **kw)
    elif fundamento == "F9.ARM_ESPACIAMIENTO":
        p = paso("F9.ARM_ESPACIAMIENTO", **kw)
    elif fundamento == "F9.ARM_E060":
        p = paso("F9.ARM_E060", **kw)
    elif fundamento == "F9.ARM_FISURACION":
        p = paso("F9.ARM_FISURACION", **kw)
    elif fundamento == "F9.ARM_DURABILIDAD":
        p = paso("F9.ARM_DURABILIDAD", **kw)
    elif fundamento == "F9.ARM_PERALTE_ZAPATA":
        p = paso("F9.ARM_PERALTE_ZAPATA", **kw)
    else:
        p = paso("F9.CICLOPEO", **kw)
    return Verificacion(
        cumple=tipo is not TipoDeVeredicto.NO_CUMPLE, numeral=numeral,
        valor_obtenido=obtenido, valor_admisible=admisible,
        criterio_aplicado=criterio, codigo=codigo, paso=p)


def diseno_flexion_corte(*, momento: Optional[float] = None,
                         cortante: Optional[float] = None,
                         espesor: Optional[float] = None,
                         solicitaciones: Sequence[SolicitacionDeArmado] = (),
                         elemento: str = ELEMENTO_PANTALLA,
                         clave: str = SECCION_PANTALLA,
                         seccion: str = "arranque de la pantalla",
                         cara: str = "trasdos",
                         es_zapata: bool = False,
                         vuelo: Optional[float] = None,
                         ancho_seccion: Optional[float] = None,
                         hm: Optional[float] = None,
                         lm: Optional[float] = None,
                         regimen: str = "",
                         sufijo: str = "",
                         id_punto: Optional[str] = None,
                         contraste_e060: Optional[Tuple[float, float]] = None,
                         momento_servicio: Optional[float] = None,
                         contra_el_suelo: bool = False
                         ) -> ArmadoDeSeccion:
    """
    Diseño por flexion y corte de UNA seccion del cabezal, por metro de
    ancho, con AASHTO LRFD Seccion 5 (Sec. 9.4, via Manual de Puentes
    Seccion 2.9). Es la funcion que hasta T-7c se detenia con
    `NotImplementedError`.

    QUE RECIBE. Las solicitaciones factoradas de la seccion -- una
    `SolicitacionDeArmado` por combinacion, cada una con SU factor de
    resistencia (0.90 en Resistencia I, 1.0 en Evento Extremo I) -- o, para
    un tanteo, un solo par `momento` (kN·m/m) y `cortante` (kN/m) de
    Resistencia I. Y el `espesor` de la seccion (m).

    QUE HACE, en este orden:
      1. minimos de la cara en traccion: el acero de retraccion y
         temperatura de 5.10.6 y, con la regla del mas exigente, el de E.060
         (`minimo_e060_por_cara`); y el espaciamiento maximo
         (`espaciamiento_maximo_del_armado`);
      2. por cada barra del catalogo, desde la minima: recubrimiento de esa
         cara y esa barra (`recubrimiento_para_armar`), peralte efectivo d =
         h - recubrimiento - diametro/2, acero por resistencia (el mayor de
         los que pide cada combinacion con su phi), acero minimo de flexion
         de 5.6.3.3 -- el que desarrolla el menor de 1.33·M_u y M_cr -- y
         acero adoptado, el mayor de los tres; se queda con la primera barra
         que lo da con un espaciamiento de la serie no mayor que el maximo;
      3. con esa barra: resistencia nominal, deformacion neta del acero
         (tiene que llegar a 0.005 para que el factor 0.90 valga) y A1;
      4. cortante del concreto sin refuerzo transversal con el procedimiento
         SIMPLIFICADO si sus condiciones se cumplen (`simplificado_permitido`)
         y, si no, desde VE-3.14, con el GENERAL de 5.7.3.4.2 (β de la ec.
         5.7.3.4.2-2 por combinacion, `beta_procedimiento_general`), y A2;
      5. A3 (acero provisto frente al minimo), A4 (espaciamiento) y, si se
         le pasa `contraste_e060` = (M_u, V_u) de las combinaciones de E.060,
         A5: el aprovechamiento de la seccion en ese marco, que INFORMA;
      6. con `momento_servicio` (el de Servicio I), A6: la fisuracion de
         AASHTO 5.6.7 (`fisuracion_aashto`; correcciones de T-7c, H3). La
         clase de exposicion la declara el Propietario
         ('clase_exposicion_fisuracion_cabezal' [A], sin valor): declarada,
         A6 DECIDE y la barra propuesta la respeta; sin declarar, la
         propuesta respeta la Clase 1 -- la menos exigente, que cualquier
         clase pide («an upper bound in regards to crack width», C5.6.7) --
         y A6 imprime las dos: CUMPLE si el espaciamiento cumple tambien la
         Clase 2, INDICADOR «no decidida» si solo cumple la 1, NO CUMPLE si
         no cumple ninguna. Sin momento de servicio (un tanteo con un par
         M, V) A6 no se evalua y A4 lo dice.

    HASTA VE-3.14 SE DETENIA con `MetodoNoEvaluableError` (rotulo del
    armado) cuando la seccion quedaba fuera de las condiciones del
    simplificado, porque el general de 5.7.3.4.2 no estaba implementado (y
    aplicar beta = 2.0 a una seccion gruesa sin estribos es lo que el
    comentario de la fuente llama «seriously unconservative»). Desde VE-3.14
    (H-2 de los ensayos de diseño del cabezal) la verifica el general.

    Lo que NO hace: no cruza marcos (las resistencias de E.060 solo se
    comparan con cargas de E.060), no dimensiona estribos y no cambia el
    espesor: si ninguna barra del catalogo alcanza, A1 no cumple y lo dice.

    --- VE-5 (m8) --- `contra_el_suelo` arma la cara con el recubrimiento
    del concreto vaciado contra el suelo (la fila de la cara inferior de la
    zapata); lo usa la losa inferior del portico del marco
    (`M8.disenar_portico`), que reutiliza esta funcion.
    """
    ca.valor(CRITERIO_FLEXION_CORTE)
    if espesor is None:
        raise DatoFaltanteError(
            "espesor", id_punto=id_punto,
            detalle="el diseño por flexion y corte necesita el espesor de "
                    "la seccion, en m")
    if not (_finito(espesor) and espesor > 0):
        raise DatoInvalidoError("espesor", valor=espesor, id_punto=id_punto,
                                motivo="espesor positivo y finito")
    proc = _procedimiento()
    sols = tuple(solicitaciones)
    if not sols:
        if momento is None or cortante is None:
            raise DatoFaltanteError(
                "momento" if momento is None else "cortante",
                id_punto=id_punto,
                detalle="el diseño por flexion y corte necesita el momento "
                        "y el cortante factorados de la seccion, o la lista "
                        "de solicitaciones por combinacion")
        for nombre, x in (("momento", momento), ("cortante", cortante)):
            if not (_finito(x) and x >= 0):
                raise DatoInvalidoError(
                    nombre, valor=x, id_punto=id_punto,
                    motivo="solicitacion factorada no negativa y finita "
                           "(el signo lo dice la cara en traccion)")
        sols = (SolicitacionDeArmado(
            combinacion="Resistencia I (declarada)",
            condicion=CondicionAnalisis.ESTATICO, M_u=float(momento),
            V_u=float(cortante), phi_flexion=proc["phi_flexion"],
            phi_corte=proc["phi_corte"], M_u_cedente=float(momento),
            V_u_cedente=float(cortante)),)
    for s in sols:
        for nombre, x in (("M_u", s.M_u), ("V_u", s.V_u)):
            if not (_finito(x) and x >= 0):
                raise LimiteNumericoError(
                    nombre, valor=x,
                    motivo=f"la solicitacion de «{s.combinacion}» en {seccion} "
                           "no es un numero finito y no negativo")
    mat = materiales_del_armado()
    fc, fy = mat["fc"], mat["fy"]
    regla = _regla_de_minimos()
    catalogo = catalogo_de_barras()
    ancho = espesor if ancho_seccion is None else ancho_seccion
    codigo = lambda n: f"{n}.{clave}" + (f".{sufijo}" if sufijo else "")  # noqa: E731
    clase = clase_de_exposicion() if momento_servicio is not None else None
    clase_rige = clase or CLASE_EXPOSICION_1
    if momento_servicio is not None and not _finito(momento_servicio):
        raise LimiteNumericoError(
            "M_s", valor=momento_servicio, id_punto=id_punto,
            motivo=f"el momento de servicio de {seccion} no es finito")
    donde = f"{seccion}" + (f" ({id_punto})" if id_punto else "")

    # 1. minimos constructivos y espaciamiento maximo ------------------------
    s_max, origen_s = espaciamiento_maximo_del_armado(espesor=espesor,
                                                      regla=regla)
    As_ts = acero_de_temperatura_aashto(ancho=max(ancho, espesor),
                                        espesor=espesor, fy=fy)
    As_min_c, origen_min = As_ts, "retraccion y temperatura (AASHTO 5.10.6)"
    As_e060_min, origen_e060 = None, ""
    if regla == MINIMOS_MAS_EXIGENTE:
        As_e060_min, origen_e060 = minimo_e060_por_cara(
            es_zapata=es_zapata,
            direccion="principal" if es_zapata else "vertical",
            espesor=espesor, hm=hm, lm=lm)
        if As_e060_min > As_min_c:
            As_min_c, origen_min = As_e060_min, origen_e060

    # 2. barra por barra ------------------------------------------------------
    estaticas = [s for s in sols if s.condicion is CondicionAnalisis.ESTATICO]
    M_resistencia = max((s.M_u for s in estaticas), default=0.0)
    M_cr = momento_de_agrietamiento(espesor=espesor, fc=fc,
                                    gamma_3=mat["gamma_3"])
    M_minimo = (min(FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO * M_resistencia,
                    M_cr) if M_resistencia > 0 else 0.0)
    def admite_fisuracion(d, rec):
        """La condicion de 5.6.7 que la propuesta respeta, o None."""
        def admite(diametro, s, As_p):
            fis = fisuracion_aashto(
                M_s=momento_servicio, As=As_p, d=d, espesor=espesor,
                d_c=(rec + diametro / 2) / MILIMETROS_POR_METRO, fc=fc,
                fy=fy)
            return (not fis["aplica"]) or (
                fis["f_ss"] <= fis["f_ss_max"] + TOL_UMBRAL_NORMATIVO
                and s <= fis["s_max"][clase_rige] + TOL_UMBRAL_NORMATIVO)
        return admite

    def elegir(con_fisuracion: bool, piso: float = 0.0):
        elegido = None
        activo = False
        for diametro, area, nombre in catalogo["barras"]:
            activo = activo or nombre == catalogo["minima_principal"]
            if not activo:
                continue
            condicion = (CONDICION_RECUBRIMIENTO_ZAPATA if contra_el_suelo
                         else _condicion_de_recubrimiento(clave, diametro,
                                                          catalogo))
            rec, origen_rec, aviso_rec = recubrimiento_para_armar(
                condicion=condicion)
            d = espesor - (rec + diametro / 2) / MILIMETROS_POR_METRO
            if not d > 0:
                continue
            por_combo = [acero_por_flexion(M_u=s.M_u, d=d, fc=fc, fy=fy,
                                           phi=s.phi_flexion) for s in sols]
            alcanza = all(x is not None for x in por_combo)
            As_res = max(por_combo) if alcanza else None
            As_minf = acero_por_flexion(M_u=M_minimo, d=d, fc=fc, fy=fy,
                                        phi=proc["phi_flexion"])
            candidato = dict(nombre=nombre, diametro=diametro, area=area,
                             d=d, rec=rec, origen_rec=origen_rec,
                             aviso_rec=aviso_rec, condicion=condicion,
                             As_res=As_res, As_minf=As_minf, barra=None)
            if alcanza and As_minf is not None:
                adoptado = max(As_res, As_minf, As_min_c, piso)
                candidato["As_adoptado"] = adoptado
                unico = dict(catalogo, barras=((diametro, area, nombre),))
                candidato["barra"] = proponer_barra(
                    As=adoptado, s_max=s_max, catalogo=unico, desde=nombre,
                    admite=(admite_fisuracion(d, rec) if con_fisuracion
                            else None))
            elegido = candidato
            if candidato["barra"] is not None:
                break
        return elegido

    con_fisuracion = momento_servicio is not None

    def elegir_con_fisuracion(piso: float = 0.0):
        elegido = elegir(con_fisuracion, piso)
        if con_fisuracion and (elegido is None or elegido["barra"] is None):
            # Ninguna barra del catalogo cumple 5.6.7: se propone sin ella y
            # A6 lo dice; el acero y el espaciamiento de resistencia no
            # esperan.
            elegido = elegir(False, piso)
        return elegido

    def piso_por_cortante(eleg) -> float:
        """
        --- VE-3.14 --- El acero que el cortante del procedimiento GENERAL
        pide con la barra de `eleg` (0.0 si el simplificado aplica, si ya
        cumple o si ningun acero alcanza: entonces A2 lo dice y la salida
        es espesor).
        """
        if eleg is None or eleg["barra"] is None:
            return 0.0
        As_p = eleg["barra"].As_provisto
        r = resistencia_a_flexion(As=As_p, d=eleg["d"], fc=fc, fy=fy)
        c = cortante_del_concreto(d=eleg["d"], a=r["a"], espesor=espesor,
                                  fc=fc, beta=proc["beta_simplificado"])
        ok, _por = simplificado_permitido(es_zapata=es_zapata,
                                          espesor=espesor, vuelo=vuelo,
                                          d_v=c["d_v_letra"])
        if ok:
            return 0.0
        piso = 0.0
        for s in sols:
            necesario = acero_para_cortante_general(
                M_u=s.M_u, V_u=s.V_u, d_v=c["d_v"], phi=s.phi_corte,
                V_c_por_beta=c["V_c"] / proc["beta_simplificado"],
                V_tope=VN_TOPE_SOBRE_FC_AASHTO * fc * KPA_POR_MPA * c["d_v"])
            if necesario is None:
                return 0.0
            piso = max(piso, necesario)
        return piso if piso > As_p + TOL_UMBRAL_NORMATIVO else 0.0

    elegido = elegir_con_fisuracion()
    # --- VE-3.14 --- FUERA DEL SIMPLIFICADO, EL ACERO LONGITUDINAL TAMBIEN
    # LO PIDE EL CORTANTE: con el procedimiento general β depende de εs, y
    # εs del acero en traccion. Si el cortante no cumple con el acero de
    # flexion, el acero adoptado sube hasta el que lo hace cumplir (la ec.
    # 5.7.3.4.2-2 despejada, `acero_para_cortante_general`), como el
    # proyectista lo haria antes de engrosar la seccion; la seccion tiene
    # que seguir controlada por traccion (A1 lo verifica). Cada pasada solo
    # sube el piso y el catalogo es finito: termina.
    As_por_cortante = 0.0
    for _barra in catalogo["barras"]:
        piso = piso_por_cortante(elegido)
        if not piso > As_por_cortante + TOL_UMBRAL_NORMATIVO:
            break
        nuevo = elegir_con_fisuracion(piso)
        if nuevo is None or nuevo["barra"] is None:
            break
        elegido, As_por_cortante = nuevo, piso
    if elegido is None:
        raise DatoInvalidoError(
            "espesor", valor=espesor, id_punto=id_punto,
            motivo=f"con el recubrimiento de {seccion} ninguna barra del "
                   "catalogo deja peralte efectivo positivo")
    d, barra = elegido["d"], elegido["barra"]
    As_res, As_minf = elegido["As_res"], elegido["As_minf"]
    alcanza = As_res is not None and As_minf is not None
    As_adoptado = elegido.get("As_adoptado")
    if As_adoptado is None:
        As_adoptado = max(x for x in (As_res, As_minf, As_min_c)
                          if x is not None)
    As_minimo = max(As_min_c, As_minf or 0.0)
    if not alcanza:
        gobierna = "la seccion no alcanza"
    elif As_por_cortante > max(As_res, As_minimo) + TOL_UMBRAL_NORMATIVO:
        gobierna = ("cortante sin estribos, procedimiento general (AASHTO "
                    "5.7.3.4.2): mas acero longitudinal, menor εs")
    elif As_res >= As_minimo - TOL_UMBRAL_NORMATIVO:
        gobierna = "resistencia"
    elif (As_minf or 0.0) >= As_min_c:
        gobierna = "minimo de flexion (AASHTO 5.6.3.3)"
    else:
        gobierna = "minimo constructivo: " + origen_min
    As_provisto = barra.As_provisto if barra is not None else As_adoptado

    # 3. flexion con la barra propuesta --------------------------------------
    res = resistencia_a_flexion(As=As_provisto, d=d, fc=fc, fy=fy)
    eps = res["epsilon_t"]
    controlada = eps is None or eps >= EPSILON_TL_AASHTO - TOL_UMBRAL_NORMATIVO
    rige_M = max(sols, key=lambda s: s.M_u / s.phi_flexion)
    M_r = rige_M.phi_flexion * res["M_n"]
    cumple_M = (barra is not None and alcanza and controlada
                and all(s.phi_flexion * res["M_n"] >= s.M_u
                        - TOL_UMBRAL_NORMATIVO for s in sols))
    if barra is None:
        falla_M = ("ninguna barra del catalogo da el acero adoptado "
                   f"({As_adoptado:.0f} mm2/m) con un espaciamiento admisible"
                   if alcanza else
                   "el momento factorado supera lo que el bloque de "
                   "compresiones puede equilibrar con cualquier acero")
        falla_M += ": aumentar el espesor de la seccion"
    elif not controlada:
        falla_M = (f"la deformacion neta del acero ({eps:.4f}) no llega a "
                   f"{EPSILON_TL_AASHTO}: la seccion no esta controlada por "
                   "traccion y el factor 0.90 no vale; aumentar el espesor")
    else:
        falla_M = "M_u > M_r: aumentar el espesor o el acero"
    mag = lambda s, v, u, p, c=CIFRAS_MAGNITUD: Magnitud(s, v, u, p, cifras=c)  # noqa: E731
    v_flexion = _verificacion_de_armado(
        fundamento="F9.ARM_FLEXION", codigo=codigo("A1"),
        que=f"A1, flexion: {donde}, cara en traccion: {cara}",
        formula="M_r = phi·A_s·f_y·(d - a/2) >= M_u;  a = A_s·f_y / "
                "(0.85·f'c·b);  epsilon_t = 0.003·(d - c)/c >= 0.005",
        sustitucion=(
            mag("M_u", rige_M.M_u, "kN·m/m",
                f"{rige_M.combinacion}"
                + (f"; {rige_M.nota}" if rige_M.nota else "")),
            mag("phi", rige_M.phi_flexion, "",
                "AASHTO 5.5.4.2 (Resistencia I) o 1.3.2.1 (Evento Extremo "
                f"I), '{CRITERIO_FLEXION_CORTE}'", CIFRAS_FACTOR),
            mag("h", espesor, "m", "espesor de la seccion (geometria del "
                "cabezal)"),
            mag("recubrimiento", elegido["rec"], "mm", elegido["origen_rec"],
                1),
            mag("d", d, "m", "h - recubrimiento - diametro/2 de la barra "
                "propuesta"),
            mag("f'c", fc, "MPa", f"'{CRITERIO_FC_CABEZAL}' [A]", 1),
            mag("f_y", fy, "MPa", f"'{CRITERIO_ACERO_CABEZAL}' [A]: "
                f"{mat['acero']}", 0),
            mag("A_s", As_provisto, "mm2/m",
                barra.texto if barra is not None
                else "acero adoptado (sin barra del catalogo que lo de)", 0),
            mag("a", res["a"], "m", "A_s·f_y / (0.85·f'c·b)", CIFRAS_FINA),
            mag("epsilon_t", eps if eps is not None else 0.0, "",
                "0.003·(d - c)/c, c = a / beta_1" if eps is not None
                else "sin acero en traccion", CIFRAS_FINA),
        ),
        resultado=mag("M_r", M_r, "kN·m/m", "phi·A_s·f_y·(d - a/2)"),
        descripcion_umbral="M_u <= M_r, con la seccion controlada por "
                           "traccion",
        admisible=M_r, unidad="kN·m/m", cita="AASHTO_LRFD_9.5.6.3.2.1#MR",
        aplicacion="exigencia de la fuente que rige la resistencia (AASHTO "
                   "LRFD Seccion 5, [C])",
        criterio=CRITERIO_FLEXION_CORTE, cumple=cumple_M,
        margen=M_r - rige_M.M_u, decide=True, obtenido=rige_M.M_u,
        nota=("Rige la combinacion que mas acero pide; las demas se "
              "comprueban con su propio factor de resistencia. "
              f"Solicitaciones de la seccion: " + "; ".join(
                  f"{s.combinacion}: M_u = {s.M_u:.2f}, V_u = {s.V_u:.2f}"
                  for s in sols)),
        explicacion_falla=falla_M,
        citas=("AASHTO_LRFD_9.5.5.4.2#FLEXION",
               "AASHTO_LRFD_9.5.6.2.1#TRACCION"))

    # 4. cortante -------------------------------------------------------------
    cort = cortante_del_concreto(d=d, a=res["a"], espesor=espesor, fc=fc,
                                 beta=proc["beta_simplificado"])
    # Las condiciones de 5.7.3.4.1 se leen con el d_v de la LETRA de 5.7.2.8
    # (la aplicabilidad del metodo es de la fuente); la resistencia, con el
    # acotado al peralte efectivo (H8).
    permitido, por_cual = simplificado_permitido(
        es_zapata=es_zapata, espesor=espesor, vuelo=vuelo,
        d_v=cort["d_v_letra"])
    # --- VE-3.14 (H-2 de los ensayos de diseño del cabezal) --- FUERA DEL
    # SIMPLIFICADO, EL PROCEDIMIENTO GENERAL. Hasta VE-3.14 la seccion se
    # detenia aqui con «metodo no evaluable» y el dimensionamiento del
    # peralte la saltaba aunque nada fallara. Hoy β sale de la ec.
    # 5.7.3.4.2-2 (seccion sin el refuerzo transversal minimo), una por
    # COMBINACION, porque depende de M_u y V_u (`beta_procedimiento_general`).
    general = {}
    if permitido:
        V_n_de = {id(s): cort["V_n"] for s in sols}
        V_c_de = {id(s): cort["V_c"] for s in sols}
        beta_de = {id(s): proc["beta_simplificado"] for s in sols}
    else:
        V_n_de, V_c_de, beta_de = {}, {}, {}
        for s in sols:
            g = beta_procedimiento_general(M_u=s.M_u, V_u=s.V_u,
                                           d_v=cort["d_v"], A_s=As_provisto)
            c_s = cortante_del_concreto(d=d, a=res["a"], espesor=espesor,
                                        fc=fc, beta=g["beta"])
            general[id(s)] = g
            V_n_de[id(s)], V_c_de[id(s)] = c_s["V_n"], c_s["V_c"]
            beta_de[id(s)] = g["beta"]
    rige_V = min(sols, key=lambda s: s.phi_corte * V_n_de[id(s)] - s.V_u)
    if not permitido:
        cort = dict(cort, V_c=V_c_de[id(rige_V)], V_n=V_n_de[id(rige_V)])
    V_r = rige_V.phi_corte * V_n_de[id(rige_V)]
    cumple_V = all(s.phi_corte * V_n_de[id(s)] >= s.V_u - TOL_UMBRAL_NORMATIVO
                   for s in sols)
    mitad = rige_V.phi_corte * cort["V_c"] / 2
    # Pregunta 4 del cierre de T-7c: la pantalla (y el alero) se tratan como
    # LOSA frente a AASHTO 5.7.2.3 y no se les pide refuerzo transversal;
    # cuando el cortante pasa de 0.5·phi·V_c, A2 sale como INDICADOR y no
    # como CUMPLE a secas.
    indicador_V = (
        f"cumple V_u <= phi·V_n, pero V_u = {rige_V.V_u:.1f} kN/m supera "
        f"0.5·phi·V_c = {mitad:.1f} kN/m: AASHTO 5.7.2.3, leido a la letra, "
        "pediria refuerzo transversal fuera de losas, zapatas y "
        "alcantarillas; el proyecto trata la pantalla como losa "
        "(interpretacion de la cita AASHTO_LRFD_9.5.7.2.3#TRANSVERSAL)"
        if (not es_zapata and cumple_V
            and rige_V.V_u > mitad + TOL_UMBRAL_NORMATIVO) else "")
    v_cortante = _verificacion_de_armado(
        fundamento="F9.ARM_CORTANTE", codigo=codigo("A2"),
        que=f"A2, cortante sin refuerzo transversal: {donde}",
        formula=("V_r = phi·V_n >= V_u;  V_n = min(V_c, 0.25·f'c·b_v·d_v);  "
                 "V_c = 0.0316·beta·sqrt(f'c)·b_v·d_v (ksi, in), "
                 + ("beta = 2.0 (5.7.3.4.1)" if permitido else
                    "beta = [4.8/(1 + 750·eps_s)]·[51/(39 + s_xe)] (ec. "
                    "5.7.3.4.2-2), eps_s = (|M_u|/d_v + |V_u|)/(E_s·A_s) "
                    "(ec. 5.7.3.4.2-4), s_xe = s_x·1.38/(a_g + 0.63) "
                    "(ec. 5.7.3.4.2-7), s_x = d_v, a_g = 0")),
        sustitucion=(
            mag("V_u", rige_V.V_u, "kN/m", rige_V.combinacion),
            mag("phi", rige_V.phi_corte, "", "AASHTO 5.5.4.2 o 1.3.2.1",
                CIFRAS_FACTOR),
            mag("d_v", cort["d_v"], "m", "min[max(d - a/2, 0.9·d, 0.72·h), "
                "d]: el de la letra de AASHTO 5.7.2.8 acotado al peralte "
                "efectivo (interpretacion de la cita AASHTO_LRFD_9.5.7.2.8#DV)"
                + ("" if abs(cort["d_v_letra"] - cort["d_v"])
                   <= TOL_UMBRAL_NORMATIVO else
                   f"; la letra daria {cort['d_v_letra']:.4f} m")),
            mag("beta", beta_de[id(rige_V)], "",
                f"procedimiento simplificado de 5.7.3.4.1, permitido por: "
                f"{por_cual}" if permitido else
                "procedimiento general de 5.7.3.4.2 (ec. 5.7.3.4.2-2), "
                f"porque el simplificado no aplica: {por_cual}",
                CIFRAS_FACTOR),
            *(() if permitido else (
                mag("eps_s", general[id(rige_V)]["eps_s"], "",
                    "(max(M_u, V_u·d_v)/d_v + V_u)/(E_s·A_s), ec. "
                    "5.7.3.4.2-4, con la barra propuesta", CIFRAS_FINA),
                mag("s_xe", general[id(rige_V)]["s_xe_in"], "in",
                    "s_x·1.38/(a_g + 0.63) con s_x = d_v y a_g = 0 (cota "
                    "inferior: interpretacion de la cita "
                    "AASHTO_LRFD_9.5.7.3.4.2#SXE), en [12, 80] in",
                    CIFRAS_FACTOR))),
            mag("V_c", cort["V_c"], "kN/m",
                f"{VC_COEFICIENTE_AASHTO_SI:.4f}·beta·sqrt(f'c [MPa])·d_v, "
                "en SI"),
        ),
        resultado=mag("V_r", V_r, "kN/m", "phi·V_n"),
        descripcion_umbral="V_u <= V_r", admisible=V_r, unidad="kN/m",
        cita="AASHTO_LRFD_9.5.7.3.3#VN",
        aplicacion="exigencia de la fuente que rige la resistencia (AASHTO "
                   "LRFD Seccion 5, [C]); el cortante se toma en la cara "
                   "del apoyo, sin reducirlo a d_v de ella",
        criterio=CRITERIO_FLEXION_CORTE, cumple=cumple_V,
        margen=V_r - rige_V.V_u, decide=True, obtenido=rige_V.V_u,
        nota=("Sin refuerzo transversal: si no cumple, la salida es mas "
              "espesor, no estribos (el programa no los dimensiona)."
              + ("" if permitido else
                 " Procedimiento general: cada combinacion con su β, " +
                 "; ".join(f"{s.combinacion}: β = {beta_de[id(s)]:.3f}, "
                           f"phi·V_n = {s.phi_corte * V_n_de[id(s)]:.1f} "
                           f"frente a V_u = {s.V_u:.1f} kN/m" for s in sols)
                 + ".")),
        explicacion_falla="V_u > phi·V_n: aumentar el espesor de la seccion",
        indicador=indicador_V,
        citas=(("AASHTO_LRFD_9.5.7.3.4.1#SIMPLIFICADO",) if permitido else
               ("AASHTO_LRFD_9.5.7.3.4.1#SIMPLIFICADO",
                "AASHTO_LRFD_9.5.7.3.4.2#GENERAL",
                "AASHTO_LRFD_9.5.7.3.4.2#MU",
                "AASHTO_LRFD_9.5.7.3.4.2#SXE",
                "AASHTO_LRFD_9.5.7.3.4.2#SX",
                "AASHTO_LRFD_9.C5.7.3.4.2#NEGATIVO"))
              + ("AASHTO_LRFD_9.5.7.2.8#DV", "AASHTO_LRFD_9.5.5.4.2#CORTE"))
    avisos = []
    if elegido["aviso_rec"]:
        avisos.append(elegido["aviso_rec"])
    if not es_zapata and rige_V.V_u > mitad + TOL_UMBRAL_NORMATIVO:
        avisos.append(
            f"{donde}: el cortante factorado ({rige_V.V_u:.1f} kN/m) supera "
            f"la mitad de la resistencia del concreto (0.5·phi·V_c = "
            f"{mitad:.1f} kN/m). El proyecto trata la pantalla como una losa "
            "y no le pide refuerzo transversal; leido a la letra, AASHTO "
            "5.7.2.3 solo exceptua losas, zapatas y alcantarillas "
            "(interpretacion de la cita AASHTO_LRFD_9.5.7.2.3#TRANSVERSAL)")
    if cort["d_v_letra"] > cort["d_v"] + TOL_UMBRAL_NORMATIVO:
        avisos.append(
            f"{donde}: el peralte de cortante de la letra de AASHTO 5.7.2.8 "
            f"(0.72·h = {cort['d_v_letra']:.3f} m) supera el peralte "
            f"efectivo (d = {d:.3f} m): el proyecto lo acota a d y la "
            f"resistencia del concreto baja de "
            f"{cort['V_c'] * cort['d_v_letra'] / cort['d_v']:.1f} a "
            f"{cort['V_c']:.1f} kN/m (interpretacion de la cita "
            "AASHTO_LRFD_9.5.7.2.8#DV)")

    # 5. minimo, espaciamiento y contraste -----------------------------------
    v_minimo = _verificacion_de_armado(
        fundamento="F9.ARM_MINIMO", codigo=codigo("A3"),
        que=f"A3, acero minimo de la cara en traccion: {donde}",
        formula="A_s provisto >= max(A_s de min(1.33·M_u, M_cr), A_s de "
                "retraccion y temperatura, A_s minimo de E.060)",
        sustitucion=(
            mag("M_cr", M_cr, "kN·m/m", "gamma_3·gamma_1·f_r·b·h²/6 "
                f"(AASHTO 5.6.3.3; gamma_3 = {mat['gamma_3']:g})"),
            mag("1.33·M_u", FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO
                * M_resistencia, "kN·m/m", "con el M_u de Resistencia I"),
            mag("A_s,min flexion", As_minf if As_minf is not None else 0.0,
                "mm2/m", "el que desarrolla el menor de los dos momentos", 0),
            mag("A_s,temperatura", As_ts, "mm2/m",
                "AASHTO 5.10.6, por cara y direccion", 0),
            mag("A_s,min E.060", As_e060_min if As_e060_min is not None
                else 0.0, "mm2/m",
                origen_e060 if As_e060_min is not None else
                f"no se aplica ('{CRITERIO_REGLA_MINIMOS}' = '{regla}')", 0),
            mag("A_s,resistencia", As_res if As_res is not None else 0.0,
                "mm2/m", "el que pide el momento que rige", 0),
        ),
        resultado=mag("A_s provisto", As_provisto, "mm2/m",
                      barra.texto if barra is not None else
                      "sin barra del catalogo", 0),
        descripcion_umbral="A_s provisto >= A_s minimo", admisible=As_minimo,
        unidad="mm2/m", cita="AASHTO_LRFD_9.5.6.3.3#MINIMO",
        aplicacion="el mas exigente de los minimos de AASHTO y de E.060 "
                   f"('{CRITERIO_REGLA_MINIMOS}' [A]); el de E.060, por "
                   "analogia",
        criterio=CRITERIO_REGLA_MINIMOS,
        cumple=barra is not None and As_provisto >= As_minimo
        - TOL_UMBRAL_NORMATIVO,
        margen=As_provisto - As_minimo, decide=True, obtenido=As_provisto,
        nota=f"Gobierna el acero adoptado: {gobierna}.",
        explicacion_falla="el acero provisto no alcanza el minimo",
        citas=("AASHTO_LRFD_9.5.10.6#TEMPERATURA", "E060.14.3.1",
               "E060.10.5.4#LOSAS"))
    s_prop = barra.espaciamiento if barra is not None else s_max
    v_espaciamiento = _verificacion_de_armado(
        fundamento="F9.ARM_ESPACIAMIENTO", codigo=codigo("A4"),
        que=f"A4, espaciamiento de la barra propuesta: {donde}",
        formula="s <= min(1.5·h, 18.0 in, tope del acero de temperatura, "
                "3·h, 400 mm)",
        sustitucion=(
            mag("h", espesor, "m", "espesor de la seccion"),
            mag("barra", barra.designacion if barra is not None else "-",
                "", f"catalogo '{CRITERIO_CATALOGO_BARRAS}' [A]: la "
                "primera, desde la minima, que da el acero adoptado"),
        ),
        resultado=mag("s", s_prop, "m", "el mayor de la serie del catalogo "
                      "que cumple"),
        descripcion_umbral="s <= s maximo", admisible=s_max, unidad="m",
        cita="AASHTO_LRFD_9.5.10.3.2#ESPACIAMIENTO",
        aplicacion=f"gobierna: {origen_s}",
        criterio=CRITERIO_REGLA_MINIMOS,
        cumple=barra is not None and s_prop <= s_max + TOL_UMBRAL_NORMATIVO,
        margen=s_max - s_prop, decide=True, obtenido=s_prop,
        nota=("Los topes de espaciamiento de 5.10.3.2, 5.10.6 y E.060 "
              "14.3.3. El control de fisuracion de AASHTO 5.6.7, que puede "
              "pedir un espaciamiento menor, es la fila A6"
              if momento_servicio is not None else
              "Los topes de espaciamiento de 5.10.3.2, 5.10.6 y E.060 "
              "14.3.3. El control de fisuracion de AASHTO 5.6.7 NO se evalua "
              "en esta seccion: no se le paso el momento de servicio, y "
              "puede pedir un espaciamiento menor"),
        explicacion_falla="no hay barra del catalogo con espaciamiento "
                          "admisible",
        citas=("AASHTO_LRFD_9.5.10.6#ESPACIAMIENTO", "E060.14.3.3"))
    verificaciones = [v_flexion, v_cortante, v_minimo, v_espaciamiento]

    # 6. fisuracion de AASHTO 5.6.7 (H3) ------------------------------------
    fis = None
    if momento_servicio is not None:
        diametro_fis = (barra.diametro_mm if barra is not None
                        else elegido["diametro"])
        fis = fisuracion_aashto(
            M_s=momento_servicio, As=As_provisto, d=d, espesor=espesor,
            d_c=(elegido["rec"] + diametro_fis / 2) / MILIMETROS_POR_METRO,
            fc=fc, fy=fy)
        verificaciones.append(_fila_de_fisuracion(
            fis=fis, s_prop=s_prop, clase=clase, codigo=codigo("A6"),
            donde=donde, M_s=momento_servicio, As=As_provisto,
            rec=elegido["rec"], barra=barra))

    M_e, V_e, As_e, V_r_e = None, None, None, None
    if contraste_e060 is not None:
        M_e, V_e = contraste_e060
        As_e = acero_por_flexion(M_u=M_e, d=d, fc=fc, fy=fy,
                                 phi=PHI_FLEXION_E060, alfa=ALFA_BLOQUE_E060)
        V_r_e = (PHI_CORTE_E060 * VC_COEFICIENTE_E060 * math.sqrt(fc)
                 * KPA_POR_MPA * d)
        res_e = resistencia_a_flexion(As=As_provisto, d=d, fc=fc, fy=fy,
                                      alfa=ALFA_BLOQUE_E060,
                                      beta_1=beta_1_e060(fc))
        eps_e = res_e["epsilon_t"]
        uso_M = (As_e / As_provisto) if (As_e is not None
                                         and As_provisto > 0) else None
        uso_V = V_e / V_r_e
        ductil = eps_e is None or eps_e >= EPSILON_T_MIN_E060 \
            - TOL_UMBRAL_NORMATIVO
        cumple_e = (uso_M is not None and uso_M <= 1 + TOL_UMBRAL_NORMATIVO
                    and uso_V <= 1 + TOL_UMBRAL_NORMATIVO and ductil)
        uso = max(uso_V, uso_M) if uso_M is not None else uso_V
        verificaciones.append(_verificacion_de_armado(
            fundamento="F9.ARM_E060", codigo=codigo("A5"),
            que=f"A5, contraste con E.060 (por analogia): {donde}",
            formula="A_s (E.060, phi = 0,90) / A_s provisto <= 1  y  V_u "
                    "(E.060) / (0,85·0,17·sqrt(f'c)·b·d) <= 1",
            sustitucion=(
                mag("M_u (E.060)", M_e, "kN·m/m",
                    "la mayor de 1,4 CM + 1,7 CV + 1,7 CE y 0,9 CM + 1,7 CE "
                    "(9.2.5), sobre las mismas cargas sin factorar"),
                mag("V_u (E.060)", V_e, "kN/m", "idem"),
                mag("A_s (E.060)", As_e if As_e is not None else 0.0,
                    "mm2/m", "flexion con phi = 0,90 y bloque de 0,85·f'c "
                    "(10.2.7)" if As_e is not None else
                    "la seccion no alcanza en el marco de E.060", 0),
                mag("phi·V_c (E.060)", V_r_e, "kN/m",
                    "0,85·0,17·sqrt(f'c)·b·d (9.3.2.3 y ec. 11-3)"),
                mag("epsilon_t (E.060)", eps_e if eps_e is not None else 0.0,
                    "", "con el acero provisto; 10.3.5 pide >= 0,004",
                    CIFRAS_FINA),
            ),
            resultado=mag("aprovechamiento", uso, "",
                          "el mayor de los dos cocientes", CIFRAS_FACTOR),
            descripcion_umbral="aprovechamiento <= 1 en el marco de E.060",
            admisible=1.0, unidad="", cita="E060.9.2.5#EMPUJE",
            aplicacion="contraste por analogia ([N→]): E.060 es norma de "
                       "edificaciones; informa y no decide el armado",
            criterio=CRITERIO_REGLA_MINIMOS, cumple=cumple_e,
            margen=1.0 - uso, decide=False, obtenido=uso,
            nota=("Cargas de E.060 con resistencias de E.060: los dos "
                  "marcos no se cruzan. Bajo sismo E.060 no escribe una "
                  "combinacion con empuje de suelos, y el contraste es solo "
                  "estatico."),
            explicacion_falla=("con las combinaciones y los factores de "
                               "E.060 la seccion queda por encima de su "
                               "resistencia"),
            citas=("E060.9.3.1#PHI", "E060.11.3.1#VC",
                   "E060.10.3.4#MAXIMO")))
        if not cumple_e:
            avisos.append(
                f"{donde}: el CONTRASTE con E.060 no cumple "
                f"(aprovechamiento {uso:.2f}): con sus combinaciones (1,7 "
                "sobre el empuje) y sus factores la seccion pide mas que el "
                "armado que sale de AASHTO. No decide; se informa")
    return ArmadoDeSeccion(
        elemento=elemento, clave=clave, seccion=seccion, cara=cara,
        espesor=espesor, recubrimiento_mm=elegido["rec"],
        origen_recubrimiento=elegido["origen_rec"], d=d, regimen=regimen,
        solicitaciones=sols, rige_flexion=rige_M, rige_cortante=rige_V,
        As_resistencia=As_res if As_res is not None else 0.0,
        As_minimo_flexion=As_minf if As_minf is not None else 0.0,
        As_minimo_constructivo=As_min_c, origen_minimo=origen_min,
        As_adoptado=As_adoptado, gobierna=gobierna, s_max=s_max,
        origen_s_max=origen_s, barra=barra, M_r=M_r, epsilon_t=eps,
        d_v=cort["d_v"], V_c=cort["V_c"], V_r=V_r, M_u_e060=M_e,
        V_u_e060=V_e, As_e060=As_e, V_r_e060=V_r_e,
        M_servicio=momento_servicio,
        fisuracion_aplica=None if fis is None else fis["aplica"],
        f_ss=None if fis is None else fis["f_ss"],
        s_fisuracion=None if fis is None else dict(fis["s_max"]),
        clase_exposicion=clase, d_v_letra=cort["d_v_letra"],
        verificaciones=tuple(verificaciones),
        pasos=tuple(v.paso for v in verificaciones), avisos=tuple(avisos))
