"""
tests/test_t3_correcciones_auditoria.py
=======================================
Las correcciones de la AUDITORIA ADVERSARIAL de T-3 (Familia C, INF-0.4),
hallazgo por hallazgo (H1 a H12), con las resoluciones del orquestador y las
decisiones del dueño del 2026-11-12.

  H1   'n_manning_cajon' pasa a [C] con la fila PROPIA del marco: HDS-5 Tabla
       B.1, «Concrete Boxes | Smooth | 0.012-0.015» (pag. impresa B.6, PDF
       208). La fila «afinado» de la Tabla N 09 (lectura corregida, 0.011 /
       0.014) queda como alternativa barrible; el texto del num. B.3 (0.012 a
       0.022 en vaciado in situ, pag. impresa B.2, PDF 204) es la ventana
       hacia arriba. La SECCION de C-01 no se mueve.
  H2   Remanso en canal de pendiente FUERTE (y_n <= y_c): dh/S no es cota
       inferior -- S1 que termina en resalto --, y el remanso NO CONCLUYE.
  H3   Remanso con VC2 fuera de tolerancia: el HW sale de una descarga libre
       que el canal no tiene, y el remanso NO CONCLUYE.
  H4   G2 y VC2 no se contradicen en la Familia C: G2 admite por debajo la
       tolerancia de VC2. Familias A y B: G2 no cambia.
  H5   G1 del MARCO avisa (INDICADOR) cuando solo falta la cobertura
       adoptada por analogia (0.3048 m); la fuente admite el marco sin
       relleno (MTC 4.1.1.3.4 a), Lamina N 03, AASHTO LRFD 12.6.6.3). El
       resguardo sigue bloqueando. G1 del TUBO no cambia.
  H6   V7 sin peso propio: no se toca V7; se corrige la CAUSA escrita en las
       fichas y se abre ficha diferida sobre `M5.v7_flotacion`.
  H7   La cita de la formula de 7.B.R, 7.B.M y VC2 queda vacia: la cita no
       contiene esa formula; va a `citas_textuales` y al umbral.
  H8   Mutantes vivos y el test vacuo de la pendiente del canal.
  H9   El aviso de VC2 imprime la S que cerraria el empalme.
  H10  La errata de la Tabla N 09 se sostiene en la evidencia INTERNA de la
       pagina, no en Ven Te Chow (que no esta en normas/).
  H11  La progresion de secciones es la DECISION del dueño, no provisional.
  H12  'espesor_pared_cajon' queda [A], con la razon en la ficha.

LOS ESPERADOS SALEN DE LA FUENTE O DE LA CUENTA A MANO: el tirante critico
de un rectangulo por la formula cerrada, el normal por una biseccion escrita
aqui, las cotas por la aritmetica de las cotas del fixture.

EL ROJO SE MIDIO contra el arbol de la FASE A rebasada sobre `e78a4e7`
(`c6712d4`), con este archivo y el codigo de antes: la primera version (52
tests, antes del codigo) dio 23 rojos y 29 verdes; el archivo final (63, con
los nueve que sumo la medida de mutacion) da 33 rojos y 30 verdes. Los
verdes son guardias y matadores de mutantes, que valen antes y despues.
"""
from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src import constantes_normativas as cn
from src import servicio
from src.constantes_fisicas import G
from src.modelos import (DatoInvalidoError, ErrorProyecto,
                         EstadoDeVerificacion, FormaSeccion, SeccionCircular,
                         SeccionReceptor, SeccionRectangular, TipoDeVeredicto,
                         TipoMaterial)
from src.modulos import M7_geometria as M7
from src.modulos.M0_carga import cargar_puntos
from src.modulos.M2_material import catalogo
from src.normativa import registro
from tests.apoyo.aproximacion import ABS_CERO
from tests.apoyo.criterios import con_valor, declarados

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
V8 = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
DIFERIDAS = RAIZ / "docs" / "decisiones_diferidas.md"

ABS = 1e-9
TOL_RESULTADO = 5e-4
TOL_BISECCION = 1e-6
# La longitud dh/S hereda el error de la biseccion dividido por S (0.001 en
# el canal suave del caso de H2).
S_CANAL_SUAVE = 0.001
TOL_LONGITUD_SUAVE = TOL_BISECCION / S_CANAL_SUAVE

# Lo que la guia de perfil pone a C-01 (coronacion y datos del canal).
CORONACION_GUIA = 38.30
EXTERNOS_GUIA = {"globales": {"TW_m": 0.3, "L_hidraulico_m": 120.0},
                 "puntos": {"C-01": {"Q_m3s": 0.85, "S_cauce": 0.006,
                                     "S_conducto": 0.006}}}
# Longitud de C-01 por la formula de T-6, a mano (la misma que
# test_t3_familia_c): ancho 9.60, H = 2.20 en los dos extremos, talud 2.0,
# esviaje 30 grados, S = 0.006.
L_C01 = (9.60 + 2.0 * (2.20 + 2.20)) / (math.cos(math.radians(30.0))
                                        - 2.0 * 0.006)


# --- la aritmetica escrita, independiente del codigo -------------------------
def _yn_rectangular(Q, b, S, n):
    """Biseccion de Manning en un rectangulo abierto (b, y)."""
    def q(y):
        A, P = b * y, b + 2.0 * y
        return (1.0 / n) * A * (A / P) ** (2.0 / 3.0) * math.sqrt(S)
    lo, hi = 1e-9, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if q(mid) > Q else (mid, hi)
    return 0.5 * (lo + hi)


def _yn_trapecial(Q, b, z, S, n):
    def q(y):
        A = (b + z * y) * y
        P = b + 2.0 * y * math.sqrt(1.0 + z * z)
        return (1.0 / n) * A * (A / P) ** (2.0 / 3.0) * math.sqrt(S)
    lo, hi = 1e-9, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if q(mid) > Q else (mid, hi)
    return 0.5 * (lo + hi)


def _yc_trapecial(Q, b, z):
    """Q^2 T = g A^3 por biseccion (la condicion de HDS-5 A.3.1, Fr = 1)."""
    def f(y):
        A = (b + z * y) * y
        T = b + 2.0 * z * y
        return Q * Q * T - G * A ** 3
    lo, hi = 1e-9, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if f(mid) < 0 else (mid, hi)
    return 0.5 * (lo + hi)


def _puntos():
    return {p.id: p for p in cargar_puntos(CSV)}


def _c01():
    return _puntos()["C-01"]


def _marco():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO,
                    forma=FormaSeccion.RECTANGULAR)


def _csv_c01(tmp_path, *, rasante=None, subrasante=None,
             coronacion=CORONACION_GUIA):
    lineas = CSV.read_text(encoding="utf-8").splitlines()
    cab = lineas[0].split(",")
    salida = [lineas[0]]
    for linea in lineas[1:]:
        if linea.startswith("C-01,"):
            celdas = linea.split(",")
            celdas[cab.index("cota_coronacion_canal")] = f"{coronacion:.2f}"
            if rasante is not None:
                celdas[cab.index("cota_rasante")] = f"{rasante:.2f}"
            if subrasante is not None:
                celdas[cab.index("cota_subrasante")] = f"{subrasante:.2f}"
            linea = ",".join(celdas)
        salida.append(linea)
    ruta = tmp_path / "puntos.csv"
    ruta.write_text("\n".join(salida) + "\n", encoding="utf-8")
    return ruta


def _externos(tmp_path, extra=None, globales=None):
    datos = json.loads(json.dumps(EXTERNOS_GUIA))
    if extra:
        datos["puntos"]["C-01"].update(extra)
    if globales:
        datos["globales"].update(globales)
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {"luz_m": 2.75})


def _informe_c01(informe):
    return next(p for p in informe.puntos if p.punto.id == "C-01")


@pytest.fixture
def corrida_guia(tmp_path):
    return servicio.correr(_csv_c01(tmp_path), _externos(tmp_path),
                           alcance=servicio.ALCANCE_PERFIL)


# ===========================================================================
# H1 · el n del marco es la fila PROPIA de HDS-5 (Tabla B.1, Concrete Boxes)
# ===========================================================================

def test_h1_el_n_del_marco_es_la_fila_concrete_boxes_y_es_C():
    c = ca.CRITERIOS["n_manning_cajon"]
    assert c.etiqueta == "C"
    assert c.valor == "concrete_boxes"
    # La tabla del valor de archivo va PRIMERA (la que la ventana muestra);
    # la Tabla N 09 queda segunda, la de la alternativa por analogia.
    assert c.resolucion.tablas == ("HDS5_3ED.TB.1", "MC_HHD.T09")
    # El par sale de la fila transcrita, no escrito a mano: pag. impresa B.6
    # (PDF 208), «Concrete Boxes | Smooth | 0.012-0.015 | FHWA 1961».
    fila = registro.construir().tabla("HDS5_3ED.TB.1").fila("concrete_boxes")
    assert (fila.valores["n_min"], fila.valores["n_max"]) == pytest.approx(
        (0.012, 0.015), abs=ABS)
    assert cn.MANNING_CAJON_HDS5["concrete_boxes"] == pytest.approx(
        (0.012, 0.015), abs=ABS)


def test_h1_el_material_marco_lleva_el_par_de_la_tabla_B1():
    m = _marco()
    assert (m.n_min, m.n_max) == pytest.approx((0.012, 0.015), abs=ABS)


def test_h1_el_paso_del_n_del_marco_es_el_de_la_tabla_B1():
    """El paso 4.1 del marco nombra la Tabla B.1 y el B.3, con su fundamento."""
    paso = _marco().pasos[-1]
    assert paso.fundamento_id == "F4.N_CAJON_TB1"
    assert paso.formula_cita_id == "HDS5_3ED.TB.1"
    assert "HDS5_3ED.B.3#CAJON_IN_SITU" in paso.citas_textuales
    with declarados({"n_manning_cajon": "concreto_afinado"}):
        alternativa = _marco().pasos[-1]
    assert alternativa.fundamento_id == "F4.N_CAJON"


def test_h1_la_alternativa_barrible_es_afinado_de_la_tabla_09():
    with declarados({"n_manning_cajon": "concreto_afinado"}):
        m = _marco()
    assert (m.n_min, m.n_max) == pytest.approx((0.011, 0.014), abs=ABS)
    sens = " ".join(ca.CRITERIOS["n_manning_cajon"].sensibilidad)
    assert "concreto_afinado" in sens


def test_h1_una_fila_de_tubo_de_la_tabla_B1_no_es_del_marco():
    """La Tabla B.1 trae filas de tubo: la del marco es una sola."""
    with declarados({"n_manning_cajon": "concrete_pipe"}):
        with pytest.raises(DatoInvalidoError):
            _marco()


def test_h1_la_ficha_cita_B3_dice_la_direccion_y_retira_la_frase_del_acabado():
    c = ca.CRITERIOS["n_manning_cajon"]
    texto = " ".join((c.justificacion, c.fuente, *c.sensibilidad))
    assert "describe el acabado que tiene un marco" not in texto
    assert "HDS5_3ED.B.3#CAJON_IN_SITU" in texto
    assert "0.022" in texto
    # La DIRECCION de cada extremo, dicha: n alto, lado seguro para tirante
    # y HW; n bajo, lado seguro para V3 y el d50.
    assert "lado seguro" in texto
    cita = registro.construir().cita("HDS5_3ED.B.3#CAJON_IN_SITU")
    assert (cita.pagina_impresa, cita.pagina_pdf) == ("B.2", 204)
    assert "0.012 to 0.022" in cita.texto_literal.texto


def test_h1_C01_de_la_guia_no_mueve_la_seccion_ni_la_carga(corrida_guia):
    """
    La seccion sigue en 1.20 x 0.90 y el HW de entrada (que no depende de n)
    en 0.589 m. Lo que se mueve es el tirante normal, con n_max = 0.015:
    biseccion de Manning en el rectangulo de 1.20 m, S = 0.006.
    """
    c01 = _informe_c01(corrida_guia)
    assert c01.dimensionado
    s = c01.resultado.seccion
    assert (s.B, s.H) == pytest.approx((1.20, 0.90), abs=ABS)
    r = c01.resultado.resultado_hidraulico
    assert r.HW == pytest.approx(0.589, abs=TOL_RESULTADO)
    assert r.y_normal == pytest.approx(
        _yn_rectangular(0.85, 1.20, 0.006, 0.015), abs=TOL_BISECCION)


def test_h1_corrida_6_no_mueve_la_seccion(tmp_path):
    """La corrida de la linea base (S 0.004, TW 0.30): marco 1.20 x 0.90."""
    informe = servicio.correr(
        _csv_c01(tmp_path),
        _externos(tmp_path, {"S_conducto": 0.004}),
        alcance=servicio.ALCANCE_PERFIL)
    c01 = _informe_c01(informe)
    assert c01.dimensionado
    s = c01.resultado.seccion
    assert (s.B, s.H) == pytest.approx((1.20, 0.90), abs=ABS)


# ===========================================================================
# H10 · la errata de la Tabla N 09, sostenida en la pagina y no en Chow
# ===========================================================================

def test_h10_la_errata_se_sostiene_en_la_evidencia_interna_de_la_pagina():
    d = registro.construir().discrepancia("DIS-MCHHD-T09-A2-DESPLAZADA")
    quienes = {p.quien for p in d.partes}
    assert not any("Chow" in q for q in quienes), quienes
    assert "Chow" not in d.gana
    texto = " ".join(p.que_dice for p in d.partes) + d.por_que
    # El corrimiento alcanza tambien a B.1, B.2 y C (pag. impresa 75).
    for bloque in ("B.1", "B.2", "C."):
        assert bloque in texto, bloque
    # Y la lectura literal seria MAS CONSERVADORA para capacidad.
    assert "conservadora" in d.efecto_si_se_sigue_la_otra


def test_h10_ninguna_ficha_dice_contrastada_con_chow():
    c = ca.CRITERIOS["n_manning_cajon"]
    assert "contrastada con Ven Te Chow" not in c.fuente + c.justificacion


def test_h10_la_v8_declara_la_lectura_corregida_de_la_tabla_09():
    v8 = V8.read_text(encoding="utf-8")
    i = v8.index("**Tabla Nº 09 — Manning**")
    tramo = v8[i:i + 4000]
    assert "DIS-MCHHD-T09-A2-DESPLAZADA" in tramo
    assert "concrete_boxes" in tramo or "Concrete Boxes" in tramo


# ===========================================================================
# H2 y H3 · el remanso del canal: cuando no concluye, lo dice
# ===========================================================================

def test_h2_el_tirante_critico_del_canal_cumple_la_condicion_critica():
    """
    `M3.tirante_critico_trapecial`: en un rectangulo, la formula cerrada
    y_c = (Q^2/(g b^2))^(1/3); en un trapecio, la biseccion de Q^2 T = g A^3
    escrita aqui. Con Q = 0 no hay lamina.
    """
    from src.modulos.M3_hidraulica import tirante_critico_trapecial
    rect = SeccionReceptor(b_m=1.20, z_HV=0.0, S=0.02, n=0.014,
                           altura_total_m=1.20)
    trap = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                           altura_total_m=2.0)
    assert tirante_critico_trapecial(Q=0.85, seccion=rect) == pytest.approx(
        (0.85 ** 2 / (G * 1.20 ** 2)) ** (1.0 / 3.0), abs=TOL_BISECCION)
    assert tirante_critico_trapecial(Q=0.85, seccion=trap) == pytest.approx(
        _yc_trapecial(0.85, 1.0, 1.0), abs=TOL_BISECCION)
    assert tirante_critico_trapecial(Q=0.0, seccion=trap) == pytest.approx(
        0.0, abs=ABS_CERO)
    with pytest.raises(DatoInvalidoError):
        tirante_critico_trapecial(Q=-0.1, seccion=trap)


def test_h2_canal_de_pendiente_fuerte_el_remanso_no_concluye():
    """
    El caso del auditor: canal rectangular b = 1.20, n = 0.014, S = 0.02,
    Q = 0.85, HW = 0.90. A mano: y_c = (Q^2/(g b^2))^(1/3) = 0.371 > y_n =
    0.231: el remanso es una S1 que termina en resalto y dh/S NO acota.
    """
    canal = SeccionReceptor(b_m=1.20, z_HV=0.0, S=0.02, n=0.014,
                            altura_total_m=1.20)
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.90,
                           Q=0.85, seccion_canal=canal)
    y_c = (0.85 ** 2 / (G * 1.20 ** 2)) ** (1.0 / 3.0)
    y_n = _yn_rectangular(0.85, 1.20, 0.02, 0.014)
    assert y_c == pytest.approx(0.371, abs=TOL_RESULTADO)
    assert y_n == pytest.approx(0.231, abs=TOL_RESULTADO)
    assert rem.evaluado and not rem.concluye
    assert rem.y_critico_canal_m == pytest.approx(y_c, abs=TOL_BISECCION)
    assert rem.y_normal_canal_m == pytest.approx(y_n, abs=TOL_BISECCION)
    assert rem.longitud_minima_m is None
    assert "resalto" in rem.aviso and "AL MENOS" not in rem.aviso
    assert "no concluye" in rem.aviso


def test_h2_canal_suave_sigue_dando_la_cota_inferior():
    """b = 1, z = 1, n = 0.025, S = 0.001: y_c < y_n, dh/S es cota inferior."""
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.90,
                           Q=0.85, seccion_canal=canal)
    y_n = _yn_trapecial(0.85, 1.0, 1.0, 0.001, 0.025)
    y_c = _yc_trapecial(0.85, 1.0, 1.0)
    assert y_c < y_n
    assert rem.concluye
    assert rem.y_critico_canal_m == pytest.approx(y_c, abs=TOL_BISECCION)
    assert rem.longitud_minima_m == pytest.approx((0.90 - y_n) / S_CANAL_SUAVE,
                                                  abs=TOL_LONGITUD_SUAVE)
    assert "AL MENOS" in rem.aviso


def test_h3_con_VC2_fuera_de_tolerancia_el_remanso_no_concluye():
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    vc2 = M7.vc2_empalme_canal(punto=_c01(), cota_salida_m=36.80)
    assert vc2.estado is EstadoDeVerificacion.INDICADOR
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.60,
                           Q=0.85, seccion_canal=canal, vc2=vc2)
    assert rem.evaluado and not rem.concluye
    assert rem.longitud_minima_m is None and rem.sobreelevacion_m is None
    assert "VC2" in rem.aviso and "descarga libre" in rem.aviso
    assert "no levanta" not in rem.aviso


def test_h3_la_corrida_de_la_guia_con_la_seccion_del_canal_no_concluye(
        tmp_path):
    """
    El caso del auditor: la guia con `seccion_receptor_medida` (b 1.0, z 1.0,
    n 0.025, S 0.001). VC2 avisa +0.57 m y el aviso del remanso ya no dice
    que la obra no levanta la lamina.
    """
    canal = {"b_m": 1.0, "z_HV": 1.0, "S": 0.001, "n": 0.025,
             "altura_total_m": 1.2}
    informe = servicio.correr(
        _csv_c01(tmp_path), _externos(tmp_path,
                                      {"seccion_receptor_medida": canal}),
        alcance=servicio.ALCANCE_PERFIL)
    c01 = _informe_c01(informe)
    rem = c01.geometria.remanso_canal
    assert rem.evaluado and not rem.concluye
    avisos = " ".join(c01.avisos())
    assert "no levanta la lamina" not in avisos
    assert "VC2" in rem.aviso


def test_h3_el_volcado_lleva_si_el_remanso_concluye(tmp_path):
    import cli
    canal = {"b_m": 1.0, "z_HV": 1.0, "S": 0.001, "n": 0.025,
             "altura_total_m": 1.2}
    informe = servicio.correr(
        _csv_c01(tmp_path), _externos(tmp_path,
                                      {"seccion_receptor_medida": canal}),
        alcance=servicio.ALCANCE_PERFIL)
    datos = cli.informe_json(informe)
    c01 = next(p for p in datos["puntos"] if p["id"] == "C-01")
    rem = c01["geometria"]["remanso_canal"]
    assert rem["concluye"] is False
    assert rem["y_critico_canal_m"] == pytest.approx(
        _yc_trapecial(0.85, 1.0, 1.0), abs=TOL_RESULTADO)
    assert rem["longitud_minima_m"] is None


# ===========================================================================
# H4 · G2 y VC2 en la Familia C: una sola banda
# ===========================================================================

@pytest.mark.parametrize("cota_salida, g2, vc2", [
    (36.205, EstadoDeVerificacion.CUMPLE, EstadoDeVerificacion.CUMPLE),
    (36.195, EstadoDeVerificacion.CUMPLE, EstadoDeVerificacion.CUMPLE),
    (36.185, EstadoDeVerificacion.NO_CUMPLE, EstadoDeVerificacion.INDICADOR),
    (36.215, EstadoDeVerificacion.CUMPLE, EstadoDeVerificacion.INDICADOR),
])
def test_h4_G2_y_VC2_no_se_contradicen_en_la_familia_C(cota_salida, g2, vc2):
    p = _c01()
    assert M7.g2_cota_salida(punto=p, cota_salida_m=cota_salida).estado is g2
    assert M7.vc2_empalme_canal(punto=p,
                                cota_salida_m=cota_salida).estado is vc2


@pytest.mark.parametrize("desajuste, estado", [
    (-0.005, EstadoDeVerificacion.NO_CUMPLE),
    (0.0, EstadoDeVerificacion.CUMPLE),
])
def test_h4_G2_no_cambia_en_la_familia_A(desajuste, estado):
    p = _puntos()["A-01"]
    v = M7.g2_cota_salida(punto=p,
                          cota_salida_m=p.cota_fondo_receptor + desajuste)
    assert v.estado is estado


# ===========================================================================
# H5 · G1 del marco avisa cuando solo falta la cobertura adoptada
# ===========================================================================

def _tamizado_marco(*, rasante, subrasante, HW):
    p = dataclasses.replace(_c01(), cota_rasante=rasante,
                            cota_subrasante=subrasante)
    return M7.tamizado_rasante(punto=p, material=_marco(),
                               seccion=SeccionRectangular(1.20, 0.90), HW=HW)


def test_h5_G1_del_marco_avisa_si_solo_falta_la_cobertura_adoptada():
    """
    Clave exterior 36.90 + 0.90 + 0.20 = 38.00; subrasante 38.20: 0.20 m de
    relleno, menos que los 0.3048 adoptados. Con HW = 0.30 el resguardo
    (38.20 >= 36.90 + 0.30 + resguardo) se cumple. G1 avisa y no bloquea.
    """
    t = _tamizado_marco(rasante=38.35, subrasante=38.20, HW=0.30)
    assert t.cobertura_como_aviso
    assert t.factible
    assert not t.alcanza_cobertura_adoptada
    assert t.cota_por_cobertura_exigible == pytest.approx(38.00 + 0.15,
                                                          abs=ABS)
    g1 = M7.g1_rasante_congelada(t)
    assert g1.cumple
    assert g1.estado is EstadoDeVerificacion.INDICADOR
    explicacion = g1.paso.veredicto.explicacion
    assert "12.6.6.3" in explicacion and "analogia" in explicacion


def test_h5_G1_del_marco_bloquea_si_falta_el_resguardo():
    t = _tamizado_marco(rasante=38.35, subrasante=38.20, HW=0.60)
    assert not t.factible
    g1 = M7.g1_rasante_congelada(t)
    assert not g1.cumple
    assert g1.estado is EstadoDeVerificacion.NO_CUMPLE


def test_h5_G1_del_tubo_no_cambia():
    p = _puntos()["A-01"]
    p = dataclasses.replace(p, cota_rasante=p.cota_fondo_receptor + 2.50,
                            cota_subrasante=p.cota_fondo_receptor + 2.35)
    t = M7.tamizado_rasante(
        punto=p, material=catalogo(TipoMaterial.CONCRETO_REFORZADO),
        seccion=SeccionCircular(0.90), HW=0.20)
    assert not t.cobertura_como_aviso
    assert t.cota_por_cobertura_exigible is None


def test_h5_la_cobertura_cita_los_tres_textos_y_dice_que_es_mas_restrictiva():
    c = ca.CRITERIOS["cobertura_minima_cajon"]
    texto = " ".join((c.justificacion, c.fuente))
    for cita in ("MC_HHD.4.1.1.3.4a#NIVELES", "MC_HHD.LAMINA_03",
                 "AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA"):
        assert cita in texto, cita
    assert "mas restrictivo" in texto
    assert "bloquea hasta que el proyectista declare" not in texto
    cita = registro.construir().cita("AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA")
    assert (cita.pagina_impresa, cita.pagina_pdf) == ("12-22", 1660)
    assert cita.texto_literal.texto.startswith("If soil cover is not provided")


def test_h5_el_aviso_de_G1_del_marco_llega_a_los_avisos_del_punto(
        corrida_guia):
    """
    Con el diseño de la guia (HW = 0.589 m) y la subrasante en 38.30: 0.30 m
    de relleno sobre la clave exterior (38.00), 4.8 mm menos que la cobertura
    adoptada, y el resguardo (0.80 m con el CBR 6.5 de C-01) cumplido por
    poco: 36.90 + 0.589 + 0.80 = 38.29 <= 38.30. Se llama a 7.B DIRECTAMENTE
    con el diseño de la guia: en una corrida, V7 -- que lleva DC = 0 y sobre
    este marco exige unos 0.83 m de relleno con sumersion completa -- habria
    rechazado antes el escalon (H6). Lo que se mide es la via del aviso.
    """
    c01 = _informe_c01(corrida_guia)
    p = dataclasses.replace(c01.punto_de_calculo, cota_rasante=38.45,
                            cota_subrasante=38.30)
    g = M7.compatibilidad_geometrica(
        punto=p, material=c01.resultado.material,
        seccion=c01.resultado.seccion,
        resultado=c01.resultado.resultado_hidraulico,
        longitud_calculada=c01.longitud_calculada,
        pendiente=c01.pendiente)
    informe = dataclasses.replace(c01, geometria=g)
    g1 = next(v for v in g.verificaciones if v.codigo == "G1")
    assert g1 in informe.con_aviso()
    assert any(a.startswith("G1") for a in informe.avisos())


def test_h5_el_caso_del_auditor_no_cae_fuera_de_ErrorProyecto(tmp_path):
    """
    Rasante 38.40 / subrasante 38.25: la tipologia de la Lamina N 03 con poco
    relleno. La corrida termina, C-01 no dimensiona, y todo lo que lo detiene
    es del expediente: el primer escalon (1.20 x 0.90, clave exterior 38.00)
    incumple V4 y V7 -- V7 lleva DC = 0, ver H6 --, y en el segundo (1.50 x
    1.20, clave 38.30) la clave queda sobre la subrasante y el
    `DatoInvalidoError` de `M5.altura_relleno_sobre_clave` detiene el
    material. G1 no llega a evaluarse: el aviso de cobertura de H5 es
    inalcanzable con esta geometria mientras V7 no pese el marco.
    """
    informe = servicio.correr(
        _csv_c01(tmp_path, rasante=38.40, subrasante=38.25),
        _externos(tmp_path), alcance=servicio.ALCANCE_PERFIL)
    c01 = _informe_c01(informe)
    assert not c01.dimensionado
    motivos = [it.motivo or "" for it in c01.traza]
    assert len(motivos) == 2, motivos
    assert "incumple V4" in motivos[0] and "V7" in motivos[0]
    assert "subrasante" in motivos[1]
    for b in c01.bloqueos:
        assert b.tipo is not None


# ===========================================================================
# H6 · la causa real de la progresion corta: V7 sin peso propio
# ===========================================================================

def test_h6_las_fichas_dicen_la_causa_real():
    sec = ca.CRITERIOS["secciones_cajon_normalizadas"]
    texto = " ".join((sec.justificacion, *sec.sensibilidad))
    assert "no cabe bajo una rasante con poco relleno" not in texto
    assert "DC = 0" in texto
    esp = ca.CRITERIOS["espesor_pared_cajon"]
    assert "extremo favorable a V7" in " ".join(
        (esp.justificacion, *esp.sensibilidad))
    diferidas = DIFERIDAS.read_text(encoding="utf-8")
    assert "`src/modulos/M5_verificaciones.py::v7_flotacion`" in diferidas


# ===========================================================================
# H7 · la cita de la formula, vacia donde la cita no la contiene
# ===========================================================================

def test_h7_los_pasos_de_T3_no_atribuyen_su_formula_a_una_cita_ajena(
        corrida_guia):
    c01 = _informe_c01(corrida_guia)
    marco = c01.geometria.geometria_marco.paso
    assert marco.formula_cita_id == ""
    assert "MC_HHD.LAMINA_03" in marco.citas_textuales
    vc2 = next(v for _, v in c01.verificaciones() if v.codigo == "VC2").paso
    assert vc2.formula_cita_id == ""
    assert vc2.umbral.cita_id == "EG2013.503.11g#COTAS"
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.90,
                           Q=0.85, seccion_canal=canal)
    assert rem.paso.formula_cita_id == ""
    assert "MC_HHD.4.1.1.3.6" in rem.paso.citas_textuales


# ===========================================================================
# H8 · los mutantes vivos
# ===========================================================================

def test_h8_el_margen_de_VC2_es_la_tolerancia_menos_el_desajuste():
    v = M7.vc2_empalme_canal(punto=_c01(), cota_salida_m=36.215)
    assert v.paso.veredicto.margen == pytest.approx(0.010 - 0.015, abs=ABS)


def test_h8_la_frontera_de_VC2_es_inclusiva_y_lleva_la_tolerancia():
    """Con el fondo en 0.0 el desajuste es la cota de salida, exacta."""
    from src.tolerancias import TOL_UMBRAL_NORMATIVO
    p = dataclasses.replace(_c01(), cota_fondo_receptor=0.0)
    borde = 0.010 + TOL_UMBRAL_NORMATIVO
    for cota in (borde, -borde):
        v = M7.vc2_empalme_canal(punto=p, cota_salida_m=cota)
        assert v.estado is EstadoDeVerificacion.CUMPLE, cota
    fuera = M7.vc2_empalme_canal(punto=p, cota_salida_m=0.010 + 10 * ABS)
    assert fuera.estado is EstadoDeVerificacion.INDICADOR


@pytest.mark.parametrize("cota, sentido", [(36.215, "SOBRE"),
                                           (36.185, "BAJO")])
def test_h8_el_aviso_de_VC2_dice_hacia_donde(cota, sentido):
    v = M7.vc2_empalme_canal(punto=_c01(), cota_salida_m=cota)
    assert sentido in v.paso.veredicto.explicacion


def test_h8_VC2_rechaza_una_tolerancia_nula():
    with con_valor("desajuste_empalme_canal_m", 0.0,
                   motivo="segunda linea: una tolerancia nula burla la puerta"):
        with pytest.raises(DatoInvalidoError):
            M7.vc2_empalme_canal(punto=_c01(), cota_salida_m=36.20)


def test_h8_la_cota_de_la_lamina_es_la_entrada_mas_HW():
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.90,
                           Q=0.85, seccion_canal=canal)
    assert rem.cota_lamina_entrada_msnm == pytest.approx(36.90 + 0.90, abs=ABS)


@pytest.mark.parametrize("Q, HW", [(float("nan"), 0.9), (float("inf"), 0.9),
                                   (-0.1, 0.9), (0.85, float("nan")),
                                   (0.85, float("inf"))])
def test_h8_el_remanso_rechaza_Q_y_HW_no_finitos(Q, HW):
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    with pytest.raises(DatoInvalidoError) as exc:
        M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=HW, Q=Q,
                         seccion_canal=canal)
    assert exc.value.campo == "Q_m3s"


@pytest.mark.parametrize("S", [0.0, -0.001, float("nan"), float("inf")])
def test_h8_el_remanso_rechaza_la_pendiente_del_canal_en_su_guardia(S):
    """
    La guardia que se mide es LA DEL REMANSO (campo
    'seccion_receptor_medida'): con S = 0 la de Manning de M3 tambien
    levanta, pero con otro campo, y el test de la FASE A no lo distinguia.
    """
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=S, n=0.025,
                            altura_total_m=2.0)
    with pytest.raises(DatoInvalidoError) as exc:
        M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.9,
                         Q=0.85, seccion_canal=canal)
    assert exc.value.campo == "seccion_receptor_medida"


@pytest.mark.parametrize("t", [0.0, -0.2, float("nan"), float("inf")])
def test_h8_la_geometria_del_marco_rechaza_un_espesor_imposible(monkeypatch,
                                                                t):
    """Segunda linea: un espesor que burlara la guardia de M2."""
    monkeypatch.setattr(M7, "espesor_pared", lambda material, D: t)
    with pytest.raises(DatoInvalidoError) as exc:
        M7.geometria_marco(punto=_c01(), material=_marco(),
                           seccion=SeccionRectangular(1.20, 0.90))
    assert exc.value.campo == "espesor_pared_cajon"


def test_h8_con_una_celda_no_hay_tabique():
    g = M7.geometria_marco(punto=_c01(), material=_marco(),
                           seccion=SeccionRectangular(1.20, 0.90))
    assert g.celdas == 1
    assert g.tabique_m == pytest.approx(0.0, abs=ABS_CERO)


# Los supervivientes de la primera medida de mutacion sobre las funciones
# tocadas (104/120 muertos con este archivo, test_t3_familia_c y
# test_M7_geometria), que no eran equivalentes; con ellos mueren 113 de 120.
# Los siete vivos son equivalentes -- la frontera exacta del tirante critico
# con su tolerancia de 1e-9, el desajuste == 0 que el brazo del aviso no
# alcanza, la semilla, la duplicacion y el signo del corchete del critico --
# y se censan en la ficha T3-12.

def test_h8_G2_lleva_el_desnivel_su_margen_y_su_resultado():
    """Familia A con desnivel 0.05 m: el umbral SUMA el desnivel."""
    p = _puntos()["A-01"]
    fondo = p.cota_fondo_receptor
    with declarados({"desnivel_minimo_entrega_m": 0.05}):
        corto = M7.g2_cota_salida(punto=p, cota_salida_m=fondo + 0.04)
        justo = M7.g2_cota_salida(punto=p, cota_salida_m=fondo + 0.06)
    assert corto.estado is EstadoDeVerificacion.NO_CUMPLE
    assert justo.estado is EstadoDeVerificacion.CUMPLE
    assert justo.paso.veredicto.margen == pytest.approx(0.06 - 0.05, abs=ABS)
    assert justo.paso.resultado.valor == pytest.approx(0.06, abs=ABS)
    # Y en la Familia C, a 36.195 sobre 36.20: margen = 36.195 - 36.19.
    c = M7.g2_cota_salida(punto=_c01(), cota_salida_m=36.195)
    assert c.paso.veredicto.margen == pytest.approx(0.005, abs=ABS)


def test_h8_G2_rechaza_un_desnivel_booleano():
    with con_valor("desnivel_minimo_entrega_m", True,
                   motivo="segunda linea: un booleano no es una altura"):
        with pytest.raises(DatoInvalidoError):
            M7.g2_cota_salida(punto=_c01(), cota_salida_m=36.20)


@pytest.mark.parametrize("L, imprime", [(0.0, False), (0.5, True),
                                        (float("inf"), False)])
def test_h9_la_S_de_cierre_solo_con_una_longitud_positiva_y_finita(L, imprime):
    v = M7.vc2_empalme_canal(punto=_c01(), cota_salida_m=36.80,
                             cota_entrada_m=36.90, longitud_m=L)
    texto = v.paso.veredicto.explicacion
    assert ("cerraria el empalme" in texto) is imprime
    if imprime:
        assert f"{(36.90 - 36.20) / L:.4f}" in texto


def test_h8_un_canal_seco_no_levanta_la_lamina():
    """Q = 0 y HW = 0: no hay remanso, y la cuenta concluye sin dividir."""
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.0,
                           Q=0.0, seccion_canal=canal)
    assert rem.evaluado and rem.concluye
    assert rem.longitud_minima_m == pytest.approx(0.0, abs=ABS_CERO)


@pytest.mark.parametrize("cota, rotulo", [(None, "no evaluada"),
                                          (36.205, "dentro de tolerancia"),
                                          (36.80, "fuera de tolerancia")])
def test_h3_el_paso_del_remanso_dice_como_estaba_VC2(cota, rotulo):
    canal = SeccionReceptor(b_m=1.0, z_HV=1.0, S=0.001, n=0.025,
                            altura_total_m=2.0)
    vc2 = (None if cota is None
           else M7.vc2_empalme_canal(punto=_c01(), cota_salida_m=cota))
    rem = M7.remanso_canal(punto=_c01(), cota_entrada_msnm=36.90, HW=0.90,
                           Q=0.85, seccion_canal=canal, vc2=vc2)
    magnitud = next(m for m in rem.paso.sustitucion if m.simbolo == "VC2")
    assert magnitud.valor == rotulo


# ===========================================================================
# H9 · el aviso de VC2 dice la pendiente que cerraria el empalme
# ===========================================================================

def test_h9_el_aviso_de_VC2_dice_la_S_que_cierra_el_empalme(corrida_guia):
    c01 = _informe_c01(corrida_guia)
    vc2 = next(v for _, v in c01.verificaciones() if v.codigo == "VC2")
    S_cierre = (36.90 - 36.20) / L_C01
    texto = vc2.paso.veredicto.explicacion
    assert f"{S_cierre:.4f}" in texto
    assert "calculad" in texto


# ===========================================================================
# H11 y H12 · textos al dia con la decision del dueño
# ===========================================================================

def test_h11_la_progresion_es_la_decision_y_no_provisional():
    sec = ca.CRITERIOS["secciones_cajon_normalizadas"]
    texto = " ".join((sec.justificacion, *sec.sensibilidad))
    assert "sin decidir" not in texto
    assert "decision del dueño" in texto
    v8 = V8.read_text(encoding="utf-8")
    assert "queda pendiente del dueño (ficha `T3-01`" not in v8
    diferidas = DIFERIDAS.read_text(encoding="utf-8")
    i = diferidas.index("## T3-01")
    assert "decisión del dueño" in diferidas[i:i + 3000]


def test_h12_el_espesor_del_marco_es_A_y_la_ficha_dice_por_que():
    assert ca.CRITERIOS["espesor_pared_cajon"].etiqueta == "A"
    diferidas = DIFERIDAS.read_text(encoding="utf-8")
    i = diferidas.index("# Parte XLVII")
    parte = diferidas[i:]
    assert "método empírico" in parte and "[A]" in parte
    assert "14.5.3" in parte
