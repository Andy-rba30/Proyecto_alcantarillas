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
    Fundamento,
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

# La firma va por SESION, no por archivo: una cita dice contra que lectura se
# comprobo, y dos lecturas distintas del mismo PDF son dos hechos distintos.
S12 = (FECHA_S12, POR_S12)
S13 = (FECHA_S13, POR_S13)

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
          "1.93. Como `caudal_adimensional` multiplica por KU_METRICO = "
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
    nota=("ERRATA DE LA PROPIA FUENTE, hallada al verificar: el titulo dice "
          "«for Charts in Appendix G» y en esta 3a edicion NO EXISTE un "
          "Apendice G -- las cartas estan en el Apendice C. Se transcribe "
          "como lo imprime, con la advertencia, para que quien lo busque lo "
          "encuentre."),
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

HDS5_3_3_3 = _cita(
    id="HDS5_3ED.3.3.3#HO",
    fuente_id="HDS5_3ED",
    numeral="3.3.3",
    titulo_numeral="Outlet Control",
    pagina_impresa="3.24",
    pagina_pdf=106,
    texto_literal=Verbatim(
        texto=("Approximate hydraulic gradeline ho = (dc + D)/2 can only be "
               "used if the barrel flows full for"),
        pagina_pdf=106),
    caracter=Caracter.APROXIMACION,
    nota=("Las TRES condiciones estan en esta pagina, y la primera tiene una "
          "SEGUNDA MITAD que el expediente no recogia: «It should not be used "
          "if the inlet is not submerged». Son dos condiciones, no una. "
          "Ademas la fuente no escribe la razon HW/D: escribe «the headwater "
          "depth (referenced to the inlet invert) is less than 1.2D», y la "
          "referencia al invert de entrada es parte de la definicion. Las "
          "tres son `should` / `can only`, no `shall`."),
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
          "cita mal por tres sitios -- ver DIS-HR-CLASE-DE-SITIO-F --, "
          "mientras que constantes_normativas.E030_S5_TEXTO la transcribe "
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
# Fundamentos (§3.10). Se pueblan aqui los que el registro ya puede sostener;
# la carga completa es trabajo de S18 y la decision abierta #4 del diseño.
# ===========================================================================

FUNDAMENTOS: Dict[str, Fundamento] = {}


def _fundamento(**kw) -> Fundamento:
    f = Fundamento(**kw)
    FUNDAMENTOS[f.id] = f
    return f


CITAS: Dict[str, Cita] = {c.id: c for c in _TODAS}

AFIRMACIONES_NEGATIVAS = (SIN_HDPE_T09, SIN_TMC_NI_HDPE_T10,
                          SIN_TABLAS_HEQ_EN_MP)
