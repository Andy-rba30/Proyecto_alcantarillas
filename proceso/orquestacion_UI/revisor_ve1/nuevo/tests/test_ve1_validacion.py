"""
tests/test_ve1_validacion.py
============================
La aceptacion de VE-1: los tres defectos que la VALIDACION EXTERNA de punta
a punta (2026-11-15) dejo confirmados por un revisor independiente, uno de
codigo y dos de documentacion.

D1 · CODIGO. `M2.siguiente_diametro` redondeaba el escalon siguiente a dos
     decimales. Con `diametros_normalizados` = {"inicio": 0.9144, "paso":
     0.1524} --la serie de 6 in que la ficha del criterio nombra como «la
     serie real», y que la puerta acepta-- el segundo escalon se evaluaba con
     1.07 m, un diametro que nadie declaro, y el tercero levantaba
     DatoInvalidoError «no pertenece a la progresion» culpando al dato `D`,
     que el usuario no escribio; el punto terminaba «no factible» en los tres
     materiales. Igual con 0.90 + 0.075 y 0.90 + 0.125. La serie declarada
     se recorre TAL CUAL, y la progresion por defecto (0.90 / 0.15) no mueve
     un byte: ni un numero impreso ni un float volcado al JSON.
D2 · DOCUMENTACION. V7 (flotacion) NO lee `NF_profundidad_m`: supone el
     conducto sumergido (fila V7 de la hoja de ruta, «Tuberia vacia, NF en su
     cota mas alta»). El contrato de entradas y el concepto de la columna
     --el texto que imprime el pre-vuelo-- decian que si. Se corrige la
     documentacion, no V7, y se dice quien la lee de verdad.
D3 · HOJA DE RUTA. La hoja de ruta dice en su §1.2 que V7 lee el NF
     (contra su propia fila V7) y rotula «Regla [N]» la doble n del
     concreto sin numeral que la sostenga. No se edita: se declara la
     discrepancia en el punto de uso, se reporta en la ficha VE1-01 y se
     deja dicho que sigue mal mientras el dueño no la corrija. La
     verificacion contra la fuente primaria, hecha con
     `python3 -m src.normativa.extraccion` sobre el Manual de Hidrologia:
     el num. 4.1.1.3.6 (pag. impresa 74, PDF 77) dice solo «n : Coeficiente
     de Manning (Ver Tabla Nº 09)»; la Tabla Nº 09 (pag. impresa 75, PDF 78)
     da MINIMO, NORMAL y MAXIMO; y en las 18 paginas donde aparece
     «rugosidad» (dos del indice) «minimo» y «maximo» solo salen como
     rotulos de esas columnas, en el «galibo minimo» de los puentes y en el
     «caudal maximo» del indice: el Manual da la tabla, no la regla de cual
     columna usar.

Escrita PRIMERO, en rojo (§1 regla 4 de la cadena): DOCE tests con
`xfail(strict=True)` fallaban por su motivo antes de tocar el codigo y la
documentacion, medidos con `--runxfail` (los seis de la serie con
DatoInvalidoError «no pertenece a la progresion», los dos de punta a punta
con 1.07 en V9 y con DisenoNoFactibleError, los dos de D2 con el texto que
atribuia el NF a V7 y los dos de las fichas con KeyError), y se liberaron al
corregir. Un caso mas de la serie (el paso de cinco decimales) se sumo
despues, por MUTACION, y lo dice en su comentario. Los otros cinco son
CUATRO GUARDIAS que valen antes y despues y un CENTINELA de la hoja de ruta,
y lo dicen en su docstring. Los
datos son DATOS DE PRUEBA: el punto P1 es el de la reproduccion minima del
validador (un cruce sintetico de Familia A), y los espesores de pared de la
serie de 6 in son los de la pared B de ASTM C 76 para 36, 42, 48 y 54 in,
declarados solo para que el escalon tenga pared; no son datos de proyecto.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

import cli
from conftest import CLAVE_ESPESOR_PARED, ESPESOR_PARED_DE_PRUEBA
from src import servicio
from src import variables_entrada as ve
from src.modelos import DatoInvalidoError, TipoMaterial
from src.modulos import M2_material as M2
from tests.apoyo.criterios import declarados

RAIZ = Path(__file__).resolve().parents[1]
CONTRATO = RAIZ / "docs" / "contrato_entradas.md"
REGISTRO = RAIZ / "docs" / "decisiones_diferidas.md"
HOJA_DE_RUTA = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
MODULOS = RAIZ / "src" / "modulos"

CONCRETO = TipoMaterial.CONCRETO_REFORZADO
TMC = TipoMaterial.TMC
HDPE = TipoMaterial.HDPE

SERIE_6_IN = {"inicio": 0.9144, "paso": 0.1524}


def _recorrido(material, serie=None) -> list:
    """
    Los escalones de la progresion de `material`, como TEXTO: `repr` del
    float, que es lo que `json.dumps` vuelca y lo que se lee en el JSON. Se
    compara asi porque lo que el defecto movia --y lo que la correccion no
    puede mover-- es exactamente esa cadena: 1.07 por 1.0668, o un
    1.7999999999999998 donde la linea base dice 1.8.
    """
    def _caminar():
        D, salida = M2.siguiente_diametro(material), []
        while D is not None:
            salida.append(repr(D))
            D = M2.siguiente_diametro(material, D)
        return salida

    if serie is None:
        return _caminar()
    with declarados({M2.CRITERIO_DIAMETROS: serie}):
        return _caminar()


# ===========================================================================
# D1 · la progresion declarada se recorre tal cual
# ===========================================================================

# La serie de 6 in de la ficha de 'diametros_normalizados', cortada por el
# tope de la norma de producto de cada material (2.70 / 2.10 / 1.50 m).
SEIS_IN_CONCRETO = ["0.9144", "1.0668", "1.2192", "1.3716", "1.524",
                    "1.6764", "1.8288", "1.9812", "2.1336", "2.286",
                    "2.4384", "2.5908"]
SEIS_IN = {
    CONCRETO: SEIS_IN_CONCRETO,
    TMC: SEIS_IN_CONCRETO[:8],         # hasta 1.9812 <= 2.10
    HDPE: SEIS_IN_CONCRETO[:4],        # hasta 1.3716 <= 1.50
}


@pytest.mark.parametrize("material", [CONCRETO, TMC, HDPE],
                         ids=lambda m: m.value)
def test_d1_la_serie_de_6_in_se_recorre_tal_cual(material):
    assert _recorrido(material, SERIE_6_IN) == SEIS_IN[material]


PASOS_DE_PRUEBA = {
    # 0.90 + 0.075: 25 escalones hasta 2.70, el tope del concreto.
    0.075: ["0.9", "0.975", "1.05", "1.125", "1.2", "1.275", "1.35",
            "1.425", "1.5", "1.575", "1.65", "1.725", "1.8", "1.875",
            "1.95", "2.025", "2.1", "2.175", "2.25", "2.325", "2.4",
            "2.475", "2.55", "2.625", "2.7"],
    # 0.90 + 0.125: 15 escalones; el siguiente, 2.775, pasa el tope.
    0.125: ["0.9", "1.025", "1.15", "1.275", "1.4", "1.525", "1.65",
            "1.775", "1.9", "2.025", "2.15", "2.275", "2.4", "2.525",
            "2.65"],
}


@pytest.mark.parametrize("paso", sorted(PASOS_DE_PRUEBA))
def test_d1_pasos_de_75_y_de_125_mm(paso):
    assert (_recorrido(CONCRETO, {"inicio": 0.90, "paso": paso})
            == PASOS_DE_PRUEBA[paso])


@pytest.mark.parametrize("serie, esperado", [
    # El caso que el revisor sumo.
    ({"inicio": 0.914, "paso": 0.152}, ["0.914", "1.066", "1.218", "1.37"]),
    # Un paso de CINCO decimales (6 1/4 in = 0.15875 m). Se sumo despues de
    # corregir, por mutacion: con un redondeo a cuatro decimales en vez del
    # escalon exacto, los casos de arriba siguen verdes y este no (1.0588).
    # Con el codigo de partida falla igual que los demas.
    ({"inicio": 0.90, "paso": 0.15875}, ["0.9", "1.05875", "1.2175",
                                          "1.37625"]),
], ids=["tres_decimales", "cinco_decimales"])
def test_d1_series_con_mas_decimales_tampoco_se_redondean(serie, esperado):
    assert _recorrido(HDPE, serie) == esperado


def test_d1_guardia_la_progresion_por_defecto_no_se_mueve():
    """
    GUARDIA (vale antes y despues). La progresion de archivo, 0.90 + 0.15,
    da exactamente los escalones que la linea base imprime y vuelca: sin el
    redondeo, `0.9 + 6 * 0.15` es 1.7999999999999998 y `0.9 + 7 * 0.15`
    1.9500000000000002, y esos floats llegarian al JSON. La correccion de D1
    no puede ser quitar el redondeo y nada mas.
    """
    por_defecto = ["0.9", "1.05", "1.2", "1.35", "1.5", "1.65", "1.8",
                   "1.95", "2.1", "2.25", "2.4", "2.55", "2.7"]
    assert _recorrido(CONCRETO) == por_defecto
    assert _recorrido(TMC) == por_defecto[:9]
    assert _recorrido(HDPE) == por_defecto[:5]
    # Y es la del archivo, no una declaracion de la suite (como texto, igual
    # que los escalones: es lo que se vuelca).
    assert {campo: repr(valor) for campo, valor in M2._progresion().items()} \
        == {"inicio": "0.9", "paso": "0.15"}


def test_d1_guardia_un_diametro_ajeno_a_la_serie_sigue_siendo_invalido():
    """
    GUARDIA (vale antes y despues). Recorrer la serie tal cual no ablanda la
    guardia de pertenencia: con la serie de 6 in, 1.07 NO es un escalon y se
    rechaza como siempre, nombrando el dato `D`. Lo que D1 corrige es que el
    programa ya no FABRICA ese 1.07 por su cuenta.
    """
    with declarados({M2.CRITERIO_DIAMETROS: SERIE_6_IN}):
        with pytest.raises(DatoInvalidoError) as exc:
            M2.siguiente_diametro(CONCRETO, 1.07)
    assert exc.value.campo == "D"
    with pytest.raises(DatoInvalidoError):
        M2.siguiente_diametro(CONCRETO, 1.00)


# --- de punta a punta --------------------------------------------------------

CABECERA = (
    "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,"
    "cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,"
    "ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,"
    "sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,"
    "cota_coronacion_canal\n")

BANDERAS_VACIAS = {"luz_m": None, "TW_m": None, "longitud_m": None,
                   "L_hidraulico_m": None, "categoria_tr": None}

# Pared B de ASTM C 76 para 36, 42, 48 y 54 in, en metros: DATOS DE PRUEBA
# para que cada escalon de la serie de 6 in tenga su fila (la clave es el
# diametro designado en milimetros, `round(D * 1000)`). La fila 1070 NO es de
# la serie y se declara A PROPOSITO, como hizo la reproduccion del validador:
# con ella el codigo de antes de VE-1 llegaba a evaluar su 1.07 y el test
# muestra la sustitucion silenciosa en vez de una fila que falta. Desde VE-1
# no la lee nadie.
PARED_6_IN_DE_PRUEBA = {914: 0.1016, 1067: 0.1143, 1070: 0.1143,
                        1219: 0.127, 1372: 0.1397}


def _correr_p1(tmp_path: Path, *, Q: float, nf: str = "") -> dict:
    """
    El punto P1 de la reproduccion minima del validador (Familia A, TW y luz
    por datos externos globales), a alcance de perfil, en proceso. Devuelve
    el volcado JSON de la corrida.
    """
    csv = tmp_path / f"puntos_{Q}_{nf or 'sin_nf'}.csv"
    csv.write_text(CABECERA + f"P1,0+100,A,{Q},50,0.005,100.0,104.0,103.85,"
                   f"10,0,9.0,99.5,,,SM,{nf},,\n", encoding="utf-8")
    externos_json = tmp_path / "externos.json"
    externos_json.write_text(json.dumps(
        {"globales": {"luz_m": 3.0, "TW_m": 0.3}}), encoding="utf-8")
    externos = cli.cargar_datos_externos(externos_json, BANDERAS_VACIAS)
    informe = servicio.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
    return cli.informe_json(informe)


def _correr_p1_con_la_serie_de_6_in(tmp_path: Path, *, Q: float) -> dict:
    pared = dict(ESPESOR_PARED_DE_PRUEBA)
    pared[CONCRETO.value] = {**pared[CONCRETO.value], **PARED_6_IN_DE_PRUEBA}
    with declarados({M2.CRITERIO_DIAMETROS: SERIE_6_IN,
                     CLAVE_ESPESOR_PARED: pared}):
        return _correr_p1(tmp_path, Q=Q)


def _verificacion(volcado: dict, codigo: str) -> dict:
    (punto,) = volcado["puntos"]
    encontradas = [v for v in punto["verificaciones"] if v["codigo"] == codigo]
    assert len(encontradas) == 1, (codigo, punto["verificaciones"])
    return encontradas[0]


def test_d1_de_punta_a_punta_el_punto_dimensiona_con_1_0668_y_no_con_1_07(tmp_path):
    """
    Con Q = 1.5 m3/s el 0.9144 no transporta el caudal y el escalon
    siguiente cumple: el punto dimensiona en el SEGUNDO escalon de la serie.
    Antes de VE-1 ese escalon era 1.07 m --el JSON lo volcaba en V9 y en el
    d50 de HEC-14-- y la pared salia de la fila 1070, que nadie declaro.
    """
    volcado = _correr_p1_con_la_serie_de_6_in(tmp_path, Q=1.5)
    (punto,) = volcado["puntos"]
    assert punto["dimensionado"], punto["bloqueos"]
    assert repr(_verificacion(volcado, "V9")["valor_obtenido"]) == "1.0668"
    assert repr(punto["proteccion_salida"]["apron_hec14"]["D_m"]) == "1.0668"
    aceptadas = [it for it in punto["iteraciones"] if it["aceptado"]]
    assert len(punto["iteraciones"]) == 2 and len(aceptadas) == 1


def test_d1_de_punta_a_punta_la_reproduccion_del_validador_dimensiona(tmp_path):
    """
    La reproduccion minima del validador, Q = 2.0 m3/s: el 1.0668 incumple
    V1 y el tercer escalon, 1.2192, cumple. Antes de VE-1 el tercero no
    llegaba a evaluarse: «no pertenece a la progresion ... (valor leido:
    1.07)» en los tres materiales y DisenoNoFactibleError.
    """
    volcado = _correr_p1_con_la_serie_de_6_in(tmp_path, Q=2.0)
    (punto,) = volcado["puntos"]
    assert punto["dimensionado"], punto["bloqueos"]
    assert repr(_verificacion(volcado, "V9")["valor_obtenido"]) == "1.2192"
    assert not any("no pertenece a la progresion" in it["motivo"]
                   for it in punto["iteraciones"])
    assert not any("DisenoNoFactibleError" in json.dumps(b)
                   for b in punto["bloqueos"])
    assert [it["incumplidas"] for it in punto["iteraciones"]] == [[], ["V1"], []]


# ===========================================================================
# D2 · V7 no lee el nivel freatico; la documentacion dice quien lo lee
# ===========================================================================

def test_d2_guardia_v7_no_lee_el_nivel_freatico(tmp_path):
    """
    GUARDIA (vale antes y despues): el HECHO que la documentacion tiene que
    describir. El mismo punto con la celda vacia, con un freatico a 10 cm
    del terreno y con uno a 10 m da la MISMA V7: supone el conducto
    sumergido sea cual sea el NF (fila V7 de la hoja de ruta, «Tuberia
    vacia, NF en su cota mas alta»; `M8.empuje_flotacion_kn_m`). Si un dia
    V7 lee el NF, este test cae y obliga a corregir el contrato y el
    concepto de la columna en el mismo cambio.
    """
    campos = ("estado", "valor_obtenido", "valor_admisible",
              "criterio_aplicado")
    v7 = {nf: _verificacion(_correr_p1(tmp_path, Q=2.0, nf=nf), "V7")
          for nf in ("", "0.10", "10.0")}
    referencia = {c: v7[""][c] for c in campos}
    for nf in ("0.10", "10.0"):
        assert {c: v7[nf][c] for c in campos} == referencia, nf


def _lectores_del_nf() -> set:
    """
    Los modulos de calculo que LEEN `NF_profundidad_m` del punto, medidos
    por AST: el atributo `punto.NF_profundidad_m` o la cadena que
    `punto.exigir(...)` recibe. Fuera M0 (que la carga) y M11 (que la
    imprime): ninguno de los dos calcula con ella.
    """
    lectores = set()
    for ruta in sorted(MODULOS.glob("*.py")):
        if ruta.stem in ("M0_carga", "M11_reporte"):
            continue
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
        for nodo in ast.walk(arbol):
            if (isinstance(nodo, ast.Attribute)
                    and nodo.attr == "NF_profundidad_m"):
                lectores.add(ruta.stem)
            if (isinstance(nodo, ast.Call) and nodo.args
                    and isinstance(nodo.args[0], ast.Constant)
                    and nodo.args[0].value == "NF_profundidad_m"):
                lectores.add(ruta.stem)
    return lectores


def test_d2_guardia_quien_lee_el_nf_es_la_fase_8_y_el_cabezal():
    """
    GUARDIA (vale antes y despues). Lo que el contrato y el concepto de la
    columna tienen que decir, medido sobre el codigo: leen el NF la Fase 8
    (la presion del agua sobre la pared del TMC y del HDPE, si el NF queda
    sobre la clave: `M8.verificar_tmc`, `M8._evaluar_hdpe`) y la Fase 9 (la
    estabilidad del cabezal), y NO M5, donde vive V7.
    """
    assert _lectores_del_nf() == {"M8_estructural", "M9_cabezal"}


def _fila_del_contrato(columna: str) -> str:
    filas = [linea for linea in CONTRATO.read_text(encoding="utf-8").split("\n")
             if linea.startswith(f"| `{columna}` |")]
    assert filas, f"el contrato no tiene fila para {columna}"
    return filas[0]


def test_d2_la_fila_del_contrato_no_atribuye_el_nf_a_v7():
    fila = _fila_del_contrato("NF_profundidad_m")
    assert "La lee V7" not in fila
    assert "V7 queda pendiente" not in fila
    # Dice lo que de verdad la lee, y que V7 no.
    assert "V7 no la lee" in fila
    assert "Fase 8" in fila and "cabezal" in fila
    # D3: la discrepancia con la hoja de ruta, declarada en el punto de uso.
    assert "VE1-01" in fila and "hoja de ruta" in fila


def test_d2_el_concepto_de_la_columna_dice_quien_la_lee():
    concepto = ve.variable("NF_profundidad_m").concepto
    assert "flotacion (V7)" not in concepto
    assert "V7 no la lee" in concepto
    assert "Fase 8" in concepto and "cabezal" in concepto


# ===========================================================================
# D3 · la hoja de ruta sigue mal, y el registro lo dice
# ===========================================================================

def _fichas() -> dict:
    texto = REGISTRO.read_text(encoding="utf-8")
    fichas, actual = {}, None
    for linea in texto.split("\n"):
        m = re.match(r"^## (VE1-\d\d) · ", linea)
        if m:
            actual = m.group(1)
            fichas[actual] = []
            continue
        if linea.startswith("## ") or linea.startswith("# "):
            actual = None
        if actual:
            fichas[actual].append(linea)
    return {k: "\n".join(v) for k, v in fichas.items()}


def test_d3_la_ficha_ve1_01_reporta_los_dos_defectos_de_la_hoja_de_ruta():
    """
    La regla de «Fuente de verdad» de CLAUDE.md, en sus tres partes: la
    discrepancia se declara en el punto de uso (el contrato, arriba), se
    reporta CONTRA la hoja de ruta y se deja dicho que sigue mal mientras no
    se corrija. Con la cita de la fuente primaria que la sostiene.
    """
    ficha = _fichas()["VE1-01"]
    for necesario in ("D1", "D2", "D3", "«la lee V7»", "Regla [N]",
                      "sigue mal", "4.1.1.3.6", "Tabla Nº 09",
                      "«n : Coeficiente de Manning (Ver Tabla Nº 09)»",
                      "2.4.3.8.2"):
        assert necesario in ficha, necesario


def test_ve1_02_lista_las_siete_decisiones_sin_tomarlas():
    ficha = _fichas()["VE1-02"]
    for letra in "abcdefg":
        assert f"({letra})" in ficha, letra
    # Cada una con el numero medido que la motiva.
    for medido in ("0.90 a 1.35", "1.13", "11.5 %", "729 mm", "770 km²",
                   "Q = 0.317"):
        assert medido in ficha, medido


def test_d3_centinela_la_hoja_de_ruta_sigue_sin_corregir():
    """
    CENTINELA, no guardia de comportamiento: VE-1 NO edita la hoja de ruta
    (es la fuente normativa del proyecto; su huella va en el encabezado de
    la memoria y en la linea base, y la corrige el dueño). Los dos textos
    defectuosos siguen ahi. EL DIA QUE EL DUEÑO LA CORRIJA ESTE TEST CAE, y
    es a proposito: hay que retirar en el mismo cambio las declaraciones de
    discrepancia del punto de uso (la fila `NF_profundidad_m` del contrato y
    el concepto de la columna) y cerrar la parte D3 de la ficha VE1-01.
    """
    hoja = HOJA_DE_RUTA.read_text(encoding="utf-8")
    assert "medido punto a punto; la lee V7)" in hoja, (
        "la §1.2 de la hoja de ruta ya no dice que V7 lee el NF: retira la "
        "declaracion de discrepancia del contrato y del concepto de la "
        "columna, y cierra D3 en la ficha VE1-01")
    assert "**Regla [N]:** **n máximo** para capacidad" in hoja, (
        "la hoja de ruta ya no rotula [N] la doble n: cierra D3 en la ficha "
        "VE1-01 y revisa la decision VE1-02 (a)")
