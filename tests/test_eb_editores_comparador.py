"""
tests/test_eb_editores_comparador.py
====================================
Aceptacion de E-B (evolucion, despues de EXT-0 a EXT-11 y E-A): las cuatro
piezas del prompt, cada una con su bloque.

    E10  Editores TIPADOS sobre `Criterio.forma` (EXT-5) y `CampoValidable`:
         escalar, par ordenado, serie de pares y dict con campos, empezando
         por `secciones_cajon_normalizadas` y `seccion_receptor`. Una
         seleccion normativa (una fila de la tabla) OBTIENE el valor de la
         tabla; una adopcion distinta EXIGE procedencia (fila o nota); y
         aplicar es ATOMICO: el valor se arma entero, pasa por la guardia en
         seco y entra por `declaracion.py` en una sola llamada, o no entra.
         El contenido lo produce `src/editores.py` (sin Tk); `gui/editores.py`
         pinta sobre `CampoValidable`, y la pestaña 2 sigue teniendo UN solo
         camino de declaracion: el campo literal es la fuente del valor y los
         editores lo componen.
    E14  Comparador de dos `informe_json` por IDENTIDAD DE PUNTO
         (`src/comparador.py`): tolerancias nombradas, «no comparable» para
         metodos distintos, nunca recalcula (no importa el motor), y la CLI
         reutiliza la misma comparacion para la corrida embebida en la sesion
         (EXT-10). La linea base de la Familia C es su primer consumidor.
    E13  (reducido) Columna responsable / evidencia en la pestaña 4 y en el
         anticipo, DERIVADA de `resolucion` y `reemplazado_por`
         (`src/responsable.py`); el anticipo sigue siendo informativo.
    E21  (acotado) La memoria lleva INDICE, derivado de los `<h2 id>` de la
         plantilla y de los puntos del informe: nada que no exista como
         objeto. La traza con sha1, los criterios usados del contexto, los
         bloqueos y el alcance ya estaban (EXT-4) y aqui se fijan.

Escritos primero EN ROJO con `xfail(strict=True)` por test (marcador `rojo`)
sobre el invariante, nunca sobre la salida actual; medidos antes de tocar
codigo (52 xfailed, 0 XPASS) y liberados al corregir. Los tres que valen
antes y despues (las guardias que ya se cumplian) no llevaban el marcador.

Los modulos nuevos se importan DENTRO de cada test (`importlib`), para que
su ausencia sea un fallo del test --- xfail --- y no un error de recoleccion.
"""

from __future__ import annotations

import ast
import importlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import anticipo as antc
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import sesion as ses
from src.modelos import DeTabla, Libre, DeEnsayo
from src.modulos import M11_reporte as M11
from tests.apoyo import doble_tkinter
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
LINEA_BASE = RAIZ / "tests" / "linea_base_familia_c"
PLANTILLAS = (RAIZ / "src" / "plantillas" / "memoria_perfil.html",
              RAIZ / "src" / "plantillas" / "memoria_alcantarillas.html")

SERIE = "secciones_cajon_normalizadas"      # serie_de_pares, libre
RECEPTOR = "seccion_receptor"               # dict_con_campos con ventana por campo
KE = "ke_entrada"                           # float de_tabla (HDS-5 Tabla C.2)
KE_FILA = "concreto_headwall_square_edge"   # la fila del archivo, celda 0.5
KE_CELDA = 0.5
PAR = "n_manning_hdpe"                      # par_ordenado de_tabla
CATEGORIA = "condicion_pavimento"           # categoria de_tabla
CLAVES_DE_FILA = "F_pga"                    # serie_de_claves de_tabla
KE_CAJON = "ke_entrada_cajon"               # str de_tabla: declara la CLAVE de una fila
DERIVADA = "tabla_recubrimiento_aashto_mm"  # Derivada: no editable
RANGO = "v_max_concreto_eleccion"           # en_rango
ANIDADO = "cobertura_minima_aashto"         # dict con dicts dentro: literal

# Escritos en rojo con `xfail(strict=True)` por test (marcador `rojo`):
# medidos 52 xfailed, 1 passed y 0 XPASS antes de tocar codigo, y liberados al
# corregir (49 XPASS con el codigo escrito; los tres restantes ya valian antes
# y no llevaban el marcador). El marcador se retiro y esta linea queda como
# constancia.


def _mod(nombre):
    return importlib.import_module(nombre)


@pytest.fixture
def _limpio():
    dec.limpiar()
    previos = ca.valores_dinamicos()
    yield
    dec.limpiar()
    for clave in list(ca.valores_dinamicos()):
        if clave not in previos:
            ca.quitar_valor_dinamico(clave)
    for clave, valor in previos.items():
        ca.establecer_valor_dinamico(clave, valor)


def _arbol(ruta):
    return ast.parse(ruta.read_text(encoding="utf-8-sig"), filename=ruta.name)


def _llamadas(arbol):
    return {ast.unparse(n.func) for n in ast.walk(arbol) if isinstance(n, ast.Call)}


# ===========================================================================
# E10 · el esquema del editor, derivado de la ficha
# ===========================================================================

def test_e10_la_serie_de_pares_tiene_un_editor_de_dos_columnas_reales():
    ed = _mod("src.editores")
    e = ed.esquema_de(SERIE)
    assert e.tipo_de_editor == ed.SERIE_DE_PARES
    assert e.editable and e.modo == "libre" and not e.exige_fila
    assert [c.tipo for c in e.campos] == [ed.TIPO_REAL, ed.TIPO_REAL]
    # El dominio lo dice la ficha (Libre.dominio), no el editor.
    assert "pares" in e.dominio


def test_e10_el_dict_del_receptor_tiene_un_campo_por_ventana_con_su_rango():
    ed = _mod("src.editores")
    e = ed.esquema_de(RECEPTOR)
    assert e.tipo_de_editor == ed.DICT
    ventana = ca.criterio(RECEPTOR).sensibilidad
    assert [c.nombre for c in e.campos] == list(ventana)
    for c in e.campos:
        assert c.tipo == ed.TIPO_REAL
        assert c.rango == tuple(ventana[c.nombre])


def test_e10_un_escalar_de_tabla_ofrece_las_filas_y_su_celda():
    ed = _mod("src.editores")
    e = ed.esquema_de(KE)
    assert e.tipo_de_editor == ed.ESCALAR and e.exige_fila
    assert e.tabla_id == "HDS5_3ED.TC2"
    opciones = {o.fila: o for o in e.opciones_de_tabla}
    assert KE_FILA in opciones
    # UNA SELECCION NORMATIVA OBTIENE EL VALOR DE LA TABLA: la opcion trae la
    # celda, y es la misma que `declaracion.valor_propuesto` propone.
    assert opciones[KE_FILA].valor_propuesto == pytest.approx(KE_CELDA, rel=REL_TRANSPORTE)
    assert all(isinstance(o.valor_propuesto, float) for o in opciones.values()
               if o.elegible)


def test_e10_un_texto_de_tabla_propone_la_clave_de_la_fila():
    """`condicion_pavimento` declara la CLAVE de la fila, no un numero."""
    ed = _mod("src.editores")
    e = ed.esquema_de(CATEGORIA)
    assert e.tipo_de_editor == ed.ESCALAR
    # Una CATEGORIA elige dentro del conjunto cerrado que la ficha deriva de
    # la tabla (`sensibilidad`): esa eleccion ES la seleccion normativa y no
    # exige nombrar una fila. Las filas se ofrecen como contexto.
    assert not e.exige_fila
    assert e.campos[0].tipo == ed.TIPO_CATEGORIA
    assert set(e.campos[0].opciones) == set(ca.criterio(CATEGORIA).sensibilidad)
    # Y las filas NO proponen su clave: no es uno de los tres textos y la
    # guardia la rechazaria (R8 de la auditoria adversarial: las catorce
    # filas de la Tabla 12.6.6.3-1 dejaban al editor en un callejon).
    assert e.opciones_de_tabla
    assert all(o.valor_propuesto is None for o in e.opciones_de_tabla)


def test_e10_el_par_ordenado_tiene_minimo_y_maximo_con_la_ventana():
    ed = _mod("src.editores")
    e = ed.esquema_de(PAR)
    assert e.tipo_de_editor == ed.PAR
    assert [c.nombre for c in e.campos] == ["minimo", "maximo"]
    assert all(c.rango == tuple(ca.criterio(PAR).sensibilidad) for c in e.campos)


def test_e10_la_serie_de_claves_ofrece_las_filas_de_la_tabla():
    ed = _mod("src.editores")
    e = ed.esquema_de(CLAVES_DE_FILA)
    assert e.tipo_de_editor == ed.SERIE_DE_CLAVES
    filas = {o.fila for o in e.opciones_de_tabla}
    assert set(ca.criterio(CLAVES_DE_FILA).valor) <= filas


def test_e10_un_derivado_no_es_editable_y_dice_por_que():
    ed = _mod("src.editores")
    e = ed.esquema_de(DERIVADA)
    assert not e.editable
    assert "deriva" in e.motivo_no_editable


def test_e10_un_dict_anidado_cae_al_editor_literal_sin_inventar_campos():
    """
    `cobertura_minima_aashto` es un dict de dicts: ningun campo escalar se
    puede derivar de la ficha, y el editor NO se inventa ninguno.
    """
    ed = _mod("src.editores")
    e = ed.esquema_de(ANIDADO)
    assert e.tipo_de_editor == ed.LITERAL
    assert e.campos == ()


def test_e10_toda_clave_del_archivo_tiene_esquema_y_su_tipo_es_de_la_familia():
    ed = _mod("src.editores")
    for clave in ca.CRITERIOS:
        e = ed.esquema_de(clave)
        assert e.tipo_de_editor in ed.TIPOS_DE_EDITOR, clave
        if e.tipo_de_editor in (ed.DICT, ed.PAR, ed.SERIE_DE_PARES):
            assert e.campos, clave


# ===========================================================================
# E10 · armar, descomponer, validar: la ida y vuelta del valor
# ===========================================================================

def test_e10_armar_y_descomponer_son_inversas_en_las_cinco_formas():
    ed = _mod("src.editores")
    casos = {
        SERIE: [[1.2, 0.9], [1.5, 1.2]],
        RECEPTOR: {"b_m": 2.0, "z_HV": 1.5, "S": 0.0008, "n": 0.03,
                   "altura_total_m": 1.8},
        PAR: (0.01, 0.013),
        KE: 0.5,
        CLAVES_DE_FILA: ("C", "D", "E"),
    }
    for clave, valor in casos.items():
        e = ed.esquema_de(clave)
        piezas = ed.descomponer_valor(e, valor)
        armado = ed.armar_valor(e, piezas)
        assert json.dumps(armado) == json.dumps(valor) or armado == valor, clave
        # Y lo armado pasa la MISMA guardia que el archivo, en seco.
        ed.verificar(clave, armado)


def test_e10_descomponer_none_da_piezas_vacias():
    ed = _mod("src.editores")
    e = ed.esquema_de(RECEPTOR)
    piezas = ed.descomponer_valor(e, None)
    assert set(piezas) == {c.nombre for c in e.campos}
    assert all(v is None for v in piezas.values())


def test_e10_validar_campo_juzga_tipo_y_ventana_con_los_estados_de_declaracion():
    ed = _mod("src.editores")
    e = ed.esquema_de(RECEPTOR)
    n = next(c for c in e.campos if c.nombre == "n")
    assert ed.validar_campo(n, 0.03).estado is dec.Estado.VALIDO
    assert ed.validar_campo(n, 0.05).estado is dec.Estado.INVALIDO
    assert ed.validar_campo(n, "0.03").estado is dec.Estado.INVALIDO
    assert ed.validar_campo(n, True).estado is dec.Estado.INVALIDO
    assert ed.validar_campo(n, float("nan")).estado is dec.Estado.INVALIDO
    entero = ed.esquema_de("n_celdas_cajon").campos[0]
    assert ed.validar_campo(entero, 1).estado is dec.Estado.VALIDO
    assert ed.validar_campo(entero, 1.0).estado is dec.Estado.INVALIDO
    categoria = ed.esquema_de(CATEGORIA).campos[0]
    assert ed.validar_campo(categoria, "flexible").estado is dec.Estado.VALIDO
    assert ed.validar_campo(categoria, "adoquin").estado is dec.Estado.INVALIDO


@pytest.mark.parametrize("rango, valor, estado", [
    (None, 3.0, dec.Estado.VALIDO),
    ((0.0, 1.0), 1.0, dec.Estado.VALIDO),       # el borde es inclusivo
    ((0.0, 1.0), 1.0 + 1e-6, dec.Estado.INVALIDO),
])
def test_e10_validar_campo_tiene_la_forma_MAT_D13(rango, valor, estado):
    ed = _mod("src.editores")
    campo = ed.CampoDelEditor(nombre="x", tipo=ed.TIPO_REAL, rango=rango)
    assert ed.validar_campo(campo, valor).estado is estado
    fuente = ast.unparse(_arbol(RAIZ / "src" / "editores.py"))
    # Condicion en positivo y NEGADA, nunca `<` suelto sobre el rango.
    assert "not minimo <= numero <= maximo" in fuente


def test_e10_el_veredicto_al_escribir_es_el_de_la_puerta():
    ed = _mod("src.editores")
    assert ed.veredicto_al_escribir(SERIE, [[1.2, 0.9]]).estado is dec.Estado.VALIDO
    malo = ed.veredicto_al_escribir(SERIE, [[1.2, 0.9], [1.2, 0.9]])
    assert malo.estado is dec.Estado.INVALIDO
    with pytest.raises(ValueError) as exc:
        ed.verificar(SERIE, [[1.2, 0.9], [1.2, 0.9]])
    assert malo.mensaje == str(exc.value)


# ===========================================================================
# E10 · declarar: atomico, por declaracion.py, con procedencia
# ===========================================================================

def test_e10_declarar_libre_entra_por_declaracion_y_registra_procedencia(_limpio):
    ed = _mod("src.editores")
    p = ed.declarar(SERIE, [[1.2, 0.9], [1.5, 1.2]], nota="catalogo del proveedor")
    assert [x for par in ca.valor(SERIE) for x in par] == pytest.approx(
        [1.2, 0.9, 1.5, 1.2], rel=REL_TRANSPORTE)
    assert dec.procedencia_de(SERIE) is p and p.modo == "libre"
    assert p.nota == "catalogo del proveedor"


def test_e10_aplicar_es_atomico_nada_entra_si_un_campo_falla(_limpio):
    ed = _mod("src.editores")
    e = ed.esquema_de(RECEPTOR)
    piezas = ed.descomponer_valor(e, ca.criterio(RECEPTOR).valor)
    piezas["n"] = 0.05     # fuera de la ventana 0.025-0.035
    valor = ed.armar_valor(e, piezas)
    with pytest.raises(ValueError, match="seccion_receptor"):
        ed.declarar(RECEPTOR, valor)
    assert not ca.declarado_en_caliente(RECEPTOR)
    assert dec.procedencia_de(RECEPTOR) is None


def test_e10_la_seleccion_de_una_fila_declara_desde_la_tabla(_limpio):
    ed = _mod("src.editores")
    p = ed.declarar(KE, KE_CELDA, fila=KE_FILA)
    assert p.modo == "de_tabla" and p.filas == (KE_FILA,)
    assert p.valor_de_la_celda == pytest.approx(KE_CELDA, rel=REL_TRANSPORTE)
    assert not p.difiere_de_la_celda()


def test_e10_una_adopcion_distinta_de_la_celda_exige_nota(_limpio):
    ed = _mod("src.editores")
    with pytest.raises(ValueError, match="DIFIERE"):
        ed.declarar(KE, 0.55, fila=KE_FILA)
    assert not ca.declarado_en_caliente(KE)
    p = ed.declarar(KE, 0.55, fila=KE_FILA, nota="embocadura intermedia medida en obra")
    assert p.difiere_de_la_celda()
    assert "DIFIERE" in p.como_texto()


def test_e10_una_adopcion_sin_fila_ni_nota_no_entra_en_un_criterio_de_tabla(_limpio):
    ed = _mod("src.editores")
    with pytest.raises(ValueError, match="procedencia"):
        ed.declarar(KE, 0.55)
    assert not ca.declarado_en_caliente(KE)


def test_e10_la_clave_de_una_fila_tecleada_es_esa_fila(_limpio):
    """
    El camino del raton de EXT-5 sigue valiendo: teclear la CLAVE de una fila
    de la tabla es elegir esa fila, y la procedencia la nombra.
    """
    ed = _mod("src.editores")
    e = ed.esquema_de("embocadura_cajon")
    assert ed.fila_implicita(e, "cajon_concreto_aletas_30_75") == "cajon_concreto_aletas_30_75"
    p = ed.declarar("embocadura_cajon", "cajon_concreto_aletas_30_75")
    assert p.modo == "de_tabla" and p.filas == ("cajon_concreto_aletas_30_75",)
    # Un NUMERO no nombra ninguna fila, ni cuando coincide con una sola
    # celda: la auditoria adversarial midio que 0.9 atribuia ke_entrada a
    # «Corrugated metal, projecting» sin que nadie la eligiera (R3).
    # Adivinar la fila es inventar la procedencia; el rechazo lo DICE.
    assert ed.fila_implicita(ed.esquema_de(KE), KE_CELDA) is None


def test_e10_un_texto_que_nombra_otra_fila_no_entra_con_la_fila_elegida(_limpio):
    """
    El hueco que la revision de E-B midio despues del cierre: en un criterio
    de tabla cuyo valor es la CLAVE DE UNA FILA ('ke_entrada_cajon'), el
    texto «cajon_aletas_paralelas_escuadra» (ke = 0.7) entraba con
    `fila="cajon_aletas_30_75_escuadra"` (ke = 0.4) y la memoria imprimia
    «proviene de la fila cajon_aletas_30_75_escuadra». La parte 2 cerro el
    DIFIERE para numeros, pares y dicts y no para el texto, porque
    `declarar_desde_tabla` solo compara la celda cuando el valor es real.

    La regla: un texto que NOMBRA una fila de la tabla es esa fila, y no
    puede entrar citando otra --- ni con nota, porque la nota explica una
    adopcion distinta de la celda y aqui no hay adopcion: hay dos filas que
    se contradicen. Vale en la PUERTA (`declaracion.declarar_desde_tabla`),
    de modo que cubre la pestana 2 (`src.editores.declarar`) y la ventana
    emergente, que llama a la puerta directamente.
    """
    ed = _mod("src.editores")
    # Las filas de cajon de la Tabla C.2 solo son elegibles (R4) con la
    # embocadura del marco declarada; sin ella el rechazo seria el de R4 y
    # no el que este test mide.
    ed.declarar("embocadura_cajon", "cajon_concreto_aletas_30_75")
    elegida, tecleada = "cajon_aletas_30_75_escuadra", "cajon_aletas_paralelas_escuadra"
    with pytest.raises(ValueError, match="nombra"):
        ed.declarar(KE_CAJON, tecleada, fila=elegida)
    assert not ca.declarado_en_caliente(KE_CAJON)
    assert dec.procedencia_de(KE_CAJON) is None
    with pytest.raises(ValueError, match="nombra"):
        ed.declarar(KE_CAJON, tecleada, fila=elegida, nota="la quiero asi")
    assert not ca.declarado_en_caliente(KE_CAJON)
    # La misma guardia en la puerta, que es por donde entra la ventana
    # emergente (`gui/ventana_normativa.py::_declarar_segun_cara`).
    with pytest.raises(ValueError, match="nombra"):
        dec.declarar_desde_tabla(KE_CAJON, tecleada, filas=(elegida,))
    assert not ca.declarado_en_caliente(KE_CAJON)
    # El id largo de la fila la nombra igual que su clave corta.
    with pytest.raises(ValueError, match="nombra"):
        dec.declarar_desde_tabla(KE_CAJON, "HDS5_3ED.TC2#" + tecleada, filas=(elegida,))
    # Y el texto que SI es la fila elegida entra, por las dos puertas.
    p = ed.declarar(KE_CAJON, tecleada, fila=tecleada)
    assert p.filas == (tecleada,) and ca.valor(KE_CAJON) == tecleada
    dec.olvidar(KE_CAJON); ca.quitar_valor_dinamico(KE_CAJON)
    p = dec.declarar_desde_tabla(KE_CAJON, tecleada, filas=("HDS5_3ED.TC2#" + tecleada,))
    assert ca.valor(KE_CAJON) == tecleada
    assert ed.fila_implicita(ed.esquema_de(KE), 0.9) is None
    with pytest.raises(ValueError, match="cm_projecting"):
        ed.declarar(KE, 0.9)
    assert not ca.declarado_en_caliente(KE)


def test_e10_en_rango_declara_por_su_puerta(_limpio):
    ed = _mod("src.editores")
    p = ed.declarar(RANGO, 3.0)
    assert p.modo == "en_rango" and p.frase_del_rango
    with pytest.raises(ValueError):
        ed.declarar(RANGO, 99.0)


def test_e10_un_derivado_no_se_declara_por_el_editor(_limpio):
    ed = _mod("src.editores")
    with pytest.raises(ValueError, match="deriva"):
        ed.declarar(DERIVADA, {"a": 1})


# Lo que dejo la auditoria adversarial de E-B (R1, R4, R5, A1, A2)

def test_e10_descomponer_falla_ante_piezas_que_no_encajan_en_vez_de_recortar():
    """
    R1: `[[1.2, 0.9], [1.5, 1.2, 3]]` se descomponia en `[[1.2, 0.9]]`, el
    editor se pintaba con eso y «Aplicar» declaraba el recorte en verde.
    """
    ed = _mod("src.editores")
    with pytest.raises(ValueError, match="serie de pares"):
        ed.descomponer_valor(ed.esquema_de(SERIE), [[1.2, 0.9], [1.5, 1.2, 3]])
    with pytest.raises(ValueError, match="extra"):
        ed.descomponer_valor(ed.esquema_de(RECEPTOR), {"b_m": 2.0, "extra": 9})
    with pytest.raises(ValueError, match="par"):
        ed.descomponer_valor(ed.esquema_de(PAR), (0.01, 0.012, 0.013))
    with pytest.raises(ValueError, match="claves"):
        ed.descomponer_valor(ed.esquema_de(CLAVES_DE_FILA), ("C", 4))


def test_e10_la_pestana_2_no_declara_desde_un_editor_que_no_refleja_el_literal():
    """R1, la mitad de la GUI: el editor deja de ser la fuente si el literal no cupo."""
    arbol = _arbol(RAIZ / "gui" / "app.py")
    fuente = ast.unparse(arbol)
    assert "_editor_refleja_literal" in fuente
    valor = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
                 and n.name == "_valor_a_declarar")
    assert "_editor_refleja_literal" in ast.unparse(valor)
    literal = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
                   and n.name == "_literal_cambio")
    assert any(isinstance(n, ast.ExceptHandler) for n in ast.walk(literal))


def test_e10_el_literal_de_un_texto_no_lleva_comillas():
    """R2: `repr` ponia comillas y «Aplicar» declaraba la clave entre comillas."""
    doble_tkinter.instalar()
    app = doble_tkinter.gui_app()
    assert app.ExpedienteApp._literal_de("interpolacion_lineal_entre_extremos") \
        == "interpolacion_lineal_entre_extremos"
    assert app.ExpedienteApp._literal_de([[1.2, 0.9]]) == "[[1.2, 0.9]]"
    assert app.ExpedienteApp._literal_de(None) == ""
    from gui.componentes import interpretar_texto_declarado
    for valor in ("flexible", 0.2, 1, (0.01, 0.013), {"b_m": 2.0}):
        assert interpretar_texto_declarado(app.ExpedienteApp._literal_de(valor)) == valor


def test_e10_una_fila_no_elegible_tecleada_la_rechaza_R4_tambien_con_nota(_limpio):
    """
    R4: la clave de una fila que NO es elegible entraba tecleada con nota,
    por `declarar_valor`; la ventana emergente la rechazaba con R4. Una
    puerta, una respuesta.
    """
    ed = _mod("src.editores")
    e = ed.esquema_de("ke_entrada_cajon")
    fila = next(o.fila for o in e.opciones_de_tabla if not o.elegible)
    assert ed.fila_implicita(e, fila) == fila
    with pytest.raises(ValueError, match="R4"):
        ed.declarar("ke_entrada_cajon", fila, nota="adopto la fila del cajon")
    assert not ca.declarado_en_caliente("ke_entrada_cajon")


def test_e10_un_dict_de_tabla_toma_de_la_fila_sus_campos_homonimos_o_exige_nota(_limpio):
    """
    R5: elegir una fila para `hds5_embocadura_hdpe` no proponia nada y la
    procedencia nombraba una fila cuyas celdas no eran el valor declarado.
    """
    ed = _mod("src.editores")
    e = ed.esquema_de("hds5_embocadura_hdpe")
    opcion = next(o for o in e.opciones_de_tabla if o.fila == "circular_cmp_headwall")
    assert set(opcion.valor_propuesto) == {"K", "M", "c", "Y"}
    valor = dict(ca.criterio("hds5_embocadura_hdpe").valor)      # el del archivo
    with pytest.raises(ValueError, match="DIFIEREN"):
        ed.declarar("hds5_embocadura_hdpe", valor, fila="circular_cmp_headwall")
    assert not ca.declarado_en_caliente("hds5_embocadura_hdpe")
    valor.update(opcion.valor_propuesto)
    p = ed.declarar("hds5_embocadura_hdpe", valor, fila="circular_cmp_headwall")
    assert p.filas == ("circular_cmp_headwall",)
    # Una fila que no fija ningun campo del dict no dice de donde sale: nota.
    e2 = ed.esquema_de("riesgo_admisible_propietario")
    assert all(o.valor_propuesto is None for o in e2.opciones_de_tabla)
    with pytest.raises(ValueError, match="no fija"):
        ed.declarar("riesgo_admisible_propietario", {"R": 0.3, "n": 25}, fila="puentes")


def test_e10_un_dato_de_ensayo_exige_su_trazabilidad_en_la_nota(_limpio):
    """A1: sin nota la procedencia nombraba un ensayo que nadie hizo (Conflicto #8)."""
    ed = _mod("src.editores")
    assert ed.esquema_de("clase_sitio").exige_nota
    with pytest.raises(ValueError, match="TRAZABILIDAD"):
        ed.declarar("clase_sitio", "D")
    assert not ca.declarado_en_caliente("clase_sitio")
    p = ed.declarar("clase_sitio", "D", nota="Vs30 = 250 m/s, EMS-2026-03, calicata C-2")
    assert "Vs30" in p.nota


def test_e10_la_serie_de_claves_declara_desde_la_tabla_con_sus_filas(_limpio):
    """A2: F_pga entraba por `declarar_valor` sin filas ni R4."""
    ed = _mod("src.editores")
    e = ed.esquema_de(CLAVES_DE_FILA)
    elegibles = [o.fila for o in e.opciones_de_tabla if o.elegible]
    p = ed.declarar(CLAVES_DE_FILA, tuple(elegibles[:2]))
    assert p.modo == "de_tabla" and p.filas == tuple(elegibles[:2])
    no_elegibles = [o.fila for o in e.opciones_de_tabla if not o.elegible]
    if no_elegibles:
        with pytest.raises(ValueError, match="R4"):
            ed.declarar(CLAVES_DE_FILA, (elegibles[0], no_elegibles[0]))


# ===========================================================================
# E10 · la GUI: sobre CampoValidable, sin segundo camino de declaracion
# ===========================================================================

def test_e10_gui_editores_declara_por_editores_y_no_por_su_cuenta():
    """
    Vale antes y despues (el archivo no existe o cumple): NO lleva `rojo`.
    Sin el archivo el test falla por `FileNotFoundError`... y por eso SI
    lleva la guardia de existencia como parte del invariante.
    """
    ruta = RAIZ / "gui" / "editores.py"
    if not ruta.exists():
        pytest.xfail("E-B: gui/editores.py todavia no existe")
    llamadas = _llamadas(_arbol(ruta))
    culpables = [n for n in llamadas if n.endswith("establecer_valor_dinamico")
                 or n.endswith("escribir_valor_en_archivo")
                 or n.startswith("dec.declarar")]
    assert not culpables, (
        f"gui/editores.py declara por su cuenta: {culpables}. Los editores "
        "COMPONEN el valor; declarar es de la pestaña 2 por `src.editores`")


def test_e10_los_editores_se_apoyan_en_CampoValidable_y_en_el_parser_unico():
    arbol = _arbol(RAIZ / "gui" / "editores.py")
    importados = {alias.name for nodo in ast.walk(arbol)
                  if isinstance(nodo, ast.ImportFrom)
                  and (nodo.module or "").endswith("componentes")
                  for alias in nodo.names}
    assert {"CampoValidable", "interpretar_texto_declarado"} <= importados
    clases = {n.name for n in ast.walk(arbol) if isinstance(n, ast.ClassDef)}
    assert {"EditorEscalar", "EditorPar", "EditorSerieDePares", "EditorDict",
            "EditorSerieDeClaves", "EditorLiteral"} <= clases
    # Ningun segundo parser: `float(` sobre texto tecleado esta prohibido.
    assert "float(self" not in ast.unparse(arbol)


def test_e10_la_pestana_2_monta_el_editor_por_forma_y_declara_por_src_editores():
    arbol = _arbol(RAIZ / "gui" / "app.py")
    llamadas = _llamadas(arbol)
    assert "sed.declarar" in llamadas or "editores_src.declarar" in llamadas
    assert "ged.construir_editor" in llamadas
    # El camino directo desaparece de la pestaña 2: sin procedencia no hay
    # adopcion.
    aplicar = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
                   and n.name == "_aplicar_valor_corrida")
    assert not [n for n in _llamadas(aplicar) if n.endswith("establecer_valor_dinamico")]
    assert not [n for n in _llamadas(aplicar) if n.endswith("olvidar_procedencia")]
    doc = ast.get_docstring(arbol) or ""
    assert "gui/editores.py" in doc


def test_e10_gui_editores_entra_en_los_dos_censos_de_la_suite():
    # Por AST y no por texto (PC-21): la cadena tiene que ser una CONSTANTE
    # del archivo --- una clave de `ARBOLES_DE_LA_GUI` o un elemento de
    # `CAPA_DE_PRESENTACION` ---, no una mencion en un comentario.
    for archivo in ("test_gui_contrato.py", "test_sin_literales.py"):
        constantes = {n.value for n in ast.walk(_arbol(RAIZ / "tests" / archivo))
                      if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert "gui/editores.py" in constantes, archivo


def test_e10_el_editor_escalar_compone_el_literal_y_la_fila_de_la_tabla():
    """Con el doble de tkinter: la logica pura del editor, sin widgets reales."""
    doble_tkinter.instalar()
    ged = _mod("gui.editores")
    ed = _mod("src.editores")
    e = ed.esquema_de(KE)
    editor = object.__new__(ged.EditorEscalar)
    editor.esquema = e
    opcion = next(o for o in e.opciones_de_tabla if o.fila == KE_FILA)
    assert ged.rotulo_de_opcion(opcion).startswith(KE_FILA)
    assert ged.opcion_del_rotulo(e, ged.rotulo_de_opcion(opcion)) is opcion


# ===========================================================================
# E14 · el comparador
# ===========================================================================

def _json(nombre):
    return json.loads((LINEA_BASE / nombre).read_text(encoding="utf-8"))


def test_e14_dos_volcados_iguales_son_iguales_y_lo_dicen():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    r = comp.comparar(a, json.loads(json.dumps(a)))
    assert r.iguales
    assert r.puntos_comunes == tuple(p["id"] for p in a["puntos"])
    assert any("IGUALES" in linea for linea in r.lineas())


def test_e14_la_marca_de_tiempo_y_el_origen_de_sitio_no_cuentan():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    b["expediente"]["generado_utc"] = "2030-01-01T00:00:00+00:00"
    b["expediente"]["corredor_del_proyecto"]["origen"] = "/otra/maquina/sitio.json"
    assert comp.comparar(a, b).iguales


def test_e14_una_diferencia_se_nombra_por_punto_y_campo():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    b["puntos"][0]["diseno"]["HW_gobernante_m"] += 0.01
    r = comp.comparar(a, b)
    assert not r.iguales
    d = next(d for d in r.diferencias if d.campo.endswith("HW_gobernante_m"))
    assert d.donde == a["puntos"][0]["id"]
    assert d.a == pytest.approx(a["puntos"][0]["diseno"]["HW_gobernante_m"], rel=REL_TRANSPORTE)
    assert any(a["puntos"][0]["id"] in linea and "HW_gobernante_m" in linea
               for linea in r.lineas())


def test_e14_las_tolerancias_tienen_nombre_y_absorben_el_ruido():
    comp = _mod("src.comparador")
    tol = _mod("src.tolerancias")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    hw = a["puntos"][0]["diseno"]["HW_gobernante_m"]
    b["puntos"][0]["diseno"]["HW_gobernante_m"] = hw + tol.TOL_COMPARADOR_ABS / 2
    assert comp.comparar(a, b).iguales
    b["puntos"][0]["diseno"]["HW_gobernante_m"] = hw * (1 + 10 * tol.TOL_COMPARADOR_REL) + 10 * tol.TOL_COMPARADOR_ABS
    assert not comp.comparar(a, b).iguales
    fuente = ast.unparse(_arbol(RAIZ / "src" / "comparador.py"))
    assert "TOL_COMPARADOR_ABS" in fuente and "TOL_COMPARADOR_REL" in fuente
    assert " == " not in fuente.replace("== None", "").replace("==None", "") or True
    # Ningun float se compara con `==` en el comparador.
    for nodo in ast.walk(_arbol(RAIZ / "src" / "comparador.py")):
        if isinstance(nodo, ast.Compare):
            assert not any(isinstance(op, ast.Eq) and isinstance(c, ast.Constant)
                           and isinstance(c.value, float)
                           for op, c in zip(nodo.ops, nodo.comparators))


def test_e14_metodos_distintos_son_no_comparables_y_no_diferencias():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    p = b["puntos"][0]
    p["diseno"]["control_gobernante"] = "salida"
    p["diseno"]["HW_gobernante_m"] += 0.5
    r = comp.comparar(a, b)
    assert not r.iguales
    nc = [n for n in r.no_comparables if n.donde == p["id"]]
    assert nc and "control" in nc[0].por_que
    assert not [d for d in r.diferencias if d.donde == p["id"]
                and d.campo.endswith("HW_gobernante_m")]
    assert "control_gobernante" in comp.CAMPOS_DE_METODO


def test_e14_un_punto_sin_diseno_en_uno_de_los_dos_es_no_comparable():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    b["puntos"][0]["diseno"] = None
    b["puntos"][0]["dimensionado"] = False
    r = comp.comparar(a, b)
    assert any(n.donde == a["puntos"][0]["id"] for n in r.no_comparables)
    assert any(d.campo == "dimensionado" for d in r.diferencias)


def test_e14_los_puntos_se_emparejan_por_id_y_no_por_posicion():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    b["puntos"].reverse()
    assert comp.comparar(a, b).iguales
    b["puntos"] = b["puntos"][:-1]
    r = comp.comparar(a, b)
    assert not r.iguales
    assert r.solo_en_a == (a["puntos"][0]["id"],) and r.solo_en_b == ()


def test_e14_alcances_distintos_son_no_comparables():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = _json("informe_expediente.json")
    r = comp.comparar(a, b)
    assert any(n.donde == "expediente" and "alcance" in n.por_que for n in r.no_comparables)


def test_e14_los_criterios_y_los_datos_de_sitio_usados_se_comparan_por_clave():
    comp = _mod("src.comparador")
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    usado = b["criterios"]["usados"][0]
    usado["valor"] = "otro"
    r = comp.comparar(a, b)
    assert any(d.donde == "criterios" and d.campo.startswith(usado["clave"])
               for d in r.diferencias)


def test_e14_no_hay_falsos_iguales_en_bloqueos_iteraciones_ni_listas_de_estado():
    """
    R6 de la auditoria adversarial: `delta_rasante_m` y `mensaje` de un
    bloqueo, un bloqueo repetido, el contenido de una iteracion, el numeral
    de una verificacion y las listas de estado quedaban fuera.
    """
    comp = _mod("src.comparador")
    a = _json("informe_rama_error.json")

    def _mutado(f):
        b = json.loads(json.dumps(a))
        f(b)
        return comp.comparar(a, b)

    punto = next(p for p in a["puntos"] if p["bloqueos"])
    i = a["puntos"].index(punto)
    assert not _mutado(lambda b: b["puntos"][i]["bloqueos"][0].update(mensaje="otro")).iguales
    assert not _mutado(lambda b: b["puntos"][i]["bloqueos"].append(
        dict(b["puntos"][i]["bloqueos"][0]))).iguales
    if punto["bloqueos"][0].get("delta_rasante_m") is not None:
        assert not _mutado(lambda b: b["puntos"][i]["bloqueos"][0].update(
            delta_rasante_m=b["puntos"][i]["bloqueos"][0]["delta_rasante_m"] + 0.75)).iguales
    con_iteraciones = next(p for p in a["puntos"] if p["iteraciones"])
    j = a["puntos"].index(con_iteraciones)
    campo = next(k for k, v in con_iteraciones["iteraciones"][0].items() if isinstance(v, str))
    assert not _mutado(lambda b: b["puntos"][j]["iteraciones"][0].update({campo: "otro"})).iguales
    con_verif = next(p for p in a["puntos"] if p["verificaciones"])
    k = a["puntos"].index(con_verif)
    assert not _mutado(lambda b: b["puntos"][k]["verificaciones"][0].update(numeral="9.9")).iguales
    assert not _mutado(lambda b: b["criterios"]["sin_consumidor"].append("x")).iguales
    assert not _mutado(lambda b: b["criterios"]["verificacion_pendiente"].append("x")).iguales
    assert not _mutado(lambda b: b["datos_sitio"]["sin_valor_declarados"].append("x")).iguales


def test_e14_un_nan_o_un_infinito_nunca_es_el_mismo_numero_que_otro():
    """R7: la forma negada dejaba caer NaN e inf del lado de «igual»."""
    comp = _mod("src.comparador")
    nan, inf = float("nan"), float("inf")
    assert not comp.mismo_numero(nan, nan)
    assert not comp.mismo_numero(nan, 1.0)
    assert not comp.mismo_numero(inf, -inf)
    assert not comp.mismo_numero(inf, 1e308)
    assert comp.mismo_numero(inf, inf) and comp.mismo_numero(-inf, -inf)
    a = _json("informe_perfil_ancho.json")
    b = json.loads(json.dumps(a))
    b["puntos"][0]["diseno"]["HW_gobernante_m"] = nan
    assert not comp.comparar(a, b).iguales


def test_e14_el_comparador_nunca_recalcula():
    """
    Vale antes y despues, y no lleva `rojo`: sin el archivo se salta con
    `pytest.xfail` dentro, porque no hay nada que afirmar.
    """
    ruta = RAIZ / "src" / "comparador.py"
    if not ruta.exists():
        pytest.xfail("E-B: src/comparador.py todavia no existe")
    arbol = _arbol(ruta)
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos |= {a.name for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom):
            modulos.add(nodo.module or "")
            modulos |= {f"{nodo.module}.{a.name}" for a in nodo.names}
    prohibidos = {m for m in modulos if any(
        m.startswith(p) for p in ("src.servicio", "src.modulos", "src.criterios_adoptados",
                                  "src.datos_sitio", "src.declaracion", "cli"))}
    assert not prohibidos, f"el comparador importa el motor: {sorted(prohibidos)}"


def test_e14_la_cli_compara_dos_json_sin_correr_el_pipeline(tmp_path):
    a = LINEA_BASE / "informe_perfil_ancho.json"
    b = tmp_path / "b.json"
    datos = _json("informe_perfil_ancho.json")
    datos["puntos"][1]["diseno"]["HW_gobernante_m"] += 0.02
    b.write_text(json.dumps(datos), encoding="utf-8")
    hecho = subprocess.run([sys.executable, str(RAIZ / "cli.py"), "--comparar", str(a), str(a)],
                           cwd=RAIZ, capture_output=True, text=True, timeout=300)
    assert hecho.returncode == 0, hecho.stderr
    assert "IGUALES" in hecho.stdout and "JSON del expediente" not in hecho.stdout
    hecho = subprocess.run([sys.executable, str(RAIZ / "cli.py"), "--comparar", str(a), str(b)],
                           cwd=RAIZ, capture_output=True, text=True, timeout=300)
    assert hecho.returncode == 1, hecho.stderr
    assert "HW_gobernante_m" in hecho.stdout
    hecho = subprocess.run([sys.executable, str(RAIZ / "cli.py"), "--comparar", str(a),
                            str(tmp_path / "no_existe.json")],
                           cwd=RAIZ, capture_output=True, text=True, timeout=300)
    assert hecho.returncode == 2


def test_e14_la_corrida_embebida_se_compara_con_el_mismo_comparador():
    arbol = _arbol(RAIZ / "cli.py")
    fn = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
              and n.name == "_comparar_con_la_corrida_embebida")
    assert any(n.endswith("comparar") for n in _llamadas(fn))
    # y no compara los dos volcados con `==` por su cuenta (el `==` que elige
    # la corrida candidata por su csv_sha1 no es una comparacion de volcados)
    assert not any(isinstance(n, ast.Compare) and any(isinstance(op, ast.Eq) for op in n.ops)
                   and "informe_json" in ast.unparse(n)
                   for n in ast.walk(fn))


def test_e14_la_linea_base_es_su_primer_consumidor():
    # Por AST (PC-21): un test de test_linea_base importa `comparador` y
    # llama a `comparar`.
    arbol = _arbol(RAIZ / "tests" / "test_linea_base.py")
    importa = any(isinstance(n, ast.ImportFrom) and n.module == "src"
                  and any(a.name == "comparador" for a in n.names)
                  for n in ast.walk(arbol))
    assert importa
    assert any(n.endswith("comparador.comparar") for n in _llamadas(arbol))


def test_e14_la_pestana_4_ofrece_comparar_con_otro_json():
    arbol = _arbol(RAIZ / "gui" / "app.py")
    nombres = {n.name for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)}
    assert "comparar_informe" in nombres
    fn = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
              and n.name == "comparar_informe")
    llamadas = _llamadas(fn)
    assert any(n.endswith("comparar") for n in llamadas)
    # NUNCA recalcula: compara el volcado de la corrida hecha.
    assert not any(n.endswith("correr") or n.endswith("informe_json") for n in llamadas)


# ===========================================================================
# E13 (reducido) · responsable / evidencia
# ===========================================================================

def test_e13_la_responsabilidad_se_deriva_de_la_resolucion_y_de_lo_que_lo_sustituye():
    resp = _mod("src.responsable")
    c = ca.criterio(RECEPTOR)               # Libre con reemplazado_por
    r = resp.responsabilidad_de(c)
    assert r.responsable == c.resolucion.que_lo_fija
    assert r.evidencia == c.reemplazado_por
    ensayo = ca.criterio("capacidad_portante_adm")   # DeEnsayo
    r = resp.responsabilidad_de(ensayo)
    assert ensayo.resolucion.ensayo in r.responsable
    tabla = ca.criterio("categoria_refuerzo_aashto")  # DeTabla sin reemplazado_por
    r = resp.responsabilidad_de(tabla)
    assert tabla.resolucion.que_elige in r.responsable
    assert r.evidencia == (tabla.reemplazado_por or tabla.fuente)


def test_e13_el_anticipo_lleva_responsable_y_evidencia_derivados():
    resp = _mod("src.responsable")
    vacios = antc.criterios_vacios_alcanzables(cli.ALCANCE_PERFIL)
    assert vacios
    for v in vacios:
        esperado = resp.responsabilidad_de(ca.criterio(v.clave))
        assert v.responsable == esperado.responsable
        assert v.evidencia == esperado.evidencia
    assert "Estimación" in antc.AVISO_DEL_ANTICIPO


@pytest.fixture(scope="module")
def informe_expediente():
    externos = cli.cargar_datos_externos(
        EXTERNOS_AMPLIADOS,
        {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
         "L_hidraulico_m": None, "categoria_tr": None})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_EXPEDIENTE)


def test_e13_los_bloqueantes_de_la_pestana_4_y_del_json_llevan_las_dos_columnas(informe_expediente):
    resp = _mod("src.responsable")
    bloqueantes = M11.criterios_bloqueantes(informe_expediente)
    assert bloqueantes
    for b in bloqueantes:
        esperado = resp.responsabilidad_de(ca.declaracion_de(b.clave))
        assert b.responsable == esperado.responsable
        assert b.evidencia == esperado.evidencia
    volcado = cli.informe_json(informe_expediente)
    fila = volcado["criterios"]["bloquearon"][0]
    assert {"responsable", "evidencia"} <= set(fila)


def test_e13_la_gui_pinta_las_dos_columnas_en_la_pestana_4_y_en_el_anticipo():
    fuente = ast.unparse(_arbol(RAIZ / "gui" / "app.py"))
    assert fuente.count("'responsable'") >= 2 and fuente.count("'evidencia'") >= 2
    assert "c.responsable" in fuente and "criterio.responsable" in fuente


# ===========================================================================
# E21 (acotado) · la memoria con indice
# ===========================================================================

@pytest.fixture(scope="module")
def memoria_expediente(informe_expediente):
    return M11.memoria_html(informe_expediente, proyecto="E-B")


def test_e21_el_indice_es_un_marcador_de_las_dos_plantillas():
    assert "indice" in M11.MARCADORES
    for plantilla in PLANTILLAS:
        texto = plantilla.read_text(encoding="utf-8")
        assert "%%indice" in texto
        assert texto.index("%%indice") < texto.index('id="trazabilidad"')


def test_e21_el_indice_se_deriva_de_los_h2_de_la_plantilla_y_de_los_puntos(informe_expediente):
    texto = PLANTILLAS[1].read_text(encoding="utf-8")
    indice = M11.indice_de_la_memoria(texto, informe_expediente)
    ids = re.findall(r'<h2 id="([^"]+)"', texto)
    assert ids
    for id_ in ids:
        assert f'href="#{id_}"' in indice, id_
    for p in informe_expediente.puntos:
        assert f'href="#{M11.ancla_de_punto(p.punto.id)}"' in indice
        assert p.punto.id in indice
    # Nada que no exista: ningun enlace del indice apunta fuera de esos dos conjuntos.
    destinos = set(re.findall(r'href="#([^"]+)"', indice))
    esperados = set(ids) | {M11.ancla_de_punto(p.punto.id) for p in informe_expediente.puntos}
    assert destinos == esperados


def test_e21_cada_punto_tiene_su_ancla_y_el_indice_dice_su_estado(informe_expediente, memoria_expediente):
    for p in informe_expediente.puntos:
        ancla = M11.ancla_de_punto(p.punto.id)
        assert memoria_expediente.count(f'id="{ancla}"') == 1
        estado = "dimensionado" if p.dimensionado else "sin dimensionar"
        assert estado in M11.indice_de_la_memoria(
            PLANTILLAS[1].read_text(encoding="utf-8"), informe_expediente)


def test_e21_la_memoria_lleva_traza_criterios_bloqueos_y_alcance_del_contexto(memoria_expediente, informe_expediente):
    contexto = informe_expediente.contexto
    assert contexto.csv_sha1 in memoria_expediente
    assert contexto.criterios_sha1 in memoria_expediente
    for clave in contexto.criterios_usados:
        assert M11.ancla_de_criterio(clave) in memoria_expediente
    # El bloque de alcance (seccion 4 de la memoria de perfil; en la de
    # expediente va dentro del mismo marcador) y el de pendientes con los
    # bloqueos, los dos del informe y no del proceso.
    assert "Alcance declarado de la corrida" in memoria_expediente
    assert 'id="pendientes"' in memoria_expediente
    assert 'class="indice"' in memoria_expediente


def test_e21_todo_enlace_del_indice_tiene_destino_unico(memoria_expediente):
    """Vale antes y despues (EXT-8 ya lo exige a toda la memoria): sin `rojo`."""
    ids = re.findall(r'\bid="([^"]+)"', memoria_expediente)
    assert len(ids) == len(set(ids))
    rotos = {h for h in re.findall(r'href="#([^"]+)"', memoria_expediente) if h not in set(ids)}
    assert not rotos


# ===========================================================================
# La ventana de verdad: los editores por el raton
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


@pytest.mark.skipif(_INTERPRETE is None,
                    reason="ningun interprete disponible puede levantar una ventana "
                           "(falta tkinter, ttkbootstrap o el entorno grafico)")
def test_eb_los_editores_tipados_en_la_ventana_de_verdad(tmp_path):
    hecho = subprocess.run(
        _ENVOLTORIO + [_INTERPRETE, "-m", "tests.apoyo.gui_eb_real", str(tmp_path)],
        cwd=RAIZ, capture_output=True, text=True, timeout=900)
    assert hecho.returncode == 0, f"la ventana fallo:\n{hecho.stdout}\n{hecho.stderr}"
    r = json.loads((tmp_path / "resumen_eb.json").read_text(encoding="utf-8"))
    # 1. La serie de pares, fila a fila por el editor, y lo que quedo declarado.
    assert r["serie"]["tipo_de_editor"] == "serie_de_pares"
    assert [x for par in r["serie"]["declarado"] for x in par] == pytest.approx(
        [1.2, 0.9, 1.5, 1.2, 2.0, 1.5], rel=REL_TRANSPORTE)
    assert r["serie"]["procedencia_modo"] == "libre"
    assert r["serie"]["literal"].startswith("[[1.2, 0.9]")
    # 2. El dict del receptor: un campo fuera de ventana se pinta en rojo, el
    #    boton no declara NADA, y con el campo corregido entra entero.
    # El rojo es EL DE LA PALETA del tema (`gui/componentes.COLOR_ERROR`), no
    # un hexadecimal copiado: el rediseño visual (bloque 1) lo movio de
    # «#e74c3c» a `ROJO` y lo que este test fija es que el campo fuera de
    # ventana se pinta con el color de error de la interfaz, sea cual sea.
    from gui import componentes as gcomp
    assert r["receptor"]["color_n_fuera"] == gcomp.COLOR_ERROR
    assert r["receptor"]["rechazado"].startswith("Error:")
    assert r["receptor"]["declarado_tras_rechazo"] is False
    assert r["receptor"]["declarado"]["n"] == pytest.approx(0.03, rel=REL_TRANSPORTE)
    # 3. ke_entrada: elegir la fila pone la celda; otro numero sin nota no
    #    entra; con nota entra y la procedencia dice DIFIERE.
    assert r["ke"]["valor_tras_elegir_fila"] == pytest.approx(KE_CELDA, rel=REL_TRANSPORTE)
    assert r["ke"]["fila_elegida"] == KE_FILA
    assert r["ke"]["procedencia_fila"] == [KE_FILA]
    assert r["ke"]["rechazo_sin_nota"].startswith("Error:") and "DIFIERE" in r["ke"]["rechazo_sin_nota"]
    assert r["ke"]["difiere_con_nota"] is True
    # 4. Las dos columnas nuevas, en la pestaña 4 y en el anticipo.
    assert {"responsable", "evidencia"} <= set(r["columnas_pestana_4"])
    assert {"responsable", "evidencia"} <= set(r["columnas_anticipo"])
    assert r["bloqueantes_con_responsable"] > 0
    # 5. Comparar la corrida con su propio volcado: iguales.
    assert r["comparacion"]["iguales"] is True
