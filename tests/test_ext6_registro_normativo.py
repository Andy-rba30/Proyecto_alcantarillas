"""
tests/test_ext6_registro_normativo.py
=====================================
La aceptacion de EXT-6, el cluster «registro normativo» del dictamen de la
auditoria externa (EXT-N-01, EXT-N-02, EXT-N-03, EXT-N-04, PC-23, PC-26,
PC-30 y el resto de EXT-G-03). Se escribieron PRIMERO, en rojo con
`xfail(strict=True)`, con la expectativa de la fuente o del invariante como
oraculo -- nunca la salida que el codigo daba --, y se liberaron al corregir.

Lo que cada bloque acredita, y contra que:

  1. DG-2018 es una Fuente PRESENTE: sha1, 285 paginas y paginacion MEDIDAS
     (284 de las 285 paginas confirman el desfase +1; la PDF 1 es la
     caratula sin numero), con la RD que la aprueba verificada y sus tres
     citas del 304.07 --el requisito juridico [N] de V5-- mas la Tabla
     304.09 transcrita entera.
  2. La guardia que faltaba (PC-23): todo PDF de `normas/` es una Fuente
     presente o esta censado en `PRESENTES_SIN_REGISTRAR` con motivo y sha1.
     T17 solo vigilaba el sentido inverso.
  3. El RNGIV que el DG-2018 §304.07.01 remite, y las dos normas de cajon
     prefabricado que AASHTO LRFD nombra, entran al censo de AUSENTES.
  4. Las citas de alcance de las tres normas de producto (M 170M, M 36, A760)
     y las de E.060 11.10 que EXT-7 necesita.
  5. La norma de producto va por (material, forma): un marco vaciado in situ
     no lleva la norma de un tubo (EXT-N-03).
  6. La eleccion de edicion se parte en fuente legal y fuentes tecnicas
     (EXT-N-01, PC-26), y la vigencia deja de ser una marca en prosa.
  7. Los textos que la memoria imprime dicen lo que el registro acredita:
     179 y no 178 (PC-30), «una geometria con n_max y dos velocidades», la
     columna «TR de diseño» de la tabla de la v8 y no de la Tabla Nº 02, y
     las dos bases de la friccion (47.7 % sobre el termino, 9.6 % sobre H).
"""

from pathlib import Path

import pytest

from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src.modelos import FormaSeccion, TipoMaterial
from src.normativa import citas as ci
from src.normativa import discrepancias as di
from src.normativa import fuentes as fu
from src.normativa import fundamentos as F
from src.normativa import registro as _registro
from src.normativa.esquema import Caracter, Corrida, ErrorDeRegistro
from src.normativa.extraccion import sha1_de
from src.tolerancias import TOL_UMBRAL_NORMATIVO

RAIZ = Path(__file__).resolve().parents[1]

NORMAS = RAIZ / "normas"


@pytest.fixture(scope="module")
def reg():
    return _registro.construir()


# ===========================================================================
# 1. DG-2018 como Fuente presente (EXT-N-02, EXT-N-04)
# ===========================================================================

def test_dg2018_es_una_fuente_presente_medida():
    f = fu.FUENTES["DG2018"]
    assert "DG2018" not in fu.FUENTES_AUSENTES
    assert not f.ausente
    assert f.sha1 == "96ea04423a7e0e7fc44b5cd5d8824d6166a8e816"
    assert f.paginas_pdf == 285
    # MEDIDO, no supuesto: 284 de las 285 paginas imprimen «Página n-1»; la
    # PDF 1 es la caratula y no imprime numero. La PDF 199 imprime 198.
    assert f.paginacion == Corrida(desfase=1)
    assert f.paginacion.pagina_pdf("198") == 199
    assert f.texto_extraible
    assert f.resolucion == "RD 03-2018-MTC/14"
    assert f.vigencia.estado is fu.EstadoDeVigencia.CONFIRMADA
    assert f.vigencia.acto_aprobatorio == "RD 03-2018-MTC/14"


def test_las_tres_citas_del_304_07_estan_en_sus_paginas(reg):
    generalidades = reg.cita("DG2018.304.07.01")
    assert generalidades.pagina_impresa == "198" and generalidades.pagina_pdf == 199
    assert "034-2008-MTC" in generalidades.texto_literal.texto
    assert generalidades.caracter is Caracter.DEFINICION

    ancho = reg.cita("DG2018.304.07.02")
    assert ancho.pagina_impresa == "198" and ancho.pagina_pdf == 199
    assert "anchos mínimos" in ancho.texto_literal.texto
    assert ancho.caracter is Caracter.EXIGENCIA

    incremento = reg.cita("DG2018.304.07.02#INCREMENTO")
    assert incremento.pagina_impresa == "199" and incremento.pagina_pdf == 200
    assert "5.00 m" in incremento.texto_literal.texto
    assert incremento.caracter is Caracter.EXIGENCIA

    # La viñeta del drenaje es cita propia: la pagina separa los cuatro casos
    # con un glifo que la capa de texto conserva y una sola cadena no los une.
    drenaje = reg.cita("DG2018.304.07.02#INCREMENTO_DRENAJE")
    assert drenaje.pagina_pdf == 200
    assert drenaje.texto_literal.texto == "Del borde más alejado de las obras de drenaje"
    assert drenaje.caracter is Caracter.EXIGENCIA
    assert "obras de drenaje" in reg.textos_literales() or any(
        "obras de drenaje" in t for t in reg.textos_literales())


def test_la_tabla_304_09_esta_transcrita_entera_y_es_el_piso_del_derecho_de_via(reg):
    t = reg.tabla("DG2018.T304.09")
    assert t.titulo_literal == "Anchos mínimos de Derecho de Vía"
    filas = {t.clave_corta(f): f.valores["ancho_min"].minimo for f in t.filas}
    assert filas == pytest.approx({
        "autopista_primera_clase": 40.0,
        "autopista_segunda_clase": 30.0,
        "carretera_primera_clase": 25.0,
        "carretera_segunda_clase": 20.0,
        "carretera_tercera_clase": 16.0,
    }, abs=TOL_UMBRAL_NORMATIVO)
    # La vista de calculo se DERIVA de la tabla, no se copia.
    assert CN.ANCHO_MIN_DERECHO_VIA_M == pytest.approx(filas, abs=TOL_UMBRAL_NORMATIVO)
    assert CN.INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M == pytest.approx(5.0, abs=TOL_UMBRAL_NORMATIVO)
    # Piso [N], SIN consumidor todavia: V5 se detiene antes, en el dato de
    # sitio `ancho_derecho_via_m`, y la clase de via del corredor esta vacia.
    # La tabla lo dice fila por fila en vez de fingir un consumidor.
    from src.normativa.esquema import NoUsada
    assert all(isinstance(f.uso, NoUsada) for f in t.filas)


def test_los_tres_textos_que_mentian_sobre_el_dg2018_ya_no_mienten():
    """
    EXT-N-02: «ninguna de las dos esta en normas/» (SIN_FUNDAMENTO F5.V5),
    «el DG-2018 no esta en normas/ y no se puede citar» (talud_terraplen) y
    «Sec. 4.2 y el DG-2018 exigen la condicion» (remanso_derecho_via): el
    304.07 no enuncia condicion hidraulica alguna.
    """
    v5 = {id_: (por_que, que) for id_, por_que, que in F.SIN_FUNDAMENTO}["F5.V5"]
    assert "ninguna de las dos esta" not in v5[0]
    assert "304.07" in v5[0]
    assert "Ley 29338" in v5[0]

    talud = ca.CRITERIOS["talud_terraplen"]
    assert "no esta en normas/" not in talud.justificacion
    assert "no esta en normas/" not in talud.resolucion.que_lo_fija
    assert "304.10" in talud.fuente and "Tabla 304.11" in talud.fuente
    assert talud.valor == pytest.approx(2.0, abs=TOL_UMBRAL_NORMATIVO)
    assert talud.sensibilidad == pytest.approx((1.5, 2.0), abs=TOL_UMBRAL_NORMATIVO)

    remanso = ca.CRITERIOS["remanso_derecho_via"]
    assert "exigen la condicion" not in remanso.justificacion
    assert "304.07" in remanso.justificacion
    assert "PENDIENTE" in remanso.fuente

    clase = __import__("src.datos_sitio", fromlist=["DATOS_SITIO"]).DATOS_SITIO["clase_de_via"]
    assert "AUSENTE" not in clase.fuente
    assert "FUENTES_AUSENTES" not in clase.fuente


# ===========================================================================
# 2. La guardia «PDF presente sin Fuente» (PC-23)
# ===========================================================================

def _pdf_de(fuente) -> Path:
    return RAIZ / fuente.archivo_pdf


def test_todo_pdf_de_normas_es_fuente_presente_o_esta_censado():
    """
    T17 vigila que una fuente AUSENTE no tenga PDF. Esta vigila el sentido
    inverso, que no tenia guardia: un PDF que llega a `normas/` y el registro
    no conoce es invisible, y asi estuvieron cuatro dias DG-2018, el Manual
    de Seguridad Vial y el de Dispositivos (EXT-N-02).
    """
    registrados = {_pdf_de(f).name for f in fu.FUENTES.values()}
    censados = {Path(p.archivo_pdf).name for p in fu.PRESENTES_SIN_REGISTRAR.values()}
    en_disco = {p.name for p in NORMAS.glob("*.pdf")}
    assert not (registrados & censados), "un PDF no puede estar en los dos censos"
    huerfanos = en_disco - registrados - censados
    assert not huerfanos, (
        f"PDF en normas/ que el registro no conoce: {sorted(huerfanos)}. O "
        "entra como Fuente presente (sha1, paginas y paginacion medidos, "
        "como N1 y N2) o se censa en PRESENTES_SIN_REGISTRAR con el motivo")
    fantasmas = (registrados | censados) - en_disco
    assert not fantasmas, f"el registro declara PDF que no estan: {sorted(fantasmas)}"


def test_el_censo_de_presentes_sin_registrar_tiene_motivo_y_sha1_medido():
    assert set(fu.PRESENTES_SIN_REGISTRAR) == {"MSV_2017", "MDCTA_2016"}
    for p in fu.PRESENTES_SIN_REGISTRAR.values():
        assert p.por_que_no_se_registra.strip()
        assert p.que_lo_registraria.strip()
        assert p.sha1 == sha1_de(RAIZ / p.archivo_pdf), p.id
    assert fu.PRESENTES_SIN_REGISTRAR["MSV_2017"].paginas_pdf == 461
    assert fu.PRESENTES_SIN_REGISTRAR["MDCTA_2016"].paginas_pdf == 532
    assert "016-2016-MTC/14" in fu.PRESENTES_SIN_REGISTRAR["MDCTA_2016"].resolucion


# ===========================================================================
# 3. Los ausentes nuevos: RNGIV, M 259, M 273
# ===========================================================================

def test_el_rngiv_entra_como_ausente_y_no_vuelve_el_binario_borrado():
    """
    El DG-2018 §304.07.01 remite al Reglamento Nacional de Gestion de
    Infraestructura Vial (DS 034-2008-MTC). El archivo que el dueño borro en
    5196dd2 NO era ese decreto: era la publicacion de El Peruano del
    10-02-2006 (12 paginas, sha1 6f6b473c...), anterior al DS de 2008 y con
    otra numeracion de articulos. No se restaura: se censa lo que falta.
    """
    r = fu.FUENTES_AUSENTES["RNGIV"]
    assert "034-2008-MTC" in r.titulo or "034-2008-MTC" in r.edicion
    assert "5196dd2" in r.nota and "2006" in r.nota
    assert "304.07.01" in r.ausencia.por_que_se_cita
    assert not (NORMAS / "Reglamento Nacional de Gestion de Infraestructura Vial.pdf").exists()


def test_las_normas_de_cajon_prefabricado_estan_censadas_como_ausentes():
    for id_ in ("AASHTO_M259", "AASHTO_M273"):
        f = fu.FUENTES_AUSENTES[id_]
        assert "12.4.2.4" in f.ausencia.por_que_se_cita or "12.11.1" in f.ausencia.por_que_se_cita
        assert "in situ" in f.ausencia.que_desbloquearia or "prefabricado" in f.ausencia.que_desbloquearia


# ===========================================================================
# 4. Citas nuevas: E.060 11.10, alcance de M 170M / M 36 / A760, LRFD 12
# ===========================================================================

@pytest.mark.parametrize("cita_id, pagina_pdf, fragmento", [
    ("E060.11.10.1", 103, "perpendiculares al plano del muro"),
    ("E060.11.10.2", 103, "horizontales en el plano del muro"),
    ("E060.11.10.10.2", 104, "no debe ser menor que 0,0025"),
    ("E060.11.10.10.3", 104, "refuerzo vertical para cortante"),
])
def test_las_citas_de_e060_11_10_estan_en_las_pdf_103_y_104(reg, cita_id, pagina_pdf, fragmento):
    c = reg.cita(cita_id)
    assert c.pagina_pdf == pagina_pdf and c.pagina_impresa == str(pagina_pdf)
    assert fragmento in c.texto_literal.texto
    assert c.caracter is Caracter.EXIGENCIA


@pytest.mark.parametrize("cita_id, pagina_pdf, fragmento", [
    ("AASHTO_M170M.1.1", 1, "storm water, and for the construction of culverts"),
    ("AASHTO_M170M.1.1#NOTA1", 1, "manufacturing and purchase specification only"),
    ("AASHTO_M36.1.1", 2, "storm water drainage, underdrains, the construction of culverts"),
    ("ASTM_A760.1.1", 1, "drenaje de aguas pluviales"),
])
def test_las_citas_de_alcance_de_las_normas_de_producto_se_leyeron_por_imagen(
        reg, cita_id, pagina_pdf, fragmento):
    from src.normativa.esquema import MetodoDeVerificacion
    c = reg.cita(cita_id)
    assert c.pagina_pdf == pagina_pdf
    assert fragmento in c.texto_literal.texto
    assert c.caracter is Caracter.DEFINICION
    assert c.verificado is not None
    assert c.verificado.metodo is MetodoDeVerificacion.IMAGEN


def test_las_dos_citas_de_lrfd_que_anclan_el_marco_in_situ(reg):
    c = reg.cita("AASHTO_LRFD_9.12.4.2.4")
    assert c.pagina_impresa == "12-8" and c.pagina_pdf == 1646
    assert "M 259" in c.texto_literal.texto and "M 273" in c.texto_literal.texto
    g = reg.cita("AASHTO_LRFD_9.12.11.1")
    assert g.pagina_impresa == "12-68" and g.pagina_pdf == 1706
    assert "cast-in-place and precast" in g.texto_literal.texto
    assert g.caracter is Caracter.EXIGENCIA


def test_el_registro_sigue_integro_con_las_citas_nuevas(reg):
    assert reg.problemas_de_integridad() == ()


# ===========================================================================
# 5. norma_producto por (material, forma) — EXT-N-03
# ===========================================================================

def test_el_marco_no_lleva_la_norma_de_producto_de_un_tubo():
    from src.modulos.M2_material import catalogo, norma_producto_de
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    assert tubo.norma_producto == "AASHTO M 170M-04 / ASTM C 76M-02 (metrica)"
    marco = norma_producto_de(TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.RECTANGULAR)
    assert marco.startswith("sin norma de producto")
    for pieza in ("in situ", "ruta_familia_c", "14.1", "LRFD", "Sec. 5",
                  "12.11", "EG-2013", "503", "504", "M 259", "M 273"):
        assert pieza in marco, pieza
    assert "M 170M" not in marco


def test_el_alcance_de_cada_norma_de_producto_esta_anclado_en_el_registro(reg):
    from src.modulos.M2_material import CITA_ALCANCE_NORMA_PRODUCTO
    claves = {(TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.CIRCULAR),
              (TipoMaterial.TMC, FormaSeccion.CIRCULAR),
              (TipoMaterial.HDPE, FormaSeccion.CIRCULAR),
              (TipoMaterial.CONCRETO_REFORZADO, FormaSeccion.RECTANGULAR)}
    assert set(CITA_ALCANCE_NORMA_PRODUCTO) == claves
    for citas in CITA_ALCANCE_NORMA_PRODUCTO.values():
        assert citas
        for cita_id in citas:
            reg.cita(cita_id)          # KeyError si no existe
    assert CITA_ALCANCE_NORMA_PRODUCTO[(TipoMaterial.CONCRETO_REFORZADO,
                                        FormaSeccion.RECTANGULAR)] == (
        "AASHTO_LRFD_9.12.4.2.4", "AASHTO_LRFD_9.12.11.1")


def test_el_motivo_de_descarte_de_un_marco_no_niega_una_norma_que_no_existe():
    """
    `MD._motivo_descarte` escribia «NO es un tope de AASHTO M 170M-04» para
    un marco que agota su serie: la norma del tubo no topa al marco, y el
    marco no tiene norma de producto que negar.
    """
    from src.modulos.MD import _motivo_descarte
    from src.modulos.M2_material import catalogo
    from tests.apoyo.criterios import declarados
    from tests.test_M2_material import DECLARACIONES_CAJON
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
    motivo = _motivo_descarte(marco, "x")
    assert "NO es un tope de" not in motivo
    assert "M 170M" not in motivo
    assert "sin norma de producto" in motivo
    assert "secciones_cajon_normalizadas" in motivo


def test_los_tres_sitios_de_m11_y_el_json_distinguen_el_marco():
    from src.modulos import M11_reporte as M11
    from src.modulos.M2_material import catalogo
    from tests.apoyo.criterios import declarados
    from tests.test_M2_material import DECLARACIONES_CAJON
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
    tubo = catalogo(TipoMaterial.TMC)
    assert M11.rotulo_norma_producto(tubo).startswith("norma de producto ")
    assert M11.rotulo_norma_producto(marco).startswith("sin norma de producto")
    assert "norma de producto sin" not in M11.rotulo_norma_producto(marco)
    import cli
    assert "alcance_norma_producto" in cli.CLAVES_DISENO_JSON


def test_las_claves_del_bloque_diseno_del_json_son_las_declaradas():
    """
    El contrato del JSON con el tablero externo (`cli.CLAVES_DISENO_JSON`)
    coincide con lo que `_diseno_json` construye, leido del AST: una clave
    nueva en el codigo sin su fila en la tupla, o al reves, falla aqui y no
    en la ruta de exportacion.
    """
    import ast, inspect
    import cli
    arbol = ast.parse(inspect.getsource(cli._diseno_json))
    dicts = [n for n in ast.walk(arbol) if isinstance(n, ast.Dict)]
    claves = tuple(k.value for k in dicts[0].keys if isinstance(k, ast.Constant))
    assert claves == cli.CLAVES_DISENO_JSON


# ===========================================================================
# 6. La eleccion de edicion: legal y tecnica (EXT-N-01, PC-26) y Vigencia
# ===========================================================================

def test_toda_fuente_presente_lleva_vigencia_como_campo_y_no_como_marca():
    for f in fu.FUENTES.values():
        assert f.vigencia is not None, f.id
        assert f.vigencia.fecha == fu.VIGENCIA_VERIFICADA_EL or f.id == "DG2018", f.id
        assert "VIGENCIA CONFIRMADA" not in f.nota and "EDICION POSTERIOR DETECTADA" not in f.nota, f.id
        assert fu.estado_de_vigencia(f) is f.vigencia.estado


def test_una_vigencia_posterior_sin_edicion_posterior_no_se_construye():
    with pytest.raises(ErrorDeRegistro):
        fu.Vigencia(estado=fu.EstadoDeVigencia.POSTERIOR, fecha="2026-09-14",
                    como="x")


def test_el_manual_de_puentes_lleva_su_acto_aprobatorio_y_el_que_lo_derogo():
    v = fu.MP.vigencia
    assert v.estado is fu.EstadoDeVigencia.POSTERIOR
    assert v.acto_aprobatorio == "RD 041-2016-MTC/14"
    assert v.derogado_por == "RD 19-2018-MTC/14"
    assert v.edicion_posterior
    # Las tecnicas de EE.UU. no se derogan por acto: nadie las «deja sin efecto».
    for id_ in ("AASHTO_LRFD_9", "AASHTO_M170M", "AASHTO_M36", "ASTM_A760",
                "ASTM_A796", "AASHTO_M294_TRAD"):
        assert fu.FUENTES[id_].vigencia.derogado_por == "", id_


def test_la_eleccion_pendiente_se_parte_en_legal_y_tecnica():
    assert fu.fuentes_con_eleccion_de_edicion_pendiente_legal() == ("MP",)
    assert set(fu.fuentes_con_eleccion_de_edicion_pendiente_tecnica()) == {
        "AASHTO_LRFD_9", "AASHTO_M170M", "AASHTO_M36", "ASTM_A760",
        "ASTM_A796", "AASHTO_M294_TRAD"}
    assert set(fu.fuentes_con_eleccion_de_edicion_pendiente()) == (
        set(fu.fuentes_con_eleccion_de_edicion_pendiente_legal())
        | set(fu.fuentes_con_eleccion_de_edicion_pendiente_tecnica()))


def test_el_criterio_legal_exige_fecha_de_inicio_y_acto_del_regimen_transitorio():
    """
    EXIGE, no dice: la opcion «citada» sin fecha de inicio del expediente ni
    acto del regimen transitorio se rechaza en la puerta (`ValueError`,
    contrato SIS-E-05). Medido en la auditoria adversarial de EXT-6: con
    forma `str` la guardia la aceptaba.
    """
    clave = "edicion_legal_que_rige_el_expediente"
    c = ca.CRITERIOS[clave]
    assert c.valor is None and c.etiqueta == "A" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert c.forma == ca.FORMA_DICT_CON_CAMPOS
    assert c.campos_obligatorios == ("opcion", "fecha_inicio_expediente",
                                     "acto_regimen_transitorio")
    assert len(c.sensibilidad) == 2
    citada, vigente = c.sensibilidad
    assert "2016" in citada and "inicio del expediente" in citada and "acto" in citada
    assert "2018" in vigente
    assert "Manual de Puentes" in c.justificacion
    assert "AASHTO" not in c.concepto
    assert c.sin_consumidor.strip()
    # La puerta: sin los dos datos, la opcion citada no entra.
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, citada)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, {"opcion": citada})
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, {"opcion": "otra edicion",
                                             "fecha_inicio_expediente": "2018-06-01",
                                             "acto_regimen_transitorio": "RD x"})
    try:
        ca.establecer_valor_dinamico(clave, {
            "opcion": citada, "fecha_inicio_expediente": "2018-06-01",
            "acto_regimen_transitorio": "RD 19-2018-MTC/14, disposicion "
                                        "transitoria (por leer)"})
        assert ca.valor(clave)["opcion"] == citada
    finally:
        ca.quitar_valor_dinamico(clave)


def test_el_criterio_tecnico_ya_no_dice_que_la_edicion_no_la_manda_nadie():
    c = ca.CRITERIOS["edicion_que_rige_el_expediente"]
    assert "no la manda nadie" not in c.justificacion
    assert "2014" in c.justificacion and "AASHTO LRFD" in c.justificacion
    assert "Manual de Puentes" not in c.concepto
    assert "seis" in c.justificacion
    assert "para las siete" not in c.justificacion and "para las siete" not in c.reemplazado_por


def test_la_introduccion_del_manual_de_puentes_ancla_la_lrfd_de_2014(reg):
    c = reg.cita("MP.INTRODUCCION#LRFD_2014")
    assert c.pagina_impresa == "43" and c.pagina_pdf == 44
    assert "2014" in c.texto_literal.texto
    assert "Septima" in c.texto_literal.texto or "Séptima" in c.texto_literal.texto
    assert c.caracter is Caracter.PERMISO
    assert "actualizaciones" in c.texto_literal.texto


# ===========================================================================
# 7. Textos que llegan al entregable (PC-30, EXT-G-03)
# ===========================================================================

def test_la_pagina_de_la_cuneta_que_imprime_la_memoria_es_la_del_registro():
    """No se repite el numero: se compara con `MC_HHD_CUNETA.pagina_impresa`."""
    from src.modulos import M10_espaciamiento as M10
    from src.modelos import Espaciamiento, GobiernaEspaciamiento
    pagina = ci.MC_HHD_CUNETA.pagina_impresa
    assert pagina == "179"
    assert f"pag. {pagina}" in M10.NUMERAL_FASE_10 and "178" not in M10.NUMERAL_FASE_10
    assert f"pag. {pagina}" in M10.__doc__ and "178" not in M10.__doc__
    e = Espaciamiento(L_normativo=1.0, L_hidraulico=2.0, espaciamiento_max=1.0,
                      gobierna=GobiernaEspaciamiento.NORMATIVO)
    assert f"pag. {pagina}" in e.numeral and "178" not in e.numeral
    assert f"pag. {pagina}" in ca.CRITERIOS["long_max_cuneta"].fuente
    assert "178" not in ca.CRITERIOS["long_max_cuneta"].fuente


def test_manning_dice_una_geometria_y_dos_velocidades():
    """
    «Escenarios independientes» contradecia MAT-D1/CP-2: M3 resuelve UNA
    geometria (tirante con n_max) y DOS velocidades. M3 no cambia.
    """
    assert "una geometr" in F.MANNING.que_paso.lower()
    assert "dos velocidades" in F.MANNING.que_paso.lower()
    assert "n_max" in F.MANNING.que_paso
    assert "dos veces" not in F.MANNING.por_que


def test_la_columna_tr_de_diseno_es_de_la_tabla_de_la_v8_y_no_de_la_tabla_02():
    from src.modelos import CategoriaTR
    from src.modulos.M1_clasificacion import tr_de_categoria
    tr = tr_de_categoria(CategoriaTR.QUEBRADA_IMPORTANTE)
    texto = tr.paso.resultado.procedencia
    assert "TR de diseño" in texto
    assert "hoja de ruta" in texto and "2.2" in texto
    assert "Tabla Nº 02" in texto and "no trae" in texto


def test_las_dos_bases_de_la_friccion_van_juntas_en_citas_discrepancias_y_fuentes():
    """
    29/19.63 = 1.477: +47.7 % sobre el TERMINO de friccion, que en CP-8 sube
    H de 0.4977 a 0.5455 m (+9.6 %). Decir «sobrestima el termino un 9.6 %»
    mezcla las bases (EXT-G-03).
    """
    textos = {
        "cita": ci.CITAS["HDS5_SI_1985.EC4B#K"].nota,
        "discrepancia": di.DISCREPANCIAS["DIS-HDS5-EDICIONES"].efecto_si_se_sigue_la_otra,
        "fuente": fu.HDS5_SI_1985.nota,
    }
    for donde, texto in textos.items():
        assert "47.7 %" in texto, donde
        assert "9.6 %" in texto, donde
        assert "termino de friccion un +9.6" not in texto, donde
