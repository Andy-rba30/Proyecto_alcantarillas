# -*- coding: utf-8 -*-
"""
M9_cabezal._criterios
=====================
Submodulo de Fase 9 (`M9_cabezal`): bloque `_criterios` (D1).
"""

from __future__ import annotations

import math
from typing import Optional

from dataclasses import replace as _reemplazar
from src import criterios_adoptados as ca
from src.constantes_normativas import (
    FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1,
    FS,
    FS_CODIGO,
    NUMERAL_CORTANTE_MUROS_E060,
    NUMERAL_F_PGA_TABLA,
    RECUBRIMIENTO_BARRA_GRUESA_DESDE,
)
from src.modelos import (
    CondicionAnalisis,
    DatoInvalidoError,
    ELEMENTO_ALEROS,
    ELEMENTO_PANTALLA,
    ELEMENTO_ZAPATA,
    ELEMENTO_ZAPATA_ALEROS,
    EmbocaduraDelPunto,
    EstabilidadDelCabezal,
    MURO_ALERO,
    ReferenciaNormativa,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

# --------------------------------------------------------------------------
# Numerales
# --------------------------------------------------------------------------

NUMERAL_9_1 = ReferenciaNormativa(
    seccion_hoja_ruta="Sec. 9.1",
    numeral_norma="EG-2013, Capitulo V, Seccion 503 (concreto estructural), "
                  "num. 503.01, pag. 905",
)


NUMERAL_9_2 = "Sec. 9.2"


NUMERAL_9_3 = "Sec. 9.3 (E.050)"


NUMERAL_MO = "Sec. 9.2 (Mononobe-Okabe)"


NUMERAL_PGA = "Manual de Puentes, Apendice A3, mapa PGA T = 0.0 seg"


NUMERAL_F_PGA = NUMERAL_F_PGA_TABLA


NUMERAL_SUBPRESION = "Manual de Puentes num. 2.4.3.8.2"


NUMERAL_FLEXION_CORTE = "Sec. 9.4 (AASHTO LRFD Seccion 5, via Seccion 2.9)"


NUMERAL_REGLA_RECUBRIMIENTO = "Sec. 0.2 (rige el recubrimiento mayor)"


# El Art. 11.10.10.2 esta en la hoja de ruta desde EXT-0 (v8 §9.4) y en el
# registro desde EXT-6 (`constantes_normativas.NUMERAL_CORTANTE_MUROS_E060`,
# con 11.10.1, 11.10.2 y 11.10.10.3); lo que sigue pendiente es CABLEAR su
# valor con caso patron (EXT-7). Ver el criterio
# 'cortante_alto_muro_e060_art_11_10_10_2'.
NUMERAL_CORTANTE_ALTO = (NUMERAL_CORTANTE_MUROS_E060["cuantia_horizontal_min"]
                         + " (cortante alto en el plano; piso declarado en "
                           "'cortante_alto_muro_e060_art_11_10_10_2')")


# El piso VERTICAL bajo el mismo regimen (EXT-M-05 / R95-031) y las dos
# lecturas del plano del cortante que deciden si el regimen rige.
NUMERAL_CORTANTE_ALTO_VERTICAL = (
    NUMERAL_CORTANTE_MUROS_E060["cuantia_vertical_min"]
    + " (ec. 11-32, cortante alto en el plano; piso declarado en "
      "'cuantia_vertical_cortante_alto_e060_art_11_10_10_3')")


NUMERAL_CORTANTE_EN_EL_PLANO = NUMERAL_CORTANTE_MUROS_E060["en_el_plano"]


NUMERAL_CORTANTE_PERPENDICULAR = (
    NUMERAL_CORTANTE_MUROS_E060["perpendicular_al_plano"]
    + " (cortante perpendicular al plano: diseño por 11.12, el regimen de "
      "11.10.10 no rige)")


CALCULADO = "Calculado"


ETIQUETA_CALCULADO = "-"


# --------------------------------------------------------------------------
# Claves de criterios_adoptados
# --------------------------------------------------------------------------

# El PGA no es un criterio: es un dato de sitio [S] y vive en datos_sitio.py.
DATO_SITIO_PGA = "PGA_roca_B"


CRITERIO_F_PGA = "F_pga"


CRITERIO_F_PGA_LECTURA = "F_pga_lectura_columna_extrema"


CRITERIO_FACTOR_MURO = "factor_muro_eleccion"


CRITERIO_K_V = "k_v"


CRITERIO_GAMMA_EQ = "gamma_EQ"


CRITERIO_PHI_RELLENO = "phi_relleno_trasdos"


CRITERIO_I_RELLENO = "pendiente_relleno_trasdos_i"


CRITERIO_BETA_MURO = "inclinacion_muro_beta"


CRITERIO_DELTA_MURO = "friccion_muro_suelo_delta"


CRITERIO_BRAZO_SISMICO = "punto_aplicacion_incremento_sismico"


CRITERIO_FACTORES_CARGA = "factores_carga_aashto"


CRITERIO_GAMMA_RELLENO = "peso_especifico_relleno_kn_m3"


CRITERIO_GAMMA_CONCRETO = "peso_especifico_concreto_kn_m3"


CRITERIO_GEOMETRIA = "predimensionamiento_cabezal"


# --- VE-3.5 --- El paso y el tope del dimensionamiento de la zapata por
# estabilidad (`dimensionar_zapata_por_estabilidad`), [A] sin valor de
# archivo.
CRITERIO_DIMENSIONAMIENTO_ZAPATA = "dimensionamiento_zapata_cabezal"


# El NF ya no es criterio: es la columna 'NF_profundidad_m' del CSV, medida en
# cada cruce. Entra por argumento a las funciones que lo necesitan.

# --- VE-5 (ficha T7B-04) --- 'N_cq_N_gammaq_meyerhof' se RETIRO: la zapata
# en talud se calcula con la RC_BC de AASHTO 10.6.3.1.2c (tablas transcritas)
# sobre la geometria del talud de 'talud_delante_del_cabezal' [S].
CRITERIO_TALUD_DELANTE = "talud_delante_del_cabezal"


CRITERIO_PORTANTE_ADMISIBLE = "capacidad_portante_adm"


CRITERIO_FORMA_PROFUNDIDAD = "factores_forma_profundidad_portante"


FORMA_CORRIDA = "corrida_sin_profundidad"


FORMA_CON_LONGITUD = "forma_con_la_longitud_del_cabezal"


FORMA_Y_PROFUNDIDAD = "forma_y_profundidad"


OPCIONES_FORMA_PROFUNDIDAD = (FORMA_CORRIDA, FORMA_CON_LONGITUD,
                              FORMA_Y_PROFUNDIDAD)


CAMPOS_TALUD_DELANTE = ("H_s_m", "beta_grados", "b_m")


CRITERIO_ESTABILIDAD_GLOBAL = "metodo_estabilidad_global"


CRITERIO_TABLA_RECUBRIMIENTO = "tabla_recubrimiento_aashto_mm"


# Las dos lagunas de las tablas de h_eq de AASHTO 3.11.6.4, que el registro
# declara y que hasta esta sesion se resolvian en duro dentro del modulo.
CRITERIO_H_EQ_BAJO_TABLA = "h_eq_bajo_altura_tabulada"


CRITERIO_H_EQ_BANDA_BORDE = "h_eq_banda_intermedia_borde"


H_EQ_BAJO_TABLA_PRIMERA_FILA = "primera_fila"


H_EQ_BAJO_TABLA_EXTRAPOLAR = "extrapolar_lineal"


H_EQ_BANDA_LEE_COLUMNA_CERO = "columna_cero"


H_EQ_BANDA_INTERPOLA = "interpolar_entre_columnas"


CRITERIO_CATEGORIA_REFUERZO = "categoria_refuerzo_aashto"


CRITERIO_SITUACION_RECUBRIMIENTO = "situacion_recubrimiento_aashto"


CRITERIO_EXPOSICION_QUIMICA = "exposicion_quimica_ems"


CRITERIO_FACTOR_BANDA_AC = "factor_recubrimiento_banda_intermedia_ac"


# Claves obligatorias del dato de sitio 'exposicion_quimica_ems'. Se exigen
# TODAS y presentes: una clave ausente no es una lectura negativa.
CLAVES_ESCALAS_SULFATOS = ("so4_suelo_pct", "so4_agua_ppm")


CLAVE_FILAS_TABLA_4_2 = "tabla_4_2"


NOMBRE_TABLA_4_2 = "Tabla 4.2"


NOMBRE_TABLA_4_4 = "Tabla 4.4"


# La columna de la Tabla 5.10.1-1 que el corpus PERUANO tambien tabula: el
# Manual de Puentes transcribe esa y solo esa ("aceros no protegidas"). Con
# cualquiera de las otras dos, el numero deja de ser [N] y pasa a ser el [C]
# con que la Via 1 de Sec. 0.2 cubre lo que el corpus peruano no tabula.
CATEGORIA_ACERO_SIN_RECUBRIR = "A"


CRITERIO_FLEXION_CORTE = "procedimiento_flexion_corte_aashto_sec5"


CRITERIO_CORTANTE_ALTO = "cortante_alto_muro_e060_art_11_10_10_2"


CRITERIO_REGIMEN_CORTANTE = "regimen_cortante_muro_e060_art_11_10_2"


CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO = (
    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3")


# LAS FILAS QUE LA TABLA DE SEC. 9.3 EXIGE, por su codigo y en su orden,
# derivadas de `constantes_normativas.FS` y no escritas aqui (EXT-M-07).
# `EstabilidadCabezal.estable` se mide contra esta tupla. E6 (la
# excentricidad sismica, `verificar_excentricidad_sismica`) NO esta: no es
# fila de esa tabla -- E.050 no la escribe; sale del Manual de Puentes -- y
# quien la quiera exigir la pasa ampliando `exigidas` en
# `verificar_estabilidad`. La decision esta en docs/decisiones_diferidas.md.
EXIGIDAS_SEC_9_3 = tuple(FS_CODIGO[clave] for clave in FS)


# Componentes de cada combinacion de Sec. 9.2, con la nomenclatura de cargas
# de AASHTO LRFD. Son NOMBRES, no factores: los factores son [N] y estan en
# `constantes_normativas.TABLA_COMBINACIONES_FILAS` y `TABLA_GAMMA_P_FILAS`.
COMPONENTES_COMBINACION = {
    "Resistencia I": ("DC", "EV", "EH", "LS", "WA"),
    "Servicio I": ("DC", "EV", "EH", "LS", "WA"),
    "Evento Extremo I": ("DC", "EV", "EH", "LS", "WA", "EQ"),
}


CRITERIO_TALUD_TERRAPLEN = "talud_terraplen"


CRITERIO_PERALTE_ZAPATA_ARMADA = "peralte_min_zapata_armada_m"


# El recubrimiento del refuerzo inferior de la zapata armada, contra el
# suelo: E.060 7.7.1 a), la fila de `RECUBRIMIENTO` que la §0.2 de la hoja de
# ruta admite por la excepcion de durabilidad.
CONDICION_RECUBRIMIENTO_ZAPATA = "contra_suelo"


ORIENTACION_PARALELO_A_LA_VIA = "paralelo_a_la_via"


EXTREMO_ENTRADA = "entrada"


EXTREMO_SALIDA = "salida"


EXTREMOS = (EXTREMO_ENTRADA, EXTREMO_SALIDA)


TIPO_VOLADIZO = "voladizo_armado"


TIPO_GRAVEDAD = "gravedad_ciclopeo"


# ---------------------------------------------------------------------------
# Guardias de segunda linea (forma MAT-D13: condicion en positivo y negada)
# ---------------------------------------------------------------------------

def _finito(x: object) -> bool:
    return (not isinstance(x, bool) and isinstance(x, (int, float))
            and math.isfinite(x))


def _exigir_positivo(campo: str, x: object, que: str,
                     id_punto: Optional[str] = None) -> float:
    if not (_finito(x) and x > 0):
        raise DatoInvalidoError(campo, valor=x, id_punto=id_punto,
                                motivo=f"{que}: se espera un numero finito "
                                       "mayor que cero")
    return float(x)


def _exigir_finito(campo: str, x: object, que: str,
                   id_punto: Optional[str] = None) -> float:
    if not _finito(x):
        raise DatoInvalidoError(campo, valor=x, id_punto=id_punto,
                                motivo=f"{que}: se espera un numero finito")
    return float(x)


def es_paralelo_a_la_via(embocadura: EmbocaduraDelPunto) -> bool:
    """--- VE-6 (ficha T7A-03) --- El muro de cabecera va paralelo a la via."""
    return embocadura.orientacion == ORIENTACION_PARALELO_A_LA_VIA


# ---------------------------------------------------------------------------
# Compatibilidad cabezal-conducto: CB1 a CB7 (T-7a punto 4 y correcciones)
# ---------------------------------------------------------------------------

def _caracter_de(cita_id: str) -> str:
    """El caracter de una cita, leido del registro y no escrito a mano."""
    from src.normativa import registro as _registro
    return _registro.construir().cita(cita_id).caracter.value.upper()


CRITERIO_TERRENO_DELANTE = "terreno_delante_del_cabezal"


CITA_ETA = "AASHTO_LRFD_9.1.3.2.1#ETA"


CITAS_DE_ETA = (CITA_ETA, "AASHTO_LRFD_9.1.3.3", "AASHTO_LRFD_9.1.3.4",
                "AASHTO_LRFD_9.1.3.5")


TERRENO_HORIZONTAL = "horizontal"


TERRENO_TALUD = "talud_descendente"


CONDICIONES_DE_ESTABILIDAD = (CondicionAnalisis.ESTATICO,
                              CondicionAnalisis.SISMICO)


ABREVIATURA_DE_CONDICION = {CondicionAnalisis.ESTATICO: "est",
                            CondicionAnalisis.SISMICO: "sis"}


PHI_MAX_TABLA_GRADOS = max(FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1)


# ===========================================================================
# --- T-7c --- 9.4 · EL ARMADO DE CADA CABEZAL (o su alternativa ciclopea)
# ===========================================================================
# INF-4.6, la ficha EXT-7-01 y el `NotImplementedError` de
# `diseno_flexion_corte`. T-7b dejo las solicitaciones factoradas de cada
# elemento; este bloque las convierte en acero.
#
# QUE NORMA ARMA (resolucion del encargo, coherente con el marco que rige la
# estabilidad): la RESISTENCIA se verifica con AASHTO LRFD Seccion 5 -- 5.6
# flexion, 5.7 cortante con el procedimiento simplificado de 5.7.3.4.1 donde
# la fuente lo permite, factores de 5.5.4.2 y de 1.3.2.1 -- sobre las cargas
# factoradas de Resistencia I y de Evento Extremo I. E.060 se calcula EN
# PARALELO como contraste [N→], con SUS combinaciones (9.2.5) y SUS factores
# de reduccion (9.3.2): nunca cargas de un marco con phi del otro. En los
# MINIMOS constructivos (acero minimo, espaciamiento maximo) se aplica el mas
# exigente de los dos ('regla_minimos_constructivos_cabezal' [A]).
#
# CON QUE EMPUJE ('regimen_resistencia_elementos_cabezal' [A]): por archivo,
# en REPOSO. La estabilidad externa de T-7b no cambia (muro que cede); lo que
# cambia es el empuje con que se arma cada elemento:
#
#   estatica   el empuje del suelo pasa de P_A a (K0 / K_A)·P_A, HORIZONTAL
#              (en reposo no hay friccion muro-relleno movilizada: la
#              componente vertical del empuje desaparece), y el de la
#              sobrecarga viva de K_A·gamma·h_eq·h a K0·gamma·h_eq·h. El
#              peso propio, el peso del relleno, el peso de la sobrecarga y
#              el agua NO se escalan. El factor de carga del empuje es el de
#              la fila «En reposo» (1.35), no el de la activa (1.50). En cada
#              seccion rige la MAYOR de esa solicitacion y la del muro que
#              cede: el K0 de 3.11.5.2-1 es de terreno horizontal y detras
#              del cabezal el relleno sube, de modo que el reposo calculado
#              puede quedar por debajo del activo de la cuña.
#   sismica    la fuente no da un coeficiente sismico de reposo. Se arma con
#              el empuje que el ensamble entrega y, para el momento de la
#              pantalla, con la mayor de su posicion y h/2 (C11.6.5.4). Si la
#              cadena sismica redujo k_h por desplazamiento, se AVISA: para
#              el muro que no cede 11.6.5.4 manda k_h = 1.0·k_h0.
#
# LO QUE NO HACE, y lo dice (fichas T7C-*): el control de fisuracion en
# servicio de AASHTO 5.6.7; el procedimiento general de cortante de
# 5.7.3.4.2; el refuerzo transversal; la zapata de los aleros (desde VE-6 su
# fuste se arma en el arranque y en la mitad, ficha VE6M9-03); el desarrollo
# y los empalmes de las barras; y la iteracion
# de dimensiones (arma la geometria que recibe, pase o no su estabilidad).
#
# UNIDADES: m, kN/m y kN·m/m por metro de muro; f'c y fy en MPa; areas de
# acero en mm2/m; recubrimientos y diametros en mm (como el Art. 7.7.1).

from dataclasses import replace as _reemplazar  # noqa: E402

from src.constantes_fisicas import KPA_POR_MPA, N_POR_KN, PULGADA_EN_MM  # noqa: E402
from src.constantes_normativas import ALTURA_VOLADIZO_ACTIVO_M  # noqa: E402
from src.constantes_normativas import (  # noqa: E402
    ALFA_1_BLOQUE_AASHTO, ALFA_BLOQUE_E060, BETA_1_BLOQUE_AASHTO,
    BETA_1_E060, BETA_1_E060_MINIMO, BETA_1_MINIMO,
    BETA_1_REDUCCION_AASHTO_SI, CORTANTE_CONCRETO_SIMPLE_E060,
    CUANTIA_MIN_CARA_TRACCION_E060, CUANTIA_MIN_LOSA_E060,
    DV_PISO_SOBRE_DE, DV_PISO_SOBRE_H, E060_FACTOR_CE, E060_FACTOR_CM,
    E060_FACTOR_CM_MINIMO, E060_FACTOR_CV, EC_11_32_ESBELTEZ,
    EC_11_32_FACTOR, EPSILON_CU_CONCRETO, EPSILON_T_MIN_E060,
    EPSILON_TL_AASHTO, ESPACIAMIENTO_MAX_ABSOLUTO_AASHTO_M,
    ESPACIAMIENTO_MAX_VECES_ESPESOR_AASHTO,
    FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO, FC_BETA_1_E060_MPA,
    FC_DISENO_MAX_CICLOPEO_MPA, FC_MAX_ALFA_1_MPA, FC_MAX_BETA_1_MPA,
    FY_ACERO_MPA, FY_MAX_EPSILON_TL_MPA, GAMMA_1_AGRIETAMIENTO_AASHTO,
    GAMMA_3_AASHTO, MODULO_ROTURA_AASHTO_SI, NUCLEO_CENTRAL_DIVISOR,
    PERALTE_MAX_SIMPLIFICADO_AASHTO_SI, PHI_CICLOPEO_E060, PHI_CORTE_E060,
    PHI_FLEXION_E060, RECUBRIMIENTO_BARRA_GRUESA_DESDE,
    REDUCCION_PERALTE_CONTRA_SUELO_M,
    TEMPERATURA_AS_MAX_AASHTO_SI, TEMPERATURA_AS_MIN_AASHTO_SI,
    TEMPERATURA_COEFICIENTE_AASHTO_SI, TEMPERATURA_ESPESOR_GRUESO_M,
    TEMPERATURA_S_MAX_GRUESO_M, TEMPERATURA_S_PISO_M,
    TEMPERATURA_S_VECES_ESPESOR, TRACCION_CONCRETO_SIMPLE_E060,
    VC_COEFICIENTE_AASHTO_SI, VC_COEFICIENTE_E060,
    VN_TOPE_SOBRE_FC_AASHTO, ZAPATA_SIMPLIFICADO_VECES_DV,
    GENERAL_BETA_NUMERADOR, GENERAL_BETA_COEF_DEFORMACION,
    GENERAL_BETA_NUMERADOR_SXE_IN, GENERAL_BETA_SUMANDO_SXE_IN,
    SXE_FACTOR_AGREGADO, SXE_SUMANDO_AGREGADO_IN, SXE_MIN_IN, SXE_MAX_IN,
    EC_COEFICIENTE_AASHTO_SI, EC_EXPONENTE_AASHTO, ES_REFUERZO_AASHTO_MPA,
    EXCENTRICIDAD_MIN_MURO_CONCRETO_SIMPLE_E060, FISURACION_BETA_S_FACTOR,
    FISURACION_COEFICIENTE_AASHTO_SI, FISURACION_FRACCION_FR,
    FISURACION_FSS_MAX_SOBRE_FY, FISURACION_GAMMA_E)
from src.modelos import (  # noqa: E402
    CIFRAS_FINA, CLASE_EXPOSICION_1, CLASE_EXPOSICION_2,
    CLASES_DE_EXPOSICION, CRITERIOS_DE_TRACCION_CICLOPEO,
    EstadoDeVerificacion, ArmadoDeSeccion,
    ArmadoDelCabezal, BarraPropuesta, FilaDeArmado, MARCO_E060,
    MINIMOS_MAS_EXIGENTE, MOTIVO_METODO_NO_EVALUABLE_ARMADO,
    REGIMEN_RESISTENCIA_CEDENTE, REGIMEN_RESISTENCIA_K0,
    REGIMENES_DE_RESISTENCIA, REGLAS_DE_MINIMOS, SECCION_ALERO,
    SECCION_ALERO_MITAD, SECCION_TALON_ALERO,
    SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON, SolicitacionDeArmado,
    TRACCION_NULA)

CRITERIO_REGIMEN_RESISTENCIA = "regimen_resistencia_elementos_cabezal"


CRITERIO_CATALOGO_BARRAS = "catalogo_barras_refuerzo_cabezal"


FILA_EH_EN_REPOSO = "EH_en_reposo"


# El 3 del nucleo de una distribucion triangular (la resultante esta a un
# tercio del lado cargado) y del centro de gravedad de un trapecio.
LADOS_DEL_TRIANGULO = 3      # literal-ok: geometria del triangulo, no un valor de proyecto


def catalogo_de_barras() -> dict:
    """
    El catalogo [A] 'catalogo_barras_refuerzo_cabezal', validado: barras
    (designacion -> diametro en mm y area en mm2) en orden creciente de
    diametro, serie de espaciamientos en m, y las dos barras nombradas
    (minima de la armadura principal y la de reparto) dentro del catalogo.
    """
    c = ca.valor(CRITERIO_CATALOGO_BARRAS)
    barras = c.get("barras") if hasattr(c, "get") else None
    series = c.get("espaciamientos_m") if hasattr(c, "get") else None
    if not (isinstance(barras, dict) and barras
            and isinstance(series, (tuple, list)) and series):
        raise DatoInvalidoError(
            CRITERIO_CATALOGO_BARRAS, valor=c,
            motivo="se esperan los campos 'barras' (designacion -> "
                   "(diametro mm, area mm2)) y 'espaciamientos_m'")
    orden = []
    for nombre, par in barras.items():
        if not (isinstance(par, (tuple, list)) and len(par) == 2
                and all(_finito(x) and x > 0 for x in par)):
            raise DatoInvalidoError(
                CRITERIO_CATALOGO_BARRAS, valor=par,
                motivo=f"la barra «{nombre}» necesita (diametro mm, area "
                       "mm2), los dos positivos")
        orden.append((float(par[0]), float(par[1]), str(nombre)))
    orden.sort()
    if not all(_finito(s) and s > 0 for s in series):
        raise DatoInvalidoError(
            CRITERIO_CATALOGO_BARRAS, valor=series,
            motivo="los espaciamientos son longitudes positivas, en m")
    nombres = [n for _, _, n in orden]
    for campo in ("barra_minima_principal", "barra_reparto"):
        if c.get(campo) not in nombres:
            raise DatoInvalidoError(
                CRITERIO_CATALOGO_BARRAS, valor=c.get(campo),
                motivo=f"'{campo}' tiene que ser una barra del catalogo: "
                       + ", ".join(nombres))
    return {"barras": tuple(orden),
            "espaciamientos": tuple(sorted((float(s) for s in series),
                                           reverse=True)),
            "minima_principal": c["barra_minima_principal"],
            "reparto": c["barra_reparto"],
            "diametro_grueso": dict((n, d) for d, _, n in orden).get(
                RECUBRIMIENTO_BARRA_GRUESA_DESDE)}


# ---------------------------------------------------------------------------
# El armado de UN cabezal: elemento por elemento, y su tabla
# ---------------------------------------------------------------------------

# --- VE-7 (ficha VE7-01) --- y la zapata de los aleros (su talon, sobre la
# franja del arranque), con el procedimiento de la zapata del cabezal.
ELEMENTOS_ARMADOS = (ELEMENTO_PANTALLA, ELEMENTO_ZAPATA, ELEMENTO_ALEROS,
                     ELEMENTO_ZAPATA_ALEROS)


# --- VE-6 (lote M9, item 9; fichas VE3-14 H-13, T7B-08 (3), T7C-04 y
# VE6M9-03) --- EL ALERO SE ARMA POR SUS PROPIAS SECCIONES. Hasta VE-6 llevaba
# la solicitacion de la pantalla en su arranque, con el espesor de la
# pantalla. AASHTO LRFD 5 pide cada seccion con SUS cargas factoradas: cada
# franja vertical del alero es el fuste de un muro en voladizo -- su altura
# baja con el talud de h0 a H_f --, con su espesor y sobre su zapata. Dos
# secciones: el arranque (la mas alta del tramo de 0 a L/2) y la mitad (la
# mas alta del tramo de L/2 a L); con la altura que baja a lo largo del
# alero, la mas alta de cada tramo es la que rige en el.
FRACCION_MITAD_ALERO = 1 / 2


# ===========================================================================
# --- VE-7 (ficha VE7-01, cierre de T7C-04; dictamen Fable del 2026-11-20)
# --- EL ALERO COMO MURO
# ===========================================================================
# Hasta VE-7 el alero se ARMABA por sus secciones (VE-6) y no se VERIFICABA
# como muro. Desde VE-7 cada alero se verifica como muro con su propia
# zapata, con el ENSAMBLE DEL CABEZAL (`ensamble_estabilidad`, `muro` =
# `MURO_ALERO`): las mismas filas E1 a E3, combinaciones, criterios y citas
# (AASHTO LRFD 11.6.3.2, 11.6.3.3 y 11.6.3.6; bajo sismo, 11.6.5, con el
# regimen cedente/no cedente vigente).
#
# EN VARIAS FRANJAS, NO SOLO EN EL ARRANQUE (dictamen Fable, abierto (a)):
# el alero baja con el talud de h0 a H_f, pero el borde de la plataforma no
# baja, de modo que detras de cada franja hacia la punta el relleno SUBE
# mas y la pendiente equivalente -- y con ella K_A (3.11.5.8.1, C3.11.5.8.1-1)
# -- crece: la franja del arranque no rige siempre. Se verifican las franjas
# de `FRACCIONES_DE_ESTABILIDAD_DEL_ALERO` (0, L/4, L/2, 3L/4, L), cada una
# con la geometria de `entorno_de_la_seccion_del_alero`; una franja sin
# fuste no se verifica y el paso lo declara. Las franjas de los dos aleros
# (corto y largo) a la misma fraccion son la misma seccion.
#
# Si alguna no cumple, la zapata de los aleros (un ancho por cabezal) crece
# por el TALON con la regla y el tope de la del cabezal
# ('dimensionamiento_zapata_cabezal' [A], tope el de la franja del
# arranque) hasta que cumplan todas; al tope, NO FACTIBLE con estos
# criterios. Su peralte crece por el armado de su talon, armado en cada
# franja con el procedimiento de la zapata del cabezal. Con el cabezal de
# GRAVEDAD la franja es la seccion del cabezal cortada a su altura, y el
# cuerpo se verifica como ciclopeo (`verificacion_ciclopea_del_alero`).
# Una dimension PROPIA declarada (`ancho_zapata_aleros_m`,
# `espesor_zapata_aleros_m`) gana y no se itera; la del cabezal es solo el
# punto de partida.

SUFIJO_ALERO = ".alero"


# La franja del arranque (fraccion 0 de la longitud del alero).
FRACCION_ARRANQUE_ALERO = 0


def sufijo_de_la_franja(fraccion: float) -> str:
    """
    El sufijo de los codigos de la franja del alero a la `fraccion` de su
    longitud: `.alero` en el arranque (los codigos de antes de las
    franjas), `.alero.25`, `.alero.50`, `.alero.75`, `.alero.100` despues.
    """
    if fraccion <= TOL_UMBRAL_NORMATIVO:
        return SUFIJO_ALERO
    return f"{SUFIJO_ALERO}.{format(fraccion, '.0%').rstrip('%')}"


def _rotulo_de_la_franja(extremo: str, fraccion: float) -> str:
    return (f"alero del cabezal de {extremo} (franja a {fraccion:g}·L, como "
            "muro en voladizo)")


def _rotular_como_alero(est: EstabilidadDelCabezal,
                        fraccion: float = FRACCION_ARRANQUE_ALERO
                        ) -> EstabilidadDelCabezal:
    """
    Los rotulos del ensamble de la franja del alero: «cabezal de X» pasa a
    «alero del cabezal de X (franja a f·L, ...)» en los pasos, las filas y
    los avisos. Las cifras no se tocan.
    """
    de = f"cabezal de {est.extremo}"
    a = _rotulo_de_la_franja(est.extremo, fraccion)

    def que(texto: str) -> str:
        return texto.replace(de, a) if de in texto else f"{texto}: {a}"

    def rotular_paso(p):
        return None if p is None else _reemplazar(p, que=que(p.que))

    def rotular_fila(v):
        return _reemplazar(v, paso=rotular_paso(v.paso),
                           numeral=(v.numeral.replace(de, a)
                                    if isinstance(v.numeral, str)
                                    else v.numeral))

    prefijo = f"Cabezal de {est.extremo} de {est.id_punto}"
    nuevo = (f"Alero del cabezal de {est.extremo} de {est.id_punto} (franja "
             f"a {fraccion:g}·L, como muro en voladizo)")
    return _reemplazar(
        est, muro=MURO_ALERO, fraccion_alero=fraccion,
        pasos=tuple(rotular_paso(p) for p in est.pasos),
        verificaciones=tuple(rotular_fila(v) for v in est.verificaciones),
        globales=tuple(rotular_fila(v) for v in est.globales),
        avisos=tuple(x.replace(prefijo, nuevo, 1) for x in est.avisos))
