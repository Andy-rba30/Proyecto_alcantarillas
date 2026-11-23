"""
Fichas de criterios adoptados del dominio: verificaciones.
"""

from typing import Dict
from src.modelos import Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_FLOAT,
    NIVEL_EXPEDIENTE,
    NIVEL_PERFIL,
)


CRITERIOS: Dict[str, Criterio] = {


    # ----------------------- FASE 5: VACIOS DE VERIFICACION ---------------
    # Tres filas de la tabla de Fase 5 (V5, V7, V8) enuncian el REQUISITO
    # pero no entregan la formula ni el dato con que M5 pueda evaluarlo.
    # Cada uno se detiene aqui, no en M5, para que quede escrito por que
    # falta y que lo resolveria -- nunca un valor supuesto en silencio.
    #
    # V7 ya NO es de esta clase: Fase 8 (M8_estructural.py) implementa el
    # procedimiento completo, y desde la correccion del marco LRFD es un
    # equilibrio de factores de carga, no un FS global. Lo que sigue faltando
    # son dos datos puntuales del procedimiento -- 'peso_especifico_relleno_kn_m3'
    # (mas abajo, seccion de Fase 8) y 'factores_carga_aashto' (seccion de
    # Fase 9, compartido con M9) -- no la formula ni el metodo, que ya estan
    # escritos.

    "origen_cota_fondo_entrada": Criterio(
        # DOS REGLAS IMPLEMENTADAS (`M5.ORIGENES_COTA_ENTRADA`), y la ventana
        # dejo de ser de un solo elemento. Hasta que el CSV trajo la columna
        # `cota_fondo_entrada` habia una sola, y este comentario decia --- con
        # razon entonces --- que declararla con una ventana de un elemento no
        # era una formalidad sino la diferencia entre "se eligio esta" y "esta
        # es la unica que el programa sabe calcular". Hoy SI hay entre que
        # elegir, y las dos opciones no son del mismo genero:
        #
        #   'cota_terreno'        adopta el terreno natural del cruce. Es la
        #                         lectura de PERFIL con las columnas que el
        #                         CSV siempre trae.
        #   'cota_fondo_entrada'  EXIGE la cota medida de la columna
        #                         homonima, y se detiene con
        #                         `DatoFaltanteError` si la fila la deja
        #                         vacia. No es "otra regla": es pedir el dato.
        #
        # Y HAY UNA TERCERA VIA QUE NO SE DECLARA AQUI, que es la que gobierna
        # de verdad: si la columna trae valor, MANDA, y este criterio ni
        # siquiera se invoca. Eso no es una opcion de la ventana --- es la
        # precedencia que el `reemplazado_por` de abajo lleva escrita desde
        # que este criterio existe.
        valor="cota_terreno",
        nivel=NIVEL_PERFIL,
        sensibilidad=("cota_terreno", "cota_fondo_entrada"),
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        concepto="Regla con la que se obtiene la cota del fondo de la entrada "
                 "(invert) de cada punto, msnm, cuando la columna "
                 "'cota_fondo_entrada' del CSV no la trae medida",
        justificacion="Decide la regla con que se obtiene la cota del fondo "
                      "de la entrada (invert) cuando la fila del CSV deja "
                      "vacia la columna 'cota_fondo_entrada'; cuando esa "
                      "columna trae valor, este criterio no se aplica -- un "
                      "dato medido no se sustituye por una regla adoptada, "
                      "que es lo que su `reemplazado_por` lleva escrito -- y "
                      "ni siquiera entra en `criterios_usados()`. HW es una "
                      "carga en metros sobre el fondo de la entrada (Sec. "
                      "4.2/4.3, `modelos.ResultadoHidraulico`), y convertirla "
                      "a cota -- lo que hacen V4, V7 y las dos condiciones "
                      "del tamizado 7.A -- exige esa cota. Lo que las fuentes "
                      "no resuelven: el CSV de Sec. 1.2 trae 'cota_terreno', "
                      "'cota_rasante', 'cota_subrasante' y "
                      "'cota_fondo_receptor' (la del receptor, o sea la "
                      "salida); la Sec. 7.B pide las cotas de entrada y "
                      "salida amarradas al perfil del cauce y a la cota de "
                      "fondo del receptor, sin decir cual de las dos lecturas "
                      "gobierna; y ninguna norma fija la regla. Se adopta que "
                      "la eleccion se declare aqui y no la tome el programa, "
                      "con dos valores admisibles implementados: "
                      "'cota_fondo_entrada', que exige la cota medida de la "
                      "columna homonima y se detiene con DatoFaltanteError si "
                      "la fila la deja vacia -- la declara quien quiere el "
                      "dato y no una regla --, y 'cota_terreno', adoptar el "
                      "terreno natural del cruce como fondo de la entrada, "
                      "que es la lectura mas defendible a nivel de perfil con "
                      "las columnas que el CSV si trae y la que hace "
                      "coincidir V4 con la segunda condicion de 7.A. La "
                      "columna medida existe porque los puntos de Familia C "
                      "de este expediente son pasos de canal -- el canal "
                      "atraviesa la via y continua, no hay cuerpo receptor "
                      "distinto -- y ahi el invert no se adopta: se hereda "
                      "del fondo del canal medido en el cruce; con "
                      "'cota_terreno' el invert queda a la cota del terreno "
                      "natural, por encima del fondo del canal en toda la "
                      "profundidad de la seccion (entre 0.30 y 0.95 m en los "
                      "cinco cruces de este corredor), y como HW se mide "
                      "sobre el invert, ese desfase se propaga entero a V4, a "
                      "V7 y al tamizado de 7.A. Sensibilidad de la regla "
                      "adoptada: 'cota_terreno' no es conservadora por "
                      "construccion -- si el invert real queda por debajo del "
                      "terreno (entrada excavada), la cota de HW calculada es "
                      "mayor que la real y V4 se vuelve exigente de mas; si "
                      "queda por encima (entrada elevada sobre relleno), V4 "
                      "se vuelve permisiva --, y por eso es adopcion "
                      "declarada [A] y no analogia normativa",
        fuente="PENDIENTE - NINGUNA norma fija esta regla: no la da el Manual "
               "de Hidrologia (Sec. 4.2/4.3 define HW sobre el fondo, no como "
               "obtener el fondo), no la da la hoja de ruta (Sec. 7.B enuncia "
               "el amarre sin regla de calculo) y no es columna de Sec. 1.2. "
               "Es una decision del proyectista sobre ESTE expediente",
        reemplazado_por="Cota de fondo de entrada MEDIDA por punto "
                        "(nivelacion del perfil longitudinal del cauce en el "
                        "cruce), como columna propia del CSV. El dia que el "
                        "expediente la entregue, este criterio deja de "
                        "aplicarse: un dato medido no se sustituye por una "
                        "regla adoptada",
        verificacion_pendiente="Declarar en la memoria, punto por punto, si "
                               "la entrada proyectada queda excavada o "
                               "elevada respecto del terreno natural: es la "
                               "diferencia entre esta adopcion y el invert "
                               "real, y es la que decide si V4 y 7.A quedaron "
                               "del lado seguro en ese punto",
        resolucion=Libre(
            que_lo_fija="el proyectista: NINGUNA norma fija esta regla "
                        "mientras el expediente no entregue la cota medida",
            dominio="declaracion de la regla de obtencion",
        ),
    ),

    "remanso_derecho_via": Criterio(
        # --- T-7b --- (PUNTO 0, decision del dueño del 2026-11-13). ELIGE EL
        # METODO con que V5 mide la extension del embalse aguas arriba, y
        # SIGUE SIN VALOR DE ARCHIVO: sin declararlo, V5 se detiene como
        # siempre y ningun resultado del fixture cambia. Hasta T-7b su forma
        # era `float` («la extension del remanso») y ningun modulo leia el
        # valor; el ancho del derecho de via NO va aqui: es el dato externo
        # `ancho_derecho_via_m`, por punto.
        valor=None,                 # VACIO: bloquea V5 para todo punto
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO.
        #   embalse_a_nivel   plano horizontal a la cota de la carga de
        #                     diseño de M4, cortando el fondo del cauce
        #                     aguas arriba de la boca. IMPLEMENTADO, con su
        #                     defecto dicho: la distancia incluye el tramo
        #                     natural del cauce (correcciones de T-7b, H2).
        #   cota_de_afectacion   la cota del embalse de diseño contra la cota
        #                     de afectacion aguas arriba (dato externo
        #                     `cota_afectacion_aguas_arriba_msnm`): el criterio
        #                     de NIVEL que el HDS-5 num. 2.2.5 sostiene.
        #                     IMPLEMENTADO (correcciones de T-7b, H2).
        #   perfil_de_remanso_paso_a_paso   la curva de remanso aguas arriba
        #                     por paso directo desde la boca, sobre la
        #                     seccion del cauce de aproximacion (dato externo
        #                     `seccion_cauce_aproximacion`), hasta donde la
        #                     lamina queda 'sobreelevacion_admisible_remanso_m'
        #                     sobre el tirante natural. IMPLEMENTADO en VE-4c
        #                     (ficha T7B-01): mide lo que la obra AÑADE.
        sensibilidad=("embalse_a_nivel", "cota_de_afectacion",
                      "perfil_de_remanso_paso_a_paso"),
        concepto="Metodo con que V5 mide la extension del embalse aguas "
                 "arriba de la alcantarilla, para compararla con el derecho "
                 "de via del punto (embalse dentro del derecho de via, sin "
                 "afectar a terceros ni a la faja marginal)",
        justificacion="Decide como se mide hasta donde llega, aguas arriba, "
                      "el embalse que la obra forma con el caudal de diseño. "
                      "La fila V5 de la hoja de ruta exige que quede dentro "
                      "del derecho de via, y lo que las fuentes escriben es "
                      "el requisito, no el metodo: el DG-2018 num. 304.07 "
                      "define la faja como bien de dominio publico y le fija "
                      "un ancho minimo por clase de carretera mas 5.00 m del "
                      "borde de las obras de drenaje (Tabla 304.09 y "
                      "304.07.02), sin enunciar condicion hidraulica alguna; "
                      "y el HDS-5 identifica la carga a la entrada con la "
                      "profundidad del embalse aguas arriba (num. 2.2.5, "
                      "cita HDS5_3ED.2.2.5#EMBALSE) sin dar como medir su "
                      "extension. Lo que ninguna resuelve es el metodo, y "
                      "por eso este criterio no tiene valor de archivo: lo "
                      "elige el proyectista. Con «cota_de_afectacion», "
                      "el metodo que la fuente sostiene, se compara la cota "
                      "del embalse de diseño (solera de entrada + HW de M4) "
                      "con la cota del terreno o del bien a proteger en el "
                      "limite del derecho de via aguas arriba, dato externo "
                      "por punto de la topografia "
                      "(`cota_afectacion_aguas_arriba_msnm`): el HDS-5 dice "
                      "que la carga de diseño no deberia superar la "
                      "admisible y que la admisible puede ser la cota de "
                      "daño de un bien aguas arriba (citas "
                      "HDS5_3ED.2.2.5#NO_EXCEDER y "
                      "HDS5_3ED.2.2.5a#COTA_DE_DANO). Con «embalse_a_nivel» el "
                      "embalse es un plano horizontal a la cota de la carga "
                      "de diseño, que corta el fondo del cauce a una "
                      "distancia HW / S_cauce aguas arriba de la boca; esa "
                      "distancia, sumada a la de la boca al eje de la via y "
                      "proyectada por el esviaje, se compara con la mitad "
                      "del ancho declarado del derecho de via. Sus supuestos "
                      "van en el paso de la memoria: el cauce sigue la "
                      "direccion del eje del conducto con la pendiente del "
                      "CSV, la faja es simetrica respecto del eje de la via, "
                      "no hay topografia lateral (no se mide si el agua se "
                      "extiende a lo ancho), y el plano horizontal no es la "
                      "curva de remanso: en un cauce de pendiente suave el "
                      "perfil real se prolonga mas alla, con tirantes "
                      "mayores que el normal, de modo que la distancia es "
                      "una cota inferior de la extension del remanso. Y "
                      "tiene un defecto que se dice sin rodeos: el plano "
                      "corta el FONDO, de modo que la distancia incluye el "
                      "tramo en que el cauce ya llevaria agua sin la obra; "
                      "como medida de lo que la obra añade es una cota "
                      "SUPERIOR, y con los anchos de la Tabla 304.09 (16 a "
                      "40 m) solo cumple en cauces de pendiente fuerte. "
                      "Lo que la obra añade lo mide el tercer metodo, el "
                      "perfil de remanso: la curva de la lamina por paso "
                      "directo desde la boca sobre la seccion del cauce de "
                      "aproximacion (`seccion_cauce_aproximacion`, dato "
                      "externo por punto), hasta donde la lamina queda a la "
                      "sobreelevacion admisible sobre el tirante natural del "
                      "cauce ('sobreelevacion_admisible_remanso_m'); la "
                      "distancia, sumada a la de la boca y proyectada por el "
                      "esviaje, se compara con la mitad del ancho del derecho "
                      "de via, como en el embalse a nivel",
        fuente="Fase 5, V5 de la hoja de ruta. El requisito juridico: "
               "DG-2018 num. 304.07.01 y 304.07.02 con la Tabla 304.09 "
               "(pags. impresas 198-199, registro DG2018.304.07.02), y la "
               "Ley 29338 (ausente de normas/) para la faja marginal. La "
               "carga como profundidad del embalse: HDS-5 num. 2.2.5, pag. "
               "impresa 2.9 (PDF 71). El metodo es del proyecto",
        reemplazado_por="Perfil de remanso calculado aguas arriba del punto "
                        "(paso a paso o HEC-RAS) sobre la topografia del "
                        "cauce",
        resolucion=Libre(
            que_lo_fija="el proyectista: ninguna fuente de normas/ da el "
                        "metodo de la extension del embalse",
            dominio="uno de los metodos de la ventana",
        ),
    ),

    "sobreelevacion_admisible_remanso_m": Criterio(
        # --- VE-4c --- (ficha T7B-01) EL FIN DEL PERFIL DE REMANSO DE V5. Lo
        # lee solo V5 con 'remanso_derecho_via' = «perfil_de_remanso_paso_a_
        # paso» (`M5._v5_perfil_de_remanso`), y SIN VALOR DE ARCHIVO: sin
        # declarar ese metodo nadie lo pide y ningun resultado cambia;
        # declarado el metodo, V5 se detiene aqui con CriterioPendienteError.
        # NIVEL: expediente, el de V5 (diferida a perfil). Ninguna corrida de
        # tests/test_nivel_medido.py lo alcanza (V5 se detiene antes, en el
        # metodo vacio): lo mide tests/test_ve4c_v5_remanso.py, y que solo lo
        # lee V5 lo comprueba test_nivel_medido por AST.
        valor=None,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        # La ventana es la del HDS-5 num. 2.2.5 b. (de 0 a 1 ft, 0.30 m). El 0
        # entra: es un valor que una autoridad puede exigir, y con el V5 dice
        # que la M1 de un cauce suave no tiene final (metodo no evaluable) en
        # vez de cortarla en un numero que nadie declaro.
        sensibilidad=(0.0, 0.30),
        concepto="Sobreelevacion de la lamina del cauce de aproximacion sobre "
                 "su tirante natural (m) por debajo de la cual el remanso de "
                 "la obra no se cuenta como afectacion: el perfil de remanso "
                 "de V5 termina donde la lamina baja a y_n + este valor, y su "
                 "longitud es la que se compara con el derecho de via",
        justificacion="Decide donde termina el remanso que V5 compara con la "
                      "faja del derecho de via cuando el metodo declarado es "
                      "el perfil de remanso. En un cauce de pendiente suave "
                      "la curva M1 se acerca al tirante natural sin "
                      "alcanzarlo, de modo que la distancia hasta la que la "
                      "obra eleva la lamina solo tiene final si se fija "
                      "cuanta elevacion no se cuenta; un valor menor alarga "
                      "el remanso y puede hacer que V5 no cumpla. El HDS-5 "
                      "describe ese aumento admisible de la superficie del "
                      "agua sobre la que hay sin la obra como una restriccion "
                      "regulatoria de EE. UU. (cita HDS5_3ED.2.2.5b#AUMENTO), "
                      "entre 0 m y 0.30 m segun el sitio; el MTC no fija "
                      "ninguno. Elegir el valor es adopcion del proyectista, y "
                      "con 0 m el cauce suave no da distancia finita. En un "
                      "cauce de pendiente fuerte el remanso termina en el "
                      "resalto y este valor solo lo acorta si supera la "
                      "diferencia entre el conjugado y el tirante natural",
        fuente="Adopcion del proyectista dentro de la ventana que describe el "
               "HDS-5 num. 2.2.5 b. (pag. impresa 2.10, PDF 72, registro "
               "HDS5_3ED.2.2.5b#AUMENTO): el aumento admisible de la "
               "superficie del agua por una obra en la llanura de inundacion "
               "del programa de la FEMA. Ninguna fuente peruana de normas/ lo "
               "fija",
        resolucion=Libre(
            que_lo_fija="el proyectista, o la autoridad del agua si fija un "
                        "aumento admisible del nivel aguas arriba",
            dominio="m, 0 <= valor <= 0.30",
        ),
    ),

    # V2b, la mitad [A] de la fila: el acceso de mantenimiento. La mitad
    # evaluable de V2b -- el indicador de pendiente del HDS-5 num. 5.3.3 -- la
    # calcula `M5.v2b_sedimentacion` y NO pasa por aqui: es una comparacion
    # entre dos numeros de la fuente y del CSV, no una adopcion. Lo que SI
    # pasa por aqui desde PF-4 es el REGIMEN con que se aplica esa
    # comparacion (`regimen_v2b`, la entrada siguiente).
    "acceso_mantenimiento_v2b": Criterio(
        # LA OPCION QUE RESUELVE EL PROBLEMA, no la que sale gratis. Las
        # tres de la ventana son declaraciones legitimas y solo una prevé la
        # obra: un buzon o camara de limpieza en cabecera deja entrar al
        # personal de mantenimiento sin desmontar nada. La segunda supone que
        # el cabezal alcanza y no anade obra; la tercera es la declaracion
        # honesta de que el punto NO se va a poder limpiar, y existe para que
        # esa decision se tenga que escribir en vez de ocurrir por omision --
        # que es lo que pasaba antes de S20, cuando V2b no existia.
        valor="camara_o_buzon_en_cabecera",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        concepto="Como se resuelve el acceso de mantenimiento para limpieza "
                 "del conducto en cada punto, que es la mitad [A] de la fila "
                 "V2b de la Fase 5 y contenido de los PLANOS (Sec. 11, "
                 "entregable 7)",
        justificacion="Decide como se resuelve el acceso de mantenimiento "
                      "para limpieza del conducto en cada punto: la mitad "
                      "adoptada de la fila V2b de la Fase 5, que se "
                      "materializa en un plano que este software no dibuja "
                      "(Sec. 11, entregable 7). La fila V2b tiene dos mitades "
                      "y este criterio es la segunda: la primera -- el "
                      "indicador de sedimentacion -- si se evalua, porque el "
                      "num. 5.3.3 de HDS-5 nombra dos indicadores y uno de "
                      "ellos, la pendiente del conducto menor que la del "
                      "cauce natural, son dos numeros que este calculo ya "
                      "tiene. Lo que las fuentes no resuelven: ninguna norma "
                      "de normas/ prescribe el dispositivo de acceso -- el "
                      "HDS-5 num. 5.3.3 describe el fenomeno, y el diametro "
                      "minimo de 0.90 m (num. 4.1.1.3.4 a) garantiza que una "
                      "persona quepa en el conducto, no que pueda entrar en "
                      "el: lo segundo depende del cabezal, de las aletas y de "
                      "si hay una camara o buzon en cabecera, que es justo lo "
                      "que aqui se declara. Se adopta declarar el dispositivo "
                      "por punto y no elegir una opcion por defecto: cada una "
                      "de las tres opciones de la sensibilidad tiene "
                      "consecuencia de obra y de costo, ninguna norma peruana "
                      "la impone, y sin esta declaracion un expediente podria "
                      "cerrar con los planos sin acceso de limpieza y nada lo "
                      "recordaria",
        # --- T-2 --- (cadena T; INF-0.5, punto 6): la `fuente` dejo de
        # decir «PENDIENTE». La mitad [N] de la fila es el num. 4.1.1.3.7 d)
        # «Mantenimiento y limpieza» (cita MC_HHD.4.1.1.3.7d, EXIGENCIA sin
        # numero), que el paso de V2b imprime; lo que sigue siendo [A] es el
        # DISPOSITIVO, que el numeral no prescribe. Y el dato de si el
        # acceso esta PREVISTO en cada punto entra, opcional, por
        # `acceso_mantenimiento_previsto` de --datos-externos.
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.7 d) 'Mantenimiento y "
               "limpieza', pag. impresa 80 (PDF 83), cita MC_HHD.4.1.1.3.7d: "
               "las dimensiones de la alcantarilla deben permitir el "
               "mantenimiento y la limpieza en su interior, y hace falta un "
               "programa de mantenimiento con inspecciones. Es la EXIGENCIA "
               "[N] de la fila V2b de la hoja de ruta ('[N] + [A]'); el "
               "DISPOSITIVO de acceso no lo prescribe ese numeral ni ninguna "
               "otra norma de normas/ (el HDS-5 num. 5.3.3 describe el "
               "fenomeno), y es lo que este criterio adopta. Sec. 11, "
               "entregable 7 (planos)",
        sensibilidad=("camara_o_buzon_en_cabecera",
                      "acceso_por_cabezal_sin_obra_adicional",
                      "sin_acceso_declarado_como_limitacion"),
        reemplazado_por="La lamina de planos del expediente que dibuje el "
                        "dispositivo de acceso de cada punto. El dia que "
                        "exista, este criterio deja de ser una declaracion y "
                        "pasa a ser la referencia a esa lamina",
        verificacion_pendiente="El SEGUNDO indicador del num. 5.3.3 -- "
                               "'roughness greater than the channel' -- se "
                               "evalua desde VE-5 solo como INDICADOR, y "
                               "solo donde el punto declara la seccion del "
                               "cauce de aproximacion (su n de Manning, que "
                               "no es columna de Sec. 1.2); sin ella V2b "
                               "verifica un indicador de los dos, y la "
                               "memoria lo dice en la propia fila",
        resolucion=Libre(
            que_lo_fija="el proyectista, en los planos: ninguna norma de "
                        "normas/ prescribe el dispositivo de acceso para "
                        "limpieza de una alcantarilla",
            dominio="declaracion del dispositivo de acceso; el conjunto "
                    "cerrado de valores admisibles viaja en `sensibilidad`",
        ),
    ),

    # V2b, el REGIMEN con que se aplica la mitad evaluable (PF-4). Hasta PF-4
    # `M5.v2b_sedimentacion` aplicaba el indicador de pendiente como umbral
    # duro «por decision conservadora del proyecto»: un [A] cableado y sin
    # ficha, que es lo que la constitucion prohibe. Aqui vive la eleccion; la
    # COMPARACION (S_conducto >= S_cauce) sigue en M5 y no pasa por aqui.
    "regimen_v2b": Criterio(
        # NO VACIO, y es deliberado: dejarlo vacio detendria los cuatro
        # puntos de toda corrida de perfil. PF-4 lo dejo en `umbral_duro`,
        # la conducta que el proyecto tenia desde S20.
        #
        # --- T-2 --- (cadena T, 2026-11-11; INF-0.5, punto 6 del encargo):
        # EL VALOR DE ARCHIVO PASA A `indicador_con_aviso`, que es aplicar la
        # fuente como la fuente esta escrita --«are key indicators of
        # potential problems», sin umbral-- y la unica lectura coherente con
        # admitir el barril horizontal (INF-5.1.6): con el umbral duro un
        # conducto con S = 0 quedaba descartado SIEMPRE frente a un cauce de
        # pendiente positiva, y lo que T-2 abria por M3 y M4 se cerraba aqui.
        # `umbral_duro` sigue en la ventana y se barre (`--barrido
        # regimen_v2b=indicador_con_aviso,umbral_duro`). MEDIDO antes de
        # cambiarlo: ningun punto de la linea base tiene S_conducto <
        # S_cauce salvo C-01 en la corrida ancha, que se detiene antes, en
        # los criterios del cajon; ningun diametro se mueve y ninguna corrida
        # de la linea base cambia que puntos dimensiona. LA ETIQUETA SIGUE
        # SIENDO [A] y no [C], que es lo que el encargo pedia: la fuente
        # define el indicador y NO prescribe el regimen, y una eleccion con
        # dos opciones defendibles es [A] con ventana (ficha T2-04).
        valor="indicador_con_aviso",
        nivel=NIVEL_PERFIL,         # lo consume V2b, que la corrida de perfil
                                    # invoca como obligatoria (servicio y M5)
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO, que es la ventana entera. «umbral_duro»: el
        # indicador disparado -- S_conducto < S_cauce -- deja la Verificacion
        # con cumple=False, MD descarta la seccion y prueba la siguiente, y
        # si ninguna cumple el punto no dimensiona. «indicador_con_aviso»: V2b
        # se evalua IGUAL (mismos numeros, mismo margen), la Verificacion sale
        # con cumple=True, el paso lleva veredicto INDICADOR (TipoDeVeredicto,
        # modelos.py) que la memoria pinta como AVISO con el texto literal de
        # la fuente, y el diametro NO se descarta. El segundo indicador del
        # numeral no entra en ninguna de las dos: ver `verificacion_pendiente`.
        sensibilidad=("umbral_duro", "indicador_con_aviso"),
        concepto="Con que regimen se aplica el indicador de sedimentacion del "
                 "HDS-5 num. 5.3.3 (pendiente del conducto frente a la del "
                 "cauce natural) en la fila V2b: como umbral duro que detiene "
                 "el punto, o como indicador que se imprime con aviso y no "
                 "descarta el diametro",
        justificacion="Decide que hace el pipeline cuando el indicador de "
                      "pendiente de V2b se dispara. La fuente (HDS-5 3.a ed., "
                      "num. 5.3.3, pag. impresa 5.11, cita "
                      "HDS5_3ED.5.3.3#INDICADORES) DEFINE dos indicadores de "
                      "posibles problemas de sedimentacion -- la pendiente "
                      "del barril menor que la del cauce y la rugosidad "
                      "mayor que la del cauce -- y no fija umbral, cifra ni "
                      "consecuencia: en toda la pagina no hay una exigencia "
                      "ni una recomendacion sobre que hacer con ellos. "
                      "Convertir un indicador en condicion de aceptacion es "
                      "por tanto una eleccion del proyectista, y una "
                      "eleccion se declara con ficha, ventana y procedencia "
                      "en vez de vivir cableada en la verificacion. Las dos "
                      "opciones son defendibles y no valen lo mismo en toda "
                      "obra. «indicador_con_aviso», el valor del archivo, "
                      "aplica la fuente como esta escrita: un indicador se "
                      "reconoce y se declara, no rechaza una seccion. El "
                      "indicador se evalua igual (mismos numeros, mismo "
                      "margen), se imprime con el texto literal de la fuente "
                      "y el veredicto de indicador, y queda como constancia "
                      "de mantenimiento junto al acceso de limpieza declarado "
                      "en 'acceso_mantenimiento_v2b'. Tres razones lo "
                      "sostienen como valor de archivo. Primera: la fuente no "
                      "fija umbral ni consecuencia, y de la entrada deprimida "
                      "dice que la sedimentacion ocurre sobre todo con "
                      "caudales bajos y que el conducto suele limpiarse solo "
                      "con los altos (cita HDS5_3ED.5.3.3#DEPRESION). "
                      "Segunda: la misma fuente admite el barril horizontal "
                      "(cita HDS5_3ED.3.3.4#HORIZONTAL), que con el umbral "
                      "duro quedaria descartado siempre frente a un cauce de "
                      "pendiente positiva. Tercera: en un cruce de canal "
                      "(Familia C) la pendiente del conducto suele venir "
                      "fijada por el canal, y con el umbral duro una "
                      "pendiente menor que la del cauce (0.004 m/m frente a "
                      "0.006 m/m en el punto C-01 del corredor) descarta la "
                      "progresion entera de marcos aunque cumplan todo lo "
                      "demas. «umbral_duro» es la lectura mas conservadora: "
                      "obliga a reconsiderar la rasante en una entrada "
                      "deprimida, y queda en la ventana para barrerla. "
                      "Ninguna de las dos opciones mueve un numero de "
                      "calculo: solo cambia si el punto se detiene",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), num. 5.3.3 'Sedimentation', "
               "pag. impresa 5.11 (PDF 147): cita HDS5_3ED.5.3.3#INDICADORES "
               "(caracter DEFINICION) y su contracara HDS5_3ED.5.3.3#ALINEADO. "
               "La fuente define el indicador; el regimen con que se aplica "
               "no sale de ella ni de la hoja de ruta: es adopcion del "
               "proyectista (Fundamento F5.V2b.REGIMEN, verbo DEFINE)",
        verificacion_pendiente="El SEGUNDO indicador del num. 5.3.3 -- "
                               "'roughness greater than the channel' -- no lo "
                               "gobierna este criterio: desde VE-5 se evalua "
                               "como INDICADOR bajo los dos regimenes (aviso, "
                               "nunca veredicto) donde el punto declara la "
                               "seccion del cauce de aproximacion, cuyo n es "
                               "el del CAUCE NATURAL; sin ella no se evalua "
                               "ni se supone. Este criterio "
                               "gobierna solo lo que se hace con el primero. "
                               "T-2 (INF-3.2.9) leyo el numeral entero: ademas "
                               "de los dos indicadores nombra como factores la "
                               "magnitud del caudal, el material del cauce, "
                               "los cauces en agradacion, las instalaciones "
                               "multibarril y las entradas deprimidas, ninguno "
                               "con cifra; el n del cauce no se supone ni se "
                               "le pone valor por defecto (ficha T2-06 de "
                               "docs/decisiones_diferidas.md)",
        resolucion=Libre(
            que_lo_fija="el proyectista: la fuente define un indicador y no "
                        "prescribe que hacer cuando se dispara; ninguna "
                        "norma de normas/ ni la hoja de ruta lo fija",
            dominio="declaracion del regimen; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    # =======================================================================
    # --- T-2 --- (cadena T, 2026-11-11) · tres criterios [A] de perfil
    # =======================================================================
    # La banda de pendiente del conducto (V10, INF-3.2.7) y la lectura del
    # borde libre cuando el barril va lleno por el nivel del receptor (V1,
    # INF-3.2.6). Los consume M5, y M7 lee la banda desde T-6 por
    # `M5.limites_de_pendiente()` (`M7.pendiente_adoptada`).
    "pendiente_minima_conducto": Criterio(
        # EL VALOR ES 0.0 Y NO UNA CIFRA DE PRACTICA, y es deliberado: es lo
        # unico que una fuente de normas/ sostiene. El Manual no da numero;
        # el HDS-5 admite expresamente el barril horizontal. Las cifras que
        # circulan (0.5 % «para autolimpieza», 1 % en marcos, 2 % en TMC) son
        # practica de expediente y ninguna esta en normas/: por eso van en la
        # VENTANA --hasta 0.005-- y no en el valor. Quien quiera exigir una
        # pendiente minima positiva la declara y la barre.
        valor=0.0,
        # lo consumen V10 (Fase 5) y, desde T-6, M7.pendiente_adoptada (antes
        # de la Fase 4): las dos corren a perfil
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Pendiente longitudinal MINIMA que el proyecto admite en el "
                 "barril de una alcantarilla (m/m); M7 eleva a ella la del "
                 "cauce y V10 juzga con ella la declarada",
        justificacion="Decide por debajo de que pendiente el proyecto no "
                      "tiende un conducto. El Manual (num. 4.1.1.3.3) exige "
                      "que la pendiente no altere desmesuradamente la erosion "
                      "y la sedimentacion y que sus cambios se estudien con "
                      "cuidado, sin fijar cifra; el HDS-5 (num. 3.3.4) admite "
                      "el barril horizontal: dice que sus procedimientos de "
                      "control de entrada y de salida se pueden aplicar "
                      "razonablemente a un conducto sin pendiente (cita "
                      "HDS5_3ED.3.3.4#HORIZONTAL). Ninguna fuente de normas/ "
                      "fija una pendiente minima en numeros, y el valor "
                      "adoptado es el que la fuente sostiene: 0.0 m/m, el "
                      "barril horizontal admitido. La pendiente minima no es "
                      "lo que protege de la sedimentacion en este calculo: "
                      "eso lo hacen V2, que exige la velocidad minima con el "
                      "caudal de diseño, y V2b, que avisa cuando el conducto "
                      "queda mas plano que su cauce. Con 0.0 m/m la "
                      "verificacion V10 no rechaza ningun conducto por abajo "
                      "y no mueve ningun diseño; lo que hace es dejar escrito "
                      "que no se exige pendiente minima y por que. "
                      "Sensibilidad: de 0.0 m/m a 0.005 m/m (0.5 %), la cifra "
                      "de practica mas extendida para autolimpieza. Subirla "
                      "rechaza los conductos mas tendidos: con 0.005 m/m el "
                      "punto C-01 de la corrida ancha (pendiente del conducto "
                      "declarada de 0.004 m/m) dejaria de cumplir V10, y "
                      "ninguno de los otros. El reparto con M7 (T-6): una "
                      "pendiente de cauce por debajo del minimo no se "
                      "rechaza, se eleva a el antes del diseño "
                      "(M7.pendiente_adoptada, origen «minima» del paso "
                      "7.B.1, con aviso): el conducto cae mas que su cauce, "
                      "la salida queda bajo el cauce natural y G2 la juzga "
                      "contra el fondo del receptor. V10 solo rechaza una "
                      "pendiente declarada (S_conducto), que M7 no toca",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.3 'Pendiente longitudinal', "
               "pag. impresa 71 (PDF 74), cita MC_HHD.4.1.1.3.3: exigencia "
               "cualitativa, sin cifra. HDS-5 3a ed. (FHWA-HIF-12-026), num. "
               "3.3.4 'Culverts with Horizontal or Adverse Slopes', pag. "
               "impresa 3.25 (PDF 107), cita HDS5_3ED.3.3.4#HORIZONTAL: "
               "admite S = 0. Ninguna de las dos fija un minimo; el valor es "
               "adopcion del proyectista (Fundamento F5.V10, verbo DEFINE)",
        reemplazado_por="Una pendiente minima que fije el expediente por "
                        "material y por tipo de cauce, con su fuente, o la "
                        "que resulte de un estudio de transporte de "
                        "sedimentos del cauce",
        sensibilidad=(0.0, 0.005),
        resolucion=Libre(
            que_lo_fija="el proyectista: ni el Manual ni el HDS-5 fijan una "
                        "pendiente minima en cifras; el HDS-5 admite el "
                        "barril horizontal",
            dominio="m/m, de 0.0 (barril horizontal) a 0.005",
        ),
    ),

    "pendiente_maxima_conducto": Criterio(
        valor=0.10,
        # lo consumen V10 (Fase 5) y, desde T-6, M7.pendiente_adoptada (antes
        # de la Fase 4): las dos corren a perfil
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Pendiente longitudinal MAXIMA que el proyecto admite en el "
                 "barril de una alcantarilla (m/m); M7 limita a ella la del "
                 "cauce y V10 juzga con ella la declarada",
        justificacion="Decide por encima de que pendiente el proyecto no "
                      "tiende un conducto sin un estudio aparte. El Manual "
                      "(num. 4.1.1.3.3) no fija cifra. El HDS-5 (num. 5.4.4 "
                      "'Barrels on Steep Slopes') DESCRIBE que la mayoria de "
                      "las alcantarillas se construyen con pendientes "
                      "menores del 10 % y que para ellas no se usan medidas "
                      "estructurales especiales; entre el 10 % y el 20 % "
                      "pide atar las ultimas secciones del tubo, y por "
                      "encima del 20 % medidas estructurales adicionales y "
                      "la cautela hidraulica del USBR. El alcance del "
                      "proyecto no incluye el dimensionamiento de anclajes, "
                      "ataduras ni bloques de empuje: 0.10 m/m es el limite "
                      "hasta el que la fuente dice que no hacen falta, y por "
                      "eso es el valor adoptado y el techo de la ventana. El "
                      "piso de la ventana, 0.02 m/m, es la pendiente con que "
                      "el HDS-5 traza sus curvas de control de entrada (num. "
                      "A.3), porque el efecto de la pendiente es chico y "
                      "fijarla ahi deja la carga del lado conservador en "
                      "pendientes mayores: un proyecto que no quiera salir de "
                      "la pendiente de las cartas declara 0.02 m/m. La "
                      "pendiente maxima no sustituye a V3: la velocidad "
                      "maxima admisible del revestimiento se sigue "
                      "verificando con la velocidad calculada, y puede "
                      "rechazar un conducto bastante antes del 10 % (en "
                      "concreto, 6.0 m/s). El reparto con M7 (T-6): una "
                      "pendiente de cauce por encima del maximo no se "
                      "rechaza, se limita a el antes del diseño "
                      "(M7.pendiente_adoptada, origen «maxima» del paso "
                      "7.B.1, con aviso): el conducto queda mas tendido que "
                      "su cauce, el desnivel (S_cauce - S_maxima) x L pide "
                      "una estructura de caida o de disipacion que este "
                      "calculo no dimensiona, y V2b lo juzga segun "
                      "'regimen_v2b'. V10 solo rechaza una pendiente "
                      "declarada (S_conducto), que M7 no toca. Sensibilidad: "
                      "en el corredor del repositorio la pendiente va de "
                      "0.004 m/m a 0.010 m/m y ningun valor de la ventana "
                      "rechaza un punto ni acota la pendiente de su cauce",
        fuente="HDS-5 3a ed. (FHWA-HIF-12-026), num. 5.4.4 'Barrels on Steep "
               "Slopes', pag. impresa 5.16 (PDF 152), citas "
               "HDS5_3ED.5.4.4#PENDIENTE_10 («Most culverts are constructed "
               "on slopes that are less than 10% ... no special structural "
               "measures are used», caracter DEFINICION) y "
               "HDS5_3ED.5.4.4#PENDIENTE_20; num. A.3, pag. impresa A.2 (PDF "
               "191), cita HDS5_3ED.A.3#PENDIENTE_2 (curvas al 2 %). El "
               "Manual de Hidrologia, num. 4.1.1.3.3, pag. impresa 71, no "
               "fija cifra. La fuente describe una practica; el limite es "
               "adopcion del proyectista (Fundamento F5.V10, verbo DEFINE)",
        reemplazado_por="El diseño estructural del conducto en pendiente "
                        "(anclajes, ataduras entre tubos, bloques de empuje) "
                        "que el expediente desarrolle para un punto "
                        "concreto, que permitiria admitir pendientes mayores "
                        "en ese punto",
        sensibilidad=(0.02, 0.10),
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre lo que el HDS-5 num. 5.4.4 "
                        "describe: bajo el 10 % no se usan medidas "
                        "estructurales especiales",
            dominio="m/m, de 0.02 (pendiente de las curvas del HDS-5) a 0.10",
        ),
    ),

    "borde_libre_bajo_tw_ahogante": Criterio(
        # EL VALOR DE ARCHIVO ES LA CONDUCTA QUE EL PROYECTO YA TENIA (EXT-3):
        # con el TW sobre la clave V1 NO cumple. No se cambia: «aviso» puede
        # hacer dimensionar puntos que hoy no dimensionan --la corrida
        # estrecha de la linea base, que toma el TW de la via 4-- y mover un
        # diametro es decision del dueño (parada (c) de la cadena T). La
        # alternativa queda en la ventana y se barre.
        valor="no_cumple",
        nivel=NIVEL_PERFIL,         # lo consume V1 (Fase 5), que corre a perfil
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO. «no_cumple»: cuando el nivel del receptor
        # toma el borde libre del barril V1 queda con cumple=False, como
        # desde EXT-3. «aviso»: V1 juzga el borde libre con el tirante PROPIO
        # del caudal de diseño (el normal de Manning), que es lo que el
        # diametro puede resolver; si ese cumple, el remanso del receptor se
        # imprime con veredicto INDICADOR (aviso) y no descarta el diametro;
        # si no cumple, V1 NO cumple igual. Con S = 0 no hay tirante normal
        # con que separar los dos casos y V1 no cumple bajo las dos opciones.
        #
        # EL CASO ES UNO A LO LARGO DE TODO EL TW: el TW por encima del
        # llenado admisible (TW/D > 0.75 con el umbral por defecto), llegue o
        # no a la clave. La primera redaccion de T-2 lo reconocia solo con el
        # barril LLENO (TW >= D) y el auditor adversarial midio que «aviso»
        # quedaba discontinua: mas ahogamiento era mas permisivo, y el tubo
        # chico pasaba donde el grande no. El nombre de la clave conserva
        # «ahogante» y cubre los dos tramos.
        sensibilidad=("no_cumple", "aviso"),
        concepto="Que hace V1 (borde libre) cuando es el nivel del cuerpo "
                 "receptor, y no el caudal de diseño, el que deja al barril "
                 "sin el borde libre: el tirante del receptor por encima del "
                 "llenado admisible, llegue o no a la clave",
        justificacion="Decide como se lee el borde libre cuando el nivel del "
                      "receptor remansa o ahoga el barril. El Manual (num. "
                      "4.1.1.3.7 b), pag. impresa 79) prohibe diseñar la "
                      "alcantarilla para trabajar a seccion llena, por el "
                      "riesgo de obstruccion (cita MC_HHD.4.1.1.3.7b#LLENA), "
                      "y recomienda un borde libre minimo del 25 % (cita "
                      "MC_HHD.4.1.1.3.7b). Hay dos maneras de llegar a la "
                      "seccion llena y no son la misma. Por el caudal de "
                      "diseño: el conducto es chico para su caudal; subir de "
                      "diametro lo resuelve, y ahi V1 no cumple siempre, sin "
                      "que este criterio intervenga. Por el nivel del "
                      "receptor: el dren o el canal de aguas abajo esta mas "
                      "alto que la clave durante la avenida; ningun diametro "
                      "menor que el tirante del receptor lo resuelve, y lo "
                      "que lo resuelve es la cota de la salida o la rasante. "
                      "El caso del receptor no empieza en la clave: empieza "
                      "donde el tirante del receptor supera el llenado "
                      "admisible (0.75 de la altura con el umbral por "
                      "defecto) y es el quien fija el tirante maximo dentro "
                      "del barril, y la lectura es la misma desde ahi hasta "
                      "el barril lleno, para que no cambie al cruzar la "
                      "clave. "
                      "El numeral no distingue los dos casos. «no_cumple», "
                      "el valor del archivo, es la lectura literal y la "
                      "conservadora: el riesgo de obstruccion que el Manual "
                      "invoca existe igual con el barril ahogado por el "
                      "receptor, porque el material flotante no tiene por "
                      "donde pasar, y por eso el diseño no se acepta mientras "
                      "el tirante del receptor alcance la clave. Su "
                      "consecuencia: el diametro lo decide el tirante del "
                      "receptor, y cuando ese tirante sale del escenario de "
                      "receptor a seccion llena con la seccion adoptada "
                      "(Sec. 1.3, paso 3) lo decide una adopcion. «aviso» "
                      "lee que la prohibicion es sobre el diseño del "
                      "conducto: si con su propio caudal el barril conserva "
                      "el borde libre, el ahogamiento por el receptor se "
                      "declara como aviso, con el tirante del receptor, su "
                      "via y la velocidad a seccion llena, que V2 sigue "
                      "juzgando, y no descarta el diametro. Con el barril "
                      "horizontal no hay tirante normal con que separar los "
                      "dos casos y V1 no cumple bajo las dos lecturas. Es la "
                      "lectura "
                      "que conviene cuando el nivel del receptor esta medido "
                      "y es un hecho del sitio que la obra no puede cambiar; "
                      "con un tirante adoptado, aceptar el ahogamiento es "
                      "aceptar la adopcion. Sensibilidad en esta obra: en la "
                      "corrida sin tirante declarado ni caudal del receptor, "
                      "con «no_cumple» ninguno de los cuatro puntos "
                      "dimensiona y con «aviso» el punto A-02 dimensiona con "
                      "un tubo de 0.90 m de diametro, ahogado por un tirante "
                      "del receptor de 1.196 m",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, RD "
               "20-2011-MTC/14), num. 4.1.1.3.7 b) 'Borde libre', pag. "
               "impresa 79 (PDF 82), citas MC_HHD.4.1.1.3.7b#LLENA "
               "(exigencia: no diseñar para seccion llena) y "
               "MC_HHD.4.1.1.3.7b (recomendacion del 25 %). El numeral no "
               "distingue la seccion llena por el caudal de la seccion "
               "llena por el nivel del receptor: la lectura es adopcion del "
               "proyectista. HDS-5 3a ed., num. 3.1.6, pag. impresa 3.18 "
               "(cita HDS5_3ED.3.1.6#V_SALIDA_TW), para el regimen: con el "
               "TW sobre la clave la seccion de salida es la entera",
        reemplazado_por="El nivel de agua del receptor MEDIDO o calculado "
                        "por quien lo opera (ANA / Junta de Usuarios), con el "
                        "que la cota de la salida se fija por encima de el, "
                        "o se acepta el ahogamiento como condicion del sitio",
        resolucion=Libre(
            que_lo_fija="el proyectista: el numeral prohibe diseñar para "
                        "seccion llena y no dice que hacer cuando la llena "
                        "el nivel del receptor",
            dominio="declaracion de la lectura; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    "TR_evento_extremo": Criterio(
        valor=None,                 # VACIO: bloquea V8 para todo punto
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Periodo de retorno del evento extremo de V8 y el umbral de "
                 "no colapso de la via ante desborde",
        justificacion="Decide el periodo de retorno del evento extremo de V8 "
                      "y el umbral con que se evalua el no colapso de la via, "
                      "y hoy es un vacio declarado. La fuente (Sec. 5 de la "
                      "hoja de ruta, V8) exige verificar el punto a un TR "
                      "mayor que el de diseno y confirmar que la via resiste "
                      "el desborde sin colapsar. Lo que no resuelve: no fija "
                      "ese TR mayor ni un umbral cuantitativo de colapso (p. "
                      "ej. HW sobre la corona del terraplen). Sin el TR no "
                      "hay Q que correr por M3/M4 aparte del Q de diseno, y "
                      "sin el umbral no hay con que comparar el HW "
                      "resultante; por eso se deja vacio y no se rellena",
        fuente="PENDIENTE - Fase 5, V8 de la hoja de ruta: '[N] verificacion, "
               "no diseño', sin numeral que fije el TR ni el umbral",
        reemplazado_por="TR del evento extremo (p.ej. el de la serie FEN de "
                        "la Fase 1-bis) y definicion tecnica de colapso de "
                        "la via, ambos declarados en la memoria",
        resolucion=Libre(
            que_lo_fija="el proyectista: V8 de la hoja de ruta pide la "
                        "verificacion y no fija ni el TR ni el umbral de "
                        "'la via no colapsa aunque desborde'",
            dominio="años > 0",
        ),
    ),
}
