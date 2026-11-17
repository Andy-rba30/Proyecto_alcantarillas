"""
tests/test_ve3_14_cabezal.py
============================
VE-3.14: los defectos del diseño del cabezal que encontraron los ensayos de
diseño (proceso/planes_mejora/ve3_estado/ENSAYOS_DISENO_CABEZAL.md, §6).

BLOQUE 1 (H-2, parte D). EL CORTANTE FUERA DEL SIMPLIFICADO SE VERIFICA. Hasta
VE-3.14, una seccion sin estribos fuera de las condiciones de AASHTO 5.7.3.4.1
(peralte de 16.0 in o mas, o una zapata con el vuelo de 3·d_v o mas) se
detenia con «metodo no evaluable», y el dimensionamiento del peralte saltaba
ese peralte aunque nada fallara: los ensayos midieron zapatas de 0.70 a 1.00 m
donde, con el procedimiento GENERAL de 5.7.3.4.2, bastan 0.45 a 0.50 m. Hoy
la seccion se verifica con β de la ec. 5.7.3.4.2-2.

SE ESCRIBIO EN ROJO PRIMERO contra bd350f9.
"""

from __future__ import annotations

import math

import pytest

from src import constantes_normativas as cn
from src.constantes_fisicas import PULGADA_EN_MM
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (CondicionAnalisis, ELEMENTO_ZAPATA, SECCION_PUNTA,
                         SolicitacionDeArmado)
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import REL_TRANSPORTE


def _beta_a_mano(M_u, V_u, d_v, A_s):
    """La ec. 5.7.3.4.2-2 con 5.7.3.4.2-4 y -7, escrita aparte (a_g = 0)."""
    M = max(M_u, V_u * d_v)
    eps = max((M / d_v + V_u) / (cn.ES_REFUERZO_AASHTO_MPA * A_s / 1000.0), 0.0)
    s_xe = d_v * 1000.0 / 25.4 * 1.38 / 0.63          # literal-ok: ec. 5.7.3.4.2-7 a mano
    s_xe = min(max(s_xe, 12.0), 80.0)                  # literal-ok: limites de s_xe a mano
    return 4.8 / (1 + 750 * eps) * 51 / (39 + s_xe)     # literal-ok: ec. 5.7.3.4.2-2 a mano


def test_beta_general_con_la_cuenta_a_mano():
    r = M9.beta_procedimiento_general(M_u=200.0, V_u=150.0, d_v=0.50,
                                      A_s=1500.0)
    assert r["beta"] == pytest.approx(_beta_a_mano(200.0, 150.0, 0.50, 1500.0),
                                      rel=REL_TRANSPORTE)
    assert r["s_x_in"] == pytest.approx(0.50 * MILIMETROS_POR_METRO
                                        / PULGADA_EN_MM, rel=REL_TRANSPORTE)
    # El momento no se toma menor que V_u·d_v.
    poco = M9.beta_procedimiento_general(M_u=1.0, V_u=150.0, d_v=0.50,
                                         A_s=1500.0)
    assert poco["M_u_efectivo"] == pytest.approx(75.0, rel=REL_TRANSPORTE)
    # s_xe acotado a [12, 80] in.
    chico = M9.beta_procedimiento_general(M_u=10.0, V_u=5.0, d_v=0.10,
                                          A_s=500.0)
    assert chico["s_xe_in"] == pytest.approx(cn.SXE_MIN_IN, rel=REL_TRANSPORTE)
    grande = M9.beta_procedimiento_general(M_u=10.0, V_u=5.0, d_v=1.20,
                                           A_s=500.0)
    assert grande["s_xe_in"] == pytest.approx(cn.SXE_MAX_IN, rel=REL_TRANSPORTE)


def test_una_pantalla_gruesa_se_verifica_con_el_procedimiento_general():
    """
    La pantalla de 0.45 m sin estribos (fuera de 5.7.3.4.1 por los 16.0 in)
    ya no se detiene: A2 se evalua con la β del procedimiento general.
    """
    s = M9.diseno_flexion_corte(momento=30.0, cortante=40.0, espesor=0.45,
                                id_punto="T-00")
    assert s.V_r is not None and s.V_r > 0
    a2 = next(v for v in s.verificaciones if v.codigo.startswith("A2"))
    beta = next(m for m in a2.paso.sustitucion if m.simbolo == "beta")
    esperado = _beta_a_mano(30.0, 40.0, s.d_v, s.barra.As_provisto)
    assert beta.valor == pytest.approx(esperado, rel=REL_TRANSPORTE)
    assert not math.isclose(beta.valor, cn.BETA_SIMPLIFICADO_AASHTO)
    assert "5.7.3.4.2" in a2.paso.formula


def test_una_zapata_gruesa_y_larga_se_verifica_con_el_general():
    kw = dict(momento=30.0, cortante=40.0, espesor=0.60, es_zapata=True,
              elemento=ELEMENTO_ZAPATA, clave=SECCION_PUNTA,
              seccion="punta de prueba", cara="inferior", ancho_seccion=2.0)
    corta = M9.diseno_flexion_corte(vuelo=0.80, **kw)     # simplificado
    larga = M9.diseno_flexion_corte(vuelo=2.50, **kw)     # general
    a2c = next(v for v in corta.verificaciones if v.codigo.startswith("A2"))
    a2l = next(v for v in larga.verificaciones if v.codigo.startswith("A2"))
    bc = next(m for m in a2c.paso.sustitucion if m.simbolo == "beta")
    bl = next(m for m in a2l.paso.sustitucion if m.simbolo == "beta")
    assert bc.valor == pytest.approx(cn.BETA_SIMPLIFICADO_AASHTO,
                                     rel=REL_TRANSPORTE)
    assert bl.valor < cn.BETA_SIMPLIFICADO_AASHTO
    assert larga.V_r < corta.V_r


def test_el_general_rige_por_combinacion():
    """β depende de M_u y V_u: cada combinacion se verifica con la suya."""
    sols = (SolicitacionDeArmado(
                combinacion="Resistencia I", condicion=CondicionAnalisis.ESTATICO,
                M_u=60.0, V_u=80.0, phi_flexion=0.9, phi_corte=0.9,
                M_u_cedente=60.0, V_u_cedente=80.0),
            SolicitacionDeArmado(
                combinacion="Evento Extremo I", condicion=CondicionAnalisis.SISMICO,
                M_u=90.0, V_u=95.0, phi_flexion=1.0, phi_corte=1.0,
                M_u_cedente=90.0, V_u_cedente=95.0))
    s = M9.diseno_flexion_corte(solicitaciones=sols, espesor=0.50)
    a2 = next(v for v in s.verificaciones if v.codigo.startswith("A2"))
    # Rige la combinacion de menor margen, con SU β.
    margenes = []
    for sol in sols:
        b = _beta_a_mano(sol.M_u, sol.V_u, s.d_v, s.barra.As_provisto)
        V_c = cn.VC_COEFICIENTE_AASHTO_SI * b * math.sqrt(21.0) * 1000.0 * s.d_v
        margenes.append((sol.phi_corte * V_c - sol.V_u, sol, b))
    _m, rige, b_rige = min(margenes, key=lambda x: x[0])
    assert s.rige_cortante.combinacion == rige.combinacion
    beta = next(m for m in a2.paso.sustitucion if m.simbolo == "beta")
    assert beta.valor == pytest.approx(b_rige, rel=REL_TRANSPORTE)
    assert "Resistencia I" in a2.paso.nota_del_proyecto and "Evento Extremo I" in a2.paso.nota_del_proyecto


# ===========================================================================
# BLOQUE 2 (H-6, H-5, H-12): el bucle de la zapata
# ===========================================================================
# H-6: en el tope el bucle seguia, el peralte crecia por el cortante «sin
# verificar» y la geometria final era absurda (E5-sal: 14 intentos en 5.679 m
# y 1.70 m de peralte) y tampoco cumplia. Hoy: al tope, la zapata corrida es
# NO FACTIBLE con estos criterios, se dice, y el peralte no se itera.
# H-5: solo crecia el talon; hoy, con el talon al tope, se prueba la punta.
# H-12: el ancho se dimensionaba con la zapata delgada y no bajaba cuando el
# peralte la hacia mas pesada; hoy se re-optimiza hacia abajo.

from tests.apoyo import validacion_integral as V          # noqa: E402
from tests.apoyo.criterios import con_valor                # noqa: E402
from tests.test_ve3_dimensionamiento_cabezal import ABS_MM  # noqa: E402

CRITERIO = "dimensionamiento_zapata_cabezal"


def _a01(informe):
    return next(p for p in informe.puntos if p.punto.id == "A-01")


@pytest.fixture(scope="module")
def juego():
    return V.correr_juego(V.juego_completo())


def test_al_tope_la_zapata_es_no_factible_y_el_peralte_no_se_infla():
    """
    Tope de 0.80·H_c, impuesto fuera de la ventana con `con_valor` (como en
    tests/test_ve3_dimensionamiento_cabezal.py) para llegar al tope: la
    entrada de A-01 no cumple con ningun ancho de la grilla. Se prueba la
    punta (sus intentos llevan la punta), se declara NO FACTIBLE y su peralte
    no se itera.
    """
    with con_valor(CRITERIO, {"paso_m": 0.10, "fraccion_ancho_max": 0.80},
                   motivo="tope bajo la ventana a proposito: llegar al tope"):
        informe = V.correr_juego(V.juego_completo())
    cab = _a01(informe).cabezal
    assert any("NO FACTIBLE" in a and "entrada" in a for a in cab.avisos)
    de_la_punta = [i for i in cab.intentos_de_zapata
                   if i.extremo == "entrada" and i.punta is not None]
    assert de_la_punta, "con el talon al tope no se probo la punta"
    puntas = [i.punta for i in de_la_punta]
    assert puntas == sorted(puntas) and len(set(puntas)) == len(puntas)
    assert not [i for i in cab.intentos_de_peralte if i.extremo == "entrada"]
    # La geometria que queda es la del talon al tope, no la ultima de la punta.
    assert cab.entrada.B == pytest.approx(1.775, abs=ABS_MM)


RAIZ = __import__("pathlib").Path(__file__).resolve().parents[1]
E5 = RAIZ / "tests" / "fixtures" / "ensayos_cabezal" / "E5_arcilla_blanda"


def correr_e5(tmp_path):
    """El escenario E5 de los ensayos (DATOS DE PRUEBA), por la CLI."""
    import json
    import subprocess
    import sys
    salida = tmp_path / "e5.json"
    args = [sys.executable, str(RAIZ / "cli.py"), str(E5 / "puntos.csv"),
            "--alcance", "expediente",
            "--datos-externos", str(E5 / "externos.json"),
            "--datos-sitio", str(E5 / "sitio.json"), "--json", str(salida)]
    for clave, valor in json.loads(
            (E5 / "declaraciones.json").read_text(encoding="utf-8")).items():
        args += ["--declarar", f"{clave}={valor!r}"]
    subprocess.run(args, cwd=RAIZ, capture_output=True, text=True,
                   check=False)
    return json.loads(salida.read_text(encoding="utf-8"))


def test_en_arcilla_la_zapata_no_factible_no_infla_el_peralte(tmp_path):
    """
    E5 de los ensayos (suelo cohesivo): con los criterios de archivo ninguna
    zapata corrida de la grilla cumple la estabilidad de la salida. Hasta
    VE-3.14 el bucle seguia en el tope, el peralte crecia a 1.704 m y la
    app entregaba 5.68 × 1.70 m sin cumplir; hoy lo declara NO FACTIBLE y el
    peralte se queda en el de la regla.
    """
    d = correr_e5(tmp_path)
    punto = d["puntos"][0]
    salida = next(c for c in punto["cabezal"]["cabezales"]
                  if c["extremo"] == "salida")
    assert salida["espesor_zapata_m"] == pytest.approx(0.40414, abs=ABS_MM)
    assert any("NO FACTIBLE" in a and "salida" in a
               for a in punto.get("avisos", []))


def test_el_ancho_se_reoptimiza_tras_el_peralte(juego):
    """
    La salida de A-01 del juego: el peralte crece a 0.804 m y con la zapata
    mas pesada se prueba un ancho menor; aqui no alcanza (E1 sismico), de
    modo que el ancho adoptado es el minimo que cumple con ese peralte.
    """
    cab = _a01(juego).cabezal
    reopt = [i for i in cab.intentos_de_zapata
             if i.extremo == "salida" and i.reoptimizado]
    assert reopt, "no se intento re-optimizar el ancho tras el peralte"
    assert reopt[-1].B == pytest.approx(cab.salida.B - 0.10, abs=ABS_MM)
    assert not reopt[-1].cumple
