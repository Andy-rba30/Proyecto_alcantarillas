"""
src/modelos/base.py
===================
Citas normativas, enumeraciones y datos de entrada (Sec. 1.1).

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Optional, Tuple

from src.modelos.errores import DatoFaltanteError

# ===========================================================================
# Citas: la seccion interna y el numeral de la norma, separados
# ===========================================================================

class ReferenciaNormativa(str):
    """
    Cita partida en sus DOS mitades, que hasta ahora viajaban pegadas en un
    solo string y se confundian entre si:

        seccion_hoja_ruta   navegacion INTERNA de docs/hoja_de_ruta_*.md.
                            "Sec. 9.1", "5.1", "Fase 10". No es una cita: son
                            las coordenadas del apartado que trata el tema
                            dentro del documento propio del proyecto.
        numeral_norma       la CITA real y verificable, la que un revisor
                            busca en el documento normativo: "EG-2013,
                            Seccion 503, num. 503.01, pag. 905".

    Por que hizo falta separarlas. Constantes como
    `NUMERAL_9_1 = "Sec. 9.1 (EG-2013 num. 503.01, pag. 905)"` mezclaban las
    dos cosas en una linea, y una verificacion externa leyo el string entero
    como si fuese la cita -- salio a buscar una "Sec. 9.1" en el EG-2013, que
    no existe. En `NUMERAL_8_1` el efecto fue peor: citaba una "Seccion 500"
    del EG-2013 que tampoco existe (los conductos son las Secciones 505 a 508
    del Capitulo V), un error de simplificacion arrastrado desde una version
    temprana de la hoja de ruta. El defecto no era de una constante suelta:
    era del formato, y por eso la solucion es un tipo y no cuatro parches.

    Es una subclase de `str` a proposito. El valor sigue siendo el texto que
    la memoria imprime, de modo que todo lo que ya consumia estos numerales
    -- `Verificacion.numeral`, el escapado de M11, las pruebas que hacen
    `numeral in memoria` -- sigue funcionando sin cambios, y ademas se puede
    pedir cualquiera de las dos mitades por separado cuando el reporte quiera
    imprimir solo la cita verificable.

    El texto se compone con el NUMERAL DELANTE y la seccion propia detras y
    etiquetada: quien lea de corrido encuentra primero lo que puede
    verificar.
    """

    seccion_hoja_ruta: str
    numeral_norma: str

    def __new__(cls, *, seccion_hoja_ruta: str, numeral_norma: str):
        obj = super().__new__(
            cls, f"{numeral_norma} [hoja de ruta: {seccion_hoja_ruta}]")
        obj.seccion_hoja_ruta = seccion_hoja_ruta
        obj.numeral_norma = numeral_norma
        return obj

    def __repr__(self) -> str:
        return (f"ReferenciaNormativa(seccion_hoja_ruta="
                f"{self.seccion_hoja_ruta!r}, numeral_norma="
                f"{self.numeral_norma!r})")



# ---------------------------------------------------------------------------
# Las constantes NUMERAL_* de modulo que ningun lector de produccion consume
# ---------------------------------------------------------------------------
# SIS-B-09: ocho constantes `NUMERAL_*` estan declaradas en sus modulos y no
# las lee nadie. Estaba decidido y no estaba escrito, que es el defecto: sin
# esta nota, un mantenedor no puede distinguir "todavia no cableada" de "no le
# corresponde cablearse", y las dos se ven igual leyendo el archivo.
#
# La razon se escribe AQUI, una sola vez, y aqui y no en cada modulo porque
# las ocho son la MISMA cosa y esta es la clase que la define:
# `ReferenciaNormativa` existe justamente para separar la coordenada interna
# de la hoja de ruta -- `seccion_hoja_ruta` -- de la cita verificable --
# `numeral_norma` --, y las ocho son de la primera clase.
#
# POR QUE NO SE BORRAN. Son la unica marca en el codigo de que apartado de la
# hoja de ruta implementa cada modulo, y esa navegacion se usa en cada
# revision: se lee el modulo y se va al apartado. Borrarlas ahorraria ocho
# lineas y costaria el mapa.
#
# POR QUE NO SE IMPRIMEN. Porque no son citas. Meter "4.1" o "Fase 5, V5" en
# una memoria como si fueran numerales es exactamente el defecto que
# `ReferenciaNormativa` existe para impedir -- una verificacion externa salio
# a buscar una "Sec. 9.1" en el EG-2013, que no existe --. El numeral REAL de
# cada calculo viaja por su propia via: `Verificacion.numeral`, las constantes
# de `constantes_normativas` y el registro de `src/normativa/`.
#
# Dos de las ocho tienen ademas una segunda razon, y es un bloqueo ya
# declarado: `NUMERAL_V5` y `NUMERAL_V8` anotan las dos verificaciones de la
# Fase 5 que se detienen antes de devolver una `Verificacion` -- V5 por falta
# del perfil de remanso y del ancho de derecho de via, V8 porque su logica no
# esta escrita --, de modo que su numeral no llega a la memoria porque no hay
# fila que anotar. Cuando esas dos se resuelvan, sus constantes se leeran
# solas y saldran de esta lista.
#
# Si alguna se cablea o se borra, sale de aqui EN EL MISMO COMMIT. La guardia
# que lo vigile es trabajo de la fase de tests (S16), no de esta: escribir
# hoy un test contra el estado actual congelaria los defectos que las fases de
# correccion todavia estan cerrando.
NUMERALES_DE_SECCION_SIN_LECTOR = (
    "modulos.M2_material.NUMERAL_MATERIAL",       # "Sec. 3.4"
    "modulos.M3_hidraulica.NUMERAL_MANNING",      # "4.1"
    "modulos.M4_control.NUMERAL_SALIDA",          # "4.3"
    "modulos.M5_verificaciones.NUMERAL_V5",       # bloqueo declarado
    "modulos.M5_verificaciones.NUMERAL_V8",       # bloqueo declarado
    "modulos.M8_estructural.NUMERAL_8_1_2",       # "Fase 8, items 1-2"
    "modulos.M8_estructural.NUMERAL_8_1",         # encabezado del bloque
    "modulos.MD.NUMERAL_BUCLE",                   # "Sec. 2 de la guia"
)


# ===========================================================================
# Enumeraciones (categorias declaradas por la hoja de ruta, no valores)
# ===========================================================================

class Familia(str, Enum):
    """Familias de alcantarilla, Sec. 2.3."""
    A = "A"   # de paso: Q hidrologico propio
    B = "B"   # de alivio: Q del drenaje longitudinal
    C = "C"   # cruces de canales y drenes: Q del canal (ANA / Junta)


class Denominacion(str, Enum):
    """
    Umbral binario de luz, Sec. 2.1 (num. 4.1.1.3.1 y 4.1.1.5.1).

    Son las DOS unicas denominaciones que reconoce la normativa MTC. No existe
    la categoria "ponton": el Manual de Puentes remite al Glosario de Terminos
    (pag. 44) y alli el termino no se tipifica. Si un expediente la usa, es uso
    corriente y no una tercera clase de estructura.
    """
    ALCANTARILLA = "alcantarilla"   # luz < 6.0 m -> Manual de Hidrologia
    PUENTE = "puente"               # luz >= 6.0 m -> Manual de Puentes, fuera de alcance


class CategoriaTR(str, Enum):
    """
    Filas de la Tabla N 02 (num. 3.6), Sec. 2.2. El valor de cada miembro
    coincide con la clave de `constantes_normativas.RIESGO_ADMISIBLE`, de modo
    que la categoria y su par (R, n) no puedan divergir.
    """
    QUEBRADA_IMPORTANTE = "quebrada_importante"   # R = 30 %, n = 25 anios
    QUEBRADA_MENOR = "quebrada_menor"             # R = 35 %, n = 15 anios


class TipoMaterial(str, Enum):
    """
    Materiales admitidos, Sec. 3.4. El valor de cada miembro coincide con la
    clave usada en `constantes_normativas.H_RELLENO_MIN` y `SECCION_EG2013`, y
    con la de los criterios que se indexan por material ('D_max_catalogo',
    'espesor_pared_conducto', 'cobertura_minima_aashto'). La correspondencia
    con las claves de la Tabla N 09 (`MANNING`) la resuelve M2, no este
    modulo.
    """
    CONCRETO_REFORZADO = "concreto_reforzado"
    TMC = "tmc"
    HDPE = "hdpe"


class FormaSeccion(str, Enum):
    """
    La forma del barril que el CATALOGO ofrece (Sec. 3.2 y §4.4 del plan de la
    Familia C), que NO es lo mismo que la `Seccion` que la resuelve.

    `Seccion` es la geometria ya construida, con sus dimensiones; esto es la
    familia a la que pertenece, y es lo que el catalogo necesita para saber de
    que progresion sacar el siguiente escalon y de que criterios leer el n y
    la carta de HDS-5. Un `Material` de marco y uno de tubo son los dos de
    concreto reforzado -- el mismo `TipoMaterial` --, y lo que los separa es
    esto.

    Hasta C5 el catalogo era exclusivamente circular y esta distincion no
    hacia falta: `Material.tipo` bastaba.
    """

    CIRCULAR = "circular"
    RECTANGULAR = "rectangular"


class ControlGobernante(str, Enum):
    """Cual de los dos controles fija la carga a la entrada."""
    ENTRADA = "entrada"   # Sec. 4.2, HDS-5
    SALIDA = "salida"     # Sec. 4.3, HW = H + ho - S*L


class RegimenBarril(str, Enum):
    """
    Como fluye el barril, que es lo que decide con QUE tirante y QUE velocidad
    se comparan V1 y V2 (v8 §1.3 y §4.1, enmendadas en EXT-0; EXT-M-01).

    LLENO cuando la salida esta sumergida, TW >= D: el TW llena el barril
    hasta la clave (HDS-5 3.1.6, pag. impresa 3.18: «Total barrel area is
    used when the tailwater exceeds the top of the barrel»). La v8 escribe la
    condicion como «TW >= D, o HW >= D con la salida sumergida»; la segunda
    clausula esta CONTENIDA en la primera --con salida sumergida TW ya es
    >= D--, y se dice aqui para que nadie la busque como un tercer caso.

    DISCREPANCIA CON LA FUENTE PRIMARIA, DECLARADA EN EL PUNTO DE USO (EXT-3,
    auditoria adversarial). La v8 §1.3 escribe que con TW >= D «el barril
    fluye lleno», a secas. HDS-5 3.1.3 (pag. impresa 3.2, PDF 84,
    `HDS5_3ED.3.1.3#SUMERGENCIA`) lo matiza para el CONTROL DE ENTRADA:
    «submergence of the outlet end of the culvert does not assure outlet
    control. In this case, the flow just downstream of the inlet is
    supercritical and a hydraulic jump forms in the culvert barrel». O sea:
    bajo control de entrada con TW >= D el barril NO va lleno en toda su
    longitud --el tramo de aguas arriba es supercritico y el resalto lo llena
    hacia la salida (Fig. 3.1C y 3.1D)--. Lo que SI va lleno es la salida y el
    tramo aguas abajo del resalto, que es donde V1 no tiene borde libre y
    donde la velocidad es Q/A_llena, la MENOR del barril: por eso LLENO se
    conserva para V1 y V2 tambien bajo control de entrada (rechaza V1 y
    compara V2 con la velocidad baja: conservador en los dos), y por eso la
    velocidad de salida bajo control de entrada se toma del tirante normal
    (mayor: conservador para d50). El defecto se reporta contra la v8, que
    sigue diciendo «fluye lleno» sin el matiz mientras no se corrija; quien
    la lea sin leer esto entendera flujo a presion en toda la longitud.

    PARCIALMENTE_LLENO en otro caso. Y ahi el regimen NO dice cuanto llena:
    bajo control de entrada el flujo es supercritico y se aproxima al tirante
    normal (HDS-5 3.1.3 y 3.1.6), que es lo que M3 entrega; bajo control de
    salida el tirante dentro del conducto exige el perfil de la lamina de
    agua (HDS-5 3.1.4, tipos 6 y 7; Section 3.5), y V1/V2 quedan PENDIENTES
    por `MetodoNoEvaluableError`. No se inventa un criterio de llenado.
    """
    LLENO = "lleno"
    PARCIALMENTE_LLENO = "parcialmente lleno"


class TipoDePerfil(str, Enum):
    """
    Que perfil de lamina de agua resolvio el paso directo desde la salida
    hacia la entrada (E-A; HDS-5 3.a ed. Section 3.5.1, pag. impresa 3.36-3.38,
    PDF 118-120, y la prosa de la pag. 3.12, PDF 94). Los rotulos son los de
    la fuente y los de HY-8:

        M1        pendiente suave, TW > y_n: la lamina BAJA hacia y_n aguas
                  arriba (tipo 3, «an M1 curve is computed starting at the
                  tailwater depth at the outlet»).
        M2        pendiente suave, max(y_c, TW) < y_n: la lamina SUBE hacia
                  y_n aguas arriba (tipo 2, «an M2 curve is computed starting
                  at critical depth at the outlet»; tipo 7 «to determine the
                  length of culvert that will flow full»).
        S1        pendiente pronunciada (y_n <= y_c) con la frontera por
                  encima de y_c: la lamina baja hacia y_c y, si lo alcanza
                  antes de la entrada, el remanso NO llega a la entrada y el
                  control es de ENTRADA (tipo 1/5: «an S1 curve is computed
                  and used if the S1 curve extends to the face of the
                  culvert»). Incluye la S1 de longitud CERO: TW <= y_c en un
                  barril supercritico, que es el caso (b) del dictamen.
        UNIFORME  la frontera coincide con y_n: nada mueve la lamina.
        LLENA     la linea de energia llena (Ec. 3.7) arranca en la salida
                  y alcanza la entrada sin bajar de la clave: el barril va a
                  presion en toda su longitud.

    Con un tramo lleno que arranca en la salida y termina antes de la
    entrada, el tipo es el de la LAMINA LIBRE que sigue aguas arriba (M1 o
    S1), y `PerfilLamina.longitud_llena_m` dice cuanto midio el tramo lleno.
    """
    M1 = "M1"
    M2 = "M2"
    S1 = "S1"
    UNIFORME = "uniforme"
    LLENA = "llena"
    # --- T-2 --- (INF-5.1.6). Barril HORIZONTAL, S = 0: no hay tirante normal
    # hacia el que tender, y la lamina sube aguas arriba desde max(y_c, TW)
    # sin asintota, hasta la entrada o hasta la clave. El rotulo es el que la
    # fuente nombra (HDS-5 3.5.1, pag. impresa 3.37, `HDS5_3ED.3.5.1#H2`:
    # «the horizontal profiles of H2 and H3 were added»); el H3 --supercritico
    # sobre fondo horizontal-- no puede arrancar en la salida y este
    # procedimiento no lo produce.
    H2 = "H2"


class CondicionRasante(str, Enum):
    """
    Cual de las dos condiciones de Sec. 7.A fija la cota de rasante minima:

        cota rasante >= max( cota clave + h_rec + e_paq ,
                             cota entrada + HW + resguardo(CBR) + e_paq )

    No es una etiqueta cosmetica: dice que hay que mover para bajar la rasante
    minima. Si gobierna RECUBRIMIENTO, el que manda es el conducto (bajar el
    invert, reducir el diametro o cambiar de material, porque h_rec depende
    del material); si gobierna RESGUARDO, manda la hidraulica (bajar el HW) o
    el CBR de la subrasante. Con la condicion equivocada en la memoria, el
    proyectista corrige la variable que no gobierna.
    """
    RECUBRIMIENTO = "recubrimiento"   # cota clave + h_rec + e_paq
    RESGUARDO = "resguardo"           # cota entrada + HW + resguardo + e_paq


class CondicionAnalisis(str, Enum):
    """
    Las dos columnas de la tabla de factores de seguridad de Sec. 9.3: cada
    verificacion de estabilidad del cabezal tiene un FS estatico y otro
    sismico, y no son la misma verificacion con otro numero -- cambian las
    fuerzas actuantes (aparece el incremento de Mononobe-Okabe) y cambia el
    umbral (3.00 -> 2.50, 1.50 -> 1.25).

    Los valores reproducen las claves de `constantes_normativas.FS`: quien
    lea el FS de la tabla lo indexa con este enum, no con un string suelto.
    """
    ESTATICO = "estatico"
    SISMICO = "sismico"


class GobiernaEspaciamiento(str, Enum):
    """
    Cual de los dos limites de Fase 10 fija el espaciamiento maximo entre
    alcantarillas de alivio (Familia B): el limite normativo de longitud de
    cuneta por regimen, o la longitud a la que la cuneta agota su capacidad
    hidraulica admisible frente al caudal aportante. No es cosmetico: si
    gobierna NORMATIVO el remedio de un espaciamiento insuficiente es
    replantear puntos de alivio adicionales por norma; si gobierna
    HIDRAULICO, el remedio esta en la cuneta (seccion, pendiente) o en el
    area tributaria, no en el limite de 4.1.2.1 d).
    """
    NORMATIVO = "normativo"     # num. 4.1.2.1 d) -- long_max_cuneta
    HIDRAULICO = "hidraulico"   # capacidad admisible de la cuneta


class RegimenEntrada(str, Enum):
    """
    Rama de la formulacion de control de entrada de HDS-5 (Sec. 4.2). No es
    una clasificacion cualitativa del flujo: es LA ECUACION que se aplico, y
    por eso viaja en el resultado. Una memoria que dice "HW = 0.87 m" sin
    decir con que rama se obtuvo no es revisable.

    El umbral es el caudal adimensional q* = Ku*Q/(A*D^0.5), con los limites
    [N] `Q_LIM_NO_SUMERGIDO` (3.5) y `Q_LIM_SUMERGIDO` (4.0).
    """
    NO_SUMERGIDO = "no_sumergido"   # q* <= 3.5 -> Forma 1, con H_c
    TRANSICION = "transicion"       # 3.5 < q* < 4.0 -> interpolacion lineal
    SUMERGIDO = "sumergido"         # q* >= 4.0 -> forma cuadratica en q*


# ===========================================================================
# Datos de entrada
# ===========================================================================

@dataclass(frozen=True)
class PuntoCritico:
    """
    Una fila del CSV de entrada. El orden y el nombre de los campos reproducen
    literalmente el encabezado de Sec. 1.2; M0 no debe renombrarlos.

    Unica excepcion: `progresiva_display`, que NO es una columna del CSV. M0
    la deriva del mismo string de entrada que `progresiva_km`, porque la
    notacion vial ('0+380') y el valor numerico (0.380) sirven para cosas
    distintas y ninguna de las dos se puede reconstruir bien desde la otra:
    la memoria de calculo y los planos se citan en progresivas, no en
    kilometros decimales, y '0.38' en un cuadro resumen es un error de forma
    que un revisor de expediente vial detecta de inmediato. El calculo no usa
    ninguna de las dos.

    Los campos Optional no son opcionales por comodidad: cada uno corresponde
    a un dato bloqueado en un tablero de pendientes. Se leen con `exigir()`,
    que lanza DatoFaltanteError en vez de asumir un valor.

    `sucs_fundacion` es obligatoria y NINGUN modulo la lee, y las dos cosas
    son correctas a la vez. La obligatoriedad no la inventa el codigo: la
    hoja de ruta la lista en Sec. 1.1 con etiqueta [N] E.050 y la incluye en
    el encabezado literal de Sec. 1.2, o sea que una fila sin ella es un
    expediente incompleto y M0 tiene que decirlo. Su consumidor previsto es
    el criterio 'c_phi_fundacion' -- correlacion de resistencia desde la
    clasificacion SUCS --, que esta declarado vacio y cuyo ensamblaje (E1-E5
    de Sec. 9.3) esta fuera del alcance de esta CLI. Se carga, se valida y se
    imprime en la memoria; el dia que E1-E5 se ensamblen, el dato ya esta.

    `NF_profundidad_m` es la unica columna que NO viene del encabezado de
    Sec. 1.2: se agrego al reclasificar el nivel freatico como dato de sitio
    [S]. Era un criterio unico de proyecto (1.4 m, la caracterizacion de la
    llanura del Bajo Piura) y su propia verificacion pendiente ya avisaba de
    que podia variar punto a punto. Un dato que se MIDE en cada cruce es una
    columna, no un criterio: el nivel freatico de un cruce en la llanura y el
    de otro a tres kilometros son dos mediciones distintas, y declararlos con
    un solo numero fingiria una uniformidad que ningun estudio del expediente
    respalda. Viene vacio mientras el estudio geotecnico no de el valor de
    cada punto, y entonces lo que se detiene es la verificacion que lo
    necesite -- V7 en M8/M5, la subpresion del cabezal en M9 -- no la carga
    del CSV.
    """

    id: str                            # identificador del punto
    progresiva_km: float               # km - localizador; desde T-9 mide el tramo de cuneta de VB1 (Familia B)
    progresiva_display: str            # '0+380' - notacion vial para el reporte
    familia: Familia                   # Sec. 2.3
    Q_m3s: Optional[float]             # m3/s - vacio en Familia C (Tablero 3.1)
    area_ha: Optional[float]           # ha  - solo clasificador (Sec. 1.1)
    S_cauce: Optional[float]           # m/m - pendiente del CAUCE (Sec. 1.5)
    cota_terreno: float                # msnm
    cota_rasante: float                # msnm - superficie de rodadura
    cota_subrasante: float             # msnm - V4 se chequea contra esta
    cbr_subrasante: float              # %   - define el resguardo de 5.1
    esviaje_grados: float              # grados sexagesimales
    ancho_plataforma: float            # m
    cota_fondo_receptor: float         # msnm
    Q_receptor_m3s: Optional[float]    # m3/s - ANA / Junta (Tablero 3.1)
    cota_TW: Optional[float]           # msnm - calculada en 1.3 (Tablero 3.1)
    sucs_fundacion: str                # clasificacion SUCS de la calicata
    NF_profundidad_m: Optional[float]  # m - profundidad del nivel freatico
    # LA COTA DE FONDO DE LA ENTRADA, MEDIDA. Dato de sitio [S] que varia punto
    # a punto: nivelacion del fondo del cauce -- del CANAL, en un paso de canal
    # -- en el cruce. Admite vacio: cuando falta, la cota la pone la regla que
    # el proyectista declaro en 'origen_cota_fondo_entrada' [A].
    #
    # POR QUE HACIA FALTA, y no es una comodidad. En un PASO DE CANAL el canal
    # atraviesa la via y continua: no hay cuerpo receptor distinto, y el invert
    # del conducto NO se adopta -- se hereda del fondo del canal medido en el
    # cruce. Con la unica regla que habia implementada ('cota_terreno') el
    # invert quedaba a la cota del TERRENO NATURAL, o sea POR ENCIMA del fondo
    # del canal en toda la profundidad de la seccion. HW es una carga sobre el
    # invert, de modo que el error se propaga entero a V4, a V7 y al tamizado
    # de 7.A.
    #
    # El `reemplazado_por` del criterio ya lo anticipaba con estas palabras:
    # «Cota de fondo de entrada MEDIDA por punto, como columna propia del CSV.
    # El dia que el expediente la entregue, este criterio deja de aplicarse: un
    # dato medido no se sustituye por una regla adoptada». Este campo es ese
    # dia.
    cota_fondo_entrada: Optional[float] = None   # msnm - nivelacion en el cruce
    # LA CORONACION DEL CANAL, MEDIDA. Segundo dato de sitio [S] del
    # levantamiento de los seis cruces, y el que le da a VC1 la cota contra la
    # que medir. Admite vacio, y sin el VC1 se detiene.
    #
    # POR QUE NO PODIA SALIR DE NINGUNA COLUMNA QUE YA HUBIERA. `cota_terreno`
    # es el terreno natural del cruce y `cota_rasante` es la calzada: ninguna
    # de las dos es el labio del canal. En un canal excavado la coronacion
    # puede quedar bajo el terreno natural; en uno con bordos, por encima. No
    # hay regla que las relacione, y por eso esto es una MEDICION y no una
    # derivacion -- al reves que `cota_fondo_entrada`, que si tiene regla
    # declarada para cuando falta.
    #
    # Y POR ESO SE MARCA EN `pendientes_externos` y aquella no. Una
    # `cota_fondo_entrada` vacia no espera a nadie: hay criterio que la cubre.
    # Una `cota_coronacion_canal` vacia espera al levantamiento, exactamente
    # como `NF_profundidad_m` espera al estudio geotecnico. Es la misma forma y
    # se marca igual.
    cota_coronacion_canal: Optional[float] = None  # msnm - labio del canal

    # Derivado por M0, no es columna del CSV: columnas que la fila dejo vacias
    # porque el dato depende de terceros (Tablero 3). NO significa fila
    # invalida; significa fila cargada y marcada. Quien decide si el punto se
    # puede calcular con lo que falta es el modulo que necesite el dato, no M0.
    pendientes_externos: Tuple[str, ...] = ()

    @property
    def pendiente_dato_externo(self) -> bool:
        """True si la fila espera algun dato de un tablero externo."""
        return bool(self.pendientes_externos)

    def exigir(self, campo: str) -> Any:
        """
        Devuelve el dato o lanza DatoFaltanteError. Unico acceso permitido a
        los campos que pueden venir vacios: nunca se sustituyen por un default.
        """
        if campo not in {f.name for f in fields(self)}:
            raise AttributeError(
                f"'{campo}' no es un campo de PuntoCritico (ver Sec. 1.2)"
            )
        dato = getattr(self, campo)
        if dato is None:
            raise DatoFaltanteError(campo, id_punto=self.id)
        return dato


@dataclass(frozen=True)
class CotaDeEntrada:
    """
    La cota del fondo de la entrada CON SU PROCEDENCIA, msnm.

    POR QUE NO ES UN `float`. Porque la misma magnitud llega hoy por dos vias
    que NO son intercambiables para quien sustenta: MEDIDA --- nivelacion del
    fondo del canal en el cruce, columna `cota_fondo_entrada` --- o
    ADOPTADA --- la regla que el proyectista declaro en
    'origen_cota_fondo_entrada' [A] ---. Un dato y una eleccion se corrigen en
    sitios distintos y se defienden con argumentos distintos, y el revisor va
    a preguntar cual de las dos es. Devolver un escalar obligaria a cada
    consumidor a volver a preguntarselo al punto, que es como dos consumidores
    acaban respondiendose cosas distintas.

    Es la misma forma que `Verificacion` --- que no devuelve un `bool` desnudo
    --- y por la misma razon: el numero sin su procedencia no es defendible.

    `procedencia` se escribe para ENTRAR EN UNA `Magnitud`, que es donde la
    memoria la imprime. No lleva formato ni etiquetas: eso lo pone M11.
    """

    valor: float                 # msnm
    medida: bool                 # True si vino de la columna del CSV
    procedencia: str             # para `Magnitud.procedencia`
    # LA REGLA QUE PRODUJO LA COTA, cuando es adoptada: la clave de
    # `M5.ORIGENES_COTA_ENTRADA` que el criterio 'origen_cota_fondo_entrada'
    # declaraba EN ESA CORRIDA. `None` cuando la cota es medida, porque
    # entonces no hubo regla. Es un campo desde EXT-4 (PC-07): el JSON la
    # publicaba leyendo el registro global AL EXPORTAR, y una declaracion
    # posterior cambiaba la regla impresa al lado de una cota que no cambio.
    # La regla que gobierna un numero viaja con el numero.
    regla: Optional[str] = None

    @property
    def rotulo(self) -> str:
        """«MEDIDA» o «ADOPTADA», para los rotulos cortos del volcado."""
        return "MEDIDA" if self.medida else "ADOPTADA"

    # --- T-10 ---
    @property
    def nota(self) -> str:
        """
        La nota que acompaña al rotulo: lo que la cota ES. Vivia escrita en
        el adaptador del JSON (`cli._geometria_json`) y la memoria decia otra
        frase; una sola fuente, tres vistas (el JSON, la CLI y la memoria).
        """
        if self.medida:
            return ("cota MEDIDA: columna cota_fondo_entrada del CSV; el "
                    "criterio no se aplico en este punto")
        return ("no es cota medida: sale de la regla declarada en ese "
                "criterio mientras el expediente no entregue la cota de "
                "invert de entrada por punto")

    # --- T-6 ---
    @property
    def aviso(self) -> str:
        """
        El aviso que acompaña a una cota ADOPTADA igual al terreno
        (INF-5.1.18), o cadena vacia cuando la cota es medida o sale de otra
        regla. No es un incumplimiento ni detiene nada: dice que la rasante
        minima de 7.A, V4 y V7 estan calculadas sobre una cota que nadie
        midio, y que dato la sustituye (la columna `cota_fondo_entrada`).
        """
        if self.medida or self.regla != REGLA_FONDO_IGUAL_AL_TERRENO:
            return ""
        return AVISO_FONDO_ENTRADA_ADOPTADO


# La regla de 'origen_cota_fondo_entrada' que dispara el aviso, y el aviso.
# El texto es el de la cadena T (T-6 punto 1) y vive aqui, junto al tipo que
# lo emite (`CotaDeEntrada.aviso`), para que M7, la CLI y M11 impriman LA
# MISMA frase.
REGLA_FONDO_IGUAL_AL_TERRENO = "cota_terreno"
AVISO_FONDO_ENTRADA_ADOPTADO = (
    "fondo de entrada adoptado igual al terreno de plataforma: medir en el "
    "cauce")
