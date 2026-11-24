"""
tests/test_n1mp_manual_puentes_2018.py
======================================
N1 del plan de normas 2 (`proceso/planes_mejora/12_PLAN_NORMAS_2.md`): el
Manual de Puentes 2018 (RD 19-2018-MTC/14) entra al registro como la Fuente
`MP2018`, CONVIVE con la de 2016 (`MP`) y no la sustituye. Fichas N1MP-01 a
N1MP-04 de `docs/decisiones_diferidas.md`.

Lo que se fija aqui, y por que no basta con las guardias generales:

  1. EL CONTRASTE ES UNO A UNO. Cada una de las citas de MP tiene su par en
     MP2018 y al reves, con `corresponde_en` cruzado. T2, T3 y T6 de
     `test_normativa_pdf.py` ya buscan cada frase en su pagina de 2018; lo
     que ninguna guardia general dice es que NO FALTE ninguna, y una cita de
     2016 sin par es un numeral que nadie miro en la edicion vigente.
  2. NINGUN VALOR QUE ENTRE EN EL CALCULO CAMBIO. Las cifras primarias que
     `constantes_normativas` toma del Manual (la HL-93, el area de contacto,
     el piso de 0.60 m, el 1.2 de k_h0, el umbral de 6.00 m) estan tambien en
     el literal de 2018. Si un dia el registro cambia de edicion y una cifra
     no esta, este test lo dice antes que la memoria.
  3. LA ELECCION SIGUE SIENDO DEL PROYECTISTA. Incorporar la edicion vigente
     no resuelve 'edicion_legal_que_rige_el_expediente': MP sigue en la
     eleccion legal pendiente y MP2018 no entra en ninguna.
  4. (con el PDF) la paginacion y lo que la capa de texto no entrega, y que
     el mapa de PGA del Apendice A3 es el MISMO raster en las dos ediciones,
     que es lo que hace que la lectura del corredor no dependa de la edicion.
"""

import re
from pathlib import Path

import numpy as np
import pytest

from src import constantes_normativas as CN
from src.normativa import fuentes as fu
from src.normativa import registro as _registro
from src.normativa.extraccion import normalizar, pymupdf_disponible
from tests.apoyo.aproximacion import REL_TRANSPORTE

PREFIJO_2016 = "MP."
PREFIJO_2018 = "MP2018."

# El unico par cuyo sufijo de id NO coincide: la edicion 2016 imprime el
# numeral con una errata (2.3.1.1.12.3, DIS-MP-NUMERAL-2.3.1.1.12.3) que la
# de 2018 corrige (2.8.1.1.12.3), y la cita de 2018 lleva el numeral que su
# pagina imprime.
SUFIJO_RENUMERADO = {"2.3.1.1.12.3#EXC_ESTATICA": "2.8.1.1.12.3#EXC_ESTATICA"}

# Las cifras PRIMARIAS que el calculo toma del Manual, con la cita de 2018
# que tiene que escribirlas. Se nombran las constantes y no las cifras: si
# una constante cambia, el test busca la cifra nueva en el literal.
CIFRAS_QUE_EL_LITERAL_2018_SOSTIENE = [
    ("MP2018.2.4.3.2.2.2", f"{CN.EJE_CAMION_HL93_KIP}-kips"),
    ("MP2018.2.4.3.2.2.2", f"{CN.SEPARACION_EJES_CAMION_MIN_PIE} ft"),
    ("MP2018.2.4.3.2.2.3", f"{CN.EJE_TANDEM_HL93_KIP} kip"),
    ("MP2018.2.4.3.2.2.3", f"{CN.SEPARACION_EJES_TANDEM_PIE} ft"),
    ("MP2018.2.4.3.2.2.3", f"{CN.SEPARACION_RUEDAS_PIE} ft"),
    ("MP2018.2.4.3.2.2.5", f"{CN.ANCHO_NEUMATICO_PULG} in"),
    ("MP2018.2.4.3.2.2.5", f"{CN.LARGO_NEUMATICO_PULG} in"),
    ("MP2018.2.4.2.2#SOBRECARGA", "0.60 m"),
    ("MP2018.2.8.1.1.14.2.1#ROCA", f"{CN.K_H0_FACTOR_ROCA_A_B} veces"),
    ("MP2018.GLOSARIO#OBRAS_DE_ARTE_MENORES", "6.00 m"),
]


@pytest.fixture(scope="module")
def reg():
    return _registro.construir()


def _pares(reg):
    return {c.id: c for c in reg.citas_de("MP")}, \
        {c.id: c for c in reg.citas_de("MP2018")}


def test_cada_cita_de_MP_tiene_su_par_en_MP2018_y_al_reves(reg):
    de_2016, de_2018 = _pares(reg)
    assert de_2016 and len(de_2016) == len(de_2018), (
        f"{len(de_2016)} citas de MP y {len(de_2018)} de MP2018: el contraste "
        "de N1 es uno a uno, y una cita nueva de una edicion necesita su par "
        "en la otra (o una razon escrita para no tenerlo)")
    for id_2016, c in de_2016.items():
        sufijo = id_2016[len(PREFIJO_2016):]
        par = PREFIJO_2018 + SUFIJO_RENUMERADO.get(sufijo, sufijo)
        assert par in de_2018, f"{id_2016} no tiene par: falta {par}"
        assert par in c.corresponde_en, (id_2016, c.corresponde_en)
        assert id_2016 in de_2018[par].corresponde_en, (par, id_2016)


def test_toda_cita_de_MP2018_dice_que_cambio_o_que_es_igual(reg):
    """
    La nota de cada par es la fila del contraste: empieza diciendo si el
    texto es IGUAL o que CAMBIO. Una nota vacia o neutra no le dice al
    revisor si puede pasar a la edicion vigente sin leer la pagina.
    """
    _, de_2018 = _pares(reg)
    marcas = ("IGUAL", "CAMBIO", "CORREGID", "LA ERRATA", "LAS CIFRAS",
              "LOS VALORES", "EL TEXTO ES IGUAL", "EL SIGNO")
    for c in de_2018.values():
        assert c.verificado is not None, c.id
        assert c.verificado.sha1_pdf == fu.MP2018.sha1, c.id
        assert c.nota.startswith(marcas), (c.id, c.nota[:60])


@pytest.mark.parametrize("cita_id,cifra", CIFRAS_QUE_EL_LITERAL_2018_SOSTIENE)
def test_las_cifras_primarias_del_calculo_siguen_en_la_edicion_2018(
        reg, cita_id, cifra):
    texto = reg.cita(cita_id).texto_literal.texto
    assert normalizar(cifra) in normalizar(texto), (
        f"{cita_id} no escribe {cifra!r}: o la edicion 2018 cambio la cifra "
        "que el calculo usa, o la cita es de otro parrafo")


def test_las_dos_ediciones_conviven_y_la_eleccion_legal_sigue_pendiente():
    assert fu.MP.convive_con == ("MP2018",)
    assert fu.MP2018.convive_con == ("MP",)
    assert fu.MP2018.resolucion == "RD 19-2018-MTC/14" == fu.MP.vigencia.derogado_por
    assert fu.MP2018.vigencia.estado is fu.EstadoDeVigencia.CONFIRMADA
    assert fu.MP2018.vigencia.acto_aprobatorio == fu.MP2018.resolucion
    assert fu.MP2018.vigencia.fecha == fu.VIGENCIA_VERIFICADA_EL_N1MP
    # Ninguna Discrepancia resuelta dice cual gobierna: elegir es del
    # proyectista, con la fecha de inicio del expediente.
    assert fu.quien_gobierna_por_discrepancia("MP") is None
    assert fu.fuentes_con_eleccion_de_edicion_pendiente_legal() == ("MP",)
    assert "MP2018" not in fu.fuentes_con_eleccion_de_edicion_pendiente()
    # Lo que T1 dejo para gabinete se hizo: ya no se pide conseguirla.
    assert "conseguir la edicion 2018" not in fu.MP.vigencia.pendiente_gabinete
    assert "MP2018" in fu.MP.vigencia.edicion_posterior
    assert "NINGUNA disposicion transitoria" in fu.MP.nota


def test_el_raster_del_mapa_de_pga_se_declara_igual_en_las_dos_ediciones():
    """La afirmacion vive en la Fuente ausente del apendice; el PDF la mide."""
    assert "MISMO raster" in fu.APENDICE_A3_MP.nota
    assert "MISMO raster" in fu.MP2018.nota


# ---------------------------------------------------------------------------
# El dictamen de Fable (fichas N1MP-05 y N1MP-06)
# ---------------------------------------------------------------------------

# Cada discrepancia de la edicion 2016 con la parte que la edicion 2018 le
# suma, y lo que NO cambio: quien gana y el estado.
PARTES_MP2018 = {
    "DIS-MP-KAE-SIGNO": ("MP2018.A.11.3.1#KAE", "AASHTO_LRFD_9",
                         "errata_de_imprenta"),
    "DIS-MP-KH0-ROCA": ("MP2018.2.8.1.1.14.2.1#ROCA", "AASHTO_LRFD_9",
                        "errata_de_imprenta"),
    "DIS-MP-NUMERAL-2.3.1.1.12.3": ("MP2018.2.8.1.1.12.3#EXC_ESTATICA", "MP",
                                    "errata_de_imprenta"),
    "DIS-MP-EXCENTRICIDAD": ("MP2018.2.8.1.1.14.1#EXC", "AASHTO_LRFD_9",
                             "errata_de_imprenta"),
    "DIS-LUZ-DENOMINACION": ("MP2018.GLOSARIO#OBRAS_DE_ARTE_MENORES",
                             "HDS5_3ED", "abierta"),
}


@pytest.mark.parametrize("dis_id", sorted(PARTES_MP2018))
def test_la_edicion_2018_es_parte_de_las_discrepancias_que_toca(reg, dis_id):
    cita, gana, estado = PARTES_MP2018[dis_id]
    d = reg.discrepancia(dis_id)
    partes = {p.quien: p for p in d.partes}
    assert partes["MP2018"].cita_id == cita
    assert d.gana == gana and d.estado.value == estado


def test_los_textos_de_errata_dicen_de_que_edicion_son():
    for texto in (CN.K_AE_ERRATA_MANUAL, CN.K_H0_ROCA_ERRATA,
                  CN.NUMERAL_EXCENTRICIDAD_ESTATICA):
        assert "edicion 2016" in normalizar(texto) and "041-2016" in texto
        assert "edicion 2018" in normalizar(texto) and "19-2018" in texto
    assert "pag. impresa 597" in CN.K_AE_ERRATA_MANUAL
    assert "pag. impresa 249" in CN.K_H0_ROCA_ERRATA
    assert "pag. impresa 244" in CN.NUMERAL_EXCENTRICIDAD_ESTATICA
    assert "EN LAS DOS EDICIONES" in CN.EXCENTRICIDAD_ERRATA_MANUAL


def test_la_pga_del_corredor_es_una_discrepancia_contra_la_hoja_de_ruta_y_el_valor_no_cambio(reg):
    from src import datos_sitio as ds
    d = reg.discrepancia("DIS-HR-PGA-LECTURA")
    assert d.estado.value == "abierta_contra_hoja_de_ruta"
    assert {p.quien for p in d.partes} == {"hoja_de_ruta", "MP2018",
                                           "AASHTO_LRFD_9"}
    assert "AASHTO_LRFD_9.3.10.2.1#INTERPOLACION" in d.citas
    assert "SIGUE MAL" in d.por_que
    # El valor es del dueño: la lectura se declara en el punto de uso.
    pga = ds.dato("PGA_roca_B")
    assert pga.valor == pytest.approx(0.50, rel=REL_TRANSPORTE)
    assert "cota INFERIOR" in pga.trazabilidad
    assert "DIS-HR-PGA-LECTURA" in pga.trazabilidad


# ---------------------------------------------------------------------------
# Con el PDF
# ---------------------------------------------------------------------------

def _ruta(fuente) -> Path:
    ruta = fu.ruta_pdf(fuente)
    if not ruta.exists():
        pytest.skip(f"falta {ruta}")
    return ruta


@pytest.mark.pdf
@pytest.mark.skipif(not pymupdf_disponible(), reason="sin PyMuPDF")
def test_la_paginacion_de_MP2018_es_la_medida_y_las_cuatro_primeras_no_tienen_texto():
    import pymupdf
    doc = pymupdf.open(str(_ruta(fu.MP2018)))
    try:
        assert doc.page_count == fu.MP2018.paginas_pdf
        confirman = 0
        for i in range(doc.page_count):
            pdf = i + 1
            texto = normalizar(doc[i].get_text())
            if fu.MP2018.paginacion.pagina_pdf(str(pdf - 4)) == pdf and \
                    re.search(rf"\bpagina {pdf - 4}(?!\d)", texto):
                confirman += 1
        assert confirman == 630, confirman
        # La RD 19-2018-MTC/14 (PDF 1 a 3) y la caratula (PDF 4) son imagen:
        # la resolucion se leyo renderizando, y por eso no hay cita a ellas.
        for pdf in (1, 2, 3, 4):
            assert not doc[pdf - 1].get_text().strip(), pdf
    finally:
        doc.close()


def _mapa_pga(fuente, pagina_pdf):
    """El raster del mapa de PGA del Apendice A3: la imagen mayor de la pagina."""
    import pymupdf
    doc = pymupdf.open(str(_ruta(fuente)))
    try:
        imagenes = doc[pagina_pdf - 1].get_images(full=True)
        xref = max(imagenes, key=lambda im: im[2] * im[3])[0]
        pix = pymupdf.Pixmap(doc, xref)
        if pix.n - pix.alpha != 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n)[..., :3].astype(int)
    finally:
        doc.close()


@pytest.mark.pdf
@pytest.mark.skipif(not pymupdf_disponible(), reason="sin PyMuPDF")
def test_el_mapa_de_pga_es_el_mismo_raster_en_las_dos_ediciones():
    """
    Medido en N1: mismas dimensiones (797 x 1099 px), diferencia media de
    unos 3 niveles sobre 255 y NINGUN pixel que difiera en mas de 64 en
    algun canal --- el ruido de volver a comprimir el mismo JPEG ---. La
    sensibilidad se midio por mutacion: desplazar 2 px el recuadro de 100 x
    60 px que rodea La Union deja 651 pixeles por encima de 80. Por eso el
    umbral es 80 y la cuenta tiene que ser cero.
    """
    a = _mapa_pga(fu.MP, 553)
    b = _mapa_pga(fu.MP2018, 568)
    assert a.shape == b.shape == (1099, 797, 3)
    dif = np.abs(a - b)
    assert dif.mean() < 5.0, dif.mean()
    umbral = 80    # literal-ok: niveles de 0-255; el ruido JPEG medido llega a 64
    distintos = int((dif.max(axis=2) > umbral).sum())
    assert distintos == 0, (
        f"{distintos} pixeles del mapa de PGA difieren en mas de {umbral} "
        "niveles entre las dos ediciones: el raster ya no es el mismo y la "
        "lectura del corredor (ficha N1MP-04) hay que rehacerla en el de 2018")
