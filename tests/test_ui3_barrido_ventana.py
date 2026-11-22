"""
tests/test_ui3_barrido_ventana.py
=================================
La aceptacion de UI-3 (cadena de interfaz): EL BOTON «Barrido…» DE LA
PESTAÑA 2, que cierra la ficha PF-3-01.

Hasta UI-3 el barrido de sensibilidad de PF-3 (`src/barrido.py`) solo se
pedia por la linea de comandos (`cli.py --barrido`). Que se vigila, en el
orden del prompt:

(a) El boton: activo solo con un criterio seleccionado que tenga ventana
    (`sensibilidad`) y no se derive; apagado con su motivo en los demas,
    y mientras haya una ventana de barrido abierta.
(b) La puerta EN EL TOPLEVEL: los valores pasan por
    `barrido.verificar_valores` ANTES de lanzar nada; un valor fuera de la
    ventana, o un criterio de tabla sin fila ni nota, se rechaza alli y no
    corre ninguna corrida, y el estado declarado del proceso queda como
    estaba. La fila y la nota son las de «Aplicar» (`editores.declarar`).
(c) Donde corre: en un PROCESO HIJO, la propia CLI con la sesion de la
    ventana (`cli.py --sesion ... --barrido ... --json <temporal>`), sin Tk
    (`gui/proceso_barrido.py`). La tabla se pinta con
    `barrido.lineas_de_la_tabla` sobre el JSON que el hijo escribe
    (`barrido.resultado_del_volcado`), y es la MISMA que la CLI imprime
    para la misma sesion, salvo el segundo en que se declaro cada valor.
    Cancelable; un hijo que falla o que no arranca es un estado terminal
    con su motivo.
(d) Guardias: la ventana del barrido no corre el pipeline ni toca el
    informe vigente ni lo invalida; ningun hilo; los dos modulos nuevos
    entran en las guardias de la capa de presentacion.
(e) La ventana de verdad bajo xvfb (`tests/apoyo/gui_ui3_barrido_real.py`),
    con el barrido de la guia (`docs/guia_perfil.md`, `n_celdas_cajon` =
    1, 2) y el estado de la ventana identico antes y despues.

Escrita PRIMERO, en rojo (`xfail(strict=True)` a nivel de modulo, medida
antes de tocar codigo) y liberada al implementar, como manda el §1 de la
cadena. Los datos son DATOS DE PRUEBA: los archivos de la guia de perfil.

Y lo que la revision independiente de UI-3 encontro (ficha UI3-02), cada
uno con su test: un criterio con claves ENTERAS (`espesor_pared_conducto`)
de ida y vuelta por «Guardar/Cargar», por el hijo del PDF y por el del
barrido (H2, corregido en `declaracion.valor_desde_json`, y comprobado por
mutacion: sin el, los tres fallan y la ventana real tambien), su barrido
(H1), el hijo que no queda huerfano al cerrar la ventana principal (H3), el
barrido anterior que sobrevive a un «Correr» que no arranca (H4), la regla
del boton en src/ con su censo y la divergencia con la CLI medida (H5), el
origen de los [S] (H6), y que la corrida del valor vigente ES la de la
ventana --- no solo que la tabla se pinta --- (H7). Y lo que la verificacion
de esa correccion encontro (N1, ficha UI3-03): el mismo valor con las claves
enteras escritas como texto tiene el MISMO veredicto por todos los caminos
que declaran, y un barrido no cambia el estado de la ventana.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import editores as sed
from src.modelos import CorridaDelBarrido, Derivada, FilaDelBarrido, ResultadoDeBarrido
from tests.apoyo import doble_tkinter
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.doble_tkinter import VariableDeTexto

RAIZ = Path(__file__).resolve().parents[1]
GUI = RAIZ / "gui" / "app.py"
VENTANA_BARRIDO = RAIZ / "gui" / "ventana_barrido.py"
PROCESO_BARRIDO = RAIZ / "gui" / "proceso_barrido.py"
EDITORES_GUI = RAIZ / "gui" / "editores.py"

# El [A] de perfil que la guia barre (seccion 6 de docs/guia_perfil.md).
CLAVE_DE_LA_GUIA = "n_celdas_cajon"
VALORES_DE_LA_GUIA = (1, 2)
# Un [A] de perfil con ventana numerica: la puerta lo rechaza fuera de ella.
CLAVE_CON_RANGO = "HW_D_max"           # ventana (1.2, 1.5)
DENTRO, FUERA = 1.3, 9.9
# Un criterio de tabla: exige fila o nota, como «Aplicar».
CLAVE_DE_TABLA = "ke_entrada"
FILA_KE = "concreto_headwall_square_edge"   # celda 0.5
CLAVE_DE_FILAS = "embocadura_cajon"         # el valor ES la clave de la fila
FILAS_DE_EMBOCADURA = ("cajon_concreto_aletas_30_75", "cajon_concreto_aletas_90_15")
# Sin ventana y derivado: el boton se apaga con su motivo.
CLAVE_SIN_VENTANA = "TR_evento_extremo"
CLAVE_DERIVADA = "coeficiente_escorrentia_superficie_vial"
NOTA = "DATOS DE PRUEBA: barrido de UI-3"
# El segundo de la declaracion, que es lo UNICO en que la tabla de dos
# corridas distintas puede diferir: la procedencia dice cuando se declaro.
SEGUNDO_DE_LA_DECLARACION = re.compile(r"declarado el \d{4}-\d\d-\d\dT\d\d:\d\d:\d\d")
TOPE_DEL_HIJO_S = 600


def _normalizadas(lineas):
    return [SEGUNDO_DE_LA_DECLARACION.sub("declarado el <segundo>", l) for l in lineas]


def _tabla_de_la_salida(stdout: str):
    """Las lineas de `lineas_de_la_tabla` dentro de lo que la CLI imprimio."""
    lineas = stdout.splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.startswith("Barrido de '"))
    fin = next(i for i in range(inicio, len(lineas)) if not lineas[i].strip())
    return lineas[inicio:fin]


def _arbol(ruta):
    return ast.parse(Path(ruta).read_text(encoding="utf-8-sig"), filename=Path(ruta).name)


def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no se encontro la funcion {nombre}")


def _nombres_llamados(nodo):
    return {ast.unparse(n.func) for n in ast.walk(nodo) if isinstance(n, ast.Call)}


def _ultimo_nombre(llamada: str) -> str:
    return llamada.rsplit(".", 1)[-1]


@pytest.fixture
def limpio():
    antes = dec.estado_de_sesion()
    yield
    dec.restaurar_sesion(antes, sustituir=True)


@pytest.fixture(scope="module")
def app():
    return doble_tkinter.gui_app()


@pytest.fixture(scope="module")
def gvb():
    doble_tkinter.instalar()
    import gui.ventana_barrido as modulo
    return modulo


@pytest.fixture(scope="module")
def pbarr():
    import gui.proceso_barrido as modulo
    return modulo


@pytest.fixture(scope="module")
def taller(tmp_path_factory):
    """Los archivos de la guia de perfil, escritos como la guia los muestra."""
    from tests.test_guia_perfil import Taller
    t = Taller(tmp_path_factory.mktemp("guia_ui3"))
    t.preparar()
    return t


class _Widget:
    """El doble minimo de un widget o de un `BotonAccion`."""

    def __init__(self):
        self.texto = ""
        self.color = None
        self.encendido = True
        self.motivo = None
        self.programados = []

    def config(self, **kw):
        if "text" in kw:
            self.texto = kw["text"]
        if "foreground" in kw:
            self.color = kw["foreground"]

    configure = config

    def habilitar(self):
        self.encendido, self.motivo = True, None

    def deshabilitar(self, motivo):
        self.encendido, self.motivo = False, motivo

    def estado(self, encendido, motivo):
        if encendido:
            self.habilitar()
        else:
            self.deshabilitar(motivo)

    def after(self, ms, funcion, *args):
        self.programados.append((ms, funcion))

    def get_children(self):
        return ()

    def delete(self, *a):
        pass

    def insert(self, *a, **k):
        pass

    def selection(self):
        return ()


class _ProcesoDeMentira:
    """Registra que se lanzo y con que; nunca arranca un hijo."""
    lanzados: list = []

    def __init__(self, **kw):
        self.kw = kw
        from gui.proceso_barrido import EstadoDelBarrido
        self.estado = EstadoDelBarrido.SIN_INICIAR
        self.detalle = ""

    def iniciar(self):
        from gui.proceso_barrido import EstadoDelBarrido
        _ProcesoDeMentira.lanzados.append(self.kw)
        self.estado = EstadoDelBarrido.EN_MARCHA

    def limpiar(self):
        pass


def _ventana_de_barrido(gvb, clave, valores, *, fila="", nota="", sesion=None):
    """Una ventana de barrido SIN widgets de verdad: lo que la logica lee."""
    v = object.__new__(gvb.VentanaBarrido)
    v.clave = clave
    v.esquema = sed.esquema_de(clave)
    v.valores = list(valores)
    v.proceso = None
    v.fila_var = VariableDeTexto(fila or gvb.FILA_NINGUNA)
    v.nota_var = VariableDeTexto(nota)
    v.sesion_de_la_ventana = (lambda: dict(sesion or {"csv": "puntos.csv"}))
    for nombre in ("lbl_estado", "btn_correr", "btn_cancelar", "btn_guardar",
                   "btn_anadir", "btn_quitar", "top", "txt_tabla", "lista_valores"):
        setattr(v, nombre, _Widget())
    return v


# ===========================================================================
# (a) El boton «Barrido…»: activo solo con ventana
# ===========================================================================

def _ventana_app(app, abierta=None):
    v = object.__new__(app.ExpedienteApp)
    v.ventana_barrido = abierta
    v.btn_barrido = _Widget()
    return v


def test_a_el_boton_se_enciende_solo_con_un_criterio_con_ventana_que_no_se_deriva(app):
    v = _ventana_app(app)
    assert v._motivo_para_no_barrer(None) == app.MOTIVO_SIN_CRITERIO
    assert v._motivo_para_no_barrer(CLAVE_DE_LA_GUIA) is None
    assert v._motivo_para_no_barrer(CLAVE_CON_RANGO) is None
    assert v._motivo_para_no_barrer(CLAVE_SIN_VENTANA) == app.MOTIVO_SIN_VENTANA
    derivado = ca.criterio(CLAVE_DERIVADA).resolucion
    assert isinstance(derivado, Derivada)
    assert v._motivo_para_no_barrer(CLAVE_DERIVADA) == \
        app.ExpedienteApp._motivo_derivado(derivado)


# LOS CRITERIOS QUE LA VENTANA NO OFRECE BARRER POR FALTA DE VENTANA, censados
# (revision de UI-3, H5): sin `sensibilidad` en su ficha y sin derivarse. Un
# censo y no el predicado reescrito: si un criterio gana o pierde ventana, este
# test lo dice y la divergencia con la CLI de la ficha UI3-01 se revisa.
SIN_VENTANA_EN_LA_VENTANA = frozenset({
    "D_max_norma_producto", "Mw_licuefaccion",
    # VE-5 (ficha T7B-04): sale 'N_cq_N_gammaq_meyerhof' (retirado) y entra
    # 'talud_delante_del_cabezal' ([S] sin valor ni ventana).
    "talud_delante_del_cabezal",
    "PERFIL_SUELO_PRESUNTO", "TR_evento_extremo", "c_phi_fundacion",
    "capacidad_portante_adm", "clase_sitio", "clases_producto_por_relleno",
    "cobertura_minima_aashto", "cortante_alto_muro_e060_art_11_10_10_2",
    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3", "dentellon_losa_entrega",
    "diametros_normalizados", "espesor_min_zapata_concreto_simple_m",
    "exposicion_quimica_ems", "geometria_control_salida", "metodo_estabilidad_global",
    "metodo_transicion_hds5", "peralte_min_zapata_armada_m",
    "peso_especifico_concreto_kn_m3", "peso_especifico_saturado_relleno_kn_m3",
    "procedimiento_flexion_corte_aashto_sec5", "profundidad_cimentacion_min_cabezal_m",
    "resguardo_HW_subrasante", "suelo_agresivo_acero_lrfd",
    # --- VE-4d --- los dos del desborde admitido de V8: el caudal unitario
    # admisible (sin valor: lo da el diseño de la proteccion) y la Figura
    # 3.11 digitalizada (una lectura de figura, sin ventana).
    "caudal_unitario_admisible_desborde_m2s",
    "coeficientes_desborde_plataforma",
    # --- VE-5 (met y mh), censados en VE-6: la integracion de VE-5 los dejo
    # fuera del censo -- el incremento de acero por despiece de los metrados
    # y los factores de la IDF regional [S], sin ventana --.
    "incremento_acero_por_despiece", "factores_idf_regional",
    # --- VE-6 (ficha T7C-10) --- las cuantias minimas de muro del 14.3.1,
    # [N→] sin ventana: el valor es el de la norma aplicada por analogia.
    "cuantia_minima_muro_e060"})
# Y de ellos, los que la puerta de la CLI (`barrido.verificar_valores`, la de
# `cli.py --barrido`) SI deja barrer con el valor de su archivo: la divergencia
# ventana/CLI, MEDIDA, que UI3-01 deja al dueño. La CLI no se cambia.
SIN_VENTANA_QUE_LA_CLI_BARRE = frozenset({
    "D_max_norma_producto", "clases_producto_por_relleno", "cobertura_minima_aashto",
    "cortante_alto_muro_e060_art_11_10_10_2",
    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3", "dentellon_losa_entrega",
    "diametros_normalizados", "espesor_min_zapata_concreto_simple_m",
    "geometria_control_salida", "metodo_transicion_hds5", "peralte_min_zapata_armada_m",
    "peso_especifico_concreto_kn_m3", "procedimiento_flexion_corte_aashto_sec5",
    "profundidad_cimentacion_min_cabezal_m", "resguardo_HW_subrasante",
    "suelo_agresivo_acero_lrfd",
    # --- VE-4d --- la CLI barre la Figura 3.11 con su propio valor de archivo
    # (un dict con campos: la puerta solo comprueba la forma).
    "coeficientes_desborde_plataforma",
    # --- VE-6 (ficha T7C-10) --- y las cuantias del 14.3.1, por lo mismo.
    "cuantia_minima_muro_e060"})


def test_a_la_regla_vive_en_src_y_la_ventana_solo_la_pinta(app, monkeypatch):
    """La ventana devuelve lo que `barrido.motivo_para_no_barrer` diga (H5)."""
    from src import barrido
    v = _ventana_app(app)
    monkeypatch.setattr(barrido, "motivo_para_no_barrer", lambda clave: f"<{clave}>")
    assert v._motivo_para_no_barrer(CLAVE_DE_LA_GUIA) == f"<{CLAVE_DE_LA_GUIA}>"
    monkeypatch.setattr(barrido, "motivo_para_no_barrer", lambda clave: None)
    assert v._motivo_para_no_barrer(CLAVE_SIN_VENTANA) is None
    assert app.MOTIVO_SIN_VENTANA is barrido.MOTIVO_SIN_VENTANA


def test_a_los_criterios_sin_ventana_son_los_del_censo_y_la_cli_barre_los_suyos(limpio):
    from src import barrido
    sin_ventana = {k for k in ca.CRITERIOS
                   if barrido.motivo_para_no_barrer(k) == barrido.MOTIVO_SIN_VENTANA}
    assert sin_ventana == SIN_VENTANA_EN_LA_VENTANA
    derivados = {k for k in ca.CRITERIOS if isinstance(ca.criterio(k).resolucion, Derivada)}
    encendidos = {k for k in ca.CRITERIOS if barrido.motivo_para_no_barrer(k) is None}
    assert len(encendidos) + len(sin_ventana) + len(derivados) == len(ca.CRITERIOS)
    # La divergencia, medida por la MISMA puerta que usa la CLI.
    antes = dec.estado_de_sesion()
    barre = set()
    for clave in sorted(sin_ventana):
        valor = ca.criterio(clave).valor
        if valor is None:
            continue
        try:
            barrido.verificar_valores(clave, (valor,))
        except ValueError:
            continue
        barre.add(clave)
    assert barre == SIN_VENTANA_QUE_LA_CLI_BARRE
    assert dec.estado_de_sesion() == antes


def test_a_con_una_ventana_de_barrido_abierta_el_boton_se_apaga_y_lo_dice(app):
    v = _ventana_app(app, abierta=object())
    v._clave_criterio_seleccionado = CLAVE_DE_LA_GUIA
    assert v._motivo_para_no_barrer(CLAVE_DE_LA_GUIA) == app.MOTIVO_BARRIDO_ABIERTO
    v._pintar_boton_barrido()
    assert not v.btn_barrido.encendido
    assert v.btn_barrido.motivo == app.MOTIVO_BARRIDO_ABIERTO
    v.ventana_barrido = None
    v._pintar_boton_barrido()
    assert v.btn_barrido.encendido


def test_a_seleccionar_un_criterio_pinta_el_boton_en_las_dos_ramas(app):
    """`_al_seleccionar_criterio` repinta el boton con y sin seleccion (por AST)."""
    fn = _funcion(_arbol(GUI), "_al_seleccionar_criterio")
    llamadas = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                and ast.unparse(n.func) == "self._pintar_boton_barrido"]
    assert len(llamadas) >= 2
    atributos = {n.attr for n in ast.walk(_arbol(GUI)) if isinstance(n, ast.Attribute)}
    assert {"btn_barrido", "ventana_barrido"} <= atributos


# ===========================================================================
# (b) La puerta en el Toplevel, antes de lanzar nada
# ===========================================================================

def test_b_un_valor_fuera_de_la_ventana_se_rechaza_sin_lanzar_ningun_hijo(gvb, monkeypatch, limpio):
    _ProcesoDeMentira.lanzados = []
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoDeMentira)
    antes = dec.estado_de_sesion()
    v = _ventana_de_barrido(gvb, CLAVE_CON_RANGO, (DENTRO, FUERA))
    v.correr()
    assert _ProcesoDeMentira.lanzados == []
    assert v.proceso is None
    assert "sensibilidad" in v.lbl_estado.texto
    assert dec.estado_de_sesion() == antes
    assert not ca.declarado_en_caliente(CLAVE_CON_RANGO)


def test_b_la_puerta_del_toplevel_es_verificar_valores_con_la_fila_y_la_nota(gvb, monkeypatch, limpio):
    from src import barrido
    llamadas = []
    original = barrido.verificar_valores
    monkeypatch.setattr(gvb._barrido, "verificar_valores",
                        lambda *a, **k: llamadas.append((a, k)) or original(*a, **k))
    _ProcesoDeMentira.lanzados = []
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoDeMentira)
    v = _ventana_de_barrido(gvb, CLAVE_DE_LA_GUIA, VALORES_DE_LA_GUIA, nota=NOTA)
    v.correr()
    assert llamadas == [((CLAVE_DE_LA_GUIA, tuple(VALORES_DE_LA_GUIA)),
                         {"fila": "", "nota": NOTA})]
    assert len(_ProcesoDeMentira.lanzados) == 1
    lanzado = _ProcesoDeMentira.lanzados[0]
    assert lanzado["clave"] == CLAVE_DE_LA_GUIA
    assert tuple(lanzado["valores"]) == VALORES_DE_LA_GUIA
    assert lanzado["fila"] == "" and lanzado["nota"] == NOTA
    assert not v.btn_correr.encendido and v.btn_cancelar.encendido
    assert v.top.programados, "el sondeo no se programo con `after`"


def test_b_un_criterio_de_tabla_sin_fila_ni_nota_no_corre(gvb, monkeypatch, limpio):
    _ProcesoDeMentira.lanzados = []
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoDeMentira)
    v = _ventana_de_barrido(gvb, CLAVE_DE_TABLA, (0.3, 0.5))
    v.correr()
    assert _ProcesoDeMentira.lanzados == []
    assert "procedencia" in v.lbl_estado.texto
    # Con la nota, la misma lista pasa la puerta (como «Aplicar»).
    v = _ventana_de_barrido(gvb, CLAVE_DE_TABLA, (0.3, 0.5), nota=NOTA)
    v.correr()
    assert len(_ProcesoDeMentira.lanzados) == 1


def test_b_la_fila_elegida_vale_para_todos_y_un_valor_que_difiere_exige_nota(gvb, monkeypatch, limpio):
    from gui.editores import rotulo_de_opcion
    _ProcesoDeMentira.lanzados = []
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoDeMentira)
    esquema = sed.esquema_de(CLAVE_DE_TABLA)
    rotulo = rotulo_de_opcion(next(o for o in esquema.opciones_de_tabla if o.fila == FILA_KE))
    v = _ventana_de_barrido(gvb, CLAVE_DE_TABLA, (0.5,), fila=rotulo)
    assert v._fila() == FILA_KE
    v.correr()
    assert _ProcesoDeMentira.lanzados[-1]["fila"] == FILA_KE
    v = _ventana_de_barrido(gvb, CLAVE_DE_TABLA, (0.3, 0.5), fila=rotulo)
    v.correr()
    assert len(_ProcesoDeMentira.lanzados) == 1
    assert "DIFIERE" in v.lbl_estado.texto


def test_b_sin_fila_cada_clave_tecleada_nombra_su_propia_fila(gvb, monkeypatch, limpio):
    """El barrido de un criterio cuyo valor ES la fila no necesita fila comun."""
    _ProcesoDeMentira.lanzados = []
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoDeMentira)
    v = _ventana_de_barrido(gvb, CLAVE_DE_FILAS, FILAS_DE_EMBOCADURA)
    v.correr()
    assert len(_ProcesoDeMentira.lanzados) == 1, v.lbl_estado.texto
    from gui.editores import rotulo_de_opcion
    esquema = sed.esquema_de(CLAVE_DE_FILAS)
    otra = rotulo_de_opcion(next(o for o in esquema.opciones_de_tabla
                                 if o.fila == FILAS_DE_EMBOCADURA[1]))
    v = _ventana_de_barrido(gvb, CLAVE_DE_FILAS, FILAS_DE_EMBOCADURA, fila=otra, nota=NOTA)
    v.correr()
    assert len(_ProcesoDeMentira.lanzados) == 1
    assert "DISTINTA" in v.lbl_estado.texto or "nombra" in v.lbl_estado.texto


def test_b_sin_valores_o_sin_csv_no_corre_y_lo_dice(gvb, monkeypatch, limpio):
    _ProcesoDeMentira.lanzados = []
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoDeMentira)
    v = _ventana_de_barrido(gvb, CLAVE_DE_LA_GUIA, ())
    v.correr()
    assert v.lbl_estado.texto == gvb.MOTIVO_SIN_VALORES
    v = _ventana_de_barrido(gvb, CLAVE_DE_LA_GUIA, VALORES_DE_LA_GUIA, sesion={"csv": ""})
    v.correr()
    assert _ProcesoDeMentira.lanzados == []
    assert v.lbl_estado.texto == gvb.MOTIVO_SIN_CSV


class _ProcesoTerminado:
    """Un barrido anterior que termino: su tabla y su JSON guardable."""

    def __init__(self):
        from gui.proceso_barrido import EstadoDelBarrido
        self.estado = EstadoDelBarrido.TERMINADO
        self.limpiado = False
        self.copias = []

    def limpiar(self):
        self.limpiado = True

    def copiar_json(self, destino):
        self.copias.append(destino)
        return destino


class _ProcesoQueNoArranca(_ProcesoDeMentira):
    def iniciar(self):
        from gui.proceso_barrido import EstadoDelBarrido
        self.estado = EstadoDelBarrido.FALLIDO
        self.detalle = "No se pudo lanzar el proceso del barrido (prueba)"


def test_b_un_barrido_que_no_arranca_conserva_el_anterior_entero(gvb, monkeypatch, limpio):
    """H4: la tabla anterior y su «Guardar» siguen valiendo, y se dice."""
    monkeypatch.setattr(gvb, "ProcesoBarrido", _ProcesoQueNoArranca)
    v = _ventana_de_barrido(gvb, CLAVE_DE_LA_GUIA, VALORES_DE_LA_GUIA)
    anterior = _ProcesoTerminado()
    v.proceso = anterior
    v.correr()
    assert v.proceso is anterior and not anterior.limpiado
    assert "No se pudo lanzar" in v.lbl_estado.texto
    assert "barrido anterior" in v.lbl_estado.texto
    assert v.btn_guardar.encendido and v.btn_correr.encendido
    assert v.guardar_json(ruta="destino.json") == Path("destino.json")
    assert anterior.copias == [Path("destino.json")]
    # Sin barrido terminado, «Guardar» lo dice en vez de callar.
    v.proceso = None
    assert v.guardar_json(ruta="otro.json") is None
    assert v.lbl_estado.texto == gvb.MOTIVO_SIN_RESULTADO


class _EditorDeMentira:
    def __init__(self, valor=None, error=None):
        self._valor, self._error = valor, error

    def valor(self):
        if self._error:
            raise ValueError(self._error)
        return self._valor


def test_b_anadir_toma_el_valor_del_editor_o_dice_por_que_no(gvb):
    v = _ventana_de_barrido(gvb, CLAVE_CON_RANGO, ())
    v.editor = _EditorDeMentira(error="«valor» = 9.9 cae fuera de la ventana")
    v.anadir_valor()
    assert v.valores == [] and "fuera de la ventana" in v.lbl_estado.texto
    v.editor = _EditorDeMentira(valor=DENTRO)
    v.anadir_valor()
    assert v.valores == pytest.approx([DENTRO], rel=REL_TRANSPORTE)


def test_b_el_editor_sin_campos_se_lee_del_literal_con_el_parser_de_la_ventana(gvb):
    """Un criterio cuyo editor es el LITERAL se teclea entero, como en la pestaña 2."""
    clave = next(k for k in sorted(ca.CRITERIOS)
                 if ca.criterio(k).sensibilidad is not None
                 and sed.esquema_de(k).tipo_de_editor == sed.LITERAL)
    v = _ventana_de_barrido(gvb, clave, ())
    v.literal_var = VariableDeTexto("{'a': [1, 2]}")
    assert v.valor_del_editor() == {"a": [1, 2]}
    v.literal_var = VariableDeTexto("")
    with pytest.raises(ValueError):
        v.valor_del_editor()


def test_b_la_nota_del_toplevel_dice_lo_mismo_que_la_del_editor():
    """Un solo texto por obligatoriedad: el de `gui/editores.py`."""
    doble_tkinter.instalar()
    from gui import editores as ged
    tabla = ged.rotulo_de_la_nota(sed.esquema_de(CLAVE_DE_TABLA))
    libre = ged.rotulo_de_la_nota(sed.esquema_de(CLAVE_DE_LA_GUIA))
    assert tabla != libre and "obligatoria" in tabla and "opcional" in libre
    pie = _funcion(_arbol(EDITORES_GUI), "_pie")
    assert "rotulo_de_la_nota" in {_ultimo_nombre(n) for n in _nombres_llamados(pie)}


# ===========================================================================
# (c) El proceso hijo, sin Tk
# ===========================================================================

@pytest.mark.parametrize("clave,valores", [
    ("HW_D_max", (1.2, 1.35)),
    ("n_celdas_cajon", (1, 2)),
    ("regimen_v2b", ("umbral_duro", "indicador_con_aviso")),
    ("n_manning_hdpe", ((0.009, 0.013), (0.011, 0.015))),
    ("secciones_cajon_normalizadas", ([[1.2, 0.9]], [[1.5, 1.2], [2.0, 1.5]])),
    ("seccion_receptor", ({"b_m": 2.0, "z_HV": 1.5}, {"b_m": 3.0, "z_HV": 1.0})),
    ("sucs_fundacion_deficiente", (("OL", "OH"), ("PT",))),
    ("ke_entrada_cajon", ("texto, con coma", "y 'comillas'")),
])
def test_c_el_texto_del_barrido_lo_lee_la_cli_con_los_mismos_objetos(pbarr, clave, valores):
    texto = pbarr.texto_del_barrido(clave, valores)
    leida, leidos = cli.valores_del_barrido(texto)
    assert leida == clave
    assert [repr(x) for x in leidos] == [repr(x) for x in valores]


def test_c_el_comando_es_el_contrato_con_cli_main(pbarr, tmp_path):
    comando = pbarr.comando_del_barrido(
        interprete="py", cli=Path("cli.py"), sesion=tmp_path / "s.json",
        clave=CLAVE_DE_TABLA, valores=(0.3, 0.5), fila=FILA_KE, nota="-una nota",
        json_salida=tmp_path / "b.json")
    args = cli._parser().parse_args(comando[2:])
    assert args.sesion == tmp_path / "s.json"
    assert args.barridos == [pbarr.texto_del_barrido(CLAVE_DE_TABLA, (0.3, 0.5))]
    assert args.barrido_fila == FILA_KE and args.barrido_nota == "-una nota"
    assert args.json_salida == tmp_path / "b.json"
    sin = pbarr.comando_del_barrido(
        interprete="py", cli=Path("cli.py"), sesion=tmp_path / "s.json",
        clave=CLAVE_DE_LA_GUIA, valores=(1, 2), fila="", nota="",
        json_salida=tmp_path / "b.json")
    args = cli._parser().parse_args(sin[2:])
    assert args.barrido_fila == "" and args.barrido_nota == ""


def test_c_la_sesion_del_hijo_es_la_de_la_ventana_sin_corridas_y_con_el_sitio_de_ejecutar(pbarr):
    viva = {"csv": "p.csv", "datos_sitio": "", "corridas": [{"x": 1}], "csv_sha1": "abc",
            "sitio": {"valores": {"PGA_roca_B": {"valor": 9}}},
            "criterios": {"valores": {"n_celdas_cajon": 1}, "procedencias": {}}}
    abierta = {"valores": {"PGA_roca_B": {"valor": "pga"},
                           "corredor_del_proyecto": {"valor": "x", "origen": "obra.json"}}}
    s = pbarr.sesion_para_el_barrido(viva, sitio_de_la_sesion=abierta)
    assert s["corridas"] == [] and s["csv_sha1"] == ""
    assert s["criterios"] == viva["criterios"]
    # Sin ruta, el bloque de la sesion abierta (lo que EJECUTAR declararia),
    # con el origen que la ventana registra donde la entrada no trae el suyo
    # (H6) y el suyo donde lo trae.
    assert s["sitio"] == {"valores": {
        "PGA_roca_B": {"valor": "pga", "origen": pbarr.ORIGEN_SESION_ABIERTA},
        "corredor_del_proyecto": {"valor": "x", "origen": "obra.json"}}}
    assert "origen" not in abierta["valores"]["PGA_roca_B"], "el bloque abierto no se toca"
    # Con ruta, la ruta: la CLI la relee y el bloque se vacia.
    s = pbarr.sesion_para_el_barrido({**viva, "datos_sitio": "sitio.json"},
                                     sitio_de_la_sesion=abierta)
    assert s["datos_sitio"] == "sitio.json" and s["sitio"] == {"valores": {}}
    assert viva["corridas"] == [{"x": 1}], "la sesion de la ventana no se toca"


def _resultado_sintetico(valores):
    corridas, filas = [], []
    for valor in valores:
        volcado = {"puntos": [{"id": "P-1"}, {"id": "P-2"}]}
        corridas.append(CorridaDelBarrido(
            valor=valor, procedencia=f"declarado el 2026-11-14T00:00:00 · {NOTA}",
            informe_json=volcado, comparacion_con_la_primera=("IGUALES: x",),
            comparable=True))
        for p in ("P-1", "P-2"):
            filas.append(FilaDelBarrido(
                valor=valor, id_punto=p, dimensionado=False, material=None, seccion=None,
                HW_gobernante_m=None, control_gobernante=None,
                verificaciones_que_cambian=("V1",), comparable=False, motivo="m",
                incumplidas_en_la_progresion=("V6", "V7")))
    return ResultadoDeBarrido(clave="n_manning_hdpe", corridas=tuple(corridas),
                              filas=tuple(filas))


def test_c_el_volcado_del_barrido_se_lee_de_vuelta_con_las_mismas_lineas():
    from src import barrido
    valores = ((0.009, 0.013), (0.011, 0.015))
    original = _resultado_sintetico(valores)
    volcado = json.loads(json.dumps(barrido.volcado_del_barrido(original)))
    leido = barrido.resultado_del_volcado(volcado, valores=valores)
    assert barrido.lineas_de_la_tabla(leido) == barrido.lineas_de_la_tabla(original)
    assert leido.filas[0].incumplidas_en_la_progresion == ("V6", "V7")
    # Sin los valores pedidos, JSON no tiene tuplas: el par se lee como lista.
    sin = barrido.resultado_del_volcado(volcado)
    assert [repr(c.valor) for c in sin.corridas] == ["[0.009, 0.013]", "[0.011, 0.015]"]
    # Y unos valores que no son los del JSON no se aceptan en silencio.
    with pytest.raises(ValueError):
        barrido.resultado_del_volcado(volcado, valores=((0.009, 0.013),))
    with pytest.raises(ValueError):
        barrido.resultado_del_volcado(volcado, valores=((0.009, 0.013), (0.02, 0.03)))
    # Un dict con claves ENTERAS (`espesor_pared_conducto`): el JSON las
    # escribe como texto, y la lectura tiene que reconocer lo pedido (H1).
    enteras = ({"hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}},
               {"hdpe": {900: 0.09, 1050: 0.0846, 1200: 0.0985}})
    original = _resultado_sintetico(enteras)
    volcado = json.loads(json.dumps(barrido.volcado_del_barrido(original)))
    leido = barrido.resultado_del_volcado(volcado, valores=enteras)
    assert barrido.lineas_de_la_tabla(leido) == barrido.lineas_de_la_tabla(original)


def _esperar(proceso, tope=TOPE_DEL_HIJO_S):
    limite = time.monotonic() + tope
    while not proceso.sondear().terminal:
        assert time.monotonic() < limite, "el hijo del barrido no termino"
        time.sleep(0.05)
    return proceso.estado


def _sesion_de_la_guia(taller):
    return json.loads((taller.raiz / "guia" / "sesion.json").read_text(encoding="utf-8"))


def test_c_el_hijo_barre_la_guia_y_pinta_las_lineas_de_la_cli(pbarr, taller, tmp_path):
    proceso = pbarr.ProcesoBarrido(
        sesion=_sesion_de_la_guia(taller), clave=CLAVE_DE_LA_GUIA,
        valores=VALORES_DE_LA_GUIA, directorio_trabajo=tmp_path / "trabajo",
        cwd=taller.raiz)
    proceso.iniciar()
    assert _esperar(proceso) is pbarr.EstadoDelBarrido.TERMINADO, proceso.detalle
    assert proceso.resultado.clave == CLAVE_DE_LA_GUIA
    assert tuple(c.valor for c in proceso.resultado.corridas) == VALORES_DE_LA_GUIA
    # La MISMA tabla que la CLI imprime para la misma sesion.
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), "--sesion", "guia/sesion.json",
         "--barrido", "n_celdas_cajon=1,2", "--json", str(tmp_path / "cli.json")],
        cwd=taller.raiz, capture_output=True, text=True, timeout=TOPE_DEL_HIJO_S)
    assert hecho.returncode == 0, hecho.stderr[-3000:]
    assert _normalizadas(proceso.lineas) == _normalizadas(_tabla_de_la_salida(hecho.stdout))
    # Con las dos columnas que la ventana tiene que conservar.
    assert any("no dimensionado" in l and "V6" in l for l in proceso.lineas)
    assert any("NO: " in l for l in proceso.lineas)
    # El JSON que se guarda es el del hijo, el mismo formato que el de la CLI.
    destino = tmp_path / "guardado.json"
    proceso.copiar_json(destino)
    guardado = json.loads(destino.read_text(encoding="utf-8"))
    de_la_cli = json.loads((tmp_path / "cli.json").read_text(encoding="utf-8"))
    assert [b["clave"] for b in guardado["barridos"]] == [b["clave"] for b in de_la_cli["barridos"]]
    assert guardado["barridos"][0]["filas"] == de_la_cli["barridos"][0]["filas"]
    proceso.limpiar()
    assert not (tmp_path / "trabajo").exists()


def test_c_cancelar_termina_el_hijo_sin_resultado(pbarr, taller, tmp_path):
    proceso = pbarr.ProcesoBarrido(
        sesion=_sesion_de_la_guia(taller), clave=CLAVE_DE_LA_GUIA,
        valores=VALORES_DE_LA_GUIA, directorio_trabajo=tmp_path / "trabajo",
        cwd=taller.raiz)
    proceso.iniciar()
    proceso.cancelar()
    assert _esperar(proceso) is pbarr.EstadoDelBarrido.CANCELADO
    assert proceso.resultado is None and proceso.lineas == ()
    assert not proceso.ruta_json.exists()


def test_c_un_hijo_que_rechaza_el_barrido_es_terminal_con_el_motivo_de_la_cli(pbarr, taller, tmp_path):
    """La CLI vuelve a cerrar la puerta: sin la de la ventana, el hijo tampoco corre."""
    proceso = pbarr.ProcesoBarrido(
        sesion=_sesion_de_la_guia(taller), clave=CLAVE_CON_RANGO,
        valores=(DENTRO, FUERA), directorio_trabajo=tmp_path / "trabajo",
        cwd=taller.raiz)
    proceso.iniciar()
    assert _esperar(proceso) is pbarr.EstadoDelBarrido.FALLIDO
    assert "sensibilidad" in proceso.detalle
    assert proceso.resultado is None


HIDRO = RAIZ / "tests" / "fixtures" / "hidrologia"
OBRAS_CON_CUENCA = ("A-01", "A-02", "B-01")


def _csv_sin_caudal(destino: Path) -> Path:
    """El CSV de ejemplo con el `Q_m3s` de las obras con cuenca vaciado (UI-1)."""
    import csv
    with (RAIZ / "tests" / "ejemplo_puntos.csv").open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for fila in filas:
        if fila["id"] in OBRAS_CON_CUENCA:
            fila["Q_m3s"] = ""
    with destino.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


def _app_con_campos(app, *, csv_, externos, sitio_ruta="", cuencas="", estacion="",
                    sitio_de_la_sesion=None):
    """Una ventana SIN widgets con los campos que `_datos_de_sesion` lee."""
    v = object.__new__(app.ExpedienteApp)
    v.proyecto_var = VariableDeTexto("obra UI-3")
    v.csv_var = VariableDeTexto(str(csv_))
    v.datos_externos_var = VariableDeTexto(str(externos))
    v.datos_sitio_var = VariableDeTexto(str(sitio_ruta))
    v.cuencas_var = VariableDeTexto(str(cuencas))
    v.estacion_var = VariableDeTexto(str(estacion))
    v.externos_vars = {clave: VariableDeTexto("") for clave, *_r in app.CAMPOS_EXTERNOS}
    v.externos_vars["luz_m"].set("2,75")
    v.alcance_var = VariableDeTexto(cli.ALCANCE_PERFIL)
    v.sesion_id = "id-ui3"
    v.corridas = []
    v.sitio_de_la_sesion = sitio_de_la_sesion or {"valores": {}}
    return v


def _lo_que_el_hijo_repone(ruta_sesion):
    """
    Lo que el hijo repone de su sesion, por el MISMO camino que `cli.main`
    (`cargar_sesion_serializada` + `aplicar_sesion_serializada`), en este
    proceso y desde el ARCHIVO que el hijo leyo: el estado declarado con sus
    procedencias. Deja el proceso como estaba.
    """
    antes = dec.estado_de_sesion()
    try:
        resultado = cli.aplicar_sesion_serializada(cli.cargar_sesion_serializada(ruta_sesion))
        return dec.estado_de_sesion(), resultado
    finally:
        dec.restaurar_sesion(antes, sustituir=True)


def _iguales(a, b):
    from src import comparador
    lineas = comparador.comparar(a, b).lineas()
    return lineas[0].startswith("IGUALES"), lineas[:6]


def test_c_el_hijo_barre_con_la_hidrologia_y_las_procedencias_de_la_ventana(app, pbarr, tmp_path, limpio):
    """
    La sesion del hijo ES el estado de la ventana: lo que el hijo repone de
    su archivo --- valores Y procedencias --- es lo declarado en la ventana,
    y la corrida del primer valor (el vigente) reproduce la que la ventana
    haria con la hidrologia de UI-1 (revision de UI-3, H7).
    """
    import hashlib
    from src import servicio
    dec.declarar_valor("homogeneidad_serie_fen", "serie_completa", nota=NOTA)
    v = _app_con_campos(
        app, csv_=_csv_sin_caudal(tmp_path / "p.csv"),
        externos=RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        cuencas=HIDRO / "cuencas_prueba.csv", estacion=HIDRO / "estacion_prueba.csv")
    de_la_ventana = dec.estado_de_sesion()
    sesion = v._sesion_para_el_barrido()
    assert sesion["cuencas"] == str(HIDRO / "cuencas_prueba.csv")
    assert sesion["estacion"] == str(HIDRO / "estacion_prueba.csv")
    vigente = ca.criterio_efectivo("distribucion_precipitacion_maxima").valor
    proceso = pbarr.ProcesoBarrido(
        sesion=sesion, clave="distribucion_precipitacion_maxima",
        valores=(vigente, "gumbel"), directorio_trabajo=tmp_path / "trabajo")
    proceso.iniciar()
    assert _esperar(proceso) is pbarr.EstadoDelBarrido.TERMINADO, proceso.detalle
    repuesto, restauracion = _lo_que_el_hijo_repone(proceso.ruta_sesion)
    assert repuesto == de_la_ventana
    assert dec.procedencia_de("homogeneidad_serie_fen").nota == NOTA
    assert set(restauracion.restaurados) == set(de_la_ventana["valores"])
    assert not restauracion.hubo_rechazos
    salida = proceso.ruta_salida.read_text(encoding="utf-8")
    assert "homogeneidad_serie_fen" in salida and "NO se restauro" not in salida
    huella = hashlib.sha1((HIDRO / "cuencas_prueba.csv").read_bytes()).hexdigest()
    for corrida in proceso.resultado.corridas:
        hidro = corrida.informe_json["expediente"]["hidrologia"]
        assert hidro["cuencas_sha1"] == huella
        assert set(OBRAS_CON_CUENCA) <= set(hidro["obras_con_cuenca"])
    # La corrida del valor vigente es la que la ventana haria con ese valor
    # declarado (el barrido lo declara en cada corrida).
    sed.declarar("distribucion_precipitacion_maxima", vigente)
    externos = cli.cargar_datos_externos(Path(v.datos_externos_var.get()), v._leer_banderas())
    informe = servicio.correr(Path(v.csv_var.get()), externos, alcance=cli.ALCANCE_PERFIL,
                              hidrologia=cli.cargar_hidrologia(*v._rutas_de_hidrologia()))
    iguales, lineas = _iguales(cli.informe_json(informe),
                               proceso.resultado.corridas[0].informe_json)
    assert iguales, lineas
    proceso.limpiar()


# ---------------------------------------------------------------------------
# H2 · una declaracion con claves NO textuales, de ida y vuelta por las tres
# puertas que serializan la sesion: «Guardar/Cargar», el hijo del barrido y el
# hijo del PDF (EXT-8). JSON escribe las claves enteras como texto.
# ---------------------------------------------------------------------------

ESPESOR = "espesor_pared_conducto"   # dict por material con el diametro (mm, entero) de clave


@pytest.fixture
def limpio_con_sitio():
    antes = dec.estado_de_sesion()
    sitio = dec.estado_de_sitio_de_sesion()
    yield
    dec.restaurar_sesion(antes, sustituir=True)
    dec.restaurar_datos_de_sitio(sitio, sustituir=True, origen="test UI-3")


def _pisar_espesor_con_el_mismo_valor():
    valor = ca.criterio(ESPESOR).valor
    assert any(isinstance(k, int) for sub in valor.values() for k in sub)
    sed.declarar(ESPESOR, valor, nota=NOTA)
    return valor


def _correr_ejemplo():
    from src import servicio
    externos = cli.cargar_datos_externos(
        RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        {"luz_m": "2.75", "TW_m": None, "longitud_m": None, "L_hidraulico_m": None,
         "categoria_tr": None})
    return servicio.correr(RAIZ / "tests" / "ejemplo_puntos.csv", externos,
                           alcance=cli.ALCANCE_PERFIL)


def test_h2_guardar_y_cargar_reponen_el_mismo_valor_con_sus_claves_enteras(tmp_path, limpio):
    from src import sesion as ses
    valor = _pisar_espesor_con_el_mismo_valor()
    antes = dec.estado_de_sesion()
    volcado = cli.informe_json(_correr_ejemplo())
    sesion = ses.sesion_vacia("UI-3")
    sesion.update(csv=str(RAIZ / "tests" / "ejemplo_puntos.csv"), criterios=antes)
    ruta = tmp_path / "s.json"
    ses.escribir_json_atomico(ruta, sesion)
    escrito = json.loads(ruta.read_text(encoding="utf-8"))
    assert set(escrito["criterios"]["valores"][ESPESOR]["hdpe"]) == {"900", "1050", "1200"}
    # Por la puerta de la ventana («Cargar sesion» -> restaurar_sesion)...
    dec.restaurar_sesion(escrito["criterios"], sustituir=True)
    assert dec.estado_de_sesion() == antes
    assert repr(ca.valores_dinamicos()[ESPESOR]) == repr(valor)
    assert repr(dec.procedencia_de(ESPESOR).valor) == repr(valor)
    iguales, lineas = _iguales(volcado, cli.informe_json(_correr_ejemplo()))
    assert iguales, lineas
    # ...y por la de la CLI (`--sesion`).
    repuesto, restauracion = _lo_que_el_hijo_repone(ruta)
    assert repuesto == antes
    assert set(restauracion.restaurados) == set(antes["valores"])


def test_h2_el_hijo_del_pdf_reproduce_la_corrida_con_claves_enteras(tmp_path, limpio):
    """La sesion que EXT-8 le pasa al hijo, sin tocar gui/exportacion_pdf.py."""
    from gui import exportacion_pdf as expdf
    from src import sesion as ses
    _pisar_espesor_con_el_mismo_valor()
    informe = _correr_ejemplo()
    sesion = expdf.sesion_de_la_corrida(
        informe, proyecto="UI-3", csv=str(RAIZ / "tests" / "ejemplo_puntos.csv"),
        datos_externos=str(RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"),
        externos={"luz_m": "2.75"}, alcance=cli.ALCANCE_PERFIL,
        formato_version=ses.FORMATO_SESION, app_version="UI-3")
    assert ESPESOR in sesion["criterios"]["valores"]
    ruta = tmp_path / "sesion_pdf.json"
    ses.escribir_json_atomico(ruta, sesion)
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), "--sesion", str(ruta),
         "--json", str(tmp_path / "hijo.json")],
        cwd=RAIZ, capture_output=True, text=True, timeout=TOPE_DEL_HIJO_S)
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    del_hijo = json.loads((tmp_path / "hijo.json").read_text(encoding="utf-8"))
    propio = json.loads(json.dumps(cli.informe_json(informe), ensure_ascii=False))
    assert ses.sin_marca_de_tiempo(del_hijo) == ses.sin_marca_de_tiempo(propio)


def test_h2_h6_h7_el_hijo_del_barrido_es_el_estado_de_la_ventana(app, pbarr, taller, tmp_path,
                                                                   limpio_con_sitio):
    """
    Con `espesor_pared_conducto` pisado (con el MISMO valor del archivo), un
    criterio declarado con su nota y los [S] del bloque de la sesion abierta
    SIN origen por entrada: el hijo repone exactamente lo declarado, registra
    el origen que la ventana registra, y la corrida del valor vigente es la
    corrida de la ventana.
    """
    from src import servicio
    guia = taller.raiz / "guia"
    bloque = {"valores": json.loads((guia / "sitio.json").read_text(encoding="utf-8"))}
    assert not any("origen" in e for e in bloque["valores"].values())
    v = _app_con_campos(app, csv_=guia / "puntos.csv", externos=guia / "externos.json",
                        sitio_de_la_sesion=bloque)
    _pisar_espesor_con_el_mismo_valor()
    sed.declarar(CLAVE_DE_LA_GUIA, 1, nota=NOTA)
    de_la_ventana = dec.estado_de_sesion()
    # Lo que EJECUTAR haria: el bloque de la sesion abierta, y correr.
    assert v._declarar_datos_de_sitio("") is None
    externos = cli.cargar_datos_externos(guia / "externos.json", v._leer_banderas())
    volcado_ventana = cli.informe_json(servicio.correr(
        guia / "puntos.csv", externos, alcance=cli.ALCANCE_PERFIL))
    sesion = v._sesion_para_el_barrido()
    assert all(e["origen"] == pbarr.ORIGEN_SESION_ABIERTA
               for e in sesion["sitio"]["valores"].values())
    proceso = pbarr.ProcesoBarrido(sesion=sesion, clave=CLAVE_DE_LA_GUIA, valores=(1, 2),
                                   directorio_trabajo=tmp_path / "trabajo")
    proceso.iniciar()
    assert _esperar(proceso) is pbarr.EstadoDelBarrido.TERMINADO, proceso.detalle
    repuesto, restauracion = _lo_que_el_hijo_repone(proceso.ruta_sesion)
    assert repuesto == de_la_ventana
    assert {ESPESOR, CLAVE_DE_LA_GUIA} <= set(restauracion.restaurados)
    assert set(restauracion.restaurados) == set(de_la_ventana["valores"])
    primera = proceso.resultado.corridas[0].informe_json
    iguales, lineas = _iguales(volcado_ventana, primera)
    assert iguales, lineas
    assert all(p["dimensionado"] for p in primera["puntos"])
    # Los origenes que el comparador no compara, uno a uno (H6).
    assert primera["expediente"]["corredor_del_proyecto"]["origen"] == \
        volcado_ventana["expediente"]["corredor_del_proyecto"]["origen"]
    assert [u["origen"] for u in primera["datos_sitio"]["usados"]] == \
        [u["origen"] for u in volcado_ventana["datos_sitio"]["usados"]]
    assert "sesion_para_el_barrido" not in json.dumps(primera, ensure_ascii=False)
    proceso.limpiar()


def test_h1_el_hijo_barre_un_criterio_de_claves_enteras(pbarr, taller, tmp_path):
    """`espesor_pared_conducto` terminaba siempre FALLIDO al leer el JSON del hijo."""
    archivo = ca.criterio(ESPESOR).valor
    otro = {**archivo, "concreto_reforzado": {**archivo["concreto_reforzado"], 900: 0.11}}
    proceso = pbarr.ProcesoBarrido(
        sesion=_sesion_de_la_guia(taller), clave=ESPESOR, valores=(archivo, otro),
        directorio_trabajo=tmp_path / "trabajo", cwd=taller.raiz)
    proceso.iniciar()
    assert _esperar(proceso) is pbarr.EstadoDelBarrido.TERMINADO, proceso.detalle
    assert [repr(c.valor) for c in proceso.resultado.corridas] == [repr(archivo), repr(otro)]
    assert proceso.lineas[0].startswith(f"Barrido de '{ESPESOR}'")
    proceso.limpiar()


def test_h3_terminar_y_limpiar_no_deja_hijo_ni_carpeta(pbarr, taller, tmp_path):
    proceso = pbarr.ProcesoBarrido(
        sesion=_sesion_de_la_guia(taller), clave=CLAVE_DE_LA_GUIA,
        valores=VALORES_DE_LA_GUIA, directorio_trabajo=tmp_path / "trabajo",
        cwd=taller.raiz)
    proceso.iniciar()
    assert proceso.estado is pbarr.EstadoDelBarrido.EN_MARCHA
    proceso.terminar_y_limpiar()
    assert proceso._proceso.poll() is not None
    assert proceso.estado.terminal
    assert not (tmp_path / "trabajo").exists()
    # Sin arrancar, tambien deja el temporal limpio.
    nunca = pbarr.ProcesoBarrido(sesion={}, clave=CLAVE_DE_LA_GUIA, valores=(1,))
    carpeta = nunca.directorio_trabajo
    assert carpeta.exists()
    nunca.terminar_y_limpiar()
    assert not carpeta.exists()


# ---------------------------------------------------------------------------
# N1 · el MISMO valor, el MISMO veredicto por todos los caminos que declaran.
# Un dict de `espesor_pared_conducto` con las claves enteras escritas como
# texto (copiado de un JSON) entraba por «Aplicar» y por `--declarar`, la
# corrida no encontraba la fila, y el barrido --- que repone por la frontera
# del JSON --- si la encontraba y cambiaba el estado de la ventana.
# ---------------------------------------------------------------------------

def _caminos_que_declaran(valor):
    from src import barrido
    return {
        "pestaña 2 y editores (editores.declarar)": lambda: sed.declarar(ESPESOR, valor),
        "ventana emergente (declaracion.declarar_valor)":
            lambda: dec.declarar_valor(ESPESOR, valor),
        "cli --declarar": lambda: cli.declarar_criterios([f"{ESPESOR}={valor!r}"]),
        "barrido (verificar_valores)": lambda: barrido.verificar_valores(ESPESOR, (valor,)),
        "barrido, declaraciones de base": lambda: barrido.verificar_valores(
            CLAVE_CON_RANGO, (DENTRO,), declaraciones_base={ESPESOR: valor}),
    }


def test_n1_todas_las_puertas_rechazan_igual_la_clave_entera_escrita_como_texto(limpio):
    archivo = ca.criterio(ESPESOR).valor
    de_texto = json.loads(json.dumps(archivo))
    antes = dec.estado_de_sesion()
    mensajes = {}
    for camino, declarar in _caminos_que_declaran(de_texto).items():
        with pytest.raises(ValueError) as rechazo:
            declarar()
        mensajes[camino] = str(rechazo.value)
        assert dec.estado_de_sesion() == antes, camino
    assert len(set(mensajes.values())) == 1, mensajes
    assert "Escriba 900 sin comillas" in next(iter(mensajes.values()))


def test_n1_el_valor_bien_escrito_deja_el_mismo_estado_por_todos_los_caminos(limpio):
    archivo = ca.criterio(ESPESOR).valor
    antes = dec.estado_de_sesion()
    for camino, declarar in _caminos_que_declaran(archivo).items():
        dec.restaurar_sesion(antes, sustituir=True)
        declarar()
        if camino.startswith("barrido"):
            # La puerta del barrido declara y repone: pasa, y no deja nada.
            assert dec.estado_de_sesion() == antes, camino
            continue
        efectivo = ca.criterio_efectivo(ESPESOR).valor
        assert repr(efectivo) == repr(archivo), camino
    dec.restaurar_sesion(antes, sustituir=True)
    # Y la frontera del JSON da el mismo valor: lo que JSON escribe de el.
    dec.restaurar_sesion({"valores": {ESPESOR: json.loads(json.dumps(archivo))}},
                         sustituir=True)
    assert repr(ca.valores_dinamicos()[ESPESOR]) == repr(archivo)
    # Una clave que no es un entero escrito no la arregla ni el JSON: se
    # rechaza con el mismo motivo que en las puertas.
    resultado = dec.restaurar_sesion(
        {"valores": {ESPESOR: {"hdpe": {"900mm": 0.09}}}}, sustituir=False)
    assert [c for c, _m in resultado.rechazados] == [ESPESOR]
    assert "ENTERAS" in resultado.rechazados[0][1]


def test_n1_un_barrido_no_cambia_el_estado_con_el_valor_declarado(limpio):
    """El estado de la ventana con el criterio de claves enteras, antes y despues."""
    from src import barrido
    archivo = ca.criterio(ESPESOR).valor
    sed.declarar(ESPESOR, archivo, nota=NOTA)
    antes = dec.estado_de_sesion()
    barrido.verificar_valores(CLAVE_CON_RANGO, (DENTRO, 1.5))
    barrido.verificar_valores(ESPESOR, (archivo,), nota=NOTA)
    assert dec.estado_de_sesion() == antes
    assert repr(ca.valores_dinamicos()[ESPESOR]) == repr(archivo)


def test_n1_la_cli_rechaza_igual_la_corrida_y_el_barrido_con_esa_declaracion(tmp_path):
    """
    Con la clave de texto, `--declarar` y `--declarar` + `--barrido` salen
    con 2 y el MISMO motivo, antes de correr nada. Hasta la revision de UI-3
    (en 4066a24 tambien) la corrida normal corria con tres puntos «no
    dimensionado»; la salida de la CLI con esta entrada cambio (ficha UI3-03).
    """
    de_texto = json.loads(json.dumps(ca.criterio(ESPESOR).valor))
    base = [sys.executable, str(RAIZ / "cli.py"), str(RAIZ / "tests" / "ejemplo_puntos.csv"),
            "--alcance", "perfil", "--luz", "2.75", "--declarar", f"{ESPESOR}={de_texto!r}"]
    normal = subprocess.run(base + ["--json", str(tmp_path / "a.json")], cwd=RAIZ,
                            capture_output=True, text=True, timeout=TOPE_DEL_HIJO_S)
    barre = subprocess.run(base + ["--barrido", f"{CLAVE_CON_RANGO}=1.5",
                                   "--json", str(tmp_path / "b.json")],
                           cwd=RAIZ, capture_output=True, text=True, timeout=TOPE_DEL_HIJO_S)
    assert normal.returncode == barre.returncode == 2
    assert normal.stderr.strip() == barre.stderr.strip()
    assert "sin comillas" in normal.stderr
    assert not (tmp_path / "a.json").exists() and not (tmp_path / "b.json").exists()


def test_c_un_hijo_que_no_arranca_es_terminal_y_no_queda_en_marcha(pbarr, tmp_path):
    proceso = pbarr.ProcesoBarrido(
        sesion={"csv": "x"}, clave=CLAVE_DE_LA_GUIA, valores=VALORES_DE_LA_GUIA,
        directorio_trabajo=tmp_path / "trabajo",
        interprete=str(tmp_path / "no_existe_este_interprete"))
    proceso.iniciar()
    assert proceso.estado is pbarr.EstadoDelBarrido.FALLIDO
    assert "No se pudo lanzar" in proceso.detalle


# ===========================================================================
# (d) Guardias
# ===========================================================================

def test_d_la_ventana_del_barrido_no_corre_el_pipeline_ni_toca_el_informe():
    for ruta in (VENTANA_BARRIDO, PROCESO_BARRIDO):
        arbol = _arbol(ruta)
        llamadas = {_ultimo_nombre(n) for n in _nombres_llamados(arbol)}
        assert not llamadas & {"correr", "barrer", "informe_json", "correr_punto"}, ruta
        importados = {a.name for n in ast.walk(arbol) if isinstance(n, ast.Import)
                      for a in n.names}
        importados |= {n.module for n in ast.walk(arbol)
                       if isinstance(n, ast.ImportFrom) and n.module}
        assert "threading" not in importados, f"{ruta.name}: el barrido no va por hilo"
        assert not [m for m in importados if m.startswith("src.modulos")], ruta
        atributos = {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
        assert "informe" not in atributos, f"{ruta.name} lee o escribe el informe"
    arbol = _arbol(GUI)
    for nombre in ("_abrir_barrido", "_tras_cerrar_barrido", "_sesion_para_el_barrido",
                   "_pintar_boton_barrido", "_motivo_para_no_barrer"):
        fn = _funcion(arbol, nombre)
        assert "self._invalidar_informe" not in _nombres_llamados(fn), nombre
        asignados = {ast.unparse(t) for n in ast.walk(fn) if isinstance(n, ast.Assign)
                     for t in n.targets}
        assert "self.informe" not in asignados, nombre


def test_d_el_barrido_se_sondea_con_after_y_al_cerrar_se_refresca_la_pestana_2():
    arbol = _arbol(VENTANA_BARRIDO)
    sondeo = _funcion(arbol, "_sondear")
    assert any(_ultimo_nombre(n) == "after" for n in _nombres_llamados(sondeo))
    llamadas = {_ultimo_nombre(n) for n in _nombres_llamados(arbol)}
    assert not llamadas & {"wait", "communicate"}, "la ventana no espera al hijo"
    tras = _funcion(_arbol(GUI), "_tras_cerrar_barrido")
    assert "self._llenar_tabla_criterios" in _nombres_llamados(tras)


def test_d_ningun_manejador_de_los_modulos_nuevos_se_traga_todo():
    for ruta in (VENTANA_BARRIDO, PROCESO_BARRIDO):
        culpables = [n.lineno for n in ast.walk(_arbol(ruta))
                     if isinstance(n, ast.ExceptHandler)
                     and (n.type is None or ast.unparse(n.type) == "BaseException")]
        assert not culpables, f"{ruta.name}: {culpables}"


def test_d_los_modulos_nuevos_entran_en_la_guardia_de_literales():
    constantes = {n.value for n in ast.walk(_arbol(RAIZ / "tests" / "test_sin_literales.py"))
                  if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert {"gui/ventana_barrido.py", "gui/proceso_barrido.py"} <= constantes


def test_d_el_volcado_del_barrido_sigue_siendo_lo_que_la_cli_escribe():
    """`resultado_del_volcado` es el inverso; `volcado_del_barrido` no cambio de claves."""
    from src import barrido
    volcado = barrido.volcado_del_barrido(_resultado_sintetico((1, 2)))
    assert set(volcado) == {"clave", "corridas", "filas"}
    assert set(volcado["corridas"][0]) == {"valor", "procedencia", "informe_json",
                                           "comparacion_con_la_primera", "comparable"}


# ===========================================================================
# (e) La ventana de verdad
# ===========================================================================

def _interprete_con_ventana():
    from tests.test_gui_contrato import _ENVOLTORIO, _INTERPRETE
    return _INTERPRETE, _ENVOLTORIO


@pytest.mark.lento
def test_e_la_ventana_real_barre_la_guia_sin_tocar_el_estado_ni_el_informe(tmp_path):
    interprete, envoltorio = _interprete_con_ventana()
    if interprete is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    doble_tkinter.instalar()
    import gui.app as gapp
    hecho = subprocess.run(
        envoltorio + [interprete, "-m", "tests.apoyo.gui_ui3_barrido_real", str(tmp_path)],
        cwd=RAIZ, capture_output=True, text=True, timeout=1500)
    assert hecho.returncode == 0, (
        f"la corrida de la GUI fallo:\n{hecho.stdout[-4000:]}\n{hecho.stderr[-4000:]}")
    r = json.loads((tmp_path / "resumen_ui3.json").read_text(encoding="utf-8"))

    # 1. El boton, por criterio, en la ventana de verdad.
    b = r["boton"]
    assert b[CLAVE_DE_LA_GUIA] == {"encendido": True, "motivo": None}
    assert b[CLAVE_CON_RANGO] == {"encendido": True, "motivo": None}
    assert b[CLAVE_SIN_VENTANA] == {"encendido": False, "motivo": gapp.MOTIVO_SIN_VENTANA}
    assert not b[CLAVE_DERIVADA]["encendido"] and b[CLAVE_DERIVADA]["motivo"]
    assert b["con_barrido_abierto"] == {"encendido": False,
                                        "motivo": gapp.MOTIVO_BARRIDO_ABIERTO}
    assert r["visible_el_motivo"].startswith(f"No disponible: {gapp.MOTIVO_SIN_VENTANA}")
    assert r["visible_en_la_geometria_por_defecto"]

    # 2. Fuera de la ventana: el editor no lo deja añadir, y la puerta no corre.
    f = r["fuera"]
    assert f["anadido_por_el_editor"] is False
    assert f["valores_tras_anadir"] == pytest.approx([DENTRO], rel=REL_TRANSPORTE)
    assert f["proceso_es_None"] and "sensibilidad" in f["estado"]
    assert f["estado_de_sesion_igual"]

    # 3. El barrido de la guia: corre en un proceso hijo, la ventana responde.
    g = r["guia"]
    assert g["estado"] == "terminado", g["detalle"]
    assert g["pid_del_hijo"] != g["pid_de_la_ventana"]
    assert g["latidos_mientras_corria"] > 0
    assert g["informe_igual_mientras_corria"] and g["estado_igual_mientras_corria"]
    assert g["sin_fila_en_un_criterio_libre"] and g["nota_presente"]
    assert g["lista_tras_quitar"] == [["1", "1"], ["2", "2"]]
    # Las MISMAS lineas que la CLI imprime para la misma sesion.
    assert _normalizadas(g["lineas_ventana"]) == _normalizadas(g["lineas_cli"])
    assert any("no dimensionado" in l and "V6" in l for l in g["lineas_ventana"])
    assert any("NO: " in l for l in g["lineas_ventana"])
    assert g["json_guardado_igual_al_del_hijo"]
    # La sesion del hijo ES el estado de la ventana (H2, H7): con
    # `espesor_pared_conducto` pisado (claves enteras), la corrida del valor
    # vigente es la de la ventana y dimensiona los cuatro puntos.
    assert r["pisado"]
    # N1: copiado de un JSON (claves de texto), «Aplicar» lo rechaza y lo dice.
    assert not r["clave_de_texto"]["declarado"]
    assert "sin comillas" in r["clave_de_texto"]["rotulo"]
    assert g["primera_igual_a_la_ventana"], g["comparacion_con_la_ventana"]
    assert g["primera_dimensiona_todo"] and g["origenes_iguales"]
    assert g["boton_guardar_tras_terminar"]

    # 4. Cancelable.
    c = r["cancelado"]
    assert c["estado"] == "cancelado" and not c["guardar_encendido"]

    # 5. Al cerrar: la pestaña 2 se refresca y nada de la ventana cambio.
    d = r["despues"]
    assert d["refrescos_al_cerrar"] >= 1 and d["ventana_barrido_es_None"]
    assert d["boton_encendido"]
    assert d["estado_de_sesion_igual"] and d["sitio_igual"]
    assert d["informe_es_el_mismo"] and d["volcado_igual"]
    assert d["exportadores_iguales"] and d["filas_de_la_pestana_2_iguales"]
    assert d["toplevels_abiertos"] == 0

    # 6. Cerrar la ventana principal con un barrido en marcha (H3).
    assert r["cerrar_la_principal"] == {"en_marcha_al_cerrar": True, "hijo_terminado": True,
                                        "carpeta_retirada": True}
