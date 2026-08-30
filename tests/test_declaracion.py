"""
tests/test_declaracion.py
=========================
DECLARAR desde la ventana: un solo camino, y la procedencia escrita.

Lo que este archivo vigila
--------------------------
    R1 del plan v12   la tabla es [N] y la eleccion de fila es [A]. Lo que la
                      ventana escribe es un criterio cuyo valor PROVIENE de la
                      fila X de la tabla T, y la procedencia lo dice: fila,
                      valor, alternativas descartadas, cita y fecha.
    «No inventes un   `declaracion` no puede tener un segundo camino de
     segundo camino»  escritura. Se comprueba sobre el AST, no leyendo el
                      texto: un `_OVERRIDES[clave] = valor` colado aqui
                      saltaria la guardia `_verificar_criterio` y con ella la
                      unica defensa del proyecto contra un valor sin declarar.
    R4                una fila que depende de un dato que el proyecto no tiene
                      no se puede elegir. El rechazo es la prueba de que la
                      ventana no elige por el usuario.
    Sec. 4.2          la validacion de un rango se hace por el TIPO del rango.
    SIS-A-18          la sesion guarda y restaura lo declarado, por el mismo
                      camino con guardia, y dice lo que la guardia rechazo.
"""

import ast
import json
from pathlib import Path

import pytest

import criterios_adoptados as ca
import declaracion as dec
import ventana_normativa as vn

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "declaracion.py"
ARBOL = ast.parse(MODULO.read_text(encoding="utf-8"), filename="declaracion.py")


@pytest.fixture(autouse=True)
def _sin_procedencias():
    """
    Cada test empieza y acaba con el mismo estado declarado que encontro.

    Las DOS mitades, y no solo el libro de procedencias: `_OVERRIDES` tambien
    es estado de modulo, y un valor declarado en un test que sobreviviera al
    siguiente convertiria «esta variable no llego a declararse» en un assert
    que pasa por herencia. Se repone el snapshot exacto en vez de limpiarlo
    todo, porque `conftest.py` declara cinco criterios para la corrida de
    pruebas y borrarlos rompe la suite por orden de ejecucion.
    """
    dec.limpiar()
    previos = ca.valores_dinamicos()
    yield
    dec.limpiar()
    for clave in list(ca.valores_dinamicos()):
        if clave not in previos:
            ca.quitar_valor_dinamico(clave)
    for clave, valor in previos.items():
        ca.establecer_valor_dinamico(clave, valor)


# ===========================================================================
# Un solo camino
# ===========================================================================

def _nombres_asignados(arbol):
    """Todo objetivo de asignacion del modulo, como texto."""
    salida = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            objetivos = (nodo.targets if isinstance(nodo, ast.Assign)
                         else [nodo.target])
            salida.extend(ast.unparse(o) for o in objetivos)
    return salida


def test_el_unico_camino_al_valor_es_establecer_valor_dinamico():
    """
    Todas las funciones que declaran llaman a `establecer_valor_dinamico`, y
    ninguna escribe el valor por su cuenta. Sin este test, «no inventes un
    segundo camino» seria una frase del prompt y no una propiedad del codigo.
    """
    llamadas = {ast.unparse(nodo.func) for nodo in ast.walk(ARBOL)
                if isinstance(nodo, ast.Call)}
    assert "_ca.establecer_valor_dinamico" in llamadas
    for prohibida in ("_ca.escribir_valor_en_archivo", "_ca.CRITERIOS.update",
                      "setattr"):
        assert prohibida not in llamadas, (
            f"'{prohibida}' abre un segundo camino de escritura")


def test_ninguna_funcion_de_declaracion_escribe_los_overrides_a_mano():
    """
    La forma concreta en que se abriria el agujero: escribir en `_OVERRIDES` o
    reasignar `CRITERIOS` salta `_verificar_criterio` entera.
    """
    for objetivo in _nombres_asignados(ARBOL):
        assert "_OVERRIDES" not in objetivo, objetivo
        assert "CRITERIOS" not in objetivo, objetivo


def test_cada_declarar_llama_a_la_guardia_antes_de_registrar_procedencia():
    """
    El ORDEN importa: registrar la procedencia antes de que la guardia acepte
    dejaria una procedencia de un valor rechazado.
    """
    for nombre in ("declarar_desde_tabla", "declarar_en_rango",
                   "declarar_valor"):
        funcion = next(n for n in ast.walk(ARBOL)
                       if isinstance(n, ast.FunctionDef) and n.name == nombre)
        cuerpo = [ast.unparse(s) for s in funcion.body]
        guardia = next(i for i, linea in enumerate(cuerpo)
                       if "establecer_valor_dinamico" in linea)
        registro = next(i for i, linea in enumerate(cuerpo)
                        if "_PROCEDENCIAS[clave]" in linea)
        assert guardia < registro, nombre


def test_la_guardia_del_archivo_sigue_rechazando_lo_que_rechazaba():
    """
    Declarar desde la ventana no relaja nada: un valor que
    `_verificar_criterio` rechaza se rechaza aqui, en el momento de
    declararlo, y no mas tarde durante el calculo.
    """
    with pytest.raises(KeyError):
        dec.declarar_valor("no_existe_este_criterio", 1.0)
    with pytest.raises(ValueError, match="no se puede declarar|valor None"):
        dec.declarar_valor("TW_receptor", None)


# ===========================================================================
# R1: la procedencia
# ===========================================================================

def test_declarar_desde_una_tabla_registra_fila_valor_alternativas_cita_y_fecha():
    """
    Las cinco cosas que la Sec. 4.3 pide, una por una. Es el criterio de
    salida de la sesion: «toda variable de_tabla se declara desde su ventana
    con procedencia registrada».
    """
    procedencia = dec.declarar_desde_tabla(
        "ke_entrada", 0.5, filas=("concreto_headwall_square_edge",))
    assert procedencia.filas == ("concreto_headwall_square_edge",)
    assert procedencia.valor == 0.5  # float-exacto: es el valor declarado, no un calculo
    assert procedencia.alternativas_descartadas
    assert "num." in procedencia.cita
    assert procedencia.fecha
    assert procedencia.tabla_id == "HDS5_3ED.TC2"
    assert dec.procedencia_de("ke_entrada") is procedencia


def test_la_procedencia_llega_al_valor_efectivo_del_criterio():
    """La otra mitad: el valor declarado gobierna de verdad el calculo."""
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    assert ca.declarado_en_caliente("ke_entrada")
    assert ca.criterio_efectivo("ke_entrada").valor == 0.5  # float-exacto: el valor declarado


def test_las_alternativas_descartadas_distinguen_tres_motivos():
    """
    «Alternativa viva no elegida», «el calculo no la usa» y «no era elegible»
    no son lo mismo, y una memoria que las listara juntas sugeriria que las
    tres se compararon. Dos de ellas no se podian comparar.
    """
    procedencia = dec.declarar_desde_tabla(
        "n_manning_hdpe", (0.010, 0.013), filas=("concreto_tubo_recto",))
    motivos = {a.motivo for a in procedencia.alternativas_descartadas}
    assert any("alternativa viva" in m for m in motivos)
    assert all(a.motivo.strip() for a in procedencia.alternativas_descartadas)
    assert all(a.id != "concreto_tubo_recto"
               for a in procedencia.alternativas_descartadas)


def test_la_procedencia_dice_en_texto_de_donde_salio_el_valor():
    procedencia = dec.declarar_desde_tabla(
        "ke_entrada", 0.5, filas=("concreto_headwall_square_edge",))
    texto = procedencia.como_texto()
    assert "proviene de la fila concreto_headwall_square_edge" in texto
    assert "de la tabla HDS5_3ED.TC2" in texto
    assert "alternativas descartadas:" in texto
    assert procedencia.fecha in texto


def test_una_eleccion_de_columna_se_registra_como_columna():
    """
    Hay elecciones que no son de fila: la categoria de acero es una COLUMNA de
    la Tabla 5.10.1-1. La procedencia tiene que decir cual de las dos cosas
    paso.
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    procedencia = dec.declarar_desde_tabla(
        "categoria_refuerzo_aashto", "A", columnas=("cat_a_mm",))
    assert procedencia.columnas == ("cat_a_mm",)
    assert not procedencia.filas
    assert "proviene de la columna cat_a_mm" in procedencia.como_texto()


def test_el_valor_propuesto_sale_de_la_celda_y_no_se_declara_solo():
    """
    Proponer y declarar estan separados a proposito: la celda es lo que la
    ventana SUGIERE, y el valor que entra al calculo lo confirma quien firma.
    Unirlos convertiria a la ventana en la que elige.
    """
    propuesto = dec.valor_propuesto("HDS5_3ED.TC2",
                                    "concreto_headwall_square_edge", "ke")
    assert propuesto == 0.5  # float-exacto: es la celda transcrita, no un calculo
    assert dec.procedencia_de("ke_entrada") is None


def test_declarar_sobre_una_variable_que_no_es_de_tabla_falla():
    with pytest.raises(ValueError, match="no `de_tabla`"):
        dec.declarar_desde_tabla("v_max_concreto_eleccion", 3.0)


def test_una_variable_que_no_es_criterio_no_se_declara_aqui():
    """
    R4 a nivel de variable: un dato de sitio se determina con un
    procedimiento, no se elige, y `datos_sitio.py` no tiene API de escritura.
    """
    with pytest.raises(ValueError, match="no se declara desde la ventana"):
        dec.declarar_valor("carriles_por_sentido", 2)


# ===========================================================================
# R4 en el camino de declaracion
# ===========================================================================

def test_no_se_puede_elegir_una_fila_bloqueada():
    """
    NOR-SUE-01. La fila «autopista» del Cuadro 4.1 cuelga de los carriles por
    sentido, que el proyecto no tiene.

    Se prueba sobre la guardia y no de punta a punta POR UNA RAZON QUE CONVIENE
    DECIR: hoy ninguna variable `de_tabla` se lee sobre `MS.C41` --- el numero
    de calicatas no lo elige este calculo ---, de modo que no hay ventana desde
    la que intentar la eleccion. La guardia si existe y se ejercita aqui; la
    version de punta a punta es el test de la columna, mas abajo, que si tiene
    variable.
    """
    contenido = vn.contenido_de_tabla("MS.C41")
    with pytest.raises(ValueError, match="R4: la fila 'autopista'"):
        dec._exigir_elegibles(contenido, ("autopista",), ())


def test_no_se_puede_elegir_una_columna_que_pide_un_dato():
    """
    NOR-AAS-01, visto desde OTRA ventana: `situacion_recubrimiento_aashto` no
    es quien elige la categoria de acero, asi que para el sigue siendo un dato
    que falta.
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    with pytest.raises(ValueError, match="R4: la columna 'cat_a_mm'"):
        dec.declarar_desde_tabla("situacion_recubrimiento_aashto", "costera",
                                 columnas=("cat_a_mm",))


def test_el_mensaje_del_rechazo_nombra_lo_que_falta():
    """Un rechazo que no diga que falta deja al usuario sin salida."""
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    with pytest.raises(ValueError) as exc:
        dec.declarar_desde_tabla("situacion_recubrimiento_aashto", "costera",
                                 columnas=("cat_b_mm",))
    assert "categoria_refuerzo_aashto" in str(exc.value)


def test_una_fila_que_no_existe_se_rechaza_antes_de_declarar():
    with pytest.raises(ValueError, match="no tiene la fila"):
        dec.declarar_desde_tabla("ke_entrada", 0.5, filas=("no_existe",))
    assert not ca.declarado_en_caliente("ke_entrada")


def test_una_variable_de_dos_tablas_exige_decir_sobre_cual_se_eligio():
    """
    `DeTabla.tablas` es una tupla porque hay elecciones que se hacen mirando
    dos. Elegir una por el usuario seria adivinar cual miro.
    """
    with pytest.raises(ValueError, match="hay que decir sobre cual"):
        dec.declarar_desde_tabla("h_eq_bajo_altura_tabulada", 0.6)


# ===========================================================================
# Sec. 4.2: validar al escribir, por el tipo del rango
# ===========================================================================

def test_un_valor_por_encima_del_mayor_maximo_es_invalido():
    resultado = dec.validar_en_rango("v_max_concreto_eleccion", 7.0)
    assert resultado.estado is dec.Estado.INVALIDO
    assert not resultado.acepta
    assert "INCUMPLE" in resultado.mensaje


def test_uno_de_los_maximos_que_la_fuente_escribe_es_valido():
    for valor in (3.0, 6.0):
        resultado = dec.validar_en_rango("v_max_concreto_eleccion", valor)
        assert resultado.estado is dec.Estado.VALIDO


def test_un_valor_intermedio_no_incumple_pero_avisa():
    """
    NOR-HID-04, en la validacion. 4.5 no pasa del mayor de los dos maximos ---
    no incumple --- y tampoco lo escribe la fuente. Rechazarlo seria inventar
    una prohibicion; callarlo seria dejar que se lea como si la tabla lo
    trajera.
    """
    resultado = dec.validar_en_rango("v_max_concreto_eleccion", 4.5)
    assert resultado.estado is dec.Estado.AVISO
    assert resultado.acepta
    assert "no manda interpolar" in resultado.mensaje


def test_el_aviso_viaja_en_la_procedencia():
    procedencia = dec.declarar_en_rango("v_max_concreto_eleccion", 4.5)
    assert procedencia.aviso
    assert "AVISO:" in procedencia.como_texto()
    assert procedencia.semantica == "ConjuntoDeMaximos"


def test_un_valor_invalido_no_llega_a_declararse():
    with pytest.raises(ValueError, match="no admite el valor"):
        dec.declarar_en_rango("v_max_concreto_eleccion", 7.0)
    assert not ca.declarado_en_caliente("v_max_concreto_eleccion")


def test_un_texto_donde_hace_falta_un_numero_es_invalido():
    resultado = dec.validar_en_rango("v_max_concreto_eleccion", "rapido")
    assert resultado.estado is dec.Estado.INVALIDO
    assert "no es un numero" in resultado.mensaje


def test_la_validacion_de_un_intervalo_usa_sus_dos_extremos():
    """
    El contraste que hace util a los tests de arriba: cuando la fuente SI
    escribe un piso y un techo, la validacion los usa como tales.
    """
    from normativa.esquema import IntervaloAdmisible, QuePasaFuera
    intervalo = IntervaloAdmisible(
        minimo=1.0, maximo=2.0, unidad="m", cita_id="x",
        que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert dec.validar_contra_rango(intervalo, 1.5).estado is dec.Estado.VALIDO
    assert dec.validar_contra_rango(intervalo, 0.5).estado is dec.Estado.INVALIDO
    assert dec.validar_contra_rango(intervalo, 2.5).estado is dec.Estado.INVALIDO


def test_un_piso_no_se_valida_como_un_techo():
    """
    La razon de que la validacion sea por tipo: con una comparacion generica,
    un piso y un techo se comportarian igual y uno de los dos estaria al
    reves.
    """
    from normativa.esquema import PisoUnico, QuePasaFuera, TechoUnico
    piso = PisoUnico(minimo=2.0, unidad="m", cita_id="x",
                     que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    techo = TechoUnico(maximo=2.0, unidad="m", cita_id="x",
                       que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)
    assert dec.validar_contra_rango(piso, 3.0).estado is dec.Estado.VALIDO
    assert dec.validar_contra_rango(techo, 3.0).estado is dec.Estado.INVALIDO


def test_validar_algo_que_no_es_un_rango_falla():
    # El mensaje lo levanta `frase_del_rango`, que es lo primero que la
    # validacion pide: sin frase que pintar tampoco hay nada que validar.
    with pytest.raises(TypeError, match="no es un rango"):
        dec.validar_contra_rango((3.0, 6.0), 4.0)


# ===========================================================================
# Olvidar
# ===========================================================================

def test_olvidar_retira_el_valor_y_la_procedencia():
    """
    Las dos juntas: una procedencia que hablara de un valor que ya no gobierna
    nada es peor que no tener procedencia.
    """
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    dec.olvidar("ke_entrada")
    assert not ca.declarado_en_caliente("ke_entrada")
    assert dec.procedencia_de("ke_entrada") is None


# ===========================================================================
# SIS-A-18: la sesion
# ===========================================================================

def test_la_sesion_guarda_los_valores_y_las_procedencias():
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    estado = dec.estado_de_sesion()
    assert estado["valores"]["ke_entrada"] == 0.5  # float-exacto: el valor declarado
    assert estado["procedencias"]["ke_entrada"]["filas"] == (
        "concreto_headwall_square_edge",)


def test_la_sesion_sobrevive_a_json_ida_y_vuelta():
    """
    Es lo que de verdad pasa: la sesion se escribe a disco. Un round-trip por
    `json` convierte tuplas en listas, y la procedencia restaurada tiene que
    seguir siendo del mismo tipo que la original --- no un dict parecido que
    la memoria tuviera que tratar aparte.
    """
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    original = dec.procedencia_de("ke_entrada")
    crudo = json.loads(json.dumps(dec.estado_de_sesion(), ensure_ascii=False))

    dec.olvidar("ke_entrada")
    assert dec.procedencia_de("ke_entrada") is None

    resultado = dec.restaurar_sesion(crudo)
    assert "ke_entrada" in resultado.restaurados
    assert not resultado.hubo_rechazos
    restaurada = dec.procedencia_de("ke_entrada")
    assert isinstance(restaurada, dec.Procedencia)
    assert restaurada == original
    assert ca.criterio_efectivo("ke_entrada").valor == 0.5  # float-exacto: el valor restaurado


def test_restaurar_pasa_por_la_guardia_y_no_por_la_puerta_de_atras():
    """
    Un JSON de sesion es un archivo que alguien pudo editar a mano. Un valor
    que la guardia rechaza no entra, y no se descarta en silencio: sale en
    `rechazados`, con el motivo.
    """
    resultado = dec.restaurar_sesion(
        {"valores": {"v_max_concreto_eleccion": 99.0,
                     "no_existe_este_criterio": 1.0}})
    assert not resultado.restaurados
    assert resultado.hubo_rechazos
    claves = {clave for clave, _motivo in resultado.rechazados}
    assert claves == {"v_max_concreto_eleccion", "no_existe_este_criterio"}
    assert all(motivo.strip() for _clave, motivo in resultado.rechazados)


def test_una_sesion_que_no_es_un_objeto_se_rechaza_con_mensaje():
    for basura in ([1, 2], "texto", 3):
        with pytest.raises(ValueError, match="no es un objeto con claves"):
            dec.restaurar_sesion(basura)


def test_una_sesion_sin_bloque_de_valores_no_revienta():
    """Una sesion v1 no traia el bloque: leerla no puede fallar."""
    resultado = dec.restaurar_sesion({})
    assert not resultado.restaurados
    assert not resultado.hubo_rechazos


def test_la_sesion_guarda_tambien_lo_declarado_por_la_cli():
    """
    Los valores salen de `valores_dinamicos()` y no del libro de procedencias:
    una declaracion hecha con `--declarar` o por `conftest` gobierna el calculo
    igual, y una sesion que solo guardara lo de la ventana la perderia en
    silencio.
    """
    ca.establecer_valor_dinamico("TW_receptor", "cota_terreno")
    estado = dec.estado_de_sesion()
    assert "TW_receptor" in estado["valores"]
    assert "TW_receptor" not in estado["procedencias"]
