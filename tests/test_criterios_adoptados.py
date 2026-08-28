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

from pathlib import Path

import pytest

import criterios_adoptados as ca
import datos_sitio as ds
from constantes_normativas import (F_PGA_TABLA,
                                   REDUCCION_KH_POR_DESPLAZAMIENTO)
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
# 'PGA_roca_B' salio del Anexo A: es un dato de sitio [S] y vive en
# datos_sitio.py. 'factor_muro' se partio en el unico valor [N] del numeral
# (constantes_normativas.REDUCCION_KH_POR_DESPLAZAMIENTO) y la declaracion [A]
# de si se aplica ('factor_muro_eleccion'). F_pga siguio el mismo camino: la
# tabla [N] completa en constantes_normativas.F_PGA_TABLA y las FILAS sobre
# las que se lee en el criterio, mas la lectura de sus rotulos extremos, que
# la tabla no resuelve ('F_pga_lectura_columna_extrema').
CLAVES_DEL_ANEXO_A = {
    "clase_sitio",
    "PERFIL_SUELO_PRESUNTO",
    "F_pga",
    "F_pga_lectura_columna_extrema",
    "factor_muro_eleccion",
    "k_v",
    "gamma_EQ",
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
    """Cinco etiquetas, no cuatro: [S] entro con el dato de sitio."""
    validas = {"N", "N->", "S", "C", "A"}
    assert set(ca.ETIQUETAS_VALIDAS) == validas
    malas = {k: c.etiqueta for k, c in CRITERIOS.items() if c.etiqueta not in validas}
    assert not malas, f"Etiquetas fuera de la convencion: {malas}"


def test_ningun_criterio_adoptado_lleva_ya_la_etiqueta_N():
    """
    Este archivo es el de lo que NO es exigencia normativa verificada. Las
    tres entradas que llevaban [N] eran justo las mal clasificadas del
    manifiesto: el PGA (dato de sitio), el factor de muro (tabla normativa
    mezclada con la eleccion) y el NF (medicion por punto). Si vuelve a
    aparecer una [N] aqui, es que alguien volvio a meter una constante
    universal en el archivo equivocado.
    """
    con_N = {k for k, c in CRITERIOS.items() if c.etiqueta == "N"}
    assert not con_N, (
        f"Criterios con etiqueta [N] en criterios_adoptados.py: {sorted(con_N)}. "
        "Una exigencia normativa con numeral verificado va a "
        "constantes_normativas.py")


def test_un_criterio_S_declara_trazabilidad_y_no_sensibilidad():
    """
    El campo que defiende un [S] no es el que defiende un [A]: un [A] muestra
    el rango que se pudo elegir, y un [S] no tiene rango -- muestra como
    repetir la lectura.
    """
    de_sitio = {k: c for k, c in CRITERIOS.items() if c.etiqueta == "S"}
    assert de_sitio, "ningun criterio [S] declarado: revisa la taxonomia"
    for clave, c in de_sitio.items():
        assert c.trazabilidad, f"'{clave}' es [S] y no declara trazabilidad"
        assert c.sensibilidad is None, (
            f"'{clave}' es [S] y declara sensibilidad: un hecho de sitio no "
            "tiene rango que elegir")


def test_solo_los_S_declaran_trazabilidad():
    intrusos = {k: c.etiqueta for k, c in CRITERIOS.items()
                if c.trazabilidad and c.etiqueta != "S"}
    assert not intrusos, f"Trazabilidad fuera de un [S]: {intrusos}"


def test_la_guardia_de_coherencia_rechaza_un_S_sin_trazabilidad(monkeypatch):
    """La guardia no es decorativa: si se rompe la regla, el modulo no carga."""
    monkeypatch.setitem(
        CRITERIOS, "criterio_de_prueba",
        ca.Criterio(valor=1.0, etiqueta="S", concepto="c",
                    justificacion="j", fuente="f"))
    with pytest.raises(ValueError, match="trazabilidad"):
        ca._coherencia_de_etiquetas()


def test_el_perfil_de_suelo_es_referencia_declarada_y_no_calculo():
    """
    Salio de constantes_normativas.py, donde figuraba como [N]. Hoy no lo
    invoca ningun modulo de calculo -- lo dice su propia trazabilidad -- y se
    conserva declarado porque es la presuncion geotecnica en la que se apoya
    'clase_sitio'.
    """
    c = criterio("PERFIL_SUELO_PRESUNTO")
    assert c.etiqueta == "S"
    assert "SPT" in c.reemplazado_por
    assert "REFERENCIA MUERTA" in c.trazabilidad

    raiz = Path(__file__).resolve().parents[1]
    invocaciones = [
        ruta.name for ruta in (raiz / "src" / "modulos").glob("*.py")
        if "PERFIL_SUELO_PRESUNTO" in ruta.read_text(encoding="utf-8-sig")
    ]
    assert not invocaciones, (
        f"'PERFIL_SUELO_PRESUNTO' dejo de ser referencia muerta ({invocaciones}): "
        "revisa si sigue bastando una presuncion de tramo o hace falta el dato "
        "por calicata")


def test_la_licuefaccion_y_la_clase_de_sitio_piden_profundidades_distintas():
    """
    Dos ensayos, dos profundidades, y no son intercambiables:

        PERFIL_SUELO_PRESUNTO   licuefaccion -> SPT de 15 m (E.050 Art. 38)
        clase_sitio             clase sismica -> 30 m (Vs30 / N_barra)

    'clase_sitio' decia antes que lo cerraba un SPT de ">= 15 m", que es la
    profundidad del OTRO requisito: con 15 m no se lee un Vs30. Este test
    existe para que la campana geotecnica no se programe corta.
    """
    licuefaccion = criterio("PERFIL_SUELO_PRESUNTO").reemplazado_por
    clase = criterio("clase_sitio").reemplazado_por

    assert "15 m" in licuefaccion and "Art. 38" in licuefaccion
    assert "30 m" in clase
    assert "15 m" not in clase.split("NO LO CIERRA")[0]


def test_todo_criterio_sin_valor_declara_de_donde_saldra():
    """Un vacio sin ruta de salida es un vacio que nadie va a cerrar."""
    for clave in CLAVES_PENDIENTES:
        c = criterio(clave)
        assert c.fuente, f"'{clave}' no declara fuente"
        assert c.justificacion, f"'{clave}' no declara por que hace falta"


def test_criterios_usados_registra_la_invocacion():
    """
    La lista que consume el reporte (cli.py la vuelca al JSON) es la misma que
    `reporte_criterios(solo_usados=True)` imprime: sale del registro de uso, no
    del catalogo completo.
    """
    valor("F_pga")
    usados = ca.criterios_usados()
    assert "F_pga" in usados
    assert usados == sorted(usados)
    assert set(usados) <= set(CRITERIOS)


def test_los_parametros_sensibilizables_traen_rango_de_dos_extremos():
    for clave, rango in parametros_sensibilizables().items():
        assert len(rango) == 2, f"'{clave}' no declara un rango de dos extremos"
        assert rango[0] <= rango[1], f"'{clave}' tiene el rango invertido"


# ===========================================================================
# La guardia de sensibilidad: un valor y su rango se defienden juntos
# ===========================================================================
#
# `_verificar_criterio` es el UNICO sitio que sabe que hace valida a una
# declaracion, y lo atraviesan los tres caminos por los que un criterio puede
# recibir valor: el archivo al importarse, la declaracion en caliente de la
# GUI, y la escritura permanente. Los tests de abajo entran por los tres.

def _criterio_de_prueba(**campos):
    base = dict(valor=1.0, etiqueta="A", concepto="c", justificacion="j",
                fuente="f")
    base.update(campos)
    return ca.Criterio(**base)


def test_el_valor_del_archivo_cae_dentro_de_su_propio_rango():
    """Estado de partida: ningun criterio se contradice con su rango."""
    for clave, c in CRITERIOS.items():
        if c.sensibilidad is None or c.valor is None:
            continue
        rango = ca._rango_numerico(c.sensibilidad)
        if rango is None:
            continue
        minimo, maximo = rango
        extremos = c.valor if isinstance(c.valor, (tuple, list)) else (c.valor,)
        for x in extremos:
            assert minimo <= x <= maximo, (
                f"'{clave}' vale {c.valor!r} fuera de su sensibilidad {c.sensibilidad!r}")


def test_la_guardia_rechaza_un_valor_fuera_del_rango_y_dice_la_salida():
    """
    El mensaje no puede quedarse en 'tu numero esta mal': quien declaro el
    rango pudo ser el equivocado, y el revisor necesita saber que las dos
    cosas se defienden juntas.
    """
    malo = _criterio_de_prueba(valor=99.0, sensibilidad=(3.0, 6.0))
    with pytest.raises(ValueError) as exc:
        ca._verificar_criterio("criterio_de_prueba", malo)
    mensaje = str(exc.value)
    assert "fuera del rango" in mensaje
    assert "corrigelo en criterios_adoptados.py" in mensaje
    assert "se defienden juntos en la memoria" in mensaje


def test_la_guardia_rechaza_el_rango_invertido():
    with pytest.raises(ValueError, match="invertido"):
        ca._verificar_criterio(
            "criterio_de_prueba", _criterio_de_prueba(valor=None, sensibilidad=(6.0, 3.0)))


def test_un_bool_no_se_cuela_como_numero_dentro_del_rango():
    """
    `bool` es subclase de `int` en Python: sin excluirlo, True pasaria por un
    1.0 valido dentro de cualquier rango que contenga al 1.
    """
    assert not ca._es_real(True)
    with pytest.raises(ValueError, match="no es un numero"):
        ca._verificar_criterio(
            "criterio_de_prueba", _criterio_de_prueba(valor=True, sensibilidad=(0.9, 1.0)))


def test_un_valor_no_numerico_contra_un_rango_numerico_se_rechaza():
    with pytest.raises(ValueError, match="no es un numero"):
        ca._verificar_criterio(
            "criterio_de_prueba", _criterio_de_prueba(valor="tres", sensibilidad=(3.0, 6.0)))


def test_un_valor_de_dos_extremos_se_valida_extremo_a_extremo():
    """
    La regla de doble n de Sec. 4.1.1: `n_manning_hdpe` es un par, no un
    numero. Los DOS extremos tienen que caer dentro del rango.
    """
    ca._verificar_criterio(
        "criterio_de_prueba",
        _criterio_de_prueba(valor=(0.011, 0.012), sensibilidad=(0.010, 0.013)))
    with pytest.raises(ValueError, match="fuera del rango"):
        ca._verificar_criterio(
            "criterio_de_prueba",
            _criterio_de_prueba(valor=(0.011, 0.020), sensibilidad=(0.010, 0.013)))


# ---------------------------------------------------------------------------
# Sensibilidad simbolica: se declara, no se evalua, no se coacciona
# ---------------------------------------------------------------------------

def test_una_sensibilidad_simbolica_se_acepta_y_no_se_evalua():
    """
    Un rango en funcion de otra variable no tiene dos numeros que recorrer.
    La guardia lo respeta tal como esta escrito -- no le hace float(), no lo
    fuerza a un formato que no tiene y no lo descarta en silencio.
    """
    simbolico = _criterio_de_prueba(
        valor="lo que resulte", sensibilidad="2*phi_relleno_trasdos/3")
    ca._verificar_criterio("criterio_de_prueba", simbolico)   # no lanza
    assert ca._rango_numerico(simbolico.sensibilidad) is None


def test_una_tupla_con_un_extremo_simbolico_es_simbolica_entera():
    """La discriminacion es por FORMA, no por nombre de criterio."""
    assert ca._rango_numerico((0.0, "2*phi/3")) is None
    ca._verificar_criterio(
        "criterio_de_prueba",
        _criterio_de_prueba(valor=None, sensibilidad=(0.0, "2*phi/3")))


def test_la_sensibilidad_vacia_se_rechaza():
    """O se declara el rango que se pudo elegir, o no se declara el campo."""
    with pytest.raises(ValueError, match="vacia"):
        ca._verificar_criterio(
            "criterio_de_prueba", _criterio_de_prueba(valor=None, sensibilidad=()))


def test_el_barrido_solo_recibe_los_rangos_que_puede_recorrer(monkeypatch):
    """
    Una sensibilidad simbolica se imprime en la memoria pero no se puede
    barrer sin resolver antes la variable de la que depende.
    """
    monkeypatch.setitem(
        CRITERIOS, "criterio_de_prueba",
        _criterio_de_prueba(valor=None, sensibilidad="2*phi_relleno_trasdos/3"))
    assert "criterio_de_prueba" not in parametros_sensibilizables()
    assert "criterio_de_prueba" in parametros_sensibilizables(solo_numericos=False)


# ---------------------------------------------------------------------------
# El mismo rasero por los tres caminos de declaracion
# ---------------------------------------------------------------------------

@pytest.fixture
def _limpia_overrides():
    yield
    ca.limpiar_valores_dinamicos()


def test_la_declaracion_en_caliente_pasa_por_la_misma_guardia(_limpia_overrides):
    """La GUI no es una puerta trasera al rango declarado."""
    with pytest.raises(ValueError, match="fuera del rango"):
        ca.establecer_valor_dinamico("v_max_concreto_eleccion", 99.0)
    assert "v_max_concreto_eleccion" not in ca.valores_dinamicos()

    ca.establecer_valor_dinamico("v_max_concreto_eleccion", 4.0)
    assert ca.valor_si_declarado("v_max_concreto_eleccion") == pytest.approx(4.0)


def test_un_override_a_None_se_rechaza_y_cierra_el_default_silencioso(_limpia_overrides):
    """
    `valor()` consulta _OVERRIDES ANTES de mirar si el valor es None: un
    override a None devolvia None en vez de lanzar CriterioPendienteError,
    que es exactamente el vacio relleno en silencio que este archivo existe
    para impedir. Retirar una declaracion es `quitar_valor_dinamico`.
    """
    with pytest.raises(ValueError, match="quitar_valor_dinamico"):
        ca.establecer_valor_dinamico("phi_relleno_trasdos", None)
    assert "phi_relleno_trasdos" not in ca.valores_dinamicos()
    with pytest.raises(CriterioPendienteError):
        valor("phi_relleno_trasdos")


def test_la_escritura_permanente_valida_antes_de_tocar_el_disco(tmp_path):
    """
    Un valor que la guardia rechaza no llega a escribirse: el archivo fuente
    nunca queda en un estado que su propio import rechazaria.
    """
    copia = tmp_path / "criterios_copia.py"
    original = Path(ca.__file__).read_text(encoding="utf-8")
    copia.write_text(original, encoding="utf-8")

    with pytest.raises(ValueError, match="fuera del rango"):
        ca.escribir_valor_en_archivo("v_max_concreto_eleccion", 99.0, ruta=str(copia))

    assert copia.read_text(encoding="utf-8") == original, (
        "la guardia rechazo el valor pero el archivo ya se habia tocado")


# ---------------------------------------------------------------------------
# Criterios opcionales: valor=None que NO es un vacio
# ---------------------------------------------------------------------------

def test_los_opcionales_declarados_hoy():
    """
    Se llamaba `..._es_el_unico_opcional_declarado_hoy`. Ya no es el unico:
    al cerrar NOR-HID-08 entro 'riesgo_admisible_propietario', que tiene
    exactamente la misma forma -- la norma fija un valor por defecto (los
    maximos recomendados de la Tabla N 02) y el criterio permite endurecerlo,
    sin bloquear si nadie lo declara.
    """
    opcionales = {k for k, c in CRITERIOS.items() if c.opcional}
    assert opcionales == {"v_max_concreto_eleccion",
                          "riesgo_admisible_propietario"}


def test_un_opcional_no_figura_entre_los_vacios_que_bloquean():
    """
    Su valor=None no detiene nada: V3 aplica el techo normativo de 6.0 m/s.
    Anunciarlo como vacio bloqueante le decia al revisor de la memoria que un
    refinamiento que nadie tiene obligacion de declarar era un hueco.
    """
    assert "v_max_concreto_eleccion" not in criterios_sin_valor()
    assert "v_max_concreto_eleccion" in ca.criterios_opcionales_sin_declarar()


def test_el_reporte_imprime_los_opcionales_en_su_propio_bloque():
    texto = reporte_criterios(solo_usados=False)
    assert "REFINAMIENTO OPCIONAL NO ADOPTADO" in texto

    bloque_vacios = texto.split("VACIOS SIN VALOR")[1].split("REFINAMIENTO OPCIONAL")[0]
    assert "v_max_concreto_eleccion" not in bloque_vacios, (
        "el opcional volvio al bloque de vacios bloqueantes")

    bloque_opcional = texto.split("REFINAMIENTO OPCIONAL NO ADOPTADO")[1]
    assert "v_max_concreto_eleccion" in bloque_opcional
    assert "Tabla N 10" in bloque_opcional, (
        "el bloque no dice de que norma sale el valor por defecto")


def test_un_opcional_sin_fuente_normativa_se_rechaza():
    """
    Un opcional se sostiene sobre un defecto que vive FUERA de este archivo.
    Sin esa norma, valor=None no significa 'se aplica lo normativo': significa
    'no hay nada', y marcarlo opcional convierte un vacio en un silencio.
    """
    with pytest.raises(ValueError, match="fuente"):
        ca._verificar_criterio("criterio_de_prueba", _criterio_de_prueba(
            valor=None, opcional=True, sensibilidad=(3.0, 6.0),
            fuente="PENDIENTE - falta extraer el numero"))


def test_un_opcional_sin_rango_declarado_se_rechaza():
    """El rango acota cuanto puede apartarse del valor normativo por defecto."""
    with pytest.raises(ValueError, match="sensibilidad"):
        ca._verificar_criterio("criterio_de_prueba", _criterio_de_prueba(
            valor=None, opcional=True, sensibilidad=None))


def test_leer_un_opcional_con_valor_no_lo_registra_como_usado():
    """
    Sin declarar no se aplico a nada, y M11 no tiene uso que declarar. Es la
    diferencia entre 'no se adopto' y 'no se miro'.
    """
    assert ca.valor_si_declarado("v_max_concreto_eleccion") is None
    assert "v_max_concreto_eleccion" not in ca._USADOS


# ---------------------------------------------------------------------------
# Contraste contra los casos patron
# ---------------------------------------------------------------------------

def test_la_cadena_sismica_reproduce_CP7():
    """
    CP-7 verifica que la cadena este desagregada y no con 0.50 hardcodeado:
    A_s = F_pga * PGA ; k_h = factor_muro * k_h0.
    """
    cp = CP7_CADENA_SISMICA
    # El PGA abre la cadena desde datos_sitio.py: es [S], no criterio.
    assert ds.valor("PGA_roca_B") == pytest.approx(cp["PGA"])

    # El criterio ya no guarda el FACTOR sino las FILAS de la tabla sobre las
    # que se lee: la tabla es [N] y la eleccion de fila es [A]. El factor sale
    # de la envolvente de esas filas al PGA del proyecto.
    filas = valor("F_pga")
    assert filas == ("C", "D", "E")
    F_pga = max(F_PGA_TABLA[fila][-1] for fila in filas)
    assert F_pga == pytest.approx(cp["F_pga"])

    A_s = ds.valor("PGA_roca_B") * F_pga
    assert A_s == pytest.approx(cp["A_s_esperado"])

    k_h0 = A_s                                 # Manual de Puentes, 2.8.1.1.14.2.1
    assert k_h0 == pytest.approx(cp["k_h0_esperado"])

    # Lo declarado es si se aplica o no la reduccion que el numeral autoriza;
    # sin reduccion, k_h = k_h0.
    assert valor("factor_muro_eleccion") == "sin_reduccion"
    assert k_h0 == pytest.approx(cp["k_h_con_muro_rigido_esperado"])

    # Si el muro admitiera desplazamiento, la misma cadena debe dar 0.25.
    assert REDUCCION_KH_POR_DESPLAZAMIENTO * k_h0 == pytest.approx(
        cp["k_h_con_muro_desplazable_esperado"]
    )
    # k_v ya no es un numero adoptado: el criterio declara que rige el cero
    # que fija el num. 2.8.1.1.14.2.1, y ese cero es [N].
    assert valor("k_v") == "prescrito_sin_caso_reservado"


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


# ===========================================================================
# Clase de sitio F: la dispensa de periodo corto no existe en AASHTO
# ===========================================================================

# Criterios que arma la cadena sismica de Sec. 0.4-0.5 y que M11 imprime en la
# seccion sismica de la memoria. 'PERFIL_SUELO_PRESUNTO' entra porque es la
# presuncion geotecnica sobre la que se apoya 'clase_sitio'.
CRITERIOS_SISMICOS = ("clase_sitio", "PERFIL_SUELO_PRESUNTO", "F_pga",
                      "F_pga_lectura_columna_extrema", "factor_muro_eleccion",
                      "k_v", "gamma_EQ", "Mw_licuefaccion")


def test_la_clase_de_sitio_es_adopcion_declarada_y_no_dispensa_normativa():
    """
    AASHTO LRFD 9a ed. (2020) NO concede dispensa por periodo corto a la
    Clase F: ni el Art. 3.10.3.1, ni el comentario C3.10.3.1, ni tabla o nota
    alguna. Exige estudio de respuesta de sitio especifico, sin condiciones.

    Por eso el criterio dejo de ser [C] -- un vacio CUBIERTO con fuente
    reconocida -- y paso a [A]: usar los factores de sitio tabulados es una
    adopcion del proyectista y no un permiso de la norma. Si alguien vuelve a
    poner [C] aqui, esta volviendo a atribuirle a AASHTO algo que no dice.
    """
    c = criterio("clase_sitio")
    assert c.etiqueta == "A", (
        "clase_sitio volvio a etiquetarse como vacio cubierto por una fuente. "
        "No hay fuente que lo cubra: la dispensa de periodo corto no existe")
    assert c.valor == "F_con_factores_tabulados_por_adopcion"
    assert "no concede" in c.fuente or "NINGUNA" in c.fuente


def test_la_memoria_no_presenta_ninguna_excepcion_en_la_seccion_sismica():
    """
    La palabra 'excepcion' desaparece de todo lo que M11 imprime de la cadena
    sismica. No es cosmetica: el expediente llego a afirmar que AASHTO
    autorizaba una dispensa para la Clase F, y un revisor con AASHTO a mano
    lee 'excepcion' y busca el numeral que la concede. No hay ninguno.

    La excepcion declarada de DURABILIDAD (Sec. 0.2, E.060 Cap. 4 y Art. 7.7)
    si existe y es legitima -- por eso este test mira solo los criterios
    sismicos y no el archivo entero.
    """
    for clave in CRITERIOS_SISMICOS:
        c = criterio(clave)
        texto = " ".join(str(campo) for campo in
                         (c.concepto, c.justificacion, c.fuente,
                          c.reemplazado_por, c.trazabilidad,
                          c.verificacion_pendiente) if campo)
        assert "excep" not in texto.lower(), (
            f"'{clave}' vuelve a hablar de una excepcion en la seccion "
            "sismica de la memoria")


def test_lo_que_cierra_la_clase_de_sitio_es_el_estudio_de_respuesta_de_sitio():
    """
    Antes lo cerraba una lectura de Vs30/N_barra sobre 30 m. Sigue haciendo
    falta -- define la clase -- pero ya no basta: la Clase F exige ADEMAS el
    estudio de respuesta de sitio especifico. Pedir solo los 30 m volveria a
    programar la campana corta, que es el error que este bloque de tests
    lleva dos correcciones intentando evitar.
    """
    c = criterio("clase_sitio")
    pendiente = f"{c.reemplazado_por} {c.verificacion_pendiente}"
    assert "30 m" in c.reemplazado_por
    assert "respuesta de sitio" in pendiente


# ---------------------------------------------------------------------------
# Valor EFECTIVO y procedencia (SIS-A-01, el bloqueante de las tres auditorias)
# ---------------------------------------------------------------------------
# El defecto era de REPORTE y no de calculo: el calculo si usaba el valor
# declarado en caliente. Estos tests fijan la mitad que faltaba -- que el
# archivo pueda decir, ademas de que valor gobierna, DE DONDE vino.

def test_criterio_efectivo_devuelve_el_valor_que_gobierna_el_calculo(_limpia_overrides):
    """`criterio()` da el valor del archivo; `criterio_efectivo()`, el que corre."""
    clave = "phi_relleno_trasdos"
    assert criterio(clave).valor is None

    ca.establecer_valor_dinamico(clave, 32.0)

    assert criterio(clave).valor is None, "el archivo no se toca"
    assert ca.criterio_efectivo(clave).valor == pytest.approx(32.0)
    assert valor(clave) == pytest.approx(32.0), (
        "el calculo y el reporte tienen que leer el MISMO valor: si divergen "
        "vuelve el hallazgo bloqueante")
    # El resto del Criterio viaja intacto: solo cambia el valor.
    assert ca.criterio_efectivo(clave).justificacion == criterio(clave).justificacion


def test_la_procedencia_distingue_el_declarado_en_caliente_del_transcrito(_limpia_overrides):
    """Un override no es un valor transcrito de una norma, y se dice."""
    assert not ca.declarado_en_caliente("F_pga")
    assert "F_pga" not in ca.criterios_declarados_en_caliente()

    ca.establecer_valor_dinamico("phi_relleno_trasdos", 32.0)

    assert ca.declarado_en_caliente("phi_relleno_trasdos")
    assert "phi_relleno_trasdos" in ca.criterios_declarados_en_caliente()
    # Ni vacio ni valor de archivo: la tercera categoria, que antes no existia
    # y hacia que el criterio se cayera de los dos bloques de la memoria.
    assert "phi_relleno_trasdos" not in criterios_sin_valor()


def test_el_reporte_de_texto_marca_lo_declarado_para_la_corrida(_limpia_overrides):
    ca.establecer_valor_dinamico("phi_relleno_trasdos", 32.0)
    valor("phi_relleno_trasdos")

    texto = reporte_criterios(solo_usados=True)

    assert "32.0" in texto
    assert "declarado para esta corrida, no en archivo" in texto
    assert "DECLARADOS SOLO PARA ESTA CORRIDA" in texto


def test_los_criterios_sin_consumidor_declaran_por_que_nadie_los_invoca():
    """
    Un criterio CON valor y sin invocacion no cae en ningun bloque de la
    memoria y desaparecia del HTML (SIS-B-15). La razon se escribe UNA vez,
    en el propio criterio, y no repartida entre la auditoria y el manifiesto.
    """
    sin_consumidor = ca.criterios_sin_consumidor()
    assert "demanda_sismica_licuefaccion" in sin_consumidor
    for clave in sin_consumidor:
        assert criterio(clave).sin_consumidor.strip(), clave


def test_hay_homologo_de_datos_con_verificacion_pendiente():
    """
    `datos_sitio` exponia la consulta y `criterios_adoptados` no, de modo que
    el JSON del expediente declaraba que datos de sitio quedaban sin cerrar
    documentalmente y no que criterios (SIS-D-07).
    """
    abiertos = ca.criterios_con_verificacion_pendiente()
    assert abiertos
    for clave in abiertos:
        assert criterio(clave).verificacion_pendiente
        assert ca.criterio_efectivo(clave).valor is not None, (
            f"'{clave}' no tiene valor: un vacio se declara en el bloque de "
            "vacios, no como verificacion documental abierta")
    # Hermanos de verdad: misma pregunta, mismo tipo de respuesta ordenada.
    assert abiertos == sorted(abiertos)
    assert ds.datos_con_verificacion_pendiente() == sorted(
        ds.datos_con_verificacion_pendiente())


def test_lo_que_declara_sin_consumidor_de_verdad_no_tiene_consumidor():
    """
    La memoria imprime "ningun modulo de produccion los llama" leyendo el
    campo `sin_consumidor`. Sin esta guardia esa frase seria una afirmacion no
    verificada -- exactamente el patron que SIS-A-03 denuncio en ocho
    docstrings: texto que describia un estado que el codigo ya no tenia.

    Se mira produccion, no tests: `src/modulos/`, `cli.py` y `gui/app.py`.
    """
    raiz = Path(__file__).resolve().parents[1]
    fuentes = list((raiz / "src" / "modulos").glob("*.py"))
    fuentes += [raiz / "cli.py", raiz / "gui" / "app.py"]
    textos = {ruta: ruta.read_text(encoding="utf-8-sig") for ruta in fuentes}

    for clave in ca.criterios_sin_consumidor():
        invocaciones = [ruta.name for ruta, texto in textos.items()
                        if clave in texto]
        assert not invocaciones, (
            f"'{clave}' declara `sin_consumidor` y aparece en {invocaciones}. "
            "O lo invoca alguien -- y entonces la memoria esta mintiendo -- o "
            "la mencion hay que quitarla")


# ---------------------------------------------------------------------------
# Topes de diametro: de catalogo, no de norma (C01)
# ---------------------------------------------------------------------------
# Los tres tests de este bloque vivian en tests/test_constantes_normativas.py,
# mirando `CN.D_MAX`. Comprueban lo mismo; lo que cambio es donde vive el dato
# y, sobre todo, QUE es: las normas de producto a las que se le atribuia el
# tope tabulan hasta 3600 mm (NOR-PRO-01, NOR-PRO-02, MAT-O8), de modo que
# 2.70 / 2.10 / 1.50 son topes de catalogo adoptados por el proyecto.

CLAVE_TOPES = "D_max_catalogo"


def test_el_hdpe_es_el_material_con_el_tope_mas_restrictivo():
    topes = valor(CLAVE_TOPES)
    assert topes["hdpe"] == min(topes.values())
    assert topes["hdpe"] < topes["tmc"] < topes["concreto_reforzado"]


def test_todos_los_topes_de_diametro_son_alcanzables_desde_la_progresion():
    inicio = valor("diametros_normalizados")["inicio"]
    for material, tope in valor(CLAVE_TOPES).items():
        assert tope >= inicio, f"el tope de {material} es menor que el minimo"


def test_ningun_diametro_de_alcantarilla_alcanza_la_luz_de_puente():
    """Sec. 2.1: con luz >= 6.0 m la obra sale del alcance del script."""
    import constantes_normativas as CN
    assert max(valor(CLAVE_TOPES).values()) < CN.LUZ_MAX_ALCANTARILLA
    assert CN.DIAMETRO_MIN < CN.LUZ_MAX_ALCANTARILLA

