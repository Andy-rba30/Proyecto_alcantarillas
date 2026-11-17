"""
tests/test_ve3_dimensionamiento_cabezal.py
==========================================
VE-3.5 (decision del dueño del 2026-11-17): el programa DIMENSIONA la
zapata del cabezal en vez de solo verificar la geometria de la regla de
T-7a, que no pasa la estabilidad LRFD en ningun punto de la validacion
integral (ficha T7B-09).

Que se fija aqui:

1. Con el paso y el tope declarados (DATOS DE PRUEBA de este archivo, no
   valores de proyecto: el criterio 'dimensionamiento_zapata_cabezal' no
   tiene valor de archivo), A-01 sale con dos cabezales cuya estabilidad
   (E1 a E3 de los dos marcos, estatica y sismica) cumple, la zapata crece
   por el TALON (la punta queda en la de la regla) y la dimension lleva el
   origen «dimensionada por estabilidad».
2. Sin el criterio declarado el dimensionamiento se detiene con su
   `CriterioPendienteError` (bloqueo del punto) y la geometria de la regla
   se sigue verificando como hasta VE-3.5.
3. Un ancho DECLARADO gana y no se itera, cumpla o no.
4. Con un tope pequeño la zapata se queda en el mayor ancho de la grilla
   que no pasa el tope, las filas que no cumplen siguen sin cumplir y un
   aviso lo dice.
5. Monotonia: con mas empuje (angulo de friccion del relleno menor, dentro
   de su ventana) la zapata dimensionada no es menor.
6. El armado se hace con la geometria FINAL.

Medido antes de escribir (rama `61a4dcc`, juego de T-11, talon creciendo
con la punta de la regla): la entrada de A-01 cumple con B = 2.40 m y la
salida con 3.20 m; con 2.00 m la entrada aun incumple E3-LRFD estatico.

SE ESCRIBIO EN ROJO PRIMERO, contra 61a4dcc.
"""

from __future__ import annotations

import pytest

from src import servicio
from src.modelos import ORIGEN_DIMENSION_REGLA, TipoDeBloqueo
from src.modulos import M9_cabezal as M9
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import ABS_CERO

CRITERIO = "dimensionamiento_zapata_cabezal"
# Un paso de 0.10 m y un tope de 1.5·H_c. Hasta VE-3.9 eran DATOS DE PRUEBA
# que el juego declaraba; desde VE-3.9 son el VALOR DE ARCHIVO del criterio
# (decision del dueño del 2026-11-17) y el juego ya no los declara.
PRUEBA = {"paso_m": 0.10, "fraccion_ancho_max": 1.5}
ABS_MM = 5e-7   # sumas exactas de datos con tres decimales


def _correr(*cambios):
    return V.correr_juego(V.aplicar(V.juego_completo(), list(cambios)))


def _punto(informe, id_punto="A-01"):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def _dim(g, nombre):
    return next(d for d in g.dimensiones if d.nombre == nombre)


def _estabilidad_cumple(cabezal, extremo):
    ests = [e for e in cabezal.estabilidad if e.extremo == extremo]
    return bool(ests) and all(e.cumple for e in ests)


# Desde VE-3.9 el criterio tiene valor de archivo: «declarar None» ya no lo
# vacia. El juego lo deja SIN VALOR, archivo incluido (`sin_valor`).
SIN_EL_CRITERIO = ("sin_valor", CRITERIO)


def test_el_paso_y_el_tope_son_el_valor_de_archivo_y_el_juego_no_los_declara():
    """
    CAMBIADO EN VE-3.9 (decision del dueño): se llamaba «el juego declara el
    criterio con los datos de prueba»; hoy los datos son el valor de archivo
    y el juego no los repite.
    """
    from src import criterios_adoptados as ca
    from tests.fixtures import juego_validacion_integral as J
    assert ca.CRITERIOS[CRITERIO].valor == PRUEBA
    assert CRITERIO not in J.DECLARACIONES


@pytest.fixture(scope="module")
def dimensionado():
    return _correr()


@pytest.fixture(scope="module")
def sin_criterio():
    return _correr(SIN_EL_CRITERIO)


def test_A01_dimensiona_una_zapata_que_cumple_la_estabilidad(dimensionado):
    cab = _punto(dimensionado).cabezal
    for g in cab.geometrias:
        assert _estabilidad_cumple(cab, g.extremo), g.extremo
        assert len([e for e in cab.estabilidad
                    if e.extremo == g.extremo]) == len(
            M9.CONDICIONES_DE_ESTABILIDAD)


def test_la_zapata_crece_por_el_talon_con_su_origen(dimensionado,
                                                    sin_criterio):
    regla = {g.extremo: g for g in _punto(sin_criterio).cabezal.geometrias}
    for g in _punto(dimensionado).cabezal.geometrias:
        r = regla[g.extremo]
        assert g.B > r.B
        assert g.ancho_punta == pytest.approx(r.ancho_punta, abs=ABS_CERO)
        assert g.ancho_talon > r.ancho_talon
        assert _dim(g, "ancho de la zapata (B)").origen == \
            M9.ORIGEN_DIMENSION_ESTABILIDAD
        assert _dim(g, "ancho del talon").origen == \
            M9.ORIGEN_DIMENSION_ESTABILIDAD


def test_es_el_menor_ancho_de_la_grilla_que_cumple(dimensionado,
                                                   sin_criterio):
    """El intento anterior al aceptado NO cumplia: la zapata es la minima."""
    cab = _punto(dimensionado).cabezal
    regla = {g.extremo: g.B for g in _punto(sin_criterio).cabezal.geometrias}
    pantalla_regla = {g.extremo: g.espesor_base_muro
                      for g in _punto(sin_criterio).cabezal.geometrias}
    for g in cab.geometrias:
        # CAMBIADO DECLARANDOLO (VE-3.14, H-12): los intentos de la
        # re-optimizacion del ancho tras el peralte van al final de la traza
        # y se miran aparte (tests/test_ve3_14_cabezal.py); aqui, la grilla
        # creciente del dimensionamiento por estabilidad.
        intentos = [i for i in cab.intentos_de_zapata
                    if i.extremo == g.extremo and not i.reoptimizado]
        assert intentos[0].B == pytest.approx(regla[g.extremo],
                                              abs=ABS_CERO)
        assert not intentos[0].cumple
        assert intentos[-1].cumple
        # CAMBIADO DECLARANDOLO (VE-3.14, H-1): si la pantalla crecio por
        # su armado, la zapata crecio lo mismo (punta y talon fijos).
        crecio = g.espesor_base_muro - pantalla_regla[g.extremo]
        assert intentos[-1].B == pytest.approx(g.B - crecio, abs=ABS_CERO)
        assert all(not i.cumple for i in intentos[:-1])
        assert len(intentos) >= 2


def test_la_memoria_explica_el_dimensionamiento(dimensionado):
    cab = _punto(dimensionado).cabezal
    pasos = [p for p in cab.pasos if p.fundamento_id == "F9.DIMENSIONADO"]
    assert {p.codigo for p in pasos} == {"9.3.d.e", "9.3.d.s"}
    for p in pasos:
        assert p.por_que
        assert CRITERIO in " ".join(m.procedencia for m in p.sustitucion)


def test_sin_el_criterio_se_detiene_y_verifica_la_regla(sin_criterio):
    a01 = _punto(sin_criterio)
    pendientes = [b for b in a01.bloqueos
                  if b.tipo is TipoDeBloqueo.CRITERIO_PENDIENTE
                  and b.criterio == CRITERIO]
    assert len(pendientes) == 1
    assert pendientes[0].etapa == servicio.ETAPA_DIMENSIONAMIENTO_CABEZAL
    cab = a01.cabezal
    for g in cab.geometrias:
        assert _dim(g, "ancho de la zapata (B)").origen == \
            ORIGEN_DIMENSION_REGLA
        assert not _estabilidad_cumple(cab, g.extremo)
    assert cab.intentos_de_zapata == ()


def test_el_ancho_declarado_gana_y_no_se_itera():
    """
    Declarada una zapata que NO cumple en los dos extremos (1.80 m), no se
    itera aunque el criterio este declarado: el criterio ni se lee.
    """
    informe = _correr(("externo", "A-01", "cabezal_declarado",
                       {"ancho_zapata_m": 1.80}))
    cab = _punto(informe).cabezal
    for g in cab.geometrias:
        assert g.B == pytest.approx(1.80, abs=ABS_CERO)
        assert _dim(g, "ancho de la zapata (B)").origen == "declarada"
    assert cab.intentos_de_zapata == ()
    assert not all(_estabilidad_cumple(cab, g.extremo)
                   for g in cab.geometrias)


def test_con_un_tope_pequeno_no_cumple_y_lo_dice():
    """
    Tope de 0.80·H_c: la entrada de A-01 (H_c = 2.25 m) necesita 2.075 m y
    el tope la deja en el mayor ancho de la grilla que no lo pasa, 1.775 m
    (1.575 + 2·0.10, porque 1.875 > 1.80). Desde VE-3.9 0.80 queda FUERA de
    la ventana del criterio (1.0 a 2.0·H_c) y la puerta lo rechazaria: se
    impone con `con_valor`, que lo dice, porque lo que se prueba es el
    comportamiento AL TOPE, que dentro de la ventana no se alcanza.
    """
    from tests.apoyo.criterios import con_valor
    with con_valor(CRITERIO, {"paso_m": 0.10, "fraccion_ancho_max": 0.80},
                   motivo="tope bajo la ventana a proposito: la zapata "
                          "tiene que llegar al tope para probar el aviso"):
        informe = _correr()
    cab = _punto(informe).cabezal
    entrada = cab.entrada
    assert entrada.B == pytest.approx(1.775, abs=ABS_MM)
    assert entrada.B <= 0.80 * (entrada.H + entrada.espesor_zapata)
    assert not _estabilidad_cumple(cab, "entrada")
    assert any("tope" in a and "entrada" in a for a in cab.avisos)



def test_mas_empuje_no_da_una_zapata_menor(dimensionado):
    """Con phi del relleno 30 grados (ventana 30-38) en vez de 34."""
    informe = _correr(("declarar", "phi_relleno_trasdos", 30.0))
    base = {g.extremo: g.B for g in _punto(dimensionado).cabezal.geometrias}
    for g in _punto(informe).cabezal.geometrias:
        assert g.B >= base[g.extremo] - ABS_MM


def test_el_armado_usa_la_geometria_final(monkeypatch):
    vistos = {}
    original = servicio._fase_9_armado

    def espia(informe, entornos):
        if informe.punto.id == "A-01":
            vistos.update({e.extremo: e.geometria.B for e in entornos})
            vistos["final"] = {g.extremo: g.B
                               for g in informe.cabezal.geometrias}
        return original(informe, entornos)

    monkeypatch.setattr(servicio, "_fase_9_armado", espia)
    _correr()
    final = vistos.pop("final")
    assert vistos == pytest.approx(final, abs=ABS_CERO)
    assert final["entrada"] > 1.575 + ABS_MM


def test_extremos_a_dimensionar_son_los_que_no_cumplen_y_no_se_declararon(
        sin_criterio):
    cab = _punto(sin_criterio).cabezal
    assert M9.extremos_a_dimensionar(cab, cab.estabilidad) == (
        "entrada", "salida")
    assert M9.extremos_a_dimensionar(
        cab, cab.estabilidad,
        {"entrada": {"ancho_zapata_m": 2.0}}) == ("salida",)
    # Sin ninguna condicion evaluada no hay nada que dimensionar.
    assert M9.extremos_a_dimensionar(cab, ()) == ()


def test_si_todo_cumple_no_se_dimensiona_ni_se_lee_el_criterio(dimensionado):
    """
    Con la geometria que ya cumple y el criterio SIN valor: devuelve None y
    no levanta `CriterioPendienteError` (el criterio ni se lee). Desde VE-3.9
    el criterio tiene valor de archivo y se vacia aqui con `sin_valor`.
    """
    from tests.apoyo.criterios import sin_valor
    p = _punto(dimensionado)
    with sin_valor(CRITERIO):
        assert M9.dimensionar_zapata_por_estabilidad(
            punto=p.punto_de_calculo, resultado=p.resultado,
            geometria=p.geometria, embocadura=p.embocadura,
            cabezal=p.cabezal, estabilidades=p.cabezal.estabilidad) is None


def test_incorporar_dimensionado_suma_intentos_pasos_y_avisos(sin_criterio):
    from src.modelos import IntentoDeZapata
    cab = _punto(sin_criterio).cabezal
    intento = IntentoDeZapata(extremo="entrada", B=2.0,
                              condiciones=("estatico",), incumplidas=())
    d = M9.DimensionadoDeZapatas(cabezal=cab, anchos={"entrada": 2.0},
                                 intentos=(intento,), pasos=(),
                                 avisos=("aviso de prueba",))
    nuevo = M9.incorporar_dimensionado(cab, d)
    assert nuevo.intentos_de_zapata == (intento,)
    assert nuevo.avisos[-1] == "aviso de prueba"
    assert nuevo.pasos == cab.pasos
    assert intento.cumple
