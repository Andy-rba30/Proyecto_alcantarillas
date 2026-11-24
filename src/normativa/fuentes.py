"""
Las fuentes normativas del proyecto: las dieciocho presentes --cuyo PDF vive,
desde T-12, SOLO en el repositorio de normas enlazado por `NORMAS_DIR`: hasta
T-12 dieciseis estaban ademas en `normas/` de este repositorio, y HEC-14 y el
WSDOT Hydraulics Manual, que T-0 dio de alta, nunca estuvieron--, las doce
que se citan y NO estan (§8 del diseño, §15 del plan) y los dos PDF que estan
en el repositorio de normas y no se registran, censados con su motivo
(`PRESENTES_SIN_REGISTRAR`, PC-23). DONDE ESTAN LOS PDF EN
DISCO lo resuelve este modulo y nadie mas: `directorios_de_normas()` y
`ruta_pdf()`, al final del archivo. Hasta N1 eran trece y trece -- este
encabezado decia «once» y llevaba tiempo sin contar: el censo de ausentes
tenia trece entradas --; ASTM A796/A796M-13 entro en `normas/` en pre-N1 y
N1 la paso del censo de ausentes a este. EXT-6 paso el DG-2018 de ausente a
presente y sumo tres ausentes (el RNGIV al que el DG-2018 remite, y AASHTO
M 259 y M 273, las normas del cajon prefabricado que el proyecto no usa).
N2 sumo la quinceava SIN restar del censo de ausentes, y no es un error de cuenta: lo
que entro en `normas/` es una TRADUCCION NO OFICIAL de AASHTO M 294-11
(`AASHTO_M294_TRAD`), y el original en ingles (`AASHTO_M294`) sigue ausente.
Una fuente derivada no sustituye a la primaria: convive con ella
(`convive_con` cruzado, el mismo recurso de las dos HDS-5) y la ausencia del
original queda redefinida como «que desbloquearia verificar contra el».
N3 del plan 12 (2026-11-24) sumo HEC-11 en su version metrica (`HEC11`),
que no estaba censada como ausente: HEC-14 la nombraba y el registro solo
lo decia en la nota de `HEC14.10.2#FILTRO`.
N2 DEL PLAN 12 (2026-11-24, «marco legal»; no es el N2 de arriba) sumo
TRES presentes y resto DOS ausentes: la Ley 29338 (`LEY_29338`, que hasta
entonces era una ausente que decia «y su reglamento»), su Reglamento como
Fuente PROPIA (`REG_LEY_29338`, DS 001-2010-AG: otro documento y otro acto)
y el RNGIV (`RNGIV`, DS 034-2008-MTC); y el dictamen de Fable sobre N2 sumo
DOS ausentes, las remisiones del marco legal que terminan fuera de normas/
(`RJ_332_2016_ANA`, `RM_660_2008_MTC`). N1 del plan 12 sumo la edicion 2018
del Manual de Puentes (`MP2018`), que convive con la 2016 (`MP`). Con eso,
HEC-11 de N3 y el marco legal de N2, las presentes son veinticinco y las
ausentes doce; los conteos de arriba son los de cada sesion.

TODOS LOS SHA-1 Y TODAS LAS PAGINACIONES DE ESTE ARCHIVO ESTAN MEDIDOS, no
supuestos. El procedimiento, para que se pueda repetir:

    python3 -m src.normativa.extraccion sha1 <fragmento>
    python3 -m src.normativa.extraccion cabeceras <fragmento> <desde> <hasta>

Los desfases se midieron barriendo el documento ENTERO y contando cuantas
paginas confirman cada desfase, no dos o tres a ojo:

    Manual de Hidrologia .... +3   confirmado en 221 de 225 paginas
    Manual de Puentes ....... +1   confirmado en 650 de 673
    Manual de Puentes 2018 .. +4   confirmado en 630 de 634 (N1 del plan de
                                  normas 2: las cuatro que no confirman son
                                  la RD y la caratula, sin folio)
    Manual de Suelos ........ +1   confirmado en 269 de 281
    EG-2013 ................. +8   confirmado en 1268 de 1282
    E.030 / E.050 / E.060 ...  0   confirmado en 67/68, 78/82 y 204/205
    HDS-5 3a ed ............. por capitulo; catorce bases medidas
    AASHTO LRFD 9a ed ....... por capitulo; quince bases medidas
    ASTM A796/A796M-13 .....  0   confirmado en 20 de 21 (N1, por imagen:
                                  la PDF 1 esta en blanco)
    DG-2018 ................. +1   confirmado en 284 de 285 (EXT-6; la PDF 1
                                  es la caratula, sin numero)
    AASHTO M 294-11 (trad.) . SIN FOLIO: ninguna de sus 17 hojas imprime
                                  numero de pagina (N2, por texto en las 17
                                  y por imagen en la 1, la 5 y la 8)
    HEC-14 3a ed ............ por capitulo; diecisiete bases medidas (T-0):
                                  270 de 287 confirman; las 17 que no son la
                                  portada, el formulario, la fe de erratas,
                                  las diez romanas (i-x) y cuatro del cuerpo
                                  sin folio extraible (PDF 15, 143, 148, 222)
    WSDOT M 23-03.12 ........ por capitulo; quince bases medidas (T-0): 311
                                  de 325 confirman por la cabecera «Page c-n»;
                                  las 14 que no son la portada, el aviso
                                  legal y los doce folios romanos del indice
                                  (i a xii, PDF 3 a 14)
    HEC-11 (SI) ............. SIN FOLIO: captura web de la FHWA, ninguna de
                                  sus 193 hojas imprime numero (N3, por texto
                                  en las 193 y por imagen en cuatro)
    Ley 29338 (SPIJ) ........ SIN FOLIO: ninguna de sus 49 hojas imprime
                                  numero de pagina (N2 del plan 12, por texto
                                  en las 49 y por imagen en la 1, la 5, la 25
                                  y la 35)
    DS 001-2010-AG .......... 0   confirmado en 83 de 83 (pie «Reglamento de
                                  la Ley Nº 29338 ... n»; N2 del plan 12)
    DS 034-2008-MTC (SPIJ) .. 0   confirmado en 17 de 17 (pie «Página n» del
                                  SPIJ; N2 del plan 12)

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

LA VIGENCIA DE CADA EDICION SE VERIFICO EN T1 (2026-09-14; la del DG-2018
en EXT-6, 2026-09-20) y vive en el campo `Fuente.vigencia` (ver el bloque
«T1 / EXT-6» de abajo y `estado_de_vigencia`); hasta EXT-6 era una marca en
la `nota`.
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

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from .esquema import (
    Ausencia,
    Catalogo,
    Corrida,
    ErrorDeRegistro,
    Esfuerzo,
    EstadoDeVigencia,
    Fuente,
    Irregular,
    PdfPresenteSinRegistrar,
    PorCapitulo,
    SinDeterminar,
    Vigencia,
)

# ===========================================================================
# T1 / EXT-6 - Vigencia de las ediciones citadas (verificada el 2026-09-14;
# la de DG-2018, el 2026-09-20)
# ===========================================================================
# HASTA EXT-6 ERA UNA MARCA EN LA NOTA Y NO UN CAMPO, y conviene dejar dicho
# por que: el esquema no tenia donde poner «el emisor publica hoy una edicion
# posterior a la citada» --- `reemplaza_a` mira hacia ATRAS, `convive_con`
# exige que la otra Fuente exista, y `Discrepancia` obliga a declarar `gana`
# ---, y T1 registro el hallazgo en `nota` detras de una marca fija que
# `estado_de_vigencia` leia (ficha T1-01 de docs/decisiones_diferidas.md).
# EXT-6 escribio el campo, `Fuente.vigencia`, con lo que la ficha pedia y lo
# que EXT-N-01 añadio: `acto_aprobatorio` y `derogado_por`, que son lo que
# separa una fuente LEGAL peruana --- aprobada y derogada por resolucion ---
# de una tecnica extranjera, que tiene edicion posterior y a la que nadie
# «deja sin efecto». La marca desaparecio de las notas; lo que cada nota
# conserva es la prosa de la verificacion, que sigue siendo el limite que
# cada confirmacion hereda.
#
# COMO SE VERIFICO, y es el limite que cada `Vigencia.como` declara: por
# busqueda web (WebSearch) sobre los resultados de las paginas del emisor y
# de los repositorios oficiales. Ninguna pagina fue LEGIBLE directamente
# desde el entorno de T1 --- el proxy de egress bloqueo gob.pe, el portal del
# MTC, busquedas.elperuano.pe, el sitio de SENCICO, los de la FHWA, AASHTO y
# ASTM, y los distribuidores de normas ---, de modo que cada confirmacion se
# apoya en lo que los resultados de busqueda transcriben de esas paginas, no
# en su lectura. Lo que eso deja para gabinete esta en `pendiente_gabinete`.
VIGENCIA_VERIFICADA_EL = "2026-09-14"
VIGENCIA_VERIFICADA_EL_EXT6 = "2026-09-20"
VIGENCIA_VERIFICADA_EL_T0 = "2026-11-11"
# --- VE-3.6 --- La del USBR «Design of Small Canal Structures» (Familia C).
VIGENCIA_VERIFICADA_EL_VE3 = "2026-11-17"
# --- N2 del plan 12 --- La del marco legal: Ley 29338, su Reglamento y el
# RNGIV.
VIGENCIA_VERIFICADA_EL_MARCO_LEGAL = "2026-11-24"
VIGENCIA_COMO = (
    "busqueda web (WebSearch) sobre resultados de las paginas del emisor y "
    "de repositorios oficiales; ninguna pagina fue legible directamente desde "
    "el entorno de T1 (egress bloqueado), de modo que la confirmacion es por "
    "lo que los resultados transcriben de esas paginas y no por su lectura")
VIGENCIA_COMO_EXT6 = (
    "busqueda web (WebSearch) desde el entorno de EXT-6 sobre resultados de "
    "El Peruano y gob.pe (MTC); las paginas tampoco fueron legibles "
    "directamente, de modo que la confirmacion es por lo que los resultados "
    "transcriben de ellas y no por su lectura")

VIGENCIA_COMO_T0 = (
    "busqueda web (WebSearch) desde el entorno de T-0 sobre resultados del "
    "sitio del emisor (wsdot.wa.gov, fhwa.dot.gov) y de repositorios que lo "
    "reproducen; las paginas del emisor tampoco fueron legibles directamente "
    "(los dos hosts estan fuera de la red permitida de la sesion), de modo "
    "que la confirmacion es por lo que los resultados transcriben de ellas y "
    "no por su lectura")

# --- N2 del plan 12 --- LO QUE «CONFIRMADA» QUIERE DECIR EN UNA NORMA
# LEGAL COMPILADA, que no es lo mismo que en una tecnica. Los tres ejemplares
# son COMPILACIONES (SPIJ, o la de la DGAAE del MINEM) con las modificatorias
# hasta una fecha, y el acto que aprueba la norma sigue vigente: lo que se
# confirma es que NO fue derogada y que los articulos CITADOS no aparecen
# modificados despues de la fecha de la compilacion. Lo que la compilacion
# no recoge de otros articulos va en `pendiente_gabinete` y en la nota, no
# en `edicion_posterior`: una norma modificada no abre una ELECCION de
# edicion para el proyectista (rige el texto vigente), que es lo que
# POSTERIOR dispararia en `fuentes_con_eleccion_de_edicion_pendiente`. Es
# una lectura del esquema que se declara (ficha N2L-02).
VIGENCIA_COMO_MARCO_LEGAL = (
    "lectura del propio ejemplar (las notas de modificacion y las "
    "concordancias que la compilacion imprime) y busqueda web (WebSearch) "
    "desde la sesion de N2 del plan 12 sobre resultados de El Peruano, "
    "gob.pe y de resoluciones de la ANA que aplican los articulos citados; "
    "ninguna pagina oficial fue leida entera, de modo que la confirmacion es "
    "por lo que los resultados transcriben y no por su lectura")

# --- N1 del plan de normas 2 (proceso/planes_mejora/12_PLAN_NORMAS_2.md) ---
# La del Manual de Puentes 2018 (`MP2018`). No es la «N1» de 2026-09-14 que
# paso ASTM A796 a presente: es la primera tarea del plan de integracion de
# `normas_2/`, y sus fichas son N1MP-xx en docs/decisiones_diferidas.md.
VIGENCIA_VERIFICADA_EL_N1MP = "2026-11-24"
VIGENCIA_COMO_N1MP = (
    "lectura del propio ejemplar --- la RD 19-2018-MTC/14 esta impresa en sus "
    "PDF 1 a 3 (escaneo sin capa de texto, leida renderizando la pagina) --- y "
    "busqueda web (WebSearch) desde la sesion de N1: los resultados "
    "transcriben la edicion de El Peruano del lunes 14-01-2019 «Aprueban "
    "Manual de Puentes» con esta RD y ninguna RD posterior que lo modifique o "
    "derogue; las paginas del MTC y de El Peruano no fueron legibles "
    "directamente, de modo que la ausencia de un acto posterior es lo que los "
    "resultados no muestran, no una lectura del portal")

# Los tres estados, con el nombre corto que el resto de la casa ya usaba.
# Son el ENUM, no cadenas: `estado_de_vigencia` devuelve uno de estos.
VIGENCIA_CONFIRMADA = EstadoDeVigencia.CONFIRMADA
VIGENCIA_POSTERIOR = EstadoDeVigencia.POSTERIOR
VIGENCIA_GABINETE = EstadoDeVigencia.GABINETE
MARCAS_DE_VIGENCIA: Tuple[EstadoDeVigencia, ...] = (
    VIGENCIA_CONFIRMADA, VIGENCIA_POSTERIOR, VIGENCIA_GABINETE)


def _confirmada(acto_aprobatorio: str = "", pendiente_gabinete: str = "",
                fecha: str = VIGENCIA_VERIFICADA_EL,
                como: str = VIGENCIA_COMO) -> Vigencia:
    return Vigencia(estado=VIGENCIA_CONFIRMADA, fecha=fecha, como=como,
                    acto_aprobatorio=acto_aprobatorio,
                    pendiente_gabinete=pendiente_gabinete)


def _posterior(edicion_posterior: str, *, acto_aprobatorio: str = "",
               derogado_por: str = "", pendiente_gabinete: str = "") -> Vigencia:
    return Vigencia(estado=VIGENCIA_POSTERIOR, fecha=VIGENCIA_VERIFICADA_EL,
                    como=VIGENCIA_COMO, edicion_posterior=edicion_posterior,
                    acto_aprobatorio=acto_aprobatorio, derogado_por=derogado_por,
                    pendiente_gabinete=pendiente_gabinete)


# ===========================================================================
# Las dieciseis fuentes que SI estan en normas/ (las dos que T-0 dio de alta
# desde el repositorio de normas van despues de DG2018)
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
    vigencia=_confirmada(
        acto_aprobatorio="RD 20-2011-MTC/14",
        pendiente_gabinete=("leer el listado de manuales del portal del MTC, "
            "que no fue legible")
    ),
    nota=("El diseño la dejo en SinDeterminar porque ninguna cita del "
          "repositorio declaraba su pagina PDF. Medido en S12: +3, "
          "confirmado en 221 de sus 225 paginas. "
          "VIGENCIA (T1): la RD "
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
    # --- N1 (plan de normas 2) --- La edicion 2018 entro a normas/ como
    # `MP2018`, y las dos CONVIVEN, como las dos HDS-5. NO hay Discrepancia
    # resuelta que diga cual gobierna, y es a proposito: elegir es del
    # proyectista ('edicion_legal_que_rige_el_expediente'), con la fecha de
    # inicio del expediente que el registro no tiene. Por eso MP sigue en
    # `fuentes_con_eleccion_de_edicion_pendiente_legal`.
    convive_con=("MP2018",),
    vigencia=_posterior(
        ("Manual de Puentes, diciembre de 2018 (RD 19-2018-MTC/14, 630 "
         "paginas), presente en normas/ como MP2018"),
        acto_aprobatorio="RD 041-2016-MTC/14",
        derogado_por="RD 19-2018-MTC/14",
        # Lo que T1 dejo para gabinete se hizo en N1 (plan de normas 2): la
        # edicion 2018 esta en normas/, sus 29 numerales citados se midieron
        # (ficha N1MP-02 y N1MP-03) y la RD se leyo en el ejemplar --- no
        # trae regimen transitorio ---. Queda lo que el ejemplar no imprime.
        pendiente_gabinete=("leer en El Peruano la fecha de publicacion de la "
            "RD 19-2018-MTC/14, que el ejemplar de 2018 no "
            "imprime (la busqueda de N1 la situa el "
            "14-01-2019, y la RD entra en vigencia al dia "
            "siguiente)")
    ),
    nota=("23 de sus 673 paginas no imprimen numero: son portadas de capitulo "
          "y laminas fotograficas de puentes. El desfase no cambia. "
          "VIGENCIA (T1): el MTC "
          "aprobo por RD 19-2018-MTC/14 (El Peruano, dispositivo 1730970-1; "
          "gob.pe, MTC, normas legales 4441255) un Manual de Puentes "
          "ACTUALIZADO de 630 paginas, vigente desde el 15-01-2019, que deja "
          "sin efecto la RD 041-2016-MTC/14 de este ejemplar y añade "
          "secciones (cimentaciones, barreras de sonido, analisis "
          "estructural). Este ejemplar es la edicion 2016: lo imprime en sus "
          "PDF 2 y 3, y por eso `resolucion` se corrigio en T1 (decia la RD "
          "de 2018). La edicion citada NO cambia y las citas siguen validas "
          "contra este archivo (sha1); cual rige el expediente es de "
          "'edicion_legal_que_rige_el_expediente' (EXT-6: es la unica fuente "
          "DEROGADA por acto, y elegir la citada exige la fecha de inicio "
          "del expediente y el regimen transitorio de la RD 19-2018-MTC/14; "
          "no comparte ventana con las normas tecnicas de EE.UU., que van a "
          "'edicion_que_rige_el_expediente'). "
          "N1 DEL PLAN DE NORMAS 2 (2026-11-24): la edicion 2018 esta en "
          "normas/ y es la Fuente MP2018, con `convive_con` cruzado. La RD "
          "19-2018-MTC/14, leida en el ejemplar de 2018 (PDF 1 a 3), tiene "
          "cinco articulos y NINGUNA disposicion transitoria: aprueba el "
          "Manual (art. 1), lo pone en vigencia al dia siguiente de su "
          "publicacion (art. 3) y deroga la RD 041-2016-MTC/14 de este "
          "ejemplar (art. 4); su considerando dice que las modificaciones "
          "«no son sustanciales y se contraen a aspectos formales». Los 29 "
          "numerales que el registro cita de este ejemplar se buscaron en la "
          "edicion 2018 (fichas N1MP-02 y N1MP-03): ningun VALOR que entre "
          "en el calculo cambio; la de 2018 corrige tres de las erratas de "
          "imprenta que el registro declaraba (el signo de K_AE, el lado del "
          "1.2 de k_h0 y el numeral 2.3.1.1.12.3, que pasa a 2.8.1.1.12.3), "
          "conserva la del «tercio central» y cambia la redaccion del "
          "Glosario y de la Introduccion. Las citas de este archivo siguen "
          "validas contra el (sha1); cada una tiene su par en MP2018."),
)

# --- N1 del plan de normas 2 (2026-11-24) --- LA EDICION VIGENTE del Manual
# de Puentes. Convive con MP (la de 2016, contra la que estan verificadas las
# citas que el calculo consume) y NO la sustituye en el registro: cual rige
# el expediente es 'edicion_legal_que_rige_el_expediente', y sigue vacio.
# Lo que N1 midio, para que no haya que volver a medirlo:
#   - PAGINACION: «Pagina N» en la cabecera de las 630 paginas del Manual
#     (PDF 5 a 634), N = PDF - 4 en las 630; las cuatro primeras son la RD
#     19-2018-MTC/14 (PDF 1 a 3) y la caratula (PDF 4), sin folio. Coincide
#     con las «seiscientos treinta (630) paginas» del art. 1 de la RD.
#   - TEXTO: el plan la anotaba como escaneo sin capa de texto, y no lo es:
#     626 de las 634 paginas entregan texto. Las ocho que no son la RD y la
#     caratula (PDF 1 a 4), los tres mapas nacionales de isoaceleraciones
#     del Apendice A3 (PDF 568 a 570, imp. 564 a 566) y una figura del
#     Apendice P (PDF 613). Las ecuaciones compuestas con fuente simbolica
#     salen ilegibles por texto («n•R = 1.2 7ijIX4d» donde la pagina dibuja
#     k_h0 = 1.2 F_pga PGA): una cita que depende de una ecuacion se
#     verifica por IMAGEN, y su `metodo` lo dice.
MP2018 = Fuente(
    id="MP2018",
    titulo="Manual de Puentes",
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="Diciembre de 2018 (actualizacion de la edicion 2016)",
    anio=2018,
    resolucion="RD 19-2018-MTC/14",
    archivo_pdf="normas/Manual de Puentes 2018 (RD 19-2018-MTC-14).pdf",
    sha1="8ccf94e82b9a8bff30d182f4f814993b4c6dbaba",
    paginas_pdf=634,
    paginacion=Corrida(desfase=4),
    reemplaza_a="MP (Manual de Puentes 2016, RD 041-2016-MTC/14)",
    convive_con=("MP",),
    vigencia=_confirmada(
        acto_aprobatorio="RD 19-2018-MTC/14",
        pendiente_gabinete=("confirmar en el portal del MTC que ninguna RD "
            "posterior modifico o sustituyo este Manual: la "
            "busqueda de N1 no encontro ninguna, que no es lo "
            "mismo que leer el portal"),
        fecha=VIGENCIA_VERIFICADA_EL_N1MP,
        como=VIGENCIA_COMO_N1MP),
    nota=("ENTRA EN N1 DEL PLAN DE NORMAS 2 (2026-11-24), desde "
          "`normas_2/` del repositorio de normas. Es la edicion VIGENTE: la RD "
          "19-2018-MTC/14 (20-12-2018), impresa en sus PDF 1 a 3, la aprueba "
          "con 630 paginas (art. 1), la pone en vigencia al dia siguiente de "
          "su publicacion en El Peruano (art. 3) y deroga la RD "
          "041-2016-MTC/14 (art. 4). NO TRAE REGIMEN TRANSITORIO: ningun "
          "articulo ni disposicion ampara a los expedientes iniciados bajo la "
          "edicion 2016. La Presentacion (pag. impresa 38) la declara "
          "actualizacion de la de 2016 «incorporando en gran parte» la AASHTO "
          "LRFD 7a ed. y su Interim de 2015. Convive con MP (`convive_con` "
          "cruzado) y no la sustituye en el registro: cual rige el expediente "
          "lo declara el proyectista en "
          "'edicion_legal_que_rige_el_expediente', que sigue vacio. Cada una "
          "de las 29 citas de MP tiene aqui su par MP2018.* con "
          "`corresponde_en` cruzado; el contraste esta en las fichas "
          "N1MP-02 y N1MP-03 de docs/decisiones_diferidas.md. El mapa de PGA "
          "del Apendice A3 (PDF 568, imp. 564) es el MISMO raster que el de "
          "la edicion 2016 (PDF 553): mismas dimensiones, diferencia media de "
          "3 niveles sobre 255, ruido de recompresion JPEG sin estructura "
          "(ficha N1MP-04)."),
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
    vigencia=_confirmada(
        acto_aprobatorio="RD 10-2014-MTC/14",
        pendiente_gabinete=("leer el listado de manuales del portal del MTC, "
            "que no fue legible")
    ),
    nota=("VIGENCIA (T1): la RD "
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
    vigencia=_confirmada(
        acto_aprobatorio="RD 03-2013-MTC/14",
        pendiente_gabinete=("leer la RD 22-2013-MTC/14 (actualizacion de la "
            "EG-2013), que probablemente es la que este "
            "ejemplar imprime como «Revisada y Corregida a "
            "Junio 2013»")
    ),
    nota=("El desfase de 8 es grande y por eso es la fuente donde mas facil "
          "es citar una pagina corrida: la impresa 976 es la PDF 984, y "
          "confundir las dos es exactamente el hallazgo NOR-EG-01. "
          "VIGENCIA (T1): no aparece "
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
    vigencia=_confirmada(
        acto_aprobatorio="RM 183-2026-VIVIENDA",
        pendiente_gabinete=("leer la RM 217-2026-VIVIENDA (transitoria de la "
            "E.030), que no fue legible")
    ),
    nota=("VIGENCIA (T1): la RM "
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
    vigencia=_confirmada(
        acto_aprobatorio="RM 406-2018-VIVIENDA",
        pendiente_gabinete=("leer el indice del RNE en gob.pe (SENCICO), que "
            "no fue legible")
    ),
    nota=("VIGENCIA (T1): la RM "
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
    vigencia=_confirmada(
        acto_aprobatorio="DS 010-2009-VIVIENDA",
        pendiente_gabinete=("vigilar la RM que apruebe la actualizacion en "
            "curso (grupo de trabajo de la RM "
            "066-2025-VIVIENDA)")
    ),
    nota=("VIGENCIA (T1): la E.060 de "
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
    # --- T-7a --- Y las preliminares en romanas: i = PDF 5, medido pagina a
    # pagina de la i (indice) a la xxii (agradecimientos); la «List of
    # Symbols» va de la xv a la xix (PDF 19 a 23).
    paginacion=PorCapitulo(base={
        "1": 38, "2": 62, "3": 82, "4": 126, "5": 136, "6": 162, "7": 181,
        "A": 189, "B": 202, "C": 210,
        "DG1": 271, "DG2": 285, "DG3": 293, "DG4": 312,
    }, romanas=4),
    convive_con=("HDS5_SI_1985",),
    vigencia=_confirmada(),
    nota=("Es la edicion que gobierna: es la unica de las dos que imprime las "
          "conversiones SI (19.63 y 1.811). "
          "VIGENCIA (T1): la "
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
    vigencia=_posterior(
        ("HDS-5 Third Edition, FHWA-HIF-12-026 (2012), presente en normas/ "
            "como HDS5_3ED")
    ),
    nota=("EL «si» DEL NOMBRE DEL ARCHIVO ES DEL REPOSITORIO, NO DEL "
          "DOCUMENTO, y conviene decirlo asi: la portada no se rotula «SI» ni "
          "«metric» en ninguna parte -- dice «September 1985» y "
          "«FHWA-IP-85-15» --; el unico «SI» del frontispicio es el enlace a "
          "una tabla anexa «U.S. - SI Conversions», y las laminas del "
          "Apendice D llevan rotulos «Metric Version» / «English Version». "
          "El cuerpo opera en unidades inglesas con rotulos duales «ft (m)»: "
          "sus ecs. (4b) y (5) imprimen 29 y no 19.63, y su gravedad es "
          "«32.2 ft/s/s (9.8 m/s/s)». Leerla literal «en SI» reproduce el "
          "error que K_FRICCION_SI existe para atrapar: 29/19.63 = 1.477, un "
          "+47.7 % sobre el TERMINO de friccion, que en CP-8 sube H de "
          "0.4977 a 0.5455 m (+9.6 % sobre H). Ver la "
          "Discrepancia DIS-HDS5-EDICIONES. "
          "VIGENCIA (T1), Y YA "
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
    vigencia=_posterior(
        ("AASHTO LRFD Bridge Design Specifications, 10th Edition (LRFDBDS-10, "
            "2024)"),
        pendiente_gabinete=("conseguir la 10a ed. y medir que articulos de los "
            "citados cambiaron, en especial las Secciones 3 y "
            "5")
    ),
    nota=("VIGENCIA (T1): AASHTO "
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
    vigencia=_posterior(
        "AASHTO M 170M-23 (2023; equivalente ASTM C76M-22)",
        pendiente_gabinete=("conseguir la M 170M-23 y comparar sus Tablas 1 a "
            "5 con las de este ejemplar")
    ),
    nota=("Escaneo con OCR de mala calidad: el volcado devuelve «Speciñcation» "
          "y «Rcinforcc». Sirve para orientarse, y para CITAR hay que "
          "renderizar la pagina; medido en el cierre de SIS-F-13 (C09) pagina "
          "a pagina: las Tablas 1 a 4 (PDF 3 a 7 y 9) NO se pueden "
          "transcribir de este ejemplar, porque su imagen es una "
          "recomposicion OCR y no un escaneo, con digitos equivocados en la "
          "propia imagen (371 por 375, 1390 por 1350, «3tS0» por 3150, "
          "«6tXI» por 600) y filas superpuestas (2100 sobre 2250); la PDF 8 "
          "es un fragmento casi en blanco. La Tabla 5 (Clase V) SI: la PDF "
          "10 es un escaneo real, legible, girado 90 grados, y su columna de "
          "diametros (27 filas, 300 a 3600 mm) y sus paredes B y C estan "
          "transcritas por imagen en AASHTO_M170M.T5, que es el dorado del "
          "concreto de CP11; la PDF 11 (continuacion) vuelve a ser OCR. "
          "VE-2 (g): la Table 6 (PDF 20) tambien es recomposicion OCR; se "
          "transcribe de 300 a 2700 mm con nueve celdas corregidas, cada "
          "una fijada por la Tabla 5 y por la conversion pulgada-milimetro "
          "de la propia tabla (AASHTO_M170M.T6, DIS-M170M-T6-RECOMPOSICION). "
          "VIGENCIA (T1): AASHTO "
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
    vigencia=_posterior(
        "AASHTO M 36M/M 36-24 (2024)",
        pendiente_gabinete=("conseguir la M 36M/M 36-24, unica via de cerrar "
            "la pagina impresa «M 36-5» que a este ejemplar le "
            "falta")
    ),
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
          "VIGENCIA (T1): AASHTO "
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
    vigencia=_posterior(
        "ASTM A760/A760M-25",
        pendiente_gabinete=("conseguir la -25 en ingles, que cerraria a la vez "
            "la vigencia y la reserva de traduccion")
    ),
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
        "VIGENCIA (T1): ASTM publica "
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
    vigencia=_posterior(
        "ASTM A796/A796M-21",
        pendiente_gabinete=("conseguir la -21 y comprobar si el procedimiento "
            "de los num. 7 a 11 cambio")
    ),
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
        "VIGENCIA (T1): ASTM publica "
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
    vigencia=_posterior(
        "AASHTO M 294-25 (2025)",
        pendiente_gabinete=("conseguir el original -11 (reverifica la "
            "traduccion) o el -25 (cita la vigente); son dos "
            "compras distintas")
    ),
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
        "VIGENCIA (T1): AASHTO publica "
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


DG2018 = Fuente(
    id="DG2018",
    titulo=("Manual de Carreteras: Diseño Geométrico DG-2018 (MTC, «Revisada "
            "y Corregida a Enero de 2018»)"),
    emisor="MTC — Direccion General de Caminos y Ferrocarriles",
    edicion="DG-2018",
    anio=2018,
    # LO QUE EL EJEMPLAR IMPRIME Y LO QUE NO. La caratula (PDF 1) rotula
    # «MANUAL DE CARRETERAS: DISEÑO GEOMÉTRICO DG – 2018» y la Presentacion
    # (PDF 9, impresa 8) dice «Lima, Enero de 2018» y que es la actualizacion
    # de la DG-2014 «aprobado por R.D. N° 028 - 2014 - MTC/14»; NO imprime la
    # RD que aprueba ESTA edicion --- «03-2018» da cero paginas en las 285
    # ---. La RD 03-2018-MTC/14 se verifico en EXT-6 por busqueda web: El
    # Peruano (dispositivo 1614481-1, 07-02-2018) y gob.pe (MTC, normas
    # legales 10438) la publican como la que aprueba el «Manual de
    # Carreteras - Diseño Geometrico DG 2018» de 284 paginas, que son las 285
    # de este PDF menos la caratula. Es verificacion externa, no del
    # ejemplar, y por eso se dice aqui y no se calla.
    resolucion="RD 03-2018-MTC/14",
    archivo_pdf="normas/Manual.de.Carreteras.DG-2018.pdf",
    sha1="96ea04423a7e0e7fc44b5cd5d8824d6166a8e816",
    paginas_pdf=285,
    # MEDIDO en EXT-6 barriendo las 285 paginas con `cabeceras`: 284 imprimen
    # «Página n» con n = PDF - 1 (la PDF 199 imprime 198, la PDF 200 imprime
    # 199); la unica que no confirma es la PDF 1, la caratula, que no imprime
    # numero. No se asumio el +1 por analogia con el Manual de Puentes: se
    # conto.
    paginacion=Corrida(desfase=1),
    vigencia=_confirmada(
        acto_aprobatorio="RD 03-2018-MTC/14",
        pendiente_gabinete=("leer la RD 03-2018-MTC/14 en El Peruano y el "
                            "listado de manuales del portal del MTC, que no "
                            "fueron legibles"),
        fecha=VIGENCIA_VERIFICADA_EL_EXT6, como=VIGENCIA_COMO_EXT6),
    nota=(
        "ENTRO EN normas/ EL 2026-09-18 Y EL REGISTRO NO LA CONOCIO HASTA "
        "EXT-6 (EXT-N-02, PC-23): los PDF llegaron cuatro dias despues del "
        "ultimo commit de codigo y este archivo la tenia como AUSENTE. Lo que "
        "el proyecto le pide, y solo eso: (1) la definicion juridica del "
        "derecho de via (304.07.01), que remite al Reglamento Nacional de "
        "Gestion de Infraestructura Vial, DS 034-2008-MTC (RNGIV, presente "
        "desde N2 del plan 12: su art. 35 repite la frase del dominio "
        "publico, y su art. 2 remite a su vez las definiciones a un glosario "
        "del MTC que no esta en normas/); "
        "(2) el piso [N] del ancho del derecho de via --- la Tabla 304.09 por "
        "clase de carretera y el incremento de 5.00 m «del borde mas alejado "
        "de las obras de drenaje» (304.07.02, impresas 198-199) ---, que es "
        "el requisito juridico de V5 y NO una condicion hidraulica: el 304.07 "
        "no enuncia ninguna, y el metodo con que se decide si el embalse cabe "
        "en la faja sigue siendo [A] ('remanso_derecho_via'); (3) los taludes "
        "referenciales de terraplen de la Tabla 304.11 (304.10, impresa 208), "
        "que acotan la ventana de 'talud_terraplen' sin sustituir a la "
        "seccion tipica del expediente; y (4) la clasificacion de carreteras "
        "por demanda y orografia (Capitulo I), que es lo que 'clase_de_via' "
        "tiene que leer para elegir fila en el Cuadro 4.1 del Manual de "
        "Suelos y en la Tabla 304.09. "
        "VIGENCIA (EXT-6): la RD 03-2018-MTC/14 (El Peruano, 07-02-2018; "
        "gob.pe, MTC, normas legales 10438) sigue publicada como la que "
        "aprueba el Manual, el portal del MTC publica este mismo archivo en "
        "su carpeta de manuales de carreteras, y ninguna RD posterior del MTC "
        "sobre este Manual ni edicion «DG-20xx» posterior aparece en los "
        "resultados."),
)

# ===========================================================================
# T-0 - Las dos fuentes tecnicas que llegaron al repositorio de normas
# ===========================================================================
# HEC-14 Y EL WSDOT HYDRAULICS MANUAL ESTUVIERON EN EL CENSO DE AUSENTES hasta
# T-0 (2026-11-11). El dueño del proyecto las subio al repositorio de normas
# (`Andy-rba30/Normas`, commit `eebfcca`) y T-0 las da de alta aqui con sha1,
# paginas y paginacion MEDIDOS abriendo cada PDF, para que T-4 (velocidad y
# abrasion en TMC y HDPE) y T-8 (proteccion de salida) puedan citarlas con
# pagina. Tres cosas que conviene leer antes de usarlas:
#
#   1. NO ESTAN EN `normas/` DE LA APP, y es deliberado: esa carpeta no gana
#      PDF (T-12 los retira; INF-5.2.3 es el problema de redistribuir normas
#      con copyright en un repositorio publico). Viven en el repositorio de
#      normas y se encuentran por `NORMAS_DIR` (`ruta_pdf`, abajo). Hasta
#      T-12 estaban por eso en el censo `SOLO_EN_EL_REPO_NORMAS`, que se
#      retiro cuando T-12 saco de `normas/` las demas: hoy TODAS viven alli,
#      y un checkout sin ese repositorio enlazado SALTA los tests que las
#      abren en vez de fallar.
#   2. T-0 NO TRANSCRIBE NINGUNA CITA SUYA. `citas.py` no tiene ninguna
#      `Cita` con estos `fuente_id`: una cita es numeral, pagina impresa,
#      pagina PDF y frase leida, y eso es de la sesion que la consume. Lo que
#      la `nota` de cada una adelanta --la pagina de la Tabla 8-4, el indice
#      real de capitulos de HEC-14-- esta leido del PDF y sirve para ORIENTAR
#      esa transcripcion, no para sustituirla.
#   3. SON [C]: fuente tecnica reconocida de EE.UU., no norma peruana. Que
#      esten presentes no convierte en [N] nada que se apoye en ellas.
HEC14 = Fuente(
    id="HEC14",
    titulo=("HEC-14 «Hydraulic Design of Energy Dissipators for Culverts and "
            "Channels» (Hydraulic Engineering Circular No. 14, "
            "FHWA-NHI-06-086)"),
    emisor="FHWA — Federal Highway Administration / National Highway Institute",
    # LO QUE LA PORTADA IMPRIME (PDF 1): «Publication No. FHWA-NHI-06-086 /
    # July 2006 / Hydraulic Engineering Circular No. 14, Third Edition». La
    # PDF 3 es una hoja añadida, «Listing of Updates and Corrections (errata &
    # corrigenda)», con ocho correcciones del Capitulo 4 fechadas el 13 de
    # agosto y el 1 de octubre de 2012 y la frase «This list includes all
    # known items as of Monday 1 October 2012»: el ejemplar es la tercera
    # edicion de 2006 CON su fe de erratas de 2012 delante, y por eso tiene
    # 287 paginas.
    edicion="Third Edition, July 2006 (con la fe de erratas del 1 de octubre "
            "de 2012 en la PDF 3)",
    anio=2006,
    archivo_pdf="normas/hec14.pdf",
    sha1="1bffcbe220cd67e4c0de8b87b46d1ece64ce7217",
    paginas_pdf=287,
    # MEDIDO en T-0 barriendo las 287 paginas: el folio «c-n» es la ULTIMA
    # linea de texto de cada pagina del cuerpo. Diecisiete bases; 270 paginas
    # confirman. No confirman las trece preliminares (PDF 1 portada, PDF 2
    # formulario DOT F 1700.7, PDF 3 fe de erratas, PDF 4-13 romanas i a x) y
    # cuatro del cuerpo cuyo folio no sale por texto (PDF 15 = 1-2, PDF 143 =
    # 8-20, PDF 148 = 8-25 y PDF 222 = 11-1, que lo imprime ARRIBA): las
    # cuatro caen donde la base de su capitulo predice. El separador es el
    # guion, no el punto: «10-1» no es 10,1.
    paginacion=PorCapitulo(base={
        "1": 13, "2": 27, "3": 31, "4": 41, "5": 53, "6": 63, "7": 77,
        "8": 123, "9": 157, "10": 201, "11": 221, "12": 245,
        "A": 249, "B": 259, "C": 277, "D": 279, "R": 283,
    }),
    vigencia=Vigencia(
        estado=VIGENCIA_CONFIRMADA, fecha=VIGENCIA_VERIFICADA_EL_T0,
        como=VIGENCIA_COMO_T0,
        pendiente_gabinete=("leer la biblioteca de hidraulica de la FHWA "
                            "(fhwa.dot.gov/engineering/hydraulics), que no "
                            "fue legible, y confirmar que no hay cuarta "
                            "edicion")),
    nota=(
        "ENTRO EN EL REPOSITORIO DE NORMAS (commit eebfcca) Y T-0 LA DIO DE "
        "ALTA el 2026-11-11; hasta entonces era AUSENTE con «el "
        "dimensionamiento de disipadores, fuera de alcance hoy». Lo que el "
        "proyecto le va a pedir es de T-8: el apron de enrocado al que HDS-5 "
        "remite en su Sec. 5.3.2 «Scour at Outlets», pag. impresa 5.11 "
        "(«many state DOTs use riprap aprons (HEC-14, Section 10.2)», segun "
        "lo declara `M6_proteccion`), que hoy ese modulo cubre solo con el "
        "d50 de Laushey del Manual MTC. "
        "EL INDICE REAL DE CAPITULOS, leido de las paginas de arranque de "
        "cada uno, porque la cadena T los cita de memoria y tres no "
        "coinciden: 1 Energy Dissipator Design (1-1, PDF 14); 2 Erosion "
        "Hazards (2-1, PDF 28); 3 Culvert Outlet Velocity and Velocity "
        "Modification (3-1, PDF 32); 4 Flow Transitions (4-1, PDF 42); 5 "
        "Estimating Scour at Culvert Outlets (5-1, PDF 54); 6 Hydraulic Jump "
        "(6-1, PDF 64); 7 Internal (Integrated) Dissipators (7-1, PDF 78); 8 "
        "Stilling Basins (8-1, PDF 124); 9 Streambed Level Dissipators (9-1, "
        "PDF 158); 10 Riprap Basins and Aprons (10-1, PDF 202: 10.1 Riprap "
        "Basin, 10.2 Riprap Aprons, 10.3 riprap aguas abajo de disipadores); "
        "11 Drop Structures (11-1, PDF 222); 12 Stilling Wells (12-1, PDF "
        "246); Apendice A sistema metrico (A-1, PDF 250); B tirante critico "
        "y flujo uniforme por forma (B-1, PDF 260); C consideraciones "
        "estructurales (C-1, PDF 278); D Riprap Apron Sizing Equations (D-1, "
        "PDF 280); Referencias (R-1, PDF 284). O sea: la SOCAVACION a la "
        "salida es el Capitulo 5 (no el 3), la VELOCIDAD de salida el 3 (no "
        "el 4-5) y los disipadores INTERNOS el 7. "
        "TEXTO: la prosa se extrae bien; las ECUACIONES salen partidas en "
        "renglones sueltos (la 10.1 llega como fragmentos «h», «⎛ D ⎞», "
        "«s = 0.86⎜»), de modo que una formula se transcribe mirando la "
        "pagina renderizada y no copiando el volcado. Opera en unidades "
        "duales, SI primero («m (ft)»). "
        "VIGENCIA (T-0): los resultados de busqueda del sitio de la FHWA y "
        "de los repositorios estatales que la reproducen listan HEC 14 como "
        "tercera edicion, FHWA-NHI-06-086, julio de 2006, con la fe de "
        "erratas del 1 de octubre de 2012; ninguno menciona una cuarta "
        "edicion, y la propia fe de erratas dice «No update to the "
        "publication is planned at this time»."),
)

WSDOT_HM = Fuente(
    id="WSDOT_HM",
    titulo="WSDOT Hydraulics Manual (M 23-03)",
    emisor=("Washington State Department of Transportation — Engineering "
            "and Regional Operations, Hydraulics Office"),
    # LO QUE LA PORTADA IMPRIME (PDF 1): «Hydraulics Manual / M 23-03.12 /
    # April 2026 / Engineering and Regional Operations Hydraulics Office», y
    # cada pagina del cuerpo lo repite en su cabecera («WSDOT Hydraulics
    # Manual M 23-03.12 / Page 8-27 / April 2026»). El censo de ausentes
    # decia «M 23-03, 2019» por suponer la edicion; los criterios 'v_max_tmc'
    # y 'v_max_hdpe' ya citaban «M 23-03.12 (abril 2026)», y ESA es la que
    # llego: no hay dos ediciones entre las que elegir.
    edicion="M 23-03.12, April 2026",
    anio=2026,
    archivo_pdf="normas/HydraulicsManual.pdf",
    sha1="b34bb7bd448c249301e2a1a82234be70e8b6d916",
    paginas_pdf=325,
    # MEDIDO en T-0 barriendo las 325 paginas por la cabecera «Page c-n»:
    # quince bases, confirmadas por 311 paginas. El capitulo 9 es una sola
    # pagina (9-1, PDF 265) y los apendices 2A, 7A, 7B y 10A tienen base
    # propia (el 10A son nueve paginas, PDF 290-298; «G» es el glosario). Las
    # catorce que no confirman son las preliminares: PDF 1 portada, PDF 2
    # aviso legal y PDF 3-14, el indice, foliado en romanas (i a xii). La
    # etiqueta lleva guion y el capitulo puede llevar letra: «10A-2» no es
    # un numero.
    paginacion=PorCapitulo(base={
        "1": 14, "2": 36, "2A": 63, "3": 65, "4": 86, "5": 100, "6": 120,
        "7": 130, "7A": 210, "7B": 211, "8": 215, "9": 264, "10": 265,
        "10A": 289, "G": 298,
    }),
    vigencia=Vigencia(
        estado=VIGENCIA_CONFIRMADA, fecha=VIGENCIA_VERIFICADA_EL_T0,
        como=VIGENCIA_COMO_T0,
        pendiente_gabinete=("leer la pagina del manual en wsdot.wa.gov, que "
                            "no fue legible: los resultados dan capitulos ya "
                            "rotulados M 23-03.12 (abril de 2026) y una "
                            "pagina indice que todavia anunciaba la .11 "
                            "(abril de 2025)")),
    nota=(
        "ENTRO EN EL REPOSITORIO DE NORMAS (commit eebfcca) Y T-0 LA DIO DE "
        "ALTA el 2026-11-11; hasta entonces era AUSENTE y 'v_max_tmc' y "
        "'v_max_hdpe' la citaban sin poder abrirla (MAT-O14, R48-030). "
        "LO QUE DICE DONDE LO DICE, leido del ejemplar para que T-4 lo "
        "transcriba con su firma: el §8-6 «Abrasion» abre en la pag. impresa "
        "8-27 (PDF 242) y la Tabla 8-4 «Pipe Abrasion Levels» ocupa la 8-27 y "
        "la 8-28 (PDF 242-243). ES UNA TABLA DE NIVELES DE ABRASION, NO DE "
        "VELOCIDADES MAXIMAS: cuatro filas --Non-abrasive («Velocities less "
        "than 3 ft/s»), Low abrasive («less than 6 ft/s»), Moderately "
        "abrasive («from 6 to 15 ft/s») y Severely abrasive («greater than "
        "15 ft/s»)-- con la proteccion de solera recomendada en cada una. La "
        "prohibicion del termoplastico en el nivel severo NO esta en la "
        "tabla sino en el §8-3.3 «Thermoplastic Pipe», pag. impresa 8-13 "
        "(PDF 228): «because thermoplastic pipe cannot be structurally "
        "reinforced, it shall not be used for severely abrasive conditions "
        "as described in Table 8-4». Y EN ESTA EDICION la fila «Severely "
        "abrasive» de la tabla (pag. 8-28) no nombra al termoplastico: su "
        "ultima frase dice «Sacrificial metal pipe exhibits better abrasion "
        "characteristics than metal or concrete. However, it generally "
        "cannot be reinforced to provide additional invert protection and "
        "shall not be used in this condition», y para el metal pide «at "
        "least two standard gages» o solera de concreto, sin prohibirlo. De "
        "modo que el techo de 15 ft/s = 4.572 m/s del HDPE se sostiene por "
        "el §8-3.3 MAS el umbral de la tabla, y el del TMC no es un techo "
        "de la fuente: es lo que la ficha de 'v_max_tmc' ya declaraba, y lo "
        "que T-4 punto 3 tiene que resolver. "
        "RESUELTO EN T-4: 'v_max_hdpe' sigue [C], con la prohibicion citada "
        "del §8-3.3 y el umbral de la Tabla 8-4; 'v_max_tmc' paso a [A] con "
        "ventana (3.048, 4.572) m/s, cuyo piso son los 10 ft/s del §3-3.5 "
        "(pag. impresa 3-11, PDF 76). T-4 transcribio ademas el §8-5.1 (pH), "
        "el §8-5.2 (resistividad) y el §8-4.3 (zonas de corrosion), que "
        "sostienen la matriz de durabilidad de M2. "
        "UNIDADES: inglesas (ft/s, in). "
        "VIGENCIA (T-0): los resultados de busqueda del sitio de WSDOT "
        "muestran capitulos del manual rotulados «M 23-03.12, April 2026», "
        "que es la edicion de este ejemplar, y ninguna posterior; la pagina "
        "indice del manual todavia listaba la M 23-03.11 (abril de 2025). "
        "El manual se revisa cada año: quien lo cite en 2027 tiene que "
        "volver a mirar."),
)

# --- VE-3.6 (Familia C, cierre de la mitad de la rasante de VC1-01) --- EL
# USBR «Design of Small Canal Structures» (1978). Es la fuente [C] del
# criterio con que se juzga si un cruce altera la rasante hidraulica de un
# canal: la obra se diseña para que sus perdidas no superen el desnivel que
# el perfil del canal provee en el cruce (F, «water surface differential»,
# num. 2-6). Documento de dominio publico del Bureau of Reclamation. El
# ejemplar es un ESCANEO con capa de texto OCR (458 paginas): el texto de las
# frases citadas sale limpio de la capa, y la numeracion es continua: la pag.
# impresa N es la PDF N + 23 en el cuerpo del Capitulo II medido (22 -> 45,
# 23 -> 46, 24 -> 47). Bajado de una copia universitaria (luk.staff.ugm.ac.id)
# porque usbr.gov no respondio desde la sesion.
USBR_DSCS = Fuente(
    id="USBR_DSCS",
    titulo="Design of Small Canal Structures",
    emisor="U.S. Department of the Interior — Bureau of Reclamation",
    edicion="1978 (Aisenbrey, Hayes, Warren, Winsett y Young)",
    anio=1978,
    archivo_pdf="normas/USBR Design of Small Canal Structures (1978).pdf",
    sha1="75510d711ce1f6643333937a1ea38f3b469cc1f7",
    paginas_pdf=458,
    paginacion=Corrida(desfase=23),
    vigencia=Vigencia(
        estado=VIGENCIA_CONFIRMADA, fecha=VIGENCIA_VERIFICADA_EL_VE3,
        como=("busqueda web (WebSearch) desde la sesion de VE-3.6: la "
              "pagina de resumenes de manuales del Bureau en usbr.gov "
              "(techreferences/mands/mands-abstracts/manabs3.html) lo lista "
              "como «Design of Small Canal Structures, 1978», sin edicion "
              "posterior: confirmada por lo que el resultado transcribe, como "
              "T-0 confirmo HEC-14; el PDF de usbr.gov no respondio y el "
              "ejemplar viene de una copia universitaria del mismo escaneo"),
        pendiente_gabinete=("confirmar en usbr.gov que no hay revision "
                            "posterior a 1978 y que el escaneo es el del "
                            "Bureau")),
    nota=(
        "ENTRA EN VE-3.6 para la Familia C (paso de canal): la Sec. 2.3 de la "
        "hoja de ruta prohibe alterar la rasante hidraulica del canal y "
        "ninguna fuente de normas/ decia como juzgarlo. El num. 2-6 (Road "
        "Crossings, Design Example, pags. impresas 23-24) lo hace: F, el "
        "desnivel de la lamina normal entre aguas arriba y aguas abajo del "
        "cruce que el perfil del canal provee, contra las perdidas "
        "calculadas de la obra. Es [C]: fuente tecnica de EE.UU., no norma "
        "peruana; el dato F es del proyecto del canal (ANA / Junta de "
        "Usuarios)."),
)

# --- VE-3.12 --- La D-load de 0.3 mm de las Clases III a V del tubo de
# concreto (decisiones 1 y 7 del dueño, 2026-11-17). El ejemplar de M 170M de
# normas/ no las deja leer; este documento del USACE las imprime en un
# EJEMPLO RESUELTO (Apendice B), no en una tabla normativa: fuente [C]
# secundaria, y su cita lo dice.
USACE_EM_1110_2_2902 = Fuente(
    id="USACE_EM_1110_2_2902",
    titulo="Conduits, Culverts, and Pipes (EM 1110-2-2902)",
    emisor="U.S. Army Corps of Engineers",
    edicion="31 Mar 1997, Change 1 del 31 Mar 1998",
    anio=1998,
    archivo_pdf=("normas/USACE EM 1110-2-2902 Conduits, Culverts and Pipes "
                 "(1997, Change 1 1998).pdf"),
    sha1="cfdc3bfd1c9291d30c98de11f27b1f1fbf7a95d8",
    paginas_pdf=87,
    paginacion=PorCapitulo(base={"B": 64}, separadores=("-",)),
    vigencia=Vigencia(
        estado=VIGENCIA_GABINETE, fecha=VIGENCIA_VERIFICADA_EL_VE3,
        como=("no se busco su vigencia: se usa SOLO por la tabla «ASTM C76 "
              "Class and D0.01» de su ejemplo resuelto del Apendice B (pag. "
              "impresa B-7), como fuente secundaria de las D-load de 0.3 mm "
              "de AASHTO M 170M / ASTM C76M que el ejemplar de normas/ no deja "
              "leer"),
        pendiente_gabinete=("sustituir la cita por la tabla de un ejemplar "
                            "legible de AASHTO M 170M (la vigente) o de ASTM "
                            "C76M en cuanto el dueño lo consiga")),
    nota=(
        "ENTRA EN VE-3.12 (decisiones 1 y 7 del dueño): las D-load de 0.3 mm "
        "de las Clases III, IV y V del tubo de concreto. Es un EJEMPLO "
        "RESUELTO del Apendice B («Chapter 3: Circular Precast Concrete Pipe "
        "for Small Dams and Major Levees — D-Load Analysis»), sin edicion de "
        "ASTM C76 y sin unidades impresas en la tabla (se deducen de la misma "
        "pagina y de la B-8, «D0.01 = 57 N/m/mm (1,172 plf/ft) ASTM C76M "
        "Class III»). Las cifras son las NOMINALES de la norma metrica (100 y "
        "140 no son 95.76 ni 143.64), que es la que el EG-2013 506 manda "
        "(AASHTO M-170M). Es [C], no [N]: el numeral no se verifica contra "
        "el ejemplar normativo. Verificacion independiente en "
        "proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/"
        "clases_iii_v_astm_c76.md."),
)

# --- N3 (plan 12, 2026-11-24) --- HEC-11, «Design of Riprap Revetment», en
# su version metrica. HEC-14 remite a ella el filtro bajo el apron («A filter
# blanket should also be provided as described in HEC 11 (Brown and Clyde,
# 1989)», Sec. 10.2, pag. impresa 10-18) y el tamaño de la piedra con el
# receptor alto (Sec. 10.1.3, pag. impresa 10-4). Estuvo en `normas_2/` del
# repositorio de normas desde su commit `ce4c90e` y N3 la paso a `normas/`.
# Tres propiedades del ejemplar, medidas en N3, que gobiernan sus citas:
#
#   1. NO IMPRIME FOLIO. Es la captura a PDF (Acrobat Web Capture 4.0, 10 de
#      agosto de 2000, segun sus metadatos) de las paginas web de la FHWA: 193
#      hojas sin cabecera ni pie numerado (barrido el texto de las 193; las
#      lineas que son solo un numero son celdas de tabla, y las PDF 47, 49,
#      66 y 82 renderizadas no imprimen folio). Es el caso de HDS5_SI_1985 y
#      de AASHTO_M294_TRAD: `SinDeterminar`, «s/n» como pagina impresa, la
#      cita localizada por numeral y pagina PDF, y SIN FIRMA (invariante T6).
#   2. EL TEXTO ES EXTRAIBLE Y LIMPIO; LAS ECUACIONES Y LAS RELACIONES DE LOS
#      EJEMPLOS SON IMAGENES. La Ec. (14) y las razones del paso 13 de los dos
#      ejemplos se leyeron renderizando la pagina (`extraccion png`, 2x y 4x).
#   3. LLEVA LA MARCA «Archived» EN TODAS SUS PAGINAS, y la biblioteca de la
#      FHWA la lista entre las publicaciones archivadas con su sucesora (ver
#      `vigencia`).
VIGENCIA_VERIFICADA_EL_N3 = "2026-11-24"

HEC11 = Fuente(
    id="HEC11",
    titulo=("HEC-11 «Design of Riprap Revetment» (Hydraulic Engineering "
            "Circular No. 11, FHWA-IP-89-016), version metrica"),
    emisor="FHWA — Federal Highway Administration",
    # LO QUE EL EJEMPLAR IMPRIME: la PDF 1, «Design of Riprap Revetment / HEC
    # 11 / Metric Version» y el aviso de que el manual se convirtio al sistema
    # metrico al pasarlo a formato electronico («keeping the document as close
    # to the original as possible»); la PDF 152, la hoja de documentacion
    # tecnica del original: «FHWA-IP-89-016», «March 1989», «Scott A. Brown,
    # Eric S. Clyde». El numero de la version metrica (FHWA-IF-00-022-1, 2000)
    # NO lo imprime el ejemplar: es el que da la biblioteca de la FHWA.
    edicion=("version metrica (SI) de la de marzo de 1989, conversion "
             "electronica de la FHWA; la biblioteca de la FHWA la lista como "
             "FHWA-IF-00-022-1 (2000)"),
    anio=2000,
    archivo_pdf="normas/hec11si.pdf",
    sha1="583b1c305c57030a93f3885d5e160fb45a023651",
    paginas_pdf=193,
    paginacion=SinDeterminar(
        por_que=("el ejemplar es la captura web de la FHWA y no imprime "
                 "numero de pagina en ninguna de sus 193 hojas (medido en N3 "
                 "sobre el texto de las 193 y sobre las PDF 47, 49, 66 y 82 "
                 "renderizadas). Sus citas se localizan por numeral y pagina "
                 "PDF, llevan «s/n» como pagina impresa y no se firman (T6), "
                 "con el precedente de HDS5_SI_1985 y AASHTO_M294_TRAD")),
    texto_extraible=True,
    vigencia=Vigencia(
        estado=VIGENCIA_POSTERIOR, fecha=VIGENCIA_VERIFICADA_EL_N3,
        como=("lectura directa (WebFetch) desde la sesion de N3 del listado "
              "de publicaciones archivadas de la biblioteca de hidraulica de "
              "la FHWA (fhwa.dot.gov/engineering/hydraulics/library_listing."
              "cfm?archived=1), que da dos filas: «HEC 11 · Design of Riprap "
              "Revetment · 1989 · FHWA-IP-89-016 · No · HEC-23» y «HEC 11 · "
              "Design of Riprap Revetment SI · 2000 · FHWA-IF-00-022-1 · Yes "
              "· HEC-23» (codigo, titulo, año, numero, en linea, sustituida "
              "por); la tercera edicion de HEC-23 (FHWA-NHI-09-111 y -112, "
              "septiembre de 2009) por busqueda web (WebSearch) sobre la "
              "pagina de la FHWA y el registro de TRB"),
        edicion_posterior=(
            "ninguna edicion de HEC-11: la FHWA la archiva y la da por "
            "sustituida por HEC-23 «Bridge Scour and Stream Instability "
            "Countermeasures» (3a ed., FHWA-NHI-09-111 y -112, septiembre de "
            "2009), que es otro documento"),
        pendiente_gabinete=(
            "leer HEC-23 3a ed. (su guia de diseño de filtros, Vol. 2) y "
            "contrastar sus criterios granulometricos con la Ec. (14); "
            "confirmar si hay una edicion de HEC-23 posterior a 2009 (un "
            "registro de TRB, View/1875786, no fue legible)")),
    nota=(
        "ENTRA EN N3 (plan 12) para el FILTRO GRANULAR bajo el enrocado de "
        "salida, que hasta aqui era solo un requisito declarado (fichas T8-05 "
        "y VE5-M6-04): HEC-14, vigente, remite expresamente a HEC 11 «(Brown "
        "and Clyde, 1989)» el filtro bajo el apron (cita HEC14.10.2#FILTRO) "
        "y el tamaño de la piedra con el receptor alto (HEC14.10.1.3#"
        "FIGURA_10_3). Lo que el proyecto le pide, y solo eso: los criterios "
        "granulometricos del filtro de la Sec. 4.4.1 (Ec. 14, pasante del "
        "tamiz N.º 200, espesor de la manta), los limites granulometricos "
        "del enrocado de la Tabla 2 (Sec. 4.2), el espesor de la capa de "
        "enrocado de la Sec. 4.3 y la cama de grava bajo el geotextil de la "
        "Sec. 4.4.2. Es [C]: fuente tecnica de EE.UU., no norma peruana, y "
        "la propia PDF 151 lo dice: «This report does not constitute a "
        "standard, specification, or regulation». Su ambito es el "
        "revestimiento de taludes y cauces («bank protection»), no la salida "
        "de una alcantarilla: lo que se toma de ella para el apron se toma "
        "por la remision de HEC-14, y cada paso lo dice. "
        "ERRATAS PROPIAS DE ESTA VERSION, medidas en N3 y no corregidas en "
        "ningun valor del proyecto: (1) la fila del 50 % de la Tabla 2 dice "
        "«1.0 D50 to 1.4 D50» y su columna de pesos «1.0 W50 to 1.5 W50», que "
        "con W proporcional a D^3 da 1.0 a 1.145 D50 --el proyecto no usa "
        "esa fila--; (2) el paso 13 del Ejemplo 2 (PDF 81-82) rotula «D15"
        "[filter]» la razon 0.15/0.00014, que es contra el suelo, y acepta "
        "«0.15/0.03 = 5 ≥ 5» frente a la Ec. (14), que imprime «< 5» (el "
        "texto dice «5 or less»). Y una diferencia que no es errata: el paso "
        "10 de los dos ejemplos toma T = 2·D50 para el espesor del enrocado, "
        "por encima del minimo de 1.5·D50 de la Sec. 4.3, sin decir por que. "
        "Los tests del filtro se contrastan contra el Ejemplo 1, que no tiene "
        "ninguna de las dos erratas. "
        "VIGENCIA (N3): archivada por la FHWA y sustituida por HEC-23, que "
        "es OTRO documento y no una edicion de esta. Que edicion rige el "
        "expediente lo declara el proyectista en "
        "'edicion_que_rige_el_expediente', como en las demas fuentes "
        "tecnicas con sucesora publicada."),
)

# ===========================================================================
# N2 del plan 12 (2026-11-24) - EL MARCO LEGAL: Ley 29338, su Reglamento y
# el RNGIV
# ===========================================================================
# LOS TRES ESTUVIERON EN EL CENSO DE AUSENTES (LEY_29338 desde §15 del plan,
# RNGIV desde EXT-6). El dueño los subio al repositorio de normas en
# `normas_2/` (commit ce4c90e) y N2 del plan 12 los paso a `normas/` y los
# da de alta aqui con sha1, paginas y paginacion MEDIDOS. Tres cosas que
# conviene leer antes de citarlos:
#
#   1. SON COMPILACIONES, NO EL DIARIO OFICIAL. La Ley y el RNGIV son textos
#      del SPIJ (Ministerio de Justicia) con las modificatorias insertas y
#      notas «(*)»; el Reglamento de la Ley es la compilacion que publica la
#      Direccion General de Asuntos Ambientales Energeticos del MINEM. Lo que
#      se cita es lo que ESTE archivo imprime (el sha1 lo ancla); la fecha
#      hasta la que cada compilacion llega va en `edicion`, y lo que la
#      compilacion no recoge, en `vigencia.pendiente_gabinete`.
#   2. EL REGLAMENTO DE LA LEY ES FUENTE PROPIA y no «la mitad» de
#      `LEY_29338`, que es lo que la ausente decia («Ley 29338 ... y su
#      reglamento»): es otro documento, otro acto (un decreto supremo y no
#      una ley), otro emisor y otra paginacion -- el Reglamento imprime
#      folio y la Ley no --. Juntarlos habria obligado a una paginacion que
#      no es de ninguno de los dos.
#   3. NINGUNO FIJA UN NUMERO QUE EL PROGRAMA USE. Lo que el proyecto les
#      pide es JURIDICO: que la faja marginal es un bien de dominio publico
#      hidraulico cuyo ancho fija la Autoridad Administrativa del Agua cuerpo
#      de agua por cuerpo de agua (Ley art. 74, Reglamento arts. 113 y 114),
#      que intervenir un cauce exige autorizacion previa (Ley art. 7,
#      Reglamento art. 277 b), y que el ancho del derecho de via lo aprueba
#      por resolucion la autoridad competente de la red vial (RNGIV arts. 4,
#      32 y 35). El ancho de la faja marginal de ESTE cauce y el del derecho
#      de via de ESTE tramo son datos de sitio [S]; ninguno es [N].
LEY_29338 = Fuente(
    id="LEY_29338",
    titulo="Ley 29338, Ley de Recursos Hidricos",
    emisor="Congreso de la Republica del Peru",
    # LO QUE EL EJEMPLAR IMPRIME: «Ley de Recursos Hídricos / LEY Nº 29338»
    # (PDF 1), con notas «(*) NOTA SPIJ» y concordancias insertas; la mas
    # reciente que nombra es la Ley 32513 «publicada el 04 diciembre 2025»
    # (PDF 1). La ley se dio el 30-03-2009 («Dado en la Casa de Gobierno, en
    # Lima, a los treinta días del mes de marzo del año dos mil nueve», PDF
    # 42); la fecha de su publicacion en El Peruano el ejemplar NO la imprime
    # y no se escribe de memoria.
    edicion=("Ley 29338, compilacion con notas del SPIJ y concordancias "
             "hasta la Ley 32513 (04-12-2025)"),
    anio=2009,
    resolucion="Ley 29338",
    archivo_pdf="normas/Ley 29338 Ley de Recursos Hidricos (SPIJ).pdf",
    sha1="ac47b59be519288b6aaa3d0eb32bc2b96dd80416",
    paginas_pdf=49,
    # NO HAY FOLIO QUE MEDIR: es el caso de AASHTO_M294_TRAD y de
    # HDS5_SI_1985, y se resuelve igual. El texto de las 49 hojas no contiene
    # ningun numero de pagina (los unicos renglones numericos sueltos, en las
    # PDF 27 a 29, son el «29» de «29 diciembre 2016» partido por la capa de
    # texto) y las hojas 1, 5, 25 y 35 renderizadas no imprimen cabecera ni
    # pie numerado. Una ley se cita por ARTICULO, y sus citas se localizan
    # por pagina PDF con «s/n» como pagina impresa y sin firma (T6), censadas
    # en `CITAS_SIN_FIRMA_A_PROPOSITO`; T2 y T3 comprueban su texto en cada
    # corrida con PyMuPDF, porque la capa de texto es limpia.
    paginacion=SinDeterminar(
        por_que=("el ejemplar no imprime numero de pagina en ninguna de sus "
                 "49 hojas: ni cabecera ni pie numerado (medido en N2 del "
                 "plan 12 sobre el texto de las 49 y sobre las hojas 1, 5, "
                 "25 y 35 renderizadas). Sus citas se localizan por pagina "
                 "PDF, llevan «s/n» como pagina impresa y no se firman (T6), "
                 "con el precedente de AASHTO_M294_TRAD")),
    texto_extraible=True,
    vigencia=Vigencia(
        estado=VIGENCIA_CONFIRMADA, fecha=VIGENCIA_VERIFICADA_EL_MARCO_LEGAL,
        como=VIGENCIA_COMO_MARCO_LEGAL,
        acto_aprobatorio="Ley 29338",
        pendiente_gabinete=(
            "leer en el SPIJ o en El Peruano el texto vigente de los arts. "
            "6, 7 y 74 y la fecha de publicacion de la ley, que el ejemplar "
            "no imprime")),
    nota=(
        "ENTRO A normas/ EN N2 DEL PLAN 12 (2026-11-24); hasta entonces era "
        "AUSENTE con «faja marginal y autorizacion de obras en cauce» y «el "
        "tramite, no el calculo». Las dos cosas se confirmaron leyendo el "
        "ejemplar. FAJA MARGINAL: el art. 74 (PDF 25) manda mantener una "
        "faja marginal en los terrenos aledaños a los cauces y remite su "
        "extension al Reglamento («El Reglamento determina su extensión»); "
        "el art. 6, num. 1, la cuenta entre los bienes naturales asociados "
        "al agua junto con los cauces (PDF 5). Ningun articulo fija un "
        "ancho: «faja(s) marginal(es)» aparece 7 veces en las 49 hojas (PDF "
        "5, 25 dos, 26, 44 y 46 dos), las de las PDF 26, 44 y 46 en "
        "concordancias que nombran los reglamentos de delimitacion de la "
        "ANA (R.J. 300-2011-ANA y R.J. 332-2016-ANA), que NO estan en "
        "normas/; la R.J. 300-2011-ANA, que es la que la concordancia del "
        "art. 74 imprime, esta derogada por la R.J. 332-2016-ANA segun los "
        "resultados de busqueda; la Ley nombra esta ultima en la PDF 46; "
        "fuente ausente RJ_332_2016_ANA. AUTORIZACION: el art. 7 (PDF 5) "
        "exige autorizacion previa "
        "de la Autoridad Administrativa del Agua para toda intervencion «de "
        "los particulares» que altere un bien de dominio publico hidraulico, "
        "y el art. 104 (PDF 35) atribuye a la Autoridad Nacional la "
        "aprobacion de las obras de infraestructura publica o privada que se "
        "proyecten en los cauces. El registro apoya la exigencia de "
        "autorizar una obra en un cauce en el art. 104, que dice «pública o "
        "privada» (cita LEY_29338.104), y en el art. 277 b del Reglamento, "
        "que no distingue quien la hace; el art. 7 queda como lo que define "
        "el dominio publico hidraulico (dictamen de Fable sobre N2). "
        "VIGENCIA (N2 del plan 12): la compilacion trae notas hasta "
        "diciembre de 2025 y los arts. 6, 7 y 74 no llevan nota de "
        "modificacion; la ley sigue siendo la base de las resoluciones de la "
        "ANA de 2025 que aparecen en los resultados."),
)

REG_LEY_29338 = Fuente(
    id="REG_LEY_29338",
    titulo=("Reglamento de la Ley 29338, Ley de Recursos Hidricos, aprobado "
            "por DS 001-2010-AG"),
    emisor=("Poder Ejecutivo (refrendo del Presidente del Consejo de "
            "Ministros y del Ministro de Agricultura); compilacion de la "
            "Direccion General de Asuntos Ambientales Energeticos del MINEM"),
    # LO QUE EL EJEMPLAR IMPRIME: «DECRETO SUPREMO Nº 001-2010-AG», «Dado en
    # la Casa de Gobierno, en Lima, a los veintitrés días del mes de marzo
    # del año dos mil diez» (PDF 1), y en cada pie «Reglamento de la Ley Nº
    # 29338, Ley de Recursos Hídricos / Decreto Supremo Nº 001-2010-AG». La
    # modificacion mas reciente que la compilacion inserta es la del DS
    # 016-2017-MINAGRI, «publicado el 16 noviembre 2017» (PDF 35 y 36).
    edicion=("DS 001-2010-AG, compilacion con las modificatorias hasta el "
             "DS 016-2017-MINAGRI (16-11-2017)"),
    anio=2010,
    resolucion="DS 001-2010-AG",
    archivo_pdf="normas/DS 001-2010-AG Reglamento de la Ley 29338.pdf",
    sha1="68fa38ad900a01e2d51384899374ea84fe0272c1",
    paginas_pdf=83,
    # MEDIDO en N2 del plan 12 barriendo las 83 paginas: el pie de cada una
    # imprime el folio n = PDF (la capa de texto lo entrega como segundo
    # renglon, debajo del rotulo «Reglamento de la Ley Nº 29338...»). 83 de
    # 83 confirman; no hay portada sin folio.
    paginacion=Corrida(desfase=0),
    vigencia=Vigencia(
        estado=VIGENCIA_CONFIRMADA, fecha=VIGENCIA_VERIFICADA_EL_MARCO_LEGAL,
        como=VIGENCIA_COMO_MARCO_LEGAL,
        acto_aprobatorio="DS 001-2010-AG",
        pendiente_gabinete=(
            "confirmar en el SPIJ o en El Peruano que los arts. 113, 114 y "
            "277 no se modificaron despues del 16-11-2017, la ultima "
            "modificatoria que esta compilacion inserta")),
    nota=(
        "ENTRO A normas/ EN N2 DEL PLAN 12 (2026-11-24) como Fuente propia: "
        "la ausente LEY_29338 lo englobaba («y su reglamento»). Lo que el "
        "proyecto le pide, y solo eso: (1) que las fajas marginales son "
        "bienes de dominio publico hidraulico y que sus DIMENSIONES las fija "
        "la Autoridad Administrativa del Agua para cada cuerpo de agua "
        "(art. 113, pag. 37); (2) que la delimitacion sigue CRITERIOS sin "
        "cifra -- la magnitud de las estructuras hidraulicas, el espacio de "
        "las defensas, los usos publicos y la maxima crecida sin eventos "
        "excepcionales -- (art. 114, pag. 37); y (3) que construir o "
        "modificar sin autorizacion obras de cualquier tipo en las fuentes "
        "naturales de agua o en sus bienes asociados es infraccion (art. 277 "
        "b, pag. 75). NINGUN ARTICULO FIJA UN ANCHO de faja marginal: "
        "«faja(s) marginal(es)» aparece 21 veces en las 83 paginas (PDF 36, "
        "37, 38 y 75) y en ninguna con una magnitud en metros (afirmacion "
        "negativa SIN_ANCHO_DE_FAJA_MARGINAL en citas.py). El art. 113.2 "
        "remite a «los criterios establecidos en el Reglamento» y la "
        "concordancia que la pagina 37 imprime es la R.J. 300-2011-ANA "
        "(Reglamento para la Delimitacion y Mantenimiento de Fajas "
        "Marginales), que no esta en normas/ y esta derogada por la R.J. "
        "332-2016-ANA segun los resultados de busqueda; la Ley nombra esta "
        "ultima en la PDF 46; fuente ausente RJ_332_2016_ANA. Si ese "
        "reglamento de la ANA fija anchos minimos no se verifico (segun los "
        "resultados, su art. 12; no leido). "
        "VIGENCIA (N2 del plan 12): no se encontro modificacion de los "
        "arts. 113 ni 114 en los resultados, y una resolucion del Tribunal "
        "Nacional de Resolucion de Controversias Hidricas de 2025 aplica el "
        "literal b) del art. 277 con el texto de esta compilacion."),
)

RNGIV = Fuente(
    id="RNGIV",
    titulo=("Reglamento Nacional de Gestion de Infraestructura Vial, aprobado "
            "por DS 034-2008-MTC, y sus modificatorias"),
    emisor="MTC (Poder Ejecutivo)",
    # LO QUE EL EJEMPLAR IMPRIME: cabecera «Sistema Peruano de Información
    # Jurídica / Ministerio de Justicia», «DECRETO SUPREMO Nº 034-2008-MTC»,
    # «Dado en la Casa de Gobierno, en Lima, a los veinticuatro días del mes
    # de octubre del año dos mil ocho» (PDF 1), «cuarenta y cinco (45)
    # artículos y cinco (05) disposiciones complementarias finales», y en
    # cada pie «Actualizado al: 28/05/13». ES EL DECRETO QUE EL DG-2018
    # NOMBRA: su art. 4 es el de las autoridades competentes, que es el que
    # el §304.07.02 del DG-2018 cita, y su Titulo III el del derecho de via.
    edicion=("DS 034-2008-MTC, texto del SPIJ «Actualizado al: 28/05/13», "
             "con las modificatorias de los DS 003-2009-MTC, 011-2009-MTC y "
             "012-2011-MTC insertas"),
    anio=2008,
    resolucion="DS 034-2008-MTC",
    archivo_pdf=("normas/DS 034-2008-MTC Reglamento Nacional de Gestion de "
                 "Infraestructura Vial (SPIJ).pdf"),
    sha1="4e41d4a1a9143ab0611ef8010c9b9598dc6f2a10",
    paginas_pdf=17,
    # MEDIDO en N2 del plan 12 barriendo las 17 paginas: el pie del SPIJ
    # imprime «Página n» con n = PDF en las 17.
    paginacion=Corrida(desfase=0),
    vigencia=Vigencia(
        estado=VIGENCIA_CONFIRMADA, fecha=VIGENCIA_VERIFICADA_EL_MARCO_LEGAL,
        como=VIGENCIA_COMO_MARCO_LEGAL,
        acto_aprobatorio="DS 034-2008-MTC",
        # --- Dictamen de Fable sobre N2 --- la reserva tiene que verse en el
        # manifiesto, que no imprime `pendiente_gabinete`: va en su campo.
        modificatorias_posteriores=(
            "DS 021-2016-MTC (arts. 10 y 12 a 16) y DS 015-2024-MTC (lit. c "
            "del 4.2 y lit. c del 11.2), no leídos"),
        pendiente_gabinete=(
            "leer en El Peruano el DS 021-2016-MTC (que segun los resultados "
            "modifica los arts. 10 y 12 a 16) y el DS 015-2024-MTC (que "
            "modifica el literal c del num. 4.2 del art. 4 y el literal c "
            "del num. 11.2 del art. 11), posteriores a esta compilacion, y "
            "confirmar que los arts. 2, 32 y 35 no cambiaron; y la Ley 32598 "
            "(publicada en El Peruano el 16-05-2026 segun los resultados; "
            "modifica la Ley 27181), sobre las autoridades competentes en la "
            "jerarquizacion vial, que aparece en los resultados y no se "
            "leyo")),
    nota=(
        "ENTRO A normas/ EN N2 DEL PLAN 12 (2026-11-24); era AUSENTE desde "
        "EXT-6. EL ARCHIVO QUE ESTUVO EN normas/ HASTA 5196dd2 NO ERA ESTE: "
        "era la publicacion de El Peruano del 10-02-2006 (12 paginas, sha1 "
        "6f6b473c9048212975914f8db46650218a371c50), anterior en dos años al "
        "decreto y con otra numeracion; no se restauro, y este ejemplar es "
        "otro archivo (ficha EXT-6-01). Lo que el proyecto le pide es lo que "
        "el DG-2018 le remite (304.07.01 y 304.07.02), y leerlo cambio una "
        "cosa: EL RNGIV NO DEFINE EL TERMINO «DERECHO DE VIA». Su art. 2 "
        "(PDF 4) remite las definiciones al «Glosario de términos de uso "
        "frecuente en proyectos de infraestructura vial» (RM "
        "660-2008-MTC/02), que no esta en normas/. Lo que si dice: la faja "
        "del derecho de via es bien de dominio publico, inalienable e "
        "imprescriptible (art. 35, PDF 13: la misma frase del DG-2018 "
        "304.07.01); cada autoridad competente del art. 4 establece y "
        "aprueba por resolucion del titular el ancho de la faja de su red "
        "(art. 32, PDF 12); y esas autoridades son el MTC, los gobiernos "
        "regionales y los gobiernos locales, por red vial (art. 4.2, PDF 4). "
        "El ancho del derecho de via de un tramo es por eso un dato de la "
        "resolucion de su autoridad, y no un valor que el programa pueda "
        "poner. El art. 18 (PDF 11) dice que los manuales son «documentos de "
        "carácter normativo y de cumplimiento obligatorio», que es lo que la "
        "nota del Manual de Suelos cita por el catalogo de SENCICO. "
        "VIGENCIA (N2 del plan 12): el decreto sigue vigente -- el DS "
        "015-2024-MTC lo modifica en 2024 --, y la compilacion de 2013 no "
        "recoge el DS 021-2016-MTC ni el DS 015-2024-MTC; el segundo toca el "
        "literal c) del num. 4.2, que la cita RNGIV.4 por eso no transcribe. "
        "Tampoco se leyo la Ley 32598 (El Peruano, 16-05-2026 segun los "
        "resultados; modifica la Ley 27181), sobre las autoridades "
        "competentes en la jerarquizacion vial, que aparece en los "
        "resultados. La reserva va en `vigencia.modificatorias_posteriores`, "
        "que el manifiesto imprime (ficha N2L-02)."),
)

FUENTES: Dict[str, Fuente] = {
    f.id: f for f in (
        MC_HHD, MP, MP2018, MS, EG2013, E030, E050, E060,
        HDS5_3ED, HDS5_SI_1985, AASHTO_LRFD_9,
        AASHTO_M170M, AASHTO_M36, ASTM_A760, ASTM_A796, AASHTO_M294_TRAD,
        DG2018, HEC14, WSDOT_HM, USBR_DSCS, USACE_EM_1110_2_2902, HEC11,
        LEY_29338, REG_LEY_29338, RNGIV,
    )
}

# --- T-12 --- `SOLO_EN_EL_REPO_NORMAS` SE RETIRO. Era el censo de las
# fuentes presentes cuyo PDF no estaba en `normas/` de este repositorio
# (HEC-14 y el WSDOT Hydraulics Manual, dados de alta por T-0), y su propio
# comentario decia que era TRANSITORIO: T-12 retiro los dieciocho PDF de
# `normas/` (comprobados antes, byte a byte por sha1, contra el repositorio
# de normas; INF-5.2.3) y desde entonces TODAS las fuentes presentes y los
# dos PDF censados viven solo en el repositorio de normas enlazado por
# `NORMAS_DIR`. La guardia de PC-23 (`tests/test_ext6_registro_normativo.py`)
# mira ahora una sola carpeta (ficha T0-01, que lo preveia, y T12-01).


# ===========================================================================
# PC-23 - PDF que ESTAN en normas/ y NO son Fuente del registro
# ===========================================================================
# LA GUARDIA QUE FALTABA. T17 vigila que una fuente AUSENTE no tenga PDF;
# nadie vigilaba el sentido inverso, y asi estuvieron cuatro dias tres PDF
# (EXT-N-02). Desde EXT-6 `tests/test_ext6_registro_normativo.py` lista
# normas/*.pdf y exige que cada archivo sea Fuente presente o este AQUI, con
# su motivo. Estos dos no se registran porque ningun calculo ni ninguna
# verificacion del proyecto cita un numeral suyo: registrarlos seria sumar
# fuentes sin citas al indice, que es ruido, no trazabilidad. Los sha1 y las
# paginas estan MEDIDOS (`python3 -m src.normativa.extraccion sha1 <pdf>`)
# para que el dia que se citen no haya que volver a medirlos y para que el
# test note si el archivo cambia.
PRESENTES_SIN_REGISTRAR: Dict[str, PdfPresenteSinRegistrar] = {
    p.id: p for p in (
        PdfPresenteSinRegistrar(
            id="MSV_2017",
            titulo="Manual de Seguridad Vial (2017)",
            emisor="MTC — Direccion General de Caminos y Ferrocarriles",
            archivo_pdf="normas/Manual_de_Seguridad_Vial_2017.pdf",
            sha1="cc47c736c38503005a85966002a3ed267524b240",
            paginas_pdf=461,
            por_que_no_se_registra=(
                "ninguna fase de la hoja de ruta v8 cita un numeral suyo: "
                "trata la seguridad vial de la plataforma (barreras, zonas "
                "despejadas, señalizacion), no el drenaje transversal. Lo "
                "unico que roza al proyecto es la zona despejada junto a "
                "cabezales y aletas, y la v8 no la evalua"),
            que_lo_registraria=(
                "que una verificacion del proyecto --- por ejemplo, la "
                "posicion del cabezal respecto de la zona despejada de la "
                "via --- necesitara citar un numeral suyo; entonces entra "
                "como Fuente con paginacion medida y esa cita"),
            # SIN RESOLUCION A PROPOSITO: el ejemplar no imprime la RD que
            # lo aprueba («MTC/14» da cero paginas en las 461) y no se
            # verifico por otra via en EXT-6; escribirla de memoria seria
            # la regla 8 al reves. Se rellena el dia que se lea.
            resolucion=""),
        PdfPresenteSinRegistrar(
            id="MDCTA_2016",
            titulo=("Manual de Dispositivos de Control del Transito Automotor "
                    "para Calles y Carreteras"),
            emisor="MTC — Direccion General de Caminos y Ferrocarriles",
            archivo_pdf=("normas/MANUAL DE DISPOSITIVOS DE CONTROL DE TRÁNSITO "
                         "AUTOMOTOR PARA CALLES Y CARRETERAS.pdf"),
            sha1="58b948b70ca1fd28e133559471b2a4dba28afb1c",
            paginas_pdf=532,
            por_que_no_se_registra=(
                "es la norma de señalizacion vial (señales, marcas, "
                "semaforos); ninguna fase de la v8 ni ninguna verificacion "
                "de M1 a M10 cita un numeral suyo. La demarcacion del derecho "
                "de via que el DG-2018 §304.07.03 remite a la RM 404-2011-"
                "MTC/02 tampoco pasa por este manual"),
            que_lo_registraria=(
                "que el expediente incorporara la señalizacion de las obras "
                "de drenaje (hitos del derecho de via, señales de badenes) "
                "como entregable del calculo; hoy no lo es"),
            # Verificada en el ejemplar: la PDF 2 imprime la RD 016-2016-MTC/14.
            resolucion="RD 016-2016-MTC/14"),
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
    vigencia=_posterior(
        "AASHTO M 294-25 (2025)",
        pendiente_gabinete=("decidir cual de las dos compras (-11 o -25) y "
            "hacerla")
    ),
    nota=("VIGENCIA (T1): la edicion "
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

# WSDOT_HM SALIO DE ESTE CENSO EN T-0: esta arriba, entre las presentes, con
# sha1, 325 paginas y paginacion por capitulo medidos. Su ficha de ausente
# decia «M 23-03, 2019» y que desbloquearia «'v_max_tmc' y 'v_max_hdpe', hoy
# [C] sin PDF». Conseguida y leida, lo que desbloquea es la CITA con pagina
# de la Tabla 8-4 y del §8-3.3 --que T-4 transcribe--, y lo que hace aparecer
# es que la tabla es de niveles de abrasion y no de velocidades maximas: el
# techo del HDPE lo sostiene el §8-3.3 y el del TMC no es de la fuente.

# DG2018 SALIO DE ESTE CENSO EN EXT-6: esta arriba, entre las presentes, con
# sha1, 285 paginas y desfase +1 medidos. Su ficha de ausente decia que
# desbloquearia 'clase_de_via' y 'carriles_por_sentido'; conseguida y leida,
# lo que desbloquea de verdad es el PISO [N] del ancho del derecho de via
# (Tabla 304.09 y el +5.00 m del 304.07.02) y la ventana de
# 'talud_terraplen' (Tabla 304.11). La clase de via NO la desbloquea el
# documento: sigue siendo un dato de sitio que fija el IMDA del estudio de
# demanda, y el Manual solo aporta la clasificacion contra la que leerlo.

# RNGIV SALIO DE ESTE CENSO EN N2 DEL PLAN 12 (2026-11-24): esta arriba,
# entre las presentes, con sha1, 17 paginas y desfase 0 medidos. Su ficha de
# ausente contaba la decision sobre el archivo borrado, y sigue en pie: lo
# que hubo en normas/ hasta 5196dd2 era la publicacion de El Peruano del
# 10-02-2006 (sha1 6f6b473c...), no el DS 034-2008-MTC, y no se restauro; lo
# que entro es OTRO archivo, el texto del SPIJ del decreto. Decia que
# desbloquearia «la cita textual de la definicion juridica del derecho de via
# y de quien lo aprueba ... no mueve ningun numero». Conseguido y leido, lo
# segundo se cumplio (arts. 4 y 32) y lo primero NO: el RNGIV no define el
# termino, remite sus definiciones a un glosario aparte (art. 2, RM
# 660-2008-MTC/02, ausente). Lo que si cita textual es la naturaleza
# juridica de la faja (art. 35). Y no mueve ningun numero, como decia.

# LAS DOS NORMAS DE PRODUCTO DEL CAJON PREFABRICADO, que el proyecto NO usa y
# censa para poder decir por que el marco no lleva norma de producto
# (EXT-N-03). AASHTO LRFD 12.4.2.4 (pag. 12-8) manda que las estructuras
# prefabricadas de cajon cumplan M 259 (ASTM C789) y M 273 (ASTM C850), y
# 12.11.1 (pag. 12-68) dice que sus dimensiones estandar estan ahi. El
# proyecto decidio el marco VACIADO IN SITU (docs/ruta_familia_c.md §14.1)
# justamente porque estas dos no estan: elegir prefabricado sin su norma de
# producto habria dejado cada dimension como un [A] sin fuente.
AASHTO_M259 = _ausente(
    "AASHTO_M259",
    ("AASHTO M 259 «Precast Reinforced Concrete Box Sections for Culverts, "
     "Storm Drains, and Sewers» (ASTM C789)"),
    "AASHTO", "M 259 (edicion no determinada)", 0,
    Ausencia(
        por_que_se_cita=("AASHTO LRFD 12.4.2.4 y 12.11.1 la nombran como la "
                         "norma de producto y de dimensiones estandar del "
                         "cajon prefabricado"),
        que_desbloquearia=("la alternativa PREFABRICADA al marco vaciado in "
                           "situ de la Familia C: seria una decision nueva "
                           "de alcance (ruta_familia_c §14.1), no un dato"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente=("marco vaciado in situ, diseñado por AASHTO LRFD "
                           "Seccion 5 y Art. 12.11 y construido por EG-2013 "
                           "503 y 504")))

AASHTO_M273 = _ausente(
    "AASHTO_M273",
    ("AASHTO M 273 «Precast Reinforced Concrete Box Sections for Culverts, "
     "Storm Drains, and Sewers with Less Than 2 ft of Cover Subjected to "
     "Highway Loadings» (ASTM C850)"),
    "AASHTO", "M 273 (edicion no determinada)", 0,
    Ausencia(
        por_que_se_cita=("AASHTO LRFD 12.4.2.4 y 12.11.1 la nombran junto a "
                         "M 259 para el cajon prefabricado con menos de 2 ft "
                         "de cobertura"),
        que_desbloquearia=("lo mismo que M 259, para el caso de cobertura "
                           "baja; ninguna de las dos mueve el diseño in situ"),
        esfuerzo=Esfuerzo.COMPRA,
        sustituto_vigente=("marco vaciado in situ, diseñado por AASHTO LRFD "
                           "Seccion 5 y Art. 12.11 y construido por EG-2013 "
                           "503 y 504")))

# HEC14 SALIO DE ESTE CENSO EN T-0: esta arriba, entre las presentes, con
# sha1, 287 paginas y paginacion por capitulo medidos. Su ficha de ausente
# decia que desbloquearia «el dimensionamiento de disipadores, fuera de
# alcance hoy»: sigue fuera de alcance mientras T-8 no lo implemente, pero
# ya no por falta de la fuente.

# LEY_29338 SALIO DE ESTE CENSO EN N2 DEL PLAN 12 (2026-11-24): esta arriba,
# entre las presentes, y PARTIDA EN DOS -- la Ley (`LEY_29338`, sin folio) y
# su Reglamento (`REG_LEY_29338`, DS 001-2010-AG, desfase 0) --, porque la
# ausente las englobaba («Ley 29338 ... y su reglamento») y son dos actos y
# dos documentos. Decia que desbloquearia «el tramite, no el calculo», y
# leidas lo confirman: ninguna fija el ancho de una faja marginal (lo fija la
# Autoridad Administrativa del Agua para cada cuerpo de agua, Reglamento art.
# 113.2), y la autorizacion de obras en cauces es un tramite (Ley art. 7,
# Reglamento art. 277 b). V5 sigue sin evaluar la faja marginal, ahora por la
# razon verdadera: falta el dato de sitio, no la ley (ficha N2L-01).

# --- Dictamen de Fable sobre N2 --- LOS DOS DOCUMENTOS A LOS QUE EL MARCO
# LEGAL REMITE Y QUE NO ESTAN. Leer la Ley, su Reglamento y el RNGIV hizo
# aparecer dos remisiones que terminan fuera de normas/: el metodo con que la
# autoridad del agua fija el ancho de la faja marginal (su reglamento de
# delimitacion) y la definicion de «derecho de via» (el glosario del MTC al
# que remite el art. 2 del RNGIV). Se censan como falta, sin transcribir
# nada de ellos: lo que se sabe de su contenido es de resultados de busqueda,
# no de su lectura, y asi se dice.
RJ_332_2016_ANA = _ausente(
    "RJ_332_2016_ANA",
    "Reglamento para la Delimitacion y Mantenimiento de Fajas Marginales "
    "(R.J. 332-2016-ANA)",
    "ANA — Autoridad Nacional del Agua", "R.J. 332-2016-ANA", 2016,
    Ausencia(
        por_que_se_cita=("la Ley 29338 la nombra en sus concordancias (PDF "
                         "46: «Aprueban el Reglamento para la Delimitación y "
                         "Mantenimiento de Fajas Marginales»), y es donde la "
                         "autoridad pone el metodo con que fija el ancho de "
                         "la faja que el art. 113.2 del Reglamento de la Ley "
                         "le encarga (cita REG_LEY_29338.113.2)"),
        que_desbloquearia=("saber si fija anchos minimos por tipo de cauce "
                           "(segun resultados de busqueda, su art. 12; no "
                           "leido) y que entiende por delimitar; no mueve "
                           "ningun calculo actual: V5 no evalua la faja "
                           "marginal, y el ancho de la de un cauce sigue "
                           "siendo el de la resolucion de delimitacion de la "
                           "autoridad"),
        esfuerzo=Esfuerzo.DESCARGA_PUBLICA,
        sustituto_vigente=None),
    nota=("DEROGO LA R.J. 300-2011-ANA (su art. 3, segun resultados de "
          "busqueda), que es la que imprimen las concordancias del art. 74 de "
          "la Ley (PDF 25-26) y del art. 113 del Reglamento (pag. 37): esas "
          "dos concordancias de los ejemplares de normas/ apuntan a una "
          "resolucion derogada. Los resultados nombran ademas una "
          "modificatoria, la R.J. 201-2017-ANA, no leida."))

RM_660_2008_MTC = _ausente(
    "RM_660_2008_MTC",
    ("Glosario de terminos de uso frecuente en proyectos de infraestructura "
     "vial (RM 660-2008-MTC/02)"),
    "MTC", "RM 660-2008-MTC/02", 2008,
    Ausencia(
        por_que_se_cita=("es el destino de la remision del art. 2 del RNGIV "
                         "(cita RNGIV.2): el RNGIV no define sus terminos, y "
                         "el DG-2018 §304.07.01 remite al RNGIV las "
                         "«definiciones» del derecho de via"),
        que_desbloquearia="la definicion de «derecho de via»",
        esfuerzo=Esfuerzo.DESCARGA_PUBLICA,
        sustituto_vigente=None),
    nota=("No consta si fue sustituido por un glosario posterior del MTC; "
          "no se busco su vigencia."))

SERIES_SENAMHI_ANA = _ausente(
    "SERIES_SENAMHI_ANA", "Series hidrometeorologicas SENAMHI / ANA para la "
    "cuenca del corredor", "SENAMHI / ANA", "series de estacion", 0,
    Ausencia(
        # CORREGIDO EN T-0 (INF-5.1.1). Esta ficha decia «el Q de la Familia
        # A, hoy bloqueado» y «ninguno: el calculo se detiene, y debe», y
        # ninguna de las dos cosas la hace el programa: ningun modulo lee
        # 'homogeneidad_serie_fen' (`variables_entrada` lo censa sin
        # consumidor), un `Q_m3s` vacio en la Familia A es `DatoFaltanteError`
        # y no `CriterioPendienteError`, y un CSV con el caudal lleno corre
        # sin que nadie pregunte por la serie. Lo que la serie sostiene es el
        # SUSTENTO del caudal, que es responsabilidad del estudio
        # hidrologico; T-1 le da consumidor real al criterio.
        por_que_se_cita=("el sustento del Q de diseño de toda la Familia A "
                         "sale de ellas: sin la serie no hay IDF ni "
                         "tratamiento de la poblacion mixta por FEN que "
                         "declarar ('homogeneidad_serie_fen')"),
        que_desbloquearia=("el SUSTENTO del Q de la Familia A, que hoy "
                           "entra ya calculado por la columna `Q_m3s` sin "
                           "que el programa pueda comprobar de que serie "
                           "salio. Es la ausencia mas cara del expediente"),
        esfuerzo=Esfuerzo.GABINETE,
        sustituto_vigente=("ninguno. El programa NO se detiene por ella: un "
                           "`Q_m3s` lleno se calcula y el criterio sale en "
                           "el bloque de pendientes sin haber frenado nada; "
                           "quien recibe el CSV exige aparte el estudio "
                           "hidrologico que lo respalda")))

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
                           "del mapa declarada y verificable por imagen")),
    # --- N1 del plan de normas 2 --- El apendice esta en las DOS ediciones
    # presentes, y su mapa de PGA es el mismo raster en las dos (medido).
    nota=("Edicion 2016 (MP): mapa de PGA en la PDF 553, pag. impresa 552. "
          "Edicion 2018 (MP2018, la vigente): Apendice A3 en las pags. "
          "impresas 558 a 566, mapa de PGA en la PDF 568, pag. impresa 564, "
          "sin capa de texto. El mapa es el MISMO raster en las dos "
          "(797 x 1099 px; diferencia media de 3 niveles sobre 255, ruido de "
          "recompresion JPEG sin estructura), de modo que la lectura del "
          "corredor no depende de la edicion. La lectura que N1 hizo sobre "
          "ese raster esta en la ficha N1MP-04 de docs/decisiones_diferidas.md "
          "y NO cambio el valor de datos_sitio['PGA_roca_B']"))


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


def estado_de_vigencia(f: Fuente) -> Optional[EstadoDeVigencia]:
    """
    El estado de vigencia de una Fuente, leido de `Fuente.vigencia`, o None
    si la fuente no lo declara (solo puede pasar en una ausente: el esquema
    lo exige en toda presente).

    Hasta EXT-6 leia una marca de texto en la nota (T1) y levantaba
    ErrorDeRegistro si habia dos; el campo hace imposible el estado doble
    por construccion, y la funcion se conserva porque es lo que el manifiesto
    y los tests venian leyendo (ficha T1-01, cerrada en EXT-6).
    """
    return None if f.vigencia is None else f.vigencia.estado


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


def fuentes_con_eleccion_de_edicion_pendiente_legal(
        fuentes: Optional[Dict[str, Fuente]] = None) -> Tuple[str, ...]:
    """
    Las de `fuentes_con_eleccion_de_edicion_pendiente` cuya edicion citada
    fue DEROGADA POR UN ACTO (`Vigencia.derogado_por`): una norma legal
    peruana, aprobada y dejada sin efecto por resolucion. Elegir la citada
    no es una preferencia tecnica: exige la fecha de inicio del expediente
    y el acto del regimen transitorio que lo ampare (EXT-N-01, PC-26). Hoy
    es una: el Manual de Puentes. Va a
    'edicion_legal_que_rige_el_expediente'.
    """
    fuentes = FUENTES if fuentes is None else fuentes
    return tuple(id_ for id_ in fuentes_con_eleccion_de_edicion_pendiente(fuentes)
                 if fuentes[id_].vigencia.derogado_por)


def fuentes_con_eleccion_de_edicion_pendiente_tecnica(
        fuentes: Optional[Dict[str, Fuente]] = None) -> Tuple[str, ...]:
    """
    Las demas pendientes: normas tecnicas cuyo emisor publico una edicion
    posterior y a las que ningun acto peruano deroga. La eleccion es
    tecnica y del proyectista, y el Manual de Puentes de 2016 le pone un
    ancla que no se puede ignorar: su Introduccion adapta la AASHTO LRFD
    2014 (7a ed.) y PERMITE considerar sus actualizaciones (cita
    MP.INTRODUCCION#LRFD_2014). Van a 'edicion_que_rige_el_expediente'.
    """
    fuentes = FUENTES if fuentes is None else fuentes
    legales = set(fuentes_con_eleccion_de_edicion_pendiente_legal(fuentes))
    return tuple(id_ for id_ in fuentes_con_eleccion_de_edicion_pendiente(fuentes)
                 if id_ not in legales)


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


# ===========================================================================
# T-0 / T-12 - DONDE ESTAN LOS PDF EN DISCO: `NORMAS_DIR`, y solo alli
# ===========================================================================
# `Fuente.archivo_pdf` es un nombre LOGICO --«normas/hif12026.pdf»--, no una
# ruta que se pueda abrir tal cual: dice como se llama el archivo dentro de
# la carpeta de normas, este donde este esa carpeta. Hasta T-0 cada lector
# componia `RAIZ / fuente.archivo_pdf` por su cuenta (cuatro sitios en la
# suite y uno en `extraccion`), lo que cableaba la carpeta `normas/` de este
# repositorio como unico lugar posible. T-0 abrio una sola puerta, con DOS
# lugares: `$NORMAS_DIR` y, despues, `normas/` de este repositorio «mientras
# exista». T-12 RETIRO los dieciocho PDF de `normas/` (sha1 comprobado, uno a
# uno, contra el repositorio de normas antes del `git rm`; el historial los
# conserva: INF-5.2.3, ficha T12-01) y con ellos la caida: desde T-12 hay UN
# lugar, y esta es su puerta:
#
#   `$NORMAS_DIR`, si la variable esta definida: el clon del repositorio de
#   normas (`Andy-rba30/Normas`). Admite la raiz del clon o su subcarpeta
#   `normas/`, que es donde ese repositorio guarda los PDF.
#
# SIN LA VARIABLE NO HAY CARPETA DE NORMAS (`directorios_de_normas()` es la
# tupla vacia), `ruta_pdf` devuelve la ruta donde el enlace que falta pondria
# el archivo (`RUTA_SIN_ENLACE`, que no existe) y TODO lo que abre un PDF se
# salta diciendolo: es el tercer eje de entorno de la suite, que desde T-12
# abarca a todos los tests que abren un PDF y no solo a los de HEC-14 y WSDOT.
# Calcular no cambia: ningun modulo de calculo abre un PDF.
#
# POR QUE UNA VARIABLE Y NO UN SUBMODULO NI UN ENLACE SIMBOLICO (decision de
# T-0, ficha T0-01 de docs/decisiones_diferidas.md): el repositorio de normas
# lleva documentos con copyright (AASHTO, ASTM) y el README recomienda
# hacerlo privado; un submodulo ataria cada clon de la app a una credencial
# sobre ese repositorio y dejaria su URL y su commit versionados aqui. La
# variable no versiona nada, funciona con el repositorio publico o privado, y
# deja que un despliegue que solo CALCULA --que no necesita ni un PDF-- no
# tenga que clonar 330 MB.
#
# NINGUN MODULO DE CALCULO LLAMA A ESTO, y tiene que seguir asi: abrir un PDF
# es cosa de quien VERIFICA (la suite `-m pdf`, `python3 -m
# src.normativa.extraccion`, `proceso/verificar_sesion.py`), no de quien
# calcula. El registro se construye sin tocar el disco.
VARIABLE_NORMAS_DIR = "NORMAS_DIR"
SUBCARPETA_DEL_REPO_NORMAS = "normas"
# Donde se le esperaria a un PDF sin el enlace: una ruta RELATIVA con el
# nombre de la variable que falta, para que el mensaje de quien llama diga que
# hacer («$NORMAS_DIR/normas/hec14.pdf») y no apunte a una carpeta de este
# repositorio que ya no existe. No se abre nunca: `ruta_pdf` la devuelve para
# que quien llama decida con `.exists()` si salta.
RUTA_SIN_ENLACE = Path("$" + VARIABLE_NORMAS_DIR) / SUBCARPETA_DEL_REPO_NORMAS


def directorios_de_normas() -> Tuple[Path, ...]:
    """
    La carpeta donde se buscan los PDF: la de `$NORMAS_DIR` (si la variable
    esta definida y no vacia), o ninguna. Desde T-12 no hay caida a
    `normas/` de este repositorio: sus PDF se retiraron.

    Un `NORMAS_DIR` que apunta a una carpeta inexistente lanza
    `FileNotFoundError` y no se ignora: quien definio la variable quiso
    enlazar el repositorio de normas, y seguir sin el le daria una suite
    verde que no verifico lo que el creia. Es un fallo de entorno, no del
    expediente, y por eso no es `ErrorProyecto` (CLAUDE.md, «Excepciones»).
    """
    declarado = os.environ.get(VARIABLE_NORMAS_DIR, "").strip()
    if not declarado:
        return ()
    enlazado = Path(declarado).expanduser()
    if not enlazado.is_dir():
        raise FileNotFoundError(
            f"{VARIABLE_NORMAS_DIR}={declarado!r} no es una carpeta. "
            "Tiene que apuntar al clon del repositorio de normas (su "
            f"raiz o su subcarpeta «{SUBCARPETA_DEL_REPO_NORMAS}/»); "
            "ver «Donde estan los PDF de normas» en CLAUDE.md")
    subcarpeta = enlazado / SUBCARPETA_DEL_REPO_NORMAS
    # La raiz del clon no tiene PDF sueltos: los guarda en su subcarpeta.
    return (subcarpeta if subcarpeta.is_dir()
            and not any(enlazado.glob("*.pdf")) else enlazado,)


def ruta_pdf(fuente) -> Path:
    """
    La ruta en disco del PDF de una `Fuente` presente (o de un
    `PdfPresenteSinRegistrar`): el archivo con ese NOMBRE en la carpeta de
    `directorios_de_normas`.

    Si no esta NO lanza: devuelve la ruta donde se le esperaba --en la
    carpeta enlazada, o bajo `RUTA_SIN_ENLACE` si no hay enlace-- para que
    quien llama decida con `.exists()` si salta, falla o lo dice, y para que
    el mensaje nombre un sitio concreto. Una fuente AUSENTE no tiene PDF que
    buscar y eso si es un error de quien llama.
    """
    if not getattr(fuente, "archivo_pdf", None):
        raise ValueError(
            f"«{getattr(fuente, 'id', fuente)}» no declara `archivo_pdf`: "
            "una fuente ausente no tiene PDF contra el que verificar")
    nombre = Path(fuente.archivo_pdf).name
    carpetas = directorios_de_normas()
    for carpeta in carpetas:
        candidata = carpeta / nombre
        if candidata.exists():
            return candidata
    return (carpetas[0] if carpetas else RUTA_SIN_ENLACE) / nombre


def pdf_en_disco() -> Dict[str, Path]:
    """
    {nombre de archivo: ruta} de todo PDF que hay en `directorios_de_normas`,
    con la misma precedencia que `ruta_pdf` (gana la primera carpeta). Es lo
    que la guardia de PC-23 y `python3 -m src.normativa.extraccion` recorren.
    """
    encontrados: Dict[str, Path] = {}
    for carpeta in directorios_de_normas():
        for pdf in sorted(carpeta.glob("*.pdf")):
            encontrados.setdefault(pdf.name, pdf)
    return encontrados
