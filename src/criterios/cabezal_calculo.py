"""
Fichas de criterios adoptados del dominio: cabezal_calculo.
"""

from typing import Dict
from src.constantes_normativas import CUANTIA_MIN_MURO_E060_14_3_1
from src.modelos import DeEnsayo, Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_DICT_CON_CAMPOS,
    FORMA_FLOAT,
    FORMA_STR,
    NIVEL_EXPEDIENTE,
    NIVEL_PERFIL,
    _FIGURA_3_11_C_R_EN_SI,
)


CRITERIOS: Dict[str, Criterio] = {


    # =======================================================================
    # --- T-7b --- (cadena T) · V8 con umbral declarable y la estabilidad del
    # cabezal en un solo marco (Fase 9). Nueve criterios; ninguno adopta un
    # numero que una fuente no escriba.
    # =======================================================================

    "umbral_no_colapso_evento_extremo": Criterio(
        # SIN VALOR DE ARCHIVO, como el metodo de V5 y por la misma decision:
        # sin declararlo V8 se detiene como siempre y ningun resultado del
        # fixture cambia.
        valor=None,                 # VACIO: bloquea V8 una vez declarado el TR
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO.
        #   sin_desborde_de_la_plataforma   el nivel del embalse con el
        #       caudal del evento extremo no alcanza el borde de la
        #       plataforma del lado de la entrada. IMPLEMENTADO.
        #   desborde_admitido_con_terraplen_protegido   se admite el flujo
        #       sobre la plataforma con el talud protegido. IMPLEMENTADO
        #       desde VE-4d: el caudal se reparte entre el conducto y la
        #       plataforma (HDS-5 num. 3.1.5, Ec. 3.9 y Figura 3.11, criterio
        #       'coeficientes_desborde_plataforma' [C]) y el caudal unitario
        #       sobre la plataforma se compara con el que la proteccion
        #       admite ('caudal_unitario_admisible_desborde_m2s' [A], sin
        #       valor). Ficha T7B-02.
        sensibilidad=("sin_desborde_de_la_plataforma",
                      "desborde_admitido_con_terraplen_protegido"),
        concepto="Como se juzga, en V8, que la via «no colapsa» con el "
                 "caudal del evento extremo: el umbral de la verificacion",
        justificacion="Decide contra que se compara el nivel del embalse "
                      "que la obra forma con el caudal del evento extremo "
                      "(el de 'TR_evento_extremo', declarado por punto como "
                      "`Q_evento_extremo_m3s`). La fila V8 de la hoja de "
                      "ruta pide que a un periodo de retorno mayor la via no "
                      "colapse aunque desborde, y no fija el umbral. La "
                      "fuente mas cercana (HDS-5 num. 2.2.5 a., pag. impresa "
                      "2.10, cita HDS5_3ED.2.2.5a#COTA_CRITICA) admite que la "
                      "cota que la carga no debe superar sea el hombro de la "
                      "plataforma o la cota de desborde de la via, y no dice "
                      "que desbordar sea colapsar. Lo que no resuelve: como "
                      "se juzga el colapso cuando el agua pasa sobre la via. "
                      "Por eso no tiene valor de archivo. Con "
                      "«sin_desborde_de_la_plataforma» V8 cumple si el nivel "
                      "del evento extremo queda por debajo del borde de la "
                      "plataforma: si no hay desborde, no hay desborde que "
                      "la haga colapsar; es la lectura mas exigente, porque "
                      "la fila admite el desborde. Con "
                      "«desborde_admitido_con_terraplen_protegido» (desde "
                      "VE-4d) el caudal del evento se reparte entre el "
                      "conducto y el vertedero que forma la plataforma "
                      "(HDS-5 num. 3.1.5) y V8 cumple si el caudal unitario "
                      "que pasa sobre la plataforma no supera el que la "
                      "proteccion del talud de aguas abajo admite, que es "
                      "otro criterio del proyecto; el diseño de esa "
                      "proteccion (HEC-23, que la fuente cita y que no esta "
                      "en el repositorio de normas) no lo hace este programa",
        fuente="Fase 5, V8 de la hoja de ruta, sin numeral. HDS-5 num. 2.2.5 "
               "a., pag. impresa 2.10 (PDF 72), para la cota de comparacion; "
               "num. 3.1.5, pags. impresas 3.15-3.16 (PDF 97-98), y num. "
               "5.4.5, pag. impresa 5.16 (PDF 152), para el desborde",
        reemplazado_por="La definicion de colapso de la via que el "
                        "Propietario declare, con el diseño de la proteccion "
                        "del terraplen adjunto a la memoria",
        resolucion=Libre(
            que_lo_fija="el proyectista: la hoja de ruta pide la "
                        "verificacion y ninguna fuente de normas/ define el "
                        "colapso de la via",
            dominio="una de las opciones de la ventana",
        ),
    ),

    "marco_estabilidad_cabezal": Criterio(
        valor="lrfd_rige_asd_informa",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO, que es a la vez la regla de desempate.
        #   lrfd_rige_asd_informa   deciden las verificaciones del marco de
        #       estados limite (AASHTO LRFD 11.6); las de factores de
        #       seguridad (E.050) se calculan e imprimen como INDICADOR: si
        #       alguna no alcanza su factor, el punto lo avisa y no se
        #       detiene.
        #   asd_rige_lrfd_informa   al reves.
        #   envolvente_de_los_dos   deciden las dos: el cabezal cumple solo
        #       si cumple en los dos marcos.
        sensibilidad=("lrfd_rige_asd_informa", "asd_rige_lrfd_informa",
                      "envolvente_de_los_dos"),
        concepto="Marco con que se verifica la estabilidad externa del "
                 "cabezal (capacidad portante, excentricidad o volteo, y "
                 "deslizamiento), y que se hace con el otro marco",
        justificacion="Decide cual de los dos marcos de verificacion RIGE la "
                      "estabilidad del cabezal y que papel tiene el otro; es "
                      "decision del dueño del proyecto. Ninguna "
                      "norma peruana, ni la Seccion 12 de AASHTO LRFD "
                      "(estructuras enterradas), prescribe el marco de "
                      "estabilidad del cabezal de una alcantarilla: el Art. "
                      "11.6 de AASHTO esta escrito para estribos y muros de "
                      "contencion, y la Seccion 12 no remite a el. El "
                      "proyecto MODELA el cabezal como un muro de "
                      "semigravedad en voladizo -- una pantalla sobre una "
                      "zapata con talon que retiene el relleno del "
                      "terraplen -- y le aplica ese articulo: es una "
                      "hipotesis de modelacion, no un mandato de la fuente. "
                      "Se adopta el marco de estados limite (cargas "
                      "factoradas contra resistencias minoradas, y la "
                      "excentricidad de la resultante en lugar del factor de "
                      "seguridad al volteo) por coherencia con la Via 1 de "
                      "la hoja de ruta -- AASHTO LRFD de extremo a extremo "
                      "en lo estructural -- y con el formato del Manual de "
                      "Puentes. La verificacion por factores de seguridad de "
                      "la norma de suelos E.050 (Art. 21 y num. 39.13.6), "
                      "que es de edificaciones y se aplica al cabezal por "
                      "analogia, se calcula en paralelo sobre cargas de "
                      "servicio y se imprime al lado. Los dos marcos no se "
                      "cruzan nunca: ni un factor de seguridad se compara "
                      "con una carga factorada, ni una resistencia minorada "
                      "con una carga de servicio. Regla de desempate: con el "
                      "valor de archivo, un factor de seguridad de E.050 que "
                      "no se alcance sale como aviso y no detiene el punto "
                      "-- con la aceleracion sismica de este sitio es lo "
                      "esperable en el deslizamiento --; quien quiera que "
                      "detenga declara la envolvente",
        fuente="Decision del dueño del proyecto sobre el "
               "dictamen del verificador normativo. AASHTO LRFD 9a ed., "
               "11.6.3 (citas AASHTO_LRFD_9.11.6.3.2#PORTANTE, "
               "AASHTO_LRFD_9.11.6.3.3#EXC, "
               "AASHTO_LRFD_9.11.6.3.6#DESLIZAMIENTO); E.050 Art. 17.1, 21 y "
               "num. 39.13.6 (citas E050.17.1#SERVICIO, E050.21, "
               "E050.39.13.6). Ninguna de las dos fuentes prescribe el marco "
               "para un cabezal de alcantarilla",
        resolucion=Libre(
            que_lo_fija="el dueño del proyecto: ninguna norma prescribe el "
                        "marco de estabilidad de un cabezal de alcantarilla",
            dominio="una de las tres reglas de la ventana",
        ),
    ),

    "fila_phi_estabilidad_cabezal": Criterio(
        valor="muros_tabla_11_5_7",   # decision 11 del dueño (VE-3.15)
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   zapatas_seccion_10   Tabla 10.5.5.2.2-1: portante 0.45 (metodo
        #       teorico en arena con SPT) o 0.50 (en arcilla); deslizamiento
        #       0.80 (vaciado in situ sobre arena) u 0.85 (sobre arcilla).
        #   muros_tabla_11_5_7   Tabla 11.5.7-1, muros de gravedad y
        #       semigravedad: portante 0.55; deslizamiento 1.0.
        sensibilidad=("zapatas_seccion_10", "muros_tabla_11_5_7"),
        concepto="De que tabla de AASHTO LRFD salen los factores de "
                 "resistencia del estado limite de resistencia para la "
                 "capacidad portante y el deslizamiento del cabezal",
        justificacion="Decide los factores de resistencia de E1 y E3 en el "
                      "estado limite de resistencia. Lo que dice la letra: "
                      "el Art. 11.5.7 manda usar los factores de la Tabla "
                      "11.5.7-1 en el diseño de muros, y esa tabla "
                      "si identifica, para los muros de gravedad y "
                      "semigravedad, 0.55 al portante y 1.0 al "
                      "deslizamiento; a la Seccion 10 solo remite lo que la "
                      "tabla no identifique (cita "
                      "AASHTO_LRFD_9.11.5.7#MUROS). Leida al pie de la "
                      "letra, la fila de un muro de semigravedad es la de "
                      "muros. La tension es otra: el Art. 11.6.3.6 remite el "
                      "deslizamiento del muro al 10.6.3.4, cuyas ecuaciones "
                      "nombran los factores de la Tabla 10.5.5.2.2-1 de las "
                      "zapatas (0.45 a 0.50 al portante y 0.80 a 0.85 al "
                      "deslizamiento de una zapata vaciada in situ), y el "
                      "cabezal no es ninguno de los muros que la Tabla "
                      "11.5.7-1 nombra sino una estructura modelada como "
                      "tal. El proyecto adopta la fila de muros, decision 11 "
                      "del dueño con la verificacion independiente de VE-3: "
                      "es la letra del Art. 11.5.7 para el muro de "
                      "semigravedad y la que usa el ejemplo resuelto de "
                      "Caltrans. Lo que juega en contra, y se declara: el "
                      "articulo de muros del Manual de Puentes peruano (num. "
                      "2.8.1.1.12.6, Deslizamiento) define el factor del "
                      "deslizamiento por la tabla de las zapatas y no "
                      "transcribe la 11.5.7-1; la hoja de ruta (§0.2) "
                      "adopta AASHTO LRFD de extremo a extremo y deja las "
                      "dos tablas en la ventana de este [A]. Y una salvedad "
                      "que queda para el EMS real: el comentario C11.5.7 "
                      "pide factores menores cuando la variabilidad del "
                      "sitio o del material es inusualmente alta, y mientras "
                      "el suelo de fundacion sea de prueba esa revision esta "
                      "pendiente. Es una eleccion [A] a la que el veredicto "
                      "es sensible: con los datos de prueba de A-01 el "
                      "deslizamiento estatico pasa de no cumplir a cumplir "
                      "con la fila de muros, y la memoria lo avisa cuando "
                      "una fila cambia de veredicto entre las dos opciones. "
                      "Con la fila de zapatas toma, en suelo friccionante, "
                      "la del metodo teorico en arena con SPT (0.45, la "
                      "menor de las de suelo) y la del concreto vaciado in "
                      "situ sobre arena (0.80); en suelo cohesivo, 0.50 y "
                      "0.85. En Evento Extremo I no hay eleccion: el Art. "
                      "11.5.8 fija 0.8 al portante de los muros de "
                      "semigravedad y 1.0 a lo demas",
        fuente="AASHTO LRFD 9a ed., Tabla 10.5.5.2.2-1, pag. impresa 10-42 "
               "(PDF 1331; cita AASHTO_LRFD_9.10.5.5.2.2#T1) y 11.5.7 con su "
               "Tabla 11.5.7-1, pags. impresas 11-15 y 11-17 (PDF 1484 y "
               "1486; cita AASHTO_LRFD_9.11.5.7#MUROS) y su comentario "
               "C11.5.7, pag. impresa 11-16 (factores menores si la "
               "variabilidad es inusualmente alta). Contraste: Manual de "
               "Puentes 2.8.1.1.12.6, pags. impresas 250-251 (deslizamiento "
               "con la tabla de zapatas); Caltrans Bridge Design Practice "
               "11.2, pags. 11.2-24 y 11.2-26 (fuente sin registrar, en "
               "ejemplos_resueltos/cabezal_muros). Los numeros, en "
               "constantes_normativas.PHI_ZAPATAS_T10_5_5_2_2_1 y "
               "PHI_MUROS_T11_5_7_1",
        resolucion=Libre(
            que_lo_fija="el proyectista: las dos tablas son de la fuente y "
                        "cual aplica a un cabezal modelado como muro no lo "
                        "dice ninguna",
            dominio="una de las dos filas de la ventana",
        ),
    ),

    "drenaje_trasdos": Criterio(
        # VALOR DE ARCHIVO «drenado» desde VE-3.16 (2026-11-18, decision del
        # dueño al aceptar la recomendacion de la verificacion independiente
        # `sismo_cabezal_que_se_pasa.md`, punto 2): AASHTO 11.6.6 MANDA drenar
        # el relleno ("shall be drained") y solo admite la hidrostatica plena
        # "if drainage cannot be provided", de modo que «sin_drenaje» era la
        # excepcion de la norma convertida en regla. Hasta VE-3.15 el valor
        # de archivo era «sin_drenaje».
        valor="drenado",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   sin_drenaje   el agua puede llenar el relleno RETENIDO hasta su
        #       superficie contra el trasdos, nunca por encima del muro:
        #       hidrostatica en esa altura y suelo sumergido (AASHTO 11.6.6;
        #       correcciones de T-7b, H6).
        #   drenado       drenaje del trasdos declarado (filtro y
        #       lloraderos, a mostrar en planos): el agua del relleno no
        #       supera el nivel freatico natural del punto.
        sensibilidad=("sin_drenaje", "drenado"),
        concepto="Si el trasdos del cabezal tiene un sistema de drenaje "
                 "declarado, y con ello hasta que nivel se cuenta el agua "
                 "en el relleno",
        justificacion="Decide el nivel del agua en el relleno del trasdos, "
                      "y con el el empuje hidrostatico, el peso sumergido del "
                      "suelo bajo ese nivel y la subpresion del lado del "
                      "relleno. La fuente (AASHTO LRFD 11.6.6, cita "
                      "AASHTO_LRFD_9.11.6.6#DRENAJE) exige drenar el relleno "
                      "o, si no se puede, diseñar el muro con la hidrostatica "
                      "completa del agua del relleno; y E.050 num. 39.13.8 "
                      "(por analogia) exige que el muro de contencion tenga "
                      "un sistema de drenaje. Lo que no resuelven: hasta que "
                      "nivel sube el agua de un relleno sin drenar; el "
                      "proyecto lee que hasta su superficie (la lectura esta "
                      "en la `Interpretacion` de la cita). El valor de "
                      "archivo es «drenado» (VE-3.16): es lo que la fuente "
                      "manda, y adoptarlo COMPROMETE un detalle -- filtro y "
                      "lloraderos -- que tiene que estar en los planos y en "
                      "su mantenimiento (un lloradero tapado devuelve el "
                      "caso «sin_drenaje»), y el comentario de la fuente "
                      "advierte que los lloraderos solos no aseguran el "
                      "drenaje. «sin_drenaje» se declara cuando el drenaje "
                      "no puede darse. Sin drenaje el agua llena el relleno "
                      "RETENIDO hasta su superficie contra el trasdos "
                      "(coronacion menos bordillo) y nunca sube por encima "
                      "del muro. Con «drenado» el agua del relleno queda en "
                      "el nivel freatico natural del punto (columna "
                      "NF_profundidad_m, bajo el terreno del cruce), que el "
                      "drenaje no baja; y el modelo NO contempla el "
                      "desembalse rapido -- el relleno mojado por la avenida "
                      "hasta la cota del agua de diseño con el cauce ya "
                      "vacio --, que el comentario C11.6.6 hace plausible al "
                      "advertir que los lloraderos no aseguran el drenaje: "
                      "el ensamble lo avisa con su orden de magnitud. "
                      "Declarar «sin_drenaje» es escribir 'drenaje_trasdos' = "
                      "«sin_drenaje» en la sesion o con --declarar. En los "
                      "dos casos el "
                      "empuje del suelo bajo el agua va con su peso "
                      "sumergido (AASHTO 3.11.3), y el agua no se cuenta dos "
                      "veces",
        fuente="AASHTO LRFD 9a ed., 11.6.6 'Drainage', pag. impresa 11-35 "
               "(PDF 1504; cita AASHTO_LRFD_9.11.6.6#DRENAJE) y 3.11.3, pag. "
               "impresa 3-118; E.050 num. 39.13.8, pag. 73 (cita "
               "E050.39.13.8#DRENAJE), por analogia",
        reemplazado_por="Detalle de drenaje del trasdos en los planos del "
                        "cabezal (filtro, geotextil o geodren, y lloraderos)",
        resolucion=Libre(
            que_lo_fija="el proyectista: es un detalle constructivo del "
                        "cabezal que se declara y se dibuja",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "peso_especifico_saturado_relleno_kn_m3": Criterio(
        valor=None,                 # VACIO: solo detiene si hay agua en el relleno
        # NIVEL MEDIDO: PERFIL desde la revision de VE-2 (M3). Lo mide la
        # corrida `--alcance perfil` de
        # `tests/test_ve2_revision_m3_m4.py::test_m3_medido_la_corrida_de_
        # perfil_lo_invoca_sin_diferir` (P1 con 'nivel_agua_diseno_v7' =
        # 'nf_del_punto' y el nivel sobre la clave): V7 lo invoca y el
        # bloqueo NO queda diferido por el alcance. Con los valores de
        # archivo ninguna corrida de referencia lo invoca (lo censa
        # `tests/test_nivel_medido.py::DE_UNA_ALTERNATIVA_NO_DE_ARCHIVO`).
        # Su otro consumidor, el cabezal (Fase 9), es de expediente: el
        # nivel es el de la PRIMERA etapa que lo consume.
        #
        # ES [S], NO [A] (verificacion de las correcciones de VE-2, N2,
        # decision del dueño): no hay nada que elegir -- es la medicion de
        # laboratorio del relleno de ESTE proyecto, a la compactacion que su
        # especificacion fija --, de modo que se defiende con la trazabilidad
        # de la lectura y no con un rango (CLAUDE.md, «Taxonomia»). Hasta N2
        # era [A] de perfil sin ventana, y para eso M3 habia eximido al dato
        # de ensayo de la regla 3 de `_verificar_nivel`; la exencion se
        # retiro con el reetiquetado.
        nivel=NIVEL_PERFIL,
        etiqueta="S",
        forma=FORMA_FLOAT,
        positivo=True,
        concepto="Peso especifico SATURADO del relleno del trasdos, kN/m3, "
                 "para el empuje del suelo bajo el nivel del agua",
        justificacion="Decide el peso sumergido del relleno (saturado menos "
                      "el del agua) con que se calcula el empuje del suelo "
                      "bajo el nivel del agua, que es como AASHTO 3.11.3 "
                      "manda calcularlo, y el peso del suelo saturado sobre "
                      "el talon. Solo se invoca cuando el agua llega al "
                      "plano de empuje: con el relleno drenado y el freatico "
                      "por debajo de la zapata no hace falta. Es un dato del "
                      "material de relleno compactado y no se deduce del "
                      "peso especifico humedo de "
                      "'peso_especifico_relleno_kn_m3': usar ese mismo "
                      "numero como saturado subestimaria el empuje del suelo "
                      "sumergido. Por eso esta vacio: lo da el ensayo del "
                      "material de cantera. Desde VE-2 lo lee tambien V7, "
                      "solo con 'nivel_agua_diseno_v7' = «nf_del_punto» y el "
                      "nivel sobre la clave, para el relleno del conducto que "
                      "queda bajo el agua (`M8.peso_relleno_bajo_el_nivel_kn_m`): "
                      "con el valor de archivo de ese criterio V7 no lo lee, "
                      "pero con la alternativa una corrida de perfil se "
                      "detiene en el, y por eso es de perfil (revision de "
                      "VE-2, M3). Es [S] y no [A]: cambia al cambiar de "
                      "cantera o de especificacion de compactacion, no al "
                      "cambiar de proyectista. Vive aqui, y no en "
                      "datos_sitio.py, porque sigue pendiente del ensayo, que "
                      "es la condicion que este archivo admite para un [S]",
        fuente="PENDIENTE - ensayo del material de relleno (peso especifico "
               "y gravedad especifica de solidos, a la compactacion "
               "especificada)",
        trazabilidad="NO SE HA EJECUTADO NINGUN ENSAYO. La lectura que hace "
                     "falta: el peso especifico saturado del material de "
                     "relleno del trasdos, compactado al grado que fija la "
                     "especificacion del proyecto, a partir de su peso "
                     "especifico seco a esa compactacion y de la gravedad "
                     "especifica de solidos (o medido sobre la muestra "
                     "saturada), en kN/m3. Se declara con la cantera, el "
                     "ensayo, el grado de compactacion y el laboratorio "
                     "(`DeEnsayo.trazabilidad_exigida`). Vale para todo el "
                     "corredor mientras el relleno venga de la misma cantera "
                     "y se compacte a la misma especificacion; con dos "
                     "canteras deja de ser un dato de corredor",
        reemplazado_por="Ensayo del material de cantera del relleno",
        resolucion=DeEnsayo(
            ensayo="peso especifico saturado del relleno compactado del "
                   "trasdos",
            trazabilidad_exigida="cantera, ensayo, grado de compactacion y "
                                 "laboratorio",
        ),
    ),

    "fraccion_delta_sobre_phi_trasdos": Criterio(
        valor=0.67,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_FLOAT,
        # De un tercio a dos tercios de phi: los dos extremos que la Figura
        # C3.11.5.3-1b de AASHTO acota sobre el plano vertical del talon.
        sensibilidad=(0.33, 0.67),
        concepto="Angulo de friccion sobre el plano de empuje del trasdos "
                 "(delta) como fraccion del angulo de friccion interna del "
                 "relleno (phi)",
        justificacion="Decide cuanto se inclina el empuje sobre su plano, "
                      "y con ello su reparto entre la componente horizontal "
                      "y la vertical. La fuente (AASHTO LRFD, comentario "
                      "C3.11.5.3, cita AASHTO_LRFD_9.C3.11.5.3#DELTA) dice "
                      "que la practica de largo plazo ha sido usar 0.67 de "
                      "phi en la interfaz entre el respaldo del muro y el "
                      "suelo retenido, para suelo contra concreto y para "
                      "suelo contra suelo, y que aun en los muros de "
                      "semigravedad en voladizo la friccion se suele limitar "
                      "a 0.67 de phi; su Figura C3.11.5.3-1b acota el angulo "
                      "sobre el plano vertical del talon entre un tercio y "
                      "dos tercios de phi. No lo prescribe: describe una "
                      "practica, y por eso es [C] con esa ventana. Un delta "
                      "mayor reduce el coeficiente de empuje y traslada "
                      "empuje de la horizontal a la vertical: alivia el "
                      "deslizamiento y la excentricidad y carga mas la base. "
                      "Si se declara 'friccion_muro_suelo_delta', gana ese "
                      "angulo",
        fuente="AASHTO LRFD 9a ed., C3.11.5.3, pags. impresas 3-121 y 3-122 "
               "(PDF 175 y 176; citas AASHTO_LRFD_9.C3.11.5.3#DELTA y "
               "AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON) y Figura "
               "C3.11.5.3-1b, pag. impresa 3-123",
        reemplazado_por="Ensayo de interfase, declarado en "
                        "'friccion_muro_suelo_delta'",
        resolucion=Libre(
            que_lo_fija="la practica que el comentario C3.11.5.3 de AASHTO "
                        "describe; la fraccion dentro de la ventana, el "
                        "proyectista",
            dominio="adimensional, entre 0.33 y 0.67",
        ),
    ),

    "regla_pendiente_relleno_trasdos": Criterio(
        # CORRECCIONES DE T-7b (H4): el valor de archivo paso de
        # «talud_quebrado_2h» a «cuna_de_tanteo». La pendiente equivalente
        # es una simplificacion de los muros de suelo reforzado y, medida
        # en A-01, SUBESTIMA el empuje estatico un 7 a 11 % frente a la cuña
        # que la fuente pide; bajo sismo, con el k_h de archivo, dejaba a
        # Mononobe-Okabe fuera de su dominio y la condicion sin cifra.
        valor="cuna_de_tanteo",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   cuna_de_tanteo       cuña de Coulomb por el metodo de Culmann
        #       sobre el plano vertical del talon, con la superficie REAL del
        #       relleno: sube con el talud del terraplen y se quiebra en la
        #       plataforma (AASHTO 3.11.5.3 y 3.11.5.8.1; bajo sismo,
        #       pseudoestatica con k_h y k_v, C11.6.5.3). Es la de archivo.
        #   talud_quebrado_2h    pendiente equivalente: la de la recta que va
        #       de la coronacion del relleno retenido al terreno a una
        #       distancia horizontal de dos veces la altura del muro
        #       (Figura C3.11.5.8.1-1 de AASHTO, por analogia), con la
        #       formula cerrada de Coulomb y de Mononobe-Okabe. SESGO
        #       DECLARADO: subestima el empuje estatico del 7 al 11 % en los
        #       cabezales de A-01.
        #   talud_del_terraplen  la del talud del terraplen, como si no se
        #       quebrara nunca: cota superior del empuje estatico.
        sensibilidad=("cuna_de_tanteo", "talud_quebrado_2h",
                      "talud_del_terraplen"),
        concepto="Como se calcula, con la geometria real del relleno del "
                 "trasdos, el empuje activo estatico y sismico del cabezal: "
                 "por la cuña de tanteo sobre la superficie real o por la "
                 "formula cerrada con una pendiente equivalente",
        justificacion="Decide el coeficiente de empuje del relleno, que "
                      "entra en todas las filas de la estabilidad. Detras "
                      "del cabezal el relleno no es horizontal ni un talud "
                      "indefinido: sube con el talud del terraplen desde la "
                      "coronacion del relleno retenido y se quiebra en el "
                      "borde de la plataforma. La formula de Coulomb de la "
                      "ec. 3.11.5.3-1 es la de un talud uniforme, y para lo "
                      "que se aparta de ella la fuente permite calcular el "
                      "empuje con cuñas de prueba por el metodo de Culmann "
                      "(AASHTO LRFD 3.11.5.3, cita "
                      "AASHTO_LRFD_9.3.11.5.3#CULMANN); para el relleno "
                      "quebrado de los muros de suelo reforzado recomienda "
                      "la cuña de tanteo de Coulomb (3.11.5.8.1, cita "
                      "AASHTO_LRFD_9.3.11.5.8.1#CUNA); y bajo sismo, donde "
                      "Mononobe-Okabe no es adecuado, permite la cuña de "
                      "tanteo (C11.6.5.3, cita "
                      "AASHTO_LRFD_9.C11.6.5.3#CUNA). El valor de archivo es "
                      "esa cuña, sobre el plano vertical del talon y con la "
                      "superficie real: es lo que la fuente pide, coincide "
                      "con Coulomb en un talud uniforme y con "
                      "Mononobe-Okabe en un relleno horizontal, y con el "
                      "relleno que se quiebra en la plataforma tiene maximo "
                      "aun donde Mononobe-Okabe con una pendiente "
                      "equivalente queda fuera de su dominio. Su "
                      "coeficiente es el equivalente, 2·P/(gamma·h²), y se "
                      "reparte en el plano con el diagrama triangular de "
                      "Coulomb. Sigue siendo [A] porque la cuña de la "
                      "fuente es de muros y su uso en el cabezal, que se "
                      "MODELA como muro, es eleccion del proyecto. Las otras "
                      "dos opciones quedan barribles: la pendiente "
                      "equivalente de la Figura C3.11.5.8.1-1 (la "
                      "alternativa simplificada que el comentario PERMITE "
                      "para los muros de suelo reforzado, cita "
                      "AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO), que en "
                      "los cabezales de A-01 da un empuje estatico un 7 a "
                      "11 % MENOR que la cuña; y el talud entero sin "
                      "quiebre, cota superior del empuje estatico. Con "
                      "cualquiera de las dos, y con la pendiente declarada "
                      "en 'pendiente_relleno_trasdos_i', rige la formula "
                      "cerrada",
        fuente="AASHTO LRFD 9a ed., 3.11.5.3, pag. impresa 3-121 (PDF 175; "
               "cita AASHTO_LRFD_9.3.11.5.3#CULMANN); 3.11.5.8.1 y "
               "C3.11.5.8.1, pag. impresa 3-137 (PDF 191; citas "
               "AASHTO_LRFD_9.3.11.5.8.1#CUNA y "
               "AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO) y Figura "
               "C3.11.5.8.1-1, pag. impresa 3-138 (PDF 192); C11.6.5.3, pag. "
               "impresa 11-30 (PDF 1499; cita AASHTO_LRFD_9.C11.6.5.3#CUNA)",
        reemplazado_por="Analisis de equilibrio limite generalizado (GLE, "
                        "AASHTO A11.3.3) del relleno con la estratigrafia "
                        "del EMS",
        resolucion=Libre(
            que_lo_fija="el proyectista: la cuña es lo que la fuente pide "
                        "para la geometria real, y su uso en el cabezal "
                        "modelado como muro es eleccion del proyecto",
            dominio="una de las tres reglas de la ventana",
        ),
    ),

    "factores_inclinacion_carga_portante": Criterio(
        valor="aplicar",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("aplicar", "omitir"),
        concepto="Si la resistencia portante nominal bajo la zapata del "
                 "cabezal se reduce por la inclinacion de la carga (factores "
                 "i_c, i_q, i_gamma de AASHTO 10.6.3.1.2a)",
        justificacion="Decide si la resistencia portante se reduce porque la "
                      "resultante sobre la base esta inclinada, que en un "
                      "muro lo esta siempre. La fuente (AASHTO LRFD "
                      "10.6.3.1.2a, cita AASHTO_LRFD_9.10.6.3.1.2a#QN) "
                      "escribe los factores de inclinacion dentro de la "
                      "ecuacion de la resistencia nominal, y su comentario "
                      "dice que la mayoria de los geotecnistas no los usa, "
                      "que se dedujeron para zapatas sin empotramiento, que "
                      "combinados con los factores de resistencia pueden ser "
                      "demasiado conservadores, y que con empotramiento "
                      "modesto cabe considerar omitirlos. Lo "
                      "que no resuelve: si se omiten en un muro. El proyecto "
                      "los APLICA -- el lado seguro, y el del texto del "
                      "articulo -- y deja «omitir» barrible: la diferencia "
                      "es grande (con la horizontal en el 40 % de la "
                      "vertical, el termino del peso propio del suelo baja a "
                      "la quinta parte)",
        fuente="AASHTO LRFD 9a ed., 10.6.3.1.2a, ecs. 10.6.3.1.2a-5 a -9 y "
               "su comentario, pags. impresas 10-70 y 10-71 (PDF 1359 y "
               "1360; cita AASHTO_LRFD_9.10.6.3.1.2a#QN)",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el permiso del comentario "
                        "C10.6.3.1.2a",
            dominio="aplicar u omitir",
        ),
    ),

    "terreno_delante_del_cabezal": Criterio(
        valor="horizontal",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   horizontal          el terreno delante de la zapata es el fondo
        #       del cauce, del que la zapata queda D_f por debajo: capacidad
        #       portante de terreno horizontal (AASHTO 10.6.3.1.2a).
        #   talud_descendente   el terreno baja delante de la zapata: zapata
        #       en o junto al talud (AASHTO 10.6.3.1.2c, RC_BC de sus tablas,
        #       desde VE-5), con la geometria de 'talud_delante_del_cabezal'.
        sensibilidad=("horizontal", "talud_descendente"),
        concepto="Forma del terreno DELANTE de la zapata del cabezal (del "
                 "lado del cauce), que decide si la capacidad portante es la "
                 "de terreno horizontal o la de una zapata en talud",
        justificacion="Decide que ecuacion de capacidad portante aplica. La "
                      "hoja de ruta (Sec. 9.3) situaba el cabezal en el "
                      "borde del terraplen, no en terreno horizontal, y "
                      "exigia la zapata en talud. Con el "
                      "cabezal que el predimensionamiento de T-7a propone "
                      "eso no describe la geometria: la zapata se desplanta "
                      "bajo el terreno del pie del muro, que es el fondo del "
                      "cauce (en la salida, la mas baja entre la solera y el "
                      "fondo del receptor), y el talud del terraplen SUBE "
                      "detras del muro, no baja delante. La reduccion por "
                      "talud de la fuente (AASHTO LRFD 10.6.3.1.2c, cita "
                      "AASHTO_LRFD_9.10.6.3.1.2c#TALUD) se define con la "
                      "altura del terreno inclinado que queda por debajo de "
                      "la base de la zapata, que aqui es cero. El proyecto "
                      "adopta por eso el terreno horizontal, y cuenta como "
                      "sobrecarga solo el empotramiento que queda bajo la "
                      "hoya de socavacion cuando la Fase 6 la entrega. La "
                      "otra opcion es para el cabezal que si queda sobre un "
                      "terreno que desciende -- una salida a media ladera "
                      "--: desde VE-5 aplica la reduccion RC_BC de las Tablas "
                      "10.6.3.1.2c-1 y -2 con la geometria del talud "
                      "('talud_delante_del_cabezal'), y sin ella se detiene. "
                      "El defecto se reporta contra la hoja de ruta, que "
                      "esta sesion corrige",
        fuente="Geometria del cabezal de 'predimensionamiento_cabezal' "
               "(T-7a) y AASHTO LRFD 9a ed., 10.6.3.1.2c y Figura "
               "10.6.3.1.2c-1, pags. impresas 10-74 y 10-75 (PDF 1363 y "
               "1364; cita AASHTO_LRFD_9.10.6.3.1.2c#TALUD)",
        reemplazado_por="Levantamiento del terreno delante de cada cabezal",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el perfil del cauce delante "
                        "del cabezal",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    # --- VE-5 (lote M9, ficha T7B-04) --- La geometria del talud que baja
    # delante de la zapata, para la RC_BC de AASHTO 10.6.3.1.2c. SUSTITUYE a
    # 'N_cq_N_gammaq_meyerhof' (los factores de los abacos de Meyerhof del
    # Manual de Puentes), que se retiro: las tablas de la 9a edicion SI se
    # transcriben, y lo que falta es la geometria, que es un dato de sitio.
    # NIVEL: el de la Fase 9 (expediente), su unico consumidor
    # (`M9._q_nominal`, con 'terreno_delante_del_cabezal' = talud).
    "talud_delante_del_cabezal": Criterio(
        valor=None,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="S",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Geometria del talud que desciende delante de la zapata del "
                 "cabezal: altura bajo la base H_s (m), inclinacion beta "
                 "(grados) y distancia b del borde de la zapata a la "
                 "coronacion (m; 0 = zapata en el talud)",
        justificacion="Decide el coeficiente de reduccion RC_BC de la "
                      "capacidad portante de una zapata en o junto a un "
                      "talud (AASHTO 10.6.3.1.2c, cita "
                      "AASHTO_LRFD_9.10.6.3.1.2c#TALUD, Tablas 10.6.3.1.2c-1 "
                      "y -2 y Figura 10.6.3.1.2c-1), que solo se lee con "
                      "'terreno_delante_del_cabezal' = 'talud_descendente'. "
                      "Es la geometria del terreno de ESTE sitio: no hay "
                      "rango que elegir y se defiende con la trazabilidad "
                      "del levantamiento",
        fuente="Levantamiento topografico del terreno delante del cabezal; "
               "AASHTO LRFD 9a ed., 10.6.3.1.2c, pags. impresas 10-74 a 10-78 "
               "(PDF 1363 a 1367)",
        trazabilidad="NO SE HA LEVANTADO. La lectura que hace falta: del "
                     "perfil del terreno delante de cada cabezal en media "
                     "ladera, la altura del terreno inclinado bajo la base de "
                     "la zapata, su inclinacion y la distancia del borde de "
                     "la zapata a la coronacion, con el levantamiento y la "
                     "fecha. Es el valor de CORREDOR: vale para un tramo con "
                     "el mismo talud",
        reemplazado_por="Levantamiento topografico del terreno delante de "
                        "cada cabezal",
        resolucion=DeEnsayo(
            ensayo="levantamiento topografico del terreno delante del "
                   "cabezal",
            trazabilidad_exigida="levantamiento, perfil y fecha",
        ),
    ),

    # --- VE-5 (lote M9, ficha T7B-04) --- Los factores de forma y de
    # profundidad de la capacidad portante (AASHTO Tabla 10.6.3.1.2a-3 y ec.
    # 10.6.3.1.2a-10), que hasta VE-5 valian 1 sin decirlo en un criterio.
    # NIVEL: el de la Fase 9 (expediente), `M9._q_nominal`.
    "factores_forma_profundidad_portante": Criterio(
        valor="corrida_sin_profundidad",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   corrida_sin_profundidad            s_c = s_q = s_gamma = d_q = 1:
        #       la zapata del cabezal sigue bajo los aleros (B/L -> 0) y el
        #       suelo sobre el desplante no se da por competente.
        #   forma_con_la_longitud_del_cabezal  los de forma con L = la
        #       longitud del cabezal (Tabla 10.6.3.1.2a-3); d_q = 1.
        #   forma_y_profundidad                ademas d_q (ec. 10.6.3.1.2a-10,
        #       <= 1.4): declara el suelo sobre el desplante tan competente
        #       como el de debajo, que es la condicion de la fuente.
        sensibilidad=("corrida_sin_profundidad",
                      "forma_con_la_longitud_del_cabezal",
                      "forma_y_profundidad"),
        concepto="Si la capacidad portante del cabezal lleva los factores de "
                 "forma (con la longitud de la zapata) y el de profundidad",
        justificacion="Decide s_c, s_q, s_gamma y d_q en la capacidad "
                      "portante del cabezal. AASHTO 10.6.3.1.2a (Tabla "
                      "10.6.3.1.2a-3 y ec. 10.6.3.1.2a-10, pag. impresa "
                      "10-73) los define; d_q solo vale con el suelo sobre el "
                      "nivel de desplante tan competente como el de debajo, "
                      "no pasa de 1.4 y se "
                      "verifico para phi de 32 a 42 grados y D_f/B de 1 a 8. "
                      "El proyecto adopta la zapata corrida sin profundidad: "
                      "la zapata continua bajo los aleros y el empotramiento "
                      "del cabezal es el relleno del cauce, que la avenida "
                      "socava. Con L finita s_gamma < 1 resta y s_q > 1 "
                      "suma: ni una ni otra es el lado seguro siempre, y por "
                      "eso esta en la ventana",
        fuente="AASHTO LRFD 9a ed., Tabla 10.6.3.1.2a-3 y ec. 10.6.3.1.2a-10, "
               "pag. impresa 10-73 (PDF 1362)",
        reemplazado_por="Decision del proyectista con el EMS",
        resolucion=Libre(
            que_lo_fija="el proyectista",
            dominio="una de las tres opciones de la ventana",
        ),
    ),

    # --- VE-4a --- La fila del factor de resistencia de la estabilidad global
    # (AASHTO 11.6.3.7) con que el marco LRFD contrasta el FS DECLARADO de E4
    # y E5. Sin valor de archivo: la calidad de los parametros del EMS la
    # juzga quien lo lee, y la hoja de ruta no dice nada. Sin declarar, la
    # fila estatica decide solo si las dos opciones dan lo mismo y sale
    # INDICADOR «no decidida» si no (el patron de la fila A6 del armado).
    "fila_phi_estabilidad_global": Criterio(
        valor=None,                 # VACIO: la decide quien lee el EMS
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   parametros_bien_definidos         phi = 0.75 (FS objetivo 1.333)
        #   parametros_variables_o_limitados  phi = 0.65 (FS objetivo 1.538)
        sensibilidad=("parametros_bien_definidos",
                      "parametros_variables_o_limitados"),
        concepto="Fila del factor de resistencia de AASHTO 11.6.3.7 para la "
                 "estabilidad global del muro y del talud del cabezal (E4 y "
                 "E5) en el estado limite de resistencia: parametros "
                 "geotecnicos y estratigrafia bien definidos (0.75) o muy "
                 "variables o con informacion limitada (0.65)",
        justificacion="Decide el minimo del marco LRFD con que se contrasta "
                      "el factor de seguridad declarado de E4 y E5 "
                      "(`estabilidad_global_declarada`, VE-4a): FS >= 1/phi, "
                      "por la lectura del comentario C11.6.3.7 (cita "
                      "AASHTO_LRFD_9.C11.6.3.7#FS). La fuente da las dos "
                      "filas y la condicion de cada una (cita "
                      "AASHTO_LRFD_9.11.6.3.7#PHI), y esa condicion -- si los "
                      "parametros y la estratigrafia del EMS estan bien "
                      "definidos -- es un juicio sobre el estudio de suelos "
                      "real, que el programa no tiene. La hoja de ruta no la "
                      "fija (§9.3 da solo los FS de E.050, del marco ASD). "
                      "Por eso no tiene valor de archivo. Sin declarar, la "
                      "fila estatica cumple si el FS alcanza 1/0.65 y no "
                      "cumple si no alcanza ni 1/0.75; entre los dos el "
                      "veredicto depende de esta fila y se DETIENE: la fila "
                      "LRFD no se emite, E4 o E5 vuelve a pendientes y el "
                      "punto lleva el Bloqueo de este criterio (VE-5 fixve4; "
                      "hasta ahi salia indicador «no decidida» y contaba "
                      "como cumplida). Bajo sismo no hay eleccion: 11.5.8 "
                      "fija 0.9",
        fuente="AASHTO LRFD 9a ed., 11.6.3.7 y C11.6.3.7, pag. impresa 11-25 "
               "(PDF 1494; citas AASHTO_LRFD_9.11.6.3.7#PHI y "
               "AASHTO_LRFD_9.C11.6.3.7#FS): las dos filas, no cual es la del "
               "cabezal. Los numeros, en "
               "constantes_normativas.PHI_ESTABILIDAD_GLOBAL_11_6_3_7",
        reemplazado_por="La calidad de los parametros geotecnicos que el EMS "
                        "del expediente declare para cada cruce",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el geotecnista, por la calidad "
                        "de los parametros y de la estratigrafia del EMS",
            dominio="una de las dos filas de la ventana",
        ),
    ),

    # --- VE-4d --- (ficha T7B-02) EL DESBORDE ADMITIDO de V8: dos criterios,
    # detras de los nueve de T-7b (que van seguidos) y no junto al umbral.
    "caudal_unitario_admisible_desborde_m2s": Criterio(
        # SIN VALOR DE ARCHIVO, como el umbral: lo lee V8 solo con
        # «desborde_admitido_con_terraplen_protegido» declarado, y ninguna
        # corrida del fixture lo alcanza.
        valor=None,                 # VACIO: bloquea V8 con el desborde admitido
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        positivo=True,
        concepto="Caudal unitario sobre la plataforma (m3/s por metro de "
                 "cresta) que la proteccion del terraplen admite: el umbral "
                 "de V8 con el desborde admitido",
        justificacion="Decide cuando el desborde de la plataforma con el "
                      "caudal del evento extremo deja de ser admisible. La "
                      "fuente acepta el desborde (HDS-5 num. 5.4.5, cita "
                      "HDS5_3ED.5.4.5#DESBORDE_ACEPTADO) y, si es frecuente, "
                      "remite la proteccion del talud de aguas abajo a las "
                      "guias de HEC-23 (cita HDS5_3ED.5.4.5#HEC23), que no "
                      "estan en el repositorio de normas; no fija ningun "
                      "limite de tirante, velocidad ni caudal sobre la via. "
                      "El proyecto juzga «no colapsa» con el caudal "
                      "unitario, Q_plataforma / L, que es la magnitud con "
                      "que se dimensiona la proteccion de un terraplen "
                      "desbordado y la que el reparto entrega sin suponer "
                      "nada mas (el tirante y la velocidad sobre la cresta "
                      "dependen del perfil del flujo, que no se calcula). "
                      "Lo que no resuelve: el valor es el de la proteccion "
                      "que el expediente diseñe, y por eso no se elige aqui",
        fuente="PENDIENTE - diseño de la proteccion del talud de aguas abajo "
               "del terraplen (HDS-5 num. 5.4.5, pag. impresa 5.17, remite a "
               "HEC-23, Design Guideline 5, que no esta en el repositorio de "
               "normas)",
        reemplazado_por="El caudal unitario de diseño de la proteccion del "
                        "talud de aguas abajo (enrocado o suelo-cemento), "
                        "con su memoria adjunta",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el diseño de la proteccion del "
                        "terraplen",
            dominio="m3/s por metro de cresta, > 0",
        ),
    ),

    "coeficientes_desborde_plataforma": Criterio(
        # LA FIGURA 3.11 DEL HDS-5, DIGITALIZADA, con C_r en SI (VE-5
        # fixve4: la conversion que la pagina 3.15 imprime es
        # constantes_normativas.K_CD_DESBORDE_SI, y la lectura en unidades de
        # la figura es `_FIGURA_3_11_C_R_LEIDA`, arriba). Es una LECTURA de una figura y por eso es [C]
        # y no [N]: la hoja de ruta no trae el desborde, y el registro no
        # tiene tipo para un abaco (ver 'N_cq_N_gammaq_meyerhof'). A
        # diferencia de aquel, aqui la lectura no depende de la geometria
        # del punto: son cinco curvas de una variable, y se leen una vez.
        #
        # COMO SE LEYO (VE-4d, 2026-11-20): la figura es una imagen
        # (hif12026.pdf, PDF 98, imagen 261, 1700 x 1754 px). Se calibraron
        # los ejes por sus lineas de rejilla (panel A: 0.16 en x = 245.5 px
        # y 0.30 en 696.5 px; 3.10 en y = 535 px y 2.90 en 792 px; panel B:
        # 0 en x = 215 px y 4.0 en 761 px, 3.10 en y = 1059 px y 2.50 en
        # 1475 px; panel C: 0.6 en x = 1089 px y 1.0 en 1635 px, 1.00 en y =
        # 799 px y 0.50 en 1475 px) y se tomo, por columna, la mediana de
        # los pixeles rojos (Paved) y azules (Gravel) del trazo. La
        # resolucion es ~0.001 en C_r y ~0.001 en k_t; el grosor del trazo,
        # ~0.005. `tests/test_ve4d_v8_desborde.py` la contrasta con las dos
        # lecturas que el ejemplo DG 1.5 imprime (2.7 y 2.92), y el test
        # marcado `pdf` la REPITE sobre el PDF.
        #
        # Cada curva es una serie de pares (abscisa, ordenada) que M4
        # interpola linealmente; fuera de la primera y la ultima abscisa no
        # hay coeficiente («metodo no evaluable»), salvo k_t por debajo del
        # inicio de su curva, que vale 1 (vertedero libre).
        valor={
            # El rotulo de los paneles A («HWr/Lr > 0.15») y B («<= 0.15»).
            "limite_HWr_sobre_Lr": 0.15,
            # --- VE-5 fixve4 --- Paneles A y B EN SI: las curvas de C_r de
            # la figura (ft^0.5/s, transcritas en `_FIGURA_3_11_C_R_LEIDA`)
            # multiplicadas por constantes_normativas.K_CD_DESBORDE_SI
            # (0.552, cita HDS5_3ED.3.1.5#CD_SI). Una lectura que se declare
            # en su lugar va tambien en m^0.5/s.
            "Cr_profundo_si": _FIGURA_3_11_C_R_EN_SI["Cr_profundo"],
            "Cr_somero_si": _FIGURA_3_11_C_R_EN_SI["Cr_somero_m"],
            # Panel C: abscisa h_t/HW_r; k_t = 1 a la izquierda del primer
            # punto (donde la curva deja el borde superior del cuadro) y
            # ningun valor a la derecha del ultimo (k_t = 0.50, el pie del
            # cuadro).
            "kt": {
                "pavimentada": ((0.83, 1.000), (0.84, 0.993), (0.86, 0.977),
                                (0.88, 0.958), (0.90, 0.927), (0.92, 0.887),
                                (0.94, 0.818), (0.95, 0.775), (0.96, 0.722),
                                (0.97, 0.648), (0.98, 0.548), (0.9815, 0.500)),
                "grava": ((0.775, 1.000), (0.80, 0.989), (0.82, 0.980),
                          (0.84, 0.960), (0.86, 0.938), (0.88, 0.911),
                          (0.90, 0.879), (0.92, 0.824), (0.94, 0.735),
                          (0.95, 0.680), (0.96, 0.616), (0.97, 0.535),
                          (0.9718, 0.500)),
            },
        },
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Coeficiente de descarga del flujo sobre la plataforma: las "
                 "curvas C_r (desborde profundo y somero, en m^0.5/s) y k_t "
                 "(sumergencia) de la Figura 3.11 del HDS-5, digitalizadas y "
                 "convertidas a SI",
        justificacion="Da el coeficiente de la Ec. 3.9 del HDS-5 (Q_o = C_d "
                      "L HW_r^1.5, cita HDS5_3ED.3.1.5#EC_3_9) con que V8 "
                      "reparte el caudal del evento extremo entre el "
                      "conducto y la plataforma cuando el desborde se "
                      "admite. El vacio es de la hoja de ruta, que no trae "
                      "el desborde; lo cubre el HDS-5, que define C_d = k_t "
                      "C_r con las curvas de la Figura 3.11 (cita "
                      "HDS5_3ED.F3.11) en ft^0.5/s; el criterio las guarda "
                      "convertidas a SI con la conversion que la fuente "
                      "imprime, 0.552 (cita HDS5_3ED.3.1.5#CD_SI, "
                      "constantes_normativas.K_CD_DESBORDE_SI: no es un campo "
                      "declarable desde VE-5 fixve4). La figura distingue la cresta "
                      "pavimentada de la de grava; cual es la de esta via lo "
                      "dice 'condicion_pavimento'. Lo que no resuelve: la "
                      "figura es un abaco y su lectura tiene la resolucion "
                      "del trazo (del orden de 0.01 en C_r); fuera de sus "
                      "ejes no hay coeficiente, y el calculo se detiene",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), num. 3.1.5 «Roadway "
               "Overtopping», pag. impresa 3.15 (PDF 97), Ec. 3.9 y la "
               "conversion a SI; Figura 3.11 «Discharge coefficients for "
               "roadway overtopping», pag. impresa 3.16 (PDF 98), leida por "
               "imagen. Fuente tecnica, no norma peruana",
        reemplazado_por="Las curvas de la fuente original (HDS-1 / HY-7) o "
                        "una calibracion del vertedero para la seccion real "
                        "de la via, con su memoria",
        resolucion=Libre(
            que_lo_fija="la Figura 3.11 del HDS-5, digitalizada en VE-4d; el "
                        "proyectista puede declarar otra lectura con su "
                        "fuente",
            dominio="las cinco curvas como series (abscisa, ordenada) "
                    "crecientes en la abscisa; C_r y k_t > 0",
        ),
    ),

    # --- correcciones de T-7b (H7) --- El regimen del cabezal frente al
    # empuje: la HIPOTESIS de modelacion con que el ensamble calcula la
    # estabilidad externa, dicha como criterio y no escondida en un K_A.
    "regimen_cabezal": Criterio(
        valor="cedente",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   cedente      el muro se desplaza lo bastante para movilizar la
        #       resistencia del relleno: empuje ACTIVO (cuña o Coulomb) y,
        #       bajo sismo, el de 11.6.5.3. Es lo que el ensamble calcula.
        #   no_cedente   el muro no puede ceder (estribo con aleros
        #       estructurales, 11.6.5.4): reposo K0 en la estatica (o el
        #       activo con la superficie real si da mas, porque K0 es de
        #       terreno horizontal) y k_h = 1.0·k_h0 con resultante en h/2
        #       bajo sismo. --- VE-5 (lote M9, ficha T7B-14) --- Hasta VE-5
        #       el ensamble lo detenia con «metodo no evaluable»; desde VE-5
        #       lo calcula (`M9.cargas_del_cabezal`), y el empuje sismico
        #       total lo declara 'empuje_sismico_muro_que_no_cede'.
        sensibilidad=("cedente", "no_cedente"),
        concepto="Si el cabezal se modela como muro que cede (empuje "
                 "activo) o como muro que no cede (empuje en reposo y "
                 "presiones sismicas de muro rigido)",
        justificacion="Decide con que empuje se calcula la estabilidad "
                      "externa del cabezal y con que coeficiente salen las "
                      "solicitaciones que T-7c armara. Los metodos de "
                      "11.6.5.3 suponen que el muro puede ceder lo bastante "
                      "para movilizar la resistencia del relleno (AASHTO "
                      "C11.6.5.4, cita AASHTO_LRFD_9.C11.6.5.4#CEDENTE), y "
                      "para los "
                      "muros que no ceden la fuente manda k_h = 1.0·k_h0 "
                      "(11.6.5.4, cita AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE) y "
                      "su comentario pone entre ellos a los estribos con "
                      "aleros estructurales, dice que las presiones pueden "
                      "superar a las de Mononobe-Okabe, que la resultante "
                      "puede subir a h/2, y que el muro que no cede se "
                      "diseña en resistencia con K0 (cita "
                      "AASHTO_LRFD_9.C11.6.5.4#K0). Un cabezal monolitico "
                      "con el barril y los aleros se parece a ese caso, y "
                      "ninguna fuente dice cual es. El proyecto adopta "
                      "«cedente» para la estabilidad EXTERNA, que es lo que "
                      "el ensamble calcula -- el vuelco y el deslizamiento "
                      "del conjunto movilizan el empuje activo -- y lo "
                      "declara como hipotesis de modelacion. Las "
                      "solicitaciones por elemento salen con ese mismo "
                      "coeficiente y lo llevan marcado, con el K0 de "
                      "3.11.5.2 al lado: si T-7c o el proyectista juzgan "
                      "que la pantalla no cede, su armado iria con K0 (en "
                      "A-01, del orden de un tercio a la mitad mas de "
                      "empuje). «no_cedente» esta en la ventana y, desde "
                      "VE-5, se calcula: empuje en reposo en la estatica, "
                      "con su factor de carga, y k_h = 1.0·k_h0 con la "
                      "resultante en h/2 bajo sismo (ficha T7B-14)",
        fuente="AASHTO LRFD 9a ed., 11.6.5.4 y C11.6.5.4, pag. impresa "
               "11-32 (PDF 1501; citas AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE, "
               "AASHTO_LRFD_9.C11.6.5.4#CEDENTE y "
               "AASHTO_LRFD_9.C11.6.5.4#K0); 3.11.5.2, pag. impresa 3-120 "
               "(PDF 174; cita AASHTO_LRFD_9.3.11.5.2#K0)",
        reemplazado_por="Analisis numerico de la interaccion del cabezal con "
                        "el relleno, aprobado por el Propietario (11.6.5.4)",
        resolucion=Libre(
            que_lo_fija="el proyectista: es la hipotesis con que se modela "
                        "el cabezal, y ninguna fuente la fija",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    # --- T-7c --- (cadena T) El armado del cabezal: con que empuje se arma,
    # con que materiales, de que catalogo salen las barras propuestas, que
    # se hace con los minimos de las dos normas y con que criterio se juzga
    # la traccion del cabezal de gravedad en ciclopeo. Seis criterios, todos
    # de expediente: los consume `M9.armado_del_cabezal`, que solo corre a
    # ese alcance (la Fase 9 se difiere entera a nivel de perfil).
    "regimen_resistencia_elementos_cabezal": Criterio(
        valor="no_cedente_k0",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   no_cedente_k0  la pantalla, la zapata y los aleros se arman con
        #       el empuje en REPOSO (K0 de AASHTO 3.11.5.2, factor de carga
        #       de la fila «En reposo», sin friccion muro-relleno), tomando
        #       en cada seccion la MAYOR de esa solicitacion y la del muro
        #       que cede; bajo sismo, el empuje que el ensamble entrega y la
        #       resultante a h/2 si da mas momento.
        #   cedente        se arman con las solicitaciones del ensamble de
        #       T-7b tal como salen (empuje activo de la cuña o de Coulomb).
        sensibilidad=("no_cedente_k0", "cedente"),
        concepto="Empuje de tierras con que se calcula la RESISTENCIA de "
                 "los elementos del cabezal (pantalla, zapata y aleros): en "
                 "reposo, de muro que no cede, o activo, de muro que cede",
        justificacion="Decide con que empuje se arma el cabezal, que no es "
                      "la misma pregunta que la de su estabilidad externa "
                      "('regimen_cabezal', que sigue en «cedente»: el vuelco "
                      "y el deslizamiento del conjunto movilizan el empuje "
                      "activo por definicion del mecanismo). La fuente "
                      "recomienda proyectar con el empuje en reposo los "
                      "muros que toleran poco o ningun movimiento (AASHTO "
                      "C3.11.1, cita AASHTO_LRFD_9.C3.11.1#REPOSO) y liga el "
                      "muro que no cede con el empuje en reposo en el estado "
                      "limite de resistencia (C11.6.5.4, cita "
                      "AASHTO_LRFD_9.C11.6.5.4#K0); del muro en voladizo "
                      "tipico de mas de 5.0 ft dice que su deformacion basta "
                      "para desarrollar el empuje activo (C3.11.5.2, cita "
                      "AASHTO_LRFD_9.C3.11.5.2#ACTIVO). Ninguna dice cual de "
                      "los dos es el cabezal de una alcantarilla. El "
                      "proyecto adopta el reposo -- decision del dueño del "
                      "proyecto, registrada en la ficha T7C-02 -- porque el "
                      "cabezal es monolitico con el "
                      "barril y con los aleros, que lo arriostran, y porque "
                      "es el lado seguro de la resistencia: mas empuje, mas "
                      "acero. Lo que la eleccion NO resuelve y la memoria "
                      "dice: el K0 de la ec. 3.11.5.2-1 es de terreno "
                      "horizontal y detras del cabezal el relleno sube, de "
                      "modo que el reposo calculado es una cota inferior del "
                      "real; por eso el armado toma en cada seccion la mayor "
                      "de la solicitacion en reposo y la del muro que cede "
                      "(que si lleva la pendiente, por la cuña de tanteo), y "
                      "avisa cuando el armado cambia de una a otra. Bajo "
                      "sismo la fuente no da un coeficiente de reposo: manda "
                      "no reducir k_h (11.6.5.4) y pide considerar la "
                      "resultante a h/2 (cita "
                      "AASHTO_LRFD_9.C11.6.5.4#H_MEDIOS). Un solo regimen "
                      "(decision 12 del dueño, con la verificacion "
                      "independiente de VE-3): el reposo es el del archivo y "
                      "«cedente» se declara solo con justificacion -- aleros "
                      "con junta, desplazamiento aceptado por el Propietario "
                      "y pantalla por encima de la altura de C3.11.5.2 --, y "
                      "es el unico con que la corrida acepta la reduccion de "
                      "k_h de 'factor_muro_eleccion'",
        fuente="AASHTO LRFD 9a ed., C3.11.1, pag. impresa 3-117 (PDF 171); "
               "3.11.5.2 y C3.11.5.2, pag. impresa 3-120 (PDF 174); 11.6.5.4 "
               "y C11.6.5.4, pag. impresa 11-32 (PDF 1501). Factor de carga "
               "del empuje en reposo: Manual de Puentes, Tabla 2.4.5.3.1-2, "
               "fila «En reposo» (1.35 / 0.90), [N] en "
               "constantes_normativas.TABLA_GAMMA_P_FILAS",
        reemplazado_por="Analisis de la interaccion del cabezal con el "
                        "relleno, el barril y los aleros que diga cuanto se "
                        "desplaza la pantalla",
        resolucion=Libre(
            que_lo_fija="el proyectista: ninguna fuente dice si la pantalla "
                        "de un cabezal cede",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "fc_cabezal_mpa": Criterio(
        valor=21.0,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        # De la Clase E (17.5 MPa) a la Clase A (35 MPa) de la Tabla 503-07
        # del EG-2013: las clases de concreto estructural con que se puede
        # especificar un cabezal armado.
        sensibilidad=(17.5, 35.0),
        concepto="Resistencia especificada a la compresion del concreto del "
                 "cabezal armado (pantalla, zapata y aleros), f'c, en MPa",
        justificacion="Decide la resistencia del concreto con que se "
                      "calculan la flexion y el cortante del cabezal. "
                      "Ninguna fuente la fija: el EG-2013 (Tabla 503-07, "
                      "cita EG2013.503.04#T503_07) da las CLASES de concreto "
                      "estructural y sus resistencias minimas, no cual "
                      "lleva un cabezal. El proyecto adopta la Clase D, 21 "
                      "MPa, que es la menor de las de concreto reforzado de "
                      "uso corriente en obras de drenaje; es el lado seguro "
                      "del calculo de resistencia (con mas f'c la seccion "
                      "resiste mas) y NO el de la durabilidad: si el "
                      "analisis quimico del EMS ('exposicion_quimica_ems') "
                      "pide un f'c minimo mayor por las Tablas 4.2 y 4.4 de "
                      "E.060, el armado lo dice como incumplimiento "
                      "(verificacion A7, que decide cuando el dato existe; "
                      "sin el, un aviso) y hay que subir este valor. La "
                      "ventana son las clases E a A de la misma tabla; por "
                      "debajo de 17 MPa E.060 9.4.1 no admite concreto "
                      "estructural",
        fuente="EG-2013 Seccion 503, num. 503.04, Tabla 503-07 'Clases de "
               "concreto estructural', pag. impresa 912 (PDF 920): clases y "
               "resistencias minimas, no la clase del cabezal",
        reemplazado_por="La especificacion de concreto del expediente, con "
                        "el analisis quimico del EMS delante",
        resolucion=Libre(
            que_lo_fija="el proyectista, eligiendo la clase de concreto de "
                        "la Tabla 503-07 del EG-2013",
            dominio="MPa, entre 17.5 (Clase E) y 35 (Clase A)",
        ),
    ),

    "acero_refuerzo_cabezal": Criterio(
        valor="A615_grado_60",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("A615_grado_60", "A706_grado_60"),
        concepto="Designacion del acero de refuerzo del cabezal: fija la "
                 "fluencia de calculo y la razon fluencia / rotura del "
                 "acero minimo de AASHTO 5.6.3.3",
        justificacion="Decide que acero arma el cabezal. La fluencia (420 "
                      "MPa en las dos designaciones, el Grado 60) y el "
                      "factor γ3 del momento de agrietamiento (0.67 para "
                      "AASHTO M 31 / ASTM A615 Grado 60 y 0.75 para ASTM "
                      "A706 Grado 60: AASHTO 5.6.3.3, cita "
                      "AASHTO_LRFD_9.5.6.3.3#MINIMO) NO se eligen aqui: "
                      "salen de la designacion y viven en "
                      "constantes_normativas (FY_ACERO_MPA, GAMMA_3_AASHTO). "
                      "Lo que se elige es la designacion, y ninguna fuente "
                      "la fija: E.060 3.5.3.1 admite las barras de la NTP "
                      "341.031, que es la equivalente de ASTM A615. El "
                      "proyecto adopta A615 Grado 60 por ser el acero "
                      "corrugado de suministro corriente; con A706 el acero "
                      "minimo por agrietamiento sube un 12 %",
        fuente="AASHTO LRFD 9a ed., 5.6.3.3, pag. impresa 5-43 (PDF 402): "
               "tabla de γ3 por designacion; E.060 3.5.3.1, pag. 32 (NTP "
               "341.031). Ninguna fija la designacion del proyecto",
        reemplazado_por="La especificacion de acero del expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista, con la especificacion de "
                        "materiales del expediente",
            dominio="una de las dos designaciones de la ventana",
        ),
    ),

    "catalogo_barras_refuerzo_cabezal": Criterio(
        valor={
            # designacion: (diametro nominal en mm, area nominal en mm2)
            "barras": {"3/8": (9.5, 71.0), "1/2": (12.7, 129.0),
                       "5/8": (15.9, 199.0), "3/4": (19.1, 284.0),
                       "1": (25.4, 510.0)},
            # de mayor a menor: se propone el mayor que cumple
            "espaciamientos_m": (0.30, 0.25, 0.20, 0.175, 0.15, 0.125,
                                 0.10),
            "barra_minima_principal": "1/2",
            "barra_reparto": "3/8",
        },
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        sensibilidad=(
            "El catalogo es una PROPUESTA y no una exigencia: con otra "
            "barra minima principal ('3/8' en vez de '1/2') o con otra "
            "serie de espaciamientos cambian la barra y el espaciamiento "
            "propuestos, no el acero requerido ni el minimo, que salen del "
            "calculo. Lo que el plano lleve tiene que cumplir el acero "
            "adoptado y el espaciamiento maximo de la tabla de armado",),
        concepto="Catalogo de barras corrugadas y de espaciamientos de "
                 "donde el programa PROPONE el armado de cada cara del "
                 "cabezal, y la regla de la propuesta",
        justificacion="Decide que barra y que espaciamiento se proponen "
                      "para cada cara: el programa calcula el acero "
                      "adoptado (el mayor del requerido y del minimo) y el "
                      "espaciamiento maximo, y de este catalogo toma, "
                      "empezando por la barra minima y subiendo de "
                      "diametro, la primera barra que con el MAYOR "
                      "espaciamiento de la serie no superior al maximo da "
                      "al menos ese acero. Ninguna fuente fija un catalogo: "
                      "las designaciones, diametros y areas son las "
                      "nominales de las barras de ASTM A615 / NTP 341.031 "
                      "(3/8\" a 1\"), norma que NO esta en normas/ y que la "
                      "sesion no pudo verificar contra su PDF -- el "
                      "proyectista las confirma con la ficha del "
                      "fabricante --; la serie de espaciamientos (de 0.30 a "
                      "0.10 m) y la barra minima de 1/2\" en la armadura "
                      "principal son practica de detalle del proyecto. El "
                      "programa propone y no impone: el proyectista puede "
                      "armar con otra barra siempre que cumpla la tabla",
        fuente="Sin fuente unica. Designaciones y areas nominales: ASTM "
               "A615 / NTP 341.031, no disponible en normas/ (no "
               "verificado contra PDF). Serie de espaciamientos y barra "
               "minima: practica de detalle, eleccion del proyecto",
        reemplazado_por="La ficha tecnica del proveedor de acero y el "
                        "criterio de detalle del proyectista",
        resolucion=Libre(
            que_lo_fija="el proyectista: es una regla de propuesta, no un "
                        "valor de norma",
            dominio="barras: designacion -> (diametro mm, area mm2); "
                    "espaciamientos en m, de mayor a menor; las dos barras "
                    "nombradas tienen que estar en el catalogo",
        ),
    ),

    "regla_minimos_constructivos_cabezal": Criterio(
        valor="mas_exigente_aashto_e060",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("mas_exigente_aashto_e060", "solo_aashto"),
        concepto="Que se hace con el acero minimo y el espaciamiento "
                 "maximo del cabezal, que AASHTO LRFD y E.060 fijan cada "
                 "una por su lado",
        justificacion="Decide cual de los dos juegos de minimos "
                      "constructivos se aplica. En RESISTENCIA rige AASHTO "
                      "LRFD Seccion 5 y E.060 solo contrasta, porque cargas "
                      "y resistencias no se cruzan entre marcos; los "
                      "minimos constructivos -- acero minimo de cada cara, "
                      "espaciamiento maximo, capas -- no dependen de las "
                      "cargas y si se pueden comparar. AASHTO pide el acero "
                      "de 5.6.3.3 en la cara en traccion y el de retraccion "
                      "y temperatura de 5.10.6 en cada cara y direccion, "
                      "con el espaciamiento de 5.10.3.2; E.060 pide las "
                      "cuantias de muros de 14.3.1 (0,0020 horizontal y "
                      "0,0015 vertical, sobre el area bruta), las de losas "
                      "y zapatas de 9.7.2 y 10.5.4 (0,0018, y 0,0012 en la "
                      "cara en traccion) y el espaciamiento de 14.3.3. "
                      "Ninguna deroga a la otra sobre una obra vial "
                      "peruana -- la primera es la fuente tecnica del "
                      "diseño y la segunda la norma local de concreto, "
                      "aplicada por analogia --, y el proyecto aplica la "
                      "mas exigente de las dos en cada cara, que es la "
                      "misma regla del mayor que la §0.2 de la hoja de ruta "
                      "usa para el recubrimiento. «solo_aashto» queda en la "
                      "ventana para quien lea la Via 1 a la letra",
        fuente="AASHTO LRFD 9a ed., 5.6.3.3, 5.10.6 y 5.10.3.2 (citas "
               "AASHTO_LRFD_9.5.6.3.3#MINIMO, "
               "AASHTO_LRFD_9.5.10.6#TEMPERATURA, "
               "AASHTO_LRFD_9.5.10.3.2#ESPACIAMIENTO); E.060 14.3.1, "
               "14.3.3, 9.7.2 y 10.5.4 (citas E060.14.3.1, E060.14.3.3, "
               "E060.9.7.2#TEMPERATURA, E060.10.5.4#LOSAS). Ninguna dice "
               "cual prevalece sobre un cabezal vial",
        reemplazado_por="Una especificacion del Propietario que fije el "
                        "juego de minimos del expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista: es la regla de conflicto entre "
                        "dos fuentes, y ninguna la escribe",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "criterio_traccion_cabezal_ciclopeo": Criterio(
        valor="tracciones_nulas",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("tracciones_nulas", "traccion_admisible_e060"),
        concepto="Con que criterio se juzga la traccion del cabezal de "
                 "gravedad en concreto ciclopeo: sin tracciones (resultante "
                 "en el tercio central) o con la traccion que E.060 admite",
        justificacion="Decide cual de dos verificaciones DETIENE el cabezal "
                      "de gravedad en la base y a media altura del cuerpo. "
                      "La clasica del muro de gravedad pide "
                      "tracciones nulas con cargas de servicio: la "
                      "resultante dentro del tercio central de la base (e "
                      "<= B/6) y de la seccion del cuerpo (e <= t/6). E.060 "
                      "no la exige en el CUERPO: para el concreto simple "
                      "admite una traccion de φ·0,42·√f'c (22.5.3, ec. 22-7; "
                      "cita E060.22.5.3#TRACCION), con φ = 0,5 y f'c no mayor "
                      "de 10 MPa en el ciclopeo (22.10.2.3; cita "
                      "E060.22.10.2.3#PHI), y solo distingue el caso del "
                      "tercio central para permitir un metodo empirico "
                      "(22.6.3; cita E060.22.6.3#TERCIO). En las juntas de "
                      "construccion si la prohibe (22.4.7; cita "
                      "E060.22.4.7#JUNTAS), y el arranque del cuerpo sobre "
                      "la zapata es una: por eso la verificacion del "
                      "arranque decide siempre, con las dos opciones, salvo "
                      "que se declare el vaciado monolitico "
                      "('junta_arranque_cabezal_ciclopeo'), y este criterio "
                      "decide las otras dos. El proyecto adopta las "
                      "tracciones nulas, que es lo mas exigente y lo que "
                      "pide el encargo de la cadena T (INFORME §4.6), y "
                      "calcula la de E.060 al lado, por analogia, con sus "
                      "cargas amplificadas; con la otra opcion decide la "
                      "traccion admisible de E.060 y las tracciones nulas "
                      "de la base y de media altura informan. AASHTO LRFD "
                      "no trae el concreto ciclopeo",
        fuente="E.060 22.5.3, 22.6.3 y 22.10.2.3, pags. 192 y 195 (citas "
               "E060.22.5.3#TRACCION, E060.22.6.3#TERCIO, "
               "E060.22.10.2.3#PHI): la traccion admisible; 22.4.7, pag. "
               "191 (cita E060.22.4.7#JUNTAS): ninguna traccion a traves de "
               "las juntas de construccion. Fuera de las juntas, el "
               "criterio de tracciones nulas no tiene numeral: es practica "
               "del muro de gravedad y eleccion del proyecto",
        reemplazado_por="Una especificacion del Propietario para muros de "
                        "gravedad en concreto ciclopeo",
        resolucion=Libre(
            que_lo_fija="el proyectista: E.060 admite traccion y el "
                        "proyecto elige no contar con ella",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "concreto_ciclopeo_cabezal": Criterio(
        valor={"fc_matriz_mpa": 14.0, "fraccion_piedra": 0.30},
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        sensibilidad={"fc_matriz_mpa": (14.0, 21.0),
                      "fraccion_piedra": (0.0, 0.30)},
        concepto="Especificacion del concreto ciclopeo del cabezal de "
                 "gravedad: resistencia de la matriz y fraccion de piedra "
                 "desplazadora en volumen",
        justificacion="Decide que concreto ciclopeo se especifica, que es "
                      "lo que las dos verificaciones del material contrastan "
                      "con sus "
                      "dos limites: f'c de la matriz no menor que el mayor "
                      "de los 10 MPa de E.060 22.10.1 y los 14 MPa de la "
                      "Clase G del EG-2013 (Tabla 503-07), y piedra "
                      "desplazadora no mayor del 30 % del volumen. Los "
                      "limites son de las fuentes; el valor especificado "
                      "es del proyecto, y se adopta en el limite de las dos "
                      "(Clase G: concreto simple Clase F, 14 MPa, con 30 % "
                      "de agregado ciclopeo), que es el menos resistente "
                      "que las fuentes admiten y por eso el lado seguro del "
                      "contraste de resistencia",
        fuente="EG-2013 Seccion 503, Tabla 503-07, Clase G, pag. impresa "
               "912 (PDF 920; cita EG2013.503.04#T503_07); E.060 22.10.1, "
               "pag. 194. Fijan los limites, no la especificacion",
        reemplazado_por="La especificacion de concreto ciclopeo del "
                        "expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista, dentro de los limites de E.060 "
                        "22.10 y de la Clase G del EG-2013",
            dominio="fc_matriz_mpa >= 14; 0 <= fraccion_piedra <= 0.30",
        ),
    ),

    # --- correcciones de T-7c ------------------------------------------------
    "clase_exposicion_fisuracion_cabezal": Criterio(
        valor=None,                 # VACIO: la declara el Propietario
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("clase_1", "clase_2"),
        concepto="Clase de exposicion del control de fisuracion de AASHTO "
                 "5.6.7 en el cabezal armado: Clase 1 (gamma_e = 1.00) o "
                 "Clase 2 (gamma_e = 0.75)",
        justificacion="Decide el espaciamiento maximo del refuerzo de cada "
                      "cara traccionada por fisuracion en servicio (fila A6 "
                      "del armado; correcciones de T-7c, H3). La fuente da "
                      "las dos clases y sus factores (cita "
                      "AASHTO_LRFD_9.5.6.7#GAMMA_E) y deja la eleccion al "
                      "Propietario: su comentario describe la Clase 1 como "
                      "la cota superior del ancho de fisura y propone la "
                      "Clase 2 para las subestructuras expuestas al agua "
                      "(cita AASHTO_LRFD_9.C5.6.7#CLASE_1). Un cabezal de "
                      "alcantarilla esta expuesto al agua del cauce, pero "
                      "ninguna fuente lo clasifica, y por eso no tiene valor "
                      "de archivo. Sin declarar, el armado no se detiene: "
                      "la barra propuesta respeta la Clase 1, que "
                      "es la menos exigente y la que cualquier clase pide, y "
                      "la fila A6 imprime los dos espaciamientos maximos y "
                      "sale como INDICADOR «no decidida» cuando el propuesto "
                      "solo cumple la Clase 1. Declarada, A6 decide y la "
                      "propuesta la respeta",
        fuente="AASHTO LRFD 9a ed., 5.6.7 y C5.6.7, pags. impresas 5-55 y "
               "5-56 (PDF 414 y 415; citas AASHTO_LRFD_9.5.6.7#FISURACION, "
               "#GAMMA_E y AASHTO_LRFD_9.C5.6.7#CLASE_1): las dos clases, no "
               "cual es la del cabezal",
        reemplazado_por="La clase de exposicion que el Propietario declare "
                        "para las subestructuras de la obra",
        resolucion=Libre(
            que_lo_fija="el Propietario, por la exposicion y la apariencia "
                        "que admita para la obra",
            dominio="una de las dos clases de la ventana",
        ),
    ),

    "junta_arranque_cabezal_ciclopeo": Criterio(
        valor="junta_de_construccion",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("junta_de_construccion", "vaciado_monolitico"),
        concepto="Como se vacia el cabezal de gravedad en concreto ciclopeo "
                 "en el encuentro de su cuerpo con la zapata: con junta de "
                 "construccion (la zapata primero) o monolitico",
        justificacion="Decide si la verificacion de tracciones nulas en el "
                      "arranque del cuerpo detiene el cabezal siempre o solo "
                      "con el criterio de tracciones nulas. E.060 22.4.7 "
                      "(cita "
                      "E060.22.4.7#JUNTAS) prohibe transmitir traccion a "
                      "traves de las juntas de construccion de un elemento "
                      "de concreto simple, y el encuentro del cuerpo con la "
                      "zapata lo es cuando la zapata se vacia primero, que es "
                      "la secuencia corriente. El proyecto adopta la junta "
                      "-- el lado exigente: la fila decide, y con las cargas "
                      "de servicio Y con las amplificadas de E.060 -- y deja "
                      "el vaciado monolitico como alternativa barrible, que "
                      "es una especificacion de obra que el plano tiene que "
                      "pedir (correcciones de T-7c, H5)",
        fuente="E.060 22.4.7, pag. 191 (cita E060.22.4.7#JUNTAS): la "
               "prohibicion; la secuencia de vaciado es del proyecto",
        reemplazado_por="La especificacion de vaciado del cabezal en el "
                        "expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista, con la secuencia de vaciado que el "
                        "plano especifique",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "espesor_min_zapata_concreto_simple_m": Criterio(
        valor=0.30,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        forma=FORMA_FLOAT,
        concepto="Espesor minimo de la zapata del cabezal de gravedad en "
                 "concreto ciclopeo, m (E.060 22.7.4)",
        justificacion="Decide el piso del espesor propuesto de la zapata del "
                      "cabezal de gravedad y el umbral de CB6 cuando ese "
                      "espesor se declara. La fuente (E.060 22.7.4, pag. 193; "
                      "cita E060.22.7.4#ZAPATA) fija 300 mm para las zapatas "
                      "de concreto simple estructural. Hasta el cierre de "
                      "T-7c vivia como constante [N] "
                      "(`ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M`); pasa a [N→] "
                      "porque E.060 es una norma de edificaciones y la "
                      "excepcion de la §0.2 de la hoja de ruta, que la hace "
                      "regir en el cabezal, cubre solo la durabilidad "
                      "(Cap. 4 y Art. 7.7): un minimo estructural de su "
                      "Cap. 22 aplicado a una obra vial es una analogia, "
                      "como el 15.7 de la zapata armada "
                      "('peralte_min_zapata_armada_m'). Pregunta 1 del "
                      "informe de la FASE A de T-7c, resuelta por el "
                      "orquestador",
        fuente="E.060, num. 22.7.4, pag. 193 (cita E060.22.7.4#ZAPATA), por "
               "analogia",
        reemplazado_por="Una norma vial que fije el espesor minimo de una "
                        "zapata de concreto simple",
        resolucion=Libre(
            que_lo_fija="E.060 22.7.4, aplicado por analogia",
            dominio="m, positivo",
        ),
    ),

    # --- VE-6 (lote M9, item 29 del censo; ficha T7C-10) -------------------
    "cuantia_minima_muro_e060": Criterio(
        valor=dict(CUANTIA_MIN_MURO_E060_14_3_1),
        # NIVEL MEDIDO: lo invoca la Fase 9 (`servicio._fase_9`, la etapa
        # «cuantia minima ... (9.4, referencia)», y `M9.cuantia_de_diseno`
        # por el armado), que solo corre a `--alcance expediente`.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Cuantias minimas del refuerzo de muro del cabezal "
                 "armado, horizontal y vertical (E.060 14.3.1)",
        justificacion="Decide el piso de cuantia de la pantalla y del alero "
                      "del cabezal armado (`M9.cuantia_de_diseno`, "
                      "`M9.verificar_cuantia` y la referencia 9.4 de la "
                      "memoria): rho_diseno = max(rho_calculado, "
                      "rho_minimo). La fuente (E.060 14.3.1, pag. 133) fija "
                      "0,0020 horizontal y 0,0015 vertical para los muros. "
                      "Hasta VE-6 vivia como constante [N] "
                      "(`CUANTIA_MIN_MURO`); pasa a [N→] por el mismo "
                      "argumento que movio el 0,30 m de 22.7.4 en el cierre "
                      "de T-7c ('espesor_min_zapata_concreto_simple_m'): E.060 "
                      "es una norma de edificaciones y la excepcion de la "
                      "§0.2 de la hoja de ruta que la hace regir en el "
                      "cabezal cubre la durabilidad (Cap. 4 y Art. 7.7), no "
                      "los minimos estructurales; un minimo de su Cap. 14 "
                      "aplicado a una obra vial es una analogia. El valor no "
                      "cambia. El minimo se aplica ENTERO porque el "
                      "expediente no ejerce la excepcion de 14.8.2 "
                      "(`M9.nota_excepcion_refuerzo_minimo`)",
        fuente="E.060, num. 14.3.1, pag. 133, por analogia; los muros de "
               "contencion en 14.8.1 y su excepcion en 14.8.2. Un valor por "
               "debajo de 14.3.1 se rechaza: bajaria de la norma que el "
               "criterio aplica",
        reemplazado_por="El retiro del contraste de E.060 si el proyecto "
                        "adopta solo AASHTO 5.10.6, o el ejercicio declarado "
                        "de 14.8.2",
        resolucion=Libre(
            que_lo_fija="E.060 14.3.1, aplicado por analogia",
            dominio="dict con 'horizontal' y 'vertical', cuantias positivas",
        ),
    ),

    "edicion_que_rige_el_expediente": Criterio(
        valor=None,                 # VACIO: lo declara el proyectista
        # NIVEL NO MEDIBLE POR CORRIDA, y se dice con esas palabras: ningun
        # modulo lo invoca (`variables_entrada.consumido_por` vacio), de modo
        # que ninguna de las tres corridas de tests/test_nivel_medido.py lo
        # puede contradecir, y esta censado en SIN_CONSUMIDOR_Y_SIN_MEDIDA.
        # El argumento: es la decision de marco normativo del expediente, no
        # un numero del perfil. El perfil se calcula contra los PDF que estan
        # en normas/, con cada cita anclada por sha1 a la edicion citada;
        # cambiar de edicion es conseguir el documento, incorporarlo al
        # registro y reverificar cada cita, que es trabajo de expediente.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_STR,
        # LA VENTANA ES SIMBOLICA Y CERRADA, como la de
        # 'homogeneidad_serie_fen': dos opciones y no hay tercera, y vale
        # para las seis fuentes TECNICAS a la vez. El Manual de Puentes SALIO
        # de esta ventana en EXT-6 (EXT-N-01, PC-26): es una norma LEGAL,
        # aprobada y derogada por resolucion del MTC, y elegir su edicion
        # citada no es una preferencia tecnica sino una cuestion de regimen
        # transitorio; tiene su propio criterio,
        # 'edicion_legal_que_rige_el_expediente'. Una eleccion por fuente NO
        # cabe aqui a proposito: `establecer_valor_dinamico` solo puede
        # validar contra esta ventana, y un valor con excepciones seria una
        # tercera forma que ninguna guardia comprueba; si hiciera falta, es
        # un criterio por fuente, no una excepcion en prosa.
        sensibilidad=(
            "la edicion citada en el registro: la que esta en normas/ y "
            "contra la que estan verificadas las citas (sha1)",
            "la edicion vigente del emisor a la fecha del expediente: exige "
            "conseguirla, incorporarla al registro como Fuente y reverificar "
            "contra ella cada cita que hoy se apoya en la citada"),
        concepto="Edicion que rige el expediente en las fuentes tecnicas "
                 "(AASHTO, ASTM) cuyo emisor publica una edicion posterior a "
                 "la citada en el registro",
        justificacion=(
            "La verificacion de vigencia del registro encontro que ocho de "
            "las fuentes presentes tienen edicion posterior publicada por su "
            "emisor. En una el registro ya dice cual gobierna (las dos "
            "ediciones de HDS-5 conviven en normas/ y una discrepancia "
            "resuelta lo fija); otra es una norma legal peruana derogada por "
            "resolucion y tiene su propio criterio, porque elegir su edicion "
            "citada depende del regimen transitorio y no de una preferencia "
            "tecnica; y en las seis restantes, todas normas tecnicas de "
            "EE.UU., hay una eleccion tecnica pendiente: AASHTO LRFD (citada "
            "la 9a ed. (2020); publicada la 10a ed. (2024)), AASHTO M 170M "
            "(citada M 170M-04; vigente M 170M-23), AASHTO M 36 (citada "
            "M 36-03; vigente M 36M/M 36-24), ASTM A760/A760M (citada -10; "
            "vigente -25), ASTM A796/A796M (citada -13; vigente -21) y AASHTO "
            "M 294 (traduccion de la -11; vigente -25). La edicion de estas "
            "seis no la fija una resolucion peruana, pero tampoco es cierto "
            "que nadie la mande: el Manual de Puentes adapta la AASHTO LRFD "
            "en su 7a ed. (2014) y permite considerar sus actualizaciones "
            "(registro MP.INTRODUCCION#LRFD_2014), de modo que citar una "
            "edicion posterior a la 7a esta autorizado y elegir entre la "
            "9a y la 10a corresponde a la entidad y/o propietario, a "
            "propuesta del proyectista, que es quien lo declara aqui; para "
            "las cinco normas de "
            "producto y practica, ninguna fuente peruana nombra edicion. Se "
            "declara vacia: elegir la citada mantiene valido el registro tal "
            "como esta; elegir la vigente obliga a conseguir cada documento, "
            "incorporarlo como Fuente y reverificar contra el cada cita, y "
            "hasta entonces el expediente citaria una edicion que no tiene. "
            "La ventana es simbolica y cerrada: la eleccion vale para las "
            "seis fuentes a la vez, y una eleccion distinta por fuente no "
            "cabe en ella --- exigiria un criterio por fuente, y se abriria "
            "entonces, no aqui ---. Lo que no cambia con la eleccion: ninguna "
            "cita y ningun valor de calculo; la vigencia es un metadato de "
            "la fuente, y el sha1 sigue anclando cada cita a la edicion "
            "contra la que se verifico"),
        fuente=("Registro normativo: el campo `vigencia` de cada Fuente "
                "presente (`fuentes.estado_de_vigencia`) y "
                "`fuentes.fuentes_con_eleccion_de_edicion_pendiente_tecnica`, "
                "que deriva de el las seis fuentes de arriba; un test exige "
                "que esta ficha las nombre todas y solo a ellas. El ancla del "
                "Manual de Puentes a la AASHTO LRFD 2014 (7a ed.) y su permiso "
                "de considerar actualizaciones: MP Introduccion, pag. impresa "
                "43 (PDF 44), registro MP.INTRODUCCION#LRFD_2014 y "
                "DIS-MP-LRFD-EDICION. Emisores consultados por busqueda web: "
                "AASHTO (AASHTO Journal, tienda y lista HM-44), ASTM "
                "(store.astm.org), FHWA (biblioteca de hidraulica)"),
        # LO QUE CIERRA EL VACIO, que es la columna «Que lo resuelve» de la
        # memoria: no un ensayo ni un dato, sino una declaracion del
        # proyectista con lo que ella arrastra si elige la vigente.
        reemplazado_por=("Declaracion del proyectista sobre el marco normativo "
                         "tecnico del expediente (edicion citada o vigente, "
                         "para las seis fuentes tecnicas a la vez); si elige "
                         "la vigente, ademas la incorporacion de cada "
                         "documento al registro y la reverificacion de sus "
                         "citas"),
        verificacion_pendiente=(
            "Declarar la opcion; si es la vigente, conseguir cada documento y "
            "abrir una sesion de registro por fuente, como las que "
            "incorporaron A796 y la traduccion de M 294. Para AASHTO LRFD, "
            "comparar ademas la 10a ed. con la 9a en las Secciones 3 y 5, que "
            "la propia AASHTO anuncia revisadas"),
        sin_consumidor=(
            "Ningun modulo lo invoca: no es una magnitud que entre en una "
            "formula sino la decision de marco normativo del expediente. Su "
            "consumidor natural seria la memoria, imprimiendo junto a cada "
            "fuente su vigencia y la eleccion; cablearlo es trabajo de M11, no "
            "de esta declaracion, y hasta entonces la vigencia se lee en el "
            "registro (`fuentes.estado_de_vigencia`) y en el manifiesto"),
        resolucion=Libre(
            que_lo_fija="el proyectista, al fijar el marco normativo tecnico "
                        "del expediente; para AASHTO LRFD, a propuesta suya "
                        "y con la conformidad de la entidad y/o propietario, "
                        "que es a quien el Manual de Puentes permite "
                        "considerar las actualizaciones",
            dominio="una de las dos opciones de la ventana, para las seis "
                    "fuentes tecnicas a la vez",
        ),
    ),

    "edicion_legal_que_rige_el_expediente": Criterio(
        valor=None,                 # VACIO: lo declara el proyectista
        # NIVEL NO MEDIBLE POR CORRIDA, por lo mismo que su hermano tecnico:
        # ningun modulo lo invoca y esta censado en SIN_CONSUMIDOR_Y_SIN_MEDIDA
        # (tests/test_nivel_medido.py). Es la decision de marco normativo
        # LEGAL del expediente, y de expediente por definicion: la edicion
        # de una norma derogada solo puede regir un expediente si un acto lo
        # ampara, y eso se declara al abrir el expediente, no al calcular el
        # perfil.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        # UN DICCIONARIO Y NO UN TEXTO, porque la exigencia se hace en la
        # puerta y no en la frase: la declaracion trae `opcion` (una de las
        # dos de `sensibilidad`), `fecha_inicio_expediente` y
        # `acto_regimen_transitorio`, y `_verificar_forma` rechaza la que no
        # los traiga con texto (campos_obligatorios). Medido en la auditoria
        # adversarial de EXT-6: con forma `str`, declarar la opcion «citada»
        # sin fecha ni acto pasaba la guardia, y el prompt pedia que la
        # exigiera. Para la opcion «vigente» los dos campos tambien tienen
        # sentido: la fecha del expediente y el acto que hace aplicable la
        # edicion 2018.
        forma=FORMA_DICT_CON_CAMPOS,
        campos_obligatorios=("opcion", "fecha_inicio_expediente",
                             "acto_regimen_transitorio"),
        # DOS OPCIONES, Y LA PRIMERA NO ES UNA PREFERENCIA: es una condicion.
        # Hasta EXT-6 el Manual de Puentes compartia ventana con cinco normas
        # tecnicas de EE.UU. («citada o vigente, para las siete a la vez»), y
        # eso trataba igual una RD derogada que una ASTM superada (EXT-N-01,
        # PC-26). Aqui la opcion «citada» dice lo que exige.
        sensibilidad=(
            "la edicion citada: Manual de Puentes 2016 (RD 041-2016-MTC/14, "
            "la que esta en normas/), admisible solo si el expediente se "
            "inicio antes de la vigencia de la RD 19-2018-MTC/14 "
            "(15-01-2019) y un acto verificado del regimen transitorio lo "
            "ampara; exige declarar la fecha de inicio del expediente y ese "
            "acto",
            "la edicion vigente: Manual de Puentes 2018 (RD 19-2018-MTC/14); "
            "exige conseguirla, incorporarla al registro como Fuente y "
            "reverificar contra ella cada cita del Manual de Puentes"),
        concepto="Edicion del Manual de Puentes que rige el expediente: la "
                 "citada en el registro, derogada por resolucion, o la "
                 "vigente",
        justificacion=(
            "El Manual de Puentes es la unica fuente del registro cuya "
            "edicion citada fue DEROGADA por un acto: el ejemplar de normas/ "
            "es la edicion 2016, aprobada por resolucion directoral del MTC, "
            "y la edicion 2018 del Manual actualizado la dejo sin efecto. Una "
            "norma tecnica extranjera con edicion posterior sigue siendo "
            "citable a eleccion del proyectista; una norma legal derogada "
            "solo rige un expediente si el regimen transitorio del acto que "
            "la derogo lo ampara para los expedientes iniciados bajo ella, y "
            "eso depende de dos hechos que este software no tiene: la fecha "
            "de inicio del expediente y el texto del acto, que hay que leer "
            "y no suponer. Por eso se separa del criterio tecnico y por eso "
            "la opcion citada no es una casilla: es una declaracion con dos "
            "datos. Se declara vacia. Lo que no cambia con la eleccion: "
            "ninguna cita y ningun valor de calculo; cada cita del Manual "
            "sigue anclada por sha1 a la edicion contra la que se verifico, "
            "y si se elige la vigente hay que conseguirla, incorporarla y "
            "reverificar contra ella cada cita del Manual de Puentes antes "
            "de que el expediente pueda citarla"),
        fuente=("Registro normativo: `fuentes.MP.vigencia` (acto aprobatorio "
                "RD 041-2016-MTC/14, impreso en las PDF 2 y 3 del ejemplar; "
                "derogado por RD 19-2018-MTC/14, El Peruano dispositivo "
                "1730970-1, vigente desde el 15-01-2019, verificado por "
                "busqueda web; la RD leida en su ejemplar, "
                "`fuentes.MP2018`, PDF 1 a 3, sin regimen transitorio) y "
                "`fuentes.fuentes_con_eleccion_de_edicion_pendiente_legal`, "
                "que deriva de ese campo la unica fuente de esta ficha; un "
                "test exige que la nombre a ella y solo a ella"),
        reemplazado_por=("Declaracion del proyectista con la fecha de inicio "
                         "del expediente y el acto del regimen transitorio "
                         "que ampara la edicion citada, o la incorporacion "
                         "del Manual de Puentes 2018 al registro y la "
                         "reverificacion de sus citas"),
        verificacion_pendiente=(
            "Declarar la fecha de inicio del expediente y la opcion. Lo que "
            "habia que leer ya se leyo (N1 del plan de normas 2): la RD "
            "19-2018-MTC/14 esta impresa en el ejemplar de la edicion 2018 "
            "(Fuente MP2018, PDF 1 a 3) y tiene cinco articulos SIN "
            "disposicion transitoria --- aprueba, publica, pone en vigencia "
            "al dia siguiente de su publicacion, deroga la RD "
            "041-2016-MTC/14 y remite al Ministerio de Justicia ---, de modo "
            "que la opcion citada exige un acto DISTINTO de esa RD que la "
            "ampare. La edicion 2018 ya esta en el registro con un par "
            "MP2018.* por cada cita del Manual de Puentes, verificado contra "
            "su pagina, y el contraste de los 29 numerales esta en las "
            "fichas N1MP-02 y N1MP-03 de docs/decisiones_diferidas.md: "
            "ninguna cifra que entre en el calculo cambio. La declaracion es "
            "un diccionario: {'opcion': <una de las dos>, "
            "'fecha_inicio_expediente': <fecha>, 'acto_regimen_transitorio': "
            "<acto leido>}"),
        sin_consumidor=(
            "Ningun modulo lo invoca: es la decision de marco normativo legal "
            "del expediente, no una magnitud. Su consumidor natural seria la "
            "memoria, imprimiendo junto a las citas del Manual de Puentes "
            "que edicion rige y por que acto; cablearlo es trabajo de M11, y "
            "hasta entonces la vigencia y los dos actos se leen en el "
            "registro (`fuentes.MP.vigencia`) y en el manifiesto"),
        resolucion=Libre(
            que_lo_fija="el proyectista, al fijar el marco normativo legal "
                        "del expediente, con la fecha de inicio y el acto "
                        "del regimen transitorio si elige la edicion citada",
            dominio="diccionario con `opcion` (una de las dos de la "
                    "ventana), `fecha_inicio_expediente` y "
                    "`acto_regimen_transitorio`",
        ),
    ),

    # =======================================================================
    # --- T-6 --- Geometria de 7.B (INF-3.3.3, INF-5.1.18)
    # =======================================================================

    "metodo_longitud_conducto": Criterio(
        # POR QUE ES UN CRITERIO Y NO UN CAMBIO DE FORMULA. El metodo por
        # extremo es el que la fuente describe (HDS-5 2.2.4 b., Figura 2.4),
        # pero mueve la L de todo punto y con ella el control de salida, la
        # caida y la cota de salida: es una decision con consecuencias, y la
        # formula anterior tiene que poder reproducirse para comparar. La
        # ventana es el conjunto cerrado de los dos metodos implementados.
        valor="por_extremo",
        nivel=NIVEL_PERFIL,         # lo invoca `M7.longitud_del_conducto`,
                                    # antes de la Fase 4, en toda corrida
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("terraplen_simetrico", "por_extremo"),
        concepto="Metodo con que se calcula la longitud del conducto de la "
                 "Sec. 7.B cuando no se declara: con la misma altura de "
                 "terraplen en los dos taludes, o con la de cada extremo",
        justificacion="Decide como se proyectan los taludes del terraplen "
                      "para obtener la longitud del conducto que usan el "
                      "control de salida (friccion y caida S*L), el TW por "
                      "cota y la cota de salida de 7.B. «por_extremo», el "
                      "valor del archivo, parte de la superposicion del "
                      "barril estimado sobre la seccion transversal del "
                      "cruce que el HDS-5 describe (num. 2.2.4 b. y Figura "
                      "2.4, pag. impresa 2.8, cita HDS5_3ED.2.2.4#LONGITUD) "
                      "-- un talud a cada lado y la salida mas baja que la "
                      "entrada -- y le añade una eleccion que es del "
                      "proyecto y no de la fuente: a cada lado el talud "
                      "baja desde el borde de la plataforma hasta el fondo "
                      "del conducto en ese extremo, como si el barril no "
                      "tuviera altura. La figura de la fuente dibuja los "
                      "taludes muriendo en la cara superior del barril, y "
                      "la Lamina N 01 del Manual del MTC en la coronacion "
                      "de los cabezales; medir al fondo da por eso la cota "
                      "superior de la longitud. La salida queda S*L mas "
                      "baja que la entrada, de modo que "
                      "L = [ancho + talud*(H_entrada + H_salida0)] / "
                      "[cos(esviaje) - talud*S], con H medida desde el "
                      "borde de la plataforma hasta el fondo de la entrada "
                      "(medido en la columna cota_fondo_entrada, o adoptado "
                      "por 'origen_cota_fondo_entrada'), corregido el borde "
                      "por bombeo o por peralte -- excluyentes en un mismo "
                      "punto -- cuando la seccion tipica los declara. El "
                      "proyecto mide al fondo y no a la clave porque la "
                      "seccion aun no se conoce cuando la longitud se "
                      "necesita: el HDS-5 dice que el diseño arranca con "
                      "una longitud aproximada (num. 3.1.4, pag. impresa "
                      "3.9, cita HDS5_3ED.3.1.4#LONGITUD) y manda encajar "
                      "despues la seccion elegida (num. 3.3.5, pag. impresa "
                      "3.25), que es lo que 7.B hace al imprimir la "
                      "longitud entre cabezales a la clave. La cota "
                      "superior no es el lado seguro por construccion: "
                      "alargar el conducto suma friccion y resta caida, y "
                      "con la pendiente de A-01 del corredor de referencia "
                      "el HW de salida baja -- 0.9925 m con la longitud al "
                      "fondo (18.869 m) contra 1.0002 m con la longitud a "
                      "la clave (14.676 m), 7.7 mm --, sin consecuencia en "
                      "ese punto porque gobierna el control de entrada "
                      "(1.042 m). Con el fondo de entrada adoptado igual al "
                      "terreno hay ademas un sesgo declarado: esa cota es "
                      "la del terreno en el eje, y el metodo ancla ahi la "
                      "entrada y carga toda la caida aguas abajo (para un "
                      "lecho de pendiente S que pasara por ella en el eje, "
                      "la longitud de A-01 seria 18.638 m y no 18.869); con "
                      "el fondo medido en el cauce es exacto. "
                      "«terraplen_simetrico» es la "
                      "formula que el proyecto usaba hasta T-6, "
                      "L = (ancho + 2*talud*H_eje)/cos(esviaje) con H_eje = "
                      "cota de rasante - cota de TERRENO, y es el caso "
                      "particular del anterior cuando el fondo de entrada "
                      "es el terreno, no hay bombeo y se desprecia la caida "
                      "en la proyeccion del talud de salida. Las dos "
                      "difieren en el factor cos/(cos - talud*S) -- 1.3 % "
                      "en A-01 del corredor de referencia, con talud 2.0 y "
                      "S = 0.006 -- y, cuando el fondo de entrada se mide "
                      "bajo el terreno, en talud*2*(terreno - fondo), que "
                      "es la parte que el metodo anterior no veia. El signo "
                      "sobre el HW de salida no es fijo: alargar el "
                      "conducto suma friccion y resta caida (ver la nota de "
                      "'talud_terraplen')",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), num. 2.2.4 'Roadway Data', "
               "inciso b. 'Culvert Length' y Figura 2.4, pag. impresa 2.8 "
               "(PDF 70); num. 3.1.4, pag. impresa 3.9 (PDF 91); num. "
               "3.3.5, pag. impresa 3.25 (PDF 107). La fuente describe el "
               "procedimiento grafico con el barril estimado; la expresion "
               "cerrada es su algebra, hecha por el proyecto, y medir al "
               "fondo es eleccion del proyecto. Que metodo aplica es "
               "adopcion: la "
               "hoja de ruta (Sec. 7.B) solo escribe 'ancho de plataforma "
               "+ proyeccion de taludes, afectada por esviaje'",
        reemplazado_por="La longitud MEDIDA sobre la seccion transversal "
                        "del cruce en los planos, declarada por punto como "
                        "dato externo `longitud_m`: un dato medido no se "
                        "sustituye por un metodo",
        resolucion=Libre(
            que_lo_fija="el proyectista: las dos formulas son geometria y "
                        "ninguna norma manda una",
            dominio="declaracion del metodo; el conjunto cerrado viaja en "
                    "`sensibilidad`",
        ),
    ),

    "desnivel_minimo_entrega_m": Criterio(
        # CERO NO ES «SIN CRITERIO»: es la entrega A NIVEL del fondo del
        # receptor, la ubicacion a) de la Lamina N 01 del Manual, y es lo que
        # G2 verificaba hasta T-6 sin decirlo en ninguna ficha. Con cualquier
        # valor de la ventana los puntos del corredor de referencia conservan
        # su veredicto de G2 (medido: el menor margen es 0.31 m).
        valor=0.0,
        nivel=NIVEL_PERFIL,         # lo invoca G2 en 7.B (`M7.g2_cota_salida`)
        etiqueta="A",
        forma=FORMA_FLOAT,
        sensibilidad=(0.0, 0.30),
        concepto="Desnivel minimo, en metros, que la cota de fondo de la "
                 "salida del conducto debe guardar SOBRE la cota de fondo "
                 "del cuerpo receptor (verificacion G2 de la Sec. 7.B)",
        justificacion="Decide cuanto por encima del fondo del receptor "
                      "tiene que quedar la salida para que G2 cumpla: "
                      "cota_salida >= cota_fondo_receptor + desnivel. La "
                      "fuente no da numero. El Manual del MTC exige que la "
                      "pendiente de la alcantarilla no altere "
                      "desmesuradamente la erosion y la sedimentacion (num. "
                      "4.1.1.3.3, pag. impresa 71, cita MC_HHD.4.1.1.3.3) "
                      "-- dos oraciones, sin cifra y sin mencion de la "
                      "entrega -- y su Lamina N 01 tipifica las ubicaciones "
                      "sin acotar ninguna: a) siguiendo la pendiente del "
                      "cauce, con la salida a nivel del fondo; c) y d) con "
                      "la salida SOBRE el cauce, y la advertencia de que "
                      "entonces el terreno a la salida debe ser roca u otro "
                      "material resistente a la erosion, o enrocado. De ahi "
                      "que el desnivel no sea conservador en un solo "
                      "sentido: una salida bajo el fondo del receptor queda "
                      "enterrada y se colmata (lo que G2 impide con "
                      "cualquier valor de la ventana), y una salida elevada "
                      "descarga en caida y socava, de modo que cada "
                      "centimetro de desnivel exigido es proteccion de "
                      "salida que hay que dimensionar. Se adopta 0.0, la "
                      "entrega a nivel: es la ubicacion a) de la lamina, la "
                      "que no introduce escalon, y la lectura minima del "
                      "amarre que la Sec. 7.B pide. El REMANSO del receptor "
                      "no se cubre con este desnivel sino con el TW de la "
                      "Sec. 1.3, que entra al control de salida. El extremo "
                      "alto de la ventana, 0.30 m, es la holgura que un "
                      "proyecto puede querer contra el sedimento que el "
                      "propio receptor deposita en su fondo entre "
                      "limpiezas; no sale de una fuente y por eso es "
                      "ventana de un [A] y no rango citado",
        fuente="NINGUNA fuente fija el valor. Manual de Hidrologia, "
               "Hidraulica y Drenaje (MTC), num. 4.1.1.3.3 'Pendiente "
               "longitudinal', pag. impresa 71 (PDF 74), y Lamina N 01 "
               "'Ubicacion tipica de alcantarillas respecto a la pendiente "
               "del cauce', pag. impresa 206 (PDF 209). El numeral exige "
               "cuidar la PENDIENTE y no habla de la entrega; la lamina "
               "tipifica donde puede quedar la salida y no acota ningun "
               "desnivel. Contrastar la cota de salida con el fondo del "
               "receptor es lectura del proyecto. La hoja de ruta (Sec. 7.B) "
               "pide las cotas 'amarradas al perfil del cauce y a la cota "
               "de fondo del receptor', sin desnivel",
        reemplazado_por="El desnivel de entrega que el levantamiento del "
                        "receptor y el estudio de su sedimentacion "
                        "justifiquen (seccion medida del dren, cota de "
                        "limpieza de la Junta de Usuarios), por punto",
        resolucion=Libre(
            que_lo_fija="el proyectista: ninguna norma ni fuente tecnica de "
                        "normas/ da un desnivel de entrega",
            dominio="m >= 0; 0 es la entrega a nivel del fondo del receptor",
        ),
    ),

    # --- T-3 --- (cadena T, INF-0.4) VC2: el empalme de la salida de un
    # paso de canal con el fondo del canal aguas abajo. Lo pidio la cadena T
    # sobre lo que §16.17 de docs/ruta_familia_c.md dejo «evaluado, medido,
    # no implementado», y con los dos avisos que aquel apartado puso: la
    # tolerancia no la da ninguna norma de normas/ como TOLERANCIA DE UN
    # EMPALME -- la mas cercana es la de aceptacion de la cota superior de
    # una placa de concreto, EG-2013 503.11 g) --, y en un paso de canal
    # `cota_fondo_receptor` es el MISMO canal aguas abajo (homonimia).
    # La verificacion AVISA y no detiene: el desajuste no depende de la
    # seccion -- subir de B x H no lo corrige --, sino de la cota de entrada
    # y de la pendiente, que son datos (G3 y V10 tienen la misma forma).
    "desajuste_empalme_canal_m": Criterio(
        valor=0.010,
        nivel=NIVEL_PERFIL,         # lo invoca VC2 en 7.B (`M7.vc2_empalme_canal`)
        etiqueta="A",
        forma=FORMA_FLOAT,
        sensibilidad=(0.010, 0.020),
        concepto="Desajuste maximo, en metros y en valor absoluto, entre la "
                 "cota de fondo de la salida de un paso de canal (Familia C) "
                 "y el fondo del canal aguas abajo (verificacion VC2)",
        justificacion="Decide cuanto puede quedar la salida del marco por "
                      "encima o por debajo del fondo del canal aguas abajo "
                      "antes de que VC2 lo avise: |cota_salida - "
                      "cota_fondo_receptor| <= desajuste. En un paso de "
                      "canal el conducto CONTINUA el canal: un escalon hacia "
                      "arriba descarga en caida sobre el lecho y uno hacia "
                      "abajo deja la salida enterrada y se colmata, de modo "
                      "que la banda es de dos lados (§16.17 de "
                      "docs/ruta_familia_c.md). La fuente no da la cifra "
                      "como tolerancia de un empalme. Se adopta 0.010 m "
                      "por analogia con la tolerancia de aceptacion de la "
                      "cota superior de una placa de concreto, -10 mm a +10 "
                      "mm (EG-2013, num. 503.11 g) 2., pag. impresa 934, "
                      "cita EG2013.503.11g#COTAS): la cota superior de la "
                      "losa de fondo ES el invert del marco, y un empalme "
                      "que el diseño deja fuera de la tolerancia con que "
                      "se recibe esa losa no se puede construir como "
                      "empalme. El extremo alto de la ventana, 0.020 m, es "
                      "la tolerancia de cota de la excavacion que recibe la "
                      "losa (EG-2013, num. 501.07, pag. impresa 889, cita "
                      "EG2013.501.07). VC2 avisa y no detiene: el desajuste "
                      "lo fijan la cota de entrada y la pendiente, que son "
                      "datos, y ninguna seccion lo corrige",
        fuente="NINGUNA fuente fija la tolerancia de un empalme con un "
               "canal. Las dos que se usan por analogia: EG-2013, num. "
               "503.11 g) 2. 'Otras tolerancias' ('Cotas superiores de "
               "placas y veredas: -10 mm a +10 mm.'), pag. impresa 934 (PDF "
               "942), y num. 501.07 'Tolerancias' de la excavacion para "
               "estructuras ('2 cm en cota'), pag. impresa 889 (PDF 897). "
               "El requisito que VC2 lee lo escribe la Sec. 2.3 de la hoja "
               "de ruta («No puede alterar la rasante hidraulica ni el "
               "borde libre del canal»), y la tipologia del cruce la "
               "dibuja la Lamina N 03 del Manual (marco en cruce de canal "
               "de riego), sin acotar nada",
        reemplazado_por="La tolerancia de empalme que fije el proyecto del "
                        "canal (ANA / Junta de Usuarios del Bajo Piura) o la "
                        "especificacion tecnica de la obra",
        resolucion=Libre(
            que_lo_fija="el proyectista, por analogia con la tolerancia de "
                        "aceptacion del EG-2013 para la cota superior de una "
                        "placa de concreto",
            dominio="m > 0, valor absoluto del desajuste admisible",
        ),
    ),

    # --- VE-3.14, OPCIONES 9, 10 y 13 de los ensayos de diseño del
    # cabezal --- tres elecciones del proyecto con su alternativa. El valor
    # de archivo es el comportamiento de hoy; la alternativa la sostiene la
    # fuente y la verifico el dueño (verificaciones_del_dueno/
    # cabezal_decisiones_9_14.md). NIVEL: el de la Fase 9 (expediente).
    "momento_talon_cabezal": Criterio(
        valor="exacto",             # decision 9 del dueño (VE-3.15)
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   peso_entero  AASHTO 11.6.1.2: el talon en voladizo con el peso
        #       ENTERO de lo que tiene encima (la regla por defecto).
        #   exacto       el «more exact method» de la misma frase: menos la
        #       reaccion lineal del terreno de 10.6.5 con las cargas
        #       factoradas de CADA combinacion (Resistencia I con gamma
        #       maximos y minimos, los dos casos del Evento Extremo I), sin
        #       traccion; si la resultante cae fuera de la base, peso entero.
        sensibilidad=("peso_entero", "exacto"),
        concepto="Con que carga se arma el talon de la zapata del cabezal: "
                 "el peso entero de lo que tiene encima o descontando la "
                 "reaccion del terreno",
        justificacion="Decide el momento y el cortante del talon, y con "
                      "ellos su acero y el peralte que el armado pide. AASHTO "
                      "LRFD 11.6.1.2 (cita AASHTO_LRFD_9.11.6.1.2#TALON) "
                      "manda el peso entero, salvo que se use un metodo mas "
                      "exacto, y 10.6.5 (cita AASHTO_LRFD_9.10.6.5#LINEAL) "
                      "fija la presion de contacto lineal con las cargas "
                      "factoradas. El valor de archivo es «exacto», "
                      "decision 9 del dueño, con la verificacion "
                      "independiente de VE-3: descuenta la "
                      "reaccion combinacion por combinacion -- Resistencia I "
                      "con los gamma maximos y minimos y los dos casos del "
                      "Evento Extremo I --, sin traccion, y deja el peso "
                      "entero impreso como contraste; si la resultante cae "
                      "fuera de la base, rige el peso entero. Los ensayos "
                      "midieron el peso entero 2.3 a 4.3 veces mayor en las "
                      "geometrias que cumplen (ficha VE3-18; la hoja de "
                      "ruta, §9.4, lo dice asi)",
        fuente="AASHTO LRFD 9a ed., 11.6.1.2, pag. impresa 11-20 (PDF 1489) "
               "y 10.6.5, pag. impresa 10-86 (PDF 1375)",
        reemplazado_por="Decision del proyectista, con el EMS",
        resolucion=Libre(
            que_lo_fija="el proyectista",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "carga_pantalla_cabezal": Criterio(
        valor="cuna_sobre_la_pantalla",   # decision 10 del dueño (VE-3.15)
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   plano_virtual_del_talon  la pantalla con el diagrama del plano
        #       virtual del extremo del talon integrado sobre el arranque
        #       (T7C-12): cota superior, carga presion por encima de la
        #       corona del muro.
        #   cuna_sobre_la_pantalla   la cuña de tanteo sobre la cara del
        #       trasdos de la pantalla, hasta la superficie REAL (el talud
        #       sobre la corona y la sobrecarga), y bajo sismo la cuña con
        #       k_h mas la inercia de la pantalla (Caltrans BDP 11.2,
        #       11.2.2.4.1).
        sensibilidad=("plano_virtual_del_talon", "cuna_sobre_la_pantalla"),
        concepto="Con que empuje se arma la pantalla del cabezal: el del "
                 "plano virtual del talon o el de una cuña sobre su propia "
                 "cara",
        justificacion="Decide el momento y el cortante de la pantalla, y con "
                      "ellos su espesor (dimensionada por su armado, en la "
                      "revision de los ensayos del cabezal). AASHTO no fija el plano de carga del diseño "
                      "estructural de la pantalla; el ejemplo resuelto de "
                      "Caltrans (Bridge Design Practice 11.2, 11.2.2.4.1, "
                      "pags. 11.2-27 y 11.2-28, fuente sin registrar en el "
                      "repositorio) carga la pantalla con una cuña de tanteo "
                      "sobre su cara y separa ese "
                      "diagrama del de la estabilidad externa; bajo sismo, "
                      "la cuña sismica y la inercia de la pantalla, no la "
                      "del relleno sobre el talon (pag. 11.2-33). El valor "
                      "de archivo es la cuña sobre la pantalla, decision del "
                      "dueño (decision 10), con sus dos "
                      "condiciones: la cuña llega a la superficie real "
                      "(talud sobre la corona y sobrecarga) y bajo sismo se "
                      "suma la inercia de la pantalla. El plano virtual del "
                      "talon queda en la ventana como la cota superior de "
                      "T7C-12",
        fuente="Caltrans Bridge Design Practice, cap. 11.2 (oct. 2022), "
               "11.2.2.4.1, pags. 11.2-27, 11.2-28 y 11.2-33 (ejemplo "
               "resuelto del repositorio de normas, ejemplos_resueltos/"
               "cabezal_muros); AASHTO LRFD 9a ed., 3.11.5.3 y C11.6.5.3 "
               "(cuña de tanteo)",
        reemplazado_por="Decision del proyectista",
        resolucion=Libre(
            que_lo_fija="el proyectista",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "distribucion_incremento_sismico": Criterio(
        valor="segun_regimen",      # decision 13 del dueño (VE-3.15)
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   segun_regimen          el del regimen: con el muro que cede
        #       ('factor_muro_eleccion' con la reduccion), el mayor del
        #       centroide estatico y h/3 (11.6.5.3); con el que no cede, el
        #       incremento sube lo necesario para que la resultante del
        #       estatico mas el sismico no quede bajo h/2 (C11.6.5.4), y si
        #       la fraccion de 'punto_aplicacion_incremento_sismico' ya la
        #       deja mas alta, se conserva.
        #   fraccion_de_h          el incremento a esa fraccion fija de h
        #       (0.6 de archivo), en los dos regimenes.
        #   distribucion_estatica  la regla del muro que cede, solo con el;
        #       con el que no cede se rechaza.
        sensibilidad=("segun_regimen", "fraccion_de_h",
                      "distribucion_estatica"),
        concepto="Donde se aplica el incremento sismico del empuje: segun "
                 "el regimen del muro, a una fraccion fija de h o con la "
                 "distribucion del empuje estatico",
        justificacion="Decide el brazo del incremento sismico y con el la "
                      "excentricidad, el volteo y la portante sismicos. "
                      "AASHTO 11.6.5.3 (cita "
                      "AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION) distribuye el "
                      "empuje total del muro que cede como el estatico, no "
                      "por debajo de H/3 («should»: un piso recomendado); el "
                      "Manual de Puentes 2.8.1.1.14.3 lo traduce y su "
                      "Apendice A.11.3.1 lo da por suficiente para muros de "
                      "rutina. Para el muro que no cede, C11.6.5.4 (cita "
                      "AASHTO_LRFD_9.C11.6.5.4#H_MEDIOS) pide considerar la "
                      "resultante del estatico mas el sismico en h/2, y el "
                      "proyecto lo lee como piso. El valor de archivo deriva "
                      "el brazo del regimen, decision 13 del dueño con la "
                      "verificacion independiente de VE-3; la fraccion fija "
                      "de antes (0.6 sobre el incremento) queda en la "
                      "ventana, y con ella la resultante del muro que no "
                      "cede quedaba entre 0.41·h y 0.52·h segun k_h",
        fuente="AASHTO LRFD 9a ed., 11.6.5.3 y C11.6.5.3, pag. impresa "
               "11-30 (PDF 1499); C11.6.5.4, pag. impresa 11-32 (PDF 1501); "
               "Manual de Puentes 2.8.1.1.14.3 y A.11.3.1",
        reemplazado_por="Decision del proyectista",
        resolucion=Libre(
            que_lo_fija="el proyectista",
            dominio="una de las tres opciones de la ventana",
        ),
    ),

    # --- VE-5 (lote M9, ficha T7B-14) --- El empuje sismico TOTAL del
    # muro que no cede: la fuente da el k_h (11.6.5.4) y la altura de la
    # resultante (C11.6.5.4), y no dice como se junta el reposo estatico con
    # el empuje pseudoestatico de 11.6.5.3. NIVEL: el de la Fase 9
    # (expediente), su unico consumidor (`M9.cargas_del_cabezal`, condicion
    # sismica con 'regimen_cabezal' = 'no_cedente'). Sin medida en las
    # corridas de referencia: solo se lee con el muro que no cede declarado.
    "empuje_sismico_muro_que_no_cede": Criterio(
        valor="reposo_mas_incremento",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   reposo_mas_incremento    el empuje en reposo de la estatica MAS
        #       el incremento pseudoestatico P_AE - P_A (Mononobe-Okabe o la
        #       cuña de tanteo con k_h = 1.0·k_h0), todo horizontal cuando
        #       rige el reposo (sin friccion muro-relleno). Lado seguro: el
        #       total supera al de Mononobe-Okabe, como dice C11.6.5.4.
        #   mayor_de_reposo_y_total  la lectura literal de 11.6.5.4 (el
        #       empuje pseudoestatico con 1.0·k_h0), sin bajar del reposo:
        #       el incremento es lo que el total horizontal supera al
        #       estatico, y puede ser cero.
        sensibilidad=("reposo_mas_incremento", "mayor_de_reposo_y_total"),
        concepto="Como se forma el empuje sismico total de un cabezal que "
                 "no cede: reposo mas el incremento pseudoestatico, o el "
                 "mayor del reposo y del total pseudoestatico",
        justificacion="Decide el empuje sismico de la estabilidad del "
                      "cabezal declarado no cedente ('regimen_cabezal'). "
                      "AASHTO 11.6.5.4 (cita AASHTO_LRFD_9.11.6.5.4#"
                      "NO_CEDENTE) manda calcular el empuje sismico con "
                      "k_h = 1.0·k_h0 y su comentario (citas "
                      "AASHTO_LRFD_9.C11.6.5.4#K0 y AASHTO_LRFD_9.C11.6.5.4#"
                      "H_MEDIOS) liga ese caso con el empuje en reposo en el "
                      "estado limite de resistencia, dice que las presiones "
                      "de un muro rigido superan a las de Mononobe-Okabe "
                      "(la solucion de Wood que el comentario cita) y pide considerar la resultante en h/2. "
                      "Ninguna dice como se suma el reposo estatico al "
                      "empuje pseudoestatico, que es de muro que cede: con "
                      "phi = 30 y k_h0 = 0.25 el total de Mononobe-Okabe "
                      "(24.7 kN/m horizontales en el muro de tanteo) queda "
                      "BAJO el reposo (25.9), y la lectura literal deja el "
                      "sismo sin incremento. El proyecto adopta el reposo "
                      "mas el incremento, que respeta las dos frases del "
                      "comentario (mas que Mononobe-Okabe y no menos que el "
                      "reposo) y es el lado seguro; la lectura literal queda "
                      "en la ventana",
        fuente="AASHTO LRFD 9a ed., 11.6.5.4 y C11.6.5.4, pag. impresa "
               "11-32 (PDF 1501); 3.11.5.2, pag. impresa 3-120 (PDF 174)",
        reemplazado_por="Analisis numerico de la interaccion del cabezal con "
                        "el relleno, aprobado por el Propietario (11.6.5.4), "
                        "o la solucion de muro rigido de Wood (1973), que no "
                        "esta en el repositorio de normas",
        resolucion=Libre(
            que_lo_fija="el proyectista: ninguna fuente lo fija",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "agua_del_relleno_bajo_sismo": Criterio(
        # --- VE-3.14 (H-3 de los ensayos de diseño del cabezal) --- Hasta
        # VE-3.14, con agua en el plano de empuje la condicion sismica del
        # cabezal se detenia sin cifra y el ancho se dimensionaba SIN ella.
        # NIVEL: el de la Fase 9 (expediente), su unico consumidor
        # (`M9.cargas_del_cabezal`, condicion sismica con agua).
        valor="se_mueve_con_el_suelo",
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_CATEGORIA,
        #   se_mueve_con_el_suelo  relleno que no drena libremente (el
        #       compactado del trasdos): el incremento sismico con el peso
        #       TOTAL del suelo bajo el agua (C11.6.5.3, primer tratamiento).
        #   relleno_muy_abierto    pedraplen: peso sumergido mas la presion
        #       hidrodinamica (Westergaard), que ninguna fuente del
        #       repositorio da: la condicion sismica se detiene sin cifra.
        sensibilidad=("se_mueve_con_el_suelo", "relleno_muy_abierto"),
        concepto="Como se trata el agua del relleno del trasdos bajo sismo: "
                 "si se mueve con el suelo o, en un relleno muy abierto, no",
        justificacion="Decide el empuje sismico del cabezal cuando hay agua "
                      "en el plano de empuje. AASHTO 11.6.5.3 excluye del "
                      "metodo el relleno saturado Y suelto (que puede "
                      "licuar), y su comentario C11.6.5.3 (citas "
                      "AASHTO_LRFD_9.C11.6.5.3#AGUA_TOTAL y "
                      "#AGUA_ABIERTO) da los dos tratamientos: con el suelo "
                      "que no drena libremente, el peso TOTAL, porque suelo "
                      "y agua se mueven juntos; con un relleno muy abierto "
                      "(pedraplen), el peso sumergido mas la presion "
                      "hidrodinamica. El valor de archivo es el primero, que "
                      "es el del relleno compactado del trasdos que el "
                      "proyecto especifica; el segundo detiene la condicion "
                      "sismica con «metodo no evaluable», porque la formula "
                      "de Westergaard no esta en ninguna fuente del "
                      "repositorio de normas y no se inventa",
        fuente="AASHTO LRFD 9a ed., 11.6.5.3 y C11.6.5.3, pags. impresas "
               "11-29 a 11-32 (PDF 1498 a 1501; citas "
               "AASHTO_LRFD_9.11.6.5.3#VALIDEZ, "
               "AASHTO_LRFD_9.C11.6.5.3#AGUA_TOTAL y "
               "AASHTO_LRFD_9.C11.6.5.3#AGUA_ABIERTO)",
        reemplazado_por="Especificacion del material del relleno del trasdos "
                        "(granulometria y permeabilidad) en los planos y en "
                        "las especificaciones tecnicas",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el material del relleno que "
                        "especifica",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "nivel_agua_relleno_sin_drenaje_bajo_sismo": Criterio(
        # --- VE-4e (ficha VE3-21) --- Hasta VE-4e, con 'drenaje_trasdos' =
        # «sin_drenaje» el sismo del cabezal iba con el relleno lleno hasta
        # su superficie, el agua de la estatica. AASHTO C11.6.5.3 recomienda
        # para el sismo el nivel MEDIO del agua en el tiempo y no dice cual
        # es en un relleno que no drena: es un vacio de la fuente, y la regla
        # de CLAUDE.md para un vacio es esta ficha SIN valor de archivo (se
        # declara o la condicion sismica se detiene). Las dos opciones son
        # niveles que el ensamble ya calcula; ninguna es un numero nuevo.
        # NIVEL: el de la Fase 9 (expediente), su unico consumidor
        # (`M9.cargas_del_cabezal`, condicion sismica con «sin_drenaje»). Con
        # «drenado» de archivo no lo lee ninguna corrida
        # (`tests/test_ve4e_agua_por_condicion.py`).
        valor=None,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   superficie_del_relleno  el relleno sin drenar queda lleno en el
        #       tiempo: su nivel medio es su superficie contra el trasdos, el
        #       agua de la estatica (y el incremento sismico con el peso
        #       total bajo el agua, 'agua_del_relleno_bajo_sismo').
        #   freatico_natural        el relleno se llena solo por episodios
        #       (lluvia, avenida) y en el tiempo vuelve al freatico natural
        #       del punto (columna NF_profundidad_m): el agua del relleno
        #       drenado.
        sensibilidad=("superficie_del_relleno", "freatico_natural"),
        concepto="Hasta que nivel se cuenta el agua del relleno del trasdos "
                 "en la condicion sismica cuando el trasdos no tiene drenaje",
        justificacion="Decide el agua del relleno en la condicion sismica "
                      "del cabezal cuando el trasdos se declara sin drenaje, "
                      "y con ella el empuje del agua, la subpresion, el peso "
                      "del relleno sobre el talon y el incremento sismico. "
                      "En la condicion estatica el agua llena el relleno "
                      "retenido hasta su superficie (cita "
                      "AASHTO_LRFD_9.11.6.6#DRENAJE, con la lectura del "
                      "proyecto en su interpretacion); para el sismo el "
                      "comentario de la fuente recomienda el nivel medio del "
                      "agua en el tiempo (cita "
                      "AASHTO_LRFD_9.C11.6.5.3#NIVEL_MEDIO) y no dice cual "
                      "es en un relleno que no drena. Las dos lecturas "
                      "posibles son las de la ventana: la superficie del "
                      "relleno, si el relleno queda lleno en el tiempo (es "
                      "la cota superior y repite el agua de la estatica), o "
                      "el freatico natural del punto, si se llena solo por "
                      "episodios y el agua sale por el terreno de fundacion "
                      "(es el agua del relleno drenado). La eleccion la "
                      "sostiene el estudio de suelos: la permeabilidad del "
                      "relleno y de la fundacion, y la permanencia del agua "
                      "en el trasdos. No tiene valor de archivo porque la "
                      "fuente no lo fija; sin declararlo la condicion "
                      "sismica de un trasdos sin drenaje se detiene. Con el "
                      "trasdos drenado no se lee",
        fuente="AASHTO LRFD 9a ed., C11.6.5.3, pag. impresa 11-31 (PDF 1500; "
               "cita AASHTO_LRFD_9.C11.6.5.3#NIVEL_MEDIO), y 11.6.6 "
               "'Drainage', pag. impresa 11-35 (PDF 1504; cita "
               "AASHTO_LRFD_9.11.6.6#DRENAJE)",
        reemplazado_por="Nivel medio del agua en el relleno del trasdos del "
                        "estudio de suelos (permeabilidad del relleno y de la "
                        "fundacion, lecturas del freatico)",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el estudio de suelos: si el "
                        "relleno sin drenar queda lleno en el tiempo o se "
                        "vacia por el terreno de fundacion",
            dominio="una de las dos opciones de la ventana",
        ),
    ),
}
