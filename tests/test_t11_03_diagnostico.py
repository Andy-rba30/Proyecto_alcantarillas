"""
tests/test_t11_03_diagnostico.py
================================
Las dos correcciones de diagnostico de MD que la ficha T11-03 dejo ABIERTAS
--(3) y (4)-- y que el dueño aprobo despues (README §8). Las dos son de
`MD.disenar_punto` y ninguna toca el calculo: deciden QUE EXCEPCION sale del
punto, no que escalones se recorren.

(3) EL RESULTADO ACEPTADO CUANDO UN MATERIAL ANTERIOR SE DETUVO POR UN DATO
    INVALIDO DEL PUNTO. Si un candidato posterior cierra, el material anterior
    --mas preferente en el orden de M2-- que la Fase 5 detuvo con un
    `DatoInvalidoError` de un dato DEL PUNTO se descartaba en silencio: el
    punto salia dimensionado con el siguiente material, elegido por descarte
    de uno que nadie termino de evaluar. Es la regla de la ficha T4-10 para el
    dato que FALTA, y la del auditor de C05 para el criterio invalido; faltaba
    para el dato del punto. Mismo alcance que T11-03 (C) y que VE-2 A1/N1: el
    que levanta la Fase 5 (trae `verificaciones_completadas`) y nombra un dato
    del punto (su `campo` no es un criterio). Sale el primero, con su campo:
    el bloqueo DATO_INVALIDO.

(4) EL DATO INVALIDO QUE M3 O M4 LEVANTAN ANTES DE LA FASE 5. El diametro de
    arranque negativo de la rama de error de la linea base (`--declarar
    'diametros_normalizados={"inicio": -0.90, ...}'`) detiene a los tres
    candidatos en M3 con «el diametro debe ser positivo» sobre 'D', y el
    punto salia «no factible». Ningun material se evaluo: el revisor tiene
    que CORREGIR un dato. Cuando ese dato detiene a TODOS los candidatos sale
    como dato invalido, con su campo, por la mitad «comun a todos» de
    `MD._exigir_datos_validos`.

LO QUE NO CAMBIA, y esta fijado aqui: el dato invalido de antes de la Fase 5
que detiene a UN material mientras otro cierra (`tests/test_MD.py::
test_un_material_que_revienta_no_impide_que_otro_cierre`) o mientras los
demas se evaluan e incumplen (la otra mitad de T4-10).

SE ESCRIBIO EN ROJO PRIMERO: contra `6b08e4b` fallan los de (3), los de (4)
y el de la ficha; pasan las guardias de «lo que no cambia».
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import cli
from src import servicio
from src.modelos import (DatoInvalidoError, DisenoNoFactibleError,
                         TipoDeBloqueo, TipoMaterial)
from src.modulos import MD
from src.modulos import M2_material as M2
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.test_MD import L_CONDUCTO, TW_LIBRE, _punto, _verificacion

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
FICHAS = RAIZ / "docs" / "decisiones_diferidas.md"

TODOS = (TipoMaterial.CONCRETO_REFORZADO, TipoMaterial.TMC, TipoMaterial.HDPE)
# La declaracion de la corrida 3 de `tests/linea_base_familia_c/regenerar.sh`.
ARRANQUE_NEGATIVO = {"inicio": -0.90, "paso": 0.15}


def _invalido_de_la_fase_5(punto, material, completadas):
    """
    El `DatoInvalidoError` de un dato DEL PUNTO como lo levanta la Fase 5:
    con lo que la tabla le evaluo antes adjunto en la instancia.
    """
    exc = DatoInvalidoError(
        "Q_evento_extremo_m3s", valor=0.5, id_punto=punto.id,
        motivo=f"es menor que el de diseño (visto en {material.nombre})")
    exc.verificaciones_completadas = tuple(completadas)
    return exc


def _invalido_de_antes_de_la_fase_5():
    """El que M3 levanta sobre el diametro de arranque negativo: sin nada adjunto."""
    return DatoInvalidoError("D", valor=-0.9,
                             motivo="el diametro debe ser positivo")


class _Doble:
    """
    Verificador de prueba. Por material: `fase_5` levanta el dato invalido de
    la Fase 5 con `completadas`; `antes` levanta el de antes de la Fase 5;
    `cierran` cumple todo; el resto se evalua y no cumple.
    """

    def __init__(self, *, fase_5=(), antes=(), cierran=(),
                 completadas=(_verificacion(True),)):
        self.fase_5, self.antes = set(fase_5), set(antes)
        self.cierran, self.completadas = set(cierran), tuple(completadas)

    def __call__(self, *, punto, material, seccion, resultado):
        if material.tipo in self.fase_5:
            raise _invalido_de_la_fase_5(punto, material, self.completadas)
        if material.tipo in self.antes:
            raise _invalido_de_antes_de_la_fase_5()
        if material.tipo in self.cierran:
            return (_verificacion(True),)
        return (_verificacion(False, obtenido="x", admisible="y"),)


def _disenar(verificar):
    return MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                            verificar=verificar)


# ===========================================================================
# (3) Un candidato cierra y uno anterior se detuvo por un dato invalido
# ===========================================================================

def test_3_el_dato_invalido_del_punto_bloquea_aunque_un_material_posterior_cierre():
    """
    El concreto se detiene en la Fase 5 por un dato invalido del punto sobre
    un escalon que cumple lo evaluado; el TMC cerraria. Ya no sale el TMC:
    sale el dato, con su campo.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        _disenar(_Doble(fase_5=[TipoMaterial.CONCRETO_REFORZADO],
                        cierran=[TipoMaterial.TMC]))
    assert exc.value.campo == "Q_evento_extremo_m3s"
    assert "visto en Concreto reforzado" in str(exc.value)


def test_3_bloquea_tambien_si_el_escalon_detenido_ya_incumplia():
    """
    Como el dato que falta (ficha T4-10): el material anterior no termino de
    recorrer su catalogo, cumpliera o no el escalon en que se detuvo, y
    adoptar el siguiente seria elegirlo por descarte.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        _disenar(_Doble(fase_5=[TipoMaterial.CONCRETO_REFORZADO],
                        cierran=[TipoMaterial.HDPE],
                        completadas=(_verificacion(False),)))
    assert exc.value.campo == "Q_evento_extremo_m3s"


def test_3_sale_el_del_primer_material_detenido():
    with pytest.raises(DatoInvalidoError) as exc:
        _disenar(_Doble(fase_5=[TipoMaterial.CONCRETO_REFORZADO,
                                TipoMaterial.TMC],
                        cierran=[TipoMaterial.HDPE]))
    assert "visto en Concreto reforzado" in str(exc.value)


def test_3_guardia_el_de_antes_de_la_fase_5_no_bloquea_al_que_cierra():
    """
    Fuera del alcance de (3), que es el de T11-03 y VE-2 A1/N1 (la Fase 5):
    un dato invalido de antes de la Fase 5 en UN material no impide que otro
    cierre (`test_MD.py::test_un_material_que_revienta_no_impide_que_otro_cierre`).
    """
    resultado = _disenar(_Doble(antes=[TipoMaterial.CONCRETO_REFORZADO],
                                cierran=[TipoMaterial.TMC]))
    assert resultado.aceptado and resultado.material.tipo is TipoMaterial.TMC


def test_3_guardia_un_invalido_de_un_material_posterior_no_cuenta():
    """El que cierra es el primero: los siguientes no se recorren."""
    resultado = _disenar(_Doble(fase_5=[TipoMaterial.TMC],
                                cierran=[TipoMaterial.CONCRETO_REFORZADO]))
    assert resultado.material.tipo is TipoMaterial.CONCRETO_REFORZADO


# ===========================================================================
# (4) El dato invalido de antes de la Fase 5
# ===========================================================================

def test_4_el_de_antes_de_la_fase_5_comun_a_todos_sale_con_su_campo():
    with pytest.raises(DatoInvalidoError) as exc:
        _disenar(_Doble(antes=TODOS))
    assert exc.value.campo == "D"
    assert "el diametro debe ser positivo" in str(exc.value)


def test_4_comun_a_todos_mezclando_los_de_antes_y_los_de_la_fase_5():
    """
    Dos materiales detenidos en la Fase 5 sobre escalones que ya incumplian
    (no deciden por si solos) y uno antes de la Fase 5: a TODOS los detuvo
    un dato invalido. Sale el del primero.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        _disenar(_Doble(antes=[TipoMaterial.CONCRETO_REFORZADO],
                        fase_5=[TipoMaterial.TMC, TipoMaterial.HDPE],
                        completadas=(_verificacion(False),)))
    assert exc.value.campo == "D"


def test_4_guardia_el_de_antes_de_la_fase_5_en_un_solo_material_no_decide():
    """
    La otra mitad de T4-10, que no cambia: un material detenido antes de la
    Fase 5 y los demas evaluados e incumpliendo: «no factible», con el
    material citado como no evaluable.
    """
    with pytest.raises(DisenoNoFactibleError) as exc:
        _disenar(_Doble(antes=[TipoMaterial.TMC]))
    assert "TMC galvanizada: material no evaluable" in exc.value.motivo


def test_4_el_arranque_negativo_por_la_fase_5_real():
    """El caso de la rama de error, con M3, M4 y M5 de verdad."""
    with declarados({M2.CRITERIO_DIAMETROS: ARRANQUE_NEGATIVO}):
        with pytest.raises(DatoInvalidoError) as exc:
            MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE)
    assert exc.value.campo == "D"
    assert exc.value.valor == pytest.approx(ARRANQUE_NEGATIVO["inicio"],
                                            rel=REL_TRANSPORTE)


def test_4_la_rama_de_error_por_el_servicio_es_un_dato_invalido():
    """
    La corrida 3 de la linea base (perfil, luz 2.75, arranque negativo): los
    tres puntos de Familia A y B salen con el bloqueo DATO_INVALIDO sobre
    'D' en el bucle de MD, y ninguno «no factible».
    """
    with declarados({M2.CRITERIO_DIAMETROS: ARRANQUE_NEGATIVO}):
        externos = cli.cargar_datos_externos(None, {"luz_m": 2.75})
        informe = servicio.correr(CSV, externos, alcance=cli.ALCANCE_PERFIL)
    for id_punto in ("A-01", "A-02", "B-01"):
        punto = next(p for p in informe.puntos if p.punto.id == id_punto)
        assert not punto.dimensionado
        tipos = {b.tipo for b in punto.bloqueos}
        assert TipoDeBloqueo.DISENO_NO_FACTIBLE not in tipos, id_punto
        b = next(b for b in punto.bloqueos
                 if b.tipo is TipoDeBloqueo.DATO_INVALIDO
                 and b.etapa == servicio.ETAPA_BUCLE_DE_MD)
        assert b.campo == "D", id_punto


# ===========================================================================
# La ficha
# ===========================================================================

def test_la_ficha_T11_03_cierra_3_y_4():
    texto = FICHAS.read_text(encoding="utf-8")
    ficha = re.search(r"^## T11-03 · .*?(?=^## |\Z)", texto,
                      flags=re.M | re.S).group(0)
    abierto = re.search(r"^- \*\*Abierto:\*\*.*?(?=^- \*\*|\Z)", ficha,
                        flags=re.M | re.S).group(0)
    assert "(3)" not in abierto and "(4)" not in abierto
    assert "_exigir_datos_validos_al_aceptar" in ficha
