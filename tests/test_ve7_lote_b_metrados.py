"""
tests/test_ve7_lote_b_metrados.py
=================================
VE-7, lote B, item B7 (VE5-MET-01; decision del consultor Fable, triaje
VE-7, 2026-11-20): lo que la Fase 11 no metra --el relleno para estructuras
(502.A), la cama y el emboquillado de la entrada-- sale como un renglon
EXPLICITO «no medido», con su motivo, en la fase de los metrados: un
`Bloqueo` de `servicio.FASE_METRADOS` como cualquier renglon que no se pudo
medir, para que el cuadro no lo omita en silencio. Los demas rubros siguen.

Sobre la corrida de referencia `expediente_cabezal` (la de
`tests/test_M12_metrados.py`), con A-01 metrado.
"""

import pytest

from src import servicio
from src.modelos import MOTIVO_METODO_NO_EVALUABLE_METRADO, TipoDeBloqueo
from src.modulos import M12_metrados as M12


@pytest.fixture(scope="module")
def corrida():
    from src import indice_formulas as idx
    ref = next(c for c in idx.CORRIDAS_DE_REFERENCIA
               if c.nombre == "expediente_cabezal")
    return idx.correr_referencia(ref)


def _a01(corrida):
    return next(p for p in corrida.puntos if p.punto.id == "A-01")


def test_los_no_medidos_son_bloqueos_de_la_fase_de_metrados(corrida):
    a01 = _a01(corrida)
    assert a01.metrado is not None and a01.metrado.renglones
    no_medidos = [b for b in a01.bloqueos
                  if b.fase == servicio.FASE_METRADOS
                  and b.etapa.endswith(": no medido")]
    etapas = {b.etapa for b in no_medidos}
    # Dictamen Fable (defecto 7): en una TUBERIA la cama la paga la partida
    # del tubo, y su «no medido» era falso: dos bloqueos, no tres.
    assert a01.resultado.material.forma.value == "circular"
    assert etapas == {M12.etapa_no_medido(e)
                      for e in (M12.NO_MEDIDO_RELLENO,
                                M12.NO_MEDIDO_EMBOQUILLADO)}
    for b in no_medidos:
        assert b.tipo is TipoDeBloqueo.METODO_NO_EVALUABLE
        assert MOTIVO_METODO_NO_EVALUABLE_METRADO in b.mensaje
        assert "no medido:" in b.mensaje


def test_los_demas_rubros_siguen_medidos(corrida):
    rubros = {r.rubro for r in _a01(corrida).metrado.renglones}
    assert {"conducto", "excavacion", "concreto"} <= rubros


def test_el_renglon_no_medido_lleva_su_motivo_y_lo_que_haria_falta():
    for elemento, (procedimiento, motivo) in M12.RENGLONES_NO_MEDIDOS.items():
        with pytest.raises(Exception) as exc:
            M12.renglon_no_medido(elemento, id_punto="X-01")
        assert exc.value.procedimiento == procedimiento
        assert exc.value.motivo == f"no medido: {motivo}"
        assert "X-01" in str(exc.value)
