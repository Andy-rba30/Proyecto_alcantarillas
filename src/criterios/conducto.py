"""
Fichas de criterios adoptados del dominio: conducto.
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


    # ----------------------- FASE 8: ESTRUCTURAL DEL CONDUCTO -------------
    # Seleccion de clase/calibre por norma de producto (items 1-2) y V7 -
    # flotacion (item 3). El resto de Fase 8 (item 5: rigidez de anillo,
    # pandeo, costura) NO se calcula por decision expresa de la hoja de
    # ruta -- se difiere al expediente tecnico, ver
    # M8_estructural.verificacion_diferida_estructural().

    # 'NF_profundidad_m' ya no vive aqui: es un dato de sitio [S] que se mide
    # en cada cruce, no una exigencia normativa, y por eso es COLUMNA DEL CSV
    # (ver modelos.PuntoCritico y M0_carga.COLUMNAS). El 1.4 m que este
    # criterio declaraba era la caracterizacion general de la llanura del Bajo
    # Piura, y su propia `verificacion_pendiente` ya avisaba de que podia no
    # ser uniforme dentro del tramo; repetirlo en las cuatro filas del CSV
    # habria fingido cuatro mediciones donde hubo una descripcion de zona.

    # --- T-5 --- (cadena T; INF-3.3.5) DEJA DE SER UN VACIO, y lo que pasa a
    # tener valor es SOLO lo que el ejemplar de M 170M deja leer. La version
    # anterior lo declaraba [C] sin valor, de nivel expediente, porque «falta
    # TRANSCRIBIR» las Tablas 1 a 5 (concreto) e «IMPLEMENTAR» el
    # procedimiento de A796 (TMC). T-5 implementa los procedimientos (M8,
    # concreto por el metodo indirecto de AASHTO LRFD 12.10.4.3, TMC por
    # 12.7.2, HDPE por 12.12) y transcribe la tabla HASTA DONDE SE LEE: de
    # las cinco D-load de 0.3 mm solo la de la Clase II es legible (cita
    # AASHTO_M170M.T2#DLOAD); las otras cuatro NO se completan de memoria.
    # Lo que el valor dice es eso, y el consumidor (`M8.verificar_concreto`)
    # se detiene con DatoFaltanteError, nombrando la clase, cuando la D-load
    # requerida supera la ultima clase transcrita. Pasa a nivel de PERFIL:
    # lo invoca la verificacion F8.CLASE de la Fase 5, que la corrida de
    # perfil evalua (medido en tests/test_nivel_medido.py).
    "clases_producto_por_relleno": Criterio(
        valor={
            # {material: {clase: D-load de 0.3 mm en N/m/mm}}. Una clase que
            # no esta es una clase cuya D-load no se pudo leer: la norma la
            # tiene; este ejemplar no la deja ver.
            # --- VE-3.12 (decisiones 1 y 7 del dueño, 2026-11-17) --- III,
            # IV y V desde la tabla «ASTM C76 Class and D0.01» del ejemplo
            # resuelto del USACE EM 1110-2-2902 (pag. impresa B-7, cita
            # USACE_EM_1110_2_2902.B-7#C76): fuente [C] SECUNDARIA, valores
            # nominales de la norma metrica. Cada clase se ofrece solo en los
            # diametros que el ejemplar de M 170M deja verificar
            # (`M8.clases_de_concreto_para`): la V con pared B hasta 1200 mm;
            # la IV, ilegible por encima de 300 mm, queda BLOQUEADA.
            "concreto_reforzado": {"II": 50.0, "III": 65.0, "IV": 100.0,
                                   "V": 140.0},
        },
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Resistencia de producto por clase del tubo de concreto "
                 "reforzado (AASHTO M 170M-04: D-load para producir una "
                 "grieta de 0.3 mm, en N/m/mm), contra la que la Fase 8 "
                 "elige la clase minima del punto. Para el TMC y el HDPE no "
                 "hay tabla de clase: el calibre y el perfil salen del "
                 "procedimiento de AASHTO LRFD 12.7 y 12.12 que M8 implementa",
        justificacion="La norma peruana de construccion manda que el "
                      "proyecto indique la clase del tubo conforme a AASHTO "
                      "M 170M, y la norma de diseño la elige comparando la "
                      "D-load requerida con la de la clase. Lo que este "
                      "criterio declara es la columna de la norma de "
                      "producto que esa comparacion necesita, transcrita "
                      "hasta donde el ejemplar la deja leer: la D-load de "
                      "0.3 mm de la Clase II, 50.0 N/m/mm, impresa al pie de "
                      "su tabla, que tiene filas con pared B y acero de 300 "
                      "a 2700 mm. Las de las Clases III, IV y V (65, 100 y "
                      "140 N/m/mm) vienen desde VE-3.12 de una fuente "
                      "SECUNDARIA, la tabla de ASTM C76 de un ejemplo "
                      "resuelto del USACE (decision 1 del dueño), porque en "
                      "el ejemplar de M 170M no se leen; y cada una se ofrece "
                      "solo donde el ejemplar deja verificar que la norma la "
                      "tabula con pared B (decision 7): la V hasta 1200 mm; "
                      "la IV no por encima de 300 mm, donde queda BLOQUEADA y "
                      "un tubo que la necesite se detiene con el dato que "
                      "falta. La Clase I no se transcribe: solo se tabula de "
                      "1500 mm en adelante. Para "
                      "el TMC (ASTM A796, AASHTO LRFD 12.7) y el HDPE (AASHTO "
                      "LRFD 12.12) no hay clase por altura: el espesor de la "
                      "plancha y la verificacion del perfil son la salida de "
                      "su procedimiento, que M8 corre con la altura real de "
                      "cada punto",
        fuente="AASHTO M 170M-04, Tabla 2 'Design Requirements for Class II "
               "Reinforced Concrete Pipe' (continuacion), pag. impresa M 170M-5, "
               "leida por imagen: «D-load to produce a 0.3-mm crack 50.0» "
               "(cita AASHTO_M170M.T2#DLOAD). Clases III, IV y V: USACE EM "
               "1110-2-2902 (Change 1, 31 Mar 98), Apendice B, pag. impresa "
               "B-7, tabla «ASTM C76 Class and D0.01» de un EJEMPLO "
               "RESUELTO, fuente secundaria (cita "
               "USACE_EM_1110_2_2902.B-7#C76); M 170M-04 solo corrobora la "
               "ultima de la III (100.0) y la V con la primera cifra "
               "ilegible; los topes de diametro, M 170M-04 Tablas 4 y 5 por "
               "imagen (citas AASHTO_M170M.T4#LEGIBLE y "
               "AASHTO_M170M.T5#PARED_B). AASHTO LRFD 9a ed., Art. "
               "12.10.4.3.1, pag. impresa 12-64: «The D-load for a particular "
               "class and size of pipe shall be determined in accordance with "
               "AASHTO M 170M» (cita AASHTO_LRFD_9.12.10.4.3.1#DLOAD). EG-2013 "
               "506.02, pag. impresa 959: la clase se indica en el Proyecto "
               "(cita EG2013.506.02#CLASE). ASTM A796/A796M-13 y AASHTO LRFD "
               "12.7 y 12.12 para el TMC y el HDPE, sin tabla de clase "
               "(afirmaciones negativas SIN_TABLA_CALIBRE_POR_COBERTURA_A796 "
               "y SIN_CLASE_POR_ALTURA_M294_TRAD)",
        reemplazado_por="Un ejemplar legible de AASHTO M 170M (la M 170M-23 "
                        "vigente) o de ASTM C76M: confirma o corrige las D-load "
                        "de las Clases III, IV y V que hoy vienen del USACE, "
                        "da la de la Clase I y, sobre todo, el ultimo diametro "
                        "con pared B de la Clase IV, que hoy la deja "
                        "BLOQUEADA por encima de 300 mm "
                        "(DIAMETRO_MAX_LEGIBLE_POR_CLASE_M170M_MM). Es una "
                        "entrada que debe conseguir el dueño del proyecto "
                        "(docs/contrato_entradas.md)",
        verificacion_pendiente="LEGIBILIDAD DEL EJEMPLAR (medida en T-5, "
                               "pagina por pagina y por imagen): Clase II "
                               "0.3 mm = 50.0 (PDF 5, legible); Clase III, "
                               "ultima = 100.0 (PDF 7), 0.3 mm no se ve; "
                               "Clase V, «\\ 40.0» y «1 ISD» (PDF 11, el "
                               "primer digito ilegible); Clases I y IV, "
                               "ilegibles. Desde VE-3.12 las D-load de III a V "
                               "vienen del USACE (fuente secundaria) y lo que "
                               "sigue pendiente es el ejemplar legible: es "
                               "decision del dueño del proyecto (2026-11-12, "
                               "reafirmada el 2026-11-17) BLOQUEAR, no subir "
                               "de diametro ni de clase para esquivar una "
                               "clase que el ejemplar no deja verificar. Los "
                               "diametros desde los que cada clase se tabula "
                               "SI se leen (PDF 3, 4, 6, 8 y 10): 1500 mm la "
                               "Clase I y 300 mm las otras cuatro; los ultimos "
                               "con pared B, solo los de la II y la III (2700 "
                               "mm) y la V (1200 mm)",
        resolucion=Libre(
            que_lo_fija="la norma de producto, por clase; el proyecto solo "
                        "transcribe lo que el ejemplar deja leer",
            tabla_pendiente="AASHTO M 170M-04 Tablas 1, 3, 4 y 5: D-load de "
                            "0.3 mm ilegible en el ejemplar de normas/ (III a "
                            "V, desde el USACE); Tabla 4: ultimo diametro con "
                            "pared B de la Clase IV, ilegible",
        ),
    ),

    # --- VE-3.12 (decision 6 del dueño, 2026-11-17) --- EL RELLENO HASTA EL
    # QUE SE IMPRIME EL CONTRASTE DE LA PRACTICA ACPA en el paso F8.CLASE del
    # tubo de concreto. La carga viva que RIGE sigue siendo la lectura literal
    # de AASHTO LRFD 9.a ed. (12.10.2.3: «uniform vertical distribution across
    # the top of the pipe», sin longitud efectiva); con poco relleno esa
    # lectura sube una o dos clases respecto de la practica ACPA (DD 1, 2009,
    # Eq. [2], L_e = L + 1.75(3/4 R_o)), y el dueño decidio mostrarlo como
    # contraste que NO gobierna, como el de la instalacion Tipo 4. Nivel de
    # PERFIL: lo consume `M8.verificar_concreto`, que la Fase 5 corre a nivel
    # de perfil (F8.CLASE; medido en tests/test_ve3_clases_iii_v.py).
    "relleno_max_contraste_acpa_m": Criterio(
        valor=1.0,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Relleno total hasta la rasante, m, por DEBAJO del cual el "
                 "paso F8.CLASE del tubo de concreto imprime, como contraste "
                 "que no rige, la clase que saldria con la longitud efectiva "
                 "de ACPA (DD 1, Eq. [2])",
        justificacion="Decision del dueño del proyecto (segunda respuesta "
                      "del LEEME de VE-3) sobre la verificacion "
                      "independiente de la carga viva de M8: se mantiene la "
                      "lectura literal de AASHTO LRFD 9.a ed. y solo se "
                      "avisa del contraste ACPA en tubos de concreto con "
                      "relleno < 1.0 m. La verificacion midio que a partir "
                      "de ~1.0 m de relleno la clase no cambia entre las dos "
                      "lecturas (con 1.5 m la D-load difiere ~10 %)",
        fuente="Decision del dueño (proceso/planes_mejora/ve3_estado/LEEME.md, "
               "segunda respuesta, punto 6); medida en proceso/planes_mejora/"
               "ve3_estado/verificaciones_del_dueno/carga_viva_m8_poco_"
               "relleno.md, §4",
        sensibilidad=(0.6096, 1.5),   # m: desde 2.0 ft (dominio del metodo) hasta donde la verificacion midio ~10 % de diferencia
        resolucion=Libre(
            que_lo_fija="el dueño del proyecto: hasta que relleno quiere ver "
                        "el contraste; no cambia ningun diseño",
        ),
    ),

    # 'FS_flotacion' SE RETIRO. Declaraba el factor de seguridad global de
    # ΣW >= FS*U, que es lenguaje de TENSION ADMISIBLE, y V7 se reescribio
    # como el equilibrio de factores de carga que corresponde al marco LRFD
    # que adopta Sec. 0.2:
    #
    #     gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U
    #
    # No se le redefinio el contenido porque en LRFD no queda nada que
    # represente: el margen entre estabilizante y desestabilizante lo hacen
    # ahora los propios gamma, y conservar ademas un FS seria contar dos veces
    # el mismo margen. Los gamma NO son un criterio: son [N] y viven en
    # constantes_normativas (las dos tablas del num. 2.4.5.3.1); lo que
    # 'factores_carga_aashto' declara, mas abajo, es de que FILA de gamma_p
    # cuelga cada estructura, y es el mismo criterio del que come M9
    # (Sec. 9.2). Que Fase 8 y Fase 9 lean las mismas tablas y la misma
    # declaracion es lo que impide que el expediente termine con dos juegos
    # de factores de carga distintos.

    "peso_especifico_relleno_kn_m3": Criterio(
        # kN/m3. EXTREMO INFERIOR del rango declarado, y es la eleccion
        # conservadora sin discusion posible: en V7 el peso del relleno esta
        # del lado ESTABILIZANTE (EV, minorado por gamma_EV_min), de modo que
        # cuanto menos pese, mas cerca de flotar queda el conducto. Adoptar
        # 20.0 haria pasar V7 en puntos donde 17.0 la reprueba.
        valor=17.0,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Peso especifico del material de relleno sobre la clave, "
                 "para el termino ΣW de V7 (peso del prisma de relleno que "
                 "se opone a la flotacion)",
        justificacion="Ni la hoja de ruta ni el CSV (Sec. 1.2) traen el "
                      "peso especifico del material de relleno: depende de "
                      "la cantera que finalmente se especifique. V7 lo "
                      "necesita para pesar el prisma de relleno sobre la "
                      "clave (ancho D, altura la del punto -- ver "
                      "M8_estructural.peso_relleno_kn_m). El peso propio del "
                      "conducto NO se suma: omitirlo es conservador (reduce "
                      "ΣW) y evita depender del espesor de pared que "
                      "'clases_producto_por_relleno' todavia no resuelve",
        fuente="PENDIENTE - ensayo de peso especifico del material de "
              "cantera propuesto, o valor de practica corriente declarado "
              "con su fuente en la memoria",
        reemplazado_por="Peso especifico medido del material de relleno "
                        "efectivamente especificado en el proyecto",
        sensibilidad=(17.0, 20.0),   # kN/m3, rango corriente de rellenos compactados
        resolucion=Libre(
            que_lo_fija="el proyectista, con el ensayo de peso especifico "
                        "del material de cantera propuesto o un valor de "
                        "practica corriente declarado con su fuente",
            dominio="kN/m3 > 0",
        ),
    ),

    # =======================================================================
    # --- VE-2 (c2) --- EL NIVEL DE AGUA DE DISEÑO DE V7, que la norma deja
    # al Propietario (Manual de Puentes 2.4.3.8.1). Hasta VE-2 era una
    # hipotesis cableada en `M8.empuje_flotacion_kn_m` --el conducto
    # sumergido entero-- y ningun criterio lo decia; desde aqui es una
    # eleccion [A] con su ventana, y el valor de archivo reproduce lo que se
    # calculaba (la linea base no se mueve). NIVEL MEDIDO, los dos de perfil:
    #   * 'nivel_agua_diseno_v7' lo invoca V7 (Fase 5) en toda corrida que la
    #     evalua: lo mide la corrida de perfil de `tests/test_nivel_medido.py`.
    #   * 'margen_estacional_nf_v7_m' solo lo lee V7 con la alternativa
    #     'nf_del_punto', que ninguna corrida de referencia declara: NO se
    #     mide por corridas de referencia (lo mide la corrida de perfil de
    #     `tests/test_ve2_flotacion.py`, que la declara) y su nivel es el de
    #     su unico consumidor, V7.
    # =======================================================================
    "nivel_agua_diseno_v7": Criterio(
        valor="en_la_clave",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        #   en_la_clave    el nivel de agua de diseño en la clave EXTERIOR del
        #       conducto: sumergido entero, el relleno sobre la clave en seco
        #       (peso humedo). Es la hipotesis de la fila V7 de la hoja de
        #       ruta («Tubería vacía, NF en su cota más alta») y la que V7
        #       calculaba hasta VE-2.
        #   nf_del_punto   el nivel en el freatico MEDIDO del cruce, mas un
        #       ascenso estacional declarado: cota_terreno - NF_profundidad_m
        #       + 'margen_estacional_nf_v7_m'. V7 se evalua solo si el fondo
        #       exterior del conducto queda bajo ese nivel (AASHTO 12.6.1); si
        #       no, «no aplica». El relleno bajo el nivel pesa sumergido.
        sensibilidad=("en_la_clave", "nf_del_punto"),
        concepto="Nivel de agua de diseño con que V7 evalua la flotacion del "
                 "conducto vacio: en la clave (sumergido entero) o en el "
                 "freatico medido del cruce mas un ascenso estacional",
        justificacion="Decide la subpresion U de V7 y cuanto del relleno "
                      "sobre la clave pesa sumergido. La norma no fija el "
                      "nivel: el Manual de Puentes, num. 2.4.3.8.1, dice que "
                      "los niveles de agua de diseño los especifica o "
                      "aprueba el Propietario (cita "
                      "MP.2.4.3.8.1#NIVEL_DE_DISENO; AASHTO 3.7.1 igual), y la "
                      "subpresion de 2.4.3.8.2 actua sobre lo que queda "
                      "debajo de ese nivel. El valor de archivo, "
                      "«en_la_clave», es la adopcion conservadora: sumergido "
                      "entero el conducto desplaza todo su volumen y ningun "
                      "nivel mas bajo da mas empuje, y el relleno sobre la "
                      "clave pesa humedo (17 kN/m3), que es coherente solo "
                      "con el nivel en la clave. «nf_del_punto» lee la "
                      "columna NF_profundidad_m, que es una lectura de campo "
                      "y no necesariamente el freatico mas alto previsto "
                      "(AASHTO 12.6.2.3): por eso le suma "
                      "'margen_estacional_nf_v7_m', sin valor, que detiene "
                      "hasta que se declare. Con ese nivel V7 se evalua solo "
                      "si el fondo EXTERIOR del conducto queda bajo el "
                      "(AASHTO 12.6.1 pide «inverts below the water table»; el "
                      "fondo exterior, mas bajo que el invert, es el lado "
                      "conservador), y el relleno bajo el nivel pesa "
                      "sumergido, el saturado menos el del agua, por "
                      "ANALOGIA [N->] con el Manual de Puentes 2.4.4.1.3, que "
                      "exige densidades sumergidas para el empuje LATERAL; el "
                      "saturado es el dato de ensayo "
                      "'peso_especifico_saturado_relleno_kn_m3'. Declararlo "
                      "es escribir 'nivel_agua_diseno_v7' = «nf_del_punto» en "
                      "la sesion o con --declarar",
        fuente="Manual de Puentes num. 2.4.3.8.1, pag. impresa 113 (cita "
               "MP.2.4.3.8.1#NIVEL_DE_DISENO) y 2.4.3.8.2; AASHTO LRFD 9a "
               "ed., 3.7.1 (pag. 3-45), 12.6.1 (pag. 12-14) y 12.6.2.3 (pag. "
               "12-19); por analogia, Manual de Puentes num. 2.4.4.1.3, pag. "
               "impresa 133 (cita MP.2.4.4.1.3#SUMERGIDO)",
        reemplazado_por="El nivel de agua de diseño que el Propietario "
                        "especifique o apruebe para la flotacion del "
                        "conducto, o el freatico mas alto previsto que de el "
                        "estudio geotecnico del cruce",
        resolucion=Libre(
            que_lo_fija="el Propietario: los niveles de agua de diseño son "
                        "los que el especifica o aprueba (Manual de Puentes "
                        "2.4.3.8.1); el proyectista propone una de las dos "
                        "reglas",
            dominio="una de las dos opciones de la ventana",
        ),
    ),

    "margen_estacional_nf_v7_m": Criterio(
        valor=None,                 # VACIO: solo lo lee V7 con 'nf_del_punto'
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        # VENTANA SIMBOLICA, y a proposito: el extremo de arriba depende del
        # punto (llevar el nivel al terreno natural del cruce es un margen
        # igual a su NF_profundidad_m), de modo que ningun par de numeros
        # unico la describe sin inventar uno. El de abajo es 0 m, la lectura
        # ya es el nivel mas alto. Un margen negativo lo rechaza la PUERTA
        # (`no_negativo`, revision de VE-2, M4: hasta ella entraba por los
        # tres caminos), y el consumidor sigue como segunda linea
        # (`M8.cota_nivel_agua_v7_del_nf`, DatoInvalidoError).
        no_negativo=True,
        sensibilidad=("0 m: la lectura de NF_profundidad_m ya es el freatico "
                      "mas alto previsto (medida en la epoca de aguas altas, "
                      "o una serie piezometrica que la cubre)",
                      "el ascenso estacional que estime el estudio "
                      "geotecnico entre la fecha de la lectura y la epoca "
                      "del nivel mas alto; con un margen igual a "
                      "NF_profundidad_m el nivel llega al terreno natural "
                      "del cruce"),
        concepto="Ascenso del nivel freatico, m, entre la lectura de "
                 "NF_profundidad_m y el freatico mas alto previsto, para el "
                 "nivel de agua de diseño de V7 con 'nivel_agua_diseno_v7' = "
                 "«nf_del_punto»",
        justificacion="La columna NF_profundidad_m es una lectura de campo "
                      "(calicata o piezometro, en una fecha): un NF de "
                      "estiaje y uno de avenida no son el mismo dato, y "
                      "AASHTO LRFD 12.6.2.3 manda considerar el levantamiento "
                      "bajo «the highest anticipated groundwater level» (cita "
                      "AASHTO_LRFD_9.12.6.2.3#UPLIFT). Ninguna fuente del "
                      "repositorio da la oscilacion estacional del freatico, "
                      "y rellenarla con 0 seria afirmar sin dato que la "
                      "lectura es el nivel mas alto: por eso esta vacio y "
                      "detiene V7 cuando 'nivel_agua_diseno_v7' = "
                      "«nf_del_punto». Con el valor de archivo de ese "
                      "criterio («en_la_clave») no se lee nunca. Es un solo "
                      "margen para todo el corredor: si el estudio da "
                      "oscilaciones distintas por cruce, rige el mayor",
        fuente="PENDIENTE - estudio geotecnico: oscilacion estacional del "
               "freatico (serie piezometrica, o lectura en la epoca de aguas "
               "altas); AASHTO LRFD 9a ed., 12.6.2.3, pag. impresa 12-19",
        reemplazado_por="El freatico mas alto previsto de cada cruce, que "
                        "de el estudio geotecnico",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el estudio geotecnico: la "
                        "oscilacion estacional del freatico entre la fecha "
                        "de la lectura y la epoca del nivel mas alto",
            dominio="m >= 0",
        ),
    ),

    # =======================================================================
    # --- T-5 --- (cadena T, 2026-11-12) SIETE CRITERIOS NUEVOS de la Fase 8,
    # al final de su seccion: cinco de la FASE A y dos del cierre
    # ('carga_viva_bajo_relleno_alto' y 'perfil_hdpe_fabricante', que
    # salieron de las dos auditorias adversariales). Los siete son [A] de
    # PERFIL: los invocan las verificaciones F8.* de la Fase 5, que deciden si
    # la combinacion material / diametro / plancha / clase EXISTE.
    #
    # QUE CORRIDA MIDIO EL NIVEL DE CADA UNO (CLAUDE.md, «Nivel de entrega»),
    # porque la version anterior de esta nota decia «medido en
    # tests/test_nivel_medido.py» de los cinco y solo era cierto de uno:
    #   * 'instalacion_estandar_concreto' y 'carga_viva_bajo_relleno_alto'
    #     los invoca la corrida de PERFIL de referencia (A-01 y A-02 se
    #     dimensionan en tubo de concreto): medidos por
    #     `tests/test_nivel_medido.py`.
    #   * 'fabricacion_tmc', 'eta_importancia_operativa_conducto',
    #     'relleno_estructural_hdpe', 'parametros_diseno_hdpe' y
    #     'perfil_hdpe_fabricante' NO los alcanza la corrida de referencia
    #     (ningun punto del fixture llega al TMC ni al HDPE): los mide la
    #     corrida de perfil de `tests/test_t5_correcciones_auditoria.py::
    #     test_la_corrida_de_perfil_que_llega_al_tmc_y_al_hdpe_invoca_sus_
    #     criterios`, que excluye el concreto por diametro de catalogo.
    #
    # LOS VALORES DE ARCHIVO NO SON TODOS «EL MAS DESFAVORABLE», y la nota
    # anterior lo decia de los cinco. Lo que cada uno es:
    #   * 'instalacion_estandar_concreto' = tipo_3: la instalacion que la
    #     compactacion exigida por el EG-2013 corresponde, leida contra la
    #     Tabla 12.10.2.1-1 (decision del dueño, 2026-11-12); el Tipo 4, cota
    #     conservadora, esta en la ventana y se imprime al lado.
    #   * 'fabricacion_tmc' = anular_remachada_simple: la costura mas debil
    #     TABULADA (decision del dueño); el EG-2013 describe tuberia
    #     empernada, que no tiene tabla, y el resultado lo avisa.
    #   * 'eta_importancia_operativa_conducto' = 1.05: extremo desfavorable
    #     de la graduacion del Manual de Puentes; la fija el Propietario.
    #   * 'relleno_estructural_hdpe' = Si-95: la columna menos favorable de
    #     las que corresponden al material GRANULAR que el EG-2013 508.02 d)
    #     exige para la cama y la sujecion lateral.
    #   * 'parametros_diseno_hdpe': K_gammaE, D_L, K_B y la deflexion, el
    #     valor que la norma llama TIPICO (no el extremo: K_B desfavorable
    #     seria 0.110 y D_L 6.0); los años, la columna desfavorable (75);
    #     nu = 0.40 es un valor corriente SIN FUENTE (0.45 seria el
    #     desfavorable de su ventana).
    #   * 'carga_viva_bajo_relleno_alto' = conservar: el lado seguro del
    #     permiso de 3.6.1.2.6a.
    #   * 'perfil_hdpe_fabricante': SIN VALOR y sin valor por defecto; es un
    #     dato del fabricante.
    # Los numeros de las tablas sobre las que eligen viven en
    # constantes_normativas, bloque «--- T-5 ---».
    # =======================================================================

    "instalacion_estandar_concreto": Criterio(
        valor="tipo_3",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("tipo_1", "tipo_2", "tipo_3", "tipo_4"),
        concepto="Tipo de instalacion estandar del tubo de concreto (AASHTO "
                 "LRFD 12.10.2.1, Tablas 12.10.2.1-1 y -3): fija el factor de "
                 "arqueo vertical de la carga de tierra y el factor de cama "
                 "con que la Fase 8 elige la clase",
        justificacion="Decide con que instalacion se verifica el tubo de "
                      "concreto. La hipotesis de calculo tiene que coincidir "
                      "con lo que la especificacion de construccion "
                      "garantiza. La norma de diseño define cuatro tipos por "
                      "el suelo y la compactacion de la cama, los riñones y "
                      "los costados, con porcentajes del Proctor Estandar. La "
                      "norma peruana de construccion pide un solado de "
                      "material de subbase granular de 15 cm y la sujecion "
                      "con ese mismo material hasta un sexto del diametro "
                      "exterior, los dos compactados como la corona del "
                      "terraplen (95 % del Proctor Modificado), y por encima "
                      "el relleno para estructuras, con los materiales de "
                      "terraplen compactados al 90 % del Proctor Modificado. "
                      "Se adopta el Tipo 3, que es la instalacion que esa "
                      "exigencia corresponde: pide en riñones y costados 85 % "
                      "de un suelo granular limpio, 90 % de uno limoso o 95 % "
                      "de uno arcilloso. La correspondencia es lectura del "
                      "proyecto y tiene una condicion: la densidad maxima del "
                      "Proctor Modificado no es menor que la del Estandar, de "
                      "modo que el 90 % del Modificado garantiza el Tipo 3 "
                      "con suelo granular o limoso; con el material mas "
                      "plastico que la norma peruana admite en un terraplen "
                      "haria falta la tabla de equivalencias entre los dos "
                      "ensayos, que la norma de diseño remite a su "
                      "especificacion de construccion y no esta entre las "
                      "fuentes del repositorio. Por eso el Tipo 4 --que no "
                      "exige compactar y que cualquier relleno compactado "
                      "cumple-- esta dentro de la ventana como cota "
                      "conservadora, y la Fase 8 imprime al lado la D-load, "
                      "la clase y el relleno maximo que saldrian con el. No "
                      "alcanza el Tipo 1 ni el 2, que piden suelo granular "
                      "al 95 o al 90 % en toda la zona de riñones: declararlos "
                      "exige que las especificaciones del proyecto pidan esa "
                      "cama y ese relleno, y con el 1 la D-load se multiplica "
                      "por 1.10",
        fuente="AASHTO LRFD 9a ed., Art. 12.10.2.1 y Tablas 12.10.2.1-1 (pags. "
               "impresas 12-50 y 12-51, cita AASHTO_LRFD_9.T12.10.2.1-1) y "
               "12.10.2.1-3 (pag. 12-53); Art. 12.10.4.3.1 y Tabla "
               "12.10.4.3.2a-1 (pags. 12-64 y 12-65). EG-2013 506.07, 506.10 y "
               "506.11 (pags. impresas 960 y 961; citas EG2013.506.07 y "
               "EG2013.506.10), Seccion 502 (502.02 y 502.09(c)(1), pags. 895 "
               "y 899) y 205.12(c)(1) (pag. 193, cita "
               "EG2013.205.12#COMPACTACION) para lo que la norma peruana "
               "exige; Tabla 205-01 (pag. 186, cita EG2013.T205-01) para los "
               "materiales. El 508.07 (mas del 95 % del Proctor Modificado) "
               "es de la tuberia de polietileno, no de la de concreto. EL "
               "VALOR DE ARCHIVO LO DECIDIO EL DUEÑO DEL PROYECTO "
               "(2026-11-12), con el Tipo 4 impreso como contraste; LA "
               "ELECCION DEL TIPO NO ESTA EN NINGUNA NORMA",
        reemplazado_por="El tipo de instalacion que las especificaciones "
                        "tecnicas del expediente fijen para la cama y el "
                        "relleno del tubo de concreto",
        resolucion=Libre(
            que_lo_fija="el proyectista, con las especificaciones de cama y "
                        "relleno del expediente",
            dominio="uno de los cuatro tipos de la Tabla 12.10.2.1-1; el "
                    "conjunto cerrado viaja en `sensibilidad`",
        ),
    ),

    "fabricacion_tmc": Criterio(
        valor="anular_remachada_simple",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("helicoidal", "anular_remachada_simple",
                      "anular_remachada_doble", "anular_empernada"),
        concepto="Fabricacion de la tuberia metalica corrugada: helicoidal "
                 "(costura engargolada o soldada, sin costura longitudinal) o "
                 "anular con costura longitudinal remachada (simple o doble) "
                 "o empernada. Decide si la Fase 8 verifica la costura y con "
                 "que resistencia",
        justificacion="Decide si la verificacion estructural del TMC incluye "
                      "la costura longitudinal y con que resistencia. La "
                      "norma de diseño la exige solo a la tuberia con costura "
                      "longitudinal; la helicoidal no la tiene. La norma "
                      "peruana de construccion describe, para la corrugacion "
                      "de 68 por 13 mm de 900 a 2100 mm, tubos conformados de "
                      "planchas corrugadas y perforadas con sus pernos y "
                      "tuercas: es tuberia armada con costura EMPERNADA. Esa "
                      "costura no tiene resistencia tabulada para esta "
                      "corrugacion en ninguna fuente del repositorio, y "
                      "declararla detiene la Fase 8 pidiendo la que garantice "
                      "el fabricante. El valor de archivo es la anular "
                      "remachada simple, la costura mas debil de las que SI "
                      "tienen resistencia tabulada (Tabla 5 de ASTM A796, "
                      "remaches de 8 mm hasta 2.01 mm de plancha y de 10 mm "
                      "desde 2.77): con ella la verificacion de la costura es "
                      "una cota con la resistencia de OTRA fabricacion, no la "
                      "del producto que la norma peruana describe, y el "
                      "resultado lo avisa en cada punto mientras rija el valor "
                      "de archivo. Que la remachada simple sea mas debil que "
                      "la empernada del producto no lo demuestra ninguna "
                      "fuente del repositorio. La helicoidal no verifica "
                      "costura",
        fuente="AASHTO LRFD 9a ed., Art. 12.7.2.5 (pag. impresa 12-27) y "
               "Tabla 12.5.5-1 (pag. 12-12); ASTM A796/A796M-13 num. 8.1.3.1 y "
               "Tabla 5 (PDF 4 y 8, por imagen; releida valor a valor en el "
               "cierre de T-5: 244/315, 266/435, 341/683, 357/715 y 374/748 "
               "kN/m); AASHTO LRFD Tabla A12-7 (pag. 12-106); EG-2013 507.02 "
               "a) (pag. impresa 969, cita EG2013.507.02#EMPERNADA). EL VALOR "
               "DE ARCHIVO LO DECIDIO EL DUEÑO DEL PROYECTO (2026-11-12). LA "
               "ELECCION NO ESTA EN NINGUNA NORMA",
        reemplazado_por="La fabricacion del producto que el expediente "
                        "especifique y, si es empernada, la resistencia de "
                        "costura que el fabricante garantice",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el producto que especifique",
            dominio="una de las cuatro fabricaciones; el conjunto cerrado "
                    "viaja en `sensibilidad`",
        ),
    ),

    "eta_importancia_operativa_conducto": Criterio(
        valor=1.05,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        sensibilidad=(0.95, 1.05),
        concepto="Modificador de las cargas por importancia operativa, eta_I, "
                 "del CRUCE: rige en las verificaciones de resistencia del "
                 "conducto (TMC y HDPE; AASHTO LRFD 12.5.4 y Manual de "
                 "Puentes 2.3.2.5) y en las combinaciones de Resistencia I "
                 "de sus cabezales (AASHTO LRFD 1.3.2.1). En el conducto, "
                 "con eta_D = eta_R = 1.00, es el eta de la carga de tierra "
                 "y de la carga viva; en el cabezal se multiplica por "
                 "'eta_ductilidad_cabezal' y 'eta_redundancia_cabezal'",
        justificacion="La clasificacion de importancia operativa es de la "
                      "VIA en ese cruce, no de una pieza: el conducto y sus "
                      "cabezales son la misma obra y llevan el mismo eta_I "
                      "(una decision, un valor; la clave conserva el nombre "
                      "con que nacio en la Fase 8 del conducto, y desde la "
                      "verificacion de las formulas del cabezal la lee "
                      "tambien `M9.modificador_de_carga`). "
                      "Decide cuanto se mayoran las cargas por la importancia "
                      "de la via. Ninguna fuente prescribe 1.05 para una "
                      "estructura enterrada: la norma de diseño manda aplicar "
                      "los modificadores generales, considera redundantes a "
                      "las estructuras enterradas en los estados limite de "
                      "resistencia (de ahi el factor de redundancia 1.00) y "
                      "dice que la clasificacion operativa se determina por "
                      "la continuidad de funcion o la seguridad de la via; y "
                      "tanto ella como el Manual de Puentes dejan esa "
                      "clasificacion al Propietario, que puede declararla. El "
                      "Manual la gradua en 1.05 o mas para puentes criticos o "
                      "esenciales, 1.00 para los tipicos y 0.95 o mas para "
                      "los de relativa menor importancia. Se adopta 1.05 como "
                      "clasificacion de importancia de esta via --acceso en "
                      "emergencia durante el Fenomeno El Niño-- por decision "
                      "del dueño del proyecto, que es quien hace de "
                      "Propietario en la tesis; es el extremo mas desfavorable "
                      "de la graduacion. No afecta al tubo de concreto, que "
                      "se verifica por el metodo indirecto en servicio, sin "
                      "factores",
        fuente="Manual de Puentes, num. 2.3.2.5 «Importancia Operativa», pag. "
               "impresa 99 (cita MP.2.3.2.5); AASHTO LRFD 9a ed., Art. 12.5.4, "
               "pag. impresa 12-11 (cita AASHTO_LRFD_9.12.5.4: «For strength "
               "limit states, "
               "buried structures shall be considered redundant. Operational "
               "classification shall be determined on the basis of continued "
               "function and/or safety of the roadway»), y Art. 1.3.5, pag. "
               "impresa 1-7 («The Owner may declare a bridge or any "
               "structural component and connection thereof to be of "
               "operational priority»). La clasificacion de esta via la hace "
               "el Propietario: decidida por el dueño del proyecto el "
               "2026-11-12. Para el cabezal: AASHTO LRFD Art. 1.3.2.1, pag. "
               "impresa 1-3 (cita AASHTO_LRFD_9.1.3.2.1#ETA)",
        reemplazado_por="La importancia operativa que el propietario declare "
                        "para la via",
        resolucion=Libre(
            que_lo_fija="el propietario, por la importancia operativa de la "
                        "via",
            dominio="0.95 a 1.05 (Manual de Puentes 2.3.2.5)",
        ),
    ),

    "relleno_estructural_hdpe": Criterio(
        valor="Si-95",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("Sn-100", "Sn-95", "Si-95", "Cl-95"),
        concepto="Suelo y compactacion del relleno estructural del HDPE, como "
                 "columna de la Tabla 12.12.3.5-1 de AASHTO LRFD (Sn, Si o Cl; "
                 "% del Proctor Estandar): de ella sale el modulo "
                 "restringido del suelo M_s del arqueo, el pandeo y la "
                 "deflexion",
        justificacion="Decide con que rigidez de suelo se verifica el tubo de "
                      "polietileno. La norma peruana de construccion manda "
                      "construir la cama de asiento y la sujecion lateral del "
                      "tubo con material GRANULAR de las caracteristicas de "
                      "un afirmado --finos entre el 5 y el 25 % e indice de "
                      "plasticidad de 4 a 9--, y compactar el relleno a mas "
                      "del 95 % de la maxima densidad seca del Proctor "
                      "Modificado. Un material asi es, en la clasificacion "
                      "con que la norma de diseño agrupa los suelos de su "
                      "tabla, una grava o arena limpia (columna Sn) o una "
                      "grava o arena con finos de baja plasticidad (columna "
                      "Si); la columna de las arcillas (Cl) reune suelos con "
                      "indice de plasticidad que el afirmado no admite. Y el "
                      "95 % del Proctor Modificado es por lo menos el 95 % "
                      "del Estandar con que la tabla gradua la compactacion, "
                      "porque la densidad maxima del ensayo modificado no es "
                      "menor. Se adopta la columna Si al 95 %, la menos "
                      "favorable de las que corresponden a lo que la norma "
                      "peruana exige. La columna Cl al 95 % queda en la "
                      "ventana como cota conservadora --es lo que resultaria "
                      "si la sujecion lateral se hiciera con el relleno "
                      "general del terraplen en vez del material granular "
                      "exigido--: con ella, y con el perfil minimo de la "
                      "norma, el tubo de 900 a 1200 mm no cumple a ninguna "
                      "altura de relleno. Declarar una arena (Sn) exige que "
                      "las especificaciones pidan un material limpio",
        fuente="AASHTO LRFD 9a ed., Tabla 12.12.3.5-1 (pag. impresa 12-81, "
               "cita AASHTO_LRFD_9.T12.12.3.5-1) y Tabla 12.12.3.5-2 (pag. "
               "12-82, cita AASHTO_LRFD_9.T12.12.3.5-2: Sn = A-1, A-3; Si = "
               "A-2-4, A-2-5, A-4; Cl = A-2-6, A-2-7, A-5, A-6); EG-2013 "
               "508.02 d) (pag. impresa 982, cita EG2013.508.02#GRANULAR), "
               "Tabla 301-01 y requisitos de la Seccion 301 (pag. 238) y "
               "508.07 (pag. 984, cita EG2013.508.07#COMPACTACION). La "
               "correspondencia entre el afirmado de la Seccion 301 y las "
               "columnas Sn y Si es LECTURA DEL PROYECTO: la Tabla "
               "12.12.3.5-2 dice que sus correlaciones son aproximadas. LA "
               "ELECCION NO ESTA EN NINGUNA NORMA",
        reemplazado_por="El suelo y la compactacion que las especificaciones "
                        "del expediente fijen para el relleno del HDPE, con "
                        "su ensayo",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el material de relleno que "
                        "especifique",
            dominio="una columna de la Tabla 12.12.3.5-1 de 95 % o mas; el "
                    "conjunto cerrado viaja en `sensibilidad`",
        ),
    ),

    "parametros_diseno_hdpe": Criterio(
        valor={"K_gamma_E": 1.5, "D_L": 1.5, "K_B": 0.10,
               "nu_suelo": 0.40, "deflexion_admisible": 0.05,
               "anios_largo_plazo": 75.0},
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        sensibilidad={"K_gamma_E": (1.0, 1.5), "D_L": (1.0, 6.0),
                      "K_B": (0.083, 0.110), "nu_suelo": (0.25, 0.45),
                      "deflexion_admisible": (0.02, 0.05),
                      "anios_largo_plazo": (50.0, 75.0)},
        concepto="Parametros del procedimiento de AASHTO LRFD 12.12 para el "
                 "HDPE que la norma deja al diseñador: factor de instalacion "
                 "K_gammaE, factor de retardo de la deflexion D_L, "
                 "coeficiente de cama K_B, coeficiente de Poisson del suelo, "
                 "deflexion admisible (fraccion del diametro) y duracion de "
                 "las propiedades de largo plazo del PE (50 o 75 años)",
        justificacion="Decide los seis numeros del procedimiento del "
                      "termoplastico que la norma de diseño no fija. Cada "
                      "uno toma el valor que la propia norma llama tipico o "
                      "el extremo desfavorable de su rango: el factor de "
                      "instalacion 1.5, el que la norma da como tipico para "
                      "la seguridad tradicional (menos exige control de "
                      "obra); el retardo de la deflexion 1.5, tipico segun "
                      "la norma, cuyo comentario recoge valores de 1.0 a "
                      "6.0; el coeficiente de cama 0.10, tipico, entre 0.083 "
                      "y 0.110; la deflexion admisible del cinco por ciento, "
                      "el limite que el comentario considera en general "
                      "apropiado; y las propiedades a 75 años, la columna "
                      "mas desfavorable de la tabla. No son todos el extremo "
                      "desfavorable de su ventana: el del coeficiente de cama "
                      "seria 0.110 y el del retardo 6.0, y la norma llama "
                      "tipicos a 0.10 y 1.5. El coeficiente de Poisson del "
                      "suelo no lo da ninguna fuente del repositorio --la "
                      "norma remite a la literatura geotecnica--: 0.40 es un "
                      "valor corriente para un relleno granular con finos, y "
                      "dentro de su ventana el desfavorable para el pandeo "
                      "general es 0.45",
        fuente="AASHTO LRFD 9a ed.: 12.12.3.5 (pag. impresa 12-78, K_gammaE; "
               "cita AASHTO_LRFD_9.12.12.3.5), 12.12.2.2 y C12.12.2.2 (pags. "
               "12-74 y 12-75, D_L, K_B y el 5 %; citas "
               "AASHTO_LRFD_9.12.12.2.2 y .C12.12.2.2), Tabla 12.12.3.3-1 "
               "(pag. 12-77, propiedades a 50 y 75 años) y 12.12.3.10.1e (pag. "
               "12-87, nu: la norma remite el coeficiente de Poisson del "
               "suelo a las referencias geotecnicas). El valor de nu NO TIENE "
               "FUENTE en el repositorio",
        reemplazado_por="Los parametros que fije el expediente con su "
                        "control de obra y, para nu, el del ensayo del "
                        "relleno",
        resolucion=Libre(
            que_lo_fija="el proyectista; la norma da el valor tipico o el "
                        "rango de cada uno, salvo nu",
            dominio="las ventanas por campo de `sensibilidad`; "
                    "anios_largo_plazo es 50 o 75",
        ),
    ),

    # --- T-5 (cierre) --- EL PERMISO DE 3.6.1.2.6a NO SE TOMA EN SILENCIO.
    # La FASE A despreciaba la carga viva pasados 8.0 ft de relleno que ademas
    # superan la luz, siempre, porque la fuente lo PERMITE («may be
    # neglected»). Un permiso del lado no conservador es una eleccion: medido
    # por el auditor en A-01 (tubo de concreto de 0.90 m, Clase II), entre
    # ~2.85 y 3.18 m de relleno el programa aceptaba un tubo que con la carga
    # viva no alcanza la clase. Valor de archivo: conservarla (decision del
    # dueño del proyecto, 2026-11-12).
    "carga_viva_bajo_relleno_alto": Criterio(
        valor="conservar",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("conservar", "despreciar_3_6_1_2_6a"),
        concepto="Que hace la Fase 8 con la carga viva cuando el relleno "
                 "sobre el conducto supera 8.0 ft (2.44 m) y ademas la luz: "
                 "conservarla, distribuida a traves del relleno como a "
                 "cualquier otra profundidad, o despreciarla como la norma "
                 "de diseño permite (AASHTO LRFD 3.6.1.2.6a)",
        justificacion="Decide si la carga viva sigue contando bajo un relleno "
                      "alto. La norma de diseño dice que en una alcantarilla "
                      "de un vano sus efectos se pueden despreciar cuando el "
                      "relleno supera 8.0 ft y la luz, y en una de varios "
                      "vanos cuando supera la distancia entre las caras "
                      "interiores de los muros extremos: es un permiso, no "
                      "una exigencia. A esa profundidad la carga viva es "
                      "pequeña pero no nula --en el tubo de concreto de "
                      "0.90 m con 2.9 m de relleno todavia aporta unos 8 kPa, "
                      "y decide si la Clase II alcanza--, el metodo de la "
                      "rueda distribuida sigue valiendo, y despreciarla hace "
                      "saltar la demanda un 14 % hacia abajo justo al cruzar "
                      "el umbral. Se adopta conservarla, que es el lado "
                      "seguro; tomar el permiso queda como alternativa "
                      "declarada",
        fuente="AASHTO LRFD 9a ed., Art. 3.6.1.2.6a, pag. impresa 3-26: «For "
               "single-span culverts, the effects of live load may be "
               "neglected where the depth of fill is more than 8.0 ft and "
               "exceeds the span length; for multiple span culverts, the "
               "effects may be neglected where the depth of fill exceeds the "
               "distance between inside faces of end walls» (citas "
               "AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE y #VARIOS_VANOS, las "
               "dos PERMISO). EL VALOR DE ARCHIVO LO DECIDIO EL DUEÑO DEL "
               "PROYECTO (2026-11-12). LA ELECCION NO ESTA EN NINGUNA NORMA",
        reemplazado_por="La decision del expediente sobre el permiso de "
                        "3.6.1.2.6a",
        resolucion=Libre(
            que_lo_fija="el proyectista",
            dominio="conservar o despreciar segun 3.6.1.2.6a; el conjunto "
                    "cerrado viaja en `sensibilidad`",
        ),
    ),

    # --- VE-4f --- EL TUBO DE CONCRETO CON 1.0 A 2.0 FT HASTA LA RASANTE.
    # AASHTO LRFD 3.6.1.2.6a manda repartir la carga viva «in accordance with
    # Eq. 4.6.2.10.2-1» (el ancho E de la franja, A LO LARGO del tubo) y
    # diseñar «for a depth of 1.0 ft»; NO dice que largo tiene el area
    # cargada A TRAVES del tubo, que es lo que decide cuanto del tandem cae
    # sobre el. Las dos lecturas que la fuente sostiene difieren solo con el
    # tandem sobre tubos de B_c entre s_a = 4 ft (1.22 m) y s_a + E_span
    # (1.82 m) --los de 1.05 a 1.50 m del catalogo--, y ahi en un 0 a 38 %
    # de W_L. Es una eleccion: sin valor (CLAUDE.md, «NO lo inventes»), con
    # la lectura recomendada en la ficha VE4F-01. NIVEL: de perfil por su
    # consumidor (M8, Fase 5); ninguna corrida de referencia lleva un tubo
    # de concreto somero, y lo mide `tests/test_ve4f_relleno_bajo.py`, que
    # corre la Fase 5 de un punto somero a perfil.
    "carga_viva_tubo_concreto_somero": Criterio(
        # --- VE-7 lote B, B8 (VE4F-01; decision del consultor Fable, triaje
        # VE-7, 2026-11-20) --- VALOR DE ARCHIVO: el largo del neumatico. Es
        # el area menor, la presion mayor y el lado seguro (con el tandem
        # sobre tubos de B_c entre s_a y s_a + E_span carga mas o igual que
        # la otra lectura, y con el camion igual), y C4.6.2.10.2 permite
        # despreciar el aumento por el relleno (cita
        # AASHTO_LRFD_9.C4.6.2.10.2#E_SPAN, PERMISO): la cota superior. La
        # otra lectura sigue en la ventana. Ficha VE7B-05.
        valor="largo_del_neumatico",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("largo_del_neumatico", "e_span_a_un_pie"),
        concepto="Largo del area cargada A TRAVES del tubo de concreto con "
                 "1.0 ft o mas y menos de 2.0 ft de relleno hasta la "
                 "rasante (AASHTO LRFD 3.6.1.2.6a con la franja de "
                 "4.6.2.10.2): el del neumatico, sin reparto por el relleno, "
                 "o el de la Eq. 4.6.2.10.2-2 a la profundidad de diseño de "
                 "1.0 ft",
        justificacion="Decide cuanto de los ejes cae sobre un tubo de "
                      "concreto con poco relleno, y con ello la carga viva "
                      "del metodo indirecto. La norma de diseño reparte el "
                      "eje a lo largo del tubo en el ancho de la franja de "
                      "las alcantarillas cajon y manda diseñar a 1.0 ft de "
                      "profundidad, pero no dice que largo tiene el area "
                      "cargada a traves del tubo. Las dos respuestas que la "
                      "fuente sostiene: el largo del neumatico, que es "
                      "despreciar el aumento por el relleno como el "
                      "comentario de la franja admite del lado conservador, "
                      "y el largo de la Eq. 4.6.2.10.2-2 a 1.0 ft. El camion "
                      "carga igual con las dos (todo su eje cae sobre "
                      "cualquier tubo del catalogo); el tandem difiere cuando "
                      "el tubo es mas ancho que la separacion de sus ejes y "
                      "mas angosto que esa separacion mas el largo del area: "
                      "con el largo del neumatico el segundo eje entra antes "
                      "y entero, y la carga es mayor o igual. Valor de "
                      "archivo: el largo del neumatico, la cota superior y "
                      "el lado seguro, que el comentario de la franja "
                      "permite (decision del consultor Fable, fichas "
                      "VE4F-01 y VE7B-05); la otra lectura queda en la "
                      "ventana para el dueño o el ingeniero estructural",
        fuente="AASHTO LRFD 9a ed.: Art. 3.6.1.2.6a, pag. impresa 3-26 (citas "
               "AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO y #UN_PIE: la Eq. "
               "4.6.2.10.2-1 y la profundidad de diseño de 1.0 ft); Art. "
               "4.6.2.10.2, pag. impresa 4-65 (cita "
               "AASHTO_LRFD_9.4.6.2.10.2#FRANJA, Eqs. 4.6.2.10.2-1 y -2 "
               "leidas renderizadas); y su comentario C4.6.2.10.2, misma "
               "pagina (cita AASHTO_LRFD_9.C4.6.2.10.2#E_SPAN, PERMISO: el "
               "aumento del largo «may be conservatively neglected»). LA "
               "ELECCION NO ESTA EN NINGUNA NORMA: la fuente da el ancho a lo "
               "largo del tubo y calla el largo a traves de el",
        reemplazado_por="Una disposicion de AASHTO (o del Manual de Puentes) "
                        "que diga el largo del area cargada sobre un tubo "
                        "de concreto con menos de 2.0 ft, o la decision del "
                        "expediente",
        resolucion=Libre(
            que_lo_fija="el dueño del proyecto o el ingeniero estructural "
                        "(ficha VE4F-01)",
            dominio="las dos lecturas de `sensibilidad`: "
                    "'largo_del_neumatico' (L_T, la cota superior) o "
                    "'e_span_a_un_pie' (L_T + 1.15 x 1.0 ft)",
        ),
    ),

    # --- T-5 (cierre) --- EL PERFIL DEL HDPE ES UN DATO DEL FABRICANTE, y sin
    # el no hay veredicto sobre un producto real. La FASE A verificaba el
    # HDPE con el perfil MINIMO de la Tabla A12-11 y daba «cumple» o «no
    # cumple»; la propia norma dice que esos minimos «are not meaningful for
    # design» y manda tomar las propiedades de secciones cortadas del tubo o
    # del fabricante (12.12.3.2 y C12.12.3.2). Decision del dueño del proyecto
    # (2026-11-12): entrada OPCIONAL sin valor por defecto; sin ella el HDPE
    # queda «no verificado con un producto real» --con el perfil minimo como
    # cota inferior impresa-- y NO se puede adoptar.
    "perfil_hdpe_fabricante": Criterio(
        valor=None,                 # OPCIONAL: sin valor, el HDPE no se adopta
        opcional=True,
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Propiedades de seccion del perfil del tubo de polietileno "
                 "corrugado que el proyecto especifique, por diametro "
                 "nominal en mm: area de pared (mm2/mm), momento de inercia "
                 "(mm4/mm) y diametro exterior (m), del catalogo o de la "
                 "certificacion del fabricante",
        justificacion="Decide con que perfil se verifica el tubo de "
                      "polietileno. Es opcional y no tiene valor por defecto: "
                      "la norma de diseño manda determinar el area, la "
                      "inercia y la geometria del perfil de secciones "
                      "cortadas del tubo u obtenerlas del fabricante, y su "
                      "comentario dice que los minimos que las "
                      "especificaciones traian no son significativos para el "
                      "diseño, porque la geometria del perfil varia con el "
                      "fabricante. Sin esta declaracion el programa calcula "
                      "con esos minimos solo para dar una cota inferior, la "
                      "imprime, y no adopta el HDPE: lo que falta es un dato "
                      "del producto, no una eleccion que el programa pueda "
                      "hacer. Declarado, cada diametro se verifica con sus "
                      "propiedades; un diametro que la declaracion no traiga "
                      "sigue sin dato. El area efectiva de la pared sigue "
                      "saliendo del minimo que la norma de producto exige al "
                      "ensayo de compresion, mientras no se implemente el "
                      "pandeo local por elementos del perfil, que necesita "
                      "su geometria idealizada",
        fuente="AASHTO LRFD 9a ed., Art. 12.12.3.2, pags. impresas 12-75 y "
               "12-76: «Section properties for thermoplastic pipe, including "
               "wall area, moment of inertia, and profile geometry should be "
               "determined from cut sections of pipe or obtained from the "
               "pipe manufacturer» (cita AASHTO_LRFD_9.12.12.3.2); "
               "C12.12.3.2: «these values have been minimum values and are "
               "not meaningful for design» (cita AASHTO_LRFD_9.C12.12.3.2). "
               "Tabla A12-11 (pag. 12-108) para los minimos de la cota "
               "inferior. EG-2013 508.02 b) (pag. impresa 982): el "
               "contratista entrega el certificado del fabricante. NINGUNA "
               "NORMA fija el perfil de un producto",
        sensibilidad=("sin declarar: el HDPE queda «no verificado con un "
                      "producto real» y no se adopta; la memoria imprime la "
                      "cota inferior con el perfil minimo de la Tabla A12-11",
                      "declarado: {'900': {'A_mm2_mm', 'I_mm4_mm', 'od_m'}, "
                      "...}, una clave de texto por diametro nominal en mm, "
                      "con las propiedades del "
                      "fabricante; ninguna puede ser menor que el minimo de "
                      "la Tabla A12-11 ni el diametro exterior mayor que su "
                      "maximo"),
        reemplazado_por="El catalogo o la certificacion del fabricante del "
                        "tubo que el expediente especifique (EG-2013 508.02 "
                        "b)",
        resolucion=Libre(
            que_lo_fija="el fabricante del tubo que el expediente "
                        "especifique: es un dato de producto, no una "
                        "eleccion del proyectista",
            dominio="{'<diametro nominal en mm>': {'A_mm2_mm' > 0, "
                    "'I_mm4_mm' > 0, 'od_m' > diametro}}; cada propiedad, no "
                    "menor que "
                    "el minimo de la Tabla A12-11 de AASHTO LRFD",
        ),
    ),

    # ----------------------- FASE 7: COMPATIBILIDAD GEOMETRICA ------------
    # 7.A ya NO queda resuelto con lo declarado: pide tres cosas que estan
    # mas arriba en este archivo -- 'cobertura_minima_aashto' (la tabla),
    # 'condicion_pavimento' (que fila) y 'espesor_pared_conducto' (donde esta
    # la clave fisica) --, y las dos ultimas bloquean. 'resguardo_HW_subrasante'
    # sigue cubriendo la otra condicion del maximo, la de la carga a la
    # entrada. Lo que 7.B abre aparte es la LONGITUD del conducto.

    "talud_terraplen": Criterio(
        # H:V. EXTREMO MAS TENDIDO del rango declarado. Es la eleccion
        # conservadora PARA LA VERIFICACION QUE LA LONGITUD GOBIERNA, que es
        # G2 --el amarre de la cota de salida al fondo del receptor, Sec. 7.B--:
        # un talud mas tendido alarga el conducto y con el la caida S*L, de
        # modo que la salida queda mas baja. Medido en A-01 al pasar de 1.5 a
        # 2.0 H:V: L de 16.461 a 18.635 m y cota de salida de 42.001 a 41.988
        # msnm, 13 mm mas cerca del fondo del receptor.
        #
        # Y HAY QUE DECIR DONDE EL SIGNO ES EL CONTRARIO, porque la version
        # anterior de esta nota afirmaba lo que no es. Sobre el CONTROL DE
        # SALIDA la longitud entra dos veces y con signos opuestos:
        #
        #     dHW/dL = K*n^2*V_llena^2 / (2*g*R_llena^(4/3))  -  S
        #
        # El primer termino es la friccion y el segundo la caida. Con los
        # numeros de A-01 --V_llena = 1.8344 m/s, R_llena = D/4 = 0.225 m,
        # n = 0.013, K = 19.63-- la friccion aporta 0.004158 m/m y la
        # pendiente resta 0.006, de modo que dHW/dL = -0.00184 m/m: alargar el
        # conducto BAJA el HW de salida. Medido: 0.997 -> 0.993 m entre los
        # mismos dos taludes, que es exactamente lo que predice la formula.
        # El signo se invierte cuando S cae por debajo de 0.004158 m/m con
        # esta geometria, y por eso no es una propiedad general del talud sino
        # de la pendiente de cada punto.
        #
        # Adoptar 2.0 es entonces conservador donde la longitud manda (G2) y
        # no lo es donde manda la pendiente (el control de salida). La memoria
        # imprime la ventana entera para que eso se pueda ver.
        valor=2.0,
        nivel=NIVEL_PERFIL,
        sensibilidad=(1.5, 2.0),     # H:V, banda de practica corriente en terraplenes viales
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Inclinacion del talud del terraplen en el punto de cruce, "
                 "como proyeccion horizontal por unidad de altura (H:V), para "
                 "la 'proyeccion de taludes' que Sec. 7.B suma al ancho de "
                 "plataforma al calcular la longitud del conducto",
        justificacion="Decide la inclinacion del talud del terraplen (H:V) "
                      "con que se calcula la proyeccion de taludes que Sec. "
                      "7.B suma al ancho de plataforma para la longitud del "
                      "conducto. La fuente proxima (Sec. 7.B de la hoja de "
                      "ruta) define la longitud como el ancho de plataforma "
                      "mas la proyeccion de taludes, afectada por el esviaje. "
                      "Lo que no resuelve: no entrega la inclinacion del "
                      "talud ni una regla para deducirla, y Sec. 1.2 no la "
                      "trae como columna -- el unico dato de seccion "
                      "transversal que llega por punto es el ancho de "
                      "plataforma. Tampoco se puede tapar con lo que ya esta "
                      "en el CSV: la altura de terraplen del punto "
                      "(cota_rasante - cota_terreno) da el brazo vertical del "
                      "talud, no su inclinacion. Se adopta declararla como "
                      "criterio, dentro de la banda de taludes "
                      "referenciales que el DG-2018 num. 304.10 da para "
                      "terraplenes de gravas, limo arenoso y arcilla (Tabla "
                      "304.11: 1.5, 1.75 y 2.0 H:V segun la altura sea menor "
                      "de 5 m, de 5 a 10 m o mayor de 10 m), mientras el "
                      "expediente vial no entregue la seccion tipica del "
                      "cruce -- la tabla es referencial y el material del "
                      "cuerpo del terraplen no es dato del expediente, de "
                      "modo que no fija el valor, lo acota --: sin longitud "
                      "no hay "
                      "caida S*L ni cota de salida que amarrar al fondo del "
                      "receptor, que es la otra mitad de 7.B, y adoptar en "
                      "silencio un talud de practica corriente moveria la "
                      "longitud, la caida y la cota de salida de todos los "
                      "puntos sin que nadie pueda rastrear de donde salio. "
                      "Sensibilidad (1.5, 2.0): los extremos de la fila de "
                      "gravas, limo arenoso y arcilla de la Tabla 304.11, "
                      "dentro de la que se movera la seccion tipica "
                      "pendiente; entre sus extremos cambia la proyeccion "
                      "horizontal por unidad de altura y, con ella, la "
                      "longitud, la caida S*L y la cota de salida de cada "
                      "punto",
        fuente="DG-2018 num. 304.10 'Taludes', Tabla 304.11 'Taludes "
               "referenciales en zonas de relleno (terraplenes)' (pag. "
               "impresa 208, PDF 209; registro DG2018.304.10#T304.11), que "
               "da la banda por material y altura y la llama referencial. "
               "PENDIENTE la seccion tipica del proyecto, que es la que fija "
               "el talud del cruce",
        reemplazado_por="Talud de la seccion tipica del expediente vial, o la "
                        "longitud medida directamente sobre la seccion "
                        "transversal de cada punto",
        verificacion_pendiente="Declarar si el talud es unico para el tramo o "
                               "varia por punto con la altura de terraplen. M7 "
                               "lo aplica hoy a los DOS taludes con la misma "
                               "altura (terraplen simetrico sobre el terreno "
                               "natural del cruce), que es lo unico que el CSV "
                               "permite calcular: si la seccion es asimetrica, "
                               "la longitud se mide y no se deduce",
        # `Libre` Y NO `DeEnsayo`, y el cambio no es cosmetico. Mientras el
        # criterio estuvo VACIO su resolucion decia la verdad: el numero
        # saldria de LEER la seccion tipica del expediente vial. Al declararlo
        # a nivel de perfil deja de salir de una lectura y pasa a salir de una
        # ELECCION dentro de una banda de practica, que es lo que `Libre`
        # nombra -- y la invariante de este archivo lo exige: un `de_ensayo`
        # con `sensibilidad` es una contradiccion, porque un dato leido no
        # tiene rango que elegir. La lectura no se pierde: sigue entera en
        # `reemplazado_por`, que es lo que cierra el criterio de verdad.
        resolucion=Libre(
            que_lo_fija="el proyectista, dentro de la banda referencial "
                        "de la Tabla 304.11 del DG-2018 para terraplenes de "
                        "gravas, limo arenoso y arcilla, mientras el "
                        "expediente vial no entregue la seccion tipica del "
                        "cruce",
            dominio="H:V > 0",
        ),
    ),
}
