"""
tests/test_M8_estructural.py
=============================
Fase 8 (M8_estructural.py):

    seleccionar_clase_calibre()      Verificacion diferida (cumple=None):
                                      'clases_producto_por_relleno' vacio y
                                      las dos tablas de norma de producto
                                      sin transcribir.
    empuje_flotacion_kn_m()          U = gamma_agua * (pi/4) * D^2, siempre
                                      calculable: la hipotesis es sumersion
                                      completa y por eso NO usa el valor del
                                      NF del punto.
    peso_relleno_kn_m()              CriterioPendienteError:
                                      'peso_especifico_relleno_kn_m3' vacio;
                                      calculo directo con el criterio declarado.
    factores_carga_flotacion()       'factores_carga_aashto' es [C] (AASHTO
                                      LRFD 9a ed.): calcula directo, lee la
                                      fila 'Resistencia I'. DatoInvalidoError
                                      si la declaracion no trae la
                                      combinacion, la fila o el extremo que
                                      V7 pide. V7 dejo de ser un FS global:
                                      es el equilibrio de factores de carga
                                      LRFD.
    cama_apoyo_relleno_lateral()     tabla 8.1, [N] literal, sin vacio.
    verificacion_diferida_estructural()  tupla de avisos, nunca calcula.
"""

import math
from dataclasses import fields
from pathlib import Path

import pytest

import criterios_adoptados as ca
from constantes_fisicas import GAMMA_AGUA_KN_M3
import modulos.M8_estructural as M8
from modelos import (CamaApoyoRelleno, CriterioPendienteError,
                     DatoInvalidoError, PuntoCritico, TipoMaterial)
from modulos.M2_material import catalogo
from modulos.M8_estructural import (cama_apoyo_relleno_lateral,
                                    empuje_flotacion_kn_m,
                                    factores_carga_flotacion,
                                    peso_relleno_kn_m,
                                    seleccionar_clase_calibre,
                                    verificacion_diferida_estructural)


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def hdpe():
    return catalogo(TipoMaterial.HDPE)


# ===========================================================================
# Items 1-2 - Seleccion de clase/calibre
# ===========================================================================

def test_seleccionar_clase_calibre_se_difiere_al_expediente(concreto):
    """
    Los items 1-2 ya no se detienen: se difieren. Devuelven un Verificacion
    con cumple=None y la razon en `nota_diferida`, que nombra las dos tablas
    de norma de producto que habria que transcribir.
    """
    v = seleccionar_clase_calibre(material=concreto, altura_relleno=1.0)
    assert v.cumple is None
    assert v.valor_obtenido is None
    assert v.valor_admisible is None
    assert v.criterio_aplicado is None
    assert v.nota_diferida
    assert "M-170M" in v.nota_diferida
    assert "M36" in v.nota_diferida
    assert "clases_producto_por_relleno" in v.nota_diferida


def test_clase_calibre_diferida_tambien_con_hdpe(hdpe):
    """
    cli._fase_8 llama a esta verificacion sin ramificar por material, aunque
    HDPE no tenga tabla de clase por altura: lo suyo lo difiere el item 5, no
    este vacio. Hoy es inofensivo porque la respuesta es un diferido y no una
    excepcion, pero la nota lo dice en vez de callarlo.
    """
    v = seleccionar_clase_calibre(material=hdpe, altura_relleno=1.0)
    assert v.cumple is None
    assert v.nota_diferida
    assert "HDPE" in v.nota_diferida


def test_clase_calibre_diferida_no_registra_el_criterio_como_usado(concreto):
    """
    Una verificacion diferida no aplico el criterio a ningun numero: si lo
    registrara, M11 lo imprimiria como usado y la memoria diria algo falso.
    """
    antes = set(ca.criterios_usados())
    seleccionar_clase_calibre(material=concreto, altura_relleno=1.0)
    nuevos = set(ca.criterios_usados()) - antes
    assert "clases_producto_por_relleno" not in nuevos


def test_clases_producto_por_relleno_esta_declarado_vacio():
    assert "clases_producto_por_relleno" in ca.criterios_sin_valor()


# ===========================================================================
# Item 3 - Piezas de V7
# ===========================================================================

def test_empuje_flotacion_es_siempre_calculable():
    """U no depende de ningun criterio pendiente ni del NF medido del punto."""
    U = empuje_flotacion_kn_m(D=0.90)
    assert U == pytest.approx(GAMMA_AGUA_KN_M3 * (math.pi / 4) * 0.90 ** 2)


def test_empuje_flotacion_crece_con_el_diametro():
    assert empuje_flotacion_kn_m(D=1.20) > empuje_flotacion_kn_m(D=0.90)


def test_peso_relleno_lanza_pendiente():
    with pytest.raises(CriterioPendienteError) as excinfo:
        peso_relleno_kn_m(D=0.90, altura_relleno=1.0)
    assert excinfo.value.clave == "peso_especifico_relleno_kn_m3"


def test_peso_relleno_calcula_con_el_criterio_declarado(monkeypatch):
    original = ca.CRITERIOS["peso_especifico_relleno_kn_m3"]
    monkeypatch.setitem(
        ca.CRITERIOS, "peso_especifico_relleno_kn_m3",
        original.__class__(**{**original.__dict__, "valor": 18.0}),
    )
    W = peso_relleno_kn_m(D=0.90, altura_relleno=1.05)
    assert W == pytest.approx(18.0 * 0.90 * 1.05)


def _declarar(monkeypatch, clave, valor):
    original = ca.CRITERIOS[clave]
    monkeypatch.setitem(ca.CRITERIOS, clave,
                        original.__class__(**{**original.__dict__, "valor": valor}))


TABLA_GAMMA_DEMO = {"Resistencia I": {"DC": {"min": 0.90, "max": 1.25},
                                      "EV": {"min": 1.00, "max": 1.35},
                                      "WA": {"min": 1.00, "max": 1.00}}}


def test_factores_carga_flotacion_calcula_con_el_criterio_real():
    """
    'factores_carga_aashto' es [C] (AASHTO LRFD 9a ed.): V7 ya no se detiene
    aqui. Lee la fila 'Resistencia I' -- DC y EV con su MINIMO (0.90 los
    dos), WA con su MAXIMO (1.00, no hay margen que tomar en esa carga).
    """
    g = factores_carga_flotacion()
    assert (g.gamma_DC, g.gamma_EV, g.gamma_WA) == (0.90, 0.90, 1.00)
    assert g.criterio == "factores_carga_aashto"


def test_fs_flotacion_ya_no_existe():
    """
    'FS_flotacion' se retiro al reescribir V7 como equilibrio LRFD. Un FS
    global es lenguaje de tension admisible y Sec. 0.2 adopta AASHTO LRFD de
    extremo a extremo; conservar ademas un FS seria contar dos veces el mismo
    margen. Este test impide que vuelva por la puerta de atras.
    """
    assert "FS_flotacion" not in ca.CRITERIOS
    assert not hasattr(M8, "fs_flotacion")


def test_los_gamma_de_v7_salen_del_criterio_y_con_el_extremo_correcto(monkeypatch):
    """
    DC y EV estabilizan la flotacion: entran con su gamma MINIMO. WA (la
    subpresion) desestabiliza: entra con el MAXIMO. Tomar el maximo de EV
    seria el error clasico, y aqui daria del lado inseguro.
    """
    _declarar(monkeypatch, "factores_carga_aashto", TABLA_GAMMA_DEMO)
    g = factores_carga_flotacion()
    assert (g.gamma_DC, g.gamma_EV, g.gamma_WA) == (0.90, 1.00, 1.00)
    assert g.criterio == "factores_carga_aashto"


def test_una_tabla_de_gamma_incompleta_es_dato_invalido(monkeypatch):
    """Falta la fila WA: el problema esta en la declaracion, no en el programa."""
    _declarar(monkeypatch, "factores_carga_aashto",
              {"Resistencia I": {"DC": {"min": 0.90, "max": 1.25},
                                 "EV": {"min": 1.00, "max": 1.35}}})
    with pytest.raises(DatoInvalidoError) as excinfo:
        factores_carga_flotacion()
    assert "WA" in str(excinfo.value)


def test_una_tabla_sin_la_combinacion_resistencia_i_es_dato_invalido(monkeypatch):
    """Falta la fila 'Resistencia I' entera: tambien es dato invalido, no KeyError."""
    _declarar(monkeypatch, "factores_carga_aashto", {"Servicio I": {}})
    with pytest.raises(DatoInvalidoError) as excinfo:
        factores_carga_flotacion()
    assert "Resistencia I" in str(excinfo.value)


def test_el_NF_ya_no_es_un_criterio_de_este_modulo():
    """
    Era un criterio [N] de proyecto (1.4 m para todo el tramo). Hoy es un dato
    de sitio [S] que se mide en cada cruce, o sea una columna del CSV. Que U
    no lo lea es lo que mantiene V7 calculable en un punto cuyo estudio
    geotecnico todavia no dio el NF: la hipotesis de la fila V7 es sumersion
    completa, y sumergido del todo el conducto desplaza su volumen entero
    este el freatico donde este.
    """
    with pytest.raises(KeyError):
        ca.valor("NF_profundidad_m")
    assert "NF_profundidad_m" in {f.name for f in fields(PuntoCritico)}

    fuente = Path(M8.__file__).read_text(encoding="utf-8-sig")
    assert 'ca.valor(CRITERIO_NF)' not in fuente
    assert "CRITERIO_NF" not in fuente


# ===========================================================================
# Item 4 - Cama de apoyo y relleno lateral (tabla 8.1, [N])
# ===========================================================================

def test_cama_apoyo_relleno_lateral_concreto_reforzado(concreto):
    fila = cama_apoyo_relleno_lateral(concreto)
    assert isinstance(fila, CamaApoyoRelleno)
    assert "1/6" in fila.sujecion_relleno_lateral
    assert "506" in fila.numeral


def test_cama_apoyo_relleno_lateral_hdpe(hdpe):
    fila = cama_apoyo_relleno_lateral(hdpe)
    assert "arena" in fila.cama_apoyo.lower()
    assert "508" in fila.numeral


# ===========================================================================
# Item 5 - Diferido al expediente (nunca calcula)
# ===========================================================================

def test_verificacion_diferida_no_lanza_y_devuelve_los_tres_avisos():
    avisos = verificacion_diferida_estructural()
    assert len(avisos) == 3
    conceptos = " ".join(avisos).lower()
    for palabra in ("rigidez de anillo", "pandeo", "costura"):
        assert palabra in conceptos
