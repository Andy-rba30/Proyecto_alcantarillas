"""
Fichas de criterios adoptados del dominio: hidrologia.
"""

from typing import Dict
from src.modelos import DeEnsayo, DeTabla, Derivada, Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_DICT_CON_CAMPOS,
    FORMA_FLOAT,
    NIVEL_PERFIL,
    _COEFICIENTES_VIALES_WSDOT,
)


CRITERIOS: Dict[str, Criterio] = {


    # ----------------------- HIDROLOGIA -----------------------------------

    "homogeneidad_serie_fen": Criterio(
        # VACIO, Y DESDE T-1 CON CONSUMIDOR REAL: `MH_hidrologia`.
        #
        # Hasta T-0 este renglon decia «bloquea el Q de diseno de TODOS los
        # puntos», y no era lo que el programa hacia: ningun modulo leia el
        # criterio (INF-5.1.1). T-0 corrigio la frase; T-1 corrige el hecho.
        # Hoy pasa esto, y son dos conductas distintas a proposito:
        #
        #   * el caudal lo CALCULA el programa (--cuencas y --estacion, con
        #     `Q_m3s` vacio): `MH_hidrologia.precipitacion_de_diseno` invoca
        #     este criterio y, sin valor, el calculo hidrologico del punto se
        #     detiene con `CriterioPendienteError`. No hay tratamiento por
        #     defecto;
        #   * el caudal entra DECLARADO por la columna `Q_m3s`: no se detiene
        #     nada --ese caudal es responsabilidad del estudio hidrologico que
        #     lo entrego-- y la memoria imprime SIEMPRE un aviso: este
        #     criterio rige solo el caudal que el programa calcula, y del
        #     declarado el programa no sabe que se hizo con los años FEN. No
        #     se lee el criterio en esa rama: atribuir al estudio externo un
        #     tratamiento declarado para otros puntos seria inventarle una
        #     procedencia (auditor adversarial de T-1).
        #
        # EL HECHO Y LA DECISION VAN SEPARADOS. Que años de El Niño contiene
        # la serie es un hecho, y lo declara el CSV de la estacion en su
        # columna `fen`, año por año; este criterio es SOLO la decision de
        # que se hace con ellos. Por eso sigue vacio en el archivo: se decide
        # con la serie delante, y la serie es una entrada del proyecto
        # (docs/contrato_entradas.md).
        valor=None,
        nivel=NIVEL_PERFIL,         # lo consume la Fase 1-bis, que produce el
                                    # caudal con que se dimensiona a perfil
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # EL CONJUNTO CERRADO, que es la ventana entera (T-1). Hasta T-1 eran
        # dos frases --la serie contiene esos años o no los contiene--, que
        # describian un hecho y no una eleccion: el hecho paso al CSV de la
        # estacion y aqui quedan los tres tratamientos.
        #   serie_completa    el ajuste se hace con todos los años, FEN
        #                     incluidos, que es lo que el num. 3.4 manda
        #                     incluir.
        #   serie_sin_fen     el ajuste se hace sin los años marcados FEN.
        #                     Se puede declarar; cuando da MENOS lluvia que
        #                     la serie completa incumple la regla de la hoja
        #                     de ruta (adoptar el mas conservador) y el
        #                     calculo hidrologico del punto SE DETIENE, con
        #                     las dos lluvias en el mensaje. Si da igual o
        #                     mas, pasa y el paso 1b.3b lo imprime. Decision
        #                     del dueño de la hoja de ruta (ficha T1-09).
        #   dos_poblaciones   analisis de poblacion mixta. Se puede declarar
        #                     y el calculo se detiene con «metodo no
        #                     evaluable»: ni el Manual ni ninguna fuente de
        #                     normas/ da el procedimiento.
        # Con cualquiera de los dos primeros la memoria imprime la
        # precipitacion de diseño de las dos series, lado a lado.
        sensibilidad=("serie_completa", "serie_sin_fen", "dos_poblaciones"),
        concepto="Tratamiento de los anios del fenomeno El Nino en la serie "
                 "de precipitacion maxima en 24 horas de la estacion, al "
                 "ajustar la distribucion de la que sale la lluvia de diseno",
        justificacion="Decide con que anios de la serie se ajusta la "
                      "distribucion de probabilidad de la que sale la "
                      "precipitacion de diseno. La fuente (num. 3.4 del "
                      "Manual de Hidrologia, cita MC_HHD.3.4#FEN) manda dos "
                      "cosas en la misma oracion: que la serie incluya los "
                      "anios del fenomeno El Nino, y que esos anios se "
                      "evaluen para no sobredimensionar las obras. Lo que no "
                      "dice es como se evaluan, y la hoja de ruta (Fase "
                      "1-bis) lo deja como decision a declarar: la serie de "
                      "Piura es de poblacion mixta, porque los anios de El "
                      "Nino extraordinario no pertenecen a la misma "
                      "poblacion estadistica que los anios neutros. La hoja "
                      "de ruta fija ademas la regla: reportar el ajuste con "
                      "esos anios y sin ellos, y adoptar el mas conservador. "
                      "Se ofrecen tres tratamientos. Con la serie completa "
                      "las distribuciones de cola corta suelen fallar la "
                      "prueba de bondad, y la que la pasa puede dejar la "
                      "lluvia de diseno por debajo de los anios del fenomeno "
                      "ya registrados: el paso del ajuste lo contrasta y lo "
                      "avisa. Sin los anios del fenomeno el ajuste mejora y "
                      "la lluvia de diseno baja, que es el lado no "
                      "conservador: se puede declarar, y el programa lo "
                      "juzga contra la regla de la hoja de ruta; cuando da "
                      "menos que la serie completa el calculo del punto se "
                      "detiene, y cuando da igual o mas, pasa. "
                      "El analisis de dos poblaciones es el que describe el "
                      "fenomeno, y no se evalua porque ninguna fuente del "
                      "expediente entrega su procedimiento. No se adopta un "
                      "valor de archivo: la eleccion depende de cuantos "
                      "anios del fenomeno trae la serie y de que tan lejos "
                      "quedan del resto, y eso solo se ve con la serie "
                      "delante. Sensibilidad: la memoria imprime la "
                      "precipitacion de diseno con la serie completa y sin "
                      "los anios del fenomeno, de modo que la diferencia "
                      "entre los dos tratamientos queda a la vista en cada "
                      "punto",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. 3.4 "
               "'Evaluación de la Información Hidrológica', pag. impresa 22 "
               "(PDF 25): cita MC_HHD.3.4#FEN, caracter EXIGENCIA sobre "
               "incluir y evaluar los anios del fenomeno El Nino, sin "
               "procedimiento. Hoja de ruta, Fase 1-bis. Requiere la serie "
               "de la estacion con su columna `fen` (--estacion)",
        reemplazado_por="Analisis de homogeneidad sobre la serie SENAMHI "
                        "completa, firmado por el estudio hidrologico",
        verificacion_pendiente="El tratamiento 'dos_poblaciones' no tiene "
                               "procedimiento en ninguna fuente de normas/: "
                               "declararlo detiene el calculo hidrologico "
                               "con «metodo no evaluable». Y cuando el "
                               "caudal entra por la columna 'Q_m3s' este "
                               "criterio no detiene nada: quien reciba un "
                               "CSV con el caudal ya calculado tiene que "
                               "exigir, aparte, el analisis de homogeneidad "
                               "que lo respalda (la memoria lo avisa)",
        resolucion=Libre(
            que_lo_fija="el proyectista, con la serie de la estacion "
                        "delante: el num. 3.4 del Manual manda incluir y "
                        "evaluar los años del fenomeno El Niño y no dice "
                        "como",
            dominio="declaracion del tratamiento; el conjunto cerrado de "
                    "valores admisibles viaja en `sensibilidad`",
        ),
    ),

    "riesgo_admisible_propietario": Criterio(
        valor=None,                 # OPCIONAL: sin valor rigen los maximos
                                    # recomendados de la Tabla N 02
        # NIVEL MEDIDO, y lo mide la TERCERA corrida de
        # `tests/test_nivel_medido.py`, que existe por este caso: `opcional=True`
        # se lee con `valor_si_declarado()`, que NO registra el uso mientras el
        # criterio siga vacio, de modo que las dos corridas normales no lo pueden
        # ver. Declarado en caliente con el valor que ya rige por defecto, la
        # corrida `--alcance perfil` SI lo invoca. Medirlo asi no mueve ningun
        # resultado: la declaracion repite lo que el consumidor ya aplicaba.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Riesgo admisible de falla R y vida util n que el Propietario "
                 "de la obra adopta, si son distintos de los maximos "
                 "recomendados de la Tabla N 02",
        justificacion="Decide que R y que n adopta el Propietario para una "
                      "fila ya elegida de la Tabla N 02, cuando difieren de "
                      "los maximos recomendados. Es opcional y no un vacio: "
                      "sin declarar, el calculo no se detiene y M1 aplica las "
                      "dos filas por defecto (quebrada importante R = 0.30 / "
                      "n = 25; quebrada menor y descarga de cunetas R = 0.35 "
                      "/ n = 15). La fuente (Tabla N 02, num. 3.6, transcrita "
                      "con sus dos notas en "
                      "constantes_normativas.TABLA_02_FILAS) recomienda esos "
                      "valores como maximos y su nota al pie asigna al "
                      "Propietario la definicion del riesgo admisible de "
                      "falla y de la vida util. Lo que la fuente no resuelve "
                      "es el par de esta obra: adoptar los maximos "
                      "recomendados es una decision del proyecto, no una "
                      "lectura del numeral, y hace falta una via declarada "
                      "por la que el Propietario ejerza la suya. Se adopta la "
                      "regla de que este criterio solo puede endurecer lo que "
                      "la tabla concede: M1 rechaza un R declarado por encima "
                      "del maximo recomendado de su fila, porque aqui el "
                      "extremo recomendado es el menos conservador -- mas "
                      "riesgo admisible da menos periodo de retorno y menos "
                      "caudal de diseno, al reves que en V1 y V2. "
                      "Sensibilidad: un Propietario que adopte R = 0.20 con n "
                      "= 25 pasa de TR = 71 a TR = 113 anios (+59 %), y con "
                      "el sube el Q de diseno de todos los puntos de Familia "
                      "A. No decide la eleccion de fila -- que cauce cae en "
                      "quebrada importante y cual en quebrada menor --, que "
                      "es otro eje y vive en "
                      "'umbral_area_quebrada_importante_ha', declarado en "
                      "100 ha con ventana: aqui se declara, para una fila ya "
                      "elegida, que R y que n adopta el Propietario",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC, "
               "RD 20-2011-MTC/14), Tabla N 02 'VALORES MAXIMOS RECOMENDADOS "
               "DE RIESGO ADMISIBLE DE OBRAS DE DRENAJE', num. 3.6, "
               "pag. impresa 25, y su nota al pie. La tabla completa -- seis "
               "filas, con las dos notas -- esta transcrita en "
               "constantes_normativas.TABLA_02_FILAS; las dos filas que el "
               "calculo consume salen de ella por "
               "constantes_normativas.RIESGO_ADMISIBLE, que es el valor por "
               "defecto que este criterio refina",
        reemplazado_por="Declaracion escrita del Propietario de la obra sobre "
                        "el riesgo admisible de falla y la vida util, que es "
                        "a quien la nota al pie de la Tabla N 02 le asigna la "
                        "decision",
        sensibilidad=("los maximos recomendados de la Tabla N 02, que el "
                      "proyecto adopta por defecto: R = 30 % con n = 25 anios "
                      "(quebrada importante, TR 71) y R = 35 % con n = 15 "
                      "anios (quebrada menor y descarga de cunetas, TR 35)",
                      "cualquier R menor y/o cualquier n mayor que declare el "
                      "Propietario: la tabla es un techo y solo se puede bajar "
                      "de el. El TR crece al bajar R o al subir n -- p.ej. "
                      "R = 20 % con n = 25 da TR = 113 anios --, y con el "
                      "crece el caudal de diseno"),
        opcional=True,      # sin declarar, rigen los maximos de la Tabla N 02
        resolucion=DeTabla(
            tablas=("MC_HHD.T02",),
            que_elige="la fila de tipo de obra con su R y su n, cuando el "
                      "Propietario adopta valores distintos de los maximos "
                      "recomendados que el proyecto toma por defecto",
        ),
    ),

    "umbral_area_quebrada_importante_ha": Criterio(
        # ha. ADOPCION DEL PROYECTO, SIN FUENTE QUE LA FIJE, y la ficha lo dice
        # asi desde T-1 (INF-5.1.3). Hasta entonces este comentario y la
        # `justificacion` defendian el 100 con las areas de los dos puntos de
        # Familia A de `tests/ejemplo_puntos.csv` --«por debajo de las areas
        # de sus dos puntos»--, que es un argumento circular: el umbral se
        # justificaba con los datos de prueba que el propio umbral clasifica,
        # y M1 dice de esos puntos que no son del expediente. El VALOR no
        # cambia (moverlo cambiaria el periodo de retorno de un punto real);
        # cambia lo que lo sostiene, que ahora es lo que la fuente dice, lo
        # que no dice, la direccion del conservadurismo y el barrido.
        valor=100.0,
        nivel=NIVEL_PERFIL,
        sensibilidad=(50.0, 200.0),  # ha; la ventana se barre: `--barrido umbral_area_quebrada_importante_ha=50,100,200`
        etiqueta="A",
        forma=FORMA_FLOAT,
        concepto="Area de cuenca a partir de la cual el cauce de un punto de "
                 "Familia A se clasifica como 'quebrada importante' (TR 71) en "
                 "vez de 'quebrada menor' (TR 35) en la Tabla N 02",
        justificacion="Decide a partir de que area de cuenca el cauce de un "
                      "punto de Familia A se clasifica como quebrada "
                      "importante (periodo de retorno de 71 anios) en vez de "
                      "quebrada menor (35 anios). La fuente (Tabla N 02, "
                      "num. 3.6 del Manual de Hidrologia, transcrita en "
                      "constantes_normativas.TABLA_02_FILAS) nombra las dos "
                      "categorias y les asigna riesgo admisible y vida util, "
                      "de donde sale el periodo de retorno de cada una. Lo "
                      "que no entrega -- ni esa tabla, ni sus notas al pie, "
                      "ni ningun otro apartado del Manual, verificado contra "
                      "el texto -- es una regla que diga cuando un cauce cae "
                      "en una categoria o en la otra: no hay umbral de area, "
                      "ni de caudal, ni de longitud, ni de orden de cauce. "
                      "El Manual nombra las categorias y las tarifa, no las "
                      "define, y la hoja de ruta (Sec. 2.3) hereda el hueco. "
                      "Se adopta un umbral de area de cuenca, y es una "
                      "adopcion del proyecto en sus dos mitades: el "
                      "descriptor (el area, que es el dato que la Sec. 1.1 "
                      "califica de solo clasificador) y el numero. Ninguna "
                      "fuente tecnica reconocida fija el numero, y por eso "
                      "la etiqueta no es la de un vacio cubierto con fuente "
                      "ajena. Los 100 ha (1 km2) no se defienden por lo que "
                      "clasifican en un conjunto de puntos dado, sino por "
                      "tres cosas que no dependen de ningun punto. Primera, "
                      "la direccion: bajar el umbral solo puede pasar cauces "
                      "de quebrada menor a quebrada importante, que es mas "
                      "periodo de retorno y mas caudal, de modo que el "
                      "extremo bajo de la ventana es el conservador. "
                      "Segunda, la sensibilidad: entre una fila y la otra el "
                      "periodo de retorno se duplica, y la ventana de 50 a "
                      "200 ha se barre para mostrar que puntos del "
                      "expediente cambian de fila y cuanto cambia su "
                      "diametro; un punto que cambia dentro de la ventana "
                      "no esta decidido por la norma sino por esta adopcion, "
                      "y la memoria lo tiene que decir. Tercera, la via "
                      "alterna: la categoria se puede declarar cauce por "
                      "cauce, y entonces este criterio no interviene y la "
                      "eleccion se documenta punto por punto",
        fuente="PENDIENTE - Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
               "Tabla N 02 (num. 3.6): da R y n por categoria de cauce y NO "
               "define 'quebrada importante' ni 'quebrada menor' por umbral "
               "de area, longitud ni caudal. Verificado contra el texto",
        reemplazado_por="Clasificacion del cauce documentada punto por punto "
                        "(categoria explicita a M1), o umbral tomado de un "
                        "estudio hidrologico de la cuenca del Bajo Piura",
        verificacion_pendiente="Si se adopta un umbral, declarar en la memoria "
                               "que puntos quedan a cada lado y correr la "
                               "sensibilidad del Q con TR 71 y TR 35: es la "
                               "misma alcantarilla con dos caudales de diseno",
        resolucion=Libre(
            que_lo_fija="el proyectista: el Manual nombra las categorias de "
                        "cauce y las tarifa, y NO da regla de asignacion "
                        "fisica -- ni area, ni caudal, ni orden de cauce",
            dominio="ha > 0",
        ),
    ),

    # --- T-1 --- las tres decisiones del calculo hidrologico (MH) ----------
    # Solo se invocan cuando el caudal lo CALCULA el programa (--cuencas y
    # --estacion con `Q_m3s` vacio). Las tres llevan valor de archivo con su
    # fuente y su ventana, y las tres se pueden barrer. Lo que NO es criterio
    # y si entrada: el metodo del tiempo de concentracion va por cuenca, en
    # la columna `metodo_tc` del CSV de cuencas, porque su validez depende
    # de la pendiente de CADA cuenca y un valor unico para el corredor
    # dejaria fuera de rango a las que no se le parecen.

    "distribucion_precipitacion_maxima": Criterio(
        valor="mejor_ajuste_ks",
        # NIVEL POR LA REGLA, medido por `tests/test_t1_hidrologia.py`: lo
        # invoca la Fase 1-bis en una corrida `--alcance perfil` con cuencas
        # y estacion. Las corridas del fixture traen `Q_m3s` lleno y no
        # llegan a el.
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # La regla de eleccion mas las ocho distribuciones del num. 3.7.1.
        # Cinco de las ocho se pueden declarar y NO se evaluan: ver
        # `verificacion_pendiente`.
        sensibilidad=("mejor_ajuste_ks", "normal", "lognormal_2p", "gumbel",
                      "lognormal_3p", "gamma_2p", "gamma_3p",
                      "log_pearson_3", "log_gumbel"),
        concepto="Distribucion de probabilidad con que se ajusta la serie de "
                 "precipitacion maxima en 24 horas para obtener la lluvia "
                 "del periodo de retorno de diseno",
        justificacion="Decide con que modelo de probabilidad se extrapola la "
                      "serie de la estacion hasta el periodo de retorno de "
                      "diseno. La fuente (num. 3.7.1 del Manual de "
                      "Hidrologia, cita MC_HHD.3.7.1) recomienda ocho "
                      "distribuciones sin preferir ninguna, y su num. 3.7.2 "
                      "(cita MC_HHD.3.7.2b#ELIGE) dice que la prueba de "
                      "Kolmogorov-Smirnov permite elegir la mas "
                      "representativa, la de mejor ajuste. Se adopta esa "
                      "regla como valor de archivo: se ajustan las "
                      "distribuciones que el programa evalua y se toma la de "
                      "menor diferencia maxima D, siempre que pase la "
                      "prueba. La alternativa es declarar una distribucion "
                      "concreta, que entonces se usa aunque otra ajuste "
                      "mejor, y tambien tiene que pasar la prueba. "
                      "La regla tiene un limite que hay que conocer: la "
                      "prueba mide la mayor diferencia de probabilidad sobre "
                      "toda la serie, y una serie de poblacion mixta -- anios "
                      "corrientes y dos o tres anios del fenomeno El Nino -- "
                      "puede ajustar muy bien en el cuerpo y dejar los "
                      "extremos por encima de la lluvia de diseno. Pasar la "
                      "prueba no garantiza que el periodo de retorno de "
                      "diseno cubra lo ya observado; por eso el paso del "
                      "ajuste contrasta la lluvia de diseno con el maximo de "
                      "la serie y lo avisa cuando queda por debajo. "
                      "Sensibilidad: la memoria imprime la precipitacion de "
                      "diseno de cada distribucion evaluada, con su D, de "
                      "modo que el efecto de elegir otra se lee en el mismo "
                      "paso; entre las tres la lluvia de diseno puede diferir "
                      "mas de un 20 %, y la de menor D no es por fuerza la "
                      "mayor",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. 3.7.1 "
               "'Modelos de distribución', pag. impresa 25 (PDF 28), y num. "
               "3.7.2 b) 'Prueba Kolmogorov – Smirnov', pag. impresa 32 "
               "(PDF 35): citas MC_HHD.3.7.1 (RECOMENDACION) y "
               "MC_HHD.3.7.2b#ELIGE (PERMISO)",
        verificacion_pendiente="De las ocho distribuciones del num. 3.7.1 el "
                               "programa evalua tres: normal, log normal de "
                               "2 parametros y Gumbel, que son las unicas de "
                               "las que el Manual imprime como se estiman "
                               "los parametros (num. 3.7.1.1, 3.7.1.2 y "
                               "3.7.1.7). Declarar cualquiera de las otras "
                               "cinco detiene el calculo con «metodo no "
                               "evaluable»: falta una fuente que fije su "
                               "estimador. 'mejor_ajuste_ks' elige entre las "
                               "tres evaluadas, no entre las ocho",
        resolucion=Libre(
            que_lo_fija="el proyectista: el Manual recomienda ocho "
                        "distribuciones y permite elegir por la prueba de "
                        "Kolmogorov-Smirnov; no manda ninguna",
            dominio="declaracion de la distribucion o de la regla de "
                    "eleccion; el conjunto cerrado viaja en `sensibilidad`",
        ),
    ),

    "nivel_significancia_ks": Criterio(
        valor=0.05,                 # alfa, adimensional
        nivel=NIVEL_PERFIL,         # mismo consumidor y misma medida que
                                    # 'distribucion_precipitacion_maxima'
        etiqueta="A",
        forma=FORMA_FLOAT,
        sensibilidad=(0.01, 0.10),  # las columnas extremas de la Tabla N 03
        concepto="Nivel de significancia alfa con que se lee el valor "
                 "critico de la prueba de Kolmogorov-Smirnov",
        justificacion="Decide con que nivel de significancia se acepta o se "
                      "rechaza el ajuste de la distribucion. La fuente "
                      "(Tabla N 03 del Manual de Hidrologia, cita "
                      "MC_HHD.3.7.2b#T03) tabula el valor critico para tres "
                      "niveles, 0.10, 0.05 y 0.01, y el texto habla del "
                      "nivel de significancia seleccionado sin seleccionar "
                      "ninguno. Se adopta 0.05, la columna central de la "
                      "tabla. La ventana son sus dos columnas extremas. La "
                      "direccion importa y no es la intuitiva: con alfa = "
                      "0.10 el valor critico es menor y la prueba rechaza "
                      "mas ajustes, de modo que el extremo alto de la "
                      "ventana es el exigente; con alfa = 0.01 casi "
                      "cualquier distribucion pasa. Sensibilidad: para una "
                      "serie de 25 anios el valor critico va de 0.24 a 0.32 "
                      "entre los dos extremos; el nivel no mueve la lluvia "
                      "de diseno, solo decide si el ajuste se acepta",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. 3.7.2 "
               "b) y Tabla N 03 'Valores críticos d para la prueba "
               "Kolmogorov – Smirnov', pags. impresas 32 y 33 (PDF 35 y 36): "
               "citas MC_HHD.3.7.2b y MC_HHD.3.7.2b#T03",
        resolucion=Libre(
            que_lo_fija="el proyectista: la Tabla N 03 ofrece tres niveles "
                        "y el Manual no elige ninguno",
            dominio="probabilidad adimensional, entre las columnas extremas "
                    "de la Tabla N 03",
        ),
    ),

    # --- VE-5 (mh, ficha T1-01) --- El numero de intervalos de la prueba
    # chi-cuadrado, que el num. 3.7.2 a) pide y no fija.
    "intervalos_de_clase_chi_cuadrado": Criterio(
        valor="sturges",
        nivel=NIVEL_PERFIL,         # lo lee la Fase 1-bis (MH) en el paso de
                                    # la bondad de ajuste (tests/test_ve5_mh.py)
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("sturges", "raiz_de_n"),
        concepto="Regla con que se fija el numero k de intervalos de clase de "
                 "la prueba chi-cuadrado (num. 3.7.2 a del Manual de "
                 "Hidrologia), que el programa imprime como contraste de la "
                 "de Kolmogorov-Smirnov",
        justificacion="Decide cuantos intervalos de clase tiene la prueba "
                      "chi-cuadrado. La fuente (num. 3.7.2 a, pag. impresa "
                      "31, cita MC_HHD.3.7.2a#INTERVALOS) manda repartir los "
                      "datos en k intervalos de clase y no fija "
                      "k ni como se trazan; ninguna fuente del repositorio de "
                      "normas lo fija. Se adopta la regla de Sturges, k = 1 + "
                      "⌈log2 n⌉, que es la regla clasica de los histogramas "
                      "y la que da menos intervalos con las series cortas de "
                      "la hidrologia vial (25 años: 6), de modo que cada "
                      "intervalo tiene eventos esperados suficientes; la "
                      "alternativa es k = ⌈√n⌉ (25 años: 5). Los intervalos "
                      "son de igual amplitud entre el menor y el mayor dato, "
                      "con el primero abierto por abajo y el ultimo por "
                      "arriba para que los esperados sumen n (lectura del "
                      "proyecto de «intervalos de clase»). Pesa poco por "
                      "construccion: la prueba chi-cuadrado no detiene el "
                      "calculo ni elige la distribucion --lo hace la de "
                      "Kolmogorov-Smirnov, que el Manual dice que «permite "
                      "elegir» (cita MC_HHD.3.7.2b#ELIGE)--; se imprime como "
                      "contraste, solo para la normal y la log normal, que "
                      "son las que el numeral dice que verifica. "
                      "Sensibilidad: con 25 años, 6 intervalos y 3 grados de "
                      "libertad (Sturges) frente a 5 y 2 (raiz de n); el "
                      "valor critico al 5 % pasa de 7.81 a 5.99",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. 3.7.2 "
               "a) 'Prueba χ²', pag. impresa 31 (PDF 34): citas "
               "MC_HHD.3.7.2a, MC_HHD.3.7.2a#INTERVALOS y "
               "MC_HHD.3.7.2a#ALCANCE. La regla de Sturges no esta en el "
               "repositorio de normas: es adopcion del proyecto",
        resolucion=Libre(
            que_lo_fija="el proyectista: el num. 3.7.2 a) pide k intervalos "
                        "de clase y no fija cuantos",
            dominio="declaracion de la regla; el conjunto cerrado viaja en "
                    "`sensibilidad`",
        ),
    ),

    "relacion_intensidad_duracion": Criterio(
        valor="dick_peschke",
        nivel=NIVEL_PERFIL,         # mismo consumidor y misma medida que
                                    # 'distribucion_precipitacion_maxima'
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        # --- VE-5 (mh, ficha T1-05) --- La tercera opcion es la relacion
        # regional de la ecuacion (17), con sus factores en
        # 'factores_idf_regional' [S].
        sensibilidad=("dick_peschke", "tabla_04_coeficientes_de_duracion",
                      "idf_regional_ec17"),
        concepto="Relacion con que la precipitacion maxima en 24 horas se "
                 "lleva a la intensidad de una lluvia de duracion igual al "
                 "tiempo de concentracion",
        justificacion="Decide como se obtiene la intensidad de diseno a "
                      "partir de la lluvia de 24 horas cuando no hay "
                      "registros pluviograficos. La fuente (num. 3.8.1 del "
                      "Manual de Hidrologia) ofrece dos caminos y los dos "
                      "son permisos: la relacion de Dick y Peschke (cita "
                      "MC_HHD.3.8.1#DICK_PESCHKE), para duraciones menores "
                      "de 1 hora o cuando no hay pluviografo, y los "
                      "coeficientes de duracion de su Tabla N 04 (cita "
                      "MC_HHD.3.8.1#T04), de 1 a 48 horas, que el propio "
                      "texto pide usar con criterio y cautela. Se adopta "
                      "Dick y Peschke por dos razones: es la unica de las "
                      "dos que cubre las duraciones menores de 1 hora, que "
                      "son las de una cuneta y de casi toda cuenca pequena, "
                      "y da mas lluvia que la tabla en todo el tramo comun "
                      "por debajo de 24 horas, que es el lado conservador. "
                      "Sensibilidad: para una "
                      "duracion de 1 hora Dick y Peschke asigna el 45 % de "
                      "la lluvia de 24 horas y la Tabla N 04 el 25 %, de "
                      "modo que la intensidad y el caudal son un 81 % "
                      "mayores con el valor adoptado; a 6 horas, 71 % "
                      "frente a 56 %. Desde VE-5 hay una tercera opcion, "
                      "'idf_regional_ec17': la relacion I = K·T^m / t^n de la "
                      "ecuacion (17) del mismo numeral (cita "
                      "MC_HHD.3.8.1#EC17), con t la duracion en minutos y K, m "
                      "y n los factores caracteristicos de la zona, que un "
                      "estudio regional entrega y se declaran en "
                      "'factores_idf_regional' [S]; con ella la lluvia de 24 "
                      "horas de la estacion no da la intensidad y la memoria "
                      "la imprime al lado como contraste",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. 3.8.1 "
               "'Curvas Intensidad – Duración – Frecuencia', ecuacion (16) "
               "en la pag. impresa 37 (PDF 40) y Tabla N 04 en las pags. "
               "impresas 36 y 37 (PDF 39 y 40): citas "
               "MC_HHD.3.8.1#DICK_PESCHKE y MC_HHD.3.8.1#T04, las dos de "
               "caracter PERMISO",
        verificacion_pendiente="La Tabla N 04 no dice que se interpole "
                               "entre sus filas ni cubre menos de 1 hora: "
                               "con ella elegida, una duracion intermedia "
                               "se interpola linealmente por lectura del "
                               "proyecto y una menor de 1 hora detiene el "
                               "calculo. La relacion regional I = K·T^m/t^n "
                               "(ecuacion 17) se evalua desde VE-5 con los "
                               "factores declarados en "
                               "'factores_idf_regional' [S]; sin ellos se "
                               "detiene",
        resolucion=Libre(
            que_lo_fija="el proyectista: el num. 3.8.1 permite las dos "
                        "relaciones y no manda ninguna",
            dominio="declaracion de la relacion; el conjunto cerrado viaja "
                    "en `sensibilidad`",
        ),
    ),

    # --- VE-5 (mh, ficha T1-05) --- LA PUERTA DE LA IDF REGIONAL. Sin valor:
    # los tres factores son de un estudio regional, no de esta obra ni de
    # este archivo, y solo se leen cuando 'relacion_intensidad_duracion' =
    # «idf_regional_ec17».
    "factores_idf_regional": Criterio(
        valor=None,                 # VACIO: solo lo lee la relacion ec. (17)
        nivel=NIVEL_PERFIL,         # lo consume la Fase 1-bis (MH), que corre
                                    # a perfil; ninguna corrida de archivo lo
                                    # invoca porque la relacion de archivo es
                                    # Dick y Peschke (lo mide tests/test_ve5_mh.py)
        etiqueta="S",
        # Sin `campos_obligatorios`: la puerta los exige CON TEXTO (EXT-6) y
        # estos son numeros. Las tres claves y su signo los comprueba el
        # consumidor, `MH.factores_idf_regional`, con DatoInvalidoError.
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Factores K, m y n de la relacion regional intensidad-"
                 "duracion-frecuencia I = K·T^m / t^n (ecuacion 17 del Manual "
                 "de Hidrologia): I en mm/h, T en años y t en minutos",
        justificacion="Da la intensidad de diseño cuando el proyecto declara "
                      "'idf_regional_ec17' en 'relacion_intensidad_duracion'. "
                      "La fuente (num. 3.8.1 del Manual de Hidrologia, pag. "
                      "impresa 38, cita MC_HHD.3.8.1#EC17) escribe la relacion "
                      "y dice que K, m y n son propios de la zona de estudio: "
                      "no da ningun valor. Es [S] y no [A]: "
                      "no hay nada que elegir, los tres salen de ajustar la "
                      "relacion a las curvas IDF de la zona (un estudio "
                      "regional o las curvas de una estacion pluviografica), "
                      "y cambian al mover la obra, no al cambiar de "
                      "proyectista. Vive aqui y no en datos_sitio.py porque "
                      "sigue pendiente del estudio y comparte tablero con la "
                      "relacion que lo pide. Los tres tienen que ser numeros "
                      "positivos: K da la escala, m hace crecer la intensidad "
                      "con el periodo de retorno y n la hace decrecer con la "
                      "duracion, que es la relacion inversa entre duracion e "
                      "intensidad que describe el num. 3.9",
        fuente="PENDIENTE - Estudio regional de curvas intensidad-duracion-"
               "frecuencia de la zona del corredor (o curvas IDF de una "
               "estacion pluviografica representativa), con los factores de "
               "la ecuacion (17) del num. 3.8.1 del Manual de Hidrologia, "
               "Hidraulica y Drenaje, pag. impresa 38 (PDF 41)",
        trazabilidad="El estudio que ajusta la relacion I = K·T^m / t^n: su "
                     "autor y fecha, la estacion o la region de la que salen "
                     "las curvas, el rango de duraciones y de periodos de "
                     "retorno del ajuste, y las unidades (I en mm/h, T en "
                     "años, t en minutos, que son las de la ecuacion 17). La "
                     "estructura del dato es un diccionario con tres claves "
                     "obligatorias: 'K', 'm' y 'n', numeros positivos. "
                     "Ambito: la zona del estudio; si el corredor cruza dos "
                     "zonas con factores distintos, la relacion regional no "
                     "vale para el corredor entero y el caudal de las obras "
                     "de la otra zona se declara en Q_m3s",
        reemplazado_por="Curvas IDF del estudio hidrologico del expediente",
        resolucion=DeEnsayo(
            ensayo="ajuste de la relacion I = K·T^m / t^n a las curvas IDF de "
                   "la zona del corredor",
            trazabilidad_exigida="estudio, estacion o region, rango de "
                                 "duraciones y de periodos de retorno del "
                                 "ajuste, y unidades",
        ),
    ),

    # --- T-1, tras el auditor adversarial: cuatro decisiones mas -----------

    "duracion_minima_lluvia_min": Criterio(
        valor=5.0,                  # minutos
        nivel=NIVEL_PERFIL,         # lo invoca la Fase 1-bis en cada caudal
                                    # calculado (medido en test_t1_hidrologia)
        etiqueta="C",
        forma=FORMA_FLOAT,
        # La ventana: desde el minimo que la fuente manda hasta el intervalo
        # mas corto del que, segun la misma fuente, suele haber dato medido.
        sensibilidad=(5.0, 15.0),
        concepto="Duracion minima de la lluvia de diseno: el piso que se "
                 "aplica cuando el tiempo de concentracion calculado queda "
                 "por debajo",
        justificacion="Fija la menor duracion de lluvia con que se calcula "
                      "la intensidad de diseno. El vacio es de la norma "
                      "peruana: el Manual de Hidrologia iguala la duracion "
                      "al tiempo de concentracion (cita "
                      "MC_HHD.3.8.1#DURACION) y no le pone piso, de modo que "
                      "una cuneta corta o una plataforma dan tiempos de 1 a "
                      "2 min y las relaciones de intensidad, extrapoladas "
                      "hasta ahi, entregan intensidades de mas de 1000 mm/h. "
                      "Lo cubre el Hydraulics Manual de WSDOT (cita "
                      "WSDOT_HM.2-6.3#TC_MINIMO), que manda usar 5 min como "
                      "duracion cuando el tiempo de concentracion es menor, "
                      "y da dos razones: las curvas de intensidad por debajo "
                      "de ese tiempo son extrapolacion, y la lluvia tarda en "
                      "generar escorrentia. Se aplica asi: si el tiempo de "
                      "concentracion es menor que el minimo, la lluvia de "
                      "diseno dura el minimo y el paso lo dice. La direccion "
                      "es la no conservadora -- un piso mas alto baja la "
                      "intensidad -- y por eso se adopta el extremo bajo de "
                      "la ventana, que es el que la fuente escribe. "
                      "Sensibilidad: con la relacion de Dick y Peschke la "
                      "intensidad varia con la duracion elevada a -0.75, de "
                      "modo que pasar de 5 a 10 min la reduce un 41 % y a "
                      "15 min un 56 %",
        fuente="WSDOT Hydraulics Manual M 23-03.12 (abril de 2026), num. "
               "2-6.3 'Time of Concentration', pag. impresa 2-10 (PDF 46): "
               "cita WSDOT_HM.2-6.3#TC_MINIMO, caracter EXIGENCIA; repetido "
               "en el num. 2-6.4 'Rainfall Intensity', pag. impresa 2-11 "
               "(PDF 47). Fuente tecnica, no norma peruana",
        resolucion=Libre(
            que_lo_fija="el proyectista, sobre el minimo de la fuente "
                        "tecnica: el Manual de Hidrologia no fija ninguno",
            dominio="minutos > 0",
        ),
    ),

    "tc_fuera_de_la_poblacion_del_metodo": Criterio(
        valor="no_evaluable",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("no_evaluable", "indicador_con_aviso"),
        concepto="Que se hace cuando la cuenca queda fuera de la poblacion "
                 "de la que salio la formula de tiempo de concentracion "
                 "declarada",
        justificacion="Decide si una formula empirica de tiempo de "
                      "concentracion se evalua en una cuenca que no se "
                      "parece a las cuencas de las que salio. La fuente "
                      "(Tabla N 05 del Manual de Hidrologia) describe esa "
                      "poblacion en sus observaciones -- pendientes de 3 a "
                      "10 % para Kirpich, cuencas de menos de 800 ha para la "
                      "ecuacion de retardo -- y no dice que hacer fuera: "
                      "describe, no prohibe. Se adopta no evaluar, que es "
                      "mas estricto que la fuente: el calculo del punto se "
                      "detiene y pide otro metodo. Se adopta asi porque "
                      "extrapolar una formula empirica es justo el riesgo de "
                      "un corredor de llanura, donde las pendientes no "
                      "llegan al 1 %. El mismo trato se da a la formula de "
                      "California, porque la tabla dice de ella que es "
                      "esencialmente la de Kirpich: sin eso el limite se "
                      "saltaria cambiando el nombre del metodo. La "
                      "alternativa evalua la formula igual y lo imprime como "
                      "indicador con aviso. No alcanza a la formula de "
                      "Temez, cuya fuente si escribe un rango de aplicacion, "
                      "ni a la de la Federal Aviation Administration, a la "
                      "que la tabla no le describe poblacion numerica. "
                      "Sensibilidad: el criterio no mueve el tiempo de "
                      "concentracion, solo decide si el punto se calcula o "
                      "se detiene",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), Tabla N 05 "
               "'Fórmulas para el cálculo del tiempo de concentración', "
               "pags. impresas 39 y 40 (PDF 42 y 43), columna de "
               "observaciones: citas MC_HHD.3.9#T05_KIRPICH, "
               "MC_HHD.3.9#T05_CALIFORNIA y MC_HHD.3.9#T05_SCS, de caracter "
               "APROXIMACION. La tabla describe la poblacion; el trato "
               "fuera de ella es adopcion del proyecto",
        resolucion=Libre(
            que_lo_fija="el proyectista: la Tabla N 05 describe de que "
                        "cuencas salio cada formula y no dice que hacer "
                        "fuera de ellas",
            dominio="declaracion del trato; el conjunto cerrado viaja en "
                    "`sensibilidad`",
        ),
    ),

    "coeficiente_uniformidad_temez": Criterio(
        valor="aplicar",
        nivel=NIVEL_PERFIL,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("aplicar", "no_aplicar"),
        concepto="Si el caudal lleva el coeficiente de uniformidad K del "
                 "metodo racional modificado cuando el tiempo de "
                 "concentracion sale de la formula de Temez",
        justificacion="Decide que se hace con el resto del metodo cuando de "
                      "el se toma una sola pieza. La formula de Temez (cita "
                      "MC_HHD.3.12.2.1#TC) no es una fila de la Tabla N 05: "
                      "es la ecuacion del tiempo de concentracion del metodo "
                      "racional modificado, cuyo caudal lleva un coeficiente "
                      "de uniformidad K mayor que 1 (cita "
                      "MC_HHD.3.12.2.1#K) y ademas su propia intensidad y su "
                      "propio coeficiente de escorrentia por numero de "
                      "curva. El proyecto usa esa formula con el metodo "
                      "racional simple, que es un uso hibrido y se declara "
                      "como tal. Se adopta aplicar K: es del mismo numeral, "
                      "crece con el tiempo de concentracion y corrige "
                      "justamente lo que el racional simple supone y una "
                      "cuenca de varias horas no cumple, la lluvia uniforme "
                      "en el tiempo; y es el lado conservador, porque K "
                      "sube el caudal. La alternativa calcula con la "
                      "ecuacion del racional simple sin K. Sensibilidad: K "
                      "vale 1.07 para un tiempo de concentracion de 1 h, "
                      "1.15 para 2 h y 1.29 para 4 h, de modo que no "
                      "aplicarlo baja el caudal entre un 6 y un 22 % en ese "
                      "tramo",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. "
               "3.12.2.1 'Método Racional Modificado', ecuaciones (29), (30) "
               "y (31), pag. impresa 51 (PDF 54): citas MC_HHD.3.12.2.1#K "
               "(DEFINICION) y MC_HHD.3.12.2.1#TC (APROXIMACION)",
        verificacion_pendiente="El criterio rige SOLO por debajo de 10 km2: "
                               "ahi lo que se calcula con la formula de "
                               "Temez es un hibrido declarado, con o sin K. "
                               "Desde VE-2 (fichas T1-08 y VE2-F de "
                               "docs/decisiones_diferidas.md), de 10 a "
                               "770 km2 el caudal sale del metodo racional "
                               "modificado completo --su intensidad, su "
                               "factor reductor por area y su coeficiente "
                               "por numero de curva-- y K es parte de su "
                               "ecuacion (29): va siempre y este criterio "
                               "no se lee",
        resolucion=Libre(
            que_lo_fija="el proyectista: el Manual da K dentro de un metodo "
                        "del que el proyecto toma solo el tiempo de "
                        "concentracion, y no dice si K acompaña a esa pieza "
                        "fuera del metodo",
            dominio="declaracion; el conjunto cerrado viaja en `sensibilidad`",
        ),
    ),

    # --- VE-2 (d) --- decision del dueño (2026-11-17) sobre VE1-02 (d) ---
    "factor_intervalo_fijo_p24": Criterio(
        valor=1.0,                  # adimensional: la serie tal cual
        nivel=NIVEL_PERFIL,         # lo invoca la Fase 1-bis en cada caudal
                                    # calculado, a perfil (medido en
                                    # tests/test_ve2_hidrologia.py)
        etiqueta="A",
        forma=FORMA_FLOAT,
        # De la serie tal cual (el Manual) al 1.13 de la practica.
        sensibilidad=(1.0, 1.13),
        concepto="Factor por el que se multiplica cada maximo anual de "
                 "precipitacion en 24 horas de la serie de la estacion, ANTES "
                 "del ajuste de frecuencia, para llevar una lectura de "
                 "intervalo fijo a la maxima de 24 horas corridas",
        justificacion="Decide si la serie de maximas en 24 horas entra al "
                      "ajuste tal como la entrega la estacion o corregida "
                      "por intervalo fijo. La fuente no la corrige: el num. "
                      "3.8.1 del Manual de Hidrologia estima la lluvia de una "
                      "duracion a partir de la precipitacion maxima en 24 "
                      "horas multiplicada por un coeficiente de duracion "
                      "(cita MC_HHD.3.8.1#P24), y el de 24 horas en su Tabla "
                      "N 04 es 1.00 (cita MC_HHD.3.8.1#T04). Se adopta 1.00, "
                      "la lectura literal del Manual. El extremo alto de la "
                      "ventana, 1.13, es una practica que aplican la tesis "
                      "UPAO y la via TU-107 de la validacion externa (VE1-02 "
                      "(d)) y que esta sin fuente en el repositorio de "
                      "normas: «1.13», «intervalo fijo», «fixed interval», "
                      "«Weiss», «OMM» y «WMO» no aparecen como factor de "
                      "lluvia en ningun PDF. Pasaria a [C] solo si se trae al "
                      "repositorio de normas la guia de la OMM o el trabajo "
                      "de Weiss que la practica cita, con su pagina. "
                      "Se aplica a la serie y no al cuantil: corrige cada "
                      "lectura, y con eso el contraste del ajuste con lo "
                      "observado sigue comparando lo mismo. Las tres "
                      "distribuciones que el programa ajusta son de escala, "
                      "de modo que el cuantil sale exactamente multiplicado "
                      "por el factor. Sensibilidad: con 1.13 la lluvia de "
                      "diseño sube un 13 % exacto, el caudal del racional "
                      "simple tambien, y el del racional modificado algo mas "
                      "(su coeficiente de escorrentia crece con la lluvia); "
                      "con el valor de archivo nada cambia",
        fuente="Manual de Hidrologia, Hidraulica y Drenaje (MTC), num. 3.8.1 "
               "'Curvas Intensidad – Duración – Frecuencia', pag. impresa 36 "
               "(PDF 39), y Tabla N 04, fila de 24 horas (1.00), pag. impresa "
               "37 (PDF 40): citas MC_HHD.3.8.1#P24 (DEFINICION) y "
               "MC_HHD.3.8.1#T04 (PERMISO). El 1.13 del extremo alto de la "
               "ventana: practica sin fuente en el repositorio de normas",
        resolucion=Libre(
            que_lo_fija="el proyectista: el Manual usa la maxima en 24 horas "
                        "sin conversion y ninguna fuente del repositorio de "
                        "normas da otro factor",
            dominio="adimensional, de 1.00 (la serie tal cual) a 1.13",
        ),
    ),

    "coeficiente_escorrentia_superficie_vial": Criterio(
        valor={
            # Coeficientes de 10 AÑOS de periodo de retorno, DERIVADOS de la
            # Table 2-2 del registro por `_coeficientes_de_superficies_viales`.
            "coeficientes_10_anios": _COEFICIENTES_VIALES_WSDOT,
            # El incremento que el num. 2-6.2 manda al diseñar para una
            # tormenta menos frecuente, por periodo de retorno en años.
            "incremento_por_periodo_de_retorno": {"10": 0.0, "25": 0.10,
                                                  "50": 0.20, "100": 0.25},
            "tope": 0.95,
        },
        nivel=NIVEL_PERFIL,         # lo invoca la Fase 1-bis cuando la
                                    # cobertura de la fila es una superficie
                                    # vial (medido en test_t1_hidrologia)
        etiqueta="C",
        forma=FORMA_DICT_CON_CAMPOS,
        concepto="Coeficiente de escorrentia de las superficies de la "
                 "plataforma vial que la Tabla N 08 no tiene: pavimento, "
                 "berma de tierra y talud de tierra o con cesped, con su "
                 "incremento por periodo de retorno",
        justificacion="Da el coeficiente de escorrentia del area tributaria "
                      "de una cuneta. El vacio es de la norma peruana: la "
                      "Tabla N 08 del Manual de Hidrologia tabula cinco "
                      "coberturas de cuenca natural y no tiene fila para una "
                      "superficie pavimentada ni para un talud, y el num. "
                      "4.1.2.1 b) pide el coeficiente de escurrimiento de la "
                      "cuenca de la cuneta sin dar tabla. Lo cubre la Table "
                      "2-2 del Hydraulics Manual de WSDOT (cita "
                      "WSDOT_HM.2-6.2#T2-2), de la que se toman solo cuatro "
                      "filas: pavimento 0.90, berma de tierra 0.50, talud de "
                      "tierra 0.60 y talud con cesped 0.30, que valen lo "
                      "mismo en las tres columnas de pendiente. Esos numeros "
                      "son de una tormenta de 10 anios de periodo de "
                      "retorno; la misma fuente (cita "
                      "WSDOT_HM.2-6.2#FRECUENCIA) manda aumentarlos un 10 % "
                      "para 25 anios, un 20 % para 50 y un 25 % para 100, "
                      "sin pasar de 0.95. Entre esas frecuencias la fuente "
                      "no dice nada: se toma el incremento de la frecuencia "
                      "tabulada inmediatamente mayor, que es el lado "
                      "conservador; por encima de 100 anios no hay "
                      "frecuencia mayor que tomar y el calculo se detiene. "
                      "Con el periodo de retorno de 35 anios de una "
                      "alcantarilla de alivio el pavimento queda en el tope, "
                      "0.95, y el talud de tierra en 0.72. No sustituye a la "
                      "Tabla N 08 para una cuenca natural: una cobertura de "
                      "cuenca se sigue leyendo de la tabla peruana",
        fuente="WSDOT Hydraulics Manual M 23-03.12 (abril de 2026), Table "
               "2-2 'Runoff Coefficients for the Rational Method: 10-Year "
               "Return Frequency', pag. impresa 2-9 (PDF 45), y num. 2-6.2 "
               "'Runoff Coefficients', pag. impresa 2-8 (PDF 44): citas "
               "WSDOT_HM.2-6.2#T2-2 y WSDOT_HM.2-6.2#FRECUENCIA. Fuente "
               "tecnica, no norma peruana",
        resolucion=Derivada(
            de=("WSDOT_HM.T2-2",),
            regla="las cuatro filas viales de la tabla del registro, leidas "
                  "por `_coeficientes_de_superficies_viales()`; los "
                  "incrementos y el tope son los del num. 2-6.2 de la misma "
                  "fuente (cita WSDOT_HM.2-6.2#FRECUENCIA)",
        ),
    ),
}
