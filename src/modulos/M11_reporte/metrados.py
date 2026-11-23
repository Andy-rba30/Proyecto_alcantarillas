# -*- coding: utf-8 -*-
"""
M11_reporte.metrados
====================
Submodulo de Fase 11 (`M11_reporte`): bloque `metrados` (D3).
"""

from __future__ import annotations

import html
from typing import (
    Any,
    Sequence,
    Tuple,
)
from src.modelos import ESTADO_RASANTE_COMPATIBLE

from src.modulos.M11_reporte._base import (
    FMT_2,
    VACIO,
    _esc,
    _etiqueta_html,
    _num,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.pasos import (
    bloque_pasos,
)

# ===========================================================================
# --- VE-5 met --- Fase 11, entregables 8 y 9: metrados y cuadro de
# compatibilidad rasante-alcantarilla. Los numeros vienen de `M12_metrados`
# (renglones, totales y filas del cuadro); aqui solo se formatean.
# ===========================================================================

TITULO_METRADO_PUNTO = ("Fase 11 &mdash; Metrados del punto referidos al "
                        "EG-2013 (entregable 8)")
TITULO_TRAZA_METRADO = "Desarrollo de los metrados del punto (Fase 11)"
TITULO_METRADOS_PROYECTO = ("Fase 11 del proyecto: cuadro de compatibilidad "
                            "rasante-alcantarilla y metrados por partida")
ANCLA_METRADOS_PROYECTO = "fase-11-proyecto"


def traza_metrado(informe: Any) -> Tuple[Any, ...]:
    """Los pasos de la Fase 11 del punto (sus metrados), una vez cada uno."""
    m = getattr(informe, "metrado", None)
    return () if m is None else tuple(m.pasos)


def _tabla_renglones(renglones: Sequence[Any]) -> str:
    """
    Los renglones del metrado del punto, con su desglose (las partes que
    `M12_metrados` multiplica o suma, con su cantidad) debajo de la
    descripcion: el JSON lo lleva y la memoria lo imprime igual.
    """
    filas = [_fila(["<th>Partida</th>", "<th>Descripcion</th>",
                    "<th>Elemento</th>", "<th>Und.</th>",
                    "<th>Cantidad</th>"])]
    for r in renglones:
        partida = (_esc(r.partida) if r.partida
                   else f"{_etiqueta_html(r.etiqueta_partida)} especial")
        desglose = "".join(f"<br><small>{_esc(parte)}: {_num(c)}</small>"
                           for parte, c in r.desglose)
        filas.append(_fila([_td(partida), _td(_esc(r.descripcion) + desglose),
                            _td(_esc(r.elemento)), _td(_esc(r.unidad)),
                            _td(_num(r.cantidad, FMT_2), "num")]))
    return '<table class="compacta">' + "".join(filas) + "</table>"


def _bloque_compatibilidad_punto(informe: Any) -> str:
    """
    La fila del punto en el cuadro de compatibilidad rasante-alcantarilla
    (Fase 11, entregable 9): la seccion que se juzga y el estado. Los numeros
    estan en el cuadro del proyecto (`bloque_metrados_proyecto`), y se
    repiten aqui sin calcular nada. Vacio si el punto no tiene fila.
    """
    f = getattr(informe, "compatibilidad_rasante", None)
    if f is None:
        return ""
    estado = _esc(f.estado)
    if f.delta_rasante_m is not None:
        estado += f" {_num(f.delta_rasante_m, FMT_2)} m"
    if f.provisional:
        estado += " (provisional)"
    return ("<h4>Fase 11 &mdash; Compatibilidad rasante-alcantarilla "
            "(entregable 9)</h4>"
            f"<p>Seccion: {_esc(f.seccion) or VACIO}. Rasante actual "
            f"{_cota(f.cota_rasante_actual)} msnm; rasante minima de 7.A "
            f"{_cota(f.cota_rasante_min)} msnm. Estado: {estado}.</p>")


def _bloque_metrado(informe: Any) -> str:
    """
    El metrado del punto: la tabla de renglones con su partida del EG-2013,
    los avisos y el desarrollo de cada renglon. Los renglones que no se
    pudieron medir estan en la tabla de bloqueos del punto (FASE_METRADOS).
    Vacio sin metrado (perfil, o el punto sin cabezal).
    """
    m = getattr(informe, "metrado", None)
    if m is None:
        return ""
    cuerpo = (_tabla_renglones(m.renglones) if m.renglones else
              '<div class="nota"><p>Ningun renglon se pudo medir: ver los '
              "bloqueos del punto.</p></div>")
    avisos = "".join(f'<div class="aviso"><p>{_esc(a)}</p></div>'
                     for a in m.avisos)
    return (f"<h4>{TITULO_METRADO_PUNTO}</h4>"
            "<p>Cantidades medidas con las reglas de medicion de cada "
            "Seccion del EG-2013 sobre la geometria final del punto; sin "
            "factor de desperdicio ni de esponjamiento (EG-2013 501.09, "
            "503.12 y 503.13). Lo que falta para medir un renglon esta en "
            "los bloqueos del punto.</p>"
            + cuerpo + avisos
            + bloque_pasos(traza_metrado(informe), TITULO_TRAZA_METRADO))


def _cota(valor: Any) -> str:
    return VACIO if valor is None else _num(valor)


def bloque_metrados_proyecto(informe: Any) -> str:
    """
    La Fase 11 del PROYECTO: el cuadro de compatibilidad rasante-alcantarilla
    (entregable 9, una fila por punto: la salida de 7.A) y los totales de
    cada partida del EG-2013 (entregable 8, `Informe.totales_metrado`). El
    cuadro sale en los dos alcances; los totales, solo cuando la corrida
    llego a metrar (expediente).
    """
    filas = [p.compatibilidad_rasante for p in informe.puntos
             if getattr(p, "compatibilidad_rasante", None) is not None]
    totales = tuple(getattr(informe, "totales_metrado", ()) or ())
    if not filas and not totales:
        return ""
    partes = [f'<h3 id="{ANCLA_METRADOS_PROYECTO}">'
              f"{_esc(TITULO_METRADOS_PROYECTO)}</h3>"]
    if filas:
        cab = ["Punto", "Progresiva", "Seccion", "Rasante actual (msnm)",
               "Rasante minima 7.A (msnm)", "Por recubrimiento",
               "Por resguardo", "Gobierna", "Holgura (m)", "Estado"]
        html = [_fila([f"<th>{_esc(c)}</th>" for c in cab])]
        for f in filas:
            estado = _esc(f.estado)
            if f.delta_rasante_m is not None:
                estado += f" {_num(f.delta_rasante_m, FMT_2)} m"
            if f.provisional:
                estado += " (provisional)"
            clase = ("cumple" if f.estado == ESTADO_RASANTE_COMPATIBLE
                     else "incumple")
            html.append(_fila([
                _td(_esc(f.id_punto)), _td(_esc(f.progresiva)),
                _td(_esc(f.seccion) or VACIO),
                _td(_cota(f.cota_rasante_actual), "num"),
                _td(_cota(f.cota_rasante_min), "num"),
                _td(_cota(f.cota_por_recubrimiento), "num"),
                _td(_cota(f.cota_por_resguardo), "num"),
                _td(_esc(f.gobierna) if f.gobierna else VACIO),
                _td(VACIO if f.holgura_m is None
                    else _num(f.holgura_m, FMT_2), "num"),
                _td(f'<span class="{clase}">{estado}</span>')]))
        notas = [f"{_esc(f.id_punto)}: {_esc(f.motivo or f.aviso)}"
                 for f in filas if f.motivo or f.aviso]
        partes.append(
            "<h4>Cuadro de compatibilidad rasante-alcantarilla (entregable "
            "9, salida de 7.A)</h4>"
            '<table class="compacta">' + "".join(html) + "</table>"
            + ('<div class="nota">' + "".join(f"<p>{n}</p>" for n in notas)
               + "</div>" if notas else ""))
    if totales:
        html = [_fila(["<th>Partida</th>", "<th>Descripcion</th>",
                       "<th>Und.</th>", "<th>Cantidad</th>",
                       "<th>Puntos</th>"])]
        for t in totales:
            partida = (_esc(t.partida) if t.partida
                       else f"{_etiqueta_html(t.etiqueta_partida)} especial")
            html.append(_fila([_td(partida), _td(_esc(t.descripcion)),
                               _td(_esc(t.unidad)),
                               _td(_num(t.cantidad, FMT_2), "num"),
                               _td(_esc(", ".join(t.puntos)))]))
        partes.append(
            "<h4>Metrados del expediente por partida del EG-2013 "
            "(entregable 8)</h4>"
            '<table class="compacta">' + "".join(html) + "</table>")
    return "".join(partes)
