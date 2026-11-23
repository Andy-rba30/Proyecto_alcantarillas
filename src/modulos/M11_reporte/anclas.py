# -*- coding: utf-8 -*-
"""
M11_reporte.anclas
==================
Submodulo de Fase 11 (`M11_reporte`): bloque `anclas` (D3).
"""

from __future__ import annotations

import hashlib
import re
from typing import (
    Any,
    Tuple,
)

from src.modulos.M11_reporte._base import (
    _esc,
    _reg_M11,
)

def _cita_como_texto(cita_id: str) -> str:
    return _reg_M11.cita(cita_id).como_texto()


# ---------------------------------------------------------------------------
# Las anclas del anexo (EXT-8, PC-12)
# ---------------------------------------------------------------------------
# Un `id` de HTML admite casi cualquier caracter, pero un `href="#..."` con
# `#` o espacios dentro no llega a ninguna parte: el `cita_id` del registro
# (`HDS5_3ED.5.4.3#REPARTO`) se pasa por `_slug`. La correspondencia tiene
# que ser INYECTIVA sobre los ids que esta corrida usa, y `anexo_referencias`
# lo comprueba: dos ids distintos con el mismo slug serian dos anclas
# pisandose, o sea un enlace que lleva al texto equivocado.
_SLUG_NO_ADMITIDO = re.compile(r"[^A-Za-z0-9_.-]+")


def _slug(texto: str) -> str:
    return _SLUG_NO_ADMITIDO.sub("-", str(texto)).strip("-")


def ancla_de_cita(cita_id: str) -> str:
    """El `id` del anexo donde esta transcrita la cita `cita_id`."""
    return "cita-" + _slug(cita_id)


def ancla_de_fundamento(fundamento_id: str) -> str:
    return "fundamento-" + _slug(fundamento_id)


def ancla_de_discrepancia(discrepancia_id: str) -> str:
    return "disc-" + _slug(discrepancia_id)


def ancla_de_criterio(clave: str) -> str:
    return "criterio-" + _slug(clave)


def ancla_de_punto(id_punto: str) -> str:
    """El `id` del bloque de un punto critico, al que el indice enlaza (E-B)."""
    return "punto-" + _slug(id_punto)


_RE_H2_DE_LA_PLANTILLA = re.compile(r'<h2\s+id="([^"]+)"[^>]*>(.*?)</h2>', re.S)
_RE_ETIQUETA_HTML = re.compile(r"<[^>]+>")


def indice_de_la_memoria(texto_plantilla: str, informe: Any) -> str:
    """
    El indice del documento (E-B, E21 acotado): una entrada por `<h2 id>` de
    la PROPIA plantilla, en su orden, y bajo la seccion de los puntos una
    entrada por punto del informe con su estado. Nada que no exista como
    objeto: los titulos y las anclas se leen del texto de la plantilla que
    se va a imprimir --- de modo que el indice no puede divergir de las
    secciones ---, y los puntos, del `Informe`. `memoria_html_por_partes` lo
    calcula sobre `plantilla.template` antes del primer trozo.
    """
    entradas = []
    for ancla, titulo in _RE_H2_DE_LA_PLANTILLA.findall(texto_plantilla):
        rotulo = " ".join(_RE_ETIQUETA_HTML.sub("", titulo).split())
        entradas.append(f'<li>{_enlace(ancla, rotulo, "indice-seccion")}')
        if ancla == "memorias" and informe.puntos:
            puntos = []
            for p in informe.puntos:
                punto = p.punto
                estado = ("dimensionado" if p.dimensionado else "sin dimensionar")
                n_bloqueos = len(p.bloqueos_reales())
                detalle = (f"{_esc(punto.id)} &nbsp;|&nbsp; progresiva "
                           f"{_esc(punto.progresiva_display)} &nbsp;|&nbsp; Familia "
                           f"{_esc(punto.familia.value)} &nbsp;|&nbsp; {estado}")
                if n_bloqueos:
                    plural = "" if n_bloqueos == 1 else "s"
                    detalle += f" &nbsp;|&nbsp; {n_bloqueos} etapa{plural} bloqueada{plural}"
                puntos.append(
                    f"<li>{_enlace(ancla_de_punto(punto.id), detalle, 'indice-punto')}</li>")
            entradas.append("<ol>" + "".join(puntos) + "</ol>")
        entradas.append("</li>")
    return ('<nav class="indice"><h2 id="indice">Indice</h2><ol>'
            + "".join(entradas) + "</ol></nav>")


def ancla_de_umbral(umbral: Any) -> str:
    """
    El `id` de la ficha de un umbral en el anexo.

    Un umbral no tiene id propio en el registro: lo identifica su contenido
    entero (descripcion, valor, unidad, cita, caracter, aplicacion y criterio
    aplicado). Dos pasos con el MISMO umbral --- V3 en dos puntos del mismo
    material --- enlazan a la misma ficha; el V3 de otro material, con otro
    valor, tiene la suya. La huella es de contenido y por eso `memoria_de_punto`
    la calcula sola, sin un indice previo: un paso se puede renderizar
    suelto (la traza de la GUI lo hace) y su enlace sigue apuntando a donde
    el anexo lo pondra.
    """
    huella = hashlib.sha1(repr(_clave_de_umbral(umbral)).encode("utf-8")).hexdigest()
    return f"umbral-{_slug(umbral.cita_id)}-{huella[:8]}"  # literal-ok: largo de la huella corta del ancla


def _clave_de_umbral(u: Any) -> Tuple[Any, ...]:
    return (u.descripcion, repr(u.valor), u.unidad, u.cita_id, u.caracter,
            u.aplicacion, u.criterio_aplicado or "")


def _donde(punto: str) -> str:
    return f"en el punto {_esc(punto)}" if punto else "mas arriba"


def _enlace(ancla: str, texto: str, clase: str = "remision") -> str:
    return f'<a href="#{_esc(ancla)}" class="{clase}">{texto}</a>'
