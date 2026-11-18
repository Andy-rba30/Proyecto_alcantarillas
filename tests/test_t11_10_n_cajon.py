"""
tests/test_t11_10_n_cajon.py
============================
T11-10 (decidido por el dueño el 2026-11-13: «abrir la forma»). El criterio
'n_manning_cajon' admite, ademas de la CLAVE de una fila de tabla, el PAR
(n_min, n_max) de la especificacion del encofrado de un marco vaciado in
situ, acotado por el num. B.3 del HDS-5 3a ed.:

    «Manning's n values for cast-in-place boxes range from 0.012 to 0.022»
    (Apendice B, num. B.3 'CONCRETE BOX CULVERT', pag. impresa B.2, PDF 204)

Lo que este archivo fija:

  1. La FICHA: forma = union (str | par_ordenado), como `k_v`; el valor de
     archivo NO cambia ('concrete_boxes').
  2. El rango del B.3 se LEE de la cita del registro (una sola
     transcripcion), y su extremo inferior es el n_min de la fila del cajon
     de la Tabla B.1 (pag. impresa B.6, PDF 208: 0.012-0.015).
  3. La PUERTA (`_verificar_criterio`, los tres caminos) rechaza con
     `ValueError` un par mal formado: invertido, con booleanos o textos, de
     otro largo, no finito o fuera del rango del B.3.
  4. El CONSUMIDOR (`M2._fila_manning_de_cajon`) usa el par en la regla de
     doble n como usaria las columnas de una fila, emite su paso con el
     fundamento del B.3, y detiene como `DatoInvalidoError` el par que
     esquive la puerta.
  5. Los editores tipados (src/editores.py) y la ventana emergente admiten la
     union sin inventar campos; un par que no es el de la fila elegida no
     PROVIENE de ella y exige nota.
  6. Punta a punta: C-01 (Familia C) por la CLI con `--declarar
     n_manning_cajon=(0.013,0.016)`.

ESCRITO EN ROJO: medido contra 5e0fa00 antes de tocar el codigo.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import cli
from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import editores as sed
from src.modelos import DatoInvalidoError, FormaSeccion, TipoMaterial
from src.modulos import M2_material as M2
from src.normativa import registro
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, declarados

CLAVE = "n_manning_cajon"
CITA_B3 = "HDS5_3ED.B.3#CAJON_IN_SITU"
TB1 = "HDS5_3ED.TB.1"
PAR = (0.013, 0.016)

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"

# La aritmetica del rango y de los pares se compara con la tolerancia de la
# doble precision: los numeros no se calculan, se leen.
ABS = 1e-12


def _marco():
    return M2.catalogo(TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.RECTANGULAR)


# ===========================================================================
# 1 · La ficha
# ===========================================================================

def test_la_forma_es_la_union_de_la_fila_y_el_par():
    c = ca.CRITERIOS[CLAVE]
    assert c.forma == (ca.FORMA_STR, ca.FORMA_PAR_ORDENADO)


def test_el_valor_de_archivo_no_cambia():
    c = ca.CRITERIOS[CLAVE]
    assert c.valor == "concrete_boxes"
    assert c.etiqueta == "C"
    assert c.resolucion.tablas == (TB1, "MC_HHD.T09")


# ===========================================================================
# 2 · El rango del B.3, leido de la cita
# ===========================================================================

def test_el_rango_del_B3_se_lee_de_la_cita_y_es_0012_0022():
    texto = registro.construir().cita(CITA_B3).texto_literal.texto
    assert "range from 0.012 to 0.022" in texto
    assert cn.MANNING_CAJON_IN_SITU_HDS5 == pytest.approx((0.012, 0.022),
                                                          abs=ABS)


def test_el_extremo_inferior_del_B3_es_el_n_min_de_la_fila_del_cajon_TB1():
    n_min_tb1, n_max_tb1 = cn.MANNING_CAJON_HDS5["concrete_boxes"]
    lo, hi = cn.MANNING_CAJON_IN_SITU_HDS5
    assert lo == pytest.approx(n_min_tb1, abs=ABS)
    assert hi > n_max_tb1           # el B.3 abre la ventana HACIA ARRIBA


# ===========================================================================
# 3 · La puerta
# ===========================================================================

@pytest.mark.parametrize("valor", [
    PAR,
    [0.013, 0.016],                 # la lista que deja el JSON de una sesion
    (0.012, 0.022),                 # los dos extremos del B.3, incluidos
    (0.015, 0.015),                 # un par degenerado sigue ordenado
    "concrete_boxes",
    "concreto_afinado",
])
def test_la_puerta_admite_la_fila_y_el_par_dentro_del_B3(valor):
    ca.verificar_declaracion(CLAVE, valor)


@pytest.mark.parametrize("valor", [
    (0.016, 0.013),                 # invertido
    (True, 0.016),                  # booleano
    (0.013, False),
    ("0.013", 0.016),               # texto
    (0.013,),                       # de otro largo
    (0.012, 0.014, 0.016),
    (0.011, 0.015),                 # bajo el B.3
    (0.013, 0.023),                 # sobre el B.3
    (0.0, 0.016),
    (-0.013, 0.016),
    (0.013, math.inf),              # no finito
    (math.nan, 0.016),
    0.013,                          # un escalar no es un par
])
def test_la_puerta_rechaza_el_par_mal_formado(valor):
    with pytest.raises(ValueError):
        ca.verificar_declaracion(CLAVE, valor)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE, valor)
    assert CLAVE not in ca.valores_dinamicos()


def test_el_rechazo_fuera_del_B3_nombra_la_cita_y_el_rango():
    with pytest.raises(ValueError) as exc:
        ca.verificar_declaracion(CLAVE, (0.013, 0.025))
    assert CITA_B3 in str(exc.value)
    assert "0.022" in str(exc.value)


# ===========================================================================
# 4 · El consumidor
# ===========================================================================

def test_el_par_es_la_doble_n_del_marco():
    with declarados({CLAVE: PAR}):
        m = _marco()
    assert (m.n_min, m.n_max) == pytest.approx(PAR, abs=ABS)


def test_el_par_en_lista_entra_como_par():
    with declarados({CLAVE: [0.013, 0.016]}):
        assert M2._fila_manning_de_cajon() == pytest.approx(PAR, abs=ABS)
        assert isinstance(M2._fila_manning_de_cajon(), tuple)


def test_el_paso_del_par_lleva_el_fundamento_del_B3():
    with declarados({CLAVE: PAR}):
        m = _marco()
    paso = m.pasos[-1]
    assert paso.fundamento_id == "F4.N_CAJON_IN_SITU"
    assert paso.formula_cita_id == CITA_B3
    assert CITA_B3 in paso.citas_textuales
    sustituidos = {s.simbolo: s.valor for s in paso.sustitucion}
    assert sustituidos["n_min"] == pytest.approx(PAR[0], abs=ABS)
    assert sustituidos["n_max"] == pytest.approx(PAR[1], abs=ABS)


def test_el_rotulo_de_la_fila_del_par_nombra_el_B3():
    with declarados({CLAVE: PAR}):
        rotulo = _marco().fila_manning
    assert "B.3" in rotulo and "encofrado" in rotulo


def test_la_fila_de_archivo_sigue_dando_el_par_de_la_TB1_invariante():
    m = _marco()
    assert (m.n_min, m.n_max) == pytest.approx((0.012, 0.015), abs=ABS)
    assert m.pasos[-1].fundamento_id == "F4.N_CAJON_TB1"


@pytest.mark.parametrize("valor", [
    (0.013, 0.025), (0.010, 0.016), (0.016, 0.013), (True, 0.016),
    ("a", "b"), (0.013,),
])
def test_el_consumidor_detiene_el_par_que_esquiva_la_puerta(valor):
    with con_valor(CLAVE, valor, motivo="se esquiva la puerta a proposito "
                   "para medir la segunda linea del consumidor"):
        with pytest.raises(DatoInvalidoError) as exc:
            M2._fila_manning_de_cajon()
    assert exc.value.campo == CLAVE


def test_el_consumidor_sigue_rechazando_una_fila_ajena_invariante():
    with declarados({CLAVE: "concrete_pipe"}):
        with pytest.raises(DatoInvalidoError):
            M2._fila_manning_de_cajon()


# ===========================================================================
# 5 · Editores tipados y ventana emergente
# ===========================================================================

def test_el_editor_es_el_de_la_union_sin_campos_inventados():
    e = sed.esquema_de(CLAVE)
    assert e.forma == (ca.FORMA_STR, ca.FORMA_PAR_ORDENADO)
    assert e.tipo_de_editor == sed.ESCALAR
    assert [c.nombre for c in e.campos] == [sed.CAMPO_UNICO]
    assert e.campos[0].tipo == sed.TIPO_LIBRE
    assert e.tabla_id == TB1


def test_el_editor_valida_el_par_con_la_misma_puerta():
    assert sed.veredicto_al_escribir(CLAVE, PAR).estado is dec.Estado.VALIDO
    assert sed.veredicto_al_escribir(
        CLAVE, (0.013, 0.025)).estado is dec.Estado.INVALIDO
    e = sed.esquema_de(CLAVE)
    assert sed.armar_valor(e, sed.descomponer_valor(e, PAR)) == PAR


def test_el_par_sin_fila_exige_nota():
    with pytest.raises(ValueError):
        sed.declarar(CLAVE, PAR)
    assert CLAVE not in ca.valores_dinamicos()
    nota = "especificacion del encofrado del marco vaciado in situ"
    procedencia = sed.declarar(CLAVE, PAR, nota=nota)
    assert ca.valores_dinamicos()[CLAVE] == PAR
    assert procedencia.nota == nota


def test_un_par_que_no_es_el_de_la_fila_no_proviene_de_ella():
    """
    La ventana emergente declara con la fila elegida y sin nota: un par que
    no es el de la fila no PROVIENE de ella (EXT-V-02, extendido al par).
    """
    with pytest.raises(ValueError) as exc:
        dec.declarar_desde_tabla(CLAVE, PAR, tabla_id=TB1,
                                 filas=("concrete_boxes",))
    assert "DIFIERE" in str(exc.value)
    assert CLAVE not in ca.valores_dinamicos()
    with pytest.raises(ValueError):
        sed.declarar(CLAVE, PAR, fila="concrete_boxes")


def test_el_par_de_la_fila_si_proviene_de_ella():
    procedencia = dec.declarar_desde_tabla(CLAVE, (0.012, 0.015),
                                           tabla_id=TB1,
                                           filas=("concrete_boxes",))
    assert procedencia.filas == ("concrete_boxes",)
    assert ca.valores_dinamicos()[CLAVE] == pytest.approx(
        (0.012, 0.015), rel=REL_TRANSPORTE)


def test_un_par_distinto_con_nota_entra_por_la_fila():
    procedencia = dec.declarar_desde_tabla(
        CLAVE, PAR, tabla_id=TB1, filas=("concrete_boxes",),
        nota="encofrado de madera cepillada: el n sube sobre el de laboratorio")
    assert procedencia.nota.startswith("encofrado")


def test_la_clave_de_la_fila_sigue_entrando_por_la_ventana_invariante():
    dec.declarar_desde_tabla(CLAVE, "concrete_boxes", tabla_id=TB1,
                             filas=("concrete_boxes",))
    assert ca.valores_dinamicos()[CLAVE] == "concrete_boxes"


def test_el_parser_de_la_gui_lee_el_par():
    componentes = pytest.importorskip("gui.componentes")
    assert componentes.interpretar_texto_declarado("(0.013, 0.016)") == PAR


# ===========================================================================
# 6 · Punta a punta: C-01 por la CLI
# ===========================================================================

# Los datos de C-01 de la guia de perfil (tests/test_t3_familia_c.py).
CORONACION_GUIA = 38.30
EXTERNOS_GUIA = {"globales": {"TW_m": 0.3, "L_hidraulico_m": 120.0},
                 "puntos": {"C-01": {"Q_m3s": 0.85, "S_cauce": 0.006,
                                     "S_conducto": 0.006,
                                     "desnivel_perfil_canal_m": 1.20}}}


def _entradas(tmp_path):
    salida = []
    for linea in CSV.read_text(encoding="utf-8").splitlines():
        if linea.startswith("C-01,"):
            assert linea.endswith(",,,"), linea
            linea = linea + f"{CORONACION_GUIA:.2f}"
        salida.append(linea)
    csv = tmp_path / "puntos.csv"
    csv.write_text("\n".join(salida) + "\n", encoding="utf-8")
    externos = tmp_path / "externos.json"
    externos.write_text(json.dumps(EXTERNOS_GUIA), encoding="utf-8")
    return csv, externos


def _c01_por_la_cli(tmp_path, *declaraciones):
    csv, externos = _entradas(tmp_path)
    destino = tmp_path / f"informe_{len(declaraciones)}.json"
    argv = [str(csv), "--luz", "2.75", "--alcance", "perfil",
            "--datos-externos", str(externos), "--json", str(destino)]
    for d in declaraciones:
        argv += ["--declarar", d]
    codigo = cli.main(argv)
    datos = json.loads(destino.read_text(encoding="utf-8"))
    punto = next(p for p in datos["puntos"] if p["id"] == "C-01")
    return codigo, punto


def test_C01_de_punta_a_punta_con_el_par_declarado_por_la_cli(tmp_path):
    _, archivo = _c01_por_la_cli(tmp_path)
    codigo, par = _c01_por_la_cli(tmp_path, "n_manning_cajon=(0.013,0.016)")
    assert codigo in (0, 1)
    assert archivo["diseno"] is not None and par["diseno"] is not None
    assert (archivo["diseno"]["n_min"], archivo["diseno"]["n_max"]) == \
        pytest.approx((0.012, 0.015), abs=ABS)
    assert (par["diseno"]["n_min"], par["diseno"]["n_max"]) == \
        pytest.approx(PAR, abs=ABS)
    # Un n_max mayor sube el tirante normal: la rama de capacidad lo lee.
    assert par["diseno"]["y_normal_m"] > archivo["diseno"]["y_normal_m"]


def test_la_cli_rechaza_el_par_fuera_del_B3(tmp_path, capsys):
    csv, externos = _entradas(tmp_path)
    codigo = cli.main([str(csv), "--luz", "2.75", "--alcance", "perfil",
                       "--datos-externos", str(externos),
                       "--json", str(tmp_path / "x.json"),
                       "--declarar", "n_manning_cajon=(0.013,0.030)"])
    assert codigo != 0
    assert "n_manning_cajon" in capsys.readouterr().err
    assert not (tmp_path / "x.json").exists()
