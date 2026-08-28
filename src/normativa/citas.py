"""
Las citas del proyecto, una por objeto y con id estable (D1).

TODAS las que llevan `verificado` pasaron por el subagente
`verificador-normativo` en la sesion S12, contra el PDF cuyo sha1 declara la
`Fuente`. Ninguna se acepto sin ese paso, y ninguna pagina se calculo a ojo
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
    PorDatoDeSitio,
    PorExpresion,
    Verbatim,
    Verificado,
)

FECHA_S12 = "2026-08-28"
POR_S12 = "fase1/S12 · verificador-normativo"

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
             metodo: MetodoDeVerificacion = MetodoDeVerificacion.TEXTO
             ) -> Verificado:
    return Verificado(fecha=FECHA_S12, por=POR_S12,
                      sha1_pdf=_SHA[fuente_id], metodo=metodo)


def _cita(*, verificada: bool = True,
          metodo: MetodoDeVerificacion = MetodoDeVerificacion.TEXTO,
          **kw) -> Cita:
    if verificada:
        kw["verificado"] = _firmado(kw["fuente_id"], metodo)
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
