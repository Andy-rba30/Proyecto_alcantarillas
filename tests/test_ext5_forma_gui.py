"""
tests/test_ext5_forma_gui.py
============================
Aceptacion de EXT-5 (cluster GUI del dictamen de la auditoria externa):
EXT-G-01, PC-13, PC-14 y la parte de FORMA de EXT-V-02 / EXT-V-05 / EXT-V-06
que EXT-1 dejo abierta, mas la ayuda derivada de las seis claves externas
que EXT-0 decidio llenar (EXT-G-03).

Los cuatro casos del prompt, en el orden del prompt:

    (a) las DOS ventanas devuelven `int` para '1' y '-3', `float` solo con
        separador decimal o exponente, `list` para el catalogo del cajon y
        `ValueError` para un literal mal cerrado;
    (b) tras declarar los siete criterios del cajon DESDE LA VENTANA, C-01
        no se bloquea en `n_celdas_cajon`, y el test afirma cual es su
        bloqueo real (hoy el test de ventana es ciego a esto);
    (c) una cadena no numerica para un criterio numerico SIN rango se
        rechaza en la declaracion, no en M2/M4 (medido en el dictamen: 53 de
        70 claves aceptaban 'cero' y la corrida reventaba con TypeError);
    (d) 'nan' recibe el MISMO veredicto al escribir y al declarar.

La correccion que los cierra: `Criterio.forma`, que `_verificar_criterio`
exige a las 70 claves --- tambien cuando la sensibilidad no es numerica ---,
y UN solo parser GUI-GUI, `gui/componentes.py::interpretar_texto_declarado`,
que usan la pestaña 2 y la ventana emergente. La divergencia deliberada con
la CLI (`ast.literal_eval` del texto entero) se conserva, con su test en
`test_gui_contrato.py`.

Escritos primero EN ROJO, con `xfail(strict=True)` sobre el invariante y
nunca sobre la salida actual como oraculo (regla comun de la cadena EXT):
130 fallos y 31 errores medidos antes de tocar codigo. La marca se retiro
al corregir.
"""

import ast
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import cli
import criterios_adoptados as ca
import declaracion as dec
import variables_entrada as ve
from modelos import Derivada, Poblacion, TipoDeBloqueo
from normativa.esquema import (BandaDeInterpolacion, ConjuntoDeMaximos,
                               IntervaloAdmisible, PisoUnico, QuePasaFuera,
                               TechoUnico)
from tests.apoyo import doble_tkinter
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parent.parent

CLAVE_DE_RANGO = "v_max_concreto_eleccion"      # cara RANGO (ConjuntoDeMaximos)
CLAVE_DERIVADA = "tabla_recubrimiento_aashto_mm"

# Lo que M2, M4 y M7 EXIGEN de cada uno de los siete del cajon, leido de sus
# consumidores: `numero_de_celdas` pide un entero; `progresion_de_cajon` una
# serie de pares (B, H); `embocadura_cajon`, `n_manning_cajon` y
# `ke_entrada_cajon` declaran la CLAVE de una fila (texto); los dos espesores
# son longitudes en metros.
FORMA_DEL_CAJON = {
    "embocadura_cajon": "str",
    "n_manning_cajon": "str",
    "ke_entrada_cajon": "str",
    "espesor_pared_cajon": "float",
    "cobertura_minima_cajon": "float",
    "n_celdas_cajon": "int",
    "secciones_cajon_normalizadas": "serie_de_pares",
}

# Las seis claves de `cli.CLAVES_EXTERNAS` que no son columna, ni dato de
# sitio, ni criterio, y que hasta EXT-5 no estaban en el censo.
SEIS_EXTERNAS = ("luz_m", "TW_m", "longitud_m", "S_conducto",
                 "L_hidraulico_m", "categoria_tr")


def _formas_de(clave):
    forma = ca.CRITERIOS[clave].forma
    return forma if isinstance(forma, tuple) else (forma,)


# ===========================================================================
# Criterio.forma: el contrato de forma en la puerta unica
# ===========================================================================

def test_toda_entrada_declara_una_forma_de_la_familia_cerrada():
    """
    `forma` es obligatoria en las 70, con o sin sensibilidad numerica: es lo
    que hace que la puerta de declaracion rechace lo que M2/M4 iban a
    rechazar despues con una excepcion fuera de `ErrorProyecto`.
    """
    assert ca.FORMAS, "la familia de formas tiene que estar censada"
    for clave in ca.CRITERIOS:
        for f in _formas_de(clave):
            assert f in ca.FORMAS, (clave, f)


def test_la_forma_es_coherente_con_la_ventana_de_sensibilidad():
    for clave, c in ca.CRITERIOS.items():
        formas = _formas_de(clave)
        s = c.sensibilidad
        if isinstance(s, dict):
            assert formas == (ca.FORMA_DICT_CON_CAMPOS,), clave
        elif ca._rango_numerico(s) is not None:
            assert set(formas) <= {ca.FORMA_INT, ca.FORMA_FLOAT,
                                   ca.FORMA_PAR_ORDENADO}, clave
        if ca.FORMA_CATEGORIA in formas:
            assert isinstance(s, tuple) and all(isinstance(x, str) for x in s), (
                f"'{clave}' es una categoria y el conjunto cerrado de valores "
                f"vive en `sensibilidad`, que tiene que ser una tupla de textos")
            if c.valor is not None:
                assert c.valor in s, clave


def test_una_forma_que_no_es_de_la_familia_no_pasa_la_guardia():
    from dataclasses import replace
    c = replace(ca.CRITERIOS["talud_terraplen"], forma="numero")
    with pytest.raises(ValueError, match="forma"):
        ca._verificar_criterio("talud_terraplen", c)


def test_los_siete_del_cajon_llevan_la_forma_que_sus_consumidores_exigen():
    for clave, forma in FORMA_DEL_CAJON.items():
        assert _formas_de(clave) == (forma,), clave


@pytest.mark.parametrize("clave", sorted(ca.CRITERIOS))
def test_c_una_cadena_no_numerica_se_rechaza_en_la_declaracion(clave):
    """
    (c) 'cero' entra solo donde la forma admite TEXTO. En cualquier otra
    clave se rechaza AQUI, con `ValueError` (contrato SIS-E-05), y no en el
    consumidor con un `TypeError` que tumba la corrida.
    """
    if ca.FORMA_STR in _formas_de(clave):
        # Texto libre: 'cero' es un texto como otro y ENTRA; que sea una
        # clave de fila valida lo decide el consumidor (ficha EXT-5-03).
        ca.establecer_valor_dinamico(clave, "cero")
        assert ca.valor(clave) == "cero"
        return
    # Un `Derivada` se rechaza antes, por no declararse (EXT-V-04); una
    # `categoria`, por su conjunto cerrado; un criterio con ventana numerica,
    # por su ventana; el resto, por su forma.
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, "cero")


def test_c_las_que_aceptan_texto_son_exactamente_las_de_forma_textual():
    """
    El complemento de (c): el conjunto de claves que aceptan 'cero' no lo
    decide el azar de tener o no rango, lo decide la forma. Y son MENOS de
    las 53 que el dictamen midio.
    """
    aceptan = set()
    for clave in ca.CRITERIOS:
        if isinstance(ca.CRITERIOS[clave].resolucion, Derivada):
            continue
        try:
            ca.establecer_valor_dinamico(clave, "cero")
            aceptan.add(clave)
        except ValueError:
            pass
        finally:
            ca.quitar_valor_dinamico(clave)
    textuales = {clave for clave in ca.CRITERIOS
                 if ca.FORMA_STR in _formas_de(clave)}
    # Una categoria rechaza 'cero' porque no esta en su conjunto cerrado.
    assert aceptan == textuales
    assert len(aceptan) < 53


@pytest.mark.parametrize("malo", [1.0, True, "1", [1], "cero"])
def test_un_entero_es_un_entero(malo):
    """
    `n_celdas_cajon` (PC-13): ni 1.0, ni True, ni '1'. Solo un `int`. Que
    ademas sea >= 1 lo sigue exigiendo `M2.numero_de_celdas`: el signo es
    dominio del consumidor, la FORMA es de la puerta.
    """
    with pytest.raises(ValueError, match="forma"):
        ca.establecer_valor_dinamico("n_celdas_cajon", malo)


def test_un_entero_declarado_como_entero_llega_a_M2():
    ca.establecer_valor_dinamico("n_celdas_cajon", 1)
    assert ca.valor("n_celdas_cajon") == 1
    assert isinstance(ca.valor("n_celdas_cajon"), int)


@pytest.mark.parametrize("malo", ["cero", "0,30 m", True, [30.0], {"a": 1}])
def test_un_float_sin_rango_rechaza_lo_que_no_es_un_numero(malo):
    """`angulo_aletas` no tiene ventana: hasta EXT-5 aceptaba cualquier cosa."""
    assert ca.CRITERIOS["angulo_aletas"].sensibilidad is None
    with pytest.raises(ValueError, match="forma"):
        ca.establecer_valor_dinamico("angulo_aletas", malo)


def test_un_float_admite_un_entero_de_python():
    ca.establecer_valor_dinamico("angulo_aletas", 30)
    assert ca.valor("angulo_aletas") == 30


@pytest.mark.parametrize("malo", [(0.013,), "a", (0.01, 0.013, 0.02), (True, 0.013)])
def test_un_par_ordenado_es_un_par(malo):
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("n_manning_hdpe", malo)


@pytest.mark.parametrize("malo", [
    [[1.2, 0.9], [1.2, 0.9]],        # repetido
    [1.2, 0.9],                      # plano, no serie de pares
    [[1.2, "a"]],                    # un extremo no numerico
    [[1.2, 0.9, 1.5]],               # un trio
    [],                              # vacia
    "[[1.2, 0.9]]",                  # el texto, no la serie
])
def test_una_serie_de_pares_es_una_serie_de_pares_sin_repetidos(malo):
    with pytest.raises(ValueError, match="forma|par"):
        ca.establecer_valor_dinamico("secciones_cajon_normalizadas", malo)


def test_una_serie_de_pares_bien_formada_se_declara():
    serie = [[1.2, 0.9], [1.5, 1.2]]
    ca.establecer_valor_dinamico("secciones_cajon_normalizadas", serie)
    assert ca.valor("secciones_cajon_normalizadas") is serie


def test_una_categoria_solo_admite_su_conjunto_cerrado():
    with pytest.raises(ValueError, match="forma|categoria"):
        ca.establecer_valor_dinamico("condicion_pavimento", "rigida")
    ca.establecer_valor_dinamico("condicion_pavimento", "rigido")
    assert ca.valor("condicion_pavimento") == "rigido"


@pytest.mark.parametrize("malo", [1.0, "x", {}, [("inicio", 0.9)]])
def test_un_dict_con_campos_es_un_dict_no_vacio(malo):
    with pytest.raises(ValueError, match="forma"):
        ca.establecer_valor_dinamico("diametros_normalizados", malo)


def test_una_serie_de_claves_es_una_tupla_de_textos_sin_repetidos():
    """`F_pga` declara las FILAS de la tabla sobre las que se lee el factor."""
    assert _formas_de("F_pga") == (ca.FORMA_SERIE_DE_CLAVES,)
    for malo in ["C", ("C", "C"), (1, 2), ()]:
        with pytest.raises(ValueError, match="forma"):
            ca.establecer_valor_dinamico("F_pga", malo)
    ca.establecer_valor_dinamico("F_pga", ("C", "D"))
    assert ca.valor("F_pga") == ("C", "D")


def test_k_v_admite_el_regimen_prescrito_o_un_numero_y_nada_mas():
    """
    `M9.k_v_declarado` acepta la cadena del regimen prescrito O un numero:
    la forma de `k_v` es la UNION de las dos, y 'cero' no es ninguna.
    """
    assert set(_formas_de("k_v")) == {ca.FORMA_STR, ca.FORMA_FLOAT}
    ca.establecer_valor_dinamico("k_v", 0.25)
    ca.establecer_valor_dinamico("k_v", "prescrito_sin_caso_reservado")
    with pytest.raises(ValueError, match="forma"):
        ca.establecer_valor_dinamico("k_v", True)


def test_cortante_alto_declara_la_cuantia_que_M9_lee_y_no_un_si_no():
    """
    Lo refuto el auditor adversarial de EXT-5: la ficha decia «declaracion
    si/no» y M9 hace `float()` sobre el valor. Con `str`, 0.0025 se
    rechazaba en la puerta y 'si' entraba y reventaba en M9 fuera de
    ErrorProyecto. La forma es `float`, y el valor llega a M9 como el minimo
    que gobierna.
    """
    from modulos import M9_cabezal as M9
    clave = "cortante_alto_muro_e060_art_11_10_10_2"
    with pytest.raises(ValueError, match="forma"):
        ca.establecer_valor_dinamico(clave, "si")
    ca.establecer_valor_dinamico(clave, 0.0025)
    cuantia = M9.cuantia_de_diseno(cuantia_calculada=0.001,
                                   direccion="horizontal", cortante_alto=True)
    assert cuantia.cuantia_minima == pytest.approx(0.0025, rel=REL_TRANSPORTE)
    assert cuantia.gobierna == "minimo_normativo"


def test_el_parser_solo_lee_cifras_ascii(parser):
    """'١' (arabe) y '１２' (ancho completo) son texto, no 1 y 12 (auditoria)."""
    assert parser("\u0661") == "\u0661"
    assert parser("\uff11\uff12") == "\uff11\uff12"


def test_el_valor_del_archivo_de_cada_criterio_cumple_su_propia_forma():
    """La guardia corre al importar: si el archivo esta, el archivo cumple."""
    for clave, c in ca.CRITERIOS.items():
        ca._verificar_criterio(clave, c)


# ===========================================================================
# (a) Un solo parser GUI-GUI
# ===========================================================================

CASOS_DEL_PARSER = [
    ("1", 1), ("-3", -3), ("+4", 4), ("007", 7),
    ("1.5", 1.5), ("1,5", 1.5), (".5", 0.5), ("5.", 5.0), ("1,200", 1.2),
    ("2e3", 2000.0), ("1E-2", 0.01), ("-0,25", -0.25),
    ("[[1.20, 0.90], [1.50, 1.20]]", [[1.20, 0.90], [1.50, 1.20]]),
    ("(0.010, 0.013)", (0.010, 0.013)),
    ("{'K': 0.0098}", {"K": 0.0098}),
    ("cero", "cero"), ("S5", "S5"), (" cota_terreno ", "cota_terreno"),
    ("nan", "nan"), ("inf", "inf"),
]

TEXTOS_RECHAZADOS = ["", "   ", "[1.2, 0.9", "[[1.20, 0.90], [1.50",
                     "1.200,50", "1,000,000", "1.2.3", "--1", "1e", "1,5e"]


@pytest.fixture(scope="module")
def parser():
    return doble_tkinter.gui_componentes().interpretar_texto_declarado


@pytest.fixture(scope="module")
def pestana(doble_app):
    return object.__new__(doble_app.ExpedienteApp)


@pytest.fixture(scope="module")
def doble_app():
    return doble_tkinter.gui_app()


@pytest.fixture(scope="module")
def emergente():
    """Una `VentanaNormativa` SIN construir widgets: solo su logica."""
    gvn = doble_tkinter.gui_ventana_normativa()
    v = object.__new__(gvn.VentanaNormativa)
    v.clave = CLAVE_DE_RANGO
    v.valor_var = doble_tkinter.VariableDeTexto()
    return v


@pytest.mark.parametrize("texto, esperado", CASOS_DEL_PARSER)
def test_a_el_parser_devuelve_int_float_list_o_texto_segun_lo_tecleado(
        parser, texto, esperado):
    leido = parser(texto)
    assert type(leido) is type(esperado), (texto, leido)
    if isinstance(esperado, float):
        assert leido == pytest.approx(esperado, rel=REL_TRANSPORTE)
    else:
        assert leido == esperado


@pytest.mark.parametrize("texto", TEXTOS_RECHAZADOS)
def test_a_el_parser_rechaza_con_ValueError_lo_que_no_sabe_leer(parser, texto):
    with pytest.raises(ValueError):
        parser(texto)


def test_a_la_politica_de_coma_y_miles_rechaza_el_punto_de_miles(parser):
    """'1.200,50' no es 1200.5 ni 1.2: se rechaza diciendo la politica."""
    with pytest.raises(ValueError, match="miles|decimal"):
        parser("1.200,50")


@pytest.mark.parametrize("texto, esperado", CASOS_DEL_PARSER)
def test_a_las_dos_ventanas_leen_lo_mismo(pestana, emergente, texto, esperado):
    """La pestaña 2 y la emergente devuelven EL MISMO objeto para el mismo texto."""
    emergente.valor_var.set(texto)
    de_la_pestana = pestana._interpretar_valor_declarado(texto)
    de_la_emergente = emergente._valor_tecleado()
    assert type(de_la_pestana) is type(esperado)
    assert type(de_la_emergente) is type(esperado)
    assert de_la_pestana == de_la_emergente


@pytest.mark.parametrize("texto", TEXTOS_RECHAZADOS)
def test_a_las_dos_ventanas_rechazan_lo_mismo(pestana, emergente, texto):
    emergente.valor_var.set(texto)
    with pytest.raises(ValueError):
        pestana._interpretar_valor_declarado(texto)
    with pytest.raises(ValueError):
        emergente._valor_tecleado()


def test_a_hay_un_solo_parser_y_las_dos_ventanas_lo_llaman():
    """
    Guardia de AST (EXT-G-01): ni `float(` ni `literal_eval` en los dos
    metodos de las ventanas; los dos llaman a `interpretar_texto_declarado`.
    """
    def cuerpo(ruta, clase, metodo):
        arbol = ast.parse((RAIZ / ruta).read_text(encoding="utf-8-sig"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ClassDef) and nodo.name == clase:
                for f in nodo.body:
                    if isinstance(f, ast.FunctionDef) and f.name == metodo:
                        return f
        raise AssertionError(f"{ruta}::{clase}.{metodo} no existe")

    for ruta, clase, metodo in (
            ("gui/app.py", "ExpedienteApp", "_interpretar_valor_declarado"),
            ("gui/ventana_normativa.py", "VentanaNormativa", "_valor_tecleado"),
            ("gui/ventana_normativa.py", "VentanaNormativa", "_validador_de_rango")):
        f = cuerpo(ruta, clase, metodo)
        llamadas = {ast.unparse(n.func) for n in ast.walk(f)
                    if isinstance(n, ast.Call)}
        assert "interpretar_texto_declarado" in llamadas, (ruta, metodo)
        assert not any(l.endswith("literal_eval") or l == "float"
                       for l in llamadas), (ruta, metodo, llamadas)


def test_a_la_divergencia_con_la_cli_se_conserva(pestana):
    """El parser es GUI-GUI: la CLI sigue leyendo el texto entero con literal_eval."""
    assert ast.literal_eval("1,5") == (1, 5)
    assert pestana._interpretar_valor_declarado("1,5") == pytest.approx(
        1.5, rel=REL_TRANSPORTE)
    assert "DIVERGE" in pestana._interpretar_valor_declarado.__doc__


# ===========================================================================
# (d) 'nan': el mismo veredicto al escribir y al declarar
# ===========================================================================

def test_d_nan_se_pinta_en_rojo_al_escribir(emergente):
    gvn = doble_tkinter.gui_ventana_normativa()
    color, mensaje = emergente._validador_de_rango("nan")
    assert color == gvn.COLOR_ERROR, mensaje


def test_d_nan_se_rechaza_al_declarar_con_el_mismo_veredicto(emergente):
    emergente.valor_var.set("nan")
    with pytest.raises(ValueError):
        dec.declarar_en_rango(CLAVE_DE_RANGO, emergente._valor_tecleado())
    assert not ca.declarado_en_caliente(CLAVE_DE_RANGO)


def test_d_un_nan_numerico_es_invalido_en_rango_y_no_un_aviso():
    """`ConjuntoDeMaximos` devolvia AVISO para NaN: dos falsos seguidos."""
    resultado = dec.validar_en_rango(CLAVE_DE_RANGO, float("nan"))
    assert resultado.estado is dec.Estado.INVALIDO


def _rangos():
    fuera = QuePasaFuera.INCUMPLE_LA_NORMA
    return [
        IntervaloAdmisible(3.0, 6.0, "m/s", "X", fuera),
        TechoUnico(6.0, "m/s", "X", fuera),
        PisoUnico(3.0, "m/s", "X", fuera),
        ConjuntoDeMaximos((3.0, 4.5, 6.0), "m/s", "X", fuera),
        BandaDeInterpolacion(((0.0, 3.0), (1.0, 6.0)), "-", "m/s", "X", fuera),
    ]


@pytest.mark.parametrize("rango", _rangos(), ids=lambda r: type(r).__name__)
@pytest.mark.parametrize("valor", [float("nan"), float("inf"), -float("inf"), "nan"])
def test_d_validar_contra_rango_tiene_la_forma_MAT_D13(rango, valor):
    """
    Condicion en positivo y negada (`not x <= tope`): un NaN es falso frente
    a `<=` igual que frente a `>`, y solo la forma negada lo atrapa en los
    CINCO tipos de rango. Un no finito nunca es VALIDO ni AVISO.
    """
    assert dec.validar_contra_rango(rango, valor).estado is dec.Estado.INVALIDO


def test_d_validar_contra_rango_no_compara_en_positivo():
    """El AST: ninguna comparacion `<=`/`>=`/`<`/`>` decide fuera de un `not`."""
    arbol = ast.parse((RAIZ / "src" / "declaracion.py").read_text(encoding="utf-8"))
    f = next(n for n in ast.walk(arbol)
             if isinstance(n, ast.FunctionDef) and n.name == "validar_contra_rango")
    negadas = {id(n.operand) for n in ast.walk(f)
               if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not)}
    for n in ast.walk(f):
        if isinstance(n, ast.Compare) and any(
                isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for op in n.ops):
            assert id(n) in negadas, ast.unparse(n)


# ===========================================================================
# (b) y la cara de solo lectura: sobre la ventana de verdad
# ===========================================================================

def _interprete_con_ventana():
    sonda = "import tkinter, ttkbootstrap; r = tkinter.Tk(); r.destroy()"
    envoltorio = [] if shutil.which("xvfb-run") is None else ["xvfb-run", "-a"]
    for candidato in (sys.executable, "python3.12", "python3.11", "python3"):
        if shutil.which(candidato) is None and not Path(candidato).exists():
            continue
        try:
            hecho = subprocess.run(envoltorio + [candidato, "-c", sonda],
                                   capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if hecho.returncode == 0:
            return candidato, envoltorio
    return None, envoltorio


_INTERPRETE, _ENVOLTORIO = _interprete_con_ventana()


@pytest.fixture(scope="module")
def resumen_real(tmp_path_factory):
    if _INTERPRETE is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    salida = tmp_path_factory.mktemp("ext5")
    hecho = subprocess.run(
        _ENVOLTORIO + [_INTERPRETE, "-m", "tests.apoyo.gui_ext5_real", str(salida)],
        cwd=RAIZ, capture_output=True, text=True, timeout=600)
    assert hecho.returncode == 0, (
        f"la corrida de la GUI fallo:\n{hecho.stdout}\n{hecho.stderr}")
    return json.loads((salida / "resumen_ext5.json").read_text(encoding="utf-8"))


@pytest.mark.skipif(_INTERPRETE is None,
                    reason="ningun interprete disponible puede levantar una "
                           "ventana (falta tkinter, ttkbootstrap o el entorno grafico)")
def test_b_c01_no_se_bloquea_en_n_celdas_y_su_bloqueo_real_es_S_cauce(resumen_real):
    """
    (b) Los siete del cajon entran por el raton --- '1' como ENTERO --- y C-01
    sigue sin dimensionar por la razon REAL: el CSV de perfil trae `S_cauce`
    vacio y ningun tablero lo aporta. Ese es el bloqueo, y es UNO.
    """
    assert resumen_real["cajon_rechazado"] == {}
    assert resumen_real["cajon_declarado"]["n_celdas_cajon"] == "1"
    assert resumen_real["cajon_declarado"]["espesor_pared_cajon"] == "0.2"
    assert (resumen_real["cajon_declarado"]["secciones_cajon_normalizadas"]
            == "[[1.2, 0.9], [1.5, 1.2], [2.0, 1.5]]")
    assert not resumen_real["c01_dimensionado"]
    assert resumen_real["dimensionados"] == ["A-01", "A-02", "B-01"]
    for b in resumen_real["bloqueos_c01"]:
        assert "n_celdas_cajon" not in b["mensaje"], b
        assert "ENTERO" not in b["mensaje"], b
    reales = [b for b in resumen_real["bloqueos_c01"] if not b["diferido"]]
    assert len(reales) == 1, reales
    assert reales[0]["tipo"] == TipoDeBloqueo.DATO_FALTANTE.value
    assert "S_cauce" in reales[0]["mensaje"]


@pytest.mark.skipif(_INTERPRETE is None,
                    reason="ningun interprete disponible puede levantar una "
                           "ventana (falta tkinter, ttkbootstrap o el entorno grafico)")
def test_la_pestana_2_pone_cara_de_solo_lectura_a_un_derivado(resumen_real):
    """
    EXT-V-04, la mitad que EXT-1 dejo en el nucleo: la pestaña 2 apaga los
    dos botones que escriben, DICIENDO POR QUE, y el campo no se teclea. La
    ventana normativa sigue abriendose (es donde se lee de que se deriva).
    """
    cara = resumen_real["cara_derivada"]
    assert cara["aplicar"]["state"] == "disabled"
    assert cara["guardar"]["state"] == "disabled"
    assert "se deriva de" in cara["aplicar"]["tooltip"]
    assert "se deriva de" in cara["guardar"]["tooltip"]
    assert cara["ventana_norma"]["state"] == "normal"
    assert cara["campo"] in ("disabled", "readonly")
    corriente = resumen_real["cara_corriente"]
    assert corriente["aplicar"]["state"] == "normal"
    assert corriente["guardar"]["state"] == "normal"
    assert corriente["campo"] == "normal"


@pytest.mark.skipif(_INTERPRETE is None,
                    reason="ningun interprete disponible puede levantar una "
                           "ventana (falta tkinter, ttkbootstrap o el entorno grafico)")
def test_d_nan_recibe_el_mismo_veredicto_en_la_ventana_real(resumen_real):
    assert resumen_real["nan_al_escribir"]["color"] == resumen_real["color_error"]
    assert resumen_real["nan_al_declarar"]["estado"].startswith("No se declaro")
    assert resumen_real["nan_al_declarar"]["declarado"] is False


# ===========================================================================
# EXT-G-03: las seis claves externas, censadas y con ayuda derivada
# ===========================================================================

def test_las_seis_claves_externas_estan_en_el_censo_como_dato_externo():
    poblacion = Poblacion["DATO_EXTERNO"]
    for clave in SEIS_EXTERNAS:
        assert clave in ve.VARIABLES, clave
        assert ve.VARIABLES[clave].poblacion is poblacion, clave
    assert {v.clave for v in ve.por_poblacion()[poblacion]} == set(SEIS_EXTERNAS)


def test_las_ocho_fichas_del_json_se_derivan_del_censo():
    import ayuda_entrada as ay
    fichas = ay.fichas_de_datos_externos()
    assert [f.clave for f in fichas] == list(cli.CLAVES_EXTERNAS)
    for f in fichas:
        v = ve.variable(f.clave)
        assert f.concepto == v.concepto
        assert f.unidad == v.unidad
        assert f.de_donde_sale == ve.como_se_lee(v)


def test_la_fase_de_las_externas_con_consumidor_esta_medida():
    """Donde hay consumidor la fase se DEDUCE; donde no, el hueco dice a que fase pertenece."""
    for clave in SEIS_EXTERNAS:
        v = ve.variable(clave)
        assert v.fase, clave
        assert v.unidad, clave
        if v.consumido_por:
            for modulo in v.consumido_por:
                assert ve._FASE_DE_MODULO[modulo] in v.fase, (clave, modulo)


def test_las_dos_puertas_de_S_conducto_acotan_igual():
    """La clave del JSON y la columna tienen el MISMO dominio (cli._DOMINIO_DE_CLAVE)."""
    assert ve.variable("S_conducto").dominio is not None
    assert "S_conducto" in cli._DOMINIO_DE_CLAVE


def test_el_reporte_de_variables_cuenta_cuatro_poblaciones():
    texto = ve.reporte_variables()
    assert "tres poblaciones" not in texto
    assert Poblacion["DATO_EXTERNO"].value.upper() in texto


def test_la_gui_de_ayuda_ya_no_anuncia_claves_sin_ficha():
    fuente = (RAIZ / "gui" / "ayuda_entrada.py").read_text(encoding="utf-8")
    assert "sin_censo" not in fuente
    assert "no tienen ficha" not in fuente
