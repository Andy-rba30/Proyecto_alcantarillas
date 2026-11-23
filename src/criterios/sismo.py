"""
Fichas de criterios adoptados del dominio: sismo.
"""

from typing import Dict
from src.modelos import DeEnsayo, DeTabla, Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_FLOAT,
    FORMA_SERIE_DE_CLAVES,
    FORMA_STR,
    NIVEL_EXPEDIENTE,
    NIVEL_PERFIL,
)


CRITERIOS: Dict[str, Criterio] = {

    # ----------------------- SISMO: cadena unica -------------------------
    # Se define UNA vez y se propaga a toda verificacion de estabilidad.

    # 'PGA_roca_B' ya no vive aqui: es un dato de sitio [S] -- la lectura de un
    # mapa normativo sobre las coordenadas de esta obra, unica para todo el
    # corredor -- y vive en `datos_sitio.py`. No se declara en dos sitios: la
    # cadena sismica de M9 lo lee de alla.

    "PERFIL_SUELO_PRESUNTO": Criterio(
        valor="S5",
        # NIVEL POR CONSUMIDOR (VE-5, lote catlic): lo lee la Fase 0-bis
        # (`ML.evaluar_licuefaccion`) para decir con que perfil se presume la
        # condicion de suelo de AASHTO 10.5.4.2, y la corrida de perfil
        # difiere ese modulo entero (MODULOS_DIFERIDOS_POR_ALCANCE).
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="S",
        forma=FORMA_STR,
        concepto="Perfil de suelo de E.030 presunto para el sitio (S0-S5)",
        justificacion="Registra que perfil de suelo de E.030 se presume para "
                      "este sitio mientras el ensayo no lo confirme o lo "
                      "cambie. La fuente (E.030, Art. 14.6, Tabla N 2; el "
                      "rotulo literal de su fila S5 viaja en "
                      "constantes_normativas.E030_S5_LECTURA) define el "
                      "esquema de perfiles S0-S5 y sus umbrales. Lo que la "
                      "fuente no resuelve: que letra le toca a este sitio, "
                      "porque eso no es una exigencia normativa con valor "
                      "fijo sino el resultado de aplicar el esquema a las "
                      "condiciones del lugar, y en otra via con otro suelo el "
                      "mismo articulo da otra letra. Se declara S5 como "
                      "presuncion de expediente -- eso dice la palabra del "
                      "nombre --, leida de las condiciones de la llanura del "
                      "Bajo Piura: arenas saturadas, nivel freatico somero, "
                      "suelos potencialmente licuables. La trazabilidad, que "
                      "en un [S] ocupa el lugar de la sensibilidad, esta en "
                      "los campos `resolucion` y `trazabilidad`",
        fuente="E.030 (RM 183-2026-VIVIENDA), Art. 14.6, Tabla N 2, fila S5 "
               "(su rotulo literal viaja en "
               "constantes_normativas.E030_S5_LECTURA), primera vineta "
               "'Suelos potencialmente licuables', pag. impresa 11 (PDF 11). "
               "La Tabla N 3 del num. "
               "14.7 -- la que el num. 14.8 obliga a usar para clasificar -- "
               "NO tiene fila S5, solo S0 a S4: coherente con que la propia "
               "fila diga que 'estos casos no estan cubiertos'",
        reemplazado_por="Ensayo SPT DE LICUEFACCION: perforaciones de al menos "
                        "15 m de profundidad con ensayo cada 1.00 m (E.050 "
                        "Art. 38). Es la profundidad que cierra ESTE criterio "
                        "-- la presuncion de suelo licuable del Art. 14.6 -- y "
                        "no la del criterio 'clase_sitio', que necesita los "
                        "100 ft (30.48 m) del Art. 3.10.3.1 de AASHTO",
        trazabilidad="Clasificacion del Art. 14.6 de E.030 aplicada a la "
                     "caracterizacion geotecnica disponible del corredor "
                     "(llanura del Bajo Piura, distrito de La Union), sin "
                     "ensayo que la cierre. Ambito: todo el corredor mientras "
                     "sea presuncion; con SPT pasa a ser dato por calicata y "
                     "entonces le corresponde una columna del CSV, no esta "
                     "entrada. DESDE VE-5 LO LEE LA FASE 0-bis "
                     "(ML_licuefaccion), que presume con el la condicion de "
                     "suelo de AASHTO 10.5.4.2 mientras el EMS no la "
                     "descarte -- y la clase de sitio de AASHTO no entra en el "
                     "calculo: el criterio 'clase_sitio' es hoy un [S] SIN "
                     "VALOR y lo que la cadena sismica consume es el factor "
                     "'F_pga' --, pero LLAMARLO "
                     "'REFERENCIA MUERTA', como decia este campo, se queda "
                     "muy por debajo de lo que la fuente dice: la fila S5 de "
                     "la Tabla N 2 trae en su ultima vineta la afirmacion "
                     "normativa mas fuerte que el expediente hace sobre este "
                     "sitio -- 'Se prohibe las construcciones apoyadas sobre "
                     "estos perfiles, salvo que, se efectue un estudio "
                     "especifico para el sitio, en el cual se debe considerar "
                     "los mejoramientos en el estrato del perfil'. Es una "
                     "prohibicion CONDICIONADA -- ni bloqueo duro ni "
                     "referencia muerta --, y la memoria imprimia la letra "
                     "sin la consecuencia (NOR-E030-02). Texto literal y "
                     "lectura en constantes_normativas.E030_S5_TEXTO y "
                     "E030_S5_LECTURA; la nota llega a la memoria por "
                     "M9.condicion_normativa_cabezal. Se conserva declarado, "
                     "y no borrado, porque es la presuncion geotecnica que "
                     "sostiene la hipotesis de licuefaccion de Sec. 0.5. Lo "
                     "que YA NO sostiene -- y es la correccion de S13/S14 --, "
                     "es la clase de sitio de AASHTO: son dos taxonomias "
                     "distintas, una por descripcion y otra por rigidez "
                     "medida, y trasladar esta a aquella era justamente el "
                     "salto no escrito (NOR-AAS-02)",
        verificacion_pendiente="Al llegar el SPT, confirmar el perfil y "
                               "decidir si es unico para el tramo o varia por "
                               "calicata; si varia, no se corrige el valor: se "
                               "convierte en columna del CSV",
        resolucion=DeEnsayo(
            ensayo="clasificacion del perfil de suelo de E.030 (S0-S5) "
                   "sobre la caracterizacion geotecnica del corredor",
            trazabilidad_exigida="el EMS del que sale la caracterizacion y "
                                 "la vineta de la Tabla N 2 de E.030 que se "
                                 "leyo; hoy es PRESUNTO y el ensayo lo "
                                 "confirma o lo cambia",
        ),
    ),

    # `clase_sitio` NO es un criterio [A] con valor, y tampoco es un vacio
    # normativo: es un DATO DE SITIO pendiente de ensayo, y por eso pasa a
    # [S] SIN VALOR. La decision, su fundamento y las doce citas verificadas
    # que la sostienen estan en docs/resolucion_clase_sitio.md (S13,
    # conflicto #8); aqui se APLICA y no se reabre.
    #
    # El valor que se retira -- "F_con_factores_tabulados_por_adopcion" --
    # pegaba DOS COSAS DISTINTAS en una sola cadena: una clasificacion que la
    # fuente no sostiene (`F`) y una decision de procedimiento que si es del
    # proyectista (con que filas se lee la tabla mientras el hecho falta). La
    # segunda no desaparece: ya vive, bien etiquetada y con su rango, en
    # 'F_pga'. Separarlas es toda la correccion (NOR-AAS-02, SIS-B-01,
    # SIS-D-01).
    "clase_sitio": Criterio(
        valor=None,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="S",
        forma=FORMA_STR,
        # LAS DOS DISCREPANCIAS QUE ESTE CRITERIO TOCABA -- DIS-HR-CLASE-DE-
        # SITIO-F y DIS-HR-30M-VS-100FT -- viajaron por este campo mientras
        # estuvieron vivas. I2 corrigio la Sec. 0.5 y la Fase 0-bis de la v8
        # y las paso a RESUELTA, y una resuelta no se declara (la guardia
        # `_verificar_discrepancias` lo impide: lo resuelto es material del
        # manifiesto, no de la memoria). El canal queda documentado aqui por
        # si una discrepancia nueva de este criterio lo necesita.
        concepto="Clase de sitio sismica (AASHTO LRFD Art. 3.10.3.1 / Manual "
                 "de Puentes num. 2.4.3.11.2.1.1). Es la rigidez MEDIDA de "
                 "los 100 ft (30.48 m) superiores leida en la tabla de "
                 "definiciones: un hecho del sitio, no una eleccion del "
                 "proyectista. Sin ella la cadena sismica no se detiene, "
                 "porque lo que consume es el factor -- 'F_pga' -- y no la "
                 "clase",
        justificacion="Decide que este expediente no se atribuye ninguna "
                      "clase de sitio, y en particular deja de atribuirse la "
                      "Clase F. No porque la fuente diga que el sitio no lo "
                      "es -- eso lo decide la campana geotecnica --, sino por "
                      "algo mas fuerte: las dos fuentes prohiben suponer la "
                      "clase E o F sin dato geotecnico ni determinacion de la "
                      "autoridad competente, y este expediente no tiene "
                      "ninguna de las dos. La prohibicion es textual en ambas "
                      "y sus Verbatim viven verificados en el registro: la de "
                      "AASHTO al pie de su tabla de definiciones, en la cita "
                      "AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES, y la del Manual de "
                      "Puentes -- que la endurece al traducirla -- en la cita "
                      "MP.2.4.3.11.2.1.1#EXCEPCIONES. Suponer la clase no es "
                      "una adopcion declarable del proyectista: es lo que la "
                      "norma veda. De donde sale la letra que este criterio "
                      "no adopta, y por que no se sostiene: el salto de suelo "
                      "potencialmente licuable a Clase de Sitio F no lo "
                      "escribe ninguno de los dos documentos que este "
                      "criterio invoca -- en las 1905 paginas de AASHTO los "
                      "conjuntos de paginas con `liquef` y con «Site Class F» "
                      "son disjuntos, y en las 673 del Manual la licuefaccion "
                      "vive en cimentaciones y en el Apendice A11, nunca en "
                      "el numeral de clases de sitio. Quien si clasifica los "
                      "suelos licuables en su categoria excepcional es E.030, "
                      "en el perfil S5 de su Tabla N 2, y son dos esquemas "
                      "distintos que discrepan justo en el rasgo que motivaba "
                      "la clasificacion de este sitio -- la discrepancia que "
                      "esto abrio contra la hoja de ruta quedo resuelta en I2 "
                      "al corregirse la Sec. 0.5 de la v8 y vive en el "
                      "manifiesto, y la lectura esta en "
                      "constantes_normativas.E030_S5_VS_CLASE_F. Ademas el "
                      "Art. 10.5.4.2 espera factor de sitio tabulado para un "
                      "sitio licuable -- acota el espectro especifico a no "
                      "menos de dos tercios del general modificado por los "
                      "factores de sitio del Art. 3.10.3.2 (cita "
                      "AASHTO_LRFD_9.10.5.4.2#ESPECTRO) --, cosa imposible si "
                      "la licuefaccion lo hiciera Clase F, porque la fila F "
                      "no da factor. Por que es [S] y no [A]: la regla que "
                      "separa las dos etiquetas es que un [A] se defiende con "
                      "un rango de sensibilidad porque hubo eleccion, y un "
                      "[S] no tiene rango que elegir. La clase de sitio no se "
                      "elige: el Art. 3.10.3.1 la determina por la rigidez "
                      "medida de los 100 ft (30.48 m) superiores, con la "
                      "velocidad de onda de corte como variable primera (cita "
                      "AASHTO_LRFD_9.3.10.3.1), y el paso 3 de la Tabla "
                      "C3.10.3.1-1 da el procedimiento de calculo. Es una "
                      "medicion, y cambia al mover la obra de sitio y no al "
                      "cambiar de proyectista; un valor que no puede declarar "
                      "rango porque la pregunta no esta resuelta no es una "
                      "eleccion: es un hecho que falta. Por que no es un "
                      "vacio normativo: la regla de los vacios gobierna el "
                      "caso en que la norma no fija el valor y hay que "
                      "adoptarlo. Aqui la norma si dice como se determina la "
                      "clase, con que variables y sobre que profundidad, e "
                      "incluso que hacer mientras no se sepa: investigar, y "
                      "no suponer E ni F. Lo que falta no es la regla, es la "
                      "medicion -- y eso es un dato de sitio pendiente de "
                      "ensayo. Lo que el proyecto si elige no desaparece y ya "
                      "esta en su sitio: sobre que filas lee la tabla "
                      "mientras el hecho falta, que es 'F_pga' = (C, D, E), "
                      "[A], con su sensibilidad 0.9-1.0 declarada. Es el "
                      "mismo reparto de siempre -- la tabla es [N], la fila "
                      "es [A] -- y esta clasificacion no lo toca. Queda "
                      "verificado, ademas, que la dispensa por periodo corto "
                      "no existe: ninguna regla de AASHTO permite, por "
                      "periodo fundamental T <= 0.5 s, clasificar como si el "
                      "suelo no licuara -- el barrido sobre las 1905 paginas "
                      "de AASHTO LRFD 9a ed. da cero coincidencias: "
                      "no esta en el Art. 3.10.3.1, ni en su comentario "
                      "C3.10.3.1, ni en ninguna tabla o nota de tabla de "
                      "clases de sitio -- y la Sec. 0.5 de la hoja de ruta v8 "
                      "deja escrita esa misma verificacion",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed. (2020), "
               "Art. 3.10.3.1 «Site Class Definitions» y su Tabla 3.10.3.1-1 "
               "(pag. impresa 3-101 y 3-102); Manual de Puentes (MTC), num. "
               "2.4.3.11.2.1.1 «Definiciones de Clases de Sitio» y su Tabla "
               "2.4.3.11.2.1.1-1 (pag. impresa 122). Las dos definen la clase "
               "y las dos prohiben suponer E o F sin dato. Citas verificadas "
               "en el registro: AASHTO_LRFD_9.3.10.3.1, "
               "AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES, "
               "MP.2.4.3.11.2.1.1#EXCEPCIONES, AASHTO_LRFD_9.T3.10.3.1-1#F y "
               "E030.T2#S5. La fuente NO da el valor: da el procedimiento "
               "para medirlo",
        trazabilidad="NO SE HA EJECUTADO NINGUNA LECTURA: este [S] esta "
                     "vacio, y eso es lo que la memoria declara. "
                     "COMO SE REPRODUCIRA cuando el ensayo exista, en el "
                     "orden en que la fuente lo escribe: (1) caracterizar los "
                     "100 ft (30.48 m) superiores del perfil bajo el nivel de "
                     "cimentacion del cabezal, obteniendo v_s, N o s_u; "
                     "(2) promediarlos por el procedimiento del paso 3 de la "
                     "Tabla C3.10.3.1-1, que es media armonica ponderada por "
                     "espesor y no media aritmetica; (3) entrar con ese "
                     "promedio en la Tabla 3.10.3.1-1 (equivalente: Tabla "
                     "2.4.3.11.2.1.1-1 del Manual, pag. impresa 122) y leer "
                     "la letra; (4) antes de esos tres pasos, comprobar la "
                     "fila F, que el paso 1 de la misma tabla manda mirar "
                     "primero. "
                     "ALCANCE: es un dato DE CORREDOR mientras el perfil "
                     "geotecnico no muestre variacion, no un dato por punto; "
                     "si la campana devuelve columnas distintas entre "
                     "progresivas, deja de serlo y pasa a columna del CSV. "
                     "QUIEN LO FIRMA: el estudio de mecanica de suelos del "
                     "expediente. Este archivo no lo puede rellenar por "
                     "analogia ni por presuncion, y esa es toda la diferencia "
                     "con 'PERFIL_SUELO_PRESUNTO', que si conserva valor: "
                     "aquel perfil se alcanza por DESCRIPCION -- la Tabla "
                     "N 2 de E.030 tiene columna «Descripcion» y su fila S5 "
                     "es una lista de condiciones cualitativas -- y este se "
                     "alcanza por NUMEROS que nadie ha medido. Una se puede "
                     "presumir declarandolo; la otra la norma prohibe "
                     "presumirla",
        reemplazado_por="DOS ENSAYOS DE PROFUNDIDADES DISTINTAS, que conviene "
                        "pedir juntos al programar la campana geotecnica. "
                        "(1) LA CARACTERIZACION DE LOS 100 ft (30.48 m) "
                        "SUPERIORES -- Vs30 o N_barra --, que es la "
                        "profundidad que el Art. 3.10.3.1 escribe («the upper "
                        "100 ft») y con la que se lee la clase. La hoja de "
                        "ruta pedia «30 m» y se lo atribuia al articulado -- "
                        "el numeral no imprime esa cifra --; la discrepancia "
                        "que eso abrio viajo por el campo `discrepancias` de "
                        "este criterio mientras estuvo viva, y quedo resuelta "
                        "en I2 al escribir la v8 la profundidad del "
                        "articulado (Sec. 0.5 y Tablero 3.6). "
                        "Los 30.48 m son "
                        "parte de la DEFINICION de la clase: una clase leida "
                        "sobre menos profundidad no es la misma variable. "
                        "(2) SI ESA CARACTERIZACION DIERA CLASE F, el "
                        "ANALISIS DE RESPUESTA DINAMICA DE SITIO, que el "
                        "Art. 3.10.2 exige con «shall» -- «A Site-Specific "
                        "Procedure shall be used if any one of the following "
                        "conditions exist» -- y el num. 2.4.3.11.2 del Manual "
                        "con «sera usado». La exigencia se ancla ahi, en el "
                        "articulado, y no en la Nota 2 al pie de la tabla de "
                        "factores, que es donde el repositorio la anclaba: la "
                        "nota la repite, no la funda. "
                        "NO LO CIERRA el SPT de 15 m de E.050 Art. 38: ese "
                        "ensayo responde a la pregunta de licuefaccion "
                        "(criterio 'PERFIL_SUELO_PRESUNTO') y se detiene a "
                        "mitad de la columna que esta clase necesita",
        # NO SE INTERPONE, Y DESDE VE-5 (lote catlic) TIENE CONSUMIDOR: la
        # Fase 0-bis (`ML.contrastar_clase_sitio`) lo lee con
        # `valor_si_declarado`, de modo que sin valor la cadena sismica sigue
        # con 'F_pga' y nada se detiene (el vacio se DECLARA, SIS-B-01); con
        # la clase medida, la contrasta con las filas de 'F_pga': la fila F
        # es metodo no evaluable (Art. 3.10.2), una clase fuera de las filas
        # es dato invalido sobre 'F_pga', y dentro de varias, un aviso.
        resolucion=DeEnsayo(
            ensayo="medicion de la rigidez de los 30.48 m superiores (Vs30, "
                   "N o su) segun AASHTO Art. 3.10.3.1",
            trazabilidad_exigida="el ensayo geofisico o geotecnico, su "
                                 "profundidad y el laboratorio; una clase de "
                                 "sitio DECLARADA sin medicion no es una "
                                 "clase de sitio",
        ),
    ),

    # F_pga deja de guardar el RESULTADO y pasa a guardar la ELECCION, que es
    # el reparto R1 del proyecto (la tabla es [N], la fila es [A]) y el mismo
    # movimiento que ya se hizo con 'factores_carga_aashto' en C03. Un 1.0
    # suelto no dice de que filas salio, no se recalcula cuando la campana
    # geotecnica cierre la clase, y hacia invisibles tres cosas que la tabla
    # si dice (NOR-PUE-09, NOR-PUE-11, NOR-MEM-03, MAT-O4, NOR-PUE-12).
    "F_pga": Criterio(
        valor=("C", "D", "E"),
        # NIVEL MEDIDO, no opinado: lo invoca la corrida `--alcance expediente`
        # de `tests/test_nivel_medido.py` y NO la de `--alcance perfil`, que
        # difiere la Fase 9 entera. Ese test contrasta las dos corridas en LAS
        # DOS DIRECCIONES, de modo que este campo no puede quedar
        # desincronizado del codigo: si algun dia la corrida de perfil lo
        # invocara sin diferirlo, la suite se pone roja aqui.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_SERIE_DE_CLAVES,
        # DIS-HR-30M-VS-100FT viajo por este campo mientras estuvo viva --
        # la profundidad sobre la que se lee la clase decide que fila de esta
        # tabla aplica, y la hoja de ruta se la atribuia al articulado con una
        # cifra que el articulado no imprime --. I2 corrigio la v8 y la paso a
        # RESUELTA: lo resuelto es material del manifiesto, no de la memoria,
        # y la guardia rechaza declararlo aqui.
        concepto="Filas de la Tabla 2.4.3.11.2.1.2-1 sobre las que se lee el "
                 "factor de sitio de la cadena sismica. El factor adoptado es "
                 "la ENVOLVENTE (el mayor) de esas filas al PGA del proyecto; "
                 "hoy vale 1.0",
        justificacion="Decide sobre que filas de la tabla se lee el factor de "
                      "sitio de la cadena sismica. La clase de sitio esta "
                      "indeterminada -- ver 'clase_sitio', que es un [S] sin "
                      "valor -- y por eso lo que se declara es el conjunto de "
                      "filas plausibles y no una. La fuente (la tabla "
                      "MP.TFPGA del registro, transcrita completa con sus dos "
                      "notas al pie) da los factores por clase de sitio y por "
                      "columna de PGA, y esos valores son [N]. Lo que la "
                      "fuente no resuelve: que filas describen a este sitio, "
                      "porque eso depende de la medicion que falta; esa "
                      "eleccion de filas es [A] y es lo unico que este "
                      "criterio decide. Se adopta el conjunto (C, D, E) y el "
                      "factor es la envolvente (el mayor) de esas filas al "
                      "PGA del proyecto: la tabla da 1.0 para C, 1.0 para D y "
                      "0.9 para E, de modo que el factor adoptado es 1.0, "
                      "conservador o exacto frente a las tres. Las filas que "
                      "no se declaran, y por que. (a) A y B son las filas de "
                      "roca (0.8 y 1.0): quedan fuera porque la cimentacion "
                      "es la llanura arenosa del Bajo Piura, y esa exclusion "
                      "no es cosmetica -- el num. 2.8.1.1.14.2.1 da a las "
                      "cimentaciones en Clase A o B una expresion distinta de "
                      "k_h0 (1.2*F_pga*PGA en vez de A_s), de modo que "
                      "declarar C/D/E es lo que descarta esa rama de forma "
                      "trazable. (b) La fila F no esta entre las leidas, "
                      "dicho con precision para que no se lea al reves: no "
                      "porque se haya descartado que el sitio sea Clase F -- "
                      "eso lo decide la campana geotecnica --, sino por dos "
                      "razones que valen hoy. La primera, que esa fila no da "
                      "factor: la tabla le pone asterisco en las cinco "
                      "columnas y su Nota 2 -- Verbatim de MP.TFPGA en el "
                      "registro -- exige investigacion geotecnica especifica "
                      "del sitio y analisis de respuesta dinamica de sitio; "
                      "elegirla no seria leer un valor, seria leer una "
                      "exigencia de estudio. La segunda, que suponerla esta "
                      "expresamente vedado mientras no haya dato geotecnico "
                      "ni determinacion de la Entidad (citas "
                      "AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES y "
                      "MP.2.4.3.11.2.1.1#EXCEPCIONES del registro). Si la "
                      "campana devolviera Clase F, no queda fila con factor: "
                      "queda el estudio de respuesta dinamica que exige el "
                      "Art. 3.10.2, y esta memoria no podria cerrarse sin el. "
                      "Alcance de lo conservador, sin coartada: los factores "
                      "tabulados permiten dimensionar el elemento estructural "
                      "dentro del marco tabulado; no constituyen una "
                      "evaluacion del riesgo de licuefaccion, que sigue "
                      "siendo el condicionante tecnico no resuelto del "
                      "proyecto, y los efectos de la licuefaccion -- perdida "
                      "de resistencia, asentamiento, desplazamiento lateral "
                      "-- quedan fuera del alcance de este calculo y "
                      "remitidos al estudio geotecnico del expediente. Un "
                      "analisis de respuesta especifica de sitio puede "
                      "arrojar valores mayores que los tabulados: la adopcion "
                      "no es conservadora por construccion, y por eso la "
                      "eleccion de filas es [A] y no [N->]. La sensibilidad "
                      "-- 0.9 a 1.0 al PGA de este proyecto, con la lectura "
                      "declarada en 'F_pga_lectura_columna_extrema' -- va en "
                      "su campo, que ademas explica por que ese es todo el "
                      "rango alcanzable",
        fuente="Manual de Puentes (MTC), Tabla 2.4.3.11.2.1.2-1 (Tabla "
               "3.10.3.2-1 AASHTO), pag. impresa 123 (PDF 124), transcrita "
               "COMPLETA -- seis filas y cinco columnas, con sus dos notas al "
               "pie -- en constantes_normativas.F_PGA_TABLA. Los valores son "
               "[N]; QUE FILAS describen a este sitio es [A] y es lo unico "
               "que se declara aqui",
        reemplazado_por="Caracterizacion de sitio sobre los 100 ft "
                        "(30.48 m) superiores -- Vs30 o N_barra --, que "
                        "cierra 'clase_sitio' y deja una sola fila. La "
                        "profundidad es la que imprime el Art. 3.10.3.1 «the "
                        "upper 100 ft»; la hoja de ruta decia «30 m» "
                        "atribuyendoselo al articulado, y esa discrepancia "
                        "quedo resuelta en I2 al corregirse la v8 (Sec. 0.5 "
                        "y Tablero 3.6) -- la historia, en el manifiesto. Si "
                        "esa "
                        "caracterizacion diera Clase F, no queda fila con "
                        "factor: queda el ANALISIS DE RESPUESTA DINAMICA DE "
                        "SITIO que exige el Art. 3.10.2 con «shall» y el num. "
                        "2.4.3.11.2 del Manual con «sera usado». La Nota 2 al "
                        "pie de esta tabla lo repite; no lo funda, y anclarlo "
                        "ahi dejaba la exigencia colgando de una nota",
        sensibilidad="entre 0.9 (fila E) y 1.0 (filas C y D) al PGA de este "
                     "proyecto, con la lectura declarada en "
                     "'F_pga_lectura_columna_extrema'. Ese es TODO el rango "
                     "alcanzable: la otra lectura declarable, "
                     "'limite_estricto', no lee la columna anterior sino que "
                     "DETIENE el calculo, porque con los rotulos leidos al "
                     "pie de la letra en PGA = 0.50 no hay columna ni hay dos "
                     "valores entre los que interpolar. El 1.1 de la fila D "
                     "en la columna PGA = 0.40 existe en la tabla y NO es "
                     "alcanzable por ninguna declaracion de este proyecto: "
                     "llegar a el exigiria una tercera lectura -- extrapolar "
                     "desde la columna anterior -- que no se declara porque "
                     "no la sostiene la Nota 1, que habla de interpolar entre "
                     "valores y no de extrapolar mas alla del ultimo",
        resolucion=DeTabla(
            tablas=("MP.TFPGA",),
            que_elige="las filas de clase de sitio sobre las que se lee "
                      "F_pga; el factor adoptado es la envolvente (el mayor) "
                      "de las filas elegidas",
        ),
    ),

    # La tabla se lee por columnas de PGA y sus dos rotulos extremos son
    # DESIGUALDADES ESTRICTAS: "PGA < 0.10" y "PGA > 0.50". El PGA de este
    # proyecto es exactamente 0.50 y no cae en ninguna columna tabulada
    # (NOR-PUE-11). La tabla no resuelve ese borde; lo resuelve quien la lee, y
    # por eso es criterio y no constante.
    #
    # R3 verifico la Nota 1 contra la pagina renderizada preguntandole si
    # resuelve el borde -- lo que habria bajado la etiqueta a [N] o [N->] --
    # y no lo resuelve: manda interpolar para valores intermedios sin nombrar
    # los nodos, y sobre el PGA exactamente igual al rotulo extremo calla.
    # El barrido esta fijado en citas.SIN_REGLA_DE_BORDE_EN_TFPGA, anclado a
    # la tabla MP.TFPGA, y la etiqueta queda [A].
    "F_pga_lectura_columna_extrema": Criterio(
        valor="limite_inclusive",
        # NIVEL MEDIDO, no opinado: lo invoca la corrida `--alcance expediente`
        # de `tests/test_nivel_medido.py` y NO la de `--alcance perfil`, que
        # difiere la Fase 9 entera. Ese test contrasta las dos corridas en LAS
        # DOS DIRECCIONES, de modo que este campo no puede quedar
        # desincronizado del codigo: si algun dia la corrida de perfil lo
        # invocara sin diferirlo, la suite se pone roja aqui.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        concepto="Como se leen los dos rotulos extremos de la Tabla "
                 "2.4.3.11.2.1.2-1 cuando el PGA cae justo sobre uno de ellos",
        justificacion="Decide como se leen los dos rotulos extremos de "
                      "columna de la tabla cuando el PGA cae exactamente "
                      "sobre uno de ellos. Lo que la fuente dice (tabla "
                      "MP.TFPGA del registro, verificada sobre la pagina "
                      "renderizada): su Nota 1 manda interpolar en linea "
                      "recta para valores intermedios de PGA, y sus dos "
                      "rotulos extremos son desigualdades estrictas. Lo que "
                      "no resuelve, con el barrido fijado en la "
                      "AfirmacionNegativa SIN_REGLA_DE_BORDE_EN_TFPGA del "
                      "registro: la nota no nombra los puntos entre los que "
                      "se interpola -- leer los cinco numeros de los rotulos "
                      "como esos nodos es ya lectura del proyecto, no texto "
                      "de la fuente --, y ni ella, ni los rotulos, ni el "
                      "articulado del numeral dicen como se lee un PGA "
                      "exactamente igual al rotulo extremo, de modo que 0.50 "
                      "no esta cubierto por ninguna columna ni queda entre "
                      "dos. Ese silencio es el que mantiene la etiqueta en "
                      "[A]: la eleccion no se apoya en una disposicion que "
                      "tome la decision, sino en el criterio del proyectista "
                      "sobre un vacio barrido. Se adopta 'limite_inclusive': "
                      "la columna 'PGA > 0.50' aplica tambien en 0.50, por "
                      "ser el valor a partir del cual la fuente deja de "
                      "variar el factor -- las filas C, D y E repiten ahi el "
                      "ultimo numero o lo bajan, ninguna lo sube -- y por "
                      "continuidad con la interpolacion que la nota si "
                      "manda, cuyo ultimo tramo solo puede rematar en el "
                      "valor de esa columna. La lectura no es neutra y por "
                      "eso se declara: con 'limite_estricto' el calculo se "
                      "detiene en vez de elegir columna, y si en su lugar se "
                      "leyera la columna anterior (PGA = 0.40) la fila D "
                      "daria 1.1 en vez de 1.0 y la envolvente subiria un "
                      "10 %, arrastrando toda la cadena sismica",
        fuente="Manual de Puentes (MTC), Tabla 2.4.3.11.2.1.2-1, rotulos de "
               "columna y Nota 1, pag. impresa 123 (PDF 124). La tabla NO "
               "resuelve el borde -- el barrido que lo sostiene esta en la "
               "AfirmacionNegativa SIN_REGLA_DE_BORDE_EN_TFPGA del registro, "
               "anclada a la propia tabla --: la lectura es del proyectista",
        reemplazado_por="Un PGA de proyecto que caiga dentro de una columna, "
                        "o el estudio de respuesta de sitio, que sustituye la "
                        "tabla entera",
        sensibilidad=("limite_inclusive", "limite_estricto"),
        verificacion_pendiente="Al registrar las coordenadas de la lectura "
                               "del PGA (pendiente 1.4), comprobar si el "
                               "valor sigue siendo exactamente 0.50: si "
                               "cayera dentro de una columna, este criterio "
                               "deja de gobernar nada y se retira",
        resolucion=DeTabla(
            tablas=("MP.TFPGA",),
            que_elige="como se leen los dos rotulos extremos de columna "
                      "cuando el PGA cae justo sobre uno de ellos",
            laguna="los rotulos extremos se imprimen con < y >, de modo que "
                   "la tabla no dice a que columna pertenece el PGA que cae "
                   "exactamente en el limite. La eleccion es del proyectista",
        ),
    ),

    # No es una fila de una tabla: el num. 2.8.1.1.14.2.2 no presenta ninguna
    # tabla y fija UN valor, 0.5, de forma permisiva. Lo que se declara es si
    # se aplica o no esa reduccion (NOR-PUE-07).
    "factor_muro_eleccion": Criterio(
        valor="sin_reduccion",
        # NIVEL MEDIDO, no opinado: lo invoca la corrida `--alcance expediente`
        # de `tests/test_nivel_medido.py` y NO la de `--alcance perfil`, que
        # difiere la Fase 9 entera. Ese test contrasta las dos corridas en LAS
        # DOS DIRECCIONES, de modo que este campo no puede quedar
        # desincronizado del codigo: si algun dia la corrida de perfil lo
        # invocara sin diferirlo, la suite se pone roja aqui.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        concepto="Si se aplica al cabezal la reduccion de k_h0 que el numeral "
                 "autoriza para muros con desplazamiento lateral admitido",
        justificacion="Decide si se aplica al cabezal la reduccion de k_h0 "
                      "que el num. 2.8.1.1.14.2.2 autoriza para muros que "
                      "admiten desplazamiento lateral. La fuente (texto "
                      "literal en constantes_normativas.REDUCCION_KH_TEXTO; "
                      "las tres condiciones que AASHTO acumula, en "
                      "REDUCCION_KH_CONDICIONES) autoriza reducir k_h a la "
                      "mitad de k_h0 -- autoriza, no manda: el verbo del "
                      "numeral es potestativo -- y define k_h0 como la "
                      "aceleracion con desplazamiento nulo del muro. Lo que "
                      "la fuente no resuelve: si este cabezal admite ese "
                      "desplazamiento; y la autorizacion no es solo tecnica "
                      "-- AASHTO, del que el numeral es traduccion, la "
                      "condiciona a que el movimiento lateral sea aceptable "
                      "para el propietario, lo que la deja fuera del alcance "
                      "de un calculo. Se adopta sin reduccion, k_h = k_h0: el "
                      "cabezal va empotrado en el terraplen y no tiene "
                      "desplazamiento lateral admisible garantizado, y el "
                      "programa no asume la aceptacion del Propietario -- la "
                      "Sec. 9.2 de la hoja de ruta (corregida, ficha VE3-20) "
                      "pide declarar la reduccion por obra -- y es el lado "
                      "conservador, con el coste que la Sec. 9.2 declara: "
                      "k_h0 es el desplazamiento nulo y con el ningun "
                      "cabezal del juego de la validacion integral cierra el "
                      "sismo. Por que esto es [A] y no la eleccion de "
                      "una fila [N]: el numeral no tabula nada -- autoriza "
                      "una reduccion, y el 1.0 no es un valor tabulado sino "
                      "la ausencia de reduccion, que es la definicion misma "
                      "de k_h0. Las dos declaraciones posibles estan en el "
                      "campo `sensibilidad`. Un solo regimen (decision 12 "
                      "del dueño): la reduccion supone un muro que cede, y "
                      "solo se acepta declarada junto con "
                      "'regimen_resistencia_elementos_cabezal' = «cedente»; "
                      "con el armado en reposo la corrida la rechaza. "
                      "Declararla pide justificar que los aleros llevan "
                      "junta, que el Propietario acepta el desplazamiento y "
                      "que la pantalla supera la altura con que C3.11.5.2 da "
                      "por movilizado el empuje activo de un muro en "
                      "voladizo",
        fuente="Manual de Puentes (MTC) num. 2.8.1.1.14.2.2 'Estimacion de la "
               "Aceleracion que Actua Sobre la Masa del Muro' (11.6.5.2.2 "
               "AASHTO), pag. impresa 255 (PDF 256). Texto literal y las tres "
               "condiciones que AASHTO acumula, en "
               "constantes_normativas.REDUCCION_KH_TEXTO y "
               "REDUCCION_KH_CONDICIONES. El unico numero [N] del numeral es "
               "el 0.5",
        reemplazado_por="Diseno de detalle del cabezal que garantice (o "
                        "descarte) un desplazamiento lateral de 1.0 a 2.0 in "
                        "o mas, mas la aceptacion del propietario",
        sensibilidad=("sin_reduccion", "reduccion_por_desplazamiento"),
        verificacion_pendiente="El repositorio convertia el rango del Manual "
                               "('1.0 a 2.0 in o mas') en '25-50 mm', que "
                               "redondea y ademas pierde el 'o mas': un muro "
                               "con 60 mm de desplazamiento admisible quedaba "
                               "fuera del rango escrito y si califica. Si "
                               "alguna vez se declara la reduccion, "
                               "contrastar contra "
                               "DESPLAZAMIENTO_HABILITA_REDUCCION_M y no "
                               "contra el rango redondeado",
        resolucion=Libre(
            que_lo_fija="el proyectista, declarando si el cabezal admite el "
                        "desplazamiento lateral que la reduccion supone. NO "
                        "es `DeTabla`, aunque la Sec. 4.3 del plan lo ponga "
                        "de ejemplo: el num. 2.8.1.1.14.2.2 NO TABULA NADA "
                        "-- autoriza una reduccion -- y el 1.0 no es una "
                        "fila sino la ausencia de reduccion, que es la "
                        "definicion misma de k_h0",
            dominio="declaracion entre los dos regimenes del numeral",
        ),
    ),

    # k_v no es una adopcion: lo fija el mismo numeral del que la cadena toma
    # k_h0. Lo que se declara aqui es si se da alguno de los dos casos que ese
    # numeral reserva -- y no es un matiz de redaccion: la fuente que este
    # criterio citaba ('practica corriente; no fijado por el Manual de
    # Puentes') afirmaba lo contrario de lo que dice el Manual (NOR-PUE-08,
    # MAT-O11, MAT-X4).
    "k_v": Criterio(
        valor="prescrito_sin_caso_reservado",
        # NIVEL MEDIDO, no opinado: lo invoca la corrida `--alcance expediente`
        # de `tests/test_nivel_medido.py` y NO la de `--alcance perfil`, que
        # difiere la Fase 9 entera. Ese test contrasta las dos corridas en LAS
        # DOS DIRECCIONES, de modo que este campo no puede quedar
        # desincronizado del codigo: si algun dia la corrida de perfil lo
        # invocara sin diferirlo, la suite se pone roja aqui.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=(FORMA_STR, FORMA_FLOAT),
        concepto="Cual de los dos regimenes de k_v del num. 2.8.1.1.14.2.1 "
                 "rige en este cabezal. Con el declarado, k_v = 0.0 y ese "
                 "cero es [N], no una adopcion",
        justificacion="Decide cual de los dos regimenes de k_v del num. "
                      "2.8.1.1.14.2.1 rige en este cabezal. La fuente (texto "
                      "literal en constantes_normativas.K_V_TEXTO; el alcance "
                      "de los casos reservados, en K_V_CASO_RESERVADO) fija "
                      "k_v = 0 para el calculo de presiones laterales y "
                      "reserva dos casos: muro significativamente afectado "
                      "por efectos de alguna falla cercana, y aceleraciones "
                      "verticales relativamente altas actuando "
                      "simultaneamente con la horizontal. Lo que la fuente no "
                      "resuelve: no cuantifica ninguno de los dos casos -- no "
                      "da distancia a la falla, no define la cercania, no "
                      "fija umbral de aceleracion vertical -- y para ellos "
                      "tampoco escribe un k_v alternativo. Se declara que "
                      "ninguno de los dos se da en este cabezal, con lo que "
                      "rige el cero prescrito: con el regimen declarado, el "
                      "k_v = 0 que resulta es [N] y no una adopcion. Si "
                      "alguno de los casos se diera, este criterio admite "
                      "entonces un numero en lugar de la declaracion, y ese "
                      "numero seria del proyectista, porque el Manual no lo "
                      "da: el valor por defecto es normativo y el del caso "
                      "reservado no existe en la fuente. Por eso el campo "
                      "`sensibilidad` declara los dos regimenes y no un rango "
                      "numerico: un rango sugeriria una libertad que el "
                      "numeral no concede -- el cero es prescrito, no elegido",
        fuente="Manual de Puentes (MTC) num. 2.8.1.1.14.2.1 'Caracterizacion "
               "de la Aceleracion en la Base del Muro de Contencion' "
               "(11.6.5.2.1 AASHTO), pag. impresa 254 (PDF 255), reiterado en "
               "el num. 2.8.1.1.14.3 (pag. impresa 255). Texto literal en "
               "constantes_normativas.K_V_TEXTO; el alcance de los dos casos "
               "reservados, en K_V_CASO_RESERVADO",
        reemplazado_por="Evaluacion neotectonica del corredor que descarte o "
                        "confirme falla activa proxima, dentro del estudio "
                        "geotecnico del expediente",
        sensibilidad=("prescrito_sin_caso_reservado",
                      "un k_v declarado por el proyectista para el caso que "
                      "el numeral reserva y no cuantifica"),
        verificacion_pendiente="El Manual no cuantifica 'falla cercana'. "
                               "AASHTO si, pero en otro articulo y sobre un "
                               "mapa que no cubre el Peru: su Art. 3.10.2.2 "
                               "(pag. impresa 3-100) habla de sitios a menos "
                               "de 6 millas de una falla activa superficial o "
                               "somera segun el USGS Active Fault Map. "
                               "Mientras el expediente no traiga la "
                               "evaluacion neotectonica equivalente, esta "
                               "declaracion se apoya en la ausencia de "
                               "hallazgo, no en un hallazgo de ausencia, y "
                               "hay que decirlo asi en la memoria",
        resolucion=Libre(
            que_lo_fija="el proyectista, declarando cual de los dos "
                        "regimenes del num. 2.8.1.1.14.2.1 rige. Con el "
                        "regimen prescrito declarado, el k_v = 0 que resulta "
                        "es [N] y no una adopcion; para el caso reservado el "
                        "numeral no escribe ningun k_v alternativo",
            dominio="declaracion de regimen, o k_v adimensional del "
                    "proyectista en el caso reservado",
        ),
    ),

    # gamma_EQ existia como PROSA dentro de la verificacion pendiente de
    # 'factores_carga_aashto' -- "sigue sin valor y bloquea esa combinacion" --
    # y no como vacio declarado, de modo que nada podia detenerse en el. Ahora
    # es entrada propia porque la cadena sismica lo NECESITA en dos sitios: la
    # combinacion Evento Extremo I y, sobre todo, el limite de excentricidad
    # de la resultante en la base, que va de B/6 a 0.4*B segun su valor
    # (MAT-O16).
    "gamma_EQ": Criterio(
        # --- T-7b --- DEJA DE SER UN VACIO. Hasta T-7b valia None «porque
        # adoptar cualquiera de las dos cifras del comentario en silencio
        # seria rellenar el vacio». El encargo de T-7b lo cierra con un valor
        # DECLARADO y su ventana entera: 0.50, que es la unica cifra que la
        # fuente califica de razonable, con 0.0 a 1.0 barrible. No es [C]: el
        # articulo manda determinarlo por proyecto.
        valor=0.5,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Factor de carga de la carga viva en la combinacion Evento "
                 "Extremo I, adimensional",
        justificacion="Decide cuanta sobrecarga viva de trafico acompaña al "
                      "sismo en la combinacion Evento Extremo I del cabezal, "
                      "y con ella el limite de excentricidad sismico. La "
                      "fuente (AASHTO Art. 3.4.1; texto literal en "
                      "constantes_normativas.GAMMA_EQ_TEXTO; via Manual de "
                      "Puentes, Tabla 2.4.5.3.1-1) imprime el simbolo "
                      "gamma_EQ en la columna de LS, no un numero, y manda "
                      "determinarlo 'on a project-specific basis'. Su "
                      "comentario C3.4.1 (pag. impresa 3-10) cuenta que las "
                      "ediciones pasadas usaban 0.0, que el asunto no esta "
                      "resuelto, y que la regla de Turkstra hace razonable "
                      "0.50 para un rango amplio de trafico pesado. Lo que la "
                      "fuente no resuelve es el numero; el proyecto adopta "
                      "0.50, la unica cifra que el comentario califica de "
                      "razonable, y deja la ventana completa del factor (de "
                      "0.0 a 1.0) para el barrido. Donde pesa: en el empuje "
                      "y el peso de la sobrecarga viva de la combinacion "
                      "sismica, y en el limite de excentricidad de la "
                      "resultante bajo sismo -- dos tercios centrales (e <= "
                      "B/3) con gamma_EQ = 0.0, ocho decimas centrales (e <= "
                      "0.4*B) con gamma_EQ = 1.0, e interpolacion lineal en "
                      "medio (AASHTO 11.6.5.1; num. 2.8.1.1.14.1 del "
                      "Manual): con 0.50 el limite es 0.367*B. Las dos "
                      "direcciones se oponen -- mas carga viva es mas empuje "
                      "y a la vez un limite mas holgado --, y por eso se "
                      "barre y no se presume conservador. Cuidado con la "
                      "cifra del Manual: imprime 'tercio central' en vez de "
                      "los dos tercios de AASHTO; es errata de traduccion, "
                      "declarada en "
                      "constantes_normativas.EXCENTRICIDAD_ERRATA_MANUAL",
        fuente="AASHTO LRFD 9a ed. (2020), Art. 3.4.1, pag. impresa 3-19, y "
               "su comentario C3.4.1, pag. impresa 3-10 (el 0.50 'is "
               "reasonable'); texto literal en "
               "constantes_normativas.GAMMA_EQ_TEXTO. Via Manual de Puentes "
               "num. 2.4.5.3.1, Tabla 2.4.5.3.1-1. Ninguno de los dos fija "
               "el numero: la adopcion es del proyecto",
        reemplazado_por="Determinacion especifica del proyecto, con el ADTT "
                        "de la via y el fundamento que la sostenga, "
                        "declarada en la memoria",
        sensibilidad=(0.0, 1.0),   # la ventana entera del factor
        resolucion=Libre(
            que_lo_fija="el proyectista, 'on a project-specific basis' "
                        "(AASHTO Art. 3.4.1). La Tabla 2.4.5.3.1-1 imprime "
                        "el SIMBOLO gamma_EQ en la columna de LS, no un "
                        "numero; el 0.50 del comentario C3.4.1 es indicacion "
                        "de razonabilidad, no un valor tabulado",
            dominio="adimensional, 0 <= gamma_EQ <= 1",
        ),
    ),

    # Los cuatro angulos que Sec. 9.2 exige ADEMAS de la cadena sismica para
    # cerrar Mononobe-Okabe: "se requieren ademas phi del relleno, pendiente
    # del relleno (i), inclinacion del muro (beta) y friccion muro-suelo
    # (delta)". El primero ya esta declarado abajo como 'phi_relleno_trasdos'
    # (bloque GEOTECNIA), porque no es solo del sismo: gobierna tambien el Ka
    # estatico. Los otros tres viven aqui.

    "pendiente_relleno_trasdos_i": Criterio(
        # --- T-7b --- YA NO BLOQUEA: es OPCIONAL. La pendiente del relleno la
        # deduce el ensamble de la GEOMETRIA de cada cabezal (el talud del
        # terraplen, la coronacion del relleno retenido y el borde de la
        # plataforma de 7.B), con la regla de 'regla_pendiente_relleno_
        # trasdos'. Este criterio queda para quien tenga el angulo MEDIDO
        # sobre la seccion transversal del cruce -- o el equivalente de un
        # analisis de cuña -- y quiera imponerlo: declarado, gana para todos
        # los cabezales de la corrida.
        valor=None,
        opcional=True,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Inclinacion de la superficie del relleno del trasdos sobre "
                 "la horizontal (i), en grados, DECLARADA: sustituye a la que "
                 "el ensamble deduce de la geometria de cada cabezal",
        justificacion="Decide, solo si se declara, la pendiente del relleno "
                      "con que se calculan el empuje activo de Coulomb y el "
                      "de Mononobe-Okabe de todos los cabezales. Sin "
                      "declararlo, la pendiente sale de la geometria de cada "
                      "cabezal por la regla de "
                      "'regla_pendiente_relleno_trasdos' -- el relleno sube "
                      "con el talud del terraplen desde la coronacion del "
                      "relleno retenido y se quiebra en el borde de la "
                      "plataforma --, que es lo que el encargo de T-7b pide: "
                      "i de la geometria del terraplen. Es el parametro con "
                      "la sensibilidad mas violenta de la Fase 9: en "
                      "Mononobe-Okabe entra en sen(phi - psi - i), y con psi "
                      "= 26.6 grados (k_h = 0.50) la ecuacion solo tiene "
                      "solucion para i menor que phi - 26.6 grados; AASHTO "
                      "11.6.5.3 escribe esa misma condicion como limite de "
                      "validez del metodo. Por eso un angulo medido, cuando "
                      "existe, debe poder imponerse",
        fuente="Seccion transversal del cruce del expediente vial (dato de "
               "geometria), o analisis de cuña del relleno quebrado (AASHTO "
               "3.11.5.8.1). Sin declarar rige "
               "'regla_pendiente_relleno_trasdos'",
        reemplazado_por="Geometria medida sobre la seccion transversal del "
                        "punto de cruce",
        sensibilidad=(0.0, 33.7),   # grados; horizontal a un talud 1.5H:1V
        resolucion=Libre(
            que_lo_fija="el proyectista, con la seccion transversal del "
                        "cruce medida; sin declararlo lo deduce el ensamble "
                        "de la geometria de cada cabezal",
            dominio="grados sobre la horizontal, 0 <= i < phi del relleno",
        ),
    ),

    "inclinacion_muro_beta": Criterio(
        # --- T-7b --- DEJA DE SER UN VACIO: 0.0, el trasdos vertical que
        # `M9.predimensionar_cabezal` propone desde T-7a
        # (`GeometriaCabezal.beta_grados`). El ensamble no lo lee de aqui
        # sino de la geometria de cada cabezal; este criterio es la
        # DECLARACION de esa regla y la fuente de `k_ae_del_proyecto`.
        valor=0.0,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Inclinacion del paramento interior (trasdos) del cabezal "
                 "respecto de la VERTICAL (beta), en grados, positiva cuando "
                 "el muro se aleja del relleno",
        justificacion="Decide la inclinacion del trasdos que entra en el "
                      "coeficiente de empuje. El predimensionamiento del "
                      "cabezal (T-7a) propone la pantalla de trasdos "
                      "vertical, y en un muro en voladizo con talon el "
                      "empuje no actua sobre el paramento sino sobre el "
                      "plano vertical que sube desde el extremo del talon "
                      "(AASHTO C3.11.5.3, cita "
                      "AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON): en los dos "
                      "casos beta = 0. Un cabezal de paramento inclinado y "
                      "sin talon tendria otro beta y otra geometria de "
                      "pantalla, que el predimensionamiento no propone; el "
                      "signo se declara con la convencion de Mononobe-Okabe, "
                      "no con la del plano",
        fuente="Regla del predimensionamiento del cabezal "
               "('predimensionamiento_cabezal', trasdos vertical) y AASHTO "
               "LRFD C3.11.5.3 (plano de empuje del muro en voladizo), pag. "
               "impresa 3-122 (PDF 176)",
        reemplazado_por="Plano de encofrado del cabezal del expediente",
        sensibilidad=(0.0, 10.0),   # grados
        resolucion=Libre(
            que_lo_fija="el predimensionamiento del cabezal, del que este "
                        "angulo es parte (ver `predimensionamiento_cabezal`)",
            dominio="grados respecto de la vertical",
        ),
    ),

    "fraccion_fin_remanso_canal": Criterio(
        # --- VE-3.7 --- OPCIONAL, sin valor de archivo. El perfil M1 de un
        # canal suave remansado es ASINTOTICO al tirante normal: no tiene un
        # final, y ninguna fuente del repositorio fija donde cortarlo. Sin
        # declararlo, `M7.remanso_canal` da la cota inferior de siempre (la
        # horizontal del embalse, dh / S) y lo avisa; declarado, da ademas la
        # longitud del perfil por paso directo hasta (1 + f) y_n.
        # NIVEL: perfil, el de la etapa que lo consume (7.B, que corre a
        # `--alcance perfil` en la Familia C con la seccion medida del
        # canal). Ninguna corrida de referencia trae esa seccion, de modo que
        # la medida de `tests/test_nivel_medido.py` no lo alcanza: lo mide
        # `tests/test_ve3_remanso.py`.
        valor=None,
        opcional=True,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Fraccion f del tirante normal del canal con que termina el "
                 "perfil M1 del remanso de un paso de canal (Familia C): la "
                 "longitud del remanso es la distancia aguas arriba hasta "
                 "donde el tirante baja a (1 + f) y_n",
        justificacion="Decide, solo si se declara, la longitud del remanso "
                      "del canal que la memoria publica en un canal suave: "
                      "una f menor alarga el perfil (la M1 se acerca al "
                      "normal sin alcanzarlo). No cambia ningun diseño: la "
                      "longitud es un aviso, y el nivel en el cruce lo "
                      "juzgan VC1 y VC3",
        fuente="Adopcion del proyectista: la fuente del metodo (el paso "
               "directo, HDS-5 num. 3.5) no fija donde termina una curva "
               "asintotica",
        sensibilidad=(0.001, 0.05),
        resolucion=Libre(
            que_lo_fija="el proyectista, como tolerancia de fin del perfil; "
                        "sin declararlo la longitud del perfil no se publica",
            dominio="fraccion, 0 < f < 1",
        ),
    ),

    "friccion_muro_suelo_delta": Criterio(
        # --- T-7b --- YA NO BLOQUEA: es OPCIONAL. El angulo de friccion sobre
        # el plano de empuje sale de phi por la fraccion de
        # 'fraccion_delta_sobre_phi_trasdos' [C] -- que es lo que su propia
        # `verificacion_pendiente` pedia: declararlo como fraccion de phi y
        # no como angulo suelto --. Este criterio queda para quien lo tenga
        # MEDIDO: declarado, gana.
        valor=None,
        opcional=True,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Angulo de friccion sobre el plano de empuje del trasdos "
                 "(delta), en grados, DECLARADO: sustituye al que sale de "
                 "'fraccion_delta_sobre_phi_trasdos' por phi del relleno",
        justificacion="Decide, solo si se declara, el angulo con que el "
                      "empuje se inclina sobre su plano, y con el su reparto "
                      "entre la componente horizontal (deslizamiento y "
                      "excentricidad) y la vertical (carga sobre la base). "
                      "Sin declararlo rige la fraccion de phi de "
                      "'fraccion_delta_sobre_phi_trasdos', de modo que al "
                      "ajustar 'phi_relleno_trasdos' los dos angulos no "
                      "quedan incoherentes. No es conservador por un lado "
                      "solo: un delta alto reduce K_A y K_AE, inclina la "
                      "resultante y traslada empuje de la horizontal a la "
                      "vertical",
        fuente="Ensayo de interfase o adopcion declarada con su fuente. Sin "
               "declarar rige 'fraccion_delta_sobre_phi_trasdos' (AASHTO "
               "LRFD C3.11.5.3)",
        reemplazado_por="Ensayo de interfase concreto-relleno, o adopcion "
                        "declarada como fraccion de phi con su fuente",
        sensibilidad=(0.0, 25.5),   # grados; 0 a 0.67*phi con phi = 38
        resolucion=Libre(
            que_lo_fija="el proyectista, medido o adoptado con su fuente; "
                        "sin declararlo sale de la fraccion de phi",
            dominio="grados, 0 <= delta <= phi_relleno_trasdos",
        ),
    ),

    "punto_aplicacion_incremento_sismico": Criterio(
        # --- T-7b --- DEJA DE SER UN VACIO: 0.6, con la cita que la hoja de
        # ruta no daba. Es [C]: la fuente (AASHTO, comentario C11.6.5.3) no
        # prescribe el valor, DESCRIBE la practica de Seed y Whitman y da la
        # ventana.
        valor=0.6,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_FLOAT,
        concepto="Altura de aplicacion del incremento sismico de empuje "
                 "(P_AE - P_A), como fraccion de la altura h del plano de "
                 "empuje",
        justificacion="Decide el brazo del incremento sismico del empuje, y "
                      "con el el momento que gobierna la excentricidad y el "
                      "volteo sismicos. Mononobe-Okabe entrega el empuje "
                      "total, no su punto de aplicacion. La fuente (AASHTO "
                      "LRFD 11.6.5.3 y su comentario, citas "
                      "AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION y "
                      "AASHTO_LRFD_9.C11.6.5.3#RESULTANTE) dice tres cosas: "
                      "que la resultante del empuje TOTAL no baje de h/3; "
                      "que la practica anterior, con el estatico y el sismico "
                      "por separado, situaba la componente sismica a 0.6h "
                      "(Seed y Whitman); y que la investigacion mas "
                      "reciente pone la resultante total en h/3, aunque una "
                      "ubicacion algo mas alta, de 0.4h a 0.5h, 'may be "
                      "considered'. Lo que no resuelve es cual adoptar. El "
                      "proyecto aplica la fraccion al INCREMENTO y adopta "
                      "0.6: con el empuje estatico en su centroide, la "
                      "resultante combinada cae entre 0.4h y 0.5h, dentro de "
                      "lo que el comentario admite y del lado del mayor "
                      "momento. El otro extremo de la ventana, 1/3, pone el "
                      "empuje total en h/3",
        fuente="AASHTO LRFD 9a ed., 11.6.5.3 y C11.6.5.3, pag. impresa 11-30 "
               "(PDF 1499; citas AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION y "
               "AASHTO_LRFD_9.C11.6.5.3#RESULTANTE)",
        reemplazado_por="Analisis dinamico de interaccion suelo-estructura "
                        "que de la distribucion del empuje sismico",
        sensibilidad=(0.333, 0.6),   # h/3 (empuje total en el centroide) a 0.6h
        resolucion=Libre(
            que_lo_fija="el proyectista, dentro de lo que el comentario "
                        "C11.6.5.3 de AASHTO describe: de h/3 a 0.6h para el "
                        "incremento",
            dominio="fraccion adimensional de la altura h del plano de empuje",
        ),
    ),
}
