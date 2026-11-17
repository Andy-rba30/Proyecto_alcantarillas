"""
tests/test_ve2_materiales.py
============================
La aceptacion de VE-2 en sus dos decisiones de MATERIALES, (a) y (g) de la
ficha VE1-02, aprobadas por el dueño el 2026-11-17.

(a) · LA COLUMNA DEL n DEL CONCRETO ES UNA ELECCION [A]. La doble n del tubo
      de concreto --n MAXIMO de la Tabla Nº 09 para capacidad y tirante, n
      MINIMO para velocidad maxima y socavacion-- no tiene numeral: el Manual
      de Hidrologia, num. 4.1.1.3.6, pag. impresa 74, solo dice «n :
      Coeficiente de Manning (Ver Tabla Nº 09)», y la tabla (pag. impresa 75)
      da MINIMO, NORMAL y MAXIMO sin regla de columna. Pasa a ser el criterio
      [A] de perfil 'columna_n_manning_concreto' (forma categoria), con valor
      de archivo = la doble n de hoy y dos alternativas: la columna NORMAL
      (0.011) y el n unico del HDS-5 para conductos de pared lisa (0.012,
      num. 3.1.4, pag. impresa 3.8, [C]). Lo consume `M2.catalogo` para el
      tubo de concreto; el marco sigue con 'n_manning_cajon' y el HDPE con
      'n_manning_hdpe'.

(g) · LOS DIAMETROS SON LOS DESIGNADOS POR LA NORMA DE PRODUCTO. Las series
      de diametros designados de AASHTO M 170M (concreto), M 36 / ASTM A760
      (TMC) y M 294 (HDPE) son [N] en `constantes_normativas`, y
      `M2.siguiente_diametro` rechaza --por material-- un escalon que no sea
      designado para ese material. El diametro ingles convertido de M 170M
      (p. ej. 1.0668 m para el designado de 1050 mm) se admite SOLO en el
      concreto y SOLO si el criterio [A] 'diametro_de_diseno_concreto' lo
      declara: «At the manufacturer's option the design diameter shall be the
      designated diameter or the converted English diameter» (num. 12.1).
      375, 525, 675 y 825 mm son designados: no hay guardia de centimetro.

Escrita PRIMERO, en rojo (§1 regla 4 de la cadena): los tests con
`xfail(strict=True)` fallaban por su motivo antes de tocar el codigo y se
liberaron al implementar; los que no lo llevan son GUARDIAS que valen antes y
despues y lo dicen en su docstring. Los datos son DATOS DE PRUEBA.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import variables_entrada as ve
from src.modelos import DatoInvalidoError, NIVEL_PERFIL, TipoMaterial
from src.modulos import M2_material as M2
from src.normativa import registro as _registro
from src.normativa.esquema import Caracter, MetodoDeVerificacion, Verbo
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP11_SERIES_NOMINALES

RAIZ = Path(__file__).resolve().parents[1]
FICHAS = RAIZ / "docs" / "decisiones_diferidas.md"

CONCRETO = TipoMaterial.CONCRETO_REFORZADO
TMC = TipoMaterial.TMC
HDPE = TipoMaterial.HDPE

COLUMNA = "columna_n_manning_concreto"
DIAMETRO_DE_DISENO = "diametro_de_diseno_concreto"

SERIE_6_IN = {"inicio": 0.9144, "paso": 0.1524}
SEIS_IN_CONCRETO = ["0.9144", "1.0668", "1.2192", "1.3716", "1.524",
                    "1.6764", "1.8288", "1.9812", "2.1336", "2.286",
                    "2.4384", "2.5908"]
ARCHIVO = ["0.9", "1.05", "1.2", "1.35", "1.5", "1.65", "1.8", "1.95",
           "2.1", "2.25", "2.4", "2.55", "2.7"]


def _reg():
    return _registro.construir()


def _fichas() -> dict:
    texto = FICHAS.read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in re.finditer(
        r"^## (\S+) · (.*?)(?=^## |\Z)", texto, flags=re.M | re.S)}


def _recorrido(material) -> list:
    """Los escalones de la progresion VIGENTE de `material`, como texto."""
    D, salida = M2.siguiente_diametro(material), []
    while D is not None:
        salida.append(repr(D))
        D = M2.siguiente_diametro(material, D)
    return salida


def _recorrido_hasta_el_rechazo(material) -> tuple:
    """(escalones admitidos, excepcion del primero que se rechaza o None)."""
    admitidos = []
    try:
        D = M2.siguiente_diametro(material)
        while D is not None:
            admitidos.append(repr(D))
            D = M2.siguiente_diametro(material, D)
    except DatoInvalidoError as exc:
        return admitidos, exc
    return admitidos, None


# ===========================================================================
# (a) · la columna del n del concreto es una eleccion [A]
# ===========================================================================

def test_a_el_criterio_tiene_su_ficha_de_perfil():
    c = ca.criterio(COLUMNA)
    assert c.etiqueta == "A"
    assert c.nivel == NIVEL_PERFIL
    assert c.forma == ca.FORMA_CATEGORIA
    assert c.valor == "doble_n_minimo_maximo"
    assert {"doble_n_minimo_maximo", "columna_normal",
            "n_unico_hds5"} <= set(c.sensibilidad)
    assert c.resolucion is not None
    # La justificacion dice que la doble n NO tiene numeral y de donde sale
    # cada alternativa, con su pagina.
    for necesario in ("4.1.1.3.6", "Tabla Nº 09", "0.011", "0.012", "3.8",
                      "sin numeral"):
        assert necesario in c.justificacion + c.fuente, necesario


def test_a_el_valor_de_archivo_es_la_doble_n_de_hoy_y_registra_el_uso():
    ca.reiniciar_usos()
    concreto = M2.catalogo(CONCRETO)
    fila = cn.TABLA_09_FILAS["concreto_tubo_recto"]
    assert (concreto.n_min, concreto.n_max) == (fila["min"], fila["max"]) \
        == cn.MANNING["concreto_tubo_recto"]
    assert (concreto.n_min, concreto.n_max) == pytest.approx(
        (0.010, 0.013), rel=REL_TRANSPORTE)
    # El rotulo de la fila NO cambia con el valor de archivo: es lo que la
    # memoria imprimia, y la linea base no puede moverse.
    assert concreto.fila_manning == fila["fila"]
    assert COLUMNA in ca.criterios_usados()


@pytest.mark.parametrize("columna, n", [
    ("columna_normal", 0.011),
    ("n_unico_hds5", 0.012),
], ids=["normal_tabla_09", "hds5_pared_lisa"])
def test_a_las_alternativas_dan_un_n_unico(columna, n):
    with declarados({COLUMNA: columna}):
        concreto = M2.catalogo(CONCRETO)
    assert concreto.n_min == concreto.n_max == n
    assert concreto.n_para_capacidad == concreto.n_para_velocidad_maxima == n


def test_a_la_columna_normal_se_lee_de_la_tabla_y_no_se_copia():
    with declarados({COLUMNA: "columna_normal"}):
        concreto = M2.catalogo(CONCRETO)
    assert concreto.n_min == cn.TABLA_09_FILAS["concreto_tubo_recto"]["normal"]
    assert "NORMAL" in concreto.fila_manning


def test_a_el_n_del_hds5_es_el_de_la_cita_verificada():
    cita = _reg().cita("HDS5_3ED.3.1.4#N_TIPICO")
    assert cita.pagina_impresa == "3.8" and cita.pagina_pdf == 90
    assert cita.numeral == "3.1.4"
    assert cita.caracter is Caracter.DEFINICION
    texto = cita.texto_literal.texto
    assert ("Typical Manning's n values used for designing culverts are "
            "n = 0.012 for smooth walled culverts") in texto
    # El numero que M2 usa es el de la frase, no otro.
    assert f"n = {ca.N_MANNING_PARED_LISA_HDS5}" in texto
    with declarados({COLUMNA: "n_unico_hds5"}):
        assert M2.catalogo(CONCRETO).n_min == ca.N_MANNING_PARED_LISA_HDS5
        assert "HDS-5" in M2.catalogo(CONCRETO).fila_manning


@pytest.mark.parametrize("columna", ["columna_normal", "n_unico_hds5"])
def test_a_el_tmc_el_hdpe_y_el_marco_no_lo_leen(columna):
    antes = {t: (M2.catalogo(t).n_min, M2.catalogo(t).n_max)
             for t in (TMC, HDPE)}
    with declarados({COLUMNA: columna}):
        despues = {t: (M2.catalogo(t).n_min, M2.catalogo(t).n_max)
                   for t in (TMC, HDPE)}
    assert antes == despues
    # La estimacion estatica de `variables_entrada` sigue tambien la llamada
    # de MD a `M2.catalogo`: lo que importa es que el que escribe la clave es
    # M2, el modulo de la Fase 3.
    assert "M2_material" in ve.variable(COLUMNA).consumido_por


def test_a_una_columna_fuera_del_conjunto_se_rechaza_en_la_puerta():
    with pytest.raises(ValueError):
        ca.verificar_declaracion(COLUMNA, "columna_maxima")
    with pytest.raises(ValueError):
        ca.verificar_declaracion(COLUMNA, 0.012)


def test_a_la_segunda_linea_de_M2_detiene_una_columna_ajena():
    """
    Por MUTACION (a8): quien esquive la puerta --sustituyendo la ficha-- no
    llega a un `KeyError`: M2 detiene la columna ajena como dato invalido del
    expediente, con la clave del criterio.
    """
    from tests.apoyo.criterios import con_valor
    with con_valor(COLUMNA, "columna_maxima",
                   motivo="prueba de la segunda linea de M2"):
        with pytest.raises(DatoInvalidoError) as exc:
            M2.catalogo(CONCRETO)
    assert exc.value.campo == COLUMNA


def test_a_el_fundamento_define_y_no_obliga():
    f = _reg().fundamento("F4.N_CONCRETO")
    assert f.verbo is Verbo.DEFINE
    assert {"MC_HHD.4.1.1.3.6", "MC_HHD.4.1.1.3.6#T09",
            "HDS5_3ED.3.1.4#N_TIPICO"} <= set(f.citas)
    for cita_id in f.citas:
        assert _reg().cita(cita_id).caracter in (Caracter.DEFINICION,
                                                  Caracter.APROXIMACION)
    assert "sin numeral" in f.por_que


@pytest.mark.parametrize("columna", ["doble_n_minimo_maximo", "columna_normal",
                                     "n_unico_hds5"])
def test_a_el_tubo_de_concreto_emite_la_eleccion_en_su_traza(columna):
    with declarados({COLUMNA: columna}):
        concreto = M2.catalogo(CONCRETO)
    (paso,) = [p for p in concreto.pasos if p.fundamento_id == "F4.N_CONCRETO"]
    (eleccion,) = paso.elecciones
    assert eleccion.clave_criterio == COLUMNA and eleccion.valor == columna
    assert len(eleccion.entre) == 3
    # El TMC y el HDPE siguen sin traza de Fase 3: su n es lectura directa
    # (o su propio criterio), no esta eleccion.
    assert M2.catalogo(TMC).pasos == () and M2.catalogo(HDPE).pasos == ()


def test_a_guardia_el_marco_sigue_con_su_propio_criterio():
    """
    GUARDIA (vale antes y despues): el n del MARCO sale de 'n_manning_cajon'
    (Tabla B.1 del HDS-5 [C] en el archivo), no de la Tabla Nº 09 del tubo.
    """
    marco = M2.catalogo(CONCRETO, forma=M2.FormaSeccion.RECTANGULAR)
    assert (marco.n_min, marco.n_max) == cn.MANNING_CAJON_HDS5["concrete_boxes"]


def test_a_la_validacion_de_sensibilidad_barre_la_columna():
    from tests.apoyo import sensibilidad as S
    barridos = [b for b in S.BARRIDOS if b.clave == COLUMNA]
    assert barridos and barridos[0].grupo == S.GRUPO_CONDUCTO
    assert S.ventana_legible(COLUMNA) == ("columna_normal", "n_unico_hds5")
    documento = (RAIZ / "docs" / "validacion_sensibilidad.md").read_text(
        encoding="utf-8")
    assert f"`{COLUMNA}`" in documento


# ===========================================================================
# (g) · los diametros son los designados por la norma de producto
# ===========================================================================

@pytest.mark.xfail(strict=True, reason="VE-2 (g): las series no son [N]")
def test_g_las_series_designadas_son_las_de_la_norma_de_producto():
    designados = cn.DIAMETROS_DESIGNADOS_MM
    for material in ("concreto_reforzado", "tmc", "hdpe"):
        assert designados[material] == \
            CP11_SERIES_NOMINALES[material]["serie_mm"], material
    # Las citas que las sostienen existen en el registro.
    for material, citas in cn.CITAS_DIAMETROS_DESIGNADOS.items():
        assert material in designados
        for cita_id in citas:
            _reg().cita(cita_id)
    # NO hay guardia de centimetro: estos son designados normativos.
    for mm in (375, 525, 675, 825):
        assert mm in designados["concreto_reforzado"], mm


@pytest.mark.xfail(strict=True, reason="VE-2 (g): la tabla no esta transcrita")
def test_g_el_equivalente_ingles_de_M170M_y_su_aritmetica():
    from src.constantes_fisicas import PULGADA_EN_MM
    equivalente = cn.EQUIVALENTE_INGLES_M170M
    assert equivalente[1050] == (42, 1067)
    assert equivalente[900] == (36, 914)
    assert equivalente[2700] == (108, 2743)
    # La columna en mm es la pulgada convertida, redondeada al milimetro: es
    # la comprobacion interna que sostiene las celdas corregidas.
    for designado, (pulgadas, mm) in equivalente.items():
        assert round(pulgadas * PULGADA_EN_MM) == mm, designado
    # Y la columna de designados es la serie de la Tabla 5 (escaneo real).
    serie_t5 = cn.DIAMETROS_DESIGNADOS_MM["concreto_reforzado"]
    assert tuple(sorted(equivalente)) == tuple(d for d in serie_t5 if d <= 2700)


@pytest.mark.xfail(strict=True, reason="VE-2 (g): la cita 12.1 no existe")
def test_g_la_opcion_del_fabricante_esta_citada():
    reg = _reg()
    cita = reg.cita("AASHTO_M170M.12.1")
    assert cita.pagina_impresa == "M 170M-19" and cita.pagina_pdf == 19
    assert cita.caracter is Caracter.PERMISO
    assert cita.verificado.metodo is MetodoDeVerificacion.IMAGEN
    assert ("At the manufacturer's option the design diameter shall be the "
            "designated diameter or the converted English diameter"
            in cita.texto_literal.texto)
    tabla = reg.tabla("AASHTO_M170M.T6")
    assert tabla.erratas and all(reg.discrepancia(e).viva for e in tabla.erratas)


def test_g_guardia_los_escalones_de_archivo_son_designados_para_su_material():
    """
    GUARDIA (vale antes y despues), y es el paso 14 del prompt: ANTES de
    poner la guardia se comprueba que los trece escalones de la progresion
    de ARCHIVO son designados para cada material que los usa (13 el
    concreto, 9 el TMC hasta su tope de corrugacion, 5 el HDPE). Si uno no lo
    fuera, (g) no se implementaba. Se mide contra el DORADO de CP11 (copia
    independiente de las series transcritas).
    """
    for material, tipo, n in (("concreto_reforzado", CONCRETO, 13),
                              ("tmc", TMC, 9), ("hdpe", HDPE, 5)):
        recorrido = _recorrido(tipo)
        assert recorrido == ARCHIVO[:n], material
        serie = CP11_SERIES_NOMINALES[material]["serie_mm"]
        for D in recorrido:
            assert round(float(D) * 1000) in serie, (material, D)


@pytest.mark.xfail(strict=True, reason="VE-2 (g): M2 no rechaza el escalon")
@pytest.mark.parametrize("tipo", [CONCRETO, TMC, HDPE], ids=lambda t: t.value)
def test_g_un_escalon_no_designado_se_rechaza_nombrando_el_criterio(tipo):
    # 0.90 + 0.075 m: el 0.975 no es designado en ninguna de las tres normas.
    with declarados({M2.CRITERIO_DIAMETROS: {"inicio": 0.90, "paso": 0.075}}):
        admitidos, exc = _recorrido_hasta_el_rechazo(tipo)
    assert admitidos == ["0.9"]
    assert exc is not None and exc.campo == M2.CRITERIO_DIAMETROS
    assert "0.975" in str(exc) and "designad" in str(exc)


@pytest.mark.xfail(strict=True, reason="VE-2 (g): M2 no rechaza el escalon")
@pytest.mark.parametrize("tipo, admitidos", [
    # 0.375 + 0.075 m: hasta 0.90 los de M 170M son todos designados; en M 36
    # el 525 no existe (la serie salta de 450 a 500); en M 294 el 825 no.
    (CONCRETO, ["0.375", "0.45", "0.525", "0.6", "0.675", "0.75", "0.825",
                "0.9"]),
    (TMC, ["0.375", "0.45"]),
    (HDPE, ["0.375", "0.45", "0.525", "0.6", "0.675", "0.75"]),
], ids=["concreto", "tmc", "hdpe"])
def test_g_la_guardia_es_por_material_y_no_de_centimetro(tipo, admitidos):
    with declarados({M2.CRITERIO_DIAMETROS: {"inicio": 0.375, "paso": 0.075}}):
        recorridos, exc = _recorrido_hasta_el_rechazo(tipo)
    assert recorridos == admitidos
    assert exc is not None and exc.campo == M2.CRITERIO_DIAMETROS


@pytest.mark.xfail(strict=True, reason="VE-2 (g): M2 no rechaza el escalon")
def test_g_sin_la_eleccion_el_concreto_rechaza_la_serie_de_6_in():
    with declarados({M2.CRITERIO_DIAMETROS: SERIE_6_IN}):
        admitidos, exc = _recorrido_hasta_el_rechazo(CONCRETO)
    assert admitidos == []
    assert exc.campo == M2.CRITERIO_DIAMETROS
    assert DIAMETRO_DE_DISENO in str(exc) and "0.9144" in str(exc)


@pytest.mark.xfail(strict=True, reason="VE-2 (g): el criterio no existe")
def test_g_con_la_eleccion_el_concreto_recorre_la_serie_de_6_in_tal_cual():
    with declarados({M2.CRITERIO_DIAMETROS: SERIE_6_IN,
                     DIAMETRO_DE_DISENO: "designado_o_ingles_convertido"}):
        assert _recorrido(CONCRETO) == SEIS_IN_CONCRETO
        # La progresion de archivo, con la eleccion declarada, sigue pasando:
        # «designated diameter OR the converted English diameter».
    with declarados({DIAMETRO_DE_DISENO: "designado_o_ingles_convertido"}):
        assert _recorrido(CONCRETO) == ARCHIVO


@pytest.mark.xfail(strict=True, reason="VE-2 (g): el criterio no existe")
@pytest.mark.parametrize("tipo", [TMC, HDPE], ids=lambda t: t.value)
def test_g_el_ingles_convertido_es_solo_del_concreto(tipo):
    with declarados({M2.CRITERIO_DIAMETROS: SERIE_6_IN,
                     DIAMETRO_DE_DISENO: "designado_o_ingles_convertido"}):
        admitidos, exc = _recorrido_hasta_el_rechazo(tipo)
    assert admitidos == [] and exc.campo == M2.CRITERIO_DIAMETROS
    assert "0.9144" in str(exc)


@pytest.mark.xfail(strict=True, reason="VE-2 (g): el criterio no existe")
def test_g_el_criterio_tiene_su_ficha_de_perfil_y_lo_lee_el_concreto():
    c = ca.criterio(DIAMETRO_DE_DISENO)
    assert c.etiqueta == "A" and c.nivel == NIVEL_PERFIL
    assert c.forma == ca.FORMA_CATEGORIA and c.valor == "designado"
    assert set(c.sensibilidad) == {"designado", "designado_o_ingles_convertido"}
    assert "12.1" in c.fuente and "M 170M" in c.fuente
    ca.reiniciar_usos()
    _recorrido(CONCRETO)
    assert DIAMETRO_DE_DISENO in ca.criterios_usados()
    ca.reiniciar_usos()
    _recorrido(TMC), _recorrido(HDPE)
    assert DIAMETRO_DE_DISENO not in ca.criterios_usados()


def test_g_guardia_el_inicio_negativo_lo_sigue_rechazando_la_seccion():
    """
    GUARDIA (vale antes y despues): la rama de error de la linea base
    (`regenerar.sh`, corrida 3) declara un inicio de -0.90 m, y lo rechaza
    la hidraulica con «el diametro debe ser positivo» sobre el dato 'D'
    (`cli_rama_error.txt`). La guardia de (g) no lo intercepta: un escalon
    no positivo no es un diametro, y la linea base no se mueve.
    """
    with declarados({M2.CRITERIO_DIAMETROS: {"inicio": -0.90, "paso": 0.15}}):
        for tipo in (CONCRETO, TMC, HDPE):
            assert M2.siguiente_diametro(tipo) == pytest.approx(
                -0.90, rel=REL_TRANSPORTE)


@pytest.mark.xfail(strict=True, reason="VE-2: las fichas no estan escritas")
def test_las_fichas_ve2_a_y_ve2_g_y_vE1_02_marcada():
    fichas = _fichas()
    assert any(k.startswith("VE2-A") for k in fichas), sorted(fichas)[-5:]
    assert any(k.startswith("VE2-G") for k in fichas)
    ve1_02 = fichas["VE1-02"]
    assert "Cerrado (VE-2)" in ve1_02
    for letra in ("(a)", "(g)"):
        assert any(letra in linea and "Cerrado (VE-2)" in linea
                   for linea in ve1_02.splitlines()), letra


@pytest.mark.xfail(strict=True, reason="VE-2: los recuentos son de 141")
def test_el_censo_suma_los_dos_criterios_nuevos():
    assert {COLUMNA, DIAMETRO_DE_DISENO} <= set(ca.CRITERIOS)
    assert len(ca.CRITERIOS) >= 143
