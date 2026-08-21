"""
tests/test_modo_rasante.py
===========================
El modo rasante de la CLI (paso 9 del encargo): el tamizado de Sec. 7.A con
puerta de entrada propia, M0 -> M2 -> M4 -> M7.tamizado_rasante, SIN exigir
dimensionamiento.

Lo que se fija aqui:

    - el barrido recorre el catalogo ENTERO de diametros, no solo el maximo,
      y la fila minima puede caer en un D interior (la cota minima no es
      monotona en D: subir D sube la clave pero baja el HW);
    - la cota minima es INVARIANTE frente al valor absoluto de la rasante
      provisional del CSV (desplazar rasante y subrasante juntas no la mueve);
    - Familia C sale como nota ("fuera del catalogo circular"), no como error;
    - concreto y TMC quedan bloqueados por 'h_relleno_min_concreto_tmc' sin
      frenar el barrido de HDPE;
    - sin L o TW declarados el punto se bloquea con el motivo escrito, no con
      una excepcion.
"""

import dataclasses
from pathlib import Path

import pytest

import cli
from modelos import Familia

CSV_EJEMPLO = Path(__file__).resolve().parent / "ejemplo_puntos.csv"


def _externos(**globales):
    base = {"luz_m": None, "TW_m": None, "longitud_m": None,
            "L_hidraulico_m": None, "categoria_tr": None}
    base.update(globales)
    return cli.cargar_datos_externos(None, base)


@pytest.fixture(scope="module")
def resultados():
    externos = _externos(TW_m=0.0, longitud_m=12.0)
    return cli.correr_modo_rasante(CSV_EJEMPLO, externos)


def _punto(resultados, id_punto):
    return next(r for r in resultados if r.punto.id == id_punto)


def test_el_tamizado_corre_sin_exigir_dimensionamiento(resultados):
    """
    Ningun punto del CSV de ejemplo llega hoy a dimensionado=True (V7
    pendiente bloquea la Fase 5), y aun asi el modo rasante produce la tabla:
    el tamizado es la generadora de la rasante y no depende del bucle de MD.
    """
    a01 = _punto(resultados, "A-01")
    assert a01.fila_minima is not None
    assert not a01.bloqueos


def test_barre_el_catalogo_entero_de_hdpe(resultados):
    """Una fila por cada D del catalogo (0.90 a 1.50), no solo el maximo."""
    a01 = _punto(resultados, "A-01")
    hdpe = next(m for m in a01.materiales if "HDPE" in m.material)
    assert [f.D for f in hdpe.filas] == pytest.approx(
        [0.90, 1.05, 1.20, 1.35, 1.50])
    for f in hdpe.filas:
        assert f.HW > 0
        assert f.control in ("entrada", "salida")
        assert f.cota_rasante_min == pytest.approx(
            max(f.cota_por_recubrimiento, f.cota_por_resguardo))


def test_la_cota_minima_no_es_monotona_y_puede_caer_en_un_D_interior(resultados):
    """
    La advertencia del docstring de M7, medida: en A-01 la fila minima es
    D = 1.20 m -- ni el primer ni el ultimo escalon del catalogo. Correr solo
    con D_max habria fijado la rasante mas arriba de lo necesario.
    """
    a01 = _punto(resultados, "A-01")
    hdpe = next(m for m in a01.materiales if "HDPE" in m.material)
    minima = hdpe.fila_minima
    assert minima.D == pytest.approx(1.20)
    assert minima.D not in (hdpe.filas[0].D, hdpe.filas[-1].D)
    for f in hdpe.filas:
        assert minima.cota_rasante_min <= f.cota_rasante_min


def test_la_cota_minima_es_invariante_frente_a_la_rasante_provisional(resultados):
    """
    El unico termino que toca la rasante del CSV es el espesor del paquete
    (rasante - subrasante), un dato de la seccion tipica: desplazar las dos
    cotas juntas (misma seccion, otra elevacion provisional) no mueve la cota
    minima. Es lo que permite correr el tamizado antes de que exista el
    perfil.
    """
    externos = _externos(TW_m=0.0, longitud_m=12.0)
    original = _punto(resultados, "A-01")

    punto = next(p for p in cli.cargar_puntos(CSV_EJEMPLO) if p.id == "A-01")
    desplazado = dataclasses.replace(punto,
                                     cota_rasante=punto.cota_rasante + 5.0,
                                     cota_subrasante=punto.cota_subrasante + 5.0)
    repetido = cli.tamizado_punto(desplazado, externos)

    filas_0 = next(m for m in original.materiales if "HDPE" in m.material).filas
    filas_5 = next(m for m in repetido.materiales if "HDPE" in m.material).filas
    assert [f.cota_rasante_min for f in filas_5] == pytest.approx(
        [f.cota_rasante_min for f in filas_0])
    assert [f.HW for f in filas_5] == pytest.approx([f.HW for f in filas_0])


def test_familia_c_es_nota_y_no_error(resultados):
    """Familia C: marco o multicelda, fuera del catalogo circular."""
    c01 = _punto(resultados, "C-01")
    assert c01.punto.familia is Familia.C
    assert c01.nota == cli.NOTA_FUERA_CATALOGO
    assert not c01.materiales
    assert c01.fila_minima is None


def test_concreto_y_tmc_bloqueados_no_frenan_a_hdpe(resultados):
    """
    'h_relleno_min_concreto_tmc' sigue vacio: concreto y TMC quedan anotados
    como bloqueados (con la clave del criterio en el motivo) y HDPE barre
    igual. El bloqueo de un material no aborta el punto.
    """
    a01 = _punto(resultados, "A-01")
    bloqueados = [m for m in a01.materiales if m.bloqueo]
    assert len(bloqueados) == 2
    assert all("h_relleno_min_concreto_tmc" in m.bloqueo for m in bloqueados)
    hdpe = next(m for m in a01.materiales if "HDPE" in m.material)
    assert hdpe.bloqueo is None and hdpe.filas


def test_sin_tw_ni_longitud_el_punto_se_bloquea_con_motivo():
    """Sin L y TW no hay control de salida: bloqueo escrito, no excepcion."""
    resultados = cli.correr_modo_rasante(CSV_EJEMPLO, _externos())
    a01 = _punto(resultados, "A-01")
    assert a01.fila_minima is None
    assert len(a01.bloqueos) == 1
    assert "longitud_m" in a01.bloqueos[0] and "TW_m" in a01.bloqueos[0]


def test_el_volcado_trae_la_tabla_y_la_nota_de_invariancia(resultados):
    texto = cli.volcar_rasante(resultados)
    assert "MODO RASANTE" in texto
    assert "invariante" in texto
    assert "Cota minima del punto" in texto
    assert "<- minima" in texto
    assert cli.NOTA_FUERA_CATALOGO in texto


def test_main_con_modo_rasante_imprime_y_devuelve_cero(capsys):
    codigo = cli.main([str(CSV_EJEMPLO), "--modo-rasante",
                       "--tw", "0.0", "--longitud", "12.0"])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "MODO RASANTE" in salida
    assert "Cota minima del punto" in salida


def test_main_bloqueado_devuelve_uno(capsys):
    codigo = cli.main([str(CSV_EJEMPLO), "--modo-rasante"])
    salida = capsys.readouterr().out
    assert codigo == 1
    assert "BLOQUEADO" in salida
