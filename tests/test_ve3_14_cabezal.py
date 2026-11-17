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
    La salida de A-01 del juego: el peralte crece (0.604 m desde el bloque 3,
    que arma la zapata con el acero que el cortante general pide; 0.804 m en
    el bloque 2) y con la zapata mas pesada se prueba un ancho menor; aqui no
    alcanza (E1 sismico), de modo que el ancho adoptado es el minimo que
    cumple con ese peralte. El ancho FINAL lleva ademas lo que la pantalla
    crecio (bloque 3): se compara con el ancho que la estabilidad acepto.
    """
    cab = _a01(juego).cabezal
    reopt = [i for i in cab.intentos_de_zapata
             if i.extremo == "salida" and i.reoptimizado]
    assert reopt, "no se intento re-optimizar el ancho tras el peralte"
    aceptado = [i for i in cab.intentos_de_zapata if i.extremo == "salida"
                and i.cumple and not i.reoptimizado][-1]
    assert reopt[-1].B == pytest.approx(aceptado.B - 0.10, abs=ABS_MM)
    assert not reopt[-1].cumple


# ===========================================================================
# BLOQUE 3 (H-1): la pantalla y el alero, DIMENSIONADOS por su armado
# ===========================================================================
# Hasta VE-3.14 la pantalla quedaba en los 0.30 m de la regla para cualquier
# altura y la app entregaba cabezales cuyo armado de la pantalla y del alero
# no cumplia (8 de 20 en los ensayos). Hoy el espesor crece con el paso de
# 'dimensionamiento_zapata_cabezal' hasta que el armado cumple; la zapata
# crece lo mismo (punta y talon fijos) y la estabilidad y la zapata se
# re-verifican. Y fuera de 5.7.3.4.1 el cortante general pide ACERO antes que
# espesor: con β de la ec. 5.7.3.4.2-2, mas acero longitudinal es menor εs.

from src.constantes_fisicas import KPA_POR_MPA                  # noqa: E402
from src.modelos import ORIGEN_DIMENSION_ARMADO                 # noqa: E402

E2 = RAIZ / "tests" / "fixtures" / "ensayos_cabezal" / "E2_alto"


def test_el_acero_del_cortante_general_cierra_la_ecuacion():
    """La ec. 5.7.3.4.2-2 despejada: con ese acero, phi·V_c = V_u exacto."""
    c = M9.cortante_del_concreto(d=0.66, a=0.02, espesor=0.75, fc=21.0,
                                 beta=1.0)
    tope = cn.VN_TOPE_SOBRE_FC_AASHTO * 21.0 * KPA_POR_MPA * c["d_v"]
    As = M9.acero_para_cortante_general(M_u=250.0, V_u=260.0, d_v=c["d_v"],
                                        phi=0.9, V_c_por_beta=c["V_c"],
                                        V_tope=tope)
    g = M9.beta_procedimiento_general(M_u=250.0, V_u=260.0, d_v=c["d_v"],
                                      A_s=As)
    phi_V_c = 0.9 * g["beta"] * c["V_c"]
    assert phi_V_c == pytest.approx(260.0, rel=REL_TRANSPORTE)
    # Ningun acero alcanza: lo que falta es espesor.
    assert M9.acero_para_cortante_general(
        M_u=250.0, V_u=5000.0, d_v=c["d_v"], phi=0.9,
        V_c_por_beta=c["V_c"], V_tope=tope) is None


def test_fuera_del_simplificado_el_cortante_pide_acero_antes_que_espesor():
    """
    Pantalla de 0.60 m (general por los 16.0 in) con poco momento y mucho
    cortante: con el acero de flexion A2 no cumple; el acero adoptado sube
    hasta el que el cortante general pide, y lo dice `gobierna`.
    """
    s = M9.diseno_flexion_corte(momento=60.0, cortante=220.0, espesor=0.60,
                                id_punto="T-00")
    a2 = next(v for v in s.verificaciones if v.codigo.startswith("A2"))
    assert a2.cumple
    assert "5.7.3.4.2" in s.gobierna
    assert s.As_adoptado > max(s.As_resistencia, s.As_minimo_flexion,
                               s.As_minimo_constructivo)


def test_la_pantalla_y_el_alero_se_dimensionan_por_su_armado(juego):
    """
    La salida de A-01 del juego: con la pantalla de 0.30 m de la regla, A1 de
    la pantalla y del alero no cumplian; la pantalla crece a 0.40 m (un
    paso), corona y arranque, el alero la hereda y los tres llevan el origen
    «dimensionada por armado». Ninguna fila del cabezal queda sin cumplir.
    """
    cab = _a01(juego).cabezal
    g = cab.salida
    assert g.espesor_corona == pytest.approx(0.40, abs=ABS_MM)
    assert g.espesor_base_muro == pytest.approx(0.40, abs=ABS_MM)
    assert g.aleros.espesor == pytest.approx(0.40, abs=ABS_MM)
    origen = {d.nombre: d.origen for d in g.dimensiones}
    for nombre in ("espesor de la pantalla en la corona",
                   "espesor de la pantalla en el arranque",
                   "espesor de los aleros"):
        assert origen[nombre] == ORIGEN_DIMENSION_ARMADO, nombre
    traza = [i for i in cab.intentos_de_pantalla if i.startswith("salida")]
    assert traza and "0.300 m: no cumplen A1.pantalla.s" in traza[0]
    assert traza[0].endswith("0.400 m: cumple")
    assert not cab.verificaciones_incumplidas
    paso = next(p for p in cab.pasos if p.codigo == "9.3.m.s")
    assert paso.resultado.valor == pytest.approx(0.40, abs=ABS_MM)
    # La entrada cumplia con la regla: no se toca.
    assert cab.entrada.espesor_base_muro == pytest.approx(0.30, abs=ABS_MM)
    assert not [i for i in cab.intentos_de_pantalla if i.startswith("entrada")]


def test_la_pantalla_crece_con_la_zapata_y_la_punta_y_el_talon_no_cambian(
        juego):
    """La zapata crece lo mismo que la pantalla: B = B_estabilidad + Δe."""
    cab = _a01(juego).cabezal
    g = cab.salida
    aceptado = [i for i in cab.intentos_de_zapata if i.extremo == "salida"
                and i.cumple and not i.reoptimizado][-1]
    assert g.B == pytest.approx(aceptado.B + (0.40 - 0.30), abs=ABS_MM)
    assert g.ancho_talon == pytest.approx(
        aceptado.B - g.ancho_punta - 0.30, abs=ABS_MM)


def correr_escenario(carpeta, tmp_path):
    """Un escenario de los ensayos (DATOS DE PRUEBA), por la CLI."""
    import json
    import subprocess
    import sys
    salida = tmp_path / f"{carpeta.name}.json"
    args = [sys.executable, str(RAIZ / "cli.py"), str(carpeta / "puntos.csv"),
            "--alcance", "expediente",
            "--datos-externos", str(carpeta / "externos.json"),
            "--datos-sitio", str(carpeta / "sitio.json"), "--json",
            str(salida)]
    for clave, valor in json.loads(
            (carpeta / "declaraciones.json").read_text(encoding="utf-8")
            ).items():
        args += ["--declarar", f"{clave}={valor!r}"]
    subprocess.run(args, cwd=RAIZ, capture_output=True, text=True,
                   check=False)
    return json.loads(salida.read_text(encoding="utf-8"))


def test_e2_alto_entrega_un_cabezal_completo_que_cumple(tmp_path):
    """
    E2 de los ensayos (H_c de la salida 4.51 m): hasta VE-3.14 la app
    entregaba la pantalla de 0.30 m con A1 a A6 de la pantalla y del alero
    sin cumplir. Hoy: pantalla y alero dimensionados, ninguna fila de la Fase
    9 sin cumplir, y la traza de los tres dimensionamientos en el JSON.
    """
    d = correr_escenario(E2, tmp_path)
    punto = d["puntos"][0]
    cab = punto["cabezal"]
    salida = next(c for c in cab["cabezales"] if c["extremo"] == "salida")
    # 0.70 m: con el acero que el cortante general pide (sin el, 1.20 m:
    # el espesor crecia para bajar un εs que el acero de flexion dejaba alto).
    assert salida["espesor_base_muro_m"] == pytest.approx(0.70, abs=ABS_MM)
    assert salida["aleros"]["espesor_m"] == pytest.approx(
        salida["espesor_base_muro_m"], abs=ABS_MM)
    fallan = [v["codigo"] for v in punto["verificaciones"]
              if "Fase 9" in (v.get("fase") or "") and not v["cumple"]]
    assert not fallan, fallan
    assert any(t.startswith("salida") and t.endswith("cumple")
               for t in cab["intentos_de_pantalla"])
    assert cab["intentos_de_zapata"] and cab["intentos_de_peralte"]


def test_si_el_armado_de_la_pantalla_nunca_cumple_el_bucle_termina_y_lo_dice(
        monkeypatch):
    """
    Terminacion, medida: con `incumplidas_del_armado_de_la_pantalla`
    sustituida por una que nunca cumple, el espesor crece hasta su tope
    fisico (la altura de la pantalla) o hasta que la estabilidad o la zapata
    dejan de cumplir, y se DETIENE con un aviso; nunca queda una pantalla tan
    gruesa como alta.
    """
    original = M9.incumplidas_del_armado_de_la_pantalla
    monkeypatch.setattr(M9, "incumplidas_del_armado_de_la_pantalla",
                        lambda entorno: (tuple(original(entorno) or ())
                                         + ("A1.pantalla.prueba",)))
    cab = _a01(V.correr_juego(V.juego_completo())).cabezal
    for g in cab.geometrias:
        assert g.espesor_base_muro < g.H
        assert any(f"Cabezal de {g.extremo}" in a and "se detuvo" in a
                   for a in cab.avisos), g.extremo



# ===========================================================================
# BLOQUE 4 (H-3): con agua en el plano de empuje, el sismo NO se salta
# ===========================================================================
# Hasta VE-3.14 la condicion sismica se detenia con «metodo no evaluable»
# en cuanto habia agua en el plano de empuje, el ancho se dimensionaba sin
# ella y se rotulaba «dimensionada por estabilidad»; el mensaje recomendaba
# declarar el drenaje aunque ya estuviera declarado. Hoy: C11.6.5.3, peso
# TOTAL bajo el agua para el relleno que no drena libremente
# ('agua_del_relleno_bajo_sismo' [C]); el relleno muy abierto sigue
# deteniendose (Westergaard no esta en ninguna fuente del repositorio).

from src.modelos import (ORIGEN_DIMENSION_ESTABILIDAD,          # noqa: E402
                         ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA)

E3 = RAIZ / "tests" / "fixtures" / "ensayos_cabezal" / "E3_muy_alto"


def _origen_del_ancho(cabezal_json, extremo):
    g = next(c for c in cabezal_json["cabezales"] if c["extremo"] == extremo)
    return next(d["origen"] for d in g["dimensiones"]
                if d["nombre"] == "ancho de la zapata (B)")


def test_e3_con_agua_la_condicion_sismica_se_evalua_y_dimensiona(tmp_path):
    d = correr_escenario(E3, tmp_path)
    punto = d["puntos"][0]
    assert not [b for b in punto["bloqueos"]
                if "agua en el plano de empuje" in (b.get("mensaje") or "")]
    codigos = {v["codigo"]: v["cumple"] for v in punto["verificaciones"]
               if v.get("codigo")}
    assert codigos.get("E1-LRFD.sis.s") is True
    assert _origen_del_ancho(punto["cabezal"], "salida") == \
        ORIGEN_DIMENSION_ESTABILIDAD
    sismica = next(e for e in punto["cabezal"]["estabilidad"]
                   if e["extremo"] == "salida" and e["condicion"] == "sismico")
    assert sismica["K_AE"] is not None
    # La cifra, medida (DATOS DE PRUEBA): con el sismo el ancho de la salida
    # crece a 5.970 m (sin el, la app daba 4.670 m; el revisor de los
    # ensayos, 5.05 a 5.37 m con sus criterios). Un incremento sismico con
    # el peso sumergido en vez del total da otro ancho.
    salida = next(c for c in punto["cabezal"]["cabezales"]
                  if c["extremo"] == "salida")
    assert salida["B_m"] == pytest.approx(5.970032344780179, abs=ABS_MM)


def test_e3_con_relleno_muy_abierto_se_detiene_y_no_rotula_estabilidad(
        tmp_path):
    """
    Con el relleno declarado muy abierto la condicion sismica se detiene
    (Westergaard no esta en el repositorio); el mensaje ya no recomienda el
    drenaje que esta declarado, y el ancho se rotula como dimensionado con la
    estabilidad EVALUABLE, no «por estabilidad».
    """
    d = correr_escenario(E3, tmp_path, "--declarar",
                         "agua_del_relleno_bajo_sismo='relleno_muy_abierto'")
    punto = d["puntos"][0]
    bloqueo = next(b for b in punto["bloqueos"]
                   if "agua en el plano de empuje" in (b.get("mensaje") or ""))
    assert "El drenaje ya esta declarado" in bloqueo["mensaje"]
    assert "Declarar el drenaje" not in bloqueo["mensaje"]
    assert _origen_del_ancho(punto["cabezal"], "salida") == \
        ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA



def test_el_incremento_sismico_con_agua_va_con_el_peso_total(juego):
    """
    La cuenta, aparte: con el relleno lleno de agua (sin drenaje y el
    freatico alto), el incremento sismico es (K_AE·(1 - k_v) - K_A)·Γ_t, con
    Γ_t la integral del peso TOTAL sobre el plano de empuje (C11.6.5.3); el
    estatico sigue con el sumergido.
    """
    from dataclasses import replace
    p = _a01(juego)
    entornos = M9.datos_del_cabezal_del_punto(
        punto=p.punto_de_calculo, cabezal=p.cabezal, geometria=p.geometria,
        socavacion=p.socavacion, suelo_del_punto=None, resultado=p.resultado)
    entorno = next(e for e in entornos if e.extremo == "salida")
    alto = replace(entorno, cota_freatico=entorno.cota_pie + 10.0)
    import tempfile
    from pathlib import Path
    from src import criterios_adoptados as ca
    from src import datos_sitio as ds
    from src import servicio
    with tempfile.TemporaryDirectory() as tmp:
        e = V.materializar(V.juego_completo(), Path(tmp))
        try:
            servicio.cargar_datos_sitio(e.sitio)
            for clave, valor in e.declaraciones.items():
                ca.establecer_valor_dinamico(clave, valor)
            ca.establecer_valor_dinamico(
                "peso_especifico_saturado_relleno_kn_m3", 20.0)
            _c, d = M9.cargas_del_cabezal(alto, CondicionAnalisis.SISMICO)
        finally:
            for clave in ca.valores_dinamicos():
                ca.quitar_valor_dinamico(clave)
            ds.limpiar_datos_dinamicos()
    assert d["h_w"] > 0
    h_seco = d["h"] - d["h_w"]
    gamma_t = (d["gamma"] * h_seco ** 2 / 2 + d["gamma"] * h_seco * d["h_w"]
               + 20.0 * d["h_w"] ** 2 / 2)
    esperado = (d["K_AE"] * (1.0 - d["k_v"]) - d["K_A"]) * gamma_t
    assert d["P_AE"] - d["P_A"] == pytest.approx(esperado, rel=REL_TRANSPORTE)



# ===========================================================================
# BLOQUE 5 (H-10, H-11): lo que la app dice de si misma
# ===========================================================================

def test_el_alcance_declarado_ya_no_dice_que_el_ancho_no_se_itera():
    from src.modelos import ALCANCE_DECLARADO
    a = next(x for x in ALCANCE_DECLARADO
             if x.clave == "iteracion_ancho_zapata_cabezal")
    assert "no se itera:" not in a.texto
    assert "NO FACTIBLE" in a.texto and "VE-3.14" in a.texto


def test_el_resumen_atribuye_el_metodo_no_evaluable_a_su_causa(tmp_path):
    """
    E3 con el relleno muy abierto: la etapa sismica se detiene por «metodo
    no evaluable» y no hay ningun criterio sin valor. El RESUMEN decia
    «Mientras un criterio siga sin valor...»; hoy dice la causa.
    """
    import cli
    import json
    import subprocess
    import sys
    args = [sys.executable, str(RAIZ / "cli.py"), str(E3 / "puntos.csv"),
            "--alcance", "expediente",
            "--datos-externos", str(E3 / "externos.json"),
            "--datos-sitio", str(E3 / "sitio.json")]
    for clave, valor in json.loads(
            (E3 / "declaraciones.json").read_text(encoding="utf-8")).items():
        args += ["--declarar", f"{clave}={valor!r}"]
    args += ["--declarar",
             "agua_del_relleno_bajo_sismo='relleno_muy_abierto'",
             "--json", str(tmp_path / "e3.json")]
    r = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True,
                       check=False)
    resumen = r.stdout[r.stdout.rindex("RESUMEN"):]
    assert "metodo no evaluable" in resumen
    assert "Mientras un criterio siga sin valor" not in resumen
    assert cli.TipoDeBloqueo is not None



# ===========================================================================
# OPCIONES 9, 10 y 13: las alternativas de tres elecciones [A]
# ===========================================================================
# El valor de archivo es el comportamiento de hoy (los tests de arriba lo
# fijan); la alternativa la sostiene la fuente, con las condiciones de la
# verificacion del dueño (verificaciones_del_dueno/cabezal_decisiones_9_14.md).
# Las cifras de los escenarios de los ensayos van en el informe de VE-3.14.

def _seccion(cabezal, extremo, clave):
    a = next(x for x in cabezal.armado if x.extremo == extremo)
    return next(s for s in a.secciones if s.clave == clave)


def test_opcion_9_el_talon_exacto_descuenta_la_reaccion(juego):
    """
    'momento_talon_cabezal' = 'exacto': el talon con la reaccion lineal de
    10.6.5 de CADA combinacion; el peso entero queda como contraste en la
    nota, y el momento que rige no supera al del peso entero.
    """
    archivo = _seccion(_a01(juego).cabezal, "entrada", "talon")
    with con_valor("momento_talon_cabezal", "exacto",
                   motivo="la alternativa de la opcion 9"):
        exacto = _seccion(_a01(V.correr_juego(V.juego_completo())).cabezal,
                          "entrada", "talon")
    assert "metodo mas exacto" in exacto.rige_flexion.nota
    assert "peso entero (contraste)" in exacto.rige_flexion.nota
    assert exacto.rige_flexion.M_u < archivo.rige_flexion.M_u
    assert all(s.condicion in (CondicionAnalisis.ESTATICO,
                               CondicionAnalisis.SISMICO)
               for s in exacto.solicitaciones)


def test_opcion_10_la_cuna_sobre_la_pantalla_carga_menos(juego):
    """
    'carga_pantalla_cabezal' = 'cuna_sobre_la_pantalla': la pantalla con la
    cuña sobre su propia cara (Caltrans BDP 11.2), hasta la superficie real;
    el plano virtual del talon es la cota superior y carga mas.
    """
    archivo = _seccion(_a01(juego).cabezal, "entrada", "pantalla")
    with con_valor("carga_pantalla_cabezal", "cuna_sobre_la_pantalla",
                   motivo="la alternativa de la opcion 10"):
        cuna = _seccion(_a01(V.correr_juego(V.juego_completo())).cabezal,
                        "entrada", "pantalla")
    assert 0 < cuna.rige_flexion.M_u < archivo.rige_flexion.M_u


def test_opcion_13_solo_con_el_muro_que_cede():
    """
    'distribucion_incremento_sismico' = 'distribucion_estatica' con el muro
    que NO cede ('factor_muro_eleccion' = 'sin_reduccion', el de archivo) se
    rechaza con la causa; con la reduccion declarada (la del juego), el
    incremento va al mayor del centroide estatico y h/3, por debajo del
    0.6·h de archivo.
    """
    from dataclasses import replace
    j = V.juego_completo()
    con13 = replace(j, declaraciones={
        **j.declaraciones,
        "distribucion_incremento_sismico": "distribucion_estatica"})
    assert con13.declaraciones["factor_muro_eleccion"] == \
        "reduccion_por_desplazamiento"
    cede = _a01(V.correr_juego(con13))
    no_cede = _a01(V.correr_juego(replace(con13, declaraciones={
        **con13.declaraciones, "factor_muro_eleccion": "sin_reduccion"})))
    assert any("distribucion_incremento_sismico" in (b.mensaje or "")
               for b in no_cede.bloqueos)
    sis = next(e for e in cede.cabezal.estabilidad
               if e.extremo == "entrada"
               and e.condicion is CondicionAnalisis.SISMICO)
    dP = next(c for c in sis.cargas if c.codigo == "EQ.dPAE.h")
    eh = next(c for c in sis.cargas if c.codigo == "EH.h")
    ls = next(c for c in sis.cargas if c.codigo == "LS.h")
    # El centroide del diagrama estatico (suelo y sobrecarga): con la
    # sobrecarga queda sobre h/3, y es el que rige.
    z_estatico = (eh.H * eh.z + ls.H * ls.z) / (eh.H + ls.H)
    assert z_estatico > sis.altura_empuje / 3
    assert dP.z == pytest.approx(max(z_estatico, sis.altura_empuje / 3),
                                 rel=REL_TRANSPORTE)
    assert dP.z < 0.6 * sis.altura_empuje
