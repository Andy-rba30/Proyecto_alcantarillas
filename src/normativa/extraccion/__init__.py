"""
Lectura de los PDF de `normas/`.

Es la unica parte del registro que abre un archivo. Vive aparte porque
`PyMuPDF` es dependencia de TEST (requirements-dev.txt) y NO del software
calculado: ningun modulo de calculo importa este paquete, y el registro
entero se puede leer sin el.
"""

from .pdf import (
    PDF_NO_DISPONIBLE,
    ExtraccionNoDisponibleError,
    aparece_en_pagina,
    normalizar,
    numero_de_paginas,
    pymupdf_disponible,
    renderizar_pagina,
    sha1_de,
    texto_de_pagina,
)

__all__ = [
    "PDF_NO_DISPONIBLE",
    "ExtraccionNoDisponibleError",
    "aparece_en_pagina",
    "normalizar",
    "numero_de_paginas",
    "pymupdf_disponible",
    "renderizar_pagina",
    "sha1_de",
    "texto_de_pagina",
]
