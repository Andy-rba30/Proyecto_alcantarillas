"""
tests/test_ve5_m9_portante_talud.py
===================================
VE-5, lote M9, item 3 del censo (ficha T7B-04): la capacidad portante del
cabezal con la reduccion por talud de AASHTO LRFD 10.6.3.1.2c (RC_BC de las
Tablas 10.6.3.1.2c-1 y -2), que SUSTITUYE la lectura de los abacos de
Meyerhof del Manual de Puentes ('N_cq_N_gammaq_meyerhof', retirado), y los
factores de forma y de profundidad de la Tabla 10.6.3.1.2a-3 y la ec.
10.6.3.1.2a-10 ('factores_forma_profundidad_portante' [A]).

Oraculos: celdas leidas en el PDF (pags. impresas 10-76 a 10-78) y
aritmetica escrita. Escritos ANTES del codigo.
"""

import math

import pytest

from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src.modelos import (CondicionAnalisis, DatoInvalidoError,
                         MetodoNoEvaluableError)
from src.modulos import M9_cabezal as M9
from src.normativa import fuentes
from tests.apoyo.criterios import declarados

from tests.apoyo.aproximacion import ABS_CERO

TOL = 1e-6              # coeficientes: las tablas a dos decimales, interpoladas
TOL_KPA = 1e-4          # presiones escritas a cuatro decimales
FILAS_BH_1 = (0.1, 0.2, 0.4, 0.6, 1, 1.5, 3)      # B/H de la Tabla -1
FILAS_BH_2 = (0.2, 0.5, 1, 2)                      # B/H de la Tabla -2
FILAS_BB_2 = (0, 0.5, 1.25, 2.5, 5, 10)            # b/B de la Tabla -2


# --- las tablas, contra el PDF ----------------------------------------------

def test_celdas_leidas_a_mano_en_las_dos_tablas():
    t1, t2 = cn.RCBC_EN_TALUD_T10_6_3_1_2C_1, cn.RCBC_JUNTO_AL_TALUD_T10_6_3_1_2C_2
    # Tabla -1, phi = 30, B/H = 3: «0.95 0.74 0.70 0.65 | 0.92 0.66 0.60 0.51
    # | 0.90 0.62 0.57 0.43 | 0.88 0.59 0.51 0.00»
    assert t1[30][3][30] == (0.90, 0.62, 0.57, 0.43)  # float-exacto: transcrito
    assert t1[0][0.2][20] == (0.89, 0.87, 0.86, 0.00)  # float-exacto: transcrito
    # Tabla -2, phi = 30, B/H = 1, b/B = 0.5: «0.78 0.87 0.89 0.74 | 0.75 0.74
    # 0.74 0.51 | 0.64 0.62 0.60 0.35 | 0.59 0.56 0.54 0.00»
    assert t2[30][1][0.5][30] == (0.64, 0.62, 0.60, 0.35)  # float-exacto: transcrito
    assert t2[0][0.2][0.5][10] == (0.97, 0.96, 0.96, 0.00)  # float-exacto: transcrito
    assert sorted(t1) == sorted(t2) == [0, 20, 30, 40]
    for p in t1:
        assert sorted(t1[p]) == pytest.approx(FILAS_BH_1, abs=ABS_CERO)
    for p in t2:
        assert sorted(t2[p]) == pytest.approx(FILAS_BH_2, abs=ABS_CERO)
        for r in t2[p]:
            assert sorted(t2[p][r]) == pytest.approx(FILAS_BB_2, abs=ABS_CERO)


def _parsear(texto, pagina_inicial):
    """El mismo analizador que transcribio las tablas, sobre el PDF."""
    import re
    t = texto.split("©")[0]
    t = t[t.index("c'=0"):]
    t = t.replace("(On Slope)", "").replace("(On", "").replace("Slope)", "")
    out = re.findall(r"c'=0|\d+(?:\.\d+)?", t)
    k = n = 0
    while n < 4:
        n += out[k] == "c'=0"
        k += 1
    return [x for x in out[k:]]


@pytest.mark.pdf
def test_las_dos_tablas_son_las_del_pdf_celda_a_celda():
    from src.normativa.extraccion import texto_de_pagina
    ruta = fuentes.ruta_pdf(fuentes.FUENTES["AASHTO_LRFD_9"])
    if not ruta.exists():
        pytest.skip("el PDF de AASHTO LRFD no esta enlazado")

    def valores(tabla):
        # los valores de cada fila en el orden de impresion
        for phi in sorted(tabla):
            for clave in sorted(tabla[phi]):
                nodo = tabla[phi][clave]
                hojas = ([nodo] if isinstance(nodo[10], tuple) else
                         [nodo[k] for k in sorted(nodo)])
                for hoja in hojas:
                    for beta in (10, 20, 30, 40):
                        yield from hoja[beta]

    def del_pdf(paginas):
        fichas = []
        for p in paginas:
            fichas += _parsear(texto_de_pagina(ruta, p), p)
        return [float(x) for x in fichas
                if re.fullmatch(r"[01]\.\d\d", x) and float(x) <= 1.0]

    import re
    assert list(valores(cn.RCBC_EN_TALUD_T10_6_3_1_2C_1)) == del_pdf([1365])
    assert list(valores(cn.RCBC_JUNTO_AL_TALUD_T10_6_3_1_2C_2)) == del_pdf(
        [1366, 1367])


# --- el coeficiente ---------------------------------------------------------

def test_rcbc_interpola_en_beta_y_en_n_s():
    """
    Cohesivo (phi = 0), en el talud (b = 0), B/H = 0.2, beta = 15, N_s = 1:
      beta 10: N_s 0 -> 0.89, N_s 2 -> 0.88 -> 0.885
      beta 20: N_s 0 -> 0.89, N_s 2 -> 0.87 -> 0.880
      beta 15 -> 0.8825
    """
    rc, _ = M9.coeficiente_rcbc(phi_grados=0.0, c_kpa=18.0, gamma=18.0,
                                B=0.2, H_s=1.0, b=0.0, beta_grados=15.0)
    assert rc == pytest.approx(0.8825, abs=TOL)


def test_rcbc_cohesionless_usa_la_columna_c_cero_de_la_tabla_junto_al_talud():
    rc, det = M9.coeficiente_rcbc(phi_grados=30.0, c_kpa=0.0, gamma=18.0,
                                  B=2.0, H_s=2.0, b=1.0, beta_grados=30.0)
    assert rc == pytest.approx(0.35, abs=TOL)
    assert det["tabla"] == "10.6.3.1.2c-2"


def test_bajo_diez_grados_rige_la_fila_de_diez():
    """El talud mas tendido de la tabla es 10 grados: con menos se toma esa
    fila (el coeficiente crece al tender el talud: lado seguro)."""
    a, _ = M9.coeficiente_rcbc(phi_grados=30.0, c_kpa=0.0, gamma=18.0, B=2.0,
                               H_s=2.0, b=1.0, beta_grados=5.0)
    assert a == pytest.approx(0.74, abs=TOL)


@pytest.mark.parametrize("cambio", [
    dict(beta_grados=45.0),                     # talud mas empinado que 40
    dict(c_kpa=2.0, phi_grados=0.0),            # N_s = 18 > 4
    dict(phi_grados=42.0),                      # phi fuera de la tabla
    dict(H_s=0.4),                              # B/H = 5 > 2 (junto al talud)
])
def test_fuera_de_las_tablas_no_hay_cifra(cambio):
    base = dict(phi_grados=30.0, c_kpa=0.0, gamma=18.0, B=2.0, H_s=2.0,
                b=1.0, beta_grados=30.0)
    base.update(cambio)
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.coeficiente_rcbc(**base)
    assert "10.6.3.1.2c" in str(exc.value)


def test_la_capacidad_en_talud_es_rcbc_por_la_ecuacion_sin_empotramiento():
    """
    Cohesivo: c = 40, gamma = 18, B = 1.5, H_s = 7.5 (B/H = 0.2), b = 0,
    beta = 20; N_s = 18·7.5/40 = 3.375 -> 0.87 + (0.86 - 0.87)·1.375/2 =
    0.863125. q = RC·c·N_c = 0.863125·40·5.14 = 177.4585 kPa.
    """
    q, det = M9.capacidad_portante_zapata_en_talud(
        B=1.5, H_s=7.5, b=0.0, beta_grados=20.0, gamma=18.0, c=40.0,
        phi_grados=0.0)
    assert det["RC_BC"] == pytest.approx(0.863125, abs=TOL)
    assert q == pytest.approx(0.863125 * 40 * 5.14, abs=TOL_KPA)
    # friccionante: 0.35·0.5·18·2.0·22.4 = 141.12
    q, _ = M9.capacidad_portante_zapata_en_talud(
        B=2.0, H_s=2.0, b=1.0, beta_grados=30.0, gamma=18.0, c=0.0,
        phi_grados=30.0)
    assert q == pytest.approx(0.35 * 0.5 * 18.0 * 2.0 * 22.4, abs=TOL_KPA)


# --- forma y profundidad ----------------------------------------------------

def test_forma_y_profundidad_de_la_tabla_10_6_3_1_2a_3():
    """
    phi = 30, c = 0, gamma = 18, B' = 2, L = 6 (B/L = 1/3), D_f = 1, sin
    agua ni inclinacion:
      s_q = 1 + tan30/3 = 1.192450;  s_gamma = 1 - 0.4/3 = 0.866667
      d_q = 1 + 2·tan30·(1 - sen30)²·arctan(0.5) = 1.133844
      q_n = 18·1·18.4·s_q·d_q + 0.5·18·2·22.4·s_gamma
    """
    suelo = {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 30.0,
             "gamma_kn_m3": 18.0}
    comun = dict(suelo=suelo, B_efectivo=2.0, D_f=1.0, D_w=50.0,
                 H_servicio=0.0, V_servicio=100.0, aplicar_inclinacion=False)
    # (VE-5) las dos piezas, nombradas: forma y profundidad sueltas.
    assert M9.factores_de_forma(phi_grados=30.0, B=2.0, L=6.0, N_c=30.1,
                                N_q=18.4)[1] == pytest.approx(
        1 + math.tan(math.radians(30)) / 3, abs=TOL)
    assert M9.factor_de_profundidad(phi_grados=30.0, D_f=1.0,
                                    B=2.0) == pytest.approx(
        1 + 2 * math.tan(math.radians(30)) * 0.25 * math.atan(0.5), abs=TOL)
    q0, d0 = M9.resistencia_portante_nominal(**comun)
    assert q0 == pytest.approx(18 * 1 * 18.4 + 0.5 * 18 * 2 * 22.4, abs=TOL_KPA)
    s_q = 1 + math.tan(math.radians(30)) / 3
    s_g = 1 - 0.4 / 3
    d_q = 1 + 2 * math.tan(math.radians(30)) * 0.25 * math.atan(0.5)
    q1, d1 = M9.resistencia_portante_nominal(**comun, longitud=6.0)
    assert d1["s_q"] == pytest.approx(s_q, abs=TOL)
    assert d1["s_gamma"] == pytest.approx(s_g, abs=TOL)
    assert q1 == pytest.approx(18 * 18.4 * s_q + 0.5 * 18 * 2 * 22.4 * s_g,
                               abs=TOL_KPA)
    q2, d2 = M9.resistencia_portante_nominal(**comun, longitud=6.0,
                                             profundidad=True)
    assert d2["d_q"] == pytest.approx(d_q, abs=TOL)
    assert q2 == pytest.approx(18 * 18.4 * s_q * d_q
                               + 0.5 * 18 * 2 * 22.4 * s_g, abs=TOL_KPA)


def test_d_q_no_pasa_de_1_4():
    suelo = {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 30.0,
             "gamma_kn_m3": 18.0}
    _q, d = M9.resistencia_portante_nominal(
        suelo=suelo, B_efectivo=0.5, D_f=40.0, D_w=80.0, H_servicio=0.0,
        V_servicio=100.0, aplicar_inclinacion=False, longitud=6.0,
        profundidad=True)
    assert d["d_q"] <= cn.DQ_MAXIMO_10_6_3_1_2A_10 + TOL


# --- los criterios ----------------------------------------------------------

def test_meyerhof_se_retiro_y_entran_la_geometria_y_la_forma():
    assert "N_cq_N_gammaq_meyerhof" not in ca.CRITERIOS
    t = ca.CRITERIOS["talud_delante_del_cabezal"]
    assert t.valor is None and t.etiqueta == "S"
    f = ca.CRITERIOS["factores_forma_profundidad_portante"]
    assert f.valor == "corrida_sin_profundidad" and f.etiqueta == "A"
    assert tuple(f.sensibilidad) == ("corrida_sin_profundidad",
                                     "forma_con_la_longitud_del_cabezal",
                                     "forma_y_profundidad")


SUELO = {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0,
         "gamma_kn_m3": 18.0}


def test_la_admisible_de_corredor_tiene_consumidor():
    """'capacidad_portante_adm' [S] entra como el q_adm_kpa del suelo de
    corredor cuando 'c_phi_fundacion' no lo trae; si los dos difieren, el
    expediente se contradice. El suelo de un punto no la hereda."""
    with declarados({"c_phi_fundacion": dict(SUELO),
                     "capacidad_portante_adm": 150.0}):
        suelo, origen = M9.suelo_de_fundacion()
        assert suelo["q_adm_kpa"] == pytest.approx(150.0, abs=ABS_CERO)
        assert "capacidad_portante_adm" in origen
        punto, _ = M9.suelo_de_fundacion(dict(SUELO))
        assert "q_adm_kpa" not in punto
    with declarados({"c_phi_fundacion": dict(SUELO, q_adm_kpa=120.0),
                     "capacidad_portante_adm": 150.0}):
        with pytest.raises(DatoInvalidoError):
            M9.suelo_de_fundacion()


@pytest.fixture
def tanteo(monkeypatch):
    from types import SimpleNamespace
    from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD as CP
    from tests.test_t7b_cabezal_estabilidad import (_declarar_sitio,
                                                    _entorno)
    ca.establecer_valor_dinamico("eta_importancia_operativa_conducto", 1.0)
    ca.establecer_valor_dinamico("phi_relleno_trasdos", CP["phi_relleno"])
    ca.establecer_valor_dinamico("peso_especifico_relleno_kn_m3",
                                 CP["gamma_relleno"])
    ca.establecer_valor_dinamico("drenaje_trasdos", "drenado")
    ca.establecer_valor_dinamico("fila_phi_estabilidad_cabezal",
                                 "zapatas_seccion_10")
    _declarar_sitio()
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h0=0.25, k_h=0.25, k_v=0.0))
    return _entorno()


def test_el_ensamble_en_ladera_pide_la_geometria_del_talud_y_la_usa(tanteo):
    from src.modelos import CriterioPendienteError
    est = CondicionAnalisis.ESTATICO
    llano = next(x for x in M9.ensamble_estabilidad(tanteo, est).verificaciones
                 if x.codigo == "E1-LRFD.est.e")
    with declarados({"terreno_delante_del_cabezal": "talud_descendente"}):
        with pytest.raises(CriterioPendienteError) as exc:
            M9.ensamble_estabilidad(tanteo, est)
        assert exc.value.clave == "talud_delante_del_cabezal"
        with declarados({"talud_delante_del_cabezal":
                         {"H_s_m": 4.0, "beta_grados": 20.0, "b_m": 0.0}}):
            e = M9.ensamble_estabilidad(tanteo, est)
    v = next(x for x in e.verificaciones if x.codigo == "E1-LRFD.est.e")
    assert 0 < v.valor_admisible < llano.valor_admisible


def test_un_talud_declarado_mal_no_entra():
    with pytest.raises((DatoInvalidoError, ValueError)):
        M9.validar_talud_delante({"H_s_m": -1.0, "beta_grados": 20.0,
                                  "b_m": 0.0})
