"""
Fichas de criterios adoptados del dominio: proteccion.
"""

from typing import Dict
from src.modelos import Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_DICT_CON_CAMPOS,
    FORMA_FLOAT,
    NIVEL_PERFIL,
)


CRITERIOS: Dict[str, Criterio] = {


    # ----------------------- PROTECCION Y DETALLE -------------------------

    "espesor_proteccion_salida": Criterio(
        valor=1.75,                 # multiplicador de d50
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Espesor de la capa de proteccion, como multiplo de d50",
        # --- T-8 --- La justificacion y la fuente dicen desde T-8 contra que
        # se contrasta el valor, sin cambiarlo (los mismos numeros en el
        # fixture): HEC-14 ya esta en el repositorio de normas.
        justificacion="El Manual solo entrega d50 (Laushey). El espesor, la "
                      "longitud y la granulometria completa no estan normados. "
                      "Se adopta el rango corriente 1.5-2.0 d50. Desde T-8 "
                      "se contrasta con HEC-14, y el contraste no lo "
                      "respalda: la Tabla 10.1 de HEC-14 (un ejemplo de "
                      "estandar de proyecto) pide al apron entre 3.5 y 2.0 "
                      "veces el D50 de su clase, y su Sec. 10.1 pide a la "
                      "poza de enrocado al menos 2 D50: el valor adoptado "
                      "queda SIEMPRE bajo ese piso, y toda la ventana salvo "
                      "su techo, que lo iguala. El valor no se cambia --es "
                      "una adopcion sobre otra practica, y moverlo cambiaria "
                      "lo que el proyecto ya declaro--, pero la Fase 6 "
                      "imprime el apron de HEC-14 al lado, AVISA en todo "
                      "punto que dimensiona que el multiplo queda bajo 2.0 "
                      "(cita HEC14.10.2#PROFUNDIDAD). Por decision del "
                      "dueño del proyecto la regla "
                      "'regla_espesor_longitud_proteccion_salida' vale "
                      "«envolvente_hec14»: donde HEC-14 es evaluable rige el "
                      "mayor de este espesor y el de la Tabla 10.1, y este "
                      "multiplo solo rige con la regla «manual» o donde "
                      "HEC-14 no se puede evaluar",
        fuente="Practica corriente de diseno de enrocado. Contraste: HEC-14 "
               "3a ed. (FHWA-NHI-06-086), Sec. 10.2, Table 10.1, pag. "
               "impresa 10-18 (PDF 219), cita HEC14.10.2#T10_1, y Sec. 10.1, "
               "pag. impresa 10-1 (PDF 202)",
        sensibilidad=(1.5, 2.0),
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre la practica corriente de "
                        "diseño de enrocado, como multiplo de d50",
            dominio="multiplo adimensional de d50 > 0",
        ),
    ),

    "longitud_proteccion_salida": Criterio(
        # m. NO SALE DE NINGUNA NORMA PERUANA y hay que decirlo asi: el
        # Manual MTC (num. 4.1.1.3.7 c) entrega d50 y nada mas, y el HDS-5
        # 3.a ed. remite el dimensionamiento del apron a HEC-14 Sec. 10.2.
        # HEC-14 ESTA en el repositorio de normas desde T-0 (este comentario
        # decia lo contrario hasta T-8): su Tabla 10.1 da la longitud del
        # apron, de 4 a 8 veces la altura del conducto segun la clase de
        # piedra, y la Fase 6 contrasta con ella este valor y avisa cuando es
        # menor (y con la regla 'regla_espesor_longitud_proteccion_salida' en
        # «envolvente_hec14» toma la mayor). Es una adopcion del proyectista
        # sobre practica corriente de enrocado a la salida, con su ventana
        # declarada, y NO gobierna ninguna verificacion: la longitud de la
        # proteccion no entra en V1-V9 ni en 7.A/7.B.
        valor=5.0,
        nivel=NIVEL_PERFIL,
        sensibilidad=(3.0, 8.0),     # m; banda de practica de aprons de enrocado en conductos de 0.9-1.2 m
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Longitud de la proteccion aguas abajo de la salida",
        justificacion="Laushey (num. 4.1.1.3.7 c) entrega d50 y nada mas. La "
                      "hoja de ruta declara expresamente que el espesor, la "
                      "LONGITUD aguas abajo, la granulometria completa y el "
                      "filtro quedan fuera de la norma. Sin filtro el enrocado "
                      "se socava por debajo y falla: la longitud sola no basta, "
                      "pero sin ella no hay pieza que dimensionar. Desde T-8 "
                      "la Fase 6 la contrasta con la longitud del apron de "
                      "HEC-14 (Tabla 10.1: de 4 a 8 veces la altura del "
                      "conducto segun la clase de piedra) y, si el lecho esta "
                      "declarado, con la longitud de la hoya de socavacion de "
                      "su Cap. 5, y avisa cuando la adoptada es menor. "
                      "Por decision del dueño del proyecto la regla "
                      "'regla_espesor_longitud_proteccion_salida' vale "
                      "«envolvente_hec14»: donde HEC-14 es evaluable rige la "
                      "mayor de esta longitud y la de la Tabla 10.1",
        fuente="PENDIENTE - Sec. 6 de la hoja de ruta la marca [A] sin valor. "
               "Practica corriente de diseno de enrocado o HEC-14. "
               "Contraste desde T-8: HEC-14 3a ed., Sec. 10.2, Table 10.1, "
               "pag. impresa 10-18 (PDF 219), cita HEC14.10.2#T10_1",
        reemplazado_por="Diseno de disipador o transicion del expediente",
        verificacion_pendiente="Con pendientes bajas los d50 son de 3-13 cm y lo "
                               "probable es que gobierne el emboquillado de piedra "
                               "por razones constructivas, no el enrocado",
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre practica corriente de "
                        "enrocado o HEC-14; Sec. 6 la marca [A] sin valor",
            dominio="m > 0",
        ),
    ),

    # =======================================================================
    # --- T-8 --- (cadena T) · tres criterios de la Fase 6
    # =======================================================================
    # La proteccion de la ENTRADA (INF-5.1.13) y las dos lecturas que la hoya
    # de socavacion de HEC-14 Cap. 5 deja abiertas. Los consume M6.
    "tipo_proteccion_entrada": Criterio(
        valor="emboquillado_de_piedra",
        nivel=NIVEL_PERFIL,         # lo invoca la Fase 6 en toda corrida que dimensiona
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO son las tres clases que el Manual enumera, con
        # sus palabras: no se añade ninguna.
        sensibilidad=("emboquillado_de_piedra", "enchapado_de_roca_acomodada",
                      "otro_revestimiento"),
        concepto="Revestimiento con que se protege el cauce y el talud en la "
                 "ENTRADA de la alcantarilla",
        justificacion="Decide que revestimiento declara la memoria para la "
                      "entrada. El Manual (num. 4.1.1.3.7 c)) recomienda "
                      "proteger el cauce cuando la velocidad en la entrada, y "
                      "particularmente en la salida, es alta, y enumera tres "
                      "clases de revestimiento sin preferir ninguna ni dar "
                      "dimensiones: emboquillados de piedra, enchapado de "
                      "rocas acomodadas u otros tipos (citas "
                      "MC_HHD.4.1.1.3.7c#PROTECCION y "
                      "MC_HHD.4.1.1.3.7c#REVESTIMIENTOS). Las Láminas 02, "
                      "02-A y 03 de sus Anexos dibujan la entrada de las "
                      "alcantarillas tipicas con «revestimiento de piedra "
                      "emboquillada» y su uña (cita MC_HHD.LAMINA_02), y ese "
                      "es el motivo del valor adoptado: es el unico "
                      "revestimiento de entrada que el Manual dibuja. Las "
                      "laminas llevan las dimensiones como letras o como "
                      "«variable», de modo que el criterio declara la CLASE "
                      "de revestimiento y no una medida: la longitud y el "
                      "espesor del zampeado y el dentellon son geometria del "
                      "cabezal. No entra en ninguna formula ni mueve ningun "
                      "resultado; cambia lo que la memoria declara para la "
                      "entrada. Sensibilidad: las tres clases del numeral",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.1.3.7 c) 'Socavación local a la salida de la "
               "alcantarilla', pags. impresas 79-80 (PDF 82-83), citas "
               "MC_HHD.4.1.1.3.7c#PROTECCION y "
               "MC_HHD.4.1.1.3.7c#REVESTIMIENTOS (recomendacion); Anexos, "
               "Lámina Nº 02, pag. impresa 207 (PDF 210), cita "
               "MC_HHD.LAMINA_02 (figura, sin dimensiones). HDS-5 3a ed., "
               "num. 5.3.1 'Scour at Inlets', pag. impresa 5.9 (PDF 145), "
               "cita HDS5_3ED.5.3.1#ENTRADA: enumera las medidas, sin "
               "dimensionarlas. La eleccion entre las tres clases es "
               "adopcion del proyectista",
        reemplazado_por="El detalle de la entrada que fijen los planos del "
                        "cabezal (zampeado, dentellon y revestimiento del "
                        "talud), con sus dimensiones",
        resolucion=Libre(
            que_lo_fija="el proyectista, entre las tres clases de "
                        "revestimiento que el num. 4.1.1.3.7 c) enumera",
            dominio="declaracion de la clase de revestimiento; el conjunto "
                    "cerrado de valores admisibles viaja en `sensibilidad`",
        ),
    ),

    "duracion_caudal_pico_socavacion_min": Criterio(
        # NIVEL NO MEDIDO POR CORRIDA, y se dice: solo se invoca cuando el
        # punto declara `material_lecho_salida` SIN declarar
        # `duracion_caudal_pico_min`, y ninguna de las tres corridas de
        # `tests/test_nivel_medido.py` trae ese dato. Lo sostiene el censo:
        # su unico consumidor es M6, que el alcance de perfil ejecuta; y lo
        # mide `tests/test_t8_proteccion.py` con una corrida de perfil que si
        # declara el lecho.
        #
        # ERA [C] CON VALOR 30 HASTA LA DECISION DEL DUEÑO DEL 2026-11-12
        # (segunda auditoria de T-8, D3). Pasa a [A] porque dejo de ser «el
        # valor de la fuente»: la fuente recomienda 30 minutos y el proyecto
        # ELIGE otro dentro de una ventana, con su sensibilidad. La etiqueta
        # dice cuanto se eligio, y aqui se eligio.
        valor=360.0,                # minutos
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Duracion del caudal pico, en minutos, con que se estima "
                 "la hoya de socavacion a la salida cuando el estudio "
                 "hidrologico no la entrega",
        justificacion="Decide el tiempo t de las ecuaciones de socavacion "
                      "de HEC-14 cuando el punto no declara la duracion del "
                      "caudal pico. La fuente recomienda para ese caso 30 "
                      "minutos (num. 5.1.2, cita HEC14.5.1.2#T30; lo repite "
                      "para suelos cohesivos en la pag. impresa 5-7), y en "
                      "la frase siguiente dice que en los primeros 30 "
                      "minutos se alcanzan entre 2/3 y 3/4 de la profundidad "
                      "maxima (cita HEC14.5.1.2#DOS_TERCIOS). La profundidad "
                      "de la hoya es la que se entrega al DESPLANTE del "
                      "cabezal de salida, y un cabezal cimentado a dos "
                      "tercios de la hoya maxima queda descalzado: por eso "
                      "el proyecto no adopta los 30 minutos sino el techo "
                      "de la ventana, 360. La hoya crece con el tiempo: con "
                      "el exponente de la Tabla 5.1 para la profundidad en "
                      "suelo no cohesivo, θ = 0.06, de 30 a 360 minutos sube "
                      "un 16 % (12^0.06 = 1.161); en suelo cohesivo, θ = "
                      "0.10, un 28 %. El dato externo "
                      "`duracion_caudal_pico_min` gana cuando viene. "
                      "Sensibilidad: de 30 minutos, el valor que la fuente "
                      "recomienda y por debajo del cual dice que sus "
                      "exponentes no aplican (cita HEC14.5.1.2#NO_BAJO_30), "
                      "a 360 minutos. Lo que la fuente no dice: el techo de "
                      "360 minutos no sale de HEC-14, que no da duracion "
                      "maxima; es adopcion del proyecto para acotar la "
                      "ventana, del orden del tiempo de referencia de la "
                      "propia ecuacion (t/316)",
        fuente="HEC-14 3a ed. (FHWA-NHI-06-086, julio de 2006), num. 5.1.2 "
               "'Time of Scour', pag. impresa 5-2 (PDF 55), citas "
               "HEC14.5.1.2#T30 (recomendacion: 30 minutos a falta de la "
               "duracion), HEC14.5.1.2#DOS_TERCIOS (a los 30 minutos, de 2/3 "
               "a 3/4 de la profundidad maxima) y HEC14.5.1.2#NO_BAJO_30 "
               "(los exponentes no aplican a los primeros 30 minutos). El "
               "valor adoptado y el techo de la ventana, 360 minutos, no "
               "salen de la fuente: son eleccion del proyecto, por decision "
               "de su dueño",
        reemplazado_por="La duracion del caudal pico del hidrograma de "
                        "diseño de cada cuenca, del estudio hidrologico "
                        "(dato externo `duracion_caudal_pico_min`)",
        sensibilidad=(30.0, 360.0),
        resolucion=Libre(
            que_lo_fija="el proyectista, dentro de la ventana: HEC-14 num. "
                        "5.1.2 recomienda 30 minutos cuando no se conoce la "
                        "duracion del caudal pico y dice que cubren de 2/3 a "
                        "3/4 de la hoya maxima",
            dominio="minutos, de 30 (limite de validez de los exponentes y "
                    "valor que la fuente recomienda) a 360",
        ),
    ),

    "lectura_coeficientes_socavacion_hec14": Criterio(
        # NIVEL NO MEDIDO POR CORRIDA: como el anterior, solo se invoca con
        # el lecho declarado. Mismo sosten y misma medida.
        valor="envolvente_de_filas_vecinas",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("envolvente_de_filas_vecinas", "interpolacion_lineal"),
        concepto="Como se leen la Tabla 5.2 (altura de la salida sobre el "
                 "lecho) y la Tabla 5.3 (pendiente) de HEC-14 cuando el dato "
                 "cae ENTRE dos filas",
        justificacion="Decide el valor de los coeficientes Ch y Cs de la "
                      "hoya de socavacion cuando la altura de caida o la "
                      "pendiente del conducto no coinciden con una fila "
                      "tabulada. Las dos tablas dan cuatro filas cada una "
                      "(alturas de 0, 1, 2 y 4 diametros; pendientes de 0, "
                      "2, 5 y mas de 7 %) y la fuente no dice como leer "
                      "entre ellas: sus ejemplos caen justo en una fila "
                      "(citas HEC14.5.1.4#T5_2 y HEC14.5.1.5#T5_3). "
                      "«envolvente_de_filas_vecinas», el valor adoptado, "
                      "toma para cada dimension de la hoya el MAYOR de los "
                      "dos coeficientes vecinos: es la lectura que nunca "
                      "queda por debajo de la tabla, tambien en la longitud, "
                      "cuyo coeficiente BAJA con la altura de caida, de Ch = "
                      "1.00 a Ch = 0.73. "
                      "«interpolacion_lineal» interpola entre las dos filas, "
                      "y entre el 5 % y el 7 % hacia la fila «>7». En la "
                      "profundidad, que es la que fija el desplante del "
                      "cabezal, la diferencia entre las dos lecturas es como "
                      "mucho del 22 % (entre las filas de altura 0 y 1 "
                      "diametro) y del 3 % en la pendiente por debajo del 2 "
                      "%. Fuera de la tabla (mas de 4 diametros de caida) "
                      "ninguna de las dos lecturas extrapola: el calculo se "
                      "declara no evaluable",
        fuente="HEC-14 3a ed. (FHWA-NHI-06-086), num. 5.1.4 'Drop Height', "
               "Table 5.2, y num. 5.1.5 'Slope', Table 5.3, pag. impresa 5-3 "
               "(PDF 56), citas HEC14.5.1.4#T5_2 y HEC14.5.1.5#T5_3. La "
               "fuente tabula y no dice como leer entre filas: la lectura "
               "es adopcion del proyectista",
        reemplazado_por="Una estimacion de socavacion del estudio del cauce "
                        "(dato externo `profundidad_socavacion_estimada_m`), "
                        "que gana sobre la de este programa",
        resolucion=Libre(
            que_lo_fija="el proyectista: las Tablas 5.2 y 5.3 de HEC-14 no "
                        "dicen como leer entre filas",
            dominio="declaracion de la lectura; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    # --- T-8, auditoria adversarial --- dos decisiones del dueño: con que
    # regla se fijan la piedra, el espesor y la longitud de la proteccion de
    # salida, y desde que cota se mide la profundidad de socavacion. La
    # primera la TOMO el 2026-11-12, tras la segunda auditoria: rige la
    # envolvente, y alcanza al tamaño de la piedra.
    "regla_espesor_longitud_proteccion_salida": Criterio(
        # NIVEL MEDIDO POR CORRIDA: lo invoca la Fase 6 en todo punto que
        # dimensiona (corrida ancha de perfil, A-01 y A-02).
        #
        # EL NOMBRE DE LA CLAVE DICE «espesor_longitud» Y LA REGLA GOBIERNA
        # TAMBIEN LA PIEDRA desde el 2026-11-12. No se renombra: la clave ya
        # esta en sesiones guardadas, en barridos y en la linea base, y un
        # alias seria una segunda puerta para la misma decision. El concepto
        # y la justificacion dicen lo que cubre.
        valor="envolvente_hec14",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("manual", "envolvente_hec14"),
        concepto="Regla con que se fijan el tamaño de la piedra, el espesor "
                 "y la longitud de la proteccion de salida",
        justificacion="Decide que rige en la proteccion de salida: lo que da "
                      "el Manual con lo adoptado, o la envolvente de eso y "
                      "de HEC-14. «envolvente_hec14», el valor del archivo "
                      "por decision del dueño del proyecto, toma en cada "
                      "magnitud el mayor: la piedra es el mayor del d50 de "
                      "Laushey (Manual, num. 4.1.1.3.7 c), que se sigue "
                      "calculando e imprimiendo) y del D50 de la Ec. (10.4) "
                      "de HEC-14 (cita HEC14.10.2#EC_10_4); el espesor y la "
                      "longitud, el mayor de los adoptados "
                      "('espesor_proteccion_salida', "
                      "'longitud_proteccion_salida') y de los que la Tabla "
                      "10.1 da a esa piedra (cita HEC14.10.2#T10_1, y "
                      "HEC14.10.2#PROFUNDIDAD para el piso del espesor, dos "
                      "veces el D50). Por que: ninguna de las dos fuentes "
                      "queda por debajo de la otra en todos los casos. "
                      "Laushey mira solo la velocidad y pide mas piedra en "
                      "la descarga rapida; la Ec. (10.4) mira el caudal, el "
                      "diametro y el tirante del receptor y pide mas en la "
                      "descarga lenta y caudalosa (a seccion llena y con el "
                      "tirante minimo de la ecuacion, siempre que Q/D^2.5 < "
                      "2.9); y el espesor adoptado, un multiplo del d50 menor "
                      "que dos, queda bajo el piso de HEC-14 en todo punto. "
                      "«manual» es la "
                      "regla anterior y reproduce sus numeros: rigen Laushey "
                      "y lo adoptado, HEC-14 se imprime al lado y la corrida "
                      "avisa donde pide mas. Donde HEC-14 no es evaluable "
                      "(marco, tirante del receptor sobre la clave, conducto "
                      "de mas de 60 pulgadas, varios barriles) rige Laushey "
                      "con lo adoptado, con aviso, bajo las dos reglas. Si "
                      "la piedra que rige no cabe en la Tabla 10.1, el "
                      "espesor y la longitud son cotas inferiores (dos veces "
                      "el d50 y la longitud de la ultima clase, lectura del "
                      "proyecto) y la corrida avisa que la salida pide un "
                      "disipador",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.1.3.7 c), ec. (49), cita MC_HHD.4.1.1.3.7c; HEC-14 3a "
               "ed., Sec. 10.2, Ec. (10.4), pag. impresa 10-17 (PDF 218), "
               "cita HEC14.10.2#EC_10_4, y Table 10.1, pag. impresa 10-18 "
               "(PDF 219), citas HEC14.10.2#T10_1 y HEC14.10.2#PROFUNDIDAD. "
               "La eleccion entre las dos reglas es adopcion del proyecto: "
               "ninguna fuente dice que hacer cuando las dos discrepan",
        reemplazado_por="El diseño de la proteccion de salida del "
                        "expediente, con la granulometria y el filtro",
        resolucion=Libre(
            que_lo_fija="el dueño del proyecto: la envolvente con HEC-14 "
                        "o lo que da el Manual con lo adoptado",
            dominio="declaracion de la regla; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    "relacion_co_poza_enrocado_hec14": Criterio(
        # --- VE-4g --- NIVEL NO MEDIDO POR CORRIDA: solo se invoca donde el
        # apron de HEC-14 no llega (marco o conducto de mas de 60 in) y la
        # poza si; ningun punto de las corridas de referencia cae ahi. Lo
        # consume M6 (Fase 6), que corre a perfil; lo mide
        # `tests/test_ve4g_hec14_limites.py`.
        valor="envolvente",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("envolvente", "mejor_ajuste"),
        concepto="Relacion del parametro de tirante del receptor (Co) con "
                 "que se dimensiona la poza de enrocado de HEC-14",
        justificacion="La Ec. (10.1) de HEC-14 da la profundidad de la poza "
                      "de enrocado restando un parametro Co que depende del "
                      "tirante del receptor, y la fuente da DOS relaciones "
                      "para el: la envolvente de los ensayos, Ec. (10.2), y "
                      "el mejor ajuste, Ec. (10.3), que resta 0.6 veces ye "
                      "mas y da una poza menos profunda y mas corta. Ella "
                      "misma dice cuando usar cada una: la envolvente cuando "
                      "la consecuencia de la falla cerca del caudal de diseño "
                      "es severa y el mejor ajuste cuando la falla de la "
                      "poza se puede atender con el mantenimiento rutinario "
                      "(cita HEC14.10.1#CO_ENVOLVENTE). La consecuencia de "
                      "la falla de la proteccion de una alcantarilla vial es "
                      "el socavamiento y el colapso del conducto (num. "
                      "10.1.4), y por eso el archivo trae la envolvente, el "
                      "lado conservador. El mejor ajuste queda barrible; los "
                      "valores intermedios de Co que la fuente admite no se "
                      "ofrecen",
        fuente="HEC-14 3a ed., num. 10.1.1, Ec. (10.1) a (10.3), pag. "
               "impresa 10-3 (PDF 204), citas HEC14.10.1#EC_10_1 y "
               "HEC14.10.1#CO_ENVOLVENTE. La eleccion entre las dos es del "
               "proyecto: la fuente la condiciona a la consecuencia de la "
               "falla, que no es un dato",
        reemplazado_por="El diseño de la proteccion de salida del "
                        "expediente",
        resolucion=Libre(
            que_lo_fija="el dueño del proyecto, segun la consecuencia de la "
                        "falla de la poza que acepte",
            dominio="declaracion de la relacion; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    "referencia_profundidad_socavacion": Criterio(
        # NIVEL NO MEDIDO POR CORRIDA: solo se invoca con el lecho declarado
        # o la socavacion declarada; lo mide `tests/test_t8_proteccion.py`.
        valor="fondo_del_cauce_receptor",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("fondo_del_cauce_receptor", "solera_de_salida"),
        concepto="Cota desde la que se mide la profundidad de socavacion "
                 "a la salida que se entrega al desplante del cabezal",
        justificacion="Decide la cota del fondo de la hoya de socavacion. "
                      "HEC-14 Cap. 5 no la define: llama hs a la profundidad "
                      "de socavacion sin figura que la acote, y con la salida "
                      "por encima del lecho (Tabla 5.2) las dos lecturas "
                      "difieren en la caida, unos 0.7 m en A-01. La Figura "
                      "10.1 de la poza de enrocado, otro metodo, mide hs "
                      "desde la solera de salida (cita HEC14.10.1#HS). "
                      "«fondo_del_cauce_receptor», el valor del archivo, es "
                      "la lectura conservadora para el desplante: la hoya "
                      "empieza en el lecho y queda a la caida mas abajo que "
                      "con la otra. «solera_de_salida» es la de la Figura "
                      "10.1. Una profundidad declarada por un estudio del "
                      "cauce se mide desde la misma referencia",
        fuente="HEC-14 3a ed., Cap. 5, pags. impresas 5-1 a 5-3 (PDF 54 a "
               "56), sin figura que defina hs; Sec. 10.1, Figura 10.1, pag. "
               "impresa 10-1 (PDF 202). La eleccion es adopcion del "
               "proyectista",
        reemplazado_por="El estudio de socavacion del cauce receptor, que "
                        "dice su propia referencia",
        resolucion=Libre(
            que_lo_fija="el proyectista: la fuente no fija la referencia",
            dominio="declaracion de la referencia; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    # --- T-7a --- EL ANGULO DE LAS ALETAS DEJA DE SER UN VACIO Y PASA A SER
    # UNA REGLA DECLARADA (INF-4.3). Y deja de ser de EXPEDIENTE: el angulo
    # elige, en un marco, la banda de filas de las Tablas A.1 y C.2 del HDS-5
    # que la embocadura declarada del cajon tiene que respetar
    # (`M9.verificar_coherencia_embocadura_cajon`), y eso corre antes de la
    # Fase 4, en los dos alcances. Lo mide la corrida de perfil: es de perfil.
    "angulo_aletas": Criterio(
        valor={"por_defecto_grados": 45.0, "umbral_esviaje_grados": 30.0,
               "con_esviaje_mayor_grados": 30.0},
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        # VENTANA POR CAMPO. Los dos angulos se mueven entre 30 y 60 grados:
        # la «ventana completa» {30, 45, 60} del encargo, y la banda de la
        # Tabla C.2 que la contiene entera -- «Wingwalls at 30⁰ to 75⁰ to
        # barrel» --, de modo que dentro de la ventana el ke de un marco con
        # borde a escuadra no cambia (0.4) y si cambia la fila de la Tabla A.1
        # en las cartas que nombran un angulo exacto (Cartas 9, 12 y 13). El
        # umbral de esviaje, entre 15 y 45 grados.
        sensibilidad={"por_defecto_grados": (30.0, 60.0),
                      "umbral_esviaje_grados": (15.0, 45.0),
                      "con_esviaje_mayor_grados": (30.0, 60.0)},
        concepto="Angulo de las aletas del cabezal con la prolongacion de la "
                 "pared del barril (paralela al eje del conducto), "
                 "como regla por punto: el de por defecto, y el que rige "
                 "cuando el esviaje del cruce supera un umbral",
        justificacion="Decide el angulo de los aleros de cada cabezal, que "
                      "la memoria imprime y del que salen la longitud de los "
                      "aleros y, en un marco, la banda de filas del HDS-5 "
                      "que la embocadura del cajon tiene que respetar. La "
                      "fuente (HDS-5, List of Symbols, pag. impresa xix; "
                      "cita HDS5_3ED.SIMBOLOS#THETA_W) define el angulo de "
                      "los aleros con la prolongacion de la pared del barril"
                      ", que es tambien lo que dicen los rotulos de la Tabla "
                      "C.2 (pag. impresa C.6; cita HDS5_3ED.TC.2), que "
                      "agrupa sus filas de cajon por bandas de ese angulo; "
                      "la Lamina Nº 02-A del Manual "
                      "dibuja la salida con aleros y deja el angulo sin "
                      "acotar. Lo que no resuelven: ninguna fuente de "
                      "normas/ fija el angulo para una obra, y con un TUBO "
                      "el angulo no mueve ni ke ni la carta: la Tabla C.2 "
                      "pone el tubo con cabezal y con cabezal y aleros en "
                      "la misma fila, y las Cartas 1 a 3 no separan aleros "
                      "(ficha T2-04). Se "
                      "adopta la regla de practica del INFORME §4.3 y del "
                      "encargo de T-7a: 45 grados por defecto y 30 grados "
                      "cuando el esviaje supera 30 grados, los dos dentro de "
                      "la banda de 30 a 75 grados de la Tabla C.2. La tercera "
                      "rama del encargo -- 60 grados en caja receptora -- "
                      "no se adopta: la Lamina Nº 02-A dibuja la entrada tipo "
                      "caja receptora SIN aleros, y ninguna fuente de normas/ "
                      "da un angulo para ella; los 60 grados quedan dentro "
                      "de la ventana como alternativa declarable",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, List of Symbols, ΘW, pag. "
               "impresa xix (PDF 23; cita HDS5_3ED.SIMBOLOS#THETA_W); "
               "Apendice C, Tabla C.2 "
               "'Entrance Loss Coefficients', pag. impresa C.6 (PDF 216), "
               "bloques 'Pipe, Concrete' y 'Box, Reinforced Concrete'; "
               "Manual de Hidrologia, Lamina Nº 02-A, pag. impresa 208 (PDF "
               "211; cita MC_HHD.LAMINA_02A). La regla (45 / 30 por esviaje) "
               "es de practica de predimensionamiento (INFORME §4.3), no "
               "verificada contra una fuente de normas/",
        reemplazado_por="El plano de aleros del expediente, con el angulo "
                        "de cada cabezal dibujado sobre el esviaje medido",
        resolucion=Libre(
            que_lo_fija="el proyectista: ninguna fuente de normas/ fija el "
                        "angulo de las aletas de una obra",
            dominio="grados con la pared del barril: los dos angulos entre "
                    "30 y 60, el umbral de esviaje entre 15 y 45",
        ),
    ),

    # --- T-7a --- LA EMBOCADURA DEL CABEZAL, la otra mitad de la decision:
    # con aleros o sin ellos. Es de PERFIL por lo mismo que el angulo: entra
    # a la proteccion de entrada (Fase 6) y a la coherencia de la embocadura
    # del marco con el cabezal, que corren en los dos alcances.
    "embocadura_cabezal": Criterio(
        valor="cabezal_con_aleros",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("cabezal_con_aleros", "cabezal_recto"),
        concepto="Remate de los dos extremos del conducto: cabezal con "
                 "aleros o cabezal recto (sin aleros)",
        justificacion="Decide si los cabezales llevan aleros, y con eso que "
                      "se protege a la entrada (Fase 6), si se predimensionan "
                      "aleros en la Fase 9 y, en un marco, que filas del "
                      "HDS-5 puede declarar su embocadura. La fuente (Lamina "
                      "Nº 02-A del Manual, pag. impresa 208) dibuja la salida "
                      "con aleros y sin aleros, sin preferir ninguna; el "
                      "HDS-5, Tabla C.2, agrupa el tubo con cabezal y con "
                      "cabezal y aleros en la MISMA fila. Lo que no "
                      "resuelve: cual lleva esta obra. Se adopta el cabezal "
                      "con aleros, que es lo que el INFORME §4.3 pide "
                      "dimensionar y lo que protege el talud a los lados de "
                      "la boca (AASHTO LRFD 12.6.5 pide extender los aleros "
                      "hasta proteger el relleno estructural del conducto; "
                      "cita AASHTO_LRFD_9.12.6.5#ALEROS). Con tubo, "
                      "las dos opciones dan el mismo ke (0.5) y la misma "
                      "carta: ningun diametro se mueve; con marco, la opcion "
                      "elige la banda de filas que la embocadura declarada "
                      "del cajon tiene que respetar. Lo que el catalogo no "
                      "tiene es la caja receptora de la Lamina Nº 02-A, que "
                      "es la entrada habitual de un alivio de cuneta "
                      "(Familia B): un punto B recibe un cabezal con aleros "
                      "-- o recto -- y la corrida lo avisa (ficha T7A-02)",
        fuente="Manual de Hidrologia, Lamina Nº 02-A, pag. impresa 208 (PDF "
               "211; cita MC_HHD.LAMINA_02A); HDS-5 3a ed., Tabla C.2, pag. "
               "impresa C.6 (PDF 216); AASHTO LRFD 9a ed., 12.6.5, pag. "
               "impresa 12-20 (PDF 1658; cita AASHTO_LRFD_9.12.6.5#ALEROS). "
               "La eleccion es del proyecto",
        reemplazado_por="El plano de cabezales del expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre las dos salidas que dibuja la "
                        "Lamina Nº 02-A",
            dominio="una de las dos opciones; el conjunto cerrado viaja en "
                    "`sensibilidad`",
        ),
    ),
}
