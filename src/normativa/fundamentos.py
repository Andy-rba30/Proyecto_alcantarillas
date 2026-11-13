"""
Los FUNDAMENTOS: por que se hace cada paso del calculo.

QUE PROBLEMA RESUELVE ESTE ARCHIVO. La memoria sabia decir *que* se calculo y
*cuanto* dio; no sabia decir *por que se calcula*. Ese "por que" estaba escrito
--y bien escrito-- en dos sitios donde el revisor de una memoria no entra: la
hoja de ruta v8 y los docstrings de los modulos. Un docstring lo lee un
programador. Aqui el mismo texto queda como DATO, con su cita, y M11 lo imprime
dentro del paso al que pertenece (`PasoDeMemoria.por_que`, Sec. 4.4 del plan
v12).

LA INVARIANTE QUE HACE QUE ESTO NO SEA PROSA (T11). `verbo` tiene que ser
compatible con el `caracter` de sus citas, y la compatibilidad la comprueba
`Registro.problemas_de_integridad` sobre `VERBO_COMPATIBLE_CON`. Es lo que
impide escribir «la norma OBLIGA a...» encima del parrafo que dice
«recomendandose que la velocidad minima sea igual a 0.25 m/s». El proyecto ya
se tropezo con esa confusion en los dos sentidos: `NOR-MEM-01` (el matiz de
recomendacion de V2 que no llegaba a la memoria) y `MAT-O13` (el mismo matiz
faltando en V1, que nace de una frase del mismo apartado).

LO QUE UN FUNDAMENTO NO ES. No es la justificacion de un VALOR --eso es
`criterios_adoptados.Criterio.justificacion`-- ni la transcripcion de la fuente
--eso es `Cita.texto_literal`--. Es la razon por la que el paso existe: que
pasa si no se hace. Por eso `que_pasa_si_no_se_hace` es obligatorio en la
practica de este archivo: un fundamento que no sabe decir que se rompe sin el
no esta fundando nada.

LOS QUE FALTAN ESTAN CENSADOS, NO OMITIDOS. `SIN_FUNDAMENTO` enumera los pasos
del pipeline que hoy no pueden tener uno, con la razon exacta y con lo que
habria que transcribir para traerlos. Un `Fundamento` exige al menos una cita
del registro; inventarle una cita a V5 o a V9 para que la tabla quede completa
seria fabricar la clase de defecto que este proyecto viene retirando.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .esquema import EstadoFundamento, Fundamento, Verbo

FUNDAMENTOS: Dict[str, Fundamento] = {}

# LOS CODIGOS DE PASO QUE CAMBIARON DE NOMBRE, y a cual apuntan hoy (T-0).
#
# El id de un fundamento es tambien el CODIGO DEL PASO que lo emite: viaja en
# `PasoDeMemoria.fundamento_id`, es el ancla de la ficha en la memoria HTML y
# la clave con que un lector de la traza busca un paso. Renombrarlo sin mas
# rompe a quien guardo el nombre viejo --una traza volcada, un indice de
# formulas sellado, un script que filtra pasos--. Por eso el nombre anterior
# no se borra: se censa aqui, y las tres puertas que resuelven un id lo
# entienden (`Registro.fundamento`, `modelos.paso` y `id_vigente`, que es la
# que un lector usa para comparar un id guardado con uno recien emitido).
#
# UN ALIAS NO ES UN SEGUNDO FUNDAMENTO: no esta en `FUNDAMENTOS`, no aparece
# en `Registro.fundamentos` ni en los manifiestos, y lo que se EMITE es
# siempre el id vigente. Solo sirve para leer.
#
#   F4.YC_RECT -> F4.YC   el paso del tirante critico. El id decia «RECT»
#                         porque lo redacto el plan de la Familia C para el
#                         marco, y desde C4 funda el paso de LAS DOS formas
#                         (anotado como C4-2 en docs/ruta_familia_c.md, sin
#                         corregir; INF-5.1.10).
ALIAS_DE_FUNDAMENTO: Dict[str, str] = {
    "F4.YC_RECT": "F4.YC",
}


def id_vigente(id_: str) -> str:
    """El id con que hoy se emite un fundamento, dado el vigente o un alias."""
    return ALIAS_DE_FUNDAMENTO.get(id_, id_)


def _fundamento(**kw) -> Fundamento:
    f = Fundamento(**kw)
    if f.id in FUNDAMENTOS:
        raise ValueError(f"fundamento duplicado: {f.id}")
    if f.id in ALIAS_DE_FUNDAMENTO:
        raise ValueError(
            f"«{f.id}» es el nombre ANTERIOR de «{ALIAS_DE_FUNDAMENTO[f.id]}» "
            "(ALIAS_DE_FUNDAMENTO): un alias no puede volver a ser un id")
    FUNDAMENTOS[f.id] = f
    return f


# Los rotulos de fase, escritos una vez. No son los de `cli.FASE_*` --este
# paquete no puede importar la capa de reporte-- sino los de la hoja de ruta,
# que es de donde sale el texto.
F1 = "Fase 1 - Datos de entrada"
F2 = "Fase 2 - Clasificacion y periodo de retorno"
F3 = "Fase 3 - Tipo, material y durabilidad"
F4 = "Fase 4 - Dimensionamiento hidraulico"
F5 = "Fase 5 - Verificaciones"
F6 = "Fase 6 - Proteccion de entrada y salida"
F7 = "Fase 7 - Compatibilidad geometrica"
F8 = "Fase 8 - Verificacion estructural del conducto"
F10 = "Fase 10 - Alcantarillas de alivio: espaciamiento"
# --- T-7a --- la Fase 9 deja de ser solo una nota de proyecto: el cabezal
# por punto emite pasos, y sus fundamentos viven aqui con los demas.
F9 = "Fase 9 - Cabezal y aletas"


# ===========================================================================
# Fase 1 - Datos de entrada
# ===========================================================================

TW = _fundamento(
    id="F1.TW",
    fase=F1,
    que_paso=("TW en el cuerpo receptor: nivel de agua durante la avenida, "
              "por Manning en la seccion del receptor (Sec. 1.3)"),
    por_que=(
        "El TW no es una propiedad de la alcantarilla: es el nivel que el "
        "cuerpo receptor tiene MIENTRAS pasa la avenida, y de el depende que "
        "el control de salida ahogue o no la descarga. Medirlo no sirve --lo "
        "que se mediria es el nivel de HOY, no el de la avenida de diseño-- y "
        "por eso Sec. 1.3 lo hace CALCULAR: con el caudal de diseño del "
        "propio receptor, su pendiente y su seccion, Manning da el tirante "
        "normal y de ahi la cota de agua. La alternativa que este paso "
        "sustituye no es un TW peor: es un TW supuesto, del que la memoria no "
        "puede decir de donde salio."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta S20 (SIS-B-04): las dos columnas que el "
        "procedimiento consume --`Q_receptor_m3s` y `cota_TW`-- se cargaban, "
        "se validaban y no las leia nadie, de modo que un expediente con las "
        "dos llenas seguia exigiendo un TW declarado a mano por la linea de "
        "comandos. El numero que gobierna el control de salida entraba como "
        "una opcion de la corrida en vez de como el resultado de un "
        "procedimiento con fuente."),
)


# ===========================================================================
# Fase 2 - Clasificacion y periodo de retorno
# ===========================================================================

LUZ = _fundamento(
    id="F2.LUZ",
    fase=F2,
    que_paso="Denominacion de la obra por su luz: alcantarilla o puente",
    por_que=(
        "El umbral de 6.0 m no es una convencion de este proyecto: separa dos "
        "cuerpos normativos distintos. Por debajo, la obra se disena con el "
        "Manual de Hidrologia, Hidraulica y Drenaje; a partir de 6.0 m es un "
        "puente y el que manda es el Manual de Puentes, con otro tren de "
        "cargas, otras combinaciones y otro procedimiento sismico. El paso se "
        "hace ANTES que ningun otro porque decide que norma se aplica al "
        "resto: no es una etiqueta descriptiva, es la eleccion del marco."),
    verbo=Verbo.DEFINE,
    # R48-001 (cierre C11): las dos definiciones a las que el 4.1.1.5.1
    # remite o con las que convive, para que la memoria diga QUE magnitud
    # compara el umbral (la abertura de la estructura, no el ancho del
    # cauce). La discrepancia DIS-LUZ-DENOMINACION llega por estas citas.
    citas=("MC_HHD.4.1.1.3.1", "MC_HHD.4.1.1.5.1",
           "MP.GLOSARIO#OBRAS_DE_ARTE_MENORES", "AASHTO_LRFD_9.1.2#BRIDGE",
           "HDS5_3ED.1.2#NBIS"),
    que_pasa_si_no_se_hace=(
        "Un cruce de luz mayor o igual a 6.0 m se dimensionaria con el "
        "aparato de una alcantarilla, y la memoria citaria numerales de un "
        "manual que no lo gobierna. El script se detiene en vez de emitir esa "
        "memoria: la Fase 2 lo declara fuera de alcance."),
)

TR = _fundamento(
    id="F2.TR",
    fase=F2,
    que_paso=("Periodo de retorno del caudal de diseno, obtenido del riesgo "
              "admisible y la vida util de la Tabla N 02"),
    por_que=(
        "El caudal de diseno no se elige: se deduce de cuanto riesgo de falla "
        "se acepta durante la vida util de la obra. La Tabla N 02 fija ese "
        "riesgo por tipo de obra y el TR sale de la relacion "
        "R = 1 - (1 - 1/T)^n. Todo lo hidraulico que viene despues --diametro, "
        "tirante, velocidad, carga a la entrada-- cuelga de este numero, y por "
        "eso es el primero que la memoria tiene que poder defender."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.3.6",),
    que_pasa_si_no_se_hace=(
        "Sin TR declarado no hay caudal de diseno defendible: el Q del CSV "
        "quedaria sin decir a que probabilidad corresponde, y dos puntos con "
        "el mismo caudal y distinta importancia se dimensionarian igual."),
)


# ===========================================================================
# Fase 3 - Tipo, material y durabilidad
# ===========================================================================

D_MIN = _fundamento(
    id="F3.D_MIN",
    fase=F3,
    que_paso="Seccion minima circular de 0.90 m (36\")",
    por_que=(
        "El minimo no lo pone la hidraulica --un conducto menor transporta el "
        "caudal-- sino el MANTENIMIENTO: por debajo de 0.90 m no entra una "
        "persona a limpiar el conducto, y una alcantarilla que no se puede "
        "limpiar se colmata y deja de ser una alcantarilla. Por eso el "
        "diametro adoptado se compara contra este piso aunque la verificacion "
        "de capacidad ya haya pasado."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.4a",),
    que_pasa_si_no_se_hace=(
        "El bucle de diseno adoptaria el menor diametro que transporta el "
        "caudal, que en los puntos de poco Q de este corredor es bastante "
        "menor de 0.90 m, y el expediente quedaria con conductos "
        "inmantenibles."),
)


# ===========================================================================
# Fase 4 - Dimensionamiento hidraulico
# ===========================================================================

MANNING = _fundamento(
    id="F4.MANNING",
    fase=F4,
    que_paso=("Tirante normal y velocidad en el conducto, por Manning: UNA "
              "geometria (el tirante, con n_max) y DOS velocidades, una por "
              "cada extremo del rango de la Tabla N 09"),
    por_que=(
        "La rugosidad de un conducto no es un numero: la Tabla N 09 da un "
        "rango por material, y el rango no es incertidumbre de medicion sino "
        "el estado real de la superficie a lo largo de la vida de la obra. "
        "Resolver con un solo n obliga a elegir cual, y esa eleccion cambia de "
        "signo segun que se verifique: contra un TECHO de velocidad el extremo "
        "conservador es el n minimo --la estimacion alta-- y contra un PISO es "
        "el n maximo --la baja--. Por eso el calculo fija UNA geometria --el "
        "tirante normal con n_max, que es el que mas llena el conducto-- y "
        "sobre ella evalua DOS velocidades, una por cada n, y cada "
        "verificacion consume la que la deja del lado seguro. No son dos "
        "escenarios independientes: es una seccion y dos rugosidades sobre "
        "la misma seccion."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6", "MC_HHD.4.1.1.3.6#T09"),
    que_pasa_si_no_se_hace=(
        "Con una sola rama, la mitad de las verificaciones corre por el lado "
        "inseguro sin que nada lo diga. Es exactamente el defecto que V2 tuvo "
        "hasta que se corrigio (MAT-D1): evaluaba el piso de velocidad con la "
        "estimacion alta, o sea declaraba «cumple» justo en el caso en que el "
        "conducto sedimenta."),
)

CONTROL = _fundamento(
    id="F4.CONTROL",
    fase=F4,
    que_paso=("Carga a la entrada HW por los dos controles del HDS-5, "
              "entrada y salida, y adopcion del mayor"),
    por_que=(
        "Una alcantarilla puede estar limitada por lo que la embocadura deja "
        "entrar o por lo que el barril y la descarga dejan salir, y cual de "
        "los dos manda no se sabe de antemano: depende de la pendiente, de la "
        "longitud, del tirante en el receptor y del propio caudal. El HDS-5 "
        "resuelve los dos regimenes por separado y el que gobierna es el que "
        "exige MAS carga, porque es el que el flujo tiene que vencer para "
        "pasar. Calcular uno solo no es un atajo: es no saber cual se calculo."),
    verbo=Verbo.DEFINE,
    # T-0 (INF-5.1.10): entra la tercera, que es la que dice «adopcion del
    # mayor». Las dos primeras sostienen como se calcula cada control; ninguna
    # decia cual manda, y el paso 4.4 citaba la A.2 --ecuaciones de entrada--
    # como si lo dijera.
    citas=("HDS5_3ED.A.2", "HDS5_3ED.3.1.4#K", "HDS5_3ED.3.3.5#GOBIERNA"),
    que_pasa_si_no_se_hace=(
        "El HW impreso seria el de un regimen que quiza no gobierna, y las "
        "verificaciones que cuelgan de el --V4 resguardo bajo subrasante, V5 "
        "remanso en el derecho de via-- se harian contra una carga menor que "
        "la real."),
)

HO = _fundamento(
    id="F4.HO",
    fase=F4,
    que_paso=("Altura de la linea de energia a la salida, h_o = max(TW, "
              "(d_c + D)/2)"),
    por_que=(
        "El control de salida necesita saber a que altura sale el agua, y esa "
        "altura la fija el receptor cuando el tirante aguas abajo es alto y la "
        "propia seccion cuando no lo es. El HDS-5 aproxima el segundo caso con "
        "la media entre el tirante critico y el diametro. Es una APROXIMACION "
        "declarada como tal por la fuente, no una definicion: la fuente le "
        "pone condicion de uso --solo si el barril fluye lleno en la mayor "
        "parte de su longitud, y no si la entrada no esta sumergida-- y el "
        "proyecto la evalua punto por punto en vez de suponerla cumplida: "
        "los dos limites sobre HW/D en este paso, y la longitud a seccion "
        "llena en el paso del perfil (4.3c), que desde E-A la mide. Donde la "
        "propia fuente dice que la aproximacion no debe usarse (HW/D < 0.75) "
        "el HW del punto es el del remanso y no el de este paso."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.3.3#HO", "HDS5_3ED.3.3.3#HO_SUMERGIDA",
           "HDS5_3ED.3.3.3#HO_1_2D", "HDS5_3ED.3.1.4#0_75D"),
    que_pasa_si_no_se_hace=(
        "Aplicar la aproximacion fuera de su rango sin decirlo: el HW de "
        "control de salida saldria de una formula que su propia fuente "
        "desautoriza para ese caso, y nadie se enteraria (NOR-HDS-05). Y "
        "decirlo no basta: hasta EXT-3 el punto se aceptaba con el aviso "
        "puesto y el paso imprimia NO_CUMPLE mientras el pipeline aceptaba. "
        "Bajo HW/D < 0.75 el metodo NO esta definido para el punto: hasta "
        "E-A eso viajaba como bloqueo «metodo no evaluable», diferible a "
        "nivel de perfil y no de expediente (EXT-M-02); desde E-A la carga "
        "de ese punto es la del REMANSO (paso 4.3c, HDS-5 pag. 3.12: «For "
        "lower headwaters, backwater calculations are required») y la "
        "aproximacion se imprime como lo que es, un numero fuera de su "
        "dominio. Y la primera condicion --que el barril fluya lleno en la "
        "mayor parte de su longitud-- ya no se declara: se MIDE en el "
        "mismo paso."),
)

REGIMEN = _fundamento(
    id="F4.REGIMEN",
    fase=F4,
    que_paso=("Regimen del barril y velocidad a la salida, con el area que "
              "HDS-5 3.1.6 asigna a cada caso"),
    por_que=(
        "El tirante y la velocidad con que se verifica el barril no son "
        "siempre los del flujo uniforme de Manning: dependen de como fluye el "
        "barril, y eso lo decide el tirante en el receptor y el control que "
        "gobierna. Con el TW sobre la clave el barril va lleno y la unica "
        "seccion es la entera; bajo control de entrada el flujo es "
        "supercritico y se aproxima al tirante normal; bajo control de salida "
        "con salida libre el agua pasa por el tirante critico a la salida. El "
        "HDS-5 fija con que area se mide la velocidad a la salida en cada "
        "caso --tirante critico, TW o seccion entera, segun el TW--, y esa "
        "velocidad es la que dimensiona la proteccion de la Fase 6: en "
        "pendiente suave con salida libre es MAYOR que la uniforme, y la "
        "piedra que sale de la uniforme es chica. Y «lleno» con el TW sobre "
        "la clave describe la salida y el tramo aguas abajo del resalto: bajo "
        "control de entrada la sumergencia de la salida no asegura flujo "
        "lleno en toda la longitud (HDS-5 3.1.3). Lo que el HDS-5 no da sin "
        "un perfil de la lamina de agua es el tirante DENTRO del conducto "
        "bajo control de salida con el barril parcialmente lleno, y ahi el "
        "proyecto no inventa un criterio de llenado: hasta E-A lo declaraba "
        "pendiente, y desde E-A lo resuelve el perfil por paso directo del "
        "paso 4.3c, del que V1 y V2 toman el tirante maximo y la velocidad "
        "minima del barril."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.1.6#V_SALIDA", "HDS5_3ED.3.1.6#V_SALIDA_TW",
           "HDS5_3ED.3.3.2#V_SALIDA_ENTRADA", "HDS5_3ED.3.1.3#SUMERGENCIA"),
    que_pasa_si_no_se_hace=(
        "Lo que pasaba hasta EXT-3 (EXT-M-01, PC-04): con TW = 1.2 m sobre "
        "un tubo de 0.90 m la memoria decia «manda TW: la salida esta "
        "ahogada» y en la misma pagina V1 [OK] con y/D = 0.135 y V2 con la "
        "velocidad uniforme, cuando a seccion llena no hay borde libre y la "
        "velocidad es Q/A_llena = 0.0786 m/s < 0.25; y la Fase 6 recibia "
        "1.184 m/s donde la velocidad de salida es 1.508."),
)


PERFIL = _fundamento(
    id="F4.PERFIL",
    fase=F4,
    que_paso=("Perfil de la lamina de agua por paso directo desde la salida "
              "hacia la entrada: longitud a seccion llena y carga a la "
              "entrada por remanso (HDS-5 pag. 3.12 y Section 3.5)"),
    por_que=(
        "Bajo control de salida con el barril parcialmente lleno la lamina "
        "de agua dentro del conducto no es la del flujo uniforme: la fija el "
        "extremo aguas abajo --el tirante critico en la salida o el del "
        "receptor, el mayor-- y desde alli remonta hacia la entrada. El "
        "HDS-5 lo escribe como el calculo de remanso que la aproximacion "
        "h_o = (d_c + D)/2 existe para evitar, y lo manda de vuelta en dos "
        "sitios: cuando la carga cae bajo 0.75D el remanso «is required», y "
        "por encima «should be used to check» la aproximacion. Con el perfil "
        "se saben tres cosas que sin el se declaraban: cuanto del barril va "
        "a seccion llena --la primera condicion de uso de h_o, que hasta E-A "
        "no se podia medir--, el tirante maximo y la velocidad minima del "
        "barril --lo que V1 y V2 comparan--, y la carga a la entrada donde "
        "la aproximacion no vale. Y una cuarta que deshace una circularidad: "
        "si la lamina que sube desde la salida corta el tirante critico antes "
        "de llegar a la entrada, el control de salida no impone carga alguna "
        "--el barril es supercritico y gobierna la entrada--, cosa que la "
        "aproximacion, que solo compara dos numeros, no puede ver."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.1.4#REMANSO", "HDS5_3ED.3.1.4#EMPALME",
           "HDS5_3ED.3.1.4#HW_REMANSO", "HDS5_3ED.3.1.4#0_75D",
           "HDS5_3ED.3.5#PERFIL", "HDS5_3ED.3.5.1#S1",
           "HDS5_3ED.3.5.1#TIPO7", "HDS5_3ED.3.3.3#HO"),
    que_pasa_si_no_se_hace=(
        "Lo que pasaba hasta E-A: V1 y V2 quedaban PENDIENTES por «metodo no "
        "evaluable» bajo control de salida parcialmente lleno, la carga con "
        "HW/D < 0.75 viajaba con el mismo bloqueo, y la primera condicion de "
        "h_o se transcribia sin medirse. Y el caso (b) del dictamen "
        "(Q = 0.3, S = 0.005, TW = 0) se publicaba bajo control de SALIDA "
        "con HW/D = 0.589 siendo un barril supercritico (y_n = 0.2965 < "
        "y_c = 0.3157): la aproximacion decidia el control con un h_o que la "
        "fuente le prohibe usar ahi."),
)


# ===========================================================================
# Fase 5 - Verificaciones
# ===========================================================================

V1 = _fundamento(
    id="F5.V1",
    fase=F5,
    que_paso=("V1 - Borde libre: y no mayor que la relacion de llenado "
              "adoptada (por defecto 0.75 de la altura, diametro o flecha "
              "de la estructura, el complemento del 25 % recomendado)"),
    por_que=(
        "Una alcantarilla que trabaja a seccion llena deja de comportarse como "
        "un canal y pasa a comportarse como un conducto a presion: la "
        "capacidad se vuelve sensible a la entrada, el aire atrapado pulsa y "
        "cualquier obstruccion parcial embalsa aguas arriba. El borde libre es "
        "el margen que mantiene el flujo en regimen libre. El Manual lo "
        "escribe como el 25 % de «la altura, diametro o flecha de la "
        "estructura»; el 0.75 es su complemento aritmetico, no una cifra "
        "impresa. LA PARAFRASIS ESTABA RECORTADA -- decia «el 25 % de la "
        "altura de la estructura» -- y el recorte importa desde C5: es "
        "justamente la enumeracion de tres magnitudes la que hace que el "
        "numeral cubra al marco sin analogia ninguna. Con «altura» a secas "
        "un lector podia entender que la fuente habla de una sola forma y "
        "que el cajon entra por extension; entra por el texto. Y cuando el "
        "barril va LLENO no hay 25 % que medir: el mismo parrafo lo prohibe "
        "--«las alcantarillas no deben ser diseñadas para trabajar a seccion "
        "llena»--, y ahi el veredicto se apoya en esa exigencia y no en la "
        "recomendacion del umbral."),
    verbo=Verbo.RECOMIENDA,
    # DOS CITAS DEL MISMO PARRAFO CON DOS FUERZAS (EXT-3): la del 25 % es
    # RECOMENDACION y es la que el verbo sigue; la de «no deben ser diseñadas
    # para trabajar a seccion llena» es EXIGENCIA y sostiene el «no cumple»
    # de V1 cuando el barril fluye LLENO (TW >= D), donde no hay 25 % que
    # medir. El verbo se queda en RECOMIENDA porque lo que este paso lleva de
    # la fuente como UMBRAL sigue siendo el par recomendado; T11 aceptaria
    # OBLIGA por la segunda cita y seria el agujero que `F5.V7` ya midio.
    citas=("MC_HHD.4.1.1.3.7b", "MC_HHD.4.1.1.3.7b#LLENA"),
    que_pasa_si_no_se_hace=(
        "El diseno aceptaria conductos trabajando a seccion llena o casi "
        "llena, donde el modelo de Manning con que se dimensionaron ya no "
        "describe el flujo. Y hasta EXT-3 los aceptaba: con el TW sobre la "
        "clave V1 seguia midiendo el tirante normal de Manning y daba [OK] "
        "con y/D = 0.135 sobre un barril que iba lleno (EXT-M-01)."),
)

# EL VERBO ES `RECOMIENDA` Y NO `OBLIGA`, Y ESO NO ES TIMIDEZ: es la unica
# lectura que las citas sostienen. La primera de las dos --- «debe contemplar
# mantener un borde libre minimo» --- SI es EXIGENCIA, de modo que poner
# `OBLIGA` pasaria T11 sin que ningun test se quejara. Seria exactamente el
# agujero estructural que C7 midio en `F5.V7`: T11 mira el `caracter` de la
# cita, no de que trata. Y aqui el «de que trata» es decisivo por partida
# doble: esa exigencia obliga a que HAYA borde libre --- no dice cuanto --- y
# obliga sobre un BADEN, no sobre un canal. Lo unico que este paso lleva de la
# fuente es el par de numeros, y ese par la fuente lo RECOMIENDA.
VC1 = _fundamento(
    id="F5.VC1",
    fase=F5,
    que_paso=("VC1 - Cruce de canal: el agua embalsada a la entrada no llega "
              "a la coronacion del canal, con su borde libre"),
    por_que=(
        "En un paso de canal no hay remanso libre aguas arriba. El agua que la "
        "alcantarilla embalsa no se extiende sobre el terreno: sube DENTRO del "
        "canal, que es un cauce confinado entre dos coronaciones, y si llega a "
        "la coronacion desborda sobre parcelas de terceros ANTES de entrar al "
        "conducto. Por eso esta verificacion mide contra una cota que ninguna "
        "otra de la Fase 5 mira: V1 mide el llenado DENTRO del barril y V4 "
        "mide contra la subrasante de la VIA. Las tres pueden cumplirse a la "
        "vez con el canal desbordado, y ese fue el estado del programa hasta "
        "aqui. "
        "QUE PARTE DE ESTO ES DE LA FUENTE Y CUAL ES DEL PROYECTO. Del "
        "proyecto: el REQUISITO --- lo fija la Sec. 2.3 de la hoja de ruta, "
        "«no puede alterar la rasante hidraulica ni el borde libre del "
        "canal», y no un numeral del MTC --- y la DESIGUALDAD con que se "
        "comprueba. De la fuente, y solo esto: que un borde libre haya que "
        "mantenerlo, y el par de valores 0.30-0.50 m con que se cuantifica. "
        "Ese par el Manual lo escribe para un BADEN y contra la superficie de "
        "rodadura; llevarlo a la coronacion de un canal es analogia declarada "
        "del proyectista, y elegir el 0.50 dentro de la banda es una segunda "
        "decision suya. Las dos viven en 'borde_libre_canal_m' [A], con la "
        "banda por ventana. EL MANUAL NO FIJA BORDE LIBRE PARA UN CANAL: "
        "verificado por ausencia sobre sus 225 paginas."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.4.1e", "MC_HHD.4.1.1.4.1e#RANGO"),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta esta sesion, y estaba declarado: §13 de "
        "`docs/ruta_familia_c.md` llamaba a VC1 «la verificacion que de "
        "verdad gobierna a la Familia C» y ninguna linea de codigo la "
        "implementaba. Un cruce de canal salia acreditado por V1, V4 y V4b "
        "--- que miden contra el barril y contra la via --- sin que nada "
        "hubiera mirado el canal. La declaracion de alcance lo decia; el "
        "veredicto de la memoria, no."),
)

V2 = _fundamento(
    id="F5.V2",
    fase=F5,
    que_paso=("V2 - Velocidad minima de autolimpieza: V no menor que el "
              "piso adoptado (por defecto los 0.25 m/s recomendados)"),
    por_que=(
        "El piso de velocidad no protege el conducto: protege su CAPACIDAD. "
        "Por debajo de cierta velocidad el material fino en suspension "
        "sedimenta, el area util baja y la alcantarilla deja de pasar el "
        "caudal para el que se calculo, sin que nada se haya roto. Es la razon "
        "por la que este minimo vale igual para todos los materiales, mientras "
        "que el techo de la Tabla N 10 cambia con el revestimiento: el piso lo "
        "pone la sedimentacion y el techo la abrasion."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.6#VMIN_INICIO", "MC_HHD.4.1.1.3.6#VMIN"),
    que_pasa_si_no_se_hace=(
        "El expediente entregaria conductos que sedimentan, y el caudal de "
        "diseno de la memoria seria el de una seccion que la obra no va a "
        "tener despues de la primera avenida."),
)

V2B = _fundamento(
    id="F5.V2b",
    fase=F5,
    que_paso=("V2b - Sedimentacion / colmatacion: el indicador de pendiente "
              "del HDS-5 mas el acceso de mantenimiento declarado"),
    por_que=(
        "V2 pone un PISO DE VELOCIDAD y con eso protege el caso normal, pero "
        "no ve el caso que de verdad colmata una alcantarilla en una llanura "
        "de riego: el conducto tendido MAS PLANO que el cauce que lo "
        "alimenta. Ahi el agua llega con su carga de finos, pierde pendiente "
        "al entrar y la deja dentro, y puede hacerlo aun cumpliendo el piso "
        "de V2 en el caudal de diseno, porque la colmatacion la producen los "
        "caudales bajos y frecuentes, no la avenida. El HDS-5 nombra "
        "exactamente esa comparacion como indicador, y es una comparacion "
        "entre dos numeros que este calculo ya tiene: la pendiente del barril "
        "y la del cauce natural. La otra mitad de la fila --el acceso de "
        "mantenimiento-- existe porque ningun indicador evita la limpieza: la "
        "evita el acceso, y el acceso se dibuja o no existe."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.5.3.3#INDICADORES", "HDS5_3ED.5.3.3#ALINEADO"),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta S20: la fila V2b de la tabla de Fase 5 no "
        "existia en ninguna linea de codigo (SIS-A-13, MAT-O15). Un punto con "
        "el conducto mas plano que su cauce salia de la memoria sin una sola "
        "linea sobre colmatacion, y la obligacion de prever el acceso de "
        "limpieza no la recordaba nada -- de modo que los planos podian "
        "omitirla sin que el expediente se enterara."),
)

# EL REGIMEN DE V2B ES UNA ELECCION, Y LO QUE LA SOSTIENE ES QUE LA FUENTE
# DEFINE Y NO EXIGE (PF-4). El verbo es DEFINE porque el `caracter` de las
# dos citas es DEFINICION -- la 5.11 escribe «are key indicators of potential
# problems», sin cifra y sin «shall»/«should» (verificado contra el PDF en
# PF-4) -- y `VERBO_COMPATIBLE_CON` no admite otro. Escribir «la norma exige
# S_conducto >= S_cauce» encima de ese parrafo seria NOR-MEM-01. Lo consume la
# `EleccionDeProyecto` del criterio `regimen_v2b` dentro del paso F5.V2b, que
# sigue fundado en `V2B`: este fundamento explica por que hay algo que
# ELEGIR, no por que existe la verificacion.
V2B_REGIMEN = _fundamento(
    id="F5.V2b.REGIMEN",
    fase=F5,
    que_paso=("V2b - El regimen con que se aplica el indicador de pendiente: "
              "umbral duro o indicador con aviso (`regimen_v2b`)"),
    por_que=(
        "El HDS-5 DEFINE dos indicadores de posibles problemas de "
        "sedimentacion -- pendiente del barril menor que la del cauce, y "
        "rugosidad mayor que la del cauce -- y no fija umbral ni prescribe "
        "que hacer cuando uno se dispara: son sintomas que la fuente pide "
        "reconocer, no una condicion de aceptacion del diseno. Que hace el "
        "proyecto con un indicador disparado es por tanto una ELECCION del "
        "proyectista, y una eleccion se declara con ficha, ventana y "
        "procedencia (`regimen_v2b`, [A]) en vez de vivir cableada como "
        "«decision conservadora» dentro de la verificacion. Las dos opciones "
        "son defendibles y no valen lo mismo en toda obra: en una entrada "
        "deprimida para ganar recubrimiento el umbral duro obliga a "
        "reconsiderar la rasante; en un cruce de canal la pendiente del "
        "conducto la fija el canal, y el aviso deja constancia del "
        "indicador y del acceso de limpieza sin descartar un marco que "
        "cumple todo lo demas."),
    verbo=Verbo.DEFINE,
    # --- T-2 --- La tercera cita es lo que la fuente dice del caso que el
    # indicador describe (pag. impresa 5.12): sedimenta sobre todo con
    # caudales bajos y suele limpiarse solo con los altos. Es lo que
    # sostiene el valor de archivo `indicador_con_aviso`.
    citas=("HDS5_3ED.5.3.3#INDICADORES", "HDS5_3ED.5.3.3#ALINEADO",
           "HDS5_3ED.5.3.3#DEPRESION"),
    que_pasa_si_no_se_hace=(
        "Lo que paso entre S20 y PF-4: el indicador se aplicaba como umbral "
        "duro sin que ningun criterio lo dijera, y en la corrida de perfil "
        "de la revision de E-B eso descarto los siete marcos de la "
        "progresion de C-01 con la pendiente de sonda (0.004 frente a "
        "0.006), sin que el proyectista tuviera donde declarar otra cosa "
        "ni la memoria dijera que habia una eleccion."),
)

V3 = _fundamento(
    id="F5.V3",
    fase=F5,
    que_paso=("V3 - Velocidad maxima admisible del revestimiento "
              "(Tabla N 10)"),
    por_que=(
        "El techo de velocidad protege el REVESTIMIENTO: por encima del "
        "maximo admisible el flujo abrasiona el concreto o la mamposteria y la "
        "obra se consume antes de su vida util. Por eso el limite cambia con "
        "el material --2.0 m/s la mamposteria de piedra, hasta 6.0 el "
        "concreto-- mientras que el piso de V2 no cambia con nada."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.6#T10",),
    que_pasa_si_no_se_hace=(
        "Se aceptarian velocidades que erosionan el revestimiento; y como el "
        "piso y el techo salen del MISMO numeral y de paginas contiguas, "
        "confundirlos es facil: es el defecto que V3 tuvo hasta que se separo "
        "el titulo de la tabla del parrafo que la sigue."),
)

V4 = _fundamento(
    id="F5.V4",
    fase=F5,
    que_paso=("V4 - Carga a la entrada bajo la subrasante, con el resguardo "
              "que fija el CBR"),
    por_que=(
        "El agua embalsada a la entrada no puede alcanzar la estructura del "
        "pavimento. Una subrasante saturada pierde capacidad de soporte y el "
        "paquete estructural que se diseno sobre ese CBR deja de ser valido; "
        "el resguardo es la distancia vertical que mantiene la subrasante "
        "fuera del agua, y crece cuanto peor es el suelo."),
    verbo=Verbo.OBLIGA,
    citas=("MS.4.5.4", "MS.9.1.3"),
    que_pasa_si_no_se_hace=(
        "La alcantarilla cumpliria hidraulicamente mientras arruina el "
        "pavimento que esta debajo del terraplen que la cubre."),
)

# EL VERBO DECIA «OBLIGA» Y NINGUNA DE SUS CITAS HABLABA DE FLOTACION. Hasta
# C7 este fundamento colgaba de `MP.T2.4.5.3.1-1` y `-2` y de nada mas: dos
# TABLAS DE FACTORES cuyos textos literales son «Combinaciones de Carga y
# Factores de Carga» y «Factores de carga para cargas permanentes». Las dos
# son EXIGENCIA, de modo que T11 pasaba -- T11 comprueba el `caracter` de la
# cita, no de que trata --, y aun asi el fundamento afirmaba una obligacion
# que ninguna de sus fuentes enunciaba. V7 corre a perfil desde el inicio del
# proyecto: el defecto es anterior a la Familia C y lo cierra C7.
V7 = _fundamento(
    id="F5.V7",
    fase=F5,
    que_paso="V7 - Flotacion del conducto vacio bajo el nivel freatico",
    por_que=(
        "Un conducto vacio bajo el nivel freatico es un flotador: la "
        "subpresion sobre su superficie exterior puede superar el peso propio "
        "mas el del relleno que lo cubre y levantarlo. En el Bajo Piura, con "
        "NF somero y arenas saturadas, no es un caso de laboratorio. "
        "QUE PARTE DE ESTO ES DE LA FUENTE Y CUAL ES DEL PROYECTO, que es lo "
        "que hay que poder separar al leer la memoria. De la fuente: que la "
        "subpresion se considere una fuerza de levantamiento sobre todos los "
        "componentes bajo el agua, y que haya que evaluarla cuando el invert "
        "queda bajo el freatico; y que a la carga permanente que AUMENTA la "
        "estabilidad se le investigue su factor MINIMO, que es lo que "
        "autoriza a minorar el relleno en vez de mayorarlo. Del proyecto: la "
        "desigualdad concreta con que se comprueba. Ninguna de las dos "
        "fuentes la escribe -- lo mas cercano es un COMENTARIO de AASHTO que "
        "dice, con `should`, que el peso sobre la clave supere el empuje --, "
        "de modo que la inecuacion es un ensamblaje: se arma con los gamma "
        "tabulados, la regla del minimo y la definicion de la fuerza. Se "
        "plantea en LRFD y no como factor de seguridad global porque el marco "
        "que el expediente adopta es LRFD de extremo a extremo. "
        "Y HAY UNA FRASE DE LA FUENTE QUE APUNTA AL REVES, que este parrafo "
        "declara en vez de dejar que la encuentre quien abra el PDF: el mismo "
        "Art. 12.6.1 de AASHTO que obliga a evaluar la flotacion dice, dos "
        "frases mas abajo y en el mismo parrafo, que «para el empuje vertical "
        "de tierra se debera aplicar el factor de carga MAXIMO de la Tabla "
        "3.4.1-2» -- y esta verificacion aplica el MINIMO --. Son dos `shall`, "
        "y el segundo es ademas el especial para estructuras enterradas. El "
        "proyecto lee esa frase como referida al diseno POR empuje de tierra, "
        "donde EV es la SOLICITACION y su maximo es el extremo desfavorable, "
        "y no al equilibrio de flotacion, donde EV es lo que SUJETA al "
        "conducto y el extremo desfavorable es el minimo. El argumento que lo "
        "sostiene es medible y no de autoridad: aplicar el maximo aqui haria "
        "la comprobacion MAS FACIL de cumplir, o sea que leerla literalmente "
        "en este sitio contradice el proposito del propio Art. 3.4.1. ES UNA "
        "LECTURA DEL PROYECTO -- el texto no trae esa salvedad -- y por eso "
        "vive declarada en la discrepancia DIS-AASHTO-GAMMA-EV-12.6.1, con "
        "estado ABIERTA."),
    verbo=Verbo.OBLIGA,
    citas=("MP.2.4.3.8.2",                      # EXIGENCIA -> sostiene OBLIGA
           "AASHTO_LRFD_9.12.6.1#FLOTACION",    # EXIGENCIA -> lo sostiene
           "AASHTO_LRFD_9.12.6.2.3#UPLIFT",     # EXIGENCIA -> lo sostiene
           "AASHTO_LRFD_9.3.7.2",               # EXIGENCIA (gemelo del peruano)
           "MP.2.4.5.3.1#MINIMO",               # EXIGENCIA: autoriza minorar
           # LA QUE APUNTA AL REVES, y va en la lista de citas de este mismo
           # fundamento a proposito: una discrepancia que solo vive en el
           # registro no la ve quien lee la memoria, y este proyecto la
           # declara EN EL PUNTO DE USO.
           "AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX",  # EXIGENCIA: el MAXIMO
           "MP.2.4.5.2#EV",                     # DEFINICION: que es EV
           "AASHTO_LRFD_9.C12.6.2.3",           # RECOMENDACION: la FORMA
           "MP.T2.4.5.3.1-1",                   # EXIGENCIA: los valores
           "MP.T2.4.5.3.1-2"),                  # EXIGENCIA: los valores
    que_pasa_si_no_se_hace=(
        "El conducto se dimensionaria solo por capacidad hidraulica y "
        "resistencia, que es el estado en que se pierden las alcantarillas de "
        "zonas con freatico alto: no fallan, flotan."),
)


# LA ELECCION DE FILA, QUE HASTA C7 NO TENIA FUNDAMENTO PROPIO y viajaba
# dentro del de V7 como si fuera parte de la misma afirmacion. No lo es: que
# haya que verificar la flotacion es EXIGENCIA de tres numerales, y que ESTA
# obra sea un «portico rigido» y no una «estructura rigida enterrada» no lo
# dice ninguna fuente. Separarlo es lo que permite imprimir cada cosa con su
# peso.
V7_FILA_GAMMA = _fundamento(
    id="F5.V7_FILA",
    fase=F5,
    que_paso=("Fila de gamma_p de la Tabla 2.4.5.3.1-2 que describe a esta "
              "estructura"),
    por_que=(
        "La tabla desglosa el empuje vertical de tierra por TIPO DE "
        "ESTRUCTURA, y ahi se acaba lo que la norma decide: A CUAL DE SUS "
        "SIETE FILAS DE EV pertenece esta obra no lo dice ningun numeral. Ni "
        "el Manual de Puentes ni AASHTO definen que es una «estructura rigida "
        "enterrada», ni un «portico rigido», ni donde empieza una «estructura "
        "flexible enterrada»: barridas las 673 paginas del Manual, fuera de "
        "la propia tabla las unicas apariciones son un parrafo de estructuras "
        "de contencion y un detalle de armadura, y ninguno clasifica una "
        "alcantarilla. La frontera es lectura del proyectista, y por eso el "
        "reparto entero vive en el criterio 'factores_carga_aashto' [A] y no "
        "en la transcripcion. "
        "DOS FILAS SI LAS DESCARTA LA TABLA MISMA, sea cual sea el conducto, "
        "y conviene saberlo para leer la lista de alternativas: «Estabilidad "
        "global» declara N/A en el minimo -- no tiene factor que aplicar --, "
        "y «Muros y estribos de retencion» es la del cabezal de la Fase 9 y "
        "lleva minimo 1.00 en vez de 0.90. Las otras CINCO estan todas "
        "abiertas: el proyecto pone hoy el tubo de concreto en «Estructura "
        "rigida enterrada», el marco en «Porticos rigidos», el HDPE en la "
        "subfila flexible «Alcantarillas termoplasticas» y el TMC en la "
        "flexible «Entre otros». "
        "LO QUE SI ESTA VERIFICADO PARA EL MARCO, que es lo que hace "
        "defendible su fila: el unico «cajon» que la tabla nombra es "
        "«Alcantarillas cajon METALICAS», colgado de las estructuras "
        "FLEXIBLES enterradas -- la categoria opuesta a un marco de concreto "
        "vaciado in situ --, de modo que no hay fila que le encaje mejor que "
        "«Porticos rigidos». Sigue siendo una eleccion, y la memoria tiene "
        "que imprimirla como tal y no como si la tabla la impusiera."),
    verbo=Verbo.DEFINE,
    citas=("MP.2.4.5.2#EV",         # DEFINICION -> sostiene DEFINE
           "MP.T2.4.5.3.1-2"),      # EXIGENCIA: la tabla con las filas
    que_pasa_si_no_se_hace=(
        "Se imprime una eleccion del proyectista con la autoridad de la "
        "tabla, que es el precedente NOR-HID-01: un valor defendible con una "
        "cita que no lo sostiene. Y con el marco es peor que con el tubo, "
        "porque el MINIMO de las dos filas vale 0.90 y el numero de V7 no "
        "cambia: nada falla de forma ruidosa mientras la fila impresa es la "
        "equivocada."),
)

# EL VERBO ES `DEFINE` Y NO `OBLIGA`, y es el mismo cuidado que F4.FORMA_HDS5
# documenta: lo que este paso hace es ELEGIR una fila, y lo que la fuente hace
# es DEFINIR la magnitud que esa fila afecta. Escribir OBLIGA pasaria T11 --la
# tabla es EXIGENCIA-- y diria algo falso: la tabla no obliga a elegir esta
# fila, no dice nada sobre cual toca.
#
# QUIEN SOSTIENE EL VERBO ES LA DEFINICION DE EV, no la tabla, y eso no es un
# rodeo para pasar T11: es la lectura correcta. Lo unico que la fuente DEFINE
# aqui es que EV es la presion vertical del peso propio del suelo de relleno;
# el reparto de esa magnitud en filas por tipo de estructura la tabla lo
# IMPONE, y a cual pertenece esta obra no lo dice nadie. Por eso la cita
# definitoria va primera y la tabla segunda.


# ===========================================================================
# Fase 6 - Proteccion de salida
# ===========================================================================

LAUSHEY = _fundamento(
    id="F6.LAUSHEY",
    fase=F6,
    que_paso=("Diametro medio del enrocado de proteccion a la salida, "
              "d50 = V^2 / (3.1 g)"),
    por_que=(
        "El chorro que sale del conducto lleva toda la energia que el barril "
        "no disipo y la descarga sobre el cauce natural, que no esta "
        "revestido. Si no se protege, la socavacion local retrocede hacia la "
        "obra y descalza la salida. El tamano de la piedra se dimensiona para "
        "que el flujo no la mueva: por eso d50 crece con el CUADRADO de la "
        "velocidad y no con ella."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.7c",),
    que_pasa_si_no_se_hace=(
        "La proteccion se dimensionaria a ojo, y la salida es donde estas "
        "obras fallan primero."),
)


# --- T-8 --- (cadena T) Los pasos que M6 emite desde T-8, ademas de Laushey:
# el Froude de la salida, la velocidad admisible del cauce, el apron de
# HEC-14, la geometria adoptada, el filtro, la proteccion de la entrada y la
# hoya de socavacion. NINGUNO LLEVA `OBLIGA`. El de la velocidad admisible
# lo llevo hasta la auditoria de T-8: su fuente escribe «debe limitarse»,
# pero lo que el paso hace con la tabla --leer «alta» como mayor que la
# admisible-- es lectura del proyecto (`citas.INTERPRETACION_VELOCIDAD_ALTA`)
# y se recomienda, no se obliga.
#
# REVISADOS UNO A UNO EN LA SEGUNDA AUDITORIA (H3, H6), con una regla: lo que
# el proyecto lee o hace se dice en nombre del proyecto, y lo que se atribuye
# a una fuente tiene que estar en el literal o en la nota de una de las citas
# del fundamento. Cayeron tres frases: «el Froude dice en que regimen entrega
# el conducto» (el propio paso 6.3 lo desmiente), «la fuente pide un
# disipador» cuando el chorro sale rapido (la Tabla 1.1 de HEC-14 da al apron
# Froude «na») y «el Manual recomienda proteger el cauce si la velocidad
# supera la tabla» (el Manual dice «alta» y no nombra la tabla).
FROUDE_SALIDA = _fundamento(
    id="F6.FROUDE",
    fase=F6,
    que_paso=("Numero de Froude de HEC-14 a la salida del conducto, Fr_e = "
              "V / (g·ye)^0.5, con el tirante equivalente"),
    por_que=(
        "HEC-14 forma su Froude de salida con un tirante EQUIVALENTE --el "
        "tirante mismo en un marco, la raiz de la mitad del area en un "
        "tubo-- para poder usar las mismas relaciones de diseño en las dos "
        "formas, y con el clasifica sus disipadores: su tabla de "
        "limitaciones lleva una columna de Froude, que para el apron de "
        "enrocado dice «no aplicable». Es un PARAMETRO DE DISEÑO de esa "
        "fuente y no "
        "clasifica el regimen del flujo: en un tubo el tirante equivalente "
        "no es el tirante hidraulico, y un chorro supercritico puede dar un "
        "Fr_e menor que 1. El regimen se lee aparte, del tirante de salida "
        "contra el critico, y el paso lo dice en su veredicto. Aqui no "
        "decide ninguna dimension: se publica junto a la velocidad con que "
        "se dimensiona la proteccion, porque es el numero con que quien "
        "diseñe un disipador por HEC-14 entra a elegirlo."),
    verbo=Verbo.DEFINE,
    citas=("HEC14.10.1.1#YE", "HDS5_3ED.3.1.6#V_SALIDA",
           "HEC14.3#CONTINUIDAD", "HEC14.1#T1_1_APRON"),
    que_pasa_si_no_se_hace=(
        "Quien tenga que pasar del apron a un disipador de HEC-14 no "
        "tendria el parametro con que esa fuente los clasifica, y tendria "
        "que rehacerlo sin saber con que velocidad y que area se formo."),
)

V_ADMISIBLE_CAUCE = _fundamento(
    id="F6.V_ADMISIBLE",
    fase=F6,
    que_paso=("Velocidad del flujo contra la maxima admisible del terreno "
              "del cauce (Tabla Nº 11)"),
    por_que=(
        "El conducto concentra el caudal en una seccion menor que la del "
        "cauce y lo entrega mas rapido de lo que el cauce lo llevaba. Que "
        "esa velocidad socave o no depende del material sobre el que "
        "descarga: una grava gruesa resiste lo que una arena fina no. El "
        "Manual exige limitar la velocidad de salida para que no socave el "
        "cauce aguas abajo y da, por tipo de terreno, la velocidad maxima "
        "que un cauce sin revestir admite; y recomienda proteger el cauce "
        "cuando la velocidad es «alta», sin decir cuanto. Leer «alta» como "
        "mayor que la admisible de la tabla es lectura del proyecto. El "
        "contraste INFORMA y no decide: si la velocidad supera la "
        "admisible, el terreno necesita la proteccion; si no la supera, el "
        "terreno la resistiria segun la tabla, y aun asi la proteccion se "
        "calcula y se mantiene, porque el HDS-5 describe el apron como "
        "practica corriente salvo que el campo diga que no hace falta."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.6#V_SALIDA", "MC_HHD.4.1.1.3.6#T11",
           "MC_HHD.4.1.1.3.7c#PROTECCION", "HDS5_3ED.5.3.2#PRACTICA"),
    que_pasa_si_no_se_hace=(
        "No se sabria en que salidas la socavacion es un riesgo declarado "
        "por el propio terreno, que es lo primero que mira quien tenga que "
        "decidir, con la inspeccion de campo, donde la proteccion se puede "
        "aligerar."),
)

APRON_HEC14 = _fundamento(
    id="F6.APRON",
    fase=F6,
    que_paso=("Tamaño de piedra del apron de enrocado por HEC-14, Ec. "
              "(10.4): D50 en funcion de Q, D y TW"),
    por_que=(
        "La formula de Laushey del Manual dimensiona la piedra con una sola "
        "variable, la velocidad. El apron de enrocado de HEC-14, que es al "
        "que el HDS-5 remite, la dimensiona con tres: el caudal, el "
        "diametro y el tirante del receptor. Las dos responden a la misma "
        "pregunta por caminos distintos, y calcular las dos deja ver cuanto "
        "pesa en este cruce lo que Laushey no mira. HEC-14 compara seis "
        "relaciones de apron y no recomienda las dos que solo miran la "
        "velocidad, porque no consideran el tirante del receptor. La que "
        "retiene es empirica, la recomienda para conductos circulares y "
        "pide limitar el tirante de aguas abajo a entre 0.4 y 1.0 "
        "diametros."),
    verbo=Verbo.RECOMIENDA,
    citas=("HEC14.10.2#EC_10_4", "HEC14.10.2#TW", "HEC14.10.2#TW_ALTO",
           "HEC14.10.2#EC_10_5", "HEC14.1#T1_1_APRON",
           "HDS5_3ED.5.3.2#APRON", "HEC14.D#SOLO_VELOCIDAD"),
    que_pasa_si_no_se_hace=(
        "La proteccion quedaria dimensionada solo por velocidad, sin la "
        "ecuacion de la fuente a la que el propio HDS-5 remite el apron."),
)

APRON_GEOMETRIA = _fundamento(
    id="F6.APRON_GEOMETRIA",
    fase=F6,
    que_paso=("Clase de enrocado, longitud, profundidad y ancho del apron "
              "por la Tabla 10.1 de HEC-14"),
    por_que=(
        "Una piedra del tamaño justo colocada en un tramo corto solo corre "
        "la erosion aguas abajo: lo que protege es el apron entero, con su "
        "longitud, su espesor y su ancho. HEC-14 no da una formula para "
        "ellos sino un ejemplo de estandar de proyecto --la tabla de la "
        "Federal Lands Highway Division--, que liga la longitud a la altura "
        "del conducto y el espesor al tamaño de la piedra, y abre el apron "
        "en planta a razon de 1:3. Es con lo que se comparan la longitud y "
        "el espesor que el proyecto adopta, que no salen de ninguna norma "
        "peruana: la Lámina Nº 05 del Manual dibuja el enrocado de salida "
        "sin una sola dimension. Cuando la piedra que la ecuacion pide no "
        "cabe en la tabla, es lectura del proyecto que un apron de catalogo "
        "deja de ser la medida: la tabla es un ejemplo y no dice que hacer "
        "mas alla de su ultima clase. El HDS-5 remite a HEC-14 las medidas "
        "de proteccion para los problemas de erosion mas serios, y el "
        "Manual ofrece reducir la velocidad con un aliviadero escalonado "
        "(su Lámina Nº 04)."),
    verbo=Verbo.RECOMIENDA,
    citas=("HEC14.10.2#T10_1", "HEC14.10.2#ANCHO", "MC_HHD.LAMINA_05",
           "MC_HHD.4.1.1.3.7c#ALIVIADERO", "MC_HHD.LAMINA_04",
           "HDS5_3ED.5.3.2#APRON"),
    que_pasa_si_no_se_hace=(
        "La longitud y el espesor adoptados no tendrian contra que "
        "compararse, y un apron corto o delgado pasaria sin aviso."),
)

GEOMETRIA_ADOPTADA = _fundamento(
    id="F6.GEOMETRIA_ADOPTADA",
    fase=F6,
    que_paso=("Espesor y longitud de la proteccion de salida que el "
              "proyecto adopta"),
    por_que=(
        "El Manual entrega el tamaño de la piedra y pide que el "
        "revestimiento se extienda hasta donde la socavacion local deje de "
        "incidir, pero no dice cuanto mide esa extension ni que espesor "
        "lleva la capa. Sin esas dos medidas no hay pieza que construir ni "
        "que presupuestar, y por eso el proyecto las adopta y las declara: "
        "el espesor como multiplo del d50 y la longitud como una distancia "
        "aguas abajo de la salida. Son adopciones con ventana, no valores "
        "de norma, y se imprimen junto a lo que HEC-14 daria para el mismo "
        "cruce. Cual rige --lo adoptado a secas o la envolvente de lo "
        "adoptado y de HEC-14, que alcanza tambien al tamaño de la piedra-- "
        "lo decide una regla declarada, y el paso que la aplica lo dice."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.7c#REVESTIMIENTOS", "MC_HHD.4.1.1.3.7c",
           "HEC14.10.2#T10_1", "HEC14.10.2#PROFUNDIDAD",
           "HEC14.10.2#EC_10_4"),
    que_pasa_si_no_se_hace=(
        "La proteccion seria un tamaño de piedra sin espesor ni longitud: "
        "un numero que no se puede construir."),
)

FILTRO_ENROCADO = _fundamento(
    id="F6.FILTRO",
    fase=F6,
    que_paso=("Filtro entre el enrocado y el suelo: requisitos del "
              "geotextil de control permanente de erosion"),
    por_que=(
        "El enrocado deja pasar el agua entre las piedras, y esa agua "
        "arrastra los finos del suelo que tiene debajo: sin una capa que "
        "los retenga, el lecho se va por los huecos y la piedra se hunde "
        "aunque su tamaño sea el correcto. La lamina tipica del Manual "
        "dibuja el enrocado de salida con su filtro y su cama de apoyo, y "
        "HEC-14 pide la manta de filtro bajo el apron. Cuando el filtro es "
        "un geotextil, las especificaciones generales fijan lo que tiene "
        "que cumplir, y lo fijan por el contenido de finos del suelo: "
        "cuanto mas fino el suelo, menor la abertura admitida."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.LAMINA_05", "HEC14.10.2#FILTRO", "EG2013.511.08#EROSION",
           "EG2013.511.08#T511_06", "EG2013.511.08#NOTA_5A",
           "EG2013.511.05#T511_02_NOTA_5"),
    que_pasa_si_no_se_hace=(
        "El enrocado se socava por debajo y falla, que es la forma mas "
        "comun de perder una proteccion bien dimensionada."),
)

PROTECCION_ENTRADA = _fundamento(
    id="F6.ENTRADA",
    fase=F6,
    que_paso=("Proteccion de la entrada: velocidad en la boca y "
              "revestimiento del cauce y del talud"),
    por_que=(
        "En la entrada el agua se acelera para caber en el conducto. Esa "
        "contraccion forma vortices y zonas de alta velocidad que atacan el "
        "talud del terraplen junto a la boca, y a menudo abre una hoya "
        "delante del piso del conducto. El Manual recomienda proteger el "
        "cauce cuando la velocidad en la entrada es alta, y nombra el "
        "emboquillado de piedra y el enchapado de roca; el HDS-5 enumera "
        "lo que protege esa zona: el revestimiento del talud y del cauce, "
        "el cabezal, los aleros y el dentellon. Ninguna de las dos fuentes "
        "da dimensiones para la entrada, de modo que el paso publica la "
        "velocidad con que el agua entra y lo que el proyecto adopta como "
        "revestimiento, y deja la geometria al cabezal."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.7c#PROTECCION", "MC_HHD.4.1.1.3.7c#REVESTIMIENTOS",
           "HDS5_3ED.5.3.1#ENTRADA", "HDS5_3ED.3.1.3#CRITICO_EN_LA_ENTRADA",
           "MC_HHD.LAMINA_02"),
    que_pasa_si_no_se_hace=(
        "La obra quedaria protegida solo aguas abajo, y la erosion del "
        "talud junto a la boca es la que descalza el cabezal de entrada."),
)

SOCAVACION_SALIDA = _fundamento(
    id="F6.SOCAVACION",
    fase=F6,
    que_paso=("Hoya de socavacion local a la salida por HEC-14, Cap. 5: "
              "profundidad, ancho y longitud"),
    por_que=(
        "Si la salida no se protege, o si la proteccion falla, el chorro "
        "abre una hoya en el lecho al pie del conducto. Su profundidad es "
        "lo que decide hasta donde tiene que bajar el cabezal de salida "
        "para no quedar descalzado, y su longitud hasta donde alcanza el "
        "daño. HEC-14 la estima con ecuaciones empiricas ajustadas sobre "
        "ensayos que buscaban la hoya maxima: dependen del caudal, del "
        "radio hidraulico del conducto, de la granulometria o de la "
        "resistencia del suelo del lecho, de cuanto dura el caudal pico, de "
        "la pendiente y de la altura de la salida sobre el lecho. Son una "
        "estimacion del peor caso de la socavacion LOCAL: no incluyen la "
        "degradacion general del cauce."),
    verbo=Verbo.RECOMIENDA,
    citas=("HEC14.5.1#EC_5_1", "HEC14.5#PEOR_CASO", "HEC14.5.1.1#T5_1",
           "HEC14.5.1.4#T5_2", "HEC14.5.1.5#T5_3", "HEC14.5.1.2#T30",
           "HEC14.5.1.2#NO_BAJO_30", "HEC14.5.1.2#DOS_TERCIOS",
           "HEC14.5.2#EC_5_2", "HEC14.5.2#RANGO_IP", "HEC14.5.2#EC_5_4"),
    que_pasa_si_no_se_hace=(
        "El desplante del cabezal de salida se fijaria sin saber cuanto "
        "puede bajar el lecho a su pie."),
)

SOCAVACION_PARA_DESPLANTE = _fundamento(
    id="F6.SOCAVACION_DESPLANTE",
    fase=F6,
    que_paso=("Profundidad de socavacion que se entrega al desplante del "
              "cabezal de salida"),
    por_que=(
        "El cabezal de salida corre la hoya aguas abajo pero no la "
        "reduce, y por eso HEC-14 pide que baje hasta la profundidad "
        "maxima de socavacion. Esa profundidad puede venir de dos sitios: "
        "de un estudio del cauce, que conoce el lecho y su historia, o de "
        "la estimacion de este programa. Cuando el estudio existe manda el "
        "estudio, y la estimacion se imprime al lado para que se vea cuanto "
        "difieren."),
    verbo=Verbo.RECOMIENDA,
    citas=("HEC14.5.1.3#CABEZAL", "HDS5_3ED.5.3.2#APRON", "HEC14.10.1#HS"),
    que_pasa_si_no_se_hace=(
        "El cabezal se cimentaria a la profundidad minima constructiva, "
        "sin relacion con lo que el lecho puede perder."),
)


# ===========================================================================
# Fase 7 - Compatibilidad geometrica
# ===========================================================================

RELLENO = _fundamento(
    id="F7.RELLENO",
    fase=F7,
    que_paso="Altura minima de relleno sobre la clave del conducto",
    por_que=(
        "La cobertura no es un margen constructivo: es la que reparte la carga "
        "de rueda antes de que llegue al conducto. Con poco relleno la "
        "sobrecarga de trafico llega concentrada sobre la clave, que es donde "
        "el tubo es mas debil, y ademas el conducto queda dentro del espesor "
        "que la construccion de la via tiene que compactar por encima. Por eso "
        "el minimo se mide desde la clave EXTERIOR y depende del diametro, no "
        "es una cifra unica."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.6.6.3#COBERTURA", "EG2013.508.07#RELLENO_MIN"),
    que_pasa_si_no_se_hace=(
        "El conducto quedaria bajo la carga concentrada del trafico y bajo el "
        "equipo de compactacion, que es el momento en que mas conductos se "
        "rompen: durante la construccion, no en servicio."),
)


# ===========================================================================
# Fase 8 - Durabilidad del conducto
# ===========================================================================

RECUBRIMIENTO = _fundamento(
    id="F8.RECUBRIMIENTO",
    fase=F8,
    que_paso=("Recubrimiento del refuerzo, por la regla del mayor entre "
              "E.060 y AASHTO"),
    por_que=(
        "El recubrimiento es lo unico que separa el acero del ambiente. En un "
        "conducto enterrado, vaciado contra el suelo y con agua corriendo por "
        "dentro, es lo que decide si la obra dura su vida util o se pierde por "
        "corrosion del refuerzo. Dos cuerpos normativos exigen recubrimiento "
        "para la misma pieza y no dicen lo mismo; el proyecto adopta el mayor "
        "de los dos porque cumplir el menor deja el otro incumplido."),
    verbo=Verbo.OBLIGA,
    citas=("E060.7.7.1", "AASHTO_LRFD_9.T5.10.1-1"),
    que_pasa_si_no_se_hace=(
        "Se aplicaria el recubrimiento de una sola norma sin declarar que la "
        "otra pedia mas, que es la forma habitual de incumplir dos normas "
        "citando una."),
)


# ===========================================================================
# Fase 10 - Espaciamiento de alivio
# ===========================================================================

CUNETA = _fundamento(
    id="F10.CUNETA",
    fase=F10,
    que_paso=("Longitud maxima de recorrido de la cuneta, que fija el "
              "espaciamiento de las alcantarillas de alivio"),
    por_que=(
        "Una cuneta acumula caudal a lo largo de su recorrido: cuanto mas "
        "larga, mas agua lleva en su extremo y mayor seccion necesita. El "
        "Manual acota el recorrido en vez de acotar la seccion, y con eso "
        "convierte el problema de capacidad en un problema de ESPACIAMIENTO: "
        "cada cuanto hay que aliviar. Por eso el numero de alcantarillas de "
        "alivio de un tramo no sale de un caudal, sale de esta longitud."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.2.1d",),
    que_pasa_si_no_se_hace=(
        "Las cunetas se disenarian por capacidad, con secciones crecientes, "
        "en vez de aliviarse; y el proyecto no tendria como decidir cuantas "
        "alcantarillas de alivio lleva un tramo."),
)


# ===========================================================================
# --- T-1 --- Fase 1-bis - Hidrologia: el caudal de diseño (MH_hidrologia)
# ===========================================================================
# Los nueve pasos de la memoria hidrologica de un punto, en el orden en que
# se emiten: la serie, el ajuste de frecuencia, la prueba de bondad, el
# contraste del tratamiento FEN, el tiempo de concentracion, la intensidad, el
# coeficiente C, el caudal por el metodo racional y el caudal especifico. El
# ultimo se emite tambien cuando el caudal entra DECLARADO por `Q_m3s`.
FH = "Fase 1-bis - Hidrologia: caudal de diseño"

H_SERIE = _fundamento(
    id="FH.SERIE",
    fase=FH,
    que_paso=("Serie de precipitacion maxima en 24 horas de la estacion: "
              "longitud de registro, años FEN que contiene y como se tratan"),
    por_que=(
        "El caudal de diseño sale de una extrapolacion estadistica, y esa "
        "extrapolacion vale lo que valga la serie. En el norte del Peru la "
        "serie de maximas anuales no es de una sola poblacion: los años del "
        "fenomeno El Niño traen valores que no pertenecen a la misma "
        "poblacion que los años neutros. El Manual manda las dos cosas a la "
        "vez --que la serie los incluya, y que se evaluen para no "
        "sobredimensionar-- y no dice como: por eso que años FEN trae la "
        "serie es un HECHO que declara el archivo de la estacion, y como se "
        "tratan es una DECISION del proyectista (criterio "
        "'homogeneidad_serie_fen'), y las dos se imprimen antes que ningun "
        "numero."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.3.4#FEN",            # EXIGENCIA -> sostiene OBLIGA
           "MC_HHD.3.4#REGISTRO",       # RECOMENDACION (los 25 años)
           "MC_HHD.3.12.5#PIURA"),      # EXIGENCIA (tratamiento especial)
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta T-1 (INF-5.1.1, INF-3.1.4): el caudal entraba "
        "ya calculado y nada obligaba a decir con que serie ni que se hizo "
        "con 1983, 1998 y 2017. Un ajuste dominado por dos o tres valores "
        "extraordinarios, o uno que los dejo fuera, dan caudales muy "
        "distintos, y sin la declaracion no se sabe cual de los dos se esta "
        "leyendo."),
)

H_AJUSTE = _fundamento(
    id="FH.AJUSTE",
    fase=FH,
    que_paso=("Precipitacion maxima en 24 horas para el periodo de retorno, "
              "por ajuste de una distribucion de probabilidad a la serie"),
    por_que=(
        "El periodo de retorno de la Fase 2 (71 o 35 años) suele ser mayor "
        "que la longitud del registro, de modo que la precipitacion de "
        "diseño no se lee de la serie: se extrapola con un modelo de "
        "probabilidad ajustado a ella. El Manual recomienda ocho "
        "distribuciones y solo de tres escribe como se estiman los "
        "parametros (Normal, Log Normal de 2 parametros y Gumbel); el "
        "programa ajusta esas tres con las expresiones que el Manual "
        "imprime y no evalua las otras cinco, porque elegirles un estimador "
        "seria adoptar un procedimiento sin fuente. Una distribucion puede "
        "pasar la prueba de bondad y aun asi dejar la lluvia de diseño por "
        "debajo de un valor que la serie ya registro con un periodo de "
        "retorno menor que el de diseño: ocurre cuando el ajuste describe "
        "bien los años corrientes y no los extremos, y por eso el paso "
        "contrasta la lluvia de diseño contra el maximo observado y lo "
        "avisa."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.3.7.1",              # RECOMENDACION -> sostiene RECOMIENDA
           "MC_HHD.3.7.1.1", "MC_HHD.3.7.1.2", "MC_HHD.3.7.1.7",
           "MC_HHD.3.7.2b"),            # la ec. (13), del periodo empirico
    que_pasa_si_no_se_hace=(
        "La precipitacion de diseño seria el maximo observado, o un numero "
        "traido de otro estudio: en los dos casos sin periodo de retorno "
        "asociado, que es justo lo que la Tabla Nº 02 fija."),
)

H_KS = _fundamento(
    id="FH.KS",
    fase=FH,
    que_paso=("Prueba de bondad de ajuste de Kolmogorov-Smirnov: D = max "
              "|Fo(xm) − F(xm)| contra el valor critico d de la Tabla Nº 03"),
    por_que=(
        "Ajustar una distribucion siempre da parametros; lo que no da es la "
        "garantia de que la serie se parezca a ella. La prueba compara la "
        "probabilidad empirica de cada dato con la del modelo y se queda con "
        "la mayor diferencia: si no baja del valor critico, la hipotesis de "
        "que la serie sale de esa distribucion se rechaza y la extrapolacion "
        "no se sostiene. La misma prueba permite elegir, entre las "
        "distribuciones ajustadas, la de menor diferencia."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.3.7.2b",             # DEFINICION -> sostiene DEFINE
           "MC_HHD.3.7.2b#T03", "MC_HHD.3.7.2b#ELIGE"),
    que_pasa_si_no_se_hace=(
        "Se extrapolaria a 71 años con un modelo que la propia serie "
        "desmiente, y el caudal llevaria una precision que no tiene."),
)

H_FEN = _fundamento(
    id="FH.FEN",
    fase=FH,
    que_paso=("Contraste del tratamiento de los años FEN: la lluvia de "
              "diseño adoptada frente a la de la serie completa y la de la "
              "serie sin los años FEN"),
    por_que=(
        "El Manual manda que la serie incluya los años del fenomeno El Niño "
        "y dice que en Piura y Tumbes hace falta un tratamiento especial; "
        "la hoja de ruta lo concreta: reportar el ajuste con esos años y "
        "sin ellos, y adoptar el mas conservador. Este paso hace las dos "
        "cosas que se pueden comprobar: imprime la lluvia de diseño de las "
        "dos series y juzga si la adoptada es la mayor. Declarar el "
        "tratamiento sin los años FEN sigue siendo posible --la decision es "
        "del proyectista--, pero cuando da menos lluvia que la serie "
        "completa no cumple la regla y el calculo hidrologico del punto se "
        "detiene; el paso se imprime cuando la lluvia adoptada es la mas "
        "conservadora de las dos, o igual."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.3.4#FEN",                # EXIGENCIA -> sostiene OBLIGA
           "MC_HHD.3.12.5#PIURA"),          # EXIGENCIA
    que_pasa_si_no_se_hace=(
        "Quitar de la serie los tres años que mas llovio es la forma mas "
        "facil de que una distribucion ajuste bien, y tambien la de bajar la "
        "lluvia de diseño a la mitad sin que la memoria lo delate."),
)

H_TC = _fundamento(
    id="FH.TC",
    fase=FH,
    que_paso=("Tiempo de concentracion de la cuenca, por el metodo declarado "
              "en el CSV de cuencas"),
    por_que=(
        "El metodo racional supone que el caudal pico llega cuando toda la "
        "cuenca aporta a la vez, y eso ocurre cuando la lluvia dura lo que "
        "tarda en llegar el agua desde el punto mas alejado: por eso la "
        "duracion de la lluvia de diseño es el tiempo de concentracion, y de "
        "el depende la intensidad. Las formulas son empiricas y cada una "
        "salio de un tipo de cuenca; fuera de esa poblacion la formula sigue "
        "dando un numero, que es lo peligroso. El paso compara la cuenca "
        "contra la poblacion que la fuente describe para el metodo, y que "
        "se hace fuera de ella lo decide un criterio declarado: no evaluar, "
        "o evaluar con aviso."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.3.9#T05",            # DEFINICION -> sostiene DEFINE
           "MC_HHD.3.9#T05_KIRPICH", "MC_HHD.3.9#T05_CALIFORNIA",
           "MC_HHD.3.9#T05_FAA", "MC_HHD.3.9#T05_SCS",
           "MC_HHD.3.12.2.1#TC"),
    que_pasa_si_no_se_hace=(
        "La intensidad se tomaria para una duracion arbitraria. Con la "
        "relacion de Dick y Peschke la intensidad varia con la duracion "
        "elevada a −0.75: a mitad de duracion, un 68 % mas de intensidad y "
        "de caudal."),
)

H_INTENSIDAD = _fundamento(
    id="FH.INTENSIDAD",
    fase=FH,
    que_paso=("Intensidad de la lluvia de diseño para una duracion igual al "
              "tiempo de concentracion, desde la precipitacion maxima en 24 "
              "horas"),
    por_que=(
        "La estacion entrega lluvia acumulada en 24 horas, y el metodo "
        "racional pide la intensidad de una lluvia que dura minutos. Sin "
        "registros pluviograficos esa intensidad no se mide: se estima con "
        "una relacion entre la precipitacion de 24 horas y la de una "
        "duracion menor. El Manual ofrece dos --la de Dick y Peschke, para "
        "cualquier duracion hasta 24 horas, y los coeficientes de duracion "
        "de su Tabla Nº 04, desde una hora--, y las dos son permisos, no "
        "mandatos: cual se usa es un criterio declarado. Para duraciones de "
        "uno o dos minutos esas relaciones son una extrapolacion que da "
        "intensidades irreales, y el Manual no fija una duracion minima: "
        "la cubre un criterio con fuente tecnica, y cuando el tiempo de "
        "concentracion queda por debajo la lluvia de diseño dura ese "
        "minimo."),
    verbo=Verbo.PERMITE,
    citas=("MC_HHD.3.8.1#DICK_PESCHKE",     # PERMISO -> sostiene PERMITE
           "MC_HHD.3.8.1#T04", "MC_HHD.3.8.1#DURACION",
           "WSDOT_HM.2-6.3#TC_MINIMO"),     # [C]: la duracion minima
    que_pasa_si_no_se_hace=(
        "No hay intensidad que meter en la ecuacion (28), o se mete la "
        "media de 24 horas, que para una cuenca de minutos subestima el "
        "caudal en mas de un orden de magnitud."),
)

H_C = _fundamento(
    id="FH.C",
    fase=FH,
    que_paso=("Coeficiente de escorrentia C de la Tabla Nº 08, por cobertura "
              "vegetal, tipo de suelo y pendiente del terreno"),
    por_que=(
        "El metodo racional mete todas las perdidas --infiltracion, "
        "intercepcion, almacenamiento-- en un solo numero, y por eso ese "
        "numero decide el caudal en la misma proporcion que la intensidad. "
        "El Manual lo tabula por tres caracteristicas de la cuenca y manda "
        "establecerlo de acuerdo con ellas: el programa no acepta un "
        "coeficiente tecleado, lee la celda que corresponde a la cobertura y "
        "el suelo que el estudio declara y a la pendiente del terreno de la "
        "cuenca. La tabla del Manual no tiene fila para una superficie "
        "pavimentada ni para un talud: para esas cuatro superficies de la "
        "plataforma el coeficiente sale de una fuente tecnica, con su "
        "incremento por periodo de retorno, y se dice que no es norma."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.3.12.2#T08",             # EXIGENCIA -> sostiene OBLIGA
           "WSDOT_HM.2-6.2#T2-2", "WSDOT_HM.2-6.2#FRECUENCIA"),   # [C]
    que_pasa_si_no_se_hace=(
        "El coeficiente seria un numero suelto sin fila que lo respalde: "
        "entre el menor y el mayor de la tabla (0.05 y 0.80) el caudal "
        "cambia dieciseis veces."),
)

H_RACIONAL = _fundamento(
    id="FH.RACIONAL",
    fase=FH,
    que_paso="Caudal de diseño por el metodo racional, Q = 0.278 · C · I · A",
    por_que=(
        "Es el paso que convierte la lluvia de diseño en el caudal con que "
        "se dimensiona el conducto: intensidad por area da un caudal de "
        "lluvia, el coeficiente C deja la parte que escurre y el 0.278 "
        "pasa de mm/h por km² a m³/s. El metodo supone lluvia uniforme "
        "sobre toda la cuenca durante el tiempo de concentracion, y eso solo "
        "es razonable en cuencas chicas: el Manual lo situa por debajo de "
        "10 km², y por encima el programa no lo evalua. Para una cuneta es "
        "la misma expresion, escrita C·I·A/3.6. Cuando el tiempo de "
        "concentracion sale de la formula de Temez, que es una pieza del "
        "metodo racional modificado, el caudal lleva ademas el coeficiente "
        "de uniformidad K de ese metodo: usar su tiempo de concentracion "
        "sin su K es tomar medio metodo, y K es siempre mayor que 1."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.3.12.2",                 # DEFINICION -> sostiene DEFINE
           "MC_HHD.3.12.2#AREA", "MC_HHD.4.1.2.1b", "MC_HHD.3.12.2.1#K"),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta T-1 (INF-3.1.5): el caudal entraba ya "
        "calculado por una columna del CSV y la memoria no podia decir de "
        "que cuenca, de que lluvia ni con que coeficiente salio."),
)

H_Q_ESPECIFICO = _fundamento(
    id="FH.Q_ESPECIFICO",
    fase=FH,
    que_paso=("Caudal especifico Q/A del caudal de diseño, como contraste de "
              "plausibilidad"),
    por_que=(
        "El caudal de diseño es el numero del que cuelga toda la obra y es "
        "tambien el que menos se puede comprobar desde el conducto: un "
        "caudal diez veces menor que el real pasa todas las verificaciones "
        "hidraulicas. El cociente Q/A lo pone en una escala comparable "
        "entre cuencas, y dividido entre 0.278 dice a que lamina de "
        "escorrentia C·I equivale, que se puede contrastar a simple vista "
        "con la lluvia de la zona. El Manual define la avenida de diseño y "
        "no le pone umbral: por eso este paso no juzga, informa."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.3.13",                   # DEFINICION -> sostiene DEFINE
           "MC_HHD.3.12.2"),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta T-1 (INF-3.1.6): del caudal declarado solo "
        "se comprobaba que fuera positivo y finito, y 850 ha con "
        "1.167 m³/s pasaban sin que nada dijera que eso es medio milimetro "
        "por hora de escorrentia."),
)


# ===========================================================================
# Lo que NO tiene fundamento, y por que. Censo, no omision.
# ===========================================================================
# (id del paso, por que no puede tener `Fundamento` hoy, que haria falta)
SIN_FUNDAMENTO: Tuple[Tuple[str, str, str], ...] = (
    ("F5.V4b",
     "El rango HW/D 1.0-1.5 no lo prescribe el HDS-5: DESCRIBE lo que imponen "
     "las agencias viales de EE. UU., y el MTC no fija ninguno "
     "(NOR-HDS-02, y el conflicto vinculante n.1 de la §6 del plan v12). Un "
     "`Fundamento` con cita convertiria en exigencia lo que es adopcion del "
     "proyectista.",
     "Nada que transcribir: la decision pendiente es de que naturaleza es el "
     "umbral, y hasta que se resuelva V4b se imprime como adopcion [A]."),
    ("F5.V5",
     "El remanso dentro del derecho de via tiene desde EXT-6 su requisito "
     "JURIDICO citado --- DG-2018 304.07.01 y 304.07.02 con la Tabla 304.09 y "
     "el incremento de 5.00 m del borde de las obras de drenaje, presentes y "
     "verificados --- y sigue sin tener paso que fundar, por dos razones que "
     "no son la misma: el 304.07 acota el ANCHO de la faja y no enuncia "
     "condicion hidraulica alguna (no dice cuanto puede remansar la obra ni "
     "como se calcula la extension del embalse: ese metodo es [A] del "
     "proyectista, 'remanso_derecho_via'), y la Ley 29338, que gobierna la "
     "faja marginal, sigue AUSENTE. Un `Fundamento` con las citas del "
     "DG-2018 convertiria un piso de ancho en una verificacion hidraulica "
     "que la fuente no escribe.",
     "El metodo de perfil de remanso declarado por el proyectista, el dato "
     "de sitio `ancho_derecho_via_m` (hoy no llega por ninguna via) y la "
     "clase de via del corredor para elegir fila en la Tabla 304.09; con los "
     "tres, el paso existe y su fundamento cuelga de DG2018.304.07.02. La "
     "faja marginal exige ademas la Ley 29338 en `normas/`."),
    ("F5.V6",
     "El material solido de arrastre lo trata el num. 4.1.1.3.7 a), que esta "
     "en el registro, pero lo que el proyecto ejecuta no es un calculo: es "
     "una constatacion declarativa sin magnitud ni umbral. No hay paso que "
     "fundar.",
     "Cuando V6 pase a evaluar un diametro minimo por zona, su fundamento "
     "cuelga de `MC_HHD.4.1.1.3.7a`, que ya esta transcrita y verificada."),
    ("F5.V8",
     "El evento extremo se verifica contra un TR adoptado por el proyecto "
     "('TR_evento_extremo'), no contra un numeral: la Tabla N 02 no tabula "
     "evento extremo para alcantarillas.",
     "Nada que transcribir mientras el TR de evento extremo siga siendo una "
     "adopcion [A]; el fundamento seria del criterio, no de la norma."),
    ("F5.V9",
     "La disponibilidad de diametro sale de un CATALOGO de fabricacion, no de "
     "una norma. `NOR-PRO-01` y `NOR-PRO-02` retiraron precisamente la "
     "atribucion de los topes a AASHTO M170 y ASTM A760, que tabulan mas. El "
     "del HDPE si coincide con el techo de la serie de AASHTO M 294-11 "
     "(N2, cita AASHTO_M294_TRAD.7.2.1), pero sobre una traduccion no "
     "oficial sin firma, y el paso sigue descartando por catalogo para los "
     "tres materiales.",
     "Nada: un catalogo no tiene numeral y no puede sostener un fundamento. "
     "Es lo que `DeCatalogo` existe para rotular. Un fundamento del HDPE "
     "sobre M 294-11 exigiria el original firmado y un paso que descartara "
     "por norma, que hoy no existe."),
    ("F9.CABEZAL",
     "La cadena sismica y la estabilidad del cabezal tienen sus citas en el "
     "registro (AASHTO 11.6.5.1, A11.3.1, 3.10.3.1), pero la Fase 9 esta "
     "DIFERIDA al expediente y no emite paso en la corrida de perfil: un "
     "fundamento sin paso que lo imprima no se puede comprobar contra la "
     "memoria generada, que es la unica prueba que este proyecto acepta "
     "(NOR-MEM-01 se cerro justo por no tenerla).",
     "Emitir `PasoDeMemoria` desde M9 en la corrida de expediente; las citas "
     "ya estan."),
)


# ===========================================================================
# El cajon: los cuatro `Fundamento` que C2 desbloquea (§15.7)
# ===========================================================================
# LOS CUATRO ESTABAN REDACTADOS EN §15.7 DE docs/ruta_familia_c.md Y NO SE
# PODIAN CONSTRUIR: sus citas no existian. C2 las transcribe y por eso los
# escribe aqui -- no es adelantar trabajo de C3 ni de C5, es que el registro
# no admite la alternativa: T4 rechaza una cita que nadie referencia, de modo
# que transcribir `MC_HHD.4.1.1.3.7d`, `MC_HHD.LAMINA_03` y
# `HDS5_3ED.A.3#FORMAS` sin su consumidor deja el registro en rojo.
#
# LOS OTROS CUATRO DE §15.7 NO SE ESCRIBEN AQUI -- F4.SECCION, F4.YC_RECT,
# F3.SECCION_CANAL y F4.N_CAJON --: sus citas ya existian antes de C2, de modo
# que no crean ninguna huerfana, y su sitio es la sesion que escribe el paso
# que los emite (C4 y C5). Escribirlos ahora seria fundar pasos que todavia no
# existen.
#
# EL `verbo` DE CADA UNO ESTA ELEGIDO CONTRA EL `caracter` DE SUS CITAS, que
# es lo que T11 comprueba, y el reparto NO es obvio en dos de ellos: ver la
# nota de F4.FORMA_HDS5 y la de F3.TIPO_MARCO.

TIPO_MARCO = _fundamento(
    id="F3.TIPO_MARCO",
    fase=F3,
    que_paso=("Tipo de estructura del cruce: alcantarilla tipo marco de "
              "concreto de seccion rectangular"),
    por_que=(
        "El marco de concreto no es una importacion ni una excepcion en este "
        "Manual: lo nombra el PRIMERO entre los tipos comunmente utilizados "
        "en carreteras del pais, cuenta la seccion rectangular y la cuadrada "
        "entre las mas usuales, PERMITE expresamente ubicarlo a la cota que "
        "se requiera -- que es justo lo que un cruce a nivel de canal "
        "necesita -- y RECOMIENDA emplearlo con suelos de fundacion de mala "
        "calidad. Ademas lo DIBUJA para este caso exacto: la Lamina Nº 03 "
        "trae una figura de marco de concreto en cruce de canal de riego. La "
        "asignacion del tipo a la Familia C la hace la Sec. 2.3 de la hoja "
        "de ruta; lo que estas citas aportan es que esa asignacion tiene "
        "respaldo en la fuente primaria y no solo en la hoja."),
    # RECOMIENDA y no DEFINE: de las cuatro citas, la que sostiene el verbo es
    # `#MARCO`, la unica RECOMENDACION. Las otras tres describen el tipo
    # (DEFINICION), lo permiten a cualquier nivel (PERMISO) y lo dibujan
    # (DEFINICION): ninguna de las tres RECOMIENDA nada, y ninguna OBLIGA.
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.4a#TIPOS",      # definicion
           "MC_HHD.4.1.1.3.4a#NIVELES",    # permiso
           "MC_HHD.4.1.1.3.4a#MARCO",      # recomendacion -> sostiene el verbo
           "MC_HHD.LAMINA_03"),            # definicion
    que_pasa_si_no_se_hace=(
        "El tipo de estructura de la Familia C se apoya solo en la Sec. 2.3 "
        "de la hoja de ruta, que no es fuente primaria, y la memoria no "
        "puede citar ningun numeral para la decision que gobierna todo lo "
        "demas del punto."),
)

MANTENIMIENTO = _fundamento(
    id="F3.MANTENIMIENTO",
    fase=F3,
    que_paso=("Cota inferior de la progresion de secciones: dimension "
              "interior que permite mantener y limpiar el conducto"),
    por_que=(
        "Levantado el piso de 0.90 m, la seccion del cajon NO queda sin cota "
        "inferior normativa. El num. 4.1.1.3.7 d) exige, sin distinguir "
        "forma alguna, que las dimensiones permitan efectuar el "
        "mantenimiento y la limpieza EN SU INTERIOR de manera factible. Es "
        "una exigencia SIN NUMERO: obliga a que exista un minimo y deja al "
        "proyecto decir cual. Esa es exactamente la forma de un vacio "
        "declarable -- la norma pide el requisito y no da la cifra --, y por "
        "eso 'secciones_cajon_normalizadas' es [A] con vacio verificado y no "
        "una eleccion libre."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.7d",),   # exigencia -> sostiene OBLIGA
    que_pasa_si_no_se_hace=(
        "La progresion de secciones del cajon se lee como una decision "
        "puramente economica o hidraulica, y el minimo se fija por el caudal. "
        "Es como se llega a un cruce que pasa el agua y no se puede limpiar, "
        "que es el mismo fallo que el piso de 0.90 m evita en las Familias A "
        "y B por otra via."),
)

CELDAS = _fundamento(
    id="F3.CELDAS",
    fase=F3,
    que_paso="Numero de celdas del cajon: una sola, o multicelda",
    por_que=(
        "El Manual toma partido y hay que citarlo donde se decide: ante "
        "capacidad de arrastre del curso -- palizada, troncos, material de "
        "cauce -- RECOMIENDA usar obras con mayor seccion transversal libre, "
        "SIN SUBDIVISIONES, porque cada tabique es un punto donde la palizada "
        "se traba. La multicelda no esta prohibida; lo que el numeral hace es "
        "invertir la carga de la prueba: quien la adopte tiene que decir por "
        "que, y no al reves. Por eso el numero de celdas es un criterio "
        "declarado y no un supuesto del codigo."),
    verbo=Verbo.RECOMIENDA,
    # DOS CITAS DESDE EXT-2, y cada una sostiene una mitad distinta del
    # paso: la del Manual sostiene la ADOPCION de N (recomendacion de seccion
    # unica ante arrastre); la de HDS-5 num. 5.4.3 sostiene el REPARTO Q/N
    # que M4 hace con ese N (regla vinculante #3), que hasta EXT-2 se
    # afirmaba sin cita (EXT-M-03). El verbo lo sigue sosteniendo la primera.
    citas=("MC_HHD.4.1.1.3.4a#MULTIPLES",   # recomendacion
           "HDS5_3ED.5.4.3#REPARTO"),       # aproximacion: Q/N por barril
    que_pasa_si_no_se_hace=(
        "V6 sigue siendo trivialmente verdadera porque MD no sabe hacer "
        "multibarril -- que es una propiedad del PROGRAMA, no del diseno --, "
        "y el dia que sepa, la verificacion se vuelve falsa en silencio. Es "
        "la trampa que la regla vinculante #10 anticipa. Y si el reparto no "
        "se imprime, la memoria adopta N y nunca dice con que caudal quedo "
        "cada barril: Q = 9.0 impreso junto a un tirante que solo transporta "
        "3.0 (EXT-M-03)."),
)

FORMA_HDS5 = _fundamento(
    id="F4.FORMA_HDS5",
    fase=F4,
    que_paso=("Forma de la ecuacion de control de entrada del HDS-5 que "
              "aplica a esta seccion, y por que"),
    por_que=(
        "El HDS-5 no tiene UNA ecuacion de control de entrada no sumergido: "
        "tiene DOS formas, y cual se usa no lo elige el proyectista, lo fija "
        "la carta de la Tabla A.1 a la que pertenece la seccion. La Forma 1 "
        "arranca del tirante critico y corrige por pendiente; la Forma 2 es "
        "un ajuste directo sobre el caudal adimensional y NO lleva el termino "
        "Ks*S. La diferencia no es de precision: son dos regresiones "
        "distintas sobre dos conjuntos de ensayos, y sus constantes K y M "
        "estan ajustadas cada una a SU forma. Por eso la memoria imprime que "
        "forma se uso: un lector que vea K y M sin saber en que ecuacion "
        "entraron no puede rehacer el numero."),
    # DEFINE y no OBLIGA, aunque `#FORMAS` sea una EXIGENCIA. Lo que el paso
    # hace es ELEGIR una ecuacion, y el HDS-5 la DEFINE; la exigencia de no
    # cruzar coeficientes es la RESTRICCION sobre esa eleccion, no el motivo
    # del paso. Escribir OBLIGA pasaria T11 y diria algo falso (§15.7).
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.A.2",          # definicion -> sostiene DEFINE
           "HDS5_3ED.TA.1",         # definicion
           "HDS5_3ED.A.3#FORMAS"),  # exigencia
    que_pasa_si_no_se_hace=(
        "Es el error que la sesion C3 existe para evitar: copiar la Forma 1 y "
        "cambiarle las constantes. La ecuacion (A.1) arrastra dos terminos "
        "que la (A.2) no tiene -- H_c/D y Ks*S -- y el que DOMINA es el "
        "primero: el HW sale MAYOR que el real (+91 % medido en I3 sobre el "
        "marco de la linea base, 2.00 x 1.50 con la Carta 10 escala 1), o "
        "sea sobrediseño y falsos no-factibles con sus deltas de rasante "
        "inventados. ESTA FRASE DECIA LO CONTRARIO hasta la auditoria de I3 "
        "-- que con Ks = -0.5 el HW saldria menor, del lado no conservador "
        "--, mirando el termino chico sin mirar el grande: para que esa "
        "direccion ocurriera haria falta S > 2*H_c/D, fuera incluso de "
        "dominios.S_CAUCE_MAX. El error sigue sin fallar ruidosamente por "
        "la misma razon de siempre: el resultado es positivo y plausible, y "
        "ninguna guardia de signo lo ve."),
)


# ===========================================================================
# La seccion rectangular: los dos `Fundamento` que C4 emite (§15.7)
# ===========================================================================
# LOS DOS ESTABAN REDACTADOS EN §15.7 y C2 los dejo sin escribir a proposito
# --"su sitio es la sesion que escribe el paso que los emite"--. Esa sesion es
# esta: `M4._pasos_hidraulicos` emite `de_seccion` con el primero y
# `de_critico` con el segundo, en TODA corrida que dimensione un punto, sea la
# seccion circular o rectangular.
#
# NINGUNO DE LOS DOS SALE DE `sin_alcanzar` DE test_memoria_sustentada.py,
# porque ninguno estaba ahi: los tres que quedan en esa lista --F3.TIPO_MARCO,
# F3.MANTENIMIENTO y F3.CELDAS-- son de C5, y se dice aqui porque el prompt de
# C4 daba por hecho que alguno era suyo. El que salio en su sesion fue
# `F4.FORMA_HDS5`, en C3.
#
# QUE NO LLEVAN, Y ES LA MITAD DEL TRABAJO (§15.7): `y_c = (q^2/g)^(1/3)` es
# ALGEBRA, no norma -- sale de la condicion de energia minima, no de un
# numeral --. El fundamento funda POR QUE EL PASO EXISTE; la formula viaja en
# `PasoDeMemoria.formula` y su `formula_cita_id` apunta al numeral que LA
# EXIGE, no a uno que la imprima. Inventarle una cita a la formula seria la
# clase de defecto que `SIN_FUNDAMENTO` existe para no cometer.

# DOS COSAS SE APARTAN DE LA REDACCION DE §15.7, Y LAS DOS LAS CAMBIO LA
# FUENTE PRIMARIA. La segunda, primero, porque es de forma y no de fondo:
# §15.7 escribia las tres variables ENTRECOMILLADAS -- «A 'area de la seccion
# hidraulica', P 'perimetro mojado'» --, o sea transcribia texto de la fuente
# A MANO y FUERA DEL REGISTRO. Ninguna de las dos frases esta en
# `Registro.textos_literales()`, y la copia ya divergia de la pagina: la
# fuente imprime «A : Área de la sección hidráulica (m2)», con tilde, con dos
# puntos y con la unidad. Es «ningun texto literal se transcribe dos veces»
# (CLAUDE.md, §4.5) incumplido en el sitio peor: un `por_que` SE IMPRIME. Se
# reescribe SIN comillas, diciendo lo mismo. Traer las frases de verdad exige
# un `Verbatim` nuevo en la cita, verificado contra su pagina; queda anotado
# como C4-6 en §16.8.
#
# UNA PALABRA SE APARTA DE LA REDACCION DE §15.7, Y LA CAMBIO LA FUENTE
# PRIMARIA. CN escribio «eso depende de la forma, y EL MANUAL no fija
# ninguna». Verificado contra el PDF: el num. 4.1.1.3.6 (impresa 74 / PDF 77)
# efectivamente prescribe Manning, define A, P y R por su significado y su
# unidad --«A : Area de la seccion hidraulica (m2)», «P : Perimetro mojado
# (m)», «R : Radio hidraulico (m)»--, escribe como unica relacion entre ellas
# R = A/P, y NO escribe ninguna geometria de seccion. Hasta ahi la frase es
# exacta. Lo que no lo es es el SUJETO: el MANUAL si enumera formas y si
# impone una, en el num. 4.1.1.3.4 a) (impresa 72 / PDF 75) --«Las secciones
# mas usuales son circulares, rectangulares y cuadradas...» y la seccion
# minima de 0.90 m--, que este mismo repositorio cita en otro sitio. Lo que no
# fija ninguna forma es ESTE numeral, y asi queda escrito. Corregido tambien
# en §15.9 del plan.
SECCION = _fundamento(
    id="F4.SECCION",
    fase=F4,
    que_paso=("Area, perimetro mojado y radio hidraulico de la seccion, para "
              "el tirante de trabajo"),
    por_que=(
        "El num. 4.1.1.3.6 prescribe Manning y define sus tres variables de "
        "seccion -- area hidraulica, perimetro mojado y radio hidraulico -- "
        "por su significado y su unidad, y escribe R = A/P como unica "
        "relacion entre ellas. Lo que NO dice es como se calcula A ni como se "
        "calcula P: eso depende de la forma, y ESTE numeral no fija ninguna. "
        "Ahi es donde entra la seccion como abstraccion: no es una "
        "generalizacion que el proyecto se inventa para que le quepan dos "
        "formas, es el hueco que el propio numeral deja al calculo. Un "
        "circulo lo llena por el angulo mojado y un rectangulo por B*y; el "
        "numeral es el mismo para los dos, y por eso el procedimiento "
        "tambien."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",),    # DEFINICION -> sostiene DEFINE
    que_pasa_si_no_se_hace=(
        "Se escribe un segundo motor de calculo para la otra forma. Es "
        "SIS-A-07 y es el antipatron numero uno de la §12: dos motores, uno "
        "con casos patron y otro sin ellos, que empiezan iguales y divergen "
        "en la primera correccion que solo se aplique a uno."),
)

# TRES FRASES SE APARTAN DE LA REDACCION DE §15.7, Y LAS TRES LAS CAMBIO LA
# FUENTE PRIMARIA. Este `por_que` SE IMPRIME bajo el rotulo «Por que se hace»,
# de modo que una imprecision aqui es una afirmacion publicada. Verificado
# contra `normas/hif12026.pdf`:
#
#   1. «h_o = max(TW, (d_c + D)/2)» NO es la ecuacion que escribe el num.
#      3.3.3. Esa pagina (impresa 3.24 / PDF 106) escribe «Approximate
#      hydraulic gradeline ho = (dc + D)/2 can only be used if...» -- el
#      simbolo atado SOLO a la semisuma -- y el maximo lo dice en PROSA, en el
#      parrafo siguiente y sin nombrar ho: «the greater of tailwater or
#      (dc + D)/2». Con forma de ecuacion, el maximo esta en OTROS numerales
#      (impresas 3.12, 3.32 y 3.43). La v8 ya lo declara en su §4.3. Aqui se
#      escribe como lo que es: la fuente APROXIMA, y el maximo lo toma el
#      proyecto.
#   2. «DOS pasos posteriores lo consumen» es cierto de ESTE pipeline y falso
#      del HDS-5, que le da un tercer uso: el area de la seccion para la
#      velocidad de salida bajo control de salida (num. 3.1.6, impresa 3.18 /
#      PDF 100). Se acota el sujeto. (Desde EXT-3 ese tercer uso SI se
#      implementa, en `M4.velocidad_de_salida`, y el texto lo dice.)
#   3. «La Forma 1 arranca de H_c/D» sin condicionar se imprimia igual bajo
#      Forma 2, donde la ec. (A.2) no usa H_c -- que es el defecto que C3
#      corrigio en la nota del paso y que aqui volvia por el fundamento --.
#
# Lo que NO cambia: el `verbo`. DEFINE esta sostenido por el `caracter` de las
# dos citas (A.2 es DEFINICION, 3.3.3#HO es APROXIMACION) y es el correcto:
# el paso no afirma una obligacion, afirma una cadena de dependencias.
#
# T-0 (INF-5.1.10): EL ID PASA A `F4.YC`. Decia `F4.YC_RECT` y fundaba el paso
# de las dos formas desde C4; el nombre anterior sigue resolviendo como alias
# (`ALIAS_DE_FUNDAMENTO`, arriba). Gana ademas la cita que le faltaba: la
# condicion de flujo critico que la fuente escribe (`HDS5_3ED.A.3.1#CRITICO`),
# que es la `formula_cita_id` del paso. Las otras dos se conservan: sostienen
# el `por_que` --para que se calcula--, no la formula.
YC = _fundamento(
    id="F4.YC",
    fase=F4,
    que_paso="Tirante critico de la seccion, y la energia critica H_c",
    por_que=(
        "El tirante critico no se calcula porque interese por si mismo: se "
        "calcula porque DOS PASOS DE ESTE CALCULO lo consumen. La Forma 1 del "
        "control de entrada arranca de H_c/D --la Forma 2 no lo usa, y la "
        "rama sumergida tampoco--, y el control de salida necesita la altura "
        "de la linea de energia a la salida, que el HDS-5 APROXIMA con "
        "ho = (dc + D)/2 y que el proyecto toma como el mayor entre esa y el "
        "TW. Y desde EXT-3 son TRES: el HDS-5 le da un tercer uso --el area "
        "de la velocidad de salida bajo control de salida, num. 3.1.6-- que "
        "el paso del regimen del barril si implementa, y que es la velocidad "
        "que recibe la proteccion de la Fase 6. En la seccion circular no hay solucion "
        "cerrada y hace falta un segundo Brent; en la rectangular el ancho "
        "superficial es constante y la condicion de energia minima se "
        "despeja: y_c = (q^2/g)^(1/3) con q = Q/B. Que sea exacta no es un "
        "lujo de elegancia: retira la clase entera de fallos de convergencia "
        "que la via por resolutor tiene en la circular, donde un caudal "
        "diminuto la lleva a un angulo en que el area de la seccion se anula. "
        "Lo que la solucion cerrada NO retira es el techo: el tirante critico "
        "no puede exceder la altura interior del barril, y eso lo escribe el "
        "HDS-5 en su num. 3.3.3."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.3.3#HO",     # sostiene DEFINE (definicion/aproximacion)
           "HDS5_3ED.A.2",          # DEFINICION
           "HDS5_3ED.A.3.1#CRITICO"),   # DEFINICION: la condicion de flujo critico
    que_pasa_si_no_se_hace=(
        "El control de salida se queda sin h_o y la Forma 1 sin H_c: los dos "
        "pasos que producen el HW gobernante. Y si en vez de la solucion "
        "cerrada se reusa el Brent de la circular, se arrastra a la "
        "rectangular una fragilidad numerica que en ella NO existe: es la "
        "clase de fallo que `LimiteNumericoError` cubre en `M4.tirante_"
        "critico` (SIS-G-02). Los identificadores internos viven AQUI y no en "
        "el `por_que` a proposito: este campo no se imprime en la memoria y "
        "aquel si, y un informe de tesis no publica el codigo de un hallazgo "
        "de auditoria bajo el rotulo «por que se hace». Es la convencion que "
        "ya siguen F4.MANNING, F5.V2b y F4.FORMA_HDS5, y que este fundamento "
        "rompia hasta que la auditoria de C4 lo vio."),
)


# El nombre de Python anterior, para quien lo importaba: es el MISMO objeto.
YC_RECT = YC


# ===========================================================================
# El catalogo del cajon: los dos `Fundamento` que C5 emite (§15.7)
# ===========================================================================
# LOS OTROS TRES DE ESTE GRUPO --F3.TIPO_MARCO, F3.MANTENIMIENTO y F3.CELDAS--
# LOS ESCRIBIO C2, que transcribio sus citas y no podia dejarlas sin
# consumidor (T4 rechaza una cita que nadie referencia). Estos dos no: sus
# citas ya existian antes de C2, de modo que no creaban ninguna huerfana, y su
# sitio era la sesion que escribe el paso que los emite. Esa sesion es C5:
# `M2_material._pasos_del_marco` emite los CINCO cuando el catalogo resuelve
# un candidato de marco.
#
# QUE SIGNIFICA QUE LOS CINCO SIGAN EN `sin_alcanzar` DE
# test_memoria_sustentada.py, y no es lo mismo que antes: hasta C5 estaban ahi
# porque EL PASO NO EXISTIA. Ahora existe, y lo que falta es que el expediente
# declare los criterios del cajon -- sin ellos ningun punto de Familia C
# dimensiona y la corrida por defecto no llega a emitirlos --. Es la misma
# categoria que F7.RELLENO, F8.RECUBRIMIENTO o F10.CUNETA: una fase que la
# corrida no alcanza por un vacio del expediente. La prueba de que el paso
# existe la da `test_M2_material`, declarando los criterios en caliente.

SECCION_CANAL = _fundamento(
    id="F3.SECCION_CANAL",
    fase=F3,
    que_paso=("Adopcion de la seccion del cajon en un cruce de canal de "
              "riego, fuera del piso de 0.90 m"),
    por_que=(
        "El piso de 0.90 m del num. 4.1.1.3.4 a) NO se aplica aqui, y no "
        "porque el proyecto decida saltarselo: el mismo numeral que lo fija "
        "lo EXCEPTUA, en la misma oracion, para los cruces de canales de "
        "riego, y ordena adoptar alli la seccion segun cada diseno "
        "particular. La Familia C ES ese conjunto de cruces. Lo que el "
        "numeral hace no es liberar la seccion: la traslada del catalogo al "
        "diseno, y por eso la progresion B*H de este proyecto es una "
        "adopcion declarada y no una lectura de la norma."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.4a",),   # EXIGENCIA -> sostiene OBLIGA
    que_pasa_si_no_se_hace=(
        "Se hereda al cajon un piso que su propio numeral le levanta, o -- al "
        "reves -- se lee 'de acuerdo a cada diseno particular' como si fuera "
        "un valor. Las dos contradicen la fuente, por lados opuestos."),
)

N_CAJON = _fundamento(
    id="F4.N_CAJON",
    fase=F4,
    que_paso=("Coeficiente de rugosidad de Manning del cajon de concreto, "
              "por analogia declarada dentro del grupo A de la Tabla N 09"),
    por_que=(
        "La Tabla N 09 SI cubre al cajon por el TITULO DE SU GRUPO, que "
        "habla de conducto cerrado con escurrimiento parcialmente lleno y no "
        "de tuberia: es el unico grupo de la tabla que describe una "
        "alcantarilla. Lo que no tiene es una FILA que nombre la seccion "
        "rectangular. El vacio es de fila y no de grupo, y por eso la "
        "analogia se declara DENTRO del grupo que ya cubre la estructura "
        "-- entre filas separadas por un atributo que no es la forma -- y es "
        "mas estrecha que la de 'n_manning_hdpe', que cruza material. El "
        "rango se toma completo, minimo y maximo: la regla de doble n pide "
        "los dos extremos, porque n_max es conservador para capacidad y "
        "n_min para velocidad y socavacion."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",          # DEFINICION -> sostiene DEFINE
           "MC_HHD.4.1.1.3.6#T09"),     # DEFINICION
    que_pasa_si_no_se_hace=(
        "Se toma el n del concreto 'porque el cajon es de concreto', que es "
        "una analogia igual de real pero SIN DECLARAR: la memoria imprimiria "
        "un valor [N] apoyado en una fila cuyo rotulo dice 'tubo', y un "
        "revisor que abra la pag. impresa 75 no encontraria el cajon por "
        "ninguna parte."),
)


# --- T-3 (auditoria adversarial, H1) --- El n del marco por la fila PROPIA
# del cajon de la Tabla B.1 del HDS-5. Desde la auditoria es el valor de
# archivo de 'n_manning_cajon' [C]; el fundamento de arriba (F4.N_CAJON)
# queda para la alternativa barrible, la fila de la Tabla N 09 por analogia.
N_CAJON_TB1 = _fundamento(
    id="F4.N_CAJON_TB1",
    fase=F4,
    que_paso=("Coeficiente de rugosidad de Manning del cajon de concreto, "
              "por la fila del cajon de la Tabla B.1 del HDS-5"),
    por_que=(
        "La Tabla N 09 del Manual cubre al cajon por el titulo de su grupo A "
        "y no tiene fila de seccion rectangular: es un vacio de fila. La "
        "fuente tecnica de la que el proyecto ya toma la carta de control "
        "de entrada y el coeficiente de perdida a la entrada del marco "
        "--el HDS-5-- si tabula el cajon de concreto, en su propia fila, y "
        "con ella se cubre el vacio. El rango se toma completo: la regla de "
        "doble n pide los dos extremos. La fuente advierte que sus valores "
        "son de laboratorio y que en un cajon vaciado in situ el n depende "
        "de la calidad del encofrado."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.TB.1",                  # DEFINICION -> sostiene DEFINE
           "HDS5_3ED.B.3#CAJON_IN_SITU"),    # DEFINICION
    que_pasa_si_no_se_hace=(
        "El n del marco saldria de una fila de la Tabla N 09 cuyo rotulo no "
        "describe un cajon, aplicada por analogia, mientras la fuente de la "
        "carta y del ke del mismo marco trae una fila para el; y la memoria "
        "no diria que el n de capacidad puede subir con un encofrado peor."),
)


# ===========================================================================
# --- T-2 --- (cadena T, 2026-11-11) · Pendiente del conducto
# ===========================================================================
# Tres fundamentos, los tres sobre la PENDIENTE DEL BARRIL (INF-3.2.7,
# INF-5.1.6, INF-0.5):
#
#   F5.V10          la verificacion nueva: pendiente del conducto dentro de la
#                   banda adoptada. Verbo DEFINE, y no OBLIGA aunque la cita
#                   del Manual sea EXIGENCIA: lo que el Manual exige es
#                   ESTUDIAR el cambio de pendiente, sin cifra; los dos
#                   numeros de la banda son adopciones [A] apoyadas en lo que
#                   el HDS-5 DESCRIBE. Poner OBLIGA pasaria T11 y seria el
#                   mismo agujero que `F5.V1` y `F5.VC1` ya documentan.
#   F4.HORIZONTAL   el barril con S = 0: no hay tirante normal, y el regimen
#                   lo fija el extremo de aguas abajo. Verbo PERMITE: la
#                   fuente dice «can be reasonably applied».
#   F4.PISO_HW      la eleccion del piso de la carga de entrada cuando la
#                   correccion por pendiente la anula. Es de ELECCION, como
#                   `F5.V2b.REGIMEN`: la fuente define la Forma 1 y el
#                   termino, no prescribe el piso.

V10 = _fundamento(
    id="F5.V10",
    fase=F5,
    que_paso=("V10 - Pendiente del conducto dentro de la banda adoptada: no "
              "menor que la minima ni mayor que la maxima"),
    por_que=(
        "La pendiente del barril no es un dato neutro: mas plana que el cauce "
        "deposita, mas empinada erosiona la salida y, pasado cierto punto, "
        "pide del tubo cosas que este calculo no dimensiona. El Manual lo "
        "escribe sin cifra --la pendiente no debe alterar "
        "«desmesuradamente» la erosion y la sedimentacion, y sus cambios "
        "«deben ser estudiados en forma cuidadosa»-- y ninguna fuente de "
        "normas/ fija un minimo ni un maximo en numeros. Lo que hay son tres "
        "hechos de la fuente tecnica: el HDS-5 admite el barril horizontal; "
        "dice que la mayoria de las alcantarillas se construyen por debajo "
        "del 10 % y que para esas no se usan medidas estructurales "
        "especiales; y traza sus curvas de control de entrada al 2 % porque "
        "el efecto de la pendiente es chico. Con eso el proyecto adopta una "
        "BANDA --'pendiente_minima_conducto' y 'pendiente_maxima_conducto', "
        "los dos [A] con ventana-- y esta verificacion dice si la pendiente "
        "con que corrio el diseño cae dentro. No sustituye a las que miden "
        "el efecto: la sedimentacion la siguen juzgando V2 (velocidad "
        "minima) y V2b (indicador de pendiente frente al cauce), y la "
        "erosion V3 (velocidad maxima) y la proteccion de salida."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.3",              # EXIGENCIA sin numero
           "HDS5_3ED.3.3.4#HORIZONTAL",     # PERMISO: S = 0
           "HDS5_3ED.5.4.4#PENDIENTE_10",   # DEFINICION -> sostiene DEFINE
           "HDS5_3ED.5.4.4#PENDIENTE_20",   # RECOMENDACION
           "HDS5_3ED.A.3#PENDIENTE_2"),     # DEFINICION
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta T-2 (INF-3.2.7): ninguna linea de codigo "
        "miraba la pendiente del barril. Una celda cargada en 0.25 por "
        "0.025 dimensionaba un tubo al 25 % sin una palabra sobre anclajes, "
        "y un barril plano se rechazaba como dato invalido, que es lo "
        "contrario de lo que la fuente admite."),
)

HORIZONTAL = _fundamento(
    id="F4.HORIZONTAL",
    fase=F4,
    que_paso=("Barril horizontal (S = 0): no hay tirante normal, y el "
              "regimen del conducto lo fija el extremo de aguas abajo"),
    por_que=(
        "Manning necesita pendiente: con S = 0 ningun tirante transporta el "
        "caudal en flujo uniforme, y el tirante normal no existe. Eso no "
        "hace imposible la obra. El HDS-5 dice que sus procedimientos de "
        "control de entrada y de salida se pueden aplicar razonablemente a "
        "un barril horizontal: en el control de entrada la correccion por "
        "pendiente vale cero, y en el de salida la perdida H es la misma y "
        "la caida S·L desaparece. Lo que cambia es de donde salen el tirante "
        "y la velocidad DENTRO del barril: sin flujo uniforme, la lamina la "
        "fija la salida --el tirante critico o el del receptor, el mayor-- "
        "y sube hacia la entrada (perfil H2), de modo que el borde libre y "
        "la velocidad minima se juzgan sobre el perfil de la lamina, la "
        "velocidad maxima sobre la seccion de salida, y la velocidad que "
        "recibe la proteccion es la de esa misma seccion."),
    verbo=Verbo.PERMITE,
    citas=("HDS5_3ED.3.3.4#HORIZONTAL",     # PERMISO -> sostiene PERMITE
           "HDS5_3ED.3.3.4#KS",
           "HDS5_3ED.3.3.4#H_SIN_AJUSTE",
           "HDS5_3ED.3.5.1#H2"),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta T-2 (INF-5.1.6): `M3.resolver_manning` y las "
        "tres piezas de M4 rechazaban S = 0 con `DatoInvalidoError`, de modo "
        "que un barril plano en una llanura --el caso que la fuente describe "
        "para un flujo que puede ir en los dos sentidos-- no se podia "
        "calcular, y quien lo necesitaba tecleaba una pendiente ficticia."),
)

PISO_HW = _fundamento(
    id="F4.PISO_HW",
    fase=F4,
    que_paso=("Carga de control de entrada cuando la correccion por pendiente "
              "Ks·S la deja nula o negativa: el piso adoptado "
              "(`hw_entrada_fuera_de_rango`)"),
    por_que=(
        "El HDS-5 define la Forma 1 de la ecuacion no sumergida como la "
        "energia especifica en el tirante critico, H_c, «adjusted with "
        "correction factors», y de esos factores el de pendiente es una "
        "recta sin tope: Ks·S, con Ks = -0.5. La misma fuente dice que ese "
        "efecto es chico y que sus curvas se trazan al 2 %. Con un caudal "
        "chico y una pendiente grande la recta se lleva la carga entera y "
        "la ecuacion devuelve una lamina por debajo del fondo, que no "
        "existe. La fuente no dice que hacer ahi. El proyecto elige entre "
        "dos salidas declaradas: quedarse con la BASE de la ecuacion --H_c, "
        "la carga minima con que la entrada pasa el caudal en regimen "
        "critico-- o descartar la combinacion. La primera es del lado "
        "seguro frente a lo que la ecuacion entregaba (una carga nula) y no "
        "inventa un numero: es un resultado que el paso 4.2 ya tiene."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.A.2.1#FORMA_1",        # DEFINICION -> sostiene DEFINE
           "HDS5_3ED.A.2.1#KS",
           "HDS5_3ED.A.3#PENDIENTE_2"),
    que_pasa_si_no_se_hace=(
        "Lo que pasaba hasta PF-1: el punto salia «no factible» por una "
        "condicion que ningun diametro resuelve, sin criterio a la vista. Y "
        "lo que pasaba entre PF-1 y T-2: el criterio existia sin valor y la "
        "corrida se detenia a pedirlo cada vez que un alivio pequeño caia en "
        "un tramo empinado."),
)


# --- T-4 --- (cadena T, 2026-11-11) Fase 3: el diametro exterior y la matriz
# de durabilidad (v8 §3.2, §3.3 y §3.4).
# ---------------------------------------------------------------------------
# SEIS fundamentos de la matriz --uno por ensayo, mas el del suelo de
# fundacion-- y el del diametro exterior. Cada uno lleva el verbo que sus
# citas sostienen (T11): los umbrales de pH y resistividad son EXIGENCIA en
# su fuente («only ... are acceptable», «será necesario proteger»); el suelo
# de fundacion es una RECOMENDACION del Manual.
#
# NINGUNO SE EMITE EN LA CORRIDA DE REFERENCIA, y no es un olvido: los cuatro
# puntos de `tests/ejemplo_puntos.csv` no traen ensayos de durabilidad --son
# entradas del EMS que el programa no rellena (docs/contrato_entradas.md)-- y
# sin datos la matriz no actua. Estan censados con esa razon en
# `tests/test_memoria_sustentada.py`, y `tests/test_t4_materiales_durabilidad.py`
# los ejercita declarando los ensayos.
# ===========================================================================

D_EXTERIOR = _fundamento(
    id="F3.D_EXTERIOR",
    fase=F3,
    que_paso=("Espesor de pared del conducto: lo que separa el diametro "
              "hidraulico D del diametro exterior D_ext = D + 2t"),
    por_que=(
        "El catalogo dimensiona con el diametro INTERIOR, que es el nominal "
        "de las tres normas de producto, y hay dos sitios donde lo que hace "
        "falta es el exterior: la clave fisica desde la que se mide el "
        "relleno (7.A) y el volumen que el conducto desplaza bajo el "
        "freatico (V7). Lo que separa uno de otro NO es la misma cosa en los "
        "tres materiales: en el tubo de concreto es el espesor de la pared; "
        "en el metal corrugado, la profundidad de la corrugacion mas el "
        "espesor de la plancha, porque el diametro nominal se mide en la "
        "cresta INTERIOR y la profundidad de cresta a valle sobre una misma "
        "cara; en el polietileno corrugado, la altura del perfil, que su "
        "norma de producto no fija y que aqui sale del diametro exterior "
        "MAXIMO que AASHTO LRFD tabula para el producto."),
    verbo=Verbo.DEFINE,
    citas=("AASHTO_M36.T1",              # DEFINICION -> sostiene DEFINE
           "AASHTO_M36.8.1.1",
           "AASHTO_LRFD_9.TA12-11",      # DEFINICION
           "EG2013.508.02a"),            # interior liso, exterior corrugado
    que_pasa_si_no_se_hace=(
        "La clave se calcula con el diametro interior y la rasante minima "
        "sale corta en t; y la subpresion de V7 se calcula sobre un volumen "
        "menor que el desplazado, del lado inseguro (MAT-D3, MAT-D4). O, que "
        "es lo que pasaba hasta T-4, el TMC y el HDPE se descartan antes de "
        "llegar a 7.A y a V7 por no tener espesor, y la matriz de materiales "
        "degenera a concreto (INF-5.1.17)."),
)

DUR_PH = _fundamento(
    id="F3.DUR.PH",
    fase=F3,
    que_paso=("Matriz de durabilidad: pH del suelo o del agua frente a los "
              "umbrales de la tuberia de acero corrugado"),
    por_que=(
        "El acero se corroe en medios acidos y alcalinos, y la corrosion "
        "perfora la solera antes de que el conducto cumpla su vida util. La "
        "norma peruana de construccion pone el umbral a partir del cual la "
        "tuberia metalica tiene que protegerse; la fuente tecnica que el "
        "proyecto adopta para el vacio que esa norma deja --a partir de que "
        "pH el acero deja de ser alternativa aunque se proteja-- pone un "
        "intervalo fuera del cual solo valen concreto, termoplastico y "
        "aluminio. Al concreto y al polietileno el pH no los excluye."),
    verbo=Verbo.OBLIGA,
    citas=("EG2013.507.10",              # EXIGENCIA -> sostiene OBLIGA
           "WSDOT_HM.8-5.1#PH",          # EXIGENCIA
           "WSDOT_HM.8-4.3#ZONA_III",
           "WSDOT_HM.8-3.1#CONCRETO",
           "MC_HHD.4.1.1.3.7f#TMC",
           "AASHTO_M36.1.2",
           "MC_HHD.4.1.1.3.4b"),
    que_pasa_si_no_se_hace=(
        "El TMC entra como candidato en un sitio donde su norma de producto "
        "reconoce que ningun recubrimiento metalico basta, y el expediente "
        "lo elegiria --o lo descartaria-- sin haber mirado el unico dato que "
        "lo decide."),
)

DUR_RESISTIVIDAD = _fundamento(
    id="F3.DUR.RESISTIVIDAD",
    fase=F3,
    que_paso=("Matriz de durabilidad: resistividad del suelo o del agua "
              "frente al umbral de la tuberia de acero corrugado"),
    por_que=(
        "La resistividad mide la facilidad con que el suelo o el agua "
        "conducen corriente: cuanto menor, mas rapida la corrosion "
        "electroquimica del acero. Un suelo salino con freatico somero es el "
        "caso tipico de resistividad baja. La fuente tecnica pone el umbral "
        "por debajo del cual el acero deja de ser alternativa."),
    verbo=Verbo.OBLIGA,
    citas=("WSDOT_HM.8-5.2#RESISTIVIDAD",     # EXIGENCIA -> sostiene OBLIGA
           "WSDOT_HM.8-4.3#ZONA_III",
           "MC_HHD.4.1.1.3.7f#SALINIDAD"),
    que_pasa_si_no_se_hace=(
        "Se especifica tuberia metalica en un suelo que la corroe a corto "
        "plazo: es lo que el Manual de Hidrologia advierte del agua con alta "
        "salinidad sin dar el numero."),
)

DUR_ABRASION = _fundamento(
    id="F3.DUR.ABRASION",
    fase=F3,
    que_paso=("Matriz de durabilidad: nivel de abrasion del sitio frente a "
              "lo que cada material admite"),
    por_que=(
        "La abrasion desgasta la solera por el arrastre de arenas, gravas y "
        "piedras, y depende de la carga de fondo tanto como de la velocidad. "
        "El termoplastico resiste la abrasion igual o mejor que los otros "
        "materiales, pero no se puede REFORZAR: por eso la fuente lo prohibe "
        "en el nivel severo, donde al metal y al concreto les pide mas "
        "espesor o solera de concreto. El nivel del sitio es un dato de "
        "campo --granulometria del lecho, pendiente, historial de las obras "
        "vecinas--, no un resultado del calculo hidraulico."),
    verbo=Verbo.OBLIGA,
    citas=("WSDOT_HM.8-3.3#SEVERA",           # EXIGENCIA -> sostiene OBLIGA
           "WSDOT_HM.T8-4",
           "WSDOT_HM.3-3.5#10FTS",
           "AASHTO_LRFD_9.C12.6.9#NIVEL_4",
           "MC_HHD.4.1.1.3.7e",
           "MC_HHD.4.1.1.3.7g#AGRESIVAS"),
    que_pasa_si_no_se_hace=(
        "El nivel de abrasion solo entraria al diseño por la velocidad de "
        "V3, que es una de sus tres caracteristicas: un cauce de pendiente "
        "suave con carga de fondo pesada pasaria V3 con un material que la "
        "fuente no admite ahi."),
)

DUR_SULFATOS = _fundamento(
    id="F3.DUR.SULFATOS",
    fase=F3,
    que_paso=("Matriz de durabilidad: sulfatos del suelo o del agua y "
              "requisitos del concreto"),
    por_que=(
        "Los sulfatos atacan la pasta de cemento. La norma peruana de "
        "concreto no prohibe el concreto en ningun nivel de exposicion: le "
        "exige un tipo de cemento, una relacion agua-material cementante "
        "maxima y una resistencia minima que crecen con la exposicion. Por "
        "eso el ensayo no descarta el material: lo deja candidato CON el "
        "requisito escrito."),
    verbo=Verbo.OBLIGA,
    citas=("E060.T4.4",),                     # EXIGENCIA
    que_pasa_si_no_se_hace=(
        "El tubo o el marco de concreto se especifican con cemento comun en "
        "un suelo que lo degrada, y la memoria no deja constancia del "
        "requisito que el ensayo imponia."),
)

DUR_CLORUROS = _fundamento(
    id="F3.DUR.CLORUROS",
    fase=F3,
    que_paso=("Matriz de durabilidad: cloruros del suelo o del agua y "
              "proteccion del refuerzo y del acero"),
    por_que=(
        "Los cloruros corroen el acero: el refuerzo del concreto y la "
        "plancha de la tuberia metalica. La norma peruana de concreto exige "
        "una mezcla mas cerrada y el recubrimiento minimo cuando el concreto "
        "reforzado va a estar expuesto a cloruros de sal, agua salobre o "
        "agua de mar, y NO pone un umbral en ppm: define la exposicion por "
        "el origen del cloruro. Por eso el ensayo no decide solo. Declarado "
        "el contenido de cloruros, la memoria deja escrito el requisito y "
        "quien tiene que decidir si la exposicion aplica."),
    verbo=Verbo.OBLIGA,
    citas=("E060.4.4.2",                      # EXIGENCIA -> sostiene OBLIGA
           "E060.T4.2",
           "MC_HHD.4.1.1.3.7f#SALINIDAD",
           "MC_HHD.4.1.1.3.7f#COSTA"),
    que_pasa_si_no_se_hace=(
        "Un ensayo con cloruros se queda en el EMS y no llega a la eleccion "
        "de material ni a la especificacion del concreto, en un corredor "
        "costero de riego donde es el dato esperable."),
)

DUR_SUELO_FUNDACION = _fundamento(
    id="F3.DUR.SUELO_FUNDACION",
    fase=F3,
    que_paso=("Suelo de fundacion deficiente: aviso de que el Manual "
              "recomienda el marco de concreto"),
    por_que=(
        "Un conducto flexible reparte la carga al suelo que lo rodea y uno "
        "rigido de seccion circular la concentra en su cama: sobre un suelo "
        "de fundacion malo los dos se asientan de forma desigual. El marco "
        "apoya en una losa. El Manual lo recomienda para ese caso y no dice "
        "que suelo es de mala calidad; el proyecto declara cuales cuenta "
        "como tales, apoyado en los que la norma peruana de cimentaciones "
        "no permite como apoyo. Es un AVISO: no cambia el material ni la "
        "seccion que el calculo adopta."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.4a#MARCO",         # RECOMENDACION -> RECOMIENDA
           "E050.24",
           "E050.24#REMOVER",                 # la norma manda reemplazarlos
           "E050.38.1",                       # lo que este aviso NO evalua
           "E050.FIG3"),
    que_pasa_si_no_se_hace=(
        "La clasificacion SUCS de la calicata se carga y nadie la lee "
        "(INF-5.1.9): un tubo sobre turba o suelo organico sale de la "
        "corrida sin una sola linea que lo advierta."),
)


# --- T-4 (auditoria adversarial, H3, H5, H6) --- Suelo agresivo para el acero.
DUR_SUELO_AGRESIVO = _fundamento(
    id="F3.DUR.SUELO_AGRESIVO",
    fase=F3,
    que_paso=("Matriz de durabilidad: agresividad del suelo para la tuberia "
              "de acero corrugado galvanizado"),
    por_que=(
        "La norma peruana de construccion exige proteger la tuberia metalica "
        "cuando el agua tiene un pH menor de 5.8 o cuando los suelos "
        "circundantes presentan sustancias agresivas, y no dice cuales ni en "
        "que cantidad. El Manual de Hidrologia advierte lo mismo sin numero: "
        "cerca del mar, con aguas salinas o acidas, en suelos alcalinos o "
        "con turba, no recomienda la alcantarilla metalica. El proyecto lee "
        "«sustancias agresivas» con las dos unicas escalas numericas que "
        "tiene a mano y lo declara como lectura suya: la exposicion a "
        "sulfatos de la norma de concreto por encima de insignificante, y "
        "los criterios electroquimicos con que AASHTO LRFD define el suelo "
        "no agresivo para acero galvanizado enterrado --pH de 5 a 10, "
        "resistividad de al menos 3000 ohm-cm, cloruros hasta 100 ppm y "
        "sulfatos hasta 200 ppm--. Esos criterios son de refuerzos de muros "
        "y de anclajes, no de alcantarillas: se aplican por analogia de "
        "metal, recubrimiento y medio, y por eso su efecto por defecto es "
        "un aviso; la exclusion del material se reserva a la fuente tecnica "
        "que habla de tuberia. El mismo cuerpo da, para pilotes, indicativos "
        "menos estrictos: resistividad menor de 2000 ohm-cm, pH menor de "
        "5.5, sulfatos sobre 1000 ppm y cloruros en el agua sobre 500 ppm."),
    verbo=Verbo.RECOMIENDA,
    citas=("AASHTO_LRFD_9.10.7.5#INDICATIVOS",      # RECOMENDACION
           "AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO",
           "AASHTO_LRFD_9.11.12.8#AGRESIVO",
           "EG2013.507.10",
           "MC_HHD.4.1.1.3.7f#COSTA",
           "MC_HHD.4.1.1.3.7g#AGRESIVAS"),
    que_pasa_si_no_se_hace=(
        "Un tubo de acero galvanizado queda candidato en un suelo con 2000 "
        "ppm de cloruros y 1500 ohm-cm sin una linea que lo advierta, porque "
        "el filtro de la fuente de alcantarillas solo mira pH y resistividad "
        "bajo 1000 ohm-cm; y la mitad de la clausula de la norma peruana "
        "--los suelos circundantes-- no se aplica nunca."),
)

# --- T-6 --- Fase 7.B: los pasos que iban como frase (INF-3.3.3)
# ===========================================================================
# Hasta T-6 la Fase 7 emitia UN paso (G1, F7.RELLENO) y todo lo demas de 7.B
# --la longitud, el factor de esviaje, la caida S*L, la cota de salida y G2--
# llegaba a la memoria como una frase de M11 con los numeros dentro: sin
# formula, sin sustitucion y sin cita. Estos siete fundan los pasos que M7
# emite ahora. Ninguno afirma un NUMERO de la fuente: lo que las fuentes dan
# es el procedimiento (HDS-5) y dos exigencias sin cifra (MTC 4.1.1.3.3, HDS-5
# 3.3.5); los valores -- talud, esviaje maximo, desnivel de entrega -- son
# criterios [A] y el paso los imprime como tales.

PENDIENTE_CONDUCTO = _fundamento(
    id="F7.PENDIENTE",
    fase=F7,
    que_paso="Pendiente adoptada del conducto, con su origen",
    por_que=(
        "La pendiente del conducto no es un numero suelto del expediente: "
        "fija la caida entre la entrada y la salida, entra en Manning y en "
        "el control de salida, y es lo que el Manual manda cuidar para no "
        "alterar la erosion y la sedimentacion del cauce. Por eso la memoria "
        "tiene que decir DE DONDE sale la que se uso -- la del cauce, que es "
        "la regla; una declarada para este punto; o un limite adoptado por "
        "el proyecto que la gobierna --, porque las tres se defienden con "
        "argumentos distintos y se corrigen en sitios distintos."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.1.3.3", "HDS5_3ED.5.3.3#ALINEADO"),
    que_pasa_si_no_se_hace=(
        "La memoria imprime una pendiente sin decir si es la del cauce o una "
        "elegida, y el revisor no puede saber si el conducto sigue al cauce "
        "-- la condicion que el HDS-5 asocia a la ausencia de problemas de "
        "sedimentacion -- o se aparta de el."),
)

ESVIAJE = _fundamento(
    id="F7.ESVIAJE",
    fase=F7,
    que_paso="Factor de esviaje, 1 / cos(esviaje)",
    por_que=(
        "El conducto se tiende sobre la direccion de la corriente, que es la "
        "ubicacion en planta que el Manual llama ideal, y la corriente no "
        "cruza la via a escuadra. El eje del conducto es entonces la "
        "hipotenusa del ancho que atraviesa: la seccion del terraplen que el "
        "conducto recorre es la del cruce esviado, no la normal al eje, y "
        "todo lo que se mide a traves de la via se alarga con 1/cos del "
        "angulo. No es un coeficiente adoptado: es la geometria del cruce "
        "oblicuo, con el angulo medido como lo define el HDS-5, desde la "
        "normal a la via."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.5.4.1#ESVIAJE", "MC_HHD.4.1.1.3.2"),
    que_pasa_si_no_se_hace=(
        "La longitud se calcularia sobre la seccion normal a la via y el "
        "conducto saldria corto justo en los cruces mas esviados: a 30 "
        "grados falta el 15 % y a 45 grados el 41 %."),
)

ESVIAJE_MAXIMO = _fundamento(
    id="F7.ESVIAJE_MAX",
    fase=F7,
    que_paso="Esviaje del cruce frente al maximo que el proyecto adopta",
    por_que=(
        "Un cruce muy esviado alarga el conducto y complica la embocadura: "
        "con el cabezal paralelo a la via, la CARA de la embocadura queda "
        "esviada respecto del barril el mismo angulo del cruce -- el flujo, "
        "alineado con el barril, no gira: lo esviado es la cara por la que "
        "entra --, y el HDS-5 describe un maximo practico de unos 45 grados "
        "para ese esviaje de embocadura. El esviaje es un DATO del cruce "
        "-- lo mide la topografia -- y no una decision del calculo, de modo "
        "que superarlo no invalida el punto: obliga a mirarlo en planta y a "
        "decidir si se acondiciona el cauce, que es la salida que el Manual "
        "nombra."),
    verbo=Verbo.RECOMIENDA,
    citas=("HDS5_3ED.5.4.2#MAXIMO_PRACTICO", "MC_HHD.4.1.1.3.2"),
    que_pasa_si_no_se_hace=(
        "Un esviaje de 60 grados duplica la longitud del conducto y uno de "
        "75 la multiplica por 3.9 sin que nada lo señale -- y es ademas la "
        "firma de un esviaje copiado de un expediente que lo mide desde el "
        "eje de la via y no desde su normal."),
)

LONGITUD_CONDUCTO = _fundamento(
    id="F7.LONGITUD",
    fase=F7,
    que_paso="Longitud del conducto sobre la seccion transversal del cruce",
    por_que=(
        "La longitud sale de superponer el conducto a la seccion "
        "transversal de la via en el cruce: no es un dato que se ponga a "
        "mano. A cada lado el talud del terraplen baja desde el borde de la "
        "plataforma hasta encontrar al conducto, y como la entrada y la "
        "salida no estan a la misma cota -- la salida queda mas baja en "
        "toda la caida --, los dos taludes no recorren la misma altura. La "
        "longitud que entra al diseño hidraulico es una APROXIMACION, y la "
        "fuente lo dice: se calcula antes de conocer la seccion, porque la "
        "seccion depende de ella. Lo que la fuente no fija, y el proyecto "
        "elige y declara, es el metodo: hasta que nivel baja cada talud "
        "mientras la seccion no se conoce."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.2.2.4#LONGITUD", "HDS5_3ED.3.1.4#LONGITUD",
           "DG2018.304.10#T304.11", "DG2018.304.05#BOMBEO",
           "DG2018.304.06#PERALTE"),
    que_pasa_si_no_se_hace=(
        "La perdida por friccion del control de salida y la caida del "
        "conducto se calculan con una longitud que nadie puede reconstruir, "
        "y la cota de salida -- que es la que se amarra al receptor -- "
        "hereda el error."),
)

COTA_SALIDA = _fundamento(
    id="F7.COTA_SALIDA",
    fase=F7,
    que_paso="Caida del conducto y cota de fondo de la salida",
    por_que=(
        "La cota de salida no se mide: es la de entrada menos lo que el "
        "conducto cae a lo largo de su longitud con la pendiente del diseño. "
        "Es el numero con que la obra se amarra al cuerpo receptor y el que "
        "decide en cual de las ubicaciones tipicas del Manual queda el "
        "conducto -- siguiendo el cauce, con la entrada deprimida o con la "
        "salida elevada --, de modo que tiene que poder rehacerse a mano."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.LAMINA_01", "HDS5_3ED.2.2.4#LONGITUD"),
    que_pasa_si_no_se_hace=(
        "La cota de salida aparece en la memoria como un dato, cuando es un "
        "resultado que arrastra la pendiente, la longitud y la cota de "
        "entrada: si una de las tres cambia, nadie ve que la salida se movio."),
)

ENTREGA = _fundamento(
    id="F7.ENTREGA",
    fase=F7,
    que_paso="Entrega al cuerpo receptor: cota de salida frente a su fondo",
    por_que=(
        "El conducto entrega el agua a un cauce que tiene su propio fondo. "
        "Una salida por DEBAJO de ese fondo queda enterrada: el receptor la "
        "colmata y el conducto trabaja ahogado en sedimento. Una salida muy "
        "por ENCIMA descarga en caida y socava. Son las dos formas en que la "
        "obra altera la erosion y la sedimentacion del cauce, que es lo que "
        "el Manual manda cuidar al fijar la pendiente -- y la cota de salida "
        "es consecuencia directa de la pendiente --. El Manual tipifica las "
        "ubicaciones de la salida respecto del cauce y NO dice cuanto "
        "desnivel debe haber: contrastar la cota de salida con el fondo del "
        "receptor es la lectura del proyecto, y el desnivel exigido una "
        "adopcion suya."),
    # DEFINE y no OBLIGA: la Lamina N 01 tipifica (DEFINICION) y el num.
    # 4.1.1.3.3 obliga sobre la PENDIENTE, no sobre la entrega. Escribir «el
    # Manual obliga a verificar la entrega» seria atribuirle lo que no dice.
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.LAMINA_01", "MC_HHD.4.1.1.3.3"),
    que_pasa_si_no_se_hace=(
        "La obra puede quedar proyectada con la salida bajo el fondo del "
        "dren que la recibe, y eso no se corrige subiendo la rasante: se "
        "corrige con la pendiente, con la longitud o con la cota del "
        "receptor."),
)

ENCAJE = _fundamento(
    id="F7.ENCAJE",
    fase=F7,
    que_paso=("Encaje de la seccion adoptada en la seccion transversal: "
              "longitud entre cabezales a la clave"),
    por_que=(
        "El diseño hidraulico arranca con una longitud aproximada porque la "
        "seccion todavia no se conoce. Elegida la seccion, la fuente manda "
        "encajarla en la seccion transversal de la via: con muro de cabecera "
        "el talud ya no baja hasta el fondo sino hasta la coronacion del "
        "muro, que como minimo esta a la clave exterior del conducto, y el "
        "barril entre cabezales es mas corto que el aproximado. La "
        "diferencia tiene que quedar a la vista, porque es la que dice si la "
        "longitud con que se calculo el control de salida sigue valiendo."),
    verbo=Verbo.OBLIGA,
    citas=("HDS5_3ED.3.3.5#ENCAJE", "HDS5_3ED.3.1.4#LONGITUD"),
    que_pasa_si_no_se_hace=(
        "El cabezal se dimensionaria sobre una longitud de barril que no es "
        "la suya, y nadie sabria cuanto se aparta la longitud construida de "
        "la que uso el calculo hidraulico."),
)


# ===========================================================================
# --- T-5 --- (cadena T, 2026-11-12) Fase 8: estructural del conducto
# (INF-3.3.5). Un fundamento por paso. El reparto de fuentes esta escrito en
# el bloque T-5 de `citas.py`: el HL-93 y su IM son del Manual de Puentes
# [N]; la distribucion a traves del relleno y el diseño de cada conducto, de
# la Seccion 12 de AASHTO LRFD [C], que el Manual no incorpora; la clase del
# tubo y el espesor minimo del TMC, del EG-2013 [N].
# ===========================================================================

CARGA_VIVA_ENTERRADA = _fundamento(
    id="F8.CARGA_VIVA",
    fase=F8,
    que_paso=("Carga viva HL-93 a la profundidad de la clave: presion "
              "vertical por la rueda distribuida a traves del relleno"),
    por_que=(
        "El conducto bajo la via recibe los ejes de los vehiculos atenuados "
        "por el relleno que tiene encima: cuanto menos relleno, mas presion. "
        "La norma de diseño de puentes manda llevar la carga de cada rueda "
        "como uniforme sobre un rectangulo que crece con la profundidad --el "
        "area de contacto del neumatico mas el relleno multiplicado por un "
        "factor de distribucion--, con UN carril cargado y su factor de "
        "presencia multiple cuando el trafico corre paralelo al vano, que "
        "es el caso de casi toda alcantarilla vial, y solo con los ejes del "
        "camion y del tandem de diseño. El incremento por carga dinamica de "
        "lo enterrado decrece con la profundidad y se anula a 8 pies. Con "
        "mas de 8 pies de relleno que ademas superan la luz, la carga viva "
        "se puede despreciar."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.3.6.1.2.6a#RELLENO",      # EXIGENCIA
           "AASHTO_LRFD_9.3.6.1.2.6a#EJES",
           "AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL",
           "AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE",
           "AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS",
           "AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO",
           "AASHTO_LRFD_9.T3.6.1.2.6a-1",
           "AASHTO_LRFD_9.3.6.1.2.6b#PL",
           "AASHTO_LRFD_9.C3.6.1.2.6b",
           "MP.2.4.3.2.2.2",
           "MP.2.4.3.2.2.3",
           "MP.2.4.3.2.2.5",
           "MP.2.4.3.2.2.6",
           "MP.2.4.3.3.2",
           "AASHTO_LRFD_9.12.11.2.1#LL"),
    que_pasa_si_no_se_hace=(
        "El conducto se verifica solo con el peso del relleno, que es lo "
        "que pasaba hasta T-5: el rotulo HL-93 aparecia en la memoria y la "
        "carga viva nunca entraba al tubo (INF-3.3.5). Con un metro de "
        "relleno la rueda distribuida es del orden del propio relleno."),
)

CARGA_TIERRA = _fundamento(
    id="F8.CARGA_TIERRA",
    fase=F8,
    que_paso=("Carga de tierra sobre el conducto: prisma de relleno y "
              "paquete estructural, con la interaccion suelo-estructura de "
              "su tipo"),
    por_que=(
        "El peso del relleno es la carga permanente del conducto. No pesa "
        "igual sobre todos: un tubo rigido atrae parte del relleno de los "
        "costados y recibe mas que su prisma --el factor de arqueo vertical "
        "de las instalaciones estandar, o el de interaccion suelo-estructura "
        "del marco, que crece con la altura de relleno y tiene tope--, y un "
        "tubo flexible se calcula con la presion de campo libre a la cota de "
        "su clave. El peso especifico del suelo no puede tomarse menor que "
        "un piso que fija la norma de diseño, y a falta de un ensayo el "
        "Manual de Puentes da el de un suelo compactado y el de una "
        "superficie de rodadura."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.10.2.1#VAF",            # EXIGENCIA
           "AASHTO_LRFD_9.12.10.2.1#PESO_MIN",
           "AASHTO_LRFD_9.12.10.2.2",
           "AASHTO_LRFD_9.C12.7.2.2",
           "AASHTO_LRFD_9.12.11.2.2.1",
           "MP.2.4.2.1#PESOS"),
    que_pasa_si_no_se_hace=(
        "La clase o el calibre se eligen contra una carga que no es la del "
        "punto: con el peso especifico que V7 adopta del lado bajo --el que "
        "es conservador para la flotacion-- el tubo quedaria cargado de "
        "menos."),
)

CLASE_CONCRETO = _fundamento(
    id="F8.CLASE_CONCRETO",
    fase=F8,
    que_paso=("Clase del tubo de concreto reforzado por el metodo indirecto: "
              "D-load requerida frente a la D-load de la clase"),
    por_que=(
        "La norma peruana de construccion manda que el proyecto indique la "
        "clase del tubo conforme a la norma de producto, y la norma de "
        "diseño da el procedimiento para elegirla: la carga de tierra, la "
        "del agua que lleva el tubo y la carga viva, cada una dividida por "
        "el factor de cama de su tipo de instalacion, se convierten en la "
        "carga de tres apoyos por metro de longitud y milimetro de diametro "
        "que el tubo tiene que resistir sin abrir una grieta de 0.3 mm. La "
        "clase que la cumple es la del punto, y el relleno con que esa clase "
        "deja de cumplir es el maximo admisible."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.10.4.3.1",               # EXIGENCIA
           "AASHTO_LRFD_9.12.10.4.3.1#TIPO1",
           "AASHTO_LRFD_9.12.10.4.3.1#DLOAD",
           "AASHTO_LRFD_9.12.10.4.3.2a",
           "AASHTO_LRFD_9.12.10.4.3.2c",
           "AASHTO_LRFD_9.12.10.2.3",
           "AASHTO_M170M.T2#DLOAD",
           "AASHTO_M170M.T1#DIAMETROS",
           "AASHTO_LRFD_9.T12.10.2.1-1",
           "AASHTO_LRFD_9.T12.10.2.1-1#PROCTOR",
           "EG2013.506.02#CLASE",
           "EG2013.506.07",
           "EG2013.506.10",
           "EG2013.T205-01",
           "EG2013.205.12#COMPACTACION"),
    que_pasa_si_no_se_hace=(
        "El expediente especifica un tubo de concreto sin clase, que es lo "
        "que la norma peruana prohibe dejar sin indicar, y la clase se "
        "decide en obra con un catalogo."),
)

TMC_AREA_Y_PANDEO = _fundamento(
    id="F8.TMC_AREA",
    fase=F8,
    que_paso=("Tuberia metalica corrugada: empuje de anillo mayorado frente "
              "a la resistencia de la pared, con el pandeo"),
    por_que=(
        "Un tubo flexible trabaja como un anillo comprimido: la presion de "
        "la clave por el radio es el empuje que la pared tiene que resistir. "
        "La norma de diseño lo verifica en resistencia, con las cargas "
        "mayoradas y el factor de resistencia de la pared, y exige "
        "comprobar el pandeo: si la tension critica de pandeo queda por "
        "debajo de la fluencia, manda ella. La plancha que lo cumple es el "
        "calibre del punto, y no puede ser mas delgada que el minimo que la "
        "norma peruana de construccion fija por diametro."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.7.2.2",                  # EXIGENCIA
           "AASHTO_LRFD_9.C12.7.2.2",
           "AASHTO_LRFD_9.12.7.2.3",
           "AASHTO_LRFD_9.12.7.2.4",
           "AASHTO_LRFD_9.12.5.4",
           "AASHTO_LRFD_9.1.3.5",
           "AASHTO_LRFD_9.12.5.5",
           "AASHTO_LRFD_9.TA12-9",
           "MP.2.3.2.5",
           "ASTM_A796.9.1",
           "ASTM_A796.T5",
           "EG2013.T507-01"),
    que_pasa_si_no_se_hace=(
        "El catalogo ofrece la plancha adoptada en todos los diametros de "
        "su corrugacion sin que nadie haya comprobado que resiste el relleno "
        "y el trafico del punto, ni que cumple el espesor minimo peruano."),
)

TMC_COSTURA = _fundamento(
    id="F8.TMC_COSTURA",
    fase=F8,
    que_paso="Tuberia metalica corrugada: resistencia de la costura longitudinal",
    por_que=(
        "En la tuberia armada con costura longitudinal --remachada, soldada "
        "por puntos o empernada-- el empuje del anillo pasa por la costura, "
        "y la norma de diseño exige que su resistencia mayorada lo "
        "desarrolle. La tuberia helicoidal con costura engargolada o soldada "
        "no tiene costura longitudinal y el criterio no aplica."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.7.2.5",                  # EXIGENCIA
           "ASTM_A796.8.1.3.1",
           "ASTM_A796.T5",
           "AASHTO_LRFD_9.12.5.5",
           "EG2013.507.02#EMPERNADA"),
    que_pasa_si_no_se_hace=(
        "Una tuberia anular se especifica sin saber si su costura aguanta el "
        "empuje que la pared si aguanta: falla por la union."),
)

TMC_FLEXIBILIDAD = _fundamento(
    id="F8.TMC_FF",
    fase=F8,
    que_paso="Tuberia metalica corrugada: factor de flexibilidad de manejo e instalacion",
    por_que=(
        "Antes de que el relleno la sostenga, la tuberia tiene que tener "
        "rigidez para el transporte, el manejo y la compactacion del relleno "
        "lateral sin perder la forma. La norma de diseño la mide con el "
        "factor de flexibilidad --el cuadrado del diametro sobre la rigidez "
        "de la pared-- y le pone un tope por material y profundidad de "
        "corrugacion. Es una exigencia constructiva, no un estado limite de "
        "servicio."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.5.6.1#FF",               # EXIGENCIA
           "ASTM_A796.10.3"),
    que_pasa_si_no_se_hace=(
        "Una plancha delgada en un diametro grande --2.01 mm desde 1.39 m "
        "con la corrugacion de 68 por 13-- se deforma al compactar el "
        "relleno: lo que el auditor de T-4 midio (ficha T4-08)."),
)

TMC_CONTRASTE_ASD = _fundamento(
    id="F8.TMC_ASD",
    fase=F8,
    que_paso=("Tuberia metalica corrugada: contraste por tensiones admisibles "
              "(ASTM A796, num. 8), que no rige"),
    por_que=(
        "La practica de diseño de la tuberia de acero corrugado admite dos "
        "metodos, tensiones admisibles o factores de carga y resistencia. "
        "El proyecto verifica por factores de carga y resistencia de "
        "extremo a extremo y no mezcla los dos en una comprobacion; el area "
        "requerida por tensiones admisibles se imprime al lado como "
        "contraste, porque es el procedimiento que siguen los expedientes y "
        "manuales de fabricantes con que la tesis se compara."),
    verbo=Verbo.PERMITE,
    citas=("ASTM_A796.7.1",                           # PERMISO
           "ASTM_A796.8.1.1.2#SELECCION",
           "ASTM_A796.6.2.2.1"),
    que_pasa_si_no_se_hace=(
        "La memoria no se puede comparar con la de un expediente que diseño "
        "por tensiones admisibles, y la diferencia entre los dos metodos "
        "queda sin explicar."),
)

HDPE_EMPUJE = _fundamento(
    id="F8.HDPE_EMPUJE",
    fase=F8,
    que_paso=("Tuberia de polietileno corrugado: deformacion de compresion "
              "por el empuje frente a su limite"),
    por_que=(
        "En el termoplastico el limite no es una tension sino una "
        "deformacion: el empuje del anillo, dividido por el area efectiva "
        "del perfil y el modulo del material para la duracion de la carga, "
        "no puede pasar la deformacion de compresion mayorada que la norma "
        "de diseño fija para el polietileno. La carga sale del prisma de "
        "suelo corregido por el arqueo vertical, que depende de la rigidez "
        "relativa del suelo y del tubo, y del factor de instalacion. El area "
        "efectiva descuenta el pandeo local de los elementos del perfil, y "
        "sin la geometria del perfil se puede obtener del ensayo de "
        "compresion que la norma de producto exige al fabricante."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.12.3.10.1d",             # EXIGENCIA
           "AASHTO_LRFD_9.12.12.3.10.1c#EP",
           "AASHTO_LRFD_9.12.12.3.5",
           "AASHTO_LRFD_9.T12.12.3.3-1",
           "AASHTO_LRFD_9.T12.12.3.5-1",
           "AASHTO_LRFD_9.12.12.3.10.1b#STUB",
           "AASHTO_M294_TRAD.7.7",
           "AASHTO_LRFD_9.TA12-11",
           "AASHTO_LRFD_9.12.12.3.2",
           "AASHTO_LRFD_9.C12.12.3.2",
           "AASHTO_LRFD_9.T12.12.3.5-2",
           "AASHTO_LRFD_9.12.5.4",
           "AASHTO_LRFD_9.1.3.5",
           "MP.2.3.2.5",
           "EG2013.508.02#GRANULAR",
           "EG2013.T301-01",
           "EG2013.508.07#COMPACTACION"),
    que_pasa_si_no_se_hace=(
        "El HDPE se acepta por hidraulica y por recubrimiento sin que nadie "
        "verifique su pared: es el material mas sensible al relleno de los "
        "tres."),
)

HDPE_PANDEO = _fundamento(
    id="F8.HDPE_PANDEO",
    fase=F8,
    que_paso="Tuberia de polietileno corrugado: pandeo general del anillo",
    por_que=(
        "Un anillo flexible rodeado de suelo puede pandear como conjunto "
        "antes de que la pared alcance su deformacion limite. La norma de "
        "diseño da la deformacion de pandeo general en funcion de la "
        "rigidez del perfil y del modulo del suelo, y exige que la "
        "deformacion del empuje no pase de esa capacidad por su factor de "
        "resistencia, que es bajo porque el pandeo colapsa el conducto."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.12.3.10.1e",             # EXIGENCIA
           "AASHTO_LRFD_9.12.12.3.3#PANDEO",          # EXIGENCIA
           "AASHTO_LRFD_9.12.12.3.10.1c#EP",
           "AASHTO_LRFD_9.T12.12.3.5-1",
           "AASHTO_LRFD_9.12.5.5"),
    que_pasa_si_no_se_hace=(
        "El tubo cumple la deformacion de su pared y aun asi colapsa por "
        "inestabilidad con un relleno de baja rigidez."),
)

HDPE_DEFLEXION = _fundamento(
    id="F8.HDPE_DEFLEXION",
    fase=F8,
    que_paso="Tuberia de polietileno corrugado: deflexion vertical de servicio",
    por_que=(
        "La norma de diseño exige que la deflexion total del tubo, por "
        "flexion del anillo mas acortamiento circunferencial, no pase de la "
        "admisible, y su comentario pone la admisible en el cinco por ciento "
        "del diametro como limite generalmente apropiado."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.12.2.2",                 # EXIGENCIA
           "AASHTO_LRFD_9.C12.12.2.2"),
    que_pasa_si_no_se_hace=(
        "Un tubo ovalizado reduce su seccion hidraulica y abre sus juntas: "
        "es la falla de servicio tipica del termoplastico mal rellenado."),
)

# --- T-5 (cierre) --- El factor de flexibilidad del termoplastico, que la
# FASE A no verificaba (auditoria): 12.5.3 lo enumera entre los estados
# limite de resistencia del tubo termoplastico («Flexibility limit»).
HDPE_FLEXIBILIDAD = _fundamento(
    id="F8.HDPE_FF",
    fase=F8,
    que_paso=("Tuberia de polietileno corrugado: factor de flexibilidad para "
              "el manejo y la instalacion"),
    por_que=(
        "Un tubo demasiado flexible se deforma al manipularlo y al compactar "
        "el relleno a sus costados antes de que el suelo lo sostenga. La "
        "norma de diseño limita por eso el factor de flexibilidad del tubo "
        "termoplastico, que calcula con el diametro, el modulo de "
        "elasticidad inicial y el momento de inercia del perfil."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.5.6.3",                  # EXIGENCIA
           "AASHTO_LRFD_9.12.12.3.6",                 # EXIGENCIA
           "AASHTO_LRFD_9.TA12-11"),
    que_pasa_si_no_se_hace=(
        "Se adopta un perfil que resiste el empuje ya enterrado pero que no "
        "llega a ese estado: se ovaliza durante la instalacion."),
)

MARCO_DEMANDA = _fundamento(
    id="F8.MARCO_DEMANDA",
    fase=F8,
    que_paso=("Marco de concreto: cargas sobre la losa superior y "
              "momento de referencia; el diseño de la seccion se difiere"),
    por_que=(
        "Para el marco no hay clase de catalogo: la losa y los muros se "
        "diseñan como elementos de concreto armado con las cargas de la "
        "Seccion 12 --el relleno con su factor de interaccion, que tiene "
        "tope con relleno compactado a los costados, y la rueda distribuida "
        "a traves del relleno--. La hoja de ruta deja el diseño de la "
        "seccion del marco fuera del alcance de este programa: aqui se "
        "calcula la demanda que ese diseño tiene que cubrir."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.11.2.2.1",               # EXIGENCIA
           "AASHTO_LRFD_9.12.11.2.1#LL"),
    que_pasa_si_no_se_hace=(
        "El marco llega al expediente sin la carga con que hay que "
        "diseñarlo, y la memoria dice «diferido» sin decir que se difiere."),
)


# --- T-3 --- (cadena T, INF-0.4) Los tres pasos que 7.B emite para un paso
# de canal: la geometria del marco, el empalme de la salida con el fondo del
# canal (VC2) y el remanso aguas arriba. Ninguno lleva verbo de obligacion:
# ninguna fuente de normas/ manda verificar un empalme ni medir un remanso
# en un cruce de canal; lo que la fuente hace es TIPIFICAR el cruce (Lamina
# N 03) y DEFINIR la herramienta (Manning para canales abiertos). Lo que se
# verifica y como es lectura del proyecto, y el umbral de VC2 lleva su
# analogia en `aplicacion`.

MARCO = _fundamento(
    id="F7.MARCO",
    fase=F7,
    que_paso=("Geometria del marco adoptado: dimensiones exteriores, cotas "
              "de fondo y de clave, relleno sobre la losa"),
    por_que=(
        "Un marco no se describe con su luz interior: la cota de la clave "
        "exterior es la que gobierna la cobertura de 7.A y la subpresion de "
        "V7, el ancho y el canto exteriores son los que desplazan agua y "
        "cargan relleno, y el relleno sobre la losa es la altura que la "
        "verificacion estructural del expediente va a cargar. La tipologia la "
        "fija el Manual -- el marco de concreto en cruce de canal de riego "
        "de la Lamina N 03, que el num. 4.1.1.3.4 a) permite ubicar al nivel "
        "que el cruce requiera -- sin acotar ninguna dimension; las dimensiones salen de la seccion "
        "adoptada y del espesor que el proyecto declara."),
    # La E.060 entra por el espesor que la geometria usa (piso adoptado por
    # analogia en 'espesor_pared_cajon'); el verbo lo sostiene la Lamina.
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.LAMINA_03", "MC_HHD.4.1.1.3.4a#NIVELES", "E060.14.5.3.2"),
    que_pasa_si_no_se_hace=(
        "La geometria exterior del marco quedaria repartida entre V7, 7.A y "
        "la Fase 8, cada uno con su propia cuenta de la clave, y la "
        "memoria no diria en ningun sitio cuanto mide la obra por fuera ni "
        "cuanto relleno lleva encima."),
)

EMPALME_CANAL = _fundamento(
    id="F7.EMPALME_CANAL",
    fase=F7,
    que_paso=("Empalme de la salida de un paso de canal con el fondo del "
              "canal aguas abajo (VC2, aviso)"),
    por_que=(
        "En un paso de canal el conducto CONTINUA el canal: el Manual lo "
        "tipifica con el marco entre los dos bordes del canal, y en ese caso "
        "el fondo del receptor es el mismo canal aguas abajo. Si la cota "
        "de salida que resulta de la entrada y la pendiente no cae sobre ese "
        "fondo, la obra deja un escalon: hacia arriba, el agua cae sobre el "
        "lecho del canal; hacia abajo, la salida queda enterrada y se "
        "colmata. G2 solo mira que la salida no quede bajo el fondo; VC2 "
        "mira las dos caras del empalme. No lo arregla ninguna seccion: lo "
        "fijan la cota de entrada y la pendiente, y por eso avisa en vez de "
        "detener."),
    # Las dos del EG-2013 sostienen la TOLERANCIA por analogia (el umbral
    # lo dice en `aplicacion`); el verbo lo sostiene la Lamina.
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.LAMINA_03", "EG2013.503.11g#COTAS", "EG2013.501.07"),
    que_pasa_si_no_se_hace=(
        "Un escalon de varios decimetros en el fondo de un canal pasaria por "
        "bueno porque G2 lo acepta en un sentido -- §16.17 de "
        "docs/ruta_familia_c.md midio uno de 7 cm hacia arriba que G2 no "
        "veia --, y con la cota de entrada adoptada del terreno el escalon "
        "puede ser de mas de medio metro sin que nada lo diga."),
)

REMANSO_CANAL = _fundamento(
    id="F7.REMANSO_CANAL",
    fase=F7,
    que_paso=("Sobreelevacion de la lamina del canal en el cruce y longitud "
              "minima del remanso aguas arriba (aviso)"),
    por_que=(
        "La Sec. 2.3 de la hoja de ruta prohibe que un cruce altere la "
        "rasante hidraulica del canal, y VC1 solo mide el nivel contra la "
        "coronacion EN EL CRUCE. Cuanto levanta la obra la lamina se mide "
        "contra la que el canal tendria sin ella, su tirante normal, que "
        "sale de Manning sobre la seccion medida del canal -- la formula que "
        "el Manual da para canales abiertos y tuberias --. Desde el cruce, el "
        "embalse se extiende aguas arriba: la lamina horizontal del embalse "
        "corta la lamina normal a sobreelevacion / S, y el perfil real llega "
        "mas lejos, de modo que esa distancia es una cota inferior. No hay "
        "umbral en ninguna fuente: el numero se publica para que el "
        "proyecto lo contraste con la coronacion del canal aguas arriba."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",),
    que_pasa_si_no_se_hace=(
        "Un cruce que cumple VC1 con holgura puede haber levantado la lamina "
        "del canal varios decimetros y embalsado decenas de metros aguas "
        "arriba, donde la coronacion puede ser mas baja, sin que la memoria "
        "lo diga: es el hueco 2 de §13 de docs/ruta_familia_c.md."),
)


# ===========================================================================
# --- T-9 --- Fase 10 - La longitud por capacidad de la cuneta y la
# verificacion del espaciamiento por tramo (M10)
# ===========================================================================
# Hasta T-9 la Fase 10 tenia UN paso (F10.CUNETA) y una frase en la memoria:
# el espaciamiento maximo como minimo de dos longitudes, una de ellas
# declarada, y un veredicto «cumple» que no podia fallar (INF-5.1.12). Ahora
# la longitud por capacidad se CALCULA en tres pasos y el espaciamiento
# ADOPTADO -- la distancia entre dos alivios del CSV -- se verifica.

CAPACIDAD_CUNETA = _fundamento(
    id="F10.CAPACIDAD",
    fase=F10,
    que_paso=("Capacidad admisible de la cuneta: el menor del caudal con la "
              "cuneta llena y del que produce la velocidad limite admisible"),
    por_que=(
        "La longitud de cuneta que se puede recorrer sin aliviar depende de "
        "cuanta agua cabe en ella. El Manual define esa capacidad con DOS "
        "caudales: el que pasa con la cuneta llena, que es un limite de "
        "seccion, y el que alcanza la velocidad limite de su revestimiento, "
        "que es un limite de erosion. Rige el menor: una cuneta que no se "
        "desborda pero se erosiona tampoco conduce el agua."),
    verbo=Verbo.DEFINE,
    # Correcciones de T-9: el n sale de la Tabla Nº 32 con la Nº 09 como
    # alternativa declarada (dudoso 2), y el talud interior se contrasta con
    # la Tabla 304.12 (H5).
    citas=("MC_HHD.4.1.2.1a", "MC_HHD.4.1.2.1a#MANNING",
           "MC_HHD.4.1.2.1a#VELOCIDAD", "MC_HHD.4.1.2.1#T32",
           "MC_HHD.4.1.2.1#T09", "MC_HHD.4.1.2.1#T304_12",
           "MC_HHD.4.1.2.1e"),
    que_pasa_si_no_se_hace=(
        "La longitud por capacidad seguiria siendo un dato declarado sin "
        "procedimiento, y la Fase 10 no podria decir si el limite de 200 m "
        "lo alcanza la cuneta o la excede."),
)

APORTE_CUNETA = _fundamento(
    id="F10.APORTE",
    fase=F10,
    que_paso=("Caudal aportante por metro de cuneta: escorrentia especifica "
              "del area tributaria por su ancho"),
    por_que=(
        "El caudal de aporte de una cuneta es el del area aportante que "
        "corresponde a su longitud (metodo racional). Con la misma "
        "escorrentia por unidad de area, ese area crece con la longitud: el "
        "caudal por metro de cuneta es la escorrentia especifica por el "
        "ancho de la faja que drena a ella, y es lo que convierte una "
        "capacidad en una longitud."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.2.1b", "MC_HHD.4.1.2a"),
    que_pasa_si_no_se_hace=(
        "No habria con que dividir la capacidad: la longitud por capacidad "
        "no se podria calcular."),
)

LONGITUD_HIDRAULICA = _fundamento(
    id="F10.L_HIDRAULICO",
    fase=F10,
    que_paso=("Longitud por capacidad de la cuneta: a partir de ella el "
              "caudal aportante supera la capacidad admisible"),
    por_que=(
        "Es la condicion del Manual escrita al reves: la cuneta esta bien "
        "dimensionada mientras su capacidad supere al caudal de aporte, y el "
        "caudal de aporte crece con la longitud. La longitud a la que los "
        "dos se igualan es la mas larga que la cuneta puede recorrer sin "
        "alivio, y entra al espaciamiento junto al limite normativo."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.2.1a", "MC_HHD.4.1.2.1b", "DG2018.304.11"),
    que_pasa_si_no_se_hace=(
        "El espaciamiento entre alivios lo fijaria solo el limite normativo, "
        "aunque la cuneta se desbordara o se erosionara antes."),
)

TRAMO_ALIVIO = _fundamento(
    id="F10.TRAMO",
    fase=F10,
    que_paso=("Verificacion VB1: espaciamiento adoptado entre alcantarillas "
              "de alivio contra el espaciamiento maximo"),
    # CORREGIDO TRAS LA AUDITORIA DE T-9 (H10, dudoso 5). Decia que un tramo
    # largo «recorre mas de lo que el Manual admite», con un umbral de 200 m
    # que la fuente solo RECOMIENDA. El verbo sigue siendo OBLIGA porque la
    # cifra de 250 m es exigencia («será de 250m como máximo»); lo que la 200
    # tiene de duro lo pone el proyecto, y el `por_que` lo dice.
    por_que=(
        "El espaciamiento maximo no verifica nada por si solo: es un limite. "
        "Lo que se verifica es la distancia que el proyecto DEJO entre la "
        "alcantarilla de alivio y el extremo de su tramo de cuneta, y esa "
        "distancia sale de las progresivas de las obras. El Manual EXIGE un "
        "recorrido maximo de 250 m en region seca o poco lluviosa y "
        "RECOMIENDA reducirlo a 200 m en region muy lluviosa; el proyecto "
        "adopta los 200 m como umbral duro, y la longitud por capacidad de "
        "la cuneta puede acortarlo. Si el tramo supera el menor de los dos, "
        "el remedio es otro alivio o una cuneta de mas capacidad."),
    verbo=Verbo.OBLIGA,
    # Correcciones de T-9 (decision C): el extremo del tramo puede ser una
    # obra de drenaje transversal, por el DG-2018, y el Manual nombra solo
    # las alcantarillas de alivio como desague.
    citas=("MC_HHD.4.1.2.1d", "DG2018.304.11#DESAGUE",
           "MC_HHD.4.1.2.1d#ALIVIO"),
    que_pasa_si_no_se_hace=(
        "Es lo que pasaba hasta T-9 (INF-5.1.12): la Fase 10 devolvia "
        "«cumple» por construccion, porque comparaba el minimo de dos "
        "limites con uno de ellos, y ningun tramo de cuneta demasiado largo "
        "podia salir en la memoria."),
)

# --- Correcciones de la auditoria de T-9 (H1). La condicion LITERAL del
# Manual: la capacidad de la cuneta contra el caudal de aporte. Es VB2, y no
# necesita el tramo: basta el caudal del punto y la capacidad.
APORTE_FRENTE_A_CAPACIDAD = _fundamento(
    id="F10.APORTE_CAPACIDAD",
    fase=F10,
    que_paso=("Verificacion VB2: el caudal de aporte del alivio contra la "
              "capacidad admisible de la cuneta"),
    por_que=(
        "El Manual da la cuneta por bien dimensionada solo si su capacidad "
        "supera al caudal de aporte, y si no manda volver atras y elegir "
        "otra seccion. En la Familia B el caudal del punto es, por "
        "contrato, el de la cuneta que descarga en el alivio: compararlo con "
        "la capacidad es la condicion del Manual escrita sobre los datos del "
        "punto. Una cuneta que no conduce su aporte desborda sobre la via "
        "antes de llegar al alivio, cualquiera sea el espaciamiento."),
    verbo=Verbo.OBLIGA,
    citas=("MC_HHD.4.1.2.1a#CONDICION", "MC_HHD.4.1.2.1a",
           "MC_HHD.4.1.2.1b"),
    que_pasa_si_no_se_hace=(
        "Es el hallazgo H1 de la auditoria de T-9: con un area tributaria "
        "que no era la faja del tramo, la longitud por capacidad salia "
        "cientos de veces mayor que el tramo y VB1 cumplia con un aporte un "
        "82 % mayor que la capacidad de la cuneta."),
)


# ===========================================================================
# --- T-7a --- Fase 9: el cabezal POR PUNTO (geometria y aleros)
# ===========================================================================
# Siete fundamentos para los pasos de `M9.predimensionar_cabezal`,
# `M9.cabezal_del_punto` y las verificaciones CB1 a CB7.
# Ninguno afirma que una fuente fije una dimension que la fuente no fija: el
# verbo lo sostiene la cita que SI la fija (E.050 26.2, AASHTO 12.6.5, E.060
# 22.7.4, HDS-5 3.3.5), y lo que es regla de practica lo dice el `por_que`.

EMBOCADURA_CABEZAL = _fundamento(
    id="F9.EMBOCADURA",
    fase=F9,
    que_paso=("Embocadura del punto: cabezal con aleros o recto, angulo de "
              "los aleros y lo que la Tabla C.2 del HDS-5 hace con ellos"),
    por_que=(
        "La embocadura no es un detalle de acabado: en un marco, la fila de "
        "perdida de entrada y la carta de control de entrada cambian con el "
        "angulo de los aleros, y la Tabla C.2 agrupa sus filas por bandas de "
        "ese angulo medido con el barril. En un tubo la misma tabla pone el "
        "cabezal y el cabezal con aleros en una sola fila, de modo que el "
        "angulo no mueve el calculo hidraulico. La Lamina 02-A del Manual "
        "dibuja las salidas con aleros y sin ellos, sin acotar el angulo: "
        "cual lleva esta obra y con que angulo es una eleccion del "
        "proyecto, y se imprime junto con lo que la fuente hace con ella."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.TC.2", "MC_HHD.LAMINA_02A"),
    que_pasa_si_no_se_hace=(
        "El control de entrada y el de salida de un marco podrian hablar de "
        "una embocadura distinta de la que el cabezal dibuja, y nada lo "
        "diria."),
)

CORONACION_CABEZAL = _fundamento(
    id="F9.CORONACION",
    fase=F9,
    que_paso=("Coronacion y altura del cabezal: sobre la clave exterior y "
              "sobre el nivel de agua del extremo"),
    por_que=(
        "Elegida la seccion, la fuente manda encajarla en el terraplen y "
        "dimensionar los cabezales y los aleros. El muro de cabecera retiene "
        "el relleno que cubre la clave exterior del conducto y contiene el "
        "agua que se levanta contra el en la entrada (la carga de diseño) y "
        "en la salida (el tirante o el nivel del receptor): su coronacion es "
        "la mayor de esas dos cotas, cada una con lo que el proyecto le "
        "suma. Lo que se suma -- relleno sobre la clave, bordillo, "
        "resguardo -- es regla de predimensionamiento del proyecto, no de "
        "la fuente."),
    verbo=Verbo.OBLIGA,
    citas=("HDS5_3ED.3.3.5#ENCAJE",),
    que_pasa_si_no_se_hace=(
        "El relleno sobre el conducto se derramaria por encima del muro, o "
        "el agua de la entrada lo rebasaria, sin que la memoria lo hubiera "
        "comparado."),
)

DESPLANTE_CABEZAL = _fundamento(
    id="F9.DESPLANTE",
    fase=F9,
    que_paso=("Profundidad de desplante del cabezal: minimo de E.050 y, a "
              "la salida, bajo la socavacion"),
    por_que=(
        "La zapata del cabezal se apoya en el borde del cauce, donde el agua "
        "socava. E.050 fija, para las cimentaciones de las edificaciones, una "
        "profundidad minima medida desde la superficie del terreno, y el "
        "proyecto la aplica al cabezal por analogia con el muro de "
        "contencion que esa norma remite a su Capitulo IV; AASHTO exige, "
        "para las estructuras enterradas, que sus zapatas queden bajo la "
        "socavacion maxima prevista con un margen, y el proyecto lee que la "
        "del cabezal es una de ellas; HEC-14 recomienda que el cabezal baje "
        "hasta esa profundidad. El desplante es el mas profundo de los dos "
        "limites, y el de la socavacion solo existe donde la Fase 6 entrega "
        "una profundidad."),
    verbo=Verbo.OBLIGA,
    citas=("E050.26.2#PROFUNDIDAD", "AASHTO_LRFD_9.12.6.5#ZAPATAS",
           "AASHTO_LRFD_9.10.6.1.2#DESPLANTE", "HEC14.5.1.3#CABEZAL"),
    que_pasa_si_no_se_hace=(
        "La socavacion a la salida descalzaria el cabezal, y con el el "
        "extremo del conducto, en la primera avenida de diseño."),
)

DIMENSIONES_CABEZAL = _fundamento(
    id="F9.DIMENSIONES",
    fase=F9,
    que_paso=("Predimensionamiento del cabezal: tipo, espesores, zapata y "
              "longitud del muro"),
    por_que=(
        "Las laminas del Manual dibujan el cabezal y acotan sus dimensiones "
        "con letras, sin tabla de valores: la geometria es del proyecto. Se "
        "propone con reglas de practica declaradas, una por dimension, y "
        "cada una se imprime con su origen -- propuesta por regla, "
        "declarada por el proyectista o derivada de una declarada --. Donde "
        "una norma fija un minimo con su numero, el minimo se aplica y una "
        "dimension declarada se contrasta con el: el espesor de la zapata de "
        "concreto simple del cabezal de gravedad, y, por analogia, la altura "
        "de la zapata armada sobre su refuerzo. La estabilidad de lo "
        "propuesto no se juzga aqui."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.LAMINA_02A", "E060.22.7.4#ZAPATA", "E060.15.7#PERALTE",
           "E060.22.10.2#CICLOPEO"),
    que_pasa_si_no_se_hace=(
        "El cabezal saldria dimensionado sin que nadie supiera de donde "
        "salio cada medida, que es lo que este expediente prohibe."),
)

ALEROS_CABEZAL = _fundamento(
    id="F9.ALEROS",
    fase=F9,
    que_paso="Aleros: angulo, longitud, alturas inicial y final, espesor",
    por_que=(
        "Los aleros contienen el talud del terraplen a los lados de la boca "
        "y lo alejan del relleno que rodea al conducto; AASHTO pide "
        "extenderlos lo bastante para protegerlo, sin dar una longitud. La "
        "longitud sale de la geometria: el alero arranca a la altura del "
        "cabezal y sigue al talud hasta que este baja a la altura final "
        "declarada. El talud baja perpendicular a la via; el angulo del "
        "alero se mide con la prolongacion de la pared del barril, y con "
        "esviaje los dos aleros de un mismo cabezal forman angulos distintos "
        "con la bajada del talud y no miden lo mismo."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.6.5#ALEROS", "MC_HHD.LAMINA_02A",
           "HDS5_3ED.SIMBOLOS#THETA_W"),
    que_pasa_si_no_se_hace=(
        "El talud a los lados de la boca quedaria sin contencion, y su "
        "erosion es la que descalza el cabezal."),
)

LOSA_CABEZAL = _fundamento(
    id="F9.LOSA",
    fase=F9,
    que_paso="Losa de entrega y dentellon delante del cabezal",
    por_que=(
        "Delante del cabezal las laminas del Manual dibujan una losa y, en "
        "su borde, una uña; AASHTO exige, sobre depositos erosionables, una "
        "pantalla que baje por debajo de la socavacion maxima prevista. La "
        "unica lamina que acota un dentellon es la del aliviadero, que mide "
        "su profundidad minima desde el terreno junto a el, y esa "
        "profundidad se aplica aqui por analogia, desde el mismo terreno que "
        "el desplante del cabezal; a la salida, si la socavacion es mayor, "
        "el dentellon baja bajo ella."),
    verbo=Verbo.OBLIGA,
    citas=("AASHTO_LRFD_9.12.6.5#DENTELLON", "MC_HHD.LAMINA_04#DENTELLON",
           "MC_HHD.LAMINA_02"),
    que_pasa_si_no_se_hace=(
        "El borde de la losa quedaria colgado sobre la hoya, y la erosion "
        "avanzaria por debajo hacia el cabezal."),
)

LONGITUD_ENTRE_CABEZALES = _fundamento(
    id="F9.LONGITUD",
    fase=F9,
    que_paso=("Longitud entre cabezales con el talud muriendo en el relleno "
              "que retienen, y longitud de metrado del barril"),
    por_que=(
        "Con la coronacion de los dos cabezales fijada, el talud ya no muere "
        "en el fondo ni en la clave sino en el relleno que cada muro "
        "retiene, contra su cara interior, y la longitud del barril entre "
        "cabezales queda cerrada; el barril atraviesa ademas los dos muros, "
        "y su longitud de metrado los suma. La fuente pide que quede cerca "
        "de la aproximada y no da tolerancia: las dos se imprimen."),
    verbo=Verbo.OBLIGA,
    citas=("HDS5_3ED.3.3.5#ENCAJE", "HDS5_3ED.3.1.4#LONGITUD"),
    que_pasa_si_no_se_hace=(
        "El barril se mediria y se pagaria con una longitud que no es la "
        "que los cabezales dejan."),
)
