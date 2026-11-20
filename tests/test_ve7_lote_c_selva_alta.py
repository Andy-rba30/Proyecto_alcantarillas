"""
tests/test_ve7_lote_c_selva_alta.py
===================================
VE-7, lote C, item C3 (VE5-CAT-01; decision del consultor Fable, triaje
VE-7, 2026-11-20): la condicion `COND-SELVA-ALTA` del num. 4.1.1.3.7 a) del
Manual de Hidrologia se resolvia `PorExpresion("region == 'selva_alta'")`
sobre un simbolo que nadie entregaba. Desde VE-5 (lote catlic) la region es
el [S] de corredor `region_natural`, y la condicion se resuelve con el:
`PorDatoDeSitio("region_natural")`. Los manifiestos generados no se
regeneran aqui (los sella el integrador).
"""

from src import datos_sitio as ds
from src import ventana_normativa as vn
from src.normativa import registro as _registro
from src.normativa.esquema import Efecto, PorDatoDeSitio


def _condicion():
    return _registro.construir().condicion("COND-SELVA-ALTA")


def test_C3_la_condicion_se_resuelve_con_el_dato_de_sitio_region_natural():
    c = _condicion()
    assert c.resuelve == PorDatoDeSitio(clave="region_natural")
    assert "region_natural" in ds.DATOS_SITIO
    assert ds.REGION_SELVA_ALTA in ds.dato("region_natural").opciones


def test_C3_el_efecto_y_la_cita_no_cambian_y_la_justificacion_nombra_el_dato():
    c = _condicion()
    assert c.cita_id == "MC_HHD.4.1.1.3.7a"
    assert c.efecto_si_indeterminada is Efecto.EXCLUYE
    assert "region_natural" in c.justificacion_de_no_bloquear


def test_C3_la_ventana_la_resuelve_por_el_dato_de_sitio():
    d = vn.disponibilidad_de(_condicion())
    assert isinstance(d, vn.Elegible)
    assert d.resuelta_por == "dato de sitio 'region_natural'"
