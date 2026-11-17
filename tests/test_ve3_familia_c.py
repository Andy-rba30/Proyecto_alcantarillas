"""
tests/test_ve3_familia_c.py
===========================
VE-3.6 y VE-3.7: lo que la ficha VC1-01 dejaba abierto de la Familia C (paso
de canal).

VE-3.6 · VC3, LA RASANTE HIDRAULICA DEL CANAL. La Sec. 2.3 de la hoja de ruta
prohibe que un cruce altere la rasante hidraulica del canal, y hasta aqui
solo habia un AVISO sin umbral (`M7.remanso_canal`, T-3): ninguna fuente de
normas/ decia como juzgarlo. El USBR «Design of Small Canal Structures»
(1978), num. 2-6, lo dice en su ejemplo de cruce de camino: F, el desnivel
de la lamina NORMAL del canal entre aguas arriba y aguas abajo del cruce que
el perfil del canal provee («F (water surface differential) = Upstream canal
NWS El. - Downstream canal NWS El.», pag. impresa 23), contra las perdidas
calculadas de la obra («Compare computed losses with the loss provided on
profile sheet», pag. impresa 24). VC3 mide las perdidas de la obra como la
diferencia de lamina entre su entrada y su salida,

    perdida = (cota_entrada + HW) - (cota_fondo_receptor + TW)  <=  F

y F es un dato del proyecto del CANAL (`desnivel_perfil_canal_m`, por
punto, de --datos-externos; ANA / Junta de Usuarios). Sin el dato VC3 no se
evalua y la corrida lo AVISA, como T-3 dejo el remanso sin seccion medida.

SE ESCRIBIO EN ROJO PRIMERO, contra 61a4dcc.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from src import servicio
from src.modelos import Familia, TipoDeVeredicto
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7
from src.normativa import registro
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_t3_familia_c import _punto_c01


CLAVE = "desnivel_perfil_canal_m"


def _vc3(F, *, entrada=36.30, HW=0.62, TW=0.41, fondo=36.20):
    punto = replace(_punto_c01(), cota_fondo_receptor=fondo)
    return M5.vc3_rasante_canal(punto=punto, cota_entrada_msnm=entrada,
                                HW=HW, TW=TW, desnivel_perfil_m=F)


def test_vc3_compara_las_perdidas_de_la_obra_con_el_desnivel_del_perfil():
    # perdida = (36.30 + 0.62) - (36.20 + 0.41) = 0.31 m
    no = _vc3(0.30)
    assert not no.cumple and no.codigo == "VC3"
    assert no.valor_obtenido == pytest.approx(0.31, rel=REL_TRANSPORTE)
    assert no.valor_admisible == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert no.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    si = _vc3(0.35)
    assert si.cumple and si.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


def test_vc3_en_el_borde_cumple_y_un_desnivel_cero_es_no_alterar():
    # La obra que no pierde nada respecto del canal cumple con F = 0.
    assert _vc3(0.0, entrada=36.20, HW=0.41, TW=0.41).cumple
    assert not _vc3(0.0, entrada=36.20, HW=0.42, TW=0.41).cumple


def test_vc3_sin_desnivel_declarado_no_se_evalua():
    assert _vc3(None) is None


def test_vc3_cita_al_usbr_y_su_fundamento_esta_registrado():
    v = _vc3(0.35)
    assert v.paso.umbral.cita_id == "USBR_DSCS.2-6#CHECK"
    assert "USBR_DSCS.2-6#F" in v.paso.citas_textuales
    reg = registro.construir()
    assert reg.cita("USBR_DSCS.2-6#CHECK").fuente_id == "USBR_DSCS"
    assert v.paso.fundamento_id == "F7.VC3"


def test_el_desnivel_es_una_clave_externa_de_la_familia_c_que_admite_cero():
    assert CLAVE in servicio.CLAVES_EXTERNAS
    assert servicio.familias_que_usan(CLAVE) == (Familia.C,)
    assert CLAVE in servicio.CLAVES_QUE_ADMITEN_CERO
    assert CLAVE in servicio.EXTERNOS_CON_VIA_ALTERNA


def _c01(cambios=()):
    informe = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
    return next(p for p in informe.puntos if p.punto.id == "C-01")


FONDO_EN_EL_CANAL = ("celda", "C-01", "cota_fondo_entrada", "36.30")
# DATO DE PRUEBA, no del juego: el juego no lleva una variante que cambie la
# seccion (parada c de T-11, `test_ninguna_variante_mueve_un_diametro_que_
# dimensiona`). 0.30 m es del orden de la caida propia del canal de C-01 en
# el cruce (S 0.006 x ~21 m = 0.13 m) mas una holgura de estructura.
F_DE_PRUEBA = 0.30


def test_VC3_va_en_la_tabla_de_la_fase_5_y_DIMENSIONA():
    """
    Con el fondo de entrada en el canal (36.30) y F = 0.30 m, el marco de
    1.20 x 0.90 m pierde 0.313 m y no cumple; la progresion pasa al de
    1.50 x 1.20 m, que pierde 0.227 m. Con F = 0.40 m basta el primero.
    """
    c01 = _c01((FONDO_EN_EL_CANAL, ("externo", "C-01", CLAVE, F_DE_PRUEBA)))
    assert c01.dimensionado
    assert c01.resultado.seccion.etiqueta() == "marco 1.50 × 1.20 m"
    vc3 = [v for v in c01.resultado.verificaciones if v.codigo == "VC3"]
    assert len(vc3) == 1 and vc3[0].cumple
    holgado = _c01((FONDO_EN_EL_CANAL, ("externo", "C-01", CLAVE, 0.40)))
    assert holgado.resultado.seccion.etiqueta() == "marco 1.20 × 0.90 m"


def test_pieza_vc3_solo_da_fila_en_un_paso_de_canal_con_el_desnivel():
    """La puerta de las dos tablas de la Fase 5 (`verificar` y perfil)."""
    from src.modelos import DatosDeExpediente
    c01 = _c01((FONDO_EN_EL_CANAL,))
    rh = c01.resultado.resultado_hidraulico
    punto = c01.punto_de_calculo
    assert M5.pieza_vc3(punto=punto, resultado=rh, expediente=None) is None
    assert M5.pieza_vc3(punto=punto, resultado=rh,
                        expediente=DatosDeExpediente()) is None
    v = M5.pieza_vc3(punto=punto, resultado=rh,
                     expediente=DatosDeExpediente(
                         desnivel_perfil_canal_m=F_DE_PRUEBA))
    assert v.codigo == "VC3"
    otro = replace(punto, familia=Familia.A)
    assert M5.pieza_vc3(punto=otro, resultado=rh,
                        expediente=DatosDeExpediente(
                            desnivel_perfil_canal_m=F_DE_PRUEBA)) is None


def test_un_desnivel_que_ninguna_seccion_alcanza_deja_el_punto_no_factible():
    c01 = _c01((FONDO_EN_EL_CANAL, ("externo", "C-01", CLAVE, 0.15)))
    assert not c01.dimensionado


def test_sin_el_desnivel_C01_avisa_que_VC3_no_se_evaluo():
    c01 = _c01()
    assert "VC3" not in [v.codigo for v in c01.resultado.verificaciones]
    assert any(M5.AVISO_VC3_SIN_DESNIVEL in a for a in c01.geometria.avisos)
    assert M7.AVISO_VC3_SIN_DESNIVEL is M5.AVISO_VC3_SIN_DESNIVEL
