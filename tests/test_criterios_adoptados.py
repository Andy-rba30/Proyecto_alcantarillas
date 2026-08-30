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

import re
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
from tests.apoyo import estructura


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

@pytest.mark.parametrize("clave", [
    "talud_terraplen",                       # [A] SIN rango de sensibilidad
    "punto_aplicacion_incremento_sismico",   # [A] CON rango de sensibilidad
    "v_max_concreto_eleccion",
])
@pytest.mark.parametrize("no_finito", [float("inf"), float("-inf"), float("nan")])
def test_ningun_criterio_admite_un_numero_no_finito(clave, no_finito):
    """
    Criterio de salida de S16: "ningun dato no finito entra al pipeline como
    diagnostico falso". El rango de sensibilidad NO basta para conseguirlo:
    solo defiende a los criterios que declaran uno, y 'talud_terraplen' -- que
    es [A] y no lo declara -- aceptaba inf y nan por los tres caminos.

    Y el camino es real, no teorico: `cli.declarar_criterios` resuelve el
    texto de --declarar con `ast.literal_eval`, y `ast.literal_eval("1e999")`
    devuelve inf sin error. Con talud_terraplen = inf, M7 devolvia
    proyeccion_taludes = inf, longitud_conducto = inf y cota_salida = -inf, y
    la memoria imprimia un diagnostico entero construido sobre numeros que no
    lo son.
    """
    try:
        with pytest.raises(ValueError, match="infinito, con NaN"):
            ca.establecer_valor_dinamico(clave, no_finito)
        assert clave not in ca.valores_dinamicos()
    finally:
        ca.quitar_valor_dinamico(clave)


def test_la_guardia_de_finitud_mira_dentro_de_las_estructuras():
    """
    Un criterio puede valer una tupla (la doble n de Sec. 4.1.1) o un dict (el
    predimensionamiento del cabezal, la exposicion quimica del EMS). Un inf
    escondido ahi dentro entra al calculo igual que uno escrito como escalar,
    de modo que la guardia recorre la estructura entera y no solo el escalar.
    """
    from dataclasses import replace

    base = ca.CRITERIOS["n_manning_hdpe"]
    with pytest.raises(ValueError, match="infinito, con NaN"):
        ca._verificar_criterio("n_manning_hdpe",
                               replace(base, valor=(0.010, float("inf"))))
    with pytest.raises(ValueError, match="infinito, con NaN"):
        ca._verificar_criterio("n_manning_hdpe",
                               replace(base, valor={"a": [1.0, float("nan")]}))


def test_la_guardia_de_finitud_no_molesta_a_un_valor_normal():
    """La guardia no puede llevarse por delante una declaracion legitima."""
    try:
        ca.establecer_valor_dinamico("talud_terraplen", 1.5)
        assert ca.valor("talud_terraplen") == pytest.approx(1.5)
    finally:
        ca.quitar_valor_dinamico("talud_terraplen")


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
                    justificacion="j", fuente="f",
                    resolucion=ca.DeEnsayo(ensayo="e", trazabilidad_exigida="t")))
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
    # SIS-C-02: se pregunta al arbol, no al texto. Un comentario que explique
    # POR QUE la referencia esta muerta es justo lo contrario de invocarla, y
    # la version de subcadena la contaba como invocacion.
    invocaciones = [
        ruta.name for ruta in (raiz / "src" / "modulos").glob("*.py")
        if "PERFIL_SUELO_PRESUNTO" in estructura.nombres_usados(ruta)
        or "PERFIL_SUELO_PRESUNTO" in estructura.textos_de_llamada_o_indice(ruta)
    ]
    assert not invocaciones, (
        f"'PERFIL_SUELO_PRESUNTO' dejo de ser referencia muerta ({invocaciones}): "
        "revisa si sigue bastando una presuncion de tramo o hace falta el dato "
        "por calicata")


def test_la_licuefaccion_y_la_clase_de_sitio_piden_profundidades_distintas():
    """
    Dos ensayos, dos profundidades, y no son intercambiables:

        PERFIL_SUELO_PRESUNTO   licuefaccion -> SPT de 15 m (E.050 Art. 38)
        clase_sitio             clase sismica -> 100 ft = 30.48 m
                                (Vs30 / N_barra)

    'clase_sitio' decia antes que lo cerraba un SPT de ">= 15 m", que es la
    profundidad del OTRO requisito: con 15 m no se lee un Vs30. Este test
    existe para que la campana geotecnica no se programe corta.
    """
    licuefaccion = criterio("PERFIL_SUELO_PRESUNTO").reemplazado_por
    clase = criterio("clase_sitio").reemplazado_por

    assert "15 m" in licuefaccion and "Art. 38" in licuefaccion
    # La profundidad de la clase es la que el articulado imprime -- «the
    # upper 100 ft» --, no los «30 m» que la hoja de ruta le atribuye. La
    # cifra de la hoja de ruta aparece aqui SOLO citada como discrepancia,
    # y por eso no basta con buscar «30 m»: hay que exigir las dos.
    assert "100 ft" in clase and "30.48 m" in clase
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
    # `resolucion` es obligatoria desde S15 (Sec. 4.3): el criterio de
    # prueba declara la mas simple, porque lo que estos tests ejercitan es la
    # guardia de sensibilidad y no la del modo de resolucion.
    base = dict(valor=1.0, etiqueta="A", concepto="c", justificacion="j",
                fuente="f", resolucion=ca.Libre(que_lo_fija="prueba"))
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


@pytest.fixture
def criterios_restaurados():
    """
    `escribir_valor_en_archivo` MUTA `CRITERIOS` en memoria a proposito (para
    que la sesion en curso vea el valor definitivo sin reiniciar). Un test que
    la ejercite tiene que devolver el diccionario a su sitio, o el resto de la
    suite veria un criterio con valor donde deberia haber un vacio.
    """
    copia = dict(ca.CRITERIOS)
    yield
    ca.CRITERIOS.clear()
    ca.CRITERIOS.update(copia)
    ca.limpiar_valores_dinamicos()


def test_la_escritura_permanente_reescribe_el_valor_en_el_archivo(
        tmp_path, criterios_restaurados):
    """
    SIS-F-02: la rama que SI escribe el archivo fuente no se ejecutaba nunca.
    El unico test de la escritura permanente comprobaba el RECHAZO previo, de
    modo que el `subn`, el `write_text` y la actualizacion en memoria -- todo
    lo que de verdad hace la funcion -- estaban sin cubrir.

    Se escribe sobre una COPIA en tmp_path: el archivo fuente del repositorio
    no se toca, que es lo que el parametro `ruta` existe para permitir.
    """
    clave = "talud_terraplen"
    copia = tmp_path / "criterios_copia.py"
    original = Path(ca.__file__).read_text(encoding="utf-8")
    copia.write_text(original, encoding="utf-8")
    assert ca.CRITERIOS[clave].valor is None, (
        f"'{clave}' dejo de estar vacio: este test necesita un criterio pendiente")

    ca.establecer_valor_dinamico(clave, 1.5)
    assert ca.declarado_en_caliente(clave)

    ca.escribir_valor_en_archivo(clave, 1.5, ruta=str(copia))

    escrito = copia.read_text(encoding="utf-8")
    assert escrito != original, "el archivo no se toco"
    assert f'"{clave}": Criterio(\n        valor=1.5,' in escrito, (
        "el valor no quedo escrito en el bloque del criterio")
    # ...y SOLO ese bloque: la escritura no puede arrastrar nada mas.
    assert len(escrito.splitlines()) == len(original.splitlines())

    # El estado en memoria: el valor pasa a ser el del archivo y el override
    # en caliente se retira, porque ya no hace falta.
    assert ca.CRITERIOS[clave].valor == pytest.approx(1.5)
    assert not ca.declarado_en_caliente(clave)
    # Los demas campos del Criterio no se tocan: describen POR QUE se adopto
    # el valor y se revisan a mano, como dice el docstring de la funcion.
    assert ca.CRITERIOS[clave].etiqueta == "A"
    assert ca.CRITERIOS[clave].sensibilidad is None
    assert ca.CRITERIOS[clave].fuente


@pytest.mark.parametrize("clave", ["n_manning_hdpe", "v_max_hdpe", "v_max_tmc",
                                   "cobertura_minima_aashto",
                                   "factores_carga_aashto",
                                   "procedimiento_flexion_corte_aashto_sec5"])
def test_la_escritura_permanente_se_niega_ante_un_valor_multilinea(
        tmp_path, criterios_restaurados, clave):
    """
    SIS-F-19: el patron de `escribir_valor_en_archivo` solo alcanza a los
    criterios cuyo `valor=` cabe en una linea. Ese ValueError es LO UNICO que
    impide escribir un escalar encima de un criterio cuyo valor es una tabla,
    un dict o una tupla multilinea -- que lo dejaria a medias y con el resto
    del literal colgando.

    La ficha hablaba de DOS criterios; en el arbol de hoy son SEIS. El test se
    parametriza sobre los seis y comprueba las dos mitades del contrato: que
    se niega, y que NO toca el archivo al negarse.

    Se reescribe el criterio con SU PROPIO valor actual, no con un numero
    inventado: asi la guardia de `_verificar_criterio` lo acepta con
    seguridad -- es el valor que el archivo ya declara -- y lo unico que puede
    fallar es lo que este test mide, el alcance del patron. Con un escalar
    cualquiera, los que declaran rango de sensibilidad caerian antes por el
    rango y el test estaria probando otra cosa.
    """
    copia = tmp_path / "criterios_copia.py"
    original = Path(ca.__file__).read_text(encoding="utf-8")
    copia.write_text(original, encoding="utf-8")
    suyo = ca.CRITERIOS[clave].valor

    with pytest.raises(ValueError, match="No se encontro el bloque"):
        ca.escribir_valor_en_archivo(clave, suyo, ruta=str(copia))

    assert copia.read_text(encoding="utf-8") == original, (
        "se nego a escribir pero el archivo ya se habia tocado")
    assert ca.CRITERIOS[clave].valor == suyo, (
        "se nego a escribir y aun asi cambio el valor en memoria")


def test_la_escritura_permanente_no_inventa_una_clave(tmp_path):
    copia = tmp_path / "criterios_copia.py"
    copia.write_text(Path(ca.__file__).read_text(encoding="utf-8"),
                     encoding="utf-8")
    with pytest.raises(KeyError):
        ca.escribir_valor_en_archivo("criterio_que_no_existe", 1.0,
                                     ruta=str(copia))


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
# Clase de sitio: un [S] sin valor, y la dispensa de periodo corto no existe
# ===========================================================================
# S14 aplica la decision de docs/resolucion_clase_sitio.md (S13, conflicto #8):
# el expediente deja de atribuirse la Clase de Sitio F porque las DOS fuentes
# prohiben suponer la clase E o F sin dato geotecnico ni determinacion de la
# autoridad, y este expediente no tiene ninguna de las dos. 'clase_sitio' pasa
# de [A] con valor a [S] SIN VALOR: no es una eleccion mal acotada, es un
# HECHO QUE FALTA.
#
# Estos tests se reescriben con la correccion y siguen vigilando lo mismo que
# vigilaban -- que nadie le atribuya a AASHTO una dispensa que no concede --,
# mas lo que la decision anade: que no vuelva a aparecer un valor.

# Criterios que arma la cadena sismica de Sec. 0.4-0.5 y que M11 imprime en la
# seccion sismica de la memoria. 'PERFIL_SUELO_PRESUNTO' entra porque es la
# presuncion geotecnica sobre la que se apoya 'clase_sitio'.
CRITERIOS_SISMICOS = ("clase_sitio", "PERFIL_SUELO_PRESUNTO", "F_pga",
                      "F_pga_lectura_columna_extrema", "factor_muro_eleccion",
                      "k_v", "gamma_EQ", "Mw_licuefaccion")


def test_la_clase_de_sitio_no_se_supone_y_queda_como_dato_de_sitio_vacio():
    """
    Las dos fuentes PROHIBEN suponer la clase E o F sin dato geotecnico ni
    determinacion de la autoridad competente, y este expediente no tiene
    ninguna de las dos (AASHTO LRFD Art. 3.10.3.1, al pie de la Tabla
    3.10.3.1-1, pag. impresa 3-102; Manual de Puentes num. 2.4.3.11.2.1.1,
    pag. impresa 122, que lo endurece a "no seran supuestas").

    Por eso el criterio no lleva valor y no es [A]: lo que falta no es la
    regla -- la norma dice como se determina la clase, con que variables y
    sobre que profundidad --, falta la MEDICION. Eso es un [S] pendiente de
    ensayo, y se defiende con trazabilidad, no con un rango.

    Si alguien vuelve a ponerle valor aqui, esta volviendo a suponer la clase
    que las dos fuentes vedan suponer.
    """
    c = criterio("clase_sitio")
    assert c.valor is None, (
        "'clase_sitio' volvio a tener valor. Atribuirse una clase de sitio "
        "sin dato geotecnico es lo que las dos fuentes prohiben "
        "expresamente: no es una adopcion declarable del proyectista")
    assert c.etiqueta == "S", (
        "'clase_sitio' no es una eleccion del proyectista ni un vacio "
        "normativo: es un hecho de sitio que se mide (Art. 3.10.3.1, «by "
        "their stiffness as determined by the shear wave velocity in the "
        "upper 100 ft»). Cambia al mover la obra y no al cambiar de "
        "proyectista, que es la regla que separa [S] de [N] y de [A]")
    assert c.trazabilidad and c.sensibilidad is None
    assert "clase_sitio" in criterios_sin_valor(), (
        "el vacio tiene que entrar por `criterios_sin_valor()`, que es la "
        "puerta de M11 que le corresponde: es la via por la que la memoria "
        "lo declara sin que nadie lo invoque (SIS-B-01)")


def test_la_cadena_sismica_no_se_detiene_por_la_clase_de_sitio_indeterminada():
    """
    Un `valor=None` invocado detiene el calculo, y eso es correcto para un
    vacio que el calculo necesita. Este no lo es: la cadena sismica consume
    el FACTOR -- 'F_pga' --, no la clase. Invocar 'clase_sitio' desde
    produccion pararia el dimensionamiento entero del cabezal sin que
    ninguna norma lo exija.

    El vacio se DECLARA, no se interpone. La guardia de que nadie lo invoca
    la pone `test_lo_que_declara_sin_consumidor_de_verdad_no_tiene_consumidor`
    sobre el campo `sin_consumidor`; aqui se fija la otra mitad: que el
    factor que la cadena si consume sigue teniendo valor y rango.
    """
    assert criterio("clase_sitio").sin_consumidor.strip()
    f_pga = criterio("F_pga")
    assert f_pga.valor == ("C", "D", "E")
    assert f_pga.etiqueta == "A" and f_pga.sensibilidad


# Sustantivos con que se nombra una concesion normativa. La palabra sola no
# es el defecto: el defecto es AFIRMAR que una norma la concede.
_CONCESION = re.compile(r"\bexcepcion(?:es)?\b|\bdispensa(?:s)?\b"
                        r"|\bexencion(?:es)?\b", re.IGNORECASE)

# El ancla de una cita registrada -- `AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES` --
# no es prosa del expediente: es el IDENTIFICADOR del pasaje en el registro,
# y ese pasaje se llama asi porque la fuente titula el bloque «Exceptions».
# Se borra antes de leer las frases, para que un identificador no cuente como
# una afirmacion.
_ANCLA_DE_CITA = re.compile(r"#[A-Z0-9_]+")

# Marcas que hacen de la frase lo CONTRARIO de una concesion: una negacion,
# una prohibicion, la denuncia de que la concesion era falsa, o la cita del
# bloque que las dos fuentes titulan «Exceptions» / «Excepciones» -- que es,
# justamente, donde vive la PROHIBICION de suponer la clase.
_NO_ES_CONCESION = re.compile(
    r"\bno\b|\bning|\bnunca\b|\bsin\b|\btampoco\b|prohib|veda|vedad"
    r"|falsa|falso|inventad|«excepciones»|«exceptions»|bloque «", re.IGNORECASE)


def test_la_seccion_sismica_no_afirma_ninguna_dispensa_normativa():
    """
    El expediente llego a afirmar que AASHTO concedia una EXCEPCION para la
    Clase F -- una dispensa por periodo fundamental T <= 0.5 s --, y un
    revisor con AASHTO a mano lee "excepcion" y busca el numeral que la
    concede. No hay ninguno: se busco sobre las 1905 paginas de AASHTO LRFD
    9a ed. (2020) con cero coincidencias.

    POR QUE ESTA GUARDIA SE ESTRECHO EN S14. Perseguia la SUBCADENA "excep",
    y con eso rechazaba la cita mas fuerte del archivo: el texto que resuelve
    la cuestion vive en un bloque que las dos fuentes titulan literalmente
    «Exceptions» / «Excepciones», y la fila de E.030 de la que salia la letra
    se llama «Suelos excepcionales». Borrar la palabra para pasar el test
    dejaria la decision sin su cita, que es el modo exacto en que este
    expediente perdio la premisa la primera vez.

    Lo que se persigue ahora es la AFIRMACION, frase por frase: nombrar una
    excepcion o una dispensa solo vale si la frase la niega, la prohibe, la
    denuncia como falsa, o cita el titulo del bloque de la fuente.
    """
    for clave in CRITERIOS_SISMICOS:
        c = criterio(clave)
        texto = " ".join(str(campo) for campo in
                         (c.concepto, c.justificacion, c.fuente,
                          c.reemplazado_por, c.trazabilidad,
                          c.sin_consumidor, c.verificacion_pendiente) if campo)
        texto = _ANCLA_DE_CITA.sub("", texto)
        for frase in re.split(r"(?<=[.;:])\s+", texto):
            if not _CONCESION.search(frase):
                continue
            assert _NO_ES_CONCESION.search(frase), (
                f"'{clave}' nombra una excepcion o dispensa sin negarla ni "
                f"atribuirla al titulo de un bloque de la fuente:\n\n"
                f"    {frase}\n\n"
                "AASHTO no concede ninguna dispensa a la Clase F, y el "
                "Manual tampoco. Si la frase cita el bloque «Excepciones» de "
                "la fuente, escribelo entre comillas angulares; si afirma "
                "una concesion, es una cita inventada")


def test_la_dispensa_por_periodo_corto_se_declara_inexistente_donde_se_nombra():
    """
    La mitad positiva de la guardia anterior, y el nucleo que sobrevive a la
    correccion de S14: no basta con no afirmar la dispensa, hay que dejar
    dicho que NO EXISTE. Si no, el proximo que lea el expediente sin abrir
    AASHTO no sabra que ya se busco.
    """
    c = criterio("clase_sitio")
    texto = f"{c.justificacion} {c.fuente}".upper()
    assert "DISPENSA POR PERIODO CORTO NO EXISTE" in texto, (
        "'clase_sitio' dejo de decir que la dispensa por periodo corto no "
        "existe. Es la unica afirmacion negativa del bloque sismico que se "
        "verifico contra la fuente primaria, con 0 coincidencias en 1905 "
        "paginas, y borrarla pierde esa verificacion")


def test_lo_que_cierra_la_clase_de_sitio_son_dos_ensayos_y_no_uno():
    """
    Son DOS ensayos, de profundidades distintas, y conviene pedirlos juntos:

        (1) la caracterizacion de los 100 ft (30.48 m) superiores -- Vs30 o
            N_barra --, que es la profundidad que el Art. 3.10.3.1 escribe y
            con la que se LEE la clase;
        (2) si esa caracterizacion diera Clase F, el analisis de respuesta
            dinamica de sitio.

    Pedir solo (1) volveria a programar la campana corta. Y (2) se ancla en
    el ARTICULADO -- Art. 3.10.2 «shall», num. 2.4.3.11.2 del Manual «sera
    usado» --, no en la Nota 2 al pie de la tabla de factores, que lo repite
    y no lo funda: era donde el repositorio lo tenia colgado.
    """
    c = criterio("clase_sitio")
    texto = f"{c.reemplazado_por} {c.trazabilidad}"

    assert "100 ft" in c.reemplazado_por and "30.48 m" in c.reemplazado_por, (
        "la profundidad volvio a escribirse como «30 m». El Art. 3.10.3.1 "
        "imprime «the upper 100 ft» y no esa cifra: atribuirsela es la "
        "discrepancia DIS-HR-30M-VS-100FT")
    assert "3.10.2" in c.reemplazado_por, (
        "el analisis de respuesta de sitio volvio a anclarse en la Nota 2 de "
        "la tabla. La exige el articulado: Art. 3.10.2 / num. 2.4.3.11.2")
    assert "respuesta dinamica de sitio" in texto.lower()
    assert "15 m" in c.reemplazado_por and "Art. 38" in c.reemplazado_por, (
        "se perdio la advertencia de que el SPT de licuefaccion de 15 m NO "
        "cierra este criterio")


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
        # El GRAVE primero: la clave usada de verdad, leida del arbol. Si esto
        # falla, la memoria esta declarando como no usado un criterio que si
        # entra en el calculo (SIS-C-02).
        usada_de_verdad = [ruta.name for ruta in textos
                           if clave in estructura.textos_de_llamada_o_indice(ruta)
                           or clave in estructura.nombres_usados(ruta)]
        assert not usada_de_verdad, (
            f"'{clave}' declara `sin_consumidor` y {usada_de_verdad} la INVOCA: "
            "la memoria esta declarando como no usado un criterio que si entra "
            "en el calculo")
        # Y el MENOR despues, que es una comprobacion de TEXTO a proposito: el
        # criterio pide que no quede ni la mencion, para que nadie lea una
        # linea suelta y crea que el modulo lo consume.
        menciones = [ruta.name for ruta, texto in textos.items()
                     if clave in texto]
        assert not menciones, (
            f"'{clave}' declara `sin_consumidor` y aparece en {menciones}. "
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



# ===========================================================================
# Las guardas de este archivo que ninguna prueba alcanzaba (SIS-F-10)
# ===========================================================================
# SIS-F-10 conto trece `raise` sin cobertura sobre un arbol anterior; medida
# de nuevo sobre el de S16 la cuenta es mayor, y una parte esta aqui. Ninguna
# de las de abajo es de la taxonomia de `modelos.py`: son `ValueError` y
# `KeyError` de ARQUITECTURA -- si saltan, el archivo esta mal escrito y
# ninguna corrida deberia empezar --, y por eso importan tanto o mas: son las
# unicas que impiden que una declaracion incoherente entre al tablero y de
# ahi a la memoria, y borrarlas no rompia ninguna prueba.
#
# Van agrupadas en tablas y no una por test a proposito: lo que se lee de un
# vistazo es la lista de formas de estar mal escrito, cada una con el trozo
# de motivo que dice POR QUE.


# ---------------------------------------------------------------------------
# Una clave que nadie declaro no se inventa por NINGUNA de las tres lecturas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lectura", [
    ca.valor,                    # ya cubierta: la lectura que bloquea
    ca.valor_si_declarado,       # la de los criterios OPCIONALES
    ca.declarado_en_caliente,    # la que dice de donde vino el valor
])
def test_ninguna_lectura_inventa_una_clave_no_declarada(lectura):
    """
    `valor()` tenia su prueba y las otras dos no. Falla si alguna devuelve
    None o False ante una clave desconocida: un criterio mal tecleado se
    leeria como "sin declarar" (y bloquearia) o como "no declarado en
    caliente" (y la memoria escribiria una procedencia falsa), en vez de
    delatar el error de tipeo.
    """
    with pytest.raises(KeyError) as exc:
        lectura("parametro_que_nadie_declaro")
    assert "parametro_que_nadie_declaro" in str(exc.value)
    assert "criterios_adoptados.py" in str(exc.value)


def test_valor_si_declarado_devuelve_none_solo_para_una_clave_que_SI_existe():
    """
    La contraparte que separa las dos situaciones: "no esta declarada" es
    KeyError y "esta declarada y sigue vacia" es None. Confundirlas en
    cualquiera de los dos sentidos rellena un vacio o esconde un tipeo.
    """
    pendiente = next(iter(CLAVES_PENDIENTES))
    assert ca.valor_si_declarado(pendiente) is None
    assert ca.declarado_en_caliente(pendiente) is False


# ---------------------------------------------------------------------------
# `verificar_resolucion`: el criterio de salida de la Sec. 4.3, hecho guardia
# ---------------------------------------------------------------------------
# Las resoluciones de prueba se derivan con `dataclasses.replace` de las que
# el archivo YA declara, y no se escriben a mano: asi los ids de tabla, de
# fila y de columna salen del registro normativo -- que es donde viven -- y
# no de una transcripcion paralela que pueda quedar desfasada.

_DE_TABLA_REAL = CRITERIOS["n_manning_hdpe"].resolucion          # con fila_id
_DE_COLUMNA_REAL = CRITERIOS["h_eq_banda_intermedia_borde"].resolucion
_EN_RANGO_REAL = CRITERIOS["v_max_concreto_eleccion"].resolucion
_OTRA_TABLA_REAL = CRITERIOS["ke_entrada"].resolucion.tablas[0]


def _sin(resolucion, **campos):
    """La misma resolucion declarada, con un campo vaciado o cambiado."""
    from dataclasses import replace
    return replace(resolucion, **campos)


RESOLUCIONES_INCOHERENTES = [
    # --- libre -------------------------------------------------------------
    (ca.Libre(que_lo_fija=""), "no dice QUIEN pone el numero"),
    # --- de_tabla ----------------------------------------------------------
    (_sin(_DE_TABLA_REAL, tablas=()), "no cita ninguna tabla"),
    (_sin(_DE_TABLA_REAL, que_elige=""), "no dice QUE se elige"),
    (_sin(_DE_TABLA_REAL, tablas=("TABLA_QUE_NADIE_TRANSCRIBIO",)),
     "no esta en el registro normativo"),
    (_sin(_DE_TABLA_REAL, tablas=_DE_TABLA_REAL.tablas + (_OTRA_TABLA_REAL,)),
     "fija fila o columna y cita 2 tablas"),
    (_sin(_DE_TABLA_REAL, fila_id="fila_que_la_tabla_no_tiene"),
     "que la tabla no tiene"),
    (_sin(_DE_COLUMNA_REAL, columna_id="columna_que_la_tabla_no_tiene"),
     "que la tabla no tiene"),
    (_sin(_DE_TABLA_REAL, elegido_por="criterio_que_nadie_declaro"),
     "no es un criterio declarado"),
    # --- en_rango ----------------------------------------------------------
    (_sin(_EN_RANGO_REAL, columna_id="columna_que_la_tabla_no_tiene"),
     "que la tabla no tiene"),
    (_sin(_EN_RANGO_REAL, que_acota=""), "no dice QUE acota el rango"),
    # --- derivada ----------------------------------------------------------
    (ca.Derivada(de=(), regla="la regla"), "no declara de que se deriva"),
    (ca.Derivada(de=("otra_variable",), regla=""), "no declara de que se deriva"),
    # --- de_ensayo ---------------------------------------------------------
    (ca.DeEnsayo(ensayo="", trazabilidad_exigida="la lectura"),
     "no declara el procedimiento o la trazabilidad"),
    (ca.DeEnsayo(ensayo="el ensayo", trazabilidad_exigida=""),
     "no declara el procedimiento o la trazabilidad"),
    # --- de_catalogo -------------------------------------------------------
    (ca.DeCatalogo(catalogo_id="CATALOGO_QUE_NO_ESTA", que_elige="x",
                   advertencia="que norma NO lo sostiene"),
     "que no esta en el registro"),
]


@pytest.mark.parametrize("resolucion, motivo", RESOLUCIONES_INCOHERENTES,
                         ids=lambda x: None)
def test_la_resolucion_no_basta_con_ser_del_tipo_correcto(resolucion, motivo):
    """
    Falla si `verificar_resolucion` se conforma con el TIPO de la resolucion.
    El modo correcto con los campos vacios o con un id que no resuelve es
    peor que no declarar modo: la ventana abre una pestana que no puede
    llenar, la memoria escribe una procedencia que nadie puede seguir, y el
    `de_tabla` promete mostrar una tabla que no esta transcrita.
    """
    with pytest.raises(ValueError) as exc:
        ca.verificar_resolucion("criterio_de_prueba", resolucion)
    assert "criterio_de_prueba" in str(exc.value)
    assert motivo in str(exc.value)


@pytest.mark.parametrize("resolucion", [_DE_TABLA_REAL, _DE_COLUMNA_REAL,
                                        _EN_RANGO_REAL])
def test_las_resoluciones_del_archivo_pasan_su_propia_guardia(resolucion):
    """
    La contraparte que hace de la tabla de arriba una prueba y no una
    tautologia: las resoluciones REALES de las que se derivaron los casos
    malos pasan sin una queja, y devuelven su modo.
    """
    modo = ca.verificar_resolucion("criterio_de_prueba", resolucion)
    assert modo is ca.modo_de(resolucion)


# ---------------------------------------------------------------------------
# `_verificar_criterio`: lo que hace valida a UNA declaracion
# ---------------------------------------------------------------------------
# El ancla del vacio verificado se LEE del unico criterio que hoy declara uno
# ('cobertura_minima_aashto'): escribirla a mano crearia una segunda cita del
# registro que puede divergir de la que el archivo usa de verdad.
ANCLA_REAL = CRITERIOS["cobertura_minima_aashto"].vacio_verificado

DECLARACIONES_INCOHERENTES = [
    # (campos del criterio, trozo del motivo)
    (dict(etiqueta="X"), "no es de la convencion"),
    (dict(etiqueta="S", trazabilidad="como se leyo", sensibilidad=(1.0, 2.0)),
     "es [S] y declara sensibilidad"),
    (dict(trazabilidad="como se leyo"), "no es [S] y declara trazabilidad"),
    (dict(sensibilidad=(1.0, 2.0, 3.0)), "de 3 extremos"),
    (dict(etiqueta="N", de_catalogo=True), "no es una exigencia normativa"),
    (dict(etiqueta="N->", de_catalogo=True), "ni una analogia normativa"),
    (dict(valor=None, vacio_verificado=ANCLA_REAL, reemplazado_por="el ensayo"),
     "declara vacio_verificado y no tiene valor"),
    (dict(vacio_verificado=ANCLA_REAL), "no declara `reemplazado_por`"),
    (dict(resolucion=None), "no declara `resolucion`"),
]


@pytest.mark.parametrize("campos, motivo", DECLARACIONES_INCOHERENTES,
                         ids=lambda x: None)
def test_la_guardia_rechaza_cada_forma_de_declaracion_incoherente(campos,
                                                                  motivo):
    """
    Falla si se pierde cualquiera de estas ramas. Cada una deja entrar una
    declaracion que la memoria imprimiria como buena:

      etiqueta fuera de la convencion   una sexta etiqueta que M11 no ordena
      [S] con sensibilidad              un hecho de sitio con rango elegible
      trazabilidad sin ser [S]          un criterio que finge ser una lectura
      rango de tres extremos            un "rango" que no acota nada
      de_catalogo con etiqueta [N]/[N->] un tope de proveedor leido como
                                        exigencia normativa (NOR-PRO-01/02)
      vacio_verificado sin valor        decir que se cubre un vacio sin cubrirlo
      vacio_verificado sin reemplazo    un vacio agotado que se lee como cerrado
      sin resolucion                    una variable sin modo (Sec. 4.3)
    """
    with pytest.raises(ValueError) as exc:
        ca._verificar_criterio("criterio_de_prueba",
                               _criterio_de_prueba(**campos))
    assert "criterio_de_prueba" in str(exc.value)
    assert motivo in str(exc.value)


ANCLAS_QUE_NO_RESUELVEN = [
    ("manifiesto_citas.md Sec. 14.a", None),          # la real: no debe lanzar
    ("Sec. 14.a", "no tiene la forma"),               # sin documento
    ("manifiesto_citas.md 14.a", "no tiene la forma"),  # sin el rotulo 'Sec.'
    ("documento_que_no_existe.md Sec. 14.a", "no existe"),
    ("manifiesto_citas.md Sec. 999.z", "no tiene una Sec. 999.z"),
]


@pytest.mark.parametrize("ancla, motivo", ANCLAS_QUE_NO_RESUELVEN,
                         ids=lambda x: None)
def test_el_ancla_de_un_vacio_verificado_tiene_que_resolver(ancla, motivo):
    """
    Un valor que dice cubrir un vacio VERIFICADO y apunta a un registro que no
    existe afirma una diligencia que nadie hizo, y es peor que no decir nada:
    el revisor lee "vacio verificado", no encuentra donde, y no tiene forma de
    saber si el vacio se agoto o si la cita esta mal.

    Falla si desaparece cualquiera de los tres chequeos -- la forma del ancla,
    que el documento exista, y que la seccion exista dentro de el --, que son
    tres errores distintos y el mensaje los distingue. La primera fila es el
    ancla que el archivo declara de verdad: tiene que pasar.
    """
    if motivo is None:
        ca._verificar_ancla_de_vacio("criterio_de_prueba", ancla)
        return
    with pytest.raises(ValueError) as exc:
        ca._verificar_ancla_de_vacio("criterio_de_prueba", ancla)
    assert "criterio_de_prueba" in str(exc.value)
    assert motivo in str(exc.value)


def test_el_reporte_sin_invocaciones_lo_dice_en_vez_de_salir_vacio():
    """
    Falla si `reporte_criterios(solo_usados=True)` devuelve un bloque de
    encabezados sin filas cuando el calculo no invoco ningun criterio. La
    memoria de una corrida que se detuvo antes de usar nada tiene que decir
    eso, no dejar una tabla vacia que se lee como "no hubo criterios que
    declarar". Es el gemelo del que ya existe para `datos_sitio`.
    """
    assert not ca._USADOS                      # lo garantiza la fixture autouse
    assert reporte_criterios(solo_usados=True) == (
        "No se invoco ningun criterio adoptado.")

# ---------------------------------------------------------------------------
# SIS-E-05 / SIS-E-06: el contrato de las dos excepciones, fijado
# ---------------------------------------------------------------------------

def test_el_rechazo_de_una_declaracion_llega_legible_a_los_tres_llamadores():
    """
    SIS-E-05. El rechazo sale como `ValueError`, fuera de `ErrorProyecto`, y
    la decision esta argumentada en el docstring de `establecer_valor_dinamico`.
    Lo que la taxonomia persigue -- que la GUI no muestre una traza donde hay
    un problema que el proyectista puede corregir -- se cumple por otra via:
    los TRES llamadores capturan (ValueError, KeyError) a tres lineas.

    Este test fija esa via. Si alguien estrecha uno de los tres brazos, el
    rechazo pasaria a salir con traza y el argumento del docstring dejaria de
    ser cierto sin que nada avisara.
    """
    import ast as _ast
    from pathlib import Path as _Path

    raiz = _Path(__file__).resolve().parents[1]
    esperados = {
        (raiz / "cli.py", "main"),
        (raiz / "gui" / "app.py", "_aplicar_valor_corrida"),
        (raiz / "gui" / "app.py", "_guardar_valor_en_archivo"),
    }
    for ruta, funcion in esperados:
        arbol = _ast.parse(ruta.read_text(encoding="utf-8-sig"))
        nodo = next((n for n in _ast.walk(arbol)
                     if isinstance(n, _ast.FunctionDef) and n.name == funcion), None)
        assert nodo is not None, f"'{funcion}' ya no existe en {ruta.name}"
        capturados = set()
        for manejador in _ast.walk(nodo):
            if not isinstance(manejador, _ast.ExceptHandler) or manejador.type is None:
                continue
            tipos = (manejador.type.elts
                     if isinstance(manejador.type, _ast.Tuple) else [manejador.type])
            for t in tipos:
                if isinstance(t, _ast.Name):
                    capturados.add(t.id)
        assert "ValueError" in capturados, (
            f"{ruta.name}::{funcion} dejo de capturar ValueError: el rechazo "
            "de una declaracion pasaria a salir con traza (SIS-E-05)")


def test_el_rechazo_por_rango_sigue_siendo_ValueError_y_dice_el_rango():
    """La otra mitad: el mensaje tiene que servir para corregir el valor."""
    with pytest.raises(ValueError) as exc:
        ca.establecer_valor_dinamico("punto_aplicacion_incremento_sismico", 9.9)
    mensaje = str(exc.value)
    assert "fuera del rango de sensibilidad" in mensaje
    assert "0.333" in mensaje and "0.6" in mensaje, (
        "el mensaje tiene que traer el rango, no solo decir que se salio")
    assert not isinstance(exc.value, ErrorProyecto), (
        "si esto cambia, hay que actualizar los tres brazos de los llamadores "
        "y el argumento del docstring de establecer_valor_dinamico")


def test_dato_faltante_admite_un_dato_que_no_es_columna_del_csv():
    """
    SIS-E-06. `modelos.py` declara el contrato ancho -- "del CSV (Sec. 1.2) o
    de un tablero externo" -- y el codigo lo usa: V5 levanta
    DatoFaltanteError('ancho_derecho_via_m'), que su propio detalle admite que
    no es columna de Sec. 1.2. CLAUDE.md describia la excepcion mas estrecha
    de lo que el proyecto la tiene; se amplio la constitucion, que era lo que
    estaba desactualizado.
    """
    from modelos import DatoFaltanteError

    assert "tablero externo" in (DatoFaltanteError.__doc__ or "")

    raiz = Path(__file__).resolve().parents[1]
    constitucion = (raiz / "CLAUDE.md").read_text(encoding="utf-8")
    assert "no es columna del CSV" in constitucion, (
        "CLAUDE.md volvio a definir DatoFaltanteError solo sobre columnas del "
        "CSV: el codigo la usa tambien para los datos externos y para los que "
        "un tablero tendria que aportar")


# ---------------------------------------------------------------------------
# La segunda vuelta de MAT-D14: el no-finito ESCRITO COMO TEXTO
# ---------------------------------------------------------------------------
#
# La primera version de este cierre puso la guardia del texto en `cli.py`, en
# el brazo `except` de `ast.literal_eval`, y una revision adversarial la
# esquivo con comillas: `--declarar "CLAVE='nan'"` hace que `literal_eval`
# TENGA EXITO y devuelva la cadena 'nan', de modo que el brazo `except` nunca
# se ejecuta. La cadena entraba entera y `M9_cabezal.cuantia_de_diseno` la
# devolvia al calculo como `float('nan')`, con la memoria imprimiendo
# `cuantia_adoptada = nan`. La guardia esta hoy en `_verificar_criterio`, que
# es el cuello por donde pasan las tres vias de declaracion.

@pytest.mark.parametrize("texto", ["nan", "inf", "-inf", "Infinity",
                                   "-Infinity", "NaN", "  inf  ", "1e999"])
def test_un_texto_que_se_lee_como_no_finito_no_entra_como_criterio(
        criterios_restaurados, texto):
    with pytest.raises(ValueError, match="infinito"):
        ca.establecer_valor_dinamico("talud_terraplen", texto)


def test_un_texto_categorico_sigue_entrando(criterios_restaurados):
    """
    El contraste que hace que la guardia no sea celo: el respaldo a texto
    existe para los criterios CATEGORICOS, y esos no se leen como numero.
    """
    ca.establecer_valor_dinamico("metodo_estabilidad_global", "Bishop_Simplificado")
    assert ca.valor("metodo_estabilidad_global") == "Bishop_Simplificado"


def test_ninguna_clave_acepta_la_cadena_nan(criterios_restaurados):
    """
    El barrido entero, porque el agujero no era de una clave sino de la via:
    la revision adversarial midio 46 claves que la aceptaban.
    """
    aceptadas = []
    for clave in list(ca.CRITERIOS):
        try:
            ca.establecer_valor_dinamico(clave, "nan")
            aceptadas.append(clave)
        except (ValueError, KeyError):
            pass
    assert not aceptadas, (
        f"estas claves aceptan la cadena 'nan': {aceptadas}. El primer "
        "consumidor que haga float() sobre ellas la devuelve al calculo.")
