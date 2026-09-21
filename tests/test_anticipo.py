# -*- coding: utf-8 -*-
"""
tests/test_anticipo.py
======================
El CONTENIDO del panel «Anticipo antes de correr» (G3), probado sin pantalla:
`src/anticipo.py` produce los tres bloques y aqui se comprueba que cada uno
se DERIVA de su fuente --- no que repita una lista escrita en el test, que
seria congelar una copia ---. El molde es el de `tests/test_ayuda_entrada.py`:
donde se puede, se MUTA la fuente y se mira que el contenido la siga solo.

Lo que estos tests fijan ademas, porque es regla dura de G3:

  * el aviso fijo dice «estimación» --- el proyecto distingue estimaciones de
    medidas, y este panel esta del lado de las estimaciones ---;
  * la pareja V5/V8 del bloque 3 no es una tabla paralela:
    `cli._verificador_perfil` CONSULTA `VERIFICACIONES_DIFERIDAS_POR_ALCANCE`
    en sus dos puntos de diferimiento.

El contrato de la GUI (que el panel existe, que pinta lo que este modulo
produce y que el boton de EJECUTAR no depende de nada de esto) vive en
`tests/test_gui_contrato.py`, no aqui.
"""

import ast
import inspect
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest

from src import anticipo as antc
import cli
from src import criterios_adoptados as ca
from src.modulos import M0_carga as m0

RAIZ = Path(__file__).resolve().parents[1]
CSV_EXPEDIENTE = RAIZ / "tests" / "ejemplo_puntos.csv"
CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
CSV_INVALIDO = RAIZ / "tests" / "ejemplo_puntos_invalido.csv"


# ---------------------------------------------------------------------------
# El aviso fijo
# ---------------------------------------------------------------------------

def test_el_aviso_del_anticipo_dice_estimacion_y_remite_a_la_corrida():
    """
    La palabra «estimación» no es opcional (regla dura de G3), y el aviso
    tiene que remitir a donde vive la verdad medida: la pestana 4.
    """
    assert "Estimación" in antc.AVISO_DEL_ANTICIPO
    assert "pestaña 4" in antc.AVISO_DEL_ANTICIPO


# ---------------------------------------------------------------------------
# Bloque 1 - criterios vacios alcanzables
# ---------------------------------------------------------------------------

def test_los_vacios_alcanzables_son_interseccion_y_no_tercera_lista():
    """
    Cada fila esta en LAS DOS fuentes: sin valor (`criterios_sin_valor`, que
    ya excluye opcionales y declarados en caliente) y alcanzable por el
    alcance (`criterios_del_alcance`, que lee `Criterio.nivel`). Y el
    concepto es el del criterio, no una redaccion propia.
    """
    for alcance in (cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE):
        filas = antc.criterios_vacios_alcanzables(alcance)
        assert filas, f"a {alcance} no salio ningun vacio alcanzable"
        sin_valor = set(ca.criterios_sin_valor())
        alcanzables = set(ca.criterios_del_alcance(alcance))
        for fila in filas:
            assert fila.clave in sin_valor
            assert fila.clave in alcanzables
            assert fila.concepto == ca.criterio(fila.clave).concepto


def test_el_alcance_de_perfil_estrecha_la_lista_y_no_la_reordena():
    """
    Perfil es un subconjunto ESTRICTO de expediente (las Fases 8 y 9 estan
    llenas de pendientes de expediente), y los dos salen en el orden
    alfabetico de `criterios_sin_valor`.
    """
    perfil = [f.clave for f in
              antc.criterios_vacios_alcanzables(cli.ALCANCE_PERFIL)]
    expediente = [f.clave for f in
                  antc.criterios_vacios_alcanzables(cli.ALCANCE_EXPEDIENTE)]
    assert set(perfil) < set(expediente)
    assert perfil == sorted(perfil)
    assert expediente == sorted(expediente)


def test_los_opcionales_no_aparecen_en_el_anticipo():
    """
    Un opcional sin declarar NO es un vacio que bloquee nada: el consumidor
    aplica el valor normativo por defecto. Anunciarlo como bloqueo le diria
    al proyectista que un refinamiento que nadie tiene obligacion de declarar
    es un hueco del expediente (la razon vive en `criterios_sin_valor`).
    """
    claves = {f.clave for f in
              antc.criterios_vacios_alcanzables(cli.ALCANCE_EXPEDIENTE)}
    for opcional in ca.criterios_opcionales_sin_declarar():
        assert opcional not in claves


def test_mover_el_nivel_de_un_criterio_lo_mueve_de_lista(monkeypatch):
    """
    LA MEDIDA, como en test_ayuda_entrada: la pertenencia se DERIVA. Un vacio
    de perfil reclasificado a expediente desaparece de la lista de perfil sin
    tocar `anticipo.py` --- si no desapareciera, el modulo llevaria su propia
    tabla ---.
    """
    perfil_antes = [f.clave for f in
                    antc.criterios_vacios_alcanzables(cli.ALCANCE_PERFIL)]
    clave = perfil_antes[0]
    monkeypatch.setitem(ca.CRITERIOS, clave,
                        replace(ca.CRITERIOS[clave],
                                nivel=ca.NIVEL_EXPEDIENTE))
    perfil_despues = {f.clave for f in
                      antc.criterios_vacios_alcanzables(cli.ALCANCE_PERFIL)}
    assert clave not in perfil_despues
    assert clave in {f.clave for f in
                     antc.criterios_vacios_alcanzables(cli.ALCANCE_EXPEDIENTE)}


def test_un_criterio_que_recibe_valor_sale_del_anticipo(monkeypatch):
    """
    El bloque 1 lista VACIOS: en cuanto el criterio tiene valor deja de
    estar. Se muta el archivo en memoria (monkeypatch lo repone) porque lo
    que se prueba es la derivacion, no la guardia de declaracion --- esa
    tiene sus propios tests ---.
    """
    perfil = [f.clave for f in
              antc.criterios_vacios_alcanzables(cli.ALCANCE_PERFIL)]
    clave = perfil[0]
    monkeypatch.setitem(ca.CRITERIOS, clave,
                        replace(ca.CRITERIOS[clave], valor="tanteo"))
    assert clave not in {f.clave for f in
                         antc.criterios_vacios_alcanzables(cli.ALCANCE_PERFIL)}


# ---------------------------------------------------------------------------
# Bloque 2 - contraste de cabecera, sin ejecutar el pipeline
# ---------------------------------------------------------------------------

def test_el_contraste_del_csv_de_ejemplo_esta_completo_y_cuenta_los_vacios():
    contraste = antc.contraste_de_cabecera(CSV_EXPEDIENTE)
    assert contraste.cabecera_completa
    assert contraste.faltan == ()
    assert contraste.sobran == ()
    assert contraste.filas == 4

    por_columna = {c.columna: c for c in contraste.con_vacios}
    # Las tres del cruce de canal (C-01) y las cinco de tablero/ensayo.
    assert por_columna["Q_m3s"].vacias == 1
    assert por_columna["cota_TW"].vacias == 4
    assert por_columna["NF_profundidad_m"].vacias == 4
    # Toda columna con vacios de ESTE csv esta admitida por algun grupo, y
    # los grupos son LOS DE M0, no una copia.
    for columna in contraste.con_vacios:
        assert columna.admite_vacio
        for grupo in columna.grupos:
            assert grupo in m0.VACIOS_ADMITIDOS
            assert columna.columna in grupo.columnas


def test_el_contraste_no_valida_ni_lanza_por_una_cabecera_incompleta():
    """
    `ejemplo_puntos_invalido.csv` existe para que `cargar_puntos` LANCE
    (le falta `cota_subrasante`). El contraste, en cambio, lo DESCRIBE: una
    cabecera incompleta es contenido del anticipo, no una excepcion.
    """
    contraste = antc.contraste_de_cabecera(CSV_INVALIDO)
    assert contraste.faltan == ("cota_subrasante",)
    assert contraste.sobran == ()
    assert not contraste.cabecera_completa
    lineas = antc.lineas_del_contraste(contraste)
    assert any("cota_subrasante" in linea and "detendrá" in linea
               for linea in lineas)


def test_una_columna_desconocida_sale_como_sobrante(tmp_path):
    ruta = tmp_path / "sobrante.csv"
    cabecera = ",".join(m0.COLUMNAS) + ",columna_inventada"
    ruta.write_text(cabecera + "\n", encoding="utf-8")
    contraste = antc.contraste_de_cabecera(ruta)
    assert contraste.sobran == ("columna_inventada",)
    assert contraste.faltan == ()
    assert any("columna_inventada" in linea
               for linea in antc.lineas_del_contraste(contraste))


def test_un_vacio_en_columna_obligatoria_se_anuncia_como_no_admitido(tmp_path):
    """
    La celda vacia de una columna que NINGUN grupo admite (cota_terreno) se
    anuncia con la consecuencia real: la carga completa se detiene ahi.
    """
    ruta = tmp_path / "obligatoria_vacia.csv"
    filas = CSV_EXPEDIENTE.read_text(encoding="utf-8").splitlines()
    indice = list(m0.COLUMNAS).index("cota_terreno")
    celdas = filas[1].split(",")
    celdas[indice] = ""
    ruta.write_text("\n".join([filas[0], ",".join(celdas)]) + "\n",
                    encoding="utf-8")

    contraste = antc.contraste_de_cabecera(ruta)
    fila = next(c for c in contraste.con_vacios if c.columna == "cota_terreno")
    assert not fila.admite_vacio
    assert fila.grupos == ()
    linea = next(l for l in antc.lineas_del_contraste(contraste)
                 if l.startswith("cota_terreno"))
    assert "no admite vacío" in linea


def test_el_contraste_se_deriva_de_los_vacios_de_M0(monkeypatch):
    """
    LA MEDIDA: quitar los grupos de `VACIOS_ADMITIDOS` convierte en «no
    admitido» lo que antes lo estaba, sin tocar `anticipo.py`. Si no
    cambiara, el contraste llevaria su propia lista de vacios.
    """
    monkeypatch.setattr(m0, "VACIOS_ADMITIDOS", ())
    contraste = antc.contraste_de_cabecera(CSV_EXPEDIENTE)
    assert contraste.con_vacios, "el conteo de vacios no depende de los grupos"
    for columna in contraste.con_vacios:
        assert not columna.admite_vacio


# ---------------------------------------------------------------------------
# Bloque 3 - diferimientos del alcance, leidos de cli
# ---------------------------------------------------------------------------

def test_los_diferimientos_salen_de_los_dos_diccionarios_de_cli():
    for alcance in (cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE):
        diferido = antc.diferimientos_del_alcance(alcance)
        assert diferido.verificaciones == tuple(
            cli.VERIFICACIONES_DIFERIDAS_POR_ALCANCE[alcance])
        assert diferido.modulos == tuple(
            cli.MODULOS_DIFERIDOS_POR_ALCANCE[alcance])
    perfil = antc.diferimientos_del_alcance(cli.ALCANCE_PERFIL)
    assert perfil.difiere_algo
    assert not antc.diferimientos_del_alcance(
        cli.ALCANCE_EXPEDIENTE).difiere_algo


def test_las_lineas_del_bloque_3_nombran_todo_lo_diferido_y_nada_mas():
    perfil = antc.diferimientos_del_alcance(cli.ALCANCE_PERFIL)
    texto = " ".join(antc.lineas_de_diferimientos(perfil))
    for nombre in perfil.verificaciones + perfil.modulos:
        assert nombre in texto
    lineas_expediente = antc.lineas_de_diferimientos(
        antc.diferimientos_del_alcance(cli.ALCANCE_EXPEDIENTE))
    assert len(lineas_expediente) == 1
    assert "no difiere nada" in lineas_expediente[0]


def test_la_pareja_V5_V8_no_es_una_tabla_paralela():
    """
    `_verificador_perfil` tiene que CONSULTAR
    `VERIFICACIONES_DIFERIDAS_POR_ALCANCE` en sus dos puntos de diferimiento
    --- el hueco de V5/VC1 y el intento de V8 ---: si volviera a los
    literales, el dato que el anticipo lee podria quedarse describiendo un
    diferimiento que la corrida ya no hace (la defensa es la misma que la de
    `MODULOS_DIFERIDOS_POR_ALCANCE`, escrita alli).
    """
    # POR AST Y NO POR TEXTO (PC-21). `getsource(...).count(...)` contaba
    # tambien las menciones en comentarios --- y la funcion tiene dos
    # comentarios que nombran el dato ---, de modo que el mutante que borra
    # una CONSULTA real seguia verde. Se cuentan los nodos `Name` del cuerpo,
    # que son las lecturas que el interprete ejecuta.
    arbol = ast.parse(textwrap.dedent(inspect.getsource(cli._verificador_perfil)))
    consultas = [n for n in ast.walk(arbol) if isinstance(n, ast.Name)
                 and n.id == "VERIFICACIONES_DIFERIDAS_POR_ALCANCE"]
    assert len(consultas) >= 2, (
        "_verificador_perfil dejo de consultar el dato en sus dos puntos "
        "de diferimiento")
    assert set(cli.VERIFICACIONES_DIFERIDAS_POR_ALCANCE) == set(
        cli.MODULOS_DIFERIDOS_POR_ALCANCE), (
        "los dos diccionarios de diferimiento tienen que declarar los "
        "mismos alcances")


def test_un_alcance_desconocido_no_inventa_diferimientos():
    with pytest.raises(KeyError):
        antc.diferimientos_del_alcance("borrador")
