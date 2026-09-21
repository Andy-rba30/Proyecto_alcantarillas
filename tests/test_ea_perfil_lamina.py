"""
tests/test_ea_perfil_lamina.py
==============================
ACEPTACION DE E-A: el perfil de la lamina de agua por PASO DIRECTO (HDS-5
3.a ed., pag. impresa 3.12 / PDF 94 con la Ec. 3.7; umbrales de la pag. 3.24 /
PDF 106; Section 3.5.1, PDF 118-120), que cierra NOR-HDS-05 entera.

Se escribieron primero EN ROJO (`xfail(strict=True)`, marcador `rojo`) con la
expectativa de la FUENTE o del invariante, nunca con la salida del codigo como
oraculo, y el marcador se retiro al corregir. Lo que fijan:

  1. El tipo nuevo `modelos.PerfilLamina` (no se amplia `ResultadoHidraulico`
     a ciegas: UN campo, `perfil`).
  2. Los DOS dorados que el conflicto #7 admite sin corrida externa citable:
     el LIMITE DE FLUJO LLENO (TW >= D y la linea de energia llena alcanza la
     entrada: el perfil reproduce la formula cerrada HW = H + h_o - S*L de
     `control_salida`) y el LIMITE DE FLUJO UNIFORME (TW = y_n: el perfil es
     plano y HW = y_n + (1 + ke)*V_n^2/2g). Ninguno es una corrida HY-8: son
     identidades de la propia formula, y por eso valen como dorado.
  3. El BALANCE DE ENERGIA estacion a estacion --E_aguas_arriba + S*dx =
     E_aguas_abajo + Sf_medio*dx-- y la monotonia de M1, M2 y S1.
  4. La primera salida util: la FRACCION DE LONGITUD A SECCION LLENA, que
     vuelve MEDIDA la primera condicion de h_o (pag. 3.24: «can only be used
     if the barrel flows full for most of its length»). Analitica cuando el
     tramo lleno arranca en la salida: x* = (TW - D)/(S - Sf_llena).
  5. La segunda: el HW POR REMANSO bajo HW/D < 0.75, que deshace la
     circularidad: el caso (b) del dictamen (Q = 0.3, S = 0.005, TW = 0) es
     un barril SUPERCRITICO (y_n = 0.2965 < y_c = 0.3157) que la aproximacion
     clasificaba como control de salida; la S1 desde y_c tiene longitud cero,
     el remanso no alcanza la entrada y gobierna la ENTRADA. Con eso V1 y V2
     dejan de estar pendientes bajo control de salida parcialmente lleno.

Los numeros de contraste del prototipo (0.489, 0.391, 1.130, 0.5518, 0.501)
se comparan a la cifra impresa, como los del dictamen en EXT-3: no son dorados.
"""

import ast
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import modelos
from src import criterios_adoptados as ca
from src.constantes_fisicas import G
from src.constantes_normativas import K_FRICCION_SI
from src.modelos import (ControlGobernante, Geometria, Magnitud, RegimenBarril,
                         SeccionCircular, SeccionRectangular, TipoDeVeredicto)
from src.modulos import M3_hidraulica as M3
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.test_ext3_regimen_barril import (D_CASO, L_CASO, CRITERIOS_CORRIDA,
                                            _b01, _concreto, _correr,
                                            _informe_dimensionado_con,
                                            _no_evaluables, _resuelto)
from tests.test_MD import _punto as _punto_md

# Escritos en rojo con `xfail(strict=True)` de modulo --medidos 26 xfailed y 0
# XPASS antes de tocar codigo-- y liberados al corregir: el marcador se retiro
# y esta linea queda como constancia.

# Con que se contrastan los dos dorados de limite: son identidades de la
# propia formula, y la unica diferencia admisible es la asociacion de la
# aritmetica en punto flotante.
REL_DORADO_LIMITE = 1e-9
# Con que se contrastan los numeros que el prototipo de E-A imprimio con tres
# o cuatro cifras: lectura, no dorado (misma regla que REL_DICTAMEN en EXT-3).
REL_PROTOTIPO = 1e-3
# Balance de energia estacion a estacion: es la ecuacion que el paso directo
# resuelve, y tiene que cerrar al ruido de la aritmetica.
REL_BALANCE = 1e-9
# Convergencia entre dos escaleras (N y 2N rungs), en metros de HW.
ABS_CONVERGENCIA_M = 1e-6

KE_CASO = 0.5           # el mismo ke que `control_salida` lee del criterio


def _normal_y_critico(seccion, Q, S, material=None):
    n = (material or _concreto()).n_para_capacidad
    normal = M3.tirante_normal(seccion, Q, S, n)
    return normal, M4.tirante_critico(Q, seccion), n


def _perfil(seccion, Q, S, TW, L=L_CASO, ke=KE_CASO, normal=None, critico=None,
            n=None, HW_aproximado=0.0, **kw):
    """`normal` se admite y se ignora: desde la auditoria de E-A el perfil
    clasifica por el signo de Sf - S con su propia ley (ver `perfil_lamina`)."""
    if critico is None or n is None:
        _normal, critico_, n_ = _normal_y_critico(seccion, Q, S)
        critico = critico if critico is not None else critico_
        n = n if n is not None else n_
    return M4.perfil_lamina(Q_celda=Q, seccion=seccion, S=S, L=L, TW=TW, n=n,
                            ke=ke, critico=critico, HW_aproximado=HW_aproximado,
                            **kw)


def _E_y_Sf(seccion, Q, n, y):
    """Energia especifica y pendiente de friccion (Ec. 3.7) al tirante y."""
    A = seccion.area(y)
    P = seccion.perimetro(y)
    V = Q / A
    R = A / P
    return y + V ** 2 / (2 * G), K_FRICCION_SI * n ** 2 * V ** 2 / (R ** (4 / 3) * 2 * G)


# ===========================================================================
# 1. Lo que E-A introduce como tipos, y donde viven
# ===========================================================================

def test_el_tipo_del_perfil_vive_en_modelos_y_el_resultado_lo_lleva_en_un_campo():
    assert {m.name for m in modelos.TipoDePerfil} == {
        "M1", "M2", "S1", "UNIFORME", "LLENA"}
    campos = {f.name for f in modelos.PerfilLamina.__dataclass_fields__.values()}
    assert {"tipo", "y_salida_m", "alcanza_entrada", "x_fin_remanso_m",
            "y_entrada_m", "V_entrada_m_s", "HW_remanso_m", "longitud_llena_m",
            "fraccion_llena", "y_max_m", "V_min_m_s", "n", "ke",
            "HW_aproximado_m", "sustituye_aproximacion", "cautela_aproximacion",
            "y_asintota_m", "rungs", "estaciones"} <= campos
    assert "perfil" in modelos.ResultadoHidraulico.__dataclass_fields__
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    assert isinstance(r.perfil, modelos.PerfilLamina)


def test_las_tolerancias_del_paso_directo_son_numericas_y_estan_nombradas():
    from src import tolerancias
    assert isinstance(tolerancias.PASOS_PERFIL_LAMINA, int)
    assert tolerancias.PASOS_PERFIL_LAMINA >= 100
    assert 0 < tolerancias.TOL_ASINTOTA_PERFIL < 1e-6


# ===========================================================================
# 2. Los dos dorados de limite (conflicto #7: sin corrida externa citable)
# ===========================================================================

def test_dorado_flujo_lleno_reproduce_la_formula_cerrada_del_control_de_salida():
    """
    TW = 1.2 m sobre D = 0.90 m, Q = 0.05, S = 0.005, L = 20: la linea de
    energia llena arranca en el TW y NO baja de la clave antes de la entrada,
    de modo que el perfil es la Ec. 3.7 de punta a punta y HW tiene que ser
    H + h_o - S*L con h_o = TW (`control_salida`), identidad algebraica.
    """
    sec = SeccionCircular(D_CASO)
    Q, S, TW = 0.05, 0.005, 1.2
    normal, critico, n = _normal_y_critico(sec, Q, S)
    salida = M4.control_salida(Q=Q, seccion=sec, S=S, L=L_CASO, TW=TW, n=n,
                               ke=KE_CASO, critico=critico)
    p = _perfil(sec, Q, S, TW, normal=normal, critico=critico, n=n,
                HW_aproximado=salida.HW)
    assert p.tipo is modelos.TipoDePerfil.LLENA
    assert p.alcanza_entrada
    assert p.fraccion_llena == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert p.longitud_llena_m == pytest.approx(L_CASO, rel=REL_TRANSPORTE)
    assert p.HW_remanso_m == pytest.approx(salida.HW, rel=REL_DORADO_LIMITE)
    assert p.V_min_m_s == pytest.approx(Q / sec.area_llena, rel=REL_TRANSPORTE)
    assert p.y_max_m == pytest.approx(D_CASO, rel=REL_TRANSPORTE)


def test_dorado_flujo_uniforme_el_perfil_es_plano_en_su_propia_asintota():
    """
    TW = y_n' (donde la Ec. 3.7 da Sf = S) en pendiente suave: nada mueve la
    lamina y HW = y_n' + (1+ke)V^2/2g. La asintota del perfil NO es el y_n de
    Manning de M3 (auditoria adversarial de E-A): esta un 0.05 % por encima,
    porque K_FRICCION_SI/(2g) = 19.63/19.62, y el perfil la publica.
    """
    sec = SeccionCircular(D_CASO)
    Q, S = 0.3, 0.001
    normal, critico, n = _normal_y_critico(sec, Q, S)
    assert normal.y > critico.y_c, "el caso es de pendiente suave"
    desde_y_n = _perfil(sec, Q, S, TW=normal.y, critico=critico, n=n)
    y_asintota = desde_y_n.y_asintota_m
    assert y_asintota is not None
    assert y_asintota == pytest.approx(normal.y * (K_FRICCION_SI / (2 * G)) ** 0,
                                       rel=1e-3)
    assert 0 < (y_asintota - normal.y) / normal.y < 1e-3
    p = _perfil(sec, Q, S, TW=y_asintota, critico=critico, n=n)
    V = Q / sec.area(y_asintota)
    assert p.tipo is modelos.TipoDePerfil.UNIFORME
    assert p.alcanza_entrada
    assert p.y_entrada_m == pytest.approx(y_asintota, rel=REL_TRANSPORTE)
    # V_entrada la publica el retorno UNIFORME y ningun otro test la leia: el
    # arnes de mutacion lo encontro (Q/A -> Q*A sobrevivia a toda la suite).
    assert p.V_entrada_m_s == pytest.approx(V, rel=REL_DORADO_LIMITE)
    assert p.HW_remanso_m == pytest.approx(
        y_asintota + (1 + KE_CASO) * V ** 2 / (2 * G), rel=REL_DORADO_LIMITE)
    assert p.y_max_m == pytest.approx(y_asintota, rel=REL_TRANSPORTE)
    assert p.V_min_m_s == pytest.approx(V, rel=REL_DORADO_LIMITE)
    assert p.fraccion_llena == pytest.approx(0.0, abs=ABS_CERO)


# Cuanto puede separarse de su asintota una lamina que arranca a un ulp de
# ella e integra 20 m: lo que mide el punto fijo, en metros.
ABS_PUNTO_FIJO_M = 1e-6
# Desplazamiento relativo con que se arranca sobre la asintota.
REL_ARRANQUE_PUNTO_FIJO = 1e-7


@pytest.mark.parametrize("signo", [+1, -1])
def test_la_asintota_es_un_punto_fijo_de_la_integracion(signo):
    """
    No el atajo: INTEGRANDO. Arrancando a 1e-7 relativo por encima (M1) o por
    debajo (M2) de y_n', la escalera no puede alejarse de la asintota, y HW
    coincide con el del flujo uniforme a la millonesima de metro. Es el dorado
    de flujo uniforme medido por el metodo y no por su atajo.
    """
    sec = SeccionCircular(D_CASO)
    Q, S = 0.3, 0.001
    normal, critico, n = _normal_y_critico(sec, Q, S)
    y_asintota = _perfil(sec, Q, S, TW=normal.y, critico=critico, n=n).y_asintota_m
    TW = y_asintota * (1 + signo * REL_ARRANQUE_PUNTO_FIJO)
    p = _perfil(sec, Q, S, TW=TW, critico=critico, n=n)
    assert p.tipo is (modelos.TipoDePerfil.M1 if signo > 0 else modelos.TipoDePerfil.M2)
    assert p.alcanza_entrada
    assert all(abs(y - y_asintota) < ABS_PUNTO_FIJO_M for _x, y in p.estaciones)
    V = Q / sec.area(y_asintota)
    assert abs(p.HW_remanso_m - (y_asintota + (1 + KE_CASO) * V ** 2 / (2 * G))) \
        < ABS_PUNTO_FIJO_M


def test_un_TW_entre_y_n_de_manning_y_la_asintota_no_revienta():
    """La banda de 0.07 mm que la auditoria de E-A encontro: M1 sin excepcion."""
    sec = SeccionCircular(D_CASO)
    Q, S = 0.3, 0.001
    normal, critico, n = _normal_y_critico(sec, Q, S)
    for TW in (normal.y + 5e-5, normal.y + 1e-6, normal.y + 3e-5):
        p = _perfil(sec, Q, S, TW=TW, critico=critico, n=n)
        assert p.tipo in (modelos.TipoDePerfil.M1, modelos.TipoDePerfil.M2,
                          modelos.TipoDePerfil.UNIFORME)
        assert p.alcanza_entrada and math.isfinite(p.HW_remanso_m)
    r = _resuelto(Q=0.3, S=0.001, TW=normal.y + 5e-5)
    assert r.perfil.alcanza_entrada


def test_un_TW_a_menos_de_la_tolerancia_de_la_clave_no_revienta():
    """TW en (D - 1e-9, D): LLENO por `regimen_del_barril`, y el perfil toma la
    clave como frontera en vez de producir un tramo lleno negativo."""
    r = _resuelto(Q=0.3, S=0.001, TW=D_CASO - 5e-10)
    assert r.regimen_barril is RegimenBarril.LLENO
    assert r.perfil.fraccion_llena == pytest.approx(0.0, abs=ABS_CERO)
    assert r.perfil.y_max_m == pytest.approx(D_CASO, rel=REL_TRANSPORTE)
    marco = SeccionRectangular(B=2.0, H=1.5)
    critico = M4.tirante_critico(3.0, marco)
    p = _perfil(marco, 3.0, 0.001, TW=1.5 - 1e-10, critico=critico, n=0.014)
    assert p.fraccion_llena == pytest.approx(0.0, abs=ABS_CERO)


def test_en_la_banda_de_cautela_manda_la_comprobacion_cuando_pide_mas_carga():
    """
    Q = 0.5, S = 0.002, TW = 0.666 (el maximo del barrido de la auditoria de
    E-A): 0.75 <= HW_aprox/D < 1.2, y el remanso da +34 mm sobre la
    aproximacion. Del lado de la inundacion manda el mayor: HW_salida es el
    del remanso, y el paso 4.3d lo dice.
    """
    r = _resuelto(Q=0.5, S=0.002, TW=0.666)
    p = r.perfil
    assert p.cautela_aproximacion and not p.sustituye_aproximacion
    assert p.alcanza_entrada and p.HW_remanso_m > p.HW_aproximado_m
    assert p.comprobacion_manda
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.HW_salida == pytest.approx(p.HW_remanso_m, rel=REL_TRANSPORTE)
    assert r.HW_sobre_D_salida == pytest.approx(p.HW_aproximado_m / D_CASO,
                                                rel=REL_TRANSPORTE)
    remanso = next(pp for pp in r.pasos
                   if pp.fundamento_id == "F4.PERFIL" and pp.codigo == "4.3d")
    assert "manda" in remanso.veredicto.explicacion
    adopcion = next(pp for pp in r.pasos
                    if pp.fundamento_id == "F4.CONTROL" and pp.codigo == "4.4")
    assert adopcion.resultado.valor == pytest.approx(p.HW_remanso_m, rel=REL_TRANSPORTE)


# ===========================================================================
# 3. Balance de energia y monotonia de M1, M2 y S1
# ===========================================================================

@pytest.mark.parametrize("Q, S, TW, tipo, creciente", [
    (0.3, 0.001, 0.0, "M2", True),     # salida libre, pendiente suave: sube hacia y_n
    (0.3, 0.001, 0.6, "M1", False),    # TW > y_n: baja hacia y_n
    (0.3, 0.005, 0.6, "S1", False),    # steep con TW > y_c: baja hacia y_c
])
def test_balance_de_energia_y_monotonia_estacion_a_estacion(Q, S, TW, tipo, creciente):
    sec = SeccionCircular(D_CASO)
    normal, critico, n = _normal_y_critico(sec, Q, S)
    p = _perfil(sec, Q, S, TW, normal=normal, critico=critico, n=n)
    assert p.tipo is modelos.TipoDePerfil[tipo]
    assert len(p.estaciones) >= 3
    xs = [x for x, _y in p.estaciones]
    ys = [y for _x, y in p.estaciones]
    assert xs == sorted(xs) and xs[0] == pytest.approx(0.0, abs=ABS_CERO)
    assert ys[0] == pytest.approx(max(critico.y_c, TW), rel=REL_TRANSPORTE)
    deltas = [b - a for a, b in zip(ys, ys[1:])]
    assert all(d > 0 for d in deltas) if creciente else all(d < 0 for d in deltas)
    for (x0, y0), (x1, y1) in zip(p.estaciones, p.estaciones[1:]):
        E0, Sf0 = _E_y_Sf(sec, Q, n, y0)
        E1, Sf1 = _E_y_Sf(sec, Q, n, y1)
        dx = x1 - x0
        assert E1 + S * dx == pytest.approx(E0 + (Sf0 + Sf1) / 2 * dx,
                                            rel=REL_BALANCE)


def test_la_escalera_converge_al_duplicar_los_rungs():
    from src import tolerancias
    sec = SeccionCircular(D_CASO)
    Q, S, TW = 0.3, 0.001, 0.0
    normal, critico, n = _normal_y_critico(sec, Q, S)
    p1 = _perfil(sec, Q, S, TW, normal=normal, critico=critico, n=n,
                 rungs=tolerancias.PASOS_PERFIL_LAMINA)
    p2 = _perfil(sec, Q, S, TW, normal=normal, critico=critico, n=n,
                 rungs=2 * tolerancias.PASOS_PERFIL_LAMINA)
    assert abs(p1.HW_remanso_m - p2.HW_remanso_m) < ABS_CONVERGENCIA_M
    assert abs(p1.y_entrada_m - p2.y_entrada_m) < ABS_CONVERGENCIA_M


def test_la_rectangular_tambien_tiene_perfil_por_la_via_canonica():
    """Un marco de 2.00 x 1.50 con salida libre en pendiente suave: M2."""
    sec = SeccionRectangular(B=2.0, H=1.5)
    Q, S, n = 3.0, 0.001, 0.014
    normal = M3.tirante_normal(sec, Q, S, n)
    critico = M4.tirante_critico(Q, sec)
    assert normal.y > critico.y_c
    p = _perfil(sec, Q, S, TW=0.0, normal=normal, critico=critico, n=n)
    assert p.tipo is modelos.TipoDePerfil.M2 and p.alcanza_entrada
    assert critico.y_c < p.y_entrada_m < normal.y
    assert math.isfinite(p.HW_remanso_m) and p.HW_remanso_m > p.y_entrada_m


def test_la_escalera_admite_dos_escalones_y_rechaza_uno():
    sec = SeccionCircular(D_CASO)
    normal, critico, n = _normal_y_critico(sec, 0.3, 0.001)
    p = _perfil(sec, 0.3, 0.001, TW=0.0, normal=normal, critico=critico, n=n,
                rungs=2)
    assert p.rungs == 2 and p.alcanza_entrada
    with pytest.raises(ValueError):
        _perfil(sec, 0.3, 0.001, TW=0.0, normal=normal, critico=critico, n=n,
                rungs=1)


def test_m1_el_tirante_maximo_y_la_velocidad_minima_estan_en_la_salida():
    """TW = 0.6 > y_n: la lamina baja aguas arriba, el maximo es el TW."""
    sec = SeccionCircular(D_CASO)
    Q, S, TW = 0.3, 0.001, 0.6
    p = _perfil(sec, Q, S, TW)
    assert p.tipo is modelos.TipoDePerfil.M1
    assert p.y_max_m == pytest.approx(TW, rel=REL_TRANSPORTE)
    assert p.V_min_m_s == pytest.approx(Q / sec.area(TW), rel=REL_DORADO_LIMITE)
    assert p.y_entrada_m < TW


def test_sin_tirante_normal_la_linea_llena_sube_desde_el_TW_hasta_la_entrada():
    """
    Q = 1.5 > Q_lleno (Manning no tiene solucion en lamina libre) con TW = 1.0
    sobre D = 0.90: Sf_llena > S, la linea de energia llena SUBE aguas arriba
    y llega a la entrada por encima de la clave. El HW vuelve a ser la formula
    cerrada de `control_salida` con h_o = TW (segundo dorado de limite).
    """
    sec = SeccionCircular(D_CASO)
    Q, S, TW, n = 1.5, 0.001, 1.0, _concreto().n_para_capacidad
    assert M3.tirante_normal(sec, Q, S, n) is None
    critico = M4.tirante_critico(Q, sec)
    salida = M4.control_salida(Q=Q, seccion=sec, S=S, L=L_CASO, TW=TW, n=n,
                               ke=KE_CASO, critico=critico)
    p = _perfil(sec, Q, S, TW, normal=None, critico=critico, n=n,
                HW_aproximado=salida.HW)
    assert p.tipo is modelos.TipoDePerfil.LLENA and p.alcanza_entrada
    assert p.fraccion_llena == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert p.y_entrada_m > TW > D_CASO
    assert p.HW_remanso_m == pytest.approx(salida.HW, rel=REL_DORADO_LIMITE)
    assert p.estaciones == ()


def test_sin_tirante_normal_la_M2_corta_la_clave_y_sigue_llena(tmp_path):
    """
    Fig. 3.7B de HDS-5 (pag. 3.12): Q = 1.0 > Q_lleno con salida libre en un
    barril de 300 m. La M2 sube desde y_c, corta la clave a x_clave y desde
    ahi «a straight, full flow hydraulic grade line extends from that point
    upstream to the culvert entrance». La longitud llena es L - x_clave y la
    carga en la entrada D + (Sf_llena - S)*(L - x_clave) + (1 + ke)*V^2/2g.
    """
    sec = SeccionCircular(D_CASO)
    Q, S, L, n = 1.0, 0.001, 300.0, _concreto().n_para_capacidad
    assert M3.tirante_normal(sec, Q, S, n) is None
    critico = M4.tirante_critico(Q, sec)
    p = _perfil(sec, Q, S, TW=0.0, L=L, normal=None, critico=critico, n=n)
    assert p.tipo is modelos.TipoDePerfil.LLENA and p.alcanza_entrada
    x_clave, y_clave = p.estaciones[-1]
    assert y_clave == pytest.approx(D_CASO, rel=REL_TRANSPORTE)
    assert p.estaciones[0][1] == pytest.approx(critico.y_c, rel=REL_TRANSPORTE)
    assert critico.y_c < y_clave and 0 < x_clave < L
    assert p.longitud_llena_m == pytest.approx(L - x_clave, rel=REL_DORADO_LIMITE)
    assert 0 < p.fraccion_llena < 1
    assert p.fraccion_llena == pytest.approx((L - x_clave) / L, rel=REL_DORADO_LIMITE)
    V = Q / sec.area_llena
    Sf = K_FRICCION_SI * n ** 2 * V ** 2 / (sec.radio_hidraulico_lleno ** (4 / 3) * 2 * G)
    assert Sf > S
    y_in = D_CASO + (Sf - S) * (L - x_clave)
    assert p.y_entrada_m == pytest.approx(y_in, rel=REL_DORADO_LIMITE)
    assert p.HW_remanso_m == pytest.approx(y_in + (1 + KE_CASO) * V ** 2 / (2 * G),
                                           rel=REL_DORADO_LIMITE)
    assert p.y_max_m == pytest.approx(D_CASO, rel=REL_TRANSPORTE)
    assert p.V_min_m_s == pytest.approx(V, rel=REL_TRANSPORTE)


def test_tramo_lleno_seguido_de_una_S1_que_no_llega_a_la_entrada():
    """TW = 0.95 > D en 200 m de barril pronunciado: lleno en x*, S1 hasta
    y_c a 162 m, y el remanso no alcanza la entrada."""
    sec = SeccionCircular(D_CASO)
    Q, S, TW, L = 0.05, 0.005, 0.95, 200.0
    normal, critico, n = _normal_y_critico(sec, Q, S)
    V = Q / sec.area_llena
    Sf = K_FRICCION_SI * n ** 2 * V ** 2 / (sec.radio_hidraulico_lleno ** (4 / 3) * 2 * G)
    x_estrella = (TW - D_CASO) / (S - Sf)
    p = _perfil(sec, Q, S, TW, L=L, normal=normal, critico=critico, n=n)
    assert p.tipo is modelos.TipoDePerfil.S1 and not p.alcanza_entrada
    assert x_estrella < p.x_fin_remanso_m < L
    assert p.longitud_llena_m == pytest.approx(x_estrella, rel=REL_DORADO_LIMITE)
    assert p.fraccion_llena == pytest.approx(x_estrella / L, rel=REL_DORADO_LIMITE)
    assert p.y_max_m == pytest.approx(D_CASO, rel=REL_TRANSPORTE)
    assert p.V_min_m_s == pytest.approx(V, rel=REL_TRANSPORTE)
    assert p.HW_remanso_m is None and p.y_entrada_m is None


# ===========================================================================
# 4. La fraccion de longitud a seccion llena: la primera condicion, MEDIDA
# ===========================================================================

def test_fraccion_llena_analitica_cuando_el_tramo_lleno_arranca_en_la_salida():
    """
    TW = 0.95 > D = 0.90 con Q = 0.05, S = 0.005: la linea llena baja de la
    clave en x* = (TW - D)/(S - Sf_llena), y aguas arriba sigue la lamina
    libre. Fraccion = x*/L, con Sf_llena la Ec. 3.7 a seccion llena.
    """
    sec = SeccionCircular(D_CASO)
    Q, S, TW = 0.05, 0.005, 0.95
    normal, critico, n = _normal_y_critico(sec, Q, S)
    V = Q / sec.area_llena
    Sf = K_FRICCION_SI * n ** 2 * V ** 2 / (sec.radio_hidraulico_lleno ** (4 / 3) * 2 * G)
    x_estrella = (TW - D_CASO) / (S - Sf)
    p = _perfil(sec, Q, S, TW, normal=normal, critico=critico, n=n)
    assert 0 < x_estrella < L_CASO
    assert p.longitud_llena_m == pytest.approx(x_estrella, rel=REL_DORADO_LIMITE)
    assert p.fraccion_llena == pytest.approx(x_estrella / L_CASO, rel=REL_DORADO_LIMITE)
    assert p.y_max_m == pytest.approx(D_CASO, rel=REL_TRANSPORTE)
    assert p.alcanza_entrada and p.y_entrada_m < D_CASO
    assert p.estaciones[0][0] == pytest.approx(x_estrella, rel=REL_DORADO_LIMITE)


def test_b01_de_la_linea_base_fluye_lleno_en_la_mitad_de_su_longitud():
    """Q = 0.095, S = 0.010, TW = 1.0 sobre D = 0.90 (la B-01 ampliada): 0.501."""
    r = _resuelto(Q=0.095, S=0.010, TW=1.0)
    assert r.regimen_barril is RegimenBarril.LLENO
    assert r.perfil.fraccion_llena == pytest.approx(0.501, rel=REL_PROTOTIPO)
    assert r.perfil.fraccion_llena > 1 / 2


def test_la_primera_condicion_se_juzga_en_el_paso_del_perfil():
    """
    El paso F4.PERFIL (codigo 4.3c) lleva como umbral la lectura de «most of
    its length» y juzga sobre la fraccion medida: CUMPLE en la B-01 ampliada
    (0.501), SIN_VEREDICTO cuando la aproximacion no se usa (el caso (c), que
    el remanso sustituye).
    """
    criterio = ca.criterio("fraccion_llena_mayor_parte")
    assert criterio.etiqueta == "A" and criterio.nivel == ca.NIVEL_PERFIL
    assert criterio.valor == pytest.approx(1 / 2, rel=REL_TRANSPORTE)
    assert criterio.sensibilidad
    b01 = _resuelto(Q=0.095, S=0.010, TW=1.0)
    paso = next(p for p in b01.pasos if p.fundamento_id == "F4.PERFIL")
    assert paso.codigo == "4.3c"
    assert paso.umbral is not None
    assert paso.umbral.criterio_aplicado == "fraccion_llena_mayor_parte"
    assert paso.umbral.valor == pytest.approx(criterio.valor, rel=REL_TRANSPORTE)
    assert paso.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert "HDS5_3ED.3.1.4#REMANSO" in paso.citas_textuales
    assert "HDS5_3ED.3.5#PERFIL" in paso.citas_textuales
    c = _resuelto(Q=0.3, S=0.001, TW=0.0)
    paso_c = next(p for p in c.pasos if p.fundamento_id == "F4.PERFIL")
    assert paso_c.veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    simbolos = {m.simbolo for m in paso_c.sustitucion}
    assert {"y_salida", "y_n", "y_c", "n", "S", "L", "ke"} <= simbolos


# ===========================================================================
# 5. El HW por remanso bajo HW/D < 0.75 y la circularidad deshecha
# ===========================================================================

def test_b_el_barril_supercritico_del_dictamen_pasa_a_control_de_entrada():
    """
    Caso (b): Q = 0.3, S = 0.005, TW = 0. La aproximacion decia SALIDA con
    HW/D = 0.589 < 0.75 (metodo no evaluable). Con y_n = 0.2965 < y_c =
    0.3157 el barril es supercritico: la S1 desde y_c tiene longitud cero, el
    remanso no alcanza la entrada (HDS-5 3.5.1: «used if the S1 curve extends
    to the face of the culvert») y gobierna la ENTRADA con su propio HW.
    """
    r = _resuelto(Q=0.3, S=0.005, TW=0.0)
    p = r.perfil
    assert r.y_normal < r.y_critico
    assert p.tipo is modelos.TipoDePerfil.S1
    assert not p.alcanza_entrada and p.HW_remanso_m is None
    assert p.x_fin_remanso_m == pytest.approx(0.0, abs=ABS_CERO)
    assert p.sustituye_aproximacion
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.HW == pytest.approx(r.HW_entrada, rel=REL_TRANSPORTE)
    assert not r.h_o_fuera_de_rango
    ho = next(pp for pp in r.pasos if pp.fundamento_id == "F4.HO")
    assert ho.veredicto.tipo is not TipoDeVeredicto.DIFERIDO


def test_c_el_remanso_sustituye_a_la_aproximacion_bajo_0_75D():
    """
    Caso (c): Q = 0.3, S = 0.001, TW = 0 (pendiente suave). La aproximacion
    daba HW_salida = 0.6103 (HW/D 0.678 < 0.75). La M2 desde y_c llega a la
    entrada con y = 0.391 y HW = 0.489 > HW_entrada = 0.438: sigue gobernando
    la SALIDA, con el HW del remanso y sin bloqueo.
    """
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    p = r.perfil
    assert p.tipo is modelos.TipoDePerfil.M2 and p.alcanza_entrada
    assert p.sustituye_aproximacion
    assert p.HW_aproximado_m == pytest.approx(0.6103, rel=REL_PROTOTIPO)
    assert p.HW_remanso_m == pytest.approx(0.489, rel=REL_PROTOTIPO)
    assert p.y_entrada_m == pytest.approx(0.391, rel=REL_PROTOTIPO)
    assert p.V_min_m_s == pytest.approx(1.130, rel=REL_PROTOTIPO)
    assert p.y_max_m == pytest.approx(p.y_entrada_m, rel=REL_TRANSPORTE)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.HW_salida == pytest.approx(p.HW_remanso_m, rel=REL_TRANSPORTE)
    # HW/D_salida sigue siendo el de la APROXIMACION: es el cociente que las
    # dos condiciones juzgan (auditoria adversarial de E-A).
    assert r.HW_sobre_D_salida == pytest.approx(p.HW_aproximado_m / D_CASO,
                                                rel=REL_TRANSPORTE)
    assert not r.h_o_fuera_de_rango
    ho = next(pp for pp in r.pasos if pp.fundamento_id == "F4.HO")
    assert ho.veredicto.tipo is not TipoDeVeredicto.DIFERIDO
    assert modelos.MOTIVO_METODO_NO_EVALUABLE not in ho.veredicto.explicacion
    adopcion = next(pp for pp in r.pasos
                    if pp.fundamento_id == "F4.CONTROL" and pp.codigo == "4.4")
    assert adopcion.resultado.valor == pytest.approx(p.HW_remanso_m, rel=REL_TRANSPORTE)


def test_s1_que_alcanza_la_entrada_sustituye_con_su_propio_hw():
    """Q = 0.3, S = 0.005, TW = 0.6 > y_c: la S1 llega a la entrada (0.5518)."""
    r = _resuelto(Q=0.3, S=0.005, TW=0.6)
    p = r.perfil
    assert p.tipo is modelos.TipoDePerfil.S1 and p.alcanza_entrada
    assert p.sustituye_aproximacion
    assert p.HW_remanso_m == pytest.approx(0.5518, rel=REL_PROTOTIPO)
    assert p.y_max_m == pytest.approx(0.6, rel=REL_TRANSPORTE)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.HW_salida == pytest.approx(p.HW_remanso_m, rel=REL_TRANSPORTE)


def test_s1_que_termina_antes_de_la_entrada_devuelve_el_control_a_la_entrada():
    """TW = 0.35, apenas sobre y_c en steep: la S1 corta y_c a x_fin < L."""
    r = _resuelto(Q=0.3, S=0.005, TW=0.35)
    p = r.perfil
    assert p.tipo is modelos.TipoDePerfil.S1
    assert not p.alcanza_entrada
    assert 0 < p.x_fin_remanso_m < L_CASO
    assert r.control_gobernante is ControlGobernante.ENTRADA
    # El tirante maximo con que V1 juzga incluye la S1 (el TW) y la S2
    # aproximada por el uniforme aguas arriba del resalto.
    assert p.y_max_m == pytest.approx(max(0.35, r.y_normal), rel=REL_TRANSPORTE)


def test_dentro_del_rango_de_la_fuente_la_aproximacion_sigue_gobernando():
    """
    A-01 (control de entrada) y el caso ahogado (SALIDA con HW/D = 1.22):
    la aproximacion no se sustituye --la pag. 3.12 la avala hasta 0.75D-- y
    el perfil viaja como comprobacion impresa. HW_salida no se mueve.
    """
    ahogado = _resuelto(Q=0.05, S=0.005, TW=1.2)
    assert not ahogado.perfil.sustituye_aproximacion
    assert ahogado.HW_salida == pytest.approx(ahogado.perfil.HW_aproximado_m,
                                              rel=REL_TRANSPORTE)
    a01 = _resuelto(Q=1.167, S=0.006, TW=0.22)
    assert a01.control_gobernante is ControlGobernante.ENTRADA
    assert not a01.perfil.sustituye_aproximacion


# ===========================================================================
# 6. V1 y V2 dejan de estar pendientes bajo control de salida parcial
# ===========================================================================

def test_V1_y_V2_se_evaluan_con_el_tirante_maximo_y_la_velocidad_minima_del_perfil():
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    assert r.regimen_barril is RegimenBarril.PARCIALMENTE_LLENO
    assert r.control_gobernante is ControlGobernante.SALIDA
    v1 = M5.v1_borde_libre(D=D_CASO, material=_concreto(), punto=_punto_md(),
                           resultado=r)
    v2 = M5.v2_velocidad_minima(resultado=r)
    assert v1.valor_obtenido == pytest.approx(r.perfil.y_max_m / D_CASO,
                                              rel=REL_TRANSPORTE)
    assert v2.valor_obtenido == pytest.approx(r.perfil.V_min_m_s, rel=REL_TRANSPORTE)
    assert v1.cumple and v2.cumple
    assert "4.3c" in v1.paso.sustitucion[0].procedencia
    assert "4.3c" in v2.paso.sustitucion[0].procedencia


def test_sin_perfil_V1_y_V2_siguen_diciendo_metodo_no_evaluable():
    """El fallback: un resultado armado sin M4 no trae perfil y no se inventa."""
    r = replace(_resuelto(Q=0.3, S=0.001, TW=0.0), perfil=None)
    with pytest.raises(modelos.MetodoNoEvaluableError):
        M5.v1_borde_libre(D=D_CASO, material=_concreto(), punto=_punto_md(),
                          resultado=r)
    with pytest.raises(modelos.MetodoNoEvaluableError):
        M5.v2_velocidad_minima(resultado=r)


def test_y_sobre_D_del_punto_sigue_al_perfil_bajo_control_de_salida():
    from src.modelos import ResultadoPunto
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    punto = ResultadoPunto(punto=_punto_md(), aceptado=True, material=_concreto(),
                           seccion=SeccionCircular(D_CASO), resultado_hidraulico=r,
                           verificaciones=())
    assert punto.y_sobre_D == pytest.approx(r.perfil.y_max_m / D_CASO,
                                            rel=REL_TRANSPORTE)


# ===========================================================================
# 7. La corrida entera: ningun «metodo no evaluable» con el perfil
# ===========================================================================

@pytest.mark.parametrize("alcance", [cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE])
def test_la_corrida_ya_no_produce_bloqueos_no_evaluables(tmp_path, alcance):
    for Q, S in ((0.3, 0.005), (0.3, 0.001), (0.095, 0.010)):
        carpeta = tmp_path / f"{Q}_{S}_{alcance}"
        carpeta.mkdir()
        informe = _correr(carpeta, Q=Q, S=S, TW=0.0, alcance=alcance)
        b01 = _b01(informe)
        assert not _no_evaluables(b01), (Q, S, [b.tipo for b in b01.bloqueos])
        if alcance == cli.ALCANCE_PERFIL:
            assert b01.dimensionado
            codigos = {v.codigo for _fase, v in b01.verificaciones()}
            assert {"V1", "V2"} <= codigos


def test_la_compuerta_solo_dispara_sobre_un_resultado_sin_perfil():
    r = _resuelto(Q=0.3, S=0.001, TW=0.0)
    assert not r.h_o_fuera_de_rango
    con_perfil = _informe_dimensionado_con(r)
    cli._compuerta_metodo_h_o(con_perfil, cli.ALCANCE_EXPEDIENTE)
    assert not con_perfil.bloqueos
    sin_perfil = _informe_dimensionado_con(
        replace(r, perfil=None, h_o_fuera_de_rango=True))
    cli._compuerta_metodo_h_o(sin_perfil, cli.ALCANCE_EXPEDIENTE)
    [b] = _no_evaluables(sin_perfil)
    assert b.diferido_por_alcance is False


# ===========================================================================
# 8. El perfil llega al JSON y a cli.volcar
# ===========================================================================

CLAVES_PERFIL = ("perfil_tipo", "perfil_alcanza_entrada", "perfil_HW_remanso_m",
                 "perfil_HW_aproximado_m", "perfil_sustituye_aproximacion",
                 "perfil_y_entrada_m", "perfil_y_max_m", "perfil_V_min_m_s",
                 "perfil_fraccion_llena", "perfil_longitud_llena_m",
                 "perfil_y_asintota_m", "perfil_comprobacion_manda")


def test_el_perfil_llega_al_json_y_a_volcar(tmp_path):
    informe = _correr(tmp_path, Q=0.3, S=0.001, TW=0.0, alcance=cli.ALCANCE_PERFIL)
    diseno = cli.informe_json(informe)["puntos"][0]["diseno"]
    for clave in CLAVES_PERFIL:
        assert clave in diseno, clave
        assert clave in cli.CLAVES_DISENO_JSON, clave
    assert diseno["perfil_tipo"] in {t.value for t in modelos.TipoDePerfil}
    json.dumps(cli.informe_json(informe))
    texto = cli.volcar(informe)
    assert "Perfil" in texto and "remanso" in texto


# ===========================================================================
# 9. La regla vinculante #12: el perfil integra en el parametro propio
# ===========================================================================

def test_el_perfil_no_gana_consumidores_de_la_via_por_tirante():
    """
    `perfil_lamina` y sus auxiliares recorren la seccion por `geometria_en`
    sobre el parametro propio y resuelven el llenado del TW con Brent sobre
    `bracket_llenado()`: ninguna llamada a `area(y)`, `perimetro(y)`,
    `ancho_superficial(y)` ni a `theta_desde_tirante`. El censo de
    `test_seccion_rectangular` lo vigila en todo `src/`; aqui se fija ademas
    por nombre de funcion, para que el motivo quede junto al motor.
    """
    fuente = (Path(__file__).resolve().parents[1] / "src" / "modulos"
              / "M4_control.py").read_text(encoding="utf-8")
    arbol = ast.parse(fuente)
    nombres = {"perfil_lamina", "_llenado_de_tirante", "_pendiente_friccion",
               "_llenado_donde_Sf_iguala_S"}
    funciones = {n.name: n for n in ast.walk(arbol)
                 if isinstance(n, ast.FunctionDef) and n.name in nombres}
    assert set(funciones) == nombres, sorted(funciones)
    prohibidas = {"area", "perimetro", "ancho_superficial", "theta_desde_tirante"}
    for nombre, fn in funciones.items():
        llamadas = {n.func.attr for n in ast.walk(fn)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        assert not (llamadas & prohibidas), (nombre, llamadas & prohibidas)
    assert "geometria_en" in {n.func.attr for n in ast.walk(funciones["perfil_lamina"])
                              if isinstance(n, ast.Call)
                              and isinstance(n.func, ast.Attribute)}


def test_las_siete_citas_nuevas_estan_en_el_registro_y_verificadas():
    from src.normativa import registro as rn
    reg = rn.construir()
    for cita_id, pagina in (("HDS5_3ED.3.1.4#REMANSO", 94),
                            ("HDS5_3ED.3.1.4#EMPALME", 94),
                            ("HDS5_3ED.3.1.4#HW_REMANSO", 94),
                            ("HDS5_3ED.3.1.4#0_75D", 94),
                            ("HDS5_3ED.3.5#PERFIL", 118),
                            ("HDS5_3ED.3.5.1#S1", 119),
                            ("HDS5_3ED.3.5.1#TIPO7", 120)):
        c = reg.cita(cita_id)
        assert c.pagina_pdf == pagina, cita_id
        assert c.verificado is not None, cita_id
    f = reg.fundamento("F4.PERFIL")
    assert "HDS5_3ED.3.1.4#REMANSO" in f.citas
