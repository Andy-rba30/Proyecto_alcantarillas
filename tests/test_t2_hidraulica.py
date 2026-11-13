# -*- coding: utf-8 -*-
"""
tests/test_t2_hidraulica.py
===========================
La aceptacion de T-2 de la cadena T (`docs/planes_mejora/
09_CADENA_PROMPTS_TESIS.md`): los cierres de metodo de la hidraulica.

    1. Pendiente del barril   INF-5.1.6, INF-3.2.7   S = 0 admitido en M3 y M4
                                                     (barril horizontal, HDS-5
                                                     num. 3.3.4); V10 con la
                                                     banda [A] de pendiente.
    2. Borde libre            INF-3.2.6              V1 separa «lleno por el
                                                     caudal» de «lleno por el
                                                     receptor» ([A]
                                                     borde_libre_bajo_tw_
                                                     ahogante).
    3. Tailwater              INF-3.2.8              la via 4 dice «seccion
                                                     adoptada [A]» y avisa; la
                                                     seccion MEDIDA del
                                                     receptor entra y gana.
    4. Cartas de aleros       INF-3.2.2              filas de las Cartas 1, 2,
                                                     3 y 13 de la Tabla A.1,
                                                     valor a valor contra la
                                                     pagina.
    5. Validacion externa     INF-3.2.2              los ejemplos DG 1.3 y DG
                                                     1.4 del HDS-5 como dorado
                                                     (`CP_HDS5_DG1`).
    6. Criterios con respaldo INF-0.5                regimen_v2b,
                                                     hw_entrada_fuera_de_rango
                                                     y el acceso de
                                                     mantenimiento.
    7. Receptor seco          INF-5.1.7              Q_receptor_m3s = 0.

EL ORACULO DE CADA TEST ES LA FUENTE O UN INVARIANTE, nunca la salida del
programa: una frase del HDS-5 con su pagina (el +0.01 del num. 3.3.4, la
tabla A.1 de la PDF 197, los formularios DG 1), una identidad de la fisica
(el balance de energia del perfil, Manning en el receptor) o la ficha de un
criterio. Donde un numero es del programa --el diametro de la linea base--
el test fija que NO SE MUEVE, que es la parada (c) de la cadena.

ESTOS TESTS NO SE ESCRIBIERON EN ROJO ANTES DEL CODIGO, y se dice: la sesion
de T-2 implemento primero y escribio la aceptacion despues. Lo que si se
MIDIO es cuantos son rojos sobre el arbol anterior (`87d1ce7`, T-0), con los
nombres que ese arbol no tiene sustituidos por un marcador para que el
archivo se recolecte: la medida, con los que valen antes y despues y por
que, esta en la ficha T2-07 de `docs/decisiones_diferidas.md`.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import barrido
from src import criterios_adoptados as ca
from src import editores as ed
from src import servicio
from src import variables_entrada as ve
from src.constantes_fisicas import G
from src.constantes_normativas import (CARTAS_CAJON_TA1, HDS5_INLET,
                                       KE_HDS5_C2, K_FRICCION_SI,
                                       UMBRALES_POR_CODIGO, Y_SOBRE_D_MAX)
from src.modelos import (AVISO_SIN_ACCESO_DE_MANTENIMIENTO, ConstantesHDS5,
                         ControlGobernante, DatoInvalidoError, RegimenBarril,
                         SECCION_RECEPTOR_ADOPTADA, SECCION_RECEPTOR_MEDIDA,
                         SeccionCircular, SeccionReceptor, SeccionRectangular,
                         SinTiranteNormal, TipoDePerfil, TipoDeVeredicto,
                         TipoMaterial, TiranteNormal, ViaDelTW)
from src.modulos import M0_carga as M0
# T-1 (integrado detras de T-2 y T-4): todo punto de Familia A o B con el
# caudal DECLARADO lleva un aviso permanente --el criterio FEN no lo alcanza--
# y sale por `InformePunto.avisos()` con los demas. Los tests de abajo que
# decian «sin avisos» dicen ahora «sin mas aviso que ese».
from src.modulos.MH_hidrologia import (
    AVISO_FEN_DEL_CAUDAL_DECLARADO as AVISO_DEL_CAUDAL_DECLARADO)
from src.modulos import M3_hidraulica as M3
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from src.modulos.M2_material import catalogo
from src.normativa import fuentes
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor
from tests.fixtures.casos_patron import (CP_HDS5_DG1, PIE_EN_METROS,
                                         PULGADA_EN_METROS)
from tests.test_M5_verificaciones import _punto, _resultado

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

# Tolerancias de este archivo, nombradas (CLAUDE.md; `tests/apoyo/
# aproximacion.py`). Las dos de la validacion externa viven en el fixture.
REL_FORMULA = 1e-9        # una formula cerrada recomputada en el test
REL_PERFIL = 1e-6         # el balance de energia entre dos estaciones del perfil
ABS_BRENT = 1e-7          # una raiz de Brent contra su identidad (xtol 1e-10)


# LOS MUTANTES QUE QUEDAN VIVOS, UNO A UNO (ficha T2-07). Medidos con el arnes
# de EXT-11 (`tests/apoyo/mutacion.py`) sobre veinte funciones tocadas por T-2
# --`v1_borde_libre`, `v10_pendiente_conducto`, `limites_de_pendiente`,
# `_lectura_bajo_tw_ahogante`, `_velocidad_de_v3`, `_regimen_de_v1_v2` (M5);
# `seccion_del_receptor`, `tirante_normal_trapecial`, `resolver_manning`,
# `_validar_parametros`, `_de_la_seccion` (M3); `_validar_pendiente`,
# `velocidad_de_salida` (M4); `y_sobre_D`, `sin_tirante_normal` (modelos);
# `_seccion_receptor_externa`, `_booleano_externo`, `_numero_externo`,
# `con_aviso`, `avisos` (servicio)-- contra este archivo y los de M3, M5,
# EXT-1, EXT-3 y las propiedades de EXT-11: 283 mutantes, 254 muertos, y uno
# mas con un test añadido despues de la medida. Cada entrada: (funcion,
# mutante, clase). No se comprueban contra el arnes en cada corrida --el
# censo que si lo hace es el de EXT-11, y ampliarlo es de T-10--; lo que se
# fija es que la lista no crezca ni pierda su clase en silencio.
BANDA = "banda de tolerancia de un umbral: solo difiere en la igualdad exacta umbral +- 1e-9"
SIN_CASO = "guardia o corchete sin caso que la distinga"
TEXTO = "texto o formato de la memoria o de un mensaje"
SIN_CONSTRUIR = "ningun camino del programa construye el caso"
OTRO_ARCHIVO = "muere con otro archivo de la suite (medido aparte contra los objetivos de EXT-11)"
MUTANTES_VIVOS_DE_T2 = (
    ("v1_borde_libre", "y_sobre_D <= max + TOL -> <", BANDA),          # ya censado en EXT-11
    ("v1_borde_libre", "TW / D <= max + TOL -> <", BANDA),
    ("v1_borde_libre", "y_propio / D <= max + TOL -> <", BANDA),
    ("v1_borde_libre", "y < D - TOL -> <=", BANDA),
    ("v1_borde_libre", "y > TW + TOL -> >=", BANDA),
    ("v1_borde_libre", "max + TOL -> max - TOL (2.a aparicion)", BANDA),
    ("v1_borde_libre", "max + TOL -> max - TOL (3.a aparicion)", BANDA),
    ("v10_pendiente_conducto", "S >= s_min - TOL -> >", BANDA),
    ("v10_pendiente_conducto", "S <= s_max + TOL -> <", BANDA),
    ("velocidad_de_salida", "y_salida < D - TOL -> <=", BANDA),          # censado
    ("velocidad_de_salida", "TW > y_c -> >=", BANDA),                    # censado
    ("velocidad_de_salida", "TW < altura - TOL -> <=", BANDA),           # censado
    ("velocidad_de_salida", "altura - TOL -> altura + TOL", BANDA),      # censado
    ("velocidad_de_salida", "D - TOL -> D + TOL", BANDA),
    ("velocidad_de_salida", "A > 0 -> A >= 0", SIN_CASO),                # censado
    ("tirante_normal_trapecial", "semilla del corchete 1.0 -> 2.0", SIN_CASO),   # censado
    ("tirante_normal_trapecial", "duplicacion del corchete 2 -> 3", SIN_CASO),   # censado
    ("tirante_normal_trapecial", "f(y_hi) > 0 -> >= 0", SIN_CASO),               # censado
    ("tirante_normal_trapecial", "f(y_hi) > 0 -> > 1", SIN_CASO),
    ("v1_borde_libre", "cifras de la magnitud TW: TW is not None -> is None", TEXTO),
    ("v1_borde_libre", "rotulo del umbral: 1 - max -> 1 + max", TEXTO),
    ("v1_borde_libre", "rotulo del umbral: 1 -> 2", TEXTO),
    ("_seccion_receptor_externa", "separador del mensaje: faltan and sobran -> or", TEXTO),
    ("_numero_externo", "indice de techo[0] en el mensaje: 0 -> 1", TEXTO),
    ("_numero_externo", "indice de techo[1] en el mensaje: 1 -> 2", TEXTO),
    ("InformePunto.avisos", "paso is not None and veredicto is not None -> or",
     SIN_CONSTRUIR),
    ("ResultadoPunto.y_sobre_D", "resultado_hidraulico is None or seccion is None -> and",
     SIN_CONSTRUIR),
    ("_numero_externo", "valor >= techo[0] -> >", OTRO_ARCHIVO),
)


def test_el_censo_de_mutantes_vivos_de_t2_dice_cuantos_y_de_que_clase():
    """La lista de la ficha T2-07: 28, sin repetidos y cada uno con su clase."""
    assert len(MUTANTES_VIVOS_DE_T2) == len(set(MUTANTES_VIVOS_DE_T2)) == 28
    por_clase = {}
    for _funcion, _mutante, clase in MUTANTES_VIVOS_DE_T2:
        por_clase[clase] = por_clase.get(clase, 0) + 1
    assert por_clase == {BANDA: 14, SIN_CASO: 5, TEXTO: 6, SIN_CONSTRUIR: 2,
                         OTRO_ARCHIVO: 1}


@pytest.fixture(autouse=True)
def _limpio():
    """Ningun test deja una declaracion en caliente para el siguiente."""
    yield
    for clave in ("borde_libre_bajo_tw_ahogante", "pendiente_minima_conducto",
                  "pendiente_maxima_conducto", "regimen_v2b",
                  "hw_entrada_fuera_de_rango", "embocadura_cajon"):
        ca.quitar_valor_dinamico(clave)


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


def _externos(tmp_path, contenido, **banderas):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, banderas)


def _correr(tmp_path, contenido, *, csv=CSV, alcance="perfil", luz=2.75):
    externos = _externos(tmp_path, contenido, luz_m=luz)
    return servicio.correr(csv, externos, alcance)


def _punto_de(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def _avisos_sin_geometria(punto):
    """
    Los avisos del punto sin los de la geometria de 7.B NI los de la Fase 6.

    T-6 (integrado detras de T-1) los saca por `InformePunto.avisos()` como a
    los demas: el fondo de entrada adoptado igual al terreno y la plataforma
    tomada horizontal acompañan a todo punto del ejemplo. T-8 hace lo mismo
    con los de la Fase 6 (terreno del cauce, lecho, contraste con HEC-14),
    que salen en todo punto dimensionado. Los tests de abajo que fijan la
    tupla ENTERA la fijan sin ellos --tienen su test en `test_t6_geometria`
    y en `test_t8_proteccion`--, para seguir diciendo lo que decian: que T-2
    no añade ningun aviso mas que los suyos. Los de la Fase 6 se restan por
    pieza, no por texto.
    """
    otros = set(punto.avisos_de_geometria())
    for pieza in (punto.proteccion, punto.proteccion_entrada, punto.socavacion):
        if pieza is not None:
            otros |= set(pieza.avisos)
    return tuple(a for a in punto.avisos() if a not in otros)


def _verificacion(informe_punto, codigo):
    return next(v for _f, v in informe_punto.verificaciones()
                if v.codigo == codigo)


# ===========================================================================
# 1 · Pendiente del barril: S = 0 se admite (INF-5.1.6)
# ===========================================================================

def test_m3_devuelve_sin_tirante_normal_con_S_cero(concreto):
    """
    HDS-5 num. 3.3.4 (pag. impresa 3.25): los procedimientos «can be
    reasonably applied to culverts with no slope (horizontal)». Con S = 0
    Manning no tiene solucion y M3 lo DICE con un objeto propio: ni una
    excepcion (el dato es valido) ni `None` (no es «el escalon no alcanza»).
    """
    normal = M3.resolver_manning(SeccionCircular(0.90), Q=0.6, S=0.0,
                                 material=concreto)
    assert isinstance(normal, SinTiranteNormal)
    assert not isinstance(normal, TiranteNormal)
    assert normal.S == pytest.approx(0.0, abs=ABS_CERO)
    # Y con una pendiente positiva sigue devolviendo lo de siempre.
    assert isinstance(M3.resolver_manning(SeccionCircular(0.90), Q=0.6,
                                          S=0.006, material=concreto),
                      TiranteNormal)


def test_el_tirante_normal_de_un_solo_n_no_existe_con_S_cero(concreto):
    """La pieza de un solo n: ningun tirante transporta Q en flujo uniforme."""
    assert M3.tirante_normal(SeccionCircular(0.90), Q=0.6, S=0.0,
                             n=concreto.n_para_capacidad) is None


@pytest.mark.parametrize("S_mala", [-0.001, -1.0, float("nan")])
def test_la_pendiente_negativa_o_nan_sigue_siendo_dato_invalido(S_mala, concreto):
    """
    La guardia MAT-D13 queda SOLO contra S < 0 (y NaN): la pendiente adversa
    no se admite. Las cuatro puertas, no una.
    """
    sec = SeccionCircular(0.90)
    hds5 = concreto.hds5
    critico = M4.tirante_critico(0.6, sec)
    llamadas = (
        lambda: M3.resolver_manning(sec, Q=0.6, S=S_mala, material=concreto),
        lambda: M4.control_entrada(0.6, sec, S_mala, hds5, critico),
        lambda: M4.control_salida(0.6, sec, S_mala, 20.0, 0.0,
                                  concreto.n_para_capacidad, critico=critico),
        lambda: M4.perfil_lamina(Q_celda=0.6, seccion=sec, S=S_mala, L=20.0,
                                 TW=0.0, n=concreto.n_para_capacidad, ke=0.5,
                                 critico=critico, HW_aproximado=0.8),
    )
    for llamada in llamadas:
        with pytest.raises(DatoInvalidoError) as exc:
            llamada()
        assert exc.value.campo == "S"


def test_el_control_de_entrada_con_S_cero_no_lleva_correccion(concreto):
    """
    Forma 1 no sumergida, ec. (A.1): HWi/D = H_c/D + K (q*)^M + Ks S. Con
    S = 0 queda H_c/D + K (q*)^M, recomputado aqui con las constantes de la
    carta.
    """
    sec, Q = SeccionCircular(1.20), 0.6        # q* < 3.5: rama no sumergida
    hds5 = concreto.hds5
    critico = M4.tirante_critico(Q, sec)
    entrada = M4.control_entrada(Q, sec, 0.0, hds5, critico)
    q = M4.caudal_adimensional(Q, sec)
    assert q < 3.5
    esperado = critico.H_c / sec.altura + hds5.K * q ** hds5.M
    assert entrada.HW_sobre_D == pytest.approx(esperado, rel=REL_FORMULA)
    assert entrada.piso is None


@pytest.mark.parametrize("Q", [0.6, 2.2])       # no sumergido y sumergido
def test_la_regla_del_0_01_del_hds5_para_el_barril_horizontal(Q, concreto):
    """
    HDS-5 num. 3.3.4 (pag. impresa 3.25, PDF 107): «For horizontal slopes,
    0.01 should be added to the HW/D obtained from the nomograph», y el
    nomograma esta trazado al 2 % (num. A.3). O sea: HW/D(S = 0) - HW/D(S =
    0.02) = 0.01, que es 0.5 x 0.02. El motor resuelve la ecuacion y tiene
    que dar exactamente esa diferencia.
    """
    sec = SeccionCircular(1.20)
    critico = M4.tirante_critico(Q, sec)
    horizontal = M4.control_entrada(Q, sec, 0.0, concreto.hds5, critico)
    al_dos = M4.control_entrada(Q, sec, 0.02, concreto.hds5, critico)
    assert horizontal.HW_sobre_D - al_dos.HW_sobre_D == pytest.approx(
        0.01, rel=REL_FORMULA)


def test_el_control_de_salida_con_S_cero_es_H_mas_h_o(concreto):
    """HW = H + h_o - S L con S = 0: la caida desaparece y H no cambia."""
    sec, Q, L = SeccionCircular(0.90), 0.6, 20.0
    n = concreto.n_para_capacidad
    plano = M4.control_salida(Q, sec, 0.0, L, 0.0, n)
    tendido = M4.control_salida(Q, sec, 0.01, L, 0.0, n)
    assert plano.caida == pytest.approx(0.0, abs=ABS_CERO)
    assert plano.HW == pytest.approx(plano.H + plano.h_o, rel=REL_FORMULA)
    assert plano.H == pytest.approx(tendido.H, rel=REL_FORMULA)


def test_el_perfil_de_un_barril_horizontal_es_un_H2_que_cierra_la_energia(concreto):
    """
    El perfil sobre fondo horizontal (HDS-5 3.5.1: «the horizontal profiles
    of H2 and H3») sube aguas arriba desde el tirante critico, sin asintota.
    El oraculo es el BALANCE DE ENERGIA recomputado aqui, estacion a
    estacion, con la Ec. 3.7 y sin llamar a M4: E_arriba - E_abajo =
    Sf_medio dx (S = 0).
    """
    sec, Q, L = SeccionCircular(0.90), 0.6, 20.0
    n = concreto.n_para_capacidad
    critico = M4.tirante_critico(Q, sec)
    perfil = M4.perfil_lamina(Q_celda=Q, seccion=sec, S=0.0, L=L, TW=0.0, n=n,
                              ke=0.5, critico=critico, HW_aproximado=0.8)
    assert perfil.tipo is TipoDePerfil.H2
    assert perfil.alcanza_entrada and perfil.y_asintota_m is None
    assert perfil.y_salida_m == pytest.approx(critico.y_c, rel=REL_FORMULA)
    tirantes = [y for _x, y in perfil.estaciones]
    assert all(b > a for a, b in zip(tirantes, tirantes[1:])), (
        "sobre fondo horizontal la lamina sube monotona hacia la entrada")
    assert perfil.estaciones[-1][0] == pytest.approx(L, rel=REL_FORMULA)

    def energia_y_friccion(y):
        A, R = sec.area(y), sec.area(y) / sec.perimetro(y)
        V = Q / A
        return (y + V ** 2 / (2 * G),
                K_FRICCION_SI * n ** 2 * V ** 2 / (R ** (4 / 3) * 2 * G))

    for (x0, y0), (x1, y1) in zip(perfil.estaciones, perfil.estaciones[1:]):
        E0, Sf0 = energia_y_friccion(y0)
        E1, Sf1 = energia_y_friccion(y1)
        assert E1 - E0 == pytest.approx((Sf0 + Sf1) / 2 * (x1 - x0),
                                        rel=REL_PERFIL)
    # La carga a la entrada: la linea de energia mas la perdida de entrada.
    y_e, V_e = perfil.y_entrada_m, perfil.V_entrada_m_s
    assert perfil.HW_remanso_m == pytest.approx(
        y_e + (1 + 0.5) * V_e ** 2 / (2 * G), rel=REL_FORMULA)


def test_el_resultado_de_un_barril_horizontal_no_inventa_el_tirante_normal(concreto):
    """
    Lo que no existe va en None, no en un sustituto; y la velocidad de salida
    es la de HDS-5 3.1.6 (Q / A(y_c) con salida libre) cualquiera que sea el
    control.
    """
    sec, Q = SeccionCircular(0.90), 0.6
    r = M4.resolver_control(sec, Q=Q, S=0.0, L=20.0, TW=0.0, material=concreto)
    assert r is not None and r.sin_tirante_normal
    assert r.y_normal is None and r.V_erosion is None
    assert r.V_sedimentacion is None
    assert r.perfil.tipo is TipoDePerfil.H2
    critico = M4.tirante_critico(Q, sec)
    assert r.V_salida.valor == pytest.approx(Q / critico.geometria.A,
                                             rel=REL_FORMULA)
    assert r.y_salida_m == pytest.approx(critico.y_c, rel=REL_FORMULA)
    # El paso 4.1 es el del barril horizontal y cita el num. 3.3.4.
    paso_41 = next(p for p in r.pasos if p.fundamento_id == "F4.HORIZONTAL")
    assert "HDS5_3ED.3.3.4#HORIZONTAL" in paso_41.citas_textuales
    assert not any(p.fundamento_id == "F4.MANNING" for p in r.pasos)
    # Y con pendiente positiva el resultado sigue teniendo los tres.
    tendido = M4.resolver_control(sec, Q=Q, S=0.006, L=20.0, TW=0.0,
                                  material=concreto)
    assert not tendido.sin_tirante_normal and tendido.y_normal > 0
    assert any(p.fundamento_id == "F4.MANNING" for p in tendido.pasos)


def test_v1_v2_y_v3_de_un_barril_horizontal_leen_el_perfil_y_la_salida(concreto):
    """
    Sin flujo uniforme: V1 juzga el tirante maximo del perfil, V2 su
    velocidad minima y V3 la velocidad de la seccion de salida, que sobre un
    fondo horizontal es la mayor del barril.
    """
    sec = SeccionCircular(1.20)
    r = M4.resolver_control(sec, Q=0.6, S=0.0, L=20.0, TW=0.0,
                            material=concreto)
    v1 = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                           resultado=r)
    v2 = M5.v2_velocidad_minima(resultado=r)
    v3 = M5.v3_velocidad_maxima(material=concreto, resultado=r)
    assert v1.valor_obtenido == pytest.approx(r.perfil.y_max_m / sec.altura,
                                              rel=REL_FORMULA)
    assert v2.valor_obtenido == pytest.approx(r.perfil.V_min_m_s,
                                              rel=REL_FORMULA)
    assert v3.valor_obtenido == pytest.approx(r.V_salida.valor,
                                              rel=REL_FORMULA)
    assert v3.valor_obtenido > v2.valor_obtenido
    assert v3.paso.sustitucion[0].simbolo == "V_salida"


def test_un_punto_con_barril_horizontal_dimensiona_por_la_corrida(tmp_path):
    """
    De punta a punta: `S_conducto = 0` por --datos-externos. El punto
    dimensiona, la memoria dice H2, V2b AVISA (el conducto queda mas plano
    que su cauce) y V10 cumple con la banda de archivo. El tubo que sale NO
    es menor que el del mismo punto con su pendiente natural.
    """
    plano = _correr(tmp_path, {"globales": {"TW_m": 0.3},
                               "puntos": {"A-01": {"S_conducto": 0.0}}})
    a01 = _punto_de(plano, "A-01")
    assert a01.dimensionado
    h = a01.resultado.resultado_hidraulico
    assert h.sin_tirante_normal and h.perfil.tipo is TipoDePerfil.H2
    assert _verificacion(a01, "V10").cumple
    v2b = _verificacion(a01, "V2b")
    assert v2b.cumple and v2b.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    natural = _punto_de(_correr(tmp_path, {"globales": {"TW_m": 0.3}}), "A-01")
    assert a01.resultado.seccion.altura >= natural.resultado.seccion.altura
    # Las tres salidas lo dicen sin reventar en el None.
    volcado = cli.informe_json(plano)
    diseno = next(p for p in volcado["puntos"] if p["id"] == "A-01")["diseno"]
    assert diseno["y_normal_m"] is None and diseno["V_erosion_m_s"] is None
    assert diseno["perfil_tipo"] == "H2"
    assert "BARRIL HORIZONTAL" in cli.volcar(plano)


def test_S_conducto_externo_admite_el_cero_y_S_cauce_no(tmp_path):
    """
    El cero de `S_conducto` es el centinela del barril horizontal, como el
    de `TW_m` es el de la salida libre. La pendiente del CAUCE no lo admite:
    es una medicion que T-2 no toca.
    """
    externos = _externos(tmp_path, {"puntos": {"A-01": {"S_conducto": 0.0,
                                                         "TW_m": 0.0}}})
    assert externos.valor("A-01", "S_conducto") == pytest.approx(0.0, abs=ABS_CERO)
    for mala in ({"S_conducto": -0.001}, {"S_cauce": 0.0}, {"luz_m": 0.0}):
        with pytest.raises(DatoInvalidoError):
            _externos(tmp_path, {"globales": mala})


# ===========================================================================
# 1-bis · V10 y los dos criterios de pendiente (INF-3.2.7)
# ===========================================================================

@pytest.mark.parametrize("clave, valor, ventana", [
    ("pendiente_minima_conducto", 0.0, (0.0, 0.005)),
    ("pendiente_maxima_conducto", 0.10, (0.02, 0.10)),
])
def test_las_fichas_de_los_dos_criterios_de_pendiente(clave, valor, ventana):
    """[A] de perfil, con valor, ventana, procedencia y las citas verificadas."""
    c = ca.criterio(clave)
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_FLOAT
    assert c.valor == pytest.approx(valor, abs=ABS_CERO)
    assert tuple(c.sensibilidad) == pytest.approx(ventana, rel=REL_TRANSPORTE)
    assert c.resolucion is not None and c.justificacion and c.reemplazado_por
    assert "MC_HHD.4.1.1.3.3" in c.fuente or "4.1.1.3.3" in c.fuente
    # La puerta rechaza lo que cae fuera de la ventana.
    for fuera in (ventana[0] - 0.001, ventana[1] + 0.001):
        with pytest.raises(ValueError):
            ca.verificar_declaracion(clave, fuera)


def test_un_barril_horizontal_gobernado_por_la_entrada(concreto):
    """
    El caso que la revision adversarial encontro sin test: S = 0 con el
    control de ENTRADA dando la mayor carga (un barril corto con caudal
    alto). Tres ramas del codigo solo se recorren aqui:

      * `M4.velocidad_de_salida`: sin tirante normal no puede devolver la
        velocidad uniforme aunque gobierne la entrada; devuelve la de la
        seccion de salida, Q/A(y_c) con el TW bajo el critico;
      * `M5._regimen_de_v1_v2`: V1 y V2 van por el perfil, no por Manning;
      * `ResultadoPunto.y_sobre_D`: el llenado del resumen es el del perfil.

    Sin esas tres ramas el caso revienta con un error de programa
    (`AttributeError` o `TypeError` sobre un `None`), fuera de
    `ErrorProyecto`.
    """
    from src.modelos import ResultadoPunto
    sec = SeccionCircular(0.90)
    Q = 1.5
    r = M4.resolver_control(sec, Q=Q, S=0.0, L=12.0, TW=0.0, material=concreto)
    assert r.sin_tirante_normal and r.y_normal is None
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.HW_entrada > r.HW_salida
    assert r.HW == pytest.approx(r.HW_entrada, rel=REL_TRANSPORTE)
    assert r.perfil is not None and r.perfil.tipo is TipoDePerfil.H2
    # La velocidad de salida es la del tirante critico, y M4 lo calcula con
    # el area critica que el paso 4.2 ya resolvio.
    critico = M4.tirante_critico(Q, sec)
    assert r.V_salida.valor == pytest.approx(Q / critico.geometria.A,
                                             rel=REL_FORMULA)
    assert "HORIZONTAL" in r.V_salida.procedencia
    # V1 y V2 sobre el perfil.
    v1 = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                           resultado=r)
    assert v1.valor_obtenido == pytest.approx(r.perfil.y_max_m / sec.altura,
                                              rel=REL_FORMULA)
    assert not v1.cumple       # y_max/D ~ 0.99: el caudal casi llena el tubo
    v2 = M5.v2_velocidad_minima(resultado=r)
    assert v2.valor_obtenido == pytest.approx(r.perfil.V_min_m_s,
                                              rel=REL_FORMULA)
    v3 = M5.v3_velocidad_maxima(material=concreto, resultado=r)
    assert v3.valor_obtenido == pytest.approx(r.V_salida.valor, rel=REL_FORMULA)
    # Y el llenado que publica el resumen del punto.
    punto_resuelto = ResultadoPunto(
        punto=_punto(), aceptado=True, material=concreto, seccion=sec,
        resultado_hidraulico=r, verificaciones=(v1, v2, v3))
    assert punto_resuelto.y_sobre_D == pytest.approx(
        r.perfil.y_max_m / sec.altura, rel=REL_FORMULA)


@pytest.mark.parametrize("S", [0.0, 0.008])
def test_la_velocidad_de_salida_con_el_tw_entre_el_critico_y_la_clave(S, concreto):
    """
    La segunda viñeta de HDS-5 num. 3.1.6 (pag. impresa 3.18): bajo control
    de SALIDA, con el TW entre el tirante critico y la clave, el area de la
    velocidad de salida es la del TW. Vale igual con el barril horizontal y
    con pendiente. La medida de mutacion de T-2 encontro que cambiar esa rama
    por la del tirante critico no lo detectaba ningun test.
    """
    sec = SeccionCircular(0.90)
    Q, TW = 0.48, 0.80
    r = M4.resolver_control(sec, Q=Q, S=S, L=20.0, TW=TW, material=concreto)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.y_critico < TW < sec.altura
    assert r.V_salida.valor == pytest.approx(Q / sec.area(TW), rel=REL_FORMULA)
    # Y no es la del tirante critico, que seria mayor (menos area).
    critico = M4.tirante_critico(Q, sec)
    assert r.V_salida.valor < Q / critico.geometria.A


def test_el_csv_de_resumen_de_un_barril_horizontal_no_lleva_marcas_de_html(tmp_path):
    """
    Con S = 0 no hay velocidad uniforme: las dos celdas de velocidad del CSV
    de resumen van VACIAS. Antes salian con la entidad `&ndash;` de la
    memoria HTML, que en una hoja de calculo es basura (auditor de T-2). Se
    LEE el CSV de una corrida real, con el lector de CSV.
    """
    import csv as _csv
    from src.modulos import M11_reporte as M11
    informe = _correr(tmp_path, {
        "globales": {"TW_m": 0.3}, "puntos": {"A-01": {"S_conducto": 0.0}}})
    assert _punto_de(informe, "A-01").dimensionado
    destino = M11.exportar_csv(informe, tmp_path / "resumen.csv")
    crudo = destino.read_text(encoding="utf-8")
    assert "&" not in crudo, "el CSV lleva una entidad HTML"
    filas = {f["id"]: f for f in _csv.DictReader(crudo.splitlines())}
    assert set(filas) == {p.punto.id for p in informe.puntos}
    horizontal, corriente = filas["A-01"], filas["A-02"]
    assert horizontal["V_erosion_ms"] == "" and horizontal["V_sedimentacion_ms"] == ""
    # Lo demas de la fila esta: seccion, llenado (el del perfil), carga y control.
    assert horizontal["seccion"] and horizontal["control_gobernante"]
    assert float(horizontal["y_sobre_D"]) > 0 and float(horizontal["HW_m"]) > 0
    # Y un punto con pendiente sigue trayendo sus dos velocidades.
    assert float(corriente["V_erosion_ms"]) > float(corriente["V_sedimentacion_ms"]) > 0


def test_los_valores_de_la_banda_son_los_que_el_hds5_sostiene():
    """
    0.0: el barril horizontal que el num. 3.3.4 admite. 0.10: «Most culverts
    are constructed on slopes that are less than 10% ... no special
    structural measures are used» (num. 5.4.4). 0.02: la pendiente de las
    curvas (num. A.3). Las tres frases estan en el registro, verificadas.
    """
    reg = construir()
    assert "no slope (horizontal)" in reg.cita(
        "HDS5_3ED.3.3.4#HORIZONTAL").texto_literal.texto
    assert "less than 10%" in reg.cita(
        "HDS5_3ED.5.4.4#PENDIENTE_10").texto_literal.texto
    assert "2 percent (0.02)" in reg.cita(
        "HDS5_3ED.A.3#PENDIENTE_2").texto_literal.texto
    # Y la del Manual es una exigencia SIN cifra.
    manual = reg.cita("MC_HHD.4.1.1.3.3")
    assert manual.titulo_numeral == "Pendiente longitudinal"
    assert not re.search(r"\d", manual.texto_literal.texto)
    assert M5.limites_de_pendiente() == pytest.approx((0.0, 0.10),
                                                      rel=REL_TRANSPORTE)


@pytest.mark.parametrize("S, cumple, criterio", [
    (0.0, True, "pendiente_maxima_conducto"),
    (0.006, True, "pendiente_maxima_conducto"),
    (0.10, True, "pendiente_maxima_conducto"),       # el borde es inclusivo
    (0.12, False, "pendiente_maxima_conducto"),
])
def test_v10_juzga_la_pendiente_del_diseno_contra_la_banda(S, cumple, criterio):
    v = M5.v10_pendiente_conducto(resultado=_resultado(S=S))
    assert v.codigo == "V10" and v.cumple is cumple
    assert v.valor_obtenido == pytest.approx(S, abs=ABS_CERO)
    assert v.criterio_aplicado == criterio
    assert v.valor_admisible == pytest.approx(0.10, rel=REL_TRANSPORTE)
    assert v.paso.veredicto.margen == pytest.approx(0.10 - S, rel=REL_FORMULA,
                                                    abs=ABS_CERO)
    assert v.paso.fundamento_id == "F5.V10"
    assert {e.clave_criterio for e in v.paso.elecciones} == {
        "pendiente_minima_conducto", "pendiente_maxima_conducto"}
    # Cada eleccion imprime SU ventana, la de la ficha: es lo que dice
    # dentro de que se eligio.
    ventanas = {e.clave_criterio: e.entre for e in v.paso.elecciones}
    assert ventanas["pendiente_minima_conducto"] == ("0 m/m", "0.005 m/m")
    assert ventanas["pendiente_maxima_conducto"] == ("0.02 m/m", "0.1 m/m")


def test_v10_rechaza_por_abajo_cuando_se_declara_una_minima_positiva():
    """Con la minima en el techo de su ventana, el conducto al 0.4 % no pasa."""
    ca.establecer_valor_dinamico("pendiente_minima_conducto", 0.005)
    v = M5.v10_pendiente_conducto(resultado=_resultado(S=0.004))
    assert not v.cumple
    assert v.criterio_aplicado == "pendiente_minima_conducto"
    assert v.valor_admisible == pytest.approx(0.005, rel=REL_TRANSPORTE)
    assert v.paso.veredicto.margen == pytest.approx(-0.001, rel=REL_FORMULA)
    assert M5.v10_pendiente_conducto(resultado=_resultado(S=0.005)).cumple


def test_la_banda_vacia_es_un_par_de_criterios_que_se_contradicen():
    """Guardia cruzada, forma MAT-D13: el mensaje nombra el par culpable."""
    with con_valor("pendiente_minima_conducto", 0.20,
                   motivo="caso sintetico: una minima por encima de la "
                          "maxima, que la ventana del archivo no permite"):
        with pytest.raises(DatoInvalidoError) as exc:
            M5.limites_de_pendiente()
    assert "pendiente_minima_conducto" in str(exc.value)
    assert "pendiente_maxima_conducto" in str(exc.value)


def test_una_banda_de_un_solo_valor_no_es_una_contradiccion():
    """
    La guardia cruzada rechaza la minima POR ENCIMA de la maxima, no la
    igualdad: quien fije la pendiente del conducto en un unico valor declara
    una banda degenerada y valida, y V10 la cumple justo en ese valor.
    """
    with con_valor("pendiente_minima_conducto", 0.02,
                   motivo="caso sintetico: la minima igual a la maxima, que "
                          "la ventana del archivo (0 a 0.005) no alcanza"):
        ca.establecer_valor_dinamico("pendiente_maxima_conducto", 0.02)
        assert M5.limites_de_pendiente() == pytest.approx(
            (0.02, 0.02), rel=REL_TRANSPORTE)
        assert M5.v10_pendiente_conducto(resultado=_resultado(S=0.02)).cumple
        assert not M5.v10_pendiente_conducto(resultado=_resultado(S=0.021)).cumple
        assert not M5.v10_pendiente_conducto(resultado=_resultado(S=0.019)).cumple


def test_v10_esta_en_los_dos_verificadores_y_no_toca_a_v2b(tmp_path, concreto):
    """
    V10 va detras de V4b y antes del hueco de V5 en `M5.verificar` y en el
    verificador de perfil, y V2b sigue haciendo la MISMA comparacion
    (S_conducto >= S_cauce).
    """
    a01 = _punto_de(_correr(tmp_path, {"globales": {"TW_m": 0.3}}), "A-01")
    codigos = [v.codigo for v in a01.resultado.verificaciones]
    assert codigos.count("V10") == 1
    assert codigos.index("V10") == codigos.index("V4b") + 1
    assert codigos.index("V10") < codigos.index("V6")
    v2b = M5.v2b_sedimentacion(punto=_punto(S_cauce=0.006),
                               resultado=_resultado(S=0.004))
    assert v2b.valor_obtenido == pytest.approx(0.004, rel=REL_TRANSPORTE)
    assert v2b.valor_admisible == pytest.approx(0.006, rel=REL_TRANSPORTE)
    assert "V10" in UMBRALES_POR_CODIGO
    assert UMBRALES_POR_CODIGO["V10"]["fundamento"] == "F5.V10"


def test_una_pendiente_fuera_de_la_banda_no_se_resuelve_con_otro_diametro(tmp_path):
    """
    V10 no depende del diametro: el punto recorre el catalogo entero con V10
    incumplida y sale «no factible», y el remedio es otra pendiente.
    """
    a01 = _punto_de(_correr(tmp_path, {
        "globales": {"TW_m": 0.3}, "puntos": {"A-01": {"S_conducto": 0.12}}}),
        "A-01")
    assert not a01.dimensionado
    assert not any(escalon.aceptado for escalon in a01.traza)
    # Un escalon que se detiene antes (V7 sin cobertura, espesor de pared sin
    # transcribir) no llega a V10: se miran los que si recorrieron la tabla.
    v10_por_escalon = [[v for v in escalon.verificaciones if v.codigo == "V10"]
                       for escalon in a01.traza]
    completos = [v10[0] for v10 in v10_por_escalon if v10]
    assert len(completos) > 2
    assert not any(v.cumple for v in completos)
    # Y el motivo de cada escalon que reporta incumplimientos la nombra (un
    # escalon que se detuvo despues en un dato que falta dice eso, no V10).
    con_incumplidas = [e for e in a01.traza if e.incumplidas]
    assert con_incumplidas
    assert all("V10" in [v.codigo for v in e.incumplidas]
               for e in con_incumplidas)


def test_v10_se_evalua_en_expediente_aunque_v5_se_detenga(concreto):
    """
    En el alcance de expediente `M5.verificar` se corta en la primera pieza
    que se detiene, y V5 se detiene siempre en las Familias A y B (falta el
    ancho del derecho de via). V10 no depende de eso ni del diametro: va
    ANTES del hueco de V5 y llega entre las completadas, con su veredicto.
    Con V10 al final de la tabla no se evaluaba en ninguna corrida de
    expediente del repositorio (auditor adversarial de T-2).
    """
    from src.modelos import ErrorProyecto
    sec = SeccionCircular(0.90)
    for S, cumple in ((0.006, True), (0.12, False)):
        r = M4.resolver_control(sec, Q=0.3, S=S, L=20.0, TW=0.0,
                                material=concreto)
        with pytest.raises(ErrorProyecto) as exc:
            M5.verificar(punto=_punto(), material=concreto, seccion=sec,
                         resultado=r)
        completadas = exc.value.verificaciones_completadas
        codigos = [v.codigo for v in completadas]
        assert "V5" not in codigos, "V5 dejo de detenerse: revisar el caso"
        assert codigos[-1] == "V10"
        assert completadas[-1].cumple is cumple


# ===========================================================================
# 2 · Borde libre: lleno por el caudal o lleno por el receptor (INF-3.2.6)
# ===========================================================================

def test_la_ficha_de_borde_libre_bajo_tw_ahogante():
    c = ca.criterio("borde_libre_bajo_tw_ahogante")
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_CATEGORIA
    assert tuple(c.sensibilidad) == ("no_cumple", "aviso")
    # El valor de archivo es la conducta que el proyecto ya tenia (EXT-3):
    # cambiarla puede mover un diametro y eso lo decide el dueño.
    assert c.valor == "no_cumple"
    assert "4.1.1.3.7 b)" in c.fuente and c.justificacion
    with pytest.raises(ValueError):
        ca.verificar_declaracion("borde_libre_bajo_tw_ahogante", "quizas")


def _lleno_por_receptor(concreto, *, Q=0.3, D=0.90, S=0.006):
    """TW sobre la clave: el barril va lleno por el nivel del receptor."""
    sec = SeccionCircular(D)
    return sec, M4.resolver_control(sec, Q=Q, S=S, L=20.0, TW=D + 0.30,
                                    material=concreto)


def test_lleno_por_el_receptor_no_cumple_con_el_valor_de_archivo(concreto):
    sec, r = _lleno_por_receptor(concreto)
    assert r.regimen_barril is RegimenBarril.LLENO
    assert r.y_normal / sec.altura < Y_SOBRE_D_MAX   # su propio caudal cabria
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert not v.cumple
    assert v.valor_obtenido == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert "MC_HHD.4.1.1.3.7b#LLENA" in v.paso.citas_textuales
    # LA MEMORIA DICE CUAL APLICO: la eleccion con su valor y el caso.
    (eleccion,) = v.paso.elecciones
    assert eleccion.clave_criterio == "borde_libre_bajo_tw_ahogante"
    assert eleccion.valor == "no_cumple"
    assert eleccion.entre == ("no_cumple", "aviso")     # la ventana de la ficha
    assert "LLENO POR EL NIVEL DEL RECEPTOR" in v.paso.nota_del_proyecto
    assert "«no_cumple»" in v.paso.nota_del_proyecto
    assert "NO CUMPLE, por la exigencia" in v.paso.nota_del_proyecto
    assert "queda como AVISO" not in v.paso.nota_del_proyecto
    # El margen es el de la comparacion: no hay borde libre (0.75 - 1.0).
    assert v.paso.veredicto.margen == pytest.approx(Y_SOBRE_D_MAX - 1.0,
                                                    rel=REL_FORMULA)
    assert "borde_libre_bajo_tw_ahogante" in ca.criterios_usados()


def test_lleno_por_el_receptor_bajo_aviso_no_descarta_si_el_caudal_cabe(concreto):
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    sec, r = _lleno_por_receptor(concreto)
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    # El numero no se maquilla: el barril va lleno, y/D = 1.
    assert v.valor_obtenido == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert v.paso.elecciones[0].valor == "aviso"
    simbolos = {m.simbolo: m for m in v.paso.sustitucion}
    assert simbolos["y_normal"].valor == pytest.approx(r.y_normal,
                                                       rel=REL_TRANSPORTE)
    assert simbolos["TW"].valor == pytest.approx(r.TW_m, rel=REL_TRANSPORTE)
    assert simbolos["TW"].unidad == "m"
    # La nota dice el caso y la lectura que aplico, y el margen sigue siendo
    # el de la comparacion (negativo: el barril va lleno).
    nota = v.paso.nota_del_proyecto
    assert "«aviso»" in nota and "queda como AVISO" in nota
    assert "NO CUMPLE, por la exigencia" not in nota
    assert v.paso.veredicto.margen == pytest.approx(Y_SOBRE_D_MAX - 1.0,
                                                    rel=REL_FORMULA)


# Los cuatro TW y los dos diametros con que la revision adversarial midio la
# discontinuidad de la primera redaccion de «aviso», sobre el caudal y la
# pendiente de A-02 (Q = 0.48 m3/s, S = 0.008): un TW bajo el llenado
# admisible del tubo chico, dos entre el llenado admisible y la clave, uno en
# la clave y uno por encima.
Q_A02, S_A02 = 0.48, 0.008
TW_DEL_BARRIDO = (0.60, 0.80, 0.89, 0.90, 1.00, 1.20)
DIAMETROS_DEL_BARRIDO = (0.90, 1.05)


def _v1_con_tw(concreto, D, TW):
    sec = SeccionCircular(D)
    r = M4.resolver_control(sec, Q=Q_A02, S=S_A02, L=20.0, TW=TW,
                            material=concreto)
    return r, M5.v1_borde_libre(D=D, material=concreto, punto=_punto(),
                                resultado=r)


@pytest.mark.parametrize("D", DIAMETROS_DEL_BARRIDO)
def test_bajo_aviso_la_lectura_es_la_misma_a_lo_largo_del_tw(D, concreto):
    """
    LA LECTURA «aviso» NO PUEDE CAMBIAR AL CRUZAR TW = D. La primera
    redaccion solo actuaba con el regimen LLENO, y el auditor midio la
    consecuencia: con TW = 0.80 y 0.89 m el Ø 0.90 no pasaba, con 0.90 si, y
    con 1.00 pasaba el Ø 0.90 y fallaba el Ø 1.05 --mas ahogamiento, mas
    permisivo; y el tubo chico pasaba donde el grande no--. Ahora el caso es
    uno: cuando el TW queda por encima del llenado admisible y es el quien
    fija el tirante maximo del barril, V1 sale como INDICADOR si el caudal
    de diseño por si solo conserva el borde libre, llegue el TW a la clave o
    no.
    """
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    tipos = []
    for TW in TW_DEL_BARRIDO:
        r, v = _v1_con_tw(concreto, D, TW)
        assert r.y_normal / D < Y_SOBRE_D_MAX        # el caudal cabe siempre
        assert v.cumple, (D, TW)
        tipos.append(v.paso.veredicto.tipo)
        if TW / D > Y_SOBRE_D_MAX:
            assert v.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR, (D, TW)
            assert v.valor_obtenido > Y_SOBRE_D_MAX   # el numero no se maquilla
            assert v.paso.elecciones[0].clave_criterio == (
                "borde_libre_bajo_tw_ahogante")
        else:
            assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE
            assert not v.paso.elecciones
    # Monotona: una vez que el receptor toma el borde libre, sigue siendo un
    # aviso para todo TW mayor. No vuelve a «cumple» ni cae a «no cumple».
    primero = tipos.index(TipoDeVeredicto.INDICADOR)
    assert all(t is TipoDeVeredicto.INDICADOR for t in tipos[primero:])
    assert all(t is TipoDeVeredicto.CUMPLE for t in tipos[:primero])


@pytest.mark.parametrize("TW", TW_DEL_BARRIDO)
def test_bajo_aviso_el_tubo_mayor_no_falla_donde_pasa_el_menor(TW, concreto):
    """La otra incoherencia medida: con TW = 1.00 pasaba el Ø 0.90 y no el Ø 1.05."""
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    chico = _v1_con_tw(concreto, DIAMETROS_DEL_BARRIDO[0], TW)[1]
    grande = _v1_con_tw(concreto, DIAMETROS_DEL_BARRIDO[1], TW)[1]
    assert chico.cumple and grande.cumple


@pytest.mark.parametrize("D", DIAMETROS_DEL_BARRIDO)
def test_con_el_valor_de_archivo_el_remanso_del_receptor_sigue_sin_cumplir(
        D, concreto):
    """
    «no_cumple» NO CAMBIA NINGUN VEREDICTO respecto de antes de T-2: con el TW
    por encima del llenado admisible V1 no cumple, este o no en la clave. Lo
    que cambia es que la memoria dice el caso y nombra el criterio.
    """
    for TW in TW_DEL_BARRIDO:
        r, v = _v1_con_tw(concreto, D, TW)
        if TW / D > Y_SOBRE_D_MAX:
            assert not v.cumple, (D, TW)
            assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
            assert v.paso.elecciones[0].valor == "no_cumple"
            nota = v.paso.nota_del_proyecto
            if r.regimen_barril is RegimenBarril.LLENO:
                assert "LLENO POR EL NIVEL DEL RECEPTOR" in nota
            else:
                assert "BORDE LIBRE TOMADO POR EL NIVEL DEL RECEPTOR" in nota
                # No es la exigencia de «seccion llena»: no se cita.
                assert "MC_HHD.4.1.1.3.7b#LLENA" not in v.paso.citas_textuales
        else:
            assert v.cumple and not v.paso.elecciones


def test_bajo_aviso_un_barril_horizontal_remansado_no_cumple(concreto):
    """
    Con S = 0 no hay tirante normal: no hay con que separar el llenado propio
    del caudal del remanso del receptor, y V1 no cumple bajo «aviso» tampoco
    con el TW entre el llenado admisible y la clave. La memoria lo dice.
    """
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    sec = SeccionCircular(0.90)
    r = M4.resolver_control(sec, Q=0.3, S=0.0, L=20.0, TW=0.80,
                            material=concreto)
    assert r.sin_tirante_normal
    assert r.regimen_barril is RegimenBarril.PARCIALMENTE_LLENO
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert not v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    simbolos = {m.simbolo: m for m in v.paso.sustitucion}
    assert simbolos["y_normal"].valor == "no existe (S = 0)"


def test_si_el_tirante_maximo_lo_fija_el_caudal_el_criterio_no_interviene(
        concreto):
    """
    El caso del receptor exige que el tirante maximo del perfil sea el TW. Si
    el caudal levanta la lamina por encima del TW --aqui, hasta la clave--,
    es el caudal quien quita el borde libre: no cumple bajo «aviso» y el
    criterio ni se invoca.
    """
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    sec = SeccionCircular(0.90)
    r = M4.resolver_control(sec, Q=1.6, S=0.0, L=60.0, TW=0.70,
                            material=concreto)
    assert r.regimen_barril is RegimenBarril.PARCIALMENTE_LLENO
    assert r.TW_m / sec.altura > Y_SOBRE_D_MAX
    assert r.perfil.y_max_m > r.TW_m
    ca.reiniciar_usos()
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert not v.cumple and not v.paso.elecciones
    assert "borde_libre_bajo_tw_ahogante" not in ca.criterios_usados()


def test_el_consumidor_rechaza_una_lectura_que_burla_la_puerta(concreto):
    """
    Segunda linea de guardia (ficha EXT-5-02): la puerta del criterio ya
    rechaza lo que no es de la ventana, y V1 no se fia de ella. Un texto que
    no es una de las dos lecturas no se interpreta: se detiene.
    """
    sec, r = _lleno_por_receptor(concreto)
    for malo in ("indicador", "", 1):
        with con_valor("borde_libre_bajo_tw_ahogante", malo,
                       motivo="probar la guardia del consumidor de V1"):
            with pytest.raises(DatoInvalidoError,
                               match="borde_libre_bajo_tw_ahogante"):
                M5.v1_borde_libre(D=sec.altura, material=concreto,
                                  punto=_punto(), resultado=r)


def test_bajo_aviso_el_caudal_que_no_cabe_sigue_sin_cumplir(concreto):
    """
    «aviso» perdona el ahogamiento, no el diametro chico: si con su propio
    caudal el barril ya no conserva el 25 %, V1 no cumple igual.
    """
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    sec, r = _lleno_por_receptor(concreto, Q=1.30)     # y_n/D ~ 0.8
    assert r.regimen_barril is RegimenBarril.LLENO
    assert r.y_normal / sec.altura > Y_SOBRE_D_MAX
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert not v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert "NO lo conserva" in v.paso.nota_del_proyecto
    assert "queda como AVISO" not in v.paso.nota_del_proyecto


def test_bajo_aviso_un_barril_horizontal_ahogado_no_cumple(concreto):
    """Sin tirante normal no hay con que separar los dos casos."""
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", "aviso")
    sec, r = _lleno_por_receptor(concreto, S=0.0)
    assert r.sin_tirante_normal and r.regimen_barril is RegimenBarril.LLENO
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert not v.cumple


@pytest.mark.parametrize("lectura", ["no_cumple", "aviso"])
def test_lleno_por_el_caudal_de_diseno_no_cumple_bajo_ninguna_lectura(
        lectura, concreto):
    """
    El otro caso: la lamina toca la clave con el TW POR DEBAJO de ella. Es el
    que la frase prohibitiva del Manual describe sin matiz; no cumple con las
    dos lecturas, y el criterio ni se invoca.
    """
    ca.establecer_valor_dinamico("borde_libre_bajo_tw_ahogante", lectura)
    sec = SeccionCircular(0.90)
    r = M4.resolver_control(sec, Q=1.6, S=0.0, L=60.0, TW=0.0, material=concreto)
    assert r.regimen_barril is RegimenBarril.PARCIALMENTE_LLENO
    assert r.TW_m < sec.altura
    assert r.perfil.y_max_m == pytest.approx(sec.altura, rel=REL_FORMULA)
    ca.reiniciar_usos()
    v = M5.v1_borde_libre(D=sec.altura, material=concreto, punto=_punto(),
                          resultado=r)
    assert not v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert "MC_HHD.4.1.1.3.7b#LLENA" in v.paso.citas_textuales
    assert "LLENO POR EL CAUDAL DE DISEÑO" in v.paso.nota_del_proyecto
    assert not v.paso.elecciones
    assert "borde_libre_bajo_tw_ahogante" not in ca.criterios_usados()


def test_el_barrido_de_la_lectura_sobre_la_corrida_estrecha(tmp_path):
    """
    LA EVIDENCIA DE LA PARADA (c), medida con el barrido de PF-3 sobre la
    corrida estrecha de la linea base (TW por la via 4, receptor a seccion
    llena con la seccion ADOPTADA). Con «no_cumple» ninguno de los cuatro
    puntos dimensiona, que es la linea base; con «aviso» A-02 pasa a
    dimensionar. Por eso el valor de archivo es «no_cumple» y la otra
    lectura queda como alternativa barrible: mover un punto de la linea base
    lo decide el dueño.
    """
    # POR LA CLI REAL, EN SUBPROCESO, como `regenerar.sh`: `conftest.py`
    # declara en caliente tres criterios de prueba para toda la suite, y una
    # corrida en proceso no es la que produce la linea base (con ellos A-01
    # llega mas lejos en su progresion). Lo que la ficha T2-02 cita es esto.
    destino = tmp_path / "barrido.json"
    hecho = subprocess.run(
        [sys.executable, "cli.py", str(CSV), "--luz", "2.75",
         "--alcance", "perfil", "--barrido",
         "borde_libre_bajo_tw_ahogante=no_cumple,aviso",
         "--json", str(destino)],
        cwd=RAIZ, capture_output=True, text=True)
    assert destino.exists(), hecho.stderr
    (uno,) = json.loads(destino.read_text(encoding="utf-8"))["barridos"]
    por_valor = {}
    for corrida in uno["corridas"]:
        puntos = corrida["informe_json"]["puntos"]
        por_valor[corrida["valor"]] = {
            p["id"]: (p["diseno"] or {}).get("seccion")
            for p in puntos if p["dimensionado"]}
    assert por_valor["no_cumple"] == {}
    assert por_valor["aviso"] == {"A-02": "Ø 0.90 m"}


# ===========================================================================
# 3 · Tailwater: la seccion del receptor, adoptada o medida (INF-3.2.8)
# ===========================================================================

MEDIDA = SeccionReceptor(b_m=1.2, z_HV=1.0, S=0.001, n=0.025,
                         altura_total_m=1.10)
MEDIDA_JSON = {"b_m": 1.2, "z_HV": 1.0, "S": 0.001, "n": 0.025,
               "altura_total_m": 1.10}


def test_la_via_4_con_la_seccion_adoptada_lo_dice_y_avisa():
    """Sin caudal ni cota del receptor: receptor lleno con la seccion [A]."""
    punto = _punto()
    ca.reiniciar_usos()
    tw = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=41.0)
    assert tw.via is ViaDelTW.ESCENARIOS_ACOTADOS
    assert tw.origen_seccion == SECCION_RECEPTOR_ADOPTADA
    assert SECCION_RECEPTOR_ADOPTADA == (
        "seccion adoptada [A] por falta de levantamiento")
    (aviso,) = tw.avisos
    assert SECCION_RECEPTOR_ADOPTADA in aviso and "seccion_receptor" in aviso
    adoptada = ca.CRITERIOS["seccion_receptor"].valor
    assert tw.valor == pytest.approx(
        punto.cota_fondo_receptor + adoptada["altura_total_m"] - 41.0,
        rel=REL_FORMULA)
    # El paso de memoria lleva el rotulo en la procedencia del dato.
    altura = next(m for m in tw.paso.sustitucion if m.simbolo == "altura_total")
    assert "ADOPTADA por falta de levantamiento" in altura.procedencia
    assert "seccion_receptor" in ca.criterios_usados()


def test_la_seccion_medida_gana_en_la_via_4_y_no_invoca_el_criterio():
    punto = _punto()
    ca.reiniciar_usos()
    tw = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=41.0,
                           seccion_medida=MEDIDA)
    assert tw.via is ViaDelTW.ESCENARIOS_ACOTADOS
    assert tw.origen_seccion == SECCION_RECEPTOR_MEDIDA
    assert tw.seccion == MEDIDA and tw.avisos == ()
    assert tw.valor == pytest.approx(
        punto.cota_fondo_receptor + MEDIDA.altura_total_m - 41.0,
        rel=REL_FORMULA)
    assert "seccion_receptor" not in ca.criterios_usados()
    altura = next(m for m in tw.paso.sustitucion if m.simbolo == "altura_total")
    assert "MEDIDA" in altura.procedencia
    # `seccion_del_receptor` es la lectura unica de las dos vias.
    assert M3.seccion_del_receptor(MEDIDA) == (MEDIDA, SECCION_RECEPTOR_MEDIDA)
    assert M3.seccion_del_receptor()[1] == SECCION_RECEPTOR_ADOPTADA


def test_la_seccion_medida_gana_en_la_via_3_y_manning_cierra():
    """
    Via 3 (caudal del receptor): el tirante sale de Manning sobre la seccion
    MEDIDA. El oraculo es la identidad Q = (1/n) A R^(2/3) S^(1/2) evaluada
    aqui en el tirante que la via devuelve.
    """
    Q = 1.6
    punto = _punto(Q_receptor_m3s=Q)
    tw = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=41.0,
                           seccion_medida=MEDIDA)
    assert tw.via is ViaDelTW.MANNING_RECEPTOR and tw.avisos == ()
    y_n = tw.cota_TW_msnm - punto.cota_fondo_receptor
    A = (MEDIDA.b_m + MEDIDA.z_HV * y_n) * y_n
    P = MEDIDA.b_m + 2 * y_n * math.sqrt(1 + MEDIDA.z_HV ** 2)
    # Manning rehecho aparte, sin la funcion de M3.
    Q_de_vuelta = (1 / MEDIDA.n) * A * (A / P) ** (2 / 3) * math.sqrt(MEDIDA.S)
    assert Q_de_vuelta == pytest.approx(Q, abs=ABS_BRENT)
    # Con la adoptada, la misma via avisa.
    adoptada = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=41.0)
    assert adoptada.origen_seccion == SECCION_RECEPTOR_ADOPTADA
    assert len(adoptada.avisos) == 1


def test_las_vias_1_y_2_no_usan_seccion_ni_avisan():
    declarado = M3.tw_seccion_1_3(punto=_punto(), cota_fondo_salida=None,
                                  tw_declarado=0.3)
    por_cota = M3.tw_seccion_1_3(punto=_punto(cota_TW=41.8),
                                 cota_fondo_salida=41.0)
    for tw in (declarado, por_cota):
        assert tw.seccion is None and tw.origen_seccion == ""
        assert tw.avisos == ()


@pytest.mark.parametrize("mala", [
    {"b_m": 1.2, "z_HV": 1.0, "S": 0.001, "n": 0.025},                # falta un campo
    dict(MEDIDA_JSON, ancho_m=2.0),                                    # sobra uno
    dict(MEDIDA_JSON, n=0.0), dict(MEDIDA_JSON, S=-0.001),
    dict(MEDIDA_JSON, S=1.5), dict(MEDIDA_JSON, altura_total_m=0.0),
    dict(MEDIDA_JSON, b_m=-1.0), dict(MEDIDA_JSON, b_m=0.0, z_HV=0.0),
    dict(MEDIDA_JSON, n=True), dict(MEDIDA_JSON, b_m="1.2"),
    [1.2, 1.0, 0.001, 0.025, 1.1], 3.0,
    # Los techos de dominio de `dominios.py` (rango fisico, no normativo): un
    # n >= 1 es un Strickler, una profundidad >= 100 m son centimetros.
    dict(MEDIDA_JSON, n=1.0), dict(MEDIDA_JSON, n=5.0),
    dict(MEDIDA_JSON, altura_total_m=100.0),
    dict(MEDIDA_JSON, altura_total_m=110.0),
])
def test_la_seccion_medida_entra_completa_y_fisica_o_no_entra(mala, tmp_path):
    """Es entrada del proyecto: se valida la forma y el dominio, no se rellena."""
    # El control: la seccion buena SI entra. Sin el, el rechazo de abajo
    # valdria tambien en un arbol que no conociera la clave.
    buena = _externos(tmp_path, {"puntos": {"A-01": {
        "seccion_receptor_medida": MEDIDA_JSON}}})
    assert buena.valor("A-01", servicio.CLAVE_SECCION_RECEPTOR_MEDIDA) == MEDIDA_JSON
    with pytest.raises(DatoInvalidoError) as exc:
        _externos(tmp_path, {"puntos": {"A-01": {"seccion_receptor_medida": mala}}})
    assert servicio.CLAVE_SECCION_RECEPTOR_MEDIDA in str(exc.value)


@pytest.mark.parametrize("buena", [
    dict(MEDIDA_JSON, b_m=0.0),                 # cuneta triangular
    dict(MEDIDA_JSON, z_HV=0.0),                # canal rectangular
    dict(MEDIDA_JSON, b_m=0.5, z_HV=0.5),       # solera y talud iguales
    dict(MEDIDA_JSON, S=0.999),                 # justo bajo el techo del dominio
    dict(MEDIDA_JSON, altura_total_m=0.4, n=0.011, S=0.0002),
    dict(MEDIDA_JSON, n=0.15),                  # un cauce muy rugoso cabe
    dict(MEDIDA_JSON, altura_total_m=12.0),     # y un dren hondo tambien
])
def test_la_seccion_medida_admite_lo_que_es_una_seccion(buena, tmp_path):
    """
    La otra mitad de la validacion: no rechaza de mas. El ancho de fondo y el
    talud admiten el cero por separado, y ningun campo tiene un piso oculto.
    """
    externos = _externos(tmp_path, {"globales": {"seccion_receptor_medida": buena}})
    leida = externos.valor("A-01", servicio.CLAVE_SECCION_RECEPTOR_MEDIDA)
    assert leida == {k: float(v) for k, v in buena.items()}
    assert SeccionReceptor(**leida).altura_total_m > 0


def test_la_pendiente_de_la_seccion_medida_va_en_m_por_m(tmp_path):
    """S = 1 (el techo de `dominios.S_CAUCE_MAX`) delata una celda en porcentaje."""
    with pytest.raises(DatoInvalidoError, match="seccion_receptor_medida.S"):
        _externos(tmp_path, {"globales": {
            "seccion_receptor_medida": dict(MEDIDA_JSON, S=1.0)}})


def test_la_seccion_medida_por_punto_llega_a_la_corrida(tmp_path):
    """
    La corrida estrecha (via 4) con la seccion levantada SOLO en A-02: A-02
    corre con la medida y sin aviso; A-01 sigue con la adoptada y avisa. El
    aviso y el rotulo salen en la CLI, en el JSON y en la memoria.
    """
    informe = _correr(tmp_path, {
        "puntos": {"A-02": {"seccion_receptor_medida": MEDIDA_JSON}}})
    a01, a02 = _punto_de(informe, "A-01"), _punto_de(informe, "A-02")
    assert a02.tw_sec13.origen_seccion == SECCION_RECEPTOR_MEDIDA
    assert a02.tw_sec13.seccion == MEDIDA
    assert _avisos_sin_geometria(a02) == (AVISO_DEL_CAUDAL_DECLARADO,)
    assert a01.tw_sec13.origen_seccion == SECCION_RECEPTOR_ADOPTADA
    de_a01 = _avisos_sin_geometria(a01)
    assert len(de_a01) == 2 and de_a01[0] == AVISO_DEL_CAUDAL_DECLARADO
    volcado = {p["id"]: p for p in cli.informe_json(informe)["puntos"]}
    assert volcado["A-02"]["tw_seccion_receptor"]["origen"] == SECCION_RECEPTOR_MEDIDA
    assert volcado["A-02"]["tw_seccion_receptor"]["altura_total_m"] == \
        pytest.approx(1.10, rel=REL_TRANSPORTE)
    assert volcado["A-02"]["avisos"] == list(a02.avisos())
    assert volcado["A-02"]["avisos"][0] == AVISO_DEL_CAUDAL_DECLARADO
    assert not set(a02.tw_sec13.avisos) & set(volcado["A-02"]["avisos"])
    assert volcado["A-01"]["avisos"] == list(a01.avisos())
    assert f"aviso: {de_a01[-1]}" in cli.volcar(informe)
    from src.modulos import M11_reporte as M11
    html_a01 = M11.memoria_de_punto(a01)
    html_a02 = M11.memoria_de_punto(a02)
    assert SECCION_RECEPTOR_ADOPTADA in html_a01
    assert 'class="aviso"' in html_a01 and "Aviso." in html_a01
    assert SECCION_RECEPTOR_MEDIDA in html_a02
    assert SECCION_RECEPTOR_ADOPTADA not in html_a02


def test_con_la_seccion_medida_la_via_4_no_necesita_el_criterio():
    """El predicado que el resolvedor y el pre-vuelo comparten."""
    from tests.apoyo.criterios import sin_valor
    with sin_valor("seccion_receptor"):
        assert servicio.tw_sin_via_de_sec_1_3(None, None, None)
        assert not servicio.tw_sin_via_de_sec_1_3(None, None, None,
                                                  hay_seccion_medida=True)


# ===========================================================================
# 4 · Las filas de la Tabla A.1 y de la Tabla C.2 (INF-3.2.2)
# ===========================================================================

# Las ocho filas que T-2 transcribe, con lo que la PDF 197 imprime: carta,
# escala, forma, K, M, c, Y. Escritas aqui A MANO desde la pagina, como
# segunda transcripcion independiente de la del registro.
FILAS_NUEVAS_TA1 = {
    "circular_concreto_groove_end_headwall": (1, 2, 1, 0.0018, 2.0, 0.0292, 0.74),
    "circular_concreto_groove_end_projecting": (1, 3, 1, 0.0045, 2.0, 0.0317, 0.69),
    "circular_cmp_projecting": (2, 3, 1, 0.0340, 1.50, 0.0553, 0.54),
    "circular_anillo_biselado_45": (3, "A", 1, 0.0018, 2.50, 0.0300, 0.74),
    "circular_anillo_biselado_337": (3, "B", 1, 0.0018, 2.50, 0.0243, 0.83),
    "cajon_concreto_bisel_superior_aletas_45_desplazadas":
        (13, 1, 2, 0.497, 0.667, 0.0302, 0.835),
    "cajon_concreto_bisel_superior_aletas_337_desplazadas":
        (13, 2, 2, 0.495, 0.667, 0.0252, 0.881),
    "cajon_concreto_bisel_superior_aletas_184_desplazadas":
        (13, 3, 2, 0.493, 0.667, 0.0227, 0.887),
}


@pytest.mark.parametrize("clave", sorted(FILAS_NUEVAS_TA1))
def test_las_filas_nuevas_de_la_tabla_a1_valen_lo_que_la_pagina_imprime(clave):
    carta, escala, forma, K, M, c, Y = FILAS_NUEVAS_TA1[clave]
    fila = HDS5_INLET[clave]
    assert fila["forma"] == forma
    assert (fila["K"], fila["M"], fila["c"], fila["Y"]) == pytest.approx(
        (K, M, c, Y), rel=REL_TRANSPORTE)
    assert fila["Ks"] == pytest.approx(-0.5, rel=REL_TRANSPORTE)   # ninguna es de inglete
    transcrita = next(f for f in construir().tabla("HDS5_3ED.TA1").filas
                      if f.id.endswith("#" + clave))
    assert transcrita.valores["chart_no"] == carta
    assert transcrita.valores["nomograph_scale"] == escala


def _filas_de_la_pagina_a1():
    """
    La Tabla A.1 leida de la capa de texto de la PDF 197, fila a fila: tras
    el rotulo de la configuracion vienen, uno por renglon, la forma y las
    cuatro constantes.
    """
    fitz = pytest.importorskip("fitz")
    ruta = fuentes.ruta_pdf(fuentes.FUENTES["HDS5_3ED"])
    if not ruta.exists():
        pytest.skip(f"falta {ruta}")
    lineas = [l.strip() for l in fitz.open(ruta)[196].get_text().splitlines()]
    return lineas


@pytest.mark.pdf
def test_las_26_filas_transcritas_coinciden_con_la_pagina_197():
    """
    TODAS las filas del registro, no solo las ocho nuevas: rotulo, forma, K,
    M, c e Y contra la pagina. Es lo que el encargo pide --«fija cada valor
    con test contra la pagina»-- y lo que impide que una fila ya transcrita
    cambie sin evidencia del PDF.
    """
    lineas = _filas_de_la_pagina_a1()
    tabla = construir().tabla("HDS5_3ED.TA1")
    assert len(tabla.filas) == 26
    vistas = set()
    for fila in tabla.filas:
        v = fila.valores
        # La unica fila cuyo rotulo ocupa dos renglones en la pagina.
        primera = str(v["inlet_configuration"]).split(" 30° skewed barrel")[0]
        candidatos = [i for i, l in enumerate(lineas)
                      if l == primera.strip() and i not in vistas
                      and lineas[i - 2] == str(v["shape_and_material"])
                      and lineas[i - 1] == str(v["nomograph_scale"])]
        if "30° skewed barrel" in str(v["inlet_configuration"]):
            candidatos = [i for i in candidatos
                          if lineas[i + 1] == "30° skewed barrel"]
        elif primera.startswith("18.4° non-offset"):
            candidatos = [i for i in candidatos
                          if lineas[i + 1] != "30° skewed barrel"]
        assert len(candidatos) == 1, (fila.id, candidatos)
        i = candidatos[0]
        vistas.add(i)
        numeros = []
        for l in lineas[i + 1:i + 8]:
            try:
                numeros.append(float(l))
            except ValueError:
                continue
        forma, K, M, c, Y = numeros[:5]
        assert int(forma) == v["equation_form"], fila.id
        assert (K, M, c, Y) == pytest.approx(
            (v["K"], v["M"], v["c"], v["Y"]), rel=REL_TRANSPORTE), fila.id
        assert lineas[i - 3] == str(v["chart_no"]), fila.id


def test_las_filas_que_el_catalogo_usa_no_se_movieron(concreto):
    """La embocadura adoptada hoy no cambia: T-2 solo deja filas disponibles."""
    assert (concreto.hds5.K, concreto.hds5.M, concreto.hds5.c,
            concreto.hds5.Y, concreto.hds5.Ks) == pytest.approx(
        (0.0098, 2.0, 0.0398, 0.67, -0.5), rel=REL_TRANSPORTE)
    assert ca.CRITERIOS["ke_entrada"].valor == pytest.approx(
        0.5, rel=REL_TRANSPORTE)
    tmc = catalogo(TipoMaterial.TMC)
    assert (tmc.hds5.K, tmc.hds5.c) == pytest.approx((0.0078, 0.0379),
                                                     rel=REL_TRANSPORTE)
    # --- T-3 --- La embocadura del CAJON tiene valor de archivo desde T-3, y
    # es una fila que ya estaba en la tabla antes de T-2 (Carta 8, escala 1):
    # ninguna de las que T-2 dejo disponibles para T-7a.
    assert ca.CRITERIOS["embocadura_cajon"].valor == \
        "cajon_concreto_aletas_30_75"
    assert ca.CRITERIOS["embocadura_cajon"].valor not in FILAS_NUEVAS_TA1


def test_la_embocadura_puede_nombrar_una_fila_de_aleros():
    """
    Lo que T-7a va a consumir: una fila de aleros se puede NOMBRAR en los
    criterios que eligen la embocadura, y la de ke lleva su rotulo.
    """
    # Cajon: las dieciocho filas, con las tres de la Carta 13.
    assert len(CARTAS_CAJON_TA1) == 18
    nuevas = {k for k in FILAS_NUEVAS_TA1 if k.startswith("cajon")}
    assert nuevas <= CARTAS_CAJON_TA1
    for clave in sorted(nuevas) + ["cajon_concreto_aletas_30_75",
                                   "cajon_concreto_aletas_90_15"]:
        ed.verificar("embocadura_cajon", clave)       # la puerta la admite
    # Tubo: la fila de ke del cabezal dice «and wingwalls» en su rotulo, y
    # las filas de campana y bisel existen para el concreto.
    assert KE_HDS5_C2["concreto_headwall_square_edge"]["agrupacion"] == (
        "Headwall or headwall and wingwalls")
    assert KE_HDS5_C2["concreto_headwall_socket"]["ke"] == pytest.approx(
        0.2, rel=REL_TRANSPORTE)
    assert KE_HDS5_C2["concreto_beveled"]["ke"] == pytest.approx(
        0.2, rel=REL_TRANSPORTE)
    aleros = {k: v["ke"] for k, v in KE_HDS5_C2.items()
              if "Wingwall" in v["agrupacion"]}
    assert aleros == pytest.approx({
        "cajon_aletas_30_75_escuadra": 0.4,
        "cajon_aletas_30_75_redondeado": 0.2,
        "cajon_aletas_10_25_escuadra": 0.5,
        "cajon_aletas_paralelas_escuadra": 0.7,
        "cajon_aletas_paralelas_tapered": 0.2}, rel=REL_TRANSPORTE)
    assert len(KE_HDS5_C2) == 22


# ===========================================================================
# 5 · Validacion externa: los ejemplos publicados del HDS-5 (INF-3.2.2)
# ===========================================================================

def _calcular_fila(grupo, fila, n=None):
    """
    Una fila del formulario, resuelta por el motor en SI y devuelta en las
    unidades de la pagina (pies). La conversion vive aqui y en el fixture.
    `n` fuerza el coeficiente de Manning: lo usan las filas de metal
    corrugado, cuyo n el formulario no imprime (`n_interpretado`).
    """
    n = fila["n"] if n is None else n
    if n is None:
        # h_o no depende de n: con el n tipico de la fuente basta para leerlo.
        n = grupo["n_interpretado"]["tipico"]
    pie = PIE_EN_METROS
    if "D_in" in fila:
        seccion = SeccionCircular(fila["D_in"] * PULGADA_EN_METROS)
    else:
        seccion = SeccionRectangular(B=fila["B_ft"] * pie, H=fila["H_ft"] * pie)
    Q = grupo["Q_ft3_s"] * pie ** 3
    S, L, TW = grupo["S"], grupo["L_ft"] * pie, grupo["TW_ft"] * pie
    hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[fila["carta"]])
    critico = M4.tirante_critico(Q, seccion)
    entrada = M4.control_entrada(Q, seccion, S, hds5, critico)
    salida = {"HW_sobre_D": entrada.HW_sobre_D,
              "HW_entrada_ft": entrada.HW / pie,
              "d_c_ft": critico.y_c / pie}
    if n is not None:
        cs = M4.control_salida(Q, seccion, S, L, TW, n, ke=fila["ke"],
                               critico=critico)
        salida.update(
            h_o_ft=cs.h_o / pie, H_ft=cs.H / pie,
            # EL_ho = EL_o + H + h_o (nota 8 del formulario): se compara la
            # ALTURA sobre el fondo de la salida, no la cota, para que el
            # 100 de la cota no esconda la diferencia.
            EL_ho_ft=grupo["EL_o_ft"] + (cs.H + cs.h_o) / pie,
            control=("entrada" if entrada.HW >= cs.HW else "salida"))
        normal = M3.tirante_normal(seccion, Q, S, n)
        if normal is not None:
            salida["V_salida_ft_s"] = Q / normal.A / pie
        # Bajo control de SALIDA la velocidad es la de la seccion de salida
        # (HDS-5 num. 3.1.6): con el TW bajo el tirante critico, Q/A(y_c).
        salida["V_salida_por_y_c_ft_s"] = Q / critico.geometria.A / pie
    return salida


def _magnitudes_del_dorado():
    for nombre in ("circular", "cajon"):
        grupo = CP_HDS5_DG1[nombre]
        for fila in grupo["filas"]:
            for magnitud in fila["publicado"]:
                yield nombre, fila["id"], magnitud


def _diferencia_relativa(grupo, fila, magnitud, calculado):
    publicado = fila["publicado"][magnitud]
    if magnitud == "EL_ho_ft":      # sobre la altura H + h_o, no sobre la cota
        base = grupo["EL_o_ft"]
        return (calculado - base) / (publicado - base) - 1
    return calculado / publicado - 1


@pytest.mark.parametrize("nombre, id_fila, magnitud",
                         list(_magnitudes_del_dorado()))
def test_el_motor_reproduce_los_ejemplos_publicados_del_hds5(
        nombre, id_fila, magnitud):
    """
    Cada cifra de los formularios DG 1.3.3 y DG 1.4.3 contra el motor. Dentro
    del 3 % de lectura, salvo las que el censo `fuera_de_tolerancia` nombra
    con su causa --y esas tienen que estar de verdad fuera, para que el censo
    no esconda nada--; y TODAS dentro del 10 % que la fuente declara para su
    procedimiento, salvo la unica que el censo dice que es inconsistente con
    la formula del propio formulario.
    """
    grupo = CP_HDS5_DG1[nombre]
    fila = next(f for f in grupo["filas"] if f["id"] == id_fila)
    calculado = _calcular_fila(grupo, fila)
    if magnitud == "control":
        assert calculado["control"] == fila["publicado"]["control"]
        return
    diferencia = _diferencia_relativa(grupo, fila, magnitud, calculado[magnitud])
    censada = (id_fila, magnitud) in CP_HDS5_DG1["fuera_de_tolerancia"]
    lectura = CP_HDS5_DG1["tolerancia_de_lectura"]
    if censada:
        assert abs(diferencia) > lectura, (
            f"{id_fila}.{magnitud} esta censada como fuera de tolerancia y "
            f"difiere {diferencia:+.2%}: el censo ya no dice la verdad")
    else:
        assert abs(diferencia) <= lectura, (
            f"{id_fila}.{magnitud}: publicado {fila['publicado'][magnitud]}, "
            f"calculado {calculado[magnitud]:.4f} ({diferencia:+.2%})")
    if (id_fila, magnitud) != ("cajon_5x5_bisel_45", "H_ft"):
        assert abs(diferencia) <= CP_HDS5_DG1["tolerancia_de_la_fuente"]


def test_el_censo_de_fuera_de_tolerancia_solo_nombra_magnitudes_del_dorado():
    existentes = {(f, m) for _n, f, m in _magnitudes_del_dorado()}
    assert set(CP_HDS5_DG1["fuera_de_tolerancia"]) <= existentes
    assert all(causa.strip() for causa in
               CP_HDS5_DG1["fuera_de_tolerancia"].values())
    sin_n = {f["id"] for g in ("circular", "cajon")
             for f in CP_HDS5_DG1[g]["filas"] if f["n"] is None}
    assert set(CP_HDS5_DG1["no_comparado"]) == sin_n
    # Y toda fila sin n impreso trae lo que se compara por intervalo.
    for g in ("circular", "cajon"):
        for f in CP_HDS5_DG1[g]["filas"]:
            assert (f["n"] is None) == ("publicado_con_n_interpretado" in f)


@pytest.mark.parametrize("id_fila", ["cmp_72_bisel_45", "cmp_60_bisel_45"])
def test_las_filas_de_metal_corrugado_con_el_n_acotado_por_la_tabla_b1(id_fila):
    """
    El formulario no imprime el n del metal corrugado, y la fuente lo acota:
    0.022-0.027 en su Tabla B.1 (corrugacion anular de 2-2/3 por 1/2 in) y
    0.024 como valor tipico de diseño (pag. impresa 3.8), que es el del
    nomograma de salida del CMP. EL n ES INTERPRETADO y por eso no se
    compara contra una cifra al 3 %: lo publicado tiene que caer DENTRO del
    intervalo que el motor da con los dos extremos del rango, y con el
    tipico tiene que salir el control que el formulario anota, a menos del
    10 % que la fuente declara para su procedimiento.
    """
    grupo = CP_HDS5_DG1["circular"]
    fila = next(f for f in grupo["filas"] if f["id"] == id_fila)
    publicado = fila["publicado_con_n_interpretado"]
    n_lo, n_hi = grupo["n_interpretado"]["rango"]
    tipico = grupo["n_interpretado"]["tipico"]
    assert n_lo < tipico < n_hi
    lo, hi = _calcular_fila(grupo, fila, n=n_lo), _calcular_fila(grupo, fila, n=n_hi)
    con_tipico = _calcular_fila(grupo, fila, n=tipico)
    # H y la cota de control de salida crecen con n: el publicado, dentro.
    for magnitud in ("H_ft", "EL_ho_ft"):
        assert lo[magnitud] < publicado[magnitud] < hi[magnitud], magnitud
        assert abs(_diferencia_relativa(
            grupo, {"publicado": publicado}, magnitud, con_tipico[magnitud])
        ) <= CP_HDS5_DG1["tolerancia_de_la_fuente"]
    assert con_tipico["control"] == publicado["control"]
    lectura = CP_HDS5_DG1["tolerancia_de_lectura"]
    if publicado["control"] == "salida":
        # Gobierna la salida en TODO el rango de n, no solo con el tipico, y
        # la velocidad de salida no depende de n: Q/A(y_c), al 3 %.
        assert lo["control"] == hi["control"] == "salida"
        assert con_tipico["V_salida_por_y_c_ft_s"] == pytest.approx(
            publicado["V_salida_ft_s"], rel=lectura)
    else:
        # Gobierna la entrada: la velocidad de salida es la normal, que BAJA
        # al subir n; la publicada, dentro del intervalo.
        assert hi["V_salida_ft_s"] < publicado["V_salida_ft_s"] < lo["V_salida_ft_s"]


def test_ninguna_fila_del_ejemplo_publicado_cae_en_la_transicion():
    """
    Lo que el ejemplo publicado NO valida, dicho con el numero: ninguna de
    sus siete filas tiene q* entre 3.5 y 4.0, de modo que la recta de
    transicion del control de entrada no la toca ninguna. Valida las dos
    ramas: una fila no sumergida y seis sumergidas.
    """
    from src.constantes_normativas import KU_SI
    q_lo, q_hi = CP_HDS5_DG1["q_estrella_transicion"]
    ramas = {"no_sumergida": 0, "sumergida": 0}
    for nombre in ("circular", "cajon"):
        grupo = CP_HDS5_DG1[nombre]
        Q = grupo["Q_ft3_s"] * PIE_EN_METROS ** 3
        for fila in grupo["filas"]:
            if "D_in" in fila:
                seccion = SeccionCircular(fila["D_in"] * PULGADA_EN_METROS)
            else:
                seccion = SeccionRectangular(B=fila["B_ft"] * PIE_EN_METROS,
                                             H=fila["H_ft"] * PIE_EN_METROS)
            q = KU_SI * Q / (seccion.area_llena * math.sqrt(seccion.altura))
            assert not q_lo < q < q_hi, (fila["id"], q)
            ramas["no_sumergida" if q <= q_lo else "sumergida"] += 1
    assert ramas == {"no_sumergida": 1, "sumergida": 6}


def test_el_diseno_adoptado_por_el_ejemplo_circular_sale_con_el_motor_entero(
        concreto):
    """
    El tubo que el ejemplo ADOPTA (concreto de 54 in, campana en cabezal),
    por `M4.resolver_control` --las seis piezas juntas-- y no pieza a pieza:
    gobierna la entrada, como en el formulario, y la carga queda a menos del
    3 % de la cota 108.0 ft publicada.
    """
    grupo = CP_HDS5_DG1["circular"]
    fila = grupo["filas"][0]
    pie = PIE_EN_METROS
    material = replace(
        concreto, n_min=fila["n"], n_max=fila["n"],
        hds5=ConstantesHDS5.desde_dict(HDS5_INLET[fila["carta"]]))
    with con_valor("ke_entrada", fila["ke"],
                   motivo="el ke de la campana del ejemplo publicado (0.2), "
                          "que no es el de la embocadura del proyecto"):
        r = M4.resolver_control(
            SeccionCircular(fila["D_in"] * PULGADA_EN_METROS),
            Q=grupo["Q_ft3_s"] * pie ** 3, S=grupo["S"],
            L=grupo["L_ft"] * pie, TW=grupo["TW_ft"] * pie, material=material)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    publicado = fila["publicado"]
    assert r.HW / pie == pytest.approx(
        publicado["HW_entrada_ft"], rel=CP_HDS5_DG1["tolerancia_de_lectura"])
    assert r.V_salida.valor / pie == pytest.approx(
        publicado["V_salida_ft_s"], rel=CP_HDS5_DG1["tolerancia_de_lectura"])


@pytest.mark.pdf
def test_las_cifras_del_dorado_que_la_pagina_trae_en_texto_estan_en_la_pagina():
    """
    Los formularios son imagen, pero el enunciado repite en TEXTO varias de
    las cifras: se buscan en su pagina, junto con la frase del +-10 %.
    """
    fitz = pytest.importorskip("fitz")
    ruta = fuentes.ruta_pdf(fuentes.FUENTES["HDS5_3ED"])
    if not ruta.exists():
        pytest.skip(f"falta {ruta}")
    doc = fitz.open(ruta)

    def texto(pagina_pdf):
        return " ".join(doc[pagina_pdf - 1].get_text().split())

    assert CP_HDS5_DG1["frase_tolerancia_de_la_fuente"] in texto(
        CP_HDS5_DG1["pagina_pdf_tolerancia_de_la_fuente"])
    # El n interpretado del metal corrugado: el tipico de diseño y el rango
    # de la Tabla B.1, cada uno en su pagina.
    n_cmp = CP_HDS5_DG1["circular"]["n_interpretado"]
    assert n_cmp["frase_tipico"] in texto(n_cmp["pagina_pdf_tipico"])
    tabla_b1 = texto(n_cmp["pagina_pdf_rango"])
    assert "Manning's n Values for Culverts" in tabla_b1
    assert ("(Annular Corrugations) 2-2/3 by 1/2 in 68 by 13 mm "
            + n_cmp["frase_rango"]) in tabla_b1
    assert "2-2/3 by 1/2 in corrugations" in texto(273)
    enunciado = texto(273)
    for cifra in ("200 ft³/s", "3.5 ft", "0.01 ft/ft", "200 ft", "100 ft"):
        assert cifra in enunciado
    resultados = texto(274)
    assert 'Elhi = 108.0 ft for 54" RCP' in resultados
    assert 'Elhi = 106.8 ft for 60" RCP' in resultados
    assert '54" RCP Vo = 15.3 ft/s' in resultados
    cajon = texto(279) + " " + texto(280)
    for cifra in ("300 ft³/s", "4.0 ft", "0.02 ft/ft", "250 ft",
                  "Elhi = 107.9 ft", "Elho = 103.2 ft",
                  "Elhi = 109.6 ft for 5x5' RCB",
                  "Elhi = 108.6 ft for 5x5' RCB",
                  "Vo = 20.8 ft/s for 5x5' RCB"):
        assert cifra in cajon, cifra


# ===========================================================================
# 6 · Los criterios que el INFORME daba por vacios (INF-0.5)
# ===========================================================================

def test_un_indicador_disparado_sube_a_los_avisos_y_al_resumen(tmp_path):
    """
    Con 'regimen_v2b' = indicador_con_aviso (el valor del archivo) un
    conducto mas tendido que su cauce NO se descarta. Eso no puede quedar
    solo en la fila de la tabla: el RESUMEN decia «Verificaciones
    incumplidas: 0» y nada mas (auditor de T-2). El indicador sube a los
    avisos del punto, con su codigo, y el resumen lo cuenta aparte.
    """
    informe = _correr(tmp_path, {
        "globales": {"TW_m": 0.3}, "puntos": {"A-01": {"S_conducto": 0.004}}})
    a01, a02 = _punto_de(informe, "A-01"), _punto_de(informe, "A-02")
    assert a01.dimensionado and not a01.incumplidas()
    assert [v.codigo for v in a01.con_aviso()] == ["V2b"]
    assert a02.con_aviso() == ()
    (aviso,) = [a for a in a01.avisos() if a.startswith("V2b:")]
    assert "indicador disparado" in aviso and "no se detiene" in aviso
    # Y lleva la explicacion del veredicto, no solo el codigo.
    explicacion = a01.con_aviso()[0].paso.veredicto.explicacion
    assert explicacion and aviso.endswith(explicacion)
    assert not [a for a in a02.avisos() if a.startswith("V2b:")]
    resumen = informe.resumen()
    assert resumen.incumplidas == 0 and resumen.con_aviso == 1
    # Las tres salidas que lo dicen: el texto de la CLI, el JSON y la memoria.
    texto = cli.volcar(informe)
    assert "Verificaciones incumplidas: 0" in texto
    assert "Verificaciones con aviso: 1" in texto
    assert "aviso: V2b: indicador disparado" in texto
    volcado = cli.informe_json(informe)
    del_punto = next(p for p in volcado["puntos"] if p["id"] == "A-01")
    assert any(a.startswith("V2b:") for a in del_punto["avisos"])
    html = cli.memoria_html(
        informe, ruta_plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL))
    fila = re.search(r"Verificaciones con aviso</b>.*?<td[^>]*>(\d+)</td>",
                     html, re.S)
    assert fila is not None and fila.group(1) == "1"


def test_sin_indicadores_el_resumen_dice_cero_avisos(tmp_path):
    informe = _correr(tmp_path, {"globales": {"TW_m": 0.3}})
    assert informe.resumen().con_aviso == 0
    assert "Verificaciones con aviso: 0" in cli.volcar(informe)


def test_el_estado_de_los_tres_criterios_que_el_encargo_nombra():
    """
    Dos de los tres ya tenian valor (el INFORME los daba por vacios);
    `regimen_v2b` cambia de valor de archivo y `hw_entrada_fuera_de_rango`
    deja de estar vacio. Las etiquetas siguen siendo [A]: la fuente no
    prescribe ni el regimen ni el piso.
    """
    regimen = ca.CRITERIOS["regimen_v2b"]
    assert regimen.valor == "indicador_con_aviso" and regimen.etiqueta == "A"
    assert tuple(regimen.sensibilidad) == ("umbral_duro", "indicador_con_aviso")
    piso = ca.CRITERIOS["hw_entrada_fuera_de_rango"]
    assert piso.valor == "energia_critica" and piso.etiqueta == "A"
    assert tuple(piso.sensibilidad) == ("energia_critica", "descartar")
    assert not piso.fuente.startswith("PENDIENTE")
    assert "HDS5_3ED.A.2.1#FORMA_1" in piso.fuente
    acceso = ca.CRITERIOS["acceso_mantenimiento_v2b"]
    assert acceso.valor == "camara_o_buzon_en_cabecera"
    assert not acceso.fuente.startswith("PENDIENTE")
    assert "MC_HHD.4.1.1.3.7d" in acceso.fuente
    # TW_receptor SIGUE SIENDO ENTRADA: no se adopta.
    assert ca.CRITERIOS["TW_receptor"].valor is None
    assert "hw_entrada_fuera_de_rango" not in ca.criterios_de_perfil_sin_valor()
    assert "TW_receptor" in ca.criterios_de_perfil_sin_valor()


def test_la_tabla_a1_no_lleva_ninguna_nota_sobre_ks():
    """
    El encargo citaba «HDS-5 Tabla A.1, nota de Ks·S». La transcripcion de
    la tabla solo lleva al pie sus referencias bibliograficas; lo que el
    HDS-5 dice del termino esta en el num. A.2.1, el 3.3.4 y el A.3.
    """
    reg = construir()
    notas = reg.tabla("HDS5_3ED.TA1").notas_al_pie
    assert [n.texto.texto for n in notas] == ["Bossy 1963"]
    assert "Slope correction" in reg.cita("HDS5_3ED.A.2.1#KS").texto_literal.texto
    assert "specific head at critical depth" in reg.cita(
        "HDS5_3ED.A.2.1#FORMA_1").texto_literal.texto
    assert "slope correction term of -0.5S" in reg.cita(
        "HDS5_3ED.3.3.4#KS").texto_literal.texto


def test_el_piso_de_energia_critica_rige_sin_declarar_nada(concreto):
    """
    Con el valor de archivo, la carta fuera de rango ya no detiene: HW = H_c,
    con el piso publicado y la eleccion fundada en `F4.PISO_HW`.
    """
    sec, Q, S = SeccionCircular(0.90), 0.05, 0.45
    critico = M4.tirante_critico(Q, sec)
    assert S > M4.pendiente_limite_de_signo(Q, sec, concreto.hds5, critico)
    entrada = M4.control_entrada(Q, sec, S, concreto.hds5, critico)
    assert entrada.piso is not None and entrada.piso.adoptado == "energia_critica"
    assert entrada.HW == pytest.approx(critico.H_c, rel=REL_FORMULA)
    assert entrada.piso.HW_sobre_D_formula <= 0
    r = M4.resolver_control(sec, Q=Q, S=S, L=10.0, TW=0.0, material=concreto)
    paso = next(p for p in r.pasos if p.codigo == "4.2"
                and p.fundamento_id == "F4.CONTROL")
    (eleccion,) = paso.elecciones
    assert eleccion.fundamento_id == "F4.PISO_HW"
    assert eleccion.valor == "energia_critica"
    assert eleccion.clave_criterio == "hw_entrada_fuera_de_rango"
    assert eleccion.cita_id == "HDS5_3ED.A.2.1#FORMA_1"
    # Y sin piso (pendiente corriente) el paso no lleva ninguna eleccion.
    normal = M4.resolver_control(sec, Q=0.6, S=0.006, L=10.0, TW=0.0,
                                 material=concreto)
    paso = next(p for p in normal.pasos if p.codigo == "4.2"
                and p.fundamento_id == "F4.CONTROL")
    assert paso.elecciones == ()


def test_v2b_con_el_valor_de_archivo_avisa_y_no_descarta():
    """
    `indicador_con_aviso`: la comparacion es la misma y el conducto mas plano
    que su cauce NO descarta la seccion. Y el paso cita la exigencia [N] del
    mantenimiento (num. 4.1.1.3.7 d)).
    """
    v = M5.v2b_sedimentacion(punto=_punto(S_cauce=0.006),
                             resultado=_resultado(S=0.004))
    assert v.cumple and v.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert "MC_HHD.4.1.1.3.7d" in v.paso.citas_textuales
    cita = construir().cita("MC_HHD.4.1.1.3.7d")
    assert cita.titulo_numeral.endswith("Mantenimiento y limpieza")
    alineado = M5.v2b_sedimentacion(punto=_punto(S_cauce=0.006),
                                    resultado=_resultado(S=0.006))
    assert alineado.cumple
    assert alineado.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE
    ca.establecer_valor_dinamico("regimen_v2b", "umbral_duro")
    assert not M5.v2b_sedimentacion(punto=_punto(S_cauce=0.006),
                                    resultado=_resultado(S=0.004)).cumple


def test_el_acceso_de_mantenimiento_es_un_booleano_opcional_por_punto(tmp_path):
    """
    `true` se imprime, `false` avisa, y sin declarar no pasa nada. Ningun
    valor cambia un calculo. Y no vale nada que no sea un booleano del JSON.
    """
    informe = _correr(tmp_path, {
        "globales": {"TW_m": 0.3, "acceso_mantenimiento_previsto": True},
        "puntos": {"A-02": {"acceso_mantenimiento_previsto": False}}})
    a01, a02 = _punto_de(informe, "A-01"), _punto_de(informe, "A-02")
    assert a01.acceso_mantenimiento.valor is True
    assert _avisos_sin_geometria(a01) == (AVISO_DEL_CAUDAL_DECLARADO,)
    assert _avisos_sin_geometria(a02) == (AVISO_DEL_CAUDAL_DECLARADO,
                                          AVISO_SIN_ACCESO_DE_MANTENIMIENTO)
    assert "4.1.1.3.7 d)" in AVISO_SIN_ACCESO_DE_MANTENIMIENTO
    texto = cli.volcar(informe)
    assert "Acceso de mantenimiento: previsto en los planos" in texto
    assert f"aviso: {AVISO_SIN_ACCESO_DE_MANTENIMIENTO}" in texto
    volcado = {p["id"]: p for p in cli.informe_json(informe)["puntos"]}
    assert volcado["A-01"]["datos_declarados"][
        "acceso_mantenimiento_previsto"]["valor"] is True
    # No decide nada: el mismo punto sin la declaracion dimensiona igual.
    sin = _punto_de(_correr(tmp_path, {"globales": {"TW_m": 0.3}}), "A-02")
    assert sin.acceso_mantenimiento is None
    assert _avisos_sin_geometria(sin) == (AVISO_DEL_CAUDAL_DECLARADO,)
    assert sin.resultado.seccion == a02.resultado.seccion
    for mala in (1, 0, "si", "true", None):
        with pytest.raises(DatoInvalidoError):
            _externos(tmp_path, {"globales": {
                "acceso_mantenimiento_previsto": mala}})


def test_las_dos_claves_nuevas_estan_en_el_censo_y_tienen_via_alterna():
    for clave in ("seccion_receptor_medida", "acceso_mantenimiento_previsto"):
        assert clave in servicio.CLAVES_EXTERNAS
        assert clave in servicio.EXTERNOS_CON_VIA_ALTERNA
        assert ve.variable(clave).poblacion.value == "dato_externo"
    assert ve.variable("seccion_receptor_medida").criterio_destino == \
        "seccion_receptor"


# ===========================================================================
# 7 · El receptor seco (INF-5.1.7)
# ===========================================================================

def _csv_con_receptor(tmp_path, valor):
    lineas = CSV.read_text(encoding="utf-8").splitlines()
    campos = lineas[1].split(",")
    campos[lineas[0].split(",").index("Q_receptor_m3s")] = valor
    lineas[1] = ",".join(campos)
    ruta = tmp_path / "puntos.csv"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta


def test_m0_admite_el_receptor_seco_y_rechaza_el_negativo(tmp_path):
    puntos = M0.cargar_puntos(_csv_con_receptor(tmp_path, "0"))
    assert puntos[0].Q_receptor_m3s == pytest.approx(0.0, abs=ABS_CERO)
    with pytest.raises(DatoInvalidoError) as exc:
        M0.cargar_puntos(_csv_con_receptor(tmp_path, "-0.5"))
    assert exc.value.campo == "Q_receptor_m3s"
    # La ficha de la variable y M0 dicen ya lo mismo.
    assert ">= 0" in ve.variable("Q_receptor_m3s").resolucion.dominio
    # Y la celda vacia sigue siendo «sin dato», no «seco».
    assert M0.cargar_puntos(CSV)[0].Q_receptor_m3s is None


def test_el_receptor_seco_no_aporta_lamina_por_la_via_3():
    """
    Via 3 con Q = 0: el tirante del receptor es cero sin resolver Manning, y
    el TW es lo que el FONDO del receptor quede por encima del fondo de la
    salida (o salida libre si queda por debajo).
    """
    assert M3.tirante_normal_trapecial(Q=0.0, seccion=MEDIDA) == pytest.approx(
        0.0, abs=ABS_CERO)
    with pytest.raises(DatoInvalidoError):
        M3.tirante_normal_trapecial(Q=-0.1, seccion=MEDIDA)
    punto = _punto(Q_receptor_m3s=0.0, cota_fondo_receptor=41.30)
    libre = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=41.90,
                              seccion_medida=MEDIDA)
    assert libre.via is ViaDelTW.MANNING_RECEPTOR
    assert libre.valor == pytest.approx(0.0, abs=ABS_CERO)
    alto = M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=41.00,
                             seccion_medida=MEDIDA)
    assert alto.valor == pytest.approx(0.30, rel=REL_FORMULA)


def test_un_csv_con_el_receptor_seco_corre(tmp_path):
    informe = servicio.correr(
        _csv_con_receptor(tmp_path, "0"),
        servicio.cargar_datos_externos(None, {"luz_m": 2.75}), "perfil")
    a01 = _punto_de(informe, "A-01")
    assert a01.tw_sec13.via is ViaDelTW.MANNING_RECEPTOR
    assert a01.tw_sec13.valor == pytest.approx(0.0, abs=ABS_CERO)
    assert a01.dimensionado


# ===========================================================================
# La parada (c): ningun diametro de la linea base se mueve
# ===========================================================================

def test_los_diametros_de_la_linea_base_no_se_movieron(tmp_path):
    """
    Las dos corridas que dimensionan: la ancha de la linea base (A-01 y A-02)
    y la de la guia de perfil (los cuatro puntos). Con los valores de archivo
    de T-2 --regimen_v2b con aviso, el piso de energia critica, la banda de
    pendiente, V1 con «no_cumple»-- cada punto conserva su seccion y su
    carga.
    """
    ancha = servicio.correr(
        CSV, servicio.cargar_datos_externos(EXTERNOS_ANCHOS, {"luz_m": 2.75}),
        "perfil")
    secciones = {p.punto.id: p.resultado.seccion.etiqueta()
                 for p in ancha.puntos if p.dimensionado}
    assert secciones == {"A-01": "Ø 0.90 m", "A-02": "Ø 0.90 m"}
    cargas = {p.punto.id: p.resultado.resultado_hidraulico.HW
              for p in ancha.puntos if p.dimensionado}
    # Contra la linea base COMPROMETIDA, leida del archivo y no copiada aqui:
    # la seccion y la carga de cada punto dimensionado.
    comprometido = json.loads(
        (RAIZ / "tests" / "linea_base_familia_c" / "informe_perfil_ancho.json")
        .read_text(encoding="utf-8"))
    de_la_linea_base = {p["id"]: p["diseno"] for p in comprometido["puntos"]
                        if p["dimensionado"]}
    assert set(de_la_linea_base) == set(secciones) == set(cargas)
    for id_punto, diseno in de_la_linea_base.items():
        assert secciones[id_punto] == diseno["seccion"]
        assert cargas[id_punto] == pytest.approx(diseno["HW_gobernante_m"],
                                                 rel=REL_FORMULA)
    # Y ninguna verificacion de un punto dimensionado es un aviso nuevo.
    for p in ancha.puntos:
        if p.dimensionado:
            assert all(v.paso is None or v.paso.veredicto is None
                       or v.paso.veredicto.tipo is not TipoDeVeredicto.INDICADOR
                       for v in p.resultado.verificaciones)
