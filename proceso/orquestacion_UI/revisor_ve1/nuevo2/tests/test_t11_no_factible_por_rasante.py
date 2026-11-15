"""
tests/test_t11_no_factible_por_rasante.py
=========================================
La aceptacion de la correccion de T11-03 (hallazgo H4 de la auditoria
adversarial de T-11): el DIAGNOSTICO del punto al que ningun escalon le
cierra y cuya progresion se detiene en la subrasante.

Tres cosas, las tres de `MD` y ninguna de calculo:

A. EL ESCALON QUE NO CABE NO ES UN DATO INVALIDO. Un escalon cuya clave
   fisica queda a nivel de la subrasante o por encima salia como
   `DatoInvalidoError` sobre 'cota_subrasante' --un dato que nadie toco--, el
   material como «no evaluable» y el punto como «no factible» sin el motivo
   verdadero. Ahora el material se descarta POR RASANTE, con el motivo del
   escalon anterior y el del que no cabe, y el punto sale «no factible
   por rasante».
B. EL DELTA DE RASANTE. `DisenoNoFactibleError.delta_rasante_m` lleva el del
   tamizado de 7.A (`M7.tamizado_rasante`) del escalon que no cabe SOLO cuando
   ese numero es geometria pura: el escalon cumple todo lo que se le evaluo
   (V4 incluida, de modo que la condicion de resguardo ya esta satisfecha) y
   gobierna el recubrimiento. Es cota inferior PARA ESE ESCALON y se rotula
   asi; cuando el escalon que no cabe ademas incumple algo, no hay delta.
C. EL HERMANO. Un `DatoInvalidoError` de un DATO DEL PUNTO levantado en la
   Fase 5 sale como bloqueo DATO_INVALIDO con su `campo`, por el mismo patron
   que PC-28 y T-5 usan para el dato que falta, y no como «no factible». El
   que M3 o M4 levantan ANTES de la Fase 5 queda como estaba (la rama de
   error de la linea base no cambia de tipo), y esta fijado.

LO QUE NO CAMBIA, y esta fijado aqui: los escalones recorridos y las
verificaciones evaluadas en cada uno (las `iteraciones`), el resultado
aceptado cuando algun material cierra, y el `DatoInvalidoError` directo de
`M5.altura_relleno_sobre_clave`.

LOS DORADOS ESTAN A MANO, con la aritmetica escrita (fila A-01 del fixture,
fondo de entrada adoptado igual al terreno, 42.10 msnm):

    Concreto Ø 1.80 m   clave = 42.10 + 1.80 + 0.175 (pared B de M 170M)
                              = 44.075 msnm; subrasante 44.05: +0.025 m
                        h_rec = max(Bc/8, 12 in) = max(2.15/8, 0.3048)
                              = 0.3048 m   (Tabla 12.6.6.3-1, pav. flexible)
                        e_paq = 44.20 - 44.05 = 0.15 m
                        rasante minima = 44.075 + 0.3048 + 0.15 = 44.5298
                        delta = 44.5298 - 44.20 = 0.3298 m
    TMC Ø 1.95 m        clave = 42.10 + 1.95 + 0.01501 (13 mm + 2.01 mm)
                              = 44.06501 msnm: +0.01501 m
                        h_rec = max(1.95/8, 0.3048) = 0.3048 m
                        rasante minima = 44.51981; delta = 0.31981 m

SE ESCRIBIO EN ROJO PRIMERO: contra `c774035` (la rama antes de la
correccion) fallan todos salvo las guardias de «lo que no cambia»; el
numero, en el informe de la correccion.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import (DatoFaltanteError, DatoInvalidoError,
                         DisenoNoFactibleError, Familia, FormaSeccion,
                         TipoDeBloqueo, TipoMaterial)
from src.modulos import M5_verificaciones as M5
from src.modulos import MD
from src.modulos.M2_material import catalogo
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_MD import L_CONDUCTO, TW_LIBRE, _punto, _verificacion

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
ENTRADAS_AMPLIADAS = (RAIZ / "tests" / "linea_base_familia_c"
                      / "entradas_ampliadas.json")

# --- Los dorados, a mano (ver el docstring) --------------------------------
CLAVE_CONCRETO_180 = 42.10 + 1.80 + 0.175            # 44.075 msnm
EXCESO_CONCRETO_180 = CLAVE_CONCRETO_180 - 44.05     # +0.025 m
DELTA_CONCRETO_180 = CLAVE_CONCRETO_180 + 0.3048 + 0.15 - 44.20   # 0.3298 m
CLAVE_TMC_195 = 42.10 + 1.95 + 0.01501               # 44.06501 msnm
DELTA_TMC_195 = CLAVE_TMC_195 + 0.3048 + 0.15 - 44.20             # 0.31981 m
# A-02 con el juego sin TW: Concreto Ø 1.95 m, pared 0.188 m.
#   clave = 39.85 + 1.95 + 0.188 = 41.988; subrasante 41.85: +0.138 m
#   h_rec = max((1.95 + 2*0.188)/8 = 0.29075, 0.3048) = 0.3048
#   delta = 41.988 + 0.3048 + 0.15 - 42.00 = 0.4428 m
DELTA_A02_CONCRETO_195 = 39.85 + 1.95 + 0.188 + 0.3048 + 0.15 - 42.00

ABS_MM = 5e-7     # los dorados son sumas exactas de datos con 5 decimales


@pytest.fixture(autouse=True)
def _con_los_valores_del_archivo():
    """
    Los dorados son los del EXPEDIENTE (la linea base, que la CLI genera en
    subproceso): se retiran las declaraciones de prueba del `conftest.py` de
    la raiz --la pared sintetica del TMC (0.013 m) y del HDPE (0.050 m en
    todos los diametros)--, que su fixture repone al terminar cada test.
    """
    for clave in ca.valores_dinamicos():
        ca.quitar_valor_dinamico(clave)


def _correr_con_los_valores_del_archivo(ruta_externos):
    """
    `servicio.correr` a nivel de perfil con las dos entradas de la linea
    base (`--luz 2.75` y, si se da, el JSON de entradas ampliadas), sin
    declaraciones en caliente y reponiendolas al salir: una fixture de
    modulo corre ANTES que la de funcion de arriba.
    """
    previas = ca.valores_dinamicos()
    for clave in previas:
        ca.quitar_valor_dinamico(clave)
    try:
        externos = cli.cargar_datos_externos(ruta_externos, {"luz_m": 2.75})
        return servicio.correr(CSV, externos, alcance=cli.ALCANCE_PERFIL)
    finally:
        for clave, valor in previas.items():
            ca.establecer_valor_dinamico(clave, valor)


class _GeometriaReal:
    """
    Verificador de prueba con la GEOMETRIA REAL: por cada escalon devuelve una
    sola fila (cumple o no, segun `decide(material, D)`; ninguna fila si
    `decide` es None, que no es un diseño aceptable) y despues pide a M5
    el relleno sobre la clave, que es lo que hace V7. Cuando la clave no cabe,
    M5 levanta su `DatoInvalidoError` de siempre y, como en `M5.verificar`, la
    excepcion se lleva en `verificaciones_completadas` lo ya evaluado.
    """

    def __init__(self, decide):
        self.decide = decide
        self.llamadas = []

    def __call__(self, *, punto, material, seccion, resultado):
        self.llamadas.append((material.tipo, seccion.etiqueta()))
        hechas = (() if self.decide is None else
                  (_verificacion(self.decide(material, seccion.altura)),))
        try:
            M5.altura_relleno_sobre_clave(punto=punto, material=material,
                                          seccion=seccion)
        except (DatoInvalidoError, DatoFaltanteError) as exc:
            exc.verificaciones_completadas = hechas
            raise
        return hechas


def _concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


def _etiquetas(pasos):
    """Los escalones de una traza por su etiqueta («Ø 1.80 m»)."""
    return [p.seccion.etiqueta() for p in pasos]


def _diametros(desde_mm, hasta_mm):
    """Las etiquetas de la progresion de 150 en 150 mm, extremos incluidos."""
    return [f"Ø {mm / 1000:.2f} m" for mm in range(desde_mm, hasta_mm + 1, 150)]


def _recorrer(material, verificar, punto=None):
    pasos = []
    punto = punto if punto is not None else _punto()
    par = MD.disenar_material(punto, material, Q=punto.Q_m3s, S=punto.S_cauce,
                              L=L_CONDUCTO, TW=TW_LIBRE, verificar=verificar,
                              registrar=pasos.append)
    return par, pasos


# ===========================================================================
# A. El escalon que no cabe: descarte por rasante, no dato invalido
# ===========================================================================

def test_el_material_cuyo_escalon_no_cabe_se_descarta_por_rasante():
    (resultado, motivo), pasos = _recorrer(
        _concreto(), _GeometriaReal(lambda m, D: False))

    assert resultado is None
    assert MD.MENSAJE_SIN_CABIDA in motivo
    assert "Dato invalido" not in motivo and "no evaluable" not in motivo
    # El escalon que no cabe, con el par culpable: la clave y la subrasante.
    assert "Ø 1.80 m" in motivo and MD.MARCA_ESCALON_SIN_CABIDA in motivo
    assert "44.075" in motivo and "44.050" in motivo and "+0.025" in motivo
    # ... y el motivo del escalon anterior, que es por lo que hacia falta mas.
    assert "Ø 1.65 m: incumple V1" in motivo

    # Los escalones, los de siempre: de 0.90 a 1.80 de 0.15 en 0.15.
    assert _etiquetas(pasos) == _diametros(900, 1800)
    ultimo = pasos[-1]
    assert not ultimo.aceptado
    assert all(p.sin_cabida is None for p in pasos[:-1])
    assert ultimo.sin_cabida.cota_clave == pytest.approx(
        CLAVE_CONCRETO_180, abs=ABS_MM)
    assert ultimo.sin_cabida.cota_subrasante == pytest.approx(44.05, abs=ABS_MM)
    assert ultimo.sin_cabida.exceso_m == pytest.approx(
        EXCESO_CONCRETO_180, abs=ABS_MM)
    # Lo que se le evaluo antes de quedarse sin relleno viaja en la traza.
    assert [v.codigo for v in ultimo.verificaciones] == ["V1"]
    assert MD.MARCA_ESCALON_SIN_CABIDA in ultimo.motivo
    assert MD.MARCA_ESCALON_SIN_EVALUAR not in ultimo.motivo
    assert "DatoInvalidoError" not in ultimo.motivo
    assert ultimo.motivo.endswith("de lo que se le evaluo antes incumple V1")


def test_un_escalon_en_el_umbral_exacto_tampoco_cabe():
    """
    La frontera es la de M5 (`altura <= TOL`): con la subrasante EXACTAMENTE
    en la clave de Ø 0.90 m (42.10 + 0.90 + 0.10 = 43.10) no hay relleno, y
    con un milimetro de relleno el escalon se evalua.
    """
    enrasado = _punto(cota_subrasante=43.10, cota_rasante=43.25)
    (_, motivo), pasos = _recorrer(_concreto(),
                                   _GeometriaReal(lambda m, D: False), enrasado)
    assert _etiquetas(pasos) == ["Ø 0.90 m"]
    assert pasos[0].sin_cabida.exceso_m == pytest.approx(0.0, abs=ABS_MM)
    assert "Es el primer escalon del catalogo" in motivo

    con_un_milimetro = _punto(cota_subrasante=43.101, cota_rasante=43.251)
    (_, motivo), pasos = _recorrer(
        _concreto(), _GeometriaReal(lambda m, D: False), con_un_milimetro)
    assert _etiquetas(pasos) == ["Ø 0.90 m", "Ø 1.05 m"]
    assert pasos[0].sin_cabida is None and pasos[1].sin_cabida is not None
    # El segundo escalon ya tiene un anterior, y el motivo lo trae.
    assert "Es el primer escalon del catalogo" not in motivo
    assert "Escalon anterior: Ø 0.90 m: incumple V1" in motivo


def test_un_dato_invalido_de_subrasante_con_la_clave_que_cabe_no_es_rasante():
    """
    El reconocimiento es por GEOMETRIA: un `DatoInvalidoError` sobre
    'cota_subrasante' en un escalon cuya clave SI cabe (Ø 0.90 m: 43.10 msnm
    bajo 44.05) no se disfraza de «no cabe». Sigue subiendo, como hasta hoy.
    """
    def reclama_otra_cosa(*, punto, material, seccion, resultado):
        raise DatoInvalidoError("cota_subrasante", valor=44.05,
                                id_punto=punto.id, motivo="otra queja")

    pasos = []
    with pytest.raises(DatoInvalidoError):
        MD.disenar_material(_punto(), _concreto(), Q=_punto().Q_m3s,
                            S=_punto().S_cauce, L=L_CONDUCTO, TW=TW_LIBRE,
                            verificar=reclama_otra_cosa,
                            registrar=pasos.append)
    assert pasos[-1].sin_cabida is None
    assert MD.MARCA_ESCALON_SIN_EVALUAR in pasos[-1].motivo


def test_M5_conserva_su_dato_invalido_directo():
    """Lo fijan C09 / SIS-F-10 y lo usa la Fase 8: aqui solo se recuerda."""
    from src.modelos import SeccionCircular
    with pytest.raises(DatoInvalidoError) as exc:
        M5.altura_relleno_sobre_clave(punto=_punto(), material=_concreto(),
                                      seccion=SeccionCircular(1.80))
    assert exc.value.campo == "cota_subrasante"


def test_el_campo_que_MD_reconoce_es_el_que_M5_levanta():
    assert MD.CAMPO_SUBRASANTE == "cota_subrasante"


# ===========================================================================
# B. El delta de rasante: el de 7.A, solo cuando es geometria pura
# ===========================================================================

def test_el_delta_es_el_de_7A_cuando_el_escalon_cumple_lo_evaluado():
    """Ø 0.90 a 1.65 incumplen; Ø 1.80 cumple lo evaluado y no cabe."""
    (_, motivo), pasos = _recorrer(
        _concreto(), _GeometriaReal(lambda m, D: D > 1.70))
    sin_cabida = pasos[-1].sin_cabida
    assert sin_cabida.delta_rasante_m == pytest.approx(
        DELTA_CONCRETO_180, abs=ABS_MM)
    # La aritmetica de 7.A, impresa: clave + h_rec + e_paq = rasante minima.
    for cifra in ("0.330 m", "44.075", "0.3048", "0.150", "44.530", "44.200"):
        assert cifra in sin_cabida.nota, cifra
    assert "COTA INFERIOR" in sin_cabida.nota
    assert "no el remedio verificado del punto" in sin_cabida.nota
    # El fondo de entrada es el terreno adoptado: el delta es provisional
    # (T-6) y la nota lo dice con el aviso de M7.
    assert "PROVISIONAL" in sin_cabida.nota
    assert sin_cabida.nota in motivo
    assert pasos[-1].motivo.endswith("lo que se le evaluo antes cumple")


def test_el_escalon_al_que_no_se_le_evaluo_nada_lo_dice():
    """
    Un verificador que no alcanza a evaluar ninguna fila antes de quedarse
    sin relleno: el motivo no afirma que «cumple» lo que nadie midio. Y como
    V4 no se evaluo, nada dice que el resguardo este satisfecho: aqui el
    tamizado lo deja gobernar (42.10 + HW + 0.80 + 0.15 pasa de la rasante,
    43.25, con cualquier HW mayor de 0.20 m) y NO hay delta, porque ese
    numero llevaria el HW dentro.
    """
    _, pasos = _recorrer(_concreto(), _GeometriaReal(None),
                         _punto(cota_subrasante=43.10, cota_rasante=43.25))
    assert pasos[0].motivo.endswith("no se le evaluo nada antes")
    sin_cabida = pasos[0].sin_cabida
    assert sin_cabida.delta_rasante_m is None
    assert "no lo deja como geometria pura" in sin_cabida.nota
    assert "gobierna la condicion de resguardo" in sin_cabida.nota


def test_sin_delta_si_el_tamizado_de_7A_no_se_puede_calcular(monkeypatch):
    """
    El tamizado lee criterios que V7 no lee (la cobertura minima y la
    condicion de pavimento). Si alguno falta, no hay delta y la nota dice
    cual; el descarte por rasante, que es geometria, se sostiene igual.
    """
    from src.modelos import CriterioPendienteError
    from src.modulos import M7_geometria as M7

    def sin_criterio(**kw):
        raise CriterioPendienteError("condicion_pavimento")

    monkeypatch.setattr(M7, "tamizado_rasante", sin_criterio)
    (resultado, motivo), pasos = _recorrer(
        _concreto(), _GeometriaReal(lambda m, D: D > 1.70))
    sin_cabida = pasos[-1].sin_cabida
    assert resultado is None and MD.MENSAJE_SIN_CABIDA in motivo
    assert sin_cabida.delta_rasante_m is None
    assert "el tamizado de 7.A no se pudo calcular" in sin_cabida.nota
    assert "CriterioPendienteError" in sin_cabida.nota
    assert "condicion_pavimento" in sin_cabida.nota


def test_sin_hidraulica_resuelta_no_se_reconoce_como_descarte_por_rasante():
    """
    La excepcion de la clave que no cabe la levanta la Fase 5, con M3 y M4
    ya resueltos. Sin resultado hidraulico no es ese caso, aunque el campo y
    la geometria coincidan: no hay HW con que pedir el tamizado.
    """
    from src.modelos import SeccionCircular
    exc = DatoInvalidoError("cota_subrasante", valor=44.05, motivo="x")
    assert MD._escalon_sin_cabida(_punto(), _concreto(), SeccionCircular(1.80),
                                  exc, (), None) is None


def test_sin_delta_cuando_el_escalon_que_no_cabe_incumple_lo_evaluado():
    (_, motivo), pasos = _recorrer(
        _concreto(), _GeometriaReal(lambda m, D: False))
    sin_cabida = pasos[-1].sin_cabida
    assert sin_cabida.delta_rasante_m is None
    assert "No se da delta de rasante" in sin_cabida.nota
    assert "incumple V1" in sin_cabida.nota
    assert sin_cabida.nota in motivo


def test_el_delta_con_fondo_de_entrada_medido_no_es_provisional():
    medido = _punto(cota_fondo_entrada=42.10)
    _, pasos = _recorrer(_concreto(), _GeometriaReal(lambda m, D: D > 1.70),
                         medido)
    sin_cabida = pasos[-1].sin_cabida
    assert sin_cabida.delta_rasante_m == pytest.approx(
        DELTA_CONCRETO_180, abs=ABS_MM)
    assert "PROVISIONAL" not in sin_cabida.nota


def _punto_de_canal(Q):
    """
    C-01 del fixture con la subrasante ENRASADA en la clave del primer marco
    (1.20 x 0.90 m, pared 0.20 m): clave = 36.90 + 0.90 + 0.20 = 38.00 msnm.
    """
    return _punto(id="C-01", familia=Familia.C, Q_m3s=Q, S_cauce=0.004,
                  cota_terreno=36.90, cota_rasante=38.15,
                  cota_subrasante=38.00, cbr_subrasante=6.5,
                  esviaje_grados=30.0, cota_fondo_receptor=36.20,
                  sucs_fundacion="ML")


@pytest.mark.parametrize("Q, rotulo", [
    # HW chico: entrada + HW + resguardo (0.80 m, CBR 6.5) + e_paq no pasa de
    # la rasante, y la losa enrasa: 7.A no pide subir nada.
    (0.02, "factible"),
    # HW grande: lo que 7.A pide ya no es geometria, es el resguardo.
    (0.85, "resguardo"),
])
def test_sin_delta_cuando_7A_no_lo_deja_como_geometria_pura(Q, rotulo):
    """
    En un MARCO la cobertura adoptada avisa y no bloquea (T-3, H5): lo
    exigible es la clave bajo la subrasante. Con la losa enrasada el tamizado
    o no pide subir la rasante, o lo pide por el resguardo, que depende del
    HW: en ninguno de los dos casos hay un delta de recubrimiento que dar.
    """
    marco = catalogo(TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.RECTANGULAR)
    (_, motivo), pasos = _recorrer(marco, _GeometriaReal(lambda m, D: True),
                                   _punto_de_canal(Q))
    assert len(pasos) == 1
    sin_cabida = pasos[0].sin_cabida
    assert sin_cabida.exceso_m == pytest.approx(0.0, abs=ABS_MM)
    assert sin_cabida.delta_rasante_m is None
    assert "no lo deja como geometria pura" in sin_cabida.nota
    assert rotulo in sin_cabida.nota
    assert "Es el primer escalon del catalogo" in motivo


def test_el_punto_sale_no_factible_por_rasante_con_el_menor_delta():
    """
    Los tres candidatos con la geometria real: el concreto no cabe en Ø 1.80
    (delta 0.3298 m), el TMC en Ø 1.95 (0.31981 m) y al HDPE le falta la
    pared de 1.35 m. El punto lleva el MENOR de los deltas, y dice de quien.
    """
    pasos = []

    def solo_el_que_no_cabe(material, D):
        # Cumple justo el escalon que no cabe: Ø 1.80 en concreto y Ø 1.95
        # en TMC (cuya pared delgada deja caber al de 1.80: 43.915 msnm).
        return D > (1.85 if material.tipo is TipoMaterial.TMC else 1.70)

    with pytest.raises(DisenoNoFactibleError) as excinfo:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=_GeometriaReal(solo_el_que_no_cabe),
                         registrar=pasos.append)
    exc = excinfo.value
    assert exc.delta_rasante_m == pytest.approx(DELTA_TMC_195, abs=ABS_MM)
    assert "NO FACTIBLE POR RASANTE" in exc.motivo
    assert "2 de 3" in exc.motivo
    assert "0.320 m" in exc.motivo and "TMC galvanizada Ø 1.95 m" in exc.motivo
    assert "0.330 m" in exc.motivo            # el del concreto, en su motivo
    assert "Dato invalido en 'cota_subrasante'" not in exc.motivo
    assert "no evaluable" not in exc.motivo
    assert str(exc).endswith("Subir la rasante 0.32 m")
    sin_cabida = [p for p in pasos if p.sin_cabida is not None]
    assert [(p.material, p.seccion.etiqueta()) for p in sin_cabida] == [
        ("Concreto reforzado", "Ø 1.80 m"), ("TMC galvanizada", "Ø 1.95 m")]


def test_el_punto_sin_delta_lo_dice():
    with pytest.raises(DisenoNoFactibleError) as excinfo:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=_GeometriaReal(lambda m, D: False))
    exc = excinfo.value
    assert exc.delta_rasante_m is None
    assert "NO FACTIBLE POR RASANTE" in exc.motivo
    assert "No se da delta de rasante" in exc.motivo
    assert "Subir la rasante" not in str(exc)


def test_un_material_que_cierra_no_cambia_porque_otro_no_quepa():
    """
    El concreto no cierra en ningun escalon y no cabe en Ø 1.80; el TMC
    cumple en el primer escalon que transporta el caudal (Ø 1.20 m: con
    n = 0.030, los de 0.90 y 1.05 no lo llevan en flujo libre y no llegan a
    la Fase 5). El resultado es el de siempre: TMC Ø 1.20 m, sin excepcion,
    y el concreto queda en la traza con sus siete escalones.
    """
    pasos = []
    verificar = _GeometriaReal(lambda m, D: m.tipo is TipoMaterial.TMC)
    resultado = MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                                 verificar=verificar, registrar=pasos.append)
    assert resultado.aceptado
    assert resultado.material.tipo is TipoMaterial.TMC
    assert resultado.seccion.altura == pytest.approx(1.20, rel=REL_TRANSPORTE)
    assert verificar.llamadas == [
        (TipoMaterial.CONCRETO_REFORZADO, etiqueta)
        for etiqueta in _diametros(900, 1800)
    ] + [(TipoMaterial.TMC, "Ø 1.20 m")]
    assert pasos[-1].aceptado and pasos[-1].material == "TMC galvanizada"


def test_el_que_no_cupo_queda_en_la_traza_aunque_otro_cierre():
    pasos = []
    MD.disenar_punto(
        _punto(), L=L_CONDUCTO, TW=TW_LIBRE, registrar=pasos.append,
        verificar=_GeometriaReal(lambda m, D: m.tipo is TipoMaterial.TMC))
    assert [(p.material, p.seccion.etiqueta()) for p in pasos
            if p.sin_cabida is not None] == [("Concreto reforzado", "Ø 1.80 m")]
    assert pasos[-1].sin_cabida is None


# ===========================================================================
# C. El hermano: el dato invalido del punto no es «no factible»
# ===========================================================================

class _DatoInvalido:
    """
    Verificador que levanta un `DatoInvalidoError` de un dato del PUNTO en
    los materiales indicados, con `completadas` evaluadas antes (como hace
    `M5.verificar`), y rechaza los demas.
    """

    def __init__(self, tipos, completadas):
        self.tipos = set(tipos)
        self.completadas = tuple(completadas)

    def __call__(self, *, punto, material, seccion, resultado):
        if material.tipo in self.tipos:
            exc = DatoInvalidoError(
                "Q_evento_extremo_m3s", valor=0.5, id_punto=punto.id,
                motivo=f"es menor que el de diseño (visto en {material.nombre})")
            exc.verificaciones_completadas = self.completadas
            raise exc
        return (_verificacion(False, obtenido="x", admisible="y"),)


TODOS = (TipoMaterial.CONCRETO_REFORZADO, TipoMaterial.TMC, TipoMaterial.HDPE)


def test_el_dato_invalido_comun_a_todos_sale_con_su_campo():
    """Aunque cada escalon ya incumpliera algo: a TODOS los detuvo el dato."""
    verificar = _DatoInvalido(TODOS, (_verificacion(False),))
    with pytest.raises(DatoInvalidoError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert exc.value.campo == "Q_evento_extremo_m3s"
    # Sale el PRIMERO, el del candidato mas preferente de M2.
    assert "visto en Concreto reforzado" in str(exc.value)


def test_el_dato_invalido_que_detiene_un_escalon_que_cumple_lo_demas_decide():
    """
    Un solo material se detiene en el dato invalido, sobre un escalon que
    cumple todo lo evaluado; los otros dos se evaluan y no cumplen. El punto
    no es «no factible»: hay un escalon al que solo lo separa de ser aceptado
    un dato que hay que CORREGIR.
    """
    verificar = _DatoInvalido([TipoMaterial.TMC], (_verificacion(True),))
    with pytest.raises(DatoInvalidoError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert exc.value.campo == "Q_evento_extremo_m3s"

    # Con dos decisivos sale el del primero de los dos.
    verificar = _DatoInvalido([TipoMaterial.TMC, TipoMaterial.HDPE],
                              (_verificacion(True),))
    with pytest.raises(DatoInvalidoError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert "visto en TMC galvanizada" in str(exc.value)


def test_el_dato_invalido_sobre_un_escalon_que_ya_incumple_no_decide():
    """
    La otra mitad, que no cambia (es la de la ficha T4-10 para el dato que
    falta): un material se detiene en un dato invalido sobre un escalon que
    YA incumplia, y los demas se evaluan y no cumplen. Sigue siendo «no
    factible», con el material citado como no evaluable.
    """
    verificar = _DatoInvalido([TipoMaterial.TMC], (_verificacion(False),))
    with pytest.raises(DisenoNoFactibleError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=verificar)
    assert "TMC galvanizada: material no evaluable" in exc.value.motivo
    assert exc.value.delta_rasante_m is None


def test_el_dato_invalido_de_antes_de_la_Fase_5_sigue_como_hasta_hoy():
    """
    Lo que la correccion deja FUERA, fijado: un `DatoInvalidoError` que no
    trae `verificaciones_completadas` --el que M3 o M4 levantan antes de la
    Fase 5, como el diametro de arranque negativo de la rama de error de la
    linea base-- sigue saliendo «no factible» con el material «no evaluable»,
    aunque detenga a los tres candidatos.
    """
    def de_M3(*, punto, material, seccion, resultado):
        raise DatoInvalidoError("D", valor=-0.9,
                                motivo="el diametro debe ser positivo")

    with pytest.raises(DisenoNoFactibleError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE, verificar=de_M3)
    assert exc.value.motivo.count("material no evaluable") == len(TODOS)
    assert exc.value.delta_rasante_m is None


def test_un_material_que_cierra_no_cambia_porque_otro_tenga_un_dato_invalido():
    """El resultado aceptado no se toca (encargo de T11-03)."""
    def verificar(*, punto, material, seccion, resultado):
        if material.tipo is TipoMaterial.CONCRETO_REFORZADO:
            exc = DatoInvalidoError("Q_evento_extremo_m3s", valor=0.5,
                                    motivo="es menor que el de diseño")
            exc.verificaciones_completadas = (_verificacion(True),)
            raise exc
        return (_verificacion(True),)

    resultado = MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                                 verificar=verificar)
    assert resultado.aceptado and resultado.material.tipo is TipoMaterial.TMC


def test_el_caudal_extremo_menor_que_el_de_diseno_es_un_dato_invalido():
    """
    El caso del auditor, por el servicio: con el juego de validacion y
    `Q_evento_extremo_m3s` = 0.5 m3/s en A-01 (su caudal de diseño es
    1.167), V8 levanta el dato invalido en los tres materiales. El informe
    decia «no existe diseño» con `campo: None`.
    """
    informe = V.correr_juego(V.aplicar(
        V.juego_completo(),
        (("externo", "A-01", "Q_evento_extremo_m3s", 0.5),)))
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert not a01.dimensionado
    tipos = {b.tipo for b in a01.bloqueos}
    assert TipoDeBloqueo.DISENO_NO_FACTIBLE not in tipos
    b = next(b for b in a01.bloqueos
             if b.tipo is TipoDeBloqueo.DATO_INVALIDO)
    assert b.campo == "Q_evento_extremo_m3s"
    assert b.etapa == servicio.ETAPA_BUCLE_DE_MD
    # Los demas puntos, como en el juego completo: dimensionados.
    for p in informe.puntos:
        if p.punto.id != "A-01":
            assert p.dimensionado, p.punto.id


# ===========================================================================
# Por el servicio: las corridas de la linea base
# ===========================================================================

@pytest.fixture(scope="module")
def estrecha():
    """La corrida ESTRECHA de la linea base: perfil, luz 2.75, sin TW."""
    return _correr_con_los_valores_del_archivo(None)


@pytest.fixture(scope="module")
def ancha():
    """La corrida ANCHA de la linea base: B-01 con TW = 1.00 m."""
    return _correr_con_los_valores_del_archivo(ENTRADAS_AMPLIADAS)


def _no_factible(informe, id_punto):
    punto = next(p for p in informe.puntos if p.punto.id == id_punto)
    assert not punto.dimensionado
    return punto, next(b for b in punto.bloqueos
                       if b.tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE)


# Los escalones de A-01 en la corrida estrecha, con lo que cada uno incumple:
# LOS MISMOS que la linea base traia antes de la correccion (leidos de
# `informe.traza` sobre `c774035`). Lo unico que cambia es el texto del
# motivo de los dos que no caben.
ITERACIONES_A01_ESTRECHA = [
    ("Concreto reforzado", "Ø 0.90 m", ["V1", "V4"]),
    ("Concreto reforzado", "Ø 1.05 m", ["V1", "V4"]),
    ("Concreto reforzado", "Ø 1.20 m", ["V1", "V7"]),
    ("Concreto reforzado", "Ø 1.35 m", ["V1", "V7"]),
    ("Concreto reforzado", "Ø 1.50 m", ["V7"]),
    ("Concreto reforzado", "Ø 1.65 m", ["V7"]),
    ("Concreto reforzado", "Ø 1.80 m", []),
    ("TMC galvanizada", "Ø 0.90 m", []),
    ("TMC galvanizada", "Ø 1.05 m", []),
    ("TMC galvanizada", "Ø 1.20 m", ["V1", "V4"]),
    ("TMC galvanizada", "Ø 1.35 m", ["V1", "V7"]),
    ("TMC galvanizada", "Ø 1.50 m", ["V7"]),
    ("TMC galvanizada", "Ø 1.65 m", ["V7"]),
    ("TMC galvanizada", "Ø 1.80 m", ["V7"]),
    ("TMC galvanizada", "Ø 1.95 m", []),
    ("HDPE", "Ø 0.90 m", ["V1", "V4", "V4b"]),
    ("HDPE", "Ø 1.05 m", ["V1", "V4"]),
    ("HDPE", "Ø 1.20 m", ["V1", "V7"]),
    ("HDPE", "Ø 1.35 m", ["V1"]),
]


def test_A01_sin_TW_es_no_factible_por_rasante_con_su_delta(estrecha):
    punto, b = _no_factible(estrecha, "A-01")
    assert b.campo is None
    assert "NO FACTIBLE POR RASANTE" in b.mensaje
    assert "Dato invalido en 'cota_subrasante'" not in b.mensaje
    assert "material no evaluable" not in b.mensaje
    assert b.delta_rasante_m == pytest.approx(DELTA_TMC_195, abs=ABS_MM)
    # Los dos escalones que no caben, con su clave.
    assert "Ø 1.80 m no cabe bajo la subrasante" in b.mensaje
    assert "44.075" in b.mensaje and "44.065" in b.mensaje
    # El motivo del escalon anterior de cada material: V7.
    assert "Ø 1.65 m: incumple V7" in b.mensaje
    assert "Ø 1.80 m: incumple V7" in b.mensaje
    # Y el volcado lleva el numero donde llevaba `null`.
    volcado = cli.informe_json(estrecha)
    a01 = next(p for p in volcado["puntos"] if p["id"] == "A-01")
    fila = next(x for x in a01["bloqueos"]
                if x["tipo"] == TipoDeBloqueo.DISENO_NO_FACTIBLE.value)
    assert fila["delta_rasante_m"] == pytest.approx(DELTA_TMC_195, abs=ABS_MM)


def test_las_iteraciones_de_A01_son_las_de_siempre(estrecha):
    punto = next(p for p in estrecha.puntos if p.punto.id == "A-01")
    assert [(p.material, p.seccion.etiqueta(),
             [v.codigo for v in p.incumplidas]) for p in punto.traza
            ] == ITERACIONES_A01_ESTRECHA
    assert not any(p.aceptado for p in punto.traza)


def test_los_dos_escalones_que_no_caben_de_A01_llevan_su_marca(estrecha):
    punto = next(p for p in estrecha.puntos if p.punto.id == "A-01")
    sin_cabida = [(p.material, p.seccion.etiqueta())
                  for p in punto.traza if p.sin_cabida is not None]
    assert sin_cabida == [("Concreto reforzado", "Ø 1.80 m"),
                          ("TMC galvanizada", "Ø 1.95 m")]
    for p in punto.traza:
        if p.sin_cabida is not None:
            assert MD.MARCA_ESCALON_SIN_CABIDA in p.motivo
            assert "DatoInvalidoError" not in p.motivo


@pytest.mark.parametrize("id_punto", ["A-02", "B-01"])
def test_sin_TW_los_puntos_cuyo_escalon_incumple_V2_no_llevan_delta(
        estrecha, id_punto):
    """
    En A-02 y B-01 el escalon que no cabe incumple ademas V2 (la velocidad
    minima cae al crecer el tubo): subir la rasante hasta darle cabida no lo
    haria cumplir, y no se da delta.
    """
    _, b = _no_factible(estrecha, id_punto)
    assert "NO FACTIBLE POR RASANTE" in b.mensaje
    assert "Dato invalido en 'cota_subrasante'" not in b.mensaje
    assert b.delta_rasante_m is None
    assert "No se da delta de rasante" in b.mensaje
    assert "incumple V2" in b.mensaje or "incumple V1, V2" in b.mensaje


def test_B01_con_el_TW_de_la_linea_base_nombra_V2(ancha):
    """
    CLAUDE.md (E-A): B-01 con TW = 1.00 m termina en `DisenoNoFactibleError`
    «con motivo V2». El mensaje nombraba un dato invalido de subrasante.
    Clave de Ø 1.95 m de concreto: 38.40 + 1.95 + 0.188 = 40.538 msnm, 0.088 m
    sobre la subrasante (40.45).
    """
    _, b = _no_factible(ancha, "B-01")
    assert "Dato invalido" not in b.mensaje
    assert "material no evaluable" not in b.mensaje
    assert "Ø 1.80 m: incumple V2" in b.mensaje          # el escalon anterior
    assert "Ø 1.95 m no cabe bajo la subrasante" in b.mensaje
    assert "40.538" in b.mensaje and "+0.088" in b.mensaje
    assert b.delta_rasante_m is None
    # A-01 y A-02 siguen dimensionados, en su seccion de siempre.
    for id_punto in ("A-01", "A-02"):
        p = next(x for x in ancha.puntos if x.punto.id == id_punto)
        assert p.dimensionado
        assert p.resultado.seccion.altura == pytest.approx(
            0.90, rel=REL_TRANSPORTE)
