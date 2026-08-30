"""
conftest.py
===========
Hace importables los dos arboles que usan los tests:

    src/   -> modulos planos, tal como los nombra el Anexo C de la hoja de ruta
              (`from criterios_adoptados import valor`)
    raiz   -> `from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING`

Sin esto, pytest solo agrega el directorio del test al path y ninguno de los
dos imports funciona.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"

for ruta in (RAIZ, SRC):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))


# ---------------------------------------------------------------------------
# La corrida de pruebas declara el origen de la cota de fondo de entrada
# ---------------------------------------------------------------------------
# 'origen_cota_fondo_entrada' es un vacio real (SIS-A-04): la cota del fondo
# de la entrada no es columna del CSV, no la fija ninguna norma, y hasta la
# correccion de C08 M5 adoptaba `cota_terreno` por su cuenta. Ahora la elige
# el proyectista, y sin declaracion V4, V7 y el tamizado 7.A se detienen.
# Desde C01 no es el unico: ver el bloque siguiente.
#
# La suite tiene que correr con la eleccion hecha, igual que corre una obra:
# se declara aqui por el MISMO camino que usan la GUI y la CLI
# (`establecer_valor_dinamico`, que pasa por la guardia `_verificar_criterio`),
# no parcheando `CRITERIOS` ni el modulo M5. Se hace al importar conftest --
# antes que cualquier modulo de test -- para que las listas que los tests
# calculan a nivel de modulo (`criterios_sin_valor()`) vean el mismo estado
# que las pruebas.
#
# Los tests que verifican el BLOQUEO lo retiran DENTRO del test con
# `quitar_valor_dinamico`: si alguna vez este bloque se borra, esos tests
# siguen probando lo suyo y el resto de la suite falla en masa, que es la
# señal correcta.
#
# Va en dos sitios y no en uno: al importar, para las listas que los modulos
# de test calculan a nivel de modulo, y en una fixture autouse, porque varios
# tests llaman `limpiar_valores_dinamicos()` -- que borra TODAS las
# declaraciones de la corrida, incluida esta -- y sin reponerla el resto de
# la suite caeria por un efecto de orden de ejecucion.
import pytest  # noqa: E402


def pytest_configure(config):
    """
    Registra la marca `pdf`, que separa los tests que ABREN un PDF de
    `normas/` del resto de la suite.

    Existe porque las dos mitades tienen precondiciones distintas:

      - los estructurales corren siempre, con `requirements.txt` a secas;
      - los de PDF necesitan `PyMuPDF` (que vive en `requirements-dev.txt`,
        porque es dependencia de TEST y no del software calculado) y los
        250 MB de `normas/`. Se SALTAN, no fallan, si falta cualquiera de las
        dos cosas.

    Para correr solo los de PDF:  pytest -m pdf
    Para excluirlos:              pytest -m "not pdf"
    """
    config.addinivalue_line(
        "markers",
        "pdf: abre un PDF de normas/; exige PyMuPDF (requirements-dev.txt)")

import criterios_adoptados as _ca  # noqa: E402

CLAVE_ORIGEN_COTA = "origen_cota_fondo_entrada"
ORIGEN_COTA_DE_PRUEBA = "cota_terreno"
CLAVE_ESPESOR_PARED = "espesor_pared_conducto"
CLAVE_CONDICION_PAVIMENTO = "condicion_pavimento"
CONDICION_PAVIMENTO_DE_PRUEBA = "flexible"

# ---------------------------------------------------------------------------
# Los DOS materiales que el expediente no puede declarar, para la corrida de
# pruebas
# ---------------------------------------------------------------------------
# 'espesor_pared_conducto' quedo declarado en el expediente SOLO para el
# concreto reforzado, y no por descuido: es el unico de los tres materiales
# cuya norma de producto esta en `normas/` (AASHTO M 170M-04, columna «Wall
# Thickness» de la pared B). El TMC depende del calibre de plancha que fija la
# Fase 8 -- 'clases_producto_por_relleno', que es de expediente y sigue
# abierto -- y el HDPE sale de AASHTO M294, que no esta en el repositorio. En
# una corrida real los dos se descartan como candidatos con su causa escrita,
# y el punto se dimensiona en concreto.
#
# LOS TESTS UNITARIOS DE M7 Y M5 SI LOS NECESITAN, porque prueban FORMULAS --
# la clave fisica, el volumen desplazado, el tamizado de 7.A -- sobre
# materiales sinteticos, y una formula no se puede probar con un material que
# se detiene antes de entrar en ella. Se declaran aqui, con el mismo rotulo
# que siempre: valores DE LA CORRIDA DE PRUEBAS, que la memoria imprime en el
# bloque "DECLARADOS SOLO PARA ESTA CORRIDA".
#
#   tmc   0.013 m  altura de la corrugacion 68 x 13 mm, tamaño estandar para
#                  900 mm en la Tabla 1 de ASTM A760/A760M-10. Es el espesor
#                  de perfil, sin el calibre de la plancha.
#   hdpe  0.050 m  extremo BAJO del rango de altura de perfil corrugado que
#                  cita la ficha MAT-D4 (0.05-0.08 m).
#
# La columna del concreto NO se copia: se LEE del criterio y se le añaden los
# dos materiales que faltan. Copiarla aqui crearia una segunda transcripcion
# de trece filas de una tabla normativa, que es exactamente lo que este
# repositorio persigue.
ESPESOR_TMC_DE_PRUEBA = 0.013      # m
ESPESOR_HDPE_DE_PRUEBA = 0.050     # m

# ---------------------------------------------------------------------------
# TRES DECLARACIONES SE RETIRARON DE AQUI EN S20, y hay que decir por que
# ---------------------------------------------------------------------------
# 'origen_cota_fondo_entrada', 'espesor_pared_conducto' y
# 'condicion_pavimento' se declaraban en este archivo, como valores DE LA
# CORRIDA DE PRUEBAS, porque el expediente los tenia vacios y sin ellos la
# suite entera se detenia. En S20 los tres se cerraron en
# `criterios_adoptados.py` -- son criterios de NIVEL DE PERFIL y el cierre de
# ese nivel era la tarea --, de modo que declararlos aqui ya no rellenaba un
# vacio: TAPABA el valor del expediente con otro.
#
# El caso que lo hizo visible es 'espesor_pared_conducto'. Este archivo lo
# declaraba como un espesor por material {concreto: 0.100, tmc: 0.013, hdpe:
# 0.050}, que era la forma correcta cuando el espesor se creia unico por
# material. Al pasar el criterio a la columna «Wall Thickness» completa por
# DIAMETRO DESIGNADO, esa declaracion dejo de ser un valor de prueba
# razonable y paso a ser un valor de la forma equivocada, con el que la suite
# fallaba en veintitantos tests a la vez.
#
# Las claves y los rotulos se conservan porque varios tests los importan para
# RETIRAR la declaracion y comprobar el bloqueo (`quitar_valor_dinamico`), y
# esa es la prueba que no se puede perder: si mañana alguien vacia el
# criterio en el archivo, esos tests siguen probando lo suyo.

# Cluster C07. El lado AASHTO de la regla del recubrimiento mayor dejo de ser
# un valor declarado (75 mm) y pasa a calcularse -- fila de la tabla, columna
# por categoria de acero, modificador por relacion a/c, piso de 1.0 in --, de
# modo que necesita dos cosas que el expediente no tiene:
#
#   'categoria_refuerzo_aashto'  la columna A/B/C de la Tabla 5.10.1-1. La fija
#                                la especificacion del acero que se compra.
#   'exposicion_quimica_ems'     el analisis quimico del EMS, del que sale la
#                                relacion a/c maxima y con ella el modificador.
#
# LAS DOS SIGUEN SIENDO VALORES DE LA CORRIDA DE PRUEBAS, y siguen aqui
# porque las dos son de NIVEL DE EXPEDIENTE: el cierre del nivel de perfil no
# las alcanza, y la Fase 9 que las consume la difiere `--alcance perfil`.
# Entran por el mismo camino que usan la GUI y la CLI --
# `establecer_valor_dinamico`, que pasa por la guardia `_verificar_criterio`
# -- y por eso la memoria las imprime en el bloque "DECLARADOS SOLO PARA ESTA
# CORRIDA". Se eligieron para ser RASTREABLES, no por comodidad:
#
#   categoria "A"   acero sin recubrir. Es la columna que el expediente venia
#                   usando sin decirlo (los 75 mm eran sus 3.0 in redondeados
#                   a la baja), asi que la corrida queda comparable con el
#                   estado anterior y ademas es la que MAS recubrimiento pide.
#   exposicion      sulfatos "insignificante" (0.0 %) y cloruros SI. Es la
#                   combinacion que deja ver cual fila gobierna: sin requisito
#                   por sulfatos, la relacion a/c que sale es la 0.40 de la
#                   fila de cloruros de la Tabla 4.2 -- la misma que el
#                   expediente afirmaba en prosa -- y el factor resulta 0.8.
#                   El 0.0 de sulfatos NO afecta al recubrimiento (cualquier
#                   fila de la Tabla 4.4 da a/c >= 0.45, y la nota al pie
#                   manda quedarse con la MENOR de las dos tablas); afecta al
#                   f'c minimo y al tipo de cemento, que este calculo no usa.
#
# El proyectista que cierre el expediente no hereda ninguna de las dos.
CLAVE_CATEGORIA_REFUERZO = "categoria_refuerzo_aashto"
CATEGORIA_REFUERZO_DE_PRUEBA = "A"
CLAVE_EXPOSICION_QUIMICA = "exposicion_quimica_ems"
EXPOSICION_QUIMICA_DE_PRUEBA = {
    "so4_suelo_pct": 0.0,
    "so4_agua_ppm": None,
    # LAS TRES FILAS DE LA TABLA 4.2, declaradas una por una. No estan las
    # tres por prolijidad: "la MENOR relacion a/c aplicable" de la nota al pie
    # es una comparacion, y con una fila sin declarar la comparacion se hacia
    # sobre un conjunto incompleto sin que nada avisara. Una clave ausente es
    # DatoInvalidoError, no un "no aplica".
    "tabla_4_2": {
        "baja_permeabilidad": False,
        "congelamiento_deshielo": False,
        "cloruros": True,
    },
}

# El barrido de diametros de la corrida de pruebas. Va de 300 a 3600 mm en
# pasos de 75 -- un superconjunto de las tres series de producto -- porque
# varios tests unitarios usan diametros SINTETICOS que ninguna serie tiene
# (0.60 m, por ejemplo, que esta por debajo del piso normativo de 0.90 m y se
# usa a proposito para probar que la formula no depende del catalogo). Es un
# rango de PRUEBA: el expediente declara solo los trece diametros que la
# norma de producto imprime.
_DIAMETROS_DE_PRUEBA_MM = tuple(range(300, 3601, 75))


def _espesor_pared_de_prueba():
    """La columna del expediente mas los dos materiales que no puede tener."""
    del_expediente = _ca.CRITERIOS[CLAVE_ESPESOR_PARED].valor
    return {
        **del_expediente,
        "tmc": {mm: ESPESOR_TMC_DE_PRUEBA for mm in _DIAMETROS_DE_PRUEBA_MM},
        "hdpe": {mm: ESPESOR_HDPE_DE_PRUEBA for mm in _DIAMETROS_DE_PRUEBA_MM},
    }


ESPESOR_PARED_DE_PRUEBA = _espesor_pared_de_prueba()

_DECLARACIONES_DE_PRUEBA = {
    CLAVE_ESPESOR_PARED: ESPESOR_PARED_DE_PRUEBA,
    CLAVE_CATEGORIA_REFUERZO: CATEGORIA_REFUERZO_DE_PRUEBA,
    CLAVE_EXPOSICION_QUIMICA: EXPOSICION_QUIMICA_DE_PRUEBA,
}


def _declarar_criterios_de_prueba():
    for clave, valor in _DECLARACIONES_DE_PRUEBA.items():
        _ca.establecer_valor_dinamico(clave, valor)


_declarar_criterios_de_prueba()


@pytest.fixture(autouse=True)
def _criterios_de_corrida_declarados():
    """Repone las declaraciones de la corrida antes de cada test."""
    _declarar_criterios_de_prueba()
    yield
