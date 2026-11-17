"""
tests/test_ve2_correcciones.py
==============================
Las correcciones de la revision independiente de VE-2 (Fable,
`proceso/planes_mejora/ve2_estado/REVISION_FABLE.md`), hallazgo A1.

A1. EL DATO QUE FALTA EN LA FASE 5 SOBRE UN ESCALON QUE CUMPLE LO DEMAS
DECIDE, COMO EL DATO INVALIDO. `MD.disenar_punto` trataba distinto a los dos
hermanos: un `DatoInvalidoError` de la Fase 5 sobre un escalon que cumplia
todo lo que se le habia evaluado salia con su campo (T11-03,
`MD._exigir_datos_validos`), y un `DatoFaltanteError` sobre el mismo escalon
solo decidia si lo marcaba la Fase 8 (`ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`,
T-5). El que levanta V8 (`Q_evento_extremo_m3s`, que pide una vez declarado
su TR) se perdia en «NO FACTIBLE» cuando otro material incumplia. Medido por
la revision con la variante `caudal_calculado` del juego de T-11: B-01 salia
`DisenoNoFactibleError` con `campo: None` y un delta de rasante, cuando su
HDPE Ø 1.20 m cumple la tabla de la Fase 5 y solo le falta el caudal del
evento extremo; con ese caudal declarado coherente (1.99 m3/s) el punto se
detiene en el perfil del fabricante del HDPE, otro dato. CLAUDE.md
(«Excepciones»): «un punto al que solo le falta un dato no es "no
factible"».

LO QUE NO CAMBIA, y esta fijado aqui (la ficha T4-10): el dato que falta
sobre un escalon que YA incumplia, y el que falta ANTES de la Fase 5 (la
pared de un diametro, sin `verificaciones_completadas`), siguen dejando el
punto en lo que son los materiales que si se evaluaron.

SE ESCRIBIO EN ROJO PRIMERO, contra d9b59f9: fallaban los dos que piden el
`DatoFaltanteError` decisivo de la Fase 5 y el del servicio con la variante.
"""

from __future__ import annotations

import pytest

from src import servicio
from src.modelos import (DatoFaltanteError, DisenoNoFactibleError,
                         TipoDeBloqueo, TipoMaterial)
from src.modulos import MD
from tests.apoyo import validacion_integral as V
from tests.fixtures import juego_validacion_integral as J
from tests.test_MD import L_CONDUCTO, TW_LIBRE, _punto, _verificacion


class _DatoFaltante:
    """
    Verificador que levanta un `DatoFaltanteError` en los materiales
    indicados. Con `completadas` lo marca como de la FASE 5 (lo que hace
    `M5.verificar` al detenerse); sin ellas, como uno de antes de la tabla.
    Los demas materiales se rechazan.
    """

    def __init__(self, tipos, completadas=None):
        self.tipos = set(tipos)
        self.completadas = completadas

    def __call__(self, *, punto, material, seccion, resultado):
        if material.tipo in self.tipos:
            exc = DatoFaltanteError(
                "Q_evento_extremo_m3s",
                detalle=f"lo pide V8 (visto en {material.nombre})")
            if self.completadas is not None:
                exc.verificaciones_completadas = tuple(self.completadas)
            raise exc
        return (_verificacion(False, obtenido="x", admisible="y"),)


def test_el_dato_que_falta_sobre_un_escalon_que_cumple_lo_demas_decide():
    """
    Un solo material se detiene en la Fase 5 por un dato que falta, sobre un
    escalon que cumple todo lo evaluado; los otros dos se evaluan y no
    cumplen. El punto no es «no factible»: le falta un dato.
    """
    verificar = _DatoFaltante([TipoMaterial.HDPE], (_verificacion(True),))
    with pytest.raises(DatoFaltanteError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert exc.value.campo == "Q_evento_extremo_m3s"

    # Con dos decisivos sale el del primero de los dos en el orden de M2.
    verificar = _DatoFaltante([TipoMaterial.TMC, TipoMaterial.HDPE],
                              (_verificacion(True),))
    with pytest.raises(DatoFaltanteError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert "visto en TMC galvanizada" in str(exc.value)


def test_el_dato_que_falta_en_la_primera_fila_de_la_fase_5_decide():
    """
    La tupla vacia de `verificaciones_completadas` es la de la primera fila
    de la tabla: el escalon no incumplio nada antes de que faltara el dato.
    """
    verificar = _DatoFaltante([TipoMaterial.HDPE], ())
    with pytest.raises(DatoFaltanteError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert exc.value.campo == "Q_evento_extremo_m3s"


def test_el_dato_que_falta_sobre_un_escalon_que_ya_incumple_no_decide():
    """La otra mitad de la ficha T4-10, que no cambia."""
    verificar = _DatoFaltante([TipoMaterial.HDPE], (_verificacion(False),))
    with pytest.raises(DisenoNoFactibleError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert "Q_evento_extremo_m3s" in exc.value.motivo


def test_el_dato_que_falta_antes_de_la_fase_5_sigue_como_hasta_hoy():
    """
    Sin `verificaciones_completadas` (la pared de un diametro, que M2 pide
    antes de la tabla) y con otros materiales evaluados que incumplen: «no
    factible», con el material citado como no evaluado.
    """
    verificar = _DatoFaltante([TipoMaterial.HDPE], completadas=None)
    with pytest.raises(DisenoNoFactibleError):
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)


def _b01(cambios):
    informe = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
    return next(p for p in informe.puntos if p.punto.id == "B-01")


def test_la_variante_caudal_calculado_dice_que_a_B01_le_falta_un_dato():
    """
    El caso de la revision, por el servicio: con la variante de referencia
    de la hidrologia (el caudal calculado y sin el del evento extremo, que
    la hidrologia no calcula: ficha T1-03), B-01 sale con el bloqueo del
    dato que falta, con su campo, y no «no factible».
    """
    b01 = _b01(J.VARIANTES[V.VARIANTE_DE_REFERENCIA][1])
    assert not b01.dimensionado
    tipos = {b.tipo for b in b01.bloqueos}
    assert TipoDeBloqueo.DISENO_NO_FACTIBLE not in tipos
    b = next(b for b in b01.bloqueos
             if b.tipo is TipoDeBloqueo.DATO_FALTANTE)
    assert b.campo == "Q_evento_extremo_m3s"
    assert b.etapa == servicio.ETAPA_BUCLE_DE_MD


def test_con_el_evento_extremo_coherente_B01_espera_el_perfil_del_hdpe():
    """
    El caso 3 de la revision: declarado un caudal del evento extremo
    coherente con el calculado (1.99 m3/s, 1.11 veces 1.79), el escalon pasa
    V8 y lo detiene la Fase 8 por el perfil del fabricante del HDPE (T-5).
    Prueba que ese escalon cumple la tabla de la Fase 5.
    """
    cambios = [c for c in J.VARIANTES[V.VARIANTE_DE_REFERENCIA][1]
               if not (c[0] == "externo" and c[1] == "B-01"
                       and c[2] == "Q_evento_extremo_m3s")]
    cambios.append(("externo", "B-01", "Q_evento_extremo_m3s", 1.99))
    b01 = _b01(cambios)
    assert not b01.dimensionado
    b = next(b for b in b01.bloqueos
             if b.tipo is TipoDeBloqueo.DATO_FALTANTE)
    assert b.campo == "perfil_hdpe_fabricante"
