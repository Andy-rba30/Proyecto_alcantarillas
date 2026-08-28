"""
Las discrepancias declaradas del expediente.

POR QUE ESTE MODULO EXISTE. `CLAUDE.md` obliga, cuando la fuente primaria gana
a la hoja de ruta, a hacer TRES cosas: declararlo en el punto de uso, reportar
el defecto contra la hoja de ruta, y dejar dicho que LA HOJA DE RUTA SIGUE MAL
mientras no se corrija. Las dos primeras se venian cumpliendo en prosa, en
bloques de comentario de `constantes_normativas.py`. La tercera no tenia donde
vivir: una obligacion que solo existe en un comentario no es enumerable, no es
imprimible y no es testeable, de modo que dependia de que alguien se acordara.

Aqui son objetos. Un test lista las `ABIERTA_CONTRA_HOJA_DE_RUTA` (T20) y M11
las imprime. Los comentarios de `constantes_normativas.py` no se borran -- son
el punto de uso, que es la primera de las tres obligaciones -- pero dejan de
ser el UNICO sitio donde vive la tercera.
"""

from __future__ import annotations

from typing import Dict

from .esquema import Discrepancia, EstadoDiscrepancia, Parte

_TODAS = []


def _d(**kw) -> Discrepancia:
    d = Discrepancia(**kw)
    _TODAS.append(d)
    return d


# ---------------------------------------------------------------------------
# Las dos ediciones de HDS-5 que conviven en normas/
# ---------------------------------------------------------------------------
DIS_HDS5_EDICIONES = _d(
    id="DIS-HDS5-EDICIONES",
    objeto="la constante K del termino de friccion del control de salida",
    partes=(
        Parte(quien="HDS5_3ED",
              que_dice="«KU = 29 in English Units (19.63 in SI)»",
              cita_id="HDS5_3ED.3.1.4#K"),
        Parte(quien="HDS5_SI_1985",
              que_dice=("imprime 29 en sus ecs. (4b) y (5) con rotulos duales "
                        "«ft (m)» y NO imprime 19.63, pese al «si» del nombre "
                        "del archivo"),
              cita_id="HDS5_SI_1985.EC4B#K"),
    ),
    gana="HDS5_3ED",
    por_que=("es la unica de las dos que publica la conversion SI. La copia de "
             "1985 opera en unidades inglesas con rotulos duales, y el «si» de "
             "su nombre de archivo se refiere a sus cartas metricas, no al "
             "cuerpo del documento"),
    efecto_si_se_sigue_la_otra=("aplicar 29 en metrico sobrestima el termino "
                                "de friccion un +9.6 %, y no falla "
                                "ruidosamente: devuelve numeros plausibles y "
                                "equivocados"),
    estado=EstadoDiscrepancia.RESUELTA,
)

# ---------------------------------------------------------------------------
# Las TRES erratas de imprenta de la cadena sismica del Manual de Puentes
# ---------------------------------------------------------------------------
DIS_KAE_SIGNO = _d(
    id="DIS-MP-KAE-SIGNO",
    objeto="el signo del denominador de K_AE (Mononobe-Okabe)",
    partes=(
        Parte(quien="MP",
              que_dice=("imprime «[1 - raiz(...)]», signo MENOS, verificado "
                        "renderizando la pag. impresa 586 a 6x: el trazo es "
                        "horizontal unico, sin trazo vertical"),
              cita_id="MP.A.11.3.1#KAE"),
        Parte(quien="AASHTO_LRFD_9",
              que_dice="imprime «[1 + raiz(...)]»",
              cita_id="AASHTO_LRFD_9.A11.3.1#KAE"),
    ),
    gana="AASHTO_LRFD_9",
    por_que=("no por preferencia de fuente: con el signo menos K_AE DIVERGE "
             "cuando el radicando tiende a 1, y el caso limite k_h = k_v = 0 "
             "deja de devolver el Ka de Coulomb. La formula se rompe donde el "
             "propio Manual la manda coincidir, y el Manual declara "
             "transcribirla de AASHTO"),
    efecto_si_se_sigue_la_otra=("K_AE diverge; quien «corrija» M9 contra la "
                                "letra impresa del Manual rompe la formula"),
    estado=EstadoDiscrepancia.ERRATA_DE_IMPRENTA,
)

DIS_KH0_ROCA = _d(
    id="DIS-MP-KH0-ROCA",
    objeto="el lado del 1.2 en la clausula de roca de k_h0",
    partes=(
        Parte(quien="MP",
              que_dice=("el parentesis imprime «1.2 kh0=FpgaPGA», con el 1.2 "
                        "del lado izquierdo; leido al pie de la letra daria "
                        "k_h0 = F_pga*PGA/1.2. La PROSA de la misma frase dice "
                        "lo contrario"),
              cita_id="MP.2.8.1.1.14.2.1#ROCA"),
        Parte(quien="AASHTO_LRFD_9",
              que_dice=("«k_h0 shall be based on 1.2 times the site-adjusted "
                        "peak ground acceleration coefficient (i.e., k_h0 = "
                        "1.2 F_pga PGA)»"),
              cita_id="AASHTO_LRFD_9.11.6.5.2.1#ROCA"),
    ),
    gana="AASHTO_LRFD_9",
    por_que=("gana la PROSA del Manual, que coincide con AASHTO; el "
             "parentesis esta mal compuesto"),
    efecto_si_se_sigue_la_otra=("una REDUCCION del 17 % de k_h0, justo lo "
                                "contrario de lo que la prosa de la misma "
                                "frase acaba de decir"),
    estado=EstadoDiscrepancia.ERRATA_DE_IMPRENTA,
)

DIS_EXCENTRICIDAD_TERCIO = _d(
    id="DIS-MP-EXCENTRICIDAD",
    objeto="el limite de excentricidad sismica para gamma_EQ = 0.0",
    partes=(
        Parte(quien="MP",
              que_dice=("traduce el «middle two-thirds» de AASHTO como «tercio "
                        "central», que no es lo mismo: dos tercios centrales "
                        "es e <= B/3 y el tercio central es e <= B/6"),
              cita_id="MP.2.8.1.1.14.1#EXC"),
        Parte(quien="AASHTO_LRFD_9",
              que_dice=("«within the middle two-thirds of the base for "
                        "gamma_EQ = 0.0»"),
              cita_id="AASHTO_LRFD_9.11.6.5.1#EXC"),
    ),
    gana="AASHTO_LRFD_9",
    por_que=("es descuido de traduccion y no decision del MTC, y lo prueba el "
             "propio Manual: tres paginas antes traduce el MISMO giro "
             "correctamente en su numeral ESTATICO, y en el mismo parrafo "
             "sismico traduce bien «eight-tenths». Solo degrada «two-thirds», "
             "y solo ahi. Ademas la lectura literal es normativamente "
             "imposible: dejaria el limite bajo SISMO al doble de estricto "
             "que bajo carga estatica permanente, invirtiendo la filosofia de "
             "estados limite"),
    efecto_si_se_sigue_la_otra=("e <= B/6 en vez de B/3: rechazaria diseños "
                                "que la norma acepta. Es conservador, y por "
                                "eso no cambia ningun resultado ya emitido, "
                                "pero deja la cita sin sostener"),
    estado=EstadoDiscrepancia.ERRATA_DE_IMPRENTA,
)

DIS_NUMERAL_EXC_ESTATICA = _d(
    id="DIS-MP-NUMERAL-2.3.1.1.12.3",
    objeto="el numeral impreso de «Limites de Excentricidad»",
    partes=(
        Parte(quien="MP",
              que_dice=("lo imprime «2.3.1.1.12.3», con un 3 donde toca un 8, "
                        "rompiendo la serie 2.8.1.1.12.2 -> 2.8.1.1.12.5; el "
                        "indice repite la errata"),
              cita_id="MP.2.3.1.1.12.3#EXC_ESTATICA"),
        Parte(quien="AASHTO_LRFD_9",
              que_dice="la remision cruzada del propio Manual (11.6.3.3) si es correcta",
              cita_id="AASHTO_LRFD_9.11.6.3.3#EXC"),
    ),
    gana="MP",
    por_que=("se cita COMO LO IMPRIME, con la advertencia, para que quien lo "
             "busque lo encuentre. Corregir el numeral en la cita mandaria al "
             "revisor a un renglon que el documento no tiene"),
    efecto_si_se_sigue_la_otra=("citar «2.8.1.1.12.3» manda a un numeral que "
                                "el Manual no imprime"),
    estado=EstadoDiscrepancia.ERRATA_DE_IMPRENTA,
)

# ---------------------------------------------------------------------------
# Las discrepancias ABIERTAS contra la hoja de ruta v8
# ---------------------------------------------------------------------------
DIS_D_MAX = _d(
    id="DIS-HR-D-MAX",
    objeto="los topes de diametro por material (2.70 / 2.10 / 1.50 m)",
    partes=(
        Parte(quien="hoja_de_ruta",
              que_dice=("su Anexo B los declara bajo el rotulo «topes por "
                        "norma de producto - VERIFICAR», atribuidos a ASTM C76 "
                        "/ AASHTO M170, AASHTO M36 / ASTM A760 y AASHTO M294")),
        Parte(quien="ASTM_A760",
              que_dice=("su Tabla 1 tabula diametros nominales de 100 mm (4 in) "
                        "a 3600 mm (144 in): los 2100 mm son una fila mas de la "
                        "serie, no un maximo"),
              cita_id="ASTM_A760.T1#DIAMETROS"),
        Parte(quien="AASHTO_M170M",
              que_dice=("sus Tablas 1 a 5 (Clases I a V) van de 300 a 3600 mm, "
                        "y la Seccion 7.2 preve diseños especiales por encima "
                        "de lo tabulado"),
              cita_id="AASHTO_M170M.T1_T5#DIAMETROS"),
    ),
    gana="ASTM_A760",
    por_que=("la fuente primaria, leida de los PDF de normas/, desmiente las "
             "dos atribuciones contrastables. No son topes normativos: son "
             "topes de CATALOGO, y como tales descartaban material en silencio "
             "con una cita que ninguna norma sostiene. AASHTO M294 no esta en "
             "normas/ y el tope del HDPE no se pudo contrastar"),
    efecto_si_se_sigue_la_otra=("un punto que necesite mas de 2.10 m de TMC se "
                                "declara no factible por una razon que la "
                                "norma citada no sostiene"),
    estado=EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
)

DIS_CICLOPEO = _d(
    id="DIS-HR-CICLOPEO",
    objeto="el f'c minimo de la matriz del concreto ciclopeo",
    partes=(
        Parte(quien="hoja_de_ruta",
              que_dice=("su Sec. 9.4 pide f'c de matriz >= 10 MPa citando solo "
                        "el Art. 22.10 de E.060")),
        Parte(quien="EG2013",
              que_dice=("la Clase G de la Tabla 503-07 -- concreto ciclopeo -- "
                        "pide 14 MPa, y la Seccion 503 es la que este proyecto "
                        "cita para los cabezales"),
              cita_id="EG2013.503.04#T503_07"),
    ),
    gana="EG2013",
    por_que=("sobre el MISMO material rigen las dos normas y por la regla del "
             "mayor de Sec. 0.2 gobierna la mayor. La hoja de ruta mira solo a "
             "E.060 y no ve que sobre el mismo material rige tambien la norma "
             "vial del MTC"),
    efecto_si_se_sigue_la_otra=("quien lea la hoja de ruta sin leer el codigo "
                                "dimensionara un cabezal de ciclopeo con una "
                                "matriz de 10 MPa que este calculo va a "
                                "rechazar"),
    estado=EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
)

DIS_A807 = _d(
    id="DIS-HR-A807",
    objeto="la norma que fija el calibre de la plancha de TMC por altura de relleno",
    partes=(
        Parte(quien="hoja_de_ruta",
              que_dice=("lo remite a «ASTM A-807» en su Sec. 7.A, en su Fase 8 "
                        "y en su Anexo B")),
        Parte(quien="ASTM_A796",
              que_dice=("el calibre por altura de cobertura es de ASTM "
                        "A796/A796M, no de A-807")),
    ),
    gana="ASTM_A796",
    por_que=("la remision de la hoja de ruta es falsa. A-807 no es la norma "
             "que se le atribuye"),
    efecto_si_se_sigue_la_otra=("se busca el calibre en un documento que no lo "
                                "tiene, y la busqueda termina en un vacio "
                                "aparente que no es tal"),
    estado=EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
)

DIS_H_RELLENO_MIN = _d(
    id="DIS-HR-H-RELLENO-MIN",
    objeto="la altura minima de relleno sobre la clave para concreto y TMC",
    partes=(
        Parte(quien="hoja_de_ruta",
              que_dice=("su Sec. 7.A dice «No fijado. Remite al Proyecto, "
                        "AASHTO M-170M (clases I-V) o ASTM A-807»")),
        Parte(quien="AASHTO_LRFD_9",
              que_dice=("el Art. 12.6.6.3 y la Tabla 12.6.6.3-1 tabulan la "
                        "cobertura minima para los tres tipos de conducto del "
                        "catalogo"),
              cita_id="AASHTO_LRFD_9.12.6.6.3#COBERTURA"),
    ),
    gana="AASHTO_LRFD_9",
    por_que=("«no fijado» ya no es cierto: lo fija AASHTO LRFD, que el propio "
             "Sec. 0.2 adopta de extremo a extremo, y las dos remisiones de la "
             "hoja son falsas (M 170M no da alturas de relleno y A-807 no es "
             "la norma que se le atribuye). Declarar un vacio sobre la fuente "
             "que SI trae el dato es el defecto que Sec. 0.5 llama el mas "
             "grave"),
    efecto_si_se_sigue_la_otra=("se declara vacio lo que la norma adoptada "
                                "tabula, y la cobertura minima queda sin piso"),
    estado=EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
)

DIS_G_LAUSHEY = _d(
    id="DIS-HR-G-LAUSHEY",
    objeto="la atribucion del valor g = 9.8 m/s2 al num. 4.1.1.3.7 c)",
    partes=(
        Parte(quien="hoja_de_ruta",
              que_dice=("escribe «d50 en m, V en m/s, g = 9.8 m/s2» bajo el "
                        "encabezado «Laushey — num. 4.1.1.3.7 c), pag. 80», "
                        "presentando el 9.8 como si el numeral lo imprimiera")),
        Parte(quien="MC_HHD",
              que_dice=("el num. 4.1.1.3.7 c), pag. impresa 80, define g SIN "
                        "numero: «g : Aceleracion de la gravedad (m/s2)». El "
                        "9.8 SI esta en el Manual, pero en otros dos numerales "
                        "-- el 3.12.5 (pag. impresa 63) y el 4.1.1.5.4 b.2.4) "
                        "(pag. impresa 111) --, y el 9.81 no aparece ni una vez"),
              cita_id="MC_HHD.4.1.1.3.7c#G"),
    ),
    gana="MC_HHD",
    por_que=("verificado contra el PDF barriendo las 225 paginas: «9.8» como "
             "valor de la gravedad aparece en dos paginas, ninguna de ellas la "
             "80. EL NUMERO ES DEFENDIBLE Y LA CITA NO LO ERA: es el mismo "
             "genero de defecto que el proyecto purgo con el «19.62 = 2g». Se "
             "corrige la atribucion, no el numero"),
    efecto_si_se_sigue_la_otra=("un revisor que abra la pag. 80 buscando el 9.8 "
                                "no lo encuentra, y una cita que no se puede "
                                "comprobar es indistinguible de una inventada"),
    estado=EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
)

DIS_H_EQ = _d(
    id="DIS-HR-H-EQ",
    objeto="la altura de suelo equivalente de la sobrecarga de trafico (h_eq)",
    partes=(
        Parte(quien="hoja_de_ruta",
              que_dice=("«Sobrecarga en el trasdos (num. 2.1.4.3.9, pag. 91): "
                        "... se añade sobrecarga vertical >= 0.60 m de relleno "
                        "equivalente ... En un cabezal bajo terraplen vial "
                        "SIEMPRE APLICA». Dos defectos en una frase: el "
                        "numeral es «Aparatos de Apoyo» y el «siempre aplica» "
                        "borra la condicion de distancia que la fuente pone")),
        Parte(quien="MP",
              que_dice=("el num. 2.1.4.3.9 se titula «Aparatos de Apoyo» y no "
                        "contiene ni la palabra sobrecarga ni el 0.60. El "
                        "texto real esta en el num. 2.4.2.2 «Cargas de Suelo: "
                        "EH, ES, y DD», pag. impresa 102, y es CONDICIONAL: "
                        "«Cuando se prevea trafico a una distancia horizontal, "
                        "medida desde la parte superior de la estructura, "
                        "menor o igual a la mitad de su altura...», con "
                        "exencion expresa si hay losa de aproximacion"),
              cita_id="MP.2.4.2.2#SOBRECARGA"),
        Parte(quien="AASHTO_LRFD_9",
              que_dice=("el Art. 3.11.6.4 tabula h_eq por altura del muro, y "
                        "para 2.0 m con trafico perpendicular da 1.12 m por "
                        "interpolacion obligatoria. El Manual de Puentes NO "
                        "transcribe esas tablas: su traduccion de la Sec. 3.11 "
                        "se corta en el empuje pasivo k_p"),
              cita_id="AASHTO_LRFD_9.3.11.6.4#LS"),
    ),
    gana="AASHTO_LRFD_9",
    por_que=("por la Via 1 de Sec. 0.2 (AASHTO LRFD de extremo a extremo) y "
             "por la regla del mayor: el Manual fija un PISO («no menor que la "
             "equivalente a 0.60 m») y AASHTO tabula el valor. Los dos rigen, "
             "y h_eq es el mayor de los dos. El 0.60 plano no es defendible "
             "para un cabezal de 2 m con trafico perpendicular"),
    efecto_si_se_sigue_la_otra=("con h_eq = 0.60 m fijo, un cabezal de 2.0 m "
                                "con trafico perpendicular subestima la "
                                "sobrecarga viva en un factor 1.87, y con "
                                "gamma_LS = 1.75 eso llega al empuje de diseño"),
    estado=EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
)

DIS_CALICATAS = _d(
    id="DIS-CN-CALICATAS",
    objeto="si el Cuadro 4.1 dice cuando son 4 calicatas y cuando 6",
    partes=(
        Parte(quien="codigo",
              que_dice=("el comentario de CALICATAS_POR_SENTIDO afirmaba: «El "
                        "Cuadro admite ademas 6 en vez de 4 para autopistas "
                        "con 4 carriles por sentido, y "
                        "«4 (o 6)» para duales. Ese 6 NO se "
                        "transcribe aqui: el Cuadro lo da como alternativa SIN "
                        "DECIR CUANDO APLICA CADA UNA, de modo que la eleccion "
                        "entre 4 y 6 no es [N]»")),
        Parte(quien="MS",
              que_dice=("el Cuadro 4.1 SI lo condiciona, y por carriles por "
                        "sentido"),
              cita_id="MS.4.2#C41"),
    ),
    gana="MS",
    por_que=("verificado contra el PDF. Afirmar que la fuente calla donde "
             "habla es la forma inversa del mismo defecto que persigue este "
             "cluster: en vez de citar lo que no dice, se niega lo que si dice, "
             "y el resultado es igual de invisible -- un vacio inventado que "
             "convierte en [A] lo que es [N]"),
    efecto_si_se_sigue_la_otra=("la densidad de la campaña geotecnica se "
                                "elegiria como criterio [A] cuando la norma la "
                                "determina, y una autopista de 4 carriles por "
                                "sentido saldria con la mitad de las calicatas "
                                "que el Cuadro exige"),
    estado=EstadoDiscrepancia.RESUELTA,
)

DIS_EG_508_07 = _d(
    id="DIS-CN-EG-508-07",
    objeto="la pagina impresa del relleno minimo de 0,30 m del HDPE",
    partes=(
        Parte(quien="codigo",
              que_dice=("el repositorio cito esa frase primero en la pag. "
                        "impresa 982 y despues en la 984, y las dos citas "
                        "conviven en el expediente")),
        Parte(quien="EG2013",
              que_dice="la pagina impresa que la imprime, verificada",
              cita_id="EG2013.508.07#RELLENO_MIN"),
    ),
    gana="EG2013",
    por_que=("el desfase de este documento es +8 y es el mas grande del "
             "corpus: confundir pagina impresa con pagina PDF produce "
             "exactamente un error de 8, que es la distancia entre las dos "
             "cifras que el repositorio manejaba"),
    efecto_si_se_sigue_la_otra=("la cita mas load-bearing del proyecto -- la "
                                "que llega impresa a la memoria -- manda al "
                                "revisor a una pagina que no dice lo que la "
                                "cita afirma"),
    estado=EstadoDiscrepancia.RESUELTA,
)


DIS_T09_A2_DESPLAZADA = _d(
    id="DIS-MCHHD-T09-A2-DESPLAZADA",
    objeto=("la alineacion de la columna de valores con sus rotulos en el "
            "bloque A.2 NO METALICOS de la Tabla Nº 09"),
    partes=(
        Parte(quien="MC_HHD",
              que_dice=("en la pag. impresa 75 los valores del bloque A.2 se "
                        "imprimen UN RENGLON MAS ARRIBA que sus rotulos: "
                        "«0.010 0.011 0.013» queda a la altura de "
                        "«a. Concreto» y «0.010 0.012 0.014» a la de "
                        "«b. Madera», que son rotulos de categoria sin valores "
                        "propios -- como «b. Acero» y «c. Metal corrugado» del "
                        "bloque A.1, que SI quedan en blanco. Leida al pie de "
                        "la letra, la pagina deja sin valor a «Tubo con "
                        "moldaje madera en bruto» y a «c. Albañilería de "
                        "piedra.», que son hojas de la jerarquia"),
              cita_id="MC_HHD.4.1.1.3.6#T09"),
        Parte(quien="Ven Te Chow 1983",
              que_dice=("la fuente que la propia Tabla Nº 09 declara asigna "
                        "0.010/0.011/0.013 a «culvert, straight and free of "
                        "debris» y 0.010/0.012/0.014 a «wood stave», que son "
                        "«tubo recto y libre de basuras» y «duelas». "
                        "Corriendo un renglon, las diez ternas del bloque "
                        "encajan una a una con las diez hojas, sin sobrar ni "
                        "faltar")),
    ),
    gana="Ven Te Chow 1983",
    por_que=("es un descuido de composicion del bloque A.2 -- el A.1 de la "
             "MISMA tabla no lo tiene --, y la lectura corrida es la unica "
             "que deja a cada hoja con su valor y coincide fila por fila con "
             "la fuente que la tabla se atribuye. HALLAZGO DE S12: el "
             "repositorio ya transcribia la lectura corregida y NO lo "
             "declaraba, de modo que su valor de Manning mas usado "
             "-- MANNING['concreto_tubo_recto'] -- se apoyaba en una lectura "
             "corregida que ningun revisor podia reproducir abriendo la "
             "pagina"),
    efecto_si_se_sigue_la_otra=("MANNING['concreto_tubo_recto'] pasaria de "
                                "(0.010, 0.013) a (0.011, 0.014): +10 % en el "
                                "n minimo, que es el que gobierna V3 y la "
                                "socavacion, y +7.7 % en el maximo, que "
                                "gobierna capacidad y tirante"),
    estado=EstadoDiscrepancia.ERRATA_DE_IMPRENTA,
)


DISCREPANCIAS: Dict[str, Discrepancia] = {d.id: d for d in _TODAS}
