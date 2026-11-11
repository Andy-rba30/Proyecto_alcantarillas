"""
Herramienta de linea de comandos para leer los PDF de `normas/`.

Existe para que verificar una cita no exija escribir un script cada vez:

    python3 -m src.normativa.extraccion texto <pdf> <pagina_pdf> [n_paginas]
    python3 -m src.normativa.extraccion buscar <pdf> "<frase>" [pag_desde] [pag_hasta]
    python3 -m src.normativa.extraccion cabeceras <pdf> <desde> <hasta>
    python3 -m src.normativa.extraccion png <pdf> <pagina_pdf> <destino.png> [escala]
    python3 -m src.normativa.extraccion sha1 <pdf>

`<pdf>` admite un fragmento del nombre: "Puentes", "Hidro", "E.060".

DONDE SE BUSCAN (T-0): en las carpetas de `fuentes.directorios_de_normas()`
--`$NORMAS_DIR`, el clon del repositorio de normas, y despues `normas/` de
este repositorio mientras exista--, de modo que `hec14` y `HydraulicsManual`,
que viven solo en el repositorio de normas, se resuelven igual que el resto:

    NORMAS_DIR=/ruta/al/clon/de/Normas python3 -m src.normativa.extraccion sha1 hec14
"""

from __future__ import annotations

import sys
from pathlib import Path

from .pdf import (
    normalizar,
    numero_de_paginas,
    pagina_impresa_declarada,
    renderizar_pagina,
    sha1_de,
    texto_de_pagina,
)

def _resolver(fragmento: str) -> Path:
    ruta = Path(fragmento)
    if ruta.exists():
        return ruta
    # Import en el punto de uso: `fuentes` importa el esquema entero y este
    # modulo se carga tambien para ordenes que traen la ruta completa.
    from ..fuentes import VARIABLE_NORMAS_DIR, pdf_en_disco
    objetivo = normalizar(fragmento)
    candidatos = [p for nombre, p in sorted(pdf_en_disco().items())
                  if objetivo in normalizar(nombre)]
    if not candidatos:
        raise SystemExit(
            f"ningun PDF de las carpetas de normas contiene «{fragmento}» "
            f"(se busca en ${VARIABLE_NORMAS_DIR} y en normas/)")
    if len(candidatos) > 1:
        nombres = "\n  ".join(p.name for p in candidatos)
        raise SystemExit(f"«{fragmento}» es ambiguo:\n  {nombres}")
    return candidatos[0]


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    orden, resto = argv[1], argv[2:]

    if orden == "sha1":
        pdf = _resolver(resto[0])
        print(f"{sha1_de(pdf)}  {numero_de_paginas(pdf)} pags  {pdf.name}")
        return 0

    if orden == "texto":
        pdf = _resolver(resto[0])
        inicio = int(resto[1])
        cuantas = int(resto[2]) if len(resto) > 2 else 1
        for p in range(inicio, inicio + cuantas):
            print(f"\n=========== PDF {p} de {pdf.name} ===========")
            print(texto_de_pagina(pdf, p))
        return 0

    if orden == "buscar":
        pdf = _resolver(resto[0])
        frase = normalizar(resto[1])
        # literal-ok: indices de argumentos de la linea de ordenes
        desde = int(resto[2]) if len(resto) > 2 else 1
        hasta = int(resto[3]) if len(resto) > 3 else numero_de_paginas(pdf)  # literal-ok: indice de argumento
        encontrados = 0
        for p in range(desde, min(hasta, numero_de_paginas(pdf)) + 1):
            plano = normalizar(texto_de_pagina(pdf, p))
            if frase in plano:
                encontrados += 1
                i = plano.index(frase)
                print(f"[PDF {p}] ...{plano[max(0, i - 160):i + len(frase) + 160]}...")  # literal-ok: 160 caracteres de contexto
        print(f"-- {encontrados} paginas con la frase")
        return 0

    if orden == "cabeceras":
        pdf = _resolver(resto[0])
        for p in range(int(resto[1]), int(resto[2]) + 1):   # literal-ok: indice de argumento
            print(f"[PDF {p}] {pagina_impresa_declarada(pdf, p)}")
        return 0

    if orden == "png":
        pdf = _resolver(resto[0])
        escala = float(resto[3]) if len(resto) > 3 else 4.0  # literal-ok: indice de argumento y escala de renderizado por defecto
        print(renderizar_pagina(pdf, int(resto[1]), Path(resto[2]), escala))
        return 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
