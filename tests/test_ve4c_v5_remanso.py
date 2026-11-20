"""
tests/test_ve4c_v5_remanso.py
=============================
VE-4c: el metodo `perfil_de_remanso_paso_a_paso` de V5 (criterio [A]
'remanso_derecho_via'), que T-7b nombro y dejo sin implementar (ficha T7B-01
de docs/decisiones_diferidas.md, con su correccion H2: el embalse a nivel
corta el FONDO y es una cota SUPERIOR de lo que la obra añade).

Lo que el metodo mide es lo que el embalse a nivel no puede dar: la distancia
aguas arriba de la boca hasta la que la obra ELEVA la lamina del cauce sobre
su tirante natural (el normal de Manning en la seccion del cauce de
aproximacion) en mas de una sobreelevacion admisible
('sobreelevacion_admisible_remanso_m', [A], ventana 0 a 0.30 m: el HDS-5 num.
2.2.5 b. describe ese aumento admisible, de 0 a 1 ft, como restriccion
regulatoria de EE. UU.). El perfil es el paso directo de VE-3.7
(`M3.perfil_remanso_trapecial`), con el HW de M4 como condicion de borde en
la boca:

    cauce suave  (y_n > y_c): M1 de HW a y_n + Δ (con Δ = 0, asintotica: no
                              hay distancia finita -> metodo no evaluable)
    cauce fuerte (y_n <= y_c): S1 de HW a max(conjugado de y_n, y_n + Δ), el
                              resalto; con HW bajo eso, el resalto queda en
                              la boca y la obra no remansa el cauce

    d = (L_boca + L_remanso)·cos(esviaje)  <=  ancho_derecho_via / 2

La seccion del cauce de aproximacion es un dato externo por punto nuevo,
`seccion_cauce_aproximacion`, con los cinco campos de `seccion_receptor_medida`.

VALIDACION CONTRA UN EJEMPLO RESUELTO PUBLICADO. En el repositorio de normas
no hay un remanso M1 resuelto paso a paso (VE-3.7 lo busco, y esta sesion
repaso HDS-5 en sus dos ediciones, HEC-14, el Manual de Hidrologia del MTC,
el USACE EM 1110-2-2902 y los casos reales). Lo que SI hay es la salida
impresa del programa 223-E3WSP del USBR («Design of Small Canal Structures»,
1978, Apendice C, pag. impresa 428, PDF 451): un perfil de lamina por la
ecuacion de la energia con la friccion de Manning promediada entre secciones,
que es el ESCALON del paso directo. El test comprueba que la energia y la
friccion del proyecto (`M3.energia_y_friccion_trapecial`, lo que el paso
directo usa en cada escalon) cierran el balance de cada tramo del perfil
publicado; la algebra del escalon y su suma ya estaban contrastadas contra
una integracion independiente (tests/test_ve3_remanso.py), y aqui se repite
sobre el metodo de V5.

SE ESCRIBIO EN ROJO PRIMERO, contra ec0306a.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest
from scipy.integrate import solve_ivp

from src import anticipo
from src import criterios_adoptados as ca
from src import modelos
from src import servicio
from src.constantes_fisicas import G
from src.modelos import (ControlGobernante, CriterioPendienteError,
                         DatoFaltanteError, DatoInvalidoError,
                         DerechoDeViaDelPunto, EstadoDeVerificacion,
                         MetodoNoEvaluableError, SeccionReceptor,
                         TipoDeVeredicto)
from src.modulos import M3_hidraulica as M3
from src.modulos import M5_verificaciones as M5
from src.normativa.registro import construir
from src.tolerancias import TOL_REL_PASO_DIRECTO_REMANSO
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.fixtures.casos_patron import CP_VE4C_USBR_WSP, CP_VE4C_V5

METODO = "perfil_de_remanso_paso_a_paso"
CRITERIO_DELTA = "sobreelevacion_admisible_remanso_m"
CLAVE_SECCION = "seccion_cauce_aproximacion"
CP = CP_VE4C_V5
SUAVE = SeccionReceptor(**CP["cauce_suave"])
FUERTE = SeccionReceptor(**CP["cauce_fuerte"])
Q = CP["Q"]
HW = CP["HW"]


def _referencia(seccion, y0, y1, Q=Q):
    """
    La longitud del remanso por una integracion INDEPENDIENTE de la ecuacion
    del flujo gradualmente variado, dx/dy = (1 - Fr^2) / (S - Sf), escrita
    aqui y no en el modulo (la misma que la de VE-3.7).
    """
    b, z, S, n = seccion.b_m, seccion.z_HV, seccion.S, seccion.n

    def dxdy(y, _x):
        A = (b + z * y) * y
        P = b + 2 * y * math.sqrt(1 + z * z)
        T = b + 2 * z * y
        Sf = (n * Q / (A * (A / P) ** (2 / 3))) ** 2
        Fr2 = Q * Q * T / (G * A ** 3)
        return [-(1 - Fr2) / (S - Sf)]

    sol = solve_ivp(dxdy, (y0, y1), [0.0], rtol=1e-11, atol=1e-12)
    return sol.y[0][-1]


# ===========================================================================
# 1. VALIDACION: el perfil publicado del USBR (223-E3WSP) cierra con la
#    energia y la friccion del proyecto
# ===========================================================================

FT = 0.3048                 # m por pie (definicion exacta)
W = CP_VE4C_USBR_WSP


def _energia_usbr_ft(fila):
    """
    (energia especifica en ft medida como el programa la imprime, Sf) de una
    seccion del perfil publicado, con las funciones del proyecto en SI.

    El programa, en un perfil de lamina («water surface profile»), toma la
    profundidad NORMAL a la solera y la distancia sobre la pendiente (listing,
    pag. impresa 413): su energia es z + D·cos(atan T) + V^2/2g. La del
    proyecto es y + V^2/2g con y vertical; se le quita D·(1 - cos) aqui, en el
    test, y no en el modulo, que trabaja en vertical (el modo «backwater
    curve» del mismo programa: «THE DEPTH OF WATER IS ASSUMED TO BE VERTICAL
    AND THE DISTANCE BETWEEN SECTIONS IS EQUAL TO THE HORIZONTAL DISTANCE»).
    La profundidad se reconstruye de la VELOCIDAD impresa (tres decimales
    en ft/s), que la fija con un error relativo de 2e-5; la impresa a tres
    decimales en ft lo haria con 1e-3.
    """
    D_ft = W["Q_cfs"] / (fila["ancho_ft"] * fila["V_fps"])
    E_m, Sf = M3.energia_y_friccion_trapecial(
        Q=W["Q_cfs"] * FT ** 3, b=fila["ancho_ft"] * FT, z=0.0, n=W["n"],
        y=D_ft * FT)
    coseno = math.cos(math.atan(fila["pendiente_solera"]))
    return E_m / FT - D_ft * (1 - coseno), Sf, D_ft


def test_la_profundidad_de_la_velocidad_impresa_es_la_profundidad_impresa():
    """La lectura de la tabla: D = Q / (W V) redondea a la D impresa."""
    for fila in W["filas"]:
        _, _, D = _energia_usbr_ft(fila)
        assert abs(D - fila["D_ft"]) <= W["tolerancia_D_ft"], fila


def test_cada_tramo_del_perfil_publicado_cierra_su_balance_de_energia():
    """
    z1 + E1 - L·(Sf1 + Sf2)/2 = z2 + E2, tramo por tramo, con L la distancia
    sobre la solera, como el programa (L9 = SQR((E2-E1)^2 + P^2)). El residuo
    de cada tramo, con la energia y la friccion del proyecto, cabe en la
    tolerancia del caso patron: el programa acepta cada seccion con +-0.005
    ft (lineas 4640-4650 del listing) y el tramo combina dos; las cifras
    impresas y la g de 32.16 ft/s^2 del programa añaden menos de 0.001 ft.
    """
    residuos = []
    previa = None
    for fila in W["filas"]:
        E, Sf, _ = _energia_usbr_ft(fila)
        if previa is not None:
            L = math.hypot(fila["estacion_ft"] - previa["estacion_ft"],
                           fila["solera_ft"] - previa["solera_ft"])
            hf = L * (Sf + previa["Sf"]) / 2
            residuo = (previa["solera_ft"] + previa["E"] - hf
                       - fila["solera_ft"] - E)
            residuos.append(residuo)
            assert abs(residuo) <= W["tolerancia_tramo_ft"], (
                previa["estacion_ft"], fila["estacion_ft"], residuo)
        previa = dict(fila, E=E, Sf=Sf)
    assert len(residuos) == len(W["filas"]) - 1


def test_una_friccion_mal_promediada_no_cierra_el_perfil_publicado():
    """
    PODER DE DISCRIMINACION: el balance no cierra con cualquier cosa. Con la
    friccion de la seccion de aguas arriba sola (sin promediar) el tramo de
    38+05 a 39+40 se descuadra en mas de diez veces la tolerancia.
    """
    filas = {f["estacion_ft"]: f for f in W["filas"]}
    a, b = filas[3805.0], filas[3940.0]
    Ea, Sfa, _ = _energia_usbr_ft(a)
    Eb, Sfb, _ = _energia_usbr_ft(b)
    L = math.hypot(b["estacion_ft"] - a["estacion_ft"],
                   b["solera_ft"] - a["solera_ft"])
    bien = a["solera_ft"] + Ea - L * (Sfa + Sfb) / 2 - b["solera_ft"] - Eb
    mal = a["solera_ft"] + Ea - L * Sfa - b["solera_ft"] - Eb
    assert abs(bien) <= W["tolerancia_tramo_ft"]
    assert abs(mal) > 10 * W["tolerancia_tramo_ft"]


def test_la_energia_y_la_friccion_son_las_del_paso_directo():
    """
    La funcion publica es la MISMA que el escalon de `perfil_remanso_
    trapecial`: un escalon unico entre dos tirantes da dx = (E1 - E2) /
    (S - Sf_medio) con ella.
    """
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    y0, y1 = HW, y_n + CP["delta_suave"]
    L, _ = M3.perfil_remanso_trapecial(Q=Q, seccion=SUAVE, y_inicio=y0,
                                       y_fin=y1, pasos=2)
    geo = dict(Q=Q, b=SUAVE.b_m, z=SUAVE.z_HV, n=SUAVE.n)
    E0, Sf0 = M3.energia_y_friccion_trapecial(y=y0, **geo)
    ym = y_n + (y0 - y_n) * ((y1 - y_n) / (y0 - y_n)) ** 0.5
    Em, Sfm = M3.energia_y_friccion_trapecial(y=ym, **geo)
    E1, Sf1 = M3.energia_y_friccion_trapecial(y=y1, **geo)
    a_mano = ((E0 - Em) / (SUAVE.S - (Sf0 + Sfm) / 2)
              + (Em - E1) / (SUAVE.S - (Sfm + Sf1) / 2))
    assert L == pytest.approx(a_mano, rel=REL_TRANSPORTE)


@pytest.mark.pdf
def test_las_cifras_del_caso_patron_estan_en_la_pagina_publicada():
    """La pagina impresa 428 (PDF 451) trae las cifras que el caso transcribe."""
    from src.normativa import fuentes
    from src.normativa.extraccion.pdf import texto_de_pagina

    ruta = fuentes.ruta_pdf(construir().fuente("USBR_DSCS"))
    texto = texto_de_pagina(ruta, W["pagina_pdf"])
    for cifra in W["cifras_en_la_pagina"]:
        assert cifra in texto, cifra


# ===========================================================================
# 2. M3: el remanso del cauce de aproximacion
# ===========================================================================

@pytest.mark.parametrize("delta", (0.30, 0.10, 0.01))
def test_cauce_suave_la_M1_hasta_el_normal_mas_delta(delta):
    r = M3.remanso_aguas_arriba(Q=Q, seccion=SUAVE, HW=HW,
                                sobreelevacion_admisible=delta)
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    assert r.suave and r.rama == modelos.RAMA_REMANSO_M1
    assert r.y_normal_m == pytest.approx(y_n, rel=REL_TRANSPORTE)
    assert r.y_fin_m == pytest.approx(y_n + delta, rel=REL_TRANSPORTE)
    assert r.longitud_m == pytest.approx(_referencia(SUAVE, HW, y_n + delta),
                                         rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert r.estaciones[0] == (0.0, HW)


def test_cauce_suave_una_delta_menor_alarga_el_remanso():
    largos = [M3.remanso_aguas_arriba(Q=Q, seccion=SUAVE, HW=HW,
                                      sobreelevacion_admisible=d).longitud_m
              for d in (0.30, 0.10, 0.01)]
    assert largos == sorted(largos)


def test_cauce_suave_con_delta_cero_la_M1_es_asintotica():
    r = M3.remanso_aguas_arriba(Q=Q, seccion=SUAVE, HW=HW,
                                sobreelevacion_admisible=0.0)
    assert r.longitud_m is None and r.asintotico


def test_sin_sobreelevacion_sobre_el_normal_mas_delta_no_hay_remanso():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    r = M3.remanso_aguas_arriba(Q=Q, seccion=SUAVE, HW=y_n + 0.05,
                                sobreelevacion_admisible=0.10)
    assert r.longitud_m == pytest.approx(0.0, abs=ABS_CERO)
    assert r.rama == modelos.RAMA_REMANSO_NINGUNA
    # Y con Δ = 0 tampoco, si la carga no supera el normal.
    r0 = M3.remanso_aguas_arriba(Q=Q, seccion=SUAVE, HW=y_n * 0.9,
                                 sobreelevacion_admisible=0.0)
    assert r0.longitud_m == pytest.approx(0.0, abs=ABS_CERO)
    assert not r0.asintotico


def test_cauce_fuerte_la_S1_hasta_el_resalto():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    r = M3.remanso_aguas_arriba(Q=Q, seccion=FUERTE, HW=HW,
                                sobreelevacion_admisible=0.0)
    assert not r.suave and r.rama == modelos.RAMA_REMANSO_S1
    assert r.y_conjugado_m == pytest.approx(y_j, rel=REL_TRANSPORTE)
    assert r.y_fin_m == pytest.approx(y_j, rel=REL_TRANSPORTE)
    assert r.longitud_m == pytest.approx(_referencia(FUERTE, HW, y_j),
                                         rel=TOL_REL_PASO_DIRECTO_REMANSO)


def test_cauce_fuerte_una_delta_mayor_que_el_salto_corta_la_S1_antes():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    delta = CP["delta_fuerte_grande"]
    assert y_n + delta > y_j
    r = M3.remanso_aguas_arriba(Q=Q, seccion=FUERTE, HW=HW,
                                sobreelevacion_admisible=delta)
    assert r.y_fin_m == pytest.approx(y_n + delta, rel=REL_TRANSPORTE)
    assert r.longitud_m == pytest.approx(_referencia(FUERTE, HW, y_n + delta),
                                         rel=TOL_REL_PASO_DIRECTO_REMANSO)


def test_cauce_fuerte_con_la_carga_bajo_el_conjugado_el_resalto_queda_en_la_boca():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    r = M3.remanso_aguas_arriba(Q=Q, seccion=FUERTE, HW=(y_n + y_j) / 2,
                                sobreelevacion_admisible=0.0)
    assert r.longitud_m == pytest.approx(0.0, abs=ABS_CERO)
    assert r.rama == modelos.RAMA_REMANSO_NINGUNA


# ===========================================================================
# 3. V5 con el metodo del perfil
# ===========================================================================

def _punto(esviaje=CP["esviaje"], S=CP["cauce_suave"]["S"]):
    return SimpleNamespace(id="A-01", esviaje_grados=esviaje,
                           exigir=lambda nombre: S)


def _resultado(HW_=HW, Q_=Q):
    return SimpleNamespace(HW=HW_, Q=Q_,
                           control_gobernante=ControlGobernante.ENTRADA)


def _derecho(ancho=CP["ancho_que_cumple"], seccion=SUAVE,
             semilongitud=CP["L_boca"]):
    return DerechoDeViaDelPunto(
        ancho_m=ancho, origen_ancho="dato externo de prueba",
        semilongitud_entrada_m=semilongitud,
        origen_semilongitud="semilongitud de entrada de 7.B (de prueba)",
        seccion_cauce=seccion,
        origen_seccion_cauce="dato externo de prueba",
        remanso_aguas_arriba=M3.remanso_aguas_arriba)


def _declarar(delta=CP["delta_suave"]):
    ca.establecer_valor_dinamico("remanso_derecho_via", METODO)
    if delta is not None:
        ca.establecer_valor_dinamico(CRITERIO_DELTA, delta)


def test_v5_perfil_sin_ancho_se_detiene_en_el_ancho():
    _declarar()
    with pytest.raises(DatoFaltanteError) as e:
        M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho(ancho=None))
    assert e.value.campo == "ancho_derecho_via_m"


def test_v5_perfil_sin_la_seccion_del_cauce_se_detiene_en_ella():
    _declarar()
    with pytest.raises(DatoFaltanteError) as e:
        M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho(seccion=None))
    assert e.value.campo == CLAVE_SECCION
    assert "--datos-externos" in str(e.value)


def test_v5_perfil_sin_la_sobreelevacion_admisible_se_detiene_en_el_criterio():
    _declarar(delta=None)
    with pytest.raises(CriterioPendienteError) as e:
        M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho())
    assert e.value.clave == CRITERIO_DELTA


def test_v5_perfil_el_dorado():
    """
    d = (L_boca + L_M1)·cos(esviaje), con L_M1 de la integracion
    independiente de HW a y_n + Δ; contra la mitad del ancho.
    """
    _declarar()
    v = M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho())
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    L = _referencia(SUAVE, HW, y_n + CP["delta_suave"])
    d = (CP["L_boca"] + L) * math.cos(math.radians(CP["esviaje"]))
    assert v.codigo == "V5" and v.criterio_aplicado == "remanso_derecho_via"
    assert v.valor_obtenido == pytest.approx(d, rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert v.valor_admisible == pytest.approx(CP["ancho_que_cumple"] / 2,
                                              abs=ABS_CERO)
    assert v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


def test_v5_perfil_puede_fallar_con_una_faja_estrecha():
    _declarar()
    v = M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho(ancho=CP["ancho_que_no"]))
    assert not v.cumple
    assert v.estado is EstadoDeVerificacion.NO_CUMPLE
    assert v.paso.veredicto.margen < 0


def test_v5_perfil_mide_menos_que_el_embalse_a_nivel_en_el_caso_patron():
    """
    Lo que la obra AÑADE (H2): en el caso patron el embalse a nivel, que
    corta el fondo, da mas del doble que el perfil sobre el tirante natural.
    """
    _declarar()
    perfil = M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                           derecho_de_via=_derecho()).valor_obtenido
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    nivel = M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                          derecho_de_via=_derecho()).valor_obtenido
    assert nivel > 2 * perfil


def test_v5_perfil_el_paso_lleva_la_seccion_el_regimen_y_sus_supuestos():
    _declarar()
    v = M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho())
    simbolos = [m.simbolo for m in v.paso.sustitucion]
    for s in ("HW", "Q", "b", "z", "n", "S", "y_n", "y_c", "Delta", "y_fin",
              "L_remanso", "L_boca", "esviaje", "ancho_derecho_via"):
        assert s in simbolos, s
    nota = v.paso.nota_del_proyecto.lower()
    for frase in ("tirante natural", "simetrica", "prismatic", "suave",
                  "carga de velocidad"):
        assert frase in nota, frase
    for cita in ("HDS5_3ED.2.2.5b#AUMENTO", "HDS5_3ED.3.5#PERFIL",
                 "HDS5_3ED.2.2.3a#SECCION_TIPICA", "DG2018.304.07.02"):
        assert cita in v.paso.citas_textuales, cita
    assert v.paso.umbral.cita_id == "DG2018.304.07.01"


def test_v5_perfil_en_cauce_fuerte_cuenta_la_S1_hasta_el_resalto():
    _declarar(delta=0.0)
    v = M5.v5_remanso(punto=_punto(S=FUERTE.S), resultado=_resultado(),
                      derecho_de_via=_derecho(seccion=FUERTE))
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    L = _referencia(FUERTE, HW, y_j)
    d = (CP["L_boca"] + L) * math.cos(math.radians(CP["esviaje"]))
    assert v.valor_obtenido == pytest.approx(d, rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert "S1" in v.paso.nota_del_proyecto


def test_v5_perfil_con_delta_cero_en_cauce_suave_no_da_cifra():
    _declarar(delta=0.0)
    with pytest.raises(MetodoNoEvaluableError) as e:
        M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho())
    assert str(e.value).startswith(
        modelos.MOTIVO_METODO_NO_EVALUABLE_REMANSO_PERFIL)
    assert "asintot" in str(e.value)


def test_v5_perfil_con_la_lamina_sobre_la_seccion_levantada_no_da_cifra():
    """
    La seccion prismatica representa el cauce hasta su `altura_total_m`: una
    carga en la boca por encima desborda el trapecio y el perfil sale del
    dominio del metodo.
    """
    _declarar()
    bajo = SeccionReceptor(**dict(CP["cauce_suave"], altura_total_m=HW * 0.9))
    with pytest.raises(MetodoNoEvaluableError) as e:
        M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho(seccion=bajo))
    assert str(e.value).startswith(
        modelos.MOTIVO_METODO_NO_EVALUABLE_REMANSO_PERFIL)
    assert "altura_total_m" in str(e.value)


def test_v5_perfil_sin_remanso_la_distancia_es_la_de_la_boca():
    _declarar(delta=CP["delta_suave"])
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    v = M5.v5_remanso(punto=_punto(), resultado=_resultado(HW_=y_n),
                      derecho_de_via=_derecho())
    d = CP["L_boca"] * math.cos(math.radians(CP["esviaje"]))
    assert v.valor_obtenido == pytest.approx(d, rel=REL_TRANSPORTE)
    assert v.cumple


def test_el_metodo_ya_no_se_detiene_por_no_estar_implementado():
    """
    REESCRIBE, declarandolo, el de T-7b (`test_v5_el_metodo_nombrado_y_no_
    implementado_no_da_cifra`): con todo declarado, el metodo da cifra.
    """
    _declarar()
    v = M5.v5_remanso(punto=_punto(), resultado=_resultado(),
                      derecho_de_via=_derecho())
    assert math.isfinite(v.valor_obtenido)


# ===========================================================================
# 4. El criterio y la cita
# ===========================================================================

def test_la_sobreelevacion_admisible_es_un_A_de_expediente_sin_valor():
    c = ca.CRITERIOS[CRITERIO_DELTA]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert c.valor is None and not c.opcional
    assert tuple(c.sensibilidad) == (0.0, 0.30)
    assert c.resolucion is not None
    assert "2.2.5" in c.fuente
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CRITERIO_DELTA, 0.5)


def test_el_metodo_del_remanso_sigue_sin_valor_de_archivo():
    """Con los datos de archivo nada cambia."""
    assert ca.CRITERIOS["remanso_derecho_via"].valor is None
    assert ca.CRITERIOS[CRITERIO_DELTA].valor is None


def test_las_citas_nuevas_estan_en_el_registro():
    reg = construir()
    aumento = reg.cita("HDS5_3ED.2.2.5b#AUMENTO")
    assert "0 to 1 ft (0.3 m)" in aumento.texto_literal.texto
    assert aumento.pagina_pdf == 72
    tipica = reg.cita("HDS5_3ED.2.2.3a#SECCION_TIPICA")
    assert "typical cross section" in tipica.texto_literal.texto
    assert tipica.pagina_pdf == 68
    assert reg.fundamento("F5.V5_PERFIL")


# ===========================================================================
# 5. El dato externo nuevo y el pre-vuelo
# ===========================================================================

def _externos(tmp_path, puntos=None, globales=None):
    import json
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"globales": globales or {},
                                "puntos": puntos or {}}), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {})


def test_la_seccion_del_cauce_es_un_dato_externo_por_punto(tmp_path):
    assert CLAVE_SECCION in servicio.CLAVES_EXTERNAS
    assert CLAVE_SECCION in servicio.CLAVES_OBJETO
    assert CLAVE_SECCION in servicio.CLAVES_DE_V5_Y_V8
    assert {f.value for f in servicio.FAMILIAS_QUE_USAN[CLAVE_SECCION]} == \
        {"A", "B"}
    assert servicio.METODO_QUE_EXIGE_LA_CLAVE[CLAVE_SECCION] == (METODO,)
    assert METODO in servicio.METODO_QUE_EXIGE_LA_CLAVE["ancho_derecho_via_m"]
    ext = _externos(tmp_path, puntos={"A-01": {CLAVE_SECCION:
                                               CP["cauce_suave"]}})
    assert ext.valor("A-01", CLAVE_SECCION) == CP["cauce_suave"]


@pytest.mark.parametrize("malo", [
    {"b_m": 1.0, "z_HV": 1.5, "S": 0.006, "n": 0.035},          # falta uno
    dict(CP["cauce_suave"], otro=1.0),                           # sobra uno
    dict(CP["cauce_suave"], n=0.0), dict(CP["cauce_suave"], S=-0.01),
    dict(CP["cauce_suave"], b_m=0.0, z_HV=0.0),
    dict(CP["cauce_suave"], S=6.0), "trapecio", [1, 2, 3],
])
def test_una_seccion_del_cauce_que_no_puede_ser_no_entra(tmp_path, malo):
    with pytest.raises(DatoInvalidoError):
        _externos(tmp_path, puntos={"A-01": {CLAVE_SECCION: malo}})


def test_el_prevuelo_pide_la_seccion_solo_con_el_metodo_del_perfil():
    from pathlib import Path
    csv = Path(__file__).resolve().parents[1] / "tests" / "ejemplo_puntos.csv"
    externos = servicio.cargar_datos_externos(None, {})
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    faltas = {(f.id_punto, f.dato) for f in anticipo.datos_faltantes_por_punto(
        csv, externos, servicio.ALCANCE_EXPEDIENTE)}
    assert not {d for _, d in faltas if d == CLAVE_SECCION}
    ca.establecer_valor_dinamico("remanso_derecho_via", METODO)
    faltas = anticipo.datos_faltantes_por_punto(
        csv, externos, servicio.ALCANCE_EXPEDIENTE)
    por_dato = {}
    for f in faltas:
        por_dato.setdefault(f.dato, set()).add(f.id_punto)
    assert por_dato[CLAVE_SECCION] == {"A-01", "A-02", "B-01"}
    assert por_dato["ancho_derecho_via_m"] == {"A-01", "A-02", "B-01"}
    assert "cota_afectacion_aguas_arriba_msnm" not in por_dato
    a_perfil = anticipo.datos_faltantes_por_punto(
        csv, externos, servicio.ALCANCE_PERFIL)
    assert not [f for f in a_perfil if f.dato == CLAVE_SECCION]


# ===========================================================================
# 6. De punta a punta
# ===========================================================================

@pytest.mark.lento
def test_A01_con_el_perfil_de_remanso_de_punta_a_punta(tmp_path):
    """
    A `--alcance expediente`, con el metodo del perfil y la seccion del cauce
    de prueba de A-01, V5 se evalua por el perfil: el paso es el del metodo y
    la distancia es la del dorado con el HW y la L_boca que el paso imprime.
    """
    from tests.test_t7b_cabezal_estabilidad import _correr_de_prueba
    _, a01 = _correr_de_prueba(
        tmp_path, metodo_v5=METODO, cota_afectacion=None,
        ancho=CP["ancho_que_cumple"],
        extra_a01={CLAVE_SECCION: CP["cauce_suave"]},
        declaraciones={CRITERIO_DELTA: CP["delta_suave"]})
    v5 = next(v for v in a01.traza[0].verificaciones if v.codigo == "V5")
    m = {x.simbolo: x.valor for x in v5.paso.sustitucion}
    assert m["b"] == CP["cauce_suave"]["b_m"]
    y_n = M3.tirante_normal_trapecial(Q=m["Q"], seccion=SUAVE)
    L = _referencia(SUAVE, m["HW"], y_n + CP["delta_suave"], Q=m["Q"])
    d = (m["L_boca"] + L) * math.cos(math.radians(m["esviaje"]))
    assert v5.valor_obtenido == pytest.approx(
        d, rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert v5.estado is EstadoDeVerificacion.CUMPLE
