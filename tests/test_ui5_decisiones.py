"""
tests/test_ui5_decisiones.py
============================
La aceptacion de UI-5 (cadena de interfaz): CUATRO DECISIONES DEL DUEÑO
(2026-11-15) sobre lo que la cadena UI dejo abierto, cada una en su apartado.

(1) Cambiar el CSV de puntos invalida el informe vigente (ficha UI1-01, su
    «Abierto»): un solo gesto en la pestaña 1 con la hidrologia. Que cuenta
    como «cambiar»: TODA escritura en el campo, tambien la misma ruta
    tecleada o elegida otra vez con «Examinar…» (el archivo pudo cambiar en
    disco, y volver a correr cuesta milisegundos); abrir una sesion o un
    proyecto nuevo retira el informe con SU motivo, que el gesto del campo no
    pisa. Doble de tkinter y ventana real.
(2) La remision de la memoria resumida a su completa dice la verdad en los
    tres contextos en que se escribe (ficha UI2-01 b): la CLI con las dos
    vistas en una invocacion, la resumida HTML de la ventana y la resumida PDF
    del proceso hijo, que vuelve a correr la obra (EXT-8-02). El texto se lee
    de M11, no se transcribe aqui.
(3) El PDF se escribe de forma atomica (ficha UI2-03): un fallo a mitad de la
    escritura no destruye el PDF que el usuario tuviera en el destino, en la
    completa y en la resumida, y en la CLI directa.
(4) La guardia del archivo de criterios exige la forma de las CLAVES (ficha
    UI3-03): la regla vive en `criterios_adoptados._verificar_criterio`, el
    cuello de los tres caminos, y las capas de arriba no la repiten. El valor
    de archivo de los 141 criterios, sus filas de tabla y los extremos de su
    ventana siguen pasando por todos los caminos.

Escrita PRIMERO, en rojo, como manda el §1 de la cadena: 26 tests con
`xfail(strict=True)` en lo que todavia no existia o estaba mal, medidos antes
de tocar codigo con `--runxfail` (cada uno fallando por su motivo), y
liberados al implementar; los otros siete son GUARDIAS que valen antes y
despues y lo dicen en su docstring. Cada decision se comprobo ademas por
mutacion: deshecha cualquiera de las cuatro, caen sus tests. Lo que la
revision independiente de UI-5 encontro (ficha UI5-02: H1, la remision daba
por suficiente que el encabezado coincidiera; H2, la pestaña 2 no se repintaba
al retirar el informe; H3, el temporal de nombre fijo) se escribio igual: 14
tests en rojo, liberados al corregir, y tres guardias; y lo que encontro la
verificacion de esa revision (ficha UI5-03: N1, la huella de la hoja de ruta
contada como de la corrida; N2, el borrador de la pestaña 2 perdido al
repintar; N3, «todavia no se ejecuto» tras un informe retirado; N4, los
permisos y los mensajes de la escritura atomica), otros 14 en rojo y una
guardia; y la de esas correcciones (N5, el borrador de una obra heredado por
otra al abrirla), cuatro mas en rojo. Los datos son DATOS DE PRUEBA:
el CSV de ejemplo, el JSON de datos externos de la linea base y las corridas
de referencia.
"""

from __future__ import annotations

import ast
import errno
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import editores as sed
from src import indice_formulas as ind
from src import sesion as ses
from src.modelos import Derivada
from src.modulos import M11_reporte as M11
from tests.apoyo import doble_tkinter
from tests.apoyo.doble_tkinter import VariableDeTexto


RAIZ = Path(__file__).resolve().parents[1]
GUI = RAIZ / "gui" / "app.py"
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
LINEA_BASE = RAIZ / "tests" / "linea_base_familia_c"
ARBOL_GUI = ast.parse(GUI.read_text(encoding="utf-8-sig"), filename="app.py")
ESPESOR = "espesor_pared_conducto"   # dict por material con el diametro (mm, ENTERO) de clave
PDF_ANTERIOR = b"%PDF-VIEJO, de otra exportacion\n%%EOF\n"
PDF_NUEVO = b"%PDF-1.7 el nuevo, entero\n%%EOF\n"
TOPE_S = 900


def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no se encontro la funcion {nombre}")


def _referencia(nombre):
    return next(c for c in ind.CORRIDAS_DE_REFERENCIA if c.nombre == nombre)


@pytest.fixture(scope="module")
def app():
    return doble_tkinter.gui_app()


@pytest.fixture(scope="module")
def informe_perfil():
    return ind.correr_referencia(_referencia("perfil_guia"))


# ===========================================================================
# (1) Cambiar el CSV de puntos invalida el informe
# ===========================================================================

class _VariableConTraza(VariableDeTexto):
    """
    El doble de un `StringVar` con su `trace_add("write")`: como el de Tk,
    avisa en CADA escritura, tambien la del mismo texto.
    """

    def __init__(self, texto="", al_escribir=None):
        super().__init__(texto)
        self.al_escribir = al_escribir

    def set(self, texto):
        super().set(texto)
        if self.al_escribir is not None:
            self.al_escribir()


def _ventana(app, **kw):
    from tests.test_ui1_hidrologia_ventana import _ventana as ventana_de_ui1
    v = ventana_de_ui1(app, **kw)
    v.llamadas = []
    v._releer_familias = lambda: v.llamadas.append("releer_familias")
    v._pintar_anticipo = lambda: v.llamadas.append("pintar_anticipo")
    return v


def _con_trazas(v):
    """Las tres trazas de la pestaña 1 que invalidan, como las pone `__init__`."""
    v.csv_var = _VariableConTraza(v.csv_var.get(), lambda: v._al_cambiar_el_csv())
    v.cuencas_var = _VariableConTraza(v.cuencas_var.get(),
                                      lambda: v._al_cambiar_la_hidrologia())
    v.estacion_var = _VariableConTraza(v.estacion_var.get(),
                                       lambda: v._al_cambiar_la_hidrologia())
    return v


def _sin_dialogos(app, monkeypatch):
    monkeypatch.setattr(app.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(app.messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(app.messagebox, "showerror", lambda *a, **k: None)


def test_1_el_motivo_del_csv_nombra_el_csv_de_puntos_y_pide_volver_a_ejecutar(app):
    motivo = app.MOTIVO_CSV_CAMBIADO
    assert "csv de puntos" in motivo.lower()
    assert "vuelva a ejecutar" in motivo.lower()
    # Es el motivo de UN gesto, distinto de los demas: el usuario lee por que.
    otros = {app.MOTIVO_HIDROLOGIA_CAMBIADA, app.MOTIVO_INFORME_DESACTUALIZADO,
             app.MOTIVO_CORRIDA_FALLIDA, app.MOTIVO_SIN_CORRIDA}
    assert motivo not in otros


def test_1_cambiar_el_csv_invalida_el_informe_y_apaga_los_siete(app):
    v = _ventana(app, csv_=CSV_EJEMPLO)
    v.informe = object()
    v._al_cambiar_el_csv()
    assert v.informe is None
    assert len(app.BOTONES_DE_EXPORTACION) == 7
    for nombre in app.BOTONES_DE_EXPORTACION:
        boton = getattr(v, nombre)
        assert not boton.encendido, nombre
        assert boton.motivo == app.MOTIVO_CSV_CAMBIADO, nombre
    # Y la anotacion de la pestaña 1 se rehace, como hasta ahora.
    assert v.llamadas == ["releer_familias"]


def test_1_sin_informe_el_gesto_no_toca_los_exportadores(app):
    """Sin informe no hay nada que invalidar: el motivo sin corrida se queda."""
    v = _ventana(app, csv_=CSV_EJEMPLO)
    for nombre in app.BOTONES_DE_EXPORTACION:
        getattr(v, nombre).deshabilitar(app.MOTIVO_SIN_CORRIDA)
    v._al_cambiar_el_csv()
    assert all(getattr(v, n).motivo == app.MOTIVO_SIN_CORRIDA
               for n in app.BOTONES_DE_EXPORTACION)
    assert v.llamadas == ["releer_familias"]


def test_1_la_traza_del_csv_es_el_gesto_y_el_csv_y_la_hidrologia_son_uno():
    init = ast.unparse(_funcion(ARBOL_GUI, "__init__"))
    tramo = init[init.index("self.csv_var.trace_add"):][:160]
    assert "_al_cambiar_el_csv" in tramo
    # UN gesto: los dos metodos retiran el informe por la misma puerta.
    for nombre in ("_al_cambiar_el_csv", "_al_cambiar_la_hidrologia"):
        cuerpo = ast.unparse(_funcion(ARBOL_GUI, nombre))
        assert "self._invalidar_informe(" in cuerpo, nombre


def test_1_teclear_la_misma_ruta_tambien_invalida(app):
    """
    La decision de que cuenta como «cambiar»: TODA escritura en el campo. La
    misma ruta otra vez es el gesto de volver a dar la entrada, y el archivo
    pudo cambiar en disco despues de correr.
    """
    v = _con_trazas(_ventana(app, csv_=CSV_EJEMPLO))
    v.informe = object()
    v.csv_var.set(str(CSV_EJEMPLO))
    assert v.informe is None
    assert v.btn_json.motivo == app.MOTIVO_CSV_CAMBIADO


def test_1_cargar_una_sesion_deja_el_motivo_de_la_sesion(app, tmp_path, monkeypatch):
    """
    Abrir una sesion SUSTITUYE todo y retira el informe con su motivo
    (`MOTIVO_INFORME_DESACTUALIZADO`); el CSV que la sesion trae no lo pisa
    con el suyo, como no lo pisan las dos rutas de la hidrologia (UI-1).
    """
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"csv": str(tmp_path / "otro.csv"),
                   "cuencas": "c.csv", "estacion": "e.csv"})
    ruta = tmp_path / "s.json"
    ruta.write_text(json.dumps(sesion), encoding="utf-8")
    _sin_dialogos(app, monkeypatch)
    monkeypatch.setattr(app.filedialog, "askopenfilename", lambda **kw: str(ruta))
    v = _con_trazas(_ventana(app, csv_=CSV_EJEMPLO))
    v.informe = object()
    v.cargar_sesion()
    assert v.csv_var.get() == sesion["csv"]
    assert v.informe is None
    for nombre in app.BOTONES_DE_EXPORTACION:
        assert getattr(v, nombre).motivo == app.MOTIVO_INFORME_DESACTUALIZADO, nombre


def test_1_un_proyecto_nuevo_deja_el_motivo_de_la_sesion(app, monkeypatch):
    _sin_dialogos(app, monkeypatch)
    v = _con_trazas(_ventana(app, csv_=CSV_EJEMPLO))
    v.informe = object()
    v.nuevo_proyecto()
    assert v.csv_var.get() == "" and v.informe is None
    for nombre in app.BOTONES_DE_EXPORTACION:
        assert getattr(v, nombre).motivo == app.MOTIVO_INFORME_DESACTUALIZADO, nombre


@pytest.mark.parametrize("gesto", ["csv", "hidrologia", "corrida fallida"])
def test_1_retirar_el_informe_repinta_la_pestana_2(app, gesto):
    """
    Revision independiente de UI-5 (H2, anterior a UI-5 y alcanzable con el
    gesto nuevo): la pestaña 2 con «Solo los que bloquearon esta corrida»
    seguia pintando las filas y el «medido sobre la corrida de …» de un
    informe ya retirado. Toda retirada pasa por `_vaciar_tablas_del_informe`,
    y desde aqui repinta la pestaña 2 sin corrida.
    """
    from tests.test_ui1_hidrologia_ventana import _Arbol
    v = _ventana(app, csv_=CSV_EJEMPLO)
    del v._vaciar_tablas_del_informe            # la de verdad, no el doble de UI-1
    v.tree_puntos, v.tree_criterios, v.lbl_resumen = _Arbol(), _Arbol(), {}
    v._al_seleccionar_punto = lambda *_a: None
    v._pintar_recuentos_de_puntos = lambda: None
    v._pintar_cabezal_del_proyecto = lambda motivo=None: None
    repintados = []
    v._refiltrar = lambda: repintados.append(v.informe)
    v.informe = object()
    if gesto == "csv":
        v._al_cambiar_el_csv()
    elif gesto == "hidrologia":
        v._al_cambiar_la_hidrologia()
    else:
        # EJECUTAR ya retiro el informe al empezar; la corrida fallo al cargar.
        v.informe = None
        v._mostrar_error_entrada("No se pudo leer la entrada")
    assert repintados == [None]


class _Todo:
    """Un widget que acepta cualquier llamada y la olvida."""

    def __getattr__(self, _nombre):
        return lambda *a, **k: None


class _ArbolConSeleccion:
    def __init__(self, clave):
        self.clave = clave

    def selection(self):
        return (self.clave,)


def test_1_la_reseleccion_de_un_repintado_conserva_el_borrador(app, monkeypatch):
    """
    Verificacion de UI-5 (N2): un repintado de la tabla vuelve a seleccionar
    la misma fila (`_reponer_seleccion`) y Tk encola `<<TreeviewSelect>>`;
    `_al_seleccionar_criterio` reescribia el campo y el editor, y el valor
    tecleado y sin aplicar se perdia. Con la misma fila y el mismo valor
    efectivo, el borrador se queda; si el valor efectivo cambia (declarar,
    quitar, cargar una sesion), se reescribe como siempre.
    """
    clave = "HW_D_max"
    v = _ventana(app)
    v.tree_criterios_todos = _ArbolConSeleccion(clave)
    for nombre in ("lbl_estado_criterio", "lbl_criterio_seleccionado", "txt_detalle_criterio",
                   "ent_valor_declarado", "btn_aplicar_corrida", "btn_quitar_declarado",
                   "btn_guardar_archivo", "btn_ventana_norma"):
        setattr(v, nombre, _Todo())
    montados = []
    v._montar_editor = lambda c, valor: montados.append((c, valor))
    v._pintar_boton_barrido = lambda: None
    v.valor_declarado_var = VariableDeTexto("")
    v._clave_criterio_seleccionado = None
    monkeypatch.setattr(app.comp, "escribir_campos", lambda *a, **k: None)
    archivo = ca.criterio(clave).valor
    v._al_seleccionar_criterio()
    assert v.valor_declarado_var.get() == v._literal_de(archivo)
    v.valor_declarado_var.set("1.3")                 # el borrador, sin aplicar
    v._al_seleccionar_criterio()                     # la reseleccion de un repintado
    assert v.valor_declarado_var.get() == "1.3"
    assert montados == [(clave, archivo)]
    ca.establecer_valor_dinamico(clave, 1.2)         # el valor efectivo cambia
    v._al_seleccionar_criterio()
    assert v.valor_declarado_var.get() == v._literal_de(1.2)


@pytest.mark.parametrize("motivo", ["MOTIVO_CSV_CAMBIADO", "MOTIVO_HIDROLOGIA_CAMBIADA",
                                    "MOTIVO_CORRIDA_FALLIDA"])
def test_1_la_pestana_2_dice_por_que_no_hay_corrida(app, motivo):
    """
    Verificacion de UI-5 (N3): sin corrida todavia, la linea del ambito dice
    `MOTIVO_SIN_CORRIDA_FILTRO`; con un informe retirado, el mismo texto que
    la barra («Sin informe vigente: <motivo>.»), sin un texto nuevo.
    """
    from tests.test_ui1_hidrologia_ventana import _Arbol
    bloqueantes = next(r for r, tag in app.FILTROS_DE_AMBITO if tag == app.AMBITO_BLOQUEANTES)
    v = _ventana(app, csv_=CSV_EJEMPLO)
    v.filtro_ambito_var = VariableDeTexto(bloqueantes)
    v.lbl_ambito = _Widget_de_ui1()
    v._pintar_aviso_de_ambito(0)
    assert v.lbl_ambito.texto == app.MOTIVO_SIN_CORRIDA_FILTRO
    del v._vaciar_tablas_del_informe
    v.tree_puntos, v.tree_criterios, v.lbl_resumen = _Arbol(), _Arbol(), {}
    v._al_seleccionar_punto = lambda *_a: None
    v._pintar_recuentos_de_puntos = lambda: None
    v._pintar_cabezal_del_proyecto = lambda motivo=None: None
    v._refiltrar = lambda: v._pintar_aviso_de_ambito(0)
    v._vaciar_tablas_del_informe(getattr(app, motivo))
    assert v.lbl_ambito.texto == f"Sin informe vigente: {getattr(app, motivo)}."
    assert v.lbl_ambito.texto == v.lbl_estado.texto


def _Widget_de_ui1():
    from tests.test_ui1_hidrologia_ventana import _Widget
    return _Widget()


def test_1_los_campos_de_la_sesion_se_escriben_despues_de_retirar_el_informe():
    """
    En «Cargar sesion» y «Nuevo proyecto» el CSV y las dos rutas de la
    hidrologia se escriben DESPUES de los bloques que retiran el informe con
    el motivo de la sesion: es lo que hace que el gesto de los campos no pise
    ese motivo. Las dos rutas ya iban detras (UI-1); el CSV, no.
    """
    for nombre in ("cargar_sesion", "nuevo_proyecto"):
        cuerpo = ast.unparse(_funcion(ARBOL_GUI, nombre))
        bloques = cuerpo.index("self._aplicar_bloques_de_sesion(")
        for var in ("self.csv_var.set(", "self.cuencas_var.set(", "self.estacion_var.set("):
            assert cuerpo.index(var) > bloques, (nombre, var)


# --- La ventana de verdad -------------------------------------------------

def _interprete_con_ventana():
    from tests.test_gui_contrato import _ENVOLTORIO, _INTERPRETE
    return _INTERPRETE, _ENVOLTORIO


@pytest.fixture(scope="module")
def ventana_real(tmp_path_factory):
    interprete, envoltorio = _interprete_con_ventana()
    if interprete is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    salida = tmp_path_factory.mktemp("ui5_ventana")
    hecho = subprocess.run(
        envoltorio + [interprete, "-m", "tests.apoyo.gui_ui5_real", str(salida)],
        cwd=RAIZ, capture_output=True, text=True, timeout=TOPE_S)
    assert hecho.returncode == 0, (
        f"la corrida de la GUI fallo:\n{hecho.stdout[-4000:]}\n{hecho.stderr[-4000:]}")
    return salida, json.loads((salida / "resumen_ui5.json").read_text(encoding="utf-8"))


def _apagados_con(exportadores, motivo):
    return (len(exportadores) == 7
            and all(not e["encendido"] and e["motivo"] == motivo
                    for e in exportadores.values()))


def test_1_la_ventana_real_invalida_al_cambiar_el_csv(app, ventana_real):
    _salida, r = ventana_real
    motivo = app.MOTIVO_CSV_CAMBIADO
    # Sin informe, el gesto no pinta otro motivo que el de no haber corrido.
    assert _apagados_con(r["sin_informe"], app.MOTIVO_SIN_CORRIDA)
    assert all(e["encendido"] for e in r["tras_correr"].values())
    # Teclear otra ruta en el campo, letra a letra.
    t = r["tras_teclear"]
    assert t["informe_es_None"] and _apagados_con(t["exportadores"], motivo)
    assert t["barra"] == f"Sin informe vigente: {motivo}."
    assert t["cabezal"] == f"Sin informe vigente: {motivo}."
    assert t["filas_puntos"] == 0
    # «Examinar…» con la MISMA ruta, y la misma ruta tecleada otra vez.
    for gesto in ("tras_examinar_la_misma", "tras_teclear_la_misma"):
        assert r[gesto]["informe_es_None"], gesto
        assert _apagados_con(r[gesto]["exportadores"], motivo), gesto
    # Volver a correr los enciende: el gesto no deja nada atascado.
    assert all(e["encendido"] for e in r["tras_volver_a_correr"].values())


def test_1_la_ventana_real_repinta_la_pestana_2_al_retirar_el_informe(app, ventana_real):
    """
    H2 en la ventana de verdad: con «Solo los que bloquearon esta corrida»
    puesto, cambiar el CSV, cambiar el CSV de cuencas o una corrida que falla
    dejan la tabla sin el filtro de una corrida que ya no existe (todas las
    filas, como sin corrida) y la linea de al lado dice por que.
    """
    _salida, r = ventana_real
    f = r["filtro_bloqueantes"]
    assert f["con_corrida"]["ambito"].startswith("medido sobre la corrida de")
    assert f["con_corrida"]["filas"] != f["total_criterios"]
    for gesto in ("tras_csv", "tras_cuencas", "tras_corrida_fallida"):
        assert f[gesto]["informe_es_None"], gesto
        assert not f[gesto]["ambito"].startswith("medido sobre"), gesto
        assert f[gesto]["filas"] == f["total_criterios"], gesto


MOTIVO_DE_CADA_GESTO = {"tras_csv": "MOTIVO_CSV_CAMBIADO",
                        "tras_cuencas": "MOTIVO_HIDROLOGIA_CAMBIADA",
                        "tras_corrida_fallida": "MOTIVO_CORRIDA_FALLIDA"}


def test_1_la_ventana_real_dice_en_la_pestana_2_por_que_no_hay_corrida(app, ventana_real):
    """
    Verificacion de UI-5 (N3): tras retirar el informe la linea del ambito
    decia MOTIVO_SIN_CORRIDA_FILTRO («todavia no se ejecuto el pipeline»),
    falso tras un cambio de CSV o una corrida que fallo. Dice lo que la barra:
    el informe se retiro, y por que.
    """
    _salida, r = ventana_real
    f = r["filtro_bloqueantes"]
    for gesto, motivo in MOTIVO_DE_CADA_GESTO.items():
        assert f[gesto]["ambito"] == f"Sin informe vigente: {getattr(app, motivo)}.", gesto
        assert f[gesto]["ambito"] == f[gesto]["barra"], gesto


def test_1_la_ventana_real_conserva_el_borrador_de_la_pestana_2(ventana_real):
    """
    Verificacion de UI-5 (N2): repintar la pestaña 2 al retirar el informe
    volvia a seleccionar la fila, y la seleccion reescribia el campo: un
    valor tecleado y sin aplicar («1.3» para `HW_D_max`) volvia a «1.5».
    """
    _salida, r = ventana_real
    b = r["borrador"]
    assert b["archivo"] == "1.5"
    for gesto in ("tras_csv", "tras_cuencas", "tras_corrida_fallida"):
        assert b[gesto]["informe_es_None"], gesto
        assert b[gesto]["borrador"] == "1.3", gesto


def test_1_la_ventana_real_no_lleva_el_borrador_a_otra_obra(ventana_real):
    """
    Verificacion de UI-5 (N5): con la firma de N2, abrir OTRA obra («Cargar
    sesion», «Nuevo proyecto») con el mismo valor efectivo del criterio
    seleccionado dejaba en el editor lo tecleado para la anterior, y un
    «Aplicar» lo habria declarado en la nueva. Hoy el editor repone el valor
    efectivo de la obra abierta.
    """
    _salida, r = ventana_real
    b = r["borrador"]
    for gesto in ("tras_cargar_otra_obra", "tras_nuevo_proyecto"):
        assert b[gesto]["borrador"] == b["archivo"], gesto


@pytest.mark.parametrize("gesto", ["cargar sesion", "nuevo proyecto", "importar decisiones"])
def test_1_abrir_otra_obra_no_hereda_el_borrador(app, monkeypatch, tmp_path, gesto):
    """
    N5 con el doble: los tres gestos que reponen los criterios de otra sesion
    pasan por `_restaurar_criterios`, que olvida que mostraba el editor; la
    reseleccion que sigue repone el valor efectivo aunque sea el mismo.
    """
    clave = "HW_D_max"
    v = _ventana(app)
    v.tree_criterios_todos = _ArbolConSeleccion(clave)
    for nombre in ("lbl_estado_criterio", "lbl_criterio_seleccionado", "txt_detalle_criterio",
                   "ent_valor_declarado", "btn_aplicar_corrida", "btn_quitar_declarado",
                   "btn_guardar_archivo", "btn_ventana_norma"):
        setattr(v, nombre, _Todo())
    v._montar_editor = lambda c, valor: None
    v._pintar_boton_barrido = lambda: None
    v.valor_declarado_var = VariableDeTexto("")
    v._clave_criterio_seleccionado = None
    monkeypatch.setattr(app.comp, "escribir_campos", lambda *a, **k: None)
    _sin_dialogos(app, monkeypatch)
    sesion = ses.sesion_vacia("1.0")
    ruta = tmp_path / "otra_obra.json"
    ruta.write_text(json.dumps(sesion), encoding="utf-8")
    monkeypatch.setattr(app.filedialog, "askopenfilename", lambda **kw: str(ruta))
    archivo = v._literal_de(ca.criterio(clave).valor)
    v._al_seleccionar_criterio()
    v.valor_declarado_var.set("1.3")                 # el borrador de la obra A
    {"cargar sesion": v.cargar_sesion, "nuevo proyecto": v.nuevo_proyecto,
     "importar decisiones": v.importar_decisiones}[gesto]()
    v._al_seleccionar_criterio()                     # la reseleccion que sigue
    assert v.valor_declarado_var.get() == archivo


def test_1_la_ventana_real_conserva_la_frontera_de_la_decision(app, ventana_real):
    """
    La decision de UI-5 era sobre el CSV, y el JSON de datos externos seguia
    sin invalidar (EXT-8). Desde VE-5 (decision del dueño, ficha UI5-01 a)
    tambien invalida, con su motivo (`MOTIVO_ENTRADA_CAMBIADA`); abrir una
    sesion y un proyecto nuevo siguen retirando el informe con el motivo de
    la sesion, no con el de un campo.
    """
    _salida, r = ventana_real
    assert r["tras_cambiar_externos"]["informe_es_None"]
    assert _apagados_con(r["tras_cambiar_externos"]["exportadores"],
                         app.MOTIVO_ENTRADA_CAMBIADA)
    for gesto in ("tras_cargar_sesion", "tras_nuevo_proyecto"):
        assert r[gesto]["informe_es_None"], gesto
        assert _apagados_con(r[gesto]["exportadores"],
                             app.MOTIVO_INFORME_DESACTUALIZADO), gesto
    assert r["tras_cargar_sesion"]["csv"] == r["csv_de_la_sesion"]
    assert r["dialogos_de_error"] == []


# ===========================================================================
# (2) La remision de la resumida a su completa dice la verdad
# ===========================================================================

_ENCABEZADO = ("SHA-1 del CSV de entrada", "SHA-1 de criterios_adoptados.py")


def _encabezado(html):
    """La hora de la corrida y las huellas del encabezado de trazabilidad."""
    utc = re.search(r"corrida UTC: ([^)]+)\)", html).group(1).strip()
    huellas = tuple(re.search(re.escape(e) + r'</th>\s*<td class="mono">([0-9a-f]{40})',
                              html).group(1) for e in _ENCABEZADO)
    return utc, huellas


def test_2_sin_completa_la_remision_no_nombra_la_puerta_ni_la_invocacion():
    remision = M11._remision_a_la_completa(None)
    for promesa in ("--html", "--pdf", "invocacion"):
        assert promesa not in remision, promesa


@pytest.mark.parametrize("nombre_completa", [None, "completa.html"])
def test_2_la_remision_no_promete_el_encabezado_entre_dos_corridas(nombre_completa):
    remision = M11._remision_a_la_completa(nombre_completa)
    assert "es el mismo en las dos" not in remision
    # Dice COMO se comprueba: con la hora y las huellas del encabezado.
    assert M11.REMISION_COMO_COMPROBARLO in remision
    for palabra in ("hora UTC de la corrida", "huellas", "dos corridas"):
        assert palabra in M11.REMISION_COMO_COMPROBARLO, palabra


def test_2_la_remision_solo_afirma_lo_que_el_encabezado_prueba():
    """
    Revision independiente de UI-5 (H1): «las dos vistas describen la MISMA
    corrida CUANDO su encabezado coincide» es una condicion suficiente que el
    encabezado no da (el test de abajo lo mide). Lo cierto es la implicacion
    inversa: de la misma corrida, el encabezado coincide; uno distinto prueba
    que son dos corridas; uno igual no prueba que sean la misma.
    """
    texto = M11.REMISION_COMO_COMPROBARLO
    assert "describen la MISMA corrida cuando" not in texto
    assert "Si las dos vistas salen de la MISMA corrida" in texto
    assert "son dos corridas" in texto
    assert "no prueba que sean la misma" in texto


def test_2_la_huella_de_la_hoja_de_ruta_no_decide_si_es_la_misma_corrida():
    """
    Verificacion de UI-5 (N1): la remision contaba la huella de la hoja de
    ruta entre lo que coincide si las vistas son de la misma corrida, y esa
    huella no es de la corrida: se lee del disco al exportar cada vista (el
    test de abajo lo mide). Lo mismo el parrafo del encabezado de la
    plantilla de la resumida, que lo prometia desde T-12.
    """
    texto = M11.REMISION_COMO_COMPROBARLO
    lo_que_coincide = texto[:texto.index("son dos corridas")]
    assert "hoja de ruta" not in lo_que_coincide
    assert "hoja de ruta" in texto and "al exportar" in texto
    plantilla = (RAIZ / "src" / "plantillas" / "memoria_resumida.html").read_text(
        encoding="utf-8")
    parrafo = plantilla[plantilla.index('<h2 id="trazabilidad">'):
                        plantilla.index('<div class="trazabilidad">')]
    assert "si las huellas o la hora de la corrida no coinciden" not in parrafo
    assert "hoja de ruta" in parrafo and "al exportar" in parrafo


def test_2_la_huella_de_la_hoja_de_ruta_se_lee_al_exportar(informe_perfil, tmp_path):
    """
    GUARDIA (vale antes y despues), el hecho detras de N1: con el MISMO
    informe, cambiar la hoja de ruta entre dos exportaciones cambia su
    huella en el encabezado, y no la hora de la corrida ni las huellas que
    vienen del `ContextoCorrida`.
    """
    hoja = M11.ruta_hoja_de_ruta()
    docs = tmp_path / "docs"
    docs.mkdir()
    copia = docs / hoja.name
    shutil.copyfile(hoja, copia)

    def encabezado():
        t = M11.trazabilidad(Path(informe_perfil.csv), informe_perfil.contexto,
                             dir_docs=docs, generado_utc=informe_perfil.generado)
        return t.hoja_ruta_sha1, (t.generado_utc, t.csv_sha1, t.criterios_sha1)

    antes = encabezado()
    copia.write_text(copia.read_text(encoding="utf-8") + "\nuna linea mas\n",
                     encoding="utf-8")
    despues = encabezado()
    assert antes[0] != despues[0]
    assert antes[1] == despues[1]


def test_2_un_encabezado_igual_no_prueba_que_sea_la_misma_corrida():
    """
    GUARDIA (vale antes y despues), el hecho que obliga a la redaccion de
    arriba: dos corridas con un valor declarado en caliente distinto
    (`HW_D_max` 1.5 y 1.2, los dos de su ventana) llevan las MISMAS huellas
    del CSV y de los criterios y dimensionan distinto. Las huellas no cubren
    lo que se declara para una corrida, y la hora va al segundo.
    """
    externos = cli.cargar_datos_externos(EXTERNOS, {"luz_m": "2.75", "TW_m": None,
                                                    "longitud_m": None,
                                                    "L_hidraulico_m": None,
                                                    "categoria_tr": None})
    corridas = []
    for valor in (1.5, 1.2):
        ca.establecer_valor_dinamico("HW_D_max", valor)
        informe = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
        corridas.append((informe.contexto.csv_sha1, informe.contexto.criterios_sha1,
                         cli.informe_json(informe)["puntos"]))
    (csv_a, criterios_a, puntos_a), (csv_b, criterios_b, puntos_b) = corridas
    assert (csv_a, criterios_a) == (csv_b, criterios_b)
    assert puntos_a != puntos_b


def test_2_con_la_completa_de_la_misma_invocacion_la_nombra():
    """
    GUARDIA (vale antes y despues): en la CLI con las dos vistas en UNA
    invocacion la resumida nombra el archivo de la completa y dice que salen
    del MISMO informe, que ahi es cierto.
    """
    remision = M11._remision_a_la_completa("completa.html")
    assert "<code>completa.html</code>" in remision
    assert "MISMA invocacion" in remision and "MISMO informe" in remision


def test_2_cli_las_dos_vistas_de_una_invocacion(tmp_path, capsys):
    """Contexto (a): la CLI escribe las dos; mismo encabezado, la resumida nombra la completa."""
    completa, resumida = tmp_path / "completa.html", tmp_path / "resumida.html"
    codigo = cli.main([str(CSV_EJEMPLO), "--luz", "2.75", "--alcance", "perfil",
                       "--datos-externos", str(EXTERNOS), "--json", str(tmp_path / "i.json"),
                       "--html", str(completa), "--html-resumida", str(resumida)])
    assert codigo in (0, 1)
    texto_c = completa.read_text(encoding="utf-8")
    texto_r = resumida.read_text(encoding="utf-8")
    assert M11._remision_a_la_completa("completa.html") in texto_r
    assert M11.REMISION_COMO_COMPROBARLO in texto_r
    assert _encabezado(texto_c) == _encabezado(texto_r)


def test_2_ventana_la_resumida_html_y_la_completa_del_mismo_informe(informe_perfil, tmp_path):
    """
    Contexto (b): la ventana escribe las dos memorias HTML del MISMO informe
    (`exportar_html` y `exportar_html_resumida`, sin `nombre_completa`): el
    encabezado coincide, y la resumida no habla de una invocacion.
    """
    completa = M11.exportar_html(informe_perfil, tmp_path / "c.html", proyecto="UI-5",
                                 ruta_plantilla=cli.plantilla_por_alcance(
                                     informe_perfil.alcance))
    resumida = M11.exportar_html_resumida(informe_perfil, tmp_path / "r.html",
                                          proyecto="UI-5")
    texto_c = completa.read_text(encoding="utf-8")
    texto_r = resumida.read_text(encoding="utf-8")
    assert M11._remision_a_la_completa(None) in texto_r
    assert "invocacion" not in M11._remision_a_la_completa(None)
    assert _encabezado(texto_c) == _encabezado(texto_r)


def test_2_ventana_real_las_dos_memorias_html_de_sus_botones(ventana_real):
    """El contexto (b) por los botones de la pestaña 4 de la ventana de verdad."""
    salida, r = ventana_real
    assert r["memorias_html"] == {"completa.html": True, "resumida.html": True}
    texto_c = (salida / "completa.html").read_text(encoding="utf-8")
    texto_r = (salida / "resumida.html").read_text(encoding="utf-8")
    assert M11._remision_a_la_completa(None) in texto_r
    assert M11.REMISION_COMO_COMPROBARLO in texto_r
    assert "invocacion" not in M11._remision_a_la_completa(None)
    assert _encabezado(texto_c) == _encabezado(texto_r)


class _WeasyQueGuarda:
    """El doble de `WeasyHTML` que guarda la memoria y escribe un PDF entero."""

    vistas = []

    def __init__(self, *, string, base_url):
        self.string = string

    def write_pdf(self, ruta):
        _WeasyQueGuarda.vistas.append(self.string)
        Path(ruta).write_bytes(PDF_NUEVO)


def test_2_hijo_la_resumida_pdf_no_promete_lo_que_la_ventana_no_cumple(tmp_path, monkeypatch,
                                                                      capsys):
    """
    Contexto (c): el hijo del PDF es `cli.py --sesion ... --pdf-resumida`, con
    la linea que arma `gui/exportacion_pdf.comando_exportar_pdf`. VUELVE A
    CORRER la obra (EXT-8-02): su encabezado no es el de la completa de la
    ventana, y la resumida no puede decir que lo es.
    """
    from gui import exportacion_pdf as expdf
    from tests.test_ext8_rendimiento_gui import _sesion_de_prueba
    ruta_sesion = tmp_path / "sesion.json"
    ses.escribir_json_atomico(ruta_sesion, _sesion_de_prueba(CSV_EJEMPLO, cli.ALCANCE_PERFIL))
    comando = expdf.comando_exportar_pdf(
        interprete=sys.executable, cli=RAIZ / "cli.py", sesion=ruta_sesion,
        destino=tmp_path / "r.pdf", json_aparte=tmp_path / "i.json",
        vista=expdf.VISTA_RESUMIDA)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", _WeasyQueGuarda)
    _WeasyQueGuarda.vistas = []
    assert cli.main(comando[2:]) in (0, 1)
    assert (tmp_path / "r.pdf").read_bytes() == PDF_NUEVO
    (memoria,) = _WeasyQueGuarda.vistas
    assert M11._remision_a_la_completa(None) in memoria
    assert "MISMA invocacion" not in memoria
    assert "es el mismo en las dos" not in memoria


def test_2_la_linea_base_lleva_la_remision_de_m11():
    """
    La corrida 4 de la linea base escribe las dos vistas en una invocacion
    (`regenerar.sh`): su resumida lleva la remision que M11 escribe hoy,
    nombrando la completa de esa invocacion.
    """
    resumida = (LINEA_BASE / "memoria_resumida_expediente.html").read_text(encoding="utf-8")
    assert M11._remision_a_la_completa("memoria_exp.html") in resumida
    assert M11.REMISION_COMO_COMPROBARLO in resumida


# ===========================================================================
# (3) El PDF se escribe de forma atomica
# ===========================================================================

class _WeasyQueFallaAMitad:
    """
    El doble de `WeasyHTML` que escribe la cabecera del PDF y falla como un
    disco lleno: lo que weasyprint hace cuando la E/S falla a mitad.
    """

    rutas = []

    def __init__(self, *, string, base_url):
        self.string = string

    def write_pdf(self, ruta):
        _WeasyQueFallaAMitad.rutas.append(str(ruta))
        with open(ruta, "wb") as f:
            f.write(b"%PDF-1.7 escrito a medias")
        raise OSError(errno.ENOSPC, "No space left on device", str(ruta))


class _WeasyQueEscribe:
    rutas = []

    def __init__(self, *, string, base_url):
        self.string = string

    def write_pdf(self, ruta):
        _WeasyQueEscribe.rutas.append(Path(ruta))
        Path(ruta).write_bytes(PDF_NUEVO)


def _exportar(vista, informe, destino, **kw):
    if vista == "completa":
        return M11.exportar_pdf(informe, destino, proyecto="UI-5",
                                ruta_plantilla=cli.plantilla_por_alcance(informe.alcance),
                                **kw)
    return M11.exportar_pdf_resumida(informe, destino, proyecto="UI-5", **kw)


@pytest.mark.parametrize("vista", ["completa", "resumida"])
def test_3_un_fallo_a_mitad_deja_intacto_el_pdf_anterior(vista, informe_perfil, tmp_path,
                                                         monkeypatch):
    destino = tmp_path / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", _WeasyQueFallaAMitad)
    _WeasyQueFallaAMitad.rutas = []
    with pytest.raises(OSError) as fallo:
        _exportar(vista, informe_perfil, destino)
    assert fallo.value.errno == errno.ENOSPC
    assert destino.read_bytes() == PDF_ANTERIOR
    # El temporal se retiro: en el directorio solo queda el PDF del usuario.
    assert sorted(p.name for p in tmp_path.iterdir()) == ["memoria.pdf"]
    # Y weasyprint escribio en el MISMO directorio, no en el destino.
    (ruta,) = _WeasyQueFallaAMitad.rutas
    assert Path(ruta).parent == destino.parent and Path(ruta) != destino


@pytest.mark.parametrize("vista", ["completa", "resumida"])
def test_3_terminada_la_escritura_el_temporal_reemplaza_al_destino(vista, informe_perfil,
                                                                   tmp_path, monkeypatch):
    destino = tmp_path / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", _WeasyQueEscribe)
    _WeasyQueEscribe.rutas = []
    salida = _exportar(vista, informe_perfil, destino)
    assert salida.via == M11.VIA_WEASYPRINT and salida.ruta == destino
    assert destino.read_bytes() == PDF_NUEVO
    assert sorted(p.name for p in tmp_path.iterdir()) == ["memoria.pdf"]
    (ruta,) = _WeasyQueEscribe.rutas
    assert ruta.parent == destino.parent and ruta != destino


@pytest.mark.parametrize("vista", ["completa", "resumida"])
def test_3_el_html_para_el_navegador_tambien_se_escribe_atomico(vista, informe_perfil,
                                                                tmp_path, monkeypatch):
    """La via sin weasyprint deja el HTML para Ctrl+P: tampoco a medias."""
    respaldo = tmp_path / "memoria.html"
    respaldo.write_text("<html>la memoria anterior</html>", encoding="utf-8")

    def falla(*_a, **_k):
        raise OSError(errno.EIO, "Input/output error")

    with monkeypatch.context() as m:
        m.setattr(M11.os, "replace", falla)
        with pytest.raises(OSError):
            _exportar(vista, informe_perfil, tmp_path / "memoria.pdf",
                      abrir_navegador=False, forzar_navegador=True)
    assert respaldo.read_text(encoding="utf-8") == "<html>la memoria anterior</html>"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["memoria.html"]
    salida = _exportar(vista, informe_perfil, tmp_path / "memoria.pdf",
                       abrir_navegador=False, forzar_navegador=True)
    assert salida.via == M11.VIA_NAVEGADOR and salida.ruta == respaldo
    assert "la memoria anterior" not in respaldo.read_text(encoding="utf-8")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["memoria.html"]


@pytest.mark.lento
@pytest.mark.skipif(os.name != "posix" or shutil.which("bash") is None,
                    reason="el limite de tamaño de archivo se pone con `ulimit -f` de bash")
def test_3_la_cli_directa_bajo_ulimit_no_destruye_el_pdf_anterior(tmp_path):
    """
    La reproduccion con weasyprint DE VERDAD, como la revision de UI-2: la
    CLI escribe la memoria completa de la corrida de perfil (unos 800 KB de
    PDF) con `ulimit -f 300` (Python ignora SIGXFSZ, y la escritura falla con
    `OSError` [Errno 27] al pasar de 300 KB; el JSON, de unos 145 KB, cabe).
    Antes el PDF anterior del usuario quedaba cortado en 300 KB.
    """
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete")
    destino = tmp_path / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    linea = " ".join(f"'{a}'" for a in (
        sys.executable, str(RAIZ / "cli.py"), str(CSV_EJEMPLO), "--luz", "2.75",
        "--alcance", "perfil", "--json", str(tmp_path / "i.json"), "--pdf", str(destino)))
    hecho = subprocess.run(["bash", "-c", f"ulimit -f 300; exec {linea}"], cwd=RAIZ,
                           capture_output=True, text=True, timeout=TOPE_S)
    assert (tmp_path / "i.json").is_file(), "el JSON no cupo: el test perderia su objeto"
    assert "File too large" in hecho.stderr or "Errno 27" in hecho.stderr, hecho.stderr[-2000:]
    assert hecho.returncode not in (0,)
    assert destino.read_bytes() == PDF_ANTERIOR
    assert sorted(p.name for p in tmp_path.iterdir()) == ["i.json", "memoria.pdf"]


# --- El temporal: unico, corto, junto al archivo real (revision de UI-5, H3) ---
# El primer intento escribia en «<destino>.parcial», un nombre FIJO: (a) un
# destino de nombre largo (248-255 bytes) ya no se podia escribir; (b) un
# archivo del usuario con ese nombre se pisaba y se borraba; (c) dos
# exportaciones al mismo destino compartian el temporal; (d) un destino que es
# enlace simbolico se volvia archivo regular, y un modo 0600 pasaba a 0644. Las
# dos escrituras que lo usaban --- la memoria en PDF de M11 y la entrega del PDF
# del hijo de la ventana (`ProcesoPdf._entregar`, UI-2) --- comparten desde
# aqui UNA funcion, `src/escritura_atomica.escribir_atomico`.

class _WeasyDeContenido:
    """El doble de `WeasyHTML` que escribe `contenido` entero."""

    contenido = PDF_NUEVO

    def __init__(self, *, string, base_url):
        self.string = string

    def write_pdf(self, ruta):
        Path(ruta).write_bytes(_WeasyDeContenido.contenido)


def _escribir_por(via, destino, contenido, informe, monkeypatch, tmp_path):
    """Escribe `contenido` en `destino` por una de las dos vias que lo hacen atomico."""
    if via == "memoria":
        monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
        monkeypatch.setattr(M11, "WeasyHTML", _WeasyDeContenido)
        _WeasyDeContenido.contenido = contenido
        M11.exportar_pdf_resumida(informe, destino, proyecto="UI-5")
        return
    from gui import exportacion_pdf as expdf
    proceso = expdf.ProcesoPdf(sesion={}, destino=destino,
                               directorio_trabajo=tmp_path / "trabajo_del_hijo")
    proceso.ruta_pdf_de_trabajo.parent.mkdir(parents=True, exist_ok=True)
    proceso.ruta_pdf_de_trabajo.write_bytes(contenido)
    proceso._entregar()


VIAS = ["memoria", "entrega del hijo"]


def _sin_restos(directorio, esperados):
    """En `directorio` solo quedan `esperados`: ningun temporal, oculto o no."""
    return sorted(p.name for p in directorio.iterdir()) == sorted(esperados)


@pytest.mark.parametrize("via", VIAS)
def test_3_a_un_destino_de_nombre_largo_se_sigue_escribiendo(via, informe_perfil, tmp_path,
                                                            monkeypatch):
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / ("m" * 246 + ".pdf")          # 250 bytes: cabe; con «.parcial», no
    _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert destino.read_bytes() == PDF_NUEVO
    assert _sin_restos(salida, [destino.name])


@pytest.mark.parametrize("via", VIAS)
def test_3_b_un_archivo_del_usuario_con_el_nombre_del_temporal_no_se_toca(
        via, informe_perfil, tmp_path, monkeypatch):
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / "memoria.pdf"
    suyo = salida / "memoria.pdf.parcial"
    suyo.write_bytes(b"un archivo del usuario")
    _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert destino.read_bytes() == PDF_NUEVO
    assert suyo.read_bytes() == b"un archivo del usuario"
    assert _sin_restos(salida, ["memoria.pdf", "memoria.pdf.parcial"])


def test_3_b_tampoco_cuando_la_escritura_falla(informe_perfil, tmp_path, monkeypatch):
    destino = tmp_path / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    suyo = tmp_path / "memoria.pdf.parcial"
    suyo.write_bytes(b"un archivo del usuario")
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", _WeasyQueFallaAMitad)
    with pytest.raises(OSError):
        M11.exportar_pdf_resumida(informe_perfil, destino, proyecto="UI-5")
    assert destino.read_bytes() == PDF_ANTERIOR
    assert suyo.read_bytes() == b"un archivo del usuario"
    assert _sin_restos(tmp_path, ["memoria.pdf", "memoria.pdf.parcial"])


class _WeasyReentrante:
    """
    Dos exportaciones al MISMO destino a la vez, sin hilos: mientras la
    primera (A) escribe, arranca la segunda (B) y termina. Con un temporal
    compartido, B escribia sobre el archivo que A tenia abierto, lo renombraba,
    y A fallaba al renombrar uno que ya no existia.
    """

    profundidad = 0
    segunda = None

    def __init__(self, *, string, base_url):
        self.string = string

    def write_pdf(self, ruta):
        cls = _WeasyReentrante
        cls.profundidad += 1
        propio = PDF_NUEVO if cls.profundidad == 1 else b"%PDF-B, la segunda\n%%EOF\n"
        try:
            with open(ruta, "wb") as f:
                f.write(propio[:6])
                if cls.profundidad == 1:
                    cls.segunda()
                f.write(propio[6:])
        finally:
            cls.profundidad -= 1


def test_3_c_dos_exportaciones_al_mismo_destino_no_comparten_el_temporal(
        informe_perfil, tmp_path, monkeypatch):
    destino = tmp_path / "memoria.pdf"
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", _WeasyReentrante)
    escritas = []

    def segunda():
        M11.exportar_pdf_resumida(informe_perfil, destino, proyecto="UI-5 B")
        escritas.append(destino.read_bytes())

    _WeasyReentrante.segunda = segunda
    M11.exportar_pdf_resumida(informe_perfil, destino, proyecto="UI-5 A")
    # Cada una deja su PDF ENTERO: B al terminar, y A, que termina despues, gana.
    assert escritas == [b"%PDF-B, la segunda\n%%EOF\n"]
    assert destino.read_bytes() == PDF_NUEVO
    assert _sin_restos(tmp_path, ["memoria.pdf"])


@pytest.mark.skipif(os.name != "posix", reason="enlaces simbolicos y modos POSIX")
@pytest.mark.parametrize("via", VIAS)
def test_3_d_un_enlace_sigue_siendo_enlace_y_el_modo_se_conserva(via, informe_perfil,
                                                                tmp_path, monkeypatch):
    import stat
    real = tmp_path / "carpeta_real" / "memoria_real.pdf"
    real.parent.mkdir()
    real.write_bytes(PDF_ANTERIOR)
    real.chmod(0o600)
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / "memoria.pdf"
    destino.symlink_to(real)
    _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert destino.is_symlink() and destino.resolve() == real.resolve()
    assert real.read_bytes() == PDF_NUEVO
    assert stat.S_IMODE(real.stat().st_mode) == 0o600
    assert _sin_restos(salida, ["memoria.pdf"])
    assert _sin_restos(real.parent, ["memoria_real.pdf"])


def test_3_la_memoria_y_la_entrega_del_hijo_usan_la_misma_escritura_atomica():
    for ruta, funcion in ((RAIZ / "src" / "modulos" / "M11_reporte.py", "_escribir_pdf"),
                          (RAIZ / "gui" / "exportacion_pdf.py", "_entregar")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8-sig"), filename=str(ruta))
        nodo = _funcion(arbol, funcion)
        llamadas = {ast.unparse(n.func) for n in ast.walk(nodo) if isinstance(n, ast.Call)}
        assert "escritura_atomica.escribir_atomico" in llamadas, funcion
        assert "os.replace" not in llamadas, funcion
        cuerpo_sin_docstring = nodo.body[1:] if ast.get_docstring(nodo) else nodo.body
        textos = {n.value for parte in cuerpo_sin_docstring for n in ast.walk(parte)
                  if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert not any(".parcial" in t for t in textos), funcion


# --- Los permisos y los mensajes (verificacion de UI-5, N4) -----------------
# Medido por la verificacion como usuario sin privilegios contra `2d37c2c`:
# (i) un archivo escribible en un directorio SIN permiso de escritura se
# escribia, y con el temporal fallaba nombrando un `.xxxx.parcial`; (ii) un
# archivo 0444 se rechazaba, y con el temporal se reemplazaba en silencio; y
# los errores citaban el temporal y no el destino. Aqui el entorno de la suite
# es root, que no lee permisos: los dos casos se reproducen con un doble de la
# llamada que el sistema contestaria (`mkstemp` sin permiso, `os.access`).

@pytest.mark.parametrize("via", VIAS)
def test_3_e_un_directorio_que_no_admite_el_temporal_escribe_como_antes(
        via, informe_perfil, tmp_path, monkeypatch):
    from src import escritura_atomica as ea
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)

    def sin_permiso(*_a, **_k):
        raise PermissionError(errno.EACCES, "Permission denied", str(salida / ".x.parcial"))

    monkeypatch.setattr(ea.tempfile, "mkstemp", sin_permiso)
    _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert destino.read_bytes() == PDF_NUEVO
    assert _sin_restos(salida, ["memoria.pdf"])


@pytest.mark.parametrize("via", VIAS)
def test_3_e_un_destino_sin_permiso_de_escritura_se_rechaza_nombrandolo(
        via, informe_perfil, tmp_path, monkeypatch):
    from src import escritura_atomica as ea
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    acceso = os.access
    monkeypatch.setattr(ea.os, "access", lambda ruta, modo, *a, **k: (
        False if Path(ruta) == destino and modo == os.W_OK else acceso(ruta, modo, *a, **k)))
    with pytest.raises(PermissionError) as rechazo:
        _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert rechazo.value.filename == str(destino)
    assert destino.read_bytes() == PDF_ANTERIOR
    assert _sin_restos(salida, ["memoria.pdf"])


@pytest.mark.parametrize("via", VIAS)
def test_3_e_un_destino_que_es_un_directorio_falla_nombrando_el_destino(
        via, informe_perfil, tmp_path, monkeypatch):
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / "memoria.pdf"
    destino.mkdir()
    with pytest.raises(OSError) as fallo:
        _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert fallo.value.filename == str(destino) and fallo.value.filename2 is None
    assert ".parcial" not in str(fallo.value)
    assert destino.is_dir() and _sin_restos(salida, ["memoria.pdf"])


def test_3_e_un_directorio_inexistente_o_un_fallo_a_mitad_nombran_el_destino(
        informe_perfil, tmp_path, monkeypatch):
    from src import escritura_atomica as ea
    destino = tmp_path / "no_existe" / "memoria.pdf"
    with pytest.raises(FileNotFoundError) as fallo:
        ea.escribir_atomico(destino, lambda temporal: temporal.write_bytes(PDF_NUEVO))
    assert fallo.value.filename == str(destino)
    destino = tmp_path / "memoria.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", _WeasyQueFallaAMitad)
    with pytest.raises(OSError) as fallo:
        M11.exportar_pdf_resumida(informe_perfil, destino, proyecto="UI-5")
    assert fallo.value.errno == errno.ENOSPC and fallo.value.filename == str(destino)
    assert destino.read_bytes() == PDF_ANTERIOR


@pytest.mark.skipif(os.name != "posix", reason="modos POSIX")
@pytest.mark.parametrize("via", VIAS)
def test_3_d_un_archivo_nuevo_lleva_el_modo_de_siempre(via, informe_perfil, tmp_path,
                                                       monkeypatch):
    """
    GUARDIA (vale antes y despues de la correccion de H3): sin archivo previo,
    el modo es el que daria abrirlo para escribir (el de la mascara del
    proceso), no el 0600 con que nace un temporal unico: el temporal cambia de
    nombre, y con el su modo, al reemplazar.
    """
    import stat
    referencia = tmp_path / "referencia.bin"
    referencia.write_bytes(b"x")
    salida = tmp_path / "salida"
    salida.mkdir()
    destino = salida / "memoria.pdf"
    _escribir_por(via, destino, PDF_NUEVO, informe_perfil, monkeypatch, tmp_path)
    assert stat.S_IMODE(destino.stat().st_mode) == stat.S_IMODE(referencia.stat().st_mode)


# ===========================================================================
# (4) La guardia del archivo de criterios exige la forma de las claves
# ===========================================================================

def _de_texto():
    """El valor de archivo de `espesor_pared_conducto` tal como lo deja JSON."""
    return json.loads(json.dumps(ca.criterio(ESPESOR).valor))


def test_4_la_guardia_rechaza_la_clave_de_texto_por_los_tres_caminos(tmp_path):
    de_texto = _de_texto()
    antes = ca.valores_dinamicos()
    # Declaracion en caliente, en seco y de verdad.
    with pytest.raises(ValueError, match="Escriba 900 sin comillas"):
        ca.verificar_declaracion(ESPESOR, de_texto)
    with pytest.raises(ValueError, match="Escriba 900 sin comillas"):
        ca.establecer_valor_dinamico(ESPESOR, de_texto)
    assert ca.valores_dinamicos() == antes
    # La guardia misma, que es el cuello de los tres caminos.
    with pytest.raises(ValueError, match="ENTERAS"):
        ca._verificar_criterio(ESPESOR, replace(ca.criterio(ESPESOR), valor=de_texto))
    # Escritura permanente: la guardia corre ANTES de tocar el disco.
    copia = tmp_path / "criterios_adoptados.py"
    shutil.copyfile(Path(ca.__file__), copia)
    original = copia.read_bytes()
    with pytest.raises(ValueError, match="ENTERAS"):
        ca.escribir_valor_en_archivo(ESPESOR, de_texto, ruta=str(copia))
    assert copia.read_bytes() == original


def test_4_la_regla_vive_una_vez_en_la_guardia_y_las_capas_de_arriba_no_la_repiten():
    """
    `_exigir_claves` y la lectura del entero escrito se definen UNA vez, en
    `criterios_adoptados.py`; `declaracion.py` (la frontera del JSON) la usa
    y no la copia, y ninguna capa llama aparte a una segunda puerta.
    """
    definiciones, asignaciones = {}, {}
    for ruta in sorted((RAIZ / "src").rglob("*.py")) + [RAIZ / "cli.py"]:
        arbol = ast.parse(ruta.read_text(encoding="utf-8-sig"), filename=str(ruta))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.FunctionDef) and nodo.name in (
                    "_exigir_claves", "verificar_claves_de_la_ficha"):
                definiciones.setdefault(nodo.name, []).append(ruta.name)
            if isinstance(nodo, ast.Assign):
                for destino in nodo.targets:
                    if isinstance(destino, ast.Name) and destino.id == "_ENTERO_ESCRITO" \
                            and isinstance(nodo.value, ast.Call):
                        asignaciones.setdefault(destino.id, []).append(ruta.name)
    assert definiciones == {"_exigir_claves": ["criterios_adoptados.py"]}
    assert asignaciones == {"_ENTERO_ESCRITO": ["criterios_adoptados.py"]}
    # Y ninguna capa la llama aparte: la llama la guardia, por los tres caminos.
    llamadas = []
    for ruta in sorted((RAIZ / "src").rglob("*.py")) + [RAIZ / "cli.py"] + sorted(
            (RAIZ / "gui").rglob("*.py")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8-sig"), filename=str(ruta))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call) and ast.unparse(nodo.func).split(".")[-1] in (
                    "verificar_claves_de_la_ficha", "_verificar_claves_de_la_ficha",
                    "_exigir_claves"):
                llamadas.append((ruta.name, ast.unparse(nodo.func)))
    assert sorted(llamadas) == [("criterios_adoptados.py", "_exigir_claves"),
                                ("criterios_adoptados.py", "_exigir_claves"),
                                ("criterios_adoptados.py", "_verificar_claves_de_la_ficha")]


def test_4_las_puertas_de_arriba_dicen_el_mismo_motivo():
    """
    GUARDIA (vale antes y despues, ficha UI3-03): la pestaña 2 y sus
    editores, la ventana emergente, `--declarar`, el barrido y la frontera del
    JSON rechazan la clave de texto con el MISMO motivo. Desde UI-5 ese motivo
    es el de la guardia del archivo (el test de arriba).
    """
    de_texto = _de_texto()
    mensajes = set()
    for declarar in (lambda: sed.declarar(ESPESOR, de_texto),
                     lambda: dec.declarar_valor(ESPESOR, de_texto),
                     lambda: cli.declarar_criterios([f"{ESPESOR}={de_texto!r}"])):
        with pytest.raises(ValueError) as rechazo:
            declarar()
        mensajes.add(str(rechazo.value))
    assert len(mensajes) == 1 and "Escriba 900 sin comillas" in mensajes.pop()
    resultado = dec.restaurar_sesion({"valores": {ESPESOR: {"hdpe": {"900mm": 0.09}}}},
                                     sustituir=False)
    assert [c for c, _m in resultado.rechazados] == [ESPESOR]
    assert "ENTERAS" in resultado.rechazados[0][1]


# --- El barrido de los 141 --------------------------------------------------

# Las filas de una tabla que la ventana del criterio RECHAZA a proposito: la
# Table B.1 del HDS-5 tiene filas de TMC, de plancha estructural y de
# polietileno corrugado, y `n_manning_hdpe` (HDPE de interior liso) solo
# admite su ventana (0.009, 0.015). No son candidatas: las rechaza la ventana,
# con o sin la regla de las claves. Censadas para que el grupo no crezca en
# silencio.
FILAS_FUERA_DE_SU_VENTANA = {
    ("n_manning_hdpe", f) for f in (
        "cmp_helicoidal_68x13", "cmp_helicoidal_150x25", "cmp_anular_68x13",
        "cmp_anular_125x25", "cmp_anular_75x25", "plancha_estructural_150x50",
        "plancha_estructural_230x64", "polietileno_corrugado_corrugado")}

# Los criterios sin valor de archivo, sin filas elegibles que propongan un
# valor y sin ventana evaluable (numerica, por campo o conjunto cerrado): no
# hay nada que barrer en ellos, y se dice cuales son.
SIN_NADA_QUE_BARRER = {
    "clase_sitio", "riesgo_admisible_propietario", "TW_receptor", "TR_evento_extremo",
    "c_phi_fundacion", "capacidad_portante_adm", "Mw_licuefaccion", "D_max_catalogo",
    "perfil_hdpe_fabricante", "metodo_estabilidad_global",
    # VE-5 (ficha T7B-04): 'talud_delante_del_cabezal' sustituye a
    # 'N_cq_N_gammaq_meyerhof' (retirado).
    "talud_delante_del_cabezal",
    "exposicion_quimica_ems", "peso_especifico_saturado_relleno_kn_m3",
    "edicion_que_rige_el_expediente", "edicion_legal_que_rige_el_expediente",
    # VE-2 (c2): sin valor de archivo y con ventana en prosa (su extremo de
    # arriba depende del NF de cada punto).
    "margen_estacional_nf_v7_m",
    # VE-4d: el caudal unitario admisible del desborde de V8, sin valor de
    # archivo y sin ventana (lo da el diseño de la proteccion del terraplen).
    "caudal_unitario_admisible_desborde_m2s",
    # VE-5 met: lo que agregan los anclajes y empalmes del despiece al acero
    # de los cabezales, sin valor de archivo y sin ventana (ninguna fuente
    # del repositorio la fija: la da el despiece de los planos).
    "incremento_acero_por_despiece",
    # VE-5 (mh, ficha T1-05): los factores K, m, n de la ecuacion (17), [S]
    # sin valor de archivo: un dato de un estudio regional no tiene ventana.
    "factores_idf_regional",
    # VE-5 (gui, ficha T8-11): los techos de transcripcion de la Fase 6,
    # opcional sin valor de archivo; su `sensibilidad` explica las dos
    # lecturas (sin declarar o declarado) y no trae valores que barrer.
    "techos_de_transcripcion_fase_6"}
# VE-3.5 lo habia sumado ('dimensionamiento_zapata_cabezal', sin valor de
# archivo y sin ventana). Desde VE-3.9 tiene valor de archivo y ventana por
# campo (decision del dueño), y ya hay que barrer.


def _formas(c):
    return c.forma if isinstance(c.forma, tuple) else (c.forma,)


def _extremos_de_la_ventana(c):
    s, formas = c.sensibilidad, _formas(c)
    rango = ca._rango_numerico(s)
    if rango is not None and len(rango) == 2:
        if ca.FORMA_PAR_ORDENADO in formas:
            return [("ventana (min, max)", tuple(rango))]
        convertir = int if formas == (ca.FORMA_INT,) else (lambda x: x)
        return [("ventana min", convertir(rango[0])), ("ventana max", convertir(rango[1]))]
    if isinstance(s, dict) and isinstance(c.valor, dict):
        return [(f"ventana por campo {nombre}", {**c.valor, **{k: par[i] for k, par in s.items()}})
                for i, nombre in ((0, "min"), (1, "max"))]
    if ca.FORMA_CATEGORIA in formas and isinstance(s, tuple):
        return [(f"opcion {x}", x) for x in s]
    return []


def _candidatos():
    """{clave: [(de donde, valor), ...]} y las filas que su ventana rechaza."""
    por_clave, fuera = {}, set()
    for clave, c in ca.CRITERIOS.items():
        candidatos = [("archivo", c.valor)] if c.valor is not None else []
        esquema = sed.esquema_de(clave)
        rango = ca._rango_numerico(c.sensibilidad)
        for opcion in esquema.opciones_de_tabla:
            if not opcion.elegible:
                continue
            valor = ((opcion.fila,) if esquema.tipo_de_editor == sed.SERIE_DE_CLAVES
                     else opcion.valor_propuesto)
            if valor is None:
                continue
            if rango is not None and len(rango) == 2:
                extremos = valor if isinstance(valor, tuple) else (valor,)
                if not all(rango[0] <= x <= rango[1] for x in extremos if ca._es_real(x)):
                    fuera.add((clave, opcion.fila))
                    continue
            candidatos.append((f"fila {opcion.fila}", valor))
        candidatos += _extremos_de_la_ventana(c)
        por_clave[clave] = candidatos
    return por_clave, fuera


@pytest.fixture(scope="module")
def candidatos():
    return _candidatos()


def test_4_el_barrido_cubre_los_141_y_censa_lo_que_no_barre(candidatos):
    por_clave, fuera = candidatos
    # 146 desde VE-2: 'columna_n_manning_concreto' (a), 'diametro_de_diseno_concreto' (g),
    # 'nivel_agua_diseno_v7' y 'margen_estacional_nf_v7_m' (c2), 'factor_intervalo_fijo_p24' (d).
    # 147 desde VE-3.5: 'dimensionamiento_zapata_cabezal'; 148 con el de VE-3.7,
    # 'fraccion_fin_remanso_canal' (las dos ramas se integraron juntas).
    # 149 desde VE-3.12: 'relleno_max_contraste_acpa_m' (decision 6 del dueño).
    # 153 desde VE-3.14: 'agua_del_relleno_bajo_sismo' (H-3 de los ensayos) y
    # las opciones 9, 10 y 13 ('momento_talon_cabezal', 'carga_pantalla_cabezal',
    # 'distribucion_incremento_sismico').
    # 154 desde VE-4a: 'fila_phi_estabilidad_global' (la fila de phi de
    # AASHTO 11.6.3.7 para el FS declarado de E4 y E5).
    # 155 desde VE-4c: 'sobreelevacion_admisible_remanso_m' (el fin del perfil
    # de remanso de V5, ficha T7B-01).
    # 157 desde VE-4d: 'caudal_unitario_admisible_desborde_m2s' y
    # 'coeficientes_desborde_plataforma' (el desborde admitido de V8).
    # 158 desde VE-4e: 'nivel_agua_relleno_sin_drenaje_bajo_sismo' (ficha
    # VE3-21), sin valor de archivo y con sus dos opciones barribles.
    # 159 desde VE-5-m6: 'relacion_co_poza_enrocado_hec14' (la poza de
    # enrocado de HEC-14 Sec. 10.1, VE-4g).
    # 162 desde VE-5-met: 'sobreancho_excavacion_estructuras_m' (opcional,
    # ventana 0-0.45 m de EG-2013 501.04), 'incremento_acero_por_despiece' y
    # 'clase_concreto_losa_entrega' (los metrados de la Fase 11).
    # 163 desde VE-5-m8 (VE-4f): 'carga_viva_tubo_concreto_somero' (ficha VE4F-01),
    # sin valor de archivo y con sus dos lecturas barribles.
    # 164 desde VE-5-m9: 'empuje_sismico_muro_que_no_cede' (ficha T7B-14).
    # 165 con el item 3 de VE-5-m9 (ficha T7B-04): sale
    # 'N_cq_N_gammaq_meyerhof' y entran 'talud_delante_del_cabezal' y
    # 'factores_forma_profundidad_portante'.
    # 167 desde VE-5-mh: 'factores_idf_regional' [S] (ficha T1-05), sin valor,
    # e 'intervalos_de_clase_chi_cuadrado' [A] (ficha T1-01).
    # 168 desde VE-5-gui: 'techos_de_transcripcion_fase_6' (ficha T8-11).
    assert len(por_clave) == len(ca.CRITERIOS) == 168
    assert fuera == FILAS_FUERA_DE_SU_VENTANA
    assert {k for k, cs in por_clave.items() if not cs} == SIN_NADA_QUE_BARRER
    # Y el barrido no es de juguete: cada valor de archivo esta, y mas.
    con_valor = sum(1 for c in ca.CRITERIOS.values() if c.valor is not None)
    assert sum(len(cs) for cs in por_clave.values()) > 3 * con_valor


def test_4_cada_candidato_pasa_la_guardia_por_el_archivo_y_en_caliente(candidatos):
    """
    Archivo (`_verificar_criterio` sobre el Criterio que resultaria) y
    declaracion en caliente (`verificar_declaracion` y
    `establecer_valor_dinamico`, que se retira). Un criterio derivado no se
    declara por diseño (EXT-V-04): solo pasa por el camino del archivo.
    """
    por_clave, _ = candidatos
    rechazos = []
    for clave, cs in por_clave.items():
        c = ca.CRITERIOS[clave]
        if c.valor is not None:
            ca._verificar_criterio(clave, c)
        for de_donde, valor in cs:
            try:
                ca._verificar_criterio(clave, replace(c, valor=valor))
                if isinstance(c.resolucion, Derivada):
                    continue
                ca.verificar_declaracion(clave, valor)
                ca.establecer_valor_dinamico(clave, valor)
                ca.quitar_valor_dinamico(clave)
            except (ValueError, KeyError) as exc:
                rechazos.append((clave, de_donde, str(exc)[:200]))
    assert rechazos == []


def test_4_cada_candidato_pasa_la_guardia_de_la_escritura_permanente(candidatos, tmp_path,
                                                                     monkeypatch):
    """
    `escribir_valor_en_archivo` sobre un archivo de UNA entrada por criterio
    (la guardia corre antes de leerlo, y el patron es el mismo): pasa la
    guardia o se detiene en el limite del patron, que no admite un literal con
    comas y no es la guardia.
    """
    por_clave, _ = candidatos
    monkeypatch.setattr(ca, "CRITERIOS", dict(ca.CRITERIOS))
    rechazos = []
    for clave, cs in por_clave.items():
        c = ca.CRITERIOS[clave]
        if isinstance(c.resolucion, Derivada):
            continue
        for de_donde, valor in cs:
            archivo = tmp_path / "una_entrada.py"
            archivo.write_text(f'CRITERIOS = {{\n    "{clave}": Criterio(\n'
                               f'        valor=None,\n    ),\n}}\n', encoding="utf-8")
            try:
                ca.escribir_valor_en_archivo(clave, valor, ruta=str(archivo))
            except ValueError as exc:
                if not str(exc).startswith(f"Reescribir 'valor=' de '{clave}'"):
                    rechazos.append((clave, de_donde, str(exc)[:200]))
            finally:
                ca.CRITERIOS[clave] = c
    assert rechazos == []


def test_4_cada_candidato_vuelve_de_una_sesion_json(candidatos):
    """
    `restaurar_sesion` de una sesion JSON de verdad (`json.dumps` y
    `json.loads`: las claves enteras vuelven como texto y la frontera del JSON
    las rearma), una ronda por candidato: ninguno se rechaza.
    """
    por_clave, _ = candidatos
    rondas = max(len(cs) for cs in por_clave.values())
    for i in range(rondas):
        valores = {clave: cs[i][1] for clave, cs in por_clave.items()
                   if i < len(cs) and not isinstance(ca.CRITERIOS[clave].resolucion, Derivada)}
        bloque = json.loads(json.dumps({"valores": valores, "procedencias": {}}))
        resultado = dec.restaurar_sesion(bloque, sustituir=True)
        assert resultado.rechazados == (), (i, resultado.rechazados[:3])
        assert set(resultado.restaurados) == set(valores)
    dec.restaurar_sesion({"valores": {}}, sustituir=True)
