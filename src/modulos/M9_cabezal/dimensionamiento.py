# -*- coding: utf-8 -*-
"""
M9_cabezal.dimensionamiento
===========================
Submodulo de Fase 9 (`M9_cabezal`): bloque `dimensionamiento` (D1).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from dataclasses import (
    dataclass,
    field,
    replace,
)
from src import criterios_adoptados as ca
from src.modelos import (
    CabezalDelPunto,
    DatoInvalidoError,
    ELEMENTO_ALEROS,
    ELEMENTO_PANTALLA,
    ELEMENTO_ZAPATA,
    EntornoDelCabezal,
    ErrorProyecto,
    EstabilidadDelCabezal,
    IntentoDePeralte,
    IntentoDeZapata,
    MOTIVO_METODO_NO_EVALUABLE_ARMADO,
    Magnitud,
    MetodoNoEvaluableError,
    ORIGEN_DIMENSION_ESTABILIDAD,
    PasoDeMemoria,
    paso,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CONDICIONES_DE_ESTABILIDAD,
    CRITERIO_DIMENSIONAMIENTO_ZAPATA,
    CRITERIO_GEOMETRIA,
    TIPO_GRAVEDAD,
    _exigir_positivo,
)
from src.modulos.M9_cabezal.armado import armar_elemento
from src.modulos.M9_cabezal.armado_secciones import solicitaciones_de_resistencia
from src.modulos.M9_cabezal.estabilidad import (
    datos_del_cabezal_del_punto,
    ensamble_estabilidad,
)
from src.modulos.M9_cabezal.geometria import cabezal_del_punto

# ===========================================================================
# --- VE-3.5 --- EL DIMENSIONAMIENTO DE LA ZAPATA POR ESTABILIDAD
# ===========================================================================
# Decision del dueño del 2026-11-17: el programa DIMENSIONA el cabezal en vez
# de solo verificar lo que la regla de T-7a propone (ficha T7B-09: con los
# datos de prueba de la validacion integral, la zapata de la regla no pasa
# E3-LRFD estatico ni E1-LRFD sismico en ningun punto). Va DETRAS de la
# estabilidad de la geometria de la regla y DELANTE del armado, que se hace
# con la geometria final (`servicio._fase_9`).
#
# QUE CRECE Y POR QUE: el ancho B, por el TALON -- la punta queda en la de la
# regla --. El talon suma el peso del relleno sobre la zapata y alarga el
# brazo de las cargas verticales, que es lo que piden el deslizamiento (mas
# fuerza normal en la base) y la capacidad portante (menos excentricidad,
# mas ancho efectivo) de un muro en voladizo. Medido con los datos de prueba
# de A-01: la entrada cumple con 2.40 m y la salida con 3.20 m, partiendo de
# 1.575 y 2.679 m.
#
# COMO: B_k = B_regla + k·paso, k = 1, 2, ...; se adopta el primer B_k con el
# que todas las condiciones evaluadas cumplen (E1 a E3 del marco que decide),
# sin pasar B_max = fraccion_ancho_max·H_c. Paso y tope son de
# 'dimensionamiento_zapata_cabezal' [A], sin valor de archivo: si falta, el
# dimensionamiento se detiene con `CriterioPendienteError` y la geometria de
# la regla se verifica como hasta VE-3.5. Un ancho DECLARADO gana y no se
# itera. Con el tope alcanzado la zapata queda en el mayor ancho de la
# grilla que no lo pasa, sus filas siguen sin cumplir y un aviso lo dice: no
# es una excepcion -- el cabezal esta calculado y la memoria muestra cuanto
# le falta --, es un resultado que no cumple.

from dataclasses import dataclass, field, replace  # noqa: E402
from typing import Dict, List  # noqa: E402


@dataclass(frozen=True)
class DimensionadoDeZapatas:
    """
    Lo que entrega `dimensionar_zapata_por_estabilidad`: el cabezal con la
    geometria FINAL (sin la estabilidad integrada: la evalua otra vez el
    servicio por su via de etapas), los anchos adoptados por extremo (solo
    los que cambiaron respecto de la regla), los intentos, los pasos de
    memoria y los avisos.
    """

    cabezal: CabezalDelPunto
    anchos: Dict[str, float]
    intentos: Tuple[IntentoDeZapata, ...]
    pasos: Tuple[PasoDeMemoria, ...]
    avisos: Tuple[str, ...]
    # --- VE-3.14 --- Las puntas que crecieron (H-5) y los extremos en los
    # que ninguna zapata corrida de la grilla cumple (H-6): NO FACTIBLE con
    # estos criterios; su peralte no se itera.
    puntas: Dict[str, float] = field(default_factory=dict)
    no_factibles: Tuple[str, ...] = ()


def extremos_a_dimensionar(cabezal: CabezalDelPunto,
                           estabilidades: Sequence[EstabilidadDelCabezal],
                           declarados: Optional[dict] = None
                           ) -> Tuple[str, ...]:
    """
    Los extremos cuyo ancho de zapata NO se declaro y cuya estabilidad
    EVALUADA no cumple (alguna fila que decide incumple). Un extremo sin
    ninguna condicion evaluada no se dimensiona: su bloqueo ya dice por que
    no hay estabilidad, y crecer la zapata a ciegas no la arregla.
    """
    declarados = declarados or {}
    extremos = []
    for g in cabezal.geometrias:
        if "ancho_zapata_m" in declarados.get(g.extremo, {}):
            continue
        propias = [e for e in estabilidades if e.extremo == g.extremo]
        if propias and not all(e.cumple for e in propias):
            extremos.append(g.extremo)
    return tuple(extremos)


def _regla_de_dimensionamiento() -> Tuple[float, float]:
    """
    'dimensionamiento_zapata_cabezal' [A]: (paso en m, fraccion del tope
    sobre H_c). Sin valor, `CriterioPendienteError`; campos ausentes o no
    positivos, `DatoInvalidoError` con la clave del criterio (segunda
    linea, como las reglas de 'predimensionamiento_cabezal').
    """
    regla = ca.valor(CRITERIO_DIMENSIONAMIENTO_ZAPATA)
    if not isinstance(regla, dict):
        raise DatoInvalidoError(CRITERIO_DIMENSIONAMIENTO_ZAPATA, valor=regla,
                                motivo="se espera el dict con 'paso_m' y "
                                       "'fraccion_ancho_max'")
    paso_m = _exigir_positivo(CRITERIO_DIMENSIONAMIENTO_ZAPATA,
                              regla.get("paso_m"),
                              "paso del ancho de la zapata ('paso_m')")
    fraccion = _exigir_positivo(CRITERIO_DIMENSIONAMIENTO_ZAPATA,
                                regla.get("fraccion_ancho_max"),
                                "tope del ancho sobre H_c "
                                "('fraccion_ancho_max')")
    return paso_m, fraccion


def _intento(extremo: str, B: float,
             estabilidades: Sequence[EstabilidadDelCabezal]) -> IntentoDeZapata:
    propias = [e for e in estabilidades if e.extremo == extremo]
    return IntentoDeZapata(
        extremo=extremo, B=B,
        condiciones=tuple(e.condicion.value for e in propias),
        incumplidas=tuple(v.codigo for e in propias
                          for v in e.verificaciones if not v.cumple))


def _estabilidades_evaluables(entornos, extremos) -> List[EstabilidadDelCabezal]:
    """
    La estabilidad de los `extremos` en las condiciones que se pueden
    evaluar. Lo que una condicion no puede evaluar (un dato del EMS,
    Mononobe-Okabe fuera de su dominio) NO detiene el dimensionamiento: se
    salta, y el servicio lo registra como `Bloqueo` cuando evalua la
    geometria final por su via de etapas.
    """
    evaluadas = []
    for entorno in entornos:
        if entorno.extremo not in extremos:
            continue
        for condicion in CONDICIONES_DE_ESTABILIDAD:
            try:
                evaluadas.append(ensamble_estabilidad(entorno, condicion))
            except ErrorProyecto:
                continue
    return evaluadas


def _texto_intentos(intentos: Sequence[IntentoDeZapata]) -> str:
    partes = []
    for i in intentos:
        if i.cumple:
            estado = "cumple"
        elif i.incumplidas:
            estado = "no cumplen " + ", ".join(i.incumplidas)
        else:
            estado = "ninguna condicion evaluable"
        punta = ("" if i.punta is None else f" (punta {i.punta:.3f} m)")
        marca = " [re-optimizado tras el peralte]" if i.reoptimizado else ""
        partes.append(f"{i.B:.3f} m{punta}{marca}: {estado}")
    return " -> ".join(partes)


def dimensionar_zapata_por_estabilidad(
        *, punto, resultado, geometria, embocadura,
        cabezal: CabezalDelPunto,
        estabilidades: Sequence[EstabilidadDelCabezal],
        socavacion=None, declarados: Optional[dict] = None,
        coherencia_embocadura: Optional[str] = None,
        motivo_sin_socavacion: str = "",
        suelo_del_punto: Optional[dict] = None,
        empuje_sismico: Optional[dict] = None,
        talud_delante: Optional[dict] = None,
        anchos_previos: Optional[dict] = None,
        espesores_por_armado: Optional[dict] = None,
        puntas_previas: Optional[dict] = None
        ) -> Optional[DimensionadoDeZapatas]:
    """
    --- VE-3.5 --- El ancho de la zapata de cada cabezal cuya estabilidad no
    cumple con la geometria de la regla, por intentos: B_k = B_regla +
    k·paso, el primero con el que todas las condiciones evaluadas cumplen
    E1 a E3 del marco que decide (AASHTO LRFD 11.6.3.2, 11.6.3.3 y
    11.6.3.6), sin pasar B_max = fraccion_ancho_max·H_c
    ('dimensionamiento_zapata_cabezal' [A]). Crece el talon.

    `cabezal` y `estabilidades` son los de la geometria de la regla (la
    partida, k = 0), ya evaluados por el servicio. Devuelve None si no hay
    nada que dimensionar (todo cumple, o el ancho de los extremos que no
    cumplen se declaro): en ese caso el criterio ni se lee. Lanza
    `CriterioPendienteError` si hay que dimensionar y el criterio no tiene
    valor.

    --- VE-3.9 --- `dimensionar_peralte_por_armado` la vuelve a llamar
    cuando un peralte mayor deja de cumplir la estabilidad: entonces
    `cabezal` ya trae los anchos dimensionados (la grilla sigue desde el
    ancho actual, que esta en ella), `anchos_previos` los conserva para el
    extremo que no se re-dimensiona y `espesores_por_armado` mantiene los
    peraltes que el armado hizo crecer.
    """
    extremos = extremos_a_dimensionar(cabezal, estabilidades, declarados)
    if not extremos:
        return None
    paso_m, fraccion = _regla_de_dimensionamiento()
    partida = {g.extremo: g for g in cabezal.geometrias}
    intentos = {e: [_intento(e, partida[e].B, estabilidades)]
                for e in extremos}
    anchos: Dict[str, float] = dict(anchos_previos or {})
    puntas: Dict[str, float] = dict(puntas_previas or {})
    vivos = list(extremos)
    final = cabezal
    k = 0
    while vivos:
        k += 1
        candidatos = {}
        for e in vivos:
            g0 = partida[e]
            tope = fraccion * (g0.H + g0.espesor_zapata)
            B = g0.B + k * paso_m
            if B > tope + TOL_UMBRAL_NORMATIVO:
                intentos[e][-1] = replace(intentos[e][-1], al_tope=True)
            else:
                candidatos[e] = B
        if not candidatos:
            break
        anchos.update(candidatos)
        final = cabezal_del_punto(
            punto=punto, resultado=resultado, geometria=geometria,
            embocadura=embocadura, socavacion=socavacion,
            declarados=declarados,
            coherencia_embocadura=coherencia_embocadura,
            motivo_sin_socavacion=motivo_sin_socavacion,
            anchos_por_estabilidad=dict(anchos),
            espesores_por_armado=espesores_por_armado,
            puntas_por_estabilidad=dict(puntas) or None)
        entornos = datos_del_cabezal_del_punto(
            punto=punto, cabezal=final, geometria=geometria,
            socavacion=socavacion, suelo_del_punto=suelo_del_punto,
            resultado=resultado, empuje_sismico=empuje_sismico,
            talud_delante=talud_delante)
        evaluadas = _estabilidades_evaluables(entornos, candidatos)
        vivos = []
        for e, B in candidatos.items():
            intento = _intento(e, B, evaluadas)
            intentos[e].append(intento)
            if not intento.cumple:
                vivos.append(e)
    # --- VE-3.14 (H-5 y H-6 de los ensayos de diseño del cabezal) --- SI
    # CON EL TALON AL TOPE NO CUMPLE, CRECE LA PUNTA. En suelo cohesivo el
    # portante no crece con B (no hay termino N_gamma) y alargar el talon
    # suma carga: el segundo pase hace crecer la punta (el talon vuelve al
    # de la regla) con el mismo paso y el mismo tope. Si tampoco cumple, la
    # zapata corrida es NO FACTIBLE con estos criterios: la geometria que
    # queda es la del pase del talon al tope, y el peralte no se itera (sin
    # estabilidad que cumplir, inflarlo no es diseño). Termina: cada pase
    # recorre a lo sumo (B_max - B_partida)/paso anchos.
    fallidos = [e for e in extremos if not intentos[e][-1].cumple]
    no_factibles: List[str] = []
    if fallidos:
        talon_al_tope = {e: anchos.get(e) for e in fallidos}
        punta_previa = {e: puntas.get(e) for e in fallidos}
        vivos = list(fallidos)
        k = 0
        while vivos:
            k += 1
            candidatos = {}
            for e in vivos:
                g0 = partida[e]
                tope = fraccion * (g0.H + g0.espesor_zapata)
                B = g0.B + k * paso_m
                if B <= tope + TOL_UMBRAL_NORMATIVO:
                    candidatos[e] = B
            if not candidatos:
                break
            for e, B in candidatos.items():
                anchos[e] = B
                puntas[e] = partida[e].ancho_punta + k * paso_m
            prueba = cabezal_del_punto(
                punto=punto, resultado=resultado, geometria=geometria,
                embocadura=embocadura, socavacion=socavacion,
                declarados=declarados,
                coherencia_embocadura=coherencia_embocadura,
                motivo_sin_socavacion=motivo_sin_socavacion,
                anchos_por_estabilidad=dict(anchos),
                espesores_por_armado=espesores_por_armado,
                puntas_por_estabilidad=dict(puntas))
            entornos = datos_del_cabezal_del_punto(
                punto=punto, cabezal=prueba, geometria=geometria,
                socavacion=socavacion, suelo_del_punto=suelo_del_punto,
                resultado=resultado, empuje_sismico=empuje_sismico,
            talud_delante=talud_delante)
            evaluadas = _estabilidades_evaluables(entornos, candidatos)
            vivos = []
            for e, B in candidatos.items():
                intento = replace(_intento(e, B, evaluadas), punta=puntas[e])
                intentos[e].append(intento)
                if not intento.cumple:
                    vivos.append(e)
        for e in fallidos:
            if not intentos[e][-1].cumple:
                no_factibles.append(e)
                if talon_al_tope[e] is None:
                    anchos.pop(e, None)
                else:
                    anchos[e] = talon_al_tope[e]
                if punta_previa[e] is None:
                    puntas.pop(e, None)
                else:
                    puntas[e] = punta_previa[e]
        final = cabezal_del_punto(
            punto=punto, resultado=resultado, geometria=geometria,
            embocadura=embocadura, socavacion=socavacion,
            declarados=declarados,
            coherencia_embocadura=coherencia_embocadura,
            motivo_sin_socavacion=motivo_sin_socavacion,
            anchos_por_estabilidad=dict(anchos) or None,
            espesores_por_armado=espesores_por_armado,
            puntas_por_estabilidad=dict(puntas) or None)
    pasos, avisos = [], []
    for e in extremos:
        g0 = partida[e]
        H_c = g0.H + g0.espesor_zapata
        tope = fraccion * H_c
        ultimo = intentos[e][-1]
        pasos.append(paso(
            "F9.DIMENSIONADO", codigo=f"9.3.d.{e[0]}",
            que=f"Ancho de la zapata del cabezal de {e}, dimensionado por "
                "estabilidad",
            formula=("B_k = B_regla + k·paso, k = 0, 1, 2, ...: el primer B_k "
                     "con el que E1 a E3 del marco que decide cumplen en "
                     "las condiciones evaluadas, con B_k <= B_max = "
                     "fraccion_ancho_max·H_c"),
            sustitucion=(
                (Magnitud("B_partida", g0.B, "m",
                          "ancho ya dimensionado por estabilidad, que el "
                          "peralte nuevo de la zapata (VE-3.9) dejo sin "
                          "cumplir: la grilla sigue desde el")
                 if e in (anchos_previos or {}) else
                 Magnitud("B_regla", g0.B, "m",
                          f"regla 'fraccion_ancho_zapata' de "
                          f"'{CRITERIO_GEOMETRIA}' [A]")),
                Magnitud("paso", paso_m, "m",
                         f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' "
                         "[A]"),
                Magnitud("B_max", tope, "m",
                         f"{fraccion:g}·H_c, H_c = {H_c:.3f} m, criterio "
                         f"'{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' [A]"),
            ),
            resultado=Magnitud(
                "B", (anchos.get(e, ultimo.B) if e in no_factibles
                      else ultimo.B), "m",
                ("dimensionada por estabilidad" if ultimo.cumple else
                 "ZAPATA CORRIDA NO FACTIBLE con estos criterios: ni el "
                 "talon ni la punta, creciendo hasta B_max, cumplen; queda "
                 "el mayor ancho de la grilla del talon")),
            nota_del_proyecto=(
                "Crece el talon; si con el talon al tope no cumple, crece la "
                "punta (el talon vuelve al de la regla). Intentos: "
                + _texto_intentos(intentos[e]))))
        if not ultimo.cumple:
            pendientes = (", ".join(ultimo.incumplidas)
                          or "condiciones sin evaluar")
            avisos.append(
                f"Cabezal de {e} de {punto.id}: ZAPATA CORRIDA NO FACTIBLE "
                f"con estos criterios: ni el talon ni la punta, creciendo "
                f"hasta el tope B_max = {tope:.3f} m ({fraccion:g}·H_c, "
                f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}'), hacen "
                f"cumplir {pendientes}; queda B = "
                f"{anchos.get(e, ultimo.B):.3f} m y el peralte no se itera. "
                "Ampliar el tope, añadir un dentellon de corte (y contar el "
                "pasivo, AASHTO 11.6.3.5), mejorar el suelo de fundacion o "
                "declarar la zapata (`cabezal_declarado`)")
    return DimensionadoDeZapatas(
        cabezal=final, anchos=anchos,
        intentos=tuple(i for e in extremos for i in intentos[e]),
        pasos=tuple(pasos), avisos=tuple(avisos), puntas=puntas,
        no_factibles=tuple(no_factibles))


def incorporar_dimensionado(cabezal: CabezalDelPunto,
                            dimensionado: DimensionadoDeZapatas
                            ) -> CabezalDelPunto:
    """El cabezal con los intentos, los pasos y los avisos del dimensionado."""
    from dataclasses import replace as _replace
    avisos = list(cabezal.avisos)
    avisos.extend(a for a in dimensionado.avisos if a not in avisos)
    return _replace(cabezal, intentos_de_zapata=dimensionado.intentos,
                    pasos=cabezal.pasos + dimensionado.pasos,
                    avisos=tuple(avisos))


# ===========================================================================
# --- VE-3.9 --- EL PERALTE DE LA ZAPATA, DIMENSIONADO POR SU ARMADO
# ===========================================================================
# Decision del dueño del 2026-11-17: con el talon que la estabilidad ensancha
# (VE-3.5), el peralte de la regla (H_c / divisor, o su piso) deja de
# alcanzar para armar la zapata -- en la corrida titular de la validacion
# integral fallaban A1 y A2 del talon en los ocho cabezales --. El peralte
# crece con el MISMO paso del criterio 'dimensionamiento_zapata_cabezal'
# hasta que el armado de la zapata cumple. Como el peralte cambia el peso y
# la distribucion de la zapata, la estabilidad se RE-VERIFICA con cada
# peralte y, si deja de cumplir, el ancho vuelve a crecer desde el actual.
#
# EL TOPE DEL PERALTE NO ES UN VALOR DE PROYECTO NUEVO: es el limite fisico
# que la geometria ya exige (`predimensionar_cabezal`: la zapata tiene que
# dejar pantalla sobre ella, H_c > e_z). Ninguna fuente de normas/ fija un
# peralte maximo (E.060 15.7 y AASHTO 5.12.8 dan minimos), y declarar uno
# seria rellenar un vacio; el bucle termina igual porque el peralte crece
# en pasos finitos hacia una cota finita.


@dataclass(frozen=True)
class DimensionadoDePeralte:
    """
    --- VE-3.9 --- Lo que `dimensionar_peralte_por_armado` entrega: el
    cabezal con la geometria final, los peraltes y los anchos dimensionados
    por extremo, los intentos de peralte, los intentos de ancho que la
    re-verificacion de la estabilidad añadio, los pasos de memoria (los del
    peralte y, si el ancho volvio a crecer, los del ancho que REEMPLAZAN a
    los de VE-3.5 de ese extremo) y los avisos.
    """

    cabezal: CabezalDelPunto
    espesores: Dict[str, float]
    anchos: Dict[str, float]
    intentos: Tuple[IntentoDePeralte, ...]
    intentos_de_ancho: Tuple[IntentoDeZapata, ...]
    pasos: Tuple[PasoDeMemoria, ...]
    pasos_de_ancho: Tuple[PasoDeMemoria, ...]
    avisos: Tuple[str, ...]
    # --- VE-3.14 --- Las puntas que la re-verificacion de la estabilidad
    # dejo (las de partida mas las que volvio a dimensionar).
    puntas: Dict[str, float] = field(default_factory=dict)


# Las filas del armado de la ZAPATA que deciden y que un peralte mayor
# puede hacer cumplir: flexion (A1), cortante sin estribos (A2), acero
# minimo (A3), espaciamiento de la barra propuesta (A4) y fisuracion en
# servicio (A6), de la punta y del talon. A5 (contraste con E.060) informa;
# A8 (altura sobre el refuerzo inferior) cumple por construccion desde la
# regla y solo mejora con el peralte.
FILAS_DEL_ARMADO_DE_LA_ZAPATA = ("A1", "A2", "A3", "A4", "A6")


# La marca del intento cuyo cortante queda FUERA de las condiciones en que
# AASHTO 5.7.3.4.1 permite el procedimiento simplificado (peralte >= 16 in y
# vuelo >= 3·d_v) y que el programa no puede verificar porque no implementa
# el general de 5.7.3.4.2. No es un incumplimiento: es un peralte que no se
# puede VERIFICAR. Un peralte mayor puede volver a serlo -- cuando el vuelo
# queda por debajo de 3·d_v --, y por eso el dimensionamiento sigue
# creciendo: adopta el primer peralte que puede verificar y que cumple, que
# es conservador frente a uno intermedio que con el general podria cumplir.
CORTANTE_NO_VERIFICABLE = "A2: fuera de 5.7.3.4.1, sin verificar"


def incumplidas_del_armado_de_la_zapata(entorno: EntornoDelCabezal
                                        ) -> Optional[Tuple[str, ...]]:
    """
    Los codigos de las filas del armado de la zapata (punta y talon) que NO
    cumplen con la geometria del `entorno`; `(CORTANTE_NO_VERIFICABLE,)` si
    el cortante queda fuera del procedimiento simplificado de 5.7.3.4.1
    (un peralte mayor puede volver a ser verificable); o None si el armado
    no se puede evaluar por otra causa (un criterio del recubrimiento sin
    declarar...), que crecer el peralte no arregla: entonces el
    dimensionamiento no adivina, y el servicio registra el `Bloqueo` cuando
    arma la geometria final. El cabezal de gravedad no se arma: vacia.
    """
    if entorno.geometria.tipo == TIPO_GRAVEDAD:
        return ()
    try:
        sol = solicitaciones_de_resistencia(entorno)
        piezas = armar_elemento(entorno, ELEMENTO_ZAPATA, sol)
    except MetodoNoEvaluableError as exc:
        if exc.rotulo == MOTIVO_METODO_NO_EVALUABLE_ARMADO:
            return (CORTANTE_NO_VERIFICABLE,)
        return None
    except ErrorProyecto:
        return None
    return tuple(v.codigo for p in piezas for v in p.verificaciones
                 if not v.cumple
                 and (v.codigo or "").split(".")[0]
                 in FILAS_DEL_ARMADO_DE_LA_ZAPATA)


def _texto_intentos_de_peralte(intentos: Sequence[IntentoDePeralte]) -> str:
    partes = []
    for i in intentos:
        estado = ("cumple" if i.cumple
                  else "no cumplen " + ", ".join(i.incumplidas))
        if i.ancho_redimensionado:
            estado += f" (el ancho volvio a crecer: B = {i.B:.3f} m)"
        partes.append(f"{i.espesor_zapata:.3f} m: {estado}")
    return " -> ".join(partes)


def dimensionar_peralte_por_armado(
        *, punto, resultado, geometria, embocadura,
        cabezal: CabezalDelPunto,
        socavacion=None, declarados: Optional[dict] = None,
        coherencia_embocadura: Optional[str] = None,
        motivo_sin_socavacion: str = "",
        suelo_del_punto: Optional[dict] = None,
        empuje_sismico: Optional[dict] = None,
        talud_delante: Optional[dict] = None,
        anchos: Optional[dict] = None,
        puntas: Optional[dict] = None,
        no_factibles: Sequence[str] = ()
        ) -> Optional[DimensionadoDePeralte]:
    """
    --- VE-3.9 --- El peralte de la zapata de cada cabezal de voladizo cuyo
    armado de la zapata (punta y talon: A1 a A4 y A6, AASHTO LRFD 5.6.3,
    5.7.3.3, 5.6.3.3, 5.10.3.2 y 5.6.7) no cumple con la geometria que llega
    -- la de la regla o la que la estabilidad dimensiono --, por intentos:
    e_z,k = e_z,0 + k·paso ('dimensionamiento_zapata_cabezal' [A], el mismo
    paso del ancho), el primero con el que esas filas cumplen, con e_z < H_c
    (la zapata deja pantalla sobre ella).

    CON CADA PERALTE SE RE-VERIFICA LA ESTABILIDAD: si deja de cumplir, el
    ancho vuelve a crecer desde el actual (`dimensionar_zapata_por_estabilidad`
    con `anchos_previos`). EL BUCLE TERMINA: en cada vuelta el peralte de
    cada extremo vivo crece un paso o el extremo sale (cumple, llega a H_c o
    su armado deja de ser evaluable), y el ancho solo crece, dentro de su
    tope; las dos sucesiones son monotonas y acotadas, de modo que hay a lo
    sumo ceil(H_c / paso) vueltas por extremo.

    Un peralte DECLARADO (`cabezal_declarado`) gana y no se itera; el
    cabezal de gravedad no se arma y no se itera. Devuelve None si no hay
    nada que dimensionar; en ese caso el criterio ni se lee.
    """
    declarados = declarados or {}
    anchos = dict(anchos or {})
    puntas = dict(puntas or {})
    no_factibles = set(no_factibles)

    def entornos_de(cab):
        return {e.extremo: e for e in datos_del_cabezal_del_punto(
            punto=punto, cabezal=cab, geometria=geometria,
            socavacion=socavacion, suelo_del_punto=suelo_del_punto,
            resultado=resultado, empuje_sismico=empuje_sismico,
            talud_delante=talud_delante)}

    entornos = entornos_de(cabezal)
    estado = {}
    for g in cabezal.geometrias:
        if "espesor_zapata_m" in declarados.get(g.extremo, {}):
            continue
        # --- VE-3.14 (H-6) --- Sin una zapata corrida que cumpla la
        # estabilidad, inflar el peralte no es diseño: no se itera.
        if g.extremo in no_factibles:
            continue
        entorno = entornos.get(g.extremo)
        if entorno is None:
            continue
        incumplidas = incumplidas_del_armado_de_la_zapata(entorno)
        if incumplidas:
            estado[g.extremo] = incumplidas
    if not estado:
        return None
    paso_m, _fraccion = _regla_de_dimensionamiento()
    partida = {g.extremo: g for g in cabezal.geometrias}
    intentos = {e: [IntentoDePeralte(
        extremo=e, espesor_zapata=partida[e].espesor_zapata,
        B=partida[e].B, incumplidas=inc)] for e, inc in estado.items()}
    espesores: Dict[str, float] = {}
    intentos_de_ancho: List[IntentoDeZapata] = []
    pasos_de_ancho: Dict[str, PasoDeMemoria] = {}
    avisos_de_ancho: List[str] = []
    final = cabezal
    vivos = list(estado)
    while vivos:
        actuales = {g.extremo: g for g in final.geometrias}
        for e in list(vivos):
            g = actuales[e]
            nuevo = g.espesor_zapata + paso_m
            if not nuevo < g.H + g.espesor_zapata - TOL_UMBRAL_NORMATIVO:
                intentos[e][-1] = replace(intentos[e][-1], al_tope=True)
                vivos.remove(e)
            else:
                espesores[e] = nuevo
        if not vivos:
            break
        final = cabezal_del_punto(
            punto=punto, resultado=resultado, geometria=geometria,
            embocadura=embocadura, socavacion=socavacion,
            declarados=declarados,
            coherencia_embocadura=coherencia_embocadura,
            motivo_sin_socavacion=motivo_sin_socavacion,
            anchos_por_estabilidad=dict(anchos) or None,
            espesores_por_armado=dict(espesores),
            puntas_por_estabilidad=dict(puntas) or None)
        # La estabilidad con el peralte nuevo: si deja de cumplir, el ancho
        # vuelve a crecer desde el actual.
        entornos = entornos_de(final)
        evaluadas = _estabilidades_evaluables(list(entornos.values()), vivos)
        redimensionados = set()
        dim = dimensionar_zapata_por_estabilidad(
            punto=punto, resultado=resultado, geometria=geometria,
            embocadura=embocadura, cabezal=final, estabilidades=evaluadas,
            socavacion=socavacion, declarados=declarados,
            coherencia_embocadura=coherencia_embocadura,
            motivo_sin_socavacion=motivo_sin_socavacion,
            suelo_del_punto=suelo_del_punto, anchos_previos=anchos,
            empuje_sismico=empuje_sismico, talud_delante=talud_delante,
            espesores_por_armado=espesores, puntas_previas=puntas)
        if dim is not None:
            redimensionados = {i.extremo for i in dim.intentos}
            anchos.update(dim.anchos)
            puntas.update(dim.puntas)
            no_factibles.update(dim.no_factibles)
            final = dim.cabezal
            entornos = entornos_de(final)
            intentos_de_ancho.extend(dim.intentos)
            for p in dim.pasos:
                pasos_de_ancho[p.codigo] = p
            avisos_de_ancho.extend(dim.avisos)
        actuales = {g.extremo: g for g in final.geometrias}
        siguen = []
        for e in vivos:
            if e in no_factibles:
                # --- VE-3.14 (H-6) --- la re-verificacion llego al tope
                # sin estabilidad: el peralte deja de crecer.
                intentos[e].append(IntentoDePeralte(
                    extremo=e, espesor_zapata=actuales[e].espesor_zapata,
                    B=actuales[e].B,
                    incumplidas=("estabilidad: zapata corrida no factible "
                                 "al tope",),
                    ancho_redimensionado=e in redimensionados))
                continue
            incumplidas = incumplidas_del_armado_de_la_zapata(entornos[e])
            # Un armado que deja de ser evaluable con este peralte no se
            # da por bueno: el intento lo dice y el extremo sale del bucle
            # (el servicio registra el `Bloqueo` al armar la geometria final).
            intentos[e].append(IntentoDePeralte(
                extremo=e, espesor_zapata=actuales[e].espesor_zapata,
                B=actuales[e].B,
                incumplidas=(("armado no evaluable",) if incumplidas is None
                             else incumplidas),
                ancho_redimensionado=e in redimensionados))
            if incumplidas:
                siguen.append(e)
        vivos = siguen
    # --- VE-3.14 (H-12 de los ensayos de diseño del cabezal) --- EL ANCHO
    # SE RE-OPTIMIZA TRAS EL PERALTE. El ancho se dimensiono con la zapata
    # delgada; con el peralte final (mas pesada) puede bastar uno menor. Se
    # prueba B - paso, B - 2·paso, ... mientras la estabilidad evaluada y el
    # armado de la zapata sigan cumpliendo y el talon quede positivo.
    # Termina: el ancho solo baja, en pasos finitos, hacia una cota finita.
    for e in [x for x in estado if x in espesores and x in anchos
              and x not in no_factibles]:
        B_antes = anchos[e]
        while True:
            actual = {g.extremo: g for g in final.geometrias}[e]
            B_menor = anchos[e] - paso_m
            # El talon no puede quedar negativo; la estabilidad decide el
            # resto (con la zapata delgada no bastaba el ancho de la regla).
            if not B_menor - actual.ancho_punta - actual.espesor_base_muro \
                    > TOL_UMBRAL_NORMATIVO:
                break
            prueba_anchos = dict(anchos, **{e: B_menor})
            prueba = cabezal_del_punto(
                punto=punto, resultado=resultado, geometria=geometria,
                embocadura=embocadura, socavacion=socavacion,
                declarados=declarados,
                coherencia_embocadura=coherencia_embocadura,
                motivo_sin_socavacion=motivo_sin_socavacion,
                anchos_por_estabilidad=prueba_anchos,
                espesores_por_armado=dict(espesores),
                puntas_por_estabilidad=dict(puntas) or None)
            entornos_p = entornos_de(prueba)
            evaluadas = _estabilidades_evaluables(list(entornos_p.values()),
                                                  [e])
            intento = replace(_intento(e, B_menor, evaluadas),
                              reoptimizado=True)
            armado = incumplidas_del_armado_de_la_zapata(entornos_p[e])
            if armado:
                intento = replace(intento, incumplidas=intento.incumplidas
                                  + tuple(armado))
            intentos_de_ancho.append(intento)
            if not intento.cumple:
                break
            anchos[e] = B_menor
            final = prueba
        if anchos[e] < B_antes - TOL_UMBRAL_NORMATIVO:
            pasos_de_ancho[f"9.3.d.{e[0]}"] = paso(
                "F9.DIMENSIONADO", codigo=f"9.3.d.{e[0]}",
                que=f"Ancho de la zapata del cabezal de {e}, dimensionado "
                    "por estabilidad y re-optimizado tras el peralte",
                formula=("con el peralte final, B_j = B - j·paso mientras "
                         "E1 a E3 y el armado de la zapata sigan cumpliendo "
                         "(con el talon positivo)"),
                sustitucion=(
                    Magnitud("B_con_zapata_delgada", B_antes, "m",
                             "el ancho que la estabilidad pidio con el "
                             "peralte de la regla"),
                    Magnitud("paso", paso_m, "m",
                             f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}'"
                             " [A]"),
                    Magnitud("e_z", espesores[e], "m",
                             "peralte final, dimensionado por armado"),
                ),
                resultado=Magnitud("B", anchos[e], "m",
                                   "dimensionada por estabilidad, "
                                   "re-optimizada tras el peralte"),
                nota_del_proyecto=(
                    "La zapata mas gruesa pesa mas y basta un ancho menor "
                    "(VE-3.14, H-12 de los ensayos de diseño del cabezal). "
                    "Intentos: " + _texto_intentos(
                        [i for i in intentos_de_ancho if i.extremo == e
                         and i.reoptimizado])))
    pasos, avisos = [], []
    for e in estado:
        g0 = partida[e]
        H_c = g0.H + g0.espesor_zapata
        ultimo = intentos[e][-1]
        pasos.append(paso(
            "F9.DIMENSIONADO_PERALTE", codigo=f"9.3.p.{e[0]}",
            que=f"Peralte de la zapata del cabezal de {e}, dimensionado por "
                "su armado",
            formula=("e_z,k = e_z,0 + k·paso, k = 0, 1, 2, ...: el primer "
                     "e_z,k con el que la flexion, el cortante sin estribos, "
                     "el acero minimo, el espaciamiento y la fisuracion de la "
                     "punta y del talon cumplen, con e_z,k < H_c; con cada "
                     "e_z,k se re-verifica la estabilidad"),
            sustitucion=(
                Magnitud("e_z,0", g0.espesor_zapata, "m",
                         f"peralte de la regla de '{CRITERIO_GEOMETRIA}' "
                         "[A] o su piso"),
                Magnitud("paso", paso_m, "m",
                         f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' "
                         "[A], el mismo paso del ancho"),
                Magnitud("H_c", H_c, "m",
                         "altura total del cabezal, de las cotas: el peralte "
                         "tiene que dejar pantalla sobre la zapata"),
            ),
            resultado=Magnitud(
                "e_z", ultimo.espesor_zapata, "m",
                ("dimensionada por armado" if ultimo.cumple else
                 "el mayor peralte probado: el armado de la zapata NO "
                 "cumple")),
            nota_del_proyecto=(
                "El tope del peralte es el fisico (H_c), no un valor de "
                "proyecto: ninguna fuente fija un peralte maximo. Un peralte "
                "de 16 in o mas cuyo vuelo es de 3·d_v o mas queda fuera del "
                "cortante simplificado de AASHTO 5.7.3.4.1 y desde VE-3.14 "
                "lo verifica el procedimiento general (5.7.3.4.2). Tras el "
                "peralte, el ancho se re-optimiza hacia abajo mientras todo "
                "siga cumpliendo. Intentos: "
                + _texto_intentos_de_peralte(intentos[e]))))
        if not ultimo.cumple:
            avisos.append(
                f"Cabezal de {e} de {punto.id}: el peralte de la zapata "
                f"crecio hasta {ultimo.espesor_zapata:.3f} m sin que su "
                f"armado cumpla ({', '.join(ultimo.incumplidas)}): revisar "
                "la geometria (la pantalla, el talon o un dentellon) o "
                "declarar la zapata (`cabezal_declarado`)")
    avisos.extend(a for a in avisos_de_ancho if a not in avisos)
    return DimensionadoDePeralte(
        cabezal=final, espesores=espesores, anchos=anchos,
        intentos=tuple(i for e in estado for i in intentos[e]),
        intentos_de_ancho=tuple(intentos_de_ancho), pasos=tuple(pasos),
        pasos_de_ancho=tuple(pasos_de_ancho.values()),
        avisos=tuple(avisos), puntas=dict(puntas))


def incorporar_peralte(cabezal: CabezalDelPunto,
                       dimensionado: DimensionadoDePeralte
                       ) -> CabezalDelPunto:
    """
    El cabezal con los intentos de peralte, los pasos (los del ancho que la
    re-verificacion volvio a dimensionar REEMPLAZAN a los de VE-3.5 con el
    mismo codigo) y los avisos.
    """
    from dataclasses import replace as _replace
    nuevos = {p.codigo for p in dimensionado.pasos_de_ancho}
    pasos = tuple(p for p in cabezal.pasos if p.codigo not in nuevos)
    avisos = list(cabezal.avisos)
    avisos.extend(a for a in dimensionado.avisos if a not in avisos)
    return _replace(
        cabezal,
        intentos_de_zapata=(cabezal.intentos_de_zapata
                            + dimensionado.intentos_de_ancho),
        intentos_de_peralte=dimensionado.intentos,
        pasos=pasos + dimensionado.pasos_de_ancho + dimensionado.pasos,
        avisos=tuple(avisos))


# ===========================================================================
# --- VE-3.14 --- LA PANTALLA Y LOS ALEROS, DIMENSIONADOS POR SU ARMADO
# ===========================================================================
# H-1 de los ensayos de diseño del cabezal: la pantalla quedaba en el espesor
# de la regla ('espesor_pantalla_voladizo_m', 0.30 m) para cualquier altura,
# y su armado (y el del alero, que hereda el espesor de la corona) no
# cumplia desde H_c ≈ 3 m: la app entregaba un cabezal que no se podia
# construir. Hoy el espesor de la pantalla -- uniforme, corona y arranque --
# crece con el MISMO paso de 'dimensionamiento_zapata_cabezal' hasta que el
# armado de la pantalla y de los aleros cumple. La zapata crece lo mismo
# (la punta y el talon no cambian: el peso solo aumenta), y con cada espesor
# se re-verifican la estabilidad y el armado de la zapata.
#
# EL TOPE ES FISICO, no un valor de proyecto: la pantalla no puede ser mas
# gruesa que alta (H_c - e_z); ninguna fuente fija un espesor maximo.

FILAS_DEL_ARMADO_DE_LA_PANTALLA = FILAS_DEL_ARMADO_DE_LA_ZAPATA


def _incumplidas_del_elemento(entorno: EntornoDelCabezal, elemento: str
                              ) -> Optional[Tuple[str, ...]]:
    """Las filas A1 a A4 y A6 de UN elemento que no cumplen, o None."""
    if entorno.geometria.tipo == TIPO_GRAVEDAD:
        return ()
    try:
        sol = solicitaciones_de_resistencia(entorno)
        piezas = list(armar_elemento(entorno, elemento, sol))
    except ErrorProyecto:
        return None
    return tuple(v.codigo for p in piezas for v in p.verificaciones
                 if not v.cumple
                 and (v.codigo or "").split(".")[0]
                 in FILAS_DEL_ARMADO_DE_LA_PANTALLA)


def incumplidas_del_armado_de_la_pantalla(entorno: EntornoDelCabezal
                                          ) -> Optional[Tuple[str, ...]]:
    """
    --- VE-3.14 --- Los codigos de las filas del armado de la PANTALLA (A1 a
    A4 y A6) que no cumplen con la geometria del `entorno`, o None si el
    armado no se puede evaluar (crecer el espesor no lo arregla: el servicio
    registra el `Bloqueo` al armar la geometria final). El cabezal de
    gravedad no se arma: vacia. Hasta VE-6 traia tambien las del alero, que
    heredaba el espesor de la pantalla; desde VE-6 el alero se dimensiona
    por las suyas (`incumplidas_del_armado_del_alero`).
    """
    return _incumplidas_del_elemento(entorno, ELEMENTO_PANTALLA)


def incumplidas_del_armado_del_alero(entorno: EntornoDelCabezal
                                     ) -> Optional[Tuple[str, ...]]:
    """
    --- VE-6 (ficha VE6M9-03) --- Lo mismo para las dos secciones del ALERO
    (`armar_elemento`, arranque y mitad), con las que su espesor se
    dimensiona sin copiar el de la pantalla. Vacia sin aleros.
    """
    return _incumplidas_del_elemento(entorno, ELEMENTO_ALEROS)


@dataclass(frozen=True)
class DimensionadoDePantalla:
    """--- VE-3.14 --- El cabezal con la pantalla dimensionada y su traza."""

    cabezal: CabezalDelPunto
    espesores: Dict[str, float]
    intentos: Tuple[str, ...]
    pasos: Tuple[PasoDeMemoria, ...]
    avisos: Tuple[str, ...]
    # --- VE-6 --- el espesor de los aleros que su PROPIO armado hizo crecer
    espesores_aleros: Dict[str, float] = field(default_factory=dict)


def dimensionar_pantalla_por_armado(
        *, punto, resultado, geometria, embocadura,
        cabezal: CabezalDelPunto,
        socavacion=None, declarados: Optional[dict] = None,
        coherencia_embocadura: Optional[str] = None,
        motivo_sin_socavacion: str = "",
        suelo_del_punto: Optional[dict] = None,
        empuje_sismico: Optional[dict] = None,
        talud_delante: Optional[dict] = None,
        anchos: Optional[dict] = None, puntas: Optional[dict] = None,
        espesores_zapata: Optional[dict] = None
        ) -> Optional[DimensionadoDePantalla]:
    """
    --- VE-3.14 (H-1) --- El espesor de la pantalla (uniforme) de cada
    cabezal de voladizo cuyo armado de la pantalla o de los aleros (A1 a A4
    y A6, AASHTO LRFD 5.6.3, 5.7.3.3, 5.6.3.3, 5.10.3.2 y 5.6.7) no cumple:
    e_k = e_0 + k·paso ('dimensionamiento_zapata_cabezal' [A], el mismo paso
    de la zapata), el primero con el que esas filas cumplen, con e_k < H (la
    pantalla no puede ser mas gruesa que alta). La zapata crece lo mismo
    (punta y talon fijos). Con cada espesor se re-verifican la estabilidad
    y el armado de la zapata: si dejaran de cumplir, el extremo se detiene y
    lo dice. Termina: el espesor solo crece, en pasos finitos, hacia H.

    Un espesor DECLARADO (corona o arranque) gana y no se itera; el cabezal
    de gravedad no se arma. Devuelve None si no hay nada que dimensionar.

    --- VE-6 (ficha VE6M9-03) --- La pantalla crece por SU armado (A1 a A4 y
    A6 de la pantalla) y, despues, el ALERO por el suyo (sus dos secciones,
    `incumplidas_del_armado_del_alero`), con el mismo paso y con tope fisico
    en su altura: hasta VE-6 el alero heredaba el espesor de la pantalla. El
    espesor del alero no entra en la estabilidad del cabezal ni en su
    zapata, de modo que su crecimiento no las re-verifica. Un
    `espesor_aleros_m` declarado gana y no se itera.
    """
    declarados = declarados or {}

    def construir(pantallas, aleros_esp=None):
        return cabezal_del_punto(
            punto=punto, resultado=resultado, geometria=geometria,
            embocadura=embocadura, socavacion=socavacion,
            declarados=declarados,
            coherencia_embocadura=coherencia_embocadura,
            motivo_sin_socavacion=motivo_sin_socavacion,
            anchos_por_estabilidad=dict(anchos or {}) or None,
            espesores_por_armado=dict(espesores_zapata or {}) or None,
            puntas_por_estabilidad=dict(puntas or {}) or None,
            pantallas_por_armado=dict(pantallas) or None,
            aleros_por_armado=dict(aleros_esp or {}) or None)

    def entornos_de(cab):
        return {e.extremo: e for e in datos_del_cabezal_del_punto(
            punto=punto, cabezal=cab, geometria=geometria,
            socavacion=socavacion, suelo_del_punto=suelo_del_punto,
            resultado=resultado, empuje_sismico=empuje_sismico,
            talud_delante=talud_delante)}

    entornos = entornos_de(cabezal)
    estado = {}
    for g in cabezal.geometrias:
        propias = declarados.get(g.extremo, {})
        if "espesor_corona_m" in propias or "espesor_base_muro_m" in propias:
            continue
        entorno = entornos.get(g.extremo)
        if entorno is None:
            continue
        inc = incumplidas_del_armado_de_la_pantalla(entorno)
        if inc:
            estado[g.extremo] = inc
    paso_m, _fraccion = _regla_de_dimensionamiento()
    partida = {g.extremo: g for g in cabezal.geometrias}
    # Lo que la estabilidad y el armado de la zapata ya no cumplian con la
    # pantalla de partida (una zapata «no factible», por ejemplo) no detiene
    # el crecimiento: lo detiene lo que DEJA de cumplir al engrosarla.
    de_partida = (_estabilidades_evaluables(list(entornos.values()), estado)
                  if estado else None)
    base = {e: set(_intento(e, 0.0, de_partida).incumplidas)
            | set(incumplidas_del_armado_de_la_zapata(entornos[e]) or ())
            for e in estado}
    trazas = {e: [f"{partida[e].espesor_base_muro:.3f} m: no cumplen "
                  + ", ".join(inc)] for e, inc in estado.items()}
    pantallas: Dict[str, float] = {}
    final = cabezal
    vivos = list(estado)
    detenidos = {}
    while vivos:
        actuales = {g.extremo: g for g in final.geometrias}
        for e in list(vivos):
            g = actuales[e]
            nuevo = g.espesor_base_muro + paso_m
            if not nuevo < g.H - TOL_UMBRAL_NORMATIVO:
                detenidos[e] = (f"el espesor llego al tope fisico (la altura "
                                f"de la pantalla, {g.H:.3f} m)")
                vivos.remove(e)
            else:
                pantallas[e] = nuevo
        if not vivos:
            break
        final = construir(pantallas)
        entornos = entornos_de(final)
        evaluadas = _estabilidades_evaluables(list(entornos.values()), vivos)
        siguen = []
        for e in vivos:
            inc = incumplidas_del_armado_de_la_pantalla(entornos[e])
            est = _intento(e, 0.0, evaluadas)
            zap = incumplidas_del_armado_de_la_zapata(entornos[e])
            if inc is None:
                trazas[e].append(f"{pantallas[e]:.3f} m: armado no evaluable")
                detenidos[e] = "el armado dejo de ser evaluable"
                continue
            nuevas = sorted((set(est.incumplidas) | set(zap or ()))
                            - base[e])
            if nuevas:
                trazas[e].append(
                    f"{pantallas[e]:.3f} m: la estabilidad o el armado de la "
                    "zapata dejan de cumplir (" + ", ".join(nuevas) + ")")
                detenidos[e] = ("al engrosar la pantalla la estabilidad o el "
                                "armado de la zapata dejan de cumplir")
                continue
            if inc:
                trazas[e].append(f"{pantallas[e]:.3f} m: no cumplen "
                                 + ", ".join(inc))
                siguen.append(e)
            else:
                trazas[e].append(f"{pantallas[e]:.3f} m: cumple")
        vivos = siguen
    pasos, avisos = [], []
    actuales = {g.extremo: g for g in final.geometrias}
    for e in estado:
        g0 = partida[e]
        cumple = e not in detenidos
        pasos.append(paso(
            "F9.DIMENSIONADO_PANTALLA", codigo=f"9.3.m.{e[0]}",
            que=f"Espesor de la pantalla (y de los aleros) del cabezal de "
                f"{e}, dimensionado por su armado",
            formula=("e_k = e_0 + k·paso, k = 0, 1, 2, ...: el primer e_k con "
                     "el que la flexion, el cortante sin estribos, el acero "
                     "minimo, el espaciamiento y la fisuracion de la "
                     "pantalla y de los aleros cumplen, con e_k < H; la "
                     "zapata crece lo mismo (punta y talon fijos)"),
            sustitucion=(
                Magnitud("e_0", g0.espesor_base_muro, "m",
                         f"espesor de la pantalla de '{CRITERIO_GEOMETRIA}' "
                         "[A]"),
                Magnitud("paso", paso_m, "m",
                         f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' "
                         "[A], el mismo paso de la zapata"),
                Magnitud("H", g0.H, "m", "altura de la pantalla: tope "
                         "fisico del espesor"),
            ),
            resultado=Magnitud(
                "e", actuales[e].espesor_base_muro, "m",
                "dimensionada por armado" if cumple else
                "el mayor espesor probado: el armado de la pantalla o de los "
                "aleros NO cumple"),
            nota_del_proyecto=(
                "Intentos: " + " -> ".join(trazas[e]) + ". La zapata crece "
                "lo mismo que la pantalla, con la punta y el talon fijos: B "
                f"= {g0.B:.3f} + ({actuales[e].espesor_base_muro:.3f} - "
                f"{g0.espesor_base_muro:.3f}) = {actuales[e].B:.3f} m; la "
                "estabilidad y el armado de la zapata se re-verificaron con "
                "cada espesor.")))
        if not cumple:
            avisos.append(
                f"Cabezal de {e} de {punto.id}: el dimensionamiento de la "
                f"pantalla se detuvo en {actuales[e].espesor_base_muro:.3f} m "
                f"porque {detenidos[e]}: revisar la geometria o declarar el "
                "espesor (`cabezal_declarado`)")
    # --- VE-6 --- y el alero, por su propio armado, sobre la geometria con
    # la pantalla ya dimensionada.
    aleros_esp, intentos_al, pasos_al, avisos_al = _dimensionar_aleros(
        punto=punto, final=final, declarados=declarados,
        entornos_de=entornos_de,
        construir=lambda al: construir(pantallas, al), paso_m=paso_m)
    if not estado and not intentos_al:
        return None
    if aleros_esp:
        final = construir(pantallas, aleros_esp)
    return DimensionadoDePantalla(
        cabezal=final, espesores=pantallas,
        intentos=tuple(f"{e}: " + " -> ".join(trazas[e]) for e in estado)
        + intentos_al,
        pasos=tuple(pasos) + pasos_al, avisos=tuple(avisos) + avisos_al,
        espesores_aleros=aleros_esp)


def _dimensionar_aleros(*, punto, final: CabezalDelPunto, declarados: dict,
                        entornos_de, construir, paso_m: float
                        ) -> Tuple[Dict[str, float], Tuple[str, ...],
                                   Tuple[PasoDeMemoria, ...], Tuple[str, ...]]:
    """
    --- VE-6 (ficha VE6M9-03) --- El espesor del ALERO de cada cabezal de
    voladizo cuyo armado de sus dos secciones no cumple:
    e_k = e_0 + k·paso, el primero con el que cumplen, con e_k menor que la
    altura del alero sobre su zapata (tope fisico) y que el ancho de su
    zapata. Parte del espesor que la geometria trae (el de la regla, o el
    de la corona declarada); un `espesor_aleros_m` declarado gana y no se
    itera. Devuelve (espesores, intentos, pasos, avisos).
    """
    entornos = entornos_de(final)
    estado = {}
    for g in final.geometrias:
        if g.aleros is None or g.tipo == TIPO_GRAVEDAD:
            continue
        if "espesor_aleros_m" in declarados.get(g.extremo, {}):
            continue
        entorno = entornos.get(g.extremo)
        if entorno is None:
            continue
        inc = incumplidas_del_armado_del_alero(entorno)
        if inc:
            estado[g.extremo] = inc
    if not estado:
        return {}, (), (), ()
    partida = {g.extremo: g.aleros for g in final.geometrias
               if g.extremo in estado}
    alto = {g.extremo: g.altura_total - g.aleros.espesor_zapata
            for g in final.geometrias if g.extremo in estado}
    trazas = {e: [f"{partida[e].espesor:.3f} m: no cumplen "
                  + ", ".join(inc)] for e, inc in estado.items()}
    espesores: Dict[str, float] = {}
    detenidos = {}
    vivos = list(estado)
    while vivos:
        for e in list(vivos):
            actual = espesores.get(e, partida[e].espesor)
            nuevo = actual + paso_m
            tope = min(alto[e], partida[e].ancho_zapata)
            if not nuevo < tope - TOL_UMBRAL_NORMATIVO:
                detenidos[e] = (f"el espesor llego al tope fisico (la altura "
                                f"del alero sobre su zapata o el ancho de "
                                f"esta, {tope:.3f} m)")
                vivos.remove(e)
            else:
                espesores[e] = nuevo
        if not vivos:
            break
        entornos = entornos_de(construir(espesores))
        siguen = []
        for e in vivos:
            inc = incumplidas_del_armado_del_alero(entornos[e])
            if inc is None:
                trazas[e].append(f"{espesores[e]:.3f} m: armado no evaluable")
                detenidos[e] = "el armado del alero dejo de ser evaluable"
            elif inc:
                trazas[e].append(f"{espesores[e]:.3f} m: no cumplen "
                                 + ", ".join(inc))
                siguen.append(e)
            else:
                trazas[e].append(f"{espesores[e]:.3f} m: cumple")
        vivos = siguen
    pasos, avisos = [], []
    for e in estado:
        cumple = e not in detenidos
        e_final = espesores.get(e, partida[e].espesor)
        pasos.append(paso(
            "F9.DIMENSIONADO_PANTALLA", codigo=f"9.3.al.{e[0]}",
            que=f"Espesor de los aleros del cabezal de {e}, dimensionado por "
                "el armado de sus dos secciones (arranque y mitad)",
            formula=("e_k = e_0 + k·paso, k = 0, 1, 2, ...: el primer e_k con "
                     "el que la flexion, el cortante sin estribos, el acero "
                     "minimo, el espaciamiento y la fisuracion de las dos "
                     "secciones del alero cumplen, con e_k menor que su "
                     "altura y que el ancho de su zapata"),
            sustitucion=(
                Magnitud("e_0", partida[e].espesor, "m",
                         "espesor del alero de la geometria (regla o corona "
                         "declarada)"),
                Magnitud("paso", paso_m, "m",
                         f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' "
                         "[A], el mismo paso de la zapata"),
                Magnitud("altura", alto[e], "m", "del alero sobre su "
                         "zapata, en el arranque: tope fisico"),
            ),
            resultado=Magnitud(
                "e", e_final, "m",
                "dimensionado por armado" if cumple else
                "el mayor espesor probado: el armado del alero NO cumple"),
            nota_del_proyecto="Intentos: " + " -> ".join(trazas[e]) + "."))
        if not cumple:
            avisos.append(
                f"Cabezal de {e} de {punto.id}: el dimensionamiento de los "
                f"aleros se detuvo en {e_final:.3f} m porque {detenidos[e]}: "
                "revisar la geometria o declarar el espesor "
                "(`cabezal_declarado.espesor_aleros_m`)")
    return (espesores, tuple(f"{e} (aleros): " + " -> ".join(trazas[e])
                             for e in estado), tuple(pasos), tuple(avisos))


def rotular_estabilidad_incompleta(cabezal: CabezalDelPunto,
                                   estabilidades) -> CabezalDelPunto:
    """
    --- VE-3.14 (H-3) --- Las dimensiones «dimensionada por estabilidad» de
    un cabezal cuya geometria FINAL no pudo evaluar alguna condicion de
    estabilidad (su etapa lleva el `Bloqueo`) pasan a
    `ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA`, con la condicion que falta en
    la regla: el ancho se dimensiono con lo evaluable, no con todo.
    """
    from dataclasses import replace as _replace
    from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA
    nuevas = {}
    for g in cabezal.geometrias:
        evaluadas = {e.condicion for e in estabilidades
                     if e.extremo == g.extremo}
        faltan = [c.value for c in CONDICIONES_DE_ESTABILIDAD
                  if c not in evaluadas]
        if not faltan:
            continue
        dims = tuple(
            _replace(d, origen=ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA,
                     regla=(f"{d.regla}; SIN la condicion "
                            f"{', '.join(faltan)}, que no se pudo evaluar "
                            "(ver su bloqueo)"))
            if d.origen == ORIGEN_DIMENSION_ESTABILIDAD else d
            for d in g.dimensiones)
        if dims != g.dimensiones:
            nuevas[g.extremo] = _replace(g, dimensiones=dims)
    if not nuevas:
        return cabezal
    return _replace(cabezal, entrada=nuevas.get("entrada", cabezal.entrada),
                    salida=nuevas.get("salida", cabezal.salida))


def incorporar_pantalla(cabezal: CabezalDelPunto,
                        dimensionado: DimensionadoDePantalla
                        ) -> CabezalDelPunto:
    """El cabezal con los pasos y los avisos del dimensionado de la pantalla."""
    from dataclasses import replace as _replace
    avisos = list(cabezal.avisos)
    avisos.extend(a for a in dimensionado.avisos if a not in avisos)
    return _replace(cabezal, pasos=cabezal.pasos + dimensionado.pasos,
                    intentos_de_pantalla=dimensionado.intentos,
                    avisos=tuple(avisos))
