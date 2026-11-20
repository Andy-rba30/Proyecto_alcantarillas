"""
tests/test_ve6_m9_alero.py
==========================
Lote M9 del censo, item 9 (VE3-14 H-13, T7B-08 (3), T7C-04), VE-6: el alero
se ARMA POR SUS PROPIAS SECCIONES (AASHTO LRFD Seccion 5: «All sections
shall be designed for the applicable factored loads»), no con la
solicitacion de la pantalla, y su espesor se DIMENSIONA por su propio armado,
no copiando el de la pantalla.

Cada seccion del alero es el fuste de un muro en voladizo de altura variable
(baja con el talud de h0 a H_f a lo largo del alero): la franja vertical a la
fraccion f de su longitud esta (h0 - H_f)·f mas abajo que el arranque, con
su propio espesor, sobre su propia zapata (`Aleros.ancho_zapata`,
`Aleros.espesor_zapata`, toda como talon) y con el relleno que sube detras de
ella hasta la plataforma. Dos secciones: el arranque (f = 0), que arma el
tramo de 0 a L/2, y la mitad (f = 1/2), que arma el tramo de L/2 a L; con la
altura que baja, la mas alta de cada tramo es la que rige.

Escrito ANTES del codigo; los dorados, a mano sobre el muro de tanteo de T-7b.
"""

import math
from dataclasses import replace

import pytest

from src import criterios_adoptados as ca
from src.modelos import (Aleros, CondicionAnalisis, ELEMENTO_ALEROS,
                         SECCION_ALERO, SECCION_PANTALLA)
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import ABS_CERO
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD as CPB
from tests.test_t7c_cabezal_armado import _geometria, tanteo  # noqa: F401

EST = CondicionAnalisis.ESTATICO
TOL = 1e-9
TOL_DORADO = CPB["tolerancia"]

# Los aleros del muro de tanteo: arrancan a la altura del cabezal (h0 =
# coronacion - pie = 102.55 - 100.80 = 1.75 m) y bajan a H_f = 0.40 m; la
# zapata del alero, 1.20 x 0.37 m; el alero, 0.25 m.
ALEROS = Aleros(angulo_grados=45.0, angulo_largo_grados=45.0,
                esviaje_grados=0.0, longitud_corto=2.5, longitud_largo=2.5,
                altura_inicial=1.75, altura_final=0.40, espesor=0.25,
                ancho_zapata=1.20, espesor_zapata=0.37)
CAIDA_MITAD = (1.75 - 0.40) / 2          # 0.675 m


def _con_aleros(tanteo, aleros=ALEROS):
    return replace(tanteo, geometria=_geometria(aleros=aleros))


def test_la_seccion_del_alero_es_un_muro_propio(tanteo):
    """
    A mano: la franja de la mitad baja 0.675 m. Su muro: H = (2.00 + 0.40)
    - 0.37 - 0.675 = 1.355 m sobre su zapata de 0.37 m; espesor 0.25 m;
    zapata de 1.20 m, toda talon (0.95 m tras el fuste); corona y relleno
    0.675 m mas abajo. El arranque (f = 0) no baja.
    """
    entorno = _con_aleros(tanteo)
    x = M9.entorno_de_la_seccion_del_alero(entorno, M9.FRACCION_MITAD_ALERO)
    g = x.geometria
    assert M9.FRACCION_MITAD_ALERO == pytest.approx(0.5, abs=ABS_CERO)
    assert g.H == pytest.approx(2.40 - 0.37 - CAIDA_MITAD, abs=TOL)
    assert g.espesor_zapata == pytest.approx(0.37, abs=TOL)
    assert g.espesor_corona == g.espesor_base_muro == pytest.approx(0.25,
                                                                   abs=TOL)
    assert g.B == pytest.approx(1.20, abs=TOL)
    assert g.ancho_punta == pytest.approx(0.0, abs=TOL)
    assert g.ancho_talon == pytest.approx(0.95, abs=TOL)
    assert g.cota_coronacion == pytest.approx(102.55 - CAIDA_MITAD, abs=TOL)
    assert g.aleros is None
    assert x.cota_relleno == pytest.approx(entorno.cota_relleno - CAIDA_MITAD,
                                           abs=TOL)
    # lo absoluto no se mueve: el desplante, el freatico, el borde
    assert g.cota_desplante == entorno.geometria.cota_desplante
    assert x.cota_borde_plataforma == entorno.cota_borde_plataforma
    assert x.cota_freatico == entorno.cota_freatico
    arranque = M9.entorno_de_la_seccion_del_alero(entorno, 0.0)
    assert arranque.geometria.H == pytest.approx(2.40 - 0.37, abs=TOL)
    assert arranque.cota_relleno == entorno.cota_relleno


def test_el_relleno_de_la_mitad_sube_detras_de_ella(tanteo):
    """
    A mano, con `geometria_del_relleno`: z_rel = 2.40 - 0.675 = 1.725 m; el
    relleno sube 0.675 m hasta la plataforma; sobre el talon de 0.95 m sube
    min(0.95/1.5, 0.675) = 0.6333 m: h = 2.3583 m.
    """
    x = M9.entorno_de_la_seccion_del_alero(_con_aleros(tanteo),
                                           M9.FRACCION_MITAD_ALERO)
    r = M9.geometria_del_relleno(x)
    assert r["z_rel"] == pytest.approx(2.40 - CAIDA_MITAD, abs=TOL)
    assert r["subida"] == pytest.approx(CAIDA_MITAD, abs=TOL)
    assert r["h"] == pytest.approx(2.40 - CAIDA_MITAD + 0.95 / 1.5, abs=TOL)


def test_el_alero_se_arma_en_dos_secciones_con_su_propio_ensamble(tanteo):
    """
    Las dos secciones del alero, cada una con las solicitaciones del fuste
    de SU franja (`solicitaciones_de_resistencia` de la seccion): ni la
    pantalla ni la otra seccion. La de la mitad pide menos.
    """
    entorno = _con_aleros(tanteo)
    piezas = M9.armar_elemento(entorno, ELEMENTO_ALEROS)
    assert [p.clave for p in piezas] == [SECCION_ALERO, M9.SECCION_ALERO_MITAD]
    for p, f in zip(piezas, (0.0, M9.FRACCION_MITAD_ALERO), strict=True):
        assert p.elemento == ELEMENTO_ALEROS
        assert p.espesor == pytest.approx(0.25, abs=ABS_CERO)
        sol = M9.solicitaciones_de_resistencia(
            M9.entorno_de_la_seccion_del_alero(entorno, f))
        propias = sol["secciones"][SECCION_PANTALLA]
        assert [s.M_u for s in p.solicitaciones] == pytest.approx(
            [s.M_u for s in propias], abs=TOL)
        assert p.rige_flexion in p.solicitaciones
    arranque, mitad = piezas
    assert max(s.M_u for s in mitad.solicitaciones) < max(
        s.M_u for s in arranque.solicitaciones)
    assert mitad.As_resistencia < arranque.As_resistencia
    assert "L/2" in arranque.seccion and "L/2" in mitad.seccion
    codigos = {v.codigo for p in piezas for v in p.verificaciones}
    assert {"A1.alero.e", "A1.alero_mitad.e"} <= codigos


def test_dorado_a_mano_del_momento_estatico_de_la_mitad(tanteo):
    """
    Con el diagrama del plano virtual ('carga_pantalla_cabezal' =
    'plano_virtual_del_talon') y el muro que cede, la Resistencia I de la
    franja de la mitad, a mano sobre el arranque de su fuste (z = 0.37 m),
    con el K_A de su propio ensamble (la cuña sobre el relleno que sube):

        M_EH = K_A·cos(delta + beta)·gamma·(h - 0.37)³/6
        M_LS = K_A·gamma·h_eq·(h - 0.37)²/2
        M_u  = 1.50·M_EH + 1.75·M_LS
    """
    ca.establecer_valor_dinamico("carga_pantalla_cabezal",
                                 "plano_virtual_del_talon")
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 "cedente")
    x = M9.entorno_de_la_seccion_del_alero(_con_aleros(tanteo),
                                           M9.FRACCION_MITAD_ALERO)
    _, d = M9.cargas_del_cabezal(x, EST)
    alto = d["h"] - 0.37
    M_EH = (d["K_A"] * math.cos(d["inclinacion"]) * d["gamma"] * alto ** 3
            / 6)
    M_LS = d["K_A"] * d["gamma"] * d["h_eq"] * alto ** 2 / 2
    M_u = 1.50 * M_EH + 1.75 * M_LS
    mitad = M9.armar_elemento(_con_aleros(tanteo), ELEMENTO_ALEROS)[1]
    resistencia = [s for s in mitad.solicitaciones
                   if s.condicion is EST and s.combinacion.startswith(
                       "Resistencia I")]
    assert resistencia
    for s in resistencia:
        assert s.M_u_cedente == pytest.approx(M_u, rel=TOL_DORADO)


def test_sin_caida_el_alero_tiene_una_sola_seccion(tanteo):
    plano = replace(ALEROS, altura_final=ALEROS.altura_inicial)
    piezas = M9.armar_elemento(_con_aleros(tanteo, plano), ELEMENTO_ALEROS)
    assert [p.clave for p in piezas] == [SECCION_ALERO]


def test_las_incumplidas_de_la_pantalla_y_del_alero_van_por_separado(tanteo):
    """
    La pantalla crece por SU armado y el alero por el SUYO: cada lista solo
    trae los codigos de su elemento.
    """
    entorno = _con_aleros(tanteo)
    pantalla = M9.incumplidas_del_armado_de_la_pantalla(entorno) or ()
    alero = M9.incumplidas_del_armado_del_alero(entorno) or ()
    assert all(".pantalla." in c for c in pantalla)
    assert all(".alero" in c for c in alero)
    # un alero de 0.10 m no cumple su armado
    delgado = _con_aleros(tanteo, replace(ALEROS, espesor=0.10))
    assert M9.incumplidas_del_armado_del_alero(delgado)


def test_un_alero_mas_grueso_que_su_zapata_se_rechaza(tanteo):
    from src.modelos import DatoInvalidoError
    ancho = _con_aleros(tanteo, replace(ALEROS, espesor=1.30))
    with pytest.raises(DatoInvalidoError):
        M9.entorno_de_la_seccion_del_alero(ancho, M9.FRACCION_MITAD_ALERO)



def test_el_ancho_de_la_seccion_de_la_mitad_es_el_de_su_franja(tanteo,
                                                              monkeypatch):
    """
    Dictamen Fable de VE-6: el ancho con que se arma la seccion de la mitad
    (el del acero de temperatura de 5.10.6) es min(H de SU franja, longitud
    del alero), no el de la altura inicial.
    """
    entorno = _con_aleros(tanteo)
    vistos = {}
    original = M9.diseno_flexion_corte

    def espia(**kw):
        vistos[kw["clave"]] = kw["ancho_seccion"]
        return original(**kw)

    monkeypatch.setattr(M9, "diseno_flexion_corte", espia)
    M9.armar_elemento(entorno, ELEMENTO_ALEROS)
    x = M9.entorno_de_la_seccion_del_alero(entorno, M9.FRACCION_MITAD_ALERO)
    assert vistos[M9.SECCION_ALERO_MITAD] == pytest.approx(
        min(x.geometria.H, max(ALEROS.longitudes)), abs=TOL)
    assert vistos[SECCION_ALERO] == pytest.approx(
        min(ALEROS.altura_inicial, max(ALEROS.longitudes)), abs=TOL)


def test_el_armado_avisa_que_el_alero_no_se_verifica_como_muro(tanteo):
    a = M9.armado_del_cabezal(_con_aleros(tanteo))
    assert any("no verificado como muro" in x and "T7C-04" in x
               for x in a.avisos)
    assert not any("no verificado como muro" in x
                   for x in M9.armado_del_cabezal(tanteo).avisos)
