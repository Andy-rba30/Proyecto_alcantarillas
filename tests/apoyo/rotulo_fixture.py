"""
tests/apoyo/rotulo_fixture.py
=============================
El ENVOLTORIO DECLARADO que pone la advertencia de fixture en las memorias
HTML de la linea base de la Familia C (T-12 punto 3, INF-5.2.4).

POR QUE UN ENVOLTORIO Y NO UNA BANDERA DEL PROGRAMA. Las memorias de
`tests/linea_base_familia_c/` las escribe la CLI de produccion sobre el CSV
del ejemplo y unas entradas de prueba, y se leian como resultados del
proyecto. Habia dos maneras de rotularlas:

  (a) que M11 imprimiera la advertencia cuando «los datos son de fixture».
      El programa no tiene como saberlo sin que se lo digan, y darle una
      bandera para decirlo (`--es-fixture`, o un rotulo libre) pone en el
      producto un texto que una memoria REAL podria llevar por error, o que
      alguien podria quitar de una memoria de prueba con la misma bandera:
      falsea en las dos direcciones.
  (b) que el GENERADOR de la linea base (`regenerar.sh`) la ponga al
      escribir sus archivos, despues de la CLI y fuera del producto.

Se eligio (b): la advertencia la pone ESTE script, que solo se invoca desde
`tests/linea_base_familia_c/regenerar.sh`; la CLI no la conoce y ninguna
memoria de un proyecto real puede llevarla. Como `test_linea_base` corre el
mismo script, lo comprometido y lo regenerado llevan la misma advertencia y
el diff de bytes sigue midiendo el programa.

Que hace: inserta un bloque visible, rojo, al principio del cuerpo
(`<body>`; en un fragmento sin `<body>`, como la memoria del punto de cajon,
al principio del archivo) y antepone el rotulo al `<title>`. No toca nada
mas: lee de la entrada estandar y escribe en la salida estandar, en bytes
UTF-8, para encadenarse detras de la normalizacion de `regenerar.sh`.

    norm memoria.html | python3 -m tests.apoyo.rotulo_fixture > destino.html
"""

from __future__ import annotations

import sys

ROTULO = "FIXTURE DE PRUEBA, NO ES UN RESULTADO DEL PROYECTO"
BLOQUE = (
    '<div class="fixture-de-prueba" style="border:3px solid #a4160f;'
    "background:#fdf1f0;color:#a4160f;padding:.6em .9em;margin:0 0 1em 0;"
    'font-weight:700;">' + ROTULO + " &mdash; archivo de la linea base de "
    "la Familia C, generado por <code>tests/linea_base_familia_c/regenerar.sh"
    "</code> con DATOS DE PRUEBA (que corrida lo produce y con que entradas lo "
    "dice el README de esa carpeta). Sirve para detectar cambios del "
    "programa; ningun numero de esta memoria es un dato ni un resultado de la "
    "obra.</div>\n")
TITULO = "<title>"


def rotular(html: str) -> str:
    """El HTML con el bloque de advertencia y el rotulo en el titulo."""
    if TITULO in html:
        html = html.replace(TITULO, f"{TITULO}{ROTULO} - ", 1)
    if "<body>" in html:
        return html.replace("<body>", "<body>\n" + BLOQUE, 1)
    return BLOQUE + html


def main() -> None:
    texto = sys.stdin.buffer.read().decode("utf-8")
    sys.stdout.buffer.write(rotular(texto).encode("utf-8"))


if __name__ == "__main__":
    main()
