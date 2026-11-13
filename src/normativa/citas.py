"""
Las citas del proyecto, una por objeto y con id estable (D1).

TODAS las que llevan `verificado` pasaron por el subagente
`verificador-normativo` -- en la sesion S12 las primeras, en la S13 el bloque
de clase de sitio -- contra el PDF cuyo sha1 declara la `Fuente`. Ninguna se acepto sin ese paso, y ninguna pagina se calculo a ojo
desde el desfase: donde el verificador no pudo leer, el campo queda en
`POR_TRANSCRIBIR` y la cita NO lleva firma. LAS DOS DE T-0 (cadena T,
2026-11-11: `HDS5_3ED.3.3.5#GOBIERNA` y `HDS5_3ED.A.3.1#CRITICO`) no pasaron
por ese subagente: las leyo la propia sesion abriendo la pagina por texto, y
su firma lo dice (`POR_T0`). Lo que las sostiene es lo mismo que a las demas:
`test_normativa_pdf` T2 y T6 buscan la frase en la pagina declarada.

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
FECHA_T0 = "2026-11-11"
POR_T0 = "tesis/T-0 · lectura directa de la pagina por la sesion"
# --- T-4 ---
FECHA_T4 = "2026-11-11"
POR_T4 = "tesis/T-4 · lectura directa de la pagina por la sesion"

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
T0 = (FECHA_T0, POR_T0)
# --- T-2 --- (cadena T). Mismo regimen que T-0: la propia sesion abrio cada
# pagina por su capa de texto (y la Tabla A.1 y los formularios DG 1 ademas
# por imagen), y la firma lo dice. `T2` ya existe y es OTRA sesion
# (trazabilidad/T2, 2026-09-12): por eso el nombre largo.
FECHA_TESIS_T2 = "2026-11-11"
POR_TESIS_T2 = "tesis/T-2 · lectura directa de la pagina por la sesion"
TESIS_T2 = (FECHA_TESIS_T2, POR_TESIS_T2)
T4 = (FECHA_T4, POR_T4)      # --- T-4 ---
# --- T-6 ---
FECHA_T6 = "2026-11-11"
POR_T6 = "tesis/T-6 · lectura directa de la pagina por la sesion"
T6 = (FECHA_T6, POR_T6)
# --- T-5 --- Mismo regimen que T-0, T-2 y T-4: la propia sesion abrio cada
# pagina (por texto AASHTO LRFD, el Manual de Puentes y EG-2013; por imagen
# ASTM A796 y AASHTO M 170M, que no entregan texto utilizable).
FECHA_T5 = "2026-11-12"
POR_T5 = "tesis/T-5 · lectura directa de la pagina por la sesion"
T5 = (FECHA_T5, POR_T5)

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
    # Las dos que T-0 dio de alta. Ninguna cita las usa todavia: estan aqui
    # para que T-4 y T-8 firmen las suyas sin tocar esta tabla.
    "HEC14": "1bffcbe220cd67e4c0de8b87b46d1ece64ce7217",
    "WSDOT_HM": "b34bb7bd448c249301e2a1a82234be70e8b6d916",
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

# ---------------------------------------------------------------------------
# T-0 - Las dos citas que dos pasos de M4 pedian y no tenian (INF-5.1.10)
# ---------------------------------------------------------------------------
# EL PASO DEL TIRANTE CRITICO NO LLEVABA `formula_cita_id` (anotado como C4-1
# en docs/ruta_familia_c.md) y el paso «cual control gobierna» llevaba la del
# num. A.2, que son las ECUACIONES DE CONTROL DE ENTRADA y no dicen nada de
# cual de los dos controles manda. Las dos frases que si lo dicen estan en el
# ejemplar y se leyeron en T-0, por texto, contra las PDF 192 y 107.
HDS5_A31_CRITICO = _cita(
    id="HDS5_3ED.A.3.1#CRITICO",
    fuente_id="HDS5_3ED",
    numeral="A.3.1",
    titulo_numeral="Elliptical Structural Plate Example",
    # EL NUMERAL ABRE AL PIE DE LA PAGINA IMPRESA A.2 (PDF 191) y la frase
    # esta en la A.3 (PDF 192): se cita la pagina de la frase y se declara
    # donde esta el titulo, como en `HDS5_3ED.A.3#FORMAS`.
    pagina_impresa="A.3",
    pagina_pdf=192,
    pagina_pdf_titulo=191,
    texto_literal=Verbatim(
        texto=("At critical depth, the critical velocity head is equal to "
               "one-half the hydraulic depth."),
        pagina_pdf=192),
    caracter=Caracter.DEFINICION,
    sesion=T0,
    nota=("ES LA CONDICION DE FLUJO CRITICO ESCRITA POR LA FUENTE, y no con "
          "los simbolos del paso que la cita. La pagina la escribe como "
          "V_c^2/(2g) = y_h/2 con y_h = A_p/T_p el tirante hidraulico, y dos "
          "renglones despues como numero de Froude: «Since the Froude number "
          "equals 1.0 at critical depth, Vc can be determined from the Froude "
          "number equation», con Qc = Ap (g yh)^0.5. Sustituyendo V = Q/A y "
          "y_h = A/T, las dos son Q^2/g = A^3/T, que es la forma en que "
          "`M4._residuo_critico` la resuelve: la igualdad es algebra de una "
          "linea y la hace el proyecto, no la fuente. Esta en un EJEMPLO del "
          "Apendice A (el desarrollo de la curva adimensional de una seccion "
          "eliptica), no en un numeral de definiciones: el HDS-5 no dedica "
          "ningun apartado a definir el tirante critico --lo lee de las "
          "cartas del Apendice C (num. 3.3.3)--, y esta es la unica pagina "
          "del ejemplar que escribe la condicion con la que se calcula. La "
          "misma pagina define H_c/D = d_c/D + y_h/(2D), ec. (A.4), que es el "
          "H_c de la Forma 1."),
)

HDS5_3_3_5_GOBIERNA = _cita(
    id="HDS5_3ED.3.3.5#GOBIERNA",
    fuente_id="HDS5_3ED",
    numeral="3.3.5",
    titulo_numeral="Evaluation of Results",
    pagina_impresa="3.25",
    pagina_pdf=107,
    pagina_pdf_titulo=107,
    texto_literal=Verbatim(
        texto=("The higher of the two is designated the controlling "
               "headwater elevation."),
        pagina_pdf=107),
    caracter=Caracter.DEFINICION,
    sesion=T0,
    nota=("Es el paso del PROCEDIMIENTO DE DISEÑO del Capitulo 3 («Culvert "
          "Hydraulic Design», num. 3.3 «Culvert Design Using Nomographs») "
          "que dice cual control gobierna. La oracion anterior fija el "
          "sujeto: «For the first alternative selected, compare the "
          "headwater elevations calculated for inlet and outlet control». "
          "Dos cosas que la frase dice y que el paso que la cita respeta: "
          "compara COTAS de carga (headwater elevations), que con los dos "
          "controles referidos al mismo fondo de entrada es comparar los dos "
          "HW; y «is designated» es una definicion del metodo, no una "
          "exigencia sobre el diseño. La oracion siguiente da la razon "
          "fisica: «The culvert can be expected to operate with that higher "
          "headwater for at least part of the time». Lo que el paso 4.4 hace "
          "ADEMAS --tomar como HW de salida el del remanso cuando la "
          "aproximacion de h_o esta fuera de rango-- no sale de aqui sino de "
          "la pag. 3.12 (`HDS5_3ED.3.1.4#0_75D`), que el paso cita aparte. "
          "Hasta T-0 el paso citaba `HDS5_3ED.A.2`, las ecuaciones de "
          "control de entrada (INF-5.1.10)."),
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

# ===========================================================================
# --- T-2 --- (cadena T, 2026-11-11) · Pendiente del conducto, barril
# horizontal y lo que HDS-5 dice de la correccion por pendiente
# ---------------------------------------------------------------------------
# NUEVE citas, leidas por la sesion sobre la capa de texto de cada pagina
# (INF-3.2.7, INF-5.1.6, INF-0.5). Lo que sostienen y lo que NO:
#
#   * NINGUNA fuente de `normas/` fija una pendiente minima ni maxima de
#     alcantarilla en CIFRAS. El Manual (4.1.1.3.3) exige que la pendiente no
#     altere «desmesuradamente» la erosion y la sedimentacion, sin numero; el
#     HDS-5 admite el barril horizontal (3.3.4), describe que la mayoria de
#     las alcantarillas se construyen por debajo del 10 % y sin medidas
#     estructurales especiales (5.4.4), y dice que sus curvas se trazan al
#     2 % (A.3). Por eso los dos limites son criterios [A] con ventana
#     (`pendiente_minima_conducto`, `pendiente_maxima_conducto`) y no [N].
#   * El encargo de T-2 citaba «HDS-5 Tabla A.1, nota de Ks·S» para el piso
#     de `hw_entrada_fuera_de_rango`. ESA NOTA NO EXISTE: la Tabla A.1 (PDF
#     197) solo lleva al pie sus cuatro referencias bibliograficas. Lo que
#     HDS-5 dice de Ks·S esta en la lista de variables del num. A.2.1
#     (`HDS5_3ED.A.2.1#KS`), en el num. 3.3.4 y en el A.3, y se transcribe
#     aqui con su pagina real.
# ===========================================================================

MC_HHD_4_1_1_3_3 = _cita(
    id="MC_HHD.4.1.1.3.3",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.3",
    titulo_numeral="Pendiente longitudinal",
    pagina_impresa="71",
    pagina_pdf=74,
    texto_literal=Verbatim(
        texto=("La pendiente longitudinal de la alcantarilla debe ser tal que "
               "no altere desmesuradamente los procesos geomorfológicos, como "
               "la erosión y sedimentación, por ello, los cambios de pendiente "
               "deben ser estudiados en forma cuidadosa, para no incidir en "
               "dichos procesos que pueden provocar el colapso de la "
               "estructura."),
        pagina_pdf=74),
    caracter=Caracter.EXIGENCIA,
    sesion=TESIS_T2,
    nota=("EXIGENCIA SIN NUMERO. El numeral entero son dos parrafos: este y "
          "la remision a la Lamina Nº 01 («ubicación típica de alcantarillas "
          "respecto a la pendiente del cauce»). No fija pendiente minima ni "
          "maxima, ni en porcentaje ni por material: obliga a ESTUDIAR el "
          "cambio de pendiente. Las cifras «2 % en TMC, 1 % en marco» que "
          "circulan en expedientes no salen de aqui."),
)

HDS5_3_3_4_HORIZONTAL = _cita(
    id="HDS5_3ED.3.3.4#HORIZONTAL",
    fuente_id="HDS5_3ED",
    numeral="3.3.4",
    titulo_numeral="Culverts with Horizontal or Adverse Slopes",
    pagina_impresa="3.25",
    pagina_pdf=107,
    texto_literal=Verbatim(
        texto=("The inlet and outlet control procedures that have been "
               "described were established assuming that culverts have some "
               "positive slope.  However, they can be reasonably applied to "
               "culverts with no slope (horizontal) or an adverse slope."),
        pagina_pdf=107),
    caracter=Caracter.PERMISO,
    sesion=TESIS_T2,
    nota=("Es la frase que admite S = 0 (INF-5.1.6). La leyo T-0 y la dejo "
          "sin cita; la transcribe T-2. El parrafo sigue con el caso en que "
          "se usa («A horizontal slope is used when flow may occur in either "
          "direction») y con una regla practica para la pendiente ADVERSA, "
          "que este proyecto NO admite: S < 0 sigue siendo dato invalido."),
)

HDS5_3_3_4_KS = _cita(
    id="HDS5_3ED.3.3.4#KS",
    fuente_id="HDS5_3ED",
    numeral="3.3.4",
    titulo_numeral="Culverts with Horizontal or Adverse Slopes",
    pagina_impresa="3.25",
    pagina_pdf=107,
    texto_literal=Verbatim(
        texto=("The inlet control nomograph solution HW/D contains a small "
               "slope correction term of -0.5S that was subtracted to account "
               "for the control section occurring within the culvert and "
               "slightly lower than the inlet invert."),
        pagina_pdf=107),
    caracter=Caracter.DEFINICION,
    derivado_de="HDS5_3ED.3.3.4#HORIZONTAL",
    sesion=TESIS_T2,
    nota=("Dice QUE ES el termino Ks·S: la seccion de control queda dentro "
          "del barril, algo mas baja que el fondo de la entrada. De ahi que "
          "con S = 0 el termino valga cero, que es lo que la ecuacion (A.1) "
          "da sola: la vineta que sigue manda SUMAR 0.01 al HW/D del "
          "nomograma en un barril horizontal, y ese 0.01 es 0.5 x 0.02, la "
          "correccion que el nomograma lleva restada por haberse trazado al "
          "2 % (`HDS5_3ED.A.3#PENDIENTE_2`). El codigo resuelve la ecuacion, "
          "no lee el nomograma, y por eso no suma nada: evalua Ks·S con la S "
          "real."),
)

HDS5_3_3_4_H = _cita(
    id="HDS5_3ED.3.3.4#H_SIN_AJUSTE",
    fuente_id="HDS5_3ED",
    numeral="3.3.4",
    titulo_numeral="Culverts with Horizontal or Adverse Slopes",
    pagina_impresa="3.25",
    pagina_pdf=107,
    texto_literal=Verbatim(
        texto=("The outlet control nomograph solution for losses through the "
               "barrel (H) for USGS flow type 4 and 6 can be used without "
               "adjustment for both a horizontal slope and an adverse slope."),
        pagina_pdf=107),
    caracter=Caracter.PERMISO,
    derivado_de="HDS5_3ED.3.3.4#HORIZONTAL",
    sesion=TESIS_T2,
    nota=("El control de salida no cambia con S = 0: H es la misma y la "
          "caida S·L vale cero, de modo que HW = H + h_o."),
)

HDS5_3_5_1_H2 = _cita(
    id="HDS5_3ED.3.5.1#H2",
    fuente_id="HDS5_3ED",
    numeral="3.5.1",
    titulo_numeral="USGS Flow Types and Water Surface Profiles",
    pagina_impresa="3.37",
    pagina_pdf=119,
    pagina_pdf_titulo=118,
    texto_literal=Verbatim(
        texto="In addition, the horizontal profiles of H2 and H3 were added.",
        pagina_pdf=119),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T2,
    nota=("La fuente NOMBRA los perfiles de pendiente horizontal (H2 y H3) "
          "como parte de los que HY-8 calcula desde la version 7.3, y no los "
          "desarrolla. El rotulo `TipoDePerfil.H2` es de aqui; el "
          "procedimiento con que el proyecto lo integra es el mismo paso "
          "directo de la pag. 3.12, con S = 0."),
)

HDS5_5_4_4_PENDIENTE_10 = _cita(
    id="HDS5_3ED.5.4.4#PENDIENTE_10",
    fuente_id="HDS5_3ED",
    numeral="5.4.4",
    titulo_numeral="Barrels on Steep Slopes",
    pagina_impresa="5.16",
    pagina_pdf=152,
    texto_literal=Verbatim(
        texto=("Most culverts are constructed on slopes that are less than "
               "10% and the effects of slope are neglected in hydraulic "
               "equations. For these culverts, no special structural measures "
               "are used."),
        pagina_pdf=152),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T2,
    nota=("DESCRIBE una practica, no fija un limite: bajo el 10 % no hacen "
          "falta medidas estructurales especiales. Es el unico numero sobre "
          "pendiente maxima que trae una fuente de `normas/`, y por eso es "
          "el valor que `pendiente_maxima_conducto` adopta como [A]. Entre "
          "10 % y 20 % la misma pagina pide atar las ultimas secciones del "
          "tubo; por encima del 20 %, `HDS5_3ED.5.4.4#PENDIENTE_20`."),
)

HDS5_5_4_4_PENDIENTE_20 = _cita(
    id="HDS5_3ED.5.4.4#PENDIENTE_20",
    fuente_id="HDS5_3ED",
    numeral="5.4.4",
    titulo_numeral="Barrels on Steep Slopes",
    pagina_impresa="5.16",
    pagina_pdf=152,
    texto_literal=Verbatim(
        texto=("For steep slopes (over 20%), the USBR hydraulic caution and "
               "additional structural measures should be considered."),
        pagina_pdf=152),
    caracter=Caracter.RECOMENDACION,
    derivado_de="HDS5_3ED.5.4.4#PENDIENTE_10",
    sesion=TESIS_T2,
    nota=("La cautela hidraulica del USBR que nombra esta en la misma "
          "pagina: no dejar que el barril fluya lleno en caidas grandes. "
          "Este programa no dimensiona anclajes ni ataduras de tubo: por eso "
          "la ventana de `pendiente_maxima_conducto` termina en 0.10."),
)

HDS5_A3_PENDIENTE_2 = _cita(
    id="HDS5_3ED.A.3#PENDIENTE_2",
    fuente_id="HDS5_3ED",
    numeral="A.3",
    titulo_numeral="A.3  INLET CONTROL DIMENSIONLESS DESIGN CURVES",
    pagina_impresa="A.2",
    pagina_pdf=191,
    pagina_pdf_titulo=191,
    texto_literal=Verbatim(
        texto=("A constant slope value of 2 percent (0.02) is usually "
               "selected for the development of design curves.  This is "
               "because the slope effect is small and the resultant headwater "
               "is conservatively high for sites with slopes exceeding 2 "
               "percent (except for mitered inlets)."),
        pagina_pdf=191),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T2,
    nota=("Dos cosas en una frase: que la correccion por pendiente es CHICA "
          "(«the slope effect is small»), y que fijarla en el 2 % deja la "
          "carga del lado conservador en pendientes mayores. Es el extremo "
          "inferior de la ventana de `pendiente_maxima_conducto` (0.02: la "
          "pendiente con que la fuente traza sus curvas) y el argumento con "
          "que el proyecto lee el termino Ks·S como una correccion menor que "
          "no puede anular la carga."),
)

HDS5_5_3_3_DEPRESION = _cita(
    id="HDS5_3ED.5.3.3#DEPRESION",
    fuente_id="HDS5_3ED",
    numeral="5.3.3",
    titulo_numeral="Sedimentation",
    pagina_impresa="5.12",
    pagina_pdf=148,
    pagina_pdf_titulo=147,
    texto_literal=Verbatim(
        texto=("Culverts built with an upstream depression possess a barrel "
               "slope which is less than that of the natural channel.  "
               "Sedimentation is the likely result, especially during times "
               "of low flow.  However, self-cleaning usually occurs during "
               "periods of high discharge."),
        pagina_pdf=148),
    caracter=Caracter.DEFINICION,
    derivado_de="HDS5_3ED.5.3.3#INDICADORES",
    sesion=TESIS_T2,
    nota=("Es el final del num. 5.3.3, ya en la pag. impresa 5.12, y lo que "
          "la fuente dice del caso que el primer indicador describe: el "
          "conducto mas plano que su cauce sedimenta SOBRE TODO con caudales "
          "bajos y SUELE limpiarse solo con los altos. La oracion siguiente "
          "pide abordar ese diseño con cautela y con mas investigacion de "
          "campo; no lo prohibe. Sostiene que el indicador se aplique como "
          "aviso (`regimen_v2b`). EL NUMERAL ENTERO, leido en T-2 (INF-3.2.9): "
          "ademas de los dos indicadores --pendiente y rugosidad-- nombra "
          "como factores la magnitud del caudal y el material del cauce, los "
          "cauces en agradacion, los cambios de pendiente a la entrada, las "
          "instalaciones multibarril y las entradas deprimidas. Ninguno "
          "lleva cifra."),
)

HDS5_A21_FORMA_1 = _cita(
    id="HDS5_3ED.A.2.1#FORMA_1",
    fuente_id="HDS5_3ED",
    numeral="A.2.1",
    titulo_numeral="Unsubmerged Inlet Control Equations",
    pagina_impresa="A.1",
    pagina_pdf=190,
    texto_literal=Verbatim(
        texto=("Form (1) is based on the specific head at critical depth, "
               "adjusted with correction factors."),
        pagina_pdf=190),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T2,
    nota=("LA BASE DE LA FORMA 1 ES H_c, y los demas terminos --K(q*)^M y "
          "Ks·S-- son «correction factors». Es lo que sostiene el piso "
          "«energia_critica» de `hw_entrada_fuera_de_rango`: cuando la "
          "correccion por pendiente, extrapolada, anula la carga, el proyecto "
          "se queda con la base de la que la ecuacion parte. LA FUENTE NO "
          "PRESCRIBE ESE PISO --no dice que hacer cuando HWi/D sale nulo o "
          "negativo--: por eso el criterio sigue siendo [A], con «descartar» "
          "como alternativa, y no [C]."),
)


# --- T-4 --- (cadena T, 2026-11-11) Materiales, espesores, topes y
# durabilidad: INF-5.1.17, INF-3.3.1, INF-3.3.4, INF-3.2.4, INF-3.2.1 (mitad
# HDPE), INF-5.1.9.
# ---------------------------------------------------------------------------
# COMO SE LEYERON. Las de WSDOT, HDS-5, AASHTO LRFD, el Manual de Hidrologia,
# EG-2013 y E.050 por TEXTO, abriendo la pagina declarada (T2, T3 y T6 las
# comprueban en cada corrida con PyMuPDF). Las cuatro de AASHTO M 36 por
# IMAGEN: el ejemplar es raster puro, y se renderizaron las PDF 2, 7, 11 y 13
# (100 dpi la pagina entera y 170 a 220 dpi los recortes de las tablas).
# NINGUNA paso por el subagente verificador: las leyo la propia sesion, y la
# firma lo dice (`POR_T4`), como las dos de T-0.
#
# LO QUE ESTE BLOQUE CORRIGE DE LO QUE EL PROYECTO CITABA: 'v_max_tmc' y
# 'v_max_hdpe' atribuian a la Tabla 8-4 de WSDOT un «techo de velocidad» y la
# prohibicion del termoplastico. La tabla es de NIVELES DE ABRASION y no
# prohibe nada al termoplastico; la prohibicion esta en el §8-3.3 y esta
# atada al NIVEL, no a la velocidad sola. Las dos citas van separadas para
# que ninguna ficha pueda volver a fundirlas.
# ===========================================================================

WSDOT_8_3_3_SEVERA = _cita(
    id="WSDOT_HM.8-3.3#SEVERA",
    fuente_id="WSDOT_HM",
    numeral="8-3.3",
    titulo_numeral="Thermoplastic Pipe: General",
    pagina_impresa="8-13",
    pagina_pdf=228,
    texto_literal=Verbatim(
        texto=("However, because thermoplastic pipe cannot be structurally "
               "reinforced, it shall not be used for severely abrasive "
               "conditions as described in Table 8-4."),
        pagina_pdf=228),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("ES LA UNICA FRASE DEL MANUAL QUE PROHIBE UN MATERIAL POR ABRASION, "
          "y la prohibicion cuelga del NIVEL («severely abrasive conditions as "
          "described in Table 8-4»), no de una velocidad. La frase anterior "
          "del mismo parrafo dice lo contrario de lo que se esperaria de un "
          "material prohibido: «Laboratory testing indicates that the "
          "resistance of thermoplastic pipe to abrasive bed loads is equal to "
          "or greater than that of other types of pipe material»; la razon de "
          "la prohibicion es que no se puede REFORZAR. El mismo parrafo "
          "declara al termoplastico resistente a pH y resistividad y "
          "aceptable en las tres zonas de corrosion sin tratamiento. "
          "Sostiene 'v_max_hdpe' [C] y la regla de abrasion de la matriz de "
          "durabilidad (`M2.matriz_durabilidad`)."),
)

WSDOT_T8_4 = _cita(
    id="WSDOT_HM.T8-4",
    fuente_id="WSDOT_HM",
    numeral="Table 8-4",
    titulo_numeral="Pipe Abrasion Levels",
    pagina_impresa="8-27",
    pagina_pdf=242,
    texto_literal=Verbatim(
        texto=("The abrasion level descriptions are intended to serve as "
               "general guidance only; not all of the criteria listed for a "
               "particular abrasion level need to be present to justify "
               "placing a site at that level."),
        pagina_pdf=242),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("LA TABLA OCUPA DOS PAGINAS: las tres primeras filas en la 8-27 "
          "(PDF 242) y la cuarta, «Severely abrasive», en la 8-28 (PDF 243). "
          "ES UNA TABLA DE NIVELES DE ABRASION, NO DE VELOCIDADES MAXIMAS: "
          "cada nivel se describe por tres caracteristicas del sitio (carga "
          "de fondo, pendiente y velocidad) y el `texto_literal` --el segundo "
          "parrafo del §8-6 «Abrasion», que la introduce-- dice que no hace "
          "falta que concurran las tres. Por eso tomar la velocidad sola como "
          "criterio suficiente de «severamente abrasivo» es una lectura que "
          "la fuente PERMITE y no impone (`Interpretacion` de la tabla). "
          "DEFINICION y no EXIGENCIA para la cita: los «shall» estan en las "
          "celdas de «Recommended Invert Protection» (mas calibre para el "
          "metal desde el nivel moderado), no en la clasificacion."),
)

WSDOT_3_3_5 = _cita(
    id="WSDOT_HM.3-3.5#10FTS",
    fuente_id="WSDOT_HM",
    numeral="3-3.5",
    titulo_numeral="Velocities in Culverts: General",
    pagina_impresa="3-11",
    pagina_pdf=76,
    texto_literal=Verbatim(
        texto=("If velocities exceed about 10 ft/s, abrasion due to bed load "
               "movement through the culvert and erosion downstream of the "
               "outlet can increase significantly."),
        pagina_pdf=76),
    caracter=Caracter.RECOMENDACION,
    sesion=T4,
    nota=("10 ft/s = 3.048 m/s ES UMBRAL DE CONSULTA, NO PROHIBICION. El "
          "mismo numeral dice antes que las alcantarillas con velocidades "
          "«in the range of 3 to 10 feet per second (ft/s) tend to have fewer "
          "operational problems» y que fuera de ese rango hay que tratarlo "
          "con el ingeniero regional; y despues, que «Corrugated metal "
          "culverts may be designed with extra thickness to account for "
          "possible abrasion». Es el PISO de la ventana de 'v_max_tmc' [A]: "
          "por debajo de el la propia fuente no ve problema de abrasion que "
          "justifique un techo mas bajo."),
)

WSDOT_8_5_1 = _cita(
    id="WSDOT_HM.8-5.1#PH",
    fuente_id="WSDOT_HM",
    numeral="8-5.1",
    titulo_numeral="pH",
    pagina_impresa="8-25",
    pagina_pdf=240,
    texto_literal=Verbatim(
        texto=("When the pH is less than 5.0 or greater than 8.5, the site "
               "will be considered unsuitable and only Corrosion Zone III "
               "pipes, as discussed in Section 8-4.3, are acceptable."),
        pagina_pdf=240),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("EL pH ES «soil or water pH» (primer parrafo del §8-5, misma "
          "pagina). Fuera de 5.0-8.5 solo valen los tubos de la Zona de "
          "Corrosion III, que el §8-4.3 y la Tabla 8-3 (misma pagina) "
          "limitan a concreto, termoplastico y aluminio: NINGUN tubo de "
          "acero. La pagina siguiente (8-26) repite el intervalo: «the "
          "acceptable range of 5.0 to 8.5». Es criterio de una agencia vial "
          "de EE. UU. --fuente tecnica reconocida, [C]--, no norma peruana: "
          "el umbral peruano es el de EG-2013 507.10 (pH < 5.8 exige "
          "proteger la tuberia), que no prohibe el material."),
)

WSDOT_8_5_2 = _cita(
    id="WSDOT_HM.8-5.2#RESISTIVIDAD",
    fuente_id="WSDOT_HM",
    numeral="8-5.2",
    titulo_numeral="Resistivity",
    pagina_impresa="8-26",
    pagina_pdf=241,
    texto_literal=Verbatim(
        texto=("If the resistivity is less than 1,000 ohm-cm for a location, "
               "then Corrosion Zone III pipe materials are the only "
               "acceptable alternatives."),
        pagina_pdf=241),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("La resistividad es «the measure of the ability of soil or water "
          "to pass electric current» (misma pagina): el dato puede ser del "
          "suelo o del agua, y rige el menor. Por debajo de 1 000 ohm-cm "
          "solo valen los materiales de la Zona III (concreto, termoplastico "
          "y aluminio): el acero corrugado queda fuera."),
)

WSDOT_8_4_3 = _cita(
    id="WSDOT_HM.8-4.3#ZONA_III",
    fuente_id="WSDOT_HM",
    numeral="8-4.3",
    titulo_numeral="Corrosion Zone III",
    pagina_impresa="8-17",
    pagina_pdf=232,
    texto_literal=Verbatim(
        texto=("Concrete and thermoplastic pipe are allowed for use in this "
               "zone without protective treatments."),
        pagina_pdf=232),
    caracter=Caracter.PERMISO,
    sesion=T4,
    nota=("LA ZONA III ES LA DE CORROSION SEVERA, y la misma pagina la "
          "describe con palabras que valen para un corredor costero de riego: "
          "«Low-lying roadways ... and coastal areas subjected to the "
          "influence of saltwater bays, marshes, and tide flats». La frase "
          "sigue en la 8-18: el aluminio se admite con las condiciones del "
          "§8-3. La Tabla 8-3 (pag. 8-25, PDF 240) lista las alternativas "
          "aceptables y no trae ningun tubo de acero."),
)

WSDOT_8_3_1 = _cita(
    id="WSDOT_HM.8-3.1#CONCRETO",
    fuente_id="WSDOT_HM",
    numeral="8-3.1",
    titulo_numeral="Concrete Pipe",
    pagina_impresa="8-10",
    pagina_pdf=225,
    pagina_pdf_titulo=224,
    texto_literal=Verbatim(
        texto=("Concrete pipe is permitted anywhere in the state, regardless "
               "of corrosion zone, pH, or resistivity."),
        pagina_pdf=225),
    caracter=Caracter.PERMISO,
    sesion=T4,
    nota=("El numeral abre en la 8-9 (PDF 224) y la frase esta en la 8-10. "
          "Es lo que sostiene que la matriz de durabilidad NO excluya al "
          "concreto por pH ni por resistividad; lo que el concreto si "
          "recibe son REQUISITOS de mezcla y recubrimiento, y esos salen de "
          "la norma peruana (E.060 Tablas 4.2 y 4.4, Art. 4.4.2)."),
)

AASHTO_C12_6_9 = _cita(
    id="AASHTO_LRFD_9.C12.6.9#NIVEL_4",
    fuente_id="AASHTO_LRFD_9",
    numeral="C12.6.9",
    titulo_numeral="Corrosive and Abrasive Conditions",
    pagina_impresa="12-24",
    pagina_pdf=1662,
    texto_literal=Verbatim(
        texto=("Level 4—Severe abrasive conditions exist in areas of heavy "
               "bed loads of sand, gravel, and rock and velocities exceeding "
               "15.0 ft/s."),
        pagina_pdf=1662),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("SEGUNDA FUENTE DEL CORTE DE 15 ft/s, y dice lo mismo que la "
          "primera: es un NIVEL de abrasion de la FHWA (carga de fondo pesada "
          "Y velocidad), no un techo de velocidad. Los otros tres niveles, en "
          "la misma columna: Level 1 sin carga de fondo y velocidades muy "
          "bajas; Level 2 «velocities of 5.0 ft/s or less»; Level 3 «between "
          "5.0 ft/s and 15.0 ft/s». El corte inferior es 5.0 ft/s aqui y "
          "6 ft/s en la Tabla 8-4 de WSDOT: las dos clasificaciones no "
          "coinciden por abajo y si por arriba. El articulado 12.6.9 (misma "
          "pagina) no fija ningun limite: pide que la vida util del material "
          "iguale o supere la de la alcantarilla y nombra los remedios "
          "usuales para el metal («increased gauge thickness», «protective "
          "linings»)."),
)

AASHTO_TA12_11 = _cita(
    id="AASHTO_LRFD_9.TA12-11",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table A12-11",
    titulo_numeral="PE Corrugated Pipes (AASHTO M 294)",
    pagina_impresa="12-108",
    pagina_pdf=1746,
    texto_literal=Verbatim(
        texto="Table A12-11—PE Corrugated Pipes (AASHTO M 294)",
        pagina_pdf=1746),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("ES LA FUENTE DEL DIAMETRO EXTERIOR DEL HDPE, que su norma de "
          "producto no trae (afirmacion negativa "
          "SIN_DIAMETRO_EXTERIOR_M294_TRAD). Apendice A12 «PLATE, PIPE, AND "
          "PIPE ARCH PROPERTIES» de la Seccion 12: para cada tamaño nominal "
          "de tuberia corrugada de PE bajo M 294 tabula el diametro interior "
          "MINIMO, el diametro exterior MAXIMO y las propiedades minimas de "
          "la pared (A, c, I). OCHO filas, de 12 a 48 in: NO trae 54 ni 60 "
          "in, de modo que para 1350 y 1500 mm el diametro exterior sigue "
          "sin fuente y 'espesor_pared_conducto' no declara esas filas. "
          "Unidades inglesas; la conversion a metros (1 in = 0.0254 m "
          "exactos) es del proyecto. La nota al pie de la tabla avisa de que "
          "para 42 y 48 in el espesor de pared se diseñe con la resistencia "
          "a traccion de largo plazo (900 psi): es de la Fase 8, no del "
          "diametro exterior, y `M8.verificar_hdpe` la aplica en esas dos "
          "filas con las propiedades de largo plazo (T-5)."),
)

HDS5_TB1 = _cita(
    id="HDS5_3ED.TB.1",
    fuente_id="HDS5_3ED",
    numeral="Table B.1",
    titulo_numeral="Manning's n Values for Culverts.",
    pagina_impresa="B.6",
    pagina_pdf=208,
    texto_literal=Verbatim(
        texto=("The Manning's n values indicated in this table were obtained "
               "in the laboratory and are supported by the provided "
               "reference. Actual field values for culverts may vary "
               "depending on the effect of abrasion, corrosion, deflection, "
               "and joint conditions."),
        pagina_pdf=208),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("LA PAGINA ROTULA «B.1.  Manning's n Values for Culverts.» SIN LA "
          "PALABRA «Table»; el numeral «Table B.1» es como el propio HDS-5 "
          "la llama en el cuerpo. El `texto_literal` es su nota al pie 1, y "
          "va a proposito: los n son de LABORATORIO y la fuente advierte que "
          "los de campo pueden variar por abrasion, corrosion, deflexion y "
          "juntas. La fila «Corrugated Polyethylene / Smooth», 0.009-0.015 "
          "(Barfuss & Tullis 1988; Tullis et al. 1990), es la que cierra "
          "'n_manning_hdpe' como [C]: hasta T-4 era la fila del concreto de "
          "la Tabla N 09 aplicada por analogia. Y desde la auditoria de T-3 "
          "(H1), la fila «Concrete Boxes / Smooth», 0.012-0.015 (FHWA 1961), "
          "cierra 'n_manning_cajon' como [C] por la misma razon: la Tabla N 09 "
          "no tiene fila de seccion rectangular."),
)

MC_HHD_4_1_1_3_4b = _cita(
    id="MC_HHD.4.1.1.3.4b",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 b)",
    titulo_numeral="b)  Materiales",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="73",
    pagina_pdf=76,
    texto_literal=Verbatim(
        texto=("En conclusión no es posible dar una regla general para la "
               "elección del tipo de material a emplear en la construcción "
               "de la alcantarilla, sino que además de los aspectos "
               "mencionados anteriormente depende del tipo de suelo, del "
               "agua y principalmente de la disponibilidad de materiales en "
               "el lugar."),
        pagina_pdf=76),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("EL MANUAL NO DA REGLA DE ELECCION DE MATERIAL, y lo dice con esas "
          "palabras. La frase anterior enumera de que depende: «tiempo de "
          "vida útil, costo, resistencia, rugosidad, condiciones del "
          "terreno, resistencia a la corrosión, abrasión, fuego e "
          "impermeabilidad». Es lo que hace de la matriz de durabilidad un "
          "FILTRO con fuentes tecnicas y no una eleccion normativa: el "
          "Manual nombra los factores (suelo, agua) y no pone umbrales."),
)

MC_HHD_4_1_1_3_7e = _cita(
    id="MC_HHD.4.1.1.3.7e",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 e)",
    titulo_numeral="e)  Abrasión",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="81",
    pagina_pdf=84,
    texto_literal=Verbatim(
        texto=("Es importante tomar en cuenta este fenómeno al momento de "
               "elegir el tipo de material del cual estará constituida la "
               "alcantarilla."),
        pagina_pdf=84),
    caracter=Caracter.RECOMENDACION,
    sesion=T4,
    nota=("CUALITATIVO, SIN NINGUN VALOR: el inciso define la abrasion «la "
          "erosión del material de la alcantarilla por la acción de sólidos "
          "flotantes transportados por el cauce natural» y dice de que "
          "depende («carácter y cantidad de material de arrastre, duración, "
          "frecuencia y velocidad del flujo»), pero no escribe ninguna "
          "velocidad maxima para el metal ni para el plastico. La Tabla N 10 "
          "(num. 4.1.1.3.6) tampoco los lista. Es la razon de que "
          "'v_max_tmc' sea [A]: la norma peruana manda considerar la "
          "abrasion y no da el numero."),
)

MC_HHD_4_1_1_3_7f_SALINIDAD = _cita(
    id="MC_HHD.4.1.1.3.7f#SALINIDAD",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 f)",
    titulo_numeral="f)  Corrosión",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="81",
    pagina_pdf=84,
    texto_literal=Verbatim(
        texto=("El agua con alta salinidad causa intensa corrosión a corto "
               "plazo en el acero."),
        pagina_pdf=84),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("El parrafo anterior nombra las tres condiciones que la matriz de "
          "durabilidad recibe como ensayo: «condiciones alcalinas y ácidas "
          "presentes en el suelo y en el agua, y la conductividad eléctrica "
          "del suelo» --o sea pH y resistividad--. NO DA UMBRAL de salinidad "
          "ni de cloruros: por eso 'cloruros_ppm' produce un AVISO y no un "
          "descarte."),
)

MC_HHD_4_1_1_3_7f_COSTA = _cita(
    id="MC_HHD.4.1.1.3.7f#COSTA",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 f)",
    titulo_numeral="f)  Corrosión",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="81",
    pagina_pdf=84,
    texto_literal=Verbatim(
        texto=("Es importante señalar que cualquier material utilizado en la "
               "construcción de alcantarillas expuesto al agua de mar o "
               "cuando las alcantarillas se ubiquen en zonas costeras "
               "cercanas al mar requieren"),
        pagina_pdf=84),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("LA FRASE SE CORTA DONDE LA CORTA LA PAGINA: «...requieren» es el "
          "ultimo renglon de la pag. impresa 81, y sigue en la 82 (PDF 85) "
          "con «algún tipo de protección para asegurar su vida útil». Dice "
          "CUALQUIER material, no solo el metal, y no cuantifica «cercanas "
          "al mar»: el corredor del repositorio (La Union, Bajo Piura) esta "
          "en la costa, y si la frase le alcanza lo decide el proyectista "
          "con el EMS, no este registro."),
)

MC_HHD_4_1_1_3_7f_TMC = _cita(
    id="MC_HHD.4.1.1.3.7f#TMC",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 f)",
    titulo_numeral="f)  Corrosión",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="82",
    pagina_pdf=85,
    pagina_pdf_titulo=84,
    texto_literal=Verbatim(
        texto=("En el caso de alcantarillas de metal corrugado generalmente "
               "se utiliza capas protectoras tales como recubrimientos "
               "asfálticos, sin embargo, esta medida muchas veces no es "
               "suficiente, por lo que un material de mayor resistencia "
               "sería el más adecuado para actuar en medios muy agresivos."),
        pagina_pdf=85),
    caracter=Caracter.RECOMENDACION,
    sesion=T4,
    nota=("El inciso abre en la pag. impresa 81 (PDF 84) y este parrafo esta "
          "en la 82. La frase anterior, misma pagina: «los suelos con alto "
          "contenido de materia orgánica son nocivos para los metales ya que "
          "se corroen»."),
)

MC_HHD_4_1_1_3_7g = _cita(
    id="MC_HHD.4.1.1.3.7g#AGRESIVAS",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 g)",
    titulo_numeral="g)  Seguridad y vida útil",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="82",
    pagina_pdf=85,
    texto_literal=Verbatim(
        texto=("Cuando las condiciones de exposición son muy agresivas, "
               "tales como velocidades excesivas con presencia de elementos "
               "abrasivos en el flujo, presencia de aguas salinas o ácidas "
               "provenientes de establecimientos mineros, suelos alcalinos y "
               "suelos con presencia de turba, el recubrimiento asfáltico no "
               "ofrece una protección suficiente, bajo estas condiciones no "
               "es recomendable el uso de alcantarillas metálicas"),
        pagina_pdf=85),
    caracter=Caracter.RECOMENDACION,
    sesion=T4,
    nota=("LA ORACION SIGUE, y se corta aqui a proposito antes del salto de "
          "pagina: «..., por ello, se recomienda el uso de otros materiales "
          "para la construcción de» (fin de la impresa 82) «alcantarillas, "
          "como concreto de alta resistencia o tubos de alta densidad» "
          "(impresa 83, PDF 86). ES RECOMENDACION («no es recomendable»), no "
          "prohibicion, y NO CUANTIFICA ninguna de las condiciones: no dice "
          "que velocidad es excesiva ni que salinidad es agresiva. La matriz "
          "de durabilidad la imprime como AVISO cuando un ensayo declarado "
          "cae en una de esas condiciones; el descarte del TMC por pH o por "
          "resistividad sale de los umbrales de WSDOT §8-5 [C]."),
)

EG_507_10 = _cita(
    id="EG2013.507.10",
    fuente_id="EG2013",
    numeral="507.10",
    titulo_numeral="Aguas y Suelos agresivos",
    pagina_impresa="974",
    pagina_pdf=982,
    texto_literal=Verbatim(
        texto=("Si las aguas que han de conducir los tubos presentan un pH "
               "menor de 5.8, o que los suelos circundantes presenten "
               "sustancias agresivas, será necesario proteger la tubería "
               "cuyo producto y procedimiento será acorde al Proyecto o "
               "aprobación del Supervisor"),
        pagina_pdf=982),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("ES EL UNICO UMBRAL NUMERICO DE DURABILIDAD DE LA TUBERIA QUE LA "
          "NORMA PERUANA ESCRIBE, y esta en la Seccion 507 «Tubería metálica "
          "corrugada»: pH < 5.8 del AGUA QUE CONDUCE el tubo. EXIGE PROTEGER, "
          "no prohibe el material, y no dice con que («acorde al Proyecto»). "
          "«Sustancias agresivas» del suelo no se cuantifica. Las Secciones "
          "505, 506 y 508 (concreto simple, concreto reforzado y polietileno) "
          "no traen clausula equivalente: buscadas por «agresiv», «corrosi», "
          "«salin», «pH» y «resistividad» en las pags. PDF 940 a 1000."),
)

E050_ART_24 = _cita(
    id="E050.24",
    fuente_id="E050",
    numeral="Art. 24",
    titulo_numeral="Suelos no permitidos para apoyar las cimentaciones",
    pagina_impresa="37",
    pagina_pdf=37,
    texto_literal=Verbatim(
        texto=("No se cimienta sobre los siguientes tipos de materiales: "
               "turba, suelo orgánico, tierra vegetal, relleno de desmonte o "
               "rellenos sanitario o industrial, ni Rellenos No Controlados."),
        pagina_pdf=37),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("ES LA FUENTE PERUANA MAS CERCANA A «suelos de fundación de mala "
          "calidad», que el num. 4.1.1.3.4 a) del Manual de Hidrologia "
          "nombra y no define (COND-MARCO-SUELO-MALA-CALIDAD). La E.050 es "
          "de EDIFICACIONES y no de obras viales: por eso el conjunto "
          "'sucs_fundacion_deficiente' es [A] --una adopcion apoyada en "
          "esta lista-- y no [N]. De los materiales que el articulo "
          "enumera, solo dos tienen simbolo SUCS (Figura 3 de la misma "
          "norma): la turba (Pt) y el suelo organico (OL, OH); la tierra "
          "vegetal y los rellenos no se clasifican por SUCS."),
)

E050_FIG_3 = _cita(
    id="E050.FIG3",
    fuente_id="E050",
    numeral="Figura 3",
    titulo_numeral="Simbología de Suelos (Referencial)",
    pagina_impresa="31",
    pagina_pdf=31,
    texto_literal=Verbatim(
        texto="TURBA Y OTROS SUELOS ALTAMENTE ORGÁNICOS.",
        pagina_pdf=31),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("Los quince simbolos SUCS con su descripcion: GW, GP, GM, GC, SW, "
          "SP, SM, SC, ML, CL, OL, MH, CH, OH y Pt. La figura se rotula "
          "«(Referencial)». Es el conjunto cerrado del que "
          "'sucs_fundacion_deficiente' elige, transcrito en la tabla "
          "E050.FIG3. Los simbolos DOBLES de un suelo de frontera («SP-SM» "
          "en el CSV de ejemplo) no estan en la figura: se componen de dos "
          "de estos."),
)

AASHTO_M36_1_2 = _cita(
    id="AASHTO_M36.1.2",
    fuente_id="AASHTO_M36",
    numeral="1.2",
    titulo_numeral="SCOPE",
    pagina_impresa="M 36-1",
    pagina_pdf=2,
    texto_literal=Verbatim(
        texto=("The several different metallic coatings may not provide "
               "equal protection of the base metal against corrosion or "
               "abrasion in all environments, or both. Some environments "
               "may be so severe that none of the metallic coatings included "
               "in this specification will provide adequate protection."),
        pagina_pdf=2),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T4,
    nota=("RASTER PURO: leida sobre la PDF 2 renderizada a 130 dpi. LA "
          "NORMA DE PRODUCTO DEL TMC NO FIJA NINGUN UMBRAL de pH, "
          "resistividad, salinidad ni velocidad: reconoce que hay ambientes "
          "en que ningun recubrimiento metalico basta y remite la proteccion "
          "adicional a M 190 (recubrimiento bituminoso) y M 245 (precubierto "
          "de polimero), que no estan en normas/. Su 1.3 excluye ademas "
          "cama, relleno y la relacion entre carga de tierra y espesor de "
          "plancha."),
)

AASHTO_M36_T1 = _cita(
    id="AASHTO_M36.T1",
    fuente_id="AASHTO_M36",
    numeral="Table 1",
    titulo_numeral=("Corrugation Requirements for Type I, IA, II, IIA, and "
                    "III Pipe"),
    pagina_impresa="M 36-6",
    pagina_pdf=7,
    texto_literal=Verbatim(
        texto=("Depth is measured as the vertical distance from a "
               "straightedge resting on the corrugation crests parallel to "
               "the axis of the pipe to the bottom of the intervening "
               "valley."),
        pagina_pdf=7),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T4,
    nota=("RASTER PURO: leida sobre la PDF 7 renderizada a 100 dpi entera y "
          "el recorte de las Tablas 1 y 2 a 220 dpi. El `texto_literal` es la "
          "nota b de la tabla, y es la que hace falta: la PROFUNDIDAD de la "
          "corrugacion se mide de cresta a valle sobre la MISMA cara de la "
          "plancha, de modo que la altura total del perfil --lo que separa "
          "el diametro interior del exterior-- es profundidad MAS espesor de "
          "plancha. La nota sigue con el procedimiento de arbitraje de la "
          "Tabla 2 cuando una corrugacion mide menos que el minimo."),
)

AASHTO_M36_8_1_1 = _cita(
    id="AASHTO_M36.8.1.1",
    fuente_id="AASHTO_M36",
    numeral="8.1.1",
    titulo_numeral="Pipe Dimensions",
    pagina_impresa="M 36-10",
    pagina_pdf=11,
    texto_literal=Verbatim(
        texto=("The average inside diameter of circular pipe and pipe to be "
               "reformed into pipe-arches shall not vary more than 1 percent "
               "or 13 mm, whichever is greater, from the nominal diameter "
               "when measured on the inside crest of the corrugations for "
               "Type I pipe"),
        pagina_pdf=11),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=T4,
    nota=("RASTER PURO: leida sobre la mitad inferior de la PDF 11 "
          "renderizada a 170 dpi. EL DIAMETRO NOMINAL DEL TMC ES EL INTERIOR, "
          "MEDIDO EN LA CRESTA INTERIOR de las corrugaciones. Es lo que "
          "permite escribir D_ext = D + 2 x (profundidad de corrugacion + "
          "espesor de plancha). La primera frase del numeral manda elegir el "
          "diametro nominal de la Tabla 6 (AASHTO_M36.T6), que marca ademas "
          "las corrugaciones estandar de cada diametro; y el 8.1.2, misma "
          "pagina, que el espesor de plancha lo especifique el comprador de "
          "entre los de la Tabla 7."),
)

AASHTO_M36_T7 = _cita(
    id="AASHTO_M36.T7",
    fuente_id="AASHTO_M36",
    numeral="Table 7",
    titulo_numeral="Thicknesses of Metallic-Coated Steel Sheet",
    pagina_impresa="M 36-12",
    pagina_pdf=13,
    texto_literal=Verbatim(
        texto=("An “X” indicates sheet thickness included in the applicable "
               "specification for coating types listed."),
        pagina_pdf=13),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T4,
    nota=("RASTER PURO: leida sobre la PDF 13 renderizada a 100 dpi entera y "
          "el recorte de la tabla a 220 dpi. SIETE ESPESORES ESPECIFICADOS "
          "DE PLANCHA: 1.02, 1.32, 1.63, 2.01, 2.77, 3.51 y 4.27 mm; la "
          "columna del galvanizado (M 218, «Zinc Coated») los marca los "
          "siete. Son los mismos siete de las Tablas 3 a 9 de ASTM A796, que "
          "es donde estan sus propiedades seccionales (A, I, r). La Nota 9, "
          "debajo de la tabla, dice que el espesor requerido lo determina "
          "el comprador con los criterios de diseño de AASHTO («Standard "
          "Specifications for Highway Bridges, Division I, Section 12, or "
          "other appropriate guidelines»): la norma de producto LISTA los "
          "espesores y no elige ninguno."),
)


# --- T-4 (auditoria adversarial, H2) --- AASHTO M 170M-04: hasta que diametro
# hay DISEÑO ESTANDAR tabulado, y que pasa por encima. La ficha de
# 'D_max_norma_producto' decia que la serie del concreto llega a 3600 mm y
# que «faltaba transcribir» la pared de 2850 a 3600: la norma NO la tabula.
AASHTO_M170M_7_2_1 = _cita(
    id="AASHTO_M170M.7.2.1",
    fuente_id="AASHTO_M170M",
    numeral="7.2.1",
    titulo_numeral="Modified and Special Designs",
    pagina_impresa="M 170M-13",
    pagina_pdf=13,
    texto_literal=Verbatim(
        texto=("If permitted by the owner the manufacturer may request "
               "approval by the owner of modified designs that differ from "
               "the designs in Section 7.1; or special designs for sizes and "
               "loads beyond those shown in Tables 1 to 5, Section 7.1, or "
               "special designs for pipe sizes that do not have steel "
               "reinforcement areas shown in Tables 1 to 5 of Section 7.1."),
        pagina_pdf=13),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T4,
    nota=("Leida sobre la PDF 13 renderizada; la capa visible del ejemplar "
          "es un OCR defectuoso («pemiitted», «mquest», «reinfomenicnt») y la "
          "transcripcion corrige esas letras. LO QUE SOSTIENE: los tamaños "
          "que las Tablas 1 a 5 listan SIN area de acero no tienen diseño "
          "estandar; son diseños especiales que el fabricante propone y el "
          "propietario aprueba. LEIDO TABLA A TABLA SOBRE LAS PAGINAS "
          "RENDERIZADAS (T-4, 2026-11-11): Tabla 1 (Clase I, PDF 3), filas "
          "de 1500 a 2700 mm con pared y acero --la de 2700: pared A 225 mm, "
          "pared B 250 mm-- y filas de 2850, 3000, 3150, 3300 y 3450 mm con "
          "llamada a nota y rayas; Tabla 3 (Clase III, PDF 6-7), la ultima "
          "fila con acero es la de 2700 mm y las de 3000, 3150 y 3600 llevan "
          "llamada y rayas (las de 2850, 3300 y 3450 no se leen en el "
          "ejemplar); Tabla 5 (Clase V, PDF 10), pared tabulada hasta 1800 "
          "mm (AASHTO_M170M.T5). La nota al pie de las tablas, leida en la "
          "PDF 3 y en la PDF 5: «For modified or special designs, see "
          "Section 7.2 ...» y «Pipe over 2400 mm in diameter shall have two "
          "circular cages or an inner circular cage plus one elliptical "
          "cage». NO LEIDO: el cuerpo de la Tabla 2 (PDF 4) y el maximo de "
          "la Tabla 4, cuya mitad baja no esta en el escaneo. Con lo leido, "
          "el mayor diametro con diseño estandar es 2700 mm en las dos "
          "clases que se pudieron leer hasta el final."),
)

AASHTO_M170M_7_2_2 = _cita(
    id="AASHTO_M170M.7.2.2",
    fuente_id="AASHTO_M170M",
    numeral="7.2.2",
    titulo_numeral="Modified and Special Designs",
    pagina_impresa="M 170M-13",
    pagina_pdf=13,
    texto_literal=Verbatim(
        texto=("The descriptions of modified or special designs shall "
               "include the wall thickness, the concrete strength, and the "
               "area, type, placement, number of layers, and strength of the "
               "steel reinforcement."),
        pagina_pdf=13),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=T4,
    nota=("Leida sobre la PDF 13 renderizada, con el mismo OCR defectuoso "
          "(«conwetc strength», «rind st ngth»). EL ESPESOR DE PARED DE UN "
          "DISEÑO ESPECIAL LO DA EL FABRICANTE en su descripcion: la norma "
          "no lo tabula. Es la segunda frase del 7.2.2; la primera exige que "
          "el diseño se base en evaluaciones racionales o empiricas de la "
          "resistencia ultima y del agrietamiento. El 7.2.3 pide al "
          "fabricante la prueba de adecuacion (ensayos de tres aristas)."),
)


# --- T-4 (auditoria adversarial, H3, H9, H11) ---
AASHTO_LRFD_11_10_6_4_2A = _cita(
    id="AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO",
    fuente_id="AASHTO_LRFD_9",
    numeral="11.10.6.4.2a",
    titulo_numeral="Steel Reinforcements",
    pagina_impresa="11-89",
    pagina_pdf=1558,
    pagina_pdf_titulo=1557,     # el numeral abre en la 11-88; la lista, en la 11-89
    texto_literal=Verbatim(
        texto=("Soils shall typically be considered nonaggressive if they "
               "meet the following criteria:"),
        pagina_pdf=1558),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("El numeral abre en la pag. impresa 11-88 (PDF 1557) y la lista "
          "esta en la 11-89: pH = 5 to 10; Resistivity >= 3000 ohm-cm; "
          "Chlorides <= 100 ppm; Sulfates <= 200 ppm; Organic Content <= 1 "
          "percent. ES UN CRITERIO PARA EL RELLENO DE MUROS DE SUELO "
          "REFORZADO CON ACERO GALVANIZADO, no para alcantarillas: define en "
          "que suelo valen las tasas de perdida de galvanizado y de acero "
          "del propio articulo. El proyecto lo aplica al tubo de acero "
          "corrugado galvanizado POR ANALOGIA --mismo metal, mismo "
          "recubrimiento, mismo medio--, y por eso el efecto por defecto es "
          "un aviso y no una exclusion (criterio "
          "'suelo_agresivo_lrfd_sobre_tmc')."),
)

AASHTO_LRFD_11_12_8 = _cita(
    id="AASHTO_LRFD_9.11.12.8#AGRESIVO",
    fuente_id="AASHTO_LRFD_9",
    numeral="11.12.8",
    titulo_numeral="Corrosion Protection",
    pagina_impresa="11-134",
    pagina_pdf=1603,
    texto_literal=Verbatim(
        texto=("Soils not meeting one or more of these criteria shall be "
               "considered to be aggressive."),
        pagina_pdf=1603),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("Muros de suelo claveteado (soil nail). Repite la lista del "
          "11.10.6.4.2a con «Resistivity >= 3,000 ohm-cm» y «Organic Content "
          "<= 1 percent by weight», y añade las dos frases que aquel no "
          "trae: basta incumplir UNO de los criterios para que el suelo sea "
          "agresivo, y «If the resistivity is greater than or equal 5,000 "
          "ohm-cm, the chlorides and sulfates requirements may be waived». "
          "Esa dispensa es potestativa y la matriz NO la aplica: es el lado "
          "seguro."),
)

AASHTO_LRFD_10_7_5 = _cita(
    id="AASHTO_LRFD_9.10.7.5#INDICATIVOS",
    fuente_id="AASHTO_LRFD_9",
    numeral="10.7.5",
    titulo_numeral="Corrosion and Deterioration",
    pagina_impresa="10-125",
    pagina_pdf=1414,
    texto_literal=Verbatim(
        texto=("The following soil or site conditions should be considered "
               "as indicative of a potential pile deterioration or corrosion "
               "situation:"),
        pagina_pdf=1414),
    caracter=Caracter.RECOMENDACION,
    sesion=T4,
    nota=("PILOTES. La lista de suelo: «resistivity less than 2,000 ohm-cm», "
          "«pH less than 5.5», «pH between 5.5 and 8.5 in soils with high "
          "organic content», «sulfate concentrations greater than 1,000 "
          "ppm», rellenos sanitarios y de escoria, drenaje minero o "
          "industrial. La de agua: «chloride content greater than 500 ppm». "
          "El comentario C10.7.5 dice que los valores se adaptaron de Fang "
          "(1991) y Tomlinson (1987). SON INDICATIVOS («should be considered "
          "as indicative») Y MENOS ESTRICTOS que los del 11.10.6.4.2a salvo "
          "en el pH: se citan como segunda fuente del mismo cuerpo; los "
          "numeros que la matriz compara son los del 11.10.6.4.2a."),
)

E050_ART_24_REMOVER = _cita(
    id="E050.24#REMOVER",
    fuente_id="E050",
    numeral="Art. 24",
    titulo_numeral="Suelos no permitidos para apoyar las cimentaciones",
    pagina_impresa="37",
    pagina_pdf=37,
    texto_literal=Verbatim(
        texto=("Estos materiales no permitidos tienen que ser removidos en "
               "la totalidad del terreno, antes de ejecutar cualquier tipo "
               "de obra en el terreno y ser reemplazados con materiales que "
               "cumplan lo indicado en el numeral 25.4."),
        pagina_pdf=37),
    caracter=Caracter.EXIGENCIA,
    sesion=T4,
    nota=("La segunda frase del articulo, que la cita E050.24 no traia: la "
          "norma no se limita a prohibir cimentar sobre turba y suelo "
          "organico, MANDA REMOVERLOS Y REEMPLAZARLOS por relleno controlado. "
          "El aviso de suelo de fundacion deficiente lo dice con estas "
          "palabras (H9 de la auditoria de T-4)."),
)

E050_ART_38_1 = _cita(
    id="E050.38.1",
    fuente_id="E050",
    numeral="Art. 38, 38.1",
    titulo_numeral="Licuación de suelos",
    pagina_impresa="51",
    pagina_pdf=51,
    texto_literal=Verbatim(
        texto=("las vibraciones de los sismos pueden generar el fenómeno "
               "denominado Licuación, el cual consiste en la pérdida "
               "momentánea de la resistencia al corte del suelo"),
        pagina_pdf=51),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("El 38.1 lo dice de los suelos granulares y de algunos suelos "
          "granulares con finos cohesivos ubicados bajo la napa freatica; el "
          "38.2, en la misma pagina, lista las caracteristicas que el suelo "
          "tiene que presentar a la vez para ser susceptible, y el 38.5 "
          "(pag. 52) manda el analisis del potencial de licuacion por Seed e "
          "Idriss. ESTE PROGRAMA NO EVALUA LA LICUACION: la cita existe para "
          "que la linea «no esta entre los grupos declarados deficientes» "
          "de un suelo SM, SP o ML no se lea como «apto» (H9)."),
)

EG2013_508_02_A = _cita(
    id="EG2013.508.02a",
    fuente_id="EG2013",
    numeral="508.02 a",
    titulo_numeral="Tubos de polietileno de alta densidad (PAD o HDPE)",
    pagina_impresa="981",
    pagina_pdf=989,
    texto_literal=Verbatim(
        texto=("Es una tubería estructural con superficie interior lisa "
               "integrada y pared exterior corrugada."),
        pagina_pdf=989),
    caracter=Caracter.DEFINICION,
    sesion=T4,
    nota=("La norma peruana de construccion DEFINE el producto: interior "
          "liso y pared exterior corrugada; sigue «Debe cumplir con la guía "
          "AASHTO, clasificación tipo “S”» y remite a AASHTO M294. Respalda "
          "DOS cosas de T-4: que la fila de n que corresponde al HDPE en la "
          "Table B.1 de HDS-5 es la de interior liso («Smooth») y no la "
          "corrugada, y que el diametro exterior del tubo no es el interior "
          "mas una pared delgada sino mas la altura de un perfil corrugado."),
)


# ===========================================================================
# --- T-1 --- Manual de Hidrologia, cap. III: la hidrologia que calcula
# `MH_hidrologia` (cadena T, 2026-11-11)
# ===========================================================================
# Leidas por la sesion abriendo cada pagina por TEXTO, y las que llevan una
# formula tambien por IMAGEN (render a 110 dpi): la extraccion de texto parte
# las ecuaciones en renglones sueltos («385 .0 77 .0 . . 01947 .0») y de ahi
# no se transcribe un exponente. Desfase +3 en todas (pag. impresa + 3 = PDF).
#
# LO QUE EL PROMPT DE T-1 SUPONIA Y LA FUENTE NO TRAE, dicho donde se cita:
#   * la Tabla Nº 05 NO lista a Temez: sus seis filas son Kirpich, California
#     Culverts Practice, Izzard, Federal Aviation Administration, onda
#     cinematica y retardo SCS. La formula de Temez es la ecuacion (30) del
#     num. 3.12.2.1 «Método Racional Modificado» (pag. impresa 51), con L en
#     km y Tc en HORAS;
#   * la Tabla Nº 04 NO es de «coeficientes regionales»: es de coeficientes
#     de DURACION, de 1 a 48 horas;
#   * la Tabla Nº 08 NO tiene fila de pavimento ni de talud;
#   * el num. 3.12.2 NO trae ejemplo numerico;
#   * el limite del metodo racional es «A<10 Km2», desigualdad estricta.
FECHA_T1 = "2026-11-11"
POR_T1 = "tesis/T-1 · lectura directa de la pagina por la sesion"
T1 = (FECHA_T1, POR_T1)

MC_HHD_3_4_FEN = _cita(
    id="MC_HHD.3.4#FEN",
    fuente_id="MC_HHD",
    numeral="3.4",
    titulo_numeral="Evaluación de la Información Hidrológica",
    pagina_impresa="22",
    pagina_pdf=25,
    pagina_pdf_titulo=24,
    texto_literal=Verbatim(
        texto=("dicha información deberá incluir los años en que se han "
               "registrado los eventos del fenómeno “El Niño”, sin embargo "
               "dado que durante el evento del fenómeno del niño la "
               "información no es medida ya que normalmente se estiman "
               "valores extraordinarios, esta información debe ser evaluada "
               "de tal manera que no se originen sobredimensionamientos en "
               "las obras."),
        pagina_pdf=25),
    caracter=Caracter.EXIGENCIA,
    sesion=T1,
    nota=("El numeral abre en la pag. impresa 21 (PDF 24) y esta oracion "
          "esta en la 22 (PDF 25). Son DOS mandatos en una oracion y tiran "
          "en sentidos opuestos: la serie «deberá incluir» los años del "
          "Niño, y esos años deben «ser evaluados» para no "
          "sobredimensionar. La fuente no dice COMO evaluarlos: de ahi el "
          "criterio 'homogeneidad_serie_fen'."),
)

MC_HHD_3_4_REGISTRO = _cita(
    id="MC_HHD.3.4#REGISTRO",
    fuente_id="MC_HHD",
    numeral="3.4",
    titulo_numeral="Evaluación de la Información Hidrológica",
    pagina_impresa="22",
    pagina_pdf=25,
    pagina_pdf_titulo=24,
    texto_literal=Verbatim(
        texto="se recomienda contar con un mínimo de 25 años de registro",
        pagina_pdf=25),
    caracter=Caracter.RECOMENDACION,
    sesion=T1,
    derivado_de="MC_HHD.3.4#FEN",
    nota=("Misma oracion que MC_HHD.3.4#FEN, otra clausula. Es «se "
          "recomienda»: una serie mas corta no queda prohibida, y por eso "
          "el paso de la serie lo imprime como INDICADOR y no detiene."),
)

MC_HHD_3_7_1 = _cita(
    id="MC_HHD.3.7.1",
    fuente_id="MC_HHD",
    numeral="3.7.1",
    titulo_numeral="Modelos de distribución",
    jerarquia_numeral=("ANALISIS ESTADISTICO DE DATOS HIDROLOGICOS",),
    pagina_impresa="25",
    pagina_pdf=28,
    texto_literal=Verbatim(
        texto=("En la estadística existen diversas funciones de distribución "
               "de probabilidad teóricas; recomendándose utilizar las "
               "siguientes funciones:"),
        pagina_pdf=28),
    caracter=Caracter.RECOMENDACION,
    sesion=T1,
    nota=("La lista de ocho (i a viii) se imprime en la pag. impresa 26 "
          "(PDF 29): Normal, Log Normal 2 parámetros, Log Normal 3 "
          "parámetros, Gamma 2 parámetros, Gamma 3 parámetros, Log Pearson "
          "tipo III, Gumbel y Log Gumbel. El Manual imprime la funcion de "
          "cada una y SOLO de tres dice como se estiman sus parametros: la "
          "Normal (media y desviacion estandar, 3.7.1.1), la Log Normal de "
          "2 parametros (media y desviacion de los logaritmos, 3.7.1.2) y "
          "Gumbel (metodo de momentos, 3.7.1.7)."),
)

MC_HHD_3_7_1_1 = _cita(
    id="MC_HHD.3.7.1.1",
    fuente_id="MC_HHD",
    numeral="3.7.1.1",
    titulo_numeral="Distribución Normal",
    pagina_impresa="26",
    pagina_pdf=29,
    texto_literal=Verbatim(
        texto=("µ = parámetro de localización, igual a la media aritmética "
               "de x."),
        pagina_pdf=29),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("Ecuacion (2), la densidad normal. El renglon siguiente dice lo "
          "mismo del otro parametro: «S = parámetro de escala, igual a la "
          "desviación estándar de x.»"),
)

MC_HHD_3_7_1_2 = _cita(
    id="MC_HHD.3.7.1.2",
    fuente_id="MC_HHD",
    numeral="3.7.1.2",
    titulo_numeral="Distribución  Log  Normal  2  Parámetros",
    pagina_impresa="27",
    pagina_pdf=30,
    pagina_pdf_titulo=29,
    texto_literal=Verbatim(
        texto=("Donde Sy es la desviación estándar de los datos de la "
               "muestra transformada."),
        pagina_pdf=30),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("La pagina imprime, vistas en imagen, Y = Σ log xi / n y "
          "Sy = raiz( Σ (yi − Y)² / (n − 1) ): la desviacion es la MUESTRAL, "
          "con n − 1. El numeral escribe «y=log(x)» sin decir la base; el "
          "cuantil no depende de ella mientras se use la misma para ajustar "
          "y para invertir, y el proyecto usa el logaritmo natural."),
)

MC_HHD_3_7_1_7 = _cita(
    id="MC_HHD.3.7.1.7",
    fuente_id="MC_HHD",
    numeral="3.7.1.7",
    titulo_numeral="Distribución Gumbel",
    pagina_impresa="29",
    pagina_pdf=32,
    texto_literal=Verbatim(
        texto=("Utilizando el método de momentos, se obtienen las siguientes "
               "relaciones:"),
        pagina_pdf=32),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("Ecuacion (9): F(x) = exp(−exp(−α(x − β))). Las dos relaciones, "
          "vistas en imagen: α = 1.2825 / σ y β = µ − 0.45 σ. Los dos "
          "numeros son los que la pagina imprime (los exactos son π/√6 = "
          "1.28255 y 0.5772·√6/π = 0.45005). La pagina NO dice para que "
          "tamaño de muestra valen ni menciona correccion alguna por n."),
    interpretacion=Interpretacion(
        texto=("Las dos relaciones impresas son las de la distribucion de "
               "Gumbel para una muestra infinita (las asintoticas): no "
               "llevan la correccion por tamaño de muestra del factor de "
               "frecuencia de Gumbel-Chow. El proyecto las aplica tal como "
               "el Manual las imprime, a la serie del tamaño que sea."),
        en_contra=(
            "con series cortas las relaciones asintoticas dan un cuantil "
            "MENOR que el del factor de frecuencia corregido por el tamaño "
            "de la muestra, y la diferencia crece al acortarse la serie: es "
            "el lado no conservador",
            "el Manual no dice que sean asintoticas: es lectura del "
            "proyecto sobre los valores 1.2825 y 0.45, que son π/√6 y "
            "0.5772·√6/π",
        ),
        a_favor=(
            "son las unicas que el Manual imprime, y adoptar la correccion "
            "por n seria tomar un procedimiento de una fuente que no esta "
            "en normas/",
            "el paso del ajuste imprime la lluvia de las tres distribuciones "
            "evaluadas, de modo que el peso de esta eleccion queda a la vista",
        )),
)

MC_HHD_3_7_2_KS = _cita(
    id="MC_HHD.3.7.2b",
    fuente_id="MC_HHD",
    numeral="3.7.2 b)",
    titulo_numeral="b) Prueba Kolmogorov – Smirnov",
    jerarquia_numeral=("3.7.2 Pruebas de bondad de ajuste",),
    pagina_impresa="32",
    pagina_pdf=35,
    texto_literal=Verbatim(
        texto="Si D<d, se acepta la hipótesis nula.",
        pagina_pdf=35),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("D = máx |Fo(xm) − F(xm)| y, ecuacion (13), Fo(xm) = 1 − m/(n+1), "
          "con m el numero de orden del dato en una lista de MAYOR a menor. "
          "El valor critico d sale de la Tabla Nº 03 de la misma pagina. La "
          "desigualdad es estricta: D = d no acepta."),
)

MC_HHD_3_7_2_KS_ELIGE = _cita(
    id="MC_HHD.3.7.2b#ELIGE",
    fuente_id="MC_HHD",
    numeral="3.7.2 b)",
    titulo_numeral="b) Prueba Kolmogorov – Smirnov",
    jerarquia_numeral=("3.7.2 Pruebas de bondad de ajuste",),
    pagina_impresa="32",
    pagina_pdf=35,
    texto_literal=Verbatim(
        texto=("Método por el cual se comprueba la bondad de ajuste de las "
               "distribuciones, asimismo permite elegir la más "
               "representativa, es decir la de mejor ajuste."),
        pagina_pdf=35),
    caracter=Caracter.PERMISO,
    sesion=T1,
    derivado_de="MC_HHD.3.7.2b",
    nota=("Es lo que sostiene el valor de archivo del criterio "
          "'distribucion_precipitacion_maxima' (la de menor D): la fuente "
          "PERMITE elegir asi, no lo manda."),
)

MC_HHD_T03 = _cita(
    id="MC_HHD.3.7.2b#T03",
    fuente_id="MC_HHD",
    numeral="3.7.2 b)",
    titulo_numeral="b) Prueba Kolmogorov – Smirnov",
    jerarquia_numeral=("3.7.2 Pruebas de bondad de ajuste",),
    pagina_impresa="32",
    pagina_pdf=35,
    texto_literal=Verbatim(
        texto=("TABLA Nº 03: Valores críticos d para la prueba Kolmogorov – "
               "Smirnov"),
        pagina_pdf=35),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("La tabla empieza en la pag. impresa 32 (PDF 35: n = 5 a 25) y "
          "termina en la 33 (PDF 36: n = 30, 35 y 40, y «Fuente: Aparicio, "
          "1999.»)."),
)

MC_HHD_3_8_1_DURACION = _cita(
    id="MC_HHD.3.8.1#DURACION",
    fuente_id="MC_HHD",
    numeral="3.8.1",
    titulo_numeral="Curvas Intensidad – Duración – Frecuencia",
    pagina_impresa="36",
    pagina_pdf=39,
    pagina_pdf_titulo=36,
    texto_literal=Verbatim(
        texto=("La duración de la lluvia de diseño es igual al tiempo de "
               "concentración (tc) para el área de drenaje en consideración"),
        pagina_pdf=39),
    caracter=Caracter.DEFINICION,
    sesion=T1,
)

MC_HHD_T04 = _cita(
    id="MC_HHD.3.8.1#T04",
    fuente_id="MC_HHD",
    numeral="3.8.1",
    titulo_numeral="Curvas Intensidad – Duración – Frecuencia",
    pagina_impresa="36",
    pagina_pdf=39,
    pagina_pdf_titulo=36,
    texto_literal=Verbatim(
        texto=("los mismos que podrán usarse, con criterio y cautela para el "
               "cálculo de la intensidad, cuando no se disponga de mejor "
               "información."),
        pagina_pdf=39),
    caracter=Caracter.PERMISO,
    metodo=AMBOS,
    sesion=T1,
    nota=("La Tabla Nº 04 empieza en la pag. impresa 36 (PDF 39: 1 a 8 "
          "horas) y termina en la 37 (PDF 40: 10 a 48 horas). El coeficiente "
          "multiplica a la precipitacion maxima en 24 horas y da la "
          "PRECIPITACION de esa duracion; la intensidad es ese producto "
          "entre la duracion."),
)

MC_HHD_3_8_1_DICK_PESCHKE = _cita(
    id="MC_HHD.3.8.1#DICK_PESCHKE",
    fuente_id="MC_HHD",
    numeral="3.8.1",
    titulo_numeral="Curvas Intensidad – Duración – Frecuencia",
    pagina_impresa="37",
    pagina_pdf=40,
    pagina_pdf_titulo=36,
    texto_literal=Verbatim(
        texto=("Para el caso de duraciones de tormenta menores a 1 hora, o no "
               "se cuente con registros pluviográficos que permitan obtener "
               "las intensidades máximas, estas pueden ser calculadas  "
               "mediante la metodología de Dick Peschke (Guevara, 1991) que "
               "relaciona la duración de la tormenta con la precipitación "
               "máxima en 24 horas."),
        pagina_pdf=40),
    caracter=Caracter.PERMISO,
    metodo=AMBOS,
    sesion=T1,
    nota=("Ecuacion (16), vista en imagen: Pd = P24h · (d / 1440)^0.25, con "
          "d en MINUTOS y las dos precipitaciones en mm. Y a renglon "
          "seguido: «La intensidad se halla dividiendo la precipitación Pd "
          "entre la duración.» Las dos condiciones van unidas por «o»: "
          "basta con no tener registros pluviograficos, que es el caso de "
          "una serie de maximas en 24 horas."),
)

MC_HHD_T05 = _cita(
    id="MC_HHD.3.9#T05",
    fuente_id="MC_HHD",
    numeral="3.9",
    titulo_numeral="Tiempo de Concentración",
    pagina_impresa="39",
    pagina_pdf=42,
    pagina_pdf_titulo=41,
    texto_literal=Verbatim(
        texto=("Las ecuaciones para calcular el tiempo de concentración se "
               "muestran en la Tabla Nº 05."),
        pagina_pdf=42),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("La Tabla Nº 05 ocupa las pags. impresas 39 (PDF 42: Kirpich, "
          "California Culverts Practice, Izzard y Federal Aviation "
          "Administration) y 40 (PDF 43: ecuaciones de onda cinematica y "
          "ecuacion de retardo SCS). Su encabezado dice «FÓRMULA PARA tc "
          "(minutos)». NO lista a Temez."),
)

MC_HHD_T05_KIRPICH = _cita(
    id="MC_HHD.3.9#T05_KIRPICH",
    fuente_id="MC_HHD",
    numeral="3.9",
    titulo_numeral="Tiempo de Concentración",
    pagina_impresa="39",
    pagina_pdf=42,
    pagina_pdf_titulo=41,
    texto_literal=Verbatim(
        texto=("Desarrollada a partir de información del SCS en siete "
               "cuencas rurales de Tennessee con canales bien definidos y "
               "pendientes empinadas (3 a 10%)"),
        pagina_pdf=42),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T1,
    derivado_de="MC_HHD.3.9#T05",
    nota=("Fila «Kirpich (1940)». La formula, vista en imagen: "
          "tc = 0.01947 · L^0.77 · S^−0.385, con «L = longitud del canal "
          "desde aguas arriba hasta la salida, m.» y «S = pendiente promedio "
          "de la cuenca, m/m». La observacion sigue: para flujo superficial "
          "en superficies de concreto o asfalto se debe multiplicar tc por "
          "0.4; para canales de concreto, por 0.2; ningun ajuste para flujo "
          "superficial en suelo descubierto o para flujo en cunetas. El "
          "«(3 a 10%)» es la poblacion de la que salio la formula."),
    interpretacion=Interpretacion(
        texto=("La observacion de la Tabla N 05 DESCRIBE las cuencas de las "
               "que salio la formula (pendientes de 3 a 10 %); no prohibe "
               "usarla fuera. El proyecto la lee como poblacion de "
               "desarrollo, y que se hace con una cuenca fuera de ella lo "
               "decide el criterio 'tc_fuera_de_la_poblacion_del_metodo': no "
               "evaluar (valor de archivo) o evaluar con aviso. Y la S: la "
               "tabla la llama «pendiente promedio de la cuenca» y el "
               "proyecto le pasa la pendiente media del cauce principal "
               "(columna S_cauce_cuenca), que es la que acompaña a la "
               "longitud del canal de la misma formula."),
        en_contra=(
            "la tabla dice «pendiente promedio de la cuenca», no «del "
            "cauce»: la del terreno de la cuenca suele ser mayor que la del "
            "cauce, y con una S mayor la formula da un tiempo de "
            "concentracion menor y mas intensidad; pasarle la del cauce es "
            "el lado no conservador",
            "fuera de 3 a 10 % la formula sigue dando un numero y la tabla "
            "no dice que sea invalido: «no evaluar» es mas estricto que la "
            "fuente",
        ),
        a_favor=(
            "la formula original de Kirpich relaciona la longitud del canal "
            "con su desnivel, y la fila vecina de la misma tabla (California "
            "Culverts Practice, «esencialmente es la ecuación de Kirpich») "
            "usa el desnivel entre la divisoria y la salida sobre la "
            "longitud del curso de agua, que es la pendiente del cauce",
            "extrapolar una formula empirica fuera de las cuencas de las "
            "que salio es lo que la cadena de correcciones del proyecto "
            "(INF-3.1.2) señala como el riesgo de la llanura",
        )),
)

MC_HHD_T05_CALIFORNIA = _cita(
    id="MC_HHD.3.9#T05_CALIFORNIA",
    fuente_id="MC_HHD",
    numeral="3.9",
    titulo_numeral="Tiempo de Concentración",
    pagina_impresa="39",
    pagina_pdf=42,
    pagina_pdf_titulo=41,
    texto_literal=Verbatim(
        texto=("Esencialmente es la ecuación de Kirpich; desarrollada para "
               "pequeñas cuencas montañosas en California."),
        pagina_pdf=42),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T1,
    derivado_de="MC_HHD.3.9#T05",
    nota=("Fila «California Culverts Practice (1942)». La formula, vista en "
          "imagen: tc = 0.0195 · (L³ / H)^0.385, con «L = longitud del curso "
          "de agua más largo, m.» y «H = diferencia de nivel entre la "
          "divisoria de aguas y la salida, m.» La observacion NO escribe un "
          "rango numerico propio."),
    interpretacion=Interpretacion(
        texto=("La fila de California no escribe rango propio, pero dice de "
               "si misma que «esencialmente es la ecuación de Kirpich» y que "
               "se desarrollo para pequeñas cuencas montañosas. El proyecto "
               "le aplica por eso la MISMA poblacion de desarrollo que a "
               "Kirpich --pendiente de 3 a 10 %, medida aqui como H / L-- y "
               "el mismo criterio 'tc_fuera_de_la_poblacion_del_metodo': si "
               "Kirpich no se evalua para una cuenca, California tampoco."),
        en_contra=(
            "la fila de California no imprime el «(3 a 10%)»: aplicarselo "
            "es lectura del proyecto, no texto de la fuente",
        ),
        a_favor=(
            "con H = S·L las dos formulas dan el mismo numero (0.0195 "
            "frente a 0.01947, L^1.155·H^-0.385 frente a L^0.77·S^-0.385): "
            "sin el mismo trato, el limite de una se salta cambiando el "
            "nombre del metodo",
            "«pequeñas cuencas montañosas» es mas estrecho, no mas ancho, "
            "que «pendientes empinadas (3 a 10%)»",
        )),
)

MC_HHD_3_12_2 = _cita(
    id="MC_HHD.3.12.2",
    fuente_id="MC_HHD",
    numeral="3.12.2",
    titulo_numeral="Método Racional",
    jerarquia_numeral=("ESTIMACIÓN DE CAUDALES",),
    pagina_impresa="49",
    pagina_pdf=52,
    texto_literal=Verbatim(texto="Q = 0,278 CIA", pagina_pdf=52),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("Ecuacion (28). Las unidades estan en la pag. impresa 50 (PDF "
          "53): Q «Descarga máxima de diseño (m3/s)», C «Coeficiente de "
          "escorrentía (Ver Tabla Nº 08)», I «Intensidad de precipitación "
          "máxima horaria (mm/h)», A «Área de la cuenca (Km2).» El 0,278 es "
          "1/3.6, la conversion de mm/h·km² a m³/s: es el mismo cociente "
          "que el num. 4.1.2.1 b) escribe como C·I·A/3.6. El numeral NO "
          "trae ejemplo numerico."),
)

MC_HHD_3_12_2_AREA = _cita(
    id="MC_HHD.3.12.2#AREA",
    fuente_id="MC_HHD",
    numeral="3.12.2",
    titulo_numeral="Método Racional",
    jerarquia_numeral=("ESTIMACIÓN DE CAUDALES",),
    pagina_impresa="49",
    pagina_pdf=52,
    texto_literal=Verbatim(texto="Muy usado para cuencas, A<10 Km2.",
                           pagina_pdf=52),
    caracter=Caracter.APROXIMACION,
    sesion=T1,
    derivado_de="MC_HHD.3.12.2",
    nota=("La desigualdad es ESTRICTA: 10 km² exactos quedan fuera. Y el "
          "verbo es descriptivo («Muy usado para»): la fuente no prohibe el "
          "metodo por encima, dice donde se usa. El proyecto lo aplica como "
          "limite de validez y por encima no evalua, remitiendo al "
          "hidrograma unitario del num. 3.12.3."),
)

MC_HHD_T08 = _cita(
    id="MC_HHD.3.12.2#T08",
    fuente_id="MC_HHD",
    numeral="3.12.2",
    titulo_numeral="Método Racional",
    jerarquia_numeral=("ESTIMACIÓN DE CAUDALES",),
    pagina_impresa="50",
    pagina_pdf=53,
    pagina_pdf_titulo=52,
    texto_literal=Verbatim(
        texto=("El valor del coeficiente de escorrentía se establecerá de "
               "acuerdo a las características hidrológicas y geomorfológicas "
               "de las quebradas cuyos cursos interceptan el alineamiento de "
               "la carretera en estudio."),
        pagina_pdf=53),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=T1,
    nota=("Es la oracion que sigue a la Tabla Nº 08. La tabla da el NUMERO; "
          "que fila describe a la cuenca lo establece el estudio, con sus "
          "caracteristicas: por eso cobertura y suelo son columnas del CSV "
          "de cuencas y no una eleccion del programa."),
)

MC_HHD_3_12_2_1_TC = _cita(
    id="MC_HHD.3.12.2.1#TC",
    fuente_id="MC_HHD",
    numeral="3.12.2.1",
    titulo_numeral="Método Racional Modificado",
    pagina_impresa="51",
    pagina_pdf=54,
    pagina_pdf_titulo=53,
    texto_literal=Verbatim(
        texto=("drenaje naturales con áreas menores de 770 km2 y con tiempos "
               "de concentración (Tc) de entre 0.25 y 24 horas"),
        pagina_pdf=54),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T1,
    nota=("Ecuacion (30), apartado «A) Tiempo de Concentración (Tc)», vista "
          "en imagen: Tc = 0.3 · (L / S^0.25)^0.76, con «L= Longitud del "
          "cauce mayor (km)» y «S= Pendiente promedio del cauce mayor "
          "(m/m)»; Tc sale en HORAS (lo dicen el rango de arriba y el "
          "apartado B). Es la formula de Temez, y vive AQUI y no en la "
          "Tabla Nº 05. El rango de area y de Tc es el del metodo racional "
          "modificado entero, del que esta formula es una pieza: el "
          "proyecto toma SOLO la formula del tiempo de concentracion y le "
          "aplica ese rango como validez; no usa el resto del metodo "
          "(coeficiente de uniformidad, factor reductor, numero de curva)."),
)

MC_HHD_3_13 = _cita(
    id="MC_HHD.3.13",
    fuente_id="MC_HHD",
    numeral="3.13",
    titulo_numeral="Avenida de Diseño",
    pagina_impresa="65",
    pagina_pdf=68,
    texto_literal=Verbatim(
        texto=("La Avenida de Diseño es el caudal que se escoge, mediante "
               "diversas consideraciones, para dimensionar un proyecto (o "
               "una parte de él)."),
        pagina_pdf=68),
    caracter=Caracter.DEFINICION,
    sesion=T1,
    nota=("El numeral no da formula ni umbral: remite al estudio hidrologico "
          "(«Estimación de Caudales») y a «la experiencia y el buen tino del "
          "ingeniero proyectista». Por eso el caudal especifico Q/A se "
          "imprime como contraste y no se juzga contra nada."),
)

MC_HHD_CUNETA_APORTE = _cita(
    id="MC_HHD.4.1.2.1b",
    fuente_id="MC_HHD",
    numeral="4.1.2.1 b)",
    titulo_numeral="b) Caudal Q de aporte",
    jerarquia_numeral=("4.1.2.1 Cunetas",),
    pagina_impresa="177",
    pagina_pdf=180,
    texto_literal=Verbatim(
        texto=("Es el caudal calculado en el área de aporte correspondiente "
               "a la longitud de cuneta. Se calcula mediante la siguiente "
               "expresión:"),
        pagina_pdf=180),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("La expresion, vista en imagen: Q = C·I·A / 3.6, con Q en m3/s, "
          "«C : Coeficiente de escurrimiento de la cuenca», «A : Área "
          "aportante en Km2» e «I : Intensidad de la lluvia de diseño en "
          "mm/h». Es la ecuacion (28) del num. 3.12.2 con el 0,278 escrito "
          "como 1/3.6. La pagina le imprime DOS numeros de ecuacion, (118) y "
          "(147): no se cita por numero."),
)

# --- T-1, tras el auditor adversarial: las otras filas de la Tabla N 05, el
# coeficiente de uniformidad del metodo de Temez, el tratamiento especial de
# Piura y Tumbes, y las tres citas de WSDOT que cubren lo que el Manual no fija
# (duracion minima de la lluvia y coeficiente de una superficie pavimentada).

MC_HHD_T05_FAA = _cita(
    id="MC_HHD.3.9#T05_FAA",
    fuente_id="MC_HHD",
    numeral="3.9",
    titulo_numeral="Tiempo de Concentración",
    pagina_impresa="39",
    pagina_pdf=42,
    pagina_pdf_titulo=41,
    texto_literal=Verbatim(
        texto=("Desarrollada de información sobre el drenaje de aeropuertos "
               "recopilada por el Corps of Engineers: el método tiene como "
               "finalidad el ser usado en problemas de drenaje de aeropuertos "
               "pero ha sido frecuentemente usado para flujo superficial en "
               "cuencas urbanas."),
        pagina_pdf=42),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T1,
    derivado_de="MC_HHD.3.9#T05",
    nota=("Fila «Federal Aviation Administration (1970)». La formula, vista "
          "en imagen: tc = 0.7035 · (1.1 − C) · L^0.50 / S^0.333, con «C = "
          "coeficiente de escorrentía del método racional», «L = longitud "
          "del flujo superficial, m.» y «S = pendiente de la superficie, "
          "m/m». Es una formula de FLUJO SUPERFICIAL (sobre una superficie, "
          "no por un cauce) y la observacion no le escribe rango numerico: "
          "es la que el proyecto ofrece para una plataforma, un talud o una "
          "cuenca plana sin cauce definido."),
)

MC_HHD_T05_SCS = _cita(
    id="MC_HHD.3.9#T05_SCS",
    fuente_id="MC_HHD",
    numeral="3.9",
    titulo_numeral="Tiempo de Concentración",
    pagina_impresa="40",
    pagina_pdf=43,
    pagina_pdf_titulo=41,
    texto_literal=Verbatim(
        texto=("Ecuación desarrollada por el SCS a partir de información de "
               "cuencas de uso agrícola; ha sido adaptada a pequeñas cuencas "
               "urbanas con áreas inferiores a 800 Ha"),
        pagina_pdf=43),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T1,
    derivado_de="MC_HHD.3.9#T05",
    nota=("Fila «Ecuación de retardo SCS (1973)». La formula, vista en "
          "imagen: tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 / S^0.5, con «L = "
          "longitud hidráulica de la cuenca (mayor trayectoria de flujo), "
          "m.», «CN = Número de curva SCS» y «S = pendiente promedio de la "
          "cuenca, m/m». La observacion sigue: buena cuando el area esta "
          "completamente pavimentada, tiende a sobreestimar en areas mixtas, "
          "y «la ecuación supone que tc = 1.67 x retardo de la cuenca». Las "
          "«800 Ha» son la poblacion a la que se adapto; el proyecto las "
          "trata como a los «3 a 10%» de Kirpich."),
)

MC_HHD_3_12_2_1_K = _cita(
    id="MC_HHD.3.12.2.1#K",
    fuente_id="MC_HHD",
    numeral="3.12.2.1",
    titulo_numeral="Método Racional Modificado",
    pagina_impresa="51",
    pagina_pdf=54,
    pagina_pdf_titulo=53,
    texto_literal=Verbatim(texto="Q =   0,278 CIAK", pagina_pdf=54),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=T1,
    nota=("Ecuacion (29), con «K : Coeficiente de Uniformidad». Su apartado "
          "«B) Coeficiente de Uniformidad» da la ecuacion (31), vista en "
          "imagen: K = 1 + Tc^1.25 / (Tc^1.25 + 14), con «Tc= Tiempo de "
          "concentración (horas)». K es siempre mayor que 1 y crece con Tc "
          "(1.01 a 0.25 h, 1.07 a 1 h, 1.79 a 24 h). El metodo trae ademas "
          "su propia intensidad (ec. 34), su factor reductor por area (ec. "
          "32) y su coeficiente C por numero de curva (ec. 35), que el "
          "proyecto NO usa: toma la formula del tiempo de concentracion "
          "(ec. 30) y, con ella, este coeficiente."),
)

MC_HHD_3_12_5_PIURA = _cita(
    id="MC_HHD.3.12.5#PIURA",
    fuente_id="MC_HHD",
    numeral="3.12.5",
    titulo_numeral="Otras Metodologías",
    pagina_impresa="64",
    pagina_pdf=67,
    pagina_pdf_titulo=65,
    texto_literal=Verbatim(
        texto=("departamentos de Piura y Tumbes, donde es necesario un "
               "tratamiento especial del análisis para determinar el caudal "
               "de diseño."),
        pagina_pdf=67),
    caracter=Caracter.EXIGENCIA,
    sesion=T1,
    nota=("La oracion entera: «Otra metodología es la que resalte la "
          "influencia de El Fenómeno “El Niño”, en especial en la Vertiente "
          "del Pacífico del Perú, departamentos de Piura y Tumbes, donde es "
          "necesario un tratamiento especial del análisis para determinar "
          "el caudal de diseño.» El Manual lo dice de los caudales y no da "
          "el tratamiento; el proyecto lo imprime en la memoria hidrologica "
          "porque el ajuste de una sola distribucion a una serie con años "
          "de El Niño puede dejar la lluvia de diseño por debajo de lo ya "
          "observado, y eso se avisa en el paso del ajuste."),
)

WSDOT_TC_MINIMO = _cita(
    id="WSDOT_HM.2-6.3#TC_MINIMO",
    fuente_id="WSDOT_HM",
    numeral="2-6.3",
    titulo_numeral="Time of Concentration",
    pagina_impresa="2-10",
    pagina_pdf=46,
    pagina_pdf_titulo=45,
    texto_literal=Verbatim(
        texto=("If the total time of concentration is less than 5 minutes, a "
               "minimum of 5 minutes shall be used as the duration (see "
               "Section 2-6.4 for details)."),
        pagina_pdf=46),
    caracter=Caracter.EXIGENCIA,
    sesion=T1,
    nota=("El num. 2-6.4 «Rainfall Intensity» (pag. impresa 2-11, PDF 47) "
          "lo repite --«PEOs shall never use a time of concentration that is "
          "less than 5 minutes for intensity calculations»-- y da las dos "
          "razones: las curvas intensidad-duracion por debajo de ese tiempo "
          "son extrapolacion, y la lluvia tarda en generar escorrentia. Es "
          "una exigencia de WSDOT para SUS curvas; aqui cubre un vacio del "
          "Manual peruano (que no fija duracion minima, barrido entero) y "
          "entra como [C], no como norma."),
)

WSDOT_T2_2 = _cita(
    id="WSDOT_HM.2-6.2#T2-2",
    fuente_id="WSDOT_HM",
    numeral="2-6.2",
    titulo_numeral="Runoff Coefficients",
    pagina_impresa="2-9",
    pagina_pdf=45,
    pagina_pdf_titulo=44,
    texto_literal=Verbatim(
        texto=("Runoff Coefficients for the Rational Method: 10-Year Return "
               "Frequency"),
        pagina_pdf=45),
    caracter=Caracter.DEFINICION,
    sesion=T1,
    nota=("Table 2-2: veintiseis coberturas por tres columnas de pendiente "
          "(Flat, Rolling 2%–10%, Hilly Over 10%). «Pavement and roofs» vale "
          "0.90 en las tres; «Side slopes, earth» 0.60; «Side slopes, turf» "
          "0.30; «Earth shoulders» 0.50. Son coeficientes para una tormenta "
          "de 10 años de periodo de retorno: ver WSDOT_HM.2-6.2#FRECUENCIA."),
)

WSDOT_C_FRECUENCIA = _cita(
    id="WSDOT_HM.2-6.2#FRECUENCIA",
    fuente_id="WSDOT_HM",
    numeral="2-6.2",
    titulo_numeral="Runoff Coefficients",
    pagina_impresa="2-8",
    pagina_pdf=44,
    texto_literal=Verbatim(
        texto=("Generally, when designing for a 25-year frequency, the "
               "coefficient shall be increased by 10 percent; when designing "
               "for a 50-year frequency, the coefficient shall be increased "
               "by 20 percent; and when designing for a 100-year frequency, "
               "the coefficient shall be increased by 25 percent."),
        pagina_pdf=44),
    caracter=Caracter.EXIGENCIA,
    sesion=T1,
    nota=("La oracion anterior fija la base: «The coefficients in Table 2-2 "
          "are applicable for peak storms of 10-year frequency.» Y la "
          "siguiente el tope: «The runoff coefficient shall not be increased "
          "above 0.95, unless approved by the RHE.» La fuente nombra tres "
          "frecuencias (25, 50 y 100 años) y no dice que hacer entre ellas "
          "ni por encima de 100."),
)

# ===========================================================================
# --- T-6 --- Geometria: longitud por extremo, esviaje, pendiente y entrega
# (INF-3.3.3, INF-5.1.18). Nueve citas, leidas por la sesion contra el PDF:
# por TEXTO las ocho de articulado y por IMAGEN la Lamina N 01, que es un
# plano. Ninguna fija un NUMERO de proyecto: sostienen el PROCEDIMIENTO
# (longitud aproximada sobre la seccion transversal y encaje posterior,
# HDS-5), la CONVENCION del esviaje (HDS-5 5.4.1), el unico pronunciamiento
# de fuente sobre un maximo practico (HDS-5 5.4.2, del esviaje de la
# EMBOCADURA) y lo que el Manual del MTC exige de la ubicacion y de la
# pendiente. El desnivel de entrega y el esviaje maximo siguen siendo [A].
# ===========================================================================

MC_HHD_4_1_1_3_2 = _cita(
    id="MC_HHD.4.1.1.3.2",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.2",
    titulo_numeral="Ubicación en planta",
    pagina_impresa="71",
    pagina_pdf=74,
    pagina_pdf_titulo=74,
    texto_literal=Verbatim(
        texto=("La ubicación en planta ideal es la que sigue la dirección de "
               "la corriente"),
        pagina_pdf=74),
    # DEFINICION: dice cual es la ubicacion «ideal», no la manda. La oracion
    # sigue con un PERMISO («sin embargo, según requerimiento del Proyecto
    # la ubicación natural puede desplazarse, lo cual implica el
    # acondicionamiento del cauce»), que es lo que hace del esviaje un dato
    # de entrada y no un incumplimiento.
    caracter=Caracter.DEFINICION,
    sesion=T6,
    nota=("El numeral NO da un esviaje maximo ni una longitud: dice que lo "
          "ideal es seguir la corriente y que desplazar la ubicacion natural "
          "obliga a acondicionar el cauce a la entrada y a la salida con "
          "obras de encauzamiento. Es el fundamento de que el conducto se "
          "tienda esviado (factor 1/cos) en vez de rectificar el cruce."),
)

# `MC_HHD.4.1.1.3.3` («Pendiente longitudinal», pag. impresa 71) NO se
# transcribe aqui: la dio de alta T-2 de la cadena T, que se integro antes,
# con el mismo id y la oracion entera. T-6 la CONSUME (F7.PENDIENTE, y como
# cita secundaria de F7.ENTREGA y de G2) y no la duplica. Lo que T-6 lee en
# ella, y conviene tener escrito junto a sus consumidores: son dos oraciones
# sin cifra, que hablan de la PENDIENTE y no de la entrega al receptor ni del
# remanso; quien la cite para un desnivel minimo de entrega le atribuye lo
# que no dice.

LAMINA_01 = _cita(
    id="MC_HHD.LAMINA_01",
    fuente_id="MC_HHD",
    numeral="Lámina Nº 01",
    # El cajetin imprime el titulo en tres renglones apilados («UBICACIÓN
    # TÍPICA DE ALCANTARILLAS» / «RESPECTO A LA PENDIENTE» / «DEL CAUCE») y
    # la capa de texto los entrega como corridas separadas: se guarda el
    # primero, por la misma limitacion declarada en `MC_HHD.LAMINA_03`.
    titulo_numeral="UBICACIÓN TÍPICA DE ALCANTARILLAS",
    jerarquia_numeral=(),
    pagina_impresa="206",
    pagina_pdf=209,
    pagina_pdf_titulo=209,
    texto_literal=Verbatim(
        texto="c) SALIDA SOBRE LA PENDIENTE NATURAL",
        pagina_pdf=209),
    # DEFINICION: la lamina TIPIFICA cinco ubicaciones y no manda ninguna.
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T6,
    nota=("Es un plano, leido sobre la pagina renderizada. Cinco esquemas: "
          "a) siguiendo la pendiente natural del cauce; b) entrada bajo la "
          "pendiente natural; c) salida sobre la pendiente natural; d) "
          "entrada bajo y salida sobre la pendiente natural; e) pendientes "
          "pronunciadas (con muro y anclaje). En a) el conducto va de "
          "cabezal a cabezal sobre el fondo del cauce y los taludes del "
          "terraplen mueren en la coronacion de los cabezales. En c) y d) la "
          "salida queda POR ENCIMA del cauce, con dos notas del propio "
          "plano: «la posibilidad de dejar el tubo en voladizo debe ser "
          "analizada estructuralmente. El terreno a la salida debe ser roca "
          "u otro material resistente a la erosión» y «alcantarillas "
          "pequeñas pueden descargar con seguridad sobre un talud de "
          "enrocado». NO ACOTA NINGUNA DIMENSION: ni el desnivel de la "
          "salida ni la longitud. Sostiene que una salida elevada sobre el "
          "fondo del receptor exige proteccion, y por eso el desnivel de "
          "entrega no es conservador en un solo sentido."),
)

HDS5_2_2_4_LONGITUD = _cita(
    id="HDS5_3ED.2.2.4#LONGITUD",
    fuente_id="HDS5_3ED",
    numeral="2.2.4 b.",
    titulo_numeral="Roadway Data",
    pagina_impresa="2.8",
    pagina_pdf=70,
    pagina_pdf_titulo=69,
    texto_literal=Verbatim(
        texto=("These elevations and the resulting culvert length are "
               "approximate since the final culvert barrel size must still "
               "be determined."),
        pagina_pdf=70),
    # APROXIMACION, y la palabra es de la fuente: «approximate».
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=T6,
    nota=("Inciso «b. Culvert Length» del num. 2.2.4, que abre en la pag. "
          "impresa 2.7 (PDF 69). Las dos oraciones anteriores dicen COMO se "
          "obtiene: «The dimensions are obtained by superimposing the "
          "estimated culvert barrel on the roadway cross section and the "
          "streambed profile (Figure 2.4). This superposition establishes "
          "the inlet and outlet invert elevations». La Figura 2.4 (misma "
          "pagina, leida por imagen) dibuja la seccion A-A SOBRE EL EJE "
          "ESVIADO del conducto, con tres cotas rotuladas en la corona "
          "-- «Pavement Elevation» en el borde izquierdo, «Centerline "
          "Elevation» en el eje y «Shoulder Elevation» en el borde derecho "
          "--, el talud «Se : 1» y un «Upstream Invert» mas alto que el "
          "«Downstream Invert»: un talud a cada lado y dos fondos a cotas "
          "distintas, no dos taludes iguales medidos en el eje. LOS TALUDES "
          "DE LA FIGURA MUEREN EN LA CARA SUPERIOR DEL BARRIL, no en su "
          "fondo. La cita sostiene la superposicion APROXIMADA del barril "
          "estimado y nada mas: que el proyecto baje cada talud hasta el "
          "fondo -- un barril de altura cero, porque la seccion no se "
          "conoce todavia -- es eleccion suya, declarada en el criterio "
          "'metodo_longitud_conducto', y da la cota superior de la "
          "longitud. El inciso «a. Cross Section» de la misma pagina añade "
          "que la seccion que el proyectista necesita es la del cruce, "
          "«skewed with reference to the roadway centerline»."),
)

HDS5_3_1_4_LONGITUD = _cita(
    id="HDS5_3ED.3.1.4#LONGITUD",
    fuente_id="HDS5_3ED",
    numeral="3.1.4",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.9",
    pagina_pdf=91,
    pagina_pdf_titulo=87,
    texto_literal=Verbatim(
        texto=("Because the design height of the barrel and the slope "
               "influence the actual length, an approximation of barrel "
               "length is usually necessary to begin the design process."),
        pagina_pdf=91),
    caracter=Caracter.APROXIMACION,
    sesion=T6,
    nota=("Lista «Factors Influencing Outlet Control», que empieza en la "
          "pag. impresa 3.8 (PDF 90); el numeral abre en la 3.5 (PDF 87). La oracion anterior define la "
          "magnitud: «Barrel length is the total culvert length from the "
          "entrance to the exit of the culvert». Es la razon, escrita por "
          "la fuente, de que la longitud del diseño hidraulico se calcule "
          "ANTES de conocer la seccion y por eso sin su altura: la altura "
          "del barril y la pendiente mueven la longitud real, y el diseño "
          "arranca con una aproximacion."),
)

HDS5_3_3_5_ENCAJE = _cita(
    id="HDS5_3ED.3.3.5#ENCAJE",
    fuente_id="HDS5_3ED",
    numeral="3.3.5",
    titulo_numeral="Evaluation of Results",
    pagina_impresa="3.25",
    pagina_pdf=107,
    pagina_pdf_titulo=107,
    texto_literal=Verbatim(
        texto=("Once the barrel is selected it must be fitted into the "
               "roadway cross section."),
        pagina_pdf=107),
    caracter=Caracter.EXIGENCIA,
    sesion=T6,
    nota=("La oracion que sigue dice que se comprueba al encajar: «The "
          "culvert barrel must have adequate cover, the length should be "
          "close to the approximate length, and the headwalls and wingwalls "
          "must be dimensioned». La cobertura es G1 (7.A); la longitud "
          "«close to the approximate length» es el paso 7.B.5 de este "
          "proyecto, que la fuente escribe con «should» y SIN TOLERANCIA: no "
          "hay cifra de cuanto es «close», y el proyecto no la inventa -- "
          "imprime las dos longitudes y su diferencia."),
)

HDS5_5_4_1_ESVIAJE = _cita(
    id="HDS5_3ED.5.4.1#ESVIAJE",
    fuente_id="HDS5_3ED",
    numeral="5.4.1",
    titulo_numeral="Skewed Barrels",
    pagina_impresa="5.12",
    pagina_pdf=148,
    pagina_pdf_titulo=148,
    texto_literal=Verbatim(
        texto=("For any other alignment, the barrel skew angle is the angle "
               "from a line normal to the highway to the culvert centerline."),
        pagina_pdf=148),
    caracter=Caracter.DEFINICION,
    sesion=T6,
    nota=("Es la convencion de `esviaje_grados`: 0 = perpendicular («A "
          "culvert aligned normal to the roadway centerline has a zero "
          "barrel skew angle», oracion anterior). El mismo numeral nombra la "
          "consecuencia geometrica que 1/cos(esviaje) cuantifica: tender el "
          "barril sobre el cauce tiene la desventaja de que «the inlet may "
          "be skewed with respect to the culvert barrel and the culvert "
          "will be longer»."),
)

HDS5_5_4_2_MAXIMO = _cita(
    id="HDS5_3ED.5.4.2#MAXIMO_PRACTICO",
    fuente_id="HDS5_3ED",
    numeral="5.4.2",
    titulo_numeral="Skewed Inlets",
    pagina_impresa="5.13",
    pagina_pdf=149,
    pagina_pdf_titulo=149,
    texto_literal=Verbatim(
        texto=("The inlet skew angle varies from 0-degrees to a practical "
               "maximum of about 45-degrees."),
        pagina_pdf=149),
    # RECOMENDACION, y es la lectura mas debil que la frase admite: la
    # fuente DESCRIBE un maximo practico («about»), sin «shall» ni «should».
    # No es EXIGENCIA y por eso el tope del proyecto es aviso y no bloqueo.
    caracter=Caracter.RECOMENDACION,
    sesion=T6,
    nota=("HABLA DEL ESVIAJE DE LA EMBOCADURA («inlet skew angle», el "
          "angulo de la cara del conducto con la normal al barril), NO del "
          "esviaje del barril. La oracion siguiente da la razon -- «The "
          "upper limit is dictated by the difficulty in transitioning the "
          "flow from the stream into the culvert» -- y el parrafo siguiente "
          "el puente entre los dos angulos: «Culverts which have a barrel "
          "skew angle often have an inlet skew angle as well. This is "
          "because headwalls are generally constructed parallel to a "
          "roadway centerline to avoid warping of the embankment fill». Con "
          "el cabezal PARALELO a la via, que es la disposicion que este "
          "proyecto supone (terraplen sin alabear), el esviaje de la "
          "embocadura es igual al del barril y el maximo practico de 45 "
          "grados le alcanza; con el terraplen alabeado para dejar la "
          "embocadura normal al barril (Figura 5.16) no le alcanza. Por eso "
          "'esviaje_max_grados' es [A] y no [C]: la analogia depende de una "
          "disposicion constructiva que el expediente decide."),
)

DG2018_304_05_BOMBEO = _cita(
    id="DG2018.304.05#BOMBEO",
    fuente_id="DG2018",
    numeral="304.05",
    titulo_numeral="Bombeo",
    pagina_impresa="195",
    pagina_pdf=196,
    pagina_pdf_titulo=196,
    texto_literal=Verbatim(
        texto=("En tramos en tangente o en curvas en contraperalte, las "
               "calzadas deben tener una inclinación transversal mínima "
               "denominada bombeo, con la finalidad de evacuar las aguas "
               "superficiales."),
        pagina_pdf=196),
    caracter=Caracter.EXIGENCIA,
    sesion=T6,
    nota=("La Tabla 304.03 «Valores del bombeo de la calzada» (misma "
          "pagina) da 2.0 % y 2.5 % para pavimento asfaltico o de concreto "
          "Portland segun la precipitacion sea menor o mayor de 500 mm/año, "
          "2.5 % y 2.5-3.0 % para tratamiento superficial y 3.0-3.5 % y "
          "3.0-4.0 % para afirmado. NO SE TRANSCRIBE como tabla ni se adopta "
          "un valor: el bombeo de la seccion tipica es un dato del trazo "
          "(dato externo 'bombeo'), y sin el la plataforma se toma "
          "horizontal a la cota de rasante. La berma lleva su propia "
          "inclinacion (num. 304.04.02, Figura 304.03), de modo que el dato "
          "que entra es la pendiente transversal MEDIA de la semiplataforma."),
)

DG2018_304_06_PERALTE = _cita(
    id="DG2018.304.06#PERALTE",
    fuente_id="DG2018",
    numeral="304.06",
    titulo_numeral="Peralte",
    pagina_impresa="196",
    pagina_pdf=197,
    pagina_pdf_titulo=197,
    texto_literal=Verbatim(
        texto=("Inclinación transversal de la carretera en los tramos de "
               "curva, destinada a contrarrestar la fuerza centrífuga del "
               "vehículo."),
        pagina_pdf=197),
    caracter=Caracter.DEFINICION,
    sesion=T6,
    nota=("Los maximos de la Tabla 304.05 (misma pagina: 4.0 a 12.0 % segun "
          "la zona) no se usan aqui. El peralte del cruce es un dato del "
          "trazo (dato externo 'peralte'): sube un borde de la plataforma y "
          "baja el otro."),
)

# ===========================================================================
# --- T-8 --- (cadena T) · proteccion de entrada y salida, socavacion local
# ===========================================================================
# Mismo regimen que T-0 y T-2: la propia sesion abrio cada pagina por su capa
# de texto, y las que llevan una ECUACION o una FIGURA ademas por imagen
# (HEC-14 PDF 54, 60, 204 y 218; Manual MTC PDF 80 y Laminas 02 a 05), y la
# firma lo dice. HEC-14 imprime sus ecuaciones partidas en renglones sueltos
# (nota de `fuentes.HEC14`): la formula de cada una va en la `nota`, leida de
# la pagina renderizada, y el `texto_literal` es la frase de prosa que la
# introduce, que es lo que T2 puede buscar.
#
# LOS CAPITULOS REALES DE HEC-14, porque la cadena T los cita de memoria: la
# socavacion a la salida es el Capitulo 5 (no el 3), y los aprons y pozas de
# enrocado el 10. Verificado sobre el ejemplar; el indice completo esta en
# la `nota` de `fuentes.HEC14`.
FECHA_TESIS_T8 = "2026-11-12"
POR_TESIS_T8 = "tesis/T-8 · lectura directa de la pagina por la sesion"
TESIS_T8 = (FECHA_TESIS_T8, POR_TESIS_T8)

# ---- Segunda auditoria de T-8 (H6): TRES LECTURAS DEL PROYECTO con efecto
# en lo que la Fase 6 calcula o declara, que viajaban como «procedencia» o
# como `por_que` y se leian como texto de la fuente. Cada una cuelga de la
# cita que interpreta, y el paso que la aplica la imprime en la cara del
# proyecto (`nota_del_proyecto`), leida de aqui: no se transcribe dos veces.
INTERPRETACION_VELOCIDAD_ALTA = Interpretacion(
    texto=("El Manual recomienda proteger el cauce «si la velocidad del "
           "flujo a la entrada y particularmente a la salida de la "
           "alcantarilla es alta», sin decir cuanto es «alta». Este proyecto "
           "lee «alta» como mayor que la maxima admisible del terreno de la "
           "Tabla Nº 11, y usa ese contraste para INFORMAR: si la velocidad "
           "la supera, el terreno necesita la proteccion; si no la supera, "
           "el terreno la resistiria segun la tabla, y aun asi la proteccion "
           "se calcula y se mantiene."),
    en_contra=("el num. 4.1.1.3.7 c) no remite a la Tabla Nº 11 ni da un "
               "umbral: «alta» queda sin definir en la fuente",
               "la Tabla Nº 11 es de velocidades medias de canales sin "
               "revestir, y el chorro de una alcantarilla socava localmente "
               "aunque su velocidad media quede bajo ella (HEC-14 Cap. 5)"),
    a_favor=("el num. 4.1.1.3.6 presenta la Tabla Nº 11 justo despues de "
             "exigir que la velocidad de salida se limite «a fin de evitar "
             "procesos de socavación del cauce aguas abajo»",),
)

INTERPRETACION_TW_CON_D_AJUSTADO = Interpretacion(
    texto=("Cuando el flujo en el conducto es supercritico y la Ec. (10.5) "
           "ajusta el diametro a D' = (D + yn)/2, este proyecto aplica los "
           "limites del tirante de aguas abajo de la Ec. (10.4) --entre 0.4 "
           "y 1.0 diametros-- al diametro AJUSTADO D', el mismo que entra en "
           "la ecuacion, y no a la altura real D del conducto."),
    en_contra=("la fuente escribe los limites con D («between 0.4D and "
               "1.0D») ANTES de presentar el ajuste, y no dice que D' entre "
               "tambien en ellos",
               "con D' un tirante de aguas abajo entre D' y D queda fuera "
               "del rango y el apron sale «no evaluable», cuando con D "
               "estaria dentro"),
    a_favor=("la Ec. (10.5) dice que «the culvert diameter is adjusted»: D' "
             "ocupa el lugar de D en la Ec. (10.4), cuyo ultimo factor es "
             "D/TW",
             "por abajo es la lectura del lado alto: el piso 0.4·D' es menor "
             "que 0.4·D, el tirante se acota menos y el D50, que va con "
             "1/TW, sale mayor"),
)

INTERPRETACION_NOTA_5_T511_06 = Interpretacion(
    texto=("La Tabla 511-06 lleva la llamada «(5)» en dos sitios --el rotulo "
           "de la fila «Tamaño de Abertura Aparente (3) (4) (5)» y la celda "
           "«0,22(5)» de la columna «>50»-- y dos notas, (5) a y (5) b. Este "
           "proyecto lee que el rotulo llama a la nota (5) a (el diseño "
           "especifico en suelos problematicos, que vale para la fila "
           "entera) y la celda a la nota (5) b: la abertura de 0.30 mm para "
           "suelos cohesivos con indice de plasticidad mayor que 7 se aplica "
           "SOLO en la columna «>50». En las columnas «<15» y «15-50» rige "
           "la celda."),
    en_contra=("el rotulo de la fila lleva un «(5)» sin letra, que tambien "
               "puede leerse como que las dos notas valen en las tres "
               "columnas: con esa lectura la columna «<15» pasaria de 0.43 a "
               "0.30 mm (mas cerrada) y la «15-50» de 0.25 a 0.30 mm (mas "
               "abierta)",
               "la tabla es la de AASHTO M 288, que no esta en el "
               "repositorio de normas: con ella a la vista se decide"),
    a_favor=("la Tabla 511-02 de la misma Seccion 511 (subdrenaje, pag. "
             "impresa 1011) trae la misma fila y las mismas dos notas con "
             "numeros distintos: el rotulo lleva «(3) (4)», donde la (4) es "
             "el diseño especifico, y solo la celda «0,22 (5)» lleva la nota "
             "de los suelos cohesivos",
             "es la lectura que no relaja la columna «15-50», donde la otra "
             "abriria la abertura de 0.25 a 0.30 mm para una arena "
             "arcillosa"),
)

# ---- Manual de Hidrologia: la velocidad de salida y la Tabla N° 11 ---------
MC_HHD_V_SALIDA_LIMITE = _cita(
    id="MC_HHD.4.1.1.3.6#V_SALIDA",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, párrafo anterior a la Tabla Nº 11",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="77",
    pagina_pdf=80,
    pagina_pdf_titulo=77,
    texto_literal=Verbatim(
        texto=("Asimismo, se debe tener muy en cuenta la velocidad de flujo a "
               "la salida de la alcantarilla, generalmente esta velocidad es "
               "mayor que la velocidad de escurrimiento en el cauce natural y "
               "debe limitarse a fin de evitar procesos de socavación del "
               "cauce aguas abajo de la estructura y no afecte su "
               "estabilidad."),
        pagina_pdf=80),
    caracter=Caracter.EXIGENCIA,
    sesion=TESIS_T8,
    nota=("Es la frase que convierte la Tabla Nº 11 en un limite de la "
          "velocidad de SALIDA: «debe limitarse». El parrafo siguiente "
          "presenta la tabla «con valores máximos admisibles de velocidades "
          "de flujo según el tipo de material donde se desplaza». El Manual "
          "no dice que hacer cuando la velocidad los supera; lo dice el num. "
          "4.1.1.3.7 c): proteger el cauce."),
)

MC_HHD_T11 = _cita(
    id="MC_HHD.4.1.1.3.6#T11",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.6, Tabla Nº 11",
    titulo_numeral="Diseño hidráulico",
    pagina_impresa="77",
    pagina_pdf=80,
    pagina_pdf_titulo=77,
    texto_literal=Verbatim(
        texto=("TABLA  Nº  11:   Velocidades  máximas  admisibles (m/s) en "
               "canales no"),
        pagina_pdf=80),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=TESIS_T8,
    derivado_de="MC_HHD.4.1.1.3.6#V_SALIDA",
    nota=("El titulo se imprime en DOS renglones y el segundo dice solo "
          "«revestidos»: mismo caso que la Tabla Nº 10. Trece filas de "
          "terreno y DOS columnas de valores, «FLUJO INTERMITENTE (M/S)» y "
          "«FLUJO PERMANENTE (M/S)»; seis de las filas cuelgan del "
          "encabezado «Material graduado (no coloidal)», que no lleva "
          "valores. Al pie: «Fuente: Manual de Carreteras de California». "
          "Leida por texto y por imagen; la transcripcion entera es "
          "`TablaNormativa` MC_HHD.T11."),
)

MC_HHD_PROTECCION_CAUCE = _cita(
    id="MC_HHD.4.1.1.3.7c#PROTECCION",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 c)",
    titulo_numeral="c)  Socavación local a la salida de la alcantarilla",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="79",
    pagina_pdf=82,
    pagina_pdf_titulo=82,
    texto_literal=Verbatim(
        texto=("Si la velocidad del flujo a la entrada y particularmente a la "
               "salida de la alcantarilla es alta, puede producir procesos de "
               "socavación local que afecte su estabilidad, por ello, se "
               "recomienda la protección del cauce"),
        pagina_pdf=82),
    caracter=Caracter.RECOMENDACION,
    interpretacion=INTERPRETACION_VELOCIDAD_ALTA,
    sesion=TESIS_T8,
    nota=("LA ORACION CRUZA DE PAGINA: sigue en la impresa 80 (PDF 83) con "
          "«natural mediante la construcción de emboquillados de piedra…» "
          "(cita MC_HHD.4.1.1.3.7c#REVESTIMIENTOS). Nombra la ENTRADA junto a "
          "la salida: es el unico texto del Manual que sostiene una "
          "proteccion de entrada, y la sostiene como RECOMENDACION, sin "
          "formula ni dimension."),
)

MC_HHD_REVESTIMIENTOS = _cita(
    id="MC_HHD.4.1.1.3.7c#REVESTIMIENTOS",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 c)",
    titulo_numeral="c)  Socavación local a la salida de la alcantarilla",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="80",
    pagina_pdf=83,
    pagina_pdf_titulo=82,
    texto_literal=Verbatim(
        texto=("natural mediante la construcción de emboquillados de piedra, "
               "enchapado de rocas acomodadas u otros tipos de "
               "revestimientos, los cuales deberán extenderse hasta zonas "
               "donde la socavación local no tenga incidencia sobre la "
               "protección"),
        pagina_pdf=83),
    caracter=Caracter.RECOMENDACION,
    derivado_de="MC_HHD.4.1.1.3.7c#PROTECCION",
    sesion=TESIS_T8,
    nota=("Segunda mitad de la oracion. Enumera TRES clases de "
          "revestimiento --emboquillados de piedra, enchapado de rocas "
          "acomodadas, «otros tipos»-- sin preferir ninguna ni dar "
          "dimensiones: de ahi el conjunto cerrado del criterio "
          "'tipo_proteccion_entrada'. Y fija el alcance en planta por un "
          "criterio fisico, no por una longitud: hasta donde la socavacion "
          "local no incida."),
)

MC_HHD_LAMINA_05 = _cita(
    id="MC_HHD.LAMINA_05",
    fuente_id="MC_HHD",
    numeral="Anexos, Lámina Nº 05",
    titulo_numeral="ALCANTARILLA  CON  ENROCADO",
    pagina_impresa="211",
    pagina_pdf=214,
    texto_literal=Verbatim(texto="FILTRO", pagina_pdf=214),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("ES UNA FIGURA, leida por imagen: «SECCIÓN TÍPICA DE CRUCE DE "
          "ALCANTARILLA CON ENROCADO DE PROTECCION A LA SALIDA». Dibuja el "
          "enrocado sobre el talud de salida hasta el fondo del cauce, y "
          "bajo el dos capas ROTULADAS: «FILTRO» y «CAMA DE APOYO». NO TRAE "
          "NINGUNA DIMENSION: los taludes van como «H:V» y las dos cotas "
          "del pie como «VARIABLE». El num. 4.1.1.3.7 c) la presenta con «En "
          "los Anexos: Lámina Nº 05, se aprecia una sección típica de "
          "alcantarilla con enrocado de protección a la salida» (pag. "
          "impresa 80). Lo unico que se le puede atribuir es que el "
          "enrocado tipico del Manual LLEVA filtro y cama de apoyo."),
)

MC_HHD_LAMINA_02 = _cita(
    id="MC_HHD.LAMINA_02",
    fuente_id="MC_HHD",
    numeral="Anexos, Lámina Nº 02",
    titulo_numeral="TIPO  TMC CON PROTECCIÓN DE",
    pagina_impresa="207",
    pagina_pdf=210,
    texto_literal=Verbatim(texto="REVESTIMIENTO  DE PIEDRA  EMBOQUILLADA",
                           pagina_pdf=210),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("ES UNA FIGURA, leida por imagen: «SECCIÓN TÍPICA DE ALCANTARILLA "
          "TIPO TMC CON PROTECCIÓN DE ENTRADA Y SALIDA». Rotula el "
          "«REVESTIMIENTO DE PIEDRA EMBOQUILLADA» del cauce, la «UÑA» al pie "
          "y la «PROTECCION DE DESCARGA» sobre «AFIRMADO COMPACTADO». Las "
          "dimensiones van como LETRAS (g, i, j, m, n, p, q) y la lamina no "
          "trae la tabla que les de valor: no fija ninguna medida. La "
          "Lámina 02-A (pag. impresa 208, PDF 211) añade la «ENTRADA TIPO "
          "CAJA RECEPTORA» y las salidas con y sin aleros, tambien con "
          "letras; la Lámina 03 (pag. impresa 209, PDF 212) rotula "
          "«CON PROTECCIÓN A LA ENTRADA Y SALIDA», con todas las cotas "
          "«VARIABLE»."),
)

# ---- EG-2013: el geotextil entre el enrocado y el suelo --------------------
EG2013_511_08 = _cita(
    id="EG2013.511.08#EROSION",
    fuente_id="EG2013",
    numeral="511.08",
    titulo_numeral="511.08 Geotextiles usados en control permanente de erosión",
    pagina_impresa="1014",
    pagina_pdf=1022,
    texto_literal=Verbatim(
        texto=("Esta especificación es aplicable al uso del geotextil entre "
               "sistemas armados de absorción de energía (escolleras, "
               "gaviones, enrocados, geoestructuras etc.) y el suelo in-situ "
               "para prevenir las pérdidas de suelo resultantes de un "
               "escurrimiento excesivo y para prevenir subpresiones "
               "hidráulicas que causen una inestabilidad del sistema de "
               "control permanente de erosión."),
        pagina_pdf=1022),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Define el AMBITO: el geotextil que va entre un enrocado y el "
          "suelo. El parrafo siguiente dice «La función principal del "
          "geotextil es la filtración». EL NUMERAL NO OBLIGA A PONER FILTRO: "
          "especifica el geotextil cuando el proyecto lo pone. EG-2013 no "
          "trae la palabra «emboquillado» en ninguna de sus 1282 paginas "
          "(barrido por texto en T-8), y su Seccion 603 «Defensas ribereñas» "
          "trata el enrocado de ribera, no el de salida de alcantarilla."),
)

EG2013_T511_06 = _cita(
    id="EG2013.511.08#T511_06",
    fuente_id="EG2013",
    numeral="511.08, Tabla 511-06",
    titulo_numeral="511.08 Geotextiles usados en control permanente de erosión",
    pagina_impresa="1015",
    pagina_pdf=1023,
    pagina_pdf_titulo=1022,
    texto_literal=Verbatim(
        texto=("El Geotextil debe cumplir con los requerimientos de la Tabla "
               "511-06 y lo indicado en el Proyecto."),
        pagina_pdf=1023),
    caracter=Caracter.EXIGENCIA,
    derivado_de="EG2013.511.08#EROSION",
    interpretacion=INTERPRETACION_NOTA_5_T511_06,
    sesion=TESIS_T8,
    nota=("La Tabla 511-06 «Geotextiles para control permanente de "
          "erosión-requerimientos» entra por el «Porcentaje de Suelo in Situ "
          "que pasa Tamiz N.º 200 (0,075 mm)» en tres columnas (< 15, 15-50, "
          "> 50) y fija la permitividad minima (0,7 / 0,2 / 0,1 s-1) y el "
          "tamaño de abertura aparente maximo (0,43 / 0,25 / 0,22 mm); la "
          "clase es la 1 de la Tabla 511-01 (la 2 para los tejidos de "
          "monofilamento) y la estabilidad ultravioleta, 50 % tras 500 "
          "horas. Su nota (5) a pide un diseño especifico en suelos "
          "problematicos y su nota (5) b da 0,30 mm para cohesivos con "
          "indice de plasticidad mayor de 7. LA LLAMADA (5) APARECE DOS "
          "VECES, en el rotulo de la fila «Tamaño de Abertura Aparente (3) "
          "(4) (5)» y en la celda «0,22(5)» de la columna «>50», y la tabla "
          "no dice que nota llama cada una: la lectura del proyecto va en "
          "`interpretacion`. El dato que la tabla pide --el pasante del "
          "tamiz N.º 200-- es del EMS."),
)

# ---- HDS-5: socavacion en la entrada y en la salida ------------------------
HDS5_5_3_1_ENTRADA = _cita(
    id="HDS5_3ED.5.3.1#ENTRADA",
    fuente_id="HDS5_3ED",
    numeral="5.3.1",
    titulo_numeral="5.3.1  Scour at Inlets",
    pagina_impresa="5.9",
    pagina_pdf=145,
    texto_literal=Verbatim(
        texto=("Upstream slope paving, channel paving, headwalls, wingwalls, "
               "and cutoff walls help to protect the slopes and channel bed "
               "at the upstream end of the culvert."),
        pagina_pdf=145),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("El parrafo anterior describe el mecanismo: al contraerse el flujo "
          "hacia el barril, vortices y zonas de alta velocidad atacan los "
          "taludes del terraplen junto a la boca, y a menudo se forma una "
          "hoya aguas arriba del piso del conducto. La fuente ENUMERA las "
          "medidas y no las dimensiona ni dice cual corresponde a que "
          "embocadura: la asignacion por tipo de embocadura es lectura del "
          "proyecto."),
)

HDS5_5_3_2_APRON = _cita(
    id="HDS5_3ED.5.3.2#APRON",
    fuente_id="HDS5_3ED",
    numeral="5.3.2",
    titulo_numeral="5.3.2  Scour at Outlets",
    pagina_impresa="5.11",
    pagina_pdf=147,
    pagina_pdf_titulo=145,
    texto_literal=Verbatim(
        texto=("Since outlet protection is expensive, many state DOTs use "
               "riprap aprons (HEC-14, Section 10.2) to provide a minimum "
               "amount of protection for small culverts."),
        pagina_pdf=147),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Describe una practica y remite a HEC-14 Sec. 10.2. El parrafo "
          "termina: «Providing scour protection for large floods or when "
          "more serious erosion problems exist requires protection measures "
          "designed based on HEC-14». En la pag. impresa 5.9 el mismo "
          "numeral dice que los metodos para estimar la hoya de socavacion "
          "local estan en HEC-14."),
)

HDS5_3_1_3_CRITICO_ENTRADA = _cita(
    id="HDS5_3ED.3.1.3#CRITICO_EN_LA_ENTRADA",
    fuente_id="HDS5_3ED",
    numeral="3.1.3",
    titulo_numeral="3.1.3  Inlet Control",
    pagina_impresa="3.2",
    pagina_pdf=84,
    texto_literal=Verbatim(
        texto=("The flow passes through critical depth just downstream of "
               "the culvert entrance and the flow in the barrel is "
               "supercritical."),
        pagina_pdf=84),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Lo dice de las Figuras 3.1A y 3.1C, el Tipo 1 del USGS, con la "
          "entrada NO sumergida. Sostiene la velocidad que el proyecto lee "
          "en la boca cuando gobierna el control de entrada: la critica. "
          "Con la entrada sumergida (Figuras 3.1B y 3.1D) la boca trabaja "
          "como orificio y la fuente no da la velocidad en ella."),
)

# ---- HEC-14, Capitulo 10: apron de enrocado y tirante equivalente ----------
HEC14_10_1_1_YE = _cita(
    id="HEC14.10.1.1#YE",
    fuente_id="HEC14",
    numeral="10.1.1",
    titulo_numeral="10.1.1 Design Development",
    pagina_impresa="10-2",
    pagina_pdf=203,
    texto_literal=Verbatim(
        texto=("Equivalent brink depth, ye, is defined to permit use of the "
               "same design relationships for rectangular and circular "
               "culverts."),
        pagina_pdf=203),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Sigue: «For rectangular culverts, ye = yo (culvert brink depth). "
          "For circular culverts, ye = (A/2)^1/2, where A is the brink "
          "area». El paso 1 del procedimiento (num. 10.1.5, pag. impresa "
          "10-5) forma con el el numero de Froude de la salida, Fr = Vo / "
          "(g·ye)^1/2. Es el Froude que HEC-14 usa para sus disipadores; el "
          "apron de la Ec. (10.4) no lo lleva."),
)

HEC14_10_2_EC_10_4 = _cita(
    id="HEC14.10.2#EC_10_4",
    fuente_id="HEC14",
    numeral="10.2, Ec. (10.4)",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-17",
    pagina_pdf=218,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("The following equation (Fletcher and Grace, 1972) is "
               "recommended for circular culverts:"),
        pagina_pdf=218),
    caracter=Caracter.RECOMENDACION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("La Ec. (10.4), leida de la pagina renderizada: D50 = 0.2·D·"
          "[Q / (g^0.5·D^2.5)]^(4/3)·(D / TW), con D50, D y TW en m (ft), Q "
          "en m3/s (ft3/s) y g = 9.81 m/s2 (32.2 ft/s2). ES ADIMENSIONAL "
          "--el grupo Q/(g^0.5·D^2.5) no tiene unidades--, de modo que el "
          "0.2 vale igual en SI y en unidades inglesas y no hay coeficiente "
          "que convertir. El Apendice D (Ec. D.5, pag. impresa D-2) da la "
          "misma relacion SIN la gravedad, D50 = 0.020·D·[Q/(α·D^2.5)]^(4/3)·"
          "(D/TW) con α = 0.55 (SI) y 1.0 (CU): esa forma SI depende de "
          "unidades y no es la que se usa. «RECOMMENDED FOR CIRCULAR "
          "CULVERTS»: no cubre el marco. La ecuacion supone una piedra de "
          "gravedad especifica 2.65."),
)

HEC14_10_2_TW = _cita(
    id="HEC14.10.2#TW",
    fuente_id="HEC14",
    numeral="10.2",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-17",
    pagina_pdf=218,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("Tailwater depth for Equation 10.4 should be limited to "
               "between 0.4D and 1.0D.  If tailwater is unknown, use 0.4D."),
        pagina_pdf=218),
    caracter=Caracter.APROXIMACION,
    derivado_de="HEC14.10.2#EC_10_4",
    interpretacion=INTERPRETACION_TW_CON_D_AJUSTADO,
    sesion=TESIS_T8,
    nota=("EL LIMITE DE VALIDEZ DE LA Ec. (10.4), con sus dos lados. Por "
          "abajo, el ejemplo resuelto de la pag. impresa 10-18 enseña que "
          "hacer: con TW/D = 0.33 «This is less than 0.4D, therefore, use TW "
          "= 0.4D». Por arriba, la pag. 10-18 remite a OTRO procedimiento "
          "(cita HEC14.10.2#TW_ALTO)."),
)

HEC14_10_2_TW_ALTO = _cita(
    id="HEC14.10.2#TW_ALTO",
    fuente_id="HEC14",
    numeral="10.2",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-18",
    pagina_pdf=219,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("For tailwater conditions above the acceptable range for "
               "Equation 10.4 (TW > 1.0D), Figure 10.3 should be used to "
               "determine the velocity downstream of the culvert."),
        pagina_pdf=219),
    caracter=Caracter.APROXIMACION,
    derivado_de="HEC14.10.2#TW",
    sesion=TESIS_T8,
    nota=("Con el TW sobre la clave la Ec. (10.4) queda FUERA de su rango "
          "aceptable y la fuente manda a la Figura 10.3 (atenuacion de la "
          "velocidad aguas abajo) y a la Sec. 10.3 para dimensionar la "
          "piedra. La Figura 10.3 es una familia de curvas que este "
          "programa no tiene digitalizada: ese caso sale como metodo no "
          "evaluable, no con la ecuacion extrapolada."),
)

HEC14_10_2_EC_10_5 = _cita(
    id="HEC14.10.2#EC_10_5",
    fuente_id="HEC14",
    numeral="10.2, Ec. (10.5)",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-17",
    pagina_pdf=218,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("Whenever the flow is supercritical in the culvert, the "
               "culvert diameter is adjusted as follows:"),
        pagina_pdf=218),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    derivado_de="HEC14.10.2#EC_10_4",
    sesion=TESIS_T8,
    nota=("La Ec. (10.5), leida de la pagina renderizada: D' = (D + yn)/2, "
          "con D' «adjusted culvert rise» e yn «normal (supercritical) depth "
          "in the culvert». D' entra en la Ec. (10.4) en lugar de D."),
)

HEC14_T10_1 = _cita(
    id="HEC14.10.2#T10_1",
    fuente_id="HEC14",
    numeral="10.2, Table 10.1",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-18",
    pagina_pdf=219,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto="Table 10.1. Example Riprap Classes and Apron Dimensions",
        pagina_pdf=219),
    caracter=Caracter.RECOMENDACION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("ES UN EJEMPLO, y la fuente lo dice dos veces: en el titulo "
          "(«Example») y en la pag. 10-17 («A project or design standard can "
          "be developed such as the example from the Federal Highway "
          "Administration Federal Lands Highway Division»). Seis clases: D50 "
          "de 125, 150, 250, 350, 500 y 550 mm; longitud del apron 4D, 4D, "
          "5D, 6D, 7D y 8D, con la nota «D is the culvert rise»; "
          "profundidad 3.5, 3.3, 2.4, 2.2, 2.0 y 2.0 veces D50. Debajo: "
          "«Table 10.1 provides guidance on the apron length and depth». La "
          "clase es la de D50 mayor o igual que el requerido (pag. 10-17)."),
)

HEC14_10_2_ANCHO = _cita(
    id="HEC14.10.2#ANCHO",
    fuente_id="HEC14",
    numeral="10.2",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-18",
    pagina_pdf=219,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("The final dimension, width, may be determined using the 1:3 "
               "flare shown in Figure 10.4 and should conform to the "
               "dimensions of the downstream channel."),
        pagina_pdf=219),
    caracter=Caracter.PERMISO,
    sesion=TESIS_T8,
    nota=("El ejemplo resuelto de la pag. impresa 10-19 (PDF 220) lo "
          "escribe: «Width (at apron end) = 3D + (2/3)L». El 3D es el ancho "
          "del apron en la boca de la Figura 10.4 y el (2/3)L el abocinado "
          "de 1:3 por cada lado."),
)

HEC14_10_2_FILTRO = _cita(
    id="HEC14.10.2#FILTRO",
    fuente_id="HEC14",
    numeral="10.2",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-18",
    pagina_pdf=219,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("A filter blanket should also be provided as described in HEC "
               "11 (Brown and Clyde, 1989)."),
        pagina_pdf=219),
    caracter=Caracter.RECOMENDACION,
    sesion=TESIS_T8,
    nota=("HEC 11 no esta en el repositorio de normas: el diseño del filtro "
          "no se transcribe. Lo que se cita es que el apron LLEVA filtro."),
)

HEC14_T1_1_APRON = _cita(
    id="HEC14.1#T1_1_APRON",
    fuente_id="HEC14",
    numeral="1, Table 1.1, nota 8",
    titulo_numeral="CHAPTER 1: ENERGY DISSIPATOR DESIGN",
    pagina_impresa="1-2",
    pagina_pdf=15,
    pagina_pdf_titulo=14,
    texto_literal=Verbatim(
        texto="Culvert rise less than or equal to 1500 mm (60 in)",
        pagina_pdf=15),
    caracter=Caracter.APROXIMACION,
    sesion=TESIS_T8,
    nota=("Es la nota 8 de la Table 1.1 «Energy Dissipators and "
          "Limitations», y cuelga de la fila «Riprap apron» (Chapter 10), "
          "cuya columna de Froude dice «na». La Sec. 10.2 lo dice como "
          "poblacion y no como prohibicion: «The most commonly used device "
          "for outlet protection, primarily for culverts 1500 mm (60 in) or "
          "smaller, is a riprap apron» (pag. impresa 10-16). La tabla se "
          "titula «Limitations» y la nota es una de ellas: un conducto mas "
          "alto sale como metodo no evaluable. LA FUENTE DA DOS CIFRAS QUE "
          "NO COINCIDEN: 60 in son 1.524 m, no 1.500. Rige 1.524 m "
          "(`constantes_normativas.HEC14_APRON_ALTURA_MAX_M`), lectura "
          "declarada: es la que deja evaluar el ejemplo resuelto de la "
          "propia fuente, que usa D = 5.0 ft = 60 in (pag. impresa 10-19). "
          "La misma tabla limita la POZA de enrocado (riprap basin) a Fr < "
          "3."),
)

# ---- HEC-14, Capitulo 5: la hoya de socavacion a la salida -----------------
HEC14_5_ALCANCE = _cita(
    id="HEC14.5#PEOR_CASO",
    fuente_id="HEC14",
    numeral="5",
    titulo_numeral="CHAPTER 5: ESTIMATING SCOUR AT CULVERT OUTLETS",
    pagina_impresa="5-1",
    pagina_pdf=54,
    texto_literal=Verbatim(
        texto=("The equations are based on tests that were conducted to "
               "determine maximum scour for the given condition and "
               "therefore represent what might be termed worst-case scour "
               "geometries."),
        pagina_pdf=54),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Dos limites en el mismo parrafo: las ecuaciones dan la hoya "
          "MAXIMA de los ensayos («worst-case») y «do not include long-term "
          "channel degradation of the downstream channel». El capitulo abre "
          "diciendo de que depende el metodo: caudal, forma del conducto, "
          "tipo de suelo, duracion del flujo, pendiente, altura del "
          "conducto sobre el lecho y tirante de aguas abajo; el tirante de "
          "aguas abajo NO entra en la Ec. (5.1)."),
)

HEC14_5_1_EC_5_1 = _cita(
    id="HEC14.5.1#EC_5_1",
    fuente_id="HEC14",
    numeral="5.1, Ec. (5.1)",
    titulo_numeral="COHESIONLESS SOILS",
    pagina_impresa="5-1",
    pagina_pdf=54,
    texto_literal=Verbatim(
        texto=("The general expression for determining scour geometry in a "
               "cohesionless soil at the culvert outlet is:"),
        pagina_pdf=54),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("La Ec. (5.1), leida de la pagina renderizada: [hs/Rc, Ws/Rc, "
          "Ls/Rc, Vs/Rc^3] = Cs·Ch·(α / σ^(1/3))·[Q / (g^0.5·Rc^2.5)]^β·"
          "(t/316)^θ, con Rc «hydraulic radius at the end of the culvert "
          "(assuming full flow)», t «time in minutes» y σ = (D84/D16)^0.5. "
          "ES ADIMENSIONAL salvo por el tiempo: el 316 esta en minutos y "
          "vale igual en SI y en unidades inglesas. ERRATA DE LA FUENTE: la "
          "lista de variables de esta pagina remite «Cs … see Table 5.2» y "
          "«Ch … see Table 5.3», y las tablas estan al reves --la 5.2 es de "
          "Ch (altura sobre el lecho) y la 5.3 de Cs (pendiente)--, como "
          "dicen sus titulos y el texto de los num. 5.1.4 y 5.1.5."),
)

HEC14_T5_1 = _cita(
    id="HEC14.5.1.1#T5_1",
    fuente_id="HEC14",
    numeral="5.1.1, Table 5.1",
    titulo_numeral="5.1.1 Scour Hole Geometry",
    pagina_impresa="5-2",
    pagina_pdf=55,
    texto_literal=Verbatim(
        texto=("Table 5.1. Coefficients for Culvert Outlet Scour in "
               "Cohesionless Soils"),
        pagina_pdf=55),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("α, β, θ: profundidad 2.27, 0.39, 0.06; ancho 6.94, 0.53, 0.08; "
          "longitud 17.10, 0.47, 0.10; volumen 127.08, 1.24, 0.18. El "
          "numeral dice ademas que la profundidad maxima se da a unos 0.4·Ls "
          "aguas abajo de la salida (Fletcher y Grace, 1972) y que la hoya "
          "maxima ocurre con tirantes de aguas abajo menores que la mitad "
          "de la altura del conducto (Bohan, 1970)."),
)

HEC14_5_1_2_T30 = _cita(
    id="HEC14.5.1.2#T30",
    fuente_id="HEC14",
    numeral="5.1.2",
    titulo_numeral="5.1.2 Time of Scour",
    pagina_impresa="5-2",
    pagina_pdf=55,
    texto_literal=Verbatim(
        texto=("Lacking this knowledge, it is recommended that a time of 30 "
               "minutes be used in Equation 5.1."),
        pagina_pdf=55),
    caracter=Caracter.RECOMENDACION,
    sesion=TESIS_T8,
    nota=("«This knowledge» es la duracion del caudal pico. Para suelos "
          "cohesivos la pag. impresa 5-7 repite la regla: «Use 30 minutes "
          "for t in Equation 5.2 and Equation 5.3 if it is not known»."),
)

HEC14_5_1_2_PISO = _cita(
    id="HEC14.5.1.2#NO_BAJO_30",
    fuente_id="HEC14",
    numeral="5.1.2",
    titulo_numeral="5.1.2 Time of Scour",
    pagina_impresa="5-2",
    pagina_pdf=55,
    texto_literal=Verbatim(
        texto=("The exponents for the time parameter in Table 5.1 reflect "
               "the relatively flat part of the scour-time relationship (t > "
               "30 minutes) and are not applicable for the first 30 minutes "
               "of the scour process."),
        pagina_pdf=55),
    caracter=Caracter.APROXIMACION,
    derivado_de="HEC14.5.1.2#T30",
    sesion=TESIS_T8,
    nota=("LIMITE DE VALIDEZ: con t < 30 min los exponentes no aplican. El "
          "mismo numeral dice que entre 2/3 y 3/4 de la profundidad maxima "
          "se alcanza en los primeros 30 minutos."),
)

HEC14_5_1_3_CABEZAL = _cita(
    id="HEC14.5.1.3#CABEZAL",
    fuente_id="HEC14",
    numeral="5.1.3",
    titulo_numeral="5.1.3 Headwalls",
    pagina_impresa="5-2",
    pagina_pdf=55,
    texto_literal=Verbatim(
        texto=("If the culvert is installed with a headwall, the headwall "
               "should extend to a depth equal to the maximum depth of "
               "scour."),
        pagina_pdf=55),
    caracter=Caracter.RECOMENDACION,
    sesion=TESIS_T8,
    nota=("Es la frase que liga la hoya de socavacion con el DESPLANTE del "
          "cabezal de salida. Antes dice que el cabezal perpendicular "
          "desplaza la hoya aguas abajo sin cambiar esencialmente su "
          "magnitud (Ruff et al., 1982)."),
)

HEC14_T5_2 = _cita(
    id="HEC14.5.1.4#T5_2",
    fuente_id="HEC14",
    numeral="5.1.4, Table 5.2",
    titulo_numeral="5.1.4 Drop Height",
    pagina_impresa="5-3",
    pagina_pdf=56,
    pagina_pdf_titulo=55,
    texto_literal=Verbatim(
        texto="Table 5.2. Coefficient Ch for Outlets above the Bed",
        pagina_pdf=56),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Hd = altura del fondo de la salida sobre el lecho, en DIAMETROS "
          "(«Hd is the height above bed in pipe diameters»): filas 0, 1, 2 "
          "y 4. Ch de profundidad 1.00, 1.22, 1.26, 1.34; de ancho 1.00, "
          "1.51, 1.54, 1.66; de longitud 1.00, 0.73, 0.73, 0.73; de volumen "
          "1.00, 1.28, 1.47, 1.55. La tabla no dice como leer entre filas "
          "ni mas alla de Hd = 4."),
)

HEC14_T5_3 = _cita(
    id="HEC14.5.1.5#T5_3",
    fuente_id="HEC14",
    numeral="5.1.5, Table 5.3",
    titulo_numeral="5.1.5 Slope",
    pagina_impresa="5-3",
    pagina_pdf=56,
    texto_literal=Verbatim(
        texto="Table 5.3. Coefficient Cs for Culvert Slope",
        pagina_pdf=56),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Pendiente en %: filas 0, 2, 5 y «>7». Cs de profundidad 1.00, "
          "1.03, 1.08, 1.12; de ancho 1.00, 1.28, 1.28, 1.28; de longitud "
          "1.00, 1.17, 1.17, 1.17; de volumen 1.00, 1.30, 1.30, 1.30. La "
          "tabla no dice como leer entre filas, ni entre el 5 % y el 7 %."),
)

HEC14_5_2_COHESIVO = _cita(
    id="HEC14.5.2#EC_5_2",
    fuente_id="HEC14",
    numeral="5.2, Ec. (5.2) y (5.3)",
    titulo_numeral="COHESIVE SOILS",
    pagina_impresa="5-6",
    pagina_pdf=59,
    texto_literal=Verbatim(
        texto=("If the soil is cohesive in nature, Equation 5.2 should be "
               "used to determine the scour hole dimensions."),
        pagina_pdf=59),
    caracter=Caracter.APROXIMACION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("Ec. (5.2), conducto circular: [hs/D, Ws/D, Ls/D, Vs/D^3] = Cs·Ch·"
          "α·(ρV²/τc)^β·(t/316)^θ. Ec. (5.3), otras formas: lo mismo con ye "
          "= (A/2)^1/2 en lugar de D y αe en lugar de α. V es la velocidad "
          "media de salida, ρ = 1000 kg/m3 (1.94 slugs/ft3) y τc la tension "
          "tractiva critica de la Ec. (5.4). El numero ρV²/τc es "
          "adimensional; lo que depende de unidades es αu de la Ec. (5.4)."),
)

HEC14_5_2_RANGO = _cita(
    id="HEC14.5.2#RANGO_IP",
    fuente_id="HEC14",
    numeral="5.2",
    titulo_numeral="COHESIVE SOILS",
    pagina_impresa="5-7",
    pagina_pdf=60,
    pagina_pdf_titulo=59,
    texto_literal=Verbatim(
        texto=("Equations 5.2 and 5.3 should be limited to sandy clay soils "
               "with a plasticity index of 5 to 16."),
        pagina_pdf=60),
    caracter=Caracter.APROXIMACION,
    derivado_de="HEC14.5.2#EC_5_2",
    sesion=TESIS_T8,
    nota=("LIMITE DE VALIDEZ. El suelo ensayado fue UNA arcilla arenosa (58 "
          "% arena, 27 % arcilla, 15 % limo, indice de plasticidad 15; pag. "
          "impresa 5-6)."),
)

HEC14_5_2_EC_5_4 = _cita(
    id="HEC14.5.2#EC_5_4",
    fuente_id="HEC14",
    numeral="5.2, Ec. (5.4)",
    titulo_numeral="COHESIVE SOILS",
    pagina_impresa="5-7",
    pagina_pdf=60,
    pagina_pdf_titulo=59,
    texto_literal=Verbatim(
        texto=("The critical tractive shear stress is defined in Equation "
               "5.4 (Dunn, 1959; Abt et al., 1996)."),
        pagina_pdf=60),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    derivado_de="HEC14.5.2#EC_5_2",
    sesion=TESIS_T8,
    nota=("Ec. (5.4): τc = 0.001·(Sv + αu)·tan(30 + 1.73·PI), con el "
          "argumento de la tangente en GRADOS (el ejemplo resuelve tan "
          "(50.76) con PI = 12), Sv la resistencia al corte saturada y αu "
          "«unit conversion constant, 8630 N/m2 (SI), 180 lb/ft2 (CU)». τc "
          "sale en N/m2. La Tabla 5.4 (misma pagina) da α, β, θ y αe: "
          "profundidad 0.86, 0.18, 0.10, 1.37; ancho 3.55, 0.17, 0.07, "
          "5.63; longitud 2.82, 0.33, 0.09, 4.48; volumen 0.62, 0.93, 0.23, "
          "2.48."),
)

# ---- HEC-14, Capitulo 3: el area de la velocidad de salida ----------------
# La cadena T cita «cap. 4-5 (velocidad de salida…)»: la velocidad de salida
# es el Capitulo 3 (verificado sobre el ejemplar, PDF 32). M4 ya la resuelve
# por HDS-5 3.1.6 (EXT-3); lo que este capitulo sostiene aqui es que el AREA
# que la acompaña sale de la continuidad, que es como M6 forma el Froude.
HEC14_3_CONTINUIDAD = _cita(
    id="HEC14.3#CONTINUIDAD",
    fuente_id="HEC14",
    numeral="3",
    titulo_numeral=("CHAPTER 3: CULVERT OUTLET VELOCITY AND VELOCITY "
                    "MODIFICATION"),
    pagina_impresa="3-1",
    pagina_pdf=32,
    texto_literal=Verbatim(
        texto=("The continuity equation, which states that discharge is equal "
               "to flow area times average velocity (Q = AV), is used to "
               "compute culvert velocities within the barrel and at the "
               "outlet."),
        pagina_pdf=32),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Sigue: «The flow area, A, for determining outlet velocity is "
          "calculated using the culvert outlet depth that is consistent with "
          "the culvert flow type», y el num. 3.1.2 (pag. impresa 3-2, PDF 33) "
          "da la regla de HDS-5 que M4 aplica: «the higher of the tailwater "
          "or critical depth», o la seccion llena con la salida sumergida "
          "(3.1.1). Es la relacion con que M6 asigna a la velocidad de salida "
          "su area, A = Q/V, para el tirante equivalente del Froude; los "
          "procedimientos de HEC-14 hacen lo mismo («A = Q/Vo», pag. impresa "
          "9-40, PDF 197)."),
)

# ---- HEC-14, Apendice D: las ecuaciones de apron que solo miran V ----------
HEC14_D_SOLO_VELOCIDAD = _cita(
    id="HEC14.D#SOLO_VELOCIDAD",
    fuente_id="HEC14",
    numeral="D",
    titulo_numeral="APPENDIX D: RIPRAP APRON SIZING EQUATIONS",
    pagina_impresa="D-2",
    pagina_pdf=281,
    pagina_pdf_titulo=280,
    texto_literal=Verbatim(
        texto=("Equations D.2 and D.3 are not recommended because they do not "
               "consider tailwater effects."),
        pagina_pdf=281),
    caracter=Caracter.RECOMENDACION,
    sesion=TESIS_T8,
    nota=("Las dos ecuaciones que HEC-14 descarta son las que dimensionan la "
          "piedra SOLO con la velocidad de salida: D.2 (Berry, 1948; Peterka, "
          "1978), D50 = α·V² con α = 0.0413 en SI, y D.3 (Searcy, 1967; la de "
          "la edicion anterior de HEC-14 y de HEC 11), D50 = 0.692/(S − 1)·"
          "V²/(2g). Ninguna de las dos es la de Laushey, que HEC-14 no "
          "nombra. El apendice compara seis relaciones sobre diez casos de HY8 "
          "y retiene la de Fletcher y Grace (Ec. D.5), que es la Ec. (10.4) "
          "del Capitulo 10 escrita sin la gravedad. La lectura de que la ec. "
          "(49) del Manual pertenece a la misma familia que D.2 y D.3 es del "
          "proyecto y va en `M6_proteccion`, no aqui."),
)

# ---- Manual de Hidrologia: el aliviadero escalonado y su Lamina -----------
MC_HHD_ALIVIADERO = _cita(
    id="MC_HHD.4.1.1.3.7c#ALIVIADERO",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.7 c)",
    titulo_numeral="c)  Socavación local a la salida de la alcantarilla",
    jerarquia_numeral=("4.1.1.3.7  Consideraciones para el diseño",),
    pagina_impresa="80",
    pagina_pdf=83,
    pagina_pdf_titulo=82,
    texto_literal=Verbatim(
        texto=("Una medida para reducir la velocidad del flujo, es la "
               "construcción de aliviaderos de entrada y salida de la "
               "alcantarilla en forma escalonada con el objetivo de disipar "
               "la energía hidráulica."),
        pagina_pdf=83),
    caracter=Caracter.PERMISO,
    sesion=TESIS_T8,
    nota=("La frase siguiente remite a la Lámina Nº 04 (cita "
          "MC_HHD.LAMINA_04). Es la alternativa que el Manual da cuando la "
          "velocidad es alta: no reviste el cauce, reduce la velocidad. El "
          "programa no la dimensiona."),
)

MC_HHD_LAMINA_04 = _cita(
    id="MC_HHD.LAMINA_04",
    fuente_id="MC_HHD",
    numeral="Anexos, Lámina Nº 04",
    titulo_numeral="PERFIL LONGITUDINAL Y SECCIÓN TÍPICAS",
    pagina_impresa="210",
    pagina_pdf=213,
    texto_literal=Verbatim(texto="0.80 min.", pagina_pdf=213),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("ES UNA FIGURA, leida por imagen: «PERFIL LONGITUDINAL Y SECCIÓN "
          "TÍPICAS DE ALIVIADERO CON DISIPADOR DE ENERGÍA HIDRÁULICA, A LA "
          "SALIDA DE ALCANTARILLAS». A diferencia de las Láminas 02, 03 y 05, "
          "ESTA SI LLEVA COTAS: escalones de concreto ciclopeo de 1.00 m de "
          "alto, losa de 0.15 m sobre 0.20 m de relleno granular, muros de "
          "0.20 m en la corona y 0.30 m en la base (Sección B-B), tubos de "
          "drenaje perforados Ø4\", y un dentellon final de «0.80 min.» de "
          "profundidad y 0.40 m de ancho. Las longitudes de los tramos van "
          "como «VARIABLE». Es el detalle tipico de una medida que el "
          "programa no dimensiona."),
)

# ---- Auditoria adversarial de T-8: lo que faltaba citar ---------------------
# LA LECTURA «SIN ENROCADO», QUE EL PROYECTO YA NO ADOPTA. La primera
# auditoria la mando declarar como lectura del proyecto; la segunda midio que
# se decidia con una velocidad subestimada (H2), y el dueño resolvio el
# 2026-11-12 que «sin enrocado» no es NUNCA una conclusion del programa: la
# proteccion se calcula y se mantiene siempre, la Tabla Nº 11 informa, y
# suprimirla queda sujeto a la inspeccion de campo que nombra el HDS-5. El
# nombre del simbolo se conserva porque la suite y los avisos lo anclan.
INTERPRETACION_SIN_ENROCADO = Interpretacion(
    texto=("Que la velocidad de salida no supere la maxima admisible del "
           "terreno del receptor (Tabla Nº 11) NO basta, para este proyecto, "
           "para dejar la salida sin proteccion: el enrocado se calcula y se "
           "mantiene siempre, el contraste con la tabla informa de si el "
           "terreno resistiria, y suprimir la proteccion queda sujeto a la "
           "inspeccion de campo en alcantarillas semejantes de la zona."),
    en_contra=("el Manual presenta la Tabla Nº 11 justo despues de exigir "
               "que la velocidad de salida se limite «a fin de evitar "
               "procesos de socavación del cauce aguas abajo», lo que admite "
               "leer que bajo ella no hay nada que proteger",
               "la cadena T lo pedia asi (T-8 punto 1: calcular el d50 solo "
               "cuando la velocidad de salida supera la admisible)"),
    a_favor=("el HDS-5 (num. 5.3.2, pag. impresa 5.11) describe el apron de "
             "enrocado como practica corriente «unless field investigation "
             "at similar culverts in the vicinity indicates that such "
             "protection is not needed»: la excepcion la da el campo, no "
             "una tabla de velocidades",
             "la Tabla Nº 11 es de velocidades medias de canales sin "
             "revestir, y el chorro de una alcantarilla socava localmente "
             "aunque su velocidad media quede bajo ella (HEC-14 Cap. 5)",
             "bajo control de salida con el tirante de aguas abajo bajo el "
             "critico la velocidad que el programa compara es una cota "
             "inferior de la real (HEC-14 num. 3.1.3)"),
)

HDS5_5_3_2_PRACTICA = _cita(
    id="HDS5_3ED.5.3.2#PRACTICA",
    fuente_id="HDS5_3ED",
    numeral="5.3.2",
    titulo_numeral="5.3.2  Scour at Outlets",
    pagina_impresa="5.11",
    pagina_pdf=147,
    pagina_pdf_titulo=145,
    texto_literal=Verbatim(
        texto=("The riprap apron is intended to withstand damage from small "
               "storm events and is typically a standard practice unless "
               "field investigation at similar culverts in the vicinity "
               "indicates that such protection is not needed."),
        pagina_pdf=147),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    interpretacion=INTERPRETACION_SIN_ENROCADO,
    nota=("La frase que sigue a la de HDS5_3ED.5.3.2#APRON. Describe una "
          "practica: el apron se pone salvo que el campo diga que no hace "
          "falta. Es lo que sostiene que el programa no concluya «sin "
          "enrocado» cuando la velocidad no supera la Tabla Nº 11: la "
          "proteccion se mantiene y el aviso cita esta frase."),
)

HEC14_10_1_DOS_D50 = _cita(
    id="HEC14.10.1#DOS_D50",
    fuente_id="HEC14",
    numeral="10.1",
    titulo_numeral="10.1 RIPRAP BASIN",
    pagina_impresa="10-1",
    pagina_pdf=202,
    texto_literal=Verbatim(
        texto=("The basin is pre-shaped and lined with riprap that is at "
               "least 2D50 thick."),
        pagina_pdf=202),
    caracter=Caracter.RECOMENDACION,
    sesion=TESIS_T8,
    nota=("Es de la POZA de enrocado, no del apron; se cita porque fija el "
          "mismo piso que la Tabla 10.1 alcanza para las piedras grandes "
          "(cita HEC14.10.2#PROFUNDIDAD). La Figura 10.1 de la misma pagina, "
          "leida por imagen, mide hs DESDE la solera de salida del conducto "
          "hasta el fondo de la poza."),
)

HEC14_10_2_PROFUNDIDAD = _cita(
    id="HEC14.10.2#PROFUNDIDAD",
    fuente_id="HEC14",
    numeral="10.2",
    titulo_numeral="10.2 RIPRAP APRON",
    pagina_impresa="10-18",
    pagina_pdf=219,
    pagina_pdf_titulo=217,
    texto_literal=Verbatim(
        texto=("Apron depth ranges from 3.5D50 for the smallest riprap to a "
               "limit of 2.0D50 for the larger riprap sizes."),
        pagina_pdf=219),
    caracter=Caracter.RECOMENDACION,
    derivado_de="HEC14.10.2#T10_1",
    sesion=TESIS_T8,
    nota=("El piso del espesor del apron: 2.0·D50. El criterio "
          "'espesor_proteccion_salida' adopta 1.75·d50 (ventana 1.5-2.0) y "
          "queda siempre bajo ese piso salvo en el techo de su ventana, que "
          "lo iguala: la Fase 6 lo avisa en todo punto que dimensiona."),
)

HEC14_3_1_3_BORDE = _cita(
    id="HEC14.3.1.3#BORDE",
    fuente_id="HEC14",
    numeral="3.1.3",
    titulo_numeral="3.1.3 Unsubmerged Outlets (Brink Depth)",
    pagina_impresa="3-3",
    pagina_pdf=34,
    texto_literal=Verbatim(
        texto=("The flow goes through critical depth upstream of the outlet "
               "when the tailwater elevation is below the critical depth "
               "elevation in the culvert."),
        pagina_pdf=34),
    caracter=Caracter.DEFINICION,
    sesion=TESIS_T8,
    nota=("Con el TW bajo el tirante critico, el tirante en el borde de la "
          "salida (brink depth) es MENOR que el critico: la velocidad real a "
          "la salida es MAYOR que Q/A(yc), que es la que M4 toma por HDS-5 "
          "3.1.6. El mismo numeral lo dice al aproximar el borde con las "
          "curvas criticas: «Since critical depth is larger than brink "
          "depth, determining brink depth in this manner is not "
          "conservative, but is acceptable». Las Figuras 3.3 y 3.4 dan el "
          "borde y no estan digitalizadas."),
)

EG2013_T511_06_NOTA_5A = _cita(
    id="EG2013.511.08#NOTA_5A",
    fuente_id="EG2013",
    numeral="511.08, Tabla 511-06, nota (5) a",
    titulo_numeral="511.08 Geotextiles usados en control permanente de erosión",
    pagina_impresa="1015",
    pagina_pdf=1023,
    pagina_pdf_titulo=1022,
    texto_literal=Verbatim(
        texto=("suelos inestables o altamente erosionables tales como los "
               "limos no cohesivos"),
        pagina_pdf=1023),
    caracter=Caracter.RECOMENDACION,
    derivado_de="EG2013.511.08#T511_06",
    sesion=TESIS_T8,
    nota=("Frase completa: «Debería efectuarse un diseño del geotextil para "
          "un sitio específico especialmente si uno o más de los siguientes "
          "suelos problemáticos son encontrados: suelos inestables o "
          "altamente erosionables tales como los limos no cohesivos; suelos "
          "de gradación abierta; suelos laminados alternando arenas y limos; "
          "arcillas dispersivas y/o polvo de roca.» La llamada (5) la llevan "
          "el rotulo de la FILA «Tamaño de Abertura Aparente (3) (4) (5)» y "
          "la celda «0,22(5)». El proyecto lee que el rotulo llama a ESTA "
          "nota, que vale para la fila entera, y la celda a la (5) b "
          "(`Interpretacion` de la cita EG2013.511.08#T511_06)."),
)

# ---- Segunda auditoria de T-8: tres citas que faltaban ----------------------
HEC14_10_1_HS = _cita(
    id="HEC14.10.1#HS",
    fuente_id="HEC14",
    numeral="10.1",
    titulo_numeral="10.1 RIPRAP BASIN",
    pagina_impresa="10-1",
    pagina_pdf=202,
    texto_literal=Verbatim(
        texto=("The riprap floor is constructed at the approximate depth of "
               "scour, hs, that would occur in a thick pad of riprap."),
        pagina_pdf=202),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("Es de la POZA de enrocado (Sec. 10.1), otro metodo que la hoya "
          "del Cap. 5. Se cita por lo unico que sostiene: en la poza, hs es "
          "la profundidad del piso de enrocado, y la Figura 10.1 de la misma "
          "pagina, leida por imagen, la acota DESDE la prolongacion de la "
          "solera de salida del conducto hasta ese piso. Es la lectura "
          "«solera_de_salida» del criterio "
          "'referencia_profundidad_socavacion'. Hasta la segunda auditoria "
          "de T-8 (H9) eso se apoyaba en HEC14.10.1#DOS_D50, cuyo literal "
          "habla del espesor del revestimiento y no de la referencia de hs."),
)

EG2013_T511_02_NOTA_5 = _cita(
    id="EG2013.511.05#T511_02_NOTA_5",
    fuente_id="EG2013",
    numeral="511.05, Tabla 511-02, nota (5)",
    titulo_numeral="511.05 Geotextiles usados en subdrenaje",
    pagina_impresa="1011",
    pagina_pdf=1019,
    texto_literal=Verbatim(
        texto=("Para los suelos cohesivos con un índice de plasticidad mayor "
               "a 7, el valor máximo promedio por rollo (VMPR)"),
        pagina_pdf=1019),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=TESIS_T8,
    nota=("LA TABLA HERMANA de la 511-06, en la misma Seccion 511: misma "
          "fila «Tamaño de Abertura Aparente», mismas tres columnas por el "
          "pasante del tamiz N.º 200 y las mismas celdas 0,43 / 0,25 / 0,22. "
          "Aqui las dos notas llevan numeros DISTINTOS: el rotulo de la fila "
          "dice «Tamaño de Abertura Aparente (3) (4)», y la (4) es el diseño "
          "para un sitio especifico en suelos problematicos; la nota de los "
          "suelos cohesivos es la (5), que termina «es de 0.30 mm», y la "
          "lleva SOLO la celda «0,22 (5)» de la columna «>50». Leida por "
          "texto y por imagen. No se aplica al enrocado --es la tabla de "
          "subdrenaje--: se cita como el hecho de la propia fuente que "
          "sostiene la lectura de la nota (5) de la Tabla 511-06 "
          "(`Interpretacion` de EG2013.511.08#T511_06)."),
)

HEC14_5_1_2_DOS_TERCIOS = _cita(
    id="HEC14.5.1.2#DOS_TERCIOS",
    fuente_id="HEC14",
    numeral="5.1.2",
    titulo_numeral="5.1.2 Time of Scour",
    pagina_impresa="5-2",
    pagina_pdf=55,
    texto_literal=Verbatim(
        texto=("The tests indicate that approximately 2/3 to 3/4 of the "
               "maximum scour depth occurs in the first 30 minutes of the "
               "flow duration."),
        pagina_pdf=55),
    caracter=Caracter.DEFINICION,
    derivado_de="HEC14.5.1.2#T30",
    sesion=TESIS_T8,
    nota=("La frase que sigue a la recomendacion de los 30 minutos. Es lo "
          "que dice cuanto de la hoya MAXIMA cubre esa duracion: entre dos "
          "tercios y tres cuartos. Sostiene que el criterio "
          "'duracion_caudal_pico_socavacion_min' no adopte los 30 minutos "
          "para el desplante del cabezal cuando no hay hidrograma (decision "
          "del dueño del 2026-11-12)."),
)


# ===========================================================================
# --- T-5 --- (cadena T, 2026-11-12) Fase 8: estructural del conducto.
# INF-3.3.5. Las de AASHTO LRFD, el Manual de Puentes y EG-2013 se leyeron
# por TEXTO, abriendo la pagina declarada (T2, T3 y T6 las comprueban en cada
# corrida); las de ASTM A796 y AASHTO M 170M por IMAGEN (las dos fuentes no
# entregan texto utilizable). Ninguna paso por el subagente verificador: las
# leyo la propia sesion, y la firma lo dice (`POR_T5`).
#
# EL REPARTO ENTRE LAS FUENTES, que es lo primero que un jurado pregunta:
# la CARGA VIVA es el HL-93 del Manual de Puentes [N] (ejes, separaciones,
# area de contacto, presencia multiple, IM de componentes enterrados) y su
# DISTRIBUCION a traves del relleno es AASHTO LRFD 3.6.1.2.6 [C], que el
# Manual no transcribe; el diseño de cada conducto es la Seccion 12 de
# AASHTO LRFD [C], que el Manual no incorpora (v8, Fase 8); y la norma
# peruana de construccion pone dos cosas propias: la clase del tubo de
# concreto la indica el Proyecto conforme a M 170M (506.02) y el espesor
# minimo del TMC por diametro (Tabla 507-01).
# ===========================================================================

AASHTO_3_6_1_2_6A_RELLENO = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6a#RELLENO",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6a",
    titulo_numeral="3.6.1.2.6a—General",
    pagina_impresa="3-26",
    pagina_pdf=80,
    texto_literal=Verbatim(
        texto=("Where the depth of fill over round, nonconcrete culverts is "
               "greater than 1.0 ft, or when the depth of fill over flat top "
               "three-sided, or long-span concrete arch culverts, or concrete "
               "pipe is 2.0 ft or greater the live load shall be distributed "
               "to the structure as wheel loads, uniformly distributed over a "
               "rectangular area with sides equal to the dimension of the "
               "tire contact area specified in Article 3.6.1.2.5 increased by "
               "the live load distribution factors (LLDF) specified in Table "
               "3.6.1.2.6a-1, and the provisions of Articles 3.6.1.2.6b and "
               "3.6.1.2.6c."),
        pagina_pdf=80),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("ES EL METODO DE LA CARGA VIVA SOBRE EL CONDUCTO, y tiene DOS "
          "dominios distintos: mas de 1.0 ft de relleno para la tuberia que no "
          "es de concreto y 2.0 ft o mas para el tubo de concreto. Por debajo "
          "el mismo numeral manda otra cosa (Eq. 4.6.2.10.2-1 para el tubo de "
          "concreto, «more comprehensive methods» con menos de 1.0 ft), que "
          "este programa no implementa: lo dice como metodo no evaluable. "
          "El Manual de Puentes no transcribe este numeral (su 2.4.3.2 trae "
          "el HL-93 y el 2.4.3.3.2 el IM de lo enterrado, no la "
          "distribucion a traves del relleno): por eso es [C]."),
)

AASHTO_3_6_1_2_6A_EJES = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6a#EJES",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6a",
    titulo_numeral="3.6.1.2.6a—General",
    pagina_impresa="3-26",
    pagina_pdf=80,
    texto_literal=Verbatim(
        texto=("Only the axle loads of the design truck or design tandem of "
               "Articles 3.6.1.2.2 and 3.6.1.2.3, respectively shall be "
               "applied as live load on culverts, regardless of traffic "
               "orientation."),
        pagina_pdf=80),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("«respectively shall» SIN coma: asi lo entrega la capa de texto "
          "del ejemplar. Es lo que deja fuera la carga de carril del HL-93: "
          "en una alcantarilla solo cuentan los ejes del camion y del tandem."),
)

AASHTO_3_6_1_2_6A_UN_CARRIL = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6a",
    titulo_numeral="3.6.1.2.6a—General",
    pagina_impresa="3-26",
    pagina_pdf=80,
    texto_literal=Verbatim(
        texto=("For traffic parallel to the span, culverts shall be analyzed "
               "for a single loaded lane with the single lane multiple "
               "presence factor."),
        pagina_pdf=80),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("El trafico «paralelo al vano» es el de la inmensa mayoria de las "
          "alcantarillas viales (C3.6.1.2.6b, misma columna de la pag. "
          "3-27): el vano de un tubo es su diametro, medido a lo largo de la "
          "via. La lectura de que las obras de este expediente caen ahi es "
          "del proyecto y la dice el paso de la carga viva."),
)

AASHTO_3_6_1_2_6A_DESPRECIABLE = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6a",
    titulo_numeral="3.6.1.2.6a—General",
    pagina_impresa="3-26",
    pagina_pdf=80,
    texto_literal=Verbatim(
        texto=("For single-span culverts, the effects of live load may be "
               "neglected where the depth of fill is more than 8.0 ft and "
               "exceeds the span length;"),
        pagina_pdf=80),
    caracter=Caracter.PERMISO,
    sesion=T5,
)

AASHTO_3_6_1_2_6A_CONCRETO_SOMERO = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6a",
    titulo_numeral="3.6.1.2.6a—General",
    pagina_impresa="3-26",
    pagina_pdf=80,
    texto_literal=Verbatim(
        texto=("Live load shall be distributed to concrete pipe culverts "
               "with less than 2.0 ft of cover in accordance with Eq. "
               "4.6.2.10.2-1, regardless of the direction of travel."),
        pagina_pdf=80),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Es el caso que este programa NO implementa: con menos de 2.0 ft "
          "(0.6096 m) de relleno sobre un tubo de concreto la Fase 8 se "
          "detiene con MetodoNoEvaluableError en vez de aplicar fuera de su "
          "dominio la distribucion de 3.6.1.2.6b."),
)

AASHTO_T3_6_1_2_6A_1 = _cita(
    id="AASHTO_LRFD_9.T3.6.1.2.6a-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 3.6.1.2.6a-1",
    titulo_numeral=("Table 3.6.1.2.6a-1—Live Load Distribution Factor (LLDF) "
                    "for Buried Structures"),
    pagina_impresa="3-27",
    pagina_pdf=81,
    texto_literal=Verbatim(texto="1.15 for diameter 2.0 ft or less",
                           pagina_pdf=81),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("Dos filas: «Concrete Pipe with fill depth 2.0 ft or greater» "
          "(1.15 para diametro de 2.0 ft o menos, 1.75 para 8.0 ft o mas, "
          "«Linearly interpolate for LLDF between these limits») y «All "
          "other culverts and buried structures» (1.15). El «diameter» se "
          "lee como el diametro INTERIOR del catalogo; vista de calculo en "
          "constantes_normativas (LLDF_*)."),
)

AASHTO_3_6_1_2_6B_PL = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6b#PL",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6b",
    titulo_numeral="3.6.1.2.6b—Traffic Parallel to the Culvert Span",
    pagina_impresa="3-28",
    pagina_pdf=82,
    pagina_pdf_titulo=81,
    texto_literal=Verbatim(
        texto="The live load vertical crown pressure shall be determined as:",
        pagina_pdf=82),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Las ecuaciones 3.6.1.2.6b-1 a -7 (pags. 3-27 y 3-28) se leyeron "
          "renderizadas: H_int-t = (s_w - w_t/12 - 0.06 D_i/12)/LLDF; "
          "w_w = w_t/12 + LLDF(H) + 0.06 D_i/12 (mas s_w si H >= H_int-t); "
          "H_int-p = (s_a - l_t/12)/LLDF; l_w = l_t/12 + LLDF(H) (mas s_a si "
          "H >= H_int-p); P_L = P(1 + IM/100)(m)/A_LL. La ec. -1 escribe D_j "
          "y la lista de simbolos D_i: errata tipografica de la fuente, el "
          "simbolo es el mismo. Las cifras en pulgadas y pies se convierten "
          "a SI una sola vez (constantes_fisicas)."),
)

AASHTO_C3_6_1_2_6B = _cita(
    id="AASHTO_LRFD_9.C3.6.1.2.6b",
    fuente_id="AASHTO_LRFD_9",
    numeral="C3.6.1.2.6b",
    titulo_numeral="C3.6.1.2.6b",
    pagina_impresa="3-27",
    pagina_pdf=81,
    texto_literal=Verbatim(
        texto=("The case where traffic is parallel to the culvert span "
               "applies to the vast majority of highway culverts."),
        pagina_pdf=81),
    caracter=Caracter.DEFINICION,
    sesion=T5,
)

MP_2_4_3_2_2_2 = _cita(
    id="MP.2.4.3.2.2.2",
    fuente_id="MP",
    numeral="2.4.3.2.2.2",
    titulo_numeral="Camión de Diseño",
    pagina_impresa="104",
    pagina_pdf=105,
    texto_literal=Verbatim(
        texto=("la distancia entre los dos ejes de 32.0-kips (14.55 t.) será "
               "tomada como aquella que, estando entre los límites de 14.0 ft "
               "(4.27 m.) y 30.0 ft (9.14 m.), resulta en los mayores "
               "efectos."),
        pagina_pdf=105),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("El eje del camion HL-93 en la unidad primaria del Manual, 32.0 "
          "kip; el «(14.55 t.)» es una equivalencia redondeada. Para la carga "
          "sobre una alcantarilla la separacion que gobierna es la MINIMA, "
          "14.0 ft, que es la que acerca los ejes."),
)

MP_2_4_3_2_2_3 = _cita(
    id="MP.2.4.3.2.2.3",
    fuente_id="MP",
    numeral="2.4.3.2.2.3",
    titulo_numeral="Tándem de Diseño",
    pagina_impresa="104",
    pagina_pdf=105,
    texto_literal=Verbatim(
        texto=("El tándem de diseño consistirá en un conjunto de dos ejes, "
               "cada uno con una carga de 25.0 kip (11.4 t.), espaciados a "
               "4.0 ft (1.20 m.). La distancia entre las ruedas de cada eje, "
               "en dirección transversal, será de 6.0 ft (1.80 m.)."),
        pagina_pdf=105),
    caracter=Caracter.DEFINICION,
    sesion=T5,
)

MP_2_4_3_2_2_5 = _cita(
    id="MP.2.4.3.2.2.5",
    fuente_id="MP",
    numeral="2.4.3.2.2.5",
    titulo_numeral="Área de Contacto de los Neumáticos",
    pagina_impresa="104",
    pagina_pdf=105,
    texto_literal=Verbatim(
        texto=("El área de contacto de una rueda consistente de una o dos "
               "neumáticos se asumirá como un rectángulo de 20.0 in. (0.50 "
               "m.) de ancho en dirección transversal del puente y 10.0 in. "
               "(0.25 m.) en el sentido del eje longitudinal del mismo."),
        pagina_pdf=105),
    caracter=Caracter.DEFINICION,
    sesion=T5,
)

MP_2_4_3_2_2_6 = _cita(
    id="MP.2.4.3.2.2.6",
    fuente_id="MP",
    numeral="2.4.3.2.2.6",
    titulo_numeral="Presencia Múltiple de Sobrecargas",
    pagina_impresa="105",
    pagina_pdf=106,
    texto_literal=Verbatim(
        texto="Se deberán utilizar al investigar el efecto de un carril cargado,",
        pagina_pdf=106),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("La frase introduce el uso obligatorio de la Tabla 2.4.3.2.2.6-1 "
          "con UN carril cargado: «1 | 1.20» (misma pagina)."),
)

MP_2_4_3_3_2 = _cita(
    id="MP.2.4.3.3.2",
    fuente_id="MP",
    numeral="2.4.3.3.2",
    titulo_numeral="Componentes Enterrados",
    pagina_impresa="109",
    pagina_pdf=110,
    texto_literal=Verbatim(
        texto=("El incremento por carga dinámica para alcantarillas y otras "
               "estructuras enterradas, en porcentaje, se deberá tomar "
               "como:"),
        pagina_pdf=110),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Sigue la ec. 2.4.3.3.2-1 (3.6.2.2-1 AASHTO): IM = 33(1.0 - "
          "0.125 D_E) >= 0 %, con «D_E = profundidad mínima de la cubierta de "
          "tierra sobre la estructura (ft)». El Manual conserva los PIES: "
          "la pendiente en SI es 0.125/0.3048 por metro "
          "(IM_ENTERRADO_PENDIENTE_SI)."),
)

MP_2_4_2_1_PESOS = _cita(
    id="MP.2.4.2.1#PESOS",
    fuente_id="MP",
    numeral="2.4.2.1, Tabla 2.4.2.1-1",
    titulo_numeral="Cargas Muertas: DC, DW, y EV",
    pagina_impresa="102",
    pagina_pdf=103,
    pagina_pdf_titulo=102,
    texto_literal=Verbatim(
        texto=("A falta de una información precisa, podrán usarse los pesos "
               "específicos de la tabla siguiente:"),
        pagina_pdf=103),
    caracter=Caracter.PERMISO,
    sesion=T5,
    nota=("Tabla 2.4.2.1-1 «Pesos específicos» (3.5.1-1 AASHTO), en kcf: "
          "«Arena, limo o arcilla compactado 0.120» y «Superficies de "
          "desgaste bituminosos 0.140» (igual que «Laminados grava, macadam, "
          "o de lastre»). PERMISO, no exigencia: rige a falta de informacion "
          "precisa, y el relleno de este proyecto no la tiene."),
)

MP_2_3_2_5 = _cita(
    id="MP.2.3.2.5",
    fuente_id="MP",
    numeral="2.3.2.5",
    titulo_numeral="Importancia Operativa",
    pagina_impresa="99",
    pagina_pdf=100,
    texto_literal=Verbatim(
        texto=("El propietario puede declarar si un puente, o algun "
               "componente estructural y conexión tienen importancia "
               "operativa."),
        pagina_pdf=100),
    caracter=Caracter.PERMISO,
    sesion=T5,
    nota=("Para resistencia: eta_I >= 1.05 criticos o esenciales, = 1.00 "
          "tipicos, >= 0.95 de relativa menor importancia (misma pagina). "
          "AASHTO 12.5.4 lo aplica a las estructuras enterradas."),
)

AASHTO_12_5_4 = _cita(
    id="AASHTO_LRFD_9.12.5.4",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.5.4",
    titulo_numeral="12.5.4—Load Modifiers and Load Factors",
    pagina_impresa="12-11",
    pagina_pdf=1649,
    texto_literal=Verbatim(
        texto=("For strength limit states, buried structures shall be "
               "considered redundant."),
        pagina_pdf=1649),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Con eta_D = 1.00 (diseño convencional) y eta_R = 1.00 "
          "(redundante), el modificador de la carga es el de importancia "
          "operativa, que declara el propietario (MP.2.3.2.5)."),
)

AASHTO_12_5_5 = _cita(
    id="AASHTO_LRFD_9.12.5.5",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.5.5",
    titulo_numeral="12.5.5—Resistance Factors",
    pagina_impresa="12-11",
    pagina_pdf=1649,
    texto_literal=Verbatim(
        texto=("Resistance factors for buried structures shall be taken as "
               "specified in Table 12.5.5-1."),
        pagina_pdf=1649),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Tabla 12.5.5-1 (pag. 12-12): tubo metalico helicoidal, area y "
          "pandeo 1.00; anular remachado o empernado, area y pandeo 1.00 y "
          "costura longitudinal 0.67; PE: empuje 1.00, rigidez del suelo "
          "0.90, pandeo global 0.70, flexion 1.00."),
)

AASHTO_12_5_6_1_FF = _cita(
    id="AASHTO_LRFD_9.12.5.6.1#FF",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.5.6.1",
    titulo_numeral="12.5.6.1—Corrugated Metal Pipe and Structural Plate Structures",
    pagina_impresa="12-13",
    pagina_pdf=1651,
    texto_literal=Verbatim(
        texto=("Flexibility factors for corrugated metal pipe, structural "
               "plate structures, and steel-reinforced thermoplastic culverts "
               "shall not exceed the values specified in Table 12.5.6.1-1."),
        pagina_pdf=1651),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Tabla 12.5.6.1-1: acero, corrugacion de 0.25 y 0.5 in, 43 in/kip "
          "(= 0.2455 mm/N); 1.0 in, 33 in/kip. Coincide con ASTM A796 num. "
          "10.3 para terraplen (0.245 mm/N con 13 mm): no hay discrepancia. "
          "C12.5.6.1: son exigencias CONSTRUCTIVAS, no un estado limite de "
          "servicio."),
)

AASHTO_12_7_2_2 = _cita(
    id="AASHTO_LRFD_9.12.7.2.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.7.2.2",
    titulo_numeral="12.7.2.2—Thrust",
    pagina_impresa="12-25",
    pagina_pdf=1663,
    texto_literal=Verbatim(
        texto="The factored thrust, TL, per unit length of wall shall be taken as:",
        pagina_pdf=1663),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("T_L = P_FD(S)/2 + P_FL(C_L)F_1/2; C_L = l_w <= S; F_1 = 0.75S/l_w "
          ">= F_min; F_min = 15/(12(S)) >= 1. P_FD «as specified in Article "
          "12.12.3.4 with VAF taken as 1.0 and D_o taken as S»: la lectura del "
          "proyecto de esa remision esta en la Interpretacion del paso."),
)

AASHTO_C12_7_2_2 = _cita(
    id="AASHTO_LRFD_9.C12.7.2.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="C12.7.2.2",
    titulo_numeral="C12.7.2.2",
    pagina_impresa="12-25",
    pagina_pdf=1663,
    texto_literal=Verbatim(
        texto=("Factored vertical crown pressure is calculated as the "
               "factored free-field soil pressure at the elevation of the "
               "top of the structure, plus the factored live load pressure "
               "distributed through the soil cover to the top of the "
               "structure."),
        pagina_pdf=1663),
    caracter=Caracter.DEFINICION,
    sesion=T5,
)

AASHTO_12_7_2_3 = _cita(
    id="AASHTO_LRFD_9.12.7.2.3",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.7.2.3",
    titulo_numeral="12.7.2.3—Wall Resistance",
    pagina_impresa="12-26",
    pagina_pdf=1664,
    texto_literal=Verbatim(
        texto=("The factored axial resistance, Rn, per unit length of wall, "
               "without consideration of buckling, shall be taken as:"),
        pagina_pdf=1664),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_7_2_4 = _cita(
    id="AASHTO_LRFD_9.12.7.2.4",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.7.2.4",
    titulo_numeral="12.7.2.4—Resistance to Buckling",
    pagina_impresa="12-26",
    pagina_pdf=1664,
    texto_literal=Verbatim(
        texto=("The wall area, calculated using Eq. 12.7.2.3-1, shall be "
               "investigated for buckling. If fcr < Fy, A shall be "
               "recalculated using fcr in lieu of Fy."),
        pagina_pdf=1664),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Ecs. 12.7.2.4-1 y -2 con k = «soil stiffness factor taken as "
          "0.22» (misma pagina); C12.7.2.4 lo llama conservador."),
)

AASHTO_12_7_2_5 = _cita(
    id="AASHTO_LRFD_9.12.7.2.5",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.7.2.5",
    titulo_numeral="12.7.2.5—Seam Resistance",
    pagina_impresa="12-27",
    pagina_pdf=1665,
    texto_literal=Verbatim(
        texto=("For pipe fabricated with longitudinal seams, the factored "
               "resistance of the seam shall be sufficient to develop the "
               "factored thrust in the pipe wall, TL."),
        pagina_pdf=1665),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Solo para costura LONGITUDINAL: la tuberia helicoidal con costura "
          "engargolada o soldada no la tiene (ASTM A796 num. 8.1.3.1). La "
          "resistencia nominal de la costura remachada de 68 x 13 mm esta en "
          "la Tabla 5 de A796 (tabla ASTM_A796.T5) y en la Tabla A12-7 de "
          "AASHTO; la EMPERNADA de esa corrugacion no esta en ninguna de las "
          "dos."),
)

AASHTO_TA12_9 = _cita(
    id="AASHTO_LRFD_9.TA12-9",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table A12-9",
    titulo_numeral=("Table A12-9—Mechanical Properties for Spiral Rib and "
                    "Corrugated Metal Pipe and Pipe Arch"),
    pagina_impresa="12-107",
    pagina_pdf=1745,
    texto_literal=Verbatim(
        texto=("Shall meet the requirements of AASHTO M 167M/M 167 (ASTM "
               "A761/A761M), M 218, and M 246 (ASTM A742)"),
        pagina_pdf=1745),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("Fila «Steel(3)»: F_u 45.0 ksi, F_y 33.0 ksi, E_m 29,000 ksi; la "
          "nota (3) es el texto literal. Son las cifras de la comprobacion "
          "LRFD que rige. ASTM A796 num. 4 escribe 225 / 310 / 200 000 MPa "
          "(redondeo metrico de las mismas): se usan solo en el contraste "
          "ASD."),
)

AASHTO_12_10_2_1_PESO_MIN = _cita(
    id="AASHTO_LRFD_9.12.10.2.1#PESO_MIN",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.2.1",
    titulo_numeral="12.10.2.1 Standard Installations",
    pagina_impresa="12-52",
    pagina_pdf=1690,
    pagina_pdf_titulo=1688,
    texto_literal=Verbatim(
        texto=("The unit weight of soil used to calculate earth load shall be "
               "the estimated unit weight for the soils specified for the "
               "pipe soil installation but shall not be taken to be less "
               "than 110 lb/ft3."),
        pagina_pdf=1690),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_10_2_1_VAF = _cita(
    id="AASHTO_LRFD_9.12.10.2.1#VAF",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.2.1",
    titulo_numeral="12.10.2.1 Standard Installations",
    pagina_impresa="12-52",
    pagina_pdf=1690,
    pagina_pdf_titulo=1688,
    texto_literal=Verbatim(
        texto=("Standard installations for both embankments and trenches "
               "shall be designed for positive projection, embankment loading "
               "conditions where Fe shall be taken as the vertical arching "
               "factor, VAF, specified in Table 12.10.2.1-3 for each type of "
               "standard installation."),
        pagina_pdf=1690),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("W_E = F_e w B_c H (Eq. 12.10.2.1-1). Tabla 12.10.2.1-3 (pag. "
          "12-53): VAF 1.35 / 1.40 / 1.40 / 1.45 para los Tipos 1 a 4. Los "
          "requisitos de cada tipo, Tabla 12.10.2.1-1 (pag. 12-50)."),
)

AASHTO_12_10_2_2 = _cita(
    id="AASHTO_LRFD_9.12.10.2.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.2.2",
    titulo_numeral="12.10.2.2 Pipe Fluid Weight",
    pagina_impresa="12-54",
    pagina_pdf=1692,
    texto_literal=Verbatim(
        texto=("The unfactored weight of fluid, WF, in the pipe shall be "
               "considered in design based on a fluid weight of 62.4 lb/ft3, "
               "unless otherwise specified."),
        pagina_pdf=1692),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("62.4 lb/ft3 = 9.80 kN/m3; el programa usa el peso especifico del "
          "agua de constantes_fisicas (9.81 kN/m3), la misma magnitud "
          "fisica: 0.1 % de diferencia, del lado mayor."),
)

AASHTO_12_10_2_3 = _cita(
    id="AASHTO_LRFD_9.12.10.2.3",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.2.3",
    titulo_numeral="12.10.2.3—Live Loads",
    pagina_impresa="12-54",
    pagina_pdf=1692,
    texto_literal=Verbatim(
        texto=("For standard installations, the live load on the pipe shall "
               "be assumed to have a uniform vertical distribution across the "
               "top of the pipe and the same distribution across the bottom "
               "of the pipe as given in Figure 12.10.2.1-1."),
        pagina_pdf=1692),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_10_4_3_1 = _cita(
    id="AASHTO_LRFD_9.12.10.4.3.1",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.4.3.1",
    titulo_numeral="12.10.4.3.1—Bearing Resistance",
    pagina_impresa="12-64",
    pagina_pdf=1702,
    texto_literal=Verbatim(
        texto=("The three-edge bearing resistance of the reinforced concrete "
               "pipe, corresponding to an experimentally tested service load, "
               "shall not be less than the design load determined for the "
               "pipe as installed, taken as:"),
        pagina_pdf=1702),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("D = (12/S_i)((W_E + W_F)/B_FE + W_L/B_FLL) (Eq. 12.10.4.3.1-1, en "
          "kip/ft y pulgadas): en SI, D en N/m/mm con W en N/m y S_i en mm, "
          "sin factor de unidad. Es estado limite de SERVICIO: sin factores "
          "de carga ni de resistencia."),
)

AASHTO_12_10_4_3_1_TIPO1 = _cita(
    id="AASHTO_LRFD_9.12.10.4.3.1#TIPO1",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.4.3.1",
    titulo_numeral="12.10.4.3.1—Bearing Resistance",
    pagina_impresa="12-64",
    pagina_pdf=1702,
    texto_literal=Verbatim(
        texto=("For Type 1 installations, D loads, as calculated above, shall "
               "be modified by multiplying by an installation factor of "
               "1.10."),
        pagina_pdf=1702),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_10_4_3_1_DLOAD = _cita(
    id="AASHTO_LRFD_9.12.10.4.3.1#DLOAD",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.4.3.1",
    titulo_numeral="12.10.4.3.1—Bearing Resistance",
    pagina_impresa="12-64",
    pagina_pdf=1702,
    texto_literal=Verbatim(
        texto=("The D-load for a particular class and size of pipe shall be "
               "determined in accordance with AASHTO M 170M"),
        pagina_pdf=1702),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_10_4_3_2A = _cita(
    id="AASHTO_LRFD_9.12.10.4.3.2a",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.4.3.2a",
    titulo_numeral="12.10.4.3.2a—Earth Load Bedding Factor for Circular Pipe",
    pagina_impresa="12-65",
    pagina_pdf=1703,
    texto_literal=Verbatim(
        texto=("Earth load bedding factors, BFE, for circular pipe are "
               "presented in Table 12.10.4.3.2a-1."),
        pagina_pdf=1703),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("Tabla 12.10.4.3.2a-1: B_FE por diametro (12, 24, 36, 72 y 144 in) "
          "y tipo de instalacion; «For pipe diameters other than those "
          "listed ... may be determined by interpolation»."),
)

AASHTO_12_10_4_3_2C = _cita(
    id="AASHTO_LRFD_9.12.10.4.3.2c",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.10.4.3.2c",
    titulo_numeral="12.10.4.3.2c—Live Load Bedding Factors",
    pagina_impresa="12-66",
    pagina_pdf=1704,
    texto_literal=Verbatim(
        texto=("The bedding factor, BFLL, for live load, WL, for both "
               "circular pipe and arch and for elliptical pipe shall be taken "
               "as specified in Table 12.10.4.3.2c-1."),
        pagina_pdf=1704),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_M170M_T2_DLOAD = _cita(
    id="AASHTO_M170M.T2#DLOAD",
    fuente_id="AASHTO_M170M",
    numeral="Table 2",
    titulo_numeral="Design Requirements for Class II Reinforced Concrete Pipe",
    pagina_impresa="M 170M-5",
    pagina_pdf=5,
    texto_literal=Verbatim(texto="D-load to produce a 0.3-mm crack 50.0",
                           pagina_pdf=5),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T5,
    nota=("LEIDO POR IMAGEN, y es LA UNICA D-load de 0.3 mm LEGIBLE en el "
          "ejemplar. La pag. PDF 5 («Table 2—Continued») imprime al pie "
          "«D-load to produce a 0.3-mm crack 50.0» y «D-load to produce the "
          "ultimate load ?S.0» (el primer digito, ilegible). Las Tablas 1, 3, "
          "4 y 5 son recomposiciones OCR con digitos equivocados (nota de la "
          "Fuente): la de la Clase V imprime «\\ 40.0», la de la Clase III "
          "solo la ultima, «100.0», y la Clase I e IV no se leen. NO SE "
          "COMPLETAN DE MEMORIA: las Clases I, III, IV y V quedan sin D-load "
          "en 'clases_producto_por_relleno' y el paso lo dice. Y la Tabla 2 "
          "(PDF 4) tiene filas con pared B y acero de 300 a 2700 mm: la "
          "Clase II existe en todo el catalogo de concreto."),
)

EG2013_506_02_CLASE = _cita(
    id="EG2013.506.02#CLASE",
    fuente_id="EG2013",
    numeral="506.02",
    titulo_numeral="Tubería",
    pagina_impresa="959",
    pagina_pdf=967,
    texto_literal=Verbatim(
        texto=("La tubería deberá cumplir los requisitos de materiales, "
               "diseño y manufactura establecidos en la especificación AASHTO "
               "M-170M. La clase de tubería y su diámetro interno, se deberán "
               "indicar en el Proyecto."),
        pagina_pdf=967),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("La norma peruana manda que el PROYECTO indique la clase: es la "
          "salida de la Fase 8 para el tubo de concreto, no una entrada."),
)

EG2013_506_10 = _cita(
    id="EG2013.506.10",
    fuente_id="EG2013",
    numeral="506.10",
    titulo_numeral="Sujeción",
    pagina_impresa="961",
    pagina_pdf=969,
    texto_literal=Verbatim(
        texto=("éste se deberá aumentar y compactar en capas a los lados de la "
               "tubería y hacia arriba, al mismo nivel de densidad exigido "
               "para el solado, hasta una altura no menor a 1/6 del diámetro "
               "exterior de ella."),
        pagina_pdf=969),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Por encima de 1/6 del diametro exterior el relleno es el de la "
          "Seccion 502 (506.11), que remite a la densidad de 205.12(c)(1): "
          "90 % del Proctor Modificado en base y cuerpo. Con esas dos "
          "exigencias el EG-2013 no garantiza el 95 % de Categoria I en toda "
          "la zona de riñones que pide el Tipo 1 de AASHTO, y si excluye el "
          "Tipo 4, que no exige compactacion: es la lectura con que "
          "'instalacion_estandar_concreto' fija su ventana."),
)

EG2013_205_12_COMPACTACION = _cita(
    id="EG2013.205.12#COMPACTACION",
    fuente_id="EG2013",
    numeral="205.12 c) 1",
    titulo_numeral="Compactación",
    pagina_impresa="193",
    pagina_pdf=201,
    texto_literal=Verbatim(
        texto=("el 90% de la máxima densidad obtenida en el ensayo Proctor "
               "Modificado de referencia (De) para la base y cuerpo del "
               "terraplén"),
        pagina_pdf=201),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Y «el 95% ... cuando se verifique la compactación de la corona "
          "del terraplén». La Seccion 502 (rellenos para estructuras) remite "
          "a estos mismos niveles (502.09(c)(1))."),
)

EG2013_T507_01 = _cita(
    id="EG2013.T507-01",
    fuente_id="EG2013",
    numeral="507.02 a), Tabla 507-01",
    titulo_numeral="Espesores Mínimos de Alcantarillas Circulares y Abovedadas",
    pagina_impresa="970",
    pagina_pdf=978,
    texto_literal=Verbatim(
        texto=("Los espesores mínimos para las tuberías con los respectivos "
               "diámetros serán los indicados en la Tabla 507-01."),
        pagina_pdf=978),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Circular: 0.60 m -> 1.80 mm; 0.90 -> 2.00; 1.20 -> 2.50; 1.50 -> "
          "3.00; 1.80 -> 3.30 (al pie: «ASTM–A–760, TABLA 1 – ASTM–A-929 – "
          "TABLA 4»). ES LA UNICA CIFRA PERUANA SOBRE EL CALIBRE DEL TMC y "
          "hasta T-5 ningun modulo la leia: la plancha adoptada de 2.01 mm "
          "queda por debajo del minimo desde 1.20 m de diametro. Vista de "
          "calculo: ESPESOR_MIN_TMC_EG2013_MM."),
)

EG2013_508_07_COMPACTACION = _cita(
    id="EG2013.508.07#COMPACTACION",
    fuente_id="EG2013",
    numeral="508.07",
    titulo_numeral="Colocación del relleno alrededor de la estructura",
    pagina_impresa="984",
    pagina_pdf=992,
    texto_literal=Verbatim(
        texto=("El relleno deberá compactarse hasta alcanzar una densidad "
               "mayor al 95% de la Máxima Densidad Seca-M.D.S. del Próctor "
               "Modificado"),
        pagina_pdf=992),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("El material del relleno es el de la Seccion 502 (mismo numeral), "
          "y el de la cama y la SUJECION LATERAL lo fija el 508.02 d): "
          "granular (cita EG2013.508.02#GRANULAR). Con 95 % del Proctor "
          "MODIFICADO la compactacion es al menos la de las columnas «-95» de "
          "la Tabla 12.12.3.5-1 de AASHTO (Proctor ESTANDAR, T 99), porque la "
          "densidad maxima del ensayo modificado no es menor que la del "
          "estandar. La version anterior de esta nota decia que el tipo de "
          "suelo no lo fija la norma y que por eso se tomaba «el mas "
          "desfavorable» (Cl-95): omitia el 508.02 d) (auditoria de T-5)."),
)

AASHTO_12_11_2_1 = _cita(
    id="AASHTO_LRFD_9.12.11.2.1#LL",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.11.2.1",
    titulo_numeral="12.11.2.1—General",
    pagina_impresa="12-68",
    pagina_pdf=1706,
    texto_literal=Verbatim(
        texto=("Distribution of wheel loads to culverts with 2.0 ft or more "
               "of cover shall be as specified in Article 3.6.1.2.6."),
        pagina_pdf=1706),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_11_2_2_1 = _cita(
    id="AASHTO_LRFD_9.12.11.2.2.1",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.11.2.2.1",
    titulo_numeral="12.11.2.2.1—Embankment and Trench Conditions",
    pagina_impresa="12-69",
    pagina_pdf=1707,
    texto_literal=Verbatim(
        texto=("Fe shall not exceed 1.15 for installations with compacted "
               "fill along the sides of the box section, or 1.40 for "
               "installations with uncompacted fill along the sides of the "
               "box section."),
        pagina_pdf=1707),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota="W_E = F_e gamma_s B_c H con F_e = 1 + 0.20 H/B_c (Eqs. 12.11.2.2.1-1 y -2).",
)

AASHTO_T12_12_3_3_1 = _cita(
    id="AASHTO_LRFD_9.T12.12.3.3-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 12.12.3.3-1",
    titulo_numeral="Table 12.12.3.3-1—Mechanical Properties of Thermoplastic Pipe",
    pagina_impresa="12-77",
    pagina_pdf=1715,
    texto_literal=Verbatim(
        texto="Table 12.12.3.3-1—Mechanical Properties of Thermoplastic Pipe",
        pagina_pdf=1715),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("Fila «Corrugated PE Pipe – AASHTO M 294» (leida renderizada): "
          "5.0 % | 4.1 % | F_u 3.0 ksi, E 110.0 ksi (inicial) | 0.90, 22 (50 "
          "años) | 0.90, 21 (75 años)."),
)

AASHTO_12_12_3_5 = _cita(
    id="AASHTO_LRFD_9.12.12.3.5",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.5",
    titulo_numeral="12.12.3.5—Factored and Service Loads",
    pagina_impresa="12-78",
    pagina_pdf=1716,
    texto_literal=Verbatim(texto="The factored thrust shall be taken as:",
                           pagina_pdf=1716),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Eqs. 12.12.3.5-1 a -8, leidas renderizadas; K_gammaE «installation "
          "factor typically taken as 1.5 to provide traditional safety» "
          "(misma pagina); K_2 = 1.0 para el empuje en el arranque (pag. "
          "12-79)."),
)

AASHTO_T12_12_3_5_1 = _cita(
    id="AASHTO_LRFD_9.T12.12.3.5-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 12.12.3.5-1",
    titulo_numeral="Table 12.12.3.5-1—Ms Based on Soil Type and Compaction Condition",
    pagina_impresa="12-81",
    pagina_pdf=1719,
    texto_literal=Verbatim(
        texto="Table 12.12.3.5-1—Ms Based on Soil Type and Compaction Condition",
        pagina_pdf=1719),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("M_s en ksi por nivel de P_sp (1, 5, 10, 20, 40 y 60 psi) y por "
          "suelo y compactacion (Sn, Si, Cl; % del Proctor ESTANDAR, nota 2). "
          "Entre niveles se interpola (pag. 12-80)."),
)

AASHTO_12_12_3_10_1B_STUB = _cita(
    id="AASHTO_LRFD_9.12.12.3.10.1b#STUB",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.10.1b",
    titulo_numeral="12.12.3.10.1b—Local Buckling Effective Area",
    pagina_impresa="12-85",
    pagina_pdf=1723,
    pagina_pdf_titulo=1722,
    texto_literal=Verbatim(
        texto=("As an alternate to determining the effective area by the "
               "calculation procedure presented above, the results of the "
               "stub compression test, AASHTO T 341, may be used, in which "
               "case the effective area, Aeff, shall satisfy:"),
        pagina_pdf=1723),
    caracter=Caracter.PERMISO,
    sesion=T5,
    nota=("A_eff = P_st K_t / F_u <= A_g (Eq. 12.12.3.10.1b-5); K_t de la "
          "Tabla 12.12.3.10.1b-1 (PE: 0.9 inicial, 0.3 a 50 años, 0.25 a 75)."),
)

AASHTO_12_12_3_10_1C_EP = _cita(
    id="AASHTO_LRFD_9.12.12.3.10.1c#EP",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.10.1c",
    titulo_numeral="12.12.3.10.1c—Compression Strain",
    pagina_impresa="12-86",
    pagina_pdf=1724,
    pagina_pdf_titulo=1723,
    texto_literal=Verbatim(
        texto=("short-term modulus for short-term loading or long-term modulus "
               "of pipe material for long-term loading as specified in Table "
               "12.12.3.3-1"),
        pagina_pdf=1724),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Es la definicion de E_p en las Eqs. 12.12.3.10.1c-1 y -2. De ella "
          "lee el proyecto que la deformacion se SUMA por duracion: la de las "
          "cargas permanentes con el modulo y el area efectiva de largo plazo "
          "y la de la carga viva con los iniciales (Interpretacion en el paso "
          "F8.EMPUJE)."),
)

AASHTO_12_12_3_10_1D = _cita(
    id="AASHTO_LRFD_9.12.12.3.10.1d",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.10.1d",
    titulo_numeral="12.12.3.10.1d—Thrust Strain Limits",
    pagina_impresa="12-86",
    pagina_pdf=1724,
    texto_literal=Verbatim(
        texto="The factored compression strain due to thrust, εuc, shall satisfy:",
        pagina_pdf=1724),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
)

AASHTO_12_12_3_10_1E = _cita(
    id="AASHTO_LRFD_9.12.12.3.10.1e",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.10.1e",
    titulo_numeral="12.12.3.10.1e—General Buckling Strain Limits",
    pagina_impresa="12-86",
    pagina_pdf=1724,
    texto_literal=Verbatim(
        texto=("The factored compression strain due to thrust, incorporating "
               "local buckling effects, εuc, shall satisfy:"),
        pagina_pdf=1724),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("eps_bck = 1.2 C_n (E_p I_p)^(1/3) [phi_s M_s (1-2nu)/(1-nu)^2]^(2/3) "
          "R_h / (A_eff E_p), R_h = 11.4/(11 + D/(12H)), C_n = 0.55 (pag. "
          "12-87). Adimensional en cualquier sistema coherente de unidades."),
)

AASHTO_12_12_2_2 = _cita(
    id="AASHTO_LRFD_9.12.12.2.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.2.2",
    titulo_numeral="12.12.2.2—Deflection Requirement",
    pagina_impresa="12-75",
    pagina_pdf=1713,
    pagina_pdf_titulo=1712,
    texto_literal=Verbatim(
        texto=("Total deflection, calculated using Spangler’s expression for "
               "predicting flexural deflection in combination with the "
               "expression for circumferential shortening, shall be "
               "determined as:"),
        pagina_pdf=1713),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Eq. 12.12.2.2-2: Delta_t = K_B(D_L P_sp + C_L P_L) D_o / (1000(E_p "
          "I_p/R^3 + 0.061 M_s)) + eps_sc D; «D_L ... a value of 1.5 is "
          "typical» y «K_B ... a value of 0.10 is typical». El 1000 es el "
          "paso de ksi a psi: en SI desaparece."),
)

AASHTO_C12_12_2_2 = _cita(
    id="AASHTO_LRFD_9.C12.12.2.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="C12.12.2.2",
    titulo_numeral="C12.12.2.2",
    pagina_impresa="12-74",
    pagina_pdf=1712,
    texto_literal=Verbatim(
        texto=("The construction specifications set the allowable deflection, "
               "ΔA, for thermoplastic pipe at five percent as a generally "
               "appropriate limit."),
        pagina_pdf=1712),
    caracter=Caracter.RECOMENDACION,
    sesion=T5,
)

AASHTO_M294_TRAD_7_7 = _cita(
    id="AASHTO_M294_TRAD.7.7",
    fuente_id="AASHTO_M294_TRAD",
    numeral="7.7",
    titulo_numeral="Ensayo de compresión",
    pagina_impresa="s/n",
    pagina_pdf=8,
    texto_literal=Verbatim(
        texto=("La capacidad de compresión del perfil en cualquier probeta en "
               "el ensayo de compresión no deberá ser inferior al 50 por "
               "ciento del área transversal bruta multiplicada por el límite "
               "elástico mínimo especificado cuando se ejecuta el ensayo de "
               "acuerdo con la Sección 9.8."),
        pagina_pdf=8),
    caracter=Caracter.EXIGENCIA,
    verificada=False,
    nota=("SIN FIRMA A PROPOSITO, no sin verificar: traduccion no oficial de "
          "AASHTO M 294-11. Lo que acredita es lo que la traduccion imprime, y "
          "sin folio no se firma (mismo regimen que las otras cuatro citas de "
          "esta fuente; leida en texto e imagen por T-5). Es el MINIMO de producto "
          "con que el programa obtiene el area efectiva del perfil sin "
          "conocer su geometria: P_st >= 0.5 A_g F_y, y por 12.12.3.10.1b-5, "
          "A_eff = P_st K_t / F_u."),
)

ASTM_A796_9_1 = _cita(
    id="ASTM_A796.9.1",
    fuente_id="ASTM_A796",
    numeral="9.1",
    titulo_numeral="Factored Loads",
    pagina_impresa="4",
    pagina_pdf=4,
    jerarquia_numeral=("9.", "Design by LRFD Method"),
    texto_literal=Verbatim(
        texto=("The pipe shall be designed to resist the following "
               "combination of factored earth load (EL) and live load plus "
               "impact (LL + IL):"),
        pagina_pdf=4),
    caracter=Caracter.EXIGENCIA,
    metodo=IMAGEN,
    sesion=T5,
    nota=("Sigue la ec. (8), P_f = 1.95 EL + 1.75 (LL + IL), con EL = Hw "
          "(ec. 1, la columna de suelo SOBRE el tubo). Es la lectura que la "
          "practica especifica del acero corrugado hace de la presion de "
          "clave: sin factor de instalacion ni nivel de arranque, y coincide "
          "con C12.7.2.2 de AASHTO. Leida por imagen (PDF 4)."),
)

ASTM_A796_8_1_3_1 = _cita(
    id="ASTM_A796.8.1.3.1",
    fuente_id="ASTM_A796",
    numeral="8.1.3.1",
    titulo_numeral="Required Seam Strength",
    pagina_impresa="4",
    pagina_pdf=4,
    texto_literal=Verbatim(
        texto=("Since helical lockseam and welded-seam pipe have no "
               "longitudinal seams, this criterion is not valid for these "
               "types of pipe."),
        pagina_pdf=4),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T5,
)


# ===========================================================================
# --- T-5 (cierre) --- Las citas que pidieron las dos auditorias adversariales
# y las decisiones del dueño del 2026-11-12. Leidas por la sesion de cierre
# abriendo cada pagina: por TEXTO las de AASHTO LRFD y EG-2013; por IMAGEN la
# de AASHTO M 170M.
# ===========================================================================

AASHTO_3_6_1_2_6A_VARIOS_VANOS = _cita(
    id="AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS",
    fuente_id="AASHTO_LRFD_9",
    numeral="3.6.1.2.6a",
    titulo_numeral="3.6.1.2.6a—General",
    pagina_impresa="3-26",
    pagina_pdf=80,
    texto_literal=Verbatim(
        texto=("for multiple span culverts, the effects may be neglected "
               "where the depth of fill exceeds the distance between inside "
               "faces of end walls."),
        pagina_pdf=80),
    caracter=Caracter.PERMISO,
    sesion=T5,
    nota=("La segunda mitad del permiso de #DESPRECIABLE: en una alcantarilla "
          "de VARIOS vanos la condicion no es la luz de un vano sino la "
          "distancia entre las caras interiores de los muros extremos. El "
          "marco de varias celdas la usa (`M8.demanda_marco`); el permiso "
          "solo se toma si 'carga_viva_bajo_relleno_alto' lo declara."),
)

AASHTO_1_3_5 = _cita(
    id="AASHTO_LRFD_9.1.3.5",
    fuente_id="AASHTO_LRFD_9",
    numeral="1.3.5",
    titulo_numeral="1.3.5—Operational Importance",
    pagina_impresa="1-7",
    pagina_pdf=22,
    texto_literal=Verbatim(
        texto=("The Owner may declare a bridge or any structural component "
               "and connection thereof to be of operational priority."),
        pagina_pdf=22),
    caracter=Caracter.PERMISO,
    sesion=T5,
    nota=("Es quien fija eta_I: el Propietario. La misma pagina gradua eta_I "
          ">= 1.05 (critical or essential), 1.00 (typical) y >= 0.95 "
          "(relatively less important), que es la graduacion que el Manual de "
          "Puentes 2.3.2.5 traduce. NINGUNA de las dos prescribe 1.05 para "
          "una estructura enterrada: 12.5.4 solo fija la redundancia."),
)

AASHTO_T12_10_2_1_1 = _cita(
    id="AASHTO_LRFD_9.T12.10.2.1-1",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 12.10.2.1-1",
    titulo_numeral=("Table 12.10.2.1-1—Standard Embankment Installation Soils "
                    "and Minimum Compaction Requirements"),
    pagina_impresa="12-50",
    pagina_pdf=1688,
    texto_literal=Verbatim(
        texto=("No compaction required, except if Category III, use 85% "
               "Category III"),
        pagina_pdf=1688),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("La fila del Tipo 4, riñones y costado inferior. Las otras tres "
          "(misma pagina): Tipo 1, riñones 95 % Categoria I, costado 90 % I, "
          "95 % II o 100 % III; Tipo 2, riñones 90 % I o 95 % II, costado "
          "85 % I, 90 % II o 95 % III; Tipo 3, riñones y costado 85 % I, 90 % "
          "II o 95 % III. Cama: D_o/24, no menos de 3.0 in, en los Tipos 1 a "
          "3 sobre suelo; ninguna en el Tipo 4."),
    interpretacion=Interpretacion(
        texto=("El proyecto lee la exigencia del EG-2013 para el tubo de "
               "concreto --solado de subbase granular de 15 cm y sujecion "
               "hasta un sexto del diametro exterior al 95 % del Proctor "
               "Modificado (506.07 y 506.10), y por encima el relleno para "
               "estructuras al 90 % del Proctor Modificado con los materiales "
               "de terraplen (506.11, 502.02 y 205.12)-- como una instalacion "
               "de Tipo 3 de esta tabla."),
        en_contra=(
            "la tabla gradua la compactacion en Proctor ESTANDAR y remite la "
            "equivalencia con el Modificado a la Tabla 27.5.2.2-3 de la "
            "especificacion de construccion de AASHTO, que no esta en "
            "normas/: lo unico que se puede afirmar sin ella es que el 90 % "
            "del Modificado es por lo menos el 90 % del Estandar",
            "con el 90 % del Estandar el Tipo 3 queda garantizado para las "
            "Categorias I y II (85 y 90 %), pero no para la III, que pide "
            "95 %; y el EG-2013 admite en un terraplen el suelo A-2-6, que la "
            "Tabla 12.12.3.5-2 de la misma norma agrupa con las arcillas",
            "la definicion de las Categorias I, II y III tampoco esta en la "
            "especificacion de diseño: se leen por analogia con Sn, Si y Cl "
            "de la Tabla 12.12.3.5-2",
            "la sujecion granular del EG-2013 llega a un sexto del diametro "
            "exterior, y la zona de riñones de la tabla, hasta el eje del "
            "tubo",
        ),
        a_favor=(
            "el EG-2013 exige compactar TODO el relleno, que es justo lo que "
            "el Tipo 4 no pide: verificar con el Tipo 4 supone una "
            "instalacion peor que la que la especificacion garantiza",
            "el solado y la sujecion son de subbase granular al 95 % del "
            "Proctor Modificado, mejor que lo que el Tipo 3 pide en esa zona",
            "el Tipo 4 queda dentro de la ventana del criterio y la Fase 8 "
            "imprime al lado la D-load, la clase y el relleno maximo que "
            "saldrian con el: el peso de esta lectura queda a la vista",
            "es la decision del dueño del proyecto (2026-11-12)",
        ),
    ),
)

AASHTO_T12_10_2_1_1_PROCTOR = _cita(
    id="AASHTO_LRFD_9.T12.10.2.1-1#PROCTOR",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 12.10.2.1-1",
    titulo_numeral=("Table 12.10.2.1-1—Standard Embankment Installation Soils "
                    "and Minimum Compaction Requirements"),
    pagina_impresa="12-51",
    pagina_pdf=1689,
    pagina_pdf_titulo=1688,
    texto_literal=Verbatim(
        texto=("shall be taken to refer to a soil material category with a "
               "minimum standard proctor compaction of 95 percent. Equivalent "
               "modified proctor values shall be as given in Table 27.5.2.2-3 "
               "of the AASHTO LRFD Bridge Construction Specifications."),
        pagina_pdf=1689),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("La primera de las interpretaciones que la norma pone al pie de la "
          "tabla. La Tabla 27.5.2.2-3 que nombra NO esta en normas/."),
)

EG2013_506_07 = _cita(
    id="EG2013.506.07",
    fuente_id="EG2013",
    numeral="506.07",
    titulo_numeral="Solado",
    pagina_impresa="960",
    pagina_pdf=968,
    texto_literal=Verbatim(
        texto=("su compactación mínima será la que se especifica para la "
               "corona en la Subsección"),
        pagina_pdf=968),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("El solado: «una capa o solado de material granular, que cumplan "
          "con las características de material para subbase, de por lo menos "
          "15 cm de espesor compactado», compactado como la corona del "
          "terraplen (205.12(c)(1): 95 % del Proctor Modificado). La sujecion "
          "(506.10) sube con el mismo material y la misma densidad hasta un "
          "sexto del diametro exterior; el relleno (506.11) es el de la "
          "Seccion 502."),
)

EG2013_T205_01 = _cita(
    id="EG2013.T205-01",
    fuente_id="EG2013",
    numeral="205.02, Tabla 205-01",
    titulo_numeral="Requisitos de los materiales",
    pagina_impresa="186",
    pagina_pdf=194,
    texto_literal=Verbatim(
        texto="A-1-a, A-1-b, A-2-4, A-2-6 y A-3",
        pagina_pdf=194),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Los materiales de terraplen, que la Seccion 502 (502.02, pag. "
          "impresa 895) manda usar en los rellenos para estructuras: «Tipo de "
          "Material: A-1-a, A-1-b, A-2-4, A-2-6 y A-3», con indice de "
          "plasticidad menor de 11 en base y cuerpo y menor de 10 en la "
          "corona. El A-2-6 es el mas plastico de los cinco, y la Tabla "
          "12.12.3.5-2 de AASHTO LRFD lo agrupa con las arcillas (Cl)."),
)

EG2013_507_02_EMPERNADA = _cita(
    id="EG2013.507.02#EMPERNADA",
    fuente_id="EG2013",
    numeral="507.02 a)",
    titulo_numeral=("Tubos conformados estructuralmente de planchas o láminas "
                    "corrugadas de acero galvanizado en caliente"),
    pagina_impresa="969",
    pagina_pdf=977,
    texto_literal=Verbatim(
        texto=("Para los tubos, circulares y/o abovedados y sus accesorios "
               "(pernos, tuercas) de corruga (68mm x 13mm), del rango de las "
               "dimensiones corresponden a 900 mm y 2100 mm de diámetro, se "
               "seguirá la especificación ASTM A-929 y AASHTO M-36 / ASTM "
               "A-760."),
        pagina_pdf=977),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("El mismo inciso fija las normas de los pernos (ASTM A-449 / F568 "
          "y A 307 Grado A) y de las tuercas (A-563 Grado C), y habla del "
          "«corrugado, perforado y formación de las planchas»."),
    interpretacion=Interpretacion(
        texto=("El proyecto lee que el producto que la norma peruana describe "
               "para la corrugacion de 68 por 13 mm es tuberia ARMADA con "
               "pernos, es decir, con costura longitudinal empernada."),
        en_contra=(
            "el inciso no usa la palabra «costura» ni dice que la union "
            "longitudinal sea empernada: nombra los pernos como accesorios",
            "las normas de producto que cita (AASHTO M 36 / ASTM A 760) "
            "cubren tambien la tuberia helicoidal y la remachada",
        ),
        a_favor=(
            "el titulo habla de tubos «conformados estructuralmente de "
            "planchas», y el texto del perforado de las planchas y de las "
            "normas de pernos y tuercas: una tuberia helicoidal o remachada "
            "no lleva pernos estructurales",
            "la lectura no decide el valor de archivo de 'fabricacion_tmc' "
            "--la empernada no tiene resistencia tabulada y detendria la "
            "Fase 8--: solo obliga a AVISAR que la costura se verifico con "
            "la resistencia de otra fabricacion",
        ),
    ),
)

EG2013_508_02_GRANULAR = _cita(
    id="EG2013.508.02#GRANULAR",
    fuente_id="EG2013",
    numeral="508.02 d)",
    titulo_numeral="Material para cama de asiento",
    pagina_impresa="982",
    pagina_pdf=990,
    texto_literal=Verbatim(
        texto=("La cama de asiento y la sujeción lateral se construirán con "
               "material granular cuyas características estarán de acuerdo "
               "con lo establecido en la Subsección 400.02 y la Sección 301."),
        pagina_pdf=990),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("La Seccion 301 es la de los afirmados: franjas granulometricas "
          "con 5 a 25 % de finos e indice de plasticidad de 4 a 9 (cita "
          "EG2013.T301-01). La misma letra dice que la cama «estará "
          "constituida por arena gruesa»."),
    interpretacion=Interpretacion(
        texto=("El proyecto lee el material granular de la Seccion 301 como "
               "un suelo de las columnas Sn o Si de la Tabla 12.12.3.5-1 de "
               "AASHTO LRFD, y adopta la menos favorable de las dos (Si) al "
               "95 % para la zona de la que depende el modulo del suelo."),
        en_contra=(
            "la Tabla 12.12.3.5-2 dice que sus correlaciones con otros tipos "
            "de suelo son aproximadas",
            "por la columna de clasificacion ASTM de esa tabla, una arena o "
            "grava arcillosa con mas del 20 % de finos seria Cl, y la franja "
            "F de la Tabla 301-01 admite hasta 25 %: la columna Cl no queda "
            "excluida del todo, y por eso sigue en la ventana del criterio",
        ),
        a_favor=(
            "por la columna de clasificacion AASHTO M 145, que es la del "
            "EG-2013, un material con no mas de 25 % de finos e indice de "
            "plasticidad de 4 a 9 es A-1 o A-2-4: Sn o Si. Los grupos de la "
            "columna Cl (A-2-6, A-2-7, A-5, A-6) piden un indice de "
            "plasticidad de 11 o mas, o son limos y arcillas",
            "el 508.07 exige mas del 95 % del Proctor Modificado, que es al "
            "menos el 95 % del Estandar de la tabla",
        ),
    ),
)

EG2013_T301_01 = _cita(
    id="EG2013.T301-01",
    fuente_id="EG2013",
    numeral="301.02, Tabla 301-01",
    titulo_numeral="Tabla 301-01",
    pagina_impresa="238",
    pagina_pdf=246,
    texto_literal=Verbatim(
        texto="Índice de Plasticidad: 4-9%",
        pagina_pdf=246),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Requisitos del afirmado, al pie de la Tabla 301-01 (franjas A-1, "
          "A-2, C, D, E y F, con 5-20, 5-20, 5-15, 5-20, 6-20 y 8-25 % que "
          "pasa el tamiz N.° 200): limite liquido 35 % max., indice de "
          "plasticidad 4-9 %, CBR 40 % min."),
)

AASHTO_T12_12_3_5_2 = _cita(
    id="AASHTO_LRFD_9.T12.12.3.5-2",
    fuente_id="AASHTO_LRFD_9",
    numeral="Table 12.12.3.5-2",
    titulo_numeral=("Table 12.12.3.5-2—Equivalent ASTM and AASHTO Soil "
                    "Classifications"),
    pagina_impresa="12-82",
    pagina_pdf=1720,
    texto_literal=Verbatim(
        texto="The correlations to other soil types are approximate.",
        pagina_pdf=1720),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("Sn (Gravelly sand, SW): SW, SP, GW, GP, arenas y gravas con 12 % "
          "de finos o menos; AASHTO M 145 A-1, A-3. Si (Sandy silt, ML): GM, "
          "SM, ML, y GC y SC con menos de 20 % que pasa el tamiz N.° 200; "
          "A-2-4, A-2-5, A-4. Cl (Silty clay, CL): CL, MH, GC, SC, y GC y SC "
          "con mas de 20 %; A-2-6, A-2-7, A-5, A-6. La nota 2 de la Tabla "
          "12.12.3.5-1 (pag. 12-81): el sufijo es el % de la densidad maxima "
          "de AASHTO T 99 (Proctor Estandar)."),
)

AASHTO_12_12_3_2 = _cita(
    id="AASHTO_LRFD_9.12.12.3.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.2",
    titulo_numeral="12.12.3.2—Section Properties",
    pagina_impresa="12-76",
    pagina_pdf=1714,
    pagina_pdf_titulo=1713,
    texto_literal=Verbatim(
        texto=("be determined from cut sections of pipe or obtained from the "
               "pipe manufacturer."),
        pagina_pdf=1714),
    caracter=Caracter.RECOMENDACION,
    sesion=T5,
    nota=("La frase empieza al pie de la pag. 12-75 (PDF 1713): «Section "
          "properties for thermoplastic pipe, including wall area, moment of "
          "inertia, and profile geometry should», y termina en la 12-76. El "
          "verbo es «should»: RECOMENDACION. El titulo del numeral esta en la "
          "PDF 1713."),
)

AASHTO_C12_12_3_2 = _cita(
    id="AASHTO_LRFD_9.C12.12.3.2",
    fuente_id="AASHTO_LRFD_9",
    numeral="C12.12.3.2",
    titulo_numeral="C12.12.3.2",
    pagina_impresa="12-76",
    pagina_pdf=1714,
    pagina_pdf_titulo=1713,
    texto_literal=Verbatim(
        texto=("have been minimum values and are not meaningful for design."),
        pagina_pdf=1714),
    caracter=Caracter.DEFINICION,
    sesion=T5,
    nota=("Comentario. La frase empieza en la pag. 12-75: «Historically, "
          "AASHTO bridge specifications have contained minimum values for "
          "the moment of inertia and wall area of thermoplastic pipe; "
          "however, these values», y sigue en la 12-76: «... Thus, there is "
          "no way to provide meaningful generic information on section "
          "properties.» Son los minimos de la Tabla A12-11: con ellos el "
          "resultado es una COTA INFERIOR, no un veredicto sobre un producto "
          "(`M8.cota_inferior_hdpe`)."),
)

AASHTO_12_12_3_3_PANDEO = _cita(
    id="AASHTO_LRFD_9.12.12.3.3#PANDEO",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.3",
    titulo_numeral="12.12.3.3—Chemical and Mechanical",
    pagina_impresa="12-76",
    pagina_pdf=1714,
    texto_literal=Verbatim(
        texto=("Investigation of general buckling shall be based on the value "
               "of modulus of elasticity that represents the design life of "
               "the project."),
        pagina_pdf=1714),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("La frase anterior deja al Ingeniero la eleccion entre propiedades "
          "iniciales y de largo plazo «Except for buckling». Es lo que manda "
          "el pandeo general del HDPE: TODO con el modulo de la vida de "
          "diseño (50 o 75 años), tambien la parte de la carga viva. La FASE "
          "A de T-5 sumaba el pandeo por duracion (la carga viva con el "
          "modulo inicial) y no citaba esta frase."),
)

AASHTO_12_12_3_6 = _cita(
    id="AASHTO_LRFD_9.12.12.3.6",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.12.3.6",
    titulo_numeral="12.12.3.6—Handling and Installation",
    pagina_impresa="12-82",
    pagina_pdf=1720,
    texto_literal=Verbatim(
        texto=("The flexibility factor, FF, shall be limited as specified in "
               "Article 12.5.6.3."),
        pagina_pdf=1720),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("Eq. 12.12.3.6-1: FF = S^2/(E I), con I el momento de inercia "
          "(in4/in), E el modulo de elasticidad INICIAL (ksi) y S el "
          "«diameter of pipe» (in). La norma no dice que diametro: el "
          "proyecto toma el EXTERIOR, que da el FF mayor."),
)

AASHTO_12_5_6_3 = _cita(
    id="AASHTO_LRFD_9.12.5.6.3",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.5.6.3",
    titulo_numeral="12.5.6.3—Thermoplastic and Fiberglass Pipe",
    pagina_impresa="12-14",
    pagina_pdf=1652,
    texto_literal=Verbatim(
        texto=("Flexibility factor, FF, of thermoplastic and fiberglass pipe "
               "shall not exceed 95.0 in./kip."),
        pagina_pdf=1652),
    caracter=Caracter.EXIGENCIA,
    sesion=T5,
    nota=("95.0 in/kip = 0.5425 mm/N. Vista de calculo: "
          "FF_LIMITE_TERMOPLASTICO_MM_N."),
)

AASHTO_M170M_T1_DIAMETROS = _cita(
    id="AASHTO_M170M.T1#DIAMETROS",
    fuente_id="AASHTO_M170M",
    numeral="Table 1",
    titulo_numeral="Design Requirements for Class I Reinforced Concrete Pipe",
    pagina_impresa="M 170M-3",
    pagina_pdf=3,
    texto_literal=Verbatim(texto="1500", pagina_pdf=3),
    caracter=Caracter.DEFINICION,
    metodo=IMAGEN,
    sesion=T5,
    nota=("LEIDO POR IMAGEN. La primera fila de la Tabla 1 (Clase I) es la de "
          "1500 mm: la norma no tabula la Clase I por debajo. Las Tablas 2 a "
          "5 (Clases II a V; PDF 4, 6, 8 y 10) empiezan en 300 mm. Vista de "
          "calculo: DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM. El ultimo "
          "diametro con diseño estandar de cada clase NO se transcribe: solo "
          "se lee con seguridad en las Clases I y II (2700 mm) y V (1800 mm, "
          "pared C); por encima la norma remite al diseño especial de su "
          "num. 7.2, y el tope de 2700 mm del catalogo de concreto lo fija "
          "DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM."),
)


# --- T-3 --- (cadena T) · Familia C: el marco de concreto se dimensiona
# ===========================================================================
# Mismo regimen que T-0, T-2 y T-8: la propia sesion abrio cada pagina por su
# capa de texto y la firma lo dice. Cuatro citas de la FASE A, y ninguna presta
# un NUMERO al marco por su cuenta: dos sostienen el valor de un criterio [A]
# POR ANALOGIA (el espesor del marco y la tolerancia de VC2) y lo dicen en su
# nota; una es la regla de separacion de las alcantarillas multiples, que el
# Manual escribe para TUBERIAS; y la cuarta es la tolerancia de la
# excavacion, el extremo alto de la ventana de VC2. Y DOS DE LAS CORRECCIONES
# DE LA AUDITORIA (H1 y H5), que si son del marco: el n del cajon vaciado in
# situ del HDS-5 (num. B.3) y la regla de AASHTO para el cajon SIN cobertura
# (num. 12.6.6.3, tras la tabla).
FECHA_TESIS_T3 = "2026-11-12"
POR_TESIS_T3 = "tesis/T-3 · lectura directa de la pagina por la sesion"
TESIS_T3 = (FECHA_TESIS_T3, POR_TESIS_T3)

MC_HHD_SEPARACION_MULTIPLES = _cita(
    id="MC_HHD.4.1.1.3.4a#SEPARACION",
    fuente_id="MC_HHD",
    numeral="4.1.1.3.4 a)",
    titulo_numeral="a)  Tipo y sección",
    jerarquia_numeral=("4.1.1.3.4  Elección del tipo de alcantarilla",),
    pagina_impresa="72",
    pagina_pdf=75,
    pagina_pdf_titulo=74,
    texto_literal=Verbatim(
        texto=("En el caso del proceso constructivo de tuberías para "
               "alcantarillas múltiples, se recomienda que la separación de "
               "los tubos, medida entre las superficies externas, deberá ser "
               "tal que facilite la compactación del material de relleno "
               "igual a la mitad del diámetro de la tubería con un máximo de "
               "1.0 m y 0.4 m como mínimo."),
        pagina_pdf=75),
    # RECOMENDACION: «se recomienda que». El «deberá ser tal que facilite la
    # compactacion» de la misma oracion recae sobre la RAZON de la regla, no
    # cambia su caracter.
    caracter=Caracter.RECOMENDACION,
    sesion=TESIS_T3,
    nota=("LA REGLA ES DE TUBERIAS y su razon es la COMPACTACION DEL RELLENO "
          "entre tubos: «medida entre las superficies externas», «que "
          "facilite la compactación del material de relleno». Un marco "
          "multicelda VACIADO IN SITU (§14.1 de docs/ruta_familia_c.md) es "
          "monolitico: sus celdas comparten tabique y entre ellas no hay "
          "relleno que compactar, de modo que la separacion entre celdas es "
          "el espesor del tabique y esta regla no la fija. Se cita en V6 "
          "(T-3) como la regla que aplicaria si las celdas fueran barriles "
          "independientes con relleno entre ellos: D/2, con 0.40 m <= s <= "
          "1.00 m."),
)

E060_14_5_3_2 = _cita(
    id="E060.14.5.3.2",
    fuente_id="E060",
    numeral="14.5.3.2",
    titulo_numeral=("Espesor mínimo de muros diseñados por el método "
                    "empírico de diseño"),
    jerarquia_numeral=("14.5", "MÉTODO EMPÍRICO DE DISEÑO PARA MUROS DE "
                               "CARGA"),
    pagina_impresa="134",
    pagina_pdf=134,
    texto_literal=Verbatim(
        texto=("El espesor de los muros exteriores de sótanos y cimentaciones "
               "no debe ser menor que 200 mm."),
        pagina_pdf=134),
    caracter=Caracter.EXIGENCIA,
    sesion=TESIS_T3,
    nota=("EXIGENCIA DENTRO DE SU AMBITO, que no es el del marco: el 14.5.3 "
          "fija el espesor minimo de los muros diseñados por el METODO "
          "EMPIRICO de 14.5, y la pared de un marco enterrado se diseña por "
          "flexion y carga axial (14.8.1 remite al Capitulo 10). Lo que la "
          "hace la fuente mas cercana para el espesor de un marco a nivel de "
          "perfil es su OBJETO: un muro exterior ENTERRADO, con suelo contra "
          "una cara, que es lo que es la pared del cajon. El proyecto la "
          "aplica POR ANALOGIA como piso del criterio [A] "
          "'espesor_pared_cajon'; no es [N] para el marco. Leida en la capa "
          "de texto de la pagina 134 (que imprime «los  muros  exteriores» "
          "con doble espacio)."),
)

EG2013_503_11_COTAS = _cita(
    id="EG2013.503.11g#COTAS",
    fuente_id="EG2013",
    numeral="503.11 g) 2.",
    titulo_numeral="Calidad del trabajo terminado",
    jerarquia_numeral=("503.11 Criterios",),
    pagina_impresa="934",
    pagina_pdf=942,
    pagina_pdf_titulo=942,
    texto_literal=Verbatim(
        texto="Cotas superiores de placas y veredas: -10 mm a +10 mm.",
        pagina_pdf=942),
    caracter=Caracter.EXIGENCIA,
    sesion=TESIS_T3,
    nota=("Es una tolerancia de ACEPTACION de la obra terminada (503.11, "
          "«Aceptación de los trabajos»), bajo el rotulo «2. Otras "
          "tolerancias» de g. «Calidad del trabajo terminado», junto a "
          "«Espesores de placas: -10 mm a +20 mm». La cota superior de la "
          "placa de FONDO de un marco es su invert: el proyecto la toma POR "
          "ANALOGIA como el desajuste que admite el empalme de la salida "
          "con el fondo del canal (VC2, criterio [A] "
          "'desajuste_empalme_canal_m'). La fuente no habla de empalmes ni "
          "de canales."),
)

EG2013_501_07 = _cita(
    id="EG2013.501.07",
    fuente_id="EG2013",
    numeral="501.07",
    titulo_numeral="Tolerancias",
    pagina_impresa="889",
    pagina_pdf=897,
    pagina_pdf_titulo=897,
    texto_literal=Verbatim(
        texto=("En ningún punto la excavación realizada variará de la "
               "proyectada más de 2 cm en cota, ni más de 5 cm en la "
               "localización en planta."),
        pagina_pdf=897),
    caracter=Caracter.EXIGENCIA,
    sesion=TESIS_T3,
    nota=("Seccion 501, excavacion para estructuras. Es el extremo ALTO de la "
          "ventana del criterio [A] 'desajuste_empalme_canal_m': la cota de "
          "la excavacion que recibe la losa de fondo admite 2 cm. Tampoco "
          "habla de empalmes: es analogia declarada."),
)

# --- T-3 (auditoria adversarial) --- Las dos citas que la auditoria pidio y
# que la sesion de cierre leyo en su pagina, por texto y renderizada.
HDS5_B3_CAJON_IN_SITU = _cita(
    id="HDS5_3ED.B.3#CAJON_IN_SITU",
    fuente_id="HDS5_3ED",
    numeral="B.3",
    titulo_numeral="CONCRETE BOX CULVERT",
    pagina_impresa="B.2",
    pagina_pdf=204,
    pagina_pdf_titulo=204,
    texto_literal=Verbatim(
        texto=("For cast-in-place boxes, the quality of the formwork, "
               "construction practices, and aging are factors. Manning's n "
               "values for cast-in-place boxes range from 0.012 to 0.022 see "
               "concrete lined open channels from HDS 3 Table 1 (FHWA 1961)."),
        pagina_pdf=204),
    caracter=Caracter.DEFINICION,
    metodo=AMBOS,
    sesion=TESIS_T3,
    nota=("La pagina imprime «0.022  see concrete lined open channels  from» "
          "con DOS espacios a cada lado y sin parentesis (comprobado "
          "renderizada); el texto va como la capa de texto lo entrega, con "
          "los espacios normalizados. DESCRIBE el rango del cajon VACIADO IN "
          "SITU y lo liga a la calidad del ENCOFRADO, no a un acabado: es la "
          "ventana HACIA ARRIBA del n de capacidad del criterio "
          "'n_manning_cajon' [C], cuyo valor de archivo es la fila «Concrete "
          "Boxes / Smooth» de la Tabla B.1 (0.012-0.015, pag. impresa B.6). "
          "Remite a la Tabla 1 del HDS 3 (FHWA 1961), que no esta en normas/."),
)

AASHTO_12_6_6_3_SIN_COBERTURA = _cita(
    id="AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA",
    fuente_id="AASHTO_LRFD_9",
    numeral="12.6.6.3",
    titulo_numeral="Minimum Cover",
    pagina_impresa="12-22",
    pagina_pdf=1660,
    pagina_pdf_titulo=1659,
    texto_literal=Verbatim(
        texto=("If soil cover is not provided, the top of precast or "
               "cast-in-place reinforced concrete box structures shall be "
               "designed for direct application of vehicular loads."),
        pagina_pdf=1660),
    caracter=Caracter.EXIGENCIA,
    metodo=AMBOS,
    sesion=TESIS_T3,
    nota=("Es la UNICA regla de la Sec. 12 sobre la cobertura de un CAJON de "
          "concreto, y esta en el articulado 12.6.6.3, debajo de la Tabla "
          "12.6.6.3-1 (que no tiene fila de cajon de concreto: "
          "`AfirmacionNegativa` SIN_CAJON_DE_CONCRETO_T12663). No fija una "
          "cobertura minima: ADMITE el cajon sin cobertura y a cambio exige "
          "diseñar la losa superior para la carga vehicular directa. Junto con "
          "el num. 4.1.1.3.4 a) del Manual (`MC_HHD.4.1.1.3.4a#NIVELES`: la "
          "rasante puede coincidir con la losa) y la Lamina N 03 (que dibuja "
          "el marco en cruce de canal sin relleno acotado), sostiene que el "
          "piso de 0.3048 m del criterio 'cobertura_minima_cajon' [A] es MAS "
          "RESTRICTIVO que la fuente: por eso G1 del marco AVISA y no bloquea "
          "cuando solo falta esa cobertura (auditoria de T-3, H5)."),
)

CITAS: Dict[str, Cita] = {c.id: c for c in _TODAS}
