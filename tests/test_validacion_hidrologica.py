"""
tests/test_validacion_hidrologica.py
====================================
La validacion hidrologica de `MH_hidrologia` contra seis casos reales
publicados (INDECI Piura, UNTumbes, UNSAAC, UPAO, UPeU, ESPOL). El generador
y las cifras transcritas estan en `tests/apoyo/validacion_hidrologica.py`;
el documento, en `docs/validacion_hidrologica.md`; las entradas, en
`tests/fixtures/hidrologia_casos_reales/` (DATOS DE CASO REAL PUBLICADO — no
son datos de este proyecto).

Lo que se fija aqui:
  * el documento esta sincronizado con el programa (sin sello: se compara
    entero, como los de la validacion integral de T-11);
  * ningun contraste es un DEFECTO del programa;
  * cada pieza que COINCIDE coincide con el numero publicado dentro de su
    tolerancia nombrada (las del dossier);
  * el CENSO de diferencias de metodo, de la unica fila fuera de tolerancia
    explicada y de las detenciones no crece ni mengua en silencio;
  * el ALCANCE de cada oraculo (cuantas celdas de cada tabla publicada se
    contrastan) es el del dossier;
  * los casos adversariales de Tumbes: la serie como se publica no carga
    (`DatoFaltanteError('fen')`) y la misma etiqueta de año repetida se
    detiene (`DatoInvalidoError('anio')`);
  * los caudales coinciden con el calculo a mano del verificador, y ninguno
    se juzga contra el documento;
  * mutar el estimador de Gumbel del programa rompe los contrastes (el
    contraste ve el programa);
  * generar el documento deja los criterios como estaban.

Ninguno abre un PDF: las cifras estan transcritas con su pagina.
"""

from __future__ import annotations

import pytest

from src import criterios_adoptados as ca
from src.modelos import DatoFaltanteError, DatoInvalidoError
from src.modulos import MH_hidrologia as MH
from tests.apoyo import validacion_hidrologica as VH


def test_el_documento_esta_sincronizado():
    assert VH.DOCUMENTO.read_text(encoding="utf-8") == VH.generar(), (
        "docs/validacion_hidrologica.md no esta sincronizado: "
        "python -m tests.apoyo.validacion_hidrologica --escribir")


CONTRASTES = VH.contrastes()


def test_ningun_contraste_es_un_defecto_del_programa():
    defectos = [(c.caso, c.pieza, c.que, c.publicado, c.programa)
                for c in CONTRASTES if c.juicio == VH.JUICIO_DEFECTO]
    assert not defectos, defectos


def _id(c):
    return f"{c.caso}: {c.pieza}: {c.que}"


COINCIDEN = [c for c in CONTRASTES if c.juicio == VH.JUICIO_COINCIDE]


@pytest.mark.parametrize("c", COINCIDEN, ids=_id)
def test_cada_pieza_coincide_con_lo_publicado(c):
    """El numero publicado por el tercero, contra el programa, con la
    tolerancia nombrada del dossier (o el medio ultimo digito impreso)."""
    t = c.tolerancia
    if t.relativa:
        assert c.programa == pytest.approx(c.publicado, rel=t.valor, abs=0)
    else:
        assert c.programa == pytest.approx(c.publicado, abs=t.valor, rel=0)


def _clave(c):
    return (c.caso, c.pieza, c.que)


METODO_ESPERADO = {
    (VH.UPEU, "K de Témez, ec. (31), con la «s» del cauce (entrada de MH)",
     "MC-08"),
    (VH.UPEU, "K de Témez, ec. (31), con la «s» del cauce (entrada de MH)",
     "MC-09"),
    (VH.ESPOL, "Dmax de K-S, La Argelia", "Log Normal"),
    (VH.ESPOL, "Dmax de K-S, Gonzanama", "Log Normal"),
    (VH.ESPOL, "Dmax de K-S, Catamayo", "Log Normal"),
    (VH.ESPOL, "Dmax de K-S, Malacatos", "Normal"),
    (VH.ESPOL, "Dmax de K-S, Malacatos", "Gumbel"),
    (VH.ESPOL, "Dmax de K-S, Malacatos", "Log Normal"),
}


def test_el_censo_de_diferencias_de_metodo():
    """
    Son del DOCUMENTO (otro metodo u otra serie), no del programa, y se fijan
    por su nombre. Las del dossier: el K de UPeU en las filas 8 y 9 (§6.2, el
    documento uso la pendiente de la microcuenca), la Log Normal de
    Hydrognomon y Malacatos entera (§7).
    """
    assert {_clave(c) for c in CONTRASTES
            if c.juicio == VH.JUICIO_METODO} == METODO_ESPERADO


def test_la_unica_fila_fuera_de_tolerancia_explicada():
    """
    C-13 de Tumbes: 0.0073 h contra el ±0.007 h del dossier, que es su
    desvio maximo redondeado. El programa da lo mismo que el calculo a mano
    del verificador (4.652699 h en su `salida_esperada.json`); la tolerancia
    no se ensancha.
    """
    fuera = [c for c in CONTRASTES if c.juicio == VH.JUICIO_EXPLICADO]
    assert [_clave(c) for c in fuera] == [(VH.TUMBES, "Témez, ec. (30)",
                                          "C-13")]
    (c,) = fuera
    assert c.programa == pytest.approx(4.652699142205859, rel=1e-9)
    assert abs(c.programa - c.publicado) < 0.0075


DETENIDAS_ESPERADAS = {
    (VH.TUMBES, "Témez, ec. (30)", "C-20"),
    (VH.TUMBES, "Témez, ec. (30)", "C-27"),
    *((VH.UNSAAC, "Témez, ec. (30)", a)
      for a in ("A8", "A9", "A10", "A11", "A12", "A13", "A15")),
}


def test_el_censo_de_las_piezas_que_el_programa_no_evalua():
    """Témez bajo 0.25 h: 2 de 41 en Tumbes y 7 de 15 en UNSAAC (dossier
    §3.5 y §4.5)."""
    detenidas = [c for c in CONTRASTES if c.juicio == VH.JUICIO_DETIENE]
    assert {_clave(c) for c in detenidas} == DETENIDAS_ESPERADAS
    assert all(c.detencion.startswith("MetodoNoEvaluableError")
               for c in detenidas)


def _cuantas(caso, prefijo):
    return sum(1 for c in CONTRASTES if c.caso == caso
               and c.pieza.startswith(prefijo))


@pytest.mark.parametrize("caso, prefijo, n", [
    (VH.INDECI, "P24(TR)", 58),           # dossier §0: 58 celdas
    (VH.INDECI, "Δ de K-S", 6),           # 6 valores
    (VH.TUMBES, "Δ de K-S", 3),
    (VH.TUMBES, "P24(TR)", 10),
    (VH.TUMBES, "Témez", 41),             # 41 cuencas
    (VH.UNSAAC, "P24(TR) Gumbel", 10),    # 10 TR
    (VH.UNSAAC, "Dick-Peschke", 48),      # 48 celdas
    (VH.UNSAAC, "Témez", 15),             # 15 cuencas
    (VH.UPAO, "serie A: Δ", 3),
    (VH.UPAO, "serie A: P24", 15),        # 15 lluvias
    (VH.UPAO, "serie B: XT'", 7),         # 7 TR
    (VH.UPEU, "K de Témez, ec. (31)", 12),
    (VH.ESPOL, "Dmax", 12),
])
def test_el_alcance_de_cada_oraculo(caso, prefijo, n):
    assert _cuantas(caso, prefijo) == n


# ---------------------------------------------------------------------------
# Los adversariales de Tumbes, escritos aqui sin pasar por el generador
# ---------------------------------------------------------------------------

TUMBES = VH.CASOS / "untumbes_tu107"


def test_tumbes_como_se_publica_no_carga_por_la_celda_fen_vacia():
    with pytest.raises(DatoFaltanteError) as error:
        MH.cargar_estacion(TUMBES / "estacion_como_se_publica_fen_vacio.csv")
    assert error.value.campo == "fen"


def test_tumbes_la_misma_etiqueta_de_año_dos_veces_se_detiene():
    ruta = TUMBES / "estacion_fen_declarado_por_el_verificador.csv"
    with pytest.raises(DatoInvalidoError) as error:
        MH.cargar_estacion(ruta, datos=VH._con_anio_repetido())
    assert error.value.campo == "anio"
    # Y sin tocarla, la serie carga entera: los años copiados no se quitan.
    assert len(MH.cargar_estacion(ruta)["Cañaveral"].registros) == 40


@pytest.mark.parametrize("d", VH.detenciones(),
                         ids=lambda d: f"{d.caso}: {d.entrada}")
def test_cada_detencion_es_la_esperada(d):
    assert d.como_se_espera, (d.esperada, d.campo_esperado, d.obtenida,
                              d.campo_obtenido)


# ---------------------------------------------------------------------------
# Caudales
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("q", VH.caudales(),
                         ids=lambda q: f"{q.caso} {q.cuenca} TR {q.TR} "
                                       f"{q.magnitud}")
def test_cada_caudal_coincide_con_el_calculo_a_mano(q):
    assert q.programa == pytest.approx(
        q.a_mano, rel=VH.TOLERANCIAS["TOL_REL_A_MANO"].valor)


def test_ningun_caudal_se_juzga_contra_el_documento():
    """Es otro metodo en los seis: el documento no da tolerancia, y el
    generador no tiene juicio que lo compare."""
    assert not hasattr(VH.Caudal, "coincide_con_el_documento")
    assert all(q.por_que_difiere for q in VH.caudales())


# ---------------------------------------------------------------------------
# El contraste ve el programa, y no deja rastro
# ---------------------------------------------------------------------------

def test_mutar_el_estimador_de_gumbel_rompe_los_contrastes(monkeypatch):
    monkeypatch.setitem(MH.GUMBEL_MOMENTOS, "beta_resta_sigmas",
                        MH.GUMBEL_MOMENTOS["beta_resta_sigmas"] * 1.01)
    rotos = [c for c in VH.contrastes_unsaac() + VH.contrastes_upao()
             if c.juicio == VH.JUICIO_DEFECTO]
    assert rotos, "el contraste no ve el estimador de Gumbel del programa"


def test_generar_deja_los_criterios_como_estaban():
    antes = dict(ca.valores_dinamicos())
    VH.generar()
    assert dict(ca.valores_dinamicos()) == antes


def test_cada_entrada_dice_que_es_de_un_caso_real():
    for ruta in sorted(VH.CASOS.glob("*/*.csv")):
        primera = ruta.read_text(encoding="utf-8").splitlines()[0]
        assert primera.startswith("# DATOS DE CASO REAL PUBLICADO — no son "
                                  "datos de este proyecto. Fuente:"), ruta
