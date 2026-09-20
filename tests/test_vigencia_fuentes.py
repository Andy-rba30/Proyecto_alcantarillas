"""
tests/test_vigencia_fuentes.py
==============================
La VIGENCIA de las ediciones citadas, verificada en T1 (2026-09-14; la del
DG-2018 en EXT-6) y registrada en el campo `Fuente.vigencia`.

HASTA EXT-6 ERA UNA MARCA EN LA NOTA, y estos tests vigilaban la marca: el
esquema no tenia campo para «el emisor publica hoy una edicion posterior a
la citada» (ficha T1-01 de docs/decisiones_diferidas.md). EXT-6 escribio el
campo con lo que la ficha pedia y lo que EXT-N-01 añadio --- el acto que
aprobo la edicion citada y el que la derogo ---, y los tests pasaron a
vigilar el campo: toda fuente presente lo lleva; el censo de las superadas
esta fijado y solo cambia a sabiendas; la eleccion que queda para el
proyectista se PARTE en legal (derogada por acto: el Manual de Puentes) y
tecnica (las seis de EE.UU.), cada una declarada vacia en
`criterios_adoptados` con su ficha nombrando a las suyas, a todas y solo a
ellas, derivadas del registro y no escritas dos veces.

LO QUE NO SE COMPRUEBA AQUI, a proposito: que la edicion vigente sea la que
la nota dice. Eso se verifico contra el emisor, por busqueda web, y se
reverifica en gabinete; un test no puede abrir la pagina del MTC.
"""

import dataclasses

import pytest

import criterios_adoptados as ca
from modelos import CriterioPendienteError, Libre
from normativa import fuentes as fu
from normativa.esquema import ErrorDeRegistro

CLAVE = "edicion_que_rige_el_expediente"
CLAVE_LEGAL = "edicion_legal_que_rige_el_expediente"

# Medido en T1. Las ocho presentes cuyo emisor publica una edicion posterior
# a la citada; HDS5_SI_1985 esta aqui y NO en la eleccion pendiente, porque
# su sucesora (HDS5_3ED) esta presente, es mas nueva y esta confirmada.
CENSO_EDICION_POSTERIOR = (
    "MP", "HDS5_SI_1985", "AASHTO_LRFD_9", "AASHTO_M170M", "AASHTO_M36",
    "ASTM_A760", "ASTM_A796", "AASHTO_M294_TRAD",
)

# Ninguna quedo indeterminable en linea. Si una sesion futura marca alguna
# «a gabinete», este censo la recibe a sabiendas.
CENSO_A_GABINETE = ()

# Como la ficha de cada criterio nombra a cada fuente con eleccion pendiente.
# El test exige que las claves sean EXACTAMENTE las que el registro deriva, de
# modo que la ficha no puede quedarse corta ni sobrar sin que se note. Desde
# EXT-6 son dos fichas: la LEGAL (derogada por acto) y la TECNICA.
DESIGNADOR_EN_LA_FICHA_LEGAL = {
    "MP": "Manual de Puentes",
}
DESIGNADOR_EN_LA_FICHA = {
    "AASHTO_LRFD_9": "AASHTO LRFD",
    "AASHTO_M170M": "M 170M",
    "AASHTO_M36": "M 36",
    "ASTM_A760": "A760",
    "ASTM_A796": "A796",
    "AASHTO_M294_TRAD": "M 294",
}


# ---------------------------------------------------------------------------
# La marca: una por fuente presente, y de las tres
# ---------------------------------------------------------------------------

def test_toda_fuente_presente_declara_su_vigencia():
    sin_campo = [f.id for f in fu.FUENTES.values() if f.vigencia is None]
    assert not sin_campo, (
        f"fuentes presentes sin `vigencia`: {sin_campo}. Una fuente nueva en "
        "normas/ entra con su vigencia verificada contra el emisor (o marcada "
        "«no determinable en linea», que tambien es un estado)")
    for f in fu.FUENTES.values():
        assert fu.estado_de_vigencia(f) is f.vigencia.estado
        assert f.vigencia.fecha in (fu.VIGENCIA_VERIFICADA_EL,
                                    fu.VIGENCIA_VERIFICADA_EL_EXT6), f.id
        assert f.vigencia.como.strip(), f.id


def test_las_marcas_en_prosa_desaparecieron_de_las_notas():
    """Una sola fuente de verdad: el campo. La marca de T1 ya no se busca."""
    for f in list(fu.FUENTES.values()) + list(fu.FUENTES_AUSENTES.values()):
        assert "VIGENCIA CONFIRMADA 2026" not in f.nota, f.id
        assert "EDICION POSTERIOR DETECTADA 2026" not in f.nota, f.id
        assert "NO DETERMINABLE EN LINEA 2026" not in f.nota, f.id


def test_una_fuente_presente_sin_vigencia_no_se_construye():
    """Vigencia en blanco no es un estado: es una fuente sin verificar."""
    with pytest.raises(ErrorDeRegistro):
        dataclasses.replace(fu.MC_HHD, vigencia=None)


def test_una_vigencia_posterior_sin_edicion_posterior_no_se_construye():
    with pytest.raises(ErrorDeRegistro):
        fu.Vigencia(estado=fu.EstadoDeVigencia.POSTERIOR,
                    fecha=fu.VIGENCIA_VERIFICADA_EL, como="x")


def test_una_derogacion_solo_cabe_en_una_edicion_superada():
    """Una edicion derogada no esta vigente: `derogado_por` exige POSTERIOR."""
    with pytest.raises(ErrorDeRegistro):
        fu.Vigencia(estado=fu.EstadoDeVigencia.CONFIRMADA,
                    fecha=fu.VIGENCIA_VERIFICADA_EL, como="x",
                    derogado_por="RD x")


def test_una_fuente_sin_vigencia_devuelve_None_y_no_inventa_un_estado():
    assert fu.estado_de_vigencia(dataclasses.replace(
        fu.MC_HHD, ausente=True, archivo_pdf=None, sha1=None, vigencia=None,
        ausencia=fu.RNGIV.ausencia)) is None


# ---------------------------------------------------------------------------
# Los censos medidos
# ---------------------------------------------------------------------------

def test_el_censo_de_edicion_posterior_es_el_medido():
    assert fu.fuentes_con_edicion_posterior() == CENSO_EDICION_POSTERIOR, (
        "el conjunto de fuentes con edicion posterior cambio: o llego un "
        "documento nuevo a normas/ (entonces la fuente superada se modela "
        "como HDS5_SI_1985, con convive_con y una Discrepancia) o una sesion "
        "reverifico la vigencia. En los dos casos se actualiza el censo A "
        "SABIENDAS, y la ficha de 'edicion_que_rige_el_expediente' con el")


def test_ninguna_fuente_quedo_a_gabinete():
    a_gabinete = tuple(f.id for f in fu.FUENTES.values()
                       if fu.estado_de_vigencia(f) == fu.VIGENCIA_GABINETE)
    assert a_gabinete == CENSO_A_GABINETE


def test_las_confirmadas_son_el_resto():
    confirmadas = {f.id for f in fu.FUENTES.values()
                   if fu.estado_de_vigencia(f) == fu.VIGENCIA_CONFIRMADA}
    assert confirmadas == (set(fu.FUENTES) - set(CENSO_EDICION_POSTERIOR)
                           - set(CENSO_A_GABINETE))


def test_toda_superada_dice_a_quien_le_toca_elegir():
    """
    La nota de una fuente superada nombra el criterio del proyectista, o
    dice por que no hace falta (HDS5_SI_1985). Sin eso, «edicion posterior
    detectada» seria un aviso sin destinatario. El Manual de Puentes nombra
    el LEGAL; las demas, el tecnico (que por su nombre contiene al otro).
    """
    for id_ in CENSO_EDICION_POSTERIOR:
        assert CLAVE in fu.FUENTES[id_].nota, id_
    assert CLAVE_LEGAL in fu.MP.nota


def test_toda_superada_dice_cual_es_la_edicion_posterior():
    for id_ in CENSO_EDICION_POSTERIOR:
        assert fu.FUENTES[id_].vigencia.edicion_posterior.strip(), id_


def test_solo_el_manual_de_puentes_fue_derogado_por_un_acto():
    """
    Lo que separa una fuente legal peruana de una tecnica extranjera no es
    el emisor: es que un acto la deje sin efecto. Las cinco normas de EE.UU.
    y la copia de 1985 del HDS-5 tienen edicion posterior y nadie las deroga.
    """
    derogadas = tuple(f.id for f in fu.FUENTES.values()
                      if f.vigencia.derogado_por)
    assert derogadas == ("MP",)
    assert fu.MP.vigencia.acto_aprobatorio == fu.MP.resolucion
    assert fu.MP.vigencia.derogado_por == "RD 19-2018-MTC/14"


# ---------------------------------------------------------------------------
# La eleccion pendiente: derivada del registro, no escrita
# ---------------------------------------------------------------------------

def test_la_eleccion_pendiente_la_resuelve_una_discrepancia_y_no_el_anio():
    """
    Lo unico que en el registro DICE quien gobierna entre dos ediciones es
    una Discrepancia resuelta con `gana`: DIS-HDS5-EDICIONES saca a
    HDS5_SI_1985 de la eleccion. AASHTO_M36 convive con ASTM_A760 --
    presente y mas nueva -- y sigue dentro, porque ninguna discrepancia hace
    ganar a A760; comparar años lo habria sacado.
    """
    pendientes = fu.fuentes_con_eleccion_de_edicion_pendiente()
    assert "HDS5_SI_1985" not in pendientes
    assert fu.quien_gobierna_por_discrepancia("HDS5_SI_1985") == "HDS5_3ED"
    assert "AASHTO_M36" in pendientes
    assert fu.quien_gobierna_por_discrepancia("AASHTO_M36") is None
    assert set(pendientes) < set(CENSO_EDICION_POSTERIOR)


def test_la_regla_comprobada_fuente_a_fuente():
    for id_ in CENSO_EDICION_POSTERIOR:
        resuelta = fu.quien_gobierna_por_discrepancia(id_) is not None
        assert (id_ in fu.fuentes_con_eleccion_de_edicion_pendiente()) == (
            not resuelta), id_


def test_una_cuarta_edicion_de_HDS5_no_reabre_la_eleccion_de_la_de_1985():
    """
    POR MUTACION, que es como se conoce el limite de una regla: si HDS5_3ED
    quedara superada, ella entra en la eleccion y la de 1985 SIGUE FUERA,
    porque la discrepancia que la descarto frente a la tercera no se reabre
    por una cuarta. Una regla por años la habria hecho reentrar.
    """
    mutadas = dict(fu.FUENTES)
    mutadas["HDS5_3ED"] = dataclasses.replace(
        fu.HDS5_3ED,
        vigencia=fu.Vigencia(estado=fu.EstadoDeVigencia.POSTERIOR,
                             fecha=fu.VIGENCIA_VERIFICADA_EL, como="mutacion",
                             edicion_posterior="una cuarta edicion hipotetica"))
    pendientes = fu.fuentes_con_eleccion_de_edicion_pendiente(mutadas)
    assert "HDS5_3ED" in pendientes
    assert "HDS5_SI_1985" not in pendientes


def test_la_eleccion_pendiente_se_parte_en_legal_y_tecnica_sin_perder_ninguna():
    legal = fu.fuentes_con_eleccion_de_edicion_pendiente_legal()
    tecnica = fu.fuentes_con_eleccion_de_edicion_pendiente_tecnica()
    assert legal == ("MP",)
    assert not (set(legal) & set(tecnica))
    assert set(legal) | set(tecnica) == set(fu.fuentes_con_eleccion_de_edicion_pendiente())


def test_la_ficha_del_criterio_nombra_a_cada_fuente_pendiente_y_solo_a_ellas():
    pendientes = fu.fuentes_con_eleccion_de_edicion_pendiente_tecnica()
    assert set(pendientes) == set(DESIGNADOR_EN_LA_FICHA), (
        "el registro deriva una lista de fuentes tecnicas con eleccion "
        "pendiente y la ficha del criterio nombra otra: se actualizan las dos "
        "a la vez")
    c = ca.CRITERIOS[CLAVE]
    for id_, designador in DESIGNADOR_EN_LA_FICHA.items():
        assert designador in c.justificacion, (id_, designador)
    # La superada que el registro resolvio (HDS5_SI_1985) no es pendiente: la
    # ficha lo dice asi, y no la lista entre las seis.
    assert "discrepancia resuelta" in c.justificacion
    assert "HDS-5 (citada" not in c.justificacion and "HDS5_SI_1985" not in c.justificacion
    # Y el Manual de Puentes ya no esta en esta ventana: tiene la suya.
    assert "Manual de Puentes (el ejemplar" not in c.justificacion
    assert "para las seis" in c.justificacion


def test_la_ficha_legal_nombra_al_manual_de_puentes_y_exige_fecha_y_acto():
    pendientes = fu.fuentes_con_eleccion_de_edicion_pendiente_legal()
    assert set(pendientes) == set(DESIGNADOR_EN_LA_FICHA_LEGAL)
    c = ca.CRITERIOS[CLAVE_LEGAL]
    for designador in DESIGNADOR_EN_LA_FICHA_LEGAL.values():
        assert designador in c.justificacion
    citada, vigente = c.sensibilidad
    assert fu.MP.vigencia.acto_aprobatorio in citada
    assert fu.MP.vigencia.derogado_por in citada and fu.MP.vigencia.derogado_por in vigente
    assert "inicio del expediente" in citada and "acto" in citada


@pytest.mark.parametrize("clave", [CLAVE, CLAVE_LEGAL])
def test_el_criterio_es_una_eleccion_vacia_de_expediente(clave):
    c = ca.CRITERIOS[clave]
    assert c.valor is None and not c.opcional
    assert c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_EXPEDIENTE
    assert isinstance(c.sensibilidad, tuple) and len(c.sensibilidad) == 2, (
        "la ventana es simbolica y cerrada: la edicion citada o la vigente")
    assert c.forma == (ca.FORMA_DICT_CON_CAMPOS if clave == CLAVE_LEGAL
                       else ca.FORMA_STR)
    assert isinstance(c.resolucion, Libre)
    assert c.sin_consumidor.strip(), (
        "un criterio sin consumidor dice por que no lo invoca nadie")
    with pytest.raises(CriterioPendienteError):
        ca.valor(clave)


def _declaracion_valida(clave):
    """La forma que cada criterio exige: texto en el tecnico, diccionario con
    fecha y acto en el legal."""
    opcion = ca.CRITERIOS[clave].sensibilidad[0]
    if clave == CLAVE_LEGAL:
        return {"opcion": opcion, "fecha_inicio_expediente": "2018-06-01",
                "acto_regimen_transitorio": "RD 19-2018-MTC/14 (por leer)"}
    return opcion


@pytest.mark.parametrize("clave", [CLAVE, CLAVE_LEGAL])
def test_declarar_la_eleccion_en_caliente_pasa_por_la_misma_guardia(clave):
    """Se puede declarar una de las dos opciones; None se rechaza."""
    try:
        ca.establecer_valor_dinamico(clave, _declaracion_valida(clave))
        assert ca.valor(clave) == _declaracion_valida(clave)
    finally:
        ca.quitar_valor_dinamico(clave)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, None)


# ---------------------------------------------------------------------------
# Lo que la verificacion hizo aparecer
# ---------------------------------------------------------------------------

def test_la_resolucion_del_Manual_de_Puentes_es_la_del_ejemplar_y_no_la_de_2018():
    """
    La ficha citaba la RD del Manual actualizado de 2018; el ejemplar es la
    edicion 2016 (lo imprime en sus PDF 2 y 3, y tests/test_normativa_pdf.py
    lo comprueba con PyMuPDF). La edicion citada no cambio: la RD si.
    """
    assert fu.MP.resolucion == "RD 041-2016-MTC/14"
    assert fu.MP.anio == 2016
    assert "19-2018-MTC/14" in fu.MP.nota, (
        "la nota tiene que decir cual es la edicion posterior y su RD")


def test_la_vigencia_no_toca_ninguna_cita():
    """
    La vigencia es un metadato de la FUENTE. Ninguna cita del registro habla
    de ella, y ninguna cita cambio de pagina, sha1 ni texto por T1: lo que se
    comprueba es que el registro sigue integro con las notas nuevas.
    """
    from normativa import registro as _registro
    reg = _registro.construir()
    assert reg.problemas_de_integridad() == ()
    assert all("VIGENCIA" not in (c.nota or "") for c in reg.citas)


def test_el_dg2018_entro_con_su_vigencia_verificada_en_ext6():
    v = fu.DG2018.vigencia
    assert v.estado is fu.EstadoDeVigencia.CONFIRMADA
    assert v.fecha == fu.VIGENCIA_VERIFICADA_EL_EXT6
    assert v.acto_aprobatorio == fu.DG2018.resolucion == "RD 03-2018-MTC/14"
