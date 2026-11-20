"""
tests/test_ve7_lote_c_voladizo.py
=================================
VE-7, lote C, item C1 (ficha VE6M9-01, abierto (c); decision del consultor
Fable, triaje VE-7, 2026-11-20): el 22.10.2.2 de E.060 -- los voladizos de
concreto ciclopeo mas largos que la mitad de su peralte se verifican en
flexion y corte -- tiene cita propia en el registro.

Hasta VE-7 la frase vivia SOLO en la nota de `E060.22.10.2#CICLOPEO` (pag.
195), y C7 de M9 la invocaba desde alli: una nota no la comprueba T2. La cita
nueva lleva el `Verbatim` que ya estaba transcrito, carácter EXIGENCIA («será
necesario»), y NO lleva firma: la sesion no tenia `NORMAS_DIR` y una firma
acredita una lectura del PDF que no se hizo. Queda censada en
`CITAS_SIN_FIRMA_A_PROPOSITO`, y T2 (`tests/test_normativa_pdf.py`) la
compara con su pagina en cada corrida que enlace el repositorio de normas.
El cambio de la cita principal de C7 en M9 lo hace el integrador.

--- VE-7, A11 (cierre, 2026-11-20) --- la sesion de cierre enlazo
`NORMAS_DIR`, comparo el Verbatim con la pagina 195 y FIRMO la cita; salio
del censo y es la cita principal de C7 en M9.
"""

from src.normativa import registro as _registro
from src.normativa.esquema import Caracter, Verbatim
from tests import test_normativa as tn

ID = "E060.22.10.2.2#VOLADIZO"
TEXTO = ("En elementos en voladizo con una longitud mayor a la mitad de su "
         "peralte, será necesario verificar las resistencias en flexión y "
         "corte")


def _reg():
    return _registro.construir()


def test_C1_la_cita_del_voladizo_existe_con_su_verbatim_y_su_pagina():
    c = _reg().cita(ID)
    assert c.fuente_id == "E060"
    assert c.numeral == "22.10.2.2"
    assert c.pagina_impresa == "195" and c.pagina_pdf == 195
    assert isinstance(c.texto_literal, Verbatim)
    assert c.texto_literal.texto == TEXTO
    assert c.texto_literal.pagina_pdf == 195
    assert c.caracter is Caracter.EXIGENCIA


def test_C1_el_verbatim_es_el_que_ya_estaba_transcrito_en_la_nota_del_ciclopeo():
    """Ningun texto literal se transcribe dos veces con dos redacciones."""
    origen = _reg().cita("E060.22.10.2#CICLOPEO")
    assert TEXTO in origen.nota
    assert origen.verificado is not None


def test_A11_la_cita_esta_firmada_y_fuera_del_censo():
    c = _reg().cita(ID)
    assert c.verificado is not None
    assert c.verificado.fecha == "2026-11-20"
    assert "A11" in c.verificado.por and "NORMAS_DIR" in c.verificado.por
    assert ID not in tn.CITAS_SIN_FIRMA_A_PROPOSITO
    assert ID not in tn.SIN_FIRMA_POR_SESION_SIN_PDF
    assert "SIN FIRMA A PROPOSITO" not in c.nota
    assert ("dictamen Fable 2026-11-20: aprobada con caducidad, se firma "
            "en la primera sesion con NORMAS_DIR") in c.nota


def test_A11_la_cita_principal_de_C7_es_la_del_voladizo():
    """C7 de M9 cita primero el 22.10.2.2 y conserva la del ciclopeo."""
    import inspect
    from src.modulos import M9_cabezal as M9
    fuente = inspect.getsource(M9._verificar_zapata_ciclopea)
    assert 'citas=("E060.22.10.2.2#VOLADIZO", "E060.22.10.2#CICLOPEO",' \
        in fuente


def test_C1_el_fundamento_del_ciclopeo_la_cita():
    """La cita tiene un consumidor: el fundamento que sostiene C1 a C8."""
    from src.normativa import fundamentos
    f = fundamentos.FUNDAMENTOS["F9.CICLOPEO"]
    assert ID in f.citas
