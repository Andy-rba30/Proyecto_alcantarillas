"""
tests/test_n3_hec11_filtro.py
=============================
N3 del plan 12 (2026-11-24): el FILTRO GRANULAR bajo el enrocado de salida por
HEC-11 (version metrica), Sec. 4.4.1, a la que HEC-14 remite la manta de filtro
del apron, y el espesor de la capa de enrocado con el receptor alto por la Sec.
4.3.

EL ORACULO ES EL EJEMPLO 1 DE LA FUENTE (paso 13, PDF 66 a 68, leido por
imagen: las razones son graficos): suelo de D85 = 0.032 m y D15 = 0.001 m,
enrocado de D15 = 0.18 m y grava de D15 = 0.030 m y D85 = 0.061 m. La fuente
imprime las razones redondeadas («= 6 > 5», «= 180 > 40», «= 0.94 < 5», «= 30
> 5 and < 40», «= 3 < 5», «= 6 > 5 and < 40») y concluye «a filter layer is
needed» y «the 50 mm filter material is adequate». El Ejemplo 2 (PDF 81-82) no
se usa: rotula mal una razon y acepta «5 ≥ 5» (nota de `fuentes.HEC11`).
"""

from __future__ import annotations

import pytest

import cli
from src import servicio
from src.constantes_normativas import (
    HEC11_FILTRO_ESPESOR_UNA_CAPA_M, HEC11_FILTRO_ESPESOR_VARIAS_CAPAS_M,
    HEC11_FILTRO_PASA_200_MAX_PCT, HEC11_TABLA_2)
from src import criterios_adoptados as ca
from src.modelos import (
    DatoFaltanteError, DatoInvalidoError, Magnitud, MaterialLecho,
    TipoDeVeredicto)
from src.modulos import M6_proteccion as M6
from src.normativa import registro as _registro
from tests.apoyo.aproximacion import REL_TRANSPORTE

# Tolerancias de este archivo, nombradas (CLAUDE.md).
REL_EJEMPLO_IMPRESO = 0.12   # la fuente imprime UNA cifra: 5.625 sale «6»
REL_EJEMPLO_DOS_CIFRAS = 0.01  # «0.94», «30», «180», «6» exactos a 2 cifras
REL_FORMULA = 1e-9           # una formula recomputada a mano en el test

# El Ejemplo 1 (PDF 61: «D85 = 0.032 m», «D15 = 0.001 m»; PDF 66-68).
D85_SUELO, D15_SUELO = 0.032, 0.001
D15_ENROCADO = 0.18
D15_GRAVA, D85_GRAVA = 0.030, 0.061


def _una_curva(D15_grueso, D85_fino, D15_fino):
    return M6.relaciones_de_filtro_hec11(
        D15_grueso_min=D15_grueso, D15_grueso_max=D15_grueso,
        D85_fino=D85_fino, D15_fino=D15_fino)


# ===========================================================================
# 1 · La Ec. (14) contra el Ejemplo 1 de la fuente
# ===========================================================================

def test_ejemplo_1_el_enrocado_no_puede_ir_directo_sobre_el_suelo():
    """PDF 66: «0.18/0.032 = 6 > 5», «0.18/0.001 = 180 > 40»."""
    r = _una_curva(D15_ENROCADO, D85_SUELO, D15_SUELO)
    assert r.tubificacion == pytest.approx(6, rel=REL_EJEMPLO_IMPRESO)
    assert r.uniformidad == pytest.approx(180, rel=REL_EJEMPLO_DOS_CIFRAS)
    assert not r.cumple_tubificacion and not r.cumple_uniformidad
    assert not r.cumple          # «Therefore, a filter layer is needed.»


def test_ejemplo_1_la_interfaz_filtro_suelo_cumple():
    """PDF 66: «0.030/0.032 = 0.94 < 5», «0.030/0.001 = 30 > 5 and < 40»."""
    r = _una_curva(D15_GRAVA, D85_SUELO, D15_SUELO)
    assert r.tubificacion == pytest.approx(0.94, rel=REL_EJEMPLO_DOS_CIFRAS)
    assert r.permeabilidad == pytest.approx(30, rel=REL_EJEMPLO_DOS_CIFRAS)
    assert r.cumple              # «Therefore, filter to soil interface is OK.»


def test_ejemplo_1_la_interfaz_enrocado_filtro_cumple():
    """PDF 67-68: «0.18/0.061 = 3 < 5», «0.18/0.030 = 6 > 5 and < 40»."""
    r = _una_curva(D15_ENROCADO, D85_GRAVA, D15_GRAVA)
    assert r.tubificacion == pytest.approx(3, rel=REL_EJEMPLO_IMPRESO)
    assert r.permeabilidad == pytest.approx(6, rel=REL_EJEMPLO_DOS_CIFRAS)
    assert r.cumple              # «the 50 mm filter material is adequate»


def test_ejemplo_1_la_grava_de_la_fuente_cae_en_la_ventana_de_una_capa():
    """
    Con la curva del enrocado del ejemplo (D15 = 0.18 m): D15 de la grava
    entre max(5·0.001, 0.18/40) = 0.005 y min(5·0.032, 40·0.001, 0.18/5) =
    0.036 m, y D85 desde 0.18/5 = 0.036 m. La grava del ejemplo (0.030 y
    0.061 m) cae dentro, como la fuente concluye.
    """
    v = M6.ventana_del_filtro_granular_hec11(
        D85_suelo=D85_SUELO, D15_suelo=D15_SUELO,
        D15_enrocado_min=D15_ENROCADO, D15_enrocado_max=D15_ENROCADO)
    assert v.una_capa_basta
    assert v.D15_mayor_que == pytest.approx(0.005, rel=REL_FORMULA)
    assert v.D15_hasta == pytest.approx(0.036, rel=REL_FORMULA)
    assert not v.D15_hasta_admitido     # lo fija la permeabilidad: estricto
    assert v.D85_desde == pytest.approx(0.036, rel=REL_FORMULA)
    assert v.D15_mayor_que < D15_GRAVA < v.D15_hasta
    assert D85_GRAVA >= v.D85_desde


def test_con_la_banda_de_la_tabla_2_la_ventana_es_mas_estrecha():
    """
    Lo que la `Interpretacion` de HEC11.4.2#T2 declara EN CONTRA: con la
    banda del D15 de la piedra de D50 = 0.29 m (0.116 a 0.174 m) la grava del
    Ejemplo 1 (D15 = 0.030 m) queda fuera: 0.116/5 = 0.0232 m.
    """
    e_min, e_max = M6.banda_d15_del_enrocado_hec11(0.29)
    assert (e_min, e_max) == pytest.approx((0.4 * 0.29, 0.6 * 0.29),
                                           rel=REL_FORMULA)
    v = M6.ventana_del_filtro_granular_hec11(
        D85_suelo=D85_SUELO, D15_suelo=D15_SUELO, D15_enrocado_min=e_min,
        D15_enrocado_max=e_max)
    assert v.D15_hasta == pytest.approx(0.116 / 5, rel=REL_FORMULA)
    assert not D15_GRAVA < v.D15_hasta


# ===========================================================================
# 2 · Los bordes de la Ec. (14): «5 or less», «exceed 5», «less than 40»
# ===========================================================================

def test_la_tubificacion_admite_el_5_y_las_otras_dos_son_estrictas():
    justo = _una_curva(0.05, 0.01, 0.005)        # 5.0 y 10.0
    assert justo.tubificacion == pytest.approx(5.0, rel=REL_FORMULA)
    assert justo.cumple_tubificacion
    en_5 = _una_curva(0.05, 0.05, 0.01)          # D15/D15 = 5.0
    assert not en_5.cumple_permeabilidad
    en_40 = _una_curva(0.40, 0.40, 0.01)         # D15/D15 = 40.0
    assert not en_40.cumple_uniformidad


def test_una_curva_desordenada_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        M6.relaciones_de_filtro_hec11(D15_grueso_min=0.2, D15_grueso_max=0.1,
                                      D85_fino=0.01, D15_fino=0.001)
    with pytest.raises(DatoInvalidoError):
        _una_curva(0.1, 0.001, 0.01)


# ===========================================================================
# 3 · El requisito: con datos, sin datos, una capa que no basta
# ===========================================================================

def test_sin_la_granulometria_el_granular_se_declara_sin_numeros():
    f = M6.requisito_de_filtro()
    g = f.granular
    assert g is not None and g.una_capa_basta is None
    assert g.D15_filtro_hasta is None and g.directo_sobre_el_suelo is None
    assert not g.pasos
    assert "material_lecho_salida.D85_m" in g.texto
    assert "Si es GRANULAR" in f.texto
    assert g.pasa_200_max_pct == HEC11_FILTRO_PASA_200_MAX_PCT
    assert set(M6.CITAS_DEL_FILTRO_GRANULAR) <= set(f.citas)


def test_el_filtro_granular_suelto_es_la_alternativa_del_requisito():
    """
    `filtro_granular_hec11` es la pieza que `requisito_de_filtro` suma al
    geotextil: llamada sola da el mismo granular, con y sin la granulometria,
    y publica siempre los dos intervalos de espesor de HEC-11 Sec. 4.4.1.
    """
    for datos in ({}, dict(D85_suelo=D85_SUELO, D15_suelo=D15_SUELO,
                           d50_enrocado=0.29)):
        solo = M6.filtro_granular_hec11(**datos)
        assert solo == M6.requisito_de_filtro(**datos).granular
        assert solo.espesor_una_capa_m == pytest.approx(
            HEC11_FILTRO_ESPESOR_UNA_CAPA_M, rel=REL_TRANSPORTE)
        assert solo.espesor_varias_capas_m == pytest.approx(
            HEC11_FILTRO_ESPESOR_VARIAS_CAPAS_M, rel=REL_TRANSPORTE)


def test_con_la_granulometria_el_requisito_emite_los_dos_pasos():
    f = M6.requisito_de_filtro(D85_suelo=D85_SUELO, D15_suelo=D15_SUELO,
                               d50_enrocado=0.29)
    g = f.granular
    assert [p.codigo for p in g.pasos] == ["6.7f", "6.7g"]
    directo, ventana = g.pasos
    assert directo.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert directo.umbral.cita_id == "HEC11.4.4.1#EC_14"
    assert directo.fundamento_id == "F6.FILTRO_GRANULAR"
    assert ventana.veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    assert g.una_capa_basta and not g.avisos
    assert g.D85_filtro_desde == pytest.approx(0.6 * 0.29 / 5, rel=REL_FORMULA)
    assert "LECTURA DEL PROYECTO" in directo.nota_del_proyecto


def test_si_una_capa_no_basta_se_avisa_con_la_frase_de_la_fuente():
    """Un limo fino bajo una piedra de 0.55 m: la ventana queda vacia."""
    f = M6.requisito_de_filtro(D85_suelo=0.0013, D15_suelo=0.00014,
                               d50_enrocado=0.55)
    g = f.granular
    assert g.una_capa_basta is False and g.D15_filtro_hasta is None
    assert M6.CITA_VARIAS_CAPAS in g.citas
    literal = _registro.construir().cita(M6.CITA_VARIAS_CAPAS).texto_literal.texto
    assert any(literal in a for a in f.avisos)
    assert "dos o mas capas" in g.texto


def test_con_un_lecho_cohesivo_no_hay_ventana_y_se_avisa_el_geotextil():
    """
    Dictamen del consultor: HEC-11 Sec. 4.4 pide el filtro «on noncohesive
    material»; con un lecho cohesivo la Ec. (14) queda fuera del marco de la
    fuente, los pasos salen como informacion, la via es el geotextil y no se
    dice que hagan falta varias capas aunque la ventana quede vacia.
    """
    f = M6.requisito_de_filtro(D85_suelo=0.0013, D15_suelo=0.00014,
                               d50_enrocado=0.55, tipo_lecho="cohesivo")
    g = f.granular
    assert g.una_capa_basta is None and g.D15_filtro_hasta is None
    assert [p.codigo for p in g.pasos] == ["6.7f", "6.7g"]
    assert "COHESIVO" in g.texto and "geotextil" in g.texto
    assert "dos o mas capas" not in g.texto
    assert M6.CITA_VARIAS_CAPAS not in g.citas
    assert "HEC11.4.4#CUANDO" in g.citas
    literal = _registro.construir().cita("HEC11.4.4#CUANDO").texto_literal.texto
    assert any(literal in a for a in f.avisos)
    assert not any("must be used" in a for a in f.avisos)


def test_el_geotextil_lleva_cama_de_grava_con_una_piedra_mayor_que_091_m():
    con = M6.requisito_de_filtro(d50_enrocado=1.0)
    assert con.cama_de_grava_bajo_geotextil is True
    assert M6.CITA_CAMA_DE_GRAVA in con.citas and "cama de grava" in con.texto
    assert M6.requisito_de_filtro(d50_enrocado=0.5
                                  ).cama_de_grava_bajo_geotextil is False
    assert M6.requisito_de_filtro().cama_de_grava_bajo_geotextil is None


def test_la_proteccion_de_salida_pasa_la_piedra_que_rige_al_filtro():
    V = Magnitud("V_salida", 3.0, "m/s", "dato del test")
    p = M6.proteccion_salida(V=V, D85_lecho=D85_SUELO, D15_lecho=D15_SUELO)
    assert p.filtro.granular.d50_enrocado == pytest.approx(p.d50,
                                                           rel=REL_FORMULA)
    assert {"6.7f", "6.7g"} <= {x.codigo for x in p.pasos}
    sin = M6.proteccion_salida(V=V)
    assert not ({"6.7f", "6.7g"} & {x.codigo for x in sin.pasos})


def test_el_json_publica_el_filtro_granular():
    V = Magnitud("V_salida", 3.0, "m/s", "dato del test")
    p = M6.proteccion_salida(V=V, D85_lecho=D85_SUELO, D15_lecho=D15_SUELO)
    g = cli._proteccion_json(p)["filtro"]["granular"]
    assert g["una_capa_basta"] is True
    assert g["directo_sobre_el_suelo"]["cumple"] is False
    assert g["espesor_una_capa_m"] == list(HEC11_FILTRO_ESPESOR_UNA_CAPA_M)


# ===========================================================================
# 4 · El dato: `material_lecho_salida.D85_m` y `.D15_m`
# ===========================================================================

def test_D85_y_D15_entran_sin_tipo_y_juntos():
    d = servicio._material_lecho_externo({"D85_m": 0.032, "D15_m": 0.001},
                                         "test")
    assert d.valor == MaterialLecho(D85_m=0.032, D15_m=0.001)


@pytest.mark.parametrize("uno, falta", [({"D85_m": 0.032}, "D15_m"),
                                        ({"D15_m": 0.001}, "D85_m")])
def test_uno_sin_el_otro_es_dato_faltante_del_otro(uno, falta):
    """Dictamen del consultor: si el revisor tiene que AÑADIR, es Faltante."""
    with pytest.raises(DatoFaltanteError) as e:
        servicio._material_lecho_externo(uno, "test")
    assert e.value.campo == f"material_lecho_salida.{falta}"


def test_el_D85_tiene_techo_de_transcripcion_opt_in():
    """Dictamen del consultor: el D85 en metros escrito en milimetros."""
    assert ("D85_m", "material_lecho_salida", "m") in \
        M6.DATOS_CON_TECHO_DE_TRANSCRIPCION
    lecho = MaterialLecho(D85_m=32.0, D15_m=1.0)
    dato = {"material_lecho_salida": lecho}.get
    assert M6.avisos_de_transcripcion(dato) == []      # sin declarar: nada
    ca.establecer_valor_dinamico("techos_de_transcripcion_fase_6",
                                 {"D85_m": 1.0})
    try:
        avisos = M6.avisos_de_transcripcion(dato)
    finally:
        ca.quitar_valor_dinamico("techos_de_transcripcion_fase_6")
    assert len(avisos) == 1 and "material_lecho_salida.D85_m" in avisos[0]


@pytest.mark.parametrize("malo", [
    {"D85_m": 0.001, "D15_m": 0.032},                       # D85 < D15
    {"tipo": "no_cohesivo", "D84_m": 0.03, "D16_m": 0.002,
     "D85_m": 0.02, "D15_m": 0.001},                        # D85 < D84
    {"tipo": "no_cohesivo", "D84_m": 0.03, "D16_m": 0.002,
     "D85_m": 0.032, "D15_m": 0.003},                       # D15 > D16
    {"D85_m": -0.01, "D15_m": 0.001},                       # negativo
])
def test_cuatro_percentiles_fuera_de_orden_detienen_la_carga(malo):
    with pytest.raises(DatoInvalidoError):
        servicio._material_lecho_externo(malo, "test")


# ===========================================================================
# 5 · Lo transcrito, contra lo que la fuente imprime
# ===========================================================================

def test_lo_transcrito_de_hec11():
    """Tabla 2 (PDF 47), Sec. 4.4.1 (PDF 49-50): leidos por texto e imagen."""
    filas = {round(pct): (bajo, alto) for pct, bajo, alto in HEC11_TABLA_2}
    assert filas[15] == pytest.approx((0.4, 0.6), rel=REL_TRANSPORTE)
    assert filas[100] == pytest.approx((1.5, 1.7), rel=REL_TRANSPORTE)
    assert HEC11_FILTRO_ESPESOR_UNA_CAPA_M == pytest.approx(
        (0.150, 0.380), rel=REL_TRANSPORTE)
    assert HEC11_FILTRO_ESPESOR_VARIAS_CAPAS_M == pytest.approx(
        (0.100, 0.200), rel=REL_TRANSPORTE)
    reg = _registro.construir()
    assert "5 or less" in reg.cita("HEC11.4.4.1#RELACION_5").texto_literal.texto
    assert "150 mm" in reg.cita("HEC11.4.4.1#ESPESOR").texto_literal.texto
    assert reg.cita("HEC11.4.4.1#EC_14").interpretacion is not None
