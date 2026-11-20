"""
tests/test_ve7_lote_a_embocadura.py
===================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20): la embocadura del marco.

A1 (VE6-T7A03 (4)) -- con el cabezal NORMAL sin aletas, el borde de la fila
de la Tabla A.1 empareja el ke de la C.2, como ya lo hacia la Carta 11. El
oraculo es el ROTULO literal de cada fila (`normativa/tablas.py::T_HDS5_A1`)
leido aqui: «chamfer» -> solo la escuadra (ke 0.5); «bevel» -> la de bordes
biselados (0.2) o la escuadra; la escala 2 de la Carta 8 («90° and 15°
wingwall flares», arista viva) -> la escuadra.
"""

import json
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.constantes_normativas import CAJON_C2_SIN_ALETAS, KE_HDS5_C2
from src.modelos import DatoInvalidoError, Familia
from src.modulos import M9_cabezal as M9
from src.normativa import tablas
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON

ESCUADRA = "cajon_sin_aletas_escuadra_3"
BISELADA = "cajon_sin_aletas_redondeado_3"


def _rotulo_ta1(clave):
    tabla = tablas.TABLAS["HDS5_3ED.TA1"]
    fila = next(f for f in tabla.filas if f.id == f"HDS5_3ED.TA1#{clave}")
    return fila.etiqueta_literal.lower()


def _normal_sin_aletas(esviaje=0.0):
    with declarados({"embocadura_cabezal": M9.EMBOCADURA_CABEZAL_RECTO}):
        return M9.embocadura_del_punto(esviaje_grados=esviaje,
                                       familia=Familia.C, id_punto="P")


@pytest.mark.parametrize("fila", [
    "cajon_concreto_cabezal_90_chaflan",
    "cajon_concreto_cabezal_90_bisel_45",
    "cajon_concreto_cabezal_90_bisel_337",
])
def test_los_rotulos_de_la_carta_10_nombran_su_borde(fila):
    rotulo = _rotulo_ta1(fila)
    if "chaflan" in fila:
        assert "chamfer" in rotulo and "bevel" not in rotulo
    else:
        assert "bevel" in rotulo and "chamfer" not in rotulo


def _vale_por_rotulo(fila, ke):
    """El emparejamiento escrito aqui desde el rotulo, no desde la constante."""
    rotulo = _rotulo_ta1(fila)
    if ke == ESCUADRA:
        return True
    return "bevel" in rotulo


@pytest.mark.parametrize("fila", [
    "cajon_concreto_cabezal_90_chaflan",
    "cajon_concreto_cabezal_90_bisel_45",
    "cajon_concreto_cabezal_90_bisel_337",
    "cajon_concreto_aletas_90_15",
])
@pytest.mark.parametrize("ke", [ESCUADRA, BISELADA])
def test_el_borde_de_la_carta_10_empareja_el_ke(fila, ke):
    embocadura = _normal_sin_aletas()
    with declarados({"embocadura_cajon": fila, "ke_entrada_cajon": ke}):
        if _vale_por_rotulo(fila, ke):
            nota = M9.verificar_coherencia_embocadura_cajon(embocadura)
            assert fila in nota and ke in nota
        else:
            with pytest.raises(DatoInvalidoError) as exc:
                M9.verificar_coherencia_embocadura_cajon(embocadura)
            assert exc.value.campo == "ke_entrada_cajon"
            assert ESCUADRA in str(exc.value)


def test_chaflan_con_ke_02_se_detiene_y_bisel_con_ke_02_pasa():
    """El caso del dictamen, dicho con el ke de la tabla (0.2)."""
    assert KE_HDS5_C2[BISELADA]["ke"] == pytest.approx(0.2, rel=REL_TRANSPORTE)
    embocadura = _normal_sin_aletas()
    with declarados({"embocadura_cajon": "cajon_concreto_cabezal_90_chaflan",
                     "ke_entrada_cajon": BISELADA}):
        with pytest.raises(DatoInvalidoError):
            M9.verificar_coherencia_embocadura_cajon(embocadura)
    with declarados({"embocadura_cajon": "cajon_concreto_cabezal_90_bisel_45",
                     "ke_entrada_cajon": BISELADA}):
        assert M9.verificar_coherencia_embocadura_cajon(embocadura)


def test_sin_carta_declarada_de_cabezal_normal_rigen_las_dos_filas():
    """Con una carta de aleros (la de archivo) y cabezal recto la coherencia
    se detiene en la carta, no en el ke: la banda del ke sigue entera."""
    _, c2 = M9.filas_hds5_del_cajon(_normal_sin_aletas())
    assert c2 == CAJON_C2_SIN_ALETAS


# ===========================================================================
# A2 (VE6-T7A03 (1)) -- la embocadura del marco declarada por punto
# ===========================================================================

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / \
    "entradas_ampliadas.json"
FILA_C01 = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
CARTA_11_30 = "cajon_concreto_chaflan_esviaje_30"
CARTA_10 = "cajon_concreto_cabezal_90_chaflan"


@pytest.fixture
def corredor_de_dos_marcos(tmp_path):
    """C-01 (esviaje 30) y C-02, la misma fila a 0 grados; los datos de
    C-01 de la linea base de la Familia C, repetidos para C-02, y la
    embocadura de cada uno declarada por punto."""
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    cabecera = texto.split("\n", 1)[0]
    c01 = FILA_C01 + "38.30"
    c02 = c01.replace("C-01,3+100", "C-02,3+400").replace(",6.5,30,",
                                                          ",6.5,0,")
    csv = tmp_path / "dos_marcos.csv"
    csv.write_text("\n".join((cabecera, c01, c02)) + "\n", encoding="utf-8")
    crudo = json.loads(EXTERNOS_AMPLIADOS.read_text(encoding="utf-8"))
    crudo["puntos"] = {"C-01": dict(crudo["puntos"]["C-01"]),
                       "C-02": dict(crudo["puntos"]["C-01"])}
    crudo["puntos"]["C-01"]["embocadura_cajon_del_punto"] = {
        "carta": CARTA_11_30, "ke": ESCUADRA}
    crudo["puntos"]["C-02"]["embocadura_cajon_del_punto"] = {
        "carta": CARTA_10, "ke": ESCUADRA}
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(crudo), encoding="utf-8")
    return csv, cli.cargar_datos_externos(ruta, {"luz_m": 2.75})


def test_la_clave_se_valida_al_cargar_y_va_solo_por_punto(tmp_path):
    assert "embocadura_cajon_del_punto" in servicio.CLAVES_DE_CABEZAL
    assert "embocadura_cajon_del_punto" not in servicio.CLAVES_EXTERNAS
    for malo in ({"carta": CARTA_10}, {"carta": CARTA_10, "ke": "x"},
                 {"carta": "tubo", "ke": ESCUADRA},
                 {"carta": CARTA_10, "ke": ESCUADRA, "n": 1}, "texto"):
        with pytest.raises(DatoInvalidoError):
            M9.validar_embocadura_cajon_del_punto(malo)
    ruta = tmp_path / "g.json"
    ruta.write_text(json.dumps({"globales": {"embocadura_cajon_del_punto": {
        "carta": CARTA_10, "ke": ESCUADRA}}}), encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        cli.cargar_datos_externos(ruta, {})


def test_un_corredor_con_un_marco_carta_10_y_otro_carta_11_corre_entero(
        corredor_de_dos_marcos):
    """
    Con 'embocadura_cabezal' = recto en el proyecto, C-01 (30 grados) corre
    con la Carta 11 -- cabezal paralelo a la via -- y C-02 (0 grados) con la
    Carta 10 -- cabezal normal --. Con una sola embocadura de proyecto, una
    de las dos se detendria en la coherencia. Al salir, el proyecto vuelve
    a la suya.
    """
    csv, externos = corredor_de_dos_marcos
    with declarados(DECLARACIONES_DEL_CAJON):
        with declarados({"embocadura_cabezal": M9.EMBOCADURA_CABEZAL_RECTO}):
            informe = cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
            assert ca.valor("embocadura_cajon") == \
                DECLARACIONES_DEL_CAJON["embocadura_cajon"]
            assert ca.valor("ke_entrada_cajon") == \
                DECLARACIONES_DEL_CAJON["ke_entrada_cajon"]
    c01, c02 = informe.puntos
    for p in (c01, c02):
        assert p.dimensionado, [b.mensaje for b in p.bloqueos]
        assert not any("coherencia" in b.etapa for b in p.bloqueos)
        assert "declarada por punto" in p.coherencia_embocadura
    assert c01.embocadura.orientacion == M9.ORIENTACION_PARALELO_A_LA_VIA
    assert c02.embocadura.orientacion == M9.ORIENTACION_NORMAL_AL_EJE
    assert CARTA_11_30 in c01.coherencia_embocadura
    assert CARTA_10 in c02.coherencia_embocadura


def test_A8_el_cabezal_paralelo_avisa_el_borde_libre_esviado_de_la_losa():
    """La embocadura paralela a la via avisa que el borde libre esviado de
    la losa no se verifica y nombra las vigas de borde de C12.11.2.1, que
    estan en la nota de la cita del registro (`#SOMERO`)."""
    from src.normativa import registro
    nota = registro.construir().cita("AASHTO_LRFD_9.12.11.2.1#SOMERO").nota
    assert "C12.11.2.1" in nota and "vigas de borde" in nota
    with declarados({"embocadura_cajon": CARTA_11_30,
                     "ke_entrada_cajon": ESCUADRA}):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C,
                                    id_punto="C-01")
    avisos = [a for a in e.avisos if "borde libre esviado" in a]
    assert len(avisos) == 1
    assert "C12.11.2.1" in avisos[0] and "12.11.2.1#SOMERO" in avisos[0]
    # el cabezal normal al eje no lo lleva
    assert not any("borde libre esviado" in a
                   for a in _normal_sin_aletas().avisos)


def test_el_valor_de_proyecto_queda_restaurado_aunque_el_punto_falle(
        corredor_de_dos_marcos, monkeypatch):
    csv, externos = corredor_de_dos_marcos

    def revienta(*a, **k):
        assert ca.valor("embocadura_cajon") in (CARTA_11_30, CARTA_10)
        raise RuntimeError("fallo de prueba dentro del punto")

    monkeypatch.setattr(servicio, "_fase_2", revienta)
    with declarados(DECLARACIONES_DEL_CAJON):
        antes = ca.valores_dinamicos()
        with pytest.raises(RuntimeError):
            cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
        assert ca.valores_dinamicos() == antes
    # y sin nada declarado en caliente, el punto no deja nada vivo
    with pytest.raises(RuntimeError):
        cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
    assert "embocadura_cajon" not in ca.valores_dinamicos()
    assert "ke_entrada_cajon" not in ca.valores_dinamicos()
