"""
tests/test_ayuda_entrada.py
===========================
La ayuda de la pestana 1, comprobada donde importa: que esta DERIVADA.

Lo que este archivo persigue
----------------------------
Una tabla de columnas escrita a mano no falla el dia que se escribe: falla
seis meses despues, cuando alguien anade una columna a `PuntoCritico` y nadie
se acuerda de la ayuda. Para entonces el proyectista lee una lista de 19
columnas mientras el programa exige 20, y el error que ve es «faltan columnas
en el encabezado» sobre un archivo que llenó siguiendo la ayuda del propio
programa.

Comparar el texto de la ayuda contra un texto esperado NO cubre eso: los dos
textos se escriben el mismo dia y envejecen juntos. Lo que si lo cubre es
MOVER LA FUENTE y comprobar que la ayuda se mueve con ella, y es lo que hacen
los tres primeros tests: anaden una columna, cambian un grupo de vacios y
quitan un limite, sobre las declaraciones de verdad.

Por que se puede escribir asi
-----------------------------
Porque `src/ayuda_entrada.py` lee `m0.COLUMNAS` POR EL MODULO y no por el
valor. Con un `from modulos.M0_carga import COLUMNAS` la ayuda tendria una
foto de la tupla, la foto no se podria mover, y este archivo no existiria ---
que es la forma en que un defecto se vuelve invisible: no dejando escribir la
prueba que lo encontraria.
"""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import ayuda_entrada as ay                                        # noqa: E402
import cli                                                        # noqa: E402
import variables_entrada as ve                                    # noqa: E402
from modelos import (Familia, Libre, Poblacion,                   # noqa: E402
                     VariableDeEntrada)
from modulos import M0_carga as m0                                # noqa: E402

COLUMNA_INVENTADA = "columna_de_prueba_que_no_existe"


# ===========================================================================
# 1 - La ayuda se mueve con su fuente
# ===========================================================================

def test_una_columna_nueva_aparece_sola_en_la_ayuda(monkeypatch):
    """
    EL TEST QUE HACE QUE ESTA AYUDA NO SEA UNA TABLA PARALELA.

    Se anade una columna al encabezado y a la ficha del censo --- las dos
    fuentes de verdad --- y NO se toca `ayuda_entrada`. Si la ayuda tuviera su
    propia lista, aqui seguiria diciendo 19.
    """
    nueva = VariableDeEntrada(
        clave=COLUMNA_INVENTADA,
        concepto="Columna inventada por el test para mover el censo",
        unidad="m",
        poblacion=Poblacion.COLUMNA_CSV,
        resolucion=Libre(que_lo_fija="el test", dominio="m > 0"),
        fase="Fase 1 - Datos de entrada",
    )
    monkeypatch.setattr(m0, "COLUMNAS", m0.COLUMNAS + (COLUMNA_INVENTADA,))
    monkeypatch.setitem(ve.VARIABLES, COLUMNA_INVENTADA, nueva)

    fichas = ay.fichas_de_columnas()
    assert fichas[-1].clave == COLUMNA_INVENTADA, (
        "la columna nueva no llego a la ayuda: la lista esta escrita aparte")
    assert fichas[-1].concepto == nueva.concepto
    assert fichas[-1].dominio_declarado == "m > 0"
    assert ay.cabecera_csv().endswith("," + COLUMNA_INVENTADA), (
        "la cabecera copiable no recogio la columna nueva, y es justo la que "
        "el proyectista pega en su hoja")
    assert ay.fila_de_ejemplo().count(ay.SEPARADOR_CSV) == len(m0.COLUMNAS) - 1


def test_la_obligatoriedad_se_mueve_con_el_grupo_de_vacios(monkeypatch):
    """
    La segunda fuente: `M0_carga.VACIOS_ADMITIDOS`.

    Se le quita a la Familia C su grupo y `Q_m3s` tiene que pasar a
    obligatoria. Si la ayuda llevara escrito «puede ir vacia en Familia C»,
    seguiria diciendolo mientras la carga ya la exige --- y el proyectista
    dejaria la celda vacia por indicacion del programa.
    """
    antes = ay.ficha_de_columna("Q_m3s")
    assert not antes.obligatoria
    assert antes.familias_que_admiten_vacio == (Familia.C,)

    sin_familia_c = tuple(v for v in m0.VACIOS_ADMITIDOS
                          if v.familias != (Familia.C,))
    monkeypatch.setattr(m0, "VACIOS_ADMITIDOS", sin_familia_c)

    despues = ay.ficha_de_columna("Q_m3s")
    assert despues.obligatoria, (
        "quitado el grupo de la Familia C, `Q_m3s` sigue figurando como "
        "opcional: la ayuda no lee `VACIOS_ADMITIDOS`")
    assert despues.resumen_de_obligatoriedad() == "SI, en las tres familias"


def test_el_limite_fisico_lo_pinta_la_misma_funcion_que_la_ventana_normativa():
    """
    El dominio de `dominios.py` se pide a `ventana_normativa.dominio_mostrado`,
    que es la que usa la ventana emergente de un criterio. Dos formas de pintar
    el mismo limite en dos pantallas del mismo programa es un limite en el que
    no se puede confiar --- y ademas una de las dos acabaria rotulandolo como
    normativo, que es el error que esa funcion existe para impedir.
    """
    import ventana_normativa as vn

    f = ay.ficha_de_columna("S_cauce")
    assert f.limite_fisico == vn.dominio_mostrado("S_CAUCE_MAX")
    assert f.limite_fisico.clase == "dominio_fisico"
    assert "S_CAUCE_MAX" in f.limite_fisico.frase


# ===========================================================================
# 2 - Lo que la ayuda promete sobre el CSV
# ===========================================================================

def test_la_cabecera_es_exactamente_la_del_encabezado_que_M0_exige():
    """
    Es lo que se pega en una hoja vacia, asi que tiene que ser la MISMA linea
    que `cargar_puntos` acepta. Se comprueba contra `COLUMNAS` y ademas contra
    la primera linea del CSV de ejemplo del repositorio, que es un archivo que
    M0 carga de verdad.
    """
    assert ay.cabecera_csv() == ",".join(m0.COLUMNAS)
    real = (RAIZ / "tests" / "ejemplo_puntos_perfil.csv").read_text(
        encoding="utf-8").splitlines()[0]
    assert ay.cabecera_csv() == real, (
        "la cabecera de la ayuda no coincide con la del CSV que la suite carga")


def test_toda_columna_llega_con_concepto_y_con_procedencia():
    """
    Una fila de la ayuda sin concepto o sin «de donde sale» es una fila que no
    ayuda. No se comprueba el texto --- eso lo decide `variables_entrada` ---
    sino que EXISTA: si manana entra una columna con la ficha a medias, el
    hueco se ve aqui y no en la pantalla del proyectista.
    """
    for f in ay.fichas_de_columnas():
        assert f.concepto.strip(), f.clave
        assert f.de_donde_sale.strip(), f.clave
        assert f.unidad.strip(), f.clave


def test_las_columnas_van_en_el_orden_del_encabezado_y_no_en_otro():
    """
    El orden es el del archivo, para poder seguir la ayuda de izquierda a
    derecha mientras se mira la hoja. Alfabetico seria mas comodo de buscar y
    inutil para llenar.
    """
    assert [f.clave for f in ay.fichas_de_columnas()] == list(m0.COLUMNAS)


def test_la_ayuda_reclama_una_columna_que_no_existe():
    with pytest.raises(KeyError, match="no es columna del encabezado"):
        ay.ficha_de_columna(COLUMNA_INVENTADA)


# ===========================================================================
# 3 - Los vacios, que es la mitad que la lista de columnas no da
# ===========================================================================

def test_los_vacios_de_la_ayuda_son_los_que_la_carga_admite_de_verdad():
    """
    El contraste que importa: lo que la ayuda dice que puede ir vacio tiene que
    ser lo que `_punto_desde_fila` acepta. Se pregunta a
    `columnas_que_admiten_vacio`, que es la funcion que la CARGA consulta, no
    una lista repetida.
    """
    for familia in Familia:
        de_la_carga = m0.columnas_que_admiten_vacio(familia)
        de_la_ayuda = {f.clave for f in ay.fichas_de_columnas()
                       if familia in f.familias_que_admiten_vacio}
        assert de_la_ayuda == de_la_carga, familia


def test_la_familia_C_es_la_unica_con_un_grupo_propio_y_la_ayuda_lo_dice():
    """
    El caso que motivo esta ayuda: en un cruce de canal, `Q_m3s`, `area_ha` y
    `S_cauce` van vacias A PROPOSITO y las debe el Tablero 3.1. Un proyectista
    que no lo sepa cree que le falta un dato suyo.
    """
    grupos = ay.vacios_por_quien_lo_debe()
    de_familia_c = [g for g in grupos if g[2] == (Familia.C,)]
    assert len(de_familia_c) == 1, "la Familia C tiene un solo grupo propio"
    quien, columnas, _familias = de_familia_c[0]
    assert set(columnas) == {"Q_m3s", "area_ha", "S_cauce"}
    assert "ANA" in quien or "Junta" in quien, (
        "el grupo tiene que nombrar a quien debe el dato, que es la razon de "
        "que la celda pueda ir vacia")


def test_el_vacio_que_no_espera_a_nadie_se_distingue_de_los_que_si():
    """
    `cota_fondo_entrada` admite vacio y NO espera a ningun tablero: el proyecto
    tiene regla declarada para su ausencia. Es el mismo matiz que
    `pendientes_externos` --- que por eso no la incluye --- y la ayuda lo
    conserva en vez de meter las cinco en un saco.
    """
    grupos = {tuple(cols): quien for quien, cols, _f in ay.vacios_por_quien_lo_debe()}
    quien = grupos[("cota_fondo_entrada",)]
    assert "nadie" in quien.lower()
    assert "origen_cota_fondo_entrada" in quien

    sin_pendiente = {c for v in m0.VACIOS_ADMITIDOS if not v.marca_pendiente
                     for c in v.columnas}
    assert sin_pendiente == {"cota_fondo_entrada"}


# ===========================================================================
# 4 - La ayuda del JSON, incluida su parte pobre
# ===========================================================================

def test_el_esqueleto_del_json_se_puede_pegar_y_correr(tmp_path):
    """
    LA PROMESA QUE HAY QUE COMPROBAR, y el primer esqueleto NO la cumplia: metia
    las ocho claves con `null` de valor, que parece el «no declarado» natural y
    no lo es --- `cli._dato_externo` exige un numero ---, de modo que el archivo
    de ejemplo de la ayuda reventaba al cargarse. Un ejemplo que no carga es
    peor que no dar ninguno.
    """
    ruta = tmp_path / "externos.json"
    ruta.write_text(ay.esqueleto_json(), encoding="utf-8")
    externos = cli.cargar_datos_externos(
        ruta, {clave: None for clave in cli.CLAVES_EXTERNAS})
    assert externos.globales == {}
    assert json.loads(ay.esqueleto_json()).keys() == {"globales", "puntos"}


def test_las_claves_del_json_son_las_que_cli_admite_y_ninguna_mas():
    """
    Una clave que la ayuda anunciara y `_exige_clave` rechazara seria una
    trampa: el proyectista la escribiria y la corrida le diria «clave no
    reconocida» sobre lo que el programa acaba de recomendarle.
    """
    assert [f.clave for f in ay.fichas_de_datos_externos()] == list(
        cli.CLAVES_EXTERNAS)
    assert ay.claves_admitidas() == ", ".join(cli.CLAVES_EXTERNAS)


def test_las_familias_de_cada_clave_salen_de_cli_y_no_de_una_copia(monkeypatch):
    """
    `FAMILIAS_QUE_USAN` es la MISMA declaracion que `cli._fase_10` consulta.
    Se comprueba moviendola.
    """
    antes = {f.clave: f.familias for f in ay.fichas_de_datos_externos()}
    assert antes["L_hidraulico_m"] == (Familia.B,)

    monkeypatch.setitem(cli.FAMILIAS_QUE_USAN, "L_hidraulico_m", (Familia.A,))
    despues = {f.clave: f.familias for f in ay.fichas_de_datos_externos()}
    assert despues["L_hidraulico_m"] == (Familia.A,), (
        "la ayuda del JSON lleva su propia tabla de familias")


def test_la_ayuda_del_json_declara_de_cuales_no_tiene_ficha():
    """
    SEIS DE OCHO NO ESTAN EN EL CENSO, y la ayuda lo dice en vez de rellenarlo.

    No son columna, ni dato de sitio, ni criterio: no pertenecen a ninguna de
    las tres poblaciones de `variables_entrada`, y su descripcion vive en prosa
    en el docstring de `cli.py`. Parsear un docstring daria una ayuda que se
    rompe callada la proxima vez que alguien lo reformatee, asi que no se
    parsea: se declara el hueco.

    Este test es ademas el marcador del arreglo de fondo. El dia que esas seis
    entren en el censo, falla, y quien lo lea sabra que ya no hay hueco que
    declarar.
    """
    fichas = ay.fichas_de_datos_externos()
    con_ficha = {f.clave for f in fichas if f.en_el_censo}
    sin_ficha = {f.clave for f in fichas if not f.en_el_censo}

    assert con_ficha == {"Q_m3s", "S_cauce"}, (
        "las unicas dos con ficha son las que ademas son columna del CSV")
    assert sin_ficha == {"luz_m", "TW_m", "longitud_m", "S_conducto",
                         "L_hidraulico_m", "categoria_tr"}
    for f in fichas:
        if f.en_el_censo:
            assert f.concepto and f.unidad and f.de_donde_sale, f.clave
        else:
            assert not f.concepto and not f.unidad and not f.de_donde_sale, (
                f"'{f.clave}' no esta en el censo y aun asi trae texto: solo "
                "puede venir de haberlo inventado o de haber parseado prosa")


def test_las_dos_claves_con_ficha_dicen_lo_mismo_que_la_ayuda_del_csv():
    """
    `Q_m3s` y `S_cauce` salen en las dos pestanas, y tienen que decir lo mismo:
    son el mismo dato, entregado por dos vias --- la columna, y el JSON cuando
    el Tablero 3.1 responde ---. Dos conceptos distintos para el mismo dato en
    la misma ventana es peor que no explicarlo.
    """
    del_json = {f.clave: f for f in ay.fichas_de_datos_externos() if f.en_el_censo}
    for clave, ficha in del_json.items():
        columna = ay.ficha_de_columna(clave)
        assert ficha.concepto == columna.concepto
        assert ficha.unidad == columna.unidad
        assert ficha.de_donde_sale == columna.de_donde_sale


# ===========================================================================
# 5 - El reparto contenido / pintura
# ===========================================================================

def test_el_contenido_no_importa_tkinter():
    """
    `src/ayuda_entrada.py` se prueba sin escritorio, y eso solo es cierto
    mientras no arrastre `gui/`. Es la misma frontera que sostiene
    `src/ventana_normativa.py`.

    SE MIRA EL ARBOL Y NO EL TEXTO, y el primer intento lo miraba: buscaba la
    cadena «tkinter» en el archivo y fallaba contra el propio docstring, que
    explica por que NO se importa. Es la trampa que este repositorio ya tiene
    nombrada --- un test verde (o rojo) sobre el comentario que explica la
    regla en vez de sobre la regla ---, y aqui salio del lado ruidoso, que es
    el barato.
    """
    import ast

    arbol = ast.parse((SRC / "ayuda_entrada.py").read_text(encoding="utf-8"))
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            importados.add(nodo.module.split(".")[0])
    assert "tkinter" not in importados
    assert "gui" not in importados


def test_la_ventana_no_escribe_ninguna_columna_por_su_cuenta():
    """
    `gui/ayuda_entrada.py` PINTA. Si nombrara una columna del CSV a mano, esa
    seria la version que envejece --- y ademas la que el proyectista lee.
    """
    fuente = (RAIZ / "gui" / "ayuda_entrada.py").read_text(encoding="utf-8")
    cuerpo = "\n".join(
        linea for linea in fuente.splitlines()
        if not linea.lstrip().startswith("#"))
    # Las dos que el docstring cita como ejemplo del cruce entre las dos
    # pestanas quedan fuera del cuerpo por el filtro de comentarios; lo que se
    # persigue son las OTRAS diecisiete escritas en un widget.
    escritas = [c for c in m0.COLUMNAS
                if c not in ("Q_m3s", "S_cauce") and f'"{c}"' in cuerpo]
    assert not escritas, (
        "la ventana escribe columnas a mano: " + ", ".join(escritas))
