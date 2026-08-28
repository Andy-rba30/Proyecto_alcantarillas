"""
tests/test_normativa_pdf.py
===========================
La guardia que ABRE LOS PDF: T0, T2, T3, T5 y T6 de la §9.2 del diseño del
registro normativo. Es la que hace verdadera la palabra «verificado».

LOS ESTRUCTURALES DICEN QUE LA CITA ESTA BIEN FORMADA; ESTOS DICEN QUE ES
CIERTA. Sin ellos, `Verificado` es una etiqueta que alguien escribio y nadie
comprobo -- que es exactamente el estado del que sale este cluster.

SE SALTAN, NO FALLAN, si PyMuPDF no esta instalado o si falta un PDF de
`normas/`. Es deliberado: `requirements.txt` es lo que hace falta para
CALCULAR una alcantarilla y `requirements-dev.txt` lo que hace falta para
COMPROBAR que lo calculado se apoya en lo que las normas dicen. Un despliegue
que solo produzca memorias no necesita ni la libreria ni los 250 MB de PDF.
Para correrlos:

    pip install -r requirements-dev.txt
    pytest -m pdf

QUE HACER SI UNO FALLA, y no es editar el test. Si falla T0, el PDF cambio y
CADUCAN TODAS LAS CITAS DE ESA FUENTE a la vez: hay que reverificarlas, no
actualizar el sha1. Si falla T2, T3 o T5, la cita dice algo que su pagina no
dice: se corrige la CITA. Si falla T6, la pagina PDF declarada no es la que la
regla de paginacion predice: o la pagina esta mal o la regla lo esta, y
averiguar cual es el trabajo.
"""

from pathlib import Path

import pytest

from normativa import registro as _registro
from normativa.esquema import (
    SinDeterminar,
    Verbatim,
    esta_por_transcribir,
)
from normativa.extraccion import (
    PDF_NO_DISPONIBLE,
    aparece_en_pagina,
    normalizar,
    numero_de_paginas,
    pymupdf_disponible,
    sha1_de,
    texto_de_pagina,
)

RAIZ = Path(__file__).resolve().parents[1]

pytestmark = [
    pytest.mark.pdf,
    pytest.mark.skipif(not pymupdf_disponible(), reason=PDF_NO_DISPONIBLE),
]


@pytest.fixture(scope="module")
def reg():
    return _registro.construir()


def _ruta(fuente) -> Path:
    return RAIZ / fuente.archivo_pdf


def _citas_verificables(reg):
    """Las que tienen fuente presente, pagina PDF y texto literal leidos."""
    for c in reg.citas:
        f = reg.fuente(c.fuente_id)
        if f.ausente or not _ruta(f).exists():
            continue
        if esta_por_transcribir(c.pagina_pdf):
            continue
        yield c, f


# ===========================================================================
# T0 - el sha1 de cada PDF coincide con el declarado
# ===========================================================================

def test_T0_el_sha1_de_cada_fuente_coincide_con_el_PDF(reg):
    """
    SI ESTE TEST FALLA, NO FALLA «UN TEST»: CADUCAN TODAS LAS CITAS DE ESA
    FUENTE. Un `Verificado` dice «esta frase esta en la pagina N del archivo
    con este sha1»; si el archivo cambio, la afirmacion ya no se sostiene
    aunque siga escrita. Por eso el mensaje lista cuantas citas quedan sin
    respaldo, y por eso el arreglo NO es actualizar el sha1: es reverificar.
    """
    caducadas = []
    for f in reg.fuentes:
        ruta = _ruta(f)
        if not ruta.exists():
            pytest.skip(f"falta {f.archivo_pdf}")
        real = sha1_de(ruta)
        if real != f.sha1:
            caducadas.append(
                f"{f.id}: declarado {f.sha1}, real {real} — caducan "
                f"{len(reg.citas_de(f.id))} citas")
    assert not caducadas, (
        "PDF cambiados; las citas que se apoyan en ellos dejan de estar "
        "verificadas:\n  " + "\n  ".join(caducadas))


def test_T0_el_numero_de_paginas_declarado_es_el_real(reg):
    """
    Barato y acota `pagina_pdf` sin abrir la pagina: una cita a la pagina 400
    de un PDF de 323 no puede ser cierta.
    """
    for f in reg.fuentes:
        ruta = _ruta(f)
        if not ruta.exists():
            pytest.skip(f"falta {f.archivo_pdf}")
        assert numero_de_paginas(ruta) == f.paginas_pdf, f.id


def test_T0_ninguna_cita_apunta_fuera_del_PDF(reg):
    for c, f in _citas_verificables(reg):
        assert 1 <= c.pagina_pdf <= f.paginas_pdf, (
            f"{c.id}: pagina {c.pagina_pdf} en un PDF de {f.paginas_pdf}")


# ===========================================================================
# T2 - el texto literal aparece de verdad en esa pagina
# ===========================================================================

def test_T2_el_texto_literal_de_cada_cita_esta_en_su_pagina(reg):
    """
    LA CITA QUE DICE LO QUE LA PAGINA NO DICE. Es el test que ya trabajo
    mientras se escribia este registro: rechazo dos citas cuyo texto no estaba
    donde decian -- una de ellas venia del propio informe de verificacion -- y
    reubico el Cuadro 4.11 del Manual de Suelos en su pagina real.

    La comparacion es sobre texto NORMALIZADO: minusculas, sin diacriticos,
    espacios colapsados y coma decimal == punto decimal. Esa ultima
    equivalencia no es cosmetica -- E.060 imprime «2,0 %» y el codigo escribe
    2.00 --; sin ella habria falsos negativos en todo el corpus peruano.
    """
    fallos = []
    for c, f in _citas_verificables(reg):
        if not f.texto_extraible:
            continue        # se verifico por imagen; ver T2-bis
        t = c.texto_literal
        if not isinstance(t, Verbatim) or esta_por_transcribir(t.pagina_pdf):
            continue
        if not aparece_en_pagina(_ruta(f), t.pagina_pdf, t.texto):
            fallos.append(f"{c.id}: su texto literal no aparece en la pagina "
                          f"PDF {t.pagina_pdf} de {f.id}")
    assert not fallos, "\n  ".join(("citas que su pagina no sostiene:", *fallos))


def test_T2_una_cita_a_una_fuente_sin_texto_se_verifico_por_imagen(reg):
    """
    Tres de las trece fuentes no entregan texto utilizable, y eso es una
    propiedad DE LA FUENTE. Una cita suya verificada «por texto» seria una
    verificacion imposible: el campo `metodo` obliga a decir cual de las dos.
    """
    from normativa.esquema import MetodoDeVerificacion
    for c, f in _citas_verificables(reg):
        if f.texto_extraible or c.verificado is None:
            continue
        assert c.verificado.metodo is not MetodoDeVerificacion.TEXTO, (
            f"{c.id}: {f.id} no entrega texto utilizable y la cita dice "
            "haberse verificado por texto")


# ===========================================================================
# T3 - el titulo del numeral aparece junto a su numeral
# ===========================================================================

def test_T3_el_titulo_de_cada_numeral_esta_en_la_pagina_que_lo_imprime(reg):
    """
    **EL TEST DE `NOR-PUE-01`.** `titulo_numeral` es obligatorio y verbatim, y
    ese es el campo que hace que una cita falsa se caiga sola: quien la rellene
    tiene que abrir la pagina y copiar el encabezado -- y entonces lee
    «Aparatos de Apoyo».

    Se busca en `pagina_del_titulo`, que no siempre es la del valor: el num.
    4.1.1.3.6 abre en la pag. impresa 74 y su Tabla Nº 10 esta en la 76. Sin
    ese campo, el test fallaria en toda cita cuyo numeral abarque mas de una
    pagina, que son casi todas.
    """
    fallos = []
    for c, f in _citas_verificables(reg):
        if not f.texto_extraible or esta_por_transcribir(c.titulo_numeral):
            continue
        pagina = c.pagina_del_titulo
        if esta_por_transcribir(pagina):
            continue
        if not aparece_en_pagina(_ruta(f), pagina, c.titulo_numeral):
            fallos.append(f"{c.id}: el titulo «{c.titulo_numeral}» no aparece "
                          f"en la pagina PDF {pagina} de {f.id}")
    assert not fallos, "\n  ".join(("titulos que su pagina no imprime:", *fallos))


def test_T3_la_jerarquia_de_encabezados_tambien_es_literal(reg):
    """
    Los encabezados de los que cuelga una cita son texto de la fuente, no
    composicion del proyecto, y por eso tienen que poder encontrarse. Se
    buscan hacia atras desde la pagina del titulo: un encabezado padre esta,
    por definicion, antes.
    """
    ventana = 40   # literal-ok: paginas hacia atras en que se busca el padre
    fallos = []
    for c, f in _citas_verificables(reg):
        if not f.texto_extraible or esta_por_transcribir(c.pagina_del_titulo):
            continue
        for j in c.jerarquia_numeral:
            desde = max(1, c.pagina_del_titulo - ventana)
            if not any(aparece_en_pagina(_ruta(f), p, j)
                       for p in range(desde, c.pagina_del_titulo + 1)):
                fallos.append(f"{c.id}: el encabezado padre «{j}» no aparece "
                              f"en las {ventana} paginas anteriores")
    assert not fallos, "\n  ".join(("jerarquia no literal:", *fallos))


# ===========================================================================
# T5 - el valor que la cita sostiene esta en su texto literal
# ===========================================================================

# Los valores que cada cita tiene que sostener, y de donde salen. La lista es
# EXPLICITA a proposito: deducir «el valor» de una cita exigiria que la cita
# supiera que constante alimenta, y eso invertiria la direccion de las
# dependencias. Aqui el test declara el par y comprueba.
#
# ES EL TEST DE LA CAUSA RAIZ DE C11 -- «atribuciones de valores a numerales
# que no los escriben» --, y por eso incluye tambien los dos casos NEGATIVOS:
# el numeral que NO escribe el 9.8 y el que NO escribe el 0.60.
VALORES_QUE_LA_CITA_SOSTIENE = [
    ("MC_HHD.4.1.1.3.1", "6.0"),
    ("MC_HHD.4.1.1.5.1", "6.0"),
    ("MC_HHD.4.1.1.3.4a", "0.90"),
    ("MC_HHD.4.1.1.3.6#VMIN", "0.25"),
    ("MC_HHD.4.1.1.3.7b", "25 %"),
    ("MC_HHD.4.1.2.1d", "250"),
    ("MC_HHD.4.1.2.1d", "200"),
    ("MC_HHD.3.12.5#G", "9.8"),
    ("MC_HHD.4.1.1.5.4b24#G", "9.8"),
    ("MP.2.4.2.2#SOBRECARGA", "0.60"),
    ("MS.4.2", "1.5 m"),
    ("MS.3.2.1", "90%"),
    ("MS.3.2.1", "95%"),
    ("MS.3.3", "6%"),
    ("MS.9.1.1", "6%"),
    ("MS.4.5.4", "0.60"),
    ("MS.4.5.4", "1.20"),
    ("AASHTO_LRFD_9.3.11.6.4#ALTURA", "bottom of the footing"),
]

# Y los dos que la cita NO puede sostener, que son el hallazgo.
VALORES_QUE_LA_CITA_NO_ESCRIBE = [
    ("MC_HHD.4.1.1.3.7c#G", "9.8",
     "NOR-HID-01 / MAT-O7: el numeral de Laushey define g SIN numero"),
    ("MP.2.1.4.3.9", "0.60",
     "NOR-PUE-01 / MAT-D5: «Aparatos de Apoyo» no habla de sobrecarga"),
]


@pytest.mark.parametrize("cita_id,valor", VALORES_QUE_LA_CITA_SOSTIENE)
def test_T5_el_valor_esta_en_el_texto_literal_de_su_cita(reg, cita_id, valor):
    c = reg.cita(cita_id)
    t = c.texto_literal
    assert isinstance(t, Verbatim)
    assert normalizar(valor) in normalizar(t.texto), (
        f"{cita_id} sostiene el valor {valor!r} y su texto literal no lo "
        "contiene. O la cita es de otro numeral, o el valor no sale de ahi")


@pytest.mark.parametrize("cita_id,valor,por_que", VALORES_QUE_LA_CITA_NO_ESCRIBE)
def test_T5_los_dos_numerales_que_NO_escriben_su_valor(reg, cita_id, valor,
                                                       por_que):
    """
    El reverso de T5, y es donde vive el hallazgo. Si algun dia uno de estos
    dos textos SI contuviera el valor, seria que alguien cambio la cita por
    otra -- y este test lo diria en vez de dejar que la correccion se
    revirtiera en silencio.
    """
    c = reg.cita(cita_id)
    assert normalizar(valor) not in normalizar(c.texto_literal.texto), por_que


def test_T5_el_numeral_de_Laushey_no_escribe_ningun_valor_de_g_en_su_pagina(reg):
    """
    Mas fuerte que el anterior: no es que el TEXTO TRANSCRITO no lo tenga, es
    que LA PAGINA ENTERA no lo tiene. Se comprueba contra el PDF, que es lo
    unico que zanja una atribucion.
    """
    c = reg.cita("MC_HHD.4.1.1.3.7c#G")
    f = reg.fuente(c.fuente_id)
    if not _ruta(f).exists():
        pytest.skip("falta el PDF")
    pagina = normalizar(texto_de_pagina(_ruta(f), c.pagina_pdf))
    assert "9.8" not in pagina and "9.81" not in pagina, (
        "la pagina impresa 80 del Manual de Hidrologia contiene un valor de "
        "gravedad: revisa NOR-HID-01, porque la correccion se apoya en que no "
        "lo contiene")


def test_T5_el_numeral_de_aparatos_de_apoyo_no_habla_de_sobrecarga(reg):
    """El mismo, para NOR-PUE-01, y sobre la pagina entera."""
    c = reg.cita("MP.2.1.4.3.9")
    f = reg.fuente(c.fuente_id)
    if not _ruta(f).exists():
        pytest.skip("falta el PDF")
    pagina = normalizar(texto_de_pagina(_ruta(f), c.pagina_pdf))
    assert "relleno equivalente" not in pagina, (
        "la pagina impresa 91 del Manual de Puentes habla de relleno "
        "equivalente: revisa NOR-PUE-01")


# ===========================================================================
# T6 - la pagina PDF es la que predice la paginacion
# ===========================================================================

def test_T6_la_pagina_pdf_es_la_que_predice_la_regla_de_paginacion(reg):
    """
    **EL TEST DE `MAT-O17`**, y lo cierra POR CONSTRUCCION en vez de pagina a
    pagina. El desfase deja de ser documentacion y pasa a ser una PREDICCION
    testeable: dada la `Paginacion` de la fuente, la `pagina_pdf` que la cita
    declara tiene que ser la que la regla calcula desde la `pagina_impresa`.

    Una pagina corrida -- 76 por 77, C.2 por C.6, 982 por 984 -- deja de poder
    entrar sin que algo falle.
    """
    fallos = []
    for c, f in _citas_verificables(reg):
        if isinstance(f.paginacion, SinDeterminar):
            continue
        predicha = f.paginacion.pagina_pdf(c.pagina_impresa)
        if predicha is None:
            fallos.append(f"{c.id}: la paginacion de {f.id} no sabe traducir "
                          f"la pagina impresa «{c.pagina_impresa}»")
        elif predicha != c.pagina_pdf:
            fallos.append(f"{c.id}: declara PDF {c.pagina_pdf} y la regla de "
                          f"{f.id} predice {predicha} desde la impresa "
                          f"«{c.pagina_impresa}»")
    assert not fallos, "\n  ".join(("paginas que la regla no predice:", *fallos))


def test_T6_ninguna_cita_a_una_fuente_sin_paginacion_declara_pagina_pdf(reg):
    """
    `SinDeterminar` no es un hueco del esquema: es el estado real de una
    fuente que no se ha medido, y una cita suya no puede fingir una pagina PDF
    que nadie calculo.
    """
    for c in reg.citas:
        f = reg.fuente(c.fuente_id)
        if isinstance(f.paginacion, SinDeterminar) and not f.ausente:
            assert esta_por_transcribir(c.pagina_pdf) or c.verificado is None, (
                f"{c.id}: {f.id} no tiene paginacion medida y la cita declara "
                "pagina PDF verificada")


def test_T6_la_pagina_del_titulo_tambien_cae_dentro_del_PDF(reg):
    for c, f in _citas_verificables(reg):
        p = c.pagina_del_titulo
        if esta_por_transcribir(p):
            continue
        assert 1 <= p <= f.paginas_pdf, f"{c.id}: titulo en la pagina {p}"
