# -*- coding: utf-8 -*-
"""
M9_cabezal.alero
================
Submodulo de Fase 9 (`M9_cabezal`): bloque `alero` (D1).
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from dataclasses import (
    dataclass,
    replace,
    replace as _reemplazar,
)
from src.modelos import (
    ArmadoDelCabezal,
    CIFRAS_MAGNITUD,
    CabezalDelPunto,
    CondicionAnalisis,
    DatoInvalidoError,
    DimensionDeCabezal,
    ELEMENTO_ZAPATA_ALEROS,
    EntornoDelCabezal,
    ErrorProyecto,
    EstabilidadDelCabezal,
    GeometriaCabezal,
    IntentoDeZapata,
    MURO_ALERO,
    Magnitud,
    ORIGEN_DIMENSION_ARMADO,
    ORIGEN_DIMENSION_ESTABILIDAD,
    PasoDeMemoria,
    paso,
)
from src.tolerancias import (
    FRACCIONES_DE_ESTABILIDAD_DEL_ALERO,
    TOL_UMBRAL_NORMATIVO,
)

from src.modulos.M9_cabezal._criterios import (
    CONDICIONES_DE_ESTABILIDAD,
    CRITERIO_DIMENSIONAMIENTO_ZAPATA,
    CRITERIO_FORMA_PROFUNDIDAD,
    FORMA_CORRIDA,
    FRACCION_ARRANQUE_ALERO,
    OPCIONES_FORMA_PROFUNDIDAD,
    SUFIJO_ALERO,
    TIPO_GRAVEDAD,
    _rotulo_de_la_franja,
    sufijo_de_la_franja,
)
from src.modulos.M9_cabezal.armado import (
    _EntornoMinimo,
    alero_verificable_como_muro,
    altura_del_fuste_del_alero,
    armar_elemento,
    fracciones_del_alero,
    franja_del_alero,
    franja_del_arranque_del_alero,
)
from src.modulos.M9_cabezal.armado_secciones import _aviso_cabezal
from src.modulos.M9_cabezal.ciclopeo import verificar_cabezal_ciclopeo
from src.modulos.M9_cabezal.dimensionamiento import (
    FILAS_DEL_ARMADO_DE_LA_ZAPATA,
    _intento,
    _regla_de_dimensionamiento,
    _texto_intentos,
)
from src.modulos.M9_cabezal.estabilidad import ensamble_estabilidad
from src.modulos.M9_cabezal.estabilidad_cargas import _eleccion

DIMENSION_ZAPATA_ALEROS = "ancho de la zapata de los aleros"


DIMENSION_PERALTE_ZAPATA_ALEROS = "espesor de la zapata de los aleros"


# Las filas de la verificacion ciclopea del CABEZAL que no se repiten en el
# alero: el material (es el mismo concreto) y el aviso del vano.
FILAS_CICLOPEAS_SOLO_DEL_CABEZAL = ("C4", "C5")


def _lecturas_de_la_forma(franja: EntornoDelCabezal
                          ) -> Tuple[EntornoDelCabezal, ...]:
    """
    --- VE-7 (dictamen Fable, abierto (b)) --- Las lecturas de la zapata de
    la franja para la capacidad portante (AASHTO 10.6.3.1.1 y la Tabla
    10.6.3.1.2a-3): con la zapata corrida de archivo, una; con forma
    declarada, la zapata corrida (L infinita, s = 1) y la de L = longitud
    del alero corto, de las que rige la de menor resistencia.
    """
    forma = _eleccion(CRITERIO_FORMA_PROFUNDIDAD, OPCIONES_FORMA_PROFUNDIDAD)
    g = franja.geometria
    corrida = _reemplazar(franja, geometria=_reemplazar(g, longitud=math.inf))
    if forma == FORMA_CORRIDA:
        return (franja,)
    if g.longitud is None:
        return (corrida,)
    return (franja, corrida)


def _portante_de_menor_resistencia(lecturas: Sequence[EstabilidadDelCabezal]
                                   ) -> EstabilidadDelCabezal:
    """La primera lectura con, fila por fila de la capacidad portante (E1),
    la de menor resistencia de todas; las demas filas no dependen de L."""
    base = lecturas[0]
    if len(lecturas) == 1:
        return base
    nuevas = []
    for v in base.verificaciones:
        if not (v.codigo or "").startswith("E1-"):
            nuevas.append(v)
            continue
        otras = [w for e in lecturas for w in e.verificaciones
                 if w.codigo == v.codigo]
        rige = min(otras, key=lambda w: w.valor_admisible)
        nota = ((rige.paso.nota_del_proyecto or "") + " Franja del alero: "
                "rige la lectura de MENOR resistencia de la zapata corrida y "
                "de la de L = longitud del alero corto (AASHTO 10.6.3.1.2a, "
                "Tabla 10.6.3.1.2a-3); la L del cabezal no se usa.")
        nuevas.append(_reemplazar(rige, paso=_reemplazar(
            rige.paso, nota_del_proyecto=nota.strip())))
    return _reemplazar(base, verificaciones=tuple(nuevas))


def estabilidad_del_alero(entorno: EntornoDelCabezal,
                          condicion: CondicionAnalisis,
                          fraccion: float = FRACCION_ARRANQUE_ALERO
                          ) -> EstabilidadDelCabezal:
    """
    --- VE-7 (ficha VE7-01) --- E1 a E3 de AASHTO LRFD 11.6 (11.6.3.2,
    11.6.3.3, 11.6.3.6 y, bajo sismo, 11.6.5) de los aleros del cabezal del
    `entorno`, en UNA condicion, sobre la franja a la `fraccion` de su
    longitud (`franja_del_alero`), con el ensamble del cabezal y codigos
    `<fila>.<condicion>.<extremo>` + `sufijo_de_la_franja`. Con forma
    declarada en el portante, rige la menor de las dos lecturas de la
    zapata (`_lecturas_de_la_forma`). Se detiene como el del cabezal
    (`ErrorProyecto`) en lo que falte.
    """
    lecturas = [ensamble_estabilidad(f, condicion, muro=MURO_ALERO,
                                     fraccion_alero=fraccion)
                for f in _lecturas_de_la_forma(franja_del_alero(entorno,
                                                                fraccion))]
    return _portante_de_menor_resistencia(lecturas)


def _estabilidad_evaluable_del_alero(entorno: EntornoDelCabezal
                                     ) -> List[EstabilidadDelCabezal]:
    """Todas las franjas con fuste y condiciones que se pueden evaluar; lo
    demas lo bloquea el servicio al evaluar la geometria final (como
    `_estabilidades_evaluables` del cabezal)."""
    evaluadas = []
    for fraccion in fracciones_del_alero(entorno)[0]:
        for condicion in CONDICIONES_DE_ESTABILIDAD:
            try:
                evaluadas.append(estabilidad_del_alero(entorno, condicion,
                                                       fraccion))
            except ErrorProyecto:
                continue
    return evaluadas


def entorno_con_zapata_de_alero(entorno: EntornoDelCabezal, **cambios
                         ) -> EntornoDelCabezal:
    g = entorno.geometria
    return _reemplazar(entorno, geometria=_reemplazar(
        g, aleros=_reemplazar(g.aleros, **cambios)))


def paso_de_las_franjas_del_alero(entorno: EntornoDelCabezal
                                  ) -> PasoDeMemoria:
    """
    --- VE-7 --- El paso que dice en que franjas se verifico el alero como
    muro y cuales no tienen fuste (no se verifican: no es un bloqueo).
    """
    con, sin = fracciones_del_alero(entorno)
    g = entorno.geometria
    return paso(
        "F9.DIMENSIONES", codigo=f"9.3.f.{entorno.extremo[0]}{SUFIJO_ALERO}",
        que=(f"Franjas de los aleros del cabezal de {entorno.extremo} que se "
             "verifican como muro"),
        formula=("H(f) = H_c - e_z,alero - (h0 - H_f)·f, f en "
                 + ", ".join(f"{f:g}" for f in
                             FRACCIONES_DE_ESTABILIDAD_DEL_ALERO)
                 + "; se verifica la franja con H(f) > 0"),
        sustitucion=tuple(
            Magnitud(f"H({f:g})", altura_del_fuste_del_alero(g, f), "m",
                     "con fuste: se verifica" if f in con else
                     "SIN fuste: no hay muro que verificar",
                     cifras=CIFRAS_MAGNITUD)
            for f in FRACCIONES_DE_ESTABILIDAD_DEL_ALERO),
        resultado=Magnitud("franjas verificadas", len(con), "",
                           ("todas" if not sin else
                            "sin fuste: " + ", ".join(f"{f:g}·L"
                                                      for f in sin))),
        nota_del_proyecto=(
            "Con el borde de la plataforma fijo, el relleno sube mas detras "
            "de cada franja hacia la punta y la pendiente equivalente crece "
            "(AASHTO 3.11.5.8.1, C3.11.5.8.1-1): la franja del arranque no "
            "rige siempre, y se verifican todas. La discretizacion es "
            "`FRACCIONES_DE_ESTABILIDAD_DEL_ALERO`."))


@dataclass(frozen=True)
class DimensionadoDeZapataDelAlero:
    """
    --- VE-7 --- Lo que `dimensionar_zapata_del_alero` entrega para UN
    cabezal: el ancho adoptado de la zapata de los aleros (el primero de la
    grilla con el que cumplen todas las franjas o, al tope, el mayor
    probado), si cumple, si llego al tope, los intentos, el paso de memoria
    y los avisos.
    """

    extremo: str
    ancho_partida: float
    ancho: float
    cumple: bool
    al_tope: bool
    intentos: Tuple[IntentoDeZapata, ...]
    paso: PasoDeMemoria
    avisos: Tuple[str, ...] = ()


def dimensionar_zapata_del_alero(entorno: EntornoDelCabezal, *,
                                 declarado: bool = False
                                 ) -> Optional[DimensionadoDeZapataDelAlero]:
    """
    --- VE-7 (ficha VE7-01) --- El ancho de la zapata de los aleros cuyas
    franjas no cumplen E1 a E3 (todas las franjas con fuste y las
    condiciones evaluables), con la MISMA regla que la del cabezal
    (`dimensionar_zapata_por_estabilidad`, AASHTO LRFD 11.6.3.2, 11.6.3.3,
    11.6.3.6 y 11.6.5):

        B_k = B_0 + k·paso,  B_k <= B_max = fraccion_ancho_max·H_c

    'dimensionamiento_zapata_cabezal' [A]; B_0 es el ancho que el alero
    trae (el del cabezal, declarado o no, o el de la regla) y H_c la altura
    total de la franja del arranque. Un ancho por cabezal; crece el TALON.
    Al tope queda el mayor ancho probado, que no cumple, con su aviso: NO
    FACTIBLE con estos criterios (no se propone otra cosa).

    None si no hay nada que dimensionar (sin aleros, nada evaluable, todo
    cumple) o si el ancho PROPIO de la zapata de los aleros se declaro
    (`declarado`, `ancho_zapata_aleros_m`): gana y no se itera. Sin el
    criterio, `CriterioPendienteError`.
    """
    if declarado or not alero_verificable_como_muro(entorno):
        return None
    evaluadas = _estabilidad_evaluable_del_alero(entorno)
    if not evaluadas or all(e.cumple for e in evaluadas):
        return None
    paso_m, fraccion = _regla_de_dimensionamiento()
    ext = entorno.extremo
    franja = franja_del_arranque_del_alero(entorno).geometria
    H_c = franja.H + franja.espesor_zapata
    tope = fraccion * H_c
    B0 = entorno.geometria.aleros.ancho_zapata
    intentos = [_intento(ext, B0, evaluadas)]
    k = 0
    while True:
        k += 1
        B = B0 + k * paso_m
        if B > tope + TOL_UMBRAL_NORMATIVO:
            intentos[-1] = replace(intentos[-1], al_tope=True)
            break
        intento = _intento(ext, B, _estabilidad_evaluable_del_alero(
            entorno_con_zapata_de_alero(entorno, ancho_zapata=B)))
        intentos.append(intento)
        if intento.cumple:
            break
    ultimo = intentos[-1]
    cumple = ultimo.cumple
    ancho = ultimo.B
    p = paso(
        "F9.DIMENSIONADO", codigo=f"9.3.d.{ext[0]}{SUFIJO_ALERO}",
        que=(f"Ancho de la zapata de los aleros del cabezal de {ext}, "
             "dimensionado por estabilidad (todas sus franjas, como muro)"),
        formula=("B_k = B_0 + k·paso, k = 0, 1, 2, ...: el primer B_k con el "
                 "que E1 a E3 del marco que decide cumplen en todas las "
                 "franjas y las condiciones evaluadas, con B_k <= B_max = "
                 "fraccion_ancho_max·H_c; crece el talon"),
        sustitucion=(
            Magnitud("B_0", B0, "m", "ancho de partida de la zapata de los "
                     "aleros: el de la zapata del cabezal (se desplanta con "
                     "el)"),
            Magnitud("paso", paso_m, "m",
                     f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' [A], el "
                     "mismo de la zapata del cabezal"),
            Magnitud("B_max", tope, "m",
                     f"{fraccion:g}·H_c, H_c = {H_c:.3f} m (la franja del "
                     f"arranque), criterio "
                     f"'{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' [A]"),
        ),
        resultado=Magnitud(
            "B", ancho, "m",
            "dimensionada por estabilidad" if cumple else
            "ZAPATA DE LOS ALEROS NO FACTIBLE con estos criterios: queda el "
            "mayor ancho probado"),
        nota_del_proyecto=(
            "Crece el talon. Intentos: " + _texto_intentos(intentos)))
    avisos = ()
    if not cumple:
        pendientes = (", ".join(ultimo.incumplidas)
                      or "condiciones sin evaluar")
        avisos = (
            f"Aleros del cabezal de {ext} de {entorno.id_punto}: ZAPATA DE "
            f"LOS ALEROS NO FACTIBLE con estos criterios: creciendo por el "
            f"talon hasta el tope B_max = {tope:.3f} m ({fraccion:g}·H_c, "
            f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}'), las franjas "
            f"del alero no cumplen {pendientes}; queda B = {ancho:.3f} m",)
    return DimensionadoDeZapataDelAlero(
        extremo=ext, ancho_partida=B0, ancho=ancho, cumple=cumple,
        al_tope=ultimo.al_tope, intentos=tuple(intentos), paso=p,
        avisos=avisos)


def incumplidas_del_armado_de_la_zapata_del_alero(
        entorno: EntornoDelCabezal) -> Optional[Tuple[str, ...]]:
    """
    --- VE-7 --- Las filas A1 a A4 y A6 del talon de la zapata de los aleros
    que no cumplen, en TODAS las franjas, o None si el armado no se puede
    evaluar (crecer el peralte no lo arregla: el servicio registra el
    `Bloqueo` al armar la geometria final). Vacia sin aleros o con el
    cabezal de gravedad (no se arma).
    """
    g = entorno.geometria
    if g.aleros is None or g.tipo == TIPO_GRAVEDAD:
        return ()
    try:
        piezas = armar_elemento(entorno, ELEMENTO_ZAPATA_ALEROS)
    except ErrorProyecto:
        return None
    return tuple(v.codigo for p in piezas for v in p.verificaciones
                 if not v.cumple
                 and (v.codigo or "").split(".")[0]
                 in FILAS_DEL_ARMADO_DE_LA_ZAPATA)


@dataclass(frozen=True)
class DimensionadoDePeralteDelAlero:
    """
    --- VE-7 --- Lo que `dimensionar_peralte_del_alero` entrega para UN
    cabezal: el peralte adoptado de la zapata de los aleros, si su armado
    cumple, los intentos (texto), el paso de memoria y los avisos.
    """

    extremo: str
    espesor_partida: float
    espesor: float
    cumple: bool
    intentos: Tuple[str, ...]
    paso: PasoDeMemoria
    avisos: Tuple[str, ...] = ()


def dimensionar_peralte_del_alero(entorno: EntornoDelCabezal, *,
                                  declarado: bool = False
                                  ) -> Optional[DimensionadoDePeralteDelAlero]:
    """
    --- VE-7 (ficha VE7-01) --- El peralte de la zapata de los aleros cuyo
    talon no se puede armar en alguna franja (A1 a A4 y A6, AASHTO LRFD
    5.6.3.2, 5.7.3.3, 5.6.3.3, 5.10.3.2 y 5.6.7), con la MISMA regla que el
    de la zapata del cabezal (`dimensionar_peralte_por_armado`): e_k = e_0 +
    k·paso ('dimensionamiento_zapata_cabezal' [A]), el primero con el que
    el talon cumple en todas, con tope fisico (la franja del arranque tiene
    que dejar fuste). La estabilidad de TODAS las franjas se re-verifica con
    cada peralte: si una fila que cumplia deja de cumplir, se detiene en el
    anterior y lo dice. e_0 es el que el alero trae (el del cabezal).

    None si no hay nada que dimensionar (cumple, no se puede evaluar, sin
    aleros, cabezal de gravedad) o si el peralte PROPIO se declaro
    (`declarado`, `espesor_zapata_aleros_m`): gana y no se itera.
    """
    if declarado or not alero_verificable_como_muro(entorno):
        return None
    inc = incumplidas_del_armado_de_la_zapata_del_alero(entorno)
    if not inc:
        return None
    paso_m, _fraccion = _regla_de_dimensionamiento()
    ext = entorno.extremo
    al = entorno.geometria.aleros
    e0 = al.espesor_zapata
    franja = franja_del_arranque_del_alero(entorno).geometria
    tope = franja.H + franja.espesor_zapata
    base = set(_intento(ext, al.ancho_zapata, _estabilidad_evaluable_del_alero(
        entorno)).incumplidas)
    trazas = [f"{e0:.3f} m: no cumplen " + ", ".join(inc)]
    adoptado, cumple, detenido = e0, False, ""
    k = 0
    while True:
        k += 1
        e = e0 + k * paso_m
        if not e < tope - TOL_UMBRAL_NORMATIVO:
            detenido = (f"el peralte llego al tope fisico (la altura de la "
                        f"franja del arranque, {tope:.3f} m)")
            break
        prueba = entorno_con_zapata_de_alero(entorno, espesor_zapata=e)
        inc = incumplidas_del_armado_de_la_zapata_del_alero(prueba)
        if inc is None:
            trazas.append(f"{e:.3f} m: armado no evaluable")
            detenido = "el armado del talon dejo de ser evaluable"
            break
        nuevas = sorted(set(_intento(
            ext, al.ancho_zapata, _estabilidad_evaluable_del_alero(
                prueba)).incumplidas) - base)
        if nuevas:
            trazas.append(f"{e:.3f} m: la estabilidad deja de cumplir ("
                          + ", ".join(nuevas) + ")")
            detenido = ("al engrosarla la estabilidad de las franjas deja de "
                        "cumplir")
            break
        adoptado = e
        if inc:
            trazas.append(f"{e:.3f} m: no cumplen " + ", ".join(inc))
            continue
        trazas.append(f"{e:.3f} m: cumple")
        cumple = True
        break
    p = paso(
        "F9.DIMENSIONADO_PERALTE", codigo=f"9.3.e.{ext[0]}{SUFIJO_ALERO}",
        que=(f"Peralte de la zapata de los aleros del cabezal de {ext}, "
             "dimensionado por el armado de su talon en todas las franjas"),
        formula=("e_k = e_0 + k·paso, k = 0, 1, 2, ...: el primer e_k con el "
                 "que la flexion, el cortante sin estribos, el acero minimo, "
                 "el espaciamiento y la fisuracion del talon cumplen en todas "
                 "las franjas, con e_k menor que la altura de la franja del "
                 "arranque; la estabilidad se re-verifica con cada peralte"),
        sustitucion=(
            Magnitud("e_0", e0, "m", "peralte de partida: el de la zapata "
                     "del cabezal, que el alero hereda"),
            Magnitud("paso", paso_m, "m",
                     f"criterio '{CRITERIO_DIMENSIONAMIENTO_ZAPATA}' [A], el "
                     "mismo de la zapata del cabezal"),
            Magnitud("H_c", tope, "m", "altura total de la franja del "
                     "arranque: tope fisico"),
        ),
        resultado=Magnitud(
            "e_z", adoptado, "m",
            "dimensionado por armado" if cumple else
            "el mayor peralte probado: el armado del talon NO cumple"),
        nota_del_proyecto=(
            "Intentos: " + " -> ".join(trazas) + ". La altura sobre el "
            "refuerzo inferior (A8, E.060 15.7) la hereda de la zapata del "
            "cabezal: el peralte de los aleros parte del suyo y solo crece, "
            "de modo que si A8 cumple en el cabezal cumple aqui."))
    avisos = () if cumple else (
        f"Aleros del cabezal de {ext} de {entorno.id_punto}: el "
        f"dimensionamiento del peralte de su zapata se detuvo en "
        f"{adoptado:.3f} m porque {detenido}: el talon no cumple su armado",)
    return DimensionadoDePeralteDelAlero(
        extremo=ext, espesor_partida=e0, espesor=adoptado, cumple=cumple,
        intentos=tuple(trazas), paso=p, avisos=avisos)


def verificacion_ciclopea_del_alero(entorno: EntornoDelCabezal,
                                    fraccion: float = FRACCION_ARRANQUE_ALERO
                                    ) -> ArmadoDelCabezal:
    """
    --- VE-7 (dictamen Fable, abierto (c)) --- El cuerpo del alero de un
    cabezal de GRAVEDAD en la franja a la `fraccion` de su longitud, con la
    verificacion ciclopea del cabezal (`verificar_cabezal_ciclopeo` sobre la
    franja): C1 a C3 y C6 a C8, con codigos + `sufijo_de_la_franja`. C4 y C5
    (el material, que es el del cabezal) y el aviso del vano no se repiten.
    El cuerpo NO se itera: lo que no cumple sale NO CUMPLE.
    """
    g = entorno.geometria
    if g.aleros is None or g.tipo != TIPO_GRAVEDAD:
        raise DatoInvalidoError(
            "aleros", valor=g.tipo, id_punto=entorno.id_punto,
            motivo="la verificacion ciclopea del alero es la del cabezal de "
                   "gravedad con aleros")
    a = verificar_cabezal_ciclopeo(franja_del_alero(entorno, fraccion))
    sufijo = sufijo_de_la_franja(fraccion)
    de = f"cabezal de {entorno.extremo}"
    rotulo = _rotulo_de_la_franja(entorno.extremo, fraccion)

    def rotular(v):
        codigo = f"{v.codigo}{sufijo}"
        p = v.paso
        if p is not None:
            p = _reemplazar(p, codigo=codigo, que=(
                p.que.replace(de, rotulo) if de in p.que
                else f"{p.que}: {rotulo}"))
        return _reemplazar(v, codigo=codigo, paso=p)

    filas = tuple(rotular(v) for v in a.verificaciones
                  if (v.codigo or "").split(".")[0]
                  not in FILAS_CICLOPEAS_SOLO_DEL_CABEZAL)
    prefijo = _aviso_cabezal(entorno)
    nuevo = (f"Alero del cabezal de {entorno.extremo} de {entorno.id_punto} "
             f"(franja a {fraccion:g}·L, cuerpo ciclopeo)")
    return _reemplazar(
        a, verificaciones=filas,
        pasos=tuple(v.paso for v in filas if v.paso is not None),
        avisos=tuple(x.replace(prefijo, nuevo, 1) for x in a.avisos
                     if "vano del conducto" not in x))


def con_zapata_del_alero(g: GeometriaCabezal, ancho: Optional[float] = None,
                         *, espesor: Optional[float] = None,
                         origen: str = ORIGEN_DIMENSION_ESTABILIDAD,
                         regla: str = "") -> GeometriaCabezal:
    """
    --- VE-7 --- La geometria del cabezal con la zapata de los aleros de
    `ancho` (dimensionada por estabilidad, con `origen`) y/o de `espesor`
    (dimensionado por el armado de su talon), y sus dimensiones. Lo demas
    no se mueve: el alero no entra en la estabilidad ni en el armado del
    cabezal.
    """
    nuevas, cambios = [], {}
    if ancho is not None:
        cambios["ancho_zapata"] = ancho
        nuevas.append(DimensionDeCabezal(
            nombre=DIMENSION_ZAPATA_ALEROS, valor=ancho, unidad="m",
            origen=origen,
            regla=regla or ("el menor de la grilla B_0 + k·paso con el que "
                            "todas las franjas de los aleros cumplen E1 a E3 "
                            "como muro; crece el talon"),
            criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
    if espesor is not None:
        cambios["espesor_zapata"] = espesor
        nuevas.append(DimensionDeCabezal(
            nombre=DIMENSION_PERALTE_ZAPATA_ALEROS, valor=espesor, unidad="m",
            origen=ORIGEN_DIMENSION_ARMADO,
            regla=("el menor de la grilla e_0 + k·paso con el que el armado "
                   "del talon de la zapata de los aleros cumple en todas las "
                   "franjas"),
            criterio=CRITERIO_DIMENSIONAMIENTO_ZAPATA))
    nombres = {d.nombre for d in nuevas}
    dims = tuple(d for d in g.dimensiones if d.nombre not in nombres) \
        + tuple(nuevas)
    return _reemplazar(g, aleros=_reemplazar(g.aleros, **cambios),
                       dimensiones=dims)


def integrar_estabilidad_de_aleros(
        cabezal: CabezalDelPunto,
        estabilidades: Sequence[EstabilidadDelCabezal],
        dimensionados: Sequence[DimensionadoDeZapataDelAlero] = (),
        peraltes: Sequence[DimensionadoDePeralteDelAlero] = (),
        ciclopeos: Sequence[ArmadoDelCabezal] = (),
        pasos_de_franjas: Sequence[PasoDeMemoria] = (),
        avisos: Sequence[str] = ()) -> CabezalDelPunto:
    """
    --- VE-7 --- El cabezal con la verificacion de sus aleros como muro:
    las filas E1 a E3 (y C1 a C8 del alero de gravedad) se suman a las del
    cabezal (la via por la que el informe las cuenta), los pasos (franjas,
    dimensionados, estabilidad, cuerpo) y los avisos a los suyos, la zapata
    de los aleros dimensionada en su geometria y los objetos enteros en
    `estabilidad_aleros`. Un cabezal cuyos aleros no se evaluaron en alguna
    franja y condicion se avisa, como el cabezal.
    """
    from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA
    estabilidades = tuple(estabilidades)
    lista = list(cabezal.avisos)
    lista.extend(a for a in avisos if a not in lista)
    geometrias = {g.extremo: g for g in cabezal.geometrias}
    esperadas = {
        g.extremo: len(fracciones_del_alero(_EntornoMinimo(g))[0])
        * len(CONDICIONES_DE_ESTABILIDAD)
        for g in cabezal.geometrias if g.aleros is not None}
    for d in dimensionados:
        lista.extend(a for a in d.avisos if a not in lista)
        if abs(d.ancho - d.ancho_partida) <= TOL_UMBRAL_NORMATIVO:
            continue
        evaluadas = [e for e in estabilidades if e.extremo == d.extremo]
        incompleta = len(evaluadas) < esperadas.get(d.extremo, 0)
        geometrias[d.extremo] = con_zapata_del_alero(
            geometrias[d.extremo], d.ancho,
            origen=(ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA if incompleta
                    else ORIGEN_DIMENSION_ESTABILIDAD),
            regla=("" if not incompleta else
                   "el menor de la grilla B_0 + k·paso con el que las franjas "
                   "evaluadas de los aleros cumplen E1 a E3; SIN las franjas "
                   "o condiciones que no se pudieron evaluar (ver sus "
                   "bloqueos)"))
    for d in peraltes:
        lista.extend(a for a in d.avisos if a not in lista)
        if abs(d.espesor - d.espesor_partida) > TOL_UMBRAL_NORMATIVO:
            geometrias[d.extremo] = con_zapata_del_alero(
                geometrias[d.extremo], espesor=d.espesor)
    for e in estabilidades:
        lista.extend(a for a in e.avisos if a not in lista)
    for c in ciclopeos:
        lista.extend(a for a in c.avisos if a not in lista)
    for extremo, n in esperadas.items():
        evaluadas = [e for e in estabilidades if e.extremo == extremo]
        if evaluadas and len(evaluadas) < n:
            lista.append(
                f"Aleros del cabezal de {extremo} de {cabezal.id_punto}: su "
                f"estabilidad como muro se evaluo SOLO en {len(evaluadas)} de "
                f"{n} franjas y condiciones (ver «Etapas bloqueadas»)")
    return _reemplazar(
        cabezal, entrada=geometrias["entrada"], salida=geometrias["salida"],
        verificaciones=cabezal.verificaciones + tuple(
            v for e in estabilidades for v in e.verificaciones + e.globales)
        + tuple(v for c in ciclopeos for v in c.verificaciones),
        pasos=(cabezal.pasos + tuple(pasos_de_franjas)
               + tuple(d.paso for d in dimensionados)
               + tuple(d.paso for d in peraltes)
               + tuple(p for e in estabilidades for p in e.pasos)
               + tuple(p for c in ciclopeos for p in c.pasos)),
        avisos=tuple(lista), estabilidad_aleros=estabilidades,
        intentos_de_zapata_aleros=tuple(i for d in dimensionados
                                        for i in d.intentos))
