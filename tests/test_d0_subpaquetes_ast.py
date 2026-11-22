# -*- coding: utf-8 -*-
"""
tests/test_d0_subpaquetes_ast.py
================================
Pruebas D0 (prerrequisito de D1): verifica que `src/indice_formulas.py` y
`src/variables_entrada.py` ven los archivos dentro de un subpaquete
`src/modulos/M*/` (y no solo `src/modulos/M*.py`) y atribuyen sus fundamentos
y variables al nombre del subpaquete de primer nivel.
"""
from __future__ import annotations

from pathlib import Path

from src import indice_formulas as ind
from src import variables_entrada as ve


def test_subpaquete_en_tmp_es_visto_por_indice_formulas_y_variables_entrada(
    tmp_path, monkeypatch
):
    falsa_src = tmp_path / "src"
    falsos_modulos = falsa_src / "modulos"
    subpaquete = falsos_modulos / "M99_prueba"
    subpaquete.mkdir(parents=True)
    (falsa_src / "__init__.py").write_text("", encoding="utf-8")
    (falsos_modulos / "__init__.py").write_text("", encoding="utf-8")
    (subpaquete / "__init__.py").write_text(
        "from src.modulos.M99_prueba.submodulo import calcular\n",
        encoding="utf-8",
    )
    (subpaquete / "constantes.py").write_text(
        'CRITERIO_EJEMPLO = "gamma_EQ"\n',
        encoding="utf-8",
    )
    (subpaquete / "submodulo.py").write_text(
        "from src import criterios_adoptados as ca\n"
        "from src.modelos import paso\n"
        "from src.modulos.M99_prueba.constantes import CRITERIO_EJEMPLO\n"
        "\n"
        "def calcular():\n"
        '    p = paso("F9.PRUEBA_D0", codigo="x", que="y")\n'
        '    return p, ca.valor(CRITERIO_EJEMPLO), "F9.MENCION_D0"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(ind, "SRC", falsa_src)
    monkeypatch.setattr(ind, "MODULOS", falsos_modulos)
    emisores = ind.emisores_por_fundamento()
    menciones = ind.menciones_del_fundamento()
    assert emisores.get("F9.PRUEBA_D0") == ("M99_prueba",)
    assert menciones.get("F9.PRUEBA_D0") == ("M99_prueba",)
    assert menciones.get("F9.MENCION_D0") == ("M99_prueba",)

    monkeypatch.setattr(ve, "_MODULOS", falsos_modulos)
    ve._analisis.cache_clear()
    ve._consumo_por_modulo.cache_clear()
    try:
        consumido = ve._consumo_por_modulo()
        assert "gamma_EQ" in consumido.get("M99_prueba", frozenset())
    finally:
        ve._analisis.cache_clear()
        ve._consumo_por_modulo.cache_clear()
