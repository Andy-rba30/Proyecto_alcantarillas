"""
tests/test_ext4_contexto_corrida.py
===================================
ACEPTACION DE EXT-4: contexto de corrida y sesiones (cluster estado;
EXT-A-01, EXT-A-02, EXT-G-02, PC-07, PC-09, PC-15, PC-16 y la deuda de la
suite: 27 accesos a `_USADOS` en 9 archivos).

Se escribieron primero EN ROJO (`xfail(strict=True)`) con la expectativa del
INVARIANTE --- lo que un informe tiene que decir de SU corrida --- y nunca con
la salida del codigo como oraculo; el xfail se retiro al corregir. Los seis
casos del prompt:

  (a) dos corridas en el mismo proceso: la segunda, detenida en la Fase 2,
      exporta CERO criterios y cero datos de sitio usados. Hasta EXT-4 el
      registro de usos era de PROCESO y nunca se vaciaba (PC-09): la memoria
      de la segunda corrida imprimia como usados los criterios de la primera.
  (b) declarar tras correr y serializar EL MISMO `Informe` da el mismo JSON y
      el mismo HTML, incluida la clave `cota_entrada_origen` de
      `_geometria_json`, que estaba DUPLICADA en el literal dict (PC-07): la
      segunda ganaba y publicaba la regla que gobierna AHORA en el registro,
      no la que produjo la cota impresa al lado.
  (c) editar el CSV tras correr: el `csv_sha1` exportado es el de los bytes
      que M0 leyo, no el del archivo que hay en disco al exportar.
  (d) A declara dos claves; abrir la sesion B vacia deja
      `valores_dinamicos() == {}` y `procedencias() == {}`; y una clave de B
      sin procedencia NO hereda la de A (EXT-A-02: `restaurar_sesion` era
      aditiva y la mezcla se persistia).
  (e) en la GUI: declarar, quitar, cargar sesion o una corrida fallida
      INVALIDAN `self.informe` y apagan los cuatro exportadores diciendo por
      que (PC-15). Aqui, sin Tk, sobre la logica y sobre el arbol; la ventana
      de verdad la mide `tests/apoyo/gui_contexto_real.py` desde
      `test_gui_contrato.py` cuando hay Tk.
  (f) «Etapas bloqueadas» de la GUI es LA MISMA cuenta que la de la CLI sobre
      el mismo `Informe` (EXT-G-02: la GUI decia 12 y la CLI 1, porque una
      contaba lo diferido por alcance y la otra no).

Y las tres guardias que dejan la correccion probada en vez de solo verde: M11
no lee estado global salvo lecturas estaticas (AST), ningun archivo de la
suite toca los registros privados, y el contexto es un objeto congelado.
"""

import ast
import json
import re
import shutil
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import declaracion as dec
from src.modulos import M11_reporte as M11
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
GUI = RAIZ / "gui" / "app.py"
M11_FUENTE = RAIZ / "src" / "modulos" / "M11_reporte.py"

# Los datos externos del corredor de perfil: los mismos de
# `tests/test_cierre_perfil.py`, para que las corridas de aqui y las de alli
# sean comparables.
EXTERNOS_PERFIL = dict(luz_m=3.0, L_hidraulico_m=120.0, TW_m=None,
                       longitud_m=None, categoria_tr=None)
EXTERNOS_POR_PUNTO = {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}}

# Las dos fechas VOLATILES que la memoria imprime y que no describen la
# corrida: la hora local de generacion del HTML y la fecha de modificacion
# del archivo de criterios. Son los mismos patrones que
# `tests/linea_base_familia_c/regenerar.sh` normaliza, por la misma razon.
_FECHA_LOCAL = re.compile(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}")

# Escritos en rojo con `xfail(strict=True)` y liberados al corregir (EXT-4):
# el marcador se retiro y esta linea queda como constancia.


def _normalizada(html: str) -> str:
    return _FECHA_LOCAL.sub("<FECHA>", html)


def _externos(**globales):
    externos = cli.cargar_datos_externos(None, dict(globales))
    for id_punto, datos in EXTERNOS_POR_PUNTO.items():
        externos.por_punto.setdefault(id_punto, {}).update(
            {clave: cli.DatoDeclarado(clave, valor, "datos del expediente")
             for clave, valor in datos.items()})
    return externos


def _corrida_de_perfil(csv=CSV_PERFIL):
    return cli.correr(csv, _externos(**EXTERNOS_PERFIL),
                      alcance=cli.ALCANCE_PERFIL)


def _corrida_sin_luz():
    """Una corrida que se detiene en la Fase 2 sin invocar ningun criterio."""
    externos = cli.cargar_datos_externos(
        None, {"luz_m": None, "TW_m": None, "longitud_m": None,
               "L_hidraulico_m": None, "categoria_tr": None})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)


def _punto_json(datos, id_punto):
    return next(p for p in datos["puntos"] if p["id"] == id_punto)


# ===========================================================================
# (a) Dos corridas en el mismo proceso
# ===========================================================================

def test_a_la_segunda_corrida_del_proceso_exporta_solo_lo_que_ella_uso():
    """
    La primera corrida es de EXPEDIENTE y usa decenas de criterios; la
    segunda se detiene en la Fase 2 por falta de luz y no invoca ninguno. El
    JSON, el volcado y la memoria de la segunda tienen que decirlo.
    """
    primera = cli.correr(CSV_EJEMPLO, _externos(
        luz_m=2.0, TW_m=0.0, longitud_m=14.0, L_hidraulico_m=None,
        categoria_tr=None))
    assert cli.informe_json(primera)["criterios"]["usados"], (
        "la primera corrida tendria que haber invocado criterios: sin eso el "
        "test no distingue nada")

    segunda = _corrida_sin_luz()
    datos = cli.informe_json(segunda)
    assert datos["criterios"]["usados"] == []
    assert datos["datos_sitio"]["usados"] == []
    volcado = cli.volcar(segunda, con_criterios=True)
    assert "No se invoco ningun criterio adoptado." in volcado
    assert "No se invoco ningun dato de sitio." in volcado
    memoria = M11.memoria_html(segunda, proyecto="segunda corrida")
    assert "no invoco ningun criterio adoptado" in memoria
    assert "no invoco ningun dato de sitio" in memoria


def test_a2_el_informe_de_la_primera_corrida_no_cambia_por_la_segunda():
    """La foto es del informe: correr otra vez no le quita usados."""
    primera = cli.correr(CSV_EJEMPLO, _externos(
        luz_m=2.0, TW_m=0.0, longitud_m=14.0, L_hidraulico_m=None,
        categoria_tr=None))
    antes = cli.informe_json(primera)["criterios"]["usados"]
    _corrida_sin_luz()
    assert cli.informe_json(primera)["criterios"]["usados"] == antes


# ===========================================================================
# (b) Declarar tras correr no mueve lo que el informe exporta
# ===========================================================================

def test_b_declarar_tras_correr_no_mueve_el_json_ni_el_html():
    informe = _corrida_de_perfil()
    json_antes = cli.informe_json(informe)
    html_antes = _normalizada(M11.memoria_html(
        informe, proyecto="b", ruta_plantilla=M11.DIR_PLANTILLAS
        / M11.NOMBRE_PLANTILLA_PERFIL))
    texto_antes = cli.volcar(informe, con_criterios=True)

    # Dos declaraciones DESPUES de correr: una pisa la regla de la cota de
    # entrada (que es lo que PC-07 publicaba en caliente) y otra rellena un
    # vacio de Fase 9 que la corrida de perfil ni siquiera invoca.
    ca.establecer_valor_dinamico("origen_cota_fondo_entrada",
                                 "cota_fondo_entrada")
    ca.establecer_valor_dinamico("phi_relleno_trasdos", 32.0)
    try:
        assert cli.informe_json(informe) == json_antes
        assert _normalizada(M11.memoria_html(
            informe, proyecto="b", ruta_plantilla=M11.DIR_PLANTILLAS
            / M11.NOMBRE_PLANTILLA_PERFIL)) == html_antes
        assert cli.volcar(informe, con_criterios=True) == texto_antes
    finally:
        ca.quitar_valor_dinamico("origen_cota_fondo_entrada")
        ca.quitar_valor_dinamico("phi_relleno_trasdos")

    # Y la clave, una sola vez y con lo que la geometria DEL PUNTO dice.
    geometria = _punto_json(json_antes, "A-01")["geometria"]
    origen = geometria["cota_entrada_origen"]
    assert origen["rotulo"] == "ADOPTADA"
    assert origen["adoptada"] is True
    assert origen["regla"] == "cota_terreno"
    assert origen["criterio"] == "origen_cota_fondo_entrada"


def test_b2_la_cota_medida_sale_rotulada_como_medida_y_sin_regla(tmp_path):
    """
    La agravante estatica de PC-07: cualquier punto con `cota_fondo_entrada`
    MEDIDA salia en el JSON como `adoptada: True, regla: 'cota_terreno'`, es
    decir, con el rotulo MEDIDA de la memoria invertido.
    """
    csv = tmp_path / "medida.csv"
    lineas = CSV_PERFIL.read_text(encoding="utf-8").splitlines()
    encabezado = lineas[0].split(",")
    columna = encabezado.index("cota_fondo_entrada")
    fila = lineas[1].split(",")
    assert fila[0] == "A-01" and fila[columna] == ""
    fila[columna] = "41.48"
    lineas[1] = ",".join(fila)
    csv.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    informe = _corrida_de_perfil(csv)
    punto = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert punto.geometria is not None, "A-01 tiene que llegar a la Fase 7"
    origen = _punto_json(cli.informe_json(informe), "A-01")["geometria"][
        "cota_entrada_origen"]
    assert origen["rotulo"] == "MEDIDA"
    assert origen["adoptada"] is False
    assert origen["regla"] is None
    assert "cota_fondo_entrada" in origen["procedencia"]


# ===========================================================================
# (c) El SHA-1 del CSV es el de la corrida
# ===========================================================================

def test_c_editar_el_csv_tras_correr_no_cambia_el_sha1_exportado(tmp_path):
    csv = tmp_path / "corrida.csv"
    shutil.copy(CSV_PERFIL, csv)
    informe = _corrida_de_perfil(csv)
    sha1_de_la_corrida = M11.sha1_archivo(csv)

    with csv.open("a", encoding="utf-8") as f:
        f.write("\n")
    sha1_editado = M11.sha1_archivo(csv)
    assert sha1_editado != sha1_de_la_corrida

    assert cli.informe_json(informe)["expediente"]["csv_sha1"] == (
        sha1_de_la_corrida)
    memoria = M11.memoria_html(
        informe, proyecto="c", ruta_plantilla=M11.DIR_PLANTILLAS
        / M11.NOMBRE_PLANTILLA_PERFIL)
    assert sha1_de_la_corrida in memoria
    assert sha1_editado not in memoria


def test_i_el_contexto_es_una_foto_congelada_de_la_corrida(tmp_path):
    from dataclasses import FrozenInstanceError

    from src.modelos import ContextoCorrida

    csv = tmp_path / "corrida.csv"
    shutil.copy(CSV_PERFIL, csv)
    informe = _corrida_de_perfil(csv)
    contexto = informe.contexto
    assert isinstance(contexto, ContextoCorrida)
    assert contexto.csv_sha1 == M11.sha1_archivo(csv)
    assert contexto.criterios_sha1 == M11.sha1_archivo(M11.ARCHIVO_CRITERIOS)
    assert contexto.criterios_usados, "la corrida de perfil invoca criterios"
    assert set(contexto.criterios_usados) <= set(ca.CRITERIOS)
    assert set(contexto.valores_efectivos) == set(ca.CRITERIOS)
    with pytest.raises(FrozenInstanceError):
        contexto.csv_sha1 = "otro"
    # Copiado en profundidad: mutar lo que el contexto devuelve no lo toca.
    espesor = contexto.valores_efectivos["espesor_pared_conducto"]
    assert espesor is not ca.criterio_efectivo("espesor_pared_conducto").valor
    # Y de solo lectura de verdad: `frozen` solo impide reasignar el campo.
    with pytest.raises(TypeError):
        contexto.valores_efectivos["ke_entrada"] = 9.0
    with pytest.raises(TypeError):
        contexto.procedencias["ke_entrada"] = None
    assert isinstance(contexto.criterios_usados, tuple)


# ===========================================================================
# (d) Abrir una sesion vacia deja el proceso limpio
# ===========================================================================

def test_d_abrir_la_sesion_B_vacia_no_hereda_nada_de_A():
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    ca.establecer_valor_dinamico("phi_relleno_trasdos", 32.0)
    assert "ke_entrada" in ca.valores_dinamicos()
    assert dec.procedencia_de("ke_entrada") is not None

    resultado = dec.restaurar_sesion({"valores": {}, "procedencias": {}})

    assert ca.valores_dinamicos() == {}
    assert dec.procedencias() == {}
    assert set(resultado.retirados) >= {"ke_entrada", "phi_relleno_trasdos"}
    assert dec.estado_de_sesion() == {"valores": {}, "procedencias": {}}


def test_d2_una_clave_de_B_sin_procedencia_no_hereda_la_de_A():
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    de_a = dec.procedencia_de("ke_entrada")
    assert de_a is not None

    dec.restaurar_sesion({"valores": {"ke_entrada": 0.7}, "procedencias": {}})

    assert list(ca.valores_dinamicos()) == ["ke_entrada"]
    assert ca.valores_dinamicos()["ke_entrada"] == pytest.approx(
        0.7, rel=REL_TRANSPORTE)
    assert dec.procedencia_de("ke_entrada") is None, (
        "la memoria de B afirmaria que 0.7 proviene de la fila que A eligio")


def test_d3_un_candidato_rechazado_no_deja_la_sesion_a_medias():
    """
    Se valida TODO en seco antes de vaciar nada: si el archivo trae una clave
    que la guardia rechaza, se restaura lo aceptado y se informa lo demas.
    """
    ca.establecer_valor_dinamico("phi_relleno_trasdos", 32.0)
    resultado = dec.restaurar_sesion({
        "valores": {"ke_entrada": 0.5, "clave_que_no_existe": 1.0},
        "procedencias": {}})
    assert resultado.restaurados == ("ke_entrada",)
    assert [clave for clave, _ in resultado.rechazados] == [
        "clave_que_no_existe"]
    assert "phi_relleno_trasdos" in resultado.retirados
    assert list(ca.valores_dinamicos()) == ["ke_entrada"]
    assert ca.valores_dinamicos()["ke_entrada"] == pytest.approx(
        0.5, rel=REL_TRANSPORTE)


def test_d4_importar_decisiones_no_retira_lo_declarado():
    """`sustituir=False` es «Importar decisiones»: suma, y lo dice."""
    ca.establecer_valor_dinamico("phi_relleno_trasdos", 32.0)
    resultado = dec.restaurar_sesion(
        {"valores": {"ke_entrada": 0.5}, "procedencias": {}},
        sustituir=False)
    assert resultado.retirados == ()
    assert dec.procedencia_de("ke_entrada") is None
    # Lo declarado antes (incluidos los criterios de la corrida de pruebas
    # que `conftest.py` deja puestos) sigue ahi, y lo importado se suma.
    assert ca.valores_dinamicos().items() >= {"phi_relleno_trasdos": 32.0,
                                              "ke_entrada": 0.5}.items()


# ===========================================================================
# (e) La GUI invalida el informe y apaga los exportadores con motivo
# ===========================================================================

class _BotonQueRecuerda:
    """El doble minimo de `BotonAccion`: guarda el ultimo motivo."""

    def __init__(self):
        self.encendido = True
        self.motivo = None

    def habilitar(self):
        self.encendido, self.motivo = True, None

    def deshabilitar(self, motivo):
        self.encendido, self.motivo = False, motivo


def _ventana_con_dobles(app):
    """Una instancia sin widgets: los cuatro exportadores y nada mas."""
    ventana = object.__new__(app.ExpedienteApp)
    for nombre in ("btn_json", "btn_html", "btn_pdf", "btn_csv"):
        setattr(ventana, nombre, _BotonQueRecuerda())
    # Las tablas de las pestañas 3 y 4 son pantalla: aqui no hay. Lo que se
    # prueba es la decision (informe fuera, botones apagados con motivo).
    ventana._vaciar_tablas_del_informe = lambda motivo: None
    return ventana


@pytest.fixture
def app():
    from tests.test_gui_contrato import _con_doble_de_tkinter
    return _con_doble_de_tkinter()


def test_d5_importar_una_clave_sin_procedencia_no_hereda_la_de_la_obra_anterior():
    """
    EXT-A-02 por la puerta de «Importar»: A declaro `ke_entrada` desde la
    fila de la tabla; B la trae sin procedencia. Heredar la de A imprimiria
    «proviene de la fila … (0.5)» al lado de un 0.7.
    """
    dec.declarar_desde_tabla("ke_entrada", 0.5,
                             filas=("concreto_headwall_square_edge",))
    dec.restaurar_sesion({"valores": {"ke_entrada": 0.7}, "procedencias": {}},
                         sustituir=False)
    assert ca.valores_dinamicos()["ke_entrada"] == pytest.approx(
        0.7, rel=REL_TRANSPORTE)
    assert dec.procedencia_de("ke_entrada") is None


def test_e_invalidar_el_informe_apaga_los_cuatro_exportadores_con_motivo(app):
    ventana = _ventana_con_dobles(app)
    ventana.informe = object()
    ventana._invalidar_informe(app.MOTIVO_INFORME_DESACTUALIZADO)
    assert ventana.informe is None
    for nombre in ("btn_json", "btn_html", "btn_pdf", "btn_csv"):
        boton = getattr(ventana, nombre)
        assert not boton.encendido, nombre
        assert boton.motivo == app.MOTIVO_INFORME_DESACTUALIZADO
    assert "vuelva a ejecutar" in app.MOTIVO_INFORME_DESACTUALIZADO.lower()


def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"gui/app.py ya no define {nombre}")


def _llama_a(funcion, nombre):
    return any(isinstance(n, ast.Call) and ast.unparse(n.func) == nombre
               for n in ast.walk(funcion))


ARBOL_GUI = ast.parse(GUI.read_text(encoding="utf-8-sig"), filename="app.py")

GESTOS_QUE_INVALIDAN = ("_aplicar_valor_corrida", "_quitar_valor_corrida",
                        "_tras_declarar_en_ventana", "_guardar_valor_en_archivo",
                        "_restaurar_criterios", "ejecutar_pipeline")


@pytest.mark.parametrize("gesto", GESTOS_QUE_INVALIDAN)
def test_e2_cada_gesto_que_cambia_el_estado_invalida_el_informe(gesto):
    assert _llama_a(_funcion(ARBOL_GUI, gesto), "self._invalidar_informe"), (
        f"{gesto} cambia lo que la proxima corrida usaria y deja el informe "
        "anterior como vigente")


def test_e3_una_corrida_fallida_no_deja_el_informe_anterior_como_vigente():
    """
    `ejecutar_pipeline` invalida ANTES de llamar a `cli.correr`: si la corrida
    falla, no hay informe que exportar, y la ventana lo dice en los botones.
    """
    funcion = _funcion(ARBOL_GUI, "ejecutar_pipeline")
    lineas = {ast.unparse(n.func): n.lineno for n in ast.walk(funcion)
              if isinstance(n, ast.Call)
              and ast.unparse(n.func) in ("self._invalidar_informe",
                                          "cli.correr")}
    assert lineas["self._invalidar_informe"] < lineas["cli.correr"]


def test_e4_una_sesion_deformada_se_rechaza_entera_antes_de_tocar_un_campo(app):
    """
    PC-16: `"externos": null` reventaba con `AttributeError` fuera del
    manejador, con proyecto y CSV ya pisados. El esquema entero se valida
    antes de escribir en ningun `StringVar`, y un externo ausente se repone a
    la cadena vacia en vez de quedarse con el valor de la sesion anterior.
    """
    assert app.errores_de_sesion({"externos": None})
    assert app.errores_de_sesion({"proyecto": 3})
    assert app.errores_de_sesion({"externos": {"luz_m": None}})
    assert app.errores_de_sesion({"criterios": []})
    assert app.errores_de_sesion({"alcance": 7})
    assert app.errores_de_sesion({"formato_version": "2"})
    # El interior de `criterios` tambien: `{"valores": null}` pasaba y
    # `restaurar_sesion` rechazaba DESPUES de pisar proyecto y CSV.
    assert app.errores_de_sesion({"criterios": {"valores": None}})
    assert app.errores_de_sesion({"criterios": {"valores": [1]}})
    assert app.errores_de_sesion({"criterios": {"valores": {},
                                                "procedencias": 3}})
    assert app.errores_de_sesion({"criterios": None}) == []
    assert app.errores_de_sesion({}) == []
    assert app.errores_de_sesion(
        {"proyecto": "x", "csv": "a.csv", "externos": {"luz_m": "2"},
         "alcance": "perfil", "criterios": {"valores": {}},
         "formato_version": 2}) == []

    funcion = _funcion(ARBOL_GUI, "cargar_sesion")
    linea_validacion = next(
        n.lineno for n in ast.walk(funcion) if isinstance(n, ast.Call)
        and ast.unparse(n.func) == "errores_de_sesion")
    primer_set = min(n.lineno for n in ast.walk(funcion)
                     if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)
                     and n.func.attr == "set")
    assert linea_validacion < primer_set


def test_e5_la_ventana_instala_un_manejador_de_excepciones_de_callback():
    """
    Una excepcion dentro de un callback de Tk sale a stderr y la ventana
    sigue como si nada: `report_callback_exception` la convierte en dialogo.
    """
    init = _funcion(ARBOL_GUI, "__init__")
    asignaciones = {ast.unparse(n.targets[0]) for n in ast.walk(init)
                    if isinstance(n, ast.Assign)}
    assert "self.root.report_callback_exception" in asignaciones


# ===========================================================================
# (f) «Etapas bloqueadas»: una sola cuenta para la CLI y la GUI
# ===========================================================================

def test_f_etapas_bloqueadas_es_la_misma_cuenta_en_la_cli_y_en_el_informe():
    informe = _corrida_de_perfil()
    reales = informe.bloqueos_reales()
    assert reales, "la corrida de perfil tiene que dejar algun bloqueo real"
    assert all(not b.diferido_por_alcance for _, b in reales)
    assert len(reales) < len(informe.bloqueos()), (
        "sin diferidos en esta corrida el test no distingue las dos cuentas")

    resumen = informe.resumen()
    assert resumen.bloqueadas == len(reales)
    assert resumen.diferidas == len(informe.diferidos())
    linea = next(l for l in cli._lineas_resumen(informe)
                 if l.startswith("Etapas bloqueadas"))
    assert linea.split(":")[1].strip() == str(len(reales))
    # Y por punto, la misma regla.
    for punto in informe.puntos:
        assert all(not b.diferido_por_alcance
                   for b in punto.bloqueos_reales())


def test_f2_la_gui_y_la_memoria_leen_el_resumen_del_informe_y_no_cuentan():
    """
    Contar en la GUI reproduce la asimetria CLI/GUI (SIS-E-01): la cuenta va
    en `cli.Informe` y las tres capas la LEEN.
    """
    llenar = _funcion(ARBOL_GUI, "_llenar_resumen")
    assert _llama_a(llenar, "informe.resumen")
    assert not _llama_a(llenar, "informe.bloqueos")
    arbol_m11 = ast.parse(M11_FUENTE.read_text(encoding="utf-8"),
                          filename="M11_reporte.py")
    resumen_m11 = _funcion(arbol_m11, "_resumen_expediente")
    assert _llama_a(resumen_m11, "informe.resumen")
    assert not _llama_a(resumen_m11, "informe.bloqueos")


def test_f3_criterios_bloqueantes_distingue_lo_diferido_por_alcance():
    perfil = _corrida_de_perfil()
    por_clave = {c.clave: c for c in cli.criterios_bloqueantes(perfil)}
    remanso = por_clave["remanso_derecho_via"]
    assert remanso.diferido is True, (
        "V5 esta diferida a nivel de perfil: su criterio no bloquea nada")
    expediente = cli.correr(CSV_PERFIL, _externos(**EXTERNOS_PERFIL))
    remanso_exp = {c.clave: c for c in cli.criterios_bloqueantes(expediente)}[
        "remanso_derecho_via"]
    assert remanso_exp.diferido is False
    bloquearon = cli.informe_json(perfil)["criterios"]["bloquearon"]
    assert all("diferido" in fila for fila in bloquearon)


# ===========================================================================
# Las guardias
# ===========================================================================

# Lo que M11 PUEDE leer de los dos catalogos y del libro de declaraciones:
# el ARCHIVO (`CRITERIOS`, `DATOS_SITIO` y sus lectores sin estado). Todo lo
# que pase por `_USADOS`, `_OVERRIDES` o `_PROCEDENCIAS` llega en el
# `ContextoCorrida` del informe.
LECTURAS_ESTATICAS = {
    "ca.CRITERIOS", "ca.criterio", "ca.declaracion_de",
    "ca.criterios_sin_consumidor", "ca.parametros_sensibilizables",
    "ds.DATOS_SITIO", "ds.dato", "ds.datos_sin_valor",
    "ds.datos_con_verificacion_pendiente",
}


MODULOS_CON_ESTADO = {"criterios_adoptados", "datos_sitio", "declaracion"}


def _alias_de_los_modulos_con_estado(arbol):
    """
    Con que nombres importa M11 a los tres modulos con estado, y por donde.
    Un `from criterios_adoptados import criterios_usados`, un import dentro
    de una funcion o un alias nuevo son formas de esquivar la guardia de
    atributos, y se rechazan aqui (auditoria adversarial de EXT-4).
    """
    # Desde EXT-9 los modulos viven en el paquete `src`: `from src import
    # criterios_adoptados as ca` es la forma del alias, y
    # `from src.criterios_adoptados import x` la de los nombres sueltos. El
    # nombre se compara SIN el prefijo del paquete, para que la guardia no
    # quede vacua al cambiar la escritura.
    def _plano(nombre):
        return nombre.split(".", 1)[1] if nombre.startswith("src.") else nombre

    alias = {}
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module \
                and _plano(nodo.module) in MODULOS_CON_ESTADO:
            raise AssertionError(
                f"M11 importa nombres sueltos de {nodo.module}: la guardia "
                "solo puede ver accesos por atributo")
        if isinstance(nodo, ast.ImportFrom) and nodo.module == "src":
            for nombre in nodo.names:
                if nombre.name in MODULOS_CON_ESTADO:
                    alias[nombre.asname or nombre.name] = nombre.name
        if isinstance(nodo, ast.Import):
            for nombre in nodo.names:
                if _plano(nombre.name) in MODULOS_CON_ESTADO:
                    alias[nombre.asname or nombre.name] = _plano(nombre.name)
    for funcion in ast.walk(arbol):
        if isinstance(funcion, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for nodo in ast.walk(funcion):
                if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                    modulos = ([_plano(n.name) for n in nodo.names]
                               if isinstance(nodo, ast.Import)
                               else [_plano(nodo.module or "")]
                               + ([n.name for n in nodo.names]
                                  if nodo.module == "src" else []))
                    assert not set(modulos) & MODULOS_CON_ESTADO, (
                        f"import diferido de un modulo con estado en "
                        f"{funcion.name}")
    return alias


def test_g_M11_no_lee_estado_global_salvo_lecturas_estaticas():
    arbol = ast.parse(M11_FUENTE.read_text(encoding="utf-8"),
                      filename="M11_reporte.py")
    alias = _alias_de_los_modulos_con_estado(arbol)
    assert "declaracion" not in alias.values(), (
        "M11 no importa `declaracion`: las procedencias llegan en el contexto")
    canonico = {"criterios_adoptados": "ca", "datos_sitio": "ds"}
    accesos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Attribute) and isinstance(nodo.value, ast.Name) \
                and nodo.value.id in alias:
            accesos.add(f"{canonico[alias[nodo.value.id]]}.{nodo.attr}")
        if isinstance(nodo, ast.Call) and ast.unparse(nodo.func) == "getattr" \
                and nodo.args and isinstance(nodo.args[0], ast.Name) \
                and nodo.args[0].id in alias:
            raise AssertionError(f"getattr sobre {nodo.args[0].id}: "
                                 "lectura de estado por la puerta de atras")
    assert accesos <= LECTURAS_ESTATICAS, (
        "M11 volvio a leer estado global al exportar: "
        f"{sorted(accesos - LECTURAS_ESTATICAS)}")


def test_g2_la_guardia_de_M11_ve_una_lectura_del_registro_de_usos():
    """La mutacion que la guardia tiene que matar."""
    assert "ca.criterios_usados" not in LECTURAS_ESTATICAS
    assert "ca.criterio_efectivo" not in LECTURAS_ESTATICAS
    assert "ds.datos_usados" not in LECTURAS_ESTATICAS


_PRIVADO = re.compile(
    r"\w+\._(USADOS|OVERRIDES|PROCEDENCIAS)\b"
    r'|setattr\(\s*\w+\s*,\s*"_(USADOS|OVERRIDES|PROCEDENCIAS)"'
    r'|vars\(\s*\w+\s*\)\s*\[\s*"_(USADOS|OVERRIDES|PROCEDENCIAS)"'
    r"|from\s+(criterios_adoptados|datos_sitio|declaracion)\s+import[^\n]*"
    r"\b_(USADOS|OVERRIDES|PROCEDENCIAS)\b")


def test_h_ningun_archivo_de_la_suite_toca_los_registros_privados():
    """
    Los 27 accesos a `_USADOS` en 9 archivos eran la suite haciendo A MANO la
    foto que `cli.correr` no hacia. Con el contexto de corrida y la fixture
    autouse de `conftest.py` --- el UNICO sitio que los toca --- sobran.
    """
    culpables = []
    for ruta in sorted((RAIZ / "tests").rglob("*.py")):
        if "__pycache__" in ruta.parts:
            continue
        for numero, linea in enumerate(
                ruta.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if _PRIVADO.search(linea):
                culpables.append(f"{ruta.relative_to(RAIZ)}:{numero}")
    assert culpables == [], culpables


def test_h2_el_detector_de_privados_ve_las_formas_que_habia():
    # Las formas se arman por concatenacion para que el barrido de arriba no
    # se encuentre a si mismo.
    for forma in ("ca." + "_USADOS.clear()", "previo = set(ds." + "_USADOS)",
                  'monkeypatch.setattr(ds, "' + '_USADOS", set())',
                  "_ca." + "_OVERRIDES[clave] = 1",
                  "dec." + "_PROCEDENCIAS.clear()",
                  "CA." + "_USADOS", 'setattr(_ca, "' + '_USADOS", set())',
                  'vars(ca)["' + '_USADOS"]',
                  "from criterios_adoptados " + "import valor, " + "_USADOS"):
        assert _PRIVADO.search(forma), forma
    assert not _PRIVADO.search("ca.criterios_usados()")
    assert not _PRIVADO.search('"_OVERRIDES" not in objetivo')


def test_h3_las_funciones_publicas_de_reinicio_existen_y_vacian():
    ca.valor("long_max_cuneta")
    ds.valor("PGA_roca_B")
    assert ca.criterios_usados() and ds.datos_usados()
    ca.reiniciar_usos()
    ds.reiniciar_usos()
    assert ca.criterios_usados() == [] and ds.datos_usados() == []
