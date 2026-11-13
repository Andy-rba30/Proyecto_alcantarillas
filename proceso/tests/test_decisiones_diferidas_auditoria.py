"""
proceso/tests/test_decisiones_diferidas_auditoria.py
====================================================
La guardia que ata `docs/decisiones_diferidas.md` (ENTREGABLE) a la
auditoria de sistema (`proceso/auditorias/auditoria_sistema.md`, PROCESO):
las veintidos fichas de los hallazgos que esa auditoria clasifico
«deliberado sin documentar». T-12 la separo de
`tests/test_decisiones_diferidas.py` (INF-5.2.2) porque lee un archivo de
proceso; su texto es el de `f77c5d4`, con la ruta nueva. Y el anclaje de las
fichas cuyo simbolo vive en `proceso/` (EXT-11-03, T0-04), que la suite del
entregable deja fuera por la misma razon.

Se corre desde la raiz del repositorio:  python -m pytest proceso/tests
"""

import re
from pathlib import Path

import pytest

from tests.test_decisiones_diferidas import (PREFIJO_PROCESO, _fichas,
                                          _nombres_de, _simbolos_declarados)

RAIZ = Path(__file__).resolve().parents[2]
AUDITORIA = RAIZ / "proceso" / "auditorias" / "auditoria_sistema.md"


def _ids_deliberados() -> list:
    """
    Los IDs que la auditoria de sistema clasifico «deliberado sin documentar»,
    leidos del informe. La lista NO se escribe aqui a proposito: derivarla es
    lo que hace que el registro no pueda quedarse corto en silencio.
    """
    lineas = AUDITORIA.read_text(encoding="utf-8").split("\n")
    ids = []
    for i, linea in enumerate(lineas):
        if "**Clasificacion** deliberado sin documentar" not in linea:
            continue
        for j in range(i, max(-1, i - 12), -1):
            m = re.match(r"^###\s+([A-G]-\d+)\s", lineas[j])
            if m:
                ids.append("SIS-" + m.group(1))
                break
    return ids



def test_estan_las_veintidos_fichas_que_la_auditoria_clasifico():
    """
    La lista se deriva del informe, no se copia. Es la diferencia entre un
    registro que se queda corto en silencio y uno que lo dice.
    """
    esperados = _ids_deliberados()
    assert len(esperados) == 22, (
        f"la auditoria clasifica hoy {len(esperados)} hallazgos como "
        "«deliberado sin documentar» y el registro se escribio para 22: "
        "revisa el informe antes de tocar el registro")

    faltan = [i for i in esperados if i not in _fichas()]
    assert not faltan, (
        f"sin ficha en docs/decisiones_diferidas.md: {faltan}")


@pytest.mark.parametrize(
    "seccion,ruta,simbolo",
    [s for s in _simbolos_declarados() if s[1].startswith(PREFIJO_PROCESO)])
def test_el_simbolo_que_ancla_una_ficha_en_proceso_sigue_existiendo(seccion, ruta, simbolo):
    archivo = RAIZ / ruta
    assert archivo.exists(), f"{seccion}: {ruta} no existe"
    assert simbolo in _nombres_de(archivo), (
        f"{seccion}: `{simbolo}` ya no existe en {ruta}")
