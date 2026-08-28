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

import criterios_adoptados as _ca  # noqa: E402

CLAVE_ORIGEN_COTA = "origen_cota_fondo_entrada"
ORIGEN_COTA_DE_PRUEBA = "cota_terreno"

_ca.establecer_valor_dinamico(CLAVE_ORIGEN_COTA, ORIGEN_COTA_DE_PRUEBA)


@pytest.fixture(autouse=True)
def _origen_cota_entrada_declarado():
    """Repone la declaracion de 'origen_cota_fondo_entrada' antes de cada test."""
    _ca.establecer_valor_dinamico(CLAVE_ORIGEN_COTA, ORIGEN_COTA_DE_PRUEBA)
    yield
