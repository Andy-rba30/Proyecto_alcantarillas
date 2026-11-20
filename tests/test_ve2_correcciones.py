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
sobre un escalon que YA incumplia, el que falta antes de la Fase 5 (sin
`verificaciones_completadas`) y, desde N1 de la verificacion de estas
correcciones, el dato de CATALOGO que falta dentro de la Fase 5 (la fila de
pared de un diametro, que pide V7 con V1 a V6 ya cumplidas) siguen dejando
el punto en lo que son los materiales que si se evaluaron. Esta frase
decia que la pared se pedia «antes de la Fase 5»: era falso, y por eso A1
la volvia decisiva sin que ningun test lo viera.

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
from tests.test_t11_no_factible_por_rasante import ABS_MM, DELTA_TMC_195


class _DatoFaltante:
    """
    Verificador que levanta un `DatoFaltanteError` en los materiales
    indicados. Con `completadas` lo marca como de la FASE 5 (lo que hace
    `M5.verificar` al detenerse); sin ellas, como uno de antes de la tabla.
    Los demas materiales se rechazan.
    """

    def __init__(self, tipos, completadas=None, campo="Q_evento_extremo_m3s"):
        self.tipos = set(tipos)
        self.completadas = completadas
        self.campo = campo

    def __call__(self, *, punto, material, seccion, resultado):
        if material.tipo in self.tipos:
            exc = DatoFaltanteError(
                self.campo,
                detalle=f"lo pide la Fase 5 (visto en {material.nombre})")
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
    Sin `verificaciones_completadas` (lo que M3 o M4 piden antes de la
    tabla; la pared de un diametro NO es de aqui: la pide V7 dentro de la
    Fase 5, ver los tests de N1 abajo) y con otros materiales evaluados que
    incumplen: «no factible», con el material citado como no evaluado.
    """
    verificar = _DatoFaltante([TipoMaterial.HDPE], completadas=None)
    with pytest.raises(DisenoNoFactibleError):
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)


def _del_dimensionado(bloqueos):
    """
    --- VE-6 --- Los bloqueos del punto menos los de las fases que se
    registran al lado del dimensionado sin detenerlo
    (`servicio.FASES_AL_MARGEN_DEL_DIMENSIONADO`): desde VE-5 (catlic) el
    juego, a expediente, lleva el de la Fase 0-bis (`licuefaccion_ems`, que
    el juego no declara; ficha VE5-CAT-03). Estos tests hablan del bucle de
    MD, y la licuefaccion no lo detiene ni se antepone a sus faltas.
    """
    return [b for b in bloqueos
            if b.fase not in servicio.FASES_AL_MARGEN_DEL_DIMENSIONADO]


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
    b = next(b for b in _del_dimensionado(b01.bloqueos)
             if b.tipo is TipoDeBloqueo.DATO_FALTANTE)
    assert b.campo == "Q_evento_extremo_m3s"
    assert b.etapa == servicio.ETAPA_BUCLE_DE_MD


def test_con_el_evento_extremo_coherente_B01_espera_el_perfil_del_hdpe():
    """
    El caso 3 de la revision: declarado un caudal del evento extremo
    coherente con el calculado (1.99 m3/s, 1.11 veces 1.79), el escalon pasa
    V8. Hasta VE-3.11 lo detenia la Fase 8 por el perfil del fabricante del
    HDPE (T-5). DESDE VE-3.11 (H4 de los ensayos de diseño del conducto) V7
    suma el peso propio del concreto, y el concreto Ø 1.20 m, que solo fallaba
    V7, cierra antes de llegar al HDPE: B-01 se DIMENSIONA. El nombre del
    test se conserva por la traza de la revision.
    """
    cambios = [c for c in J.VARIANTES[V.VARIANTE_DE_REFERENCIA][1]
               if not (c[0] == "externo" and c[1] == "B-01"
                       and c[2] == "Q_evento_extremo_m3s")]
    cambios.append(("externo", "B-01", "Q_evento_extremo_m3s", 1.99))
    b01 = _b01(cambios)
    assert b01.dimensionado
    assert b01.resultado.material.tipo is TipoMaterial.CONCRETO_REFORZADO
    assert b01.resultado.seccion.etiqueta() == "Ø 1.20 m"


# ===========================================================================
# N1 de la verificacion de las correcciones (Fable): SOLO EL DATO DEL PUNTO
# ===========================================================================
# A1 tal como se escribio primero volvia decisivo TODO dato que falta en la
# Fase 5 sobre un escalon que cumple lo evaluado, y eso incluia la fila de
# pared de un diametro del catalogo que V7 pide (`espesor_pared_conducto`):
# la verificacion midio 30 casos del juego de T-11 que pasaban de «NO
# FACTIBLE POR RASANTE», con su delta, a «falta la pared», y que declarada la
# fila volvian al mismo «no factible» con el mismo delta. Decision del dueño
# (2026-11-17): decide solo el dato DEL PUNTO; el que nombra un criterio
# --un dato de catalogo o de producto-- sigue la ficha T4-10.


def test_el_dato_de_catalogo_que_falta_en_la_fase_5_no_decide():
    """
    La fila de pared que V7 pide, sobre un escalon que cumple lo evaluado, y
    los otros materiales que incumplen: «no factible», como en T4-10.
    """
    verificar = _DatoFaltante([TipoMaterial.HDPE], (_verificacion(True),),
                              campo="espesor_pared_conducto[hdpe][1350]")
    with pytest.raises(DisenoNoFactibleError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert "espesor_pared_conducto[hdpe][1350]" in exc.value.motivo

    # Con el campo de un criterio sin corchetes, igual.
    verificar = _DatoFaltante([TipoMaterial.HDPE], (_verificacion(True),),
                              campo="espesor_pared_conducto")
    with pytest.raises(DisenoNoFactibleError):
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)


def test_el_caso_real_de_la_pared_sigue_no_factible_por_rasante_con_su_delta():
    """
    El caso medido por la verificacion, por el servicio: A-01 del juego con
    S = 0.004 y un evento extremo de 3 veces el caudal. El HDPE Ø 1.35 m
    cumple V1 a V6 y V7 pide su fila de pared, que el catalogo no trae. Sale
    «no factible por rasante» con el delta de 7.A de `d9b59f9` (0.3198 m),
    no «falta la pared».

    LA VERIFICACION LO MIDIO CON Q = 1.0 m3/s; DESDE VE-3.11 (H4 de los
    ensayos de diseño del conducto) V7 suma el peso propio del concreto y con
    ese caudal el concreto Ø 1.20 m, que solo fallaba V7, cumple: el punto se
    dimensiona. El caso se lleva a Q = 1.4 m3/s (evento extremo 4.2), donde
    el HDPE sigue detenido por su pared de 1.35 m y el punto sigue «no
    factible por rasante» con el mismo delta (medido en VE-3.11).
    """
    cambios = (("celda", "A-01", "Q_m3s", "1.4"),
               ("celda", "A-01", "S_cauce", "0.004"),
               ("externo", "A-01", "Q_evento_extremo_m3s", 4.2))
    informe = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert not a01.dimensionado
    tipos = {b.tipo for b in _del_dimensionado(a01.bloqueos)}
    assert TipoDeBloqueo.DATO_FALTANTE not in tipos
    b = next(b for b in a01.bloqueos
             if b.tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE)
    assert "espesor_pared_conducto[hdpe][1350]" in b.mensaje
    # El delta es el del TMC Ø 1.95 m de A-01, el dorado a mano de T11-03
    # (0.31981 m), con su tolerancia nombrada.
    assert b.delta_rasante_m == pytest.approx(DELTA_TMC_195, abs=ABS_MM)


def test_otro_dato_del_punto_de_V8_tambien_decide():
    """
    La regla es «dato del punto», no «Q_evento_extremo_m3s» (B1 de la
    segunda verificacion Fable: el mutante que la limitaba a ese campo
    sobrevivia). A-01 con Q = 1.5 m3/s, S = 0.004 y sin el tirante aguas
    abajo del evento extremo: un escalon que cumple lo evaluado se detiene
    en V8 por `TW_evento_extremo_m`, y el punto sale con ese dato que falta
    (en `d9b59f9` salia «no factible por rasante», delta 0.31981).
    """
    cambios = (("celda", "A-01", "Q_m3s", "1.5"),
               ("celda", "A-01", "S_cauce", "0.004"),
               ("externo", "A-01", "TW_evento_extremo_m", None))
    informe = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert not a01.dimensionado
    assert TipoDeBloqueo.DISENO_NO_FACTIBLE not in {b.tipo for b in a01.bloqueos}
    b = next(b for b in _del_dimensionado(a01.bloqueos)
             if b.tipo is TipoDeBloqueo.DATO_FALTANTE)
    assert b.campo == "TW_evento_extremo_m"
