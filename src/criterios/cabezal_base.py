"""
Fichas de criterios adoptados del dominio: cabezal_base.
"""

from typing import Dict
from src.constantes_normativas import (
    BETA_SIMPLIFICADO_AASHTO,
    PHI_CORTE_AASHTO,
    PHI_EVENTO_EXTREMO_AASHTO,
    PHI_FLEXION_AASHTO,
    REGIMEN_CORTANTE_EN_EL_PLANO,
    REGIMEN_CORTANTE_PERPENDICULAR,
)
from src.modelos import DeEnsayo, DeTabla, Derivada, Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_DICT_CON_CAMPOS,
    FORMA_FLOAT,
    FORMA_STR,
    NIVEL_EXPEDIENTE,
    NIVEL_PERFIL,
    _TABLA_RECUBRIMIENTO_AASHTO_MM,
)


CRITERIOS: Dict[str, Criterio] = {


    # ----------------------- FASE 9: CABEZAL Y ALETAS ---------------------
    # Sec. 9.2 nombra las combinaciones y la cadena sismica; Sec. 9.3 da los
    # FS; Sec. 9.4 remite el diseno a AASHTO LRFD Sec. 5. De las tablas
    # numericas de esas tres remisiones, la hoja de ruta no transcribe
    # ninguna; el corpus normativo peruano, en cambio, SI trae las dos de los
    # factores de carga, y desde NOR-PUE-04 estan transcritas donde les
    # corresponde -- `constantes_normativas.TABLA_GAMMA_P_FILAS` y
    # `TABLA_COMBINACIONES_FILAS`, [N] -- y aqui queda solo la ELECCION de
    # fila. Lo que sigue siendo vacio de tabla se declara aqui, cada uno con
    # su razon, en vez de rellenarse con el valor "de siempre".

    "factores_carga_aashto": Criterio(
        valor={
            # LA ELECCION, y nada mas que la eleccion: que FILA de la Tabla
            # 2.4.5.3.1-2 [N] describe a cada estructura de esta obra. Los
            # numeros no estan aqui ni pueden estarlo -- son las claves de
            # `constantes_normativas.TABLA_GAMMA_P_FILAS`, que es donde vive
            # la tabla completa. Ese reparto es el de F_PGA_TABLA / 'F_pga' y
            # REDUCCION_KH_POR_DESPLAZAMIENTO / 'factor_muro_eleccion'.
            #
            # Las tres primeras claves son los valores de `TipoMaterial`, el
            # mismo indexado por material que ya usan 'D_max_catalogo',
            # 'espesor_pared_conducto' y 'cobertura_minima_aashto'.

            # Tubo de concreto reforzado enterrado bajo el terraplen. No es
            # "Porticos rigidos" (1.35/0.90): un portico es un marco con
            # patas, y ESTA clave es la del TUBO.
            #
            # LA RAZON QUE ESTE COMENTARIO DABA YA NO VALE, y por eso se
            # reescribio en C5. Decia: «el catalogo de Sec. 3.2 es circular
            # -- la Familia C, de marco o multicelda, sale sin candidatos».
            # Esa premisa la destruyo esta misma sesion: `materiales_candidatos`
            # devuelve hoy un marco de concreto para la Familia C. Lo que
            # separa las dos filas no era nunca el catalogo, era la ESTRUCTURA:
            # un tubo enterrado y un marco son dos tipos distintos en la Tabla
            # 2.4.5.3.1-2, y ahora las dos claves existen.
            "concreto_reforzado": {"EV": "EV_estructura_rigida_enterrada"},

            # EL MARCO DE LA FAMILIA C. La fila la fija la regla vinculante #8
            # de docs/ruta_familia_c.md §6 -- «Porticos rigidos» (1.35/0.90)
            # y no «Estructura rigida enterrada» --, que no es eleccion de esta
            # sesion sino una decision ya tomada y verificada contra el Manual
            # de Puentes, Tabla 2.4.5.3.1-2, pag. impresa 143.
            #
            # LA CLAVE ES 'cajon' Y NO UN TipoMaterial, y tiene que serlo: un
            # marco de concreto y un tubo de concreto son el MISMO
            # `TipoMaterial`, de modo que indexar por material no puede
            # distinguirlos. Es la misma razon por la que 'cabezal' tampoco es
            # un material.
            #
            # HOY NO TIENE CONSUMIDOR, y hay que decirlo entero porque es un
            # numero que se lee mal en silencio: `M8.factores_carga_flotacion`
            # indexa por `material.tipo.value`, de modo que un marco recibe
            # HOY la fila del TUBO. El minimo de las dos filas es 0.90, o sea
            # que el NUMERO que V7 usa es el mismo y lo que sale mal es la
            # FILA QUE LA MEMORIA IMPRIME -- el precedente NOR-HID-01, valor
            # que acierta por casualidad y cita falsa --. Cablearlo es de C7
            # (punto 2 de su brief), que generaliza M8 a la seccion; C5 deja
            # la clave puesta y el defecto declarado en §15.8 y en el
            # docstring de `M5.v7_flotacion`, que es su consumidor.
            #
            # --- VE-5 (m8) --- Y EL EMPUJE DEL PORTICO, EN REPOSO: las
            # paredes de un marco cerrado no se desplazan lo que el empuje
            # activo pide, y el dueño adopto el de reposo de 3.11.5.2 (censo
            # del 2026-11-20, decision 3), que es la fila «EH: En reposo»
            # (1.35/0.90). La lee `M8.disenar_portico`.
            "cajon": {"EV": "EV_porticos_rigidos", "EH": "EH_en_reposo"},

            # TMC. Es estructura flexible enterrada, y de las tres subfilas
            # flexibles le toca la de "Entre otros" (1.95/0.90): no es
            # alcantarilla cajon metalica, no es de fibra de vidrio, y no es
            # una plancha estructural. AQUI HAY QUE DECLARAR UNA DIVERGENCIA
            # DE LA FUENTE PERUANA: AASHTO 9a ed. restringe esa fila a
            # "Structural Plate Culverts with DEEP Corrugations" y el Manual
            # traduce "plancas estructurales con corrugaciones", sin
            # "profundas". Leido al pie de la letra, el Manual dejaria caer
            # ahi cualquier tubo corrugado y le daria 1.50 en vez de 1.95. Se
            # elige "Entre otros" por dos razones que apuntan al mismo lado:
            # es lo que sostiene la fuente primaria (un tubo corrugado no es
            # una plancha estructural) y es el maximo mas alto de las tres,
            # o sea el extremo conservador cuando EV desestabiliza.
            "tmc": {"EV": "EV_flexibles_entre_otros"},

            # HDPE: la subfila flexible es literal, "Alcantarillas
            # termoplasticas" (1.30/0.90). No hay eleccion que discutir.
            "hdpe": {"EV": "EV_flexibles_alcantarillas_termoplasticas"},

            # El cabezal. M9 lo modela como muro de contencion con zapata, y
            # esa es la fila "Muros y estribos de retencion" (1.35/1.00). Su
            # MINIMO es 1.00, no 0.90 (NOR-PUE-03). Y "EH_activa" porque el
            # proyecto disena con empuje ACTIVO -- Mononobe-Okabe / Coulomb,
            # ver 'inclinacion_muro_beta' y companeros --, no en reposo.
            "cabezal": {"EV": "EV_muros_y_estribos_de_retencion",
                        "EH": "EH_activa"},
        },
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Que fila de la Tabla 2.4.5.3.1-2 (factores gamma_p de "
                 "cargas permanentes) describe a cada estructura de esta "
                 "obra: los tres conductos del catalogo, por material, y el "
                 "cabezal. La TABLA es [N] y vive en constantes_normativas; "
                 "aqui solo esta la eleccion de fila",
        justificacion="Decide que fila de la Tabla 2.4.5.3.1-2 (factores "
                      "gamma_p de cargas permanentes) describe a cada "
                      "estructura de esta obra: los tres conductos por "
                      "material y el cabezal como muro de retencion. La "
                      "fuente (las dos tablas del Manual de Puentes, "
                      "transcritas en "
                      "constantes_normativas.TABLA_GAMMA_P_FILAS y "
                      "TABLA_COMBINACIONES_FILAS con su correspondencia y sus "
                      "divergencias frente a AASHTO LRFD) desglosa gamma_p "
                      "por tipo de estructura, y un par unico de EV no puede "
                      "expresar ese desglose: para una estructura rigida "
                      "enterrada el minimo de EV es 0.90 y para un muro o "
                      "estribo de retencion es 1.00, de modo que cualquier "
                      "par unico da mal uno de los dos consumidores -- V7 lee "
                      "el minimo del conducto, y la estabilidad del cabezal "
                      "leera el del muro. Por eso el valor es un mapa "
                      "estructura -> clave de fila, no un numero. Lo que la "
                      "fuente no resuelve: de que fila cuelga cada estructura "
                      "de esta obra. Eso lo decide el proyectista, sostenido "
                      "en la descripcion literal de cada fila, y es la parte "
                      "[A]; los numeros son [N] y viven en "
                      "constantes_normativas -- el mismo reparto que "
                      "F_PGA_TABLA / 'F_pga' y "
                      "REDUCCION_KH_POR_DESPLAZAMIENTO / "
                      "'factor_muro_eleccion': la tabla es [N] y elegir una "
                      "fila no convierte la eleccion en norma. Sobre la "
                      "direccion de los minimos, dicho con cuidado porque "
                      "invita al error contrario: rebajar lo que estabiliza "
                      "es la direccion conservadora -- es lo que el marco "
                      "LRFD hace a proposito, y la razon por la que V7 minora "
                      "DC y EV --, de modo que el 1.00 del muro frente al "
                      "0.90 del conducto relaja volteo y deslizamiento en "
                      "torno a un 8 %, no los endurece: el desglose es una "
                      "exigencia de conformidad con la fila que corresponde, "
                      "no una correccion de seguridad. AASHTO LRFD lo "
                      "prescribe expresamente en su comentario C3.4.1 al "
                      "aplicar los criterios al deslizamiento de muros -- el "
                      "empuje vertical de tierra tras un muro en voladizo se "
                      "multiplica por su minimo (1.00) y el peso de la "
                      "estructura por el suyo (0.90), porque ambos aumentan "
                      "la tension de contacto y la resistencia al corte en la "
                      "base --, y el mismo comentario da el otro extremo para "
                      "la capacidad portante, donde gobiernan los maximos: "
                      "peso propio 1.25, empuje vertical 1.35, empuje activo "
                      "1.50. Las tres filas de EH estan en "
                      "TABLA_GAMMA_P_FILAS con sus pares completos -- la de "
                      "reposo lleva 1.35 / 0.90, y el N/A pertenece a la fila "
                      "de paredes ancladas, que comparte el maximo 1.35 --, y "
                      "el N/A de la fila que si lo tiene viaja como "
                      "GAMMA_P_NO_APLICA, para que pedirlo sea un error del "
                      "expediente y no un silencio. Alcance hoy: ningun "
                      "modulo de produccion consume los factores del cabezal "
                      "-- la estabilidad de Sec. 9.3 sigue bloqueada por "
                      "'predimensionamiento_cabezal', y E2 y E3 se evaluan "
                      "como FS globales de E.050 sobre demandas sin factorar "
                      "--, de modo que este mapa fija el numero que se "
                      "consumira cuando se desbloqueen; gamma_EQ (carga viva "
                      "de Evento Extremo I) sigue sin valor y sigue "
                      "bloqueando esa combinacion (ver "
                      "`verificacion_pendiente`). La sensibilidad enumera las "
                      "claves de fila admisibles: declarar una estructura "
                      "contra una fila cuya descripcion literal no la cubre "
                      "es exactamente el defecto que este desglose existe "
                      "para impedir",
        fuente="LA TABLA (valores [N], no estan aqui): Manual de Puentes "
               "(MTC) num. 2.4.5.3.1, Tabla 2.4.5.3.1-2 'Factores de carga "
               "para cargas permanentes, gamma_p' y Tabla 2.4.5.3.1-1 "
               "'Combinaciones de Carga y Factores de Carga', las DOS en la "
               "pag. impresa 143 (PDF 144) de normas/'Puentes (Version "
               "Libro).pdf'; transcritas en "
               "constantes_normativas.TABLA_GAMMA_P_FILAS y "
               "TABLA_COMBINACIONES_FILAS, con su correspondencia y sus "
               "divergencias frente a AASHTO LRFD 9a ed. (2020), Tablas "
               "3.4.1-2 (pag. impresa 3-18) y 3.4.1-1 (pag. impresa 3-17). "
               "LA ELECCION (esto, [A]): de que fila cuelga cada estructura "
               "del proyecto, decidido por el proyectista y sostenido en la "
               "descripcion literal de cada fila. "
               "TRES PAGINAS QUE ESTE CAMPO CITABA MAL, verificadas una a una "
               "leyendo el encabezado impreso del PDF y corregidas aqui: la "
               "Tabla 3.4.1-1 NO esta en la pag. 3-14 de AASHTO (esa pagina "
               "es texto corrido sobre gamma_TU, sin tabla) sino en la 3-17; "
               "y las dos tablas del Manual no estan en las pags. 143 y 146 "
               "sino las dos en la 143 -- la 146 es una lamina fotografica "
               "sin numerar, 'PUENTE. CARACHA'. La Tabla 2.4.5.3.1-3, que "
               "este proyecto no usa, esta en la 144. "
               "ERRATA DE LA PROPIA FUENTE, anotada para no citarla mal: el "
               "cuerpo del Manual en la pag. impresa 142 llama a estas tablas "
               "'2.4.5.3-1' y '2.4.5.3-2', sin el '.1', mientras el rotulo "
               "impreso sobre cada una dice '2.4.5.3.1-1' y '2.4.5.3.1-2'. Se "
               "cita la forma del rotulo",
        sensibilidad=("EV_estructura_rigida_enterrada", "EV_porticos_rigidos",
                      "EV_muros_y_estribos_de_retencion",
                      "EV_flexibles_entre_otros",
                      "EV_flexibles_cajon_metalico_plancha_fibra_vidrio",
                      "EV_flexibles_alcantarillas_termoplasticas"),
        reemplazado_por="Nada normativo: la tabla no elige por el proyecto. "
                        "Lo que cerraria la eleccion del TMC es que el MTC "
                        "corrija la traduccion de la fila flexible de 1.50 "
                        "('plancas estructurales con corrugaciones') "
                        "reponiendo el 'profundas' que AASHTO exige; hasta "
                        "entonces la frontera entre esa fila y 'Entre otros' "
                        "la sostiene la fuente primaria y no la peruana",
        verificacion_pendiente="gamma_EQ, el factor de la carga viva en "
                               "Evento Extremo I, SIGUE SIN VALOR y bloquea "
                               "esa combinacion: la Tabla 2.4.5.3.1-1 imprime "
                               "el simbolo, no un numero. Y la atribucion con "
                               "que este campo lo declaraba era falsa: decia "
                               "'a criterio del propietario del proyecto "
                               "(0.50 o 0.00, AASHTO LRFD C3.4.1)', y esa "
                               "frase no existe en la 9a ed. -- 'discretion' "
                               "no aparece ni una vez en el Art. 3.4.1 ni en "
                               "su comentario. Lo que la fuente dice, literal, "
                               "esta en constantes_normativas.GAMMA_EQ_TEXTO: "
                               "el factor 'shall be determined on a "
                               "project-specific basis' (Art. 3.4.1, pag. "
                               "impresa 3-19); el 0.0 es practica de "
                               "ediciones pasadas y el 0.50 una indicacion de "
                               "razonabilidad del comentario C3.4.1, no dos "
                               "opciones tabuladas a elegir. Declarar en la "
                               "memoria el valor adoptado y su fundamento, "
                               "antes de evaluar Evento Extremo I. TRAMPA "
                               "CERCANA: el par '0.0 / 0.50' SI aparece "
                               "tabulado en la pag. impresa 3-16, pero es de "
                               "gamma_TG (gradiente de temperatura), otra "
                               "carga",
        resolucion=DeTabla(
            tablas=("MP.TGAMMA_P", "MP.TCOMB"),
            que_elige="que fila de gamma_p describe a cada estructura de "
                      "esta obra: los tres conductos por material y el "
                      "cabezal como muro de retencion",
        ),
    ),

    "peso_especifico_concreto_kn_m3": Criterio(
        valor=23.56,                # kN/m3, concreto armado (0.150 kcf)
        # NIVEL MEDIDO: PERFIL desde VE-3.11 (H4 de los ensayos de diseño del
        # conducto). V7 suma el peso propio del conducto de concreto
        # (`M8.peso_propio_conducto_kn_m`), V7 corre en la Fase 5 y la
        # corrida `--alcance perfil` lo invoca sin diferir. Hasta VE-3.11 era
        # de expediente: su unico consumidor era el cabezal (Fase 9).
        nivel=NIVEL_PERFIL,
        etiqueta="C",
        forma=FORMA_FLOAT,
        concepto="Peso especifico del concreto armado del cabezal y del "
                 "conducto de concreto (peso propio en V7, desde VE-3.11), "
                 "kN/m3",
        justificacion="Es el peso propio (carga DC) que resiste el volteo y "
                      "el deslizamiento de Sec. 9.3: sin el no hay momento "
                      "estabilizante ni fuerza normal en la base. CERRADO "
                      "por verificacion externa: AASHTO LRFD Tabla 3.5.1-1 "
                      "+ Comentario C3.5.1 dan 0.150 kcf (concreto normal "
                      "armado) = 23.56 kN/m3. El valor cae dentro del rango "
                      "de practica corriente (23.5-24.5 kN/m3) que este "
                      "criterio manejaba antes de tener cita directa, pero "
                      "no se adopta el redondeo regional de 24.0: ese numero "
                      "no tiene fuente propia y 23.56 si la tiene",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tabla "
               "3.5.1-1 + Comentario C3.5.1, pag. 3-21 (0.150 kcf, concreto "
               "normal armado)",
        resolucion=Libre(
            que_lo_fija="el proyectista, adoptando el concreto normal armado "
                        "de la Tabla 3.5.1-1 de AASHTO",
            dominio="kN/m3 > 0",
            tabla_pendiente="AASHTO LRFD 9a ed., Tabla 3.5.1-1 'Unit "
                            "Weights', no transcrita al registro",
        ),
    ),

    # --- T-7a --- DEJA DE SER UN VACIO (INF-4.2): es la tabla de REGLAS con
    # que `M9.predimensionar_cabezal` propone la geometria de cada cabezal de
    # cada punto dimensionado. Hasta T-7a declaraba UNA geometria para todo el
    # corredor -- H, B, D_f y espesores, vacia --, y esa geometria unica era
    # INF-5.1.15. Las dimensiones ya no se declaran aqui sino POR PUNTO, en
    # `--datos-externos` (`cabezal_declarado`), y ganan sobre la regla.
    "predimensionamiento_cabezal": Criterio(
        valor={"recubrimiento_clave_m": 0.30,
               "bordillo_m": 0.15,
               "resguardo_agua_m": 0.0,
               "espesor_pantalla_voladizo_m": 0.30,
               "divisor_espesor_gravedad": 6.0,
               "fraccion_ancho_zapata": 0.70,
               "divisor_peralte_zapata": 10.0,
               "fraccion_punta": 0.33,
               "altura_max_gravedad_m": 2.0,
               "empotramiento_lateral_m": 0.30,
               "altura_final_aleros_m": 0.40,
               "fraccion_longitud_losa": 1.5,
               "espesor_losa_m": 0.30},
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        # VENTANA POR CAMPO, y casi todas son las del encargo de T-7a y del
        # INFORME §4.2 / §4.3, que las dan como rangos de practica: espesor
        # de pantalla en voladizo 0.20-0.30 m; en gravedad H/8-H/6 (divisor
        # 6 a 8); zapata 0.4-0.7·H; peralte H/12-H/10 (divisor 10 a 12);
        # altura final de aleros 0.30-0.50 m; losa 1.0-1.5·D y 0.20-0.30 m.
        # Donde el encargo no da rango (recubrimiento, bordillo, resguardo,
        # punta, altura maxima del ciclopeo, empotramiento) la ventana es la
        # del proyecto y lo dice la justificacion.
        sensibilidad={"recubrimiento_clave_m": (0.15, 0.60),
                      "bordillo_m": (0.0, 0.30),
                      "resguardo_agua_m": (0.0, 0.30),
                      "espesor_pantalla_voladizo_m": (0.20, 0.30),
                      "divisor_espesor_gravedad": (6.0, 8.0),
                      "fraccion_ancho_zapata": (0.40, 0.70),
                      "divisor_peralte_zapata": (10.0, 12.0),
                      "fraccion_punta": (0.25, 0.40),
                      "altura_max_gravedad_m": (1.5, 2.5),
                      "empotramiento_lateral_m": (0.20, 0.50),
                      "altura_final_aleros_m": (0.30, 0.50),
                      "fraccion_longitud_losa": (1.0, 1.5),
                      "espesor_losa_m": (0.20, 0.30)},
        concepto="Reglas de predimensionamiento del cabezal por punto: "
                 "recubrimiento y bordillo sobre la clave exterior, resguardo "
                 "sobre el nivel de agua, espesor de pantalla (voladizo; "
                 "gravedad como H/divisor), zapata (ancho como fraccion de H, "
                 "peralte como H/divisor, punta como fraccion del ancho), "
                 "altura maxima del cabezal de gravedad ciclopeo, empotramiento "
                 "lateral de los aleros, altura final de los aleros y losa de "
                 "entrega (longitud como fraccion de D, espesor)",
        justificacion="Decide la geometria PROPUESTA de cada cabezal de "
                      "cada punto, que la Fase 9 imprime dimension por "
                      "dimension como «propuesta por regla» y que el "
                      "proyectista puede pisar por punto en "
                      "`--datos-externos` (`cabezal_declarado`, «declarada»; "
                      "una dimension que la regla calcula A PARTIR de otra "
                      "declarada se imprime «derivada»). Las fuentes con "
                      "numero fijan lo que fijan y no estan aqui: la "
                      "profundidad minima de desplante de E.050 Art. 26.2 "
                      "(0,80 m, [N→] para un cabezal vial: "
                      "'profundidad_cimentacion_min_cabezal_m'), el desplante "
                      "de la salida bajo la socavacion de AASHTO 12.6.5 "
                      "('margen_zapata_bajo_socavacion_m' [C]), el espesor "
                      "minimo de la zapata de concreto simple de E.060 22.7.4 "
                      "(300 mm, [N], solo el de gravedad), la altura minima "
                      "de la zapata armada sobre su refuerzo de E.060 15.7 "
                      "(300 mm, [N→], mas el recubrimiento de 7.7.1: "
                      "'peralte_min_zapata_armada_m') y el dentellon de la "
                      "Lamina Nº 04 ('dentellon_losa_entrega' [N→]). Lo que "
                      "ninguna fuente de normas/ fija es el resto del "
                      "predimensionamiento: las Laminas 02, 02-A y 03 del "
                      "Manual acotan con letras o con «VARIABLE», E.060 no da "
                      "espesor minimo para un muro de contencion (su "
                      "14.5.3.2, 200 mm, es del metodo empirico de muros de "
                      "carga y de cimentacion) y el PDF de VARIOS que el "
                      "encargo cita (pp. 18 y 42) no esta en normas/: su "
                      "origen no se pudo verificar, tampoco el de «H/8 a H/6» "
                      "como espesor de la pantalla de gravedad (el "
                      "predimensionamiento clasico lo da tambien para la "
                      "zapata), que por eso sigue [A]. Se adoptan las reglas "
                      "de practica del INFORME §4.2-§4.3, en el extremo de "
                      "cada ventana que da MAS material (pantalla 0.30 m, "
                      "H/6, B = 0.7·H, peralte H/10, losa 1.5·D y 0.30 m). "
                      "Eso no es el lado seguro de la estabilidad, y no se "
                      "afirma: con kh = 0.50 y un coeficiente de friccion en "
                      "la base menor que kh, cada kN de muro suma mas fuerza "
                      "sismica que desliza (kh·W) que resistencia (μ·W), y "
                      "mas masa EMPEORA el deslizamiento sismico; que mas "
                      "material ayude depende de φ, que el EMS no ha dado. La "
                      "estabilidad de lo propuesto la verifica T-7b y el "
                      "armado T-7c. La coronacion es la mayor de dos: la "
                      "clave exterior mas el relleno que el muro retiene "
                      "sobre ella (0.30 m, regla del proyecto, no un minimo "
                      "de cobertura de ninguna fuente: la cobertura minima "
                      "del conducto la juzga la Fase 7 por su cuenta) mas un "
                      "bordillo de 0.15 m que sobresale del relleno, y el "
                      "nivel de agua del extremo mas un resguardo; el "
                      "resguardo es 0 porque es la condicion que el INFORME "
                      "§4.2 escribe -- que el agua no desborde el muro -- y "
                      "la ventana permite endurecerla. El talud del "
                      "terraplen muere en el RELLENO retenido (coronacion "
                      "menos bordillo), no en la corona del bordillo: es el "
                      "nivel con que se cierra la longitud entre cabezales. "
                      "El tipo es gravedad en concreto ciclopeo hasta 2.0 m "
                      "de altura total -- base de zapata a corona, desplante "
                      "incluido -- y voladizo armado por encima; con la "
                      "altura interior minima de 0.90 m (4.1.1.3.4 a) la "
                      "menor altura total de la obra suma 0.90 m de altura, "
                      "0.30 m de relleno, 0.15 m de bordillo y 0.80 m de "
                      "desplante: 2.15 m mas la pared del conducto (2.165 m "
                      "en TMC, 2.25 m en concreto), de modo que "
                      "con este umbral TODO cabezal sale voladizo armado y la "
                      "rama de gravedad solo se alcanza moviendo el umbral en "
                      "su ventana o declarando el tipo; el umbral no se "
                      "cambia (ficha T7A-04) y la corrida lo avisa. Cuando "
                      "sale gravedad, E.060 22.10.2.1 limita el ciclopeo a "
                      "muros de contencion de GRAVEDAD y el 22.10.2.2 exige "
                      "verificar flexion y corte en voladizos mas largos que "
                      "medio peralte: lo juzga T-7c. La punta es un tercio "
                      "del ancho de la zapata, y el empotramiento de 0.30 m "
                      "por lado es lo que el muro sobresale del ancho "
                      "exterior del conducto para recibir el arranque de los "
                      "aleros. El terreno al pie del muro, desde el que se "
                      "mide el desplante, el dentellon de la losa y las "
                      "alturas de los aleros, es UNO por extremo: en la "
                      "entrada la solera del conducto, y en la salida la mas "
                      "baja entre la solera y el fondo del cauce receptor: "
                      "con la salida en caida sobre el lecho, el terreno "
                      "delante del muro baja hasta el receptor",
        fuente="Practica de predimensionamiento: INFORME §4.2 y §4.3 y el "
               "encargo de T-7a (PDF de VARIOS pp. 18 y 42, NO verificado: no "
               "esta en normas/). Las dimensiones con fuente numerica estan "
               "en los criterios 'espesor_min_zapata_concreto_simple_m' "
               "(E.060 22.7.4, [N→] desde el cierre de T-7c), "
               "'profundidad_cimentacion_min_cabezal_m', "
               "'peralte_min_zapata_armada_m', "
               "'margen_zapata_bajo_socavacion_m' y 'dentellon_losa_entrega'",
        reemplazado_por="Plano de encofrado del cabezal de cada punto, "
                        "acotado, o la dimension declarada por punto en "
                        "`--datos-externos` (`cabezal_declarado`)",
        verificacion_pendiente="La geometria propuesta es compatible con el "
                               "conducto que remata por construccion; la que "
                               "se DECLARA por punto se verifica (CB1 a CB7 "
                               "de `M9.verificar_compatibilidad_cabezal`). "
                               "La ESTABILIDAD de cualquiera de las dos no "
                               "se verifica aqui: es T-7b",
        resolucion=Libre(
            que_lo_fija="el proyectista, o el plano tipo de cabezal del "
                        "expediente vial",
            dominio="reglas en m o adimensionales, cada una en su ventana",
        ),
    ),

    # --- VE-3.5 (decision del dueño del 2026-11-17: el programa DIMENSIONA
    # el cabezal) --- EL PASO Y EL TOPE DEL ANCHO DE LA ZAPATA, VACIOS. La
    # geometria de la regla de T-7a no pasa la estabilidad LRFD en ningun
    # punto de la validacion integral (ficha T7B-09), y desde VE-3.5 la
    # zapata CRECE por el talon hasta cumplir E1 a E3 de los dos marcos que
    # deciden (`M9.dimensionar_zapata_por_estabilidad`). Cuanto crece en cada
    # intento y hasta donde son valores de proyecto que ninguna fuente fija:
    # la hoja de ruta no los trae; AASHTO 11.6.3 y el Manual de Puentes
    # verifican una geometria, no la dimensionan; y la practica que la regla
    # de T-7a ya cita (B = 0.4 a 0.7·H) no sirve de tope, porque la regla
    # esta en 0.7 y es la que no cumple. Hasta VE-3.9 el vacio se declaraba
    # y detenia el dimensionamiento (la geometria de la regla se seguia
    # verificando).
    #
    # --- VE-3.9 --- VALOR DE ARCHIVO POR DECISION DEL DUEÑO (2026-11-17):
    # paso 0.10 m (modulo de encofrado) y tope 1.5·H_c. Medido con los datos
    # de prueba del juego de T-11 (A-01): la entrada cumple con 1.07·H_c y la
    # salida con 0.84·H_c, de modo que 1.5·H_c deja margen sin llegar a un
    # cimiento que ya pide un dentellon o una zapata declarada. Sigue siendo
    # [A]: ninguna fuente fija los dos numeros, y la VENTANA de abajo es la
    # del dueño, no de una fuente. El mismo paso hace crecer el PERALTE de la
    # zapata por su armado (`M9.dimensionar_peralte_por_armado`), cuyo tope
    # es el fisico (H_c), no un campo de este criterio.
    "dimensionamiento_zapata_cabezal": Criterio(
        valor={"paso_m": 0.10, "fraccion_ancho_max": 1.5},
        # NIVEL: el de su etapa, la Fase 9, que solo corre a expediente.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        # Los dos campos son NUMEROS: `campos_obligatorios` es para campos
        # de texto (EXT-6) y no aplica; los valida el consumidor en segunda
        # linea (`M9._regla_de_dimensionamiento`), como las reglas de
        # 'predimensionamiento_cabezal'.
        forma=FORMA_DICT_CON_CAMPOS,
        # VENTANA POR CAMPO (VE-3.9), propuesta al dueño y no de una fuente:
        # un paso de 0.05 a 0.20 m (de un modulo fino de encofrado a uno
        # grueso) y un tope de 1.0 a 2.0·H_c (por debajo de 1.0 la entrada
        # de A-01 ya no cumple; por encima de 2.0 la zapata deja de ser la
        # solucion racional frente a un dentellon).
        sensibilidad={"paso_m": (0.05, 0.20),
                      "fraccion_ancho_max": (1.0, 2.0)},
        concepto="Dimensionamiento de la zapata del cabezal: el paso con que "
                 "crece el ancho B en cada intento de estabilidad, y el "
                 "peralte en cada intento de armado (m), y el tope del ancho "
                 "como fraccion de la altura total del cabezal H_c (B_max = "
                 "fraccion_ancho_max·H_c)",
        justificacion="Decide cuanto crece la zapata de un cabezal cuya "
                      "geometria de regla no cumple la estabilidad LRFD "
                      "(E1 capacidad portante, E2 excentricidad, E3 "
                      "deslizamiento, estatica y sismica) y hasta donde se "
                      "intenta antes de declarar que con esa familia de "
                      "geometrias no cumple. Crece el TALON (la punta queda "
                      "en la de la regla): suma el peso del relleno sobre la "
                      "zapata y el brazo de las cargas verticales, que es lo "
                      "que la estabilidad de un muro en voladizo pide cuando "
                      "falla el deslizamiento o la capacidad portante. El "
                      "paso fino da la zapata minima de la grilla y cuesta "
                      "corridas; el grueso, al reves. El tope dice donde la "
                      "solucion racional deja de ser una zapata mas ancha y "
                      "pasa a ser un dentellon de corte (y el pasivo de "
                      "AASHTO 11.6.3.5), una zapata declarada o un suelo "
                      "mejorado: eso lo decide el proyectista, no el "
                      "programa. Medido con los datos de PRUEBA del juego de "
                      "T-11 (A-01): la entrada cumple con B = 2.40 m "
                      "(1.07·H_c) y la salida con 3.20 m (0.84·H_c)",
        fuente="Decision del dueño del proyecto (2026-11-17): paso 0.10 m "
               "(modulo de encofrado) y tope 1.5·H_c. Ninguna fuente de "
               "normas/ fija el paso ni el tope: AASHTO LRFD 11.6.3 (E1 a "
               "E3) y el Manual de Puentes 2.4 verifican una geometria; el "
               "predimensionamiento B = 0.4 a 0.7·H de la regla de T-7a "
               "('predimensionamiento_cabezal', [A]) es el punto de partida, "
               "no el tope",
        reemplazado_por="Plano de encofrado del cabezal de cada punto, o el "
                        "ancho declarado en `cabezal_declarado`, que gana y "
                        "no se itera",
        resolucion=Libre(
            que_lo_fija="el proyectista: modulo de encofrado para el paso y "
                        "el limite a partir del cual prefiere un dentellon o "
                        "una zapata declarada para el tope",
            dominio="paso_m > 0 en m; fraccion_ancho_max > 0, adimensional",
        ),
    ),

    "metodo_estabilidad_global": Criterio(
        valor=None,                 # VACIO: bloquea las filas E4 y E5 de Sec. 9.3
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_STR,
        concepto="Metodo de analisis de estabilidad global del muro y del "
                 "talud que lo soporta (equilibrio limite: Bishop "
                 "simplificado, Spencer, Morgenstern-Price...)",
        justificacion="La tabla de Sec. 9.3 exige FS = 1.50 estatico y 1.25 "
                      "sismico para la estabilidad global del muro "
                      "(39.13.6 b) y para la del talud (Art. 30.3), pero un "
                      "FS de estabilidad global no se calcula con una "
                      "formula cerrada: sale de un analisis de superficies "
                      "de falla que exige el perfil estratigrafico completo, "
                      "la geometria del terraplen y un metodo declarado. "
                      "Ninguna de las tres cosas esta en el alcance del CSV "
                      "de Sec. 1.2. El FS existe y esta transcrito; lo que "
                      "falta es con que producir el valor a comparar",
        fuente="PENDIENTE - E.050 Art. 30.3 y num. 39.13.6 b) fijan el "
               "umbral, no el metodo. El analisis es del EMS del expediente",
        reemplazado_por="Analisis de estabilidad de taludes del estudio "
                        "geotecnico, con su metodo y sus superficies criticas",
        resolucion=Libre(
            que_lo_fija="el proyectista: E.050 Art. 30.3 y num. 39.13.6 b) "
                        "fijan el umbral, no el metodo. Es una ELECCION de "
                        "metodo y por eso no es `DeEnsayo`, aunque el "
                        "analisis lo corra el mismo EMS",
            dominio="declaracion del metodo de equilibrio limite",
        ),
    ),

    # ---- El recubrimiento del refuerzo: la CADENA, no un numero -----------
    # Estos cuatro criterios sustituyen al antiguo 'recubrimiento_aashto_mm',
    # que era un solo dict con 75.0 mm en las tres condiciones y la conclusion
    # ya escrita ("AASHTO gobierna en los tres casos por la regla del mayor").
    # Ese numero no se podia defender por tres razones que se acumulaban:
    #
    #   (1) 75 mm no esta en ninguna tabla. La Tabla 5.10.1-1 esta en
    #       PULGADAS y da 3.0 in = 76.2 mm; redondear un MINIMO hacia abajo va
    #       del lado no conservador (MAT-D16).
    #   (2) Los 3.0 in son UNA COLUMNA de tres. La tabla se organiza por
    #       "Reinforcing Material Category" -- A acero sin recubrir, B epoxico
    #       o galvanizado, C acero AASHTO M 334M -- y con acero protegido da
    #       2.0 in = 50.8 mm (NOR-AAS-01). La categoria no se declaraba en
    #       ninguna parte del expediente.
    #   (3) Falta el modificador por relacion agua-cemento, que el Art. 5.10.1
    #       impone sobre la tabla y el criterio ignoraba entero: con
    #       W/CM <= 0.40 el factor es 0.8 (NOR-AAS-05).
    #
    # Y las tres juntas INVIERTEN la conclusion, que es lo que hace que este
    # cluster no se pueda corregir hallazgo por hallazgo: 3.0 in x 0.8 = 61.0
    # mm queda POR DEBAJO de los 70 mm que E.060 pide para concreto contra el
    # suelo, de modo que la regla del mayor la gana E.060 y no AASHTO. Con
    # acero protegido, 2.0 in x 0.8 = 40.6 mm, y E.060 gana en dos de las tres
    # condiciones y pierde por medio milimetro en la tercera. Corregir solo el
    # 75 -> 76.2 habria dejado en pie una conclusion falsa con un numero mas
    # exacto: es el conflicto #3 de docs/hoja_de_ruta_correcciones_v12.md.
    #
    # De ahi el reparto: la TABLA es dato (transcrita entera, aqui abajo y en
    # constantes_normativas), la CATEGORIA y la EXPOSICION son declaraciones
    # que el expediente tiene que hacer, y el VALOR se calcula en
    # `M9.recubrimiento_de_diseno`. Mientras falte una de las dos
    # declaraciones, el calculo se detiene. No hay numero por defecto.

    "categoria_refuerzo_aashto": Criterio(
        valor=None,                 # VACIO: bloquea la regla del mayor de 9.4
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_STR,
        concepto="Categoria de material de refuerzo de la Tabla 5.10.1-1 de "
                 "AASHTO LRFD ('A' acero sin recubrir, 'B' epoxico o "
                 "galvanizado, 'C' acero AASHTO M 334M), que decide que "
                 "columna de la tabla de recubrimientos aplica a este cabezal",
        justificacion="Decide que columna de categoria de material de "
                      "refuerzo de la tabla de recubrimientos aplica a este "
                      "cabezal, y hoy es un vacio declarado: es la condicion "
                      "de aplicacion de la tabla, no un refinamiento. La "
                      "fuente (AASHTO LRFD, Tabla 5.10.1-1, transcrita como "
                      "AASHTO_LRFD_9.T5.10.1-1 en el registro con su nota al "
                      "pie) no tiene un recubrimiento por situacion sino "
                      "tres, uno por categoria de acero, y su nota al pie "
                      "define las tres categorias: A, acero sin recubrir "
                      "(AASHTO M 31M/M 31); B, con recubrimiento epoxico o "
                      "galvanizado (ASTM A775/A775M); C, materiales AASHTO M "
                      "334M/M 334. Leer la tabla sin declarar columna es "
                      "elegir la A por omision. Lo que la fuente no resuelve: "
                      "la categoria la fija la especificacion del acero del "
                      "expediente, que es una decision de proyecto con "
                      "consecuencia de costo y de suministro, no una lectura "
                      "de norma; en un corredor salino con freatico somero el "
                      "acero galvanizado o epoxico es una opcion natural, y "
                      "justamente por eso no se puede suponer la A -- "
                      "suponerla es suponer el caso que mas recubrimiento "
                      "pide, que parece conservador y no lo es, porque con "
                      "acero protegido el proyectista podria creer que le "
                      "sobra recubrimiento cuando lo que cambio fue la "
                      "columna. Donde queda el corpus peruano: el Manual de "
                      "Puentes transcribe esta misma tabla (num. 2.9.1.5.5.3, "
                      "cita MP.T2.9.1.5.5.3-1 del registro) pero solo la "
                      "columna A -- su propio titulo la acota a los aceros no "
                      "protegidos -- y trata la proteccion epoxica o "
                      "galvanizada en el numeral aparte 2.9.1.5.5.4, donde "
                      "solo autoriza usar la tabla con acero protegido en "
                      "exposicion interior. De modo que con categoria A el "
                      "valor es [N] peruano, y con B o C el corpus peruano no "
                      "tabula nada para exposicion exterior y el hueco lo "
                      "cubre AASHTO LRFD por la Via 1 de Sec. 0.2, como [C]: "
                      "la etiqueta de la fuente del recubrimiento adoptado "
                      "depende de este mismo criterio. Se deja vacio para que "
                      "lo fije la especificacion del acero del expediente. "
                      "Sensibilidad, con el factor 0.8 por a/c <= 0.40 ya "
                      "aplicado y para la fila costera: A da 76.2 x 0.8 = "
                      "61.0 mm, y E.060 gobierna el caso 'contra_suelo' con "
                      "sus 70 mm; B o C dan 50.8 x 0.8 = 40.6 mm, y E.060 "
                      "gobierna tambien 'suelo_intemperie_ge_3_4' (50 mm). La "
                      "eleccion mueve el recubrimiento adoptado y mueve quien "
                      "lo impone, que es lo que la memoria tiene que declarar",
        fuente="PENDIENTE - AASHTO LRFD 9a ed., Tabla 5.10.1-1 y su nota al "
               "pie, pag. impresa 5-169 (PDF 528); Manual de Puentes "
               "num. 2.9.1.5.5.3 y 2.9.1.5.5.4, pags. impresas 377-378. La "
               "tabla y sus categorias estan verificadas; lo que falta es "
               "CUAL de las tres se especifica en esta obra",
        sensibilidad=("A: acero sin recubrir (AASHTO M 31M/M 31)",
                      "B: epoxico o galvanizado (ASTM A775/A775M)",
                      "C: acero AASHTO M 334M/M 334",
                      "LECTURA ALTERNATIVA, declarada porque bajar de columna "
                      "con B o C NO es una lectura neutra: el num. "
                      "2.9.1.5.5.4 del Manual autoriza usar la tabla con "
                      "acero protegido 'Para exposicion interior', y de ahi "
                      "caben dos lecturas. La adoptada: fuera de la "
                      "exposicion interior el corpus peruano calla y el hueco "
                      "lo cubren las columnas B y C de AASHTO, como [C]. La "
                      "contraria: si el Manual solo autoriza la reduccion en "
                      "interior, en exposicion exterior sigue rigiendo su "
                      "unica columna -- la de aceros no protegidos -- y el "
                      "acero protegido no baja de 3.0 in. En la fila costera "
                      "con el factor 0.8 la diferencia es 40.6 mm frente a "
                      "61.0 mm, y en 'suelo_intemperie_le_5_8' decide ademas "
                      "quien gobierna: E.060 con 40 mm en la lectura "
                      "adoptada, AASHTO en la contraria"),
        reemplazado_por="Especificacion del acero de refuerzo del expediente "
                        "(norma de producto del acero que se compra), o la "
                        "decision expresa del proyectista de proteger o no el "
                        "refuerzo en ambiente salino",
        resolucion=DeTabla(
            tablas=("AASHTO_LRFD_9.T5.10.1-1",),
            que_elige="la COLUMNA de categoria de material de refuerzo: A "
                      "(acero sin recubrir), B (epoxico o galvanizado) o C "
                      "(AASHTO M 334M)",
        ),
    ),

    "factor_recubrimiento_banda_intermedia_ac": Criterio(
        valor=1.0,
        # NIVEL DECLARADO Y NO MEDIDO, y conviene decir por que: NINGUNA de
        # las dos corridas de `tests/test_nivel_medido.py` llega a invocarlo
        # --- la cadena de la Fase 9 se detiene antes, en un criterio
        # pendiente ---, de modo que no hay medicion que citar. Lo sostiene el
        # censo: `variables_entrada` no le encuentra mas consumidor que
        # `M9_cabezal`, y `--alcance perfil` no ejecuta ese modulo. El test lo
        # comprueba por esa via, que es la unica que queda.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_FLOAT,
        concepto="Factor de modificacion del recubrimiento para la banda "
                 "intermedia de relacion agua-cemento, 0.40 < a/c < 0.50, que "
                 "el Manual de Puentes no imprime",
        justificacion="Decide el factor de modificacion del recubrimiento en "
                      "la banda de relacion agua-cemento que el corpus "
                      "peruano no imprime, 0.40 < a/c < 0.50. La fuente "
                      "peruana (Manual de Puentes, num. 2.9.1.5.5.3) escribe "
                      "dos factores -- 0.8 para a/c <= 0.40 y 1.2 para a/c >= "
                      "0.50 -- y deja la banda de en medio sin factor; AASHTO "
                      "LRFD Art. 5.10.1, de donde el Manual toma la tabla, si "
                      "la cubre con 1.0 (el pasaje esta citado en `fuente`; "
                      "la laguna, declarada en "
                      "constantes_normativas.RECUBRIMIENTO_MP_FACTOR_AC_LAGUNA). "
                      "Lo que el corpus peruano no resuelve es exactamente "
                      "esa banda, y no es un caso teorico: con sulfatos "
                      "severos y sin cloruros la a/c maxima resulta 0.45, "
                      "dentro de ella. Se adopta el 1.0 de AASHTO por la Via "
                      "1 de Sec. 0.2, que es exactamente lo que una etiqueta "
                      "[C] declara. Por que el numero vive aqui y no en el "
                      "modulo: multiplicar por uno es neutro en aritmetica y "
                      "no en normativa -- aqui significa que en esta banda el "
                      "recubrimiento no se modifica, que es una afirmacion "
                      "que el corpus peruano no hace y que hay que sostener "
                      "con una fuente. La unica alternativa defendible esta "
                      "en el campo `sensibilidad`: extender el 1.2 de la "
                      "banda alta daria mas recubrimiento pero contradiria la "
                      "fuente de la que sale la propia tabla",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed. (2020), "
               "Art. 5.10.1 'Concrete Cover', pag. impresa 5-167 (PDF 526): "
               "'For W/CM ratio between 0.40 and 0.50 ... 1.0'. El Manual de "
               "Puentes num. 2.9.1.5.5.3 (pag. impresa 377) imprime solo los "
               "otros dos factores. Ver RECUBRIMIENTO_MP_FACTOR_AC_LAGUNA",
        sensibilidad=("El unico valor alternativo defendible seria extender "
                      "el 1.2 de la banda alta a la intermedia, por no dejar "
                      "sin modificar un concreto que el corpus peruano no "
                      "clasifica. Daria mas recubrimiento (76.2 -> 91.4 mm en "
                      "la fila costera con categoria A) y seria mas "
                      "conservador, pero contradice la fuente de la que sale "
                      "la propia tabla, que si escribe el 1.0",),
        resolucion=Libre(
            que_lo_fija="el proyectista, cubriendo la banda 0.40 < a/c < "
                        "0.50 que el Art. 5.10.1 no imprime",
            dominio="factor adimensional > 0",
        ),
    ),

    "exposicion_quimica_ems": Criterio(
        valor=None,                 # VACIO: bloquea el factor por a/c de 9.4
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="S",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Agresividad quimica del suelo y del agua freatica en el "
                 "corredor, y condiciones de exposicion del concreto, en las "
                 "magnitudes con que E.060 clasifica: sulfato soluble en el "
                 "suelo (% en peso) y en el agua (ppm) para la Tabla 4.4, y "
                 "cual de las TRES filas de la Tabla 4.2 aplica",
        justificacion="Registra el dato del que cuelga el recubrimiento, por "
                      "una cadena que conviene dejar escrita: la agresividad "
                      "quimica fija la relacion a/c maxima (E.060, Tablas 4.2 "
                      "y 4.4, transcritas como E060.T4.2 y E060.T4.4 en el "
                      "registro y combinadas por su nota al pie), la a/c "
                      "maxima fija el factor de modificacion del "
                      "recubrimiento (AASHTO Art. 5.10.1 y Manual de Puentes "
                      "num. 2.9.1.5.5.3: 0.8 / 1.0 / 1.2), y el factor "
                      "multiplica al valor tabulado. Sin este dato no hay "
                      "factor, y sin factor el recubrimiento de AASHTO seria "
                      "el valor bruto de la tabla, un 20 % por encima del que "
                      "la norma exige. Lo que ninguna fuente resuelve sin "
                      "ensayo: la fila de cloruros de la Tabla 4.2 no se "
                      "dispara con suelos salinos en general, sino con los "
                      "origenes concretos que su texto enumera -- "
                      "descongelantes, sal, agua salobre, agua de mar o "
                      "salpicaduras de ese origen; el texto exacto vive en "
                      "E060.T4.2 --, de modo que afirmar que el corredor "
                      "tiene suelos salinos y freatico somero no basta: quien "
                      "sostenga que la fila aplica tiene que poder mostrar el "
                      "analisis, y mientras no este, el calculo se detiene "
                      "aqui y no aguas abajo con un numero que nadie puede "
                      "reproducir. Es [S] y no [A]: no hay nada que elegir -- "
                      "es una medicion de laboratorio sobre muestras de este "
                      "corredor, y cambia al mover la obra, no al cambiar de "
                      "proyectista. Vive aqui, y no en datos_sitio.py, porque "
                      "sigue pendiente del ensayo, que es la condicion que "
                      "este archivo admite para un [S]; la estructura exigida "
                      "del dato y sus reglas de lectura estan en el campo "
                      "`trazabilidad`",
        fuente="PENDIENTE - Analisis quimico del EMS (contenido de sulfatos y "
               "cloruros en suelo y en agua freatica). Las tablas contra las "
               "que se clasifica ya estan transcritas: E.060 Tabla 4.2 "
               "(pag. impresa 37), Tabla 4.4 (pag. impresa 38) y la nota al "
               "pie comun a las dos",
        trazabilidad="Ensayo quimico de suelos y de agua del EMS del "
                     "expediente, sobre muestras del corredor, MAS la "
                     "condicion de exposicion del elemento. La estructura del "
                     "dato es un diccionario con estas claves, TODAS "
                     "obligatorias: 'so4_suelo_pct', sulfato soluble en agua "
                     "presente en el suelo, en porcentaje en peso; "
                     "'so4_agua_ppm', sulfato en el agua, en ppm; y "
                     "'tabla_4_2', a su vez un diccionario con las TRES filas "
                     "de esa tabla como si/no -- 'baja_permeabilidad', "
                     "'congelamiento_deshielo' y 'cloruros'. "
                     "POR QUE LAS TRES FILAS Y NO SOLO LA DE CLORUROS: la "
                     "nota al pie comun a las Tablas 4.2 y 4.4 manda aplicar "
                     "'la MENOR relacion maxima agua-material cementante "
                     "APLICABLE', y aplicable no se puede evaluar sobre un "
                     "conjunto que el dato deja a medias. Con solo la fila de "
                     "cloruros declarada, un concreto que ademas deba ser de "
                     "baja permeabilidad se evaluaba contra un candidato "
                     "menos que el que la norma manda mirar. "
                     "UNA CLAVE AUSENTE NO ES UN 'NO': es DatoInvalidoError. "
                     "La version anterior leia la de cloruros con `.get()`, y "
                     "un EMS que no la trajera se leia como 'no hay "
                     "cloruros', que es rellenar un vacio en silencio. "
                     "El dato vale para todo el corredor si el EMS lo "
                     "muestrea por tramos homogeneos; si la agresividad varia "
                     "de un punto a otro, deja de ser un dato de corredor y "
                     "tiene que pasar a ser columna del CSV. Las dos escalas "
                     "de sulfato son alternativas -- el suelo O el agua --: "
                     "las dos claves tienen que estar, pero una de ellas "
                     "puede venir en None; con las dos medidas, gobierna la "
                     "mas exigente",
        reemplazado_por="El analisis quimico del EMS. Mientras no exista, "
                        "ningun recubrimiento de 9.4 se puede calcular",
        resolucion=DeEnsayo(
            ensayo="analisis quimico del EMS: sulfato soluble en suelo y en "
                   "agua freatica, y cloruros",
            trazabilidad_exigida="calicata, profundidad, laboratorio, fecha "
                                 "e informe de ensayo; las tablas contra las "
                                 "que se clasifica (E060.T4.2 y E060.T4.4) "
                                 "ya estan en el registro",
        ),
    ),

    "situacion_recubrimiento_aashto": Criterio(
        valor={"contra_suelo": "vaciado_contra_suelo",
               "suelo_intemperie_ge_3_4": "costera",
               "suelo_intemperie_le_5_8": "costera"},
        # NIVEL MEDIDO, no opinado: lo invoca la corrida `--alcance expediente`
        # de `tests/test_nivel_medido.py` y NO la de `--alcance perfil`, que
        # difiere la Fase 9 entera. Ese test contrasta las dos corridas en LAS
        # DOS DIRECCIONES, de modo que este campo no puede quedar
        # desincronizado del codigo: si algun dia la corrida de perfil lo
        # invocara sin diferirlo, la suite se pone roja aqui.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Fila de la tabla de recubrimientos de AASHTO / Manual de "
                 "Puentes que se contrasta con cada condicion de E.060 "
                 "Art. 7.7.1, para poder evaluar la regla del mayor",
        justificacion="Decide que fila de la tabla de recubrimientos de "
                      "AASHTO / Manual de Puentes se contrasta con cada "
                      "condicion de E.060 Art. 7.7.1, para poder evaluar la "
                      "regla del mayor entre las dos normas. Las fuentes "
                      "(E060.7.7.1 y AASHTO_LRFD_9.T5.10.1-1 en el registro) "
                      "no se indexan igual: E.060 organiza el recubrimiento "
                      "por diametro de barra (3/4 de pulgada o mas gruesa / "
                      "5/8 o mas delgada) y por contacto con el suelo; AASHTO "
                      "y el Manual lo organizan por severidad de exposicion, "
                      "sin mirar el diametro. Lo que ninguna de las dos "
                      "resuelve: que fila de la segunda se pone enfrente de "
                      "cada condicion de la primera. Se adopta: la cara del "
                      "cabezal que se vacia contra el terreno se contrasta "
                      "con la fila del vaciado contra el suelo "
                      "('vaciado_contra_suelo' en "
                      "'tabla_recubrimiento_aashto_mm'), que es literalmente "
                      "la misma situacion fisica; las dos condiciones de "
                      "intemperie de E.060 se contrastan con la fila de "
                      "ubicaciones costeras ('costera'), porque La Union "
                      "(Piura) esta en el corredor costero y esa es la "
                      "exposicion de las caras vistas. La eleccion es "
                      "defendible ademas porque no mueve el numero: las dos "
                      "filas elegidas tienen valores identicos en las tres "
                      "categorias de acero (3.0 / 2.0 / 2.0 in). Se declara "
                      "igual, porque en una obra no costera la fila 'costera' "
                      "deja de valer y la sustituye la fila exterior no "
                      "superior ('exterior_no_superior', 2.0 in en la columna "
                      "A), que si cambia el resultado; ese caso, y el de "
                      "exposicion directa a agua salada, estan en el campo "
                      "`sensibilidad`",
        fuente="AASHTO LRFD 9a ed., Tabla 5.10.1-1, pag. impresa 5-169 "
               "(PDF 528); Manual de Puentes, Tabla 2.9.1.5.5.3-1, pag. "
               "impresa 378 (PDF 379). Las filas existen y estan transcritas "
               "enteras; lo que se elige es el emparejamiento con E.060",
        sensibilidad=("costera y vaciado_contra_suelo: 3.0/2.0/2.0 in, "
                      "identicas",
                      "agua_salada, si el cabezal quedara con exposicion "
                      "directa a agua salada: 4.0/2.5/2.5 in",
                      "exterior_no_superior, en una obra no costera: "
                      "2.0/2.0/1.5 in"),
        resolucion=DeTabla(
            tablas=("AASHTO_LRFD_9.T5.10.1-1",),
            que_elige="que FILA de la tabla se contrasta con cada condicion "
                      "de E.060 Art. 7.7.1, para poder evaluar la regla del "
                      "mayor entre las dos normas",
        ),
    ),

    "tabla_recubrimiento_aashto_mm": Criterio(
        valor=_TABLA_RECUBRIMIENTO_AASHTO_MM,
        # NIVEL MEDIDO, no opinado: lo invoca la corrida `--alcance expediente`
        # de `tests/test_nivel_medido.py` y NO la de `--alcance perfil`, que
        # difiere la Fase 9 entera. Ese test contrasta las dos corridas en LAS
        # DOS DIRECCIONES, de modo que este campo no puede quedar
        # desincronizado del codigo: si algun dia la corrida de perfil lo
        # invocara sin diferirlo, la suite se pone roja aqui.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Tabla 5.10.1-1 de AASHTO LRFD (recubrimiento minimo del "
                 "acero principal de refuerzo), completa: las 21 situaciones "
                 "por las tres categorias de material de refuerzo, "
                 "convertidas a mm",
        justificacion="Registra la Tabla 5.10.1-1 de AASHTO LRFD entera "
                      "aunque el calculo use dos filas. La fuente es la tabla "
                      "AASHTO_LRFD_9.T5.10.1-1 del registro, con su titulo y "
                      "su nota al pie de categorias verificados contra el "
                      "PDF; este dict no es una copia a mano -- lo arma "
                      "`_tabla_recubrimiento_aashto_mm()` leyendo "
                      "`normativa.registro`, con la conversion exacta de "
                      "pulgadas a mm (1 in = 25.4 mm). Un solo numero ya "
                      "digerido no se puede comprobar contra el PDF sin "
                      "rehacer la lectura, no deja ver que hay tres columnas "
                      "y no permite contestar que pasaria con otra categoria "
                      "de acero; con la tabla completa las tres preguntas se "
                      "contestan leyendo. Es [C] y no [N]: AASHTO LRFD no es "
                      "norma peruana, y esta transcripcion cubre lo que el "
                      "corpus peruano no tabula -- las columnas B y C, de "
                      "acero protegido. La columna A si la tiene el Manual de "
                      "Puentes, y por eso vive ademas en "
                      "constantes_normativas.RECUBRIMIENTO_MP_MM con etiqueta "
                      "[N]: no son dos transcripciones rivales, son la misma "
                      "tabla en los dos corpus, y "
                      "`M9.recubrimiento_de_diseno` declara de cual sale el "
                      "valor que aplica segun la categoria elegida. Lo que no "
                      "esta en este dict y hay que aplicarle encima, en este "
                      "orden: el modificador por relacion agua-cemento del "
                      "Art. 5.10.1 (0.8 / 1.0 / 1.2) y el piso absoluto de "
                      "1.0 in = 25.4 mm sobre las barras principales, que "
                      "impide que el modificador de 0.8 baje el recubrimiento "
                      "por debajo de la pulgada. Los dos los aplica "
                      "`M9.recubrimiento_de_diseno`, no este criterio: aqui "
                      "vive la tabla, no la regla",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed. (2020), "
               "Tabla 5.10.1-1 'Minimum Cover for Main Reinforcing Steel "
               "(in.)', pag. impresa 5-169 (PDF 528), con su nota al pie de "
               "categorias; Art. 5.10.1 'Concrete Cover', pag. impresa 5-167 "
               "(PDF 526), para el modificador por W/CM; pag. impresa 5-168 "
               "(PDF 527) para el piso de 1.0 in sobre barras principales",
        resolucion=Derivada(
            de=("AASHTO_LRFD_9.T5.10.1-1",),
            regla="transcripcion de la tabla del registro con las columnas "
                  "en mm; la arma `_tabla_recubrimiento_aashto_mm()` leyendo "
                  "`normativa.registro`, no una copia a mano. La conversion "
                  "in -> mm es exacta (1 in = 25.4 mm)",
        ),
    ),

    "cortante_alto_muro_e060_art_11_10_10_2": Criterio(
        # --- T-7c --- DEJA DE ESTAR VACIO. Lo que faltaba no era el numero
        # -- el 0,0025 esta literal en el articulo desde EXT-6 -- sino la
        # demanda de cortante con que decidir si el muro esta bajo ese
        # regimen. Desde T-7c el armado la tiene (`M9.armado_del_cabezal`)
        # y sabe en que plano actua: ver el criterio del regimen, abajo.
        valor=0.0025,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        # `float` (auditoria adversarial de EXT-5): lo que M9 lee de aqui es
        # la CUANTIA que rige bajo el regimen de 11.10.10, con `float()`.
        forma=FORMA_FLOAT,
        concepto="Cuantia horizontal minima del muro del cabezal bajo el "
                 "regimen de cortante en el plano de E.060 11.10.10 (Art. "
                 "11.10.10.2), que escalona la de 14.3.1 de 0,0020 a 0,0025",
        justificacion="Es el piso horizontal del regimen de cortante en el "
                      "plano del muro. La fuente (E.060 11.10.10.2, pag. "
                      "104; cita E060.11.10.10.2) dice en una sola frase que "
                      "la cuantia de refuerzo horizontal para cortante no "
                      "debe ser menor que 0,0025, con espaciamiento no mayor "
                      "que tres veces el espesor ni que 400 mm; el regimen "
                      "lo abren 11.10.7 y 11.10.8 (pags. 103 y 104; cita "
                      "E060.11.10.7#UMBRAL) segun V_u en el plano sea menor "
                      "o mayor que 0,085·raiz(f'c)·Acw, y por debajo de ese "
                      "umbral rigen 0,002 y 0,0015, los mismos de 14.3.1. "
                      "Es [N→] y no [N]: E.060 es la norma de concreto de "
                      "las edificaciones y se aplica al cabezal vial por "
                      "analogia, como contraste y como minimo constructivo "
                      "('regla_minimos_constructivos_cabezal'). Cuando se "
                      "aplica lo decide el regimen declarado "
                      "('regimen_cortante_muro_e060_art_11_10_2'): con el "
                      "cortante perpendicular al plano, que es el del empuje "
                      "de tierras y el de archivo, este piso no rige; con el "
                      "cortante en el plano declarado, rige -- el programa "
                      "no modela ninguna carga en el plano del muro con que "
                      "evaluar el umbral de 11.10.7, de modo que quien lo "
                      "declara afirma estar por encima de el, y el armado "
                      "lo avisa",
        fuente="E.060 Art. 11.10.10.2, pag. impresa 104 (cita "
               "E060.11.10.10.2); umbral del regimen: 11.10.7 y 11.10.8, "
               "pags. 103 y 104 (cita E060.11.10.7#UMBRAL). Por analogia",
        reemplazado_por="El diseño por cortante en el plano del muro, si el "
                        "proyectista modela una carga en ese plano",
        resolucion=Libre(
            que_lo_fija="E.060 11.10.10.2, aplicado por analogia",
            dominio="cuantia adimensional > 0",
        ),
    ),

    # ---- EXT-M-05 / R95-031: el regimen del cortante y el piso VERTICAL ---
    # Dos preguntas que la ficha anterior no hacia y que deciden si el 0.0025
    # rige. La PRIMERA es de aplicabilidad: E.060 11.10.2 restringe 11.10.3 a
    # 11.10.10 al cortante EN EL PLANO del muro, y 11.10.1 manda el cortante
    # perpendicular al plano a las losas de 11.12. Un cabezal en voladizo
    # bajo empuje de tierras trabaja perpendicular a su plano; si ese es el
    # cortante que dispara la pregunta, ni el 11.10.10.2 ni el .3 rigen y el
    # minimo es el del 14.3.1. La SEGUNDA es el piso vertical: bajo el regimen
    # de 11.10.10 la cuantia vertical tambien tiene piso 0.0025 (ec. 11-32),
    # y M9 devolvia 0.0015 afirmando lo contrario. Ninguna de las dos se
    # contesta aqui: se detienen.

    "regimen_cortante_muro_e060_art_11_10_2": Criterio(
        # --- T-7c --- DEJA DE ESTAR VACIO: el diseño estructural que la
        # ficha pedia «tener delante» existe, y su cortante es el del empuje
        # de tierras sobre la pantalla, PERPENDICULAR al plano del muro.
        valor=REGIMEN_CORTANTE_PERPENDICULAR,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        concepto="En que plano actua la fuerza cortante del muro del "
                 "cabezal para E.060: perpendicular a el (11.10.1, losas de "
                 "11.12) o en su plano (11.10.2, regimen de 11.10.3 a "
                 "11.10.10)",
        justificacion="Decide si los dos pisos de cuantia de 11.10.10.2 y "
                      "11.10.10.3 rigen o no. Lo que la fuente dice: el "
                      "11.10.2 aplica 11.10.3 a 11.10.10 a las fuerzas "
                      "cortantes horizontales en el plano del muro, y el "
                      "11.10.1 manda las perpendiculares al plano a las "
                      "disposiciones para losas de 11.12 (pag. 103; citas "
                      "E060.11.10.1 y E060.11.10.2). Lo que la fuente no "
                      "resuelve es en cual esta este muro, y desde T-7c lo "
                      "contesta el modelo de cargas: el unico cortante que "
                      "el ensamble de T-7b entrega para la pantalla es el "
                      "del empuje de tierras, de la sobrecarga y del agua, "
                      "que actua perpendicular al plano del muro, y el "
                      "programa no modela ninguna carga en el plano (el "
                      "sismo a lo largo del muro, o el empuje de los aleros "
                      "sobre la pantalla). Por eso el valor de archivo es "
                      "«perpendicular»: el cortante se diseña como el de "
                      "una losa y el minimo es el de 14.3.1 en las dos "
                      "direcciones. Es una eleccion y no un hecho -- un "
                      "cabezal corto con aleros que le transmiten carga en "
                      "su plano caeria en 11.10.2 --, y «en el plano» queda "
                      "en la ventana: declararlo aplica los pisos de "
                      "11.10.10 (0,0025 horizontal y la ec. 11-32 vertical) "
                      "con aviso, porque no hay V_u en el plano con que "
                      "evaluar el umbral de 11.10.7",
        fuente="E.060 11.10.1 y 11.10.2, pag. impresa 103 (citas "
               "E060.11.10.1 y E060.11.10.2): la norma reparte los dos "
               "planos; cual es el de este muro lo dice el modelo de "
               "cargas del proyecto",
        reemplazado_por="Un analisis del cabezal que incluya cargas en el "
                        "plano del muro",
        sensibilidad=(REGIMEN_CORTANTE_EN_EL_PLANO,
                      REGIMEN_CORTANTE_PERPENDICULAR),
        resolucion=Libre(
            que_lo_fija="el proyectista: el modelo de cargas del programa "
                        "solo tiene cortante perpendicular al plano",
            dominio="una de las dos lecturas del plano del cortante",
        ),
    ),

    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3": Criterio(
        # --- T-7c --- DEJA DE ESTAR VACIO: guarda el PISO de la ec. (11-32),
        # y la ecuacion entera la evalua `M9.cuantia_vertical_ec_11_32` con
        # la altura y la longitud del cabezal, que desde T-7a existen.
        valor=0.0025,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        forma=FORMA_FLOAT,
        concepto="Piso de la cuantia vertical minima del muro del cabezal "
                 "bajo el regimen de cortante en el plano de E.060 11.10.10: "
                 "el 0,0025 de la ec. (11-32) del 11.10.10.3",
        justificacion="Es el piso vertical del regimen de cortante en el "
                      "plano. La fuente (E.060 11.10.10.3, pag. 104; cita "
                      "E060.11.10.10.3, leida por imagen) da la ec. (11-32): "
                      "rho_v >= 0,0025 + 0,5·(2,5 - hm/lm)·(rho_h - 0,0025) "
                      ">= 0,0025, con techo en la rho_h que el 11.10.10.1 "
                      "requiera, hm la altura total del muro y lm su "
                      "longitud total. Este criterio "
                      "guarda el piso; la ecuacion la evalua "
                      "`M9.cuantia_vertical_ec_11_32` con hm y lm del "
                      "cabezal del punto (T-7a le dio longitud a la "
                      "geometria) y con la rho_h del muro. El programa no "
                      "modela cortante en el plano, de modo que la rho_h "
                      "requerida por 11.10.10.1 no existe y se toma el piso "
                      "horizontal de 11.10.10.2: con rho_h = 0,0025 la "
                      "ecuacion da 0,0025 para cualquier esbeltez, y el "
                      "armado lo dice. Es [N→]: E.060 se aplica al cabezal "
                      "vial por analogia. Solo rige si el regimen declarado "
                      "es «en el plano» "
                      "('regimen_cortante_muro_e060_art_11_10_2')",
        fuente="E.060 11.10.10.3, ec. (11-32), pag. impresa 104 (cita "
               "E060.11.10.10.3, con la ecuacion en su nota). Por analogia",
        reemplazado_por="La rho_h requerida por 11.10.10.1 de un diseño "
                        "por cortante en el plano del muro, con la que la "
                        "ec. (11-32) da mas que su piso",
        resolucion=Libre(
            que_lo_fija="E.060 11.10.10.3, aplicado por analogia",
            dominio="cuantia adimensional, no menor que 0.0025",
        ),
    ),

    "procedimiento_flexion_corte_aashto_sec5": Criterio(
        valor={
            # --- T-7c --- LO QUE SE EJECUTA. Los tres factores de
            # resistencia y el factor beta del procedimiento SIMPLIFICADO de
            # cortante son los de `constantes_normativas` (bloque T-7c,
            # transcritos de 5.5.4.2, 1.3.2.1 y 5.7.3.4.1): este criterio
            # declara QUE subconjunto de la Seccion 5 arma el cabezal, y
            # `M9.diseno_flexion_corte` lo lee de aqui.
            "phi_flexion": PHI_FLEXION_AASHTO,
            "phi_corte": PHI_CORTE_AASHTO,
            "phi_evento_extremo": PHI_EVENTO_EXTREMO_AASHTO,
            "modelo_corte": "simplificado_5_7_3_4_1",
            "beta_simplificado": BETA_SIMPLIFICADO_AASHTO,
            "theta_simplificado_grados": 45.0,
            # --- T-7c --- LO QUE NO SE EJECUTA. El procedimiento GENERAL de
            # 5.7.3.4.2 (MCFT, beta y theta en funcion de epsilon_s) quedo
            # transcrito en C07 en las unidades de la fuente (kip, ksi,
            # pulgada: la 9a ed. no publica edicion SI, C5.1). Se conserva
            # como REFERENCIA, bajo una sola clave y rotulado: ninguna
            # funcion lo lee ni lo evalua, y no se puede alimentar con MPa y
            # metros. Donde el simplificado no esta permitido el armado se
            # detiene con «metodo no evaluable», no cae aqui.
            "referencia_no_ejecutable_5_7_3_4_2": {
                "nota": "Procedimiento general de AASHTO LRFD 5.7.3.4.2, en "
                        "kip - ksi - pulgada. REFERENCIA NO EJECUTABLE: el "
                        "programa arma con el simplificado de 5.7.3.4.1 y "
                        "no evalua estas expresiones",
                "beta_con_refuerzo_transversal_minimo":
                    "4.8 / (1 + 750*epsilon_s)   [Ec. 5.7.3.4.2-1]",
                "beta_sin_refuerzo_transversal_minimo":
                    "(4.8 / (1 + 750*epsilon_s)) * (51 / (39 + sxe_in))"
                    "   [Ec. 5.7.3.4.2-2]",
                "sxe_in": "sx * 1.38 / (ag + 0.63), acotado a 12.0 in <= "
                          "sxe <= 80.0 in   [Ec. 5.7.3.4.2-7]",
                "theta_grados": "29 + 3500*epsilon_s   [Ec. 5.7.3.4.2-3]",
                "limites_epsilon_s": "-0.40e-3 <= epsilon_s <= 6.0e-3",
            },
        },
        # NIVEL MEDIDO desde T-7c: lo invoca la corrida de expediente que
        # llega al armado del cabezal (`M9.armado_del_cabezal`); la de
        # perfil difiere la Fase 9 entera.
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Procedimiento de diseño por flexion y corte de AASHTO LRFD "
                 "Seccion 5 con que se arma el cabezal: factores de "
                 "resistencia y modelo de cortante (el simplificado de "
                 "5.7.3.4.1)",
        justificacion="Decide que subconjunto de la Seccion 5 de AASHTO LRFD "
                      "rige el diseño por flexion y corte del cabezal. La "
                      "hoja de ruta (Sec. 9.4) remite el diseño a esa "
                      "seccion por la Via 1 de la Sec. 0.2, y mezclarla con "
                      "las expresiones de E.060 romperia la consistencia "
                      "carga-resistencia: no se combinan demandas mayoradas "
                      "por AASHTO con resistencias reducidas por E.060. Se "
                      "adopta, verificado contra el PDF: factores de "
                      "resistencia de 5.5.4.2 (0.90 en flexion de secciones "
                      "controladas por traccion y 0.90 en cortante; citas "
                      "AASHTO_LRFD_9.5.5.4.2#FLEXION y #CORTE) y 1.0 en el "
                      "evento extremo (1.3.2.1; cita "
                      "AASHTO_LRFD_9.1.3.2.1#EXTREMO); flexion por 5.6.3.2 "
                      "con el bloque rectangular de 5.6.2.2; y cortante por "
                      "5.7.3.3 con el procedimiento SIMPLIFICADO de "
                      "5.7.3.4.1 (beta = 2.0, theta = 45 grados; cita "
                      "AASHTO_LRFD_9.5.7.3.4.1#SIMPLIFICADO), que la fuente "
                      "PERMITE solo en zapatas con la distancia del cortante "
                      "nulo a la cara del muro menor que 3·d_v y en "
                      "secciones de menos de 16.0 in de peralte (o con el "
                      "refuerzo transversal minimo, que el cabezal no "
                      "lleva). `M9.diseno_flexion_corte` comprueba esas "
                      "condiciones seccion por seccion y, donde no se "
                      "cumplen, se detiene con «metodo no evaluable»: el "
                      "procedimiento general de 5.7.3.4.2 no se implementa "
                      "(decision del encargo de T-7c) y queda transcrito "
                      "como referencia no ejecutable. Las cuantias minimas "
                      "de E.060 son un piso sobre el resultado, por la "
                      "regla de 'regla_minimos_constructivos_cabezal'",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed.: Art. "
               "5.5.4.2 (pags. impresas 5-29 y 5-30, PDF 388 y 389) y "
               "1.3.2.1 (pag. 1-3, PDF 18) para los phi; 5.6.2.2 y 5.6.3.2 "
               "(pags. 5-36 y 5-40, PDF 395 y 399) para la flexion; 5.7.2.8 "
               "(pag. 5-65, PDF 424) para d_v; 5.7.3.3 (pag. 5-67, PDF 426) "
               "para V_c; 5.7.3.4.1 (pag. 5-70, PDF 429) para el "
               "simplificado y sus condiciones; 5.7.3.4.2 (pags. 5-70 a "
               "5-72) para el general, que no se ejecuta; C5.1 (pag. 5-1) "
               "para el sistema de unidades. PAGINA CORREGIDA en T-7c: la "
               "fuente declaraba 5-32 para el 5.5.4.2, que esta en la 5-29 "
               "y la 5-30",
        resolucion=Libre(
            que_lo_fija="el proyectista, al declarar que subconjunto de la "
                        "Seccion 5 de AASHTO arma el cabezal",
            dominio="declaracion del procedimiento; los factores son los de "
                    "la fuente",
        ),
    ),

    # =======================================================================
    # --- T-7a --- (cadena T) · el cabezal por punto: dos criterios con fuente
    # =======================================================================
    "margen_zapata_bajo_socavacion_m": Criterio(
        valor=0.0,                  # decision 14 del dueño (VE-3.15)
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="C",
        forma=FORMA_FLOAT,
        # 0 es la lectura de AASHTO 10.6.1.2 («bear below the maximum
        # anticipated depth of scour») y la de HEC-14 5.1.3 («extend to a
        # depth equal to the maximum depth of scour»); 0.6096 m (2.0 ft) es
        # la de 12.6.5 para las estructuras enterradas, el techo.
        sensibilidad=(0.0, 0.6096),
        concepto="Distancia minima de la base de la zapata del cabezal de "
                 "salida, y de la base del dentellon de su losa, por debajo "
                 "del fondo de la hoya de socavacion",
        justificacion="Decide cuanto por debajo de la socavacion se "
                      "desplanta el cabezal de salida. El proyecto adopta "
                      "margen cero, decision 14 del dueño con la "
                      "verificacion independiente de VE-3: HEC-14 lleva el "
                      "cabezal a la profundidad de la socavacion maxima "
                      "(cita HEC14.5.1.3#CABEZAL, recomendacion) y la regla "
                      "general de las zapatas lo pone bajo esa profundidad "
                      "sin margen (cita AASHTO_LRFD_9.10.6.1.2#DESPLANTE). "
                      "La hoya es la de la salida SIN proteger, y el "
                      "delantal de enrocado de la Fase 6 se diseña ademas: "
                      "por eso el margen extra no se suma. No se adopta una "
                      "hoya protegida, menos profunda, porque ninguna fuente "
                      "del repositorio da su profundidad y habria que "
                      "inventarla. Lo que juega en contra, y queda como el "
                      "otro extremo de la ventana: AASHTO LRFD 12.6.5 "
                      "(Seccion 12, estructuras enterradas; cita "
                      "AASHTO_LRFD_9.12.6.5#ZAPATAS) exige que las zapatas "
                      "de la estructura queden no menos de 2.0 ft bajo la "
                      "socavacion maxima prevista, y si la zapata de un "
                      "cabezal es una de ellas no lo dice. El mismo margen "
                      "se aplica a la base del dentellon de la losa de "
                      "salida. Es [C] y no [N] porque las dos fuentes son "
                      "tecnicas reconocidas (hoja de ruta §0.1). La "
                      "profundidad la entrega la Fase 6 (T-8): la "
                      "declarada, o la hoya de HEC-14 Cap. 5; sin ninguna de "
                      "las dos, el desplante de salida queda solo con el "
                      "minimo de E.050 y la corrida lo avisa",
        fuente="HEC-14 5.1.3, pag. impresa 5-2 (PDF 55; cita "
               "HEC14.5.1.3#CABEZAL) y AASHTO LRFD 9a ed., 10.6.1.2 'Bearing "
               "Depth', pag. impresa 10-52 (PDF 1341; cita "
               "AASHTO_LRFD_9.10.6.1.2#DESPLANTE). Contraste: 12.6.5 'Scour', "
               "pag. impresa 12-20 (PDF 1658; cita "
               "AASHTO_LRFD_9.12.6.5#ZAPATAS)",
        reemplazado_por="Un estudio de socavacion del cauce que fije el "
                        "desplante",
        resolucion=Libre(
            que_lo_fija="el proyecto: HEC-14 5.1.3 y AASHTO 10.6.1.2 dan "
                        "el cero y AASHTO 12.6.5 los 2.0 ft; cual aplica a "
                        "la zapata de un cabezal no lo dice ninguna",
            dominio="m, entre 0 y 0.6096",
        ),
    ),

    "dentellon_losa_entrega": Criterio(
        valor={"profundidad_min_m": 0.80, "ancho_m": 0.40},
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Dentellon (uña) en el borde libre de la losa de entrega de "
                 "cada cabezal: profundidad minima, medida desde el TERRENO "
                 "al borde de la losa (el pie del muro de ese extremo) hasta "
                 "la base del dentellon, y ancho",
        justificacion="Decide la profundidad minima y el ancho del dentellon "
                      "de la losa de entrega. La fuente (Lamina Nº 04 del "
                      "Manual, pag. impresa 210) acota el dentellon de un "
                      "ALIVIADERO a la salida de alcantarillas: «0.80 min.» "
                      "de profundidad --medida desde la superficie del "
                      "terreno natural al borde del dentellon, que alli es la "
                      "cara inferior del paquete losa + relleno granular, "
                      "hasta su base; no desde la cara superior de la losa "
                      "(correcciones de T-7a, H3)-- y «0.40m» de ancho; es "
                      "la unica lamina "
                      "del Manual que acota un dentellon (la 02 y la 02-A lo "
                      "rotulan «UÑA» y lo acotan con letras; la 03 no acota "
                      "nada). Lo que no resuelve: el dentellon de la losa de "
                      "un cabezal, que es otra estructura. Se aplica por "
                      "ANALOGIA, y por eso es [N→] y no [A]: un valor "
                      "justificado con la cota de una lamina normativa no "
                      "puede ser adopcion libre (regla de coherencia de la "
                      "§0.1). El terreno desde el que se mide es el mismo "
                      "del desplante del cabezal de ese extremo "
                      "(`ExtremoDelConducto.cota_pie`): en la salida, la mas "
                      "baja entre la solera y el fondo del cauce receptor. Y "
                      "en la salida, si la Fase 6 entrega la socavacion, la "
                      "base del dentellon baja ademas bajo el fondo de la "
                      "hoya con el margen de "
                      "'margen_zapata_bajo_socavacion_m' (AASHTO 12.6.5 pide "
                      "una pantalla «extending below» la socavacion maxima "
                      "prevista sin cuantificar cuanto; cita "
                      "AASHTO_LRFD_9.12.6.5#DENTELLON y su `Interpretacion` "
                      "en la de las zapatas)",
        fuente="Manual de Hidrologia, Lamina Nº 04, pag. impresa 210 (PDF "
               "213; cita MC_HHD.LAMINA_04#DENTELLON), por analogia; AASHTO "
               "LRFD 12.6.5, pag. impresa 12-20 (PDF 1658; cita "
               "AASHTO_LRFD_9.12.6.5#DENTELLON) para la salida",
        reemplazado_por="El plano de la losa de entrega de cada cabezal",
        resolucion=Libre(
            que_lo_fija="la Lamina Nº 04, aplicada por analogia",
            dominio="m, profundidad y ancho positivos",
        ),
    ),

    # --- T-7a, correcciones de la auditoria (H8 y dudoso 4) --- DOS MINIMOS
    # DE NORMAS DE EDIFICACION APLICADOS POR ANALOGIA AL CABEZAL VIAL. Hasta
    # las correcciones el primero era [N] en constantes_normativas
    # (`PROFUNDIDAD_CIMENTACION_MIN_M`); el ambito de E.050 son las
    # edificaciones del RNE, y para un cabezal vial es [N→] (dictamen del
    # verificador normativo del marco del cabezal).
    "profundidad_cimentacion_min_cabezal_m": Criterio(
        valor=0.80,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        forma=FORMA_FLOAT,
        concepto="Profundidad minima de desplante del cabezal (de entrada y "
                 "de salida) bajo el terreno al pie del muro, m",
        justificacion="Decide la profundidad minima de la base de la zapata "
                      "del cabezal bajo el terreno al pie del muro (CB4 y el "
                      "piso del desplante propuesto). La fuente (E.050 Art. "
                      "26.2, pag. 38; cita E050.26.2#PROFUNDIDAD) fija 0.80 m "
                      "como minimo para cualquier tipo de cimentacion y el "
                      "26.1 la mide desde la superficie del "
                      "terreno. Lo que no resuelve: E.050 es una norma de "
                      "EDIFICACIONES (Art. 1 y 3, pag. 7) y no nombra las "
                      "obras de drenaje vial. Se aplica por ANALOGIA, y por "
                      "eso es [N→] y no [N]: lo que la hace cercana es que la "
                      "misma norma manda que el muro de contencion cumpla su "
                      "Capitulo IV (39.13.7, pag. 73), donde esta el Art. "
                      "26, y el cabezal se predimensiona como un muro de "
                      "contencion. La excepcion de roca del mismo 26.2 (el "
                      "PR puede bajarla) no se supone: no hay dato de roca "
                      "por punto. La tabla de la §0.1 de la hoja de ruta "
                      "rotula E.050 como [N] sin esta salvedad: es un defecto "
                      "de la hoja, declarado en ella",
        fuente="E.050 (RM 406-2018-VIVIENDA), Art. 26.2, pag. 38 (cita "
               "E050.26.2#PROFUNDIDAD, con su `Interpretacion`); ambito, "
               "Art. 1 y 3, pag. 7; remision del muro de contencion, 39.13.7, "
               "pag. 73. Por analogia",
        reemplazado_por="La profundidad de cimentacion que el EMS del punto "
                        "recomiende para el cabezal",
        resolucion=Libre(
            que_lo_fija="E.050 Art. 26.2, aplicado por analogia",
            dominio="m, positivo",
        ),
    ),

    "peralte_min_zapata_armada_m": Criterio(
        valor=0.30,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="N->",
        forma=FORMA_FLOAT,
        concepto="Altura minima de la zapata del cabezal de voladizo armado "
                 "medida sobre el refuerzo inferior, m (el espesor minimo de "
                 "la zapata le suma el recubrimiento contra el suelo)",
        justificacion="Decide el piso del espesor propuesto de la zapata del "
                      "cabezal de voladizo armado, que la regla H/10 de "
                      "'predimensionamiento_cabezal' dejaba en 0.225 m en la "
                      "entrada de A-01. La fuente (E.060 15.7, pag. 138; "
                      "cita E060.15.7#PERALTE) fija 300 mm como minimo de la "
                      "altura de una zapata apoyada sobre el suelo, medida "
                      "sobre su refuerzo inferior. Lo "
                      "que no resuelve: E.060 es una norma de edificaciones y "
                      "la Via 1 de la §0.2 de la hoja de ruta la saca del "
                      "diseño estructural armado (rige AASHTO LRFD Seccion "
                      "5). Se aplica por ANALOGIA como minimo del "
                      "PREDIMENSIONAMIENTO, y por eso es [N→]: el espesor "
                      "minimo de la zapata es esta altura mas el "
                      "recubrimiento del refuerzo inferior contra el suelo de "
                      "E.060 7.7.1 a) (70 mm, `RECUBRIMIENTO['contra_suelo']`"
                      ", [N] por la excepcion de durabilidad de la §0.2). El "
                      "peralte de diseño -- con el recubrimiento mayor entre "
                      "AASHTO y E.060 y el diametro de la barra -- es de "
                      "T-7c",
        fuente="E.060, num. 15.7, pag. 138 (cita E060.15.7#PERALTE), por "
               "analogia; recubrimiento: E.060 7.7.1 a), pag. 54",
        reemplazado_por="El peralte de la zapata que resulte del diseño a "
                        "flexion y corte de T-7c",
        resolucion=Libre(
            que_lo_fija="E.060 15.7, aplicado por analogia",
            dominio="m, positivo",
        ),
    ),

    # =======================================================================
    # --- verificacion de T-7 --- (cadena T) · El modificador de carga de
    # AASHTO 1.3.2.1 en el cabezal: eta = eta_D·eta_R·eta_I. eta_I es el del
    # cruce ('eta_importancia_operativa_conducto'); estos dos son los del
    # cabezal, y ninguno adopta un numero que la fuente no escriba.
    # Nivel: los invoca la Fase 9 (`M9.modificador_de_carga`), que solo corre
    # a expediente; la corrida de referencia no la alcanza y los mide la de
    # los datos de prueba de `tests/test_t7_verificacion.py`.
    # =======================================================================

    "eta_ductilidad_cabezal": Criterio(
        valor=1.00,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        sensibilidad=(0.95, 1.05),
        concepto="Modificador de las cargas por ductilidad, eta_D, en las "
                 "combinaciones de Resistencia I del cabezal (AASHTO LRFD "
                 "1.3.3): entra al producto eta = eta_D·eta_R·eta_I de la "
                 "Ec. 1.3.2.1-1, en la estabilidad y en el armado",
        justificacion="Decide cuanto se mayoran las cargas del cabezal por la "
                      "ductilidad de sus componentes. La fuente lo gradua "
                      "para el estado limite de resistencia: 1.05 o mas para "
                      "componentes y conexiones no ductiles, 1.00 para los "
                      "diseños y detalles convencionales que cumplen la "
                      "norma, y 0.95 o mas cuando se especifican medidas "
                      "adicionales de ductilidad; en los demas estados "
                      "limite vale 1.00. Se adopta 1.00: el cabezal de "
                      "voladizo se arma con la Seccion 5 de la misma norma "
                      "--seccion controlada por traccion, refuerzo minimo "
                      "que evita la falla fragil al agrietarse-- y no lleva "
                      "medidas adicionales. Lo que no resuelve: el cabezal "
                      "de gravedad en concreto ciclopeo no es ductil, pero "
                      "se verifica con E.060 por analogia y no con estas "
                      "combinaciones; si el Propietario clasifica el cabezal "
                      "armado como no ductil, el valor sube a 1.05",
        fuente="AASHTO LRFD 9a ed., Art. 1.3.3 «Ductility», pag. impresa 1-5 "
               "(PDF 20; cita AASHTO_LRFD_9.1.3.3: «1.00 for conventional "
               "designs and details complying with these Specifications»), "
               "y Art. 1.3.2.1, pag. impresa 1-3 (cita "
               "AASHTO_LRFD_9.1.3.2.1#ETA)",
        reemplazado_por="La clasificacion de ductilidad que el proyectista "
                        "estructural del expediente declare para el cabezal",
        resolucion=Libre(
            que_lo_fija="el proyectista, por el detallado del cabezal",
            dominio="0.95 a 1.05 (AASHTO LRFD 1.3.3)",
        ),
    ),

    "eta_redundancia_cabezal": Criterio(
        valor=1.00,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        sensibilidad=(0.95, 1.05),
        concepto="Modificador de las cargas por redundancia, eta_R, en las "
                 "combinaciones de Resistencia I del cabezal (AASHTO LRFD "
                 "1.3.4): entra al producto eta = eta_D·eta_R·eta_I de la "
                 "Ec. 1.3.2.1-1, en la estabilidad y en el armado",
        justificacion="Decide cuanto se mayoran las cargas del cabezal por su "
                      "redundancia. La fuente lo gradua para el estado limite "
                      "de resistencia: 1.05 o mas para miembros no "
                      "redundantes, 1.00 para niveles convencionales de "
                      "redundancia y para los elementos de cimentacion cuyo "
                      "factor de resistencia ya la considera, y 0.95 o mas "
                      "para niveles excepcionales; en los demas estados "
                      "limite vale 1.00. Se adopta 1.00, el valor "
                      "convencional: la estabilidad externa del cabezal se "
                      "juzga con los factores de resistencia de cimentacion, "
                      "que es el caso que la fuente nombra, y el muro es "
                      "continuo a lo largo de su longitud y esta ligado a "
                      "los aleros y al barril. Lo que juega en contra, y por "
                      "eso 1.05 esta en la ventana: la pantalla trabaja como "
                      "voladizo, con un solo camino de carga en su arranque, "
                      "y la fuente deja al Propietario clasificar un miembro "
                      "asi como no redundante. El 1.00 del conducto no sirve "
                      "de precedente: sale de la regla de las estructuras "
                      "enterradas, que no alcanza al cabezal",
        fuente="AASHTO LRFD 9a ed., Art. 1.3.4 «Redundancy», pags. impresas "
               "1-6 y 1-7 (PDF 21 y 22; cita AASHTO_LRFD_9.1.3.4), y Art. "
               "1.3.2.1, pag. impresa 1-3 (cita AASHTO_LRFD_9.1.3.2.1#ETA)",
        reemplazado_por="La clasificacion de redundancia que el Propietario "
                        "declare para el cabezal",
        resolucion=Libre(
            que_lo_fija="el Propietario, por la redundancia del cabezal",
            dominio="0.95 a 1.05 (AASHTO LRFD 1.3.4)",
        ),
    ),
}
