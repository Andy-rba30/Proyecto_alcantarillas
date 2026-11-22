# -*- coding: utf-8 -*-
"""
M9_cabezal.estabilidad_cargas
=============================
Submodulo de Fase 9 (`M9_cabezal`): bloque `estabilidad_cargas` (D1).
"""

from __future__ import annotations

import math
from typing import Any, Optional, Tuple

from src import criterios_adoptados as ca
from src.constantes_fisicas import GAMMA_AGUA_KN_M3
from src.constantes_normativas import (
    CW_NIVEL_FREATICO_T10_6_3_1_2A_2,
    CW_PROFUNDIDAD_SIN_EFECTO_VECES_B,
    DQ_MAXIMO_10_6_3_1_2A_10,
    ETA_PISO_GAMMA_MAXIMO_AASHTO,
    ETA_TECHO_GAMMA_MINIMO_AASHTO,
    FACTOR_MURO_CON_REDUCCION,
    FORMA_SC_PHI_CERO_DIVISOR,
    FORMA_SGAMMA_COEFICIENTE,
    FS_CODIGO,
    P_SEIS_COMBINACIONES,
    P_SEIS_PISO_ESTATICO,
    TABLA_GAMMA_P_FILAS,
    TALUD_QUEBRADO_DISTANCIA_VECES_H,
)
from src.modelos import (
    CARGA_DC,
    CARGA_EH,
    CARGA_EQ,
    CARGA_EV,
    CARGA_LS,
    CARGA_WA,
    CargaDeCabezal,
    CombinacionDeEstabilidad,
    CondicionAnalisis,
    DatoFaltanteError,
    DatoInvalidoError,
    ELEMENTO_PANTALLA,
    ELEMENTO_ZAPATA,
    EntornoDelCabezal,
    LimiteNumericoError,
    MARCO_ASD,
    MARCO_ENVOLVENTE,
    MARCO_LRFD,
    MARCO_RIGE_LRFD,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL,
    MetodoNoEvaluableError,
    REGLAS_DE_MARCO,
)
from src.tolerancias import (
    TOL_ANGULO_CUNA,
    TOL_UMBRAL_NORMATIVO,
    TRAMOS_CUNA_DE_TANTEO,
)

from src.modulos.M9_cabezal._criterios import (
    CRITERIO_BRAZO_SISMICO,
    CRITERIO_DELTA_MURO,
    CRITERIO_FACTOR_MURO,
    CRITERIO_GAMMA_CONCRETO,
    CRITERIO_GAMMA_EQ,
    CRITERIO_GAMMA_RELLENO,
    CRITERIO_I_RELLENO,
    CRITERIO_PHI_RELLENO,
    CRITERIO_PORTANTE_ADMISIBLE,
    CRITERIO_REGIMEN_RESISTENCIA,
    CRITERIO_TALUD_TERRAPLEN,
    EXTREMOS,
    FILA_EH_EN_REPOSO,
    LADOS_DEL_TRIANGULO,
    PHI_MAX_TABLA_GRADOS,
    _exigir_finito,
    _exigir_positivo,
    _finito,
)
from src.modulos.M9_cabezal.empujes import (
    angulo_inercia_sismica,
    cadena_sismica,
    empuje_activo_sismico_total,
    h_eq_del_cabezal,
    k_a_coulomb,
    k_ae_mononobe_okabe,
    peso_especifico_relleno,
)
from src.modulos.M9_cabezal.estabilidad_base import (
    factores_de_capacidad_de_carga,
    factores_de_carga,
    gamma_eq,
    parametros_resistencia_art20,
)

# ===========================================================================
# --- T-7b --- 9.2 y 9.3 EL ENSAMBLE DE ESTABILIDAD, POR CABEZAL Y EN DOS
# MARCOS QUE NO SE CRUZAN
# ===========================================================================
# Cierra INF-4.4, INF-4.5 e INF-5.1.5 y las fichas EXT-7-02 y EXT-7-04 (la
# EXT-7-03 no tenia nada que cerrar y la EXT-7-01 es del armado, de T-7c). Hasta
# aqui M9 era una caja de herramientas: daba los factores de carga del marco
# de estados limite (`factores_de_carga`) junto a verificaciones que comparan
# con los factores de seguridad de E.050 (`verificar_volteo`...), sin decir
# que cargas recibia cada una, y ninguna corrida las ensamblaba. Desde T-7b:
#
#   * el cabezal de CADA EXTREMO de cada punto dimensionado se verifica en
#     DOS MARCOS, cada uno con SUS cargas y SUS resistencias:
#       LRFD  AASHTO LRFD 11.6: cargas FACTORADAS (gamma maximos para el
#             portante; minimos de lo que estabiliza para el deslizamiento y
#             la excentricidad) contra resistencias MINORADAS por phi, y la
#             EXCENTRICIDAD de la resultante en lugar del volteo;
#       ASD   E.050 Art. 21 y 39.13.6, por analogia: cargas de SERVICIO
#             (todos los factores 1) contra la resistencia nominal dividida
#             por su FACTOR DE SEGURIDAD.
#     Cual RIGE lo declara 'marco_estabilidad_cabezal' [A] (decision del
#     dueño: rige LRFD y ASD informa); las verificaciones del marco que no
#     rige salen como INDICADOR y no detienen el punto;
#   * el empuje es el de COULOMB sobre el plano vertical del talon (AASHTO
#     C3.11.5.3), DESCOMPUESTO: la componente horizontal empuja y vuelca, la
#     vertical carga la base (EXT-7-04);
#   * el agua NO se cuenta dos veces: bajo su nivel el suelo empuja con su
#     peso sumergido y el agua aparte (AASHTO 3.11.3); hasta donde sube lo
#     declara 'drenaje_trasdos' (era la desviacion que declaraba
#     `HIPOTESIS_EMPUJE_BAJO_NF`);
#   * los cuatro angulos dejan de detener el caso estatico: phi es del
#     ensayo del relleno, delta sale de phi por una fraccion [C], i de la
#     GEOMETRIA de cada cabezal y beta del muro (punto 5 del encargo);
#   * la demanda sismica se ensambla entera: Mononobe-Okabe dentro de su
#     dominio de validez (AASHTO 11.6.5.3) y la inercia del muro, en los dos
#     casos del 11.6.5.1, con la excentricidad sismica (E6 de antes) como la
#     fila E2 del marco LRFD (EXT-7-02);
#   * E4 y E5 (estabilidad global y del talud) se IMPRIMEN como diferidas al
#     expediente con el EMS: ya no terminan en un AssertionError.
#
# EL MODELO, que es una HIPOTESIS y se dice: el cabezal se calcula como un
# muro de semigravedad en voladizo, por metro de muro, en la seccion llena
# junto al conducto. No se descuenta el vano del conducto ni se cuenta la
# restriccion que el barril y los aleros le dan; no se cuenta empuje pasivo
# delante de la zapata (AASHTO 11.6.3.5) ni el agua del cauce contra la cara
# frontal, que estabiliza: la condicion critica es el cauce vacio.
#
# LA INTERFAZ PARA T-7c: `EstabilidadDelCabezal.cargas` (cada carga sin
# factorar, con su brazo y el elemento al que llega) y `.combinaciones` (los
# factores de cada una), y `solicitaciones_por_elemento`, que entrega el
# cortante y el momento factorados de la pantalla y de la zapata (punta y
# talon) para cada combinacion del marco LRFD.

from src.constantes_normativas import (  # noqa: E402
    C_DESLIZAMIENTO_10_6_3_4, CW_NIVEL_FREATICO_T10_6_3_1_2A_2,
    CW_PROFUNDIDAD_SIN_EFECTO_VECES_B, ETA_OTROS_ESTADOS_LIMITE_AASHTO,
    ETA_PISO_GAMMA_MAXIMO_AASHTO, ETA_TECHO_GAMMA_MINIMO_AASHTO,
    EXCENTRICIDAD_ESTATICA_FRACCION_B, NUMERAL_ETA_DUCTILIDAD_AASHTO,
    NUMERAL_ETA_REDUNDANCIA_AASHTO, NUMERAL_MODIFICADOR_DE_CARGA_AASHTO,
    FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1,
    NUMERAL_CAPACIDAD_PORTANTE_AASHTO, NUMERAL_DESLIZAMIENTO_AASHTO,
    NUMERAL_EXCENTRICIDAD_ESTATICA_AASHTO, NUMERAL_PHI_EVENTO_EXTREMO,
    NUMERAL_PHI_MUROS, NUMERAL_PHI_ZAPATAS, PHI_EVENTO_EXTREMO_11_5_8,
    PHI_MUROS_T11_5_7_1, PHI_ZAPATAS_T10_5_5_2_2_1,
    TALUD_QUEBRADO_DISTANCIA_VECES_H, FS_NOMBRE_DE_LA_CONDICION,
    NUMERAL_PHI_ESTABILIDAD_GLOBAL, PHI_ESTABILIDAD_GLOBAL_11_6_3_7)
from src.modelos import (  # noqa: E402
    CARGA_DC, CARGA_EH, CARGA_EQ, CARGA_EV, CARGA_LS, CARGA_WA,
    ELEMENTO_ALEROS, ELEMENTO_PANTALLA, ELEMENTO_ZAPATA,
    ELEMENTO_ZAPATA_ALEROS, MURO_ALERO, MURO_CABEZAL, MARCO_ASD,
    MARCO_ENVOLVENTE, MARCO_LRFD, MARCO_RIGE_ASD, MARCO_RIGE_LRFD,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL, REGLAS_DE_MARCO, CargaDeCabezal,
    CombinacionDeEstabilidad, CriterioPendienteError, DatoFaltanteError,
    EntornoDelCabezal, ErrorProyecto, EstabilidadDelCabezal,
    MetodoNoEvaluableError, SolicitacionDeElemento)

CRITERIO_MARCO = "marco_estabilidad_cabezal"


CRITERIO_FILA_PHI = "fila_phi_estabilidad_cabezal"


# --- VE-4a --- la fila de phi de 11.6.3.7 para el FS declarado de E4 y E5.
CRITERIO_FILA_PHI_GLOBAL = "fila_phi_estabilidad_global"


CRITERIO_DRENAJE = "drenaje_trasdos"


# --- VE-3.14 (H-3) --- el agua del relleno bajo sismo (C11.6.5.3).
CRITERIO_AGUA_SISMO = "agua_del_relleno_bajo_sismo"


AGUA_SE_MUEVE_CON_EL_SUELO = "se_mueve_con_el_suelo"


AGUA_RELLENO_MUY_ABIERTO = "relleno_muy_abierto"


# --- VE-4e (ficha VE3-21) --- el nivel MEDIO del agua de un relleno sin
# drenar bajo sismo (C11.6.5.3): la fuente no lo da y lo declara el
# proyectista; sin declararlo, la condicion sismica se detiene.
CRITERIO_NIVEL_AGUA_SISMO = "nivel_agua_relleno_sin_drenaje_bajo_sismo"


NIVEL_MEDIO_SUPERFICIE = "superficie_del_relleno"


NIVEL_MEDIO_FREATICO = "freatico_natural"


NIVELES_MEDIOS_SIN_DRENAJE = (NIVEL_MEDIO_SUPERFICIE, NIVEL_MEDIO_FREATICO)


CITA_NIVEL_MEDIO = "AASHTO_LRFD_9.C11.6.5.3#NIVEL_MEDIO"


# --- VE-3.14, opciones 9, 10 y 13 --- (ver sus fichas en criterios_adoptados)
CRITERIO_MOMENTO_TALON = "momento_talon_cabezal"


TALON_PESO_ENTERO = "peso_entero"


TALON_EXACTO = "exacto"


CRITERIO_CARGA_PANTALLA = "carga_pantalla_cabezal"


PANTALLA_PLANO_VIRTUAL = "plano_virtual_del_talon"


PANTALLA_CUNA = "cuna_sobre_la_pantalla"


CRITERIO_DISTRIBUCION_INCREMENTO = "distribucion_incremento_sismico"


INCREMENTO_FRACCION = "fraccion_de_h"


INCREMENTO_DISTRIBUCION_ESTATICA = "distribucion_estatica"


INCREMENTO_SEGUN_REGIMEN = "segun_regimen"


def _eleccion(clave: str, opciones: Tuple[str, ...]) -> str:
    """El valor de una eleccion de conjunto cerrado, validado (segunda linea)."""
    valor = ca.valor(clave)
    if valor not in opciones:
        raise DatoInvalidoError(clave, valor=valor,
                                motivo="se espera una de: " + ", ".join(opciones))
    return valor


CRITERIO_GAMMA_SATURADO = "peso_especifico_saturado_relleno_kn_m3"


CRITERIO_FRACCION_DELTA = "fraccion_delta_sobre_phi_trasdos"


CRITERIO_REGLA_PENDIENTE = "regla_pendiente_relleno_trasdos"


CRITERIO_INCLINACION_PORTANTE = "factores_inclinacion_carga_portante"


CRITERIO_SUELO_FUNDACION = "c_phi_fundacion"


FILA_PHI_ZAPATAS = "zapatas_seccion_10"


FILA_PHI_MUROS = "muros_tabla_11_5_7"


FILAS_DE_PHI = (FILA_PHI_ZAPATAS, FILA_PHI_MUROS)


DRENAJE_SIN = "sin_drenaje"


DRENAJE_CON = "drenado"


DRENAJES = (DRENAJE_SIN, DRENAJE_CON)


REGLA_CUNA_DE_TANTEO = "cuna_de_tanteo"


REGLA_TALUD_QUEBRADO = "talud_quebrado_2h"


REGLA_TALUD_ENTERO = "talud_del_terraplen"


REGLAS_DE_PENDIENTE = (REGLA_CUNA_DE_TANTEO, REGLA_TALUD_QUEBRADO,
                       REGLA_TALUD_ENTERO)


# Como se calcula el empuje: por la cuña con la superficie real, o por la
# formula cerrada (Coulomb / Mononobe-Okabe) con una pendiente equivalente.
METODO_EMPUJE_CUNA = "cuna de tanteo (Culmann) con la superficie real"


METODO_EMPUJE_FORMULA = "formula cerrada con pendiente equivalente"


# --- VE-5 (ficha T7B-06) --- el incremento sismico por la cuña de tanteo
# cuando la formula cerrada de la regla queda fuera del dominio de M-O.
METODO_INCREMENTO_CUNA = ("cuña de tanteo pseudoestatica (C11.6.5.3): "
                          "Mononobe-Okabe fuera de su dominio")


# El regimen del cabezal frente al empuje (correcciones de T-7b, H7).
CRITERIO_REGIMEN = "regimen_cabezal"


# --- verificacion de T-7 (punto 9) --- los tres factores del modificador de
# carga de AASHTO 1.3.2.1. eta_I es el del CRUCE: la misma clave que lee la
# Fase 8 del conducto (`M8.CRITERIO_ETA_CONDUCTO`); no se duplica el numero.
CRITERIO_ETA_IMPORTANCIA = "eta_importancia_operativa_conducto"


CRITERIO_ETA_DUCTILIDAD = "eta_ductilidad_cabezal"


CRITERIO_ETA_REDUNDANCIA = "eta_redundancia_cabezal"


REGIMEN_CEDENTE = "cedente"


REGIMEN_NO_CEDENTE = "no_cedente"


REGIMENES_DEL_CABEZAL = (REGIMEN_CEDENTE, REGIMEN_NO_CEDENTE)


# --- VE-5 (lote M9, ficha T7B-14) --- el empuje sismico total del muro que
# no cede (ver su ficha en criterios_adoptados) y el empuje estatico que
# rige en cada caso.
CRITERIO_EMPUJE_SISMICO_NO_CEDE = "empuje_sismico_muro_que_no_cede"


NO_CEDE_REPOSO_MAS_INCREMENTO = "reposo_mas_incremento"


NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL = "mayor_de_reposo_y_total"


EMPUJES_SISMICOS_NO_CEDE = (NO_CEDE_REPOSO_MAS_INCREMENTO,
                            NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL)


EMPUJE_ESTATICO_ACTIVO = "activo"


EMPUJE_ESTATICO_REPOSO = "reposo"


INCLINACION_APLICAR = "aplicar"


INCLINACION_OMITIR = "omitir"


NUMERAL_9_3_LRFD = "Sec. 9.3, marco LRFD (AASHTO LRFD 11.6.3 y 11.6.5)"


NUMERAL_9_3_ASD = ("Sec. 9.3, marco ASD (E.050 Art. 21 y num. 39.13.6, por "
                   "analogia)")


CAMPOS_SUELO_OBLIGATORIOS = ("cohesivo", "c_kpa", "phi_grados", "gamma_kn_m3")


# (Correcciones de T-7b, H8: `gamma_saturado_kn_m3` se validaba y nadie lo
# consumia -- la capacidad portante bajo el freatico va con los coeficientes
# C_w de la Tabla 10.6.3.1.2a-2 sobre el peso total --; se retiro.)
CAMPOS_SUELO_OPCIONALES = ("q_n_kpa", "q_adm_kpa")


# Los codigos de las cargas del ensamble: nombres, no valores.
C_DC_PANTALLA = "DC.pantalla"


C_DC_ZAPATA = "DC.zapata"


C_EV_TALON = "EV.talon"


C_EH_H = "EH.h"


C_EH_V = "EH.v"


C_LS_H = "LS.h"


C_LS_V = "LS.v"


C_WA_H = "WA.h"


C_WA_U = "WA.u"


C_EQ_H = "EQ.dPAE.h"


C_EQ_V = "EQ.dPAE.v"


C_EQ_PIR_MURO = "EQ.PIR.muro"


C_EQ_PIR_SUELO = "EQ.PIR.suelo"


CARGAS_DE_INERCIA = (C_EQ_PIR_MURO, C_EQ_PIR_SUELO)


# --- dictamen Fable (VE-7 lote A, abierto (i)) --- con k_v distinto de cero
# los pesos estabilizantes (DC y EV) van con (1 - k_v): una carga vertical
# -k_v·(W_w + W_s) en su centro de gravedad (AASHTO A11.3.1, el mismo k_v
# de Mononobe-Okabe; los dos casos de 11.6.5.1 y su contraparte del Manual
# de Puentes 2.8.1.1.14.1). El (1 - k_v) en los pesos es DERIVACION del
# equilibrio seudoestatico de Mononobe-Okabe (A11.3.1), no texto literal de
# la norma (dictamen Fable, revision residual de VE-7). Solo bajo sismo y
# solo con |k_v| > 0.
C_EQ_KV = "EQ.kv.pesos"


CITAS_K_V_EN_LOS_PESOS = ("AASHTO_LRFD_9.A11.3.1#KAE",
                          "AASHTO_LRFD_9.11.6.5.1#EXC",
                          "MP.2.8.1.1.14.1#EXC")


CARGAS_DE_EMPUJE_ESTATICO = (C_EH_H, C_EH_V)


CARGAS_DE_INCREMENTO = (C_EQ_H, C_EQ_V)


def _no_evaluable(que: str, procedimiento: str, motivo: str,
                  id_punto: Optional[str] = None) -> MetodoNoEvaluableError:
    """El `MetodoNoEvaluableError` del ensamble, con SU rotulo."""
    return MetodoNoEvaluableError(que, procedimiento, motivo,
                                  id_punto=id_punto,
                                  rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)


# ---------------------------------------------------------------------------
# El suelo de fundacion: la puerta del dato y su lectura
# ---------------------------------------------------------------------------

def validar_suelo_fundacion(valor: Any, *, campo: str = "suelo_fundacion",
                            id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de los parametros del suelo de fundacion del cabezal --
    el dato externo `suelo_fundacion` del punto, o el criterio de corredor
    'c_phi_fundacion' --, y su forma normalizada.

    Obligatorios: `cohesivo` (booleano: si el EMS lo trata como cohesivo o
    como friccionante; E.050 Art. 20 obliga a usar solo uno de c y phi),
    `c_kpa` (>= 0), `phi_grados` (0 a 45, que es hasta donde llega la Tabla
    10.6.3.1.2a-1 de AASHTO) y `gamma_kn_m3` (> 0). Opcionales: `q_n_kpa`
    (resistencia portante NOMINAL del EMS; gana en el marco LRFD),
    `q_adm_kpa` (presion ADMISIBLE del EMS; gana en el marco ASD). Una
    clave desconocida -- tambien `gamma_saturado_kn_m3`, que la FASE A
    validaba sin que nadie la leyera --, un texto o un bool donde va un
    numero se rechazan: ninguno tiene valor por defecto.
    """
    if not isinstance(valor, dict):
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con los parametros del suelo de "
                   "fundacion: " + ", ".join(CAMPOS_SUELO_OBLIGATORIOS))
    desconocidas = [k for k in valor if k not in CAMPOS_SUELO_OBLIGATORIOS
                    + CAMPOS_SUELO_OPCIONALES]
    faltan = [k for k in CAMPOS_SUELO_OBLIGATORIOS if k not in valor]
    if desconocidas or faltan:
        raise DatoInvalidoError(
            campo, valor=sorted(valor), id_punto=id_punto,
            motivo=("campos no reconocidos: " + ", ".join(desconocidas) + ". "
                    if desconocidas else "")
            + ("faltan: " + ", ".join(faltan) + ". " if faltan else "")
            + "Obligatorios: " + ", ".join(CAMPOS_SUELO_OBLIGATORIOS)
            + "; opcionales: " + ", ".join(CAMPOS_SUELO_OPCIONALES))
    if not isinstance(valor["cohesivo"], bool):
        raise DatoInvalidoError(
            f"{campo}.cohesivo", valor=valor["cohesivo"], id_punto=id_punto,
            motivo="se espera true o false: si el EMS trata el suelo de "
                   "fundacion como cohesivo (phi = 0) o como friccionante "
                   "(c = 0), E.050 Art. 20")
    limpio = {"cohesivo": valor["cohesivo"]}
    for k in CAMPOS_SUELO_OBLIGATORIOS[1:] + CAMPOS_SUELO_OPCIONALES:
        if k not in valor:
            continue
        x = valor[k]
        if not _finito(x):
            raise DatoInvalidoError(
                f"{campo}.{k}", valor=x, id_punto=id_punto,
                motivo="se espera un numero finito")
        limpio[k] = float(x)
    if not limpio["c_kpa"] >= 0:
        raise DatoInvalidoError(f"{campo}.c_kpa", valor=limpio["c_kpa"],
                                id_punto=id_punto,
                                motivo="la cohesion no puede ser negativa")
    if not 0 <= limpio["phi_grados"] <= PHI_MAX_TABLA_GRADOS:
        raise DatoInvalidoError(
            f"{campo}.phi_grados", valor=limpio["phi_grados"],
            id_punto=id_punto,
            motivo=f"se espera un angulo entre 0 y {PHI_MAX_TABLA_GRADOS} "
                   "grados, que es el alcance de la Tabla 10.6.3.1.2a-1 de "
                   "AASHTO")
    for k in ("gamma_kn_m3", "q_n_kpa", "q_adm_kpa"):
        if k in limpio and not limpio[k] > 0:
            raise DatoInvalidoError(f"{campo}.{k}", valor=limpio[k],
                                    id_punto=id_punto,
                                    motivo="tiene que ser mayor que cero")
    if limpio["cohesivo"] and not limpio["c_kpa"] > 0:
        raise DatoInvalidoError(
            f"{campo}.c_kpa", valor=limpio["c_kpa"], id_punto=id_punto,
            motivo="un suelo declarado cohesivo necesita su cohesion (E.050 "
                   "Art. 20: phi = 0 y solo cuenta c)")
    if not limpio["cohesivo"] and not limpio["phi_grados"] > 0:
        raise DatoInvalidoError(
            f"{campo}.phi_grados", valor=limpio["phi_grados"],
            id_punto=id_punto,
            motivo="un suelo declarado friccionante necesita su angulo de "
                   "friccion (E.050 Art. 20: c = 0 y solo cuenta phi)")
    return limpio


def suelo_de_fundacion(suelo_del_punto: Optional[dict] = None, *,
                       id_punto: Optional[str] = None) -> Tuple[dict, str]:
    """
    Los parametros del suelo de fundacion del cabezal y de donde salen: los
    del PUNTO (`suelo_fundacion` de `--datos-externos`, ya validados) si
    vienen, y si no los del corredor, el criterio 'c_phi_fundacion', que se
    detiene con `CriterioPendienteError` mientras el EMS no los de.
    """
    if suelo_del_punto is not None:
        return dict(suelo_del_punto), ("dato externo del punto "
                                       "(`suelo_fundacion`), del EMS")
    declarado = ca.valor(CRITERIO_SUELO_FUNDACION)   # CriterioPendienteError
    suelo = validar_suelo_fundacion(declarado, campo=CRITERIO_SUELO_FUNDACION,
                                    id_punto=id_punto)
    origen = f"criterio de corredor '{CRITERIO_SUELO_FUNDACION}', del EMS"
    # --- VE-5 (ficha T7B-04) --- 'capacidad_portante_adm' [S] ya no es un
    # criterio sin consumidor: es la presion ADMISIBLE de corredor, la misma
    # magnitud que el campo `q_adm_kpa` del suelo de corredor, y entra cuando
    # ese campo no viene. Si vienen los dos y difieren, el expediente se
    # contradice: `DatoInvalidoError`. El suelo de un PUNTO no la hereda (es
    # del EMS de ese punto, y gana entero).
    adm = ca.valor_si_declarado(CRITERIO_PORTANTE_ADMISIBLE)
    if adm is not None:
        if "q_adm_kpa" in suelo and not math.isclose(
                suelo["q_adm_kpa"], adm, rel_tol=TOL_UMBRAL_NORMATIVO):
            raise DatoInvalidoError(
                CRITERIO_PORTANTE_ADMISIBLE, valor=adm, id_punto=id_punto,
                motivo=f"'{CRITERIO_SUELO_FUNDACION}' declara q_adm_kpa = "
                       f"{suelo['q_adm_kpa']:g} kPa y "
                       f"'{CRITERIO_PORTANTE_ADMISIBLE}' {adm:g} kPa: la "
                       "presion admisible del EMS es una sola")
        if "q_adm_kpa" not in suelo:
            suelo["q_adm_kpa"] = float(adm)
            origen += (f"; la presion admisible de "
                       f"'{CRITERIO_PORTANTE_ADMISIBLE}' [S]")
    return suelo, origen


# ---------------------------------------------------------------------------
# --- VE-4a --- La puerta del dato externo `estabilidad_global_declarada`
# ---------------------------------------------------------------------------
# E4 y E5 (estabilidad global del muro y del talud) no las calcula este
# programa: las calcula el estudio de suelos con la estratigrafia y un
# programa de equilibrio limite (ficha T7B-07). Lo que entra es su RESULTADO,
# por punto y por cabezal, con la traza del documento que lo sostiene, y el
# ensamble lo contrasta en los dos marcos (`_filas_globales_declaradas`).
DATO_ESTABILIDAD_GLOBAL = "estabilidad_global_declarada"


CODIGOS_GLOBALES = (FS_CODIGO["estabilidad_global"], FS_CODIGO["talud"])


CLAVE_FS_DE_CODIGO = {FS_CODIGO[k]: k for k in ("estabilidad_global",
                                                 "talud")}


CONDICIONES_GLOBALES = (CondicionAnalisis.ESTATICO.value,
                        CondicionAnalisis.SISMICO.value)


CAMPOS_TRAZA_GLOBAL = ("documento", "fecha", "metodo")


CAMPOS_TRAZA_GLOBAL_OPCIONALES = ("programa",)


def validar_estabilidad_global_declarada(valor: Any, *,
                                         id_punto: Optional[str] = None
                                         ) -> dict:
    """
    Forma y dominio de `estabilidad_global_declarada` (dato externo
    opcional, SOLO por punto), y su forma normalizada {"entrada": {...},
    "salida": {...}}; un extremo sin factores queda vacio.

    Por extremo, "E4" y/o "E5", cada uno con los DOS factores de seguridad
    del analisis externo, {"estatico": FS, "sismico": FS} (finitos y mayores
    que cero: medio analisis no es un analisis), y la TRAZA del documento que
    los sostiene: `documento`, `fecha` y `metodo` obligatorios, `programa`
    opcional, en el nivel superior -- valen para los dos extremos -- o dentro
    del extremo, que gana. Un FS en el nivel superior se rechaza: es de la
    seccion analizada de UN cabezal. Una clave desconocida, un texto donde va
    un numero o un FS sin su documento se rechazan: un resultado sin fuente
    es exactamente lo que la memoria no puede imprimir como declarado.
    """
    campo = DATO_ESTABILIDAD_GLOBAL
    traza_admitida = CAMPOS_TRAZA_GLOBAL + CAMPOS_TRAZA_GLOBAL_OPCIONALES
    if not isinstance(valor, dict) or not valor:
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con 'entrada' y/o 'salida', cada uno "
                   "con 'E4' y/o 'E5' = {'estatico': FS, 'sismico': FS}, y la "
                   "traza: " + ", ".join(CAMPOS_TRAZA_GLOBAL))

    def _traza(bloque: dict, donde: str) -> dict:
        limpio = {}
        for k in traza_admitida:
            if k not in bloque:
                continue
            x = bloque[k]
            if not isinstance(x, str) or not x.strip():
                raise DatoInvalidoError(
                    f"{campo}.{donde}.{k}", valor=x, id_punto=id_punto,
                    motivo="se espera un texto no vacio: la traza del "
                           "documento del analisis externo")
            limpio[k] = x.strip()
        return limpio

    comunes = {k: v for k, v in valor.items() if k not in EXTREMOS}
    sobran = [k for k in comunes if k not in traza_admitida]
    if sobran:
        raise DatoInvalidoError(
            campo, valor=sorted(sobran), id_punto=id_punto,
            motivo=("un factor de seguridad es de la seccion analizada de UN "
                    "cabezal: va dentro de 'entrada' o 'salida'"
                    if set(sobran) & set(CODIGOS_GLOBALES) else
                    "campos no reconocidos. Arriba solo van "
                    + ", ".join(EXTREMOS + traza_admitida)))
    base = _traza(comunes, "comun")
    normalizado = {}
    for extremo in EXTREMOS:
        bloque = valor.get(extremo, {})
        if not isinstance(bloque, dict):
            raise DatoInvalidoError(
                f"{campo}.{extremo}", valor=bloque, id_punto=id_punto,
                motivo="se espera un objeto con 'E4' y/o 'E5'")
        desconocidas = [k for k in bloque
                        if k not in traza_admitida + CODIGOS_GLOBALES]
        if desconocidas:
            raise DatoInvalidoError(
                f"{campo}.{extremo}", valor=sorted(desconocidas),
                id_punto=id_punto,
                motivo="campos no reconocidos. Admitidos: "
                       + ", ".join(CODIGOS_GLOBALES + traza_admitida))
        factores = {}
        for codigo in CODIGOS_GLOBALES:
            if codigo not in bloque:
                continue
            par = bloque[codigo]
            if not isinstance(par, dict) or set(par) != set(
                    CONDICIONES_GLOBALES):
                raise DatoInvalidoError(
                    f"{campo}.{extremo}.{codigo}", valor=par,
                    id_punto=id_punto,
                    motivo="se esperan los dos factores de seguridad del "
                           "analisis, " + " y ".join(CONDICIONES_GLOBALES)
                           + ", y nada mas: medio analisis no es un "
                             "analisis")
            for condicion in CONDICIONES_GLOBALES:
                x = par[condicion]
                if not (_finito(x) and x > 0):
                    raise DatoInvalidoError(
                        f"{campo}.{extremo}.{codigo}.{condicion}", valor=x,
                        id_punto=id_punto,
                        motivo="se espera un factor de seguridad: numero "
                               "finito y mayor que cero")
            factores[codigo] = {c: float(par[c]) for c in CONDICIONES_GLOBALES}
        if not factores:
            if bloque:
                raise DatoInvalidoError(
                    f"{campo}.{extremo}", valor=sorted(bloque),
                    id_punto=id_punto,
                    motivo="el bloque no declara ningun factor de seguridad "
                           "(E4 o E5)")
            normalizado[extremo] = {}
            continue
        traza = dict(base)
        traza.update(_traza(bloque, extremo))
        faltan = [k for k in CAMPOS_TRAZA_GLOBAL if k not in traza]
        if faltan:
            raise DatoInvalidoError(
                f"{campo}.{extremo}", valor=sorted(traza), id_punto=id_punto,
                motivo="un factor de seguridad sin su fuente no entra: "
                       "faltan " + ", ".join(faltan))
        normalizado[extremo] = dict(factores, **traza)
    if not any(normalizado.values()):
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="el objeto no declara ningun factor de seguridad")
    return normalizado


# ---------------------------------------------------------------------------
# --- VE-7 (lote A, A5; triaje VE-7 de Fable) --- La puerta del dato externo
# `empuje_sismico_declarado` (fichas VE5M9-02 y VE3-15)
# ---------------------------------------------------------------------------
# Donde el ensamble NO puede calcular el empuje sismico -- la cuña de tanteo
# sin maximo (psi >= phi: la fuente pide el GLE de A11.3.3) o el relleno muy
# abierto con agua (la presion hidrodinamica, que ninguna fuente del
# repositorio da) -- el proyecto puede DECLARAR el resultado de un analisis
# externo, por punto y por cabezal, con su traza. Es el patron de
# `estabilidad_global_declarada` (VE-4a): el programa no lo calcula, lo
# usa SOLO alli; nunca sustituye un empuje que el programa calcula.
DATO_EMPUJE_SISMICO = "empuje_sismico_declarado"


CAMPOS_EMPUJE_SISMICO = ("P_AE_kn_m", "altura_aplicacion_m",
                         "incluye_hidrodinamica", "k_h", "k_v",
                         "altura_plano_m")


# --- dictamen Fable (VE-7 lote A, 5.2) --- un extremo admite hasta DOS
# analisis, de k_h distinto (el de la estabilidad y el 1.0·k_h0 del armado
# del muro que no cede).
MAX_EMPUJES_POR_EXTREMO = 2


# --- dictamen Fable (abierto (ii)) --- lo que la solicitacion y el cabezal
# dicen del armado con el empuje declarado.
NOTA_ARMADO_CON_EMPUJE_DECLARADO = (
    "; Evento Extremo I con el empuje sismico DECLARADO, entero sobre el "
    "plano virtual del talon (AASHTO 11.6.5.2.2 y 11.6.5.3; sin la cuña "
    "sobre la cara de la pantalla)")


CITAS_ARMADO_CON_EMPUJE_DECLARADO = (
    "AASHTO_LRFD_9.11.6.5.2.2#ALTURA", "AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION",
    "AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE", "AASHTO_LRFD_9.11.6.5.3#VALIDEZ")


CAMPOS_TRAZA_EMPUJE = CAMPOS_TRAZA_GLOBAL


METODO_INCREMENTO_DECLARADO = (
    "empuje sismico DECLARADO por un analisis externo "
    f"(`{DATO_EMPUJE_SISMICO}`): el programa no lo puede calcular aqui")


PUERTA_EMPUJE_DECLARADO = (
    f"; o declarar por punto y cabezal el resultado de ese analisis en "
    f"'{DATO_EMPUJE_SISMICO}' de --datos-externos (P_AE_kn_m, "
    "altura_aplicacion_m, incluye_hidrodinamica, k_h, k_v, altura_plano_m, "
    "documento, fecha, metodo)")


def validar_empuje_sismico_declarado(valor: Any, *,
                                     id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de `empuje_sismico_declarado` (dato externo opcional,
    SOLO por punto), y su forma normalizada {"entrada": [..], "salida":
    [..]}: por extremo, la lista de analisis declarados (vacia si no hay).

    QUE ES CADA CAMPO (dictamen Fable, 5.1 y 5.2):
      P_AE_kn_m             la componente HORIZONTAL del empuje TOTAL del
                            suelo bajo sismo (estatico + sismico, con la
                            presion hidrodinamica si aplica) sobre el plano
                            vertical del talon de altura h (AASHTO
                            11.6.5.2.2, cita `AASHTO_LRFD_9.11.6.5.2.2#ALTURA`),
                            SIN la hidrostatica: el programa suma WA aparte;
                            kN/m de muro, > 0
      altura_aplicacion_m   la de su resultante sobre la base de ese plano,
                            m, > 0
      incluye_hidrodinamica si trae la presion hidrodinamica (booleano)
      k_h, k_v              los coeficientes con que se analizo (k_h >= 0,
                            0 <= k_v < 1): solo se usa con los MISMOS
      altura_plano_m        la altura del plano analizado, m, > 0: solo se
                            usa si el plano del ensamble no es mas alto

    Cada extremo lleva un objeto o una lista de hasta
    `MAX_EMPUJES_POR_EXTREMO`, de k_h distinto. La TRAZA (`documento`,
    `fecha`, `metodo`) va arriba -- vale para todos -- o dentro de cada
    objeto, que gana. Un resultado sin su fuente, un campo de mas o de
    menos, o un numero fuera de dominio se rechazan.
    """
    campo = DATO_EMPUJE_SISMICO
    if not isinstance(valor, dict) or not valor:
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con 'entrada' y/o 'salida', cada uno "
                   "con " + ", ".join(CAMPOS_EMPUJE_SISMICO)
                   + ", y la traza: " + ", ".join(CAMPOS_TRAZA_EMPUJE))
    comunes = {k: v for k, v in valor.items() if k not in EXTREMOS}
    sobran = [k for k in comunes if k not in CAMPOS_TRAZA_EMPUJE]
    if sobran:
        raise DatoInvalidoError(
            campo, valor=sorted(sobran), id_punto=id_punto,
            motivo="arriba solo va la traza (" + ", ".join(CAMPOS_TRAZA_EMPUJE)
                   + "): el empuje es de UN cabezal y va dentro de 'entrada' "
                     "o 'salida'")

    def _traza(bloque: dict, donde: str) -> dict:
        limpio = {}
        for k in CAMPOS_TRAZA_EMPUJE:
            if k not in bloque:
                continue
            x = bloque[k]
            if not isinstance(x, str) or not x.strip():
                raise DatoInvalidoError(
                    f"{campo}.{donde}.{k}", valor=x, id_punto=id_punto,
                    motivo="se espera un texto no vacio: la traza del "
                           "analisis externo")
            limpio[k] = x.strip()
        return limpio

    def _uno(bloque: Any, donde: str) -> dict:
        if not isinstance(bloque, dict) or not bloque:
            raise DatoInvalidoError(
                f"{campo}.{donde}", valor=bloque, id_punto=id_punto,
                motivo="se espera un objeto con "
                       + ", ".join(CAMPOS_EMPUJE_SISMICO))
        desconocidas = [k for k in bloque if k not in
                        CAMPOS_EMPUJE_SISMICO + CAMPOS_TRAZA_EMPUJE]
        faltan = [k for k in CAMPOS_EMPUJE_SISMICO if k not in bloque]
        if desconocidas or faltan:
            raise DatoInvalidoError(
                f"{campo}.{donde}", valor=sorted(bloque), id_punto=id_punto,
                motivo="se esperan " + ", ".join(CAMPOS_EMPUJE_SISMICO)
                       + " (y la traza); "
                       + (f"faltan {', '.join(faltan)}" if faltan else
                          f"sobran {', '.join(desconocidas)}"))
        resultado = {}
        for k in ("P_AE_kn_m", "altura_aplicacion_m", "altura_plano_m"):
            x = bloque[k]
            if not (_finito(x) and x > 0):
                raise DatoInvalidoError(
                    f"{campo}.{donde}.{k}", valor=x, id_punto=id_punto,
                    motivo="se espera un numero finito y mayor que cero")
            resultado[k] = float(x)
        k_h, k_v = bloque["k_h"], bloque["k_v"]
        if not (_finito(k_h) and k_h >= 0):
            raise DatoInvalidoError(f"{campo}.{donde}.k_h", valor=k_h,
                                    id_punto=id_punto,
                                    motivo="se espera k_h finito y >= 0")
        if not (_finito(k_v) and 0 <= k_v < 1):
            raise DatoInvalidoError(f"{campo}.{donde}.k_v", valor=k_v,
                                    id_punto=id_punto,
                                    motivo="se espera 0 <= k_v < 1")
        resultado.update(k_h=float(k_h), k_v=float(k_v))
        hidro = bloque["incluye_hidrodinamica"]
        if not isinstance(hidro, bool):
            raise DatoInvalidoError(
                f"{campo}.{donde}.incluye_hidrodinamica", valor=hidro,
                id_punto=id_punto, motivo="se espera true o false")
        resultado["incluye_hidrodinamica"] = hidro
        traza = dict(base)
        traza.update(_traza(bloque, donde))
        sin_traza = [k for k in CAMPOS_TRAZA_EMPUJE if k not in traza]
        if sin_traza:
            raise DatoInvalidoError(
                f"{campo}.{donde}", valor=sorted(traza), id_punto=id_punto,
                motivo="un empuje sin su fuente no entra: faltan "
                       + ", ".join(sin_traza))
        return dict(resultado, **traza)

    base = _traza(comunes, "comun")
    normalizado = {}
    for extremo in EXTREMOS:
        bloque = valor.get(extremo)
        if bloque is None or bloque == {} or bloque == []:
            normalizado[extremo] = []
            continue
        lista = bloque if isinstance(bloque, list) else [bloque]
        if len(lista) > MAX_EMPUJES_POR_EXTREMO:
            raise DatoInvalidoError(
                f"{campo}.{extremo}", valor=len(lista), id_punto=id_punto,
                motivo=f"hasta {MAX_EMPUJES_POR_EXTREMO} analisis por "
                       "cabezal, de k_h distinto")
        analisis = [_uno(b, f"{extremo}[{n}]") for n, b in enumerate(lista)]
        k_hs = [a["k_h"] for a in analisis]
        if any(abs(x - y) <= TOL_UMBRAL_NORMATIVO
               for n, x in enumerate(k_hs) for y in k_hs[n + 1:]):
            raise DatoInvalidoError(
                f"{campo}.{extremo}", valor=k_hs, id_punto=id_punto,
                motivo="dos analisis del mismo cabezal con el mismo k_h: "
                       "cual rige no se decide aqui")
        normalizado[extremo] = analisis
    if not any(normalizado.values()):
        raise DatoInvalidoError(campo, valor=valor, id_punto=id_punto,
                                motivo="el objeto no declara ningun empuje")
    return normalizado


def _empuje_declarado_utilizable(entorno: EntornoDelCabezal, *, k_h: float,
                                 k_v: float, h: float
                                 ) -> Tuple[Optional[dict], str]:
    """
    --- dictamen Fable (VE-7 lote A, 5.2) --- El analisis declarado de este
    cabezal que CASA con la llamada: el mismo k_h y el mismo k_v (con
    `TOL_UMBRAL_NORMATIVO`) y un plano analizado no mas bajo que el del
    ensamble (h <= altura_plano_m: unilateral; con h menor se usa el P_AE
    entero, sin escalar, del lado seguro). Devuelve (analisis, "") o, si hay
    declarados y ninguno casa, (None, que no casa y que valor se pide).
    """
    declarados = getattr(entorno, "empuje_sismico", None) or []
    if isinstance(declarados, dict):
        declarados = [declarados]
    if not declarados:
        return None, ""
    razones = []
    for d in declarados:
        if abs(d["k_h"] - k_h) > TOL_UMBRAL_NORMATIVO:
            razones.append(f"k_h declarado {d['k_h']:g} y el de esta "
                           f"verificacion {k_h:g}")
        elif abs(d["k_v"] - k_v) > TOL_UMBRAL_NORMATIVO:
            razones.append(f"k_v declarado {d['k_v']:g} y el de esta "
                           f"verificacion {k_v:g}")
        elif h > d["altura_plano_m"] + TOL_UMBRAL_NORMATIVO:
            razones.append(f"plano analizado de {d['altura_plano_m']:g} m y "
                           f"el del ensamble de {h:.3f} m (mas alto)")
        else:
            return d, ""
    return None, (f". Hay '{DATO_EMPUJE_SISMICO}' declarado y NO casa ("
                  + "; ".join(razones) + f"): hace falta el de k_h = {k_h:g}, "
                  f"k_v = {k_v:g} y un plano de al menos {h:.3f} m")


def _citas_del_empuje_declarado(datos: dict) -> tuple:
    """--- VE-7 (A5; dictamen Fable 5.6) --- Las citas del paso 9.2.4 con el
    empuje declarado: la validez de M-O, la remision al GLE de A11.3.3 (en
    la frase de 3.11.5.8.1) y la distribucion; con la presion
    hidrodinamica, el comentario del relleno muy abierto."""
    declarado = datos.get("empuje_sismico_declarado")
    if not declarado:
        return ()
    return (("AASHTO_LRFD_9.11.6.5.3#VALIDEZ",
             "AASHTO_LRFD_9.3.11.5.8.1#CUNA",
             "AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION")
            + (("AASHTO_LRFD_9.C11.6.5.3#AGUA_ABIERTO",)
               if declarado["incluye_hidrodinamica"] else ()))


def _nota_del_empuje_declarado(datos: dict) -> str:
    """--- VE-7 (A5) --- Lo que el paso 9.2.4 dice del empuje declarado."""
    declarado = datos.get("empuje_sismico_declarado")
    if not declarado:
        return ""
    return (
        f"EMPUJE SISMICO DECLARADO (`{DATO_EMPUJE_SISMICO}`): el programa no "
        "lo puede calcular aqui -- la cuña de tanteo no tiene maximo (la "
        "fuente pide el GLE de AASHTO A11.3.3) o el relleno muy abierto "
        "pide la presion hidrodinamica (C11.6.5.3) --, y se usa el del "
        f"analisis externo: P_AE = {declarado['P_AE_kn_m']:.3f} kN/m a "
        f"{declarado['altura_aplicacion_m']:.3f} m, "
        + ("con" if declarado["incluye_hidrodinamica"] else "sin")
        + " presion hidrodinamica; documento "
        f"{declarado['documento']} ({declarado['fecha']}), metodo "
        f"{declarado['metodo']} (k_h = {declarado['k_h']:g}, k_v = "
        f"{declarado['k_v']:g}, plano de {declarado['altura_plano_m']:g} m). "
        "Es la componente horizontal del empuje total del suelo sobre el "
        "plano del talon, sin la hidrostatica, que se suma aparte; sin "
        "componente vertical. ")


def _incremento_del_empuje_declarado(declarado: dict, *, h: float,
                                     gamma: float, k_v: float, P_A: float,
                                     P_0: float, z_A: float,
                                     inclinacion: float, reposo_rige: bool,
                                     regimen: str, ang: dict, k_h: float,
                                     dominio_MO: bool, ext: str,
                                     id_punto: Optional[str]) -> tuple:
    """
    --- VE-7 (lote A, A5; dictamen Fable 5.3 y 5.4) --- El incremento
    sismico a partir del P_AE DECLARADO (total, horizontal) y la altura z_AE
    de su resultante, con P_A,h = P_A·cos(delta + beta):

      * P_AE < P_A,h: `DatoInvalidoError` (¿se declaro solo el incremento?).
      * muro que cede (o reposo sin regir): dP_h = P_AE - P_A,h, P_ref =
        P_A,h; con el reposo rigiendo, 'empuje_sismico_muro_que_no_cede':
        «reposo_mas_incremento» -> dP_h = P_AE - P_A,h sobre P_0 (P_ref =
        P_A,h); «mayor_de_reposo_y_total» -> dP_h = max(P_AE - P_0, 0)
        (P_ref = P_0). El piso del 50 % lo dan los casos de 11.6.5.1.
      * z_dP = max[(P_AE·z_AE - P_ref·z_A)/dP_h, h/3], SIN techo: el momento
        total no baja del declarado; despues, el piso de la resultante en h/2
        del muro que no cede con 'segun_regimen' (C11.6.5.4), como el camino
        calculado. Con dP_h nulo y un momento declarado mayor que el del
        estatico, `MetodoNoEvaluableError` (remedio: «reposo_mas_incremento»).
      * K_AE (EQUIVALENTE, solo se imprime) = 2·P_AE/(gamma·h²·(1 - k_v)).

    Sin componente vertical: el declarado es horizontal (5.1).
    """
    z_AE = declarado["altura_aplicacion_m"]
    if not z_AE <= h + TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            f"{DATO_EMPUJE_SISMICO}.{ext}.altura_aplicacion_m", valor=z_AE,
            id_punto=id_punto,
            motivo=f"la resultante declarada queda por encima del plano de "
                   f"empuje (h = {h:.3f} m)")
    P_AE = declarado["P_AE_kn_m"]
    P_A_h = P_A * math.cos(inclinacion)
    if P_AE < P_A_h - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            f"{DATO_EMPUJE_SISMICO}.{ext}.P_AE_kn_m", valor=P_AE,
            id_punto=id_punto,
            motivo=f"menor que el activo estatico horizontal (P_A·cos(delta "
                   f"+ beta) = {P_A_h:.3f} kN/m): ¿se declaro solo el "
                   "incremento? P_AE es el empuje TOTAL")
    forma_no_cede = None
    if reposo_rige:
        forma_no_cede = _eleccion(CRITERIO_EMPUJE_SISMICO_NO_CEDE,
                                  EMPUJES_SISMICOS_NO_CEDE)
        P_est = P_0
        if forma_no_cede == NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL:
            dP_h, P_ref = max(P_AE - P_0, 0.0), P_0
        else:
            dP_h, P_ref = P_AE - P_A_h, P_A_h
    else:
        P_est = P_A_h
        dP_h, P_ref = P_AE - P_A_h, P_A_h
    dP_h = max(dP_h, 0.0)
    if dP_h <= TOL_UMBRAL_NORMATIVO:
        if P_AE * z_AE > P_est * z_A + TOL_UMBRAL_NORMATIVO:
            raise _no_evaluable(
                f"empuje sismico declarado del cabezal de {ext}",
                "el reposo mas el incremento declarado "
                f"('{CRITERIO_EMPUJE_SISMICO_NO_CEDE}' = "
                f"'{NO_CEDE_REPOSO_MAS_INCREMENTO}')",
                f"el P_AE declarado ({P_AE:.3f} kN/m) no supera el estatico "
                f"que rige ({P_est:.3f} kN/m) pero su momento sobre la base "
                f"({P_AE * z_AE:.3f} kN·m/m) es mayor: no hay incremento que "
                "lo represente", id_punto)
        dP_h, z_dP = 0.0, z_AE
    else:
        z_dP = max((P_AE * z_AE - P_ref * z_A) / dP_h,
                   h / LADOS_DEL_TRIANGULO)
    P_total = P_est + dP_h
    distribucion = _eleccion(CRITERIO_DISTRIBUCION_INCREMENTO,
                             (INCREMENTO_SEGUN_REGIMEN, INCREMENTO_FRACCION,
                              INCREMENTO_DISTRIBUCION_ESTATICA))
    cede = (regimen == REGIMEN_CEDENTE
            and ca.valor(CRITERIO_FACTOR_MURO) == FACTOR_MURO_CON_REDUCCION)
    if distribucion == INCREMENTO_SEGUN_REGIMEN and not cede and dP_h > 0:
        z_dP = max(z_dP, (P_total * h / 2 - P_est * z_A) / dP_h)
    K_AE = 2 * P_AE / (gamma * h ** 2 * (1.0 - k_v))
    K_AE_formula = (k_ae_mononobe_okabe(
        phi_grados=ang["phi"], i_grados=ang["i"], beta_grados=ang["beta"],
        delta_grados=ang["delta"], k_h=k_h, k_v=k_v) if dominio_MO else None)
    fraccion = z_dP / h
    traza = (f"{declarado['documento']}, {declarado['fecha']}, "
             f"{declarado['metodo']}")
    proc_h = (f"P_AE declarado ({traza}) - {P_ref:.3f} = {dP_h:.3f}"
              + (" sobre el reposo" if reposo_rige else "")
              + f", a {fraccion:g}·h")
    proc_v = ("sin componente vertical: el empuje declarado es la "
              "componente horizontal")
    return (K_AE, K_AE_formula, None, P_AE, dP_h, dP_h, 0.0, z_dP,
            fraccion, P_est, P_total, proc_h, proc_v, forma_no_cede)


def coeficientes_de_nivel_freatico(*, D_w: float, D_f: float,
                                   B: float) -> Tuple[float, float]:
    """
    (C_wq, C_wgamma) de la Tabla 10.6.3.1.2a-2 de AASHTO LRFD (pag. impresa
    10-72) para un nivel freatico a la profundidad `D_w` bajo la superficie
    del terreno, con la zapata empotrada `D_f` y de ancho `B`.

    La tabla da tres filas: D_w = 0 -> (0.5, 0.5); D_w = D_f -> (1.0, 0.5);
    D_w > 1.5·B + D_f -> (1.0, 1.0). ENTRE FILAS LA TABLA CALLA: se interpola
    linealmente (C_wq entre la superficie y el desplante; C_wgamma entre el
    desplante y 1.5·B por debajo), que es lectura del proyecto y va del lado
    de la fuente -- «Where the position of groundwater is at a depth less
    than 1.5 times the footing width below the footing base, the bearing
    resistance is affected» --. Un nivel por encima del terreno se lee como
    en la superficie.
    """
    for nombre, x in (("D_w", D_w), ("D_f", D_f), ("B", B)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x,
                                    motivo="se espera un numero finito")
    if not (B > 0 and D_f >= 0):
        raise DatoInvalidoError("B", valor=(B, D_f),
                                motivo="ancho positivo y empotramiento no "
                                       "negativo")
    sup = CW_NIVEL_FREATICO_T10_6_3_1_2A_2["en_la_superficie"]
    des = CW_NIVEL_FREATICO_T10_6_3_1_2A_2["en_el_desplante"]
    bajo = CW_NIVEL_FREATICO_T10_6_3_1_2A_2["bajo_la_zona_de_falla"]
    D_w = max(D_w, 0.0)
    if D_f > 0 and D_w < D_f:
        c_wq = sup[0] + (des[0] - sup[0]) * D_w / D_f
    else:
        c_wq = des[0]
    zona = CW_PROFUNDIDAD_SIN_EFECTO_VECES_B * B
    if D_w <= D_f:
        c_wg = des[1]
    elif D_w >= D_f + zona:
        c_wg = bajo[1]
    else:
        c_wg = des[1] + (bajo[1] - des[1]) * (D_w - D_f) / zona
    return c_wq, c_wg


def factores_de_forma(*, phi_grados: float, B: float, L: float,
                      N_c: float, N_q: float) -> Tuple[float, float, float]:
    """
    (s_c, s_q, s_gamma) de la Tabla 10.6.3.1.2a-3 de AASHTO LRFD (pag.
    impresa 10-73): con phi = 0, s_c = 1 + B/(5L) y s_q = s_gamma = 1; con
    phi > 0, s_c = 1 + (B/L)(N_q/N_c), s_q = 1 + (B/L)·tan(phi) y s_gamma =
    1 - 0.4·(B/L). B/L no pasa de 1 (L es la dimension mayor).
    """
    if not (_finito(B) and _finito(L) and B > 0 and L > 0):
        raise DatoInvalidoError("longitud", valor=(B, L),
                                motivo="ancho y longitud de la zapata "
                                       "positivos y finitos")
    r = min(B / L, 1.0)
    if phi_grados > 0:
        return (1.0 + r * N_q / N_c,
                1.0 + r * math.tan(math.radians(phi_grados)),
                1.0 - FORMA_SGAMMA_COEFICIENTE * r)
    return 1.0 + r / FORMA_SC_PHI_CERO_DIVISOR, 1.0, 1.0


def factor_de_profundidad(*, phi_grados: float, D_f: float,
                          B: float) -> float:
    """
    d_q de la ec. 10.6.3.1.2a-10 de AASHTO LRFD (pag. impresa 10-73):

        d_q = 1 + 2·tan(phi)·(1 - sen(phi))²·arctan(D_f/B)  (radianes)

    «shall not exceed 1.4» (`DQ_MAXIMO_10_6_3_1_2A_10`). La fuente lo pide
    solo con el suelo sobre el desplante tan competente como el de debajo,
    y lo verifico para phi de 32 a 42 grados y D_f/B de 1 a 8: quien lo
    declara ('factores_forma_profundidad_portante') asume lo primero, y el
    paso dice si se esta fuera de lo segundo.
    """
    phi = math.radians(phi_grados)
    d_q = (1.0 + 2 * math.tan(phi) * (1.0 - math.sin(phi)) ** 2
           * math.atan(max(D_f, 0.0) / B))
    return min(d_q, DQ_MAXIMO_10_6_3_1_2A_10)


def resistencia_portante_nominal(*, suelo: dict, B_efectivo: float,
                                 D_f: float, D_w: float, H_servicio: float,
                                 V_servicio: float,
                                 aplicar_inclinacion: bool,
                                 longitud: Optional[float] = None,
                                 profundidad: bool = False
                                 ) -> Tuple[float, dict]:
    """
    q_n, resistencia portante NOMINAL del terreno bajo la zapata corrida del
    cabezal, kPa, con la ecuacion general de AASHTO LRFD 10.6.3.1.2a (ec.
    10.6.3.1.2a-1 a -4, pag. impresa 10-70), y el detalle de sus terminos:

        q_n = c·N_c·i_c + gamma·D_f·N_q·i_q·C_wq
              + 0.5·gamma·B'·N_gamma·i_gamma·C_wgamma

    LO QUE SE TOMA IGUAL A 1 DE ARCHIVO, y por que: los factores de FORMA
    (s_c, s_q, s_gamma), porque la zapata del cabezal continua bajo los
    aleros y se trata como corrida (B/L -> 0); y el de PROFUNDIDAD d_q,
    porque la fuente lo admite solo con suelo competente sobre el desplante
    y lo verifico para D_f/B de 1 a 8, que no es el caso de esta zapata.
    --- VE-5 (ficha T7B-04) --- Con `longitud` (L) se aplican los de forma
    (`factores_de_forma`, Tabla 10.6.3.1.2a-3) y con `profundidad`, d_q
    (`factor_de_profundidad`, ec. 10.6.3.1.2a-10): lo declara
    'factores_forma_profundidad_portante' [A].

        q_n = c·N_c·s_c·i_c + gamma·D_f·N_q·s_q·d_q·i_q·C_wq
              + 0.5·gamma·B'·N_gamma·s_gamma·i_gamma·C_wgamma

    `B_efectivo` es B - 2e de la combinacion (10.6.3.1.1 manda usar las
    dimensiones efectivas). `D_f` es el empotramiento que queda DELANTE de la
    zapata -- bajo la hoya de socavacion, si la hay -- y `D_w` la profundidad
    del nivel freatico bajo ese mismo terreno.

    LOS FACTORES DE INCLINACION (ecs. 10.6.3.1.2a-5 a -9) usan las cargas SIN
    FACTORAR, como la fuente las define («H = unfactored horizontal load»),
    con n = 2: zapata corrida cargada en la direccion de su ancho. Con suelo
    friccionante, i_q = (1 - H/V)^n e i_gamma = (1 - H/V)^(n+1); con suelo
    cohesivo (phi = 0), i_c = 1 - n·H/(c·B'·N_c) e i_q = 1. Se aplican o se
    omiten segun 'factores_inclinacion_carga_portante' [A], que es lo que
    decide `aplicar_inclinacion`.

    E.050 Art. 20, que la hoja de ruta hace regir sobre los parametros: con
    suelo cohesivo phi = 0; con friccionante c = 0. No se combinan.
    """
    for nombre, x in (("B_efectivo", B_efectivo), ("D_f", D_f), ("D_w", D_w),
                      ("H_servicio", H_servicio), ("V_servicio", V_servicio)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x,
                                    motivo="se espera un numero finito")
    if not (B_efectivo > 0 and V_servicio > 0 and D_f >= 0):
        raise DatoInvalidoError(
            "B_efectivo", valor=(B_efectivo, V_servicio, D_f),
            motivo="la resistencia portante necesita ancho efectivo y carga "
                   "vertical positivos, y un empotramiento no negativo")
    c, phi = parametros_resistencia_art20(c=suelo["c_kpa"],
                                          phi_grados=suelo["phi_grados"],
                                          cohesivo=suelo["cohesivo"])
    gamma = suelo["gamma_kn_m3"]
    N_c, N_q, N_g = factores_de_capacidad_de_carga(phi)
    c_wq, c_wg = coeficientes_de_nivel_freatico(D_w=D_w, D_f=D_f,
                                                B=B_efectivo)
    n = 2                       # zapata corrida cargada segun su ancho
    H = abs(H_servicio)
    i_c = i_q = i_g = 1.0
    if aplicar_inclinacion:
        if phi > 0:
            base = max(1.0 - H / V_servicio, 0.0)
            i_q = base ** n
            i_g = base ** (n + 1)
            i_c = i_q - (1.0 - i_q) / (N_q - 1.0)
        else:
            i_c = max(1.0 - n * H / (c * B_efectivo * N_c), 0.0)
    s_c = s_q = s_g = d_q = 1.0
    if longitud is not None:
        s_c, s_q, s_g = factores_de_forma(phi_grados=phi, B=B_efectivo,
                                          L=longitud, N_c=N_c, N_q=N_q)
    if profundidad:
        d_q = factor_de_profundidad(phi_grados=phi, D_f=D_f, B=B_efectivo)
    termino_c = c * N_c * s_c * i_c
    termino_q = gamma * D_f * N_q * s_q * d_q * i_q * c_wq
    termino_g = gamma * B_efectivo * N_g * s_g * i_g * c_wg / 2
    q_n = termino_c + termino_q + termino_g
    if not (math.isfinite(q_n) and q_n >= 0):
        raise LimiteNumericoError(
            "q_n", valor=q_n,
            motivo="la resistencia portante nominal no es un numero finito "
                   f"y no negativo (B' = {B_efectivo!r} m, H/V = "
                   f"{H!r}/{V_servicio!r})")
    return q_n, {"N_c": N_c, "N_q": N_q, "N_gamma": N_g, "i_c": i_c,
                 "s_c": s_c, "s_q": s_q, "s_gamma": s_g, "d_q": d_q,
                 "i_q": i_q, "i_gamma": i_g, "C_wq": c_wq, "C_wgamma": c_wg,
                 "c": c, "phi": phi, "gamma": gamma,
                 "termino_c": termino_c, "termino_q": termino_q,
                 "termino_gamma": termino_g}


# ---------------------------------------------------------------------------
# El relleno detras del cabezal: angulos y geometria
# ---------------------------------------------------------------------------

def geometria_del_relleno(entorno: EntornoDelCabezal) -> dict:
    """
    La geometria del relleno detras de UN cabezal, que es de donde salen la
    altura del plano de empuje y la pendiente equivalente (punto 5 del
    encargo de T-7b: «i de la geometria del terraplen»).

    El relleno retenido llega, contra el trasdos, a `cota_relleno`
    (coronacion menos bordillo). Detras SUBE con el talud del terraplen
    (1 V : talud H) hasta el borde de la plataforma, donde se quiebra y
    sigue con la plataforma, que se toma horizontal:

        z_rel   = cota_relleno - cota_desplante       altura retenida
        subida  = max(cota_borde - cota_relleno, 0)   lo que el relleno sube
        h       = z_rel + min(talon / talud, subida)  plano de empuje: hasta
                  el terreno que queda encima del extremo del talon (AASHTO
                  11.6.5.2.2)
        i       = arctan( min(2·z_rel / talud, subida) / (2·z_rel) )
                  pendiente equivalente del relleno quebrado (Figura
                  C3.11.5.8.1-1 de AASHTO, por analogia), o arctan(1/talud)
                  con la regla «talud_del_terraplen»
        subida_sobre_plano = subida - (h - z_rel)
                  lo que el relleno sigue subiendo por encima del tope del
                  plano de empuje hasta la plataforma: la superficie que la
                  cuña de tanteo usa (regla «cuna_de_tanteo», la de archivo;
                  con ella la pendiente equivalente solo alimenta el
                  CONTRASTE de la formula cerrada)

    El plano de empuje es el vertical del extremo del talon (AASHTO
    C3.11.5.3) si la zapata tiene talon, y el propio trasdos si no lo tiene.
    """
    g = entorno.geometria
    for nombre, x in (("cota_relleno", entorno.cota_relleno),
                      ("cota_borde_plataforma", entorno.cota_borde_plataforma),
                      ("cota_desplante", g.cota_desplante)):
        _exigir_finito(nombre, x, f"{nombre} del cabezal de "
                       f"{entorno.extremo}", entorno.id_punto)
    talud = _exigir_positivo(CRITERIO_TALUD_TERRAPLEN, entorno.talud,
                             "talud del terraplen", entorno.id_punto)
    talon = g.exigir_ancho_talon()
    z_rel = entorno.cota_relleno - g.cota_desplante
    if not z_rel > g.espesor_zapata:
        raise DatoInvalidoError(
            "cota_relleno", valor=entorno.cota_relleno,
            id_punto=entorno.id_punto,
            motivo=f"el relleno retenido por el cabezal de {entorno.extremo} "
                   f"({z_rel:.3f} m sobre la base) no queda sobre la zapata "
                   f"({g.espesor_zapata:.3f} m)")
    subida = max(entorno.cota_borde_plataforma - entorno.cota_relleno, 0.0)
    sobre_talon = min(talon / talud, subida)
    h = z_rel + sobre_talon
    regla = ca.valor(CRITERIO_REGLA_PENDIENTE)
    if regla not in REGLAS_DE_PENDIENTE:
        raise DatoInvalidoError(CRITERIO_REGLA_PENDIENTE, valor=regla,
                                motivo="se espera una de: "
                                       + ", ".join(REGLAS_DE_PENDIENTE))
    declarado = ca.valor_si_declarado(CRITERIO_I_RELLENO)
    alcance = TALUD_QUEBRADO_DISTANCIA_VECES_H * z_rel
    if declarado is not None:
        i_grados = float(declarado)
        origen_i = (f"declarado en '{CRITERIO_I_RELLENO}' [A]: gana sobre el "
                    "que saldria de la geometria")
    elif regla in (REGLA_TALUD_QUEBRADO, REGLA_CUNA_DE_TANTEO):
        i_grados = math.degrees(math.atan2(min(alcance / talud, subida),
                                           alcance))
        origen_i = (f"regla '{regla}' ('{CRITERIO_REGLA_PENDIENTE}' [A]): "
                    "recta de la coronacion del relleno retenido al terreno "
                    f"a 2·{z_rel:.3f} = {alcance:.3f} m detras del muro "
                    "(Figura C3.11.5.8.1-1 de AASHTO, por analogia)"
                    + (": con la cuña de tanteo esta pendiente SOLO entra "
                       "en el contraste de la formula cerrada"
                       if regla == REGLA_CUNA_DE_TANTEO else ""))
    else:
        i_grados = (math.degrees(math.atan2(1.0, talud)) if subida > 0
                    else 0.0)
        origen_i = (f"regla '{regla}' ('{CRITERIO_REGLA_PENDIENTE}' [A]): "
                    "el talud del terraplen entero, sin quiebre")
    if not (_finito(i_grados) and i_grados >= 0):
        raise DatoInvalidoError(CRITERIO_I_RELLENO, valor=i_grados,
                                id_punto=entorno.id_punto,
                                motivo="pendiente finita y no negativa")
    # La cuña de relleno sobre el talon por encima de z_rel: triangulo hasta
    # donde el talud alcanza la plataforma, y rectangulo despues.
    x_quiebre = min(subida * talud, talon)
    area_tri = x_quiebre * (x_quiebre / talud) / 2
    area_rec = (talon - x_quiebre) * subida
    return {"z_rel": z_rel, "subida": subida, "h": h, "i_grados": i_grados,
            "origen_i": origen_i, "talon": talon, "talud": talud,
            "regla": regla, "x_quiebre": x_quiebre, "area_tri": area_tri,
            "area_rec": area_rec, "sobre_talon": sobre_talon,
            "subida_sobre_plano": subida - sobre_talon,
            "i_declarado": declarado is not None}


def angulos_del_empuje(entorno: EntornoDelCabezal, relleno: dict) -> dict:
    """
    Los cuatro angulos del empuje de UN cabezal (punto 5 del encargo):

        phi    del ensayo del relleno ('phi_relleno_trasdos'; sin el se
               detiene con `CriterioPendienteError`)
        delta  el declarado en 'friccion_muro_suelo_delta', o la fraccion de
               phi de 'fraccion_delta_sobre_phi_trasdos' [C] (0.67)
        i      de la geometria (`geometria_del_relleno`)
        beta   0 sobre el plano vertical del talon; el del trasdos
               (`GeometriaCabezal.beta_grados`) si la zapata no tiene talon
    """
    phi = _exigir_positivo(CRITERIO_PHI_RELLENO, ca.valor(CRITERIO_PHI_RELLENO),
                           "angulo de friccion del relleno", entorno.id_punto)
    declarado = ca.valor_si_declarado(CRITERIO_DELTA_MURO)
    if declarado is not None:
        delta = float(declarado)
        origen_delta = (f"declarado en '{CRITERIO_DELTA_MURO}' [A]")
    else:
        fraccion = ca.valor(CRITERIO_FRACCION_DELTA)
        if not (_finito(fraccion) and 0 <= fraccion <= 1):
            raise DatoInvalidoError(CRITERIO_FRACCION_DELTA, valor=fraccion,
                                    motivo="fraccion entre 0 y 1")
        delta = fraccion * phi
        origen_delta = (f"{fraccion:g}·phi ('{CRITERIO_FRACCION_DELTA}' [C], "
                        "AASHTO C3.11.5.3)")
    if not (_finito(delta) and 0 <= delta <= phi):
        raise DatoInvalidoError(CRITERIO_DELTA_MURO, valor=delta,
                                id_punto=entorno.id_punto,
                                motivo=f"delta entre 0 y phi = {phi:g} grados")
    con_talon = relleno["talon"] > TOL_UMBRAL_NORMATIVO
    beta = 0.0 if con_talon else float(entorno.geometria.beta_grados)
    return {"phi": float(phi), "delta": delta, "i": relleno["i_grados"],
            "beta": beta, "origen_delta": origen_delta,
            "plano": ("vertical del extremo del talon (AASHTO C3.11.5.3)"
                      if con_talon else "trasdos de la pantalla (sin talon)")}


def _sesgo(K_formula: float, K: float) -> str:
    """Cuanto se aparta la formula cerrada del coeficiente que rige, dicho."""
    diferencia = (K_formula - K) / K
    return (f"la formula da un {abs(diferencia):.1%} "
            + ("MENOS" if diferencia < 0 else "MAS") + " que la cuña")


def _regimen() -> str:
    """
    El regimen del cabezal ('regimen_cabezal' [A]): «cedente», empuje
    activo de 11.6.5.3; «no_cedente», las presiones del muro que no cede
    (reposo K0 en la estatica, k_h = 1.0·k_h0 y resultante en h/2 bajo
    sismo, AASHTO 11.6.5.4 y su comentario), que hasta VE-5 detenian el
    ensamble sin cifra y desde VE-5 calcula `cargas_del_cabezal`.
    """
    regimen = ca.valor(CRITERIO_REGIMEN)
    if regimen not in REGIMENES_DEL_CABEZAL:
        raise DatoInvalidoError(CRITERIO_REGIMEN, valor=regimen,
                                motivo="se espera una de: "
                                       + ", ".join(REGIMENES_DEL_CABEZAL))
    return regimen


def _regla_de_marco() -> str:
    regla = ca.valor(CRITERIO_MARCO)
    if regla not in REGLAS_DE_MARCO:
        raise DatoInvalidoError(CRITERIO_MARCO, valor=regla,
                                motivo="se espera una de: "
                                       + ", ".join(REGLAS_DE_MARCO))
    return regla


def _decide(marco: str, regla: str) -> bool:
    """Si las verificaciones de ese marco DECIDEN con esa regla."""
    if regla == MARCO_ENVOLVENTE:
        return True
    return (marco == MARCO_LRFD) == (regla == MARCO_RIGE_LRFD)


# ---------------------------------------------------------------------------
# La cuña de tanteo de Coulomb (metodo de Culmann) sobre el plano del talon,
# con la superficie REAL del relleno (correcciones de T-7b, H4)
# ---------------------------------------------------------------------------
# Lo que la fuente pide cuando el relleno no es el de la Figura 3.11.5.3-1
# (talud uniforme): AASHTO 3.11.5.3, «the active pressure may be calculated
# by using a trial procedure based on wedge theory using the Culmann method»
# (cita AASHTO_LRFD_9.3.11.5.3#CULMANN); para el relleno quebrado, «a Coulomb
# trial wedge analysis should be used» (3.11.5.8.1, cita
# AASHTO_LRFD_9.3.11.5.8.1#CUNA, de los muros de suelo reforzado: por
# analogia); y bajo sismo, «the trial wedge method ... may also be used for
# situations when the M-O Method is not suitable» (C11.6.5.3, cita
# AASHTO_LRFD_9.C11.6.5.3#CUNA). La pendiente equivalente «2H» de la Figura
# C3.11.5.8.1-1 queda como alternativa barrible: medida en A-01, SUBESTIMA el
# empuje estatico un 7 a 11 % frente a esta cuña.

def _area_de_la_cuna(*, h: float, subida: float, talud: float,
                     tan_rho: float, beta_grados: float = 0.0) -> float:
    """
    Area de la cuña entre el plano de empuje (de la base (0, 0) a su tope
    (x_t, h), con x_t = -h·tan(beta): beta sobre la vertical, positiva cuando
    el muro se aleja del relleno, la convencion de Mononobe-Okabe; con beta
    = 0, el plano vertical x = 0), el plano de falla z = x·tan(rho) y la
    superficie del relleno: sube desde el tope del plano con 1 V : `talud` H
    y se quiebra, `subida` m mas arriba, en una plataforma horizontal (con
    `subida` infinita, el talud no se quiebra nunca). Area del poligono por
    la formula del cordon de zapato. --- VE-5 (ficha T7B-06) --- `beta`: la
    cuña sobre el trasdos inclinado.
    """
    pendiente = 1.0 / talud
    x_t = -h * math.tan(math.radians(beta_grados))
    x_quiebre = x_t + subida * talud
    vertices = [(0.0, 0.0), (x_t, h)]
    corte = None
    if tan_rho > pendiente:
        x_corte = (h - x_t * pendiente) / (tan_rho - pendiente)
        if x_corte <= x_quiebre:
            corte = (x_corte, x_corte * tan_rho)
    if corte is None:
        if math.isinf(subida):
            return math.inf             # el plano no alcanza el talud
        tope = h + subida
        vertices.append((x_quiebre, tope))
        corte = (tope / tan_rho, tope)
    vertices.append(corte)
    n = len(vertices)
    doble = sum(vertices[k][0] * vertices[(k + 1) % n][1]
                - vertices[(k + 1) % n][0] * vertices[k][1]
                for k in range(n))
    return abs(doble) / 2


def empuje_de_una_cuna(*, rho_grados: float, h: float, subida: float,
                       talud: float, phi_grados: float, delta_grados: float,
                       gamma: float, k_h: float = 0.0,
                       k_v: float = 0.0, beta_grados: float = 0.0) -> float:
    """
    El empuje, kN/m, que UNA cuña de prueba ejerce sobre el plano de empuje
    (vertical, o inclinado `beta_grados` sobre la vertical), con el plano de
    falla a `rho_grados` sobre la horizontal y la superficie del relleno de
    `_area_de_la_cuna`. Equilibrio de la cuña con su peso W, la inercia
    k_h·W hacia el muro y -k_v·W, la reaccion del plano de empuje inclinada
    delta sobre su normal (la normal gira beta con el plano) y la del plano
    de falla inclinada phi sobre la suya:

        P = W·(1 - k_v)·sen(rho - phi + psi)
            / [cos(psi)·cos(rho - phi - delta - beta)]
        psi = arctan[k_h / (1 - k_v)]

    Con k_h = k_v = 0 es la cuña de Coulomb; el maximo sobre rho, con la
    superficie de talud uniforme, es la ec. 3.11.5.3-1 de AASHTO, y con
    sismo, Mononobe-Okabe (A11.3.1): los dos dorados analiticos de la
    funcion, tambien con beta (VE-5).
    """
    psi = math.atan2(k_h, 1.0 - k_v)
    rho, phi, delta, beta = (math.radians(rho_grados),
                             math.radians(phi_grados),
                             math.radians(delta_grados),
                             math.radians(beta_grados))
    area = _area_de_la_cuna(h=h, subida=subida, talud=talud,
                            tan_rho=math.tan(rho), beta_grados=beta_grados)
    W = gamma * area
    return (W * (1.0 - k_v) * math.sin(rho - phi + psi)
            / (math.cos(psi) * math.cos(rho - phi - delta - beta)))


def cuna_de_tanteo(*, h: float, subida: float, talud: float,
                   phi_grados: float, delta_grados: float, gamma: float,
                   k_h: float = 0.0, k_v: float = 0.0,
                   que: str = "empuje del relleno",
                   id_punto: Optional[str] = None,
                   remedio: str = "",
                   beta_grados: float = 0.0) -> Tuple[float, float]:
    """
    (P, rho_critico): el MAYOR empuje de las cuñas de prueba sobre el plano
    vertical de altura `h` y el angulo de su plano de falla, en grados
    (metodo de Culmann, AASHTO 3.11.5.3; bajo sismo, la cuña de tanteo de
    C11.6.5.3). Se muestrea el intervalo admisible de rho en
    `TRAMOS_CUNA_DE_TANTEO` tramos y se afina el mejor a `TOL_ANGULO_CUNA`.

    EL INTERVALO: rho entre phi - psi (por debajo la cuña no empuja) y 90
    grados; con el talud sin quiebre, ademas, por encima de su pendiente; y
    con el plano de empuje inclinado hacia el relleno (beta < 0, VE-5), por
    debajo de la inclinacion del plano.

    SIN MAXIMO, que con la superficie que se quiebra en la plataforma solo
    pasa con psi >= phi (k_h/(1 - k_v) >= tan phi): es el RELLENO el que no
    es estable bajo ese k_h, y no la formula la que falla. Ningun empuje
    sobre el muro lo describe; lo dice el mensaje.

    SE DETIENE, sin cifra (forma MAT-D13):
      * datos fuera de su dominio -> `DatoInvalidoError`;
      * la cuña SIN MAXIMO interior -- el empuje crece hasta el borde del
        intervalo, que es lo que pasa con un talud sin quiebre mas empinado
        que phi - psi: la condicion de 11.6.5.3 en su forma de cuña -- ->
        `MetodoNoEvaluableError` con el rotulo del cabezal;
      * un empuje no finito o no positivo -> `LimiteNumericoError`.
    """
    from scipy.optimize import minimize_scalar   # en el punto de uso (EXT-8)
    for nombre, x in (("h", h), ("talud", talud), ("phi", phi_grados),
                      ("delta", delta_grados), ("gamma", gamma),
                      ("k_h", k_h), ("k_v", k_v), ("beta", beta_grados)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x, id_punto=id_punto,
                                    motivo="la cuña de tanteo necesita un "
                                           "numero finito")
    recto = math.degrees(math.pi / 2)       # el angulo recto, en grados
    if not (h > 0 and talud > 0 and gamma > 0 and 0 < phi_grados < recto
            and 0 <= delta_grados <= phi_grados and k_h >= 0
            and 0 <= k_v < 1 and abs(beta_grados) < recto / 2):
        raise DatoInvalidoError(
            "cuña de tanteo", valor=(h, talud, phi_grados, delta_grados,
                                     k_h, k_v, beta_grados),
            id_punto=id_punto,
            motivo="altura, talud y peso positivos; 0 < phi < 90; 0 <= delta "
                   "<= phi; k_h >= 0, 0 <= k_v < 1 y |beta| < 45")
    if not (subida >= 0 and not math.isnan(subida)):
        raise DatoInvalidoError("subida", valor=subida, id_punto=id_punto,
                                motivo="lo que el relleno sube sobre el "
                                       "plano no puede ser negativo")
    psi = math.degrees(math.atan2(k_h, 1.0 - k_v))
    bajo = max(phi_grados - psi, 0.0)
    if math.isinf(subida):
        bajo = max(bajo, math.degrees(math.atan2(1.0, talud)))
    alto = recto + min(beta_grados, 0.0)

    def P(rho: float) -> float:
        return empuje_de_una_cuna(rho_grados=rho, h=h, subida=subida,
                                  talud=talud, phi_grados=phi_grados,
                                  delta_grados=delta_grados, gamma=gamma,
                                  k_h=k_h, k_v=k_v, beta_grados=beta_grados)

    paso_rho = (alto - bajo) / TRAMOS_CUNA_DE_TANTEO
    malla = [bajo + paso_rho * k for k in range(1, TRAMOS_CUNA_DE_TANTEO)]
    valores = [P(r) for r in malla]
    k_max = max(range(len(malla)), key=lambda k: valores[k])
    if k_max in (0, len(malla) - 1) or not math.isfinite(valores[k_max]):
        inestable = psi >= phi_grados - TOL_UMBRAL_NORMATIVO
        raise _no_evaluable(
            que, "metodo de equilibrio limite generalizado (GLE, AASHTO "
            "A11.3.3) con un programa de estabilidad de taludes, o un "
            "analisis externo",
            "la cuña de tanteo no tiene maximo dentro del intervalo "
            f"admisible ({bajo:.2f} a {alto:.2f} grados): el empuje crece "
            "hasta el borde"
            + (f". Con psi = arctan[k_h/(1 - k_v)] = {psi:.2f} >= phi = "
               f"{phi_grados:.2f} grados el relleno no es estable bajo ese "
               "k_h: el plano de falla tiende a la horizontal y arrastra un "
               "relleno sin cota, de modo que no hay empuje sobre el muro "
               "que describa el caso; es la estabilidad global del "
               "terraplen (E5) la que lo juzga"
               if inestable else
               ", como en un talud sin quiebre mas empinado que phi - psi "
               f"= {phi_grados - psi:.2f} grados")
            + ". La fuente pide otro metodo; el programa no lo tiene"
            + (". " + remedio if remedio else ""), id_punto)
    fino = minimize_scalar(lambda r: -P(r), method="bounded",
                           bounds=(malla[k_max - 1], malla[k_max + 1]),
                           options={"xatol": math.degrees(TOL_ANGULO_CUNA)})
    rho_c = float(fino.x)
    P_max = P(rho_c)
    if P_max < valores[k_max]:          # el afinado no puede empeorar
        rho_c, P_max = malla[k_max], valores[k_max]
    if not (math.isfinite(P_max) and P_max > 0):
        raise LimiteNumericoError(
            "empuje de la cuña", valor=P_max, id_punto=id_punto,
            motivo=f"la cuña critica de {que} no da un empuje finito y "
                   f"positivo (h = {h!r} m, subida = {subida!r} m)")
    return P_max, rho_c


# ---------------------------------------------------------------------------
# Las cargas del ensamble, sin factorar y con su brazo
# ---------------------------------------------------------------------------

def cargas_del_cabezal(entorno: EntornoDelCabezal,
                       condicion: CondicionAnalisis, *,
                       k_h: Optional[float] = None) -> Tuple[tuple, dict]:
    """
    Las cargas de UN cabezal en UNA condicion, por metro de muro y SIN
    FACTORAR, cada una con su brazo (`CargaDeCabezal`), y el diccionario de
    lo que las produjo (coeficientes, alturas, niveles de agua).

    `k_h` (correcciones de T-7c, H2) SOBRESCRIBE el coeficiente sismico
    horizontal de la cadena: es la puerta por la que el ARMADO del muro que
    no cede pide k_h = 1.0·k_h0 (AASHTO 11.6.5.4, «shall be increased to
    1.0kh0»). La estabilidad externa no la usa: sigue con el k_h de la
    cadena, reducido o no segun 'factor_muro_eleccion'.

      DC  peso de la pantalla (trapecio de trasdos vertical) y de la zapata.
      EV  peso del relleno sobre el talon, hasta la superficie del relleno.
      EH  empuje activo sobre el plano de empuje, de altura h, con el
          coeficiente de la cuña de tanteo (Culmann) sobre la superficie REAL
          del relleno -- la regla de archivo de
          'regla_pendiente_relleno_trasdos' -- o el de Coulomb con una
          pendiente equivalente (las otras dos reglas), DESCOMPUESTO: P·cos(delta + beta) horizontal y P·sen(delta + beta)
          vertical, aplicada en el plano (EXT-7-04). Bajo el nivel del agua
          el suelo empuja con su peso SUMERGIDO (AASHTO 3.11.3).
      LS  sobrecarga viva: empuje K_A·gamma·h_eq·h a media altura, y su peso
          gamma·h_eq sobre el talon (que solo entra en el portante).
      WA  empuje hidrostatico del agua del relleno sobre el plano de empuje
          y subpresion bajo la zapata, lineal entre el nivel de delante (el
          freatico natural) y el del relleno. Hasta donde sube el agua del
          relleno lo declara 'drenaje_trasdos', y es POR CONDICION (VE-4e,
          ficha VE3-21): con el trasdos drenado es el freatico natural en
          las dos; sin drenaje, la estatica llena el relleno retenido hasta
          su superficie (AASHTO 11.6.6) y la sismica va con el nivel MEDIO
          del agua en el tiempo (C11.6.5.3, «should»), que la fuente no da
          para un relleno sin drenar y declara
          'nivel_agua_relleno_sin_drenaje_bajo_sismo' [A] (sin valor de
          archivo: sin el, la sismica se detiene). Todo lo que depende del
          agua -- el suelo sumergido del empuje, el peso del relleno sobre el
          talon, la subpresion, el incremento sismico -- sale del nivel de
          SU condicion.
      EQ  (solo sismica) incremento sismico P_AE - P_A (cuña de tanteo
          pseudoestatica con k_h y k_v, o Mononobe-Okabe), con sus
          dos componentes, aplicado a la fraccion de h de
          'punto_aplicacion_incremento_sismico'; e inercia del muro y del
          relleno sobre el talon, k_h·W, en el centro de gravedad de cada
          uno (AASHTO 11.6.5.1).

    SE DETIENE, sin cifra (`MetodoNoEvaluableError`): bajo sismo con agua
    en el plano de empuje (relleno saturado: AASHTO 11.6.5.3 admite los
    metodos de equilibrio limite con el relleno no saturado, y su comentario
    pide entonces tratar el agua aparte); con la formula cerrada, cuando
    phi < i + arctan[k_h / (1 - k_v)]; y con la cuña, cuando no tiene maximo
    dentro de su intervalo (`cuna_de_tanteo`). La fuente pide entonces otro
    metodo (GLE), que el programa no tiene.
    """
    g = entorno.geometria
    ext = entorno.extremo
    idp = entorno.id_punto
    relleno = geometria_del_relleno(entorno)
    ang = angulos_del_empuje(entorno, relleno)
    gamma = _exigir_positivo(CRITERIO_GAMMA_RELLENO, peso_especifico_relleno(),
                             "peso especifico del relleno", idp)
    gamma_c = _exigir_positivo(CRITERIO_GAMMA_CONCRETO,
                               ca.valor(CRITERIO_GAMMA_CONCRETO),
                               "peso especifico del concreto", idp)
    B, e_z, H = g.B, g.espesor_zapata, g.H
    e_c, e_b = g.espesor_corona, g.espesor_base_muro
    talon = relleno["talon"]
    punta = B - talon - e_b
    if not punta >= -TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "ancho_talon", valor=talon, id_punto=idp,
            motivo=f"talon ({talon:.3f} m) + pantalla ({e_b:.3f} m) no caben "
                   f"en la zapata (B = {B:.3f} m)")
    punta = max(punta, 0.0)
    x_trasdos = punta + e_b
    z_rel, h = relleno["z_rel"], relleno["h"]
    x_plano = B if talon > TOL_UMBRAL_NORMATIVO else x_trasdos

    # --- agua --------------------------------------------------------------
    # LA COTA DEL AGUA, no una profundidad (correcciones de T-7b, H1): la
    # columna NF_profundidad_m se mide bajo el terreno natural del CRUCE, como
    # en M8, y `datos_del_cabezal_del_punto` la convierte en cota; aqui solo
    # se compara con la base de cada zapata.
    if entorno.cota_freatico is None:
        raise DatoFaltanteError(
            "NF_profundidad_m", id_punto=idp,
            detalle="la estabilidad del cabezal necesita la profundidad del "
                    "nivel freatico bajo el terreno del cruce (columna "
                    "NF_profundidad_m del CSV, del EMS): decide el empuje "
                    "del agua, la subpresion y la capacidad portante. No "
                    "tiene valor por defecto")
    cota_nf = entorno.cota_freatico
    if not _finito(cota_nf):
        raise DatoInvalidoError("NF_profundidad_m", valor=cota_nf,
                                id_punto=idp,
                                motivo="la cota del nivel freatico no es un "
                                       "numero finito")
    D_f = entorno.cota_pie - g.cota_desplante
    h_w_natural = min(max(cota_nf - g.cota_desplante, 0.0), h)
    drenaje = ca.valor(CRITERIO_DRENAJE)
    if drenaje not in DRENAJES:
        raise DatoInvalidoError(CRITERIO_DRENAJE, valor=drenaje,
                                motivo="se espera una de: "
                                       + ", ".join(DRENAJES))
    # SIN DRENAJE el agua llena el relleno RETENIDO, hasta su superficie
    # contra el trasdos (`cota_relleno`, z_rel sobre la base) y no mas arriba:
    # el muro no retiene agua por encima de su relleno (correcciones de T-7b,
    # H6; la FASE A la subia hasta el terreno sobre el extremo del talon, por
    # encima de la coronacion). Con DRENAJE declarado queda en el freatico
    # natural. `HIPOTESIS_EMPUJE_BAJO_NF` lo dice con las mismas palabras.
    # --- VE-4e (ficha VE3-21) --- POR CONDICION: el relleno lleno es la
    # regla ESTATICA de 11.6.6; bajo sismo C11.6.5.3 recomienda el nivel
    # medio en el tiempo, que para un relleno sin drenar declara
    # 'nivel_agua_relleno_sin_drenaje_bajo_sismo' [A] (CriterioPendienteError
    # sin declararlo). Con el trasdos drenado el criterio no se lee: el nivel
    # medio es el freatico natural, el mismo de la estatica.
    nivel_agua_sismo = None
    if drenaje == DRENAJE_SIN:
        h_w = max(min(z_rel, h), h_w_natural)
        if condicion is CondicionAnalisis.SISMICO:
            nivel_agua_sismo = _eleccion(CRITERIO_NIVEL_AGUA_SISMO,
                                         NIVELES_MEDIOS_SIN_DRENAJE)
            if nivel_agua_sismo == NIVEL_MEDIO_FREATICO:
                h_w = h_w_natural
    else:
        h_w = h_w_natural
    gamma_sat = None
    if h_w > TOL_UMBRAL_NORMATIVO:
        gamma_sat = ca.valor(CRITERIO_GAMMA_SATURADO)   # CriterioPendienteError
        if not (_finito(gamma_sat) and gamma_sat > GAMMA_AGUA_KN_M3):
            raise DatoInvalidoError(
                CRITERIO_GAMMA_SATURADO, valor=gamma_sat,
                motivo="mayor que el peso especifico del agua")

    # --- empuje activo, con el suelo sumergido bajo el agua -----------------
    # Con la regla de archivo («cuna_de_tanteo») el coeficiente es el
    # EQUIVALENTE de la cuña critica de Culmann sobre la superficie real,
    # K_A = 2·P_cuña / (gamma·h²), y se reparte sobre el plano con el mismo
    # diagrama triangular que Coulomb (resultante a h/3 en seco); la formula
    # cerrada con la pendiente equivalente queda como CONTRASTE. Con una de
    # las otras dos reglas, o con la pendiente declarada, rige la formula.
    K_A_formula = k_a_coulomb(phi_grados=ang["phi"], i_grados=ang["i"],
                              beta_grados=ang["beta"],
                              delta_grados=ang["delta"])
    usa_cuna = (relleno["regla"] == REGLA_CUNA_DE_TANTEO
                and not relleno["i_declarado"])
    rho_A = None
    if usa_cuna:
        # --- VE-5 (ficha T7B-06) --- sobre el trasdos inclinado (zapata sin
        # talon) la cuña va sobre ESE plano: hasta VE-5 se detenia aqui.
        P_unitario, rho_A = cuna_de_tanteo(
            h=h, subida=relleno["subida_sobre_plano"],
            talud=relleno["talud"], phi_grados=ang["phi"],
            delta_grados=ang["delta"], gamma=1.0,
            que=f"empuje estatico del cabezal de {ext}", id_punto=idp,
            beta_grados=ang["beta"])
        K_A = 2 * P_unitario / h ** 2
        metodo = METODO_EMPUJE_CUNA
    else:
        K_A = K_A_formula
        metodo = METODO_EMPUJE_FORMULA
    inclinacion = math.radians(ang["delta"] + ang["beta"])
    h_seco = h - h_w
    gamma_sum = (gamma_sat - GAMMA_AGUA_KN_M3) if gamma_sat is not None else 0.0
    # Diagrama de presion del suelo: triangulo seco, rectangulo de su
    # continuacion bajo el agua, y triangulo sumergido.
    partes = (
        (K_A * gamma * h_seco ** 2 / 2, h_w + h_seco / 3),      # literal-ok: centroide del triangulo
        (K_A * gamma * h_seco * h_w, h_w / 2),
        (K_A * gamma_sum * h_w ** 2 / 2, h_w / 3),               # literal-ok: centroide del triangulo
    )
    P_A = sum(p for p, _ in partes)
    z_A = (sum(p * z for p, z in partes) / P_A) if P_A > 0 else 0.0
    # --- VE-5 (ficha T7B-14) --- EL MURO QUE NO CEDE ('regimen_cabezal' =
    # 'no_cedente'): la estatica con el empuje en REPOSO, K0 de AASHTO
    # 3.11.5.2-1 sobre el mismo diagrama (suelo sumergido bajo el agua),
    # todo horizontal -- en reposo no se moviliza la friccion muro-relleno --
    # y con el factor de la fila «En reposo» de la Tabla 3.4.1-2
    # (`combinaciones_de_estabilidad`). K0 es de terreno HORIZONTAL: si el
    # activo con la superficie real da MAS componente horizontal (relleno
    # empinado), rige el activo, que un muro que no cede no puede tener por
    # debajo; la misma regla que el armado aplica por seccion (ficha
    # T7C-02). Con 'cedente', el activo de siempre.
    regimen = _regimen()
    K0 = 1.0 - math.sin(math.radians(ang["phi"]))
    P_0 = K0 / K_A * P_A if K_A > 0 else 0.0
    reposo_rige = (regimen == REGIMEN_NO_CEDENTE
                   and P_0 >= P_A * math.cos(inclinacion))
    if reposo_rige:
        empuje_estatico = EMPUJE_ESTATICO_REPOSO
        K_est, P_est, incl_est = K0, P_0, 0.0
    else:
        empuje_estatico = EMPUJE_ESTATICO_ACTIVO
        K_est, P_est, incl_est = K_A, P_A, inclinacion

    cargas = []
    # --- DC ----------------------------------------------------------------
    W_rect = gamma_c * e_c * H
    W_tri = gamma_c * (e_b - e_c) * H / 2
    W_pant = W_rect + W_tri
    x_pant = ((W_rect * (x_trasdos - e_c / 2)
               + W_tri * (punta + 2 * (e_b - e_c) / 3))          # literal-ok: centroide del triangulo
              / W_pant) if W_pant > 0 else x_trasdos
    z_pant = ((W_rect * (e_z + H / 2) + W_tri * (e_z + H / 3))   # literal-ok: centroide del triangulo
              / W_pant) if W_pant > 0 else e_z
    W_zap = gamma_c * B * e_z
    cargas.append(CargaDeCabezal(
        C_DC_PANTALLA, CARGA_DC, "peso de la pantalla", V=W_pant, x=x_pant,
        z=z_pant, sobre=ELEMENTO_PANTALLA,
        procedencia=f"gamma_c·(e_corona + e_base)/2·H = {gamma_c:g}·"
                    f"({e_c:.3f} + {e_b:.3f})/2·{H:.3f}"))
    cargas.append(CargaDeCabezal(
        C_DC_ZAPATA, CARGA_DC, "peso de la zapata", V=W_zap, x=B / 2,
        z=e_z / 2, sobre=ELEMENTO_ZAPATA,
        procedencia=f"gamma_c·B·e_zapata = {gamma_c:g}·{B:.3f}·{e_z:.3f}"))
    # --- EV ----------------------------------------------------------------
    alto_talon = z_rel - e_z
    mojado = min(max(h_w - e_z, 0.0), alto_talon)
    area_seca = talon * (alto_talon - mojado)
    area_mojada = talon * mojado
    cuña = relleno["area_tri"] + relleno["area_rec"]
    gamma_cuña = gamma_sat if (gamma_sat is not None and h_w >= h
                               - TOL_UMBRAL_NORMATIVO) else gamma
    W_s = (gamma * area_seca
           + (gamma_sat if gamma_sat is not None else gamma) * area_mojada
           + gamma_cuña * cuña)
    xq = relleno["x_quiebre"]
    momento_cuña = (relleno["area_tri"] * (x_trasdos + 2 * xq / 3)   # literal-ok: centroide del triangulo
                    + relleno["area_rec"] * (x_trasdos + xq + (talon - xq) / 2))
    x_s = ((gamma * area_seca + (gamma_sat or gamma) * area_mojada)
           * (x_trasdos + talon / 2) + gamma_cuña * momento_cuña) / W_s \
        if W_s > 0 else x_trasdos
    z_s = e_z + alto_talon / 2
    if W_s > 0:
        cargas.append(CargaDeCabezal(
            C_EV_TALON, CARGA_EV, "peso del relleno sobre el talon", V=W_s,
            x=x_s, z=z_s, sobre=ELEMENTO_ZAPATA,
            procedencia=f"gamma·talon·(z_rel - e_z) = {gamma:g}·{talon:.3f}·"
                        f"{alto_talon:.3f}, mas la cuña sobre el talon "
                        f"({cuña:.3f} m2)"))
    # --- EH ----------------------------------------------------------------
    if reposo_rige:
        cargas.append(CargaDeCabezal(
            C_EH_H, CARGA_EH, "empuje en reposo, horizontal (muro que no "
            "cede)", H=P_0, z=z_A, sobre=ELEMENTO_PANTALLA,
            procedencia=f"(K0 / K_A)·P_A, K0 = 1 - sen(phi) = {K0:.4f} "
                        "(AASHTO 3.11.5.2-1), sin friccion muro-relleno"))
        cargas.append(CargaDeCabezal(
            C_EH_V, CARGA_EH, "empuje en reposo, sin componente vertical",
            V=0.0, x=x_plano, sobre=ELEMENTO_ZAPATA,
            procedencia="en reposo no se moviliza friccion muro-relleno"))
    else:
        cargas.append(CargaDeCabezal(
            C_EH_H, CARGA_EH, "empuje activo, componente horizontal",
            H=P_A * math.cos(inclinacion), z=z_A, sobre=ELEMENTO_PANTALLA,
            procedencia="P_A·cos(delta + beta)"))
        cargas.append(CargaDeCabezal(
            C_EH_V, CARGA_EH, "empuje activo, componente vertical",
            V=P_A * math.sin(inclinacion), x=x_plano, sobre=ELEMENTO_ZAPATA,
            procedencia="P_A·sen(delta + beta), en el plano de empuje"))
    # --- LS ----------------------------------------------------------------
    # --- VE-6 (ficha T7B-11) --- con la orientacion y la distancia que el
    # punto declara para ESTE cabezal, si las declara.
    # --- VE-7 (lote A, A7) --- con el cabezal paralelo a la via y el
    # corredor perpendicular sin orientacion del punto, la envolvente.
    h_eq = h_eq_del_cabezal(entorno, altura_muro_total=h)
    nombre_K = "K0" if reposo_rige else "K_A"
    cargas.append(CargaDeCabezal(
        C_LS_H, CARGA_LS, "sobrecarga viva, empuje",
        H=K_est * gamma * h_eq * h, z=h / 2, sobre=ELEMENTO_PANTALLA,
        procedencia=f"{nombre_K}·gamma·h_eq·h = {K_est:.4f}·{gamma:g}·"
                    f"{h_eq:.4f}·{h:.3f}"))
    if talon > TOL_UMBRAL_NORMATIVO:
        cargas.append(CargaDeCabezal(
            C_LS_V, CARGA_LS, "sobrecarga viva, peso sobre el talon",
            V=gamma * h_eq * talon, x=x_trasdos + talon / 2,
            sobre=ELEMENTO_ZAPATA,
            procedencia=f"gamma·h_eq·talon = {gamma:g}·{h_eq:.4f}·"
                        f"{talon:.3f}"))
    # --- WA ----------------------------------------------------------------
    u_punta = GAMMA_AGUA_KN_M3 * h_w_natural
    u_talon = GAMMA_AGUA_KN_M3 * h_w
    if h_w > TOL_UMBRAL_NORMATIVO:
        cargas.append(CargaDeCabezal(
            C_WA_H, CARGA_WA, "empuje hidrostatico del agua del relleno",
            H=GAMMA_AGUA_KN_M3 * h_w ** 2 / 2,
            z=h_w / 3,                                       # literal-ok: centroide del triangulo
            sobre=ELEMENTO_PANTALLA,
            procedencia=f"gamma_w·h_w^2/2 con h_w = {h_w:.3f} m"))
    if u_punta + u_talon > TOL_UMBRAL_NORMATIVO:
        U = (u_punta + u_talon) / 2 * B
        x_U = B * (u_punta + 2 * u_talon) / (3 * (u_punta + u_talon))   # literal-ok: centroide del trapecio
        cargas.append(CargaDeCabezal(
            C_WA_U, CARGA_WA, "subpresion bajo la zapata", V=-U, x=x_U,
            sobre=ELEMENTO_ZAPATA,
            procedencia=f"gamma_w·(h_delante + h_relleno)/2·B = "
                        f"{GAMMA_AGUA_KN_M3:.2f}·({h_w_natural:.3f} + "
                        f"{h_w:.3f})/2·{B:.3f}"))

    datos = {"relleno": relleno, "angulos": ang, "K_A": K_A, "P_A": P_A,
             "z_A": z_A, "h": h, "h_eq": h_eq, "h_w": h_w,
             "h_w_natural": h_w_natural, "drenaje": drenaje, "gamma": gamma,
             "nivel_agua_sismo": nivel_agua_sismo,
             "gamma_saturado": gamma_sat, "gamma_c": gamma_c, "D_f": D_f,
             "cota_freatico": cota_nf, "W_w": W_pant + W_zap, "W_s": W_s, "x_plano": x_plano,
             "x_trasdos": x_trasdos, "punta": punta, "talon": talon,
             "inclinacion": inclinacion, "K_AE": None, "k_h": None,
             "k_v": None, "P_AE": None, "z_AE": None, "fraccion_brazo": None,
             "metodo_empuje": metodo, "K_A_formula": K_A_formula,
             "rho_A": rho_A, "K_AE_formula": None, "rho_AE": None,
             "cota_agua_diseno": entorno.cota_agua_diseno,
             "regimen": regimen, "z_rel": z_rel,
             # K0 de AASHTO 3.11.5.2-1, de REFERENCIA para T-7c: la ec. es
             # de muro vertical y terreno horizontal (cita
             # AASHTO_LRFD_9.3.11.5.2#K0). Desde VE-5 rige la estatica del
             # muro que no cede cuando da mas que el activo.
             "K0": K0, "P_0": P_0,
             # --- VE-5 --- el empuje estatico que RIGE y su componente
             # horizontal: el activo (cedente, o no cedente con relleno
             # empinado) o el reposo (no cedente).
             "empuje_estatico": empuje_estatico, "K_estatico": K_est,
             "P_estatico": P_est, "P_total_sismico": None,
             "metodo_incremento": None,
             "empuje_sismico_no_cede": None}

    # --- EQ ----------------------------------------------------------------
    if condicion is CondicionAnalisis.SISMICO:
        cadena = cadena_sismica()
        if k_h is None:
            # --- VE-5 --- el muro que no cede no admite la reduccion por
            # desplazamiento: «shall be increased to 1.0kh0» (11.6.5.4),
            # aunque 'factor_muro_eleccion' la declare para la cadena.
            k_h = (cadena.k_h0 if regimen == REGIMEN_NO_CEDENTE
                   else cadena.k_h)
        elif not (_finito(k_h) and k_h >= 0):
            raise DatoInvalidoError("k_h", valor=k_h, id_punto=idp,
                                    motivo="coeficiente sismico horizontal "
                                           "no negativo y finito")
        k_v = cadena.k_v
        psi = angulo_inercia_sismica(k_h=k_h, k_v=k_v)
        # --- VE-7 (lote A, A5) --- el P_AE DECLARADO de este cabezal, si lo
        # hay y es del k_h de la estabilidad: SOLO se consume donde el
        # programa no puede calcular el empuje (abajo), nunca en su lugar.
        declarado, no_casa = _empuje_declarado_utilizable(
            entorno, k_h=k_h, k_v=k_v, h=h)
        usar_declarado = False
        # --- VE-3.14 (H-3 de los ensayos de diseño del cabezal) --- CON
        # AGUA EN EL PLANO DE EMPUJE, EL SISMO NO SE SALTA. Hasta VE-3.14 se
        # detenia aqui sin cifra, y el ancho se dimensionaba sin la
        # condicion sismica (y se rotulaba «dimensionada por estabilidad»).
        # El comentario C11.6.5.3 da dos tratamientos: el relleno que no
        # drena libremente -- suelo y agua se mueven juntos -- va con el
        # peso TOTAL (cita AASHTO_LRFD_9.C11.6.5.3#AGUA_TOTAL), y el muy
        # abierto con el sumergido mas la presion hidrodinamica de
        # Westergaard, que ninguna fuente del repositorio da: ese sigue
        # deteniendose ('agua_del_relleno_bajo_sismo' [C]).
        tratamiento_agua = None
        if h_w > TOL_UMBRAL_NORMATIVO:
            tratamiento_agua = ca.valor(CRITERIO_AGUA_SISMO)
            if tratamiento_agua not in (AGUA_SE_MUEVE_CON_EL_SUELO,
                                        AGUA_RELLENO_MUY_ABIERTO):
                raise DatoInvalidoError(
                    CRITERIO_AGUA_SISMO, valor=tratamiento_agua,
                    motivo="se espera una de: " + ", ".join(
                        (AGUA_SE_MUEVE_CON_EL_SUELO,
                         AGUA_RELLENO_MUY_ABIERTO)))
            if (tratamiento_agua == AGUA_RELLENO_MUY_ABIERTO
                    and declarado is not None):
                # --- VE-7 (lote A, A5) --- el declarado tiene que traer la
                # presion hidrodinamica que C11.6.5.3 pide aqui.
                if not declarado["incluye_hidrodinamica"]:
                    raise DatoInvalidoError(
                        f"{DATO_EMPUJE_SISMICO}.{ext}.incluye_hidrodinamica",
                        valor=False, id_punto=idp,
                        motivo=("con el relleno muy abierto y agua en el "
                                "plano de empuje AASHTO C11.6.5.3 pide el "
                                "peso sumergido MAS la presion hidrodinamica: "
                                "el empuje declarado tiene que incluirla"))
                usar_declarado = True
            elif tratamiento_agua == AGUA_RELLENO_MUY_ABIERTO:
                remedio = (
                    " Declarar el drenaje del trasdos ('drenaje_trasdos' = "
                    "'drenado') baja el agua del relleno al freatico natural"
                    if drenaje == DRENAJE_SIN else
                    " El drenaje ya esta declarado: esta agua es la del "
                    "freatico natural, que el drenaje no baja")
                raise _no_evaluable(
                    f"empuje sismico del cabezal de {ext}",
                    "la presion hidrodinamica del agua del relleno "
                    "(solucion de Westergaard, que ninguna fuente del "
                    "repositorio de normas da) o un analisis externo",
                    f"hay agua en el plano de empuje (h_w = {h_w:.3f} m, "
                    f"'{CRITERIO_DRENAJE}' = '{drenaje}') y el relleno "
                    f"esta declarado muy abierto ('{CRITERIO_AGUA_SISMO}' "
                    f"= '{tratamiento_agua}'): AASHTO C11.6.5.3 pide el "
                    "peso sumergido MAS la presion hidrodinamica." + remedio
                    + PUERTA_EMPUJE_DECLARADO + " (con "
                    "'incluye_hidrodinamica' = true)" + no_casa, idp)
        dominio_MO = ang["phi"] >= ang["i"] + psi - TOL_UMBRAL_NORMATIVO
        # --- dictamen Fable (5.8) --- solo la cuña SISMICA (la de k_h) se
        # sustituye por el declarado; la estatica que falle sigue fallando.
        en_cuna_sismica = False
        if not usar_declarado:
            try:
                metodo_incremento = (METODO_EMPUJE_CUNA if usa_cuna
                                     else METODO_EMPUJE_FORMULA)
                K_AE_formula = (k_ae_mononobe_okabe(
                    phi_grados=ang["phi"], i_grados=ang["i"],
                    beta_grados=ang["beta"], delta_grados=ang["delta"], k_h=k_h,
                    k_v=k_v) if dominio_MO else None)
                rho_AE = None
                if usa_cuna:
                    # La cuña de tanteo bajo sismo (C11.6.5.3): con el relleno que
                    # se quiebra en la plataforma tiene maximo aunque Mononobe-Okabe
                    # con la pendiente equivalente quede fuera de su dominio; esa
                    # formula, si es evaluable, se imprime al lado como contraste.
                    en_cuna_sismica = True
                    P_unitario_E, rho_AE = cuna_de_tanteo(
                        h=h, subida=relleno["subida_sobre_plano"],
                        talud=relleno["talud"], phi_grados=ang["phi"],
                        delta_grados=ang["delta"], gamma=1.0, k_h=k_h, k_v=k_v,
                        beta_grados=ang["beta"],
                        que=f"empuje sismico del cabezal de {ext}", id_punto=idp,
                        remedio=("Lo que lo destraba es una decision del Propietario "
                                 "-- admitir el desplazamiento del muro, "
                                 f"'{CRITERIO_FACTOR_MURO}', que reduce k_h a la "
                                 "mitad (11.6.5.2.2) y exige declarar tambien el "
                                 "armado del muro que cede "
                                 f"('{CRITERIO_REGIMEN_RESISTENCIA}' = 'cedente') --, "
                                 "un relleno de mayor friccion o un analisis "
                                 "externo" + PUERTA_EMPUJE_DECLARADO))
                    K_AE = 2 * P_unitario_E / (h ** 2 * (1.0 - k_v))
                elif not dominio_MO:
                    # --- VE-5 (ficha T7B-06) --- Mononobe-Okabe no es aceptable
                    # (11.6.5.3, ec. 11.6.5.3-1) y la fuente da la cuña de tanteo
                    # para ese caso (C11.6.5.3, «may also be used for situations
                    # when the M–O Method is not suitable»): con la superficie REAL
                    # del relleno, o con la pendiente declarada como talud sin
                    # quiebre si 'pendiente_relleno_trasdos_i' la declara. El
                    # INCREMENTO sale de la misma cuña (P_AE - P_A de la cuña, no
                    # menos el P_A de la formula: dos modelos no se restan) y el
                    # estatico sigue con la formula de la regla. Hasta VE-5 se
                    # detenia aqui.
                    if relleno["i_declarado"]:
                        sub_c = math.inf
                        talud_c = (1.0 / math.tan(math.radians(ang["i"]))
                                   if ang["i"] > TOL_UMBRAL_NORMATIVO else math.inf)
                    else:
                        sub_c, talud_c = relleno["subida_sobre_plano"], relleno["talud"]
                    remedio_c = (
                        f"Mononobe-Okabe tampoco es aceptable (AASHTO 11.6.5.3, ec. "
                        f"11.6.5.3-1: phi = {ang['phi']:.2f} < i + psi = "
                        f"{ang['i']:.2f} + {psi:.2f} grados). Lo que lo destraba es "
                        "una decision del Propietario -- admitir el desplazamiento "
                        f"del muro, '{CRITERIO_FACTOR_MURO}', que reduce k_h a la "
                        "mitad --, un relleno de mayor friccion o un analisis "
                        "externo; la cuña de archivo es "
                        f"'{CRITERIO_REGLA_PENDIENTE}' = '{REGLA_CUNA_DE_TANTEO}'"
                        + PUERTA_EMPUJE_DECLARADO)
                    if math.isinf(talud_c):
                        sub_c, talud_c = 0.0, relleno["talud"]
                    P1_c, _ = cuna_de_tanteo(
                        h=h, subida=sub_c, talud=talud_c, phi_grados=ang["phi"],
                        delta_grados=ang["delta"], gamma=1.0,
                        beta_grados=ang["beta"],
                        que=f"empuje estatico (cuña) del cabezal de {ext}",
                        id_punto=idp, remedio=remedio_c)
                    en_cuna_sismica = True
                    P1_cE, rho_AE = cuna_de_tanteo(
                        h=h, subida=sub_c, talud=talud_c, phi_grados=ang["phi"],
                        delta_grados=ang["delta"], gamma=1.0, k_h=k_h, k_v=k_v,
                        beta_grados=ang["beta"],
                        que=f"empuje sismico del cabezal de {ext}", id_punto=idp,
                        remedio=remedio_c)
                    K_AE = (K_A + 2 * (P1_cE - P1_c) / h ** 2) / (1.0 - k_v)
                    metodo_incremento = METODO_INCREMENTO_CUNA
                else:
                    K_AE = K_AE_formula
                P_AE = empuje_activo_sismico_total(gamma_relleno=gamma, K_AE=K_AE,
                                                   H=h, k_v=k_v)
                dP = P_AE - P_A
                if tratamiento_agua == AGUA_SE_MUEVE_CON_EL_SUELO:
                    # El incremento con el peso TOTAL bajo el agua (C11.6.5.3): la
                    # integral del peso total sobre el plano, Γ_t, en lugar de
                    # gamma·h²/2; el estatico (suelo sumergido mas hidrostatica) no
                    # cambia. En seco Γ_t = gamma·h²/2 y es la formula de arriba.
                    gamma_t = (gamma * h_seco ** 2 / 2 + gamma * h_seco * h_w
                               + gamma_sat * h_w ** 2 / 2)
                    dP = (K_AE * (1.0 - k_v) - K_A) * gamma_t
                    P_AE = P_A + dP
            except MetodoNoEvaluableError as exc:
                # --- VE-7 (lote A, A5) --- la cuña sin maximo (psi >=
                # phi, o el talud mas empinado que phi - psi): la fuente
                # pide el GLE de A11.3.3. Con el P_AE declarado, ese es.
                if not en_cuna_sismica:
                    raise
                if declarado is None:
                    if no_casa:
                        raise _no_evaluable(exc.que, exc.procedimiento,
                                            exc.motivo + no_casa,
                                            idp) from exc
                    raise
                usar_declarado = True
        forma_no_cede = None
        if usar_declarado:
            (K_AE, K_AE_formula, rho_AE, P_AE, dP, dP_h, dP_v, z_dP,
             fraccion, P_estatico, P_total, proc_h, proc_v,
             forma_no_cede) = _incremento_del_empuje_declarado(
                    declarado, h=h, gamma=gamma, k_v=k_v, P_A=P_A, P_0=P_0,
                    z_A=z_A, inclinacion=inclinacion,
                    reposo_rige=reposo_rige, regimen=regimen, ang=ang,
                    k_h=k_h, dominio_MO=dominio_MO, ext=ext, id_punto=idp)
            metodo_incremento = METODO_INCREMENTO_DECLARADO
        else:
            fraccion = ca.valor(CRITERIO_BRAZO_SISMICO)
            if not (_finito(fraccion) and 0 < fraccion <= 1):
                raise DatoInvalidoError(CRITERIO_BRAZO_SISMICO, valor=fraccion,
                                        motivo="fraccion de h entre 0 y 1")
            z_dP = fraccion * h
            distribucion = _eleccion(CRITERIO_DISTRIBUCION_INCREMENTO,
                                     (INCREMENTO_SEGUN_REGIMEN,
                                      INCREMENTO_FRACCION,
                                      INCREMENTO_DISTRIBUCION_ESTATICA))
            # --- VE-5 --- con 'regimen_cabezal' = 'no_cedente' el muro no cede
            # aunque la cadena declare la reduccion: manda el regimen.
            cede = (regimen == REGIMEN_CEDENTE
                    and ca.valor(CRITERIO_FACTOR_MURO)
                    == FACTOR_MURO_CON_REDUCCION)
            # --- VE-5 (ficha T7B-14) --- el empuje sismico del muro que no cede
            # sobre el reposo: el reposo mas el incremento pseudoestatico, o el
            # mayor del reposo y del total ('empuje_sismico_muro_que_no_cede'
            # [A]). Todo horizontal, como el reposo. Con el activo rigiendo, el
            # incremento de siempre (P_AE - P_A) con sus dos componentes.
            dP_h = dP * math.cos(inclinacion)
            dP_v = dP * math.sin(inclinacion)
            P_estatico, P_total = P_A, P_AE
            forma_no_cede = None
            if regimen == REGIMEN_NO_CEDENTE:
                forma_no_cede = _eleccion(CRITERIO_EMPUJE_SISMICO_NO_CEDE,
                                          EMPUJES_SISMICOS_NO_CEDE)
            if reposo_rige:
                if forma_no_cede == NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL:
                    dP_h = max((P_A + dP) * math.cos(inclinacion) - P_0, 0.0)
                dP_v = 0.0
                dP = dP_h
                P_estatico, P_total = P_0, P_0 + dP_h
            if distribucion == INCREMENTO_DISTRIBUCION_ESTATICA and not cede:
                raise DatoInvalidoError(
                    CRITERIO_DISTRIBUCION_INCREMENTO, valor=distribucion,
                    id_punto=idp,
                    motivo=("la distribucion estatica del incremento (11.6.5.3) "
                            "es del muro que CEDE, y "
                            f"'{CRITERIO_FACTOR_MURO}' no declara la "
                            "reduccion por desplazamiento: para el muro que "
                            "no cede C11.6.5.4 pide la resultante a h/2"))
            if (distribucion == INCREMENTO_DISTRIBUCION_ESTATICA
                    or (distribucion == INCREMENTO_SEGUN_REGIMEN and cede)):
                # --- VE-3.14, opcion 13; VE-3.15, derivada del regimen ---
                # AASHTO 11.6.5.3: el empuje total con la distribucion del
                # estatico, «but no less than H/3»: el incremento en el mayor
                # del centroide estatico y h/3 (muro que cede). El centroide del
                # diagrama ESTATICO con que se diseña el muro: el suelo (EH, a
                # z_A) y la sobrecarga (LS, uniforme, a h/2), en componente
                # horizontal; con la sobrecarga queda sobre h/3.
                H_EH = P_A * math.cos(inclinacion)
                H_LS = K_A * gamma * h_eq * h
                z_estatico = ((H_EH * z_A + H_LS * h / 2) / (H_EH + H_LS)
                              if H_EH + H_LS > 0 else z_A)
                z_dP = max(z_estatico, h / LADOS_DEL_TRIANGULO)
                fraccion = z_dP / h
            elif distribucion == INCREMENTO_SEGUN_REGIMEN and dP > 0:
                # --- VE-3.15, decision 13 --- Muro que NO cede: C11.6.5.4 pide
                # considerar la resultante del empuje estatico mas el sismico
                # en h/2 («a higher resultant location ... of h/2»), y se lee
                # como piso: el incremento sube lo necesario para que la
                # resultante no quede bajo h/2, y si la fraccion de archivo ya
                # la deja mas alta, se conserva. (VE-5: con el estatico que
                # rige, el reposo del muro que no cede si es el caso.)
                z_h_medios = (P_total * h / 2 - P_estatico * z_A) / dP
                if z_h_medios > z_dP:
                    z_dP = z_h_medios
                    fraccion = z_dP / h
            if reposo_rige:
                proc_h = (("max[P_AE·cos(delta + beta) - P_0, 0] (el mayor del "
                           "reposo y del total)"
                           if forma_no_cede == NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL
                           else "(P_AE - P_A)·cos(delta + beta), sobre el "
                                "reposo")
                          + f" con k_h = 1.0·k_h0, a {fraccion:g}·h")
                proc_v = ("sin componente vertical: sobre el reposo no se "
                          "moviliza la friccion muro-relleno")
            else:
                proc_h = f"(P_AE - P_A)·cos(delta + beta), a {fraccion:g}·h"
                proc_v = "(P_AE - P_A)·sen(delta + beta)"
        cargas.append(CargaDeCabezal(
            C_EQ_H, CARGA_EQ, "incremento sismico del empuje, horizontal",
            H=dP_h, z=z_dP, sobre=ELEMENTO_PANTALLA, procedencia=proc_h))
        cargas.append(CargaDeCabezal(
            C_EQ_V, CARGA_EQ, "incremento sismico del empuje, vertical",
            V=dP_v, x=x_plano, sobre=ELEMENTO_ZAPATA, procedencia=proc_v))
        z_muro = ((W_pant * z_pant + W_zap * e_z / 2)
                  / (W_pant + W_zap))
        cargas.append(CargaDeCabezal(
            C_EQ_PIR_MURO, CARGA_EQ, "inercia del muro", H=k_h * (W_pant + W_zap),
            z=z_muro, sobre=ELEMENTO_PANTALLA,
            procedencia=f"k_h·W_w = {k_h:.3f}·{W_pant + W_zap:.3f}"))
        if W_s > 0:
            cargas.append(CargaDeCabezal(
                C_EQ_PIR_SUELO, CARGA_EQ,
                "inercia del relleno sobre el talon", H=k_h * W_s, z=z_s,
                sobre=ELEMENTO_ZAPATA,
                procedencia=f"k_h·W_s = {k_h:.3f}·{W_s:.3f}"))
        if abs(k_v) > TOL_UMBRAL_NORMATIVO:
            pesos = [c for c in cargas
                     if c.codigo in (C_DC_PANTALLA, C_DC_ZAPATA, C_EV_TALON)]
            W_v = sum(c.V for c in pesos)
            if W_v > 0:
                cargas.append(CargaDeCabezal(
                    C_EQ_KV, CARGA_EQ,
                    "aceleracion vertical sobre los pesos estabilizantes",
                    V=-k_v * W_v, x=sum(c.V * c.x for c in pesos) / W_v,
                    sobre=ELEMENTO_ZAPATA,
                    procedencia=(f"k_v·(W_w + W_s) = {k_v:g}·{W_v:.3f}, "
                                 "hacia arriba (signo desfavorable)")))
        datos.update(K_AE=K_AE, k_h=k_h, k_v=k_v, P_AE=P_AE,
                     tratamiento_agua_sismo=tratamiento_agua,
                     z_AE=((P_estatico * z_A + dP * z_dP) / P_total
                           if P_total > 0 else z_A),
                     P_total_sismico=P_total,
                     empuje_sismico_no_cede=forma_no_cede,
                     fraccion_brazo=fraccion, psi=psi,
                     K_AE_formula=K_AE_formula, rho_AE=rho_AE,
                     metodo_incremento=metodo_incremento,
                     empuje_sismico_declarado=(declarado if usar_declarado
                                               else None),
                     # --- dictamen Fable (5.7) --- declarado y NO usado:
                     # el programa calculo el empuje.
                     empuje_declarado_no_usado=bool(
                         getattr(entorno, "empuje_sismico", None))
                     and not usar_declarado)
    return tuple(cargas), datos


# ---------------------------------------------------------------------------
# Las combinaciones de cada marco
# ---------------------------------------------------------------------------

def _combinar(nombre: str, marco: str, condicion: CondicionAnalisis,
              cargas: tuple, factores: dict, B: float,
              para: str) -> CombinacionDeEstabilidad:
    """Aplica `factores` (codigo -> factor) a las cargas y suma."""
    pares = tuple((c.codigo, float(factores.get(c.codigo, 0.0)))
                  for c in cargas)
    f = dict(pares)
    N = sum(f[c.codigo] * c.V for c in cargas)
    H = sum(f[c.codigo] * c.H for c in cargas)
    M_e = sum(f[c.codigo] * c.V * c.x for c in cargas if c.V > 0)
    M_v = (sum(f[c.codigo] * c.H * c.z for c in cargas)
           + sum(f[c.codigo] * -c.V * c.x for c in cargas if c.V < 0))
    for nombre_x, x in (("N", N), ("H", H), ("M_e", M_e), ("M_v", M_v)):
        if not math.isfinite(x):
            raise LimiteNumericoError(
                nombre_x, valor=x,
                motivo=f"la resultante de la combinacion «{nombre}» no es "
                       "finita")
    return CombinacionDeEstabilidad(
        nombre=nombre, marco=marco, condicion=condicion, factores=pares,
        N=N, H=H, M_estabilizante=M_e, M_volcante=M_v, B=B, para=para)


def modificador_de_carga() -> dict:
    """
    --- verificacion de T-7 (punto 9; cierra la ficha T7C-11) --- El
    modificador de carga eta de AASHTO LRFD 1.3.2.1 (pag. impresa 1-3, PDF
    18; cita AASHTO_LRFD_9.1.3.2.1#ETA) para las combinaciones de
    RESISTENCIA I del cabezal:

        Σ eta_i·gamma_i·Q_i <= phi·R_n                        (1.3.2.1-1)
        cargas de gamma maximo:  eta_i = eta_D·eta_R·eta_I >= 0.95   (-2)
        cargas de gamma minimo:  eta_i = 1/(eta_D·eta_R·eta_I) <= 1.0 (-3)

    eta_I es la importancia operativa del CRUCE, el MISMO criterio que lee
    la Fase 8 del conducto ('eta_importancia_operativa_conducto' [A], 1.05
    de archivo): hasta aqui el cabezal usaba 1.00 implicito, sin criterio ni
    paso, junto a un conducto mayorado con 1.05. eta_D y eta_R son del
    cabezal ('eta_ductilidad_cabezal' y 'eta_redundancia_cabezal' [A], 1.00
    convencional por 1.3.3 y 1.3.4).

    Devuelve los tres factores, su producto y los dos eta_i ya acotados:
    `maximo` (el que multiplica a las cargas de gamma maximo) y `minimo` (a
    las de gamma minimo). EN EL EVENTO EXTREMO I Y EN SERVICIO NO SE LLAMA:
    «For all other limit states» los tres valen 1.00 (1.3.3, 1.3.4 y 1.3.5).
    Y es del marco LRFD: el ASD de E.050 y el contraste de E.060 no llevan
    eta (los marcos no se cruzan).
    """
    factores = {}
    for nombre, clave in (("eta_D", CRITERIO_ETA_DUCTILIDAD),
                          ("eta_R", CRITERIO_ETA_REDUNDANCIA),
                          ("eta_I", CRITERIO_ETA_IMPORTANCIA)):
        factores[nombre] = _exigir_positivo(
            clave, ca.valor(clave), f"modificador de carga {nombre}")
    producto = factores["eta_D"] * factores["eta_R"] * factores["eta_I"]
    if not (math.isfinite(producto) and producto > 0):
        raise LimiteNumericoError(
            "eta", valor=producto,
            motivo="el producto eta_D·eta_R·eta_I no es finito y positivo")
    return dict(factores, producto=producto,
                maximo=max(producto, ETA_PISO_GAMMA_MAXIMO_AASHTO),
                minimo=min(1 / producto, ETA_TECHO_GAMMA_MINIMO_AASHTO))


def _resistencia_i_con_eta(g: dict, EH_max: float) -> Tuple[dict, dict]:
    """
    Los factores de las dos variantes de Resistencia I del cabezal --
    maximos y minimos -- con el modificador de carga DENTRO (gamma·eta_i):
    en la de maximos todas las cargas llevan `maximo`; en la de minimos el
    peso propio (DC) y el relleno sobre el talon (EV), que son las que la
    Tabla 3.4.1-2 gradua con un minimo, llevan `minimo`, y el empuje (EH,
    con su maximo), la sobrecarga viva y el agua --cargas de factor unico,
    desfavorables alli-- siguen con `maximo` (la lectura, en la
    `Interpretacion` de la cita). `EH_max` es el gamma_p maximo del empuje
    que corresponda: el activo, o el de reposo en el armado.
    """
    eta = modificador_de_carga()
    mas, menos = eta["maximo"], eta["minimo"]
    maximos = dict(DC=mas * g["DC"]["max"], EV=mas * g["EV"]["max"],
                   EH=mas * EH_max, LS=mas * g["LS"],
                   WA=mas * g["WA"]["max"])
    minimos = dict(DC=menos * g["DC"]["min"], EV=menos * g["EV"]["min"],
                   EH=mas * EH_max, LS=mas * g["LS"], LS_v=0.0,
                   WA=mas * g["WA"]["max"])
    return maximos, minimos


def _casos_sismicos(datos: dict) -> Tuple[Tuple[str, float, float, float], ...]:
    """
    Los dos casos del num. 11.6.5.1 (`P_SEIS_COMBINACIONES`), como factores
    sobre el empuje estatico (EH), el incremento (P_AE - P_A) y la inercia:

        100 % P_AE + 50 % P_IR   ->  EH 1, incremento 1, inercia 0.5
        50 % P_AE + 100 % P_IR   ->  si 0.5·P_AE >= P_A: EH 0.5, incremento
                                     0.5; si no rige el PISO estatico: EH 1,
                                     incremento 0. Inercia 1.
    """
    casos = []
    # --- VE-5 --- el piso es el empuje estatico que RIGE (el reposo del
    # muro que no cede, si es el caso) frente al total sismico.
    P_est = datos.get("P_estatico") or datos["P_A"]
    P_tot = datos.get("P_total_sismico") or datos["P_AE"]
    for nombre, f_ae, f_ir in P_SEIS_COMBINACIONES:
        con_piso = (nombre == P_SEIS_PISO_ESTATICO
                    and f_ae * P_tot < P_est)
        if con_piso:
            casos.append((nombre + " (rige el piso del empuje estatico)",
                          1.0, 0.0, f_ir))
        else:
            casos.append((nombre, f_ae, f_ae, f_ir))
    return tuple(casos)


def combinaciones_de_estabilidad(cargas: tuple, datos: dict,
                                 condicion: CondicionAnalisis, B: float
                                 ) -> Tuple[CombinacionDeEstabilidad, ...]:
    """
    Las combinaciones de UN cabezal en UNA condicion, en los DOS marcos.

    MARCO LRFD (AASHTO 3.4.1 y C11.5.6, Figuras C11.5.6-1, -2 y -4):
      estatica   «Resistencia I, maximos» para el portante: gamma_p maximos
                 de DC y EV, EH maximo, LS 1.75 con su peso sobre el talon;
                 «Resistencia I, minimos» para la excentricidad y el
                 deslizamiento: gamma_p MINIMOS de DC y EV, EH maximo en sus
                 dos componentes, LS 1.75 solo como empuje.
      sismica    «Evento Extremo I», por cada caso del 11.6.5.1: permanentes
                 y sismo con 1.00, LS con gamma_EQ; una variante con el peso
                 de la sobrecarga (portante) y otra sin el.
    WA va siempre con 1.00 (C11.5.6).

    --- dictamen Fable (VE-7 lote A, abierto (i)) --- La carga
    `C_EQ_KV` (-k_v·(W_w + W_s), solo con k_v distinto de cero) va con
    factor 1.0 en las filas de excentricidad, deslizamiento y volteo, en
    los dos casos de 11.6.5.1, y con 0 en las «(portante)».

    --- verificacion de T-7 (punto 9) --- Y EN RESISTENCIA I CADA FACTOR
    LLEVA EL MODIFICADOR DE CARGA eta_i de AASHTO 1.3.2.1
    (`modificador_de_carga`, `_resistencia_i_con_eta`): eta en las cargas
    de gamma maximo y 1/eta en las de gamma minimo. En el Evento Extremo I
    vale 1.00 y no se aplica. `CombinacionDeEstabilidad.factores` guarda el
    producto gamma·eta_i, que es lo que multiplica a la carga.

    MARCO ASD (E.050 Art. 17.1): TODAS las cargas con factor 1, en las
    mismas variantes (con y sin el peso de la sobrecarga viva). Sin eta: es
    de otro marco.
    """
    codigos = [c.codigo for c in cargas]
    combos = []

    def factores(**por_tipo) -> dict:
        f = {}
        for c in cargas:
            f[c.codigo] = por_tipo.get(c.codigo.replace(".", "_"),
                                       por_tipo.get(c.tipo, 0.0))
        return f

    if condicion is CondicionAnalisis.ESTATICO:
        g = factores_de_carga("Resistencia I")
        # --- VE-5 (ficha T7B-14) --- con el empuje en reposo del muro que
        # no cede, el gamma_p de la fila «En reposo» de la Tabla 3.4.1-2
        # (1.35), no el de la activa (1.50).
        EH_max = (TABLA_GAMMA_P_FILAS[FILA_EH_EN_REPOSO]["max"]
                  if datos.get("empuje_estatico") == EMPUJE_ESTATICO_REPOSO
                  else g["EH"]["max"])
        maximos, minimos = _resistencia_i_con_eta(g, EH_max)
        combos.append(_combinar(
            "Resistencia I (maximos)", MARCO_LRFD, condicion, cargas,
            factores(**maximos), B, "portante"))
        combos.append(_combinar(
            "Resistencia I (minimos)", MARCO_LRFD, condicion, cargas,
            factores(**minimos), B, "excentricidad y deslizamiento"))
        combos.append(_combinar(
            "Servicio (portante)", MARCO_ASD, condicion, cargas,
            factores(DC=1.0, EV=1.0, EH=1.0, LS=1.0, WA=1.0), B, "portante"))
        combos.append(_combinar(
            "Servicio (volteo y deslizamiento)", MARCO_ASD, condicion, cargas,
            factores(DC=1.0, EV=1.0, EH=1.0, LS=1.0, LS_v=0.0, WA=1.0), B,
            "volteo y deslizamiento"))
        return tuple(combos)

    g = factores_de_carga("Evento Extremo I")
    g_eq = gamma_eq()
    if not (_finito(g_eq) and 0 <= g_eq <= 1):
        raise DatoInvalidoError(CRITERIO_GAMMA_EQ, valor=g_eq,
                                motivo="gamma_EQ entre 0 y 1")
    for nombre, f_eh, f_inc, f_ir in _casos_sismicos(datos):
        comunes = dict(DC=g["DC"]["max"], EV=g["EV"]["max"],
                       WA=g["WA"]["max"], EH=f_eh * g["EH"]["max"],
                       EQ_dPAE_h=f_inc, EQ_dPAE_v=f_inc,
                       EQ_PIR_muro=f_ir, EQ_PIR_suelo=f_ir)
        combos.append(_combinar(
            f"Evento Extremo I, {nombre} (portante)", MARCO_LRFD, condicion,
            cargas, factores(LS=g_eq, **comunes), B, "portante"))
        combos.append(_combinar(
            f"Evento Extremo I, {nombre}", MARCO_LRFD, condicion, cargas,
            factores(LS=g_eq, LS_v=0.0, EQ_kv_pesos=1.0, **comunes), B,
            "excentricidad y deslizamiento"))
        servicio = dict(comunes, DC=1.0, EV=1.0, WA=1.0, EH=f_eh)
        combos.append(_combinar(
            f"Servicio con sismo, {nombre} (portante)", MARCO_ASD, condicion,
            cargas, factores(LS=1.0, **servicio), B, "portante"))
        combos.append(_combinar(
            f"Servicio con sismo, {nombre}", MARCO_ASD, condicion, cargas,
            factores(LS=1.0, LS_v=0.0, EQ_kv_pesos=1.0, **servicio), B,
            "volteo y deslizamiento"))
    del codigos
    return tuple(combos)
