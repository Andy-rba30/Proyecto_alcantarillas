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

# ---------------------------------------------------------------------------
# La corrida de pruebas declara tambien la geometria fisica del conducto
# ---------------------------------------------------------------------------
# Cluster C01. El tamizado de 7.A y la flotacion V7 dejaron de correr con el
# diametro interior: la clave se mide sobre la superficie EXTERIOR (EG-2013
# 508.07, MAT-D4) y la subpresion sobre el volumen desplazado real (num.
# 2.4.3.8.2, MAT-D3). Eso pide dos datos que el proyecto NO tiene:
#
#   'espesor_pared_conducto'  el t de cada material. Es consecuencia de la
#                             clase, calibre o perfil que se especifique, y esa
#                             seleccion es el vacio que
#                             'clases_producto_por_relleno' ya declara abierto.
#   'condicion_pavimento'     que fila de la Tabla 12.6.6.3-1 de AASHTO LRFD
#                             aplica a esta via (NOR-VAC-01).
#
# LOS VALORES DE ABAJO SON DE LA CORRIDA DE PRUEBAS, NO DEL EXPEDIENTE. Entran
# por el mismo camino que usan la GUI y la CLI -- `establecer_valor_dinamico`,
# que pasa por la guardia `_verificar_criterio` -- y por eso la memoria los
# imprime en el bloque "DECLARADOS SOLO PARA ESTA CORRIDA": no estan en
# criterios_adoptados.py y no valen para ninguna otra corrida. Se eligieron
# para que sean RASTREABLES, no por comodidad:
#
#   concreto 0.100 m  espesor de pared B de C76/M 170M para D = 0.90 m
#                     (t = D/12 + 25 mm), la cifra que la propia ficha MAT-D4
#                     usa en su evidencia numerica.
#   tmc      0.013 m  altura de la corrugacion 68 x 13 mm, tamaño estandar
#                     para 900 mm en la Tabla 1 de ASTM A760/A760M-10. Es el
#                     espesor de perfil, sin el calibre de la plancha, que
#                     sigue abierto en 'clases_producto_por_relleno'.
#   hdpe     0.050 m  extremo BAJO del rango de altura de perfil corrugado que
#                     cita MAT-D4 (0.05-0.08 m); AASHTO M294 no esta en normas/.
#
# El proyectista que cierre el expediente no hereda ninguno de los tres: los
# declara el mismo, con la clase o el calibre que especifique.
ESPESOR_PARED_DE_PRUEBA = {
    "concreto_reforzado": 0.100,
    "tmc": 0.013,
    "hdpe": 0.050,
}
CLAVE_ESPESOR_PARED = "espesor_pared_conducto"

# 'flexible' es la fila de pavimento asfaltico, la corriente en un corredor
# vial de este tipo. No es la mas exigente de las tres ni la mas benigna: en
# concreto pide lo mismo que 'no_pavimentado' (Bc/8 >= 12 in) y mas que
# 'rigido' (9 in); en HDPE pide ID/2 >= 24 in, mucho mas que 'no_pavimentado'.
CLAVE_CONDICION_PAVIMENTO = "condicion_pavimento"
CONDICION_PAVIMENTO_DE_PRUEBA = "flexible"

# ---------------------------------------------------------------------------
# ...y las dos declaraciones de las que cuelga el recubrimiento del refuerzo
# ---------------------------------------------------------------------------
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
# TAMBIEN SON VALORES DE LA CORRIDA DE PRUEBAS, elegidos para ser rastreables:
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

_DECLARACIONES_DE_PRUEBA = {
    CLAVE_ORIGEN_COTA: ORIGEN_COTA_DE_PRUEBA,
    CLAVE_ESPESOR_PARED: ESPESOR_PARED_DE_PRUEBA,
    CLAVE_CONDICION_PAVIMENTO: CONDICION_PAVIMENTO_DE_PRUEBA,
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
