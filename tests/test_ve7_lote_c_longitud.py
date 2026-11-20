"""
tests/test_ve7_lote_c_longitud.py
=================================
VE-7, lote C, item C2 (decision del consultor Fable, triaje VE-7,
2026-11-20): el `por_que` de `F9.LONGITUD` dejaba leer como exigencia la
clausula que el HDS-5 3.3.5 escribe con «should» («the length should be
close to the approximate length»). El verbo NO cambia --el paso aplica
«must be fitted» (`HDS5_3ED.3.3.5#ENCAJE`, EXIGENCIA)--; cambia el texto:
lo de «cerca de la aproximada» es recomendacion, y la juzga el paso del
refinamiento, `F9.REFINAMIENTO_LONGITUD` (RECOMIENDA desde VE-6).
"""

from src.normativa import fundamentos as F
from src.normativa.esquema import Verbo


def _f():
    return F.FUNDAMENTOS["F9.LONGITUD"]


def test_C2_el_verbo_y_las_citas_no_cambian():
    f = _f()
    assert f.verbo is Verbo.OBLIGA
    assert f.citas == ("HDS5_3ED.3.3.5#ENCAJE", "HDS5_3ED.3.1.4#LONGITUD")


def test_C2_el_por_que_dice_que_la_cercania_es_recomendacion_y_nombra_el_refinamiento():
    texto = _f().por_que
    assert "La fuente pide que quede cerca" not in texto
    assert "«should»" in texto
    assert "recomendacion" in texto
    assert "F9.REFINAMIENTO_LONGITUD" in texto
    assert "F9.REFINAMIENTO_LONGITUD" in F.FUNDAMENTOS
