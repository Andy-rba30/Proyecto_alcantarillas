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


def _fundamento(**kw) -> Fundamento:
    f = Fundamento(**kw)
    if f.id in FUNDAMENTOS:
        raise ValueError(f"fundamento duplicado: {f.id}")
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
    citas=("MC_HHD.4.1.1.3.1", "MC_HHD.4.1.1.5.1"),
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
    que_paso=("Tirante normal y velocidad en el conducto, por Manning, "
              "resueltos con las DOS rugosidades del rango de la Tabla N 09"),
    por_que=(
        "La rugosidad de un conducto no es un numero: la Tabla N 09 da un "
        "rango por material, y el rango no es incertidumbre de medicion sino "
        "el estado real de la superficie a lo largo de la vida de la obra. "
        "Resolver con un solo n obliga a elegir cual, y esa eleccion cambia de "
        "signo segun que se verifique: contra un TECHO de velocidad el extremo "
        "conservador es el n minimo --la estimacion alta-- y contra un PISO es "
        "el n maximo --la baja--. Por eso el calculo resuelve la seccion dos "
        "veces y cada verificacion consume la rama que la deja del lado "
        "seguro, en vez de que una sola rama pretenda servir para las dos."),
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
    citas=("HDS5_3ED.A.2", "HDS5_3ED.3.1.4#K"),
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
        "proyecto la evalua punto por punto en vez de suponerla cumplida."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.3.3#HO", "HDS5_3ED.3.3.3#HO_SUMERGIDA",
           "HDS5_3ED.3.3.3#HO_1_2D"),
    que_pasa_si_no_se_hace=(
        "Aplicar la aproximacion fuera de su rango sin decirlo: el HW de "
        "control de salida saldria de una formula que su propia fuente "
        "desautoriza para ese caso, y nadie se enteraria (NOR-HDS-05)."),
)


# ===========================================================================
# Fase 5 - Verificaciones
# ===========================================================================

V1 = _fundamento(
    id="F5.V1",
    fase=F5,
    que_paso="V1 - Borde libre: y/D <= 0.75",
    por_que=(
        "Una alcantarilla que trabaja a seccion llena deja de comportarse como "
        "un canal y pasa a comportarse como un conducto a presion: la "
        "capacidad se vuelve sensible a la entrada, el aire atrapado pulsa y "
        "cualquier obstruccion parcial embalsa aguas arriba. El borde libre es "
        "el margen que mantiene el flujo en regimen libre. El Manual lo "
        "escribe como el 25 % de la altura de la estructura; el 0.75 es su "
        "complemento aritmetico, no una cifra impresa."),
    verbo=Verbo.RECOMIENDA,
    citas=("MC_HHD.4.1.1.3.7b",),
    que_pasa_si_no_se_hace=(
        "El diseno aceptaria conductos trabajando a seccion llena o casi "
        "llena, donde el modelo de Manning con que se dimensionaron ya no "
        "describe el flujo."),
)

V2 = _fundamento(
    id="F5.V2",
    fase=F5,
    que_paso="V2 - Velocidad minima de autolimpieza: V >= 0.25 m/s",
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

V7 = _fundamento(
    id="F5.V7",
    fase=F5,
    que_paso="V7 - Flotacion del conducto vacio bajo el nivel freatico",
    por_que=(
        "Un conducto vacio bajo el nivel freatico es un flotador: la "
        "subpresion sobre su superficie exterior puede superar el peso propio "
        "mas el del relleno que lo cubre y levantarlo. En el Bajo Piura, con "
        "NF somero y arenas saturadas, no es un caso de laboratorio. La "
        "verificacion se plantea como equilibrio de factores de carga LRFD "
        "--las acciones que estabilizan minoradas, la que desestabiliza "
        "mayorada--, no como un factor de seguridad global, porque el marco "
        "adoptado por el expediente es LRFD de extremo a extremo."),
    verbo=Verbo.OBLIGA,
    citas=("MP.T2.4.5.3.1-1", "MP.T2.4.5.3.1-2"),
    que_pasa_si_no_se_hace=(
        "El conducto se dimensionaria solo por capacidad hidraulica y "
        "resistencia, que es el estado en que se pierden las alcantarillas de "
        "zonas con freatico alto: no fallan, flotan."),
)


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
     "El remanso dentro del derecho de via se apoya en la DG-2018 y en la Ley "
     "29338, y ninguna de las dos esta en `normas/`: son fuentes AUSENTES del "
     "registro. Sin PDF no hay `Verbatim` que verificar y sin cita no hay "
     "`Fundamento`.",
     "Incorporar la DG-2018 y la Ley 29338 a `normas/` y transcribir el "
     "numeral que acota la afectacion del derecho de via."),
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
     "atribucion de los topes a AASHTO M170 y ASTM A760, que tabulan mas.",
     "Nada: un catalogo no tiene numeral y no puede sostener un fundamento. "
     "Es lo que `DeCatalogo` existe para rotular."),
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
    citas=("MC_HHD.4.1.1.3.4a#MULTIPLES",),  # recomendacion
    que_pasa_si_no_se_hace=(
        "V6 sigue siendo trivialmente verdadera porque MD no sabe hacer "
        "multibarril -- que es una propiedad del PROGRAMA, no del diseno --, "
        "y el dia que sepa, la verificacion se vuelve falsa en silencio. Es "
        "la trampa que la regla vinculante #10 anticipa."),
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
        "cambiarle las constantes. El termino Ks*S sobreviviria en una "
        "ecuacion que no lo tiene, y con Ks = -0.5 RESTA carga: el HW saldria "
        "menor que el real y V4, V4b y el tamizado de 7.A se evaluarian del "
        "lado no conservador, sin que nada avise -- exactamente la forma de "
        "MAT-D10, pero por una via que ninguna guardia de signo detecta, "
        "porque el resultado sigue siendo positivo."),
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
        "El num. 4.1.1.3.6 prescribe Manning y define sus variables -- A "
        "'area de la seccion hidraulica', P 'perimetro mojado', R = A/P -- "
        "pero NO dice como se calcula A ni como se calcula P: eso depende de "
        "la forma, y ESTE numeral no fija ninguna. Ahi es donde entra la "
        "seccion como abstraccion: no es una generalizacion que el proyecto "
        "se inventa para que le quepan dos formas, es el hueco que el propio "
        "numeral deja al calculo. Un circulo lo llena por el angulo mojado y "
        "un rectangulo por B*y; el numeral es el mismo para los dos, y por "
        "eso el procedimiento tambien."),
    verbo=Verbo.DEFINE,
    citas=("MC_HHD.4.1.1.3.6",),    # DEFINICION -> sostiene DEFINE
    que_pasa_si_no_se_hace=(
        "Se escribe un segundo motor de calculo para la otra forma. Es "
        "SIS-A-07 y es el antipatron numero uno de la §12: dos motores, uno "
        "con casos patron y otro sin ellos, que empiezan iguales y divergen "
        "en la primera correccion que solo se aplique a uno."),
)

YC_RECT = _fundamento(
    id="F4.YC_RECT",
    fase=F4,
    que_paso="Tirante critico de la seccion, y la energia critica H_c",
    por_que=(
        "El tirante critico no se calcula porque interese por si mismo: se "
        "calcula porque DOS pasos posteriores lo consumen. La Forma 1 del "
        "control de entrada arranca de H_c/D, y el control de salida necesita "
        "h_o = max(TW, (d_c + D)/2). En la seccion circular no hay solucion "
        "cerrada y hace falta un segundo Brent; en la rectangular el ancho "
        "superficial es constante y la condicion de energia minima se "
        "despeja: y_c = (q^2/g)^(1/3) con q = Q/B. Que sea exacta no es un "
        "lujo de elegancia -- retira la clase entera de fallos de "
        "convergencia que LimiteNumericoError cubre en la circular "
        "(SIS-G-02), donde un Q diminuto lleva el resolutor a un angulo "
        "donde el area se cancela."),
    verbo=Verbo.DEFINE,
    citas=("HDS5_3ED.3.3.3#HO",     # sostiene DEFINE (definicion/aproximacion)
           "HDS5_3ED.A.2"),         # DEFINICION
    que_pasa_si_no_se_hace=(
        "El control de salida se queda sin h_o y la Forma 1 sin H_c: los dos "
        "pasos que producen el HW gobernante. Y si en vez de la solucion "
        "cerrada se reusa el Brent de la circular, se arrastra a la "
        "rectangular una fragilidad numerica que en ella NO existe."),
)
