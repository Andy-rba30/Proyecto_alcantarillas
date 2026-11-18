"""
tests/test_ve3_19_maximos_repetidos.py — los maximos anuales repetidos (VE3-19)
==============================================================================
El hallazgo H1 de la verificacion independiente de la hidrologia con casos
reales (dossier `proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/
hidrologia/hidrologia_casos_reales.md`, §3.4): en la serie de Cañaveral de la
tesis de UNTumbes (Tabla 23, p. 60) 2002 es copia de 1989 y 2001 de 1996, mes
a mes. Con la entrada que el contrato pide --un maximo anual por año-- la
copia NO es demostrable: dos maximos iguales son normales (8 de las 10 series
reales del dossier los tienen). La recomendacion, aceptada: AVISAR, sin
umbral, en el aviso de consistencia que ya existe (paso 1b.3c,
`MH._paso_consistencia`), con los valores repetidos y sus años; no detener,
no deduplicar y no juzgar.

COMO SE MIDIO EL ROJO: este archivo se escribio y se corrio ANTES de tocar
`MH_hidrologia` (falla por `AttributeError: maximos_anuales_repetidos` y por
la nota sin el renglon). El oraculo del recuento es la tabla del dossier
§3.4, medida por el verificador sobre los documentos, no la salida del
programa.

LOS DATOS SON DE CASOS REALES PUBLICADOS (`tests/fixtures/
hidrologia_casos_reales/`, rotulados): no son datos de este proyecto.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.modelos import TipoDeVeredicto
from src.modulos import MH_hidrologia as MH
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados

CASOS = Path(__file__).resolve().parent / "fixtures" / "hidrologia_casos_reales"
FEN = "homogeneidad_serie_fen"


def _serie(caso: str, archivo: str, estacion: str):
    return MH.cargar_estacion(CASOS / caso / archivo)[estacion]


def _tumbes():
    return _serie("untumbes_tu107",
                  "estacion_fen_declarado_por_el_verificador.csv", "Cañaveral")


def _consistencia(pasos):
    (p,) = [x for x in pasos if x.codigo == MH.CODIGO_CONSISTENCIA]
    return p


def test_tumbes_los_dos_valores_copiados_con_sus_años():
    """Tabla 24, p. 61: 129.00 en 1989 y 2002; 63.00 en 1996 y 2001."""
    repetidos = MH.maximos_anuales_repetidos(_tumbes())
    assert [anios for _v, anios in repetidos] == [(1989, 2002), (1996, 2001)]
    assert [v for v, _anios in repetidos] == pytest.approx(
        [129.0, 63.0], rel=REL_TRANSPORTE)


def test_tumbes_el_aviso_lo_dice_sin_juzgar_ni_detener_ni_quitar():
    serie = _tumbes()
    with declarados({FEN: "serie_completa"}):
        ajuste, *_, pasos, _ = MH.precipitacion_de_diseno(serie, 70)
    p = _consistencia(pasos)
    nota = p.nota_del_proyecto
    assert "129.0 mm (1989 y 2002)" in nota
    assert "63.0 mm (1996 y 2001)" in nota
    for trozo in ("no distingue", "registro mensual o diario"):
        assert trozo in nota, trozo
    # Sin umbral ni veredicto, y la serie entra ENTERA al ajuste.
    assert p.umbral is None
    assert p.veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    assert ajuste.n == len(serie.registros) == 40


def test_una_serie_sin_repetidos_no_lleva_el_renglon():
    serie = _serie("upao_la_jalca", "estacion.csv", "Chachapoyas-A")
    assert MH.maximos_anuales_repetidos(serie) == ()
    with declarados({FEN: "serie_completa"}):
        *_, pasos, _ = MH.precipitacion_de_diseno(serie, 50)
    assert "se repiten" not in _consistencia(pasos).nota_del_proyecto


def test_un_valor_tres_veces_lleva_los_tres_años():
    """La Argelia (ESPOL, Anexo 2): un valor aparece en tres años."""
    serie = _serie("espol_intervalles", "estacion.csv", "La Argelia")
    repetidos = MH.maximos_anuales_repetidos(serie)
    assert sorted(len(anios) for _, anios in repetidos) == [2, 3]
    with declarados({FEN: "serie_completa"}):
        *_, pasos, _ = MH.precipitacion_de_diseno(serie, 50)
    (tres,) = [anios for _, anios in repetidos if len(anios) == 3]
    nota = _consistencia(pasos).nota_del_proyecto
    assert f"{tres[0]}, {tres[1]} y {tres[2]}" in nota


# El recuento de la tabla del dossier, §3.4: cuantos VALORES distintos se
# repiten en cada una de las diez series reales.
RECUENTO_DEL_DOSSIER = [
    ("indeci_piura", "estacion.csv", "Miraflores", 3),
    ("upeu_colpahuayco", "estacion.csv", "Sicuani", 4),
    ("untumbes_tu107", "estacion_fen_declarado_por_el_verificador.csv",
     "Cañaveral", 2),
    ("unsaac_42tmc", "estacion.csv", "Colquepata", 2),
    ("espol_intervalles", "estacion.csv", "La Argelia", 2),
    ("espol_intervalles", "estacion.csv", "Gonzanama", 1),
    ("espol_intervalles", "estacion.csv", "Malacatos", 3),
    ("espol_intervalles", "estacion.csv", "Catamayo", 2),
    ("upao_la_jalca", "estacion.csv", "Chachapoyas-A", 0),
    ("upao_la_jalca", "estacion.csv", "Chachapoyas-B", 0),
]


@pytest.mark.parametrize("caso, archivo, estacion, n", RECUENTO_DEL_DOSSIER,
                         ids=[f[2] for f in RECUENTO_DEL_DOSSIER])
def test_el_recuento_de_las_diez_series_reales(caso, archivo, estacion, n):
    assert len(MH.maximos_anuales_repetidos(_serie(caso, archivo, estacion))) == n


def test_el_modulo_no_gana_un_umbral_de_repeticion():
    """
    Ningun numero de corte (cuantas repeticiones, que cociente): la unica
    tolerancia es la de representacion, nombrada en `tolerancias.py`.
    """
    import ast
    arbol = ast.parse(Path(MH.__file__).read_text(encoding="utf-8"))
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
    sospechosos = {x for x in nombres if "REPETID" in x.upper()
                   and any(t in x.upper() for t in ("UMBRAL", "LIMITE", "CORTE",
                                                     "MINIMO", "MAXIMO_N"))}
    assert not sospechosos, sospechosos
