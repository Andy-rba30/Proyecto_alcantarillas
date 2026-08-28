"""
Las fuentes normativas del proyecto: las trece que estan en `normas/` y las
once que se citan y NO estan (§8 del diseño, §15 del plan).

TODOS LOS SHA-1 Y TODAS LAS PAGINACIONES DE ESTE ARCHIVO ESTAN MEDIDOS, no
supuestos. El procedimiento, para que se pueda repetir:

    python3 -m src.normativa.extraccion sha1 <fragmento>
    python3 -m src.normativa.extraccion cabeceras <fragmento> <desde> <hasta>

Los desfases se midieron barriendo el documento ENTERO y contando cuantas
paginas confirman cada desfase, no dos o tres a ojo:

    Manual de Hidrologia .... +3   confirmado en 221 de 225 paginas
    Manual de Puentes ....... +1   confirmado en 650 de 673
    Manual de Suelos ........ +1   confirmado en 269 de 281
    EG-2013 ................. +8   confirmado en 1268 de 1282
    E.030 / E.050 / E.060 ...  0   confirmado en 67/68, 78/82 y 204/205
    HDS-5 3a ed ............. por capitulo; catorce bases medidas
    AASHTO LRFD 9a ed ....... por capitulo; quince bases medidas

Las paginas que no confirman son las que no imprimen numero -- portadas,
separadores y las laminas fotograficas del Manual de Puentes --, no
excepciones a la regla.

LO QUE MEDIR ESTO HIZO APARECER, y en prosa no se veia:

  1. El Manual de Hidrologia -- la fuente con MAS citas del proyecto, la que
     gobierna las Fases 2 a 6 -- no tenia declarada ni una sola pagina PDF. El
     diseño lo dejo como `SinDeterminar` porque «el desfase no se puede
     inferir de lo escrito y hay que medirlo abriendo el PDF». Se midio: es
     `Corrida(+3)`, y con eso sus citas pasan a ser verificables por la via
     barata.
  2. TRES de las trece fuentes NO ENTREGAN TEXTO UTILIZABLE, y eso es una
     propiedad de la fuente que el registro tiene que declarar, no un
     percance de quien la lee:
       - AASHTO M 36 es un raster sin capa de texto: `get_text()` devuelve
         cadena vacia en las 24 paginas.
       - ASTM A760/A760M-10 trae una codificacion de fuente sin ToUnicode: el
         volcado da «@esmkgbdmog» donde la pagina imprime «Designacion». No es
         un cifrado uniforme (los digitos tampoco se corresponden), de modo
         que no se puede deshacer.
       - AASHTO M 170M-04 es un escaneo con OCR de mala calidad
         («Speciñcation», «Rcinforcc»), util para orientarse y no para citar.
     Una cita a esas tres se verifica RENDERIZANDO la pagina o no se verifica:
     `Verificado.metodo` obliga a decir cual de las dos.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .esquema import (
    Ausencia,
    Catalogo,
    Corrida,
    Esfuerzo,
    Fuente,
    Irregular,
    PorCapitulo,
    SinDeterminar,
)

# ===========================================================================
# Las trece fuentes que SI estan en normas/
# ===========================================================================

MC_HHD = Fuente(
    id="MC_HHD",
    titulo="Manual de Hidrologia, Hidraulica y Drenaje",
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="Version Libro",
    anio=2011,
    resolucion="RD 20-2011-MTC/14",
    archivo_pdf="normas/Hidrología, Hidráulica y Drenaje (Versión Libro).pdf",
    sha1="a31e853b8171b931863d7afa4379bbbc57cacb0d",
    paginas_pdf=225,
    paginacion=Corrida(desfase=3),
    nota=("El diseño la dejo en SinDeterminar porque ninguna cita del "
          "repositorio declaraba su pagina PDF. Medido en S12: +3, "
          "confirmado en 221 de sus 225 paginas."),
)

MP = Fuente(
    id="MP",
    titulo="Manual de Puentes",
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="Version Libro",
    anio=2016,
    resolucion="RD 19-2018-MTC/14",
    archivo_pdf="normas/Puentes (Versión Libro).pdf",
    sha1="67a7a9f1c61cad8f9ca179cd4ca777f96b49dc44",
    paginas_pdf=673,
    paginacion=Corrida(desfase=1),
    nota=("23 de sus 673 paginas no imprimen numero: son portadas de capitulo "
          "y laminas fotograficas de puentes. El desfase no cambia."),
)

MS = Fuente(
    id="MS",
    titulo=("Manual de Carreteras: Suelos, Geologia, Geotecnia y Pavimentos — "
            "Seccion Suelos y Pavimentos"),
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="Version abril 2014",
    anio=2014,
    resolucion="RD 10-2014-MTC/14",
    archivo_pdf=("normas/Suelos, Geologia y Pavimentos Sección Suelos y "
                 "Pavimentos (Versión Libro).pdf"),
    sha1="21d19a71090c1e586cd31596db8a4d007dc7b96f",
    paginas_pdf=281,
    paginacion=Corrida(desfase=1),
)

EG2013 = Fuente(
    id="EG2013",
    titulo=('Manual de Carreteras "Especificaciones Tecnicas Generales para '
            'Construccion" (EG-2013)'),
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="Version revisada y corregida a junio 2013",
    anio=2013,
    resolucion="RD 03-2013-MTC/14 (MC-01-13)",
    archivo_pdf=("normas/MC-01-13 Especificaciones Tecnicas Generales para "
                 "Construcción - EG-2013 - (Versión Revisada - JULIO 2013).pdf"),
    sha1="e35681d06b13226744324bc6b242b608ca9fa3ba",
    paginas_pdf=1282,
    paginacion=Corrida(desfase=8),
    nota=("El desfase de 8 es grande y por eso es la fuente donde mas facil "
          "es citar una pagina corrida: la impresa 976 es la PDF 984, y "
          "confundir las dos es exactamente el hallazgo NOR-EG-01."),
)

E030 = Fuente(
    id="E030",
    titulo="Norma Tecnica E.030 «Diseño Sismorresistente»",
    emisor="SENCICO / Ministerio de Vivienda, Construccion y Saneamiento",
    edicion="Edicion 2026, publicada en el diario oficial El Peruano",
    anio=2026,
    resolucion="RM 183-2026-VIVIENDA",
    archivo_pdf="normas/Norma E.030 Diseño sismorresistente (2026).pdf",
    sha1="fe0a58e4be4b8709324e65ed6ad0c25b8e0b6899",
    paginas_pdf=68,
    paginacion=Corrida(desfase=0),
    reemplaza_a="E.030 (2018)",
)

E050 = Fuente(
    id="E050",
    titulo="Norma Tecnica E.050 «Suelos y Cimentaciones»",
    emisor="SENCICO / Ministerio de Vivienda, Construccion y Saneamiento",
    edicion="Edicion 2018",
    anio=2018,
    resolucion="RM 406-2018-VIVIENDA",
    archivo_pdf="normas/Norma E.050 Suelos y cimentaciones.pdf",
    sha1="5fac1ecd997a6d6e80bcbf0967f89f9ddcc8106c",
    paginas_pdf=82,
    paginacion=Corrida(desfase=0),
)

E060 = Fuente(
    id="E060",
    titulo="Norma Tecnica E.060 «Concreto Armado»",
    emisor="SENCICO / Ministerio de Vivienda, Construccion y Saneamiento",
    edicion="Edicion 2009",
    anio=2009,
    resolucion="DS 010-2009-VIVIENDA",
    archivo_pdf="normas/Norma E.060 Concreto armado.pdf",
    sha1="cffe0efffc767f5d06a33e1f4eed3a16a01bdd81",
    paginas_pdf=205,
    paginacion=Corrida(desfase=0),
)

HDS5_3ED = Fuente(
    id="HDS5_3ED",
    titulo=("HDS-5 «Hydraulic Design of Highway Culverts» "
            "(FHWA-HIF-12-026)"),
    emisor="FHWA — Federal Highway Administration",
    edicion="Third Edition, April 2012",
    anio=2012,
    archivo_pdf="normas/hif12026.pdf",
    sha1="7b985e047c615b765e7c41b6ff12df0505c02ce4",
    paginas_pdf=323,
    # Catorce bases medidas barriendo el documento entero. Las etiquetas
    # "3.24", "A.8" y "DG3.3" son ETIQUETAS, no numeros: "3.24" no es 3,24.
    paginacion=PorCapitulo(base={
        "1": 38, "2": 62, "3": 82, "4": 126, "5": 136, "6": 162, "7": 181,
        "A": 189, "B": 202, "C": 210,
        "DG1": 271, "DG2": 285, "DG3": 293, "DG4": 312,
    }),
    convive_con=("HDS5_SI_1985",),
    nota=("Es la edicion que gobierna: es la unica de las dos que imprime las "
          "conversiones SI (19.63 y 1.811)."),
)

HDS5_SI_1985 = Fuente(
    id="HDS5_SI_1985",
    titulo=("HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-IP-85-15), "
            "copia rotulada «SI» por sus cartas metricas"),
    emisor="FHWA — Federal Highway Administration",
    edicion="September 1985",
    anio=1985,
    archivo_pdf="normas/fhwa_culvert_hydraulics_hds5si.pdf",
    sha1="59c6623c78793f7f947b7095027096b86f88ddf0",
    paginas_pdf=410,
    paginacion=SinDeterminar(
        por_que=("la copia no imprime numeros de pagina propios: es una "
                 "conversion a PDF de la version HTML del documento, y sus "
                 "410 paginas no llevan cabecera ni pie numerado. Sus citas "
                 "se localizan por pagina PDF y no tienen pagina impresa que "
                 "declarar")),
    convive_con=("HDS5_3ED",),
    nota=("PESE AL «si» DEL NOMBRE DEL ARCHIVO, opera en unidades inglesas "
          "con rotulos duales «ft (m)»: sus ecs. (4b) y (5) imprimen 29 y no "
          "19.63. Leerla literal «en SI» reproduce el error de +9.6 % que "
          "K_FRICCION_SI existe para atrapar. Ver la Discrepancia "
          "DIS-HDS5-EDICIONES."),
)

AASHTO_LRFD_9 = Fuente(
    id="AASHTO_LRFD_9",
    titulo="AASHTO LRFD Bridge Design Specifications",
    emisor="AASHTO — American Association of State Highway and "
           "Transportation Officials",
    edicion="Ninth Edition, 2020",
    anio=2020,
    archivo_pdf=("normas/AASHTO.LRFD.Bridge.Design.Specifications_9th."
                 "Edition.2020.pdf"),
    sha1="71f4ced4c80f58db75a0bcdf4ac6b5d86dc0f858",
    paginas_pdf=1905,
    paginacion=PorCapitulo(base={
        "1": 15, "2": 24, "3": 54, "4": 251, "5": 359, "6": 706, "7": 1134,
        "8": 1197, "9": 1239, "10": 1289, "11": 1469, "12": 1638, "13": 1750,
        "14": 1782, "15": 1872,
    }),
)

AASHTO_M170M = Fuente(
    id="AASHTO_M170M",
    titulo=("AASHTO M 170M-04 «Standard Specification for Reinforced Concrete "
            "Culvert, Storm Drain, and Sewer Pipe [Metric]»"),
    emisor="AASHTO",
    edicion="M 170M-04",
    anio=2004,
    archivo_pdf=("normas/AASHTO M 170M-04 Reinforced Concrete Culvert, Storm "
                 "Drain, and Sewer Pipe.pdf"),
    sha1="dcc40c0e5e9c99ad9f18490fa8c5b2d9394faa51",
    paginas_pdf=23,
    # Las paginas se rotulan "M 170M-1", "M 170M-2"...: es una etiqueta con
    # prefijo, no un entero, aunque la base sea 0.
    paginacion=PorCapitulo(base={"M 170M": 0}, separadores=("-",)),
    texto_extraible=False,
    nota=("Escaneo con OCR de mala calidad: el volcado devuelve «Speciñcation» "
          "y «Rcinforcc». Sirve para orientarse; para CITAR hay que renderizar "
          "la pagina y leerla."),
)

AASHTO_M36 = Fuente(
    id="AASHTO_M36",
    titulo=("AASHTO M 36 «Corrugated Steel Pipe, Metallic-Coated, for Sewers "
            "and Drains»"),
    emisor="AASHTO",
    edicion="M 36",
    anio=2006,
    archivo_pdf=("normas/AASHTO M 36 Corrugated Steel Pipe, Metallic-Coated, "
                 "for Sewers and Drains.pdf"),
    sha1="f85b5658385ae6779dde4e5fd340ac3122b62636",
    paginas_pdf=24,
    paginacion=SinDeterminar(
        por_que=("el PDF es un raster SIN capa de texto: la extraccion "
                 "devuelve cadena vacia en las 24 paginas, de modo que no hay "
                 "cabecera que leer para medir el desfase. Se localiza "
                 "renderizando")),
    texto_extraible=False,
)

ASTM_A760 = Fuente(
    id="ASTM_A760",
    titulo=("ASTM A760/A760M-10 «Especificacion Estandar para Tuberia de "
            "Acero Corrugado, con Recubrimiento Metalico, para Alcantarillas "
            "y Drenajes»"),
    emisor="ASTM International",
    edicion="A760/A760M-10",
    anio=2010,
    archivo_pdf=("normas/ASTM A760-A760M-10 Corrugated Steel Pipe, "
                 "Metallic-Coated for Sewers and Drains.pdf"),
    sha1="47d0d447143ca158615dff7dec79f2f7a8975732",
    paginas_pdf=15,
    paginacion=SinDeterminar(
        por_que=("el PDF trae una codificacion de fuente sin tabla ToUnicode: "
                 "el volcado devuelve «@esmkgbdmog» donde la pagina imprime "
                 "«Designacion», y la sustitucion no es uniforme ni siquiera "
                 "en los digitos, de modo que no se puede deshacer. Tampoco "
                 "se puede leer el numero de pagina. Se localiza renderizando")),
    texto_extraible=False,
)


FUENTES: Dict[str, Fuente] = {
    f.id: f for f in (
        MC_HHD, MP, MS, EG2013, E030, E050, E060,
        HDS5_3ED, HDS5_SI_1985, AASHTO_LRFD_9,
        AASHTO_M170M, AASHTO_M36, ASTM_A760,
    )
}


# ===========================================================================
# §8 / §15 - Las fuentes que se citan y NO estan en normas/
# ===========================================================================
# Cuatro invariantes que el tipo impone y que aqui se ven en acto:
#   1. archivo_pdf = None y sha1 = None. No hay contra que verificar.
#   2. Ninguna Cita a una de estas lleva texto_literal ni pagina_pdf: se cita
#      EL DOCUMENTO, no una pagina suya. Es lo que impide estructuralmente una
#      cita como «WSDOT Hydraulics Manual (M 23-03.12, abril 2026)» con pagina
#      y frase que nadie abrio.
#   3. Una fuente ausente NO puede sostener un [N] (T17). Es la definicion
#      misma de [N] en CLAUDE.md: numeral VERIFICADO.
#   4. `que_desbloquearia` convierte la deuda en trabajo con precio.

FUENTES_AUSENTES: Dict[str, Fuente] = {}


def _ausente(id_, titulo, emisor, edicion, anio, ausencia, **kw) -> Fuente:
    f = Fuente(id=id_, titulo=titulo, emisor=emisor, edicion=edicion,
               anio=anio, ausente=True, ausencia=ausencia,
               paginacion=SinDeterminar(por_que="la fuente no esta en normas/"),
               **kw)
    FUENTES_AUSENTES[id_] = f
    return f


ASTM_A796 = _ausente(
    "ASTM_A796",
    "ASTM A796/A796M «Structural Design of Corrugated Steel Pipe...»",
    "ASTM International", "A796/A796M", 2019,
    Ausencia(
        por_que_se_cita=("es la norma que da el calibre de la plancha por "
                         "altura de cobertura, que es la mitad TMC del "
                         "criterio 'clases_producto_por_relleno'"),
        que_desbloquearia=("la mitad TMC de 'clases_producto_por_relleno'. "
                           "Es una de las DOS ausencias baratas del plan"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente="el criterio queda [A] y declara el vacio"))

AASHTO_M294 = _ausente(
    "AASHTO_M294",
    "AASHTO M 294 «Corrugated Polyethylene Pipe, 300- to 1500-mm Diameter»",
    "AASHTO", "M 294", 2020,
    Ausencia(
        por_que_se_cita="el tope de diametro del HDPE se le atribuia",
        que_desbloquearia=("D_max['hdpe']: hoy es tope de CATALOGO ([A], "
                           "criterio 'D_max_catalogo') porque la norma que lo "
                           "sostendria no esta. La otra ausencia barata"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente="Catalogo CAT_TUBERIA_LOCAL, rotulado como tal"))

ASTM_C76 = _ausente(
    "ASTM_C76", "ASTM C76 «Reinforced Concrete Culvert, Storm Drain, and "
    "Sewer Pipe»", "ASTM International", "C76", 2020,
    Ausencia(
        por_que_se_cita="se citaba como sustento del tope de 2.70 m del concreto",
        que_desbloquearia=("nada nuevo: AASHTO M 170M-04, que SI esta, tabula "
                           "de 300 a 3600 mm y ya desmiente el tope"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente="AASHTO M 170M-04, presente en normas/"))

ASTM_A798 = _ausente(
    "ASTM_A798", "ASTM A798/A798M «Installing Factory-Made Corrugated Steel "
    "Pipe for Sewers and Other Applications»", "ASTM International",
    "A798/A798M", 2019,
    Ausencia(
        por_que_se_cita="practica de instalacion de TMC",
        que_desbloquearia="nada que el EG-2013 no cubra ya para obra vial peruana",
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente="EG-2013 Seccion 507"))

ASTM_A807 = _ausente(
    "ASTM_A807", "ASTM A-807 (la designacion que la hoja de ruta atribuye al "
    "calibre de TMC por altura de relleno)", "ASTM International", "A-807", 0,
    Ausencia(
        por_que_se_cita=("la hoja de ruta v8 la cita dos veces (Sec. 7.A y "
                         "Fase 8) para el calibre de TMC segun altura"),
        que_desbloquearia=("nada: la remision es FALSA. El calibre por altura "
                           "de cobertura es de ASTM A796/A796M. Queda "
                           "declarada como discrepancia abierta contra la "
                           "hoja de ruta"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente="ninguno; la remision se retira, no se sustituye"))

WSDOT_HM = _ausente(
    "WSDOT_HM", "WSDOT Hydraulics Manual", "Washington State DOT",
    "M 23-03", 2019,
    Ausencia(
        por_que_se_cita=("es la fuente tecnica con que se cubren los techos "
                         "de velocidad de TMC y HDPE, que la Tabla N 10 del "
                         "Manual no lista"),
        que_desbloquearia="'v_max_tmc' y 'v_max_hdpe', hoy [C] sin PDF",
        esfuerzo=Esfuerzo.DESCARGA_PUBLICA,
        sustituto_vigente=("los dos criterios siguen [C] y la ventana los "
                           "rotula «fuente no disponible en el expediente»")))

DG2018 = _ausente(
    "DG2018", "Manual de Carreteras: Diseño Geometrico DG-2018",
    "MTC", "DG-2018", 2018,
    Ausencia(
        por_que_se_cita=("clasifica las carreteras por IMDA y por numero de "
                         "carriles, que es justo el dato que condiciona el "
                         "Cuadro 4.1 del Manual de Suelos"),
        que_desbloquearia=("'clase_de_via' y con ella "
                           "'carriles_por_sentido': hoy el Cuadro 4.1 no se "
                           "puede aplicar sin declararlos"),
        esfuerzo=Esfuerzo.DESCARGA_PUBLICA,
        sustituto_vigente="datos de sitio declarados por el proyectista"))

HEC14 = _ausente(
    "HEC14", "HEC-14 «Hydraulic Design of Energy Dissipators for Culverts "
    "and Channels»", "FHWA", "Third Edition", 2006,
    Ausencia(
        por_que_se_cita="disipadores de energia a la salida",
        que_desbloquearia="el dimensionamiento de disipadores, fuera de alcance hoy",
        esfuerzo=Esfuerzo.DESCARGA_PUBLICA,
        sustituto_vigente="Laushey (num. 4.1.1.3.7 c) del Manual) para d50"))

LEY_29338 = _ausente(
    "LEY_29338", "Ley 29338, Ley de Recursos Hidricos, y su reglamento",
    "Congreso de la Republica del Peru", "Ley 29338", 2009,
    Ausencia(
        por_que_se_cita="faja marginal y autorizacion de obras en cauce",
        que_desbloquearia="el tramite, no el calculo",
        esfuerzo=Esfuerzo.DESCARGA_PUBLICA,
        sustituto_vigente=None))

SERIES_SENAMHI_ANA = _ausente(
    "SERIES_SENAMHI_ANA", "Series hidrometeorologicas SENAMHI / ANA para la "
    "cuenca del corredor", "SENAMHI / ANA", "series de estacion", 0,
    Ausencia(
        por_que_se_cita=("el Q de diseño de toda la Familia A depende de "
                         "ellas via 'homogeneidad_serie_fen'"),
        que_desbloquearia=("el Q de la Familia A, hoy bloqueado. Es la "
                           "ausencia mas cara del expediente"),
        esfuerzo=Esfuerzo.GABINETE,
        sustituto_vigente="ninguno: el calculo se detiene, y debe"))

MEYERHOF_1957 = _ausente(
    "MEYERHOF_1957", "Meyerhof, G. G. (1957), abacos de N_cq y N_gamma_q",
    "Meyerhof", "articulo original", 1957,
    Ausencia(
        por_que_se_cita="capacidad portante de zapata en talud",
        que_desbloquearia=("nada nuevo: los abacos SI estan, reproducidos en "
                           "el Manual de Puentes. Lo que no se puede es "
                           "leerlos por texto — son raster"),
        esfuerzo=Esfuerzo.GABINETE,
        sustituto_vigente=("Manual de Puentes num. 2.8.1.3.1.2c. NO es un "
                           "caso de fuente ausente sino de fuente presente "
                           "ilegible por texto: la lectura del abaco se "
                           "declara [S] y se verifica por imagen")))

ESTUDIO_GEOTECNICO = _ausente(
    "ESTUDIO_GEOTECNICO", "Estudio de Mecanica de Suelos (EMS) del expediente",
    "el proyectista", "por elaborar", 0,
    Ausencia(
        por_que_se_cita=("es la fuente de 'exposicion_quimica_ems', "
                         "'clase_sitio', 'PERFIL_SUELO_PRESUNTO' y del CBR "
                         "punto a punto"),
        que_desbloquearia=("toda la durabilidad del concreto (y con ella el "
                           "recubrimiento), la clase de sitio sismica y el "
                           "resguardo de la napa"),
        esfuerzo=Esfuerzo.CAMPO,
        sustituto_vigente="ninguno: los criterios valen None y bloquean"))

APENDICE_A3_MP = _ausente(
    "APENDICE_A3_MP", "Manual de Puentes, Apendice A3: mapas de isoaceleracion",
    "MTC", "Version Libro", 2016,
    Ausencia(
        por_que_se_cita="de ahi sale el PGA de roca del corredor",
        que_desbloquearia=("nada por la via de conseguirlo: el apendice SI "
                           "esta en el PDF. Lo que no se puede es leer la "
                           "isolinea por texto"),
        esfuerzo=Esfuerzo.GABINETE,
        sustituto_vigente=("datos_sitio['PGA_roca_B'], [S] con la lectura "
                           "del mapa declarada y verificable por imagen")))


# ===========================================================================
# Los catalogos, que NO son fuentes
# ===========================================================================
CAT_TUBERIA_LOCAL = Catalogo(
    id="CAT_TUBERIA_LOCAL",
    titulo="Catalogo de conductos disponibles para el corredor",
    proveedor_o_ambito=("oferta comercial y capacidad de transporte a la obra "
                        "(La Union, Piura)"),
    que_norma_NO_lo_sostiene=(
        "NINGUNA. Los topes 2.70 / 2.10 / 1.50 m se atribuian a «ASTM C76 / "
        "AASHTO M170», «AASHTO M36 / ASTM A760» y «AASHTO M294», y las dos "
        "primeras atribuciones estan verificadas EN CONTRA sobre los PDF de "
        "normas/: ASTM A760/A760M-10 tabula de 100 a 3600 mm y AASHTO "
        "M 170M-04 de 300 a 3600 mm con diseños especiales por encima. La "
        "tercera no se pudo contrastar porque M294 no esta. Un tope de "
        "catalogo no tiene numeral, y descartaba material en silencio con una "
        "cita que ninguna norma sostiene (NOR-PRO-01, NOR-PRO-02, MAT-O8)"),
)

CATALOGOS: Dict[str, Catalogo] = {CAT_TUBERIA_LOCAL.id: CAT_TUBERIA_LOCAL}


def fuente(id_fuente: str) -> Fuente:
    if id_fuente in FUENTES:
        return FUENTES[id_fuente]
    if id_fuente in FUENTES_AUSENTES:
        return FUENTES_AUSENTES[id_fuente]
    if id_fuente in CATALOGOS:
        raise KeyError(
            f"«{id_fuente}» es un Catalogo, no una Fuente. Un tope de catalogo "
            "no tiene numeral y no puede sostener una cita (T1)")
    raise KeyError(f"no hay fuente «{id_fuente}» en el registro")


def ausentes_por_esfuerzo() -> Tuple[Fuente, ...]:
    """
    Las ausentes ordenadas por lo que cuesta traerlas, para que la deuda se
    vea sin leer la §15 del plan.
    """
    orden = {e: i for i, e in enumerate(Esfuerzo)}
    return tuple(sorted(FUENTES_AUSENTES.values(),
                        key=lambda f: (orden[f.ausencia.esfuerzo], f.id)))
