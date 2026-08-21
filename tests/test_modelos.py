"""
tests/test_modelos.py
=====================
Los tipos que fluyen entre modulos. Se verifica lo que otros modulos van a dar
por supuesto: que PuntoCritico reproduce el encabezado de Sec. 1.2, que la
geometria circular es coherente, que Verificacion nunca degenera en un bool
desnudo y que la taxonomia de excepciones esta completa.

Valores de referencia: tests/fixtures/casos_patron.py.
"""

import csv
import dataclasses
import math
from pathlib import Path

import pytest

import constantes_normativas as CN
from modelos import (CompatibilidadGeometrica, ConstantesHDS5,
                     ControlGobernante, CriterioPendienteError,
                     DatoFaltanteError, DisenoNoFactibleError, ErrorProyecto,
                     Familia, Geometria, Material, PasoDiseno, PuntoCritico,
                     ReferenciaNormativa, ResultadoHidraulico, ResultadoPunto,
                     TamizadoRasante, TipoMaterial, Verificacion)
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING, CP8_CONTROL_SALIDA

DIRECTORIO_TESTS = Path(__file__).resolve().parent
CSV_VALIDO = DIRECTORIO_TESTS / "ejemplo_puntos.csv"
CSV_INVALIDO = DIRECTORIO_TESTS / "ejemplo_puntos_invalido.csv"

# Campos de PuntoCritico que M0 deriva y que no son columnas del CSV (Sec. 1.2):
# la notacion vial de la progresiva y la marca de datos pendientes de terceros.
DERIVADOS = {"progresiva_display", "pendientes_externos"}


def _encabezado(ruta: Path):
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))


def _punto(**cambios) -> PuntoCritico:
    """Punto de prueba con la fila A-01 del CSV de ejemplo como base."""
    base = dict(
        id="A-01",
        progresiva_km=0.380,
        progresiva_display="0+380",
        familia=Familia.A,
        Q_m3s=CP2_GEOMETRIA_MANNING["Q_con_n_max_esperado"],
        area_ha=850.0,
        S_cauce=0.006,
        cota_terreno=42.10,
        cota_rasante=44.20,
        cota_subrasante=44.05,
        cbr_subrasante=8.5,
        esviaje_grados=15.0,
        ancho_plataforma=9.60,
        cota_fondo_receptor=41.30,
        Q_receptor_m3s=None,       # Tablero 3.1
        cota_TW=None,              # Tablero 3.1
        sucs_fundacion="SM",
        NF_profundidad_m=None,     # lo da el estudio geotecnico, por punto
    )
    base.update(cambios)
    return PuntoCritico(**base)


def _geometria_CP2() -> Geometria:
    c = CP2_GEOMETRIA_MANNING
    return Geometria(
        D=c["D"],
        theta=c["theta_esperado"],
        A=c["A_esperado"],
        P=c["P_esperado"],
        R=c["R_esperado"],
        y=c["y_sobre_D"] * c["D"],
    )


# ---------------------------------------------------------------------------
# PuntoCritico: el contrato con el CSV
# ---------------------------------------------------------------------------

def test_los_campos_reproducen_el_encabezado_de_la_seccion_1_2():
    """
    Mismo nombre y mismo orden: M0 no renombra columnas. El unico campo que no
    es columna del CSV es progresiva_display, que M0 deriva del mismo string
    de entrada que progresiva_km.
    """
    campos = [f.name for f in dataclasses.fields(PuntoCritico)]
    assert [c for c in campos if c not in DERIVADOS] == _encabezado(CSV_VALIDO)


def test_la_progresiva_vial_acompana_a_la_numerica():
    """
    '0+380' y 0.380 salen del mismo dato de entrada y deben viajar juntas: la
    memoria se cita en progresivas, no en kilometros decimales.
    """
    campos = [f.name for f in dataclasses.fields(PuntoCritico)]
    assert campos.index("progresiva_display") == campos.index("progresiva_km") + 1

    punto = _punto()
    assert punto.progresiva_display == "0+380"
    assert punto.progresiva_km == pytest.approx(0.380)
    assert str(punto.progresiva_km) not in punto.progresiva_display


def test_el_csv_invalido_es_el_que_omite_una_columna_obligatoria():
    """Documenta para que sirve el fixture de M0: le falta cota_subrasante."""
    columnas = {f.name for f in dataclasses.fields(PuntoCritico)} - DERIVADOS
    faltantes = columnas - set(_encabezado(CSV_INVALIDO))
    assert faltantes == {"cota_subrasante"}


def test_exigir_lanza_dato_faltante_en_vez_de_asumir_un_valor():
    punto = _punto()
    with pytest.raises(DatoFaltanteError) as exc:
        punto.exigir("cota_TW")
    assert exc.value.campo == "cota_TW"
    assert exc.value.id_punto == punto.id


def test_exigir_devuelve_el_dato_cuando_existe():
    punto = _punto()
    assert punto.exigir("Q_m3s") == pytest.approx(punto.Q_m3s)


def test_exigir_rechaza_un_campo_que_no_es_del_encabezado():
    with pytest.raises(AttributeError):
        _punto().exigir("caudal")


def test_el_punto_critico_es_inmutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        _punto().cota_rasante = 0.0


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------

def test_la_geometria_reproduce_CP2():
    c = CP2_GEOMETRIA_MANNING
    g = _geometria_CP2()
    tol = c["tolerancia_geometria"]
    assert g.y_sobre_D == pytest.approx(c["y_sobre_D"], rel=tol)
    # A, P y R vienen redondeados a 5 decimales en el fixture: la coherencia
    # R = A/P solo puede exigirse con tolerancia absoluta, no relativa.
    assert g.R == pytest.approx(g.A / g.P, abs=tol)


def test_el_ancho_superficial_es_consistente_con_el_tirante():
    """
    T = D*sen(theta/2) debe coincidir con la cuerda calculada desde el
    tirante, 2*sqrt(r^2 - (y-r)^2). M4 lo usa en Q^2*T/(g*A^3) = 1.
    """
    g = _geometria_CP2()
    radio = g.D / 2
    cuerda = 2 * math.sqrt(radio**2 - (g.y - radio) ** 2)
    assert g.T == pytest.approx(cuerda, rel=CP2_GEOMETRIA_MANNING["tolerancia_geometria"])


# ---------------------------------------------------------------------------
# Material: la regla de doble n
# ---------------------------------------------------------------------------

def _material_concreto() -> Material:
    n_min, n_max = CN.MANNING["concreto_recto"]
    return Material(
        tipo=TipoMaterial.CONCRETO_REFORZADO,
        nombre="Concreto reforzado",
        n_min=n_min,
        n_max=n_max,
        D_max=CN.D_MAX["concreto_reforzado"],
        norma_producto="ASTM C76 / AASHTO M170",
        hds5=ConstantesHDS5.desde_dict(
            CN.HDS5_INLET["circular_concreto_square_edge_headwall"]
        ),
        v_max_rango=CN.V_MAX["concreto"],
        h_relleno_min=CN.H_RELLENO_MIN["concreto"],
        seccion_eg2013=CN.SECCION_EG2013["concreto_reforzado"],
    )


def test_el_material_expone_las_dos_ramas_de_n():
    m = _material_concreto()
    assert m.n_para_capacidad == pytest.approx(CP2_GEOMETRIA_MANNING["n_max"])
    assert m.n_para_velocidad == pytest.approx(CP2_GEOMETRIA_MANNING["n_min"])
    assert m.n_para_velocidad < m.n_para_capacidad


def test_la_velocidad_maxima_del_concreto_esta_tabulada():
    assert _material_concreto().v_max_definida is True


def test_las_constantes_hds5_se_construyen_desde_la_tabla_A1():
    fila = CN.HDS5_INLET["circular_concreto_square_edge_headwall"]
    constantes = ConstantesHDS5.desde_dict(fila)
    assert constantes.K == pytest.approx(fila["K"])
    assert constantes.Ks == pytest.approx(fila["Ks"])   # no se omite


# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

def _resultado_hidraulico(control: ControlGobernante) -> ResultadoHidraulico:
    c = CP2_GEOMETRIA_MANNING
    return ResultadoHidraulico(
        y_normal=c["y_sobre_D"] * c["D"],
        y_critico=c["y_sobre_D"] * c["D"] / 2,     # valor de forma, no de calculo
        V=c["V_con_n_min_esperado"],
        Q=c["Q_con_n_max_esperado"],
        HW_entrada=CP8_CONTROL_SALIDA["H_esperado_con_K_SI"],
        HW_salida=CP8_CONTROL_SALIDA["H_con_29_incorrecto"],
        control_gobernante=control,
    )


def test_HW_selecciona_el_control_que_gobierna():
    entrada = _resultado_hidraulico(ControlGobernante.ENTRADA)
    salida = _resultado_hidraulico(ControlGobernante.SALIDA)
    assert entrada.HW == pytest.approx(entrada.HW_entrada)
    assert salida.HW == pytest.approx(salida.HW_salida)


def test_la_velocidad_no_es_el_caudal_dividido_entre_el_area():
    """
    Regla de doble n: V sale de n_min y Q de n_max, asi que V*A != Q. Si algun
    dia coinciden, alguien se ahorro el calculo doble de Sec. 4.1.
    """
    c = CP2_GEOMETRIA_MANNING
    r = _resultado_hidraulico(ControlGobernante.ENTRADA)
    assert r.V * c["A_esperado"] != pytest.approx(r.Q, rel=c["tolerancia_hidraulica"])


def test_la_verificacion_no_es_un_bool_desnudo():
    g = _geometria_CP2()
    v = Verificacion(
        cumple=g.y_sobre_D <= CN.Y_SOBRE_D_MAX,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=g.y_sobre_D,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,          # umbral [N] puro
        codigo="V1",
    )
    assert not isinstance(v, bool)
    assert v.numeral
    assert v.valor_admisible == pytest.approx(CN.Y_SOBRE_D_MAX)


def test_una_verificacion_incumplida_se_reporta_como_tal():
    g = _geometria_CP2()
    excedido = g.y_sobre_D + CN.Y_SOBRE_D_MAX      # muy por encima del limite
    v = Verificacion(
        cumple=excedido <= CN.Y_SOBRE_D_MAX,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=excedido,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,
        codigo="V1",
    )
    assert v.cumple is False


def _resultado_punto(cumple: bool) -> ResultadoPunto:
    v = Verificacion(
        cumple=cumple,
        numeral="4.1.1.3.7 b)",
        valor_obtenido=CN.Y_SOBRE_D_MAX,
        valor_admisible=CN.Y_SOBRE_D_MAX,
        criterio_aplicado=None,
        codigo="V1",
    )
    return ResultadoPunto(
        punto=_punto(),
        aceptado=cumple,
        material=_material_concreto(),
        D=CN.DIAMETRO_MIN,
        resultado_hidraulico=_resultado_hidraulico(ControlGobernante.ENTRADA),
        verificaciones=(v,),
        motivo_rechazo=None if cumple else "V1: y/D por encima del maximo",
    )


def test_el_resultado_del_punto_separa_las_verificaciones_incumplidas():
    aceptado = _resultado_punto(True)
    rechazado = _resultado_punto(False)
    assert aceptado.verificaciones_incumplidas == ()
    assert len(rechazado.verificaciones_incumplidas) == 1
    assert aceptado.coherente and rechazado.coherente


def test_un_rechazo_sin_motivo_es_incoherente():
    incoherente = dataclasses.replace(_resultado_punto(False), motivo_rechazo=None)
    assert not incoherente.coherente


# ---------------------------------------------------------------------------
# Taxonomia de excepciones
# ---------------------------------------------------------------------------

def test_toda_excepcion_del_negocio_desciende_de_error_proyecto():
    for excepcion in (CriterioPendienteError, DisenoNoFactibleError,
                      DatoFaltanteError):
        assert issubclass(excepcion, ErrorProyecto)


def test_diseno_no_factible_lleva_motivo_y_delta_de_rasante():
    """Sec. 7.B: devuelve 'no factible -> subir rasante X', nunca un silencio."""
    delta = 0.35
    e = DisenoNoFactibleError(
        "HW supera la subrasante con el maximo diametro disponible",
        delta_rasante_m=delta,
        id_punto="A-01",
    )
    assert e.delta_rasante_m == pytest.approx(delta)
    assert "A-01" in str(e)
    assert "0.35" in str(e)
    assert e.motivo in str(e)


def test_diseno_no_factible_admite_no_tener_delta_de_rasante():
    e = DisenoNoFactibleError("HDPE descartado por diametro requerido")
    assert e.delta_rasante_m is None
    assert e.motivo in str(e)


def test_resultado_punto_fallido_tiene_campos_en_none_y_motivo_explicito():
    """
    Un punto no factible -- capturado por disenar_lote -- tiene aceptado=False,
    todos los campos de diseño en None y motivo_rechazo explicito. M11 lo lista
    aparte del expediente de puntos resueltos.
    """
    fallido = ResultadoPunto(
        punto=_punto(),
        aceptado=False,
        motivo_rechazo="ningun material candidato cumple la Fase 5",
    )
    assert not fallido.aceptado
    assert fallido.material is None
    assert fallido.D is None
    assert fallido.resultado_hidraulico is None
    assert fallido.verificaciones == ()
    assert fallido.coherente                   # motivo_rechazo no es None
    assert fallido.verificaciones_incumplidas == ()


# ---------------------------------------------------------------------------
# ReferenciaNormativa: la seccion propia y el numeral de la norma, separados
# ---------------------------------------------------------------------------

def test_la_referencia_normativa_separa_la_navegacion_interna_de_la_cita():
    """
    Un verificador externo leyo "Sec. 9.1 (EG-2013 num. 503.01, pag. 905)"
    como si el string entero fuese la cita, y salio a buscar una "Sec. 9.1"
    en el EG-2013. Las dos mitades tienen que poder pedirse por separado.
    """
    r = ReferenciaNormativa(
        seccion_hoja_ruta="Sec. 9.1",
        numeral_norma="EG-2013, Capitulo V, Seccion 503, num. 503.01")

    assert r.seccion_hoja_ruta == "Sec. 9.1"
    assert "Sec. 9.1" not in r.numeral_norma
    assert "503.01" in r.numeral_norma


def test_la_referencia_normativa_sigue_siendo_un_string_para_quien_la_imprime():
    """
    Es subclase de str a proposito: `Verificacion.numeral`, el escapado de
    M11 y las pruebas que hacen `numeral in memoria` no tenian que cambiar.
    """
    r = ReferenciaNormativa(seccion_hoja_ruta="Fase 10",
                            numeral_norma="num. 4.1.2.1 d), pag. 178")

    assert isinstance(r, str)
    assert "4.1.2.1" in r
    assert "hoja de ruta" in str(r)          # la mitad interna, etiquetada
    assert str(r).startswith("num. 4.1.2.1")  # la cita verificable, delante


# ===========================================================================
# Verificaciones diferidas (cumple=None) en los agregados
# ---------------------------------------------------------------------------
# Sitios 3, 4 y 11 del inventario del paso 7: en todo agregado que filtra
# incumplidas, el filtro es `cumple is False`. None es falsy, y un
# `not v.cumple` arrastraria un diferido como incumplimiento en silencio.
# ===========================================================================

def _v(cumple, codigo="V1"):
    return Verificacion(
        cumple=cumple, numeral="Fase 5", valor_obtenido=None,
        valor_admisible=None, criterio_aplicado=None, codigo=codigo,
        nota_diferida="diferida al expediente" if cumple is None else None)


def test_resultado_punto_una_diferida_no_es_incumplimiento():
    """Sitio 3: un punto aceptado con diferidas es coherente."""
    r = ResultadoPunto(punto=_punto(), aceptado=True,
                       verificaciones=(_v(True), _v(None, "V5"), _v(None, "V8")))
    assert r.verificaciones_incumplidas == ()
    assert r.coherente


def test_resultado_punto_solo_las_false_son_incumplidas():
    r = ResultadoPunto(punto=_punto(), aceptado=False, motivo_rechazo="V1",
                       verificaciones=(_v(False), _v(None, "V5")))
    assert [v.codigo for v in r.verificaciones_incumplidas] == ["V1"]


def test_paso_diseno_una_diferida_no_causa_el_descarte():
    """Sitio 4: la traza de M11 no puede acusar a una diferida."""
    paso = PasoDiseno(material="HDPE", D=0.60, aceptado=False, motivo="V1",
                      verificaciones=(_v(False), _v(None, "V5")))
    assert [v.codigo for v in paso.incumplidas] == ["V1"]


def _tamizado_factible():
    return TamizadoRasante(
        cota_rasante_min=44.0, cota_rasante_actual=44.2,
        cota_por_recubrimiento=44.0, cota_por_resguardo=43.8,
        condicion_gobernante="recubrimiento", cota_entrada=42.0,
        cota_clave=42.6, D_supuesto=0.6, HW=0.5, h_recubrimiento=0.6,
        espesor_paquete=0.15, resguardo=0.5, factible=True,
        delta_rasante_m=0.0, criterio_recubrimiento="h_relleno_min",
        criterio_resguardo="resguardo_HW_subrasante")


def test_compatibilidad_geometrica_una_diferida_no_la_hace_infactible():
    """
    Sitio 11 (dormido, defensa): G1 y G2 hoy nunca se difieren, pero si
    algun dia una llegara con cumple=None, el punto no puede salir
    infactible -- `exigir_factible` lanzaria DisenoNoFactibleError por una
    verificacion que nadie evaluo.
    """
    compat = CompatibilidadGeometrica(
        punto=_punto(), D=0.6, tamizado=_tamizado_factible(), longitud=12.0,
        proyeccion_taludes=3.0, factor_esviaje=1.03, altura_terraplen=2.1,
        S_conducto=0.01, cota_entrada=42.0, cota_salida=41.88, caida=0.12,
        verificaciones=(_v(True, "G1"), _v(None, "G2")))
    assert compat.verificaciones_incumplidas == ()
    assert compat.factible
    compat.exigir_factible()          # no lanza
