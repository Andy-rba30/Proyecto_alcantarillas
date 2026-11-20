"""
M12_metrados.py
===============
Fase 11 de la hoja de ruta v8, entregables 8 y 9 (VE-5, lote «met», item 8
del censo de pendientes):

    8. Especificaciones y METRADOS referidos a EG-2013: los conductos (Sec.
       505 a 508), los cabezales (503 y 504), su excavacion (501), el
       enrocado de salida y el geotextil bajo el (511).
    9. CUADRO DE COMPATIBILIDAD RASANTE-ALCANTARILLA: la salida de 7.A.

LO QUE ESTE MODULO NO HACE, Y ES LA REGLA QUE LO SOSTIENE: no vuelve a
diseñar. Lee las geometrias FINALES que las fases anteriores ya entregaron
--la seccion adoptada (Fase 4), las cotas de 7.B, la longitud de metrado
del barril y la geometria de los dos cabezales con su armado (Fase 9), la
proteccion de salida (Fase 6)-- y las MIDE con la regla de medicion de la
Seccion del EG-2013 que les toca. Cada renglon sale con su `PasoDeMemoria`
(la regla, la sustitucion con la procedencia de cada dimension y el
resultado), y M11 y la CLI solo lo formatean.

Las reglas de medicion que se aplican, con su cita del registro:

    conducto     m, entre las caras exteriores de los cabezales, a lo largo
                 del eje y siguiendo la pendiente (506.14, 507.12, 508.11);
                 el marco vaciado en sitio, m3 de concreto (503.12)
    excavacion   m3 en su posicion original, dentro de las lineas del
                 proyecto y con caras verticales (501.09): la zanja de un
                 tubo con el ancho de su Seccion (506.06, 507.05, 508.04) y
                 el fondo bajo el solado o la cama minima (506.07, 508.05);
                 las zapatas con sus dimensiones mas el sobreancho de
                 encofrado, hasta 45 cm (501.04); clasificada por material y
                 nivel freatico (501.01)
    concreto     m3 de mezcla colocada, con el vano del conducto descontado
                 (503.12); la clase de la Tabla 503-07
    acero        kg, por las barras propuestas y los pesos de la Tabla
                 504-01 (504.10), mas lo que agreguen anclajes y empalmes
                 (criterio [A] 'incremento_acero_por_despiece')
    enrocado     m3, con el apron de HEC-14 (3D en la boca, abocinado 1:3);
                 sin partida en el EG-2013 (603.10 mide defensas riberenas
                 por metro lineal)
    geotextil    m2, el area en planta del enrocado, traslapes incluidos
                 (511.13)

Ningun factor de desperdicio ni de esponjamiento: el EG-2013 mide la
excavacion en su posicion original y el concreto colocado, y pone el
desperdicio en el precio (503.13, 504.11).

CONVENCIONES GEOMETRICAS DEL METRADO, dichas porque la Fase 9 no las fija y
el metrado las necesita (cada paso las repite en su nota):

    * el eje x corre a lo largo del conducto desde la cara exterior del muro
      de entrada; el terreno y el fondo del conducto varian linealmente
      entre los pies de los dos cabezales;
    * la zanja del conducto corre entre los bordes de los TALONES de las dos
      zapatas: bajo el talon la excavacion es la de la zapata;
    * los aleros se miden a lo largo de su longitud desde el extremo del
      cabezal, sin descontar el encuentro de las zapatas en la esquina;
    * la losa de entrega ocupa el espacio entre los aleros: su ancho es la
      longitud del cabezal mas lo que cada alero se abre (L·sen alfa, con
      alfa medido desde la pared del barril) hasta la longitud de la losa;
      el dentellon corre a lo ancho de su borde libre.
"""

from __future__ import annotations

import math
from collections import OrderedDict
from typing import Dict, List, Optional, Sequence, Tuple

from src import criterios_adoptados as ca
from src.constantes_normativas import (
    ANCHO_ZANJA_EG2013, CITA_LONGITUD_TUBERIA_EG2013, CITA_PESO_BARRA_EG2013,
    CLASE_CONCRETO_CICLOPEO_EG2013, CLASES_CONCRETO_EG2013_MPA,
    CLASES_CONCRETO_REFORZADO_EG2013, ESPESOR_MIN_CAMA_EG2013_M,
    HEC14_APRON_ABOCINADO_POR_LONGITUD, HEC14_APRON_ANCHO_EN_LA_BOCA_EN_D,
    PARTIDA_ACERO_EG2013, PARTIDA_CONCRETO_EG2013, PARTIDA_EXCAVACION_EG2013,
    PARTIDA_GEOTEXTIL_EG2013, PARTIDA_TUBERIA_EG2013, PESO_BARRA_KG_M_EG2013,
    REGLA_ZANJA_EXTERIOR_MAS, SIMBOLOS_SUCS,
    SIN_PARTIDA_ENROCADO_SALIDA_EG2013, UNIDAD_KG, UNIDAD_M, UNIDAD_M2,
    UNIDAD_M3)
from src.dominios import MILIMETROS_POR_METRO
from src.modulos.M9_cabezal import TIPO_GRAVEDAD
from src.modelos import SECCION_ALERO, SECCION_ALERO_MITAD  # --- VE-6 ---
from src.modelos import (
    CIFRAS_MAGNITUD, ELEMENTO_ALEROS, ELEMENTO_PANTALLA, ELEMENTO_ZAPATA,
    ESTADO_RASANTE_COMPATIBLE, ESTADO_RASANTE_SIN_TAMIZADO,
    ESTADO_RASANTE_SUBIR, MOTIVO_METODO_NO_EVALUABLE_METRADO,
    PARTIDA_ESPECIAL, RUBRO_ACERO, RUBRO_CONCRETO,
    RUBRO_CONDUCTO, RUBRO_ENROCADO, RUBRO_EXCAVACION, RUBRO_GEOTEXTIL,
    RUBRO_LOSA, DatoFaltanteError, DatoInvalidoError, FilaCompatibilidadRasante,
    FormaSeccion, Magnitud, MetodoNoEvaluableError, RenglonDeMetrado,
    SeccionRectangular, TipoDeVeredicto, TotalDePartida, Veredicto, paso)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

# Los criterios que este modulo lee, por su clave.
CRITERIO_SOBREANCHO = "sobreancho_excavacion_estructuras_m"
CRITERIO_INCREMENTO_ACERO = "incremento_acero_por_despiece"
CRITERIO_CLASE_LOSA = "clase_concreto_losa_entrega"

# Los codigos de paso de la Fase 11 (`PasoDeMemoria.codigo`).
CODIGO_CONDUCTO = "11.1"
CODIGO_ZANJA = "11.2"
CODIGO_CIMIENTOS = "11.3"
CODIGO_CONCRETO = "11.4"
CODIGO_ACERO = "11.5"
CODIGO_LOSA = "11.6"
CODIGO_ENROCADO = "11.7"
CODIGO_GEOTEXTIL = "11.8"

# Lo que dice cada renglon de excavacion segun la clase (501.01).
_EN_SECO = "en seco"
_BAJO_AGUA = "bajo agua (bajo el nivel freatico)"

NOTA_SIN_DESPERDICIO = (
    "Sin factor de desperdicio ni de esponjamiento: el EG-2013 mide la "
    "cantidad colocada o en su posicion original y pone el desperdicio en "
    "el precio unitario (503.13, 504.11).")


def _m(simbolo: str, valor, unidad: str, procedencia: str) -> Magnitud:
    return Magnitud(simbolo, valor, unidad, procedencia, cifras=CIFRAS_MAGNITUD)


def _sin_veredicto(explicacion: str) -> Veredicto:
    return Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO, explicacion=explicacion)


# ===========================================================================
# Entregable 9 - Cuadro de compatibilidad rasante-alcantarilla (7.A)
# ===========================================================================

def fila_compatibilidad(*, punto, tamizado=None, cota_salida: Optional[float]
                        = None, seccion: str = "",
                        delta_no_factible: Optional[float] = None,
                        motivo: str = "") -> FilaCompatibilidadRasante:
    """
    Una fila del cuadro de compatibilidad rasante-alcantarilla (Fase 11,
    entregable 9: «salida de 7.A»).

    Con el `TamizadoRasante` de la seccion ADOPTADA (el que 7.B recalcula)
    transcribe sus cotas y su condicion gobernante, y calcula la HOLGURA:

        holgura = cota de rasante actual - cota de rasante minima de 7.A

    positiva es el margen y negativa lo que falta. Sin tamizado --el punto no
    dimensiono-- la fila dice por que: el delta de rasante del «no factible»
    de MD, si lo hubo (`delta_no_factible`), o el motivo.
    """
    comunes = dict(id_punto=punto.id, progresiva=punto.progresiva_display,
                   familia=punto.familia.value, seccion=seccion)
    if tamizado is None:
        if delta_no_factible is not None:
            return FilaCompatibilidadRasante(
                **comunes, estado=ESTADO_RASANTE_SUBIR,
                cota_rasante_actual=punto.cota_rasante,
                delta_rasante_m=delta_no_factible,
                holgura_m=-delta_no_factible,
                motivo=motivo or "ningun escalon cabe bajo la subrasante: "
                                 "el delta es la cota inferior de 7.A")
        return FilaCompatibilidadRasante(
            **comunes, estado=ESTADO_RASANTE_SIN_TAMIZADO,
            cota_rasante_actual=punto.cota_rasante,
            motivo=motivo or "el punto no llego a 7.A con una seccion "
                             "adoptada")
    holgura = tamizado.cota_rasante_actual - tamizado.cota_rasante_min
    return FilaCompatibilidadRasante(
        **comunes,
        estado=(ESTADO_RASANTE_COMPATIBLE if tamizado.factible
                else ESTADO_RASANTE_SUBIR),
        cota_rasante_actual=tamizado.cota_rasante_actual,
        cota_rasante_min=tamizado.cota_rasante_min,
        cota_por_recubrimiento=tamizado.cota_por_recubrimiento,
        cota_por_resguardo=tamizado.cota_por_resguardo,
        gobierna=tamizado.condicion_gobernante.value,
        holgura_m=holgura,
        delta_rasante_m=(None if tamizado.factible
                         else tamizado.delta_rasante_m),
        cota_entrada=tamizado.cota_entrada, cota_clave=tamizado.cota_clave,
        cota_salida=cota_salida, provisional=tamizado.provisional,
        aviso=tamizado.aviso, motivo=motivo)


# ===========================================================================
# Utilidades de geometria del metrado
# ===========================================================================

def integral_positiva(d0: float, d1: float, longitud: float) -> float:
    """
    ∫_0^L max(0, d(x)) dx con d lineal de d0 a d1: el area de la parte
    POSITIVA de un trapecio que puede cruzar el cero (la profundidad de una
    zanja que sale del terreno, o el espesor bajo el freatico que se anula).
    Exacta: si d cambia de signo, el area positiva es un triangulo.
    """
    if not longitud > 0:
        return 0.0
    if d0 >= 0 and d1 >= 0:
        return (d0 + d1) / 2 * longitud
    if d0 <= 0 and d1 <= 0:
        return 0.0
    positiva, negativa = (d0, d1) if d0 > 0 else (d1, d0)
    corte = longitud * positiva / (positiva - negativa)
    return positiva * corte / 2


def _pie(g) -> float:
    """El terreno al pie del muro, msnm: desplante + D_f (la referencia de
    `M9.predimensionar_cabezal`)."""
    return g.cota_desplante + g.D_f


def _aleros(g) -> Tuple[Tuple[str, float, float], ...]:
    """(nombre, longitud, alfa con la pared del barril en grados) de los
    dos aleros del cabezal, o () sin aleros."""
    a = g.aleros
    if a is None:
        return ()
    return (("alero corto", a.longitud_corto, a.angulo_grados),
            ("alero largo", a.longitud_largo, a.angulo_largo_grados))


def _altura_media_alero(g) -> float:
    """La altura media del FUSTE de un alero sobre su zapata: la visible
    media sobre el pie mas lo que queda bajo el pie hasta la cara superior
    de su zapata (D_f - e_zapata del alero)."""
    a = g.aleros
    return ((a.altura_inicial + a.altura_final) / 2
            + g.D_f - a.espesor_zapata)


def ancho_losa(g, x: float) -> float:
    """
    El ancho de la losa de entrega a la distancia x del cabezal: la
    longitud del cabezal mas lo que cada alero se abre hasta x (x·tan alfa
    mientras el alero llega, L·sen alfa despues), con alfa medido desde la
    pared del barril (ΘW del HDS-5). Sin aleros, la longitud del cabezal.
    """
    ancho = g.longitud
    for _nombre, L, alfa in _aleros(g):
        rad = math.radians(alfa)
        alcance = L * math.cos(rad)
        ancho += (x * math.tan(rad) if x <= alcance else L * math.sin(rad))
    return ancho


def area_losa(g) -> float:
    """
    ∫_0^L_losa ancho_losa(x) dx, exacta: por cada alero, la parte en que
    todavia se abre (triangulo) y la parte en que ya termino (rectangulo).
    """
    L_losa = g.losa.longitud
    area = g.longitud * L_losa
    for _nombre, L, alfa in _aleros(g):
        rad = math.radians(alfa)
        alcance = L * math.cos(rad)
        if L_losa <= alcance:
            area += math.tan(rad) * L_losa ** 2 / 2
        else:
            area += (math.tan(rad) * alcance ** 2 / 2
                     + L * math.sin(rad) * (L_losa - alcance))
    return area


def area_exterior_del_conducto(seccion, espesor: float,
                               celdas: int) -> float:
    """El area que encierra la superficie exterior del conducto, con todas
    sus celdas: el vano que descuenta el concreto de un cabezal."""
    if isinstance(seccion, SeccionRectangular):
        return (seccion.ancho_exterior_de_celdas(espesor, celdas)
                * seccion.canto_exterior(espesor))
    return celdas * seccion.area_exterior(espesor)


def _ancho_exterior(seccion, espesor: float, celdas: int) -> float:
    if isinstance(seccion, SeccionRectangular):
        return seccion.ancho_exterior_de_celdas(espesor, celdas)
    return seccion.ancho_exterior(espesor)


def _extremos(cabezal):
    return ((cabezal.entrada.extremo or "entrada", cabezal.entrada),
            (cabezal.salida.extremo or "salida", cabezal.salida))


# ===========================================================================
# Entregable 8 - Metrados
# ===========================================================================

def renglones_conducto(*, material, seccion, celdas: int, espesor: float,
                       cabezal, S: float) -> Tuple[RenglonDeMetrado, ...]:
    """
    El conducto (EG-2013 506.14, 507.12, 508.11; 503.12 para el marco).

        L_eje = L_metrado · sqrt(1 + S^2)

    L_metrado es la longitud del barril en planta que la Fase 9 cierra con
    el relleno retenido y los dos muros (`CabezalDelPunto.longitud_metrado`,
    ficha T7A-06): entre las caras exteriores de los cabezales. La
    especificacion manda medirla «a lo largo del eje longitudinal y siguiendo
    la pendiente», de ahi el factor. Un tubo se mide en m (partida 50x.A); un
    marco vaciado en sitio no es tuberia y se mide en m3 de concreto:

        V = (Bc · B'c - N · B · H) · L_eje
    """
    L = cabezal.longitud_metrado
    if L is None:
        raise DatoFaltanteError(
            "longitud_metrado", id_punto=cabezal.id_punto,
            detalle="la Fase 9 no cerro la longitud entre cabezales ("
                    + (cabezal.motivo_sin_longitud or "sin motivo") + "): sin "
                    "ella no hay caras exteriores entre las que medir el "
                    "conducto (EG-2013 506.14)")
    factor = math.sqrt(1 + S ** 2)
    L_eje = L * factor
    sust = (_m("L_metrado", L, "m", "Fase 9, longitud entre cabezales mas "
               "los dos muros (paso 9.0.5)"),
            _m("S", S, "m/m", "pendiente del conducto con que corrio el "
               "diseño (Fase 7.B)"))
    if material.forma is FormaSeccion.RECTANGULAR:
        A_ext = area_exterior_del_conducto(seccion, espesor, celdas)
        A_int = celdas * seccion.B * seccion.H
        V = (A_ext - A_int) * L_eje
        clase = "sin determinar"
        p = paso(
            "F11.CONDUCTO", codigo=CODIGO_CONDUCTO,
            que="Metrado del marco vaciado en sitio: concreto estructural",
            formula="V = (Bc·B'c - N·B·H)·L_metrado·sqrt(1 + S^2)",
            formula_cita_id="EG2013.503.12",
            sustitucion=sust + (
                _m("Bc·B'c", A_ext, "m2", f"area exterior de {celdas} "
                   "celda(s) con el espesor de pared adoptado"),
                _m("N·B·H", A_int, "m2", "area interior de las celdas")),
            resultado=_m("V", V, "m3", "concreto del marco, medido como "
                         "estructura (503.12)"),
            veredicto=_sin_veredicto("metrado: no se contrasta"),
            citas_textuales=("EG2013.503.12",),
            nota_del_proyecto=(
                "El marco no es una tuberia: el EG-2013 no tiene partida de "
                "cajon y se construye bajo la Seccion 503 (num. 503.10 h)). "
                "Su acero no se metra: el armado de la seccion del marco "
                "esta fuera del alcance declarado. " + NOTA_SIN_DESPERDICIO))
        codigo, plantilla = PARTIDA_CONCRETO_EG2013
        return (RenglonDeMetrado(
            rubro=RUBRO_CONDUCTO, elemento="marco vaciado en sitio",
            partida=codigo, descripcion=plantilla.format(clase=clase),
            unidad=UNIDAD_M3, cantidad=V, paso=p,
            avisos=("marco: la clase de concreto no se determina, porque el "
                    "armado de la seccion del marco esta fuera del alcance "
                    "declarado (armado_seccion_marco); el volumen vale "
                    "igual",),
            desglose=(("seccion de concreto por metro (m2)", A_ext - A_int),
                      ("longitud a lo largo del eje (m)", L_eje))),)
    tipo = material.tipo.value
    codigo, plantilla = PARTIDA_TUBERIA_EG2013[tipo]
    cita = CITA_LONGITUD_TUBERIA_EG2013[tipo]
    D = seccion.D
    descripcion = plantilla.format(D_mm=f"{D * MILIMETROS_POR_METRO:.0f}",
                                   D_m=f"{D:.2f}")
    p = paso(
        "F11.CONDUCTO", codigo=CODIGO_CONDUCTO,
        que="Metrado del conducto: tuberia entre las caras exteriores de "
            "los cabezales, siguiendo la pendiente",
        formula="L_eje = N · L_metrado · sqrt(1 + S^2)",
        formula_cita_id=cita,
        sustitucion=sust + (_m("N", celdas, "", "barriles del conducto"),),
        resultado=_m("L_eje", celdas * L_eje, "m", f"partida {codigo}"),
        veredicto=_sin_veredicto("metrado: no se contrasta"),
        citas_textuales=(cita,),
        nota_del_proyecto=(
            "La partida incluye el solado o la cama y la sujecion; la "
            "excavacion y el relleno se pagan aparte (Secciones 501 y 502)."))
    return (RenglonDeMetrado(
        rubro=RUBRO_CONDUCTO, elemento="conducto", partida=codigo,
        descripcion=descripcion, unidad=UNIDAD_M, cantidad=celdas * L_eje,
        paso=p, desglose=(("longitud en planta (m)", L),
                          ("factor de pendiente", factor))),)


def _clasificacion_del_material(punto) -> bool:
    """
    True si la excavacion es en ROCA, False si en material comun (501.01).
    Material comun es «toda excavación de materiales no cubiertos» por la
    roca: el punto lo es si su calicata declara un suelo SUCS (E.050, Figura
    3; un simbolo doble como «SP-SM» se lee simbolo por simbolo). Un
    `sucs_fundacion` que no es un simbolo de suelo no se interpreta: puede
    ser roca, y la partida 501.A/B no se supone.
    """
    simbolos = [s.strip().upper()
                for s in str(punto.sucs_fundacion or "").split("-")]
    if simbolos and all(s in SIMBOLOS_SUCS for s in simbolos):
        return False
    raise DatoFaltanteError(
        "sucs_fundacion", id_punto=punto.id,
        detalle=f"«{punto.sucs_fundacion}» no es un simbolo de suelo de la "
                "E.050 (Figura 3): la excavacion puede ser en roca (501.A o "
                "501.B, la que exige explosivos) y el metrado no la "
                "clasifica. Declarar el suelo de la calicata, o metrar la "
                "roca con el estudio de suelos")


def renglones_excavacion(*, punto, material, seccion, celdas: int,
                         espesor: float, cabezal, cota_solera_entrada: float,
                         cota_solera_salida: float
                         ) -> Tuple[RenglonDeMetrado, ...]:
    """
    La excavacion para estructuras (EG-2013 501.09): la zanja del conducto y
    la de los cimientos de los dos cabezales (zapata, aleros y dentellon),
    cada una partida en «en seco» y «bajo agua» por el nivel freatico del
    punto (501.01). Volumen en su posicion original, caras verticales.

    ZANJA. Ancho W de la Seccion del tubo (506.06: Bc + 0.60 m; 507.05:
    1.5·D; 508.04: 2·D) o, en un marco, su ancho exterior mas el sobreancho
    de 501.04. Fondo bajo el fondo exterior del conducto con el solado o la
    cama minima (15 cm; el marco, sin solado). Corre entre los bordes de los
    talones, y su profundidad d(x) = terreno(x) - fondo(x) es lineal:

        V = W · ∫ max(0, d(x)) dx       V_agua = W · ∫ max(0, d(x) - NF) dx

    CIMIENTOS. Por cabezal, con s el sobreancho ('sobreancho_excavacion_
    estructuras_m', cero sin declarar):

        zapata      (B + 2s)(L_c + 2s) · D_f
        aleros      (B_al + 2s)(L_i + 2s) · D_f, cada uno
        dentellon   b_d · ancho de la losa en su borde · h_d
    """
    NF = punto.exigir("NF_profundidad_m")
    en_roca = _clasificacion_del_material(punto)
    s = ca.valor_si_declarado(CRITERIO_SOBREANCHO)
    s_origen = (f"'{CRITERIO_SOBREANCHO}' declarado" if s is not None else
                "sin declarar: caras verticales conforme a la estructura "
                "(501.04)")
    s = 0.0 if s is None else s
    renglones: List[RenglonDeMetrado] = []
    ent, sal = cabezal.entrada, cabezal.salida
    L_met = cabezal.longitud_metrado
    if L_met is None:
        raise DatoFaltanteError(
            "longitud_metrado", id_punto=punto.id,
            detalle="sin la longitud entre cabezales no se ubican los "
                    "talones entre los que corre la zanja")

    # --- zanja del conducto ------------------------------------------------
    tipo = material.tipo.value
    if material.forma is FormaSeccion.RECTANGULAR:
        W = _ancho_exterior(seccion, espesor, celdas) + 2 * s
        regla_ancho = (f"Bc + 2s = {_ancho_exterior(seccion, espesor, celdas):.3f}"
                       f" + 2·{s:.3f} (501.04, el marco como estructura)")
        cama, cita_ancho, cita_cama = 0.0, "EG2013.501.04#CARAS", ""
    else:
        regla, valor, cita_ancho = ANCHO_ZANJA_EG2013[tipo]
        if celdas > 1:
            raise MetodoNoEvaluableError(
                "ancho de la zanja", id_punto=punto.id,
                procedimiento="el ancho de la zanja de varios tubos en los "
                              "planos del expediente",
                motivo="las Secciones 506 a 508 dan el ancho de la zanja de "
                       "UN tubo", rotulo=MOTIVO_METODO_NO_EVALUABLE_METRADO)
        if regla == REGLA_ZANJA_EXTERIOR_MAS:
            W = seccion.ancho_exterior(espesor) + valor
            regla_ancho = (f"Bc + {valor:.2f} = "
                           f"{seccion.ancho_exterior(espesor):.3f} + "
                           f"{valor:.2f}")
        else:
            W = valor * seccion.D
            regla_ancho = f"{valor:g}·D = {valor:g}·{seccion.D:.3f}"
        cama, cita_cama = ESPESOR_MIN_CAMA_EG2013_M[tipo]
    fondo_e = cota_solera_entrada - espesor - cama
    fondo_s = cota_solera_salida - espesor - cama
    pie_e, pie_s = _pie(ent), _pie(sal)
    x_a = ent.espesor_base_muro + (ent.ancho_talon or 0.0)
    x_b = L_met - sal.espesor_base_muro - (sal.ancho_talon or 0.0)
    L_zanja = x_b - x_a

    def _en(x: float, a: float, b: float) -> float:
        return a + (b - a) * x / L_met

    d_a = _en(x_a, pie_e, pie_s) - _en(x_a, fondo_e, fondo_s)
    d_b = _en(x_b, pie_e, pie_s) - _en(x_b, fondo_e, fondo_s)
    V_zanja = W * integral_positiva(d_a, d_b, L_zanja)
    V_zanja_agua = W * integral_positiva(d_a - NF, d_b - NF, L_zanja)
    citas_zanja = tuple(c for c in ("EG2013.501.09", cita_ancho, cita_cama,
                                    "EG2013.501.01#CLASES") if c)
    p = paso(
        "F11.EXCAVACION", codigo=CODIGO_ZANJA,
        que="Metrado de la excavacion de la zanja del conducto",
        formula="V = W·∫max(0, d(x))dx;  V_agua = W·∫max(0, d(x) - NF)dx;  "
                "d = terreno - (solera - t - cama)",
        formula_cita_id="EG2013.501.09",
        sustitucion=(
            _m("W", W, "m", regla_ancho),
            _m("t", espesor, "m", "espesor de pared adoptado (Fase 3)"),
            _m("cama", cama, "m", "solado o cama minima de la Seccion del "
               "tubo" if cama else "el marco sin solado"),
            _m("terreno_e / terreno_s", f"{pie_e:.3f} / {pie_s:.3f}", "msnm",
               "pie de cada cabezal (Fase 9)"),
            _m("solera_e / solera_s", f"{cota_solera_entrada:.3f} / "
               f"{cota_solera_salida:.3f}", "msnm", "fondo del conducto en "
               "cada extremo (7.B)"),
            _m("L_zanja", L_zanja, "m", "entre los bordes de los talones: "
               "L_metrado - (e_muro + talon) en cada extremo"),
            _m("d_a / d_b", f"{d_a:.3f} / {d_b:.3f}", "m", "profundidad en "
               "los bordes de los talones (negativa: el conducto va sobre el "
               "terreno, en relleno)"),
            _m("NF", NF, "m", "profundidad del nivel freatico del punto "
               "(columna NF_profundidad_m)")),
        resultado=_m("V", V_zanja, "m3", f"de ellos {V_zanja_agua:.3f} m3 "
                     "bajo el nivel freatico"),
        veredicto=_sin_veredicto("metrado: no se contrasta"),
        citas_textuales=citas_zanja,
        nota_del_proyecto=(
            "El terreno y el fondo varian linealmente entre los pies de los "
            "dos cabezales; bajo los talones la excavacion es la de la zapata "
            "(paso 11.3). En su posicion original: sin esponjamiento."))
    renglones.extend(_renglones_por_agua(
        punto=punto, en_roca=en_roca, elemento="zanja del conducto",
        V=V_zanja, V_agua=V_zanja_agua, paso_=p))

    # --- cimientos de los cabezales ---------------------------------------
    for extremo, g in _extremos(cabezal):
        partes: List[Tuple[str, float, float]] = []   # (parte, V, V_agua)
        D_agua = max(0.0, g.D_f - NF)
        A_zap = (g.B + 2 * s) * (g.longitud + 2 * s)
        partes.append(("zapata del cabezal", A_zap * g.D_f, A_zap * D_agua))
        for nombre, L_i, _alfa in _aleros(g):
            A_al = (g.aleros.ancho_zapata + 2 * s) * (L_i + 2 * s) \
                if L_i > TOL_UMBRAL_NORMATIVO else 0.0
            partes.append((f"zapata del {nombre}", A_al * g.D_f,
                           A_al * D_agua))
        if g.losa is not None:
            lo = g.losa
            A_dent = lo.ancho_dentellon * ancho_losa(g, lo.longitud)
            partes.append(("dentellon de la losa",
                           A_dent * lo.profundidad_dentellon,
                           A_dent * max(0.0, lo.profundidad_dentellon - NF)))
        V = sum(v for _p, v, _a in partes)
        V_agua = sum(a for _p, _v, a in partes)
        p = paso(
            "F11.EXCAVACION", codigo=f"{CODIGO_CIMIENTOS}.{extremo[0]}",
            que=f"Metrado de la excavacion de los cimientos del cabezal de "
                f"{extremo}",
            formula="V = Σ A_i · h_i;  zapata (B + 2s)(L_c + 2s)·D_f; aleros "
                    "(B_al + 2s)(L_i + 2s)·D_f; dentellon b_d·ancho·h_d",
            formula_cita_id="EG2013.501.09",
            sustitucion=(
                _m("s", s, "m", s_origen),
                _m("B / L_c / D_f", f"{g.B:.3f} / {g.longitud:.3f} / "
                   f"{g.D_f:.3f}", "m", "geometria final del cabezal (Fase "
                   "9)"),
                _m("NF", NF, "m", "profundidad del nivel freatico del "
                   "punto")) + tuple(
                _m(parte, v, "m3", f"{a:.3f} m3 bajo el nivel freatico")
                for parte, v, a in partes),
            resultado=_m("V", V, "m3", f"de ellos {V_agua:.3f} m3 bajo el "
                         "nivel freatico"),
            veredicto=_sin_veredicto("metrado: no se contrasta"),
            citas_textuales=("EG2013.501.09", "EG2013.501.04#CARAS",
                             "EG2013.501.04#ENCOFRADO",
                             "EG2013.501.01#CLASES"),
            nota_del_proyecto=(
                "Desde el terreno al pie del cabezal hasta el desplante, con "
                "caras verticales. Los aleros se miden desde el extremo del "
                "cabezal, sin descontar el encuentro de las zapatas en la "
                "esquina."))
        renglones.extend(_renglones_por_agua(
            punto=punto, en_roca=en_roca,
            elemento=f"cimientos del cabezal de {extremo}",
            V=V, V_agua=V_agua, paso_=p,
            desglose=tuple((parte, v) for parte, v, _a in partes)))
    return tuple(renglones)


# --- VE-6 (dictamen Fable) --- EL REPARTO SECO / BAJO AGUA ES UNA LECTURA, NO
# LA PARTIDA DE OBRA. Lo lleva todo renglon bajo agua (501.B, 501.D); sin
# margen ni correccion numerica: la cantidad es la de la lectura.
AVISO_PARTIDA_BAJO_AGUA = (
    "excavacion bajo agua: el reparto entre seco y bajo agua sale de "
    "NF_profundidad_m, la lectura de campo del EMS, y no del freatico mas "
    "alto previsto; la partida definitiva la fija el Supervisor en obra, "
    "por las lineas «aprobadas por el Supervisor» (EG-2013 501.09) y donde "
    "«la presencia permanente de agua dificulte los trabajos de excavacion» "
    "(501.01, pag. impresa 886)")


def _renglones_por_agua(*, punto, en_roca: bool, elemento: str, V: float,
                        V_agua: float, paso_, desglose=()
                        ) -> Tuple[RenglonDeMetrado, ...]:
    """
    Parte un volumen de excavacion en sus dos partidas (501.01). El renglon
    bajo agua lleva `AVISO_PARTIDA_BAJO_AGUA`.
    """
    salida = []
    for bajo_agua, volumen in ((False, V - V_agua), (True, V_agua)):
        if not volumen > TOL_UMBRAL_NORMATIVO:
            continue
        codigo, texto = PARTIDA_EXCAVACION_EG2013[(en_roca, bajo_agua)]
        salida.append(RenglonDeMetrado(
            rubro=RUBRO_EXCAVACION,
            elemento=f"{elemento}, {_BAJO_AGUA if bajo_agua else _EN_SECO}",
            partida=codigo, descripcion=texto, unidad=UNIDAD_M3,
            cantidad=volumen, paso=paso_, desglose=desglose,
            avisos=(AVISO_PARTIDA_BAJO_AGUA,) if bajo_agua else ()))
    return tuple(salida)


def clase_de_concreto(fc_mpa: Optional[float], tipo: Optional[str]
                      ) -> Optional[str]:
    """
    La clase de la Tabla 503-07 del EG-2013 (cita EG2013.503.04#T503_07):
    la G para el cabezal de gravedad en ciclopeo; para el armado, la clase
    de concreto REFORZADO de menor resistencia que alcanza el f'c con que se
    armo. None si ninguna lo alcanza o si no hay f'c.
    """
    if tipo == TIPO_GRAVEDAD:
        return CLASE_CONCRETO_CICLOPEO_EG2013
    if fc_mpa is None:
        return None
    candidatas = sorted(
        (CLASES_CONCRETO_EG2013_MPA[c], c)
        for c in CLASES_CONCRETO_REFORZADO_EG2013
        if CLASES_CONCRETO_EG2013_MPA[c] >= fc_mpa - TOL_UMBRAL_NORMATIVO)
    return candidatas[0][1] if candidatas else None


def volumen_cabezal(g, area_vano: float) -> Tuple[Tuple[str, float], ...]:
    """
    Las partes del concreto de UN cabezal, m3 (503.12):

        pantalla   (e_corona + e_base)/2 · H · L_c
        zapata     B · e_z · L_c
        aleros     e_al · h_media · L_i + B_al · e_z,al · L_i, cada uno
        vano       - A_ext · e_base (el conducto atraviesa el muro)
    """
    partes = [
        ("pantalla", (g.espesor_corona + g.espesor_base_muro) / 2 * g.H
         * g.longitud),
        ("zapata", g.B * g.espesor_zapata * g.longitud)]
    for nombre, L_i, _alfa in _aleros(g):
        a = g.aleros
        partes.append((f"fuste del {nombre}",
                       a.espesor * _altura_media_alero(g) * L_i))
        partes.append((f"zapata del {nombre}",
                       a.ancho_zapata * a.espesor_zapata * L_i))
    partes.append(("vano del conducto (se descuenta)",
                   -area_vano * g.espesor_base_muro))
    return tuple(partes)


def renglones_concreto_cabezales(*, cabezal, seccion, celdas: int,
                                 espesor: float
                                 ) -> Tuple[RenglonDeMetrado, ...]:
    """El concreto estructural de los dos cabezales (503.12, 503.A)."""
    area_vano = area_exterior_del_conducto(seccion, espesor, celdas)
    armados = {a.extremo: a for a in cabezal.armado}
    renglones = []
    for extremo, g in _extremos(cabezal):
        partes = volumen_cabezal(g, area_vano)
        V = sum(v for _p, v in partes)
        armado = armados.get(g.extremo)
        clase = clase_de_concreto(armado.fc_mpa if armado else None, g.tipo)
        avisos = ()
        if clase is None:
            avisos = (f"cabezal de {extremo}: la clase de concreto no se "
                      "determina (el armado no se evaluo o su f'c supera la "
                      "Clase C de la Tabla 503-07); el volumen vale igual",)
        codigo, plantilla = PARTIDA_CONCRETO_EG2013
        p = paso(
            "F11.CONCRETO", codigo=f"{CODIGO_CONCRETO}.{extremo[0]}",
            que=f"Metrado del concreto del cabezal de {extremo}",
            formula="V = (e_c + e_b)/2·H·L_c + B·e_z·L_c + Σ aleros - "
                    "A_ext·e_b",
            formula_cita_id="EG2013.503.12",
            sustitucion=(
                _m("H / L_c", f"{g.H:.3f} / {g.longitud:.3f}", "m",
                   "geometria final del cabezal (Fase 9)"),
                _m("e_c / e_b / e_z", f"{g.espesor_corona:.3f} / "
                   f"{g.espesor_base_muro:.3f} / {g.espesor_zapata:.3f}",
                   "m", "geometria final del cabezal (Fase 9)"),
                _m("B", g.B, "m", "ancho final de la zapata (Fase 9)"),
                _m("A_ext", area_vano, "m2", "area exterior del conducto "
                   "(vano)"),
                _m("f'c", armado.fc_mpa if armado else "sin armado", "MPa",
                   "con el que se armo el cabezal (Fase 9)")) + tuple(
                _m(parte, v, "m3", "parte del cabezal") for parte, v in partes),
            resultado=_m("V", V, "m3", f"Clase {clase or 'sin determinar'} "
                         "de la Tabla 503-07"),
            veredicto=_sin_veredicto("metrado: no se contrasta"),
            citas_textuales=("EG2013.503.12", "EG2013.503.13#DESPERDICIOS",
                             "EG2013.503.04#T503_07"),
            nota_del_proyecto=(
                "La clase es la de concreto reforzado de menor resistencia "
                "que alcanza el f'c del armado; el cabezal de gravedad es "
                "Clase G (ciclopeo). " + NOTA_SIN_DESPERDICIO))
        renglones.append(RenglonDeMetrado(
            rubro=RUBRO_CONCRETO, elemento=f"cabezal de {extremo}",
            partida=codigo,
            descripcion=plantilla.format(clase=clase or "sin determinar"),
            unidad=UNIDAD_M3, cantidad=V, paso=p, desglose=partes,
            avisos=avisos))
    return tuple(renglones)


def _geometria_de_la_fila(fila, g) -> Tuple[float, float, int, str]:
    """
    (largo de cada barra, ancho en que se reparten, caras, regla) de una
    fila de la tabla de armado: la direccion la dice su posicion
    (vertical o transversal frente a horizontal o longitudinal) y el
    elemento las dimensiones.
    """
    pos = fila.posicion.lower()
    caras = 2 if "cada cara" in pos else 1
    a_lo_largo = "horizontal" in pos or "longitudinal" in pos
    if fila.elemento == ELEMENTO_PANTALLA:
        if a_lo_largo:
            return g.longitud, g.H, caras, "largo L_c, repartidas en H"
        return g.H, g.longitud, caras, "largo H, repartidas en L_c"
    if fila.elemento == ELEMENTO_ZAPATA:
        if a_lo_largo:
            return g.longitud, g.B, caras, "largo L_c, repartidas en B"
        return g.B, g.longitud, caras, "largo B, repartidas en L_c"
    if fila.elemento == ELEMENTO_ALEROS and g.aleros is not None:
        L_al = g.aleros.longitud_corto + g.aleros.longitud_largo
        h = _altura_media_alero(g)
        if a_lo_largo:
            return L_al, h, caras, ("largo de los dos aleros, repartidas en "
                                    "su altura media")
        # --- VE-6 (ficha VE6M9-03) --- el alero se arma por tramos: la
        # seccion del arranque arma de 0 a L/2 y la de la mitad de L/2 a L;
        # cada fila se reparte en la mitad de la longitud de los aleros.
        por_tramos = (pos.startswith(f"{SECCION_ALERO_MITAD}:")
                      or (pos.startswith(f"{SECCION_ALERO}:")
                          and g.aleros.altura_inicial
                          > g.aleros.altura_final + TOL_UMBRAL_NORMATIVO))
        if por_tramos:
            return h, L_al / 2, caras, ("altura media de los aleros, "
                                        "repartidas en la mitad de su "
                                        "longitud (su tramo)")
        return h, L_al, caras, ("altura media de los aleros, repartidas en "
                                "su longitud")
    raise DatoInvalidoError(
        "armado del cabezal", valor=(fila.elemento, fila.posicion),
        motivo="la fila no corresponde a ningun elemento del cabezal que el "
               "metrado sepa medir")


def renglones_acero_cabezales(*, cabezal) -> Tuple[RenglonDeMetrado, ...]:
    """
    El acero de refuerzo de los cabezales armados (504.10, 504.A):

        P = (1 + i) · Σ caras · (ancho / s) · largo · w

    con la barra y el espaciamiento que el armado PROPONE para cada cara
    (`ArmadoDelCabezal.tabla`), el peso w de la Tabla 504-01 y el incremento
    i de 'incremento_acero_por_despiece' [A] por anclajes y empalmes. Un
    cabezal de gravedad no lleva acero.
    """
    armados = [(e, g, next((a for a in cabezal.armado
                            if a.extremo == g.extremo), None))
               for e, g in _extremos(cabezal)]
    a_metrar = [(e, g, a) for e, g, a in armados if g.tipo != TIPO_GRAVEDAD]
    if not a_metrar:
        return ()
    faltan = [e for e, _g, a in a_metrar if a is None]
    if faltan:
        raise MetodoNoEvaluableError(
            "acero de refuerzo", id_punto=cabezal.id_punto,
            procedimiento="el armado del cabezal (Fase 9), que su propio "
                          "bloqueo detiene",
            motivo="el armado del cabezal de " + " y ".join(faltan)
                   + " no se evaluo", rotulo=MOTIVO_METODO_NO_EVALUABLE_METRADO)
    i = ca.valor(CRITERIO_INCREMENTO_ACERO)
    codigo, texto = PARTIDA_ACERO_EG2013
    renglones = []
    for extremo, g, armado in a_metrar:
        por_barra: Dict[str, float] = OrderedDict()
        filas_sust = []
        for fila in armado.tabla:
            if fila.barra is None:
                raise DatoFaltanteError(
                    "barra del armado", id_punto=cabezal.id_punto,
                    detalle=f"el armado del cabezal de {extremo} no propone "
                            f"barra para «{fila.posicion}»: sin barra no hay "
                            "peso que medir (504.10)")
            b = fila.barra
            if b.designacion not in PESO_BARRA_KG_M_EG2013:
                raise DatoInvalidoError(
                    "barra del armado", valor=b.designacion,
                    id_punto=cabezal.id_punto,
                    motivo="la Tabla 504-01 del EG-2013 no tiene esa barra")
            largo, ancho, caras, regla = _geometria_de_la_fila(fila, g)
            w = PESO_BARRA_KG_M_EG2013[b.designacion]
            peso = caras * (ancho / b.espaciamiento) * largo * w
            clave = f"Ø {b.designacion}\""
            por_barra[clave] = por_barra.get(clave, 0.0) + peso
            filas_sust.append(_m(
                fila.posicion, peso, "kg",
                f"{b.texto}, {regla}: {caras}·({ancho:.3f}/"
                f"{b.espaciamiento:.3f})·{largo:.3f}·{w:.2f} kg/m"))
        neto = sum(por_barra.values())
        P = (1 + i) * neto
        p = paso(
            "F11.ACERO", codigo=f"{CODIGO_ACERO}.{extremo[0]}",
            que=f"Metrado del acero de refuerzo del cabezal de {extremo}",
            formula="P = (1 + i)·Σ caras·(ancho/s)·largo·w",
            formula_cita_id="EG2013.504.10",
            sustitucion=tuple(filas_sust) + (
                _m("Σ", neto, "kg", "peso de las barras dentro de los "
                   "elementos"),
                _m("i", i, "", f"'{CRITERIO_INCREMENTO_ACERO}' [A]: "
                   "anclajes, ganchos y empalmes del despiece")),
            resultado=_m("P", P, "kg", f"partida {codigo}"),
            veredicto=_sin_veredicto("metrado: no se contrasta"),
            citas_textuales=("EG2013.504.10", CITA_PESO_BARRA_EG2013),
            nota_del_proyecto=(
                "Las barras transversales de la zapata recorren su ancho B y "
                "las de los aleros su altura media o su longitud. " +
                NOTA_SIN_DESPERDICIO))
        renglones.append(RenglonDeMetrado(
            rubro=RUBRO_ACERO, elemento=f"cabezal de {extremo}",
            partida=codigo,
            descripcion=f"{texto} (fy = {armado.fy_mpa:.0f} MPa)"
            if armado.fy_mpa else texto,
            unidad=UNIDAD_KG, cantidad=P, paso=p,
            desglose=tuple((k, (1 + i) * v) for k, v in por_barra.items())))
    return tuple(renglones)


def renglones_losa_entrega(*, cabezal) -> Tuple[RenglonDeMetrado, ...]:
    """
    El concreto de la losa de entrega y su dentellon (503.12), con la clase
    que declare 'clase_concreto_losa_entrega' [A]:

        V = e_losa · A_losa + b_d · h_d · ancho(L_losa)

    A_losa es el area entre los aleros hasta la longitud de la losa
    (`area_losa`).
    """
    losas = [(e, g) for e, g in _extremos(cabezal) if g.losa is not None]
    if not losas:
        return ()
    clase = ca.valor(CRITERIO_CLASE_LOSA)
    codigo, plantilla = PARTIDA_CONCRETO_EG2013
    renglones = []
    for extremo, g in losas:
        lo = g.losa
        A = area_losa(g)
        ancho_borde = ancho_losa(g, lo.longitud)
        V_losa = lo.espesor * A
        V_dent = lo.ancho_dentellon * lo.profundidad_dentellon * ancho_borde
        p = paso(
            "F11.CONCRETO", codigo=f"{CODIGO_LOSA}.{extremo[0]}",
            que=f"Metrado del concreto de la losa de entrega y el dentellon "
                f"del cabezal de {extremo}",
            formula="V = e_losa·A_losa + b_d·h_d·ancho(L_losa)",
            formula_cita_id="EG2013.503.12",
            sustitucion=(
                _m("L_losa / e_losa", f"{lo.longitud:.3f} / "
                   f"{lo.espesor:.3f}", "m", "losa de entrega (Fase 9)"),
                _m("A_losa", A, "m2", "entre los aleros hasta L_losa"),
                _m("ancho(L_losa)", ancho_borde, "m", "ancho en el borde "
                   "libre, donde corre el dentellon"),
                _m("b_d / h_d", f"{lo.ancho_dentellon:.3f} / "
                   f"{lo.profundidad_dentellon:.3f}", "m", "dentellon "
                   "(Fase 9)"),
                _m("clase", clase, "", f"'{CRITERIO_CLASE_LOSA}' [A]")),
            resultado=_m("V", V_losa + V_dent, "m3", f"Clase {clase}"),
            veredicto=_sin_veredicto("metrado: no se contrasta"),
            citas_textuales=("EG2013.503.12", "EG2013.503.04#T503_07"),
            nota_del_proyecto=(
                "La losa ocupa el espacio entre los aleros; cada alero se "
                "abre L·sen(alfa) desde el extremo del cabezal. " +
                NOTA_SIN_DESPERDICIO))
        renglones.append(RenglonDeMetrado(
            rubro=RUBRO_LOSA, elemento=f"losa de entrega y dentellon del "
            f"cabezal de {extremo}", partida=codigo,
            descripcion=plantilla.format(clase=clase), unidad=UNIDAD_M3,
            cantidad=V_losa + V_dent, paso=p,
            desglose=(("losa", V_losa), ("dentellon", V_dent))))
    return tuple(renglones)


def renglones_proteccion_salida(*, proteccion, seccion, celdas: int
                                ) -> Tuple[RenglonDeMetrado, ...]:
    """
    El enrocado de salida y el geotextil bajo el. La planta es la del apron
    de HEC-14 (cita HEC14.10.2#ANCHO): 3D en la boca y abocinado 1:3 por
    lado hasta la longitud que rige:

        A = (W_0 + W_L)/2 · L,   W_0 = 3D,   W_L = 3D + (2/3)L
        V_enrocado = A · e        A_geotextil = A   (511.13, traslapes dentro)

    D es la altura del conducto («D is the culvert rise», como en M6).
    """
    if celdas > 1:
        raise MetodoNoEvaluableError(
            "area del enrocado de salida", procedimiento="la planta del "
            "enrocado de varios barriles en los planos del expediente",
            motivo="el apron de HEC-14 (Figura 10.4) es el de un conducto",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_METRADO)
    L, e = proteccion.longitud, proteccion.espesor
    if L is None or e is None:
        raise DatoFaltanteError(
            "proteccion de salida", detalle="la Fase 6 no fijo la longitud o "
            "el espesor del enrocado")
    D = seccion.altura
    W0 = HEC14_APRON_ANCHO_EN_LA_BOCA_EN_D * D
    WL = W0 + HEC14_APRON_ABOCINADO_POR_LONGITUD * L
    A = (W0 + WL) / 2 * L
    V = A * e
    sust = (_m("D", D, "m", "altura del conducto adoptado"),
            _m("L", L, "m", "longitud de la proteccion que rige (Fase 6)"),
            _m("W_0 / W_L", f"{W0:.3f} / {WL:.3f}", "m", "ancho en la boca "
               "y al final del apron (HEC-14, abocinado 1:3)"))
    p_enr = paso(
        "F11.ENROCADO", codigo=CODIGO_ENROCADO,
        que="Metrado del enrocado de salida",
        formula="V = (W_0 + W_L)/2·L·e;  W_0 = 3D;  W_L = 3D + (2/3)L",
        formula_cita_id="HEC14.10.2#ANCHO",
        sustitucion=sust + (_m("e", e, "m", "espesor de la proteccion que "
                               "rige (Fase 6)"),),
        resultado=_m("V", V, "m3", "partida especial del proyecto"),
        veredicto=_sin_veredicto("metrado: no se contrasta"),
        citas_textuales=("HEC14.10.2#ANCHO", "EG2013.603.10"),
        nota_del_proyecto=SIN_PARTIDA_ENROCADO_SALIDA_EG2013)
    renglones = [RenglonDeMetrado(
        rubro=RUBRO_ENROCADO, elemento="enrocado de salida", partida="",
        descripcion=("Enrocado de proteccion de salida (partida especial"
                     + (f", d50 = {proteccion.d50:.3f} m"
                        if proteccion.d50 is not None else "") + ")"),
        unidad=UNIDAD_M3, cantidad=V, paso=p_enr,
        etiqueta_partida=PARTIDA_ESPECIAL,
        desglose=(("area en planta (m2)", A), ("espesor (m)", e)))]
    if proteccion.filtro is not None:
        codigo, texto = PARTIDA_GEOTEXTIL_EG2013
        p_geo = paso(
            "F11.ENROCADO", codigo=CODIGO_GEOTEXTIL,
            que="Metrado del geotextil de filtro bajo el enrocado de salida",
            formula="A = (W_0 + W_L)/2·L",
            formula_cita_id="EG2013.511.13",
            sustitucion=sust,
            resultado=_m("A", A, "m2", f"partida {codigo}, traslapes "
                         "incluidos en la medida"),
            veredicto=_sin_veredicto("metrado: no se contrasta"),
            citas_textuales=("EG2013.511.13", "HEC14.10.2#ANCHO"),
            nota_del_proyecto=(
                "El geotextil cubre la planta del enrocado; los traslapes y "
                "costuras estan en la medida y en el precio (511.13, "
                "511.14). Su clase la fija el requisito de la Fase 6 (Tabla "
                "511-06)."))
        renglones.append(RenglonDeMetrado(
            rubro=RUBRO_GEOTEXTIL, elemento="geotextil bajo el enrocado",
            partida=codigo,
            descripcion=f"{texto} ({proteccion.filtro.clase_geotextil})",
            unidad=UNIDAD_M2, cantidad=A, paso=p_geo))
    return tuple(renglones)


# ===========================================================================
# Totales del expediente
# ===========================================================================

# ---------------------------------------------------------------------------
# --- VE-7 lote B, B7 (VE5-MET-01; decision del consultor Fable, triaje VE-7,
# 2026-11-20) --- LO QUE NO SE METRA, DICHO RENGLON POR RENGLON. Tres partes
# de la obra no se miden y hasta VE-7 el cuadro las omitia en silencio: cada
# una sale como `Bloqueo` de la fase de los metrados («no medido») con su
# motivo, como cualquier renglon que no se pudo medir (`MetradoDelPunto`).
# ---------------------------------------------------------------------------
NO_MEDIDO_RELLENO = "relleno para estructuras (EG-2013 502.A)"
NO_MEDIDO_CAMA = "cama de apoyo del conducto"
NO_MEDIDO_EMBOQUILLADO = "revestimiento de la entrada (emboquillado)"

# (que se omite, que haria falta para medirlo, por que no se mide hoy)
RENGLONES_NO_MEDIDOS: Dict[str, Tuple[str, str]] = OrderedDict((
    (NO_MEDIDO_RELLENO, (
        "la seccion del relleno compactado alrededor del conducto y del "
        "trasdos de los cabezales, de los planos del expediente",
        "el programa no tiene la seccion del relleno: la Fase 9 da el "
        "cabezal y la 7.B la cota del conducto, no las lineas del relleno")),
    (NO_MEDIDO_CAMA, (
        "el espesor y el ancho de la cama de la seccion tipica del plano",
        "la excavacion baja hasta el fondo de la cama (506.07, 508.05), pero "
        "el material de la cama no tiene renglon propio en este programa")),
    (NO_MEDIDO_EMBOQUILLADO, (
        "la geometria del zampeado y del dentellon de la entrada (planos del "
        "expediente; ficha T8-03)",
        "la proteccion de la entrada declara la CLASE de revestimiento "
        "('tipo_proteccion_entrada') y ninguna fuente del repositorio le da "
        "dimensiones")),
))


def etapa_no_medido(elemento: str) -> str:
    """La etapa de `servicio.FASE_METRADOS` del renglon no medido."""
    return f"metrado de {elemento}: no medido"


def renglon_no_medido(elemento: str, *, id_punto: Optional[str] = None):
    """
    --- VE-7 lote B, B7 --- El renglon que NO se metra, como excepcion: el
    servicio lo convierte en el `Bloqueo` de la fase de los metrados con su
    motivo, para que el cuadro no lo omita en silencio. `MetodoNoEvaluable`
    con el rotulo de los metrados: el dato esta, y lo que falta es la
    medicion de esa parte de la obra, que el programa no implementa.
    """
    procedimiento, motivo = RENGLONES_NO_MEDIDOS[elemento]
    raise MetodoNoEvaluableError(
        f"{elemento} (no medido)", id_punto=id_punto,
        procedimiento=procedimiento, motivo=f"no medido: {motivo}",
        rotulo=MOTIVO_METODO_NO_EVALUABLE_METRADO)


def totales_por_partida(metrados: Sequence) -> Tuple[TotalDePartida, ...]:
    """
    La suma de cada partida en el expediente: los renglones con la misma
    partida, la misma descripcion (diametro, clase) y la misma unidad, en el
    orden en que aparecen. `metrados` son los `MetradoDelPunto` de la
    corrida.
    """
    suma: "OrderedDict[Tuple[str, str, str, str], List]" = OrderedDict()
    for m in metrados:
        for r in m.renglones:
            clave = (r.partida, r.descripcion, r.unidad, r.etiqueta_partida)
            fila = suma.setdefault(clave, [0.0, []])
            fila[0] += r.cantidad
            if m.id_punto not in fila[1]:
                fila[1].append(m.id_punto)
    return tuple(TotalDePartida(partida=p, descripcion=d, unidad=u,
                                cantidad=c, puntos=tuple(ids),
                                etiqueta_partida=et)
                 for (p, d, u, et), (c, ids) in suma.items())
