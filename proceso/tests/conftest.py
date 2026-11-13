"""
proceso/tests/conftest.py
=========================
El `conftest` de la suite de PROCESO (T-12, INF-5.2.2).

Los tests de esta carpeta comprueban el material del proceso de desarrollo
que T-12 movio a `proceso/` —el tracker de auditorias, los temarios, la copia
de la cadena T, la cobertura de la auditoria de sistema, `verificar_sesion`—
y por eso NO son parte de la suite del entregable: `python -m pytest` desde
la raiz recoge solo `tests/` (`testpaths` en `pyproject.toml`). Se corren
aparte, desde la raiz:

    python -m pytest proceso/tests

El `conftest.py` de la raiz sigue aplicando (es el de la carpeta raiz de la
corrida): pone la raiz en el camino de importacion, registra las marcas y
aisla el estado de proceso entre tests. Este solo marca cada test recogido
aqui con `proceso`, para que una corrida conjunta (`python -m pytest tests
proceso/tests`) pueda separarlos con `-m "not proceso"`.
"""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "proceso: test del material de proceso (proceso/tests); no es de la "
        "suite del entregable")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "proceso" in item.nodeid.split("/")[0:1]:
            item.add_marker(pytest.mark.proceso)
