"""
tests/test_ve3_13_gobierno_receptor.py
======================================
VE-3.13: la DECISION 8 del dueño (proceso/planes_mejora/ve3_estado/LEEME.md,
«TERCERA RESPUESTA DEL DUEÑO»). `borde_libre_bajo_tw_ahogante` SIGUE en
`no_cumple` y ningun diametro adoptado cambia; lo que cambia es la
PRESENTACION. Cuando V1 descarto escalones SOLO por el nivel del receptor
--el escalon conservaba el borde libre con su tirante propio y nada mas de
la Fase 5 lo descartaba--, la corrida dice:

  (a) que el diametro lo gobierno el nivel del receptor, no el caudal;
  (b) el diametro que bastaria por la hidraulica sola: el que la lectura
      «aviso» adoptaria, evaluado de verdad bajo esa lectura;
  (c) el descenso del TW --o la subida de la solera de salida-- con el que
      ese diametro cumpliria V1 (TW <= (y/D)max · D sobre la solera),
      rotulado como ALTERNATIVA que el proyectista evalua, no como remedio
      verificado.

Lo dice un `PasoDeMemoria` EMITIDO por el calculo (MD, donde se decide la
progresion), y lo imprimen la memoria completa, la resumida, el JSON y la
pestaña 3 (que pinta `cli._lineas_punto`) por el aviso del punto.

EL CASO ES E07 de los ensayos de diseño del conducto (DATO DE PRUEBA,
`tests/fixtures/ve3_13_gobierno_receptor/`): Q = 0.6 m3/s, S = 0.004,
TW = 1.0 m. Con «no_cumple» Ø 1.35 m (V1 descarta 0.90, 1.05 y 1.20 por el
receptor); con «aviso» Ø 0.90 m. A mano: (y/D)max = 0.75, TW admisible
sobre la solera del Ø 0.90 = 0.75 · 0.90 = 0.675 m, y el descenso es
1.0 - 0.675 = 0.325 m.

SE ESCRIBIO EN ROJO PRIMERO, contra 7221fe0.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import cli
from src import servicio
from src.modelos import PasoDiseno, SeccionCircular, Verificacion
from src.modulos import M11_reporte as M11
from src.modulos import MD
from src.modulos.M2_material import catalogo
from src.modelos import TipoMaterial

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "tests" / "fixtures" / "ve3_13_gobierno_receptor"
CSV = DIR / "puntos.csv"
EXTERNOS = DIR / "externos.json"
EXTERNOS_LIBRE = DIR / "externos_salida_libre.json"

# La cuenta a mano del docstring: TW - 0.75 · D_hidraulico.
TW_E07 = 1.0
D_HIDRAULICO_E07 = 0.90
D_ADOPTADO_E07 = 1.35
DESCENSO_E07 = TW_E07 - 0.75 * D_HIDRAULICO_E07          # 0.325 m
# El descenso se compara con la mitad del milimetro con que se imprime.
MEDIO_MILIMETRO = 5e-4


def _informe(externos: Path):
    ext = servicio.cargar_datos_externos(externos, {})
    return servicio.correr(CSV, ext, alcance="perfil")


@pytest.fixture(scope="module")
def e07():
    return _informe(EXTERNOS).puntos[0]


@pytest.fixture(scope="module")
def e07_libre():
    return _informe(EXTERNOS_LIBRE).puntos[0]


def test_el_diametro_adoptado_no_cambia(e07):
    assert e07.dimensionado
    assert e07.resultado.seccion.altura == pytest.approx(
        D_ADOPTADO_E07, abs=MEDIO_MILIMETRO)


def test_e07_dice_que_lo_gobierna_el_receptor_y_el_diametro_hidraulico(e07):
    g = e07.resultado.gobierno_por_receptor
    assert g is not None, "E07: el receptor gobierna y la corrida no lo dice"
    assert g.seccion_adoptada.altura == pytest.approx(D_ADOPTADO_E07,
                                                      abs=MEDIO_MILIMETRO)
    assert g.seccion_hidraulica.altura == pytest.approx(D_HIDRAULICO_E07,
                                                        abs=MEDIO_MILIMETRO)
    assert g.material_hidraulico == g.material_adoptado == "Concreto reforzado"
    assert g.descenso_tw_m == pytest.approx(DESCENSO_E07, abs=MEDIO_MILIMETRO)
    assert g.tw_m == pytest.approx(TW_E07, abs=MEDIO_MILIMETRO)
    # Los escalones que el receptor descarto, en orden.
    assert [s for s in g.escalones_descartados] == ["Ø 0.90 m", "Ø 1.05 m",
                                                   "Ø 1.20 m"]


def test_el_paso_lo_emite_el_calculo_y_rotula_la_alternativa(e07):
    g = e07.resultado.gobierno_por_receptor
    p = g.paso
    assert p.fundamento_id == "F5.V1.RECEPTOR"
    assert p.resultado.valor == pytest.approx(DESCENSO_E07,
                                              abs=MEDIO_MILIMETRO)
    assert "ALTERNATIVA" in p.nota_del_proyecto
    assert "no es un remedio verificado" in p.nota_del_proyecto
    # La eleccion que decide es la del criterio, con su justificacion leida
    # de la ficha (no transcrita).
    from src import criterios_adoptados as ca
    (el,) = p.elecciones
    assert el.clave_criterio == "borde_libre_bajo_tw_ahogante"
    assert el.valor == "no_cumple"
    assert el.por_que == ca.criterio("borde_libre_bajo_tw_ahogante").justificacion


def test_el_aviso_dice_las_tres_cosas(e07):
    avisos = [a for a in e07.avisos() if "nivel del receptor" in a
              and "gobern" in a]
    assert len(avisos) == 1, e07.avisos()
    a = avisos[0]
    assert "Ø 1.35 m" in a and "Ø 0.90 m" in a
    assert "0.325 m" in a
    assert "ALTERNATIVA" in a


def test_sin_gobierno_del_receptor_no_se_dice_nada(e07_libre):
    assert e07_libre.dimensionado
    assert e07_libre.resultado.gobierno_por_receptor is None
    assert not [a for a in e07_libre.avisos() if "nivel del receptor" in a
                and "gobern" in a]


def test_lo_imprimen_la_memoria_completa_la_resumida_y_la_pestana_3(e07):
    completa = M11.memoria_de_punto(e07)
    assert e07.resultado.gobierno_por_receptor.paso.que in completa
    resumida = M11.resumen_de_punto(e07, {}, None)
    assert "0.325 m" in resumida
    pestana_3 = "\n".join(str(x) for x in cli._lineas_punto(e07))
    assert "0.325 m" in pestana_3


def test_lo_imprime_el_json(tmp_path):
    salida = tmp_path / "e07.json"
    cli.main([str(CSV), "--alcance", "perfil", "--datos-externos",
              str(EXTERNOS), "--json", str(salida)])
    p = json.loads(salida.read_text(encoding="utf-8"))["puntos"][0]
    g = p["gobierno_por_receptor"]
    assert g["seccion_hidraulica"] == "Ø 0.90 m"
    assert g["seccion_adoptada"] == "Ø 1.35 m"
    assert g["descenso_tw_m"] == pytest.approx(DESCENSO_E07,
                                               abs=MEDIO_MILIMETRO)
    assert g["alternativa_no_verificada"] is True
    assert any("0.325 m" in a for a in p["avisos"])


# ---------------------------------------------------------------------------
# «Solo por el TW»: un escalon que ademas incumple otra cosa no cuenta
# ---------------------------------------------------------------------------

def _v(codigo, cumple, solo_receptor=False):
    return Verificacion(cumple=cumple, numeral="x", valor_obtenido=None,
                        valor_admisible=None, criterio_aplicado=None,
                        codigo=codigo, descarta_solo_el_receptor=solo_receptor)


def _escalon(*verificaciones):
    return PasoDiseno(material="Concreto reforzado",
                      seccion=SeccionCircular(D=0.90), aceptado=False,
                      motivo="x", verificaciones=tuple(verificaciones))


def test_solo_por_el_receptor_exige_que_v1_sea_la_unica_incumplida():
    assert MD._descartado_solo_por_el_receptor(
        _escalon(_v("V1", False, True), _v("V2", True), _v("V3", True)))
    assert not MD._descartado_solo_por_el_receptor(
        _escalon(_v("V1", False, True), _v("V3", False)))
    # V1 incumplida por el caudal propio (sin la marca) tampoco cuenta.
    assert not MD._descartado_solo_por_el_receptor(
        _escalon(_v("V1", False, False), _v("V2", True)))
    assert not MD._descartado_solo_por_el_receptor(_escalon())


def test_la_lectura_forzada_se_repone_aunque_la_fase_5_lance():
    """
    `M5.lectura_bajo_tw_forzada` solo vale dentro del bloque y no declara
    nada: al salir --tambien con excepcion-- V1 vuelve a leer el criterio.
    """
    from src.modulos import M5_verificaciones as M5
    assert M5._lectura_bajo_tw_ahogante() == "no_cumple"
    with pytest.raises(RuntimeError):
        with M5.lectura_bajo_tw_forzada(M5.LECTURA_TW_AVISO):
            assert M5._lectura_bajo_tw_ahogante() == "aviso"
            raise RuntimeError("la Fase 5 lanzo")
    assert M5._lectura_bajo_tw_ahogante() == "no_cumple"
    with pytest.raises(ValueError):
        with M5.lectura_bajo_tw_forzada("otra"):
            pass

