#!/bin/sh
# Regenera la LINEA BASE de la Familia C. La abrio la sesion C0 y su unico
# consumidor es C1, que la usa como DIFF: el refactor de seccion no puede mover
# ningun numero, y esto es contra que se comprueba.
#
# Se corre desde la raiz del repositorio:   sh tests/linea_base_familia_c/regenerar.sh
#
# POR QUE NORMALIZA, y no es cosmetica. La corrida trae TRES campos volatiles, y
# sin retirarlos el diff da rojo por razones que no son el refactor:
#   1. `generado (UTC): <iso>` en la salida de la CLI.
#   2. `corrida UTC: <iso>` y la misma fecha en formato local, en el HTML.
#   3. `Fecha de criterios_adoptados.py` en el HTML, que M11 saca de
#      `ruta.stat().st_mtime`. ESTE ES EL PELIGROSO: no cambia por corrida sino
#      por CLON -- en un checkout nuevo es la hora del clon --, de modo que el
#      diff daria rojo en otra maquina aunque el codigo fuera identico.
# Las rutas de salida tambien entran en la salida de la CLI, y por eso son fijas.
set -e
DIR="tests/linea_base_familia_c"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil \
        --json "$TMP/informe.json" \
        --html "$TMP/memoria.html" > "$TMP/cli.txt" 2>&1 || true

# 1 y 2: sello de la corrida.   3: mtime de criterios_adoptados.py.
# Los patrones son especificos a proposito: un barrido de fechas generico
# pisaria texto normativo. Medido en C0: en el HTML hay TRES fechas y las tres
# son volatiles; ninguna otra cadena coincide.
norm () {
  sed -e 's#[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}+00:00#<UTC>#g' \
      -e 's#[0-9]\{2\}/[0-9]\{2\}/[0-9]\{4\} [0-9]\{2\}:[0-9]\{2\}#<FECHA>#g' \
      -e "s#$TMP#<SALIDA>#g" "$1"
}
norm "$TMP/cli.txt"      > "$DIR/cli_perfil.txt"
norm "$TMP/memoria.html" > "$DIR/memoria_perfil.html"
echo "linea base regenerada en $DIR"
