"""
tests/test_ext7_cabezal.py
==========================
Aceptacion del cluster «cabezal» de la auditoria externa del 2026-09-19
(EXT-M-05, EXT-M-06, EXT-M-07; R95-031 por la misma correccion que M-05),
ejecutada por EXT-7 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md.

Escritos PRIMERO, en rojo, con `xfail(strict=True)` y la expectativa de la
fuente o del invariante como oraculo --- nunca la salida actual ---, y
liberados al corregir. Tres bloques, uno por hallazgo:

  M-05  la rama vertical de `cuantia_de_diseno` con cortante alto devolvia
        0.0015 (Art. 14.3.1) y su docstring afirmaba «cortante_alto=True no
        cambia el minimo»: el Art. 11.10.10.3 (ec. 11-32, pag. 104) fija
        piso 0.0025 tambien en vertical. Y hay una pregunta PREVIA que decide
        si los dos articulos rigen: el 11.10.2 gobierna el cortante EN EL
        PLANO del muro y el 11.10.1 manda el perpendicular a las losas del
        11.12. Ninguna de las dos se implementa como formula: las dos se
        DETIENEN en un criterio [A] de expediente.
  M-06  el empuje estatico y la sobrecarga iban con el Ka de Rankine mientras
        el incremento sismico iba con Mononobe-Okabe (Coulomb con
        aceleracion): base mixta, declarada y no autorizada por ninguna
        fuente. La fuente primaria del marco (MP 2.4.4.1.5.3) es Coulomb.
  M-07  `EstabilidadCabezal.estable` era True con E1-E3 solas y con el
        conjunto vacio, mientras el docstring prometia cinco.

Lo que NO se prueba aqui, a proposito: la ec. (11-32) no se implementa
(faltan lm y Vu), y nada se cablea a la CLI (`M9.FUNCIONES_SIN_CONSUMIDOR`
sigue vigilando).
"""
from __future__ import annotations

import ast
import math
from dataclasses import replace
from pathlib import Path

import pytest

import constantes_normativas as CN
import criterios_adoptados as ca
import datos_sitio as ds
from modelos import (CondicionAnalisis, CriterioPendienteError,
                     DatoInvalidoError, EstabilidadCabezal,
                     GeometriaCabezal, Verificacion)
from modulos import M9_cabezal as M9
from normativa import registro as _registro
from normativa.esquema import Caracter, EstadoDiscrepancia
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, sin_valor
from tests.fixtures.casos_patron import (CP9_EMPUJE_TRASDOS,
                                         CP9_RANKINE_LIMITE,
                                         CP9_TOLERANCIA_RELATIVA)
from tolerancias import TOL_UMBRAL_NORMATIVO

RAIZ = Path(__file__).resolve().parents[1]
CP9 = CP9_EMPUJE_TRASDOS

# Nacio con `pytestmark = pytest.mark.xfail(strict=True)` a nivel de modulo:
# medido en rojo ANTES de tocar codigo, 44 xfailed y 6 XPASS (los cinco del
# caso limite de Rankine, que ya se cumplia, y la guardia de que nada se
# cablea a la CLI, que ya se cumplia). Liberado al corregir.
REL_CP9 = CP9["tolerancia_relativa"]

CLAVE_CORTANTE_ALTO = "cortante_alto_muro_e060_art_11_10_10_2"
CLAVE_REGIMEN = "regimen_cortante_muro_e060_art_11_10_2"
CLAVE_VERTICAL = "cuantia_vertical_cortante_alto_e060_art_11_10_10_3"

# Valores DE PRUEBA para los dos vacios, no de proyecto: el 0.0025 es el piso
# que el Art. 11.10.10.2 escribe y el vertical es un valor cualquiera por
# encima de ese piso. No cierran ningun vacio: viven en el test.
CUANTIA_H_DE_PRUEBA = 0.0025
CUANTIA_V_DE_PRUEBA = 0.0030
MOTIVO_PRUEBA = "valor de prueba de la aceptacion EXT-7, no de proyecto"


@pytest.fixture
def reg():
    return _registro.construir()


@pytest.fixture
def geometria():
    """Cabezal de tanteo (el mismo de tests/test_M9_cabezal.py)."""
    return GeometriaCabezal(H=2.00, B=1.60, D_f=1.00, espesor_corona=0.25,
                            espesor_base_muro=0.35, espesor_zapata=0.40)


# ===========================================================================
# M-05 · La rama vertical con cortante alto SE DETIENE, y antes pregunta en
#        que plano actua el cortante
# ===========================================================================

def test_M05_existen_los_dos_criterios_nuevos_vacios_A_y_de_expediente():
    for clave in (CLAVE_REGIMEN, CLAVE_VERTICAL):
        c = ca.criterio(clave)
        assert c.valor is None, f"{clave} no puede nacer con valor"
        assert c.etiqueta == "A"
        assert c.nivel == ca.NIVEL_EXPEDIENTE
        assert c.resolucion is not None
    # El vertical dice de que depende la ec. (11-32): hm, lm y la rho_h que
    # el 11.10.10.1 requiere. Es lo que `GeometriaCabezal` no tiene.
    texto = ca.criterio(CLAVE_VERTICAL).resolucion.que_lo_fija.lower()
    for termino in ("hm", "lm", "11.10.10.1"):
        assert termino in texto, f"la resolucion no nombra {termino}"
    # El regimen es una categoria cerrada, con las dos lecturas de la norma.
    assert ca.criterio(CLAVE_REGIMEN).forma == ca.FORMA_CATEGORIA
    assert set(ca.criterio(CLAVE_REGIMEN).sensibilidad) == set(
        CN.REGIMENES_CORTANTE_MURO)


@pytest.mark.parametrize("direccion", ["vertical", "horizontal"])
def test_M05_con_cortante_alto_lo_primero_que_se_pregunta_es_el_plano(direccion):
    """
    §11.10.2 restringe 11.10.3-11.10.10 al cortante EN EL PLANO. Con el
    regimen sin declarar, ninguna de las dos direcciones puede seguir: ni al
    0.0025 ni al 0.0020/0.0015 por defecto.
    """
    with sin_valor(CLAVE_REGIMEN):
        with pytest.raises(CriterioPendienteError) as excinfo:
            M9.cuantia_de_diseno(cuantia_calculada=0.0031, direccion=direccion,
                                 cortante_alto=True)
    assert excinfo.value.clave == CLAVE_REGIMEN


def test_M05_en_vertical_con_cortante_en_el_plano_se_detiene_en_el_11_10_10_3():
    """
    EL HALLAZGO. Antes devolvia 0.0015 sin aviso; ahora lee el criterio del
    Art. 11.10.10.3 y se detiene mientras siga vacio. No hay rama al 14.3.1.
    """
    with con_valor(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_EN_EL_PLANO,
                   motivo=MOTIVO_PRUEBA), sin_valor(CLAVE_VERTICAL):
        with pytest.raises(CriterioPendienteError) as excinfo:
            M9.cuantia_de_diseno(cuantia_calculada=0.0031, direccion="vertical",
                                 cortante_alto=True)
    assert excinfo.value.clave == CLAVE_VERTICAL
    assert ca.criterio(CLAVE_VERTICAL).valor is None


def test_M05_en_horizontal_con_cortante_en_el_plano_sigue_leyendo_el_11_10_10_2():
    with con_valor(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_EN_EL_PLANO,
                   motivo=MOTIVO_PRUEBA), sin_valor(CLAVE_CORTANTE_ALTO):
        with pytest.raises(CriterioPendienteError) as excinfo:
            M9.cuantia_de_diseno(cuantia_calculada=0.0031,
                                 direccion="horizontal", cortante_alto=True)
    assert excinfo.value.clave == CLAVE_CORTANTE_ALTO


@pytest.mark.parametrize("direccion, clave, valor", [
    ("vertical", CLAVE_VERTICAL, CUANTIA_V_DE_PRUEBA),
    ("horizontal", CLAVE_CORTANTE_ALTO, CUANTIA_H_DE_PRUEBA),
])
def test_M05_declarado_el_piso_del_regimen_11_10_10_es_el_que_rige(
        direccion, clave, valor):
    """
    Con el regimen en el plano y el piso declarado, `cuantia_de_diseno` lo
    aplica como minimo y el resultado dice de que criterio salio.
    """
    with con_valor(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_EN_EL_PLANO,
                   motivo=MOTIVO_PRUEBA), con_valor(clave, valor,
                                                    motivo=MOTIVO_PRUEBA):
        r = M9.cuantia_de_diseno(cuantia_calculada=0.0010,
                                 direccion=direccion, cortante_alto=True)
    assert r.cuantia_minima == pytest.approx(valor, rel=REL_CP9)
    assert r.cuantia_adoptada == pytest.approx(valor, rel=REL_CP9)
    assert r.gobierna == "minimo_normativo"
    assert r.criterio_cortante_alto == clave
    assert r.criterio_regimen_cortante == CLAVE_REGIMEN
    assert r.regimen_cortante == CN.REGIMEN_CORTANTE_EN_EL_PLANO
    assert "11.10.10" in r.numeral


@pytest.mark.parametrize("direccion", ["vertical", "horizontal"])
def test_M05_si_el_cortante_es_perpendicular_ni_el_11_10_10_2_ni_el_3_rigen(
        direccion):
    """
    §11.10.1: el cortante perpendicular al plano se diseña por 11.12. Un
    cabezal en voladizo bajo empuje de tierras trabaja asi. Entonces
    `cortante_alto=True` NO escalona nada: rige el 14.3.1, y el resultado
    lo dice con el numeral del 11.10.1 y sin leer el piso del 11.10.10.
    """
    with con_valor(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_PERPENDICULAR,
                   motivo=MOTIVO_PRUEBA), \
            sin_valor(CLAVE_VERTICAL), sin_valor(CLAVE_CORTANTE_ALTO):
        r = M9.cuantia_de_diseno(cuantia_calculada=0.0010,
                                 direccion=direccion, cortante_alto=True)
    assert r.cuantia_minima == pytest.approx(CN.CUANTIA_MIN_MURO[direccion],
                                             rel=REL_CP9)
    assert r.regimen_cortante == CN.REGIMEN_CORTANTE_PERPENDICULAR
    assert "11.10.1" in r.numeral and "11.12" in r.numeral
    assert "14.3.1" in r.numeral
    # El numero es [N] y quien lo DECIDIO es un [A]: se atribuye al regimen y
    # no se rellena con la clave de un piso que no se leyo (auditoria).
    assert r.criterio_regimen_cortante == CLAVE_REGIMEN
    assert r.criterio_cortante_alto == ""
    # y verificar_cuantia contesta lo mismo, con el [A] en `criterio_aplicado`
    with con_valor(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_PERPENDICULAR,
                   motivo=MOTIVO_PRUEBA):
        v = M9.verificar_cuantia(cuantia_provista=0.0010, direccion=direccion,
                                 cortante_alto=True)
    assert v.criterio_aplicado == CLAVE_REGIMEN
    assert v.valor_admisible == pytest.approx(CN.CUANTIA_MIN_MURO[direccion],
                                              rel=REL_TRANSPORTE)


@pytest.mark.parametrize("direccion", ["vertical", "horizontal"])
def test_M05_sin_cortante_alto_no_se_lee_ningun_criterio(direccion):
    """Con cortante_alto=False la ficha del regimen ni se abre."""
    ca.reiniciar_usos()
    r = M9.cuantia_de_diseno(cuantia_calculada=0.0031, direccion=direccion,
                             cortante_alto=False)
    assert r.cuantia_minima == pytest.approx(CN.CUANTIA_MIN_MURO[direccion],
                                             rel=REL_TRANSPORTE)
    assert r.regimen_cortante is None
    assert r.criterio_cortante_alto == "" and r.criterio_regimen_cortante == ""
    assert CLAVE_REGIMEN not in ca.criterios_usados()


# --- verificar_cuantia con el MISMO argumento ------------------------------

def test_M05_verificar_cuantia_exige_cortante_alto_sin_valor_por_defecto():
    with pytest.raises(TypeError):
        M9.verificar_cuantia(cuantia_provista=0.0025, direccion="vertical")


@pytest.mark.parametrize("direccion, codigo", [("vertical", "R2"),
                                               ("horizontal", "R1")])
def test_M05_verificar_cuantia_se_detiene_igual_que_cuantia_de_diseno(
        direccion, codigo):
    with sin_valor(CLAVE_REGIMEN):
        with pytest.raises(CriterioPendienteError) as excinfo:
            M9.verificar_cuantia(cuantia_provista=0.0025, direccion=direccion,
                                 cortante_alto=True)
    assert excinfo.value.clave == CLAVE_REGIMEN
    # y sin cortante alto sigue siendo el contraste de siempre
    v = M9.verificar_cuantia(cuantia_provista=0.0025, direccion=direccion,
                             cortante_alto=False)
    assert isinstance(v, Verificacion) and v.cumple and v.codigo == codigo
    assert v.criterio_aplicado is None          # [N] puro, Art. 14.3.1


def test_M05_verificar_cuantia_en_vertical_con_el_piso_declarado_lo_usa():
    """
    Una cuantia vertical de 0.0020 cumple el 14.3.1 (0.0015) y NO cumple el
    piso declarado del 11.10.10.3: la verificacion tiene que decir que no.
    """
    with con_valor(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_EN_EL_PLANO,
                   motivo=MOTIVO_PRUEBA), \
            con_valor(CLAVE_VERTICAL, CUANTIA_V_DE_PRUEBA, motivo=MOTIVO_PRUEBA):
        v = M9.verificar_cuantia(cuantia_provista=0.0020, direccion="vertical",
                                 cortante_alto=True)
    assert not v.cumple
    assert v.valor_admisible == pytest.approx(CUANTIA_V_DE_PRUEBA, rel=REL_CP9)
    assert v.criterio_aplicado == CLAVE_VERTICAL
    assert v.codigo == "R2"


def test_M05_el_docstring_ya_no_afirma_lo_contrario_de_la_norma():
    """
    R95-031: la afirmacion negativa falsa («en vertical, cortante_alto=True
    no cambia el minimo del Art. 14.3.1») no puede seguir escrita en el
    modulo, ni en el docstring ni como comentario.
    """
    fuente = (RAIZ / "src" / "modulos" / "M9_cabezal.py").read_text(
        encoding="utf-8")
    assert "no cambia el minimo" not in fuente
    for termino in ("11.10.10.3", "11.10.2", "11.10.1"):
        assert termino in M9.cuantia_de_diseno.__doc__, (
            f"el docstring de cuantia_de_diseno no cita el {termino}")


def test_M05_el_regimen_fuera_de_las_dos_lecturas_se_rechaza_en_la_puerta():
    """Categoria cerrada: la puerta de declaracion lo rechaza (SIS-E-05)."""
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE_REGIMEN, "diagonal")
    ca.establecer_valor_dinamico(CLAVE_REGIMEN, CN.REGIMEN_CORTANTE_EN_EL_PLANO)
    try:
        assert ca.valor(CLAVE_REGIMEN) == CN.REGIMEN_CORTANTE_EN_EL_PLANO
    finally:
        ca.quitar_valor_dinamico(CLAVE_REGIMEN)


def test_M05_la_ec_11_32_no_se_implementa_y_queda_dicho_donde():
    """
    Faltan lm y Vu. La decision no es un olvido: esta en
    docs/decisiones_diferidas.md anclada a `cuantia_de_diseno`, y el codigo
    no contiene la formula.
    """
    arbol = ast.parse((RAIZ / "src" / "modulos" / "M9_cabezal.py").read_text(
        encoding="utf-8"))
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
    argumentos = {a.arg for n in ast.walk(arbol)
                  if isinstance(n, ast.FunctionDef) for a in n.args.kwonlyargs}
    for simbolo in ("hm", "lm", "rho_h", "rho_h_requerida"):
        assert simbolo not in nombres | argumentos, (
            f"M9 opera con `{simbolo}`: la ec. (11-32) no se implementa en "
            "EXT-7 (faltan lm y Vu)")
    registro = (RAIZ / "docs" / "decisiones_diferidas.md").read_text(
        encoding="utf-8")
    assert "11-32" in registro
    assert "`src/modulos/M9_cabezal.py::cuantia_de_diseno`" in registro


def test_M05_las_citas_del_11_10_que_EXT6_dejo_tienen_ahora_consumidor(reg):
    """
    Las cuatro citas nacieron «por delante del codigo que las lea». Ahora
    las lee M9 a traves de `NUMERAL_CORTANTE_MUROS_E060`, y los dos criterios
    nuevos las nombran en su fuente.
    """
    for cita_id, clave in (("E060.11.10.2", CLAVE_REGIMEN),
                           ("E060.11.10.1", CLAVE_REGIMEN),
                           ("E060.11.10.10.3", CLAVE_VERTICAL)):
        assert reg.cita(cita_id).numeral in ca.criterio(clave).fuente


# ===========================================================================
# M-06 · Ka de Coulomb (MP 2.4.4.1.5.3) en el empuje estatico y la sobrecarga
# ===========================================================================

def _declarar_angulos(monkeypatch, *, phi, i, beta, delta):
    """Los cuatro angulos de Sec. 9.2 y el gamma, de PRUEBA."""
    valores = {
        "phi_relleno_trasdos": phi,
        "pendiente_relleno_trasdos_i": i,
        "inclinacion_muro_beta": beta,
        "friccion_muro_suelo_delta": delta,
        "punto_aplicacion_incremento_sismico": 0.6,
        "peso_especifico_relleno_kn_m3": CP9["C_gamma_relleno"],
    }
    for clave, valor in valores.items():
        monkeypatch.setitem(ca.CRITERIOS, clave,
                            replace(ca.criterio(clave), valor=valor))
    monkeypatch.setitem(
        ds.DATOS_SITIO, "orientacion_muro_respecto_al_trafico",
        replace(ds.dato("orientacion_muro_respecto_al_trafico"),
                valor=CN.ORIENTACION_PARALELO_AL_TRAFICO))
    monkeypatch.setitem(
        ds.DATOS_SITIO, "distancia_borde_calzada_al_trasdos_m",
        replace(ds.dato("distancia_borde_calzada_al_trasdos_m"), valor=1.0))


def _angulos_c():
    return dict(phi=CP9["C_phi_grados"], i=CP9["C_i_grados"],
                beta=CP9["C_beta_grados"], delta=CP9["C_delta_grados"])


def test_M06_el_bloque_C_del_caso_patron_tiene_angulos_no_nulos_en_ventana():
    """
    El caso i = 20 grados de la auditoria NO es declarable (ventana 0-10).
    El bloque C esta dentro de las cuatro ventanas y con i, delta != 0, que
    es donde Coulomb y Rankine difieren.
    """
    ventanas = {"C_phi_grados": "phi_relleno_trasdos",
                "C_i_grados": "pendiente_relleno_trasdos_i",
                "C_beta_grados": "inclinacion_muro_beta",
                "C_delta_grados": "friccion_muro_suelo_delta"}
    for clave_cp, clave_ca in ventanas.items():
        bajo, alto = ca.criterio(clave_ca).sensibilidad
        assert bajo <= CP9[clave_cp] <= alto, f"{clave_cp} fuera de ventana"
    assert CP9["C_i_grados"] > 0 and CP9["C_delta_grados"] > 0
    assert CP9["C_K_A_coulomb_esperado"] != pytest.approx(
        CP9["C_K_A_rankine_esperado"], rel=REL_CP9)


def test_M06_k_a_coulomb_reproduce_el_dorado_del_bloque_C():
    K_A = M9.k_a_coulomb(phi_grados=CP9["C_phi_grados"],
                         i_grados=CP9["C_i_grados"],
                         beta_grados=CP9["C_beta_grados"],
                         delta_grados=CP9["C_delta_grados"])
    assert K_A == pytest.approx(CP9["C_K_A_coulomb_esperado"], rel=REL_CP9)
    assert M9.ka_rankine(phi_grados=CP9["C_phi_grados"]) == pytest.approx(
        CP9["C_K_A_rankine_esperado"], rel=REL_CP9)
    assert (K_A - CP9["C_K_A_rankine_esperado"]) / CP9["C_K_A_rankine_esperado"] \
        == pytest.approx(CP9["C_diferencia_relativa_coulomb_rankine"],
                         rel=REL_CP9)


def test_M06_el_empuje_estatico_del_ensamble_va_con_coulomb(monkeypatch,
                                                            geometria):
    """
    EL HALLAZGO. `EmpujesTrasdos.K_A` era el de Rankine; con i, delta != 0
    tiene que ser el de Coulomb del bloque C, y E_activo su empuje.
    """
    _declarar_angulos(monkeypatch, **_angulos_c())
    e = M9.empujes_trasdos(geometria=geometria,
                           condicion=CondicionAnalisis.ESTATICO,
                           altura_empuje=CP9["C_H"], NF_profundidad_m=1.4)
    assert e.K_A == pytest.approx(CP9["C_K_A_coulomb_esperado"], rel=REL_CP9)
    assert e.E_activo == pytest.approx(CP9["C_P_A_esperado"], rel=REL_CP9)
    assert e.K_A != pytest.approx(CP9["C_K_A_rankine_esperado"], rel=REL_CP9)


def test_M06_la_sobrecarga_va_con_el_mismo_Ka_que_el_empuje(monkeypatch,
                                                            geometria):
    """La sobrecarga tambien iba con Rankine (dictamen). Un solo Ka."""
    _declarar_angulos(monkeypatch, **_angulos_c())
    e = M9.empujes_trasdos(geometria=geometria,
                           condicion=CondicionAnalisis.ESTATICO,
                           altura_empuje=CP9["C_H"], NF_profundidad_m=1.4)
    assert e.E_sobrecarga == pytest.approx(
        e.gamma_relleno * e.K_A * e.h_eq_sobrecarga * CP9["C_H"], rel=REL_CP9)


def test_M06_en_sismico_el_Ka_del_ensamble_y_el_de_mononobe_okabe_son_uno(
        monkeypatch, geometria):
    """
    Base homogenea: el K_A que resta el incremento y el que calcula el
    empuje estatico son el MISMO numero, tambien con angulos no nulos.
    Antes solo coincidian con i = beta = delta = 0.
    """
    _declarar_angulos(monkeypatch, **_angulos_c())
    e = M9.empujes_trasdos(geometria=geometria,
                           condicion=CondicionAnalisis.SISMICO,
                           altura_empuje=CP9["C_H"], NF_profundidad_m=1.4)
    assert e.mononobe_okabe.K_A == pytest.approx(e.K_A, rel=REL_CP9)
    assert e.K_A == pytest.approx(CP9["C_K_A_coulomb_esperado"], rel=REL_CP9)


@pytest.mark.parametrize("clave", ["pendiente_relleno_trasdos_i",
                                   "inclinacion_muro_beta",
                                   "friccion_muro_suelo_delta"])
def test_M06_el_estatico_ya_no_ignora_los_tres_angulos(monkeypatch, geometria,
                                                       clave):
    """
    Con Rankine el estatico solo leia phi; con Coulomb los cuatro angulos
    son entrada tambien en condicion ESTATICA, y un vacio lo detiene.
    """
    _declarar_angulos(monkeypatch, **_angulos_c())
    with sin_valor(clave):
        with pytest.raises(CriterioPendienteError) as excinfo:
            M9.empujes_trasdos(geometria=geometria,
                               condicion=CondicionAnalisis.ESTATICO,
                               altura_empuje=CP9["C_H"], NF_profundidad_m=1.4)
    assert excinfo.value.clave == clave


def test_M06_la_cadena_sismica_del_bloque_C_contra_sus_dorados():
    c = CP9
    mo = M9.empuje_mononobe_okabe(
        phi_grados=c["C_phi_grados"], i_grados=c["C_i_grados"],
        beta_grados=c["C_beta_grados"], delta_grados=c["C_delta_grados"],
        k_h=c["C_k_h"], k_v=c["C_k_v"])
    assert mo.psi_grados == pytest.approx(c["C_psi_grados_esperado"], rel=REL_CP9)
    assert mo.K_AE == pytest.approx(c["C_K_AE_esperado"], rel=REL_CP9)
    assert mo.K_A == pytest.approx(c["C_K_A_coulomb_esperado"], rel=REL_CP9)
    P_AE = M9.empuje_activo_sismico_total(gamma_relleno=c["C_gamma_relleno"],
                                          K_AE=mo.K_AE, H=c["C_H"], k_v=mo.k_v)
    P_A = M9.empuje_activo_estatico(gamma_relleno=c["C_gamma_relleno"],
                                    k_a=mo.K_A, H=c["C_H"])
    assert P_AE == pytest.approx(c["C_P_AE_esperado"], rel=REL_CP9)
    assert P_A == pytest.approx(c["C_P_A_esperado"], rel=REL_CP9)
    assert P_AE - P_A == pytest.approx(c["C_incremento_P_esperado"], rel=REL_CP9)


@pytest.mark.parametrize("phi, ka", list(zip(CP9_RANKINE_LIMITE["phi_casos"],
                                             CP9_RANKINE_LIMITE["Ka_rankine_esperado"])))
def test_M06_ka_rankine_se_conserva_como_caso_limite(phi, ka):
    """`ka_rankine` no se retira: es el patron del caso limite (Sec. 9.2)."""
    assert M9.ka_rankine(phi_grados=phi) == pytest.approx(
        ka, rel=CP9_TOLERANCIA_RELATIVA)
    assert M9.k_a_coulomb(phi_grados=phi, i_grados=0.0, beta_grados=0.0,
                          delta_grados=0.0) == pytest.approx(
        ka, rel=CP9_TOLERANCIA_RELATIVA)


def test_M06_la_cita_de_coulomb_del_manual_esta_en_el_registro(reg):
    """
    MP 2.4.4.1.5.3 «Coeficiente de Empuje Lateral Activo, ka», pag. impresa
    135 (PDF 136). Su verificacion contra la pagina la hace
    tests/test_normativa_pdf.py como a toda cita.
    """
    c = reg.cita("MP.2.4.4.1.5.3")
    assert c.pagina_impresa == "135" and c.pagina_pdf == 136
    assert "Coulomb" not in c.texto_literal.texto, (
        "el Manual no escribe la palabra Coulomb en el articulado; la "
        "escribe en el pie de su figura. El verbatim es lo que dice el texto")
    assert "se puede tomar como" in c.texto_literal.texto
    assert c.caracter is Caracter.PERMISO
    assert "3.11.5.3" in c.nota            # el numeral AASHTO que el Manual traduce


def test_M06_la_discrepancia_con_la_hoja_de_ruta_esta_declarada_y_resuelta(reg):
    """
    La v8 §9.2 escribia «Ka = tan2(45 - phi/2)» y EXT-0 la enmendo: la
    discrepancia se registra RESUELTA, con la hoja de ruta y el Manual como
    partes, anclada a la cita. Es la obligacion de CLAUDE.md escrita como
    objeto, no como prosa.
    """
    d = reg.discrepancia("DIS-HR-KA-COULOMB")
    assert d.estado is EstadoDiscrepancia.RESUELTA
    assert {p.quien for p in d.partes} >= {"hoja_de_ruta", "MP"}
    assert "MP.2.4.4.1.5.3" in d.citas
    assert d.gana == "MP"
    assert d.id in [x.id for x in reg.discrepancias_de_cita("MP.2.4.4.1.5.3")]


def test_M06_el_punto_de_uso_declara_coulomb_y_la_memoria_lo_recibe():
    """
    Declarar «en el punto de uso»: `empujes_trasdos` dice de donde sale su
    Ka, el objeto lo lleva (`numeral_k_a`) y `condicion_normativa_cabezal`
    lo imprime con el numeral del Manual.
    """
    assert "2.4.4.1.5.3" in CN.NUMERAL_KA_COULOMB
    assert "2.4.4.1.5.3" in M9.empujes_trasdos.__doc__
    assert "DIS-HR-KA-COULOMB" in M9.empujes_trasdos.__doc__
    texto = "\n".join(M9.condicion_normativa_cabezal())
    assert "2.4.4.1.5.3" in texto and "Coulomb" in texto
    assert "tan" in texto          # dice que la forma reducida es la de la v8
    # Y declara que la resultante inclinada se toma ENTERA como horizontal,
    # con su direccion (auditoria adversarial de EXT-7; EXT-7-04).
    assert "delta + beta" in texto and "ENTERA" in texto
    assert "cos(delta + beta)" in M9.empujes_trasdos.__doc__
    registro = (RAIZ / "docs" / "decisiones_diferidas.md").read_text(
        encoding="utf-8")
    assert "`src/modelos.py::EmpujesTrasdos`" in registro


def test_M06_el_objeto_lleva_el_numeral_del_Ka(monkeypatch, geometria):
    _declarar_angulos(monkeypatch, **_angulos_c())
    e = M9.empujes_trasdos(geometria=geometria,
                           condicion=CondicionAnalisis.ESTATICO,
                           altura_empuje=CP9["C_H"], NF_profundidad_m=1.4)
    assert e.numeral_k_a == CN.NUMERAL_KA_COULOMB


def test_M06_la_sensibilidad_de_i_dice_donde_se_agota_mononobe_okabe():
    """
    Con k_h = 0.50 (psi = 26.6 grados) la formula solo tiene solucion para
    i < phi - psi: 3.4 grados con phi = 30 y 8.4 con phi = 35. La ventana
    0-10 no es alcanzable entera en condicion sismica, y la ficha lo dice.
    """
    c = ca.criterio("pendiente_relleno_trasdos_i")
    texto = (c.justificacion + " " + (c.verificacion_pendiente or "")).lower()
    assert "26.6" in texto or "26,6" in texto
    assert "3.4" in texto and "8.4" in texto
    # y el numero es el que sale de la cadena sismica de la obra, no uno
    # escrito a mano: los dos limites de la ficha, redondeados a la decima
    # de grado con que la ficha los escribe, son phi - psi.
    psi = M9.angulo_inercia_sismica(k_h=M9.cadena_sismica().k_h, k_v=0.0)
    limites = {phi: f"{phi - psi:.1f}" for phi in (30, 35)}
    assert f"{psi:.1f}" == "26.6"
    assert limites[30] == "3.4" and limites[35] == "8.4"


# ===========================================================================
# M-07 · EstabilidadCabezal: exigidas, pendientes y `estable` honesto
# ===========================================================================

def _verificacion(codigo: str, cumple: bool = True) -> Verificacion:
    return Verificacion(cumple=cumple, numeral="prueba", valor_obtenido=2.0,
                        valor_admisible=1.5, criterio_aplicado=None,
                        codigo=codigo)


def test_M07_las_exigidas_se_derivan_de_la_tabla_de_FS():
    """E1..E5 son las cinco filas de Sec. 9.3, una por clave de `FS`."""
    assert set(CN.FS_CODIGO) == set(CN.FS)
    assert tuple(CN.FS_CODIGO[k] for k in CN.FS) == M9.EXIGIDAS_SEC_9_3
    assert M9.EXIGIDAS_SEC_9_3 == ("E1", "E2", "E3", "E4", "E5")


def test_M07_el_conjunto_vacio_ya_no_es_estable(geometria):
    with pytest.raises(ValueError, match="vac"):
        EstabilidadCabezal(condicion=CondicionAnalisis.ESTATICO,
                           geometria=geometria, verificaciones=(),
                           exigidas=M9.EXIGIDAS_SEC_9_3)


def test_M07_un_codigo_fuera_de_las_exigidas_se_rechaza(geometria):
    with pytest.raises(ValueError, match="E9"):
        EstabilidadCabezal(condicion=CondicionAnalisis.ESTATICO,
                           geometria=geometria,
                           verificaciones=(_verificacion("E1"),
                                           _verificacion("E9")),
                           exigidas=M9.EXIGIDAS_SEC_9_3)


def test_M07_sin_exigidas_no_hay_expediente(geometria):
    with pytest.raises(ValueError, match="exigidas"):
        EstabilidadCabezal(condicion=CondicionAnalisis.ESTATICO,
                           geometria=geometria,
                           verificaciones=(_verificacion("E1"),),
                           exigidas=())


def test_M07_un_codigo_repetido_se_rechaza(geometria):
    with pytest.raises(ValueError, match="repet"):
        EstabilidadCabezal(condicion=CondicionAnalisis.ESTATICO,
                           geometria=geometria,
                           verificaciones=(_verificacion("E1"),
                                           _verificacion("E1")),
                           exigidas=M9.EXIGIDAS_SEC_9_3)


def test_M07_con_E1_a_E3_cumplidas_la_interna_cumple_y_estable_es_False(
        geometria):
    """EL HALLAZGO: tres de cinco no es estable. Es «interna cumple»."""
    e = EstabilidadCabezal(
        condicion=CondicionAnalisis.ESTATICO, geometria=geometria,
        verificaciones=tuple(_verificacion(c) for c in ("E1", "E2", "E3")),
        exigidas=M9.EXIGIDAS_SEC_9_3)
    assert e.estabilidad_interna_cumple
    assert not e.estable
    assert e.pendientes == ("E4", "E5")
    assert e.verificaciones_incumplidas == ()


def test_M07_estable_solo_con_todas_las_exigidas_presentes_y_cumplidas(
        geometria):
    todas = tuple(_verificacion(c) for c in M9.EXIGIDAS_SEC_9_3)
    e = EstabilidadCabezal(condicion=CondicionAnalisis.ESTATICO,
                           geometria=geometria, verificaciones=todas,
                           exigidas=M9.EXIGIDAS_SEC_9_3)
    assert e.estable and e.pendientes == () and e.estabilidad_interna_cumple
    # una sola incumplida, y deja de serlo aunque no falte ninguna
    con_fallo = todas[:3] + (_verificacion("E4", cumple=False),) + todas[4:]
    e2 = replace(e, verificaciones=con_fallo)
    assert not e2.estable and not e2.estabilidad_interna_cumple
    assert [v.codigo for v in e2.verificaciones_incumplidas] == ["E4"]


def test_M07_verificar_estabilidad_registra_E4_y_E5_como_pendientes(geometria):
    """
    Antes las omitia; ahora el objeto dice que faltan y POR QUE: el criterio
    que las bloquea.
    """
    e = M9.verificar_estabilidad(
        geometria=geometria, condicion=CondicionAnalisis.SISMICO,
        q_actuante=100.0, q_ultima=300.0,
        momento_estabilizante=200.0, momento_volcante=100.0,
        fuerza_resistente=80.0, fuerza_actuante=50.0)
    assert [v.codigo for v in e.verificaciones] == ["E1", "E2", "E3"]
    assert e.exigidas == M9.EXIGIDAS_SEC_9_3
    assert e.pendientes == ("E4", "E5")
    assert dict(e.motivos_pendientes) == {
        "E4": "metodo_estabilidad_global", "E5": "metodo_estabilidad_global"}
    assert e.estabilidad_interna_cumple and not e.estable


def test_M07_un_motivo_de_pendiente_sobre_una_presente_se_rechaza(geometria):
    with pytest.raises(ValueError, match="motivos_pendientes"):
        EstabilidadCabezal(
            condicion=CondicionAnalisis.ESTATICO, geometria=geometria,
            verificaciones=tuple(_verificacion(c) for c in ("E1", "E2", "E3")),
            exigidas=M9.EXIGIDAS_SEC_9_3,
            motivos_pendientes=(("E1", "metodo_estabilidad_global"),))


def test_M07_E6_no_entra_en_las_exigidas_por_defecto_y_queda_dicho():
    """
    E6 (`verificar_excentricidad_sismica`) no es fila de la tabla de FS de
    Sec. 9.3: entra solo si quien llama la pasa en `exigidas`. La decision
    esta en docs/decisiones_diferidas.md, anclada al simbolo.
    """
    assert "E6" not in M9.EXIGIDAS_SEC_9_3
    registro = (RAIZ / "docs" / "decisiones_diferidas.md").read_text(
        encoding="utf-8")
    assert "`src/modulos/M9_cabezal.py::EXIGIDAS_SEC_9_3`" in registro


def test_M07_verificar_estabilidad_admite_exigir_E6(geometria):
    """Quien tenga E6 la pasa ampliando `exigidas`, y queda como pendiente."""
    e = M9.verificar_estabilidad(
        geometria=geometria, condicion=CondicionAnalisis.SISMICO,
        q_actuante=100.0, q_ultima=300.0,
        momento_estabilizante=200.0, momento_volcante=100.0,
        fuerza_resistente=80.0, fuerza_actuante=50.0,
        exigidas=M9.EXIGIDAS_SEC_9_3 + ("E6",))
    assert e.pendientes == ("E4", "E5", "E6")
    assert not e.estable


# ===========================================================================
# Nada se cablea a la CLI
# ===========================================================================

def test_EXT7_nada_se_cablea_a_la_cli():
    """
    `FUNCIONES_SIN_CONSUMIDOR` sigue nombrando a las tres familias tocadas,
    y ni cli.py ni M11 las llaman.
    """
    for nombre in ("empujes_trasdos", "verificar_estabilidad",
                   "armado del num. 9.4 (ocho funciones)"):
        assert nombre in M9.FUNCIONES_SIN_CONSUMIDOR
    for archivo in ("cli.py", "src/modulos/M11_reporte.py"):
        arbol = ast.parse((RAIZ / archivo).read_text(encoding="utf-8"))
        llamadas = {n.func.attr for n in ast.walk(arbol)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)}
        assert not llamadas & {"empujes_trasdos", "verificar_estabilidad",
                               "cuantia_de_diseno", "verificar_cuantia"}, (
            f"{archivo} llama a una funcion de M9 que EXT-7 no cablea")
