"""
tests/apoyo/tracker.py
======================
Lector de SOLO LECTURA del tracker de auditorias
(`docs/auditorias/matriz_cruzada_auditorias.xlsx`) con la biblioteca
estandar: `zipfile` + `xml.etree`. Existe para que un TEST pueda leer la
hoja `Hallazgos` sin sumar `openpyxl` a las dependencias de test: openpyxl
esta preautorizado como herramienta de MANTENIMIENTO del tracker
(CLAUDE.md, regla 9) --- lo usa `verificar_sesion.py`, que salta el paso si
falta ---, y un test que dependiera de el abriria un TERCER eje en la tabla
de cuatro entornos (PyMuPDF x Tk) de CLAUDE.md. Un .xlsx es un zip de XML,
y lo que este lector necesita cabe en sesenta lineas.

Que lee: hojas por nombre (workbook.xml -> rels -> sheetN.xml), celdas de
cadena en linea (`t="inlineStr"`, que es como openpyxl escribio este
archivo), cadenas compartidas (`t="s"`, por si alguna vez se guarda con
Excel) y valores numericos (`<v>`). Devuelve texto en todas las celdas:
el tracker es un documento, no una hoja de calculo.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree as ET

RAIZ = Path(__file__).resolve().parents[2]
TRACKER = RAIZ / "docs" / "auditorias" / "matriz_cruzada_auditorias.xlsx"
HOJA_HALLAZGOS = "Hallazgos"

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
       "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


def _columna(ref: str) -> int:
    """'A' -> 0, 'L' -> 11, 'AA' -> 26 (de la referencia 'L304')."""
    letras = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for letra in letras:
        n = n * 26 + (ord(letra) - ord("A") + 1)
    return n - 1


def _texto(celda, compartidas: List[str]) -> str:
    tipo = celda.get("t")
    if tipo == "inlineStr":
        return "".join(t.text or "" for t in celda.iter(f"{{{_NS['m']}}}t"))
    v = celda.find("m:v", _NS)
    if v is None or v.text is None:
        return ""
    if tipo == "s":
        return compartidas[int(v.text)]
    return v.text


def filas(hoja: str = HOJA_HALLAZGOS, ruta: Path = TRACKER) -> List[List[str]]:
    """Las filas de la hoja, como listas de texto (celdas vacias = '')."""
    with zipfile.ZipFile(ruta) as z:
        libro = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        destinos = {r.get("Id"): r.get("Target") for r in rels.findall("rel:Relationship", _NS)}
        rid = next(s.get(f"{{{_NS['r']}}}id") for s in libro.find("m:sheets", _NS)
                   if s.get("name") == hoja)
        destino = destinos[rid].lstrip("/")
        if not destino.startswith("xl/"):
            destino = "xl/" + destino
        compartidas: List[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            compartidas = ["".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t"))
                           for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        hoja_xml = ET.fromstring(z.read(destino))
    salida = []
    for fila in hoja_xml.find("m:sheetData", _NS):
        celdas: Dict[int, str] = {_columna(c.get("r")): _texto(c, compartidas)
                                  for c in fila.findall("m:c", _NS)}
        ancho = max(celdas) + 1 if celdas else 0
        salida.append([celdas.get(i, "") for i in range(ancho)])
    return salida


def hallazgos(ruta: Path = TRACKER) -> List[Dict[str, str]]:
    """Cada fila de `Hallazgos` como {encabezado: texto}."""
    todas = filas(HOJA_HALLAZGOS, ruta)
    encabezado = todas[0]
    return [{encabezado[i]: (fila[i] if i < len(fila) else "")
             for i in range(len(encabezado))}
            for fila in todas[1:] if any(fila)]
