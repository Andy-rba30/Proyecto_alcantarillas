"""
tests/test_t0_gobernanza.py
===========================
La aceptacion de T-0 de la cadena T
(`proceso/planes_mejora/09_CADENA_PROMPTS_TESIS.md`; en `docs/planes_mejora/`
hasta T-12): gobernanza, especificacion
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
  5. Los PDF de normas se encuentran por `NORMAS_DIR` (con caida a `normas/`
     hasta T-12, que la retiro con los PDF),
     y HEC-14 y el WSDOT Hydraulics Manual son Fuente presente con edicion y
     paginacion medidas (bloque 5). Los tests que ABREN esos dos PDF llevan
     la marca `pdf` y se saltan sin PyMuPDF o sin el repositorio de normas
     enlazado: no estan en `normas/` de la app y T-0 no los copia.
  6. La copia de la cadena en `docs/planes_mejora/` no se edita sin que se
     note (bloque 6).

DESDE T-12 ESTE ARCHIVO SOLO LLEVA LO DEL ENTREGABLE (bloques 2 a 5). Los
bloques 1 (el tracker) y 6 (la copia de la cadena), y la comprobacion de
`verificar_sesion.py`, son de PROCESO: leen material que T-12 movio a
`proceso/` (INF-5.2.2) y se movieron con el, intactos, a
`proceso/tests/test_t0_gobernanza_proceso.py`, que se corre con
`python -m pytest proceso/tests`. La tabla `LO_QUE_ESCRIBIO_CADA_PROMPT`
vive alli.

Se escribio primero en rojo, con `xfail(strict=True)` de modulo --- medidos
50 xfailed y 3 XPASS antes de tocar nada: los tres que valen antes y despues
son que la Familia B sigue con `None`, que ninguna cita se apoya todavia en
las dos fuentes nuevas, y el de las filas INF-, que entonces era vacuo y gano
su `assert filas_inf` ---, y se libero al corregir (regla comun 4 de la
cadena).
"""

import ast
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

RAIZ = Path(__file__).resolve().parents[1]
HOJA_DE_RUTA = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
CONTRATO = RAIZ / "docs" / "contrato_entradas.md"
MANIFIESTO_REGISTRO = RAIZ / "docs" / "manifiesto_registro_normativo.md"



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
    ("### 2.3 Familias", "verificaciones_aceptacion"),       # familia B: VB1 (T-9)
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


def test_la_familia_B_lleva_el_conjunto_que_la_hoja_declara(hoja):
    """
    T-0 no tocaba logica: `verificaciones_aceptacion` de la Familia B quedo en
    None y la hoja lo DECLARO en vez de callarlo. T-9 lo cablea (ficha T0-03):
    la Fase 10 tiene desde entonces una verificacion que puede fallar (VB1),
    y la tupla es la frase de la v8 §2.3 --«V1 + V2 + V4 + V5 + espaciamiento
    de la Fase 10»-- con el codigo de esa verificacion.
    """
    # Desde las correcciones de T-9 (H1), con VB2: el aporte contra la
    # capacidad de la cuneta, la otra verificacion de la Fase 10.
    from src.modelos import CODIGO_VB1, CODIGO_VB2, Familia
    assert M1_clasificacion.PERFILES[Familia.B].verificaciones_aceptacion == (
        "V1", "V2", "V4", "V5", CODIGO_VB1, CODIGO_VB2)
    assert "V1 + V2 + V4 + V5 + espaciamiento de la Fase 10" in hoja


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
    # El hecho que sostenia la correccion en T-0 era que NADIE consumia el
    # criterio (`consumido_por` vacio). T-1 le dio consumidor real --la Fase
    # 1-bis-- y este renglon afirma ahora eso: lo lee `MH_hidrologia` y nadie
    # mas, y sigue sin bloquear un caudal DECLARADO (lo mide
    # tests/test_t1_hidrologia.py).
    from src import variables_entrada as ve
    assert ve.variable("homogeneidad_serie_fen").consumido_por == ("MH_hidrologia",)


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

def test_los_PDF_se_buscan_solo_en_NORMAS_DIR(tmp_path, monkeypatch):
    """
    Se llamaba `test_los_PDF_se_buscan_en_NORMAS_DIR_y_despues_en_normas`:
    T-0 dejo la caida a `normas/` de la app «mientras exista». T-12 retiro
    esos PDF (INF-5.2.3) y con ellos la caida: sin la variable no hay carpeta
    de normas y la ruta esperada nombra el enlace que falta, no una carpeta
    de este repositorio.
    """
    monkeypatch.delenv(fu.VARIABLE_NORMAS_DIR, raising=False)
    assert fu.directorios_de_normas() == ()
    sin_enlace = fu.ruta_pdf(fu.HDS5_3ED)
    assert sin_enlace == fu.RUTA_SIN_ENLACE / "hif12026.pdf"
    assert not sin_enlace.exists() and "$NORMAS_DIR" in sin_enlace.as_posix()
    assert not (RAIZ / "normas").exists()

    enlazado = tmp_path / "Normas"
    enlazado.mkdir()
    (enlazado / "hif12026.pdf").write_bytes(b"%PDF-")
    monkeypatch.setenv(fu.VARIABLE_NORMAS_DIR, str(enlazado))
    assert fu.directorios_de_normas() == (enlazado,)
    assert fu.ruta_pdf(fu.HDS5_3ED) == enlazado / "hif12026.pdf"
    # Lo que el repositorio enlazado no tiene se espera ALLI, no en la app.
    assert fu.ruta_pdf(fu.MC_HHD).parent == enlazado


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
    T-0 no añadio los dos PDF nuevos a `normas/` de la app y los censo como
    «solo en el repositorio Normas» (`SOLO_EN_EL_REPO_NORMAS`). Desde T-12
    eso vale para TODAS: la app no tiene carpeta de normas, el censo
    transitorio se retiro y la guardia de PC-23 mira solo el repositorio
    enlazado (`tests/test_ext6_registro_normativo.py`).
    """
    assert not hasattr(fu, "SOLO_EN_EL_REPO_NORMAS")
    assert not (RAIZ / "normas").exists()
    for id_ in ("HEC14", "WSDOT_HM"):
        assert Path(fu.FUENTES[id_].archivo_pdf).parent.name == "normas"


def test_hec14_la_cita_T8_y_wsdot_las_tiene_desde_t4():
    """
    T-0 dio de alta las dos fuentes sin citas; citarlas (con pagina y frase)
    era de T-4 y T-8. T-4 cito el WSDOT Hydraulics Manual --abrasion, pH,
    resistividad, velocidad--, cada cita verificada contra su pagina por
    `test_normativa_pdf`. El test se llamaba «…ninguna cita se apoya todavia
    en las dos fuentes nuevas».

    T-1 (auditoria) sumo TRES del capitulo 2 del mismo manual (hidrologia):
    la duracion minima de la lluvia y la tabla de coeficientes de
    escorrentia con su incremento por frecuencia.

    T-8 cita HEC-14 (apron, hoya de socavacion, velocidad de salida,
    Apendice D), y TODAS sus citas las firma la sesion de T-8: ninguna entra
    sin verificar contra el ejemplar.
    """
    reg = _registro.construir()
    hec14 = reg.citas_de("HEC14")
    assert hec14
    assert all(c.verificado and "T-8" in c.verificado.por for c in hec14)
    assert {"WSDOT_HM.2-6.3#TC_MINIMO", "WSDOT_HM.2-6.2#T2-2",
            "WSDOT_HM.2-6.2#FRECUENCIA"} <= {c.id for c in reg.citas_de("WSDOT_HM")}


def test_el_indice_del_registro_las_lista_como_presentes():
    texto = MANIFIESTO_REGISTRO.read_text(encoding="utf-8")
    presentes = texto.split("## 2. Fuentes que se citan y NO están")[0]
    assert "`HEC14`" in presentes and "`WSDOT_HM`" in presentes


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
