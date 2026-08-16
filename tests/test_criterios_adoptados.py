"""
tests/test_criterios_adoptados.py
=================================
El test central de este archivo es el que exige la regla de arquitectura:
`valor()` sobre un criterio pendiente LANZA, no devuelve un default.

Rellenar un vacio en silencio es el peor error posible en este proyecto; si
alguna vez alguien "arregla" la excepcion devolviendo 0, None o un valor
plausible, estos tests lo detienen.

Valores de referencia: tests/fixtures/casos_patron.py (no se recalculan aqui).
"""

import pytest

import criterios_adoptados as ca
from criterios_adoptados import (CRITERIOS, criterio, criterios_sin_valor,
                                 parametros_sensibilizables, reporte_criterios,
                                 valor)
from modelos import CriterioPendienteError, ErrorProyecto
from tests.fixtures.casos_patron import (CP2_GEOMETRIA_MANNING,
                                         CP7_CADENA_SISMICA,
                                         CP8_CONTROL_SALIDA)


CLAVES_PENDIENTES = criterios_sin_valor()

# Anexo A - indice de criterios no normativos. Cada fila de esa tabla debe
# tener su entrada declarada aqui; si se agrega una fila al Anexo A y no al
# modulo, este test lo delata.
CLAVES_DEL_ANEXO_A = {
    "PGA_roca_B",
    "clase_sitio",
    "F_pga",
    "factor_muro",
    "k_v",
    "Mw_licuefaccion",
    "hds5_embocadura_hdpe",
    "n_manning_hdpe",
    "v_max_hdpe",
    "v_max_tmc",
    "diametros_normalizados",
    "HW_D_max",
    "resguardo_HW_subrasante",
    "TW_receptor",
    "long_max_cuneta",
    "phi_relleno_trasdos",
    "c_phi_fundacion",
    "capacidad_portante_adm",
    "espesor_proteccion_salida",
    "angulo_aletas",
    "homogeneidad_serie_fen",
}


@pytest.fixture(autouse=True)
def _aisla_registro_de_uso():
    """
    El registro de invocaciones es estado global del modulo. Se aisla por test
    para que el orden de ejecucion no altere `reporte_criterios(solo_usados)`.
    """
    previo = set(ca._USADOS)
    ca._USADOS.clear()
    yield
    ca._USADOS.clear()
    ca._USADOS.update(previo)


# ---------------------------------------------------------------------------
# Lo que exige la regla: un criterio pendiente detiene el calculo
# ---------------------------------------------------------------------------

def test_hay_criterios_pendientes_declarados():
    """Si algun dia se llenan todos, este test avisa para revisar los tableros."""
    assert CLAVES_PENDIENTES, (
        "Ningun criterio quedo sin valor. Revisa que los tableros 1, 2 y 3 se "
        "hayan cerrado de verdad y no por descuido."
    )


@pytest.mark.parametrize("clave", CLAVES_PENDIENTES)
def test_criterio_pendiente_lanza_error_y_no_devuelve_default(clave):
    """
    valor() sobre un criterio con valor None lanza CriterioPendienteError.
    NO devuelve 0, ni None, ni un valor plausible: detiene el calculo.
    """
    try:
        devuelto = valor(clave)
    except CriterioPendienteError as exc:
        assert exc.clave == clave
        # El criterio sigue vacio: nadie lo relleno al pasar por aqui.
        assert criterio(clave).valor is None
    else:
        pytest.fail(
            f"valor('{clave}') devolvio {devuelto!r} en vez de lanzar "
            "CriterioPendienteError. Un vacio normativo relleno en silencio "
            "es el peor error posible en este proyecto."
        )


def test_el_mensaje_permite_a_la_gui_decir_falta_declarar():
    """La GUI muestra 'falta declarar: <clave>', no un traceback."""
    clave = "Mw_licuefaccion"
    with pytest.raises(CriterioPendienteError) as exc:
        valor(clave)
    assert exc.value.mensaje_gui == f"falta declarar: {clave}"
    assert clave in str(exc.value)
    assert criterio(clave).concepto in str(exc.value)


def test_la_excepcion_es_de_la_taxonomia_del_proyecto():
    """No una Exception generica: la GUI necesita distinguirla de un crash."""
    assert issubclass(CriterioPendienteError, ErrorProyecto)
    assert CriterioPendienteError is not Exception
    with pytest.raises(ErrorProyecto):
        valor("TW_receptor")


def test_una_clave_no_declarada_no_se_inventa():
    """Usar un parametro sin declararlo antes aqui es un error, no un default."""
    with pytest.raises(KeyError):
        valor("parametro_que_nadie_declaro")


def test_el_criterio_pendiente_queda_registrado_como_invocado():
    """
    M11 debe poder decir que el calculo intento usarlo. El registro ocurre
    antes de lanzar.
    """
    with pytest.raises(CriterioPendienteError):
        valor("phi_relleno_trasdos")
    assert "phi_relleno_trasdos" in ca._USADOS


# ---------------------------------------------------------------------------
# Comportamiento normal
# ---------------------------------------------------------------------------

def test_criterio_con_valor_lo_devuelve_y_registra_el_uso():
    devuelto = valor("long_max_cuneta")
    assert devuelto == pytest.approx(criterio("long_max_cuneta").valor)
    assert "long_max_cuneta" in ca._USADOS


def test_el_reporte_lista_solo_los_criterios_usados():
    valor("long_max_cuneta")
    texto = reporte_criterios(solo_usados=True)
    assert "long_max_cuneta" in texto
    assert "espesor_proteccion_salida" not in texto


def test_el_reporte_imprime_los_vacios_en_bloque_aparte():
    """Sec. 0.7: los pendientes se imprimen aparte, no mezclados."""
    texto = reporte_criterios(solo_usados=False)
    assert "VACIOS SIN VALOR" in texto
    for clave in CLAVES_PENDIENTES:
        assert clave in texto


# ---------------------------------------------------------------------------
# Cobertura del Anexo A y coherencia de etiquetas
# ---------------------------------------------------------------------------

def test_estan_declarados_todos_los_items_del_anexo_A():
    faltan = CLAVES_DEL_ANEXO_A - set(CRITERIOS)
    assert not faltan, f"Items del Anexo A sin declarar: {sorted(faltan)}"


def test_las_etiquetas_son_de_la_convencion():
    validas = {"N", "N->", "C", "A"}
    malas = {k: c.etiqueta for k, c in CRITERIOS.items() if c.etiqueta not in validas}
    assert not malas, f"Etiquetas fuera de la convencion: {malas}"


def test_todo_criterio_sin_valor_declara_de_donde_saldra():
    """Un vacio sin ruta de salida es un vacio que nadie va a cerrar."""
    for clave in CLAVES_PENDIENTES:
        c = criterio(clave)
        assert c.fuente, f"'{clave}' no declara fuente"
        assert c.justificacion, f"'{clave}' no declara por que hace falta"


def test_los_parametros_sensibilizables_traen_rango_de_dos_extremos():
    for clave, rango in parametros_sensibilizables().items():
        assert len(rango) == 2, f"'{clave}' no declara un rango de dos extremos"
        assert rango[0] <= rango[1], f"'{clave}' tiene el rango invertido"


# ---------------------------------------------------------------------------
# Contraste contra los casos patron
# ---------------------------------------------------------------------------

def test_la_cadena_sismica_reproduce_CP7():
    """
    CP-7 verifica que la cadena este desagregada y no con 0.50 hardcodeado:
    A_s = F_pga * PGA ; k_h = factor_muro * k_h0.
    """
    cp = CP7_CADENA_SISMICA
    assert valor("PGA_roca_B") == pytest.approx(cp["PGA"])
    assert valor("F_pga") == pytest.approx(cp["F_pga"])

    A_s = valor("PGA_roca_B") * valor("F_pga")
    assert A_s == pytest.approx(cp["A_s_esperado"])

    k_h0 = A_s                                   # Manual de Puentes, 2.8.1.1.14.2
    assert k_h0 == pytest.approx(cp["k_h0_esperado"])

    k_h = valor("factor_muro") * k_h0
    assert k_h == pytest.approx(cp["k_h_con_muro_rigido_esperado"])

    # Si el muro admitiera desplazamiento, la misma cadena debe dar 0.25.
    assert cp["factor_muro_desplazable"] * k_h0 == pytest.approx(
        cp["k_h_con_muro_desplazable_esperado"]
    )
    assert valor("k_v") == pytest.approx(cp["k_v_esperado"])


def test_el_ke_del_control_de_salida_esta_trazado_contra_CP8():
    """
    CP-8 usaba ke = 0.5 como dato fijo del fixture, sin declarar de donde
    salia. Ahora el valor tiene origen (HDS-5, square edge with headwall) y un
    unico punto de cambio: si se mueve el criterio, el caso patron deja de
    coincidir y el test lo dice.
    """
    c = criterio("ke_entrada")
    assert valor("ke_entrada") == pytest.approx(CP8_CONTROL_SALIDA["ke"])
    assert c.etiqueta == "C"
    assert "square edge" in c.fuente


def test_el_n_de_hdpe_es_un_rango_y_no_un_valor_puntual():
    """
    Un valor puntual rompe la regla de doble n (Sec. 4.1.1): con un solo
    numero, capacidad y velocidad usan la misma rugosidad y una de las dos
    deja de ser conservadora. El rango es el del concreto, por analogia.
    """
    n = valor("n_manning_hdpe")
    assert isinstance(n, tuple) and len(n) == 2
    n_min, n_max = n
    assert n_min < n_max
    assert n_min == pytest.approx(CP2_GEOMETRIA_MANNING["n_min"])
    assert n_max == pytest.approx(CP2_GEOMETRIA_MANNING["n_max"])
