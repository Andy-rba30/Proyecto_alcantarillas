"""
Acceso a los PDF de `normas/`: SHA-1, texto por pagina, render a imagen.

QUE HACE Y QUE NO. Extrae; no interpreta. Todo lo que decide si una cita es
cierta vive en `tests/test_normativa_pdf.py`; aqui solo estan las cuatro
operaciones que ese test necesita y la NORMALIZACION con que compara.

POR QUE LA NORMALIZACION VIVE AQUI Y NO EN EL TEST. Porque la usan tres
consumidores -- el test T2 (texto literal), el T3 (titulo del numeral) y el T5
(el valor dentro del texto) -- y tenerla en un solo sitio es lo que hace que
los tres busquen lo mismo. La regla, escrita una vez:

    minusculas, sin diacriticos (NFKD), espacios colapsados, comillas y
    guiones unificados, y COMA DECIMAL == PUNTO DECIMAL.

La ultima equivalencia no es cosmetica: E.060 imprime "2,0 %" y el codigo
escribe 2.00. Sin ella T5 daria falso negativo en todo el corpus peruano.

Y AL REVES, LO QUE LA NORMALIZACION NO ES: no es como se GUARDA un
`Verbatim`. Un literal guardado sin tildes no se puede encontrar en el PDF con
el buscador de un lector; la normalizacion es para comparar, nunca para
almacenar. Esa asimetria es el invariante T21.

DEPENDENCIA. `PyMuPDF` (import `pymupdf`) es dependencia de TEST, declarada en
`requirements-dev.txt`, NO en `requirements.txt`. Si no esta instalada, este
modulo importa igual y `pymupdf_disponible()` devuelve False: los tests que
abren PDF se saltan (`pytest.mark.pdf`) y los estructurales siguen corriendo.
Se eligio sobre `pdfminer.six` porque cubre texto E IMAGEN: tres hallazgos ya
cerrados del proyecto -- el `>` de la ultima columna de F_pga, el asterisco de
la fila F y el `[1 -]` de K_AE -- se decidieron renderizando la pagina, cosa
que `pdfminer.six` no puede hacer.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - la rama depende del entorno, no de la logica
    import pymupdf as _pymupdf
except ImportError:  # pragma: no cover
    try:
        import fitz as _pymupdf  # nombre antiguo del mismo paquete
    except ImportError:
        _pymupdf = None

PDF_NO_DISPONIBLE = (
    "PyMuPDF no esta instalado. Es dependencia de TEST: "
    "pip install -r requirements-dev.txt")


class ExtraccionNoDisponibleError(RuntimeError):
    """
    No se pudo abrir el PDF. NO desciende de ErrorProyecto a proposito: no es
    un problema del expediente ni del programa de calculo, es que falta una
    herramienta de verificacion. La taxonomia de `modelos.py` no le toca.
    """


def pymupdf_disponible() -> bool:
    """True si se puede abrir un PDF en este entorno."""
    return _pymupdf is not None


def _abrir(ruta: Path):
    if _pymupdf is None:
        raise ExtraccionNoDisponibleError(PDF_NO_DISPONIBLE)
    if not Path(ruta).exists():
        raise FileNotFoundError(f"no existe el PDF: {ruta}")
    return _pymupdf.open(str(ruta))


def sha1_de(ruta: Path) -> str:
    """
    SHA-1 del archivo entero. Es lo que ata un `Verificado` a UN archivo
    exacto: si el PDF cambia, el hash cambia y todas las citas de esa fuente
    caducan a la vez (test T0).
    """
    h = hashlib.sha1()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):   # literal-ok: tamaño de bloque de lectura, no valor de proyecto
            h.update(bloque)
    return h.hexdigest()


def numero_de_paginas(ruta: Path) -> int:
    """Paginas del PDF. Acota `pagina_pdf` sin tener que leer su contenido."""
    doc = _abrir(ruta)
    try:
        return doc.page_count
    finally:
        doc.close()


def texto_de_pagina(ruta: Path, pagina_pdf: int) -> str:
    """
    Texto de UNA pagina, 1-indexada como la cuenta un lector de PDF.

    Devuelve el volcado crudo, con sus saltos de linea y su orden de columnas.
    Quien compara usa `aparece_en_pagina`, que normaliza; quien depura mira
    esto.
    """
    doc = _abrir(ruta)
    try:
        if not 1 <= pagina_pdf <= doc.page_count:
            raise ValueError(
                f"pagina_pdf {pagina_pdf} fuera de rango: el PDF tiene "
                f"{doc.page_count} paginas")
        return doc[pagina_pdf - 1].get_text()
    finally:
        doc.close()


_COMILLAS = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "«": '"',
    "»": '"', "‹": "'", "›": "'", "´": "'",
}
_GUIONES = {
    "‐": "-", "‑": "-", "‒": "-", "–": "-",
    "—": "-", "―": "-", "−": "-",
}
# La coma decimal del corpus peruano y el punto decimal del codigo son EL
# MISMO numero: "2,0 %" y 2.00. Solo se toca la coma que va ENTRE DIGITOS --
# la de una enumeracion ("DC, DD, DW") no es un decimal y se deja.
_COMA_DECIMAL = re.compile(r"(?<=\d),(?=\d)")
# EL GUION DE FIN DE LINEA. Cuando una palabra se parte al final de un
# renglon, la extraccion devuelve el guion Y un espacio: la pag. impresa
# 11-25 de AASHTO imprime «middle two-thirds» y el volcado da «middle two-
# thirds». Es un artefacto DEL EXTRACTOR, no del documento, y si no se
# deshace obliga a recortar todo `Verbatim` para que no cruce un salto de
# linea -- con lo que las citas dejarian de poder ser frases enteras.
#
# La regla es deliberadamente ESTRECHA: guion PEGADO a la letra anterior,
# seguido de espacio o salto de linea, y letra despues. Un guion con espacio a
# AMBOS lados no se toca, porque entonces es del documento: E.050 imprime
# «Condición Pseudo - dinámico» asi, con los dos espacios, y esa es una
# errata de la fuente que hay que conservar.
_GUION_DE_FIN_DE_LINEA = re.compile(r"(?<=[^\W\d_])-\s+(?=[^\W\d_])")
_ESPACIOS = re.compile(r"\s+")


def normalizar(texto: str) -> str:
    """
    Forma de COMPARACION de un texto. Ver el encabezado del modulo: es para
    buscar, nunca para guardar.
    """
    for origen, destino in _COMILLAS.items():
        texto = texto.replace(origen, destino)
    for origen, destino in _GUIONES.items():
        texto = texto.replace(origen, destino)
    texto = _COMA_DECIMAL.sub(".", texto)
    texto = _GUION_DE_FIN_DE_LINEA.sub("-", texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.casefold()
    return _ESPACIOS.sub(" ", texto).strip()


def aparece_en_pagina(ruta: Path, pagina_pdf: int, buscado: str) -> bool:
    """
    Si `buscado`, normalizado, aparece en esa pagina del PDF.

    Es la operacion que hace verdadera la palabra "verificado": el test T2
    la aplica al `texto_literal` de cada cita y el T3 al titulo de su numeral.
    """
    return normalizar(buscado) in normalizar(texto_de_pagina(ruta, pagina_pdf))


def renderizar_pagina(ruta: Path, pagina_pdf: int, destino: Path,
                      escala: float = 4.0) -> Path:   # literal-ok: escala de renderizado; no entra en ninguna formula
    """
    Vuelca una pagina a PNG, para leerla a ojo cuando el texto no basta.

    HACE FALTA, y no es un lujo: tres decisiones ya tomadas del proyecto no se
    podian tomar sobre el volcado de texto -- el signo `>` de la ultima columna
    de F_pga, el asterisco de la fila F y el `[1 -]` del denominador de K_AE --,
    y ademas tres de las trece fuentes (AASHTO M 36, AASHTO M 170M y ASTM A760)
    no entregan texto utilizable. Una cita de esas se verifica por imagen o no
    se verifica: `Verificado.metodo` obliga a decir cual de las dos.
    """
    doc = _abrir(ruta)
    try:
        if not 1 <= pagina_pdf <= doc.page_count:
            raise ValueError(
                f"pagina_pdf {pagina_pdf} fuera de rango: el PDF tiene "
                f"{doc.page_count} paginas")
        matriz = _pymupdf.Matrix(escala, escala)
        pixmap = doc[pagina_pdf - 1].get_pixmap(matrix=matriz)
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(str(destino))
        return destino
    finally:
        doc.close()


def texto_extraible(ruta: Path, muestra: int = 12) -> bool:   # literal-ok: tamaño de la muestra de paginas que se sondea
    """
    Si el PDF entrega texto que se puede comparar.

    No todos lo hacen, y esa es una propiedad de la FUENTE que el registro
    tiene que declarar: AASHTO M 36 es un raster sin capa de texto y ASTM A760
    trae una codificacion de fuente que devuelve caracteres sustituidos
    ("@esmkgbdmog" por "Designacion"). Una cita a esas dos no se puede
    verificar por texto y decirlo es parte de la verificacion, no una excusa.
    """
    doc = _abrir(ruta)
    try:
        paginas = min(muestra, doc.page_count)
        # literal-ok: 40 caracteres y un tercio de las paginas son el
        # criterio con que se decide si un PDF tiene capa de texto util; no
        # son valores de proyecto y no entran en ninguna magnitud fisica.
        util = sum(1 for i in range(paginas)
                   if len(doc[i].get_text().strip()) > 40)   # literal-ok: umbral de «pagina con texto»
        return util >= max(1, paginas // 3)   # literal-ok: un tercio de la muestra
    finally:
        doc.close()


def pagina_impresa_declarada(ruta: Path, pagina_pdf: int,
                             lineas: int = 4) -> Optional[str]:   # literal-ok: cuantas lineas de cabecera se devuelven
    """
    Las primeras lineas no vacias de una pagina, donde suele imprimirse su
    numero. Sirve para MEDIR el desfase en vez de suponerlo, que es lo que
    `Paginacion` convierte despues en prediccion testeable (T6).
    """
    texto = texto_de_pagina(ruta, pagina_pdf)
    utiles = [l.strip() for l in texto.split("\n") if l.strip()]
    if not utiles:
        return None
    return " | ".join(utiles[:lineas])
