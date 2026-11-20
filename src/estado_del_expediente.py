"""
src/estado_del_expediente.py
============================
LO ABIERTO DEL EXPEDIENTE, CON INDEPENDENCIA DE LA CORRIDA (VE-5, ficha C8-02).

`Registro.discrepancias_abiertas` era el censo completo de las discrepancias
que siguen abiertas contra la hoja de ruta, sin consumidor de produccion: la
memoria consume `discrepancias_que_tocan` --- lo que ESTA corrida toca ---, y
la ficha C8-02 pedia «un informe de estado del expediente, distinto de la
memoria, que enumere lo abierto con independencia de la corrida». Aqui se
deriva su contenido, sin Tk: la pestaña 4 lo pinta.

Y la lista de corridas para comparar: la sesion embebe cada corrida de la
ventana con su volcado (E04), y la pestaña 4 ofrece compararlas con la
vigente sin ir a buscar un JSON al disco. El rotulo de cada una se escribe
aqui; la comparacion es la de `src/comparador.py` (E-B, E14), que nunca
recalcula.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

from src.normativa import registro as _registro_normativo


@dataclass(frozen=True)
class DiscrepanciaAbierta:
    """Una discrepancia abierta, con lo que la ventana necesita decir de ella."""
    id: str
    objeto: str
    estado: str
    gana: str
    efecto_si_se_sigue_la_otra: str

    def linea(self) -> str:
        return (f"{self.id} ({self.estado}) — {self.objeto}. Gana: {self.gana}. "
                f"Si se sigue la otra: {self.efecto_si_se_sigue_la_otra}")


def discrepancias_abiertas() -> Tuple[DiscrepanciaAbierta, ...]:
    """
    El censo de `Registro.discrepancias_abiertas`, en su orden: las que
    `CLAUDE.md` obliga a seguir declarando mientras nadie corrija la hoja de
    ruta (o la fuente). No depende de ninguna corrida.
    """
    registro = _registro_normativo.construir()
    return tuple(DiscrepanciaAbierta(
        id=d.id, objeto=d.objeto, estado=d.estado.value, gana=d.gana,
        efecto_si_se_sigue_la_otra=d.efecto_si_se_sigue_la_otra)
        for d in registro.discrepancias_abiertas())


@dataclass(frozen=True)
class CorridaParaComparar:
    """Una corrida embebida en la sesion, con su rotulo y su volcado."""
    indice: int
    rotulo: str
    informe_json: Dict[str, Any]


# Cuantos caracteres de cada huella lleva el rotulo: bastan para distinguir
# dos versiones del CSV o de los criterios a la vista, sin ocupar la fila.
CARACTERES_DE_HUELLA = 8  # literal-ok: presentacion del rotulo, no una magnitud


def corridas_para_comparar(corridas: Sequence[Any]) -> Tuple[CorridaParaComparar, ...]:
    """
    Las corridas de la sesion que traen su volcado, de la MAS RECIENTE a la
    mas antigua, cada una con un rotulo legible: su hora, su alcance y las
    dos huellas (CSV y criterios), cortas.
    """
    salida: List[CorridaParaComparar] = []
    for indice, corrida in enumerate(corridas):
        if not isinstance(corrida, dict) or not isinstance(corrida.get("informe_json"), dict):
            continue
        csv = str(corrida.get("csv_sha1") or "?")[:CARACTERES_DE_HUELLA]
        criterios = str(corrida.get("criterios_sha1") or "?")[:CARACTERES_DE_HUELLA]
        rotulo = (f"{corrida.get('generado_utc', '?')} · {corrida.get('alcance', '?')} · "
                  f"CSV {csv} · criterios {criterios}")
        salida.append(CorridaParaComparar(indice, rotulo, corrida["informe_json"]))
    return tuple(reversed(salida))
