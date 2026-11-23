"""
Fichas de criterios adoptados del dominio: hidraulica.
"""

from typing import Dict
from src.constantes_normativas import (
    BORDE_LIBRE_BADEN_RANGO_M,
    H_O_CONDICION_TEXTO,
    H_O_NUMERAL,
    V_MIN,
    Y_SOBRE_D_MAX,
)
from src.modelos import DeTabla, EnRango, Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_DICT_CON_CAMPOS,
    FORMA_FLOAT,
    FORMA_PAR_ORDENADO,
    FORMA_STR,
    NIVEL_PERFIL,
    REVESTIMIENTOS_CUNETA,
    _N_MANNING_HDPE_HDS5,
    _VENTANA_KE_C2,
)


CRITERIOS: Dict[str, Criterio] = {


    # ----------------------- HIDRAULICA: vacios ---------------------------

    "hds5_embocadura_hdpe": Criterio(
        valor={"K": 0.0098, "M": 2.00, "c": 0.0398, "Y": 0.67, "Ks": -0.5,
               "forma": 1},
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Constantes de control de entrada HDS-5 para tuberia HDPE",
        justificacion="Decide la fila de la Tabla A.1 de HDS-5 de la que se "
                      "toman las constantes de control de entrada (K, M, c, Y "
                      "y Ks) para la tuberia HDPE de interior liso. La fuente "
                      "(Tabla A.1; fila adoptada y verificada, ver `fuente` y "
                      "`resolucion`) se organiza en cartas por forma/material "
                      "y, dentro de cada carta, por configuracion de borde: "
                      "la misma configuracion de borde recto con muro de "
                      "cabecera tiene K = 0.0098 en concreto y K = 0.0078 en "
                      "metal corrugado, y esa diferencia responde al perfil "
                      "de pared en la boca (lisa frente a corrugada), no a la "
                      "friccion del barril. Lo que la tabla no resuelve es el "
                      "HDPE: no lo lista. Se adopta por analogia la fila del "
                      "concreto de borde recto con muro de cabecera, porque "
                      "el HDPE de interior liso cortado a ras del muro "
                      "presenta en la boca pared lisa y borde cuadrado: la "
                      "misma condicion de entrada que el concreto. La "
                      "sensibilidad declara la fila alternativa del metal "
                      "corrugado con muro de cabecera, con sus constantes al "
                      "lado de las adoptadas",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice A, Tabla A.1, "
               "pag. A.8, fila 'Circular Concrete / Square edge w/headwall'. "
               "Los cinco valores confirman contra esa fila y la pagina es la "
               "correcta (verificado por la auditoria normativa, NOR-ANA-03)",
        sensibilidad=("Tabla A.1, fila 'Circular Concrete / Square edge "
                      "w/headwall' (la adoptada): K=0.0098, c=0.0398, Y=0.67",
                      "Tabla A.1, fila 'Circular CM / Headwall' (la "
                      "alternativa): K=0.0078, c=0.0379, Y=0.69"),
        verificacion_pendiente="LA DIRECCION DE LA COMPARACION SE DECLARO AL "
                               "REVES HASTA I1b, COPIADA DE LA FICHA "
                               "NOR-ANA-03, Y SE CORRIGIO MIDIENDOLA con las "
                               "constantes de este mismo criterio y los "
                               "dominios de M4: en los TRES regimenes "
                               "vigentes la fila del concreto adoptada da un "
                               "HW MAYOR o igual que la del metal corrugado. "
                               "No sumergida (q* <= 3.5), manda K: 0.0098 > "
                               "0.0078. Sumergida (q* >= 4.0), HW_i/D = "
                               "c*q*^2 + Y + Ks*S: la diferencia es "
                               "0.0019*q*^2 - 0.02, positiva para q* > 3.245, "
                               "y 3.245 queda FUERA del dominio de esta rama "
                               "-- evaluar ahi la ecuacion sumergida es "
                               "exactamente el error de la ficha, que "
                               "ademas enumera 'c y Y ambos menores' cuando "
                               "0.0398 > 0.0379 --. La transicion es una "
                               "recta entre dos extremos donde el concreto "
                               "ya es mayor. La adopcion es por tanto "
                               "CONSERVADORA EN DIRECCION para V1, V4 y el "
                               "resguardo de 7.A, pero se sostiene en el "
                               "argumento fisico de arriba -- el perfil de "
                               "pared EN LA BOCA, no la friccion del barril "
                               "-- y no en ese margen: son dos cosas "
                               "distintas. El defecto contra la ficha "
                               "NOR-ANA-03 queda reportado en el tracker. Lo "
                               "que sigue pendiente no cambia: el detalle "
                               "constructivo -- confirmar que el tubo enrasa "
                               "en la cara del cabezal con pared interior "
                               "lisa. Si aloja campana, sobresale o el HDPE "
                               "es de interior corrugado, corresponde otra "
                               "fila y la alternativa de la sensibilidad "
                               "pasa a ser la adoptada",
        resolucion=DeTabla(
            tablas=("HDS5_3ED.TA1",),
            fila_id="circular_concreto_square_edge_headwall",
            que_elige="la fila de embocadura de la que se toman K, M, c, Y y "
                      "Ks para el HDPE, por analogia con el concreto de "
                      "borde recto con muro de cabecera",
        ),
    ),

    "metodo_transicion_hds5": Criterio(
        valor="interpolacion_lineal_entre_extremos",
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_STR,
        concepto="Metodo con que se cubre la zona de transicion del control de "
                 "entrada de HDS-5, 3.5 < q* < 4.0",
        justificacion="Decide el metodo con que M4 cubre la zona de "
                      "transicion del control de entrada, 3.5 < q* < 4.0. La "
                      "fuente (HDS-5, num. 3.1.3 y num. A.2; citas literales "
                      "en `fuente`) describe esa zona como mal definida y la "
                      "resuelve trazando una curva empirica tangente a las "
                      "ramas no sumergida y sumergida, sin publicar ecuacion "
                      "cerrada. Lo que no resuelve es el procedimiento "
                      "programable: el empalme de la fuente es grafico. Se "
                      "adopta la recta que Sec. 4.2 de la hoja de ruta "
                      "prescribe -- interpolar linealmente entre la rama no "
                      "sumergida evaluada en q* = 3.5 y la sumergida evaluada "
                      "en q* = 4.0 --. Y «evaluada en q* = 3.5» quiere decir "
                      "evaluada para el CAUDAL que corresponde a q* = 3.5, "
                      "Q_lo = 3.5*A_llena*sqrt(D)/Ku, con el H_c de ESE "
                      "caudal cuando la carta es de Forma 1 (v8 §4.2, "
                      "enmendada en EXT-0; EXT-M-04): con el H_c del caudal "
                      "real el extremo inferior se mueve con q* y la recta "
                      "deja de ser una recta. Los dos extremos son FIJOS "
                      "para un D, una S y una carta dados, y por eso la "
                      "recta lo es. Se declara que esa recta es una "
                      "simplificacion adoptada del empalme de la fuente, no "
                      "una transcripcion de la fuente primaria: por eso es "
                      "[C] y no [N]. La recta empalma continua en los dos "
                      "extremos (coincide con cada rama en su borde de "
                      "validez), lo que deja el error acotado y del orden del "
                      "espesor de la propia curva de la fuente, sin convertir "
                      "la recta en el metodo de la fuente. Alcance: solo "
                      "afecta a los puntos cuyo q* cae dentro de la ventana "
                      "3.5-4.0; fuera de ella rigen las dos ecuaciones tal "
                      "como las escribe la tabla",
        fuente=(
            "HDS-5 (FHWA) 3a ed., abril 2012: num. 3.1.3 'Inlet Control', "
            "pag. impresa 3.4 (PDF 86) -- 'The flow transition zone between "
            "the low headwater (weir control) and the high headwater (orifice "
            "control) flow conditions is poorly defined. This zone is "
            "approximated by plotting the unsubmerged and submerged flow "
            "equations and connecting them with a line tangent to both "
            "curves' -- y num. A.2 'INLET CONTROL EQUATIONS', pag. impresa "
            "A.1 (PDF 190) -- 'The transition zone is defined empirically by "
            "drawing a curve between and tangent to the curves defined by the "
            "unsubmerged and submerged equations'. "
            "NUMERAL CORREGIDO (NOR-HDS-06): esta fuente citaba 'Cap. IV', y "
            "el Capitulo 4 de ESTA 3a edicion se titula 'CULVERT DESIGN FOR "
            "AQUATIC ORGANISM PASSAGE (AOP)' -- paso de fauna acuatica, "
            "biologia de peces y barreras de salto --, que no tiene nada que "
            "ver con la zona de transicion. Es el mismo patron que "
            "NOR-PUE-01: el numeral existe y su titulo no corresponde al "
            "contenido que se le atribuye. Tampoco se salva leyendolo como la "
            "edicion de 1985, cuyo Capitulo 4 es 'Tapered Inlets'. La mitad "
            "'y Apendice A' de la cita vieja SI era correcta y se conserva. "
            "La interpolacion lineal la prescribe Sec. 4.2 de la hoja de "
            "ruta, no HDS-5"),
        reemplazado_por="Lectura directa de la carta de HDS-5 en la zona de "
                        "transicion, o el procedimiento tangente si el "
                        "expediente exige reproducir la curva original",
        verificacion_pendiente="Declarar en la memoria que puntos del corredor "
                               "caen con q* entre 3.5 y 4.0: si ninguno lo hace, "
                               "esta simplificacion no toca ningun resultado y "
                               "basta con dejarla enunciada",
        resolucion=Libre(
            que_lo_fija="el proyectista: HDS-5 traza a mano una curva "
                        "tangente a las dos ramas y no publica ecuacion "
                        "cerrada, de modo que el procedimiento programable "
                        "no sale de la fuente",
            dominio="declaracion del metodo de empalme",
        ),
    ),

    "hw_entrada_fuera_de_rango": Criterio(
        # EL VACIO QUE PC-03 PIDIO Y PF-1 ABRIO. La correccion por pendiente
        # Ks*S de las ecs. (A.1) y (A.3) de HDS-5 es una recta sin tope: con
        # Ks = -0.5, un caudal chico y una pendiente grande la carga a la
        # entrada sale en cero o bajo cero (MAT-D10). HDS-5 no dice que hacer
        # ahi y la hoja de ruta tampoco. Hasta PF-1 `M4.control_entrada`
        # lanzaba DisenoNoFactibleError y el material se descartaba entero,
        # con razon --- HWi/D DECRECE con D, y si la carta se cae en el D
        # minimo ninguno mayor la levanta --- pero MUDO: el Bloqueo viajaba
        # sin criterio y la pestaña 4 no lo mostraba. La regla de CLAUDE.md
        # para un vacio es esta entrada: valor=None, [A], y detener el
        # calculo con excepcion; la decision de clase (CriterioPendienteError
        # y no MetodoNoEvaluableError) esta en la ficha PF-1-01 de
        # docs/decisiones_diferidas.md.
        # --- T-2 --- (cadena T, 2026-11-11; INF-0.5, punto 6 del encargo):
        # DEJA DE ESTAR VACIO. Se adopta «energia_critica», con lo que el
        # HDS-5 SI dice: que la Forma 1 es H_c «adjusted with correction
        # factors» (num. A.2.1, pag. impresa A.1, cita
        # `HDS5_3ED.A.2.1#FORMA_1`) y que el efecto de la pendiente es chico
        # (num. A.3, `HDS5_3ED.A.3#PENDIENTE_2`). Cuando la correccion,
        # extrapolada, anula la carga, el proyecto se queda con la base de la
        # ecuacion. DOS COSAS QUE EL ENCARGO PEDIA Y NO SE HICIERON, porque
        # la fuente no las sostiene: (1) la cita «HDS-5 Tabla A.1, nota de
        # Ks·S» NO EXISTE --la Tabla A.1 (PDF 197) solo lleva al pie sus
        # referencias bibliograficas--; (2) la etiqueta [C]: HDS-5 no
        # prescribe este piso ni ningun otro, de modo que sigue siendo una
        # adopcion con alternativa, [A]. Ningun punto de la linea base cae
        # fuera de rango (S 0.004-0.010 frente a S* >= 0.27): el valor no
        # toca ningun resultado del repositorio.
        valor="energia_critica",
        nivel=NIVEL_PERFIL,         # lo consume M4 (Fase 4), que corre a perfil;
                                    # el corredor del repositorio nunca lo invoca
                                    # (S_cauce 0.006-0.008 frente a S* ~ 0.38)
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO, que es la ventana entera. «energia_critica»:
        # se adopta HW = H_c, la energia especifica critica que el paso 4.2.1
        # ya resolvio --- la carga minima con que la entrada pasa Q en
        # regimen critico ---, y se declara que la correccion por pendiente
        # quedo saturada; la memoria imprime al lado el HWi/D que la ecuacion
        # devolvio y el S* de la carta. Es una adopcion con un salto: justo
        # por debajo de S* la ecuacion entrega una carga diminuta y positiva
        # (con S = 0.37706 y D = 0.90, HW = +1e-6 m) y justo por encima el
        # piso vale H_c; el salto es de la ecuacion extrapolada, no del
        # piso, y queda dicho aqui porque quien declare esta opcion tiene
        # que saber que la carga NO es continua en S*. «descartar»: la
        # conducta de antes de PF-1, DisenoNoFactibleError con el par (Q, S)
        # y S* en el motivo, y el material entero descartado.
        sensibilidad=("energia_critica", "descartar"),
        concepto="Que se adopta cuando la ecuacion de control de entrada de "
                 "HDS-5 devuelve una carga nula o negativa por la correccion "
                 "por pendiente Ks*S (caudal chico con pendiente grande)",
        justificacion="La ec. (A.1) HWi/D = H_c/D + K*(q*)^M + Ks*S y la (A.3) "
                      "HWi/D = c*(q*)^2 + Y + Ks*S llevan la correccion por "
                      "pendiente como recta sin tope, con Ks = -0.5 en las "
                      "embocaduras sin inglete. Para S > S* = -(H_c/D + "
                      "K*(q*)^M)/Ks (Forma 1 no sumergida) la carga sale bajo "
                      "cero: una lamina por debajo del fondo, que no existe. "
                      "HDS-5 formula la correccion para pendientes corrientes "
                      "de alcantarilla y no dice que hacer fuera de ese rango; "
                      "la hoja de ruta (Sec. 4.2) tampoco. Adoptar un piso en "
                      "el codigo seria rellenar el vacio en silencio; "
                      "descartar sin decirlo era un no factible definitivo "
                      "por una condicion que el proyectista podia resolver "
                      "declarando. Se adopta «energia_critica» como valor de "
                      "archivo por lo que la fuente si dice: define la Forma "
                      "1 como la energia especifica en el tirante critico "
                      "ajustada con factores de correccion (cita "
                      "HDS5_3ED.A.2.1#FORMA_1) y dice del termino de "
                      "pendiente que su efecto es chico (cita "
                      "HDS5_3ED.A.3#PENDIENTE_2). H_c es por tanto la base de "
                      "la que la ecuacion parte: un resultado que el paso 4.2 "
                      "ya tiene, no un numero nuevo. Lo que el piso acota y "
                      "lo que no: queda por encima de lo que la ecuacion "
                      "entregaba (carga nula o negativa, con la que V4 y la "
                      "rasante de 7.A se evaluaban sin carga), y solo en ese "
                      "sentido es del lado seguro. No es una cota conservadora "
                      "de la carga: omite el termino K*(q*)^M de la "
                      "contraccion de la entrada y queda por debajo de la "
                      "carga que la misma ecuacion da con el barril "
                      "horizontal, de modo que el paso lo imprime como piso "
                      "adoptado y no como resultado de la ecuacion. Y es un "
                      "caso practicamente inalcanzable desde que la pendiente "
                      "del conducto se limita a 0.10 m/m ('pendiente_maxima_"
                      "conducto', V10): con el tubo de 0.90 m la ecuacion "
                      "solo deja de entregar carga por debajo de 0.10 m/m "
                      "con caudales menores de 0.005 m3/s. La fuente "
                      "no prescribe este piso ni ningun otro, de modo que la "
                      "etiqueta es [A] y «descartar» sigue en la ventana. "
                      "Lo que el piso hace y lo que no: acota el "
                      "signo. Solo gobierna cuando la ecuacion no entrega "
                      "carga (S > S*); por debajo de S* la ecuacion puede dar "
                      "una carga positiva menor que H_c y se acepta tal cual "
                      "(con D = 0.90 y Q = 0.05: HW = 0.035 m a S = 0.30 "
                      "frente a H_c = 0.169 m), de modo que «energia_critica» "
                      "no impone H_c como minimo en todo el rango y la carga "
                      "salta en S*: justo por debajo la ecuacion da +1e-6 m y "
                      "justo por encima el piso vale H_c. El salto es de la "
                      "ecuacion extrapolada, no del piso, y quien declare "
                      "esta opcion tiene que saberlo. Con D = 0.90 m (el "
                      "minimo del catalogo) S* vale 0.377 para Q = 0.05 m3/s "
                      "y 0.54 para 0.10: en el corredor del repositorio "
                      "(S_cauce 0.006-0.008) no se alcanza; en una via con "
                      "alivios pequenos en tramos empinados si. Y descartar "
                      "el material entero bajo «descartar» es correcto para "
                      "las cartas de Forma 1 del catalogo circular, donde S* "
                      "no crece con D; bajo Forma 2 un D mayor puede llevar "
                      "la rama a la (A.2), sin Ks*S, y S* deja de existir",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), num. A.2 'INLET CONTROL "
               "EQUATIONS', pag. impresa A.1-A.2 (PDF 190-191): las ecs. "
               "(A.1) y (A.3) con su termino Ks*S, sin acotar su rango de "
               "pendiente; num. A.2.1, pag. impresa A.1 (cita "
               "HDS5_3ED.A.2.1#FORMA_1): «Form (1) is based on the specific "
               "head at critical depth, adjusted with correction factors»; "
               "num. A.3, pag. impresa A.2 (cita HDS5_3ED.A.3#PENDIENTE_2): "
               "«the slope effect is small». La fuente define la base y el "
               "termino y NO fija el piso: adoptarlo es decision del "
               "proyectista (Fundamento F4.PISO_HW, verbo DEFINE). La Tabla "
               "A.1 no lleva nota alguna sobre Ks*S",
        reemplazado_por="Un procedimiento de control de entrada valido para "
                        "pendientes de ese orden (curvas de HDS-5 para "
                        "pendientes fuertes, o ensayo), que ninguna fuente de "
                        "normas/ trae hoy",
        verificacion_pendiente="Declarar en la memoria que puntos del corredor "
                               "caen con S > S*(Q, D): si ninguno lo hace, "
                               "este criterio no toca ningun resultado y no "
                               "se invoca",
        resolucion=Libre(
            que_lo_fija="el proyectista, cuando un punto cae fuera del rango "
                        "de la correccion por pendiente: H_c como piso "
                        "declarado, o el descarte",
            dominio="declaracion del tratamiento del caso fuera de rango",
        ),
    ),

    "n_manning_hdpe": Criterio(
        # --- T-4 --- DEJA DE SER UNA ANALOGIA CON EL CONCRETO (INF-3.2.1).
        # Hasta T-4 valia `MANNING["concreto_tubo_recto"]` = (0.010, 0.013),
        # la fila del concreto de la Tabla N 09 peruana aplicada [N->] a un
        # material que esa tabla no lista. La fuente tecnica que SI tabula el
        # polietileno corrugado estaba en normas/ desde el principio: HDS-5
        # 3a ed., Apendice B, Table B.1, fila «Corrugated Polyethylene /
        # Smooth», 0.009-0.015 (pag. impresa B.6). Ni AASHTO M 294-11 (leida
        # entera, traduccion no oficial) ni el WSDOT Hydraulics Manual (su
        # Table 4-1 es una tabla de REFERENCIAS, sin valores) traen un n.
        #
        # El valor NO se escribe: se LEE de la fila transcrita en el registro
        # (`_N_MANNING_HDPE_HDS5`), por lo mismo que antes se leia de MANNING.
        valor=_N_MANNING_HDPE_HDS5,     # RANGO (n_min, n_max), no puntual
        nivel=NIVEL_PERFIL,
        etiqueta="C",               # fuente tecnica reconocida (FHWA), ya no analogia
        forma=FORMA_PAR_ORDENADO,
        concepto="Coeficiente de rugosidad de Manning para HDPE de interior liso",
        justificacion="Decide el coeficiente de rugosidad de Manning que se "
                      "aplica al HDPE de interior liso. La Tabla N 09 del "
                      "Manual de Hidrologia tabula materiales y no lista el "
                      "polietileno, y la norma de producto del HDPE tampoco "
                      "trae un coeficiente de rugosidad. El vacio se cubre "
                      "con la fuente tecnica que el Manual ya toma para la "
                      "hidraulica de alcantarillas: la tabla de valores de n "
                      "para alcantarillas del manual HDS-5 de la FHWA, cuya "
                      "fila del polietileno corrugado de interior liso da el "
                      "rango 0.009 a 0.015. Se toma el rango completo y no "
                      "un valor puntual: la regla de doble n pide los dos "
                      "extremos -- el maximo para capacidad y tirante, el "
                      "minimo para velocidad maxima y socavacion -- y con un "
                      "solo numero una de las dos verificaciones deja de ser "
                      "conservadora. Frente a la fila del concreto de tubo "
                      "recto de la Tabla N 09, que es la que el proyecto "
                      "aplicaba por analogia, el rango de la fuente es mas "
                      "ancho en los dos sentidos: exige mas diametro por "
                      "capacidad y da mas velocidad contra el techo. La "
                      "fuente advierte que sus valores son de laboratorio y "
                      "que los de campo pueden variar por abrasion, "
                      "corrosion, deflexion y juntas",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), Apendice B, Table B.1 "
               "'Manning's n Values for Culverts', pag. impresa B.6 (PDF "
               "208): fila 'Corrugated Polyethylene / Smooth', 0.009-0.015, "
               "con referencias Barfuss & Tullis 1988 y Tullis et al. 1990. "
               "Tabla HDS5_3ED.TB.1 del registro, transcrita integra (trece "
               "filas) y cita HDS5_3ED.TB.1 con su nota al pie 1. "
               "LO QUE NO LO DA: la Tabla N 09 del Manual de Hidrologia "
               "(num. 4.1.1.3.6, pag. impresa 75) no lista el HDPE "
               "(afirmacion negativa SIN_HDPE_T09); AASHTO M 294-11, en "
               "normas/ como traduccion no oficial, no trae coeficiente de "
               "rugosidad en ninguna de sus 17 hojas (buscado 'Manning' y "
               "'rugosidad': cero apariciones); y la Table 4-1 del WSDOT "
               "Hydraulics Manual M 23-03.12 (pag. impresa 4-7) es una tabla "
               "de referencias que remite a HEC-22, sin valores. "
               "HASTA T-4 este criterio era [N->]: la fila del concreto de "
               "tubo recto de la Tabla N 09, (0.010, 0.013), por analogia. QUE LA "
               "FILA ES LA DE INTERIOR LISO lo respalda la norma peruana de "
               "construccion: EG-2013, Subseccion 508.02 a), pag. impresa "
               "981 (cita EG2013.508.02a), define el tubo de PAD/HDPE como "
               "de superficie interior lisa y pared exterior corrugada, "
               "clasificacion tipo S",
        reemplazado_por="Ficha tecnica del producto seleccionado, con el n "
                        "del fabricante y el ensayo que lo respalda",
        # LA VENTANA ES EL RANGO DE LA PROPIA FILA: dentro de el se puede
        # declarar un par mas estrecho (el del fabricante); fuera de el, el
        # valor ya no lo sostiene esta fuente.
        sensibilidad=_N_MANNING_HDPE_HDS5,
        verificacion_pendiente="Confirmar que el HDPE especificado es de INTERIOR "
                               "LISO (Tipo S o Tipo D de AASHTO M 294). El de "
                               "interior corrugado (Tipo C) tiene en la misma "
                               "tabla n = 0.018-0.025 y aplicarle esta fila "
                               "seria gruesamente inseguro en capacidad",
        resolucion=DeTabla(
            tablas=("HDS5_3ED.TB.1",),
            fila_id="polietileno_corrugado_liso",
            que_elige="la fila cuyo par (minimo, maximo) es la doble n del "
                      "HDPE de interior liso. La Tabla N 09 peruana no "
                      "tabula el polietileno: la fila es de la fuente "
                      "tecnica, y por eso la etiqueta es [C]",
        ),
    ),

    # --- VE-2 (a) --- (decision del dueño, 2026-11-17, ficha VE1-02 (a)) LA
    # COLUMNA DEL n DEL TUBO DE CONCRETO ES UNA ELECCION [A]. Hasta VE-2 la
    # doble n del concreto era lectura directa de la Tabla N 09 --MINIMO para
    # velocidad, MAXIMO para capacidad-- rotulada «Regla [N]» por la hoja de
    # ruta (§4.1) sin numeral (ficha VE1-01, D3; la hoja de ruta la escribe
    # como adopcion [A] desde su correccion del 2026-11-18). El valor de
    # archivo es esa misma doble n: ningun numero del expediente se mueve.
    "columna_n_manning_concreto": Criterio(
        valor="doble_n_minimo_maximo",
        # DE PERFIL: lo lee `M2.catalogo` al armar el tubo de concreto, que
        # la corrida `--alcance perfil` arma para todo punto de Familia A o
        # B (lo mide `tests/test_nivel_medido.py`).
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("doble_n_minimo_maximo", "columna_normal",
                      "n_unico_hds5"),
        concepto="Columna de la Tabla Nº 09 de la que sale el coeficiente de "
                 "Manning del TUBO de concreto: la doble n (minimo y maximo), "
                 "la columna normal o el n unico del HDS-5",
        justificacion="Decide con que n de Manning se resuelve el tubo de "
                      "concreto. El Manual de Hidrologia, num. 4.1.1.3.6 "
                      "(pag. impresa 74, cita MC_HHD.4.1.1.3.6), solo remite "
                      "a la Tabla Nº 09, y la tabla (pag. impresa 75) da "
                      "para la fila del tubo recto de concreto "
                      "tres columnas, MINIMO 0.010, NORMAL 0.011 y MAXIMO "
                      "0.013 (lectura corregida del bloque A.2, errata "
                      "DIS-MCHHD-T09-A2-DESPLAZADA), sin regla de columna: "
                      "la doble n es una adopcion del proyecto, sin numeral "
                      "que la sostenga, y asi la escribe la hoja de ruta en "
                      "su §4.1. Se adopta la doble n "
                      "('doble_n_minimo_maximo'): el MAXIMO (0.013) para "
                      "capacidad, tirante y control de salida, y el MINIMO "
                      "(0.010) para velocidad maxima y socavacion, cada "
                      "verificacion con el extremo que la deja del lado "
                      "seguro. Alternativas barribles: 'columna_normal' -- el "
                      "0.011 de la misma fila para las dos ramas, el valor "
                      "corriente de la tabla: baja el tirante y la carga de "
                      "salida y sube la velocidad de capacidad; 'n_unico_hds5' "
                      "-- 0.012 para las dos ramas, el n tipico de diseño de "
                      "un conducto de pared lisa del HDS-5 (num. 3.1.4, pag. "
                      "impresa 3.8), [C]; el num. B.2 del HDS-5 (pag. impresa "
                      "B.2) da 0.011 a 0.013 para el tubo de concreto en "
                      "obra. Con un n unico la estimacion alta y la baja de "
                      "velocidad coinciden: se pierde el margen de la doble "
                      "n en las dos ramas a la vez",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.1.3.6 «Diseño hidraulico», pag. impresa 74 (PDF 77), "
               "cita MC_HHD.4.1.1.3.6, y Tabla Nº 09, pag. impresa 75 (PDF "
               "78), cita MC_HHD.4.1.1.3.6#T09, fila «A.2 NO METALICOS - a. "
               "Concreto - tubo recto y libre de basuras», leida con la "
               "correccion de DIS-MCHHD-T09-A2-DESPLAZADA "
               "(constantes_normativas.TABLA_09_FILAS). HDS-5 3a ed. "
               "(FHWA-HIF-12-026), num. 3.1.4 «Outlet Control», pag. impresa "
               "3.8 (PDF 90), cita HDS5_3ED.3.1.4#N_TIPICO: «Typical "
               "Manning's n values used for designing culverts are n = 0.012 "
               "for smooth walled culverts»; y num. B.2 «CONCRETE PIPE "
               "CULVERTS», pag. impresa B.2 (PDF 204), cita "
               "HDS5_3ED.B.2#CONCRETO_CAMPO: «These values are increased to "
               "0.011 to 0.013 based on field installation and aging». LA "
               "DOBLE N NO TIENE NUMERAL, sin numeral en ninguna de las tres "
               "fuentes: es la Sec. 4.1 de la hoja de ruta, que la escribe "
               "como adopcion [A]",
        reemplazado_por="Ficha tecnica del tubo especificado (metodo de "
                        "fabricacion y juntas), con el n del fabricante y el "
                        "ensayo que lo respalda",
        resolucion=Libre(
            que_lo_fija="el proyectista: la Tabla Nº 09 da tres columnas por "
                        "fila y ni el Manual ni el HDS-5 dicen cual usar ni "
                        "que se usen los dos extremos",
            dominio="doble_n_minimo_maximo | columna_normal | n_unico_hds5",
        ),
    ),

    "v_max_hdpe": Criterio(
        # 15 ft/s x 0.3048 m/ft = 4.572 m/s EXACTOS. Antes decia 4.6 (MAT-O14):
        # un maximo redondeado HACIA ARRIBA queda 0.6 % por encima del corte
        # que dice aplicar. Un minimo se redondea hacia arriba y un maximo
        # hacia abajo; aqui no hace falta redondear porque la conversion es
        # exacta.
        #
        # --- T-4 --- LA FICHA SE REESCRIBE CONTRA EL PDF (INF-3.2.4). Decia
        # «Tabla 8-4 ... Techo duro: por encima de 15 ft/s el termoplastico
        # ... su uso queda prohibido». Dos cosas eran falsas: la Tabla 8-4 no
        # es de velocidades maximas sino de NIVELES DE ABRASION, y la
        # prohibicion no esta en ella sino en el §8-3.3, atada al NIVEL y no
        # a la velocidad sola. Las dos citas van separadas en el registro
        # (WSDOT_HM.8-3.3#SEVERA y WSDOT_HM.T8-4) y la lectura que las une
        # --la velocidad por si sola como criterio suficiente-- esta
        # declarada como `Interpretacion` de la tabla. Sigue siendo [C]: la
        # fuente asocia al termoplastico un «shall not be used».
        valor=4.572,
        nivel=NIVEL_PERFIL,
        etiqueta="C",               # fuente tecnica reconocida (WSDOT)
        forma=FORMA_FLOAT,
        concepto="Velocidad maxima admisible en HDPE",
        justificacion="Decide el techo de velocidad de la verificacion V3 "
                      "para el HDPE. La Tabla N 10 del Manual de Hidrologia "
                      "no lista materiales flexibles y el inciso de abrasion "
                      "del mismo Manual manda considerarla sin dar un "
                      "numero. La fuente tecnica adoptada prohibe el "
                      "termoplastico en sitios de abrasion severa, porque "
                      "no se puede reforzar, y describe ese nivel por tres "
                      "caracteristicas del sitio, una de las cuales es una "
                      "velocidad mayor de 15 ft/s, que son 4.572 m/s. El "
                      "proyecto toma esa velocidad por si sola como criterio "
                      "suficiente para clasificar el sitio como severamente "
                      "abrasivo: es una lectura conservadora que la fuente "
                      "permite -- su nota dice que no hace falta que "
                      "concurran las tres caracteristicas -- y que no "
                      "impone, porque una velocidad mayor sin carga de fondo "
                      "no es abrasion severa. El nivel de abrasion del "
                      "sitio, cuando el estudio de campo lo declara, entra "
                      "ademas por la matriz de durabilidad y descarta el "
                      "HDPE aunque la velocidad sea menor",
        fuente="WSDOT Hydraulics Manual M 23-03.12 (abril 2026), fuente "
               "WSDOT_HM del registro, con el PDF en el repositorio de "
               "normas. LA PROHIBICION: num. 8-3.3 'Thermoplastic Pipe: "
               "General', pag. impresa 8-13 (PDF 228), cita "
               "WSDOT_HM.8-3.3#SEVERA: el termoplastico no se usa en "
               "condiciones severamente abrasivas como las describe la "
               "Tabla 8-4. EL UMBRAL: num. 8-6 'Abrasion', Table 8-4 'Pipe "
               "Abrasion Levels', pags. impresas 8-27 y 8-28 (PDF 242 y "
               "243), tabla y cita WSDOT_HM.T8-4: la fila 'Severely "
               "abrasive' se describe, entre otras dos caracteristicas, por "
               "velocidades mayores de 15 ft/s. EL VALOR ES LA CONVERSION "
               "EXACTA: 15 x 0.3048 = 4.572 m/s. LA TABLA NO PROHIBE NADA AL "
               "TERMOPLASTICO: la celda de proteccion de su fila severa, en "
               "esta edicion, no lo nombra. SEGUNDA FUENTE DEL CORTE: AASHTO "
               "LRFD 9a ed., C12.6.9, pag. impresa 12-24, nivel 4 de "
               "abrasion de la FHWA (cita AASHTO_LRFD_9.C12.6.9#NIVEL_4). "
               "La hoja de ruta v8 nombra esta fuente y este valor en la "
               "fila V3 de la Fase 5, el Tablero 1.3 y el Anexo A",
        reemplazado_por="Ficha tecnica del producto seleccionado o "
                        "especificacion del fabricante con su propio techo "
                        "de velocidad; o el nivel de abrasion del sitio "
                        "declarado por el estudio de campo, que es el "
                        "criterio que la fuente escribe",
        # POR QUE NO LLEVA `vacio_verificado`, siendo una afirmacion negativa
        # sobre la Tabla N 10 (SIS-D-12): el campo es para el valor que cubre
        # un vacio AGOTADO sin encontrar nada. Aqui la busqueda ENCONTRO una
        # fuente tecnica reconocida y el valor sale de ella: es [C].
        #
        # LA VENTANA (PC-02): el techo es el corte de 15 ft/s --por encima,
        # bajo la lectura declarada, la fuente no admite el termoplastico-- y
        # el piso es la velocidad minima de V2 (`V_MIN`, 0.25 m/s): un techo
        # por debajo del piso no deja banda admisible. A diferencia de
        # 'v_max_tmc', aqui el piso NO se sube a los 10 ft/s del §3-3.5: ese
        # numeral habla de abrasion por arrastre y nombra al metal y al
        # concreto como los que necesitan mas espesor, y del termoplastico
        # dice que resiste mejor; no hay en la fuente una razon para que el
        # proyectista no pueda adoptar un techo mas bajo para el HDPE.
        sensibilidad=(V_MIN, 4.572),
        resolucion=Libre(
            que_lo_fija="el proyectista, leyendo el corte de velocidad de "
                        "la fila severa de la Tabla 8-4 del WSDOT "
                        "Hydraulics Manual como criterio suficiente de la "
                        "prohibicion del num. 8-3.3. Es fuente tecnica "
                        "reconocida y no norma peruana",
            dominio="m/s > 0",
        ),
    ),

    "v_max_tmc": Criterio(
        # 15 ft/s = 4.572 m/s exactos (MAT-O14); el numero no se mueve.
        #
        # --- T-4 --- PASA DE [C] A [A] (INF-3.2.4; opcion A, decidida por
        # el dueño del proyecto el 2026-11-11 y verificada contra el PDF).
        # NINGUNA fuente de normas/ fija una velocidad maxima para la
        # tuberia metalica corrugada: la Tabla N 10 no la lista, el inciso
        # de abrasion del Manual es cualitativo, la norma de producto
        # (AASHTO M 36 num. 1.2) reconoce ambientes severos sin cuantificar,
        # ASTM A796 remite a pavimentar la solera, y la Tabla 8-4 de WSDOT
        # --la que esta ficha citaba como fuente de un «techo»-- clasifica
        # SITIOS por abrasion y al metal le prescribe remedio, no
        # prohibicion. Un numero que ninguna fuente escribe como limite es
        # una adopcion: [A], con ventana.
        #
        # LO QUE LA FICHA DECIA Y SE RETIRA: «limite de diseño conservador»
        # y «por encima de este valor exige mayor calibre o revestimiento».
        # Lo segundo era falso tal como estaba: la fuente manda aumentar uno
        # o dos calibres ya desde 6 ft/s, en el nivel moderado.
        #
        # LA ASIMETRIA CON 'v_max_hdpe', que lleva el MISMO numero y es [C]:
        # al termoplastico la fuente le asocia una prohibicion («shall not
        # be used», §8-3.3) en el nivel que ese corte describe; al metal, en
        # el mismo nivel, un remedio. El numero es el mismo; lo que la
        # fuente hace con el, no.
        valor=4.572,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Velocidad maxima admisible en TMC",
        justificacion="Decide el techo de velocidad de la verificacion V3 "
                      "para la tuberia metalica corrugada. Ninguna fuente "
                      "consultada fija una velocidad maxima para este "
                      "material: la Tabla N 10 del Manual de Hidrologia no "
                      "lo lista, el inciso de abrasion del mismo Manual "
                      "manda considerarla al elegir el material y no da un "
                      "numero, y la norma de producto reconoce ambientes "
                      "severos sin cuantificarlos. El proyecto adopta como "
                      "techo el corte entre los niveles de abrasion moderado "
                      "y severo de la tabla de niveles de abrasion del "
                      "manual de hidraulica adoptado, 15 ft/s, que son "
                      "4.572 m/s. Ese corte es una clasificacion del sitio "
                      "que depende tambien de la carga de fondo y de la "
                      "pendiente, no un limite de velocidad, y para el metal "
                      "la fuente no prohibe nada en ningun nivel: prescribe "
                      "aumentar el espesor de la plancha o revestir la "
                      "solera, y lo prescribe ya desde 6 ft/s, que son "
                      "1.829 m/s. La verificacion V3 no sustituye esa "
                      "proteccion de la solera, que se decide con el nivel "
                      "de abrasion del sitio. Sensibilidad (3.048, 4.572) "
                      "m/s: el piso son los 10 ft/s a partir de los cuales "
                      "la misma fuente dice que la abrasion puede crecer de "
                      "forma significativa y pide tratar el caso; el techo "
                      "es el valor adoptado, y no se sube porque por encima "
                      "de el la fuente clasifica el sitio como severamente "
                      "abrasivo. Bajar el techo dentro de la ventana "
                      "descarta antes el material o lleva a un diametro "
                      "mayor; no mueve ninguna otra verificacion",
        fuente="NINGUNA NORMA NI FUENTE TECNICA FIJA EL VALOR COMO LIMITE. "
               "Lo que cada fuente dice, verificado sobre el PDF: (1) Manual "
               "de Hidrologia, Hidraulica y Drenaje (MTC), num. 4.1.1.3.7 e) "
               "'Abrasion', pag. impresa 81 (cita MC_HHD.4.1.1.3.7e): "
               "cualitativo; su Tabla N 10 (num. 4.1.1.3.6, pag. impresa "
               "76) no lista metal ni plastico (afirmacion negativa "
               "SIN_TMC_NI_HDPE_T10). (2) WSDOT Hydraulics Manual M "
               "23-03.12 (abril 2026), num. 8-6, Table 8-4 'Pipe Abrasion "
               "Levels', pags. impresas 8-27 y 8-28 (PDF 242 y 243), tabla "
               "y cita WSDOT_HM.T8-4: cuatro niveles de abrasion; el severo "
               "se describe por velocidades mayores de 15 ft/s entre otras "
               "dos caracteristicas, y para el metal pide al menos dos "
               "calibres mas o solera de concreto; el moderado, de 6 a "
               "15 ft/s, uno o dos calibres mas. EL VALOR ADOPTADO ES LA "
               "CONVERSION EXACTA DE ESE CORTE: 15 x 0.3048 = 4.572 m/s. "
               "(3) El mismo manual, num. 3-3.5 'Velocities in Culverts: "
               "General', pag. impresa 3-11 (PDF 76), cita "
               "WSDOT_HM.3-3.5#10FTS: por encima de unos 10 ft/s "
               "(3.048 m/s) la abrasion puede crecer de forma "
               "significativa; es el piso de la ventana. (4) AASHTO LRFD 9a "
               "ed., C12.6.9, pag. impresa 12-24 (cita "
               "AASHTO_LRFD_9.C12.6.9#NIVEL_4): los niveles de abrasion de "
               "la FHWA ponen el mismo corte de 15.0 ft/s para el nivel 4, "
               "tambien como clasificacion. (5) AASHTO M 36-03 (2007), num. "
               "1.2, pag. impresa M 36-1 (cita AASHTO_M36.1.2): sin umbral. "
               "(6) ASTM A796/A796M-13, num. 21.1 (PDF 6): donde haga falta "
               "resistencia adicional a la abrasion remite a pavimentar la "
               "solera, sin limite de velocidad. "
               "HASTA T-4 este criterio era [C] y atribuia el valor a la "
               "Tabla 8-4 como techo de la fuente",
        reemplazado_por="El nivel de abrasion del sitio declarado por el "
                        "estudio de campo (dato de entrada `abrasion` de la "
                        "matriz de durabilidad) junto con el espesor de "
                        "plancha y la proteccion de solera que la Tabla 8-4 "
                        "pide para ese nivel, que es el criterio que la "
                        "fuente escribe en lugar de un techo unico; o la "
                        "ficha tecnica del producto seleccionado",
        # LA VENTANA CAMBIA DE PISO EN T-4: era (V_MIN, 4.572), con el piso
        # en la velocidad minima de V2 (PC-02), y pasa a (3.048, 4.572). El
        # techo 4.6 que proponia la cadena T no tiene respaldo: son 15.09
        # ft/s, reintroduce el redondeo que MAT-O14 corrigio y entra en la
        # banda que la fuente clasifica como severa.
        sensibilidad=(3.048, 4.572),
        resolucion=Libre(
            que_lo_fija="el proyectista: ninguna fuente fija un techo de "
                        "velocidad para el metal corrugado. Adopta el corte "
                        "entre los niveles moderado y severo de la Tabla "
                        "8-4 del WSDOT Hydraulics Manual, que es una "
                        "clasificacion de abrasion y no un limite",
            dominio="m/s, entre los 10 ft/s del num. 3-3.5 y los 15 ft/s "
                    "de la Tabla 8-4 del WSDOT Hydraulics Manual",
        ),
    ),

    "v_max_concreto_eleccion": Criterio(
        valor=None,                 # OPCIONAL: sin valor, V3 usa el techo [N]
        # NIVEL MEDIDO, y lo mide la TERCERA corrida de
        # `tests/test_nivel_medido.py`, que existe por este caso: `opcional=True`
        # se lee con `valor_si_declarado()`, que NO registra el uso mientras el
        # criterio siga vacio, de modo que las dos corridas normales no lo pueden
        # ver. Declarado en caliente con el valor que ya rige por defecto, la
        # corrida `--alcance perfil` SI lo invoca. Medirlo asi no mueve ningun
        # resultado: la declaracion repite lo que el consumidor ya aplicaba.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Techo de velocidad adoptado para el concreto, mas "
                 "conservador que el maximo normativo de 6.0 m/s",
        justificacion="Decide el techo de velocidad que el proyecto aplica al "
                      "concreto cuando adopta uno mas conservador que el "
                      "maximo normativo. Es opcional y no un vacio: sin "
                      "declarar, el calculo no se detiene, V3 aplica el techo "
                      "normativo de 6.0 m/s y la memoria no declara este "
                      "criterio. Es uno de los tres `opcional=True` del archivo, "
                      "con 'riesgo_admisible_propietario' y "
                      "'esviaje_max_grados', y los tres comparten la "
                      "mecanica: sin declarar, nada se detiene. M2 lee ademas "
                      "con `valor_si_declarado()` otras cuatro "
                      "claves no opcionales ('n_manning_hdpe', "
                      "'espesor_pared_conducto', 'v_max_tmc' y 'v_max_hdpe') "
                      "para armar el catalogo con campos vacios, pero "
                      "aquellas si detienen el calculo mas tarde, en el punto "
                      "de uso, y esta no detiene nada nunca. La fuente (Tabla "
                      "N 10 del Manual de Hidrologia, num. 4.1.1.3.6) trae "
                      "para el concreto dos valores, 3.0 y 6.0 m/s, y su "
                      "titulo y el rotulo de su unica columna de valores los "
                      "declaran maximos; el piso de velocidad no sale de esa "
                      "tabla sino de V2 (0.25 m/s, misma pagina) y vale para "
                      "todos los materiales. Lo que la fuente no resuelve es "
                      "por que la fila trae dos maximos: el Manual no lo "
                      "explica en ninguna parte, y que el superior "
                      "corresponda al acabado de mejor calidad es "
                      "interpretacion del proyecto, declarada aparte en "
                      "constantes_normativas.TABLA_10_INTERPRETACION_PROYECTO "
                      "-- de donde la lee la memoria --, no adosada a la "
                      "cita. Se adopta que el proyectista pueda bajar el "
                      "techo dentro de la fila -- un concreto de acabado "
                      "corriente admite menos --, decision defendible sobre "
                      "las condiciones de esta obra y no exigencia del "
                      "numeral: por eso [A]. Sensibilidad (3.0, 6.0): los dos "
                      "valores que la fila del concreto escribe, en m/s; "
                      "adoptar 3.0 m/s es el techo mas conservador que se "
                      "puede tomar sin salirse de la tabla, y 3.0 no es un "
                      "piso a decidir -- el piso es V2, y leer el 3.0 como "
                      "piso llevaria a rechazar conductos de concreto "
                      "admisibles",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, "
               "RD 20-2011-MTC/14), Tabla N 10 'Velocidades maximas "
               "admisibles (m/s) en conductos revestidos', num. 4.1.1.3.6, "
               "pag. impresa 76. Fuente de la propia tabla: HCANALES, Maximo "
               "Villon B. -- no es una tabla de elaboracion del MTC. "
               "TITULO CORREGIDO (NOR-HID-06): este campo entrecomillaba el "
               "titulo sin '(m/s)'. En una cita entre comillas que la memoria "
               "reproduce, la unidad omitida es lo primero que un revisor "
               "comprueba. "
               "LO QUE LA FUENTE SOSTIENE: que los dos numeros de la fila del "
               "concreto, 3.0 y 6.0 m/s, son ambos MAXIMOS. Lo dice el titulo "
               "de la tabla y lo confirma el rotulo de su unica columna de "
               "valores, 'VELOCIDAD (M/S)'. 6.0 m/s es el mayor de los dos y "
               "es el valor [N] que V3 aplica cuando este criterio no se "
               "declara. El piso de velocidad NO sale de esta tabla: es V2, "
               "0.25 m/s del parrafo siguiente, y vale para todos los "
               "materiales. "
               "LO QUE NO SOSTIENE, Y ESTE CAMPO AFIRMABA (NOR-HID-04): que "
               "el rango 'recorra la calidad del revestimiento' y que 3.0 sea "
               "'el maximo del acabado mas pobre'. El Manual no explica en "
               "ninguna parte por que hay dos numeros. La frase con que "
               "introduce la tabla apunta incluso en otra direccion ('se "
               "encuentre dentro de un rango, cuyos limites se describen a "
               "continuacion') y la fila de mamposteria trae UN SOLO valor "
               "(2.0), que no encaja con una lectura de acabados. Es "
               "INTERPRETACION DEL PROYECTISTA -- razonable, y la que sostiene "
               "que este criterio pueda bajar el techo dentro de la fila -- y "
               "se declara como tal, no adosada a la cita: "
               "constantes_normativas.TABLA_10_INTERPRETACION_PROYECTO la "
               "imprime separada, y la memoria la lee de ahi. "
               "QUE SIGNIFICA ENTONCES EL RANGO DE SENSIBILIDAD (3.0, 6.0): "
               "los dos valores que la fila del concreto escribe. Adoptar el "
               "menor es el techo mas conservador que se puede tomar sin "
               "salirse de la tabla; no lo normaliza ningun numeral, y por eso "
               "[A] y no [N]",
        sensibilidad=(3.0, 6.0),
        opcional=True,      # sin declarar, V3 aplica el techo [N] de 6.0 m/s
        resolucion=EnRango(
            tabla_id="MC_HHD.T10",
            fila_id="MC_HHD.T10#concreto",
            columna_id="velocidad",
            que_acota="el techo de velocidad adoptado para el concreto. LA "
                      "FILA TRAE DOS MAXIMOS Y NINGUN PISO (NOR-HID-04): la "
                      "celda es un `ConjuntoDeMaximos` y la ventana no puede "
                      "pintar el 3.0 como minimo",
        ),
    ),

    "ke_entrada": Criterio(
        valor=0.5,
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_FLOAT,
        concepto="Coeficiente de perdida de carga en la embocadura (ke)",
        justificacion="La ecuacion de control de salida de la hoja de ruta, "
                      "H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g), contiene ke "
                      "pero ningun apartado de la hoja le asigna valor. El "
                      "Manual MTC no desarrolla el control de salida, de modo "
                      "que el dato sale de HDS-5, en la fila que corresponde a "
                      "la embocadura ya adoptada por diseno: tubo a ras del "
                      "muro (square edge with headwall). "
                      "TRAZABILIDAD: este 0.5 ya estaba en uso como dato fijo "
                      "en el caso patron CP-8 de tests/fixtures/casos_patron.py "
                      "('ke': 0.5), donde entra en el calculo de H sin declarar "
                      "de donde salia. Queda trazado aqui: el fixture y el "
                      "calculo leen ahora el mismo origen, y si el valor cambia, "
                      "cambia en un solo sitio",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice C, Tabla C.2 "
               "'Entrance Loss Coefficients', pag. impresa C.6 (PDF 216). "
               "En el bloque 'Pipe, Concrete', la fila se imprime "
               "'Square-edge  0.5' SANGRADA bajo el rotulo de agrupacion "
               "'Headwall or headwall and wingwalls': el 0.5 lo fija esa "
               "pertenencia, y la fila suelta sin su encabezado pierde la "
               "condicion. NINGUNA fila de la tabla se imprime literalmente "
               "'square edge with headwall', que es como el proyecto nombra a "
               "la embocadura adoptada: ese nombre es la suma de la fila y de "
               "su rotulo de agrupacion, y por eso se citan los dos. "
               "LA PAGINA ESTABA MAL Y SE CORRIGE: este campo "
               "decia 'pag. C.2', que es el numero de la TABLA leido como "
               "numero de pagina. La pag. impresa C.2 (PDF 212) es la "
               "continuacion del indice de cartas del Apendice C y no "
               "contiene ningun coeficiente. Verificado contra el PDF en la "
               "sesion de C06; el valor 0.5 confirma, el localizador no. "
               "OJO AL 0.7 (NOR-HDS-04): esta misma tabla da ke = 0.7 para "
               "'Mitered to conform to fill slope', que es el MISMO numero "
               "que el Ks = +0.7 de inglete del control de ENTRADA "
               "(constantes_normativas.HDS5_INLET) y una magnitud sin "
               "ninguna relacion con el. Con embocadura a ras del muro, que "
               "es la adoptada, no coinciden; con inglete si, y no hay que "
               "deducir uno del otro",
        reemplazado_por="Fila de HDS-5 que corresponda si cambia el detalle de "
                        "embocadura del cabezal (Tablero 2.3). La Tabla C.2 "
                        "trae las demas configuraciones de borde",
        # LA VENTANA ES LA DE LA TABLA DE LA QUE SALE (PC-02, EXT-V-02): el
        # recorrido de los coeficientes que la Tabla C.2 imprime, 0.2 a 0.9,
        # DERIVADO de la transcripcion (`KE_HDS5_C2`) y no copiado. Sin ella
        # `--declarar ke_entrada=-0.5` pasaba la CLI entera, bajaba el HW de
        # salida y podia cambiar el control gobernante, y `ke_entrada=0,5`
        # declaraba la tupla (0, 5) por una coma. El consumidor
        # (`M4.perdida_carga`) valida ademas el signo y el tipo, porque la
        # ventana solo defiende lo que entra por la puerta de declaracion.
        sensibilidad=_VENTANA_KE_C2,
        resolucion=DeTabla(
            tablas=("HDS5_3ED.TC2",),
            fila_id="concreto_headwall_square_edge",
            que_elige="la fila de embocadura de la que sale ke; el 0.5 lo "
                      "fija la pertenencia de la fila al rotulo de "
                      "agrupacion 'Headwall or headwall and wingwalls'",
        ),
    ),

    "geometria_control_salida": Criterio(
        valor="seccion_llena",
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_STR,
        concepto="Seccion de referencia de la que se toman V y R en la ecuacion "
                 "de control de salida H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g)",
        justificacion="Decide de que seccion se toman V y R en la ecuacion de "
                      "control de salida H = (1 + ke + "
                      "19.63*n^2*L/R^(4/3))*V^2/(2g). La fuente proxima (Sec. "
                      "4.3 de la hoja de ruta) escribe la ecuacion y no dice "
                      "a que seccion pertenecen V y R, y la eleccion no es "
                      "cosmetica: con la seccion llena de un tubo de 0.90 m, "
                      "R = D/4 = 0.225 m; con el tirante normal de y/D = "
                      "0.75, R = 0.2715 m -- la misma formula da dos H "
                      "distintas. Lo que se elige es la seccion, no una "
                      "formula: como se calculan A y R a partir de ella es "
                      "asunto de la geometria de cada forma "
                      "(`Seccion.area_llena` y "
                      "`Seccion.radio_hidraulico_lleno`), y M4 no los "
                      "escribe: los pide. Se adopta la seccion llena porque "
                      "es la seccion para la que HDS-5 (Cap. III) deriva esa "
                      "expresion: los tres sumandos (1 = carga de velocidad, "
                      "ke = perdida de entrada, 19.63*n^2*L/R^(4/3) = perdida "
                      "por friccion) son las perdidas de un barril trabajando "
                      "lleno, que es el caso de control de salida por "
                      "definicion; aplicarla sobre la geometria del tirante "
                      "normal mezcla dos regimenes. Sensibilidad, medida "
                      "sobre las dos formas de esta obra: en el marco de 2.00 "
                      "x 1.50 m, el R de la seccion llena es B*H/(2*(B+H)) = "
                      "0.4286 m -- que no es H/4 = 0.375 m -- y el del "
                      "tirante de y/H = 0.75 es 0.5294 m, un +23.5 % frente "
                      "al +20.7 % del tubo; la eleccion pesa lo mismo en las "
                      "dos formas y por eso el criterio vale para las dos, "
                      "aunque la aritmetica de una no sirva para la otra. "
                      "Trazabilidad del caso patron: CP-8 alimenta la formula "
                      "con R = 0.27152 m y V = 2.2807 m/s, los de la seccion "
                      "parcialmente llena de CP-2, y no contradice esta "
                      "adopcion: es un caso patron de la constante en SI "
                      "(19.63) frente al 29 imperial, y para eso da V y R "
                      "como datos sueltos, no como la geometria de un control "
                      "de salida real",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Cap. III - control de salida a "
               "seccion llena. Sec. 4.3 de la hoja de ruta cita la ecuacion sin "
               "definir la seccion",
        reemplazado_por="Procedimiento de barril parcialmente lleno de HDS-5 "
                        "(Cap. III), que desde E-A el proyecto SI calcula "
                        "(`M4.perfil_lamina`, paso 4.3c/4.3d): mide la "
                        "longitud a seccion llena y da la carga por remanso "
                        "bajo HW/D < 0.75. Lo que este criterio sigue "
                        "decidiendo es de que seccion salen V y R del termino "
                        "de friccion de H; una seccion de referencia distinta "
                        "exigiria ademas cambiar ese termino, no el perfil",
        verificacion_pendiente=(
            "Con TW bajo y pendiente pronunciada el barril puede no llegar a "
            "llenarse y el control de salida no gobierna igualmente; "
            "verificar que el punto donde el control de salida GOBIERNE sea "
            "uno donde la hipotesis de seccion llena tenga sentido fisico. "
            "ESTA VERIFICACION NO ES SOLO DE ESTE CRITERIO: es tambien la "
            "condicion de uso que HDS-5 impone a h_o = (dc + D)/2, el otro "
            "termino de la misma ecuacion, y el proyecto la aplicaba sin "
            "recogerla (NOR-HDS-05). " + H_O_NUMERAL + " la escribe asi: "
            + "; ".join(f"<<{cita}>>" for cita in H_O_CONDICION_TEXTO)
            + ". La premisa entraba dos veces por dos puertas -- este criterio "
            "la ADOPTA y h_o la SUPONE -- y hasta E-A no se comprobaba por "
            "ninguna. Desde E-A (2026-09-21) SE COMPRUEBA: el perfil de la "
            "lamina de agua por paso directo (`M4.perfil_lamina`) mide la "
            "longitud a seccion llena en cada punto y el paso 4.3c juzga con "
            "ella la primera condicion (lleno en mas de la mitad de la "
            "longitud, el criterio 'fraccion_llena_mayor_parte' [A]); bajo HW/D < 0.75 la "
            "aproximacion se sustituye por el remanso (paso 4.3d). Lo que "
            "queda declarado, y no verificado, es lo PROPIO de este criterio: "
            "que el termino de friccion de H se forme con V y R de la seccion "
            "llena aunque el perfil mida que el barril no llena. La pag. 3.12 "
            "del HDS-5 lo avala hasta HW = 0.75D («adequate results»), y por "
            "debajo el remanso ya no usa H"),
        resolucion=Libre(
            que_lo_fija="el proyectista: Sec. 4.3 escribe la ecuacion y no "
                        "dice a que seccion pertenecen V y R",
            dominio="declaracion entre seccion llena y tirante normal",
        ),
    ),

    "fraccion_llena_mayor_parte": Criterio(
        valor=0.5,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Fraccion de la longitud del barril a seccion llena por "
                 "encima de la cual se lee que fluye lleno «for most of its "
                 "length» (primera condicion de uso de h_o, HDS-5 pag. 3.24)",
        justificacion="Desde E-A el perfil de la lamina (M4, paso 4.3c) MIDE "
                      "la longitud a seccion llena, y juzgar la primera "
                      "condicion de uso de h_o exige decir cuanto es «la mayor "
                      "parte». La fuente escribe la palabra y no el numero: "
                      "«most» es la mayoria --mas de la mitad-- y esa es la "
                      "lectura adoptada, declarada en el registro con lo que "
                      "juega en contra (citas.INTERPRETACION_MAYOR_PARTE). Es "
                      "[A] y no [N] porque la palabra admite lecturas mas "
                      "exigentes («casi toda»), y una lectura con alternativas "
                      "es una eleccion con ventana. Sensibilidad: de 0.5 (la "
                      "mitad) a 0.9 («casi toda»); solo mueve el ROTULO del "
                      "veredicto del paso 4.3c, nunca una magnitud: la "
                      "consecuencia de fallar la condicion la fija la pag. "
                      "3.12 (la aproximacion vale hasta HW/D = 0.75, y bajo "
                      "0.75 el remanso), no esta fraccion. Se compara en "
                      "estricto: la fraccion llena tiene que SUPERAR el valor",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, num. 3.3.3, pag. impresa "
               "3.24 (cita HDS5_3ED.3.3.3#HO): «can only be used if the "
               "barrel flows full for most of its length». La pag. impresa "
               "3.12 relaja la condicion («works best when the barrel flows "
               "full over at least part of its length»; «adequate results "
               "... down to a headwater of 0.75D»)",
        sensibilidad=(0.5, 0.9),
        resolucion=Libre(
            que_lo_fija="el proyectista: la fuente escribe «most» y no un "
                        "numero, y la pag. 3.12 de la misma fuente relaja la "
                        "condicion a «at least part»",
            dominio="fraccion en (0, 1]",
        ),
    ),

    "esviaje_max_grados": Criterio(
        # --- T-6 --- (punto 4 de su prompt). TRES COSAS CAMBIAN, y las tres
        # sobre la ficha que dejo el cierre de C10 (PC-32, ficha C10-03):
        #
        #   1. TIENE VALOR, 45 grados, y deja de ser `opcional`. Hasta T-6
        #      era un [A] sin valor que solo actuaba si el proyectista lo
        #      declaraba; el cierre decia «ninguna fuente de normas/ fija un
        #      esviaje maximo» y era cierto del esviaje DEL BARRIL. Lo que no
        #      se habia leido es el num. 5.4.2 del HDS-5, que da un maximo
        #      practico de unos 45 grados para el esviaje DE LA EMBOCADURA y
        #      explica cuando los dos angulos coinciden (ver `justificacion`).
        #   2. LA VENTANA ES (45, 60), no el dominio fisico entero (0, 90).
        #   3. SUPERARLO ES AVISO, NO BLOQUEO. `M7.factor_esviaje` ya no lanza
        #      `DatoInvalidoError`: el esviaje es un dato de entrada medido
        #      (regla 2 de la cadena T), y un dato que supera una adopcion
        #      del proyecto se SEÑALA, no se rechaza. Lo emite la
        #      verificacion G3 de 7.B con veredicto INDICADOR.
        #
        # NIVEL MEDIDO: la corrida de perfil lo invoca en M7 (G3) para todo
        # punto que llega a 7.B.
        valor=45.0,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Esviaje maximo, en grados, por encima del cual el cruce "
                 "se señala para revision en planta (aviso, no bloqueo)",
        justificacion="Decide a partir de que esviaje del cruce la memoria "
                      "AVISA. No acota el calculo: 1/cos(esviaje) se aplica "
                      "igual por encima del valor, y la unica guardia que "
                      "detiene es la NUMERICA de `tolerancias."
                      "COS_ESVIAJE_MIN` (PC-32). El esviaje es un dato de "
                      "entrada -- lo mide la topografia -- y el Manual del "
                      "MTC dice que la ubicacion en planta ideal es la que "
                      "sigue la direccion de la corriente (num. 4.1.1.3.2, "
                      "cita MC_HHD.4.1.1.3.2), de modo que un conducto "
                      "esviado no es un defecto; el mismo numeral admite "
                      "desplazar la ubicacion natural acondicionando el "
                      "cauce a la entrada y a la salida, que es la salida "
                      "cuando el esviaje resulta excesivo. Ninguna fuente "
                      "fija un esviaje maximo del barril. La mas cercana es "
                      "el HDS-5 num. 5.4.2 (pag. impresa 5.13, cita "
                      "HDS5_3ED.5.4.2#MAXIMO_PRACTICO): el esviaje de la "
                      "EMBOCADURA -- el angulo de la cara del conducto con "
                      "la normal al barril -- va de cero a un maximo "
                      "practico de unos 45 grados, limite que la fuente "
                      "atribuye a la dificultad de la transicion del flujo "
                      "del cauce al conducto; y añade que un barril esviado "
                      "suele tener tambien la embocadura esviada porque los "
                      "cabezales se construyen paralelos al eje de la via "
                      "para no alabear el terraplen. Con esa disposicion "
                      "-- la que este proyecto supone: la longitud de 7.B se "
                      "mide con los taludes paralelos a la via -- el esviaje "
                      "de la embocadura es el del barril, y el maximo "
                      "practico de 45 grados le alcanza. Es una ANALOGIA "
                      "que depende de una disposicion constructiva, y por "
                      "eso el criterio es [A] y no [C]. El segundo "
                      "argumento es la longitud resultante: el factor "
                      "1/cos vale 1.41 a 45 grados y 2.00 a 60, o sea que "
                      "entre los dos extremos de la ventana el conducto "
                      "pasa de un 41 % a un 100 % mas largo que el cruce a "
                      "escuadra. Sensibilidad (45, 60): 45 es el maximo "
                      "practico de la fuente y el valor adoptado; 60 es el "
                      "extremo en que el conducto duplica su longitud, "
                      "donde el aviso llegaria ya tarde. El script de "
                      "topografia del proyecto avisa con el mismo umbral "
                      "(pide revisar en planta todo esviaje mayor de 45 "
                      "grados). Un "
                      "esviaje sobre el maximo es ademas la firma del error "
                      "de convencion que docs/contrato_entradas.md §5 "
                      "describe: un angulo copiado de un expediente que lo "
                      "mide desde el eje de la via",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), num. 5.4.2 'Skewed Inlets', "
               "pag. impresa 5.13 (PDF 149), cita "
               "HDS5_3ED.5.4.2#MAXIMO_PRACTICO, POR ANALOGIA del esviaje de "
               "la embocadura al del barril bajo cabezal paralelo a la via; "
               "num. 5.4.1 'Skewed Barrels', pag. impresa 5.12 (PDF 148), "
               "para la definicion del angulo; Manual de Hidrologia, "
               "Hidraulica y Drenaje (MTC), num. 4.1.1.3.2 'Ubicacion en "
               "planta', pag. impresa 71 (PDF 74). El DG-2018 num. "
               "502.03.03, pag. impresa 220 (PDF 221), es de intersecciones "
               "entre carreteras y no acota una obra de drenaje",
        reemplazado_por="El esviaje maximo que la solucion constructiva del "
                        "cruce admita (cabezales y aletas esviados o "
                        "terraplen alabeado, HDS-5 Figura 5.16), decidido "
                        "en los planos",
        sensibilidad=(45.0, 60.0),
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre la solucion constructiva del "
                        "cruce; la fuente da un maximo practico de la "
                        "embocadura, no del barril",
            dominio="grados sexagesimales, entre el maximo practico del "
                    "HDS-5 (45) y el esviaje que duplica la longitud (60)",
        ),
    ),

    "borde_libre_y_sobre_d_max": Criterio(
        valor=Y_SOBRE_D_MAX,        # el 0.75 que resulta del 25 % recomendado
        # NIVEL MEDIDO por las dos corridas de `tests/test_nivel_medido.py`:
        # V1 corre en el alcance de perfil y lee este criterio.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Relacion de llenado maxima y/D (o y/H) que el proyecto "
                 "aplica como umbral duro en V1: el complemento del borde "
                 "libre minimo adoptado",
        justificacion="Decide el borde libre que el proyecto exige de verdad. "
                      "El Manual escribe el borde libre como recomendacion: "
                      "un minimo del 25 % de la altura, diametro o flecha de "
                      "la estructura, del que el 0.75 es el complemento "
                      "aritmetico. Verificar el borde libre es una exigencia "
                      "del numeral; aplicar la cifra recomendada como rechazo "
                      "de un escalon de diametro es una adopcion del "
                      "proyectista, y por eso lleva etiqueta propia y ventana. "
                      "El valor por defecto es el recomendado, de modo que sin "
                      "tocar este criterio el calculo hace lo que hacia. Solo "
                      "se puede endurecer: V1 rechaza con DatoInvalidoError "
                      "una relacion de llenado mayor que 0.75, porque relajar "
                      "una recomendacion de la fuente no es ejercer una "
                      "adopcion sino salirse de lo que la fuente concede. "
                      "Sensibilidad: con y/D = 0.70 un tubo de 0.90 m que "
                      "cumple con 0.75 deja de cumplir con 0.65 y el diseno "
                      "sube de escalon; la direccion de endurecer es siempre "
                      "la segura (mas diametro, mas borde libre). A seccion "
                      "llena no hay borde libre que medir y el veredicto se "
                      "apoya en la exigencia del mismo parrafo, no en esta "
                      "cifra",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.7 b) 'Borde libre', pag. "
               "impresa 79 (PDF 82): recomienda como minimo el 25 % de la "
               "altura, diametro o flecha de la estructura. La cifra vive "
               "como [N] en constantes_normativas.Y_SOBRE_D_MAX; aqui vive "
               "la adopcion de aplicarla como umbral duro",
        reemplazado_por="Un borde libre distinto que el proyectista fije con "
                        "razon escrita, siempre mayor o igual que el 25 % "
                        "recomendado; o una exigencia normativa que lo "
                        "convierta en [N] sin recomendacion de por medio",
        # Ventana NUMERICA porque sus dos extremos existen sin inventar
        # nada: el techo es el 0.75 que la fuente recomienda (solo se puede
        # endurecer) y el piso es el dominio fisico de una relacion de
        # llenado. Asi la PUERTA rechaza 0.9 antes de correr, y no solo el
        # consumidor (auditor de C05).
        sensibilidad=(0.0, Y_SOBRE_D_MAX),
        resolucion=Libre(
            que_lo_fija="el proyectista, a partir de la recomendacion del "
                        "num. 4.1.1.3.7 b); el 0.75 es el valor por defecto",
            dominio="0 < y/D <= 0.75",
        ),
    ),
    "velocidad_minima_autolimpieza_m_s": Criterio(
        valor=V_MIN,                # el 0.25 m/s que la fuente recomienda
        # NIVEL MEDIDO por las dos corridas de `tests/test_nivel_medido.py`:
        # V2 corre en el alcance de perfil y lee este criterio.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Velocidad minima de autolimpieza, en m/s, que el proyecto "
                 "aplica como umbral duro en V2",
        justificacion="Decide el piso de velocidad que el proyecto exige de "
                      "verdad. El Manual manda verificar que la velocidad "
                      "minima no produzca sedimentacion, y la cifra del piso "
                      "la escribe como recomendacion (0.25 m/s). Verificar es "
                      "exigencia del numeral; aplicar la cifra recomendada "
                      "como rechazo de un escalon es una adopcion del "
                      "proyectista, con etiqueta propia y ventana. El valor "
                      "por defecto es el recomendado, de modo que sin tocar "
                      "este criterio el calculo hace lo que hacia. Solo se "
                      "puede endurecer: V2 rechaza con DatoInvalidoError un "
                      "piso menor que 0.25 m/s, porque relajar una "
                      "recomendacion no es ejercer una adopcion. "
                      "Sensibilidad: el piso casi nunca gobierna (haria falta "
                      "una pendiente del orden de 0.00006 para violarlo con "
                      "0.25 m/s); subirlo a 0.35 m/s empieza a rechazar "
                      "tramos de pendiente muy baja, y la direccion de "
                      "endurecer es la segura frente a la sedimentacion",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.6, parrafo posterior a la "
               "Tabla N 10, pags. impresas 76-77 (PDF 79-80): manda "
               "verificar la velocidad minima y recomienda que sea igual a "
               "0.25 m/s. La cifra vive como [N] en "
               "constantes_normativas.V_MIN; aqui vive la adopcion de "
               "aplicarla como umbral duro",
        reemplazado_por="Un piso distinto que el proyectista fije con razon "
                        "escrita, siempre mayor o igual que el recomendado; "
                        "o una exigencia normativa que lo convierta en [N]",
        sensibilidad=("0.25 m/s, la velocidad minima que la fuente recomienda "
                      "y que el proyecto adopta por defecto",
                      "cualquier piso mayor que declare el proyectista: la "
                      "recomendacion es un minimo y solo se puede endurecer. "
                      "Un valor menor se rechaza en V2"),
        resolucion=Libre(
            que_lo_fija="el proyectista, a partir de la recomendacion del "
                        "num. 4.1.1.3.6; 0.25 m/s es el valor por defecto",
            dominio="V >= 0.25 m/s",
        ),
    ),
    "HW_D_max": Criterio(
        valor=1.5,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Relacion maxima de carga a la entrada sobre diametro",
        justificacion="Decide la relacion maxima de carga a la entrada sobre "
                      "diametro, HW/D, y es adopcion del proyectista sobre "
                      "una banda de practica ajena, no un valor que alguna "
                      "fuente fije. La fuente (HDS-5, num. 2.2.5 d; texto "
                      "literal en `fuente`) describe lo que imponen las "
                      "agencias viales de los Estados Unidos -- limites HW/D "
                      "que varian por el pais, comunmente entre 1.0 y 1.5 -- "
                      "y su unico imperativo tiene por sujeto la restriccion "
                      "que cada agencia impone, no el rango. Lo que no "
                      "resuelve: no prescribe HW/D alguno, y en el Peru la "
                      "agencia es el MTC, cuyo Manual tampoco lo fija -- no "
                      "hay restriccion de agencia que seguir. Por eso elegir "
                      "un numero dentro de la banda es decision del "
                      "proyectista, [A] con su sensibilidad, y no la lectura "
                      "de una tabla ni un [C]: la fuente no cubre este vacio, "
                      "lo describe. Se adopta 1.5, el extremo superior de la "
                      "banda descrita -- el menos restrictivo de los dos: "
                      "admite mas embalse a la entrada, no menos --, porque "
                      "el control gobernante del embalse en este proyecto no "
                      "es este umbral sino V5 (remanso dentro del derecho de "
                      "via), que es el que de verdad protege a terceros. "
                      "Sensibilidad (1.2, 1.5): es un subrango deliberado, la "
                      "mitad alta de la banda descrita (1.0, 1.5), y se deja "
                      "dicho para que nadie la confunda con lo que la fuente "
                      "describe. Reglas de aplicacion: lo consume "
                      "`M5.v4b_relacion_hw_d`, y el HW que se divide entre D "
                      "es el del control gobernante, no el del control de "
                      "entrada -- lo que la fuente acota es el embalse real "
                      "aguas arriba, y tomar el HWi/D de la Tabla A.1 cuando "
                      "gobierna el control de salida daria un numero menor "
                      "que el embalse que la obra produce",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, num. 2.2.5 'Allowable "
               "Headwater' (arranca en la pag. impresa 2.9), apartado "
               "d. 'Agency Constraints', pag. impresa 2.10 (PDF 72). Texto "
               "literal: <<Some state or local highway agencies place limits "
               "on the headwater produced by a culvert. For example, the "
               "headwater depth may not be allowed to exceed the barrel "
               "height or some multiple of the barrel height, expressed as "
               "HW/D. The allowable HW/D ratio varies throughout the "
               "country, but commonly ranges from 1.0 to 1.5. Although very "
               "low HW/D constraints will severely limit the flexibility "
               "inherent in culvert design, they must be followed unless a "
               "design exemption is granted.>> "
               "LA PAGINA ANTERIOR ERA FALSA y la cita se daba por CERRADA: "
               "este campo decia 'Sec. 2.2.5, pag. 2.14', y la pag. impresa "
               "2.14 (PDF 76) trata de espolones de escombros (Figura 2.8) y "
               "de seguridad vial (num. 2.3.3). Verificado contra el PDF en "
               "la sesion de C06. El pasaje ademas NO EXISTE en la otra copia "
               "de HDS-5 que hay en normas/ (la edicion de 1985): el rango es "
               "exclusivo de la 3a ed.",
        sensibilidad=(1.2, 1.5),
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre una BANDA DE PRACTICA AJENA. "
                        "NO es `EnRango`, aunque la Sec. 4.3 del plan lo "
                        "ponga de ejemplo: el num. 2.2.5 d) del HDS-5 "
                        "DESCRIBE lo que imponen las agencias viales de "
                        "EE.UU. y no prescribe HW/D alguno (NOR-HDS-02, "
                        "conflicto vinculante #1 del plan). Un rango con "
                        "cita normativa aqui seria la cita falsa que ese "
                        "hallazgo vino a retirar",
            dominio="adimensional > 0",
        ),
    ),

    "resguardo_HW_subrasante": Criterio(
        valor="segun_CBR",          # 0.60 / 0.80 / 1.00 / 1.20 m
        nivel=NIVEL_PERFIL,
        etiqueta="N->",
        forma=FORMA_STR,
        concepto="Resguardo entre nivel de agua a la entrada y subrasante",
        justificacion="Decide con que resguardo se separa el nivel de agua a "
                      "la entrada (HW) de la subrasante. La fuente (Manual de "
                      "Suelos MTC, num. 4.5.4, con la tabla repetida en "
                      "9.1(3)) da una tabla de resguardo por CBR cuyo objeto "
                      "es la separacion frente al nivel freatico. Lo que no "
                      "resuelve es el caso de esta verificacion: un nivel "
                      "transitorio de avenida no es un freatico permanente. "
                      "Se aplica la tabla por analogia -- por eso [N->] -- "
                      "por ser el unico parametro normativo nacional que "
                      "protege la subrasante de la saturacion, y la analogia "
                      "se declara en la memoria. Que la analogia quede del "
                      "lado seguro es plausible, no demostrado: el resguardo "
                      "del num. 4.5.4 protege del ascenso capilar continuo de "
                      "un freatico permanente, mientras que un HW de avenida "
                      "moja el terreno durante horas, por un mecanismo "
                      "distinto, y puede subir por encima del freatico; que "
                      "el resguardo dimensionado para el primer mecanismo "
                      "baste para el segundo no se deduce del numeral ni de "
                      "ningun otro del Manual de Suelos. La adopcion se "
                      "sostiene entonces en la ausencia de alternativa "
                      "nacional, no en un conservadurismo demostrado, y asi "
                      "se imprime. Cuando gobierna: la verificacion compara "
                      "niveles (la cota de fondo de la entrada mas la carga, "
                      "contra la cota de subrasante menos el resguardo de la "
                      "fila de CBR del punto), de modo que decide la "
                      "aceptacion de un diametro cuando el relleno sobre la "
                      "entrada es bajo o cuando el CBR de la subrasante cae "
                      "en una fila de resguardo mayor (de 0.60 m con CBR de "
                      "20 % o mas, hasta 1.20 m con CBR menor de 3 %). En "
                      "ese caso el remedio no es solo otro diametro: el "
                      "mismo parrafo de la fuente ofrece subdrenes, capas "
                      "drenantes o elevar la rasante (cita MS.4.5.4), y la "
                      "elevacion necesaria la calcula el tamizado de la Fase "
                      "7. En el corredor del repositorio no descarta ningun "
                      "diametro: el punto mas ajustado de la corrida de "
                      "perfil con los datos externos completos, A-01, cumple "
                      "con 0.108 m de margen",
        fuente="Manual de Suelos MTC, numeral 4.5.4 (pags. 41-42) y 9.1(3) "
               "(pags. 89-90), que repite la tabla en el capitulo de "
               "estabilizacion",
        verificacion_pendiente="La equivalencia entre saturacion permanente "
                               "(el mecanismo del 4.5.4) y mojado transitorio "
                               "por avenida (el de V4) queda sin demostrar. "
                               "Cerrarla exige una fuente que trate el "
                               "remanso de avenida sobre la subrasante, no una "
                               "lectura mas del mismo numeral",
        resolucion=Libre(
            que_lo_fija="la tabla de resguardo por CBR del Manual de Suelos, "
                        "aplicada POR ANALOGIA (el num. 4.5.4 regula la "
                        "separacion frente al freatico, no frente a un nivel "
                        "de avenida). NO es `DeTabla` todavia, aunque la "
                        "Sec. 4.3 del plan ponga `resguardo(CBR)` de "
                        "ejemplo: esa tabla vive como escalares [N] en "
                        "`constantes_normativas.py` y no esta transcrita "
                        "como `TablaNormativa` en el registro, de modo que "
                        "no hay tabla que la ventana pueda mostrar entera",
            tabla_pendiente="Manual de Suelos MTC num. 4.5.4 (pags. 41-42) "
                            "y 9.1(3) (pags. 89-90), tabla de resguardo por "
                            "CBR",
        ),
    ),

    # -----------------------------------------------------------------------
    # VC1 -- el borde libre del CANAL, que no es el borde libre de V1
    # -----------------------------------------------------------------------
    # POR QUE ES CRITERIO DE CORREDOR Y NO COLUMNA [S] POR PUNTO. La pregunta
    # se decide con la regla de CLAUDE.md que separa [S] de [A]: «un [A] se
    # defiende con un rango de sensibilidad porque hubo eleccion; un [S] no
    # tiene rango que elegir y se defiende con la trazabilidad de la lectura».
    # Aqui hay banda y no hay lectura: el levantamiento de los seis cruces
    # midio cota de fondo, seccion trapecial y CORONACION --- y la coronacion
    # SI es [S] y SI es columna, `cota_coronacion_canal` ---, pero no midio
    # ningun borde libre, porque un borde libre no se mide: se adopta. Es el
    # resguardo que el proyecto decide dejar sin usar bajo la coronacion, y esa
    # decision es la misma en los seis cruces porque sale de una sola
    # adopcion, no de seis mediciones. Ponerlo por punto invitaria ademas a
    # aflojarlo justo donde aprieta, que es la direccion insegura.
    #
    # POR QUE [A] Y NO [N->], que es el vecino con el que se confunde. El
    # precedente de [N->] en este archivo es 'resguardo_HW_subrasante': un
    # numeral que regula el freatico, aplicado por analogia a un nivel de
    # avenida. Alli, CONCEDIDA la analogia, la fuente determina el numero ---
    # la tabla del 4.5.4 entra con el CBR y da 0.60 / 0.80 / 1.00 / 1.20 ---.
    # Aqui no: concedida la analogia, la fuente sigue dando una BANDA y
    # ninguna regla para elegir dentro de ella. Quedan dos saltos y no uno, y
    # el de afuera es una eleccion. [N->] la esconderia; [A] la publica con su
    # ventana, que es para lo que existe la ventana.
    #
    # EL SIGNO DE LA VENTANA, escrito porque la intuicion apunta al reves. El
    # borde libre se RESTA de la coronacion: moverlo hacia 0.50 BAJA la cota
    # admisible y ACERCA el punto al incumplimiento. Quien lo declare esta
    # eligiendo cuanta exigencia se pone a si mismo, no cuanta holgura se
    # concede. Por eso el valor adoptado es el extremo superior.
    "borde_libre_canal_m": Criterio(
        valor=0.50,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Borde libre del canal: resguardo bajo su coronacion que el "
                 "agua embalsada por la alcantarilla no puede invadir (VC1)",
        justificacion=(
            "Decide el borde libre del canal que VC1 protege: el resguardo "
            "bajo su coronacion que el agua embalsada por la alcantarilla no "
            "puede invadir. El requisito de verificarlo es de la Sec. 2.3 de "
            "la hoja de ruta (ver `fuente`), no de un numeral del MTC. Lo que "
            "el corpus nacional no resuelve, verificado por ausencia sobre "
            "sus 225 paginas (`citas.SIN_BORDE_LIBRE_DE_CANAL`): el Manual no "
            "fija borde libre para un canal -- «borde libre» aparece en dos "
            "apartados y ninguno tiene por objeto un canal: el 4.1.1.3.7 b) "
            "es de alcantarillas y es relativo (>= 25 % de la altura del "
            "barril), y el 4.1.1.4.1 e) es de badenes y mide contra la "
            "superficie de rodadura --; tampoco aparecen «faja marginal» ni "
            "«terceros». Se adopta el par 0.30-0.50 m del num. 4.1.1.4.1 e) "
            "por ser el unico resguardo absoluto que el corpus nacional "
            "escribe para el mismo concepto, y la analogia se declara: alli "
            "el datum superior es la calzada -- desbordar afecta la propia "
            "plataforma -- y aqui es la coronacion -- desbordar inunda "
            "parcela de terceros. Dentro de la banda se adopta 0.50 m, el "
            "extremo superior, porque el borde libre se resta de la "
            "coronacion y el extremo superior es el conservador: baja la cota "
            "admisible y endurece VC1 -- direccion contraria a la de la "
            "adopcion de riesgo de la Tabla N 02, donde adoptar el maximo "
            "recomendado afloja. Sensibilidad: la fuente no da regla para "
            "elegir dentro de la banda -- va en texto corrido, sin tabla, y "
            "no es funcion del caudal, de la luz ni de la velocidad --, por "
            "eso la eleccion es del proyectista y el criterio es [A]; la "
            "banda misma es [N] y vive en "
            "`constantes_normativas.BORDE_LIBRE_BADEN_RANGO_M`"),
        fuente="MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.4.1 e) «Borde libre», "
               "pag. impresa 85 (PDF 88), bajo «4.1.1.4  BADENES». El "
               "REQUISITO que obliga a verificarlo es de la Sec. 2.3 de la "
               "hoja de ruta («No puede alterar la rasante hidraulica ni el "
               "borde libre del canal»), no de un numeral del MTC",
        sensibilidad=BORDE_LIBRE_BADEN_RANGO_M,
        verificacion_pendiente=(
            "El borde libre que el propio canal adopto en SU proyecto. Lo "
            "fija la entidad que lo opera (ANA / Junta de Usuarios del Bajo "
            "Piura) y seria el valor exacto en vez de uno analogo: si el "
            "canal se diseño con 0.30 m, exigirle 0.50 a la alcantarilla es "
            "mas duro que su propio proyecto; si se diseño con mas de 0.50, "
            "esta adopcion se queda corta y la analogia deja de ser "
            "conservadora. Es la unica de las dos direcciones que importa, y "
            "no se puede resolver leyendo otra vez el mismo numeral"),
        resolucion=Libre(
            que_lo_fija="el proyectista, dentro de la banda 0.30-0.50 m que "
                        "el num. 4.1.1.4.1 e) recomienda PARA UN BADEN. NO es "
                        "`EnRango`: aquel tipo referencia (tabla, fila, "
                        "columna) del registro, y este par no es una tabla "
                        "--- va en texto corrido --- de modo que no hay tabla "
                        "que la ventana pueda pintar. Lo que la ventana "
                        "muestra es la banda por `sensibilidad`, y lo que el "
                        "proyectista tiene que saber al moverse dentro de "
                        "ella es el SIGNO: hacia 0.50 la verificacion se "
                        "endurece",
            dominio="0.30 <= borde libre <= 0.50 m",
        ),
    ),

    "TW_receptor": Criterio(
        # SIGUE VACIO A PROPOSITO, Y DESDE S20 POR OTRA RAZON. Hasta S20 era
        # la UNICA puerta del TW y por eso detenia toda corrida: el
        # procedimiento de Sec. 1.3 no existia en src/ (SIS-B-04). Hoy existe
        # -- `M3.tw_seccion_1_3` -- y este criterio quedo donde le corresponde:
        # la ULTIMA puerta, la que se abre cuando el expediente no aporta ni
        # `cota_TW`, ni `Q_receptor_m3s`, ni la seccion del receptor. Con
        # 'seccion_receptor' declarado, ninguna corrida lo invoca, y por eso
        # no aparece en la memoria: `reporte_criterios(solo_usados=True)`
        # imprime lo que el calculo consumio.
        #
        # NO SE DECLARA, y es deliberado: declararlo seria volver a poner un
        # TW a mano donde Sec. 1.3 dice «se calcula, no se mide». Su ficha
        # sigue aqui porque el dia que un punto descargue a un receptor del
        # que no se sepa ni el caudal ni la seccion, esta es la puerta que
        # tiene que detener la corrida en vez de inventar un nivel.
        valor=None,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        # LA VENTANA DE ESTE CRITERIO SON LOS DOS ESCENARIOS DEL PASO 3 de
        # Sec. 1.3, y no es una analogia: son literalmente las dos opciones
        # que la hoja de ruta ofrece cuando no hay caudal documentado del
        # receptor, que es exactamente la situacion en la que esta puerta se
        # abre. Es simbolica y no numerica porque un TW no tiene banda de
        # practica: tiene dos escenarios acotados, y lo que se declara es en
        # cual se esta. Se escribe aunque el criterio siga vacio: la ventana
        # es parte de la ficha, no del valor, y sin ella ni la GUI ni la CLI
        # podrian declararlo en caliente.
        sensibilidad=("salida libre (TW = 0): el receptor no aporta lamina "
                      "sobre el fondo de la salida",
                      "receptor a seccion llena: el agua llega a la corona "
                      "del bordo del dren",
                      "nivel documentado por la ANA / Junta de Usuarios para "
                      "el periodo de retorno de diseño"),
        concepto="Nivel de agua en el cuerpo receptor durante la avenida",
        justificacion="No se mide: se calcula con Manning en el receptor usando "
                      "su propio caudal de diseno. Sin ese dato se adoptan dos "
                      "escenarios acotados (salida libre / seccion llena)",
        fuente="PENDIENTE: ANA / Junta de Usuarios del Bajo Piura",
        reemplazado_por="Caudal de diseno documentado del dren o canal receptor",
        # `Libre` Y NO `DeEnsayo`, y el cambio lo trajo la propia Sec. 1.3.
        # Mientras este criterio fue la UNICA puerta del TW, su resolucion
        # decia la verdad: el numero saldria de un dato de la ANA. Hoy ese
        # dato entra por otro sitio -- la columna `cota_TW`, o el caudal del
        # receptor con su seccion -- y lo que queda aqui es la ultima puerta,
        # la que se abre cuando no hay ninguno de los tres: entonces lo que
        # se declara no es una lectura, es EN CUAL DE LOS DOS ESCENARIOS
        # ACOTADOS del paso 3 se esta. Eso es una eleccion, y la invariante de
        # este archivo lo exige: un `de_ensayo` con ventana es una
        # contradiccion. La lectura de la ANA no se pierde: es el
        # `reemplazado_por`, y sigue siendo lo que cierra esto de verdad.
        resolucion=Libre(
            que_lo_fija="el proyectista, eligiendo escenario, cuando el "
                        "expediente no aporta ni el nivel del receptor "
                        "(`cota_TW`) ni su caudal de diseño con la seccion "
                        "para correr Manning (Sec. 1.3, pasos 1 y 2)",
            dominio="m >= 0 sobre el fondo de la salida; 0 es salida libre",
        ),
    ),

    # El DATO que el paso 2 de Sec. 1.3 necesita, y que la hoja de ruta no
    # entrega: la seccion del receptor. Sin ella el paso 2 no es una formula
    # que falte, es una geometria que nadie declaro.
    "seccion_receptor": Criterio(
        # SECCION ADOPTADA A NIVEL DE PERFIL, con la ventana de cada campo
        # en `sensibilidad`. Es la unica de las declaraciones de esta sesion
        # que describe una obra de TERCEROS -- el dren colector de la Junta
        # de Usuarios --, y por eso su `verificacion_pendiente` es la mas
        # exigente: mientras no exista el levantamiento, la memoria tiene que
        # decir que el nivel del receptor es una adopcion.
        #
        # QUE NO GOBIERNA ESTA ADOPCION, que es lo primero que hay que mirar
        # antes de leerla como un numero peligroso: en los puntos cuyo CSV
        # trae `cota_TW`, la via 2 de Sec. 1.3 gana y este criterio ni se
        # invoca. Solo entra donde el expediente aporta el CAUDAL del
        # receptor y no su nivel, que es la situacion que Sec. 1.3 describe.
        valor={"b_m": 2.0, "z_HV": 1.5, "S": 0.0008, "n": 0.030,
               "altura_total_m": 1.80},
        nivel=NIVEL_PERFIL,
        # VENTANA POR CAMPO, ESTRUCTURADA Y EVALUADA (EXT-V-05). Hasta EXT-1
        # estaba escrita en prosa -- «n: 0.025 a 0.035 (canal en tierra con
        # vegetacion estacional)» -- y por eso caia en la forma SIMBOLICA de
        # `_verificar_sensibilidad`: se imprimia y no se evaluaba. La
        # auditoria externa midio lo que eso dejaba pasar: `n='0.03'` llegaba
        # a M3 como texto y salia TypeError, `n=True` valia 1, un tirante x5
        # se aceptaba y una clave con errata se ignoraba. Un solo par
        # (min, max) no puede acotar cinco magnitudes distintas, y la
        # respuesta no es renunciar a la ventana sino darle la forma del
        # valor: un par POR CAMPO, que `_verificar_dict` evalua clave a clave.
        #
        # LO QUE LA PROSA DECIA Y SIGUE VALIENDO, ahora fuera del dato: b_m y
        # z_HV son los del dren colector de la red del Bajo Piura (talud de
        # dren en suelo fino); S, la de una llanura de riego; n, el de un canal
        # en tierra con vegetacion estacional. El campo que mas mueve el
        # resultado es `altura_total_m`, y solo en la via 4 (escenarios
        # acotados): es el que fija el TW del escenario "receptor a seccion
        # llena". En la via 3 lo que gobierna es la terna b/z/n/S a traves de
        # Manning, y el mas sensible de los cuatro es el n: MEDIDO sobre esta
        # seccion con el caudal de A-01 (2.00 m3/s), pasar de n = 0.025 a
        # n = 0.030 sube el tirante normal de 0.8258 a 0.9082 m, un +10.0 %,
        # y esos 82 mm se trasladan al TW milimetro a milimetro.
        sensibilidad={"b_m": (1.5, 3.0),             # m
                      "z_HV": (1.0, 2.0),            # H:V
                      "S": (0.0005, 0.0015),         # m/m
                      "n": (0.025, 0.035),
                      "altura_total_m": (1.2, 2.5)}, # m
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Seccion transversal del cuerpo receptor (dren o canal) en "
                 "el punto de descarga, con su pendiente y su n de Manning: "
                 "b_m (solera), z_HV (talud), S, n y altura_total_m "
                 "(profundidad de la seccion, del fondo a la corona del "
                 "bordo)",
        justificacion="Decide la seccion transversal con que se resuelve el "
                      "paso 2 de la Sec. 1.3 de la hoja de ruta mientras no "
                      "exista el levantamiento del receptor. La fuente (Sec. "
                      "1.3) establece que TW se calcula y no se mide, y da "
                      "tres pasos; el segundo aplica Manning en la seccion "
                      "del receptor con el caudal de la columna "
                      "`Q_receptor_m3s` (Sec. 1.2) y su pendiente -- la "
                      "formula es la misma de Manning que ya usa M3 y el "
                      "caudal esta. Lo que no resuelve: la seccion misma. Ni "
                      "Sec. 1.1 ni Sec. 1.2 la traen, la hoja de ruta no la "
                      "describe y no hay norma que la fije, porque es la "
                      "geometria de una obra de terceros -- el dren de la "
                      "Junta de Usuarios -- que hay que ir a levantar. Se "
                      "adopta declarar aqui la seccion completa (b_m, z_HV, "
                      "S, n y altura_total_m) y bloquear mientras falte, en "
                      "vez de aproximarla: el TW entra en el control de "
                      "salida y de ahi al HW, y el HW decide V4 (carga bajo "
                      "la subrasante) y V4b; una seccion inventada mueve la "
                      "cota de agua del receptor y con ella el diametro de la "
                      "alcantarilla, sin que nada en la memoria diga de donde "
                      "salio. altura_total_m no es decorativa: acota el "
                      "segundo escenario del paso 3 -- receptor a seccion "
                      "llena --, que sin ella no se puede escribir, y la hoja "
                      "de ruta pide cumplir en los dos escenarios. Cuando el "
                      "CSV ya trae `cota_TW`, este criterio no hace nada: esa "
                      "columna es el resultado del paso 2 resuelto fuera (el "
                      "Tablero 3.1 la rotula como calculada por la Sec. 1.3) "
                      "y un dato entregado no se recalcula -- "
                      "`M3.tw_seccion_1_3` la usa y ni siquiera invoca este "
                      "criterio. La sensibilidad declara, campo por campo, "
                      "los rangos plausibles dentro de los que se movera el "
                      "levantamiento, y de donde sale cada banda: b_m 1.5 a "
                      "3.0 m y z_HV 1.0 a 2.0 son los del dren colector de "
                      "la red del Bajo Piura (talud de dren en suelo fino); "
                      "S 0.0005 a 0.0015 m/m, la pendiente de una llanura de "
                      "riego; n 0.025 a 0.035, el de un canal en tierra con "
                      "vegetacion estacional; altura_total_m 1.2 a 2.5 m, la "
                      "profundidad del dren a la corona del bordo",
        fuente="PENDIENTE - levantamiento de la seccion del dren o canal "
               "receptor en el punto de descarga (ANA / Junta de Usuarios "
               "del Bajo Piura). Sec. 1.3 de la hoja de ruta describe el "
               "procedimiento y NO entrega la seccion; Sec. 1.2 no la trae "
               "como columna",
        reemplazado_por="Seccion levantada por punto (si los puntos "
                        "descargan a drenes distintos, deja de ser un "
                        "criterio de corredor y pasa a ser columna del CSV), "
                        "o directamente la `cota_TW` medida, que la hace "
                        "innecesaria",
        verificacion_pendiente="Declarar si los cuatro puntos del corredor "
                               "descargan al MISMO receptor. Un criterio "
                               "unico afirma que si, y esa afirmacion es "
                               "parte de la adopcion: si descargan a drenes "
                               "distintos, un solo juego de b/z/S/n asigna a "
                               "todos la seccion de uno",
        # `Libre`, POR LO MISMO QUE 'talud_terraplen': mientras el criterio
        # estaba vacio su resolucion era `DeEnsayo`, porque el numero iba a
        # salir de un levantamiento. Declarado a nivel de perfil sale de una
        # ELECCION dentro de una banda, y la invariante de este archivo no
        # admite un `de_ensayo` con ventana -- con razon: un dato levantado no
        # tiene rango que elegir. El levantamiento no desaparece: es el
        # `reemplazado_por`, y es lo unico que cierra este criterio de verdad.
        resolucion=Libre(
            que_lo_fija="el proyectista, mientras no exista el levantamiento "
                        "topografico de la seccion del receptor en el punto "
                        "de descarga. La seccion es de una obra de TERCEROS "
                        "-- el dren de la Junta de Usuarios --: ninguna norma "
                        "la fija y este proyecto no la diseña",
            dominio="b_m >= 0, z_HV >= 0, S > 0, n > 0, altura_total_m > 0; "
                    "b_m y z_HV no pueden ser cero a la vez",
        ),
    ),

    "long_max_cuneta": Criterio(
        valor=200.0,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Longitud maxima de cuneta -> espaciamiento de alcantarillas de alivio",
        justificacion="El Manual fija 250 m para region seca y 200 m para region "
                      "muy lluviosa. El regimen normal de Piura es arido, pero el "
                      "evento de diseno relevante es el FEN, durante el cual la "
                      "zona se comporta como region muy lluviosa. Se adopta 200 m",
        # La pagina es la de la cita del registro (MC_HHD_CUNETA, 179); un
        # test la compara con `pagina_impresa` para que no vuelva a quedarse
        # en 178, que era la Tabla Nº 34 del apartado c) (PC-30).
        fuente="Manual MTC, numeral 4.1.2.1 d), pag. 179",
        sensibilidad=(200.0, 250.0),
        resolucion=Libre(
            que_lo_fija="el proyectista, al declarar el regimen de la zona: "
                        "el num. 4.1.2.1 d) da 250 m para region seca y "
                        "200 m para region muy lluviosa, y el evento de "
                        "diseño relevante en Piura es el FEN",
            dominio="m > 0",
            tabla_pendiente="Manual de Hidrologia num. 4.1.2.1 d): los dos "
                            "valores por region no estan transcritos como "
                            "`TablaNormativa` en el registro",
        ),
    ),

    # ----------------------------------------------------------------------
    # --- T-9 --- La cuneta con que la Fase 10 calcula su capacidad (VB2) y la
    # longitud por capacidad (L_hidraulico) cuando no se declara. Cuatro
    # criterios desde las correcciones de la auditoria de T-9.
    #
    # 'seccion_cuneta' NACIO SIN VALOR en la FASE A («es del trazo») y LO TIENE
    # desde la decision A del dueño (2026-11-12): el MINIMO de la Tabla Nº 34
    # para la region que el proyecto ya adopto con `long_max_cuneta` (muy
    # lluviosa por el FEN), con el talud exterior como eleccion [A] declarada.
    # ----------------------------------------------------------------------
    "seccion_cuneta": Criterio(
        valor={"profundidad_m": 0.40,       # m, Tabla Nº 34, muy lluviosa
               "ancho_m": 1.20,             # m, Tabla Nº 34, muy lluviosa
               "talud_exterior_HV": 1.0,    # H:V, eleccion [A] (justificacion)
               "borde_libre_m": 0.0,        # m, la «cuneta llena» del Manual
               # VE-5 (catlic, T9-01): 0 = triangular; > 0 = la trapezoidal
               # de la Tabla Nº 34 para mas de 3000 mm/año (nota «*»).
               "ancho_fondo_m": 0.0},       # m
        # DE PERFIL: lo consume M10, y la Fase 10 corre a perfil (no esta en
        # MODULOS_DIFERIDOS_POR_ALCANCE). Lo MIDE `tests/test_t9_espaciamiento.py`
        # con una corrida de perfil que calcula la capacidad.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        # VENTANA POR CAMPO, y cada banda dice de donde sale (corregida tras la
        # auditoria de T-9, H5: la de la FASE A tenia de piso el minimo de la
        # region SECA, por debajo de la EXIGENCIA de la Tabla Nº 34 para la
        # region que el propio proyecto adopta, y atribuia su techo de ancho a
        # la Tabla 304.12 leyendola al reves):
        #   profundidad_m       0.40 = la profundidad minima de la Tabla Nº 34
        #                       para la region muy lluviosa (1600 a <3000
        #                       mm/año) que `long_max_cuneta` adopta; 0.60 =
        #                       «Elijo una altura H, que sea menor a 0.60m»
        #                       (num. 4.1.2.1 a), pag. impresa 176).
        #   ancho_m             1.20 = el ancho minimo de esa fila; 2.40 m es
        #                       techo ADOPTADO, no de la fuente: la Tabla 304.12
        #                       da inclinaciones MAXIMAS del talud interior (un
        #                       talud mas tendido siempre cumple) y no pone techo
        #                       al ancho; 4 x 0.60 es el talud 1:4 de su fila mas
        #                       exigente a la profundidad maxima.
        #   talud_exterior_HV   H:V del talud exterior, que «por lo general
        #                       coincide con el talud de corte» (DG-2018 num.
        #                       304.11): de 0.10 (1:10, roca fija) a 2.0 (2:1,
        #                       arenas), la Tabla 304.10 para cortes menores de
        #                       5 m (Relacion H:V).
        #   borde_libre_m       0.0 = la «cuneta llena» del num. 4.1.2.1 a); el
        #                       techo de 0.10 m es adopcion del proyecto (la
        #                       fuente no da borde libre para cunetas).
        # VE-7 lote B, B11 (ficha VE5-CAT-02): con fondo (la trapezoidal de
        # la fila de mas de 3000 mm/año) el piso de la profundidad BAJA a
        # 0.30, su minimo (`_PISO_CONDICIONADO`); la triangular sigue en
        # 0.40. La fila que rige la contrasta M10 con la precipitacion del
        # corredor declarada (`M10._contrastar_con_la_tabla_34`).
        sensibilidad={"profundidad_m": (0.40, 0.60),     # m
                      "ancho_m": (1.20, 2.40),           # m
                      "talud_exterior_HV": (0.10, 2.0),  # H:V
                      "borde_libre_m": (0.0, 0.10),      # m
                      # 0 = triangular; 1.20 = el ancho minimo de la fila
                      # (el fondo no puede llegar al ancho). Un fondo entre
                      # 0 y 0.30 lo rechaza M10: la nota «*» de la Tabla Nº
                      # 34 pide 0.30 como minimo (VE-5, T9-01).
                      "ancho_fondo_m": (0.0, 1.20)},     # m
        concepto="Seccion de la cuneta del tramo que descarga en la "
                 "alcantarilla de alivio: profundidad d y ancho a (Figura Nº "
                 "27 del num. 4.1.2.1: el ancho se mide del borde de la "
                 "rasante a la vertical del vertice, a = Z1·d), talud "
                 "exterior (H:V), borde libre bajo el que se calcula la "
                 "capacidad y ancho de fondo: 0 es la TRIANGULAR; mayor que "
                 "0, la TRAPEZOIDAL de la Tabla Nº 34 para mas de 3000 "
                 "mm/año (fondo minimo 0.30 m, VE-5)",
        justificacion="Decide la seccion con que la Fase 10 calcula la "
                      "capacidad de la cuneta (VB2) y, con ella, la longitud "
                      "a la que se agota (L_hidraulico) cuando no se declara. "
                      "VALOR: 0.40 x 1.20 m es el minimo de la Tabla Nº 34 "
                      "(num. 4.1.2.1 c), pag. impresa 178, cita "
                      "MC_HHD.4.1.2.1c#T34) para la region muy lluviosa (de "
                      "1600 a <3000 mm/año), que es la que el proyecto ya "
                      "adopta con 'long_max_cuneta' (200 m por el regimen "
                      "FEN); la fila EXIGE ese minimo («las dimensiones "
                      "mínimas serán»). Como el ancho se mide hasta la "
                      "vertical del vertice, 0.40 m x 1.20 m fija el talud "
                      "INTERIOR Z1 = 3 (1:3); el EXTERIOR no lo fija la tabla: "
                      "el Manual lo hace depender del talud de corte (pag. "
                      "impresa 173) y el DG-2018 (num. "
                      "304.11, cita DG2018.304.11) lo hace coincidir por lo "
                      "general con el talud de corte. Z2 = 1.0 (1:1) es "
                      "ELECCION [A] de este proyecto: el talud mas empinado "
                      "de las filas de suelo fino o arenoso de la Tabla "
                      "304.10 del DG-2018 para cortes menores de 5 m (limo "
                      "arcilloso 1:1, arenas 2:1), que son los suelos del "
                      "corredor, hasta que el EMS diga el talud de corte; un "
                      "talud mas empinado da menos area y menos capacidad, y "
                      "por eso es el lado seguro. Borde libre 0: el Manual "
                      "calcula la capacidad con la cuneta llena (cita "
                      "MC_HHD.4.1.2.1a); el techo de 0.10 m de la ventana es "
                      "adopcion del proyecto. Lo que este valor supone y no "
                      "tiene trazabilidad en el repositorio: (i) la REGION "
                      "pluvial del corredor en año FEN (1600 a <3000 mm/año) "
                      "es una eleccion ligada a un dato de sitio que nadie "
                      "midio aqui, coherente con los 200 m; por encima de "
                      "3000 mm/año el minimo de la Tabla Nº 34 es una seccion "
                      "TRAPEZOIDAL, que la Fase 10 no implementa; (ii) Z1 = 3 "
                      "vale con velocidad de diseño menor de 70 km/h o IMDA "
                      "menor de 750 veh/dia: con las dos mayores la Tabla "
                      "304.12 (cita MC_HHD.4.1.2.1#T304_12) exige 1:4, y la "
                      "Fase 10 lo avisa porque ni la velocidad ni el IMDA son "
                      "datos del programa. Sensibilidad (medida en la ficha): "
                      "con S = 1 % y concreto la capacidad va de 0.467 a "
                      "0.871 m3/s al mover Z2 de 0.10 a 2.0 (0.670 con Z2 = 1)",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.2.1 a) y c), pags. impresas 173-178 (Figura Nº 27, Tabla "
               "304.12, Tabla Nº 34); DG-2018 num. 304.10 (Tabla 304.10, pag. "
               "impresa 204) y 304.11 (pag. impresa 208)",
        reemplazado_por="La seccion tipica de la cuneta del proyecto vial "
                        "(DG-2018) por tramo, con el talud de corte del EMS; "
                        "si cambia entre tramos, deja de ser un criterio de "
                        "corredor y pasa a ser dato externo por punto",
        verificacion_pendiente="Confirmar con el estudio hidrologico la "
                               "region pluvial del corredor en año FEN (la "
                               "fila de la Tabla Nº 34) y con el EMS el talud "
                               "de corte del tramo",
        resolucion=Libre(
            que_lo_fija="el proyectista de la seccion tipica de la via "
                        "(DG-2018): la Tabla Nº 34 del Manual da los minimos "
                        "por region pluvial y el talud exterior es el del "
                        "corte",
            dominio="profundidad_m > 0, ancho_m > 0, talud_exterior_HV > 0, "
                    "0 <= borde_libre_m < profundidad_m, ancho_fondo_m = 0 "
                    "(triangular) o 0.30 <= ancho_fondo_m < ancho_m "
                    "(trapezoidal, Tabla Nº 34 nota «*»)",
        ),
    ),

    "revestimiento_cuneta": Criterio(
        valor="concreto",
        nivel=NIVEL_PERFIL,          # lo consume M10, que corre a perfil
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # Las claves de `REVESTIMIENTOS_CUNETA`: cada una une una fila de la
        # Tabla Nº 32 (el K de Strickler) con una de la Tabla Nº 33 (la
        # velocidad limite). La UNION es lectura del proyecto y esta en la
        # justificacion; las filas, en el registro.
        sensibilidad=tuple(REVESTIMIENTOS_CUNETA),
        concepto="Revestimiento de la cuneta: fija su n de Manning (1/K de "
                 "la Tabla Nº 32) y su velocidad limite admisible (Tabla Nº "
                 "33)",
        justificacion="Decide la rugosidad y la velocidad limite con que se "
                      "calcula la capacidad de la cuneta. Se adopta "
                      "«concreto» porque es lo que la fuente pide y "
                      "recomienda: el num. 4.1.2.1 (pag. impresa 173, cita "
                      "MC_HHD.4.1.2.1#SECCION) quiere las cunetas de concreto "
                      "o de otro material resistente a la erosion, y el "
                      "apartado e) (pag. impresa 180, cita MC_HHD.4.1.2.1e) "
                      "exige revestirlas si la velocidad supera la Tabla Nº "
                      "33 y recomienda el concreto de 175 kg/cm2. Es tambien "
                      "la unica opcion en que las dos tablas nombran el "
                      "mismo material («Cunetas de concreto» K = 67, "
                      "«Concreto» 4.50 – 6.00 m/s). Las "
                      "demas opciones unen una fila de la Tabla Nº 32 con "
                      "una de la Tabla Nº 33 que la fuente no relaciona "
                      "(«Cunetas en roca» con «Mampostería, rocas duras» o "
                      "con «Conglomerado, pizarras duras, rocas blandas»; "
                      "«Cunetas excavadas en el terreno» con cada fila de "
                      "suelo): esa union es lectura del proyecto, declarada "
                      "como `Interpretacion` de la cita MC_HHD.4.1.2.1#T33, y "
                      "la memoria la imprime. Lo que este valor cuesta, y se "
                      "dice porque no es el extremo conservador (auditoria de "
                      "T-9, H6): para la LONGITUD entre alivios, el concreto "
                      "es la opcion MENOS conservadora de la ventana --K = 67 "
                      "frente a 33 y 25, y una velocidad limite de 4.50 m/s "
                      "frente a 3.00 o menos-- porque es la que mas caudal "
                      "conduce. Se adopta igual porque la fuente lo pide y lo "
                      "recomienda, no porque sea el lado seguro; una cuneta "
                      "sin revestir del corredor se declara aqui y la "
                      "capacidad baja. Y su fila de la Tabla Nº 33 lleva la "
                      "llamada «*», la de los flujos de muy corta duracion, "
                      "que el paso de la capacidad imprime desde el registro: "
                      "la fuente no da otro "
                      "valor para un flujo prolongado (el FEN), y el extremo "
                      "inferior de 'lectura_velocidad_limite_cuneta' es la "
                      "lectura conservadora de esa fila",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.2.1 (pag. impresa 173), a) Tablas Nº 32 y 33 (pag. "
               "impresa 175) y e) (pag. impresa 180)",
        resolucion=Libre(
            que_lo_fija="el proyectista, al especificar el revestimiento de "
                        "la cuneta (el Manual lo recomienda de concreto)",
            dominio="una de las claves de la ventana",
        ),
    ),

    "lectura_velocidad_limite_cuneta": Criterio(
        valor="extremo_inferior",
        nivel=NIVEL_PERFIL,          # lo consume M10, que corre a perfil
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("extremo_inferior", "extremo_superior"),
        concepto="Cual de los dos numeros de la fila de la Tabla Nº 33 rige "
                 "como velocidad limite admisible de la cuneta",
        justificacion="Decide la velocidad con que se calcula el segundo "
                      "limite de capacidad del num. 4.1.2.1 a) (el caudal a "
                      "la velocidad maxima admisible, cita "
                      "MC_HHD.4.1.2.1a). La Tabla Nº "
                      "33 (pag. impresa 175) da un INTERVALO por superficie "
                      "(«0.20 – 0.60» ... «4.50 – 6.00 *») y no dice cual de "
                      "los dos rige ni de que depende: la eleccion es del "
                      "proyectista. Se adopta el extremo inferior, que es el "
                      "conservador (menos velocidad admisible, menos "
                      "capacidad, menos longitud entre alivios); el superior "
                      "queda como alternativa barrible y la memoria imprime "
                      "el caudal con los dos",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.2.1 a), Tabla Nº 33, pag. impresa 175",
        resolucion=Libre(
            que_lo_fija="el proyectista: la fuente da el intervalo y no la "
                        "regla para elegir dentro de el",
            dominio="extremo_inferior | extremo_superior",
        ),
    ),

    # --- T-9 (correcciones; decision C del dueño, 2026-11-12) --- Si una obra
    # de Familia A cierra el tramo de cuneta de la alcantarilla de alivio
    # siguiente. La FASE A solo tomaba como extremo la obra B anterior o un
    # inicio declarado, de modo que el primer alivio de un corredor no tenia
    # tramo que verificar aunque una quebrada lo precediera.
    "obras_familia_a_extremo_de_cuneta": Criterio(
        valor="si",
        # DE PERFIL: lo consume M10 (`extremo_del_tramo`), que corre a perfil
        # para todo punto de Familia B; lo mide la corrida de perfil del
        # fixture en `tests/test_t9_correcciones.py`.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("si", "no"),
        concepto="Si la obra de Familia A anterior en progresiva cierra el "
                 "tramo de cuneta que descarga en la alcantarilla de alivio "
                 "siguiente (extremo de la verificacion VB1)",
        justificacion="Decide donde empieza el tramo de cuneta que VB1 mide "
                      "cuando el alivio no lo declara. Se adopta «si», por "
                      "decision del dueño del proyecto: una alcantarilla de "
                      "paso de quebrada es una obra de drenaje transversal, "
                      "y el DG-2018 (num. 304.11, pag. impresa 208, cita "
                      "DG2018.304.11#DESAGUE) limita la longitud de las "
                      "cunetas conduciendolas a los cauces naturales y a las "
                      "obras de drenaje transversal. Es LECTURA del proyecto y "
                      "va declarada como `Interpretacion` de esa cita: el "
                      "Manual de Hidrologia (num. 4.1.2.1 d), pag. impresa "
                      "179, cita MC_HHD.4.1.2.1d#ALIVIO) nombra solo las "
                      "alcantarillas de alivio, y que la cuneta llegue de "
                      "verdad a esa obra lo decide el perfil longitudinal "
                      "(curvas verticales, tramos en terraplen). «no» deja "
                      "como extremos solo las obras de Familia B y el inicio "
                      "declarado, que es la conducta de la FASE A; un "
                      "`inicio_tramo_cuneta_km` declarado gana en los dos "
                      "casos. Consecuencia medida en el fixture: B-01 (2+450) "
                      "queda a 530 m de A-02 (1+920) y VB1 no cumple; no se "
                      "mueve ningun diametro",
        fuente="DG-2018 num. 304.11 (pag. impresa 208); Manual de "
               "Hidrologia, Hidraulica y Drenaje (MTC), num. 4.1.2.1 d) (pag. "
               "impresa 179)",
        resolucion=Libre(
            que_lo_fija="el proyectista del drenaje longitudinal, con el "
                        "perfil de la rasante: si la cuneta descarga o no en "
                        "la quebrada de la obra de Familia A",
            dominio="si | no",
        ),
    ),
}
