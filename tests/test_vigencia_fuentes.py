"""
tests/test_vigencia_fuentes.py
==============================
La VIGENCIA de las ediciones citadas, verificada en T1 (2026-09-14) y
registrada en la `nota` de cada Fuente presente detras de una marca fija.

POR QUE HAY TESTS SOBRE UNA MARCA EN PROSA. El esquema no tiene campo para
«el emisor publica hoy una edicion posterior a la citada» (ver el bloque T1
de `fuentes.py` y la ficha T1-01 de docs/decisiones_diferidas.md). Mientras
no lo tenga, lo que impide que la vigencia sea prosa que nadie enumera son
estas guardias: toda fuente presente lleva exactamente UNA marca; el censo de
las superadas esta fijado y solo cambia a sabiendas; la eleccion que queda
para el proyectista esta declarada vacia en `criterios_adoptados` y su ficha
nombra a cada fuente superada, a todas y solo a ellas, derivadas del
registro y no escritas dos veces.

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

# Como la ficha del criterio nombra a cada fuente con eleccion pendiente. El
# test exige que las claves sean EXACTAMENTE las que el registro deriva, de
# modo que la ficha no puede quedarse corta ni sobrar sin que se note.
DESIGNADOR_EN_LA_FICHA = {
    "MP": "Manual de Puentes",
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
    sin_marca = [f.id for f in fu.FUENTES.values()
                 if fu.estado_de_vigencia(f) is None]
    assert not sin_marca, (
        f"fuentes presentes sin marca de vigencia: {sin_marca}. Una fuente "
        "nueva en normas/ entra con su vigencia verificada contra el emisor "
        "(o marcada «no determinable en linea», que tambien es una marca)")


def test_las_tres_marcas_llevan_la_fecha_de_la_verificacion():
    for marca in fu.MARCAS_DE_VIGENCIA:
        assert marca.endswith(fu.VIGENCIA_VERIFICADA_EL), marca


def test_una_nota_con_dos_marcas_es_un_error_de_registro():
    """Vigente y superada a la vez no es un estado: es una nota mal escrita."""
    doble = dataclasses.replace(
        fu.MC_HHD, nota=fu.VIGENCIA_CONFIRMADA + " ... " + fu.VIGENCIA_POSTERIOR)
    with pytest.raises(ErrorDeRegistro):
        fu.estado_de_vigencia(doble)


def test_una_nota_sin_marca_devuelve_None_y_no_inventa_un_estado():
    assert fu.estado_de_vigencia(dataclasses.replace(fu.MC_HHD, nota="")) is None


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
    detectada» seria un aviso sin destinatario.
    """
    for id_ in CENSO_EDICION_POSTERIOR:
        assert CLAVE in fu.FUENTES[id_].nota, id_


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
        nota=fu.HDS5_3ED.nota.replace(fu.VIGENCIA_CONFIRMADA, fu.VIGENCIA_POSTERIOR))
    pendientes = fu.fuentes_con_eleccion_de_edicion_pendiente(mutadas)
    assert "HDS5_3ED" in pendientes
    assert "HDS5_SI_1985" not in pendientes


def test_la_ficha_del_criterio_nombra_a_cada_fuente_pendiente_y_solo_a_ellas():
    pendientes = fu.fuentes_con_eleccion_de_edicion_pendiente()
    assert set(pendientes) == set(DESIGNADOR_EN_LA_FICHA), (
        "el registro deriva una lista de fuentes con eleccion pendiente y la "
        "ficha del criterio nombra otra: se actualizan las dos a la vez")
    c = ca.CRITERIOS[CLAVE]
    for id_, designador in DESIGNADOR_EN_LA_FICHA.items():
        assert designador in c.justificacion, (id_, designador)
    # La octava superada (HDS5_SI_1985) no es pendiente: la ficha lo dice
    # asi, como resuelto por el registro, y no la lista entre las siete.
    assert "discrepancia resuelta" in c.justificacion, (
        "la ficha tiene que decir que el registro ya resolvio una de las "
        "ocho superadas (las dos ediciones de HDS-5) y por que no se elige")
    assert "HDS-5 (citada" not in c.justificacion and "HDS5_SI_1985" not in c.justificacion, (
        "la ficha no debe presentar como pendiente lo que el registro ya "
        "resolvio (HDS5_SI_1985)")


def test_el_criterio_es_una_eleccion_vacia_de_expediente():
    c = ca.CRITERIOS[CLAVE]
    assert c.valor is None and not c.opcional
    assert c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_EXPEDIENTE
    assert isinstance(c.sensibilidad, tuple) and len(c.sensibilidad) == 2, (
        "la ventana es simbolica y cerrada: la edicion citada o la vigente")
    assert isinstance(c.resolucion, Libre)
    assert c.sin_consumidor.strip(), (
        "un criterio sin consumidor dice por que no lo invoca nadie")
    with pytest.raises(CriterioPendienteError):
        ca.valor(CLAVE)


def test_declarar_la_eleccion_en_caliente_pasa_por_la_misma_guardia():
    """Se puede declarar una de las dos opciones; None se rechaza."""
    try:
        ca.establecer_valor_dinamico(CLAVE, ca.CRITERIOS[CLAVE].sensibilidad[0])
        assert ca.valor(CLAVE) == ca.CRITERIOS[CLAVE].sensibilidad[0]
    finally:
        ca.quitar_valor_dinamico(CLAVE)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(CLAVE, None)


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
