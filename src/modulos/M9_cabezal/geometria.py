# -*- coding: utf-8 -*-
"""
M9_cabezal.geometria
====================
Submodulo de Fase 9 (`M9_cabezal`): bloque `geometria` (D1).
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple

from dataclasses import replace
from src import (
    criterios_adoptados as ca,
    datos_sitio as ds,
)
from src.constantes_normativas import (
    BANDAS_ALETAS_CAJON_A1,
    BANDAS_ALETAS_CAJON_C2,
    BANDAS_ESVIAJE_CABEZAL_CAJON_A1,
    CAJON_A1_SIN_ALETAS,
    CAJON_C2_SIN_ALETAS,
    KE_C2_POR_FILA_CARTA_11,
    KE_C2_POR_FILA_SIN_ALETAS,
    NUMERAL_ZAPATA_CONCRETO_SIMPLE,
    ORIENTACIONES_TABULADAS,
    ORIENTACION_PARALELO_AL_TRAFICO,
    ORIENTACION_PERPENDICULAR_AL_TRAFICO,
)
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (
    Aleros,
    CIFRAS_MAGNITUD,
    CabezalDelPunto,
    CriterioPendienteError,
    DatoInvalidoError,
    DimensionDeCabezal,
    EmbocaduraDelPunto,
    EntornoDelCabezal,
    ExtremoDelConducto,
    Familia,
    FormaSeccion,
    GeometriaCabezal,
    LimiteNumericoError,
    LosaDeEntrega,
    Magnitud,
    MetodoLongitud,
    ORIGEN_DIMENSION_ARMADO,
    ORIGEN_DIMENSION_DECLARADA,
    ORIGEN_DIMENSION_DERIVADA,
    ORIGEN_DIMENSION_ESTABILIDAD,
    ORIGEN_DIMENSION_REGLA,
    PasoDeMemoria,
    TipoDeVeredicto,
    Umbral,
    Veredicto,
    Verificacion,
    cifras_de_dimension,
    paso,
)
from src.modulos.M2_material import espesor_pared
from src.modulos.M6_proteccion import (
    EMBOCADURA_CABEZAL_CON_ALEROS,
    EMBOCADURA_CABEZAL_RECTO,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CONDICION_RECUBRIMIENTO_ZAPATA,
    CRITERIO_DIMENSIONAMIENTO_ZAPATA,
    CRITERIO_GEOMETRIA,
    CRITERIO_PERALTE_ZAPATA_ARMADA,
    CRITERIO_TALUD_TERRAPLEN,
    EXTREMOS,
    EXTREMO_ENTRADA,
    EXTREMO_SALIDA,
    ORIENTACION_PARALELO_A_LA_VIA,
    TIPO_GRAVEDAD,
    TIPO_VOLADIZO,
    _caracter_de,
    _exigir_finito,
    _exigir_positivo,
    _finito,
    catalogo_de_barras,
    es_paralelo_a_la_via,
)
from src.modulos.M9_cabezal.durabilidad import recubrimiento_para_armar
from src.modulos.M9_cabezal.empujes import envolvente_de_h_eq_paralelo

# ===========================================================================
# --- T-7a --- 9.0 EL CABEZAL POR PUNTO: EMBOCADURA, GEOMETRIA Y ALEROS
# ===========================================================================
# Cierra INF-4.1, INF-4.2, INF-4.3 e INF-5.1.15. Hasta aqui la Fase 9 era
# «del proyecto»: una sola `GeometriaCabezal`, leida de un criterio vacio,
# para todos los puntos, mientras el NF que entra en sus empujes era el de
# cada punto. Desde T-7a:
#
#   * la EMBOCADURA es del punto (`embocadura_del_punto`) y se resuelve antes
#     de la Fase 4, porque en un marco elige la banda de filas del HDS-5 que
#     su embocadura declarada tiene que respetar
#     (`verificar_coherencia_embocadura_cajon`) y entra a la proteccion de
#     entrada de la Fase 6;
#   * el cabezal de CADA EXTREMO de cada punto dimensionado se predimensiona
#     con las reglas declaradas de 'predimensionamiento_cabezal' [A] sobre
#     lo que las fases 4, 6 y 7.B ya resolvieron (`extremos_del_conducto`,
#     `predimensionar_cabezal`, `predimensionar_aleros`), y cualquier
#     dimension se puede pisar por punto en `--datos-externos`;
#   * la compatibilidad con el conducto, y los minimos con numero que una
#     dimension declarada puede violar, son VERIFICACIONES (CB1 a CB7) y no
#     una frase en la ficha del criterio;
#   * la longitud entre cabezales queda cerrada con el relleno que retienen
#     los dos (ficha T6-01), sin sustituir a la que uso la hidraulica.
#
# LAS CORRECCIONES DE LA AUDITORIA ADVERSARIAL (2026-11-13), en una linea
# cada una: los aleros miden distinto con esviaje (H1); el dentellon se mide
# desde el terreno del pie, la misma referencia del desplante (H3); CB6 y CB7
# (H4); el talud muere en el relleno retenido y hay longitud de metrado
# (H6); la regla del tipo se mide sobre la altura total y se avisa (H7); los
# dos minimos de normas de edificacion son [N→] (H8, dudoso 4); el origen
# «derivada» y los avisos con su causa (H9).
#
# Lo que NO hace, y es de T-7b y T-7c: ensamblar cargas, verificar la
# estabilidad (E1-E6) o armar. La geometria sale con la interfaz que esas
# funciones ya aceptan (`GeometriaCabezal` con talon, espesores y zapata).

from src.constantes_normativas import (BANDAS_ALETAS_CAJON_A1,  # noqa: E402
                                       BANDAS_ALETAS_CAJON_C2,
                                       BANDAS_ESVIAJE_CABEZAL_CAJON_A1,
                                       KE_C2_POR_FILA_CARTA_11,
                                       KE_C2_POR_FILA_SIN_ALETAS,
                                       CAJON_A1_SIN_ALETAS,
                                       CAJON_C2_SIN_ALETAS,
                                       NUMERAL_ZAPATA_CONCRETO_SIMPLE)
from src.dominios import MILIMETROS_POR_METRO  # noqa: E402
from src.modelos import (ORIGEN_DIMENSION_DECLARADA,  # noqa: E402
                         ORIGEN_DIMENSION_DERIVADA,
                         ORIGEN_DIMENSION_ESTABILIDAD, IntentoDeZapata,
                         ORIGEN_DIMENSION_ARMADO, IntentoDePeralte,
                         ORIGEN_DIMENSION_REGLA, Aleros, CabezalDelPunto,
                         Familia, LimiteNumericoError, PasoDeMemoria,
                         DimensionDeCabezal, EmbocaduraDelPunto,
                         ExtremoDelConducto, LosaDeEntrega, CIFRAS_MAGNITUD,
                         cifras_de_dimension,
                         FormaSeccion, MetodoLongitud)
from src.modulos.M2_material import espesor_pared  # noqa: E402
from src.modulos.M6_proteccion import (EMBOCADURA_CABEZAL_CON_ALEROS,  # noqa: E402
                                       EMBOCADURA_CABEZAL_RECTO)

CRITERIO_EMBOCADURA_CABEZAL = "embocadura_cabezal"


CRITERIO_ANGULO_ALETAS = "angulo_aletas"


CRITERIO_MARGEN_SOCAVACION = "margen_zapata_bajo_socavacion_m"


CRITERIO_DENTELLON = "dentellon_losa_entrega"


CRITERIO_EMBOCADURA_CAJON = "embocadura_cajon"


CRITERIO_KE_CAJON = "ke_entrada_cajon"


# --- T-7a, correcciones (H8 y dudoso 4) --- los dos minimos de normas de
# edificacion aplicados por analogia al cabezal vial: [N→], no [N].
CRITERIO_DESPLANTE_MIN = "profundidad_cimentacion_min_cabezal_m"


CRITERIO_ESPESOR_ZAPATA_SIMPLE = "espesor_min_zapata_concreto_simple_m"


EMBOCADURAS_DEL_CABEZAL = (EMBOCADURA_CABEZAL_CON_ALEROS,
                           EMBOCADURA_CABEZAL_RECTO)


# --- VE-6 (ficha T7A-03) --- La orientacion del muro de cabecera
# (`EmbocaduraDelPunto.orientacion`). Normal al eje del conducto es la de
# archivo en las tres familias (decision del dueño del 2026-11-13); paralelo a
# la via, solo en el marco y solo cuando 'embocadura_cajon' declara una fila
# de la Carta 11 del HDS-5 (cabezal esviado respecto del barril, sin aletas).
ORIENTACION_NORMAL_AL_EJE = "normal_al_eje"


CRITERIO_N_CELDAS_CAJON_EMBOCADURA = "n_celdas_cajon"


TIPOS_DE_CABEZAL = (TIPO_VOLADIZO, TIPO_GRAVEDAD)


NUMERAL_9_0 = "Sec. 9 (cabezal por punto, T-7a)"


CITA_PROFUNDIDAD_CIMENTACION = "E050.26.2#PROFUNDIDAD"


CITA_PERALTE_ZAPATA_ARMADA = "E060.15.7#PERALTE"


CITA_ZAPATA_CONCRETO_SIMPLE = "E060.22.7.4#ZAPATA"


CITA_CICLOPEO_LIMITES = "E060.22.10.2#CICLOPEO"


CITA_CONVENCION_ALEROS = "HDS5_3ED.SIMBOLOS#THETA_W"


# --- VE-7 (lote A, A8) --- la cita cuya nota nombra las vigas de borde del
# cajon (C12.11.2.1): el borde libre esviado del marco con cabezal paralelo.
CITA_BORDE_LIBRE_ESVIADO = "AASHTO_LRFD_9.12.11.2.1#SOMERO"


# Las dimensiones que el proyectista puede declarar por punto en
# `--datos-externos` (clave `cabezal_declarado`), en m. La validacion de
# forma y dominio es `validar_cabezal_declarado`; aqui, solo los nombres.
DIMENSIONES_DECLARABLES = (
    "altura_total_m", "profundidad_desplante_m", "longitud_m",
    "espesor_corona_m", "espesor_base_muro_m", "ancho_zapata_m",
    "espesor_zapata_m", "ancho_punta_m", "longitud_aleros_m",
    "altura_final_aleros_m", "espesor_aleros_m", "longitud_losa_m",
    "espesor_losa_m", "profundidad_dentellon_m",
    # --- VE-7 (dictamen Fable, abierto (d)) --- la zapata PROPIA de los
    # aleros: gana y no se itera (sin ella parte de la del cabezal).
    "ancho_zapata_aleros_m", "espesor_zapata_aleros_m",
)


CAMPO_ANCHO_ZAPATA_ALEROS = "ancho_zapata_aleros_m"


CAMPO_ESPESOR_ZAPATA_ALEROS = "espesor_zapata_aleros_m"


CAMPO_TIPO_DECLARADO = "tipo"


# --- T-7a, integracion (decision del dueño del 2026-11-13) --- El angulo del
# alero LARGO (el que forma alfa + theta con la bajada del talud), en grados
# con la pared del barril: el remedio del alero largo de un cruce esviado
# -- 8.1 m en C-01 con 30 grados -- es declararlo menor de ese lado (aleros
# asimetricos). No es una dimension en m: se valida como angulo, en [0, 90).
CAMPO_ANGULO_ALERO_LARGO = "angulo_alero_largo_grados"


ANGULOS_DECLARABLES = (CAMPO_ANGULO_ALERO_LARGO,)


def _exigir_angulo(campo: str, x: object, que: str,
                   id_punto: Optional[str] = None) -> float:
    """Un angulo de aleros con la pared del barril: finito y en [0, 90)."""
    if not (_finito(x) and x >= 0
            and math.cos(math.radians(x)) > TOL_UMBRAL_NORMATIVO):
        raise DatoInvalidoError(
            campo, valor=x, id_punto=id_punto,
            motivo=f"{que}: se espera un angulo finito en [0, 90) grados con "
                   "la pared del barril (a 90 el alero esta en el plano del "
                   "muro)")
    return float(x)


def _en_banda(angulo: float, banda: Tuple[float, float]) -> bool:
    """`angulo` dentro de [min, max] con la tolerancia normativa nombrada."""
    minimo, maximo = banda
    return (minimo - TOL_UMBRAL_NORMATIVO <= angulo
            <= maximo + TOL_UMBRAL_NORMATIVO)


# ---------------------------------------------------------------------------
# La embocadura del punto (perfil: entra a la Fase 4 y a la Fase 6)
# ---------------------------------------------------------------------------

def embocadura_del_punto(*, esviaje_grados: float,
                         familia: Optional[Familia] = None,
                         id_punto: Optional[str] = None
                         ) -> EmbocaduraDelPunto:
    """
    La embocadura de un punto: cabezal con aleros o recto
    ('embocadura_cabezal' [A]) y, con aleros, su angulo con la prolongacion
    de la pared del barril (ΘW del HDS-5) por la regla de 'angulo_aletas'
    [A]: el de por defecto, salvo que el esviaje SUPERE el umbral, y
    entonces el otro (INFORME §4.3).

    La lee el servicio ANTES de la Fase 4 y en los dos alcances: en un marco
    gobierna la banda de filas del HDS-5 que la embocadura del cajon tiene
    que respetar, y en todo punto lo que protege la Fase 6 a la entrada. Por
    eso los dos criterios son de perfil aunque la geometria sea de
    expediente.

    LA CAJA RECEPTORA NO ESTA EN EL CATALOGO (decision 3 del dueño, ficha
    T7A-02): la Lamina Nº 02-A la dibuja como la entrada de una TMC, sin
    aleros, y es la entrada habitual de un alivio de cuneta. Un punto de la
    Familia B recibe la embocadura del criterio y la corrida lo AVISA
    (`EmbocaduraDelPunto.avisos`, que sale por `InformePunto.avisos()`).

    El esviaje se valida aqui en segunda linea (M0 ya lo valida contra
    `dominios.ESVIAJE_MAX`): un NaN es falso frente a `>` igual que frente a
    `<=`, y caeria en la rama del angulo por defecto sin decir nada.
    """
    if not (_finito(esviaje_grados) and esviaje_grados >= 0):
        raise DatoInvalidoError(
            "esviaje_grados", valor=esviaje_grados, id_punto=id_punto,
            motivo="el angulo de los aleros se elige con el esviaje del "
                   "cruce, y este no es un angulo finito y no negativo")
    tipo = ca.valor(CRITERIO_EMBOCADURA_CABEZAL)
    if tipo not in EMBOCADURAS_DEL_CABEZAL:
        raise DatoInvalidoError(
            CRITERIO_EMBOCADURA_CABEZAL, valor=tipo, id_punto=id_punto,
            motivo="se espera una de " + ", ".join(EMBOCADURAS_DEL_CABEZAL))
    avisos = ()
    if familia is Familia.B:
        avisos = (
            f"Embocadura de {id_punto}: la entrada de un alivio de cuneta "
            "(Familia B) suele ser una CAJA RECEPTORA (Lamina Nº 02-A del "
            "Manual, sin aleros), que el programa NO modela: el punto recibe "
            f"«{tipo}» ('{CRITERIO_EMBOCADURA_CABEZAL}'), y con esa "
            "embocadura se calculan su perdida de entrada, su proteccion de "
            "entrada y su cabezal de entrada. Una caja receptora no tiene "
            "fila en las Tablas A.1 y C.2 del HDS-5 (ficha T7A-02)",)
    # --- VE-6 (ficha T7A-03) --- EL CABEZAL PARALELO A LA VIA, SOLO EN EL
    # MARCO: lo elige la fila DECLARADA de 'embocadura_cajon' cuando es de la
    # Carta 11 del HDS-5 («skewed headwall», sin aletas). Es la fila de la
    # tabla la que dibuja la embocadura (justificacion del criterio: «Eso lo
    # decide el detalle que el proyectista dibuje»), y con ella el muro es
    # recto y paralelo a la via, esviado respecto del barril el esviaje del
    # cruce. 'embocadura_cabezal' sigue rigiendo los tubos.
    if familia is Familia.C:
        fila = ca.valor_si_declarado(CRITERIO_EMBOCADURA_CAJON)
        if fila in BANDAS_ESVIAJE_CABEZAL_CAJON_A1:
            return _embocadura_paralela(
                fila=fila, tipo_criterio=tipo,
                esviaje_grados=float(esviaje_grados), id_punto=id_punto,
                avisos=avisos)
    if tipo == EMBOCADURA_CABEZAL_RECTO:
        return EmbocaduraDelPunto(
            tipo=tipo, angulo_aletas=None,
            regla="cabezal recto: sin aleros",
            esviaje_grados=float(esviaje_grados),
            criterio_tipo=CRITERIO_EMBOCADURA_CABEZAL,
            criterio_angulo="", avisos=avisos)
    regla = ca.valor(CRITERIO_ANGULO_ALETAS)
    por_defecto = _exigir_positivo(
        CRITERIO_ANGULO_ALETAS, regla.get("por_defecto_grados"),
        "angulo de los aleros por defecto", id_punto)
    umbral = _exigir_finito(
        CRITERIO_ANGULO_ALETAS, regla.get("umbral_esviaje_grados"),
        "umbral de esviaje de la regla de los aleros", id_punto)
    con_esviaje = _exigir_positivo(
        CRITERIO_ANGULO_ALETAS, regla.get("con_esviaje_mayor_grados"),
        "angulo de los aleros con esviaje mayor que el umbral", id_punto)
    if esviaje_grados > umbral:
        angulo = con_esviaje
        rama = (f"esviaje {esviaje_grados:g} grados > umbral {umbral:g}: "
                f"{con_esviaje:g} grados")
    else:
        angulo = por_defecto
        rama = (f"esviaje {esviaje_grados:g} grados <= umbral {umbral:g}: "
                f"{por_defecto:g} grados (por defecto)")
    return EmbocaduraDelPunto(
        tipo=tipo, angulo_aletas=angulo,
        regla=rama, esviaje_grados=float(esviaje_grados),
        criterio_tipo=CRITERIO_EMBOCADURA_CABEZAL,
        criterio_angulo=CRITERIO_ANGULO_ALETAS, avisos=avisos)


def _embocadura_paralela(*, fila: str, tipo_criterio: str,
                         esviaje_grados: float, id_punto: Optional[str],
                         avisos: Tuple[str, ...]) -> EmbocaduraDelPunto:
    """
    --- VE-6 (ficha T7A-03) --- La embocadura del marco con el cabezal
    PARALELO A LA VIA que pide una fila de la Carta 11: cabezal recto (sin
    aletas: los rotulos de la Carta 11 no nombran aletas, y su ke es el de
    «Headwall parallel to embankment (no wingwalls)» de la Tabla C.2),
    esviado respecto del barril el esviaje del cruce. Dos avisos que la
    fuente sostiene: con 'embocadura_cabezal' = con aleros, que el marco no
    los lleva (la fila declarada manda en el marco); y con mas de una celda,
    que el HDS-5 recomienda evitar el esviaje de la embocadura en los
    barriles multiples (num. 5.4.2, pag. impresa 5.14, cita
    `HDS5_3ED.5.4.2#EVITAR`).
    """
    extra = []
    if tipo_criterio == EMBOCADURA_CABEZAL_CON_ALEROS:
        extra.append(
            f"Embocadura de {id_punto}: el marco lleva el cabezal PARALELO A "
            f"LA VIA y SIN aleros que pide la fila declarada de "
            f"'{CRITERIO_EMBOCADURA_CAJON}' ({fila}, Carta 11 del HDS-5: "
            f"cabezal esviado respecto del barril); "
            f"'{CRITERIO_EMBOCADURA_CABEZAL}' = {tipo_criterio} sigue rigiendo "
            "los tubos (ficha T7A-03)")
    # --- VE-7 (lote A, A8; triaje VE-7 de Fable) --- el extremo del marco
    # cortado en oblicuo deja un borde libre esviado de la losa que el
    # programa no verifica: el comentario C12.11.2.1 lo resuelve con vigas
    # de borde (nota de la cita `AASHTO_LRFD_9.12.11.2.1#SOMERO`).
    extra.append(
        f"Embocadura de {id_punto}: con el cabezal paralelo a la via el "
        f"extremo del marco se corta esviado {esviaje_grados:g} grados y el "
        "borde libre esviado de la losa NO se verifica; las vigas de borde "
        "del comentario C12.11.2.1 de AASHTO LRFD (nota de "
        f"`{CITA_BORDE_LIBRE_ESVIADO}`) son detalle del proyectista "
        "(ficha VE7A-08)")
    celdas = ca.valor(CRITERIO_N_CELDAS_CAJON_EMBOCADURA)
    if isinstance(celdas, int) and celdas > 1:
        extra.append(
            f"Embocadura de {id_punto}: cabezal paralelo a la via (esviado "
            f"{esviaje_grados:g} grados respecto del barril) en un marco de "
            f"{celdas} celdas. El HDS-5 recomienda evitar el esviaje de la "
            "embocadura en los barriles multiples (num. 5.4.2, pag. impresa "
            "5.14: «Inlet skew should be avoided ... for multiple barrel "
            "culverts»); con el terraplen alabeado el cabezal normal al eje "
            "es el de archivo (ficha T7A-03)")
    return EmbocaduraDelPunto(
        tipo=EMBOCADURA_CABEZAL_RECTO, angulo_aletas=None,
        regla=(f"cabezal recto PARALELO A LA VIA, esviado "
               f"{esviaje_grados:g} grados respecto del barril: fila "
               f"declarada de '{CRITERIO_EMBOCADURA_CAJON}' = {fila} (Carta "
               "11 del HDS-5, «skewed headwall»)"),
        esviaje_grados=esviaje_grados,
        criterio_tipo=CRITERIO_EMBOCADURA_CAJON,
        criterio_angulo="", avisos=tuple(avisos) + tuple(extra),
        orientacion=ORIENTACION_PARALELO_A_LA_VIA)


def factor_cara_del_muro(embocadura: EmbocaduraDelPunto) -> float:
    """
    --- VE-6 (ficha T7A-03) --- Cuanto mide, a lo largo del muro, un ancho
    normal al eje del conducto: 1 con el muro normal al eje; 1/cos(theta)
    con el muro paralelo a la via, que corta al barril esviado theta en
    oblicuo (la misma proyeccion que `M7.factor_esviaje` aplica a la
    longitud).
    """
    if not es_paralelo_a_la_via(embocadura):
        return 1.0
    coseno = math.cos(math.radians(embocadura.esviaje_grados))
    if not coseno > TOL_UMBRAL_NORMATIVO:
        raise LimiteNumericoError(
            "esviaje_grados", valor=embocadura.esviaje_grados,
            motivo="con el cabezal paralelo a la via el muro corta al barril "
                   "en oblicuo, y a 90 grados de esviaje no lo corta nunca")
    return 1.0 / coseno


def filas_hds5_del_cajon(embocadura: EmbocaduraDelPunto
                         ) -> Tuple[frozenset, frozenset]:
    """
    Las claves de fila de las Tablas A.1 y C.2 del HDS-5 que valen para un
    MARCO con esta embocadura: (cartas de 'embocadura_cajon', filas de
    'ke_entrada_cajon').

    Sale de las bandas que el ROTULO de cada fila imprime
    (`constantes_normativas.BANDAS_ALETAS_CAJON_A1` / `_C2`): sin aleros,
    las filas de cabezal recto; con aleros, las que contienen su angulo con
    el barril. Con un TUBO no se llama: la Tabla C.2 agrupa «Headwall or
    headwall and wingwalls» y el angulo no elige fila.
    """
    if es_paralelo_a_la_via(embocadura):
        # --- VE-6 (ficha T7A-03) --- las filas de la Carta 11 cuyo rotulo
        # contiene el esviaje del cruce, y el ke del cabezal paralelo al
        # terraplen sin aletas de la Tabla C.2.
        theta = embocadura.esviaje_grados
        a1 = frozenset(k for k, bandas in
                       BANDAS_ESVIAJE_CABEZAL_CAJON_A1.items()
                       if any(_en_banda(theta, b) for b in bandas))
        # --- dictamen Fable (2026-11-20) --- el ke se empareja con el
        # BORDE de la fila declarada (`KE_C2_POR_FILA_CARTA_11`, lectura de
        # los rotulos): el chaflan, solo la escuadra; el bisel, la de bordes
        # biselados y la escuadra.
        declarada = ca.valor_si_declarado(CRITERIO_EMBOCADURA_CAJON)
        c2 = (KE_C2_POR_FILA_CARTA_11[declarada] if declarada in a1
              else CAJON_C2_SIN_ALETAS)
        return a1, c2
    if embocadura.angulo_aletas is None:
        # --- VE-7 (lote A, A1) --- el cabezal normal sin aletas: el ke se
        # empareja con el BORDE de la fila declarada
        # (`KE_C2_POR_FILA_SIN_ALETAS`, la lectura de los rotulos de
        # `KE_C2_POR_FILA_CARTA_11`): el chaflan y la escala 2 de la Carta
        # 8, solo la escuadra; los biseles, la biselada y la escuadra.
        declarada = ca.valor_si_declarado(CRITERIO_EMBOCADURA_CAJON)
        c2 = (KE_C2_POR_FILA_SIN_ALETAS[declarada]
              if declarada in CAJON_A1_SIN_ALETAS
              and declarada in KE_C2_POR_FILA_SIN_ALETAS
              else CAJON_C2_SIN_ALETAS)
        return CAJON_A1_SIN_ALETAS, c2
    angulo = embocadura.angulo_aletas
    a1 = frozenset(k for k, bandas in BANDAS_ALETAS_CAJON_A1.items()
                   if any(_en_banda(angulo, b) for b in bandas))
    c2 = frozenset(k for k, bandas in BANDAS_ALETAS_CAJON_C2.items()
                   if any(_en_banda(angulo, b) for b in bandas))
    return a1, c2


def _describir_embocadura(embocadura: EmbocaduraDelPunto) -> str:
    if es_paralelo_a_la_via(embocadura):
        return (f"cabezal recto paralelo a la via, esviado "
                f"{embocadura.esviaje_grados:g} grados respecto del barril")
    if embocadura.angulo_aletas is None:
        return "cabezal recto (sin aleros)"
    return (f"cabezal con aleros a {embocadura.angulo_aletas:g} grados con "
            "la pared del barril")


def verificar_coherencia_embocadura_cajon(embocadura: EmbocaduraDelPunto, *,
                                          id_punto: Optional[str] = None
                                          ) -> Optional[str]:
    """
    Que la embocadura DECLARADA del marco ('embocadura_cajon', carta de la
    Tabla A.1; 'ke_entrada_cajon', fila de la Tabla C.2) sea la del cabezal
    del punto. Es la frase de la Sec. 9.1 de la hoja de ruta -- «ambas
    decisiones deben moverse juntas» -- llevada a una puerta.

    Solo mira lo DECLARADO: si un criterio del cajon sigue sin valor no lo
    rellena ni lo deduce -- es de T-3 y su vacio lo levanta M2/M4, con su
    nombre, como hasta ahora --. Si uno declarado es de otra banda de angulo
    que la del cabezal, `DatoInvalidoError` nombrando el par y las filas que
    SI corresponden: el control de entrada y el de salida no corren con una
    embocadura distinta de la que el cabezal dibuja. Asi, cambiar el angulo
    de los aleros NO deja intactos ke ni la carta: o la fila declarada sigue
    siendo de la banda nueva, o el punto se detiene pidiendo la que es; y
    declarada, M4 recalcula con ella. Con las filas de 30 a 75 grados y los
    aleros de la ventana de 'angulo_aletas' (30 a 60 grados) la coherencia
    se cumple siempre: la nota que devuelve es un dato del punto (JSON, paso
    9.0.0), no un aviso.

    SE DECIDE POR LA FAMILIA (la llama `servicio._fase_embocadura` con un
    punto de la Familia C) y no por la forma de la seccion, porque corre
    ANTES del bucle de MD, cuando la seccion todavia no existe. Es
    equivalente mientras M2 solo ofrezca el marco a la Familia C, y
    `tests/test_t7a_cabezal_geometria.py` lo fija.

    Devuelve una nota con las filas comprobadas, o None si no habia nada
    declarado que comprobar.
    """
    a1_ok, c2_ok = filas_hds5_del_cajon(embocadura)
    comprobadas = []
    for criterio, admisibles, tabla in (
            (CRITERIO_EMBOCADURA_CAJON, a1_ok, "Tabla A.1"),
            (CRITERIO_KE_CAJON, c2_ok, "Tabla C.2")):
        declarado = ca.valor_si_declarado(criterio)
        if declarado is None:
            continue
        if declarado not in admisibles:
            raise DatoInvalidoError(
                criterio, valor=declarado, id_punto=id_punto,
                motivo=(f"la fila declarada de la {tabla} del HDS-5 no es de "
                        f"la embocadura del cabezal ({_describir_embocadura(embocadura)}, "
                        f"'{embocadura.criterio_tipo}'"
                        + (f" y '{embocadura.criterio_angulo}'"
                           if embocadura.criterio_angulo else "")
                        + "). Filas de esa embocadura: "
                        + (", ".join(sorted(admisibles)) or
                           "ninguna: la tabla no tiene fila para ese angulo")
                        + ". Declarar una de ellas, o cambiar la embocadura "
                          "del cabezal: las dos decisiones se mueven juntas "
                          "(Sec. 9.1)"))
        comprobadas.append(f"'{criterio}' = {declarado}")
    if not comprobadas:
        return None
    return ("Embocadura del marco coherente con la del cabezal ("
            + _describir_embocadura(embocadura) + "): "
            + "; ".join(comprobadas))


# --- VE-7 (lote A, A2; triaje VE-7 de Fable, 2026-11-20) --- LA EMBOCADURA
# DEL MARCO DECLARADA POR PUNTO: {"carta": fila de la Tabla A.1, "ke": fila
# de la Tabla C.2}. 'embocadura_cajon' y 'ke_entrada_cajon' son de proyecto
# y el esviaje es del punto: con una fila de la Carta 11 (paralelo a la via)
# todo marco fuera de su banda se detenia (VE6-T7A03 (1)). El servicio la
# aplica en caliente durante el punto y la retira al salir; la coherencia
# sigue en `verificar_coherencia_embocadura_cajon`.
DATO_EMBOCADURA_CAJON_DEL_PUNTO = "embocadura_cajon_del_punto"


CAMPOS_EMBOCADURA_CAJON_DEL_PUNTO = ("carta", "ke")


CRITERIO_DE_CAMPO_EMBOCADURA = {"carta": CRITERIO_EMBOCADURA_CAJON,
                                "ke": CRITERIO_KE_CAJON}


NOTA_EMBOCADURA_DECLARADA_POR_PUNTO = (
    "declarada por punto (`embocadura_cajon_del_punto` de "
    "--datos-externos): rige para este punto en lugar de la del proyecto")


def validar_embocadura_cajon_del_punto(valor: Any, *,
                                       id_punto: Optional[str] = None
                                       ) -> dict:
    """
    Forma y dominio de `embocadura_cajon_del_punto` (dato externo opcional,
    SOLO por punto): un objeto con exactamente `carta` (una fila de cajon de
    la Tabla A.1 del HDS-5) y `ke` (una fila de cajon de la Tabla C.2). Las
    dos van juntas -- «ambas decisiones deben moverse juntas» (Sec. 9.1) --:
    medio par no entra. Si son de la embocadura del cabezal del punto lo
    decide despues `verificar_coherencia_embocadura_cajon`, como con las de
    proyecto.
    """
    campo = DATO_EMBOCADURA_CAJON_DEL_PUNTO
    if not (isinstance(valor, dict)
            and set(valor) == set(CAMPOS_EMBOCADURA_CAJON_DEL_PUNTO)):
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con 'carta' (fila de la Tabla A.1) y "
                   "'ke' (fila de la Tabla C.2) del HDS-5, los dos y nada "
                   "mas: las dos decisiones se mueven juntas (Sec. 9.1)")
    admitidas = {"carta": tuple(sorted(BANDAS_ALETAS_CAJON_A1)),
                 "ke": tuple(sorted(BANDAS_ALETAS_CAJON_C2))}
    limpio = {}
    for k in CAMPOS_EMBOCADURA_CAJON_DEL_PUNTO:
        x = valor[k]
        if not isinstance(x, str) or x.strip() not in admitidas[k]:
            raise DatoInvalidoError(
                f"{campo}.{k}", valor=x, id_punto=id_punto,
                motivo="se espera una de las filas de cajon de '"
                       + CRITERIO_DE_CAMPO_EMBOCADURA[k] + "': "
                       + ", ".join(admitidas[k]))
        limpio[k] = x.strip()
    return limpio


# ---------------------------------------------------------------------------
# Lo que el cabezal necesita del conducto, en cada extremo
# ---------------------------------------------------------------------------

def extremos_del_conducto(*, punto, resultado, geometria,
                          socavacion=None
                          ) -> Tuple[ExtremoDelConducto, ExtremoDelConducto]:
    """
    Los dos `ExtremoDelConducto` de un punto dimensionado, leidos de lo que
    las fases anteriores ya resolvieron -- la seccion y el material de la
    Fase 4 (`ResultadoPunto`), el HW de diseño y el tirante de salida de M4,
    las cotas de 7.B (`CompatibilidadGeometrica`) y la socavacion de la Fase
    6 (`SocavacionSalida`) -- sin decidir nada otra vez.

    La clave exterior es la FISICA (altura interior + pared, MAT-D4), la
    misma de `M5.cota_clave`, trasladada a cada extremo con su solera. El
    ancho exterior lleva todas las celdas del marco: N·B + (N+1)·t.

    EL PIE DEL MURO -- la superficie del terreno desde la que se miden el
    desplante (E.050 Art. 26.1, por analogia), el dentellon de la losa y las
    alturas de los aleros: UNA referencia por extremo -- es en la entrada la
    solera, y en la salida la MAS BAJA entre la solera y el fondo del cauce
    receptor: con la salida en caida sobre el lecho (G2 lo admite), el
    terreno delante del muro baja hasta el receptor, y medir desde la solera
    dejaria la zapata y el dentellon por encima del lecho. Es la lectura
    conservadora, la misma que T-8 adopto para la referencia de la hoya
    ('referencia_profundidad_socavacion').

    El nivel de agua contra el cabezal: en la entrada, solera + HW de diseño
    (el del control que gobierna); en la salida, solera + el mayor entre el
    TW y el tirante con que M4 midio la velocidad de salida. M4 llena los
    dos siempre (EXT-3); si faltan, es un fallo del programa y no se
    sustituye por cero.
    """
    seccion = resultado.seccion
    material = resultado.material
    h = resultado.resultado_hidraulico
    altura = seccion.altura
    t = espesor_pared(material, altura)
    n = h.numero_celdas
    ancho = n * seccion.ancho_exterior(t) - (n - 1) * t
    c = altura + t
    solera_e = geometria.cota_entrada.valor
    solera_s = geometria.cota_salida
    if h.TW_m is None and h.y_salida_m is None:
        raise ValueError(
            f"el resultado hidraulico de {punto.id} no trae ni el TW ni el "
            "tirante de salida: la Fase 9 no elige un nivel de agua por su "
            "cuenta")
    tirante_salida = max(x for x in (h.TW_m, h.y_salida_m) if x is not None)
    hoya = None if socavacion is None else socavacion.cota_fondo_de_la_hoya
    origen_soc = ("" if socavacion is None else socavacion.origen)
    receptor = punto.cota_fondo_receptor
    _exigir_finito("cota_fondo_receptor", receptor,
                   "fondo del cauce receptor", punto.id)
    pie_s = min(solera_s, receptor)
    entrada = ExtremoDelConducto(
        extremo=EXTREMO_ENTRADA, cota_solera=solera_e, cota_pie=solera_e,
        origen_cota_pie=("solera de entrada (regla de "
                         "'predimensionamiento_cabezal'); cota de entrada "
                         f"{geometria.cota_entrada.rotulo}"),
        cota_clave_exterior=solera_e + c,
        cota_agua=solera_e + h.HW,
        origen_cota_agua=(f"solera + HW de diseño ({h.control_gobernante.value}"
                          f", M4) = {h.HW:.3f} m"),
        ancho_exterior=ancho, altura_interior=altura)
    salida = ExtremoDelConducto(
        extremo=EXTREMO_SALIDA, cota_solera=solera_s, cota_pie=pie_s,
        origen_cota_pie=(
            "la MAS BAJA entre la solera de salida de 7.B y el fondo del "
            "cauce receptor (columna cota_fondo_receptor): con la salida "
            "sobre el lecho, el terreno delante del muro baja hasta el "
            "receptor, y medir el desplante y el dentellon desde la solera "
            "los dejaria colgados (regla de 'predimensionamiento_cabezal')"),
        cota_clave_exterior=solera_s + c,
        cota_agua=solera_s + tirante_salida,
        origen_cota_agua=("solera + max(TW, tirante de salida de M4) = "
                          f"{tirante_salida:.3f} m"),
        ancho_exterior=ancho, altura_interior=altura,
        cota_fondo_hoya=hoya, origen_socavacion=origen_soc)
    return entrada, salida


# ---------------------------------------------------------------------------
# El predimensionamiento de UN cabezal
# ---------------------------------------------------------------------------

def _reglas() -> dict:
    """Las reglas de 'predimensionamiento_cabezal', validadas en segunda linea."""
    reglas = ca.valor(CRITERIO_GEOMETRIA)
    if not isinstance(reglas, dict):
        raise DatoInvalidoError(CRITERIO_GEOMETRIA, valor=reglas,
                                motivo="se espera el dict de reglas")
    for campo, x in reglas.items():
        if campo in ("resguardo_agua_m", "bordillo_m"):
            if not (_finito(x) and x >= 0):
                raise DatoInvalidoError(
                    CRITERIO_GEOMETRIA, valor=x,
                    motivo=f"'{campo}' tiene que ser finito y no negativo")
        else:
            _exigir_positivo(CRITERIO_GEOMETRIA, x, f"regla '{campo}'")
    return reglas


def _desplante_minimo() -> float:
    """'profundidad_cimentacion_min_cabezal_m' [N→], en segunda linea."""
    return _exigir_positivo(CRITERIO_DESPLANTE_MIN,
                            ca.valor(CRITERIO_DESPLANTE_MIN),
                            "profundidad minima de desplante del cabezal")


def _margen_socavacion() -> float:
    """'margen_zapata_bajo_socavacion_m' [C], finito y no negativo."""
    margen = ca.valor(CRITERIO_MARGEN_SOCAVACION)
    if not (_finito(margen) and margen >= 0):
        raise DatoInvalidoError(CRITERIO_MARGEN_SOCAVACION, valor=margen,
                                motivo="margen finito y no negativo")
    return float(margen)


def _lectura_del_margen(margen: float) -> Tuple[str, str, str, Tuple[str, ...]]:
    """
    --- VE-3.15, decision 14 --- La cita, el texto y la aplicacion del umbral
    del desplante bajo la hoya segun el margen DECLARADO: sin margen (el de
    archivo) rige la regla general de las zapatas (AASHTO 10.6.1.2) con la
    recomendacion de HEC-14 5.1.3, y AASHTO 12.6.5 queda de contraste; con un
    margen, la lectura de 12.6.5 que lo da como extremo alto de la ventana.
    """
    if margen > TOL_UMBRAL_NORMATIVO:
        return ("AASHTO_LRFD_9.12.6.5#ZAPATAS",
                "fondo de la hoya menos el margen declarado",
                "EXIGENCIA de AASHTO para las zapatas de las estructuras "
                "enterradas (2.0 ft), con el margen que el proyecto declara "
                "dentro de esa ventana, leida como aplicable a la del cabezal "
                "de salida ([C]; la lectura y lo que juega en contra, en la "
                "`Interpretacion` de la cita)",
                ("HEC14.5.1.3#CABEZAL", "AASHTO_LRFD_9.10.6.1.2#DESPLANTE"))
    return ("AASHTO_LRFD_9.10.6.1.2#DESPLANTE",
            "fondo de la hoya de la salida sin proteger, sin margen",
            "EXIGENCIA de AASHTO para las zapatas superficiales y "
            "RECOMENDACION de HEC-14 para el cabezal, aplicadas al cabezal de "
            "salida ([C], decision 14 del dueño): bajo la hoya SIN proteger, "
            "con el delantal de enrocado diseñado aparte. AASHTO 12.6.5 pide "
            "2.0 ft a las zapatas de las estructuras enterradas: contraste",
            ("HEC14.5.1.3#CABEZAL", "AASHTO_LRFD_9.12.6.5#ZAPATAS"))


def peralte_minimo_zapata(tipo: str) -> Tuple[float, str, str]:
    """
    El espesor MINIMO de la zapata del cabezal segun su tipo, m, con el
    texto de su origen y la cita que lo fija:

      * gravedad ciclopeo: 300 mm de E.060 22.7.4 (concreto simple), por
        analogia ('espesor_min_zapata_concreto_simple_m' [N→]; hasta el
        cierre de T-7c era una constante [N]);
      * voladizo armado: la altura minima sobre el refuerzo inferior de E.060
        15.7 ('peralte_min_zapata_armada_m', [N→]) mas lo que queda DEBAJO
        de ese refuerzo tal como la fila A8 del armado lo mide: el
        recubrimiento con que la cara inferior SE ARMA
        (`recubrimiento_para_armar`: la regla del mayor de la Sec. 0.2, o
        su cota mas exigente mientras falte la categoria del acero o el
        analisis quimico) y medio diametro de la MAYOR barra del catalogo
        de propuesta ('catalogo_barras_refuerzo_cabezal').

    --- verificacion de T-7 (punto 7) --- HASTA AQUI SUMABA SOLO LOS 70 mm
    de E.060 7.7.1 a), y la regla no podia cumplir nunca la norma que cita:
    0.30 + 0.070 = 0.37 m, y A8 mide hasta el EJE de la barra con un
    recubrimiento que la regla del mayor nunca deja bajo 70 mm -- 0.2722 m
    con la cota de 91.44 mm y 0.2937 m aun con las categorias B o C y una
    barra de 1/2" --. Ahora el piso se construye con la MISMA lectura de
    A8 (eje de la capa inferior) y con la barra mas gruesa que el armado
    puede proponer: un cabezal de regla cumple A8 por construccion, y una
    zapata DECLARADA mas delgada sigue pudiendo fallar (CB6 y A8). Sin
    redondeo: el piso es la suma, y se imprime con sus tres sumandos.

    Es el piso del espesor PROPUESTO (la regla H/10 gobierna por encima) y el
    umbral de CB6 cuando el espesor se DECLARA.
    """
    if tipo not in TIPOS_DE_CABEZAL:
        raise DatoInvalidoError(
            "tipo", valor=tipo,
            motivo="el minimo de la zapata depende del tipo de cabezal; se "
                   "espera " + " o ".join(TIPOS_DE_CABEZAL))
    if tipo == TIPO_GRAVEDAD:
        espesor = _exigir_positivo(
            CRITERIO_ESPESOR_ZAPATA_SIMPLE,
            ca.valor(CRITERIO_ESPESOR_ZAPATA_SIMPLE),
            "espesor minimo de la zapata de concreto simple")
        return (espesor,
                f"minimo de {espesor:.2f} m de concreto simple "
                f"({NUMERAL_ZAPATA_CONCRETO_SIMPLE}, por analogia, "
                f"'{CRITERIO_ESPESOR_ZAPATA_SIMPLE}' [N→])",
                CITA_ZAPATA_CONCRETO_SIMPLE)
    altura = _exigir_positivo(
        CRITERIO_PERALTE_ZAPATA_ARMADA,
        ca.valor(CRITERIO_PERALTE_ZAPATA_ARMADA),
        "altura minima de la zapata armada sobre su refuerzo")
    rec_mm, origen_rec, _aviso = recubrimiento_para_armar(
        condicion=CONDICION_RECUBRIMIENTO_ZAPATA)
    diametro_mm, _area, barra = catalogo_de_barras()["barras"][-1]
    debajo = (rec_mm + diametro_mm / 2) / MILIMETROS_POR_METRO
    return (altura + debajo,
            f"minimo de la zapata armada: {altura:.2f} m sobre el refuerzo "
            f"inferior (E.060 15.7, por analogia, '{CRITERIO_PERALTE_ZAPATA_ARMADA}'"
            f" [N→]), medidos hasta el eje de la capa inferior, + "
            f"{rec_mm:.2f} mm del recubrimiento con que se arma la cara "
            f"contra el suelo ({origen_rec}) + {diametro_mm / 2:.2f} mm de "
            f"medio diametro de la mayor barra del catalogo (Ø {barra}\")",
            CITA_PERALTE_ZAPATA_ARMADA)


def _dim(nombre, valor, regla, criterio, declarado,
         de=frozenset()) -> DimensionDeCabezal:
    """
    Una fila de la tabla de geometria con su ORIGEN: «declarada» si el punto
    la trae; «derivada de dimensiones declaradas» si la regla la calcula a
    partir de alguna que el punto declaro (`de`, sus nombres); y «propuesta
    por regla» solo si ninguna de sus entradas se declaro (correcciones de
    T-7a, H9: el talon con B declarado se imprimia «propuesta por regla»).
    """
    if declarado:
        return DimensionDeCabezal(nombre=nombre, valor=valor, unidad="m",
                                  origen=ORIGEN_DIMENSION_DECLARADA,
                                  regla="dato externo del punto "
                                        "(`cabezal_declarado`)")
    if de:
        return DimensionDeCabezal(
            nombre=nombre, valor=valor, unidad="m",
            origen=ORIGEN_DIMENSION_DERIVADA,
            regla=f"{regla}, con {', '.join(sorted(de))} declarado",
            criterio=criterio)
    return DimensionDeCabezal(nombre=nombre, valor=valor, unidad="m",
                              origen=ORIGEN_DIMENSION_REGLA, regla=regla,
                              criterio=criterio)


def predimensionar_aleros(*, embocadura: EmbocaduraDelPunto,
                          altura_inicial: float, espesor: float,
                          ancho_zapata: float, espesor_zapata: float,
                          talud: float, reglas: dict,
                          declaradas: Optional[dict] = None,
                          de_altura_inicial: frozenset = frozenset(),
                          de_espesor: frozenset = frozenset(),
                          id_punto: Optional[str] = None
                          ) -> Tuple[Optional[Aleros], Tuple[DimensionDeCabezal, ...], str]:
    """
    Los dos aleros de UN cabezal (INF-4.3), o None con cabezal recto.

        L_corto = (h0 - H_f) · talud / cos(alfa - theta)
        L_largo = (h0 - H_f) · talud / cos(alfa + theta)

    alfa es el angulo de los aleros con la PROLONGACION DE LA PARED DEL
    BARRIL (ΘW del HDS-5, List of Symbols, pag. impresa xix: «Flare angle of
    wingwalls with respect to extension of culvert side wall»;
    `embocadura_del_punto`) y theta el esviaje del cruce. EL TALUD DEL
    TERRAPLEN BAJA PERPENDICULAR A LA VIA, como lo modela
    `M7.longitud_conducto`, y el eje del conducto forma theta con esa
    direccion: con el cabezal normal al eje, un alero forma alfa - theta con
    la bajada del talud y el otro alfa + theta. Para bajar de h0 a H_f el
    talud avanza (h0 - H_f)·talud en planta, y cada alero lo recorre
    dividido por el COSENO de su angulo con esa direccion (por eso coseno y
    no seno: la convencion de la fuente mide desde el barril, y con el seno
    un alero paralelo, alfa -> 0, seria infinito). Con theta = 0 las dos
    longitudes son la misma, (h0 - H_f)·talud/cos(alfa). El CSV trae la
    magnitud del esviaje y no su sentido de giro: cual de los dos lados es el
    largo lo fija la planta del cruce, y los dos se llaman «corto» y «largo».

    h0 Y H_f SE MIDEN IGUAL (correcciones de T-7a, H6): son las alturas del
    alero sobre el pie, la inicial la del cabezal en su arranque (coronacion
    menos pie, bordillo incluido) y la final la de la punta. Con la cresta
    del alero paralela al talud un bordillo por encima de el, la caida del
    talud entre el arranque y la punta es exactamente h0 - H_f. Si H_f se
    leyera como la altura del TALUD en la punta (el alero sin bordillo
    alli), la caida seria h0 - bordillo - H_f y los aleros saldrian mas
    cortos: la lectura adoptada es la de MAS longitud.

    GUARDIA (forma MAT-D13): con alfa + theta >= 90 grados el alero largo
    corre paralelo al talud, o se aleja de su bajada, y no alcanza nunca la
    altura final: el denominador se anula. `LimiteNumericoError` con el par
    (alfa, theta) y lo que lo resuelve -- declarar los aleros por
    `cabezal_declarado` o un alfa menor dentro de la ventana --. Con la
    longitud declarada la formula no se evalua y no hay guardia.

    El espesor y la zapata del alero son los del cabezal en su arranque
    (regla del proyecto: el alero se desplanta con el cabezal y se
    predimensiona con sus reglas y su altura inicial, que es su maxima).
    Devuelve (aleros, dimensiones, nota). Si el talud ya esta a la altura
    final en el arranque (h0 <= H_f) no hay alero que alargar: longitud 0 y
    la nota lo dice.
    """
    declaradas = declaradas or {}
    if embocadura.angulo_aletas is None:
        return None, (), ""
    alfa = embocadura.angulo_aletas
    theta = embocadura.esviaje_grados
    if not (_finito(alfa) and alfa >= 0
            and math.cos(math.radians(alfa)) > TOL_UMBRAL_NORMATIVO):
        raise DatoInvalidoError(
            CRITERIO_ANGULO_ALETAS, valor=alfa, id_punto=id_punto,
            motivo="el angulo de los aleros con la pared del barril tiene "
                   "que estar en [0, 90): a 90 grados el alero esta en el "
                   "plano del muro y el talud no baja a lo largo de el")
    if not (_finito(theta) and theta >= 0):
        raise DatoInvalidoError(
            "esviaje_grados", valor=theta, id_punto=id_punto,
            motivo="la longitud de los aleros se mide con el esviaje del "
                   "cruce, y este no es un angulo finito y no negativo")
    largo_decl = CAMPO_ANGULO_ALERO_LARGO in declaradas
    alfa_largo = (_exigir_angulo(f"cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}",
                                 declaradas[CAMPO_ANGULO_ALERO_LARGO],
                                 "angulo declarado del alero largo", id_punto)
                  if largo_decl else alfa)
    _exigir_positivo("talud_terraplen", talud, "talud del terraplen (H:V)",
                     id_punto)
    h_f_decl = "altura_final_aleros_m" in declaradas
    H_f = (declaradas["altura_final_aleros_m"] if h_f_decl
           else reglas["altura_final_aleros_m"])
    caida = altura_inicial - H_f
    L_decl = "longitud_aleros_m" in declaradas
    if L_decl:
        L_corto = L_largo = declaradas["longitud_aleros_m"]
    else:
        cos_largo = math.cos(math.radians(alfa_largo + theta))
        if not cos_largo > TOL_UMBRAL_NORMATIVO:
            raise LimiteNumericoError(
                (f"cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}" if largo_decl
                 else CRITERIO_ANGULO_ALETAS),
                valor=(alfa_largo, theta), id_punto=id_punto,
                motivo=(f"con el alero largo a alfa = {alfa_largo:g} grados de "
                        f"la pared del barril y un esviaje theta = {theta:g} "
                        "grados, el alero largo forma alfa + theta = "
                        f"{alfa_largo + theta:g} grados con la bajada del "
                        "talud: corre paralelo a ella o se aleja, y no alcanza "
                        "nunca la altura final (cos(alfa + theta) se anula). "
                        "Declarar los aleros en `cabezal_declarado` "
                        f"(longitud_aleros_m, o {CAMPO_ANGULO_ALERO_LARGO} "
                        "menor de ese lado) o un alfa menor dentro de la "
                        f"ventana de '{CRITERIO_ANGULO_ALETAS}'"))
        cos_corto = math.cos(math.radians(alfa - theta))
        avance = max(caida, 0.0) * talud
        L_corto = avance / cos_corto
        L_largo = avance / cos_largo
    nota = ("" if caida > 0 else
            f"el talud ya esta a la altura final en el arranque del alero "
            f"(h0 = {altura_inicial:.3f} m <= H_f = {H_f:.3f} m): el alero no "
            "se alarga")
    e_decl = "espesor_aleros_m" in declaradas
    e = declaradas["espesor_aleros_m"] if e_decl else espesor
    # --- VE-7 (dictamen Fable, abierto (d)) --- la zapata propia de los
    # aleros, declarada: gana sobre la del cabezal (que es solo el punto de
    # partida de su dimensionamiento) y no se itera.
    bz_decl = CAMPO_ANCHO_ZAPATA_ALEROS in declaradas
    ez_decl = CAMPO_ESPESOR_ZAPATA_ALEROS in declaradas
    aleros = Aleros(angulo_grados=alfa, angulo_largo_grados=alfa_largo,
                    esviaje_grados=float(theta),
                    longitud_corto=L_corto, longitud_largo=L_largo,
                    altura_inicial=altura_inicial, altura_final=H_f,
                    espesor=e,
                    ancho_zapata=(declaradas[CAMPO_ANCHO_ZAPATA_ALEROS]
                                  if bz_decl else ancho_zapata),
                    espesor_zapata=(declaradas[CAMPO_ESPESOR_ZAPATA_ALEROS]
                                    if ez_decl else espesor_zapata))
    de_L = frozenset(de_altura_inicial) | (
        frozenset({"altura_final_aleros_m"}) if h_f_decl else frozenset())
    sustitucion = (f"({altura_inicial:.3f} - {H_f:.3f})·{talud:g}")
    angulo_largo = (
        (DimensionDeCabezal(nombre="angulo del alero largo", valor=alfa_largo,
                            unidad="grados", origen=ORIGEN_DIMENSION_DECLARADA,
                            regla="dato externo del punto "
                                  f"(`cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}`)"
                                  ": aleros asimetricos"),)
        if largo_decl else ())
    dims = (
        DimensionDeCabezal(nombre="angulo de los aleros", valor=alfa,
                           unidad="grados", origen=ORIGEN_DIMENSION_REGLA,
                           regla=embocadura.regla,
                           criterio=embocadura.criterio_angulo),
    ) + angulo_largo + (
        _dim("altura final de los aleros (H_f)", H_f,
             "regla 'altura_final_aleros_m'", CRITERIO_GEOMETRIA, h_f_decl),
        _dim("longitud del alero corto (alfa - theta)", L_corto,
             f"(h0 - H_f)·talud/cos(alfa - theta) = {sustitucion}/"
             f"cos({alfa:g} - {theta:g})", CRITERIO_GEOMETRIA, L_decl,
             de=de_L),
        _dim("longitud del alero largo (alfa + theta)", L_largo,
             f"(h0 - H_f)·talud/cos(alfa + theta) = {sustitucion}/"
             f"cos({alfa_largo:g} + {theta:g})", CRITERIO_GEOMETRIA, L_decl,
             de=de_L | (frozenset({CAMPO_ANGULO_ALERO_LARGO})
                        if largo_decl else frozenset())),
        _dim("espesor de los aleros", e,
             "el de la pantalla del cabezal en la corona", CRITERIO_GEOMETRIA,
             e_decl, de=de_espesor),
    ) + tuple(
        _dim(nombre, valor, "dato externo del punto (`cabezal_declarado."
             f"{campo}`)", CRITERIO_GEOMETRIA, True)
        for nombre, valor, campo, declarado in (
            ("ancho de la zapata de los aleros", aleros.ancho_zapata,
             CAMPO_ANCHO_ZAPATA_ALEROS, bz_decl),
            ("espesor de la zapata de los aleros", aleros.espesor_zapata,
             CAMPO_ESPESOR_ZAPATA_ALEROS, ez_decl))
        if declarado)
    return aleros, dims, nota


def predimensionar_cabezal(*, extremo: ExtremoDelConducto,
                           embocadura: EmbocaduraDelPunto,
                           talud: float,
                           declaradas: Optional[dict] = None,
                           tipo_declarado: Optional[str] = None,
                           id_punto: Optional[str] = None,
                           ancho_por_estabilidad: Optional[float] = None,
                           espesor_por_armado: Optional[float] = None,
                           punta_por_estabilidad: Optional[float] = None,
                           pantalla_por_armado: Optional[float] = None,
                           alero_por_armado: Optional[float] = None
                           ) -> GeometriaCabezal:
    """
    La geometria PROPUESTA del cabezal de UN extremo (INF-4.2), con las
    reglas declaradas de 'predimensionamiento_cabezal' [A] y los minimos que
    las normas escriben con su numero. Cada dimension sale con su origen
    (`GeometriaCabezal.dimensiones`): «propuesta por regla», «declarada» --
    la que el punto trae en `declaradas`, que gana -- o «derivada de
    dimensiones declaradas» -- la que la regla calcula a partir de una
    declarada --.

    --- VE-3.5 --- `ancho_por_estabilidad` es el ancho de zapata que el
    dimensionamiento por estabilidad adopto
    (`dimensionar_zapata_por_estabilidad`): sustituye al de la regla solo si
    el punto NO declaro `ancho_zapata_m` (lo declarado gana siempre), crece
    por el TALON -- la punta queda en la de la regla, fraccion_punta·B de la
    regla, salvo que se declare -- y la zapata y el talon salen con el origen
    «dimensionada por estabilidad».

        coronacion   = max(clave exterior + recubrimiento + bordillo,
                           nivel de agua del extremo + resguardo)
        D_f          = max(0.80 m [N→, E.050 Art. 26.2 por analogia],
                           pie - (fondo de la hoya - margen) [C, AASHTO
                           12.6.5; solo a la salida y solo si la Fase 6
                           entrego la socavacion])
        desplante    = pie - D_f
        H_c          = coronacion - desplante  (= H + e_zapata)
        tipo         = gravedad ciclopeo si H_c <= altura maxima; si no,
                       voladizo armado (H_c es la altura TOTAL, desplante
                       incluido: con altura interior >= 0.90 m la rama de
                       gravedad no se alcanza con el umbral de archivo)
        pantalla     = 0.30 m (voladizo) | H_c / 6 (gravedad), corona = base
        zapata       = B = 0.7·H_c; e = max(H_c/10, minimo del tipo: 0.30 m
                       de concreto simple, E.060 22.7.4 [N]; 0.30 m sobre el
                       refuerzo + 0.07 m de recubrimiento en el armado, E.060
                       15.7 [N→] y 7.7.1); punta = 0.33·B;
                       talon = B - punta - pantalla
        L_c          = ancho exterior del conducto + 2·empotramiento
        losa         = 1.5·D de largo, 0.30 m de espesor, sobre el terreno
                       del pie; dentellon con su base en
                       min(pie - 0.80 m [N→, Lamina Nº 04],
                           fondo de la hoya - margen [C, AASHTO 12.6.5]),
                       0.40 m de ancho

    EL TERRENO ES UNO POR EXTREMO (correcciones de T-7a, H3): el pie del
    muro (`ExtremoDelConducto.cota_pie`) es la referencia del desplante, de
    la losa y del dentellon, cuya profundidad se mide desde ese terreno como
    la cota «0.80 min.» de la Lamina Nº 04 -- no desde la cara superior de
    la losa ni desde la solera --.

    El muro se supone NORMAL al eje del conducto y de trasdos vertical
    (beta = 0). CON ESVIAJE ESO TIENE UN PRECIO, y se dice: el talud baja
    perpendicular a la via, de modo que a lo largo de un muro normal al eje
    queda a cotas distintas en sus dos extremos, Δz = L_c·sen(theta)/talud,
    y la corona horizontal no coincide con el talud en toda su longitud;
    `cabezal_del_punto` lo avisa. Los dos aleros resultan de longitudes
    distintas (`predimensionar_aleros`). La alternativa -- un cabezal
    paralelo a la via, esviado respecto del barril (Carta 11 del HDS-5) --
    existe desde VE-6 SOLO PARA EL MARCO (ficha T7A-03): sin aleros, con
    L_c = ancho exterior/cos(theta) + 2·empotramiento, y la corona sigue al
    talud. La estabilidad de lo propuesto NO se
    juzga aqui (T-7b): esta funcion propone, y
    `verificar_compatibilidad_cabezal` comprueba que lo propuesto -- o lo
    declarado -- remate al conducto.
    """
    declaradas = dict(declaradas or {})
    # --- VE-6 (ficha T7B-11) --- la planta del cruce que el punto declara
    # para este cabezal (las dos claves de la sobrecarga del punto, que el
    # servicio funde aqui por extremo): no son dimensiones, viajan con la
    # geometria.
    orientacion_trafico = declaradas.pop(CAMPO_ORIENTACION_DEL_PUNTO, None)
    distancia_borde = declaradas.pop(CAMPO_DISTANCIA_BORDE_DEL_PUNTO, None)
    reglas = _reglas()
    for nombre, x in declaradas.items():
        if nombre in ANGULOS_DECLARABLES:
            _exigir_angulo(f"cabezal_declarado.{nombre}", x,
                           f"angulo declarado del cabezal de "
                           f"{extremo.extremo}", id_punto)
            continue
        if nombre not in DIMENSIONES_DECLARABLES:
            raise DatoInvalidoError(
                "cabezal_declarado", valor=nombre, id_punto=id_punto,
                motivo="no es una dimension declarable del cabezal: "
                       + ", ".join(DIMENSIONES_DECLARABLES
                                   + ANGULOS_DECLARABLES))
        _exigir_positivo(f"cabezal_declarado.{nombre}", x,
                         f"dimension declarada del cabezal de "
                         f"{extremo.extremo}", id_punto)
    for campo in ("cota_solera", "cota_pie", "cota_clave_exterior",
                  "cota_agua"):
        _exigir_finito(campo, getattr(extremo, campo),
                       f"{campo} del extremo {extremo.extremo}", id_punto)
    _exigir_positivo("ancho_exterior", extremo.ancho_exterior,
                     "ancho exterior del conducto", id_punto)
    dims = []
    # De que dimensiones DECLARADAS depende cada cantidad (H9): vacio =
    # sale solo de las reglas.
    de: dict = {}
    nada = frozenset()

    # 1. Desplante
    df_min = _desplante_minimo()
    df_por_socavacion = None
    margen = None
    if extremo.cota_fondo_hoya is not None:
        margen = _margen_socavacion()
        _exigir_finito("cota_fondo_hoya", extremo.cota_fondo_hoya,
                       "fondo de la hoya de socavacion", id_punto)
        df_por_socavacion = extremo.cota_pie - (extremo.cota_fondo_hoya - margen)
    df_decl = "profundidad_desplante_m" in declaradas
    if df_decl:
        D_f = declaradas["profundidad_desplante_m"]
    else:
        D_f = max(df_min, df_por_socavacion if df_por_socavacion is not None
                  else df_min)
    de["desplante"] = (frozenset({"profundidad_desplante_m"}) if df_decl
                       else nada)
    desplante = extremo.cota_pie - D_f
    dims.append(_dim(
        "profundidad de desplante (D_f)", D_f,
        (f"max({df_min:.2f} m de E.050 Art. 26.2 por analogia, pie - (fondo "
         f"de la hoya - margen de '{CRITERIO_MARGEN_SOCAVACION}'))"
         if df_por_socavacion is not None else
         f"{df_min:.2f} m de E.050 Art. 26.2 por analogia (sin socavacion "
         "entregada por la Fase 6)"),
        CRITERIO_DESPLANTE_MIN, df_decl))

    # 2. Coronacion y altura total
    h_decl = "altura_total_m" in declaradas
    cor_relleno = (extremo.cota_clave_exterior
                   + reglas["recubrimiento_clave_m"] + reglas["bordillo_m"])
    cor_agua = extremo.cota_agua + reglas["resguardo_agua_m"]
    if h_decl:
        H_c = declaradas["altura_total_m"]
        coronacion = desplante + H_c
        de["H_c"] = nada
        de["corona"] = frozenset({"altura_total_m"}) | de["desplante"]
    else:
        coronacion = max(cor_relleno, cor_agua)
        H_c = coronacion - desplante
        de["H_c"] = de["desplante"]
        de["corona"] = nada
    if not H_c > 0:
        raise DatoInvalidoError(
            "altura_total_m", valor=H_c, id_punto=id_punto,
            motivo=f"la coronacion ({coronacion:.3f} msnm) no queda sobre "
                   f"el desplante ({desplante:.3f} msnm) del cabezal de "
                   f"{extremo.extremo}")
    dims.append(_dim(
        "altura total del cabezal (H_c, base de zapata a corona)", H_c,
        "coronacion - desplante, coronacion = max(clave exterior + "
        "recubrimiento + bordillo, nivel de agua + resguardo)",
        CRITERIO_GEOMETRIA, h_decl, de=de["H_c"]))
    if h_decl:
        de["H_c"] = frozenset({"altura_total_m"})

    # 3. Tipo
    if tipo_declarado is not None:
        if tipo_declarado not in TIPOS_DE_CABEZAL:
            raise DatoInvalidoError(
                "cabezal_declarado.tipo", valor=tipo_declarado,
                id_punto=id_punto,
                motivo="se espera " + " o ".join(TIPOS_DE_CABEZAL))
        tipo = tipo_declarado
        de_tipo = frozenset({CAMPO_TIPO_DECLARADO})
    else:
        tipo = (TIPO_GRAVEDAD if H_c <= reglas["altura_max_gravedad_m"]
                + TOL_UMBRAL_NORMATIVO else TIPO_VOLADIZO)
        de_tipo = nada

    # 4. Pantalla
    if tipo == TIPO_VOLADIZO:
        e_regla = reglas["espesor_pantalla_voladizo_m"]
        texto_e = "regla 'espesor_pantalla_voladizo_m'"
        de_e = de_tipo
    else:
        e_regla = H_c / reglas["divisor_espesor_gravedad"]
        texto_e = (f"H_c / {reglas['divisor_espesor_gravedad']:g} (regla "
                   "'divisor_espesor_gravedad')")
        de_e = de_tipo | de["H_c"]
    ec_decl = "espesor_corona_m" in declaradas
    eb_decl = "espesor_base_muro_m" in declaradas
    e_corona = declaradas["espesor_corona_m"] if ec_decl else e_regla
    e_base = declaradas["espesor_base_muro_m"] if eb_decl else e_regla
    de["e_corona"] = frozenset({"espesor_corona_m"}) if ec_decl else de_e
    de["e_base"] = frozenset({"espesor_base_muro_m"}) if eb_decl else de_e
    # --- VE-3.14 (H-1 de los ensayos de diseño del cabezal) --- La pantalla
    # de espesor uniforme que el armado hizo crecer
    # (`dimensionar_pantalla_por_armado`): la corona y el arranque crecen
    # juntos (desde VE-6 el alero NO lo hereda) y la zapata crece lo
    # mismo, de modo que la punta y el talon no cambian. Lo declarado gana.
    crecimiento_pantalla = 0.0
    # --- VE-6 --- el espesor del que PARTE el alero: el de la corona antes
    # de que el armado de la pantalla la haga crecer (la regla, o la corona
    # declarada); su propio armado lo hace crecer aparte.
    e_alero_partida = e_corona
    pantalla_por_arm = (pantalla_por_armado is not None and not ec_decl
                        and not eb_decl and tipo == TIPO_VOLADIZO)
    if pantalla_por_arm:
        crecimiento_pantalla = pantalla_por_armado - e_base
        e_corona = e_base = pantalla_por_armado
        for nombre in ("espesor de la pantalla en la corona",
                       "espesor de la pantalla en el arranque"):
            dims.append(DimensionDeCabezal(
                nombre=nombre, valor=pantalla_por_armado, unidad="m",
                origen=ORIGEN_DIMENSION_ARMADO,
                regla=(f"el menor de la grilla {e_regla:.3f} m + k·paso con "
                       "el que el armado de la pantalla cumple, partiendo de "
                       f"{texto_e}"),
                criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
    else:
        dims.append(_dim("espesor de la pantalla en la corona", e_corona,
                         texto_e, CRITERIO_GEOMETRIA, ec_decl, de=de_e))
        dims.append(_dim("espesor de la pantalla en el arranque", e_base,
                         texto_e + "; trasdos vertical", CRITERIO_GEOMETRIA,
                         eb_decl, de=de_e))

    # 5. Zapata
    B_decl = "ancho_zapata_m" in declaradas
    B_regla = reglas["fraccion_ancho_zapata"] * H_c + crecimiento_pantalla
    B = declaradas["ancho_zapata_m"] if B_decl else B_regla
    texto_B = (f"{reglas['fraccion_ancho_zapata']:g}·H_c (regla "
               "'fraccion_ancho_zapata')")
    por_estabilidad = ancho_por_estabilidad is not None and not B_decl
    if por_estabilidad:
        B = ancho_por_estabilidad + crecimiento_pantalla
        dims.append(DimensionDeCabezal(
            nombre="ancho de la zapata (B)", valor=B, unidad="m",
            origen=ORIGEN_DIMENSION_ESTABILIDAD,
            regla=(f"el menor de la grilla {B_regla:.3f} m + k·paso que "
                   f"cumple la estabilidad, partiendo de {texto_B}"),
            criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
    else:
        dims.append(_dim("ancho de la zapata (B)", B, texto_B,
                         CRITERIO_GEOMETRIA, B_decl, de=de["H_c"]))
    de["B"] = frozenset({"ancho_zapata_m"}) if B_decl else de["H_c"]
    ez_decl = "espesor_zapata_m" in declaradas
    if ez_decl:
        e_z = declaradas["espesor_zapata_m"]
        texto_ez = ""
        de_ez = nada
        criterio_ez = CRITERIO_GEOMETRIA
    else:
        e_z = H_c / reglas["divisor_peralte_zapata"]
        texto_ez = (f"H_c / {reglas['divisor_peralte_zapata']:g} (regla "
                    "'divisor_peralte_zapata')")
        de_ez = de_tipo | de["H_c"]
        criterio_ez = CRITERIO_GEOMETRIA
        piso, texto_piso, _cita = peralte_minimo_zapata(tipo)
        if e_z < piso:
            e_z = piso
            texto_ez = f"{texto_piso}, mayor que {texto_ez}"
            de_ez = de_tipo
            criterio_ez = (CRITERIO_PERALTE_ZAPATA_ARMADA
                           if tipo == TIPO_VOLADIZO else CRITERIO_GEOMETRIA)
    # --- VE-3.9 --- El peralte que el armado de la zapata hizo crecer
    # (`dimensionar_peralte_por_armado`): no lo eligio la regla ni lo
    # declaro nadie. La altura total no cambia (la fijan las cotas): crece
    # la zapata hacia arriba y la pantalla sobre ella se acorta.
    if espesor_por_armado is not None and not ez_decl:
        dims.append(DimensionDeCabezal(
            nombre="espesor de la zapata", valor=espesor_por_armado,
            unidad="m", origen=ORIGEN_DIMENSION_ARMADO,
            regla=(f"el menor de la grilla {e_z:.3f} m + k·paso con el que "
                   "el armado de la zapata (punta y talon) cumple, partiendo "
                   f"de {texto_ez}"),
            criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
        e_z = espesor_por_armado
    else:
        dims.append(_dim("espesor de la zapata", e_z, texto_ez or "-",
                         criterio_ez, ez_decl, de=de_ez))
    if not H_c > e_z:
        raise DatoInvalidoError(
            "espesor_zapata_m", valor=e_z, id_punto=id_punto,
            motivo=f"la zapata ({e_z:.3f} m) no deja muro sobre ella con la "
                   f"altura total del cabezal de {extremo.extremo} "
                   f"({H_c:.3f} m)")
    p_decl = "ancho_punta_m" in declaradas
    # Con B dimensionado por estabilidad la punta queda en la de la REGLA
    # (VE-3.5): crece el talon, que suma el peso del relleno.
    punta = (declaradas["ancho_punta_m"] if p_decl
             else reglas["fraccion_punta"]
             * ((B_regla if por_estabilidad else B) - crecimiento_pantalla))
    # --- VE-3.14 (H-5 de los ensayos de diseño del cabezal) --- La punta
    # tambien puede crecer: cuando con el talon al tope la estabilidad no
    # cumple (suelo cohesivo, excentricidad hacia la punta), el
    # dimensionamiento prueba hacerla crecer (`dimensionar_zapata_por_
    # estabilidad`). Una punta declarada gana.
    punta_por_est = (punta_por_estabilidad is not None and por_estabilidad
                     and not p_decl)
    if punta_por_est:
        punta = punta_por_estabilidad
        dims.append(DimensionDeCabezal(
            nombre="ancho de la punta", valor=punta, unidad="m",
            origen=ORIGEN_DIMENSION_ESTABILIDAD,
            regla=("la punta de la regla + k·paso: con el talon al tope la "
                   "estabilidad no cumplia y crecio la punta"),
            criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
    else:
        dims.append(_dim("ancho de la punta", punta,
                         f"{reglas['fraccion_punta']:g}·B (regla "
                         "'fraccion_punta')", CRITERIO_GEOMETRIA, p_decl,
                         de=de["B"]))
    de["punta"] = frozenset({"ancho_punta_m"}) if p_decl else de["B"]
    talon = B - punta - e_base
    if not talon >= 0:
        raise DatoInvalidoError(
            "ancho_zapata_m", valor=B, id_punto=id_punto,
            motivo=f"el talon sale negativo en el cabezal de "
                   f"{extremo.extremo}: B = {B:.3f} m no alcanza para la "
                   f"punta ({punta:.3f} m) y la pantalla ({e_base:.3f} m)")
    if por_estabilidad:
        dims.append(DimensionDeCabezal(
            nombre="ancho del talon", valor=talon, unidad="m",
            origen=ORIGEN_DIMENSION_ESTABILIDAD,
            regla=("B - punta - pantalla, con B dimensionado por "
                   "estabilidad" + (" y la punta crecida (el talon queda en "
                                    "la de la regla)" if punta_por_est else
                                    " (la punta queda en la de la regla: "
                                    "crece el talon)")),
            criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
    else:
        dims.append(_dim("ancho del talon", talon, "B - punta - pantalla",
                         CRITERIO_GEOMETRIA, False,
                         de=de["B"] | de["punta"] | de["e_base"]))

    # 6. Longitud del muro
    L_decl = "longitud_m" in declaradas
    # --- VE-6 (ficha T7A-03) --- con el muro paralelo a la via la boca se
    # corta en oblicuo y mide ancho/cos(theta) a lo largo del muro.
    factor_cara = factor_cara_del_muro(embocadura)
    boca = extremo.ancho_exterior * factor_cara
    L_c = (declaradas["longitud_m"] if L_decl else
           boca + 2 * reglas["empotramiento_lateral_m"])
    dims.append(_dim("longitud del muro (L_c)", L_c,
                     (f"ancho exterior del conducto ({extremo.ancho_exterior:.3f}"
                      " m) + 2·empotramiento (regla 'empotramiento_lateral_m')"
                      if not es_paralelo_a_la_via(embocadura) else
                      f"ancho exterior del conducto ({extremo.ancho_exterior:.3f}"
                      f" m) / cos({embocadura.esviaje_grados:g}) = "
                      f"{boca:.3f} m, la boca cortada en oblicuo por el muro "
                      "paralelo a la via, + 2·empotramiento (regla "
                      "'empotramiento_lateral_m')"),
                     CRITERIO_GEOMETRIA, L_decl))

    # 7. Aleros: h0 = coronacion - pie (ver `predimensionar_aleros`)
    aleros, dims_aleros, _nota = predimensionar_aleros(
        embocadura=embocadura, altura_inicial=coronacion - extremo.cota_pie,
        espesor=(alero_por_armado if alero_por_armado is not None
                 else e_alero_partida),
        ancho_zapata=B, espesor_zapata=e_z, talud=talud,
        reglas=reglas, declaradas=declaradas,
        de_altura_inicial=de["corona"], de_espesor=de["e_corona"],
        id_punto=id_punto)
    if aleros is not None and CAMPO_ANCHO_ZAPATA_ALEROS in declaradas:
        # --- VE-7 (abierto (d)) --- el ancho propio declarado tiene que
        # alcanzar para el fuste del alero (y, en gravedad, para la punta y
        # la base de su franja del arranque).
        if tipo == TIPO_GRAVEDAD:
            H0 = H_c - aleros.espesor_zapata
            necesario = punta + aleros.espesor + (e_base - e_corona) * H0 / (
                H_c - e_z)
        else:
            necesario = aleros.espesor
        if aleros.ancho_zapata < necesario - TOL_UMBRAL_NORMATIVO:
            raise DatoInvalidoError(
                f"cabezal_declarado.{CAMPO_ANCHO_ZAPATA_ALEROS}",
                valor=aleros.ancho_zapata, id_punto=id_punto,
                motivo=f"la zapata de los aleros declarada "
                       f"({aleros.ancho_zapata:.3f} m) no alcanza para el "
                       f"fuste del alero ({necesario:.3f} m"
                       + (" con la punta y la base de su franja"
                          if tipo == TIPO_GRAVEDAD else "") + ")")
    if alero_por_armado is not None:
        # --- VE-6 (ficha VE6M9-03) --- el alero dimensionado por el armado
        # de SUS dos secciones (`_dimensionar_aleros`), no por el de la
        # pantalla; un espesor declarado gana (lo deja `predimensionar_
        # aleros` con su origen).
        dims_aleros = tuple(
            replace(d, origen=ORIGEN_DIMENSION_ARMADO,
                    regla=(f"el menor de la grilla {e_alero_partida:.3f} m + "
                           "k·paso con el que el armado de las dos secciones "
                           "del alero (arranque y mitad) cumple"),
                    criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA)
            if (d.nombre == "espesor de los aleros"
                and d.origen != ORIGEN_DIMENSION_DECLARADA) else d
            for d in dims_aleros)
    dims.extend(dims_aleros)

    # 8. Losa de entrega y dentellon, sobre el terreno del pie (H3)
    dentellon = ca.valor(CRITERIO_DENTELLON)
    prof_min = _exigir_positivo(CRITERIO_DENTELLON,
                                dentellon.get("profundidad_min_m"),
                                "profundidad minima del dentellon")
    ancho_dent = _exigir_positivo(CRITERIO_DENTELLON, dentellon.get("ancho_m"),
                                  "ancho del dentellon")
    ll_decl = "longitud_losa_m" in declaradas
    largo_losa = (declaradas["longitud_losa_m"] if ll_decl else
                  reglas["fraccion_longitud_losa"] * extremo.altura_interior)
    el_decl = "espesor_losa_m" in declaradas
    e_losa = (declaradas["espesor_losa_m"] if el_decl
              else reglas["espesor_losa_m"])
    pd_decl = "profundidad_dentellon_m" in declaradas
    terreno = extremo.cota_pie
    if pd_decl:
        prof_dent = declaradas["profundidad_dentellon_m"]
        texto_dent = ""
    elif extremo.cota_fondo_hoya is not None:
        prof_dent = max(prof_min,
                        terreno - (extremo.cota_fondo_hoya - margen))
        texto_dent = (f"base en min(pie - {prof_min:.2f} m de la Lamina Nº 04 "
                      "[N→], fondo de la hoya - margen de "
                      f"'{CRITERIO_MARGEN_SOCAVACION}' [C])")
    else:
        prof_dent = prof_min
        texto_dent = (f"{prof_min:.2f} m de la Lamina Nº 04 [N→] bajo el "
                      "terreno del pie (sin socavacion entregada)")
    losa = LosaDeEntrega(longitud=largo_losa, espesor=e_losa,
                         profundidad_dentellon=prof_dent,
                         ancho_dentellon=ancho_dent, cota_terreno=terreno,
                         cota_base_dentellon=terreno - prof_dent)
    dims.append(_dim("longitud de la losa de entrega", largo_losa,
                     f"{reglas['fraccion_longitud_losa']:g}·D (regla "
                     "'fraccion_longitud_losa')", CRITERIO_GEOMETRIA, ll_decl))
    dims.append(_dim("espesor de la losa de entrega", e_losa,
                     "regla 'espesor_losa_m'", CRITERIO_GEOMETRIA, el_decl))
    dims.append(_dim("profundidad del dentellon (desde el terreno del pie)",
                     prof_dent, texto_dent or "-", CRITERIO_DENTELLON,
                     pd_decl))
    dims.append(_dim("ancho del dentellon", ancho_dent,
                     "0.40 m de la Lamina Nº 04 [N→]", CRITERIO_DENTELLON,
                     False))

    return GeometriaCabezal(
        H=H_c - e_z, B=B, D_f=D_f, espesor_corona=e_corona,
        espesor_base_muro=e_base, espesor_zapata=e_z, beta_grados=0.0,
        ancho_talon=talon, longitud=L_c, tipo=tipo, id_punto=id_punto,
        extremo=extremo.extremo, cota_coronacion=coronacion,
        cota_desplante=desplante, ancho_punta=punta, aleros=aleros,
        losa=losa, dimensiones=tuple(dims),
        orientacion_trafico=orientacion_trafico,
        distancia_borde_calzada_m=distancia_borde)


def _verificacion_cb(*, codigo: str, extremo: str, que: str, formula: str,
                     obtenido: float, admisible: float, mayor_o_igual: bool,
                     sustitucion: tuple, resultado: Magnitud,
                     descripcion_umbral: str, cita: str, aplicacion: str,
                     criterio: Optional[str], citas: Tuple[str, ...] = (),
                     numeral: str = "") -> Tuple[dict, dict]:
    """
    Lo comun de una verificacion CB, en la forma de las G de 7.B: los
    argumentos del paso y los de la `Verificacion`. El `paso()` lo llama
    cada verificacion con su fundamento LITERAL (el indice de formulas
    localiza al emisor por el literal: `test_indice_formulas`).
    """
    if mayor_o_igual:
        cumple = obtenido >= admisible - TOL_UMBRAL_NORMATIVO
        margen = obtenido - admisible
    else:
        cumple = obtenido <= admisible + TOL_UMBRAL_NORMATIVO
        margen = admisible - obtenido
    cod = f"{codigo}.{extremo[0]}"
    kw_paso = dict(
        codigo=cod, que=f"{que} (cabezal de {extremo})",
        formula=formula, citas_textuales=(cita,) + tuple(citas),
        sustitucion=sustitucion, resultado=resultado,
        umbral=Umbral(descripcion=descripcion_umbral, valor=admisible,
                      unidad=resultado.unidad, cita_id=cita,
                      caracter=_caracter_de(cita), aplicacion=aplicacion,
                      criterio_aplicado=criterio),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.CUMPLE if cumple
                  else TipoDeVeredicto.NO_CUMPLE),
            margen=margen, unidad=resultado.unidad,
            explicacion=("cumple con margen" if cumple else
                         "no cumple: la dimension declarada no remata al "
                         "conducto o queda bajo su minimo; corregirla en "
                         "`cabezal_declarado` o retirarla para que rija la "
                         "regla")))
    kw_verificacion = dict(
        cumple=cumple,
        numeral=(numeral or NUMERAL_9_0) + f", cabezal de {extremo}",
        valor_obtenido=obtenido, valor_admisible=admisible,
        criterio_aplicado=criterio, codigo=cod)
    return kw_paso, kw_verificacion


def verificar_compatibilidad_cabezal(*, geometria: GeometriaCabezal,
                                     extremo: ExtremoDelConducto,
                                     embocadura: Optional[EmbocaduraDelPunto]
                                     = None
                                     ) -> Tuple[Verificacion, ...]:
    """
    Lo que la ficha de 'predimensionamiento_cabezal' llevaba como
    `verificacion_pendiente` -- «la geometria tiene que ser COMPATIBLE con la
    SECCION adoptada y con la altura de terraplen» --, hecho verificacion, y
    los minimos con numero que una dimension DECLARADA puede violar
    (correcciones de T-7a, H4):

        CB1  L_c >= ancho exterior del conducto           (el muro contiene la boca)
        CB2  coronacion >= clave exterior + recubrimiento  (retiene el relleno)
        CB3  coronacion >= nivel de agua + resguardo      (el agua no lo rebasa)
        CB4  D_f >= 0.80 m                  [N→] E.050 Art. 26.2, por analogia
        CB5  desplante <= fondo de la hoya - margen        [C] AASHTO 12.6.5
             (solo a la salida y solo con socavacion entregada por la Fase 6)
        CB6  espesor de la zapata >= minimo de su tipo:
             gravedad 0.30 m [N] E.060 22.7.4; voladizo armado 0.30 m sobre
             el refuerzo [N→] E.060 15.7 + 0.07 m de recubrimiento (7.7.1)
        CB7  base del dentellon <= min(terreno del pie - 0.80 m [N→, Lamina
             Nº 04], fondo de la hoya - margen [C, AASHTO 12.6.5 «extending
             below»]); el segundo, solo con socavacion entregada

    Con las dimensiones propuestas por regla cumplen por construccion; las
    que el proyectista DECLARA por punto pueden no cumplir, y entonces el
    punto lleva la verificacion incumplida con su remedio. Codigo con el
    extremo: CB1.e, CB1.s, ...
    """
    reglas = _reglas()
    ext = extremo.extremo
    v = []
    # --- VE-6 (ficha T7A-03) --- con el muro paralelo a la via, la boca que
    # tiene que contener mide ancho/cos(theta) a lo largo de el.
    paralelo = embocadura is not None and es_paralelo_a_la_via(embocadura)
    boca = extremo.ancho_exterior * (factor_cara_del_muro(embocadura)
                                     if paralelo else 1)
    kp, kv = _verificacion_cb(
            codigo="CB1", extremo=ext,
            que="Longitud del muro frente al ancho exterior del conducto",
            formula=("L_c >= ancho exterior del conducto / cos(esviaje) "
                     "(muro paralelo a la via)" if paralelo else
                     "L_c >= ancho exterior del conducto"),
            obtenido=geometria.longitud, admisible=boca,
            mayor_o_igual=True,
            sustitucion=(Magnitud("ancho_exterior", extremo.ancho_exterior,
                                  "m", "seccion adoptada (Fase 4) con su "
                                  "pared y sus celdas", cifras=CIFRAS_MAGNITUD),)
            + ((Magnitud("esviaje", embocadura.esviaje_grados, "grados",
                         "el muro paralelo a la via corta al barril en "
                         "oblicuo", cifras=CIFRAS_MAGNITUD),)
               if paralelo else ()),
            resultado=Magnitud("L_c", geometria.longitud, "m",
                               "longitud del muro de cabecera",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="ancho exterior del conducto en planta",
            cita="MC_HHD.LAMINA_02A",
            aplicacion="LECTURA DEL PROYECTO sobre la lamina: el muro de "
                       "cabecera tiene que contener la boca del conducto; "
                       "la lamina lo dibuja asi y no lo acota",
            criterio=CRITERIO_GEOMETRIA)
    v.append(Verificacion(**kv, paso=paso("F9.DIMENSIONES", **kp)))
    kp, kv = _verificacion_cb(
            codigo="CB2", extremo=ext,
            que="Coronacion frente a la clave exterior mas el relleno "
                "retenido",
            formula="coronacion >= clave exterior + recubrimiento",
            obtenido=geometria.cota_coronacion,
            admisible=(extremo.cota_clave_exterior
                       + reglas["recubrimiento_clave_m"]),
            mayor_o_igual=True,
            sustitucion=(
                Magnitud("clave_exterior", extremo.cota_clave_exterior,
                         "msnm", "solera + altura interior + pared "
                         "(M5.cota_clave)", cifras=CIFRAS_MAGNITUD),
                Magnitud("recubrimiento", reglas["recubrimiento_clave_m"],
                         "m", "regla 'recubrimiento_clave_m' de "
                         f"'{CRITERIO_GEOMETRIA}' [A]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("coronacion", geometria.cota_coronacion,
                               "msnm", "coronacion del cabezal",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="clave exterior mas el relleno que el muro "
                               "retiene sobre ella",
            cita="HDS5_3ED.3.3.5#ENCAJE",
            aplicacion="REGLA DEL PROYECTO [A]: la fuente manda dimensionar "
                       "los cabezales al encajar la seccion; el relleno que "
                       "el muro retiene sobre la clave lo adopta el proyecto",
            criterio=CRITERIO_GEOMETRIA)
    v.append(Verificacion(**kv, paso=paso("F9.CORONACION", **kp)))
    kp, kv = _verificacion_cb(
            codigo="CB3", extremo=ext,
            que="Coronacion frente al nivel de agua del extremo",
            formula="coronacion >= nivel de agua + resguardo",
            obtenido=geometria.cota_coronacion,
            admisible=extremo.cota_agua + reglas["resguardo_agua_m"],
            mayor_o_igual=True,
            sustitucion=(
                Magnitud("nivel_agua", extremo.cota_agua, "msnm",
                         extremo.origen_cota_agua, cifras=CIFRAS_MAGNITUD),
                Magnitud("resguardo", reglas["resguardo_agua_m"], "m",
                         "regla 'resguardo_agua_m' de "
                         f"'{CRITERIO_GEOMETRIA}' [A]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("coronacion", geometria.cota_coronacion,
                               "msnm", "coronacion del cabezal",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="nivel de agua de diseño contra el muro mas "
                               "el resguardo",
            cita="HDS5_3ED.3.3.5#ENCAJE",
            aplicacion="REGLA DEL PROYECTO [A] (INFORME §4.2: «el agua no "
                       "desborda el muro»)",
            criterio=CRITERIO_GEOMETRIA)
    v.append(Verificacion(**kv, paso=paso("F9.CORONACION", **kp)))
    df_min = _desplante_minimo()
    kp, kv = _verificacion_cb(
            codigo="CB4", extremo=ext,
            que="Profundidad de desplante frente al minimo de E.050, por "
                "analogia",
            formula=f"D_f >= {df_min:.2f} m",
            obtenido=geometria.D_f, admisible=df_min,
            mayor_o_igual=True,
            sustitucion=(Magnitud("pie", extremo.cota_pie, "msnm",
                                  extremo.origen_cota_pie,
                                  cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("D_f", geometria.D_f, "m",
                               "profundidad de la base de la zapata bajo el "
                               "pie del muro", cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="profundidad minima de cimentacion",
            cita=CITA_PROFUNDIDAD_CIMENTACION,
            aplicacion=f"ANALOGIA [N→] ('{CRITERIO_DESPLANTE_MIN}'): E.050 es "
                       "una norma de edificaciones y el proyecto aplica su "
                       "minimo al cabezal vial porque la misma norma manda "
                       "que el muro de contencion cumpla su Capitulo IV "
                       "(39.13.7). Medida desde la superficie del terreno "
                       "(26.1). Sobre roca el PR puede bajarla: el programa "
                       "no tiene el dato y no lo supone",
            criterio=CRITERIO_DESPLANTE_MIN,
            numeral=_registro_t7a().cita(
                CITA_PROFUNDIDAD_CIMENTACION).como_texto() + ", por analogia")
    v.append(Verificacion(**kv, paso=paso("F9.DESPLANTE", **kp)))
    margen = None
    if extremo.cota_fondo_hoya is not None:
        margen = _margen_socavacion()
        lectura_margen = _lectura_del_margen(margen)
        kp, kv = _verificacion_cb(
            codigo="CB5", extremo=ext,
            que="Desplante frente al fondo de la hoya de socavacion",
            formula="cota de desplante <= fondo de la hoya - margen",
            obtenido=geometria.cota_desplante,
            admisible=extremo.cota_fondo_hoya - margen,
            mayor_o_igual=False,
            sustitucion=(
                Magnitud("fondo_hoya", extremo.cota_fondo_hoya, "msnm",
                         "Fase 6: " + extremo.origen_socavacion,
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("margen", margen, "m",
                         f"criterio '{CRITERIO_MARGEN_SOCAVACION}' [C]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("cota_desplante", geometria.cota_desplante,
                               "msnm", "base de la zapata del cabezal",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral=lectura_margen[1],
            cita=lectura_margen[0],
            aplicacion=lectura_margen[2],
            criterio=CRITERIO_MARGEN_SOCAVACION,
            citas=lectura_margen[3])
        v.append(Verificacion(**kv, paso=paso("F9.DESPLANTE", **kp)))
    # CB6: el espesor de la zapata contra el minimo de su tipo
    minimo_ez, texto_minimo, cita_minimo = peralte_minimo_zapata(geometria.tipo)
    kp, kv = _verificacion_cb(
        codigo="CB6", extremo=ext,
        que=f"Espesor de la zapata frente al minimo del cabezal de "
            f"{geometria.tipo}",
        formula="espesor de la zapata >= minimo del tipo",
        obtenido=geometria.espesor_zapata, admisible=minimo_ez,
        mayor_o_igual=True,
        sustitucion=(Magnitud("minimo", minimo_ez, "m", texto_minimo,
                              cifras=CIFRAS_MAGNITUD),),
        resultado=Magnitud("espesor_zapata", geometria.espesor_zapata, "m",
                           "espesor de la zapata del cabezal",
                           cifras=CIFRAS_MAGNITUD),
        descripcion_umbral=texto_minimo,
        cita=cita_minimo,
        aplicacion=(f"EXIGENCIA de E.060 para las zapatas de concreto simple "
                    "([N], la que la §9.4 de la hoja de ruta hace regir sobre "
                    "el ciclopeo)" if geometria.tipo == TIPO_GRAVEDAD else
                    f"ANALOGIA [N→] ('{CRITERIO_PERALTE_ZAPATA_ARMADA}'): "
                    "E.060 15.7 es de edificaciones y la Via 1 de la §0.2 "
                    "saca a E.060 del diseño armado; se aplica como minimo "
                    "del predimensionamiento, con el recubrimiento con que "
                    "se arma y la mayor barra del catalogo, de modo que la "
                    "fila A8 del armado lo cumple por construccion"),
        criterio=(CRITERIO_GEOMETRIA if geometria.tipo == TIPO_GRAVEDAD
                  else CRITERIO_PERALTE_ZAPATA_ARMADA),
        citas=((CITA_CICLOPEO_LIMITES,) if geometria.tipo == TIPO_GRAVEDAD
               else ("E060.7.7.1",)))
    v.append(Verificacion(**kv, paso=paso("F9.DIMENSIONES", **kp)))
    # --- VE-7 (abierto (d)) --- CB6 de la zapata de los aleros, si su
    # espesor se DECLARO: bajo el minimo de su tipo es NO CUMPLE, no error.
    al = geometria.aleros
    if al is not None and any(
            d.nombre == "espesor de la zapata de los aleros"
            and d.origen == ORIGEN_DIMENSION_DECLARADA
            for d in geometria.dimensiones):
        kp, kv = _verificacion_cb(
            codigo="CB6", extremo=ext,
            que=f"Espesor de la zapata de los aleros frente al minimo del "
                f"cabezal de {geometria.tipo}",
            formula="espesor de la zapata de los aleros >= minimo del tipo",
            obtenido=al.espesor_zapata, admisible=minimo_ez,
            mayor_o_igual=True,
            sustitucion=(Magnitud("minimo", minimo_ez, "m", texto_minimo,
                                  cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("espesor_zapata_aleros", al.espesor_zapata,
                               "m", "declarado (`cabezal_declarado."
                               f"{CAMPO_ESPESOR_ZAPATA_ALEROS}`)",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral=texto_minimo, cita=cita_minimo,
            aplicacion=("el mismo minimo de la zapata del cabezal, por ser "
                        "de su mismo tipo"),
            criterio=(CRITERIO_GEOMETRIA if geometria.tipo == TIPO_GRAVEDAD
                      else CRITERIO_PERALTE_ZAPATA_ARMADA))
        codigo_al = f"CB6.{ext[0]}.alero"
        kp["codigo"] = kv["codigo"] = codigo_al
        v.append(Verificacion(**kv, paso=paso("F9.DIMENSIONES", **kp)))
    # CB7: la base del dentellon contra el terreno y contra la hoya
    if geometria.losa is not None:
        lo = geometria.losa
        dentellon = ca.valor(CRITERIO_DENTELLON)
        prof_min = _exigir_positivo(CRITERIO_DENTELLON,
                                    dentellon.get("profundidad_min_m"),
                                    "profundidad minima del dentellon")
        por_terreno = lo.cota_terreno - prof_min
        sust = [Magnitud("terreno", lo.cota_terreno, "msnm",
                         extremo.origen_cota_pie, cifras=CIFRAS_MAGNITUD),
                Magnitud("profundidad_min", prof_min, "m",
                         f"criterio '{CRITERIO_DENTELLON}' [N→], Lamina Nº 04",
                         cifras=CIFRAS_MAGNITUD)]
        admisible, cita_dent = por_terreno, "MC_HHD.LAMINA_04#DENTELLON"
        descripcion = "terreno del pie menos la profundidad minima"
        citas_extra = ("AASHTO_LRFD_9.12.6.5#DENTELLON",)
        if extremo.cota_fondo_hoya is not None:
            por_hoya = extremo.cota_fondo_hoya - margen
            sust.append(Magnitud("fondo_hoya", extremo.cota_fondo_hoya,
                                 "msnm", "Fase 6: " + extremo.origen_socavacion,
                                 cifras=CIFRAS_MAGNITUD))
            sust.append(Magnitud("margen", margen, "m",
                                 f"criterio '{CRITERIO_MARGEN_SOCAVACION}' [C]",
                                 cifras=CIFRAS_MAGNITUD))
            if por_hoya < por_terreno:
                admisible, cita_dent = por_hoya, "AASHTO_LRFD_9.12.6.5#DENTELLON"
                descripcion = "fondo de la hoya menos el margen"
                citas_extra = ("MC_HHD.LAMINA_04#DENTELLON",
                               "AASHTO_LRFD_9.12.6.5#ZAPATAS")
        kp, kv = _verificacion_cb(
            codigo="CB7", extremo=ext,
            que="Base del dentellon de la losa frente al terreno y a la "
                "socavacion",
            formula=("cota de la base del dentellon <= min(terreno - "
                     "profundidad minima, fondo de la hoya - margen)"),
            obtenido=lo.cota_base_dentellon, admisible=admisible,
            mayor_o_igual=False, sustitucion=tuple(sust),
            resultado=Magnitud("base_dentellon", lo.cota_base_dentellon,
                               "msnm", "base del dentellon de la losa de "
                               "entrega", cifras=CIFRAS_MAGNITUD),
            descripcion_umbral=descripcion, cita=cita_dent,
            aplicacion=(
                "ANALOGIA [N→] con la cota «0.80 min.» del dentellon del "
                "aliviadero de la Lamina Nº 04, medida desde el terreno"
                if cita_dent == "MC_HHD.LAMINA_04#DENTELLON" else
                "EXIGENCIA de AASHTO 12.6.5 para la pantalla del dentellon "
                "(que baje bajo la socavacion maxima prevista, sin "
                "cuantificar cuanto), con el margen de "
                f"'{CRITERIO_MARGEN_SOCAVACION}' ({margen:.3f} m): lectura "
                "del proyecto, [C]"),
            criterio=(CRITERIO_DENTELLON
                      if cita_dent == "MC_HHD.LAMINA_04#DENTELLON"
                      else CRITERIO_MARGEN_SOCAVACION),
            citas=citas_extra)
        v.append(Verificacion(**kv, paso=paso("F9.LOSA", **kp)))
    return tuple(v)


def _registro_t7a():
    """El registro normativo, para leer el texto de una cita (perezoso)."""
    from src.normativa import registro as _registro
    return _registro.construir()


# ---------------------------------------------------------------------------
# La longitud entre cabezales (ficha T6-01)
# ---------------------------------------------------------------------------

def longitud_entre_cabezales(*, longitud, ancho_plataforma: float,
                             cota_relleno_entrada: float,
                             cota_relleno_salida: float
                             ) -> Tuple[Optional[float], str]:
    """
    La longitud del barril entre cabezales, m, MEDIDA ENTRE LAS CARAS
    INTERIORES (trasdos) DE LOS DOS MUROS, con el talud muriendo en el
    RELLENO que cada muro retiene, y la razon cuando no aplica (ficha
    T6-01).

        L_cab = [ancho + talud·(borde_e - rel_e + borde_s - rel_s)] / cos(esviaje)

    con `borde` la cota del borde de la plataforma en cada lado y `rel` la
    cota del relleno retenido por el cabezal de ese extremo: la coronacion
    MENOS EL BORDILLO, que por definicion sobresale del relleno (msnm,
    absolutas). Hasta las correcciones de T-7a (H6) el talud moria en la
    corona del bordillo, lo que acortaba la longitud en talud·bordillo por
    extremo (en A-01, 12.865 m en vez de 13.486 m). Es la formula de
    `M7.longitud_a_la_clave` con el relleno en lugar de la clave: el termino
    talud·S desaparece porque las dos cotas ya son absolutas. La longitud de
    METRADO del barril suma el espesor de los dos muros (`cabezal_del_punto`).

    La coronacion de SALIDA se fijo con la cota de salida de 7.B, que sale de
    la longitud aproximada; con la longitud entre cabezales el muro de salida
    queda mas cerca del eje de la via y la solera bajo el sube S·ΔL, con ΔL
    del orden de 2.5 a 3 m por extremo en el fixture: CENTIMETROS (1.6 cm en
    la salida de A-01 con S = 0.006). Se declara en vez de iterar.

    NO SUSTITUYE a la longitud del diseño (T6-01): la friccion, la caida y
    la cota de salida siguen con la aproximada. Solo con el metodo por
    extremo: con el terraplen simetrico la referencia es el terreno y no el
    conducto, y una longitud declarada no se recalcula.
    """
    if longitud is None:
        return None, ("la longitud del conducto se declaro (`longitud_m`): "
                      "no se recalcula")
    if longitud.metodo is not MetodoLongitud.POR_EXTREMO:
        return None, (f"metodo de longitud '{longitud.metodo.value}': la "
                      "referencia del talud es el terreno, no el cabezal")
    for nombre, x in (("cota_borde_entrada", longitud.cota_borde_entrada),
                      ("cota_borde_salida", longitud.cota_borde_salida),
                      ("talud", longitud.talud),
                      ("factor_esviaje", longitud.factor_esviaje)):
        _exigir_finito(nombre, x, "dato de la longitud por extremo de 7.B")
    proyeccion = longitud.talud * (
        (longitud.cota_borde_entrada - cota_relleno_entrada)
        + (longitud.cota_borde_salida - cota_relleno_salida))
    L = (ancho_plataforma + proyeccion) * longitud.factor_esviaje
    if not L > 0:
        raise LimiteNumericoError(
            "longitud_entre_cabezales", valor=L,
            motivo="el relleno que retienen los cabezales queda sobre el "
            "borde de la plataforma: el talud no llega a ellos y la longitud "
            "entre cabezales no existe (relleno a "
            f"{cota_relleno_entrada:.3f} y {cota_relleno_salida:.3f} msnm)")
    return L, ""


# ---------------------------------------------------------------------------
# Los pasos de memoria del cabezal de un extremo
# ---------------------------------------------------------------------------

# La nota comun de los pasos cuya formula es GEOMETRIA DEL PROYECTO (H9): la
# cita del fundamento sostiene por que se hace el paso, no la formula, y por
# eso `formula_cita_id` va vacio y el indice de formulas lo dice.
NOTA_FORMULA_DEL_PROYECTO = ("La formula es geometria del proyecto: ninguna "
                             "fuente de normas/ la escribe, y por eso el paso "
                             "no le atribuye una cita.")


def _pasos_del_extremo(*, geometria: GeometriaCabezal,
                       extremo: ExtremoDelConducto,
                       embocadura: EmbocaduraDelPunto,
                       talud: float) -> Tuple[PasoDeMemoria, ...]:
    """Los pasos 9.0.x de UN cabezal: coronacion, desplante, aleros, losa."""
    reglas = _reglas()
    ext = extremo.extremo
    e = ext[0]
    origen = {d.nombre: d.origen for d in geometria.dimensiones}
    pasos = [
        paso("F9.CORONACION", codigo=f"9.0.1{e}",
             que=f"Coronacion y altura del cabezal de {ext}",
             formula=("coronacion = max(clave exterior + recubrimiento + "
                      "bordillo, nivel de agua + resguardo);  H_c = "
                      "coronacion - desplante"),
             sustitucion=(
                 Magnitud("clave_exterior", extremo.cota_clave_exterior,
                          "msnm", "solera + altura interior + pared",
                          cifras=CIFRAS_MAGNITUD),
                 Magnitud("recubrimiento + bordillo",
                          reglas["recubrimiento_clave_m"] + reglas["bordillo_m"],
                          "m", f"reglas de '{CRITERIO_GEOMETRIA}' [A]",
                          cifras=CIFRAS_MAGNITUD),
                 Magnitud("nivel_agua", extremo.cota_agua, "msnm",
                          extremo.origen_cota_agua, cifras=CIFRAS_MAGNITUD),
                 Magnitud("resguardo", reglas["resguardo_agua_m"], "m",
                          f"regla de '{CRITERIO_GEOMETRIA}' [A]",
                          cifras=CIFRAS_MAGNITUD),
                 Magnitud("desplante", geometria.cota_desplante, "msnm",
                          "paso del desplante", cifras=CIFRAS_MAGNITUD)),
             resultado=Magnitud(
                 "H_c", geometria.altura_total, "m",
                 "altura total, base de zapata a corona: "
                 + origen.get("altura total del cabezal (H_c, base de "
                              "zapata a corona)", ORIGEN_DIMENSION_REGLA),
                 cifras=CIFRAS_MAGNITUD),
             nota_del_proyecto=(
                 f"Coronacion {geometria.cota_coronacion:.3f} msnm; relleno "
                 f"retenido a {geometria.cota_coronacion - reglas['bordillo_m']:.3f}"
                 " msnm (el bordillo sobresale de el); tipo "
                 f"{geometria.tipo} (gravedad en ciclopeo hasta "
                 f"{reglas['altura_max_gravedad_m']:g} m de altura TOTAL, "
                 "desplante incluido). El muro es normal al eje del "
                 "conducto y de trasdos vertical. Su estabilidad no se "
                 "verifica aqui (T-7b). " + NOTA_FORMULA_DEL_PROYECTO)),
    ]
    df_min = _desplante_minimo()
    sust_d = [Magnitud("pie", extremo.cota_pie, "msnm",
                       extremo.origen_cota_pie, cifras=CIFRAS_MAGNITUD),
              Magnitud("D_f_min", df_min, "m",
                       f"criterio '{CRITERIO_DESPLANTE_MIN}' [N→]: E.050 Art. "
                       "26.2 por analogia", cifras=CIFRAS_MAGNITUD)]
    if extremo.cota_fondo_hoya is not None:
        sust_d.append(Magnitud("fondo_hoya", extremo.cota_fondo_hoya, "msnm",
                               "Fase 6: " + extremo.origen_socavacion,
                               cifras=CIFRAS_MAGNITUD))
        sust_d.append(Magnitud("margen", _margen_socavacion(),
                               "m", f"criterio '{CRITERIO_MARGEN_SOCAVACION}' "
                               "[C]", cifras=CIFRAS_MAGNITUD))
        nota_d = ("La socavacion la entrega la Fase 6 (T-8) y se mide desde "
                  "la referencia de 'referencia_profundidad_socavacion'.")
    elif ext == EXTREMO_SALIDA:
        nota_d = ("SIN SOCAVACION ENTREGADA por la Fase 6 (el motivo va en los "
                  "avisos del punto). El desplante de salida queda con el "
                  "minimo de E.050, que no es el que AASHTO 10.6.1.2 pide en un "
                  "cauce que socava.")
    else:
        nota_d = ("En la entrada no se estima socavacion (HEC-14 Cap. 5 es "
                  "de la salida): rige el minimo de E.050.")
    pasos.append(paso(
        "F9.DESPLANTE", codigo=f"9.0.2{e}",
        que=f"Profundidad de desplante del cabezal de {ext}",
        formula=(f"D_f = max({df_min:.2f} m, pie - (fondo de la hoya - "
                 "margen));  desplante = pie - D_f"),
        formula_cita_id=CITA_PROFUNDIDAD_CIMENTACION,
        citas_textuales=(_lectura_del_margen(_margen_socavacion())[0],),
        sustitucion=tuple(sust_d),
        resultado=Magnitud(
            "D_f", geometria.D_f, "m",
            origen.get("profundidad de desplante (D_f)",
                       ORIGEN_DIMENSION_REGLA)
            + f"; desplante {geometria.cota_desplante:.3f} msnm",
            cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=nota_d))
    if geometria.aleros is not None:
        a = geometria.aleros
        pasos.append(paso(
            "F9.ALEROS", codigo=f"9.0.3{e}",
            que=f"Aleros del cabezal de {ext}",
            formula=("L_corto = (h0 - H_f)·talud / cos(alfa - theta);  "
                     "L_largo = (h0 - H_f)·talud / cos(alfa_largo + theta)"),
            citas_textuales=(CITA_CONVENCION_ALEROS,),
            sustitucion=(
                Magnitud("alfa", a.angulo_grados, "grados",
                         embocadura.regla + f" ('{CRITERIO_ANGULO_ALETAS}' [A]"
                         "), medido con la prolongacion de la pared del "
                         "barril (ΘW del HDS-5)", cifras=CIFRAS_MAGNITUD),
                Magnitud("alfa_largo", a.angulo_largo_grados, "grados",
                         ("declarado en `cabezal_declarado."
                          f"{CAMPO_ANGULO_ALERO_LARGO}` (aleros asimetricos)"
                          if abs(a.angulo_largo_grados - a.angulo_grados)
                          > TOL_UMBRAL_NORMATIVO
                          else "el mismo alfa: ninguno declarado de ese lado"),
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("theta", a.esviaje_grados, "grados",
                         "esviaje del cruce (columna esviaje_grados): el "
                         "angulo del eje con la bajada del talud, que es "
                         "perpendicular a la via", cifras=CIFRAS_MAGNITUD),
                Magnitud("h0", a.altura_inicial, "m",
                         "coronacion - pie: la altura del cabezal en el "
                         "arranque, bordillo incluido", cifras=CIFRAS_MAGNITUD),
                Magnitud("H_f", a.altura_final, "m",
                         origen.get("altura final de los aleros (H_f)",
                                    ORIGEN_DIMENSION_REGLA),
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("talud", talud, "H:V",
                         "talud del terraplen (el de 7.B o "
                         f"'{CRITERIO_TALUD_TERRAPLEN}')",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "L_corto / L_largo",
                f"{a.longitud_corto:.3f} / {a.longitud_largo:.3f}", "m",
                origen.get("longitud del alero largo (alfa + theta)",
                           ORIGEN_DIMENSION_REGLA)),
            nota_del_proyecto=(
                "El talud baja perpendicular a la via y el cabezal es normal "
                "al eje del conducto: con esviaje, un alero forma alfa - "
                "theta con la bajada del talud y el otro alfa + theta, y no "
                "miden lo mismo. El CSV da la magnitud del esviaje y no su "
                "sentido: cual lado es el largo lo fija la planta del cruce. "
                "El cabezal se supone normal al eje del conducto (lo que "
                "supone la hidraulica del HDS-5); el alero largo se puede "
                "acortar declarando un alfa menor de ese lado en "
                f"`cabezal_declarado` (`{CAMPO_ANGULO_ALERO_LARGO}`): aleros "
                "asimetricos. "
                "h0 y H_f se miden igual (alturas del alero sobre el pie, con "
                "su bordillo), de modo que h0 - H_f es la caida del talud; "
                "medir H_f sobre el talud acortaria los aleros. El encargo "
                "escribia el seno con alfa medido desde el eje, que solo "
                "coincide con esto a 45 grados y sin esviaje (ficha T7A-03). "
                + NOTA_FORMULA_DEL_PROYECTO)))
    if geometria.losa is not None:
        lo = geometria.losa
        pasos.append(paso(
            "F9.LOSA", codigo=f"9.0.4{e}",
            que=f"Losa de entrega y dentellon del cabezal de {ext}",
            formula=("L_losa = fraccion·D;  base del dentellon = min(terreno "
                     "- profundidad minima, fondo de la hoya - margen)"),
            citas_textuales=("MC_HHD.LAMINA_04#DENTELLON",
                             "AASHTO_LRFD_9.12.6.5#DENTELLON"),
            sustitucion=(
                # --- VE-7 (lote A, A10; ficha VE5GUI-46) --- con los
                # decimales del rotulo de la seccion, no tres fijos.
                Magnitud("D", extremo.altura_interior, "m",
                         "altura interior de la seccion adoptada",
                         cifras=cifras_de_dimension(extremo.altura_interior)),
                Magnitud("terreno", lo.cota_terreno, "msnm",
                         "el pie del muro de este extremo, la misma "
                         "referencia del desplante", cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "profundidad del dentellon", lo.profundidad_dentellon, "m",
                origen.get("profundidad del dentellon (desde el terreno del "
                           "pie)", ORIGEN_DIMENSION_REGLA)
                + f"; base a {lo.cota_base_dentellon:.3f} msnm; losa "
                f"{lo.longitud:.2f} x {lo.espesor:.2f} m",
                cifras=CIFRAS_MAGNITUD),
            nota_del_proyecto=(
                "Geometria declarada (ficha T8-03): su verificacion "
                "hidraulica es de la Fase 6. La profundidad del dentellon se "
                "mide desde el TERRENO al borde de la losa, como la cota "
                "«0.80 min.» de la Lamina Nº 04 (de un aliviadero, aplicada "
                "por analogia, [N→]), y no desde la cara superior de la "
                "losa. " + NOTA_FORMULA_DEL_PROYECTO)))
    return tuple(pasos)


def _paso_embocadura(embocadura: EmbocaduraDelPunto,
                     es_marco: bool,
                     coherencia: Optional[str] = None) -> PasoDeMemoria:
    if embocadura.angulo_aletas is None:
        res = "cabezal recto, sin aleros"
    else:
        res = (f"aleros a {embocadura.angulo_aletas:g} grados con la pared "
               "del barril")
    if es_marco:
        hds5 = ("En un MARCO la embocadura elige la banda de filas de las "
                "Tablas A.1 y C.2 que 'embocadura_cajon' y 'ke_entrada_cajon' "
                "tienen que respetar; la coherencia se comprueba antes de la "
                "Fase 4" + (f" ({coherencia})." if coherencia else "."))
    else:
        hds5 = ("En un TUBO el angulo de los aleros no mueve ke ni la carta: "
                "la Tabla C.2 pone el tubo con cabezal y con cabezal y aleros "
                "en la misma fila («Headwall or headwall and wingwalls», "
                "0.5) y las Cartas 1 a 3 no separan aleros.")
    return paso(
        "F9.EMBOCADURA", codigo="9.0.0",
        que="Embocadura del punto",
        formula=("alfa = por defecto, salvo esviaje > umbral; tipo = "
                 "'embocadura_cabezal'"),
        sustitucion=(
            Magnitud("tipo", embocadura.tipo, "",
                     f"criterio '{embocadura.criterio_tipo}' [A]"),
            Magnitud("esviaje", embocadura.esviaje_grados, "grados",
                     "columna esviaje_grados del CSV",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("embocadura", res, "", embocadura.regla),
        nota_del_proyecto=hds5)


# ---------------------------------------------------------------------------
# La Fase 9 de UN punto
# ---------------------------------------------------------------------------

def _motivo_sin_socavacion(socavacion, motivo_externo: str) -> str:
    """
    Por que el cabezal de salida no tiene hoya (H9): lo que la Fase 6 dijo,
    y no siempre «falta el lecho». Sin objeto de socavacion, la etapa de la
    Fase 6 se bloqueo (o no corrio) y el motivo lo trae el servicio.
    """
    if socavacion is None:
        return (motivo_externo or
                "la Fase 6 no entrego la socavacion a la salida")
    if socavacion.profundidad_para_desplante is None:
        return (socavacion.motivo_no_estimada or
                "la Fase 6 no estimo la hoya ni hay una declarada")
    return ("la Fase 6 dio la profundidad pero no la cota del fondo de la "
            "hoya (faltan la cota del receptor o la de la solera de salida)")


def cabezal_del_punto(*, punto, resultado, geometria, embocadura,
                      socavacion=None,
                      declarados: Optional[dict] = None,
                      coherencia_embocadura: Optional[str] = None,
                      motivo_sin_socavacion: str = "",
                      anchos_por_estabilidad: Optional[dict] = None,
                      espesores_por_armado: Optional[dict] = None,
                      puntas_por_estabilidad: Optional[dict] = None,
                      pantallas_por_armado: Optional[dict] = None,
                      aleros_por_armado: Optional[dict] = None
                      ) -> CabezalDelPunto:
    """
    Los dos cabezales de un punto DIMENSIONADO, con sus aleros, su losa, sus
    verificaciones de compatibilidad (CB1 a CB7), la longitud entre
    cabezales y la de metrado, sus pasos y sus avisos (T-7a, INF-4.1 a
    INF-4.3, INF-5.1.15).

    `declarados` es lo que el punto trae en `cabezal_declarado`, ya
    normalizado por `validar_cabezal_declarado`: {"entrada": {...},
    "salida": {...}}; cada dimension declarada gana sobre su regla.

    Usa el talud de 7.B si la longitud se calculo por extremo y, si no, el
    criterio 'talud_terraplen' -- el mismo que 7.B leeria --: los aleros
    siguen al talud del terraplen sea cual sea el metodo de longitud.

    LOS AVISOS (por `InformePunto.avisos()`): el desplante de salida sin
    socavacion, con SU motivo (`motivo_sin_socavacion` lo trae el servicio
    cuando la etapa de la Fase 6 se bloqueo); el desnivel del talud a lo
    largo de un muro normal al eje cuando hay esviaje, Δz = L_c·sen(theta)/
    talud (H1); y la regla del tipo por altura total, que con altura interior
    >= 0.90 m no alcanza nunca la rama de gravedad (H7).
    """
    declarados = declarados or {}
    entrada, salida = extremos_del_conducto(
        punto=punto, resultado=resultado, geometria=geometria,
        socavacion=socavacion)
    calculada = geometria.longitud_calculada
    talud = (calculada.talud if calculada is not None
             and calculada.talud is not None
             else ca.valor(CRITERIO_TALUD_TERRAPLEN))
    reglas = _reglas()
    geometrias = []
    verificaciones = []
    tipos_por_regla = []
    pasos = [_paso_embocadura(
        embocadura, resultado.material.forma is FormaSeccion.RECTANGULAR,
        coherencia_embocadura)]
    for extremo in (entrada, salida):
        propias = dict(declarados.get(extremo.extremo, {}))
        tipo = propias.pop(CAMPO_TIPO_DECLARADO, None)
        g = predimensionar_cabezal(
            extremo=extremo, embocadura=embocadura, talud=talud,
            declaradas=propias, tipo_declarado=tipo, id_punto=punto.id,
            ancho_por_estabilidad=(anchos_por_estabilidad or {}).get(
                extremo.extremo),
            espesor_por_armado=(espesores_por_armado or {}).get(
                extremo.extremo),
            punta_por_estabilidad=(puntas_por_estabilidad or {}).get(
                extremo.extremo),
            pantalla_por_armado=(pantallas_por_armado or {}).get(
                extremo.extremo),
            alero_por_armado=(aleros_por_armado or {}).get(extremo.extremo))
        geometrias.append(g)
        if tipo is None:
            tipos_por_regla.append(g)
        verificaciones.extend(verificar_compatibilidad_cabezal(
            geometria=g, extremo=extremo, embocadura=embocadura))
        pasos.extend(_pasos_del_extremo(geometria=g, extremo=extremo,
                                        embocadura=embocadura, talud=talud))
    bordillo = reglas["bordillo_m"]
    L, motivo = longitud_entre_cabezales(
        longitud=calculada, ancho_plataforma=punto.ancho_plataforma,
        cota_relleno_entrada=geometrias[0].cota_coronacion - bordillo,
        cota_relleno_salida=geometrias[1].cota_coronacion - bordillo)
    L_metrado = None
    if L is not None:
        L_metrado = (L + geometrias[0].espesor_base_muro
                     + geometrias[1].espesor_base_muro)
        pasos.append(paso(
            "F9.LONGITUD", codigo="9.0.5",
            que="Longitud entre cabezales y longitud de metrado del barril",
            formula=("L_cab = [ancho + talud·(borde_e - rel_e + borde_s - "
                     "rel_s)] / cos(esviaje), rel = coronacion - bordillo;  "
                     "L_metrado = L_cab + e_e + e_s"),
            sustitucion=(
                Magnitud("rel_e", geometrias[0].cota_coronacion - bordillo,
                         "msnm", "relleno retenido por el cabezal de entrada "
                         "(coronacion de 9.0.1e - bordillo)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("rel_s", geometrias[1].cota_coronacion - bordillo,
                         "msnm", "relleno retenido por el cabezal de salida "
                         "(coronacion de 9.0.1s - bordillo)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("e_e + e_s", geometrias[0].espesor_base_muro
                         + geometrias[1].espesor_base_muro, "m",
                         "espesor de los dos muros sobre el eje (normales a "
                         "el)", cifras=CIFRAS_MAGNITUD),
                Magnitud("L", calculada.longitud, "m",
                         "longitud aproximada de 7.B, la del diseño",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "L_cab / L_metrado", f"{L:.3f} / {L_metrado:.3f}", "m",
                "entre las caras interiores (trasdos) de los dos muros / "
                "barril completo, que atraviesa los dos muros"),
            nota_del_proyecto=(
                "El talud muere en el RELLENO que cada muro retiene "
                "(coronacion menos bordillo), contra su cara interior: L_cab "
                "se mide entre los trasdos. El barril atraviesa ademas los "
                "dos muros, normales al eje, y su longitud de metrado suma "
                f"sus espesores. L_cab es {calculada.longitud - L:.3f} m "
                "menor que la aproximada con que corrio el diseño hidraulico, "
                "que NO se sustituye (ficha T6-01): la friccion, la caida y "
                "la cota de salida siguen con la aproximada. Para que el "
                "control de salida use esta, declarar `longitud_m` por "
                "punto. " + NOTA_FORMULA_DEL_PROYECTO)))
    avisos = []
    if salida.cota_fondo_hoya is None:
        avisos.append(
            f"Cabezal de salida de {punto.id}: desplante sin socavacion "
            "entregada por la Fase 6 ("
            + _motivo_sin_socavacion(socavacion, motivo_sin_socavacion)
            + "); rige solo el minimo de "
            f"{_desplante_minimo():.2f} m de E.050 Art. 26.2 (por "
            "analogia), no el de AASHTO 10.6.1.2 bajo la socavacion")
    theta = embocadura.esviaje_grados
    if theta > TOL_UMBRAL_NORMATIVO and not es_paralelo_a_la_via(embocadura):
        seno = math.sin(math.radians(theta))
        partes = ", ".join(
            f"{g.extremo}: {g.longitud:.2f}·{seno:.3f}/{talud:g} = "
            f"{g.longitud * seno / talud:.3f} m" for g in geometrias)
        avisos.append(
            f"Cabezales de {punto.id}: el muro es NORMAL al eje del conducto "
            f"y el cruce tiene un esviaje de {theta:g} grados, de modo que el "
            "talud (que baja perpendicular a la via) queda a cotas distintas "
            "en los dos extremos de cada muro, Δz = L_c·sen(theta)/talud ("
            + partes + "): la corona horizontal no sigue al talud en toda su "
            f"longitud y, con el relleno al nivel de diseño en el eje, un "
            f"extremo queda Δz/2 por encima (bordillo de {bordillo:.2f} m). "
            "Los dos aleros de cada cabezal miden distinto (paso 9.0.3): el "
            f"largo se acorta declarando un alfa menor de ese lado en "
            f"`cabezal_declarado` (`{CAMPO_ANGULO_ALERO_LARGO}`, aleros "
            "asimetricos). El cabezal normal al eje es el de archivo en las "
            "tres familias; el paralelo a la via, solo para el marco, sale "
            "declarando en 'embocadura_cajon' una fila de la Carta 11 del "
            "HDS-5 (ficha T7A-03)")
    asimetricos = [g for g in geometrias if g.aleros is not None
                   and abs(g.aleros.angulo_largo_grados - g.aleros.angulo_grados)
                   > TOL_UMBRAL_NORMATIVO]
    if asimetricos and resultado.material.forma is FormaSeccion.RECTANGULAR:
        avisos.append(
            f"Cabezales de {punto.id}: aleros asimetricos declarados ("
            + ", ".join(f"{g.extremo}: {g.aleros.angulo_grados:g} / "
                        f"{g.aleros.angulo_largo_grados:g} grados"
                        for g in asimetricos)
            + "). Las filas de las Tablas A.1 y C.2 del HDS-5 nombran un solo "
            "angulo de aleros por embocadura: el ke y la carta del marco "
            "siguen siendo los del angulo de la regla, "
            f"{embocadura.angulo_aletas:g} grados")
    # --- correcciones de T-7b (H9) --- ALEROS DESPROPORCIONADOS. La guardia
    # de `predimensionar_aleros` solo cubre la singularidad (alfa + theta >=
    # 90); cerca de ella el alero largo crece sin cota (12 m con theta = 50 y
    # alfa = 30; decenas de metros cerca de 59). Sin umbral nuevo: se compara
    # con una magnitud que ya existe, la longitud entre cabezales. Un alero
    # mas largo que el conducto que encauza no es un alero.
    if L is not None:
        largos = [g for g in geometrias if g.aleros is not None
                  and g.aleros.longitud_largo > L + TOL_UMBRAL_NORMATIVO]
        if largos:
            avisos.append(
                f"Cabezales de {punto.id}: el alero largo "
                + ", ".join(f"del cabezal de {g.extremo} mide "
                            f"{g.aleros.longitud_largo:.2f} m (alfa + theta "
                            f"= {g.aleros.angulo_largo_grados + theta:g} "
                            "grados)" for g in largos)
                + f", MAS que la longitud entre cabezales ({L:.2f} m): con "
                "alfa + theta cerca de 90 grados el alero largo crece sin "
                "cota y queda desproporcionado. Declarar un alfa menor de "
                f"ese lado (`cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}`, "
                "aleros asimetricos) o la longitud de los aleros")
    if tipos_por_regla and all(g.tipo == TIPO_VOLADIZO for g in tipos_por_regla):
        avisos.append(
            f"Cabezales de {punto.id}: tipo voladizo armado por la regla de "
            f"'{CRITERIO_GEOMETRIA}' (gravedad en ciclopeo hasta "
            f"{reglas['altura_max_gravedad_m']:g} m), que se mide sobre la "
            "altura TOTAL, desplante incluido (H_c = "
            + " / ".join(f"{g.altura_total:.2f}" for g in tipos_por_regla)
            + " m): con altura interior de 0.90 m o mas ningun cabezal de la "
            "obra alcanza la rama de gravedad con el umbral de archivo "
            "(ficha T7A-04)")
    gravedad = [g for g in geometrias if g.tipo == TIPO_GRAVEDAD]
    if gravedad:
        avisos.append(
            f"Cabezales de {punto.id}: "
            + ", ".join(f"el de {g.extremo}" for g in gravedad)
            + " sale de gravedad en concreto ciclopeo: E.060 22.10.2.1 limita "
            "ese concreto a los muros de contencion de GRAVEDAD y el "
            "22.10.2.2 exige verificar flexion y corte en voladizos mas "
            "largos que la mitad de su peralte (pag. 195): el cabezal no "
            "se arma, se verifica como concreto ciclopeo (filas C1 a C8 del "
            "armado; su zapata, como voladizo en C7)")
    # Las CB incumplidas NO son avisos: son verificaciones, y salen por
    # `InformePunto.incumplidas` (un aviso repetido se cuenta dos veces).
    return CabezalDelPunto(
        id_punto=punto.id, embocadura=embocadura, entrada=geometrias[0],
        salida=geometrias[1], verificaciones=tuple(verificaciones),
        longitud_entre_cabezales=L, longitud_metrado=L_metrado,
        motivo_sin_longitud=motivo, pasos=tuple(pasos), avisos=tuple(avisos))


# ---------------------------------------------------------------------------
# La puerta del dato externo `cabezal_declarado`
# ---------------------------------------------------------------------------

# --- VE-6 (lote M9, item 28; fichas T7B-11 y VE6M9-04) --- LA ORIENTACION
# DEL MURO FRENTE AL TRAFICO Y LA DISTANCIA DEL BORDE DE CALZADA AL TRASDOS,
# POR PUNTO. Dos claves de `--datos-externos` (por punto o en `globales`),
# fuera de `CLAVES_EXTERNAS` como `cabezal_declarado`: sin ellas rige el [S]
# de corredor. El valor vale para los dos cabezales o va por extremo.
CAMPO_ORIENTACION_DEL_PUNTO = "orientacion_muro_del_punto"


CAMPO_DISTANCIA_BORDE_DEL_PUNTO = "distancia_borde_calzada_del_punto_m"


CAMPOS_DE_SOBRECARGA_DEL_PUNTO = (CAMPO_ORIENTACION_DEL_PUNTO,
                                  CAMPO_DISTANCIA_BORDE_DEL_PUNTO)


def validar_sobrecarga_del_punto(clave: str, valor: Any, *,
                                 id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de una de las dos claves de la sobrecarga viva del
    punto, normalizada a {"entrada": v | None, "salida": v | None}:

      orientacion_muro_del_punto           una de ORIENTACIONES_TABULADAS
                                           (las dos que AASHTO 3.11.6.4
                                           tabula; no hay «oblicuo»)
      distancia_borde_calzada_del_punto_m  m, finita y no negativa (0 es la
                                           columna «0.0 ft» de la tabla)

    El valor es uno solo (los dos cabezales) o un objeto con "entrada" y/o
    "salida". Un texto en la distancia, un bool, un negativo, una clave
    desconocida o un objeto vacio se rechazan.
    """
    if clave not in CAMPOS_DE_SOBRECARGA_DEL_PUNTO:
        raise DatoInvalidoError(
            clave, valor=valor, id_punto=id_punto,
            motivo="no es una clave de la sobrecarga del punto: "
                   + ", ".join(CAMPOS_DE_SOBRECARGA_DEL_PUNTO))

    def _uno(x, donde):
        if clave == CAMPO_ORIENTACION_DEL_PUNTO:
            if not isinstance(x, str) or x not in ORIENTACIONES_TABULADAS:
                raise DatoInvalidoError(
                    f"{clave}{donde}", valor=x, id_punto=id_punto,
                    motivo="se espera una de las dos que AASHTO 3.11.6.4 "
                           "tabula: " + ", ".join(ORIENTACIONES_TABULADAS)
                           + " (no hay tabla para el muro oblicuo)")
            return x
        if isinstance(x, bool) or not (_finito(x) and x >= 0):
            raise DatoInvalidoError(
                f"{clave}{donde}", valor=x, id_punto=id_punto,
                motivo="se espera una distancia en m, finita y no negativa")
        return float(x)

    if isinstance(valor, dict):
        if not valor or set(valor) - set(EXTREMOS):
            raise DatoInvalidoError(
                clave, valor=valor, id_punto=id_punto,
                motivo="se espera un valor o un objeto con 'entrada' y/o "
                       "'salida'")
        return {e: (_uno(valor[e], f".{e}") if e in valor else None)
                for e in EXTREMOS}
    limpio = _uno(valor, "")
    return {e: limpio for e in EXTREMOS}


def avisos_de_la_sobrecarga_del_punto(entorno: EntornoDelCabezal
                                      ) -> List[str]:
    """
    --- dictamen Fable de VE-6 --- Lo que la sobrecarga del cabezal no puede
    leer de su tabla y la corrida tiene que decir:

      - el cruce tiene esviaje y el punto no declara su orientacion: rige
        la de corredor (AASHTO no tabula el muro oblicuo y el programa no
        deduce nada del esviaje);
      - el punto declara la distancia al borde y la orientacion vigente es
        la perpendicular: la Tabla 3.11.6.4-1 no tiene columna de distancia,
        y la declarada no se usa.
    """
    g = entorno.geometria
    quien = f"Cabezal de {entorno.extremo} de {entorno.id_punto}"
    avisos = []
    if (g.orientacion_trafico is None and _finito(entorno.esviaje_grados)
            and abs(entorno.esviaje_grados) > TOL_UMBRAL_NORMATIVO):
        avisos.append(
            f"{quien}: el cruce tiene esviaje ({entorno.esviaje_grados:g} "
            "grados) y el punto no declara "
            f"`{CAMPO_ORIENTACION_DEL_PUNTO}`: rige la orientacion de "
            "corredor ('orientacion_muro_respecto_al_trafico'). AASHTO "
            "3.11.6.4 no tiene tabla para el muro oblicuo y el programa no la "
            "deduce del esviaje")
    if envolvente_de_h_eq_paralelo(entorno):
        avisos.append(
            f"{quien}: el cabezal es PARALELO A LA VIA (fila de la Carta 11) "
            "y por tanto paralelo al trafico, pero la orientacion vigente es "
            "la perpendicular del corredor y el punto no declara otra: h_eq "
            "se toma como la MAYOR de las dos tablas de AASHTO 3.11.6.4"
            + ("" if g.distancia_borde_calzada_m is not None else
               " (la de muro paralelo con la columna «0.0 ft», la mayor)")
            + ". Declarar `" + CAMPO_ORIENTACION_DEL_PUNTO + "` = "
            f"'{ORIENTACION_PARALELO_AL_TRAFICO}' y `"
            + CAMPO_DISTANCIA_BORDE_DEL_PUNTO + "` para leer la tabla que "
            "corresponde (ficha VE7A-07)")
        return avisos
    if g.distancia_borde_calzada_m is not None:
        vigente = g.orientacion_trafico
        if vigente is None:
            try:
                vigente = ds.valor("orientacion_muro_respecto_al_trafico")
            except CriterioPendienteError:
                vigente = None      # el ensamble ya se detuvo por el corredor
        if vigente == ORIENTACION_PERPENDICULAR_AL_TRAFICO:
            avisos.append(
                f"{quien}: `{CAMPO_DISTANCIA_BORDE_DEL_PUNTO}` = "
                f"{g.distancia_borde_calzada_m:g} m declarada, pero la "
                "orientacion vigente es perpendicular al trafico: la Tabla "
                "3.11.6.4-1 no tiene columna de distancia y el dato no se usa")
    return avisos


def _texto_de_la_sobrecarga(g: GeometriaCabezal,
                            envolvente: bool = False) -> str:
    """De donde salen la orientacion y la distancia de ESTE cabezal."""
    if envolvente:
        return ("cabezal PARALELO A LA VIA (Carta 11): el muro es paralelo al "
                "trafico y el corredor dice perpendicular, sin orientacion "
                "del punto: la MAYOR de las Tablas 3.11.6.4-1 y -2 (esta, con "
                + (f"el borde a {g.distancia_borde_calzada_m:g} m, declarado "
                   "por punto" if g.distancia_borde_calzada_m is not None
                   else "la columna «0.0 ft», la mayor")
                + "; ficha VE7A-07)")
    if g.orientacion_trafico is not None:
        texto = (f"'{g.orientacion_trafico}', declarada por punto "
                 f"(`{CAMPO_ORIENTACION_DEL_PUNTO}`)")
    else:
        texto = ("[S] 'orientacion_muro_respecto_al_trafico' = "
                 f"'{ds.valor('orientacion_muro_respecto_al_trafico')}', de "
                 "corredor")
    if g.distancia_borde_calzada_m is not None:
        texto += (f"; borde de calzada a {g.distancia_borde_calzada_m:g} m "
                  "del trasdos, declarada por punto "
                  f"(`{CAMPO_DISTANCIA_BORDE_DEL_PUNTO}`)")
    return texto


def validar_cabezal_declarado(valor: Any, *,
                              id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de `cabezal_declarado` (dato externo opcional, por punto
    o global), y su forma normalizada: {"entrada": {...}, "salida": {...}}.

    Admite las dimensiones de `DIMENSIONES_DECLARABLES` en m (finitas y
    mayores que cero, y no mayores que `dominios.DIMENSION_CABEZAL_MAX_M`),
    el angulo del alero largo (`ANGULOS_DECLARABLES`, en [0, 90) grados) y
    `tipo` (uno de `TIPOS_DE_CABEZAL`), en el nivel superior -- valen para
    los dos extremos -- o dentro de "entrada" / "salida", que ganan sobre el
    nivel superior. Una clave desconocida, un texto, un bool, un cero o un
    negativo se rechazan: un valor por defecto silencioso o una errata
    ignorada son el defecto que esta puerta existe para cerrar.
    """
    from src.dominios import DIMENSION_CABEZAL_MAX_M
    if not isinstance(valor, dict) or not valor:
        raise DatoInvalidoError(
            "cabezal_declarado", valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con dimensiones del cabezal (y "
                   "opcionalmente 'entrada' / 'salida')")
    comunes = {k: v for k, v in valor.items() if k not in EXTREMOS}
    salida_norm = {}

    def _uno(bloque: dict, donde: str) -> dict:
        if not isinstance(bloque, dict):
            raise DatoInvalidoError(
                f"cabezal_declarado.{donde}", valor=bloque, id_punto=id_punto,
                motivo="se espera un objeto de dimensiones")
        limpio = {}
        for k, x in bloque.items():
            if k == CAMPO_TIPO_DECLARADO:
                if x not in TIPOS_DE_CABEZAL:
                    raise DatoInvalidoError(
                        f"cabezal_declarado.{donde}.tipo", valor=x,
                        id_punto=id_punto,
                        motivo="se espera " + " o ".join(TIPOS_DE_CABEZAL))
                limpio[k] = x
                continue
            if k in ANGULOS_DECLARABLES:
                limpio[k] = _exigir_angulo(f"cabezal_declarado.{donde}.{k}",
                                           x, "angulo declarado de los aleros",
                                           id_punto)
                continue
            if k not in DIMENSIONES_DECLARABLES:
                raise DatoInvalidoError(
                    f"cabezal_declarado.{donde}", valor=k, id_punto=id_punto,
                    motivo="no es una dimension declarable del cabezal: "
                           + ", ".join(DIMENSIONES_DECLARABLES
                                       + ANGULOS_DECLARABLES))
            if not (_finito(x) and 0 < x <= DIMENSION_CABEZAL_MAX_M):
                raise DatoInvalidoError(
                    f"cabezal_declarado.{donde}.{k}", valor=x,
                    id_punto=id_punto,
                    motivo="se espera un numero finito, mayor que cero y no "
                           f"mayor que {DIMENSION_CABEZAL_MAX_M:g} m")
            limpio[k] = float(x)
        return limpio

    base = _uno(comunes, "comun") if comunes else {}
    for extremo in EXTREMOS:
        propio = _uno(valor[extremo], extremo) if extremo in valor else {}
        fusion = dict(base)
        fusion.update(propio)
        salida_norm[extremo] = fusion
    if not any(salida_norm.values()):
        raise DatoInvalidoError(
            "cabezal_declarado", valor=valor, id_punto=id_punto,
            motivo="el objeto no declara ninguna dimension")
    return salida_norm
