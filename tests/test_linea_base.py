"""
tests/test_linea_base.py
========================
LA LINEA BASE DE LA FAMILIA C, CONSUMIDA POR LA SUITE.

Hasta C3.5 esta linea base solo «miraba» si alguien se acordaba de correr
`regenerar.sh` a mano. Eso la hacia exactamente igual de fragil que el
manifiesto anclado por linea: dependia de disciplina, no de la suite. Y la
auditoria de C3 lo demostro midiendo, no opinando -- una mutacion que cambiaba
la etiqueta de ecuacion impresa en las TRES memorias de produccion dejaba la
suite en 1547 passed --.

Este test cierra ese hueco: corre el MISMO script y compara. No reimplementa
la corrida -- le pasa un destino y contrasta --, de modo que sigue habiendo UNA
definicion de la linea base y no dos que puedan divergir.

QUE HACER SI FALLA, y no es regenerar a ciegas. El mensaje nombra los archivos
que se movieron. Hay que MIRAR EL DIFF y decidir cual de las dos cosas es:

  * un numero de calculo se movio  -> es una regresion; se arregla el codigo.
  * la salida cambio A PROPOSITO   -> se regenera con
                                      `sh tests/linea_base_familia_c/regenerar.sh`
                                      Y SE DECLARA en el commit que linea
                                      cambio y por que.

Las dos veces que esta linea base sirvio de verdad -- C1 y C3 -- el cambio fue
de una sola linea, y la diferencia entre las dos lecturas se decidio leyendola.

LO QUE ESTE TEST NO PUEDE VER, Y HAY QUE SABERLO PARA NO CONFIARSE. La linea
base solo ve lo que el FIXTURE EJERCITA. Medido con tres mutaciones:

    A · cablear `forma = 1` en el paso de memoria     -> NO lo ve  (hasta C3.5)
    B · invertir la etiqueta de ecuacion (A.1)/(A.2)  -> lo ve
    C · renombrar el `motivo` de un DatoInvalidoError -> lo ve

LA A YA NO SE ESCAPA, Y ESO ES LO QUE C4 CAMBIO. Se le escapaba porque
NINGUN PUNTO DEL FIXTURE USABA FORMA 2: las tres cartas circulares del
catalogo son Forma 1, de modo que suponerla no movia un byte. C4 añadio la
quinta corrida --`punto_cajon.py`, una seccion rectangular con una carta de
cajon de la Tabla A.1, que es Forma 2--. Vuelto a medir sobre este mismo
arbol, con las dos mutaciones que la Forma 2 admite:

    A · `forma = FORMA_1` cableada en `_pasos_hidraulicos` (la ETIQUETA)
        -> MUEVE `memoria_punto_cajon.html`. Antes no movia nada.
    B · la Forma 2 deja de bifurcar en el CALCULO y se aplica la ec. (A.1)
        -> HW de control de entrada  1.576717 m  ->  3.031241 m
           (+1.454524 m, que es H_c/D + Ks*S sobre la altura del marco)

La direccion de B es al ALZA en este punto, y conviene no confundirla con la
de `CP5D_FORMA2_KS_ESPUREO`: aquella mide la mitad Ks*S sola --30 mm a la
BAJA, no conservadora-- y esta mide las dos mitades juntas, con el H_c/D
dominando. Las dos son la misma familia de defecto y solo una de ellas tiene
signo peligroso; por eso el caso patron fija la que lo tiene y la linea base
fija que el conjunto se mueve.

Las dos capas siguen siendo COMPLEMENTARIAS y ninguna sustituye a la otra:
los tests unitarios cubren caminos que el corredor no recorre; la linea base
cubre la composicion entera -- las cinco corridas, los dos alcances, el JSON,
el CSV y ahora las dos formas de seccion --.

LA QUINTA CORRIDA NO ES LA CLI, y hay que saberlo: la CLI no puede producir
un cajon hasta que C5 abra el catalogo de M2. El driver llama a M3 y a M4
directamente. No es un diseño --no pasa por la Fase 5-- y su propio docstring
declara las tres decisiones de C5 que toma prestadas para poder correr.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "tests" / "linea_base_familia_c"
SCRIPT = DIR / "regenerar.sh"

# Los generados. `regenerar.sh`, `README.md` y `entradas_ampliadas.json` son
# ENTRADAS del proceso, no salidas, y por eso no se comparan.
NO_GENERADOS = {"regenerar.sh", "README.md", "entradas_ampliadas.json",
                "punto_cajon.py"}


def _generados_comprometidos():
    return {f.name for f in DIR.iterdir()
            if f.is_file() and f.name not in NO_GENERADOS}


@pytest.fixture(scope="module")
def recien_generada(tmp_path_factory):
    """Corre el script contra un destino temporal. No toca el arbol."""
    destino = tmp_path_factory.mktemp("linea_base")
    r = subprocess.run(["sh", str(SCRIPT), str(destino)], cwd=RAIZ,
                       capture_output=True, text=True)
    assert r.returncode == 0, (
        f"`regenerar.sh` fallo con codigo {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}")
    return destino


def test_la_linea_base_comprometida_es_la_que_produce_el_codigo(recien_generada):
    """
    EL TEST QUE HACE QUE LA VENTANA DEJE DE DEPENDER DE QUE ALGUIEN SE ACUERDE.

    Compara byte a byte cada salida. Un `assert` por archivo seria mas comodo
    de leer, pero da UN fallo y esconde los otros once: aqui se recogen todos
    y el mensaje los lista, porque saber si se movio una memoria o se movieron
    las tres es la mitad del diagnostico.
    """
    movidos = []
    for nombre in sorted(_generados_comprometidos()):
        esperado = (DIR / nombre).read_bytes()
        obtenido = (recien_generada / nombre).read_bytes()
        if esperado != obtenido:
            movidos.append(
                f"{nombre}: {len(esperado)} bytes comprometidos, "
                f"{len(obtenido)} generados")
    assert not movidos, (
        "la salida del programa ya no es la que la linea base tiene "
        "comprometida:\n  " + "\n  ".join(movidos)
        + "\n\nMIRA EL DIFF antes de regenerar. Si se movio un numero de "
        "calculo es una regresion y se arregla el codigo; si la salida "
        "cambio a proposito, regenera con `sh "
        "tests/linea_base_familia_c/regenerar.sh` y DECLARA en el commit que "
        "linea cambio y por que.")


def test_el_script_no_produce_salidas_sin_comprometer(recien_generada):
    """
    La otra mitad: si alguien AÑADE una corrida al script y no compromete su
    archivo, la ventana crece en el papel y no en el repositorio. Esto lo
    caza -- y tambien el caso inverso, un archivo comprometido que el script
    ya no produce y que se quedaria congelado para siempre --.
    """
    generados = {f.name for f in recien_generada.iterdir() if f.is_file()}
    comprometidos = _generados_comprometidos()
    assert generados == comprometidos, (
        f"sin comprometer: {sorted(generados - comprometidos)} | "
        f"comprometidos y ya no generados: "
        f"{sorted(comprometidos - generados)}")


def test_la_corrida_es_determinista(recien_generada, tmp_path):
    """
    Sin determinismo, el test de arriba seria intermitente y acabaria
    desactivado. C0 midio que la corrida trae TRES campos volatiles -- dos
    sellos de reloj y el mtime de criterios_adoptados.py, que cambia POR CLON
    y no por corrida --, y `regenerar.sh` los normaliza. Esto comprueba que
    la normalizacion sigue cubriendolos.
    """
    segunda = tmp_path / "segunda"
    r = subprocess.run(["sh", str(SCRIPT), str(segunda)], cwd=RAIZ,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    distintos = [f.name for f in sorted(recien_generada.iterdir())
                 if f.is_file()
                 and f.read_bytes() != (segunda / f.name).read_bytes()]
    assert not distintos, (
        f"dos corridas del mismo arbol dieron bytes distintos en {distintos}: "
        "hay un campo volatil que la normalizacion de `regenerar.sh` no cubre")


def test_la_ventana_cubre_los_ejes_que_dice_cubrir(recien_generada):
    """
    LA VENTANA MIDE LO QUE DICE MEDIR, y no de palabra. Cada assert de aqui
    corresponde a un eje que el README declara, y esta escrito para que
    ESTRECHARLA rompa un test en vez de pasar inadvertido -- que es como llego
    a estar estrecha en primer lugar --.
    """
    lee = lambda n: (recien_generada / n).read_text(encoding="utf-8")

    # (a) los dos alcances, con sus plantillas distintas
    assert "perfil" in lee("cli_perfil.txt")
    assert "expediente" in lee("cli_expediente.txt")

    # (b) el JSON y el CSV de resumen, que la ventana de C0 tiraba
    assert '"generado_utc"' in lee("informe_perfil_ancho.json")
    assert lee("resumen_perfil_ancho.csv").strip(), "el CSV de resumen vino vacio"

    # (c) TRES de los cuatro puntos dimensionan en la corrida ancha; en la
    # estrecha de C0 solo uno. Si alguien estrecha las entradas, esto cae.
    ancho = lee("cli_perfil_ancho.txt")
    assert ancho.count("Fase 4  sin dimensionar") == 1
    assert lee("cli_perfil.txt").count("Fase 4  sin dimensionar") == 3

    # (d) C-01, el punto de Familia C, llega a su bloqueo REAL -- el que C4 y
    # C5 van a cambiar -- y no se detiene antes por falta de TW.
    assert "no ofrece material candidato para la Familia C" in ancho

    # (d-bis) EL PUNTO DE CAJON, el eje que añadio C4: una seccion NO
    # circular resuelta por una carta de FORMA 2. Es lo que hace visible aqui
    # la mutacion A, que hasta C3.5 solo cazaban los tests unitarios. Se
    # comprueban las tres cosas que la hacen visible -- que la seccion es un
    # marco, que la carta es de Forma 2 y que la rama aplicada es la que usa
    # la ec. (A.2) pura --, porque si cualquiera de las tres se pierde la
    # ceguera vuelve sin que nada avise.
    cajon = lee("memoria_punto_cajon.html")
    assert "marco 2.00 × 1.50 m" in cajon
    assert "Equation Form 2" in cajon
    assert "regimen entrada    no_sumergido" in cajon
    assert "critico cerrado    True" in cajon

    # (e) LA RAMA DE ERROR, que es la que motivo el ensanche: es la que C1
    # movio sin que nada lo viera. Se comprueban las DOS cadenas -- `campo` y
    # `motivo` --, porque C1 renombro la segunda dejando la primera intacta.
    err = lee("cli_rama_error.txt")
    assert "Dato invalido en 'D'" in err
    assert "el diametro debe ser positivo" in err
    assert "el diametro debe ser positivo" in lee("informe_rama_error.json")
