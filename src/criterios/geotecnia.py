"""
Fichas de criterios adoptados del dominio: geotecnia.
"""

from typing import Dict
from src.modelos import DeCatalogo, DeEnsayo, DeTabla, Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_DICT_CON_CAMPOS,
    FORMA_FLOAT,
    FORMA_INT,
    FORMA_PAR_ORDENADO,
    FORMA_SERIE_DE_CLAVES,
    FORMA_SERIE_DE_PARES,
    FORMA_STR,
    NIVEL_EXPEDIENTE,
    NIVEL_PERFIL,
    _CLAVES_DE_PLANCHA_TMC,
    _ESPESOR_HDPE_AASHTO,
    _SIMBOLOS_SUCS_E050,
    _TOPES_DE_LA_NORMA_DE_PRODUCTO,
)


CRITERIOS: Dict[str, Criterio] = {


    # ----------------------- GEOTECNIA -----------------------------------

    "phi_relleno_trasdos": Criterio(
        valor=None,                 # completar
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Angulo de friccion interna del material de cantera del trasdos",
        justificacion="Estimado por correlacion desde granulometria y grado de "
                      "compactacion especificado",
        fuente="PENDIENTE",
        reemplazado_por="Ensayo de corte directo sobre el material de cantera",
        sensibilidad=(30.0, 38.0),
        resolucion=Libre(
            que_lo_fija="el proyectista, con el ensayo del material de "
                        "cantera del trasdos o un valor de practica "
                        "corriente declarado con su fuente",
            dominio="grados, 0 < phi < 90",
        ),
    ),

    "c_phi_fundacion": Criterio(
        # --- T-7b --- TIENE CONSUMIDOR: `M9.ensamble_estabilidad` (portante
        # y deslizamiento). Sigue VACIO: son datos del estudio de suelos y el
        # programa no los supone. Es el valor de CORREDOR; un punto puede
        # traer el suyo en `--datos-externos` (`suelo_fundacion`), que gana.
        valor=None,                 # completar con el EMS
        nivel=NIVEL_EXPEDIENTE,
        # ES [S], NO [A] (VE-3, ficha VE2-05, decision del dueño): son los
        # parametros que el EMS de ESTE sitio mide; no hay rango que elegir y
        # se defienden con la trazabilidad de la lectura, como el peso
        # especifico saturado del relleno desde N2 de VE-2. Sin `positivo`:
        # la forma es un dict (un booleano y tres numeros) y sus campos los
        # valida el consumidor, `M9.validar_suelo_fundacion`.
        etiqueta="S",
        forma=FORMA_DICT_CON_CAMPOS,
        # Los cuatro campos obligatorios (cohesivo, c_kpa, phi_grados,
        # gamma_kn_m3) NO van en `campos_obligatorios`, que exige TEXTO en
        # cada uno (EXT-6): son un booleano y tres numeros, y los valida el
        # consumidor, `M9.validar_suelo_fundacion`, con `DatoInvalidoError`.
        concepto="Parametros del suelo de fundacion del cabezal: si se trata "
                 "como cohesivo o friccionante, cohesion (kPa), angulo de "
                 "friccion interna (grados) y peso especifico (kN/m3); y, si "
                 "el estudio de suelos las entrega, la resistencia portante "
                 "NOMINAL `q_n_kpa` y la presion ADMISIBLE `q_adm_kpa`",
        justificacion="Deciden la resistencia al deslizamiento y la "
                      "capacidad portante bajo la zapata del cabezal, en los "
                      "dos marcos. Son datos del estudio de mecanica de "
                      "suelos del expediente: el programa no los deduce de "
                      "la clasificacion SUCS del CSV ni los supone, y sin "
                      "ellos la estabilidad del cabezal se detiene. E.050 "
                      "Art. 20 obliga a usar solo uno de los dos parametros: "
                      "phi = 0 en los suelos cohesivos y c = 0 en los "
                      "friccionantes; cual de los dos es el caso lo declara "
                      "el campo `cohesivo`, porque los suelos de frontera "
                      "(SC, SM, ML) los decide el geotecnista y no una "
                      "regla. Dos campos opcionales, para lo que el "
                      "estudio entregue directamente, y cada uno entra en UN "
                      "marco: `q_n_kpa`, la resistencia portante nominal "
                      "(ultima), gana sobre la calculada con la ecuacion de "
                      "AASHTO 10.6.3.1.2a en el marco de estados limite; "
                      "`q_adm_kpa`, la presion admisible, que ya lleva su "
                      "factor de seguridad, gana en el marco de factores de "
                      "seguridad y no entra en el otro: multiplicarla por un "
                      "factor para volverla nominal seria cruzar los marcos",
        fuente="Estudio de mecanica de suelos (EMS) del expediente: ensayo "
               "de corte directo o triaxial, o correlacion con SPT, por "
               "calicata. E.050 Art. 20 (cita E050.20) para la regla de c "
               "y phi",
        trazabilidad="NO SE HA EJECUTADO NINGUN ENSAYO. La lectura que hace "
                     "falta: del EMS del expediente, por calicata y a la "
                     "profundidad de desplante del cabezal, si el suelo se "
                     "trata como cohesivo o friccionante, la cohesion (kPa), "
                     "el angulo de friccion interna (grados) y el peso "
                     "especifico (kN/m3), con el ensayo (corte directo o "
                     "triaxial, o la correlacion con SPT declarada), y si "
                     "el EMS las entrega la resistencia portante nominal y "
                     "la presion admisible. Se declara con el ensayo, la "
                     "calicata, la profundidad y el laboratorio "
                     "(`DeEnsayo.trazabilidad_exigida`). Es el valor de "
                     "CORREDOR: vale mientras el EMS lo de por tramo "
                     "homogeneo, y un punto con otro suelo trae el suyo en "
                     "`suelo_fundacion` de `--datos-externos`, que gana",
        reemplazado_por="Corte directo o SPT",
        resolucion=DeEnsayo(
            ensayo="parametros de resistencia y peso especifico del suelo de "
                   "fundacion (c, phi, gamma), del EMS del expediente",
            trazabilidad_exigida="ensayo (corte directo o triaxial), "
                                 "calicata, profundidad y laboratorio; la "
                                 "columna `sucs_fundacion` del CSV es su "
                                 "entrada por correlacion",
        ),
    ),

    "capacidad_portante_adm": Criterio(
        valor=None,                 # completar
        nivel=NIVEL_EXPEDIENTE,
        # ES [S], NO [A] (VE-3, ficha VE2-05, decision del dueño): la
        # presion admisible la entrega el EMS de ESTE sitio; no hay rango que
        # elegir. `positivo`: una presion admisible no es cero ni negativa.
        etiqueta="S",
        forma=FORMA_FLOAT,
        positivo=True,
        concepto="Capacidad portante admisible del terreno de fundacion",
        justificacion="Derivada de c_phi_fundacion, que es a su vez un dato "
                      "de ensayo del EMS ([S])",
        fuente="PENDIENTE",
        trazabilidad="NO SE HA EJECUTADO NINGUN ENSAYO. La lectura que hace "
                     "falta: la presion admisible del terreno de fundacion "
                     "que entrega el EMS, en kPa, con la calicata, la "
                     "profundidad de desplante, el metodo de calculo y el "
                     "factor de seguridad que adopta "
                     "(`DeEnsayo.trazabilidad_exigida`). Depende de la "
                     "zapata de cada cabezal, de modo que un valor de "
                     "corredor solo vale para un tramo homogeneo",
        reemplazado_por="EMS conforme a E.050",
        # --- VE-5 (ficha T7B-04) --- TIENE CONSUMIDOR desde VE-5
        # (`M9.suelo_de_fundacion`): es la presion admisible de CORREDOR, la
        # misma magnitud que el campo `q_adm_kpa` de 'c_phi_fundacion', y
        # entra cuando ese campo no viene (si vienen los dos y difieren, se
        # detiene). Hasta VE-5 era sin consumidor; el censo pedia retirarla
        # o darle uno, y se le dio porque el Anexo A de la hoja de ruta la
        # nombra. El suelo de un punto (`suelo_fundacion`) no la hereda.
        resolucion=DeEnsayo(
            ensayo="capacidad portante admisible del terreno de fundacion, "
                   "del EMS del expediente",
            trazabilidad_exigida="calicata, profundidad de desplante, metodo "
                                 "de calculo y factor de seguridad "
                                 "adoptados por el EMS",
        ),
    ),

    "Mw_licuefaccion": Criterio(
        valor=None,                 # VACIO: bloquea la evaluacion de licuefaccion
        # NIVEL POR CONSUMIDOR (VE-5, lote catlic): lo lee la Fase 0-bis
        # (`ML._contrastar_declarada`) cuando el EMS declara su resultado de
        # licuefaccion; la corrida de perfil difiere ese modulo entero.
        nivel=NIVEL_EXPEDIENTE,
        # SIGUE [A] (VE-3, ficha VE2-05, decision del dueño), aunque se
        # resuelva `DeEnsayo` como los dos parametros del suelo que pasaron
        # a [S]: elegir el escenario sismico -- la desagregacion del peligro
        # o el sismo de subduccion que se adopta -- es una decision del
        # proyectista, no la lectura de un ensayo.
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Magnitud sismica para el factor de escala de magnitud (MSF)",
        justificacion="El procedimiento simplificado de evaluacion de licuefaccion "
                      "no se alimenta solo de a_max: requiere Mw para el MSF. El "
                      "mapa de PGA no la entrega",
        fuente="PENDIENTE: desagregacion del peligro sismico o adopcion justificada "
               "del sismo de diseno de la subduccion del norte peruano",
        reemplazado_por="Estudio de peligro sismico especifico",
        resolucion=DeEnsayo(
            ensayo="desagregacion del peligro sismico del sitio, o adopcion "
                   "justificada del sismo de diseño de la subduccion del "
                   "norte peruano",
            trazabilidad_exigida="el estudio de peligro y el periodo de "
                                 "retorno sobre el que se desagrego; si en "
                                 "vez del estudio se adopta el sismo de "
                                 "subduccion, la fuente que lo caracteriza",
        ),
    ),

    "demanda_sismica_licuefaccion": Criterio(
        valor=1000,                 # anios
        # NIVEL MEDIDO (VE-5, lote catlic): lo invoca la Fase 0-bis
        # (`ML.evaluar_licuefaccion`) en la corrida `--alcance expediente` y
        # no en la de perfil, que difiere ese modulo entero. Hasta VE-5 no lo
        # consumia ningun modulo.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_INT,
        concepto="Periodo de retorno para la evaluacion de licuefaccion",
        justificacion="Se descarta el sismo de 475 anios de E.030. Al tratarse de "
                      "infraestructura vial regida por el Manual de Puentes, se "
                      "exige al suelo la misma demanda que a la estructura que "
                      "soporta. Un terreno evaluado a 475 anios bajo una estructura "
                      "disenada a 1000 es incoherencia de niveles de seguridad",
        fuente="Coherencia con el marco del Manual de Puentes",
        sensibilidad=(475, 1000),
        resolucion=Libre(
            que_lo_fija="el proyectista, por coherencia de niveles de "
                        "seguridad con el marco del Manual de Puentes",
            dominio="años > 0",
        ),
    ),

    "diametros_normalizados": Criterio(
        valor={"inicio": 0.90, "paso": 0.15},
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Progresion de diametros normalizados (inicio y paso)",
        justificacion="Decide la progresion de diametros normalizados con que "
                      "el solver recorre el catalogo: inicio en 0.90 m y paso "
                      "de 0.15 m. Las fuentes (series de diametro nominal de "
                      "las normas de producto y minimo normativo peruano del "
                      "num. 4.1.1.3.4 a, con su ambito condicional; ver "
                      "`fuente` y constantes_normativas.DIAMETRO_MIN_AMBITO) "
                      "dan la serie y el piso. Lo que no resuelven: ninguna "
                      "norma fija la progresion de busqueda, y la neutralidad "
                      "comercial exigible en obra publica impide resolverla "
                      "por catalogo de proveedor. Se adopta el paso de 0.15 m "
                      "porque reproduce las series de 6 in (ASTM/AASHTO: 6 in "
                      "= 0.1524 m) y de 150 mm (AASHTO M 294-11, verificado en "
                      "N2 sobre su traduccion no oficial: de 900 a 1500 mm la "
                      "serie es exactamente 900, 1050, 1200, 1350 y 1500) con "
                      "error despreciable, "
                      "y el inicio en 0.90 m en vez de 0.9144 m (36 in) "
                      "porque subestima el area en torno al 3 %, del lado de "
                      "la seguridad. Este criterio no declara topes: los "
                      "topes por material no salen de ninguna norma y viven "
                      "en 'D_max_catalogo', rotulados como topes de catalogo "
                      "-- una clase de dato distinta del paso, que si se "
                      "verifica contra la serie de la norma de producto",
        fuente="Series de diametro nominal de las normas de producto: ASTM "
               "A760/A760M-10, Tabla 1 'Tamaños de tuberia' (100 a 3600 mm, en "
               "escalones de 150 mm a partir de 900 mm); AASHTO M 170M-04, "
               "Tablas 1 a 5 (300 a 3600 mm); AASHTO M 294-11, num. 7.2.1 y "
               "tabla de 7.2.2 (300 a 1500 mm, escalones de 150 mm a partir "
               "de 900 mm; en normas/ desde N2 como TRADUCCION NO OFICIAL, "
               "citas AASHTO_M294_TRAD.7.2.1 y tabla AASHTO_M294_TRAD.T7.2.2, "
               "sin firma porque el ejemplar no imprime folio, T6; la v8 §3.2 "
               "decia «pasos de 150 mm por encima de 600 mm» y la serie tiene "
               "el 675: discrepancia registrada contra la hoja de ruta y "
               "corregida en N2, ver el manifiesto). El "
               "piso de 0.90 m no sale de ellas sino del minimo normativo "
               "peruano: Manual de Hidrologia num. 4.1.1.3.4 a), pag. impresa "
               "72 (constantes_normativas.DIAMETRO_MIN). "
               "EL PISO ES CONDICIONAL Y ESTE CAMPO LO OMITIA (NOR-HID-03, "
               "MAT-O19). El numeral lo escribe asi: 'En carreteras de alto "
               "volumen de transito y por necesidad de limpieza y "
               "mantenimiento de las alcantarillas, se adoptara una seccion "
               "minima circular de 0.90 m (36\") de diametro o su equivalente "
               "de otra seccion, salvo en cruces de canales de riego donde se "
               "adoptaran secciones de acuerdo a cada diseno particular'. Las "
               "dos condiciones tocan a este proyecto: la clase de via NO esta "
               "cerrada, de modo que 'alto volumen de transito' no se puede "
               "afirmar -- el piso se aplica igual a las Familias A y B y eso "
               "es una adopcion conservadora declarada, no una lectura "
               "automatica --, y la Familia C ES un conjunto de cruces de "
               "canal, o sea el caso que el numeral EXCEPTUA. El detalle esta "
               "en constantes_normativas.DIAMETRO_MIN_AMBITO, que la memoria "
               "imprime",
        resolucion=Libre(
            que_lo_fija="la serie de diametro nominal de la norma de "
                        "producto para el paso, y el proyecto para el "
                        "inicio (0.90 m frente a los 0.9144 m = 36 in de la "
                        "serie real, ~3 % del lado seguro). NO es "
                        "`DeCatalogo`, aunque la Sec. 4.3 del plan lo ponga "
                        "de ejemplo: el ejemplo apunta al 'max' que este "
                        "criterio ya no tiene -- S4 mudo los topes a "
                        "`D_max_catalogo`, que si es de catalogo -- y la "
                        "neutralidad comercial en obra publica prohibe "
                        "justamente resolver la serie por catalogo",
            tabla_pendiente="ASTM A760/A760M-10, Tabla 1 'Tamaños de "
                            "tuberia' (100 a 3600 mm). Su PDF no entrega "
                            "texto utilizable y por eso no esta transcrita",
        ),
    ),

    # --- VE-2 (g) --- (decision del dueño, 2026-11-17, ficha VE1-02 (g)) EL
    # DIAMETRO INGLES CONVERTIDO SOLO EN EL CONCRETO, Y DECLARADO. La guardia
    # de M2 (`M2._exigir_escalon_designado`) rechaza, por material, el escalon
    # que no sea un diametro DESIGNADO de su norma de producto
    # (`constantes_normativas.DIAMETROS_DESIGNADOS_MM`, [N]). AASHTO M 170M es
    # la unica de las tres que deja al fabricante diseñar con el diametro
    # ingles convertido (num. 12.1); este criterio dice si el catalogo del
    # proyecto lo admite. El valor de archivo, 'designado', no mueve nada: la
    # progresion de archivo (0.90 + 0.15 m) es toda designada.
    "diametro_de_diseno_concreto": Criterio(
        valor="designado",
        # DE PERFIL: lo lee `M2.siguiente_diametro` en cada escalon del tubo
        # de concreto, que la corrida `--alcance perfil` recorre (lo mide
        # `tests/test_nivel_medido.py`).
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("designado", "designado_o_ingles_convertido"),
        concepto="Diametros de diseño que admite la progresion del tubo de "
                 "concreto: solo los DESIGNADOS de AASHTO M 170M, o tambien "
                 "el diametro ingles convertido de cada uno",
        justificacion="Decide que diametros de la progresion se admiten en "
                      "el tubo de concreto. AASHTO M 170M, num. 12.1 (pag. "
                      "impresa M 170M-19, cita AASHTO_M170M.12.1), deja al "
                      "FABRICANTE elegir como diametro de diseño el "
                      "designado o el ingles convertido, y su Table 6 da por "
                      "cada designado el ingles convertido (1050 mm -> 42 in "
                      "-> 1067 mm). La eleccion no es de una norma peruana "
                      "ni del proyecto por si solo: depende del producto que "
                      "se especifique, y por eso [A]. Se adopta 'designado': "
                      "la serie metrica designada de la norma, la misma que "
                      "M 36 / ASTM A760 y M 294 designan para el TMC y el "
                      "HDPE, y la que recorre la progresion de archivo (0.90 "
                      "+ 0.15 m). 'designado_o_ingles_convertido' admite "
                      "ademas el diametro ingles convertido de cada fila (la "
                      "serie de 6 in, 0.9144 + 0.1524 m): +1.6 % de "
                      "diametro y +3.2 % de area en el 900, del lado de la "
                      "capacidad. NO alcanza al TMC ni al HDPE: M 36 (num. "
                      "8.1.1 y Table 6) y M 294 (num. 7.2.1) solo designan "
                      "la serie metrica, y alli un escalon de 6 in se "
                      "rechaza con cualquier valor de este criterio",
        fuente="AASHTO M 170M-04, num. 12.1 «Internal Diameter», pag. "
               "impresa M 170M-19 (PDF 19), cita AASHTO_M170M.12.1, y Table 6 "
               "«Permissible Variation in Internal Diameter», pag. impresa M "
               "170M-20 (PDF 20), tabla AASHTO_M170M.T6, leidas por imagen "
               "(el ejemplar es una recomposicion OCR: las correcciones "
               "estan declaradas en la cita y en las erratas de la tabla del "
               "registro). Las "
               "series designadas de los tres materiales: "
               "constantes_normativas.DIAMETROS_DESIGNADOS_MM (Tabla 5 de "
               "M 170M; Table 6 de M 36 y Tabla 1 de A760; num. 7.2.1 y tabla "
               "de 7.2.2 de M 294, traduccion no oficial)",
        reemplazado_por="Especificacion del tubo de concreto con el diametro "
                        "de diseño que el fabricante adopte (num. 12.1)",
        resolucion=Libre(
            que_lo_fija="el fabricante, a su opcion (AASHTO M 170M num. "
                        "12.1); el proyecto declara cual admite su catalogo",
            dominio="designado | designado_o_ingles_convertido",
        ),
    ),

    # =======================================================================
    # LOS SIETE DEL CAJON (C5 y C7). DESDE T-3 TODOS LLEVAN VALOR DE ARCHIVO.
    # =======================================================================
    # --- T-3 --- (cadena T, INF-0.4). Hasta T-3 este encabezado decia
    # «NINGUNO LLEVA VALOR, Y NO ES UN OLVIDO», y era la regla del plan de la
    # Familia C (§11 criterio 7 de docs/ruta_familia_c.md: «Ningun criterio
    # nuevo tiene valor escrito en criterios_adoptados.py»). T-3 la levanta
    # por mandato de la cadena T --que la Familia C se dimensione sin que el
    # tesista tenga que declarar siete criterios en caliente-- y la levanta
    # SIN MOVER NADA: cada valor de archivo es el que la guia de perfil, la
    # suite y la corrida del entregable de C7 declaraban en caliente, y C-01
    # sigue saliendo como marco 1.20 x 0.90 con HW 0.589 m. Lo que cambia es
    # que cada valor queda en el archivo CON SU FILA NOMBRADA, su cita y su
    # ventana, y que los que cubren un vacio verificado lo dicen en
    # `vacio_verificado` (R-23 de §15.8 se cierra por esa via: con valor de
    # archivo el campo ya se puede poner). La progresion de secciones es la
    # excepcion declarada: la de la cadena T no se adopta porque deja a C-01
    # sin dimensionar (PARADA (c), ver su ficha).
    #
    # Lo que sigue del encabezado de C5 vale igual:
    # La Familia C es el conjunto de cruces de canal de riego, y el propio
    # numeral que fija el piso de 0.90 m la EXCEPTUA de el: "salvo en cruces
    # de canales de riego donde se adoptaran secciones de acuerdo a cada
    # diseno particular". Lo que el numeral hace no es liberar la seccion --
    # la traslada del catalogo al DISENO --, y por eso estos cuatro son
    # adopciones declaradas y no lecturas de la norma.
    #
    # LOS CUATRO SE MUEVEN JUNTOS EN DOS PARES, y quien declare uno tiene que
    # mirar su pareja:
    #   'embocadura_cajon'  <->  'ke_entrada_cajon'   (Tabla A.1 y Tabla C.2)
    #   'secciones_cajon_normalizadas'  <->  'n_celdas_cajon'  (B*H por celda)
    #
    # NO SE ABRE 'v_max_cajon', y conviene decir por que se decidio NO abrirlo:
    # la Tabla N 10 clasifica por TIPO DE REVESTIMIENTO --"Concreto 3.0 - 6.0
    # m/s"-- y no por forma de seccion, de modo que su fila sirve al marco tal
    # cual. Abrir un criterio ahi seria inventar un vacio que no existe, que
    # es el error simetrico del que estos cuatro evitan.

    "secciones_cajon_normalizadas": Criterio(
        # --- T-3 --- LA DECISION DEL DUEÑO DEL PROYECTO (2026-11-12): se
        # mantiene la progresion con que C-01 dimensiona desde C7; la de la
        # cadena T no se activa. Ampliarla espera la seccion real del canal
        # (ANA / Junta): ficha T3-01. Ver la justificacion.
        valor=((1.20, 0.90), (1.50, 1.20), (2.00, 1.50)),
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_SERIE_DE_PARES,
        concepto="Progresion de secciones normalizadas del marco: ancho B y "
                 "altura H interiores de UNA celda",
        justificacion="Decide la progresion de secciones normalizadas del "
                      "marco -- la serie de pares (B, H) interiores de una "
                      "celda, de menor a mayor -- que el bucle de MD recorre "
                      "igual que recorre los diametros: hace falta la serie y "
                      "su orden, no un solo par. Las fuentes (num. 4.1.1.3.4 "
                      "a) y num. 4.1.1.3.7 d) del Manual de Hidrologia; citas "
                      "MC_HHD.4.1.1.3.4a y MC_HHD.4.1.1.3.7d del registro, "
                      "traidas por los Fundamento F3.SECCION_CANAL y "
                      "F3.MANTENIMIENTO) dicen dos cosas: el mismo numeral "
                      "que fija el piso de 0.90 m lo exceptua, en la misma "
                      "oracion, para los cruces de canales de riego -- que es "
                      "lo que la Familia C es, de modo que el marco no hereda "
                      "ese piso; el texto literal y su ambito estan en "
                      "constantes_normativas.DIAMETRO_MIN_TEXTO y "
                      "DIAMETRO_MIN_AMBITO y no se repiten aqui --, y el num. "
                      "4.1.1.3.7 d) exige, sin distinguir forma alguna, que "
                      "las dimensiones permitan el mantenimiento y la "
                      "limpieza en el interior del conducto. Lo que no "
                      "resuelven: la exigencia de mantenimiento no trae "
                      "numero -- obliga a que exista un minimo y deja al "
                      "proyecto decir cual --, y la seccion del cruce de "
                      "canal se remite a cada diseno particular. Por eso el "
                      "criterio es [A] y no [N]: la norma pide el requisito y "
                      "no da la cifra. Se adopta la progresion ((1.20, "
                      "0.90), (1.50, 1.20), (2.00, 1.50)): arranca en la "
                      "altura interior de 0.90 m, que es la seccion minima "
                      "de mantenimiento que el mismo num. 4.1.1.3.4 a) fija "
                      "para las demas alcantarillas -- aqui por analogia, "
                      "porque el numeral exceptua el cruce de canal --; "
                      "lleva B >= H porque un cruce de canal es ancho y poco "
                      "profundo; y crece en las dos dimensiones a la vez, en "
                      "el orden en que se declara. Es la progresion con que "
                      "C-01 dimensiona en la corrida del entregable de la "
                      "Familia C y la que la guia de perfil y la suite "
                      "declaraban en caliente, de modo que darle valor de "
                      "archivo no mueve ninguna seccion, y es la decision "
                      "del dueño del proyecto: [A] con su ventana, no "
                      "provisional. No es la que propone la "
                      "cadena T (anchos de 1.00 a 4.00 m con paso de 0.50 m "
                      "por alturas de 1.00 a 3.00 m con paso de 0.25 m): esa "
                      "no contiene el 1.20 x 0.90 y con ella C-01 no "
                      "dimensiona -- V7 (flotacion) incumple en los siete "
                      "primeros escalones y el octavo, 1.00 x 2.00 m, deja la "
                      "clave por encima de la subrasante y detiene el "
                      "material --; queda como alternativa declarable y "
                      "barrible. La causa de que V7 incumpla no es que el "
                      "marco no quepa: es que `M5.v7_flotacion` lleva DC = 0 "
                      "-- no pesa el concreto del marco, del lado seguro --, "
                      "y con un canto mayor el empuje crece mas que el "
                      "relleno que queda encima. Medido sobre C-01: el marco "
                      "de 1.00 x 1.00 m incumple con 18.21 kN/m de suelo "
                      "contra 19.23 kN/m de empuje, y su concreto, 0.96 m2 a "
                      "unos 23.5 kN/m3, pesaria por si solo unos 22.6 kN/m, "
                      "mas que el empuje. Con el peso propio, la progresion "
                      "de la cadena probablemente daria a C-01 un marco de "
                      "1.00 x 1.00 m: moveria una seccion dimensionada, y eso "
                      "lo decide el dueño (ficha T3-08, sobre "
                      "`M5.v7_flotacion`). Por la misma causa, de esta "
                      "progresion solo el primer escalon es alcanzable bajo "
                      "la rasante de C-01: el de 1.50 x 1.20 m incumple V7 "
                      "con 18.9 contra 29.8 kN/m. Ampliarla -- alturas de "
                      "0.60 y 0.75 m, mas anchos -- queda diferido a cuando "
                      "exista la seccion real del canal de ANA o de la Junta "
                      "de Usuarios (ficha T3-01). Con tres escalones la "
                      "serie se agota en 2.00 x 1.50 m: un canal mas grande "
                      "se detiene con la progresion agotada y hay que "
                      "declarar la suya. La "
                      "sensibilidad describe las dos cotas de la eleccion: "
                      "por abajo, la minima dimension interior que permita "
                      "entrar a limpiar el conducto -- el numeral la exige y "
                      "no la cifra, y bajarla convierte la obra en no "
                      "mantenible sin que ningun numero lo senale --; por "
                      "arriba no manda la hidraulica sino la geometria del "
                      "cruce -- recubrimiento sobre la clave y cota de "
                      "subrasante --, que es lo que verifican V4 y la Fase 7",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.4 a) 'Tipo y seccion', pag. "
               "impresa 72 -- la excepcion de los cruces de canal --, y num. "
               "4.1.1.3.7 d) 'Mantenimiento y limpieza', pag. impresa 80 "
               "(PDF 83) -- la exigencia de "
               "mantenimiento que pone la cota inferior sin darle numero --. "
               "Los dos literales estan en el registro normativo "
               "(`MC_HHD.4.1.1.3.4a` y `MC_HHD.4.1.1.3.7d`) y se citan desde "
               "los `Fundamento` F3.SECCION_CANAL y F3.MANTENIMIENTO",
        reemplazado_por="La seccion que el proyectista adopte para el cruce, "
                        "con el ancho de solera y el tirante de diseno del "
                        "canal (ANA / Junta de Usuarios del Bajo Piura) y con "
                        "la dimension interior que permita mantenerlo",
        sensibilidad=(
            "cota inferior: la MINIMA dimension interior que permita entrar a "
            "limpiar el conducto (num. 4.1.1.3.7 d). El numeral la exige y no "
            "la cifra; bajarla convierte la obra en no mantenible y el "
            "requisito se incumple sin que ningun numero lo señale",
            "cota superior: la seccion que el canal y la rasante admitan. Por "
            "arriba no manda la hidraulica sino la geometria del cruce -- "
            "recubrimiento sobre la clave y cota de subrasante --, que es lo "
            "que verifican V4 y la Fase 7",
            "alternativa de la cadena T (no se activa: decision del dueño "
            "del 2026-11-12): anchos 1.00 a 4.00 m con paso 0.50 por alturas "
            "1.00 a 3.00 m con paso 0.25, por area creciente. Medida sobre "
            "C-01: no dimensiona -- V7, que lleva DC = 0 (no pesa el marco), "
            "incumple con H >= 1.00 m bajo la rasante del fixture; con el "
            "peso propio daria probablemente 1.00 x 1.00 m, ficha T3-08 --",
        ),
        # --- T-3 --- `vacio_verificado` YA SE PUEDE PONER, y se pone: el
        # criterio tiene valor de archivo y cubre el vacio que el comentario
        # de C5 dejo escrito -- el num. 4.1.1.3.7 d) exige dimensiones que
        # permitan el mantenimiento y la limpieza interior y NO da ninguna
        # cifra, y el 4.1.1.3.4 a) remite el cruce de canal a «cada diseño
        # particular» --. El ancla es la lectura de §15.3.1 de la ruta de la
        # Familia C. Con el, el criterio sale por `bloque_acotaciones` (R-23).
        vacio_verificado="ruta_familia_c.md Sec. 15.3.1",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el ancho y el tirante de diseno "
                        "del canal que se cruza y con la dimension interior "
                        "que el num. 4.1.1.3.7 d) exige para poder mantener "
                        "el conducto",
            dominio="serie de pares (B, H) en metros, de menor a mayor, con "
                    "B y H interiores de UNA celda",
            tabla_pendiente="ninguna: el num. 4.1.1.3.4 a) remite "
                            "expresamente a 'cada diseno particular', de modo "
                            "que aqui NO hay tabla que transcribir. Esa "
                            "ausencia es la lectura correcta del numeral, no "
                            "una laguna del registro",
        ),
    ),

    "n_manning_cajon": Criterio(
        # --- T-3 (auditoria adversarial, H1) --- PASA A [C] CON LA FILA
        # PROPIA DEL MARCO. La FASE A de T-3 adopto la fila «afinado» de la
        # Tabla N 09, (0.011, 0.014), por analogia [N->]; la auditoria
        # encontro que la MISMA fuente de la que salen la carta (Tabla A.1) y
        # el ke (Tabla C.2) del marco tabula el cajon de concreto en su
        # propia fila -- HDS-5 Tabla B.1, «Concrete Boxes | Smooth |
        # 0.012-0.015 | FHWA 1961», pag. impresa B.6 (PDF 208) -- y que la
        # ficha no la nombraba. Es el mismo trato que T-4 dio al HDPE. La
        # fila «afinado» queda como alternativa barrible.
        valor="concrete_boxes",
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        # --- T11-10 (decidido por el dueño el 2026-11-13: «abrir la forma»)
        # --- LA UNION de la fila y el par, como `k_v`: la CLAVE de una fila
        # de tabla (el valor de archivo y la alternativa barrible) O el PAR
        # (n_min, n_max) de la especificacion del encofrado de un marco
        # vaciado in situ, que la tercera ventana de abajo promete y hasta
        # T11-10 la forma `str` rechazaba. El par lo acota el rango del num.
        # B.3 en la puerta (`_verificar_par_de_encofrado`) y en el consumidor
        # (`M2._fila_manning_de_cajon`). El valor de archivo NO cambia.
        forma=(FORMA_STR, FORMA_PAR_ORDENADO),
        concepto="Coeficiente de rugosidad de Manning del marco de concreto: "
                 "fila de la que se toma la doble n (n_min, n_max), o el par "
                 "de la especificacion del encofrado de un marco vaciado in "
                 "situ",
        justificacion="Decide de que fila sale la doble n del marco de "
                      "concreto, tomando siempre el rango completo (minimo, "
                      "maximo): la regla de doble n pide los dos extremos -- "
                      "n_max para capacidad y tirante, n_min para velocidad "
                      "maxima y socavacion -- y un valor puntual dejaria una "
                      "de las dos verificaciones sin lado seguro. La Tabla N "
                      "09 del Manual (num. 4.1.1.3.6) cubre al marco por el "
                      "titulo de su grupo A -- conducto cerrado con "
                      "escurrimiento parcialmente lleno -- y NO tiene fila de "
                      "seccion rectangular (verificado contra el PDF): el "
                      "vacio es de fila. La fuente tecnica de la que el "
                      "proyecto toma la carta de control de entrada y el ke "
                      "del marco, el HDS-5 de la FHWA, si tabula el cajon de "
                      "concreto en su propia fila: Tabla B.1, «Concrete Boxes "
                      "/ Smooth», 0.012 a 0.015 (pag. impresa B.6). Se adopta "
                      "esa fila, y por eso la etiqueta es "
                      "[C]: cubre el vacio de la Tabla N 09 con una fuente "
                      "reconocida, la misma de la carta y del ke, como T-4 "
                      "hizo con el HDPE. Dos acotaciones de la propia fuente, "
                      "que la ventana recoge: sus n son de laboratorio (nota "
                      "1 de la tabla), y en un cajon vaciado in situ el n va "
                      "de 0.012 a 0.022 segun la calidad del encofrado, las "
                      "practicas constructivas y el envejecimiento (num. B.3, "
                      "pag. impresa B.2, cita HDS5_3ED.B.3#CAJON_IN_SITU). "
                      "Esa es la ventana hacia arriba del n de capacidad. La "
                      "direccion de cada extremo, dicha: un n mas alto es el "
                      "lado seguro para el tirante, V1 y el HW del control de "
                      "salida, y un n mas bajo es el lado seguro para V3 y el "
                      "d50 de la proteccion; la regla de doble n toma cada "
                      "extremo para su verificacion, de modo que ensanchar el "
                      "rango es conservador en las dos ramas a la vez. Frente "
                      "a la alternativa de la Tabla N 09 (fila «afinado», "
                      "0.011-0.014), esta fila sube el n de capacidad (0.015 "
                      "> 0.014) y el de erosion (0.012 > 0.011): mas "
                      "conservadora para tirante y HW, menos para V3 y el "
                      "d50. Sobre C-01 no mueve la seccion (1.20 x 0.90 m) "
                      "ni el HW de control de entrada, que no depende de n; "
                      "mueve el tirante normal y el HW de control de salida",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), Apendice B, Table B.1 "
               "'Manning's n Values for Culverts', pag. impresa B.6 (PDF "
               "208): fila 'Concrete Boxes / Smooth', 0.012-0.015, referencia "
               "FHWA 1961. Tabla HDS5_3ED.TB.1 del registro, fila "
               "HDS5_3ED.TB.1#concrete_boxes, leida por "
               "constantes_normativas.MANNING_CAJON_HDS5. Y el num. B.3 "
               "'CONCRETE BOX CULVERT', pag. impresa B.2 (PDF 204): el n del "
               "cajon vaciado in situ va de 0.012 a 0.022 segun el encofrado "
               "(cita HDS5_3ED.B.3#CAJON_IN_SITU). LO QUE NO LO DA: la Tabla "
               "N 09 del Manual de Hidrologia (num. 4.1.1.3.6, pags. impresas "
               "75-76) no tiene fila de seccion rectangular, verificado contra "
               "el PDF en la fase CN. La alternativa barrible, su fila "
               "«afinado», se lee con el corrimiento de una fila que la "
               "pagina trae en los bloques A.2, B.1, B.2 y C: errata de "
               "imprenta DIS-MCHHD-T09-A2-DESPLAZADA del registro normativo, "
               "sostenida en la evidencia interna de la pagina. Leida al pie "
               "de la letra la fila «afinado» daria 0.013/0.015/0.017",
        reemplazado_por="Ficha tecnica del acabado interior y del encofrado "
                        "que se especifiquen para el marco vaciado in situ",
        sensibilidad=(
            "'concrete_boxes' -- Tabla B.1 del HDS-5, «Concrete Boxes / "
            "Smooth» (0.012 - 0.015) --: el valor de archivo, [C]. La fila "
            "especifica del cajon de concreto, de la misma fuente que la "
            "carta y el ke del marco",
            "'concreto_afinado' -- Tabla N 09, «A.2 NO METALICOS - a. "
            "Concreto - afinado» (0.011 - 0.014), lectura CORREGIDA del "
            "corrimiento de una fila (DIS-MCHHD-T09-A2-DESPLAZADA) --: "
            "ALTERNATIVA BARRIBLE, por analogia [N->] dentro del grupo A, que "
            "cubre al marco por su titulo. Es la que adopto la FASE A de T-3. "
            "Frente a la de archivo baja el n de capacidad (lado inseguro "
            "para tirante y HW) y el de erosion (lado seguro para V3 y el "
            "d50). Leida al pie de la letra, sin corregir la errata, daria "
            "0.013 - 0.017, mas conservadora para capacidad",
            "num. B.3 del HDS-5 (cita HDS5_3ED.B.3#CAJON_IN_SITU): 0.012 a "
            "0.022 en un cajon VACIADO IN SITU, segun el encofrado -- remite "
            "a la Tabla 1 del HDS 3, que no esta en normas/ --. Es la ventana "
            "HACIA ARRIBA del n de capacidad: con un encofrado de calidad "
            "inferior a la de laboratorio, un n_max mayor es el lado seguro "
            "para el tirante y el HW. Se declara como el par de la "
            "especificacion del encofrado, no como una fila",
        ),
        # `vacio_verificado` con el texto que C5 dejo escrito para quien le
        # diera valor: la Tabla N 09 del num. 4.1.1.3.6 cubre al marco por el
        # TITULO de su grupo A y NINGUNA de sus filas nombra la seccion
        # rectangular (verificado contra el PDF en la fase CN). El ancla es
        # §15.3.2 de la ruta de la Familia C, que lo documenta fila por fila.
        # Desde la auditoria de T-3 lo cubre la fila de la Tabla B.1 [C].
        vacio_verificado="ruta_familia_c.md Sec. 15.3.2",
        resolucion=DeTabla(
            # LA PRIMERA TABLA ES LA DEL VALOR DE ARCHIVO (la que la ventana
            # y los editores de la GUI muestran); la segunda, la de la
            # alternativa por analogia. Con dos tablas la resolucion no fija
            # `fila_id` (la guardia de `verificar_resolucion` lo prohibe: no
            # se sabria de cual): el valor es la CLAVE de la fila, como en
            # 'embocadura_cajon', y `M2._fila_manning_de_cajon` la acota.
            # Declarar la fila de la segunda tabla desde un editor exige
            # decir de cual se elige; el barrido la acepta con su
            # `--barrido-nota`, y la CLI con `--declarar`.
            tablas=("HDS5_3ED.TB.1", "MC_HHD.T09"),
            que_elige="la fila cuyo par (minimo, maximo) es la doble n del "
                      "marco: la del cajon de concreto de la Tabla B.1 del "
                      "HDS-5 ([C]) o, por analogia, una del subgrupo «a. "
                      "Concreto» de la Tabla N 09. Fuera de las tablas, el "
                      "par (n_min, n_max) de la especificacion del encofrado "
                      "de un marco vaciado in situ, dentro del rango del num. "
                      "B.3 del HDS-5, con la nota que dice de donde sale",
            laguna="la Tabla N 09 no trae fila de cajon. El vacio es de FILA "
                   "y no de grupo: el rotulo del grupo A -- conducto cerrado "
                   "con escurrimiento parcialmente lleno -- ya cubre al marco",
        ),
    ),

    "embocadura_cajon": Criterio(
        # --- T-3 --- Carta 8, escala 1: aletas de 30 a 75 grados (Forma 1).
        # La de cabezal recto se midio y da OTRA carga (ver la justificacion).
        valor="cajon_concreto_aletas_30_75",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_STR,
        concepto="Detalle de embocadura del marco: carta y escala de la Tabla "
                 "A.1 de HDS-5 que le corresponde (aletas, chaflan, bisel, "
                 "esviaje)",
        justificacion="Decide la carta y escala de la Tabla A.1 de HDS-5 que "
                      "corresponde a la embocadura del marco, y con ella las "
                      "constantes K, M, c e Y del control de entrada y la "
                      "forma de ecuacion (1 o 2) con que se aplican: la "
                      "embocadura no es un detalle de acabado. La fuente "
                      "(Tabla A.1; los bloques de cajon estan transcritos en "
                      "normativa/tablas.py::T_HDS5_A1 y los lee "
                      "constantes_normativas.HDS5_INLET) trae, en la "
                      "transcripcion de este repositorio, dieciocho filas de "
                      "cajon -- Cartas 8 a 13 --: tres de Forma 1 (Carta 8) y "
                      "quince de Forma 2 (Cartas 9 a 13; medido: Carta 9 con "
                      "2 filas, la 10 con 3, la 11 con 4, la 12 con 3 y la 13 "
                      "con 3), y las "
                      "dos ecuaciones no se parecen -- la Forma 1 arranca de "
                      "H_c/D y corrige por pendiente, la Forma 2 no lleva "
                      "ninguno de los dos terminos. Ese censo es de la "
                      "transcripcion y no de la tabla: la Tabla A.1 trae mas "
                      "cajon del que este proyecto alcanza, y lo que queda "
                      "fuera esta censado fila por fila en el `Acotada` de "
                      "`normativa/tablas.py::T_HDS5_A1` -- las cinco de las "
                      "Cartas 57 a 59, que son gargantas de tapered inlet --; "
                      "quien declare una embocadura que caiga en esas cinco "
                      "tiene que transcribirlas primero. El esviaje no es un "
                      "bloque de la tabla: es un valor de la columna de "
                      "configuracion de entrada dentro de la Carta 11. Lo que "
                      "la tabla no resuelve: cual fila le toca a esta obra. "
                      "Eso lo decide el detalle que el proyectista dibuje, "
                      "que es la separacion que CLAUDE.md fija entre la tabla "
                      "([N], sus constantes) y la eleccion ([A], este "
                      "criterio). Se adopta que la eleccion se declare junto "
                      "con dos cosas mas, porque se mueven a la vez: el "
                      "detalle del cabezal de la Sec. 9.1 -- donde el "
                      "proyecto dibuja la embocadura, y cambiar el detalle "
                      "obliga a cambiar la carta, igual que en la circular -- "
                      "y 'ke_entrada_cajon', que sale de la fila de la Tabla "
                      "C.2 de esa misma embocadura; declarar una sin la otra "
                      "deja el control de entrada y el de salida hablando de "
                      "dos embocaduras distintas. La sensibilidad separa las "
                      "dos familias -- Carta 8 (Forma 1) frente a Cartas 9 a "
                      "13 (Forma 2) -- porque entre una y otra no cambia solo "
                      "una constante: cambia la ecuacion. Se adopta la "
                      "Carta 8, escala 1, aletas de 30 a 75 grados (K "
                      "0.026, M 1.0, c 0.0347, Y 0.81, Forma 1; Tabla A.1, "
                      "PDF 197), emparejada en 'ke_entrada_cajon' con la "
                      "fila de la Tabla C.2 de esa misma embocadura, borde "
                      "recto en la clave bajo aletas de 30 a 75 grados (ke "
                      "0.4): es la embocadura con aletas -- la transicion "
                      "que un canal trapecial necesita para entrar a un "
                      "marco -- y la que la guia de perfil, la suite y la "
                      "corrida del entregable de la Familia C declaraban, "
                      "de modo que no mueve ninguna carga. La de cabezal "
                      "recto se midio y no se adopta: la cadena T la "
                      "sugeria por ahora (Carta 8, escala 2, aletas de 90 y "
                      "15 grados, con la fila de cabezal paralelo al "
                      "terraplen sin aletas y borde recto en tres lados de "
                      "la Tabla C.2, ke 0.5) y sobre C-01 da HW = 0.629 m "
                      "contra 0.589 m con aletas; se deja la de hoy, y la "
                      "coherencia entre la carta, el ke y la geometria de "
                      "los aleros la cierra el dimensionamiento del cabezal "
                      "por punto. La Lamina N 03 no decide entre las dos: "
                      "es un corte longitudinal y no muestra el angulo de "
                      "las aletas (`SIN_COTAS_LAMINA_03`)",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice A, Tabla A.1, "
               "bloque 'Rect. Box Concrete' (Cartas 8 a 11) y el que lo "
               "sigue, 'Rect. Box 3/4\" chamf. Conc.' (Carta 12), PDF 197. "
               "EL ESVIAJE NO ES UN BLOQUE, y la redaccion anterior lo "
               "contaba como tal --decia «y los tres que lo siguen (chaflan, "
               "bisel y esviaje)»--: es un valor de la columna 'Inlet "
               "Configuration' DENTRO de la Carta 11, bajo 'Rect. Box "
               "Concrete'. Y el del bisel superior es la Carta 13, 'Rect. "
               "Box Top Bev. Conc.', transcrita en T-2 (tres filas, aletas "
               "desplazadas de 45, 33.7 y 18.4 grados). Transcrita en "
               "normativa/tablas.py::T_HDS5_A1 y leida por "
               "constantes_normativas.HDS5_INLET, donde las dieciocho filas "
               "de cajon transcritas estan como claves 'cajon_concreto_*'",
        reemplazado_por="El detalle de embocadura del cabezal que fije el "
                        "expediente (Sec. 9.1), del que salen la carta y la "
                        "fila de ke a la vez",
        sensibilidad=(
            "Carta 8 (Forma 1), aletas de 30 a 75 grados: K = 0.026, M = "
            "1.00. Es la unica familia de cajon que usa la ecuacion (A.1), la "
            "que arranca de H_c/D. La adoptada (T-3); sobre C-01, HW = 0.589 m",
            "Carta 8 (Forma 1), escala 2, «90° and 15° wingwall flares» -- el "
            "cabezal recto que la cadena T sugeria --: K = 0.061, M = 0.75. "
            "Sobre C-01, HW = 0.629 m (+0.040 m); su ke es el de «Headwall "
            "parallel to embankment (no wingwalls)», 0.5",
            "Cartas 9 a 13 (Forma 2) -- aletas, chaflan, bisel o esviaje; la "
            "12 es la familia 'Rect. Box 3/4\" chamf. Conc.' y la 13 la del "
            "bisel superior con aletas desplazadas --: K entre 0.486 "
            "y 0.545 con M = 0.667. La ecuacion (A.2) no lleva H_c/D ni Ks*S, "
            "de modo que entre una carta de Forma 1 y una de Forma 2 no "
            "cambia solo una constante: cambia la ecuacion",
        ),
        resolucion=DeTabla(
            tablas=("HDS5_3ED.TA1", "HDS5_3ED.TC2"),
            que_elige="la carta y escala de la Tabla A.1 de la que salen K, "
                      "M, c, Y y la forma de ecuacion; y, emparejada con "
                      "ella, la fila de la Tabla C.2 de la que sale ke",
            # SIN `elegido_por`, y a proposito: ese campo tiene que nombrar
            # un CRITERIO declarado --`verificar_resolucion` lo comprueba-- y
            # aqui no hay ninguno detras. Quien elige la fila es el detalle de
            # embocadura del cabezal (Sec. 9.1), que es un DIBUJO del
            # expediente y no un criterio. El acoplamiento en el otro sentido
            # si es de criterio a criterio, y esta escrito donde corresponde:
            # `ke_entrada_cajon` lleva `elegido_por="embocadura_cajon"`.
        ),
    ),

    "n_celdas_cajon": Criterio(
        # --- T-3 --- Una celda: lo que el numeral recomienda ante arrastre.
        valor=1,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_INT,
        concepto="Numero de celdas del marco: una sola o multicelda",
        justificacion="Decide el numero de celdas del marco: una sola o "
                      "multicelda. La fuente (num. 4.1.1.3.4 a) del Manual de "
                      "Hidrologia; cita MC_HHD.4.1.1.3.4a#MULTIPLES del "
                      "registro, traida a la memoria por el Fundamento "
                      "F3.CELDAS con verbo RECOMIENDA) toma partido: ante "
                      "capacidad de arrastre del curso -- palizada, troncos, "
                      "material de cauce -- recomienda obras de mayor seccion "
                      "transversal libre, sin subdivisiones, porque cada "
                      "tabique es un punto donde la palizada se traba. Lo que "
                      "no resuelve: no prohibe la multicelda -- invierte la "
                      "carga de la prueba, y quien la adopte tiene que decir "
                      "por que -- ni fija N para una obra concreta. Se adopta "
                      "N = 1, la seccion unica que el numeral recomienda, y "
                      "la que la guia de perfil y la suite declaraban; la "
                      "multicelda queda declarable y V6 la sigue rechazando "
                      "mientras no haya dato de arrastre del cauce (ver "
                      "docs/decisiones_diferidas.md): con N > 1 V6 publica "
                      "el reparto Q/N, el tabique entre celdas y el ancho "
                      "total, y dice por que no la acepta. En el "
                      "calculo, N no entra en la geometria: los coeficientes "
                      "de HDS-5, el radio hidraulico y el control de entrada "
                      "son por barril, de modo que con N celdas se dimensiona "
                      "una con Q/N y se declara N -- es la razon por la que "
                      "`modelos.SeccionRectangular` modela una celda y no el "
                      "conjunto. En V6 (material solido de arrastre), la "
                      "verificacion pasa a depender de una decision escrita "
                      "en vez de cumplirse trivialmente por una propiedad del "
                      "programa -- MD no sabe hacer multibarril, y el dia que "
                      "supiera, una V6 sin este criterio se habria vuelto "
                      "falsa en silencio. La sensibilidad describe los dos "
                      "extremos: N = 1, lo que el numeral recomienda ante "
                      "arrastre -- V6 se cumple sin tabiques que trabar y el "
                      "ancho necesario lo da una sola celda --, y N > 1, "
                      "admisible y no recomendado por defecto -- baja el "
                      "canto necesario cuando la rasante no da altura, a "
                      "cambio de meter tabiques en el paso del arrastre y de "
                      "dimensionar cada celda con Q/N",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.4 a) 'Tipo y seccion', pag. "
               "impresa 72. RECOMENDACION, no exigencia. "
               "EL LITERAL NO SE REPITE AQUI, y este campo lo repetia: "
               "traia a mano un FRAGMENTO de la oracion del numeral, sin "
               "acentos y por tanto ya divergente de su `Verbatim`, y "
               "ademas recortado -- que es la elision sin marcar que "
               "`MC_HHD.4.1.1.3.4a#MULTIPLES` documenta y rechaza en su "
               "propio comentario, y que CLAUDE.md nombra --. El texto vive "
               "en el registro, en esa "
               "cita, con la ORACION ENTERA, y lo trae a la memoria el "
               "`Fundamento` F3.CELDAS con verbo RECOMIENDA",
        reemplazado_por="La decision de tipologia del cruce, con el ancho "
                        "disponible en la rasante y la capacidad de arrastre "
                        "observada en el canal",
        sensibilidad=(
            "N = 1 (celda unica): lo que el numeral recomienda ante arrastre "
            "de solidos. V6 se cumple sin tabiques que trabar, y el ancho "
            "necesario lo da una sola celda",
            "N > 1 (multicelda): admisible y no recomendado por defecto. "
            "Baja el canto necesario cuando la rasante no da altura, y a "
            "cambio mete tabiques en el paso del arrastre; ademas obliga a "
            "dimensionar cada celda con Q/N",
        ),
        resolucion=Libre(
            que_lo_fija="el proyectista, con la capacidad de arrastre del "
                        "curso y el ancho disponible bajo la rasante. El "
                        "numeral recomienda una sola celda y no lo impone",
            dominio="entero >= 1",
        ),
    ),

    "ke_entrada_cajon": Criterio(
        # --- T-3 --- La fila de la MISMA embocadura que 'embocadura_cajon'.
        valor="cajon_aletas_30_75_escuadra",
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_STR,
        concepto="Coeficiente de perdida de carga en la embocadura (ke) del "
                 "marco de concreto",
        justificacion="Decide de que fila del bloque de cajon de la Tabla C.2 "
                      "sale el coeficiente de perdida de entrada ke del "
                      "marco, y lo que se declara es la clave de la fila, no "
                      "el coeficiente. La fuente (Tabla C.2 de HDS-5, bloque "
                      "'Box, Reinforced Concrete', transcrita en "
                      "normativa/tablas.py::T_HDS5_C2) trae siete filas con "
                      "coeficiente bajo cuatro rotulos de agrupacion, con ke "
                      "entre 0.2 y 0.7; tres de esas filas se imprimen con el "
                      "mismo texto -- 'Square-edged at crown', con ke 0.4, "
                      "0.5 y 0.7 -- y sin su rotulo de agrupacion son "
                      "indistinguibles: la fila suelta pierde la condicion, y "
                      "por eso la memoria tiene que imprimir las dos cosas. "
                      "Lo que no se resuelve copiando el tubo: el ke del tubo "
                      "no sirve para el marco aunque el numero coincida -- "
                      "para la embocadura a ras sin aletas que la Sec. 9.1 "
                      "adopta hoy, la fila del cajon vale 0.5 tambien --, y "
                      "un valor que acierta por casualidad deja una cita "
                      "falsa que no falla nunca de forma ruidosa, de modo que "
                      "nadie la comprueba; y deja de coincidir en cuanto haya "
                      "aletas, que es lo que la Lamina N 03 dibuja: 0.4 con "
                      "aletas a 30-75 grados, 0.5 a 10-25 grados y 0.7 con "
                      "aletas paralelas -- con 0.5 -> 0.7 y V = 3 m/s son "
                      "0.2*V^2/2g = 0.092 m de carga que el calculo no veria, "
                      "contra V4 y contra el tamizado de la Fase 7. Se adopta "
                      "abrirlo sin valor: el ke del marco sale de la fila que "
                      "'embocadura_cajon' declare, y las dos decisiones se "
                      "mueven juntas; escribir aqui un 0.5 repetiria, con "
                      "otra etiqueta, el defecto de la cita que acierta por "
                      "casualidad. Se declara la clave y no el numero porque "
                      "en el bloque del cajon el 0.2 esta en tres filas y el "
                      "0.5 en dos: un numero declarado no permite decir de "
                      "donde salio, y la memoria imprimiria el coeficiente "
                      "perdiendo la condicion que lo justifica, que es "
                      "exactamente el defecto que este criterio existe para "
                      "impedir. Las claves admitidas son las de "
                      "`constantes_normativas.KE_HDS5_C2`, derivadas de la "
                      "transcripcion y no copiadas de ella. El criterio "
                      "hermano 'ke_entrada' (tubo) sigue declarando un "
                      "numero: tiene valor y consumidor, y cambiarle la forma "
                      "por simetria seria mover un dato de proyecto que nadie "
                      "pidio mover; la asimetria esta escrita en KE_HDS5_C2. "
                      "La sensibilidad da los dos extremos del bloque -- ke = "
                      "0.2, solo alcanzable construyendo el detalle de borde "
                      "redondeado, biselado o abocinado, y ke = 0.7, borde "
                      "recto bajo aletas paralelas --: entre los dos hay "
                      "0.5*V^2/2g de carga, 0.229 m con V = 3 m/s, que se "
                      "descuenta de V4 y del tamizado de la Fase 7. Se "
                      "adopta la fila de borde recto en la clave bajo "
                      "aletas de 30 a 75 grados, ke 0.4: la de la misma "
                      "embocadura que 'embocadura_cajon' declara (Carta 8, "
                      "escala 1). Las dos se mueven juntas, y el "
                      "dimensionamiento de los aleros por punto las vuelve a "
                      "mirar",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice C, Tabla C.2 "
               "'Entrance Loss Coefficients', pag. impresa C.6 (PDF 216), "
               "bloque 'Box, Reinforced Concrete': siete filas con "
               "coeficiente repartidas bajo cuatro rotulos de agrupacion -- "
               "'Headwall parallel to embankment (no wingwalls)', 'Wingwalls "
               "at 30 to 75 degrees to barrel', 'Wingwall at 10 to 25 degrees "
               "to barrel' y 'Wingwalls parallel (extension of sides)' --, "
               "con ke entre 0.2 y 0.7. Transcritas en "
               "normativa/tablas.py::T_HDS5_C2",
        reemplazado_por="La fila de la Tabla C.2 que corresponda a la "
                        "embocadura que declare 'embocadura_cajon'",
        # LA SENSIBILIDAD ES SIMBOLICA Y NO UN PAR DE NUMEROS, y el motivo es
        # el mismo que hace que este criterio declare una clave: lo que se
        # elige es una FILA, no un punto de un intervalo. Un rango (0.2, 0.7)
        # aqui seria ademas rechazado por `_verificar_sensibilidad` -- un
        # rango numerico no puede defender un valor que no es numero --, y esa
        # guardia tiene razon: el recorrido del coeficiente es la CONSECUENCIA
        # de la eleccion, no su dominio.
        sensibilidad=(
            "extremo bajo: ke = 0.2, en las tres filas de borde redondeado, "
            "biselado o de entrada abocinada del bloque. Es el minimo del "
            "bloque y solo se alcanza construyendo ese detalle: declararlo "
            "sin dibujarlo en la Lamina de embocadura es cobrar una perdida "
            "que la obra no tendra",
            "extremo alto: ke = 0.7, fila «Square-edged at crown» bajo "
            "«Wingwalls parallel (extension of sides)». Entre los dos "
            "extremos hay 0.5*V^2/2g de carga -- 0.229 m con V = 3 m/s --, "
            "que se descuenta de V4 y del tamizado de la Fase 7",
        ),
        resolucion=DeTabla(
            tablas=("HDS5_3ED.TC2",),
            que_elige="la fila del bloque 'Box, Reinforced Concrete' de la "
                      "que sale ke. Lo que se declara es la CLAVE de la fila "
                      "y no el coeficiente: el valor lo fija la fila JUNTO "
                      "CON su rotulo de agrupacion, porque tres filas del "
                      "bloque se imprimen con el mismo texto y distinto "
                      "coeficiente. Claves en "
                      "`constantes_normativas.KE_HDS5_C2`",
            elegido_por="embocadura_cajon",
        ),
    ),

    # EL SEXTO DEL CAJON, y el que abre C7. Los cinco de C5 gobiernan la
    # HIDRAULICA del marco; este gobierna su GEOMETRIA EXTERIOR, que es lo que
    # V7 y la cota de clave necesitan y no tenian por donde entrar.
    "espesor_pared_cajon": Criterio(
        # --- T-3 --- 0.20 m: el piso de la E.060 num. 14.5.3.2 para muros
        # exteriores enterrados, POR ANALOGIA. Ver la justificacion.
        valor=0.20,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Espesor de pared del marco de concreto vaciado in situ, m",
        justificacion="Decide el espesor de pared del marco de concreto "
                      "vaciado in situ a nivel de perfil. El vacio es del "
                      "catalogo de productos, no "
                      "del Manual: el Manual de Hidrologia no tabula "
                      "espesores de pared de nada -- no hay numeral que "
                      "callar --, y quien los tabula son las normas de "
                      "producto; la que este proyecto usa, AASHTO M 170M-04 "
                      "(columna de espesor de pared), es de tuberia: sus "
                      "filas se enumeran por diametro designado y un marco no "
                      "es una de ellas. Es el cuarto caso de la regla 3 de la "
                      "§15.1 de docs/ruta_familia_c.md, ya clasificado ahi: "
                      "las normas de producto quedan fuera de su alcance "
                      "declarado para el marco, no en analogia. Tampoco es un "
                      "vacio que una tabla vaya a llenar: la §14.1 adopto el "
                      "vaciado in situ precisamente porque en normas/ no hay "
                      "norma de producto de cajon prefabricado. Lo que si "
                      "existe y este alcance difiere es el procedimiento de "
                      "calculo (AASHTO LRFD Sec. 5 y Art. 12.11), de modo que "
                      "a nivel de perfil el espesor es una adopcion del "
                      "proyectista y por eso [A]. Hasta T-3 se adoptaba "
                      "bloquear en vez de tomar un valor plausible, y la "
                      "razon estaba medida: "
                      "las alturas de marco plausibles caen sobre la misma "
                      "serie de 900 + 150k mm que los diametros de tubo, de "
                      "modo que un marco de 2.00 x 1.50 m que leyera la tabla "
                      "del tubo no se detendria -- recibiria la pared del "
                      "tubo de 1500 mm y V7 lo evaluaria como un cilindro, "
                      "sobreestimando la seguridad en torno a un 27 % --, y "
                      "un valor que acierta de forma silenciosa es peor que "
                      "un bloqueo, porque el bloqueo se ve. La sensibilidad "
                      "de la ficha explica el signo, que es contraintuitivo "
                      "-- engrosar la pared empeora la flotacion --, y por "
                      "que hacia abajo el limite no es la flotacion sino el "
                      "calculo estructural diferido: la ventana no se puede "
                      "cerrar a nivel de perfil y el criterio se adopta en "
                      "vez de optimizarse. Se adopta 0.20 m, el espesor "
                      "minimo que la E.060 fija a los muros exteriores de "
                      "sotanos y cimentaciones (num. 14.5.3.2, pag. 134, "
                      "cita E060.14.5.3.2): es la fuente mas cercana porque "
                      "su objeto es un muro exterior enterrado con suelo "
                      "contra una cara, que es lo que es la pared del "
                      "marco; no es [N] para el marco, porque el 14.5.3 "
                      "rige los muros del metodo empirico de 14.5 y la "
                      "pared del cajon se diseña por flexion (14.8.1 remite "
                      "al Capitulo 10), y la ventana existe. 0.20 m es el "
                      "extremo favorable a V7 de esa ventana: con DC = 0 en "
                      "V7 un espesor mayor ensancha el empuje mas que el "
                      "suelo que lo equilibra, y sobre C-01 el marco "
                      "dimensiona con 0.20 y 0.25 m y deja de hacerlo con "
                      "0.26 y 0.30 m (ficha T3-08). Es ademas el "
                      "espesor que la guia de perfil y la suite declaraban, "
                      "de modo que no mueve ni la clave ni V7. Vale para "
                      "paredes, losa superior, losa de fondo y, con N > 1, "
                      "el tabique: un solo espesor, adoptado, hasta que la "
                      "Fase 8 del expediente lo calcule",
        fuente="NINGUNA PARA EL MARCO, y esa es la afirmacion; el piso "
               "adoptado sale POR ANALOGIA de la E.060, num. 14.5.3.2 "
               "'Espesor minimo de muros diseñados por el metodo empirico de "
               "diseño', pag. impresa 134 (PDF 134), que fija 200 mm a los "
               "muros exteriores de sotanos y cimentaciones (cita "
               "E060.14.5.3.2, leida en T-3). Barrido declarado: el num. "
               "4.1.1.3.4 a) del Manual de Hidrologia nombra el marco y "
               "remite su seccion a «cada diseno particular» sin dar "
               "espesores; AASHTO M 170M-04 tabula 'Wall Thickness' por "
               "diametro designado de TUBERIA (Tablas 1 a 5) y su Nota 1 la "
               "declara especificacion de fabricacion y compra; y en normas/ "
               "no hay norma de producto de cajon prefabricado -- que es la "
               "razon por la que §14.1 adopto el vaciado in situ --. Lo que "
               "SI existe y este alcance difiere es el procedimiento de "
               "calculo: AASHTO LRFD Sec. 5 y Art. 12.11 «Reinforced Concrete "
               "Cast-in-Place and Precast Box Culverts», pag. impresa 12-68",
        reemplazado_por="El calculo estructural del portico (AASHTO LRFD "
                        "Sec. 5 y 12.11), que es lo que fija el espesor de un "
                        "marco vaciado in situ. A nivel de EXPEDIENTE deja de "
                        "ser una adopcion y pasa a ser un resultado; a nivel "
                        "de perfil se adopta y se declara",
        sensibilidad=(
            "EL SIGNO, Y QUE SE INVIRTIO EN VE-3.11: desde entonces V7 "
            "suma el peso propio del concreto (H4 de los ensayos de diseño "
            "del conducto), y ENGROSAR LA PARED MEJORA LA FLOTACION: el "
            "anillo que se agrega pesa gamma_c = 23.56 kN/m3 y desplaza "
            "agua de 9.81, de modo que por cada metro de t el lado "
            "estabilizante crece 0.90*gamma_c*2*(Bc + B'c) y el empuje solo "
            "gamma_w*2*(Bc + B'c). Medido sobre un marco de 2.00 x 1.50 m "
            "con 0.95 m de relleno y gamma_r = 18 kN/m3: t = 0.15 da margen "
            "+18.96 kN/m, t = 0.20 da +25.28 y t = 0.25 da +31.83. HASTA "
            "VE-3.11, con DC = 0, era al reves -- engrosar la pared EMPEORABA "
            "la flotacion: -5.22, -7.80 y -10.58 kN/m en el mismo marco --, "
            "y este texto lo advertia porque la intuicion decia lo contrario",
            "HACIA ABAJO el limite no es la flotacion sino el propio calculo "
            "estructural, que este alcance difiere: una pared que flota mejor "
            "puede no resistir el empuje de tierras ni la carga viva. Por eso "
            "la ventana no se puede cerrar a nivel de perfil y el criterio "
            "se ADOPTA en vez de optimizarse: el optimo de V7 y el minimo "
            "estructural empujan en sentidos opuestos y solo la Fase 8 tiene "
            "los dos numeros",
            "VENTANA DE LA ADOPCION (T-3): 0.20 m -- el piso de la E.060 num. "
            "14.5.3.2 para muros exteriores enterrados, por analogia, y el "
            "valor adoptado -- a 0.30 m, techo que elige el proyecto para "
            "el predimensionamiento de perfil y que NO sale de ninguna "
            "fuente. Por eso esta ventana es simbolica: un valor fuera de "
            "ella se puede declarar para medir una formula, y la memoria "
            "imprime el adoptado. El adoptado es el extremo favorable a V7: "
            "sobre C-01, con 0.26 m o mas V7 incumple (con 0.26 m, 23.42 kN/m "
            "de suelo contra 23.96 kN/m de empuje) y el marco no dimensiona "
            "-- porque V7 lleva DC = 0, ficha T3-08 --",
        ),
        resolucion=Libre(
            que_lo_fija="el proyectista, por predimensionamiento, hasta que "
                        "el calculo estructural del portico lo determine "
                        "(AASHTO LRFD Sec. 5 y 12.11, diferidos por "
                        "`--alcance perfil`)",
            dominio="metros, > 0",
            tabla_pendiente="ninguna, y es deliberado: no hay norma de "
                            "producto de cajon prefabricado en normas/, y "
                            "§14.1 adopto el vaciado in situ por esa razon. "
                            "La tabla que existe -- AASHTO M 170M-04 -- es de "
                            "tuberia y NO se le puede leer la fila de la "
                            "misma altura, aunque exista: es la coincidencia "
                            "de series que midio la auditoria de C5",
        ),
        # --- T-3 --- El vacio que cubre: no hay norma de producto de cajon
        # ni espesor tabulado para un marco vaciado in situ (§14.1 de la ruta
        # de la Familia C, que lo decidio por esa razon).
        vacio_verificado="ruta_familia_c.md Sec. 14.1",
    ),

    # --- T-4 --- PASA A SER OPCIONAL Y SIN VALOR (INF-3.3.1). Hasta T-4
    # valia {concreto 2.70, TMC 2.10, HDPE 1.50} m: tres topes [A] de los
    # que dos no tenian respaldo documental (la propia ficha lo decia en
    # `verificacion_pendiente`). El tope que rige por defecto es ahora el
    # de la SERIE de la norma de producto, 'D_max_norma_producto' [C], y
    # este criterio queda como lo que su nombre dice: la disponibilidad
    # de mercado, que el proyectista declara SI la conoce y que solo
    # puede BAJAR el tope de la serie (`M2.tope_de_diametro` rechaza con
    # DatoInvalidoError un valor por encima). Sin declarar no hay tope de
    # catalogo y no se imprime ninguno.
    #
    # NIVEL MEDIDO por la TERCERA corrida de `tests/test_nivel_medido.py`
    # (opcional=True se lee con `valor_si_declarado()`, que no registra el
    # uso mientras el criterio siga vacio): declarado en caliente con los
    # topes de la serie, la corrida de perfil lo invoca en M2 sin mover
    # ningun resultado.
    "D_max_catalogo": Criterio(
        valor=None,                 # OPCIONAL: sin valor, rige la serie de la norma
        opcional=True,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Diametro maximo que el mercado local entrega por material, "
                 "en metros: tope de disponibilidad (catalogo) que solo puede "
                 "bajar el tope de la serie de la norma de producto",
        de_catalogo="TOPE DE CATALOGO, NO DE NORMA. Imprimir siempre asi: "
                    "'diametro maximo adoptado por disponibilidad de mercado'. "
                    "Es un tope que el proyectista declara por debajo del de "
                    "la serie de la norma de producto ('D_max_norma_producto') "
                    "porque el mercado local no entrega el producto mas alla. "
                    "Superarlo NO significa 'material inexistente': significa "
                    "'fuera del catalogo declarado', y se levanta declarando "
                    "otro tope o retirando la declaracion",
        justificacion="Decide, cuando se declara, el diametro maximo que el "
                      "mercado local entrega de cada material. Es opcional y "
                      "no un vacio: sin declarar, el catalogo llega hasta el "
                      "mayor diametro de la serie que tabula la norma de "
                      "producto de cada material, y el calculo no se detiene. "
                      "Ninguna norma dice que diametros se consiguen en una "
                      "obra concreta: eso es disponibilidad del mercado, no "
                      "norma, y por eso la eleccion es del proyectista. La "
                      "declaracion solo puede bajar el tope de la serie, "
                      "nunca subirlo: un diametro que la norma de producto "
                      "no tabula no es un producto que un catalogo pueda "
                      "ofrecer bajo esa norma. El tope no entra en ninguna "
                      "formula de dimensionamiento; lo unico que cambia al "
                      "declararlo es cuantos puntos quedan sin solucion por "
                      "diametro en ese material, y ese descarte se imprime "
                      "como adoptado por disponibilidad y no como exigencia",
        fuente="NINGUNA NORMA fija la disponibilidad de mercado. El tope que "
               "rige cuando este criterio no se declara es el de la serie de "
               "la norma de producto de cada material, en "
               "'D_max_norma_producto': AASHTO M 170M-04 Tablas 1 a 5 "
               "(concreto, 300 a 3600 mm), AASHTO M 36-03 (2007) Table 6 "
               "(TMC, 100 a 3600 mm; cada corrugacion es estandar en una "
               "parte de la serie) y AASHTO M 294-11 num. 7.2.1 (HDPE, 300 a "
               "1500 mm, traduccion no oficial). HASTA T-4 este criterio "
               "valia 2.70 m (concreto), 2.10 m (TMC) y 1.50 m (HDPE) como "
               "adopcion sin respaldo documental en los dos primeros",
        sensibilidad=("sin declarar: rige el tope de la serie de la norma de "
                      "producto ('D_max_norma_producto')",
                      "declarado: un diametro por material, en metros, menor "
                      "o igual que el tope de la serie de ese material; lo "
                      "unico que cambia es cuantos puntos salen 'no factible "
                      "por diametro'"),
        reemplazado_por="Disponibilidad real de mercado para el corredor, "
                        "declarada en el expediente con su respaldo "
                        "(consulta a fabricantes y proveedores)",
        resolucion=DeCatalogo(
            catalogo_id="CAT_TUBERIA_LOCAL",
            que_elige="el tope de diametro por material que el mercado "
                      "local entrega, cuando es menor que el de la serie de "
                      "la norma de producto",
            advertencia="NINGUNA norma sostiene un tope de disponibilidad: "
                        "es un dato de mercado. Las series de las normas de "
                        "producto llegan a 3600 mm en concreto (AASHTO "
                        "M 170M-04) y en TMC (AASHTO M 36 / ASTM A760) y a "
                        "1500 mm en HDPE (AASHTO M 294-11, traduccion no "
                        "oficial). Declarado, el descarte por diametro se "
                        "imprime como de catalogo, no de norma",
        ),
    ),

    # --- VE-5 (ficha T8-11, H12 de la segunda auditoria de T-8) --- LOS
    # TECHOS DE TRANSCRIPCION DE LA FASE 6. Cuatro datos del sitio entran sin
    # techo porque ninguna fuente de `normas/` lo da (HEC-14 Cap. 5 no limita
    # ni la duracion, ni Sv, ni el tamaño del lecho; releidas las pags. 5-1 a
    # 5-7), y `dominios.py` no los inventa: acota lo que un dato PUEDE ser.
    # Un `D84_m` de 5.0 huele a milimetros escritos como metros, y la ficha
    # pedia un AVISO --- nunca un rechazo, nunca un cambio de resultado --- con
    # un criterio que diga donde esta el umbral. Ese umbral no lo da ninguna
    # norma, y por eso el criterio nace SIN VALOR y OPCIONAL: sin declarar no
    # hay aviso y todo sigue como hasta VE-5; declarado, cada dato por encima
    # de su techo se avisa en el punto. DECISION PENDIENTE DE FABLE: la sesion
    # de VE-5 no pudo consultar al consultor y tomo la mas conservadora, que
    # es no fijar ningun techo de archivo (informe de VE-5, lote «gui»).
    #
    # NIVEL MEDIDO: lo invoca la corrida de perfil con los opcionales
    # declarados de `tests/test_nivel_medido.py` (`servicio.correr_punto` lo
    # lee en cada punto, antes de la Fase 2, por `M6.avisos_de_transcripcion`).
    "techos_de_transcripcion_fase_6": Criterio(
        valor=None,                 # OPCIONAL: sin valor, no hay aviso
        opcional=True,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Techo de TRANSCRIPCION de cada dato de sitio de la Fase 6 "
                 "que entra sin techo fisico: por encima de el, el dato se "
                 "AVISA como probable error de unidad (milimetros escritos "
                 "como metros, segundos como minutos), sin rechazarlo ni "
                 "cambiar ningun resultado. Claves: "
                 "'duracion_caudal_pico_min' (min), "
                 "'profundidad_socavacion_estimada_m' (m), 'D84_m' (m), "
                 "'Sv_Pa' (Pa) y 'D85_m' (m), las tres ultimas del objeto "
                 "'material_lecho_salida'",
        justificacion="Decide, cuando se declara, a partir de que valor un "
                      "dato de sitio de la Fase 6 se avisa como probable "
                      "error de transcripcion. Es opcional y no un vacio: "
                      "sin declarar, la corrida es la de siempre y la "
                      "guardia de salida de la hoya (LimiteNumericoError) "
                      "sigue atrapando lo que desborda. Ninguna norma da un "
                      "techo para estos datos (HEC-14 Cap. 5, pags. 5-1 a "
                      "5-7, no los limita), de modo que el umbral es una "
                      "eleccion del proyectista y solo produce un aviso",
        fuente="NINGUNA NORMA. HEC-14 (FHWA-HIF-12-026) Cap. 5, pags. "
               "impresas 5-1 a 5-7, no limita la duracion del caudal pico, "
               "el esfuerzo cortante Sv ni el tamaño D84 del lecho, y HEC-11 "
               "Sec. 4.4.1 no limita el D85 del filtro granular; dominios.py "
               "no lleva techo para ellos (fichas T8-11 y N3-01)",
        sensibilidad=("sin declarar: ningun aviso de transcripcion; la "
                      "corrida es la de antes de VE-5",
                      "declarado: un techo positivo por clave, en la unidad "
                      "de la clave; cada dato del punto por encima de su "
                      "techo sale como aviso del punto, y ningun numero del "
                      "calculo cambia"),
        reemplazado_por="Los techos que el proyectista adopte con su "
                        "respaldo (el rango del EMS y del estudio "
                        "hidrologico del corredor)",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el rango plausible de cada dato "
                        "en su corredor; ninguna norma lo fija",
            dominio="un real positivo y finito por clave, en la unidad de "
                    "la clave",
        ),
    ),

    # 'h_relleno_min_concreto_tmc' SE RETIRO. Declaraba 0.30 m [N->] para
    # concreto y TMC "por analogia sobre un vacio verificado": el HDPE es el
    # material menos tolerante a cobertura reducida, luego exigirle a los
    # otros dos su mismo recubrimiento no podia quedar del lado inseguro.
    #
    # Las dos mitades del argumento cayeron a la vez.
    #
    # (1) EL VACIO NO ERA UN VACIO (NOR-VAC-01). La busqueda se declaro
    #     cerrada tras agotar tres fuentes -- normas de producto, Manual de
    #     Puentes y EG-2013 -- y falto la cuarta, que ademas esta en el propio
    #     repositorio y es la que Sec. 0.2 adopta de extremo a extremo: AASHTO
    #     LRFD 9a ed. (2020), Art. 12.6.6.3 "Minimum Cover" y su
    #     Tabla 12.6.6.3-1, pag. 12-22, tabulan la cobertura minima por tipo
    #     de conducto. Vive ahora en 'cobertura_minima_aashto'.
    # (2) EL NUMERO ERA CORTO. Esa tabla pone un PISO de 12.0 in = 0.3048 m
    #     para concreto y metal, de modo que 0.30 m quedaba 5 mm por debajo;
    #     y lo que gobierna en diametros grandes no es el piso sino Bc/8, que
    #     para un tubo de 2.40 m de concreto (Bc ~ 2.9 m) da ~0.36 m, un 20 %
    #     mas que lo adoptado.
    #
    # Se retira en vez de corregirle el numero porque ya no queda vacio que
    # cubrir: el recubrimiento minimo pasa a CALCULARSE
    # (`M7_geometria.altura_recubrimiento`) como el mayor entre el minimo de
    # EG-2013 -- que solo existe para HDPE -- y la cobertura minima de AASHTO,
    # que depende del diametro EXTERIOR y de la condicion de pavimento. Un
    # escalar unico para dos materiales no puede expresar eso.
    #
    # Cae con el la referencia a WSDOT M 23-03.12 Tabla 8-6 (NOR-ANA-01): era
    # la unica cita que la memoria ofrecia para sostener "el concreto tolera
    # mas", y no esta en el repositorio. La Tabla 12.6.6.3-1 confirma la
    # DIRECCION de aquel argumento -- bajo pavimento el termoplastico pide
    # ID/2 >= 24 in, el valor mas alto de la tabla -- y desmiente su MAGNITUD:
    # la analogia era conservadora en el orden de los materiales y no en el
    # numero. Con la tabla cableada, ni la direccion ni la magnitud dependen
    # ya de una fuente ausente.

    "cobertura_minima_aashto": Criterio(
        valor={
            # Tabla 12.6.6.3-1, transcrita a SI. Por material del catalogo y
            # por condicion de pavimento. Cada fila:
            #   divisor   el D se divide por el (None: la fila es un valor
            #             fijo, sin termino proporcional al diametro)
            #   sobre     que diametro entra en el divisor, con la nomenclatura
            #             del propio Art. 12.6.6.3: "exterior" para Bc
            #             ("outside diameter or width of the structure"),
            #             "interior" para ID ("inside diameter"), "nominal"
            #             para S ("diameter of pipe")
            #   piso_m    el ">=" de la tabla: minimo absoluto, en metros
            #
            # Los tres divisores son adimensionales y las tres filas son
            # homogeneas: la cobertura sale en la misma unidad que el diametro
            # con que se entra. No hay conversion de unidades que hacer.
            "concreto_reforzado": {
                # "Reinforced Concrete Pipe / Under unpaved areas or top of
                # flexible pavement -- Bc/8 or B'c/8, whichever is greater,
                # >= 12.0 in."
                #
                # POR QUE EL "whichever is greater" NO APARECE EN EL DATO. El
                # segundo termino es B'c, que el Art. 12.6.6.3 define como
                # "out-to-out vertical rise of pipe (ft)". En un conducto
                # CIRCULAR la altura exterior de punta a punta ES el diametro
                # exterior, de modo que B'c = Bc por geometria y el maximo de
                # los dos terminos se reduce a Bc/8.
                #
                # ESTA REDUCCION ES CORRECTA PARA EL CIRCULAR Y LA PREGUNTA
                # DEL CAJON NO SE CONTESTA AQUI. Dos versiones anteriores de
                # este comentario se equivocaron, cada una por su lado, y
                # conviene separar que parte de cada una se sostiene.
                #
                # LO QUE SE SOSTIENE, y es de C5: la lectura de B'c como
                # «out-to-out vertical rise», verificada contra la pag.
                # impresa 12-21. Es ademas la que corrigio el «sqrt(Bc)/8» que
                # la ficha NOR-VAC-01 habia inventado leyendo la prima como un
                # radical.
                #
                # LO QUE NO SE SOSTIENE, tambien de C5: que «en un marco B'c y
                # Bc son DISTINTOS, de modo que esta reduccion pide DE MENOS»,
                # con la medicion «un marco de 3.00 x 1.50 m: el codigo
                # exigiria 0.3048 m y la tabla exige 0.4125 m, un 26 % mas».
                # Esa medicion APLICA AL CAJON UNA FILA ROTULADA «Reinforced
                # Concrete PIPE», y la tabla no le exige nada a un marco:
                # verificado en C7 contra AASHTO LRFD 9a ed., leida
                # renderizada. No hay fila de cajon de concreto; `B'c` se
                # define «of pipe» y no esta definido para seccion rectangular
                # en las 110 paginas de la Sec. 12; y el «whichever is
                # greater» aparece UNA vez en toda la seccion, dentro de esa
                # celda, sin articulado que lo extienda.
                #
                # DONDE VA EL CAJON: a `cobertura_minima_cajon`, vacio
                # declarado [A], con su AfirmacionNegativa. La regla
                # vinculante #9 pedia lo contrario y SE RETIRO en C7 -- no
                # estaba pendiente, estaba mal enunciada --. Ver §6 y §16.12.
                "no_pavimentado": {"divisor": 8.0, "sobre": "exterior",
                                   "piso_m": 0.3048},
                "flexible": {"divisor": 8.0, "sobre": "exterior",
                             "piso_m": 0.3048},
                # "Under bottom of rigid pavement -- 9.0 in."
                "rigido": {"divisor": None, "sobre": "exterior",
                           "piso_m": 0.2286},
            },
            "tmc": {
                # "Corrugated Metal Pipe / -- / S/8 >= 12.0 in." Fila unica:
                # la tabla no distingue condicion de pavimento para el metal
                # corrugado, y por eso las tres condiciones repiten la misma
                # fila en vez de inventarle dos que la tabla no trae.
                "no_pavimentado": {"divisor": 8.0, "sobre": "nominal",
                                   "piso_m": 0.3048},
                "flexible": {"divisor": 8.0, "sobre": "nominal",
                             "piso_m": 0.3048},
                "rigido": {"divisor": 8.0, "sobre": "nominal",
                           "piso_m": 0.3048},
            },
            "hdpe": {
                # "Thermoplastic Pipe / Under unpaved areas -- ID/8 >= 12.0 in.
                #                     / Under paved roads  -- ID/2 >= 24.0 in."
                # Las dos condiciones pavimentadas caen en la MISMA fila: la
                # tabla dice "paved roads" sin separar flexible de rigido.
                "no_pavimentado": {"divisor": 8.0, "sobre": "interior",
                                   "piso_m": 0.3048},
                "flexible": {"divisor": 2.0, "sobre": "interior",
                             "piso_m": 0.6096},
                "rigido": {"divisor": 2.0, "sobre": "interior",
                           "piso_m": 0.6096},
            },
        },
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Cobertura minima sobre la clave del conducto, por material y "
                 "condicion de pavimento (Tabla 12.6.6.3-1 de AASHTO LRFD)",
        justificacion="Decide con que tabla se cubre la cobertura minima "
                      "sobre la clave del conducto para concreto y TMC, donde "
                      "el corpus peruano no da numero. La fuente adoptada "
                      "(AASHTO LRFD, Art. 12.6.6.3 y Tabla 12.6.6.3-1; filas, "
                      "definiciones y nota al pie transcritas literales en "
                      "`fuente` y en el registro, tabla "
                      "AASHTO_LRFD_9.T12.6.6.3-1) fija minimos por material y "
                      "condicion de pavimento. Lo que el corpus peruano no "
                      "resuelve, con la busqueda agotada fuente por fuente y "
                      "registrada en docs/manifiesto_citas.md Sec. 14.a: "
                      "EG-2013 fija la altura minima de relleno solo para "
                      "HDPE (Subseccion 508.07) y el Manual de Puentes no "
                      "incorporo la Sec. 12 de AASHTO LRFD. Se adopta esta "
                      "tabla porque Sec. 0.2 de la hoja de ruta toma la Via 1 "
                      "-- AASHTO LRFD de extremo a extremo --, lo que la hace "
                      "la fuente natural y no una analogia; es [C] y no [N] "
                      "porque AASHTO no es norma peruana vigente: es la "
                      "fuente tecnica reconocida con que se cubre el vacio. "
                      "Regla de conflicto, la misma que Sec. 0.2 aplica al "
                      "recubrimiento de concreto frente a E.060: rige el "
                      "mayor de los dos minimos -- para HDPE conviven el 0.30 "
                      "m de EG-2013 [N] y esta tabla, y se aplica el mayor; "
                      "para concreto y TMC solo existe esta. Simplificacion "
                      "conservadora declarada, el datum: la nota al pie de la "
                      "tabla mide la cobertura desde el pavimento (cara "
                      "superior del rigido, cara inferior del flexible), "
                      "mientras 7.A mide h_rec de la clave a la subrasante; "
                      "la cobertura de la tabla es entonces h_rec mas el "
                      "paquete que quede por encima de la subrasante, siempre "
                      "mayor o igual que h_rec, de modo que exigir el minimo "
                      "de la tabla a h_rec solo pide de mas, nunca de menos. "
                      "Se declara porque es una eleccion de encuadre, aunque "
                      "su direccion sea segura: cerrarla exige el desglose "
                      "del paquete estructural, que Sec. 1.2 no trae como "
                      "columna. La propia tabla trae una tension interna, "
                      "anotada para que nadie la lea como un descuido: la "
                      "fila del concreto describe su condicion contra la cara "
                      "superior del pavimento flexible y la nota al pie mide "
                      "desde la inferior; no se resuelve aqui porque "
                      "cualquiera de las dos lecturas situa el datum a nivel "
                      "de subrasante o mas arriba -- conservador con las dos "
                      "-- y resolverla sin el desglose del paquete seria "
                      "elegir una lectura sin dato que la sostenga. En la "
                      "fila del metal, S es el diametro nominal -- el Art. "
                      "12.6.6.3 define S como diametro del tubo y define Bc e "
                      "ID aparte -- y en la serie del producto ese nominal es "
                      "el interior: la Tabla 1 de ASTM A760/A760M-10 titula "
                      "su primera columna como diametro interior nominal; en "
                      "TMC la distincion es ademas de milimetros -- la pared "
                      "es una plancha mas la corrugacion -- mientras que la "
                      "cota de clave si la necesita entera. Que fila aplica "
                      "lo decide 'condicion_pavimento', que es un vacio "
                      "aparte y bloquea: la tabla es [C] y elegir su fila es "
                      "[A], el mismo reparto que F_PGA_TABLA / 'F_pga' y "
                      "REDUCCION_KH_POR_DESPLAZAMIENTO / "
                      "'factor_muro_eleccion' -- este ultimo con la salvedad "
                      "de que ahi la parte [N] no es una tabla sino un solo "
                      "valor autorizado",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed. (2020), "
               "Seccion 12 'Buried Structures and Tunnel Liners', "
               "Art. 12.6.6.3 'Minimum Cover' y Tabla 12.6.6.3-1, pag. "
               "impresa 12-22 (indice de pagina 1659 del PDF, 0-based, en "
               "normas/AASHTO.LRFD.Bridge.Design.Specifications_9th.Edition."
               "2020.pdf). Nomenclatura del propio articulo, las CUATRO "
               "definiciones: 'S = diameter of pipe (in.)', 'Bc = outside "
               "diameter or width of the structure (ft)', \"Bc' = out-to-out "
               "vertical rise of pipe (ft)\", 'ID = inside diameter (in.)'. "
               "Filas transcritas, literales, leidas sobre la celda RENDERIZADA "
               "y no sobre la extraccion de texto: Corrugated Metal Pipe "
               "'S/8 >= 12.0 in.'; Thermoplastic Pipe 'Under unpaved areas "
               "ID/8 >= 12.0 in.' y 'Under paved roads ID/2 >= 24.0 in.'; "
               "Reinforced Concrete Pipe 'Under unpaved areas or top of "
               "flexible pavement: Bc/8 or B'c/8, whichever is greater, "
               ">= 12.0 in.' y 'Under bottom of rigid pavement: 9.0 in.'. Nota "
               "al pie: 'Minimum cover taken from top of rigid pavement or "
               "bottom of flexible pavement'. Cuerpo del articulo: 'The "
               "minimum cover, including a well-compacted granular subbase and "
               "base course, shall not be less than that specified in Table "
               "12.6.6.3-1'. "
               "POR QUE SE INSISTE EN 'RENDERIZADA': el segundo termino de la "
               "fila del concreto se extrae como 'Bc\\uf0a2' -- la prima de "
               "B'c es un glifo de SymbolMT -- y la ficha NOR-VAC-01 de la "
               "auditoria normativa lo leyo como una RAIZ, 'sqrt(Bc)/8'. Esta "
               "transcripcion lo copio de la ficha en su primera version, sin "
               "abrir el PDF, y de ahi salio una formula que no existe, un "
               "argumento de homogeneidad inventado y un factor de conversion "
               "pie-metro que no hacia falta. No hay radical en la tabla: la "
               "celda dice 'Bc/8 or B'c/8'. Es exactamente el defecto que este "
               "cluster existe para eliminar, cometido dentro de el. "
               "Conversiones a SI: 12.0 in = 0.3048 m, 9.0 in = 0.2286 m, "
               "24.0 in = 0.6096 m (1 in = 0.0254 m exacto). "
               "BUSQUEDA EN EL CORPUS PERUANO, agotada fuente por fuente y "
               "registrada en docs/manifiesto_citas.md Sec. 14.a: EG-2013 "
               "Cap. V fija la altura minima de relleno SOLO para HDPE "
               "(Subseccion 508.07, pag. impresa 984, verificada leyendo el "
               "PDF); las Secciones 505, 506 y 507 regulan colocacion y "
               "compactacion y remiten a la Seccion 502, que tampoco fija "
               "altura minima de diseño. El Manual de Puentes (RD "
               "041-2016-MTC/14) no incorporo un capitulo equivalente a la "
               "Seccion 12 de AASHTO LRFD y no fija altura minima de relleno "
               "para ningun material: trata estructuras enterradas en al "
               "menos cinco numerales (2.4.3.3.2 pag. 109; Tabla 2.4.5.3.1-2 "
               "pag. 143; 2.8.1.3A.6.2 pag. 280; 2.9.1.4.6.4.6 pag. 362; "
               "2.4.3.11.1 pag. 121) y los cinco SUPONEN conocida la "
               "cobertura. Las normas de producto tampoco: AASHTO M 170M-04 "
               "lo excluye en su Nota 1 ('manufacturing and purchase "
               "specification only'), AASHTO M 36 en su §1.3 y ASTM "
               "A760/A760M-10 en su §1.4 -- la atribucion anterior ponia la "
               "misma 'Nota 1' en las tres y era falsa en dos (NOR-PRO-03). "
               "TRAMPA DE VOCABULARIO, anotada para que nadie la vuelva a "
               "pisar: el Manual de Puentes SI usa la palabra 'recubrimiento' "
               "para alcantarillas en la Tabla 2.9.1.5.5.3-1 (pag. impresa "
               "378), pero ahi significa el recubrimiento de CONCRETO "
               "SOBRE EL ACERO DE REFUERZO, no la altura de relleno de "
               "tierra. Son dos conceptos que comparten palabra en espaniol y "
               "no tienen ninguna relacion; el numero de esa tabla NO sirve "
               "aqui. "
               "LA FILA DE ESA TABLA, COMPLETA (NOR-PUE-14): esta nota citaba "
               "'2.0 in / 50 mm' a secas, como si fuera el recubrimiento de "
               "una alcantarilla cualquiera, y son dos imprecisiones en seis "
               "caracteres. Primera, la fila es 'Alcantarillas de cajon de "
               "concreto PREFABRICADOS' y tiene tres subfilas, cada una con "
               "su condicion: 'forjados para ser utilizados como superficie "
               "de conduccion' 2.5 in; 'forjados con inferior a 2 pies de "
               "relleno que no se utilicen como una superficie de conduccion' "
               "2.0 in; 'todos los demas miembros' 1.0 in. Los 2.0 in son de "
               "la losa superior de una alcantarilla CAJON PREFABRICADA con "
               "menos de 2 pies de relleno que ademas no sea superficie de "
               "rodadura: dos condiciones que no cumple ningun conducto del "
               "catalogo circular de Sec. 3.2. Segunda, 2.0 in son 50.8 mm, "
               "no 50. Las tres subfilas estan transcritas, con sus tres "
               "categorias de acero, en 'tabla_recubrimiento_aashto_mm'. "
               "LA EVIDENCIA DE INDICE QUE SE RETIRO, por falsa (NOR-PUE-06): "
               "se sostenia que 'el indice del Manual salta de 2.11 (Muros de "
               "Contencion y Estribos) a 2.12'. El 2.11 del Manual es 'DISEÑO "
               "DE BARRERAS DE SONIDO' (15 AASHTO), pag. 505, y el 2.12 "
               "'Disposiciones Constructivas', pag. 513; los muros y estribos "
               "viven dentro de 2.8 Cimentaciones, de donde este mismo "
               "expediente saca 2.8.1.1.14.2. Ademas la numeracion del Manual "
               "no sigue la de AASHTO (2.8 <-> 10, 2.10 <-> 14.6, 2.11 <-> "
               "15), de modo que 'entre 2.11 y 2.12 deberia estar la Sec. 12' "
               "no era una inferencia valida. La conclusion -- que el Manual "
               "no incorporo la Sec. 12 -- no cambia; el argumento con que se "
               "sostenia, si",
        reemplazado_por="Una disposicion PERUANA que fije la cobertura minima "
                        "para concreto y TMC: hoy no existe, y por eso se "
                        "aplica AASHTO LRFD. La cerraria que el MTC "
                        "incorporase la Sec. 12 de AASHTO LRFD al Manual de "
                        "Puentes, o una version del EG-2013 que extendiese el "
                        "508.07 a los otros dos materiales. Queda ademas "
                        "abierto el DATUM: la tabla mide la cobertura desde "
                        "el fondo del pavimento flexible o el techo del "
                        "rigido, y 7.A la exige sobre la subrasante -- la "
                        "simplificacion es conservadora y se cierra con el "
                        "desglose del paquete estructural, que Sec. 1.2 no "
                        "trae como columna",
        vacio_verificado="manifiesto_citas.md Sec. 14.a",
        verificacion_pendiente="EL SEGUNDO TERMINO DE LA FILA DEL CONCRETO "
                               "(B'c/8) no esta en el dato, y se reduce a "
                               "Bc/8 porque en un CIRCULO B'c = Bc. "
                               "ESTE CAMPO SE CONTRADECIA CON EL COMENTARIO "
                               "DE ARRIBA Y HAY QUE DECIR EN QUE, porque es "
                               "un dato sobre como se escribio el criterio y "
                               "no solo un error a pisar: decia que la "
                               "reduccion vale «porque el catalogo es "
                               "circular» y que el termino haria falta «si "
                               "algun dia entra una seccion no circular», "
                               "mientras el comentario del `valor`, reescrito "
                               "en C5, ya afirmaba que ese dia habia llegado. "
                               "C5 reescribio el comentario que leyo y no el "
                               "campo que no leyo, de modo que el criterio "
                               "afirmaba a la vez que el caso ya llego y que "
                               "todavia no. Las DOS versiones eran "
                               "incorrectas, por motivos distintos: la vieja "
                               "por obsoleta, la nueva por extender una fila "
                               "fuera de su rotulo. "
                               "LO QUE QUEDA PENDIENTE DE VERDAD es otra "
                               "cosa: si algun dia entra un TUBO-ARCO -- que "
                               "sigue siendo `pipe` y por tanto sigue dentro "
                               "de esta fila --, ahi B'c y Bc si difieren y "
                               "el termino hace falta. Un CAJON no es ese "
                               "caso: no tiene fila aqui (C7, regla #9 "
                               "retirada). "
                               "Las filas que el catalogo de este proyecto NO "
                               "usa quedaron fuera de la transcripcion "
                               "(Spiral Rib, Structural Plate, Fiberglass, "
                               "Steel-Reinforced Thermoplastic, Long-Span, "
                               "Box y Deep Corrugated). Si algun dia el "
                               "catalogo de Sec. 3.2 admite otra forma, hay "
                               "que traerlas: hoy no estan porque no aplican, "
                               "no porque no existan. Falta ademas cerrar el "
                               "datum -- ver la SIMPLIFICACION CONSERVADORA de "
                               "la justificacion --, que necesita el desglose "
                               "del paquete estructural",
        resolucion=DeTabla(
            tablas=("AASHTO_LRFD_9.T12.6.6.3-1",),
            que_elige="nada por si mismo: el valor es la tabla por material. "
                      "La fila la elige `condicion_pavimento`",
            elegido_por="condicion_pavimento",
        ),
    ),

    # -----------------------------------------------------------------------
    # LA COBERTURA DEL MARCO, que no sale de la tabla de al lado
    # -----------------------------------------------------------------------
    # LA REGLA VINCULANTE #9 PEDIA LO CONTRARIO Y ERA FALSA, no pendiente.
    # Decia que «para un cajon vuelve el segundo termino B'c/8», y la
    # verificacion contra la fuente primaria (AASHTO LRFD 9a ed., Sec. 12
    # leida RENDERIZADA, folio 12-N = PDF - 1638 medido) refuta su premisa: la
    # Tabla 12.6.6.3-1 no tiene fila de cajon de concreto, de modo que no hay
    # segundo termino que devolver porque no hay fila de la que devolverlo.
    # Traerlo seria aplicar una fila rotulada «Reinforced Concrete PIPE» a algo
    # que no lo es, que es el defecto que este proyecto declara no cometer.
    # Se retiro en C7 -- §6 y §16 de docs/ruta_familia_c.md --.
    #
    # Y HAY UN TERCER ERROR EN AQUELLA MEDICION, medido aqui, que no es el de
    # la regla ni el de C5 y que conviene dejar escrito porque cambia cual es
    # el arreglo. La medicion de C5 -- «un marco de 3.00 x 1.50 m: el codigo
    # exigiria 0.3048 m y la tabla exige 0.4125 m» -- llama a su 0.4125 «el
    # segundo termino B'c/8», y no lo es: con t = 0.15 ese marco tiene
    # Bc = 3.30 y B'c = 1.80, de modo que 3.30/8 = 0.4125 es el PRIMER termino,
    # Bc/8, mientras B'c/8 = 0.225 es el MENOR de los tres numeros en juego.
    # Lo que le falta al codigo no es el termino que se dejo fuera: es que al
    # UNICO termino que conserva le entra la dimension equivocada. `M7` recibe
    # un escalar `D` que en un marco vale la ALTURA, y el `D + 2t` de entonces lo
    # convierte en H + 2t = B'c, que se mete en la ranura de Bc. Medido: para
    # ese marco la cobertura de hoy sale 0.3048 m Y NO DEPENDE DE B EN
    # ABSOLUTO -- el ancho no es argumento de la funcion --. Por eso el arreglo
    # es de DOS piezas y no de una: este vacio declarado, y M7 llevando la
    # `Seccion` en vez del escalar (punto 5 de C7).
    "cobertura_minima_cajon": Criterio(
        # --- T-3 --- 0.3048 m (12.0 in): el piso de la fila del TUBO de
        # concreto de la Tabla 12.6.6.3-1, POR ANALOGIA rotulada.
        # --- T-3 (auditoria adversarial, H5) --- Y COMO AVISO: la fuente
        # admite el marco sin relleno, y este valor es mas restrictivo que
        # ella. G1 del marco avisa (INDICADOR) cuando solo falta esta
        # cobertura; el resguardo sigue bloqueando. Ver `M7.g1_rasante_
        # congelada` y `TamizadoRasante.cobertura_como_aviso`.
        valor=0.3048,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Cobertura minima de SUELO sobre la clave de un marco de "
                 "concreto vaciado in situ, m (Sec. 7.A). No es el "
                 "recubrimiento de concreto sobre la armadura",
        justificacion="Decide la cobertura de suelo sobre la clave de un "
                      "marco de concreto vaciado in situ que el proyecto "
                      "pide, y con ella el AVISO de G1 en la Sec. 7.A. Lo que "
                      "las fuentes dicen del marco -- tres textos, leidos en "
                      "su pagina -- es que lo admiten sin relleno: el Manual "
                      "de Hidrologia, num. 4.1.1.3.4 a), pag. impresa 72 "
                      "(cita MC_HHD.4.1.1.3.4a#NIVELES), permite ubicar el "
                      "marco con la rasante a nivel de su losa superior; "
                      "su Lamina N 03, pag. impresa 209 (cita "
                      "MC_HHD.LAMINA_03), dibuja el marco en cruce de canal "
                      "de riego con la calzada sobre la losa, sin relleno "
                      "acotado; y AASHTO LRFD 9a ed., Art. 12.6.6.3, pag. "
                      "impresa 12-22 (cita "
                      "AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA), dice que si no "
                      "hay cobertura de suelo la losa superior del cajon de "
                      "concreto se diseña para la aplicacion directa de la "
                      "carga vehicular. Ninguna fija una cobertura minima "
                      "para el marco: la Tabla 12.6.6.3-1 no tiene fila de "
                      "cajon de concreto -- sus dos filas de concreto son de "
                      "tubo y la unica con cajon en el rotulo es de placa "
                      "estructural metalica --, el Art. 12.11 no la fija "
                      "(barrido en la AfirmacionNegativa "
                      "SIN_CAJON_DE_CONCRETO_T12663), EG-2013 trae altura "
                      "minima de relleno solo para HDPE (Subseccion 508.07) "
                      "y el Manual de Puentes no tiene un capitulo "
                      "equivalente a la Sec. 12. Se adopta 0.3048 m, el piso "
                      "de 12.0 in que la fila del TUBO de concreto bajo zonas "
                      "sin pavimentar o bajo pavimento flexible pone a la "
                      "cobertura (Tabla 12.6.6.3-1, pag. impresa 12-22), por "
                      "analogia rotulada -- la tabla mide desde el fondo del "
                      "pavimento flexible, que es lo que 7.A hace al sumar el "
                      "paquete --: con relleno el marco trabaja enterrado, y "
                      "la carga viva a traves del relleno solo es evaluable "
                      "desde 2.0 ft (AASHTO LRFD 3.6.1.2.6a), de modo que un "
                      "marco con menos queda fuera de lo que la Fase 8 sabe "
                      "verificar. Es mas restrictivo que la fuente, y por eso "
                      "avisa y no bloquea (criterio general del dueño del "
                      "proyecto: las analogias avisan): con la rasante bajo "
                      "la cota que pide, G1 cumple con veredicto INDICADOR "
                      "si la clave queda bajo la subrasante y el resguardo "
                      "se cumple, y dice que la fuente admite el marco sin "
                      "cobertura a cambio de diseñar la losa para la carga "
                      "directa. El resguardo bajo la subrasante, que no es "
                      "analogia, sigue bloqueando. Es ademas el valor que el "
                      "codigo entregaba al marco antes de abrirse este "
                      "criterio y el que la guia de perfil y la suite "
                      "declaraban. No se adopta la fila entera, max(Bc/8, "
                      "0.3048), porque su Bc/8 solo se despega del piso con "
                      "Bc > 2.4384 m, que ningun escalon de la progresion "
                      "adoptada alcanza (el mayor, 2.00 x 1.50 con t = 0.20 "
                      "y una celda, tiene Bc = 2.40 m); con un marco mas "
                      "ancho o con varias celdas hay que revisarlo. Ni el "
                      "cero de la fuente como valor, que traslada la "
                      "exigencia a un diseño estructural de la losa para "
                      "carga directa que este alcance difiere",
        fuente="NINGUNA fija la cobertura minima de un marco, y las tres que "
               "hablan de el lo ADMITEN SIN RELLENO: Manual de Hidrologia "
               "(MTC), num. 4.1.1.3.4 a), pag. impresa 72, PDF 75 (cita "
               "MC_HHD.4.1.1.3.4a#NIVELES, permiso: la rasante puede "
               "coincidir con la losa); su Lamina N 03, pag. impresa 209, PDF "
               "212 (cita MC_HHD.LAMINA_03, el marco en cruce de canal de "
               "riego); y AASHTO LRFD 9a ed., Art. 12.6.6.3, pag. impresa "
               "12-22, PDF 1660 (cita AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA: "
               "sin cobertura, la losa superior se diseña para la carga "
               "vehicular directa). El vacio esta verificado, no es una "
               "omision: ver la `AfirmacionNegativa` "
               "SIN_CAJON_DE_CONCRETO_T12663 en el registro, que fija el "
               "ambito barrido de la Sec. 12 completa. El 0.3048 m es la "
               "fila del TUBO de la Tabla 12.6.6.3-1 aplicada por analogia, "
               "mas restrictivo que la fuente",
        reemplazado_por="Una fila de cajon de concreto en la Tabla 12.6.6.3-1 "
                        "de una edicion futura de AASHTO LRFD, o una "
                        "disposicion peruana -- EG-2013 o Manual de Puentes -- "
                        "que fije altura minima de relleno para marco. "
                        "Tambien lo cerraria, por otra via, declarar el "
                        "diseno de la losa superior para carga vehicular "
                        "directa: entonces el numero deja de hacer falta "
                        "porque la fuente cubre ese caso expresamente",
        sensibilidad=(
            "0.3048 m (12.0 in): el PISO que la Tabla 12.6.6.3-1 pone a la "
            "fila del TUBO de concreto, adoptado por analogia. Es el valor "
            "que el codigo entregaba de hecho antes de C7, de modo que "
            "declararlo no mueve ninguna rasante: lo que cambia es que pasa a "
            "estar dicho. Quien lo adopte tiene que declarar la analogia -- "
            "la fila es de `pipe` -- y no presentarla como exigencia",
            "max(Bc/8, 0.3048): la misma fila del tubo aplicada ENTERA, con "
            "el ancho exterior del marco en la ranura de Bc. Solo se despega "
            "del piso cuando Bc > 2.4384 m: para el marco de 2.00 x 1.50 con "
            "t = 0.15 da Bc/8 = 0.2875 m y gobierna el piso; para uno de "
            "3.00 x 1.50 da 0.4125 m, un 35 % sobre el piso. Es la lectura "
            "mas exigente de las tres y sigue siendo analogia",
            "0 (sin cobertura): la unica rama que la fuente cubre "
            "EXPRESAMENTE para un cajon, y a cambio obliga a disenar la losa "
            "superior para carga vehicular directa (pag. impresa 12-22). No "
            "es la opcion barata: traslada la exigencia de la rasante al "
            "refuerzo, y esa parte es de expediente",
        ),
        resolucion=Libre(
            que_lo_fija="el proyectista, declarando de cual de las tres "
                        "lecturas parte y por que. Las dos primeras son "
                        "ANALOGIA con la fila del tubo y hay que rotularlas "
                        "asi; la tercera es la unica que la fuente cubre para "
                        "un cajon, y arrastra una exigencia estructural",
            dominio="real >= 0, en metros",
        ),
        # --- T-3 --- `vacio_verificado` YA SE DECLARA: con valor de
        # archivo el criterio cubre el vacio que la AfirmacionNegativa
        # SIN_CAJON_DE_CONCRETO_T12663 fija, y el ancla es §16.12 de la ruta
        # de la Familia C, donde C7 lo verifico contra la pagina renderizada.
        vacio_verificado="ruta_familia_c.md Sec. 16.12",
    ),

    # -----------------------------------------------------------------------
    # LAS DOS LAGUNAS DE LAS TABLAS DE h_eq, que estaban resueltas en duro
    # -----------------------------------------------------------------------
    # Las declaraba el registro (`Laguna(..., si_nadie_lo_cierra=BLOQUEA)`) y
    # apuntaban a estas dos claves, que NO EXISTIAN: el codigo resolvia las
    # dos a mano -- el clamp de `_interpolar_h_eq` y el `lejos = borde >= ...`
    # de `h_eq_sobrecarga_trasdos` -- sin etiqueta, sin sensibilidad y sin
    # excepcion. Es el «rellenar un vacio en silencio» que CLAUDE.md llama el
    # peor error posible, cometido DENTRO del cluster que existe para
    # eliminarlo, y lo encontro la auditoria adversarial de la propia sesion.
    #
    # Y NO ERA INOCUO. Con muro paralelo, borde 0.20 m y altura total 1.20 m
    # las dos lagunas se apilan y la funcion devolvia 1.524 m -- 2.54 veces el
    # piso del Manual -- sin decir de donde salia. Ahora se detiene.
    "h_eq_bajo_altura_tabulada": Criterio(
        valor=None,                 # VACIO: bloquea h_eq bajo 5.0 ft
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_STR,
        concepto="Que hacer con un muro de menos de 5.0 ft (1.524 m), altura "
                 "por debajo de la primera fila de las Tablas 3.11.6.4-1 y "
                 "-2 de AASHTO: 'primera_fila' o 'extrapolar_lineal'",
        justificacion="Decide que hacer con un muro por debajo de la primera "
                      "fila tabulada de altura equivalente de suelo, y hoy es "
                      "un vacio declarado. La fuente (Tablas 3.11.6.4-1 y -2 "
                      "de AASHTO, transcritas como AASHTO_LRFD_9.T3.11.6.4-1 "
                      "y -2 en el registro con su regla de interpolacion) "
                      "arranca en 5.0 ft (1.524 m) y manda interpolar solo "
                      "para alturas intermedias -- entre filas. Lo que no "
                      "resuelve: por debajo de la primera fila no hay dos "
                      "filas entre las que interpolar; extrapolar el primer "
                      "tramo no lo autoriza la fuente, y tomar la primera "
                      "fila tampoco lo dice, aunque va del lado conservador "
                      "porque h_eq decrece con la altura. Las dos lecturas "
                      "son elecciones del proyectista y por eso esto es [A] y "
                      "no [N]; se deja vacio hasta que se declare una, y sus "
                      "numeros estan en el campo `sensibilidad`. El caso es "
                      "alcanzable en este expediente: un cabezal de "
                      "alcantarilla pequeña con H mas espesor de zapata menor "
                      "de 1.524 m cae aqui, y el corredor tiene puntos de "
                      "diametro pequeño",
        fuente="AASHTO LRFD 9a ed. (2020), Art. 3.11.6.4, Tablas 3.11.6.4-1 y "
               "3.11.6.4-2, pag. impresa 3-151 (PDF 205). Las dos arrancan en "
               "'5.0' y su regla de interpolacion es literal: 'Linear "
               "interpolation shall be used for intermediate wall heights'. "
               "Laguna registrada en normativa/tablas.py, tablas "
               "AASHTO_LRFD_9.T3.11.6.4-1 y -2",
        sensibilidad=("primera_fila (h_eq = 5.0 ft = 1.524 m para muro "
                      "paralelo con borde 0.0, o 4.0 ft = 1.219 m para "
                      "estribo perpendicular) frente a extrapolar_lineal "
                      "(para 3.94 ft: 5.318 ft = 1.621 m en el caso paralelo, "
                      "un +6.4 %). La extrapolacion es la MAS conservadora de "
                      "las dos, de modo que ni siquiera 'el lado seguro' "
                      "decide sola: hay que elegir",),
        resolucion=DeTabla(
            tablas=("AASHTO_LRFD_9.T3.11.6.4-1",
                    "AASHTO_LRFD_9.T3.11.6.4-2"),
            que_elige="que hacer con un muro por debajo de la primera fila "
                      "tabulada (5.0 ft): tomar esa primera fila o "
                      "extrapolar linealmente",
            laguna="las dos tablas arrancan en 5.0 ft y su regla de "
                   "interpolacion habla de alturas INTERMEDIAS; por debajo "
                   "de la primera fila la fuente no se pronuncia",
        ),
    ),

    "h_eq_banda_intermedia_borde": Criterio(
        valor=None,                 # VACIO: bloquea h_eq en 0 < d < 1.0 ft
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_STR,
        concepto="Que columna de la Tabla 3.11.6.4-2 leer cuando la distancia "
                 "del trasdos al borde de calzada cae ESTRICTAMENTE entre "
                 "0.0 ft y 1.0 ft: 'columna_cero' o "
                 "'interpolar_entre_columnas'",
        justificacion="Decide que columna de la Tabla 3.11.6.4-2 se lee "
                      "cuando la distancia del trasdos al borde de calzada "
                      "cae estrictamente entre sus dos rotulos, y hoy es un "
                      "vacio declarado. La fuente (tabla "
                      "AASHTO_LRFD_9.T3.11.6.4-2 del registro, con su laguna "
                      "declarada) tiene dos columnas -- '0.0 ft' y '1.0 ft or "
                      "Further' -- y la unica interpolacion que autoriza es "
                      "entre filas, para alturas intermedias de muro, no "
                      "entre columnas. Lo que no resuelve: ninguna regla para "
                      "la banda 0.0 < d < 1.0 ft. Leer la columna de 0.0 ft "
                      "para toda distancia menor que 1.0 ft es el lado "
                      "conservador y no es lo que la tabla dice; interpolar "
                      "entre columnas es inventarse una regla que la fuente "
                      "no da. Los dos son elecciones del proyectista y por "
                      "eso esto es [A]; se deja vacio hasta que se declare "
                      "una, y los numeros de las dos lecturas estan en el "
                      "campo `sensibilidad`. El efecto no es marginal: para "
                      "un muro de 5.0 ft las dos columnas valen 5.0 ft y 2.0 "
                      "ft, un factor 2.5",
        fuente="AASHTO LRFD 9a ed. (2020), Tabla 3.11.6.4-2 'Equivalent "
               "Height of Soil for Vehicular Loading on Retaining Walls "
               "Parallel to Traffic', pag. impresa 3-151 (PDF 205), "
               "encabezado superior 'heq (ft) Distance from wall backface to "
               "edge of traffic'. Laguna registrada en normativa/tablas.py, "
               "tabla AASHTO_LRFD_9.T3.11.6.4-2",
        sensibilidad=("para un muro de 5.0 ft y borde 0.5 ft: columna_cero da "
                      "5.0 ft (1.524 m) e interpolar_entre_columnas da 3.5 ft "
                      "(1.067 m), un -30 %. Para un muro de 10.0 ft: 3.5 ft "
                      "frente a 2.75 ft, un -21 %. La eleccion mueve el "
                      "empuje LS en la misma proporcion",),
        resolucion=DeTabla(
            tablas=("AASHTO_LRFD_9.T3.11.6.4-2",),
            columna_id="borde_0_0_ft",
            que_elige="que columna leer cuando la distancia del trasdos al "
                      "borde de calzada cae estrictamente entre 0.0 ft y "
                      "1.0 ft",
            laguna="la tabla manda interpolar entre FILAS (alturas) y no "
                   "autoriza interpolar entre estas dos columnas: la banda "
                   "0.0 < d < 1.0 ft es una laguna de la fuente",
        ),
    ),

    "condicion_pavimento": Criterio(
        # LA MAS EXIGENTE DE LAS TRES, y ademas la realista para una via de
        # evitamiento pavimentada. Medido sobre `cobertura_minima_aashto`
        # para D = 0.90 m: concreto 0.305 m con 'flexible' y con
        # 'no_pavimentado' frente a 0.229 m con 'rigido'; HDPE 0.610 m con
        # 'flexible' y con 'rigido' frente a 0.305 m con 'no_pavimentado'.
        # 'flexible' es el maximo en las tres columnas de material a la vez:
        # no hay eleccion mas conservadora dentro de la ventana.
        valor="flexible",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        concepto="Condicion de la superficie de rodadura sobre el cruce, para "
                 "elegir la fila de la Tabla 12.6.6.3-1: 'no_pavimentado', "
                 "'flexible' o 'rigido'",
        justificacion="Decide que fila de condicion de superficie de rodadura "
                      "de la Tabla 12.6.6.3-1 aplica a este corredor: no "
                      "pavimentado, flexible o rigido. La tabla es [C] y "
                      "elegir su fila es [A], el mismo reparto que "
                      "F_PGA_TABLA / 'F_pga' y "
                      "REDUCCION_KH_POR_DESPLAZAMIENTO / "
                      "'factor_muro_eleccion'. La fuente (transcripcion "
                      "completa de las catorce filas en el registro, tabla "
                      "AASHTO_LRFD_9.T12.6.6.3-1; pag. impresa 12-22, leida "
                      "sobre el PDF renderizado) tiene tres columnas -- tipo, "
                      "condicion y cobertura minima -- y las condiciones de "
                      "pavimento son valores de la segunda columna que solo "
                      "aparecen en 2 de los 13 tipos; los otros once llevan "
                      "un guion impreso, de modo que no hay matriz material "
                      "por condicion que buscar. La agrupacion cambia ademas "
                      "con el material: en concreto, no pavimentado y "
                      "pavimento flexible caen en la misma fila; en HDPE la "
                      "fuente agrupa al reves -- vias pavimentadas, sin "
                      "separar flexible de rigido --; en metal corrugado no "
                      "hay condicion de pavimento en absoluto. Por eso el "
                      "criterio conserva las tres opciones y es "
                      "'cobertura_minima_aashto' quien las mapea material por "
                      "material. Lo que las fuentes no resuelven: cual de las "
                      "tres es esta via no lo dice ninguna norma -- lo dice "
                      "la seccion tipica del expediente vial --, y no se "
                      "deduce de lo que ya hay: el CSV (Sec. 1.2) trae cota "
                      "de rasante y cota de subrasante, y su diferencia -- el "
                      "paquete estructural e_paq -- es positiva tambien en un "
                      "afirmado; un paquete no dice si hay carpeta asfaltica "
                      "ni si es losa de concreto. Se adopta declarar la "
                      "condicion en vez de tomar un extremo conservador en "
                      "silencio, porque no hay extremo seguro unico y el "
                      "efecto es grande: en HDPE la fila pavimentada pide "
                      "ID/2 >= 24 in -- 0.75 m para un tubo de 1.50 m -- "
                      "frente a 0.30 m de la no pavimentada, 2.5 veces, y "
                      "elegir la mas exigente por si acaso subiria la rasante "
                      "de todos los puntos sin que nadie pueda rastrear de "
                      "donde salio, que es exactamente lo que CLAUDE.md "
                      "prohibe; en concreto el efecto es el contrario: la "
                      "fila de pavimento rigido pide 9.0 in fijos (0.2286 m), "
                      "menos que las otras dos",
        fuente="PENDIENTE - seccion tipica del expediente vial (Manual de "
               "Diseño Geometrico DG-2018 y el estudio de pavimentos), que fija "
               "el tipo de superficie de rodadura del corredor. Misma "
               "procedencia que 'talud_terraplen'",
        reemplazado_por="Tipo de pavimento de la seccion tipica del proyecto "
                        "vial, o una columna por punto si el corredor cambia de "
                        "superficie a lo largo de sus 5 km",
        sensibilidad=("no_pavimentado", "flexible", "rigido"),
        verificacion_pendiente="Declarar si la condicion es unica para el "
                               "corredor o varia por punto. Se declara como "
                               "criterio de corredor porque la seccion tipica "
                               "lo es; si el expediente trae tramos con "
                               "superficie distinta, pasa a ser columna del CSV",
        resolucion=DeTabla(
            tablas=("AASHTO_LRFD_9.T12.6.6.3-1",),
            que_elige="la fila de condicion de la superficie de rodadura "
                      "sobre el cruce: no pavimentado, flexible o rigido",
        ),
    ),

    "espesor_pared_conducto": Criterio(
        # LA COLUMNA «WALL B» ENTERA DE AASHTO M 170M-04, en metros, por
        # DIAMETRO DESIGNADO en mm -- no un espesor unico por material, que
        # era el modelo equivocado: el espesor de pared depende del diametro,
        # y el bucle de MD recorre el catalogo entero. Con un escalar, un
        # punto que cerrara en 1.20 m se habria calculado con el espesor del
        # de 0.90 m sin que nada avisara; con la columna, un diametro que no
        # este declarado DETIENE el material con su causa.
        #
        # DE DONDE SALEN LOS TRECE NUMEROS DEL CONCRETO. AASHTO M 170M-04,
        # columna «Wall Thickness» de la PARED B, Tabla 2 (Clase II) y Tabla
        # 3 (Clase III), que imprimen los MISMOS espesores para el mismo
        # diametro designado: el espesor lo fija la pared, no la clase, y eso
        # es lo que independiza este criterio de
        # 'clases_producto_por_relleno' (Fase 8), que sigue abierto. Leidos
        # sobre la IMAGEN renderizada del PDF, no sobre su texto: el archivo
        # de normas/ es un escaneo con OCR inservible para tablas. La lectura
        # se cruzo ademas contra la regularidad que las trece filas cumplen
        # sin excepcion, t = D/12 + 25 mm, que reproduce cada valor con el
        # mismo redondeo que imprime la tabla (1050 -> 112.5 -> 113;
        # 1350 -> 137.5 -> 138; 2250 -> 212.5 -> 213).
        #
        # --- T-4 --- EL HDPE Y EL TMC DEJAN DE DESCARTARSE (INF-5.1.17,
        # INF-3.3.4). Hasta T-4 este criterio declaraba SOLO el concreto: el
        # TMC y el HDPE se detenian con `DatoFaltanteError` antes de llegar a
        # 7.A y a V7, y la matriz de materiales degeneraba a concreto.
        #
        #   HDPE  TRES FILAS (900, 1050 y 1200 mm), DERIVADAS de la Table
        #         A12-11 de AASHTO LRFD 9a ed. (`_ESPESOR_HDPE_AASHTO`): el t
        #         que hace D + 2t = «Max. OD» de la fila de 36, 42 y 48 in.
        #         La norma de producto no fija el diametro exterior
        #         (SIN_DIAMETRO_EXTERIOR_M294_TRAD) y esa tabla si. Las filas
        #         de 1350 y 1500 mm NO se declaran: la tabla termina en
        #         48 in y no se extrapola; el material se detiene en ese
        #         escalon nombrando la fila que falta.
        #   TMC   NO SE DECLARA AQUI: su «espesor» es la profundidad de la
        #         corrugacion mas el espesor de la plancha, y cual corrugacion
        #         y cual plancha lo elige 'corrugacion_y_espesor_tmc' [A].
        #         `M2.espesor_pared_de_tmc` lo deriva de ese criterio para
        #         los diametros en que la corrugacion es estandar. Una
        #         entrada «tmc» declarada AQUI manda sobre la derivada (es el
        #         espesor del producto ya especificado, y un dato del
        #         producto no se sustituye por una regla): es por donde la
        #         corrida de pruebas declara su TMC sintetico.
        valor={"concreto_reforzado": {900: 0.100, 1050: 0.113, 1200: 0.125,
                                      1350: 0.138, 1500: 0.150, 1650: 0.163,
                                      1800: 0.175, 1950: 0.188, 2100: 0.200,
                                      2250: 0.213, 2400: 0.225, 2550: 0.238,
                                      2700: 0.250},
               "hdpe": _ESPESOR_HDPE_AASHTO},
        nivel=NIVEL_PERFIL,
        # LA VENTANA ES SIMBOLICA PORQUE LA ELECCION LO ES: M 170M-04 tabula
        # TRES paredes por diametro (A, B y C) y no dice cual usar. La B es la
        # intermedia y la que las tablas imprimen como referencia de diseño;
        # la A daria una clave mas baja y un volumen desplazado menor -- las
        # dos cosas del lado inseguro, que es lo que MAT-D3 y MAT-D4 miden --
        # y la C, mas espesor, seria conservadora en los dos frentes a costa
        # de una rasante mas alta. Un rango numerico no puede defender un
        # valor que es una tabla: lo que se defiende es la COLUMNA elegida.
        sensibilidad=("Concreto: Pared A (AASHTO M 170M-04, Tablas 1 a 5)",
                      "Concreto: Pared B (AASHTO M 170M-04, Tablas 1 a 5) -- "
                      "adoptada",
                      "Concreto: Pared C (AASHTO M 170M-04, Tablas 1 a 5)",
                      "HDPE: el t que da el diametro exterior maximo de la "
                      "Table A12-11 de AASHTO LRFD -- adoptado; o el del "
                      "perfil del fabricante, que no puede ser mayor",
                      "TMC: se elige en 'corrugacion_y_espesor_tmc'"),
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Espesor de pared del conducto por material, en metros: la "
                 "distancia entre la superficie interior y la exterior que "
                 "separa el diametro hidraulico D del diametro exterior "
                 "D_ext = D + 2*t",
        justificacion="Decide el espesor de pared t por material y por "
                      "diametro designado -- la distancia que separa el "
                      "diametro hidraulico D del exterior D_ext = D + 2*t --. "
                      "El catalogo de Sec. 3.2 modela el tubo con un solo "
                      "diametro, el interior, y hay dos sitios donde el que "
                      "hace falta es el exterior. Primero, la clave fisica: "
                      "EG-2013 Subseccion 508.07 mide el relleno minimo "
                      "desde la clave de la tuberia, que es la superficie "
                      "exterior, de modo que calcular la clave como cota de "
                      "entrada + D la deja corta en t. Segundo, el empuje de "
                      "flotacion: el num. 2.4.3.8.2 del Manual de Puentes "
                      "define la subpresion sobre el volumen desplazado, que "
                      "es el exterior; con t = 0.100 m en un tubo de "
                      "concreto de D = 0.90 m, D_ext = 1.10 m y el empuje "
                      "calculado con el diametro interior queda un 33.1 % "
                      "por debajo. Lo que las fuentes no resuelven con un "
                      "numero unico es distinto en cada material. En "
                      "concreto, la norma de producto tabula tres espesores "
                      "por diametro (paredes A, B y C) y no dice cual usar: "
                      "se adopta la pared B, la intermedia. En polietileno "
                      "corrugado, la norma de producto no fija el diametro "
                      "exterior ni la altura del perfil; la tabla de "
                      "propiedades de tuberia corrugada de polietileno del "
                      "apendice de la Seccion 12 de las especificaciones "
                      "LRFD da el diametro exterior maximo del producto para "
                      "cada tamaño nominal hasta 48 in, y se adopta el t que "
                      "lleva el diametro designado hasta ese maximo: "
                      "0.090 m, 0.085 m y 0.099 m para 0.90 m, 1.05 m y "
                      "1.20 m. En metal corrugado el espesor no se declara "
                      "aqui: es la profundidad de la corrugacion mas el "
                      "espesor de la plancha, y los elige otro criterio. En "
                      "los tres materiales un t mayor es el lado conservador "
                      "en los dos sitios: sube la clave y exige mas rasante, "
                      "y sube el empuje de flotacion mas que el peso del "
                      "relleno. Por eso se adopta la pared intermedia del "
                      "concreto y no la mas delgada, y el diametro exterior "
                      "maximo del polietileno y no uno tipico",
        fuente="CONCRETO: AASHTO M 170M-04, Tablas 2 y 3, columna 'Wall "
               "Thickness' de la pared B, leida por imagen (trece filas, 900 "
               "a 2700 mm); la Tabla 5 (Clase V), transcrita en "
               "AASHTO_M170M.T5, coincide en las tres filas que comparte "
               "(900, 1050 y 1200 mm). Las filas de 2850 a 3600 mm de la "
               "serie no se declaran: no se leyeron. HDPE: AASHTO LRFD 9a "
               "ed. (2020), Apendice A12, Table A12-11 'PE Corrugated Pipes "
               "(AASHTO M 294)', pag. impresa 12-108 (PDF 1746), columna "
               "'Max. OD', filas de 36, 42 y 48 in: 42.5, 48.0 y 55.0 in "
               "(tabla y cita AASHTO_LRFD_9.TA12-11). t = (Max. OD x 0.0254 "
               "- D designado) / 2: (1.0795 - 0.900)/2 = 0.08975 m; (1.2192 "
               "- 1.050)/2 = 0.0846 m; (1.3970 - 1.200)/2 = 0.0985 m. La "
               "norma de producto, AASHTO M 294-11 (traduccion no oficial), "
               "NO fija el diametro exterior (afirmacion negativa "
               "SIN_DIAMETRO_EXTERIOR_M294_TRAD) y la tabla de AASHTO LRFD "
               "no trae 54 ni 60 in: las filas de 1350 y 1500 mm siguen sin "
               "fuente. TMC: se deriva de 'corrugacion_y_espesor_tmc' "
               "(AASHTO M 36 Table 1 y num. 8.1.1; ASTM A796 Tables 5, 7 y "
               "9)",
        reemplazado_por="El espesor de pared de la clase, el calibre o el "
                        "perfil efectivamente especificado en el expediente: "
                        "la pared de la clase que resulte de la Fase 8 "
                        "(concreto), y el diametro exterior de la ficha del "
                        "fabricante del perfil (HDPE), que ademas cerraria "
                        "las filas de 1350 y 1500 mm",
        verificacion_pendiente="(1) Las filas de 1350 y 1500 mm del HDPE no "
                               "tienen fuente en normas/: AASHTO LRFD Table "
                               "A12-11 termina en 48 in. El HDPE se detiene "
                               "en esos dos escalones con el dato que falta. "
                               "(2) El t del HDPE sale del diametro exterior "
                               "MAXIMO de una tabla de propiedades de diseño, "
                               "no de un producto: confirmar con la ficha "
                               "del fabricante, que solo puede dar un valor "
                               "menor o igual. (3) La pared del concreto "
                               "depende de la clase que fije la Fase 8 solo "
                               "si esa clase se fabrica con otra pared: "
                               "confirmar al especificar",
        resolucion=Libre(
            que_lo_fija="la clase o el perfil del producto especificado; "
                        "mientras no se especifique, el proyectista adopta "
                        "la pared B de AASHTO M 170M-04 para el concreto y "
                        "el diametro exterior maximo de AASHTO LRFD Table "
                        "A12-11 para el HDPE",
            dominio="m > 0, y menor que el radio interior; una tabla por "
                    "material con el diametro designado en mm como clave",
        ),
    ),

    # ----------------------------------------------------------------------
    # --- T-4 --- (cadena T, 2026-11-11) CUATRO CRITERIOS NUEVOS, al final de
    # la seccion del catalogo: la corrugacion y la plancha del TMC, el tope
    # de la serie de la norma de producto, los umbrales de durabilidad del
    # acero corrugado y el conjunto de suelos de fundacion deficientes.
    # ----------------------------------------------------------------------

    # LA CLAVE ES «corrugacion/espesor» COMO SE IMPRIMEN: «68x13/2.01» es
    # la corrugacion de 68 por 13 mm con plancha de 2.01 mm. Las claves
    # admisibles son las filas de `constantes_normativas.
    # TMC_PLANCHA_CORRUGADA`, que se DERIVA de las Tablas 5, 7 y 9 de
    # ASTM A796 y de la Table 1 de AASHTO M 36: el conjunto cerrado no se
    # escribe a mano.
    #
    # ES BARRIBLE (PF-3): `--barrido corrugacion_y_espesor_tmc=68x13/1.63,
    # 68x13/2.01,68x13/2.77` corre una vez por plancha. Lo que la Fase 8
    # (T-5) consume de la MISMA fila --area, inercia y radio de giro de la
    # seccion-- viaja en la vista de `constantes_normativas`.
    "corrugacion_y_espesor_tmc": Criterio(
        valor="68x13/2.01",
        nivel=NIVEL_PERFIL,         # lo consume M2 al armar el catalogo del
                                    # TMC, que la corrida de perfil recorre
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=_CLAVES_DE_PLANCHA_TMC,
        concepto="Corrugacion y espesor de plancha de la tuberia metalica "
                 "corrugada del catalogo: de ellos sale el diametro "
                 "exterior D_ext = D + 2 x (profundidad de corrugacion + "
                 "espesor de plancha), en que diametros es estandar el "
                 "producto y, en la Fase 8, las propiedades de la seccion",
        justificacion="Decide que producto de tuberia metalica corrugada "
                      "modela el catalogo: la corrugacion y el espesor de la "
                      "plancha. La norma de producto lista siete espesores "
                      "de plancha y cuatro corrugaciones y deja la eleccion "
                      "al comprador, que la hace con el diseño estructural; "
                      "ese diseño es de la Fase 8, que desde T-5 lo hace "
                      "tambien a nivel de perfil. Se adopta la corrugacion de 68 por "
                      "13 mm, que la norma de producto marca como estandar "
                      "de 300 mm a 2100 mm de diametro, con plancha de "
                      "2.01 mm, que es el cuarto de los siete espesores de "
                      "la norma. El unico respaldo de practica disponible es "
                      "de segunda mano y esta declarado como tal en la "
                      "fuente: el expediente de referencia de la tesis, "
                      "segun el informe que lo resume, adopta 2.0 mm con "
                      "esa corrugacion en tuberia de 0.90 m y de 1.20 m. "
                      "Con esa eleccion el diametro exterior es el interior "
                      "mas dos veces 0.015 m. La "
                      "eleccion mueve tres cosas y ninguna es hidraulica: "
                      "el diametro exterior, y con el la clave fisica y el "
                      "empuje de flotacion, en milimetros; el diametro "
                      "maximo del catalogo, porque la corrugacion de 68 por "
                      "13 mm no es estandar por encima de 2100 mm y las de "
                      "25 mm de profundidad lo son hasta 3600 mm; y, en la "
                      "Fase 8, la resistencia de la pared. El coeficiente de "
                      "rugosidad no cambia con esta eleccion: sale de la "
                      "fila de metal corrugado de la Tabla N 09, que no "
                      "distingue corrugaciones. El tope de 2100 mm es el de "
                      "la corrugacion y no el de la plancha: con 2.01 mm de "
                      "espesor el factor de flexibilidad de instalacion en "
                      "terraplen de la norma de diseño estructural, que para "
                      "13 mm de profundidad no puede pasar de 0.245 mm/N, se "
                      "supera desde un diametro de unos 1.39 m, de modo que "
                      "los escalones mayores del catalogo necesitan mas "
                      "espesor u otra corrugacion. Esa comprobacion y la "
                      "eleccion del calibre son de la Fase 8, tambien a "
                      "nivel de perfil; aqui el espesor solo fija la "
                      "envolvente geometrica del tubo",
        fuente="AASHTO M 36-03 (2007): num. 8.1.2 y Table 7 'Thicknesses of "
               "Metallic-Coated Steel Sheet', pags. impresas M 36-10 y "
               "M 36-12 (el comprador elige el espesor de entre 1.02, 1.32, "
               "1.63, 2.01, 2.77, 3.51 y 4.27 mm; cita AASHTO_M36.T7); "
               "Table 1 'Corrugation Requirements', pag. impresa M 36-6 "
               "(las cuatro corrugaciones y la definicion de profundidad; "
               "cita AASHTO_M36.T1); num. 8.1.1, pag. impresa M 36-10 (el "
               "diametro nominal se mide en la cresta interior; cita "
               "AASHTO_M36.8.1.1); Table 6 'Pipe Sizes', pag. impresa "
               "M 36-11 (en que diametros es estandar cada corrugacion; "
               "tabla AASHTO_M36.T6). ASTM A796/A796M-13, Tables 5, 7 y 9 "
               "(propiedades de la seccion por espesor; tablas "
               "ASTM_A796.T5, .T7 y .T9). LA ELECCION NO ESTA EN NINGUNA "
               "NORMA: la Nota 9 de la Table 7 de M 36 remite el espesor al "
               "diseño estructural. RESPALDO DE PRACTICA, de segunda mano: "
               "segun el INFORME de evaluacion de la app (seccion 1.1), que "
               "resume el expediente de referencia de la tesis ('2.7 "
               "Estudio de Estructuras de Obras de Arte y Drenaje', "
               "repositorio VARIOS), su memoria de TMC de 36 y 48 pulgadas "
               "calcula un area requerida que 'espesor 1,6 mm pasa' y "
               "adopta 2,0 mm con corrugacion 68 x 13; la pagina del PDF "
               "original no se verifico en esta sesion: el PDF no esta en "
               "normas/",
        reemplazado_por="La corrugacion y el espesor que resulten del "
                        "diseño estructural de la Fase 8 (ASTM A796 num. 7 a "
                        "11, o AASHTO LRFD Art. 12.7) para la altura de "
                        "relleno real de cada punto, y la disponibilidad "
                        "del producto en el mercado",
        verificacion_pendiente="FACTOR DE FLEXIBILIDAD: ASTM A796/A796M-13, "
                               "num. 10.3 (PDF 4), limita FF = s2/(E I) a "
                               "0.245 mm/N con corrugacion de 13 mm en "
                               "terraplen; con I = 39.20 mm4/mm (Tabla 5, "
                               "2.01 mm) y E = 200 000 MPa el diametro "
                               "limite es raiz(0.245 x 200000 x 39.20) = "
                               "1386 mm. El catalogo ofrece esta plancha "
                               "hasta 2100 mm porque el tope es el de la "
                               "corrugacion; lo cierra la Fase 8. "
                               "Desde T-5 la Fase 8 verifica la plancha punto "
                               "a punto (F8.AREA, F8.COSTURA y F8.FF, por "
                               "AASHTO LRFD 12.7.2) y, si la adoptada no "
                               "alcanza, prueba las mas gruesas de la misma "
                               "corrugacion y AVISA: la envolvente geometrica "
                               "de 7.A y V7 sigue armada con la adoptada, "
                               "donde 1 mm de plancha mueve 2 mm del "
                               "diametro exterior (ficha T5-03)",
        resolucion=Libre(
            que_lo_fija="el proyectista, de entre las corrugaciones y los "
                        "espesores que AASHTO M 36 lista; la norma remite "
                        "la eleccion al diseño estructural",
            dominio="una clave 'corrugacion/espesor' de las tablas de "
                    "propiedades de ASTM A796 (Tables 5, 7 y 9); el "
                    "conjunto cerrado viaja en `sensibilidad`",
        ),
    ),

    # EL TOPE QUE RIGE POR DEFECTO DESDE T-4 (INF-3.3.1): el mayor
    # diametro designado de la SERIE que tabula la norma de producto de
    # cada material. No se escribe: se DERIVA de las tres tablas del
    # registro (`_TOPES_DE_LA_NORMA_DE_PRODUCTO`).
    #
    # PARA EL TMC NO ES EL TOPE EFECTIVO: la serie de AASHTO M 36 llega a
    # 3600 mm, pero cada corrugacion es estandar solo en una parte de
    # ella. `M2.tope_de_diametro` toma el menor entre este tope y el
    # mayor diametro en que la corrugacion adoptada
    # ('corrugacion_y_espesor_tmc') lleva «X» en la Table 6: 2100 mm con
    # 68 por 13 mm.
    "D_max_norma_producto": Criterio(
        valor=_TOPES_DE_LA_NORMA_DE_PRODUCTO,
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Diametro maximo de la serie que tabula la norma de "
                 "producto de cada material, en metros: el tope del "
                 "catalogo de diametros cuando no se declara uno de "
                 "disponibilidad de mercado",
        justificacion="Decide hasta que diametro recorre el catalogo cada "
                      "material: hasta el mayor diametro que su norma de "
                      "producto cubre con un producto definido. En tuberia "
                      "de concreto reforzado son 2.70 m: la serie de "
                      "diametros designados de la norma sigue hasta 3.60 m, "
                      "pero por encima de 2.70 m sus tablas no dan espesor "
                      "de pared ni area de acero y remiten a un diseño "
                      "especial que propone el fabricante y aprueba el "
                      "propietario. En tuberia metalica corrugada y en "
                      "polietileno corrugado es el mayor diametro designado "
                      "de la serie, 3.60 m y 1.50 m. El tope existe por una "
                      "razon de calculo: sin el, la progresion de diametros "
                      "no termina. En tuberia metalica la serie completa no "
                      "esta disponible en cada corrugacion: la norma marca "
                      "en que diametros es estandar cada una, y el tope "
                      "efectivo es el de la corrugacion adoptada, 2.10 m "
                      "con la de 68 por 13 mm. Que el tope sea el de la "
                      "norma no garantiza que el producto se consiga: la "
                      "disponibilidad de mercado se declara aparte y solo "
                      "puede bajarlo",
        fuente="CONCRETO: AASHTO M 170M-04. Mayor diametro con diseño "
               "estandar, 2700 mm: Tabla 1 (Clase I, pag. PDF 3), filas de "
               "1500 a 2700 mm con pared y acero y filas de 2850 a 3450 mm "
               "con llamada a nota y rayas; Tabla 3 (Clase III, pags. PDF 6 "
               "y 7), ultima fila con acero la de 2700 mm. Por encima, num. "
               "7.2.1 y 7.2.2 'Modified and Special Designs', pag. impresa "
               "M 170M-13 (citas AASHTO_M170M.7.2.1 y AASHTO_M170M.7.2.2, "
               "leidas por imagen; el cuerpo de la Tabla 2 y el final de la "
               "Tabla 4 no se leen en el ejemplar). TMC: AASHTO M 36-03 "
               "(2007), Table 6 'Pipe Sizes', pag. impresa M 36-11, de 100 a "
               "3600 mm (tabla AASHTO_M36.T6; coincide con la Tabla 1 de "
               "ASTM A760/A760M-10, ASTM_A760.T1). HDPE: AASHTO M 294-11, "
               "num. 1.1.1 y 7.2.1, tamaños nominales de 300 a 1500 mm "
               "(tabla AASHTO_M294_TRAD.T7.2.2; TRADUCCION NO OFICIAL, sin "
               "firma porque el ejemplar no imprime folio)",
        reemplazado_por="La edicion vigente de cada norma de producto, si "
                        "cambia la serie; para bajar el tope, la "
                        "disponibilidad de mercado declarada en "
                        "'D_max_catalogo'; y, para un tubo de concreto de "
                        "2850 a 3600 mm, el diseño especial aprobado del "
                        "fabricante, con su espesor de pared",
        verificacion_pendiente="El tope del HDPE (1.50 m) se lee de una "
                               "traduccion no oficial de AASHTO M 294-11: "
                               "falta reverificarlo contra el original en "
                               "ingles (FUENTES_AUSENTES['AASHTO_M294']). "
                               "El del concreto se leyo por imagen de las "
                               "Tablas 1 y 3 de AASHTO M 170M-04; el cuerpo "
                               "de la Tabla 2 y el final de la Tabla 4 no "
                               "se leen en el ejemplar",
        resolucion=DeTabla(
            tablas=("AASHTO_M170M.T5", "AASHTO_M36.T6",
                    "AASHTO_M294_TRAD.T7.2.2"),
            que_elige="el mayor diametro que cada norma de producto cubre. "
                      "No hay eleccion del proyectista: en TMC y HDPE es la "
                      "ultima fila de la tabla; en concreto, la ultima fila "
                      "con diseño estandar (2700 mm), que no es la ultima "
                      "de la serie",
        ),
    ),

    # LOS TRES UMBRALES CON QUE LA MATRIZ DE DURABILIDAD DESCARTA EL TMC
    # (`M2.matriz_durabilidad`). Son [C]: la norma peruana solo escribe
    # el umbral de PROTECCION (pH < 5.8, EG-2013 507.10, [N] en
    # `constantes_normativas.PH_MIN_AGUA_TMC_SIN_PROTECCION`), no el de
    # inadmisibilidad. Sin ensayo declarado ninguno de los tres actua.
    "durabilidad_tmc_umbrales": Criterio(
        valor={"pH_min": 5.0, "pH_max": 8.5,
               "resistividad_min_ohm_cm": 1000.0},
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Umbrales de pH y de resistividad del suelo o del agua "
                 "fuera de los cuales la tuberia de acero corrugado deja de "
                 "ser material candidato",
        justificacion="Decide a partir de que pH y de que resistividad la "
                      "matriz de durabilidad retira la tuberia metalica "
                      "corrugada de los materiales candidatos de un punto. "
                      "El Manual de Hidrologia nombra las condiciones que "
                      "corroen una alcantarilla -- suelos y aguas acidos o "
                      "alcalinos, y la conductividad electrica del suelo -- "
                      "y no les pone umbral; las especificaciones generales "
                      "de construccion exigen proteger la tuberia metalica "
                      "cuando el agua tiene pH menor de 5.8, sin prohibir "
                      "el material; y la norma de producto reconoce que hay "
                      "ambientes en que ningun recubrimiento metalico "
                      "basta, sin decir cuales. El vacio se cubre con el "
                      "manual de hidraulica de una agencia vial que si los "
                      "cuantifica: con pH menor de 5.0 o mayor de 8.5, o "
                      "con resistividad menor de 1000 ohm-cm, solo admite "
                      "los materiales de su zona de corrosion severa, que "
                      "son concreto, termoplastico y aluminio. Los umbrales "
                      "son de una agencia de otro pais y de otro clima: se "
                      "adoptan como criterio de descarte porque son los "
                      "unicos escritos, y el proyectista puede "
                      "endurecerlos dentro de la ventana, nunca relajarlos. "
                      "Entre pH 5.0 y 5.8 la tuberia metalica sigue "
                      "candidata con el requisito peruano de proteccion",
        fuente="WSDOT Hydraulics Manual M 23-03.12 (abril 2026): num. 8-5.1 "
               "'pH', pag. impresa 8-25 (PDF 240), cita WSDOT_HM.8-5.1#PH "
               "(pH menor de 5.0 o mayor de 8.5: sitio no apto, solo tubos "
               "de la Zona de Corrosion III); num. 8-5.2 'Resistivity', pag. "
               "impresa 8-26 (PDF 241), cita WSDOT_HM.8-5.2#RESISTIVIDAD "
               "(menos de 1,000 ohm-cm: solo materiales de la Zona III); "
               "num. 8-4.3 'Corrosion Zone III', pag. impresa 8-17 (PDF "
               "232), cita WSDOT_HM.8-4.3#ZONA_III, y su Table 8-3 (pag. "
               "impresa 8-25): concreto, termoplastico y aluminio, ningun "
               "tubo de acero. NORMA PERUANA, que no da estos umbrales: "
               "EG-2013 Subseccion 507.10 (pH < 5.8: proteger; cita "
               "EG2013.507.10) y Manual de Hidrologia num. 4.1.1.3.7 f) y "
               "g) (citas MC_HHD.4.1.1.3.7f#TMC y .7g#AGRESIVAS), "
               "cualitativos. NORMA DE PRODUCTO: AASHTO M 36 num. 1.2 (cita "
               "AASHTO_M36.1.2), sin umbral",
        reemplazado_por="Un estudio de durabilidad del corredor que estime "
                        "la vida util de la tuberia metalica con el pH y la "
                        "resistividad medidos (el propio manual remite al "
                        "metodo del departamento de transporte de "
                        "California), o la especificacion de un "
                        "recubrimiento con vida util garantizada",
        # VENTANA POR CAMPO. pH_min entre el umbral de la fuente tecnica y el
        # de PROTECCION de la norma peruana (5.8): declarar 5.8 es tratar el
        # «será necesario proteger» de EG-2013 como descarte, la lectura mas
        # exigente que una fuente respalda. pH_max y la resistividad no
        # tienen una segunda fuente verificada: su ventana es el dominio en
        # que el umbral conserva sentido (de neutro a la escala entera; de
        # cero a diez veces el valor de la fuente), no una banda de practica.
        #
        # H4 DE LA AUDITORIA DE T-4: LAS TRES VENTANAS SOLO ENDURECEN. La
        # primera version dejaba pH_max hasta 14 y la resistividad minima
        # desde 0, que APAGAN el filtro declarando un valor: la ficha decia
        # «solo se puede endurecer» y la puerta no lo cumplia. Ahora cada
        # ventana va del valor de la fuente hacia el lado exigente: pH_max
        # de neutro al 8.5 de la fuente; resistividad minima del 1000 de la
        # fuente al 3000 ohm-cm con que AASHTO LRFD define el suelo no
        # agresivo para acero galvanizado ('suelo_agresivo_acero_lrfd').
        sensibilidad={"pH_min": (5.0, 5.8), "pH_max": (7.0, 8.5),
                      "resistividad_min_ohm_cm": (1000.0, 3000.0)},
        resolucion=Libre(
            que_lo_fija="el proyectista, adoptando los umbrales del WSDOT "
                        "Hydraulics Manual, que es fuente tecnica reconocida "
                        "y no norma peruana",
            dominio="pH adimensional, de 0 a 14; resistividad en ohm-cm, "
                    "positiva",
        ),
    ),

    # EL CONSUMIDOR QUE `sucs_fundacion` NO TENIA (INF-5.1.9). La columna
    # es obligatoria en el CSV y hasta T-4 no la leia ningun modulo
    # (ficha C6-01 de decisiones_diferidas.md, que dejo dicho por que no
    # se cableaba: el Manual no define «mala calidad»). Lo que T-4 abre
    # NO es un mapeo inventado: es un conjunto DECLARADO, [A], apoyado en
    # la unica lista peruana de suelos que no sirven de apoyo, y produce
    # un AVISO en la memoria -- no cambia material ni seccion --.
    "sucs_fundacion_deficiente": Criterio(
        valor=("OL", "OH", "PT"),
        nivel=NIVEL_PERFIL,         # lo lee `M2.matriz_durabilidad`, que la
                                    # corrida de perfil ejecuta por punto
        etiqueta="A",
        forma=FORMA_SERIE_DE_CLAVES,
        concepto="Grupos de la clasificacion SUCS del suelo de fundacion "
                 "que el proyecto cuenta como deficientes, para avisar de "
                 "que el Manual recomienda en ese caso la alcantarilla tipo "
                 "marco de concreto",
        justificacion="Decide que grupos SUCS del suelo de fundacion "
                      "disparan el aviso de suelo deficiente. El Manual de "
                      "Hidrologia recomienda la alcantarilla tipo marco de "
                      "concreto cuando el suelo de fundacion es de mala "
                      "calidad y no dice que suelo lo es: no da umbral, ni "
                      "clasificacion, ni remision a otra norma. La fuente "
                      "peruana mas cercana es la norma de suelos y "
                      "cimentaciones, que prohibe cimentar sobre turba y "
                      "sobre suelo organico; en su figura de simbolos SUCS "
                      "esos materiales son la turba y los limos y arcillas "
                      "organicos de baja y de alta plasticidad. Se adoptan "
                      "esos tres grupos, que son el conjunto minimo: los "
                      "que una norma peruana excluye como apoyo. Esa norma "
                      "es de edificaciones y no de obras viales, y por eso "
                      "el conjunto es una adopcion y no una exigencia. No "
                      "se añaden las arcillas de alta plasticidad ni los "
                      "limos, que un estudio de suelos puede calificar de "
                      "deficientes por su capacidad portante o su "
                      "asentamiento: ninguna fuente consultada lo dice por "
                      "el solo simbolo, y el proyectista puede declararlos. "
                      "El aviso no cambia el material ni la seccion que el "
                      "calculo adopta",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "4.1.1.3.4 a), pag. impresa 72 (cita "
               "MC_HHD.4.1.1.3.4a#MARCO, condicion "
               "COND-MARCO-SUELO-MALA-CALIDAD): recomienda el marco con "
               "suelos de fundacion de mala calidad, sin definirlos. NTE "
               "E.050 Suelos y Cimentaciones, Art. 24 'Suelos no permitidos "
               "para apoyar las cimentaciones', pag. impresa 37 (cita "
               "E050.24): turba, suelo organico, tierra vegetal y rellenos; "
               "y su Figura 3 'Simbologia de Suelos (Referencial)', pag. "
               "impresa 31 (tabla y cita E050.FIG3): OL, OH y Pt son los "
               "simbolos del suelo organico y de la turba",
        reemplazado_por="El estudio de mecanica de suelos del expediente, "
                        "que califica el suelo de fundacion de cada cruce "
                        "por su capacidad portante y su asentamiento, no "
                        "por su simbolo",
        # LA VENTANA ES EL CONJUNTO DE LOS QUINCE SIMBOLOS de la Figura 3 de
        # la E.050, DERIVADO de la tabla transcrita. Un simbolo doble de
        # frontera («SP-SM», «CL-ML») se compara por sus dos mitades.
        sensibilidad=_SIMBOLOS_SUCS_E050,
        resolucion=DeTabla(
            tablas=("E050.FIG3",),
            que_elige="los simbolos SUCS que cuentan como suelo de "
                      "fundacion deficiente; los tres adoptados son los que "
                      "el Art. 24 de la misma norma no permite como apoyo",
        ),
    ),

    # --- T-4 (auditoria adversarial, H3) --- LOS CRITERIOS ELECTROQUIMICOS
    # DE AASHTO LRFD PARA ACERO GALVANIZADO ENTERRADO, y que hace la matriz
    # de durabilidad con ellos. Son DOS criterios porque son dos preguntas:
    # los NUMEROS son de la fuente ([C]); aplicarlos a una alcantarilla es
    # una analogia, y QUE EFECTO tiene esa analogia sobre el TMC es una
    # eleccion del proyecto ([A]).
    "suelo_agresivo_acero_lrfd": Criterio(
        valor={"pH_min": 5.0, "pH_max": 10.0,
               "resistividad_min_ohm_cm": 3000.0,
               "cloruros_max_ppm": 100.0, "sulfatos_max_ppm": 200.0},
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Criterios electroquimicos del suelo no agresivo para "
                 "acero galvanizado enterrado: intervalo de pH, resistividad "
                 "minima y contenidos maximos de cloruros y de sulfatos",
        justificacion="Decide cuando la matriz de durabilidad considera "
                      "agresivo para la tuberia metalica el suelo de un "
                      "punto con ensayos declarados. La norma peruana de "
                      "construccion exige proteger la tuberia metalica "
                      "cuando los suelos circundantes presentan sustancias "
                      "agresivas y no las cuantifica; la norma de diseño "
                      "adoptada si cuantifica el suelo no agresivo para "
                      "acero galvanizado, aunque lo hace para refuerzos de "
                      "muros y anclajes y no para alcantarillas. El proyecto "
                      "toma esos numeros como la lectura cuantitativa de la "
                      "clausula peruana, por analogia de metal, "
                      "recubrimiento y medio. Basta incumplir uno para que "
                      "el suelo cuente como agresivo. El contenido de "
                      "materia organica, que la fuente limita al 1 por "
                      "ciento, no entra porque no hay dato de entrada que lo "
                      "traiga, y la dispensa que la fuente permite con "
                      "resistividad de 5000 ohm-cm o mas no se aplica, del "
                      "lado seguro. Sin ensayos declarados ninguno actua",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed.: Art. "
               "11.10.6.4.2a 'Steel Reinforcements', pag. impresa 11-89 (PDF "
               "1558), cita AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO: pH de 5 "
               "a 10, resistividad de al menos 3000 ohm-cm, cloruros hasta "
               "100 ppm, sulfatos hasta 200 ppm, materia organica hasta 1 "
               "por ciento; Art. 11.12.8 'Corrosion Protection', pag. "
               "impresa 11-134 (PDF 1603), cita "
               "AASHTO_LRFD_9.11.12.8#AGRESIVO: la misma lista, y que basta "
               "incumplir un criterio. Segunda fuente, menos estricta salvo "
               "en el pH: Art. 10.7.5, pag. impresa 10-125 (PDF 1414), cita "
               "AASHTO_LRFD_9.10.7.5#INDICATIVOS, indicativos para pilotes. "
               "NINGUNO DE LOS TRES ARTICULOS ES DE ALCANTARILLAS: la "
               "aplicacion es por analogia",
        reemplazado_por="Un criterio de agresividad del suelo escrito para "
                        "tuberia de acero corrugado por una norma o un "
                        "manual de drenaje, o el estudio de durabilidad del "
                        "corredor",
        resolucion=Libre(
            que_lo_fija="el proyectista, adoptando por analogia los "
                        "criterios que AASHTO LRFD escribe para refuerzos "
                        "de acero galvanizado enterrados",
            dominio="pH adimensional, de 0 a 14; resistividad en ohm-cm, "
                    "positiva; concentraciones en ppm, no negativas",
        ),
    ),

    "suelo_agresivo_lrfd_sobre_tmc": Criterio(
        valor="aviso",
        nivel=NIVEL_PERFIL,         # lo lee `M2.matriz_durabilidad` cuando
                                    # el punto trae ensayos
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("aviso", "excluye"),
        concepto="Que hace la matriz de durabilidad con la tuberia metalica "
                 "cuando el suelo resulta agresivo segun los criterios de "
                 "acero galvanizado enterrado aplicados por analogia: avisar "
                 "y exigir proteccion, o excluir el material",
        justificacion="Decide si un suelo agresivo segun los criterios "
                      "electroquimicos adoptados por analogia saca a la "
                      "tuberia metalica de los materiales candidatos o solo "
                      "lo advierte. Los criterios son de la norma de diseño "
                      "adoptada, pero estan escritos para refuerzos de muros "
                      "de suelo reforzado y para anclajes, piezas delgadas "
                      "cuya seccion resistente se pierde con la corrosion, "
                      "y no para un tubo que admite proteccion de solera, "
                      "mas espesor o recubrimiento. Por eso el valor del "
                      "archivo es aviso: la exclusion del material se "
                      "reserva a la fuente tecnica que habla de tuberia, por "
                      "pH y por resistividad, y la analogia deja la tuberia "
                      "metalica como candidata con el aviso impreso y con "
                      "la exigencia de proteccion de la norma peruana de "
                      "construccion. La opcion excluye es la lectura "
                      "estricta de la misma analogia y existe para medir "
                      "cuanto cambia el expediente si se adopta: con ella un "
                      "suelo con cloruros o sulfatos sobre el criterio, o "
                      "con resistividad entre 1000 y 3000 ohm-cm, descarta "
                      "el material. Ninguna de las dos mueve un numero de "
                      "calculo: cambia que materiales se evaluan. Sin "
                      "ensayos declarados ninguna actua",
        fuente="NINGUNA FUENTE FIJA ESTE EFECTO. Los criterios son de AASHTO "
               "LRFD 9a ed., Art. 11.10.6.4.2a (pag. impresa 11-89) y Art. "
               "11.12.8 (pag. impresa 11-134), escritos para refuerzos de "
               "acero enterrados; el efecto sobre una alcantarilla metalica "
               "es adopcion del proyecto. La exclusion por pH y por "
               "resistividad con fuente especifica de tuberia esta en "
               "'durabilidad_tmc_umbrales' (WSDOT Hydraulics Manual, num. "
               "8-5.1 y 8-5.2) y la exigencia de proteccion en EG-2013 "
               "507.10",
        reemplazado_por="Un criterio de agresividad escrito para tuberia de "
                        "acero corrugado, que diga que hacer con el material "
                        "y no solo cuando el suelo es agresivo",
        resolucion=Libre(
            que_lo_fija="el proyectista: la fuente define cuando el suelo "
                        "es agresivo para acero galvanizado enterrado y no "
                        "dice que hacer con una alcantarilla",
            dominio="una de las dos opciones: aviso o excluye",
        ),
    ),
}
