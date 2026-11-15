"""
tests/test_t5_correcciones_auditoria.py
=======================================
El cierre de T-5 de la cadena T: lo que corrigieron las DOS auditorias
adversariales de la Fase 8 real del conducto (INF-3.3.5) y las decisiones del
dueño del proyecto del 2026-11-12 sobre lo que las auditorias dejaron «para
el dueño».

Cada bloque nombra el hallazgo que cierra (F = auditoria «fable», O = auditoria
«opus», con su numero) y fija lo que la FASE A no fijaba:

  1. F-H1   gobierna el vehiculo de mayor EFECTO, no el de mayor presion;
  2. F-H2   la carga viva pasados 8 ft se CONSERVA; despreciarla es un
     O-H11  criterio [A] declarado ('carga_viva_bajo_relleno_alto');
  3. O-H2   `tipo_4` en la ventana de la instalacion y el Tipo 4 impreso al
            lado como contraste;
  4. O-H1   el HDPE sin el perfil del fabricante queda «no verificado con un
     F-H3   producto real» y no se adopta; relleno granular (EG-2013 508.02);
     O-H4   pandeo por la letra de 12.12.3.3; factor de flexibilidad
     O-H5   (12.12.3.6);
  5. F-H4   la costura del TMC: aviso fijo, pista de otra fabricacion y
     O-H3   progresion de plancha (el caso G2 esta en test_t4);
  6. F-H5   las clases de M 170M por diametro, el mensaje del bloqueo y el
     O-H6/7 «no cumple» cuando estan todas;
  7. F-H6   los huecos que dejo la mutacion: deflexion admisible, rama
     O-H8   elastica del pandeo, relleno maximo del TMC y del HDPE, muestreo
            del primer cruce, nivel freatico, margenes;
  8. F-H7   el caracter del umbral se lee de la cita;
  9. F-H8   el nivel de los criterios, medido por corridas que llegan al TMC
     O-H13  y al HDPE;
 10. F-H11  lo que no se verifica, por material; guardias de segunda linea
     O-H9   (F-H14, O-H12); un punto al que solo le falta un dato no es «no
            factible»; el motivo de MD cuando el catalogo se agota por la
            Fase 8 (O-H14).

LOS DORADOS SE CALCULARON A MANO en unidades inglesas, sin M8:
`tests/fixtures/casos_patron.py::CP_FASE_8_CIERRE`, con la aritmetica escrita.

ESTOS TESTS NO SE ESCRIBIERON EN ROJO ANTES DEL CODIGO (el encargo llego con
las dos auditorias y las decisiones del dueño a media sesion). El rojo se
midio despues, contra el arbol de la FASE A rebasada (`1768b45`): ver el
informe de cierre de la sesion y la ficha T5-10.
"""

import ast
import json
import math
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from conftest import CLAVE_ESPESOR_PARED
from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src.modelos import (DatoFaltanteError, DatoInvalidoError, FormaSeccion,
                         SeccionCircular, SeccionRectangular, TipoMaterial)
from src.modulos import M5_verificaciones as M5
from src.modulos import M8_estructural as M8
from src.modulos import MD
from src.modulos.M2_material import catalogo
from src.normativa import registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP_FASE_8_CIERRE as CP
from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP_A

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"

# Las tolerancias de este archivo:
#   REL            el dorado calculado a mano en unidades inglesas (la
#                  constante del agua difiere un 0.08 %): la del caso patron.
#   ABS_ALTURA_M   una altura escrita con tres decimales: 1 mm.
#   ABS_CRUCE_M    cuanto se aparta uno del relleno maximo para comprobar que
#                  ES un cruce: 1 cm.
#   REL_PLANCHA    un dorado hecho con el relleno NOMINAL contra un paso
#                  calculado con la plancha que la progresion eligio, que
#                  sube la clave unos milimetros: 2 %.
#   REL_EN_EL_CRUCE  una magnitud evaluada a 1 cm del relleno maximo contra
#                  su valor EN el cruce: 0.2 % (la pendiente por 1 cm).
#   ABS_DLOAD_EN_EL_CRUCE  lo mismo para la D-load, en N/m/mm: 0.2.
#   REL_EMPALME    las dos ramas del pandeo evaluadas a 1e-9 del umbral.
#   REL_ESTIMA     una estimacion a mano que desprecia la carga viva y el
#                  agua frente a la tierra a 26 m de relleno: 3 %.
#   REL_NO_ES      cuanto tiene que apartarse un numero de OTRO para afirmar
#                  que no es ese (el camion frente al tandem): 5 %.
REL = CP["tolerancia_rel"]
ABS_ALTURA_M = 1e-3
ABS_CRUCE_M = 0.01
REL_PLANCHA = 0.02
REL_EN_EL_CRUCE = 2e-3
ABS_DLOAD_EN_EL_CRUCE = 0.2
REL_EMPALME = 1e-6
REL_ESTIMA = 0.03
REL_NO_ES = 0.05
#   REL_FINA       un numero de una sola operacion (F_u/2 entre 1.02 al
#                  cuadrado): solo redondeo. Hace falta para separar las dos
#                  ramas del pandeo cerca de su empalme, donde difieren 0.16 %.
#   ABS_PLANCHA_M  la clave que sube con una plancha mas gruesa: 0.76 mm
#                  entre la de 2.01 y la de 2.77; se compara a la centesima
#                  de milimetro.
REL_FINA = 1e-4
ABS_PLANCHA_M = 1e-5

# Un perfil «del fabricante»: el minimo de la Tabla A12-11 declarado como si
# fuera el del producto (declaracion legal: nada queda por debajo del minimo).
PERFIL_DECLARADO = {
    str(D_mm): {"A_mm2_mm": f["A_mm2_mm"], "I_mm4_mm": f["I_mm4_mm"],
                "od_m": f["od_max_m"]}
    for D_mm, f in CN.PE_M294_PERFIL_MINIMO.items()}

# Las cinco D-load de 0.3 mm de M 170M en N/m/mm. SON VALORES DE PRUEBA: solo
# la de la Clase II (50.0) esta leida del ejemplar; las otras cuatro NO se
# transcribieron y aqui solo sirven para ejercitar la logica de clases.
CINCO_CLASES_DE_PRUEBA = {"concreto_reforzado": {
    "I": 40.0, "II": 50.0, "III": 65.0, "IV": 100.0, "V": 140.0}}


@pytest.fixture
def del_expediente():
    """Retira el espesor sintetico de `conftest`: queda el del archivo."""
    ca.quitar_valor_dinamico(CLAVE_ESPESOR_PARED)
    yield


@pytest.fixture
def a01():
    return CP_A["punto_A01"]()


def _mat(tipo):
    return catalogo(tipo)


def _altura(punto, material, D):
    return M5.altura_relleno_sobre_clave(punto=punto, material=material,
                                        seccion=SeccionCircular(D))


def _con_relleno(punto, material, D, H_rel):
    """
    El punto con que se llama a M8 para un relleno `H_rel` distinto del
    suyo. M8 recibe la altura de relleno EXPLICITA y del punto solo lee el
    paquete (rasante menos subrasante), el id y, con nivel freatico, las
    cotas: sin NF el mismo punto sirve para cualquier relleno, y se devuelve
    tal cual. Se deja como funcion para que cada llamada diga con que
    relleno se esta probando.
    """
    assert punto.NF_profundidad_m is None
    return punto


def _por_codigo(resultado):
    return {v.codigo: v for v in resultado.verificaciones}


def _sust(verificacion_o_paso):
    paso = getattr(verificacion_o_paso, "paso", verificacion_o_paso)
    return {m.simbolo: m.valor for m in paso.sustitucion}


# ===========================================================================
# 1. F-H1 · Gobierna el vehiculo de mayor EFECTO
# ===========================================================================

def test_con_poco_relleno_y_luz_grande_gobierna_el_tandem_aunque_presione_menos(
        del_expediente, a01):
    """
    El dorado del auditor, rehecho a mano: concreto de 2.10 m con 0.47 m de
    relleno. El camion da 51.6 kPa sobre 1.27 m y el tandem 41.1 kPa sobre
    2.49 m: W_L = 65.5 contra 102.4 kN/m, y la D-load 30.7 contra 38.7
    N/m/mm. La FASE A elegia el camion (la mayor presion).
    """
    g = CP["efecto"]
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    punto = _con_relleno(a01, mat, g["D"], g["H_rel"])
    with declarados({"instalacion_estandar_concreto": "tipo_3"}):
        r = M8.verificar_concreto(punto=punto, material=mat,
                                  seccion=SeccionCircular(g["D"]),
                                  altura_relleno=g["H_rel"])
    (p_ll,) = [p for p in r.pasos if p.codigo == "F8.LL"]
    assert g["gobierna"] in p_ll.que and "por efecto" in p_ll.que
    v = _por_codigo(r)[M8.CODIGO_CLASE]
    assert v.valor_obtenido == pytest.approx(g["tandem"]["D_N_m_mm"], rel=REL)
    assert _sust(v)["W_L"] == pytest.approx(g["tandem"]["W_L_kN_m"], rel=REL)
    # ...y NO es la del camion, que es lo que salia.
    assert v.valor_obtenido != pytest.approx(g["camion"]["D_N_m_mm"], rel=REL_NO_ES)
    assert "tandem" in next(m for m in v.paso.sustitucion
                            if m.simbolo == "W_L").procedencia


def test_los_dos_vehiculos_del_dorado_son_los_calculados_a_mano():
    """
    Los dos candidatos, con su presion y su largo: el camion PRESIONA mas y
    el tandem CARGA mas. La eleccion sale del efecto que pasa el consumidor.
    """
    g = CP["efecto"]
    B_c = g["D"] + 2 * g["t"]
    cv = M8.carga_viva_enterrada(
        H=g["H_rel"] + g["e_paq"], D_i=g["D"], D_E=g["H_rel"],
        conducto=M8.CONDUCTO_TUBO_CONCRETO,
        efecto=lambda P_L, l_w: P_L * min(l_w, B_c),
        efecto_descripcion="W_L")
    por_nombre = {c[0]: c for c in cv.candidatos}
    for nombre in ("camion", "tandem"):
        _n, _P, l_w, _w, P_L, efecto = por_nombre[nombre]
        assert P_L == pytest.approx(g[nombre]["P_L_kPa"], rel=REL)
        assert l_w == pytest.approx(g[nombre]["l_w_m"], rel=REL)
        assert efecto == pytest.approx(g[nombre]["W_L_kN_m"], rel=REL)
    assert por_nombre["camion"][4] > por_nombre["tandem"][4]      # presion
    assert por_nombre["camion"][5] < por_nombre["tandem"][5]      # efecto
    assert cv.vehiculo == "tandem"
    assert cv.efecto == pytest.approx(g["tandem"]["W_L_kN_m"], rel=REL)
    # Con la PRESION como medida --la del marco, que la aplica a toda la
    # luz-- gobierna el camion: la medida la pone quien consume.
    por_presion = M8.carga_viva_enterrada(
        H=g["H_rel"] + g["e_paq"], D_i=g["D"], D_E=g["H_rel"],
        conducto=M8.CONDUCTO_TUBO_CONCRETO, efecto=lambda P_L, _l: P_L,
        efecto_descripcion="P_L")
    assert por_presion.vehiculo == "camion"


def test_en_A01_sigue_gobernando_el_camion_y_la_D_load_no_se_mueve(
        del_expediente, a01):
    """
    Con el tubo de 0.90 m el area cargada de los dos vehiculos es mas larga
    que el tubo (B_c = 1.10 m): el efecto ordena igual que la presion, y la
    D-load de la linea base (37.42 N/m/mm) no cambia con la correccion.
    """
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    r = M8.verificar_concreto(punto=a01, material=mat,
                              seccion=SeccionCircular(0.90),
                              altura_relleno=_altura(a01, mat, 0.90))
    (p_ll,) = [p for p in r.pasos if p.codigo == "F8.LL"]
    assert "camion" in p_ll.que
    assert _por_codigo(r)[M8.CODIGO_CLASE].valor_obtenido == pytest.approx(
        CP_A["concreto"]["D_req_N_m_mm"], rel=REL)
    # Las alturas del resultado: el relleno, el paquete y la SUMA de los dos
    # (la profundidad que distribuye la carga viva).
    assert r.H_relleno_m == pytest.approx(0.950, abs=ABS_ALTURA_M)
    assert r.e_paquete_m == pytest.approx(0.150, abs=ABS_ALTURA_M)
    assert r.H_total_m == pytest.approx(1.100, abs=ABS_ALTURA_M)


@pytest.mark.parametrize("H_rel", (0.40, 0.99))
def test_en_el_tmc_de_2_10_m_F1_y_el_vehiculo_son_los_calculados_a_mano(
        del_expediente, a01, H_rel):
    """
    El dorado a mano que el test de F_1 de la FASE A no tenia (reconstruia el
    empuje con la formula de M8): a 0.40 m gobierna el camion con F_1 =
    1.777; a 0.99 m, el tandem, que presiona menos sobre toda la luz.
    """
    g = CP["tmc_f1"]
    mat = _mat(TipoMaterial.TMC)
    with declarados({"fabricacion_tmc": "helicoidal"}):
        r = M8.verificar_tmc(punto=a01, material=mat,
                             seccion=SeccionCircular(g["D"]),
                             altura_relleno=H_rel)
    # La plancha que la progresion elige sube la clave unos milimetros: el
    # relleno con que se calculo es el del paso, y el dorado se hizo con el
    # nominal. Se comprueba que la diferencia es de milimetros y se compara
    # con la tolerancia que eso pide.
    (p_t,) = [p for p in r.pasos if p.codigo == "F8.T"]
    m = _sust(p_t)
    assert m["H_rel"] == pytest.approx(H_rel, abs=ABS_CRUCE_M)
    assert g[H_rel]["vehiculo"] in next(
        x for x in p_t.sustitucion if x.simbolo == "P_L").procedencia
    assert m["P_L"] == pytest.approx(g[H_rel]["P_L_kPa"], rel=REL_PLANCHA)
    assert m["C_L"] == pytest.approx(g[H_rel]["C_L_m"], rel=REL_PLANCHA)
    assert m["F_1"] == pytest.approx(g[H_rel]["F_1"], rel=REL_PLANCHA)
    assert m["P_L"] * m["C_L"] * m["F_1"] == pytest.approx(
        g[H_rel]["efecto_kN_m"], rel=REL_PLANCHA)
    # Y la carga viva, sola y con el relleno NOMINAL, al 0.1 %.
    cv = M8.carga_viva_enterrada(
        H=H_rel + 0.15, D_i=g["D"], D_E=H_rel, conducto=M8.CONDUCTO_FLEXIBLE,
        efecto=lambda P_L, l_w: P_L * min(l_w, g["D"]) * max(
            0.75 * g["D"] / l_w, 1.0),
        efecto_descripcion="P_L C_L F_1")
    assert cv.vehiculo == g[H_rel]["vehiculo"]
    assert cv.P_L_kPa == pytest.approx(g[H_rel]["P_L_kPa"], rel=REL)
    assert cv.efecto == pytest.approx(g[H_rel]["efecto_kN_m"], rel=REL)


def test_cada_consumidor_pasa_su_medida_del_efecto():
    """
    Por AST: las cuatro llamadas de produccion a `carga_viva_enterrada`
    (concreto, TMC, HDPE y marco) pasan `efecto=`. Sin eso volveria la
    eleccion por defecto para un conducto cuya carga no es P_L min(l_w, D_i).
    """
    arbol = ast.parse((RAIZ / "src/modulos/M8_estructural.py").read_text(
        encoding="utf-8"))
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.Call)
                and getattr(n.func, "id", "") == "carga_viva_enterrada"]
    assert len(llamadas) == 4
    for llamada in llamadas:
        assert "efecto" in {k.arg for k in llamada.keywords}, ast.unparse(llamada)


# ===========================================================================
# 2. F-H2 / O-H11 · La carga viva bajo relleno alto: conservar o declarar
# ===========================================================================

def test_la_carga_viva_pasados_8_ft_se_conserva_y_la_clase_II_deja_de_alcanzar(
        del_expediente, a01):
    """
    El dorado a mano: tubo de 0.90 m con 2.90 m de relleno. Conservando la
    carga viva la D-load es 50.59 > 50.0 y el concreto se detiene pidiendo la
    clase que falta; despreciandola (lo que hacia la FASE A, en silencio)
    daba 46.04 y «cumplia».
    """
    g = CP["conservar"]
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    punto = _con_relleno(a01, mat, g["D"], g["H_rel"])
    sec = SeccionCircular(g["D"])
    with declarados({"instalacion_estandar_concreto": "tipo_3"}):
        with pytest.raises(DatoFaltanteError) as exc:
            M8.verificar_concreto(punto=punto, material=mat, seccion=sec,
                                  altura_relleno=g["H_rel"])
        assert f"{g['D_conservando']:.1f} N/m/mm" in str(exc.value)
        with declarados({"carga_viva_bajo_relleno_alto":
                         "despreciar_3_6_1_2_6a"}):
            r = M8.verificar_concreto(punto=punto, material=mat, seccion=sec,
                                      altura_relleno=g["H_rel"])
    v = _por_codigo(r)[M8.CODIGO_CLASE]
    assert v.cumple
    assert v.valor_obtenido == pytest.approx(g["D_despreciando"], rel=REL)
    # Tomar el permiso SE AVISA en el punto, no solo en el paso.
    assert any("DESPRECIO" in a and "3.6.1.2.6a" in a for a in r.avisos)
    (p_ll,) = [p for p in r.pasos if p.codigo == "F8.LL"]
    assert "despreciada" in p_ll.que


def test_la_presion_conservada_a_esa_profundidad_es_la_calculada_a_mano():
    g = CP["conservar"]
    cv = M8.carga_viva_enterrada(
        H=g["H_rel"] + 0.15, D_i=g["D"], D_E=g["H_rel"],
        conducto=M8.CONDUCTO_TUBO_CONCRETO,
        efecto=lambda P_L, l_w: P_L * min(l_w, 1.10), efecto_descripcion="W_L")
    assert cv.en_zona_de_permiso and not cv.despreciada
    assert cv.vehiculo == g["vehiculo"]
    assert cv.P_L_kPa == pytest.approx(g["P_L_kPa"], rel=REL)
    assert cv.IM_pct == pytest.approx(0.0, abs=ABS_CERO)


def test_el_criterio_del_permiso_es_una_categoria_de_dos_valores_con_su_cita():
    c = ca.CRITERIOS["carga_viva_bajo_relleno_alto"]
    assert c.valor == "conservar" and c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_PERFIL and c.forma == ca.FORMA_CATEGORIA
    assert c.sensibilidad == ("conservar", "despreciar_3_6_1_2_6a")
    assert "may be neglected" in c.fuente
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("carga_viva_bajo_relleno_alto", "ignorar")
    reg = registro.construir()
    for cita_id in ("AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE",
                    "AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS"):
        assert reg.cita(cita_id).caracter.value == "permiso"
    assert M8.regla_de_la_carga_viva_bajo_relleno_alto() == M8.CARGA_VIVA_CONSERVAR


def test_el_relleno_maximo_del_concreto_ya_no_usa_el_permiso(del_expediente, a01):
    """
    3.18 m con la carga viva despreciada (FASE A) y ~2.85 m conservandola:
    el relleno maximo de A-01 es un cruce de la D-load CON carga viva.
    """
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(0.90)
    H = _altura(a01, mat, 0.90)
    conservando = M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                                        altura_relleno=H)
    with declarados({"carga_viva_bajo_relleno_alto": "despreciar_3_6_1_2_6a"}):
        despreciando = M8.verificar_concreto(punto=a01, material=mat,
                                             seccion=sec, altura_relleno=H)
    assert 2.80 < conservando.relleno_maximo_m < 2.90
    assert 3.15 < despreciando.relleno_maximo_m < 3.22
    # Es un CRUCE: 1 cm antes cumple; 1 cm despues pide otra clase.
    H_max = conservando.relleno_maximo_m
    antes = M8.verificar_concreto(
        punto=_con_relleno(a01, mat, 0.90, H_max - ABS_CRUCE_M), material=mat,
        seccion=sec, altura_relleno=H_max - ABS_CRUCE_M)
    v = _por_codigo(antes)[M8.CODIGO_CLASE]
    assert v.cumple
    assert v.valor_obtenido == pytest.approx(v.valor_admisible, abs=ABS_DLOAD_EN_EL_CRUCE)
    with pytest.raises(DatoFaltanteError):
        M8.verificar_concreto(
            punto=_con_relleno(a01, mat, 0.90, H_max + ABS_CRUCE_M),
            material=mat, seccion=sec, altura_relleno=H_max + ABS_CRUCE_M)


def test_en_un_marco_de_varias_celdas_el_permiso_mira_los_muros_extremos(a01):
    """
    3.6.1.2.6a: «for multiple span culverts ... the distance between inside
    faces of end walls». Marco de 2 celdas de 2.00 m con t = 0.15: 4.15 m.
    Con 3.00 m de relleno (mas de 8 ft y mas que UNA celda, menos que 4.15)
    el permiso no aplica; con una sola celda si.
    """
    decl = {"embocadura_cajon": "cajon_concreto_aletas_30_75",
            "n_manning_cajon": "concreto_afinado",
            "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
            "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50)),
            "espesor_pared_cajon": 0.15,
            "carga_viva_bajo_relleno_alto": "despreciar_3_6_1_2_6a"}
    sec = SeccionRectangular(B=2.00, H=1.50)
    vivas = {}
    for celdas in (1, 2):
        with declarados({**decl, "n_celdas_cajon": celdas}):
            marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                             forma=FormaSeccion.RECTANGULAR)
            vivas[celdas] = M8.demanda_marco(
                punto=a01, material=marco, seccion=sec,
                altura_relleno=2.85).w_viva_kPa
    assert vivas[1] == pytest.approx(0.0, abs=ABS_CERO)
    assert vivas[2] > 0


# ===========================================================================
# 3. O-H2 · La instalacion del concreto: tipo_4 en la ventana y al lado
# ===========================================================================

def test_el_tipo_4_se_puede_declarar_y_se_imprime_al_lado_como_contraste(
        del_expediente, a01):
    """
    Decision del dueño (2026-11-12): valor de archivo Tipo 3, `tipo_4` en la
    ventana y el Tipo 4 impreso al lado. En A-01: 44.85 N/m/mm (a mano) y el
    relleno maximo baja de ~2.85 a ~1.69 m.
    """
    g = CP["tipo_4"]
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(g["D"])
    H = _altura(a01, mat, g["D"])
    r3 = M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                               altura_relleno=H)
    por_codigo = {p.codigo: p for p in r3.pasos}
    p_t4 = por_codigo[M8.CODIGO_PASO_TIPO4]
    assert "NO RIGE" in p_t4.que
    assert p_t4.resultado.valor == pytest.approx(g["D_T4"], rel=REL)
    assert _sust(p_t4)["clase_T4"] == "Clase II"
    assert "AASHTO_LRFD_9.T12.10.2.1-1" in p_t4.citas_textuales
    H_max_T4 = por_codigo[M8.CODIGO_PASO_HMAX_TIPO4].resultado.valor
    assert 1.60 < H_max_T4 < 1.75 < r3.relleno_maximo_m
    # Y es exactamente lo que da DECLARAR el Tipo 4 (que ya no imprime
    # contraste: es el propio Tipo 4).
    with declarados({"instalacion_estandar_concreto": "tipo_4"}):
        r4 = M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                                   altura_relleno=H)
    assert _por_codigo(r4)[M8.CODIGO_CLASE].valor_obtenido == pytest.approx(
        g["D_T4"], rel=REL)
    assert r4.relleno_maximo_m == pytest.approx(H_max_T4, abs=ABS_ALTURA_M)
    assert M8.CODIGO_PASO_TIPO4 not in {p.codigo for p in r4.pasos}
    # El Tipo 4 no mueve la clase de A-01: sigue siendo la II.
    assert r4.seleccion == r3.seleccion == "Clase II"


def test_la_cita_de_la_tabla_de_instalaciones_separa_fuente_e_interpretacion():
    reg = registro.construir()
    tabla = reg.cita("AASHTO_LRFD_9.T12.10.2.1-1")
    assert tabla.interpretacion is not None
    assert "Tipo 3" in tabla.interpretacion.texto
    # Lo que la lectura tiene en contra esta dicho: la equivalencia entre
    # ensayos y el suelo mas plastico que el EG-2013 admite.
    en_contra = " ".join(tabla.interpretacion.en_contra)
    assert "27.5.2.2-3" in en_contra and "A-2-6" in en_contra
    assert reg.cita("EG2013.T205-01").texto_literal.texto == (
        "A-1-a, A-1-b, A-2-4, A-2-6 y A-3")


# ===========================================================================
# 4. O-H1 / F-H3 / O-H4 / O-H5 · El HDPE
# ===========================================================================

def test_sin_el_perfil_del_fabricante_el_hdpe_no_tiene_veredicto(
        del_expediente, a01):
    """
    «No verificado con un producto real»: `DatoFaltanteError` sobre
    'perfil_hdpe_fabricante', con la cota inferior del perfil minimo en el
    mensaje y en `exc.cota_inferior`, y la cita de C12.12.3.2.
    """
    mat = _mat(TipoMaterial.HDPE)
    H = _altura(a01, mat, 0.90)
    with pytest.raises(DatoFaltanteError) as exc:
        M8.verificar_hdpe(punto=a01, material=mat,
                          seccion=SeccionCircular(0.90), altura_relleno=H)
    assert exc.value.campo == M8.CRITERIO_PERFIL_HDPE == "perfil_hdpe_fabricante"
    mensaje = str(exc.value)
    assert M8.ROTULO_HDPE_SIN_PRODUCTO in mensaje
    assert "COTA INFERIOR" in mensaje and "not meaningful for design" in mensaje
    cota = exc.value.cota_inferior
    assert cota.cota_inferior
    assert [v.codigo for v in cota.verificaciones] == [
        M8.CODIGO_EMPUJE, M8.CODIGO_PANDEO, M8.CODIGO_DEFLEXION, M8.CODIGO_FF]
    assert any(M8.ROTULO_HDPE_SIN_PRODUCTO in a for a in cota.avisos)
    for v in cota.verificaciones:
        assert M8.ROTULO_HDPE_SIN_PRODUCTO.upper() in v.paso.nota_del_proyecto
    assert "AASHTO_LRFD_9.C12.12.3.2" in cota.verificaciones[0].paso.citas_textuales
    # Y `cota_inferior_hdpe` es la puerta para pedirla sin excepcion.
    directa = M8.cota_inferior_hdpe(punto=a01, material=mat,
                                    seccion=SeccionCircular(0.90),
                                    altura_relleno=H)
    assert [v.valor_obtenido for v in directa.verificaciones] == [
        v.valor_obtenido for v in cota.verificaciones]


def test_el_hdpe_con_el_relleno_de_archivo_cumple_con_los_numeros_a_mano(
        del_expediente, a01):
    """
    El dorado que la FASE A no tenia: un HDPE que CUMPLE (Si-95, el relleno
    granular de archivo; perfil minimo de 36 in declarado como del
    fabricante). Fija el umbral de la deflexion, el pandeo por las dos
    lecturas y el factor de flexibilidad.
    """
    g = CP["hdpe_si95"]
    assert ca.CRITERIOS["relleno_estructural_hdpe"].valor == "Si-95"
    mat = _mat(TipoMaterial.HDPE)
    H = _altura(a01, mat, 0.90)
    with declarados({"perfil_hdpe_fabricante": PERFIL_DECLARADO}):
        r = M8.verificar_hdpe(punto=a01, material=mat,
                              seccion=SeccionCircular(0.90), altura_relleno=H)
    assert not r.cota_inferior
    assert r.seleccion == "perfil declarado del fabricante, 900 mm"
    assert not any(M8.ROTULO_HDPE_SIN_PRODUCTO in a for a in r.avisos)
    v = _por_codigo(r)
    assert all(x.cumple for x in r.verificaciones)
    assert v[M8.CODIGO_EMPUJE].valor_obtenido == pytest.approx(g["eps_uc"], rel=REL)
    pandeo = _sust(v[M8.CODIGO_PANDEO])
    assert pandeo["u_duracion"] == pytest.approx(g["u_duracion"], rel=REL)
    assert pandeo["u_letra"] == pytest.approx(g["u_letra"], rel=REL)
    # Rige la MAYOR: aqui la suma por duracion; con Cl-95, la letra.
    assert v[M8.CODIGO_PANDEO].valor_obtenido == pytest.approx(
        g["u_duracion"], rel=REL)
    assert "AASHTO_LRFD_9.12.12.3.3#PANDEO" in \
        v[M8.CODIGO_PANDEO].paso.citas_textuales
    assert v[M8.CODIGO_DEFLEXION].valor_obtenido == pytest.approx(
        g["Delta_m"], rel=REL)
    # EL UMBRAL DE LA DEFLEXION: 5 % del diametro, 0.045 m (mutante vivo).
    assert v[M8.CODIGO_DEFLEXION].valor_admisible == pytest.approx(
        0.05 * 0.90, rel=REL_TRANSPORTE)
    assert v[M8.CODIGO_FF].valor_obtenido == pytest.approx(g["FF_mm_N"], rel=REL)
    assert v[M8.CODIGO_FF].valor_admisible == pytest.approx(
        g["FF_lim_mm_N"], rel=REL)
    assert v[M8.CODIGO_FF].paso.fundamento_id == "F8.HDPE_FF"
    assert v[M8.CODIGO_FF].paso.umbral.cita_id == "AASHTO_LRFD_9.12.5.6.3"
    # El relleno granular de 508.02 d) esta citado en el paso del empuje.
    assert "EG2013.508.02#GRANULAR" in v[M8.CODIGO_EMPUJE].paso.citas_textuales
    # Los margenes: con signo y con valor.
    for x in r.verificaciones:
        assert x.paso.veredicto.margen == pytest.approx(
            x.valor_admisible - x.valor_obtenido, rel=REL_TRANSPORTE)
        assert x.paso.veredicto.margen > 0


def test_el_relleno_maximo_del_hdpe_es_el_primer_cruce(del_expediente, a01):
    """
    A mano: a 1.40 m eps_uc = 0.0400 (cumple) y a 1.60 m 0.0426 (no). El
    relleno maximo cae entre los dos, y ES un cruce del empuje.
    """
    g = CP["hdpe_si95"]
    mat = _mat(TipoMaterial.HDPE)
    sec = SeccionCircular(0.90)
    with declarados({"perfil_hdpe_fabricante": PERFIL_DECLARADO}):
        r = M8.verificar_hdpe(punto=a01, material=mat, seccion=sec,
                              altura_relleno=_altura(a01, mat, 0.90))
        H_max = r.relleno_maximo_m
        assert g["H_max_entre"][0] < H_max < g["H_max_entre"][1]
        (p_h,) = [p for p in r.pasos if p.codigo == "F8.HMAX"]
        assert p_h.resultado.valor == H_max
        antes, despues = (
            M8.verificar_hdpe(punto=_con_relleno(a01, mat, 0.90, H),
                              material=mat, seccion=sec, altura_relleno=H)
            for H in (H_max - ABS_CRUCE_M, H_max + ABS_CRUCE_M))
    assert all(v.cumple for v in antes.verificaciones)
    assert antes.relleno_maximo_m == pytest.approx(H_max, abs=ABS_ALTURA_M)
    assert not _por_codigo(despues)[M8.CODIGO_EMPUJE].cumple
    assert despues.relleno_maximo_m is None and despues.seleccion == ""


@pytest.mark.parametrize("D", (0.90, 1.05, 1.20))
def test_con_arcilla_y_el_perfil_minimo_el_hdpe_no_cumple_a_ninguna_altura(
        del_expediente, a01, D):
    """
    Lo que la FASE A tenia por defecto y no decia (F-H3, O-H1): con Cl-95 y
    el perfil minimo el HDPE de 900 a 1200 mm no cumple a NINGUN relleno.
    Queda fijado, y dicho en la ficha del criterio, para que se vea el dia
    que cambie.
    """
    mat = _mat(TipoMaterial.HDPE)
    sec = SeccionCircular(D)
    alturas = (0.35, 0.5, 0.65, 0.8, 1.0, 1.5, 2.5, 3.5, 5.0, 10.0)
    with declarados({"relleno_estructural_hdpe": "Cl-95"}):
        for H in alturas:
            cota = M8.cota_inferior_hdpe(
                punto=_con_relleno(a01, mat, D, H), material=mat, seccion=sec,
                altura_relleno=H)
            assert not cota.cumple, (D, H)
            assert cota.relleno_maximo_m is None
    assert "no cumple a ninguna altura" in \
        ca.CRITERIOS["relleno_estructural_hdpe"].justificacion


def test_el_relleno_de_archivo_del_hdpe_es_granular_y_cita_el_508_02():
    c = ca.CRITERIOS["relleno_estructural_hdpe"]
    assert c.valor == "Si-95" and "Cl-95" in c.sensibilidad
    assert "EG2013.508.02#GRANULAR" in c.fuente
    reg = registro.construir()
    cita = reg.cita("EG2013.508.02#GRANULAR")
    assert cita.caracter.value == "exigencia"
    assert "material granular" in cita.texto_literal.texto
    assert cita.interpretacion is not None       # Sn/Si es lectura del proyecto
    assert "aproximadas" in " ".join(cita.interpretacion.en_contra)


def test_el_factor_de_flexibilidad_usa_el_modulo_inicial_tambien_con_la_llamada(
        del_expediente, a01):
    """
    42 in lleva la llamada «*» de la Tabla A12-11 (la carga viva con el
    modulo de largo plazo), pero el FF es de 12.12.3.6: modulo INICIAL.
    FF = (1.2192 m)^2 / (110 ksi * 8898.18 mm4/mm) = 0.2203 mm/N.
    """
    mat = _mat(TipoMaterial.HDPE)
    cota = M8.cota_inferior_hdpe(punto=a01, material=mat,
                                 seccion=SeccionCircular(1.05),
                                 altura_relleno=_altura(a01, mat, 1.05))
    ff = _por_codigo(cota)[M8.CODIGO_FF]
    E_ini_MPa = 110.0 * 6.894757
    assert ff.valor_obtenido == pytest.approx(
        1219.2 ** 2 / (E_ini_MPa * 8898.175752), rel=REL)
    assert _sust(ff)["E"] == pytest.approx(E_ini_MPa, rel=REL)
    assert CN.FF_LIMITE_TERMOPLASTICO_MM_N == pytest.approx(
        95.0 * 25.4 / 4448.2216, rel=REL)


def test_un_perfil_declarado_por_debajo_del_minimo_es_dato_invalido(
        del_expediente, a01):
    mat = _mat(TipoMaterial.HDPE)
    bueno = PERFIL_DECLARADO["900"]
    for malo in ({**bueno, "A_mm2_mm": bueno["A_mm2_mm"] * 0.9},
                 {**bueno, "I_mm4_mm": bueno["I_mm4_mm"] * 0.9},
                 {**bueno, "od_m": bueno["od_m"] + 0.05},
                 {**bueno, "od_m": 0.80},
                 {"A_mm2_mm": bueno["A_mm2_mm"], "I_mm4_mm": bueno["I_mm4_mm"]},
                 {**bueno, "A_mm2_mm": -1.0},
                 {**bueno, "I_mm4_mm": "3638"}):
        with declarados({"perfil_hdpe_fabricante": {"900": malo}}):
            with pytest.raises(DatoInvalidoError) as exc:
                M8.perfil_declarado_hdpe(0.90, a01.id)
            assert exc.value.campo == "perfil_hdpe_fabricante"
    # Un NaN no llega: lo rechaza la puerta de declaracion (EXT-5).
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(
            "perfil_hdpe_fabricante",
            {"900": {**bueno, "A_mm2_mm": float("nan")}})
    # Un diametro que la declaracion no trae sigue sin dato.
    with declarados({"perfil_hdpe_fabricante": {"1050": PERFIL_DECLARADO["1050"]}}):
        assert M8.perfil_declarado_hdpe(0.90, a01.id) is None
        assert M8.perfil_declarado_hdpe(1.05, a01.id)["A_mm2_mm"] == \
            PERFIL_DECLARADO["1050"]["A_mm2_mm"]
        with pytest.raises(DatoFaltanteError):
            M8.verificar_hdpe(punto=a01, material=mat,
                              seccion=SeccionCircular(0.90),
                              altura_relleno=_altura(a01, mat, 0.90))


def test_un_perfil_del_fabricante_mejor_que_el_minimo_mejora_el_resultado(
        del_expediente, a01):
    mat = _mat(TipoMaterial.HDPE)
    sec = SeccionCircular(0.90)
    H = _altura(a01, mat, 0.90)
    minimo = PERFIL_DECLARADO["900"]
    mejor = {"A_mm2_mm": minimo["A_mm2_mm"] * 1.3,
             "I_mm4_mm": minimo["I_mm4_mm"] * 1.5, "od_m": minimo["od_m"]}
    resultados = {}
    for nombre, perfil in (("minimo", minimo), ("mejor", mejor)):
        with declarados({"perfil_hdpe_fabricante": {"900": perfil}}):
            resultados[nombre] = M8.verificar_hdpe(
                punto=a01, material=mat, seccion=sec, altura_relleno=H)
    a, b = (_por_codigo(resultados[n]) for n in ("minimo", "mejor"))
    assert b[M8.CODIGO_EMPUJE].valor_obtenido < a[M8.CODIGO_EMPUJE].valor_obtenido
    assert b[M8.CODIGO_FF].valor_obtenido < a[M8.CODIGO_FF].valor_obtenido
    assert resultados["mejor"].relleno_maximo_m > resultados["minimo"].relleno_maximo_m


# ===========================================================================
# 5. F-H4 / O-H3 · La costura del TMC
# ===========================================================================

def test_la_fabricacion_de_archivo_es_la_costura_mas_debil_tabulada_y_lo_avisa(
        del_expediente, a01):
    c = ca.CRITERIOS["fabricacion_tmc"]
    assert c.valor == "anular_remachada_simple"
    assert "EMPERNADA" in c.justificacion
    assert "sin fijar la fabricacion" not in c.justificacion
    mat = _mat(TipoMaterial.TMC)
    r = M8.verificar_tmc(punto=a01, material=mat, seccion=SeccionCircular(0.90),
                         altura_relleno=_altura(a01, mat, 0.90))
    costura = _por_codigo(r)[M8.CODIGO_COSTURA]
    assert costura.cumple
    # Cumple, y dice que la resistencia es la de OTRA fabricacion.
    assert any("EG-2013 507.02 a)" in a and "OTRA fabricacion" in a
               for a in r.avisos)
    assert "OTRA fabricacion" in costura.paso.nota_del_proyecto
    assert "EG2013.507.02#EMPERNADA" in costura.paso.citas_textuales
    reg = registro.construir()
    assert reg.cita("EG2013.507.02#EMPERNADA").interpretacion is not None
    # La tabla, releida valor a valor en el cierre (ASTM A796 Tabla 5).
    simple = {c: f["simple"] for c, f in CN.COSTURA_REMACHADA_TMC_KN_M.items()
              if c.startswith("68x13/") and f["simple"] is not None}
    assert simple == pytest.approx({"68x13/1.63": 244.0, "68x13/2.01": 266.0,
                                    "68x13/2.77": 341.0, "68x13/3.51": 357.0,
                                    "68x13/4.27": 374.0}, rel=REL_TRANSPORTE)


def test_una_plancha_mas_gruesa_sube_la_clave_y_baja_el_relleno(
        del_expediente, a01):
    """
    TMC de 1.20 m: el EG-2013 lleva la plancha de 2.01 a 2.77 mm, la
    envolvente crece 0.76 mm y la clave SUBE: el relleno con que se verifica
    es 0.76 mm MENOR que el de la plancha adoptada (mutante vivo: `+`).
    """
    mat = _mat(TipoMaterial.TMC)
    H = _altura(a01, mat, 1.20)
    r = M8.verificar_tmc(punto=a01, material=mat, seccion=SeccionCircular(1.20),
                         altura_relleno=H)
    assert r.seleccion == "68x13/2.77"
    (p_t,) = [p for p in r.pasos if p.codigo == "F8.T"]
    assert _sust(p_t)["H_rel"] == pytest.approx(H - 0.00076, abs=ABS_PLANCHA_M)
    assert r.H_relleno_m == pytest.approx(H - 0.00076, abs=ABS_PLANCHA_M)


def test_el_contraste_asd_dice_que_no_es_a796_puro(del_expediente, a01):
    mat = _mat(TipoMaterial.TMC)
    r = M8.verificar_tmc(punto=a01, material=mat, seccion=SeccionCircular(0.90),
                         altura_relleno=_altura(a01, mat, 0.90))
    (p_asd,) = [p for p in r.pasos if p.codigo == "F8.ASD"]
    assert "NO ES «A796 PURO»" in p_asd.nota_del_proyecto
    assert "presencia multiple" in p_asd.nota_del_proyecto
    # La suma del contraste: P_sp + P_L (mutante vivo: `-`).
    sust = _sust(p_asd)
    (p_t,) = [p for p in r.pasos if p.codigo == "F8.T"]
    carga = _sust(p_t)
    assert sust["EL+LL"] == pytest.approx(carga["P_sp"] + carga["P_L"],
                                          rel=REL_TRANSPORTE)
    assert sust["T"] == pytest.approx(sust["EL+LL"] * 0.90 / 2, rel=REL_TRANSPORTE)


def test_el_paso_del_empuje_del_tmc_declara_la_lectura_sin_k_gamma_e(
        del_expediente, a01):
    """La sospecha de la auditoria: es la lectura de la menor demanda y la
    letra no la dice. Queda declarada en el paso, con su razon."""
    mat = _mat(TipoMaterial.TMC)
    r = M8.verificar_tmc(punto=a01, material=mat, seccion=SeccionCircular(0.90),
                         altura_relleno=_altura(a01, mat, 0.90))
    (p_t,) = [p for p in r.pasos if p.codigo == "F8.T"]
    assert "MENOR DEMANDA" in p_t.nota_del_proyecto
    assert "K_gammaE" in p_t.nota_del_proyecto


# ===========================================================================
# 6. F-H5 / O-H6 / O-H7 · Las clases de M 170M
# ===========================================================================

def test_la_clase_I_no_se_ofrece_por_debajo_de_1500_mm(del_expediente, a01):
    """
    Completar el criterio con la Clase I hacia que un tubo de 0.90 m saliera
    «Clase I», que M 170M no tabula por debajo de 1500 mm.
    """
    assert CN.DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM == {
        "I": 1500, "II": 300, "III": 300, "IV": 300, "V": 300}
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    with declarados({"clases_producto_por_relleno": CINCO_CLASES_DE_PRUEBA}):
        ofrecidas, faltan = M8.clases_de_concreto_para(0.90)
        assert list(ofrecidas) == ["II", "III", "IV", "V"] and faltan == ()
        assert list(M8.clases_de_concreto_para(1.50)[0]) == [
            "I", "II", "III", "IV", "V"]
        r = M8.verificar_concreto(
            punto=_con_relleno(a01, mat, 0.90, 1.0), material=mat,
            seccion=SeccionCircular(0.90), altura_relleno=1.0)
        assert r.seleccion == "Clase II"          # 38.0 < 40: y aun asi no la I
        assert _por_codigo(r)[M8.CODIGO_CLASE].valor_obtenido < 40.0
        r = M8.verificar_concreto(
            punto=_con_relleno(a01, mat, 1.50, 1.0), material=mat,
            seccion=SeccionCircular(1.50), altura_relleno=1.0)
        assert _por_codigo(r)[M8.CODIGO_CLASE].valor_obtenido < 40.0
        assert r.seleccion == "Clase I"


def test_con_las_cinco_clases_un_tubo_que_no_alcanza_no_cumple_y_no_falta_dato(
        del_expediente, a01):
    """
    Con las cinco declaradas ya no falta ningun dato: el tubo NO CUMPLE
    frente a la Clase V (la FASE A levantaba `DatoFaltanteError` con un
    mensaje falso, y `F8.CLASE` no podia salir `False`).
    """
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    with declarados({"clases_producto_por_relleno": CINCO_CLASES_DE_PRUEBA}):
        r = M8.verificar_concreto(
            punto=_con_relleno(a01, mat, 0.90, 30.0), material=mat,
            seccion=SeccionCircular(0.90), altura_relleno=30.0)
    v = _por_codigo(r)[M8.CODIGO_CLASE]
    assert not v.cumple and v.valor_admisible == pytest.approx(
        140.0, rel=REL_TRANSPORTE)
    assert "Clase V" in v.paso.que
    assert v.paso.veredicto.margen < 0
    assert r.seleccion == "" and r.relleno_maximo_m is None
    assert M8.DIFERIDO_CLASES_M170M not in r.diferido


def test_el_bloqueo_del_concreto_dice_exactamente_que_falta(del_expediente, a01):
    """
    Decision del dueño: BLOQUEAR. El mensaje nombra las clases que la norma
    tabula para ESE diametro y no estan transcritas, y lo que lo destraba.
    """
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    with pytest.raises(DatoFaltanteError) as exc:
        M8.verificar_concreto(
            punto=_con_relleno(a01, mat, 1.50, 5.0), material=mat,
            seccion=SeccionCircular(1.50), altura_relleno=5.0)
    mensaje = str(exc.value)
    assert exc.value.campo == "clases_producto_por_relleno"
    # En 1.50 m la Clase I SI se tabula, pero es INFERIOR a la II transcrita:
    # las que faltan son las superiores.
    assert "Clases III, IV, V" in mensaje
    assert "AASHTO M 170M" in mensaje and "ASTM C76M" in mensaje
    assert "docs/contrato_entradas.md" in mensaje
    contrato = (RAIZ / "docs/contrato_entradas.md").read_text(encoding="utf-8")
    assert "M 170M" in contrato and "clases_producto_por_relleno" in contrato
    assert "perfil_hdpe_fabricante" in contrato


def test_subir_de_diametro_SI_puede_bajar_la_D_load_con_relleno_somero(
        del_expediente, a01):
    """
    El docstring de la FASE A decia «subir de diametro no la baja» y es
    falso con relleno somero (contraejemplo del auditor: 52.2, 41.7 y 36.0
    N/m/mm en 0.90, 1.20 y 1.50 m con 0.50 m de relleno). El bloqueo se
    sostiene por decision, no por una monotonia que no existe.
    """
    mat = _mat(TipoMaterial.CONCRETO_REFORZADO)
    D_loads = {}
    with declarados({"clases_producto_por_relleno": CINCO_CLASES_DE_PRUEBA}):
        for D in (0.90, 1.20, 1.50):
            r = M8.verificar_concreto(
                punto=_con_relleno(a01, mat, D, 0.50), material=mat,
                seccion=SeccionCircular(D), altura_relleno=0.50)
            D_loads[D] = _por_codigo(r)[M8.CODIGO_CLASE].valor_obtenido
    assert D_loads[0.90] > 50.0 > D_loads[1.20] > D_loads[1.50]
    assert "subir de diametro no la baja (W crece" not in \
        M8.verificar_concreto.__doc__.replace("\n", " ").replace("  ", " ") \
        .split("(La version")[0]


@pytest.mark.parametrize("tabla", (
    {"concreto_reforzado": {"II": 50.0, "VI": 200.0}},
    {"concreto_reforzado": {"II": "50"}},
    {"concreto_reforzado": {"II": -50.0}},
))
def test_una_tabla_de_clases_rara_es_dato_invalido(tabla):
    with declarados({"clases_producto_por_relleno": tabla}):
        with pytest.raises(DatoInvalidoError) as exc:
            M8._clases_transcritas()
    assert exc.value.campo == "clases_producto_por_relleno"


# ===========================================================================
# 7. F-H6 / O-H8 · Lo que la mutacion dejo vivo
# ===========================================================================

def test_la_rama_elastica_del_pandeo_del_tmc_a_mano():
    g = CP["pandeo_elastico"]
    E, F_u, k = CN.ACERO_TMC_EM_MPA, CN.ACERO_TMC_FU_MPA, CN.K_RIGIDEZ_SUELO_TMC
    umbral = (g["r_mm"] / k) * math.sqrt(24 * E / F_u)
    assert umbral == pytest.approx(g["S_umbral_mm"], rel=REL)
    f_cr = M8.tension_critica_de_pandeo(S_mm=g["S_mm"], r_mm=g["r_mm"], E=E,
                                        F_u=F_u, k=k)
    assert f_cr == pytest.approx(g["f_cr_MPa"], rel=REL)
    # Las dos ramas empalman en el umbral (F_u/2) y la elastica decrece.
    justo_antes = M8.tension_critica_de_pandeo(
        S_mm=umbral * (1 - 1e-9), r_mm=g["r_mm"], E=E, F_u=F_u, k=k)
    justo_despues = M8.tension_critica_de_pandeo(
        S_mm=umbral * (1 + 1e-9), r_mm=g["r_mm"], E=E, F_u=F_u, k=k)
    assert justo_antes == pytest.approx(F_u / 2, rel=REL_EMPALME)
    assert justo_despues == pytest.approx(F_u / 2, rel=REL_EMPALME)
    assert M8.tension_critica_de_pandeo(S_mm=2 * g["S_mm"], r_mm=g["r_mm"],
                                        E=E, F_u=F_u, k=k) == pytest.approx(
        f_cr / 4, rel=REL_TRANSPORTE)
    # EL UMBRAL ES 24 Y NO OTRO: un 2 % por encima rige ya la rama elastica,
    # F_u/2/1.02^2 = 149.11 MPa; la inelastica daria 148.87 (0.16 % menos).
    un_poco_despues = M8.tension_critica_de_pandeo(
        S_mm=umbral * 1.02, r_mm=g["r_mm"], E=E, F_u=F_u, k=k)
    assert un_poco_despues == pytest.approx(F_u / 2 / 1.02 ** 2, rel=REL_FINA)
    assert un_poco_despues == pytest.approx(149.11, rel=REL_FINA)


def test_el_relleno_maximo_del_tmc_helicoidal_lo_agota_el_area(
        del_expediente, a01):
    """
    Helicoidal: no hay costura, gobierna el area. En el relleno maximo el
    empuje iguala phi A min(F_y, f_cr) = 1.0 * 2.049 mm2/mm * 227.53 MPa =
    466.2 kN/m, y es un cruce.
    """
    mat = _mat(TipoMaterial.TMC)
    sec = SeccionCircular(0.90)
    with declarados({"fabricacion_tmc": "helicoidal"}):
        r = M8.verificar_tmc(punto=a01, material=mat, seccion=sec,
                             altura_relleno=_altura(a01, mat, 0.90))
        H_max = r.relleno_maximo_m
        assert r.seleccion == "68x13/2.01" and H_max is not None
        (p_h,) = [p for p in r.pasos if p.codigo == "F8.HMAX"]
        resistencia = 2.049 * 1.00 * CN.ACERO_TMC_FY_MPA
        assert _sust(p_h)["phi A f"] == pytest.approx(resistencia, rel=REL)
        assert resistencia == pytest.approx(466.2, rel=REL)
        antes, despues = (
            M8.verificar_tmc(punto=_con_relleno(a01, mat, 0.90, H),
                             material=replace(mat), seccion=sec,
                             altura_relleno=H)
            for H in (H_max - ABS_CRUCE_M, H_max + ABS_CRUCE_M))
    (p_t,) = [p for p in antes.pasos if p.codigo == "F8.T"]
    assert p_t.resultado.valor == pytest.approx(resistencia, rel=REL_EN_EL_CRUCE)
    assert antes.seleccion == "68x13/2.01"
    # 1 cm despues la plancha de 2.01 ya no alcanza: la progresion sube.
    assert despues.seleccion != "68x13/2.01"
    # A mano: T ~ eta gamma_EV gamma_s H S/2 -> H ~ 466.2/(1.05*1.95*18.85*0.45)
    assert H_max == pytest.approx(466.2 / (1.05 * 1.95 * 18.85 * 0.45), rel=REL_ESTIMA)


def test_el_relleno_maximo_del_tmc_remachado_lo_agota_la_costura(
        del_expediente, a01):
    """Con costura remachada simple la plancha de 2.01 se agota por
    phi_s SS = 0.67 * 266 = 178.2 kN/m, antes que por el area (466.2)."""
    mat = _mat(TipoMaterial.TMC)
    sec = SeccionCircular(0.90)
    r = M8.verificar_tmc(punto=a01, material=mat, seccion=sec,
                         altura_relleno=_altura(a01, mat, 0.90))
    with declarados({"fabricacion_tmc": "helicoidal"}):
        helicoidal = M8.verificar_tmc(punto=a01, material=mat, seccion=sec,
                                      altura_relleno=_altura(a01, mat, 0.90))
    assert r.relleno_maximo_m < helicoidal.relleno_maximo_m
    antes = M8.verificar_tmc(
        punto=_con_relleno(a01, mat, 0.90, r.relleno_maximo_m - ABS_CRUCE_M),
        material=mat, seccion=sec,
        altura_relleno=r.relleno_maximo_m - ABS_CRUCE_M)
    costura = _por_codigo(antes)[M8.CODIGO_COSTURA]
    assert costura.valor_admisible == pytest.approx(0.67 * 266.0, rel=REL)
    assert costura.valor_obtenido == pytest.approx(0.67 * 266.0, rel=REL_EN_EL_CRUCE)
    assert costura.paso.veredicto.margen == pytest.approx(
        costura.valor_admisible - costura.valor_obtenido, rel=REL_TRANSPORTE)


def test_el_primer_cruce_no_se_le_escapa_a_un_muestreo_roto():
    """
    Un hundimiento ESTRECHO del margen (5 cm) seguido de un tramo largo
    positivo: un Brent sobre el intervalo entero --lo que harian los
    mutantes `(H_techo - H_rel) * TRAMOS` o `i / tramo`-- encuentra el cruce
    de 5.0 m; el muestreo en tramos, el de 1.00 m. El test anterior usaba un
    hundimiento de 1 m, que cualquier busqueda encontraba.
    """
    def margen(H):
        if H < 1.00:
            return 1.0
        if H < 1.05:
            return -1.0
        return 5.0 - H

    assert M8._relleno_maximo(margen, 0.5, 0.90) == pytest.approx(
        1.00, abs=ABS_ALTURA_M)
    # El mismo hundimiento mas lejos del arranque y con otro diametro.
    def margen_2(H):
        return 1.0 if H < 3.00 else (-1.0 if H < 3.05 else 9.0 - H)

    assert M8._relleno_maximo(margen_2, 0.95, 1.50) == pytest.approx(
        3.00, abs=ABS_ALTURA_M)


def test_el_nivel_freatico_sobre_la_clave_sube_el_empuje_lo_calculado_a_mano(
        del_expediente, a01):
    """
    La rama de `NF_profundidad_m`, que ningun test tocaba: con el agua 0.685
    m mas alta sobre el arranque el empuje del TMC sube 3.175 kN/m, y la
    deformacion permanente del HDPE 0.005902.
    """
    g = CP["nf"]
    con_nf = replace(a01, cota_terreno=g["cota_terreno"],
                     NF_profundidad_m=g["NF"], cota_fondo_entrada=a01.cota_terreno)
    sec = SeccionCircular(0.90)
    tmc = _mat(TipoMaterial.TMC)
    H = CP_A["H_relleno"]["tmc"]
    seco = M8.verificar_tmc(punto=a01, material=tmc, seccion=sec, altura_relleno=H)
    mojado = M8.verificar_tmc(punto=con_nf, material=tmc, seccion=sec,
                              altura_relleno=H)
    T = {n: next(p for p in r.pasos if p.codigo == "F8.T").resultado.valor
         for n, r in (("seco", seco), ("mojado", mojado))}
    assert T["mojado"] - T["seco"] == pytest.approx(g["delta_T_tmc_kN_m"], rel=REL)
    # Un NF por DEBAJO de la clave no cambia nada: rige el agua hasta la clave.
    bajo = replace(a01, NF_profundidad_m=1.0)
    assert next(p for p in M8.verificar_tmc(
        punto=bajo, material=tmc, seccion=sec, altura_relleno=H).pasos
        if p.codigo == "F8.T").resultado.valor == pytest.approx(
        T["seco"], rel=REL_TRANSPORTE)
    hdpe = _mat(TipoMaterial.HDPE)
    H = CP_A["H_relleno"]["hdpe"]
    eps = {}
    for nombre, punto in (("seco", a01), ("mojado", con_nf)):
        cota = M8.cota_inferior_hdpe(punto=punto, material=hdpe, seccion=sec,
                                     altura_relleno=H)
        s = _sust(_por_codigo(cota)[M8.CODIGO_EMPUJE])
        eps[nombre] = s["T_d"] / (s["A_eff,lp"] / 1000 * 21.0 * 6894.757)
    assert eps["mojado"] - eps["seco"] == pytest.approx(
        g["delta_eps_d_hdpe"], rel=REL)


# ===========================================================================
# 8. F-H7 · El caracter del umbral se lee de la cita
# ===========================================================================

def test_el_caracter_de_cada_umbral_de_la_fase_8_es_el_de_su_cita(
        del_expediente, a01):
    """
    `_campos_f8` escribia "EXIGENCIA" a mano para todas, tambien para el 5 %
    de la deflexion del HDPE, que es la recomendacion de un comentario.
    """
    reg = registro.construir()
    pasos = []
    for tipo in (TipoMaterial.CONCRETO_REFORZADO, TipoMaterial.TMC):
        mat = _mat(tipo)
        r = M8.verificar_conducto(punto=a01, material=mat,
                                  seccion=SeccionCircular(0.90),
                                  altura_relleno=_altura(a01, mat, 0.90))
        pasos += [v.paso for v in r.verificaciones if v.paso is not None]
    hdpe = _mat(TipoMaterial.HDPE)
    pasos += [v.paso for v in M8.cota_inferior_hdpe(
        punto=a01, material=hdpe, seccion=SeccionCircular(0.90),
        altura_relleno=_altura(a01, hdpe, 0.90)).verificaciones]
    assert len(pasos) == 8
    for p in pasos:
        assert p.umbral.caracter == reg.cita(p.umbral.cita_id).caracter.value.upper(), p.codigo
    deflexion = next(p for p in pasos if p.codigo == M8.CODIGO_DEFLEXION)
    assert deflexion.umbral.cita_id == "AASHTO_LRFD_9.C12.12.2.2"
    assert deflexion.umbral.caracter == "RECOMENDACION"
    assert {p.umbral.caracter for p in pasos if p is not deflexion} == {"EXIGENCIA"}
    # Por AST: ninguna llamada de M8 pasa `caracter=` con un texto escrito.
    arbol = ast.parse((RAIZ / "src/modulos/M8_estructural.py").read_text(
        encoding="utf-8"))
    escritos = [ast.unparse(k.value) for n in ast.walk(arbol)
                if isinstance(n, ast.Call) for k in n.keywords
                if k.arg == "caracter" and isinstance(k.value, ast.Constant)]
    assert escritos == []


# ===========================================================================
# 9. F-H8 / O-H13 · El nivel de los criterios, medido
# ===========================================================================

def _correr_ancho(declaraciones):
    externos = cli.cargar_datos_externos(EXTERNOS, {
        "luz_m": 2.75, "TW_m": None, "longitud_m": None,
        "L_hidraulico_m": None, "categoria_tr": None})
    with declarados(declaraciones):
        return cli.correr(CSV, externos, alcance=cli.ALCANCE_PERFIL)


def _punto(informe, id_):
    return next(p for p in informe.puntos if p.punto.id == id_)


# El concreto y el TMC fuera del catalogo (un tope de disponibilidad por
# debajo del primer diametro): es la forma de que una corrida de PERFIL del
# fixture llegue a la Fase 8 del TMC y a la del HDPE.
SIN_CONCRETO = {"D_max_catalogo": {"concreto_reforzado": 0.75}}
SIN_CONCRETO_NI_TMC = {"D_max_catalogo": {"concreto_reforzado": 0.75,
                                           "tmc": 0.75}}


def test_la_corrida_de_perfil_que_llega_al_tmc_y_al_hdpe_invoca_sus_criterios(
        del_expediente):
    """
    La MEDIDA del nivel de los cinco criterios que la corrida de referencia
    no alcanza (el comentario de `criterios_adoptados` decia «medido en
    test_nivel_medido» de los cinco y solo era cierto de uno).
    """
    nuevos = {"instalacion_estandar_concreto", "fabricacion_tmc",
              "eta_importancia_operativa_conducto", "relleno_estructural_hdpe",
              "parametros_diseno_hdpe", "carga_viva_bajo_relleno_alto",
              "perfil_hdpe_fabricante"}
    for clave in nuevos:
        assert ca.CRITERIOS[clave].nivel == ca.NIVEL_PERFIL, clave
    referencia = _correr_ancho({})
    assert set(referencia.contexto.criterios_usados) & nuevos == {
        "instalacion_estandar_concreto", "carga_viva_bajo_relleno_alto"}
    con_tmc = _correr_ancho(SIN_CONCRETO)
    assert _punto(con_tmc, "A-02").resultado.material.tipo is TipoMaterial.TMC
    assert {"fabricacion_tmc", "eta_importancia_operativa_conducto"} <= set(
        con_tmc.contexto.criterios_usados)
    con_hdpe = _correr_ancho({**SIN_CONCRETO_NI_TMC,
                              "perfil_hdpe_fabricante": PERFIL_DECLARADO})
    assert _punto(con_hdpe, "A-02").resultado.material.tipo is TipoMaterial.HDPE
    assert {"relleno_estructural_hdpe", "parametros_diseno_hdpe",
            "perfil_hdpe_fabricante",
            "eta_importancia_operativa_conducto"} <= set(
        con_hdpe.contexto.criterios_usados)


def test_sin_el_perfil_el_hdpe_no_se_adopta_y_el_punto_queda_incompleto(
        del_expediente):
    """
    El HDPE no se ADOPTA sin el perfil del fabricante, y el punto no sale
    «no factible» --que seria decir que no cumple--: sale detenido por el
    dato que falta, con su campo y la cota inferior en el mensaje.
    """
    informe = _correr_ancho(SIN_CONCRETO_NI_TMC)
    a02 = _punto(informe, "A-02")
    assert not a02.dimensionado
    (bloqueo,) = [b for b in a02.bloqueos if "MD" in b.etapa]
    assert bloqueo.tipo.value == "DatoFaltanteError"
    assert "perfil_hdpe_fabricante" in bloqueo.mensaje
    assert M8.ROTULO_HDPE_SIN_PRODUCTO in bloqueo.mensaje
    assert "COTA INFERIOR" in bloqueo.mensaje
    # Con el perfil declarado se adopta, y lo dice.
    informe = _correr_ancho({**SIN_CONCRETO_NI_TMC,
                             "perfil_hdpe_fabricante": PERFIL_DECLARADO})
    a02 = _punto(informe, "A-02")
    assert a02.dimensionado
    assert a02.estructural.seleccion == "perfil declarado del fabricante, 900 mm"
    assert a02.resultado.seccion.etiqueta() == "Ø 0.90 m"


def test_el_fixture_no_se_mueve_el_hdpe_no_desplaza_ni_bloquea_a_nadie(
        del_expediente):
    """
    La restriccion que el dueño NO levanto: A-01 y A-02 siguen en concreto de
    0.90 m, Clase II; B-01 sigue «no factible» por V2 (no por el dato del
    HDPE); C-01 sigue detenido en los criterios del cajon.
    """
    informe = _correr_ancho({})
    for id_ in ("A-01", "A-02"):
        p = _punto(informe, id_)
        assert p.dimensionado
        assert p.resultado.material.tipo is TipoMaterial.CONCRETO_REFORZADO
        assert p.resultado.seccion.etiqueta() == "Ø 0.90 m"
        assert p.estructural.seleccion == "Clase II"
        assert not [e for e in p.traza if "HDPE" in e.material]
    b01 = _punto(informe, "B-01")
    assert not b01.dimensionado
    (bloqueo,) = [b for b in b01.bloqueos if "MD" in b.etapa]
    assert bloqueo.tipo.value == "DisenoNoFactibleError"
    assert "perfil_hdpe_fabricante" not in bloqueo.mensaje
    assert not _punto(informe, "C-01").dimensionado


# ===========================================================================
# 10. Lo demas: por material, guardias, MD, CLI y JSON
# ===========================================================================

def test_lo_que_no_se_verifica_se_imprime_por_material(del_expediente, tmp_path):
    """
    El bloque del tubo de concreto de A-01 listaba el portico del marco, la
    flexion del HDPE y la costura empernada del TMC. Ahora, lo suyo.
    """
    salida = tmp_path / "informe.json"
    memoria = tmp_path / "memoria.html"
    subprocess.run(
        [sys.executable, "cli.py", str(CSV), "--luz", "2.75", "--alcance",
         "perfil", "--datos-externos", str(EXTERNOS), "--json", str(salida),
         "--html", str(memoria)],
        cwd=RAIZ, capture_output=True, text=True)   # sale con 1: no cierra
    datos = json.loads(salida.read_text(encoding="utf-8"))
    a01 = next(p for p in datos["puntos"] if p["id"] == "A-01")
    diferida = a01["estructural"]["verificacion_diferida"]
    assert diferida == [M8.DIFERIDO_CONCRETO_DIRECTO, M8.DIFERIDO_CLASES_M170M]
    codigos = [p["codigo"] for p in a01["estructural"]["pasos"]]
    assert M8.CODIGO_PASO_TIPO4 in codigos and M8.CODIGO_PASO_HMAX_TIPO4 in codigos
    html = memoria.read_text(encoding="utf-8")
    bloque = html[html.index('id="punto-A-01"'):html.index('id="punto-A-02"')]
    assert "Lo que no se verifica" in bloque
    seccion = bloque[bloque.index("Lo que no se verifica"):]
    assert "portico del marco" not in seccion
    assert "HDPE" not in seccion.split("</div>")[0] + seccion.split("</div>")[1]
    assert "Contraste con la instalacion Tipo 4" in bloque


def test_la_cli_de_texto_imprime_el_contraste_del_tipo_4(del_expediente):
    hecho = subprocess.run(
        [sys.executable, "cli.py", str(CSV), "--luz", "2.75", "--alcance",
         "perfil", "--datos-externos", str(EXTERNOS)],
        cwd=RAIZ, capture_output=True, text=True)
    lineas = [l for l in hecho.stdout.splitlines() if "Fase 8  Clase II" in l]
    assert len(lineas) == 2
    for linea in lineas:
        assert "con instalacion Tipo 4:" in linea


def test_cada_resultado_dice_lo_que_sigue_diferido_de_su_material(
        del_expediente, a01):
    tmc = _mat(TipoMaterial.TMC)
    r = M8.verificar_tmc(punto=a01, material=tmc, seccion=SeccionCircular(0.90),
                         altura_relleno=_altura(a01, tmc, 0.90))
    assert r.diferido == (M8.DIFERIDO_COSTURA_EMPERNADA,)
    hdpe = _mat(TipoMaterial.HDPE)
    cota = M8.cota_inferior_hdpe(punto=a01, material=hdpe,
                                 seccion=SeccionCircular(0.90),
                                 altura_relleno=_altura(a01, hdpe, 0.90))
    assert cota.diferido == (M8.DIFERIDO_FLEXION_HDPE,
                             M8.DIFERIDO_PANDEO_LOCAL_HDPE)
    assert set(r.diferido) | set(cota.diferido) <= set(
        M8.verificacion_diferida_estructural())


@pytest.mark.parametrize("conducto", ("xx", "", None, "tubo"))
def test_un_conducto_que_no_es_del_conjunto_cerrado_es_dato_invalido(conducto):
    with pytest.raises(DatoInvalidoError) as exc:
        M8.carga_viva_enterrada(H=1.0, D_i=0.90, conducto=conducto)
    assert exc.value.campo == "conducto"
    assert set(M8.CONDUCTOS) == {M8.CONDUCTO_TUBO_CONCRETO,
                                 M8.CONDUCTO_FLEXIBLE, M8.CONDUCTO_CAJON}


@pytest.mark.parametrize("D_E", (-5.0, -1e-9, float("nan"), float("inf"), True))
def test_una_cubierta_sin_sentido_no_da_un_IM_de_mas_del_33(D_E):
    """`incremento_dinamico_enterrado(-5.0)` devolvia 100.7 %."""
    with pytest.raises(DatoInvalidoError):
        M8.incremento_dinamico_enterrado(D_E)
    assert M8.incremento_dinamico_enterrado(0.0) == pytest.approx(
        33.0, rel=REL_TRANSPORTE)


def test_el_piso_del_peso_del_suelo_del_tubo_de_concreto_no_gobierna():
    """110 lb/ft3 (17.28) es menor que los 0.120 kcf del Manual (18.85): se
    lista en la procedencia, y el docstring dice que no puede gobernar."""
    con_piso = M8.pesos_especificos_de_carga(piso_tubo_concreto=True)
    sin_piso = M8.pesos_especificos_de_carga(piso_tubo_concreto=False)
    assert con_piso[0] == sin_piso[0] == pytest.approx(
        CN.PESO_SUELO_COMPACTADO_KN_M3, rel=REL_TRANSPORTE)
    assert "110 lb/ft3" in con_piso[2] and "110 lb/ft3" not in sin_piso[2]
    assert CN.PESO_SUELO_MIN_TUBO_CONCRETO_KN_M3 < CN.PESO_SUELO_COMPACTADO_KN_M3
    assert "NO PUEDE GOBERNAR" in M8.pesos_especificos_de_carga.__doc__


def test_md_dice_cuando_el_catalogo_se_agoto_por_la_fase_8():
    """
    El texto del Anexo B no se parafrasea; detras, cuando el ultimo escalon
    solo incumple verificaciones F8.*, la aclaracion.
    """
    mat = _mat(TipoMaterial.TMC)
    con = MD._motivo_descarte(mat, "Ø 2.10 m: incumple F8.COSTURA ...",
                              por_fase_8=True)
    sin = MD._motivo_descarte(mat, "Ø 2.10 m: incumple V3 ...")
    assert con.startswith(MD.MENSAJE_DIAMETRO_SUPERADO)
    assert MD.ACLARACION_DESCARTE_POR_FASE_8 in con
    assert MD.ACLARACION_DESCARTE_POR_FASE_8 not in sin
    assert MD.PREFIJO_CODIGO_FASE_8 == "F8."
    assert all(c.startswith(MD.PREFIJO_CODIGO_FASE_8) for c in M8.CODIGOS_FASE_8)


def test_eta_no_la_prescribe_ninguna_fuente_y_la_ficha_lo_dice():
    """
    12.5.4 fija la redundancia (eta_R = 1.00) y deja la clasificacion
    operativa; 1.3.5: «The Owner may declare». El 1.05 es la clasificacion
    del Propietario, [A] con la ventana del Manual de Puentes 2.3.2.5.
    """
    c = ca.CRITERIOS["eta_importancia_operativa_conducto"]
    assert c.valor == pytest.approx(1.05, rel=REL_TRANSPORTE)
    assert c.etiqueta == "A"
    assert c.sensibilidad == pytest.approx((0.95, 1.05), rel=REL_TRANSPORTE)
    assert "Ninguna fuente prescribe 1.05" in c.justificacion
    assert "The Owner may declare" in c.fuente
    reg = registro.construir()
    assert reg.cita("AASHTO_LRFD_9.1.3.5").caracter.value == "permiso"
    assert "redundant" in reg.cita("AASHTO_LRFD_9.12.5.4").texto_literal.texto


def test_los_parametros_del_hdpe_no_se_venden_como_el_extremo_desfavorable():
    c = ca.CRITERIOS["parametros_diseno_hdpe"]
    assert "No son todos el extremo" in c.justificacion
    assert c.valor["nu_suelo"] < c.sensibilidad["nu_suelo"][1]
    assert c.valor["K_B"] < c.sensibilidad["K_B"][1]
    assert c.valor["D_L"] < c.sensibilidad["D_L"][1]


@pytest.mark.pdf
@pytest.mark.parametrize("fuente_id, pagina_pdf, fragmentos", [
    ("AASHTO_LRFD_9", 80, ("may be neglected", "8.0 ft", "exceeds the span",
                           "distance between inside faces of end walls")),
    ("AASHTO_LRFD_9", 22, ("The Owner may declare",
                           "1.05 for critical or essential bridges")),
    ("AASHTO_LRFD_9", 1649, ("shall be considered redundant",)),
    ("AASHTO_LRFD_9", 1652, ("shall not exceed 95.0 in./kip",)),
    ("AASHTO_LRFD_9", 1688, ("85% Category I, 90% Category II, or 95% "
                             "Category III",
                             "No compaction required, except if Category III")),
    ("AASHTO_LRFD_9", 1689, ("minimum standard proctor compaction",
                             "Table 27.5.2.2-3")),
    ("AASHTO_LRFD_9", 1714, ("not meaningful for design",
                             "obtained from the pipe manufacturer",
                             "represents the design life of the project")),
    ("AASHTO_LRFD_9", 1720, ("A-2-4, A-2-5, A-4", "A-2-6, A-2-7, A-5, A-6",
                             "initial modulus of elasticity",
                             "limited as specified in Article 12.5.6.3")),
    ("EG2013", 194, ("A-1-a, A-1-b, A-2-4, A-2-6 y A-3",)),
    ("EG2013", 201, ("90% de la máxima densidad", "0,95 De (corona)")),
    ("EG2013", 246, ("4-9%",)),
    ("EG2013", 968, ("por lo menos 15 cm de espesor compactado",)),
    ("EG2013", 977, ("(pernos, tuercas)", "perforado")),
    ("EG2013", 990, ("sujeción lateral se construirán con material granular",)),
    ("EG2013", 992, ("mayor al 95%",)),
])
def test_los_literales_del_cierre_estan_en_la_pagina_que_se_cita(
        fuente_id, pagina_pdf, fragmentos):
    """Cada frase en que se apoya una correccion, en su pagina del PDF."""
    from src.normativa import fuentes
    from src.normativa.extraccion.pdf import texto_de_pagina
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[fuente_id])
    if not ruta.exists():
        pytest.skip(f"el PDF de {fuente_id} no esta enlazado (NORMAS_DIR)")
    texto = " ".join(texto_de_pagina(ruta, pagina_pdf).split())
    for fragmento in fragmentos:
        assert fragmento in texto, (fuente_id, pagina_pdf, fragmento)
