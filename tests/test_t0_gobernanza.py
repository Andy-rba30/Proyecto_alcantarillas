"""
tests/test_t0_gobernanza.py
===========================
La aceptacion de T-0 de la cadena T
(`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`): gobernanza, especificacion
y enlace al repositorio de normas. T-0 no toca formulas ni umbrales, de modo
que lo que aqui se comprueba no es un numero sino que cada cosa que T-0 dejo
ESCRITA siga atada a lo que el codigo hace:

  1. El tracker conoce los hallazgos del INFORME con prefijo `INF-`, con el
     numero de item del INFORME como ID canonico, y cada alias con que la
     cadena cita un hallazgo lleva a UNA fila (bloque 1).
  2. La hoja de ruta v8 se titula v8, su encabezado del CSV es el de
     `M0_carga.COLUMNAS`, y las claves y la gravedad de su Anexo B son las
     que el codigo tiene (bloque 2).
  3. Los docstrings que el INFORME midio como falsos dejaron de afirmar lo
     que el codigo no hace; el paso del tirante critico tiene codigo neutro
     (`F4.YC`, con `F4.YC_RECT` como alias) y cita de formula, y el paso
     «cual control gobierna» cita el numeral que lo dice (bloque 3).
  4. `docs/contrato_entradas.md` nombra TODAS las entradas de diseño que el
     codigo declara --- columnas, datos externos y [S] ---, de modo que una
     entrada nueva sin fila en el contrato pone esto en rojo (bloque 4).
  5. Los PDF de normas se encuentran por `NORMAS_DIR` con caida a `normas/`,
     y HEC-14 y el WSDOT Hydraulics Manual son Fuente presente con edicion y
     paginacion medidas (bloque 5). Los tests que ABREN esos dos PDF llevan
     la marca `pdf` y se saltan sin PyMuPDF o sin el repositorio de normas
     enlazado: no estan en `normas/` de la app y T-0 no los copia.
  6. La copia de la cadena en `docs/planes_mejora/` no se edita sin que se
     note (bloque 6).

Se escribio primero en rojo, con `xfail(strict=True)` de modulo --- medidos
50 xfailed y 3 XPASS antes de tocar nada: los tres que valen antes y despues
son que la Familia B sigue con `None`, que ninguna cita se apoya todavia en
las dos fuentes nuevas, y el de las filas INF-, que entonces era vacuo y gano
su `assert filas_inf` ---, y se libero al corregir (regla comun 4 de la
cadena).
"""

import ast
import hashlib
import re
from pathlib import Path

import pytest

from src import constantes_fisicas as CF
from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import servicio
from src.modelos import FormaSeccion, SeccionCircular, SeccionRectangular, TipoMaterial
from src.modulos import M0_carga, M1_clasificacion, M4_control, M5_verificaciones
from src.modulos import M11_reporte, MD
from src.modulos.M2_material import catalogo
from src.normativa import fuentes as fu
from src.normativa import fundamentos as fund
from src.normativa import registro as _registro
from src.normativa.esquema import PorCapitulo
from src.normativa.extraccion import (PDF_NO_DISPONIBLE, numero_de_paginas,
                                      pymupdf_disponible, sha1_de,
                                      texto_de_pagina)
from tests.apoyo import tracker

RAIZ = Path(__file__).resolve().parents[1]
HOJA_DE_RUTA = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
CONTRATO = RAIZ / "docs" / "contrato_entradas.md"
CADENA = RAIZ / "docs" / "planes_mejora" / "09_CADENA_PROMPTS_TESIS.md"
MANIFIESTO_REGISTRO = RAIZ / "docs" / "manifiesto_registro_normativo.md"



# ===========================================================================
# 1. El tracker: los hallazgos del INFORME, con ID canonico y alias
# ===========================================================================

# Cuantos items trae cada apartado del INFORME. No es un numero elegido: es
# el recuento de la lista numerada del §5.1, de las viñetas del §5.2, de las
# filas de las cuatro tablas del §3 y de los siete apartados del §4. Los dos
# de §0 son los puntos 4 y 5 de «lo que falta, en orden de gravedad», que no
# tienen fila propia en ninguna tabla y que la cadena cita (T-3: «Familia C
# no se dimensiona»).
ITEMS_DEL_INFORME = {
    "INF-5.1.": 18,
    "INF-5.2.": 7,
    "INF-3.1.": 6,
    "INF-3.2.": 9,
    "INF-3.3.": 8,
    "INF-3.4.": 7,
    "INF-4.": 7,
}
ITEMS_DE_LA_SECCION_0 = ("INF-0.4", "INF-0.5")

# (prompt que lo escribe, alias tal como lo escribe) -> ID canonico. Son las
# citas de la cadena cuyo numero NO es el del item del INFORME, mas las que
# citan una tabla entera con un rotulo entre comillas.
ALIAS_DE_LA_CADENA = {
    ("T-0", "INF-5.1.9"): "INF-5.1.10",
    ("T-10", "INF-5.1.9"): "INF-5.1.10",
    ("T-4", "INF-5.1.13"): "INF-5.1.17",
    ("T-5", "INF-5.1.5"): "INF-3.3.5",
    ("T-6", "INF-5.1.14"): "INF-5.1.18",
    ("T-7a", "INF-5.1.12"): "INF-5.1.15",
    ("T-8", "INF-5.1.11"): "INF-5.1.13",
    ("T-9", "INF-5.1.11"): "INF-5.1.12",
    ("T-1", "INF-5.2"): "INF-5.2.5",
    ("T-3", "INF-3.x"): "INF-0.4",
}

# Lo que T-0 cierra: los cuatro del punto 3 del prompt (con su numero
# canonico), el desacuerdo hoja de ruta / codigo del punto 2 y la gravedad
# con dos valores, que el punto 2 explica una vez en el Anexo B.
CERRADOS_EN_T0 = {"INF-5.1.1", "INF-5.1.2", "INF-5.1.4", "INF-5.1.10",
                  "INF-5.1.11", "INF-5.1.14"}


@pytest.fixture(scope="module")
def filas():
    return tracker.hallazgos()


@pytest.fixture(scope="module")
def filas_inf(filas):
    return {f["ID"]: f for f in filas if f["ID"].startswith("INF-")}


def _ids_esperados():
    ids = set(ITEMS_DE_LA_SECCION_0)
    for prefijo, cuantos in ITEMS_DEL_INFORME.items():
        ids |= {f"{prefijo}{k}" for k in range(1, cuantos + 1)}
    return ids


def test_el_tracker_tiene_una_fila_por_hallazgo_del_INFORME(filas, filas_inf):
    assert set(filas_inf) == _ids_esperados()
    assert len({f["ID"] for f in filas}) == len(filas), "IDs repetidos en el tracker"


def test_cada_fila_INF_lleva_severidad_cluster_prompt_y_estado(filas_inf):
    assert filas_inf, "el tracker no tiene filas INF-"
    for id_, f in filas_inf.items():
        assert f["Severidad"].strip(), id_
        assert re.fullmatch(r"C\d\d", f["Cluster"]), (id_, f["Cluster"])
        assert f["Hallazgo"].strip() and f["Ubicación (archivo:línea del informe)"].strip(), id_
        # La columna «Fase» dice que prompt lo cierra, o que ninguno lo nombra.
        assert re.search(r"T-\d", f["Fase"]) or "ningún prompt" in f["Fase"], (id_, f["Fase"])
        assert f["Estado"] in ("Abierto", "Cerrado", "N/A (sin trabajo)"), (id_, f["Estado"])


def test_T0_cierra_los_que_dice_y_deja_abiertos_los_demas(filas_inf):
    cerrados = {i for i, f in filas_inf.items() if f["Estado"] == "Cerrado"}
    assert cerrados == CERRADOS_EN_T0
    for id_ in cerrados:
        assert "T-0" in filas_inf[id_]["Commit / PR"], id_
        assert "cadena T, T-0" in filas_inf[id_]["Responsable"], id_
    # Lo que el INFORME reviso y dio por correcto no es trabajo pendiente.
    sin_trabajo = {i for i, f in filas_inf.items() if f["Estado"] == "N/A (sin trabajo)"}
    assert sin_trabajo == {"INF-3.2.3", "INF-3.3.2", "INF-3.3.6"}
    for id_ in sin_trabajo:
        assert filas_inf[id_]["Severidad"] == "OK"


@pytest.mark.parametrize("prompt,alias,canonico",
                         [(p, a, c) for (p, a), c in sorted(ALIAS_DE_LA_CADENA.items())])
def test_cada_alias_de_la_cadena_lleva_a_una_sola_fila(prompt, alias, canonico, filas_inf):
    """
    La cadena cita `INF-5.1.9` (T-0, T-10) para lo que el INFORME numera 10,
    `INF-5.1.11` para dos items distintos (T-8 y T-9), y asi. Cada alias
    queda escrito en «Vinculos cruzados» de SU fila, con el prompt que lo
    usa, y en ninguna otra con ese mismo prompt.
    """
    marca = f"{prompt} la cita como «{alias}"
    con_la_marca = [i for i, f in filas_inf.items() if marca in f["Vínculos cruzados"]]
    assert con_la_marca == [canonico], (marca, con_la_marca)


def test_la_tabla_de_equivalencias_esta_en_la_copia_de_la_cadena():
    texto = CADENA.read_text(encoding="utf-8")
    nota = texto.split(MARCA_DE_COPIA)[0]
    for (prompt, alias), canonico in ALIAS_DE_LA_CADENA.items():
        assert any(prompt in linea and alias in linea and canonico in linea
                   for linea in nota.split("\n")), (prompt, alias, canonico)


# ===========================================================================
# 2. La hoja de ruta v8 dice lo que el codigo tiene
# ===========================================================================

@pytest.fixture(scope="module")
def hoja():
    return HOJA_DE_RUTA.read_text(encoding="utf-8")


def _bloque_de_codigo_tras(texto: str, titulo: str) -> str:
    """El primer bloque ``` que sigue a un titulo de la hoja."""
    resto = texto.split(titulo, 1)[1]
    return resto.split("```", 2)[1]


def test_la_hoja_v8_se_titula_v8(hoja):
    primera = hoja.split("\n", 1)[0]
    assert primera.endswith("· v8"), primera


def test_el_encabezado_del_CSV_de_la_hoja_es_el_de_M0(hoja):
    bloque = _bloque_de_codigo_tras(hoja, "### 1.2 Encabezado del CSV")
    columnas = tuple(c.strip() for c in bloque.replace("\n", "").split(",") if c.strip())
    assert columnas == M0_carga.COLUMNAS
    assert len(columnas) == 19


def test_las_claves_de_Manning_y_la_gravedad_del_Anexo_B_son_las_del_codigo(hoja):
    bloque = _bloque_de_codigo_tras(hoja, "## Anexo B — Constantes normativas para el script")
    arbol = ast.parse(bloque.split("python\n", 1)[1])
    asignado = {}
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and isinstance(nodo.targets[0], ast.Name):
            asignado[nodo.targets[0].id] = nodo.value
    manning = ast.literal_eval(asignado["MANNING"])
    assert manning, "el Anexo B perdio la tabla de Manning"
    for clave, par in manning.items():
        assert clave in CN.MANNING, f"la hoja nombra MANNING[{clave!r}], que el codigo no tiene"
        assert tuple(par) == CN.MANNING[clave], clave
    assert {"concreto_tubo_recto", "metal_corrugado_dren_aguas_lluvias"} <= set(manning)
    # Dos gravedades, cada una con su nombre: la generica y la de Laushey.
    assert ast.literal_eval(asignado["G"]) == CF.G
    assert ast.literal_eval(asignado["G_LAUSHEY"]) == CN.G_LAUSHEY
    assert CF.G != CN.G_LAUSHEY


@pytest.mark.parametrize("donde,que", [
    ("### 1.1 Por punto crítico", "MH_hidrologia"),          # el caudal: T-1
    ("### 2.3 Familias", "verificaciones_aceptacion"),       # familia B: hoy None
    ("### 7.B Verificación final por punto", "pendiente_minima_conducto"),
    ("### 7.B Verificación final por punto", "desnivel_minimo_entrega_m"),
    ("## Fase 9 — Cabezal y aletas", "POR PUNTO"),
    ("| **V5** |", "ancho_derecho_via_m"),
])
def test_cada_enmienda_de_T0_esta_en_su_apartado_y_lleva_su_ID(hoja, donde, que):
    """La nota de correccion vive en el apartado que enmienda, no al final."""
    desde = hoja.index(donde)
    siguiente = re.search(r"\n#{2,3} ", hoja[desde + len(donde):])
    hasta = desde + len(donde) + (siguiente.start() if siguiente else len(hoja))
    if donde.startswith("|"):
        hasta = hoja.index("\n", desde)
    apartado = hoja[desde:hasta]
    assert que in apartado, (donde, que)
    assert "T-0" in apartado and "INF-" in apartado, donde


def test_la_familia_B_sigue_sin_conjunto_propio_y_la_hoja_lo_dice(hoja):
    """
    T-0 no toca logica: `verificaciones_aceptacion` de la Familia B sigue en
    None, y lo que cambia es que la hoja lo DECLARA en vez de callarlo.
    """
    from src.modelos import Familia
    assert M1_clasificacion.PERFILES[Familia.B].verificaciones_aceptacion is None


# ===========================================================================
# 3. Docstrings que decian lo que el codigo no hace, y los dos pasos de M4
# ===========================================================================

def _lo_que_afirma(docstring: str) -> str:
    """
    El docstring en una linea y SIN lo que entrecomilla con «». La casa no
    borra la frase que corrige: la deja citada («este parrafo decia «...»»)
    para que se vea que cambio y por que. Lo que aqui se comprueba es que la
    frase falsa ya no este AFIRMADA, no que no este citada.
    """
    return re.sub(r"«[^«»]*»", "«…»", " ".join(docstring.split()))


def test_M1_ya_no_dice_que_el_umbral_de_area_esta_vacio():
    modulo = _lo_que_afirma(M1_clasificacion.__doc__)
    assert "sigue vacio" not in modulo
    assert "SIN ELLA EL EJEMPLO NO CORRE" not in modulo
    funcion = _lo_que_afirma(M1_clasificacion._categoria_por_area.__doc__)
    assert "bloqueada a proposito" not in funcion
    assert "no tiene valor" not in funcion
    tr = _lo_que_afirma(M1_clasificacion.periodo_retorno_de.__doc__)
    assert "criterio pendiente y el calculo se detiene" not in tr
    # Y lo que dicen es verdad: con el valor del archivo, el area decide.
    assert ca.CRITERIOS[M1_clasificacion.CRITERIO_CATEGORIA_A].valor is not None
    puntos = M0_carga.cargar_puntos(RAIZ / "tests" / "ejemplo_puntos.csv")
    assert M1_clasificacion.periodo_retorno_de(puntos[0]).anios == 71


def test_M5_ya_no_dice_que_el_TW_de_Sec_1_3_no_esta_implementado():
    doc = _lo_que_afirma(M5_verificaciones.__doc__)
    assert "no esta implementado en ningun modulo" not in doc
    assert "ningun modulo lee esas dos columnas" not in doc
    assert "tw_seccion_1_3" in doc
    # ... y es verdad: la funcion existe y M3 la define.
    from src.modulos import M3_hidraulica
    assert callable(M3_hidraulica.tw_seccion_1_3)


def test_M4_ya_no_dice_DIFERIDO_ni_da_el_rechazo_por_fijo():
    doc = _lo_que_afirma(M4_control.__doc__)
    assert "juzga el paso F4.HO como DIFERIDO" not in doc
    assert "perfil de la lamina de agua que este script no calcula" not in doc
    assert "perfil de la lamina de agua que el script no calcula" not in doc
    assert "V1/V2 quedan pendientes" not in doc
    # El bloque de excepciones nombra lo que hoy sale por esa via.
    excepciones = doc.split("Excepciones")[1].split("Uso")[0]
    assert "hw_entrada_fuera_de_rango" in excepciones
    assert "CriterioPendienteError" in excepciones


def test_nadie_afirma_ya_que_el_criterio_FEN_bloquea_el_caudal():
    """
    INF-5.1.1: ningun modulo lee 'homogeneidad_serie_fen', y un Q vacio en la
    Familia A es `DatoFaltanteError`. Los docstrings y la ficha de la fuente
    ausente decian lo contrario.
    """
    lote = _lo_que_afirma(MD.disenar_lote.__doc__)
    assert "porque 'homogeneidad_serie_fen' esta vacio" not in lote
    umbrales = _lo_que_afirma(M11_reporte.bloque_umbrales.__doc__)
    assert "bloquea el Q" not in umbrales
    assert "bloqueado" not in fu.SERIES_SENAMHI_ANA.ausencia.que_desbloquearia
    # El hecho que sostiene la correccion, medido por el consumo declarado.
    from src import variables_entrada as ve
    assert not ve.variable("homogeneidad_serie_fen").consumido_por


def _pasos(forma: FormaSeccion):
    if forma is FormaSeccion.CIRCULAR:
        material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        seccion, Q = SeccionCircular(0.90), 0.30
    else:
        import dataclasses
        from src.modelos import ConstantesHDS5
        base = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        material = dataclasses.replace(
            base, hds5=ConstantesHDS5.desde_dict(
                CN.HDS5_INLET["cajon_concreto_aleta_45_d043"]))
        seccion, Q = SeccionRectangular(2.0, 1.5), 3.0
    r = M4_control.resolver_control(seccion, Q, 0.005, 20.0, 0.30, material)
    return r.pasos


@pytest.mark.parametrize("forma", [FormaSeccion.CIRCULAR, FormaSeccion.RECTANGULAR])
def test_el_paso_del_tirante_critico_tiene_codigo_neutro_y_cita_de_formula(forma):
    criticos = [p for p in _pasos(forma) if p.codigo == "4.2.1"]
    assert len(criticos) == 1
    p = criticos[0]
    assert p.fundamento_id == "F4.YC"
    assert "RECT" not in p.fundamento_id
    assert p.formula_cita_id == "HDS5_3ED.A.3.1#CRITICO"


def test_el_codigo_anterior_del_paso_sigue_resolviendo_como_alias():
    reg = _registro.construir()
    assert fund.ALIAS_DE_FUNDAMENTO == {"F4.YC_RECT": "F4.YC"}
    assert fund.id_vigente("F4.YC_RECT") == "F4.YC"
    assert fund.id_vigente("F4.YC") == "F4.YC"
    assert reg.fundamento("F4.YC_RECT") is reg.fundamento("F4.YC")
    # El alias no es un segundo fundamento: no aparece en la coleccion.
    assert "F4.YC_RECT" not in {f.id for f in reg.fundamentos}
    # Y `paso()` con el codigo viejo emite el vigente.
    from src.modelos import Magnitud, paso
    p = paso("F4.YC_RECT", que="x", formula="y",
             sustitucion=(), resultado=Magnitud("y_c", 1.0, "m", "z"))
    assert p.fundamento_id == "F4.YC"


def test_un_alias_no_puede_pisar_un_fundamento_ni_apuntar_a_nada():
    for viejo, vigente in fund.ALIAS_DE_FUNDAMENTO.items():
        assert viejo not in fund.FUNDAMENTOS
        assert vigente in fund.FUNDAMENTOS


def test_el_paso_cual_control_gobierna_cita_el_numeral_que_lo_dice():
    reg = _registro.construir()
    gobernante = [p for p in _pasos(FormaSeccion.CIRCULAR) if p.codigo == "4.4"]
    assert len(gobernante) == 1
    p = gobernante[0]
    assert p.formula_cita_id == "HDS5_3ED.3.3.5#GOBIERNA"
    cita = reg.cita(p.formula_cita_id)
    assert cita.numeral == "3.3.5"
    assert (cita.pagina_impresa, cita.pagina_pdf) == ("3.25", 107)
    assert "higher of the two" in cita.texto_literal.texto
    assert cita.verificado is not None
    # Las ecuaciones de CONTROL DE ENTRADA siguen citando el A.2: es su sitio.
    entrada = [p for p in _pasos(FormaSeccion.CIRCULAR) if p.codigo == "4.2"
               and p.fundamento_id == "F4.CONTROL"]
    assert entrada and entrada[0].formula_cita_id == "HDS5_3ED.A.2"


def test_la_cita_del_tirante_critico_esta_medida():
    reg = _registro.construir()
    cita = reg.cita("HDS5_3ED.A.3.1#CRITICO")
    assert (cita.pagina_impresa, cita.pagina_pdf) == ("A.3", 192)
    assert reg.fuente(cita.fuente_id).paginacion.pagina_pdf("A.3") == 192
    assert cita.verificado is not None
    assert "F4.YC" in " ".join(reg.consumidores_de_cita(cita.id))


# ===========================================================================
# 4. El contrato de entradas nombra todo lo que el codigo declara
# ===========================================================================

@pytest.fixture(scope="module")
def contrato():
    return CONTRATO.read_text(encoding="utf-8")


def _nombrados(texto: str) -> set:
    return set(re.findall(r"`([^`]+)`", texto))


def test_el_contrato_nombra_cada_columna_del_CSV(contrato):
    faltan = [c for c in M0_carga.COLUMNAS if c not in _nombrados(contrato)]
    assert not faltan, f"columnas del CSV sin fila en el contrato: {faltan}"


def test_el_contrato_nombra_cada_dato_externo(contrato):
    faltan = [c for c in servicio.CLAVES_EXTERNAS if c not in _nombrados(contrato)]
    assert not faltan, f"datos externos sin fila en el contrato: {faltan}"


def test_el_contrato_nombra_cada_dato_de_sitio_y_cada_S_pendiente_de_ensayo(contrato):
    nombrados = _nombrados(contrato)
    de_sitio = [c for c in ds.DATOS_SITIO if c not in nombrados]
    assert not de_sitio, f"datos de sitio [S] sin fila en el contrato: {de_sitio}"
    pendientes = [c for c, crit in ca.CRITERIOS.items()
                  if crit.etiqueta == "S" and c not in nombrados]
    assert not pendientes, f"[S] de criterios_adoptados sin fila: {pendientes}"


def test_el_contrato_dice_la_convencion_de_esviaje_y_su_conversion(contrato):
    plano = " ".join(contrato.split())
    assert "0° = perpendicular" in plano
    assert "esviaje_app = 90° − esviaje_expediente" in plano
    # La convencion escrita es la que el codigo aplica: a 0° el factor es 1.
    import dataclasses
    from src.modulos import M7_geometria
    punto = M0_carga.cargar_puntos(RAIZ / "tests" / "ejemplo_puntos.csv")[0]
    perpendicular = dataclasses.replace(punto, esviaje_grados=0.0)
    from src.tolerancias import TOL_UMBRAL_NORMATIVO
    assert M7_geometria.factor_esviaje(perpendicular) == pytest.approx(
        1.0, abs=TOL_UMBRAL_NORMATIVO)
    assert M7_geometria.factor_esviaje(punto) > 1.0     # 15 grados alargan


def test_el_contrato_dice_que_la_cadena_no_rellena_las_entradas(contrato):
    plano = " ".join(contrato.split()).lower()
    assert "la cadena t no las rellena" in plano
    assert "valor por defecto" in plano


# ===========================================================================
# 5. El enlace al repositorio de normas, y las dos fuentes nuevas
# ===========================================================================

def test_los_PDF_se_buscan_en_NORMAS_DIR_y_despues_en_normas(tmp_path, monkeypatch):
    del_repo = fu.DIRECTORIO_NORMAS_DEL_REPOSITORIO
    assert del_repo == RAIZ / "normas"
    monkeypatch.delenv(fu.VARIABLE_NORMAS_DIR, raising=False)
    assert fu.directorios_de_normas() == (del_repo,)
    # Sin la variable, una fuente del repositorio se resuelve en normas/.
    assert fu.ruta_pdf(fu.HDS5_3ED) == del_repo / "hif12026.pdf"

    enlazado = tmp_path / "Normas"
    enlazado.mkdir()
    (enlazado / "hif12026.pdf").write_bytes(b"%PDF-")
    monkeypatch.setenv(fu.VARIABLE_NORMAS_DIR, str(enlazado))
    assert fu.directorios_de_normas() == (enlazado, del_repo)
    # NORMAS_DIR gana cuando tiene el archivo...
    assert fu.ruta_pdf(fu.HDS5_3ED) == enlazado / "hif12026.pdf"
    # ... y lo que no tiene sigue saliendo del repositorio mientras exista.
    assert fu.ruta_pdf(fu.MC_HHD).parent == del_repo


def test_NORMAS_DIR_admite_la_raiz_del_clon_o_su_carpeta_normas(tmp_path, monkeypatch):
    """El repositorio Normas guarda los PDF en su subcarpeta `normas/`."""
    clon = tmp_path / "Normas"
    (clon / "normas").mkdir(parents=True)
    (clon / "normas" / "hec14.pdf").write_bytes(b"%PDF-")
    monkeypatch.setenv(fu.VARIABLE_NORMAS_DIR, str(clon))
    assert fu.ruta_pdf(fu.HEC14) == clon / "normas" / "hec14.pdf"


def test_un_NORMAS_DIR_que_no_existe_no_se_calla(tmp_path, monkeypatch):
    monkeypatch.setenv(fu.VARIABLE_NORMAS_DIR, str(tmp_path / "no_esta"))
    with pytest.raises(FileNotFoundError):
        fu.directorios_de_normas()


def test_una_fuente_que_no_esta_en_disco_dice_donde_se_espera(tmp_path, monkeypatch):
    vacio = tmp_path / "vacio"
    vacio.mkdir()
    monkeypatch.setenv(fu.VARIABLE_NORMAS_DIR, str(vacio))
    # Devuelve una ruta que NO existe (no lanza): quien abre decide si salta.
    if (fu.DIRECTORIO_NORMAS_DEL_REPOSITORIO / "hec14.pdf").exists():
        pytest.fail("hec14.pdf no se añade a normas/ de la app (T-12 lo retira)")
    ruta = fu.ruta_pdf(fu.HEC14)
    assert not ruta.exists() and ruta.name == "hec14.pdf"
    assert ruta.parent == vacio


def test_HEC14_y_WSDOT_son_fuente_presente_con_edicion_medida():
    assert {"HEC14", "WSDOT_HM"} <= set(fu.FUENTES)
    assert not {"HEC14", "WSDOT_HM"} & set(fu.FUENTES_AUSENTES)
    hec, wsdot = fu.FUENTES["HEC14"], fu.FUENTES["WSDOT_HM"]
    assert "FHWA-NHI-06-086" in hec.titulo and "Third Edition" in hec.edicion
    assert (hec.anio, hec.paginas_pdf) == (2006, 287)
    assert "M 23-03.12" in wsdot.edicion and "April 2026" in wsdot.edicion
    assert (wsdot.anio, wsdot.paginas_pdf) == (2026, 325)
    for f in (hec, wsdot):
        assert f.sha1 and len(f.sha1) == 40
        assert isinstance(f.paginacion, PorCapitulo)
        assert f.vigencia is not None and f.vigencia.fecha == fu.VIGENCIA_VERIFICADA_EL_T0
        assert Path(f.archivo_pdf).parent.name == "normas"
    # La paginacion medida PREDICE: el capitulo 10 de HEC-14 y la Tabla 8-4.
    assert hec.paginacion.pagina_pdf("10-1") == 202
    assert hec.paginacion.pagina_pdf("D-1") == 280
    assert wsdot.paginacion.pagina_pdf("8-27") == 242
    assert wsdot.paginacion.pagina_pdf("8-13") == 228


def test_las_dos_fuentes_nuevas_viven_solo_en_el_repositorio_de_normas():
    """
    No se añaden PDF a `normas/` de la app (T-12 los retira; INF-5.2.3): los
    dos nuevos se censan como «solo en el repositorio Normas», y la guardia
    de PC-23 los espera alli y no aqui.
    """
    assert fu.SOLO_EN_EL_REPO_NORMAS == ("HEC14", "WSDOT_HM")
    en_la_app = {p.name for p in fu.DIRECTORIO_NORMAS_DEL_REPOSITORIO.glob("*.pdf")}
    for id_ in fu.SOLO_EN_EL_REPO_NORMAS:
        assert Path(fu.FUENTES[id_].archivo_pdf).name not in en_la_app


def test_ninguna_cita_se_apoya_todavia_en_las_dos_fuentes_nuevas():
    """T-0 las da de alta; citarlas (con pagina y frase) es de T-4 y T-8."""
    reg = _registro.construir()
    assert not reg.citas_de("HEC14") and not reg.citas_de("WSDOT_HM")


def test_el_indice_del_registro_las_lista_como_presentes():
    texto = MANIFIESTO_REGISTRO.read_text(encoding="utf-8")
    presentes = texto.split("## 2. Fuentes que se citan y NO están")[0]
    assert "`HEC14`" in presentes and "`WSDOT_HM`" in presentes


def test_verificar_sesion_busca_los_PDF_por_la_misma_puerta():
    arbol = ast.parse((RAIZ / "verificar_sesion.py").read_text(encoding="utf-8"))
    atributos = {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert {"ruta_pdf", "directorios_de_normas"} <= atributos
    constantes = {n.targets[0].id: n.value for n in arbol.body
                  if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
    assert ast.literal_eval(constantes["HALLAZGOS_EN_LA_MATRIZ"]) == len(tracker.hallazgos())


def _fuente_en_disco(id_):
    f = fu.FUENTES[id_]
    ruta = fu.ruta_pdf(f)
    if not ruta.exists():
        pytest.skip(f"falta {f.archivo_pdf}: enlace el repositorio de normas "
                    f"con {fu.VARIABLE_NORMAS_DIR} (ver CLAUDE.md)")
    return f, ruta


@pytest.mark.parametrize("id_", ["HEC14", "WSDOT_HM"])
@pytest.mark.pdf
@pytest.mark.skipif(not pymupdf_disponible(), reason=PDF_NO_DISPONIBLE)
def test_el_PDF_de_cada_fuente_nueva_es_el_medido(id_):
    f, ruta = _fuente_en_disco(id_)
    assert sha1_de(ruta) == f.sha1
    assert numero_de_paginas(ruta) == f.paginas_pdf


@pytest.mark.pdf
@pytest.mark.skipif(not pymupdf_disponible(), reason=PDF_NO_DISPONIBLE)
def test_la_portada_y_la_paginacion_de_HEC14_son_las_declaradas():
    f, ruta = _fuente_en_disco("HEC14")
    portada = " ".join(texto_de_pagina(ruta, 1).split())
    assert "Publication No. FHWA-NHI-06-086" in portada and "July 2006" in portada
    assert "Hydraulic Engineering Circular No. 14, Third Edition" in portada
    for impresa, comienza in (("1-1", "CHAPTER 1: ENERGY DISSIPATOR DESIGN"),
                              ("5-1", "CHAPTER 5: ESTIMATING SCOUR AT CULVERT OUTLETS"),
                              ("10-1", "CHAPTER 10: RIPRAP BASINS AND APRONS"),
                              ("D-1", "APPENDIX D: RIPRAP APRON SIZING EQUATIONS")):
        pagina = texto_de_pagina(ruta, f.paginacion.pagina_pdf(impresa))
        lineas = [l.strip() for l in pagina.split("\n") if l.strip()]
        assert comienza in " ".join(lineas[:3]), impresa
        assert lineas[-1] == impresa, impresa


@pytest.mark.pdf
@pytest.mark.skipif(not pymupdf_disponible(), reason=PDF_NO_DISPONIBLE)
def test_la_portada_y_la_paginacion_del_WSDOT_son_las_declaradas():
    f, ruta = _fuente_en_disco("WSDOT_HM")
    portada = " ".join(texto_de_pagina(ruta, 1).split())
    assert "Hydraulics Manual" in portada and "M 23-03.12" in portada
    assert "April 2026" in portada
    tabla = " ".join(texto_de_pagina(ruta, f.paginacion.pagina_pdf("8-27")).split())
    assert "Page 8-27" in tabla and "Table 8-4 Pipe Abrasion Levels" in tabla
    assert "Velocities from 6 to 15 ft/s" in tabla
    seccion = " ".join(texto_de_pagina(ruta, f.paginacion.pagina_pdf("8-13")).split())
    assert "Page 8-13" in seccion and "8-3.3" in seccion
    assert "shall not be used for severely abrasive conditions" in seccion


# ===========================================================================
# 6. La copia de la cadena en docs/planes_mejora
# ===========================================================================

MARCA_DE_COPIA = "<!-- COPIA FIEL: desde la linea siguiente, sin editar -->\n"


def test_la_copia_de_la_cadena_no_se_edita_sin_que_se_note():
    """
    El original vive en otro repositorio y la suite no puede leerlo: lo que
    se fija es que el cuerpo copiado conserve la huella que la nota declara.
    """
    texto = CADENA.read_text(encoding="utf-8")
    assert texto.count(MARCA_DE_COPIA) == 1
    nota, cuerpo = texto.split(MARCA_DE_COPIA)
    declarada = re.search(r"sha1 del original: `([0-9a-f]{40})`", nota)
    assert declarada, "la nota del orquestador perdio la huella del original"
    assert hashlib.sha1(cuerpo.encode("utf-8")).hexdigest() == declarada.group(1)
    assert cuerpo.startswith("# Cadena de prompts T")
    for n in ("T-0", "T-1", "T-7a", "T-7b", "T-7c", "T-12"):
        assert f"### {n} · " in cuerpo, n
