"""
tests/test_ext1_entradas.py
===========================
Tests de aceptacion de EXT-1: el cluster «entradas» del dictamen de la
auditoria externa del 2026-09-19
(`docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md`, paso 1;
prompt EXT-1 de `docs/planes_mejora/07_CADENA_PROMPTS_EXT.md`).

Guardias locales SIN cambio de contrato: ningun numero de la linea base se
mueve. Cada bloque nombra el ID que cierra. Se escribieron primero EN ROJO
(`xfail(strict=True)`) con la expectativa del invariante -- nunca con la
salida vigente como oraculo -- y el xfail se retiro al corregir.

Lo que se comprueba, por ID:

    EXT-A-03  `M2.progresion_de_cajon` rechaza pares (B, H) repetidos dentro
              de TOL_UMBRAL_NORMATIVO; `MD.disenar_material` no entra en
              bucle si la progresion no avanza.
    EXT-V-03  `M2.espesor_pared`: la rama circular rechaza lo mismo que la
              rectangular (Real y no bool, finito, `not t > 0`) y devuelve
              float.
    EXT-V-06  `M1._riesgo_del_propietario` valida la forma del mapa: fila
              desconocida, campo con errata, tipo, bool y no finito son
              DatoInvalidoError con la ruta, no un silencio.
    EXT-V-04  `establecer_valor_dinamico` rechaza toda escritura sobre un
              criterio de resolucion `Derivada`.
    EXT-V-05  sensibilidad estructurada {campo: (min, max)} para criterios de
              valor dict (empieza por 'seccion_receptor').
    PC-01     pares (min, max): len == 2 y orden en la guardia;
              `Material.__post_init__`; `M2.catalogo` con forma mala del par.
    EXT-V-02  `perdida_carga` / `ke_declarado` validan ke; ventana de tabla
    PC-02     para 'ke_entrada', 'v_max_tmc', 'v_max_hdpe'; la procedencia
              guarda la celda y dice «DIFIERE de la celda».
    PC-05     `M3._validar_parametros` y `M4._validar_positivo` a la forma
              MAT-D13; `control_salida` con TW no finito y finitud de salida.
    PC-28     `MD.disenar_punto` relanza el `DatoFaltanteError` comun a todos
              los candidatos en vez de degradarlo.
    PC-32     `M7.factor_esviaje`: guardia de salida con umbral nombrado.
    PC-33     `cli._numero_externo` excluye bool.
    PC-34     `cli.declarar_criterios`: «0,5» no declara la tupla (0, 5).
    PC-35     `cli --plantilla` inexistente o sin marcadores: sin traceback y
              sin JSON a medias.
"""
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
import criterios_adoptados as ca
import declaracion as dec
from constantes_normativas import KE_HDS5_C2
from dominios import ESVIAJE_MAX
from modelos import (DatoFaltanteError, DatoInvalidoError, ErrorProyecto,
                     Familia, FormaSeccion, LimiteNumericoError, PuntoCritico,
                     SeccionCircular, TipoMaterial, Verificacion)
from modulos import M1_clasificacion as M1
from modulos import M3_hidraulica as M3
from modulos import M4_control as M4
from modulos import M7_geometria as M7
from modulos import M11_reporte as M11
from modulos import MD
from modulos.M2_material import (CRITERIO_ESPESOR_PARED,
                                 CRITERIO_ESPESOR_PARED_CAJON,
                                 CRITERIO_N_MANNING_HDPE,
                                 CRITERIO_SECCIONES_CAJON, catalogo,
                                 espesor_pared, progresion_de_cajon)
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, declarados
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING, CP8_CONTROL_SALIDA
from tests.test_M2_material import DECLARACIONES_CAJON

CSV = Path(__file__).resolve().parent / "ejemplo_puntos.csv"
L_CONDUCTO = 24.0     # m
TW_LIBRE = 0.0        # m
FILA_TR = "quebrada_importante"
CLAVE_DERIVADA = "tabla_recubrimiento_aashto_mm"
FILA_KE = "concreto_headwall_square_edge"


def _punto(**cambios) -> PuntoCritico:
    base = dict(
        id="A-01", progresiva_km=0.380, progresiva_display="0+380",
        familia=Familia.A,
        Q_m3s=CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"],
        area_ha=850.0, S_cauce=CP2_GEOMETRIA_MANNING["S"],
        cota_terreno=42.10, cota_rasante=44.20, cota_subrasante=44.05,
        cbr_subrasante=8.5, esviaje_grados=15.0, ancho_plataforma=9.60,
        cota_fondo_receptor=41.30, Q_receptor_m3s=None, cota_TW=None,
        sucs_fundacion="SM", NF_profundidad_m=None,
    )
    base.update(cambios)
    return PuntoCritico(**base)


def _nada_cumple(*, punto, material, seccion, resultado):
    return (Verificacion(cumple=False, numeral="4.1.1.3.7 b)",
                         valor_obtenido="x", valor_admisible="y",
                         criterio_aplicado=None, codigo="V1"),)


@pytest.fixture
def _limpia():
    yield
    ca.limpiar_valores_dinamicos()
    dec.limpiar()
    # `conftest` repone sus declaraciones antes de cada test; aqui solo se
    # retira lo que este archivo declaro en caliente.


# ===========================================================================
# EXT-A-03 - la progresion del cajon no puede repetir un escalon
# ===========================================================================

@pytest.mark.parametrize("caso, serie", [
    ("adyacente", ((1.50, 1.20), (1.50, 1.20), (2.00, 1.50))),
    ("no adyacente: ciclo de longitud 2",
     ((1.50, 1.20), (2.00, 1.50), (1.50, 1.20))),
    ("casi duplicado dentro de TOL_UMBRAL_NORMATIVO",
     ((1.50, 1.20), (1.50 + 5e-10, 1.20), (2.00, 1.50))),
])
def test_progresion_de_cajon_rechaza_un_par_repetido(caso, serie):
    """
    EXT-A-03. Con un escalon repetido `_siguiente_seccion_cajon` devuelve
    siempre el mismo siguiente y el bucle de MD no termina (50 escalones en
    0.00 s). La igualdad es la de `_misma_seccion`, con tolerancia: un par a
    5e-10 del anterior es el mismo escalon del catalogo.
    """
    # `con_valor`: desde EXT-5 la puerta rechaza un par repetido EXACTO por
    # su forma; la igualdad con tolerancia sigue siendo de M2 y se prueba aqui.
    resto = {k: v for k, v in DECLARACIONES_CAJON.items()
             if k != CRITERIO_SECCIONES_CAJON}
    with declarados(resto), con_valor(
            CRITERIO_SECCIONES_CAJON, serie,
            motivo="prueba de la guardia de M2 con un escalon repetido"):
        with pytest.raises(DatoInvalidoError) as exc:
            progresion_de_cajon()
    assert exc.value.campo == CRITERIO_SECCIONES_CAJON
    assert "repet" in exc.value.motivo.lower(), caso


def test_la_progresion_no_se_ordena_ni_cambia_de_api():
    """La API por valor y el orden declarado se conservan (tres tests los fijan)."""
    serie = ((2.00, 1.50), (1.50, 1.20))       # decreciente a proposito
    with declarados({**DECLARACIONES_CAJON, CRITERIO_SECCIONES_CAJON: serie}):
        pares = progresion_de_cajon()
    assert len(pares) == 2
    assert pares[0][0] == pytest.approx(2.00, rel=REL_TRANSPORTE)
    assert pares[1][0] == pytest.approx(1.50, rel=REL_TRANSPORTE)


def test_disenar_material_no_entra_en_bucle_si_la_progresion_no_avanza(
        monkeypatch):
    """
    EXT-A-03, la guardia de progreso: si `siguiente_seccion` devuelve la
    seccion actual (o una ya visitada), MD levanta ErrorProyecto. Nunca un
    bucle: cualquier regresion futura colgaria la GUI sin excepcion.

    El doble cuenta llamadas y revienta con RuntimeError -- que NO es
    ErrorProyecto -- si el bucle sigue pidiendo escalones: asi el test falla
    en vez de colgarse mientras la guardia no exista.
    """
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    primera = SeccionCircular(0.90)
    llamadas = {"n": 0}

    def sin_avance(material, actual=None):
        llamadas["n"] += 1
        if llamadas["n"] > 5:
            raise RuntimeError("la progresion no avanza y MD sigue pidiendo")
        return primera

    monkeypatch.setattr(MD, "siguiente_seccion", sin_avance)
    with pytest.raises(ErrorProyecto) as exc:
        MD.disenar_material(_punto(), tubo,
                            Q=CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"],
                            S=CP2_GEOMETRIA_MANNING["S"],
                            L=L_CONDUCTO, TW=TW_LIBRE, verificar=_nada_cumple)
    assert "no avanza" in str(exc.value)


# ===========================================================================
# EXT-V-03 - un solo validador de espesor para las dos ramas
# ===========================================================================

ESPESORES_MALOS = [-0.1, 0, True, -0.0, float("inf"), float("nan"), "0.1"]


@pytest.mark.parametrize("t", ESPESORES_MALOS)
def test_la_rama_circular_de_espesor_pared_rechaza_lo_que_la_rectangular(t):
    """
    EXT-V-03. `True` era el peor: pared de 1.0 m (D_ext 2.9 m); `0` salia
    como int; -0.1 e inf entraban a la clave fisica y a V7.
    """
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    with pytest.raises(DatoInvalidoError) as exc:
        espesor_pared(replace(tubo, espesor_pared={900: t}), 0.90)
    assert exc.value.campo == CRITERIO_ESPESOR_PARED


@pytest.mark.parametrize("t", ESPESORES_MALOS)
def test_la_rama_rectangular_de_espesor_pared_rechaza_los_mismos(t):
    with declarados(DECLARACIONES_CAJON), \
            con_valor(CRITERIO_ESPESOR_PARED_CAJON, t,
                      motivo="valor de sonda para la guardia; no es una adopcion"):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        with pytest.raises(DatoInvalidoError) as exc:
            espesor_pared(marco, 1.50)
    assert exc.value.campo == CRITERIO_ESPESOR_PARED_CAJON


def test_el_espesor_valido_sale_como_float_en_las_dos_ramas():
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    t = espesor_pared(replace(tubo, espesor_pared={900: 1}), 0.90)
    assert isinstance(t, float) and t == pytest.approx(1.0, rel=REL_TRANSPORTE)


# ===========================================================================
# EXT-V-06 - la forma del mapa del Propietario
# ===========================================================================

RIESGOS_MALOS = [
    ("fila desconocida (errata)", {"quebrada_importantee": {"R": 0.10}},
     "quebrada_importantee"),
    ("campo con errata: 'r' por 'R'", {FILA_TR: {"r": 0.10}}, "'r'"),
    ("campo que no es numero", {FILA_TR: {"R": "0.10"}}, "R"),
    ("bool no es numero", {FILA_TR: {"n": True}}, "n"),
    ("no finito", {FILA_TR: {"R": float("nan")}}, "R"),
    ("la fila no es un mapa", {FILA_TR: (0.10, 25)}, FILA_TR),
    ("el exterior no es un mapa", [(FILA_TR, {"R": 0.10})], "mapa"),
]


@pytest.mark.parametrize("caso, declaracion, en_el_motivo", RIESGOS_MALOS)
def test_una_declaracion_del_propietario_mal_formada_es_dato_invalido(
        caso, declaracion, en_el_motivo, _limpia):
    """
    EXT-V-06. Hoy una fila con errata o la clave 'r' se IGNORA EN SILENCIO y
    la memoria imprime «DECLARADOS POR EL PROPIETARIO» con los maximos de la
    tabla; una lista o un texto tumban la corrida con TypeError/KeyError.
    """
    with con_valor(M1.CRITERIO_RIESGO_PROPIETARIO, declaracion,
                   motivo="valor de sonda para la guardia de forma"):
        with pytest.raises(DatoInvalidoError) as exc:
            M1.tr_de_categoria(FILA_TR)
    assert exc.value.campo == M1.CRITERIO_RIESGO_PROPIETARIO
    assert en_el_motivo in exc.value.motivo, caso


def test_una_declaracion_bien_formada_del_propietario_sigue_gobernando(_limpia):
    from constantes_normativas import RIESGO_ADMISIBLE
    maximos = RIESGO_ADMISIBLE[FILA_TR]
    ca.establecer_valor_dinamico(
        M1.CRITERIO_RIESGO_PROPIETARIO,
        {FILA_TR: {"R": maximos["R"] / 2, "n": maximos["n"] * 2}})
    tr = M1.tr_de_categoria(FILA_TR)
    assert tr.R == pytest.approx(maximos["R"] / 2, rel=REL_TRANSPORTE)


# ===========================================================================
# EXT-V-04 - un criterio Derivada no se pisa por ningun camino
# ===========================================================================

def test_establecer_valor_dinamico_rechaza_un_criterio_derivado(_limpia):
    """
    EXT-V-04. Medido en el dictamen: con la tabla pisada a 1.0 el
    recubrimiento AASHTO de M9 baja de 40.64 a 25.4 mm. La emergente protegia
    (`editable=False`); la pestaña 2, `--declarar` y `declarar_valor` no.
    """
    original = ca.CRITERIOS[CLAVE_DERIVADA].valor
    with pytest.raises(ValueError, match="se deriva de"):
        ca.establecer_valor_dinamico(CLAVE_DERIVADA, original)
    assert CLAVE_DERIVADA not in ca.valores_dinamicos()


def test_los_otros_dos_caminos_dinamicos_tampoco_pisan_un_derivado(_limpia):
    with pytest.raises(ValueError, match="se deriva de"):
        dec.declarar_valor(CLAVE_DERIVADA, {"x": 1.0})
    with pytest.raises(ValueError, match="se deriva de"):
        cli.declarar_criterios([f"{CLAVE_DERIVADA}=1.0"])
    assert CLAVE_DERIVADA not in ca.valores_dinamicos()


# ===========================================================================
# EXT-V-05 - sensibilidad estructurada por campo para valores dict
# ===========================================================================

CAMPOS_RECEPTOR = ("b_m", "z_HV", "S", "n", "altura_total_m")


def test_seccion_receptor_declara_su_ventana_campo_por_campo():
    s = ca.CRITERIOS["seccion_receptor"].sensibilidad
    assert isinstance(s, dict)
    assert set(s) == set(CAMPOS_RECEPTOR)
    for campo, rango in s.items():
        assert len(rango) == 2 and rango[0] <= rango[1], campo


def _receptor(**cambios):
    base = dict(ca.CRITERIOS["seccion_receptor"].valor)
    base.update(cambios)
    return base


@pytest.mark.parametrize("caso, valor", [
    ("n como texto", _receptor(n="0.03")),
    ("n como bool", _receptor(n=True)),
    ("tirante x5, fuera de su ventana", _receptor(altura_total_m=9.0)),
    ("clave desconocida", {**_receptor(), "ancho_m": 2.0}),
    ("clave que falta", {k: v for k, v in _receptor().items() if k != "n"}),
    ("no es un dict", (2.0, 1.5, 0.0008, 0.030, 1.80)),
])
def test_la_ventana_por_campo_se_evalua_de_verdad(caso, valor, _limpia):
    """
    EXT-V-05. La ventana en prosa no se evaluaba: `n='0.03'` -> TypeError en
    M3, `n=True` -> 1, clave desconocida ignorada, tirante x5 aceptado.
    """
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("seccion_receptor", valor)
    assert "seccion_receptor" not in ca.valores_dinamicos(), caso


def test_un_receptor_dentro_de_su_ventana_se_declara_y_llega_a_M3(_limpia):
    ca.establecer_valor_dinamico("seccion_receptor", _receptor(n=0.028))
    assert M3._seccion_declarada().n == pytest.approx(0.028, rel=REL_TRANSPORTE)


def test_la_sensibilidad_estructurada_no_entra_al_barrido_numerico():
    """Un dict de rangos no es un par (min, max): no se recorre como escalar."""
    assert "seccion_receptor" not in ca.parametros_sensibilizables()
    assert "seccion_receptor" in ca.parametros_sensibilizables(solo_numericos=False)


# ===========================================================================
# PC-01 - el par (n_min, n_max) se valida como par
# ===========================================================================

@pytest.mark.parametrize("par", [(0.013, 0.010), (0.010, 0.012, 0.013),
                                 [0.012], ()])
def test_la_guardia_exige_un_par_ordenado_de_dos_extremos(par, _limpia):
    """
    PC-01. `(0.013, 0.010)` pasaba: cada extremo cae en la ventana y nadie
    miraba el orden. Con Q = 1.167 y S = 0.020 el par nominal descarta el
    HDPE por V3 y el invertido APRUEBA 0.90 m con d50 de 0.443 en vez de 0.860.
    """
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CRITERIO_N_MANNING_HDPE, par)
    assert CRITERIO_N_MANNING_HDPE not in ca.valores_dinamicos()


def test_material_rechaza_n_min_mayor_que_n_max():
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    with pytest.raises(DatoInvalidoError) as exc:
        replace(tubo, n_min=0.013, n_max=0.010)
    assert "n_min" in exc.value.motivo and "n_max" in exc.value.motivo


@pytest.mark.parametrize("par", [0.012, [0.012], (0.013, 0.010), "0.012",
                                 (0.010, True)])
def test_el_catalogo_convierte_la_forma_mala_del_par_en_dato_invalido(par):
    """Un escalar declarado tumbaba la corrida ENTERA con TypeError (los tres
    materiales se construyen juntos en `materiales_candidatos`)."""
    with con_valor(CRITERIO_N_MANNING_HDPE, par,
                   motivo="forma de sonda para la guardia del par"):
        with pytest.raises(DatoInvalidoError) as exc:
            catalogo(TipoMaterial.HDPE)
    assert exc.value.campo == CRITERIO_N_MANNING_HDPE


# ===========================================================================
# EXT-V-02 / PC-02 - ke y los [C] escalares con ventana de tabla
# ===========================================================================

KE_MALOS = [-0.5, True, float("inf"), float("nan"), "0.5"]


@pytest.mark.parametrize("ke", KE_MALOS)
def test_perdida_carga_rechaza_un_ke_que_no_es_un_coeficiente(ke):
    c = CP8_CONTROL_SALIDA
    with pytest.raises(DatoInvalidoError) as exc:
        M4.perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"], ke=ke)
    assert exc.value.campo == "ke"


def test_perdida_carga_admite_ke_cero():
    """`not ke >= 0`: el cero es una embocadura sin perdida, no un error."""
    c = CP8_CONTROL_SALIDA
    H0 = M4.perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"], ke=0.0)
    H5 = M4.perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"], ke=c["ke"])
    assert H0 < H5


@pytest.mark.parametrize("ke", [-50, "texto", True, [1, 2]])
def test_ke_declarado_rechaza_un_criterio_que_no_es_un_coeficiente(ke):
    """
    EXT-V-02. `--declarar ke_entrada=-50` producia HW_salida = -7.668 m con el
    punto dimensionado y cero incumplidas; 'texto', True y [1,2] salian como
    TypeError fuera de ErrorProyecto.
    """
    with con_valor(M4.CRITERIO_KE, ke, motivo="valor de sonda para la guardia"):
        with pytest.raises(DatoInvalidoError) as exc:
            M4.ke_declarado()
    assert exc.value.campo == M4.CRITERIO_KE


def test_ke_entrada_lleva_la_ventana_de_la_tabla_C2():
    """PC-02: la Tabla C.2 va de 0.2 a 0.9, y la ventana sale de ella."""
    coeficientes = [f["ke"] for f in KE_HDS5_C2.values()]
    s = ca.CRITERIOS["ke_entrada"].sensibilidad
    assert s[0] == pytest.approx(min(coeficientes), rel=REL_TRANSPORTE)
    assert s[1] == pytest.approx(max(coeficientes), rel=REL_TRANSPORTE)
    assert "ke_entrada" in ca.parametros_sensibilizables()


@pytest.mark.parametrize("clave, valor", [
    ("ke_entrada", -0.5), ("ke_entrada", 0.0), ("ke_entrada", 5.0),
    ("v_max_tmc", -1.0), ("v_max_tmc", 0.0), ("v_max_tmc", 100.0),
    ("v_max_hdpe", -1.0), ("v_max_hdpe", 0.0), ("v_max_hdpe", 100.0),
])
def test_los_tres_C_escalares_de_perfil_tienen_ventana_que_los_cubre(
        clave, valor, _limpia):
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, valor)
    assert clave not in ca.valores_dinamicos()


def test_declarar_desde_tabla_guarda_la_celda_y_exige_nota_si_difiere(_limpia):
    """
    EXT-V-02, la procedencia veraz. Hoy -50 se declaraba con «proviene de la
    fila» de la Tabla C.2. Con fila y columna nombradas la celda es 0.5:
    declarar otra cosa sin nota se rechaza; con nota, la procedencia lo dice.
    """
    with pytest.raises(ValueError, match="celda"):
        dec.declarar_desde_tabla("ke_entrada", 0.7, filas=(FILA_KE,),
                                 columnas=("ke",))
    assert "ke_entrada" not in ca.valores_dinamicos()

    p = dec.declarar_desde_tabla("ke_entrada", 0.7, filas=(FILA_KE,),
                                 columnas=("ke",), nota="tanteo de sensibilidad")
    assert p.valor_de_la_celda == pytest.approx(0.5, rel=REL_TRANSPORTE)
    assert "DIFIERE de la celda (0.5)" in p.como_texto()
    assert "DIFIERE de la celda" in M11._de_donde_salio(
        "ke_entrada", cli.capturar_contexto(csv_sha1=""))


def test_declarar_el_valor_de_la_celda_sigue_diciendo_proviene(_limpia):
    p = dec.declarar_desde_tabla("ke_entrada", 0.5, filas=(FILA_KE,),
                                 columnas=("ke",))
    assert p.valor_de_la_celda == pytest.approx(0.5, rel=REL_TRANSPORTE)
    assert "proviene de la fila" in p.como_texto()
    assert "DIFIERE" not in p.como_texto()
    assert "PROVIENE de esa fila" in M11._de_donde_salio(
        "ke_entrada", cli.capturar_contexto(csv_sha1=""))


def test_un_criterio_que_declara_la_clave_de_fila_no_difiere_de_ninguna_celda(
        _limpia):
    """
    Lo que el auditor adversarial de EXT-1 refuto: 'ke_entrada_cajon' declara
    la CLAVE de la fila de la Tabla C.2 -- asi lo hace la ventana de la GUI
    (`_declarar_segun_cara`, solo fila) -- y la primera version de la guardia
    la comparaba con el coeficiente de la celda y la rechazaba. La celda solo
    se cita cuando lo declarado es un numero.
    """
    fila = "cajon_aletas_30_75_escuadra"
    with declarados({k: v for k, v in DECLARACIONES_CAJON.items()
                     if k != "ke_entrada_cajon"}):
        p = dec.declarar_desde_tabla("ke_entrada_cajon", fila,
                                     tabla_id="HDS5_3ED.TC2", filas=(fila,))
        assert p.valor_de_la_celda is None
        assert not p.difiere_de_la_celda()
        assert "proviene de la fila" in p.como_texto()
        assert ca.valor("ke_entrada_cajon") == fila


def test_material_admite_el_par_de_manning_sin_declarar():
    """El (None, None) documentado en M2 no es un TypeError del constructor."""
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    sin_n = replace(tubo, n_min=None, n_max=None)
    assert sin_n.n_min is None and sin_n.n_max is None


# ===========================================================================
# PC-05 - guardias a la forma MAT-D13 y finitud a la salida
# ===========================================================================

@pytest.mark.parametrize("Q, S, n", [
    (float("nan"), 0.006, 0.013), (1.0, float("nan"), 0.013),
    (1.0, 0.006, float("nan")),
])
def test_validar_parametros_de_M3_no_es_permeable_a_NaN(Q, S, n):
    """`if x <= 0` deja pasar NaN y sale ValueError de brentq."""
    with pytest.raises(DatoInvalidoError):
        M3._validar_parametros(SeccionCircular(0.90), Q=Q, S=S, n=n)


def test_validar_positivo_de_M4_no_es_permeable_a_NaN():
    with pytest.raises(DatoInvalidoError) as exc:
        M4._validar_positivo("Q", float("nan"), "el caudal debe ser positivo")
    assert exc.value.campo == "Q"


def _control_salida(**cambios):
    """El tubo de CP-2 bajo control de salida, con lo que el test cambie."""
    c2, c8 = CP2_GEOMETRIA_MANNING, CP8_CONTROL_SALIDA
    base = dict(Q=c2["Q_con_n_max_esperado"], seccion=SeccionCircular(c2["D"]),
                S=c2["S"], L=c8["L"], TW=TW_LIBRE, n=c8["n"], ke=c8["ke"])
    base.update(cambios)
    return M4.control_salida(**base)


@pytest.mark.parametrize("TW", [float("nan"), -0.1])
def test_control_salida_rechaza_un_TW_que_no_es_un_tirante(TW):
    with pytest.raises(DatoInvalidoError) as exc:
        _control_salida(TW=TW)
    assert exc.value.campo == "TW"


@pytest.mark.parametrize("L, TW", [(float("inf"), 0.0), (24.0, float("inf"))])
def test_control_salida_no_devuelve_un_HW_no_finito(L, TW):
    """SIS-G-01 en M4: la guardia va a la SALIDA y nombra el par."""
    with pytest.raises(LimiteNumericoError) as exc:
        _control_salida(L=L, TW=TW)
    assert "L = " in exc.value.motivo and "TW = " in exc.value.motivo


# ===========================================================================
# PC-28 - el dato que falta no se pierde en «no factible»
# ===========================================================================

def test_disenar_punto_relanza_el_dato_faltante_comun_a_todos(monkeypatch):
    def falta_el_dato(punto, material, **kw):
        raise DatoFaltanteError("Q_evento_extremo_m3s",
                                detalle="lo pide V8 una vez declarado su TR")

    monkeypatch.setattr(MD, "disenar_material", falta_el_dato)
    with pytest.raises(DatoFaltanteError) as exc:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=_nada_cumple)
    assert exc.value.campo == "Q_evento_extremo_m3s"


def test_si_un_candidato_posterior_cierra_el_dato_faltante_no_lo_impide(
        monkeypatch):
    """Sin cambio de contrato: el descarte por material sigue igual."""
    vistos = []

    def uno_falta_otro_cierra(punto, material, **kw):
        vistos.append(material.tipo)
        if len(vistos) == 1:
            raise DatoFaltanteError("x", detalle="sonda")
        return "RESULTADO", ""

    monkeypatch.setattr(MD, "disenar_material", uno_falta_otro_cierra)
    assert MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                            verificar=_nada_cumple) == "RESULTADO"


# ===========================================================================
# PC-32 - guardia de salida del factor de esviaje
# ===========================================================================

def test_factor_esviaje_tiene_guardia_de_salida_con_umbral_nombrado():
    """
    PC-32. A 89.99999 grados el coseno esta por debajo del umbral nombrado en
    `tolerancias.COS_ESVIAJE_MIN` y el factor deja de estar determinado.
    """
    from tolerancias import COS_ESVIAJE_MIN
    assert 0 < COS_ESVIAJE_MIN < 1
    with pytest.raises(LimiteNumericoError) as exc:
        M7.factor_esviaje(_punto(esviaje_grados=ESVIAJE_MAX - 1e-7))
    assert exc.value.campo == "esviaje_grados"
    assert "COS_ESVIAJE_MIN" in exc.value.motivo


def test_el_casi_paralelo_que_M0_admite_sigue_teniendo_factor():
    """MAT-O18 sigue en pie: 89.9 grados no se corta con un tope inventado."""
    assert M7.factor_esviaje(_punto(esviaje_grados=ESVIAJE_MAX - 0.1)) > 1.0


# ===========================================================================
# PC-33 / PC-34 / PC-35 - la CLI
# ===========================================================================

def test_un_dato_externo_booleano_no_es_un_numero():
    with pytest.raises(DatoInvalidoError) as exc:
        cli._numero_externo("luz_m", True, "prueba")
    assert exc.value.campo == "luz_m"
    assert "bool" in exc.value.motivo.lower()


def test_una_coma_decimal_no_declara_una_tupla_en_silencio(_limpia):
    """PC-34: `--declarar ke_entrada=0,5` declaraba la TUPLA (0, 5)."""
    with pytest.raises(ValueError, match="coma"):
        cli.declarar_criterios(["ke_entrada=0,5"])
    assert "ke_entrada" not in ca.valores_dinamicos()
    # La tupla ESCRITA como tupla sigue siendo declarable.
    cli.declarar_criterios([f"{CRITERIO_N_MANNING_HDPE}=(0.011, 0.012)"])
    assert CRITERIO_N_MANNING_HDPE in ca.valores_dinamicos()


def test_una_plantilla_inexistente_no_deja_el_json_a_medias(tmp_path, capsys):
    json_salida = tmp_path / "a.json"
    codigo = cli.main([str(CSV), "--luz", "2.0", "--json", str(json_salida),
                       "--html", str(tmp_path / "m.html"),
                       "--plantilla", str(tmp_path / "no_existe.html")])
    err = capsys.readouterr().err
    assert codigo == 2
    assert "no_existe.html" in err
    assert not json_salida.exists()


def test_una_plantilla_sin_marcadores_no_deja_el_json_a_medias(tmp_path, capsys):
    vacia = tmp_path / "vacia.html"
    vacia.write_text("<html><body>sin marcadores</body></html>", encoding="utf-8")
    json_salida = tmp_path / "a.json"
    codigo = cli.main([str(CSV), "--luz", "2.0", "--json", str(json_salida),
                       "--html", str(tmp_path / "m.html"),
                       "--plantilla", str(vacia)])
    err = capsys.readouterr().err
    assert codigo == 2
    assert "vacia.html" in err
    assert not json_salida.exists()
