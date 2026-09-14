"""
Las fuentes normativas del proyecto: las quince que estan en `normas/` y las
doce que se citan y NO estan (§8 del diseño, §15 del plan). Hasta N1 eran
trece y trece -- este encabezado decia «once» y llevaba tiempo sin contar:
el censo de ausentes tenia trece entradas --; ASTM A796/A796M-13 entro en
`normas/` en pre-N1 y N1 la paso del censo de ausentes a este. N2 sumo la
quinceava SIN restar del censo de ausentes, y no es un error de cuenta: lo
que entro en `normas/` es una TRADUCCION NO OFICIAL de AASHTO M 294-11
(`AASHTO_M294_TRAD`), y el original en ingles (`AASHTO_M294`) sigue ausente.
Una fuente derivada no sustituye a la primaria: convive con ella
(`convive_con` cruzado, el mismo recurso de las dos HDS-5) y la ausencia del
original queda redefinida como «que desbloquearia verificar contra el».

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
    ASTM A796/A796M-13 .....  0   confirmado en 20 de 21 (N1, por imagen:
                                  la PDF 1 esta en blanco)
    AASHTO M 294-11 (trad.) . SIN FOLIO: ninguna de sus 17 hojas imprime
                                  numero de pagina (N2, por texto en las 17
                                  y por imagen en la 1, la 5 y la 8)

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
  2. CUATRO de las quince fuentes NO ENTREGAN TEXTO UTILIZABLE, y eso es
     una propiedad de la fuente que el registro tiene que declarar, no un
     percance de quien la lee:
       - AASHTO M 36 es un raster sin capa de texto: `get_text()` devuelve
         cadena vacia en las 24 paginas.
       - ASTM A760/A760M-10 trae una codificacion de fuente sin ToUnicode: el
         volcado da «@esmkgbdmog» donde la pagina imprime «Designacion». No es
         un cifrado uniforme (los digitos tampoco se corresponden), de modo
         que no se puede deshacer.
       - AASHTO M 170M-04 es un escaneo con OCR de mala calidad
         («Speciñcation», «Rcinforcc»), util para orientarse y no para citar.
       - ASTM A796/A796M-13 (N1) trae la capa de texto DUPLICADA E
         INTERCALADA: cada renglon aparece dos veces y la segunda copia llega
         partida a mitad de palabra («Plac / Place e by / by Nuc / Nuclear»),
         de modo que una frase entera no se encuentra por texto aunque una
         palabra suelta si. Es artefacto del PDF (Ghostscript 9.26 sobre un
         ejemplar con dos capas), no de la norma.
     Una cita a esas cuatro se verifica RENDERIZANDO la pagina o no se
     verifica: `Verificado.metodo` obliga a decir cual de las dos.

LA VIGENCIA DE CADA EDICION SE VERIFICO EN T1 (2026-09-14) y vive en la
`nota` de cada Fuente presente, detras de una de las tres marcas de
`MARCAS_DE_VIGENCIA` (ver el bloque «T1» de abajo y `estado_de_vigencia`).
Es un metadato de la FUENTE, no de la cita: una cita verificada contra la
edicion que esta en normas/ sigue siendo valida contra ese PDF, porque el
sha1 la ancla. Lo que T1 midio, en resumen: siete ediciones confirmadas
vigentes, ocho con edicion posterior publicada por su emisor (una de ellas,
HDS-5 de 1985, ya modelada con `convive_con` y DIS-HDS5-EDICIONES), ninguna
indeterminable en linea. Que edicion rige el expediente en las siete con
eleccion pendiente NO lo decide el registro: es del proyectista, y esta
declarado vacio en `criterios_adoptados['edicion_que_rige_el_expediente']`.
Y una correccion que la verificacion hizo aparecer: la ficha del Manual de
Puentes citaba como resolucion la RD 19-2018-MTC/14, que es la de la edicion
POSTERIOR; el ejemplar imprime «R.D. N° 041-2016-MTC/14» en sus PDF 2 y 3.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from .esquema import (
    Ausencia,
    Catalogo,
    Corrida,
    ErrorDeRegistro,
    Esfuerzo,
    Fuente,
    Irregular,
    PorCapitulo,
    SinDeterminar,
)

# ===========================================================================
# T1 - Vigencia de las ediciones citadas (verificada el 2026-09-14)
# ===========================================================================
# POR QUE ES UNA MARCA EN LA NOTA Y NO UN CAMPO. El esquema no tiene donde
# poner «el emisor publica hoy una edicion posterior a la citada»: `reemplaza_a`
# mira hacia ATRAS (lo que ESTA fuente sustituye), `convive_con` exige que la
# otra Fuente exista en el registro, y `Discrepancia` obliga a declarar
# `gana`, que aqui seria decidir por el proyectista. T1 no fuerza ninguno de
# los tres: registra el hallazgo en `nota` detras de una marca fija, que
# `estado_de_vigencia` lee y un test comprueba en las quince presentes, y
# propone el campo `Fuente.vigencia` para una sesion de esquema (ficha
# T1-01 de docs/decisiones_diferidas.md). Mientras el campo no exista, la
# marca es lo que impide que esto sea prosa que nadie enumera.
#
# COMO SE VERIFICO, y es el limite que cada nota hereda: por busqueda web
# (WebSearch) sobre los resultados de las paginas del emisor y de los
# repositorios oficiales. Ninguna pagina fue LEGIBLE directamente desde el
# entorno de T1 --- el proxy de egress bloqueo gob.pe, el portal del MTC,
# busquedas.elperuano.pe, el sitio de SENCICO, los de la FHWA, AASHTO y
# ASTM, y los distribuidores de normas ---, de modo que cada confirmacion
# se apoya en lo que los resultados de busqueda transcriben de esas paginas,
# no en su lectura. Lo que eso deja para gabinete esta dicho en cada nota.
VIGENCIA_VERIFICADA_EL = "2026-09-14"
VIGENCIA_CONFIRMADA = "VIGENCIA CONFIRMADA " + VIGENCIA_VERIFICADA_EL
VIGENCIA_POSTERIOR = "EDICION POSTERIOR DETECTADA " + VIGENCIA_VERIFICADA_EL
VIGENCIA_GABINETE = ("VIGENCIA NO DETERMINABLE EN LINEA "
                     + VIGENCIA_VERIFICADA_EL)
MARCAS_DE_VIGENCIA: Tuple[str, ...] = (
    VIGENCIA_CONFIRMADA, VIGENCIA_POSTERIOR, VIGENCIA_GABINETE)
VIGENCIA_COMO = (
    "busqueda web (WebSearch) sobre resultados de las paginas del emisor y "
    "de repositorios oficiales; ninguna pagina fue legible directamente desde "
    "el entorno de T1 (egress bloqueado), de modo que la confirmacion es por "
    "lo que los resultados transcriben de esas paginas y no por su lectura")

# ===========================================================================
# Las quince fuentes que SI estan en normas/
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
          "confirmado en 221 de sus 225 paginas. "
          + VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): la RD "
          "20-2011-MTC/14 sigue publicada en gob.pe (MTC, normas legales "
          "4443017) como la que aprueba el Manual, y ninguna RD posterior del "
          "MTC sobre este Manual aparece en los resultados; las reediciones "
          "comerciales de 2026 (ICG, PT-55 «2.a ed.») declaran seguir la RD "
          "20-2011-MTC/14. Para gabinete: leer el listado de manuales del "
          "portal del MTC, que no fue legible."),
)

MP = Fuente(
    id="MP",
    titulo="Manual de Puentes",
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="Version Libro",
    anio=2016,
    # LO QUE EL EJEMPLAR IMPRIME, verificado por texto en T1: la PDF 2 dice
    # «"MANUAL DE PUENTES" R.D. N° 041-2016-MTC/14» y la PDF 3 «R.D. N°
    # 041-2016-MTC/14 ... 1ra Edicion, Lima 2016». Hasta T1 este campo decia
    # «RD 19-2018-MTC/14», que es la RD del Manual de Puentes ACTUALIZADO de
    # 2018 (630 paginas; este ejemplar tiene 673 PDF), o sea la de la edicion
    # POSTERIOR y no la de este archivo. Se corrige contra el PDF, que es la
    # fuente primaria; la edicion citada («Version Libro», 2016) no cambia.
    resolucion="RD 041-2016-MTC/14",
    archivo_pdf="normas/Puentes (Versión Libro).pdf",
    sha1="67a7a9f1c61cad8f9ca179cd4ca777f96b49dc44",
    paginas_pdf=673,
    paginacion=Corrida(desfase=1),
    nota=("23 de sus 673 paginas no imprimen numero: son portadas de capitulo "
          "y laminas fotograficas de puentes. El desfase no cambia. "
          + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): el MTC "
          "aprobo por RD 19-2018-MTC/14 (El Peruano, dispositivo 1730970-1; "
          "gob.pe, MTC, normas legales 4441255) un Manual de Puentes "
          "ACTUALIZADO de 630 paginas, vigente desde el 15-01-2019, que deja "
          "sin efecto la RD 041-2016-MTC/14 de este ejemplar y añade "
          "secciones (cimentaciones, barreras de sonido, analisis "
          "estructural). Este ejemplar es la edicion 2016: lo imprime en sus "
          "PDF 2 y 3, y por eso `resolucion` se corrigio en T1 (decia la RD "
          "de 2018). La edicion citada NO cambia y las citas siguen validas "
          "contra este archivo (sha1); cual rige el expediente es de "
          "'edicion_que_rige_el_expediente'. Para gabinete: conseguir la "
          "edicion 2018 y medir que numerales de los citados cambiaron."),
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
    nota=(VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): la RD "
          "10-2014-MTC/14 (El Peruano, 16-04-2014; gob.pe, MTC, normas legales "
          "4441297) sigue siendo la que aprueba la Seccion; el portal del MTC "
          "la mantiene en su carpeta de manuales de carreteras y el catalogo "
          "de SENCICO la registra como documento normativo de cumplimiento "
          "obligatorio (articulo 18 del Reglamento Nacional de Gestion de "
          "Infraestructura Vial). Ninguna RD posterior del MTC sobre esta "
          "Seccion en los resultados. Para gabinete: leer el listado de "
          "manuales del portal del MTC, que no fue legible."),
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
          "confundir las dos es exactamente el hallazgo NOR-EG-01. "
          + VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): no aparece "
          "en el MTC ninguna EG posterior a la EG-2013; el portal del MTC "
          "publica este mismo archivo («Version Revisada - JULIO 2013») en su "
          "carpeta de manuales de carreteras. PRECISION SOBRE LA RD, que "
          "queda para gabinete: el MTC aprobo la EG-2013 por RD 03-2013-MTC/14 "
          "(El Peruano, 16-02-2013) y su ACTUALIZACION por RD 22-2013-MTC/14 "
          "(El Peruano, 07-08-2013; gob.pe, MTC, normas legales 4438760), y el "
          "portal la publica junto a este archivo rotulada «Act EG-2013». Lo "
          "probable es que la version «Revisada y Corregida a Junio 2013» de "
          "este ejemplar sea la que la RD 22-2013 aprueba, y entonces "
          "`resolucion` deberia nombrarla; no se cambia en T1 porque el texto "
          "de esa RD no se pudo leer y el ejemplar no imprime ninguna RD en "
          "sus primeras paginas."),
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
    nota=(VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): la RM "
          "183-2026-VIVIENDA (El Peruano, separata especial del 03-05-2026, "
          "que es lo que la PDF 1 de este ejemplar imprime; gob.pe/vivienda "
          "normas legales 8081915) es la modificacion vigente de la E.030 y "
          "no hay edicion posterior del texto tecnico. HAY UNA RM POSTERIOR "
          "QUE NO ES UNA EDICION: la RM 217-2026-VIVIENDA (02-06-2026, El "
          "Peruano 03-06-2026, dispositivo 2521423-1; gob.pe/vivienda "
          "8219609) modifica la Unica Disposicion Complementaria Transitoria "
          "de la RM 183-2026 --- el ambito de los proyectos en curso que "
          "pueden seguir rigiendose por la version anterior de la norma ---. "
          "Su texto no se pudo leer desde el entorno de T1 y queda para "
          "gabinete: es la disposicion que dice si un expediente en curso "
          "puede quedarse en la E.030 de 2018, y este registro solo tiene la "
          "de 2026."),
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
    nota=(VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): la RM "
          "406-2018-VIVIENDA (30-11-2018; El Peruano, 03-12-2018) sigue siendo "
          "la ultima modificacion publicada de la E.050; ninguna RM posterior "
          "sobre la E.050 en los resultados de gob.pe/vivienda ni de El "
          "Peruano. Para gabinete: leer el indice del RNE en gob.pe (SENCICO), "
          "que no fue legible."),
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
    nota=(VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): la E.060 de "
          "2009 (DS 010-2009-VIVIENDA) sigue vigente sin modificacion "
          "publicada; este ejemplar es la «Primera edicion digital: Diciembre "
          "de 2020» de SENCICO (lo imprime la PDF 2), reedicion del mismo "
          "texto. ACTUALIZACION EN CURSO, NO PUBLICADA: la RM 066-2025-"
          "VIVIENDA (marzo de 2025; El Peruano, dispositivo 2377319-1; "
          "gob.pe/vivienda 6539836) creo el grupo de trabajo que elabora la "
          "propuesta de actualizacion de la E.060; a la fecha de T1 no aparece "
          "RM que apruebe una E.060 nueva. El dia que se publique, esta fuente "
          "pasa a «edicion posterior detectada» y entra en "
          "'edicion_que_rige_el_expediente'."),
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
          "conversiones SI (19.63 y 1.811). "
          + VIGENCIA_CONFIRMADA + " (T1, " + VIGENCIA_COMO + "): la "
          "biblioteca de hidraulica de la FHWA (library_arc.cfm, pub_number=7, "
          "id=13) lista HDS 5 Third Edition, FHWA-HIF-12-026 (2012), como la "
          "publicacion vigente, con descarga gratuita desde el sitio de la FHWA "
          "(engineering/hydraulics/pubs/12026/hif12026.pdf); no "
          "existe cuarta edicion."),
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
                 "conversion electronica del documento a HTML y de ahi a PDF, "
                 "y sus 410 paginas no llevan cabecera ni pie numerado. El "
                 "propio archivo lo declara en su frontispicio: «During the "
                 "editing of this manual for conversion to an electronic "
                 "format, the intent has been to keep the document text as "
                 "close to the original as possible. In the process of "
                 "scanning and converting, some changes may have been made "
                 "inadvertently». Sus citas se localizan por pagina PDF y no "
                 "tienen pagina impresa que declarar")),
    convive_con=("HDS5_3ED",),
    nota=("EL «si» DEL NOMBRE DEL ARCHIVO ES DEL REPOSITORIO, NO DEL "
          "DOCUMENTO, y conviene decirlo asi: la portada no se rotula «SI» ni "
          "«metric» en ninguna parte -- dice «September 1985» y "
          "«FHWA-IP-85-15» --; el unico «SI» del frontispicio es el enlace a "
          "una tabla anexa «U.S. - SI Conversions», y las laminas del "
          "Apendice D llevan rotulos «Metric Version» / «English Version». "
          "El cuerpo opera en unidades inglesas con rotulos duales «ft (m)»: "
          "sus ecs. (4b) y (5) imprimen 29 y no 19.63, y su gravedad es "
          "«32.2 ft/s/s (9.8 m/s/s)». Leerla literal «en SI» reproduce el "
          "error de +9.6 % que K_FRICCION_SI existe para atrapar. Ver la "
          "Discrepancia DIS-HDS5-EDICIONES. "
          + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "), Y YA "
          "MODELADA: es la edicion de 1985 que la tercera (2012, HDS5_3ED, "
          "presente en normas/) sustituye --- la FHWA la presenta como «the "
          "first major rewrite of HDS 5 since 1985» ---. El registro ya dice "
          "cual gobierna, con `convive_con` cruzado y DIS-HDS5-EDICIONES "
          "(resuelta: gana HDS5_3ED), y por eso NO entra en "
          "'edicion_que_rige_el_expediente': no hay nada que el proyectista "
          "tenga que elegir cuando la edicion vigente esta en normas/ y es la "
          "que gobierna. `fuentes_con_eleccion_de_edicion_pendiente` la "
          "excluye leyendo esa discrepancia, no por excepcion escrita a mano "
          "ni por comparar años."),
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
    nota=(VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): AASHTO "
          "publico la 10a ed. (LRFDBDS-10, diciembre de 2024, con erratas de "
          "2025; store.transportation.org, Item 5380), que sustituye a la 9a "
          "ed. (2020) citada; la propia AASHTO lo anuncia en AASHTO Journal "
          "(«AASHTO Issues 10th LRFD Bridge Design Spec Edition») con "
          "revisiones extensas en las Secciones 3, 5 y 6. Este proyecto cita "
          "de la 9a ed. las Secciones 3 (cargas: 3.4.1, 3.7.2, 3.10, 3.11 y su "
          "Apendice A11), 5 (recubrimiento: 5.10.1 y Table 5.10.1-1), 10 "
          "(licuefaccion: 10.5.4.2), 11 (muros: 11.6) y 12 (estructuras "
          "enterradas: 12.6), y DOS de ellas, la 3 y la 5, estan entre las "
          "que la 10a ed. revisa extensamente: el gabinete tiene que comparar "
          "esas dos articulo por articulo, no solo constatar la edicion. "
          "La edicion citada NO "
          "cambia y las citas siguen validas contra este archivo (sha1); cual "
          "rige el expediente es de 'edicion_que_rige_el_expediente'. Para "
          "gabinete: conseguir la 10a ed. y medir que articulos de los "
          "citados cambiaron."),
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
          "la pagina y leerla. "
          + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): AASHTO "
          "publica M 170M-23 (agosto de 2023; equivalente ASTM C76M-22; "
          "distribuidores accuristech y globalspec), posterior a la M 170M-04 "
          "citada; entre ambas hubo al menos la M 170M-15 y la M 170M-20. La "
          "edicion citada NO cambia y las citas siguen validas contra este "
          "archivo (sha1); cual rige el expediente es de "
          "'edicion_que_rige_el_expediente'. Para gabinete: conseguir la "
          "M 170M-23 y comparar sus Tablas 1 a 5 con las de este ejemplar."),
)

AASHTO_M36 = Fuente(
    id="AASHTO_M36",
    titulo=("AASHTO M 36 «Corrugated Steel Pipe, Metallic-Coated, for Sewers "
            "and Drains»"),
    emisor="AASHTO",
    # LO QUE LA PORTADA ROTULA (verificado por imagen en I1, re-verificado en
    # I1b): «AASHTO Designation: M 36-03 (2007)» y, debajo, «ASTM
    # Designation: A 760/A 760M-01a»; el pie de las paginas con contenido
    # dice «(c) 2008» (la caratula y la PDF 6 no llevan pie), que es el año
    # de impresion del tomo, no el de la edicion. `anio=2007` es LECTURA del
    # «(2007)» de la portada -- el año de reaprobacion; «-03» es el de
    # aprobacion --, no un rotulo que diga «edicion 2007». Hasta I1 aqui
    # decia edicion="M 36" y anio=2006, un año que no aparece en la portada
    # ni en ninguna de las paginas verificadas (raster: no se puede barrer
    # con grep, solo renderizar).
    edicion="M 36-03 (2007)",
    anio=2007,
    archivo_pdf=("normas/AASHTO M 36 Corrugated Steel Pipe, Metallic-Coated, "
                 "for Sewers and Drains.pdf"),
    sha1="f85b5658385ae6779dde4e5fd340ac3122b62636",
    paginas_pdf=24,
    # Medido renderizando el pie de cada pagina: la impresa se rotula
    # «M 36-n» (asi, con prefijo, igual que M 170M) y es la PDF n+1, porque
    # la PDF 1 es una caratula sin numerar. Hasta I1 esto estaba escrito
    # Corrida(desfase=1), que predice lo mismo pero no sabe LEER el rotulo
    # impreso: la primera cita real de esta fuente (AASHTO_M36.T6, pagina
    # impresa «M 36-11») lo hizo fallar en T6.
    paginacion=PorCapitulo(base={"M 36": 1}, separadores=("-",)),
    texto_extraible=False,
    convive_con=("ASTM_A760",),
    nota=("RASTER PURO, SIN CAPA DE TEXTO: la extraccion devuelve cadena "
          "vacia en las 24 paginas. Todo dato suyo se verifica renderizando. "
          "Y es la MISMA norma de doble designacion que ASTM A760/A760M, en "
          "edicion anterior: el PDF de A760 rotula «AASHTO No. M 36 / M 36M» "
          "en su propia portada. AL EJEMPLAR LE FALTA UNA PAGINA IMPRESA "
          "(hallado en I1b): la PDF 6 esta completamente en blanco y ocupa "
          "el lugar de la impresa «M 36-5» (aprox. numerales 6.3 a 7.2) -- "
          "la PDF 5 termina en el 6.2 y la PDF 7 arranca a media frase del "
          "7.2 --. No rompe la paginacion (la hoja en blanco conserva el "
          "desfase +1), pero un numeral en ese hueco NO es verificable "
          "contra este ejemplar. "
          + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): AASHTO "
          "publica M 36M/M 36-24 (edicion 2024 de sus Materials Standards, "
          "publicada en enero de 2024; lista HM-44 de nuevas y revisadas en "
          "downloads.transportation.org), posterior a la M 36-03 (2007) "
          "citada; entre ambas, al menos la M 36-16 (2020). La edicion citada "
          "NO cambia y las citas siguen validas contra este archivo (sha1); "
          "cual rige el expediente es de 'edicion_que_rige_el_expediente'. "
          "Para gabinete: conseguir la M 36M/M 36-24 --- que ademas es la "
          "unica via de cerrar la pagina impresa «M 36-5» que a este "
          "ejemplar le falta ---."),
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
    # Medido renderizando el pie de cada pagina: pagina impresa = pagina PDF.
    paginacion=Corrida(desfase=0),
    texto_extraible=False,
    convive_con=("AASHTO_M36",),
    nota=(
        "DOS COSAS QUE SOLO SE VEN RENDERIZANDO, y las dos son propiedades de "
        "la fuente que el registro tiene que declarar. "
        "PRIMERA: la capa de texto EXISTE y es INUTILIZABLE. La fuente no "
        "trae tabla ToUnicode usable y el volcado devuelve caracteres "
        "sustituidos -- «@esmkgbdmog» donde la pagina imprime «Designacion» "
        "--; la sustitucion no es uniforme ni siquiera en los digitos, de "
        "modo que no se puede deshacer. Todo dato de esta fuente se verifica "
        "por imagen. "
        "SEGUNDA: NO ES EL ORIGINAL EN INGLES. Es una TRADUCCION AL ESPAÑOL, "
        "y ademas de doble designacion: su portada rotula «Designación: A760 "
        "/ A760M - 10» y, arriba a la derecha, «AASHTO No. M 36 / M 36M». Es "
        "decir que este PDF y el de AASHTO M 36 son la MISMA norma en dos "
        "ediciones distintas, no dos normas independientes. Citar una "
        "traduccion como si fuera el original es una cita imprecisa aunque el "
        "dato sea correcto, y por eso se declara. "
        + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): ASTM publica "
        "A760/A760M-25 (tienda en linea de ASTM, a0760_a0760m-25), posterior a la "
        "A760/A760M-10 citada --- que ademas es traduccion ---; entre ambas, "
        "la -13, la -15 y la -15(2020). La edicion citada NO cambia y las "
        "citas siguen validas contra este archivo (sha1); cual rige el "
        "expediente es de 'edicion_que_rige_el_expediente'. Para gabinete: "
        "conseguir la -25 en ingles, que cerraria a la vez la vigencia y la "
        "reserva de traduccion."),
)

ASTM_A796 = Fuente(
    id="ASTM_A796",
    titulo=("ASTM A796/A796M-13 «Structural Design of Corrugated Steel Pipe, "
            "Pipe-Arches, and Arches» (practica de diseño estructural de "
            "tuberia de acero corrugado, arcos-tubo y arcos)"),
    emisor="ASTM International",
    # LO QUE EL EJEMPLAR ROTULA, y solo eso: el encabezado de las veinte
    # paginas con contenido imprime «A796/A796M – 13» (verificado por
    # imagen, N1), y el texto se llama a si mismo «this practice» (num. 5.1,
    # 5.2, 5.3) y «Practice» (num. 22.1). La PORTADA CON EL TITULO COMPLETO
    # NO ESTA en este ejemplar -- su pagina impresa 1 falta, ver la nota --,
    # de modo que el titulo de arriba es el que el dueño le puso al archivo
    # y coincide con el nombre corto con que las normas de producto la
    # citan; el titulo largo oficial («Standard Practice for ... for Storm
    # and Sanitary Sewers and Other Buried Applications») NO se transcribe
    # porque no hay pagina contra la que verificarlo. El censo de ausentes
    # decia año 2019 porque suponia la edicion vigente; se registra la que
    # ES.
    edicion="A796/A796M-13",
    anio=2013,
    archivo_pdf=("normas/ASTM A796-A796M-13 Structural Design of Corrugated "
                 "Steel Pipe, Pipe-Arches, and Arches.pdf"),
    sha1="df7858f04caf61bc1c3a4ea3d664e38cacddee25",
    paginas_pdf=21,
    # Medido renderizando el pie de las 21 paginas (N1): la impresa n es la
    # PDF n, del 2 al 21, y la PDF 1 esta EN BLANCO donde tendria que estar
    # la impresa 1. El pie imprime el numero con el primer digito recortado
    # («]0», «]1»...), de modo que la medida se hizo sobre la secuencia
    # completa y no sobre un digito suelto.
    paginacion=Corrida(desfase=0),
    texto_extraible=False,
    nota=(
        "TRES PROPIEDADES DEL EJEMPLAR, las tres medidas en N1. "
        "PRIMERA: la capa de texto EXISTE y esta DUPLICADA E INTERCALADA -- "
        "cada renglon aparece dos veces, y la segunda copia llega partida a "
        "mitad de palabra («Plac / Place e by / by Nuc / Nuclear») --. Una "
        "palabra suelta se encuentra por texto (sirve para ORIENTARSE: "
        "«minimum cover» localiza la pag. 5); una frase entera, no. Por eso "
        "se declara NO extraible, con el precedente de M 36 y A760: toda "
        "cita suya se verifica por IMAGEN, y asi lo firman. "
        "SEGUNDA: AL EJEMPLAR LE FALTA LA PAGINA IMPRESA 1 -- portada, "
        "num. 1 «Scope» y arranque del num. 2 --: la PDF 1 esta completamente "
        "en blanco y la PDF 2 abre a mitad del num. 2.1 («Place by the Rubber "
        "Balloon Method», D2487...). Es el mismo defecto que el ejemplar de "
        "M 36 tiene en su PDF 6, y con la misma consecuencia: un numeral de "
        "esa pagina NO es verificable contra este ejemplar. "
        "TERCERA, Y ES LA QUE IMPORTA AL PROYECTO: es una PRACTICA DE "
        "DISEÑO, no una norma de producto ni una tabla. NO CONTIENE ninguna "
        "tabla de calibre (espesor) por altura de cobertura: el espesor sale "
        "del PROCEDIMIENTO (num. 7 a 9: presion de diseño, empuje, area de "
        "pared requerida con SF = 2, pandeo, costura; num. 10: factor de "
        "flexibilidad) y se ELIGE de las Tablas 2 a 35 de propiedades "
        "seccionales (num. 8.1.1.2). La cobertura minima sale de las ecs. "
        "(13) a (16) del num. 11.1 en funcion de la rigidez, con dos pisos "
        "absolutos (300 mm siempre; 600 mm si el espesor es menor de "
        "1.32 mm) y 1.2 m bajo cargas de construccion (num. 11.4). Las "
        "tablas de «calibre por altura de cobertura» de la practica "
        "norteamericana son DERIVADAS de este procedimiento por fabricantes "
        "y asociaciones, y no estan en la norma. Lo que si trae, ademas: la "
        "presion de carga viva por altura de cobertura (num. 6.2.2.1), los "
        "limites de FF por corrugacion (num. 10.2 a 10.8) y, en el num. "
        "22.1, la remision de la INSTALACION a «Practice A798/A798M or "
        "A807/A807M» -- la unica mencion de A807 en las 20 paginas con "
        "contenido del ejemplar (la impresa 1, con la lista de normas "
        "referenciadas del num. 2.1, falta), que confirma "
        "que A807 es practica de instalacion y no la norma del calibre "
        "(DIS-HR-A807). "
        + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): ASTM publica "
        "A796/A796M-21 (tienda en linea de ASTM, a0796_a0796m-21; ANSI webstore), "
        "posterior a la A796/A796M-13 citada; entre ambas, la -17 y la -17a; "
        "ninguna -23, -24 ni -25 en los resultados. La edicion citada NO "
        "cambia y las citas siguen validas contra este archivo (sha1); cual "
        "rige el expediente es de 'edicion_que_rige_el_expediente'. Para "
        "gabinete: conseguir la -21 y comprobar si el procedimiento de los "
        "num. 7 a 11 cambio, porque es el que cerraria la mitad TMC de "
        "'clases_producto_por_relleno'."),
)

AASHTO_M294_TRAD = Fuente(
    id="AASHTO_M294_TRAD",
    titulo=("AASHTO M 294-11 «Tubería corrugada de polietileno, 300 a 1500 mm "
            "(12 a 60 in.) de diámetro» — TRADUCCION NO OFICIAL al español"),
    emisor=("AASHTO (el original); la traduccion es de autor no identificado, "
            "obtenida de un sitio de documentos compartidos"),
    # LO QUE EL EJEMPLAR ROTULA, y solo eso: la portada interior imprime
    # «Designación AASHTO: M 294-11» (PDF 1, verificado por texto y por
    # imagen). No lleva sello, copyright, pie editorial ni fecha de AASHTO:
    # el «-11» es la edicion del ORIGINAL que la traduccion declara seguir,
    # y `anio=2011` es la lectura de ese rotulo, no una fecha de la
    # traduccion, que no la imprime.
    edicion="M 294-11 (traduccion no oficial al español)",
    anio=2011,
    archivo_pdf=("normas/AASHTO M 294-11 Tuberia corrugada de polietileno 300 "
                 "a 1500 mm (traduccion no oficial).pdf"),
    sha1="7cecb19f73e4d101866832a3fc57db752fa53379",
    paginas_pdf=17,
    # NO HAY FOLIO QUE MEDIR, y es una propiedad del ejemplar, no una medida
    # que falte: el texto extraido de las 17 hojas no contiene ningun numero
    # de pagina, y las hojas 1, 5 y 8 renderizadas no imprimen cabecera ni
    # pie numerado. Por eso NO es `Corrida(desfase=0)`: eso afirmaria una
    # numeracion impresa que coincide con la del PDF, y aqui no hay ninguna.
    # Es el caso de HDS5_SI_1985, resuelto igual que alli: `SinDeterminar`
    # con la razon, citas localizadas por pagina PDF con «s/n» como pagina
    # impresa, y SIN FIRMA -- el invariante T6 impide firmar una pagina PDF
    # de una fuente sin paginacion medida, y no se toca por conveniencia --.
    # Las citas quedan censadas en `CITAS_SIN_FIRMA_A_PROPOSITO`
    # (tests/test_normativa.py) y su contenido lo comprueban T0, T2 y T3 en
    # cada corrida con PyMuPDF, porque el texto SI es extraible.
    paginacion=SinDeterminar(
        por_que=("el ejemplar no imprime numero de pagina en ninguna de sus "
                 "17 hojas: ni cabecera ni pie numerado (medido en N2 sobre "
                 "el texto de las 17 y sobre las hojas 1, 5 y 8 "
                 "renderizadas). No hay «pagina impresa» que medir; sus "
                 "citas se localizan por pagina PDF, llevan «s/n» como "
                 "pagina impresa y no se firman (T6), con el precedente de "
                 "HDS5_SI_1985")),
    texto_extraible=True,
    convive_con=("AASHTO_M294",),
    nota=(
        "CUATRO PROPIEDADES DEL EJEMPLAR, las cuatro medidas en N2. "
        "PRIMERA, Y ES LA QUE GOBIERNA TODO LO QUE SALE DE AQUI: NO ES EL "
        "ORIGINAL EN INGLES DE AASHTO. Es una TRADUCCION AL ESPAÑOL NO "
        "OFICIAL, de autor no identificado, obtenida de un sitio de "
        "documentos compartidos; no lleva sello ni pie editorial de AASHTO y "
        "trae erratas propias de traduccion («expresadoe», «instalaión», "
        "«seción», «Tip D», «qur», «menoreas», «vrgenes»), que se "
        "transcriben como se imprimen (T21). COMO SE MODELA, decidido "
        "leyendo el esquema: igual que ASTM_A760, que tambien es traduccion "
        "-- Fuente PRESENTE con la naturaleza declarada en esta nota -- y, "
        "a diferencia de A760, con el ORIGINAL todavia en FUENTES_AUSENTES "
        "(`AASHTO_M294`) y `convive_con` cruzado entre los dos: verificar "
        "contra una traduccion no oficial acredita que la TRADUCCION dice X, "
        "no que AASHTO lo diga, de modo que la ausencia del original no se "
        "cierra sino que se REDEFINE (su `que_desbloquearia` dice ahora que "
        "firmar). Toda cita suya lleva el sufijo TRAD en el id y las palabras "
        "«traducción no oficial» en su nota, y una guardia de la suite lo "
        "exige; todo valor que sostenga lo sostiene con esa reserva. Una "
        "FIRMA acredita el ARCHIVO exacto (sha1), no a AASHTO -- es el "
        "precedente de ASTM_A760, cuya cita si va firmada --, de modo que "
        "lo que impide firmar estas citas es una sola cosa, que no imprimen "
        "folio (T6), no que sean de una traduccion; el dia que llegue el "
        "original se reverifica contra el y la cita pasa a ser al original. "
        "SEGUNDA: NO IMPRIME FOLIO (ver `paginacion`). "
        "TERCERA: el texto ES extraible y limpio -- la unica de las cinco "
        "normas de producto y practica ASTM/AASHTO de normas/ que lo es --, "
        "de modo que T2 y T3 comprueban cada cita en cada corrida. "
        "CUARTA, Y ES LA QUE IMPORTA AL PROYECTO: EL AMBITO TERMINA EN "
        "1500 mm. El num. 1.1.1 (tamaños nominales de 300 a 1500 mm) y el "
        "num. 7.2.1 (los doce diametros nominales, de 300 a 1500 mm, con "
        "paso de 75 mm hasta 750 y de 150 mm de 900 a 1500) fijan la serie, "
        "y el num. 1.3 declara los valores SI como los estandar y las "
        "pulgadas como aproximadas. Es la unica de las tres normas de "
        "producto del catalogo cuya serie TERMINA donde el proyecto topa: a "
        "diferencia de A760 y M 170M (hasta 3600 mm), aqui 1.50 m ES el "
        "techo del ambito -- segun la traduccion, que es lo unico que hay --. "
        "LO QUE NO TRAE, leido entero (17 hojas): (a) ninguna tabla de "
        "clase, calibre o rigidez por ALTURA DE RELLENO -- el num. 1.4 "
        "excluye expresamente camas, relleno y carga de cubierta de tierra y "
        "remite el diseño estructural a AASHTO LRFD Seccion 12 --; lo que si "
        "tabula es la RIGIDEZ MINIMA de tuberia al 5 % de deflexion por "
        "diametro (num. 7.4, de 345 kPa en 300 mm a 105 kPa en 1500 mm), "
        "insumo de ese diseño, no transcrita en N2 porque no sostiene nada "
        "que el proyecto calcule hoy; (b) ningun DIAMETRO EXTERIOR ni altura "
        "del perfil corrugado: el num. 7.2.2 tabula el espesor MINIMO de la "
        "pared interior lisa (Tipo S) o de las dos paredes (Tipo D), de 0,9 "
        "a 2,0 mm, que NO es el t que separa D interior de D exterior -- por "
        "eso `espesor_pared_conducto['hdpe']` sigue sin fuente --. Trae "
        "ademas la Tabla 1 (perforaciones Clase 1), las tolerancias de "
        "diametro interior (7.2.3), el marcado (11) y un anexo y un "
        "apendice de control de calidad. "
        + VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): AASHTO publica "
        "M 294-25 (publicada el 19-09-2025; distribuidor Intertek Inform), "
        "posterior a la M 294-11 que esta traduccion declara seguir; entre "
        "ambas, al menos la M 294-15 y la M 294-21 --- el censo de ausentes "
        "llego a decir «2020» por suponer la vigente, y N2 lo dejo en -11 ---. "
        "El titulo de la edicion vigente conserva la serie «300- to 1500-mm "
        "(12- to 60-in.) Diameter», de modo que el techo de la serie que "
        "sostiene 'D_max_catalogo' no se movio en el rotulo; el contenido no "
        "se contrasto. La edicion citada NO cambia y las citas siguen validas "
        "contra este archivo (sha1); cual rige el expediente es de "
        "'edicion_que_rige_el_expediente'. Para el original ausente "
        "(AASHTO_M294) la consecuencia es que hay DOS compras distintas: la "
        "-11, que reverificaria la traduccion, y la -25, que citaria la "
        "vigente; ver su nota."),
)


FUENTES: Dict[str, Fuente] = {
    f.id: f for f in (
        MC_HHD, MP, MS, EG2013, E030, E050, E060,
        HDS5_3ED, HDS5_SI_1985, AASHTO_LRFD_9,
        AASHTO_M170M, AASHTO_M36, ASTM_A760, ASTM_A796, AASHTO_M294_TRAD,
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


# ASTM_A796 SALIO DE ESTE CENSO EN N1: esta arriba, entre las presentes. Su
# ficha de ausente decia que desbloquearia «la mitad TMC de
# 'clases_producto_por_relleno'» y que era «una de las DOS ausencias baratas
# del plan». Conseguida y leida, desbloqueo menos de lo que la ficha
# prometia, y conviene dejarlo escrito donde estaba la promesa: la norma NO
# TABULA el calibre por altura de cobertura -- lo fija por procedimiento
# (ver la nota de la Fuente) --, de modo que la mitad TMC del criterio no se
# cierra transcribiendo sino IMPLEMENTANDO el num. 6 a 11, que es una sesion
# de calculo con caso patron y no de registro.

# AASHTO_M294 NO SALIO DE ESTE CENSO EN N2, aunque en normas/ haya un PDF con
# su designacion, y conviene leer por que antes de «corregirlo»: lo que
# llego es una TRADUCCION NO OFICIAL (`AASHTO_M294_TRAD`, arriba, entre las
# presentes), y una traduccion no oficial no es el documento normativo. La
# ficha de ausente decia que la fuente desbloquearia «D_max['hdpe']» y era
# «la otra ausencia barata»; conseguida y leida la traduccion, lo que se
# midio es esto: la serie de tamaños nominales SI termina en 1500 mm (1.1.1,
# 7.2.1), de modo que el tope del HDPE es el unico de los tres que la norma
# de producto sostiene -- y lo sostiene una traduccion sin firma --. El
# criterio sigue siendo [A] de catalogo (la eleccion es la misma para los
# tres materiales) con ese extremo declarado; lo que el ORIGINAL desbloquea
# ya no es el tope sino la FIRMA.
AASHTO_M294 = _ausente(
    "AASHTO_M294",
    ("AASHTO M 294-11 «Corrugated Polyethylene Pipe, 300- to 1500-mm "
     "Diameter» -- el ORIGINAL EN INGLES, del que deriva la traduccion no "
     "oficial presente en normas/"),
    # El censo decia «M 294», 2020, porque suponia la edicion vigente. Se
    # registra la que la traduccion declara seguir (-11): es contra ESA
    # edicion contra la que habria que reverificar lo transcrito; si la
    # vigente es otra, es una pregunta distinta y es de la sesion T1.
    "AASHTO", "M 294-11 (original en ingles)", 2011,
    Ausencia(
        por_que_se_cita=("es el ORIGINAL del que deriva `AASHTO_M294_TRAD`, "
                         "la traduccion no oficial que N2 incorporo; el tope "
                         "de diametro del HDPE se le atribuia, y desde N2 la "
                         "serie 300-1500 mm que lo sostiene esta transcrita "
                         "DE LA TRADUCCION"),
        que_desbloquearia=("citar a AASHTO y no a un traductor anonimo, no "
                           "el tope: (1) reverificar contra el original lo "
                           "que hoy sostiene la traduccion -- la serie de "
                           "tamaños nominales 300-1500 mm (1.1.1, 7.2.1), la "
                           "tabla de espesores minimos de pared (7.2.2) y la "
                           "exclusion del diseño estructural (1.4) -- y, si "
                           "el original imprime folio, firmar (`Verificado`) "
                           "lo que hoy no puede firmarse por T6; (2) "
                           "comprobar que el original no imprime nada que la "
                           "traduccion omita o altere en esos numerales; (3) "
                           "leer el diametro exterior o la altura de perfil "
                           "si el original los fijara, que la traduccion no "
                           "trae. NO desbloquearia un [N]: es norma de "
                           "producto extranjera, y 'D_max_catalogo' seguiria "
                           "[A] con el techo de la serie como extremo declarado"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente=("AASHTO_M294_TRAD, traduccion no oficial presente "
                           "en normas/, rotulada como tal en cada cita")),
    convive_con=("AASHTO_M294_TRAD",),
    nota=(VIGENCIA_POSTERIOR + " (T1, " + VIGENCIA_COMO + "): la edicion "
          "vigente del emisor es M 294-25 (19-09-2025), no la -11 que este "
          "censo registra. No se cambia la edicion: es contra la -11 contra la "
          "que hay que reverificar lo que la traduccion transcribe. Pero la "
          "compra tiene ahora dos destinos posibles y son decisiones "
          "distintas: la -11 cierra la reserva de traduccion; la -25 cierra la "
          "vigencia y obliga a reverificar 1.1.1, 1.4, 7.2.1 y 7.2.2 contra un "
          "texto que puede haber cambiado. Cual de las dos es de "
          "'edicion_que_rige_el_expediente'."))

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
        por_que_se_cita=("practica de instalacion de TMC: A796 num. 22.1 "
                         "(presente desde N1) manda que la instalacion se "
                         "ajuste a «Practice A798/A798M or A807/A807M»"),
        que_desbloquearia="nada que el EG-2013 no cubra ya para obra vial peruana",
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente="EG-2013 Seccion 507"))

ASTM_A807 = _ausente(
    "ASTM_A807", "ASTM A-807 (la designacion que la hoja de ruta atribuye al "
    "calibre de TMC por altura de relleno)", "ASTM International", "A-807", 0,
    Ausencia(
        por_que_se_cita=("la hoja de ruta v8 la cita dos veces (Sec. 7.A y "
                         "Fase 8) para el calibre de TMC segun altura"),
        que_desbloquearia=("nada: la remision es FALSA, y desde N1 esta "
                           "VERIFICADA en positivo y no solo por ausencia: "
                           "A796 num. 22.1 la cita como practica de "
                           "INSTALACION («shall conform to Practice "
                           "A798/A798M or A807/A807M»), que es exactamente "
                           "para lo que EG-2013 507.05/.06/.08 la invocan. "
                           "El calibre lo fija A796 por procedimiento "
                           "(num. 7 a 10) -- no hay tabla en ninguna de las "
                           "dos --. DIS-HR-A807 quedo RESUELTA en N1 al "
                           "corregirse la fila de la v8"),
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
        "NINGUNA de las dos contrastables sobre el original, y la tercera "
        "solo sobre una traduccion. Los topes 2.70 / 2.10 / 1.50 m se "
        "atribuian a «ASTM C76 / AASHTO M170», «AASHTO M36 / ASTM A760» y "
        "«AASHTO M294», y las dos primeras atribuciones estan verificadas EN "
        "CONTRA sobre los PDF de normas/: ASTM A760/A760M-10 tabula de 100 a "
        "3600 mm y AASHTO M 170M-04 de 300 a 3600 mm con diseños especiales "
        "por encima. La tercera se contrasto en N2 sobre la TRADUCCION NO "
        "OFICIAL de AASHTO M 294-11 (`AASHTO_M294_TRAD`, citas 1.1.1 y "
        "7.2.1): su ambito y su serie de tamaños nominales terminan en "
        "1500 mm, de modo que el tope del HDPE es el unico que coincide con "
        "el techo de una norma de producto -- segun una traduccion sin firma; "
        "el original sigue ausente --. No cambia la clase del dato: el tope "
        "sigue siendo de catalogo para los tres materiales, porque la "
        "eleccion (que diametro admite el proyecto por disponibilidad) es la "
        "misma, y en HDPE ademas no hay serie por encima. Un tope de catalogo "
        "no tiene numeral, y descartaba material en silencio con una cita "
        "que ninguna norma sostiene (NOR-PRO-01, NOR-PRO-02, MAT-O8)"),
)

CATALOGOS: Dict[str, Catalogo] = {CAT_TUBERIA_LOCAL.id: CAT_TUBERIA_LOCAL}


def estado_de_vigencia(f: Fuente) -> Optional[str]:
    """
    La marca de vigencia de T1 que lleva la nota de una Fuente, o None.

    Devuelve una de `MARCAS_DE_VIGENCIA` --- confirmada, edicion posterior
    detectada, o no determinable en linea --- y levanta ErrorDeRegistro si la
    nota lleva mas de una: una fuente no puede estar vigente y superada a la
    vez. Es lo que un test comprueba en las quince presentes, para que la
    vigencia no vuelva a ser prosa que nadie enumera. El dia que el esquema
    tenga `Fuente.vigencia` (ficha T1-01), esta funcion lee ese campo y la
    marca desaparece de las notas.
    """
    presentes = [m for m in MARCAS_DE_VIGENCIA if m in f.nota]
    if len(presentes) > 1:
        raise ErrorDeRegistro(
            f"Fuente {f.id}: la nota lleva {len(presentes)} marcas de vigencia "
            f"({presentes}); una fuente no esta vigente y superada a la vez")
    return presentes[0] if presentes else None


def fuentes_con_edicion_posterior(
        fuentes: Optional[Dict[str, Fuente]] = None) -> Tuple[str, ...]:
    """Las presentes cuyo emisor publica una edicion posterior a la citada."""
    fuentes = FUENTES if fuentes is None else fuentes
    return tuple(f.id for f in fuentes.values()
                 if estado_de_vigencia(f) == VIGENCIA_POSTERIOR)


def quien_gobierna_por_discrepancia(
        id_fuente: str,
        fuentes: Optional[Dict[str, Fuente]] = None) -> Optional[str]:
    """
    La Fuente PRESENTE con la que esta CONVIVE (`convive_con`) y a la que una
    Discrepancia RESUELTA le da `gana` frente a esta, o None si ninguna
    discrepancia resolvio la pareja.

    Es lo unico que en el registro DICE quien gobierna entre dos ediciones
    del mismo documento: DIS-HDS5-EDICIONES (HDS5_3ED gana a HDS5_SI_1985).
    Se lee de ahi y no se infiere de `anio`, que solo dice cual es mas
    nueva. LAS DOS CONDICIONES HACEN FALTA, y la primera version de esta
    funcion solo miraba la discrepancia: el Manual de Puentes pierde varias
    discrepancias resueltas frente a AASHTO_LRFD_9 (erratas de imprenta de
    su cadena sismica) y eso no hace de AASHTO su edicion vigente --- son
    documentos distintos, y MP no convive con AASHTO ---. La discrepancia
    que resuelve una EDICION es la que enfrenta a dos fuentes que conviven.
    Import diferido por la misma razon que en `registro.construir`:
    `discrepancias` importa `esquema`, y este modulo no quiere un ciclo el
    dia que aquel consulte fuentes.
    """
    from . import discrepancias as _discrepancias
    from .esquema import EstadoDiscrepancia
    fuentes = FUENTES if fuentes is None else fuentes
    f = fuentes[id_fuente]
    for d in _discrepancias.DISCREPANCIAS.values():
        if d.estado is not EstadoDiscrepancia.RESUELTA:
            continue
        if id_fuente in {p.quien for p in d.partes} \
                and d.gana != id_fuente and d.gana in f.convive_con \
                and d.gana in fuentes:
            return d.gana
    return None


def fuentes_con_eleccion_de_edicion_pendiente(
        fuentes: Optional[Dict[str, Fuente]] = None) -> Tuple[str, ...]:
    """
    Las de `fuentes_con_edicion_posterior` en las que el proyectista tiene
    algo que elegir: las que ninguna Discrepancia RESUELTA subordina a otra
    Fuente presente.

    La regla, y no una lista: una fuente superada queda fuera solo si el
    registro ya DIJO quien gobierna en su lugar --- una `Discrepancia`
    resuelta con `gana` a favor de otra presente, que es DIS-HDS5-EDICIONES
    para HDS5_SI_1985 ---. No se infiere de `anio` ni de la vigencia de la
    sucesora, y la diferencia se ve por mutacion: si HDS5_3ED quedara
    superada por una cuarta edicion, la de 1985 seguiria fuera, porque la
    discrepancia que la descarto frente a la tercera no se reabre; y
    AASHTO_M36, que convive con ASTM_A760 (presente y mas nueva, pero sin
    discrepancia que la haga ganar), sigue dentro. Las que quedan son las
    que 'edicion_que_rige_el_expediente' nombra, y un test comprueba que las
    nombre todas y solo a ellas.
    """
    fuentes = FUENTES if fuentes is None else fuentes
    return tuple(id_ for id_ in fuentes_con_edicion_posterior(fuentes)
                 if quien_gobierna_por_discrepancia(id_, fuentes) is None)


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
