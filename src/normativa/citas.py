"""
Las citas del proyecto, una por objeto y con id estable (D1).

TODAS las que llevan `verificado` pasaron por el subagente
`verificador-normativo` -- en la sesion S12 las primeras, en la S13 el bloque
de clase de sitio -- contra el PDF cuyo sha1 declara la `Fuente`. Ninguna se acepto sin ese paso, y ninguna pagina se calculo a ojo
desde el desfase: donde el verificador no pudo leer, el campo queda en
`POR_TRANSCRIBIR` y la cita NO lleva firma.

POR QUE ESTO ES UN ARCHIVO Y NO SEIS CADENAS. El numeral `2.1.4.3.9` estaba
escrito en seis sitios del repositorio como seis cadenas independientes que
casualmente coincidian. Cuando se descubrio que ese numeral se titula
«Aparatos de Apoyo» no habia UNA cosa que corregir: habia seis, y nada que
garantizara que se corrigieran las seis. Aqui hay un objeto y seis referencias
a el.

LOS LITERALES VAN CON SUS TILDES Y CON SUS ERRATAS. Un `Verbatim`
de-acentuado no se puede encontrar en el PDF con el buscador de un lector, y
entonces no es verificable por nadie salvo por quien ya sabe donde esta. La
normalizacion sin diacriticos de `extraccion.pdf.normalizar` es para BUSCAR,
nunca para GUARDAR (T21). Es la unica zona del repositorio donde esta regla
manda sobre la costumbre de escribir sin tildes.
"""

from __future__ import annotations

from typing import Dict

from .esquema import (
    AfirmacionNegativa,
    Caracter,
    Cita,
    CondicionAplicacion,
    Efecto,
    Interpretacion,
    MetodoDeVerificacion,
    NoEvaluable,
    PorCriterio,
    PorDatoDeSitio,
    PorExpresion,
    Verbatim,
    Verificado,
)

FECHA_S12 = "2026-08-28"
POR_S12 = "fase1/S12 · verificador-normativo"
FECHA_S13 = "2026-08-29"
POR_S13 = "fase1/S13 · verificador-normativo"
FECHA_S20 = "2026-08-30"
POR_S20 = "fase1/S20 · verificador-normativo"

# La firma va por SESION, no por archivo: una cita dice contra que lectura se
# comprobo, y dos lecturas distintas del mismo PDF son dos hechos distintos.
FECHA_C2 = "2026-09-07"
POR_C2 = "familiaC/C2 · verificador-normativo"
FECHA_VC1 = "2026-09-08"
POR_VC1 = "familiaC/VC1 · verificador-normativo"
FECHA_I1 = "2026-09-12"
POR_I1 = "cierre/I1 · verificador-normativo"
FECHA_T2 = "2026-09-12"
POR_T2 = "trazabilidad/T2 · verificador-normativo"
FECHA_N1 = "2026-09-14"
POR_N1 = "normativa/N1 · verificador-normativo"

FECHA_EXT2 = "2026-09-20"
POR_EXT2 = "ext/EXT-2 · verificador-normativo"
FECHA_EXT3 = "2026-09-20"
POR_EXT3 = "ext/EXT-3 · verificador-normativo"
FECHA_EXT6 = "2026-09-20"
POR_EXT6 = "ext/EXT-6 · verificador-normativo"
FECHA_EXT7 = "2026-09-20"
POR_EXT7 = "ext/EXT-7 · verificador-normativo"
FECHA_EA = "2026-09-21"
POR_EA = "ext/E-A · verificador-normativo"
FECHA_CIERRE = "2026-09-22"
POR_CIERRE = "cierre/C11 · verificador-normativo"

S12 = (FECHA_S12, POR_S12)
S13 = (FECHA_S13, POR_S13)
S20 = (FECHA_S20, POR_S20)
C2 = (FECHA_C2, POR_C2)
VC1 = (FECHA_VC1, POR_VC1)
I1 = (FECHA_I1, POR_I1)
T2 = (FECHA_T2, POR_T2)
N1 = (FECHA_N1, POR_N1)
EXT2 = (FECHA_EXT2, POR_EXT2)
EXT3 = (FECHA_EXT3, POR_EXT3)
EXT6 = (FECHA_EXT6, POR_EXT6)
EXT7 = (FECHA_EXT7, POR_EXT7)
EA = (FECHA_EA, POR_EA)
CIERRE = (FECHA_CIERRE, POR_CIERRE)

_SHA = {
    "MC_HHD": "a31e853b8171b931863d7afa4379bbbc57cacb0d",
    "MP": "67a7a9f1c61cad8f9ca179cd4ca777f96b49dc44",
    "MS": "21d19a71090c1e586cd31596db8a4d007dc7b96f",
    "EG2013": "e35681d06b13226744324bc6b242b608ca9fa3ba",
    "E030": "fe0a58e4be4b8709324e65ed6ad0c25b8e0b6899",
    "E050": "5fac1ecd997a6d6e80bcbf0967f89f9ddcc8106c",
    "E060": "cffe0efffc767f5d06a33e1f4eed3a16a01bdd81",
    "HDS5_3ED": "7b985e047c615b765e7c41b6ff12df0505c02ce4",
    "HDS5_SI_1985": "59c6623c78793f7f947b7095027096b86f88ddf0",
    "AASHTO_LRFD_9": "71f4ced4c80f58db75a0bcdf4ac6b5d86dc0f858",
    "AASHTO_M170M": "dcc40c0e5e9c99ad9f18490fa8c5b2d9394faa51",
    "AASHTO_M36": "f85b5658385ae6779dde4e5fd340ac3122b62636",
    "ASTM_A760": "47d0d447143ca158615dff7dec79f2f7a8975732",
    "ASTM_A796": "df7858f04caf61bc1c3a4ea3d664e38cacddee25",
    "DG2018": "96ea04423a7e0e7fc44b5cd5d8824d6166a8e816",
}

_TODAS = []


def _firmado(fuente_id: str,
             metodo: MetodoDeVerificacion = MetodoDeVerificacion.TEXTO,
             sesion: tuple = S12) -> Verificado:
    fecha, por = sesion
    return Verificado(fecha=fecha, por=por,
                      sha1_pdf=_SHA[fuente_id], metodo=metodo)


def _cita(*, verificada: bool = True,
          metodo: MetodoDeVerificacion = MetodoDeVerificacion.TEXTO,
          sesion: tuple = S12,
          **kw) -> Cita:
    if verificada:
        kw["verificado"] = _firmado(kw["fuente_id"], metodo, sesion)
    c = Cita(**kw)
    _TODAS.append(c)
    return c


IMAGEN = MetodoDeVerificacion.IMAGEN
AMBOS = MetodoDeVerificacion.AMBOS


# ===========================================================================
# Manual de Hidrologia, Hidraulica y Drenaje  (desfase +3)
# ===========================================================================

MC_HHD_3_6 = _cita(
    id="MC_HHD.3.6",
    fuente_id="MC_HHD",
    numeral="3.6",
    titulo_numeral="Selección del Período de Retorno",
    pagina_impresa="25",
    pagina_pdf=28,
    pagina_pdf_titulo=26,
    texto_literal=Verbatim(
        texto=("De acuerdo a los valores presentados en la Tabla Nº 01 se "
               "recomienda utilizar como máximo, los siguientes valores de "
               "riesgo admisible de obras  de drenaje:"),
        pagina_pdf=28),
    caracter=Caracter.RECOMENDACION,
    metodo=AMBOS,
    nota=("El numeral abre en la pag. impresa 23 (PDF 26); la Tabla Nº 02 y "
          "este parrafo estan en la 25 (PDF 28)."),
)

MC_HHD_4_1_1_3_1 = _cita(
    id="MC_HHD.4.1.1.3.1",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.1",
    titulo_numeral="Aspectos generales",
    pagina_impresa="70",
    pagina_pdf=73,
    texto_literal=Verbatim(
        texto=("Se define como alcantarilla a la estructura cuya luz sea "
               "menor a 6.0 m y su función es evacuar el flujo superficial "
               "proveniente de cursos naturales o artificiales que "
               "interceptan la carretera."),
        pagina_pdf=73),
    caracter=Caracter.DEFINICION,
)

# NOR-HID-05: el repositorio citaba «pag. 88» y ahi no hay definicion de
# puente ninguna -- la pag. impresa 88 trae «a.1) Topografia - Batimetria del
# cauce...», que es parte del 4.1.1.5.2. El numeral ocupa las impresas 86-87 y
# la frase de los 6.0 m se imprime en la 87.
MC_HHD_4_1_1_5_1 = _cita(
    id="MC_HHD.4.1.1.5.1",
    fuente_id="MC_HHD",
    numeral="4.1.1.5.1",
    titulo_numeral="Aspectos generales",
    jerarquia_numeral=("4.1.1.5  PUENTES",),
    pagina_impresa="87",
    pagina_pdf=90,
    pagina_pdf_titulo=89,
    texto_literal=Verbatim(
        texto=("En el presente Manual se definirá como puente a la estructura "
               "cuya luz sea mayor o igual a 6.0 m, siguiendo lo establecido "
               "en las especificaciones AASHTO LRFD."),
        pagina_pdf=90),
    caracter=Caracter.DEFINICION,
    nota=("NOR-HID-05, cerrado: el numeral ARRANCA en la pag. impresa 86 "
          "(PDF 89) y la frase que sostiene el valor esta en la 87 (PDF 90). "
          "La cita anterior decia «pag. 88», donde el Manual imprime "
          "«a.1) Topografía – Batimetría del cauce y zonas adyacentes», del "
          "num. 4.1.1.5.2."),
)

MC_HHD_4_1_1_3_4a = _cita(
    id="MC_HHD.4.1.1.3.4a",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 a)",
    titulo_numeral="a)  Tipo y sección",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="72",
    pagina_pdf=75,
    pagina_pdf_titulo=74,
    texto_literal=Verbatim(
        texto=("En carreteras de alto volumen de tránsito y por necesidad de "
               "limpieza y mantenimiento de las alcantarillas, se adoptará "
               "una sección mínima circular de 0.90 m (36”) de diámetro o su "
               "equivalente de otra sección, salvo en cruces de canales de "
               "riego donde se adoptarán secciones de acuerdo a cada diseño "
               "particular."),
        pagina_pdf=75),
    caracter=Caracter.EXIGENCIA,
    condiciones=(
        CondicionAplicacion(
            id="COND-DMIN-ALTO-VOLUMEN",
            texto=Verbatim(texto="En carreteras de alto volumen de tránsito",
                           pagina_pdf=75),
            cita_id="MC_HHD.4.1.1.3.4a",
            resuelve=PorDatoDeSitio(clave="clase_de_via"),
            efecto_si_indeterminada=Efecto.ADVIERTE,
            justificacion_de_no_bloquear=(
                "el piso se aplica igual a las Familias A y B como ADOPCION "
                "conservadora declarada, y esa adopcion es anterior a este "
                "registro: bloquear aqui detendria un calculo que hoy corre y "
                "que ya declara la adopcion en la memoria. Lo que la condicion "
                "aporta es que la direccion NO es uniformemente conservadora "
                "-- mas diametro favorece a V1 y perjudica al piso de V2 --, "
                "y eso viaja al punto, no al preambulo")),
        CondicionAplicacion(
            id="COND-DMIN-CANAL-RIEGO",
            texto=Verbatim(
                texto=("salvo en cruces de canales de riego donde se "
                       "adoptarán secciones de acuerdo a cada diseño "
                       "particular"),
                pagina_pdf=75),
            cita_id="MC_HHD.4.1.1.3.4a",
            resuelve=PorExpresion(expresion="familia == 'C'",
                                  simbolos=("familia",)),
            efecto_si_indeterminada=Efecto.EXCLUYE,
            justificacion_de_no_bloquear=(
                "el numeral EXCEPTUA expresamente los cruces de canal de "
                "riego, que es lo que es la Familia C de este expediente: "
                "alli el piso no rige y la fila queda fuera, no pendiente")),
    ),
)

MC_HHD_4_1_1_3_5 = _cita(
    id="MC_HHD.4.1.1.3.5",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.5",
    titulo_numeral=("Recomendaciones y factores a tomar en cuenta para el "
                    "diseño de una alcantarilla"),
    pagina_impresa="73",
    pagina_pdf=76,
    texto_literal=Verbatim(
        texto=("A continuación se presentan algunas recomendaciones prácticas "
               "y factores que intervienen para el diseño adecuado de una "
               "alcantarilla."),
        pagina_pdf=76),
    caracter=Caracter.RECOMENDACION,
    nota=("Se declara aunque el proyecto no tome ningun valor de el: es el "
          "numeral con el que se confundio la Tabla Nº 09 antes de S5, y "
          "tenerlo escrito con su titulo es lo que impide repetir la "
          "confusion. NO contiene ninguna tabla de rugosidad."),
)

MC_HHD_4_1_1_3_6 = _cita(
    id="MC_HHD.4.1.1.3.6",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="74",
    pagina_pdf=77,
    texto_literal=Verbatim(
        texto="n : Coeficiente de Manning (Ver Tabla Nº 09)",
        pagina_pdf=77),
    caracter=Caracter.DEFINICION,
)

MC_HHD_T09 = _cita(
    id="MC_HHD.4.1.1.3.6#T09",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, Tabla Nº 09",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="75",
    pagina_pdf=78,
    pagina_pdf_titulo=77,
    texto_literal=Verbatim(
        texto="TABLA  Nº  09:  Valores del Coeficiente de Rugosidad de Manning (n)",
        pagina_pdf=78),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    condiciones=(
        # LA FILA `afinado` ESPERA A QUE SE DECLARE LA ANALOGIA DEL MARCO, y
        # es la hermana de `COND-EMBOCADURA-CAJON-KE` en la Tabla C.2. Su
        # `uso` era `NoUsada` con la razon «el catalogo de la Sec. 3.2 no
        # ofrece cajon todavia ... el criterio que declara esta analogia lo
        # abre C5»; C5 lo abrio, de modo que la fila dejo de estar sin usar y
        # paso a estar PENDIENTE de una declaracion. La evidencia sale de la
        # pagina de ESTA tabla y no de otra, que es la leccion que dejo la
        # condicion de la C.2.
        CondicionAplicacion(
            id="COND-N-MANNING-CAJON",
            texto=Verbatim(
                texto=("TABLA  Nº  09:  Valores del Coeficiente de Rugosidad "
                       "de Manning (n)"),
                pagina_pdf=78),
            cita_id="MC_HHD.4.1.1.3.6#T09",
            resuelve=PorCriterio(clave="n_manning_cajon"),
            efecto_si_indeterminada=Efecto.BLOQUEA),
    ),
    nota=("La tabla ocupa dos paginas impresas: los grupos A, B y C en la 75 "
          "(PDF 78) y el grupo D con la linea de Fuente en la 76 (PDF 79)."),
)

MC_HHD_T10 = _cita(
    id="MC_HHD.4.1.1.3.6#T10",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, Tabla Nº 10",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="76",
    pagina_pdf=79,
    pagina_pdf_titulo=77,
    texto_literal=Verbatim(
        texto=("TABLA  Nº  10:    Velocidades máximas  admisibles (m/s)  en "
               "conductos"),
        pagina_pdf=79),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("El titulo se imprime en DOS renglones y el segundo dice solo "
          "«revestidos»; el `texto_literal` es el primero, que es el que se "
          "puede buscar de corrido. El titulo completo esta en "
          "`TablaNormativa.titulo_literal`."),
)

MC_HHD_V_MIN = _cita(
    id="MC_HHD.4.1.1.3.6#VMIN",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, párrafo posterior a la Tabla Nº 10",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="77",
    pagina_pdf=80,
    pagina_pdf_titulo=77,
    texto_literal=Verbatim(
        texto=("reducción de su capacidad hidráulica, recomendándose que la "
               "velocidad mínima sea igual a 0.25 m/s."),
        pagina_pdf=80),
    caracter=Caracter.RECOMENDACION,
    metodo=AMBOS,
    nota=("El parrafo cruza el salto de pagina: arranca en la impresa 76 "
          "(«Se deberá verificar que la velocidad mínima del flujo dentro del "
          "conducto no produzca sedimentación que pueda incidir en una») y el "
          "numero se imprime en la 77. El `texto_literal` es la mitad que "
          "contiene el valor, porque es la que T5 tiene que poder encontrar "
          "en la pagina que la cita declara."),
)

# LA OTRA MITAD DEL MISMO PARRAFO, y no es un duplicado: cambia el CARACTER.
# La frase que arranca en la pag. impresa 76 dice «se deberá verificar», que es
# una EXIGENCIA -- verificar el minimo es obligatorio --, y la que termina en la
# 77 dice «recomendándose que la velocidad minima sea igual a 0.25 m/s», que es
# una RECOMENDACION sobre el VALOR. Son dos afirmaciones normativas distintas
# dentro de una sola oracion, y la memoria las tiene que poder imprimir por
# separado: sin esta mitad, «V2 es una recomendacion» se lee como que verificar
# el piso es opcional, que no es lo que el Manual dice. Vivia dentro de la
# `nota` de #VMIN -- o sea como prosa del proyecto, no como cita citable -- y
# por eso ninguna verificacion podia apoyarse en ella.
MC_HHD_4_1_1_3_6_VMIN_INICIO = _cita(
    id="MC_HHD.4.1.1.3.6#VMIN_INICIO",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, párrafo posterior a la Tabla Nº 10 (primera mitad)",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="76",
    pagina_pdf=79,
    pagina_pdf_titulo=77,
    texto_literal=Verbatim(
        texto=("Se deberá verificar que la velocidad mínima del flujo dentro "
               "del conducto no produzca sedimentación que pueda incidir en "
               "una"),
        pagina_pdf=79),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    derivado_de="MC_HHD.4.1.1.3.6#VMIN",
    nota=("La frase se corta donde la corta la PAGINA, no donde conviene: "
          "«...incidir en una» es literalmente el ultimo renglon de la pag. "
          "impresa 76, y completarla aqui con «reducción de su capacidad "
          "hidráulica» produciria un texto que no esta en esta pagina y que "
          "el buscador de un lector no encuentra. La continuacion es "
          "`MC_HHD.4.1.1.3.6#VMIN`, y las dos juntas son la oracion entera."),
)

MC_HHD_4_1_1_3_7a = _cita(
    id="MC_HHD.4.1.1.3.7a",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 a)",
    titulo_numeral="a)   Material sólido de arrastre",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="79",
    pagina_pdf=82,
    pagina_pdf_titulo=80,
    texto_literal=Verbatim(
        texto=("Se recomienda utilizar, en  zonas de selva alta, con las "
               "características físicas y geomorfológicos indicadas en el "
               "párrafo anterior,  como diámetro mínimo alcantarillas TMC "
               "Ф 48”"),
        pagina_pdf=82),
    caracter=Caracter.RECOMENDACION,
    nota=("Las CUATRO caracteristicas a las que «el párrafo anterior» remite "
          "estan en la pag. impresa 78 (PDF 81), no en la 79: la cita del "
          "repositorio decia solo «pag. 79» y con eso el condicionante "
          "quedaba fuera del rango citado. El rango correcto es 78-79. "
          "El valor 1.22 m NO esta en la fuente: el Manual escribe «Ф 48”» y "
          "la conversion (48 in = 1.2192 m) es del proyecto."),
    condiciones=(
        CondicionAplicacion(
            id="COND-SELVA-ALTA",
            texto=Verbatim(
                texto=("En zonas de selva alta en donde las características "
                       "físicas y geomorfológicos (típicas) sean:"),
                pagina_pdf=81),
            cita_id="MC_HHD.4.1.1.3.7a",
            resuelve=PorExpresion(expresion="region == 'selva_alta'",
                                  simbolos=("region",)),
            efecto_si_indeterminada=Efecto.EXCLUYE,
            justificacion_de_no_bloquear=(
                "el corredor esta en costa (La Union, Piura) y la "
                "recomendacion es expresamente para selva alta: la fila queda "
                "FUERA, que no es lo mismo que pendiente. Ademas es solo para "
                "TMC")),
    ),
)

MC_HHD_4_1_1_3_7b = _cita(
    id="MC_HHD.4.1.1.3.7b",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 b)",
    titulo_numeral="b)  Borde libre",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="79",
    pagina_pdf=82,
    texto_literal=Verbatim(
        texto=("Se recomienda que el diseño hidráulico considere como mínimo "
               "el 25 % de la altura, diámetro o flecha de la estructura."),
        pagina_pdf=82),
    caracter=Caracter.RECOMENDACION,
    nota=("El 0.75 que el codigo usa es la DERIVACION aritmetica de este "
          "25 % (1 - 0.25), no una cifra impresa; y la fuente no escribe "
          "«y/D» sino «la altura, diámetro o flecha de la estructura». La "
          "frase inmediatamente anterior SI es prohibitiva («las "
          "alcantarillas no deben ser diseñadas para trabajar a sección "
          "llena») pero prohibe la seccion llena, no fija el 25 %."),
)

# LA FRASE PROHIBITIVA DE ESE MISMO PARRAFO, como Cita y no como nota
# (EXT-3; EXT-M-01). Hasta EXT-3 vivia solo dentro de la `nota` de arriba,
# y por eso V1 no podia citarla: cuando el barril fluye lleno (TW >= D) el
# «no cumple» de V1 no es la recomendacion del 25 % aplicada como umbral
# duro --que es [A]-- sino esta exigencia, que es [N] de una pieza: la fuente
# escribe «no deben», no «se recomienda». Son dos oraciones del mismo
# apartado con dos fuerzas normativas, y la memoria tiene que poder decir
# cual de las dos sostiene cada veredicto (NOR-HID-10, NOR-MEM-01).
MC_HHD_4_1_1_3_7b_LLENA = _cita(
    id="MC_HHD.4.1.1.3.7b#LLENA",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 b)",
    titulo_numeral="b)  Borde libre",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="79",
    pagina_pdf=82,
    texto_literal=Verbatim(
        texto=("las alcantarillas no deben ser diseñadas para trabajar a "
               "sección llena, ya que esto incrementa su riesgo de "
               "obstrucción, afectando su capacidad hidráulica."),
        pagina_pdf=82),
    caracter=Caracter.EXIGENCIA,
    derivado_de="MC_HHD.4.1.1.3.7b",
    sesion=EXT3,
    nota=("Es la oracion inmediatamente ANTERIOR a la del 25 %, en el mismo "
          "parrafo. Prohibe la seccion llena y no fija cuanto borde libre "
          "hace falta: por eso sostiene el «no cumple» de V1 a barril LLENO "
          "(y/D = 1) y no el umbral 0.75, que sigue siendo la recomendacion "
          "endurecida por el proyecto."),
)

# ---------------------------------------------------------------------------
# EL SEGUNDO «Borde libre» DEL MISMO MANUAL, Y NO ES INTERCAMBIABLE CON EL DE
# ARRIBA. Va pegado a el a proposito: son dos apartados homonimos, los dos
# RECOMENDACION en su numero, y separarlos en el archivo es invitar a que
# alguien cite uno creyendo citar el otro.
#
#   4.1.1.3.7 b)   ALCANTARILLAS.  >= 25 % de la altura, diametro o flecha.
#                  Relativo, medido DENTRO del barril.        -> V1
#   4.1.1.4.1 e)   BADENES.        0.30 - 0.50 m.
#                  Absoluto, medido contra la SUPERFICIE DE RODADURA.  -> VC1
#
# EL OBJETO DEL SEGUNDO ES UN BADEN, NO UN CANAL, y esta dicho aqui porque es
# lo que decide la etiqueta del criterio que lo consume. El apartado cuelga de
# «4.1.1.4   BADENES»; su datum superior es la calzada, o sea el sitio donde
# desbordar es un riesgo para la propia plataforma. Que el proyecto lleve ese
# par de numeros a la coronacion de un canal --- donde desbordar inunda parcela
# de terceros --- es una ANALOGIA del proyectista, y por eso el valor vive en
# `criterios_adoptados['borde_libre_canal_m']` como [A] con su ventana, no como
# [N] ni como umbral cableado. El numeral 4.1.1.4.2, tres renglones mas abajo,
# dice «se idealizará el badén como un canal trapezoidal»: esa palabra «canal»
# es una idealizacion de CALCULO del baden y no el sujeto de este apartado.
# Tomarla por el sujeto es el error que esta nota existe para impedir.
MC_HHD_BADEN_BORDE_LIBRE = _cita(
    id="MC_HHD.4.1.1.4.1e",
    fuente_id="MC_HHD",
    numeral="4.1.1.4.1 e)",
    titulo_numeral="e)   Borde libre",
    jerarquia_numeral=("4.1.1.4   BADENES",
                       "4.1.1.4.1  Consideraciones para el diseño"),
    # EL ENCABEZADO DEL NUMERAL ESTA EN OTRA PAGINA QUE EL APARTADO: el
    # «4.1.1.4.1» abre en la impresa 84 (PDF 87) y el apartado e) esta en la
    # 85 (PDF 88). Citar el apartado como impresa 84 --- que es lo que da el
    # indice del Manual --- manda al revisor a la pagina equivocada.
    pagina_impresa="85",
    pagina_pdf=88,
    pagina_pdf_titulo=88,
    texto_literal=Verbatim(
        texto=("El diseño hidráulico del badén también debe contemplar "
               "mantener un borde libre mínimo entre el nivel del flujo "
               "máximo esperado y el nivel de la superficie de rodadura, a "
               "fin de evitar probables desbordes que afecten los lados "
               "adyacentes de la plataforma vial."),
        pagina_pdf=88),
    caracter=Caracter.EXIGENCIA,
    sesion=VC1,
    nota=("«debe contemplar mantener» es EXIGENCIA, y lo que exige es que "
          "HAYA borde libre: no fija cuanto. El cuanto esta en la oracion "
          "siguiente y es RECOMENDACION --- por eso son dos citas y no una, "
          "igual que el par VMIN_INICIO / VMIN de V2 ---. Fundir las dos en "
          "un solo objeto haria pasar por exigido el 0.30-0.50, que la fuente "
          "solo recomienda."),
)

MC_HHD_BADEN_BORDE_LIBRE_RANGO = _cita(
    id="MC_HHD.4.1.1.4.1e#RANGO",
    fuente_id="MC_HHD",
    numeral="4.1.1.4.1 e), segunda oracion",
    titulo_numeral="e)   Borde libre",
    jerarquia_numeral=("4.1.1.4   BADENES",
                       "4.1.1.4.1  Consideraciones para el diseño"),
    pagina_impresa="85",
    pagina_pdf=88,
    pagina_pdf_titulo=88,
    texto_literal=Verbatim(
        texto=("Generalmente, el borde libre se asume igual a la altura de "
               "agua entre el nivel de flujo máximo esperado y el nivel de la "
               "línea de energía, sin embargo, se recomienda adoptar valores "
               "entre 0.30 y 0.50m."),
        pagina_pdf=88),
    caracter=Caracter.RECOMENDACION,
    sesion=VC1,
    nota=("LA ORACION LLEVA DOS COSAS Y SOLO UNA ES EL RANGO. La primera "
          "mitad DESCRIBE una practica --- que el borde libre se asuma igual "
          "a la altura de velocidad --- y el «sin embargo» la desplaza en "
          "favor del par de valores. El rango va en TEXTO CORRIDO, sin tabla, "
          "y no es funcion de ninguna variable: ni del caudal, ni de la luz, "
          "ni de la velocidad. El Manual tampoco da regla para elegir dentro "
          "de el, y por eso la eleccion es del proyectista y no de la fuente. "
          "«0.50m» va sin espacio entre numero y unidad, tal como imprime."),
)

MC_HHD_LAUSHEY = _cita(
    id="MC_HHD.4.1.1.3.7c",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 c), ec. (49)",
    titulo_numeral="c)  Socavación local a la salida de la alcantarilla",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="80",
    pagina_pdf=83,
    pagina_pdf_titulo=82,
    texto_literal=Verbatim(
        texto=("A continuación, se presenta la fórmula de Laushey que permite "
               "calcular el diámetro medio de los elementos de protección a "
               "la salida de alcantarillas en función de la velocidad del "
               "flujo."),
        pagina_pdf=83),
    caracter=Caracter.APROXIMACION,
    metodo=IMAGEN,
    nota=("La ec. (49) es d50 = V² / (3.1 g). La extraccion de texto la "
          "devuelve desordenada («) 1.3 ( 2 50 g V d =») por el orden de "
          "trazado, de modo que la lectura fiable es la de la pagina "
          "renderizada: el metodo de esta cita es IMAGEN y decirlo es parte "
          "de la verificacion."),
)

# LA CITA QUE NO EXISTIA. `G_LAUSHEY = 9.8` se atribuia a este numeral con la
# formula «g tal como lo escribe la Sec. 4.1.1.3.7 c) junto a su formula de
# d50». El numeral define g SIN numero. Es el mismo genero de defecto que el
# proyecto purgo con el «19.62 = 2g»: el numero es defendible y la cita no lo
# era.
MC_HHD_LAUSHEY_G = _cita(
    id="MC_HHD.4.1.1.3.7c#G",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 c), lista de variables de la ec. (49)",
    titulo_numeral="c)  Socavación local a la salida de la alcantarilla",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="80",
    pagina_pdf=83,
    pagina_pdf_titulo=82,
    texto_literal=Verbatim(
        texto="g       : Aceleración de la gravedad (m/s2)",
        pagina_pdf=83),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    nota=("NOR-HID-01 / MAT-O7. ESTE NUMERAL NO ESCRIBE NINGUN VALOR DE g: "
          "define el simbolo y su unidad. El 9.8 que el proyecto usa SI esta "
          "en el Manual, en otros dos numerales (ver MC_HHD.3.12.5 y "
          "MC_HHD.4.1.1.5.4b24), y el 9.81 no aparece ni una vez en las 225 "
          "paginas. Se corrige la ATRIBUCION, no el numero."),
)

MC_HHD_3_12_5 = _cita(
    id="MC_HHD.3.12.5#G",
    fuente_id="MC_HHD",
    numeral="3.12.5",
    titulo_numeral="Otras Metodologías",
    pagina_impresa="63",
    pagina_pdf=66,
    pagina_pdf_titulo=65,
    texto_literal=Verbatim(
        texto=("la velocidad crítica (Vc) se define como la raíz cuadrada del "
               "calado crítico (yc) multiplicado por la aceleración de la "
               "gravedad (g= 9.8 m/s2)"),
        pagina_pdf=66),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    nota="Primera de las DOS paginas del Manual donde 9.8 figura como gravedad.",
)

MC_HHD_LAURSEN_G = _cita(
    id="MC_HHD.4.1.1.5.4b24#G",
    fuente_id="MC_HHD",
    numeral="4.1.1.5.4 b.2.4), ec. (63)",
    titulo_numeral="Método de Laursen",
    jerarquia_numeral=("b.2.) Socavación General",),
    pagina_impresa="111",
    pagina_pdf=114,
    pagina_pdf_titulo=112,
    texto_literal=Verbatim(
        texto="g       : Aceleración de la gravedad (9.8 m/s2)",
        pagina_pdf=114),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    nota=("Segunda y ultima pagina del Manual donde 9.8 figura como gravedad. "
          "Es socavacion general por contraccion en PUENTES, no la de salida "
          "de alcantarilla: sostiene el NUMERO, no el numeral de Laushey."),
)

MC_HHD_CUNETA = _cita(
    id="MC_HHD.4.1.2.1d",
    fuente_id="MC_HHD",
    numeral="4.1.2.1 d)",
    titulo_numeral="d) Desagüe de las cunetas",
    jerarquia_numeral=("4.1.2.1 Cunetas",),
    pagina_impresa="179",
    pagina_pdf=182,
    texto_literal=Verbatim(
        texto=("En región seca o poca lluviosa la longitud de las cunetas "
               "será de 250m como máximo, las longitudes de recorridos "
               "mayores deberán justificarse técnicamente; en región muy "
               "lluviosa se recomienda reducir esta longitud máxima a 200m."),
        pagina_pdf=182),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("NOR-HID-02, cerrado en sus DOS extremos. (1) LA PAGINA: el "
          "repositorio citaba la impresa 178, que trae la TABLA Nº 34 de "
          "dimensiones minimas del apartado c); el apartado d) esta en la "
          "179. (2) EL CARACTER: las dos cifras NO tienen la misma fuerza. "
          "El 250 es «será ... como máximo», exigencia con valvula de escape "
          "expresa («deberán justificarse técnicamente»); el 200 es «se "
          "recomienda reducir», recomendacion pura. Tratarlas como un dict de "
          "topes duros equivalentes borra la diferencia. Ademas la fuente "
          "nombra solo DOS regimenes en este apartado y deja sin longitud el "
          "regimen «lluvioso» intermedio de su propia Tabla Nº 34."),
)

# Afirmaciones negativas: lo que AUTORIZA saltar a un criterio [C].
SIN_HDPE_T09 = AfirmacionNegativa(
    que_no_dice="la Tabla Nº 09 no lista HDPE",
    ambito_barrido=("las 225 paginas del PDF: «HDPE» aparece 0 veces y "
                    "«polietileno» solo en la pag. impresa 71 (listado de "
                    "tipos de alcantarilla) y en la de subdrenes. Ninguna "
                    "fila de la Tabla Nº 09 lo nombra"),
    cita_id="MC_HHD.4.1.1.3.6#T09")

SIN_TMC_NI_HDPE_T10 = AfirmacionNegativa(
    que_no_dice="la Tabla Nº 10 no lista TMC ni HDPE",
    ambito_barrido=("las TRES filas de la tabla, leidas integras en la pag. "
                    "impresa 76 sobre la pagina renderizada. «TMC» aparece en "
                    "otras paginas del Manual (impresas 73 y 79 y en las "
                    "laminas), nunca en esta tabla; HDPE no aparece en el "
                    "Manual"),
    cita_id="MC_HHD.4.1.1.3.6#T10")

# EL VACIO QUE AUTORIZA A VC1 A ADOPTAR UN BORDE LIBRE EN VEZ DE CITARLO.
# Barrido completo, no impresion: «borde libre» aparece en CUATRO paginas del
# PDF y dos son el indice (PDF 6 y 7). Las otras dos son los dos apartados
# homonimos, y ninguno tiene por objeto un canal. La palabra «canal» aparece
# junto al borde libre una sola vez --- «se idealizará el badén como un canal
# trapezoidal», num. 4.1.1.4.2 --- y ahi el canal es la idealizacion de
# calculo del baden, no el objeto normado.
SIN_BORDE_LIBRE_DE_CANAL = AfirmacionNegativa(
    que_no_dice=("el Manual no fija borde libre para un CANAL: sus dos "
                 "apartados de «Borde libre» tienen por objeto la "
                 "alcantarilla (4.1.1.3.7 b), relativo a la altura del "
                 "barril) y el baden (4.1.1.4.1 e), absoluto contra la "
                 "superficie de rodadura)"),
    ambito_barrido=("las 225 paginas del PDF, buscando «borde libre» sin "
                    "distinguir mayusculas: aparece en las PDF 6 y 7 "
                    "(indice), 82 (num. 4.1.1.3.7 b), alcantarillas) y 88 "
                    "(num. 4.1.1.4.1 e), badenes). Ninguna otra. Tampoco "
                    "aparecen «faja marginal» --- que si nombra la Sec. 2.3 "
                    "de la hoja de ruta --- ni «terceros» en ninguna pagina"),
    cita_id="MC_HHD.4.1.1.4.1e#RANGO")

INTERPRETACION_T10 = Interpretacion(
    texto=("Que los dos números de una fila recorran la calidad del "
           "revestimiento — el superior para el acabado de mejor calidad y el "
           "inferior para el más pobre — es una lectura que este proyecto "
           "adopta para poder elegir un techo más conservador dentro de la "
           "fila ('v_max_concreto_eleccion'). El Manual NO la escribe."),
    en_contra=("la frase que introduce la tabla habla de «un rango, cuyos "
               "límites se describen a continuación»",
               "la fila de mampostería trae un solo valor, que no encaja con "
               "una lectura de acabados"),
    a_favor=("el título dice «Velocidades máximas admisibles (m/s)», que es "
             "lo único que decide que ninguno de los dos números sea un piso",
             "el rótulo de su única columna de valores es «VELOCIDAD (M/S)»"),
)


# ===========================================================================
# Manual de Puentes  (desfase +1)
# ===========================================================================

# LA CITA FALSA, conservada A PROPOSITO. No se borra: se declara. Un revisor
# que venga con la cita vieja en la mano tiene que poder encontrar aqui por
# que no vale, y el test T3 tiene contra que fallar si alguien la reactiva.
MP_2_1_4_3_9 = _cita(
    id="MP.2.1.4.3.9",
    fuente_id="MP",
    numeral="2.1.4.3.9",
    titulo_numeral="Aparatos de Apoyo",
    pagina_impresa="91",
    pagina_pdf=92,
    texto_literal=Verbatim(
        texto=("Los aparatos de apoyo proporcionan la conexión para controlar "
               "la interacción de las cargas y los movimientos entre la "
               "superestructura y la subestructura del puente."),
        pagina_pdf=92),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("NOR-PUE-01 / MAT-D5. ESTE NUMERAL NO SOSTIENE LA SOBRECARGA DE "
          "TRASDOS y esta aqui para que se vea que no la sostiene. No "
          "contiene la palabra «sobrecarga», ni «trasdós», ni «relleno "
          "equivalente», ni el valor 0.60: va de aparatos de apoyo "
          "(bearings), y su contexto lo confirma (2.1.4.3.7 Drenaje, "
          "2.1.4.3.8 Pavimentación, 2.1.4.3.9 Aparatos de Apoyo, 2.1.5 "
          "Señalización). El texto que si sostiene la sobrecarga esta en el "
          "num. 2.4.2.2 — ver MP.2.4.2.2#SOBRECARGA. El numeral falso estaba "
          "propagado a seis puntos del repositorio."),
)

MP_SOBRECARGA = _cita(
    id="MP.2.4.2.2#SOBRECARGA",
    fuente_id="MP",
    numeral="2.4.2.2",
    titulo_numeral="Cargas de Suelo: EH, ES, y DD",
    pagina_impresa="102",
    pagina_pdf=103,
    texto_literal=Verbatim(
        texto=("Cuando se prevea tráfico a una distancia horizontal, medida "
               "desde la parte superior de la estructura, menor o igual a la "
               "mitad de su altura, las presiones serán incrementadas "
               "añadiendo una sobrecarga vertical no menor que la equivalente "
               "a 0.60 m de altura de relleno."),
        pagina_pdf=103),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    corresponde_en=("AASHTO_LRFD_9.3.11.6.4",),
    nota=("EL 0.60 ES UN PISO, NO UN VALOR DE DISEÑO: la fuente dice «no "
          "menor que». Y esta expresado como ALTURA DE RELLENO EQUIVALENTE, "
          "no como presion: el paso a p = γ·0.60·Ka es derivacion del "
          "proyectista, correcta pero no escrita en este numeral. El titulo "
          "del numeral nombra EH, ES y DD y NO incluye LS."),
    condiciones=(
        CondicionAplicacion(
            id="COND-LS-DISTANCIA-H-MEDIO",
            texto=Verbatim(
                texto=("Cuando se prevea tráfico a una distancia horizontal, "
                       "medida desde la parte superior de la estructura, "
                       "menor o igual a la mitad de su altura"),
                pagina_pdf=103),
            cita_id="MP.2.4.2.2#SOBRECARGA",
            resuelve=PorExpresion(expresion="distancia_trafico <= H / 2",
                                  simbolos=("distancia_trafico", "H")),
            efecto_si_indeterminada=Efecto.ADVIERTE,
            justificacion_de_no_bloquear=(
                "un cabezal de alcantarilla bajo terraplen vial tiene el "
                "trafico ENCIMA, o sea a distancia horizontal cero desde la "
                "parte superior de la estructura: la condicion se cumple por "
                "geometria y no por medicion, y bloquear por ella detendria "
                "un calculo cuyo resultado no cambia. Lo que SI viaja al "
                "punto es la segunda mitad del numeral, la exencion por losa "
                "de aproximacion, que este expediente no invoca")),
        CondicionAplicacion(
            id="COND-LS-LOSA-APROXIMACION",
            texto=Verbatim(
                texto=("Cuando se diseñe una losa de aproximación soportada "
                       "en un extremo del puente, no será necesario "
                       "considerar dicho incremento de carga."),
                pagina_pdf=103),
            cita_id="MP.2.4.2.2#SOBRECARGA",
            resuelve=PorExpresion(expresion="losa_de_aproximacion",
                                  simbolos=("losa_de_aproximacion",)),
            efecto_si_indeterminada=Efecto.EXCLUYE,
            justificacion_de_no_bloquear=(
                "este expediente no proyecta losa de aproximacion en ningun "
                "cabezal: la exencion no se invoca, y por tanto la sobrecarga "
                "se aplica. Se declara para que un revisor vea que la salida "
                "existe y que no se tomo")),
    ),
)

SIN_TABLAS_HEQ_EN_MP = AfirmacionNegativa(
    que_no_dice=("el Manual de Puentes NO transcribe las Tablas 3.11.6.4-1 ni "
                 "3.11.6.4-2 de AASHTO, ni ninguna tabla de altura de suelo "
                 "equivalente h_eq"),
    ambito_barrido=(
        "las 673 paginas del PDF. Busquedas: «3.11.6.4» -> 0 paginas; "
        "«3.11.6» -> 8 paginas, todas falsos positivos del num. 2.4.3.11.6 "
        "(factores de modificacion de respuesta sismica); «suelo "
        "equivalente» -> 0; «altura de suelo equivalente» -> 0; «heq» -> 1, "
        "dentro de «chequear». Y ademas por estructura: el num. 2.4.4.1 "
        "«Empuje del Suelo: EH, ES, LS y DD» (pag. impresa 133) tiene "
        "subnumerales 2.4.4.1.1 a 2.4.4.1.5.4 y despues del empuje pasivo k_p "
        "salta directamente a 2.4.5. No hay 2.4.4.1.6 ni ningun subnumeral "
        "LS: la traduccion peruana de la Sec. 3.11 de AASHTO se CORTA en el "
        "empuje pasivo"),
    cita_id="MP.2.4.2.2#SOBRECARGA")



# ---------------------------------------------------------------------------
# R48-001 (cierre C11): que magnitud compara el umbral de 6.0 m. El Manual de
# Hidrologia escribe «luz» sin definirla; el glosario del Manual de Puentes
# USA «luz libre» en la entrada de las obras de arte menores (la define su
# Fig. 1.10-a: por vano, entre pilares); AASHTO, a la que el 4.1.1.5.1
# remite, escribe «opening»; y HDS-5 §1.2 escribe para que sirve el ancho
# TOTAL de un cruce multibarril. Ninguna de las cuatro es el ANCHO DEL CAUCE
# NATURAL, y ese era el hallazgo; en que magnitud discrepan lo dice
# DIS-LUZ-DENOMINACION.
# ---------------------------------------------------------------------------
MP_GLOSARIO_OBRAS_MENORES = _cita(
    id="MP.GLOSARIO#OBRAS_DE_ARTE_MENORES",
    fuente_id="MP",
    numeral="Glosario",
    titulo_numeral="GLOSARIO DE TERMINOS",
    pagina_impresa="45",
    pagina_pdf=46,
    pagina_pdf_titulo=45,
    texto_literal=Verbatim(
        texto=("OBRAS DE ARTE MENORES: Son aquellas obras cuya luz libre es "
               "menor que 6.00 m (20 ft)."),
        pagina_pdf=46),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=CIERRE,
    nota=("La magnitud que el glosario compara con los 6.00 m es la LUZ "
          "LIBRE de la obra, no el ancho del cauce que la obra salva. El "
          "glosario empieza en la pag. impresa 44 (PDF 45), donde imprime "
          "su titulo «GLOSARIO DE TERMINOS»; esta entrada esta en la 45 "
          "(PDF 46). Que es «luz libre» NO lo dice esta entrada: lo dibuja "
          "la Fig. 1.10-a (MP.1.10#FIG_1_10A_LUZ_LIBRE), por VANO."),
)

MP_FIG_1_10A_LUZ_LIBRE = _cita(
    id="MP.1.10#FIG_1_10A_LUZ_LIBRE",
    fuente_id="MP",
    numeral="Figura 1.10-a",
    titulo_numeral="Figura 1.10-a Puentes Tipo Viga",
    pagina_impresa="73",
    pagina_pdf=74,
    texto_literal=Verbatim(texto="C = LUZ LIBRE", pagina_pdf=74),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=CIERRE,
    nota=("Rotulo de la figura, leido sobre la pagina renderizada: la cota "
          "«C = LUZ LIBRE» va entre el PILAR N° 1 y el PILAR N° 2 --un solo "
          "vano--, mientras «L = LONGITUD» cubre todo entre estribos y "
          "«L1, L2 = LUZ DE TRAMO» van entre ejes de apoyo. Es la unica "
          "definicion de luz libre del Manual de Puentes, y es POR VANO: "
          "bajo esta lectura un marco de tres celdas de 2.5 m tiene luz "
          "libre 2.5 m. La parte EN CONTRA de DIS-LUZ-DENOMINACION."),
)

HDS5_NBIS_MULTIBARRIL = _cita(
    id="HDS5_3ED.1.2#NBIS",
    fuente_id="HDS5_3ED",
    numeral="1.2",
    titulo_numeral="COMPARISONS BETWEEN CULVERTS, BRIDGES, AND STORM DRAINS",
    pagina_impresa="1.3",
    pagina_pdf=41,
    texto_literal=Verbatim(
        texto=("It is important to recognize that culverts exceeding a 20 ft "
               "(6.1 m) span width (either as a single barrel or the total "
               "width of a multiple barrel crossing) are considered bridges "
               "in the National Bridge Inspection Standards (NBIS) and "
               "therefore subject to routine inspection according to NBIS "
               "requirements."),
        pagina_pdf=41),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=CIERRE,
    nota=("La unica fuente de normas/ que dice que ancho cuenta en un cruce "
          "de VARIOS barriles: el TOTAL («the total width of a multiple "
          "barrel crossing»), para la clasificacion como puente (NBIS). Es "
          "la parte que sostiene la lectura de `luz_m` como abertura total "
          "del cruce (DIS-LUZ-DENOMINACION). El parrafo siguiente, en la "
          "pag. 1.4, matiza que para el METODO HIDRAULICO la guia razonable "
          "es modelar como puente «a single culvert with a span of 20 ft "
          "(6.1 m) or more» (HDS5_3ED.1.2#MODELO)."),
)

HDS5_MODELO_PUENTE = _cita(
    id="HDS5_3ED.1.2#MODELO",
    fuente_id="HDS5_3ED",
    numeral="1.2",
    titulo_numeral="COMPARISONS BETWEEN CULVERTS, BRIDGES, AND STORM DRAINS",
    pagina_impresa="1.4",
    pagina_pdf=42,
    pagina_pdf_titulo=41,
    texto_literal=Verbatim(
        texto=("Based on NBIS regulations, as well as hydraulic issues, a "
               "reasonable guideline is to use bridge based modeling for a "
               "single culvert with a span of 20 ft (6.1 m) or more, given "
               "that such structures will typically operate with free "
               "surface flow."),
        pagina_pdf=42),
    caracter=Caracter.RECOMENDACION,
    metodo=AMBOS,
    sesion=CIERRE,
    nota=("«A reasonable guideline»: RECOMENDACION, no definicion. Distingue "
          "dos cosas que DIS-LUZ-DENOMINACION separa: la clasificacion "
          "administrativa del cruce (ancho total, NBIS, pag. 1.3) y el "
          "metodo hidraulico (luz de UN barril). Este proyecto aplica el "
          "umbral de 6.0 m del Manual de Hidrologia a la denominacion "
          "--alcantarilla o puente-- y por eso lee el ancho total."),
)

# ---------------------------------------------------------------------------
# AASHTO M 170M-04, Tabla 5 (Clase V): la UNICA de las cinco tablas de
# diseno que el ejemplar de normas/ conserva como escaneo real (pag. PDF 10,
# girada 90 grados; la continuacion en la PDF 11). Las Tablas 1 a 4 son
# recomposiciones OCR con digitos equivocados en la propia imagen (SIS-F-13,
# cierre C09). Leida por IMAGEN a 2.0x, rotada.
# ---------------------------------------------------------------------------
AASHTO_M170M_T5 = _cita(
    id="AASHTO_M170M.T5",
    fuente_id="AASHTO_M170M",
    numeral="Table 5",
    titulo_numeral="Table 5—Design Requirements for Class V Reinforced Concrete Pipe",
    pagina_impresa="M 170M-10",
    pagina_pdf=10,
    texto_literal=Verbatim(
        texto="Table 5—Design Requirements for Class V Reinforced Concrete Pipe",
        pagina_pdf=10),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=CIERRE,
    nota=("La pagina PDF 10 es un escaneo real, legible, impreso girado 90 "
          "grados (el rotulo de pie «M 170M-10» y «TS-4a» van verticales). "
          "La columna «Internal Designed Diameter, mm» --asi la imprime, con "
          "«Designed» y no «Designated»-- tiene 27 filas de 300 a 3600 mm, y "
          "es la serie que CP11 usa como dorado del concreto. Las columnas de "
          "espesor de pared B (300 a 1200 mm) y C (300 a 1800 mm) son "
          "legibles y se transcriben; las de refuerzo no, porque ningun "
          "modulo las consume (M8 no dimensiona el tubo de concreto)."),
)

AASHTO_DEF_BRIDGE = _cita(
    id="AASHTO_LRFD_9.1.2#BRIDGE",
    fuente_id="AASHTO_LRFD_9",
    numeral="1.2",
    titulo_numeral="DEFINITIONS",
    pagina_impresa="1-2",
    pagina_pdf=17,
    texto_literal=Verbatim(
        texto=("Bridge\u2014Any structure having an opening not less than "
               "20.0 ft that forms part of a highway or that is located over "
               "or under a highway."),
        pagina_pdf=17),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=CIERRE,
    nota=("Es la definicion a la que remite el num. 4.1.1.5.1 del Manual de "
          "Hidrologia («siguiendo lo establecido en las especificaciones "
          "AASHTO LRFD»). La magnitud es «an opening»: la ABERTURA de la "
          "estructura. 20.0 ft son 6.096 m y el Manual escribe 6.0 m sin "
          "decir como pasa de una cifra a la otra: la diferencia esta "
          "declarada en DIS-LUZ-DENOMINACION y el codigo compara los 6.0 m "
          "del Manual ([N], el mas exigente de los dos)."),
)

# ===========================================================================
# AASHTO LRFD 9a ed.  (por capitulo: base cap. 3 = 54)
# ===========================================================================

AASHTO_LS = _cita(
    id="AASHTO_LRFD_9.3.11.6.4",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.11.6.4",
    titulo_numeral="Live Load Surcharge (LS)",
    pagina_impresa="3-151",
    pagina_pdf=205,
    texto_literal=Verbatim(
        texto=("Equivalent heights of soil, heq, for highway loadings on "
               "abutments and retaining walls may be taken from Tables "
               "3.11.6.4-1 and 3.11.6.4-2. Linear interpolation shall be used "
               "for intermediate wall heights."),
        pagina_pdf=205),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    corresponde_en=("MP.2.4.2.2#SOBRECARGA",),
    nota=("El articulo entero, sus dos tablas y su comentario C3.11.6.4 caben "
          "en la pag. impresa 3-151; no continua en la 3-152, donde empieza "
          "el 3.11.6.5. La frase de la interpolacion es EXIGENCIA («shall»); "
          "la de tomar valores de las tablas es PERMISO («may be taken»)."),
)

AASHTO_LS_ALTURA_MURO = _cita(
    id="AASHTO_LRFD_9.3.11.6.4#ALTURA",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.11.6.4",
    titulo_numeral="Live Load Surcharge (LS)",
    pagina_impresa="3-151",
    pagina_pdf=205,
    texto_literal=Verbatim(
        texto=("The wall height shall be taken as the distance between the "
               "surface of the backfill and the bottom of the footing along "
               "the pressure surface being considered."),
        pagina_pdf=205),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("La altura que entra en las tablas NO es la altura visible del "
          "muro: incluye la zapata. Con `GeometriaCabezal` eso es "
          "H + espesor_zapata. Medirla sin la zapata SUBESTIMA la altura y, "
          "como h_eq decrece con ella, SOBRESTIMA h_eq -- conservador, pero "
          "es la lectura equivocada de la tabla."),
)

AASHTO_LS_APLICABILIDAD = _cita(
    id="AASHTO_LRFD_9.3.11.6.4#APLICA",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.11.6.4",
    titulo_numeral="Live Load Surcharge (LS)",
    pagina_impresa="3-151",
    pagina_pdf=205,
    texto_literal=Verbatim(
        texto=("A live load surcharge shall be applied where vehicular load "
               "is expected to act on the surface of the backfill within a "
               "distance equal to one-half the wall height behind the back "
               "face of the wall."),
        pagina_pdf=205),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    corresponde_en=("MP.2.4.2.2#SOBRECARGA",),
)

AASHTO_LS_COMENTARIO = _cita(
    id="AASHTO_LRFD_9.C3.11.6.4",
    fuente_id="AASHTO_LRFD_9",
    numeral="C3.11.6.4",
    titulo_numeral="Live Load Surcharge (LS)",
    pagina_impresa="3-151",
    pagina_pdf=205,
    texto_literal=Verbatim(
        texto=("Subsequent analyses, i.e., Kim and Barker (1998), show the "
               "importance of the direction of traffic, i.e., parallel for a "
               "wall and perpendicular for an abutment on the magnitude of "
               "heq. The magnitude of heq is greater for an abutment than for "
               "a wall due to the proximity and closer spacing of wheel loads "
               "to the back of an abutment compared to a wall."),
        pagina_pdf=205),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    nota=("HALLAZGO DE S12, y es el que obliga a matizar el conflicto #4: "
          "NO EXISTE en el articulado ninguna frase que reparta las dos "
          "tablas. El cuerpo normativo las cita JUNTAS Y SIN CONDICIONANTE "
          "(«may be taken from Tables 3.11.6.4-1 and 3.11.6.4-2»). Lo que las "
          "reparte son (a) los TITULOS de las tablas y (b) este comentario, "
          "que no es articulado. Y no ofrecen un eje libre «orientacion»: "
          "ofrecen dos BINOMIOS ACOPLADOS -- estribo+perpendicular y muro de "
          "contencion+paralelo --. No hay tabla para «muro perpendicular» ni "
          "para «estribo paralelo»."),
)

AASHTO_T3_11_6_4_1 = _cita(
    id="AASHTO_LRFD_9.T3.11.6.4-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 3.11.6.4-1",
    titulo_numeral=("Equivalent Height of Soil for Vehicular Loading on "
                    "Abutments Perpendicular to Traffic"),
    pagina_impresa="3-151",
    pagina_pdf=205,
    texto_literal=Verbatim(
        texto=("Table 3.11.6.4-1—Equivalent Height of Soil for Vehicular "
               "Loading on Abutments Perpendicular to Traffic"),
        pagina_pdf=205),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("Su variable de entrada se llama literalmente «Abutment Height "
          "(ft)»: es una tabla de ESTRIBOS. Aplicarla a un cabezal de "
          "alcantarilla es analogia declarada, no lectura directa."),
)

AASHTO_T3_11_6_4_2 = _cita(
    id="AASHTO_LRFD_9.T3.11.6.4-2",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 3.11.6.4-2",
    titulo_numeral=("Equivalent Height of Soil for Vehicular Loading on "
                    "Retaining Walls Parallel to Traffic"),
    pagina_impresa="3-151",
    pagina_pdf=205,
    texto_literal=Verbatim(
        texto=("Table 3.11.6.4-2—Equivalent Height of Soil for Vehicular "
               "Loading on Retaining Walls Parallel to Traffic"),
        pagina_pdf=205),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("Encabezado de DOS niveles: sobre las columnas 2 y 3 va «heq (ft) "
          "Distance from wall backface to edge of traffic», y bajo el «0.0 "
          "ft» y «1.0 ft or Further». El umbral es UNA PULGADA-PIE EXACTA: "
          "1.0 ft = 0.3048 m, no 0.30 m. Redondearlo a 0.30 relaja el "
          "criterio y va del lado inseguro."),
)


# ===========================================================================
# Manual de Suelos  (desfase +1)
# ===========================================================================

MS_4_2 = _cita(
    id="MS.4.2",
    fuente_id="MS",
    numeral="4.2",
    titulo_numeral="Caracterización de la sub rasante",
    pagina_impresa="28",
    pagina_pdf=29,
    texto_literal=Verbatim(
        texto=("Con el objeto de determinar las características "
               "físico-mecánicas de los materiales de la sub rasante se  "
               "llevarán  a  cabo  investigaciones  mediante la  ejecución  "
               "de  pozos exploratorios o  calicatas de 1.5 m de profundidad "
               "mínima; el número mínimo de calicatas por kilómetro, estará "
               "de acuerdo al cuadro 4.1."),
        pagina_pdf=29),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
)

MS_C41 = _cita(
    id="MS.4.2#C41",
    fuente_id="MS",
    numeral="4.2, Cuadro 4.1",
    titulo_numeral="Caracterización de la sub rasante",
    pagina_impresa="28",
    pagina_pdf=29,
    texto_literal=Verbatim(
        texto="Cuadro 4.1 Número de Calicatas para Exploración de Suelos",
        pagina_pdf=29),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("El Cuadro entero cabe en una sola pagina impresa; no se parte. "
          "NOR-SUE-01: SI condiciona el numero por CARRILES POR SENTIDO, y la "
          "cadena «4 (o 6)» que el repositorio le atribuia no existe en "
          "ninguna celda."),
)

MS_PERFIL = _cita(
    id="MS.4.2#PERFIL",
    fuente_id="MS",
    numeral="4.2, párrafo posterior al Cuadro 4.1",
    titulo_numeral="Caracterización de la sub rasante",
    pagina_impresa="29",
    pagina_pdf=30,
    pagina_pdf_titulo=29,
    texto_literal=Verbatim(
        texto=("En caso de estudios a nivel de perfil se utilizará "
               "información secundaria existente en el tramo del proyecto, de "
               "no existir información secundaria se efectuará el número de "
               "calicatas del cuadro 4.1 espaciadas cada 4.0 km en vez de "
               "cada km."),
        pagina_pdf=30),
    caracter=Caracter.EXIGENCIA,
    nota=("NOR-SUE-02, cerrado en sus dos extremos. (1) NO ESTA EN EL CUADRO "
          "4.1: el Cuadro no contiene ninguna celda con 4.0 km ni con 2.0 km, "
          "solo «x km». El 4.0 vive en este parrafo de la pag. impresa 29. "
          "(2) ES CONDICIONAL DOS VECES: solo para estudios a nivel de "
          "perfil, y solo «de no existir información secundaria» -- el orden "
          "de prelacion impreso es usar primero la informacion secundaria. El "
          "mismo parrafo fija ademas 2.0 km para factibilidad y "
          "prefactibilidad, que el repositorio no recoge."),
    condiciones=(
        CondicionAplicacion(
            id="COND-PERFIL-SIN-INFO-SECUNDARIA",
            texto=Verbatim(
                texto=("se utilizará información secundaria existente en el "
                       "tramo del proyecto, de no existir información "
                       "secundaria"),
                pagina_pdf=30),
            cita_id="MS.4.2#PERFIL",
            resuelve=PorDatoDeSitio(clave="existe_informacion_secundaria_tramo"),
        ),
    ),
)

MS_3_2_1 = _cita(
    id="MS.3.2.1",
    fuente_id="MS",
    numeral="3.2.1",
    titulo_numeral="Terraplén",
    pagina_impresa="24",
    pagina_pdf=25,
    texto_literal=Verbatim(
        texto=("La base y cuerpo del terraplén o relleno será conformado en "
               "capas de hasta 0.30m y compactadas al 90% de la máxima "
               "densidad seca del ensayo proctor modificado. La corona es la "
               "parte superior del terraplén tendrá un  espesor mínimo de "
               "0.30m y será conformada en capas de 0.15m, compactadas al 95% "
               "de la máxima densidad seca del ensayo proctor modificado."),
        pagina_pdf=25),
    caracter=Caracter.EXIGENCIA,
    nota=("NOR-SUE-03: ES EL UNICO DE LOS CUATRO NUMERALES QUE EL REPOSITORIO "
          "CITABA QUE SOSTIENE LOS DOS VALORES. El 3.2.2 «Corte» y el 3.3 "
          "«Sub rasante del camino» traen un 95 % de OTRO elemento (fondo de "
          "excavacion escarificado, y ultimos 0.30 m bajo la subrasante) y "
          "ningun 90 %; el 9.1(1) no contiene ningun porcentaje de "
          "compactacion."),
)

MS_3_2_2 = _cita(
    id="MS.3.2.2",
    fuente_id="MS",
    numeral="3.2.2",
    titulo_numeral="Corte",
    pagina_impresa="24",
    pagina_pdf=25,
    texto_literal=Verbatim(
        texto=("El fondo de las zonas excavadas se preparará mediante "
               "escarificación  en una profundidad de 0.15m, conformando y "
               "nivelando de acuerdo con las pendientes transversales "
               "especificadas en el diseño geométrico vial; y se compactará "
               "al 95% de la máxima densidad seca del ensayo proctor "
               "modificado."),
        pagina_pdf=25),
    caracter=Caracter.EXIGENCIA,
    nota=("Su 95 % es el del FONDO DE EXCAVACION EN CORTE, escarificado "
          "0.15 m: no es el de la corona del terraplen. No contiene el 90 %."),
)

MS_3_3 = _cita(
    id="MS.3.3",
    fuente_id="MS",
    numeral="3.3",
    titulo_numeral="Sub rasante del camino",
    pagina_impresa="24",
    pagina_pdf=25,
    texto_literal=Verbatim(
        texto=("Los suelos por debajo del nivel superior de la sub rasante, "
               "en una profundidad no menor de  0.60 m, deberán ser suelos "
               "adecuados y estables con CBR ≥ 6%."),
        pagina_pdf=25),
    caracter=Caracter.EXIGENCIA,
    nota=("Sostiene CBR_MIN_SUBRASANTE = 6.0 %, no la compactacion del "
          "cuerpo. Y el 6 % TAMPOCO es umbral binario: el mismo numeral da "
          "salida por estabilizacion, reemplazo, elevacion de rasante o "
          "cambio de trazo."),
)

MS_9_1_1 = _cita(
    id="MS.9.1.1",
    fuente_id="MS",
    numeral="9.1, apartado 1)",
    titulo_numeral=("Criterios geotécnicos para establecer la estabilización "
                    "de suelos"),
    pagina_impresa="89",
    pagina_pdf=90,
    texto_literal=Verbatim(
        texto=("Se considerarán como materiales aptos para las capas de la "
               "sub rasante suelos con CBR ≥  6%."),
        pagina_pdf=90),
    caracter=Caracter.EXIGENCIA,
    nota=("NOR-SUE-03: ES EL NUMERAL QUE NO CONTIENE NINGUNO DE LOS DOS "
          "VALORES DE COMPACTACION. No imprime ni 0.95 ni 0.90 ni ningun "
          "porcentaje: va de CBR ≥ 6 % y de alternativas de estabilizacion. "
          "Sostiene CBR_MIN_SUBRASANTE, no COMPACTACION_*."),
)

MS_4_5_4 = _cita(
    id="MS.4.5.4",
    fuente_id="MS",
    numeral="4.5.4",
    titulo_numeral="Sub rasante",
    pagina_impresa="42",
    pagina_pdf=43,
    texto_literal=Verbatim(
        texto=("El nivel superior de la sub rasante debe quedar encima del "
               "nivel de la napa freática como mínimo a 0.60 m cuando se "
               "trate de una sub rasante excelente - muy buena (CBR ≥ 20 %); "
               "a 0.80 m cuando se trate de una sub rasante buena - regular "
               "(6% ≤ CBR < 20%); a 1.00 m cuando se trate de una sub rasante "
               "Insuficiente (3% ≤ CBR < 6%); y, a 1.20 m cuando se trate de "
               "una sub rasante inadecuada (CBR < 3%). En caso necesario, se "
               "colocarán subdrenes o capas anticontaminantes y/o drenantes o "
               "se elevará la rasante hasta el nivel necesario."),
        pagina_pdf=43),
    caracter=Caracter.EXIGENCIA,
    nota=("NOR-SUE-05, cerrado en sus dos extremos. (1) NO ES UNA TABLA: es "
          "PROSA CORRIDA, y el numeral arranca en la pag. impresa 41 mientras "
          "este parrafo esta en la 42. (2) «RESGUARDO» NO ES PALABRA DEL "
          "MANUAL: aparece UNA sola vez en las 281 paginas, en la impresa 56, "
          "y en el sentido de «al resguardo de la luz» para conservar "
          "muestras. El Manual lo llama «quedar encima del nivel de la napa "
          "freática como mínimo a X m». (3) LA FUENTE OFRECE REMEDIO: la "
          "ultima oracion del mismo parrafo autoriza subdrenes, capas "
          "anticontaminantes o drenantes, o elevar la rasante. Tratarlo como "
          "umbral duro de rechazo endurece a la fuente."),
)

MS_9_1_3 = _cita(
    id="MS.9.1.3",
    fuente_id="MS",
    numeral="9.1, apartado 3)",
    titulo_numeral=("Criterios geotécnicos para establecer la estabilización "
                    "de suelos"),
    pagina_impresa="89",
    pagina_pdf=90,
    texto_literal=Verbatim(
        texto=("La superficie de la sub rasante debe quedar encima del nivel "
               "de la napa freática como mínimo a 0.60 m cuando se trate de "
               "una sub rasante extraordinaria y muy buena; a 0.80 m cuando "
               "se trate de una sub rasante"),
        pagina_pdf=90),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("MS.4.5.4",),
    nota=("El apartado 3) CRUZA EL SALTO DE PAGINA: arranca en la impresa 89 "
          "(PDF 90) y termina en la 90 (PDF 91), donde se imprimen el 1.00 m, "
          "el 1.20 m y la frase de los remedios («En caso necesario, se "
          "colocarán subdrenes o capas anticontaminantes y/o drenantes o se "
          "elevará la rasante hasta el nivel necesario»). El `texto_literal` "
          "es la mitad que cabe en la pagina que la cita declara, porque es "
          "la que T2 tiene que poder encontrar ahi. "
          "Segunda ocurrencia de la MISMA regla, con las mismas cuatro "
          "cifras, y con tres diferencias literales: dice «La superficie» "
          "donde el 4.5.4 dice «El nivel superior», dice «extraordinaria y "
          "muy buena» donde aquel dice «excelente - muy buena», y NO enuncia "
          "los intervalos numericos de CBR. Los intervalos solo estan en el "
          "4.5.4, y por eso la cita del proyecto al 4.5.4 es la correcta."),
)

MS_C411 = _cita(
    id="MS.4.4#C411",
    fuente_id="MS",
    numeral="Cuadro 4.11",
    titulo_numeral="Cuadro 4.11 Categorías de Sub rasante",
    pagina_impresa="37",
    pagina_pdf=38,
    texto_literal=Verbatim(
        texto=("Cuadro 4.11 Categorías de Sub rasante Categorías de Sub "
               "rasante CBR S0 : Sub rasante Inadecuada CBR < 3%"),
        pagina_pdf=38),
    caracter=Caracter.DEFINICION,
    nota=("LA PAGINA LA CORRIGIO LA GUARDIA, no el verificador: el informe de "
          "verificacion daba la impresa 38 (PDF 39) y el test T2 la rechazo "
          "porque el texto no estaba ahi. El Cuadro 4.11 se imprime en la "
          "pag. impresa 37 (PDF 38); la 38 trae la Figura 4.1 de "
          "correlaciones. Es exactamente para lo que existe T2. "
          "ERRATA DE LA PROPIA FUENTE, hallada al verificar: el num. 4.5.4 "
          "remite «al cuadro 4.10» para la categoria de sub rasante, pero el "
          "Cuadro 4.10 (pag. impresa 36) es «Clasificación de los suelos "
          "basada en AASHTO M 145 y/o ASTM D 3282». La tabla de categorias es "
          "esta, el Cuadro 4.11. Sin efecto sobre los cuatro escalones del "
          "resguardo, que el propio 4.5.4 enuncia con sus intervalos."),
)


# ===========================================================================
# E.060 Concreto Armado  (desfase 0)
# ===========================================================================

E060_T42 = _cita(
    id="E060.T4.2",
    fuente_id="E060",
    numeral="Tabla 4.2",
    titulo_numeral="REQUISITOS PARA CONDICIONES ESPECIALES DE EXPOSICIÓN",
    pagina_impresa="37",
    pagina_pdf=37,
    texto_literal=Verbatim(
        texto=("Los concretos expuestos a las condiciones especiales de "
               "exposición señaladas en la Tabla 4.2 deben cumplir con las "
               "relaciones máximas agua-material cementante y con la "
               "resistencia mínima f’c señaladas en ésta."),
        pagina_pdf=37),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("La invocan DOS numerales por vias distintas, y los dos hacen falta: "
          "el 4.2.2 (pag. impresa 37) por condiciones especiales de "
          "exposicion en general, y el 4.4.2 (pag. impresa 39) "
          "especificamente para los cloruros, que es el disparador de este "
          "expediente."),
)

E060_4_4_2 = _cita(
    id="E060.4.4.2",
    fuente_id="E060",
    numeral="4.4.2",
    titulo_numeral="PROTECCIÓN DEL REFUERZO CONTRA LA CORROSIÓN",
    pagina_impresa="39",
    pagina_pdf=39,
    # El encabezado del bloque 4.4 se imprime al pie de la pag. anterior.
    pagina_pdf_titulo=38,
    texto_literal=Verbatim(
        texto=("Cuando el concreto con refuerzo vaya a estar expuesto a "
               "cloruros de químicos descongelantes, sal, agua salobre, agua "
               "de mar o salpicaduras de las mismas, deben cumplirse los "
               "requisitos de la Tabla 4.2 para la máxima relación "
               "agua-material cementante y valor mínimo de f’c, y los "
               "requisitos de recubrimiento mínimo del concreto de 7.7."),
        pagina_pdf=39),
    caracter=Caracter.EXIGENCIA,
    nota=("ES EL ESLABON QUE ATA EL CLUSTER DE DURABILIDAD DE PUNTA A PUNTA: "
          "manda aplicar la Tabla 4.2 a los cloruros externos Y remite al "
          "recubrimiento del 7.7. Sin el, la cadena a/c -> recubrimiento "
          "queda sin numeral que la sostenga. El disparador es acotado -- "
          "cloruros «de quimicos descongelantes, sal, agua salobre, agua de "
          "mar o salpicaduras» --, no cloruros en el suelo en general."),
)

E060_T44 = _cita(
    id="E060.T4.4",
    fuente_id="E060",
    numeral="Tabla 4.4",
    titulo_numeral="REQUISITOS PARA CONCRETO EXPUESTO A SOLUCIONES DE SULFATOS",
    pagina_impresa="38",
    pagina_pdf=38,
    texto_literal=Verbatim(
        texto=("Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se "
               "debe utilizar la menor relación máxima agua-material "
               "cementante aplicable y el mayor f’c mínimo."),
        pagina_pdf=38),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    condiciones=(
        # La exposicion quimica del sitio es un [S] pendiente de ENSAYO: sin
        # el EMS del expediente no se sabe en que fila cae el suelo, y por
        # tanto ni la a/c maxima ni -- via el modificador de AASHTO -- el
        # recubrimiento del refuerzo. Bloquea, y debe.
        CondicionAplicacion(
            id="COND-EXPOSICION-QUIMICA-EMS",
            texto=Verbatim(
                texto=("Sulfato soluble en agua (SO4) presente en el suelo, "
                       "porcentaje en peso"),
                pagina_pdf=38),
            cita_id="E060.T4.4",
            resuelve=PorCriterio(clave="exposicion_quimica_ems")),
    ),
    nota=("La invoca el num. 4.3.1, bajo «4.3 EXPOSICION A SULFATOS». El "
          "`texto_literal` es la NOTA COMUN a las dos tablas, y esta a "
          "proposito: es la regla que decide que se especifica cuando el "
          "sitio tiene sulfatos Y cloruros a la vez -- el caso de un corredor "
          "costero con freatico somero --, y esta impresa al pie de LAS DOS "
          "(pags. 37 y 38), colgando en cada una de las columnas de a/c y de "
          "f'c. Transcribir una tabla sin la otra deja el requisito a medias."),
)

E060_7_7_1 = _cita(
    id="E060.7.7.1",
    fuente_id="E060",
    numeral="7.7.1",
    titulo_numeral="Concreto construido en sitio (no preesforzado)",
    pagina_impresa="54",
    pagina_pdf=54,
    texto_literal=Verbatim(
        texto=("Debe proporcionarse el siguiente recubrimiento mínimo de "
               "concreto al refuerzo, excepto cuando se requieran "
               "recubrimientos mayores según 7.7.5.1 ó se requiera protección "
               "especial contra el fuego"),
        pagina_pdf=54),
    caracter=Caracter.EXIGENCIA,
    jerarquia_numeral=("7.7 RECUBRIMIENTO DE CONCRETO PARA EL REFUERZO",),
    nota=("EL PROPIO ENCABEZADO REMITE AL 7.7.5.1: el aumento por ambiente "
          "corrosivo no es una nota externa que alguien decidio traer, es la "
          "excepcion que el articulo de los 70/50/40 mm declara."),
)

E060_7_7_5_1 = _cita(
    id="E060.7.7.5.1",
    fuente_id="E060",
    numeral="7.7.5.1",
    titulo_numeral="Ambientes corrosivos",
    pagina_impresa="55",
    pagina_pdf=55,
    texto_literal=Verbatim(
        texto=("En ambientes corrosivos u otras condiciones severas de "
               "exposición, debe aumentarse adecuadamente el espesor del "
               "recubrimiento de concreto y debe tomarse en consideración su "
               "densidad y porosidad o debe disponerse de otro tipo de "
               "protección."),
        pagina_pdf=55),
    caracter=Caracter.EXIGENCIA,
    nota=("EXIGENCIA DE RESULTADO SIN CUANTIFICAR: manda aumentar y no dice "
          "cuanto. El cuanto es [A] del proyectista, y la ALTERNATIVA del "
          "final -- «o debe disponerse de otro tipo de proteccion» -- es un "
          "camino de cumplimiento distinto que este expediente no contempla y "
          "que hay que dejar visible."),
)

E060_14_3_1 = _cita(
    id="E060.14.3.1",
    fuente_id="E060",
    numeral="14.3.1",
    titulo_numeral="REFUERZO MÍNIMO",
    pagina_impresa="133",
    pagina_pdf=133,
    texto_literal=Verbatim(
        texto=("El refuerzo mínimo vertical y horizontal debe cumplir con las "
               "disposiciones de 14.3, a menos que se requiera una cantidad "
               "mayor por cortante de acuerdo con 11.10."),
        pagina_pdf=133),
    caracter=Caracter.EXIGENCIA,
    nota=("EL ESCALONAMIENTO 0,002 -> 0,0025 LO ANUNCIA ESTE MISMO NUMERAL, "
          "no solo el 11.10.10.2: su primera oracion remite a 11.10 «a menos "
          "que se requiera una cantidad mayor por cortante». La norma imprime "
          "«0,002» y «0,0015»."),
)

E060_14_3_2 = _cita(
    id="E060.14.3.2",
    fuente_id="E060",
    numeral="14.3.2",
    titulo_numeral="REFUERZO MÍNIMO",
    pagina_impresa="133",
    pagina_pdf=133,
    texto_literal=Verbatim(
        texto=("Los muros con un espesor mayor que 200 mm, excepto los muros "
               "de sótanos, deben tener el refuerzo en cada dirección "
               "colocado en dos capas paralelas a las caras del muro."),
        pagina_pdf=133),
    caracter=Caracter.EXIGENCIA,
)

E060_14_3_3 = _cita(
    id="E060.14.3.3",
    fuente_id="E060",
    numeral="14.3.3",
    titulo_numeral="REFUERZO MÍNIMO",
    pagina_impresa="133",
    pagina_pdf=133,
    texto_literal=Verbatim(
        texto=("El refuerzo vertical y el horizontal no debe estar espaciados "
               "a más de tres veces el espesor del muro, ni de 400 mm."),
        pagina_pdf=133),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("E060.14.8.4",),
    nota=("El repositorio no le asignaba pagina; es la impresa 133. Y hay un "
          "SEGUNDO numeral con el mismo contenido y otras palabras: el 14.8.4 "
          "(pag. impresa 134), que es el que rige DIRECTAMENTE un muro de "
          "contencion como el cabezal."),
)

E060_14_8_4 = _cita(
    id="E060.14.8.4",
    fuente_id="E060",
    numeral="14.8.4",
    titulo_numeral="Muros de contención",
    pagina_impresa="134",
    pagina_pdf=134,
    texto_literal=Verbatim(
        texto=("El refuerzo vertical y horizontal no se colocará a un "
               "espaciamiento mayor que tres veces el espesor del muro ni que "
               "400 mm."),
        pagina_pdf=134),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("E060.14.3.3",),
    nota=("Hallado al verificar: es el gemelo del 14.3.3 para muros de "
          "contencion, y por tanto el aplicable directo a un cabezal. El "
          "expediente citaba solo el 14.3.3."),
)


# ===========================================================================
# E.050 Suelos y Cimentaciones  (desfase 0)
# ===========================================================================

E050_21 = _cita(
    id="E050.21",
    fuente_id="E050",
    numeral="Art. 21.1 y 21.2",
    titulo_numeral="Factor de seguridad frente a una falla por corte",
    pagina_impresa="34",
    pagina_pdf=34,
    texto_literal=Verbatim(
        texto=("Los factores de seguridad mínimos que deben tener las "
               "cimentaciones son los siguientes: 21.1. Para cargas "
               "estáticas: 3,0 21.2. Para solicitación máxima de sismo o "
               "viento (la que sea más desfavorable): 2,5"),
        pagina_pdf=34),
    caracter=Caracter.EXIGENCIA,
    nota=("LA SEGUNDA CONDICION NO ES «SISMICA» A SECAS: es «solicitacion "
          "maxima de sismo O VIENTO (la que sea mas desfavorable)». El viento "
          "esta dentro de la misma casilla, y la clave «sismico» del "
          "repositorio lo excluia (NOR-E050-01)."),
)

E050_30_3 = _cita(
    id="E050.30.3",
    fuente_id="E050",
    numeral="Art. 30.3",
    titulo_numeral="Cimentaciones superficiales en taludes o en su cercanía",
    pagina_impresa="39",
    pagina_pdf=39,
    texto_literal=Verbatim(
        texto=("El factor de seguridad mínimo del talud, en consideraciones "
               "estáticas debe ser 1,5 y en condiciones sísmicas 1,25."),
        pagina_pdf=39),
    caracter=Caracter.EXIGENCIA,
    nota=("AQUI la norma SI dice «condiciones sismicas». Es el unico de los "
          "tres numerales de FS que usa esa palabra."),
)

E050_39_13_6 = _cita(
    id="E050.39.13.6",
    fuente_id="E050",
    numeral="39.13.6 a) y b)",
    titulo_numeral="Muros de contención",
    pagina_impresa="72",
    pagina_pdf=72,
    jerarquia_numeral=("Sostenimiento de excavaciones",),
    texto_literal=Verbatim(
        texto=("a-1) Condición Estático 1.50 (por volteo y por "
               "deslizamiento)"),
        pagina_pdf=72),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("NOR-E050-01, cerrado. La palabra «sismico» NO APARECE en este "
          "numeral: la segunda condicion se llama «Condición Pseudo - "
          "dinámico» en a-2 y «condición pseudo-dinámica» en b). No es un "
          "sinonimo decorativo -- designa el METODO de analisis, coeficiente "
          "sismico horizontal aplicado como fuerza estatica equivalente --, y "
          "E.050 usa CUATRO vocabularios distintos para esa casilla segun el "
          "numeral: «sismo o viento» (Art. 21.2), «condiciones sismicas» "
          "(Art. 30.3), «pseudo-dinamico» (39.13.6) y «dinamico» a secas "
          "(Anexo I, pag. impresa 74). "
          "Y una coletilla que el repositorio no recogia cierra el numeral y "
          "condiciona a) y b) por igual: «En todos los casos respecto al "
          "estado límite del suelo»."),
)

E050_20 = _cita(
    id="E050.20",
    fuente_id="E050",
    numeral="Art. 20.2 y 20.3",
    titulo_numeral="Capacidad de carga",
    pagina_impresa="33",
    pagina_pdf=33,
    texto_literal=Verbatim(
        texto=("En suelos friccionantes (gravas, arenas y gravas-arenosas), "
               "se emplea una cohesión (c) igual a cero."),
        pagina_pdf=33),
    caracter=Caracter.EXIGENCIA,
    nota=("El repositorio citaba «Art. 20» a secas; los numerales exactos son "
          "20.2 (cohesivos, phi = 0) y 20.3 (friccionantes, c = 0). El "
          "simbolo phi no sobrevive a la extraccion de texto -- la norma lo "
          "compone con fuente simbolica --, y por eso el `texto_literal` es "
          "el inciso que si se puede buscar."),
)

E050_38_4_3 = _cita(
    id="E050.38.4.3",
    fuente_id="E050",
    numeral="38.4.3",
    titulo_numeral="Exploración de campo",
    pagina_impresa="51",
    pagina_pdf=51,
    jerarquia_numeral=("Licuación de suelos",),
    texto_literal=Verbatim(
        texto=("Las perforaciones deben tener una profundidad mínima de 15 m "
               "y deben ser realizadas por las técnicas de lavado o rotativa. "
               "Dentro de las perforaciones se llevan a cabo Ensayos de "
               "Penetración Estándar SPT (NTP 339.133) espaciados "
               "obligatoriamente cada 1 m."),
        pagina_pdf=51),
    caracter=Caracter.EXIGENCIA,
    nota=("NOR-E050-02, cerrado, y con un hallazgo de mas. (1) EL "
          "ESPACIAMIENTO SI TIENE NUMERAL: es este, y el repositorio lo "
          "declaraba «sin numeral». Ademas va reforzado con «obligatoriamente». "
          "(2) LO GRAVE, que el repositorio omitia: los dos valores viven bajo "
          "«Articulo 38.- Licuacion de suelos», y el 38.4.1 los dispara SOLO "
          "«Cuando la historia sismica del lugar haga sospechar la posibilidad "
          "de ocurrencia de Licuacion». NO son el programa de SPT general de "
          "E.050 -- ese esta en el 14.2.3 y la Tabla 3, pags. 18-19 --: son el "
          "programa de exploracion PARA ANALISIS DE LICUEFACCION. Citarlos "
          "como minimos universales del SPT extiende la norma mas alla de lo "
          "que dice."),
)


# ===========================================================================
# EG-2013
# ===========================================================================

EG_503_04 = _cita(
    id="EG2013.503.04#T503_07",
    fuente_id="EG2013",
    numeral="503.04, Tabla 503-07",
    titulo_numeral="Clases de concreto",
    pagina_impresa="912",
    pagina_pdf=920,
    pagina_pdf_titulo=919,
    texto_literal=Verbatim(
        texto=("Se compone de concreto simple Clase F y agregado ciclópeo, en "
               "proporción de 30% del volumen total, como máximo"),
        pagina_pdf=920),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("La tabla tiene DOS columnas, no tres: «Clase» y «Resistencia "
          "minima a la compresion a 28 dias». El uso no es columna, es "
          "encabezado de grupo dentro de la primera. Y no lleva ninguna nota "
          "al pie."),
)

# ---------------------------------------------------------------------------
# LAS TRES CITAS QUE DICEN BAJO QUE SECCION SE CONSTRUYE UN MARCO (C7, punto 6)
# ---------------------------------------------------------------------------
# El proyecto mapeaba material -> Seccion del EG-2013 con un dict, y un marco
# de concreto reforzado heredaba la 506. La 506 se titula «Tuberia de concreto
# reforzado»: es atribucion sin fuente, y ademas la MISMA forma del defecto
# NOR-PUE-01 -- numeral que existe, titulo que suena a lo buscado, contenido
# que es otra cosa --. Estas tres citas son las que lo cierran, y hacen falta
# las tres porque cada una responde una pregunta distinta: donde NO cae el
# marco (506.01), bajo que Seccion SI se construye (503.10 h) y que alcance
# tiene esa Seccion (503.01).
EG_506_01 = _cita(
    id="EG2013.506.01#ALCANCE",
    fuente_id="EG2013",
    numeral="506.01",
    titulo_numeral="Descripción",
    pagina_impresa="959",
    pagina_pdf=967,
    pagina_pdf_titulo=967,
    texto_literal=Verbatim(
        texto=("Este trabajo consiste en la instalación de tubos de concreto "
               "reforzado, aprobados para el paso de agua superficial y "
               "desagües pluviales transversales, de acuerdo con estas "
               "especificaciones y de conformidad con el Proyecto."),
        pagina_pdf=967),
    caracter=Caracter.DEFINICION,
    nota=("LO QUE ESTA CITA HACE ES DELIMITAR, y por eso es DEFINICION y no "
          "EXIGENCIA: no prohibe nada, dice de que trata la Seccion. Su "
          "objeto es «la instalacion de TUBOS», y las otras tres piezas de la "
          "misma Seccion lo confirman -- 506.02 remite a AASHTO M-170M y pide "
          "el «diametro interno», y la partida 506.A del Anexo 2 se mide en "
          "METRO LINEAL --. Un marco vaciado in situ no tiene diametro "
          "interior ni se mide por metro lineal de tubo suministrado: la 506 "
          "no lo alcanza. Los cuatro titulos de las Secciones 505 a 508 "
          "empiezan por «Tuberia»."),
)

EG_503_01 = _cita(
    id="EG2013.503.01#ALCANCE",
    fuente_id="EG2013",
    numeral="503.01",
    titulo_numeral="Descripción",
    pagina_impresa="905",
    pagina_pdf=913,
    pagina_pdf_titulo=913,
    texto_literal=Verbatim(
        texto=("Este trabajo consiste en el suministro de concreto de cemento "
               "Portland de diversas resistencias a la compresión, para la "
               "construcción de estructuras de drenaje, muros de contención, "
               "cabezales de alcantarillas, cajas de captación, aletas, "
               "sumideros y estructuras de puentes en general, de acuerdo con "
               "estas especificaciones y de conformidad con el Proyecto."),
        pagina_pdf=913),
    caracter=Caracter.DEFINICION,
    nota=("«ESTRUCTURAS DE DRENAJE» ES EL TERMINO DE ENCABEZAMIENTO y la "
          "lista que sigue es ENUNCIATIVA, no cerrada: un marco de concreto "
          "vaciado in situ es una estructura de drenaje y no esta nombrado "
          "ahi. Que si lo esta bajo esta Seccion lo prueba el 503.10 h), que "
          "le fija plazo de desencofrado a la «placa superior en "
          "alcantarillas de cajon». Por si sola esta cita NO dice que el "
          "marco se pague aqui: eso es ensamblaje del proyecto sobre las tres "
          "citas mas la ausencia de partida propia."),
)

EG_503_10H = _cita(
    id="EG2013.503.10h#CAJON",
    fuente_id="EG2013",
    numeral="503.10 h)",
    titulo_numeral="Operaciones para el vaciado de la mezcla",
    pagina_impresa="926",
    pagina_pdf=934,
    pagina_pdf_titulo=929,
    texto_literal=Verbatim(
        texto="Placa superior en alcantarillas de cajón: 14 días",
        pagina_pdf=934),
    caracter=Caracter.RECOMENDACION,
    nota=("ES LA UNICA MENCION DEL CAJON DE CONCRETO EN TODO EL EG-2013 -- "
          "barrido de las 1282 paginas, ver SIN_PARTIDA_DE_CAJON_EG2013 -- y "
          "hay que leerla por lo que prueba y no por lo que dice. "
          "LO QUE PRUEBA: que el EG-2013 CONTEMPLA la alcantarilla de cajon "
          "de concreto y la regula bajo la Seccion 503, «Concreto "
          "estructural». Una norma que fija plazo de desencofrado de la placa "
          "superior de un cajon esta regulando su vaciado in situ. "
          "LO QUE NO DICE: nada sobre pago, ni sobre cobertura, ni sobre "
          "dimensiones. Y su CARACTER no es exigencia: el parrafo que la "
          "introduce dice «Excepcionalmente si las operaciones de campo no "
          "estan controladas por pruebas de laboratorio la siguiente lista "
          "PUEDE ser empleada como GUIA para el tiempo minimo requerido antes "
          "de la remocion de encofrados y soportes». O sea que el plazo es "
          "guia condicionada; lo que NO es condicionado es la existencia de "
          "la fila, que es lo unico que este proyecto le pide."),
)

EG_508_07 = _cita(
    id="EG2013.508.07#RELLENO_MIN",
    fuente_id="EG2013",
    numeral="508.07",
    titulo_numeral="Colocación del relleno alrededor de la estructura",
    pagina_impresa="984",
    pagina_pdf=992,
    texto_literal=Verbatim(
        texto=("La altura de relleno mínimo desde la clave de la tubería "
               "hasta el nivel de la subrasante será de 0,30 m."),
        pagina_pdf=992),
    caracter=Caracter.EXIGENCIA,
    nota=("NOR-EG-01 / NOR-EG-02. La pagina impresa es la 984 (PDF 992). La "
          "982 (PDF 990) trae 508.02 b), c) y d) -- calidad del tubo, "
          "muestreo y material para cama de asiento --, nada de altura de "
          "relleno. El desfase de este documento es +8, el mayor del corpus, "
          "y confundir impresa con PDF produce exactamente ese error. "
          "NO CONFUNDIR CON SU VECINA: el 508.08 (pag. impresa 985) tambien "
          "dice 0,30 m, pero es la exigencia de EJECUCION -- que el equipo "
          "pesado no circule antes de alcanzarla --, no la altura minima de "
          "diseño. Dos frases con el mismo numero en paginas contiguas."),
)

EG_205_12 = _cita(
    id="EG2013.205.12c1",
    fuente_id="EG2013",
    numeral="205.12 c) 1.",
    # El EG-2013 lo imprime en SINGULAR, «Criterio», y en la pag. impresa 191:
    # el apartado c) y su punto 1 caen dos paginas mas adelante.
    titulo_numeral="205.12 Criterio",
    pagina_impresa="193",
    pagina_pdf=201,
    pagina_pdf_titulo=199,
    texto_literal=Verbatim(
        texto=("el 90% de la máxima densidad obtenida en el ensayo Proctor "
               "Modificado de referencia (De) para la base y cuerpo del "
               "terraplén y el 95% con respecto a la máxima obtenida en el "
               "mismo ensayo, cuando se verifique la compactación de la "
               "corona del terraplén."),
        pagina_pdf=201),
    caracter=Caracter.EXIGENCIA,
    nota=("ES LA REMISION DE SEGUNDO NIVEL de tres de las cuatro fichas de "
          "cama y relleno: el «95 % MDS» que el expediente les atribuia no es "
          "literal de las Secciones 505, 506 ni 507 -- llega desde aqui, por "
          "remision. El valor es correcto; lo que faltaba era decir por que "
          "via llega, que es la diferencia entre una cita y una deduccion."),
)


# ===========================================================================
# HDS-5, 3a ed.  (por capitulo)
# ===========================================================================

HDS5_A2 = _cita(
    id="HDS5_3ED.A.2",
    fuente_id="HDS5_3ED",
    numeral="A.2, A.2.1",
    titulo_numeral="INLET CONTROL EQUATIONS",
    pagina_impresa="A.2",
    pagina_pdf=191,
    pagina_pdf_titulo=190,
    texto_literal=Verbatim(
        texto="Ku          Unit conversion 1.0 (1.811 SI)",
        pagina_pdf=191),
    caracter=Caracter.DEFINICION,
    nota=("NOR-HDS-03, confirmado: `Ku` y `Ks` estan en la LISTA DE VARIABLES "
          "de las ecuaciones del num. A.2.1, pag. impresa A.2, y NO en la "
          "Tabla A.1. La Tabla A.1 tiene nueve columnas y de constantes de la "
          "ecuacion solo cuatro -- K, M, c e Y --: no hay columna K_u ni "
          "columna K_s."),
)

HDS5_A21_KS = _cita(
    id="HDS5_3ED.A.2.1#KS",
    fuente_id="HDS5_3ED",
    numeral="A.2.1",
    titulo_numeral="Unsubmerged Inlet Control Equations",
    pagina_impresa="A.2",
    pagina_pdf=191,
    pagina_pdf_titulo=190,
    texto_literal=Verbatim(
        texto="Ks          Slope correction, -0.5 (mitered inlets +0.7)",
        pagina_pdf=191),
    caracter=Caracter.DEFINICION,
)

HDS5_A21_QLIM = _cita(
    id="HDS5_3ED.A.2.1#QLIM",
    fuente_id="HDS5_3ED",
    numeral="A.2.1",
    titulo_numeral="Unsubmerged Inlet Control Equations",
    pagina_impresa="A.1",
    pagina_pdf=190,
    texto_literal=Verbatim(
        texto=("Equations (A.1) and (A.2) apply up to about Q/AD0.5 = 3.5 "
               "(1.93 SI)."),
        pagina_pdf=190),
    caracter=Caracter.APROXIMACION,
    nota=("«apply up to ABOUT»: la fuente NO fija un umbral duro. Y los 3.5 "
          "son del sistema INGLES; su equivalente SI, entre parentesis, es "
          "1.93. Como `caudal_adimensional` multiplica por KU_SI = "
          "1.811, el q* que M4 compara ya esta en la escala inglesa y le "
          "corresponden 3.5 y 4.0: cambiarlos por los del parentesis seria "
          "aplicar dos veces la conversion."),
)

HDS5_A22_QLIM = _cita(
    id="HDS5_3ED.A.2.2#QLIM",
    fuente_id="HDS5_3ED",
    numeral="A.2.2",
    titulo_numeral="Submerged Inlet Control Equations",
    pagina_impresa="A.2",
    pagina_pdf=191,
    texto_literal=Verbatim(
        texto=("The submerged equation (A.3) applies above about Q/AD0.5 = "
               "4.0 (2.21 SI)."),
        pagina_pdf=191),
    caracter=Caracter.APROXIMACION,
)

HDS5_TA1 = _cita(
    id="HDS5_3ED.TA.1",
    fuente_id="HDS5_3ED",
    numeral="Table A.1",
    titulo_numeral=("Constants for Inlet Control Equations for Charts in "
                    "Appendix G."),
    pagina_impresa="A.8",
    pagina_pdf=197,
    texto_literal=Verbatim(
        texto=("Table A.1.  Constants for Inlet Control Equations for Charts "
               "in Appendix G."),
        pagina_pdf=197),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    condiciones=(
        # LA CONDICION QUE C2 DEJA ABIERTA, y que es la razon de que las
        # quince filas del cajon entren como `PendienteDeCondicion` y no como
        # `Usada`. La tabla elige fila por CONFIGURACION DE BORDE -- es una
        # columna suya --, y para el cajon esa configuracion no esta
        # declarada en ninguna parte: el criterio que la elegiria,
        # 'embocadura_cajon', lo abre C5 y HOY NO EXISTE.
        #
        # Por D4 BLOQUEA, y tiene que bloquear: las quince filas no son
        # equivalentes ni parecidas. Entre la Carta 8 escala 1 (K = 0.026,
        # Forma 1) y la Carta 11 escala 1 (K = 0.545, Forma 2) no hay un
        # matiz, hay dos ecuaciones distintas. Elegir una por defecto seria
        # rellenar un vacio en silencio.
        CondicionAplicacion(
            id="COND-EMBOCADURA-CAJON",
            texto=Verbatim(texto="Inlet Configuration", pagina_pdf=197),
            cita_id="HDS5_3ED.TA.1",
            resuelve=PorCriterio(clave="embocadura_cajon"),
            efecto_si_indeterminada=Efecto.BLOQUEA),
    ),
    nota=("ERRATA DE LA PROPIA FUENTE, hallada al verificar: el titulo dice "
          "«for Charts in Appendix G» y en esta 3a edicion NO EXISTE un "
          "Apendice G -- las cartas estan en el Apendice C. Se transcribe "
          "como lo imprime, con la advertencia, para que quien lo busque lo "
          "encuentre. "
          "SEGUNDA REMISION RANCIA DE LA MISMA FUENTE, hallada en C2 y sin "
          "ID propio todavia: el num. A.3.1 (pag. impresa A.2, PDF 191) dice "
          "«From Table A.1, Chart 34, Scale 3», y la carta 34 -- Pipe Arch "
          "CM -- esta en la Tabla A.2 de esta edicion, no en la A.1. Explica "
          "por que el repositorio llego a afirmar que la Tabla A.1 trae "
          "pipe-arch, que no lo trae. "
          "Y LA PAGINA IMPRESA «A.8» ES INFERIDA, NO LEIDA: PDF 197 no lleva "
          "folio. La inferencia por secuencia es correcta (PDF 196 lleva "
          "A.7) y la regla de paginacion la predice; queda dicho aqui "
          "porque «pagina impresa» nombra algo que en esta pagina no esta "
          "impreso. "
          "VERIFICADO EN I3 (verificador-normativo, metodo texto extraido "
          "con coordenadas + render de la pagina entera, los cuatro bordes): "
          "PDF 197 no imprime folio en ningun borde -- la pagina esta "
          "almacenada apaisada de forma nativa (792x612, rotation=0), asi "
          "que el barrido de texto no pierde nada --; los folios vecinos "
          "leidos son A.5@194, A.6@195, A.7@196 y B.1@203; entre A.7 y B.1 "
          "van SEIS paginas sin folio y no «cuatro apaisadas», como decia "
          "esta nota hasta I3: las cinco del Apendice A -- tres apaisadas "
          "de tablas (197-199), la VERTICAL de las Tablas A.4-A.6 (200) y "
          "la en blanco (201) -- mas la portadilla del Apendice B (202), "
          "que por regla del documento nunca folia. La cadena «A.8» no "
          "aparece en ninguna pagina del PDF, y ningun esquema consistente "
          "con los folios impresos puede asignar a PDF 197 otro numero: la "
          "unica lectura alternativa no es otro folio, es «sin folio». "
          "Veredicto: CORRECTO-INFERIDO; `pagina_impresa` se queda en "
          "«A.8» -- es el valor que la regla de paginacion de T6 predice -- "
          "y esta nota es la que dice que no es una lectura."),
)

HDS5_TC2 = _cita(
    id="HDS5_3ED.TC.2",
    fuente_id="HDS5_3ED",
    numeral="Table C.2",
    titulo_numeral="Entrance Loss Coefficients.",
    pagina_impresa="C.6",
    pagina_pdf=216,
    texto_literal=Verbatim(
        texto="Table C.2.  Entrance Loss Coefficients.",
        pagina_pdf=216),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    condiciones=(
        # LA HERMANA DE `COND-EMBOCADURA-CAJON`, Y VA APARTE A PROPOSITO. Las
        # siete filas de cajon de ESTA tabla tambien esperan a que se declare
        # la embocadura, pero colgarlas de la condicion de la Tabla A.1 hacia
        # que la ventana pintara, como razon de que una fila de la C.2 no se
        # pueda elegir, un `Verbatim` de la pagina 197 -- «Inlet
        # Configuration», que es un encabezado de columna de OTRA tabla --.
        # La evidencia de una condicion tiene que salir de la pagina que la
        # impone.
        CondicionAplicacion(
            id="COND-EMBOCADURA-CAJON-KE",
            texto=Verbatim(
                texto="Type of Structure and Design of Entrance",
                pagina_pdf=216),
            cita_id="HDS5_3ED.TC.2",
            resuelve=PorCriterio(clave="embocadura_cajon"),
            efecto_si_indeterminada=Efecto.BLOQUEA),
    ),
    nota=("NOR-HDS-01, confirmado contra el PDF. La cita original decia "
          "«pagina C.2», que es EL NUMERO DE LA TABLA LEIDO COMO PAGINA: la "
          "pag. impresa C.2 (PDF 212) es la continuacion del indice de cartas "
          "del apendice. La tabla esta en la C.6 (PDF 216)."),
)

HDS5_3_1_4 = _cita(
    id="HDS5_3ED.3.1.4#K",
    fuente_id="HDS5_3ED",
    numeral="3.1.4, ec. (3.4b)",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.10",
    pagina_pdf=92,
    pagina_pdf_titulo=87,
    texto_literal=Verbatim(
        texto="KU  =  29 in English Units (19.63 in SI)",
        pagina_pdf=92),
    caracter=Caracter.DEFINICION,
    nota=("El 19.63 ESTA en la fuente, no es derivacion. El numeral abre en "
          "la pag. impresa 3.5 y la ecuacion esta en la 3.10."),
)

HDS5_3_1_3 = _cita(
    id="HDS5_3ED.3.1.3#TRANSICION",
    fuente_id="HDS5_3ED",
    numeral="3.1.3",
    titulo_numeral="Inlet Control",
    pagina_impresa="3.4",
    pagina_pdf=86,
    texto_literal=Verbatim(
        texto=("The flow transition zone between the low headwater (weir "
               "control) and the high headwater (orifice control) flow "
               "conditions is poorly defined.  This zone is approximated by "
               "plotting the unsubmerged and submerged flow equations and "
               "connecting them with a line tangent to both curves"),
        pagina_pdf=86),
    caracter=Caracter.APROXIMACION,
    nota=("NOR-HDS-06, cerrado: ESTE es el numeral de la zona de transicion, "
          "no el «Cap. IV» que el criterio citaba. El Capitulo 4 de la 3a ed. "
          "se titula «CULVERT DESIGN FOR AQUATIC ORGANISM PASSAGE (AOP)» -- "
          "paso de fauna acuatica -- y tampoco se salva leyendolo como la "
          "edicion de 1985, cuyo Capitulo 4 es «Tapered Inlets». Es el mismo "
          "patron que NOR-PUE-01: el numeral existe y su titulo no "
          "corresponde. La otra mitad de la cita vieja, «y Apendice A», SI "
          "era correcta: la misma regla esta en el num. A.2."),
)

# EL REPARTO ENTRE BARRILES, que la regla vinculante #3 de ruta_familia_c.md
# §6 afirmaba sin cita (EXT-M-03): «Multicelda se resuelve por barril, no por
# conjunto». El numeral que lo sostiene es el 5.4.3 «Multiple Barrels», cuyo
# titulo esta en la pag. impresa 5.14 (PDF 150) y cuyo parrafo del reparto
# esta en la 5.15 (PDF 151). Verificado en EXT-2 contra el PDF con PyMuPDF:
# la oracion es una sola y termina en «among the barrels.» Lleva ademas la
# condicion que la fuente pone -- «with identical hydraulic characteristics»
# -- y por eso el `Verbatim` la incluye: sin ella el reparto igual seria
# una afirmacion mas ancha que la de la fuente.
HDS5_5_4_3_REPARTO = _cita(
    id="HDS5_3ED.5.4.3#REPARTO",
    fuente_id="HDS5_3ED",
    numeral="5.4.3",
    titulo_numeral="Multiple Barrels",
    pagina_impresa="5.15",
    pagina_pdf=151,
    pagina_pdf_titulo=150,
    texto_literal=Verbatim(
        texto=("The nomographs provide the culvert discharge rate per barrel "
               "for pipes or the flow per foot (meter) of span width for box "
               "culverts.  For multiple barrels with identical hydraulic "
               "characteristics, the total discharge is assumed to be "
               "divided equally among the barrels."),
        pagina_pdf=151),
    caracter=Caracter.APROXIMACION,
    sesion=EXT2,
    nota=("Es el sosten de la regla vinculante #3 (Q/N por barril) que hasta "
          "EXT-2 no estaba en el registro. La fuente lo escribe como un "
          "SUPUESTO («is assumed») condicionado a barriles hidraulicamente "
          "identicos -- misma seccion, misma cota de fondo, misma "
          "embocadura --, que es exactamente lo que `SeccionRectangular` "
          "modela: UNA celda repetida N veces. Para barriles distintos o con "
          "cotas distintas la misma pagina remite a un procedimiento "
          "iterativo o a una curva de funcionamiento combinada (Section "
          "3.5), que el proyecto NO implementa: el criterio 'n_celdas_cajon' "
          "declara N celdas iguales y nada mas."),
)

# LA LECTURA DE «most of its length» (E-A). Desde E-A la primera condicion
# de h_o se MIDE --el perfil de la lamina da la longitud a seccion llena--, y
# medirla obliga a decir cuanto es «la mayor parte». No es un valor elegido:
# es el significado de la palabra, mas de la mitad. Aun asi es una lectura
# del proyectista sobre un texto que no escribe el numero, y por eso va como
# `Interpretacion`, con lo que juega en contra; el numero es un [A] con
# ventana (`criterios_adoptados 'fraccion_llena_mayor_parte'`, 0.5), no una
# cifra [N].
INTERPRETACION_MAYOR_PARTE = Interpretacion(
    texto=("Que «for most of its length» signifique MAS DE LA MITAD de la "
           "longitud del barril --fraccion a seccion llena > 1/2-- es la "
           "lectura que este proyecto adopta para juzgar la primera "
           "condicion de uso de h_o con la longitud llena que el perfil de "
           "la lamina mide (paso 4.3c). La fuente escribe la palabra, no el "
           "numero."),
    en_contra=("la misma fuente, en la pag. impresa 3.12, relaja la "
               "condicion a «works best when the barrel flows full over at "
               "least PART of its length» y da resultados adecuados hasta "
               "HW = 0.75D aun con el barril «partly full over its entire "
               "length», de modo que la mayor parte no es una frontera "
               "dura del propio manual",
               "«most» admite lecturas mas exigentes («casi toda») que la "
               "mitad, y la fuente no las excluye"),
    a_favor=("en ingles tecnico «most of» es la mayoria: mas de la mitad",
             "es la lectura menos restrictiva compatible con la palabra, y "
             "la consecuencia de fallarla la fija la pag. 3.12 y no esta "
             "lectura: el HW sigue siendo el de la aproximacion mientras "
             "HW/D >= 0.75, con el remanso impreso como comprobacion"),
)

HDS5_3_3_3 = _cita(
    id="HDS5_3ED.3.3.3#HO",
    fuente_id="HDS5_3ED",
    numeral="3.3.3",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.24",
    pagina_pdf=106,
    texto_literal=Verbatim(
        texto=("Approximate hydraulic gradeline ho = (dc + D)/2 can only be "
               "used if the barrel flows full for most of its length."),
        pagina_pdf=106),
    caracter=Caracter.APROXIMACION,
    interpretacion=INTERPRETACION_MAYOR_PARTE,
    nota=("Las TRES condiciones estan en esta pagina, y la primera tiene una "
          "SEGUNDA MITAD que el expediente no recogia: «It should not be used "
          "if the inlet is not submerged». Son dos condiciones, no una. "
          "Ademas la fuente no escribe la razon HW/D: escribe «the headwater "
          "depth (referenced to the inlet invert) is less than 1.2D», y la "
          "referencia al invert de entrada es parte de la definicion. Las "
          "tres son `should` / `can only`, no `shall`. "
          "C4: EL VERBATIM ESTABA TRUNCADO EN «flows full for», que es donde "
          "el PDF parte la linea, y la truncadura se llevaba «most of its "
          "length» -- o sea LA CONDICION MISMA --. Leido asi, el rotulo "
          "«texto literal» publicaba un requisito MAS LAXO que el de la "
          "fuente: «que el barril fluya lleno» en vez de «que fluya lleno en "
          "la mayor parte de su longitud». Es la elision sin marcar que "
          "CLAUDE.md persigue, y `test_normativa_pdf` no la veia porque "
          "verifica por subcadena y una truncadura siempre lo es. Verificado "
          "contra la PDF 106: la oracion termina en «most of its length.»"),
)


# LAS OTRAS DOS CONDICIONES DE h_o, cada una con su cita. Vivian como prosa
# dentro de `constantes_normativas.H_O_CONDICION_TEXTO`, o sea transcritas a
# mano una segunda vez y de-acentuadas; y la segunda venia ademas con una
# ELISION SIN MARCAR -- se saltaba la oracion sobre el calculo de remanso --
# bajo un rotulo que decia "Texto literal". Aqui estan enteras y verificadas
# contra la pagina.
HDS5_3_3_3_HO_SUMERGIDA = _cita(
    id="HDS5_3ED.3.3.3#HO_SUMERGIDA",
    fuente_id="HDS5_3ED",
    numeral="3.3.3",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.24",
    pagina_pdf=106,
    texto_literal=Verbatim(
        texto="It should not be used if the inlet is not submerged.",
        pagina_pdf=106),
    caracter=Caracter.EXIGENCIA,
    derivado_de="HDS5_3ED.3.3.3#HO",
    nota=("Segunda mitad de la vineta de h_o, y es una condicion DISTINTA de "
          "la primera: aquella acota por llenado del barril, esta por "
          "sumergencia de la entrada. El expediente las leia como una sola."),
)

HDS5_3_3_3_HO_1_2D = _cita(
    id="HDS5_3ED.3.3.3#HO_1_2D",
    fuente_id="HDS5_3ED",
    numeral="3.3.3",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.24",
    pagina_pdf=106,
    texto_literal=Verbatim(
        texto=("If outlet control governs and the headwater depth "
               "(referenced to the inlet invert) is less than 1.2D, it is "
               "possible that the barrel flows partly full though its entire "
               "length.  In this case, caution should be used in applying "
               "the approximate method of setting the downstream elevation "
               "based on the greater of tailwater or (dc + D)/2.  If a more "
               "accurate headwater is necessary, backwater calculations "
               "(Section 3.5) should be used to check the result from the "
               "approximate method. If the headwater depth falls below "
               "0.75D, the approximate method should not be used."),
        pagina_pdf=106),
    caracter=Caracter.EXIGENCIA,
    derivado_de="HDS5_3ED.3.3.3#HO",
    nota=("De aqui salen los DOS limites que `M4` evalua punto por punto: "
          "1.2D (cautela) y 0.75D (no usar). La transcripcion anterior del "
          "expediente se saltaba, sin marcarlo, la oracion sobre las "
          "backwater calculations -- que es justamente la que dice QUE HACER "
          "cuando el punto cae en la banda de cautela. Una elision no marcada "
          "dentro de algo rotulado «texto literal» es la misma clase de "
          "defecto que NOR-HID-06."),
)

# ---------------------------------------------------------------------------
# 3.1.4 (pag. impresa 3.12) y 3.5.1 (pags. 3.36-3.38): el PERFIL DE LA LAMINA
# por remanso, que es el procedimiento de barril parcialmente lleno (E-A)
# ---------------------------------------------------------------------------
# Siete citas, verificadas contra las PDF 94, 118, 119 y 120, que sostienen
# `M4.perfil_lamina` y el paso F4.PERFIL. Las cuatro primeras estan en la
# prosa «Hydraulics of Outlet Control (Unsubmerged Outlet)» del num. 3.1.4:
# el procedimiento (de donde arranca y hacia donde avanza), el empalme con la
# linea de energia llena y la Ec. 3.7, como se forma el HW en la entrada, y
# el limite de 0.75D bajo el que «backwater calculations are required». Las
# tres de la Section 3.5.1 son las que dicen QUE perfil se computa en cada
# caso y para que: la fraccion de barril lleno, la M2/M1 desde la salida y la
# S1 que solo se usa si llega a la cara de entrada. La Ec. 3.7 NO se cita
# como Verbatim: el PDF la extrae como una hilera de simbolos sueltos
# («g 2 V R n K L H S 2 33 . 1 2 u f f = =»), y lo que se cita es la frase
# que la introduce; la ecuacion misma se transcribe en la formula del paso.
HDS5_3_1_4_REMANSO = _cita(
    id="HDS5_3ED.3.1.4#REMANSO",
    fuente_id="HDS5_3ED",
    numeral="3.1.4",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.12",
    pagina_pdf=94,
    pagina_pdf_titulo=87,
    texto_literal=Verbatim(
        texto=("These calculations begin at the water surface at the "
               "downstream end of the culvert and proceed upstream to the "
               "entrance of the culvert (see Section 3.5). The downstream "
               "water surface is based on critical depth at the culvert "
               "outlet or on the tailwater depth, whichever is higher."),
        pagina_pdf=94),
    caracter=Caracter.DEFINICION,
    sesion=EA,
    nota=("Es el procedimiento en prosa (pieza 1 del paquete I1): la "
          "frontera aguas abajo max(y_c, TW) y la marcha hacia la entrada. "
          "La frase anterior dice para que casos: «Backwater calculations "
          "may be required for the partly full flow conditions shown in "
          "Figures 3.7A and C»."),
)

HDS5_3_1_4_EMPALME = _cita(
    id="HDS5_3ED.3.1.4#EMPALME",
    fuente_id="HDS5_3ED",
    numeral="3.1.4, ec. (3.7)",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.12",
    pagina_pdf=94,
    pagina_pdf_titulo=87,
    texto_literal=Verbatim(
        texto=("If the calculated backwater profile intersects the top of "
               "the barrel, as in Figure 3.7B, a straight, full flow "
               "hydraulic grade line extends from that point upstream to "
               "the culvert entrance. From Equation 3.4b, the full flow "
               "friction slope is:"),
        pagina_pdf=94),
    caracter=Caracter.DEFINICION,
    sesion=EA,
    nota=("La Ec. 3.7 sigue a esta frase: Sf = Hf/L = Ku·n²·V²/(R^1.33·2g), "
          "con Ku = 29 (19.63 en SI, la misma `K_FRICCION_SI` de la Sec. "
          "4.3). El proyecto la escribe con R^(4/3), como `perdida_carga`, "
          "y la usa en los dos sentidos: la linea llena que arranca en un TW "
          "sobre la clave y BAJA de ella aguas arriba cuando Sf < S (el caso "
          "del corredor de referencia, B-01 ampliada), y la que arranca "
          "donde la M2 corta la clave (Fig. 3.7B)."),
)

HDS5_3_1_4_HW_REMANSO = _cita(
    id="HDS5_3ED.3.1.4#HW_REMANSO",
    fuente_id="HDS5_3ED",
    numeral="3.1.4",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.12",
    pagina_pdf=94,
    pagina_pdf_titulo=87,
    texto_literal=Verbatim(
        texto=("The inlet losses and the velocity head are added to the "
               "elevation of the hydraulic grade line at the inlet to obtain "
               "the headwater elevation."),
        pagina_pdf=94),
    caracter=Caracter.DEFINICION,
    sesion=EA,
    nota=("Es la forma del HW por remanso: HW = y_entrada + (1 + ke)·"
          "V_entrada²/2g, con las velocidades de aproximacion y de salida "
          "nulas (num. 3.3.3, «assumed to be zero for the manual method»). "
          "Con la linea llena de punta a punta reproduce exactamente "
          "HW = H + h_o - S·L de `control_salida` con h_o = TW."),
)

HDS5_3_1_4_0_75D = _cita(
    id="HDS5_3ED.3.1.4#0_75D",
    fuente_id="HDS5_3ED",
    numeral="3.1.4",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.12",
    pagina_pdf=94,
    pagina_pdf_titulo=87,
    texto_literal=Verbatim(
        texto=("Adequate results are obtained down to a headwater of 0.75D. "
               "For lower headwaters, backwater calculations are required "
               "to obtain accurate headwater elevations."),
        pagina_pdf=94),
    caracter=Caracter.EXIGENCIA,
    sesion=EA,
    nota=("Las dos frases anteriores de la misma pagina dicen cuando el "
          "metodo aproximado «works best» (barril lleno al menos en parte) y "
          "que «becomes increasingly inaccurate as the headwater falls "
          "further below the top of the barrel». Esta es la que CUANTIFICA: "
          "hasta 0.75D los resultados son adecuados aun con el barril "
          "parcialmente lleno en toda su longitud, y por debajo el remanso "
          "es obligatorio («are required»). Es lo que sostiene que bajo "
          "HW/D < 0.75 `ResultadoHidraulico.HW_salida` sea el HW del remanso "
          "y no el de la aproximacion, y que por encima la aproximacion siga "
          "gobernando con el remanso impreso como comprobacion (v8 §4.3). "
          "Conviene leerla junto a la pag. 3.24: alli la vineta dice «can "
          "only be used if the barrel flows full for most of its length», "
          "una condicion MAS estricta que esta; el proyecto mide aquella "
          "(paso 4.3c) y aplica esta, y lo declara como discrepancia interna "
          "de la fuente en `constantes_normativas.H_O_CONDICION_APLICACION`."),
)

HDS5_3_5_PERFIL = _cita(
    id="HDS5_3ED.3.5#PERFIL",
    fuente_id="HDS5_3ED",
    numeral="3.5",
    titulo_numeral="CULVERT DESIGN USING SOFTWARE (WATER SURFACE PROFILES)",
    pagina_impresa="3.36",
    pagina_pdf=118,
    pagina_pdf_titulo=116,
    texto_literal=Verbatim(
        texto=("Beginning with HY-8, water surface profile computation "
               "within the culvert barrel was adopted to refine the "
               "computation of flow depth, flow velocity, and length of "
               "barrel flowing full."),
        pagina_pdf=118),
    caracter=Caracter.DEFINICION,
    sesion=EA,
    nota=("La frase esta en el parrafo introductorio de la Seccion 3.5 que "
          "abre la pag. 3.36, justo ANTES del encabezado 3.5.1 (el encabezado "
          "3.5 esta en la pag. 3.34, PDF 116), y es la que nombra las TRES "
          "salidas del "
          "perfil que E-A implementa: el tirante (V1), la velocidad (V2) y "
          "la longitud de barril lleno (la primera condicion de h_o). El "
          "parrafo sigue: «The profile is determined by first establishing "
          "if the culvert slope is supercritical (inlet control) or "
          "subcritical (outlet control). Next, the tailwater is used to "
          "establish which profile to assume and at what depth to start "
          "the profile»."),
)

HDS5_3_5_1_S1 = _cita(
    id="HDS5_3ED.3.5.1#S1",
    fuente_id="HDS5_3ED",
    numeral="3.5.1",
    titulo_numeral="USGS Flow Types and Water Surface Profiles",
    pagina_impresa="3.37",
    pagina_pdf=119,
    pagina_pdf_titulo=118,
    texto_literal=Verbatim(
        texto=("For this case, an S1 curve is computed and used if the S1 "
               "curve extends to the face of the culvert."),
        pagina_pdf=119),
    caracter=Caracter.DEFINICION,
    sesion=EA,
    nota=("Parrafo «USGS Flow Type 1 (Inlet Control)». Es lo que sostiene "
          "`PerfilLamina.alcanza_entrada`: en pendiente pronunciada la S1 "
          "que arranca en el TW (o en y_c, con longitud cero) solo gobierna "
          "el HW si llega a la cara de entrada; si corta y_c antes, el "
          "control es de entrada y aguas arriba del resalto el flujo es "
          "supercritico. La fuente sigue con la localizacion del resalto "
          "por la profundidad secuente (JFt, JFf) y, en HY-8 7.3, por "
          "momentum: el proyecto NO situa el resalto --le basta saber que "
          "la S1 no llega-- y lo deja escrito en decisiones_diferidas.md."),
)

HDS5_3_5_1_TIPO7 = _cita(
    id="HDS5_3ED.3.5.1#TIPO7",
    fuente_id="HDS5_3ED",
    numeral="3.5.1",
    titulo_numeral="USGS Flow Types and Water Surface Profiles",
    pagina_impresa="3.38",
    pagina_pdf=120,
    pagina_pdf_titulo=118,
    texto_literal=Verbatim(
        texto=("For this case (M2c), the barrel flows full for part of its "
               "length. An M2 curve is computed starting at the outlet to "
               "determine the length of culvert that will flow full."),
        pagina_pdf=120),
    caracter=Caracter.DEFINICION,
    sesion=EA,
    nota=("Parrafo «USGS Flow Type 7 (Outlet Control)»; el de los tipos 4 y "
          "6, en la misma pagina, dice lo mismo para el barril lleno «for "
          "most of its length» (FFt/FFc) y que con «tailwater … higher than "
          "the culvert crown at the exit … the barrel flows full (FFf)». Es "
          "la fuente de que la fraccion llena sea un RESULTADO del perfil y "
          "no una lectura, y de los rotulos M1/M2 de `modelos.TipoDePerfil`."),
)


# ---------------------------------------------------------------------------
# 3.1.6 Outlet Velocity -- con QUE AREA se mide la velocidad a la salida
# ---------------------------------------------------------------------------
# Tres citas y no una, porque la pagina dice tres cosas con tres sujetos
# (EXT-3; EXT-M-01, PC-04). El numeral abre en la pag. impresa 3.17 (PDF 99)
# y la regla del area esta en la 3.18 (PDF 100); la de control de entrada
# esta en la 3.24 (PDF 106), en el ultimo parrafo del num. 3.3.2 antes de que
# empiece el 3.3.3, y por eso se cita alli y no en 3.1.6. Hasta EXT-3 el
# proyecto sabia que el numeral existia --`fundamentos.F4.YC_RECT` decia que
# HDS-5 le da a y_c «un tercer uso que aqui no se implementa»-- y M6 recibia
# siempre la velocidad del flujo uniforme, tambien bajo control de salida,
# donde en pendiente suave con salida libre la de salida a y_c es MAYOR
# (1.508 vs 1.184 m/s en el caso del dictamen).
HDS5_3_1_6_V_SALIDA = _cita(
    id="HDS5_3ED.3.1.6#V_SALIDA",
    fuente_id="HDS5_3ED",
    numeral="3.1.6",
    titulo_numeral="Outlet Velocity",
    pagina_impresa="3.18",
    pagina_pdf=100,
    pagina_pdf_titulo=99,
    texto_literal=Verbatim(
        texto=("In outlet control, the cross sectional area of the flow is "
               "defined by the geometry of the outlet and either critical "
               "depth, tailwater depth, or the height of the conduit"),
        pagina_pdf=100),
    caracter=Caracter.DEFINICION,
    sesion=EXT3,
    nota=("La oracion sigue con «(Figure 3.14).» y la lista de tres vinetas "
          "que reparte los casos por el TW: tirante critico si TW < y_c, TW "
          "si y_c < TW < D, seccion entera si TW > D. `M4.velocidad_de_salida` "
          "lo escribe como el area al tirante min(D, max(TW, y_c))."),
)

HDS5_3_1_6_V_SALIDA_TW = _cita(
    id="HDS5_3ED.3.1.6#V_SALIDA_TW",
    fuente_id="HDS5_3ED",
    numeral="3.1.6",
    titulo_numeral="Outlet Velocity",
    pagina_impresa="3.18",
    pagina_pdf=100,
    pagina_pdf_titulo=99,
    texto_literal=Verbatim(
        texto=("Total barrel area is used when the tailwater exceeds the "
               "top of the barrel"),
        pagina_pdf=100),
    caracter=Caracter.DEFINICION,
    derivado_de="HDS5_3ED.3.1.6#V_SALIDA",
    sesion=EXT3,
    nota=("Tercera vineta de la lista. Es la que sostiene el regimen LLENO "
          "de `modelos.RegimenBarril`: con TW sobre la clave la seccion "
          "efectiva es la entera, y V2 compara Q/A_llena."),
)

# LA SUMERGENCIA DE LA SALIDA NO ASEGURA FLUJO LLENO BAJO CONTROL DE ENTRADA
# (EXT-3, auditoria adversarial). Es la frase que matiza la regla «TW >= D =>
# barril lleno» de la v8 §1.3 y que el proyecto declara como discrepancia en
# `modelos.RegimenBarril` y `M4.regimen_del_barril`: con la salida sumergida y
# el control en la entrada, el tramo de aguas arriba es supercritico y un
# resalto llena el barril hacia la salida.
HDS5_3_1_3_SUMERGENCIA = _cita(
    id="HDS5_3ED.3.1.3#SUMERGENCIA",
    fuente_id="HDS5_3ED",
    numeral="3.1.3",
    titulo_numeral="Inlet Control",
    pagina_impresa="3.2",
    pagina_pdf=84,
    texto_literal=Verbatim(
        texto=("In Figure 3.1C, submergence of the outlet end of the culvert "
               "does not assure outlet control.  In this case, the flow just "
               "downstream of the inlet is supercritical and a hydraulic jump "
               "forms in the culvert barrel."),
        pagina_pdf=84),
    caracter=Caracter.DEFINICION,
    sesion=EXT3,
    nota=("El parrafo sigue con la Fig. 3.1D: «submergence of both the inlet "
          "and the outlet ends of the culvert does not assure full flow». "
          "Sostiene que LLENO, en `modelos.RegimenBarril`, describe la salida "
          "y el tramo aguas abajo del resalto, no la longitud entera."),
)

HDS5_3_3_2_V_SALIDA_ENTRADA = _cita(
    id="HDS5_3ED.3.3.2#V_SALIDA_ENTRADA",
    fuente_id="HDS5_3ED",
    numeral="3.3.2",
    titulo_numeral="Inlet Control",
    pagina_impresa="3.24",
    pagina_pdf=106,
    pagina_pdf_titulo=104,
    texto_literal=Verbatim(
        texto=("If the controlling headwater is based on inlet control, "
               "determine the normal depth and velocity in the culvert "
               "barrel.  The velocity at normal depth is assumed to be the "
               "outlet velocity."),
        pagina_pdf=106),
    caracter=Caracter.APROXIMACION,
    sesion=EXT3,
    nota=("Es el ultimo parrafo del num. 3.3.2, en la misma pagina en que "
          "arranca el 3.3.3. El 3.1.6 dice lo mismo con mas matiz en la pag. "
          "3.18 («the velocity calculated in this manner may be slightly "
          "higher than the actual velocity at the outlet»): por eso el "
          "caracter es APROXIMACION. De las dos ramas de n el proyecto toma "
          "la de n_min, el techo, para el d50 de la Fase 6."),
)

# ---------------------------------------------------------------------------
# V2b - Sedimentacion / colmatacion (Fase 5). Las dos citas que la sostienen.
# ---------------------------------------------------------------------------
# La fila V2b de la tabla de Fase 5 tiene dos mitades: la de SEDIMENTACION,
# que hasta S20 no tenia mas apoyo que el motivo declarado del piso de V2, y
# la del ACCESO DE MANTENIMIENTO en los planos, que sigue siendo entregable de
# dibujo. Estas dos citas cierran la primera: el HDS-5 3.a ed. SI nombra los
# indicadores, y los nombra en terminos de dos numeros que este software ya
# tiene -- la pendiente del barril frente a la del cauce natural y la
# rugosidad del barril frente a la del cauce.
#
# El caracter es DEFINICION y no EXIGENCIA a proposito: la fuente escribe
# «are key indicators of potential problems», no un umbral que haya que
# cumplir. Es el mismo reparto que V1 y V2 -- donde la fuente RECOMIENDA y el
# proyecto endurece --, declarado en el `Fundamento` y no tapado.

HDS5_5_3_3_INDICADORES = _cita(
    id="HDS5_3ED.5.3.3#INDICADORES",
    fuente_id="HDS5_3ED",
    numeral="5.3.3",
    titulo_numeral="Sedimentation",
    pagina_impresa="5.11",
    pagina_pdf=147,
    texto_literal=Verbatim(
        texto=("Therefore, barrel slope less than the natural channel and "
               "roughness greater than the channel are key indicators of "
               "potential problems at culvert sites."),
        pagina_pdf=147),
    caracter=Caracter.DEFINICION,
    sesion=S20,
    nota=("LOS DOS INDICADORES SON COMPARACIONES, NO UMBRALES. La fuente no "
          "escribe ninguna cifra: nombra dos desigualdades entre el conducto "
          "y el cauce natural. La primera -- S_conducto < S_cauce -- este "
          "software la puede evaluar con dos columnas que ya tiene. La "
          "segunda -- n_conducto > n_cauce -- necesita el n del CAUCE "
          "NATURAL, que no es columna de Sec. 1.2 y por eso queda declarada, "
          "no adivinada."),
)

HDS5_5_3_3_ALINEADO = _cita(
    id="HDS5_3ED.5.3.3#ALINEADO",
    fuente_id="HDS5_3ED",
    numeral="5.3.3",
    titulo_numeral="Sedimentation",
    pagina_impresa="5.11",
    pagina_pdf=147,
    texto_literal=Verbatim(
        texto=("Culverts which are located on and aligned with the natural "
               "channel generally do not have a sedimentation problem."),
        pagina_pdf=147),
    caracter=Caracter.DEFINICION,
    derivado_de="HDS5_3ED.5.3.3#INDICADORES",
    sesion=S20,
    nota=("Es la contracara del indicador y la que explica por que la "
          "verificacion pasa en la inmensa mayoria de los puntos de este "
          "corredor: Sec. 7.B fija que la alcantarilla sigue la pendiente "
          "del cauce, de modo que S_conducto = S_cauce salvo que el punto "
          "declare `S_conducto` aparte. El «generally» es de la fuente y se "
          "conserva: no dice «nunca»."),
)


# LA FORMA CON EL MAXIMO NO SE INTERNA COMO `Cita`, Y HAY QUE DECIR POR QUE.
# `M4.control_salida` implementa h_o = max(TW, (dc + D)/2) y la 3a ed. NO
# imprime esa igualdad: la escribe en prosa («the greater of tailwater or
# (dc + D)/2», pag. 3.24). Impresa como igualdad esta en la edicion SI de 1985,
# que tambien vive en normas/ -- «ho = TW or (dc + D)/2 whichever is larger.»,
# PDF 67, comprobado con `aparece_en_pagina` --, y aun asi no puede entrar aqui:
# la `Paginacion` de `HDS5_SI_1985` es `SinDeterminar` (esa copia electronica no
# imprime numeros de pagina propios) y el invariante T6 prohibe que una cita
# suya declare pagina PDF firmada. La prohibicion es correcta y no se toca por
# conveniencia: es la que impide que una pagina supuesta pase por medida.
#
# Consecuencia, declarada donde se usa: el texto de 1985 viaja en
# `constantes_normativas.H_O_FORMA_MAXIMO_TEXTO` y M11 lo imprime bajo el
# rotulo TRANSCRIPCION, nunca bajo "texto literal de la fuente" -- la memoria
# dice de que edicion sale y que la 3a ed. no lo escribe asi.
#
# LA CITA DE ABAJO NO CONTRADICE ESA DECISION, y conviene decir por que antes
# de leerla como precedente: h_o necesitaba entrar a la MEMORIA como literal
# entrecomillado, y eso exige una cita FIRMADA -- imposible aqui --. Esta otra
# es el ANCLA de una parte de DIS-HDS5-EDICIONES («la copia de 1985 imprime
# 29») y no llega a ninguna memoria: la discrepancia es RESUELTA y vive en el
# manifiesto. T6 permite exactamente esta forma -- pagina PDF declarada y
# `verificado=None` -- y la letra del test lo dice con un `or`. Lo que la
# vigila no es la firma sino la suite: T0 acota la pagina y T2 exige que el
# Verbatim aparezca en la PDF 54 en cada corrida con PyMuPDF. El 29 de las
# ecuaciones es imagen incrustada y va en la nota, verificado por render en
# T2 (sesion), no por firma.

HDS5_SI_1985_EC4B = _cita(
    id="HDS5_SI_1985.EC4B#K",
    fuente_id="HDS5_SI_1985",
    numeral="ecs. (4b) y (5)",
    titulo_numeral="Hydraulics of Outlet Control",
    pagina_impresa="s/n",
    pagina_pdf=54,
    pagina_pdf_titulo=52,
    texto_literal=Verbatim(
        texto="L is the length of the culvert barrel, ft (m)",
        pagina_pdf=54),
    caracter=Caracter.DEFINICION,
    verificada=False,
    nota=("SIN FIRMA A PROPOSITO, no sin verificar: la paginacion de la "
          "fuente es `SinDeterminar` (la copia no imprime folios; "
          "`pagina_impresa` dice «s/n» por eso) y el invariante T6 impide "
          "firmar una pagina PDF de una fuente sin paginacion medida. El "
          "contenido esta verificado de hecho (trazabilidad/T2 · "
          "verificador-normativo, 2026-09-12, metodo AMBOS): POR IMAGEN, la "
          "ec. rotulada (4b) imprime Hf = [29 n² L / R^1.33]·V²/2g y la (5) "
          "H = [1 + ke + 29 n² L / R^1.33]·V²/2g -- constante 29, no 19.63; "
          "las ecuaciones son imagenes incrustadas y no salen en la capa de "
          "texto --. POR TEXTO, las definiciones llevan rotulo dual «ft "
          "(m)» (el Verbatim es una de ellas) y «19.63» da cero paginas en "
          "las 410 del documento. Es el ancla de DIS-HDS5-EDICIONES: leer "
          "el 29 «en SI» multiplica el termino de friccion por 29/19.63 = "
          "1.477 (+47.7 % sobre el TERMINO), que en CP-8 sube H de 0.4977 a "
          "0.5455 m (+9.6 % sobre H); es lo que K_FRICCION_SI existe para "
          "atrapar. Las dos bases se dicen juntas porque el repositorio las "
          "mezclo (EXT-G-03)."),
)


# ===========================================================================
# AASHTO LRFD 9a ed. -- el resto
# ===========================================================================

AASHTO_T3_4_1_1 = _cita(
    id="AASHTO_LRFD_9.T3.4.1-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 3.4.1-1",
    titulo_numeral="Load Combinations and Load Factors",
    pagina_impresa="3-17",
    pagina_pdf=71,
    texto_literal=Verbatim(
        texto="Table 3.4.1-1—Load Combinations and Load Factors",
        pagina_pdf=71),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    corresponde_en=("MP.T2.4.5.3.1-1",),
    nota=("NOR-AAS-03, resuelto a favor del codigo vigente: la ficha "
          "reprochaba «pag. 3-14» y el repositorio ya decia 3-17, que es lo "
          "correcto segun la fuente."),
)

AASHTO_T3_4_1_2 = _cita(
    id="AASHTO_LRFD_9.T3.4.1-2",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 3.4.1-2",
    titulo_numeral="Load Factors for Permanent Loads",
    pagina_impresa="3-18",
    pagina_pdf=72,
    texto_literal=Verbatim(
        texto="Load Factors for Permanent Loads",
        pagina_pdf=72),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("MP.T2.4.5.3.1-2",),
    nota=("Confirma dos hallazgos abiertos: EV «Retaining Walls and "
          "Abutments» = 1.35 / 1.00 (no 0.90; sostiene NOR-PUE-03) y EH "
          "At-Rest = 1.35 / 0.90, CON minimo declarado -- lo que refuta la "
          "afirmacion negativa de NOR-AAS-04, que sostenia que la fuente no "
          "declara minimo para EH en reposo. El N/A pertenece a la fila "
          "siguiente, «AEP for anchored walls»."),
)

AASHTO_5_10_1 = _cita(
    id="AASHTO_LRFD_9.5.10.1",
    fuente_id="AASHTO_LRFD_9",
    numeral="5.10.1",
    titulo_numeral="Concrete Cover",
    pagina_impresa="5-167",
    pagina_pdf=526,
    texto_literal=Verbatim(
        texto=("Cover for prestressing and reinforcing steel shall not be "
               "less than that specified in Table 5.10.1-1 and modified for "
               "W/CM ratio."),
        pagina_pdf=526),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("El factor por relacion agua-cemento NO es opcional: la norma dice "
          "`shall`, y esta en el CUERPO ARTICULADO (columna izquierda), no en "
          "el comentario. Sostiene NOR-AAS-05."),
)

AASHTO_5_10_1_ESTRIBOS = _cita(
    id="AASHTO_LRFD_9.5.10.1#ESTRIBOS",
    fuente_id="AASHTO_LRFD_9",
    numeral="5.10.1",
    titulo_numeral="Concrete Cover",
    pagina_impresa="5-168",
    pagina_pdf=527,
    pagina_pdf_titulo=526,
    texto_literal=Verbatim(
        texto=("Cover to ties and stirrups may be 0.5 in. less than the "
               "values specified in Table 5.10.1-1 for main bars but shall "
               "not be less than 1.0 in. except for precast soffit form "
               "panels noted in the table below."),
        pagina_pdf=527),
    caracter=Caracter.PERMISO,
    metodo=AMBOS,
    nota=("EL TERCER TEXTO QUE CONDICIONA LA TABLA 5.10.1-1, y el ultimo: la "
          "cadena «Table 5.10.1-1» aparece en TRES paginas de toda la "
          "especificacion -- 5-167, 5-168 y 5-169 -- y en ninguna mas, de "
          "modo que la lista de condicionantes esta cerrada, no muestreada. "
          "ESTE PROYECTO NO LO CONSUME: dimensiona barras PRINCIPALES, y la "
          "regla es de estribos y zunchos. Se registra porque «tabla "
          "transcrita completa» incluye lo que la condiciona, y porque su "
          "forma -- restar 0.5 in con piso de 1.0 in -- NO es un "
          "`Modificador` del registro, que es multiplicativo: meterla ahi "
          "seria una lectura falsa del tipo, que es justo lo que el esquema "
          "existe para impedir."),
)

AASHTO_5_10_1_PISO = _cita(
    id="AASHTO_LRFD_9.5.10.1#PISO",
    fuente_id="AASHTO_LRFD_9",
    numeral="5.10.1",
    titulo_numeral="Concrete Cover",
    pagina_impresa="5-168",
    pagina_pdf=527,
    pagina_pdf_titulo=526,
    texto_literal=Verbatim(
        texto="Minimum cover to main bars shall be 1.0 in.",
        pagina_pdf=527),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    corresponde_en=("MP.T2.9.1.5.5.3-1",),
    nota=("El piso absoluto sobre las barras principales, que es lo que "
          "impide que el factor de 0.8 del W/CM lleve el recubrimiento a "
          "cualquier cosa. El Manual de Puentes lo traduce como «1.0 in "
          "(25 mm)» y el proyecto aplica la PULGADA EXACTA (25.4 mm), que es "
          "la mayor de las dos cifras que la propia fuente peruana escribe."),
)

AASHTO_T5_10_1_1 = _cita(
    id="AASHTO_LRFD_9.T5.10.1-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 5.10.1-1",
    titulo_numeral="Minimum Cover for Main Reinforcing Steel (in.)",
    pagina_impresa="5-169",
    pagina_pdf=528,
    texto_literal=Verbatim(
        texto="Minimum Cover for Main Reinforcing Steel",
        pagina_pdf=528),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    corresponde_en=("MP.T2.9.1.5.5.3-1",),
    nota=("TRES categorias de acero -- A, B y C --, bajo el encabezado de "
          "grupo «Reinforcing Material Category», y la tabla peruana tiene "
          "UNA sola columna porque cubre una sola categoria: la no protegida. "
          "Es la clave de NOR-AAS-01: los 3.0 in de «Coastal» son de la "
          "Categoria A, y con B o C la tabla baja a 2.0 in = 50.8 mm, con lo "
          "que la regla del mayor la pasaria a ganar E.060."),
)

# EL GEMELO DE 2.4.3.8.2, y se transcribe para que la correspondencia sea
# comprobable y no una afirmacion: el Manual de Puentes traduce este articulo
# casi palabra por palabra. La Sec. 0.2 adopta AASHTO LRFD de extremo a
# extremo, de modo que tener las dos permite ver que el corpus peruano y el
# adoptado dicen lo mismo aqui -- que es justo lo que el proyecto necesita
# poder ensenar cuando aplica una a un caso que la otra no cubre.
AASHTO_3_7_2 = _cita(
    id="AASHTO_LRFD_9.3.7.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.7.2",
    titulo_numeral="Buoyancy",
    pagina_impresa="3-45",
    pagina_pdf=99,
    texto_literal=Verbatim(
        texto=("Buoyancy shall be considered to be an uplift force, taken as "
               "the sum of the vertical components of static pressures, as "
               "specified in Article 3.7.1, acting on all components below "
               "design water level."),
        pagina_pdf=99),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("MP.2.4.3.8.2",),
    nota=("«all components below design water level»: el mismo ambito neutro "
          "que el numeral peruano. Es DEFINITORIA de la fuerza; quien pone la "
          "condicion de disparo para una estructura enterrada es el 12.6.1, "
          "que remite aqui expresamente."),
)


# LAS DOS EXIGENCIAS DE FLOTACION DE LA SEC. 12, que V7 no citaba. Hasta C7
# el unico respaldo de V7 en el registro eran las dos TABLAS de factores del
# Manual de Puentes, que dan gamma y no obligan a verificar nada. Estas dos si
# obligan, con `shall`, y su ambito -- «buried structures» -- alcanza al cajon
# de concreto por el 12.1 SCOPE, que lo nombra: «reinforced concrete
# cast-in-place and precast arch, box and elliptical structures».
AASHTO_12_6_1 = _cita(
    id="AASHTO_LRFD_9.12.6.1#FLOTACION",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.6.1",
    titulo_numeral="Loading",
    pagina_impresa="12-14",
    pagina_pdf=1652,
    texto_literal=Verbatim(
        texto=("Water buoyancy loads shall be evaluated for buried "
               "structures with inverts below the water table to control "
               "flotation, as indicated in Article 3.7.2."),
        pagina_pdf=1652),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("MP.2.4.3.8.2",),
    nota=("ES LA UNICA APARICION DE «flotation» EN LAS 1905 PAGINAS del PDF, "
          "medida. Y trae su propia CONDICION DE DISPARO -- «with inverts "
          "below the water table» --, que es la que hace de esta verificacion "
          "algo que no siempre aplica: sin freatico sobre el invert no hay "
          "nada que evaluar. "
          "NO SE LEE SOLA: dos frases mas abajo, EN EL MISMO PARRAFO de este "
          "mismo numeral, esta `AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX`, que manda "
          "aplicar el factor MAXIMO de EV -- lo contrario de lo que V7 hace --. "
          "C7 cito esta frase y elidio aquella, y lo encontro su auditoria "
          "adversarial: recortar un parrafo justo antes de la frase que "
          "discute tu propia lectura es la forma NOR-HID-01 aplicada a un "
          "recorte. La discusion esta registrada en DIS-AASHTO-GAMMA-EV-12.6.1."),
)

# LA FRASE QUE C7 ELIDIO, Y VA COMO CITA PROPIA PARA QUE NADIE PUEDA VOLVER A
# CITAR EL PARRAFO SIN ELLA. Es del mismo numeral y del mismo parrafo que la
# de arriba, dos frases despues, y apunta en direccion CONTRARIA a la lectura
# que V7 aplica: V7 minora EV (gamma = 0.90, amparado en MP.2.4.5.3.1#MINIMO)
# y esto manda mayorarla. Las dos son `shall`. Que la discusion exista es un
# hecho de la fuente; como se resuelve es del proyecto, y por eso lo resuelve
# una `Discrepancia` declarada y no un silencio.
AASHTO_12_6_1_GAMMA_EV = _cita(
    id="AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.6.1",
    titulo_numeral="Loading",
    pagina_impresa="12-14",
    pagina_pdf=1652,
    texto_literal=Verbatim(
        texto=("For vertical earth pressure, the maximum load factor from "
               "Table 3.4.1-2 shall apply."),
        pagina_pdf=1652),
    caracter=Caracter.EXIGENCIA,
    nota=("PARRAFO PROPIO dentro del num. 12.6.1, inmediatamente despues de "
          "la frase de flotacion y antes de la de reparto de carga de rueda. "
          "ES `lex specialis` PARA ESTRUCTURAS ENTERRADAS y dice MAXIMO, "
          "mientras el Art. 3.4.1 -- que el Manual de Puentes traduce en "
          "2.4.5.3.1 -- manda investigar el MINIMO cuando la carga permanente "
          "aumenta la estabilidad. Los dos son `shall`. "
          "QUE NO SE DEDUZCA DE AQUI: que V7 este mal. Aplicar el maximo a EV "
          "en una verificacion de FLOTACION haria la comprobacion MAS FACIL, "
          "no mas exigente, porque ahi EV estabiliza -- medido sobre la "
          "corrida del entregable de C7: el lado estabilizante pasaria de "
          "23.256 a 34.884 kN/m contra los mismos 20.405 de subpresion, y el "
          "margen se multiplicaria por cinco --. Esa es justamente la razon "
          "de que el proyecto lea esta frase como referida al diseno POR "
          "empuje de tierra y no al equilibrio de flotacion. Pero es una "
          "LECTURA: el texto no trae esa salvedad, y por eso vive en "
          "DIS-AASHTO-GAMMA-EV-12.6.1 y no en un comentario."),
)

AASHTO_12_6_2_3 = _cita(
    id="AASHTO_LRFD_9.12.6.2.3#UPLIFT",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.6.2.3",
    titulo_numeral="Uplift",
    pagina_impresa="12-19",
    pagina_pdf=1657,
    texto_literal=Verbatim(
        texto=("Uplift shall be considered where structures are installed "
               "below the highest anticipated groundwater level."),
        pagina_pdf=1657),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("MP.2.4.3.8.2",),
    nota=("SEGUNDA exigencia, acumulativa con la del 12.6.1 y no redundante: "
          "aquella manda EVALUAR la carga de flotacion y esta manda "
          "CONSIDERAR el levantamiento. Su condicion de disparo es el nivel "
          "freatico MAS ALTO previsto, que es la hipotesis que V7 adopta."),
)

# EL COMENTARIO QUE DA LA FORMA DE LA COMPARACION, y hay que leerlo con su
# caracter puesto: es un COMENTARIO y dice `should`. Es lo mas cercano que
# existe -- en cualquiera de las dos fuentes -- a la desigualdad que V7
# evalua, y aun asi NO la escribe: no menciona factores concretos ni
# extremos. Por eso la inecuacion del proyecto es ENSAMBLAJE y se imprime
# como `Interpretacion`, no como cita (NOR-HID-04).
AASHTO_C12_6_2_3 = _cita(
    id="AASHTO_LRFD_9.C12.6.2.3",
    fuente_id="AASHTO_LRFD_9",
    numeral="C12.6.2.3",
    titulo_numeral="Uplift",
    pagina_impresa="12-19",
    pagina_pdf=1657,
    texto_literal=Verbatim(
        texto=("To satisfy this provision, the dead load on the crown of the "
               "structure should exceed the buoyancy of the culvert, using "
               "load factors as appropriate."),
        pagina_pdf=1657),
    caracter=Caracter.RECOMENDACION,
    nota=("DICE «the culvert», NO «pipe», y eso importa: es de las pocas "
          "frases de la Sec. 12 sobre flotacion que no se restringe a "
          "tuberia. Pero es comentario y dice `should`: sostiene la FORMA de "
          "la comparacion -- peso de la clave contra empuje -- y no el "
          "criterio de aceptacion. Un factor de seguridad numerico NO sale de "
          "aqui, y atribuirselo seria inventarle una exigencia."),
)


AASHTO_12_6_6_3 = _cita(
    id="AASHTO_LRFD_9.12.6.6.3#COBERTURA",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.6.6.3",
    titulo_numeral="Minimum Cover",
    pagina_impresa="12-21",
    pagina_pdf=1659,
    texto_literal=Verbatim(
        texto=("The minimum cover, including a well-compacted granular "
               "subbase and base course, shall not be less than that "
               "specified in Table 12.6.6.3-1"),
        pagina_pdf=1659),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    nota=("El ARTICULO abre en la pag. impresa 12-21; solo la TABLA esta en "
          "la 12-22. Y una correccion contra la ficha de auditoria, no contra "
          "el repositorio: NOR-VAC-01 transcribe la fila de Reinforced "
          "Concrete Pipe como «raiz(Bc)/8» y el PDF imprime «B'c/8», con Bc' "
          "definido en 12-21 como «out-to-out vertical rise of pipe». Es una "
          "PRIMA, no un radical: artefacto de la linearizacion de la capa de "
          "texto. Corregir en la ficha antes de derivar cualquier numero."),
)

AASHTO_T12_6_6_3_1 = _cita(
    id="AASHTO_LRFD_9.T12.6.6.3-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 12.6.6.3-1",
    titulo_numeral="Minimum Cover",
    pagina_impresa="12-22",
    pagina_pdf=1660,
    pagina_pdf_titulo=1660,
    jerarquia_numeral=("12.6.6.3", "Minimum Cover"),
    texto_literal=Verbatim(
        texto="Table 12.6.6.3-1—Minimum Cover",
        pagina_pdf=1660),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    nota=("LA TABLA VIVE UNA PAGINA DESPUES QUE SU NUMERAL, y por eso lleva "
          "cita propia: el articulado 12.6.6.3 abre en la 12-21 (PDF 1659) y "
          "la tabla entera esta en la 12-22 (PDF 1660). Citarlas con la misma "
          "pagina manda al revisor a la pagina donde la tabla no esta. "
          "SUS COLUMNAS NO SON LAS QUE EL EXPEDIENTE SUPONIA: son «Type», "
          "«Condition» y «Minimum Cover*», TRES, y las condiciones de "
          "pavimento son VALORES de la segunda columna que solo aparecen en "
          "2 de los 13 tipos. No es una matriz tipo x condicion de pavimento. "
          "El repositorio ya la leia asi -- repite la misma fila en las tres "
          "condiciones para el metal corrugado, en vez de inventarle dos que "
          "la tabla no trae --, y esta verificacion lo confirma."),
)

AASHTO_3_10_2_2 = _cita(
    id="AASHTO_LRFD_9.3.10.2.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.10.2.2",
    titulo_numeral="Site-Specific Procedure",
    pagina_impresa="3-100",
    pagina_pdf=154,
    texto_literal=Verbatim(
        texto=("For sites located within 6 miles of an active surface or a "
               "shallow fault, as depicted in the USGS Active Fault Map, "
               "studies shall be considered to quantify near-fault effects"),
        pagina_pdf=154),
    caracter=Caracter.EXIGENCIA,
    nota=("«6 miles» esta literal; cualquier conversion a km (9.66) es del "
          "proyecto. Y `shall be CONSIDERED`: obliga a considerar el estudio, "
          "no a hacerlo. La remision al USGS Active Fault Map tambien es "
          "literal, y es el punto: ese mapa no cubre el Peru."),
)

AASHTO_3_11_3 = _cita(
    id="AASHTO_LRFD_9.3.11.3",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.11.3",
    titulo_numeral="Presence of Water",
    pagina_impresa="3-118",
    pagina_pdf=172,
    texto_literal=Verbatim(
        texto=("Submerged unit weights of the soil shall be used to determine "
               "the lateral earth pressure below the groundwater table."),
        pagina_pdf=172),
    caracter=Caracter.EXIGENCIA,
)

AASHTO_11_6_5_1 = _cita(
    id="AASHTO_LRFD_9.11.6.5.1#EXC",
    fuente_id="AASHTO_LRFD_9",
    numeral="11.6.5.1",
    titulo_numeral="General",
    pagina_impresa="11-25",
    pagina_pdf=1494,
    texto_literal=Verbatim(
        texto=("For seismic eccentricity evaluation of walls with foundations "
               "on soil and rock, the location of the resultant of the "
               "reaction forces shall be within the middle two-thirds of the "
               "base for"),
        pagina_pdf=1494),
    caracter=Caracter.EXIGENCIA,
    nota=("«middle two-thirds», no «tercio central»: es la parte de AASHTO "
          "que gana a la errata de traduccion del Manual. Y su comentario "
          "C11.6.5.1 ARRANCA en esta misma pagina (columna derecha), no en la "
          "11-26; lo que si esta en la 11-26 es el texto que el repositorio "
          "le atribuye."),
)

AASHTO_11_6_5_2_1 = _cita(
    id="AASHTO_LRFD_9.11.6.5.2.1#ROCA",
    fuente_id="AASHTO_LRFD_9",
    numeral="11.6.5.2.1",
    titulo_numeral="Characterization of Acceleration at Wall Base",
    pagina_impresa="11-27",
    pagina_pdf=1496,
    texto_literal=Verbatim(
        texto=("For walls founded on Site Class A or B soil (hard or soft "
               "rock), kh0 shall be based on 1.2 times the site-adjusted peak "
               "ground acceleration coefficient (i.e., kh0 = 1.2FpgaPGA)."),
        pagina_pdf=1496),
    caracter=Caracter.EXIGENCIA,
    nota=("El 1.2 esta literal, y del lado correcto de la igualdad: es lo que "
          "resuelve la errata de imprenta del Manual, cuyo parentesis lo pone "
          "a la izquierda."),
)

AASHTO_A11_3_1 = _cita(
    id="AASHTO_LRFD_9.A11.3.1#KAE",
    fuente_id="AASHTO_LRFD_9",
    numeral="A11.3.1, ec. A11.3.1-1",
    titulo_numeral="Mononobe–Okabe Method",
    pagina_impresa="11-145",
    pagina_pdf=1614,
    pagina_pdf_titulo=1613,
    texto_literal=Verbatim(
        texto="seismic active earth pressure coefficient",
        pagina_pdf=1614),
    caracter=Caracter.APROXIMACION,
    metodo=IMAGEN,
    nota=("El ENCABEZADO del articulo se imprime en la pag. impresa 11-144 "
          "(PDF 1613) y la ECUACION en la 11-145 (PDF 1614). La forma exacta "
          "del corchete -- «[1 + raiz(...)]» -- NO ES VERIFICABLE por "
          "extraccion de texto: la capa devuelve la formula rota. Se decide "
          "sobre la imagen renderizada, y por eso el metodo es IMAGEN. Las "
          "unidades de la fuente son imperiales (kcf, ft)."),
)

# ===========================================================================
# T2 -- las contrapartes que las discrepancias anunciaban y nadie transcribio
# ===========================================================================
# Censo de T2 (entonces 23 discrepancias): 52 partes y 38 anunciando una
# cita; NUEVE de esos
# ids no existian en el registro (`partes_sin_cita_transcrita`, hallazgo de
# C8). Este bloque transcribe las que el Manual de Puentes y AASHTO
# sostienen, verificadas por el subagente en la sesion T2. Cada una es la
# EVIDENCIA de una parte: donde la parte dice «el Manual imprime X», la cita
# lleva el X impreso, con su errata si la tiene.

AASHTO_11_6_3_3 = _cita(
    id="AASHTO_LRFD_9.11.6.3.3#EXC",
    fuente_id="AASHTO_LRFD_9",
    numeral="11.6.3.3",
    titulo_numeral="Eccentricity Limits",
    pagina_impresa="11-24",
    pagina_pdf=1493,
    texto_literal=Verbatim(
        texto=("For foundations on soil, the location of the resultant of "
               "the reaction forces shall be within the middle two-thirds of "
               "the base width."),
        pagina_pdf=1493),
    caracter=Caracter.EXIGENCIA,
    sesion=T2,
    corresponde_en=("MP.2.3.1.1.12.3#EXC_ESTATICA",),
    nota=("Es el numeral al que la remision impresa del Manual -- "
          "«(11.6.3.3 AASHTO)», bajo su encabezado errado 2.3.1.1.12.3 -- "
          "llega: existe, se titula «Eccentricity Limits» y su cuerpo "
          "articulado (columna izquierda; el C11.6.3.3 va aparte) impone el "
          "mismo limite estatico. La remision es correcta aunque el numeral "
          "peruano este mal impreso, que es lo que DIS-MP-NUMERAL-"
          "2.3.1.1.12.3 declara. Para roca, la frase hermana dice «middle "
          "nine-tenths». En el flujo del PDF «two-thirds» va partido con "
          "guion a fin de renglon; la busqueda normalizada lo reconstruye."),
)

MP_2_3_1_1_12_3_EXC_ESTATICA = _cita(
    id="MP.2.3.1.1.12.3#EXC_ESTATICA",
    fuente_id="MP",
    numeral="2.3.1.1.12.3",
    titulo_numeral="Límites de Excentricidad",
    pagina_impresa="250",
    pagina_pdf=251,
    texto_literal=Verbatim(
        texto=("En las fundaciones en suelo la ubicación de la resultante de "
               "las fuerzas de reacción deberá estar dentro los dos tercios "
               "centrales del ancho de la base."),
        pagina_pdf=251),
    caracter=Caracter.EXIGENCIA,
    sesion=T2,
    corresponde_en=("AASHTO_LRFD_9.11.6.3.3#EXC",),
    nota=("EL NUMERAL SE CITA COMO LO IMPRIME, CON SU ERRATA: un 3 donde la "
          "serie pide un 8. En la misma pagina impresa 250 conviven "
          "«2.3.1.1.12.3 Límites de Excentricidad» y «2.3.1.1.12.4 Erosión "
          "Subsuperficial» (la errata alcanza a los dos sufijos) con "
          "«2.8.1.1.12.5 Resistencia Pasiva» y «2.8.1.1.12.6 Deslizamiento», "
          "ya en la serie correcta; el indice (PDF 21) repite las dos "
          "erratas. Ver DIS-MP-NUMERAL-2.3.1.1.12.3. La frase transcrita es "
          "ademas la traduccion CORRECTA de «middle two-thirds» en el "
          "numeral ESTATICO -- el hecho que sostiene el por_que de "
          "DIS-MP-EXCENTRICIDAD: el Manual sabe traducir el giro y solo lo "
          "degrada en el numeral sismico --. El «dentro los» sin «de» es de "
          "la fuente. Dos parrafos mas abajo la misma pagina dice «dentro "
          "del medio central del ancho de la base» para el mismo caso de "
          "suelo: tension interna de la fuente, que se deja anotada y no se "
          "resuelve aqui."),
)

MP_2_8_1_1_14_1_EXC = _cita(
    id="MP.2.8.1.1.14.1#EXC",
    fuente_id="MP",
    numeral="2.8.1.1.14.1",
    titulo_numeral="Generalidades",
    pagina_impresa="253",
    pagina_pdf=254,
    pagina_pdf_titulo=253,
    texto_literal=Verbatim(
        texto=("Para la evaluación de la excentricidad sísmica de los muros "
               "que cimentan en suelo y roca, la ubicación de la resultante "
               "de las fuerzas de reacción estará dentro del tercio central "
               "de la base para ɤEQ = 0.0 y dentro de ocho décimas centrales "
               "para ɤEQ = 1.0."),
        pagina_pdf=254),
    caracter=Caracter.EXIGENCIA,
    sesion=T2,
    corresponde_en=("AASHTO_LRFD_9.11.6.5.1#EXC",),
    nota=("«tercio central» donde AASHTO 11.6.5.1 escribe «middle "
          "two-thirds»: es la frase que DIS-MP-EXCENTRICIDAD declara errata "
          "de traduccion -- el mismo parrafo traduce bien «ocho décimas» "
          "(eight-tenths), y el numeral estatico de tres paginas antes "
          "traduce bien los dos tercios --. El encabezado «2.8.1.1.14.1  "
          "Generalidades (11.6.5.1 AASHTO)» se imprime al pie de la pag. "
          "impresa 252 (PDF 253) y la frase esta en la 253 (PDF 254)."),
)

MP_2_8_1_1_14_2_1_ROCA = _cita(
    id="MP.2.8.1.1.14.2.1#ROCA",
    fuente_id="MP",
    numeral="2.8.1.1.14.2.1",
    titulo_numeral=("Caracterización de la Aceleración en la Base del Muro "
                    "de Contención"),
    pagina_impresa="254",
    pagina_pdf=255,
    texto_literal=Verbatim(
        texto=("Para muros cimentados sobre Sitio con suelos Clase A o B "
               "(roca dura o blanda), kh0 estará basado en 1.2 veces el "
               "coeficiente de aceleración pico del suelo (es decir, 1.2 "
               "kh0=FpgaPGA)."),
        pagina_pdf=255),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=T2,
    corresponde_en=("AASHTO_LRFD_9.11.6.5.2.1#ROCA",),
    nota=("LA FRASE CONTIENE LAS DOS MITADES DE DIS-MP-KH0-ROCA: la prosa "
          "correcta («estará basado en 1.2 veces el coeficiente...») y el "
          "parentesis mal compuesto, con el 1.2 del lado IZQUIERDO de la "
          "igualdad -- confirmado sobre la imagen renderizada, por eso el "
          "metodo es AMBOS; en el impreso el «=» va compuesto a nivel de "
          "subindice y hay salto de linea entre «1.2» y «kh0»; la "
          "transcripcion lineal es fiel --. El rotulo de remision debajo "
          "del titulo imprime «(11.6.5.2.1AASHTO)» sin espacio. Que el lado "
          "correcto sea k_h0 = 1.2·F_pga·PGA lo dice AASHTO 11.6.5.2.1, no "
          "este parentesis: por eso gana la prosa (ver la discrepancia)."),
)

MP_A_11_3_1_KAE = _cita(
    id="MP.A.11.3.1#KAE",
    fuente_id="MP",
    numeral="A.11.3.1, ec. A.11.3.1-2",
    titulo_numeral="Método de Mononobe -Okabe",
    pagina_impresa="586",
    pagina_pdf=587,
    texto_literal=Verbatim(
        texto=("Donde el coeficiente sísmico KAE de presión de tierra "
               "activa, adimensional, es:"),
        pagina_pdf=587),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T2,
    corresponde_en=("AASHTO_LRFD_9.A11.3.1#KAE",),
    nota=("EL CORCHETE DEL DENOMINADOR IMPRIME «[1 −√ ...]^-2», SIGNO "
          "MENOS: trazo horizontal unico, sin trazo vertical, decidido "
          "sobre la imagen renderizada a 6x -- es la errata de imprenta que "
          "DIS-MP-KAE-SIGNO declara; AASHTO imprime «[1 + raiz(...)]» y "
          "gana --. La etiqueta impresa de la ecuacion es «Donde "
          "(A.11.3.1-2. AASHTO)», con punto tras el 2. El espaciado del "
          "titulo, «Mononobe -Okabe» (espacio antes del guion, ninguno "
          "despues), es de la fuente y se conserva. Unidades imperiales "
          "(kcf, ft), como en el apendice AASHTO del que se transcribe."),
)


AASHTO_C3_4_1 = _cita(
    id="AASHTO_LRFD_9.C3.4.1#GAMMA_EQ",
    fuente_id="AASHTO_LRFD_9",
    numeral="C3.4.1",
    titulo_numeral="3.4.1-Load Factors and Load Combinations",
    pagina_impresa="3-10",
    pagina_pdf=64,
    # El encabezado del articulo se imprime en la pag. impresa 3-9; el
    # comentario que esta cita transcribe, en la 3-10.
    pagina_pdf_titulo=63,
    texto_literal=Verbatim(
        texto=("Application of Turkstra's rule for combining uncorrelated "
               "loads indicates that"),
        pagina_pdf=64),
    caracter=Caracter.RECOMENDACION,
    metodo=AMBOS,
    nota=("EL 0.50 ESTA LITERAL EN LA FUENTE, pero como COMENTARIO y con el "
          "calificador «is reasonable»: no es una exigencia ni una de dos "
          "opciones tabuladas. Y el 0.0 aparece solo como referencia a "
          "ediciones pasadas del Standard Specifications, seguido de «This "
          "issue is not resolved». Quien lo determina es el PROYECTO "
          "(«project-specific basis», Art. 3.4.1, pag. impresa 3-19), no «el "
          "propietario»."),
)


# ===========================================================================
# Manual de Puentes -- el resto de la cadena
# ===========================================================================

# EL NUMERAL QUE OBLIGA, que el codigo llevaba doce veces como CADENA y cero
# como cita. `M8.NUMERAL_V7`, `M5.NUMERAL_V7`, el docstring de
# `empuje_flotacion_kn_m`, `M9.NUMERAL_SUBPRESION` y `criterios_adoptados` lo
# nombran; ningun test lo habia contrastado nunca contra su pagina. Se
# transcribe en C7 y dice lo que se le atribuia -- que es el resultado bueno,
# porque el malo habria sido descubrir que no.
MP_SUBPRESIONES = _cita(
    id="MP.2.4.3.8.2",
    fuente_id="MP",
    numeral="2.4.3.8.2",
    titulo_numeral="Subpresiones",
    pagina_impresa="113",
    pagina_pdf=114,
    texto_literal=Verbatim(
        texto=("La subpresión (flotabilidad) se deberá considerar como una "
               "fuerza de levantamiento, tomada como la sumatoria de las "
               "componentes verticales de las presiones hidrostáticas, según "
               "lo especificado en el Artículo 2.4.3.8.1 (3.7.1 AASHTO) que "
               "actúa sobre todos los componentes de la estructura que se "
               "encuentran debajo del nivel de agua de diseño."),
        pagina_pdf=114),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("AASHTO_LRFD_9.3.7.2",),
    nota=("SU AMBITO ES NEUTRO RESPECTO DE LA FORMA y por eso el marco entra "
          "DIRECTO, sin analogia que declarar: dice «todos los componentes de "
          "la estructura», no «la tuberia». DEFINE LA FUERZA U y nada mas: no "
          "fija estado limite, ni combinacion, ni criterio de aceptacion. La "
          "desigualdad que V7 evalua NO sale de aqui -- ver el `por_que` de "
          "F5.V7 --. El «2.4.3.8.1» al que remite es el empuje hidrostatico "
          "general, del que esta es la componente vertical."),
)

MP_FACTOR_MINIMO = _cita(
    id="MP.2.4.5.3.1#MINIMO",
    fuente_id="MP",
    numeral="2.4.5.3.1",
    titulo_numeral="Factores de Carga y Combinaciones de Carga",
    pagina_impresa="142",
    pagina_pdf=143,
    pagina_pdf_titulo=141,
    texto_literal=Verbatim(
        texto=("Si la carga permanente aumenta la estabilidad o la capacidad "
               "de carga de un componente o puente, también se deberá "
               "investigar el valor mínimo del factor de carga para dicha "
               "carga permanente."),
        pagina_pdf=143),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("AASHTO_LRFD_9.T3.4.1-2",),
    nota=("ES EL ESLABON QUE FALTABA, y faltaba entero: es lo que AUTORIZA a "
          "V7 a minorar EV y DC. Sin esta frase, tomar el extremo minimo de "
          "la fila de gamma_p seria una eleccion del proyectista sin "
          "respaldo; con ella es lo que la fuente manda hacer cuando la carga "
          "permanente ESTABILIZA, que es exactamente el caso de la flotacion. "
          "El titulo del numeral se imprime en la pag. impresa 140 (PDF 141) "
          "y el texto en la 142 (PDF 143): por eso `pagina_pdf_titulo`."),
)

MP_EV = _cita(
    id="MP.2.4.5.2#EV",
    fuente_id="MP",
    numeral="2.4.5.2",
    titulo_numeral="Cargas y Denominación de las Cargas",
    pagina_impresa="140",
    pagina_pdf=141,
    pagina_pdf_titulo=140,
    texto_literal=Verbatim(
        texto="presión vertical del peso propio del suelo de relleno",
        pagina_pdf=141),
    caracter=Caracter.DEFINICION,
    nota=("LO QUE LA DEFINICION NO DICE, y hay que decirlo porque el proyecto "
          "lo da por supuesto: no aparecen las palabras «sobre», «encima» ni "
          "«cobertura». Que EV sea el relleno que descansa SOBRE la "
          "estructura es una lectura -- razonable y estandar, y sostenida por "
          "la fila «enterrada» que se elige, no por esta frase --. Se "
          "transcribe el predicado y no la linea entera («EV = presion...») "
          "porque la tabla de simbolos separa el simbolo del texto y el "
          "volcado los reordena."),
)


MP_T_COMBINACIONES = _cita(
    id="MP.T2.4.5.3.1-1",
    fuente_id="MP",
    numeral="2.4.5.3.1, Tabla 2.4.5.3.1-1",
    titulo_numeral="Factores de Carga y Combinaciones",
    pagina_impresa="143",
    pagina_pdf=144,
    pagina_pdf_titulo=141,
    texto_literal=Verbatim(
        texto="Combinaciones de Carga y Factores de Carga",
        pagina_pdf=144),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("AASHTO_LRFD_9.T3.4.1-1",),
    nota=("EL PROPIO MANUAL LA NOMBRA DE DOS FORMAS INCOMPATIBLES: el rotulo "
          "impreso sobre la tabla dice «Tabla 2.4.5.3.1-1» y el cuerpo del "
          "texto, en la pag. impresa 142, la llama «Tabla 2.4.5.3-1», sin el "
          "«.1». Se cita la forma del ROTULO, que es la que un revisor lee "
          "sobre la tabla que tiene delante."),
)

MP_T_GAMMA_P = _cita(
    id="MP.T2.4.5.3.1-2",
    fuente_id="MP",
    numeral="2.4.5.3.1, Tabla 2.4.5.3.1-2",
    titulo_numeral="Factores de Carga y Combinaciones",
    pagina_impresa="143",
    pagina_pdf=144,
    pagina_pdf_titulo=141,
    texto_literal=Verbatim(
        texto="Factores de carga para cargas permanentes",
        pagina_pdf=144),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("AASHTO_LRFD_9.T3.4.1-2",),
    nota=("NOR-PUE-04: el repositorio afirmaba que el Manual «no transcribe "
          "la Tabla 3.4.1-1» y que los gamma eran un vacio declarado. Las dos "
          "afirmaciones eran falsas -- el Manual transcribe LAS DOS tablas, "
          "completas y con sus valores, dentro del rango de paginas que el "
          "propio archivo citaba --, y declarar un vacio sobre la pagina que "
          "trae la tabla es el defecto que Sec. 0.5 llama el mas grave."),
)

MP_T_F_PGA = _cita(
    id="MP.T2.4.3.11.2.1.2-1",
    fuente_id="MP",
    numeral="Tabla 2.4.3.11.2.1.2-1",
    titulo_numeral="Efectos de Sitio",
    pagina_impresa="123",
    pagina_pdf=124,
    # El numeral 2.4.3.11.2.1 abre en la pag. impresa 122 y la tabla esta en
    # la 123.
    pagina_pdf_titulo=123,
    texto_literal=Verbatim(
        texto="Coeficiente Aceleracion Pico del Terreno",
        pagina_pdf=124),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    condiciones=(
        # La clase de sitio es la PREMISA ABIERTA del expediente, y por eso
        # bloquea: el salto «suelo licuable -> Clase F» no lo escribe ninguno
        # de los dos documentos que el criterio invoca. La discrepancia entre
        # el esquema de E.030 (perfil S5) y el de AASHTO / Manual de Puentes
        # (Clase F) esta declarada y NO se resuelve aqui: es S13.
        CondicionAplicacion(
            id="COND-CLASE-DE-SITIO",
            texto=Verbatim(texto="Clase de Sitio", pagina_pdf=124),
            cita_id="MP.T2.4.3.11.2.1.2-1",
            resuelve=PorCriterio(clave="clase_sitio")),
    ),
    nota=("TRES DE SUS RASGOS SOLO SE VEN RENDERIZANDO, y los tres deciden "
          "una lectura: el signo `>` de la ultima columna, el asterisco de "
          "la fila F y el «1» del encabezado superior, que es la llamada a la "
          "Nota 1 y no un exponente."),
)

# EL SILENCIO QUE SOSTIENE LA LECTURA DEL BORDE DE LA TABLA DE F_pga. No
# autoriza un [C] -- ninguna fuente externa entra --: fija el barrido que
# permite a 'F_pga_lectura_columna_extrema' seguir siendo eleccion [A] sobre
# un silencio real de la fuente y no sobre una impresion. R3 verifico la
# Nota 1 sobre la pagina renderizada preguntandole exactamente esto -- si los
# valores rotulados son los puntos entre los que se interpola y el borde
# exacto queda definido por la columna extrema -- y la respuesta es que la
# nota calla: la laguna que T_MP_F_PGA declara (NOR-PUE-11) es de la fuente,
# confirmada, no un fallo de lectura del registro.
SIN_REGLA_DE_BORDE_EN_TFPGA = AfirmacionNegativa(
    que_no_dice=(
        "el Manual no dice como se lee un PGA exactamente igual a un rotulo "
        "extremo de la Tabla 2.4.3.11.2.1.2-1 (0.10 o 0.50 exactos): su "
        "Nota 1 manda interpolar en linea recta para valores intermedios de "
        "PGA sin nombrar los puntos entre los que se interpola, sus dos "
        "rotulos extremos son desigualdades estrictas que no cubren su "
        "propio limite, y el articulado del num. 2.4.3.11.2.1.2 presenta "
        "las tablas sin regla de lectura de bordes. Tratar los cinco "
        "numeros de los rotulos como nodos de la interpolacion -- y en "
        "particular suponer que la columna extrema aplica en su propio "
        "limite -- es inferencia del lector, no texto de la fuente"),
    ambito_barrido=(
        "las paginas PDF 121 a 126 (impresas 120 a 125), las seis sobre "
        "pagina renderizada y la de la tabla ademas en recorte ampliado y "
        "en texto plano: numerales 2.4.3.10.3 a 2.4.3.11.5 completos, "
        "incluido el 2.4.3.11.2.1.2 «Factores de Sitio» con sus dos "
        "parrafos y sus tres tablas con sus notas. Nada en ese ambito trae "
        "regla de borde. El contraste que muestra que la desigualdad "
        "estricta es deliberada y no tipografia: la Tabla 2.4.3.11.5-1 "
        "(impresa 125, PDF 126) si imprime el signo de menor o igual "
        "cuando quiere decirlo. Fuera de esas paginas no se barrio"),
    cita_id="MP.T2.4.3.11.2.1.2-1")

MP_T_RECUBRIMIENTO = _cita(
    id="MP.T2.9.1.5.5.3-1",
    fuente_id="MP",
    numeral="2.9.1.5.5.3, Tabla 2.9.1.5.5.3-1",
    titulo_numeral="Recubrimiento de Concreto",
    pagina_impresa="377",
    pagina_pdf=378,
    texto_literal=Verbatim(
        texto="Recubrimiento de Concreto",
        pagina_pdf=378),
    caracter=Caracter.EXIGENCIA,
    corresponde_en=("AASHTO_LRFD_9.T5.10.1-1",),
    nota=("LO QUE EL TITULO DE LA TABLA DICE Y NADIE HABIA LEIDO -- y es la "
          "clave del cluster C07 --: «Recubrimiento para las armaduras "
          "principales de aceros NO PROTEGIDAS». La tabla peruana tiene UNA "
          "columna porque cubre UNA categoria de acero: la no protegida, que "
          "AASHTO llama Categoria A. El acero epoxico o galvanizado el Manual "
          "lo trata en un numeral aparte, el 2.9.1.5.5.4."),
)


# ===========================================================================
# CLASE DE SITIO  (S13 - conflicto #8: NOR-AAS-02, NOR-VOC-04, NOR-E030-02,
#                  NOR-MEM-03, SIS-B-01)
# ===========================================================================
# LAS DOCE CITAS SOBRE LAS QUE SE DECIDE LA PREMISA, y estan aqui y no en un
# comentario porque la pregunta que el expediente tenia abierta -- si el sitio
# «es Clase de Sitio F por licuefaccion» -- solo se contesta leyendo tres
# documentos a la vez. Ver docs/resolucion_clase_sitio.md.
#
# QUE SE COMPROBO, dicho corto, porque es lo que cambia la decision:
#
#   1. Ninguno de los dos documentos que el criterio 'clase_sitio' invoca
#      escribe el salto «suelo licuable -> Clase F». La palabra `liquef` no
#      aparece en la pagina de la Tabla 3.10.3.1-1 (PDF 156), y en las 1905
#      paginas de AASHTO los conjuntos {paginas con `liquef`} y {paginas con
#      «Site Class F»} son DISJUNTOS.
#   2. Pero la fila F se abre con «such as», que deja la lista ABIERTA: de la
#      ausencia NO se sigue la exclusion. La afirmacion defendible es la
#      negativa -- la norma no lo escribe --, no la contraria.
#   3. Y hay algo mas fuerte que el silencio, que es lo que cierra la
#      cuestion: las dos fuentes PROHIBEN SUPONER la clase F sin dato
#      geotecnico ni determinacion de la autoridad. No es que no autoricen el
#      salto: es que lo vedan expresamente.
#
# La Nota 2 de la tabla de factores, que es lo que el repositorio venia
# citando, dice «should»; el `shall` esta en el Art. 3.10.2. Se cita el
# fuerte.

# --------------------------- AASHTO LRFD 9a ed. ----------------------------

AASHTO_SITE_CLASS = _cita(
    id="AASHTO_LRFD_9.3.10.3.1",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.10.3.1",
    titulo_numeral="Site Class Definitions",
    pagina_impresa="3-101",
    pagina_pdf=155,
    texto_literal=Verbatim(
        texto=("Sites shall be classified by their stiffness as determined "
               "by the shear wave velocity in the upper 100 ft"),
        pagina_pdf=155),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    nota=("LA CLASE DE SITIO ES UNA MEDICION, y de ahi cuelga la etiqueta del "
          "criterio: se determina por la RIGIDEZ medida (v_s, N o s_u) sobre "
          "una profundidad fija, no por una eleccion del proyectista. "
          "PROFUNDIDAD: el articulado dice «the upper 100 ft» -- 30.48 m --, "
          "no «30 m»; ver DIS-HR-30M-VS-100FT. Y dos erratas de la fuente que "
          "se conservan en el verbatim de la primera oracion cuando se cite "
          "entera: «A though F» por «through», y la falta de punto tras "
          "«100 ft»."),
)

AASHTO_SITE_CLASS_EXCEPCIONES = _cita(
    id="AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.10.3.1, nota «Exceptions» al pie de la Tabla 3.10.3.1-1",
    titulo_numeral="Site Class Definitions",
    pagina_impresa="3-102",
    pagina_pdf=156,
    # El numeral abre en la 3-101 y la nota va al pie de la tabla, en la 3-102.
    pagina_pdf_titulo=155,
    texto_literal=Verbatim(
        texto=("Site classes E or F should not be assumed unless the "
               "authority having jurisdiction determines that site classes E "
               "or F could be present at the site or in the event that site "
               "classes E or F are established by geotechnical data."),
        pagina_pdf=156),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    corresponde_en=("MP.2.4.3.11.2.1.1#EXCEPCIONES",),
    nota=("LA CITA QUE CIERRA EL CONFLICTO #8, y estaba en el articulado sin "
          "que nadie la hubiera leido. El expediente no necesitaba una "
          "autorizacion para suponer la Clase F: tenia una PROHIBICION "
          "expresa de suponerla, con dos puertas de salida que no tiene "
          "abiertas -- determinacion de la autoridad competente, o dato "
          "geotecnico -- porque el SPT esta pendiente. "
          "Y la misma nota trae un DEBER POSITIVO que es la otra mitad: "
          "«Where the soil properties are not known in sufficient detail to "
          "determine the site class, a site investigation shall be undertaken "
          "sufficient to determine the site class». No dice «no supongas y "
          "sigue»: dice INVESTIGA. "
          "ES ARTICULADO, no comentario: va al pie de la Tabla 3.10.3.1-1, "
          "en la columna de especificacion. El `should not` de AASHTO lo "
          "endurece el Manual de Puentes a «no seran supuestas»."),
)

# El DEBER POSITIVO del mismo bloque «Exceptions», que hasta S14 vivia solo
# en la `nota` de la cita anterior y por eso la memoria no lo podia citar sin
# transcribirlo a mano por segunda vez. Es la otra mitad de la prohibicion y
# la que dice que hacer: la norma no dice «no supongas y sigue», dice
# INVESTIGA, y es lo que convierte a 'clase_sitio' en un [S] pendiente de
# ensayo y no en un vacio que se adopta.
AASHTO_SITE_CLASS_INVESTIGACION = _cita(
    id="AASHTO_LRFD_9.3.10.3.1#INVESTIGACION",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.10.3.1, nota «Exceptions» al pie de la Tabla 3.10.3.1-1",
    titulo_numeral="Site Class Definitions",
    pagina_impresa="3-102",
    pagina_pdf=156,
    pagina_pdf_titulo=155,
    texto_literal=Verbatim(
        texto=("Where the soil properties are not known in sufficient detail "
               "to determine the Site Class, a site investigation shall be "
               "undertaken sufficient to determine the Site Class."),
        pagina_pdf=156),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    nota=("Es la PRIMERA oracion del bloque «Exceptions» y precede a la "
          "prohibicion de suponer E o F: el orden de la fuente es investigar "
          "primero y no suponer despues. Se registra aparte porque es una "
          "exigencia distinta -- un deber de hacer, no una prohibicion -- y "
          "porque la memoria la cita por su cuenta al declarar que ensayo "
          "cierra el vacio."),
)

AASHTO_T_SITE_CLASS_F = _cita(
    id="AASHTO_LRFD_9.T3.10.3.1-1#F",
    fuente_id="AASHTO_LRFD_9",
    numeral="Tabla 3.10.3.1-1, fila F",
    titulo_numeral="Site Class Definitions",
    pagina_impresa="3-102",
    pagina_pdf=156,
    texto_literal=Verbatim(
        texto="Soils requiring site-specific evaluations, such as:",
        pagina_pdf=156),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=S13,
    corresponde_en=("MP.2.4.3.11.2.1.1",),
    nota=("LAS TRES CATEGORIAS Y EL «SUCH AS». La celda enumera turbas o "
          "arcillas altamente organicas (H > 10.0 ft), arcillas de muy alta "
          "plasticidad (H > 25.0 ft con PI > 75) y estratos potentes de "
          "arcilla blanda o semirrigida (H > 120 ft). NINGUNA es "
          "licuefaccion: la busqueda de `liquef` sobre la pagina PDF 156 "
          "entera da cero, y en las 1905 paginas del documento los conjuntos "
          "{paginas con `liquef`} y {paginas con «Site Class F»} son "
          "disjuntos. "
          "PERO el encabezado es «such as», lista abierta, de modo que lo que "
          "se sostiene es la afirmacion NEGATIVA -- la norma no escribe el "
          "salto -- y no la contraria. La tension con el «the three "
          "categories» del comentario esta declarada en "
          "DIS-AASHTO-F-LISTA-ABIERTA, y la decision no depende de como se "
          "resuelva: por las dos lecturas el salto sigue sin estar escrito. "
          "Verificada tambien por imagen: los tres bullets son glifos Symbol."),
)

AASHTO_C_PASOS_CLASE_SITIO = _cita(
    id="AASHTO_LRFD_9.C3.10.3.1-1#PASO1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Tabla C3.10.3.1-1, paso 1",
    titulo_numeral="Steps for Site Classification",
    pagina_impresa="3-103",
    pagina_pdf=157,
    texto_literal=Verbatim(
        texto=("Check for the three categories of Site Class F in Table "
               "3.10.3.1-1 requiring site-specific evaluation."),
        pagina_pdf=157),
    caracter=Caracter.RECOMENDACION,
    sesion=S13,
    nota=("ES COMENTARIO Y POR ESO NO ESTRECHA EL ARTICULADO -- lleva prefijo "
          "`C` y cuelga del epigrafe C3.10.3.1 --, pero importa por algo que "
          "el debate «lista abierta o cerrada» estaba tapando: el paso 1 no "
          "es retorico, es un PROCEDIMIENTO. Manda comprobar esas categorias "
          "y, si el sitio no cae en ninguna, seguir al paso 2 (capa blanda -> "
          "Clase E) y al paso 3 (calcular v_s, N o s_u sobre los 100 ft "
          "superiores -> Clase A a E). En ninguno de los tres pasos hay una "
          "ruta que lleve de «suelo licuable» a la Clase F. "
          "Refuta por su cuenta la version fuerte de NOR-AAS-02 que la "
          "refutacion adversarial R95-073 ya habia tumbado: el «the three "
          "categories» existe, pero esta aqui, no en el articulado."),
)

AASHTO_PELIGRO_SISMICO_CLASE_F = _cita(
    id="AASHTO_LRFD_9.3.10.2#CLASE_F",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.10.2",
    titulo_numeral="Seismic Hazard",
    pagina_impresa="3-71",
    pagina_pdf=125,
    texto_literal=Verbatim(
        texto=("A Site-Specific Procedure shall be used if any one of the "
               "following conditions exist:"),
        pagina_pdf=125),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    corresponde_en=("MP.2.4.3.11.2#CLASE_F",),
    nota=("AQUI ESTA EL `SHALL`, Y EL REPOSITORIO CITABA EL TEXTO MAS DEBIL "
          "DE LOS TRES. La segunda condicion de la lista es «The site is "
          "classified as Site Class F (Article 3.10.3.1),», y el verbo de la "
          "frase que la introduce es `shall`. La Nota 2 de las tablas de "
          "factores -- que es lo que Sec. 0.5 y el criterio venian citando -- "
          "dice `should`, y el Art. 3.10.2.2 (pag. impresa 3-100) repite el "
          "`shall`. La afirmacion del expediente («AASHTO exige de forma "
          "incondicional un estudio de respuesta de sitio para la Clase F») "
          "es CIERTA; lo que estaba mal era el anclaje, que se apoyaba en una "
          "recomendacion para sostener una exigencia. No es una discrepancia "
          "-- las fuentes no se contradicen --, es una cita corta."),
)

AASHTO_LICUEFACCION = _cita(
    id="AASHTO_LRFD_9.10.5.4.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="10.5.4.2",
    titulo_numeral="Liquefaction Design Requirements",
    pagina_impresa="10-34",
    pagina_pdf=1323,
    texto_literal=Verbatim(
        texto=("A liquefaction assessment shall be conducted for Seismic "
               "Zones 3 and 4 if both of the following conditions are "
               "present:"),
        pagina_pdf=1323),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    nota=("POR DONDE ENTRA LA LICUEFACCION EN AASHTO, que no es por la clase "
          "de sitio: es la Seccion 10, Cimentaciones, bajo 10.5.4 «Extreme "
          "Events Limit States». Y el disparador lo dice todo -- zona sismica "
          "3 o 4, MAS napa freatica en los 50 ft superiores, MAS "
          "caracteristicas de suelo por (N1)60, q_ciN, V_s1 o unidad "
          "geologica con antecedente de licuefaccion --: ninguna de las tres "
          "condiciones menciona la clase de sitio. "
          "«Site Class F» no aparece en NINGUNA pagina de la Seccion 10."),
)

AASHTO_LICUEFACCION_ESPECTRO = _cita(
    id="AASHTO_LRFD_9.10.5.4.2#ESPECTRO",
    fuente_id="AASHTO_LRFD_9",
    numeral="10.5.4.2, configuracion licuada",
    titulo_numeral="Liquefaction Design Requirements",
    pagina_impresa="10-34",
    pagina_pdf=1323,
    texto_literal=Verbatim(
        texto=("The design spectrum should be the same as that used in the "
               "nonliquefied configuration."),
        pagina_pdf=1323),
    caracter=Caracter.RECOMENDACION,
    sesion=S13,
    nota=("EL ARGUMENTO POSITIVO, y es el que convierte NOR-AAS-02 de "
          "argumento por silencio en argumento por coherencia interna de la "
          "fuente. Si un suelo licuable fuera Clase F por serlo, su fila no "
          "tendria factor -- son cinco asteriscos -- y no habria espectro "
          "«no licuado» con que empezar. AASHTO manda justo lo contrario: "
          "analizar primero SIN licuefaccion y despues CON ella, con el mismo "
          "espectro; y en la pag. impresa 10-35 acota el espectro especifico "
          "de sitio a no menos de dos tercios del que da el procedimiento "
          "general «modified by the site factors in Article 3.10.3.2». Es "
          "decir: AASHTO ESPERA que a un sitio licuable le aplique un factor "
          "de sitio TABULADO de 3.10.3.2. Eso es incompatible con que la "
          "licuefaccion lo hiciera Clase F por si sola."),
)

# ---------------------------- Manual de Puentes ----------------------------

MP_DEFINICION_CLASE_SITIO = _cita(
    id="MP.2.4.3.11.2.1.1",
    fuente_id="MP",
    numeral="2.4.3.11.2.1.1, Tabla 2.4.3.11.2.1.1-1, fila F",
    titulo_numeral="Definiciones de Clases de Sitio",
    pagina_impresa="122",
    pagina_pdf=123,
    texto_literal=Verbatim(
        texto=("Suelos que requieren evaluaciones específicas de sitio, "
               "tales como:"),
        pagina_pdf=123),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=S13,
    corresponde_en=("AASHTO_LRFD_9.T3.10.3.1-1#F",),
    nota=("LA TRADUCCION ES FIEL: las tres categorias son las mismas de "
          "AASHTO -- turbas o arcillas altamente organicas (H > 10 ft), "
          "arcillas de alta plasticidad (H > 25 ft con PI > 75), estratos de "
          "arcillas de buen espesor blandas o semirrigidas (H > 120 ft) -- y "
          "el «tales como» traduce el «such as», de modo que la lista queda "
          "abierta tambien aqui. TAMPOCO nombra la licuefaccion. "
          "El Manual la trata en otros sitios -- num. 2.4.3.11.1, 2.8.0.3, "
          "2.8.2.1.1.1, 2.8.2.1.1.3, 2.8.2.1.1.6.2 y Apendice A11 --, once "
          "apariciones en ocho paginas, y NINGUNA en este numeral ni en su "
          "tabla. No existe en el Manual un solo numeral titulado "
          "«Licuefaccion»."),
)

MP_CLASE_SITIO_EXCEPCIONES = _cita(
    id="MP.2.4.3.11.2.1.1#EXCEPCIONES",
    fuente_id="MP",
    numeral="2.4.3.11.2.1.1, bloque «Excepciones»",
    titulo_numeral="Definiciones de Clases de Sitio",
    pagina_impresa="122",
    pagina_pdf=123,
    texto_literal=Verbatim(
        texto=("Las clases de Sitio E o F no serán supuestas a no ser que la "
               "Entidaddetermine la clase de sitio E o F o estas sean "
               "establecidas por datos geotécnicos."),
        pagina_pdf=123),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    corresponde_en=("AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES",),
    nota=("LA MISMA PROHIBICION QUE AASHTO, Y MAS DURA: donde AASHTO dice "
          "«should not be assumed», el Manual escribe «NO SERAN SUPUESTAS». "
          "La norma nacional endurece la traduccion, de modo que por la Via 1 "
          "(AASHTO) o por la Via 2 (Manual) el resultado es el mismo y el "
          "expediente no puede elegir la version blanda. "
          "«Entidaddetermine», sin espacio, es errata del impreso y se "
          "transcribe tal cual (T21). "
          "DOS PUERTAS Y UN DEBER: la prohibicion cede si la Entidad "
          "determina la clase -- via autonoma, sin dato geotecnico -- o si la "
          "establecen datos geotecnicos; y la oracion anterior manda "
          "«se emprenderá una investigación de sitio suficiente para definir "
          "su clase». Este expediente no tiene ninguna de las dos puertas "
          "abiertas y si tiene el deber pendiente."),
)

MP_PELIGRO_SISMICO_CLASE_F = _cita(
    id="MP.2.4.3.11.2#CLASE_F",
    fuente_id="MP",
    numeral="2.4.3.11.2",
    titulo_numeral="Peligro Sísmico",
    pagina_impresa="121",
    pagina_pdf=122,
    texto_literal=Verbatim(
        texto=("El procedimiento especificado de sitio será usado si existen "
               "las siguientes condiciones:"),
        pagina_pdf=122),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    corresponde_en=("AASHTO_LRFD_9.3.10.2#CLASE_F",),
    nota=("LA SEGUNDA VIA, INDEPENDIENTE DE LA NOTA 2 DE LA TABLA. La segunda "
          "condicion de la lista es «Si el sitio está clasificado como sitio "
          "clase F (Articulo. 2.4.3.11.2.1.1) (3.10.3.1 AASHTO).», y el verbo "
          "es «sera usado», imperativo. De modo que la exigencia de estudio "
          "para la Clase F esta DOS veces en el Manual -- aqui en el "
          "articulado y en la Nota 2 de las tres tablas de factores -- y "
          "ninguna de las dos admite dispensa. "
          "Barrido completo: «sitio clase F» aparece 4 veces en las 673 "
          "paginas (esta y las tres Notas 2); no hay ninguna salvedad por "
          "periodo fundamental corto. La quinta aparicion de «clase F» en el "
          "Manual es ACERO ASTM A668 Clase F (pag. impresa 289) y no guarda "
          "relacion: es la tercera homonimia de «Clase F» del corpus, junto "
          "al concreto Clase F de EG-2013 (NOR-VOC-04)."),
)

# --------------------------------- E.030 -----------------------------------

E030_PERFIL_S5 = _cita(
    id="E030.T2#S5",
    fuente_id="E030",
    numeral="Art. 14.6, Tabla Nº 2, fila S5",
    titulo_numeral="Tipos de perfiles de suelo",
    pagina_impresa="11",
    pagina_pdf=11,
    texto_literal=Verbatim(
        texto=("Estos casos no están cubiertos en la clasificación "
               "establecida en la Tabla Nº2 de la presente Norma Técnica. Se "
               "prohíbe las construcciones apoyadas sobre estos perfiles, "
               "salvo que, se efectúe un estudio específico para el sitio, en "
               "el cual se debe considerar los mejoramientos en el estrato "
               "del perfil."),
        pagina_pdf=11),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    nota=("LA PRIMERA CITA DE E.030 DEL REGISTRO, y llego tarde por un "
          "artefacto: el PDF emite la ligadura U+FB01 seguida de un espacio "
          "-- «clasiﬁ cación», «perﬁ les», «especíﬁ co» --, de modo que "
          "ninguna frase entera de esta norma se encontraba en su propia "
          "pagina hasta que `extraccion.pdf` aprendio a deshacerlo. "
          "EL ESTATUTO DE S5, con precision: es fila de la Tabla Nº 2 -- "
          "sexta y ultima, «Suelos excepcionales», con diez viñetas de las "
          "que la PRIMERA es «Suelos potencialmente licuables» y esta es la "
          "decima --, y a la vez NO tiene fila en la Tabla Nº 3 del num. 14.7 "
          "ni columna en las Tablas Nº 4 y Nº 5. Es decir: nominal en la "
          "tabla que la define, laguna en las tres que dan numeros. "
          "La prohibicion es CONDICIONADA: la misma oracion la levanta con "
          "estudio especifico y mejoramiento del estrato. La hoja de ruta la "
          "citaba mal por tres sitios -- corregidos en I2; ver "
          "DIS-HR-CLASE-DE-SITIO-F, resuelta --, y su pasaje de Fase 0-bis "
          "quedo literal con la elision marcada, como "
          "constantes_normativas.E030_S5_TEXTO, que siempre la transcribio "
          "exacta."),
)

E030_FACTOR_SUELO = _cita(
    id="E030.T4",
    fuente_id="E030",
    numeral="Art. 17, Tabla Nº 4",
    titulo_numeral="Factor de suelo",
    pagina_impresa="13",
    pagina_pdf=13,
    texto_literal=Verbatim(
        texto="Requiere un análisis de respuesta de sitio",
        pagina_pdf=13),
    caracter=Caracter.EXIGENCIA,
    sesion=S13,
    nota=("DONDE LOS DOS ESQUEMAS CONVERGEN, que es lo que faltaba mirar. "
          "E.030 no tiene F_pga, Fa ni Fv: su aparato es S, T_P y T_L. Y su "
          "Tabla Nº 4 «Factor de suelo S» tiene columnas S0, S1, S2, S3 y S4 "
          "-- NO tiene columna S5 --, de modo que a su categoria excepcional "
          "no le asigna factor, igual que AASHTO y el Manual no se lo asignan "
          "a la Clase F. "
          "El verbatim es la celda de la fila Z4, columna S4: en la zona "
          "sismica de esta obra, E.030 ya exige analisis de respuesta de "
          "sitio un escalon ANTES de la categoria excepcional. Con S5 no hay "
          "siquiera celda que leer. "
          "Los dos esquemas discrepan en el CRITERIO -- E.030 nombra los "
          "suelos licuables, AASHTO no -- y coinciden en la CONSECUENCIA: "
          "ninguno tabula un factor para su categoria excepcional."),
)


# ===========================================================================
# LAS SIETE CITAS DEL CAJON (sesion C2)
# ===========================================================================
# Las transcribe C2 porque §15.7 de docs/ruta_familia_c.md las declaro
# BLOQUEANTES: sin ellas, tres de los ocho `Fundamento` que C3, C4 y C5
# consumen -- F3.TIPO_MARCO, F3.MANTENIMIENTO y F3.CELDAS -- no se pueden
# construir, y C5 se detiene sin aviso previo.
#
# LAS CUATRO PRIMERAS CUELGAN DEL MISMO NUMERAL, 4.1.1.3.4 a), que ya tiene
# cita propia (`MC_HHD.4.1.1.3.4a`, el piso de 0.90 m). No se amplia aquella:
# una `Cita` sostiene UNA frase, y estas cuatro dicen cosas distintas con
# CARACTERES DISTINTOS -- una define, una permite y dos recomiendan --. Meter
# las cinco en un solo objeto obligaria a elegirle un caracter unico al
# numeral, y entonces `VERBO_COMPATIBLE_CON` dejaria de poder distinguir
# «la norma obliga» de «la norma recomienda», que es justo lo que T11 existe
# para impedir (NOR-MEM-01).

CAJON_TIPOS = _cita(
    id="MC_HHD.4.1.1.3.4a#TIPOS",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 a)",
    titulo_numeral="a)  Tipo y sección",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="71",
    pagina_pdf=74,
    pagina_pdf_titulo=74,
    texto_literal=Verbatim(
        texto=("Los tipos de alcantarillas comúnmente utilizadas en proyectos "
               "de carreteras en nuestro país son; marco de concreto, "
               "tuberías metálicas corrugadas, tuberías de concreto y "
               "tuberías de polietileno de alta densidad."),
        pagina_pdf=74),
    caracter=Caracter.DEFINICION,
    sesion=C2,
)

CAJON_NIVELES = _cita(
    id="MC_HHD.4.1.1.3.4a#NIVELES",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 a)",
    titulo_numeral="a)  Tipo y sección",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="72",
    pagina_pdf=75,
    pagina_pdf_titulo=74,
    texto_literal=Verbatim(
        texto=("Las alcantarillas tipo marco de concreto de sección "
               "rectangular o cuadrada pueden ubicarse a niveles que se "
               "requiera, como colocarse de tal manera que el nivel de la "
               "rasante coincida con el nivel superior de la losa o debajo "
               "del terraplén."),
        pagina_pdf=75),
    # PERMISO y no EXIGENCIA: el verbo de la fuente es «pueden ubicarse». Es
    # lo que hace citable el cruce a nivel de canal de riego -- la rasante
    # coincidiendo con la losa -- sin convertirlo en obligacion.
    caracter=Caracter.PERMISO,
    sesion=C2,
)

CAJON_MARCO = _cita(
    id="MC_HHD.4.1.1.3.4a#MARCO",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 a)",
    titulo_numeral="a)  Tipo y sección",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="72",
    pagina_pdf=75,
    pagina_pdf_titulo=74,
    # «ESTE TIPO» TIENE SU ANTECEDENTE EN LA ORACION ANTERIOR, que es la de
    # `#NIVELES`: las dos son la primera y la segunda oracion del MISMO
    # parrafo. Se citan separadas porque su `caracter` difiere -- permiso y
    # recomendacion --, y se deja dicho aqui para que nadie lea «este tipo»
    # como si el numeral recomendara cualquier alcantarilla.
    texto_literal=Verbatim(
        texto=("Generalmente, se recomienda emplear este tipo de "
               "alcantarillas cuando se tiene la presencia de suelos de "
               "fundación de mala calidad."),
        pagina_pdf=75),
    caracter=Caracter.RECOMENDACION,
    condiciones=(
        CondicionAplicacion(
            id="COND-MARCO-SUELO-MALA-CALIDAD",
            texto=Verbatim(
                texto=("cuando se tiene la presencia de suelos de fundación "
                       "de mala calidad"),
                pagina_pdf=75),
            cita_id="MC_HHD.4.1.1.3.4a#MARCO",
            # `NoEvaluable` Y NO `PorDatoDeSitio`, y la primera redaccion lo
            # tuvo mal. Escribia `PorDatoDeSitio(clave="sucs_fundacion")` con
            # el comentario «la clave existe y hoy no tiene valor», y las dos
            # mitades eran falsas: `sucs_fundacion` NO esta en
            # `datos_sitio.DATOS_SITIO` -- es COLUMNA DEL CSV, porque es un
            # dato que varia punto a punto --. El efecto era peor que el
            # error: `ventana_normativa.disponibilidad_de` corta por la rama
            # «la clave no esta en datos_sitio» ANTES de mirar el efecto, de
            # modo que esta condicion BLOQUEABA declarando que advertia, la
            # `justificacion_de_no_bloquear` que T15 obliga a escribir era
            # texto muerto, y la ventana mandaba al revisor a declarar en
            # `datos_sitio.py` un dato que CLAUDE.md manda poner en el CSV.
            #
            # Lo que la condicion dice de verdad es que el Manual NO DEFINE
            # «mala calidad»: no hay mapeo SUCS -> mala calidad en la fuente,
            # y inventarlo es lo que §15.5 dejo dicho que NO se haga. Eso es
            # `NoEvaluable`, y ahi el ADVIERTE si se honra.
            resuelve=NoEvaluable(
                por_que=("el Manual recomienda el marco «cuando se tiene la "
                         "presencia de suelos de fundacion de mala calidad» y "
                         "NO define «mala calidad»: no da umbral, ni "
                         "clasificacion, ni remision a otra norma. La columna "
                         "`sucs_fundacion` del CSV trae el grupo SUCS del "
                         "punto, y traducirlo a «mala calidad» seria inventar "
                         "el mapeo que la fuente calla"),
                que_lo_cerraria=("un criterio declarado que fije que grupos "
                                 "SUCS cuentan como mala calidad, con su "
                                 "fuente tecnica y su ventana. C6 LO REVISO Y "
                                 "NO LO ABRIO, que es lo contrario de lo que "
                                 "esta linea anunciaba: abrirlo como "
                                 "`Criterio(valor=None)` lo dejaria entrando "
                                 "en `criterios_sin_valor()` como vacio "
                                 "BLOQUEANTE que nadie tiene obligacion de "
                                 "contestar -- el defecto que la bandera "
                                 "`opcional` se creo para retirar --, y "
                                 "`opcional=True` tampoco vale porque el "
                                 "catalogo la define para el criterio que "
                                 "refina un valor que la norma YA fija, y "
                                 "aqui no hay valor normativo por defecto. "
                                 "Queda para la sesion que implemente de "
                                 "verdad la eleccion de tipo a partir del "
                                 "suelo, con la fuente que respalde el mapeo "
                                 "(la candidata peruana es la E.050) y con el "
                                 "cambio de esquema de "
                                 "`_Columna.criterio_destino`, que hoy admite "
                                 "UN destino")),
            efecto_si_indeterminada=Efecto.ADVIERTE,
            justificacion_de_no_bloquear=(
                "la frase RECOMIENDA el marco cuando el suelo es malo; no lo "
                "PROHIBE cuando es bueno. Un suelo de fundacion sin declarar "
                "deja sin apoyo a la recomendacion, no al tipo: la asignacion "
                "del marco a la Familia C se sostiene ademas en el permiso de "
                "niveles y en la Lamina Nº 03. Bloquear aqui detendria el "
                "calculo por un dato que solo REFUERZA la eleccion")),
    ),
    sesion=C2,
)

CAJON_MULTIPLES = _cita(
    id="MC_HHD.4.1.1.3.4a#MULTIPLES",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 a)",
    titulo_numeral="a)  Tipo y sección",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="72",
    pagina_pdf=75,
    pagina_pdf_titulo=74,
    # LA ORACION ENTERA, Y NO EL FRAGMENTO. §15.7 la proponia recortada --
    # «...recomendandose utilizar obras con mayor seccion transversal libre,
    # sin subdivisiones.» --, y eso es una ELISION SIN MARCAR bajo el rotulo
    # «texto literal»: exactamente el defecto que CLAUDE.md nombra a proposito
    # de la tercera condicion de h_o. Ademas el recorte se lee como una
    # preferencia GENERAL por la celda unica, y no lo es: la recomendacion
    # esta condicionada al supuesto de alcantarillas multiples en cauce con
    # arrastre, que es lo que la oracion completa dice y el fragmento esconde.
    texto_literal=Verbatim(
        texto=("En cauces naturales que presentan caudales de diseño "
               "importantes donde la rasante no permite el emplazamiento de "
               "una alcantarilla de dimensión considerable, se suelen colocar "
               "alcantarillas múltiples, sin embargo, este diseño debe tener "
               "en cuenta la capacidad de arrastre del curso natural "
               "(palizada, troncos y material de cauce) y su pendiente "
               "longitudinal para evitar obstrucciones, recomendándose "
               "utilizar obras con mayor sección transversal libre, sin "
               "subdivisiones."),
        pagina_pdf=75),
    # RECOMENDACION y no EXIGENCIA: el verbo de la fuente es
    # «recomendandose». El «debe tener en cuenta» de la misma oracion recae
    # sobre el DISEÑO MULTIPLE, no sobre la eleccion de celda unica.
    caracter=Caracter.RECOMENDACION,
    condiciones=(
        CondicionAplicacion(
            id="COND-MULTICELDA-ARRASTRE",
            texto=Verbatim(
                texto=("este diseño debe tener en cuenta la capacidad de "
                       "arrastre del curso natural (palizada, troncos y "
                       "material de cauce) y su pendiente longitudinal para "
                       "evitar obstrucciones"),
                pagina_pdf=75),
            cita_id="MC_HHD.4.1.1.3.4a#MULTIPLES",
            resuelve=NoEvaluable(
                por_que=("la capacidad de arrastre del curso -- palizada, "
                         "troncos, material de cauce -- no es una magnitud "
                         "que este programa calcule ni una columna del CSV: "
                         "se establece con inspeccion del cauce"),
                que_lo_cerraria=("una caracterizacion del arrastre por punto, "
                                 "que hoy no entra al calculador por ninguna "
                                 "via")),
            efecto_si_indeterminada=Efecto.ADVIERTE,
            justificacion_de_no_bloquear=(
                "la recomendacion apunta a la seccion UNICA, que es la que "
                "este proyecto adopta: mientras no haya multicelda, seguir la "
                "recomendacion no exige evaluar la condicion. El dia que "
                "alguien adopte multicelda, es su adopcion la que tiene que "
                "justificarse -- la carga de la prueba la invierte el "
                "numeral --, y entonces esta condicion deja de ser "
                "indeterminada y pasa a ser el argumento que falta")),
    ),
    sesion=C2,
)

MANTENIMIENTO_Y_LIMPIEZA = _cita(
    id="MC_HHD.4.1.1.3.7d",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 d)",
    titulo_numeral="d)  Mantenimiento y limpieza",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="80",
    pagina_pdf=83,
    pagina_pdf_titulo=83,
    texto_literal=Verbatim(
        texto=("Las dimensiones de las alcantarillas deben permitir efectuar "
               "trabajos de mantenimiento y limpieza en su interior de manera "
               "factible."),
        pagina_pdf=83),
    # EXIGENCIA SIN NUMERO, y ese es todo su valor. Levantado el piso de
    # 0.90 m para los cruces de canal, esta frase es lo que impide que la
    # seccion del cajon quede sin cota inferior normativa: obliga a que
    # exista un minimo y deja al proyecto decir cual. Es la forma exacta de
    # un vacio declarable.
    caracter=Caracter.EXIGENCIA,
    sesion=C2,
)

LAMINA_03 = _cita(
    id="MC_HHD.LAMINA_03",
    fuente_id="MC_HHD",
    numeral="Lámina Nº 03",
    # EL TITULO DEL CAJETIN SE GUARDA A MEDIAS, Y ES UNA LIMITACION DEL
    # REGISTRO, NO UNA LECTURA. Medido sobre la pagina: el cajetin imprime el
    # titulo en DOS RENGLONES APILADOS del mismo bloque -- «SECCIONES TÍPICAS
    # DE ALCANTARILLAS» en y = 671.4 y «CON PROTECCIÓN A LA ENTRADA Y SALIDA»
    # en y = 689.2, con la x solapada --, de modo que VISUALMENTE el titulo es
    # uno solo y §15.4 tiene razon al darlo entero.
    #
    # Aqui va solo el primer renglon porque T3 verifica `titulo_numeral`
    # BUSCANDOLO EN LA CAPA DE TEXTO, y esa capa entrega los dos renglones
    # como corridas independientes y ademas en orden inverso: la cadena
    # compuesta no aparece y T3 la rechazaria. Es una limitacion de la
    # maquinaria de verificacion -- un titulo repartido en dos corridas no se
    # puede guardar entero y seguir siendo verificable --, y se declara como
    # tal en vez de disfrazarse de decision.
    #
    # LA PRIMERA REDACCION DE ESTE COMENTARIO DECIA DOS COSAS QUE NO ERAN: que
    # unirlas seria una `Transcripcion` -- no lo seria, la pagina las imprime
    # apiladas como un titulo --, y que la segunda mitad «viaja como
    # texto_previo», que es campo de `TablaNormativa` y NO de `Cita`. La
    # segunda mitad hoy no viaja a ninguna parte, y eso es lo que hay que
    # saber al leer esto.
    titulo_numeral="SECCIONES TÍPICAS DE ALCANTARILLAS",
    jerarquia_numeral=(),
    pagina_impresa="209",
    pagina_pdf=212,
    pagina_pdf_titulo=212,
    texto_literal=Verbatim(
        texto="ALCANTARILLA TIPO MARCO DE CONCRETO EN CRUCE DE CANAL DE RIEGO",
        pagina_pdf=212),
    # DEFINICION: la lamina no manda nada, TIPIFICA. Es el respaldo de fuente
    # primaria del TIPO de estructura de la Familia C -- hasta hoy apoyado
    # solo en la Sec. 2.3 de la hoja de ruta, que no es fuente primaria --.
    caracter=Caracter.DEFINICION,
    # Es un PLANO: se leyo sobre la pagina renderizada. Declararlo es lo que
    # `MetodoDeVerificacion` existe para obligar (§15.4).
    metodo=IMAGEN,
    sesion=C2,
)

HDS5_A3_FORMAS = _cita(
    id="HDS5_3ED.A.3#FORMAS",
    fuente_id="HDS5_3ED",
    numeral="A.3",
    titulo_numeral="A.3  INLET CONTROL DIMENSIONLESS DESIGN CURVES",
    jerarquia_numeral=(),
    # EL NUMERAL ES A.3 Y LA PAGINA IMPRESA ES A.2, y no es un desliz: el
    # numeral ABRE al pie de la pagina anterior a la que lleva su nombre. La
    # §15.7 de docs/ruta_familia_c.md escribio «A.3» en la columna de pagina,
    # que es la confusion numeral/folio que NOR-HDS-01 ya cerro una vez -- el
    # ke citado a la pag. «C.2» cuando la Tabla C.2 esta en la C.6 --.
    pagina_impresa="A.2",
    pagina_pdf=191,
    pagina_pdf_titulo=191,
    texto_literal=Verbatim(
        texto=("Note that coefficients for rectangular (box) shapes should "
               "not be used for nonrectangular (circular, arch, pipe-arch, "
               "etc.) shapes and vice-versa."),
        pagina_pdf=191),
    # EXIGENCIA: «should not be used» es una prohibicion, y hay que ser preciso
    # sobre QUE prohibe, porque este comentario lo dijo mal y el error se
    # propago a cuatro archivos.
    #
    # PROHIBE CRUZAR COEFICIENTES ENTRE GEOMETRIAS -- «rectangular (box)
    # shapes» frente a «nonrectangular» --. En esa lectura es vinculante y
    # directa para la Familia C: el cajon usa una carta DE CAJON, no la
    # circular de concreto con otras constantes.
    #
    # NO PROHIBE NADA SOBRE LAS DOS FORMAS DE ECUACION. Este comentario decia
    # «es la prohibicion que separa las dos formas de ecuacion», y es falso.
    # Cual de las dos aplica lo decide la COLUMNA «Equation Form» de la Tabla
    # A.1, fila por fila. La prueba de que son ejes ortogonales esta en la
    # propia tabla, medida sobre sus 36 filas en C3: «Rect. Box Concrete»
    # aparece con Forma 1 (Carta 8) Y con Forma 2 (Cartas 9 a 11), y
    # «Circular» tambien (Carta 3 Forma 1, Carta 55 Forma 2). La misma
    # geometria vive en las dos formas; una prohibicion sobre geometrias no
    # puede ser la regla que separa las formas.
    #
    # De aqui salio el error: la regla vinculante #5 de §6 lo enunciaba asi, y
    # C3 lo copio a `constantes_normativas`, a `M4._hw_sobre_D_no_sumergido` y
    # a `modelos.ConstantesHDS5` creyendo que lo verificaba. Los cuatro sitios
    # estan corregidos.
    caracter=Caracter.EXIGENCIA,
    sesion=C2,
)


# ===========================================================================
# ASTM A760/A760M-10 y AASHTO M 36 -- las dos ediciones de la norma de
# producto del TMC (I1, NOR-PRO-04). TODO por IMAGEN: ninguna de las dos
# fuentes entrega texto utilizable (raster puro en M 36; ToUnicode roto en
# A760), y las dos citas se leyeron sobre la pagina renderizada.
# ===========================================================================

ASTM_A760_T1 = _cita(
    id="ASTM_A760.T1",
    fuente_id="ASTM_A760",
    numeral="Tabla 1",
    titulo_numeral="TABLA 1 Tamaños de tubería",
    pagina_impresa="3",
    pagina_pdf=3,
    texto_literal=Verbatim(
        texto="TABLA 1 Tamaños de tubería",
        pagina_pdf=3),
    # DEFINICION: la tabla TIPIFICA que tamaños de corrugacion son estandar
    # para cada diametro nominal (su nota A lo dice con esas palabras); no
    # manda nada por si misma. La exigencia de elegir el diametro DE esta
    # tabla vive en el articulado de la norma, no en el rotulo de la tabla.
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=I1,
    nota=("Leida sobre la pagina PDF 3 renderizada (S14 dejo comprobado que "
          "es legible a escala 2.0; esta transcripcion se hizo a 4.0). El "
          "PDF es la TRADUCCION AL ESPAÑOL de la norma (propiedad declarada "
          "en la Fuente): el titulo impreso es «TABLA 1 Tamaños de tubería» "
          "y los encabezados mezclan «en.» (in.) con «pulg.». La MISMA tabla "
          "existe como Table 6 de AASHTO M 36 (doble designacion, ediciones "
          "distintas): las diferencias medidas entre las dos estan "
          "declaradas en la correspondencia CORR-TAMANOS-TMC."),
)

AASHTO_M36_T6 = _cita(
    id="AASHTO_M36.T6",
    fuente_id="AASHTO_M36",
    numeral="Table 6",
    titulo_numeral="Table 6—Pipe Sizes",
    pagina_impresa="M 36-11",
    pagina_pdf=12,
    texto_literal=Verbatim(
        texto="Table 6—Pipe Sizes",
        pagina_pdf=12),
    # DEFINICION, igual que su gemela de A760: la tabla tipifica. El numeral
    # que la hace vinculante es el 8.1.1 (pag. impresa M 36-10, PDF 11):
    # «Pipe Dimensions—The nominal diameter of the pipe shall be as stated
    # in the order, selected from the size listed in Table 6. The size of
    # corrugations that are standard for each size of pipe are also shown
    # in Table 6.» Ese «shall» viaja como texto_previo de la TablaNormativa,
    # con su propia pagina.
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=I1,
    nota=("RASTER PURO: leida entera sobre la pagina PDF 12 renderizada "
          "(escalas 4.0 y 8.0; las filas 2550-3600 exigieron la segunda "
          "para separar las columnas de costilla). La pagina impresa lleva "
          "el rotulo «M 36-11» al pie, que confirma el desfase +1 de la "
          "Fuente."),
)

AASHTO_M170M_T1_T5 = _cita(
    id="AASHTO_M170M.T1_T5#DIAMETROS",
    fuente_id="AASHTO_M170M",
    numeral="Tables 1 to 5",
    titulo_numeral=("Table 1—Design Requirements for Class I Reinforced "
                    "Concrete Pipe"),
    pagina_impresa="M 170M-3",
    pagina_pdf=3,
    texto_literal=Verbatim(
        texto=("Table 1—Design Requirements for Class I Reinforced "
               "Concrete Pipe"),
        pagina_pdf=3),
    # DEFINICION, como sus gemelas de producto: las cinco tablas tipifican
    # que diametros existen por clase; lo que las hace vinculantes es el
    # num. 7.1 («shall be as prescribed for Class I to V in Tables 1 to 5,
    # except as provided in Section 7.2»).
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T2,
    nota=("ES EL ANCLA DE DIS-HR-D-MAX: la envolvente de diametros de las "
          "cinco tablas, leida TABLA POR TABLA sobre las paginas "
          "renderizadas (escaneo con OCR inutilizable; ver la Fuente). "
          "Columna «Internal Designated Diameter, mm»: Tabla 1 (Clase I, "
          "PDF 3): 1500 a 3450; Tabla 2 (Clase II, PDF 4-5): 300 a 3450; "
          "Tabla 3 (Clase III, PDF 6-7): 300 a 3600; Tabla 4 (Clase IV, "
          "PDF 8-9): arranca en 300 y SU MAXIMO NO ES VERIFICABLE en este "
          "ejemplar -- la tinta de la mitad baja de la PDF 8 no esta en el "
          "escaneo --; Tabla 5 (Clase V, PDF 10-11): 300 a 3600. La "
          "envolvente NO es uniforme y por eso «Tablas 1 a 5: de 300 a "
          "3600» solo es cierta leida como CONJUNTO. Encima de lo tabulado, "
          "el num. 7.2 «Modified and Special Designs» (PDF 13) preve, "
          "con permiso del propietario, «special designs for sizes and "
          "loads beyond those shown in Tables 1 to 5» (7.2.1); y el num. "
          "4.1 «CLASSIFICATION» (PDF 2) remite: «The corresponding "
          "strength requirements are prescribed in Tables 1 to 5.» "
          "DOS RESERVAS DE LEGIBILIDAD, ninguna contraria: el rotulo al "
          "pie de la PDF 3 esta degradado (la correspondencia «M 170M-3» "
          "la fijan los rotulos legibles de las paginas vecinas M 170M-2 y "
          "M 170M-4 y la regla de paginacion), y los digitos del numero de "
          "tabla en las paginas de continuacion (PDF 7 y 9) no se leen: la "
          "asignacion de cada continuacion a su tabla es por secuencia de "
          "rotulos y coherencia de filas."),
)



# ===========================================================================
# AASHTO M 294-11, TRADUCCION NO OFICIAL (N2) -- la norma de producto del
# HDPE, leida sobre un ejemplar que NO es el original de AASHTO.
#
# TRES COSAS ANTES DE LEER UNA SOLA CITA. (1) La Fuente es una traduccion al
# español no oficial (ver `fuentes.AASHTO_M294_TRAD`): cada cita lleva el
# sufijo TRAD en el id y las palabras «traducción no oficial» en su nota, y
# `test_toda_cita_de_la_traduccion_de_M294_lo_dice` lo exige. Lo que
# acreditan es lo que la TRADUCCION dice; el original sigue ausente
# (`AASHTO_M294`) y su ficha dice que lo que desbloquearia es FIRMARLAS.
# (2) NINGUNA LLEVA FIRMA, y no es por no haberse leido: el ejemplar no
# imprime folio, la paginacion es `SinDeterminar` y el invariante T6 impide
# firmar una pagina PDF de una fuente sin paginacion medida. El precedente
# es HDS5_SI_1985.EC4B#K, y la prohibicion no se toca por conveniencia: es
# la que impide que una pagina supuesta pase por medida. Estan censadas en
# CITAS_SIN_FIRMA_A_PROPOSITO (tests/test_normativa.py). Lo que las vigila
# es la suite: T0 acota la pagina y T2/T3 exigen que el Verbatim y el titulo
# aparezcan en su PDF en cada corrida con PyMuPDF, porque el texto SI es
# extraible -- a diferencia de las otras cuatro normas de producto y
# practica ASTM/AASHTO de normas/ --. Leidas por el verificador-normativo
# en N2 (2026-09-14) por texto y por imagen (hojas 1 y 5 renderizadas).
# (3) LO QUE SOSTIENEN: el techo de la serie del HDPE en 1500 mm (1.1.1 y
# 7.2.1), la tabla de espesores minimos de pared (7.2.2, transcrita en
# tablas.py como AASHTO_M294_TRAD.T7.2.2) y la EXCLUSION del diseño
# estructural (1.4), que es lo que autoriza la afirmacion negativa de
# 'clases_producto_por_relleno' para el HDPE.
# ===========================================================================

AASHTO_M294_TRAD_1_1_1 = _cita(
    id="AASHTO_M294_TRAD.1.1.1",
    fuente_id="AASHTO_M294_TRAD",
    numeral="1.1.1",
    # El numeral no lleva titulo propio: cuelga de «1. Ámbito», y eso es lo
    # que se transcribe. La jerarquia es el 1.1 del que es inciso.
    titulo_numeral="Ámbito",
    pagina_impresa="s/n",
    pagina_pdf=1,
    jerarquia_numeral=("1.1.",),
    texto_literal=Verbatim(
        texto="Se incluyen los tamaños nominales de 300 a 1500 mm (12 a 60 in.).",
        pagina_pdf=1),
    # DEFINICION: es la frase de AMBITO de la especificacion. No exige ni
    # prohibe un diametro; dice que tamaños cubre, y el 7.2.1 los desarrolla.
    # Es el ancla de la parte AASHTO_M294_TRAD de DIS-HR-D-MAX (el techo);
    # el 7.2.1 es el ancla de DIS-HR-M294-PASO (la serie, fila a fila).
    caracter=Caracter.DEFINICION,
    verificada=False,
    nota=("SIN FIRMA A PROPOSITO, no sin verificar: la fuente es una "
          "TRADUCCIÓN NO OFICIAL al español de AASHTO M 294-11 y no imprime "
          "folio (`pagina_impresa` dice «s/n» por eso), y el invariante T6 "
          "impide firmar una pagina PDF de una fuente sin paginacion medida "
          "-- ver la cabecera del bloque --. Contenido comprobado en N2 "
          "(verificador-normativo, 2026-09-14, por texto y por imagen de la "
          "hoja 1): la frase esta integra en la PDF 1 bajo «1. Ámbito», "
          "inciso 1.1.1. Es la frase que fija el TECHO DE LA SERIE del HDPE "
          "en 1500 mm, y el ancla de DIS-HR-D-MAX para el HDPE; el num. "
          "7.2.1 la desarrolla diametro a diametro. Lo que acredita es lo que la "
          "traduccion dice; el original en ingles sigue ausente "
          "(`AASHTO_M294`)."),
)

AASHTO_M294_TRAD_1_4 = _cita(
    id="AASHTO_M294_TRAD.1.4",
    fuente_id="AASHTO_M294_TRAD",
    numeral="1.4",
    # Tampoco lleva titulo propio: es un parrafo del «1. Ámbito».
    titulo_numeral="Ámbito",
    pagina_impresa="s/n",
    pagina_pdf=1,
    texto_literal=Verbatim(
        texto=("Esta especificación no incluye requerimientos para camas, "
               "relleno o carga de cubierta de tierra. El desempeño exitoso "
               "de este producto depende del tipo apropiado de cama y "
               "relleno, y del cuidado en la instalaión. El diseño "
               "estructural de la tubería corrugada de PE y los "
               "procedimientos apropiados de instalación, se proporcionan en "
               "AASHTO LRFD Especificaciones de Diseño de Puentes, Sección "
               "12, y en LFRD Especificación de Construcción de Puentes, "
               "Sección 30, respectivamente."),
        pagina_pdf=1),
    # DEFINICION de lo que la especificacion NO cubre: es la frase que
    # autoriza la afirmacion negativa SIN_CLASE_POR_ALTURA_M294_TRAD.
    caracter=Caracter.DEFINICION,
    verificada=False,
    nota=("SIN FIRMA A PROPOSITO, no sin verificar: TRADUCCIÓN NO OFICIAL "
          "sin folio, invariante T6 (ver la cabecera del bloque). Contenido "
          "comprobado en N2 (verificador-normativo, 2026-09-14, por texto y "
          "por imagen de la hoja 1): el Verbatim son las TRES PRIMERAS "
          "ORACIONES de un parrafo de cuatro, integras en la PDF 1; la "
          "cuarta -- la que remite al fabricante «el detalle de la seción "
          "del perfil de la pared» -- queda fuera del Verbatim a proposito "
          "y la usa la afirmacion negativa SIN_DIAMETRO_EXTERIOR_M294_TRAD. "
          "«instalaión» y «LFRD» son erratas de la traduccion y se "
          "transcriben como se imprimen (T21). Es el ancla de la afirmacion "
          "negativa SIN_CLASE_POR_ALTURA_M294_TRAD: la norma de producto del "
          "HDPE excluye camas, relleno y carga de cubierta, y remite el "
          "diseño estructural a AASHTO LRFD Seccion 12 -- que es lo que "
          "'clases_producto_por_relleno' venia afirmando del HDPE sin poder "
          "contrastarlo --."),
)

AASHTO_M294_TRAD_7_2_1 = _cita(
    id="AASHTO_M294_TRAD.7.2.1",
    fuente_id="AASHTO_M294_TRAD",
    # La pagina imprime «7.2.1» sin punto final, a diferencia de sus vecinos
    # «7.2.2.» y «7.2.3.»: se transcribe como esta.
    numeral="7.2.1",
    titulo_numeral="Tamaño nominal",
    pagina_impresa="s/n",
    pagina_pdf=5,
    jerarquia_numeral=("REQUERIMIENTOS", "Dimensiones de la tubería:"),
    texto_literal=Verbatim(
        texto=("Los diámetros nominales deberán ser 300, 375, 450, 525, 600, "
               "675, 750, 900, 1050, 1200, 1350 y 1500 mm (12, 15, 18, 21, "
               "24, 27, 30, 36, 42, 48, 54 y 60 in.)."),
        pagina_pdf=5),
    # EXIGENCIA («deberán ser»): la serie es cerrada. Doce diametros, de 300
    # a 1500 mm, con paso de 75 mm hasta 750 y de 150 mm de 900 a 1500; el
    # 1500 es la ultima fila y no hay «y superiores». Es el ancla nueva de
    # DIS-HR-D-MAX para el HDPE: el unico de los tres topes del catalogo que
    # coincide con el techo de una norma de producto.
    caracter=Caracter.EXIGENCIA,
    verificada=False,
    nota=("SIN FIRMA A PROPOSITO, no sin verificar: TRADUCCIÓN NO OFICIAL "
          "sin folio, invariante T6 (ver la cabecera del bloque). Contenido "
          "comprobado en N2 (verificador-normativo, 2026-09-14, por texto y "
          "por imagen de la hoja 5): la frase esta integra en la PDF 5 bajo "
          "«7. REQUERIMIENTOS» > «7.2. Dimensiones de la tubería:». La "
          "primera oracion del numeral, que el Verbatim no incluye, define "
          "el tamaño nominal como el diametro nominal INTERIOR. El num. 1.3 "
          "(PDF 1) declara los valores SI como los estandar y las pulgadas "
          "entre parentesis como no necesariamente equivalencias exactas, de "
          "modo que 1500 mm es el valor y 60 in. la aproximacion. Lo que "
          "acredita es lo que la traduccion dice; para el HDPE la serie "
          "TERMINA donde el proyecto topa (1.50 m), a diferencia de A760 y "
          "M 170M, que tabulan hasta 3600 mm."),
)

AASHTO_M294_TRAD_7_2_2 = _cita(
    id="AASHTO_M294_TRAD.7.2.2",
    fuente_id="AASHTO_M294_TRAD",
    numeral="7.2.2",
    titulo_numeral="Espesor de pared",
    pagina_impresa="s/n",
    pagina_pdf=5,
    jerarquia_numeral=("REQUERIMIENTOS", "Dimensiones de la tubería:"),
    texto_literal=Verbatim(
        texto=("La pared interior de la tubería Tipo S y las paredes "
               "interior y exterior de la tubería Tipo D, deberán tener lo "
               "siguientes espesores mínimos cuando se midan de acuerdo con "
               "la Sección 9.6.4."),
        pagina_pdf=5),
    # EXIGENCIA («deberán tener»): la tabulacion que sigue es de MINIMOS.
    caracter=Caracter.EXIGENCIA,
    verificada=False,
    nota=("SIN FIRMA A PROPOSITO, no sin verificar: TRADUCCIÓN NO OFICIAL "
          "sin folio, invariante T6 (ver la cabecera del bloque). Contenido "
          "comprobado en N2 (verificador-normativo, 2026-09-14, por texto y "
          "por imagen de la hoja 5). «lo siguientes» es errata de la "
          "traduccion, transcrita como se imprime (T21). Sostiene la tabla "
          "AASHTO_M294_TRAD.T7.2.2. LO QUE ESTE ESPESOR ES Y NO ES, porque "
          "el nombre invita al error: es el minimo de la pared interior lisa "
          "(Tipo S) o de las dos paredes (Tipo D), medido segun 9.6.4; NO es "
          "la altura del perfil corrugado y NO fija el diametro exterior, "
          "que la traduccion no trae en ninguna hoja "
          "(SIN_DIAMETRO_EXTERIOR_M294_TRAD). Por eso esta tabla NO cierra "
          "'espesor_pared_conducto' para el HDPE."),
)


# Los Fundamentos (§3.10) NO viven aqui: la decision abierta #4 del diseño del
# registro los difirio a S18 y S18 les dio archivo propio,
# `normativa/fundamentos.py`. El motivo es de lectura, no de tamaño: una cita
# dice QUE dice la fuente y un fundamento dice POR QUE se hace el paso, y
# mezclarlos en el mismo archivo invita a redactar el segundo como si fuera lo
# primero -- que es la confusion que NOR-MEM-01 y NOR-HID-04 dejaron por
# escrito. `registro.construir()` los toma de alli.


# `CITAS` se materializa al FINAL del archivo (junto a AFIRMACIONES_NEGATIVAS):
# el bloque de ASTM A796 (N1) se define despues de este punto.

# LA LAMINA Nº 03 NO ACOTA NADA, y hay que decirlo en el registro porque esta
# cita es TENTADORA: es un plano, y un plano invita a leerle dimensiones. Sin
# esta afirmacion, antes o despues alguien la usara para respaldar un ancho,
# una altura, un espesor o una longitud de solado, y esa constante llevaria la
# etiqueta equivocada. La lamina respalda el TIPO, no el TAMAÑO.
SIN_COTAS_LAMINA_03 = AfirmacionNegativa(
    que_no_dice=("la Lamina Nº 03 no acota ninguna dimension: no da ancho, "
                 "altura, espesor ni longitud de solado"),
    ambito_barrido=("las TRES figuras de la pag. impresa 209 (PDF 212), "
                    "leidas sobre la pagina renderizada y barridas con "
                    "expresion regular sobre todo token con digito. El "
                    "resultado completo de ese barrido es ['209', '03'] -- el "
                    "folio y el numero de lamina --. Toda dimension esta "
                    "acotada como «VARIABLE» (nueve veces) o con literal "
                    "alfabetico «a», «b», «c» sin tabla de valores. El "
                    "contraste que demuestra que la ausencia es deliberada y "
                    "no un fallo del extractor: la Lamina Nº 04 (impresa 210, "
                    "PDF 213) SI acota -- 0.15m, 0.20m, 0.30m, 0.40m, 0.60m, "
                    "0.80 min., 1.00m --"),
    cita_id="MC_HHD.LAMINA_03")

# LA SECCION 12 NO TABULA LA COBERTURA DE UN CAJON DE CONCRETO, y hace falta
# decirlo EN EL REGISTRO porque la tentacion aqui no es una lamina sino una
# tabla que casi encaja: tiene fila de concreto, tiene cajon, y ninguna de las
# dos es la que hace falta -- la de concreto es de TUBO y la de cajon es
# METALICA --. La regla vinculante #9 de la Familia C mandaba traer «B'c/8»
# para el marco desde esa misma tabla, y se retiro en C7 por esto.
#
# TRES FALSOS AMIGOS, y el orden es de menos a mas peligroso. El primero es de
# titulo: `12.11.5.4—Minimum Cover for Precast Box Structures` esta en el
# articulo de los cajones, se titula «Minimum Cover» y su cuerpo entero es
# «The provisions of Article 5.10.1 shall apply» -- y el 5.10.1 es «Concrete
# Cover», recubrimiento de armadura --. El segundo es de NUMERO, y es peor
# porque el numero SI es una altura de relleno: las cuatro apariciones de
# «2.0 ft» en 12.11 son umbrales que CONMUTAN EL METODO de reparto de la carga
# de rueda, y las cuatro presuponen que existe la alcantarilla con menos de
# 2.0 ft encima. Leer cualquiera como «cobertura minima = 0.61 m» invierte el
# sentido de la frase. El tercero solo se ve renderizado: las Figuras
# 12.11.2.2.1-1 y -2 rotulan «LEVELING COURSE (FINE GRANULAR FILL MATERIAL
# 2" MIN.)», que es la cama BAJO el cajon y no cobertura encima.
SIN_CAJON_DE_CONCRETO_T12663 = AfirmacionNegativa(
    que_no_dice=("la Tabla 12.6.6.3-1 no tiene fila de alcantarilla CAJON DE "
                 "CONCRETO -- ni vaciada in situ ni prefabricada --, y el "
                 "Art. 12.11, que es el de los cajones de concreto, no fija "
                 "altura minima de cobertura de suelo ni se remite al "
                 "Art. 12.6.6.3"),
    ambito_barrido=(
        "las CATORCE filas de la tabla, leidas sobre la pagina RENDERIZADA "
        "(impresa 12-22, PDF 1660): sus dos filas de concreto dicen "
        "«Reinforced Concrete PIPE» y la unica que trae la palabra «box» es "
        "«Structural Plate Box Structures», que es METALICA y cuya celda de "
        "cobertura dice «1.4 ft. as specified in Article 12.9.1»: SI da "
        "cobertura, y ademas remite. ESTA FRASE DECIA «ni siquiera da "
        "cobertura» Y ERA FALSA SOBRE LA PROPIA PAGINA que este objeto existe "
        "para acreditar; lo encontro la auditoria adversarial de C7. El hecho "
        "negativo no cambia -- esa fila es metalica y no cubre a un marco de "
        "concreto --; lo que cambia es que se sostiene por lo que la fila ES y "
        "no por un vacio que no tiene. Mas el Art. 12.11 completo, "
        "«REINFORCED CONCRETE CAST-IN-PLACE AND PRECAST BOX CULVERTS AND "
        "REINFORCED CAST-IN-PLACE ARCHES», SIETE paginas impresas de la 12-68 "
        "a la 12-74, delimitadas por encabezado impreso (12.10.5 cierra "
        "antes; 12.12 «THERMOPLASTIC PIPES» abre en la 12-74) y leidas las "
        "siete renderizadas ademas del volcado. Censo dentro de ese ambito, "
        "insensible a mayusculas: «12.6.6» 0 veces, «12.6.6.3» 0, «table "
        "12.6.6.3-1» 0, «fill height» 0, «depth of fill» 0, «soil cover» 0, "
        "«earth cover» 0; «minimum cover» 1, y es el titulo del falso amigo "
        "12.11.5.4. «cover» 3: ese titulo mas DOS de los cuatro umbrales de "
        "metodo de «2.0 ft». «fill» 7: los otros DOS de esos umbrales, TRES "
        "«backfill» del num. 12.11.2.2.1 --donde H es «depth of backfill», la "
        "VARIABLE de la carga de tierra, sin cota inferior-- y el «compacted "
        "fill» / «uncompacted fill» del C12.11.2.2.1. EL REPARTO ANTERIOR "
        "DECIA «los cuatro umbrales y cinco backfill», que suma NUEVE y no "
        "los SIETE que el propio censo declara: lo encontro la auditoria "
        "adversarial de C7 remidiendo, y es el defecto propio de este objeto "
        "-- un barrido cuyo desglose no cuadra no acredita el hecho negativo, "
        "aunque los totales sean correctos, que lo eran --. Lo unico que "
        "remite hacia fuera "
        "es el paraguas generico del 12.11.1 -- «Designs shall conform to "
        "applicable Articles of these Specifications, except as provided "
        "otherwise herein» --, que no es la remision especifica a 12.6.6.3. "
        "Paginacion medida sobre encabezados impresos: pagina PDF 1-based = "
        "folio + 1638 (en indice 0-based, + 1637); comprobada en los folios "
        "12-67, 12-68, 12-69 y 12-74"),
    cita_id="AASHTO_LRFD_9.T12.6.6.3-1")

# EL EG-2013 NO LE DA PARTIDA PROPIA AL CAJON, y esta afirmacion es la que
# autoriza a este proyecto a decir «se paga por 503 + 504» en vez de buscar un
# numeral que no existe. Es exactamente el mismo argumento que
# `M9.condicion_normativa_cabezal` ya hacia para los cabezales -- «NO tienen
# partida con numeral propio: se pagan bajo el volumen de concreto y el
# acero» --, y ahora con el barrido escrito en vez de supuesto.
SIN_PARTIDA_DE_CAJON_EG2013 = AfirmacionNegativa(
    que_no_dice=("el EG-2013 no tiene ninguna Seccion ni ninguna partida de "
                 "alcantarilla de CAJON de concreto: ni vaciada in situ ni "
                 "prefabricada"),
    ambito_barrido=(
        "las 1282 paginas del PDF, con el desfase medido sobre el encabezado "
        "impreso en 1268 de ellas -- pagina impresa = PDF (1-based) - 8, sin "
        "excepciones --. Dos barridos. "
        "EL PRIMERO, las Secciones del Capitulo V: existen de la 501 a la 514 "
        "y ninguna mas, y las cuatro de alcantarilla se titulan «Tuberia de "
        "concreto simple» (505, impresa 949), «Tuberia de concreto reforzado» "
        "(506, impresa 959), «Tuberia metalica corrugada» (507, impresa 969) "
        "y «Tuberia de polietileno de alta densidad» (508, impresa 981). Las "
        "cuatro empiezan por «Tuberia». "
        "EL SEGUNDO, por cadena sobre el documento entero, sin tildes y en "
        "minusculas: «box» 0 veces, «box culvert» 0, «ponton» 0, «alcantarilla "
        "de cajon» 0, «marco de concreto» 0, «seccion rectangular» 0, "
        "«vaciado in situ» 0; «cajon» CUATRO, y tres son falsos amigos -- el "
        "«cajon mezclador» de la Sec. 420 (impresa 536), los «cajones» de "
        "cimentacion de la Tabla 503-08 (impresa 915) y las «alcantarillas de "
        "cajon de PIEDRA» de la Sec. 601 Mamposteria (impresa 1045) --. La "
        "cuarta es la unica real y es EG2013.503.10h#CAJON. "
        "Y EL INDICE OFICIAL DE PARTIDAS, Tabla Anexo 2-1 (impresa 1273): el "
        "Capitulo 5 lista 501.A-D, 502.A, 503.A «Concreto estructural» (m3), "
        "504.A «Acero de refuerzo» (kg), 505.A a 508.A -- las cuatro "
        "«Tuberia... de diametro interior» en metro lineal -- y 509.A en "
        "adelante. Ninguna partida de cajon, marco ni box."),
    cita_id="EG2013.503.10h#CAJON")



# ===========================================================================
# ASTM A796/A796M-13 -- la practica de diseño estructural del TMC (N1).
# TODO por IMAGEN: la Fuente declara `texto_extraible=False` (capa de texto
# duplicada e intercalada a mitad de palabra), y cada cita se leyo sobre la
# pagina renderizada a escala 2.5 y sobre recortes a escala 5.0.
#
# LO QUE ESTAS CITAS ACREDITAN, Y LO QUE NO. NOR-PRO-04(2) y DIS-HR-A807
# esperaban de esta fuente «la tabla de calibre por altura de cobertura».
# LEIDA ENTERA (21 paginas PDF; la impresa 1 falta): esa tabla NO EXISTE en
# A796. La norma es una PRACTICA: el espesor es la SALIDA de un procedimiento
# (num. 7 a 9, con las Tablas 2 a 35 como catalogo de espesores y
# propiedades seccionales) y la cobertura minima sale de las ecs. (13) a
# (16) del num. 11.1 con dos pisos absolutos. Las citas de abajo son las que
# sostienen exactamente eso -- y la del num. 22.1, que es la que cierra la
# discrepancia: A807/A807M es practica de INSTALACION.
# ===========================================================================

ASTM_A796_5_1 = _cita(
    id="ASTM_A796.5.1",
    fuente_id="ASTM_A796",
    numeral="5.1",
    titulo_numeral="Basis of Design",
    pagina_impresa="2",
    pagina_pdf=2,
    texto_literal=Verbatim(
        texto=("The safety factors and other specific quantitative recom-"
               "mendations herein represent generally accepted design prac-"
               "tice. The design engineer should, however, determine that "
               "these recommendations meet particular project needs."),
        pagina_pdf=2),
    # DEFINICION del caracter del documento entero: se declara «practica de
    # diseño generalmente aceptada», y remite al ingeniero la decision de si
    # sirve al proyecto. Es la razon de que todo lo que salga de esta fuente
    # sea [C] y no [N]: no es norma peruana ni la adopta ninguna.
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Los dos guiones de fin de renglon («recom-mendations», "
          "«prac-tice») se transcriben como los imprime la columna. El "
          "encabezado «5. Basis of Design» esta al pie de la columna derecha "
          "de la PDF 2 y el numeral 5.2 sigue en la PDF 3."),
)

ASTM_A796_7_1 = _cita(
    id="ASTM_A796.7.1",
    fuente_id="ASTM_A796",
    numeral="7.1",
    titulo_numeral="Design Method",
    pagina_impresa="3",
    pagina_pdf=3,
    texto_literal=Verbatim(
        texto=("Strength requirements for wall strength, buckling strength, "
               "and seam strength may be determined by either the allowable "
               "stress design (ASD) method presented in Section 8, or the "
               "load and resistance factor design (LRFD) method presented in "
               "Section 9. Additionally, the design considerations in other "
               "paragraphs shall be followed for either design method."),
        pagina_pdf=3),
    # PERMISO («may be determined by either»): la practica admite dos
    # metodos y el proyecto tendra que ELEGIR uno el dia que implemente
    # Fase 8. Esa eleccion es un [A] que hoy no existe y no se inventa aqui.
    caracter=Caracter.PERMISO,
    metodo=IMAGEN,
    sesion=N1,
)

ASTM_A796_8_1_1_2_SELECCION = _cita(
    id="ASTM_A796.8.1.1.2#SELECCION",
    fuente_id="ASTM_A796",
    numeral="8.1.1.2",
    titulo_numeral="Design by ASD Method",
    pagina_impresa="3",
    pagina_pdf=3,
    jerarquia_numeral=("8.", "8.1.1", "Required Wall Area:"),
    texto_literal=Verbatim(
        texto=("Select from Table 2, Table 4, Table 6, Table 8, Table 10, "
               "Table 12, Table 14, Table 16, Table 18, Table 20, Table 22, "
               "Table 24, Table 26, Table 28, Table 30, Table 32, or Table 34 "
               "[Table 3, Table 5, Table 7, Table 9, Table 11, Table 13, "
               "Table 15, Table 17, Table 19, Table 21, Table 23, Table 25, "
               "Table 27, Table 29, Table 31, Table 33, or Table 35] a wall "
               "thickness equal to or greater than the required wall area "
               "(A)."),
        pagina_pdf=3),
    # EXIGENCIA, y es LA frase de esta fuente para NOR-PRO-04(2): el
    # calibre (espesor) se SELECCIONA de las tablas de propiedades
    # seccionales por el area de pared REQUERIDA que sale del calculo -- no
    # se lee de una tabla por altura de cobertura, que no existe --.
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota=("El 8.1.1.2 no lleva titulo propio: cuelga de «8.1.1 Required "
          "Wall Area:» bajo «8. Design by ASD Method», y abre con «Determine "
          "the required wall cross-sectional area. The safety factor (SF) on "
          "wall area is 2.» y la ec. (4), A = T(SF)/f_y -- el SF = 2 no lleva "
          "cita propia porque ningun objeto del registro lo consumiria hoy "
          "(T4); lo consumira la sesion que implemente el procedimiento --. "
          "La lista entre corchetes es la de las tablas en unidades SI, "
          "que son las que este registro transcribe para las siete "
          "corrugaciones de ASTM_A760.T1 (Tablas 3, 5, 7, 9, 11, 15 y 17). "
          "Los dos ultimos renglones de la frase se imprimen SOLAPADOS en el "
          "render («15, Table 17, ... Table 27,» sobre «Table 29, Table 31, "
          "Table 33, or Table 35]»): es la capa de texto duplicada del "
          "ejemplar, y se leyo a escala 5.0."),
)

ASTM_A796_6_2_2_1 = _cita(
    id="ASTM_A796.6.2.2.1",
    fuente_id="ASTM_A796",
    numeral="6.2.2.1",
    titulo_numeral="Live Loads Under Highway",
    pagina_impresa="3",
    pagina_pdf=3,
    jerarquia_numeral=("6.", "Loads", "6.2.2", "Live Loads"),
    texto_literal=Verbatim(
        texto=("Live load pressures for H20 highway loadings, including "
               "impact effects, are:"),
        pagina_pdf=3),
    # DEFINICION: la frase introduce la tabulacion de presion de carga viva
    # por altura de cobertura (ASTM_A796.6.2.2.1 en tablas.py). El caracter
    # vinculante lo pone el num. 6.2 («loads are defined as follows»), no
    # este renglon.
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Es una tabulacion SIN TITULO ni numero de tabla, impresa en el "
          "cuerpo del numeral: la TablaNormativa toma como titulo literal el "
          "encabezado del numeral, con el precedente de E060.7.7.1. El "
          "num. 6.2.2.3 (misma pagina, sin titulo propio) añade «Values for "
          "intermediate covers shall be interpolated.»: es el renglon que "
          "hace de la tabulacion una BANDA y no escalones, y la "
          "Interpretacion de la tabla lo recoge. No lleva cita propia "
          "porque ningun objeto del registro la consumiria hoy (T4)."),
)

ASTM_A796_10_2 = _cita(
    id="ASTM_A796.10.2",
    fuente_id="ASTM_A796",
    numeral="10.2",
    titulo_numeral="Handling and Installation",
    pagina_impresa="4",
    pagina_pdf=4,
    jerarquia_numeral=("10.",),
    texto_literal=Verbatim(
        texto=("For curve and tangent corrugated pipe installed in a trench "
               "cut in undisturbed soil, the flexibility factor shall not "
               "exceed the following:"),
        pagina_pdf=4),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota=("El 10.2 no lleva titulo propio: cuelga de «10. Handling and "
          "Installation». FF = s²/EI es la ec. (12) del 10.1. Los limites "
          "de FF (10.2 a 10.8) son el sitio de la practica donde la RIGIDEZ "
          "MINIMA por perfil esta tabulada -- 10.2/10.3 para plancha "
          "corrugada, 10.4 a 10.6 para costilla espiral (con o sin "
          "insertos), 10.7 compuesta, 10.8 costilla cerrada --: es lo que, "
          "en la practica norteamericana, gobierna el calibre minimo por "
          "diametro en coberturas bajas."),
)

ASTM_A796_10_3 = _cita(
    id="ASTM_A796.10.3",
    fuente_id="ASTM_A796",
    numeral="10.3",
    titulo_numeral="Handling and Installation",
    pagina_impresa="4",
    pagina_pdf=4,
    jerarquia_numeral=("10.",),
    texto_literal=Verbatim(
        texto=("For curve and tangent corrugated pipe installed in an "
               "embankment or fill section and for all multiple lines of "
               "pipe, the flexibility factor shall not exceed the following:"),
        pagina_pdf=4),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota="Sin titulo propio: cuelga de «10. Handling and Installation».",
)

ASTM_A796_10_4 = _cita(
    id="ASTM_A796.10.4",
    fuente_id="ASTM_A796",
    numeral="10.4",
    titulo_numeral="Handling and Installation",
    pagina_impresa="4",
    pagina_pdf=4,
    jerarquia_numeral=("10.",),
    texto_literal=Verbatim(
        texto=("For ribbed pipes and ribbed pipes with metallic-coated "
               "inserts, installed in a trench cut in undisturbed soil and "
               "provided with a soil envelope meeting the requirements of "
               "18.2.3 to minimize compactive effort, the flexibility factor "
               "shall not exceed the following:"),
        pagina_pdf=4),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Sin titulo propio: cuelga de «10. Handling and Installation». "
          "Aplica a los TRES perfiles de costilla espiral de ASTM_A760.T1 "
          "(Tablas 11, 15 y 17): lo señalo la auditoria adversarial de N1, "
          "que refuto la primera version de este bloque, donde 10.4 a 10.6 "
          "se habian dejado fuera como si fueran de otro producto."),
)

ASTM_A796_10_5 = _cita(
    id="ASTM_A796.10.5",
    fuente_id="ASTM_A796",
    numeral="10.5",
    titulo_numeral="Handling and Installation",
    pagina_impresa="4",
    pagina_pdf=4,
    jerarquia_numeral=("10.",),
    texto_literal=Verbatim(
        texto=("For ribbed pipes and ribbed pipes with metallic-coated "
               "inserts, installed in a trench cut in undisturbed soil and "
               "where the soil envelope does not meet the requirements of "
               "18.2.3, the flexibility factor shall not exceed the "
               "following:"),
        pagina_pdf=4),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota="Sin titulo propio: cuelga de «10. Handling and Installation».",
)

ASTM_A796_10_6 = _cita(
    id="ASTM_A796.10.6",
    fuente_id="ASTM_A796",
    numeral="10.6",
    titulo_numeral="Handling and Installation",
    pagina_impresa="4",
    pagina_pdf=4,
    jerarquia_numeral=("10.",),
    texto_literal=Verbatim(
        texto=("For ribbed pipes and ribbed pipes with metallic-coated "
               "inserts, installed in an embankment or fill section, the "
               "flexibility factor shall not exceed the following:"),
        pagina_pdf=4),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Sin titulo propio: cuelga de «10. Handling and Installation». "
          "El 10.7 (misma pagina) añade que para tuberia COMPUESTA de "
          "costilla los limites de 10.4 a 10.6 «shall be multiplied by "
          "1.05», y el 10.8 tabula la costilla cerrada; ninguno de los dos "
          "productos esta en ASTM_A760.T1 y no se transcriben."),
)

ASTM_A796_11_1_DEF = _cita(
    id="ASTM_A796.11.1#DEF",
    fuente_id="ASTM_A796",
    numeral="11.1",
    titulo_numeral="Minimum Cover Design",
    pagina_impresa="5",
    pagina_pdf=5,
    jerarquia_numeral=("11.", "Minimum Cover Requirements"),
    texto_literal=Verbatim(
        texto=("Where pipe is to be placed under roads, streets, or "
               "freeways, the minimum cover require-ments shall be "
               "determined. Minimum cover (Hmin) is defined as the distance "
               "from the top of the pipe to the top of rigid pavement or to "
               "the top of subgrade for flexible pavement."),
        pagina_pdf=5),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("«require-ments» lleva el guion de fin de renglon como lo imprime "
          "la columna, con el mismo criterio que «recom-mendations» en la "
          "cita 5.1. «Hmin» se imprime con el «min» en subindice; se "
          "transcribe en linea. La MISMA definicion (a la subrasante en pavimento "
          "flexible, a la cara superior del pavimento rigido) es la de la "
          "variable h del num. 4.1. Sigue la tabulacion de cargas por eje "
          "(ASTM_A796.11.1 en tablas.py) y las ecs. (13) a (16), que dan "
          "Hmin en funcion de raiz((AL)d/EI) y del diametro S: 0.55·S·raiz(…) "
          "entre 0.23 y 0.45, S/8 por debajo de 0.23 y S/4 por encima de "
          "0.45. Las ecuaciones no se transcriben como Verbatim porque son "
          "formulas compuestas; quien las implemente las lee de la pagina."),
)

ASTM_A796_11_1_PISOS = _cita(
    id="ASTM_A796.11.1#PISOS",
    fuente_id="ASTM_A796",
    numeral="11.1",
    titulo_numeral="Minimum Cover Design",
    pagina_impresa="5",
    pagina_pdf=5,
    jerarquia_numeral=("11.", "Minimum Cover Requirements"),
    texto_literal=Verbatim(
        texto=("In all cases, Hmin is never less than 1 ft [300 mm]. "
               "Additionally, for pipe with a specified thickness less than "
               "0.052 in. [1.32 mm], Hmin shall not be less than 2 ft "
               "[600 mm]."),
        pagina_pdf=5),
    # EXIGENCIA, y es la UNICA cobertura minima NUMERICA que la fuente
    # escribe para tuberia bajo carretera: dos pisos absolutos que dependen
    # del ESPESOR, no de la altura de relleno. Es el unico sitio de la norma
    # donde calibre y cobertura minima se cruzan, y lo hacen al reves de lo
    # que NOR-PRO-04(2) esperaba: no «calibre por cobertura» sino «cobertura
    # por calibre», y solo en el escalon de 1.32 mm.
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota=("«Hmin» con el «min» en subindice, transcrito en linea. Los 300 mm "
          "coinciden con los 12 in de la Tabla 12.6.6.3-1 de AASHTO LRFD para "
          "el metal corrugado (AASHTO_LRFD_9.T12.6.6.3-1), y la ec. (15) "
          "(Hmin = S/8 para tuberia rigida) coincide con el S/8 de esa misma "
          "fila: las dos fuentes son consistentes y NO se abre discrepancia. "
          "El escalon de 600 mm para espesor < 1.32 mm NO esta en AASHTO. "
          "El num. 11.4 «Construction Loads» (misma pagina) añade una "
          "cobertura minima DE OBRA, bajo equipo pesado: «The minimum cover "
          "shall be 4 ft [1.2 m] unless field conditions and experience "
          "justify modification.»; es exigencia de construccion, no de "
          "servicio, y no lleva cita propia porque ningun objeto del "
          "registro la consumiria hoy (T4)."),
)

ASTM_A796_17_1 = _cita(
    id="ASTM_A796.17.1",
    fuente_id="ASTM_A796",
    numeral="17.1",
    titulo_numeral="Materials",
    pagina_impresa="5",
    pagina_pdf=5,
    jerarquia_numeral=("17.",),
    texto_literal=Verbatim(
        texto=("Acceptable pipe materials, methods of manufacture, and "
               "quality of finished pipe are given in Specifications "
               "A760/A760M, A761/A761M, A762/A762M, A978/A978M, "
               "A1019/A1019M, and A1042/A1042M."),
        pagina_pdf=5),
    # DEFINICION: cierra el circuito con la norma de producto que SI esta en
    # normas/ (ASTM_A760, de doble designacion con AASHTO_M36). La practica
    # diseña; A760 fabrica.
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
)

ASTM_A796_22_1 = _cita(
    id="ASTM_A796.22.1",
    fuente_id="ASTM_A796",
    numeral="22.1",
    titulo_numeral="Construction and Installation",
    pagina_impresa="6",
    pagina_pdf=6,
    jerarquia_numeral=("22.",),
    texto_literal=Verbatim(
        texto=("The construction and installation of corrugated steel pipe "
               "and pipe-arches and steel structural plate pipe, pipe-"
               "arches, arches, and underpasses shall conform to Practice "
               "A798/A798M or A807/A807M."),
        pagina_pdf=6),
    # EXIGENCIA, y es LA cita de DIS-HR-A807: la UNICA mencion de A807 en
    # las 20 paginas CON CONTENIDO del ejemplar (barrido por texto: «A807»
    # aparece en una sola pagina, la PDF 6, y es esta; la impresa 1, que
    # falta, es la que lleva la lista alfabetica del num. 2.1 donde A807
    # figuraria como norma referenciada), y la nombra «Practice» de
    # INSTALACION junto a A798/A798M. A807/A807M es, por tanto, una norma
    # real -- la que EG-2013 507.05/.06/.08 invocan para terreno base,
    # solado y relleno -- y NO la norma del calibre, que aqui se determina
    # por el num. 8/9 y no se remite a ninguna parte.
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=N1,
    nota=("El guion de «pipe-arches» partido a fin de renglon («pipe- / "
          "arches») es el propio guion de la palabra, no uno de corte, y se "
          "transcribe como «pipe-arches»."),
)

# Las siete tablas SI de propiedades seccionales que este registro
# transcribe: una por cada corrugacion de ASTM_A760.T1. Cada cita lleva el
# titulo impreso de la tabla como titulo y como literal (precedente:
# ASTM_A760.T1, AASHTO_M36.T6). La «NOTE 1» de las paginas 7, 8 y 9 esta
# impresa bajo las gemelas IMPERIALES (Tables 2, 4 y 6), no bajo las SI, y
# por eso no viaja con estas; solo la Table 9 la imprime bajo su propio
# titulo y la lleva como texto_previo.

ASTM_A796_T3 = _cita(
    id="ASTM_A796.T3",
    fuente_id="ASTM_A796",
    numeral="Table 3",
    titulo_numeral=("TABLE 3 Sectional Properties of Corrugated Steel Sheets "
                    "for Corrugation: 38 by 6.5 mm (Helical) [SI Units]"),
    pagina_impresa="7",
    pagina_pdf=7,
    texto_literal=Verbatim(
        texto=("TABLE 3 Sectional Properties of Corrugated Steel Sheets for "
               "Corrugation: 38 by 6.5 mm (Helical) [SI Units]"),
        pagina_pdf=7),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Gemela SI de la Table 2 (1 1/2 by 1/4 in.), impresa debajo de "
          "ella en la misma pagina. La figura acotada (Pitch = 38.1 mm, "
          "Depth = 6.35 mm, radio 7.14 mm) no se transcribe: es dibujo."),
)

ASTM_A796_T5 = _cita(
    id="ASTM_A796.T5",
    fuente_id="ASTM_A796",
    numeral="Table 5",
    titulo_numeral=("TABLE 5 Sectional Properties of Corrugated Steel Sheets "
                    "for Corrugation: 68 by 13 mm (Annular or Helical) "
                    "[SI Units]"),
    pagina_impresa="8",
    pagina_pdf=8,
    texto_literal=Verbatim(
        texto=("TABLE 5 Sectional Properties of Corrugated Steel Sheets for "
               "Corrugation: 68 by 13 mm (Annular or Helical) [SI Units]"),
        pagina_pdf=8),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Gemela SI de la Table 4 (2 2/3 by 1/2 in.). Es la corrugacion "
          "estandar de la mayor parte de los diametros de ASTM_A760.T1. Los "
          "subencabezados de remaches («8-mm Rivets», «10-mm Rivets») se "
          "imprimen SOLAPADOS con «Single/Double» en el render por la capa "
          "duplicada del ejemplar; se leyeron a escala 8.0."),
)

ASTM_A796_T7 = _cita(
    id="ASTM_A796.T7",
    fuente_id="ASTM_A796",
    numeral="Table 7",
    titulo_numeral=("TABLE 7 Sectional Properties of Corrugated Steel Sheets "
                    "for Corrugation: 75 by 25 mm (Annular or Helical) "
                    "[SI Units]"),
    pagina_impresa="9",
    pagina_pdf=9,
    texto_literal=Verbatim(
        texto=("TABLE 7 Sectional Properties of Corrugated Steel Sheets for "
               "Corrugation: 75 by 25 mm (Annular or Helical) [SI Units]"),
        pagina_pdf=9),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Gemela SI de la Table 6 (3 by 1 in.). ERRATA DE LA FUENTE, "
          "transcrita tal cual: el encabezado del momento de inercia imprime "
          "«I, mm4/m» donde las otras seis tablas imprimen «mm4/mm»; los "
          "valores (112.94 a 411.04) son del orden de mm4/mm, como en la "
          "Table 9 de la corrugacion vecina."),
)

ASTM_A796_T9 = _cita(
    id="ASTM_A796.T9",
    fuente_id="ASTM_A796",
    numeral="Table 9",
    titulo_numeral=("TABLE 9 Sectional Properties of Corrugated Steel Sheets "
                    "for Corrugation: 125 by 25 mm (Helical) [SI Units]"),
    pagina_impresa="10",
    pagina_pdf=10,
    texto_literal=Verbatim(
        texto=("TABLE 9 Sectional Properties of Corrugated Steel Sheets for "
               "Corrugation: 125 by 25 mm (Helical) [SI Units]"),
        pagina_pdf=10),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Gemela SI de la Table 8 (5 by 1 in.), que esta al pie de la PDF "
          "9; la Table 9 abre la PDF 10 con su propia «NOTE 1»."),
)

ASTM_A796_T11 = _cita(
    id="ASTM_A796.T11",
    fuente_id="ASTM_A796",
    numeral="Table 11",
    titulo_numeral=("TABLE 11 Sectional Properties of Spiral Rib Pipe for "
                    "19 mm Wide by 19 mm Deep Rib with a Spacing of 190 mm "
                    "Center to Center (Helical) [SI Units]"),
    pagina_impresa="11",
    pagina_pdf=11,
    texto_literal=Verbatim(
        texto=("TABLE 11 Sectional Properties of Spiral Rib Pipe for 19 mm "
               "Wide by 19 mm Deep Rib with a Spacing of 190 mm Center to "
               "Center (Helical) [SI Units]"),
        pagina_pdf=11),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Gemela SI de la Table 10 (3/4 by 3/4 by 7 1/2 in.), que esta al "
          "pie de la PDF 10 y cuya nota A se imprime al ABRIR la PDF 11. La "
          "Table 12/13 que sigue («Ribbed Pipe with Inserts») es otro "
          "producto y no se transcribe."),
)

ASTM_A796_T15 = _cita(
    id="ASTM_A796.T15",
    fuente_id="ASTM_A796",
    numeral="Table 15",
    titulo_numeral=("TABLE 15 Sectional Properties of Spiral Rib Pipe for "
                    "19 mm Wide by 25 mm Deep Rib with a Spacing of 292 mm "
                    "Center to Center (Helical) [SI Units]"),
    pagina_impresa="12",
    pagina_pdf=12,
    texto_literal=Verbatim(
        texto=("TABLE 15 Sectional Properties of Spiral Rib Pipe for 19 mm "
               "Wide by 25 mm Deep Rib with a Spacing of 292 mm Center to "
               "Center (Helical) [SI Units]"),
        pagina_pdf=12),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota=("Gemela SI de la Table 14 (3/4 by 1 by 11 1/2 in.). SU NOTA A NO "
          "ESTA EN SU PAGINA: la PDF 12 termina en la ultima fila (2.77) y "
          "el renglon «A Net effective properties at full yield stress.» "
          "se imprime al ABRIR la PDF 13, antes de la Table 16. La "
          "TablaNormativa lo transcribe con pagina_pdf=13 por esa razon."),
)

ASTM_A796_T17 = _cita(
    id="ASTM_A796.T17",
    fuente_id="ASTM_A796",
    numeral="Table 17",
    titulo_numeral=("TABLE 17 Sectional Properties of Spiral Rib Pipe for "
                    "19 mm Wide by 25 mm Deep Rib with a Spacing of 216 mm "
                    "Center to Center (Helical) [SI Units]"),
    pagina_impresa="13",
    pagina_pdf=13,
    texto_literal=Verbatim(
        texto=("TABLE 17 Sectional Properties of Spiral Rib Pipe for 19 mm "
               "Wide by 25 mm Deep Rib with a Spacing of 216 mm Center to "
               "Center (Helical) [SI Units]"),
        pagina_pdf=13),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=N1,
    nota="Gemela SI de la Table 16 (3/4 by 1 by 8 1/2 in.).",
)

# LO QUE A796 NO TIENE, dicho como afirmacion negativa con su ambito, porque
# es lo que NOR-PRO-04(2) y DIS-HR-A807 daban por hecho y lo que autoriza a
# decir que la mitad TMC de 'clases_producto_por_relleno' no se cierra
# transcribiendo.
SIN_TABLA_CALIBRE_POR_COBERTURA_A796 = AfirmacionNegativa(
    que_no_dice=("ASTM A796/A796M-13 no contiene ninguna tabla de calibre "
                 "(espesor) de TMC por altura de cobertura, ni de altura "
                 "maxima de relleno por calibre: el espesor es la SALIDA del "
                 "procedimiento de los num. 7 a 10 (area de pared requerida "
                 "con SF = 2, pandeo, costura, factor de flexibilidad) "
                 "elegida de las Tablas 2 a 35, y la cobertura minima sale "
                 "de las ecs. (13) a (16) del num. 11.1 mas dos pisos "
                 "absolutos"),
    ambito_barrido=(
        "las 21 paginas PDF del ejemplar (la impresa 1 falta: es la PDF 1 "
        "en blanco), leidas RENDERIZADAS de la 2 a la 7 -- todo el "
        "articulado, num. 2.1 a 24.1 -- y de la 7 a la 21 por los titulos "
        "de las 35 tablas: la TABLE 1 «Resistance Factors for LRFD Design» "
        "(PDF 3, factores phi) y las 34 restantes, TABLE 2 a TABLE 35, que "
        "son todas «Sectional Properties of ...» (planchas corrugadas, "
        "costilla espiral, costilla con insertos, compuestas, costilla "
        "cerrada y planchas estructurales); ninguna cruza espesor con "
        "altura de cobertura -- la PDF 15, "
        "girada, con las Tablas 20 y 21, se leyo entera por imagen porque "
        "su capa de texto no devuelve los titulos --. Censo por texto sobre "
        "la capa duplicada, que localiza palabras sueltas pero NO todas sus "
        "apariciones (la copia partida a mitad de palabra las esconde), "
        "contrastado por imagen: «height of cover» 1 pagina por texto (la "
        "PDF 6, num. 18.2.4) y TRES por imagen (PDF 2, la variable h del "
        "4.1; PDF 3, las cabeceras de las tabulaciones del 6.2.2; PDF 6, "
        "num. 18.2.4 y 18.3); «minimum cover» 3 paginas por texto y por "
        "imagen (PDF 5, num. 11; PDF 6, num. 18.3; PDF 7, keywords); "
        "«maximum cover» 0, «gage» 0, «gauge» 0, «A807» 1 (la PDF 6, num. "
        "22.1). El num. 18.3 dice que la altura maxima de cobertura de un "
        "ARCO-TUBO la fija a menudo la capacidad portante del suelo en la "
        "esquina, no una tabla. El unico cruce "
        "espesor/cobertura es el escalon del 11.1: espesor < 1.32 mm => "
        "Hmin >= 600 mm"),
    cita_id="ASTM_A796.8.1.1.2#SELECCION")

# LAS DOS DE LA TRADUCCION NO OFICIAL DE M 294-11 (N2). Las dos se afirman
# sobre la TRADUCCION, y el ambito lo dice: lo que el original diga en
# ingles no se ha leido. Son las dos cosas que el proyecto venia afirmando o
# necesitando del HDPE sin fuente: que la norma de producto no clasifica por
# altura de relleno (lo afirmaba 'clases_producto_por_relleno') y que no
# fija el diametro exterior (lo necesitaba 'espesor_pared_conducto').
SIN_CLASE_POR_ALTURA_M294_TRAD = AfirmacionNegativa(
    que_no_dice=("AASHTO M 294-11 (traducción no oficial) no contiene "
                 "ninguna tabla de clase, calibre ni rigidez por altura de "
                 "relleno o de cobertura: el num. 1.4 excluye expresamente "
                 "camas, relleno y carga de cubierta de tierra y remite el "
                 "diseño estructural a AASHTO LRFD Seccion 12. Lo unico que "
                 "tabula por diametro es la rigidez MINIMA de tuberia al 5 % "
                 "de deflexion (7.4), que es un requisito de producto, no una "
                 "seleccion por altura"),
    ambito_barrido=(
        "las 17 hojas del ejemplar, leidas ENTERAS por texto (extraible y "
        "limpio) y las hojas 1, 5 y 8 tambien renderizadas: doce numerales "
        "de nivel 1 (Ámbito, Documentos mencionados, Terminología, "
        "Clasificación, Información para órdenes de compra, Materiales, "
        "Requerimientos, Acondicionamiento, Método de ensayo, Inspección y "
        "re-ensayo, Marcado, Aseguramiento de calidad), la Tabla 1 "
        "(perforaciones Clase 1), las tabulaciones de 7.2.2 (espesor de "
        "pared) y 7.4 (rigidez), el Anexo A1 y el Apéndice X1. Barrido por "
        "palabra: «cobertura» 0 apariciones; «relleno» 5, todas en 1.4 (la "
        "exclusion) o en 7.9.1 y 7.9.2 (el material de relleno frente a las "
        "uniones, no una altura); «cubierta» 2 (1.4 y «la tubería ... "
        "cubierta en esta especificación», 4.1); «altura» 3 (la H de las "
        "perforaciones en la Tabla 1 y 7.3.1, y la altura de caida del "
        "martillo en 9.3); «clase» solo para perforaciones y para la "
        "clasificacion de celda de la resina"),
    cita_id="AASHTO_M294_TRAD.1.4")

SIN_DIAMETRO_EXTERIOR_M294_TRAD = AfirmacionNegativa(
    que_no_dice=("AASHTO M 294-11 (traducción no oficial) no fija el diametro "
                 "exterior ni la altura del perfil corrugado de ningun tamaño "
                 "nominal: el tamaño nominal es el diametro INTERIOR (7.2.1), "
                 "la tolerancia es del diametro interior (7.2.3), y el 7.2.2 "
                 "tabula el espesor minimo de la pared interior lisa (Tipo S) "
                 "o de las dos paredes (Tipo D), no la altura del perfil. El "
                 "t que separa D interior de D exterior no sale de esta fuente"),
    ambito_barrido=(
        "las 17 hojas del ejemplar, por texto: «diámetro exterior» y "
        "«diámetro externo» dan cero apariciones; «exterior» aparece 7 veces "
        "(3.9 dos veces, 4.1.1, 4.1.3, 7.2.2, 9.4.2 y 9.7) y «externa/"
        "externo» 10, nombrando una pared, un valle, una carga, una grieta "
        "(3.8), unas fuerzas (9.6.3) o un laboratorio (A1.1), nunca una "
        "dimension; «espesor» aparece 5 veces (6 con «espesores»), en 7.2.2, "
        "en la Nota 4 de 9.4 (espesor de la probeta) y en 9.6.4; «perfil» "
        "7 (1.4, el titulo de T 341 en 2.1, 6.1.1, dos en 7.7 y dos en "
        "9.4.2), ninguna con una altura -- el 1.4 remite al fabricante «el "
        "detalle de la seción del perfil de la pared», que es exactamente "
        "el dato que la norma no fija --. Recuentos del verificador-normativo "
        "de N2 por palabra entera, sin distinguir mayusculas"),
    cita_id="AASHTO_M294_TRAD.7.2.2")

# El censo de afirmaciones negativas va al FINAL del archivo a proposito: la
# ultima (A796, N1) se define tras el bloque de esa fuente, y las dos de N2
# tras el de la suya.
AFIRMACIONES_NEGATIVAS = (SIN_HDPE_T09, SIN_TMC_NI_HDPE_T10,
                          SIN_BORDE_LIBRE_DE_CANAL,
                          SIN_TABLAS_HEQ_EN_MP, SIN_COTAS_LAMINA_03,
                          SIN_CAJON_DE_CONCRETO_T12663,
                          SIN_PARTIDA_DE_CAJON_EG2013,
                          SIN_TABLA_CALIBRE_POR_COBERTURA_A796,
                          SIN_CLASE_POR_ALTURA_M294_TRAD,
                          SIN_DIAMETRO_EXTERIOR_M294_TRAD)


# ===========================================================================
# EXT-6 -- DG-2018 (desfase +1, medido en 284 de 285 paginas)
#
# LO QUE EL PROYECTO LE PIDE AL DG-2018, y solo eso: el requisito JURIDICO
# de V5 --- que el remanso quede dentro del derecho de via --- tiene aqui su
# definicion (304.07.01, por remision al RNGIV) y su PISO de ancho (Tabla
# 304.09 por clase de carretera, mas 5.00 m «del borde mas alejado de las
# obras de drenaje», 304.07.02). Lo que NO tiene: ninguna condicion
# hidraulica. El 304.07 no dice cuanto puede remansar una alcantarilla ni
# como se calcula la extension del embalse; ese metodo sigue siendo [A] del
# proyectista ('remanso_derecho_via') y el ancho de ESTE corredor un dato de
# sitio que hoy no llega ('ancho_derecho_via_m'). Por eso F5.V5 sigue en
# SIN_FUNDAMENTO con la razon corregida (EXT-N-02, EXT-N-04).
# ===========================================================================

DG2018_304_07_01 = _cita(
    id="DG2018.304.07.01",
    fuente_id="DG2018",
    numeral="304.07.01",
    titulo_numeral="Generalidades",
    jerarquia_numeral=("304.07 Derecho de Vía o faja de dominio",),
    pagina_impresa="198",
    pagina_pdf=199,
    texto_literal=Verbatim(
        texto=("La faja del terreno que conforma el Derecho de Vía es un bien "
               "de dominio público inalienable e imprescriptible, cuyas "
               "definiciones y condiciones de uso se encuentran establecidas "
               "en el Reglamento Nacional de Gestión de Infraestructura Vial "
               "aprobado con Decreto Supremo Nº 034-2008-MTC y sus "
               "modificatorias, bajo los siguientes conceptos:"),
        pagina_pdf=199),
    # DEFINICION: dice QUE ES el derecho de via y a QUE reglamento remite; la
    # exigencia sobre el ancho esta en el 304.07.02.
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("LA REMISION AL RNGIV (DS 034-2008-MTC) ES LO QUE ESTA CITA "
          "ACREDITA, y el Reglamento NO esta en normas/: el archivo que "
          "hubo hasta 5196dd2 era la publicacion de El Peruano de 2006, no "
          "el decreto de 2008 (ver `fuentes.RNGIV`). La pagina imprime a "
          "continuacion seis conceptos (ancho y aprobacion, libre "
          "disponibilidad, registro, propiedad, propiedad restringida, "
          "condiciones de uso) que remiten al Reglamento y no se "
          "transcriben: ninguno trae numero."),
)

DG2018_304_07_02 = _cita(
    id="DG2018.304.07.02",
    fuente_id="DG2018",
    numeral="304.07.02",
    titulo_numeral="Ancho y aprobación del Derecho de Vía",
    jerarquia_numeral=("304.07 Derecho de Vía o faja de dominio",),
    pagina_impresa="198",
    pagina_pdf=199,
    texto_literal=Verbatim(
        texto=("La Tabla 304.09 indica los anchos mínimos que debe tener el "
               "Derecho de Vía, en función a la clasificación de la "
               "carretera por demanda y orografía."),
        pagina_pdf=199),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("EXIGENCIA SOBRE EL ANCHO, no sobre el agua: «anchos mínimos que "
          "debe tener». El mismo numeral dice antes que cada autoridad "
          "competente del articulo 4 del RNGIV «establece y aprueba mediante "
          "resolución del titular» el derecho de via de sus carreteras, y "
          "que para determinarlo «deberá tenerse en consideración la "
          "instalación de los dispositivos auxiliares y obras básicas "
          "requeridas para el funcionamiento de la vía». Es el requisito "
          "juridico [N] de V5 (v8 fila V5, enmendada en EXT-0); la condicion "
          "hidraulica no esta aqui ni en ninguna otra parte del 304.07."),
)

INTERPRETACION_INCREMENTO_DERECHO_VIA = Interpretacion(
    texto=("Que el incremento de 5.00 m se cuente DESDE EL BORDE mas alejado "
           "de la obra de drenaje --- el limite de la faja queda a 5.00 m del "
           "cabezal o del ala --- y no como una suma fija sobre el ancho de "
           "la Tabla 304.09 es la lectura que este proyecto adopta para el "
           "dia en que V5 compare el ancho declarado del corredor. La norma "
           "escribe el incremento y el caso; no escribe la composicion."),
    en_contra=("la frase dice «se incrementarán en 5.00 m» sobre «los anchos "
               "... fijados por la autoridad competente», que es un ancho de "
               "faja, y un ancho se incrementa sumando",
               "ninguna otra pagina del 304.07 define el punto de medida "
               "del incremento ni dibuja el caso"),
    a_favor=("los cuatro casos son bordes fisicos --- taludes de corte, pie "
             "de terraplenes, obras de drenaje, caminos de servicio ---, y un "
             "incremento «del borde mas alejado» solo tiene sentido medido "
             "desde ese borde",
             "la faja de propiedad restringida del 304.07.04 tambien se fija "
             "«a cada lado del Derecho de Vía» como una distancia, no como "
             "una suma al ancho"),
)

DG2018_304_07_02_INCREMENTO = _cita(
    id="DG2018.304.07.02#INCREMENTO",
    fuente_id="DG2018",
    numeral="304.07.02",
    titulo_numeral="Ancho y aprobación del Derecho de Vía",
    jerarquia_numeral=("304.07 Derecho de Vía o faja de dominio",),
    pagina_impresa="199",
    pagina_pdf=200,
    pagina_pdf_titulo=199,
    texto_literal=Verbatim(
        texto=("En general, los anchos de la faja de dominio o Derecho de "
               "Vía, fijados por la autoridad competente se incrementarán en "
               "5.00 m, en los siguientes casos:"),
        pagina_pdf=200),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=EXT6,
    interpretacion=INTERPRETACION_INCREMENTO_DERECHO_VIA,
    nota=("EL TERCERO DE LOS CUATRO CASOS ES EL DEL PROYECTO: la pagina "
          "imprime, con viñeta, «Del borde más alejado de las obras de "
          "drenaje» (los otros tres: el borde superior de los taludes de "
          "corte mas alejados, el pie de los terraplenes mas altos y el "
          "borde exterior de los caminos de servicio). Lo que la frase "
          "ESCRIBE es que el ancho fijado «se incrementará en 5.00 m» en ese "
          "caso; COMO se compone ese incremento con el ancho de la Tabla "
          "304.09 --- si el limite de la faja queda a 5.00 m del borde de la "
          "obra de drenaje, o si se suman 5.00 m al ancho de la fila --- no "
          "lo escribe, y es la lectura registrada en `interpretacion` "
          "(auditoria adversarial de EXT-6). El mismo numeral admite anchos menores en zonas "
          "urbanas «excepcionalmente», por saneamiento fisico legal: es una "
          "excepcion de la autoridad, no del proyectista. Vive en "
          "`constantes_normativas.INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M`. "
          "La viñeta del drenaje es su propia cita (#INCREMENTO_DRENAJE): "
          "la pagina separa los cuatro casos con un glifo de viñeta que la "
          "capa de texto conserva, y una sola cadena no los une."),
)

DG2018_304_07_02_INCREMENTO_DRENAJE = _cita(
    id="DG2018.304.07.02#INCREMENTO_DRENAJE",
    fuente_id="DG2018",
    numeral="304.07.02",
    titulo_numeral="Ancho y aprobación del Derecho de Vía",
    jerarquia_numeral=("304.07 Derecho de Vía o faja de dominio",),
    pagina_impresa="199",
    pagina_pdf=200,
    pagina_pdf_titulo=199,
    texto_literal=Verbatim(
        texto="Del borde más alejado de las obras de drenaje",
        pagina_pdf=200),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("El tercero de los cuatro casos en que el ancho «se incrementará "
          "en 5.00 m» (cita gemela #INCREMENTO). Es el que aplica a una "
          "alcantarilla: el borde es el del cabezal o el ala mas alejada "
          "del eje. Como se compone el incremento con el ancho de la Tabla "
          "304.09 es la interpretacion registrada en la cita gemela."),
)

DG2018_T304_09 = _cita(
    id="DG2018.304.07.02#T304.09",
    fuente_id="DG2018",
    numeral="Tabla 304.09",
    titulo_numeral="Anchos mínimos de Derecho de Vía",
    jerarquia_numeral=("304.07 Derecho de Vía o faja de dominio",),
    pagina_impresa="199",
    pagina_pdf=200,
    texto_literal=Verbatim(
        texto="Anchos mínimos de Derecho de Vía",
        pagina_pdf=200),
    # DEFINICION: la tabla tipifica los anchos por clase; lo que la hace
    # vinculante es el 304.07.02 («debe tener»), que es su cita gemela.
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("CINCO FILAS Y DOS COLUMNAS, transcritas enteras en "
          "`tablas.DG2018_T304_09`: Autopistas Primera Clase 40, Autopistas "
          "Segunda Clase 30, Carretera Primera Clase 25, Carretera Segunda "
          "Clase 20, Carretera Tercera Clase 16 (m). La clase de la via de "
          "ESTE corredor es el dato de sitio 'clase_de_via', vacio hasta que "
          "el estudio de demanda cierre el IMDA; sin el, ninguna fila se "
          "elige y el piso no se aplica."),
)

DG2018_304_10_T304_11 = _cita(
    id="DG2018.304.10#T304.11",
    fuente_id="DG2018",
    numeral="304.10, Tabla 304.11",
    titulo_numeral="Taludes",
    pagina_impresa="208",
    pagina_pdf=209,
    pagina_pdf_titulo=203,
    texto_literal=Verbatim(
        texto=("Los taludes en zonas de relleno (terraplenes), variarán en "
               "función de las características del material con el cual "
               "está formado. En la Tabla 304.11 se muestra taludes "
               "referenciales."),
        pagina_pdf=209),
    # DEFINICION, y la palabra es de la fuente: «referenciales». No manda
    # un talud; acota la banda dentro de la que 'talud_terraplen' elige.
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("El numeral 304.10 abre en la impresa 202 (PDF 203) y la Tabla "
          "304.11 esta en la 208 (PDF 209). Transcrita entera en "
          "`tablas.DG2018_T304_11`: tres materiales por tres alturas, en "
          "V:H. La fila «Gravas, limo arenoso y arcilla» da 1:1.5, 1:1.75 y "
          "1:2 para menos de 5 m, 5 a 10 m y mas de 10 m, que es exactamente "
          "la ventana (1.5, 2.0) H:V que 'talud_terraplen' declaraba como "
          "«practica corriente» sin poder citarla. Sigue siendo [A]: la tabla "
          "es referencial y la seccion tipica del expediente es la que "
          "cierra el valor."),
)


# ===========================================================================
# EXT-6 -- E.060 11.10, disposiciones especiales para muros (desfase 0)
#
# LAS CUATRO QUE EXT-7 CONSUME (EXT-M-05, R95-031): la pregunta de
# aplicabilidad --- el 11.10 rige el cortante EN EL PLANO del muro (11.10.2)
# y remite el perpendicular a las losas (11.10.1) --- y los dos pisos de
# cuantia bajo el regimen de 11.10.10. Se transcriben aqui, por delante del
# codigo que las lea, porque la v8 §9.4 ya las recoge desde EXT-0 y el
# criterio 'cortante_alto_muro_e060_art_11_10_10_2' las nombraba sin cita.
# ===========================================================================

E060_11_10_1 = _cita(
    id="E060.11.10.1",
    fuente_id="E060",
    numeral="11.10.1",
    titulo_numeral="DISPOSICIONES ESPECIALES PARA MUROS",
    pagina_impresa="103",
    pagina_pdf=103,
    texto_literal=Verbatim(
        texto=("El diseño para fuerzas cortantes perpendiculares al plano del "
               "muro debe hacerse según lo estipulado en las disposiciones "
               "para losas de 11.12."),
        pagina_pdf=103),
    caracter=Caracter.EXIGENCIA,
    sesion=EXT6,
    nota=("LA PREGUNTA DE APLICABILIDAD, dicha por la norma: el cortante "
          "PERPENDICULAR al plano --- que es el que el empuje de tierras "
          "produce en la pantalla de un cabezal --- se diseña por 11.12 "
          "(losas), no por 11.10. Antes de aplicar el 0.0025 de 11.10.10.2 "
          "hay que decir en que plano actua el cortante que lo dispara."),
)

E060_11_10_2 = _cita(
    id="E060.11.10.2",
    fuente_id="E060",
    numeral="11.10.2",
    titulo_numeral="DISPOSICIONES ESPECIALES PARA MUROS",
    pagina_impresa="103",
    pagina_pdf=103,
    texto_literal=Verbatim(
        texto=("El diseño para fuerzas cortantes horizontales en el plano del "
               "muro debe hacerse de acuerdo con las disposiciones de 11.10.3 "
               "a 11.10.10."),
        pagina_pdf=103),
    caracter=Caracter.EXIGENCIA,
    sesion=EXT6,
    nota=("La segunda oracion del numeral --- «Para muros estructurales que "
          "resistan cargas en su plano originadas por la acción de los "
          "sismos, se aplicará adicionalmente lo dispuesto en 21.9» --- no "
          "se transcribe: el cabezal no es muro estructural de un edificio."),
)

E060_11_10_10_2 = _cita(
    id="E060.11.10.10.2",
    fuente_id="E060",
    numeral="11.10.10.2",
    titulo_numeral="Diseño del refuerzo para cortante en muros",
    jerarquia_numeral=("11.10 DISPOSICIONES ESPECIALES PARA MUROS",),
    pagina_impresa="104",
    pagina_pdf=104,
    pagina_pdf_titulo=104,
    texto_literal=Verbatim(
        texto=("La cuantía de refuerzo horizontal para cortante no debe ser "
               "menor que 0,0025 y su espaciamiento no debe exceder tres "
               "veces el espesor del muro ni de 400 mm."),
        pagina_pdf=104),
    caracter=Caracter.EXIGENCIA,
    sesion=EXT6,
    nota=("El titulo de la jerarquia esta en la PDF 103 y el del 11.10.10 en "
          "la 104. El 0,0025 rige BAJO 11.10.10, que 11.10.7 y 11.10.8 "
          "disparan por Vu contra 0,085·raiz(f'c)·Acw; fuera de ese regimen "
          "el piso es el 0,002 del 14.3.1 (cita E060.14.3.1, cuya primera "
          "oracion remite aqui). El valor NO se transcribe como constante "
          "[N] en esta sesion: lo cablea EXT-7 con su caso patron."),
)

E060_11_10_10_3 = _cita(
    id="E060.11.10.10.3",
    fuente_id="E060",
    numeral="11.10.10.3",
    titulo_numeral="Diseño del refuerzo para cortante en muros",
    jerarquia_numeral=("11.10 DISPOSICIONES ESPECIALES PARA MUROS",),
    pagina_impresa="104",
    pagina_pdf=104,
    pagina_pdf_titulo=104,
    texto_literal=Verbatim(
        texto="La cuantía de refuerzo vertical para cortante,",
        pagina_pdf=104),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("EL VERBATIM SE CORTA DONDE EMPIEZA EL SIMBOLO: la capa de texto "
          "imprime «ρv» como glifos sueltos y la ecuacion como imagen, de "
          "modo que la oracion entera no se encuentra por texto. Leida "
          "sobre la pagina renderizada (EXT-6), la ec. (11-32) es "
          "ρv = 0,0025 + 0,5·(2,5 − hm/ℓm)·(ρh − 0,0025) ≥ 0,0025, «pero no "
          "necesita ser mayor que el valor de ρh requerido por 11.10.10.1», "
          "con hm la altura total del muro y ℓm su longitud total. Es lo que "
          "R95-031 (H-13) señalo: bajo el regimen de 11.10.10 la cuantia "
          "VERTICAL tambien tiene piso 0,0025, y `M9.cuantia_de_diseno` "
          "devolvia 0,0015 en vertical con cortante alto. Se corrige en "
          "EXT-7 (EXT-M-05); aqui queda la cita que le faltaba."),
)


# ===========================================================================
# EXT-6 -- El ALCANCE de las tres normas de producto (EXT-N-03)
#
# Las tres tenian UNA sola cita cada una, y de tablas. Sin la clausula de
# alcance, el registro no podia decir que cubre cada norma --- y por eso
# `_NORMA_PRODUCTO` pudo rotular un marco con la norma de un tubo sin que
# nada lo acusara. M 170M y M 36 por IMAGEN (OCR inutil y raster); A760 por
# IMAGEN (ToUnicode roto), sobre la traduccion al español del ejemplar.
# ===========================================================================

AASHTO_M170M_1_1 = _cita(
    id="AASHTO_M170M.1.1",
    fuente_id="AASHTO_M170M",
    numeral="1.1",
    titulo_numeral="SCOPE",
    pagina_impresa="M 170M-1",
    pagina_pdf=1,
    texto_literal=Verbatim(
        texto=("This specification covers reinforced concrete pipe intended "
               "to be used for the conveyance of sewage, industrial wastes, "
               "and storm water, and for the construction of culverts."),
        pagina_pdf=1),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=EXT6,
    nota=("Leida sobre la PDF 1 renderizada a escala 3.0 (el OCR imprime "
          "«iniendcd io be used» y «culvens»). Cubre TUBERIA («pipe»); un "
          "marco rectangular vaciado in situ no es tuberia y esta norma no "
          "lo rige. La PDF 1 rotula ademas «AASHTO Designation: M 170M-04» y "
          "«ASTM Designation: C 76M-02», que es la doble designacion del "
          "rotulo que M2 imprime."),
)

AASHTO_M170M_1_1_NOTA1 = _cita(
    id="AASHTO_M170M.1.1#NOTA1",
    fuente_id="AASHTO_M170M",
    numeral="1.2, Note 1",
    titulo_numeral="SCOPE",
    pagina_impresa="M 170M-1",
    pagina_pdf=1,
    texto_literal=Verbatim(
        texto=("Note 1—This specification is a manufacturing and purchase "
               "specification only, and does not include requirements for "
               "bedding, backfill, or the relationship between field load "
               "condition and the strength classification of pipe."),
        pagina_pdf=1),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=EXT6,
    nota=("LO QUE LA NORMA DICE QUE NO ES: ni cama, ni relleno, ni la "
          "relacion entre la carga de campo y la clase. La nota sigue: la "
          "experiencia muestra que el buen desempeño depende de elegir la "
          "clase, la cama y el relleno, y el propietario «is cautioned that "
          "he must correlate the field requirements with the class of pipe "
          "specified». Es la misma clausula que M 36 lleva en su 1.3 y A760 "
          "en su 1.4, y la razon de que 'clases_producto_por_relleno' sea un "
          "criterio del proyecto y no una lectura de la norma."),
)

AASHTO_M36_1_1 = _cita(
    id="AASHTO_M36.1.1",
    fuente_id="AASHTO_M36",
    numeral="1.1",
    titulo_numeral="SCOPE",
    pagina_impresa="M 36-1",
    pagina_pdf=2,
    texto_literal=Verbatim(
        texto=("This specification covers corrugated steel pipe intended for "
               "use for storm water drainage, underdrains, the construction "
               "of culverts, and similar uses. Pipe covered by this "
               "specification is not normally used for the conveyance of "
               "sanitary or industrial wastes."),
        pagina_pdf=2),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=EXT6,
    corresponde_en=("ASTM_A760.1.1",),
    nota=("RASTER PURO: leida sobre la PDF 2 renderizada a escala 3.0. La "
          "portada rotula «AASHTO Designation: M 36-03 (2007)» y «ASTM "
          "Designation: A 760/A 760M-01a». Cubre tuberia de acero corrugado "
          "para drenaje pluvial, subdrenes y alcantarillas; el resto del "
          "numeral 1.1 enumera los recubrimientos metalicos (zinc, aluminio "
          "tipo 2, aleacion 55 % Al-Zn, Zn-5 % Al-mischmetal, aluminio tipo "
          "1) y no se transcribe. La MISMA clausula, en español, es el 1.1 "
          "de A760 (`corresponde_en`)."),
)

ASTM_A760_1_1 = _cita(
    id="ASTM_A760.1.1",
    fuente_id="ASTM_A760",
    numeral="1.1",
    titulo_numeral="Alcance",
    pagina_impresa="1",
    pagina_pdf=1,
    texto_literal=Verbatim(
        texto=("Esta especificación cubre la tubería de acero corrugada "
               "destinada para uso en drenaje de aguas pluviales, desagües "
               "subterráneos, construcción de alcantarillas y usos "
               "similares."),
        pagina_pdf=1),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=EXT6,
    corresponde_en=("AASHTO_M36.1.1",),
    nota=("ToUnicode roto: leida sobre la PDF 1 renderizada a escala 3.0. El "
          "ejemplar es la TRADUCCION AL ESPAÑOL (propiedad declarada en la "
          "Fuente): el encabezado imprime «1 Alcance» y, arriba a la "
          "derecha, «AASHTO No. M 36 / M 36M», la doble designacion. Su 1.4 "
          "repite la clausula de M 170M Note 1 y M 36 1.3: la norma no "
          "incluye cama, relleno ni la relacion carga-espesor, y remite la "
          "instalacion a la Practica A798/A798M (ausente, DIS-HR-A807)."),
)


# ===========================================================================
# EXT-6 -- AASHTO LRFD 9a ed., Seccion 12: lo que ancla el marco IN SITU
# ===========================================================================

AASHTO_12_4_2_4 = _cita(
    id="AASHTO_LRFD_9.12.4.2.4",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.4.2.4",
    titulo_numeral="Precast Concrete Structures",
    pagina_impresa="12-8",
    pagina_pdf=1646,
    texto_literal=Verbatim(
        texto=("Precast concrete arch, elliptical, and box structures shall "
               "comply with the requirements of AASHTO M 206M/M 206 (ASTM "
               "C506M and C506), M 207M/M 207 (ASTM C507M and C507), M 259 "
               "(ASTM C789), and M 273 (ASTM C850)."),
        pagina_pdf=1646),
    caracter=Caracter.EXIGENCIA,
    sesion=EXT6,
    nota=("LA NORMA DE PRODUCTO DEL CAJON PREFABRICADO ES M 259 / M 273, y "
          "las dos estan AUSENTES de normas/ (`fuentes.AASHTO_M259`, "
          "`AASHTO_M273`). Es lo que sostiene la decision de "
          "docs/ruta_familia_c.md §14.1 --- marco VACIADO IN SITU --- y el "
          "rotulo «sin norma de producto» que M2 imprime para la seccion "
          "rectangular (EXT-N-03): un marco in situ no es un producto que "
          "se compra contra una especificacion, y rotularlo con la norma del "
          "tubo (M 170M) era una atribucion falsa."),
)

AASHTO_12_11_1 = _cita(
    id="AASHTO_LRFD_9.12.11.1",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.11.1",
    titulo_numeral="General",
    pagina_impresa="12-68",
    pagina_pdf=1706,
    texto_literal=Verbatim(
        texto=("The provisions herein shall apply to the structural design "
               "of cast-in-place and precast reinforced concrete box "
               "culverts and cast-in-place reinforced concrete arches with "
               "the arch barrel monolithic with each footing."),
        pagina_pdf=1706),
    caracter=Caracter.EXIGENCIA,
    sesion=EXT6,
    nota=("El Art. 12.11 se titula «REINFORCED CONCRETE CAST-IN-PLACE AND "
          "PRECAST BOX CULVERTS AND REINFORCED CAST-IN-PLACE ARCHES» "
          "(partido en tres renglones en la misma pagina; por eso no va en "
          "`jerarquia_numeral`). Rige el diseño estructural del marco in "
          "situ Y del prefabricado; y su cuarto parrafo dice que las "
          "dimensiones ESTANDAR del prefabricado estan en «AASHTO M 259 "
          "(ASTM C789) and M 273 (ASTM C850)»: para el in situ no hay "
          "dimensiones estandar, se proyectan. Es la mitad de diseño del "
          "rotulo de M2: «diseño LRFD Sec. 5 y Art. 12.11»."),
)


# ===========================================================================
# EXT-6 -- Manual de Puentes: la edicion de AASHTO LRFD que el MP ancla
# ===========================================================================

MP_INTRODUCCION_LRFD_2014 = _cita(
    id="MP.INTRODUCCION#LRFD_2014",
    fuente_id="MP",
    numeral="Introducción al Manual de Puentes",
    titulo_numeral="INTRODUCCIÓN AL MANUAL DE PUENTES",
    pagina_impresa="43",
    pagina_pdf=44,
    texto_literal=Verbatim(
        texto=("El Titulo II del Manual, presenta los aspectos de diseño que "
               "son, en gran parte, una adaptación del AASHTO en su versión "
               "LRFD BRIDGE DESIGN SPECIFICATIONS del año 2014, Septima "
               "Edición. Asimismo la entidad y/o propietario podrá "
               "considerar las actualizaciones de la AASTHO LRFD BRIDGE "
               "DESIGN."),
        pagina_pdf=44),
    # PERMISO: «podrá considerar las actualizaciones». Es lo que autoriza al
    # expediente a citar una LRFD posterior a la 7a de 2014 que el Manual
    # adapta, y lo que la ficha de 'edicion_que_rige_el_expediente' decia
    # que no existia («cuya edicion no la manda nadie», EXT-N-01).
    caracter=Caracter.PERMISO,
    metodo=AMBOS,
    sesion=EXT6,
    nota=("«AASTHO» y «Septima» sin tilde son de la fuente (sic). La "
          "Presentacion (PDF 42, impresa 41) lo repite: la actualizacion "
          "«se elaboró incorporando en gran parte las Especificaciones "
          "Técnicas de las Normas Americanas AASHTO LRFD, Septima Edición "
          "del año 2014». El registro cita la 9a ed. (2020) y la 10a (2024) "
          "esta publicada: el MP ancla la 7a y PERMITE las posteriores a "
          "«la entidad y/o propietario» --- no al proyectista, que propone "
          "---, de modo que la eleccion entre 9a y 10a es tecnica "
          "(DIS-MP-LRFD-EDICION dice por que la 9a es admisible; cual rige "
          "es de 'edicion_que_rige_el_expediente')."),
)

# ===========================================================================
# EXT-7 (EXT-M-06) · El coeficiente activo del Manual de Puentes es COULOMB
# ---------------------------------------------------------------------------
# La v8 §9.2 escribia «Ka = tan²(45 − φ/2)» sin decir de donde salia, y el
# codigo la seguia con Rankine en el empuje estatico mientras el incremento
# sismico iba con Mononobe-Okabe (Coulomb con aceleracion). La fuente primaria
# del marco elegido en §9.1 escribe Coulomb, con θ (cara posterior del muro
# sobre la horizontal), δ y β (talud del relleno): con θ = 90°, δ = β = 0 se
# reduce EXACTAMENTE a tan²(45 − φ/2). EXT-0 enmendo la hoja; esta es la cita
# que sostiene la enmienda y el punto de uso (`M9.empujes_trasdos`).
# Verificada sobre el texto extraido de la PDF 136 (pag. impresa 135): el
# numeral, el titulo y la frase de apertura estan literales; las dos
# ecuaciones se imprimen como formula y no se transcriben aqui. La palabra
# «Coulomb» NO esta en el articulado: la escribe el pie de la Figura
# 2.4.4.1.5.3-1 («Simbología para el empuje activo de Coulomb», PDF 137).
# ===========================================================================

MP_KA_COULOMB = _cita(
    id="MP.2.4.4.1.5.3",
    fuente_id="MP",
    numeral="2.4.4.1.5.3",
    titulo_numeral="Coeficiente de Empuje Lateral Activo, ka",
    pagina_impresa="135",
    pagina_pdf=136,
    texto_literal=Verbatim(
        texto="El coeficiente de empuje lateral activo se puede tomar como:",
        pagina_pdf=136),
    caracter=Caracter.PERMISO,
    sesion=EXT7,
    nota=("ES COULOMB (3.11.5.3 AASHTO): ka = sen²(θ + φ'f) / [r·sen²θ·"
          "sen(θ − δ)], con r = [1 + √(sen(φ'f + δ)·sen(φ'f − β) / "
          "(sen(θ − δ)·sen(θ + β)))]², ecs. 2.4.4.1.5.3-1 y -2 (PDF 136); "
          "la simbologia (Figura 2.4.4.1.5.3-1, «empuje activo de Coulomb») "
          "y la Tabla 2.4.4.1.5.3-1 de δ estan en la PDF 137 (pag. impresa "
          "136). θ es el angulo de la cara posterior del muro con la "
          "HORIZONTAL y β el del relleno con la horizontal: en la "
          "formulacion de M9 (Mononobe-Okabe con k_h = k_v = 0) el trasdos "
          "se mide desde la VERTICAL (β_M9 = 90° − θ) y el talud del relleno "
          "es i (= β del Manual); la identidad entre las dos escrituras es "
          "exacta y la recalcula el bloque __main__ de "
          "tests/fixtures/casos_patron.py (CP-9, bloque C). Con θ = 90°, "
          "δ = 0 y β = 0 se reduce a tan²(45 − φ/2), la forma que la v8 "
          "§9.2 escribia (DIS-HR-KA-COULOMB, resuelta en EXT-0). El "
          "«se puede tomar» es PERMISO: la fuente ofrece la expresion, no "
          "la impone; el proyecto la adopta como coeficiente estatico por "
          "homogeneidad con el sismico (EXT-M-06)."),
)

CITAS: Dict[str, Cita] = {c.id: c for c in _TODAS}
