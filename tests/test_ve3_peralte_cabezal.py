"""
tests/test_ve3_peralte_cabezal.py
=================================
VE-3.9 (decisiones del dueño del 2026-11-17): el paso y el tope del
dimensionamiento de la zapata del cabezal son VALOR DE ARCHIVO (0.10 m y
1.5·H_c), y el PERALTE de la zapata tambien se dimensiona: con el talon que
la estabilidad ensancha (VE-3.5), el peralte de la regla no alcanzaba para
armar la zapata (A1/A2 del talon de la salida de A-01 en el juego de T-11).

Que se fija aqui:

1. Con los valores de archivo y SIN declarar nada, A-01 del juego sale con
   las dos filas de estabilidad y TODAS las del armado de la zapata (punta y
   talon: A1 a A4 y A6; A8 de la zapata) cumpliendo en los dos cabezales.
2. El peralte crece SOLO si hace falta: la entrada de A-01 conserva el de la
   regla; la salida crece por pasos de 0.10 m, con su origen «dimensionada
   por armado», y el intento anterior al adoptado no cumplia.
3. Entre 16 in y el peralte cuyo vuelo queda bajo 3·d_v el cortante cae
   fuera de AASHTO 5.7.3.4.1 y el programa no lo puede VERIFICAR (no
   implementa el general de 5.7.3.4.2): esos intentos se marcan y el
   dimensionamiento sigue al primero verificable (conservador).
4. Lo declarado gana y no se itera.
5. Monotonia: con mas empuje el peralte y el ancho no son menores.
6. La estabilidad se RE-VERIFICA con cada peralte: el dimensionamiento del
   ancho se vuelve a llamar con los peraltes nuevos y su resultado se usa.
7. El bucle termina: con un armado que nunca cumple, el peralte se detiene
   en el limite fisico (H_c) con su marca de tope, en a lo sumo
   ceil(H_c / paso) intentos.

Medido antes de escribir (rama 6a87006 con el criterio declarado como dato
de prueba): la salida de A-01 incumplia A1 y A2 del talon con 0.404 m; con
0.504, 0.604 y 0.704 m el cortante queda fuera de 5.7.3.4.1; con 0.804 m
cumple. La entrada cumple con el de la regla.

SE ESCRIBIO EN ROJO PRIMERO, contra 6a87006: sin valor de archivo del
criterio y sin el peralte dimensionado, fallan 1, 2, 3, 5, 6 y 7.
"""

from __future__ import annotations

import math

import pytest

from src import servicio
from src.modelos import ORIGEN_DIMENSION_DECLARADA, ORIGEN_DIMENSION_REGLA
from src.modulos import M9_cabezal as M9
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import ABS_CERO

PASO = 0.10
ABS_MM = 5e-7   # sumas exactas de datos con tres decimales
FILAS_DE_LA_ZAPATA = ("A1", "A2", "A3", "A4", "A6", "A8")


def _correr(*cambios):
    return V.correr_juego(V.aplicar(V.juego_completo(), list(cambios)))


def _punto(informe, id_punto="A-01"):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def _dim(g, nombre):
    return next(d for d in g.dimensiones if d.nombre == nombre)


def _de_la_zapata(codigo):
    partes = (codigo or "").split(".")
    return (partes[0] in FILAS_DE_LA_ZAPATA and len(partes) > 1
            and partes[1] in ("punta", "talon", "zapata"))


@pytest.fixture(scope="module")
def juego():
    return _correr()


def test_A01_cumple_la_estabilidad_y_el_armado_de_la_zapata(juego):
    cab = _punto(juego).cabezal
    assert len(cab.estabilidad) == 2 * len(M9.CONDICIONES_DE_ESTABILIDAD)
    assert all(e.cumple for e in cab.estabilidad)
    assert {a.extremo for a in cab.armado} == {"entrada", "salida"}
    zapata = [v for a in cab.armado for v in a.verificaciones
              if _de_la_zapata(v.codigo)]
    assert zapata, "el armado de la zapata no se evaluo"
    assert all(v.cumple for v in zapata), [
        v.codigo for v in zapata if not v.cumple]
    # Ningun bloqueo del armado de la zapata.
    assert not [b for b in _punto(juego).bloqueos
                if "zapata" in b.etapa and "armado" in b.etapa]


def test_el_peralte_crece_solo_donde_hace_falta(juego):
    cab = _punto(juego).cabezal
    entrada, salida = cab.entrada, cab.salida
    assert _dim(entrada, "espesor de la zapata").origen != \
        M9.ORIGEN_DIMENSION_ARMADO
    assert [i for i in cab.intentos_de_peralte
            if i.extremo == "entrada"] == []
    assert _dim(salida, "espesor de la zapata").origen == \
        M9.ORIGEN_DIMENSION_ARMADO
    intentos = [i for i in cab.intentos_de_peralte if i.extremo == "salida"]
    assert len(intentos) >= 2
    assert not intentos[0].cumple
    assert all(not i.cumple for i in intentos[:-1])
    assert intentos[-1].cumple
    assert intentos[-1].espesor_zapata == pytest.approx(
        salida.espesor_zapata, abs=ABS_CERO)
    for antes, despues in zip(intentos, intentos[1:]):
        assert despues.espesor_zapata - antes.espesor_zapata == \
            pytest.approx(PASO, abs=ABS_MM)
    # La altura total no cambia (la fijan las cotas): crece la zapata y la
    # pantalla sobre ella se acorta lo mismo.
    regla = _punto(_correr(("sin_valor", "dimensionamiento_zapata_cabezal")))
    assert salida.H + salida.espesor_zapata == pytest.approx(
        regla.cabezal.salida.H + regla.cabezal.salida.espesor_zapata,
        abs=ABS_MM)
    assert salida.H < regla.cabezal.salida.H


def test_los_peraltes_que_5734_1_no_cubre_se_marcan_y_se_saltan(juego):
    cab = _punto(juego).cabezal
    intentos = [i for i in cab.intentos_de_peralte if i.extremo == "salida"]
    marcados = [i for i in intentos
                if i.incumplidas == (M9.CORTANTE_NO_VERIFICABLE,)]
    assert marcados, "ningun intento cayo fuera de 5.7.3.4.1"
    # Todos los marcados tienen 16 in o mas.
    assert all(i.espesor_zapata >= 0.4064 - ABS_MM for i in marcados)
    assert intentos[-1].cumple


def test_la_memoria_explica_el_peralte(juego):
    cab = _punto(juego).cabezal
    pasos = [p for p in cab.pasos
             if p.fundamento_id == "F9.DIMENSIONADO_PERALTE"]
    assert [p.codigo for p in pasos] == ["9.3.p.s"]
    p = pasos[0]
    assert p.por_que
    assert "dimensionamiento_zapata_cabezal" in " ".join(
        m.procedencia for m in p.sustitucion)
    assert p.resultado.valor == pytest.approx(cab.salida.espesor_zapata,
                                              abs=ABS_CERO)
    assert "5.7.3.4.1" in p.nota_del_proyecto


def test_el_peralte_declarado_gana_y_no_se_itera():
    informe = _correr(("externo", "A-01", "cabezal_declarado",
                       {"espesor_zapata_m": 0.45}))
    cab = _punto(informe).cabezal
    for g in cab.geometrias:
        assert g.espesor_zapata == pytest.approx(0.45, abs=ABS_CERO)
        assert _dim(g, "espesor de la zapata").origen == \
            ORIGEN_DIMENSION_DECLARADA
    assert cab.intentos_de_peralte == ()


def test_mas_empuje_no_da_un_peralte_ni_un_ancho_menor(juego):
    """Con phi del relleno 30 grados (ventana 30-38) en vez de 34."""
    informe = _correr(("declarar", "phi_relleno_trasdos", 30.0))
    base = {g.extremo: g for g in _punto(juego).cabezal.geometrias}
    for g in _punto(informe).cabezal.geometrias:
        assert g.espesor_zapata >= base[g.extremo].espesor_zapata - ABS_MM
        assert g.B >= base[g.extremo].B - ABS_MM


def test_la_estabilidad_se_reverifica_con_cada_peralte(monkeypatch):
    """
    Con cada peralte nuevo, `dimensionar_peralte_por_armado` vuelve a llamar
    al dimensionamiento del ancho con los peraltes que el armado hizo
    crecer, y lo que este devuelve se usa.
    """
    llamadas = []
    original = M9.dimensionar_zapata_por_estabilidad

    def espia(**kw):
        resultado = original(**kw)
        if kw.get("espesores_por_armado"):
            llamadas.append(dict(kw["espesores_por_armado"]))
        return resultado

    monkeypatch.setattr(M9, "dimensionar_zapata_por_estabilidad", espia)
    informe = _correr()
    salida = _punto(informe).cabezal.salida
    a01 = [d for d in llamadas if "salida" in d]
    assert a01, "la estabilidad no se re-verifico con el peralte nuevo"
    assert max(d["salida"] for d in a01) == pytest.approx(
        salida.espesor_zapata, abs=ABS_CERO)


def test_el_bucle_termina_en_el_limite_fisico(monkeypatch, juego):
    """
    Con un armado que nunca cumple, el peralte crece hasta el limite fisico
    (la zapata tiene que dejar pantalla: e_z < H_c) y se detiene con la
    marca de tope.
    """
    p = _punto(juego)
    monkeypatch.setattr(M9, "incumplidas_del_armado_de_la_zapata",
                        lambda entorno: ("A1.talon.x",))
    regla = _punto(_correr(("sin_valor", "dimensionamiento_zapata_cabezal")))
    d = M9.dimensionar_peralte_por_armado(
        punto=p.punto_de_calculo, resultado=p.resultado,
        geometria=p.geometria, embocadura=p.embocadura,
        cabezal=regla.cabezal, socavacion=p.socavacion)
    assert d is not None
    for g in regla.cabezal.geometrias:
        intentos = [i for i in d.intentos if i.extremo == g.extremo]
        H_c = g.H + g.espesor_zapata
        assert intentos[-1].al_tope
        assert intentos[-1].espesor_zapata < H_c
        assert len(intentos) <= math.ceil(H_c / PASO) + 1
    assert any("crecio hasta" in a for a in d.avisos)


def test_sin_el_criterio_no_se_dimensiona_ni_el_ancho_ni_el_peralte():
    a01 = _punto(_correr(("sin_valor", "dimensionamiento_zapata_cabezal")))
    pendientes = [b for b in a01.bloqueos
                  if b.criterio == "dimensionamiento_zapata_cabezal"]
    assert len(pendientes) == 1
    assert pendientes[0].etapa == servicio.ETAPA_DIMENSIONAMIENTO_CABEZAL
    for g in a01.cabezal.geometrias:
        assert _dim(g, "espesor de la zapata").origen in (
            ORIGEN_DIMENSION_REGLA,)
    assert a01.cabezal.intentos_de_peralte == ()
