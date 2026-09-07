#!/bin/sh
# Regenera la LINEA BASE de la Familia C. La abrio C0 y la usan C1 en adelante
# como DIFF: un refactor o una bifurcacion no pueden mover ningun numero, y
# esto es contra que se comprueba.
#
# Se corre desde la raiz del repositorio:   sh tests/linea_base_familia_c/regenerar.sh
#
# ---------------------------------------------------------------------------
# POR QUE ENSANCHO C3, y no es celo
# ---------------------------------------------------------------------------
# La ventana de C0 miraba UNA corrida: alcance perfil, sin TW, tirando el JSON
# y sin el CSV de resumen, y de los cuatro puntos del fixture solo UNO llegaba
# a dimensionarse. Costo dos veces:
#
#   C1 metio una REGRESION DE SALIDA IMPRESA -- renombro el `motivo` de un
#   DatoInvalidoError -- y esta linea base no la vio, porque la rama de error
#   necesita un `--declarar` para alcanzarse.
#   C2 escribio mal la ecuacion Forma 2 en un docstring, y quien lo encontro
#   fue un auditor leyendo el codigo: la linea base no tenia como verlo.
#
# C3 la ensancha en cuatro ejes a la vez:
#   (a) el JSON deja de tirarse -- es la salida que un tablero externo lee;
#   (b) entra el CSV de resumen, entregable 3 de la Fase 11;
#   (c) entra la corrida a ALCANCE EXPEDIENTE, con su plantilla propia;
#   (d) entran los CUATRO puntos con datos suficientes para avanzar: con
#       TW declarado, TRES de los cuatro dimensionan en vez de uno, y C-01
#       -- el punto de Familia C -- deja de detenerse por falta de TW y llega
#       hasta su bloqueo REAL, el que dice que el catalogo de la Sec. 3.2 no
#       ofrece marco. Ese bloqueo es justo lo que C4 y C5 van a cambiar, de
#       modo que a partir de aqui el cambio se ve en el diff.
#
# LAS ENTRADAS AMPLIADAS SON UN FIXTURE, NO DATOS DE PROYECTO, y viven en
# `entradas_ampliadas.json` con esa advertencia escrita. El TW y el caudal de
# C-01 estan ahi para EJERCITAR CAMINOS DE CODIGO; no son una medicion de
# campo ni pretenden serlo.
#
# LA CORRIDA ESTRECHA DE C0 SE CONSERVA INTACTA -- misma linea de comando y
# mismos dos archivos -- para que el diff historico siga siendo comparable.
#
# ---------------------------------------------------------------------------
# POR QUE NORMALIZA, y no es cosmetica
# ---------------------------------------------------------------------------
# La corrida trae TRES campos volatiles, y sin retirarlos el diff da rojo por
# razones que no son el cambio:
#   1. `generado (UTC): <iso>` en la salida de la CLI y `generado_utc` en el JSON.
#   2. `corrida UTC: <iso>` y la misma fecha en formato local, en el HTML.
#   3. `Fecha de criterios_adoptados.py` en el HTML, que M11 saca de
#      `ruta.stat().st_mtime`. ESTE ES EL PELIGROSO: no cambia por corrida sino
#      por CLON -- en un checkout nuevo es la hora del clon --, de modo que el
#      diff daria rojo en otra maquina aunque el codigo fuera identico.
# Las rutas de salida tambien entran en la salida de la CLI, y por eso son fijas.
set -e
DIR="tests/linea_base_familia_c"
EXT="$DIR/entradas_ampliadas.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- 1 · la corrida ESTRECHA de C0, sin tocar -------------------------------
python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil \
        --json "$TMP/informe.json" \
        --html "$TMP/memoria.html" > "$TMP/cli.txt" 2>&1 || true

# --- 2 · la corrida ANCHA, a nivel de perfil --------------------------------
python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil \
        --datos-externos "$EXT" \
        --json "$TMP/informe_ancho.json" \
        --html "$TMP/memoria_ancha.html" \
        --csv-resumen "$TMP/resumen_ancho.csv" > "$TMP/cli_ancho.txt" 2>&1 || true

# --- 3 · la corrida ANCHA, a nivel de EXPEDIENTE ----------------------------
# Otra plantilla (memoria_alcantarillas.html) y otras fases: las 8 y 9 se
# ejecutan en vez de diferirse.
python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance expediente \
        --datos-externos "$EXT" \
        --json "$TMP/informe_exp.json" \
        --html "$TMP/memoria_exp.html" \
        --csv-resumen "$TMP/resumen_exp.csv" > "$TMP/cli_exp.txt" 2>&1 || true

# Los patrones son especificos a proposito: un barrido de fechas generico
# pisaria texto normativo. Medido en C0: en el HTML hay TRES fechas y las tres
# son volatiles; ninguna otra cadena coincide.
norm () {
  sed -e 's#[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}+00:00#<UTC>#g' \
      -e 's#[0-9]\{2\}/[0-9]\{2\}/[0-9]\{4\} [0-9]\{2\}:[0-9]\{2\}#<FECHA>#g' \
      -e "s#$TMP#<SALIDA>#g" "$1"
}
norm "$TMP/cli.txt"           > "$DIR/cli_perfil.txt"
norm "$TMP/memoria.html"      > "$DIR/memoria_perfil.html"

norm "$TMP/cli_ancho.txt"     > "$DIR/cli_perfil_ancho.txt"
norm "$TMP/memoria_ancha.html" > "$DIR/memoria_perfil_ancha.html"
norm "$TMP/informe_ancho.json" > "$DIR/informe_perfil_ancho.json"
norm "$TMP/resumen_ancho.csv"  > "$DIR/resumen_perfil_ancho.csv"

norm "$TMP/cli_exp.txt"       > "$DIR/cli_expediente.txt"
norm "$TMP/memoria_exp.html"  > "$DIR/memoria_expediente.html"
norm "$TMP/informe_exp.json"  > "$DIR/informe_expediente.json"
norm "$TMP/resumen_exp.csv"   > "$DIR/resumen_expediente.csv"
echo "linea base regenerada en $DIR (10 archivos: 2 de la ventana estrecha de C0 + 8 de la ancha)"
